"""
tests/evaluation_phase22/test_phase22_properties.py

Hypothesis property-based tests for Phase 22 mathematical invariants.
Validates entropy bounds, LIGP non-negativity, and EFE stability across domains.
"""

from __future__ import annotations

import math
from hypothesis import given, settings, strategies as st

from tests.evaluation_phase22.models.actions import ActionType
from tests.evaluation_phase22.models.efe_policy import (
    EFEConfig,
    EFEPolicyEvaluator,
    compute_homeostatic_beta,
    compute_social_cost,
)
from tests.evaluation_phase22.models.ligp import compute_expected_information_gain
from tests.evaluation_phase22.models.uncertainty import bernoulli_entropy, compute_proposition_entropy


# -----------------------------------------------------------------------------
# Property 1: Bernoulli entropy bounds & continuity
# -----------------------------------------------------------------------------

@settings(max_examples=200)
@given(c=st.floats(min_value=-10.0, max_value=10.0))
def test_property_bernoulli_entropy_bounds(c: float) -> None:
    """Invariant: H(c) must be strictly in [0.0, 1.0] for any input float."""
    h = bernoulli_entropy(c)
    assert 0.0 <= h <= 1.0 + 1e-9
    assert not math.isnan(h)
    assert not math.isinf(h)


# -----------------------------------------------------------------------------
# Property 2: Proposition entropy non-negativity
# -----------------------------------------------------------------------------

@settings(max_examples=100)
@given(confs=st.lists(st.floats(min_value=0.0, max_value=1.0), min_size=0, max_size=50))
def test_property_proposition_entropy_non_negative(confs: list[float]) -> None:
    """Invariant: H(P) >= 0.0 and bounded by len(confs) * 1.0 bit."""
    h_p = compute_proposition_entropy(confs)
    assert h_p >= -1e-9
    assert h_p <= len(confs) * 1.0 + 1e-9


# -----------------------------------------------------------------------------
# Property 3: LIGP Expected Information Gain Non-Negativity
# -----------------------------------------------------------------------------

@settings(max_examples=100)
@given(
    action=st.sampled_from(list(ActionType)),
    delta_k=st.floats(min_value=-5.0, max_value=5.0),
    delta_m=st.floats(min_value=-5.0, max_value=5.0),
)
def test_property_ligp_non_negativity(action: ActionType, delta_k: float, delta_m: float) -> None:
    """Invariant: EIG(a) must be >= 0.0 regardless of input deltas."""
    eig = compute_expected_information_gain(action, delta_k, delta_m)
    assert eig >= 0.0
    assert not math.isnan(eig)


# -----------------------------------------------------------------------------
# Property 4: Homeostatic beta non-negativity and bounds
# -----------------------------------------------------------------------------

@settings(max_examples=100)
@given(
    e=st.floats(min_value=0.0, max_value=1.0),
    c=st.floats(min_value=0.0, max_value=1.0),
    b0=st.floats(min_value=0.1, max_value=10.0),
)
def test_property_homeostatic_beta_bounds(e: float, c: float, b0: float) -> None:
    """Invariant: beta_epist(E, C) in [0.0, b0]."""
    beta = compute_homeostatic_beta(e, c, b0)
    assert 0.0 <= beta <= b0 + 1e-9


# -----------------------------------------------------------------------------
# Property 5: Social Cost Zero for Internal Actions
# -----------------------------------------------------------------------------

@settings(max_examples=100)
@given(
    action=st.sampled_from([
        ActionType.A1_IMMEDIATE_RESPONSE,
        ActionType.A3_EXTENDED_SDM_PROBE,
        ActionType.A4_KNOWLEDGE_DERIVATION,
        ActionType.A5_DEEP_REASONING_MODE_SHIFT,
        ActionType.A6_WAIT_CONVERSATIONAL_PAUSE,
    ]),
    n_q=st.integers(min_value=-10, max_value=20),
    trust=st.floats(min_value=-2.0, max_value=2.0),
)
def test_property_social_cost_internal_zero(action: ActionType, n_q: int, trust: float) -> None:
    """Invariant: Internal actions have strictly 0.0 social cost under all inputs."""
    cost = compute_social_cost(action, n_q, trust)
    assert cost == 0.0


# -----------------------------------------------------------------------------
# Property 6: EFE G(a) values are always finite
# -----------------------------------------------------------------------------

@settings(max_examples=100)
@given(
    e=st.floats(min_value=0.0, max_value=1.0),
    c=st.floats(min_value=0.0, max_value=1.0),
    tension=st.floats(min_value=0.0, max_value=1.0),
    trust=st.floats(min_value=0.0, max_value=1.0),
    n_q=st.integers(min_value=0, max_value=5),
)
def test_property_efe_valuations_finite(
    e: float, c: float, tension: float, trust: float, n_q: int
) -> None:
    """Invariant: G(a) for all actions must be finite real numbers."""
    evaluator = EFEPolicyEvaluator()
    delta_k = {a: 0.5 for a in ActionType}
    delta_m = {a: 0.5 for a in ActionType}

    best_action, vals = evaluator.select_action_c2(
        delta_h_knowledge_map=delta_k,
        delta_h_memory_map=delta_m,
        energy=e,
        cognitive_load=c,
        tension=tension,
        r_trust=trust,
        n_recent_queries=n_q,
        contradiction_present=False,
    )
    assert best_action in ActionType
    for a, v in vals.items():
        assert not math.isnan(v.g_value)
        assert not math.isinf(v.g_value)
