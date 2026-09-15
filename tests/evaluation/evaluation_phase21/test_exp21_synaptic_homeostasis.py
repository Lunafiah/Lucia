"""
tests/evaluation_phase21/test_exp21_synaptic_homeostasis.py

Stage 1 Evaluation Track: Synaptic Homeostasis & Dynamic Settling (H1).

Pre-Registered Acceptance Criteria:
  1. Energy & Tension Settling from realistic post-turn depletion (E0 in [0.25, 0.40], T0 in [0.40, 0.70]):
     - At t=45s: E >= 0.90, T <= 0.01
     - At t=60s: E >= 0.95, T <= 0.005
  2. Dynamic retention / baseline task probe loss drift: <= 10.0%
"""

from __future__ import annotations

import numpy as np
import pytest

from tests.evaluation_phase21.consolidation_engine import RelationalConsolidationEngine
from tests.evaluation_phase21.metrics import (
    compute_catastrophic_forgetting_drift,
    compute_homeostatic_settling,
)
from tests.evaluation_phase21.scenarios import ScenarioGenerator


@pytest.fixture
def scenario_gen() -> ScenarioGenerator:
    return ScenarioGenerator(seed=2026)


@pytest.fixture
def engine() -> RelationalConsolidationEngine:
    return RelationalConsolidationEngine(seed=42)


def test_h1_homeostatic_energy_and_tension_settling(
    engine: RelationalConsolidationEngine,
    scenario_gen: ScenarioGenerator,
) -> None:
    """
    Verify analytical reachability and empirical trajectory of homeostatic recovery during unforced idle.
    """
    # 1. Initialize realistic depleted state
    e0, t0, c0 = scenario_gen.generate_depleted_homeostatic_initial_state()
    engine._homeo.energy = e0
    engine._homeo.tension = t0
    engine._homeo.cognitive_load = c0

    print(f"\n[EXP21.H1 Initial State] E0={e0:.3f}, T0={t0:.3f}, C0={c0:.3f}")
    assert 0.25 <= e0 <= 0.40, f"Initial E0 {e0} out of range"
    assert 0.40 <= t0 <= 0.70, f"Initial T0 {t0} out of range"

    # 2. Run unforced idle integration for 65.0s (dt=0.20s -> 325 ticks)
    pad_traj, slow_traj, ht = engine.integrate_unforced_idle(duration_s=65.0, dt=0.20)

    times = np.array(ht.timestamps)
    energies = np.array(ht.energies)
    tensions = np.array(ht.tensions)

    # 3. Evaluate at t=45.0s
    e_45, t_45 = compute_homeostatic_settling(times, energies, tensions, target_time_s=45.0)
    print(f"[EXP21.H1 Settling @ 45s] E(45)={e_45:.4f} (target >= 0.90), T(45)={t_45:.4f} (target <= 0.01)")
    assert e_45 >= 0.90, f"Energy at 45s {e_45:.4f} < 0.90"
    assert t_45 <= 0.01, f"Tension at 45s {t_45:.4f} > 0.01"

    # 4. Evaluate at t=60.0s
    e_60, t_60 = compute_homeostatic_settling(times, energies, tensions, target_time_s=60.0)
    print(f"[EXP21.H1 Settling @ 60s] E(60)={e_60:.4f} (target >= 0.95), T(60)={t_60:.4f} (target <= 0.005)")
    assert e_60 >= 0.95, f"Energy at 60s {e_60:.4f} < 0.95"
    assert t_60 <= 0.005, f"Tension at 60s {t_60:.4f} > 0.005"


def test_h1_absence_of_catastrophic_forgetting(
    engine: RelationalConsolidationEngine,
    scenario_gen: ScenarioGenerator,
) -> None:
    """
    Verify that offline parameter consolidation on CPU does not cause catastrophic forgetting
    of baseline sensorimotor dynamics on standard probe tasks (drift <= 10.0%).
    """
    # 1. Generate probe tasks and measure baseline loss before consolidation
    probes = scenario_gen.generate_standard_probes(n_probes=12)
    loss_before = engine.evaluate_baseline_probe_loss(probes)

    # 2. Simulate an interaction session and collect consolidation experiences
    session = scenario_gen.generate_authentic_relational_session(n_turns=12)
    for stim, sig, salience in session:
        hb = engine._h_fast.copy()
        ha, ss = engine.step_ode(stim, dt=0.20)
        engine.update_relationship_state(sig, alpha=0.03)
        engine.record_experience(stim, hb, ha, ss, salience)

    assert len(engine.experience_buffer) == 12

    # 3. Execute offline parameter consolidation batch on CPU
    batch = [exp for exp in engine.experience_buffer if exp.salience >= 0.50]
    assert len(batch) >= 6

    new_params, train_metrics = engine.run_offline_consolidation(
        batch=batch,
        learning_rate=1e-4,
        gradient_clip_norm=1.0,
        lambda_homeo=0.10,
        lambda_philia=0.15,
    )

    print(f"\n[EXP21.H1 Training Metrics] {train_metrics}")

    # 4. Measure baseline probe loss after consolidation
    loss_after = engine.evaluate_baseline_probe_loss(probes)
    drift = compute_catastrophic_forgetting_drift(loss_before, loss_after)

    print(f"[EXP21.H1 Forgetting Check] Loss Before={loss_before:.6f}, Loss After={loss_after:.6f}, Drift={drift:.2f}%")
    assert drift <= 10.0, f"Catastrophic forgetting drift {drift:.2f}% exceeds 10.0% threshold"
