"""
Dedicated unit tests for Coupled Multi-Timescale Liquid Neural Network (MT-LNN) EmotionCore.

Validates Phase 19 Production Realization:
- State dimensions (fast R^32, slow R^16)
- Philia dynamic resting attractor grounding
- Two-timescale observed trajectory retention (biphasic decay)
- Pre-reflective homeostatic fatigue coupling
- Numerical safety and NaN/Inf resilience
- Thread-safe state lock latency and trainer compatibility
"""

from __future__ import annotations

import time
import threading
import numpy as np
import pytest

from src.core.config import EmotionConfig
from src.core.emotion.emotion_core import EmotionCore
from src.core.models import PADState


def test_fast_slow_state_dimensions():
    """Verify H_f=32, H_s=16 and initial resting PAD state."""
    cfg = EmotionConfig(hidden_dim=32, hidden_slow_dim=16)
    core = EmotionCore(cfg)

    h_f = core.get_fast_state()
    s_s = core.get_slow_state()
    pad = core.get_pad_state()

    assert h_f.shape == (32,)
    assert s_s.shape == (16,)
    assert np.all(h_f == 0.0)
    assert np.allclose(s_s[:3], np.array([0.20, -0.05, 0.05]))
    assert pad.pleasure == pytest.approx(0.25, abs=1e-4)
    assert pad.arousal == pytest.approx(-0.05, abs=1e-4)
    assert pad.dominance == pytest.approx(0.05, abs=1e-4)


def test_philia_attractor_exact_convergence():
    """Verify unforced resting state matches Philia attractor within 10^-4."""
    core = EmotionCore(EmotionConfig())
    dist = core.get_attractor_distance()
    assert dist < 1e-4

    # Step once unforced
    pad = core.step_once()
    assert abs(pad.pleasure - 0.25) < 1e-4
    assert abs(pad.arousal - (-0.05)) < 1e-4
    assert abs(pad.dominance - 0.05) < 1e-4
    assert core.get_attractor_distance() < 1e-4


def test_two_timescale_trajectory_retention():
    """
    Verify observed biphasic trajectory retention following stimulus perturbation.
    Replaces static parameter ratio checks with empirical dynamic trajectory testing (EXP-19.1/19.2).
    """
    core = EmotionCore(EmotionConfig(loop_cadence_ms=100))

    # 1. Perturb with 5-turn positive stimulus sequence (matching EXP-19.1 protocol)
    stimulus = np.zeros(16, dtype=np.float64)
    stimulus[0] = 1.50  # Strong positive valence
    stimulus[1] = 1.20  # High arousal
    for _ in range(5):
        core.push_stimulus(stimulus)
        pad_initial = core.commit_stimulus()

    # Immediate response should elevate valence and arousal
    assert pad_initial.pleasure > 0.35
    assert pad_initial.arousal > 0.05

    initial_fast_norm = np.linalg.norm(core.get_fast_state())
    assert initial_fast_norm > 0.30

    # 2. Relax unforced over 15 seconds (150 steps of dt=0.1s)
    for _ in range(150):
        core.step_once()

    fast_state_15s = core.get_fast_state()
    slow_state_15s = core.get_slow_state()
    pad_15s = core.get_pad_state()

    # Fast layer reflex should have rapidly cleared (> 70% decay)
    fast_norm_15s = np.linalg.norm(fast_state_15s)
    assert fast_norm_15s < 0.30 * initial_fast_norm

    # Slow layer should exhibit strong persistent momentum (> 0.05 deviation from resting Philia)
    slow_deviation_15s = np.linalg.norm(slow_state_15s - core.s_philia)
    assert slow_deviation_15s > 0.05

    # PAD state maintains non-zero affective momentum above baseline
    assert pad_15s.pleasure > 0.255 or pad_15s.arousal > -0.05

    # 3. Extended unforced relaxation to 60 seconds (total 600 steps)
    for _ in range(450):
        core.step_once()

    pad_60s = core.get_pad_state()
    final_attractor_dist = core.get_attractor_distance()

    # Must converge into Philia attractor neighborhood (<= 0.0386 per EXP-19.2)
    assert final_attractor_dist <= 0.0386

    # Must NOT collapse to neutral apathy / origin [0, 0, 0]
    origin_dist = np.linalg.norm(np.array([pad_60s.pleasure, pad_60s.arousal, pad_60s.dominance]))
    assert origin_dist >= 0.20, "State must ground at Philia resting baseline rather than collapsing to [0,0,0]"


