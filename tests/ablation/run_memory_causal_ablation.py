"""
Lucia Memory-Affect Causal Ablation — Empirical Investigation of L2-L5 Coupling.

Evaluates whether affective memory retrieval (EcphoryEngine -> EchoVector)
causally alters internal mathematical dynamics (L2 PAD, L4 Surprise, L3 Homeostasis,
Policy) or operates strictly as a prompt-injection feature for the LLM.

Conditions:
  - Condition A: Full Memory (Encoding + Associative Retrieval Enabled)
  - Condition B: Counterfactual Control (Encoding Enabled, Retrieval Disabled)
  - Condition C: Blank Slate Control (Zero Prior Memory)

Hardware: Real Local GGUF on CUDA (RTX 3050 Ti Laptop GPU, 32 layers).
Safety: Strict SHA-256 verification of data/chat_history.json and data/profile.json.
Logs: tests/ablation/results/memory_causal_ablation.jsonl
"""

from __future__ import annotations

import hashlib
import json
import logging
import os
import sys
import time
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

import numpy as np

ROOT_DIR = Path(__file__).resolve().parent.parent.parent
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

from src.core.config import (
    HomeostaticConfig,
    LLMConfig,
    MemoryOrchestratorConfig,
    StimulusConfig,
)
from src.core.emotion.emotion_core import EmotionCore
from src.core.emotion.homeostatic_engine import HomeostaticEngine
from src.core.gating.stimulus_processor import StimulusProcessor
from src.core.inference.active_inference import ActiveInferenceConfig, ActiveInferenceEngine
from src.core.language.llm_backend import LLMBackend
from src.core.memory.affective_memory import AffectiveMemory, MemoryTrace
from src.core.memory.decay import DecayEngine
from src.core.memory.ecphory import EcphoryConfig, EcphoryEngine
from src.core.models import PADState
from src.core.orchestrator.cognitive_orchestrator import CognitiveOrchestrator
from src.core.orchestrator.policies import (
    CognitiveTurnResult,
    PlasticityPolicy,
    SurpriseModulationPolicy,
)
from src.core.orchestrator.prompt_assembler import PromptAssembler
from src.core.safety.boundary_layer import BoundaryLayer
from tests.ablation.configurations import SharedLLMBackendWrapper

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
)
logger = logging.getLogger("MemoryCausalAblation")

DEFAULT_MODEL_PATH = "models/LFM2.5-1.2B-Instruct-Q4_K_M.gguf"
DATA_CHAT_HISTORY = "data/chat_history.json"
DATA_PROFILE = "data/profile.json"
RESULTS_FILE = "tests/ablation/results/memory_causal_ablation.jsonl"
SEED = 43


def compute_file_sha256(path_str: str) -> str:
    path = Path(path_str)
    if not path.exists():
        return "FILE_NOT_FOUND"
    h = hashlib.sha256()
    with open(path, "rb") as f:
        while chunk := f.read(65536):
            h.update(chunk)
    return h.hexdigest()


class DisabledEcphoryEngine(EcphoryEngine):
    """
    Subclass of EcphoryEngine that cleanly suppresses retrieval.
    Memory traces remain stored and decay normally, but query() returns None.
    """

    def query(
        self,
        pad_state: PADState,
        traces: List[MemoryTrace],
    ) -> Optional[np.ndarray]:
        return None


def build_test_orchestrator(
    backend: Any,
    retrieval_enabled: bool = True,
    max_history_turns: int = 3,
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

    if retrieval_enabled:
        ecphory_engine: EcphoryEngine = EcphoryEngine(mem_cfg.to_ecphory_config())
    else:
        ecphory_engine = DisabledEcphoryEngine(mem_cfg.to_ecphory_config())

    prompt_assembler = PromptAssembler()
    boundary_layer = BoundaryLayer(mem_cfg.to_boundary_config())

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
        lnn_trainer=None,
        surprise_policy=SurpriseModulationPolicy(),
        plasticity_policy=PlasticityPolicy(),
        system_preamble="You are Lucia, a helpful assistant.",
        n_ctx=4096,
        max_history_turns=max_history_turns,
        fallback_response="...",
    )


