"""
Exploratory Diagnostic Simulation: Tick-by-Tick PAD Trajectories (T = 1..12).

Calculates step-by-step state trajectories in PAD space for:
1. Protocol v1.4 templates (Low, Med, High)
2. Historical Path C templates (Low, Med, High)

Outputs trajectory tables and displacement metrics to diagnose Gate 2 compression.
"""

from __future__ import annotations

import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent.parent.parent
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

import json
from typing import Dict, List
import numpy as np

from src.core.gating.stimulus_processor import StimulusProcessor
from src.core.emotion.emotion_core import EmotionCore
from src.core.inference.active_inference import ActiveInferenceEngine, ActiveInferenceConfig
from src.core.config import StimulusConfig, EmotionConfig
from tests.evaluation_phase22.fixtures.probes_h1_v14 import (
    _SL_TEMPLATES as sl_v14,
    _SM_TEMPLATES as sm_v14,
    _SH_TEMPLATES as sh_v14,
)
from tests.evaluation_phase22.fixtures.probes_h1_path_c import (
    _SL_TEMPLATES as sl_pc,
    _SM_TEMPLATES as sm_pc,
    _SH_TEMPLATES as sh_pc,
)


def run_trajectory_simulation(templates: List[str], label: str) -> Dict[str, Any]:
    sp = StimulusProcessor(StimulusConfig())
    core = EmotionCore(EmotionConfig())
    ai = ActiveInferenceEngine(ActiveInferenceConfig())

    # Form concrete texts with idx=1
    texts = [t.format(idx=1) for t in templates]
    N = len(texts)

    # We will record PAD at t = 0..12 for each text
    # Array shape: (N, 13, 3)
    pad_trajectories = np.zeros((N, 13, 3), dtype=np.float64)
    s_trajectories = np.zeros((N, 13), dtype=np.float64)

    for i, txt in enumerate(texts):
        core.reset_to_resting()
        ai.reset()
        p0 = core.get_pad_state()
        p0_vec = np.array([p0.pleasure, p0.arousal, p0.dominance])
        pad_trajectories[i, 0] = p0_vec
        s_trajectories[i, 0] = 0.0

        stim = sp.encode(txt)

        p_curr = p0
        for t in range(1, 13):
            token = core.push_stimulus(stim)
            p_curr = core.commit_stimulus(token)
            pt_vec = np.array([p_curr.pleasure, p_curr.arousal, p_curr.dominance])
            pad_trajectories[i, t] = pt_vec
            s_trajectories[i, t] = float(ai.step(p0, p_curr))

    # Mean across texts
    mean_pad = np.mean(pad_trajectories, axis=0) # (13, 3)
    mean_s = np.mean(s_trajectories, axis=0)     # (13,)

    return {
        "label": label,
        "mean_pad": mean_pad,
        "mean_s": mean_s,
        "all_s": s_trajectories,
    }


def main():
    print("=" * 88)
    print("TICK-BY-TICK PAD TRAJECTORY SIMULATION (t = 0..12 ticks, dt = 0.10s)")
    print("=" * 88)

    suite = [
        ("v1.4 Low", sl_v14),
        ("v1.4 Med", sm_v14),
        ("v1.4 High", sh_v14),
        ("Path C Low", sl_pc),
        ("Path C Med", sm_pc),
        ("Path C High", sh_pc),
    ]

    results = {}
    for name, tmpls in suite:
        results[name] = run_trajectory_simulation(tmpls, name)

    print("\n[Table S1] S_observed Trajectory across t = 1..12 ticks:")
    print(f"{'t':<3} | {'v1.4 Low':<10} | {'v1.4 Med':<10} | {'v1.4 High':<10} | {'Path C Low':<10} | {'Path C Med':<10} | {'Path C High':<10}")
    print("-" * 75)

    for t in range(1, 13):
        print(
            f"{t:2d}  | "
            f"{results['v1.4 Low']['mean_s'][t]:10.4f} | "
            f"{results['v1.4 Med']['mean_s'][t]:10.4f} | "
            f"{results['v1.4 High']['mean_s'][t]:10.4f} | "
            f"{results['Path C Low']['mean_s'][t]:10.4f} | "
            f"{results['Path C Med']['mean_s'][t]:10.4f} | "
            f"{results['Path C High']['mean_s'][t]:10.4f}"
        )

    print("\n[Table S2] Separation Margins across t = 1..12 ticks:")
    print(f"{'t':<3} | {'v1.4 dML':<10} | {'v1.4 dHM':<10} | {'Path C dML':<10} | {'Path C dHM':<10} | {'Diff dHM (v14 - PC)':<20}")
    print("-" * 75)

    for t in range(1, 13):
        v14_dml = results['v1.4 Med']['mean_s'][t] - results['v1.4 Low']['mean_s'][t]
        v14_dhm = results['v1.4 High']['mean_s'][t] - results['v1.4 Med']['mean_s'][t]
        pc_dml = results['Path C Med']['mean_s'][t] - results['Path C Low']['mean_s'][t]
        pc_dhm = results['Path C High']['mean_s'][t] - results['Path C Med']['mean_s'][t]
        diff_dhm = v14_dhm - pc_dhm
        print(f"{t:2d}  | {v14_dml:+10.4f} | {v14_dhm:+10.4f} | {pc_dml:+10.4f} | {pc_dhm:+10.4f} | {diff_dhm:+20.4f}")

    print("\n[Table S3] Detailed PAD Coordinates for v1.4 Med vs High at key ticks:")
    print(f"{'t':<3} | {'v1.4 Med (P, A, D)':<28} | {'v1.4 High (P, A, D)':<28}")
    print("-" * 65)
    for t in (1, 2, 3, 4, 6, 8, 10, 12):
        mp = results['v1.4 Med']['mean_pad'][t]
        hp = results['v1.4 High']['mean_pad'][t]
        print(f"{t:2d}  | ({mp[0]:+.3f}, {mp[1]:+.3f}, {mp[2]:+.3f})               | ({hp[0]:+.3f}, {hp[1]:+.3f}, {hp[2]:+.3f})")


if __name__ == "__main__":
    main()
