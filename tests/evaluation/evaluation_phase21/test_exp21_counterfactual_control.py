"""
tests/evaluation_phase21/test_exp21_counterfactual_control.py

Stage 4 Evaluation Track: Computational Plasticity & Counterfactual Controls (H4).

Addresses the Phase 11 vector-dependence vulnerability:
  Verifies that computational synaptic consolidation responds to authentic, structured
  relational interaction history rather than arbitrary random vector energy or shuffled temporal order.

Pre-Registered Acceptance Criteria under 'Failure is Informative' Protocol:
  1. Parameter-Update Directional Cosine Similarity:
     - CosineSim(Delta Theta_auth, Delta Theta_shuffled) <= 0.20 (primary control)
     - CosineSim(Delta Theta_auth, Delta Theta_random) <= 0.20
  2. Trajectory Divergence Ratio:
     - AUC(Authentic) / AUC(Random) >= 2.50
  3. Statistical Outcome Specificity:
     - Effect size Cohen's d >= 1.20 (large separation > 3 sigma between authentic and control distributions)
"""

from __future__ import annotations

import numpy as np
import pytest

from tests.evaluation_phase21.consolidation_engine import RelationalConsolidationEngine
from tests.evaluation_phase21.metrics import (
    compute_cohens_d,
    compute_trajectory_auc,
    cosine_similarity,
)
from tests.evaluation_phase21.scenarios import ScenarioGenerator


@pytest.fixture
def scenario_gen() -> ScenarioGenerator:
    return ScenarioGenerator(seed=3030)


@pytest.fixture
def engine() -> RelationalConsolidationEngine:
    return RelationalConsolidationEngine(seed=42)


def test_h4_parameter_update_directional_similarity(
    engine: RelationalConsolidationEngine,
    scenario_gen: ScenarioGenerator,
) -> None:
    """
    Verify that gradient / parameter updates Delta Theta resulting from offline consolidation
    are strictly dependent on authentic temporal structure (shuffled <= 0.20, random <= 0.20).
    """
    # 1. Generate authentic interaction sequence
    session = scenario_gen.generate_authentic_relational_session(n_turns=16)

    # Record experiences under authentic run
    for stim, sig, salience in session:
        hb = engine._h_fast.copy()
        ha, ss = engine.step_ode(stim, dt=0.20)
        engine.update_relationship_state(sig, alpha=0.03)
        engine.record_experience(stim, hb, ha, ss, salience)

    auth_batch = [exp for exp in engine.experience_buffer if exp.salience >= 0.50]
    assert len(auth_batch) >= 8

    # 2. Generate controlled counterfactual cohorts
    shuffled_batch, random_batch, ortho_batch = scenario_gen.create_counterfactual_controls(auth_batch)

    # 3. Compute Delta Theta for Authentic condition
    init_params = engine.get_parameter_state()
    w_init = init_params.flatten_weights()

    params_auth, _ = engine.run_offline_consolidation(auth_batch, learning_rate=2e-4)
    delta_auth = params_auth.flatten_weights() - w_init

    # Reset engine parameters back to init
    engine.set_parameter_state(init_params)

    # 4. Compute Delta Theta for Shuffled condition (primary temporal control)
    params_shuffled, _ = engine.run_offline_consolidation(shuffled_batch, learning_rate=2e-4)
    delta_shuffled = params_shuffled.flatten_weights() - w_init

    # Reset engine parameters back to init
    engine.set_parameter_state(init_params)

    # 5. Compute Delta Theta for Random noise condition
    params_random, _ = engine.run_offline_consolidation(random_batch, learning_rate=2e-4)
    delta_random = params_random.flatten_weights() - w_init

    # 6. Evaluate Cosine Similarities
    cos_shuffled = cosine_similarity(delta_auth, delta_shuffled)
    cos_random = cosine_similarity(delta_auth, delta_random)

    print(f"\n[EXP21.H4 Directional Parameter Similarity]")
    print(f"  CosineSim(Delta Theta_auth, Delta Theta_shuffled) = {cos_shuffled:.4f} (target <= 0.20)")
    print(f"  CosineSim(Delta Theta_auth, Delta Theta_random)   = {cos_random:.4f} (target <= 0.20)")

    assert cos_shuffled <= 0.20, f"Authentic vs Shuffled similarity {cos_shuffled:.4f} > 0.20"
    assert cos_random <= 0.20, f"Authentic vs Random similarity {cos_random:.4f} > 0.20"


