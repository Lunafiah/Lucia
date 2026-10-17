"""
Integration tests for FastAPI server with in-memory InstrumentedOrchestrator.

Requirements: Phase 3 (1.1–1.7, 2.1–2.6, 3.7)
"""

import threading
import time
from unittest.mock import MagicMock, patch

import pytest
from starlette.testclient import TestClient

import src.api.server as api_module
from src.core.config import MemoryOrchestratorConfig
from src.core.orchestrator.cognitive_orchestrator import (
    CognitiveOrchestrator,
    build_cognitive_orchestrator,
)


@pytest.fixture
def integrated_server(tmp_path):
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

    with patch("src.core.orchestrator.cognitive_orchestrator.LLMBackend") as mock_llm_cls:
        mock_llm = MagicMock()
        mock_llm.is_ready.return_value = True
        mock_llm.generate.return_value = "I hear you clearly, my friend."
        mock_llm_cls.return_value = mock_llm

        orch = build_cognitive_orchestrator(config)
        api_module._orchestrator = orch
        # Phase 8: force live mode so /process and /lifecycle endpoints are not blocked.
        # test_simulation_api uses scope=module and leaves _mode/_sim_runtime set globally.
        original_mode = api_module._mode
        original_sim_runtime = api_module._sim_runtime
        original_active = api_module._is_live_companion_active
        original_history_path = api_module._history_store.file_path
        api_module._history_store.file_path = tmp_path / "chat_history.json"
        api_module._history_store._ensure_file_exists()
        api_module._mode = "live"
        api_module._sim_runtime = None
        api_module._is_live_companion_active = True
        client = TestClient(api_module.app)

        yield client, orch

        orch.shutdown()
        api_module._orchestrator = None
        api_module._history_store.file_path = original_history_path
        api_module._is_live_companion_active = original_active
        api_module._mode = original_mode
        api_module._sim_runtime = original_sim_runtime


class TestAPIServerIntegration:
    def test_end_to_end_process_and_state_evolution(self, integrated_server):
        client, orch = integrated_server

        # Healthcheck — Phase 8 adds 'mode' and 'healthy' fields; check only 'status'.
        health_resp = client.get("/health")
        assert health_resp.status_code == 200
        assert health_resp.json()["status"] == "ok"

        # Initial state before turn
        state_0 = client.get("/state").json()
        assert state_0["memory_trace_count"] == 0

        # Execute turn
        turn_resp = client.post("/process", json={"input": "Hello Lucia!"})
        assert turn_resp.status_code == 200
        data = turn_resp.json()
        assert data["response"] == "I hear you clearly, my friend."
        assert "call_id" in data

        # State after turn
        state_1 = client.get("/state").json()
        assert state_1["memory_trace_count"] == 1
        assert state_1["somatic"]["energy"] > 0.0

    def test_concurrent_state_polling_during_process(self, integrated_server):
        client, orch = integrated_server

        results = {"state_polled": False, "process_done": False}

        def poll_state_worker():
            for _ in range(5):
                resp = client.get("/state")
                assert resp.status_code == 200
                time.sleep(0.02)
            results["state_polled"] = True

        poll_thread = threading.Thread(target=poll_state_worker)
        poll_thread.start()

        # Send chat message concurrently
        proc_resp = client.post(
            "/process", json={"input": "Concurrent test message"}
        )
        assert proc_resp.status_code == 200
        results["process_done"] = True

        poll_thread.join(timeout=2.0)
        assert results["state_polled"]
        assert results["process_done"]

    @pytest.mark.anyio
    async def test_turn_serialization_and_http_429_admission_control(self, integrated_server):
        """
        Acceptance Invariant 3:
        When 5 requests hit POST /process simultaneously, request 1 executes,
        request 2 queues, and requests 3-5 receive HTTP 429.
        """
        import asyncio
        import httpx
        from httpx import ASGITransport

        client, orch = integrated_server

        # Simulate slower LLM generation so queue builds up
        orig_generate = orch._llm_backend.generate

        def slow_generate(*args, **kwargs):
            time.sleep(0.2)
            return "Deliberated reply."

        orch._llm_backend.generate = slow_generate

        try:
            transport = ASGITransport(app=api_module.app)
            async with httpx.AsyncClient(transport=transport, base_url="http://test") as ac:
                tasks = [
                    ac.post("/process", json={"input": f"Simultaneous request {i}"})
                    for i in range(5)
                ]
                responses = await asyncio.gather(*tasks)
                status_codes = [r.status_code for r in responses]
        finally:
            orch._llm_backend.generate = orig_generate

        assert len(status_codes) == 5
        # Exactly 2 requests admitted (1 active + 1 queued) -> 200 OK
        assert status_codes.count(200) == 2
        # Remaining 3 requests rejected -> 429 Too Many Requests
        assert status_codes.count(429) == 3
