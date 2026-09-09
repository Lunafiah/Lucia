"""
Unit tests for CognitiveOrchestrator — Phase 9 Unified Cognitive Architecture.

Requirements: Phase 9 (ADR-014, ADR-016, ADR-018, ADR-020, PHASE_9_ARCHITECTURE_GATE.md § 19).
"""

import threading
import time
from unittest.mock import MagicMock, patch

import numpy as np
import pytest

from src.core.config import MemoryOrchestratorConfig
from src.core.models import BehavioralConstraints, PADState, SomaticMarkers
from src.core.orchestrator.cognitive_orchestrator import (
    CognitiveOrchestrator,
    build_cognitive_orchestrator,
)
from src.core.orchestrator.policies import (
    CognitiveTurnResult,
    GenerationPolicy,
    PlasticityPolicy,
    SurpriseModulationPolicy,
)


@pytest.fixture
def test_config(tmp_path):
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
def mock_orchestrator(test_config):
    with patch("src.core.orchestrator.cognitive_orchestrator.LLMBackend") as mock_llm_cls:
        mock_llm = MagicMock()
        mock_llm.is_ready.return_value = True
        mock_llm.generate.return_value = "I am listening with quiet attention."
        mock_llm_cls.return_value = mock_llm

        orch = build_cognitive_orchestrator(test_config)
        yield orch
        orch.shutdown()


class TestCognitiveOrchestratorPipeline:
    def test_single_turn_executes_10_stages_and_returns_frozen_result(self, mock_orchestrator):
        result = mock_orchestrator.process("Hello Lucia, it's good to see you.")

        assert isinstance(result, CognitiveTurnResult)
        assert result.response_text == "I am listening with quiet attention."
        assert len(result.call_id) > 0
        assert result.stimulus.shape[0] == 16
        assert isinstance(result.prediction_error, float)
        assert result.prediction_error >= 0.0
        assert isinstance(result.pad_initial, PADState)
        assert isinstance(result.pad_final, PADState)
        assert isinstance(result.somatic, SomaticMarkers)
        assert isinstance(result.constraints, BehavioralConstraints)
        assert isinstance(result.generation_policy, GenerationPolicy)
        assert result.execution_time_s >= 0.0

        # Verify atomic latest_result pointer
        assert mock_orchestrator.latest_result is result

    def test_singular_stimulus_integration_invariant(self, mock_orchestrator):
        """
        Acceptance Invariant 1:
        A single turn must push stimulus to EmotionCore exactly ONCE and
        record input in HomeostaticEngine exactly ONCE.
        """
        spy_push = MagicMock(wraps=mock_orchestrator._emotion_core.push_stimulus)
        spy_record = MagicMock(wraps=mock_orchestrator._homeostatic_engine.record_input)
        mock_orchestrator._emotion_core.push_stimulus = spy_push
        mock_orchestrator._homeostatic_engine.record_input = spy_record

        mock_orchestrator.process("Testing single stimulus injection.")

        assert spy_push.call_count == 1
        assert spy_record.call_count == 1

    def test_causal_active_inference_flow(self, mock_orchestrator):
        """
        Acceptance Invariant 2:
        High prediction surprise modulates somatic markers and triggers
        deliberative mode when above threshold.
        """
        # Provide non-zero baseline PAD state so active inference prior is evaluated
        mock_orchestrator._emotion_core.get_pad_state = MagicMock(
            return_value=PADState.resting(0.25, -0.05, 0.05)
        )
        # Force a large prediction error by making active inference predict far from limbic state
        mock_orchestrator._active_inference._b = np.array([5.0, 5.0, 5.0])

        result = mock_orchestrator.process("Shocking revelation!")
        assert result.prediction_error > 0.60
        # Deliberative policy should have been selected
        assert result.generation_policy.mode == "deliberative"
        assert result.constraints.reasoning_depth == 2

    def test_turn_serialization_under_concurrent_callers(self, mock_orchestrator):
        """
        Acceptance Invariant 3:
        Multiple threads calling process() must be serialized through _turn_lock.
        No interleaved history, no deadlocks.
        """
        results = []
        errors = []

        def worker(msg_idx: int):
            try:
                res = mock_orchestrator.process(f"Message from thread {msg_idx}")
                results.append(res)
            except Exception as e:
                errors.append(e)

        threads = [threading.Thread(target=worker, args=(i,)) for i in range(5)]
        for t in threads:
            t.start()
        for t in threads:
            t.join(timeout=5.0)

        assert len(errors) == 0
        assert len(results) == 5
        # Verify history contains exactly 5 user turns and 5 assistant turns in order
        history = mock_orchestrator._history
        assert len(history) == 10
        user_roles = [role for role, _ in history if role == "user"]
        assert len(user_roles) == 5

    def test_invalid_input_guard(self, mock_orchestrator):
        """Empty input or input > 4000 chars returns fallback immediately."""
        res_empty = mock_orchestrator.process("")
        assert res_empty.response_text == mock_orchestrator._fallback_response
        assert res_empty.trace_stored is False

        res_oversized = mock_orchestrator.process("x" * 4001)
        assert res_oversized.response_text == mock_orchestrator._fallback_response
        assert res_oversized.trace_stored is False

    def test_pipeline_exception_triggers_degraded_state(self, mock_orchestrator):
        """Uncaught exception in pipeline must transition orchestrator to degraded state."""
        with patch.object(mock_orchestrator._stimulus_processor, "encode", side_effect=RuntimeError("Gating crash")):
            res = mock_orchestrator.process("Crash me")
            assert res.response_text == mock_orchestrator._fallback_response
            assert mock_orchestrator._degraded is True
            assert mock_orchestrator.is_healthy() is False

        # Subsequent calls in degraded state return fallback immediately
        res2 = mock_orchestrator.process("Hello after crash")
        assert res2.response_text == mock_orchestrator._fallback_response

    def test_lifecycle_reset(self, mock_orchestrator):
        """Reset clears dialogue history, resets baseline, and clears memory."""
        mock_orchestrator.process("Turn 1")
        assert len(mock_orchestrator._history) == 2
        assert mock_orchestrator.latest_result is not None
        assert mock_orchestrator._affective_memory.trace_count >= 1

        mock_orchestrator.reset_lifecycle()

        assert len(mock_orchestrator._history) == 0
        assert mock_orchestrator.latest_result is None
        assert mock_orchestrator._affective_memory.trace_count == 0
        assert mock_orchestrator._degraded is False

        pad = mock_orchestrator._emotion_core.get_pad_state()
        assert pad.pleasure == pytest.approx(0.25)
        assert pad.arousal == pytest.approx(-0.05)
        assert pad.dominance == pytest.approx(0.05)
