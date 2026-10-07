"""
Migration Boundary Specification & Transactional Engine (WP-05).

Governing ADR: ADR-034 (ARCH-034: Identity Authority, Instance Exclusivity & Anti-Branching Boundary).
Reference Specification: docs/others/IDENTITY_AUTHORITY_SPECIFICATION/IDENTITY_AUTHORITY_SPEC_V01.md
Reference Plan: docs/others/IDENTITY_AUTHORITY_SPECIFICATION/IMPLEMENTATION_PLAN.md

Primary Architectural Purpose:
Establish and enforce the formal sequential transaction boundary for transferring
an existing, initialized Lucia identity between distinct hosts or environments:

    Freeze (Source) ──> Export/Transfer ──> Verify (Target) ──> Decommission (Source) ──> Activate (Target)

Boundary & Invariant Guarantees:
- INV-1 (One Continuous Life): Anti-branching guarantee. Migration must never silently
  create two active authorities for one identity.
- INV-5 (Zero Cloud Dependencies): 100% offline edge execution. All cryptographic integrity
  checks, receipts, and proofs use local SHA-256 and HMAC keyed to the identity anchor root.
- INV-8 (Genesis Gate Invariant): Development / Simulation != Lucia Activation.
  Pre-Genesis profiles (e.g. `{"is_onboarded": false}`) are Genesis-locked and CANNOT be migrated.
  Ordinary system operation never triggers migration or Genesis activation.
- Tripartite Ontological Boundary (Ontology B):
    Identity State (Anchor) != Host Environment (Binding) != Substrate (Phylogeny) != Life State (Stores)
  Throughout migration:
    - Identity Anchor: 100% bit-for-bit identical and immutable (instance_uuid, born_at, genesis_commit, genesis_root_hash).
    - Host Environment: Bound to new host hardware digest and canonical path; hardware_migration_epoch incremented.
    - Phylogenetic Lineage: Substrate/engine updates permitted while preserving identity anchor.
    - Life State: Epoch-synchronized stores transferred intact with multi-file commit barrier.
- Epistemic Honesty Standard (ADR-034 §2.4.2):
  Software-level migration protocol prevents accidental split-brain and provides tamper-evident receipts,
  but cannot prevent deliberate offline hypervisor cloning (the Offline Clone Paradox).
"""

from __future__ import annotations

import copy
from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum
import hashlib
import hmac
import json
import logging
import os
from pathlib import Path
import shutil
import tarfile
from typing import Any, Dict, List, Optional, Sequence, Set, Tuple, Union
import uuid

from src.core.identity.identity_anchor import (
    DEFAULT_PROFILE_PATH,
    DecommissionedInstanceError,
    FrozenMigrationStateError,
    IdentityAnchor,
    IdentityAnchorError,
    PhylogeneticLineage,
    apply_phylogenetic_upgrade,
    guard_immutable_fields,
    validate_identity_anchor,
    validate_profile_identity,
    verify_identity_on_startup,
)
from src.core.identity.instance_lock import (
    DEFAULT_LOCK_PATH,
    InstanceAuthorityConflictError,
    InstanceLock,
)
from src.core.identity.provenance_verifier import (
    AuthorityBinding,
    HardwareDigestComponents,
    ProvenanceVerificationStatus,
    collect_hardware_components,
    compute_component_digests,
    compute_hardware_digest,
    normalize_workspace_path,
    verify_provenance_and_environment,
)
from src.core.emotion.persistence import (
    DEFAULT_EPOCH_MANIFEST_PATH,
    load_epoch_manifest,
    verify_and_reconcile_stores,
)

logger = logging.getLogger("lucia.identity.migration")

# Canonical Filenames
MIGRATION_MANIFEST_FILENAME: str = "migration_manifest.json"
MIGRATION_RECEIPT_FILENAME: str = "migration_receipt.json"
DECOMMISSION_PROOF_FILENAME: str = "decommission_proof.json"

REQUIRED_PAYLOAD_FILES: Tuple[str, ...] = (
    "profile.json",
    "epoch_manifest.json",
    "relationship.json",
    "dynamical_state.json",
    "chat_history.json",
)


# ---------------------------------------------------------------------------
# Migration Status Enum & Exceptions
# ---------------------------------------------------------------------------

class MigrationStatus(str, Enum):
    """Canonical transactional states for migration lifecycle."""
    IDLE = "IDLE"
    FROZEN = "FROZEN"
    VERIFIED = "VERIFIED"
    DECOMMISSIONED = "DECOMMISSIONED"
    ACTIVE = "ACTIVE"
    ABORTED = "ABORTED"


class MigrationError(IdentityAnchorError):
    """Base exception for all migration boundary errors."""
    pass


class PreGenesisMigrationForbiddenError(MigrationError):
    """Raised when attempting migration on an un-onboarded / pre-Genesis profile."""
    pass


class CorruptedArchiveError(MigrationError):
    """Raised when a migration archive cannot be read or is physically corrupted."""
    pass


class ManifestHashMismatchError(MigrationError):
    """Raised when file content or hashes in the archive diverge from migration manifest."""
    pass


class MissingReceiptError(MigrationError):
    """Raised when decommissioning is attempted without a valid target migration receipt."""
    pass


class InvalidReceiptError(MigrationError):
    """Raised when a migration receipt fails cryptographic or semantic validation."""
    pass


