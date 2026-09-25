"""
Experiment Runner for Phase 22-SSF:
Semantic State Formation & Latent Target Decoupling.
"""
import os
import json
import time
from typing import Dict, List, Tuple
import numpy as np

from .config import (
    TRAIN_SEEDS,
    HELD_OUT_SEEDS,
    ALL_SEEDS,
    STRESS_REGIMES,
    LANGUAGES,
    STATE_DIM,
    DIM_NAMES,
    FAST_DIMS,
    SLOW_DIMS,
    FAST_DIM_NAMES,
    SLOW_DIM_NAMES,
    GATE_R2_TARGET,
    GATE_R2_FALSIFICATION,
    GATE_DOWNSTREAM_FLAPPING,
    GATE_CONTRADICTION_RECOVERY,
    GATE_TRAJECTORY_COVERAGE,
    GATE_CPU_P50_MS,
    CANONICAL_BASELINES,
)
from .env import SimUserEnvSSF
from .model import SemanticStateFormationDecoupled, RawBaselineModel

def extract_features(step: Dict, stream_mode: str = "full") -> np.ndarray:
    text = step["text_features"]            # 7
    acoust = step["acoustics_base"]        # 6
    temp = step["temporal_dynamics"]       # 6
    inter = step["interaction_dynamics"]   # 4
    
    if stream_mode == "full":
        return np.concatenate([text, acoust, temp, inter]) # 23
    elif stream_mode == "no_interaction":
        return np.concatenate([text, acoust, temp])         # 19
    elif stream_mode == "no_temporal":
        return np.concatenate([text, acoust, inter])        # 17
    elif stream_mode == "text_only":
        return text                                         # 7
    elif stream_mode == "acoustics_only":
        return acoust                                       # 6
    else:
        raise ValueError(f"Unknown stream mode: {stream_mode}")

def generate_trajectory(seed: int, regime: str, language: str = "English", turns: int = 30) -> List[Dict]:
    env = SimUserEnvSSF(seed=seed, regime=regime, language=language)
    traj = [env.reset()]
    for _ in range(turns - 1):
        traj.append(env.step())
    return traj

