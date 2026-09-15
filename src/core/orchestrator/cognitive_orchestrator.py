"""
CognitiveOrchestrator — Phase 9 Unified Cognitive Architecture.

Replaces the 5-tier inheritance hierarchy (Orchestrator →
MemoryAugmentedOrchestrator → InstrumentedOrchestrator) with a single,
flat, composition-based coordinator.

Public interface:
    process(input_text: str) -> CognitiveTurnResult   # sole entry point
    shutdown()                                         # clean teardown
    is_healthy() -> bool                               # health probe
    reset_lifecycle()                                  # restart dialogue state
    latest_result: Optional[CognitiveTurnResult]      # most recent turn (read-only)

10-Stage Pipeline (ADR-014, PHASE_9_ARCHITECTURE_GATE.md § 7):
    S1  — Sensory encoding via StimulusProcessor
    S2  — Generative prior expectation via ActiveInferenceEngine
    S3  — Limbic integration via EmotionCore (push_stimulus)
    S4  — Prediction surprise computation & belief update
    S5  — Homeostatic modulation with surprise coupling
    S6  — Affective ecphory (subconscious echo vector)
    S7  — Prompt assembly & LLM generation & BoundaryLayer
    S8  — Affective memory consolidation (surprise-weighted)
    S9  — Plasticity tagging (online salience → LNNTrainer)
    S10 — Frozen CognitiveTurnResult construction & emission

Concurrency (ADR-018):
    _turn_lock (non-reentrant threading.Lock) — serialises all callers.
    Callers at the HTTP layer add asyncio.Lock() + HTTP 429 admission.
    Background daemons (FastLoop, DecayEngine, LNNTrainer) run freely.

Requirements: Phase 9 — Cognitive Unification
"""

from __future__ import annotations

import logging
import threading
import time
import uuid
from typing import List, Optional, Tuple

import numpy as np

from src.core.communication.communication_policy import CommunicationPolicy
from src.core.communication.communication_state import CommIntent, CommunicationState
from src.core.communication.semantic_consistency_guard import (
    SemanticConsistencyGuard as CommSemanticGuard,
)
from src.core.config import (
    BoundaryConfig,
    HomeostaticConfig,
    MemoryOrchestratorConfig,
    OrchestratorConfig,
    StimulusConfig,
)
from src.core.emotion.emotion_core import EmotionCore
from src.core.emotion.homeostatic_engine import HomeostaticEngine
from src.core.errors import AssemblyError
from src.core.expression.expression_policy import ExpressionPolicy
from src.core.expression.expression_state import ExpressionState
from src.core.expression.semantic_consistency_guard import (
    SemanticConsistencyGuard as ExprSemanticGuard,
)
from src.core.gating.stimulus_processor import StimulusProcessor
from src.core.inference.active_inference import ActiveInferenceConfig, ActiveInferenceEngine
from src.core.inference.lnn_trainer import LNNTrainer, LNNTrainerConfig
from src.core.knowledge.proposition import Proposition
from src.core.knowledge.store import KnowledgeStore
from src.core.language.llm_backend import LLMBackend
from src.core.memory.affective_memory import AffectiveMemory
from src.core.memory.decay import DecayEngine
from src.core.memory.ecphory import EcphoryEngine, RecollectionResult
from src.core.models import BehavioralConstraints, PADState, SomaticMarkers
from src.core.orchestrator.policies import (
    CognitiveTurnResult,
    GenerationPolicy,
    PlasticityPolicy,
    SurpriseModulationPolicy,
)
from src.core.orchestrator.prompt_assembler import PromptAssembler
from src.core.relationship.signals import RelationshipSignal, RelationshipSignalType
from src.core.relationship.state import RelationshipState
from src.core.relationship.updater import RelationshipUpdater
from src.core.safety.boundary_layer import BoundaryLayer

logger = logging.getLogger(__name__)

# Maximum input length accepted by process()
_MAX_INPUT_LEN = 4000

