"""
Orchestrator — central pipeline coordinator for Lucia Core Phase 1.

Public interface:
    process(input_text: str) -> str   # sole entry point for callers
    shutdown() -> None                # clean teardown
    is_healthy() -> bool              # False when degraded or shut down

Pipeline (8 steps, Requirement 8.2):
    1. Encode input via StimulusProcessor
    2. Push stimulus to EmotionCore
    3. Read PAD state; record input; compute SomaticMarkers
    4. Derive BehavioralConstraints
    5. Assemble Conditioned_Prompt
    6. Apply latency_ms delay (capped at 5000 ms)
    7. Call LLM_Backend
    8. Apply BoundaryLayer; return safe response

Error handling:
    - Input out of range (empty or > 4000 chars): return fallback immediately,
      no pipeline steps executed (Requirement 8.10).
    - Any unhandled exception in steps 1–8: log with traceback, enter
      Degraded_State, return fallback (Requirement 8.7).
    - In Degraded_State: all process() calls return fallback immediately.

Requirements: 8.1–8.10, 9.1, 9.4–9.6, 10.1–10.8
"""

from __future__ import annotations

import logging
import time
import uuid
from typing import List, Optional, Tuple

from src.core.config import (
    BoundaryConfig,
    EmotionConfig,
    HomeostaticConfig,
    LLMConfig,
    OrchestratorConfig,
    StimulusConfig,
)
from src.core.emotion.emotion_core import EmotionCore
from src.core.emotion.homeostatic_engine import HomeostaticEngine
from src.core.errors import AssemblyError
from src.core.gating.stimulus_processor import StimulusProcessor
from src.core.language.llm_backend import LLMBackend
from src.core.models import BehavioralConstraints, SomaticMarkers
from src.core.orchestrator.prompt_assembler import PromptAssembler
from src.core.safety.boundary_layer import BoundaryLayer

logger = logging.getLogger(__name__)

# Maximum input length accepted by process() (Requirement 8.1)
_MAX_INPUT_LEN = 4000

# Maximum sleep imposed by latency_ms (Requirement 8.3)
_MAX_LATENCY_MS = 5000

# Timeout waiting for Fast_Loop to become ready (Requirement 8.4)
_STARTUP_TIMEOUT_S = 5.0


