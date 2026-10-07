"""
Isolated Unit Tests for WP-02: Immutable Identity Anchor & Lineage Separation.

Governing ADR: ADR-034 (ARCH-034)
Reference: docs/others/IDENTITY_AUTHORITY_SPECIFICATION/IMPLEMENTATION_PLAN.md

Tests cover:
- T01: Pre-Genesis profile ({"is_onboarded": false} accepted as Genesis-locked, no identity generated, zero mutation)
- T02: Valid initialized anchor (parses, validates, immutable fields preserved, roundtrip serialization)
- T03: Missing immutable field (each of instance_uuid, born_at, genesis_commit, genesis_root_hash fails closed)
- T04: Invalid UUID representation (malformed, bad length, non-hex fails closed)
- T05: Invalid timestamp representation (malformed ISO, invalid year fails closed)
- T06: Invalid genesis commit (wrong length, non-hex fails closed)
- T07: Invalid genesis root hash (wrong length, non-hex fails closed)
- T08: Immutable mutation attempt (modifying any of the 4 immutable fields or deleting anchor fails closed)
- T09: Phylogenetic update (engine_version, last_upgraded_at, schema metadata update allowed; anchor unchanged)
- T10: Engine/model upgrade simulation (simulated upgrade preserves identity_anchor bit-for-bit)
- Schema version compatibility check (unsupported major version fails closed)
- Inconsistent state checks (is_onboarded=True without anchor; is_onboarded=False with anchor)
- Genesis root hash ceremony deferral verification
"""

from __future__ import annotations

from dataclasses import FrozenInstanceError
import json
from pathlib import Path
import pytest

from src.core.identity.identity_anchor import (
    CANONICAL_SCHEMA_VERSION,
    GENESIS_ROOT_HASH_STATUS,
    IMMUTABLE_IDENTITY_FIELDS,
    IdentityAnchor,
    IdentityProfileState,
    ImmutableIdentityMutationError,
    InvalidIdentityAnchorError,
    PhylogeneticLineage,
    apply_phylogenetic_upgrade,
    compute_genesis_root_hash,
    guard_immutable_fields,
    validate_born_at,
    validate_genesis_commit,
    validate_genesis_root_hash,
    validate_identity_anchor,
    validate_instance_uuid,
    validate_profile_identity,
    verify_identity_on_startup,
)

# Canonical sample fixtures for tests
VALID_UUID = "3fa85f64-5717-4562-b3fc-2c963f66afa6"
VALID_URN_UUID = "urn:uuid:3fa85f64-5717-4562-b3fc-2c963f66afa6"
VALID_BORN_AT = "2026-10-07T07:36:33.123456Z"
VALID_COMMIT = "ce106a245890abcdef1234567890abcdef123456"
VALID_ROOT_HASH = "e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855"


def create_valid_anchor_dict() -> dict:
    return {
        "instance_uuid": VALID_UUID,
        "born_at": VALID_BORN_AT,
        "genesis_commit": VALID_COMMIT,
        "genesis_root_hash": VALID_ROOT_HASH,
    }


def create_valid_profile_dict() -> dict:
    return {
        "schema_version": CANONICAL_SCHEMA_VERSION,
        "is_onboarded": True,
        "identity_anchor": create_valid_anchor_dict(),
        "phylogenetic_lineage": {
            "engine_version": "0.24.2",
            "last_upgraded_at": "2026-10-07T07:36:33.123456Z",
            "compatible_schema_major": 2,
        },
        "user_name": "Friend",
        "companion_name": "Lucia",
    }


