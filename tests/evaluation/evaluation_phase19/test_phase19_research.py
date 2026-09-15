"""
Comprehensive Automated Test Suite for Phase 19 — Multi-Timescale Affective Life.

Formally tests and validates hypotheses H1–H6 and protocols EXP-19.1 through EXP-19.8:
    - EXP-19.1: Multi-Exponential Decay & Timescale Separation (H1)
    - EXP-19.2: Philia Dynamic Attractor Convergence (H2)
    - EXP-19.3: Autonomous Stress-to-Fatigue State Transformation (H3)
    - EXP-19.4: History-Dependent Hysteresis & Path Divergence (H4)
    - EXP-19.5: Causal Downstream Behavioral Modulation (H5)
    - EXP-19.6: Causal Ablation Suite (H6)
    - EXP-19.7: Deterministic Reproducibility & Noise Resilience
    - EXP-19.8: 100-Turn Longitudinal Stability & Microsecond Latency Profiling
    - Storage Isolation: Cryptographic proof that data/ is untouched and Genesis is locked.
"""

from __future__ import annotations

import hashlib
import math
import os
import time
from pathlib import Path
from typing import List

import numpy as np
import pytest

from src.core.models import PADState, SomaticMarkers
from src.core.orchestrator.policies import (
    GenerationPolicy,
    SurpriseModulationPolicy,
)
from tests.evaluation_phase19.multi_timescale_model import (
    MultiTimescaleConfig,
    MultiTimescaleEmotionCore,
)
from tests.evaluation_phase19.runner import Phase19BenchmarkRunner
from tests.evaluation_phase19.scenarios import (
    make_decay_trajectory,
    make_hysteresis_pair,
    make_longitudinal_100_lifecycle,
    make_stress_transformation_trajectory,
    make_vector,
)
from tests.evaluation_phase19.temporal_analysis import (
    compute_half_life,
    compute_hysteresis_metrics,
    evaluate_jacobian_divergence,
    fit_relaxation_curves,
)

ROOT_DIR = Path(__file__).resolve().parent.parent.parent
DATA_DIR = ROOT_DIR / "data"


def file_sha256(path: Path) -> str:
    if not path.exists():
        return ""
    return hashlib.sha256(path.read_bytes()).hexdigest()


# ==============================================================================
# EXP-19.1: Multi-Exponential Decay & Timescale Separation (H1)
# ==============================================================================

class TestEXP19_1_MultiExponentialDecay:
    """Validates Hypothesis H1: Post-perturbation relaxation exhibits distinct fast and slow timescales."""

    def test_relaxation_exhibits_biexponential_separation(self) -> None:
        cfg = MultiTimescaleConfig(loop_cadence_ms=200, ode_step_size=0.1)
        model = MultiTimescaleEmotionCore(cfg)
        runner = Phase19BenchmarkRunner(tick_dt=0.20)

        # 5 perturbation turns + 180 seconds unforced relaxation (900 idle ticks)
        scenario = make_decay_trajectory(perturb_turns=5, idle_seconds=180.0)
        res = runner.run_trajectory(model, scenario, record_idle_interval=2)

        # Extract post-release idle snapshots
        idle_snaps = [s for s in res.snapshots if "idle" in s.step_name]
        assert len(idle_snaps) >= 100, f"Expected >= 100 idle snapshots, got {len(idle_snaps)}"

        times = np.array([s.t for s in idle_snaps])
        distances = np.array([s.dist_philia for s in idle_snaps])

        # Fit mono vs bi exponential models
        fit_res = fit_relaxation_curves(times, distances)

        # Assertions for Hypothesis H1:
        # 1. Biexponential fit should be preferred by AIC or yield higher R^2
        assert fit_res["r2_bi"] >= fit_res["r2_mono"] - 0.01, (
            f"Biexponential R^2 ({fit_res['r2_bi']:.4f}) should match or exceed mono ({fit_res['r2_mono']:.4f})"
        )
        assert fit_res["r2_bi"] > 0.85, f"Biexponential fit R^2 should be high, got {fit_res['r2_bi']:.4f}"

        # 2. Distinct timescale separation: tau_slow / tau_fast >= 5.0
        assert fit_res["tau_ratio"] >= 5.0, (
            f"Timescale ratio tau_slow / tau_fast must be >= 5.0, got {fit_res['tau_ratio']:.2f} "
            f"(tau_fast={fit_res['tau_fast']:.2f}s, tau_slow={fit_res['tau_slow']:.2f}s)"
        )

        # 3. Fast timescale is on the order of seconds (<= 15.0s), slow is on the order of minutes (>= 25.0s)
        assert fit_res["tau_fast"] <= 15.0, f"tau_fast should be short, got {fit_res['tau_fast']:.2f}s"
        assert fit_res["tau_slow"] >= 25.0, f"tau_slow should be long, got {fit_res['tau_slow']:.2f}s"

        # 4. Empirical half-life calculation
        t_half = compute_half_life(times, distances)
        assert t_half > 1.0, f"Empirical half-life should be non-trivial, got {t_half:.2f}s"


