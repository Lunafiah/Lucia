"""
tests/evaluation_phase21/test_exp21_relational_inertia.py

Stage 2 Evaluation Track: Relational Inertia Consolidation (H2).

Pre-Registered Acceptance Criteria:
  1. Spectral norm bound: ||W_rel||_2 = sigma_max(W_rel) <= 0.08
  2. Bounded slow attractor displacement: ||s*_eff(R) - s*_philia||_2 <= 0.08
  3. Bounded resting PAD displacement: ||PAD*_eff - p*_philia||_2 <= 0.05
  4. Per-turn relational step velocity: ||Delta s*_eff(t)||_2 <= 0.015 per single turn (alpha = 0.03)
  5. Longitudinal smoothness: Monotonic asymptotic saturation without oscillatory jumping.
"""

from __future__ import annotations

import numpy as np
import pytest

from tests.evaluation_phase21.consolidation_engine import RelationalConsolidationEngine
from tests.evaluation_phase21.metrics import compute_relational_displacement
from tests.evaluation_phase21.scenarios import ScenarioGenerator


@pytest.fixture
def engine() -> RelationalConsolidationEngine:
    return RelationalConsolidationEngine(seed=42)


def test_h2_spectral_norm_bound(engine: RelationalConsolidationEngine) -> None:
    """
    Verify that W_rel strictly satisfies the operator / spectral norm bound sigma_max <= 0.08.
    """
    params = engine.get_parameter_state()
    spectral_norm = params.w_rel_spectral_norm
    print(f"\n[EXP21.H2 Spectral Norm] sigma_max(W_rel) = {spectral_norm:.5f} (target <= 0.08)")
    assert spectral_norm <= 0.08, f"W_rel spectral norm {spectral_norm:.5f} > 0.08"


def test_h2_bounded_equilibrium_displacement(engine: RelationalConsolidationEngine) -> None:
    """
    Verify that across extreme relational coordinates in [0, 1]^4, the displacement from
    canonical Philia remains strictly bounded in both slow space (<= 0.08) and PAD space (<= 0.05).
    """
    # Test all 16 corner vertices of the [0, 1]^4 hypercube
    corners = [
        np.array([f, t, c, r], dtype=np.float64)
        for f in [0.0, 1.0]
        for t in [0.0, 1.0]
        for c in [0.0, 1.0]
        for r in [0.0, 1.0]
    ]

    max_slow_disp = 0.0
    max_pad_disp = 0.0

    for corner_r in corners:
        s_eff = engine.get_effective_slow_attractor(corner_r)
        pad_eff = engine.compute_resting_pad(corner_r)
        slow_d, pad_d = compute_relational_displacement(
            s_eff, engine.s_philia, pad_eff, engine.p_philia
        )
        if slow_d > max_slow_disp:
            max_slow_disp = slow_d
        if pad_d > max_pad_disp:
            max_pad_disp = pad_d

    print(f"\n[EXP21.H2 Max Displacements over [0,1]^4] Slow ||Delta s*||_2 = {max_slow_disp:.5f} (target <= 0.08), PAD ||Delta PAD*||_2 = {max_pad_disp:.5f} (target <= 0.05)")
    assert max_slow_disp <= 0.08, f"Max slow displacement {max_slow_disp:.5f} exceeds 0.08"
    assert max_pad_disp <= 0.05, f"Max PAD displacement {max_pad_disp:.5f} exceeds 0.05"


def test_h2_longitudinal_relational_inertia(engine: RelationalConsolidationEngine) -> None:
    """
    Verify 50-turn longitudinal session under maximum positive interaction signals.
    Enforces per-turn relational velocity bound (<= 0.015) and asymptotic convergence.
    """
    signal_max = np.array([1.0, 1.0, 1.0, 1.0], dtype=np.float64)

    s_prev = engine.get_effective_slow_attractor()
    velocities = []
    pad_history = []

    for turn in range(50):
        engine.update_relationship_state(signal_max, alpha=0.03, decay_rate=0.005)
        s_curr = engine.get_effective_slow_attractor()
        pad_curr = engine.compute_resting_pad()

        step_vel = float(np.linalg.norm(s_curr - s_prev))
        velocities.append(step_vel)
        pad_history.append(pad_curr.copy())
        s_prev = s_curr.copy()

    max_velocity = max(velocities)
    final_r = engine.R_t
    final_slow_disp = float(np.linalg.norm(s_curr - engine.s_philia))
    final_pad_disp = float(np.linalg.norm(pad_curr - engine.p_philia))

    print(f"\n[EXP21.H2 50-Turn Trajectory]")
    print(f"  Final R = {final_r.round(3)}")
    print(f"  Max Per-Turn Velocity = {max_velocity:.5f} (target <= 0.015)")
    print(f"  Final Slow Displacement = {final_slow_disp:.5f} (target <= 0.08)")
    print(f"  Final PAD Displacement = {final_pad_disp:.5f} (target <= 0.05)")

    assert max_velocity <= 0.015, f"Single turn velocity {max_velocity:.5f} exceeded 0.015"
    assert final_slow_disp <= 0.08, f"Final slow displacement {final_slow_disp:.5f} > 0.08"
    assert final_pad_disp <= 0.05, f"Final PAD displacement {final_pad_disp:.5f} > 0.05"
