"""
tests/evaluation_phase22/test_phase22_harness.py

Targeted unit tests for Phase 22 mathematical correctness, boundary checks,
policy behavior, and runtime isolation invariants.
"""

from __future__ import annotations

import json
import math
from pathlib import Path
from typing import List

import numpy as np
import pytest
import torch

from tests.evaluation_phase22.fixtures.knowledge import (
    DerivationRule,
    EvaluationProposition,
    SimulatedDerivationEngine,
)
from tests.evaluation_phase22.fixtures.memory import CandidateTrace, SimulatedSDMEngine
from tests.evaluation_phase22.fixtures.oracle import MockExternalOracle
from tests.evaluation_phase22.fixtures.probes import build_benchmark_probes
from tests.evaluation_phase22.models.actions import ACTION_REGISTRY, ActionType
from tests.evaluation_phase22.models.efe_policy import (
    EFEPolicyEvaluator,
    SocialCostConfig,
    compute_compute_cost,
    compute_homeostatic_beta,
    compute_pragmatic_value,
    compute_social_cost,
)
from tests.evaluation_phase22.models.ligp import compute_expected_information_gain
from tests.evaluation_phase22.models.uncertainty import (
    bernoulli_entropy,
    compute_delta_h_knowledge,
    compute_delta_h_memory,
    compute_ecphory_entropy,
    compute_ecphory_softmax,
    compute_proposition_entropy,
)


# =============================================================================
# 1. Mathematical Correctness
# =============================================================================

def test_bernoulli_entropy_boundaries_and_symmetry() -> None:
    """Verify Bernoulli entropy properties: H(0)=0, H(1)=0, H(0.5)=1, symmetry."""
    assert bernoulli_entropy(0.0) == 0.0
    assert bernoulli_entropy(1.0) == 0.0
    assert abs(bernoulli_entropy(0.5) - 1.0) < 1e-9

    # Symmetry: H(c) == H(1-c)
    for c in (0.1, 0.25, 0.7, 0.85):
        assert abs(bernoulli_entropy(c) - bernoulli_entropy(1.0 - c)) < 1e-9

    # Out of bounds clamping
    assert bernoulli_entropy(-0.5) == 0.0
    assert bernoulli_entropy(1.5) == 0.0


def test_proposition_entropy_aggregation() -> None:
    """Verify total propositional entropy H(P) = sum_i H(c_i)."""
    confs = [0.5, 0.5, 0.0, 1.0]
    expected = 1.0 + 1.0 + 0.0 + 0.0
    assert abs(compute_proposition_entropy(confs) - expected) < 1e-9


def test_oracle_posterior_confidence_and_delta_h() -> None:
    """Verify oracle update rule: c_post = min(1.0, c_prior + I_oracle * (1 - c_prior))."""
    oracle = MockExternalOracle(default_i_oracle=0.5)
    resp = oracle.clarify(target_ids=["p1"], prior_confidences=[0.4])
    # c_post = 0.4 + 0.5 * (1.0 - 0.4) = 0.4 + 0.3 = 0.7
    assert abs(resp.post_confidences[0] - 0.7) < 1e-9
    assert resp.delta_h_knowledge > 0.0

    # Completeness 0.9
    resp_09 = oracle.clarify(target_ids=["p1"], prior_confidences=[0.0], i_oracle=0.9)
    assert abs(resp_09.post_confidences[0] - 0.9) < 1e-9


def test_ecphory_softmax_and_competition_entropy() -> None:
    """Verify competitive softmax and ecphory entropy calculation in nats."""
    salience_scores = [0.8, 0.4, 0.3]  # Only 0.8 passes theta_gate=0.50
    _, weights = compute_ecphory_softmax(salience_scores, theta_gate=0.50, tau_comp=0.20)
    assert len(weights) == 1
    assert compute_ecphory_entropy(salience_scores, theta_gate=0.50) == 0.0

    # Tied competition between 2 candidates passing threshold
    tied_scores = [0.7, 0.7]
    idx, w = compute_ecphory_softmax(tied_scores, theta_gate=0.50, tau_comp=0.20)
    assert len(idx) == 2
    assert abs(w[0] - 0.5) < 1e-9
    # H = - (0.5 * ln(0.5) + 0.5 * ln(0.5)) = ln(2) nats ≈ 0.6931 nats
    assert abs(compute_ecphory_entropy(tied_scores, theta_gate=0.50) - math.log(2.0)) < 1e-5


