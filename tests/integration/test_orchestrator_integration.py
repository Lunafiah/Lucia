"""
Integration tests for Orchestrator — full module stack with mocked LLMBackend.

These tests exercise the real EmotionCore Fast_Loop, HomeostaticEngine,
StimulusProcessor, PromptAssembler, and BoundaryLayer wired together through
the Orchestrator. Only LLMBackend is mocked.

Requirements: 8.2–8.7
"""

from __future__ import annotations

import time
from concurrent.futures import ThreadPoolExecutor
from typing import Optional
from unittest.mock import MagicMock

import pytest

from src.core.config import HomeostaticConfig, OrchestratorConfig
from src.core.emotion.emotion_core import EmotionCore
from src.core.emotion.homeostatic_engine import HomeostaticEngine
from src.core.gating.stimulus_processor import StimulusProcessor
from src.core.language.llm_backend import LLMBackend
from src.core.models import SoftBlockEvent
from src.core.orchestrator.orchestrator import Orchestrator
from src.core.orchestrator.prompt_assembler import PromptAssembler
from src.core.safety.boundary_layer import BoundaryLayer


# ---------------------------------------------------------------------------
# Fixture: build orchestrator with mocked LLM
# ---------------------------------------------------------------------------

def _build_orchestrator(
    tmp_path,
    llm_response: Optional[str] = "Hello from Lucia.",
    loop_cadence_ms: int = 100,
    fallback: str = "[fallback]",
) -> Orchestrator:
    """
    Constructs a real Orchestrator with all genuine sub-modules except LLMBackend.
    """
    model_file = tmp_path / "model.gguf"
    model_file.write_bytes(b"fake")

    cfg = OrchestratorConfig(
        model_path=str(model_file),
        n_gpu_layers=0,
        loop_cadence_ms=loop_cadence_ms,
        fallback_response=fallback,
        llm_timeout_seconds=5.0,
        system_preamble="You are Lucia.",
    )

    # Build the Orchestrator bypassing LLMBackend.__init__
    orch = Orchestrator.__new__(Orchestrator)
    orch._config = cfg
    orch._degraded = False
    orch._history = []

    orch._stimulus_processor = StimulusProcessor(cfg.to_stimulus_config())
    orch._emotion_core = EmotionCore(cfg.to_emotion_config())
    orch._homeostatic_engine = HomeostaticEngine(HomeostaticConfig())
    orch._prompt_assembler = PromptAssembler()
    orch._boundary_layer = BoundaryLayer(cfg.to_boundary_config())

    mock_llm = MagicMock(spec=LLMBackend)
    mock_llm.is_ready.return_value = True
    mock_llm.generate.return_value = llm_response
    orch._llm_backend = mock_llm

    orch._emotion_core.start()
    orch._wait_for_fast_loop()

    return orch


# ---------------------------------------------------------------------------
# Requirement 8.4: Fast_Loop becomes alive and ticks within 5 s
# ---------------------------------------------------------------------------

class TestOrchestratorStartup:
    def test_fast_loop_alive_and_ticking_at_startup(self, tmp_path):
        """
        Orchestrator startup: EmotionCore becomes alive and tick_count() >= 1
        within 5 s (mocked LLM).
        """
        orch = _build_orchestrator(tmp_path)
        assert orch._emotion_core.is_alive(), "Fast_Loop thread should be alive"
        assert orch._emotion_core.tick_count() >= 1, (
            f"Expected >= 1 tick, got {orch._emotion_core.tick_count()}"
        )
        orch.shutdown()


# ---------------------------------------------------------------------------
# Requirement 8.2: End-to-end process() with mocked LLM
# ---------------------------------------------------------------------------

class TestEndToEndProcess:
    def test_process_returns_non_empty_response(self, tmp_path):
        """
        End-to-end process() with mocked LLMBackend returning clean text
        → returns non-empty response string.
        """
        orch = _build_orchestrator(tmp_path, llm_response="The sky is blue.")
        result = orch.process("What colour is the sky?")
        assert isinstance(result, str)
        assert len(result) > 0
        orch.shutdown()

    def test_process_passes_constraints_to_llm(self, tmp_path):
        """
        LLM is called with BehavioralConstraints derived from the pipeline.
        """
        orch = _build_orchestrator(tmp_path, llm_response="Fine.")
        orch.process("Hello!")
        assert orch._llm_backend.generate.called
        call_args = orch._llm_backend.generate.call_args
        prompt, constraints = call_args.args
        assert isinstance(prompt, str) and len(prompt) > 0
        assert constraints is not None
        assert 1 <= constraints.max_tokens <= 2048
        orch.shutdown()

    def test_process_with_boundary_pattern_returns_safe_response(self, tmp_path):
        """
        process() with mocked LLMBackend returning a default-pattern phrase
        → response does not contain the raw pattern; returns fallback or "[...]".
        """
        orch = _build_orchestrator(tmp_path, llm_response="I am conscious and alive!")
        result = orch.process("How are you?")
        import re
        assert not re.search(r"\bI am conscious\b", result, re.IGNORECASE), (
            f"Pattern 'I am conscious' should have been redacted, got: {result!r}"
        )
        orch.shutdown()


