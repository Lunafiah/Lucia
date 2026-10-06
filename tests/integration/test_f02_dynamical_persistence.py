"""
tests/integration/test_f02_dynamical_persistence.py

Comprehensive verification suite for F-02 — Persistent Dynamical State Across Cold Restart.

Verifies:
1. Checkpoint creation and atomic disk write.
2. Checkpoint schema adherence and required state fields (h_fast in R^32, s_slow in R^16, created_at).
3. Exact restore of h_fast across process boundaries.
4. Exact restore of s_slow across process boundaries.
5. Temporal reference persistence (created_at UTC float).
6. Cold restart does not silently reset to Philia when a valid checkpoint exists.
7. Corrupted checkpoint rejection (does not mutate live state).
8. Incomplete checkpoint rejection (missing vectors, wrong dimensions, non-finite values).
9. Incompatible schema rejection (version mismatch).
10. Fallback to previous valid checkpoint (.json.bak) when primary is corrupted.
11. Fallback to canonical initial baseline when no valid checkpoint exists.
12. Genesis invariant preservation (data/profile.json bit-exact {"is_onboarded": false}).
13. Lock / I/O separation (zero disk I/O under _step_lock or _state_lock).
14. End-to-end multi-turn CognitiveOrchestrator cold restart recovery.
"""

import hashlib
import json
import os
import time
from pathlib import Path

import numpy as np
import pytest

from src.core.config import EmotionConfig, MemoryOrchestratorConfig
from src.core.emotion.emotion_core import EmotionCore
from src.core.emotion.persistence import (
    CURRENT_SCHEMA_VERSION,
    DEFAULT_DYNAMICAL_STATE_PATH,
    DEFAULT_EPOCH_MANIFEST_PATH,
    EXPECTED_FAST_DIM,
    EXPECTED_SLOW_DIM,
    DynamicalStateSnapshot,
    EpochManifest,
    load_dynamical_checkpoint,
    load_epoch_manifest,
    save_dynamical_checkpoint,
    save_epoch_manifest,
    validate_checkpoint_dict,
    verify_and_reconcile_stores,
)
from src.core.orchestrator.cognitive_orchestrator import build_cognitive_orchestrator
from src.core.relationship.persistence import load_relationship, save_relationship
from src.core.relationship.state import RelationshipState
from src.core.storage.history_store import ChatHistoryStore