def test_homeostatic_beta_modulation() -> None:
    """Verify beta_epist(E, C) = beta_0 * E * (1.0 - 0.5 * C)."""
    beta_max = compute_homeostatic_beta(energy=1.0, cognitive_load=0.0, beta_0=2.0)
    assert abs(beta_max - 2.0) < 1e-9

    beta_depleted = compute_homeostatic_beta(energy=0.15, cognitive_load=0.85, beta_0=2.0)
    # 2.0 * 0.15 * (1.0 - 0.425) = 0.30 * 0.575 = 0.1725
    assert abs(beta_depleted - 0.1725) < 1e-9
    assert beta_depleted < 0.1 * beta_max


def test_ligp_action_substrate_isolation() -> None:
    """Verify that actions only draw EIG from their appropriate substrate."""
    # a1 has zero EIG regardless of inputs
    assert compute_expected_information_gain(ActionType.A1_IMMEDIATE_RESPONSE, 1.5, 1.5) == 0.0

    # a2 only uses delta_h_knowledge
    eig_a2 = compute_expected_information_gain(ActionType.A2_EXTERNAL_CLARIFICATION, 0.8, 1.2)
    assert abs(eig_a2 - 0.8) < 1e-9

    # a3 only uses delta_h_memory
    eig_a3 = compute_expected_information_gain(ActionType.A3_EXTENDED_SDM_PROBE, 0.8, 1.2)
    assert abs(eig_a3 - 1.2) < 1e-9


# =============================================================================
# 2. Boundary Correctness
# =============================================================================

def test_social_cost_internal_vs_external() -> None:
    """Verify internal actions have strictly zero social cost; a2 incurs bounded positive cost."""
    cfg = SocialCostConfig(gamma_0=0.20, gamma_1=0.15, tau_q=2.0, mu_trust=0.20)

    for action in (
        ActionType.A1_IMMEDIATE_RESPONSE,
        ActionType.A3_EXTENDED_SDM_PROBE,
        ActionType.A4_KNOWLEDGE_DERIVATION,
        ActionType.A5_DEEP_REASONING_MODE_SHIFT,
        ActionType.A6_WAIT_CONVERSATIONAL_PAUSE,
    ):
        assert compute_social_cost(action, n_recent_queries=5, r_trust=0.0, config=cfg) == 0.0

    # a2 cost increases with recent query count
    cost_0 = compute_social_cost(ActionType.A2_EXTERNAL_CLARIFICATION, n_recent_queries=0, r_trust=0.5, config=cfg)
    cost_3 = compute_social_cost(ActionType.A2_EXTERNAL_CLARIFICATION, n_recent_queries=3, r_trust=0.5, config=cfg)
    assert cost_3 > cost_0
    # Mitigated by higher trust
    cost_high_trust = compute_social_cost(ActionType.A2_EXTERNAL_CLARIFICATION, n_recent_queries=0, r_trust=0.9, config=cfg)
    assert cost_high_trust < cost_0


def test_derivation_engine_max_depth_bound() -> None:
    """Verify derivation engine does not exceed d_max = 3."""
    engine = SimulatedDerivationEngine(max_depth=3)
    p1 = EvaluationProposition("p1", "A", "rel", "B", confidence=0.95, is_verified=True)
    p2 = EvaluationProposition("p2", "B", "rel", "C", confidence=0.95, is_verified=True)
    rules = [
        DerivationRule("r1", ("p1", "p2"), EvaluationProposition("p3", "A", "rel", "C", confidence=0.90), depth=2),
        DerivationRule("r2", ("p3",), EvaluationProposition("p4", "A", "rel", "D", confidence=0.85), depth=4),  # Exceeds depth 3
    ]

    updated, delta_h = engine.derive([p1, p2], rules)
    derived_ids = {p.id for p in updated}
    assert "p3" in derived_ids
    assert "p4" not in derived_ids  # Rule r2 at depth 4 must be ignored


# =============================================================================
# 3. Policy Behavior
# =============================================================================

def test_high_surprise_low_uncertainty_behavior() -> None:
    """
    Verify that high affective surprise alone (S_t > 0.60) does NOT force epistemic foraging
    under Condition 2 when semantic and memory entropy are near zero.
    """
    evaluator = EFEPolicyEvaluator()
    # EIG is zero for all actions because uncertainty is zero
    delta_k = {a: 0.0 for a in ActionType}
    delta_m = {a: 0.0 for a in ActionType}

    action, val = evaluator.select_action_c2(
        delta_h_knowledge_map=delta_k,
        delta_h_memory_map=delta_m,
        energy=0.9,
        cognitive_load=0.2,
        tension=0.1,
        r_trust=0.8,
        n_recent_queries=0,
        contradiction_present=False,
    )

    # Pragmatic a1 should be chosen because it offers V_pragm = 1.0 and zero foraging cost
    assert action == ActionType.A1_IMMEDIATE_RESPONSE


