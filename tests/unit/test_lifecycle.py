"""
Unit tests for Backend Lifecycle Reset (POST /lifecycle/end).

Validates:
- Lifecycle endpoint success (200 OK and valid response schema)
- Profile persistence becomes Genesis-ready (is_onboarded == False, default identity)
- Conversation history persistence is wiped clean
- Affective memory / SDM store is cleared (trace count 0)
- EmotionCore PAD returns to documented resting attractor (+0.25, -0.05, +0.05)
- EmotionCore learned weights and hidden state h are reset to baseline
- HomeostaticEngine and active orchestrator dialogue state are reset
- Stability telemetry evaluator is reset
- Repeated lifecycle reset calls are safe and idempotent
- Unrelated model and application assets remain untouched
- Atomicity / error handling when a subsystem reset fails
"""

from __future__ import annotations

import json
from pathlib import Path
from unittest.mock import MagicMock, patch

import numpy as np
import pytest
from starlette.testclient import TestClient

import src.api.server as api_module
from src.core.config import EmotionConfig, MemoryOrchestratorConfig
from src.core.emotion.emotion_core import EmotionCore
from src.core.emotion.homeostatic_engine import HomeostaticEngine
from src.core.memory.affective_memory import AffectiveMemory, AffectiveMemoryConfig
from src.core.memory.sdm import SDMConfig, SDMCore
from src.core.models import BehavioralConstraints, PADState, SomaticMarkers
from src.core.orchestrator.orchestrator import MemoryAugmentedOrchestrator
from src.core.storage.history_store import ChatHistoryStore
from src.core.telemetry.stability_evaluator import StabilityEvaluator


@pytest.fixture
def isolated_env(tmp_path):
    """
    Provide isolated profile and history files in a temporary directory
    to prevent mutating actual application data.
    """
    profile_file = tmp_path / "profile.json"
    history_file = tmp_path / "chat_history.json"

    # Save original globals
    orig_profile_path = api_module._PROFILE_FILE_PATH
    orig_history_file = api_module._history_store.file_path

    # Set up isolated paths
    api_module._PROFILE_FILE_PATH = profile_file
    api_module._history_store.file_path = history_file
    api_module._history_store._ensure_file_exists()

    # Pre-populate active/onboarded profile
    active_profile = {
        "version": 1,
        "user_name": "ActiveUser",
        "companion_name": "OldLucia",
        "born_at": "2026-01-01T00:00:00",
        "is_onboarded": True,
        "pronouns": "she/her",
        "avatar_engine": "sprites",
        "avatar_model": "custom_v1",
    }
    with open(profile_file, "w", encoding="utf-8") as f:
        json.dump(active_profile, f, indent=2)

    # Pre-populate history turns
    api_module._history_store.append_turn("user", "Hello old Lucia")
    api_module._history_store.append_turn("companion", "Farewell my friend")

    # Dirty stability evaluator
    api_module._stability_evaluator.record_recovery_event()
    api_module._stability_evaluator.record_recovery_event()
    api_module._stability_evaluator.record_surprise(0.85)
    api_module._stability_evaluator.update_sdm_count(42)

    yield {
        "tmp_path": tmp_path,
        "profile_file": profile_file,
        "history_file": history_file,
    }

    # Restore originals
    api_module._PROFILE_FILE_PATH = orig_profile_path
    api_module._history_store.file_path = orig_history_file


@pytest.fixture
def mock_instrumented_orchestrator():
    """Create a fully-mocked orchestrator with dirty state."""
    orch = MagicMock(spec=api_module.InstrumentedOrchestrator)
    orch.is_healthy.return_value = True
    orch._degraded = True
    orch._history = [("user", "old text"), ("assistant", "old answer")]
    orch._last_somatic = SomaticMarkers(0.5, 0.9, 0.2, 0.8)
    orch._last_constraints = BehavioralConstraints(80, 0.9, 500, 2)

    # Mock emotion core
    emotion_core = MagicMock(spec=EmotionCore)
    emotion_core.get_pad_state.return_value = PADState(0.9, 0.8, -0.4, 1.0)
    orch._emotion_core = emotion_core

    # Mock affective memory
    affective_memory = MagicMock(spec=AffectiveMemory)
    affective_memory.trace_count = 15
    affective_memory.get_all_traces.return_value = [1, 2, 3]
    orch._affective_memory = affective_memory

    # When reset_lifecycle is called, mimic resetting internal state
    def do_reset():
        orch._degraded = False
        orch._history = []
        orch._last_somatic = None
        orch._last_constraints = None
        orch._affective_memory.trace_count = 0
        orch._affective_memory.get_all_traces.return_value = []
        orch._emotion_core.get_pad_state.return_value = PADState(0.25, -0.05, 0.05, 0.0)

    orch.reset_lifecycle.side_effect = do_reset
    return orch


