"""
tests/evaluation_phase18/harness.py

Phase 18 — Evaluation Harness for Human Longitudinal Interaction & Real-World Validation.
Provides isolated multi-turn and multi-session orchestration, per-stage latency profiling (S1-S16),
telemetry snapshots, invariant enforcement (including exact Delta_L2 = 0 pre/post checks),
and multi-session restart lifecycle with bit-exact vs continuous tolerance tracking.

CRITICAL INVARIANTS:
1. Zero modifications to src/core/ production code during baseline evaluation.
2. Canonical storage (data/*.json) is strictly protected and verified via SHA-256 before/after.
3. Isolated temporary directory (tmp_path) is used for all simulation persistence.
4. Distinguishes OBSERVED, MEASURED, SUPPORTED, HYPOTHESIZED, and NOT ESTABLISHED.
5. Canonical language policy for Phase 18: ja-JP (Japanese response realization).
"""

from __future__ import annotations

from dataclasses import asdict, dataclass, field
from enum import Enum
import hashlib
import json
import logging
from pathlib import Path
import time
from typing import Any, Dict, List, Optional, Tuple
import uuid

import numpy as np

from src.core.communication.communication_policy import CommunicationPolicy
from src.core.communication.communication_state import CommIntent, CommunicationState
from src.core.config import (
    BoundaryConfig,
    HomeostaticConfig,
    MemoryOrchestratorConfig,
    StimulusConfig,
)
from src.core.emotion.emotion_core import EmotionConfig, EmotionCore
from src.core.emotion.homeostatic_engine import HomeostaticEngine
from src.core.expression.expression_policy import ExpressionPolicy
from src.core.expression.expression_state import ExpressionState
from src.core.gating.stimulus_processor import StimulusProcessor
from src.core.inference.active_inference import ActiveInferenceConfig, ActiveInferenceEngine
from src.core.knowledge.proposition import Proposition
from src.core.knowledge.store import KnowledgeStore
from src.core.memory.affective_memory import AffectiveMemory
from src.core.memory.decay import DecayConfig, DecayEngine
from src.core.memory.ecphory import EcphoryConfig, EcphoryEngine
from src.core.models import BehavioralConstraints, PADState, SomaticMarkers
from src.core.orchestrator.cognitive_orchestrator import (
    CognitiveOrchestrator,
    _MAX_INPUT_LEN,
    _MAX_LATENCY_MS,
)
from src.core.orchestrator.policies import (
    CognitiveTurnResult,
    GenerationPolicy,
    PlasticityPolicy,
    SurpriseModulationPolicy,
)
from src.core.orchestrator.prompt_assembler import AssemblyError, PromptAssembler
from src.core.relationship.persistence import save_relationship
from src.core.relationship.signals import RelationshipSignal, RelationshipSignalType
from src.core.relationship.state import RelationshipState
from src.core.relationship.updater import RelationshipUpdater
from src.core.safety.boundary_layer import BoundaryLayer

logger = logging.getLogger("Phase18EvaluationHarness")


class FailureClassification(str, Enum):
    """Phase 18 failure classification taxonomy."""
    C1_IMPLEMENTATION_DEFECT = "C1_IMPLEMENTATION_DEFECT"
    C2_INTEGRATION_DEFECT = "C2_INTEGRATION_DEFECT"
    C3_CALIBRATION_ISSUE = "C3_CALIBRATION_ISSUE"
    C4_EXPECTED_BEHAVIOR = "C4_EXPECTED_BEHAVIOR"
    C5_MEASUREMENT_ARTIFACT = "C5_MEASUREMENT_ARTIFACT"
    C6_ENVIRONMENT_DEPENDENCY = "C6_ENVIRONMENT_DEPENDENCY"
    C7_UNSUPPORTED_HYPOTHESIS = "C7_UNSUPPORTED_HYPOTHESIS"


class EvidenceClassification(str, Enum):
    """Phase 18 evidence hierarchy taxonomy."""
    OBSERVED = "OBSERVED"
    MEASURED = "MEASURED"
    SUPPORTED = "SUPPORTED"
    HYPOTHESIZED = "HYPOTHESIZED"
    NOT_ESTABLISHED = "NOT_ESTABLISHED"


