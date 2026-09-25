"""
Canonical Experiment Runner for Phase 22-AL (Observation-to-Latent Alignment Study).
Tests Hypotheses H-AL1 through H-AL5 across Candidates C1–C6 and Alignment Models A0–A7.
Strict Anti-Cheating:
  Train seeds: 42, 137, 618
  Held-out seeds: 1024, 2026
Scientific Controls:
  Control A: Random Projection
  Control B: Randomized Temporal Order
  Control C: Shuffled Latent Targets
  Control D: Oracle Observation
"""
import argparse
import datetime
import json
import math
import os
import platform
import sys
import time
from typing import Dict, List, Tuple, Any
import numpy as np

from .config import (
    TRAIN_SEEDS,
    HELD_OUT_SEEDS,
    ALL_SEEDS,
    LANGUAGES,
    REGIMES,
    CANDIDATES,
    TEMPORAL_WINDOWS,
    STATE_DIM,
    INTERFACE_DIM,
    GATE_THRESHOLDS,
    HISTORICAL_BASELINES,
)
from ..phase22_observation.datasets.multilingual_env import SimUserEnvV2Observation
from ..phase22_observation.stability.continuous_tracker import ContinuousUserStateTracker
from ..phase22_observation.candidates.c1.encoder import CandidateC1Encoder
from ..phase22_observation.candidates.c2.encoder import CandidateC2Encoder
from ..phase22_observation.candidates.c3.encoder import CandidateC3Encoder
from ..phase22_observation.candidates.c4.encoder import CandidateC4Encoder
from ..phase22_observation.candidates.c5.encoder import CandidateC5Encoder
from ..phase22_observation.candidates.c6.encoder import CandidateC6Encoder
from ..phase22_observation.metrics import compute_r2, compute_mae, compute_mse, compute_flapping_rate, compute_contradiction_recovery, compute_mahalanobis_containment
from ..phase22_observation.statistics import compute_percentiles

from .alignment_models import (
    AlignmentA0Naive,
    AlignmentA1Linear,
    AlignmentA2Constrained,
    AlignmentA3SmallMLP,
    AlignmentA4TemporalWindow,
    AlignmentA5LeakyIntegrator,
    AlignmentA6ObservationLikelihood,
    AlignmentA7Hybrid,
)

ENCODER_FACTORIES = {
    "C1": CandidateC1Encoder,
    "C2": CandidateC2Encoder,
    "C3": CandidateC3Encoder,
    "C4": CandidateC4Encoder,
    "C5": CandidateC5Encoder,
    "C6": CandidateC6Encoder,
}

def extract_trajectories_for_candidate(cand_id: str, seeds: List[int]) -> List[Dict[str, Any]]:
    """
    Extracts time-series sequences of (raw_evidence, true_latent_state) across regimes and languages.
    """
    sequences = []
    factory = ENCODER_FACTORIES[cand_id]
    
    for seed in seeds:
        enc = factory(seed=seed)
        for lang in LANGUAGES:
            for regime in REGIMES:
                env = SimUserEnvV2Observation(seed=seed, regime=regime, language=lang)
                seq_obs = []
                seq_true = []
                step = env.reset()
                for _ in range(20):
                    step = env.step()
                    obs = enc.observe(step["utterance"], step["acoustics"], lang, regime)
                    seq_obs.append(obs.projected_state.copy())
                    seq_true.append(step["z_true"].copy())
                sequences.append({
                    "seed": seed,
                    "lang": lang,
                    "regime": regime,
                    "obs": np.array(seq_obs),
                    "true": np.array(seq_true),
                })
    return sequences

def build_temporal_windows(sequences: List[Dict[str, Any]], k: int) -> Tuple[np.ndarray, np.ndarray]:
    X_list = []
    y_list = []
    for seq in sequences:
        obs = seq["obs"]
        true = seq["true"]
        T = len(obs)
        for t in range(T):
            # Window of length k ending at t
            window = []
            for tau in range(k):
                idx = max(0, t - (k - 1) + tau)
                window.append(obs[idx])
            X_list.append(np.concatenate(window))
            y_list.append(true[t])
    return np.array(X_list), np.array(y_list)

def evaluate_predictions(y_true: np.ndarray, y_pred: np.ndarray) -> Dict[str, float]:
    return {
        "r2": float(compute_r2(y_true, y_pred)),
        "mae": float(compute_mae(y_true, y_pred)),
        "mse": float(compute_mse(y_true, y_pred)),
    }

