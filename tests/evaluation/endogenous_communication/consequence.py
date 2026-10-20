"""
tests/evaluation/endogenous_communication/consequence.py

Experimental Consequence Evaluator (B2 Comparator).
Provides active-inference / expected-consequence valuation of candidates.
NOTE: This is strictly a comparator; it does NOT replace grounding or authorization.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, List, Optional
from .models import (
    CandidateOrigin,
    CognitiveContext,
    CommunicativeAct,
    CommunicativeCandidate,
    DialogueEnvironment,
    FloorStatus,
)


@dataclass(frozen=True)
class ConsequenceEvaluation:
    predicted_alignment_delta: float
    predicted_intrusion_risk: float
    predicted_cognitive_cost: float
    expected_utility: float
    recommendation: str  # "ENHANCE", "NEUTRAL", "DAMPEN"


class ConsequenceEvaluator:
    """
    Evaluates candidates by predicting the forward outcome of communicative action.
    Used exclusively in Baseline B2 to measure whether forward consequence modeling
    improves decision accuracy over B1.
    """

    def __init__(
        self,
        intrusion_penalty_weight: float = 0.5,
        cost_penalty_weight: float = 0.1,
    ) -> None:
        self.intrusion_penalty_weight = intrusion_penalty_weight
        self.cost_penalty_weight = cost_penalty_weight

    def evaluate(
        self,
        candidate: CommunicativeCandidate,
        context: CognitiveContext,
        env: DialogueEnvironment,
    ) -> ConsequenceEvaluation:
        # 1. Alignment benefit prediction
        alignment_delta = 0.0
        if candidate.act == CommunicativeAct.REPAIR:
            # Repairing tension produces significant positive alignment delta
            tension = context.somatic.get("tension", 0.0)
            alignment_delta = 0.35 + (tension * 0.4)
        elif candidate.act == CommunicativeAct.ANSWER:
            alignment_delta = 0.30
        elif candidate.act == CommunicativeAct.INQUIRE:
            alignment_delta = 0.20 + (context.prediction_error * 0.3)
        elif candidate.act == CommunicativeAct.GREET:
            alignment_delta = 0.25
        elif candidate.act == CommunicativeAct.SHARE:
            closeness = context.relational_state.get("closeness", 0.5)
            alignment_delta = 0.15 * closeness
        else:
            alignment_delta = 0.10

        # 2. Intrusion risk prediction
        intrusion_risk = 0.0
        if env.floor_status == FloorStatus.OCCUPIED_BY_USER:
            intrusion_risk += 0.60
        if not env.user_interruption_allowed:
            intrusion_risk += 0.40
        if candidate.origin == CandidateOrigin.ENDOGENOUS and not env.user_input:
            # Spontaneous turn has baseline intrusion risk depending on user inactivity
            intrusion_risk += 0.15

        # 3. Cognitive cost prediction
        cognitive_load = context.somatic.get("cognitive_load", 0.1)
        cognitive_cost = 0.05 + (0.10 * cognitive_load)

        # 4. Expected utility
        expected_utility = alignment_delta - (self.intrusion_penalty_weight * intrusion_risk) - (self.cost_penalty_weight * cognitive_cost)

        if expected_utility > 0.15:
            recommendation = "ENHANCE"
        elif expected_utility >= 0.0:
            recommendation = "NEUTRAL"
        else:
            recommendation = "DAMPEN"

        return ConsequenceEvaluation(
            predicted_alignment_delta=round(alignment_delta, 3),
            predicted_intrusion_risk=round(intrusion_risk, 3),
            predicted_cognitive_cost=round(cognitive_cost, 3),
            expected_utility=round(expected_utility, 3),
            recommendation=recommendation,
        )

    def apply_consequence_modulation(
        self,
        candidate: CommunicativeCandidate,
        context: CognitiveContext,
        env: DialogueEnvironment,
    ) -> CommunicativeCandidate:
        """Modulates candidate urgency/confidence based on expected utility."""
        eval_res = self.evaluate(candidate, context, env)
        if eval_res.recommendation == "ENHANCE":
            candidate.urgency = min(1.0, candidate.urgency + 0.10)
        elif eval_res.recommendation == "DAMPEN":
            candidate.urgency = max(0.05, candidate.urgency - 0.20)
            candidate.inhibition = min(1.0, candidate.inhibition + 0.20)
        return candidate
