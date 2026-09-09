"""
Unit tests for FastAPI server endpoints.

Requirements: Phase 3 (1.3–1.6, 2.1–2.5, 2.7, 3.7)
"""

from unittest.mock import MagicMock, patch

import pytest
from starlette.testclient import TestClient

import src.api.server as api_module
from src.core.models import BehavioralConstraints, PADState, SomaticMarkers
from src.core.resource_manager import get_resource_profile


@pytest.fixture
def mock_orchestrator():
    orch = MagicMock()
    orch.is_healthy.return_value = True
    orch._degraded = False
    orch._emotion_core.get_pad_state.return_value = PADState(0.25, -0.05, 0.05, 0.0)
    orch._last_somatic = None
    orch._last_constraints = None
    orch._affective_memory.get_all_traces.return_value = []
    orch._affective_memory.trace_count = 0
    orch.process.return_value = "Hello from Lucia!"
    return orch


@pytest.fixture
def client(mock_orchestrator):
    orig_mode = api_module._mode
    orig_sim = api_module._sim_runtime
    api_module._mode = "live"
    api_module._sim_runtime = None
    api_module._orchestrator = mock_orchestrator
    api_module._resource_profile = get_resource_profile("laptop")
    test_client = TestClient(api_module.app)
    yield test_client
    api_module._orchestrator = None
    api_module._resource_profile = None
    api_module._mode = orig_mode
    api_module._sim_runtime = orig_sim


class TestAPIServerProcessEndpoint:
    def test_process_valid_input_returns_response(self, client, mock_orchestrator):
        resp = client.post("/process", json={"input": "Hello Lucia!"})
        assert resp.status_code == 200
        data = resp.json()
        assert data["response"] == "Hello from Lucia!"
        assert "call_id" in data
        mock_orchestrator.process.assert_called_once_with("Hello Lucia!")

    def test_process_missing_input_returns_422(self, client):
        resp = client.post("/process", json={})
        assert resp.status_code == 422

    def test_process_empty_input_returns_422(self, client):
        resp = client.post("/process", json={"input": ""})
        assert resp.status_code == 422

    def test_process_oversized_input_returns_422(self, client):
        long_input = "a" * 4001
        resp = client.post("/process", json={"input": long_input})
        assert resp.status_code == 422

    def test_process_when_degraded_returns_503(self, client, mock_orchestrator):
        mock_orchestrator._degraded = True
        mock_orchestrator.is_healthy.return_value = False
        resp = client.post("/process", json={"input": "Hello"})
        assert resp.status_code == 503
        data = resp.json()
        assert data["error"] == "orchestrator_degraded"


class TestAPIServerStateEndpoint:
    def test_get_state_initial_defaults(self, client):
        resp = client.get("/state")
        assert resp.status_code == 200
        assert resp.headers["cache-control"] == "no-store"
        data = resp.json()
        assert data["pad"]["pleasure"] == 0.25
        assert data["pad"]["arousal"] == -0.05
        assert data["pad"]["dominance"] == 0.05
        assert data["somatic"]["stability"] == 0.0
        assert data["somatic"]["energy"] == 0.0
        assert data["memory_trace_count"] == 0

    def test_get_state_with_active_somatic_and_constraints(
        self, client, mock_orchestrator
    ):
        mock_orchestrator._last_somatic = SomaticMarkers(0.9, 0.1, 0.8, 0.2)
        mock_orchestrator._last_constraints = BehavioralConstraints(200, 0.8, 10, 2)
        mock_orchestrator._affective_memory.get_all_traces.return_value = [1, 2, 3]
        mock_orchestrator._affective_memory.trace_count = 3

        resp = client.get("/state")
        assert resp.status_code == 200
        data = resp.json()
        assert data["somatic"]["stability"] == 0.9
        assert data["somatic"]["energy"] == 0.8
        assert data["constraints"]["max_tokens"] == 200
        assert data["constraints"]["reasoning_depth"] == 2
        assert data["memory_trace_count"] == 3


class TestAPIServerHealthAndProfileEndpoints:
    def test_get_health_when_healthy(self, client):
        resp = client.get("/health")
        assert resp.status_code == 200
        assert resp.json() == {"status": "ok"}

    def test_get_health_when_degraded(self, client, mock_orchestrator):
        mock_orchestrator.is_healthy.return_value = False
        resp = client.get("/health")
        assert resp.status_code == 503
        assert resp.json() == {"status": "degraded"}

    def test_get_system_profile(self, client):
        resp = client.get("/system/profile")
        assert resp.status_code == 200
        data = resp.json()
        assert data["tier"] == "laptop"
        assert data["n_gpu_layers"] == 32
        assert data["n_ctx"] == 4096