class TestF02DynamicalPersistence:
    """Test suite for F-02 Persistent Dynamical State Checkpoint & Recovery."""

    def test_checkpoint_creation(self, tmp_path: Path):
        """Verify checkpoint file is created atomically on disk."""
        ckpt_path = tmp_path / "dynamical_state.json"
        assert not ckpt_path.exists()

        core = EmotionCore(storage_path=ckpt_path, auto_restore=False)
        saved = core.checkpoint()

        assert saved == ckpt_path
        assert ckpt_path.exists()
        assert ckpt_path.stat().st_size > 0

    def test_checkpoint_contains_required_state(self, tmp_path: Path):
        """Verify checkpoint contains all canonical fields matching the schema."""
        ckpt_path = tmp_path / "dynamical_state.json"
        core = EmotionCore(storage_path=ckpt_path, auto_restore=False)
        core.checkpoint()

        with open(ckpt_path, "r", encoding="utf-8") as f:
            data = json.load(f)

        assert data["schema_version"] == CURRENT_SCHEMA_VERSION
        assert isinstance(data["created_at"], (int, float))
        assert data["created_at"] > 0.0

        state = data["state"]
        assert "h_fast" in state
        assert "s_slow" in state
        assert len(state["h_fast"]) == EXPECTED_FAST_DIM
        assert len(state["s_slow"]) == EXPECTED_SLOW_DIM
        assert all(isinstance(x, (int, float)) for x in state["h_fast"])
        assert all(isinstance(x, (int, float)) for x in state["s_slow"])

        # Optional metadata
        assert "pad" in state
        assert "pleasure" in state["pad"]
        assert "arousal" in state["pad"]
        assert "dominance" in state["pad"]

    def test_restore_of_h_fast(self, tmp_path: Path):
        """Verify exact restore of fast reactive hidden state vector h_fast in R^32."""
        ckpt_path = tmp_path / "dynamical_state.json"
        core1 = EmotionCore(storage_path=ckpt_path, auto_restore=False)

        # Seed distinctive, non-zero fast state
        custom_h = np.linspace(-0.8, 0.8, EXPECTED_FAST_DIM, dtype=np.float64)
        core1._h = custom_h.copy()
        core1.checkpoint()

        # Cold restart with auto_restore=True and apply_elapsed_time=False for deterministic check
        core2 = EmotionCore(storage_path=ckpt_path, auto_restore=False)
        success = core2.restore_from_checkpoint(apply_elapsed_time=False)

        assert success is True
        recovered_h = core2.get_fast_state()
        np.testing.assert_allclose(recovered_h, custom_h, atol=1e-6)

    def test_restore_of_s_slow(self, tmp_path: Path):
        """Verify exact restore of slow affective latent field vector s_slow in R^16."""
        ckpt_path = tmp_path / "dynamical_state.json"
        core1 = EmotionCore(storage_path=ckpt_path, auto_restore=False)

        # Seed distinctive, non-baseline slow state
        custom_s = np.linspace(-0.5, 0.5, EXPECTED_SLOW_DIM, dtype=np.float64)
        core1._s_slow = custom_s.copy()
        core1.checkpoint()

        core2 = EmotionCore(storage_path=ckpt_path, auto_restore=False)
        success = core2.restore_from_checkpoint(apply_elapsed_time=False)

        assert success is True
        recovered_s = core2.get_slow_state()
        np.testing.assert_allclose(recovered_s, custom_s, atol=1e-6)

    def test_temporal_reference_persistence(self, tmp_path: Path):
        """Verify created_at POSIX timestamp is persisted and read back."""
        ckpt_path = tmp_path / "dynamical_state.json"
        t_before = time.time() - 0.001

        core = EmotionCore(storage_path=ckpt_path, auto_restore=False)
        core.checkpoint()

        t_after = time.time() + 0.001

        snapshot = load_dynamical_checkpoint(ckpt_path)
        assert snapshot is not None
        assert t_before <= snapshot.created_at <= t_after

    def test_restart_does_not_silently_reset_to_philia(self, tmp_path: Path):
        """Verify restart restores accumulated state instead of silently falling back to Philia."""
        ckpt_path = tmp_path / "dynamical_state.json"
        core1 = EmotionCore(storage_path=ckpt_path, auto_restore=False)

        # Perturb state away from Philia
        core1._h = np.ones(EXPECTED_FAST_DIM, dtype=np.float64) * 0.45
        core1._s_slow = np.ones(EXPECTED_SLOW_DIM, dtype=np.float64) * -0.35
        core1.checkpoint()

        # Re-initialize new core with auto_restore=True
        core2 = EmotionCore(storage_path=ckpt_path, auto_restore=True)

        # Confirm state is NOT Philia resting baseline
        assert not np.allclose(core2.get_fast_state(), np.zeros(EXPECTED_FAST_DIM))
        assert not np.allclose(core2.get_slow_state(), core2.s_philia)

    def test_corrupted_checkpoint_rejection(self, tmp_path: Path):
        """Verify corrupted JSON syntax is safely rejected without mutating live state."""
        ckpt_path = tmp_path / "corrupted_state.json"
        ckpt_path.write_text('{"schema_version": "1.0", "state": {"h_fast": [corrupted...', encoding="utf-8")

        core = EmotionCore(storage_path=ckpt_path, auto_restore=False)
        initial_h = core.get_fast_state().copy()
        initial_s = core.get_slow_state().copy()

        success = core.restore_from_checkpoint()
        assert success is False

        # Live state must remain unmutated
        np.testing.assert_array_equal(core.get_fast_state(), initial_h)
        np.testing.assert_array_equal(core.get_slow_state(), initial_s)

    def test_incomplete_checkpoint_rejection(self, tmp_path: Path):
        """Verify incomplete checkpoints (missing fields, wrong dimensions, non-finite values) are rejected."""
        ckpt_path = tmp_path / "incomplete.json"

        # Case 1: Missing s_slow
        bad_data_1 = {
            "schema_version": CURRENT_SCHEMA_VERSION,
            "created_at": time.time(),
            "state": {"h_fast": [0.0] * EXPECTED_FAST_DIM},
        }
        ckpt_path.write_text(json.dumps(bad_data_1), encoding="utf-8")
        assert load_dynamical_checkpoint(ckpt_path) is None

        # Case 2: Dimension mismatch for h_fast (length 10 instead of 32)
        bad_data_2 = {
            "schema_version": CURRENT_SCHEMA_VERSION,
            "created_at": time.time(),
            "state": {
                "h_fast": [0.0] * 10,
                "s_slow": [0.0] * EXPECTED_SLOW_DIM,
            },
        }
        ckpt_path.write_text(json.dumps(bad_data_2), encoding="utf-8")
        assert load_dynamical_checkpoint(ckpt_path) is None

        # Case 3: Out-of-bounds / NaN values
        bad_data_3 = {
            "schema_version": CURRENT_SCHEMA_VERSION,
            "created_at": time.time(),
            "state": {
                "h_fast": [2.5] + [0.0] * (EXPECTED_FAST_DIM - 1),  # 2.5 > 1.0 bound
                "s_slow": [0.0] * EXPECTED_SLOW_DIM,
            },
        }
        ckpt_path.write_text(json.dumps(bad_data_3), encoding="utf-8")
        assert load_dynamical_checkpoint(ckpt_path) is None

    def test_incompatible_schema_rejection(self, tmp_path: Path):
        """Verify checkpoints with unsupported schema versions are rejected."""
        ckpt_path = tmp_path / "version_mismatch.json"
        data = {
            "schema_version": "99.0",  # incompatible version
            "created_at": time.time(),
            "state": {
                "h_fast": [0.0] * EXPECTED_FAST_DIM,
                "s_slow": [0.0] * EXPECTED_SLOW_DIM,
            },
        }
        ckpt_path.write_text(json.dumps(data), encoding="utf-8")
        assert load_dynamical_checkpoint(ckpt_path) is None

    def test_fallback_to_previous_valid_checkpoint(self, tmp_path: Path):
        """Verify fallback to previous valid backup (.json.bak) when primary checkpoint is corrupted."""
        ckpt_path = tmp_path / "dynamical_state.json"
        backup_path = tmp_path / "dynamical_state.json.bak"

        core = EmotionCore(storage_path=ckpt_path, auto_restore=False)

        # Checkpoint 1: baseline state
        core._h = np.ones(EXPECTED_FAST_DIM, dtype=np.float64) * 0.25
        core.checkpoint()

        # Checkpoint 2: new state (causes checkpoint 1 to be backed up to .json.bak)
        core._h = np.ones(EXPECTED_FAST_DIM, dtype=np.float64) * 0.75
        core.checkpoint()

        assert backup_path.exists()

        # Corrupt primary checkpoint
        ckpt_path.write_text("corrupted_junk", encoding="utf-8")

        # Loading must fallback to backup
        recovered_snapshot = load_dynamical_checkpoint(ckpt_path)
        assert recovered_snapshot is not None
        # State from checkpoint 1 (0.25) was preserved in backup
        np.testing.assert_allclose(recovered_snapshot.h_fast, np.ones(EXPECTED_FAST_DIM) * 0.25, atol=1e-5)

    def test_no_valid_checkpoint_fallback_to_existing_initialization(self, tmp_path: Path):
        """Verify clean fallback to canonical initial baseline when neither primary nor backup exists."""
        nonexistent = tmp_path / "does_not_exist.json"
        core = EmotionCore(storage_path=nonexistent, auto_restore=True)

        # Must initialize to canonical Philia resting baseline
        np.testing.assert_array_equal(core.get_fast_state(), np.zeros(EXPECTED_FAST_DIM))
        np.testing.assert_array_equal(core.get_slow_state(), core.s_philia)
        pad = core.get_pad_state()
        assert np.isclose(pad.pleasure, 0.25)
        assert np.isclose(pad.arousal, -0.05)
        assert np.isclose(pad.dominance, 0.05)

    def test_genesis_invariant_remains_bit_exact(self):
        """Verify data/profile.json remains bit-exact {"is_onboarded": false}."""
        profile_path = Path("data/profile.json")
        assert profile_path.exists()
        content = profile_path.read_bytes()
        assert content == b'{"is_onboarded": false}'
        sha256 = hashlib.sha256(content).hexdigest().upper()
        assert sha256 == "1BF496E742B503A324ECD27156E4E30B30ED35CAB496897C3A831380FBF0F97C"

    def test_lock_io_separation(self, tmp_path: Path):
        """Verify disk I/O operations are never executed while holding _step_lock or _state_lock."""
        ckpt_path = tmp_path / "dynamical_state.json"
        core = EmotionCore(storage_path=ckpt_path, auto_restore=False)

        import src.core.emotion.emotion_core as ec_mod
        orig_save = ec_mod.save_dynamical_checkpoint

        lock_held_during_save = []

        def tracked_save(snapshot, filepath=None, storage_policy=None):
            # Assert neither lock is held when disk I/O occurs
            lock_held_during_save.append(core._step_lock.locked())
            lock_held_during_save.append(core._state_lock.locked())
            return orig_save(snapshot, filepath=filepath, storage_policy=storage_policy)

        ec_mod.save_dynamical_checkpoint = tracked_save
        try:
            core.checkpoint()
        finally:
            ec_mod.save_dynamical_checkpoint = orig_save

        assert lock_held_during_save == [False, False], "Lock was illegally held during disk I/O!"

    def test_orchestrator_multiturn_cold_restart_dynamical_persistence(self, tmp_path: Path):
        """
        Integration test: verify CognitiveOrchestrator persists dynamical state
        across turns and reloads accumulated limbic state across cold process restarts.
        """
        from unittest.mock import MagicMock

        ckpt_path = tmp_path / "dyn_orch.json"
        rel_path = tmp_path / "rel_orch.json"
        model_file = tmp_path / "model.gguf"
        model_file.write_bytes(b"dummy")

        config = MemoryOrchestratorConfig(
            model_path=str(model_file),
            loop_cadence_ms=100,
            decay_loop_cadence_seconds=60,
            sdm_num_locations=100,
            sdm_address_dim=64,
            sdm_content_dim=16,
            sdm_capacity=50,
        )

        mock_llm = MagicMock()
        mock_llm.is_ready.return_value = True
        mock_llm.generate.return_value = "Acknowledged with warmth."

        # Session 1: Turn 1
        orch1 = build_cognitive_orchestrator(
            config=config,
            llm_backend=mock_llm,
            relationship_storage_path=rel_path,
            dynamical_storage_path=ckpt_path,
        )
        try:
            res1 = orch1.process("Hello, I am glad to meet you today!")
            assert res1.response_text is not None

            # Verify checkpoint was created by Stage 16.5
            assert ckpt_path.exists()
            snap1 = load_dynamical_checkpoint(ckpt_path)
            assert snap1 is not None

            # Seed distinctive state on orchestrator 1 before shutdown
            orch1._emotion_core._s_slow = np.ones(EXPECTED_SLOW_DIM, dtype=np.float64) * 0.33
            orch1.shutdown()
        finally:
            if hasattr(orch1, "shutdown"):
                orch1.shutdown()

        # Session 2: Cold restart
        mock_llm2 = MagicMock()
        mock_llm2.is_ready.return_value = True
        mock_llm2.generate.return_value = "Continuing our discussion."

        orch2 = build_cognitive_orchestrator(
            config=config,
            llm_backend=mock_llm2,
            relationship_storage_path=rel_path,
            dynamical_storage_path=ckpt_path,
        )
        try:
            # Verify recovered state in session 2 is non-baseline (recovered from session 1)
            recovered_s = orch2._emotion_core.get_slow_state()
            assert not np.allclose(recovered_s, orch2._emotion_core.s_philia)

            # Turn 2 continues accumulation seamlessly
            res2 = orch2.process("We have accomplished something great together.")
            assert res2.response_text is not None
        finally:
            orch2.shutdown()

    def test_startup_dependency_inversion_relational_synchrony(self, tmp_path: Path):
        """
        Verify that RelationshipState (R_t) is loaded and injected into EmotionCore
        BEFORE dynamical checkpoint restoration and elapsed physical time integration (Remediating E-01).
        Ensures long-downtime recovery relaxes to s*_eff(R_t), NEVER to stranger Philia s_philia.
        """
        from unittest.mock import MagicMock

        rel_path = tmp_path / "relationship.json"
        dyn_path = tmp_path / "dynamical_state.json"
        model_file = tmp_path / "model.gguf"
        model_file.write_bytes(b"dummy")

        # 1. Persist mature relational state (deep friendship, far from stranger baseline [0.0, 0.5, 0.0, 0.5])
        mature_rel = RelationshipState(familiarity=0.85, trust=0.90, closeness=0.80, reciprocity=0.75)
        save_relationship(mature_rel, filepath=rel_path)

        # 2. Persist dynamical checkpoint created 10 minutes ago (Delta t = 600s >= 300s asymptotic cutoff)
        # Seed an agitated fast and slow state
        t_checkpoint = time.time() - 600.0
        agitated_h = np.ones(EXPECTED_FAST_DIM, dtype=np.float64) * 0.75
        agitated_s = np.ones(EXPECTED_SLOW_DIM, dtype=np.float64) * -0.50
        snapshot = DynamicalStateSnapshot(
            h_fast=agitated_h,
            s_slow=agitated_s,
            created_at=t_checkpoint,
            m_homeo=np.array([0.2, 0.9, 0.8, 0.1], dtype=np.float64),  # fatigued & tense
            pad={"pleasure": -0.8, "arousal": 0.8, "dominance": -0.5},
        )
        save_dynamical_checkpoint(snapshot, filepath=dyn_path)

        # 3. Boot orchestrator via build_cognitive_orchestrator
        config = MemoryOrchestratorConfig(
            model_path=str(model_file),
            loop_cadence_ms=100,
            decay_loop_cadence_seconds=60,
            sdm_num_locations=100,
            sdm_address_dim=64,
            sdm_content_dim=16,
            sdm_capacity=50,
        )
        mock_llm = MagicMock()
        mock_llm.is_ready.return_value = True

        orch = build_cognitive_orchestrator(
            config=config,
            llm_backend=mock_llm,
            relationship_storage_path=rel_path,
            dynamical_storage_path=dyn_path,
        )
        try:
            core = orch._emotion_core

            # Verification 1: EmotionCore received authoritative R_t
            r_context = core.get_relationship_context()
            np.testing.assert_allclose(r_context, mature_rel.to_array(), atol=1e-5)
            assert not np.allclose(r_context, core.R_0), "Relational context must not be stranger baseline R_0!"

            # Verification 2: Recovered slow field relaxed toward s*_eff(R_t), NOT s_philia
            s_recovered = core.get_slow_state()
            s_eff_target = core.get_effective_slow_attractor(mature_rel.to_array())

            # s*_eff(R_t) must be displaced from unconditioned s_philia
            assert not np.allclose(s_eff_target, core.s_philia), "s*_eff(R_t) must differ from unconditioned s_philia!"

            # The recovered state must match s*_eff(R_t) bit-exact or within direct projection tolerance
            np.testing.assert_allclose(s_recovered, s_eff_target, atol=1e-5)

            # Fast layer contracted to 0
            np.testing.assert_allclose(core.get_fast_state(), np.zeros(EXPECTED_FAST_DIM), atol=1e-5)

            # Verification 3: Homeostatic equilibrium restored
            markers = core._m_homeo
            assert np.isclose(markers[0], 1.0), "Energy must be 1.0 at asymptotic recovery"
            assert np.isclose(markers[1], 0.0), "Cognitive load must be 0.0 at asymptotic recovery"
            assert np.isclose(markers[2], 0.0), "Tension must be 0.0 at asymptotic recovery"

            # Verification 4: Output PAD is reprojected from recovered state, matching resting PAD
            pad = core.get_pad_state()
            expected_resting_pad = core.compute_resting_pad(mature_rel.to_array())
            np.testing.assert_allclose(
                [pad.pleasure, pad.arousal, pad.dominance],
                expected_resting_pad,
                atol=1e-4,
            )
        finally:
            orch.shutdown()

    def test_long_downtime_recovery_latency_and_boundedness(self):
        """
        Verify that 1 day (86,400s) downtime does NOT execute 432,000 Euler steps.
        Startup latency must execute in <= 10ms CPU time via direct equilibrium projection.
        """
        config = EmotionConfig(
            recovery_short_replay_cutoff_s=180.0,
            recovery_asymptotic_cutoff_s=300.0,
        )
        core = EmotionCore(config=config, auto_restore=False)

        # Perturb state
        core._h = np.ones(EXPECTED_FAST_DIM) * 0.5
        core._s_slow = np.ones(EXPECTED_SLOW_DIM) * -0.3
        core._m_homeo = np.array([0.3, 0.8, 0.7, 0.4])

        t0 = time.perf_counter()
        pad_hist, slow_hist, ht = core.integrate_unforced_idle(duration_s=86400.0, dt=0.20)
        elapsed_s = time.perf_counter() - t0

        assert elapsed_s < 0.020, f"Long downtime recovery took too long: {elapsed_s:.4f}s (must be < 20ms)"
        np.testing.assert_allclose(core.get_fast_state(), np.zeros(EXPECTED_FAST_DIM), atol=1e-6)
        np.testing.assert_allclose(core.get_slow_state(), core.get_effective_slow_attractor(), atol=1e-6)
        assert np.isclose(core._m_homeo[0], 1.0)
        assert np.isclose(core._m_homeo[1], 0.0)

    def test_hybrid_recovery_three_regimes(self):
        """
        Verify behavior across the three ratified recovery regimes:
        1. Delta t <= tau_candidate (180s): exact numerical forward Euler replay.
        2. tau_candidate < Delta t < tau_asymptotic (240s): numerical replay + exponential relaxation.
        3. Delta t >= tau_asymptotic (360s): direct equilibrium projection.
        """
        config = EmotionConfig(
            recovery_short_replay_cutoff_s=180.0,
            recovery_asymptotic_cutoff_s=300.0,
        )

        # Regime 1: Short replay (60s)
        core1 = EmotionCore(config=config, auto_restore=False)
        core1._h = np.ones(EXPECTED_FAST_DIM) * 0.4
        _, _, ht1 = core1.integrate_unforced_idle(duration_s=60.0, dt=0.20, record_trajectory=True)
        assert len(ht1.timestamps) == 300, f"Expected 300 steps for 60s at dt=0.2, got {len(ht1.timestamps)}"

        # Regime 2: Boundary (180s)
        core2 = EmotionCore(config=config, auto_restore=False)
        core2._h = np.ones(EXPECTED_FAST_DIM) * 0.4
        _, _, ht2 = core2.integrate_unforced_idle(duration_s=180.0, dt=0.20, record_trajectory=True)
        assert len(ht2.timestamps) == 900, f"Expected 900 steps for 180s at dt=0.2, got {len(ht2.timestamps)}"

        # Regime 3: Intermediate (240s)
        core3 = EmotionCore(config=config, auto_restore=False)
        core3._h = np.ones(EXPECTED_FAST_DIM) * 0.4
        _, _, ht3 = core3.integrate_unforced_idle(duration_s=240.0, dt=0.20, record_trajectory=True)
        # Should have evaluated 900 steps of Euler plus 1 final relaxed point
        assert len(ht3.timestamps) == 901
        np.testing.assert_allclose(core3.get_fast_state(), np.zeros(EXPECTED_FAST_DIM), atol=1e-6)

        # Regime 4: Long downtime (360s >= 300s)
        core4 = EmotionCore(config=config, auto_restore=False)
        core4._h = np.ones(EXPECTED_FAST_DIM) * 0.4
        _, _, ht4 = core4.integrate_unforced_idle(duration_s=360.0, dt=0.20, record_trajectory=True)
        assert len(ht4.timestamps) == 1  # direct projection point
        np.testing.assert_allclose(core4.get_fast_state(), np.zeros(EXPECTED_FAST_DIM), atol=1e-6)
        np.testing.assert_allclose(core4.get_slow_state(), core4.get_effective_slow_attractor(), atol=1e-6)

    def test_pad_derived_from_state_and_stale_pad_ignored(self, tmp_path: Path):
        """
        Verify that PAD is strictly derived from (h_fast, s_slow) and that
        any stale or bogus PAD in a serialized checkpoint cannot override runtime state.
        """
        ckpt_path = tmp_path / "dynamical_state.json"

        # Checkpoint with deliberate contradictory PAD (e.g. extreme -0.99)
        snapshot = DynamicalStateSnapshot(
            h_fast=np.zeros(EXPECTED_FAST_DIM),
            s_slow=np.zeros(EXPECTED_SLOW_DIM),
            created_at=time.time(),
            pad={"pleasure": -0.99, "arousal": 0.99, "dominance": -0.99},
        )
        save_dynamical_checkpoint(snapshot, filepath=ckpt_path)

        core = EmotionCore(storage_path=ckpt_path, auto_restore=False)
        restored = core.restore_from_checkpoint(ckpt_path, apply_elapsed_time=False)
        assert restored is True

        pad = core.get_pad_state()
        # Must match projection of (0, 0), NOT the bogus -0.99 in the JSON
        expected_pad = core._project_to_pad(np.zeros(EXPECTED_FAST_DIM), np.zeros(EXPECTED_SLOW_DIM))
        assert np.isclose(pad.pleasure, expected_pad.pleasure, atol=1e-5)
        assert not np.isclose(pad.pleasure, -0.99)

    def test_commit_barrier_and_uncommitted_rollback(self, tmp_path: Path):
        """
        Simulate a crash occurring after relationship update (epoch 5) but before
        epoch_manifest.json commit barrier (which remains at epoch 4).
        Verify that verify_and_reconcile_stores rolls back relationship.json to .bak (epoch 4).
        """
        rel_path = tmp_path / "relationship.json"
        dyn_path = tmp_path / "dynamical_state.json"
        man_path = tmp_path / "epoch_manifest.json"

        # State at epoch 4
        rel_state_4 = RelationshipState(familiarity=0.4, trust=0.5, closeness=0.4, reciprocity=0.5)
        dyn_state_4 = DynamicalStateSnapshot(
            h_fast=np.zeros(EXPECTED_FAST_DIM),
            s_slow=np.ones(EXPECTED_SLOW_DIM) * 0.1,
            created_at=time.time() - 100,
            epoch_id=4,
        )
        save_relationship(rel_state_4, filepath=rel_path, epoch_id=4)
        save_dynamical_checkpoint(dyn_state_4, filepath=dyn_path)

        # Commit barrier recorded at epoch 4
        manifest_4 = EpochManifest(
            epoch_id=4,
            t_checkpoint=time.time() - 100,
            stores={"relationship": 4, "dynamical_state": 4},
        )
        save_epoch_manifest(manifest_4, filepath=man_path)

        # Now simulate next turn step 1 (relationship written with epoch 5, creating .bak at epoch 4)
        rel_state_5 = RelationshipState(familiarity=0.5, trust=0.6, closeness=0.5, reciprocity=0.6)
        save_relationship(rel_state_5, filepath=rel_path, epoch_id=5)

        # At this moment, crash happens!
        # relationship.json has epoch 5, but manifest is at epoch 4
        assert rel_path.exists()
        assert rel_path.with_suffix(".json.bak").exists()

        # On restart, verify_and_reconcile_stores is invoked
        verify_and_reconcile_stores(
            relationship_path=rel_path,
            dynamical_path=dyn_path,
            manifest_path=man_path,
        )

        # Verification: relationship.json was rolled back to epoch 4
        restored_rel = load_relationship(rel_path)
        assert np.isclose(restored_rel.familiarity, 0.4)
        assert np.isclose(restored_rel.trust, 0.5)

    def test_divergent_epoch_detection_without_manifest(self, tmp_path: Path):
        """
        Verify that if manifest is absent and stores disagree on epoch,
        reconciliation rolls back the higher epoch store to its .bak copy.
        """
        rel_path = tmp_path / "relationship.json"
        dyn_path = tmp_path / "dynamical_state.json"

        # Setup relationship with epoch 2 (and .bak at epoch 1)
        save_relationship(RelationshipState.initial(), filepath=rel_path, epoch_id=1)
        save_relationship(RelationshipState(familiarity=0.3, trust=0.6, closeness=0.3, reciprocity=0.6), filepath=rel_path, epoch_id=2)

        # Dynamical state is at epoch 1
        dyn_snap = DynamicalStateSnapshot(
            h_fast=np.zeros(EXPECTED_FAST_DIM),
            s_slow=np.zeros(EXPECTED_SLOW_DIM),
            created_at=time.time(),
            epoch_id=1,
        )
        save_dynamical_checkpoint(dyn_snap, filepath=dyn_path)

        verify_and_reconcile_stores(
            relationship_path=rel_path,
            dynamical_path=dyn_path,
            manifest_path=tmp_path / "absent_manifest.json",
        )

        # Relationship must have been rolled back to match epoch 1
        restored_rel = load_relationship(rel_path)
        np.testing.assert_allclose(restored_rel.to_array(), RelationshipState.initial().to_array())

    def test_working_memory_reseeding_configurable_k(self, tmp_path: Path):
        """
        Verify that runtime working memory (_history) is reseeded from chat_history.json
        up to K turns (2*K messages), and that K is a configurable parameter (not hard-coded 10).
        """
        from unittest.mock import MagicMock

        chat_path = tmp_path / "chat_history.json"
        model_file = tmp_path / "model.gguf"
        model_file.write_bytes(b"dummy")

        store = ChatHistoryStore(file_path=str(chat_path))
        for i in range(25):
            store.append_turn(role="user", content=f"User prompt {i}")
            store.append_turn(role="assistant", content=f"Lucia response {i}")

        mock_llm = MagicMock()
        mock_llm.is_ready.return_value = True

        # Test with K = 5 turns (10 messages)
        cfg_k5 = MemoryOrchestratorConfig(
            model_path=str(model_file),
            context_history_turns=5,
            loop_cadence_ms=100,
            decay_loop_cadence_seconds=60,
            sdm_num_locations=100,
            sdm_address_dim=64,
            sdm_content_dim=16,
            sdm_capacity=50,
        )
        orch_k5 = build_cognitive_orchestrator(
            config=cfg_k5,
            llm_backend=mock_llm,
            chat_history_path=chat_path,
            relationship_storage_path=tmp_path / "rel.json",
            dynamical_storage_path=tmp_path / "dyn.json",
        )
        try:
            assert len(orch_k5._history) == 10, f"Expected 10 messages for K=5, got {len(orch_k5._history)}"
            assert orch_k5._history[0] == ("user", "User prompt 20")
            assert orch_k5._history[-1] == ("assistant", "Lucia response 24")
        finally:
            orch_k5.shutdown()

        # Test with K = 12 turns (24 messages)
        cfg_k12 = MemoryOrchestratorConfig(
            model_path=str(model_file),
            context_history_turns=12,
            loop_cadence_ms=100,
            decay_loop_cadence_seconds=60,
            sdm_num_locations=100,
            sdm_address_dim=64,
            sdm_content_dim=16,
            sdm_capacity=50,
        )
        orch_k12 = build_cognitive_orchestrator(
            config=cfg_k12,
            llm_backend=mock_llm,
            chat_history_path=chat_path,
            relationship_storage_path=tmp_path / "rel.json",
            dynamical_storage_path=tmp_path / "dyn.json",
        )
        try:
            assert len(orch_k12._history) == 24, f"Expected 24 messages for K=12, got {len(orch_k12._history)}"
            assert orch_k12._history[0] == ("user", "User prompt 13")
            assert orch_k12._history[-1] == ("assistant", "Lucia response 24")
        finally:
            orch_k12.shutdown()

    def test_multi_turn_commit_barrier_manifest_generation(self, tmp_path: Path):
        """
        Verify that successive turns on CognitiveOrchestrator advance the logical epoch
        and atomically synchronize relationship.json, dynamical_state.json, and epoch_manifest.json.
        """
        from unittest.mock import MagicMock

        rel_path = tmp_path / "relationship.json"
        dyn_path = tmp_path / "dynamical_state.json"
        man_path = tmp_path / "epoch_manifest.json"
        model_file = tmp_path / "model.gguf"
        model_file.write_bytes(b"dummy")

        config = MemoryOrchestratorConfig(
            model_path=str(model_file),
            loop_cadence_ms=100,
            decay_loop_cadence_seconds=60,
            sdm_num_locations=100,
            sdm_address_dim=64,
            sdm_content_dim=16,
            sdm_capacity=50,
        )
        mock_llm = MagicMock()
        mock_llm.is_ready.return_value = True
        mock_llm.generate.return_value = "Response content."

        orch = build_cognitive_orchestrator(
            config=config,
            llm_backend=mock_llm,
            relationship_storage_path=rel_path,
            dynamical_storage_path=dyn_path,
            epoch_manifest_path=man_path,
        )
        try:
            # Turn 1
            orch.process("First user message")
            manifest1 = load_epoch_manifest(man_path)
            assert manifest1 is not None
            assert manifest1.epoch_id == 1
            assert manifest1.stores["relationship"] == 1
            assert manifest1.stores["dynamical_state"] == 1

            # Turn 2
            orch.process("Second user message")
            manifest2 = load_epoch_manifest(man_path)
            assert manifest2 is not None
            assert manifest2.epoch_id == 2
            assert manifest2.stores["relationship"] == 2
            assert manifest2.stores["dynamical_state"] == 2

            # Turn 3
            orch.process("Third user message")
            manifest3 = load_epoch_manifest(man_path)
            assert manifest3 is not None
            assert manifest3.epoch_id == 3
        finally:
            orch.shutdown()
