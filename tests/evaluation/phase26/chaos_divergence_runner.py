"""
tests/evaluation/phase26/chaos_divergence_runner.py

P26 Blocker 3 — Dynamic Epsilon-Perturbation Chaos Baseline Runner.
Characterizes the natural divergence distribution D_chaos(t, epsilon) of the
multi-turn dynamical limbic ODE system under infinitesimal state perturbations.

GOVERNANCE & BOUNDARIES:
- TEST-ONLY research infrastructure. Zero changes to src/core/** or electron/**.
- Evaluates isolated, ephemeral EmotionCore instances via VirtualClockHarness.
- Uses Common Random Numbers (CRN) for identical multi-turn stimulus sequences.
- Characterizes dynamical sensitivity; does NOT claim C1, C2, C3, or individuality.
- Emits raw telemetry JSON to docs/PhaseDocs/.../evaluation_artifacts/
"""

from __future__ import annotations

import json
import logging
import math
import os
import sys
import time
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

import numpy as np

# Ensure project root in sys.path
PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from src.core.config import EmotionConfig
from src.core.emotion.emotion_core import EmotionCore
from src.core.models import PADState
from tests.evaluation.phase26.determinism.virtual_clock_harness import VirtualClockHarness

logger = logging.getLogger("ChaosDivergenceRunner")

ARTIFACT_DIR = (
    PROJECT_ROOT
    / "docs"
    / "PhaseDocs"
    / "lucia-phase26-Emergent Individuality & Autonomous Preferences"
    / "evaluation_artifacts"
)
ARTIFACT_DIR.mkdir(parents=True, exist_ok=True)
RAW_TELEMETRY_PATH = ARTIFACT_DIR / "step6_dynamic_chaos_baseline_telemetry.json"


@dataclass
class TrajectoryPoint:
    """Snapshot of dynamical state at timestep t."""
    step: int
    virtual_time_sec: float
    # Absolute divergences
    d_fast: float
    d_slow: float
    d_limbic: float
    d_pad: float
    # Relative divergence
    relative_divergence: float
    # Local log growth rate (Lyapunov proxy)
    lyapunov_proxy: Optional[float]


@dataclass
class RunSummary:
    """Summary of a single rollout run at a given epsilon and seed."""
    epsilon: float
    seed: int
    timesteps: int
    dt: float
    max_d_limbic: float
    final_d_limbic: float
    max_d_pad: float
    final_d_pad: float
    mean_relative_divergence: float
    amplification_factor: float
    trajectory: List[TrajectoryPoint]


