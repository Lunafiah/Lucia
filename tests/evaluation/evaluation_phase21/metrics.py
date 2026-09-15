"""
tests/evaluation_phase21/metrics.py

Quantitative evaluation metrics for Phase 21 Experimental Validation Cycle (H1 - H6).
Strictly pre-registered operational definitions without post-hoc relaxation.
"""

from __future__ import annotations

from typing import Any, Dict, List, Optional, Tuple

import numpy as np


def compute_homeostatic_settling(
    trajectory_times: np.ndarray,
    energies: np.ndarray,
    tensions: np.ndarray,
    target_time_s: float,
) -> Tuple[float, float]:
    """
    Interpolate and evaluate energy and tension at target_time_s.
    """
    if len(trajectory_times) == 0:
        return 0.0, 1.0

    idx = np.searchsorted(trajectory_times, target_time_s)
    if idx == 0:
        return float(energies[0]), float(tensions[0])
    if idx >= len(trajectory_times):
        return float(energies[-1]), float(tensions[-1])

    t0, t1 = trajectory_times[idx - 1], trajectory_times[idx]
    w = (target_time_s - t0) / (t1 - t0 + 1e-12)
    e_interp = float(energies[idx - 1] + w * (energies[idx] - energies[idx - 1]))
    t_interp = float(tensions[idx - 1] + w * (tensions[idx] - tensions[idx - 1]))
    return e_interp, t_interp


def compute_catastrophic_forgetting_drift(
    baseline_probe_loss_before: float,
    baseline_probe_loss_after: float,
) -> float:
    """
    Compute percentage drift in loss over standard baseline probe tasks.
    drift = (|L_after - L_before| / (L_before + 1e-9)) * 100%
    """
    denom = max(abs(baseline_probe_loss_before), 1e-6)
    drift = (abs(baseline_probe_loss_after - baseline_probe_loss_before) / denom) * 100.0
    return float(drift)


def compute_relational_displacement(
    s_eff: np.ndarray,
    s_philia: np.ndarray,
    pad_eff: np.ndarray,
    p_philia: np.ndarray,
) -> Tuple[float, float]:
    """
    Compute slow attractor displacement and projected PAD displacement.
    Returns: (slow_displacement_l2, pad_displacement_l2)
    """
    slow_disp = float(np.linalg.norm(s_eff - s_philia))
    pad_disp = float(np.linalg.norm(pad_eff - p_philia))
    return slow_disp, pad_disp


def compute_philia_restoration_error(
    final_pad: np.ndarray,
    p_philia: np.ndarray,
) -> float:
    """
    Compute epsilon error of unforced long-term resting PAD against canonical Philia attractor.
    """
    return float(np.linalg.norm(final_pad - p_philia))


def cosine_similarity(v1: np.ndarray, v2: np.ndarray) -> float:
    """Compute cosine similarity between two 1D vectors."""
    n1 = np.linalg.norm(v1)
    n2 = np.linalg.norm(v2)
    if n1 < 1e-12 or n2 < 1e-12:
        return 0.0
    return float(np.dot(v1, v2) / (n1 * n2))


def compute_trajectory_auc(
    trajectory: np.ndarray,
    baseline: np.ndarray,
    dt: float = 0.20,
) -> float:
    """
    Compute Area Under Curve (integrated L2 deflection) over time.
    AUC = sum_t (||trajectory[t] - baseline|| * dt)
    """
    diffs = np.linalg.norm(trajectory - baseline, axis=1)
    return float(np.sum(diffs) * dt)


def compute_cohens_d(group1: np.ndarray, group2: np.ndarray) -> float:
    """Compute Cohen's d effect size between two empirical sample distributions."""
    n1, n2 = len(group1), len(group2)
    if n1 < 2 or n2 < 2:
        return 0.0
    var1, var2 = np.var(group1, ddof=1), np.var(group2, ddof=1)
    pooled_sd = np.sqrt(((n1 - 1) * var1 + (n2 - 1) * var2) / (n1 + n2 - 2))
    if pooled_sd < 1e-12:
        return 0.0
    return float(abs(np.mean(group1) - np.mean(group2)) / pooled_sd)


def compute_percentiles(latencies_ms: List[float]) -> Dict[str, float]:
    """Compute p50, p90, p95, p99, and max latencies."""
    if not latencies_ms:
        return {"p50": 0.0, "p90": 0.0, "p95": 0.0, "p99": 0.0, "max": 0.0, "mean": 0.0}
    arr = np.array(latencies_ms, dtype=np.float64)
    return {
        "p50": float(np.percentile(arr, 50)),
        "p90": float(np.percentile(arr, 90)),
        "p95": float(np.percentile(arr, 95)),
        "p99": float(np.percentile(arr, 99)),
        "max": float(np.max(arr)),
        "mean": float(np.mean(arr)),
    }
