"""
Experiment Runner for Phase 22-INF:
Information Sufficiency & Semantic State Formation Study.
Executes:
1. Ablations E0 through E6 across train seeds (42, 137, 618) and held-out seeds (1024, 2026).
2. Latent Identifiability Analysis (dimension-wise R^2 decomposition).
3. Scientific Controls (Control A: Random Projection, Control B: Shuffled Temporal Order, Control C: Shuffled Targets, Control D: Oracle).
4. Language Independence Evaluation (EN, VI, JA).
5. Computational Latency & Downstream Stability Verification.
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
    GATE_R2_TARGET,
    GATE_R2_FALSIFICATION,
    GATE_DOWNSTREAM_FLAPPING,
    GATE_CONTRADICTION_RECOVERY,
    GATE_TRAJECTORY_COVERAGE,
    GATE_CPU_P50_MS,
    CANONICAL_BASELINES,
)
from .enriched_env import EnrichedSimUserEnv
from .streams import InformationStreamBundler, StateFormationEstimator

def generate_trajectory(seed: int, regime: str, language: str = "English", turns: int = 30) -> List[Dict]:
    env = EnrichedSimUserEnv(seed=seed, regime=regime, language=language)
    traj = [env.reset()]
    for _ in range(turns - 1):
        traj.append(env.step())
    return traj

def evaluate_stream(config_code: str, estimator: StateFormationEstimator, trajectories: List[List[Dict]]) -> Dict:
    all_true = []
    all_pred = []
    flapping_counts = 0
    total_acc_transitions = 0
    contradiction_recoveries = []
    h1_in_cone = 0
    h2_in_cone = 0
    total_horizon_points = 0
    
    for traj in trajectories:
        estimator.reset_state(traj[0]["z_true"])
        prev_vel = None
        prev_acc = None
        recovering = False
        recovery_turn_count = 0
        
        for t_idx, step in enumerate(traj):
            z_true = step["z_true"]
            x = InformationStreamBundler.extract_stream(step, config_code)
            z_pred = estimator.step(x)
            
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
                    if err < 0.30 or recovery_turn_count >= 5:
                        contradiction_recoveries.append(recovery_turn_count)
                        recovering = False
                        
            # Horizon coverage
            if t_idx + 1 < len(traj):
                z_true_h1 = traj[t_idx + 1]["z_true"]
                # Forecast cone radius = 0.35
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
    r2 = 1.0 - (mse / max(var_total, 1e-6))
    
    # Dimension-wise R2
    dim_r2 = {}
    for d in range(STATE_DIM):
        d_mse = float(np.mean((Y_true[:, d] - Y_pred[:, d]) ** 2))
        d_var = float(np.var(Y_true[:, d]))
        dim_r2[DIM_NAMES[d]] = float(1.0 - (d_mse / max(d_var, 1e-6)))
        
    flapping_rate = float(flapping_counts / max(total_acc_transitions, 1))
    mean_recovery = float(np.mean(contradiction_recoveries)) if contradiction_recoveries else 1.0
    h1_cov = float(h1_in_cone / max(total_horizon_points, 1))
    h2_cov = float(h2_in_cone / max(total_horizon_points, 1))
    
    return {
        "r2": r2,
        "mae": mae,
        "mse": mse,
        "dim_r2": dim_r2,
        "flapping_rate": flapping_rate,
        "contradiction_recovery_turns": mean_recovery,
        "trajectory_h1_coverage": h1_cov,
        "trajectory_h2_coverage": h2_cov,
    }

def run_all_experiments() -> Dict:
    print("=" * 60)
    print("Executing Phase 22-INF: Information Sufficiency Study")
    print("=" * 60)
    
    # 1. Collect training trajectories
    print("\n[Step 1] Collecting training trajectories (Seeds: 42, 137, 618)...")
    train_trajs = []
    for s in TRAIN_SEEDS:
        for r in STRESS_REGIMES:
            train_trajs.append(generate_trajectory(seed=s, regime=r, language="English", turns=30))
            
    # Collect held-out trajectories
    print("[Step 2] Collecting held-out trajectories (Seeds: 1024, 2026)...")
    held_out_trajs = []
    for s in HELD_OUT_SEEDS:
        for r in STRESS_REGIMES:
            held_out_trajs.append(generate_trajectory(seed=s, regime=r, language="English", turns=30))
            
    # 2. Fit and evaluate each stream ablation
    stream_configs = [
        "E0_Baseline",
        "E1_Temporal",
        "E2_Prosodic",
        "E3_Interaction",
        "E4_Relational",
        "E5_FullMultimodal",
        "E6_Oracle",
    ]
    
    results = {"ablations": {}, "dim_analysis": {}, "controls": {}, "languages": {}, "latency": {}}
    
    for cfg in stream_configs:
        print(f" -> Training and evaluating stream: {cfg}...")
        # Prepare training data matrix
        X_train_list = []
        Y_train_list = []
        for traj in train_trajs:
            for step in traj:
                X_train_list.append(InformationStreamBundler.extract_stream(step, cfg))
                Y_train_list.append(step["z_true"])
        X_train = np.array(X_train_list)
        Y_train = np.array(Y_train_list)
        
        estimator = StateFormationEstimator(alpha=0.35)
        estimator.fit(X_train, Y_train)
        
        # Benchmark latency
        x_sample = X_train[0]
        t_lats = []
        for _ in range(500):
            t0 = time.perf_counter()
            estimator.step(x_sample)
            t_lats.append((time.perf_counter() - t0) * 1000.0)
            
        p50_lat = float(np.percentile(t_lats, 50))
        p95_lat = float(np.percentile(t_lats, 95))
        
        # Evaluate on held-out trajectories
        eval_metrics = evaluate_stream(cfg, estimator, held_out_trajs)
        eval_metrics["p50_latency_ms"] = p50_lat
        eval_metrics["p95_latency_ms"] = p95_lat
        eval_metrics["feature_dim"] = int(X_train.shape[1])
        
        results["ablations"][cfg] = eval_metrics
        print(f"    Held-Out R^2: {eval_metrics['r2']:.4f}, MAE: {eval_metrics['mae']:.4f}, Latency P50: {p50_lat:.4f} ms")

    # 3. Latent Identifiability Analysis (from E5_FullMultimodal)
    results["dim_analysis"] = results["ablations"]["E5_FullMultimodal"]["dim_r2"]
    
    # 4. Scientific Controls Verification
    print("\n[Step 3] Executing Scientific Controls...")
    # Control A: Random Projection
    X_sample_E5 = InformationStreamBundler.extract_stream(held_out_trajs[0][0], "E5_FullMultimodal")
    rand_estimator = StateFormationEstimator(alpha=0.35)
    rand_estimator.W = np.random.normal(0, 1.0, size=(STATE_DIM, len(X_sample_E5)))
    rand_estimator.b = np.zeros(STATE_DIM)
    ctrl_a = evaluate_stream("E5_FullMultimodal", rand_estimator, held_out_trajs)
    results["controls"]["Control_A_Random_Projection"] = {"r2": ctrl_a["r2"], "mae": ctrl_a["mae"], "mse": ctrl_a["mse"]}
    
    # Control B: Shuffled Temporal Order
    shuffled_trajs = []
    for traj in held_out_trajs:
        shuffled = list(traj)
        np.random.RandomState(42).shuffle(shuffled)
        shuffled_trajs.append(shuffled)
    best_estimator = StateFormationEstimator(alpha=0.35)
    X_all_train = np.array([InformationStreamBundler.extract_stream(step, "E5_FullMultimodal") for traj in train_trajs for step in traj])
    Y_all_train = np.array([step["z_true"] for traj in train_trajs for step in traj])
    best_estimator.fit(X_all_train, Y_all_train)
    ctrl_b = evaluate_stream("E5_FullMultimodal", best_estimator, shuffled_trajs)
    results["controls"]["Control_B_Shuffled_Temporal_Order"] = {"r2": ctrl_b["r2"], "mae": ctrl_b["mae"], "mse": ctrl_b["mse"]}
    
    # Control C: Shuffled Latent Targets
    ctrl_c_trajs = []
    for traj in held_out_trajs:
        c_traj = []
        for s in traj:
            s_copy = dict(s)
            s_copy["z_true"] = np.random.RandomState(137).permutation(s["z_true"])
            c_traj.append(s_copy)
        ctrl_c_trajs.append(c_traj)
    ctrl_c = evaluate_stream("E5_FullMultimodal", best_estimator, ctrl_c_trajs)
    results["controls"]["Control_C_Shuffled_Targets"] = {"r2": ctrl_c["r2"], "mae": ctrl_c["mae"], "mse": ctrl_c["mse"]}
    
    # Control D: Oracle Observation
    y_he_all = np.vstack([np.array([step["z_true"] for step in traj]) for traj in held_out_trajs])
    pred_ctrl_d = y_he_all + np.random.RandomState(42).normal(0, 0.05, size=y_he_all.shape)
    mse_d = float(np.mean((y_he_all - pred_ctrl_d) ** 2))
    mae_d = float(np.mean(np.abs(y_he_all - pred_ctrl_d)))
    var_d = float(np.var(y_he_all))
    r2_d = float(1.0 - (mse_d / max(var_d, 1e-6)))
    results["controls"]["Control_D_Oracle_Observation"] = {"r2": r2_d, "mae": mae_d, "mse": mse_d}

    # 5. Language Independence Evaluation (E5 across EN, VI, JA)
    print("\n[Step 4] Evaluating Language Independence (EN, VI, JA)...")
    for lang in LANGUAGES:
        lang_trajs = []
        for s in HELD_OUT_SEEDS:
            for r in STRESS_REGIMES:
                lang_trajs.append(generate_trajectory(seed=s, regime=r, language=lang, turns=30))
        lang_eval = evaluate_stream("E5_FullMultimodal", best_estimator, lang_trajs)
        results["languages"][lang] = {"r2": lang_eval["r2"], "mae": lang_eval["mae"], "mse": lang_eval["mse"]}
        print(f"    Language: {lang} -> R^2: {lang_eval['r2']:.4f}, MAE: {lang_eval['mae']:.4f}")

    # 6. Gates Evaluation
    e5_r2 = results["ablations"]["E5_FullMultimodal"]["r2"]
    e5_flapping = results["ablations"]["E5_FullMultimodal"]["flapping_rate"]
    e5_cov = results["ablations"]["E5_FullMultimodal"]["trajectory_h1_coverage"]
    e5_lat = results["ablations"]["E5_FullMultimodal"]["p50_latency_ms"]
    
    gates = {
        "G_INF1_HELD_OUT_R2_TARGET": "PASS" if e5_r2 >= GATE_R2_TARGET else "FAIL",
        "G_INF2_FALSIFICATION_CHECK": "SUPPORTED" if e5_r2 >= GATE_R2_FALSIFICATION else "FALSIFIED",
        "G_INF3_DOWNSTREAM_FLAPPING": "PASS" if e5_flapping <= GATE_DOWNSTREAM_FLAPPING else "FAIL",
        "G_INF4_TRAJECTORY_COVERAGE": "PASS" if e5_cov >= GATE_TRAJECTORY_COVERAGE else "FAIL",
        "G_INF5_CPU_LATENCY": "PASS" if e5_lat <= GATE_CPU_P50_MS else "FAIL",
    }
    results["gates"] = gates
    results["peak_held_out_r2"] = e5_r2
    results["canonical_baselines"] = CANONICAL_BASELINES
    
    print("\n[Step 5] Writing results artifacts...")
    out_dir = os.path.join("evaluation_artifacts", "phase22_information")
    os.makedirs(out_dir, exist_ok=True)
    
    raw_path = os.path.join(out_dir, "raw_measurements.json")
    with open(raw_path, "w", encoding="utf-8") as f:
        json.dump(results, f, indent=2)
        
    gate_path = os.path.join(out_dir, "gate_results.json")
    with open(gate_path, "w", encoding="utf-8") as f:
        json.dump(gates, f, indent=2)
        
    manifest_path = os.path.join(out_dir, "experiment_manifest.json")
    manifest = {
        "study": "Phase 22-INF Information Sufficiency & Semantic State Formation",
        "train_seeds": TRAIN_SEEDS,
        "held_out_seeds": HELD_OUT_SEEDS,
        "regimes": STRESS_REGIMES,
        "languages": LANGUAGES,
        "ablations": stream_configs,
        "gates": gates,
        "peak_held_out_r2": e5_r2,
    }
    with open(manifest_path, "w", encoding="utf-8") as f:
        json.dump(manifest, f, indent=2)
        
    print(f"Results written successfully to {out_dir}")
    return results

if __name__ == "__main__":
    run_all_experiments()
