"""
Genesis Semantic & Protocol Contract (G1–G4).

Governing Specifications:
- ADR-034 (ARCH-034: Identity Authority, Instance Exclusivity & Anti-Branching Boundary)
- Genesis Implementation Contract (G1–G4)

Primary Architectural Purpose:
Establish and enforce the canonical origin boundary (Genesis) for Lucia.
Genesis establishes origin, not history.

Canonical Sequence:
    PRE-GENESIS
        ↓
    Preconditions + Human Authorization
        ↓
    Construct Genesis Record
        ↓
    Validate Genesis Record
        ↓
    Durable Genesis Commitment
        ║
        ║ BIRTH BOUNDARY
        ▼
    BORN
        ↓
    Verify / Recover
        ↓
    BORN + INACTIVE
        ↓
    First Activation
        ↓
    ACTIVE

Invariants & Boundary Guarantees:
- INV-1 (One Continuous Life): Anti-branching invariant. Identity is established once.
- INV-8 (Genesis Gate Invariant): Development / Simulation != Lucia Activation.
  Pre-Genesis profiles (e.g. {"is_onboarded": false}) remain Genesis-locked.
  Live data/profile.json is preserved bit-exact.
- Birth Boundary:
  Birth is defined solely by the existence of a valid durable Genesis Commitment.
  Birth is NOT UUID creation, first boot, profile modification, first activation,
  worker startup, runtime initialization, or generation of an isolated hash.
  There is NO PARTIALLY_BORN state.
- Ontological Separation:
  Ontological state (NOT_BORN -> BORN -> ENDED) is distinct from runtime state
  (INACTIVE <-> ACTIVE). BORN + INACTIVE is valid.
- Genesis Root:
  An immutable commitment to the Genesis Record. Smallest deterministic construction.
  Root MUST remain unchanged after Genesis.
- Verification Outcomes:
  VERIFIED_BORN, NOT_FOUND, UNKNOWN, INVALID_EVIDENCE.
  Fail closed on UNKNOWN or INVALID_EVIDENCE.
- Re-Genesis Guard:
  Genesis may execute only when verification establishes NOT_BORN (NOT_FOUND).
- Terminal End:
  /lifecycle/end transitions to ENDED and strictly forbids re-Genesis.
"""

from __future__ import annotations

import copy
from dataclasses import dataclass
from datetime import datetime, timezone
from enum import Enum
import hashlib
import json
import logging
import os
from pathlib import Path
from typing import Any, Dict, Optional, Tuple, Union

from src.core.identity.identity_anchor import (
    DEFAULT_PROFILE_PATH,
    IdentityAnchor,
    IdentityAnchorError,
    ImmutableIdentityMutationError,
    InvalidIdentityAnchorError,
    guard_immutable_fields,
    validate_identity_anchor,
)

logger = logging.getLogger("lucia.identity.genesis")

DEFAULT_GENESIS_COMMITMENT_PATH: Path = Path("data/genesis_commitment.json")
CANONICAL_GENESIS_PROTOCOL_VERSION: str = "G1-G4"
CANONICAL_GENESIS_SCHEMA_VERSION: str = "2.0"


# ---------------------------------------------------------------------------
# Enums
# ---------------------------------------------------------------------------

class OntologyState(str, Enum):
    """
    Ontological existence lifecycle states.
    Strictly separate from runtime activation state.
    """
    NOT_BORN = "NOT_BORN"
    BORN = "BORN"
    ENDED = "ENDED"


class RuntimeState(str, Enum):
    """
    Runtime execution state.
    Operates orthogonally to ontology. BORN + INACTIVE is valid.
    """
    INACTIVE = "INACTIVE"
    ACTIVE = "ACTIVE"


class GenesisVerificationOutcome(str, Enum):
    """
    Strict verification outcomes codified in G1–G4 §8.
    """
    VERIFIED_BORN = "VERIFIED_BORN"
    NOT_FOUND = "NOT_FOUND"
    UNKNOWN = "UNKNOWN"
    INVALID_EVIDENCE = "INVALID_EVIDENCE"


# ---------------------------------------------------------------------------
# Exceptions
# ---------------------------------------------------------------------------

class GenesisError(IdentityAnchorError):
    """Base exception for all Genesis operations and contract violations."""
    pass