def run_alignment_study():
    print("=================================================================")
    print("PHASE 22-AL: OBSERVATION-TO-LATENT ALIGNMENT STUDY BENCHMARK")
    print(f"Platform: {platform.system()} {platform.machine()} | Python: {platform.python_version()}")
    print(f"Train Seeds: {TRAIN_SEEDS} | Held-Out Seeds: {HELD_OUT_SEEDS}")
    print(f"Regimes: {REGIMES} | Candidates: {CANDIDATES}")
    print("=================================================================")
    
    t0_global = time.time()
    results: Dict[str, Any] = {
        "candidates": {},
        "temporal_ablation": {},
        "information_sufficiency": {},
        "controls": {},
        "downstream_stability": {},
        "latency": {},
        "gates": {},
    }
    
    # 1. Main Candidate x Alignment Model Matrix
    for cand_id in CANDIDATES:
        print(f"\n---> Evaluating Candidate {cand_id} across Alignment Ladder (A0–A7)...")
        train_seqs = extract_trajectories_for_candidate(cand_id, TRAIN_SEEDS)
        held_out_seqs = extract_trajectories_for_candidate(cand_id, HELD_OUT_SEEDS)
        
        # Flatten single-frame dataset
        X_train = np.vstack([s["obs"] for s in train_seqs])
        y_train = np.vstack([s["true"] for s in train_seqs])
        X_held = np.vstack([s["obs"] for s in held_out_seqs])
        y_held = np.vstack([s["true"] for s in held_out_seqs])
        
        # Temporal dataset (k=3)
        X_train_k3, y_train_k3 = build_temporal_windows(train_seqs, k=3)
        X_held_k3, y_held_k3 = build_temporal_windows(held_out_seqs, k=3)
        
        cand_results = {}
        
        # A0: Naive Baseline (Zero-Shot)
        a0 = AlignmentA0Naive()
        pred_a0 = np.array([a0.predict(x) for x in X_held])
        cand_results["A0_Naive"] = evaluate_predictions(y_held, pred_a0)
        
        # A1: Ridge Linear
        a1 = AlignmentA1Linear()
        a1.fit(X_train, y_train)
        pred_a1 = np.array([a1.predict(x) for x in X_held])
        cand_results["A1_Linear"] = evaluate_predictions(y_held, pred_a1)
        
        # A2: Constrained Projection
        a2 = AlignmentA2Constrained()
        a2.fit(X_train, y_train)
        pred_a2 = np.array([a2.predict(x) for x in X_held])
        cand_results["A2_Constrained"] = evaluate_predictions(y_held, pred_a2)
        
        # A3: Small MLP
        a3 = AlignmentA3SmallMLP()
        a3.fit(X_train, y_train, epochs=30)
        pred_a3 = np.array([a3.predict(x) for x in X_held])
        cand_results["A3_SmallMLP"] = evaluate_predictions(y_held, pred_a3)
        
        # A4: Temporal Window (k=3)
        a4 = AlignmentA4TemporalWindow(window_size=3)
        a4.fit(X_train_k3, y_train_k3)
        pred_a4 = np.array([a4.predict(x) for x in X_held_k3])
        cand_results["A4_TemporalWindow_k3"] = evaluate_predictions(y_held_k3, pred_a4)
        
        # A5: Leaky State Estimator (Sequential on held-out trajectories)
        a5 = AlignmentA5LeakyIntegrator(alpha=0.35, base_model=a1)
        pred_a5_list = []
        for s in held_out_seqs:
            prev = None
            for obs in s["obs"]:
                prev = a5.predict(obs, prev_z=prev)
                pred_a5_list.append(prev)
        cand_results["A5_LeakyIntegrator"] = evaluate_predictions(y_held, np.array(pred_a5_list))
        
        # A6: Observation-Likelihood State Estimator
        a6 = AlignmentA6ObservationLikelihood()
        a6.fit(X_train, y_train)
        pred_a6_list = []
        for s in held_out_seqs:
            prev = None
            for obs in s["obs"]:
                prev = a6.predict(obs, prev_z=prev)
                pred_a6_list.append(prev)
        cand_results["A6_ObservationLikelihood"] = evaluate_predictions(y_held, np.array(pred_a6_list))
        
        # A7: Hybrid Temporal Alignment
        a7 = AlignmentA7Hybrid(window_size=3)
        a7.fit(X_train_k3, y_train_k3)
        pred_a7_list = []
        idx = 0
        for s in held_out_seqs:
            prev = None
            for t in range(len(s["obs"])):
                window = [s["obs"][max(0, t - 2 + tau)] for tau in range(3)]
                w_vec = np.concatenate(window)
                prev = a7.predict(w_vec, prev_z=prev)
                pred_a7_list.append(prev)
        cand_results["A7_HybridTemporal"] = evaluate_predictions(y_held, np.array(pred_a7_list))
        
        results["candidates"][cand_id] = cand_results
        print(f"   [Held-out R²]: A0={cand_results['A0_Naive']['r2']:.4f}, A1={cand_results['A1_Linear']['r2']:.4f}, A4_k3={cand_results['A4_TemporalWindow_k3']['r2']:.4f}, A7={cand_results['A7_HybridTemporal']['r2']:.4f}")

    # 2. Temporal Window Ablation (k = 1, 3, 5, 10 on C2 and C4)
    print("\n---> Running Temporal Window Ablation (k = 1, 3, 5, 10)...")
    for test_cand in ["C2", "C4"]:
        train_seqs = extract_trajectories_for_candidate(test_cand, TRAIN_SEEDS)
        held_out_seqs = extract_trajectories_for_candidate(test_cand, HELD_OUT_SEEDS)
        k_res = {}
        for k in TEMPORAL_WINDOWS:
            X_tr, y_tr = build_temporal_windows(train_seqs, k=k)
            X_he, y_he = build_temporal_windows(held_out_seqs, k=k)
            model = AlignmentA4TemporalWindow(window_size=k)
            model.fit(X_tr, y_tr)
            preds = np.array([model.predict(x) for x in X_he])
            k_res[f"k_{k}"] = evaluate_predictions(y_he, preds)
        results["temporal_ablation"][test_cand] = k_res

    # 3. Information Sufficiency Experiment (Raw vs Aligned vs Oracle)
    print("\n---> Running Information Sufficiency Experiment (Raw vs Aligned vs Oracle)...")
    for cand_id in CANDIDATES:
        train_seqs = extract_trajectories_for_candidate(cand_id, TRAIN_SEEDS)
        held_out_seqs = extract_trajectories_for_candidate(cand_id, HELD_OUT_SEEDS)
        
        y_held = np.vstack([s["true"] for s in held_out_seqs])
        raw_preds = np.vstack([s["obs"] for s in held_out_seqs])
        
        # Aligned (A7 Hybrid)
        aligned_r2 = results["candidates"][cand_id]["A7_HybridTemporal"]["r2"]
        aligned_mae = results["candidates"][cand_id]["A7_HybridTemporal"]["mae"]
        
        # Oracle Observation (ground truth with irreducible measurement noise sigma=0.05)
        rng = np.random.RandomState(42)
        oracle_preds = y_held + rng.normal(0, 0.05, size=y_held.shape)
        oracle_eval = evaluate_predictions(y_held, oracle_preds)
        raw_eval = evaluate_predictions(y_held, raw_preds)
        
        results["information_sufficiency"][cand_id] = {
            "raw": raw_eval,
            "aligned_A7": {"r2": aligned_r2, "mae": aligned_mae},
            "oracle": oracle_eval,
            "information_gain_delta_r2": float(aligned_r2 - raw_eval["r2"]),
            "gap_to_oracle_r2": float(oracle_eval["r2"] - aligned_r2),
        }

    # 4. Scientific Controls (A, B, C, D)
    print("\n---> Running Scientific Controls (A: Random Proj, B: Shuffled Time, C: Shuffled Targets, D: Oracle)...")
    train_seqs = extract_trajectories_for_candidate("C2", TRAIN_SEEDS)
    held_out_seqs = extract_trajectories_for_candidate("C2", HELD_OUT_SEEDS)
    X_tr, y_tr = np.vstack([s["obs"] for s in train_seqs]), np.vstack([s["true"] for s in train_seqs])
    X_he, y_he = np.vstack([s["obs"] for s in held_out_seqs]), np.vstack([s["true"] for s in held_out_seqs])
    
    # Control A: Random Projection
    rng = np.random.RandomState(42)
    W_rand = rng.randn(STATE_DIM, STATE_DIM)
    b_rand = rng.randn(STATE_DIM)
    pred_ctrl_a = np.array([W_rand @ x + b_rand for x in X_he])
    eval_ctrl_a = evaluate_predictions(y_he, pred_ctrl_a)
    
    # Control B: Shuffled Temporal Order
    shuffled_held_seqs = []
    for s in held_out_seqs:
        p = rng.permutation(len(s["obs"]))
        shuffled_held_seqs.append({"obs": s["obs"][p], "true": s["true"][p]})
    X_he_shuff_k3, y_he_shuff_k3 = build_temporal_windows(shuffled_held_seqs, k=3)
    X_tr_k3, y_tr_k3 = build_temporal_windows(train_seqs, k=3)
    model_a4 = AlignmentA4TemporalWindow(window_size=3)
    model_a4.fit(X_tr_k3, y_tr_k3)
    pred_ctrl_b = np.array([model_a4.predict(x) for x in X_he_shuff_k3])
    eval_ctrl_b = evaluate_predictions(y_he_shuff_k3, pred_ctrl_b)
    
    # Control C: Shuffled Latent Targets
    y_tr_shuffled = y_tr[rng.permutation(len(y_tr))]
    model_ctrl_c = AlignmentA1Linear()
    model_ctrl_c.fit(X_tr, y_tr_shuffled)
    pred_ctrl_c = np.array([model_ctrl_c.predict(x) for x in X_he])
    eval_ctrl_c = evaluate_predictions(y_he, pred_ctrl_c)
    
    # Control D: Oracle
    pred_ctrl_d = y_he + rng.normal(0, 0.05, size=y_he.shape)
    eval_ctrl_d = evaluate_predictions(y_he, pred_ctrl_d)
    
    results["controls"] = {
        "Control_A_Random_Projection": eval_ctrl_a,
        "Control_B_Shuffled_Temporal_Order": eval_ctrl_b,
        "Control_C_Shuffled_Targets": eval_ctrl_c,
        "Control_D_Oracle_Observation": eval_ctrl_d,
    }

    # 5. Downstream Stability & Recovery under Aligned Observations
    print("\n---> Evaluating Downstream Continuous Stability with Aligned Input...")
    for cand_id in ["C2", "C4"]:
        held_out_seqs = extract_trajectories_for_candidate(cand_id, HELD_OUT_SEEDS)
        # Use A7 model to project observations before feeding to tracker
        a7_model = AlignmentA7Hybrid(window_size=3)
        X_tr_k3, y_tr_k3 = build_temporal_windows(extract_trajectories_for_candidate(cand_id, TRAIN_SEEDS), k=3)
        a7_model.fit(X_tr_k3, y_tr_k3)
        
        all_tracker_states = []
        recovery_turns = []
        containment_h1 = []
        containment_h2 = []
        
        for s in held_out_seqs:
            tracker = ContinuousUserStateTracker()
            seq_states = []
            prev_z = None
            for t in range(len(s["obs"])):
                window = [s["obs"][max(0, t - 2 + tau)] for tau in range(3)]
                w_vec = np.concatenate(window)
                z_aligned = a7_model.predict(w_vec, prev_z=prev_z)
                prev_z = z_aligned
                
                # Mock observation result for tracker
                from ..phase22_observation.schemas import ContinuousObservationResult, ObservationProvenance
                mock_obs = ContinuousObservationResult(
                    evidence_vector=z_aligned,
                    noise_covariance=np.eye(STATE_DIM) * 0.05,
                    probabilities=np.clip((z_aligned + 1.0) / 2.0, 0.0, 1.0),
                    projected_state=z_aligned,
                    confidence=0.85,
                    encoder_latency_ms=25.0,
                    projection_latency_ms=0.1,
                    provenance=ObservationProvenance(cand_id, "aligned-v1", s["seed"], s["regime"], s["lang"], "aligned", "CPU", "learned", "now"),
                )
                step_res = tracker.step(mock_obs, z_true=s["true"][t])
                seq_states.append(step_res.z_post)
                
                if t == 10:
                    means, covs, _ = tracker.forecast(horizon=2)
                    c1 = compute_mahalanobis_containment(s["true"][t], means[0], covs[0])
                    c2 = compute_mahalanobis_containment(s["true"][t], means[1], covs[1])
                    containment_h1.append(c1)
                    containment_h2.append(c2)
                    
            seq_arr = np.array(seq_states)
            all_tracker_states.append(seq_arr)
            if s["regime"] in ["ContradictionShock", "CombinedStress"]:
                rec = compute_contradiction_recovery(seq_arr, target_shock=s["true"][-1], shock_turn=15)
                recovery_turns.append(rec)
                
        flapping_rates = [compute_flapping_rate(states) for states in all_tracker_states]
        results["downstream_stability"][cand_id] = {
            "mean_flapping_rate": float(np.mean(flapping_rates)),
            "contradiction_recovery_turns": float(np.mean(recovery_turns)) if recovery_turns else 1.0,
            "trajectory_h1_coverage": float(np.mean(containment_h1)) if containment_h1 else 1.0,
            "trajectory_h2_coverage": float(np.mean(containment_h2)) if containment_h2 else 1.0,
        }

    # 6. Latency & Resource Profiling for Alignment Models
    print("\n---> Measuring Latency and Resource Overheads of Alignment Models...")
    model_instances = {
        "A1_Linear": AlignmentA1Linear(),
        "A2_Constrained": AlignmentA2Constrained(),
        "A3_SmallMLP": AlignmentA3SmallMLP(),
        "A4_Temporal_k3": AlignmentA4TemporalWindow(window_size=3),
        "A5_Leaky": AlignmentA5LeakyIntegrator(),
        "A6_ObsLikelihood": AlignmentA6ObservationLikelihood(),
        "A7_Hybrid": AlignmentA7Hybrid(window_size=3),
    }
    dummy_x6 = np.zeros(STATE_DIM)
    dummy_x18 = np.zeros(STATE_DIM * 3)
    
    for name, m in model_instances.items():
        inp = dummy_x18 if "k3" in name or "Hybrid" in name else dummy_x6
        # Warmup
        for _ in range(50):
            m.predict(inp)
        lats = []
        for _ in range(500):
            t_start = time.perf_counter()
            m.predict(inp)
            lats.append((time.perf_counter() - t_start) * 1000.0)
        pct = compute_percentiles(lats)
        results["latency"][name] = {
            "p50_ms": pct["p50"],
            "p95_ms": pct["p95"],
            "param_count": m.param_count,
        }

    # 7. Gate Evaluations
    # Highest achieved R2 on held-out seeds
    max_held_out_r2 = max(
        max(results["candidates"][c][m]["r2"] for m in results["candidates"][c])
        for c in CANDIDATES
    )
    gates = {
        "G_AL1_HELD_OUT_R2_TARGET": "PASS" if max_held_out_r2 >= GATE_THRESHOLDS["target_r2"] else "FAIL",
        "G_AL2_FALSIFICATION_CHECK": "PASS" if max_held_out_r2 >= GATE_THRESHOLDS["falsification_r2"] else "FALSIFIED",
        "G_AL3_DOWNSTREAM_FLAPPING": "PASS" if results["downstream_stability"]["C2"]["mean_flapping_rate"] <= GATE_THRESHOLDS["gate_flapping"] else "FAIL",
        "G_AL4_TRAJECTORY_COVERAGE": "PASS" if results["downstream_stability"]["C2"]["trajectory_h2_coverage"] >= GATE_THRESHOLDS["trajectory_coverage_h2"] else "FAIL",
        "G_AL5_ALIGNMENT_LATENCY": "PASS" if results["latency"]["A7_Hybrid"]["p50_ms"] <= 1.0 else "FAIL",
    }
    results["gates"] = gates
    results["max_held_out_r2"] = float(max_held_out_r2)

    # 8. Emit Canonical raw_measurements.json
    out_dir = "evaluation_artifacts/phase22_alignment"
    os.makedirs(out_dir, exist_ok=True)
    raw_path = os.path.join(out_dir, "raw_measurements.json")
    with open(raw_path, "w", encoding="utf-8") as f:
        json.dump(results, f, indent=2)
    print(f"\n[Artifact Emitted] Canonical raw measurements: {raw_path}")
    
    # Emit gate_results.json
    gate_path = os.path.join(out_dir, "gate_results.json")
    with open(gate_path, "w", encoding="utf-8") as f:
        json.dump(gates, f, indent=2)
    print(f"[Artifact Emitted] Gate results: {gate_path}")
    
    duration = time.time() - t0_global
    print(f"Phase 22-AL Study completed in {duration:.2f} seconds.")

if __name__ == "__main__":
    run_alignment_study()
