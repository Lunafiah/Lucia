"""
tests/unit/test_epoch_state_interaction.py

Unit test suite for WP-04 — Epoch / State Interaction under ADR-034 & ADR-033 / F-02.

Validates:
1. Normal startup with valid epoch across manifest and stores.
2. Valid identity anchor + valid authority binding + valid epoch integration.
3. Epoch divergence detection with manifest commit barrier (uncommitted rollback to .bak).
4. Epoch divergence detection without manifest (reconcile higher store to .bak).
5. Truncated or corrupted epoch manifest detection and handling.
6. Manifest with missing required fields (epoch_id, t_checkpoint) detection.
7. Corrupted primary stores restored from valid .bak.
8. Corrupted primary stores without .bak detected and reported.
9. Stale stores (store epoch < committed epoch) detected and reported.
10. Interrupted / partial state commit simulation (crash between relationship write and manifest commit).
11. Profile and epoch orthogonality: profile.json is NEVER touched by .bak or epoch rollbacks.
12. Identity Anchor immutable fields bit-for-bit preservation across all reconciliation operations.
13. Hardware reconfirmation preserves identity anchor and precedes epoch verification.
14. Phylogenetic upgrade preserves identity anchor and epoch state.
15. Pre-Genesis profile invariant: data/profile.json remains {"is_onboarded": false}.
"""

from __future__ import annotations

import copy
import hashlib
import json
import os
from pathlib import Path
import time
from typing import Any, Dict

import numpy as np
import pytest

from src.core.emotion.persistence import (
    CURRENT_SCHEMA_VERSION,
    DEFAULT_DYNAMICAL_STATE_PATH,
    DEFAULT_EPOCH_MANIFEST_PATH,
    EXPECTED_FAST_DIM,
    EXPECTED_SLOW_DIM,
    DynamicalStateSnapshot,
    EpochManifest,
    StoreReconciliationReport,
    load_dynamical_checkpoint,
    load_epoch_manifest,
    save_dynamical_checkpoint,
    save_epoch_manifest,
    verify_and_reconcile_stores,
)
from src.core.identity.identity_anchor import (
    CANONICAL_SCHEMA_VERSION,
    DEFAULT_PROFILE_PATH,
    IMMUTABLE_IDENTITY_FIELDS,
    apply_phylogenetic_upgrade,
    guard_immutable_fields,
    verify_identity_on_startup,
)
from src.core.identity.provenance_verifier import (
    collect_hardware_components,
    compute_component_digests,
    compute_hardware_digest,
    normalize_workspace_path,
    reconfirm_hardware_environment,
    verify_provenance_and_environment,
)
from src.core.relationship.persistence import (
    DEFAULT_RELATIONSHIP_PATH,
    load_relationship,
    save_relationship,
)
from src.core.relationship.state import RelationshipState

SAMPLE_UUID = "3fa85f64-5717-4562-b3fc-2c963f66afa6"
SAMPLE_BORN_AT = "2026-10-01T00:00:00.000000Z"
SAMPLE_COMMIT = "ce106a245890abcdef1234567890abcdef123456"
SAMPLE_ROOT_HASH = "e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855"


def create_test_profile(
    path: Path,
    workspace_path: Path,
    bound_hardware_digest: str,
    migration_epoch: int = 0,
) -> Dict[str, Any]:
    """Helper to write a valid onboarded profile for testing."""
    comps = collect_hardware_components(workspace_path)
    data = {
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
            "bound_machine_guid_digest": bound_hardware_digest,
            "activation_host_platform": comps.platform_str,
            "last_known_canonical_path": normalize_workspace_path(workspace_path),
            "hardware_migration_epoch": migration_epoch,
            "last_verified_at": SAMPLE_BORN_AT,
            "component_digests": compute_component_digests(comps),
        },
        "user_name": "Friend",
        "companion_name": "Lucia",
    }
    path.write_text(json.dumps(data, indent=2), encoding="utf-8")
    return data


