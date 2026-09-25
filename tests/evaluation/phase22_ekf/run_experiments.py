"""
Experiment Runner for Phase 22-EKF:
Kalman-Based Semantic State Formation.
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
    GATE_OVERALL_R2_TARGET,
    GATE_FAST_R2_TARGET,
    GATE_FLAPPING_RATE,
    GATE_RECOVERY_TURNS,
    GATE_CPU_P50_MS,
    CANONICAL_BASELINES,
)
from .env import SimUserEnvEKF
from .models import (
    Model1_JointRawBaseline,
    Model2_OpenLoopSSF,
    Model3_EKF,
    Model4_UKF,
)

def generate_trajectory(seed: int, regime: str, language: str = "English", turns: int = 30) -> List[Dict]:
    env = SimUserEnvEKF(seed=seed, regime=regime, language=language)
    traj = [env.reset()]
    for _ in range(turns - 1):
        traj.append(env.step())
    return traj

def evaluate_model_pipeline(model, trajectories: List[List[Dict]]) -> Dict:
    all_true = []
    all_pred = []
    flapping_counts = 0
    total_acc_transitions = 0
    contradiction_recoveries = []
    h1_in_cone = 0
    h2_in_cone = 0
    total_horizon_points = 0
    innovations = []
    kalman_gains = []
    
    for traj in trajectories:
        model.reset(traj[0]["z_true"])
        prev_vel = None
        prev_acc = None
        recovering = False
        recovery_turn_count = 0
        
        for t_idx, step in enumerate(traj):
            z_true = step["z_true"]
            x = step["features_23d"]
            latency = step["interaction_latency"]
            pause_ratio = step["pause_ratio"]
            
            z_pred = model.step(x, latency=latency, pause_ratio=pause_ratio)
            
            all_true.append(z_true)
            all_pred.append(z_pred)
            
            if hasattr(model, "last_innovation"):
                innovations.append(np.abs(model.last_innovation))
            if hasattr(model, "last_kalman_gain"):
                kalman_gains.append(model.last_kalman_gain)
                
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
    
    res = {
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
    if innovations:
        res["mean_innovation"] = [float(x) for x in np.mean(innovations, axis=0)]
    if kalman_gains:
        res["mean_kalman_gain"] = [float(x) for x in np.mean(kalman_gains, axis=0)]
    return res

def run_all_experiments() -> Dict:
    print("=" * 65)
    print("Executing Phase 22-EKF: Kalman-Based Semantic State Formation")
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
            
    X_train = np.array([step["features_23d"] for traj in train_trajs for step in traj])
    Y_train = np.array([step["z_true"] for traj in train_trajs for step in traj])
    
    # 2. Train Models M1 - M4
    print("\n[Step 2] Training Models (Joint Raw, Open-Loop SSF, EKF, UKF)...")
    m1 = Model1_JointRawBaseline()
    m1.fit(X_train, Y_train)
    
    m2 = Model2_OpenLoopSSF()
    m2.fit(X_train, Y_train)
    
    m3 = Model3_EKF(dt=1.0)
    m3.fit(X_train, Y_train)
    
    m4 = Model4_UKF(dt=1.0)
    m4.fit(X_train, Y_train)
    
    # Latency Benchmark
    sample_x = X_train[0]
    latencies = {}
    for name, model in [("M1_Raw", m1), ("M2_SSF", m2), ("M3_EKF", m3), ("M4_UKF", m4)]:
        lats = []
        for _ in range(500):
            t0 = time.perf_counter()
            model.step(sample_x, latency=1.2, pause_ratio=0.3)
            lats.append((time.perf_counter() - t0) * 1000.0)
        latencies[name] = {
            "p50_ms": float(np.percentile(lats, 50)),
            "p95_ms": float(np.percentile(lats, 95)),
        }
        
    # 3. Primary Evaluation on Held-Out Trajectories
    print("\n[Step 3] Evaluating Primary Comparison Models...")
    eval_m1 = evaluate_model_pipeline(m1, held_out_trajs)
    eval_m1["latency"] = latencies["M1_Raw"]
    
    eval_m2 = evaluate_model_pipeline(m2, held_out_trajs)
    eval_m2["latency"] = latencies["M2_SSF"]
    
    eval_m3 = evaluate_model_pipeline(m3, held_out_trajs)
    eval_m3["latency"] = latencies["M3_EKF"]
    
    eval_m4 = evaluate_model_pipeline(m4, held_out_trajs)
    eval_m4["latency"] = latencies["M4_UKF"]
    
    # Oracle Control
    y_he_all = np.vstack([np.array([step["z_true"] for step in traj]) for traj in held_out_trajs])
    pred_oracle = y_he_all + np.random.RandomState(42).normal(0, 0.05, size=y_he_all.shape)
    oracle_mse = float(np.mean((y_he_all - pred_oracle) ** 2))
    oracle_mae = float(np.mean(np.abs(y_he_all - pred_oracle)))
    oracle_r2 = float(1.0 - (oracle_mse / max(float(np.var(y_he_all)), 1e-6)))
    eval_oracle = {"r2": oracle_r2, "mae": oracle_mae, "mse": oracle_mse}
    
    print(f"  -> M1 Joint Raw Baseline: Held-Out R^2 = {eval_m1['r2']:.4f} (Fast={eval_m1['fast_r2']:.4f}, Slow={eval_m1['slow_r2']:.4f})")
    print(f"  -> M2 Open-Loop SSF:      Held-Out R^2 = {eval_m2['r2']:.4f} (Fast={eval_m2['fast_r2']:.4f}, Slow={eval_m2['slow_r2']:.4f})")
    print(f"  -> M3 EKF + OU Prior:     Held-Out R^2 = {eval_m3['r2']:.4f} (Fast={eval_m3['fast_r2']:.4f}, Slow={eval_m3['slow_r2']:.4f})")
    print(f"  -> M4 UKF + OU Prior:     Held-Out R^2 = {eval_m4['r2']:.4f} (Fast={eval_m4['fast_r2']:.4f}, Slow={eval_m4['slow_r2']:.4f})")
    print(f"  -> Oracle Control:        Held-Out R^2 = {eval_oracle['r2']:.4f}, MAE = {eval_oracle['mae']:.4f}")

    # 4. Cross-Lingual Evaluation (EN, VI, JA) on EKF
    print("\n[Step 4] Evaluating Cross-Lingual Parity (EN, VI, JA)...")
    lang_results = {}
    for lang in LANGUAGES:
        lang_trajs = []
        for s in HELD_OUT_SEEDS:
            for r in STRESS_REGIMES:
                lang_trajs.append(generate_trajectory(seed=s, regime=r, language=lang, turns=30))
        lang_eval = evaluate_model_pipeline(m3, lang_trajs)
        lang_results[lang] = {"r2": lang_eval["r2"], "mae": lang_eval["mae"], "mse": lang_eval["mse"]}
        print(f"  -> Language {lang}: Held-Out R^2 = {lang_eval['r2']:.4f}, MAE = {lang_eval['mae']:.4f}")

    # 5. Scientific Controls
    print("\n[Step 5] Running Scientific Controls...")
    # Control A: Random Measurement Matrix on EKF
    ctrl_a_model = Model3_EKF(dt=1.0)
    ctrl_a_model.W_obs = np.random.RandomState(42).randn(6, 23)
    ctrl_a_model.b_obs = np.zeros(6)
    ctrl_a_model.R = 0.05 * np.eye(6)
    ctrl_a = evaluate_model_pipeline(ctrl_a_model, held_out_trajs)
    
    # Control B: Shuffled Temporal Order on EKF
    shuffled_trajs = []
    for traj in held_out_trajs:
        shuffled = list(traj)
        np.random.RandomState(42).shuffle(shuffled)
        shuffled_trajs.append(shuffled)
    ctrl_b = evaluate_model_pipeline(m3, shuffled_trajs)
    
    # Control C: Shuffled Latent Targets on EKF
    ctrl_c_trajs = []
    for traj in held_out_trajs:
        c_traj = []
        for s in traj:
            s_copy = dict(s)
            s_copy["z_true"] = np.random.RandomState(137).permutation(s["z_true"])
            c_traj.append(s_copy)
        ctrl_c_trajs.append(c_traj)
    ctrl_c = evaluate_model_pipeline(m3, ctrl_c_trajs)
    
    controls = {
        "Control_A_Random_Projection": {"r2": ctrl_a["r2"], "mae": ctrl_a["mae"], "mse": ctrl_a["mse"]},
        "Control_B_Shuffled_Temporal_Order": {"r2": ctrl_b["r2"], "mae": ctrl_b["mae"], "mse": ctrl_b["mse"]},
        "Control_C_Shuffled_Targets": {"r2": ctrl_c["r2"], "mae": ctrl_c["mae"], "mse": ctrl_c["mse"]},
        "Control_D_Oracle_Observation": eval_oracle,
    }

    # 6. Gates Evaluation
    p50_ekf_ms = latencies["M3_EKF"]["p50_ms"]
    gates = {
        "G_EKF1_OVERALL_R2_TARGET": "PASS" if eval_m3["r2"] >= GATE_OVERALL_R2_TARGET else "FAIL",
        "G_EKF2_FAST_R2_TARGET": "PASS" if eval_m3["fast_r2"] >= GATE_FAST_R2_TARGET else "FAIL",
        "G_EKF3_DOWNSTREAM_FLAPPING": "PASS" if eval_m3["flapping_rate"] <= GATE_FLAPPING_RATE else "FAIL",
        "G_EKF4_CONTRADICTION_RECOVERY": "PASS" if eval_m3["contradiction_recovery_turns"] <= GATE_RECOVERY_TURNS else "FAIL",
        "G_EKF5_CPU_LATENCY": "PASS" if p50_ekf_ms <= GATE_CPU_P50_MS else "FAIL",
    }

    results = {
        "models": {
            "M1_JointRawBaseline": eval_m1,
            "M2_OpenLoopSSF": eval_m2,
            "M3_EKF_OU_Prior": eval_m3,
            "M4_UKF_OU_Prior": eval_m4,
            "OracleControl": eval_oracle,
        },
        "latencies": latencies,
        "languages": lang_results,
        "controls": controls,
        "gates": gates,
        "peak_held_out_r2": max(eval_m1["r2"], eval_m2["r2"], eval_m3["r2"], eval_m4["r2"]),
        "canonical_baselines": CANONICAL_BASELINES,
    }

    print("\n[Step 6] Writing Results Artifacts...")
    out_dir = os.path.join("evaluation_artifacts", "phase22_ekf")
    os.makedirs(out_dir, exist_ok=True)
    
    with open(os.path.join(out_dir, "raw_measurements.json"), "w", encoding="utf-8") as f:
        json.dump(results, f, indent=2)
        
    with open(os.path.join(out_dir, "gate_results.json"), "w", encoding="utf-8") as f:
        json.dump(gates, f, indent=2)
        
    print(f"Phase 22-EKF completed successfully. Results in {out_dir}")
    return results

if __name__ == "__main__":
    run_all_experiments()
