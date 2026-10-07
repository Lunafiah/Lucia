"""
Unit test suite for WP-05 — Migration Boundary under ADR-034.

Governing ADR: ADR-034 (Identity Authority, Instance Exclusivity & Anti-Branching Boundary).
Reference Specification: docs/others/IDENTITY_AUTHORITY_SPECIFICATION/IDENTITY_AUTHORITY_SPEC_V01.md
Reference Plan: docs/others/IDENTITY_AUTHORITY_SPECIFICATION/IMPLEMENTATION_PLAN.md

Tests:
1. Valid migration: Freeze -> Export -> Verify -> Decommission -> Activate.
2. Corrupted transfer archive fails destination verification.
3. Manifest/hash mismatch (tampered payload file in archive) fails closed.
4. Missing migration receipt on decommission attempt fails closed.
5. Invalid or incomplete source freeze / pre-Genesis profile migration fails closed.
6. Destination verification failure (missing payload file or invalid schema) fails closed.
7. Attempt to activate destination before source decommission fails closed.
8. Attempt to restart a successfully migrated source fails closed with DecommissionedInstanceError.
9. Attempt to activate two destinations from the same migration fails closed with DestinationMismatchError.
10. Migration interrupted midway (abort source freeze restores to ABORTED/IDLE, destination remains unactivated).
11. Migration followed by normal WP-01 -> WP-04 startup validation passes cleanly on destination.
12. Identity Anchor remains bit-for-bit unchanged throughout migration.
13. Genesis invariant remains untouched (data/profile.json is {"is_onboarded": false}).
14. Phylogenetic software evolvability during migration preserves identity anchor.
15. Aborting an already decommissioned instance fails closed.
"""

from __future__ import annotations

import copy
import hashlib
import json
import os
from pathlib import Path
import shutil
import tarfile
import time
from typing import Any, Dict, Tuple

import numpy as np
import pytest

from src.core.emotion.persistence import (
    CURRENT_SCHEMA_VERSION,
    EXPECTED_FAST_DIM,
    EXPECTED_SLOW_DIM,
    DynamicalStateSnapshot,
    EpochManifest,
    save_dynamical_checkpoint,
    save_epoch_manifest,
    verify_and_reconcile_stores,
)
from src.core.identity.identity_anchor import (
    CANONICAL_SCHEMA_VERSION,
    DEFAULT_PROFILE_PATH,
    IMMUTABLE_IDENTITY_FIELDS,
    DecommissionedInstanceError,
    FrozenMigrationStateError,
    apply_phylogenetic_upgrade,
    guard_immutable_fields,
    validate_identity_anchor,
    verify_identity_on_startup,
)
from src.core.identity.instance_lock import InstanceLock
from src.core.identity.migration_boundary import (
    MIGRATION_MANIFEST_FILENAME,
    CorruptedArchiveError,
    DecommissionProof,
    DestinationMismatchError,
    InvalidDecommissionProofError,
    InvalidReceiptError,
    ManifestHashMismatchError,
    MigrationActivationResult,
    MigrationConflictError,
    MigrationError,
    MigrationManifest,
    MigrationReceipt,
    MigrationStatus,
    MigrationVerificationResult,
    MissingDecommissionProofError,
    MissingReceiptError,
    PreGenesisMigrationForbiddenError,
    abort_source_freeze,
    activate_destination_instance,
    canonical_json_bytes,
    compute_file_sha256,
    compute_manifest_digest,
    compute_proof_token,
    compute_receipt_token,
    decommission_source_instance,
    export_migration_archive,
    freeze_for_migration,
    verify_migration_archive,
)
from src.core.identity.provenance_verifier import (
    HardwareDigestComponents,
    collect_hardware_components,
    compute_component_digests,
    compute_hardware_digest,
    normalize_workspace_path,
    verify_provenance_and_environment,
)
from src.core.relationship.persistence import RelationshipState, save_relationship