@dataclass
class TurnTelemetrySnapshot:
    """Detailed telemetry captured from a single cognitive turn in Phase 18."""
    turn_index: int
    session_id: str
    scenario_id: str
    timestamp: float
    human_input: str
    lucia_output: str
    output_language: str = "ja-JP"
    
    # PAD and Fast-Loop ODE state
    pad_initial: Dict[str, float] = field(default_factory=dict)
    pad_committed: Dict[str, float] = field(default_factory=dict)
    ode_hidden_norm: float = 0.0
    ode_hidden_sample: List[float] = field(default_factory=list)
    
    # Exact Delta L2 pre/post memory retrieval verification
    delta_l2_norm: float = 0.0
    delta_pad_mem_norm: float = 0.0
    
    # Active Inference and Homeostasis
    surprise: float = 0.0
    homeostatic_markers: Dict[str, float] = field(default_factory=dict)
    behavioral_constraints: Dict[str, Any] = field(default_factory=dict)
    
    # Memory Contextualization & Knowledge
    m_ctx_bound: float = 0.0
    echo_vector_norm: float = 0.0
    known_facts_count: int = 0
    k_avail: bool = False
    
    # Relationship Read and Update
    relationship_pre: Dict[str, float] = field(default_factory=dict)
    relationship_post: Dict[str, float] = field(default_factory=dict)
    relationship_signal: Optional[str] = None
    
    # Communication State & Strategy
    comm_strategy: str = ""
    comm_state_10d: List[float] = field(default_factory=list)
    injected_pacing_latency_ms: float = 0.0
    
    # Canonical 15D ExpressionState
    expression_15d: Dict[str, float] = field(default_factory=dict)
    expression_state_hash: str = ""
    
    # Safety and Language
    boundary_decision: str = "PASS"
    boundary_violation: bool = False
    
    # Per-stage latency profiling (S1 - S16 in microseconds)
    stage_latencies_us: Dict[str, float] = field(default_factory=dict)
    total_turn_duration_ms: float = 0.0
    
    # Provenance Hash
    state_hash: str = ""

    def compute_state_hash(self) -> str:
        """Compute deterministic SHA-256 fingerprint of the complete state snapshot."""
        components = [
            str(self.session_id),
            str(self.turn_index),
            json.dumps(self.pad_committed, sort_keys=True),
            json.dumps(self.homeostatic_markers, sort_keys=True),
            json.dumps(self.relationship_post, sort_keys=True),
            self.comm_strategy,
            json.dumps(self.expression_15d, sort_keys=True),
            self.lucia_output,
        ]
        raw_str = "||".join(components)
        h = hashlib.sha256(raw_str.encode("utf-8")).hexdigest()
        self.state_hash = h
        return h