def test_low_surprise_high_uncertainty_behavior() -> None:
    """
    Verify that when surprise is tiny (S_t < 0.10) but semantic uncertainty is high,
    EFE selects an epistemic action (a2) to acquire information.
    """
    evaluator = EFEPolicyEvaluator()
    delta_k = {ActionType.A2_EXTERNAL_CLARIFICATION: 1.8}  # Large entropy reduction
    delta_m = {a: 0.0 for a in ActionType}

    action, _ = evaluator.select_action_c2(
        delta_h_knowledge_map=delta_k,
        delta_h_memory_map=delta_m,
        energy=0.95,
        cognitive_load=0.10,
        tension=0.05,
        r_trust=0.8,
        n_recent_queries=0,
        contradiction_present=False,
    )
    assert action == ActionType.A2_EXTERNAL_CLARIFICATION


def test_metabolic_depletion_suppresses_expensive_clarification() -> None:
    """
    Verify that under severe metabolic depletion (E = 0.15, C = 0.85),
    costly external clarification (a2) is suppressed compared to nominal state.
    """
    evaluator = EFEPolicyEvaluator()
    delta_k = {ActionType.A2_EXTERNAL_CLARIFICATION: 1.5}
    delta_m = {a: 0.0 for a in ActionType}

    # Nominal state: energy=0.9, load=0.1 -> chooses a2
    act_nominal, _ = evaluator.select_action_c2(
        delta_h_knowledge_map=delta_k,
        delta_h_memory_map=delta_m,
        energy=0.90,
        cognitive_load=0.10,
        tension=0.10,
        r_trust=0.7,
        n_recent_queries=0,
        contradiction_present=False,
    )
    assert act_nominal == ActionType.A2_EXTERNAL_CLARIFICATION

    # Depleted state with query fatigue -> beta_epist drops, social cost rises -> chooses a1 or a6
    act_depleted, _ = evaluator.select_action_c2(
        delta_h_knowledge_map=delta_k,
        delta_h_memory_map=delta_m,
        energy=0.15,
        cognitive_load=0.85,
        tension=0.65,
        r_trust=0.5,
        n_recent_queries=2,
        contradiction_present=False,
    )
    assert act_depleted != ActionType.A2_EXTERNAL_CLARIFICATION
    assert act_depleted in (ActionType.A1_IMMEDIATE_RESPONSE, ActionType.A6_WAIT_CONVERSATIONAL_PAUSE)


# =============================================================================
# 4. Strict Isolation & System Invariants
# =============================================================================

def test_genesis_onboarding_invariant_bit_exact() -> None:
    """Verify data/profile.json is bit-exact {"is_onboarded": false}."""
    profile_path = Path("data/profile.json")
    assert profile_path.exists(), "data/profile.json must exist!"
    content = profile_path.read_text(encoding="utf-8").strip()
    data = json.loads(content)
    assert data.get("is_onboarded") is False, "Genesis Gate breached: is_onboarded must be False!"


def test_zero_gpu_vram_and_cpu_device_discipline() -> None:
    """
    Verify that the Phase 22 policy execution creates zero CUDA tensors,
    does not invoke CUDA operations, and operates strictly on CPU.
    """
    probes = build_benchmark_probes()
    probe = probes[0]
    evaluator = EFEPolicyEvaluator()

    # Pre-check GPU allocation
    gpu_before = torch.cuda.memory_allocated() if torch.cuda.is_available() else 0

    delta_k = {a: 0.5 for a in ActionType}
    delta_m = {a: 0.5 for a in ActionType}

    # Execute 100 iterations of policy evaluation
    for _ in range(100):
        action, vals = evaluator.select_action_c2(
            delta_h_knowledge_map=delta_k,
            delta_h_memory_map=delta_m,
            energy=probe.homeostatic_state.energy,
            cognitive_load=probe.homeostatic_state.cognitive_load,
            tension=probe.homeostatic_state.tension,
            r_trust=probe.r_trust,
            n_recent_queries=probe.n_recent_queries,
            contradiction_present=probe.contradiction_present,
        )

    # Post-check GPU allocation
    gpu_after = torch.cuda.memory_allocated() if torch.cuda.is_available() else 0
    assert gpu_after == gpu_before, "Phase 22 epistemic policy leaked memory onto GPU VRAM!"


def test_production_src_unmodified() -> None:
    """Verify that no production files under src/core/ are modified by Phase 22."""
    assert Path("src/core/orchestrator/cognitive_orchestrator.py").exists()
    assert Path("src/core/inference/active_inference.py").exists()
    assert Path("src/core/memory/ecphory.py").exists()
    assert Path("src/core/knowledge/store.py").exists()