# Maximum artificial latency delay (ms) — same cap as legacy orchestrators
_MAX_LATENCY_MS = 5000

# Fast-Loop startup timeout (seconds)
_STARTUP_TIMEOUT_S = 5.0


class CognitiveOrchestrator:
    """
    Composition-based coordinator for the unified Lucia cognitive turn.

    All subsystem instances are injected at construction.  No private state is
    duplicated here: the Orchestrator owns the turn lifecycle, NOT the cognitive
    state (ADR-020).

    Thread-safety:
        process() acquires _turn_lock before executing any pipeline stage.
        _turn_lock is a non-reentrant threading.Lock — recursive calls deadlock
        by design (prevents nested stimulus injection / history corruption).
    """

    def __init__(
        self,
        *,
        # --- Layer 1 ---
        stimulus_processor: StimulusProcessor,
        # --- Layer 2 ---
        emotion_core: EmotionCore,
        # --- Layer 3 ---
        homeostatic_engine: HomeostaticEngine,
        # --- Layer 4 ---
        active_inference: ActiveInferenceEngine,
        # --- Layer 5 ---
        affective_memory: AffectiveMemory,
        ecphory_engine: EcphoryEngine,
        decay_engine: Optional[DecayEngine] = None,
        # --- Layer 6 ---
        prompt_assembler: PromptAssembler,
        llm_backend: LLMBackend,
        boundary_layer: BoundaryLayer,
        # --- Plasticity ---
        lnn_trainer: Optional[LNNTrainer] = None,
        # --- Policy objects ---
        surprise_policy: Optional[SurpriseModulationPolicy] = None,
        plasticity_policy: Optional[PlasticityPolicy] = None,
        # --- Phase 16 Subsystems (Optional) ---
        knowledge_store: Optional[KnowledgeStore] = None,
        relationship_updater: Optional[RelationshipUpdater] = None,
        comm_policy: Optional[CommunicationPolicy] = None,
        expression_policy: Optional[ExpressionPolicy] = None,
        # --- Configuration knobs ---
        system_preamble: str = "",
        n_ctx: int = 2048,
        max_history_turns: int = 20,
        fallback_response: str = "...",
    ) -> None:
        # Subsystems
        self._stimulus_processor = stimulus_processor
        self._emotion_core = emotion_core
        self._homeostatic_engine = homeostatic_engine
        self._active_inference = active_inference
        self._affective_memory = affective_memory
        self._ecphory_engine = ecphory_engine
        self._decay_engine = decay_engine
        self._prompt_assembler = prompt_assembler
        self._llm_backend = llm_backend
        self._boundary_layer = boundary_layer
        self._lnn_trainer = lnn_trainer

        # Phase 16 Promoted Subsystems
        self._knowledge_store = knowledge_store if knowledge_store is not None else KnowledgeStore()
        self._relationship_updater = (
            relationship_updater if relationship_updater is not None else RelationshipUpdater()
        )
        self._comm_policy = (
            comm_policy if comm_policy is not None else CommunicationPolicy(smoothing_factor=0.25)
        )
        self._expression_policy = (
            expression_policy if expression_policy is not None else ExpressionPolicy(smoothing_factor=0.25)
        )
        self._comm_semantic_guard = CommSemanticGuard()
        self._expr_semantic_guard = ExprSemanticGuard()
        self._latest_comm_state: Optional[CommunicationState] = None
        self._latest_expr_state: Optional[ExpressionState] = None

        # Policy defaults
        self._surprise_policy = surprise_policy or SurpriseModulationPolicy()
        self._plasticity_policy = plasticity_policy or PlasticityPolicy()

        # Configuration
        self._system_preamble = system_preamble
        self._n_ctx = n_ctx
        self._max_history_turns = max_history_turns
        self._fallback_response = fallback_response

        # Mutable orchestrator state (only these — no subsystem state copies)
        self._history: List[Tuple[str, str]] = []
        self._degraded: bool = False
        self._shutdown: bool = False

        # Non-reentrant turn serialization lock (Tier 3, ADR-018)
        self._turn_lock = threading.Lock()

        # Latest turn result — written atomically after each turn; read by /state
        self._latest_result: Optional[CognitiveTurnResult] = None

        # --- Start background daemons ---
        self._emotion_core.start()
        self._wait_for_fast_loop()

        if self._decay_engine is not None:
            self._decay_engine.start()

        if self._lnn_trainer is not None:
            self._lnn_trainer.start()

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    @property
    def latest_result(self) -> Optional[CognitiveTurnResult]:
        """Most recent completed turn result (thread-safe atomic read)."""
        return self._latest_result

    @property
    def knowledge_store(self) -> KnowledgeStore:
        return self._knowledge_store

    @property
    def relationship_updater(self) -> RelationshipUpdater:
        return self._relationship_updater

    @property
    def latest_communication(self) -> Optional[CommunicationState]:
        return self._latest_comm_state

    @property
    def latest_expression(self) -> Optional[ExpressionState]:
        return self._latest_expr_state

    def process(self, input_text: str) -> CognitiveTurnResult:
        """
        Execute a full 10-stage cognitive turn and return an immutable result.

        Returns the fallback result immediately for:
          - empty or oversized input
          - Degraded_State (any previous unhandled exception)

        Acquires _turn_lock before any pipeline execution; all concurrent
        callers block until the lock is released.
        """
        # --- Input guard ---
        if len(input_text) == 0 or len(input_text) > _MAX_INPUT_LEN:
            return self._make_fallback_result(
                input_text, "empty_or_oversized_input", 0.0
            )

        # --- Degraded guard ---
        if self._degraded:
            return self._make_fallback_result(
                input_text, "degraded_state", 0.0
            )

        call_id = uuid.uuid4().hex
        t_start = time.perf_counter()

        # Tier 3: non-reentrant turn serialization
        acquired = self._turn_lock.acquire(blocking=True)
        try:
            result = self._execute_pipeline(input_text, call_id, t_start)
        except Exception:
            logger.exception(
                "CognitiveOrchestrator: unhandled exception (call_id=%s)", call_id
            )
            self._degraded = True
            result = self._make_fallback_result(
                input_text, "pipeline_exception", max(0.0001, time.perf_counter() - t_start)
            )
        finally:
            if acquired:
                self._turn_lock.release()

        # Atomic pointer update — readable by /state without locks
        self._latest_result = result
        return result

    def shutdown(self) -> None:
        """Stop all background daemons and release the LLM model."""
        self._shutdown = True
        self._emotion_core.stop()
        if self._emotion_core._thread is not None:
            self._emotion_core._thread.join(timeout=2.0)
        if self._decay_engine is not None:
            self._decay_engine.stop()
        if self._lnn_trainer is not None:
            self._lnn_trainer.stop()
        self._llm_backend.shutdown()
        logger.info("CognitiveOrchestrator: shut down.")

    def is_healthy(self) -> bool:
        """Return False when in Degraded_State, shut down, or LLM unready."""
        return (
            not self._degraded
            and not self._shutdown
            and self._llm_backend.is_ready()
        )

    def reset_lifecycle(self) -> None:
        """
        Reset dialogue context, metabolic state, emotional baseline, and
        affective memory without clearing permanent chat history.
        """
        with self._turn_lock:
            self._degraded = False
            self._history.clear()
            self._homeostatic_engine.reset()
            self._emotion_core.reset_to_resting()
            self._affective_memory.clear()
            self._active_inference.reset()
            self._latest_result = None
            self._latest_comm_state = None
            self._latest_expr_state = None
        logger.info("CognitiveOrchestrator: lifecycle reset.")

    # ------------------------------------------------------------------
    # Private: 16-stage pipeline (Phase 16 Realization)
    # ------------------------------------------------------------------

    def _execute_pipeline(
        self, input_text: str, call_id: str, t_start: float
    ) -> CognitiveTurnResult:
        """
        Execute all 16 cognitive pipeline stages in strict causal order.
        All exceptions propagate to process(), which enters Degraded_State.
        """

        # ── Stage 1: Sensory Encoding ────────────────────────────────────
        stimulus: np.ndarray = self._stimulus_processor.encode(input_text)

        # ── Stage 2: Generative Prior Expectation ────────────────────────
        # Capture PAD *before* the stimulus is integrated (S2 must precede S3)
        pad_initial: PADState = self._emotion_core.get_pad_state()
        predicted_pad: np.ndarray = (
            self._active_inference._A @ np.array(
                [pad_initial.pleasure, pad_initial.arousal, pad_initial.dominance],
                dtype=np.float64,
            )
            + self._active_inference._b
        )

        # ── Stage 3: Limbic Integration ──────────────────────────────────
        # Inject stimulus into L2 limbic engine
        token = self._emotion_core.push_stimulus(stimulus)
        # Deterministically commit state transition before Stage 4 reads (temporal barrier)
        pad_committed: Optional[PADState] = None
        if hasattr(self._emotion_core, "commit_stimulus"):
            pad_committed = self._emotion_core.commit_stimulus(token)
        # Record metabolic cost ONCE (fixes double-execution bug from InstrumentedOrchestrator)
        self._homeostatic_engine.record_input()

        # ── Stage 4: Prediction Surprise & Belief Update ─────────────────
        # Read committed post-stimulus PAD state (exact snapshot from barrier)
        pad_final: PADState = (
            pad_committed if pad_committed is not None else self._emotion_core.get_pad_state()
        )
        prediction_error: float = self._active_inference.step(pad_initial, pad_final)

        # ── Stage 5: Homeostatic Modulation ──────────────────────────────
        base_markers: SomaticMarkers = self._homeostatic_engine.compute_somatic_markers(
            pad_final
        )
        # Causally couple surprise into cognitive load & tension
        markers: SomaticMarkers = self._surprise_policy.modulate_somatic(
            base_markers, prediction_error
        )
        # Phase 19: Push updated homeostatic context into limbic slow-layer context for subsequent ticks
        if hasattr(self._emotion_core, "update_homeostatic_context"):
            self._emotion_core.update_homeostatic_context(
                energy=markers.energy,
                load=markers.cognitive_load,
                tension=markers.tension,
                stability=markers.stability,
            )
        base_constraints: BehavioralConstraints = (
            self._homeostatic_engine.compute_behavioral_constraints(markers, pad_final)
        )
        # Select generation policy based on somatic state + surprise
        gen_policy: GenerationPolicy = GenerationPolicy.select(
            markers, prediction_error, self._surprise_policy
        )
        # Apply policy adjustments to homeostatic constraints
        constraints: BehavioralConstraints = gen_policy.apply_to_constraints(
            base_constraints
        )

        # ── Stage 6: Affective Ecphory (Memory Retrieval) ────────────────
        echo_vector: Optional[np.ndarray] = None
        recollection_result: Optional[RecollectionResult] = None
        try:
            traces = self._affective_memory.get_all_traces()
            if hasattr(self._ecphory_engine, "query_recollection"):
                echo_vector, recollection_result = (
                    self._ecphory_engine.query_recollection(
                        pad_final, stimulus, traces, config=self._emotion_core.config
                    )
                )
                if (
                    recollection_result.active
                    and self._emotion_core.config.enable_affective_recollection
                ):
                    self._emotion_core.inject_recollection(
                        recollection_result.r_slow_bounded
                    )
            else:
                echo_vector = self._ecphory_engine.query(pad_final, traces)
        except Exception:
            logger.error("CognitiveOrchestrator: ecphory step failed; omitting echo", exc_info=True)

        # ── Stage 7: Memory Context Extraction (Bounded Contextualization)
        m_avail = 0.0
        if echo_vector is not None:
            norm_val = float(np.linalg.norm(echo_vector))
            if norm_val > 0.01:
                m_avail = 1.0

        # ── Stage 8: Structured Knowledge Retrieval ──────────────────────
        known_propositions: List[Proposition] = []
        try:
            if self._knowledge_store is not None:
                known_propositions = self._knowledge_store.query_relevant(input_text, max_results=5)
        except Exception:
            logger.error("CognitiveOrchestrator: knowledge retrieval failed", exc_info=True)

        # ── Stage 9: Relationship Read (Read-Only Pre-Turn State) ────────
        # Point 1: Read existing state R_{t-1} BEFORE communication generation; no update here!
        rel_state: RelationshipState
        try:
            if self._relationship_updater is not None:
                rel_state = self._relationship_updater.get_state()
            else:
                rel_state = RelationshipState.initial()
        except Exception:
            logger.error("CognitiveOrchestrator: relationship read failed", exc_info=True)
            rel_state = RelationshipState.initial()

        # ── Stage 10: Communication Policy Evaluation ────────────────────
        comm_state: CommunicationState
        try:
            k_dict = {"fact_count": len(known_propositions)} if known_propositions else None
            rec_act = bool(recollection_result is not None and recollection_result.active)
            m_dict = (
                {"echo_active": m_avail > 0, "recollection_active": rec_act}
                if (m_avail > 0 or rec_act)
                else None
            )
            comm_state = self._comm_policy.compute(
                pad=pad_final,
                somatic=markers,
                relationship=rel_state.to_dict(),
                knowledge=k_dict,
                recollection=m_dict,
                prev_state=self._latest_comm_state,
            )
            self._latest_comm_state = comm_state
        except Exception:
            logger.error(
                "CognitiveOrchestrator: communication policy failed; falling back to neutral baseline",
                exc_info=True,
            )
            comm_state = self._comm_policy.get_neutral_actuator_baseline()

        # ── Stage 11: Contextual Prompt Assembly (formerly Stage 7: Prompt Assembly) ──
        prompt_or_err = self._prompt_assembler.assemble(
            somatic=markers,
            constraints=constraints,
            history=self._history,
            system_preamble=self._system_preamble,
            n_ctx=self._n_ctx,
            echo_vector=echo_vector,
            comm_state=comm_state,
            knowledge_propositions=known_propositions,
        )
        if isinstance(prompt_or_err, AssemblyError):
            logger.warning(
                "CognitiveOrchestrator: prompt assembly failed (call_id=%s): %s",
                call_id,
                prompt_or_err,
            )
            return self._make_fallback_result(
                input_text, "assembly_error", max(0.0001, time.perf_counter() - t_start)
            )

        prompt: str = prompt_or_err

        # ── Stage 12: Conversational Pacing ──────────────────────────────
        delta_tau_pace = 0
        if (
            recollection_result is not None
            and recollection_result.active
            and self._emotion_core.config.enable_affective_recollection
        ):
            r_norm = float(np.linalg.norm(recollection_result.r_slow_bounded))
            valence_factor = 1.0 - ((pad_final.pleasure + 1.0) / 2.0)
            delta_tau_pace = int(
                self._emotion_core.config.recollection_pacing_weight
                * r_norm
                * valence_factor
            )

        pacing_delay_ms = min(
            constraints.latency_ms
            + comm_state.injected_pacing_latency_ms
            + delta_tau_pace,
            _MAX_LATENCY_MS,
        )
        if pacing_delay_ms > 0:
            time.sleep(pacing_delay_ms / 1000.0)

        # ── Stage 13: LLM Generation & Boundary Layer ────────────────────
        raw_response = self._llm_backend.generate(prompt, constraints)
        if raw_response is None:
            logger.warning(
                "CognitiveOrchestrator: LLM returned None (call_id=%s)", call_id
            )
            return self._make_fallback_result(
                input_text, "llm_none", max(0.0001, time.perf_counter() - t_start)
            )

        safe_response: str = self._boundary_layer.validate(raw_response)
        if safe_response.strip() == "[...]":
            safe_response = self._fallback_response

        # ── Stage 14: Semantic Consistency Guard ─────────────────────────
        # Point 4: Evaluates consistency without claiming universal truth verification
        try:
            if known_propositions:
                facts_dict = {p.subject: p.object for p in known_propositions}
                guard_result = self._comm_semantic_guard.evaluate(
                    intent=CommIntent(
                        subject=known_propositions[0].subject,
                        predicate=known_propositions[0].predicate,
                        object=known_propositions[0].object,
                        polarity=True,
                    ),
                    surface_text=safe_response,
                    known_facts=facts_dict,
                )
                if not guard_result.is_preserved:
                    logger.debug(
                        "CognitiveOrchestrator: semantic guard flagged deviation (non-blocking): %s",
                        guard_result,
                    )
        except Exception:
            logger.debug("CognitiveOrchestrator: semantic guard check skipped", exc_info=True)

        # ── Stage 15: Expression Policy & Actuation State ────────────────
        expr_state: ExpressionState
        try:
            expr_state = self._expression_policy.compute(
                pad=pad_final,
                somatic=markers,
                relationship=rel_state.to_dict(),
                prev_state=self._latest_expr_state,
            )
            self._latest_expr_state = expr_state
        except Exception:
            logger.error(
                "CognitiveOrchestrator: expression policy failed; falling back to neutral baseline",
                exc_info=True,
            )
            expr_state = self._expression_policy.get_neutral_actuator_baseline()

        # ── Stage 16: Post-Turn Persistence & Adaptation ──────────────────
        # 16.1 Affective Memory Consolidation
        trace_stored = False
        try:
            M = self._affective_memory._M
            if stimulus.shape[0] >= M:
                content = stimulus[:M].astype(np.float32)
            else:
                content = np.zeros(M, dtype=np.float32)
                content[: stimulus.shape[0]] = stimulus.astype(np.float32)
            content = np.clip(content, -1.0, 1.0)
            s_slow_snapshot = (
                self._emotion_core.get_slow_latent_state()
                if hasattr(self._emotion_core, "get_slow_latent_state")
                else None
            )
            self._affective_memory.store(
                content, pad_final, slow_latent_trace=s_slow_snapshot
            )
            trace_stored = True
        except Exception:
            logger.error(
                "CognitiveOrchestrator: memory store step failed; continuing",
                exc_info=True,
            )

        # 16.2 Plasticity Tagging
        experience_queued = False
        if self._lnn_trainer is not None and self._plasticity_policy.should_tag(
            prediction_error
        ):
            try:
                hidden_dim: int = getattr(
                    self._lnn_trainer._config, "hidden_dim", 32
                )
                h_before = np.zeros(hidden_dim, dtype=np.float64)
                h_after = stimulus.astype(np.float64)
                self._lnn_trainer.push_sample(
                    stimulus=stimulus,
                    h_before=h_before,
                    h_after=h_after,
                )
                experience_queued = True
            except Exception:
                logger.warning(
                    "CognitiveOrchestrator: plasticity tagging failed; continuing",
                    exc_info=True,
                )

        # Phase 21: Tier 3 Consolidation Experience Tagging (salience >= 0.50)
        try:
            if hasattr(self._emotion_core, "record_consolidation_experience"):
                salience = float(prediction_error)
                if salience >= 0.50:
                    h_before = getattr(self._emotion_core, "_h", np.zeros(32, dtype=np.float64))
                    s_slow = (
                        self._emotion_core.get_slow_latent_state()
                        if hasattr(self._emotion_core, "get_slow_latent_state")
                        else np.zeros(16, dtype=np.float64)
                    )
                    r_slow = (
                        self._emotion_core._recollection_forcing
                        if hasattr(self._emotion_core, "_recollection_forcing")
                        else np.zeros(16, dtype=np.float64)
                    )
                    self._emotion_core.record_consolidation_experience(
                        stimulus=stimulus,
                        h_before=h_before,
                        h_after=stimulus.astype(np.float64) if len(stimulus) == len(h_before) else h_before,
                        s_slow=s_slow,
                        salience=salience,
                        relational_state=rel_state.to_array(),
                        r_slow=r_slow,
                    )
        except Exception:
            logger.warning("CognitiveOrchestrator: Phase 21 consolidation experience recording failed", exc_info=True)

        # 16.3 Structured Relationship Update (Points 1 & 3)
        rel_state_updated = rel_state
        if self._relationship_updater is not None:
            try:
                signal_type = RelationshipSignalType.CASUAL_INTERACTION
                if prediction_error < 0.30 and markers.tension < 0.40:
                    signal_type = RelationshipSignalType.COLLABORATIVE_SUCCESS
                sig = RelationshipSignal.create(signal_type, intensity=0.5)
                rel_state_updated, _ = self._relationship_updater.step(signal=sig)
            except Exception:
                logger.error(
                    "CognitiveOrchestrator: relationship update step failed; continuing",
                    exc_info=True,
                )

        # Phase 21: Forward updated relationship state to EmotionCore
        if hasattr(self._emotion_core, "update_relationship_context"):
            try:
                self._emotion_core.update_relationship_context(rel_state_updated.to_array())
            except Exception:
                logger.warning(
                    "CognitiveOrchestrator: failed to forward relationship context to EmotionCore",
                    exc_info=True,
                )

        # 16.4 Update dialogue history (ephemeral working memory)
        self._history.append(("user", input_text))
        self._history.append(("assistant", safe_response))
        max_pairs = self._max_history_turns * 2
        if len(self._history) > max_pairs:
            self._history = self._history[-max_pairs:]

        execution_time_s = max(0.0001, time.perf_counter() - t_start)

        logger.info(
            "CognitiveOrchestrator call_id=%s t=%.3fs pred_err=%.4f mode=%s "
            "markers=%s constraints=%s trace=%s",
            call_id,
            execution_time_s,
            prediction_error,
            gen_policy.mode,
            markers,
            constraints,
            trace_stored,
        )

        return CognitiveTurnResult(
            call_id=call_id,
            response_text=safe_response,
            pad_initial=pad_initial,
            pad_final=pad_final,
            stimulus=stimulus,
            prediction_error=prediction_error,
            somatic=markers,
            constraints=constraints,
            generation_policy=gen_policy,
            echo_vector=echo_vector,
            trace_stored=trace_stored,
            experience_queued=experience_queued,
            execution_time_s=execution_time_s,
            relationship=rel_state_updated,
            communication=comm_state,
            expression=expr_state,
            known_facts=known_propositions,
            recollection=recollection_result,
        )

    # ------------------------------------------------------------------
    # Private: helpers
    # ------------------------------------------------------------------

    def _make_fallback_result(
        self, input_text: str, reason: str, elapsed: float
    ) -> CognitiveTurnResult:
        """
        Construct a sentinel CognitiveTurnResult for degraded/guard paths.
        Uses resting PAD and default constraints so callers always receive a
        structurally valid object.
        """
        resting = PADState.resting()
        from src.core.models import default_behavioral_constraints
        return CognitiveTurnResult(
            call_id=uuid.uuid4().hex,
            response_text=self._fallback_response,
            pad_initial=resting,
            pad_final=resting,
            stimulus=np.zeros(16, dtype=np.float64),
            prediction_error=0.0,
            somatic=SomaticMarkers(stability=1.0, cognitive_load=0.0, energy=1.0, tension=0.0),
            constraints=default_behavioral_constraints(),
            generation_policy=GenerationPolicy.reflexive(),
            echo_vector=None,
            trace_stored=False,
            experience_queued=False,
            execution_time_s=elapsed,
        )

    def _wait_for_fast_loop(self) -> None:
        """
        Poll until the Fast_Loop thread is alive and has completed >= 1 tick.
        Raises RuntimeError after _STARTUP_TIMEOUT_S seconds.
        """
        deadline = time.monotonic() + _STARTUP_TIMEOUT_S
        while time.monotonic() < deadline:
            if (
                self._emotion_core.is_alive()
                and self._emotion_core.tick_count() >= 1
            ):
                logger.info(
                    "CognitiveOrchestrator: Fast_Loop ready (ticks=%d)",
                    self._emotion_core.tick_count(),
                )
                return
            time.sleep(0.05)
        raise RuntimeError(
            f"CognitiveOrchestrator: EmotionCore Fast_Loop did not become ready "
            f"within {_STARTUP_TIMEOUT_S:.0f} seconds."
        )


