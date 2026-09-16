"""
tests/evaluation_phase22/fixtures/memory.py

SDM traces, competitive ecphory fixtures, and extended Hamming search (a3).
Models deterministic radius expansion from r = 451 to r = 470.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import List, Sequence, Tuple

from tests.evaluation_phase22.models.uncertainty import (
    compute_delta_h_memory,
    compute_ecphory_entropy,
)


@dataclass(frozen=True)
class CandidateTrace:
    """A candidate SDM memory trace with salience evaluated at two radii."""
    trace_id: int
    content_summary: str
    salience_at_451: float   # Salience under standard Kanerva radius r = 451
    salience_at_470: float   # Salience under expanded radius r = 470


class SimulatedSDMEngine:
    """
    Deterministic SDM fixture evaluating ecphory competition and expanded probing.
    """

    def __init__(self, theta_gate: float = 0.50, tau_comp: float = 0.20) -> None:
        self.theta_gate = theta_gate
        self.tau_comp = tau_comp

    def evaluate_prior(self, traces: Sequence[CandidateTrace]) -> float:
        """Compute prior ecphory entropy at standard radius r = 451."""
        scores = [t.salience_at_451 for t in traces]
        return compute_ecphory_entropy(scores, self.theta_gate, self.tau_comp)

    def execute_extended_probe(
        self, traces: Sequence[CandidateTrace]
    ) -> Tuple[float, float, float]:
        """
        Execute a3: expand Hamming search radius from 451 to 470.
        Returns:
          (h_prior_nats, h_post_nats, delta_h_memory)
        """
        prior_scores = [t.salience_at_451 for t in traces]
        post_scores = [t.salience_at_470 for t in traces]

        h_prior = compute_ecphory_entropy(prior_scores, self.theta_gate, self.tau_comp)
        h_post = compute_ecphory_entropy(post_scores, self.theta_gate, self.tau_comp)
        delta_h = compute_delta_h_memory(prior_scores, post_scores, self.theta_gate, self.tau_comp)

        return float(h_prior), float(h_post), float(delta_h)
