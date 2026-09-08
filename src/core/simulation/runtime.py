"""
SimulationRuntime — Isolated runtime container for Lucia Simulation Environment (Phase 8).

Architectural Invariants:
- INV-1 / Requirement 3: Activation safety enforced at runtime boundary. SimulationRuntime
  can NEVER activate live companion lifecycle; calling activate() raises ActivationSafetyError.
- INV-2 / Requirement 5: Zero Live Data Contamination. Uses purely in-memory stores;
  protected production files (data/chat_history.json, data/profile.json) are guarded.
- INV-4: Normal sensory pathway (Text → StimulusProcessor → Vector → Brain) preserved.
- INV-6 / Requirement 4: Virtualized, deterministic time via SimClock. Background daemons
  (EmotionCore-FastLoop, DecayEngine-SlowLoop) are NOT started; execution is synchronously
  driven by SimClock ticks.
"""

from __future__ import annotations

import logging
import time
from typing import Any, Dict, List, Optional

import numpy as np

from src.core.config import (
    BoundaryConfig,
    EmotionConfig,
    HomeostaticConfig,
    StimulusConfig,
)
from src.core.emotion.emotion_core import EmotionCore
from src.core.emotion.homeostatic_engine import HomeostaticEngine
from src.core.gating.stimulus_processor import StimulusProcessor
from src.core.memory.affective_memory import AffectiveMemory, AffectiveMemoryConfig
from src.core.memory.decay import DecayConfig, DecayEngine
from src.core.memory.sdm import SDMConfig
from src.core.models import BehavioralConstraints, PADState, SomaticMarkers
from src.core.orchestrator.prompt_assembler import PromptAssembler
from src.core.simulation.sim_clock import SimClock
from src.core.simulation.stimulus_service import StimulusService
from src.core.simulation.storage_policy import (
    ActivationSafetyError,
    InMemoryChatHistoryStore,
    InMemoryProfileStore,
    StoragePolicy,
)
from src.core.telemetry.stability_evaluator import StabilityEvaluator

logger = logging.getLogger("lucia.simulation.runtime")