def evaluate_model(model, trajectories: List[List[Dict]], stream_mode: str = "full", is_decoupled: bool = True) -> Dict:
    all_true = []
    all_pred = []
    flapping_counts = 0
    total_acc_transitions = 0
    contradiction_recoveries = []
    h1_in_cone = 0
    h2_in_cone = 0
    total_horizon_points = 0
    
    for traj in trajectories:
        model.reset_state(traj[0]["z_true"])
        prev_vel = None
        prev_acc = None
        recovering = False
        recovery_turn_count = 0
        
        for t_idx, step in enumerate(traj):
            z_true = step["z_true"]
            x = extract_features(step, stream_mode=stream_mode)
            
            if is_decoupled:
                latency = float(step["interaction_dynamics"][0])
                pause_ratio = float(step["temporal_dynamics"][2])
                z_pred = model.step(x, interaction_latency=latency, pause_ratio=pause_ratio)
            else:
                z_pred = model.step(x)
                
            all_true.append(z_true)
            all_pred.append(z_pred)
            
            # Flapping detection
            if prev_vel is not None:
                curr_vel = z_pred - prev_vel
                if prev_acc is not None:
                    curr_acc = curr_vel - prev_acc
                    for d in range(STATE_DIM):
                        if (curr_acc[d] * prev_acc[d]) < -1e-4:
                            flapping_counts += 1
                        total_acc_transitions += 1
                    prev_acc = curr_acc
                else:
                    prev_acc = curr_vel
                prev_vel = z_pred
            else:
                prev_vel = z_pred
                
            # Contradiction recovery at t=15
            if step["regime"] in ["ContradictionShock", "CombinedStress"]:
                if t_idx == 15:
                    recovering = True
                    recovery_turn_count = 0
                elif recovering:
                    recovery_turn_count += 1
                    err = np.linalg.norm(z_pred - z_true)
                    if err < 0.35 or recovery_turn_count >= 5:
                        contradiction_recoveries.append(recovery_turn_count)
                        recovering = False
                        
            # Horizon coverage (radius h1=0.45, h2=0.60)
            if t_idx + 1 < len(traj):
                z_true_h1 = traj[t_idx + 1]["z_true"]
                if np.linalg.norm(z_pred - z_true_h1) <= 0.45:
                    h1_in_cone += 1
            if t_idx + 2 < len(traj):
                z_true_h2 = traj[t_idx + 2]["z_true"]
                if np.linalg.norm(z_pred - z_true_h2) <= 0.60:
                    h2_in_cone += 1
            total_horizon_points += 1

    Y_true = np.array(all_true)
    Y_pred = np.array(all_pred)
    
    mse = float(np.mean((Y_true - Y_pred) ** 2))
    mae = float(np.mean(np.abs(Y_true - Y_pred)))
    var_total = float(np.var(Y_true))
    r2 = float(1.0 - (mse / max(var_total, 1e-6)))
    
    dim_r2 = {}
    for d in range(STATE_DIM):
        d_mse = float(np.mean((Y_true[:, d] - Y_pred[:, d]) ** 2))
        d_var = float(np.var(Y_true[:, d]))
        dim_r2[DIM_NAMES[d]] = float(1.0 - (d_mse / max(d_var, 1e-6)))
        
    fast_r2 = float(np.mean([dim_r2[DIM_NAMES[d]] for d in FAST_DIMS]))
    slow_r2 = float(np.mean([dim_r2[DIM_NAMES[d]] for d in SLOW_DIMS]))
    
    flapping_rate = float(flapping_counts / max(total_acc_transitions, 1))
    mean_recovery = float(np.mean(contradiction_recoveries)) if contradiction_recoveries else 1.0
    h1_cov = float(h1_in_cone / max(total_horizon_points, 1))
    h2_cov = float(h2_in_cone / max(total_horizon_points, 1))
    
    return {
        "r2": r2,
        "fast_r2": fast_r2,
        "slow_r2": slow_r2,
        "mae": mae,
        "mse": mse,
        "dim_r2": dim_r2,
        "flapping_rate": flapping_rate,
        "contradiction_recovery_turns": mean_recovery,
        "trajectory_h1_coverage": h1_cov,
        "trajectory_h2_coverage": h2_cov,
    }