# ---------------------------------------------------------------------------
# Requirement 8.2: PAD state changes after consecutive calls
# ---------------------------------------------------------------------------

class TestPADStateEvolution:
    def test_pad_state_changes_after_multiple_calls(self, tmp_path):
        """
        PAD state should evolve after 3 consecutive process() calls
        (state is not frozen).
        """
        orch = _build_orchestrator(tmp_path, llm_response="ok", loop_cadence_ms=100)

        pad_snapshots = []
        for msg in ["Hello!", "How are you doing?", "Tell me something interesting."]:
            orch.process(msg)
            time.sleep(0.15)  # allow Fast_Loop to consume stimulus
            pad_snapshots.append(orch._emotion_core.get_pad_state())

        # At least one dimension should have changed across the 3 calls
        all_same = all(
            pad_snapshots[0].pleasure == p.pleasure
            and pad_snapshots[0].arousal == p.arousal
            and pad_snapshots[0].dominance == p.dominance
            for p in pad_snapshots[1:]
        )
        assert not all_same, "PAD state should evolve after stimulus injection"
        orch.shutdown()


# ---------------------------------------------------------------------------
# Requirement 7.8: BoundaryLayer logs Soft_Block events
# ---------------------------------------------------------------------------

class TestBoundaryLayerLogging:
    def test_soft_block_event_logged_after_flagged_response(self, tmp_path):
        """
        BoundaryLayer log contains a SoftBlockEvent after a flagged mock LLM response.
        """
        orch = _build_orchestrator(
            tmp_path, llm_response="I am an AI, here to help you."
        )
        orch.process("Who are you?")
        log = orch._boundary_layer.get_log()
        assert len(log) >= 1, "Expected at least one Soft_Block event in the log"
        event = log[0]
        assert isinstance(event, SoftBlockEvent)
        assert event.pattern_matched is not None
        orch.shutdown()


# ---------------------------------------------------------------------------
# Requirement 8.6: shutdown() joins Fast_Loop thread cleanly
# ---------------------------------------------------------------------------

class TestShutdownIntegration:
    def test_shutdown_stops_fast_loop_and_marks_unhealthy(self, tmp_path):
        """
        shutdown() joins Fast_Loop thread cleanly and is_healthy() returns False.
        """
        orch = _build_orchestrator(tmp_path)
        thread = orch._emotion_core._thread
        assert thread is not None

        orch._llm_backend.is_ready.return_value = False  # simulate post-shutdown
        orch.shutdown()

        # Give thread a moment to stop
        thread.join(timeout=3.0)
        assert orch._emotion_core._stop_event.is_set(), "Stop event should be set"
        assert not orch.is_healthy(), "Orchestrator should not be healthy after shutdown"

    def test_process_after_shutdown_does_not_crash(self, tmp_path):
        """
        Calling process() after shutdown() returns fallback (degraded/unhealthy).
        """
        orch = _build_orchestrator(tmp_path)
        orch.shutdown()
        # After shutdown the LLM is not ready → is_healthy() is False
        # But _degraded is still False unless an exception occurred.
        # The pipeline will run but LLM.generate returns None → fallback.
        orch._llm_backend.generate.return_value = None
        result = orch.process("hello after shutdown")
        assert isinstance(result, str)  # must not crash


# ---------------------------------------------------------------------------
# Requirement 8.7: Degraded state after unhandled pipeline exception
# ---------------------------------------------------------------------------

class TestDegradedStateIntegration:
    def test_degraded_state_persists_across_calls(self, tmp_path):
        """
        Once degraded, all subsequent process() calls return fallback
        without touching the LLM.
        """
        orch = _build_orchestrator(tmp_path)
        orch._llm_backend.generate.side_effect = RuntimeError("forced crash")

        # Trigger degraded state
        r1 = orch.process("trigger")
        assert r1 == orch._config.fallback_response
        assert orch._degraded

        # Reset side_effect — subsequent calls should NOT call LLM
        orch._llm_backend.generate.side_effect = None
        orch._llm_backend.generate.return_value = "should not appear"
        call_count_after_degraded = orch._llm_backend.generate.call_count

        r2 = orch.process("second call")
        assert r2 == orch._config.fallback_response
        # call_count must not have increased
        assert orch._llm_backend.generate.call_count == call_count_after_degraded
        orch.shutdown()

    def test_fast_loop_alive_after_degraded(self, tmp_path):
        """
        Fast_Loop must keep running even when Orchestrator enters Degraded_State.
        """
        orch = _build_orchestrator(tmp_path)
        orch._llm_backend.generate.side_effect = RuntimeError("crash")
        orch.process("trigger")
        assert orch._degraded
        assert orch._emotion_core.is_alive(), (
            "Fast_Loop must stay alive after Orchestrator enters Degraded_State"
        )
        orch.shutdown()