def test_h4_trajectory_divergence_and_auc_ratio(
    engine: RelationalConsolidationEngine,
    scenario_gen: ScenarioGenerator,
) -> None:
    """
    Verify that authentic consolidation yields significant trajectory divergence compared to
    unperturbed baseline, exceeding random noise injection by AUC_auth / AUC_random >= 2.50.
    """
    session = scenario_gen.generate_authentic_relational_session(n_turns=16)

    # Collect experiences
    for stim, sig, salience in session:
        hb = engine._h_fast.copy()
        ha, ss = engine.step_ode(stim, dt=0.20)
        engine.update_relationship_state(sig, alpha=0.03)
        engine.record_experience(stim, hb, ha, ss, salience)

    auth_batch = [exp for exp in engine.experience_buffer if exp.salience >= 0.50]
    _, random_batch, _ = scenario_gen.create_counterfactual_controls(auth_batch)

    init_params = engine.get_parameter_state()

    # Consolidate with authentic batch
    params_auth, _ = engine.run_offline_consolidation(auth_batch, learning_rate=2e-4)
    engine.set_parameter_state(params_auth)
    pad_traj_auth, _, _ = engine.integrate_unforced_idle(duration_s=60.0, dt=0.20)

    # Reset to baseline
    engine.set_parameter_state(init_params)
    pad_traj_base, _, _ = engine.integrate_unforced_idle(duration_s=60.0, dt=0.20)

    # Consolidate with random batch
    engine.set_parameter_state(init_params)
    params_random, _ = engine.run_offline_consolidation(random_batch, learning_rate=2e-4)
    engine.set_parameter_state(params_random)
    pad_traj_random, _, _ = engine.integrate_unforced_idle(duration_s=60.0, dt=0.20)

    # Compute AUC
    auc_auth = compute_trajectory_auc(pad_traj_auth, engine.p_philia, dt=0.20)
    auc_random = compute_trajectory_auc(pad_traj_random, engine.p_philia, dt=0.20)
    auc_ratio = auc_auth / (auc_random + 1e-12)

    print(f"\n[EXP21.H4 Trajectory Divergence AUC]")
    print(f"  AUC(Authentic) = {auc_auth:.4f}")
    print(f"  AUC(Random)    = {auc_random:.4f}")
    print(f"  AUC Ratio      = {auc_ratio:.4f} (target >= 2.50)")

    assert auc_ratio >= 2.50, f"AUC ratio {auc_ratio:.4f} < 2.50"


def test_h4_statistical_outcome_specificity(
    engine: RelationalConsolidationEngine,
    scenario_gen: ScenarioGenerator,
) -> None:
    """
    Verify distribution separation (Cohen's d >= 1.20) across repeated trials of authentic
    vs shuffled vs random consolidation parameter updates.
    """
    cos_auths: List[float] = []
    cos_shufs: List[float] = []
    cos_rands: List[float] = []

    for trial in range(8):
        gen = ScenarioGenerator(seed=4000 + trial * 37)
        sess = gen.generate_authentic_relational_session(n_turns=16)

        eng = RelationalConsolidationEngine(seed=100 + trial)
        for stim, sig, salience in sess:
            hb = eng._h_fast.copy()
            ha, ss = eng.step_ode(stim, dt=0.20)
            eng.update_relationship_state(sig, alpha=0.03)
            eng.record_experience(stim, hb, ha, ss, salience)

        batch = [e for e in eng.experience_buffer if e.salience >= 0.50]
        shuf, rand, _ = gen.create_counterfactual_controls(batch)

        init_p = eng.get_parameter_state()
        w_init = init_p.flatten_weights()

        # Auth
        p_auth, _ = eng.run_offline_consolidation(batch, learning_rate=1e-3)
        d_auth = p_auth.flatten_weights() - w_init

        # Shuffled
        eng.set_parameter_state(init_p)
        p_shuf, _ = eng.run_offline_consolidation(shuf, learning_rate=1e-3)
        d_shuf = p_shuf.flatten_weights() - w_init

        # Random
        eng.set_parameter_state(init_p)
        p_rand, _ = eng.run_offline_consolidation(rand, learning_rate=1e-3)
        d_rand = p_rand.flatten_weights() - w_init

        # Directional cosine similarities
        cs_s = cosine_similarity(d_auth, d_shuf)
        cs_r = cosine_similarity(d_auth, d_rand)
        cos_shufs.append(cs_s)
        cos_rands.append(cs_r)

        # Split-half internal consistency of authentic session
        even_batch = [batch[i] for i in range(0, len(batch), 2)]
        eng.set_parameter_state(init_p)
        p_even, _ = eng.run_offline_consolidation(even_batch, learning_rate=1e-3)
        d_even = p_even.flatten_weights() - w_init
        cs_a = cosine_similarity(d_auth, d_even)
        cos_auths.append(cs_a)

    arr_auth = np.array(cos_auths)
    arr_shuf = np.array(cos_shufs)
    arr_rand = np.array(cos_rands)

    d_shuf = compute_cohens_d(arr_auth, arr_shuf)
    d_rand = compute_cohens_d(arr_auth, arr_rand)

    print(f"\n[EXP21.H4 Outcome Specificity Cohen's d]")
    print(f"  CosSim Auth (split-half): {np.mean(arr_auth):.4f} +/- {np.std(arr_auth):.4f}")
    print(f"  CosSim Shuffled:          {np.mean(arr_shuf):.4f} +/- {np.std(arr_shuf):.4f}")
    print(f"  CosSim Random:            {np.mean(arr_rand):.4f} +/- {np.std(arr_rand):.4f}")
    print(f"  Cohen's d (Auth vs Shuffled): {d_shuf:.3f} (target >= 1.20)")
    print(f"  Cohen's d (Auth vs Random):   {d_rand:.3f} (target >= 1.20)")

    assert d_shuf >= 1.20, f"Cohen's d (Auth vs Shuffled) {d_shuf:.3f} < 1.20"
    assert d_rand >= 1.20, f"Cohen's d (Auth vs Random) {d_rand:.3f} < 1.20"