class SimulationRuntime:
    """
    Isolated simulation environment executing Lucia's cognitive architecture
    without waking the live companion or touching persistent storage.
    """

    def __init__(
        self,
        sim_clock: Optional[SimClock] = None,
        fast_loop_cadence_s: float = 0.2,
        slow_loop_cadence_s: float = 900.0,
    ) -> None:
        self._state: str = "CREATED"
        self._is_live: bool = False
        self._is_simulated: bool = True

        # Virtual clock and storage isolation
        self._sim_clock = sim_clock or SimClock(
            fast_loop_cadence_s=fast_loop_cadence_s,
            slow_loop_cadence_s=slow_loop_cadence_s,
        )
        self._storage_policy = StoragePolicy(is_simulation=True)
        self._chat_store = InMemoryChatHistoryStore()
        self._profile_store = InMemoryProfileStore()

        # Cognitive modules (instantiated but background daemon loops NOT started)
        self._stimulus_processor = StimulusProcessor(StimulusConfig())
        self._emotion_core = EmotionCore(EmotionConfig(loop_cadence_ms=int(fast_loop_cadence_s * 1000)))
        self._homeostatic_engine = HomeostaticEngine(HomeostaticConfig())
        self._prompt_assembler = PromptAssembler()

        # Affective memory & decay engine (in-memory)
        sdm_cfg = SDMConfig(address_dim=256, content_dim=64, num_locations=500)
        self._affective_memory = AffectiveMemory(AffectiveMemoryConfig(sdm_config=sdm_cfg, m=64))
        decay_cfg = DecayConfig(base_decay_rate=0.0001, viability_threshold=0.05, loop_cadence_seconds=int(slow_loop_cadence_s))
        self._decay_engine = DecayEngine(self._affective_memory, decay_cfg)

        # Telemetry & Stimulus Service
        self._stability_evaluator = StabilityEvaluator(nominal_tick_ms=fast_loop_cadence_s * 1000.0)
        self._stimulus_service = StimulusService(
            emotion_core=self._emotion_core,
            stimulus_processor=self._stimulus_processor,
        )

        # Connect SimClock to cognitive execution
        self._sim_clock.register_fast_tick_callback(self._on_fast_tick)
        self._sim_clock.register_slow_tick_callback(self._on_slow_tick)

        self._state = "SIMULATING"

    # ------------------------------------------------------------------
    # Properties & Invariants
    # ------------------------------------------------------------------

    @property
    def is_live(self) -> bool:
        """Invariable: SimulationRuntime is NEVER live."""
        return False

    @property
    def is_simulated(self) -> bool:
        """Invariable: SimulationRuntime is ALWAYS simulated."""
        return True

    @property
    def state(self) -> str:
        return self._state

    @property
    def sim_clock(self) -> SimClock:
        return self._sim_clock

    @property
    def storage_policy(self) -> StoragePolicy:
        return self._storage_policy

    @property
    def stimulus_service(self) -> StimulusService:
        return self._stimulus_service

    @property
    def chat_store(self) -> InMemoryChatHistoryStore:
        return self._chat_store

    @property
    def profile_store(self) -> InMemoryProfileStore:
        return self._profile_store

    @property
    def emotion_core(self) -> EmotionCore:
        return self._emotion_core

    @property
    def homeostatic_engine(self) -> HomeostaticEngine:
        return self._homeostatic_engine

    @property
    def affective_memory(self) -> AffectiveMemory:
        return self._affective_memory

    @property
    def decay_engine(self) -> DecayEngine:
        return self._decay_engine

    @property
    def stability_evaluator(self) -> StabilityEvaluator:
        return self._stability_evaluator

    # ------------------------------------------------------------------
    # Lifecycle Safety Guards
    # ------------------------------------------------------------------

    def activate(self) -> None:
        """
        CRITICAL ARCHITECTURAL GUARD (INV-1 / Requirement 3):
        Simulation runtime must NEVER be able to invoke or mutate the live lifecycle.
        """
        raise ActivationSafetyError(
            "ActivationSafetyError: SimulationRuntime cannot activate live companion lifecycle. "
            "Live awakening is strictly forbidden in simulation environment."
        )

    def start_simulation(self) -> None:
        """Transitions runtime to SIMULATING and resumes SimClock."""
        self._state = "SIMULATING"
        self._sim_clock.resume()
        logger.info("SimulationRuntime started; state=SIMULATING")

    def pause_simulation(self) -> None:
        """Pauses SimClock."""
        self._sim_clock.pause()
        self._state = "PAUSED"
        logger.info("SimulationRuntime paused; state=PAUSED")

    def step_simulation(self, delta_ms: float) -> Dict[str, Any]:
        """Advances virtual time deterministically by delta_ms."""
        new_time, fast_ticks, slow_ticks = self._sim_clock.step(delta_ms)
        return {
            "virtual_time_s": new_time,
            "fast_ticks_executed": fast_ticks,
            "slow_ticks_executed": slow_ticks,
            "pad": self._emotion_core.get_pad_state().to_dict(),
        }

    def reset_simulation(self) -> None:
        """Resets simulation clock, emotion, stores, and homeostasis to clean baseline."""
        self._sim_clock.pause()
        self._sim_clock.reset(0.0)
        self._emotion_core.reset_to_resting()
        self._homeostatic_engine.reset()
        self._chat_store.clear_history()
        self._profile_store.reset()
        self._stimulus_service.clear_history()
        self._state = "INITIALIZED"
        logger.info("SimulationRuntime reset to clean baseline")

    def shutdown(self) -> None:
        """Clean shutdown of simulation clock and workers."""
        self._sim_clock.shutdown()
        self._state = "STOPPED"
        logger.info("SimulationRuntime shut down")

    # ------------------------------------------------------------------
    # Internal Step Callbacks
    # ------------------------------------------------------------------

    def _on_fast_tick(self, virtual_timestamp: float) -> None:
        """Called by SimClock for every due 200ms fast loop tick."""
        pad = self._emotion_core.step_once(custom_timestamp=virtual_timestamp)
        self._stability_evaluator.record_tick()

    def _on_slow_tick(self, elapsed_seconds: float) -> None:
        """Called by SimClock for every due slow loop decay tick."""
        purged = self._decay_engine.apply_decay_tick(elapsed_seconds)
        logger.debug("Sim slow tick executed: purged %d traces over %.1fs", purged, elapsed_seconds)

    def inject_sensory_text(self, text: str, source: str = "simulation_ui") -> Dict[str, Any]:
        """Convenience method to inject text stimulus via normal sensory pathway."""
        return self._stimulus_service.inject_text(
            text,
            source=source,
            custom_timestamp=self._sim_clock.virtual_time_s,
        )

    def inject_vector_probe(self, vector: List[float] | np.ndarray, source: str = "debug_probe") -> Dict[str, Any]:
        """Convenience method to inject 16D vector directly via developer probe."""
        return self._stimulus_service.inject_vector(
            vector,
            source=source,
            custom_timestamp=self._sim_clock.virtual_time_s,
        )

    # ------------------------------------------------------------------
    # Simulated Conversational Turn
    # ------------------------------------------------------------------

    def send_chat(self, user_text: str, source: str = "sim_user") -> Dict[str, Any]:
        """
        Executes an isolated conversational turn:
        1. Encodes text via StimulusProcessor.
        2. Pushes 16D vector to EmotionCore.
        3. Computes somatic markers & behavioral constraints.
        4. Simulates assistant reply based on emotional state.
        5. Records turns in InMemoryChatHistoryStore (zero disk writes).
        """
        # Guard live data
        self._storage_policy.assert_write_permitted()

        # Step 1 & 2: Normal sensory pathway injection
        stimulus_entry = self._stimulus_service.inject_text(
            user_text,
            source=source,
            custom_timestamp=self._sim_clock.virtual_time_s,
        )

        pad = self._emotion_core.get_pad_state()
        self._homeostatic_engine.record_input()
        markers = self._homeostatic_engine.compute_somatic_markers(pad)
        constraints = self._homeostatic_engine.compute_behavioral_constraints(markers, pad)

        # Append user turn to in-memory store
        self._chat_store.append_turn(
            role="user",
            content=user_text,
            metadata={"source": source, "virtual_time": self._sim_clock.virtual_time_s},
        )

        # Formulate simulated companion response reflecting PAD and constraints
        # (Does not make LLM GPU calls or self-report emotion)
        if pad.pleasure > 0.3 and pad.arousal > 0.2:
            reply = "I understand completely! Let's explore that together."
        elif pad.pleasure < -0.2:
            reply = "I'm listening closely. Tell me more about what's going on."
        elif constraints.latency_ms > 1000:
            reply = "...I am processing this carefully. Let's take our time."
        else:
            reply = "I hear you. I'm right here."

        # Append assistant turn to in-memory store
        self._chat_store.append_turn(
            role="assistant",
            content=reply,
            metadata={
                "pad": pad.to_dict(),
                "constraints": {
                    "temperature": constraints.temperature,
                    "max_tokens": constraints.max_tokens,
                    "latency_ms": constraints.latency_ms,
                },
                "virtual_time": self._sim_clock.virtual_time_s,
            },
        )

        return {
            "user_text": user_text,
            "assistant_reply": reply,
            "pad": pad.to_dict(),
            "markers": {
                "stability": round(float(markers.stability), 4),
                "cognitive_load": round(float(markers.cognitive_load), 4),
                "energy": round(float(markers.energy), 4),
                "tension": round(float(markers.tension), 4),
            },
            "constraints": {
                "temperature": constraints.temperature,
                "max_tokens": constraints.max_tokens,
                "latency_ms": constraints.latency_ms,
                "reasoning_depth": constraints.reasoning_depth,
            },
            "stimulus": stimulus_entry,
            "history_length": len(self._chat_store.get_history(100)),
        }

    # ------------------------------------------------------------------
    # State Snapshot Inspection
    # ------------------------------------------------------------------

    def get_state_snapshot(self) -> Dict[str, Any]:
        """
        Comprehensive state snapshot for UI inspection and telemetry.
        """
        pad = self._emotion_core.get_pad_state()
        stability = self._stability_evaluator.get_snapshot()
        markers = self._homeostatic_engine.compute_somatic_markers(pad)
        constraints = self._homeostatic_engine.compute_behavioral_constraints(markers, pad)

        return {
            "runtime": {
                "mode": "simulation",
                "state": self._state,
                "is_live": False,
                "is_simulated": True,
            },
            "clock": {
                "virtual_time_s": round(self._sim_clock.virtual_time_s, 3),
                "is_paused": self._sim_clock.is_paused,
                "speed_factor": self._sim_clock.speed_factor,
            },
            "pad": pad.to_dict(),
            "somatic_markers": {
                "stability": round(float(markers.stability), 4),
                "cognitive_load": round(float(markers.cognitive_load), 4),
                "energy": round(float(markers.energy), 4),
                "tension": round(float(markers.tension), 4),
            },
            "somatic": {
                "stability": round(float(markers.stability), 4),
                "cognitive_load": round(float(markers.cognitive_load), 4),
                "energy": round(float(markers.energy), 4),
                "tension": round(float(markers.tension), 4),
            },
            "behavioral_constraints": {
                "temperature": round(float(constraints.temperature), 3),
                "max_tokens": constraints.max_tokens,
                "latency_ms": constraints.latency_ms,
                "reasoning_depth": constraints.reasoning_depth,
            },
            "constraints": {
                "temperature": round(float(constraints.temperature), 3),
                "max_tokens": constraints.max_tokens,
                "latency_ms": constraints.latency_ms,
                "reasoning_depth": constraints.reasoning_depth,
            },
            "stability": stability.to_dict(),
            "memory": {
                "trace_count": self._affective_memory.trace_count,
            },
            "storage": {
                "storage_type": "InMemoryIsolated",
                "chat_turns_count": len(self._chat_store.get_history(1000)),
                "is_onboarded": self._profile_store.get_profile().get("is_onboarded", False),
                "protected_writes_blocked": True,
            },
        }

    get_snapshot = get_state_snapshot