def create_test_stores(
    directory: Path,
    epoch_id: int,
) -> tuple[Path, Path, Path]:
    """Create synchronized relationship.json, dynamical_state.json, and epoch_manifest.json."""
    rel_p = directory / "relationship.json"
    dyn_p = directory / "dynamical_state.json"
    man_p = directory / "epoch_manifest.json"

    rel_state = RelationshipState(familiarity=0.5, trust=0.6, closeness=0.4, reciprocity=0.5)
    save_relationship(rel_state, filepath=rel_p, epoch_id=epoch_id)

    dyn_snap = DynamicalStateSnapshot(
        h_fast=np.zeros(EXPECTED_FAST_DIM),
        s_slow=np.ones(EXPECTED_SLOW_DIM) * 0.1,
        created_at=time.time(),
        epoch_id=epoch_id,
    )
    save_dynamical_checkpoint(dyn_snap, filepath=dyn_p)

    manifest = EpochManifest(
        epoch_id=epoch_id,
        t_checkpoint=time.time(),
        stores={"relationship": epoch_id, "dynamical_state": epoch_id},
    )
    save_epoch_manifest(manifest, filepath=man_p)

    return rel_p, dyn_p, man_p


class TestEpochStateInteractionUnit:
    """Unit tests for WP-04 Epoch manifest and persistent state interactions."""

    def test_normal_startup_with_valid_epoch(self, tmp_path: Path):
        """Valid epoch across manifest and stores produces consistent report with zero rollbacks."""
        rel_p, dyn_p, man_p = create_test_stores(tmp_path, epoch_id=3)

        report = verify_and_reconcile_stores(
            relationship_path=rel_p,
            dynamical_path=dyn_p,
            manifest_path=man_p,
        )

        assert isinstance(report, StoreReconciliationReport)
        assert report.is_consistent
        assert report.manifest_loaded
        assert not report.manifest_corrupted_or_truncated
        assert report.committed_epoch == 3
        assert report.corrupted_stores_restored == []
        assert report.uncommitted_stores_rolled_back == []
        assert report.divergent_stores_reconciled == []
        assert report.inconsistencies_detected == []

    def test_valid_identity_valid_authority_valid_epoch_integration(self, tmp_path: Path):
        """Verifies full validation chain from identity to authority to epoch manifest."""
        ws_dir = tmp_path / "workspace"
        ws_dir.mkdir()
        profile_p = tmp_path / "profile.json"

        comps = collect_hardware_components(ws_dir)
        hw_digest = compute_hardware_digest(comps)
        create_test_profile(profile_p, ws_dir, bound_hardware_digest=hw_digest)

        # 1. Identity Anchor validation (WP-02)
        id_state = verify_identity_on_startup(profile_p)
        assert id_state.is_onboarded
        assert not id_state.is_genesis_locked
        assert id_state.anchor is not None
        assert id_state.anchor.instance_uuid == SAMPLE_UUID

        # 2. Authority & Provenance validation (WP-03)
        prov_res = verify_provenance_and_environment(
            workspace_path=ws_dir,
            profile_path=profile_p,
            allow_reconfirmation=False,
        )
        assert prov_res.is_valid
        assert prov_res.hardware_matched

        # 3. Epoch & store reconciliation (ADR-033 / WP-04)
        rel_p, dyn_p, man_p = create_test_stores(tmp_path, epoch_id=5)
        report = verify_and_reconcile_stores(
            relationship_path=rel_p,
            dynamical_path=dyn_p,
            manifest_path=man_p,
        )
        assert report.is_consistent
        assert report.committed_epoch == 5

        # 4. Identity anchor bit-exact verification
        re_checked_id = verify_identity_on_startup(profile_p)
        assert re_checked_id.anchor.instance_uuid == SAMPLE_UUID
        assert re_checked_id.anchor.born_at == SAMPLE_BORN_AT
        assert re_checked_id.anchor.genesis_commit == SAMPLE_COMMIT
        assert re_checked_id.anchor.genesis_root_hash == SAMPLE_ROOT_HASH

    def test_epoch_divergence_detection_relationship_ahead_of_manifest(self, tmp_path: Path):
        """Crash after relationship write rolls uncommitted relationship store back to .bak."""
        rel_p, dyn_p, man_p = create_test_stores(tmp_path, epoch_id=4)

        # Write next relationship state (epoch 5), creating .bak at epoch 4
        rel_state_5 = RelationshipState(familiarity=0.8, trust=0.9, closeness=0.8, reciprocity=0.9)
        save_relationship(rel_state_5, filepath=rel_p, epoch_id=5)

        # Manifest remains at epoch 4
        report = verify_and_reconcile_stores(
            relationship_path=rel_p,
            dynamical_path=dyn_p,
            manifest_path=man_p,
        )

        assert "relationship.json" in report.uncommitted_stores_rolled_back
        assert report.committed_epoch == 4

        # Loaded relationship must reflect rolled back state at epoch 4
        restored = load_relationship(rel_p)
        assert np.isclose(restored.familiarity, 0.5)
        assert np.isclose(restored.trust, 0.6)

    def test_epoch_divergence_detection_dynamical_ahead_of_manifest(self, tmp_path: Path):
        """Crash after dynamical state write rolls uncommitted dynamical store back to .bak."""
        rel_p, dyn_p, man_p = create_test_stores(tmp_path, epoch_id=4)

        # Write next dynamical state (epoch 5), creating .bak at epoch 4
        dyn_snap_5 = DynamicalStateSnapshot(
            h_fast=np.ones(EXPECTED_FAST_DIM) * 0.9,
            s_slow=np.ones(EXPECTED_SLOW_DIM) * 0.9,
            created_at=time.time(),
            epoch_id=5,
        )
        save_dynamical_checkpoint(dyn_snap_5, filepath=dyn_p)

        report = verify_and_reconcile_stores(
            relationship_path=rel_p,
            dynamical_path=dyn_p,
            manifest_path=man_p,
        )

        assert "dynamical_state.json" in report.uncommitted_stores_rolled_back
        assert report.committed_epoch == 4

        restored = load_dynamical_checkpoint(dyn_p)
        assert restored is not None
        assert restored.epoch_id == 4
        assert np.allclose(restored.h_fast, np.zeros(EXPECTED_FAST_DIM))

    def test_epoch_divergence_detection_without_manifest(self, tmp_path: Path):
        """When manifest is absent, store divergence rolls back higher store to match lower."""
        rel_p = tmp_path / "relationship.json"
        dyn_p = tmp_path / "dynamical_state.json"
        absent_man = tmp_path / "absent_manifest.json"

        # Relationship at epoch 1 then epoch 2 (bak at 1)
        save_relationship(RelationshipState.initial(), filepath=rel_p, epoch_id=1)
        save_relationship(RelationshipState(familiarity=0.7, trust=0.8, closeness=0.7, reciprocity=0.8), filepath=rel_p, epoch_id=2)

        # Dynamical state at epoch 1
        dyn_snap = DynamicalStateSnapshot(
            h_fast=np.zeros(EXPECTED_FAST_DIM),
            s_slow=np.zeros(EXPECTED_SLOW_DIM),
            created_at=time.time(),
            epoch_id=1,
        )
        save_dynamical_checkpoint(dyn_snap, filepath=dyn_p)

        report = verify_and_reconcile_stores(
            relationship_path=rel_p,
            dynamical_path=dyn_p,
            manifest_path=absent_man,
        )

        assert "relationship" in report.divergent_stores_reconciled
        assert not report.manifest_loaded
        assert report.committed_epoch is None

        restored_rel = load_relationship(rel_p)
        np.testing.assert_allclose(restored_rel.to_array(), RelationshipState.initial().to_array())

    def test_truncated_or_corrupted_manifest_detection(self, tmp_path: Path):
        """Truncated or corrupted manifest is flagged and stores reconciled safely."""
        rel_p, dyn_p, man_p = create_test_stores(tmp_path, epoch_id=2)

        # Overwrite manifest with truncated JSON
        man_p.write_text('{"epoch_id": 2, "t_checkpoint": ', encoding="utf-8")

        report = verify_and_reconcile_stores(
            relationship_path=rel_p,
            dynamical_path=dyn_p,
            manifest_path=man_p,
        )

        assert not report.manifest_loaded
        assert report.manifest_corrupted_or_truncated
        assert any("truncated, corrupted" in err for err in report.inconsistencies_detected)

    def test_manifest_missing_required_fields_detection(self, tmp_path: Path):
        """Manifest lacking required schema fields (epoch_id or t_checkpoint) is flagged."""
        rel_p, dyn_p, man_p = create_test_stores(tmp_path, epoch_id=2)

        # Missing t_checkpoint
        man_p.write_text(json.dumps({"epoch_id": 2, "stores": {}}), encoding="utf-8")

        report = verify_and_reconcile_stores(
            relationship_path=rel_p,
            dynamical_path=dyn_p,
            manifest_path=man_p,
        )

        assert not report.manifest_loaded
        assert report.manifest_corrupted_or_truncated

    def test_corrupted_primary_store_restores_from_bak(self, tmp_path: Path):
        """Corrupted primary JSON store is automatically restored from its .json.bak."""
        rel_p, dyn_p, man_p = create_test_stores(tmp_path, epoch_id=1)

        # Ensure backup exists by saving a second state
        save_relationship(RelationshipState(familiarity=0.6, trust=0.7, closeness=0.6, reciprocity=0.7), filepath=rel_p, epoch_id=2)
        save_epoch_manifest(EpochManifest(epoch_id=2, t_checkpoint=time.time(), stores={"relationship": 2, "dynamical_state": 1}), filepath=man_p)

        # Corrupt primary relationship.json
        rel_p.write_bytes(b"CORRUPTED_NON_JSON_BYTES{{")

        report = verify_and_reconcile_stores(
            relationship_path=rel_p,
            dynamical_path=dyn_p,
            manifest_path=man_p,
        )

        assert "relationship.json" in report.corrupted_stores_restored
        # The file is valid JSON again
        restored = load_relationship(rel_p)
        assert restored is not None

    def test_corrupted_primary_store_without_bak_reports_inconsistency(self, tmp_path: Path):
        """Corrupted store without any backup is recorded as an inconsistency."""
        rel_p = tmp_path / "relationship.json"
        dyn_p = tmp_path / "dynamical_state.json"
        man_p = tmp_path / "epoch_manifest.json"

        rel_p.write_bytes(b"MALFORMED_GARBAGE")
        bak_p = rel_p.with_suffix(".json.bak")
        if bak_p.exists():
            bak_p.unlink()

        dyn_snap = DynamicalStateSnapshot(
            h_fast=np.zeros(EXPECTED_FAST_DIM),
            s_slow=np.zeros(EXPECTED_SLOW_DIM),
            created_at=time.time(),
            epoch_id=1,
        )
        save_dynamical_checkpoint(dyn_snap, filepath=dyn_p)

        report = verify_and_reconcile_stores(
            relationship_path=rel_p,
            dynamical_path=dyn_p,
            manifest_path=man_p,
        )

        assert not report.is_consistent
        assert any("no valid backup exists" in err for err in report.inconsistencies_detected)

    def test_stale_store_behind_manifest_reports_inconsistency(self, tmp_path: Path):
        """Store with epoch strictly behind manifest is reported as inconsistent."""
        rel_p = tmp_path / "relationship.json"
        dyn_p = tmp_path / "dynamical_state.json"
        man_p = tmp_path / "epoch_manifest.json"

        # Manifest at epoch 5
        manifest = EpochManifest(epoch_id=5, t_checkpoint=time.time(), stores={"relationship": 5, "dynamical_state": 5})
        save_epoch_manifest(manifest, filepath=man_p)

        # Stores at epoch 3 (behind manifest)
        save_relationship(RelationshipState.initial(), filepath=rel_p, epoch_id=3)
        dyn_snap = DynamicalStateSnapshot(
            h_fast=np.zeros(EXPECTED_FAST_DIM),
            s_slow=np.zeros(EXPECTED_SLOW_DIM),
            created_at=time.time(),
            epoch_id=3,
        )
        save_dynamical_checkpoint(dyn_snap, filepath=dyn_p)

        report = verify_and_reconcile_stores(
            relationship_path=rel_p,
            dynamical_path=dyn_p,
            manifest_path=man_p,
        )

        assert not report.is_consistent
        assert any("behind committed epoch" in err for err in report.inconsistencies_detected)

    def test_interrupted_partial_state_commit_simulation(self, tmp_path: Path):
        """
        Simulate an interrupted cognitive turn commit:
        Step 1: Relationship updated to epoch 8 (bak at 7).
        Step 2: Crash occurs before dynamical checkpoint or manifest write (both at 7).
        Reconciliation rolls back relationship to 7, leaving zero contradictory state.
        Asserts profile.json remains completely untouched.
        """
        ws_dir = tmp_path / "workspace"
        ws_dir.mkdir()
        profile_p = tmp_path / "profile.json"
        comps = collect_hardware_components(ws_dir)
        hw_digest = compute_hardware_digest(comps)
        create_test_profile(profile_p, ws_dir, bound_hardware_digest=hw_digest)
        profile_hash_before = hashlib.sha256(profile_p.read_bytes()).hexdigest()

        # Initial coherent state at epoch 7
        rel_p, dyn_p, man_p = create_test_stores(tmp_path, epoch_id=7)

        # Advance relationship to 8
        rel_8 = RelationshipState(familiarity=0.75, trust=0.85, closeness=0.75, reciprocity=0.85)
        save_relationship(rel_8, filepath=rel_p, epoch_id=8)

        # Crash happens here!
        # Reconcile stores on recovery
        report = verify_and_reconcile_stores(
            relationship_path=rel_p,
            dynamical_path=dyn_p,
            manifest_path=man_p,
        )

        assert "relationship.json" in report.uncommitted_stores_rolled_back
        assert report.committed_epoch == 7

        # Both relationship and dynamical state are coherent at epoch 7
        restored_rel = load_relationship(rel_p)
        assert np.isclose(restored_rel.familiarity, 0.5)

        restored_dyn = load_dynamical_checkpoint(dyn_p)
        assert restored_dyn is not None
        assert restored_dyn.epoch_id == 7

        # Profile was completely untouched
        profile_hash_after = hashlib.sha256(profile_p.read_bytes()).hexdigest()
        assert profile_hash_before == profile_hash_after

    def test_profile_and_epoch_orthogonality_no_profile_bak_rollback(self, tmp_path: Path):
        """
        Invariant 7: .json.bak recovery must not accidentally restore an older
        identity anchor or authority state over a newer valid state.
        verify_and_reconcile_stores NEVER touches profile.json.
        """
        profile_p = tmp_path / "profile.json"
        ws_dir = tmp_path / "ws"
        ws_dir.mkdir()
        comps = collect_hardware_components(ws_dir)
        hw_digest = compute_hardware_digest(comps)
        create_test_profile(profile_p, ws_dir, bound_hardware_digest=hw_digest, migration_epoch=2)
        valid_bytes = profile_p.read_bytes()

        # Create an artificial profile.json.bak with an older or tampered state
        profile_bak = tmp_path / "profile.json.bak"
        tampered_data = json.loads(valid_bytes.decode("utf-8"))
        tampered_data["authority_binding"]["hardware_migration_epoch"] = 0
        profile_bak.write_text(json.dumps(tampered_data, indent=2), encoding="utf-8")

        # Run store reconciliation
        rel_p, dyn_p, man_p = create_test_stores(tmp_path, epoch_id=1)
        verify_and_reconcile_stores(
            relationship_path=rel_p,
            dynamical_path=dyn_p,
            manifest_path=man_p,
        )

        # profile.json must remain 100% bit-exact to valid_bytes, NOT restored to .bak
        assert profile_p.read_bytes() == valid_bytes

    def test_identity_anchor_bit_for_bit_preservation_across_all_operations(self, tmp_path: Path):
        """Invariant 4: Identity Anchor immutable fields remain bit-for-bit unchanged through all operations."""
        ws_dir = tmp_path / "ws"
        ws_dir.mkdir()
        profile_p = tmp_path / "profile.json"
        comps = collect_hardware_components(ws_dir)
        hw_digest = compute_hardware_digest(comps)
        initial_profile = create_test_profile(profile_p, ws_dir, bound_hardware_digest=hw_digest)

        def _get_anchor(p_path: Path) -> Dict[str, str]:
            data = json.loads(p_path.read_text(encoding="utf-8"))
            return {k: str(data["identity_anchor"][k]) for k in IMMUTABLE_IDENTITY_FIELDS}

        expected_anchor = _get_anchor(profile_p)

        # 1. Normal startup verification
        verify_identity_on_startup(profile_p)
        assert _get_anchor(profile_p) == expected_anchor

        # 2. State checkpoint & turn
        rel_p, dyn_p, man_p = create_test_stores(tmp_path, epoch_id=1)
        assert _get_anchor(profile_p) == expected_anchor

        # 3. Store rollback / reconciliation
        save_relationship(RelationshipState(familiarity=0.9, trust=0.9, closeness=0.9, reciprocity=0.9), filepath=rel_p, epoch_id=2)
        verify_and_reconcile_stores(relationship_path=rel_p, dynamical_path=dyn_p, manifest_path=man_p)
        assert _get_anchor(profile_p) == expected_anchor

        # 4. Hardware reconfirmation
        reconfirm_hardware_environment(current_workspace_path=ws_dir, profile_path=profile_p)
        assert _get_anchor(profile_p) == expected_anchor

        # 5. Phylogenetic upgrade
        with open(profile_p, "r", encoding="utf-8") as f:
            curr = json.load(f)
        upgraded = apply_phylogenetic_upgrade(curr, new_engine_version="0.25.0")
        with open(profile_p, "w", encoding="utf-8") as f:
            json.dump(upgraded, f, indent=2)
        assert _get_anchor(profile_p) == expected_anchor

    def test_hardware_reconfirmation_followed_by_epoch_verification(self, tmp_path: Path):
        """
        Hardware reconfirmation safely updates authority_binding, increments migration_epoch,
        preserves identity anchor, and proceeds safely to epoch verification.
        """
        ws_dir = tmp_path / "ws"
        ws_dir.mkdir()
        profile_p = tmp_path / "profile.json"
        stale_digest = "a" * 64
        create_test_profile(profile_p, ws_dir, bound_hardware_digest=stale_digest, migration_epoch=0)

        # 1. Detection before reconfirmation
        res = verify_provenance_and_environment(
            workspace_path=ws_dir,
            profile_path=profile_p,
            allow_reconfirmation=False,
        )
        assert not res.is_valid
        assert res.status.name == "AWAITING_HARDWARE_RECONFIRMATION"

        # 2. Reconfirmation
        updated_profile = reconfirm_hardware_environment(current_workspace_path=ws_dir, profile_path=profile_p)
        auth = updated_profile["authority_binding"]
        assert auth["hardware_migration_epoch"] == 1
        comps = collect_hardware_components(ws_dir)
        assert auth["bound_machine_guid_digest"] == compute_hardware_digest(comps)

        # 3. Provenance check now passes
        res_after = verify_provenance_and_environment(
            workspace_path=ws_dir,
            profile_path=profile_p,
            allow_reconfirmation=False,
        )
        assert res_after.is_valid

        # 4. Epoch verification follows cleanly
        rel_p, dyn_p, man_p = create_test_stores(tmp_path, epoch_id=4)
        rep = verify_and_reconcile_stores(
            relationship_path=rel_p,
            dynamical_path=dyn_p,
            manifest_path=man_p,
        )
        assert rep.is_consistent
        assert rep.committed_epoch == 4

        # 5. Identity Anchor bit-exact check
        anchor = updated_profile["identity_anchor"]
        assert anchor["instance_uuid"] == SAMPLE_UUID
        assert anchor["born_at"] == SAMPLE_BORN_AT
        assert anchor["genesis_commit"] == SAMPLE_COMMIT
        assert anchor["genesis_root_hash"] == SAMPLE_ROOT_HASH

    def test_pre_genesis_profile_invariant(self, tmp_path: Path):
        """
        Invariant 10: Genesis remains completely LOCKED.
        Pre-Genesis profile {"is_onboarded": false} causes zero identity generation
        and zero disk mutations.
        """
        profile_p = tmp_path / "profile.json"
        profile_p.write_text('{"is_onboarded": false}', encoding="utf-8")
        hash_before = hashlib.sha256(profile_p.read_bytes()).hexdigest()

        # 1. Identity startup check
        id_state = verify_identity_on_startup(profile_p)
        assert not id_state.is_onboarded
        assert id_state.is_genesis_locked
        assert id_state.anchor is None

        # 2. Provenance check (deferred)
        prov_res = verify_provenance_and_environment(
            workspace_path=tmp_path,
            profile_path=profile_p,
            allow_reconfirmation=False,
        )
        assert prov_res.is_genesis_locked

        # 3. Store reconciliation
        rel_p, dyn_p, man_p = create_test_stores(tmp_path, epoch_id=1)
        rep = verify_and_reconcile_stores(
            relationship_path=rel_p,
            dynamical_path=dyn_p,
            manifest_path=man_p,
        )
        assert rep.is_consistent

        # 4. Verify live data/profile.json remains bit-exact
        live_profile = Path("data/profile.json")
        assert live_profile.exists()
        assert live_profile.read_text(encoding="utf-8").strip() == '{"is_onboarded": false}'

        # Test profile remains bit-exact
        assert hashlib.sha256(profile_p.read_bytes()).hexdigest() == hash_before
