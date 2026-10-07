"""
Immutable Identity Anchor & Lineage Separation (WP-02).

Governing ADR: ADR-034 (Identity Authority, Instance Exclusivity & Anti-Branching Boundary).
Reference: docs/others/IDENTITY_AUTHORITY_SPECIFICATION/IDENTITY_AUTHORITY_SPEC_V01.md
Plan Reference: docs/others/IDENTITY_AUTHORITY_SPECIFICATION/IMPLEMENTATION_PLAN.md

Primary Architectural Purpose:
Establish the persistent cryptographic identity root that identifies ONE Lucia individual
across software engine updates and model weight replacements without conflating ontogenetic
identity with relationship, covenant, or runtime state.

Tripartite Ontological Boundary (Ontology B):
    Identity State != Relationship State != Covenant State

Boundary & Invariant Guarantees:
- INV-1 (One Continuous Life): The IdentityAnchor is created once at Genesis and remains
  permanently immutable for the entire lifespan of the individual.
- INV-8 (Genesis Gate Invariant): Development / Simulation != Lucia Activation.
  Pre-Genesis profiles (e.g. `{"is_onboarded": false}`) are Genesis-locked. Ordinary startup
  must NEVER silently generate an identity anchor or mutate the Genesis-locked profile.
- Ontogenetic vs. Phylogenetic Separation:
  IdentityAnchor fields (instance_uuid, born_at, genesis_commit, genesis_root_hash) are
  strictly immutable. Phylogenetic lineage fields (engine_version, last_upgraded_at,
  compatible_schema_major) evolve across software releases and preserve the identity anchor bit-for-bit.
- Fail-Closed Semantics:
  Any corruption, missing required field, syntactic invalidity, or attempted mutation
  of an initialized identity anchor results in immediate fail-closed termination.
"""

from __future__ import annotations

import copy
from dataclasses import dataclass
from datetime import datetime, timezone
import json
import logging
from pathlib import Path
import re
from typing import Any, Dict, Optional, Set, Tuple, Union
import uuid

logger = logging.getLogger("lucia.identity.anchor")

DEFAULT_PROFILE_PATH: Path = Path("data/profile.json")
CANONICAL_SCHEMA_VERSION: str = "2.0"
COMPATIBLE_SCHEMA_MAJORS: Set[int] = {1, 2}

IMMUTABLE_IDENTITY_FIELDS: Tuple[str, ...] = (
    "instance_uuid",
    "born_at",
    "genesis_commit",
    "genesis_root_hash",
)

# Git commit SHA regex: 40-character hex (SHA-1) or 64-character hex (SHA-256)
_COMMIT_HEX_PATTERN: re.Pattern = re.compile(r"^[0-9a-fA-F]{40}$|^[0-9a-fA-F]{64}$")

# Cryptographic root digest regex: 64-character hex (SHA-256)
_ROOT_HASH_PATTERN: re.Pattern = re.compile(r"^[0-9a-fA-F]{64}$")

# Status of genesis root hash generation ceremony
GENESIS_ROOT_HASH_STATUS: str = "DEFERRED — GENESIS CREATION CEREMONY REQUIRED"


# ---------------------------------------------------------------------------
# Exceptions
# ---------------------------------------------------------------------------

class IdentityAnchorError(RuntimeError):
    """Base exception for all Identity Anchor operations and integrity errors."""
    pass


class InvalidIdentityAnchorError(IdentityAnchorError):
    """
    Raised when an initialized identity anchor is missing required fields,
    contains syntactically/cryptographically invalid data, or violates schema rules.
    """
    pass


class CorruptedIdentityAnchorError(InvalidIdentityAnchorError):
    """Raised when an identity anchor file on disk cannot be read or is corrupted."""
    pass


class ImmutableIdentityMutationError(IdentityAnchorError):
    """
    Raised when an operation attempts to mutate or delete immutable identity anchor
    fields (instance_uuid, born_at, genesis_commit, genesis_root_hash) on an
    initialized identity profile.
    """
    pass


class UninitializedIdentityError(IdentityAnchorError):
    """
    Raised when an operation requires an initialized identity anchor, but the
    instance is still in a pre-Genesis locked state.
    """
    pass


