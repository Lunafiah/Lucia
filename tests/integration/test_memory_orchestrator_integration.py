"""
Integration tests for MemoryAugmentedOrchestrator.

Requirements: 11.1–11.8, 12.1–12.5, 13.1–13.8, 14.1–14.5
"""

from unittest.mock import MagicMock, patch

import pytest

from src.core.config import MemoryOrchestratorConfig
from src.core.orchestrator.orchestrator import MemoryAugmentedOrchestrator


@pytest.fixture
def memory_orchestrator(tmp_path):
    model_file = tmp_path / "test_model.gguf"
    model_file.write_bytes(b"dummy")

    config = MemoryOrchestratorConfig(
        model_path=str(model_file),
        loop_cadence_ms=100,
        decay_loop_cadence_seconds=60,
        sdm_num_locations=100,
        sdm_address_dim=64,
        sdm_content_dim=16,
        sdm_capacity=100,
    )

    with patch("src.core.orchestrator.orchestrator.LLMBackend") as mock_llm_cls:
        mock_llm = MagicMock()
        mock_llm.is_ready.return_value = True
        mock_llm.generate.return_value = "I acknowledge your message."
        mock_llm_cls.return_value = mock_llm

        orch = MemoryAugmentedOrchestrator(config)
        yield orch
        orch.shutdown()


class TestMemoryOrchestratorIntegration:
    def test_multi_turn_memory_accumulation(self, memory_orchestrator):
        # Turn 1
        resp1 = memory_orchestrator.process("The weather is stormy today.")
        assert resp1 == "I acknowledge your message."
        traces_1 = memory_orchestrator._affective_memory.get_all_traces()
        assert len(traces_1) == 1

        # Turn 2
        resp2 = memory_orchestrator.process("The storm is getting worse.")
        assert resp2 == "I acknowledge your message."
        traces_2 = memory_orchestrator._affective_memory.get_all_traces()
        assert len(traces_2) == 2

        # Turn 3
        resp3 = memory_orchestrator.process("Finally the sun is shining.")
        assert resp3 == "I acknowledge your message."
        traces_3 = memory_orchestrator._affective_memory.get_all_traces()
        assert len(traces_3) == 3

    def test_boundary_layer_suppresses_recall_patterns_in_pipeline(
        self, tmp_path
    ):
        model_file = tmp_path / "test_model.gguf"
        model_file.write_bytes(b"dummy")

        config = MemoryOrchestratorConfig(
            model_path=str(model_file),
            loop_cadence_ms=100,
            decay_loop_cadence_seconds=60,
            sdm_num_locations=100,
            sdm_address_dim=64,
            sdm_content_dim=16,
            sdm_capacity=100,
        )

        with patch("src.core.orchestrator.orchestrator.LLMBackend") as mock_llm_cls:
            mock_llm = MagicMock()
            mock_llm.is_ready.return_value = True
            mock_llm.generate.return_value = (
                "I recall that you mentioned the blue sky yesterday."
            )
            mock_llm_cls.return_value = mock_llm

            orch = MemoryAugmentedOrchestrator(config)
            resp = orch.process("What color was the sky?")

            assert "I recall" not in resp
            assert "you mentioned" not in resp
            assert "[...]" in resp
            orch.shutdown()

    def test_clean_shutdown_joins_all_loops(self, memory_orchestrator):
        assert memory_orchestrator._emotion_core.is_alive()
        assert memory_orchestrator._decay_engine.is_alive()

        memory_orchestrator.shutdown()

        assert not memory_orchestrator._emotion_core.is_alive()
        assert not memory_orchestrator._decay_engine.is_alive()
        assert not memory_orchestrator.is_healthy()