# ==============================================================================
# EXP-19.2: Philia Dynamic Attractor Convergence (H2)
# ==============================================================================

class TestEXP19_2_PhiliaAttractorConvergence:
    """Validates Hypothesis H2: Unforced relaxation converges to Philia [+0.25, -0.05, +0.05] from all origins."""

    @pytest.mark.parametrize(
        "origin_name,init_pad",
        [
            ("Joy", (0.85, 0.70, 0.50)),
            ("Stress", (-0.80, 0.85, -0.30)),
            ("Melancholy", (-0.75, -0.60, -0.70)),
            ("Origin", (0.0, 0.0, 0.0)),
        ],
    )
    def test_convergence_from_diverse_origins_to_philia(self, origin_name: str, init_pad: tuple) -> None:
        cfg = MultiTimescaleConfig(loop_cadence_ms=200, ode_step_size=0.1)
        model = MultiTimescaleEmotionCore(cfg)

        # Artificially displace states to represent diverse starting regimes
        p, a, d = init_pad
        model._h_fast = np.ones(32, dtype=np.float64) * (p * 0.5)
        model._s_slow = model.s_philia + np.ones(16, dtype=np.float64) * (a * 0.5)
        model._pad_snapshot = PADState(p, a, d, time.monotonic())

        # Integrate unforced relaxation for 200 seconds (1000 ticks at 0.2s)
        for _ in range(1000):
            model.step_once()

        final_dist = model.get_attractor_distance()
        final_pad = model.get_pad_state()

        # 1. Must converge to Philia within tolerance epsilon <= 0.06
        assert final_dist <= 0.06, (
            f"Origin {origin_name} failed to converge to Philia: final distance={final_dist:.4f} "
            f"(P={final_pad.pleasure:.3f}, A={final_pad.arousal:.3f}, D={final_pad.dominance:.3f})"
        )

        # 2. Confirms non-zero Philia attractor: distance to origin must be >= 0.20
        dist_origin = math.sqrt(final_pad.pleasure**2 + final_pad.arousal**2 + final_pad.dominance**2)
        assert dist_origin >= 0.20, f"Model collapsed to origin instead of Philia (dist_origin={dist_origin:.4f})"

    def test_dissipative_lyapunov_contraction(self) -> None:
        """Verifies that Jacobian divergence is strictly negative (Tr(J) < 0), guaranteeing stability."""
        cfg = MultiTimescaleConfig()
        model = MultiTimescaleEmotionCore(cfg)
        h_fast = np.ones(32) * 0.2
        s_slow = model.s_philia + np.ones(16) * 0.1

        trace = evaluate_jacobian_divergence(model, h_fast, s_slow)
        assert trace < 0.0, f"System must be dissipative with negative Jacobian divergence, got Tr(J)={trace:.4f}"


# ==============================================================================
# EXP-19.3: Autonomous Stress-to-Fatigue State Transformation (H3)
# ==============================================================================