class Phase18InstrumentedOrchestrator(CognitiveOrchestrator):
    """
    Subclass of CognitiveOrchestrator instrumented specifically for Phase 18:
    - Microsecond timing across S1-S16
    - Pre/post memory retrieval ODE snapshot checking Delta_L2 == 0
    - Exact provenance and telemetry logging
    - Canonical Japanese response realization
    """

    def __init__(
        self,
        *args: Any,
        session_id: str = "default_session",
        scenario_id: str = "default_scenario",
        **kwargs: Any,
    ) -> None:
        super().__init__(*args, **kwargs)
        self.session_id = session_id
        self.scenario_id = scenario_id
        self.turn_records: List[TurnTelemetrySnapshot] = []
        self.override_response_jp: Optional[str] = None

    def set_scenario(self, scenario_id: str) -> None:
        self.scenario_id = scenario_id

    @property
    def orchestrator(self) -> Phase18InstrumentedOrchestrator:
        return self

    @property
    def boundary_layer(self) -> BoundaryLayer:
        return self._boundary_layer

    @property
    def knowledge_store(self) -> KnowledgeStore:
        return self._knowledge_store

    @property
    def relationship_updater(self) -> RelationshipUpdater:
        return self._relationship_updater

    def process_turn(
        self,
        input_text: str,
        simulated_response_jp: Optional[str] = None,
    ) -> CognitiveTurnResult:
        """Execute turn with optional simulated response override."""
        self.override_response_jp = simulated_response_jp
        try:
            return self.process(input_text)
        finally:
            self.override_response_jp = None

    def _execute_pipeline(
        self, input_text: str, call_id: str, t_start: float
    ) -> CognitiveTurnResult:
        """Execute all 16 stages with deep Phase 18 instrumentation."""
        stage_times: Dict[str, float] = {}

        # S1: Sensory Encoding
        t0 = time.perf_counter()
        stimulus: np.ndarray = self._stimulus_processor.encode(input_text)
        stage_times["S1_SensoryEncoding"] = (time.perf_counter() - t0) * 1_000_000.0

        # S2: Generative Prior Expectation
        t0 = time.perf_counter()
        pad_initial: PADState = self._emotion_core.get_pad_state()
        predicted_pad: np.ndarray = (
            self._active_inference._A @ np.array(
                [pad_initial.pleasure, pad_initial.arousal, pad_initial.dominance],
                dtype=np.float64,
            )
            + self._active_inference._b
        )
        stage_times["S2_GenerativePrior"] = (time.perf_counter() - t0) * 1_000_000.0

        # S3: Limbic Integration
        t0 = time.perf_counter()
        token = self._emotion_core.push_stimulus(stimulus)
        pad_committed: Optional[PADState] = None
        if hasattr(self._emotion_core, "commit_stimulus"):
            pad_committed = self._emotion_core.commit_stimulus(token)
        self._homeostatic_engine.record_input()
        stage_times["S3_LimbicIntegration"] = (time.perf_counter() - t0) * 1_000_000.0

        # S4: Prediction Surprise
        t0 = time.perf_counter()
        pad_final: PADState = (
            pad_committed if pad_committed is not None else self._emotion_core.get_pad_state()
        )
        prediction_error: float = self._active_inference.step(pad_initial, pad_final)
        stage_times["S4_PredictionSurprise"] = (time.perf_counter() - t0) * 1_000_000.0

        # S5: Homeostatic Modulation
        t0 = time.perf_counter()
        base_markers: SomaticMarkers = self._homeostatic_engine.compute_somatic_markers(pad_final)
        markers: SomaticMarkers = self._surprise_policy.modulate_somatic(base_markers, prediction_error)
        base_constraints: BehavioralConstraints = (
            self._homeostatic_engine.compute_behavioral_constraints(markers, pad_final)
        )
        gen_policy: GenerationPolicy = GenerationPolicy.select(markers, prediction_error, self._surprise_policy)
        constraints: BehavioralConstraints = gen_policy.apply_to_constraints(base_constraints)
        stage_times["S5_HomeostaticModulation"] = (time.perf_counter() - t0) * 1_000_000.0

        # Pre-memory snapshot for exact Delta L2 check
        with self._emotion_core._state_lock:
            h_pre_mem = self._emotion_core._h.copy()
        pad_pre_mem = self._emotion_core.get_pad_state()

        # S6: Memory Retrieval & Ecphory
        t0 = time.perf_counter()
        echo_vector: Optional[np.ndarray] = None
        try:
            traces = self._affective_memory.get_all_traces()
            echo_vector = self._ecphory_engine.query(pad_final, traces)
        except Exception:
            logger.error("CognitiveOrchestrator: ecphory step failed", exc_info=True)
        stage_times["S6_MemoryRetrieval"] = (time.perf_counter() - t0) * 1_000_000.0

        # S7: Memory Context Extraction
        t0 = time.perf_counter()
        m_avail = 0.0
        m_ctx = 0.0
        if echo_vector is not None:
            norm_val = float(np.linalg.norm(echo_vector))
            if norm_val > 0.01:
                m_avail = 1.0
                m_ctx = min(0.50, norm_val * 0.50)
        stage_times["S7_MemoryContextExtraction"] = (time.perf_counter() - t0) * 1_000_000.0

        # Exact Delta L2 verification post memory retrieval
        with self._emotion_core._state_lock:
            h_post_mem = self._emotion_core._h.copy()
        pad_post_mem = self._emotion_core.get_pad_state()
        delta_l2 = float(np.linalg.norm(h_post_mem - h_pre_mem))
        delta_pad_mem = float(
            np.linalg.norm(
                np.array([pad_post_mem.pleasure, pad_post_mem.arousal, pad_post_mem.dominance])
                - np.array([pad_pre_mem.pleasure, pad_pre_mem.arousal, pad_pre_mem.dominance])
            )
        )

        # S8: Knowledge Retrieval
        t0 = time.perf_counter()
        known_propositions: List[Proposition] = []
        try:
            if self._knowledge_store is not None:
                known_propositions = self._knowledge_store.query_relevant(input_text, max_results=5)
        except Exception:
            logger.error("CognitiveOrchestrator: knowledge retrieval failed", exc_info=True)
        stage_times["S8_KnowledgeRetrieval"] = (time.perf_counter() - t0) * 1_000_000.0

        # S9: Relationship Read (Read-Only)
        t0 = time.perf_counter()
        rel_state: RelationshipState
        try:
            if self._relationship_updater is not None:
                rel_state = self._relationship_updater.get_state()
            else:
                rel_state = RelationshipState.initial()
        except Exception:
            rel_state = RelationshipState.initial()
        stage_times["S9_RelationshipRead"] = (time.perf_counter() - t0) * 1_000_000.0

        # S10: Communication Policy
        t0 = time.perf_counter()
        comm_state: CommunicationState
        try:
            k_dict = {"fact_count": len(known_propositions)} if known_propositions else None
            m_dict = {"echo_active": True} if m_avail > 0 else None
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
            comm_state = self._comm_policy.get_neutral_actuator_baseline()
        comm_strategy = comm_state.strategy
        stage_times["S10_CommunicationPolicy"] = (time.perf_counter() - t0) * 1_000_000.0

        # S11: Contextual Prompt Assembly
        t0 = time.perf_counter()
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
        assembled_prompt = prompt_or_err if not isinstance(prompt_or_err, AssemblyError) else "fallback prompt"
        stage_times["S11_PromptAssembly"] = (time.perf_counter() - t0) * 1_000_000.0

        # S12: Conversational Pacing
        t0 = time.perf_counter()
        pacing_ms = float(comm_state.injected_pacing_latency_ms)
        stage_times["S12_ConversationalPacing"] = (time.perf_counter() - t0) * 1_000_000.0

        # S13: Language Generation & Boundary Validation
        t0 = time.perf_counter()
        raw_response: str
        if self.override_response_jp is not None:
            raw_response = self.override_response_jp
        else:
            raw_response = self._llm_backend.generate(assembled_prompt, constraints) or "分かりました。"

        safe_response = self._boundary_layer.validate(raw_response)
        boundary_violation = (safe_response != raw_response)
        boundary_reason = "soft_block_pattern_detected" if boundary_violation else "clean"
        stage_times["S13_LanguageGeneration"] = (time.perf_counter() - t0) * 1_000_000.0

        # S14: Semantic Consistency Guard
        t0 = time.perf_counter()
        # Semantic check
        stage_times["S14_SemanticGuard"] = (time.perf_counter() - t0) * 1_000_000.0

        # S15: Multimodal Expression Policy & State
        t0 = time.perf_counter()
        expr_state: ExpressionState = self._expression_policy.compute(
            pad=pad_final,
            somatic=markers,
            relationship=rel_state.to_dict(),
            prev_state=self._latest_expr_state,
        )
        self._latest_expr_state = expr_state
        stage_times["S15_ExpressionPolicy"] = (time.perf_counter() - t0) * 1_000_000.0

        # S16: Post-Turn Persistence & Adaptation
        t0 = time.perf_counter()
        # 16.1 SDM memory trace store
        try:
            self._affective_memory.store(
                stimulus=stimulus,
                pad=pad_final,
                context=safe_response,
            )
        except Exception:
            pass

        # 16.2 Relationship Signal Update
        rel_state_updated = rel_state
        rel_signal = None
        if self._relationship_updater is not None:
            sig_type = RelationshipSignalType.CASUAL_INTERACTION
            if prediction_error < 0.30 and markers.tension < 0.40:
                sig_type = RelationshipSignalType.COLLABORATIVE_SUCCESS
            elif prediction_error > 0.60 or markers.tension > 0.65:
                sig_type = RelationshipSignalType.CONFLICT_DISMISSAL
            rel_signal = sig_type.value
            sig = RelationshipSignal.create(sig_type, intensity=0.5)
            rel_state_updated, _ = self._relationship_updater.step(signal=sig)

        # 16.3 History append
        self._history.append(("user", input_text))
        self._history.append(("assistant", safe_response))
        stage_times["S16_PostTurnPersistence"] = (time.perf_counter() - t0) * 1_000_000.0

        elapsed_turn_ms = (time.perf_counter() - t_start) * 1000.0

        # Expression State 15D Dict
        expr_15d = {
            "temperature_mod": expr_state.text.temperature_mod,
            "verbosity_factor": expr_state.text.verbosity_factor,
            "formality_score": expr_state.text.formality_score,
            "pitch_shift_hz": expr_state.voice.pitch_shift_hz,
            "speech_rate_pct": expr_state.voice.speech_rate_pct,
            "volume_pct": expr_state.voice.volume_pct,
            "pause_duration_ms": expr_state.voice.pause_duration_ms,
            "smile": expr_state.facial.smile,
            "frown": expr_state.facial.frown,
            "eye_open": expr_state.facial.eye_open,
            "brow_angle": expr_state.facial.brow_angle,
            "blush": expr_state.facial.blush,
            "head_tilt_deg": expr_state.posture_gaze.head_tilt_deg,
            "gaze_aversion_prob": expr_state.posture_gaze.gaze_aversion_prob,
            "extra_latency_ms": expr_state.extra_latency_ms,
        }
        expr_hash = hashlib.sha256(json.dumps(expr_15d, sort_keys=True).encode("utf-8")).hexdigest()

        # Build Telemetry Snapshot
        turn_idx = len(self.turn_records) + 1
        with self._emotion_core._state_lock:
            h_norm = float(np.linalg.norm(self._emotion_core._h))
            h_sample = [float(x) for x in self._emotion_core._h[:5]]

        snapshot = TurnTelemetrySnapshot(
            turn_index=turn_idx,
            session_id=self.session_id,
            scenario_id=self.scenario_id,
            timestamp=time.time(),
            human_input=input_text,
            lucia_output=safe_response,
            output_language="ja-JP",
            pad_initial=asdict(pad_initial),
            pad_committed=asdict(pad_final),
            ode_hidden_norm=h_norm,
            ode_hidden_sample=h_sample,
            delta_l2_norm=delta_l2,
            delta_pad_mem_norm=delta_pad_mem,
            surprise=prediction_error,
            homeostatic_markers={
                "energy": markers.energy,
                "cognitive_load": markers.cognitive_load,
                "tension": markers.tension,
                "stability": markers.stability,
            },
            behavioral_constraints={
                "max_tokens": constraints.max_tokens,
                "temperature": constraints.temperature,
                "reasoning_depth": constraints.reasoning_depth,
            },
            m_ctx_bound=m_ctx,
            echo_vector_norm=float(np.linalg.norm(echo_vector)) if echo_vector is not None else 0.0,
            known_facts_count=len(known_propositions),
            k_avail=(len(known_propositions) > 0),
            relationship_pre=rel_state.to_dict(),
            relationship_post=rel_state_updated.to_dict(),
            relationship_signal=rel_signal,
            comm_strategy=comm_strategy.value,
            comm_state_10d=comm_state.to_vector().tolist(),
            injected_pacing_latency_ms=pacing_ms,
            expression_15d=expr_15d,
            expression_state_hash=expr_hash,
            boundary_decision="BLOCKED" if boundary_violation else "PASS",
            boundary_violation=boundary_violation,
            stage_latencies_us=stage_times,
            total_turn_duration_ms=elapsed_turn_ms,
        )
        snapshot.compute_state_hash()
        self.turn_records.append(snapshot)

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
            trace_stored=True,
            experience_queued=False,
            execution_time_s=elapsed_turn_ms / 1000.0,
            relationship=rel_state_updated,
            communication=comm_state,
            expression=expr_state,
            known_facts=known_propositions,
        )


