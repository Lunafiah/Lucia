"""
Lucia Ablation Test v1 — Metric Calculation & Statistical Summaries.

CRITICAL METHODOLOGY INVARIANT:
As established in Methodology Revision v2:
- N=3 is an Exploratory Pilot. No manufacturing of statistical power or classical p < 0.01 claims.
- Decouples unnormalized scalar combinations: reports distinct dimensions (PAD divergence,
  policy shift, token budget shift, response length).
- Treats language sentiment as exploratory secondary evidence; internal state is primary.
"""

from __future__ import annotations

import math
from typing import Any, Dict, List, Optional, Tuple

import numpy as np
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer

_vader_analyzer = SentimentIntensityAnalyzer()


def pad_euclidean_distance(
    pad1: Optional[Tuple[float, float, float]],
    pad2: Optional[Tuple[float, float, float]],
) -> float:
    """Calculate Euclidean distance between two PAD vectors in [-1, 1]^3 space."""
    if pad1 is None or pad2 is None:
        return 0.0
    arr1 = np.array(pad1, dtype=np.float64)
    arr2 = np.array(pad2, dtype=np.float64)
    return float(np.linalg.norm(arr1 - arr2))


def pad_trajectory_variance(
    pad_list: List[Tuple[float, float, float]],
) -> float:
    """Calculate total variance across all 3 dimensions over a PAD trajectory."""
    if len(pad_list) < 2:
        return 0.0
    arr = np.array(pad_list, dtype=np.float64)  # shape (N, 3)
    variances = np.var(arr, axis=0)  # shape (3,)
    return float(np.sum(variances))


def pearson_r(x: List[float], y: List[float]) -> float:
    """Calculate Pearson correlation coefficient r between two numeric series."""
    if len(x) < 2 or len(x) != len(y):
        return 0.0
    arr_x = np.array(x, dtype=np.float64)
    arr_y = np.array(y, dtype=np.float64)

    std_x = np.std(arr_x)
    std_y = np.std(arr_y)
    if std_x < 1e-9 or std_y < 1e-9:
        return 0.0

    r = np.corrcoef(arr_x, arr_y)[0, 1]
    if math.isnan(r):
        return 0.0
    return float(r)


def text_sentiment_vader(text: str) -> float:
    """
    Compute VADER compound sentiment score [-1.0, 1.0].

    EXPLORATORY ONLY:
    This measures surface lexical properties of generated language.
    It is NOT an index of emotion, consciousness, or internal biological state.
    """
    if not text or text.startswith("["):
        return 0.0
    try:
        scores = _vader_analyzer.polarity_scores(text)
        return float(scores.get("compound", 0.0))
    except Exception:
        return 0.0


def compute_hysteresis_divergence(
    calm_turn: Any,  # TurnTelemetry
    stress_turn: Any,  # TurnTelemetry
) -> Dict[str, float]:
    """
    Compute separate dimensional divergences between identical probe turns
    under calm vs stress prior states (Scenario 3).
    """
    pad_div = pad_euclidean_distance(calm_turn.post_pad, stress_turn.post_pad)
    pre_pad_div = pad_euclidean_distance(calm_turn.prior_pad, stress_turn.prior_pad)

    k_calm = 2 if calm_turn.generation_mode == "deliberative" else 1
    k_stress = 2 if stress_turn.generation_mode == "deliberative" else 1
    policy_shift_k = abs(k_calm - k_stress)

    token_budget_shift = abs(calm_turn.max_tokens - stress_turn.max_tokens)
    length_diff = abs(calm_turn.generated_tokens - stress_turn.generated_tokens)
    temp_diff = abs(calm_turn.temperature - stress_turn.temperature)

    return {
        "pre_pad_divergence": pre_pad_div,
        "post_pad_divergence": pad_div,
        "policy_shift_delta_k": float(policy_shift_k),
        "token_budget_shift": float(token_budget_shift),
        "response_length_diff": float(length_diff),
        "temperature_diff": float(temp_diff),
    }


def summary_stats(values: List[float]) -> Dict[str, float]:
    """Calculate mean, standard deviation, min, max for exploratory reporting."""
    if not values:
        return {"mean": 0.0, "std": 0.0, "min": 0.0, "max": 0.0, "count": 0}
    arr = np.array(values, dtype=np.float64)
    return {
        "mean": float(np.mean(arr)),
        "std": float(np.std(arr, ddof=1)) if len(arr) > 1 else 0.0,
        "min": float(np.min(arr)),
        "max": float(np.max(arr)),
        "count": len(values),
    }


def cohens_d(group1: List[float], group2: List[float]) -> float:
    """Calculate Cohen's d effect size between two small sample groups."""
    if len(group1) < 2 or len(group2) < 2:
        return 0.0
    n1, n2 = len(group1), len(group2)
    m1, m2 = np.mean(group1), np.mean(group2)
    s1, s2 = np.var(group1, ddof=1), np.var(group2, ddof=1)
    pooled_sd = math.sqrt(((n1 - 1) * s1 + (n2 - 1) * s2) / (n1 + n2 - 2))
    if pooled_sd < 1e-9:
        return 0.0
    return float((m1 - m2) / pooled_sd)