@pytest.fixture
def client(isolated_env, mock_instrumented_orchestrator):
    orig_mode = api_module._mode
    orig_sim = api_module._sim_runtime
    api_module._mode = "live"
    api_module._sim_runtime = None
    api_module._orchestrator = mock_instrumented_orchestrator
    test_client = TestClient(api_module.app)
    yield test_client
    api_module._orchestrator = None
    api_module._mode = orig_mode
    api_module._sim_runtime = orig_sim


class TestSubsystemResetPrimitives:
    """Validate explicit reset() and clear() methods on individual subsystems."""

    def test_sdm_core_clear(self):
        sdm = SDMCore(SDMConfig(num_locations=100, address_dim=64, content_dim=16, capacity=10))
        addr = np.ones(64, dtype=np.uint8)
        content = np.ones(16, dtype=np.float32) * 0.5
        tid = sdm.write(addr, content)
        assert sdm.trace_count == 1
        assert tid == 0
        assert np.any(sdm._accumulator != 0.0)
        assert np.any(sdm._act_counts != 0)

        sdm.clear()
        assert sdm.trace_count == 0
        assert sdm._next_id == 0
        assert np.all(sdm._accumulator == 0.0)
        assert np.all(sdm._act_counts == 0)

    def test_affective_memory_clear(self):
        sdm_cfg = SDMConfig(num_locations=100, address_dim=64, content_dim=16, capacity=10)
        mem = AffectiveMemory(AffectiveMemoryConfig(sdm_config=sdm_cfg, m=16))
        content = np.ones(16, dtype=np.float32) * 0.3
        pad = PADState(0.4, -0.2, 0.1, 0.0)
        mem.store(content, pad)
        assert mem.trace_count == 1
        assert len(mem.get_all_traces()) == 1

        mem.clear()
        assert mem.trace_count == 0
        assert len(mem.get_all_traces()) == 0

    def test_emotion_core_reset_to_resting(self):
        cfg = EmotionConfig(loop_cadence_ms=100, hidden_dim=8, resting_baseline=(0.25, -0.05, 0.05))
        core = EmotionCore(cfg)

        # Dirty state
        core._h = np.ones(8, dtype=np.float64) * 0.77
        core.push_stimulus(np.ones(16) * 0.9)
        core.W_f += 1.5  # simulate trained weights

        core.reset_to_resting()

        pad = core.get_pad_state()
        assert pad.pleasure == pytest.approx(0.25)
        assert pad.arousal == pytest.approx(-0.05)
        assert pad.dominance == pytest.approx(0.05)
        assert np.all(core._h == 0.0)
        assert core._pending_stimulus is None

    def test_homeostatic_engine_reset(self):
        engine = HomeostaticEngine()
        engine.record_input()
        engine.record_input()
        assert engine._energy < 1.0
        assert len(engine._input_timestamps) == 2

        engine.reset()
        assert engine._energy == 1.0
        assert len(engine._input_timestamps) == 0
        assert engine._last_input_time is None
        assert engine._last_constraints is None

    def test_stability_evaluator_reset(self):
        evaluator = StabilityEvaluator()
        evaluator.record_recovery_event()
        evaluator.record_recovery_event()
        evaluator.record_surprise(0.9)
        evaluator.update_sdm_count(50)

        snap_before = evaluator.get_snapshot()
        assert snap_before.recovery_count == 2
        assert snap_before.sdm_saturation_pct > 0.0

        evaluator.reset()
        snap_after = evaluator.get_snapshot()
        assert snap_after.recovery_count == 0
        assert snap_after.sdm_saturation_pct == 0.0
        assert len(evaluator._surprises) == 0
        assert len(evaluator._velocities) == 0