def run_all_experiments() -> Dict:
    print("=" * 65)
    print("Executing Phase 22-SSF: Semantic State Formation & Target Decoupling")
    print("=" * 65)
    
    # 1. Collect Trajectories
    print("[Step 1] Collecting trajectories...")
    train_trajs = []
    for s in TRAIN_SEEDS:
        for r in STRESS_REGIMES:
            train_trajs.append(generate_trajectory(seed=s, regime=r, language="English", turns=30))
            
    held_out_trajs = []
    for s in HELD_OUT_SEEDS:
        for r in STRESS_REGIMES:
            held_out_trajs.append(generate_trajectory(seed=s, regime=r, language="English", turns=30))
            
    # 2. Train Models
    print("\n[Step 2] Training Models (Decoupled SSF vs Raw Baseline)...")
    X_train_full = np.array([extract_features(step, "full") for traj in train_trajs for step in traj])
    Y_train = np.array([step["z_true"] for traj in train_trajs for step in traj])
    
    ssf_model = SemanticStateFormationDecoupled(alpha_fast=0.35, beta_slow=0.12)
    ssf_model.fit(X_train_full, Y_train)
    
    raw_model = RawBaselineModel()
    raw_model.fit(X_train_full, Y_train)
    
    # Benchmark Latency
    sample_x = X_train_full[0]
    latencies = []
    for _ in range(500):
        t0 = time.perf_counter()
        ssf_model.step(sample_x, interaction_latency=1.2, pause_ratio=0.3)
        latencies.append((time.perf_counter() - t0) * 1000.0)
    p50_lat = float(np.percentile(latencies, 50))
    p95_lat = float(np.percentile(latencies, 95))
    
    # 3. Main Comparison: Raw vs SSF vs Oracle
    print("\n[Step 3] Evaluating Primary Comparison: Raw vs SSF vs Oracle...")
    eval_ssf = evaluate_model(ssf_model, held_out_trajs, stream_mode="full", is_decoupled=True)
    eval_ssf["p50_latency_ms"] = p50_lat
    eval_ssf["p95_latency_ms"] = p95_lat
    
    eval_raw = evaluate_model(raw_model, held_out_trajs, stream_mode="full", is_decoupled=False)
    
    # Oracle Control (irreducible noise sigma=0.05)
    y_he_all = np.vstack([np.array([step["z_true"] for step in traj]) for traj in held_out_trajs])
    pred_oracle = y_he_all + np.random.RandomState(42).normal(0, 0.05, size=y_he_all.shape)
    oracle_mse = float(np.mean((y_he_all - pred_oracle) ** 2))
    oracle_mae = float(np.mean(np.abs(y_he_all - pred_oracle)))
    oracle_r2 = float(1.0 - (oracle_mse / max(float(np.var(y_he_all)), 1e-6)))
    eval_oracle = {"r2": oracle_r2, "mae": oracle_mae, "mse": oracle_mse}
    
    print(f"  -> Raw Baseline:   Held-Out R^2 = {eval_raw['r2']:.4f}, MAE = {eval_raw['mae']:.4f}")
    print(f"  -> Decoupled SSF:   Held-Out R^2 = {eval_ssf['r2']:.4f} (Fast R^2={eval_ssf['fast_r2']:.4f}, Slow R^2={eval_ssf['slow_r2']:.4f}), MAE = {eval_ssf['mae']:.4f}")
    print(f"  -> Oracle Control: Held-Out R^2 = {eval_oracle['r2']:.4f}, MAE = {eval_oracle['mae']:.4f}")
    
    # 4. Stream Ablation over SSF
    print("\n[Step 4] Running Stream Ablations over SSF...")
    ablation_modes = ["no_interaction", "no_temporal", "text_only", "acoustics_only"]
    ablation_results = {}
    for mode in ablation_modes:
        X_tr = np.array([extract_features(step, mode) for traj in train_trajs for step in traj])
        abl_model = SemanticStateFormationDecoupled(alpha_fast=0.35, beta_slow=0.12)
        abl_model.fit(X_tr, Y_train)
        abl_eval = evaluate_model(abl_model, held_out_trajs, stream_mode=mode, is_decoupled=True)
        ablation_results[mode] = abl_eval
        print(f"  -> Ablation ({mode}): Held-Out R^2 = {abl_eval['r2']:.4f}, Fast R^2 = {abl_eval['fast_r2']:.4f}")

    # 5. Language Independence Evaluation (EN, VI, JA)
    print("\n[Step 5] Evaluating Cross-Lingual Parity (EN, VI, JA)...")
    lang_results = {}
    for lang in LANGUAGES:
        lang_trajs = []
        for s in HELD_OUT_SEEDS:
            for r in STRESS_REGIMES:
                lang_trajs.append(generate_trajectory(seed=s, regime=r, language=lang, turns=30))
        lang_eval = evaluate_model(ssf_model, lang_trajs, stream_mode="full", is_decoupled=True)
        lang_results[lang] = {"r2": lang_eval["r2"], "mae": lang_eval["mae"], "mse": lang_eval["mse"]}
        print(f"  -> Language {lang}: Held-Out R^2 = {lang_eval['r2']:.4f}, MAE = {lang_eval['mae']:.4f}")

    # 6. Controls Evaluation
    print("\n[Step 6] Running Scientific Controls...")
    # Control A: Random Fast Projection
    ctrl_a_model = SemanticStateFormationDecoupled()
    ctrl_a_model.W_fast = np.random.RandomState(42).randn(4, 23)
    ctrl_a_model.b_fast = np.zeros(4)
    ctrl_a = evaluate_model(ctrl_a_model, held_out_trajs, stream_mode="full", is_decoupled=True)
    
    # Control B: Shuffled Temporal Order
    shuffled_trajs = []
    for traj in held_out_trajs:
        shuffled = list(traj)
        np.random.RandomState(42).shuffle(shuffled)
        shuffled_trajs.append(shuffled)
    ctrl_b = evaluate_model(ssf_model, shuffled_trajs, stream_mode="full", is_decoupled=True)
    
    # Control C: Shuffled Targets
    ctrl_c_trajs = []
    for traj in held_out_trajs:
        c_traj = []
        for s in traj:
            s_copy = dict(s)
            s_copy["z_true"] = np.random.RandomState(137).permutation(s["z_true"])
            c_traj.append(s_copy)
        ctrl_c_trajs.append(c_traj)
    ctrl_c = evaluate_model(ssf_model, ctrl_c_trajs, stream_mode="full", is_decoupled=True)
    
    controls = {
        "Control_A_Random_Projection": {"r2": ctrl_a["r2"], "mae": ctrl_a["mae"], "mse": ctrl_a["mse"]},
        "Control_B_Shuffled_Temporal_Order": {"r2": ctrl_b["r2"], "mae": ctrl_b["mae"], "mse": ctrl_b["mse"]},
        "Control_C_Shuffled_Targets": {"r2": ctrl_c["r2"], "mae": ctrl_c["mae"], "mse": ctrl_c["mse"]},
        "Control_D_Oracle_Observation": eval_oracle,
    }

    # 7. Gates Verification
    gates = {
        "G_SSF1_HELD_OUT_R2_TARGET": "PASS" if eval_ssf["r2"] >= GATE_R2_TARGET else "FAIL",
        "G_SSF2_FALSIFICATION_CHECK": "SUPPORTED" if eval_ssf["r2"] >= GATE_R2_FALSIFICATION else "FALSIFIED",
        "G_SSF3_FAST_STATES_R2": "PASS" if eval_ssf["fast_r2"] >= 0.70 else "FAIL",
        "G_SSF4_DOWNSTREAM_FLAPPING": "PASS" if eval_ssf["flapping_rate"] <= GATE_DOWNSTREAM_FLAPPING else "FAIL",
        "G_SSF5_CPU_LATENCY": "PASS" if p50_lat <= GATE_CPU_P50_MS else "FAIL",
    }
    
    results = {
        "comparison": {
            "raw_baseline": eval_raw,
            "decoupled_ssf": eval_ssf,
            "oracle_control": eval_oracle,
        },
        "ablations": ablation_results,
        "languages": lang_results,
        "controls": controls,
        "gates": gates,
        "peak_held_out_r2": eval_ssf["r2"],
        "fast_states_r2": eval_ssf["fast_r2"],
        "slow_states_r2": eval_ssf["slow_r2"],
        "canonical_baselines": CANONICAL_BASELINES,
    }

    print("\n[Step 7] Writing Output Artifacts...")
    out_dir = os.path.join("evaluation_artifacts", "phase22_ssf")
    os.makedirs(out_dir, exist_ok=True)
    
    with open(os.path.join(out_dir, "raw_measurements.json"), "w", encoding="utf-8") as f:
        json.dump(results, f, indent=2)
        
    with open(os.path.join(out_dir, "gate_results.json"), "w", encoding="utf-8") as f:
        json.dump(gates, f, indent=2)
        
    print(f"Phase 22-SSF completed successfully. Artifacts in {out_dir}")
    return results

if __name__ == "__main__":
    run_all_experiments()
