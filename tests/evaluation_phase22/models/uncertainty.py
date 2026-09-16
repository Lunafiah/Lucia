"""
tests/evaluation_phase22/models/uncertainty.py

Mathematical formulation of semantic and memory uncertainty substrates.
Strictly decoupled from affective/physiological surprise S_t and PAD variance.
"""

from __future__ import annotations

import math
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Sequence, Tuple

import numpy as np


def bernoulli_entropy(c: float) -> float:
    """
    Binary Shannon entropy (base 2) for confidence c in [0.0, 1.0].
    H(c) = -c * log2(c) - (1-c) * log2(1-c)
    Returns 0.0 for c <= 0.0 or c >= 1.0.
    """
    c = float(np.clip(c, 0.0, 1.0))
    if c <= 1e-12 or c >= 1.0 - 1e-12:
        return 0.0
    return -(c * math.log2(c) + (1.0 - c) * math.log2(1.0 - c))


def compute_proposition_entropy(confidences: Sequence[float]) -> float:
    """
    Total propositional entropy H(P) = sum_i H(c_i) in bits.
    """
    return float(sum(bernoulli_entropy(c) for c in confidences))


def compute_delta_h_knowledge(
    prior_confidences: Sequence[float],
    post_confidences: Sequence[float],
) -> float:
    """
    Knowledge entropy reduction:
    ΔH_Knowledge = H(P_prior) - H(P_post)
    Positive value denotes uncertainty reduction (information gain).
    """
    h_prior = compute_proposition_entropy(prior_confidences)
    h_post = compute_proposition_entropy(post_confidences)
    return float(max(0.0, h_prior - h_post))


def compute_ecphory_softmax(
    salience_scores: Sequence[float],
    theta_gate: float = 0.50,
    tau_comp: float = 0.20,
) -> Tuple[np.ndarray, np.ndarray]:
    """
    Competitive softmax gating for candidate memory traces passing theta_gate.
    Returns:
      (passing_indices, alpha_weights)
    """
    scores = np.asarray(salience_scores, dtype=np.float64)
    passing_idx = np.where(scores >= theta_gate)[0]
    if len(passing_idx) == 0:
        return np.array([], dtype=np.int64), np.array([], dtype=np.float64)

    passing_scores = scores[passing_idx]
    max_s = np.max(passing_scores)
    exp_s = np.exp((passing_scores - max_s) / tau_comp)
    sum_exp = np.sum(exp_s)
    if sum_exp <= 1e-12:
        weights = np.ones(len(passing_scores), dtype=np.float64) / len(passing_scores)
    else:
        weights = exp_s / sum_exp

    return passing_idx, weights


def compute_ecphory_entropy(
    salience_scores: Sequence[float],
    theta_gate: float = 0.50,
    tau_comp: float = 0.20,
) -> float:
    """
    Memory competition entropy in nats:
    H_Ecphory = - sum_i alpha_i * ln(alpha_i)
    Returns 0.0 if fewer than 2 candidates pass theta_gate.
    """
    _, weights = compute_ecphory_softmax(salience_scores, theta_gate, tau_comp)
    if len(weights) <= 1:
        return 0.0

    # Shannon entropy in natural units (nats)
    ent = 0.0
    for w in weights:
        if w > 1e-12:
            ent -= float(w * math.log(w))
    return float(max(0.0, ent))


def compute_delta_h_memory(
    prior_salience_scores: Sequence[float],
    post_salience_scores: Sequence[float],
    theta_gate: float = 0.50,
    tau_comp: float = 0.20,
) -> float:
    """
    Memory entropy reduction:
    ΔH_Memory = H_Ecphory_prior - H_Ecphory_post
    Positive value denotes resolved competition.
    """
    h_prior = compute_ecphory_entropy(prior_salience_scores, theta_gate, tau_comp)
    h_post = compute_ecphory_entropy(post_salience_scores, theta_gate, tau_comp)
    return float(max(0.0, h_prior - h_post))


@dataclass(frozen=True)
class UncertaintyState:
    """
    Snapshot of decoupled cognitive uncertainty substrates for a turn.
    """
    u_sem: float              # Semantic/propositional uncertainty (normalized or aggregate bits)
    u_mem: float              # Memory competition uncertainty (nats)
    h_knowledge_bits: float   # Raw H(P) in bits
    h_ecphory_nats: float     # Raw H_Ecphory in nats
    s_physiological: float    # Retrospective prediction surprise S_t = ||p_hat - p||_2
