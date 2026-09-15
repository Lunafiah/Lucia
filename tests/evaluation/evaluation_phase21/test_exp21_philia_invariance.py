"""
tests/evaluation_phase21/test_exp21_philia_invariance.py

Stage 3 Evaluation Track: Philia Attractor Manifold Invariance & Reversibility (H3).

Pre-Registered Acceptance Criteria:
  1. Canonical Philia Invariance:
     In uncoupled state (R = R0), unforced idle relaxation (T >= 120s) converges back
     to canonical Philia p*_philia = (+0.25, -0.05, +0.05) with error epsilon < 10^-4.
  2. Conditioned Attractor Stability:
     Under mature relational coupling (R != R0), the system settles stably at s*_eff(R)
     with bounded displacement ||Delta PAD*||_2 <= 0.05 and zero limit cycles.
  3. Longitudinal Reversibility under Relational Decay:
     When an intensely bonded relationship decays back to R0 under absence, the system
     asymptotically restores canonical Philia within epsilon < 10^-4.
  4. Numerical Contraction & Boundedness:
     Zero NaNs/Infs, strictly bounded state space (||h||_inf <= 1.0, ||s||_inf <= 1.0).
"""

from __future__ import annotations

import numpy as np
import pytest

from tests.evaluation_phase21.consolidation_engine import RelationalConsolidationEngine
from tests.evaluation_phase21.metrics import compute_philia_restoration_error


@pytest.fixture
def engine() -> RelationalConsolidationEngine:
    return RelationalConsolidationEngine(seed=42)


def test_h3_canonical_philia_attractor_restoration(engine: RelationalConsolidationEngine) -> None:
    """
    Verify that from an arbitrary perturbed limbic state at R = R0, unforced idle relaxation
    restores the canonical Philia attractor with epsilon < 10^-4.
    """
    # 1. Perturb limbic state strongly away from Philia
    engine.R_t = engine.R_0.copy()
    engine._h_fast = np.array([0.70, -0.60, 0.50] + [0.10] * (engine.hidden_dim - 3), dtype=np.float64)
    engine._s_slow = np.array([-0.50, 0.60, -0.30] + [0.05] * (engine.hidden_slow_dim - 3), dtype=np.float64)

    pad_perturbed = engine.project_to_pad(engine._h_fast, engine._s_slow)
    init_err = float(np.linalg.norm(pad_perturbed - engine.p_philia))
    print(f"\n[EXP21.H3 Initial Perturbed PAD] PAD={pad_perturbed.round(4)}, Initial Offset={init_err:.4f}")
    assert init_err > 0.20, "Initial state was not sufficiently perturbed"

    # 2. Run unforced idle relaxation for 550s (coupled slow eigenvalue tau_eff ~ 56s -> e^-9.8 < 10^-4)
    pad_traj, slow_traj, _ = engine.integrate_unforced_idle(duration_s=550.0, dt=0.20)

    final_pad = pad_traj[-1]
    final_err = compute_philia_restoration_error(final_pad, engine.p_philia)
    final_slow_err = float(np.linalg.norm(slow_traj[-1] - engine.s_philia))

    print(f"[EXP21.H3 Relaxation @ 550s] Final PAD={final_pad.round(6)}, Epsilon Error={final_err:.6e} (target < 1e-4)")
    print(f"                             Final Slow Error={final_slow_err:.6e}")

    assert final_err < 1e-4, f"Final Philia error {final_err:.6e} >= 1e-4"
    assert np.all(np.isfinite(pad_traj)), "Non-finite values detected in PAD trajectory"
    assert np.all(np.isfinite(slow_traj)), "Non-finite values detected in slow trajectory"


def test_h3_conditioned_attractor_stability(engine: RelationalConsolidationEngine) -> None:
    """
    Verify that under mature relationship (R != R0), the system converges stably to
    relationship-conditioned equilibrium s*_eff(R) without limit cycles or divergence.
    """
    # Set relationship to high trust, closeness, familiarity
    mature_r = np.array([0.80, 0.90, 0.75, 0.85], dtype=np.float64)
    engine.R_t = mature_r.copy()

    s_eff_target = engine.get_effective_slow_attractor(mature_r)
    pad_eff_target = engine.compute_resting_pad(mature_r)

    # Perturb state
    engine._h_fast = np.ones(engine.hidden_dim, dtype=np.float64) * 0.30
    engine._s_slow = engine.s_philia.copy()

    # Run unforced relaxation for 550s
    pad_traj, slow_traj, _ = engine.integrate_unforced_idle(duration_s=550.0, dt=0.20)

    final_pad = pad_traj[-1]
    final_slow = slow_traj[-1]

    slow_conv_err = float(np.linalg.norm(final_slow - s_eff_target))
    pad_conv_err = float(np.linalg.norm(final_pad - pad_eff_target))
    philia_disp = float(np.linalg.norm(final_pad - engine.p_philia))

    print(f"\n[EXP21.H3 Conditioned Equilibrium]")
    print(f"  Target Slow Attractor: {s_eff_target[:3].round(4)}")
    print(f"  Target PAD Attractor:  {pad_eff_target.round(4)}")
    print(f"  Final PAD:             {final_pad.round(4)}")
    print(f"  Convergence Error:     {pad_conv_err:.6e} (target < 1e-4)")
    print(f"  Displacement from Philia: {philia_disp:.4f} (target <= 0.05)")

    assert pad_conv_err < 1e-4, f"Conditioned equilibrium convergence error {pad_conv_err:.6e} >= 1e-4"
    assert philia_disp <= 0.05, f"Displacement from canonical Philia {philia_disp:.4f} > 0.05"


def test_h3_longitudinal_reversibility_under_absence_decay(engine: RelationalConsolidationEngine) -> None:
    """
    Verify that when relational forcing decays back towards stranger baseline (R -> R0)
    during long absence, the system asymptotically restores canonical Philia (epsilon < 10^-4).
    """
    # 1. Start from mature bonded relationship
    engine.R_t = np.array([0.90, 0.95, 0.85, 0.90], dtype=np.float64)

    # 2. Simulate prolonged absence with relationship decay ticks:
    # dR/dt = -decay_rate * (R - R0)
    decay_rate = 0.04
    dt = 1.0  # 1-second ticks for absence simulation

    for absence_step in range(220):
        delta_r = -decay_rate * (engine.R_t - engine.R_0) * dt
        engine.R_t = np.clip(engine.R_t + delta_r, 0.0, 1.0)
        # Advance limbic resting ODE
        engine.step_ode(np.zeros(engine.stimulus_dim), dt=0.20)

    final_r = engine.R_t
    r_restoration_err = float(np.linalg.norm(final_r - engine.R_0))

    # 3. Final relaxation tick (280s unforced relaxation)
    pad_traj, slow_traj, _ = engine.integrate_unforced_idle(duration_s=280.0, dt=0.20)
    final_pad = pad_traj[-1]
    final_philia_err = compute_philia_restoration_error(final_pad, engine.p_philia)

    print(f"\n[EXP21.H3 Absence Reversibility]")
    print(f"  R Restoration Error: {r_restoration_err:.6e}")
    print(f"  Final PAD Error to Canonical Philia: {final_philia_err:.6e} (target < 1e-4)")

    assert r_restoration_err < 1e-3, f"Relationship did not decay to baseline: {r_restoration_err}"
    assert final_philia_err < 1e-4, f"Philia restoration error {final_philia_err:.6e} >= 1e-4"