class DynamicChaosRunner:
    """
    Executes the multi-turn epsilon-perturbation sweep across seeds and timesteps.
    """

    DEFAULT_EPSILONS: Tuple[float, ...] = (
        0.0,
        1e-8,
        1e-7,
        1e-6,
        1e-5,
        1e-4,
        1e-3,
    )

    DEFAULT_SEEDS: Tuple[int, ...] = (1001, 2002, 3003, 4004, 5005)

    def __init__(
        self,
        epsilons: Optional[List[float]] = None,
        seeds: Optional[List[int]] = None,
        timesteps: int = 50,
        dt: float = 0.200,
        output_path: Optional[Path] = RAW_TELEMETRY_PATH,
    ) -> None:
        self.epsilons = list(epsilons) if epsilons is not None else list(self.DEFAULT_EPSILONS)
        self.seeds = list(seeds) if seeds is not None else list(self.DEFAULT_SEEDS)
        self.timesteps = timesteps
        self.dt = dt
        self.output_path = output_path

    def _generate_stimulus_sequence(self, num_steps: int, stimulus_dim: int = 16) -> Dict[int, np.ndarray]:
        """
        Creates a deterministic multi-turn stimulus schedule using CRN.
        Simulates 3 conversational turns spaced across the rollout.
        """
        schedule: Dict[int, np.ndarray] = {}
        # Turn 1 at step 5 (t=1.0s) - Positive collaborative query
        vec1 = np.zeros(stimulus_dim, dtype=np.float64)
        vec1[0] = 0.45  # Valence
        vec1[1] = 0.35  # Arousal
        vec1[2] = 0.20  # Density
        schedule[5] = vec1

        # Turn 2 at step 20 (t=4.0s) - High-intensity investigative prompt
        vec2 = np.zeros(stimulus_dim, dtype=np.float64)
        vec2[0] = 0.20  # Valence
        vec2[1] = 0.60  # Arousal (high cognitive load)
        vec2[2] = 0.50  # Density
        schedule[20] = vec2

        # Turn 3 at step 35 (t=7.0s) - Resolving calm turn
        vec3 = np.zeros(stimulus_dim, dtype=np.float64)
        vec3[0] = 0.50  # Valence
        vec3[1] = -0.20 # Low arousal relaxation
        vec3[2] = 0.10  # Density
        schedule[35] = vec3

        return schedule

    def _run_single_pair(
        self,
        epsilon: float,
        seed: int,
        stimuli: Dict[int, np.ndarray],
    ) -> RunSummary:
        """
        Executes a paired baseline vs perturbed rollout under Common Random Numbers.
        """
        config = EmotionConfig(ode_step_size=self.dt)

        # 1. Instantiate baseline core
        core_base = EmotionCore(config)
        harness_base = VirtualClockHarness(core_base, initial_time=0.0)

        # 2. Instantiate perturbed core
        core_pert = EmotionCore(config)
        harness_pert = VirtualClockHarness(core_pert, initial_time=0.0)

        # Generate a deterministic unit perturbation direction vector from seed
        rng = np.random.default_rng(seed)
        H = config.hidden_dim
        Hs = config.hidden_slow_dim
        v_fast = rng.standard_normal(H)
        v_slow = rng.standard_normal(Hs)
        v_total = np.concatenate([v_fast, v_slow])
        v_unit = v_total / (np.linalg.norm(v_total) + 1e-12)

        unit_fast = v_unit[:H]
        unit_slow = v_unit[H:]

        # Apply perturbation at t=0
        if epsilon > 0.0:
            with core_pert._state_lock:
                core_pert._h += epsilon * unit_fast
                core_pert._s_slow += epsilon * unit_slow

        trajectory_points: List[TrajectoryPoint] = []
        max_d_limbic = 0.0
        max_d_pad = 0.0
        rel_div_sum = 0.0

        for step_idx in range(1, self.timesteps + 1):
            # Check for stimulus injection at this step (CRN applied identically)
            if step_idx in stimuli:
                stim_vec = stimuli[step_idx]
                core_base.push_stimulus(stim_vec)
                core_pert.push_stimulus(stim_vec)

            # Advance ODE synchronously by dt
            pad_base = harness_base.step(dt=self.dt)
            pad_pert = harness_pert.step(dt=self.dt)

            # Extract internal state snapshots under _state_lock
            h_base = core_base.get_fast_state()
            s_base = core_base.get_slow_state()
            h_pert = core_pert.get_fast_state()
            s_pert = core_pert.get_slow_state()

            # Divergences
            diff_h = h_pert - h_base
            diff_s = s_pert - s_base
            d_fast = float(np.linalg.norm(diff_h))
            d_slow = float(np.linalg.norm(diff_s))
            d_limbic = float(math.sqrt(d_fast**2 + d_slow**2))

            pad_diff = np.array([
                pad_pert.pleasure - pad_base.pleasure,
                pad_pert.arousal - pad_base.arousal,
                pad_pert.dominance - pad_base.dominance,
            ])
            d_pad = float(np.linalg.norm(pad_diff))

            # Relative divergence
            norm_base = float(math.sqrt(np.linalg.norm(h_base)**2 + np.linalg.norm(s_base)**2))
            rel_div = d_limbic / (norm_base + 1e-12)
            rel_div_sum += rel_div

            # Local Lyapunov proxy
            lyap = None
            if epsilon > 0.0 and step_idx > 0:
                t_sec = step_idx * self.dt
                ratio = max(1e-18, d_limbic) / epsilon
                lyap = float(math.log(ratio) / t_sec)

            max_d_limbic = max(max_d_limbic, d_limbic)
            max_d_pad = max(max_d_pad, d_pad)

            trajectory_points.append(
                TrajectoryPoint(
                    step=step_idx,
                    virtual_time_sec=step_idx * self.dt,
                    d_fast=d_fast,
                    d_slow=d_slow,
                    d_limbic=d_limbic,
                    d_pad=d_pad,
                    relative_divergence=rel_div,
                    lyapunov_proxy=lyap,
                )
            )

        final_pt = trajectory_points[-1]
        amp_factor = (max_d_limbic / epsilon) if epsilon > 0.0 else 0.0

        return RunSummary(
            epsilon=epsilon,
            seed=seed,
            timesteps=self.timesteps,
            dt=self.dt,
            max_d_limbic=max_d_limbic,
            final_d_limbic=final_pt.d_limbic,
            max_d_pad=max_d_pad,
            final_d_pad=final_pt.d_pad,
            mean_relative_divergence=rel_div_sum / self.timesteps,
            amplification_factor=amp_factor,
            trajectory=trajectory_points,
        )

    def run_benchmark(self) -> Dict[str, Any]:
        """
        Executes the full grid across all epsilons and seeds.
        """
        logger.info(
            "Starting Dynamic Chaos Baseline across %d epsilons and %d seeds (T=%d steps, dt=%.3fs)...",
            len(self.epsilons),
            len(self.seeds),
            self.timesteps,
            self.dt,
        )
        t0 = time.time()
        stimuli = self._generate_stimulus_sequence(self.timesteps)

        runs: List[RunSummary] = []
        for eps in self.epsilons:
            for seed in self.seeds:
                summary = self._run_single_pair(eps, seed, stimuli)
                runs.append(summary)

        total_duration = time.time() - t0
        logger.info("Completed %d rollouts in %.2f seconds.", len(runs), total_duration)

        # Aggregate distributions: D_chaos(t, epsilon)
        d_chaos = self._aggregate_d_chaos(runs)

        null_entry = d_chaos.get("epsilon_0.0", {})
        null_mean = null_entry.get("max_d_limbic", {}).get("mean", None)
        drift_status = "NOT_EVALUATED"
        if null_mean is not None:
            drift_status = "EXACT_ZERO" if null_mean == 0.0 else "SUB_EPSILON"

        results = {
            "metadata": {
                "benchmark": "P26 Blocker 3 — Dynamic Epsilon-Perturbation Chaos Baseline",
                "timestamp": time.time(),
                "total_rollout_pairs": len(runs),
                "total_duration_sec": total_duration,
                "epsilons": self.epsilons,
                "seeds": self.seeds,
                "timesteps": self.timesteps,
                "dt_sec": self.dt,
                "virtual_time_total_sec": self.timesteps * self.dt,
                "stimulus_turn_steps": list(stimuli.keys()),
            },
            "numerical_tolerance": {
                "null_epsilon": 0.0,
                "max_observed_drift_at_null": null_mean,
                "drift_floor_status": drift_status,
            },
            "D_chaos_distributions": d_chaos,
            "raw_runs": [asdict(r) for r in runs],
        }

        if self.output_path is not None:
            with open(self.output_path, "w", encoding="utf-8") as f:
                json.dump(results, f, indent=2)
            logger.info("Saved raw chaos baseline telemetry to %s", self.output_path)
        return results

    def _aggregate_d_chaos(self, runs: List[RunSummary]) -> Dict[str, Any]:
        """
        Computes mean, std, percentiles (5th, 50th, 95th), and envelopes for each epsilon.
        """
        grouped: Dict[float, List[RunSummary]] = {}
        for r in runs:
            grouped.setdefault(r.epsilon, []).append(r)

        result: Dict[str, Any] = {}
        for eps, eps_runs in grouped.items():
            key = f"epsilon_{eps}"
            max_limbic_vals = [r.max_d_limbic for r in eps_runs]
            final_limbic_vals = [r.final_d_limbic for r in eps_runs]
            max_pad_vals = [r.max_d_pad for r in eps_runs]
            final_pad_vals = [r.final_d_pad for r in eps_runs]
            amp_factors = [r.amplification_factor for r in eps_runs]

            # Timestep-by-timestep aggregation for D_chaos(t, eps)
            t_steps: List[Dict[str, Any]] = []
            for t_idx in range(self.timesteps):
                t_sec = (t_idx + 1) * self.dt
                limbic_at_t = [r.trajectory[t_idx].d_limbic for r in eps_runs]
                pad_at_t = [r.trajectory[t_idx].d_pad for r in eps_runs]
                rel_at_t = [r.trajectory[t_idx].relative_divergence for r in eps_runs]

                t_steps.append({
                    "step": t_idx + 1,
                    "virtual_time_sec": t_sec,
                    "d_limbic_mean": float(np.mean(limbic_at_t)),
                    "d_limbic_std": float(np.std(limbic_at_t)),
                    "d_limbic_p05": float(np.percentile(limbic_at_t, 5)),
                    "d_limbic_median": float(np.median(limbic_at_t)),
                    "d_limbic_p95": float(np.percentile(limbic_at_t, 95)),
                    "d_pad_mean": float(np.mean(pad_at_t)),
                    "d_pad_p95": float(np.percentile(pad_at_t, 95)),
                    "relative_div_mean": float(np.mean(rel_at_t)),
                })

            result[key] = {
                "epsilon": eps,
                "n_runs": len(eps_runs),
                "max_d_limbic": {
                    "mean": float(np.mean(max_limbic_vals)),
                    "std": float(np.std(max_limbic_vals)),
                    "p05": float(np.percentile(max_limbic_vals, 5)),
                    "median": float(np.median(max_limbic_vals)),
                    "p95": float(np.percentile(max_limbic_vals, 95)),
                },
                "final_d_limbic": {
                    "mean": float(np.mean(final_limbic_vals)),
                    "p95": float(np.percentile(final_limbic_vals, 95)),
                },
                "max_d_pad": {
                    "mean": float(np.mean(max_pad_vals)),
                    "p95": float(np.percentile(max_pad_vals, 95)),
                },
                "final_d_pad": {
                    "mean": float(np.mean(final_pad_vals)),
                    "p95": float(np.percentile(final_pad_vals, 95)),
                },
                "amplification_factor": {
                    "mean": float(np.mean(amp_factors)),
                    "max": float(np.max(amp_factors)),
                },
                "timestep_profile": t_steps,
            }

        return result


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    runner = DynamicChaosRunner()
    res = runner.run_benchmark()
    print("Chaos Baseline Benchmark completed successfully.")
    print(f"Null drift floor: {res['numerical_tolerance']['max_observed_drift_at_null']}")
    for eps in runner.epsilons:
        key = f"epsilon_{eps}"
        mean_max = res['D_chaos_distributions'][key]['max_d_limbic']['mean']
        p95_pad = res['D_chaos_distributions'][key]['max_d_pad']['p95']
        print(f"eps={eps:1.0e} -> mean max d_limbic={mean_max:.3e}, p95 max d_pad={p95_pad:.3e}")
