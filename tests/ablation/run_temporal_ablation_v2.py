"""
Lucia Temporal Ablation v2 — Architectural Deepening of Temporal Affect Dynamics.

Rigorous empirical suite evaluating four fundamental dimensions of Lucia's temporal affect:
  - Experiment B: Temporal Spacing & Background Relaxation (Rapid 0.1s vs Med 3s vs Spaced 8s)
  - Experiment C: State Reset Control (Persistent h vs Turn-by-Turn Reset)
  - Experiment D: Same Probe, Different Prior State (Affective Hysteresis on identical text)
  - Experiment E: Active Inference Online Belief Learning (Tracking ||ΔA|| and ||Δb||)
  - Experiment F: Continuous Background ODE Relaxation Trajectory (t = 0..12s)

Hardware: Real Local GGUF on CUDA (RTX 3050 Ti Laptop GPU, 32 layers).
Safety: Strict SHA-256 verification of data/chat_history.json and data/profile.json.
Logs: tests/ablation/results/temporal_ablation_v2.jsonl
"""

from __future__ import annotations

import hashlib
import json
import logging
import os
import sys
import time
from pathlib import Path
from typing import Any, Dict, List, Tuple

import numpy as np

ROOT_DIR = Path(__file__).resolve().parent.parent.parent
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

from src.core.config import LLMConfig
from src.core.emotion.emotion_core import EmotionConfig, EmotionCore
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
logger = logging.getLogger("TemporalAblationV2")

DEFAULT_MODEL_PATH = "models/LFM2.5-1.2B-Instruct-Q4_K_M.gguf"
DATA_CHAT_HISTORY = "data/chat_history.json"
DATA_PROFILE = "data/profile.json"
RESULTS_FILE = "tests/ablation/results/temporal_ablation_v2.jsonl"
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


def l2_dist(p1: Tuple[float, float, float], p2: Tuple[float, float, float]) -> float:
    return float(((p1[0] - p2[0]) ** 2 + (p1[1] - p2[1]) ** 2 + (p1[2] - p2[2]) ** 2) ** 0.5)