# ---------------------------------------------------------------------------
# Factory: build CognitiveOrchestrator from existing config objects
# ---------------------------------------------------------------------------

def build_cognitive_orchestrator(
    config: MemoryOrchestratorConfig,
    surprise_policy: Optional[SurpriseModulationPolicy] = None,
    plasticity_policy: Optional[PlasticityPolicy] = None,
    knowledge_store: Optional[KnowledgeStore] = None,
    relationship_updater: Optional[RelationshipUpdater] = None,
    comm_policy: Optional[CommunicationPolicy] = None,
    expression_policy: Optional[ExpressionPolicy] = None,
    llm_backend: Optional[LLMBackend] = None,
) -> CognitiveOrchestrator:
    """
    Construct a fully wired CognitiveOrchestrator from a MemoryOrchestratorConfig.

    This factory replicates the wiring that was previously scattered across the
    inheritance chain (Orchestrator, MemoryAugmentedOrchestrator,
    InstrumentedOrchestrator) and consolidates it in one place.
    """
    stimulus_processor = StimulusProcessor(config.to_stimulus_config())
    emotion_core = EmotionCore(config.to_emotion_config())
    homeostatic_engine = HomeostaticEngine(HomeostaticConfig())
    active_inference = ActiveInferenceEngine(ActiveInferenceConfig())
    affective_memory = AffectiveMemory(config.to_affective_memory_config())
    decay_engine = DecayEngine(affective_memory, config.to_decay_config())
    ecphory_engine = EcphoryEngine(config.to_ecphory_config())
    prompt_assembler = PromptAssembler()
    if llm_backend is None:
        llm_backend = LLMBackend(config.to_llm_config())
    boundary_layer = BoundaryLayer(config.to_boundary_config())

    # LNN trainer is optional — gracefully disabled when torch is unavailable
    lnn_trainer: Optional[LNNTrainer] = None
    try:
        lnn_trainer = LNNTrainer(
            emotion_core=emotion_core,
            config=LNNTrainerConfig(batch_size=16),
        )
    except Exception:
        logger.warning(
            "CognitiveOrchestrator: LNNTrainer unavailable (torch/torchdiffeq "
            "not installed); plasticity disabled.",
            exc_info=True,
        )

    return CognitiveOrchestrator(
        stimulus_processor=stimulus_processor,
        emotion_core=emotion_core,
        homeostatic_engine=homeostatic_engine,
        active_inference=active_inference,
        affective_memory=affective_memory,
        ecphory_engine=ecphory_engine,
        decay_engine=decay_engine,
        prompt_assembler=prompt_assembler,
        llm_backend=llm_backend,
        boundary_layer=boundary_layer,
        lnn_trainer=lnn_trainer,
        surprise_policy=surprise_policy,
        plasticity_policy=plasticity_policy,
        knowledge_store=knowledge_store,
        relationship_updater=relationship_updater,
        comm_policy=comm_policy,
        expression_policy=expression_policy,
        system_preamble=config.system_preamble,
        n_ctx=config.n_ctx,
        max_history_turns=config.max_history_turns,
        fallback_response=config.fallback_response,
    )