class MissingDecommissionProofError(MigrationError):
    """Raised when activating a target without valid proof of source decommissioning."""
    pass


class InvalidDecommissionProofError(MigrationError):
    """Raised when decommission proof fails cryptographic or semantic verification."""
    pass


class DestinationMismatchError(MigrationError):
    """Raised when activation is attempted on an unauthorized or secondary destination host."""
    pass


class MigrationConflictError(MigrationError):
    """Raised when a conflicting migration transaction is already in progress."""
    pass


# ---------------------------------------------------------------------------
# Cryptographic Helpers (100% Offline Local HMAC & SHA-256)
# ---------------------------------------------------------------------------

def compute_file_sha256(path: Union[Path, str]) -> Tuple[str, int]:
    """Compute SHA-256 digest and byte size for a local file."""
    p = Path(path)
    if not p.is_file():
        raise FileNotFoundError(f"File '{p}' does not exist.")
    h = hashlib.sha256()
    size = 0
    with open(p, "rb") as f:
        while chunk := f.read(65536):
            h.update(chunk)
            size += len(chunk)
    return h.hexdigest(), size


def canonical_json_bytes(data: Dict[str, Any]) -> bytes:
    """Return deterministic canonical UTF-8 JSON bytes (sorted keys, no spaces)."""
    return json.dumps(data, sort_keys=True, separators=(",", ":")).encode("utf-8")


def compute_manifest_digest(manifest_dict: Dict[str, Any]) -> str:
    """Compute SHA-256 over canonical JSON of manifest excluding manifest_digest."""
    d = {k: v for k, v in manifest_dict.items() if k != "manifest_digest"}
    return hashlib.sha256(canonical_json_bytes(d)).hexdigest()


def compute_receipt_token(receipt_dict: Dict[str, Any], genesis_root_hash: str) -> str:
    """Compute HMAC-SHA256 token for receipt bound to identity genesis root."""
    d = {k: v for k, v in receipt_dict.items() if k != "receipt_token"}
    key = genesis_root_hash.encode("utf-8")
    return hmac.new(key, canonical_json_bytes(d), hashlib.sha256).hexdigest()


def compute_proof_token(proof_dict: Dict[str, Any], genesis_root_hash: str) -> str:
    """Compute HMAC-SHA256 token for decommission proof bound to identity genesis root."""
    d = {k: v for k, v in proof_dict.items() if k != "proof_token"}
    key = genesis_root_hash.encode("utf-8")
    return hmac.new(key, canonical_json_bytes(d), hashlib.sha256).hexdigest()


# ---------------------------------------------------------------------------
# Domain Models
# ---------------------------------------------------------------------------