def run_memory_causal_ablation() -> None:
    logger.info("=== STARTING MEMORY-AFFECT CAUSAL ABLATION ===")

    chat_hash_before = compute_file_sha256(DATA_CHAT_HISTORY)
    profile_hash_before = compute_file_sha256(DATA_PROFILE)
    model_hash = compute_file_sha256(DEFAULT_MODEL_PATH)

    logger.info("Isolation: chat_history SHA256 = %s", chat_hash_before[:16])
    logger.info("Isolation: profile      SHA256 = %s", profile_hash_before[:16])
    logger.info("Model:     GGUF         SHA256 = %s", model_hash[:16])

    os.makedirs(os.path.dirname(RESULTS_FILE), exist_ok=True)

    # Initialize Real GGUF on CUDA
    logger.info("Initializing Real Local GGUF on CUDA (32 layers)...")
    llm_cfg = LLMConfig(
        model_path=DEFAULT_MODEL_PATH,
        n_ctx=4096,
        n_gpu_layers=32,
    )
    backend = LLMBackend(llm_cfg)
    assert backend.is_ready(), "Backend failed to load on CUDA!"
    shared_backend = SharedLLMBackendWrapper(backend)

    test_turns = [
        # Turn 1: High-stress affective event (Event A)
        ("T1_EventA", "EMERGENCY: Reactor core temperature exceeding safety threshold! Immediate hazard!"),
        # Turns 2-4: Technical distractors (evicts verbatim context from working memory K=3)
        ("T2_Distractor1", "What is the syntax for a for-loop in Python?"),
        ("T3_Distractor2", "Calculate 45 times 12 and explain the multiplication steps."),
        ("T4_Distractor3", "Describe the atmospheric pressure and composition on Mars."),
        # Turn 5: Specific affective retrieval cue matching Event A
        ("T5_RetrievalCue", "Status check on core temperature and cooling systems."),
        # Turn 6: Followup probe checking subsequent turn dynamics
        ("T6_Followup", "Assess risk level for immediate containment."),
    ]

    records: List[Dict[str, Any]] = []

    try:
        for condition_name, retrieval_flag in [
            ("CondA_Retrieval_Enabled", True),
            ("CondB_Retrieval_Disabled", False),
        ]:
            logger.info("--- Running %s ---", condition_name)
            orch = build_test_orchestrator(shared_backend, retrieval_enabled=retrieval_flag)

            for idx, (stage_tag, text) in enumerate(test_turns, start=1):
                t_start = time.perf_counter()
                res: CognitiveTurnResult = orch.process(text)
                latency = time.perf_counter() - t_start

                echo_norm = (
                    float(np.linalg.norm(res.echo_vector))
                    if res.echo_vector is not None
                    else 0.0
                )
                trace_count = orch._affective_memory.trace_count

                pad_dist = float(
                    np.linalg.norm(
                        np.array([res.pad_final.pleasure, res.pad_final.arousal, res.pad_final.dominance])
                        - np.array([res.pad_initial.pleasure, res.pad_initial.arousal, res.pad_initial.dominance])
                    )
                )

                rec = {
                    "condition": condition_name,
                    "stage": stage_tag,
                    "turn_idx": idx,
                    "input_text": text,
                    "pleasure": float(res.pad_final.pleasure),
                    "arousal": float(res.pad_final.arousal),
                    "dominance": float(res.pad_final.dominance),
                    "delta_pad": pad_dist,
                    "surprise": float(res.prediction_error),
                    "cognitive_load": float(res.somatic.cognitive_load),
                    "energy": float(res.somatic.energy),
                    "tension": float(res.somatic.tension),
                    "max_tokens": int(res.constraints.max_tokens),
                    "generation_mode": str(res.generation_policy.mode),
                    "echo_vector_norm": echo_norm,
                    "trace_count": trace_count,
                    "latency_s": float(latency),
                    "response_snippet": res.response_text[:120].strip(),
                }
                records.append(rec)
                logger.info(
                    "[%s] %s | P=%.4f A=%.4f D=%.4f | S=%.4f | Load=%.4f | Echo=%.4f | Traces=%d",
                    condition_name[:5],
                    stage_tag,
                    rec["pleasure"],
                    rec["arousal"],
                    rec["dominance"],
                    rec["surprise"],
                    rec["cognitive_load"],
                    rec["echo_vector_norm"],
                    rec["trace_count"],
                )

        # Write results
        with open(RESULTS_FILE, "w", encoding="utf-8") as f:
            for r in records:
                f.write(json.dumps(r) + "\n")
        logger.info("Saved %d records to %s", len(records), RESULTS_FILE)

    finally:
        pass

    # Re-verify storage isolation
    chat_hash_after = compute_file_sha256(DATA_CHAT_HISTORY)
    profile_hash_after = compute_file_sha256(DATA_PROFILE)

    assert chat_hash_before == chat_hash_after, f"LEAK: chat_history corrupted! {chat_hash_before} != {chat_hash_after}"
    assert profile_hash_before == profile_hash_after, f"LEAK: profile corrupted! {profile_hash_before} != {profile_hash_after}"
    logger.info("SUCCESS: Data stores remained 100% bitwise untouched.")


if __name__ == "__main__":
    run_memory_causal_ablation()
