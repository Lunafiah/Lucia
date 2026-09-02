"""
Integration tests for InferencePipelineOrchestrator online learning pipeline.

Requirements: Phase 4 (7.1–7.6, 8.4)
"""

import time
from unittest.mock import MagicMock, patch

import pytest

from src.core.inference.orchestrator import (
    InferenceOrchestratorConfig,
    InferencePipelineOrchestrator,
)


class TestInferenceIntegration:
    def test_multi_turn_experience_accumulation_and_weight_adaptation(self, tmp_path):
        model_file = tmp_path / "model.gguf"
        model_file.write_bytes(b"dummy")

        config = InferenceOrchestratorConfig(
            model_path=str(model_file),
            loop_cadence_ms=100,
            decay_loop_cadence_seconds=60,
            sdm_num_locations=100,
            sdm_address_dim=64,
            sdm_content_dim=16,
            sdm_capacity=50,
            ai_kl_weight=0.01,
            ai_learning_rate=0.05,
            lnn_batch_size=4,
            lnn_learning_rate=1e-2,
            lnn_t_span=0.05,
        )

        with patch("src.core.orchestrator.orchestrator.LLMBackend") as mock_backend_cls:
            mock_backend = MagicMock()
            mock_backend.is_ready.return_value = True
            mock_backend.generate.return_value = "Hello my dear friend!"
            mock_backend_cls.return_value = mock_backend

            orch = InferencePipelineOrchestrator(config)

            # Record initial LNN weights
            w_f_init = orch._emotion_core.W_f.copy()

            # Execute 6 turns to trigger online batch update (batch_size=4)
            for i in range(6):
                resp = orch.process(f"Turn {i}: How are you feeling today?")
                assert resp == "Hello my dear friend!"
                time.sleep(0.06)

            # Wait up to 3 seconds for background trainer to execute step
            t0 = time.monotonic()
            while orch.lnn_trainer.training_step_count() < 1 and time.monotonic() - t0 < 3.0:
                time.sleep(0.05)

            assert orch.lnn_trainer.training_step_count() >= 1

            # Verify that LNN weights have neuroplastically adapted
            w_f_updated = orch._emotion_core.W_f
            assert not (w_f_init == w_f_updated).all()

            orch.shutdown()