def test_homeostatic_fatigue_coupling():
    """Verify that depleted energy and elevated cognitive load drive arousal down into somatic fatigue."""
    core = EmotionCore(EmotionConfig())

    # Feed post-stress fatigue: depleted energy (0.20), residual load (0.60), zero acute threat tension
    core.update_homeostatic_context(energy=0.20, load=0.60, tension=0.0, stability=0.50)

    # Step unforced for 200 ticks (20s)
    for _ in range(200):
        core.step_once()

    pad = core.get_pad_state()
    # Arousal must drop below resting baseline (-0.05) into somatic fatigue
    assert pad.arousal < -0.08
    assert pad.pleasure < 0.25


def test_numerical_safety_nan_resilience():
    """Verify that injecting NaN/Inf stimulus does not cause NaN explosion or crashes."""
    core = EmotionCore(EmotionConfig())

    nan_stimulus = np.full(16, np.nan, dtype=np.float64)
    core.push_stimulus(nan_stimulus)
    pad = core.commit_stimulus()

    assert np.isfinite(pad.pleasure)
    assert np.isfinite(pad.arousal)
    assert np.isfinite(pad.dominance)
    assert -1.0 <= pad.pleasure <= 1.0
    assert -1.0 <= pad.arousal <= 1.0
    assert -1.0 <= pad.dominance <= 1.0


def test_reset_to_resting_clears_momentum():
    """Verify reset_to_resting() clears fast/slow momentum and immediately restores Philia baseline."""
    core = EmotionCore(EmotionConfig())

    # Perturb with stimulus and fatigue
    core.push_stimulus(np.ones(16) * 1.2)
    core.update_homeostatic_context(energy=0.1, load=0.9, tension=0.9, stability=0.1)
    for _ in range(50):
        core.step_once()

    # Confirm dirty state
    assert core.get_attractor_distance() > 0.05

    # Reset
    core.reset_to_resting()

    assert np.all(core.get_fast_state() == 0.0)
    assert np.allclose(core.get_slow_state(), core.s_philia)
    assert core.get_attractor_distance() < 1e-4

    # Subsequent unforced step remains at Philia
    pad_next = core.step_once()
    assert abs(pad_next.pleasure - 0.25) < 1e-4
    assert abs(pad_next.arousal - (-0.05)) < 1e-4
    assert abs(pad_next.dominance - 0.05) < 1e-4


def test_lnn_trainer_weight_swap_compatibility():
    """Verify weight property aliases and in-place compatibility for LNNTrainer."""
    core = EmotionCore(EmotionConfig())

    assert core.W_f is core.W_ff
    assert core.W_tau is core.W_tau_f
    assert core.U_tau is core.U_tau_f
    assert core.b_tau is core.b_tau_f
    assert core.W_proj is core.W_proj_f

    # Modify W_f in place
    original_shape = core.W_f.shape
    new_weights = np.ones(original_shape, dtype=np.float64) * 0.123
    core.W_f = new_weights

    assert np.all(core.W_ff == 0.123)


def test_concurrent_state_lock_timeout():
    """Verify get_pad_state() returns within deadline under concurrent execution."""
    core = EmotionCore(EmotionConfig(loop_cadence_ms=100))
    core.start()
    try:
        latencies = []
        for _ in range(50):
            t0 = time.monotonic()
            pad = core.get_pad_state()
            latencies.append((time.monotonic() - t0) * 1000.0)
            time.sleep(0.01)

        mean_latency = np.mean(latencies)
        max_latency = np.max(latencies)
        assert mean_latency < 1.0, f"Mean read latency exceeded 1ms: {mean_latency:.3f}ms"
        assert max_latency < 5.0, f"Max read latency exceeded 5ms: {max_latency:.3f}ms"
    finally:
        core.stop()
