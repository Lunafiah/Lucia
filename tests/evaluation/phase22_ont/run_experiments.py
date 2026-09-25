"""
Experiment Runner for Phase 22-ONT:
Target Ontology Redesign Study.
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
    OBSERVABLE_4D_DIMS,
    SLOW_MEMORY_DIMS,
    LEGACY_6D_DIMS,
    GATE_OBSERVABLE_4D_R2,
    GATE_TARGET_RECOVERY_TURNS,
    GATE_FLAPPING_RATE,
    GATE_CPU_P50_MS,
    CANONICAL_BASELINES,
)
from .env import SimUserEnvONT
from .models import (
    Ontology1_Legacy6D,
    Ontology2_Decoupled4D2D,
    Ontology3_MultiTimescaleConsolidation,
)

def generate_trajectory(seed: int, regime: str, language: str = "English", turns: int = 30) -> List[Dict]:
    env = SimUserEnvONT(seed=seed, regime=regime, language=language)
    traj = [env.reset()]
    for _ in range(turns - 1):
        traj.append(env.step())
    return traj

def evaluate_ontology_pipeline(ont_variant: str, model, trajectories: List[List[Dict]]) -> Dict:
    all_u_true = []
    all_u_pred = []
    all_m_true = []
    all_m_pred = []
    all_z_true = []
    all_z_pred = []
    
    flapping_counts = 0
    total_acc_transitions = 0
    contradiction_recoveries = []
    h1_in_cone = 0
    h2_in_cone = 0
    total_horizon_points = 0
    
    for traj in trajectories:
        if ont_variant == "O1":
            model.reset(traj[0]["z_legacy_true"])
        elif ont_variant == "O2":
            model.reset(traj[0]["u_true"], traj[0]["m_true"])
        elif ont_variant == "O3":
            model.reset(traj[0]["u_true"], traj[0]["m_true"])
            
        prev_vel = None
        prev_acc = None
        recovering = False
        recovery_turn_count = 0
        
        for t_idx, step in enumerate(traj):
            u_true = step["u_true"]
            m_true = step["m_true"]
            z_true = step["z_legacy_true"]
            x = step["features_23d"]
            
            if ont_variant == "O1":
                z_pred = model.step(x)
                u_pred = z_pred[0:4]
                m_pred = z_pred[4:6]
            elif ont_variant == "O2":
                u_pred, m_pred = model.step(x)
                z_pred = np.concatenate([u_pred, m_pred])
            elif ont_variant == "O3":
                u_pred, m_pred, _ = model.step(x)
                z_pred = np.concatenate([u_pred, m_pred])
                
            all_u_true.append(u_true)
            all_u_pred.append(u_pred)
            all_m_true.append(m_true)
            all_m_pred.append(m_pred)
            all_z_true.append(z_true)
            all_z_pred.append(z_pred)
            
            # Flapping detection on 4D Observable state
            if prev_vel is not None:
                curr_vel = u_pred - prev_vel
                if prev_acc is not None:
                    curr_acc = curr_vel - prev_acc
                    for d in range(4):
                        if (curr_acc[d] * prev_acc[d]) < -1e-4:
                            flapping_counts += 1
                        total_acc_transitions += 1
                    prev_acc = curr_acc
                else:
                    prev_acc = curr_vel
                prev_vel = u_pred
            else:
                prev_vel = u_pred
                
            # Contradiction recovery at t=15 (measured on valence u1)
            if step["regime"] in ["ContradictionShock", "CombinedStress"]:
                if t_idx == 15:
                    recovering = True
                    recovery_turn_count = 0
                elif recovering:
                    recovery_turn_count += 1
                    err_val = abs(u_pred[1] - u_true[1])
                    if err_val < 0.25 or recovery_turn_count >= 5:
                        contradiction_recoveries.append(recovery_turn_count)
                        recovering = False
                        
            # Horizon coverage on 4D observable state
            if t_idx + 1 < len(traj):
                u_true_h1 = traj[t_idx + 1]["u_true"]
                if np.linalg.norm(u_pred - u_true_h1) <= 0.35:
                    h1_in_cone += 1
            if t_idx + 2 < len(traj):
                u_true_h2 = traj[t_idx + 2]["u_true"]
                if np.linalg.norm(u_pred - u_true_h2) <= 0.50:
                    h2_in_cone += 1
            total_horizon_points += 1

    U_true = np.array(all_u_true)
    U_pred = np.array(all_u_pred)
    M_true = np.array(all_m_true)
    M_pred = np.array(all_m_pred)
    Z_true = np.array(all_z_true)
    Z_pred = np.array(all_z_pred)
    
    # 4D Observable state metrics
    mse_u = float(np.mean((U_true - U_pred) ** 2))
    mae_u = float(np.mean(np.abs(U_true - U_pred)))
    r2_u = float(1.0 - (mse_u / max(float(np.var(U_true)), 1e-6)))
    
    # Per-dimension 4D R2
    dim_u_r2 = {}
    for d in range(4):
        d_mse = float(np.mean((U_true[:, d] - U_pred[:, d]) ** 2))
        d_var = float(np.var(U_true[:, d]))
        dim_u_r2[OBSERVABLE_4D_DIMS[d]] = float(1.0 - (d_mse / max(d_var, 1e-6)))
        
    # 2D Slow state metrics
    mse_m = float(np.mean((M_true - M_pred) ** 2))
    mae_m = float(np.mean(np.abs(M_true - M_pred)))
    r2_m = float(1.0 - (mse_m / max(float(np.var(M_true)), 1e-6)))
    dim_m_r2 = {}
    for d in range(2):
        d_mse = float(np.mean((M_true[:, d] - M_pred[:, d]) ** 2))
        d_var = float(np.var(M_true[:, d]))
        dim_m_r2[SLOW_MEMORY_DIMS[d]] = float(1.0 - (d_mse / max(d_var, 1e-6)))
        
    # Full 6D combined metrics
    mse_z = float(np.mean((Z_true - Z_pred) ** 2))
    mae_z = float(np.mean(np.abs(Z_true - Z_pred)))
    r2_z = float(1.0 - (mse_z / max(float(np.var(Z_true)), 1e-6)))
    
    flapping_rate = float(flapping_counts / max(total_acc_transitions, 1))
    mean_recovery = float(np.mean(contradiction_recoveries)) if contradiction_recoveries else 1.0
    h1_cov = float(h1_in_cone / max(total_horizon_points, 1))
    h2_cov = float(h2_in_cone / max(total_horizon_points, 1))
    
    return {
        "r2_observable_4d": r2_u,
        "mae_observable_4d": mae_u,
        "mse_observable_4d": mse_u,
        "dim_observable_r2": dim_u_r2,
        "r2_slow_memory_2d": r2_m,
        "mae_slow_memory_2d": mae_m,
        "mse_slow_memory_2d": mse_m,
        "dim_slow_r2": dim_m_r2,
        "r2_overall_6d": r2_z,
        "mae_overall_6d": mae_z,
        "flapping_rate": flapping_rate,
        "contradiction_recovery_turns": mean_recovery,
        "trajectory_h1_coverage": h1_cov,
        "trajectory_h2_coverage": h2_cov,
    }

def run_all_experiments() -> Dict:
    print("=" * 65)
    print("Executing Phase 22-ONT: Target Ontology Redesign Study")
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
    U_train = np.array([step["u_true"] for traj in train_trajs for step in traj])
    Z_train = np.array([step["z_legacy_true"] for traj in train_trajs for step in traj])
    
    # 2. Train Models O1, O2, O3
    print("\n[Step 2] Training Ontology Variants (O1 Legacy 6D, O2 Decoupled, O3 Multi-Timescale)...")
    o1 = Ontology1_Legacy6D()
    o1.fit(X_train, Z_train)
    
    o2 = Ontology2_Decoupled4D2D()
    o2.fit(X_train, U_train)
    
    o3 = Ontology3_MultiTimescaleConsolidation(dt=1.0)
    o3.fit(X_train, U_train)
    
    # Benchmarking Latencies
    sample_x = X_train[0]
    latencies = {}
    for name, model, ont_var in [("O1_Legacy6D", o1, "O1"), ("O2_Decoupled", o2, "O2"), ("O3_MultiTimescale", o3, "O3")]:
        lats = []
        for _ in range(500):
            t0 = time.perf_counter()
            model.step(sample_x)
            lats.append((time.perf_counter() - t0) * 1000.0)
        latencies[name] = {
            "p50_ms": float(np.percentile(lats, 50)),
            "p95_ms": float(np.percentile(lats, 95)),
        }
        
    # 3. Evaluate Models on Held-Out Seeds
    print("\n[Step 3] Evaluating Ontology Variants on Held-Out Seeds...")
    eval_o1 = evaluate_ontology_pipeline("O1", o1, held_out_trajs)
    eval_o1["latency"] = latencies["O1_Legacy6D"]
    
    eval_o2 = evaluate_ontology_pipeline("O2", o2, held_out_trajs)
    eval_o2["latency"] = latencies["O2_Decoupled"]
    
    eval_o3 = evaluate_ontology_pipeline("O3", o3, held_out_trajs)
    eval_o3["latency"] = latencies["O3_MultiTimescale"]
    
    print(f"  -> O1 Legacy 6D:         Overall R^2={eval_o1['r2_overall_6d']:.4f}, Observable 4D R^2={eval_o1['r2_observable_4d']:.4f}, Slow 2D R^2={eval_o1['r2_slow_memory_2d']:.4f}")
    print(f"  -> O2 Decoupled 4D+2D:    Observable 4D R^2={eval_o2['r2_observable_4d']:.4f}, Slow Memory R^2={eval_o2['r2_slow_memory_2d']:.4f}")
    print(f"  -> O3 Multi-Timescale:    Observable 4D R^2={eval_o3['r2_observable_4d']:.4f}, Relational Memory R^2={eval_o3['r2_slow_memory_2d']:.4f}, Recovery={eval_o3['contradiction_recovery_turns']:.2f} turns")

    # 4. Cross-Lingual Evaluation (EN, VI, JA) on O3
    print("\n[Step 4] Evaluating Cross-Lingual Invariance on O3 (EN, VI, JA)...")
    lang_results = {}
    for lang in LANGUAGES:
        lang_trajs = []
        for s in HELD_OUT_SEEDS:
            for r in STRESS_REGIMES:
                lang_trajs.append(generate_trajectory(seed=s, regime=r, language=lang, turns=30))
        lang_eval = evaluate_ontology_pipeline("O3", o3, lang_trajs)
        lang_results[lang] = {
            "r2_observable_4d": lang_eval["r2_observable_4d"],
            "mae_observable_4d": lang_eval["mae_observable_4d"],
            "r2_slow_memory_2d": lang_eval["r2_slow_memory_2d"],
        }
        print(f"  -> Language {lang}: Observable 4D R^2 = {lang_eval['r2_observable_4d']:.4f}, MAE = {lang_eval['mae_observable_4d']:.4f}")

    # 5. Scientific Controls
    print("\n[Step 5] Executing Scientific Controls...")
    # Control A: Random Projection on O3
    ctrl_a_model = Ontology3_MultiTimescaleConsolidation()
    ctrl_a_model.W_u = np.random.RandomState(42).randn(4, 23)
    ctrl_a_model.b_u = np.zeros(4)
    ctrl_a = evaluate_ontology_pipeline("O3", ctrl_a_model, held_out_trajs)
    
    # Control B: Shuffled Temporal Order on O3
    shuffled_trajs = []
    for traj in held_out_trajs:
        shuffled = list(traj)
        np.random.RandomState(42).shuffle(shuffled)
        shuffled_trajs.append(shuffled)
    ctrl_b = evaluate_ontology_pipeline("O3", o3, shuffled_trajs)
    
    # Control C: Shuffled Latent Targets on O3
    ctrl_c_trajs = []
    for traj in held_out_trajs:
        c_traj = []
        for s in traj:
            s_copy = dict(s)
            s_copy["u_true"] = np.random.RandomState(137).permutation(s["u_true"])
            s_copy["m_true"] = np.random.RandomState(137).permutation(s["m_true"])
            c_traj.append(s_copy)
        ctrl_c_trajs.append(c_traj)
    ctrl_c = evaluate_ontology_pipeline("O3", o3, ctrl_c_trajs)
    
    # Control D: Oracle Observable 4D
    U_he_all = np.vstack([np.array([step["u_true"] for step in traj]) for traj in held_out_trajs])
    pred_oracle_u = U_he_all + np.random.RandomState(42).normal(0, 0.05, size=U_he_all.shape)
    oracle_mse = float(np.mean((U_he_all - pred_oracle_u) ** 2))
    oracle_mae = float(np.mean(np.abs(U_he_all - pred_oracle_u)))
    oracle_r2 = float(1.0 - (oracle_mse / max(float(np.var(U_he_all)), 1e-6)))
    ctrl_d = {"r2_observable_4d": oracle_r2, "mae_observable_4d": oracle_mae, "mse_observable_4d": oracle_mse}
    
    controls = {
        "Control_A_Random_Projection": {"r2_observable_4d": ctrl_a["r2_observable_4d"], "mae_observable_4d": ctrl_a["mae_observable_4d"]},
        "Control_B_Shuffled_Temporal_Order": {"r2_observable_4d": ctrl_b["r2_observable_4d"], "mae_observable_4d": ctrl_b["mae_observable_4d"]},
        "Control_C_Shuffled_Targets": {"r2_observable_4d": ctrl_c["r2_observable_4d"], "mae_observable_4d": ctrl_c["mae_observable_4d"]},
        "Control_D_Oracle_Observable": ctrl_d,
    }

    # 6. Gates Evaluation
    p50_o3 = latencies["O3_MultiTimescale"]["p50_ms"]
    gates = {
        "G_ONT1_OBSERVABLE_4D_R2_TARGET": "PASS" if eval_o3["r2_observable_4d"] >= GATE_OBSERVABLE_4D_R2 else "FAIL",
        "G_ONT2_CONTRADICTION_RECOVERY": "PASS" if eval_o3["contradiction_recovery_turns"] <= GATE_TARGET_RECOVERY_TURNS else "FAIL",
        "G_ONT3_FLAPPING_RATE": "PASS" if eval_o3["flapping_rate"] <= GATE_FLAPPING_RATE else "FAIL",
        "G_ONT4_CPU_LATENCY": "PASS" if p50_o3 <= GATE_CPU_P50_MS else "FAIL",
    }

    results = {
        "ontologies": {
            "O1_Legacy6D": eval_o1,
            "O2_Decoupled4D2D": eval_o2,
            "O3_MultiTimescale": eval_o3,
            "OracleControl": ctrl_d,
        },
        "latencies": latencies,
        "languages": lang_results,
        "controls": controls,
        "gates": gates,
        "peak_observable_4d_r2": eval_o3["r2_observable_4d"],
        "canonical_baselines": CANONICAL_BASELINES,
    }

    print("\n[Step 6] Writing Results Artifacts...")
    out_dir = os.path.join("evaluation_artifacts", "phase22_ont")
    os.makedirs(out_dir, exist_ok=True)
    
    with open(os.path.join(out_dir, "raw_measurements.json"), "w", encoding="utf-8") as f:
        json.dump(results, f, indent=2)
        
    with open(os.path.join(out_dir, "gate_results.json"), "w", encoding="utf-8") as f:
        json.dump(gates, f, indent=2)
        
    print(f"Phase 22-ONT completed successfully. Results in {out_dir}")
    return results

if __name__ == "__main__":
    run_all_experiments()