SAMPLE_UUID = "550e8400-e29b-41d4-a716-446655440000"
SAMPLE_BORN_AT = "2026-10-07T00:00:00+00:00"
SAMPLE_COMMIT = "abcdef1234567890abcdef1234567890abcdef12"
SAMPLE_ROOT_HASH = "e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855"


def setup_test_workspace(
    ws_path: Path,
    is_onboarded: bool = True,
    epoch_id: int = 5,
    migration_epoch: int = 0,
) -> Dict[str, Any]:
    """Helper to set up a mock Lucia workspace with valid data/ directory."""
    ws = Path(ws_path).resolve()
    data_dir = ws / "data"
    data_dir.mkdir(parents=True, exist_ok=True)

    comps = collect_hardware_components(ws)
    hw_digest = compute_hardware_digest(comps)

    if is_onboarded:
        profile_data = {
            "schema_version": CANONICAL_SCHEMA_VERSION,
            "is_onboarded": True,
            "identity_anchor": {
                "instance_uuid": SAMPLE_UUID,
                "born_at": SAMPLE_BORN_AT,
                "genesis_commit": SAMPLE_COMMIT,
                "genesis_root_hash": SAMPLE_ROOT_HASH,
            },
            "phylogenetic_lineage": {
                "engine_version": "0.24.2",
                "last_upgraded_at": SAMPLE_BORN_AT,
                "compatible_schema_major": 2,
            },
            "authority_binding": {
                "hardware_binding_mode": "SOFT_WARNING",
                "bound_machine_guid_digest": hw_digest,
                "activation_host_platform": comps.platform_str,
                "last_known_canonical_path": normalize_workspace_path(ws),
                "hardware_migration_epoch": migration_epoch,
                "last_verified_at": SAMPLE_BORN_AT,
                "component_digests": compute_component_digests(comps),
            },
            "user_name": "CompanionOwner",
            "companion_name": "Lucia",
        }
    else:
        profile_data = {"is_onboarded": False}

    prof_file = data_dir / "profile.json"
    with open(prof_file, "w", encoding="utf-8") as f:
        json.dump(profile_data, f, indent=2)

    # Relationship store
    rel_file = data_dir / "relationship.json"
    rel_state = RelationshipState(familiarity=0.6, trust=0.7, closeness=0.5, reciprocity=0.6)
    save_relationship(rel_state, filepath=rel_file, epoch_id=epoch_id)

    # Dynamical state store
    dyn_file = data_dir / "dynamical_state.json"
    dyn_snap = DynamicalStateSnapshot(
        h_fast=np.zeros(EXPECTED_FAST_DIM),
        s_slow=np.ones(EXPECTED_SLOW_DIM) * 0.1,
        created_at=time.time(),
        epoch_id=epoch_id,
    )
    save_dynamical_checkpoint(dyn_snap, filepath=dyn_file)

    # Epoch manifest
    man_file = data_dir / "epoch_manifest.json"
    manifest = EpochManifest(
        epoch_id=epoch_id,
        t_checkpoint=time.time(),
        stores={"relationship": epoch_id, "dynamical_state": epoch_id},
    )
    save_epoch_manifest(manifest, filepath=man_file)

    # Chat history
    chat_file = data_dir / "chat_history.json"
    with open(chat_file, "w", encoding="utf-8") as f:
        json.dump(
            {
                "version": 1,
                "turns": [
                    {"role": "user", "content": "Hello Lucia"},
                    {"role": "assistant", "content": "Hello. I am here."},
                ],
            },
            f,
            indent=2,
        )

    return profile_data


