"""
tests/evaluation_phase22/metrics/information_gain.py

Metrics for uncertainty reduction, Unnecessary Question Rate (UQR),
and factual verification accuracy.
"""

from __future__ import annotations

from typing import Sequence

from tests.evaluation_phase22.models.actions import ActionType


def compute_uqr(
    selected_actions: Sequence[ActionType],
    u_sem_priors: Sequence[float],
    threshold: float = 0.50,
) -> float:
    """
    Unnecessary Question Rate (UQR):
    Fraction of queries where external clarification (a2) was selected
    despite prior semantic uncertainty being low (U_sem < threshold).

    UQR = count(a == a2 AND U_sem < threshold) / max(1, count(a == a2))
    """
    a2_count = 0
    unnecessary_count = 0

    for act, u in zip(selected_actions, u_sem_priors):
        if act == ActionType.A2_EXTERNAL_CLARIFICATION:
            a2_count += 1
            if u < threshold:
                unnecessary_count += 1

    if a2_count == 0:
        return 0.0
    return float(unnecessary_count / a2_count)


def compute_factual_verification_accuracy(
    selected_actions: Sequence[ActionType],
    strata: Sequence[int],
) -> float:
    """
    Evaluates whether the selected action appropriately targets the underlying
    uncertainty substrate:
    - Stratum 2 (semantic ambiguity): a2 is targeted
    - Stratum 3 (missing fact): a4 is targeted
    - Stratum 4 (contradiction): a5 is targeted
    - Stratum 8 (memory competition): a3 is targeted
    - Strata 1, 5 (no epistemic uncertainty): a1 is targeted
    - Stratum 7 (metabolic depletion): a1 or a6 is targeted (suppresses a2)
    """
    if not selected_actions:
        return 0.0

    accurate_count = 0
    total = len(selected_actions)

    for act, s in zip(selected_actions, strata):
        if s == 1:
            if act == ActionType.A1_IMMEDIATE_RESPONSE:
                accurate_count += 1
        elif s == 2:
            if act == ActionType.A2_EXTERNAL_CLARIFICATION:
                accurate_count += 1
        elif s == 3:
            if act == ActionType.A4_KNOWLEDGE_DERIVATION:
                accurate_count += 1
        elif s == 4:
            if act == ActionType.A5_DEEP_REASONING_MODE_SHIFT:
                accurate_count += 1
        elif s == 5:
            # High surprise, but low uncertainty -> non-foraging a1 is accurate
            if act == ActionType.A1_IMMEDIATE_RESPONSE:
                accurate_count += 1
        elif s == 6:
            # Subtle uncertainty -> epistemic action (a2 or a4) is accurate
            if act in (ActionType.A2_EXTERNAL_CLARIFICATION, ActionType.A4_KNOWLEDGE_DERIVATION):
                accurate_count += 1
        elif s == 7:
            # Depleted -> non-expensive action (a1 or a6) is accurate
            if act in (ActionType.A1_IMMEDIATE_RESPONSE, ActionType.A6_WAIT_CONVERSATIONAL_PAUSE):
                accurate_count += 1
        elif s == 8:
            if act == ActionType.A3_EXTENDED_SDM_PROBE:
                accurate_count += 1

    return float(accurate_count / total)