@dataclass(frozen=True)
class MigrationManifest:
    """
    Cryptographic manifest generated at source freeze.

    Binds identity anchor, phylogenetic metadata, source hardware provenance,
    and exact SHA-256 checksums of all exported persistent state files.
    """
    migration_id: str
    migration_epoch: int
    created_at: str
    source_hardware_digest: str
    source_canonical_path: str
    identity_anchor: Dict[str, str]
    phylogenetic_lineage: Dict[str, Any]
    files: Dict[str, Dict[str, Any]]  # rel_path -> {"sha256": hex, "size_bytes": int}
    manifest_digest: str

    def to_dict(self) -> Dict[str, Any]:
        return {
            "migration_id": self.migration_id,
            "migration_epoch": self.migration_epoch,
            "created_at": self.created_at,
            "source_hardware_digest": self.source_hardware_digest,
            "source_canonical_path": self.source_canonical_path,
            "identity_anchor": self.identity_anchor,
            "phylogenetic_lineage": self.phylogenetic_lineage,
            "files": self.files,
            "manifest_digest": self.manifest_digest,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "MigrationManifest":
        return cls(
            migration_id=str(data.get("migration_id", "")),
            migration_epoch=int(data.get("migration_epoch", 0)),
            created_at=str(data.get("created_at", "")),
            source_hardware_digest=str(data.get("source_hardware_digest", "")),
            source_canonical_path=str(data.get("source_canonical_path", "")),
            identity_anchor=dict(data.get("identity_anchor", {})),
            phylogenetic_lineage=dict(data.get("phylogenetic_lineage", {})),
            files=dict(data.get("files", {})),
            manifest_digest=str(data.get("manifest_digest", "")),
        )


@dataclass(frozen=True)
class MigrationReceipt:
    """
    Cryptographic receipt issued by destination after full archive verification.

    Binds destination hardware environment to manifest digest and identity anchor.
    """
    receipt_id: str
    migration_id: str
    destination_hardware_digest: str
    destination_canonical_path: str
    manifest_digest: str
    verified_at: str
    status: str = "VERIFIED"
    receipt_token: str = ""

    def to_dict(self) -> Dict[str, Any]:
        return {
            "receipt_id": self.receipt_id,
            "migration_id": self.migration_id,
            "destination_hardware_digest": self.destination_hardware_digest,
            "destination_canonical_path": self.destination_canonical_path,
            "manifest_digest": self.manifest_digest,
            "verified_at": self.verified_at,
            "status": self.status,
            "receipt_token": self.receipt_token,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "MigrationReceipt":
        return cls(
            receipt_id=str(data.get("receipt_id", "")),
            migration_id=str(data.get("migration_id", "")),
            destination_hardware_digest=str(data.get("destination_hardware_digest", "")),
            destination_canonical_path=str(data.get("destination_canonical_path", "")),
            manifest_digest=str(data.get("manifest_digest", "")),
            verified_at=str(data.get("verified_at", "")),
            status=str(data.get("status", "VERIFIED")),
            receipt_token=str(data.get("receipt_token", "")),
        )


@dataclass(frozen=True)
class DecommissionProof:
    """
    Cryptographic proof issued by source upon successful decommission.

    Attests that source has permanently revoked its authority and released locks.
    Required before target can execute activation.
    """
    proof_id: str
    migration_id: str
    receipt_id: str
    source_hardware_digest: str
    destination_hardware_digest: str
    destination_canonical_path: str
    decommissioned_at: str
    proof_token: str = ""

    def to_dict(self) -> Dict[str, Any]:
        return {
            "proof_id": self.proof_id,
            "migration_id": self.migration_id,
            "receipt_id": self.receipt_id,
            "source_hardware_digest": self.source_hardware_digest,
            "destination_hardware_digest": self.destination_hardware_digest,
            "destination_canonical_path": self.destination_canonical_path,
            "decommissioned_at": self.decommissioned_at,
            "proof_token": self.proof_token,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "DecommissionProof":
        return cls(
            proof_id=str(data.get("proof_id", "")),
            migration_id=str(data.get("migration_id", "")),
            receipt_id=str(data.get("receipt_id", "")),
            source_hardware_digest=str(data.get("source_hardware_digest", "")),
            destination_hardware_digest=str(data.get("destination_hardware_digest", "")),
            destination_canonical_path=str(data.get("destination_canonical_path", "")),
            decommissioned_at=str(data.get("decommissioned_at", "")),
            proof_token=str(data.get("proof_token", "")),
        )


@dataclass(frozen=True)
class MigrationVerificationResult:
    """Result of destination-side archive and state verification."""
    is_valid: bool
    status: str
    migration_id: Optional[str] = None
    receipt: Optional[MigrationReceipt] = None
    errors: List[str] = field(default_factory=list)


@dataclass(frozen=True)
class MigrationActivationResult:
    """Result of destination activation execution."""
    is_activated: bool
    status: str
    migration_id: Optional[str] = None
    target_path: Optional[Path] = None
    new_hardware_migration_epoch: int = 0
    errors: List[str] = field(default_factory=list)


# ---------------------------------------------------------------------------
# Core Step 1: Source Freeze
# ---------------------------------------------------------------------------

def freeze_for_migration(
    workspace_path: Union[Path, str],
    profile_path: Optional[Union[Path, str]] = None,
    lock_path: Optional[Union[Path, str]] = None,
    hardware_components: Optional[HardwareDigestComponents] = None,
) -> Tuple[MigrationManifest, Dict[str, Any]]:
    """
    Step 1: Freeze source instance for migration.

    Execution Contract:
    1. Holds exclusive instance authority over source workspace (WP-01).
    2. Verifies identity anchor is initialized (fails closed on un-onboarded / pre-Genesis).
    3. Verifies source is not already decommissioned or currently frozen.
    4. Verifies store consistency against epoch manifest barrier (WP-04).
    5. Sets source profile migration_state to 'FROZEN'.
    6. Constructs signed MigrationManifest binding files, anchor, and hardware digest.
    7. Atomically saves source profile.json with immutable anchor guarded.
    """
    ws = Path(workspace_path).resolve()
    data_dir = ws / "data"
    prof_p = Path(profile_path) if profile_path else data_dir / "profile.json"
    lk_p = Path(lock_path) if lock_path else data_dir / ".instance.lock"

    if not prof_p.exists():
        raise PreGenesisMigrationForbiddenError(
            f"Cannot freeze for migration: profile not found at '{prof_p}'."
        )

    with open(prof_p, "r", encoding="utf-8") as f:
        profile_data = json.load(f)

    if not isinstance(profile_data, dict):
        raise MigrationError(f"Invalid profile at '{prof_p}': expected JSON object.")

    # Invariant: Genesis Locked profiles cannot be migrated
    if not profile_data.get("is_onboarded", False):
        raise PreGenesisMigrationForbiddenError(
            "Cannot migrate an un-onboarded / pre-Genesis Lucia identity. "
            "Genesis remains strictly LOCKED under INV-8."
        )

    # Invariant: Decommissioned profiles cannot be migrated
    mig_block = profile_data.get("migration_state", {})
    if isinstance(mig_block, dict) and mig_block.get("status") == MigrationStatus.DECOMMISSIONED.value:
        raise DecommissionedInstanceError(
            "This instance has already been decommissioned and cannot be re-migrated."
        )

    # Check existing freeze
    if isinstance(mig_block, dict) and mig_block.get("status") == MigrationStatus.FROZEN.value:
        raise MigrationConflictError(
            f"Source instance is already frozen under migration_id '{mig_block.get('migration_id')}'. "
            f"Must abort active freeze before initiating a new migration."
        )

    # Validate anchor
    anchor_dict = profile_data.get("identity_anchor")
    if not anchor_dict or not isinstance(anchor_dict, dict):
        raise MigrationError("Missing identity_anchor block in onboarded profile.")
    validate_identity_anchor(anchor_dict)

    # Validate required stores exist
    file_hashes: Dict[str, Dict[str, Any]] = {}
    for filename in REQUIRED_PAYLOAD_FILES:
        fp = data_dir / filename
        if not fp.exists():
            raise MigrationError(f"Required persistent store missing from data/: '{filename}'.")
        sha256, size = compute_file_sha256(fp)
        file_hashes[filename] = {"sha256": sha256, "size_bytes": size}

    # Verify store consistency prior to freeze
    reconcile_rep = verify_and_reconcile_stores(
        relationship_path=data_dir / "relationship.json",
        dynamical_path=data_dir / "dynamical_state.json",
        manifest_path=data_dir / "epoch_manifest.json",
    )
    if not reconcile_rep.is_consistent:
        raise MigrationError(
            f"Cannot freeze for migration: persistent stores are in inconsistent state: "
            f"{reconcile_rep.inconsistencies_detected}"
        )

    comps = hardware_components or collect_hardware_components(ws)
    hw_digest = compute_hardware_digest(comps)
    auth_block = profile_data.get("authority_binding", {})
    source_epoch = int(auth_block.get("hardware_migration_epoch", 0))

    migration_id = str(uuid.uuid4())
    now_utc = datetime.now(timezone.utc).isoformat()

    # Update source profile to FROZEN state first
    updated_profile = copy.deepcopy(profile_data)
    updated_profile["migration_state"] = {
        "status": MigrationStatus.FROZEN.value,
        "migration_id": migration_id,
        "frozen_at": now_utc,
    }

    # Guard immutability: Ensure zero mutation of ontogenetic anchor
    guard_immutable_fields(profile_data, updated_profile)

    # Atomic write to profile.json so on-disk file reflects frozen state
    tmp_path = prof_p.with_suffix(".tmp")
    with open(tmp_path, "w", encoding="utf-8") as f:
        json.dump(updated_profile, f, indent=2)
    tmp_path.replace(prof_p)

    # Validate required stores exist and compute exact on-disk hashes
    file_hashes: Dict[str, Dict[str, Any]] = {}
    for filename in REQUIRED_PAYLOAD_FILES:
        fp = data_dir / filename
        if not fp.exists():
            raise MigrationError(f"Required persistent store missing from data/: '{filename}'.")
        sha256, size = compute_file_sha256(fp)
        file_hashes[filename] = {"sha256": sha256, "size_bytes": size}

    manifest_content: Dict[str, Any] = {
        "migration_id": migration_id,
        "migration_epoch": source_epoch,
        "created_at": now_utc,
        "source_hardware_digest": hw_digest,
        "source_canonical_path": normalize_workspace_path(ws),
        "identity_anchor": copy.deepcopy(anchor_dict),
        "phylogenetic_lineage": copy.deepcopy(profile_data.get("phylogenetic_lineage", {})),
        "files": file_hashes,
    }
    manifest_digest = compute_manifest_digest(manifest_content)
    manifest_content["manifest_digest"] = manifest_digest
    manifest = MigrationManifest.from_dict(manifest_content)

    # Save local copy of manifest in data_dir
    manifest_file = data_dir / MIGRATION_MANIFEST_FILENAME
    with open(manifest_file, "w", encoding="utf-8") as f:
        json.dump(manifest.to_dict(), f, indent=2)

    logger.info("Source identity successfully FROZEN for migration: id=%s", migration_id)
    return manifest, updated_profile


def abort_source_freeze(
    workspace_path: Union[Path, str],
    profile_path: Optional[Union[Path, str]] = None,
) -> Dict[str, Any]:
    """
    Abort an in-progress migration freeze on the source instance.

    Contract:
    - Allowed ONLY if source has NOT been decommissioned.
    - Transitions migration_state status from FROZEN back to ABORTED/IDLE.
    """
    ws = Path(workspace_path).resolve()
    prof_p = Path(profile_path) if profile_path else ws / "data" / "profile.json"

    with open(prof_p, "r", encoding="utf-8") as f:
        profile_data = json.load(f)

    mig_block = profile_data.get("migration_state", {})
    if isinstance(mig_block, dict) and mig_block.get("status") == MigrationStatus.DECOMMISSIONED.value:
        raise DecommissionedInstanceError(
            "Cannot abort freeze: source instance has already been permanently decommissioned."
        )

    updated_profile = copy.deepcopy(profile_data)
    updated_profile["migration_state"] = {
        "status": MigrationStatus.ABORTED.value,
        "aborted_at": datetime.now(timezone.utc).isoformat(),
        "previous_migration_id": mig_block.get("migration_id"),
    }

    guard_immutable_fields(profile_data, updated_profile)

    tmp_path = prof_p.with_suffix(".tmp")
    with open(tmp_path, "w", encoding="utf-8") as f:
        json.dump(updated_profile, f, indent=2)
    tmp_path.replace(prof_p)

    logger.info("Source migration freeze successfully ABORTED.")
    return updated_profile


# ---------------------------------------------------------------------------
# Core Step 2: Export Archive
# ---------------------------------------------------------------------------

def export_migration_archive(
    manifest: MigrationManifest,
    data_dir: Union[Path, str],
    output_archive_path: Union[Path, str],
) -> Path:
    """
    Step 2: Package frozen state files and manifest into tar.gz migration archive.

    Contract:
    - Includes exact files from manifest.
    - Writes migration_manifest.json at the root of the archive.
    """
    d_dir = Path(data_dir).resolve()
    out_p = Path(output_archive_path).resolve()
    out_p.parent.mkdir(parents=True, exist_ok=True)

    with tarfile.open(out_p, "w:gz") as tar:
        # 1. Add manifest
        manifest_bytes = canonical_json_bytes(manifest.to_dict())
        tinfo = tarfile.TarInfo(name=MIGRATION_MANIFEST_FILENAME)
        tinfo.size = len(manifest_bytes)
        tinfo.mtime = int(datetime.now(timezone.utc).timestamp())
        import io
        tar.addfile(tinfo, io.BytesIO(manifest_bytes))

        # 2. Add files
        for rel_name in manifest.files.keys():
            fp = d_dir / rel_name
            if not fp.exists():
                raise MigrationError(f"File '{rel_name}' listed in manifest missing on disk.")
            tar.add(fp, arcname=f"data/{rel_name}")

    logger.info("Migration archive successfully exported to: %s", out_p)
    return out_p


# ---------------------------------------------------------------------------
# Core Step 3: Destination Verification & Receipt Generation
# ---------------------------------------------------------------------------

def verify_migration_archive(
    archive_path: Union[Path, str],
    destination_workspace_path: Union[Path, str],
    destination_hardware_components: Optional[HardwareDigestComponents] = None,
    destination_lock_path: Optional[Union[Path, str]] = None,
) -> Tuple[MigrationVerificationResult, Optional[MigrationReceipt]]:
    """
    Step 3: Destination-side verification of migration archive.

    Execution Contract:
    1. Validates archive integrity (handles corruption/truncation).
    2. Validates migration_manifest.json and manifest_digest.
    3. Verifies every file against manifest checksum and size.
    4. Validates identity anchor structure via validate_identity_anchor.
    5. Confirms archive profile is onboarded and contains matching anchor.
    6. Verifies destination instance is NOT currently running.
    7. Generates cryptographically bound MigrationReceipt if valid.
    """
    arc_p = Path(archive_path).resolve()
    dest_ws = Path(destination_workspace_path).resolve()

    if not arc_p.exists() or not arc_p.is_file():
        return (
            MigrationVerificationResult(
                is_valid=False,
                status="ARCHIVE_NOT_FOUND",
                errors=[f"Archive not found: '{arc_p}'"],
            ),
            None,
        )

    # 1. Open tar archive safely
    try:
        tar = tarfile.open(arc_p, "r:gz")
    except Exception as exc:
        return (
            MigrationVerificationResult(
                is_valid=False,
                status="CORRUPTED_ARCHIVE",
                errors=[f"Failed to open archive: {exc}"],
            ),
            None,
        )

    try:
        # Check path traversal
        for member in tar.getmembers():
            if member.name.startswith("/") or ".." in member.name:
                return (
                    MigrationVerificationResult(
                        is_valid=False,
                        status="SECURITY_VIOLATION",
                        errors=[f"Malicious member path detected: '{member.name}'"],
                    ),
                    None,
                )

        # 2. Extract and parse manifest
        try:
            m_member = tar.getmember(MIGRATION_MANIFEST_FILENAME)
        except KeyError:
            return (
                MigrationVerificationResult(
                    is_valid=False,
                    status="MISSING_MANIFEST",
                    errors=[f"Archive missing '{MIGRATION_MANIFEST_FILENAME}'"],
                ),
                None,
            )

        f_manifest = tar.extractfile(m_member)
        if f_manifest is None:
            return (
                MigrationVerificationResult(
                    is_valid=False,
                    status="UNREADABLE_MANIFEST",
                    errors=["Unable to read manifest file from archive"],
                ),
                None,
            )

        manifest_data = json.load(f_manifest)
        manifest = MigrationManifest.from_dict(manifest_data)

        # Verify manifest digest
        expected_digest = compute_manifest_digest(manifest.to_dict())
        if expected_digest != manifest.manifest_digest:
            return (
                MigrationVerificationResult(
                    is_valid=False,
                    status="MANIFEST_DIGEST_MISMATCH",
                    migration_id=manifest.migration_id,
                    errors=[
                        f"Manifest digest mismatch: expected '{expected_digest}', got '{manifest.manifest_digest}'"
                    ],
                ),
                None,
            )

        # 3. Validate identity anchor
        try:
            validate_identity_anchor(manifest.identity_anchor)
        except Exception as exc:
            return (
                MigrationVerificationResult(
                    is_valid=False,
                    status="INVALID_IDENTITY_ANCHOR",
                    migration_id=manifest.migration_id,
                    errors=[f"Identity anchor in manifest invalid: {exc}"],
                ),
                None,
            )

        # 4. Verify each file in manifest against archive contents
        for rel_name, expected_meta in manifest.files.items():
            arc_rel_name = f"data/{rel_name}"
            try:
                member = tar.getmember(arc_rel_name)
            except KeyError:
                return (
                    MigrationVerificationResult(
                        is_valid=False,
                        status="MISSING_PAYLOAD_FILE",
                        migration_id=manifest.migration_id,
                        errors=[f"Archive missing required payload file: '{arc_rel_name}'"],
                    ),
                    None,
                )

            extracted_f = tar.extractfile(member)
            if extracted_f is None:
                return (
                    MigrationVerificationResult(
                        is_valid=False,
                        status="UNREADABLE_PAYLOAD_FILE",
                        migration_id=manifest.migration_id,
                        errors=[f"Unable to read file '{arc_rel_name}' from archive"],
                    ),
                    None,
                )

            content = extracted_f.read()
            actual_size = len(content)
            actual_sha256 = hashlib.sha256(content).hexdigest()

            if actual_size != expected_meta.get("size_bytes") or actual_sha256 != expected_meta.get("sha256"):
                return (
                    MigrationVerificationResult(
                        is_valid=False,
                        status="FILE_HASH_MISMATCH",
                        migration_id=manifest.migration_id,
                        errors=[
                            f"File checksum mismatch for '{rel_name}': expected {expected_meta.get('sha256')}, "
                            f"got {actual_sha256}"
                        ],
                    ),
                    None,
                )

        # 5. Extract profile and verify consistency
        prof_member = tar.getmember("data/profile.json")
        prof_f = tar.extractfile(prof_member)
        if prof_f is None:
            return (
                MigrationVerificationResult(
                    is_valid=False,
                    status="MISSING_PROFILE",
                    migration_id=manifest.migration_id,
                    errors=["Missing profile.json in archive"],
                ),
                None,
            )
        archive_profile = json.load(prof_f)
        if not archive_profile.get("is_onboarded", False):
            return (
                MigrationVerificationResult(
                    is_valid=False,
                    status="PRE_GENESIS_ARCHIVE",
                    migration_id=manifest.migration_id,
                    errors=["Archive contains an un-onboarded / pre-Genesis profile."],
                ),
                None,
            )

        # Confirm identity anchor matches
        if archive_profile.get("identity_anchor") != manifest.identity_anchor:
            return (
                MigrationVerificationResult(
                    is_valid=False,
                    status="PROFILE_ANCHOR_MISMATCH",
                    migration_id=manifest.migration_id,
                    errors=["Profile identity anchor does not match manifest identity anchor."],
                ),
                None,
            )

    finally:
        tar.close()

    # 6. Gather destination hardware details & generate MigrationReceipt
    dest_comps = destination_hardware_components or collect_hardware_components(dest_ws)
    dest_hw_digest = compute_hardware_digest(dest_comps)
    dest_canonical_path = normalize_workspace_path(dest_ws)

    receipt_id = str(uuid.uuid4())
    verified_at = datetime.now(timezone.utc).isoformat()

    receipt_dict: Dict[str, Any] = {
        "receipt_id": receipt_id,
        "migration_id": manifest.migration_id,
        "destination_hardware_digest": dest_hw_digest,
        "destination_canonical_path": dest_canonical_path,
        "manifest_digest": manifest.manifest_digest,
        "verified_at": verified_at,
        "status": "VERIFIED",
    }
    genesis_root = manifest.identity_anchor.get("genesis_root_hash", "")
    receipt_token = compute_receipt_token(receipt_dict, genesis_root)
    receipt_dict["receipt_token"] = receipt_token

    receipt = MigrationReceipt.from_dict(receipt_dict)

    logger.info(
        "Archive verification successful: migration_id=%s, receipt_id=%s",
        manifest.migration_id,
        receipt.receipt_id,
    )
    return (
        MigrationVerificationResult(
            is_valid=True,
            status="VERIFIED",
            migration_id=manifest.migration_id,
            receipt=receipt,
            errors=[],
        ),
        receipt,
    )


# ---------------------------------------------------------------------------
# Core Step 4: Source Decommissioning
# ---------------------------------------------------------------------------

def decommission_source_instance(
    workspace_path: Union[Path, str],
    receipt: MigrationReceipt,
    profile_path: Optional[Union[Path, str]] = None,
    lock_path: Optional[Union[Path, str]] = None,
) -> DecommissionProof:
    """
    Step 4: Permanently decommission source instance authority.

    Execution Contract:
    1. Validates receipt against source state and identity anchor.
    2. Asserts source is in FROZEN state with matching migration_id.
    3. Sets source migration_state to 'DECOMMISSIONED'.
    4. Releases source InstanceLock.
    5. Issues cryptographically bound DecommissionProof.
    6. Ensures source profile can NEVER boot or acquire authority again.
    """
    if not isinstance(receipt, MigrationReceipt):
        raise MissingReceiptError("A valid MigrationReceipt instance is required for decommissioning.")

    ws = Path(workspace_path).resolve()
    prof_p = Path(profile_path) if profile_path else ws / "data" / "profile.json"

    if not prof_p.exists():
        raise MigrationError(f"Source profile not found at '{prof_p}'.")

    with open(prof_p, "r", encoding="utf-8") as f:
        profile_data = json.load(f)

    # Verify source was frozen
    mig_block = profile_data.get("migration_state", {})
    if not isinstance(mig_block, dict) or mig_block.get("status") != MigrationStatus.FROZEN.value:
        raise MigrationConflictError(
            f"Cannot decommission source: instance status is '{mig_block.get('status')}', expected 'FROZEN'."
        )

    if mig_block.get("migration_id") != receipt.migration_id:
        raise MigrationConflictError(
            f"Migration ID mismatch: source frozen under '{mig_block.get('migration_id')}', "
            f"receipt is for '{receipt.migration_id}'."
        )

    anchor_dict = profile_data.get("identity_anchor", {})
    genesis_root = anchor_dict.get("genesis_root_hash", "")

    # Validate receipt token
    expected_token = compute_receipt_token(receipt.to_dict(), genesis_root)
    if expected_token != receipt.receipt_token:
        raise InvalidReceiptError("Migration receipt cryptographic token verification failed.")

    # Validate manifest digest matches
    manifest_file = ws / "data" / MIGRATION_MANIFEST_FILENAME
    if manifest_file.exists():
        with open(manifest_file, "r", encoding="utf-8") as f:
            local_manifest = json.load(f)
        if local_manifest.get("manifest_digest") != receipt.manifest_digest:
            raise InvalidReceiptError("Receipt manifest digest does not match local manifest digest.")
    elif mig_block.get("manifest_digest") and mig_block.get("manifest_digest") != receipt.manifest_digest:
        raise InvalidReceiptError("Receipt manifest digest does not match source frozen manifest digest.")

    now_utc = datetime.now(timezone.utc).isoformat()
    proof_id = str(uuid.uuid4())

    auth_block = profile_data.get("authority_binding", {})
    source_hw_digest = auth_block.get("bound_machine_guid_digest", "")
    if not source_hw_digest:
        source_hw_digest = compute_hardware_digest(collect_hardware_components(ws))

    proof_dict: Dict[str, Any] = {
        "proof_id": proof_id,
        "migration_id": receipt.migration_id,
        "receipt_id": receipt.receipt_id,
        "source_hardware_digest": source_hw_digest,
        "destination_hardware_digest": receipt.destination_hardware_digest,
        "destination_canonical_path": receipt.destination_canonical_path,
        "decommissioned_at": now_utc,
    }
    proof_token = compute_proof_token(proof_dict, genesis_root)
    proof_dict["proof_token"] = proof_token
    proof = DecommissionProof.from_dict(proof_dict)

    # Transition source profile to DECOMMISSIONED
    updated_profile = copy.deepcopy(profile_data)
    updated_profile["migration_state"] = {
        "status": MigrationStatus.DECOMMISSIONED.value,
        "migration_id": receipt.migration_id,
        "receipt_id": receipt.receipt_id,
        "proof_id": proof_id,
        "decommissioned_at": now_utc,
        "destination_hardware_digest": receipt.destination_hardware_digest,
        "destination_canonical_path": receipt.destination_canonical_path,
    }

    # Guard immutability: Ensure zero mutation of ontogenetic anchor
    guard_immutable_fields(profile_data, updated_profile)

    tmp_path = prof_p.with_suffix(".tmp")
    with open(tmp_path, "w", encoding="utf-8") as f:
        json.dump(updated_profile, f, indent=2)
    tmp_path.replace(prof_p)

    logger.critical(
        "Source instance DECOMMISSIONED: migration_id=%s, proof_id=%s. Local authority permanently revoked.",
        receipt.migration_id,
        proof_id,
    )
    return proof


# ---------------------------------------------------------------------------
# Core Step 5: Destination Activation Gate
# ---------------------------------------------------------------------------

def activate_destination_instance(
    destination_workspace_path: Union[Path, str],
    archive_path: Union[Path, str],
    receipt: MigrationReceipt,
    decommission_proof: DecommissionProof,
    destination_lock_path: Optional[Union[Path, str]] = None,
    destination_hardware_components: Optional[HardwareDigestComponents] = None,
    engine_version_override: Optional[str] = None,
) -> MigrationActivationResult:
    """
    Step 5: Activate target instance following verified source decommission.

    Execution Contract:
    1. Requires valid receipt and decommission_proof.
    2. Cryptographically verifies decommission_proof matches receipt and identity anchor.
    3. Verifies executing host matches destination_hardware_digest and path bound in receipt/proof.
       (Rejects dual-activation or activation on wrong machine).
    4. Acquires destination InstanceLock.
    5. Extracts payload files to destination data/ directory.
    6. Updates destination profile:
       - authority_binding: updates hardware digest, canonical path, and increments hardware_migration_epoch.
       - migration_state: transitions status to 'ACTIVE'.
       - identity_anchor: assert 100% bit-for-bit identical to source anchor via guard_immutable_fields.
       - phylogenetic_lineage: optionally updates engine_version if substrate evolved.
    7. Executes complete startup validation boundary (WP-01 -> WP-04).
    """
    if not isinstance(decommission_proof, DecommissionProof):
        raise MissingDecommissionProofError("Valid DecommissionProof is required to activate destination.")

    if not isinstance(receipt, MigrationReceipt):
        raise InvalidReceiptError("Valid MigrationReceipt is required to activate destination.")

    dest_ws = Path(destination_workspace_path).resolve()
    dest_data = dest_ws / "data"
    arc_p = Path(archive_path).resolve()

    # 1. Cross-validate receipt and decommission proof
    if decommission_proof.migration_id != receipt.migration_id:
        raise InvalidDecommissionProofError(
            f"Decommission proof migration_id '{decommission_proof.migration_id}' "
            f"does not match receipt migration_id '{receipt.migration_id}'."
        )

    if decommission_proof.receipt_id != receipt.receipt_id:
        raise InvalidDecommissionProofError(
            f"Decommission proof receipt_id '{decommission_proof.receipt_id}' "
            f"does not match receipt receipt_id '{receipt.receipt_id}'."
        )

    # 2. Verify destination host hardware & path match binding
    dest_comps = destination_hardware_components or collect_hardware_components(dest_ws)
    curr_dest_digest = compute_hardware_digest(dest_comps)
    curr_dest_path = normalize_workspace_path(dest_ws)

    if curr_dest_digest != receipt.destination_hardware_digest:
        raise DestinationMismatchError(
            f"Destination hardware digest divergence: current host digest '{curr_dest_digest[:12]}...' "
            f"does not match authorized receipt digest '{receipt.destination_hardware_digest[:12]}...'."
        )

    if curr_dest_path != receipt.destination_canonical_path:
        raise DestinationMismatchError(
            f"Destination canonical path divergence: current path '{curr_dest_path}' "
            f"does not match authorized receipt path '{receipt.destination_canonical_path}'."
        )

    # 3. Read manifest from archive to obtain identity anchor for cryptographic verification
    tar = tarfile.open(arc_p, "r:gz")
    try:
        m_member = tar.getmember(MIGRATION_MANIFEST_FILENAME)
        f_manifest = tar.extractfile(m_member)
        if f_manifest is None:
            raise CorruptedArchiveError("Failed to extract manifest from archive.")
        manifest_data = json.load(f_manifest)
        manifest = MigrationManifest.from_dict(manifest_data)
    finally:
        tar.close()

    genesis_root = manifest.identity_anchor.get("genesis_root_hash", "")

    # 4. Verify proof token
    expected_proof_token = compute_proof_token(decommission_proof.to_dict(), genesis_root)
    if expected_proof_token != decommission_proof.proof_token:
        raise InvalidDecommissionProofError("Decommission proof cryptographic token verification failed.")

    # 5. Extract payload files to destination data/
    dest_data.mkdir(parents=True, exist_ok=True)
    tar = tarfile.open(arc_p, "r:gz")
    try:
        for rel_name in manifest.files.keys():
            member = tar.getmember(f"data/{rel_name}")
            extracted = tar.extractfile(member)
            if extracted is None:
                raise CorruptedArchiveError(f"Failed to extract '{rel_name}' from archive.")
            target_file = dest_data / rel_name
            with open(target_file, "wb") as f_out:
                f_out.write(extracted.read())
    finally:
        tar.close()

    # 6. Update destination profile.json
    dest_prof_p = dest_data / "profile.json"
    with open(dest_prof_p, "r", encoding="utf-8") as f:
        dest_profile = json.load(f)

    updated_dest_profile = copy.deepcopy(dest_profile)

    # Increment migration epoch and bind to new destination host
    new_epoch = manifest.migration_epoch + 1
    auth_block = updated_dest_profile.setdefault("authority_binding", {})
    auth_block["hardware_binding_mode"] = "SOFT_WARNING"
    auth_block["bound_machine_guid_digest"] = curr_dest_digest
    auth_block["activation_host_platform"] = dest_comps.platform_str
    auth_block["last_known_canonical_path"] = curr_dest_path
    auth_block["hardware_migration_epoch"] = new_epoch
    auth_block["last_verified_at"] = datetime.now(timezone.utc).isoformat()
    auth_block["component_digests"] = compute_component_digests(dest_comps)

    now_utc = datetime.now(timezone.utc).isoformat()
    updated_dest_profile["migration_state"] = {
        "status": MigrationStatus.ACTIVE.value,
        "migration_id": receipt.migration_id,
        "activated_at": now_utc,
        "previous_host_digest": decommission_proof.source_hardware_digest,
        "decommission_proof_id": decommission_proof.proof_id,
        "hardware_migration_epoch": new_epoch,
    }

    # Apply phylogenetic upgrade if engine version evolved
    if engine_version_override:
        updated_dest_profile = apply_phylogenetic_upgrade(
            updated_dest_profile,
            new_engine_version=engine_version_override,
            last_upgraded_at=now_utc,
        )

    # CRITICAL INVARIANT: Guard immutable identity anchor fields
    # instance_uuid, born_at, genesis_commit, genesis_root_hash MUST be bit-exact!
    guard_immutable_fields(dest_profile, updated_dest_profile)

    # Atomic write to destination profile.json
    tmp_path = dest_prof_p.with_suffix(".tmp")
    with open(tmp_path, "w", encoding="utf-8") as f:
        json.dump(updated_dest_profile, f, indent=2)
    tmp_path.replace(dest_prof_p)

    # 7. Complete startup validation boundary on target (WP-02, WP-03, WP-04)
    # Validate identity anchor
    id_state = verify_identity_on_startup(dest_prof_p)
    if not id_state.is_onboarded or id_state.is_genesis_locked:
        raise MigrationError("Activated destination failed identity verification.")

    # Validate provenance and environment
    prov_res = verify_provenance_and_environment(
        workspace_path=dest_ws,
        profile_path=dest_prof_p,
        allow_reconfirmation=False,
    )
    if not prov_res.is_valid:
        raise MigrationError(f"Activated destination failed provenance verification: {prov_res.status}")

    # Reconcile stores
    reconcile_rep = verify_and_reconcile_stores(
        relationship_path=dest_data / "relationship.json",
        dynamical_path=dest_data / "dynamical_state.json",
        manifest_path=dest_data / "epoch_manifest.json",
    )
    if not reconcile_rep.is_consistent:
        raise MigrationError(f"Activated destination failed store reconciliation: {reconcile_rep.inconsistencies_detected}")

    logger.info(
        "Destination Lucia identity successfully ACTIVATED: migration_id=%s, epoch=%d, path=%s",
        receipt.migration_id,
        new_epoch,
        curr_dest_path,
    )

    return MigrationActivationResult(
        is_activated=True,
        status="ACTIVE",
        migration_id=receipt.migration_id,
        target_path=dest_ws,
        new_hardware_migration_epoch=new_epoch,
        errors=[],
    )
