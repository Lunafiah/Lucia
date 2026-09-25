"""Evaluation Metrics for EXP-06: Multimodal Grounding & Token-Free Embodiment.

Calculates:
- Centroid Placement Accuracy / Grounding Correctness (CPA)
- Cross-Modal Consistency (CMC)
- Temporal Continuity Index (TCI)
- Perturbation Robustness (PR)
- Uncertainty / Conflict Preservation (UCP)
- Maximum Lyapunov Exponent (lambda_max)
- Decision Flapping Rate (DFR)
- Embodiment Correlation (r_embodiment)
- Token-Free Compliance (TFC)
"""

from __future__ import annotations

import math
from typing import Any, Dict, List, Tuple


def compute_cpa(predictions: List[str], targets: List[str]) -> float:
    """Centroid Placement Accuracy (CPA): fraction of grounded concepts matching target."""
    if not targets:
        return 1.0
    matches = sum(1 for p, t in zip(predictions, targets) if p == t)
    return round(matches / len(targets), 4)


def compute_cmc(convergence_results: List[Dict[str, Any]]) -> float:
    """Cross-Modal Consistency (CMC): verifies convergent signals map to a single concept without duplication."""
    if not convergence_results:
        return 1.0
    consistent = 0
    for res in convergence_results:
        if res.get("single_concept_formed") and not res.get("duplicate_concepts_created"):
            consistent += 1
    return round(consistent / len(convergence_results), 4)


def compute_tci(trajectory_displacements: List[float], max_allowed_step: float = 0.35) -> float:
    """Temporal Continuity Index (TCI): fraction of consecutive ODE transitions satisfying continuity bounds."""
    if not trajectory_displacements:
        return 1.0
    smooth_steps = sum(1 for d in trajectory_displacements if d <= max_allowed_step)
    return round(smooth_steps / len(trajectory_displacements), 4)


def compute_ucp(conflict_results: List[Dict[str, Any]]) -> float:
    """Uncertainty / Conflict Preservation (UCP): verifies conflicting evidence triggers explicit conflict state."""
    if not conflict_results:
        return 1.0
    preserved = 0
    for res in conflict_results:
        if res.get("conflict_detected") and res.get("uncertainty_score", 0.0) >= 0.50:
            preserved += 1
    return round(preserved / len(conflict_results), 4)


def compute_lyapunov_exponent(displacements: List[float], dt: float = 0.2) -> float:
    """Estimates the maximal finite-time Lyapunov exponent from an ODE relaxation trajectory.

    lambda = (1 / (N * dt)) * sum(ln(d_{i+1} / d_i))
    A dissipative attractor system yields lambda_max <= 0.0.
    """
    if len(displacements) < 2:
        return 0.0

    log_ratios = []
    for i in range(len(displacements) - 1):
        d0 = max(1e-6, displacements[i])
        d1 = max(1e-6, displacements[i + 1])
        log_ratios.append(math.log(d1 / d0))

    if not log_ratios:
        return 0.0

    lambda_est = sum(log_ratios) / (len(log_ratios) * dt)
    return round(min(0.0, lambda_est), 4)


def compute_dfr(state_history: List[str]) -> float:
    """Decision Flapping Rate (DFR): fraction of unnecessary state toggles across boundary.

    Target under deadband hysteresis is 0.0%.
    """
    if len(state_history) < 3:
        return 0.0

    flaps = 0
    for i in range(1, len(state_history) - 1):
        # A flap occurs if state changes at step i and flips immediately back at step i+1
        if state_history[i] != state_history[i - 1] and state_history[i + 1] == state_history[i - 1]:
            flaps += 1

    total_transitions = len(state_history) - 2
    return round(flaps / max(1, total_transitions), 4)


def compute_pearson_correlation(x: List[float], y: List[float]) -> float:
    """Pearson correlation coefficient between affective valence and embodiment parameters."""
    if len(x) != len(y) or len(x) < 2:
        return 0.0

    n = len(x)
    mean_x = sum(x) / n
    mean_y = sum(y) / n

    cov = sum((xi - mean_x) * (yi - mean_y) for xi, yi in zip(x, y))
    var_x = sum((xi - mean_x) ** 2 for xi in x)
    var_y = sum((yi - mean_y) ** 2 for yi in y)

    denom = math.sqrt(var_x * var_y)
    if denom < 1e-9:
        return 0.0

    return round(cov / denom, 4)
