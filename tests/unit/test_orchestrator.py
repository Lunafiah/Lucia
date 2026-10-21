"""
Unit tests for Orchestrator.
LLMBackend is always mocked — no real model required.
Requirements: 8.1–8.10, 10.1, 10.6, 10.7
"""

from __future__ import annotations

import time
from concurrent.futures import ThreadPoolExecutor
from typing import Optional
from unittest.mock import MagicMock, patch

import pytest

from src.core.config import OrchestratorConfig
from src.core.models import BehavioralConstraints, SomaticMarkers


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

_FAKE_MODEL = "fake_model.gguf"


def _make_config(tmp_path, fallback: str = "[fallback]") -> OrchestratorConfig:
    """Create a config pointing to a temporary fake model file."""
    model_file = tmp_path / "model.gguf"
    model_file.write_bytes(b"fake")
    return OrchestratorConfig(
        model_path=str(model_file),
        n_gpu_layers=0,
        loop_cadence_ms=100,
        fallback_response=fallback,
        llm_timeout_seconds=5.0,
    )


def _make_orchestrator(tmp_path, llm_response: Optional[str] = "Hello!"):
    """
    Build an Orchestrator with a mocked LLMBackend.
    llm_response=None simulates LLM failure.
    """
    from src.core.orchestrator.orchestrator import Orchestrator
    from src.core.language.llm_backend import LLMBackend

    cfg = _make_config(tmp_path)

    with patch.object(LLMBackend, "__init__", lambda self, config: None):
        orch = Orchestrator.__new__(Orchestrator)
        # Manually wire up like __init__ would, bypassing LLMBackend init
        from src.core.config import HomeostaticConfig, BoundaryConfig
        from src.core.emotion.emotion_core import EmotionCore
        from src.core.emotion.homeostatic_engine import HomeostaticEngine
        from src.core.gating.stimulus_processor import StimulusProcessor
        from src.core.orchestrator.prompt_assembler import PromptAssembler
        from src.core.safety.boundary_layer import BoundaryLayer

        orch._config = cfg
        orch._degraded = False
        orch._history = []
        orch._stimulus_processor = StimulusProcessor(cfg.to_stimulus_config())
        orch._emotion_core = EmotionCore(cfg.to_emotion_config())
        orch._homeostatic_engine = HomeostaticEngine(HomeostaticConfig())
        orch._prompt_assembler = PromptAssembler()
        orch._boundary_layer = BoundaryLayer(cfg.to_boundary_config())

        # Mock LLMBackend
        mock_llm = MagicMock(spec=LLMBackend)
        mock_llm.is_ready.return_value = True
        mock_llm.generate.return_value = llm_response
        orch._llm_backend = mock_llm

        # Start Fast_Loop and wait
        orch._emotion_core.start()
        orch._wait_for_fast_loop()

    return orch


# ---------------------------------------------------------------------------
# Config validation (Req 10.6, 10.7)
# ---------------------------------------------------------------------------

class TestConfigValidation:
    def test_missing_model_path_raises_value_error(self):
        with pytest.raises(ValueError, match="model_path"):
            OrchestratorConfig(model_path="")

    def test_loop_cadence_too_low_raises_value_error(self):
        with pytest.raises(ValueError, match="loop_cadence_ms"):
            OrchestratorConfig(model_path="x.gguf", loop_cadence_ms=50)

    def test_loop_cadence_too_high_raises_value_error(self):
        with pytest.raises(ValueError, match="loop_cadence_ms"):
            OrchestratorConfig(model_path="x.gguf", loop_cadence_ms=600)

    def test_hidden_dim_zero_raises_value_error(self):
        with pytest.raises(ValueError, match="hidden_dim"):
            OrchestratorConfig(model_path="x.gguf", hidden_dim=0)

    def test_ode_step_size_zero_raises_value_error(self):
        with pytest.raises(ValueError, match="ode_step_size"):
            OrchestratorConfig(model_path="x.gguf", ode_step_size=0.0)

    def test_llm_timeout_below_1_raises_value_error(self):
        with pytest.raises(ValueError, match="llm_timeout_seconds"):
            OrchestratorConfig(model_path="x.gguf", llm_timeout_seconds=0.5)

    def test_valid_config_succeeds(self, tmp_path):
        cfg = _make_config(tmp_path)
        assert cfg.model_path.endswith("model.gguf")


# ---------------------------------------------------------------------------
# Input validation (Req 8.10)
# ---------------------------------------------------------------------------