class TestIdentityAnchorUnit:
    """Test suite for Identity Anchor schema, validation, immutability, and lineage separation."""

    def test_t01_pre_genesis_profile(self, tmp_path: Path):
        """T01: Pre-Genesis profile is accepted as Genesis-locked; no identity generated; zero file mutation."""
        pre_genesis_data = {"is_onboarded": False}
        state = validate_profile_identity(pre_genesis_data)

        assert state.is_onboarded is False
        assert state.is_genesis_locked is True
        assert state.anchor is None

        # Verify startup reader on a Pre-Genesis file
        profile_file = tmp_path / "profile.json"
        profile_file.write_text(json.dumps(pre_genesis_data), encoding="utf-8")
        file_stat_before = profile_file.stat()

        startup_state = verify_identity_on_startup(profile_file)
        assert startup_state.is_onboarded is False
        assert startup_state.is_genesis_locked is True
        assert startup_state.anchor is None

        # Ensure zero mutation occurred to the file
        file_stat_after = profile_file.stat()
        assert file_stat_before.st_mtime == file_stat_after.st_mtime
        assert json.loads(profile_file.read_text(encoding="utf-8")) == {"is_onboarded": False}

    def test_t02_valid_initialized_anchor(self):
        """T02: Valid initialized anchor parses, validates, and preserves all immutable fields."""
        raw = create_valid_anchor_dict()
        anchor = validate_identity_anchor(raw)

        assert anchor.instance_uuid == VALID_UUID
        assert anchor.born_at == VALID_BORN_AT
        assert anchor.genesis_commit == VALID_COMMIT
        assert anchor.genesis_root_hash == VALID_ROOT_HASH

        # Roundtrip to dict
        roundtrip = anchor.to_dict()
        assert roundtrip == raw

        # In-memory immutability (frozen dataclass)
        with pytest.raises(FrozenInstanceError):
            anchor.instance_uuid = "cannot-mutate-in-memory"  # type: ignore

    def test_t02_valid_initialized_anchor_with_urn(self):
        """T02b: URN UUID notation is accepted and preserved."""
        raw = create_valid_anchor_dict()
        raw["instance_uuid"] = VALID_URN_UUID
        anchor = validate_identity_anchor(raw)
        assert anchor.instance_uuid == VALID_URN_UUID

    @pytest.mark.parametrize("missing_field", IMMUTABLE_IDENTITY_FIELDS)
    def test_t03_missing_immutable_field(self, missing_field: str):
        """T03: Removing any required immutable identity field fails closed."""
        raw = create_valid_anchor_dict()
        del raw[missing_field]

        with pytest.raises(InvalidIdentityAnchorError) as exc_info:
            validate_identity_anchor(raw)
        assert missing_field in str(exc_info.value)

    @pytest.mark.parametrize("empty_field", IMMUTABLE_IDENTITY_FIELDS)
    def test_t03_empty_or_none_immutable_field(self, empty_field: str):
        """T03b: None or empty string for an immutable field fails closed."""
        raw_none = create_valid_anchor_dict()
        raw_none[empty_field] = None
        with pytest.raises(InvalidIdentityAnchorError):
            validate_identity_anchor(raw_none)

        raw_empty = create_valid_anchor_dict()
        raw_empty[empty_field] = ""
        with pytest.raises(InvalidIdentityAnchorError):
            validate_identity_anchor(raw_empty)

    @pytest.mark.parametrize("bad_uuid", [
        "not-a-uuid",
        "12345",
        "3fa85f64-5717-4562-b3fc",  # truncated
        "3fa85f64-5717-4562-b3fc-2c963f66afa6-extra",  # too long
        "gfa85f64-5717-4562-b3fc-2c963f66afa6",  # illegal character 'g'
        12345,  # wrong type
    ])
    def test_t04_invalid_uuid(self, bad_uuid: object):
        """T04: Corrupt instance_uuid fails closed."""
        raw = create_valid_anchor_dict()
        raw["instance_uuid"] = bad_uuid
        with pytest.raises(InvalidIdentityAnchorError):
            validate_identity_anchor(raw)

    @pytest.mark.parametrize("bad_ts", [
        "not-a-timestamp",
        "2026-99-99T00:00:00Z",
        "2019-12-31T23:59:59Z",  # before project epoch 2020
        "invalid-iso-format",
        1700000000,  # unix int instead of ISO string
    ])
    def test_t05_invalid_timestamp(self, bad_ts: object):
        """T05: Corrupt born_at timestamp fails closed."""
        raw = create_valid_anchor_dict()
        raw["born_at"] = bad_ts
        with pytest.raises(InvalidIdentityAnchorError):
            validate_identity_anchor(raw)

    @pytest.mark.parametrize("bad_commit", [
        "not-a-commit",
        "abc123",  # too short
        "ce106a245890abcdef1234567890abcdef12345g",  # non-hex char 'g'
        "ce106a245890abcdef1234567890abcdef12345678",  # 42 chars (invalid length)
        123456,
    ])
    def test_t06_invalid_genesis_commit(self, bad_commit: object):
        """T06: Corrupt genesis_commit fails closed."""
        raw = create_valid_anchor_dict()
        raw["genesis_commit"] = bad_commit
        with pytest.raises(InvalidIdentityAnchorError):
            validate_identity_anchor(raw)

    @pytest.mark.parametrize("bad_hash", [
        "not-a-root-hash",
        "e3b0c442",  # truncated
        "e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b85g",  # illegal char 'g'
        "e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855aa",  # 66 chars
        12345,
    ])
    def test_t07_invalid_root_hash(self, bad_hash: object):
        """T07: Corrupt genesis_root_hash fails closed."""
        raw = create_valid_anchor_dict()
        raw["genesis_root_hash"] = bad_hash
        with pytest.raises(InvalidIdentityAnchorError):
            validate_identity_anchor(raw)

    @pytest.mark.parametrize("field_to_mutate", IMMUTABLE_IDENTITY_FIELDS)
    def test_t08_immutable_mutation_attempt(self, field_to_mutate: str):
        """T08: Attempting to mutate any immutable field is rejected by the guard."""
        existing_profile = create_valid_profile_dict()
        updated_profile = create_valid_profile_dict()

        # Mutate the target immutable field
        if field_to_mutate == "instance_uuid":
            updated_profile["identity_anchor"][field_to_mutate] = "4fa85f64-5717-4562-b3fc-2c963f66afa7"
        elif field_to_mutate == "born_at":
            updated_profile["identity_anchor"][field_to_mutate] = "2026-10-08T00:00:00Z"
        elif field_to_mutate == "genesis_commit":
            updated_profile["identity_anchor"][field_to_mutate] = "0000000000000000000000000000000000000000"
        elif field_to_mutate == "genesis_root_hash":
            updated_profile["identity_anchor"][field_to_mutate] = "0000000000000000000000000000000000000000000000000000000000000000"

        with pytest.raises(ImmutableIdentityMutationError) as exc_info:
            guard_immutable_fields(existing_profile, updated_profile)
        assert field_to_mutate in str(exc_info.value)

    def test_t08_deletion_of_anchor_rejected(self):
        """T08b: Deletion or removal of initialized identity anchor is rejected."""
        existing_profile = create_valid_profile_dict()
        updated_profile = create_valid_profile_dict()
        del updated_profile["identity_anchor"]

        with pytest.raises(ImmutableIdentityMutationError) as exc_info:
            guard_immutable_fields(existing_profile, updated_profile)
        assert "deletion" in str(exc_info.value).lower()

    def test_t08_reverting_onboarded_flag_rejected(self):
        """T08c: Reverting is_onboarded from True to False on an initialized anchor is rejected."""
        existing_profile = create_valid_profile_dict()
        updated_profile = create_valid_profile_dict()
        updated_profile["is_onboarded"] = False

        with pytest.raises(ImmutableIdentityMutationError) as exc_info:
            guard_immutable_fields(existing_profile, updated_profile)
        assert "is_onboarded" in str(exc_info.value)

    def test_t09_phylogenetic_update_allowed(self):
        """T09: Changing phylogenetic metadata is permitted while preserving identity fields."""
        existing_profile = create_valid_profile_dict()
        updated_profile = create_valid_profile_dict()

        # Update phylogenetic lineage and user preferences
        updated_profile["phylogenetic_lineage"]["engine_version"] = "0.25.0"
        updated_profile["phylogenetic_lineage"]["last_upgraded_at"] = "2026-11-01T12:00:00Z"
        updated_profile["user_name"] = "Best Friend"
        updated_profile["companion_name"] = "Lucia-Custom"

        # Guard must not raise any exception
        guard_immutable_fields(existing_profile, updated_profile)

        # Validate that identity anchor remains bit-identical
        assert existing_profile["identity_anchor"] == updated_profile["identity_anchor"]

    def test_t10_engine_model_upgrade_simulation(self):
        """T10: Simulating multiple engine/model upgrades preserves identity anchor bit-for-bit."""
        profile = create_valid_profile_dict()
        original_anchor = dict(profile["identity_anchor"])

        # First upgrade: 0.24.2 -> 0.25.0
        upgraded_v1 = apply_phylogenetic_upgrade(
            profile,
            new_engine_version="0.25.0",
            last_upgraded_at="2026-10-15T10:00:00Z",
        )
        assert upgraded_v1["phylogenetic_lineage"]["engine_version"] == "0.25.0"
        assert upgraded_v1["identity_anchor"] == original_anchor
        assert upgraded_v1["identity_anchor"]["instance_uuid"] == VALID_UUID

        # Second upgrade: 0.25.0 -> 0.26.0 (simulating SLM weight swap)
        upgraded_v2 = apply_phylogenetic_upgrade(
            upgraded_v1,
            new_engine_version="0.26.0",
            last_upgraded_at="2026-11-01T15:30:00Z",
        )
        assert upgraded_v2["phylogenetic_lineage"]["engine_version"] == "0.26.0"
        assert upgraded_v2["identity_anchor"] == original_anchor
        assert upgraded_v2["identity_anchor"]["instance_uuid"] == VALID_UUID

    def test_inconsistent_profile_states(self):
        """Verify fail-closed behavior on contradictory profile states."""
        # Case A: is_onboarded=True but no identity_anchor
        with pytest.raises(InvalidIdentityAnchorError) as exc_a:
            validate_profile_identity({"is_onboarded": True})
        assert "missing" in str(exc_a.value).lower()

        # Case B: is_onboarded=False but identity_anchor is present
        with pytest.raises(InvalidIdentityAnchorError) as exc_b:
            validate_profile_identity({
                "is_onboarded": False,
                "identity_anchor": create_valid_anchor_dict(),
            })
        assert "inconsistent" in str(exc_b.value).lower()

    def test_incompatible_schema_version(self):
        """Verify fail-closed behavior on unsupported major schema versions."""
        profile = create_valid_profile_dict()
        profile["schema_version"] = "99.0"  # Major version 99 is unsupported

        with pytest.raises(InvalidIdentityAnchorError) as exc_info:
            validate_profile_identity(profile)
        assert "incompatible" in str(exc_info.value).lower()

    def test_genesis_root_hash_ceremony_deferred(self):
        """Verify that genesis root hash generation ceremony is explicitly deferred and raises NotImplementedError."""
        assert GENESIS_ROOT_HASH_STATUS == "DEFERRED — GENESIS CREATION CEREMONY REQUIRED"
        with pytest.raises(NotImplementedError) as exc_info:
            compute_genesis_root_hash()
        assert "DEFERRED" in str(exc_info.value)