class GenesisVerificationError(GenesisError):
    """Raised when Genesis verification encounters an unexpected failure."""
    pass


class ReGenesisForbiddenError(GenesisError):
    """
    Raised when Genesis is attempted on an instance that is already BORN,
    whose evidence is UNKNOWN or INVALID_EVIDENCE, or whose lifecycle has ENDED.
    """
    pass


class PreGenesisActivationForbiddenError(GenesisError):
    """
    Raised when First Activation is attempted on an instance that has not
    completed durable Genesis (ontology != BORN).
    """
    pass


class GenesisCommitmentCorruptedError(GenesisError):
    """Raised when durable Genesis commitment exists but fails integrity checks."""
    pass


class TerminalLifecycleError(GenesisError):
    """Raised when an operation is attempted on an instance whose lifecycle has ENDED."""
    pass


# ---------------------------------------------------------------------------
# Canonical Deterministic Preimage & Serialization
# ---------------------------------------------------------------------------

def canonical_json_bytes(data: Dict[str, Any]) -> bytes:
    """Return deterministic canonical UTF-8 JSON bytes (sorted keys, no spaces)."""
    return json.dumps(data, sort_keys=True, separators=(",", ":")).encode("utf-8")


def get_canonical_genesis_root_preimage(
    instance_uuid: str,
    born_at: str,
    genesis_commit: str,
    protocol_version: str = CANONICAL_GENESIS_PROTOCOL_VERSION,
    schema_version: str = CANONICAL_GENESIS_SCHEMA_VERSION,
) -> Dict[str, Any]:
    """
    Construct the canonical input dictionary for Genesis Root computation.

    Contains strictly WHO (Identity Anchor origin parameters) and
    WHEN/HOW (Genesis Provenance / Protocol Identity).
    Excludes personality, memory, relationship, PAD, or runtime state.
    """
    return {
        "genesis_provenance": {
            "genesis_protocol_identity": {
                "protocol_version": str(protocol_version),
                "schema_version": str(schema_version),
            }
        },
        "identity_anchor": {
            "born_at": str(born_at),
            "genesis_commit": str(genesis_commit),
            "instance_uuid": str(instance_uuid),
        },
    }


def compute_genesis_root(
    instance_uuid: str,
    born_at: str,
    genesis_commit: str,
    protocol_version: str = CANONICAL_GENESIS_PROTOCOL_VERSION,
    schema_version: str = CANONICAL_GENESIS_SCHEMA_VERSION,
) -> str:
    """
    Compute the deterministic Genesis Root (SHA-256 digest) over the canonical preimage.

    The Genesis Root is an immutable commitment to the Genesis Record.
    """
    preimage = get_canonical_genesis_root_preimage(
        instance_uuid=instance_uuid,
        born_at=born_at,
        genesis_commit=genesis_commit,
        protocol_version=protocol_version,
        schema_version=schema_version,
    )
    return hashlib.sha256(canonical_json_bytes(preimage)).hexdigest()


# ---------------------------------------------------------------------------
# Domain Models (Frozen Data Classes)
# ---------------------------------------------------------------------------