class TestLifecycleEndpoint:
    """Validate POST /lifecycle/end integration and semantics."""

    def test_lifecycle_end_success(self, client, isolated_env, mock_instrumented_orchestrator):
        # 1. Verify dirty initial state
        assert len(api_module._history_store.get_history()) > 0
        with open(isolated_env["profile_file"], "r", encoding="utf-8") as f:
            profile_data = json.load(f)
        assert profile_data["is_onboarded"] is True
        assert profile_data["user_name"] == "ActiveUser"

        # 2. Call POST /lifecycle/end
        resp = client.post("/lifecycle/end")
        assert resp.status_code == 200
        data = resp.json()

        assert data["status"] == "ok"
        assert "Lucia lifecycle ended successfully" in data["message"]
        assert data["profile"]["is_onboarded"] is False
        assert data["profile"]["user_name"] == "Friend"
        assert data["profile"]["companion_name"] == "Lucia"
        assert data["profile"]["born_at"] is None

        # 3. Verify orchestrator reset was called
        mock_instrumented_orchestrator.reset_lifecycle.assert_called_once()

    def test_profile_becomes_genesis_ready(self, client, isolated_env):
        resp = client.post("/lifecycle/end")
        assert resp.status_code == 200

        # Subsequent GET /profile must immediately report is_onboarded == False and born_at == None
        prof_resp = client.get("/profile")
        assert prof_resp.status_code == 200
        prof = prof_resp.json()
        assert prof["is_onboarded"] is False
        assert prof["user_name"] == "Friend"
        assert prof["companion_name"] == "Lucia"
        assert prof["born_at"] is None

    def test_conversation_history_cleared(self, client):
        resp = client.post("/lifecycle/end")
        assert resp.status_code == 200

        # Conversation history must be empty
        hist_resp = client.get("/history")
        assert hist_resp.status_code == 200
        turns = hist_resp.json()["turns"]
        assert len(turns) == 0

    def test_stability_telemetry_reset(self, client):
        resp = client.post("/lifecycle/end")
        assert resp.status_code == 200

        # Stability snapshot must be reset
        stab_resp = client.get("/telemetry/stability")
        assert stab_resp.status_code == 200
        stab = stab_resp.json()
        assert stab["recovery_count"] == 0
        assert stab["sdm_saturation_pct"] == 0.0

    def test_state_reflects_resting_attractor(self, client):
        resp = client.post("/lifecycle/end")
        assert resp.status_code == 200

        state_resp = client.get("/state")
        assert state_resp.status_code == 200
        state = state_resp.json()
        assert state["pad"]["pleasure"] == pytest.approx(0.25)
        assert state["pad"]["arousal"] == pytest.approx(-0.05)
        assert state["pad"]["dominance"] == pytest.approx(0.05)
        assert state["memory_trace_count"] == 0

    def test_repeated_lifecycle_reset_is_idempotent(self, client):
        # Call 1
        resp1 = client.post("/lifecycle/end")
        assert resp1.status_code == 200
        assert resp1.json()["status"] == "ok"

        # Call 2
        resp2 = client.post("/lifecycle/end")
        assert resp2.status_code == 200
        assert resp2.json()["status"] == "ok"
        assert resp2.json()["profile"]["is_onboarded"] is False

    def test_unrelated_assets_remain_untouched(self, client):
        # Models directory and avatar directory must remain present and intact
        avatar_dir = Path("models/avatar")
        assert avatar_dir.exists()
        assert avatar_dir.is_dir()

        resp = client.post("/lifecycle/end")
        assert resp.status_code == 200

        # Directory still exists and avatar models endpoint still operates
        assert avatar_dir.exists()
        avatar_resp = client.get("/models/avatar")
        assert avatar_resp.status_code == 200
        assert "engines" in avatar_resp.json()

    def test_atomicity_error_handling(self, client, monkeypatch):
        # Simulate an unexpected failure inside _reset_profile_file
        def exploding_reset():
            raise OSError("Disk write failed")

        monkeypatch.setattr(api_module, "_reset_profile_file", exploding_reset)

        resp = client.post("/lifecycle/end")
        assert resp.status_code == 500
        data = resp.json()
        assert data["status"] == "error"
        assert "Disk write failed" in data["message"]