class TestInputValidation:
    def test_empty_string_returns_fallback_immediately(self, tmp_path):
        orch = _make_orchestrator(tmp_path)
        result = orch.process("")
        assert result == orch._config.fallback_response
        # No pipeline steps — LLM should not have been called
        orch._llm_backend.generate.assert_not_called()
        orch.shutdown()

    def test_4001_chars_returns_fallback_immediately(self, tmp_path):
        orch = _make_orchestrator(tmp_path)
        long_input = "a" * 4001
        result = orch.process(long_input)
        assert result == orch._config.fallback_response
        orch._llm_backend.generate.assert_not_called()
        orch.shutdown()

    def test_4000_chars_accepted(self, tmp_path):
        orch = _make_orchestrator(tmp_path, llm_response="OK")
        valid_input = "a" * 4000
        result = orch.process(valid_input)
        assert result == "OK"
        orch.shutdown()

    def test_1_char_accepted(self, tmp_path):
        orch = _make_orchestrator(tmp_path, llm_response="OK")
        result = orch.process("a")
        assert result == "OK"
        orch.shutdown()


# ---------------------------------------------------------------------------
# Degraded state (Req 8.7)
# ---------------------------------------------------------------------------

class TestDegradedState:
    def test_exception_in_pipeline_sets_degraded(self, tmp_path):
        orch = _make_orchestrator(tmp_path)
        # Make LLM raise to trigger degraded state
        orch._llm_backend.generate.side_effect = RuntimeError("model crash")

        result = orch.process("hello")
        assert result == orch._config.fallback_response
        assert orch._degraded is True
        orch.shutdown()

    def test_subsequent_calls_return_fallback_in_degraded_state(self, tmp_path):
        orch = _make_orchestrator(tmp_path)
        orch._llm_backend.generate.side_effect = RuntimeError("crash")

        orch.process("trigger crash")
        assert orch._degraded is True
        first_call_count = orch._llm_backend.generate.call_count  # 1 call that crashed

        # Reset mock — second call should NOT reach LLM because degraded guard fires
        orch._llm_backend.generate.side_effect = None
        orch._llm_backend.generate.return_value = "Should not reach"

        result = orch.process("second call")
        assert result == orch._config.fallback_response, "Degraded state should return fallback"
        # call_count unchanged — second call never reached LLM
        assert orch._llm_backend.generate.call_count == first_call_count
        orch.shutdown()

    def test_emotion_core_keeps_running_after_degraded(self, tmp_path):
        orch = _make_orchestrator(tmp_path)
        orch._llm_backend.generate.side_effect = RuntimeError("crash")
        orch.process("hello")
        assert orch._degraded is True
        # Fast_Loop should still be alive
        assert orch._emotion_core.is_alive()
        orch.shutdown()

    def test_is_healthy_false_after_degraded(self, tmp_path):
        orch = _make_orchestrator(tmp_path)
        orch._llm_backend.generate.side_effect = RuntimeError("crash")
        orch.process("hello")
        assert orch.is_healthy() is False
        orch.shutdown()


# ---------------------------------------------------------------------------
# Successful pipeline (Req 8.2)
# ---------------------------------------------------------------------------

class TestPipeline:
    def test_process_returns_llm_response(self, tmp_path):
        orch = _make_orchestrator(tmp_path, llm_response="Hello from Lucia.")
        result = orch.process("How are you?")
        assert result == "Hello from Lucia."
        orch.shutdown()

    def test_process_appends_to_history(self, tmp_path):
        orch = _make_orchestrator(tmp_path, llm_response="Response A")
        orch.process("Turn 1")
        assert len(orch._history) == 2  # user + assistant
        assert orch._history[0] == ("user", "Turn 1")
        assert orch._history[1] == ("assistant", "Response A")
        orch.shutdown()

    def test_history_trimmed_to_max_turns(self, tmp_path):
        cfg = _make_config(tmp_path)
        cfg_dict = {k: v for k, v in cfg.__dict__.items()}
        cfg_with_small_history = OrchestratorConfig(
            **{k: v for k, v in cfg.__dict__.items()
               if k in OrchestratorConfig.__dataclass_fields__}
        )
        orch = _make_orchestrator(tmp_path, llm_response="ok")
        orch._config = OrchestratorConfig(
            model_path=cfg.model_path,
            max_history_turns=3,
            loop_cadence_ms=100,
            fallback_response="[fallback]",
        )
        for i in range(10):
            orch.process(f"message {i}")
        # max 3 * 2 = 6 history entries
        assert len(orch._history) <= 6
        orch.shutdown()

    def test_llm_none_returns_fallback(self, tmp_path):
        orch = _make_orchestrator(tmp_path, llm_response=None)
        result = orch.process("hello")
        assert result == orch._config.fallback_response
        orch.shutdown()

    def test_boundary_layer_applied_to_response(self, tmp_path):
        """LLM returns a pattern-matching phrase → Boundary_Layer replaces it."""
        orch = _make_orchestrator(tmp_path, llm_response="I am an AI language model.")
        result = orch.process("How are you?")
        assert "I am an AI" not in result
        orch.shutdown()

    def test_is_healthy_true_when_running(self, tmp_path):
        orch = _make_orchestrator(tmp_path)
        assert orch.is_healthy() is True
        orch.shutdown()


