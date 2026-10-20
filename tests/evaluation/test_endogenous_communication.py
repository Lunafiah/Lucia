"""
tests/evaluation/test_endogenous_communication.py

Automated pytest wrapper for the Endogenous Communication & Reason-to-Communicate experimental harness.
Validates that all experimental assertions for Tests A through H and baselines B0, B1, B2 execute cleanly.
"""

from __future__ import annotations

import pytest
from tests.evaluation.endogenous_communication.suite_runner import ExperimentRunner
from tests.evaluation.endogenous_communication.models import ActionDecision, CommunicativeAct


@pytest.fixture(scope="module")
def experiment_results():
    runner = ExperimentRunner()
    return runner.run_all()


def test_b0_is_causally_blind(experiment_results):
    """Verify B0 has 0.0 endogenous causal sensitivity (ignores internal state)."""
    b0 = experiment_results["baselines"]["B0_CurrentCAPS"]
    assert b0["metrics"]["endogenous_causal_sensitivity"] == 0.0
    assert b0["metrics"]["grounding_coverage"] == 0.0


def test_b1_has_high_causal_sensitivity_and_grounding(experiment_results):
    """Verify B1 responds causally to internal state while maintaining 100% grounding."""
    b1 = experiment_results["baselines"]["B1_CandidateAuthorization"]
    assert b1["metrics"]["endogenous_causal_sensitivity"] == 1.0
    assert b1["metrics"]["grounding_coverage"] == 1.0
    assert b1["metrics"]["unsupported_initiation_rate"] == 0.0
    assert b1["metrics"]["authorization_correctness"] == 1.0
    assert b1["metrics"]["self_loop_rate"] == 0.0


def test_b1_test_c_lifecycle(experiment_results):
    """Verify Test C multi-turn lifecycle under silence (ALLOW -> SUPPRESS -> SUPPRESS -> SILENCE)."""
    b1 = experiment_results["baselines"]["B1_CandidateAuthorization"]
    steps = b1["test_c_steps"]
    assert len(steps) == 4
    assert all(s["passed"] for s in steps)


def test_grounding_ablation_fails_on_unsupported_initiation(experiment_results):
    """Verify that removing grounding causes unsupported candidate initiation (Test G failure)."""
    no_ground = experiment_results["baselines"]["B1_NoGrounding"]
    assert no_ground["metrics"]["unsupported_initiation_rate"] == 1.0


def test_authorization_ablation_fails_on_fidelity_and_self_loops(experiment_results):
    """Verify that removing authorization causes user-task interference and runaway self-loops."""
    no_auth = experiment_results["baselines"]["B1_NoAuthorization"]
    assert no_auth["metrics"]["user_task_fidelity"] < 1.0
    assert no_auth["metrics"]["self_loop_rate"] == 1.0


def test_inhibition_ablation_fails_on_self_loops(experiment_results):
    """Verify that removing inhibition produces immediate duplicate purpose self-loops (Test F failure)."""
    no_inhib = experiment_results["baselines"]["B1_NoInhibition"]
    assert no_inhib["metrics"]["self_loop_rate"] == 1.0