class DecommissionedInstanceError(IdentityAnchorError):
    """
    Raised when an operation attempts to run or validate an identity instance that
    has been decommissioned via an authorized migration transfer.
    """
    pass


class FrozenMigrationStateError(IdentityAnchorError):
    """
    Raised when normal execution is attempted on an identity instance that is
    currently frozen pending a migration transaction.
    """
    pass


# ---------------------------------------------------------------------------
# Domain Models (Frozen Data Classes)
# ---------------------------------------------------------------------------

@dataclass(frozen=True)
class IdentityAnchor:
    """
    Persistent ontogenetic identity root for a single Lucia individual.

    Established strictly and once during the Genesis Onboarding Ceremony.
    Permanently immutable across all subsequent software engine upgrades,
    model weight replacements, or dependency updates.

    Fields answer strictly: "Which Lucia individual is this?"
    """

    instance_uuid: str
    born_at: str
    genesis_commit: str
    genesis_root_hash: str

    def to_dict(self) -> Dict[str, str]:
        """Return canonical dictionary representation of the anchor."""
        return {
            "instance_uuid": self.instance_uuid,
            "born_at": self.born_at,
            "genesis_commit": self.genesis_commit,
            "genesis_root_hash": self.genesis_root_hash,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "IdentityAnchor":
        """Instantiate from dictionary without validation (use validate_identity_anchor)."""
        return cls(
            instance_uuid=str(data.get("instance_uuid", "")),
            born_at=str(data.get("born_at", "")),
            genesis_commit=str(data.get("genesis_commit", "")),
            genesis_root_hash=str(data.get("genesis_root_hash", "")),
        )


@dataclass(frozen=True)
class PhylogeneticLineage:
    """
    Evolving computational substrate metadata.

    Answers: "Which software engine and schema revision is running this individual?"
    Changes dynamically upon software upgrades and refactors without mutating the IdentityAnchor.
    """

    engine_version: str
    last_upgraded_at: str
    compatible_schema_major: int = 2

    def to_dict(self) -> Dict[str, Any]:
        """Return canonical dictionary representation of phylogenetic metadata."""
        return {
            "engine_version": self.engine_version,
            "last_upgraded_at": self.last_upgraded_at,
            "compatible_schema_major": self.compatible_schema_major,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "PhylogeneticLineage":
        """Instantiate from dictionary."""
        return cls(
            engine_version=str(data.get("engine_version", "")),
            last_upgraded_at=str(data.get("last_upgraded_at", "")),
            compatible_schema_major=int(data.get("compatible_schema_major", 2)),
        )


@dataclass(frozen=True)
class IdentityProfileState:
    """
    Parsed identity state derived from profile storage.

    Distinguishes pre-Genesis locked profile from an initialized companion identity.
    """

    is_onboarded: bool
    is_genesis_locked: bool
    anchor: Optional[IdentityAnchor]
    lineage: Optional[PhylogeneticLineage]
    schema_version: Optional[str] = None
    raw_profile: Optional[Dict[str, Any]] = None
    migration_status: Optional[str] = None


# ---------------------------------------------------------------------------
# Field-Level Validators
# ---------------------------------------------------------------------------

def validate_instance_uuid(val: Any) -> str:
    """
    Validate that instance_uuid is a valid RFC 4122 canonical UUID string or URN.

    Fails closed with InvalidIdentityAnchorError if malformed.
    """
    if not isinstance(val, str) or not val.strip():
        raise InvalidIdentityAnchorError("Field 'instance_uuid' must be a non-empty string.")

    cleaned = val.strip()
    # Check for urn:uuid: prefix
    uuid_str = cleaned[9:] if cleaned.lower().startswith("urn:uuid:") else cleaned

    try:
        parsed = uuid.UUID(uuid_str)
    except (ValueError, AttributeError) as exc:
        raise InvalidIdentityAnchorError(
            f"Invalid UUID representation for 'instance_uuid': '{val}'. "
            f"Must be a valid canonical RFC 4122 UUID."
        ) from exc

    # Ensure canonical hyphenated representation matches parsed hex
    canonical_hex = parsed.hex
    normalized_input = uuid_str.replace("-", "").lower()
    if normalized_input != canonical_hex:
        raise InvalidIdentityAnchorError(
            f"Malformed UUID representation for 'instance_uuid': '{val}'."
        )

    return cleaned


def validate_born_at(val: Any) -> str:
    """
    Validate that born_at is a canonical ISO-8601 timestamp string.

    Fails closed with InvalidIdentityAnchorError if malformed.
    """
    if not isinstance(val, str) or not val.strip():
        raise InvalidIdentityAnchorError("Field 'born_at' must be a non-empty string.")

    cleaned = val.strip()
    iso_candidate = cleaned.replace("Z", "+00:00")
    try:
        dt = datetime.fromisoformat(iso_candidate)
    except (ValueError, TypeError) as exc:
        raise InvalidIdentityAnchorError(
            f"Invalid timestamp representation for 'born_at': '{val}'. "
            f"Must be a valid ISO-8601 UTC timestamp."
        ) from exc

    if dt.year < 2020:
        raise InvalidIdentityAnchorError(
            f"Timestamp 'born_at' ({val}) is before project epoch (2020)."
        )

    return cleaned


def validate_genesis_commit(val: Any) -> str:
    """
    Validate that genesis_commit is a 40-char (SHA-1) or 64-char (SHA-256) git commit SHA.

    Fails closed with InvalidIdentityAnchorError if malformed.
    """
    if not isinstance(val, str) or not val.strip():
        raise InvalidIdentityAnchorError("Field 'genesis_commit' must be a non-empty string.")

    cleaned = val.strip()
    if not _COMMIT_HEX_PATTERN.match(cleaned):
        raise InvalidIdentityAnchorError(
            f"Invalid git commit hash for 'genesis_commit': '{val}'. "
            f"Must be a 40-character (SHA-1) or 64-character (SHA-256) hexadecimal SHA."
        )

    return cleaned


def validate_genesis_root_hash(val: Any) -> str:
    """
    Validate that genesis_root_hash is a 64-character SHA-256 hexadecimal digest.

    Fails closed with InvalidIdentityAnchorError if malformed.
    """
    if not isinstance(val, str) or not val.strip():
        raise InvalidIdentityAnchorError("Field 'genesis_root_hash' must be a non-empty string.")

    cleaned = val.strip()
    if not _ROOT_HASH_PATTERN.match(cleaned):
        raise InvalidIdentityAnchorError(
            f"Invalid cryptographic digest for 'genesis_root_hash': '{val}'. "
            f"Must be a 64-character SHA-256 hexadecimal digest."
        )

    return cleaned


# ---------------------------------------------------------------------------
# Anchor & Profile Validation
# ---------------------------------------------------------------------------

def validate_identity_anchor(data: Union[IdentityAnchor, Dict[str, Any]]) -> IdentityAnchor:
    """
    Validate an initialized Identity Anchor block.

    Verifies:
    - All required immutable fields exist (instance_uuid, born_at, genesis_commit, genesis_root_hash).
    - instance_uuid is a valid RFC 4122 UUID.
    - born_at is a canonical ISO-8601 timestamp.
    - genesis_commit is a 40-char or 64-char hex commit hash.
    - genesis_root_hash is a 64-char hex SHA-256 digest.

    Fails closed on any defect. Never auto-generates replacement values.
    """
    if isinstance(data, IdentityAnchor):
        raw_dict = data.to_dict()
    elif isinstance(data, dict):
        raw_dict = data
    else:
        raise InvalidIdentityAnchorError(
            f"Expected dict or IdentityAnchor, got {type(data).__name__}."
        )

    for field in IMMUTABLE_IDENTITY_FIELDS:
        if field not in raw_dict or raw_dict[field] is None:
            raise InvalidIdentityAnchorError(
                f"Missing required immutable identity field: '{field}'."
            )
        if isinstance(raw_dict[field], str) and not raw_dict[field].strip():
            raise InvalidIdentityAnchorError(
                f"Required immutable identity field '{field}' is empty."
            )

    valid_uuid = validate_instance_uuid(raw_dict["instance_uuid"])
    valid_born_at = validate_born_at(raw_dict["born_at"])
    valid_commit = validate_genesis_commit(raw_dict["genesis_commit"])
    valid_root_hash = validate_genesis_root_hash(raw_dict["genesis_root_hash"])

    return IdentityAnchor(
        instance_uuid=valid_uuid,
        born_at=valid_born_at,
        genesis_commit=valid_commit,
        genesis_root_hash=valid_root_hash,
    )


def validate_profile_identity(
    profile_data: Dict[str, Any],
    allow_frozen: bool = False,
    allow_decommissioned: bool = False,
) -> IdentityProfileState:
    """
    Validate the identity state of a Lucia profile dictionary.

    Three distinct cases:
    1. Pre-Genesis / LOCKED:
       `is_onboarded` is False and `identity_anchor` is absent.
       Valid state. Returns IdentityProfileState(is_genesis_locked=True, anchor=None).
       Zero identity is synthesized.
    2. Inconsistent / Corrupted:
       - `is_onboarded: true` but `identity_anchor` is missing.
       - `is_onboarded: false` but `identity_anchor` is present.
       Fails closed with InvalidIdentityAnchorError.
    3. Initialized Identity:
       - `is_onboarded: true` and `identity_anchor` is present.
       Validates migration status (rejects DECOMMISSIONED or FROZEN unless allowed).
       Validates schema version compatibility, all anchor fields, and phylogenetic lineage.
       Returns IdentityProfileState(is_genesis_locked=False, anchor=validated_anchor).
    """
    if not isinstance(profile_data, dict):
        raise InvalidIdentityAnchorError(
            f"Profile data must be a dictionary, got {type(profile_data).__name__}."
        )

    is_onboarded = bool(profile_data.get("is_onboarded", False))
    has_anchor = "identity_anchor" in profile_data and profile_data["identity_anchor"] is not None

    # Case 1: Pre-Genesis / Locked state
    if not is_onboarded and not has_anchor:
        lineage = None
        if "phylogenetic_lineage" in profile_data and isinstance(profile_data["phylogenetic_lineage"], dict):
            lineage = PhylogeneticLineage.from_dict(profile_data["phylogenetic_lineage"])

        schema_version = str(profile_data.get("schema_version", profile_data.get("version", "1")))
        return IdentityProfileState(
            is_onboarded=False,
            is_genesis_locked=True,
            anchor=None,
            lineage=lineage,
            schema_version=schema_version,
            raw_profile=profile_data,
        )

    # Case 2: Inconsistent state (contradiction between is_onboarded and anchor presence)
    if not is_onboarded and has_anchor:
        raise InvalidIdentityAnchorError(
            "Inconsistent profile state: 'identity_anchor' is present while 'is_onboarded' is False. "
            "Identity anchor must not exist on an un-onboarded profile."
        )

    if is_onboarded and not has_anchor:
        raise InvalidIdentityAnchorError(
            "Corrupted profile state: 'is_onboarded' is True but 'identity_anchor' is missing. "
            "Failing closed to prevent unanchored companion instantiation."
        )

    # Case 3: Initialized identity
    # Check migration status
    mig_block = profile_data.get("migration_state")
    mig_status = None
    if isinstance(mig_block, dict):
        mig_status = str(mig_block.get("status", "")).upper()
        if mig_status == "DECOMMISSIONED" and not allow_decommissioned:
            raise DecommissionedInstanceError(
                f"Instance was decommissioned on {mig_block.get('decommissioned_at', 'unknown date')} "
                f"via authorized migration (id={mig_block.get('migration_id', 'unknown')}). "
                f"Authority permanently transferred to destination host. "
                f"Execution refused to prevent dual-authority split-brain."
            )
        elif mig_status == "FROZEN" and not allow_frozen:
            raise FrozenMigrationStateError(
                f"Instance is currently frozen pending migration (id={mig_block.get('migration_id', 'unknown')}). "
                f"Normal execution refused while migration transaction is in progress."
            )

    raw_schema_ver = profile_data.get("schema_version", profile_data.get("version", "2.0"))
    try:
        major_str = str(raw_schema_ver).split(".")[0]
        major_ver = int(major_str)
        if major_ver not in COMPATIBLE_SCHEMA_MAJORS:
            raise InvalidIdentityAnchorError(
                f"Incompatible profile schema version: '{raw_schema_ver}'. "
                f"Supported major revisions: {sorted(list(COMPATIBLE_SCHEMA_MAJORS))}."
            )
    except (ValueError, IndexError) as exc:
        raise InvalidIdentityAnchorError(
            f"Unparseable profile schema version: '{raw_schema_ver}'."
        ) from exc

    # Validate the anchor block
    anchor = validate_identity_anchor(profile_data["identity_anchor"])

    # Parse lineage if present
    lineage = None
    if "phylogenetic_lineage" in profile_data and isinstance(profile_data["phylogenetic_lineage"], dict):
        lineage = PhylogeneticLineage.from_dict(profile_data["phylogenetic_lineage"])

    return IdentityProfileState(
        is_onboarded=True,
        is_genesis_locked=False,
        anchor=anchor,
        lineage=lineage,
        schema_version=str(raw_schema_ver),
        raw_profile=profile_data,
        migration_status=mig_status,
    )


# ---------------------------------------------------------------------------
# Immutability Guard Mechanism
# ---------------------------------------------------------------------------

def guard_immutable_fields(
    existing_profile: Dict[str, Any],
    updated_profile: Dict[str, Any],
) -> None:
    """
    Guard initialized identity anchor fields against silent or explicit mutation.

    If existing_profile contains an initialized identity anchor:
    - updated_profile MUST contain an identical identity_anchor block.
    - Any divergence in instance_uuid, born_at, genesis_commit, or genesis_root_hash
      raises ImmutableIdentityMutationError.
    - Attempting to delete identity_anchor raises ImmutableIdentityMutationError.
    - Attempting to flip is_onboarded from True to False raises ImmutableIdentityMutationError.

    Updates to phylogenetic_lineage or general user preferences (user_name, pronouns)
    are permitted and do not raise errors.
    """
    if not isinstance(existing_profile, dict) or not isinstance(updated_profile, dict):
        return

    existing_anchor_raw = existing_profile.get("identity_anchor")
    if existing_anchor_raw is None:
        # Pre-Genesis profile; no initialized immutable anchor to guard yet
        return

    # Existing profile has an initialized identity anchor
    if "identity_anchor" not in updated_profile or updated_profile["identity_anchor"] is None:
        raise ImmutableIdentityMutationError(
            "Attempted deletion of initialized identity_anchor. "
            "An initialized companion identity anchor is permanently immutable under ADR-034."
        )

    updated_anchor_raw = updated_profile["identity_anchor"]

    # Convert to standard dict for comparison
    existing_dict = (
        existing_anchor_raw.to_dict()
        if isinstance(existing_anchor_raw, IdentityAnchor)
        else dict(existing_anchor_raw)
    )
    updated_dict = (
        updated_anchor_raw.to_dict()
        if isinstance(updated_anchor_raw, IdentityAnchor)
        else dict(updated_anchor_raw)
    )

    for field in IMMUTABLE_IDENTITY_FIELDS:
        existing_val = str(existing_dict.get(field, ""))
        updated_val = str(updated_dict.get(field, ""))
        if existing_val != updated_val:
            raise ImmutableIdentityMutationError(
                f"Attempted mutation of immutable identity anchor field '{field}': "
                f"existing='{existing_val}' -> attempted='{updated_val}'. "
                f"Identity anchor fields are permanently immutable under ADR-034."
            )

    # Invariant: An initialized companion cannot be quietly reset via normal update
    if existing_profile.get("is_onboarded") is True and updated_profile.get("is_onboarded") is False:
        raise ImmutableIdentityMutationError(
            "Attempted to revert 'is_onboarded' from True to False on an initialized identity anchor. "
            "Failing closed to prevent identity invalidation."
        )


# ---------------------------------------------------------------------------
# Phylogenetic Update Simulation & Execution
# ---------------------------------------------------------------------------

def apply_phylogenetic_upgrade(
    profile_data: Dict[str, Any],
    new_engine_version: str,
    last_upgraded_at: Optional[str] = None,
) -> Dict[str, Any]:
    """
    Apply a software engine / model weight update to profile phylogenetic lineage.

    Guarantees:
    - Evolving fields (engine_version, last_upgraded_at) are updated.
    - Ontogenetic IdentityAnchor fields remain bit-exact and untouched.
    - Verified via guard_immutable_fields.
    """
    if not isinstance(profile_data, dict):
        raise ValueError("profile_data must be a dictionary.")

    updated = copy.deepcopy(profile_data)
    timestamp = last_upgraded_at or datetime.now(timezone.utc).isoformat()

    lineage = updated.setdefault("phylogenetic_lineage", {})
    if not isinstance(lineage, dict):
        lineage = {}
        updated["phylogenetic_lineage"] = lineage

    lineage["engine_version"] = str(new_engine_version)
    lineage["last_upgraded_at"] = str(timestamp)
    lineage.setdefault("compatible_schema_major", 2)

    # Guard immutability: Ensure zero mutation of ontogenetic anchor
    guard_immutable_fields(profile_data, updated)

    return updated


# ---------------------------------------------------------------------------
# Startup Identity Verification
# ---------------------------------------------------------------------------

def verify_identity_on_startup(
    profile_path: Optional[Union[Path, str]] = None,
    allow_frozen: bool = False,
    allow_decommissioned: bool = False,
) -> IdentityProfileState:
    """
    Verify identity anchor integrity upon system startup.

    Execution contract:
    - Called in live mode after exclusive instance authority (WP-01) is acquired.
    - If profile does not exist: returns uninitialized state without writing files.
    - If profile exists and is un-onboarded ({"is_onboarded": false}): returns
      Genesis-locked state. Generates ZERO identity and performs ZERO disk writes.
    - If profile exists and is onboarded: validates identity anchor fields.
      If anchor is valid: returns initialized state.
      If anchor is missing or corrupted: raises CorruptedIdentityAnchorError / InvalidIdentityAnchorError.
      If instance is decommissioned: raises DecommissionedInstanceError.
      If instance is frozen: raises FrozenMigrationStateError.
    """
    target = Path(profile_path) if profile_path else DEFAULT_PROFILE_PATH

    if not target.exists():
        logger.info("Profile file not found at %s. Runtime remains in Genesis-ready state.", target)
        return IdentityProfileState(
            is_onboarded=False,
            is_genesis_locked=True,
            anchor=None,
            lineage=None,
            schema_version=None,
            raw_profile=None,
            migration_status=None,
        )

    try:
        with open(target, "r", encoding="utf-8") as f:
            raw_data = json.load(f)
    except Exception as exc:
        raise CorruptedIdentityAnchorError(
            f"Failed to read or parse profile at '{target}': {exc}"
        ) from exc

    if not isinstance(raw_data, dict):
        raise CorruptedIdentityAnchorError(
            f"Profile file '{target}' does not contain a JSON dictionary."
        )

    return validate_profile_identity(
        raw_data,
        allow_frozen=allow_frozen,
        allow_decommissioned=allow_decommissioned,
    )


# ---------------------------------------------------------------------------
# Genesis Root Hash Ceremony Construction (Deferred)
# ---------------------------------------------------------------------------

def compute_genesis_root_hash(*args: Any, **kwargs: Any) -> str:
    """
    Placeholder for Genesis Creation Ceremony root hash computation.

    DEFERRED: Under ADR-034 and Identity Authority Spec v0.1, the exact
    set of foundational state files, canonical serialization, and file order
    for the Genesis root hash are deferred to the controlled Genesis Onboarding Ceremony.

    Status: DEFERRED — GENESIS CREATION CEREMONY REQUIRED.
    """
    raise NotImplementedError(
        f"Genesis root hash generation is a Genesis-bound ceremony operation. "
        f"Status: {GENESIS_ROOT_HASH_STATUS}. Genesis remains LOCKED under INV-8."
    )