class Orchestrator:
    """
    Coordinates the full stimulus-to-response pipeline.

    All module instances are created here and owned for their full lifetime.
    """

    def __init__(self, config: OrchestratorConfig) -> None:
        # OrchestratorConfig.__post_init__ already validates; calling here
        # re-raises if config was mutated after construction.
        self._config = config
        self._degraded = False
        self._history: List[Tuple[str, str]] = []

        # --- Instantiate sub-modules ---
        self._stimulus_processor = StimulusProcessor(config.to_stimulus_config())
        self._emotion_core = EmotionCore(config.to_emotion_config())
        self._homeostatic_engine = HomeostaticEngine(HomeostaticConfig())
        self._prompt_assembler = PromptAssembler()
        self._boundary_layer = BoundaryLayer(config.to_boundary_config())

        # LLMBackend raises FileNotFoundError / RuntimeError if model is unusable
        self._llm_backend = LLMBackend(config.to_llm_config())

        # --- Start Fast_Loop and wait for first tick (Requirement 8.4) ---
        self._emotion_core.start()
        self._wait_for_fast_loop()

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def process(self, input_text: str) -> str:
        """
        Process a user input through the full pipeline and return a response.

        Returns the configured fallback string immediately for:
          - empty or oversized input (Requirement 8.10)
          - Degraded_State (Requirement 8.7)

        Enters Degraded_State on any unhandled exception (Requirement 8.7).
        """
        # --- Input guard (Requirement 8.10) ---
        if len(input_text) == 0 or len(input_text) > _MAX_INPUT_LEN:
            return self._config.fallback_response

        # --- Degraded state guard (Requirement 8.7) ---
        if self._degraded:
            return self._config.fallback_response

        call_id = uuid.uuid4().hex
        t_start = time.monotonic()

        try:
            return self._execute_pipeline(input_text, call_id, t_start)
        except Exception:
            logger.exception(
                "Orchestrator: unhandled exception in pipeline (call_id=%s)", call_id
            )
            self._degraded = True
            return self._config.fallback_response

    def shutdown(self) -> None:
        """
        Stop the Fast_Loop, join it (2-second timeout), release LLM model.
        (Requirement 8.6)
        """
        self._emotion_core.stop()
        if self._emotion_core._thread is not None:
            self._emotion_core._thread.join(timeout=2.0)
        self._llm_backend.shutdown()
        logger.info("Orchestrator: shut down.")

    def is_healthy(self) -> bool:
        """Return False when in Degraded_State or after shutdown()."""
        return not self._degraded and self._llm_backend.is_ready()

    # ------------------------------------------------------------------
    # Private: pipeline execution
    # ------------------------------------------------------------------

    def _execute_pipeline(
        self, input_text: str, call_id: str, t_start: float
    ) -> str:
        """
        8-step pipeline. Any exception propagates to process() which handles it.
        Steps are executed in strict order (Requirement 8.2).
        """
        # Step 1: encode stimulus
        stimulus = self._stimulus_processor.encode(input_text)

        # Step 2: push stimulus to EmotionCore (does not block Fast_Loop)
        self._emotion_core.push_stimulus(stimulus)

        # Step 3: read PAD, record input, compute somatic markers
        pad = self._emotion_core.get_pad_state()
        self._homeostatic_engine.record_input()
        markers: SomaticMarkers = self._homeostatic_engine.compute_somatic_markers(pad)

        # Step 4: derive behavioral constraints
        constraints: BehavioralConstraints = (
            self._homeostatic_engine.compute_behavioral_constraints(markers, pad)
        )

        # Step 5: assemble conditioned prompt
        prompt_or_err = self._prompt_assembler.assemble(
            somatic=markers,
            constraints=constraints,
            history=self._history,
            system_preamble=self._config.system_preamble,
            n_ctx=self._config.n_ctx,
        )
        if isinstance(prompt_or_err, AssemblyError):
            logger.warning(
                "Orchestrator: prompt assembly failed (call_id=%s): %s",
                call_id, prompt_or_err
            )
            return self._config.fallback_response

        prompt: str = prompt_or_err

        # Step 6: apply latency delay (capped, Requirement 8.3)
        delay_ms = min(constraints.latency_ms, _MAX_LATENCY_MS)
        if delay_ms > 0:
            time.sleep(delay_ms / 1000.0)

        # Step 7: call LLM_Backend (Requirement 9.5, 9.6 — pass constraints unmodified)
        raw_response = self._llm_backend.generate(prompt, constraints)
        if raw_response is None:
            logger.warning(
                "Orchestrator: LLM returned None (call_id=%s)", call_id
            )
            return self._config.fallback_response

        # Step 8: apply BoundaryLayer
        safe_response = self._boundary_layer.validate(raw_response)

        # If the entire response was suppressed to "[...]", return fallback
        if safe_response.strip() == "[...]":
            safe_response = self._config.fallback_response

        # Append to conversation history
        self._history.append(("user", input_text))
        self._history.append(("assistant", safe_response))

        # Trim history to configured max turns (keep most recent N pairs)
        max_turns = self._config.max_history_turns * 2  # pairs
        if len(self._history) > max_turns:
            self._history = self._history[-max_turns:]

        # Log call metadata (Requirement 8.8)
        logger.info(
            "Orchestrator call_id=%s t=%.3fs markers=%s constraints=%s",
            call_id,
            time.monotonic() - t_start,
            markers,
            constraints,
        )

        return safe_response

    # ------------------------------------------------------------------
    # Private: startup validation
    # ------------------------------------------------------------------

    def _wait_for_fast_loop(self) -> None:
        """
        Poll until the Fast_Loop thread is alive and has completed >= 1 tick,
        or raise RuntimeError after _STARTUP_TIMEOUT_S seconds (Requirement 8.4, 8.5).
        """
        deadline = time.monotonic() + _STARTUP_TIMEOUT_S
        while time.monotonic() < deadline:
            if self._emotion_core.is_alive() and self._emotion_core.tick_count() >= 1:
                logger.info(
                    "Orchestrator: Fast_Loop ready (ticks=%d)", self._emotion_core.tick_count()
                )
                return
            time.sleep(0.05)
        raise RuntimeError(
            f"Orchestrator: EmotionCore Fast_Loop did not become ready within "
            f"{_STARTUP_TIMEOUT_S:.0f} seconds."
        )
