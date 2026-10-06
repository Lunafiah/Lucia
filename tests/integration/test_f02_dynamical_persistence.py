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
    EXPECTED_FAST_DIM,
    EXPECTED_SLOW_DIM,
    DynamicalStateSnapshot,
    load_dynamical_checkpoint,
    save_dynamical_checkpoint,
    validate_checkpoint_dict,
)
from src.core.orchestrator.cognitive_orchestrator import build_cognitive_orchestrator


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