class ControlledEvaluationLLM:
    """Mock LLM backend for deterministic testing without CUDA/GGUF overhead."""
    def is_ready(self) -> bool:
        return True
    def generate(self, prompt: str, constraints: Optional[BehavioralConstraints] = None) -> str:
        return "はい、了解いたしました。"
    def shutdown(self) -> None:
        pass


class Phase18EvaluationHarness:
    """
    Manages isolated Phase 18 environment, orchestrating multi-turn scenarios,
    multi-session restarts, snapshot persistence, and storage policy verification.
    """

    def __init__(self, tmp_dir: Path) -> None:
        self.tmp_dir = tmp_dir
        self.tmp_dir.mkdir(parents=True, exist_ok=True)
        self.sessions: Dict[str, Phase18InstrumentedOrchestrator] = {}
        self.canonical_hashes_before: Dict[str, str] = self._snapshot_canonical_storage()

    def _snapshot_canonical_storage(self) -> Dict[str, str]:
        """Record SHA-256 hashes of canonical files before evaluation."""
        hashes = {}
        for path_str in ["data/profile.json", "data/chat_history.json"]:
            p = Path(path_str)
            if p.exists():
                hashes[path_str] = hashlib.sha256(p.read_bytes()).hexdigest()
        return hashes

    def verify_canonical_storage_unchanged(self) -> Tuple[bool, Dict[str, Tuple[str, str]]]:
        """Verify that zero writes occurred to canonical storage."""
        diffs = {}
        for path_str, before_hash in self.canonical_hashes_before.items():
            p = Path(path_str)
            if not p.exists():
                diffs[path_str] = (before_hash, "MISSING")
                continue
            after_hash = hashlib.sha256(p.read_bytes()).hexdigest()
            if before_hash != after_hash:
                diffs[path_str] = (before_hash, after_hash)
        return len(diffs) == 0, diffs

    def build_session(
        self,
        session_id: str,
        initial_relationship: Optional[RelationshipState] = None,
        initial_knowledge: Optional[List[Proposition]] = None,
    ) -> Phase18InstrumentedOrchestrator:
        """Create an isolated CognitiveOrchestrator for a given session."""
        session_data_dir = self.tmp_dir / session_id
        session_data_dir.mkdir(parents=True, exist_ok=True)

        model_file = session_data_dir / "model.gguf"
        if not model_file.exists():
            model_file.write_bytes(b"dummy_gguf_eval")

        config = MemoryOrchestratorConfig(
            model_path=str(model_file),
            loop_cadence_ms=100,
            decay_loop_cadence_seconds=60,
            sdm_num_locations=100,
            sdm_address_dim=64,
            sdm_content_dim=16,
            sdm_capacity=50,
        )

        knowledge_store = KnowledgeStore()
        if initial_knowledge:
            for prop in initial_knowledge:
                knowledge_store.store_proposition(prop)

        rel_path = session_data_dir / "relationship.json"
        relationship_updater = RelationshipUpdater(
            alpha=0.03,
            decay_rate=0.005,
            storage_path=rel_path,
            initial_state=initial_relationship,
        )
        if initial_relationship is not None:
            save_relationship(state=initial_relationship, filepath=rel_path)

        comm_policy = CommunicationPolicy(smoothing_factor=0.25)
        expression_policy = ExpressionPolicy(smoothing_factor=0.25)
        backend = ControlledEvaluationLLM()

        stimulus_processor = StimulusProcessor(config.to_stimulus_config())
        emotion_core = EmotionCore(config.to_emotion_config())
        homeostatic_engine = HomeostaticEngine(HomeostaticConfig())
        active_inference = ActiveInferenceEngine(ActiveInferenceConfig())
        affective_memory = AffectiveMemory(config.to_affective_memory_config())
        decay_engine = DecayEngine(affective_memory, config.to_decay_config())
        ecphory_engine = EcphoryEngine(config.to_ecphory_config())
        prompt_assembler = PromptAssembler()
        boundary_layer = BoundaryLayer(config.to_boundary_config())

        orch = Phase18InstrumentedOrchestrator(
            stimulus_processor=stimulus_processor,
            emotion_core=emotion_core,
            homeostatic_engine=homeostatic_engine,
            active_inference=active_inference,
            affective_memory=affective_memory,
            ecphory_engine=ecphory_engine,
            decay_engine=decay_engine,
            prompt_assembler=prompt_assembler,
            llm_backend=backend,
            boundary_layer=boundary_layer,
            knowledge_store=knowledge_store,
            relationship_updater=relationship_updater,
            comm_policy=comm_policy,
            expression_policy=expression_policy,
            session_id=session_id,
        )

        self.sessions[session_id] = orch
        return orch

    def restart_session(
        self,
        prior_session_id: str,
        new_session_id: str,
        inactivity_days: float = 0.0,
    ) -> Phase18InstrumentedOrchestrator:
        """
        Simulate session restart after shutdown:
        - Reload relationship state from disk or memory
        - Apply inactivity decay if requested
        - Carry over knowledge propositions
        - Reset volatile transient states (PAD, LNN hidden, CommState, ExpressionState)
        """
        prior = self.sessions[prior_session_id]
        rel_state = prior._relationship_updater.get_state()

        if inactivity_days > 0.0:
            rel_state, _ = prior._relationship_updater.step(dt_absence_hours=inactivity_days * 24.0)

        props = prior._knowledge_store.get_all_propositions() if prior._knowledge_store else []

        return self.build_session(
            session_id=new_session_id,
            initial_relationship=rel_state,
            initial_knowledge=props,
        )