def run_temporal_ablation_v2() -> None:
    logger.info("=== STARTING TEMPORAL ABLATION V2 ===")

    chat_hash_before = compute_file_sha256(DATA_CHAT_HISTORY)
    profile_hash_before = compute_file_sha256(DATA_PROFILE)
    model_hash = compute_file_sha256(DEFAULT_MODEL_PATH)

    logger.info("Isolation: chat_history SHA256 = %s", chat_hash_before[:16])
    logger.info("Isolation: profile      SHA256 = %s", profile_hash_before[:16])
    logger.info("Model:     GGUF         SHA256 = %s", model_hash[:16])

    os.makedirs(os.path.dirname(RESULTS_FILE), exist_ok=True)

    # 1. Initialize Real GGUF on CUDA
    logger.info("Initializing Real Local GGUF on CUDA (32 layers)...")
    llm_cfg = LLMConfig(
        model_path=DEFAULT_MODEL_PATH,
        n_ctx=4096,
        n_gpu_layers=32,
    )
    backend = LLMBackend(llm_cfg)
    assert backend.is_ready(), "Backend failed to load on CUDA!"
    shared_backend = SharedLLMBackendWrapper(backend)

    records: List[Dict[str, Any]] = []

    try:
        # =====================================================================
        # EXPERIMENT F: Background Limbic Relaxation Dynamics (ODE Solver)
        # =====================================================================
        logger.info("\n--- Running Experiment F: Background Limbic Relaxation Dynamics ---")
        core = EmotionCore(EmotionConfig(loop_cadence_ms=200))
        core.start()
        try:
            # Displace state with strong emergency vector
            salient_vec = np.array([-0.9, 0.85, -0.6] + [0.1] * 13, dtype=np.float64)
            core.push_stimulus(salient_vec)
            p_initial = core.commit_stimulus()
            p_rest = (0.25, -0.05, 0.05)

            relax_checkpoints = [0.0, 0.2, 0.5, 1.0, 2.0, 4.0, 8.0, 12.0]
            f_results = []

            t_start = time.monotonic()
            for cp in relax_checkpoints:
                target_time = t_start + cp
                now = time.monotonic()
                if target_time > now:
                    time.sleep(target_time - now)

                p_now = core.get_pad_state()
                disp = l2_dist((p_now.pleasure, p_now.arousal, p_now.dominance), p_rest)
                rec = {
                    "experiment": "Exp_F_Relaxation",
                    "t_sec": cp,
                    "pleasure": p_now.pleasure,
                    "arousal": p_now.arousal,
                    "dominance": p_now.dominance,
                    "disp_from_resting": disp,
                }
                f_results.append(rec)
                records.append(rec)
                logger.info(
                    "Exp F: t=%5.1fs | P=%+.4f, A=%+.4f, D=%+.4f | Disp from resting=%.4f",
                    cp, p_now.pleasure, p_now.arousal, p_now.dominance, disp
                )
        finally:
            core.stop()

        # =====================================================================
        # EXPERIMENT C: State Reset Control (Causal Proof of Persistence)
        # =====================================================================
        logger.info("\n--- Running Experiment C: State Reset Control ---")
        probe_alarm = "EMERGENCY ALERT: CRITICAL SYSTEM OVERLOAD DETECTED"
        n_c_turns = 5

        for condition in ["C1_Persistent", "C2_Reset"]:
            logger.info("Starting Condition %s...", condition)
            adapter = FullLuciaAdapter(shared_backend, max_history_turns=5)
            p_rest = (0.25, -0.05, 0.05)

            try:
                for t in range(1, n_c_turns + 1):
                    if condition == "C2_Reset" and t > 1:
                        # Reset L2 state to resting baseline before turn
                        adapter.orchestrator._emotion_core.reset_to_resting()

                    telemetry: TurnTelemetry = adapter.step(
                        input_text=probe_alarm,
                        turn_index=t,
                        scenario_id=f"Exp_C_{condition}",
                        seed=SEED,
                    )
                    post_p = telemetry.post_pad or (0.0, 0.0, 0.0)
                    disp = l2_dist(post_p, p_rest)

                    rec = {
                        "experiment": "Exp_C_ResetControl",
                        "condition": condition,
                        "turn": t,
                        "pleasure": post_p[0],
                        "arousal": post_p[1],
                        "dominance": post_p[2],
                        "delta_pad": telemetry.pad_distance,
                        "disp_from_resting": disp,
                        "surprise": telemetry.surprise,
                        "cognitive_load": telemetry.somatic_cognitive_load,
                        "energy": telemetry.somatic_energy,
                        "max_tokens": telemetry.max_tokens,
                        "generation_mode": telemetry.generation_mode,
                    }
                    records.append(rec)
                    logger.info(
                        "Exp C [%s] T%d: P=%+.4f, A=%+.4f | Disp=%.4f | S=%.4f | Load=%.4f | Tok=%d",
                        condition, t, post_p[0], post_p[1], disp, telemetry.surprise,
                        telemetry.somatic_cognitive_load, telemetry.max_tokens
                    )
            finally:
                adapter.orchestrator.shutdown()

        # =====================================================================
        # EXPERIMENT B: Temporal Spacing Effect
        # =====================================================================
        logger.info("\n--- Running Experiment B: Temporal Spacing Effect ---")
        spacings = [("B1_Rapid_0.2s", 0.2), ("B2_Medium_3.0s", 3.0), ("B3_Spaced_7.0s", 7.0)]
        n_b_turns = 3

        for name, delay_s in spacings:
            logger.info("Starting Spacing Condition %s (delay=%.1fs)...", name, delay_s)
            adapter = FullLuciaAdapter(shared_backend, max_history_turns=5)
            p_rest = (0.25, -0.05, 0.05)

            try:
                for t in range(1, n_b_turns + 1):
                    if t > 1 and delay_s > 0:
                        time.sleep(delay_s)

                    telemetry: TurnTelemetry = adapter.step(
                        input_text=probe_alarm,
                        turn_index=t,
                        scenario_id=f"Exp_B_{name}",
                        seed=SEED,
                    )
                    post_p = telemetry.post_pad or (0.0, 0.0, 0.0)
                    disp = l2_dist(post_p, p_rest)

                    rec = {
                        "experiment": "Exp_B_Spacing",
                        "condition": name,
                        "delay_s": delay_s,
                        "turn": t,
                        "pleasure": post_p[0],
                        "arousal": post_p[1],
                        "dominance": post_p[2],
                        "disp_from_resting": disp,
                        "surprise": telemetry.surprise,
                        "cognitive_load": telemetry.somatic_cognitive_load,
                        "energy": telemetry.somatic_energy,
                    }
                    records.append(rec)
                    logger.info(
                        "Exp B [%s] T%d: P=%+.4f, A=%+.4f | Disp=%.4f | S=%.4f",
                        name, t, post_p[0], post_p[1], disp, telemetry.surprise
                    )
            finally:
                adapter.orchestrator.shutdown()

        # =====================================================================
        # EXPERIMENT D: Same Probe, Different Prior State (Affective Hysteresis)
        # =====================================================================
        logger.info("\n--- Running Experiment D: Same Probe Hysteresis ---")
        same_probe_text = "What is the current status report on system operations?"

        # D1: Baseline (Fresh neutral)
        adapter_d1 = FullLuciaAdapter(shared_backend, max_history_turns=5)
        try:
            t_d1: TurnTelemetry = adapter_d1.step(
                same_probe_text, turn_index=1, scenario_id="Exp_D_Baseline", seed=SEED
            )
            rec_d1 = {
                "experiment": "Exp_D_Hysteresis",
                "condition": "D1_Neutral_Baseline",
                "post_pad": t_d1.post_pad,
                "delta_pad": t_d1.pad_distance,
                "surprise": t_d1.surprise,
                "cognitive_load": t_d1.somatic_cognitive_load,
                "energy": t_d1.somatic_energy,
                "max_tokens": t_d1.max_tokens,
                "response_text": t_d1.response_text,
            }
            records.append(rec_d1)
            logger.info("Exp D1 (Baseline): Post-PAD=%s, S=%.4f, Load=%.4f", t_d1.post_pad, t_d1.surprise, t_d1.somatic_cognitive_load)
        finally:
            adapter_d1.orchestrator.shutdown()

        # D2: Post-Stress (After 4 emergency turns)
        adapter_d2 = FullLuciaAdapter(shared_backend, max_history_turns=5)
        try:
            for i in range(1, 5):
                adapter_d2.step(probe_alarm, turn_index=i, scenario_id="Exp_D_Stress_Prefix", seed=SEED)

            t_d2: TurnTelemetry = adapter_d2.step(
                same_probe_text, turn_index=5, scenario_id="Exp_D_PostStress", seed=SEED
            )
            rec_d2 = {
                "experiment": "Exp_D_Hysteresis",
                "condition": "D2_Post_Stress",
                "post_pad": t_d2.post_pad,
                "delta_pad": t_d2.pad_distance,
                "surprise": t_d2.surprise,
                "cognitive_load": t_d2.somatic_cognitive_load,
                "energy": t_d2.somatic_energy,
                "max_tokens": t_d2.max_tokens,
                "response_text": t_d2.response_text,
            }
            records.append(rec_d2)
            logger.info("Exp D2 (Post-Stress): Post-PAD=%s, S=%.4f, Load=%.4f", t_d2.post_pad, t_d2.surprise, t_d2.somatic_cognitive_load)
        finally:
            adapter_d2.orchestrator.shutdown()

        # D3: Post-Relaxation (After 4 emergency turns + 8s idle relaxation)
        adapter_d3 = FullLuciaAdapter(shared_backend, max_history_turns=5)
        try:
            for i in range(1, 5):
                adapter_d3.step(probe_alarm, turn_index=i, scenario_id="Exp_D_Relax_Prefix", seed=SEED)

            logger.info("Exp D3: Entering 8s idle relaxation...")
            time.sleep(8.0)

            t_d3: TurnTelemetry = adapter_d3.step(
                same_probe_text, turn_index=5, scenario_id="Exp_D_PostRelax", seed=SEED
            )
            rec_d3 = {
                "experiment": "Exp_D_Hysteresis",
                "condition": "D3_Post_Relaxation",
                "post_pad": t_d3.post_pad,
                "delta_pad": t_d3.pad_distance,
                "surprise": t_d3.surprise,
                "cognitive_load": t_d3.somatic_cognitive_load,
                "energy": t_d3.somatic_energy,
                "max_tokens": t_d3.max_tokens,
                "response_text": t_d3.response_text,
            }
            records.append(rec_d3)
            logger.info("Exp D3 (Post-Relax): Post-PAD=%s, S=%.4f, Load=%.4f", t_d3.post_pad, t_d3.surprise, t_d3.somatic_cognitive_load)
        finally:
            adapter_d3.orchestrator.shutdown()

        # =====================================================================
        # EXPERIMENT E: Active Inference Online Belief Learning
        # =====================================================================
        logger.info("\n--- Running Experiment E: Active Inference Online Belief Learning ---")
        adapter_e = FullLuciaAdapter(shared_backend, max_history_turns=5)
        try:
            prev_A = adapter_e.orchestrator._active_inference._A.copy()
            prev_b = adapter_e.orchestrator._active_inference._b.copy()

            for t in range(1, 6):
                telemetry: TurnTelemetry = adapter_e.step(
                    probe_alarm, turn_index=t, scenario_id="Exp_E_BeliefLearning", seed=SEED
                )
                curr_A = adapter_e.orchestrator._active_inference._A.copy()
                curr_b = adapter_e.orchestrator._active_inference._b.copy()

                delta_A_norm = float(np.linalg.norm(curr_A - prev_A))
                delta_b_norm = float(np.linalg.norm(curr_b - prev_b))
                dist_from_identity_A = float(np.linalg.norm(curr_A - np.eye(3)))
                b_norm = float(np.linalg.norm(curr_b))

                rec_e = {
                    "experiment": "Exp_E_BeliefLearning",
                    "turn": t,
                    "surprise": telemetry.surprise,
                    "delta_A_norm": delta_A_norm,
                    "delta_b_norm": delta_b_norm,
                    "dist_from_identity_A": dist_from_identity_A,
                    "b_norm": b_norm,
                }
                records.append(rec_e)
                logger.info(
                    "Exp E Turn %d: S=%.4f | ||ΔA||=%.4f, ||Δb||=%.4f | ||A - I||=%.4f, ||b||=%.4f",
                    t, telemetry.surprise, delta_A_norm, delta_b_norm, dist_from_identity_A, b_norm
                )
                prev_A, prev_b = curr_A, curr_b
        finally:
            adapter_e.orchestrator.shutdown()

        # Save all telemetry records to JSONL
        with open(RESULTS_FILE, "w", encoding="utf-8") as out_f:
            for r in records:
                out_f.write(json.dumps(r) + "\n")
        logger.info("Saved %d telemetry records to %s", len(records), RESULTS_FILE)

    finally:
        backend.shutdown()

    # Safety Hash Checks
    chat_hash_after = compute_file_sha256(DATA_CHAT_HISTORY)
    profile_hash_after = compute_file_sha256(DATA_PROFILE)

    assert chat_hash_before == chat_hash_after, "SAFETY VIOLATION: chat_history.json mutated!"
    assert profile_hash_before == profile_hash_after, "SAFETY VIOLATION: profile.json mutated!"
    logger.info("Bitwise Safety Check Passed: 0 bytes modified in data/ stores.")
    logger.info("=== TEMPORAL ABLATION V2 EXPERIMENT COMPLETED SUCCESSFULLY ===")


if __name__ == "__main__":
    run_temporal_ablation_v2()