class TestMigrationBoundaryUnit:
    """Unit tests verifying WP-05 Migration Boundary mechanics."""

    def test_01_valid_end_to_end_migration(self, tmp_path: Path):
        """Case 1: Full canonical sequence (Freeze -> Export -> Verify -> Decommission -> Activate)."""
        src_ws = tmp_path / "source"
        dest_ws = tmp_path / "dest"
        src_ws.mkdir()
        dest_ws.mkdir()

        setup_test_workspace(src_ws, is_onboarded=True, epoch_id=5, migration_epoch=0)

        # 1. Freeze
        manifest, frozen_profile = freeze_for_migration(src_ws)
        assert manifest.migration_id is not None
        assert frozen_profile["migration_state"]["status"] == "FROZEN"

        # 2. Export
        archive_path = tmp_path / "migration.tar.gz"
        export_migration_archive(manifest, src_ws / "data", archive_path)
        assert archive_path.exists()

        # 3. Verify on target
        dest_comps = collect_hardware_components(dest_ws)
        verif_res, receipt = verify_migration_archive(
            archive_path=archive_path,
            destination_workspace_path=dest_ws,
            destination_hardware_components=dest_comps,
        )
        assert verif_res.is_valid is True
        assert receipt is not None
        assert receipt.status == "VERIFIED"
        assert receipt.migration_id == manifest.migration_id

        # 4. Decommission source
        proof = decommission_source_instance(
            workspace_path=src_ws,
            receipt=receipt,
        )
        assert proof.migration_id == manifest.migration_id
        assert proof.receipt_id == receipt.receipt_id

        # Check source profile is DECOMMISSIONED
        with open(src_ws / "data" / "profile.json", "r", encoding="utf-8") as f:
            decom_profile = json.load(f)
        assert decom_profile["migration_state"]["status"] == "DECOMMISSIONED"

        # 5. Activate destination
        act_res = activate_destination_instance(
            destination_workspace_path=dest_ws,
            archive_path=archive_path,
            receipt=receipt,
            decommission_proof=proof,
            destination_hardware_components=dest_comps,
        )
        assert act_res.is_activated is True
        assert act_res.status == "ACTIVE"
        assert act_res.new_hardware_migration_epoch == 1

        # Check destination profile is ACTIVE and has incremented epoch
        with open(dest_ws / "data" / "profile.json", "r", encoding="utf-8") as f:
            dest_profile = json.load(f)
        assert dest_profile["migration_state"]["status"] == "ACTIVE"
        assert dest_profile["authority_binding"]["hardware_migration_epoch"] == 1

    def test_02_corrupted_transfer_archive(self, tmp_path: Path):
        """Case 2: Corrupted or truncated archive fails verification."""
        dest_ws = tmp_path / "dest"
        dest_ws.mkdir()

        bad_archive = tmp_path / "corrupted.tar.gz"
        bad_archive.write_bytes(b"NOT_A_VALID_GZIP_ARCHIVE_DATA_TRUNCATED")

        verif_res, receipt = verify_migration_archive(
            archive_path=bad_archive,
            destination_workspace_path=dest_ws,
        )
        assert verif_res.is_valid is False
        assert verif_res.status == "CORRUPTED_ARCHIVE"
        assert receipt is None

    def test_03_manifest_hash_mismatch(self, tmp_path: Path):
        """Case 3: Tampered payload file in archive fails destination verification."""
        src_ws = tmp_path / "source"
        dest_ws = tmp_path / "dest"
        src_ws.mkdir()
        dest_ws.mkdir()

        setup_test_workspace(src_ws, is_onboarded=True)
        manifest, _ = freeze_for_migration(src_ws)

        # Mutate relationship.json before packaging
        with open(src_ws / "data" / "relationship.json", "a", encoding="utf-8") as f:
            f.write("\n")

        archive_path = tmp_path / "tampered.tar.gz"
        export_migration_archive(manifest, src_ws / "data", archive_path)

        verif_res, receipt = verify_migration_archive(
            archive_path=archive_path,
            destination_workspace_path=dest_ws,
        )
        assert verif_res.is_valid is False
        assert verif_res.status == "FILE_HASH_MISMATCH"
        assert receipt is None

    def test_04_missing_migration_receipt(self, tmp_path: Path):
        """Case 4: Attempt to decommission source without receipt fails closed."""
        src_ws = tmp_path / "source"
        src_ws.mkdir()
        setup_test_workspace(src_ws, is_onboarded=True)
        freeze_for_migration(src_ws)

        with pytest.raises(MissingReceiptError):
            decommission_source_instance(
                workspace_path=src_ws,
                receipt=None,  # type: ignore
            )

    def test_05_invalid_or_incomplete_source_freeze(self, tmp_path: Path):
        """Case 5: Attempting to freeze pre-Genesis profile fails closed."""
        src_ws = tmp_path / "source"
        src_ws.mkdir()
        setup_test_workspace(src_ws, is_onboarded=False)  # pre-Genesis

        with pytest.raises(PreGenesisMigrationForbiddenError):
            freeze_for_migration(src_ws)

    def test_06_destination_verification_failure_missing_file(self, tmp_path: Path):
        """Case 6: Archive missing required persistent store fails verification."""
        src_ws = tmp_path / "source"
        dest_ws = tmp_path / "dest"
        src_ws.mkdir()
        dest_ws.mkdir()

        setup_test_workspace(src_ws, is_onboarded=True)
        manifest, _ = freeze_for_migration(src_ws)

        # Remove dynamical_state.json from data/ before exporting
        (src_ws / "data" / "dynamical_state.json").unlink()

        archive_path = tmp_path / "missing_file.tar.gz"
        with pytest.raises(MigrationError):
            export_migration_archive(manifest, src_ws / "data", archive_path)

    def test_07_activate_before_source_decommission(self, tmp_path: Path):
        """Case 7: Attempting destination activation without decommission proof fails closed."""
        dest_ws = tmp_path / "dest"
        dest_ws.mkdir()

        receipt = MigrationReceipt(
            receipt_id="r1",
            migration_id="m1",
            destination_hardware_digest="h1",
            destination_canonical_path=str(dest_ws),
            manifest_digest="man1",
            verified_at=SAMPLE_BORN_AT,
        )

        with pytest.raises(MissingDecommissionProofError):
            activate_destination_instance(
                destination_workspace_path=dest_ws,
                archive_path=tmp_path / "arch.tar.gz",
                receipt=receipt,
                decommission_proof=None,  # type: ignore
            )

    def test_08_restart_decommissioned_source_fails(self, tmp_path: Path):
        """Case 8: Attempt to boot or verify a decommissioned source fails closed."""
        src_ws = tmp_path / "source"
        dest_ws = tmp_path / "dest"
        src_ws.mkdir()
        dest_ws.mkdir()

        setup_test_workspace(src_ws, is_onboarded=True)
        manifest, _ = freeze_for_migration(src_ws)
        archive_path = tmp_path / "mig.tar.gz"
        export_migration_archive(manifest, src_ws / "data", archive_path)

        _, receipt = verify_migration_archive(archive_path, dest_ws)
        assert receipt is not None
        decommission_source_instance(src_ws, receipt)

        # Attempt to run verify_identity_on_startup on the decommissioned source
        with pytest.raises(DecommissionedInstanceError) as exc_info:
            verify_identity_on_startup(src_ws / "data" / "profile.json")
        assert "decommissioned" in str(exc_info.value).lower()

    def test_09_activate_two_destinations_from_same_migration(self, tmp_path: Path):
        """Case 9: Attempting to activate a second destination from same proof fails closed."""
        src_ws = tmp_path / "source"
        dest_1 = tmp_path / "dest_1"
        dest_2 = tmp_path / "dest_2"
        src_ws.mkdir()
        dest_1.mkdir()
        dest_2.mkdir()

        setup_test_workspace(src_ws, is_onboarded=True)
        manifest, _ = freeze_for_migration(src_ws)
        archive_path = tmp_path / "mig.tar.gz"
        export_migration_archive(manifest, src_ws / "data", archive_path)

        # Receipt and decommission issued for dest_1
        comps_1 = collect_hardware_components(dest_1)
        _, receipt_1 = verify_migration_archive(
            archive_path=archive_path,
            destination_workspace_path=dest_1,
            destination_hardware_components=comps_1,
        )
        assert receipt_1 is not None
        proof = decommission_source_instance(src_ws, receipt_1)

        # dest_1 activates successfully
        res_1 = activate_destination_instance(
            destination_workspace_path=dest_1,
            archive_path=archive_path,
            receipt=receipt_1,
            decommission_proof=proof,
            destination_hardware_components=comps_1,
        )
        assert res_1.is_activated is True

        # Now attempt to activate dest_2 with the same receipt & proof
        # DestinationMismatchError because dest_2 has a different workspace path and/or hardware digest!
        with pytest.raises(DestinationMismatchError) as exc_info:
            activate_destination_instance(
                destination_workspace_path=dest_2,
                archive_path=archive_path,
                receipt=receipt_1,
                decommission_proof=proof,
            )
        assert "divergence" in str(exc_info.value).lower()

    def test_10_migration_interrupted_midway(self, tmp_path: Path):
        """Case 10: Interrupted freeze can be aborted cleanly before decommission."""
        src_ws = tmp_path / "source"
        src_ws.mkdir()
        setup_test_workspace(src_ws, is_onboarded=True)

        manifest, _ = freeze_for_migration(src_ws)

        # Verify normal startup is blocked while FROZEN
        with pytest.raises(FrozenMigrationStateError):
            verify_identity_on_startup(src_ws / "data" / "profile.json")

        # Source decides to abort the migration
        aborted_prof = abort_source_freeze(src_ws)
        assert aborted_prof["migration_state"]["status"] == "ABORTED"

        # Now normal startup succeeds
        id_state = verify_identity_on_startup(src_ws / "data" / "profile.json")
        assert id_state.is_onboarded is True

    def test_11_destination_startup_validation(self, tmp_path: Path):
        """Case 11: Activated destination passes complete WP-01 -> WP-04 validation chain."""
        src_ws = tmp_path / "source"
        dest_ws = tmp_path / "dest"
        src_ws.mkdir()
        dest_ws.mkdir()

        setup_test_workspace(src_ws, is_onboarded=True, epoch_id=8)
        manifest, _ = freeze_for_migration(src_ws)
        archive_path = tmp_path / "mig.tar.gz"
        export_migration_archive(manifest, src_ws / "data", archive_path)

        dest_comps = collect_hardware_components(dest_ws)
        _, receipt = verify_migration_archive(archive_path, dest_ws, destination_hardware_components=dest_comps)
        assert receipt is not None
        proof = decommission_source_instance(src_ws, receipt)

        activate_destination_instance(
            destination_workspace_path=dest_ws,
            archive_path=archive_path,
            receipt=receipt,
            decommission_proof=proof,
            destination_hardware_components=dest_comps,
        )

        # Step 1: Instance Lock
        lock = InstanceLock(lock_path=dest_ws / "data" / ".instance.lock")
        lock.acquire()
        assert lock.is_locked is True

        # Step 2: Identity Anchor Verification
        dest_prof = dest_ws / "data" / "profile.json"
        id_state = verify_identity_on_startup(dest_prof)
        assert id_state.is_onboarded is True
        assert id_state.anchor.instance_uuid == SAMPLE_UUID

        # Step 3: Provenance & Environment Verification
        prov_res = verify_provenance_and_environment(
            workspace_path=dest_ws,
            profile_path=dest_prof,
            allow_reconfirmation=False,
        )
        assert prov_res.is_valid is True

        # Step 4: Epoch Manifest & Stores Reconciliation
        reconcile_rep = verify_and_reconcile_stores(
            relationship_path=dest_ws / "data" / "relationship.json",
            dynamical_path=dest_ws / "data" / "dynamical_state.json",
            manifest_path=dest_ws / "data" / "epoch_manifest.json",
        )
        assert reconcile_rep.is_consistent is True
        assert len(reconcile_rep.inconsistencies_detected) == 0

        lock.release()

    def test_12_identity_anchor_bit_for_bit_immutability(self, tmp_path: Path):
        """Case 12: Identity Anchor fields remain 100% bit-exact throughout migration."""
        src_ws = tmp_path / "source"
        dest_ws = tmp_path / "dest"
        src_ws.mkdir()
        dest_ws.mkdir()

        src_prof = setup_test_workspace(src_ws, is_onboarded=True)
        manifest, _ = freeze_for_migration(src_ws)
        archive_path = tmp_path / "mig.tar.gz"
        export_migration_archive(manifest, src_ws / "data", archive_path)

        _, receipt = verify_migration_archive(archive_path, dest_ws)
        assert receipt is not None
        proof = decommission_source_instance(src_ws, receipt)

        activate_destination_instance(
            destination_workspace_path=dest_ws,
            archive_path=archive_path,
            receipt=receipt,
            decommission_proof=proof,
        )

        with open(dest_ws / "data" / "profile.json", "r", encoding="utf-8") as f:
            dest_profile = json.load(f)

        src_anchor = src_prof["identity_anchor"]
        dest_anchor = dest_profile["identity_anchor"]

        for field_name in IMMUTABLE_IDENTITY_FIELDS:
            assert dest_anchor[field_name] == src_anchor[field_name], (
                f"Identity anchor divergence in field '{field_name}'! "
                f"Source: {src_anchor[field_name]}, Destination: {dest_anchor[field_name]}"
            )

    def test_13_genesis_invariant_remains_untouched(self):
        """Case 13: Live repository data/profile.json is strictly {'is_onboarded': false}."""
        repo_root = Path(__file__).resolve().parent.parent.parent
        live_profile = repo_root / "data" / "profile.json"

        assert live_profile.exists(), "Live data/profile.json must exist."
        with open(live_profile, "r", encoding="utf-8") as f:
            data = json.load(f)

        assert data == {"is_onboarded": False}, (
            f"VIOLATION OF INV-8: Live profile.json was contaminated or altered! Value: {data}"
        )

    def test_14_phylogenetic_software_upgrade_during_migration(self, tmp_path: Path):
        """Case 14: Engine version can be updated during migration while anchor is preserved."""
        src_ws = tmp_path / "source"
        dest_ws = tmp_path / "dest"
        src_ws.mkdir()
        dest_ws.mkdir()

        setup_test_workspace(src_ws, is_onboarded=True)
        manifest, _ = freeze_for_migration(src_ws)
        archive_path = tmp_path / "mig.tar.gz"
        export_migration_archive(manifest, src_ws / "data", archive_path)

        _, receipt = verify_migration_archive(archive_path, dest_ws)
        assert receipt is not None
        proof = decommission_source_instance(src_ws, receipt)

        activate_destination_instance(
            destination_workspace_path=dest_ws,
            archive_path=archive_path,
            receipt=receipt,
            decommission_proof=proof,
            engine_version_override="0.25.0-next",
        )

        with open(dest_ws / "data" / "profile.json", "r", encoding="utf-8") as f:
            dest_profile = json.load(f)

        # Engine version evolved
        assert dest_profile["phylogenetic_lineage"]["engine_version"] == "0.25.0-next"
        # Anchor is untouched
        assert dest_profile["identity_anchor"]["instance_uuid"] == SAMPLE_UUID

    def test_15_abort_after_decommission_fails_closed(self, tmp_path: Path):
        """Case 15: Cannot abort freeze after source has already decommissioned."""
        src_ws = tmp_path / "source"
        dest_ws = tmp_path / "dest"
        src_ws.mkdir()
        dest_ws.mkdir()

        setup_test_workspace(src_ws, is_onboarded=True)
        manifest, _ = freeze_for_migration(src_ws)
        archive_path = tmp_path / "mig.tar.gz"
        export_migration_archive(manifest, src_ws / "data", archive_path)

        _, receipt = verify_migration_archive(archive_path, dest_ws)
        assert receipt is not None
        decommission_source_instance(src_ws, receipt)

        with pytest.raises(DecommissionedInstanceError):
            abort_source_freeze(src_ws)