# ---------------------------------------------------------------------------
# Shutdown (Req 8.6)
# ---------------------------------------------------------------------------

class TestShutdown:
    def test_shutdown_joins_fast_loop_thread(self, tmp_path):
        orch = _make_orchestrator(tmp_path)
        thread = orch._emotion_core._thread
        assert thread is not None and thread.is_alive()
        orch.shutdown()
        thread.join(timeout=3.0)
        assert not thread.is_alive() or orch._emotion_core._stop_event.is_set()

    def test_shutdown_calls_llm_backend_shutdown(self, tmp_path):
        orch = _make_orchestrator(tmp_path)
        orch.shutdown()
        orch._llm_backend.shutdown.assert_called_once()

    def test_is_healthy_false_after_shutdown(self, tmp_path):
        orch = _make_orchestrator(tmp_path)
        orch._llm_backend.is_ready.return_value = False  # simulate post-shutdown
        orch.shutdown()
        assert orch.is_healthy() is False


# ---------------------------------------------------------------------------
# Startup — Fast_Loop ready check (Req 8.4, 8.5)
# ---------------------------------------------------------------------------

class TestStartup:
    def test_fast_loop_running_after_init(self, tmp_path):
        orch = _make_orchestrator(tmp_path)
        assert orch._emotion_core.is_alive()
        assert orch._emotion_core.tick_count() >= 1
        orch.shutdown()

    def test_fast_loop_not_ready_raises_runtime_error(self, tmp_path):
        """If Fast_Loop never ticks, __init__ should raise RuntimeError."""
        from src.core.orchestrator.orchestrator import Orchestrator
        from src.core.language.llm_backend import LLMBackend

        cfg = _make_config(tmp_path)

        with patch.object(LLMBackend, "__init__", lambda self, config: None):
            orch = Orchestrator.__new__(Orchestrator)
            from src.core.config import HomeostaticConfig
            from src.core.emotion.emotion_core import EmotionCore
            from src.core.emotion.homeostatic_engine import HomeostaticEngine
            from src.core.gating.stimulus_processor import StimulusProcessor
            from src.core.orchestrator.prompt_assembler import PromptAssembler
            from src.core.safety.boundary_layer import BoundaryLayer

            orch._config = cfg
            orch._degraded = False
            orch._history = []
            orch._stimulus_processor = StimulusProcessor(cfg.to_stimulus_config())

            # Create a mock EmotionCore that never becomes alive
            mock_core = MagicMock(spec=EmotionCore)
            mock_core.is_alive.return_value = False
            mock_core.tick_count.return_value = 0
            mock_core.start.return_value = None
            orch._emotion_core = mock_core
            orch._homeostatic_engine = HomeostaticEngine(HomeostaticConfig())
            orch._prompt_assembler = PromptAssembler()
            orch._boundary_layer = BoundaryLayer(cfg.to_boundary_config())
            mock_llm = MagicMock(spec=LLMBackend)
            mock_llm.is_ready.return_value = True
            orch._llm_backend = mock_llm

            from src.core.orchestrator.orchestrator import _STARTUP_TIMEOUT_S
            import src.core.orchestrator.orchestrator as mod
            original_timeout = mod._STARTUP_TIMEOUT_S

            # Temporarily reduce timeout for speed
            mod._STARTUP_TIMEOUT_S = 0.2
            try:
                with pytest.raises(RuntimeError, match="Fast_Loop"):
                    orch._wait_for_fast_loop()
            finally:
                mod._STARTUP_TIMEOUT_S = original_timeout
