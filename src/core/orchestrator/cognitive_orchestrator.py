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
from pathlib import Path
from typing import List, Optional, Tuple, Union

import numpy as np

from src.core.communication.caps import (
    AdmissibleEvidencePool,
    CAPSResult,
    CognitiveStateSnapshot,
    CommunicationPolicySnapshot,
    CommunicativeAct,
    DialogueContextSnapshot,
    DialoguePhase,
    DyadicDiscourseState,
    FloorStatus,
    PragmaticStance,
    evaluate_caps,
)
from src.core.communication.communication_policy import CommunicationPolicy
from src.core.communication.communication_state import CommIntent, CommunicationState
from src.core.communication.semantic_consistency_guard import (
    SemanticConsistencyGuard as CommSemanticGuard,
)
from src.core.orchestrator.discourse_cache import (
    DiscourseContextCache,
    DiscourseReferent,
    ResolutionStatus,
)
from src.core.config import (
    BoundaryConfig,
    HomeostaticConfig,
    MemoryOrchestratorConfig,
    OrchestratorConfig,
    StimulusConfig,
)
from src.core.embodiment.coordinator import TemporalEmbodimentCoordinator
from src.core.emotion.emotion_core import EmotionCore
from src.core.emotion.homeostatic_engine import HomeostaticEngine
from src.core.errors import AssemblyError
from src.core.expression.expression_policy import ExpressionPolicy
from src.core.expression.expression_state import ExpressionState, VoiceProsody
from src.core.expression.semantic_consistency_guard import (
    SemanticConsistencyGuard as ExprSemanticGuard,
)
from src.core.gating.stimulus_processor import StimulusProcessor
from src.core.inference.active_inference import ActiveInferenceConfig, ActiveInferenceEngine
from src.core.inference.lnn_trainer import LNNTrainer, LNNTrainerConfig
from src.core.knowledge.proposition import Proposition, ProvenanceType
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
from src.core.emotion.persistence import (
    DEFAULT_DYNAMICAL_STATE_PATH,
    DEFAULT_EPOCH_MANIFEST_PATH,
    EpochManifest,
    load_epoch_manifest,
    save_epoch_manifest,
    verify_and_reconcile_stores,
)
from src.core.orchestrator.prompt_assembler import PromptAssembler
from src.core.language.contract import (
    RealizationInputContract,
    RealizationOutput,
    TextRealization,
    VoiceRealization,
)
from src.core.language.detection import detect_active_language
from src.core.language.realization import construct_realization_output
from src.core.language.gate import GateDecision, SemanticFidelityGate
from src.core.relationship.persistence import DEFAULT_RELATIONSHIP_PATH
from src.core.relationship.signals import RelationshipSignal, RelationshipSignalType
from src.core.relationship.state import RelationshipState
from src.core.relationship.updater import RelationshipUpdater
from src.core.safety.boundary_layer import BoundaryLayer
from src.core.storage.history_store import ChatHistoryStore
from src.core.telemetry import (
    CognitiveExecutionTracer,
    CognitiveTurnTrace,
    ContractResult,
    ExecutionFailureClass,
    ExecutionSpan,
    InvariantResult,
    NullSpanContext,
    SpanStatus,
    TraceBuffer,
)

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
        # --- Phase 25 Subsystem (Optional) ---
        temporal_coordinator: Optional[TemporalEmbodimentCoordinator] = None,
        # --- Stage S14 Verification Subsystem (ADR-035) ---
        semantic_gate: Optional[SemanticFidelityGate] = None,
        # --- Stage Execution Observability (Blocker 4) ---
        execution_tracer: Optional[CognitiveExecutionTracer] = None,
        # --- Configuration knobs ---
        system_preamble: str = "",
        n_ctx: int = 2048,
        max_history_turns: int = 20,
        fallback_response: str = "...",
        epoch_manifest_path: Optional[Union[str, Path]] = None,
        initial_history: Optional[List[Tuple[str, str]]] = None,
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
        self._temporal_coordinator = (
            temporal_coordinator
            if temporal_coordinator is not None
            else TemporalEmbodimentCoordinator()
        )
        # ADR-035: Stage S14 Fail-Closed Semantic Fidelity Gate
        self._semantic_gate = semantic_gate if semantic_gate is not None else SemanticFidelityGate()
        self._latest_gate_decision: Optional[GateDecision] = None
        # Blocker 4: In-Memory Cognitive Execution Tracer
        self._execution_tracer = (
            execution_tracer if execution_tracer is not None else CognitiveExecutionTracer()
        )

        # Policy defaults
        self._surprise_policy = surprise_policy or SurpriseModulationPolicy()
        self._plasticity_policy = plasticity_policy or PlasticityPolicy()

        # Configuration
        self._system_preamble = system_preamble
        n_ctx = n_ctx
        self._n_ctx = n_ctx
        self._max_history_turns = max_history_turns
        self._fallback_response = fallback_response
        self._epoch_manifest_path = Path(epoch_manifest_path) if epoch_manifest_path else None
        self._current_epoch = 0
        if self._epoch_manifest_path is not None and self._epoch_manifest_path.exists():
            man = load_epoch_manifest(self._epoch_manifest_path)
            if man is not None:
                self._current_epoch = man.epoch_id

        # Mutable orchestrator state (only these — no subsystem state copies)
        self._history: List[Tuple[str, str]] = list(initial_history) if initial_history else []
        self._discourse_cache = DiscourseContextCache()
        self._dyadic_state = DyadicDiscourseState()
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
    def latest_gate_decision(self) -> Optional[GateDecision]:
        """Most recent Stage S14 verification gate decision."""
        return self._latest_gate_decision

    @property
    def knowledge_store(self) -> KnowledgeStore:
        return self._knowledge_store

    @property
    def relationship_updater(self) -> RelationshipUpdater:
        return self._relationship_updater

    @property
    def temporal_coordinator(self) -> TemporalEmbodimentCoordinator:
        return self._temporal_coordinator

    @property
    def latest_communication(self) -> Optional[CommunicationState]:
        return self._latest_comm_state

    @property
    def latest_expression(self) -> Optional[ExpressionState]:
        return self._latest_expr_state

    @property
    def discourse_cache(self) -> DiscourseContextCache:
        return self._discourse_cache

    @property
    def execution_tracer(self) -> CognitiveExecutionTracer:
        return self._execution_tracer

    def get_latest_trace(self) -> Optional[CognitiveTurnTrace]:
        """Return the most recent cognitive execution trace from the in-memory buffer."""
        try:
            return self._execution_tracer.buffer.get_latest()
        except Exception:
            return None

    def get_trace_buffer(self) -> TraceBuffer:
        """Return the bounded in-memory trace buffer."""
        return self._execution_tracer.buffer

    def get_execution_tracer(self) -> CognitiveExecutionTracer:
        """Return the execution tracer instance."""
        return self._execution_tracer

    def _trace_span(
        self,
        sequence_id: str,
        stage_name: str,
        module_id: Optional[str] = None,
        module_version: Optional[str] = None,
        causal_parent: Optional[str] = None,
    ):
        try:
            return self._execution_tracer.span(
                sequence_id=sequence_id,
                stage_name=stage_name,
                module_id=module_id,
                module_version=module_version,
                causal_parent=causal_parent,
            )
        except Exception as exc:
            logger.debug("CognitiveOrchestrator._trace_span error: %s", exc)
            return NullSpanContext(sequence_id=sequence_id, stage_name=stage_name)

    def clear_history(self) -> None:
        """Clear ephemeral dialogue history and active discourse referents."""
        with self._turn_lock:
            self._history.clear()
            self._discourse_cache.clear()

    def process(
        self, input_text: str, user_language: Optional[str] = None
    ) -> CognitiveTurnResult:
        """
        Execute a full 16-stage cognitive turn and return an immutable result.

        Returns the fallback result immediately for:
          - empty or oversized input
          - Degraded_State (any previous unhandled exception)

        Acquires _turn_lock before any pipeline execution; all concurrent
        callers block until the lock is released.
        """
        # --- Input guard ---
        if len(input_text) == 0 or len(input_text) > _MAX_INPUT_LEN:
            return self._make_fallback_result(
                input_text, "empty_or_oversized_input", 0.0, user_language=user_language
            )

        # --- Degraded guard ---
        if self._degraded:
            return self._make_fallback_result(
                input_text, "degraded_state", 0.0, user_language=user_language
            )

        call_id = uuid.uuid4().hex
        t_start = time.perf_counter()

        # Blocker 4: Start Cognitive Execution Trace (fail-open)
        try:
            self._execution_tracer.start_turn(turn_id=self._current_epoch, call_id=call_id)
        except Exception as exc:
            logger.debug("CognitiveOrchestrator: trace start error (fail-open): %s", exc)

        # Tier 3: non-reentrant turn serialization
        acquired = self._turn_lock.acquire(blocking=True)
        try:
            result = self._execute_pipeline(
                input_text, call_id, t_start, user_language=user_language
            )
        except Exception:
            logger.exception(
                "CognitiveOrchestrator: unhandled exception (call_id=%s)", call_id
            )
            self._degraded = True
            trace = None
            try:
                trace = self._execution_tracer.end_turn()
            except Exception:
                pass
            result = self._make_fallback_result(
                input_text,
                "pipeline_exception",
                max(0.0001, time.perf_counter() - t_start),
                trace=trace,
                user_language=user_language,
            )
        finally:
            if acquired:
                self._turn_lock.release()
            try:
                if self._execution_tracer.active_trace is not None:
                    trace = self._execution_tracer.end_turn()
                    if trace is not None and getattr(result, "execution_trace", None) is None:
                        object.__setattr__(result, "execution_trace", trace)
            except Exception:
                pass

        # Atomic pointer update — readable by /state without locks
        self._latest_result = result
        return result

    def shutdown(self) -> None:
        """Stop all background daemons and release the LLM model."""
        self._shutdown = True
        if hasattr(self._emotion_core, "checkpoint"):
            try:
                self._emotion_core.checkpoint()
            except Exception:
                pass
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
            self._temporal_coordinator.reset()
            self._latest_result = None
            self._latest_comm_state = None
            self._latest_expr_state = None
            self._latest_gate_decision = None
        logger.info("CognitiveOrchestrator: lifecycle reset.")

    def get_latest_trace(self) -> Optional[CognitiveTurnTrace]:
        """Return the most recent cognitive execution trace from in-memory buffer."""
        return self._execution_tracer.buffer.get_latest()

    def get_trace_buffer(self) -> TraceBuffer:
        """Return the bounded in-memory trace buffer."""
        return self._execution_tracer.buffer

    def get_execution_tracer(self) -> CognitiveExecutionTracer:
        """Return the active cognitive execution tracer."""
        return self._execution_tracer

    # ------------------------------------------------------------------
    # Private: 16-stage pipeline (Phase 16 Realization)
    # ------------------------------------------------------------------

    def _execute_pipeline(
        self,
        input_text: str,
        call_id: str,
        t_start: float,
        user_language: Optional[str] = None,
    ) -> CognitiveTurnResult:
        """
        Execute all 16 cognitive pipeline stages in strict causal order.
        All exceptions propagate to process(), which enters Degraded_State.
        """

        # ── Stage 0: Temporal Embodiment & Social Observation (P25) ──────
        t_now = time.time()
        cur_pad = self._emotion_core.get_pad_state()
        cur_energy = getattr(self._homeostatic_engine, "_energy", 1.0)
        temp_obs, temp_est, idle_res = self._temporal_coordinator.process_turn_start(
            current_timestamp=t_now,
            user_text=input_text,
            current_pad=cur_pad,
            current_energy=cur_energy,
        )

        # ── Stage 1: Sensory Encoding ────────────────────────────────────
        with self._trace_span("S1", "SensoryEncoding", module_id="StimulusProcessor") as s1_span:
            stimulus: np.ndarray = self._stimulus_processor.encode(input_text)
            s1_span.set_summary({
                "input_len": len(input_text),
                "stimulus_dim": int(stimulus.shape[0]),
                "stimulus_norm": float(np.linalg.norm(stimulus)),
            })

        # ── Stage 2: Generative Prior Expectation ────────────────────────
        with self._trace_span("S2", "GenerativePriorExpectation", module_id="ActiveInferenceEngine") as s2_span:
            # Capture PAD *before* the stimulus is integrated (S2 must precede S3)
            pad_initial: PADState = self._emotion_core.get_pad_state()
            predicted_pad: np.ndarray = (
                self._active_inference._A @ np.array(
                    [pad_initial.pleasure, pad_initial.arousal, pad_initial.dominance],
                    dtype=np.float64,
                )
                + self._active_inference._b
            )
            s2_span.set_summary({
                "pad_p": pad_initial.pleasure,
                "pad_a": pad_initial.arousal,
                "pad_d": pad_initial.dominance,
                "pred_p": float(predicted_pad[0]),
                "pred_a": float(predicted_pad[1]),
                "pred_d": float(predicted_pad[2]),
            })

        # ── Stage 3: Limbic Integration ──────────────────────────────────
        with self._trace_span("S3", "LimbicIntegration", module_id="EmotionCore", causal_parent="S1") as s3_span:
            # Inject stimulus into L2 limbic engine
            token = self._emotion_core.push_stimulus(stimulus)
            # Deterministically commit state transition before Stage 4 reads (temporal barrier)
            pad_committed: Optional[PADState] = None
            if hasattr(self._emotion_core, "commit_stimulus"):
                pad_committed = self._emotion_core.commit_stimulus(token)
            # Record metabolic cost ONCE (fixes double-execution bug from InstrumentedOrchestrator)
            self._homeostatic_engine.record_input()

            if token is None:
                s3_span.record_contract(
                    satisfied=False,
                    failure_class=ExecutionFailureClass.CONTRACT_VIOLATION,
                    detail="Limbic stimulus push returned None token",
                )
            s3_span.set_summary({
                "token_valid": token is not None,
                "committed": pad_committed is not None,
                "committed_p": pad_committed.pleasure if pad_committed else None,
                "committed_a": pad_committed.arousal if pad_committed else None,
                "committed_d": pad_committed.dominance if pad_committed else None,
            })

        # ── Stage 4: Prediction Surprise & Belief Update ─────────────────
        with self._trace_span("S4", "PredictionSurpriseUpdate", module_id="ActiveInferenceEngine", causal_parent="S3") as s4_span:
            # Read committed post-stimulus PAD state (exact snapshot from barrier)
            pad_final: PADState = (
                pad_committed if pad_committed is not None else self._emotion_core.get_pad_state()
            )
            active_trace = self._execution_tracer.active_trace
            if active_trace and "S3" in active_trace.failed_stages:
                s4_span.record_contract(
                    satisfied=False,
                    failure_class=ExecutionFailureClass.DOWNSTREAM_PROPAGATED_FAILURE,
                    detail="S4 received uncommitted/invalid limbic state from failed S3",
                )
            prediction_error: float = self._active_inference.step(pad_initial, pad_final)
            s4_span.set_summary({
                "prediction_error": float(prediction_error),
                "pad_final_p": pad_final.pleasure,
                "pad_final_a": pad_final.arousal,
                "pad_final_d": pad_final.dominance,
            })

        # ── Stage 5: Homeostatic Modulation ──────────────────────────────
        with self._trace_span("S5", "HomeostaticModulation", module_id="HomeostaticEngine", causal_parent="S4") as s5_span:
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
            s5_span.set_summary({
                "energy": markers.energy,
                "cognitive_load": markers.cognitive_load,
                "tension": markers.tension,
                "stability": markers.stability,
                "policy_mode": gen_policy.mode,
            })

        # ── Stage 6: Affective Ecphory (Memory Retrieval) ────────────────
        with self._trace_span("S6", "AffectiveEcphory", module_id="EcphoryEngine", causal_parent="S3") as s6_span:
            echo_vector: Optional[np.ndarray] = None
            recollection_result: Optional[RecollectionResult] = None
            traces_count = 0
            try:
                traces = self._affective_memory.get_all_traces()
                traces_count = len(traces)
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
            except Exception as exc:
                logger.error("CognitiveOrchestrator: ecphory step failed; omitting echo", exc_info=True)
                s6_span.record_contract(
                    satisfied=False,
                    failure_class=ExecutionFailureClass.HARD_EXECUTION_FAILURE,
                    detail=str(exc),
                )
            s6_span.set_summary({
                "traces_count": traces_count,
                "echo_active": echo_vector is not None,
                "recollection_active": bool(recollection_result and recollection_result.active),
            })

        # ── Stage 7: Memory Context Extraction (Bounded Contextualization)
        with self._trace_span("S7", "MemoryContextExtraction", module_id="AffectiveMemory", causal_parent="S6") as s7_span:
            m_avail = 0.0
            if echo_vector is not None:
                norm_val = float(np.linalg.norm(echo_vector))
                if norm_val > 0.01:
                    m_avail = 1.0
            s7_span.set_summary({"m_avail": m_avail})

        # ── Stage 8: Structured Knowledge Retrieval ──────────────────────
        with self._trace_span("S8", "KnowledgeRetrieval", module_id="KnowledgeStore", causal_parent="S1") as s8_span:
            known_propositions: List[Proposition] = []
            try:
                if self._knowledge_store is not None:
                    known_propositions = self._knowledge_store.query_relevant(input_text, max_results=5)
            except Exception as exc:
                logger.error("CognitiveOrchestrator: knowledge retrieval failed", exc_info=True)
                s8_span.record_contract(
                    satisfied=False,
                    failure_class=ExecutionFailureClass.HARD_EXECUTION_FAILURE,
                    detail=str(exc),
                )
            s8_span.set_summary({"propositions_count": len(known_propositions)})

        # ── Stage 9: Relationship Read (Read-Only Pre-Turn State) ────────
        with self._trace_span("S9", "RelationshipRead", module_id="RelationshipUpdater", causal_parent=None) as s9_span:
            # Point 1: Read existing state R_{t-1} BEFORE communication generation; no update here!
            rel_state: RelationshipState
            try:
                if self._relationship_updater is not None:
                    rel_state = self._relationship_updater.get_state()
                else:
                    rel_state = RelationshipState.initial()
            except Exception as exc:
                logger.error("CognitiveOrchestrator: relationship read failed", exc_info=True)
                rel_state = RelationshipState.initial()
                s9_span.record_contract(
                    satisfied=False,
                    failure_class=ExecutionFailureClass.HARD_EXECUTION_FAILURE,
                    detail=str(exc),
                )
            s9_span.set_summary({
                "trust": rel_state.trust,
                "familiarity": rel_state.familiarity,
                "closeness": rel_state.closeness,
                "reciprocity": rel_state.reciprocity,
            })

        # ── Stage 10: Communication Policy Evaluation ────────────────────
        with self._trace_span("S10", "CommunicationPolicy", module_id="CommunicationPolicy", causal_parent="S5") as s10_span:
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
            except Exception as exc:
                logger.error(
                    "CognitiveOrchestrator: communication policy failed; falling back to neutral baseline",
                    exc_info=True,
                )
                comm_state = self._comm_policy.get_neutral_actuator_baseline()
                s10_span.record_contract(
                    satisfied=False,
                    failure_class=ExecutionFailureClass.HARD_EXECUTION_FAILURE,
                    detail=str(exc),
                )

            # ── Stage 10b: Communicative Act & Proposition Selection (CAPS, Phase 23) ──
            caps_result: Optional[CAPSResult] = None
            history_turn_count = len(self._history) // 2
            # Persistent identity & interaction boundary:
            # First conversation only if both current epoch <= 1 and familiarity < 0.15.
            # Epoch > 1 or familiarity >= 0.15 implies persistent relationship history across restarts.
            is_first_interaction = (self._current_epoch <= 1 and rel_state.familiarity < 0.15)
            life_state_props = [
                Proposition(
                    id="prop:first_conversation",
                    subject="ent:lucia",
                    predicate="c:IS_FIRST_CONVERSATION",
                    object="true" if is_first_interaction else "false",
                    confidence=1.0,
                    provenance=ProvenanceType.OBSERVED,
                ),
                Proposition(
                    id="prop:turn_count",
                    subject="ent:dialogue",
                    predicate="c:TURN_COUNT",
                    object=str(history_turn_count),
                    confidence=1.0,
                    provenance=ProvenanceType.OBSERVED,
                ),
                Proposition(
                    id="prop:familiarity",
                    subject="ent:relationship",
                    predicate="c:FAMILIARITY_LEVEL",
                    object="initial_stranger" if rel_state.familiarity < 0.15 else "acquaintance" if rel_state.familiarity < 0.4 else "familiar",
                    confidence=1.0,
                    provenance=ProvenanceType.OBSERVED,
                ),
            ]
            all_verified_props = tuple(known_propositions) + tuple(life_state_props)

            try:
                active_refs = tuple(self._discourse_cache.get_all_referents())
                res_status, resolved_id, cand_ids = self._discourse_cache.resolve_reference()

                cand_pred = known_propositions[0].predicate if known_propositions else None
                cand_subj = known_propositions[0].subject if known_propositions else None
                cand_obj = known_propositions[0].object if known_propositions else None

                dialogue_snap = DialogueContextSnapshot(
                    turn_id=self._current_epoch,
                    input_text=input_text,
                    active_referents=active_refs,
                    resolution_status=res_status,
                    resolved_entity_id=resolved_id,
                    candidate_referent_ids=tuple(cand_ids),
                    dyadic_state=self._dyadic_state,
                )
                cog_snap = CognitiveStateSnapshot(
                    candidate_predicate=cand_pred,
                    candidate_subject=cand_subj,
                    candidate_object=cand_obj,
                    polarity=True,
                )
                evidence_pool = AdmissibleEvidencePool(
                    verified_propositions=all_verified_props,
                    user_claims=(),
                )
                policy_snap = CommunicationPolicySnapshot(
                    strategy=comm_state.strategy.value if comm_state else "balanced",
                    directness=comm_state.directness if comm_state else 1.0,
                    formality=comm_state.formality_score if comm_state else 0.5,
                    elaboration=comm_state.elaboration_depth if comm_state else 0.5,
                    supportiveness=comm_state.supportiveness if comm_state else 0.5,
                )
                caps_result = evaluate_caps(
                    dialogue_ctx=dialogue_snap,
                    cognitive_state=cog_snap,
                    evidence_pool=evidence_pool,
                    comm_policy=policy_snap,
                    session_id=call_id,
                )
            except Exception:
                logger.warning(
                    "CognitiveOrchestrator: CAPS evaluation failed; continuing without CAPS conditioning",
                    exc_info=True,
                )

            # ADR-035: Construct typed RealizationInputContract from CAPS decision
            # Production target language for text realization is canonically English ("en").
            # Multilingual perception is admitted, but realization targets are decoupled from perception.
            # Non-English text targets can be explicitly specified via user_language for research runs.
            target_lang = user_language if user_language is not None else "en"
            speaker_h = "em" if target_lang == "vi" else None
            addressee_h = "anh" if target_lang == "vi" else None
            forbidden_adds = ("bạn",) if target_lang == "vi" else ()
            current_phase_str = (
                self._dyadic_state.dialogue_phase.value
                if hasattr(self._dyadic_state.dialogue_phase, "value")
                else str(self._dyadic_state.dialogue_phase)
            )
            realization_contract: RealizationInputContract
            if caps_result is not None:
                realization_contract = RealizationInputContract.from_caps(
                    caps_result,
                    target_language=target_lang,
                    known_propositions=all_verified_props,
                    speaker_honorific=speaker_h,
                    addressee_honorific=addressee_h,
                    forbidden_additions=forbidden_adds,
                    dialogue_phase=current_phase_str,
                )
            else:
                realization_contract = RealizationInputContract.create_default(
                    target_language=target_lang,
                    speaker_honorific=speaker_h,
                    addressee_honorific=addressee_h,
                    forbidden_additions=forbidden_adds,
                    dialogue_phase=current_phase_str,
                )

            s10_span.set_summary({
                "strategy": comm_state.strategy.value if hasattr(comm_state.strategy, "value") else str(comm_state.strategy),
                "directness": comm_state.directness,
                "formality": comm_state.formality_score,
                "caps_active": caps_result is not None,
            })

        # ── Stage 11: Contextual Prompt Assembly (formerly Stage 7: Prompt Assembly) ──
        with self._trace_span("S11", "PromptAssembly", module_id="PromptAssembler", causal_parent="S10") as s11_span:
            prompt_or_err = self._prompt_assembler.assemble(
                somatic=markers,
                constraints=constraints,
                history=self._history + [("user", input_text)],
                system_preamble=self._system_preamble,
                n_ctx=self._n_ctx,
                echo_vector=echo_vector,
                comm_state=comm_state,
                knowledge_propositions=known_propositions,
                caps_result=caps_result,
                contract=realization_contract,
            )
            if isinstance(prompt_or_err, AssemblyError):
                logger.warning(
                    "CognitiveOrchestrator: prompt assembly failed (call_id=%s): %s",
                    call_id,
                    prompt_or_err,
                )
                s11_span.record_contract(
                    satisfied=False,
                    failure_class=ExecutionFailureClass.CONTRACT_VIOLATION,
                    detail=str(prompt_or_err),
                )
                trace = None
                try:
                    trace = self._execution_tracer.end_turn()
                except Exception:
                    pass
                return self._make_fallback_result(
                    input_text,
                    "assembly_error",
                    max(0.0001, time.perf_counter() - t_start),
                    trace=trace,
                    user_language=user_language,
                )

            prompt: str = prompt_or_err
            s11_span.set_summary({
                "prompt_len": len(prompt),
                "contract_enforced": realization_contract is not None,
            })

        # ── Stage 12: Conversational Pacing ──────────────────────────────
        with self._trace_span("S12", "ConversationalPacing", module_id="TemporalEmbodimentCoordinator", causal_parent="S10") as s12_span:
            temp_mod = self._temporal_coordinator.compute_attunement_modulation(
                rel_state=rel_state,
                somatic=markers,
                base_constraints=constraints,
            )

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
                + delta_tau_pace
                + temp_mod.injected_pacing_delay_ms,
                _MAX_LATENCY_MS,
            )
            if pacing_delay_ms > 0:
                time.sleep(pacing_delay_ms / 1000.0)
            s12_span.set_summary({"pacing_delay_ms": int(pacing_delay_ms)})

        # ── Stage 13: LLM Generation & Boundary Layer ────────────────────
        with self._trace_span("S13", "LanguageGeneration", module_id="LLMBackend", causal_parent="S11") as s13_span:
            raw_response = self._llm_backend.generate(prompt, constraints)
            if raw_response is None:
                logger.warning(
                    "CognitiveOrchestrator: LLM returned None (call_id=%s)", call_id
                )
                s13_span.record_contract(
                    satisfied=False,
                    failure_class=ExecutionFailureClass.HARD_EXECUTION_FAILURE,
                    detail="LLM returned None",
                )
                trace = None
                try:
                    trace = self._execution_tracer.end_turn()
                except Exception:
                    pass
                return self._make_fallback_result(
                    input_text,
                    "llm_none",
                    max(0.0001, time.perf_counter() - t_start),
                    trace=trace,
                    user_language=user_language,
                )
            s13_span.set_summary({"raw_response_len": len(raw_response)})

        # ── Stage 14: Fail-Closed Semantic Fidelity Gate (ADR-035) ──────────────
        with self._trace_span("S14", "SemanticFidelityGate", module_id="SemanticFidelityGate", causal_parent="S13") as s14_span:
            gate_decision = self._semantic_gate.verify(realization_contract, raw_response)
            self._latest_gate_decision = gate_decision
            if gate_decision.status in ("BLOCK", "UNCERTAIN"):
                logger.warning(
                    "CognitiveOrchestrator: Stage S14 SemanticFidelityGate BLOCKED realization "
                    "(status=%s, violations=%s, latency=%.3fms) -> Triggering deterministic fallback",
                    gate_decision.status,
                    gate_decision.violation_reasons,
                    gate_decision.latency_ms,
                )
                safe_response = gate_decision.fallback_text or self._fallback_response
                s14_span.record_contract(
                    satisfied=False,
                    failure_class=ExecutionFailureClass.CONTRACT_VIOLATION,
                    detail=f"Gate {gate_decision.status}: {gate_decision.violation_reasons}",
                )
            else:
                safe_response = self._boundary_layer.validate(raw_response)
                if safe_response.strip() == "[...]":
                    safe_response = self._fallback_response

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

            s14_span.set_summary({
                "gate_status": gate_decision.status,
                "safe_response_len": len(safe_response),
            })

        # ── Stage 15: Expression Policy & Actuation State ────────────────
        with self._trace_span("S15", "ExpressionPolicy", module_id="ExpressionPolicy", causal_parent="S5") as s15_span:
            expr_state: ExpressionState
            try:
                expr_state = self._expression_policy.compute(
                    pad=pad_final,
                    somatic=markers,
                    relationship=rel_state.to_dict(),
                    prev_state=self._latest_expr_state,
                )
                # P25: Apply bounded unilateral prosodic modulation to expression
                if expr_state is not None and expr_state.voice is not None and temp_mod is not None:
                    v_curr = expr_state.voice
                    v_curr.speech_rate_pct = float(
                        np.clip(v_curr.speech_rate_pct + temp_mod.speech_rate_pct_delta, -20.0, 20.0)
                    )
                    v_curr.pause_duration_ms = float(
                        np.clip(v_curr.pause_duration_ms + temp_mod.pause_duration_ms_delta, 100.0, 1000.0)
                    )
                    v_curr.pitch_shift_semitones = float(
                        np.clip(v_curr.pitch_shift_semitones + temp_mod.pitch_shift_st_delta, -2.0, 4.0)
                    )
                self._latest_expr_state = expr_state
            except Exception as exc:
                logger.error(
                    "CognitiveOrchestrator: expression policy failed; falling back to neutral baseline",
                    exc_info=True,
                )
                expr_state = self._expression_policy.get_neutral_actuator_baseline()
                s15_span.record_contract(
                    satisfied=False,
                    failure_class=ExecutionFailureClass.HARD_EXECUTION_FAILURE,
                    detail=str(exc),
                )
            s15_span.set_summary({
                "has_voice": expr_state.voice is not None if expr_state else False,
            })

        # ── Stage 16: Post-Turn Persistence & Adaptation ──────────────────
        with self._trace_span("S16", "PostTurnPersistence", module_id="ConsolidationEngine", causal_parent="S4") as s16_span:
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
            next_epoch = self._current_epoch + 1
            rel_state_updated = rel_state
            if self._relationship_updater is not None:
                try:
                    signal_type = RelationshipSignalType.CASUAL_INTERACTION
                    if prediction_error < 0.30 and markers.tension < 0.40:
                        signal_type = RelationshipSignalType.COLLABORATIVE_SUCCESS
                    sig = RelationshipSignal.create(signal_type, intensity=0.5)
                    rel_state_updated, _ = self._relationship_updater.step(signal=sig, epoch_id=next_epoch)
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

            # 16.4b Update Discourse Context Cache (Phase 23)
            try:
                mentioned = []
                if known_propositions:
                    for kp in known_propositions[:2]:
                        mentioned.append(
                            DiscourseReferent(
                                entity_id=kp.subject,
                                concept_id=f"c:{kp.subject.replace('ent:', '')}",
                                salience=1.0,
                                turn_introduced=self._current_epoch,
                                last_referenced_turn=self._current_epoch,
                                grammatical_role=":ARG0",
                            )
                        )
                self._discourse_cache.update_turn(
                    turn_id=self._current_epoch,
                    mentioned_referents=mentioned,
                )
            except Exception:
                logger.warning("CognitiveOrchestrator: discourse cache update failed; continuing", exc_info=True)

            # 16.4c Update Dyadic Discourse State (P23-D Grounding Correction)
            try:
                curr_phase = self._dyadic_state.dialogue_phase
                history_turns = len(self._history) // 2
                if history_turns > 3 and curr_phase == DialoguePhase.OPENING_ENCOUNTER:
                    next_phase = DialoguePhase.ACTIVE_EXCHANGE
                else:
                    next_phase = curr_phase

                # Determine current user stance from CAPS result or input
                user_stance = (
                    caps_result.pragmatic_stance.value
                    if caps_result and caps_result.pragmatic_stance
                    else "NEUTRAL"
                )

                # Determine assistant act
                asst_act = caps_result.act.value if caps_result else "ACKNOWLEDGE"

                # Floor status updates: if user yielded floor (hesitation), assistant took initiative -> MUTUAL_OPEN
                floor = FloorStatus.MUTUAL_OPEN

                # Unresolved expectation
                unresolved = None
                if caps_result and caps_result.act in (CommunicativeAct.INQUIRE, CommunicativeAct.CLARIFY):
                    unresolved = "USER_RESPONSE_EXPECTED"

                self._dyadic_state = DyadicDiscourseState(
                    dialogue_phase=next_phase,
                    floor_status=floor,
                    previous_assistant_act=asst_act,
                    previous_user_stance=user_stance,
                    unresolved_expectation=unresolved,
                )
            except Exception:
                logger.warning("CognitiveOrchestrator: dyadic state update failed; continuing", exc_info=True)

            # 16.5 F-02: Checkpoint persistent dynamical state & Epoch Commit Barrier
            if hasattr(self._emotion_core, "checkpoint"):
                try:
                    self._emotion_core.checkpoint(epoch_id=next_epoch)
                except Exception:
                    logger.warning(
                        "CognitiveOrchestrator: dynamical state checkpointing failed; continuing",
                        exc_info=True,
                    )

            if self._epoch_manifest_path is not None:
                try:
                    manifest = EpochManifest(
                        epoch_id=next_epoch,
                        t_checkpoint=time.time(),
                        stores={"relationship": next_epoch, "dynamical_state": next_epoch},
                    )
                    save_epoch_manifest(manifest, filepath=self._epoch_manifest_path)
                    self._current_epoch = next_epoch
                except Exception:
                    logger.warning(
                        "CognitiveOrchestrator: epoch manifest commit failed; continuing",
                        exc_info=True,
                    )

            s16_span.set_summary({
                "trace_stored": bool(trace_stored),
                "experience_queued": bool(experience_queued),
                "next_epoch": int(next_epoch),
            })

        execution_time_s = max(0.0001, time.perf_counter() - t_start)

        # Construct explicit RealizationOutput: text follows target_lang (canonical production "en"), voice is canonical Japanese ("ja")
        target_lang = (
            realization_contract.target_language
            if realization_contract
            else (user_language or "en")
        )
        japanese_voice_text = None
        if target_lang != "ja" and self._llm_backend is not None and hasattr(self._llm_backend, "translate_to_japanese"):
            try:
                japanese_voice_text = self._llm_backend.translate_to_japanese(safe_response)
            except Exception:
                logger.debug(
                    "CognitiveOrchestrator: Direct parallel voice realization will use semantic contract",
                    exc_info=True,
                )

        realization_output = construct_realization_output(
            safe_response=safe_response,
            user_language=target_lang,
            contract=realization_contract,
            known_propositions=known_propositions,
            japanese_voice_text=japanese_voice_text,
        )

        trace = None
        try:
            trace = self._execution_tracer.end_turn()
        except Exception:
            pass

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
            temporal_state=temp_est,
            temporal_modulation=temp_mod,
            caps_result=caps_result,
            discourse_referents=self._discourse_cache.get_all_referents(),
            realization_contract=realization_contract,
            gate_decision=gate_decision,
            execution_trace=trace,
            realization=realization_output,
        )

    # ------------------------------------------------------------------
    # Private: helpers
    # ------------------------------------------------------------------

    def _make_fallback_result(
        self,
        input_text: str,
        reason: str,
        elapsed: float,
        trace: Optional[Any] = None,
        user_language: Optional[str] = None,
    ) -> CognitiveTurnResult:
        """
        Construct a sentinel CognitiveTurnResult for degraded/guard paths.
        Uses resting PAD and default constraints so callers always receive a
        structurally valid object.
        """
        resting = PADState.resting()
        from src.core.models import default_behavioral_constraints
        fallback_lang = user_language or "en"
        fallback_realization = construct_realization_output(
            safe_response=self._fallback_response,
            user_language=fallback_lang,
            contract=None,
        )
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
            execution_trace=trace,
            realization=fallback_realization,
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
    temporal_coordinator: Optional[TemporalEmbodimentCoordinator] = None,
    llm_backend: Optional[LLMBackend] = None,
    relationship_storage_path: Optional[Union[str, Path]] = DEFAULT_RELATIONSHIP_PATH,
    dynamical_storage_path: Optional[Union[str, Path]] = DEFAULT_DYNAMICAL_STATE_PATH,
    epoch_manifest_path: Optional[Union[str, Path]] = None,
    chat_history_path: Optional[Union[str, Path]] = None,
    semantic_gate: Optional[SemanticFidelityGate] = None,
    execution_tracer: Optional[CognitiveExecutionTracer] = None,
) -> CognitiveOrchestrator:
    """
    Construct a fully wired CognitiveOrchestrator from a MemoryOrchestratorConfig.

    Implements the Ratified F-02 Inverted Startup Sequence:
    1. Read and reconcile commit barrier (epoch_manifest.json) across stores.
    2. Construct/load RelationshipUpdater first to obtain authoritative R_t.
    3. Construct EmotionCore with auto_restore=False.
    4. Inject R_t into EmotionCore before recovery (critical invariant: no stranger R_0 recovery).
    5. Restore dynamical checkpoint and apply two-stage physical downtime recovery.
    6. Reconstruct working context _history from trailing K turns of chat_history.json.
    """
    rel_path = Path(relationship_storage_path) if relationship_storage_path else DEFAULT_RELATIONSHIP_PATH
    dyn_path = Path(dynamical_storage_path) if dynamical_storage_path else DEFAULT_DYNAMICAL_STATE_PATH
    man_path = Path(epoch_manifest_path) if epoch_manifest_path else (dyn_path.parent / "epoch_manifest.json")

    # 1. Commit Barrier & Consistency Detection reconciliation
    verify_and_reconcile_stores(
        relationship_path=rel_path,
        dynamical_path=dyn_path,
        manifest_path=man_path,
    )

    # 2. Authoritative Tier 1 Relational Invariants loaded FIRST
    if relationship_updater is None:
        relationship_updater = RelationshipUpdater(
            storage_path=rel_path
        )
    R_t = relationship_updater.get_state().to_array()

    # 3. Instantiate EmotionCore without auto-restore
    stimulus_processor = StimulusProcessor(config.to_stimulus_config())
    emotion_core = EmotionCore(
        config.to_emotion_config(),
        storage_path=dyn_path,
        auto_restore=False,
    )

    # 4. Inject authoritative relational context BEFORE downtime recovery
    emotion_core.update_relationship_context(R_t)

    # 5. Restore dynamical checkpoint & apply two-stage hybrid recovery
    emotion_core.restore_from_checkpoint(apply_elapsed_time=True)

    # 6. Reconstruct working memory context from chat_history.json
    initial_history: List[Tuple[str, str]] = []
    if chat_history_path is not None:
        c_path = Path(chat_history_path)
        if c_path.exists():
            try:
                c_store = ChatHistoryStore(file_path=str(c_path))
                k_turns = getattr(config, "context_history_turns", 10)
                recent = c_store.get_history(limit=k_turns * 2)
                for t in recent:
                    initial_history.append((str(t.get("role", "user")), str(t.get("content", ""))))
            except Exception as e:
                logger.warning("CognitiveOrchestrator: failed to reseed working history: %s", e)

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
        temporal_coordinator=temporal_coordinator,
        system_preamble=config.system_preamble,
        n_ctx=config.n_ctx,
        max_history_turns=config.max_history_turns,
        fallback_response=config.fallback_response,
        epoch_manifest_path=man_path,
        initial_history=initial_history,
        semantic_gate=semantic_gate,
        execution_tracer=execution_tracer,
    )
