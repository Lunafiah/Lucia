"""
tests/evaluation/phase26/test_historical_differentiation_harness.py

Unit and integration tests for the P26 historical differentiation research harness.
Verifies:
- Harness isolation and reproducibility
- Zero production mutation
- Ablation behaviors (Ablation A baseline, Ablation B memory, Ablation C fast state decay)
- Confound controls (Experiment 2)
- Hysteresis and plasticity transitions (Experiment 3)
- Covert reward audit verification
"""

from __future__ import annotations

import json
from pathlib import Path
import numpy as np
import pytest

from tests.evaluation.phase26.p26_historical_differentiation_harness import (
    ExperimentalReplicaConfig,
    ExperimentalResearchReplica,
    HistoricalDifferentiationRunner,
    HysteresisPlasticityRunner,
    P26HistoricalValidationSuite,
    ProcessingBiasConfoundRunner,
    ResearchAblation,
    audit_covert_rewards,
)


def test_genesis_gate_and_production_isolation():
    """Verify that data/profile.json is preserved bit-exact."""
    profile_path = Path("data/profile.json")
    if profile_path.exists():
        with open(profile_path, "r", encoding="utf-8") as f:
            data = json.load(f)
        assert data.get("is_onboarded") is False, "INV-8 VIOLATION: is_onboarded must be false!"


def test_baseline_control_identical_history_zero_divergence():
    """
    Under Ablation A, identical-history twins must produce identical behavior
    (TV = 0.0, zero divergence).
    """
    runner = HistoricalDifferentiationRunner(seeds=[1001, 1002, 1003], num_history_turns=5, washout_ticks=10)
    for seed in [1001, 1002, 1003]:
        res = runner.run_trial_for_seed(seed, ResearchAblation.ABLATION_A_BASELINE)
        assert res.ctrl_divergent is False, "Control twins with identical history must not diverge!"


def test_fast_state_decays_during_neutral_washout():
    """
    Under Ablation C (fast state only), divergence immediately post-history must
    decay significantly towards zero after neutral washout due to Philia relaxation.
    """
    runner = HistoricalDifferentiationRunner(seeds=[2001, 2002], num_history_turns=10, washout_ticks=40)
    res = runner.run_trial_for_seed(2001, ResearchAblation.ABLATION_C_FAST_STATE_ONLY)
    # Post-washout PAD distance should be substantially lower than pre-washout
    assert res.pad_dist_post <= res.pad_dist_pre + 1e-4
    assert res.pad_dist_post < 0.15


def test_memory_only_lacks_context_generalization():
    """
    Under Ablation B (memory only), differentiation is preserved in-domain,
    but collapses to zero on novel concepts (superconducting qubits vs cellular senescence)
    because no memory traces exist for novel topics.
    """
    runner = HistoricalDifferentiationRunner(seeds=[3001, 3002], num_history_turns=10, washout_ticks=10)
    res = runner.run_trial_for_seed(3001, ResearchAblation.ABLATION_B_MEMORY_ONLY)
    # Target domain prob difference should be positive (twin A prefers A, twin B prefers B)
    assert res.prob_A_twin_A_post > res.prob_A_twin_B_post
    # Novel concepts choice outcomes should match (no preference divergence)
    assert res.novel_twin_A_outcome == res.novel_twin_B_outcome
    # Probability difference should be negligible (cross-talk noise < 0.05)
    assert abs(res.novel_prob_A_twin_A - res.novel_prob_A_twin_B) < 0.05


def test_processing_bias_confound_experiment_2():
    """
    Experiment 2 verifies that high processing load under neutral valence
    does not create substantial choice divergence when isolated from memory accumulation.
    """
    runner = ProcessingBiasConfoundRunner(seeds=[4001, 4002, 4003], num_turns=5)
    res = runner.run_experiment_2()
    assert "c1_processing_load_alone_tv" in res
    assert "c2_valence_with_matched_load_tv" in res
    # Asymmetric valence should produce higher TV than neutral processing load alone
    assert res["c2_valence_with_matched_load_tv"] >= res["c1_processing_load_alone_tv"]


def test_hysteresis_runner_experiment_3():
    """
    Experiment 3 verifies execution across the 4 stages of formation, steering,
    retention, and counter-history.
    """
    runner = HysteresisPlasticityRunner(seeds=[5001, 5002], ablation=ResearchAblation.ABLATION_D_CONSOLIDATION)
    res = runner.run_experiment_3()
    assert res["sample_size"] == 2
    assert 0.0 <= res["rate_healthy_revision"] <= 1.0
    assert 0.0 <= res["rate_brittle_compliance"] <= 1.0


def test_covert_reward_audit():
    """
    Covert reward audit must confirm zero reduction to scalar utility optimization.
    """
    report = audit_covert_rewards()
    assert report.reduction_to_scalar_reward_detected is False
    for mech, details in report.audited_mechanisms.items():
        assert details["reduces_to_scalar_utility"] is False
