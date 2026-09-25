"""
Canonical Phase 22-XR Experiment Runner.
Executes XR-E1 through XR-E8 and Ablations A0 through A7.
Usage:
    python tests/evaluation/phase22_xr/run_experiments.py --experiment all
    python tests/evaluation/phase22_xr/run_experiments.py --experiment xr_e1
"""
import argparse
import json
import os
import sys
import time
from typing import Dict, Any
import numpy as np

# Adjust path for isolated execution
curr_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.abspath(os.path.join(curr_dir, "..", "..", ".."))
if parent_dir not in sys.path:
    sys.path.insert(0, parent_dir)

from tests.evaluation.phase22_xr.seeds import EVAL_SEEDS
from tests.evaluation.phase22_xr.experiments import (
    run_xr_e1,
    run_xr_e2,
    run_xr_e3,
    run_xr_e4,
    run_xr_e5,
    run_xr_e6,
    run_xr_e7,
    run_xr_e8,
)
from tests.evaluation.phase22_xr.baselines import (
    RandomBaseline,
    B4SurrogateModel,
    LightweightCalibratedModel,
    DiscreteBayesTracker,
)
from tests.evaluation.phase22_xr.continuous import BucyKalmanFilter
from tests.evaluation.phase22_xr.laya import LayaObservationAdapter
from tests.evaluation.phase22_xr.simulator.sim_user_env_v2 import SimUserEnvV2
from tests.evaluation.phase22_xr.metrics import compute_r2_score, compute_flapping_rate

def run_ablations_matrix(seeds=EVAL_SEEDS) -> Dict[str, Any]:
    print("Running Ablation Matrix A0-A7 across seeds:", seeds)
    ablations = ["A0", "A1", "A2", "A3", "A4", "A5", "A6", "A7"]
    results = {}
    
    for abl in ablations:
        scores, flaps = [], []
        for s in seeds:
            env = SimUserEnvV2(seed=s, regime="Canonical")
            kf = BucyKalmanFilter()
            d_track = DiscreteBayesTracker()
            
            if abl == "A0":
                m_rand = RandomBaseline()
            elif abl in ["A1", "A2"]:
                m_b4 = B4SurrogateModel(seed=s)
            elif abl == "A3":
                m_laya_uncal = LayaObservationAdapter(calibrated=False)
            elif abl == "A5":
                m_b1 = LightweightCalibratedModel(seed=s)
            else:
                m_laya_cal = LayaObservationAdapter(calibrated=True)
                
            y_t, y_p, states = [], [], []
            for _ in range(120):
                step = env.step()
                if abl == "A0":
                    p = m_rand.observe(step.utterance, step.acoustic_features)
                    conf = 1.0 / 6.0
                elif abl in ["A1", "A2"]:
                    p, conf = m_b4.observe(step.utterance, step.acoustic_features)
                elif abl == "A3":
                    res = m_laya_uncal.observe(step.utterance, step.acoustic_features)
                    p, conf = res["probabilities"], res["confidence"]
                elif abl == "A5":
                    p, conf = m_b1.observe(step.utterance, step.acoustic_features)
                else:
                    res = m_laya_cal.observe(step.utterance, step.acoustic_features)
                    p, conf = res["probabilities"], res["confidence"]
                    
                if abl in ["A0", "A1", "A3", "A4"]:
                    _, d_dom = d_track.update(p)
                    states.append(d_dom)
                    y_p.append(np.ones(6) * (d_dom / 5.0))
                else:
                    c_state = kf.update(p, conf)
                    states.append(int(np.argmax(c_state.z)))
                    y_p.append(c_state.z)
                y_t.append(step.true_latent_state)
                
            scores.append(compute_r2_score(np.array(y_t), np.array(y_p)))
            flaps.append(compute_flapping_rate(states))
            
        results[abl] = {
            "mean_R2": float(np.mean(scores)),
            "std_R2": float(np.std(scores)),
            "mean_flapping": float(np.mean(flaps)),
            "std_flapping": float(np.std(flaps)),
        }
    return results

def main():
    parser = argparse.ArgumentParser(description="Phase 22-XR Experiment Runner")
    parser.add_argument("--experiment", default="all", choices=["all", "xr_e1", "xr_e2", "xr_e3", "xr_e4", "xr_e5", "xr_e6", "xr_e7", "xr_e8", "ablations"])
    parser.add_argument("--seed", type=int, default=42)
    parser.add_argument("--output", default="evaluation_artifacts/phase22_xr")
    args = parser.parse_args()
    
    os.makedirs(args.output, exist_ok=True)
    raw_data = {}
    
    print("=" * 70)
    print("LUCIA PHASE 22-XR EXPERIMENT RUNNER")
    print(f"Target: {args.experiment} | Seed: {args.seed} | Output: {args.output}")
    print("=" * 70)
    
    t_start = time.time()
    
    if args.experiment in ["all", "xr_e1"]:
        raw_data["XR-E1"] = run_xr_e1(seed=args.seed)
    if args.experiment in ["all", "xr_e2"]:
        raw_data["XR-E2"] = run_xr_e2(seed=args.seed)
    if args.experiment in ["all", "xr_e3"]:
        raw_data["XR-E3"] = run_xr_e3(seed=args.seed)
    if args.experiment in ["all", "xr_e4"]:
        raw_data["XR-E4"] = run_xr_e4(seed=args.seed)
    if args.experiment in ["all", "xr_e5"]:
        raw_data["XR-E5"] = run_xr_e5(seed=args.seed)
    if args.experiment in ["all", "xr_e6"]:
        raw_data["XR-E6"] = run_xr_e6(seed=args.seed)
    if args.experiment in ["all", "xr_e7"]:
        raw_data["XR-E7"] = run_xr_e7(seed=args.seed)
    if args.experiment in ["all", "xr_e8"]:
        raw_data["XR-E8"] = run_xr_e8(seed=args.seed)
    if args.experiment in ["all", "ablations"]:
        raw_data["Ablations"] = run_ablations_matrix()
        
    # Persist raw measurements
    raw_path = os.path.join(args.output, "raw_measurements.json")
    with open(raw_path, "w") as f:
        json.dump(raw_data, f, indent=2)
    print(f"\n[DONE] Saved authoritative raw measurements to: {raw_path}")
    print(f"Execution took {time.time() - t_start:.2f} seconds.")

if __name__ == "__main__":
    main()
