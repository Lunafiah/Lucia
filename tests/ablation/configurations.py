"""
Lucia Ablation Test v1 — Configuration Adapters.

Implements the primary experimental matrix adapters:
  - Configuration A: Plain LLM (Zero state, zero memory, default prompt)
  - Configuration B: LLM + Conversation Memory (Sliding window history K=3)
  - Configuration C: LLM + Prompted Emotion (Static emotional prompt, K=3 history)
  - Configuration D: Full Lucia (Phase 9 CognitiveOrchestrator, complete causal architecture)
  - Configuration E: L1-L5 Without LLM (Zero-computation sentinel L6, real limbic/memory core)

CRITICAL INVARIANT:
These adapters are strictly isolated in tests/ablation/ and do not mutate production
cognition files or live state stores (data/profile.json, data/chat_history.json).
"""

from __future__ import annotations

import hashlib
import logging
import time
import uuid
from dataclasses import asdict, dataclass
from typing import Any, Dict, List, Optional, Tuple

import numpy as np

from src.core.config import (
    HomeostaticConfig,
    MemoryOrchestratorConfig,
    StimulusConfig,
)
from src.core.emotion.emotion_core import EmotionConfig, EmotionCore
from src.core.emotion.homeostatic_engine import HomeostaticEngine
from src.core.gating.stimulus_processor import StimulusProcessor
from src.core.inference.active_inference import ActiveInferenceConfig, ActiveInferenceEngine
from src.core.inference.lnn_trainer import LNNTrainer, LNNTrainerConfig
from src.core.language.llm_backend import LLMBackend
from src.core.memory.affective_memory import AffectiveMemory
from src.core.memory.decay import DecayEngine
from src.core.memory.ecphory import EcphoryEngine
from src.core.models import BehavioralConstraints, PADState, SomaticMarkers
from src.core.orchestrator.cognitive_orchestrator import CognitiveOrchestrator
from src.core.orchestrator.policies import (
    CognitiveTurnResult,
    GenerationPolicy,
    PlasticityPolicy,
    SurpriseModulationPolicy,
)
from src.core.orchestrator.prompt_assembler import PromptAssembler
from src.core.safety.boundary_layer import BoundaryLayer

logger = logging.getLogger(__name__)


# ---------------------------------------------------------------------------
# Telemetry Data Record
# ---------------------------------------------------------------------------

@dataclass
class TurnTelemetry:
    """Complete, reproducible record of a single experimental turn."""

    call_id: str
    configuration: str
    scenario: str
    turn_index: int
    seed: int
    timestamp: float

    # Inputs & Outputs
    input_text: str
    prompt: str
    prompt_hash: str
    prompt_tokens: int
    system_tokens: int
    history_tokens: int
    response_text: str
    response_hash: str
    generated_tokens: int
    latency_s: float

    # Generation Constraints
    temperature: float
    max_tokens: int
    reasoning_depth: int
    generation_mode: str

    # Limbic & Homeostasis Telemetry
    prior_pad: Optional[Tuple[float, float, float]]
    post_pad: Optional[Tuple[float, float, float]]
    pad_distance: float
    surprise: float
    somatic_stability: Optional[float]
    somatic_cognitive_load: Optional[float]
    somatic_energy: Optional[float]
    somatic_tension: Optional[float]

    # Memory & Plasticity Telemetry
    echo_vector_norm: float
    trace_stored: bool
    experience_queued: bool

    # Status
    success: bool
    error_msg: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


# ---------------------------------------------------------------------------
# Backend Wrappers
# ---------------------------------------------------------------------------

class SharedLLMBackendWrapper:
    """
    Wraps an active LLMBackend instance to prevent premature shutdown
    during orchestrator resets across trials.
    """

    def __init__(self, real_backend: Any) -> None:
        self._real_backend = real_backend

    @property
    def _llm(self) -> Any:
        return getattr(self._real_backend, "_llm", None)

    @property
    def _config(self) -> Any:
        return getattr(self._real_backend, "_config", None)

    def generate(
        self, prompt: str, constraints: Optional[BehavioralConstraints] = None
    ) -> Optional[str]:
        return self._real_backend.generate(prompt, constraints)

    def is_ready(self) -> bool:
        return self._real_backend.is_ready()

    def shutdown(self) -> None:
        # Intercepted: keep underlying backend alive until full experiment completes
        pass

    def close_underlying(self) -> None:
        if hasattr(self._real_backend, "shutdown"):
            self._real_backend.shutdown()