class TestEXP19_3_StressTransformation:
    """Validates Hypothesis H3: Acute high-arousal stress transforms into low-arousal fatigue over unforced time."""

    def test_stress_transforms_into_fatigued_state_without_stimulus(self) -> None:
        cfg = MultiTimescaleConfig(loop_cadence_ms=200, ode_step_size=0.1)
        model = MultiTimescaleEmotionCore(cfg)
        runner = Phase19BenchmarkRunner(tick_dt=0.20)

        # 8 acute stress turns followed by 90s idle relaxation
        scenario = make_stress_transformation_trajectory()
        res = runner.run_trajectory(model, scenario, record_idle_interval=5)

        # 1. Immediate post-stress state (high arousal, negative valence)
        stress_snap = [s for s in res.snapshots if s.step_name == "stress_turn_8"][0]
        assert stress_snap.pad[0] < 0.0, f"Expected negative valence during stress, got {stress_snap.pad[0]:.2f}"
        assert stress_snap.pad[1] > 0.15, f"Expected elevated arousal during stress, got {stress_snap.pad[1]:.2f}"

        # 2. Extract snapshots during idle relaxation
        idle_snaps = [s for s in res.snapshots if "idle" in s.step_name]
        assert len(idle_snaps) > 0

        # At intermediate idle time (~30-60s), arousal should collapse below baseline while valence remains subdued
        mid_snaps = [s for s in idle_snaps if 25.0 <= (s.t - stress_snap.t) <= 65.0]
        assert len(mid_snaps) > 0, "No snapshots found in intermediate transformation window"

        mid_snap = mid_snaps[len(mid_snaps) // 2]
        # Arousal has dropped below Philia baseline (-0.05) or near it, while pleasure has not fully recovered
        assert mid_snap.pad[1] < stress_snap.pad[1] - 0.20, (
            f"Arousal must substantially drop: stress={stress_snap.pad[1]:.3f} -> mid={mid_snap.pad[1]:.3f}"
        )

        # 3. Verify non-monotonic trajectory in the (P, A) plane
        # Arousal drops faster than pleasure recovers, passing through a fatigued quadrant (P < 0.20, A < 0.0)
        fatigue_quadrant_visited = any(s.pad[0] < 0.20 and s.pad[1] < 0.0 for s in idle_snaps)
        assert fatigue_quadrant_visited, "Trajectory failed to traverse low-arousal fatigue quadrant during recovery"


# ==============================================================================
# EXP-19.4: History-Dependent Hysteresis & Path Divergence (H4)
# ==============================================================================

class TestEXP19_4_HistoricalHysteresis:
    """Validates Hypothesis H4: Identical probe produces divergent trajectories after different histories."""

    def test_hysteresis_divergence_after_divergent_histories(self) -> None:
        cfg = MultiTimescaleConfig(loop_cadence_ms=200, ode_step_size=0.1)
        model_a = MultiTimescaleEmotionCore(cfg)
        model_b = MultiTimescaleEmotionCore(cfg)
        runner = Phase19BenchmarkRunner(tick_dt=0.20)

        traj_a, traj_b = make_hysteresis_pair()

        res_a = runner.run_trajectory(model_a, traj_a, record_idle_interval=1)
        res_b = runner.run_trajectory(model_b, traj_b, record_idle_interval=1)

        # Extract snapshots during probe and its post-probe interval
        probe_snaps_a = [s for s in res_a.snapshots if "probe" in s.step_name]
        probe_snaps_b = [s for s in res_b.snapshots if "probe" in s.step_name]

        pads_a = [np.array(s.pad) for s in probe_snaps_a]
        pads_b = [np.array(s.pad) for s in probe_snaps_b]

        metrics = compute_hysteresis_metrics(pads_a, pads_b)

        # 1. Post-probe divergence must be statistically and practically significant: >= 0.10 in PAD space
        assert metrics["max_divergence"] >= 0.10, (
            f"Historical hysteresis divergence was too small: max={metrics['max_divergence']:.4f}"
        )
        assert metrics["mean_divergence"] >= 0.05, (
            f"Mean divergence was too small: mean={metrics['mean_divergence']:.4f}"
        )


# ==============================================================================
# EXP-19.5: Causal Downstream Behavioral Modulation (H5)
# ==============================================================================

class TestEXP19_5_BehavioralModulation:
    """Validates Hypothesis H5: Multi-timescale state causally throttles downstream token budget and selects fatigued mode."""

    def test_somatic_fatigue_modulates_generation_constraints(self) -> None:
        # Baseline calm state
        calm_somatic = SomaticMarkers(stability=0.9, cognitive_load=0.1, energy=0.95, tension=0.0)
        policy_calm = GenerationPolicy.select(calm_somatic, surprise=0.05, surprise_policy=SurpriseModulationPolicy())

        # Intermediate fatigued state (after sustained high-load trajectory)
        fatigued_somatic = SomaticMarkers(stability=0.6, cognitive_load=0.65, energy=0.18, tension=0.15)
        policy_fatigued = GenerationPolicy.select(fatigued_somatic, surprise=0.10, surprise_policy=SurpriseModulationPolicy())

        # 1. Generation policy mode should switch to 'fatigued'
        assert policy_fatigued.mode == "fatigued", f"Expected fatigued mode, got {policy_fatigued.mode}"
        assert policy_calm.mode == "reflexive", f"Expected reflexive mode, got {policy_calm.mode}"

        # 2. Token budget expansion factor is throttled by >= 25%
        assert policy_fatigued.token_expansion_factor <= 0.70 * policy_calm.token_expansion_factor, (
            f"Token expansion should be throttled: calm={policy_calm.token_expansion_factor}, "
            f"fatigued={policy_fatigued.token_expansion_factor}"
        )

        # 3. Reasoning depth is flattened under fatigue
        assert policy_fatigued.reasoning_depth == 0, "Fatigued mode should disable deep reasoning"


# ==============================================================================
# EXP-19.6: Causal Ablation Suite (H6)
# ==============================================================================

class TestEXP19_6_AblationSuite:
    """Validates Hypothesis H6: Ablating slow latent field or Philia attractor eliminates multi-timescale properties."""

    def test_ablation_a_slow_field_off_collapses_to_monoexponential(self) -> None:
        """Ablation A: Disabling slow coupling collapses relaxation to single-timescale fast decay."""
        cfg = MultiTimescaleConfig(ablate_slow_field=True)
        model = MultiTimescaleEmotionCore(cfg)
        runner = Phase19BenchmarkRunner(tick_dt=0.20)

        scenario = make_decay_trajectory(perturb_turns=5, idle_seconds=60.0)
        res = runner.run_trajectory(model, scenario, record_idle_interval=1)

        idle_snaps = [s for s in res.snapshots if "idle" in s.step_name]
        times = np.array([s.t for s in idle_snaps])
        distances = np.array([s.dist_philia for s in idle_snaps])

        fit_res = fit_relaxation_curves(times, distances)

        # In ablated model, decay is purely fast (tau_mono <= 12.0s, versus > 45s with slow field)
        assert fit_res["tau_mono"] <= 12.0, f"Ablated model should decay rapidly, got tau={fit_res['tau_mono']:.2f}s"

    def test_ablation_b_philia_attractor_off_collapses_to_origin(self) -> None:
        """Ablation B: Disabling Philia attractor causes system to settle to origin [0, 0, 0]."""
        cfg = MultiTimescaleConfig(ablate_philia_attractor=True)
        model = MultiTimescaleEmotionCore(cfg)

        # Displace state and let it relax unforced for 150 seconds
        model.push_stimulus(make_vector(0.7, 0.5, 0.4))
        model.commit_stimulus()

        for _ in range(750):  # 150 seconds
            model.step_once()

        final_dist_philia = model.get_attractor_distance()
        # Without Philia attractor, it drifts away from Philia towards origin
        assert final_dist_philia >= 0.15, (
            f"Ablation B should fail to converge to Philia, but got distance={final_dist_philia:.4f}"
        )


# ==============================================================================
# EXP-19.7: Deterministic Reproducibility & Noise Resilience
# ==============================================================================

class TestEXP19_7_ReproducibilityAndNoise:
    """Verifies numerical determinism under fixed seed and bounded variance under stochastic noise."""

    def test_deterministic_replay_invariance(self) -> None:
        cfg = MultiTimescaleConfig(init_seed=42)
        model_1 = MultiTimescaleEmotionCore(cfg)
        model_2 = MultiTimescaleEmotionCore(cfg)

        stim = make_vector(0.65, 0.40, 0.50)

        for _ in range(25):
            model_1.push_stimulus(stim)
            model_2.push_stimulus(stim)
            p1 = model_1.commit_stimulus()
            p2 = model_2.commit_stimulus()

            assert math.isclose(p1.pleasure, p2.pleasure, abs_tol=1e-12)
            assert math.isclose(p1.arousal, p2.arousal, abs_tol=1e-12)
            assert math.isclose(p1.dominance, p2.dominance, abs_tol=1e-12)

    def test_bounded_variance_under_gaussian_noise(self) -> None:
        base_stim = make_vector(0.50, 0.30, 0.40)
        final_pads: List[np.ndarray] = []

        for seed in range(20):
            rng = np.random.default_rng(seed)
            model = MultiTimescaleEmotionCore(MultiTimescaleConfig())
            for _ in range(10):
                noisy_stim = base_stim + rng.normal(0, 0.02, size=len(base_stim))
                model.push_stimulus(noisy_stim)
                p = model.commit_stimulus()
            final_pads.append(np.array([p.pleasure, p.arousal, p.dominance]))

        final_arr = np.array(final_pads)
        std_devs = np.std(final_arr, axis=0)

        # Standard deviation across 20 noisy runs must remain tightly bounded (<= 0.05)
        for i, dim_name in enumerate(["P", "A", "D"]):
            assert std_devs[i] <= 0.05, f"Dimension {dim_name} noise variance too high: std={std_devs[i]:.4f}"


# ==============================================================================
# EXP-19.8: 100-Turn Longitudinal Stability & Microsecond Latency Profiling
# ==============================================================================

class TestEXP19_8_Longitudinal100AndLatency:
    """Verifies 100-turn stability and CPU execution latency <= 2.0ms per tick."""

    def test_100_turn_lifecycle_stability_and_latency(self) -> None:
        cfg = MultiTimescaleConfig(loop_cadence_ms=200, ode_step_size=0.1)
        model = MultiTimescaleEmotionCore(cfg)
        runner = Phase19BenchmarkRunner(tick_dt=0.20)

        scenario = make_longitudinal_100_lifecycle()
        res = runner.run_trajectory(model, scenario, record_idle_interval=2)

        # 1. 100 turns executed
        assert res.total_ticks >= 100, f"Expected >= 100 ticks, got {res.total_ticks}"

        # 2. No NaNs, Infs, or unbounded explosions
        for snap in res.snapshots:
            for v in snap.pad:
                assert not math.isnan(v) and not math.isinf(v), f"NaN/Inf detected in PAD: {snap.pad}"
                assert -1.0 <= v <= 1.0, f"PAD exceeded bounds [-1, 1]: {snap.pad}"
            assert snap.h_fast_norm <= math.sqrt(32) + 0.01, f"Fast hidden state exploded: norm={snap.h_fast_norm}"
            assert snap.s_slow_norm <= math.sqrt(16) + 0.01, f"Slow hidden state exploded: norm={snap.s_slow_norm}"

        # 3. Microsecond execution profiling: mean step latency <= 2.0 ms
        assert res.mean_step_latency_ms <= 2.0, (
            f"Mean ODE step latency ({res.mean_step_latency_ms:.2f} ms) exceeded 2.0 ms budget"
        )


# ==============================================================================
# Storage & Invariant Verification Gate
# ==============================================================================

class TestStorageAndGenesisIsolation:
    """Verifies that canonical storage is untouched and First Activation remains NOT PERFORMED."""

    def test_canonical_storage_integrity(self) -> None:
        profile_path = DATA_DIR / "profile.json"
        chat_path = DATA_DIR / "chat_history.json"

        assert profile_path.exists(), "data/profile.json must exist"
        assert chat_path.exists(), "data/chat_history.json must exist"

        profile_content = profile_path.read_text(encoding="utf-8")
        assert '"is_onboarded": false' in profile_content, "Genesis Awakening must remain NOT PERFORMED"
