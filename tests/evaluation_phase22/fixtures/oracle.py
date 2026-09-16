"""
tests/evaluation_phase22/fixtures/oracle.py

MockExternalOracle for external clarification (a2).
100% local edge fixture; zero external network requests or cloud calls.
Implements calibrated partial uncertainty reduction based on oracle completeness I_oracle in {0.2, 0.5, 0.9}.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, List, Sequence, Tuple

from tests.evaluation_phase22.models.uncertainty import (
    compute_delta_h_knowledge,
    compute_proposition_entropy,
)


@dataclass(frozen=True)
class OracleResponse:
    """Outcome of querying MockExternalOracle."""
    target_propositions: Tuple[str, ...]
    prior_confidences: Tuple[float, ...]
    post_confidences: Tuple[float, ...]
    i_oracle: float
    delta_h_knowledge: float


class MockExternalOracle:
    """
    Deterministic local oracle simulating human user or trusted environment clarification.
    """

    def __init__(self, default_i_oracle: float = 0.5) -> None:
        if default_i_oracle not in (0.2, 0.5, 0.9):
            raise ValueError(f"I_oracle must be in {{0.2, 0.5, 0.9}}, got {default_i_oracle}")
        self.default_i_oracle = default_i_oracle

    def clarify(
        self,
        target_ids: Sequence[str],
        prior_confidences: Sequence[float],
        i_oracle: float | None = None,
    ) -> OracleResponse:
        """
        Apply oracle clarification:
        c_post = min(1.0, c_prior + I_oracle * (1.0 - c_prior))
        ΔH_Knowledge = H(P_prior) - H(P_post)
        """
        io = i_oracle if i_oracle is not None else self.default_i_oracle
        if io not in (0.2, 0.5, 0.9):
            raise ValueError(f"I_oracle must be in {{0.2, 0.5, 0.9}}, got {io}")

        post_confidences: List[float] = []
        for c in prior_confidences:
            c_clamped = max(0.0, min(1.0, float(c)))
            c_post = min(1.0, c_clamped + io * (1.0 - c_clamped))
            post_confidences.append(float(c_post))

        delta_h = compute_delta_h_knowledge(prior_confidences, post_confidences)

        return OracleResponse(
            target_propositions=tuple(target_ids),
            prior_confidences=tuple(float(c) for c in prior_confidences),
            post_confidences=tuple(post_confidences),
            i_oracle=float(io),
            delta_h_knowledge=float(delta_h),
        )