class SentinelLLMBackend:
    """
    Zero-computation sentinel backend for Configuration E (No-LLM).
    Returns instantly with a fixed sentinel token and zero computational delay.
    """

    def __init__(self) -> None:
        self._ready = True

    def generate(
        self, prompt: str, constraints: Optional[BehavioralConstraints] = None
    ) -> Optional[str]:
        return "[NO_LLM_SENTINEL]"

    def is_ready(self) -> bool:
        return True

    def shutdown(self) -> None:
        self._ready = False


# ---------------------------------------------------------------------------
# Utility Helpers
# ---------------------------------------------------------------------------

def sha256_text(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def count_tokens(backend: Any, text: str) -> int:
    """Exact token count via llama_cpp if available; fallback to len // 4."""
    if not text:
        return 0
    llm = getattr(backend, "_llm", None)
    if llm is not None and hasattr(llm, "tokenize"):
        try:
            return len(llm.tokenize(text.encode("utf-8")))
        except Exception:
            pass
    return max(1, len(text) // 4)


def apply_seed(backend: Any, seed: int) -> None:
    """Apply random seed to underlying llama_cpp instance if supported."""
    llm = getattr(backend, "_llm", None)
    if llm is not None and hasattr(llm, "set_seed"):
        try:
            llm.set_seed(seed)
        except Exception as e:
            logger.debug("set_seed failed: %s", e)


# ---------------------------------------------------------------------------
# Base Adapter
# ---------------------------------------------------------------------------

class BaseAblationAdapter:
    """Common interface for all ablation configurations."""

    def __init__(self, backend: Any, config_name: str) -> None:
        self.backend = backend
        self.config_name = config_name

    def step(
        self,
        input_text: str,
        turn_index: int,
        scenario_id: str,
        seed: int,
    ) -> TurnTelemetry:
        raise NotImplementedError

    def reset(self) -> None:
        pass

    def shutdown(self) -> None:
        pass


# ---------------------------------------------------------------------------
# Configuration A: Plain LLM
# ---------------------------------------------------------------------------

class PlainLLMAdapter(BaseAblationAdapter):
    """
    Configuration A — Plain LLM.
    No internal limbic state, no memory, zero history retained across turns.
    """

    def __init__(self, backend: Any) -> None:
        super().__init__(backend, "A_PlainLLM")
        self.system_prompt = "You are Lucia, a helpful assistant."

    def step(
        self,
        input_text: str,
        turn_index: int,
        scenario_id: str,
        seed: int,
    ) -> TurnTelemetry:
        call_id = uuid.uuid4().hex
        t_start = time.perf_counter()
        apply_seed(self.backend, seed)

        prompt = (
            f"{self.system_prompt}\n\n"
            f"[CONVERSATION]\n"
            f"user: {input_text}\n"
            f"assistant:"
        )
        constraints = BehavioralConstraints(
            max_tokens=512,
            temperature=0.7,
            reasoning_depth=0,
            latency_ms=0,
        )

        resp = self.backend.generate(prompt, constraints)
        latency = time.perf_counter() - t_start
        response_text = resp if resp is not None else "[GENERATION_FAILED]"

        p_tokens = count_tokens(self.backend, prompt)
        sys_tokens = count_tokens(self.backend, self.system_prompt)
        g_tokens = count_tokens(self.backend, response_text)

        return TurnTelemetry(
            call_id=call_id,
            configuration=self.config_name,
            scenario=scenario_id,
            turn_index=turn_index,
            seed=seed,
            timestamp=time.time(),
            input_text=input_text,
            prompt=prompt,
            prompt_hash=sha256_text(prompt),
            prompt_tokens=p_tokens,
            system_tokens=sys_tokens,
            history_tokens=0,
            response_text=response_text,
            response_hash=sha256_text(response_text),
            generated_tokens=g_tokens,
            latency_s=latency,
            temperature=0.7,
            max_tokens=512,
            reasoning_depth=0,
            generation_mode="reflexive",
            prior_pad=None,
            post_pad=None,
            pad_distance=0.0,
            surprise=0.0,
            somatic_stability=None,
            somatic_cognitive_load=None,
            somatic_energy=None,
            somatic_tension=None,
            echo_vector_norm=0.0,
            trace_stored=False,
            experience_queued=False,
            success=(resp is not None),
        )

    def reset(self) -> None:
        pass


# ---------------------------------------------------------------------------
# Configuration B: LLM + Conversation Memory
# ---------------------------------------------------------------------------

class MemoryLLMAdapter(BaseAblationAdapter):
    """
    Configuration B — LLM + Conversation Memory.
    Maintains a sliding window of recent conversation turns (K=3 user-assistant pairs).
    No internal limbic state, no affective memory.
    """

    def __init__(self, backend: Any, k_turns: int = 3) -> None:
        super().__init__(backend, "B_MemoryLLM")
        self.system_prompt = "You are Lucia, a helpful assistant."
        self.k_turns = k_turns
        self.history: List[Tuple[str, str]] = []

    def step(
        self,
        input_text: str,
        turn_index: int,
        scenario_id: str,
        seed: int,
    ) -> TurnTelemetry:
        call_id = uuid.uuid4().hex
        t_start = time.perf_counter()
        apply_seed(self.backend, seed)

        # Build sliding window history: keep at most k_turns pairs
        active_history = self.history[-self.k_turns:]
        hist_lines = []
        for u, a in active_history:
            hist_lines.append(f"user: {u}")
            hist_lines.append(f"assistant: {a}")
        hist_str = "\n".join(hist_lines) if hist_lines else "(no history)"

        prompt = (
            f"{self.system_prompt}\n\n"
            f"[CONVERSATION]\n"
            f"{hist_str}\n"
            f"user: {input_text}\n"
            f"assistant:"
        )
        constraints = BehavioralConstraints(
            max_tokens=512,
            temperature=0.7,
            reasoning_depth=0,
            latency_ms=0,
        )

        resp = self.backend.generate(prompt, constraints)
        latency = time.perf_counter() - t_start
        if resp is not None:
            # Truncate any multi-turn hallucinated continuation generated by small SLM
            cleaned = resp.split("\nuser:")[0].split("\nUser:")[0].split("\n[CONVERSATION]")[0].strip()
            response_text = cleaned if cleaned else resp.strip()
            self.history.append((input_text, response_text))
        else:
            response_text = "[GENERATION_FAILED]"

        p_tokens = count_tokens(self.backend, prompt)
        sys_tokens = count_tokens(self.backend, self.system_prompt)
        hist_tokens = count_tokens(self.backend, hist_str)
        g_tokens = count_tokens(self.backend, response_text)

        return TurnTelemetry(
            call_id=call_id,
            configuration=self.config_name,
            scenario=scenario_id,
            turn_index=turn_index,
            seed=seed,
            timestamp=time.time(),
            input_text=input_text,
            prompt=prompt,
            prompt_hash=sha256_text(prompt),
            prompt_tokens=p_tokens,
            system_tokens=sys_tokens,
            history_tokens=hist_tokens,
            response_text=response_text,
            response_hash=sha256_text(response_text),
            generated_tokens=g_tokens,
            latency_s=latency,
            temperature=0.7,
            max_tokens=512,
            reasoning_depth=0,
            generation_mode="reflexive",
            prior_pad=None,
            post_pad=None,
            pad_distance=0.0,
            surprise=0.0,
            somatic_stability=None,
            somatic_cognitive_load=None,
            somatic_energy=None,
            somatic_tension=None,
            echo_vector_norm=0.0,
            trace_stored=False,
            experience_queued=False,
            success=(resp is not None),
        )

    def reset(self) -> None:
        self.history.clear()


# ---------------------------------------------------------------------------
# Configuration C: LLM + Prompted Emotion
# ---------------------------------------------------------------------------

class PromptedEmotionAdapter(BaseAblationAdapter):
    """
    Configuration C — LLM + Prompted Emotion.
    Static emotional context label injected into system prompt.
    Maintains sliding window history (K=3). No dynamic ODE limbic model.
    """

    def __init__(self, backend: Any, k_turns: int = 3) -> None:
        super().__init__(backend, "C_PromptedEmotion")
        self.system_prompt = (
            "You are Lucia, a helpful assistant.\n"
            "[EMOTIONAL CONTEXT]\n"
            "Status: Calm, attentive, composed\n"
            "Affect: Neutral-positive baseline"
        )
        self.k_turns = k_turns
        self.history: List[Tuple[str, str]] = []

    def step(
        self,
        input_text: str,
        turn_index: int,
        scenario_id: str,
        seed: int,
    ) -> TurnTelemetry:
        call_id = uuid.uuid4().hex
        t_start = time.perf_counter()
        apply_seed(self.backend, seed)

        active_history = self.history[-self.k_turns:]
        hist_lines = []
        for u, a in active_history:
            hist_lines.append(f"user: {u}")
            hist_lines.append(f"assistant: {a}")
        hist_str = "\n".join(hist_lines) if hist_lines else "(no history)"

        prompt = (
            f"{self.system_prompt}\n\n"
            f"[CONVERSATION]\n"
            f"{hist_str}\n"
            f"user: {input_text}\n"
            f"assistant:"
        )
        constraints = BehavioralConstraints(
            max_tokens=512,
            temperature=0.7,
            reasoning_depth=0,
            latency_ms=0,
        )

        resp = self.backend.generate(prompt, constraints)
        latency = time.perf_counter() - t_start
        if resp is not None:
            # Truncate any multi-turn hallucinated continuation generated by small SLM
            cleaned = resp.split("\nuser:")[0].split("\nUser:")[0].split("\n[CONVERSATION]")[0].strip()
            response_text = cleaned if cleaned else resp.strip()
            self.history.append((input_text, response_text))
        else:
            response_text = "[GENERATION_FAILED]"

        p_tokens = count_tokens(self.backend, prompt)
        sys_tokens = count_tokens(self.backend, self.system_prompt)
        hist_tokens = count_tokens(self.backend, hist_str)
        g_tokens = count_tokens(self.backend, response_text)

        return TurnTelemetry(
            call_id=call_id,
            configuration=self.config_name,
            scenario=scenario_id,
            turn_index=turn_index,
            seed=seed,
            timestamp=time.time(),
            input_text=input_text,
            prompt=prompt,
            prompt_hash=sha256_text(prompt),
            prompt_tokens=p_tokens,
            system_tokens=sys_tokens,
            history_tokens=hist_tokens,
            response_text=response_text,
            response_hash=sha256_text(response_text),
            generated_tokens=g_tokens,
            latency_s=latency,
            temperature=0.7,
            max_tokens=512,
            reasoning_depth=0,
            generation_mode="reflexive",
            prior_pad=None,
            post_pad=None,
            pad_distance=0.0,
            surprise=0.0,
            somatic_stability=None,
            somatic_cognitive_load=None,
            somatic_energy=None,
            somatic_tension=None,
            echo_vector_norm=0.0,
            trace_stored=False,
            experience_queued=False,
            success=(resp is not None),
        )

    def reset(self) -> None:
        self.history.clear()


# ---------------------------------------------------------------------------
# Configuration D: Full Lucia
# ---------------------------------------------------------------------------

class FullLuciaAdapter(BaseAblationAdapter):
    """
    Configuration D — Full Lucia Whole-Brain Architecture (Phase 9).
    Continuous LNN ODE, Active Inference, Homeostatic modulation,
    Affective Ecphory, and dynamic generation policy.
    """

    def __init__(
        self,
        backend: Any,
        max_history_turns: int = 3,
    ) -> None:
        super().__init__(backend, "D_FullLucia")
        self.max_history_turns = max_history_turns
        self.orchestrator = self._build_orchestrator(backend, max_history_turns)

    def _build_orchestrator(
        self, backend: Any, max_history_turns: int
    ) -> CognitiveOrchestrator:
        mem_cfg = MemoryOrchestratorConfig(
            model_path="dummy/model.gguf",  # Backend is injected directly
            sdm_num_locations=1000,
            sdm_address_dim=1000,
            sdm_content_dim=64,
            max_history_turns=max_history_turns,
        )
        stimulus_processor = StimulusProcessor(mem_cfg.to_stimulus_config())
        emotion_core = EmotionCore(mem_cfg.to_emotion_config())
        homeostatic_engine = HomeostaticEngine(HomeostaticConfig())
        active_inference = ActiveInferenceEngine(ActiveInferenceConfig())
        affective_memory = AffectiveMemory(mem_cfg.to_affective_memory_config())
        decay_engine = DecayEngine(affective_memory, mem_cfg.to_decay_config())
        ecphory_engine = EcphoryEngine(mem_cfg.to_ecphory_config())
        prompt_assembler = PromptAssembler()
        boundary_layer = BoundaryLayer(mem_cfg.to_boundary_config())

        lnn_trainer: Optional[LNNTrainer] = None
        try:
            lnn_trainer = LNNTrainer(
                emotion_core=emotion_core,
                config=LNNTrainerConfig(batch_size=16),
            )
        except Exception:
            pass

        return CognitiveOrchestrator(
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
            lnn_trainer=lnn_trainer,
            surprise_policy=SurpriseModulationPolicy(),
            plasticity_policy=PlasticityPolicy(),
            system_preamble="You are Lucia, a helpful assistant.",
            n_ctx=4096,
            max_history_turns=max_history_turns,
            fallback_response="...",
        )

    def step(
        self,
        input_text: str,
        turn_index: int,
        scenario_id: str,
        seed: int,
    ) -> TurnTelemetry:
        apply_seed(self.backend, seed)
        result: CognitiveTurnResult = self.orchestrator.process(input_text)

        p_init = (
            result.pad_initial.pleasure,
            result.pad_initial.arousal,
            result.pad_initial.dominance,
        )
        p_final = (
            result.pad_final.pleasure,
            result.pad_final.arousal,
            result.pad_final.dominance,
        )
        pad_dist = float(
            np.linalg.norm(np.array(p_final) - np.array(p_init))
        )
        echo_norm = (
            float(np.linalg.norm(result.echo_vector))
            if result.echo_vector is not None
            else 0.0
        )

        # Assemble prompt to obtain exact text and token breakdown
        prompt_str = self.orchestrator._prompt_assembler.assemble(
            somatic=result.somatic,
            constraints=result.constraints,
            history=self.orchestrator._history[:-2] if len(self.orchestrator._history) >= 2 else [],
            system_preamble=self.orchestrator._system_preamble,
            n_ctx=self.orchestrator._n_ctx,
            echo_vector=result.echo_vector,
        )
        if isinstance(prompt_str, Exception):
            prompt_str = "[PROMPT_ASSEMBLY_ERROR]"

        p_tokens = count_tokens(self.backend, prompt_str)
        sys_tokens = count_tokens(self.backend, self.orchestrator._system_preamble)
        g_tokens = count_tokens(self.backend, result.response_text)

        return TurnTelemetry(
            call_id=result.call_id,
            configuration=self.config_name,
            scenario=scenario_id,
            turn_index=turn_index,
            seed=seed,
            timestamp=time.time(),
            input_text=input_text,
            prompt=prompt_str,
            prompt_hash=sha256_text(prompt_str),
            prompt_tokens=p_tokens,
            system_tokens=sys_tokens,
            history_tokens=max(0, p_tokens - sys_tokens),
            response_text=result.response_text,
            response_hash=sha256_text(result.response_text),
            generated_tokens=g_tokens,
            latency_s=result.execution_time_s,
            temperature=result.constraints.temperature or 0.7,
            max_tokens=result.constraints.max_tokens or 512,
            reasoning_depth=result.constraints.reasoning_depth,
            generation_mode=result.generation_policy.mode,
            prior_pad=p_init,
            post_pad=p_final,
            pad_distance=pad_dist,
            surprise=float(result.prediction_error),
            somatic_stability=float(result.somatic.stability),
            somatic_cognitive_load=float(result.somatic.cognitive_load),
            somatic_energy=float(result.somatic.energy),
            somatic_tension=float(result.somatic.tension),
            echo_vector_norm=echo_norm,
            trace_stored=result.trace_stored,
            experience_queued=result.experience_queued,
            success=(result.response_text != "..."),
        )

    def reset(self) -> None:
        self.orchestrator.reset_lifecycle()

    def shutdown(self) -> None:
        self.orchestrator.shutdown()


# ---------------------------------------------------------------------------
# Configuration E: L1-L5 Without LLM
# ---------------------------------------------------------------------------

class NoLLMAdapter(BaseAblationAdapter):
    """
    Configuration E — L1-L5 Without Language Organ (No-LLM).
    Executes the full 10-stage causal pipeline with L6 replaced by
    a zero-computation sentinel backend. Tests cognitive independence.
    """

    def __init__(self, max_history_turns: int = 3) -> None:
        sentinel_backend = SentinelLLMBackend()
        super().__init__(sentinel_backend, "E_NoLLM")
        self.orchestrator = self._build_orchestrator(sentinel_backend, max_history_turns)

    def _build_orchestrator(
        self, backend: Any, max_history_turns: int
    ) -> CognitiveOrchestrator:
        mem_cfg = MemoryOrchestratorConfig(
            model_path="dummy/model.gguf",
            sdm_num_locations=1000,
            sdm_address_dim=1000,
            sdm_content_dim=64,
            max_history_turns=max_history_turns,
        )
        stimulus_processor = StimulusProcessor(mem_cfg.to_stimulus_config())
        emotion_core = EmotionCore(mem_cfg.to_emotion_config())
        homeostatic_engine = HomeostaticEngine(HomeostaticConfig())
        active_inference = ActiveInferenceEngine(ActiveInferenceConfig())
        affective_memory = AffectiveMemory(mem_cfg.to_affective_memory_config())
        decay_engine = DecayEngine(affective_memory, mem_cfg.to_decay_config())
        ecphory_engine = EcphoryEngine(mem_cfg.to_ecphory_config())
        prompt_assembler = PromptAssembler()
        boundary_layer = BoundaryLayer(mem_cfg.to_boundary_config())

        lnn_trainer: Optional[LNNTrainer] = None
        try:
            lnn_trainer = LNNTrainer(
                emotion_core=emotion_core,
                config=LNNTrainerConfig(batch_size=16),
            )
        except Exception:
            pass

        return CognitiveOrchestrator(
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
            lnn_trainer=lnn_trainer,
            surprise_policy=SurpriseModulationPolicy(),
            plasticity_policy=PlasticityPolicy(),
            system_preamble="You are Lucia, a helpful assistant.",
            n_ctx=4096,
            max_history_turns=max_history_turns,
            fallback_response="[NO_LLM_SENTINEL]",
        )

    def step(
        self,
        input_text: str,
        turn_index: int,
        scenario_id: str,
        seed: int,
    ) -> TurnTelemetry:
        result: CognitiveTurnResult = self.orchestrator.process(input_text)

        p_init = (
            result.pad_initial.pleasure,
            result.pad_initial.arousal,
            result.pad_initial.dominance,
        )
        p_final = (
            result.pad_final.pleasure,
            result.pad_final.arousal,
            result.pad_final.dominance,
        )
        pad_dist = float(
            np.linalg.norm(np.array(p_final) - np.array(p_init))
        )
        echo_norm = (
            float(np.linalg.norm(result.echo_vector))
            if result.echo_vector is not None
            else 0.0
        )

        # Allow physical time for EmotionCore's 200ms Fast Loop ODE thread to integrate
        # between conversational turns (matching real-time conversational passage of time)
        time.sleep(0.25)

        return TurnTelemetry(
            call_id=result.call_id,
            configuration=self.config_name,
            scenario=scenario_id,
            turn_index=turn_index,
            seed=seed,
            timestamp=time.time(),
            input_text=input_text,
            prompt="[NO_LLM_SENTINEL]",
            prompt_hash=sha256_text("[NO_LLM_SENTINEL]"),
            prompt_tokens=0,
            system_tokens=0,
            history_tokens=0,
            response_text="[NO_LLM_SENTINEL]",
            response_hash=sha256_text("[NO_LLM_SENTINEL]"),
            generated_tokens=0,
            latency_s=result.execution_time_s,
            temperature=result.constraints.temperature or 0.7,
            max_tokens=result.constraints.max_tokens or 512,
            reasoning_depth=result.constraints.reasoning_depth,
            generation_mode=result.generation_policy.mode,
            prior_pad=p_init,
            post_pad=p_final,
            pad_distance=pad_dist,
            surprise=float(result.prediction_error),
            somatic_stability=float(result.somatic.stability),
            somatic_cognitive_load=float(result.somatic.cognitive_load),
            somatic_energy=float(result.somatic.energy),
            somatic_tension=float(result.somatic.tension),
            echo_vector_norm=echo_norm,
            trace_stored=result.trace_stored,
            experience_queued=result.experience_queued,
            success=True,
        )

    def reset(self) -> None:
        self.orchestrator.reset_lifecycle()

    def shutdown(self) -> None:
        self.orchestrator.shutdown()
