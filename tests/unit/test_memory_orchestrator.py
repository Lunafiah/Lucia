"""
Unit tests for MemoryAugmentedOrchestrator.

Requirements: 11.1–11.8, 13.1–13.8, 14.1–14.5
"""

import time
from unittest.mock import MagicMock, patch

import pytest

from src.core.config import MemoryOrchestratorConfig
from src.core.orchestrator.orchestrator import MemoryAugmentedOrchestrator


@pytest.fixture
def memory_config(tmp_path):
    # Dummy file path for model
    model_file = tmp_path / "model.gguf"
    model_file.write_bytes(b"dummy")
    return MemoryOrchestratorConfig(
        model_path=str(model_file),
        loop_cadence_ms=100,
        decay_loop_cadence_seconds=60,
        sdm_num_locations=100,
        sdm_address_dim=64,
        sdm_content_dim=16,
        sdm_capacity=50,
    )


@pytest.fixture
def orchestrator(memory_config):
    with patch("src.core.orchestrator.orchestrator.LLMBackend") as mock_llm_cls:
        mock_llm = MagicMock()
        mock_llm.is_ready.return_value = True
        mock_llm.generate.return_value = "Mock response from Lucia."
        mock_llm_cls.return_value = mock_llm

        orch = MemoryAugmentedOrchestrator(memory_config)
        yield orch
        orch.shutdown()


class TestMemoryOrchestratorConfig:
    def test_missing_model_path_raises_value_error(self):
        with pytest.raises(ValueError, match="model_path"):
            MemoryOrchestratorConfig(model_path="")

    def test_sdm_num_locations_below_100_raises(self):
        with pytest.raises(ValueError, match="sdm_num_locations"):
            MemoryOrchestratorConfig(model_path="test.gguf", sdm_num_locations=99)

    def test_sdm_content_dim_below_8_raises(self):
        with pytest.raises(ValueError, match="sdm_content_dim"):
            MemoryOrchestratorConfig(model_path="test.gguf", sdm_content_dim=7)

    def test_decay_cadence_below_60_raises(self):
        with pytest.raises(ValueError, match="decay_loop_cadence_seconds"):
            MemoryOrchestratorConfig(
                model_path="test.gguf", decay_loop_cadence_seconds=59
            )

    def test_invalid_orchestrator_config_type_raises(self):
        with pytest.raises(ValueError):
            MemoryAugmentedOrchestrator("invalid")


class TestMemoryAugmentedOrchestratorPipeline:
    def test_process_stores_trace_in_memory(self, orchestrator):
        traces_before = orchestrator._affective_memory.get_all_traces()
        assert len(traces_before) == 0

        resp = orchestrator.process("Hello Lucia!")
        assert resp == "Mock response from Lucia."

        traces_after = orchestrator._affective_memory.get_all_traces()
        assert len(traces_after) == 1

    def test_ecphory_exception_falls_back_gracefully(self, orchestrator):
        with patch.object(
            orchestrator._ecphory_engine,
            "query",
            side_effect=RuntimeError("Ecphory failed"),
        ):
            resp = orchestrator.process("Testing ecphory failure.")
            assert resp == "Mock response from Lucia."
            assert not orchestrator._degraded

    def test_store_exception_does_not_break_response(self, orchestrator):
        with patch.object(
            orchestrator._affective_memory,
            "store",
            side_effect=RuntimeError("Store failed"),
        ):
            resp = orchestrator.process("Testing store failure.")
            assert resp == "Mock response from Lucia."
            assert not orchestrator._degraded

    def test_shutdown_stops_decay_engine(self, orchestrator):
        assert orchestrator._decay_engine.is_alive()
        orchestrator.shutdown()
        assert not orchestrator._decay_engine.is_alive()
        assert not orchestrator.is_healthy()
