"""Unit tests for Phase 6 endpoints: stability telemetry and history store."""
import pytest
from starlette.testclient import TestClient
import src.api.server as api_module
from src.core.models import PADState
from unittest.mock import MagicMock


@pytest.fixture
def mock_orch():
    orch = MagicMock()
    orch.is_healthy.return_value = True
    orch._degraded = False
    orch._emotion_core.get_pad_state.return_value = PADState(0.25, -0.05, 0.05, 0.0)
    orch._last_somatic = None
    orch._last_constraints = None
    orch._affective_memory.get_all_traces.return_value = []
    orch._affective_memory.trace_count = 5
    orch.process.return_value = "Hello my friend!"
    return orch


@pytest.fixture
def client(mock_orch, tmp_path):
    orig_mode = api_module._mode
    orig_sim = api_module._sim_runtime
    orig_active = api_module._is_live_companion_active
    api_module._mode = "live"
    api_module._sim_runtime = None
    api_module._is_live_companion_active = True
    api_module._orchestrator = mock_orch
    # Point history store to tmp_path
    orig_history_path = api_module._history_store.file_path
    api_module._history_store.file_path = tmp_path / "chat_history.json"
    api_module._history_store._ensure_file_exists()

    test_client = TestClient(api_module.app)
    yield test_client
    api_module._orchestrator = None
    api_module._history_store.file_path = orig_history_path
    api_module._is_live_companion_active = orig_active
    api_module._mode = orig_mode
    api_module._sim_runtime = orig_sim


class TestPhase6Endpoints:
    def test_stability_telemetry_endpoint(self, client):
        resp = client.get("/telemetry/stability")
        assert resp.status_code == 200
        data = resp.json()
        assert "lsi" in data
        assert "status" in data
        assert "fast_loop_jitter_mean_ms" in data
        assert "ode_velocity_variance" in data
        assert "sdm_saturation_pct" in data
        assert 0.0 <= data["lsi"] <= 1.0

    def test_history_lifecycle(self, client):
        # 1. Start with empty / initial history
        resp = client.get("/history")
        assert resp.status_code == 200
        turns = resp.json()["turns"]

        # 2. Process turn
        process_resp = client.post("/process", json={"input": "Hello Lucia!"})
        assert process_resp.status_code == 200

        # 3. History should have user turn and companion turn
        resp2 = client.get("/history")
        turns2 = resp2.json()["turns"]
        assert len(turns2) >= 2
        assert turns2[-2]["content"] == "Hello Lucia!"
        assert turns2[-1]["content"] == "Hello my friend!"

        # 4. Export markdown
        export_resp = client.get("/history/export")
        assert export_resp.status_code == 200
        assert "# Lucia — Conversation History Log" in export_resp.text
        assert "Hello Lucia!" in export_resp.text

        # 5. Clear history
        del_resp = client.delete("/history")
        assert del_resp.status_code == 200
        resp3 = client.get("/history")
        assert len(resp3.json()["turns"]) == 0
