"""
tests/evaluation_phase22/fixtures/knowledge.py

Propositional knowledge models, deduction rules, and forward derivation simulation (a4).
Deterministic forward derivation bounded by maximum depth d <= 3.
"""

from __future__ import annotations

import uuid
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Sequence, Tuple

from tests.evaluation_phase22.models.uncertainty import (
    bernoulli_entropy,
    compute_delta_h_knowledge,
    compute_proposition_entropy,
)


@dataclass(frozen=True)
class EvaluationProposition:
    """Proposition item for evaluation probe."""
    id: str
    subject: str
    predicate: str
    object: str
    confidence: float          # Confidence in [0.0, 1.0]
    is_verified: bool = False  # Verified knowledge (c >= 0.90)
    is_contradicted: bool = False

    @property
    def entropy_bits(self) -> float:
        return bernoulli_entropy(self.confidence)


@dataclass(frozen=True)
class DerivationRule:
    """Symbolic rule for a4: antecedent -> consequent."""
    rule_id: str
    antecedent_props: Tuple[str, ...]
    consequent_prop: EvaluationProposition
    depth: int = 1


class SimulatedDerivationEngine:
    """
    Deterministic forward derivation fixture for a4.
    Applies inference rules up to max_depth = 3 without LLM calls.
    """

    def __init__(self, max_depth: int = 3) -> None:
        self.max_depth = max_depth

    def derive(
        self,
        current_propositions: Sequence[EvaluationProposition],
        available_rules: Sequence[DerivationRule],
    ) -> Tuple[List[EvaluationProposition], float]:
        """
        Execute forward deduction steps up to max_depth.
        Returns:
          (updated_propositions, delta_h_knowledge)
        """
        props_by_id = {p.id: p for p in current_propositions}
        prior_confidences = [p.confidence for p in current_propositions]

        for depth in range(1, self.max_depth + 1):
            derived_in_pass = 0
            for rule in available_rules:
                if rule.depth > self.max_depth:
                    continue
                # Check if all antecedents exist and have high confidence
                antecedents_valid = True
                min_conf = 1.0
                for a_id in rule.antecedent_props:
                    if a_id not in props_by_id or props_by_id[a_id].confidence < 0.60:
                        antecedents_valid = False
                        break
                    min_conf = min(min_conf, props_by_id[a_id].confidence)

                if antecedents_valid:
                    consequent = rule.consequent_prop
                    if (
                        consequent.id not in props_by_id
                        or props_by_id[consequent.id].confidence < consequent.confidence
                    ):
                        props_by_id[consequent.id] = consequent
                        derived_in_pass += 1

            if derived_in_pass == 0:
                break

        updated_list = list(props_by_id.values())
        post_confidences = [p.confidence for p in updated_list]

        # Calculate knowledge gain from newly established or resolved facts
        delta_h = compute_delta_h_knowledge(prior_confidences, post_confidences)
        # If new facts were added with high confidence (e.g. c=0.95, H=0.28 bits),
        # they reduce unbound slot entropy (which had max entropy 1.0 bit)
        if len(updated_list) > len(current_propositions):
            # Prior unbound slots had implicit confidence 0.5 (1 bit entropy)
            unbound_prior_entropy = (len(updated_list) - len(current_propositions)) * 1.0
            new_fact_entropy = sum(
                p.entropy_bits for p in updated_list if p.id not in {cp.id for cp in current_propositions}
            )
            delta_h += max(0.0, unbound_prior_entropy - new_fact_entropy)

        return updated_list, float(delta_h)