@dataclass(frozen=True)
class GenesisProvenance:
    """
    Minimum origin evidence required to establish WHEN / HOW / DID GENESIS COMPLETE.
    """
    protocol_version: str = CANONICAL_GENESIS_PROTOCOL_VERSION
    schema_version: str = CANONICAL_GENESIS_SCHEMA_VERSION

    def to_dict(self) -> Dict[str, Any]:
        return {
            "genesis_protocol_identity": {
                "protocol_version": self.protocol_version,
                "schema_version": self.schema_version,
            }
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "GenesisProvenance":
        gpi = data.get("genesis_protocol_identity", data)
        return cls(
            protocol_version=str(gpi.get("protocol_version", CANONICAL_GENESIS_PROTOCOL_VERSION)),
            schema_version=str(gpi.get("schema_version", CANONICAL_GENESIS_SCHEMA_VERSION)),
        )


@dataclass(frozen=True)
class GenesisRecord:
    """
    The canonical minimum Genesis Record (G2):
        Genesis Record
        ├── Identity Anchor (WHO)
        └── Genesis Provenance (WHEN / HOW / Protocol Identity)
    """
    identity_anchor: IdentityAnchor
    provenance: GenesisProvenance

    def to_dict(self) -> Dict[str, Any]:
        return {
            "identity_anchor": self.identity_anchor.to_dict(),
            "genesis_provenance": self.provenance.to_dict(),
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "GenesisRecord":
        anchor_raw = data.get("identity_anchor")
        if not anchor_raw or not isinstance(anchor_raw, dict):
            raise InvalidIdentityAnchorError("GenesisRecord missing or invalid 'identity_anchor'.")
        anchor = validate_identity_anchor(anchor_raw)
        prov_raw = data.get("genesis_provenance", {})
        provenance = GenesisProvenance.from_dict(prov_raw if isinstance(prov_raw, dict) else {})
        return cls(identity_anchor=anchor, provenance=provenance)


@dataclass(frozen=True)
class GenesisCommitment:
    """
    Single durable Genesis Commitment boundary.
    Represents the durable persistence of origin evidence establishing Birth.
    """
    record: GenesisRecord
    genesis_root_hash: str
    committed_at: str
    durable: bool = True
    ontology_state: str = OntologyState.BORN.value
    ended_at: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        res: Dict[str, Any] = {
            "format_version": "1.0",
            "record": self.record.to_dict(),
            "genesis_root_hash": self.genesis_root_hash,
            "committed_at": self.committed_at,
            "durable": self.durable,
            "ontology_state": self.ontology_state,
        }
        if self.ended_at:
            res["ended_at"] = self.ended_at
        return res

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "GenesisCommitment":
        if not isinstance(data, dict):
            raise GenesisCommitmentCorruptedError("Commitment data must be a JSON dictionary.")
        rec_data = data.get("record")
        if not rec_data or not isinstance(rec_data, dict):
            raise GenesisCommitmentCorruptedError("Commitment missing 'record' section.")
        record = GenesisRecord.from_dict(rec_data)
        root = str(data.get("genesis_root_hash", ""))
        committed_at = str(data.get("committed_at", ""))
        durable = bool(data.get("durable", True))
        ont_state = str(data.get("ontology_state", OntologyState.BORN.value))
        ended_at = data.get("ended_at")
        return cls(
            record=record,
            genesis_root_hash=root,
            committed_at=committed_at,
            durable=durable,
            ontology_state=ont_state,
            ended_at=str(ended_at) if ended_at else None,
        )


@dataclass(frozen=True)
class GenesisVerificationResult:
    """
    Comprehensive result of Genesis verification (§8).
    """
    outcome: GenesisVerificationOutcome
    ontology_state: OntologyState
    commitment: Optional[GenesisCommitment] = None
    error_details: Optional[str] = None


# ---------------------------------------------------------------------------
# Validation & Integrity Verification
# ---------------------------------------------------------------------------

def verify_genesis_record_integrity(record: GenesisRecord) -> bool:
    """
    Verify that the Genesis Record matches its Genesis Root hash.
    """
    expected_root = compute_genesis_root(
        instance_uuid=record.identity_anchor.instance_uuid,
        born_at=record.identity_anchor.born_at,
        genesis_commit=record.identity_anchor.genesis_commit,
        protocol_version=record.provenance.protocol_version,
        schema_version=record.provenance.schema_version,
    )
    return expected_root == record.identity_anchor.genesis_root_hash


def build_genesis_record(
    instance_uuid: str,
    born_at: str,
    genesis_commit: str,
    provenance: Optional[GenesisProvenance] = None,
) -> GenesisRecord:
    """
    Construct and validate a minimum Genesis Record with deterministic Genesis Root.
    """
    prov = provenance or GenesisProvenance()
    root_hash = compute_genesis_root(
        instance_uuid=instance_uuid,
        born_at=born_at,
        genesis_commit=genesis_commit,
        protocol_version=prov.protocol_version,
        schema_version=prov.schema_version,
    )
    anchor = validate_identity_anchor({
        "instance_uuid": instance_uuid,
        "born_at": born_at,
        "genesis_commit": genesis_commit,
        "genesis_root_hash": root_hash,
    })
    record = GenesisRecord(identity_anchor=anchor, provenance=prov)
    if not verify_genesis_record_integrity(record):
        raise InvalidIdentityAnchorError("Genesis Record integrity validation failed upon construction.")
    return record


# ---------------------------------------------------------------------------
# Verification Engine (G1–G4 §8)
# ---------------------------------------------------------------------------

def verify_genesis(
    workspace_dir: Optional[Union[Path, str]] = None,
    commitment_path: Optional[Union[Path, str]] = None,
    profile_path: Optional[Union[Path, str]] = None,
) -> GenesisVerificationResult:
    """
    Execute authoritative local Genesis verification.

    Exposes exact verification outcomes:
    - VERIFIED_BORN: Commitment exists, Record <-> Root integrity is valid, durable evidence available.
    - NOT_FOUND: Authoritative local evidence establishes no Genesis Commitment exists (Ontology = NOT_BORN).
    - UNKNOWN: Storage temporarily unavailable / I/O failure / evidence unreadable. Fail closed.
    - INVALID_EVIDENCE: Evidence exists but fails integrity validation. Fail closed, never overwrite.
    """
    ws = Path(workspace_dir).resolve() if workspace_dir else None
    c_path = Path(commitment_path).resolve() if commitment_path else (
        (ws / "data" / "genesis_commitment.json") if ws else DEFAULT_GENESIS_COMMITMENT_PATH.resolve()
    )
    p_path = Path(profile_path).resolve() if profile_path else (
        (ws / "data" / "profile.json") if ws else (
            (c_path.parent / "profile.json") if commitment_path else DEFAULT_PROFILE_PATH.resolve()
        )
    )

    # 1. Check if commitment file exists on disk
    if not c_path.exists():
        # Check profile file evidence
        if not p_path.exists():
            return GenesisVerificationResult(
                outcome=GenesisVerificationOutcome.NOT_FOUND,
                ontology_state=OntologyState.NOT_BORN,
                commitment=None,
                error_details="Neither genesis_commitment.json nor profile.json exists. Pre-Genesis state.",
            )

        try:
            with open(p_path, "r", encoding="utf-8") as f:
                raw_prof = json.load(f)
        except Exception as exc:
            return GenesisVerificationResult(
                outcome=GenesisVerificationOutcome.UNKNOWN,
                ontology_state=OntologyState.NOT_BORN,
                commitment=None,
                error_details=f"Failed to read profile at '{p_path}': {exc}",
            )

        if not isinstance(raw_prof, dict):
            return GenesisVerificationResult(
                outcome=GenesisVerificationOutcome.INVALID_EVIDENCE,
                ontology_state=OntologyState.NOT_BORN,
                commitment=None,
                error_details=f"Profile at '{p_path}' is not a JSON dictionary.",
            )

        # Check for un-onboarded / pre-Genesis profile
        is_onboarded = bool(raw_prof.get("is_onboarded", False))
        has_anchor = "identity_anchor" in raw_prof and raw_prof["identity_anchor"] is not None
        ont_field = raw_prof.get("ontology_state")

        if ont_field == OntologyState.ENDED.value:
            return GenesisVerificationResult(
                outcome=GenesisVerificationOutcome.VERIFIED_BORN,
                ontology_state=OntologyState.ENDED,
                commitment=None,
                error_details="Instance lifecycle has ENDED (terminal state).",
            )

        if not is_onboarded and not has_anchor:
            return GenesisVerificationResult(
                outcome=GenesisVerificationOutcome.NOT_FOUND,
                ontology_state=OntologyState.NOT_BORN,
                commitment=None,
                error_details="Authoritative local evidence confirms pre-Genesis profile ({'is_onboarded': false}).",
            )

        # Contradiction: profile has identity anchor or is_onboarded=True, but commitment file missing
        return GenesisVerificationResult(
            outcome=GenesisVerificationOutcome.INVALID_EVIDENCE,
            ontology_state=OntologyState.NOT_BORN,
            commitment=None,
            error_details="Profile contains initialized anchor/onboarded flag, but durable genesis_commitment.json is missing.",
        )

    # 2. Commitment file exists: read and validate
    try:
        # Check for empty file
        if c_path.stat().st_size == 0:
            return GenesisVerificationResult(
                outcome=GenesisVerificationOutcome.INVALID_EVIDENCE,
                ontology_state=OntologyState.NOT_BORN,
                commitment=None,
                error_details=f"Commitment file '{c_path}' exists but has 0 bytes (corrupted/truncated).",
            )

        with open(c_path, "r", encoding="utf-8") as f:
            raw_commit = json.load(f)
    except PermissionError as exc:
        return GenesisVerificationResult(
            outcome=GenesisVerificationOutcome.UNKNOWN,
            ontology_state=OntologyState.NOT_BORN,
            commitment=None,
            error_details=f"Permission denied reading commitment file '{c_path}': {exc}",
        )
    except (json.JSONDecodeError, UnicodeDecodeError) as exc:
        return GenesisVerificationResult(
            outcome=GenesisVerificationOutcome.INVALID_EVIDENCE,
            ontology_state=OntologyState.NOT_BORN,
            commitment=None,
            error_details=f"Corrupted JSON in commitment file '{c_path}': {exc}",
        )
    except OSError as exc:
        return GenesisVerificationResult(
            outcome=GenesisVerificationOutcome.UNKNOWN,
            ontology_state=OntologyState.NOT_BORN,
            commitment=None,
            error_details=f"I/O error reading commitment file '{c_path}': {exc}",
        )

    if not isinstance(raw_commit, dict):
        return GenesisVerificationResult(
            outcome=GenesisVerificationOutcome.INVALID_EVIDENCE,
            ontology_state=OntologyState.NOT_BORN,
            commitment=None,
            error_details=f"Commitment file '{c_path}' does not contain a JSON dictionary.",
        )

    # 3. Parse commitment and validate record integrity
    try:
        commitment = GenesisCommitment.from_dict(raw_commit)
    except (GenesisError, InvalidIdentityAnchorError, ValueError) as exc:
        return GenesisVerificationResult(
            outcome=GenesisVerificationOutcome.INVALID_EVIDENCE,
            ontology_state=OntologyState.NOT_BORN,
            commitment=None,
            error_details=f"Commitment schema validation failed: {exc}",
        )

    # Validate Record <-> Root integrity
    if not verify_genesis_record_integrity(commitment.record):
        return GenesisVerificationResult(
            outcome=GenesisVerificationOutcome.INVALID_EVIDENCE,
            ontology_state=OntologyState.NOT_BORN,
            commitment=None,
            error_details="Genesis Record <-> Genesis Root integrity check failed.",
        )

    if commitment.record.identity_anchor.genesis_root_hash != commitment.genesis_root_hash:
        return GenesisVerificationResult(
            outcome=GenesisVerificationOutcome.INVALID_EVIDENCE,
            ontology_state=OntologyState.NOT_BORN,
            commitment=None,
            error_details="Commitment genesis_root_hash diverges from identity_anchor.genesis_root_hash.",
        )

    # Check terminal ENDED state
    if commitment.ontology_state == OntologyState.ENDED.value:
        return GenesisVerificationResult(
            outcome=GenesisVerificationOutcome.VERIFIED_BORN,
            ontology_state=OntologyState.ENDED,
            commitment=commitment,
            error_details="Instance lifecycle has ENDED (terminal).",
        )

    # 4. Valid durable commitment verified
    return GenesisVerificationResult(
        outcome=GenesisVerificationOutcome.VERIFIED_BORN,
        ontology_state=OntologyState.BORN,
        commitment=commitment,
        error_details=None,
    )


# ---------------------------------------------------------------------------
# Durable Commitment & Ceremony Execution
# ---------------------------------------------------------------------------

def commit_genesis(
    record: GenesisRecord,
    workspace_dir: Optional[Union[Path, str]] = None,
    commitment_path: Optional[Union[Path, str]] = None,
    profile_path: Optional[Union[Path, str]] = None,
) -> GenesisCommitment:
    """
    Establish durable Genesis Commitment using atomic local filesystem primitive.

    Birth Boundary Guarantee:
    - Atomically writes commitment payload to .tmp, fsyncs, and replaces destination.
    - If a crash occurs before fsync/replace, the commitment does NOT exist (NOT_BORN).
    - Only after durable persistence is confirmed is Birth established.
    """
    if not verify_genesis_record_integrity(record):
        raise InvalidIdentityAnchorError("Cannot commit: Genesis Record <-> Genesis Root integrity mismatch.")

    ws = Path(workspace_dir).resolve() if workspace_dir else None
    c_path = Path(commitment_path).resolve() if commitment_path else (
        (ws / "data" / "genesis_commitment.json") if ws else DEFAULT_GENESIS_COMMITMENT_PATH.resolve()
    )
    p_path = Path(profile_path).resolve() if profile_path else (
        (ws / "data" / "profile.json") if ws else (
            (c_path.parent / "profile.json") if commitment_path else DEFAULT_PROFILE_PATH.resolve()
        )
    )

    c_path.parent.mkdir(parents=True, exist_ok=True)
    p_path.parent.mkdir(parents=True, exist_ok=True)

    committed_at = datetime.now(timezone.utc).isoformat()
    commitment = GenesisCommitment(
        record=record,
        genesis_root_hash=record.identity_anchor.genesis_root_hash,
        committed_at=committed_at,
        durable=True,
        ontology_state=OntologyState.BORN.value,
    )

    raw_bytes = json.dumps(commitment.to_dict(), indent=2, sort_keys=True).encode("utf-8")
    tmp_path = c_path.with_suffix(".tmp")

    # Atomic durable write: write -> fsync -> replace
    fd = os.open(str(tmp_path), os.O_WRONLY | os.O_CREAT | os.O_TRUNC, 0o600)
    try:
        os.write(fd, raw_bytes)
        os.fsync(fd)
    finally:
        os.close(fd)

    os.replace(tmp_path, c_path)

    # Synchronize profile.json if present
    try:
        existing_profile: Dict[str, Any] = {}
        if p_path.exists():
            with open(p_path, "r", encoding="utf-8") as f:
                existing_profile = json.load(f)
                if not isinstance(existing_profile, dict):
                    existing_profile = {}

        updated_profile = copy.deepcopy(existing_profile)
        updated_profile["is_onboarded"] = True
        updated_profile["identity_anchor"] = record.identity_anchor.to_dict()
        updated_profile["born_at"] = record.identity_anchor.born_at
        updated_profile["ontology_state"] = OntologyState.BORN.value

        guard_immutable_fields(existing_profile, updated_profile)

        p_tmp = p_path.with_suffix(".tmp")
        p_bytes = json.dumps(updated_profile, indent=2, sort_keys=True, ensure_ascii=False).encode("utf-8")
        p_fd = os.open(str(p_tmp), os.O_WRONLY | os.O_CREAT | os.O_TRUNC, 0o600)
        try:
            os.write(p_fd, p_bytes)
            os.fsync(p_fd)
        finally:
            os.close(p_fd)
        os.replace(p_tmp, p_path)

        # Establish initial host authority binding for ADR-034
        try:
            from src.core.identity.provenance_verifier import reconfirm_hardware_environment
            reconfirm_hardware_environment(
                profile_path=p_path,
                current_workspace_path=ws,
            )
        except Exception as p_exc:
            logger.warning("Could not establish initial authority binding during Genesis: %s", p_exc)
    except Exception as exc:
        logger.warning("Could not synchronize profile during commitment: %s", exc)

    logger.info("Durable Genesis Commitment established at %s (root=%s...)", c_path, record.identity_anchor.genesis_root_hash[:12])
    return commitment


def execute_genesis(
    instance_uuid: str,
    born_at: str,
    genesis_commit: str,
    workspace_dir: Optional[Union[Path, str]] = None,
    commitment_path: Optional[Union[Path, str]] = None,
    profile_path: Optional[Union[Path, str]] = None,
    provenance: Optional[GenesisProvenance] = None,
) -> GenesisCommitment:
    """
    Execute the Genesis sequence under Re-Genesis Guard (§10).

    Precondition:
    - Genesis may execute ONLY when verification establishes NOT_FOUND (Ontology = NOT_BORN).
    - Fails closed on VERIFIED_BORN, UNKNOWN, INVALID_EVIDENCE, or ENDED.
    """
    verification = verify_genesis(
        workspace_dir=workspace_dir,
        commitment_path=commitment_path,
        profile_path=profile_path,
    )

    if verification.ontology_state == OntologyState.ENDED:
        raise TerminalLifecycleError(
            "Genesis forbidden: Instance lifecycle has ENDED. /lifecycle/end is terminal and re-Genesis is strictly forbidden."
        )

    if verification.outcome == GenesisVerificationOutcome.VERIFIED_BORN:
        raise ReGenesisForbiddenError(
            "Genesis forbidden: Instance is already VERIFIED_BORN. Lucia is one continuous life; re-Genesis is strictly prohibited."
        )

    if verification.outcome == GenesisVerificationOutcome.UNKNOWN:
        raise ReGenesisForbiddenError(
            f"Genesis forbidden: Verification outcome is UNKNOWN ({verification.error_details}). Fail closed."
        )

    if verification.outcome == GenesisVerificationOutcome.INVALID_EVIDENCE:
        raise ReGenesisForbiddenError(
            f"Genesis forbidden: Corrupted Genesis evidence detected (INVALID_EVIDENCE: {verification.error_details}). "
            "Corrupted evidence must NEVER be overwritten or re-Genesised. Fail closed."
        )

    if verification.outcome != GenesisVerificationOutcome.NOT_FOUND:
        raise ReGenesisForbiddenError(f"Genesis forbidden: Unexpected verification outcome '{verification.outcome}'.")

    # Construct validated minimum Genesis Record
    record = build_genesis_record(
        instance_uuid=instance_uuid,
        born_at=born_at,
        genesis_commit=genesis_commit,
        provenance=provenance,
    )

    # Persist durable Genesis Commitment
    return commit_genesis(
        record=record,
        workspace_dir=workspace_dir,
        commitment_path=commitment_path,
        profile_path=profile_path,
    )


def recover_genesis(
    workspace_dir: Optional[Union[Path, str]] = None,
    commitment_path: Optional[Union[Path, str]] = None,
    profile_path: Optional[Union[Path, str]] = None,
) -> GenesisVerificationResult:
    """
    Verify / recover Genesis state upon system startup or after crash.

    Non-destructive: Does NOT mutate, overwrite, or delete existing evidence.
    """
    return verify_genesis(
        workspace_dir=workspace_dir,
        commitment_path=commitment_path,
        profile_path=profile_path,
    )


def mark_lifecycle_ended(
    workspace_dir: Optional[Union[Path, str]] = None,
    commitment_path: Optional[Union[Path, str]] = None,
    profile_path: Optional[Union[Path, str]] = None,
) -> None:
    """
    Mark instance ontology as terminal ENDED (§7).

    Guarantees that re-Genesis and activation are permanently forbidden.
    """
    ws = Path(workspace_dir).resolve() if workspace_dir else None
    c_path = Path(commitment_path).resolve() if commitment_path else (
        (ws / "data" / "genesis_commitment.json") if ws else DEFAULT_GENESIS_COMMITMENT_PATH.resolve()
    )
    p_path = Path(profile_path).resolve() if profile_path else (
        (ws / "data" / "profile.json") if ws else (
            (c_path.parent / "profile.json") if commitment_path else DEFAULT_PROFILE_PATH.resolve()
        )
    )

    ended_at = datetime.now(timezone.utc).isoformat()

    # Update commitment file if it exists
    if c_path.exists():
        try:
            with open(c_path, "r", encoding="utf-8") as f:
                c_data = json.load(f)
            if isinstance(c_data, dict):
                c_data["ontology_state"] = OntologyState.ENDED.value
                c_data["ended_at"] = ended_at
                tmp = c_path.with_suffix(".tmp")
                with open(tmp, "w", encoding="utf-8") as f:
                    json.dump(c_data, f, indent=2)
                os.replace(tmp, c_path)
        except Exception as exc:
            logger.warning("Failed to mark commitment as ended: %s", exc)

    # Update profile file
    if p_path.exists():
        try:
            with open(p_path, "r", encoding="utf-8") as f:
                p_data = json.load(f)
            if isinstance(p_data, dict):
                p_data["ontology_state"] = OntologyState.ENDED.value
                p_data["ended_at"] = ended_at
                tmp = p_path.with_suffix(".tmp")
                with open(tmp, "w", encoding="utf-8") as f:
                    json.dump(p_data, f, indent=2)
                os.replace(tmp, p_path)
        except Exception as exc:
            logger.warning("Failed to mark profile as ended: %s", exc)
