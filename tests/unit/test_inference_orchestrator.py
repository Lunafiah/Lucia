"""
Unit tests for InferencePipelineOrchestrator.

Requirements: Phase 4 (7.1–7.6, 8.4)
"""

from unittest.mock import MagicMock, patch

import pytest

from src.core.inference.orchestrator import (
    InferenceOrchestratorConfig,
    InferencePipelineOrchestrator,
)


@pytest.fixture
def base_config(tmp_path):
    model_file = tmp_path / "model.gguf"
    model_file.write_bytes(b"dummy")

    return InferenceOrchestratorConfig(
        model_path=str(model_file),
        loop_cadence_ms=100,
        decay_loop_cadence_seconds=60,
        sdm_num_locations=100,
        sdm_address_dim=64,
        sdm_content_dim=16,
        sdm_capacity=50,
        ai_kl_weight=0.01,
        ai_learning_rate=1e-3,
        lnn_batch_size=4,
        lnn_learning_rate=1e-4,
    )


@pytest.fixture
def mock_llm_orchestrator(base_config):
    with patch("src.core.orchestrator.orchestrator.LLMBackend") as mock_backend_cls:
        mock_backend = MagicMock()
        mock_backend.is_ready.return_value = True
        mock_backend.generate.return_value = "Response from Lucia"
        mock_backend_cls.return_value = mock_backend

        orch = InferencePipelineOrchestrator(base_config)
        yield orch, mock_backend
        orch.shutdown()


class TestInferencePipelineOrchestrator:
    def test_invalid_config_raises_value_error(self, tmp_path):
        model_file = tmp_path / "model.gguf"
        model_file.write_bytes(b"dummy")

        with pytest.raises(ValueError, match="ai_kl_weight"):
            InferenceOrchestratorConfig(
                model_path=str(model_file), ai_kl_weight=1.5
            )

        with pytest.raises(ValueError, match="lnn_batch_size"):
            InferenceOrchestratorConfig(
                model_path=str(model_file), lnn_batch_size=3
            )

    def test_process_runs_full_10_step_pipeline(self, mock_llm_orchestrator):
        orch, mock_llm = mock_llm_orchestrator

        assert orch.is_healthy()
        assert orch.lnn_trainer.is_training_active()

        resp = orch.process("Hello Lucia!")
        assert resp == "Response from Lucia"
        assert orch.last_pred_error >= 0.0
        assert len(orch._history) == 2

    def test_disabled_lnn_training_when_batch_size_zero(self, tmp_path):
        model_file = tmp_path / "model.gguf"
        model_file.write_bytes(b"dummy")

        cfg = InferenceOrchestratorConfig(
            model_path=str(model_file),
            lnn_batch_size=0,
            loop_cadence_ms=100,
            decay_loop_cadence_seconds=60,
        )

        with patch("src.core.orchestrator.orchestrator.LLMBackend") as mock_backend_cls:
            mock_backend = MagicMock()
            mock_backend.is_ready.return_value = True
            mock_backend.generate.return_value = "Response"
            mock_backend_cls.return_value = mock_backend

            orch = InferencePipelineOrchestrator(cfg)
            assert not orch.lnn_trainer.is_training_active()

            resp = orch.process("Test message")
            assert resp == "Response"
            orch.shutdown()

    def test_step_4c_failure_isolated_from_pipeline(self, mock_llm_orchestrator):
        orch, mock_llm = mock_llm_orchestrator

        # Inject exception into active inference step
        with patch.object(
            orch._active_inference, "step", side_effect=RuntimeError("AI failed")
        ):
            resp = orch.process("Resilient turn")
            assert resp == "Response from Lucia"
            assert not orch._degraded

    def test_shutdown_stops_all_loops(self, base_config):
        with patch("src.core.orchestrator.orchestrator.LLMBackend") as mock_backend_cls:
            mock_backend = MagicMock()
            mock_backend.is_ready.return_value = True
            mock_backend_cls.return_value = mock_backend

            orch = InferencePipelineOrchestrator(base_config)
            assert orch._emotion_core.is_alive()
            assert orch._decay_engine.is_alive()
            assert orch._lnn_trainer.is_training_active()

            orch.shutdown()

            assert not orch._emotion_core.is_alive()
            assert not orch._decay_engine.is_alive()
            assert not orch._lnn_trainer.is_training_active()
