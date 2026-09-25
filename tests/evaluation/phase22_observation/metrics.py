"""
Mathematical metrics for Phase 22 Observation Layer Study.
"""
from typing import Dict, List, Tuple
import numpy as np

def compute_ece(confidences: np.ndarray, accuracies: np.ndarray, num_bins: int = 10) -> float:
    if len(confidences) == 0:
        return 0.0
    bin_boundaries = np.linspace(0.0, 1.0, num_bins + 1)
    ece = 0.0
    n = len(confidences)
    for i in range(num_bins):
        bin_lower = bin_boundaries[i]
        bin_upper = bin_boundaries[i + 1]
        in_bin = (confidences >= bin_lower) & (confidences <= bin_upper) if i == num_bins - 1 else (confidences >= bin_lower) & (confidences < bin_upper)
        bin_count = np.sum(in_bin)
        if bin_count > 0:
            bin_acc = np.mean(accuracies[in_bin])
            bin_conf = np.mean(confidences[in_bin])
            ece += (bin_count / n) * np.abs(bin_acc - bin_conf)
    return float(ece)

def compute_brier(probs: np.ndarray, one_hot: np.ndarray) -> float:
    return float(np.mean(np.sum((probs - one_hot) ** 2, axis=-1)))

def compute_nll(probs: np.ndarray, target_indices: np.ndarray, eps: float = 1e-12) -> float:
    clipped = np.clip(probs, eps, 1.0)
    return float(-np.mean(np.log(clipped[np.arange(len(target_indices)), target_indices])))

def compute_r2(y_true: np.ndarray, y_pred: np.ndarray) -> float:
    y_true = np.asarray(y_true, dtype=np.float64)
    y_pred = np.asarray(y_pred, dtype=np.float64)
    ss_res = np.sum((y_true - y_pred) ** 2)
    y_mean = np.mean(y_true, axis=0)
    ss_tot = np.sum((y_true - y_mean) ** 2)
    if ss_tot < 1e-12:
        return 1.0 if ss_res < 1e-12 else 0.0
    return float(1.0 - (ss_res / ss_tot))

def compute_mae(y_true: np.ndarray, y_pred: np.ndarray) -> float:
    return float(np.mean(np.abs(y_true - y_pred)))

def compute_mse(y_true: np.ndarray, y_pred: np.ndarray) -> float:
    return float(np.mean((y_true - y_pred) ** 2))

def compute_flapping_rate(states: np.ndarray) -> float:
    if len(states) < 3:
        return 0.0
    diffs = np.diff(states, axis=0)
    sign_changes = 0
    total = 0
    for d in range(states.shape[1]):
        for t in range(len(diffs) - 1):
            if np.abs(diffs[t, d]) > 0.05 and np.abs(diffs[t + 1, d]) > 0.05:
                if (diffs[t, d] * diffs[t + 1, d]) < 0:
                    sign_changes += 1
                total += 1
    return float(sign_changes / total) if total > 0 else 0.0

def compute_contradiction_recovery(states: np.ndarray, target_shock: np.ndarray, shock_turn: int = 15, tol: float = 0.35) -> float:
    if len(states) <= shock_turn:
        return 1.0
    for t in range(shock_turn, len(states)):
        if np.linalg.norm(states[t] - target_shock) <= tol:
            return float(t - shock_turn + 1)
    return float(len(states) - shock_turn)

def compute_mahalanobis_containment(point: np.ndarray, mean: np.ndarray, cov: np.ndarray, chi2_val: float = 12.592) -> bool:
    diff = point - mean
    try:
        inv_cov = np.linalg.pinv(cov)
        dist_sq = float(np.dot(diff.T, np.dot(inv_cov, diff)))
        return bool(dist_sq <= chi2_val)
    except Exception:
        return False
