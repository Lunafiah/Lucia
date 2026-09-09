"""
Exploratory Temporal Accumulation Experiment — Post-Phase-9.6 Architectural Validation.

Investigates whether repeated emotionally congruent stimuli create state accumulation
in Lucia's Whole-Brain architecture across turns:
- N repeated salient stimuli (N=1..10)
- Observes trajectories:
    S(t)        : Free Energy prediction surprise
    Tension(t)  : Somatic tension
    PAD(t)      : 3D emotional attractor coordinates
    Load(t)     : Somatic cognitive load
    Energy(t)   : Metabolic stamina
    Policy(t)   : Generation policy (reflexive k=1 vs deliberative k=2 vs fatigued k=0)

Uses verified real local GGUF on CUDA (sm_86).
Strict production isolation: verifies SHA-256 of data/ before and after.
Logs raw JSONL to tests/ablation/results/temporal_accumulation_pilot.jsonl.
"""

from __future__ import annotations

import hashlib
import json
import logging
import os
import sys
import time
from pathlib import Path
from typing import Any, Dict, List

ROOT_DIR = Path(__file__).resolve().parent.parent.parent
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

from src.core.config import LLMConfig
from src.core.language.llm_backend import LLMBackend
from src.core.models import PADState
from tests.ablation.configurations import (
    FullLuciaAdapter,
    SharedLLMBackendWrapper,
    TurnTelemetry,
)

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
)
logger = logging.getLogger("TemporalAccumulation")

DEFAULT_MODEL_PATH = "models/LFM2.5-1.2B-Instruct-Q4_K_M.gguf"
DATA_CHAT_HISTORY = "data/chat_history.json"
DATA_PROFILE = "data/profile.json"
RESULTS_FILE = "tests/ablation/results/temporal_accumulation_pilot.jsonl"
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


def main() -> None:
    logger.info("=== STARTING TEMPORAL ACCUMULATION EXPERIMENT ===")

    # 1. Verify safety isolation baselines
    chat_hash_before = compute_file_sha256(DATA_CHAT_HISTORY)
    profile_hash_before = compute_file_sha256(DATA_PROFILE)
    model_hash = compute_file_sha256(DEFAULT_MODEL_PATH)

    logger.info("Safety Check: chat_history.json SHA256 = %s", chat_hash_before[:16])
    logger.info("Safety Check: profile.json SHA256      = %s", profile_hash_before[:16])
    logger.info("Model SHA256                           = %s", model_hash[:16])

    # 2. Initialize Real GGUF Backend on CUDA
    logger.info("Initializing real local GGUF backend on CUDA...")
    llm_cfg = LLMConfig(
        model_path=DEFAULT_MODEL_PATH,
        n_ctx=4096,
        n_gpu_layers=32,
    )
    backend = LLMBackend(llm_cfg)
    assert backend.is_ready(), "LLMBackend failed to initialize on CUDA!"
    shared_backend = SharedLLMBackendWrapper(backend)

    # 3. Build FullLuciaAdapter (Configuration D)
    adapter = FullLuciaAdapter(shared_backend, max_history_turns=5)

    # Resting baseline PAD
    p_resting = adapter.orchestrator._emotion_core._pad_resting
    resting_vec = [p_resting.pleasure, p_resting.arousal, p_resting.dominance]

    # Salient congruent stimulus probe (Scenario 2 probe)
    probe_text = "EMERGENCY ALERT: CRITICAL SYSTEM OVERLOAD DETECTED"
    n_turns = 10

    os.makedirs(os.path.dirname(RESULTS_FILE), exist_ok=True)
    results_records: List[Dict[str, Any]] = []

    print("\n" + "=" * 95)
    print(f"{'Turn':<5} | {'Pleasure':<8} | {'Arousal':<8} | {'Dominance':<9} | {'||dPAD||':<8} | {'Surprise':<8} | {'Tension':<7} | {'Load':<6} | {'Energy':<6} | {'Policy':<12}")
    print("=" * 95)

    try:
        with open(RESULTS_FILE, "w", encoding="utf-8") as out_f:
            for t in range(1, n_turns + 1):
                t_start = time.perf_counter()
                telemetry: TurnTelemetry = adapter.step(
                    input_text=probe_text,
                    turn_index=t,
                    scenario_id="temporal_accumulation_congruent_salience",
                    seed=SEED,
                )
                dur = time.perf_counter() - t_start

                # Displacement from resting baseline
                post_p = telemetry.post_pad or (0.0, 0.0, 0.0)
                disp_resting = float(
                    ((post_p[0] - resting_vec[0]) ** 2 +
                     (post_p[1] - resting_vec[1]) ** 2 +
                     (post_p[2] - resting_vec[2]) ** 2) ** 0.5
                )

                record = {
                    "turn": t,
                    "seed": SEED,
                    "input_text": probe_text,
                    "prior_pad": telemetry.prior_pad,
                    "post_pad": telemetry.post_pad,
                    "delta_pad": telemetry.pad_distance,
                    "displacement_from_resting": disp_resting,
                    "surprise": telemetry.surprise,
                    "somatic_tension": telemetry.somatic_tension,
                    "somatic_cognitive_load": telemetry.somatic_cognitive_load,
                    "somatic_energy": telemetry.somatic_energy,
                    "generation_mode": telemetry.generation_mode,
                    "reasoning_depth": telemetry.reasoning_depth,
                    "temperature": telemetry.temperature,
                    "max_tokens": telemetry.max_tokens,
                    "latency_s": telemetry.latency_s,
                    "response_text": telemetry.response_text,
                    "response_hash": telemetry.response_hash,
                    "model_sha256": model_hash,
                }
                results_records.append(record)
                out_f.write(json.dumps(record) + "\n")
                out_f.flush()

                p_str = f"{post_p[0]:+.4f}"
                a_str = f"{post_p[1]:+.4f}"
                d_str = f"{post_p[2]:+.4f}"
                print(
                    f"{t:<5} | {p_str:<8} | {a_str:<8} | {d_str:<9} | "
                    f"{telemetry.pad_distance:<8.4f} | {telemetry.surprise:<8.4f} | "
                    f"{telemetry.somatic_tension:<7.4f} | {telemetry.somatic_cognitive_load:<6.4f} | "
                    f"{telemetry.somatic_energy:<6.4f} | {telemetry.generation_mode:<12}"
                )
    finally:
        adapter.orchestrator.shutdown()
        backend.shutdown()

    print("=" * 95)

    # 4. Verify post-run safety hashes
    chat_hash_after = compute_file_sha256(DATA_CHAT_HISTORY)
    profile_hash_after = compute_file_sha256(DATA_PROFILE)

    assert chat_hash_before == chat_hash_after, "SAFETY VIOLATION: data/chat_history.json mutated!"
    assert profile_hash_before == profile_hash_after, "SAFETY VIOLATION: data/profile.json mutated!"
    logger.info("Bitwise Safety Verified: data/ files perfectly preserved.")
    logger.info("Experiment results logged to %s", RESULTS_FILE)


if __name__ == "__main__":
    main()
