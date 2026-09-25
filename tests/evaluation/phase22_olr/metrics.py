"""
Evaluation Metrics for Phase 22-OLR.
Computes Calibration, Alignment, Temporal Stability, Trajectory Density, and Latency statistics.
"""
from typing import Dict, List, Tuple, Any
import numpy as np

def compute_ece(confidences: np.ndarray, accuracies: np.ndarray, num_bins: int = 10) -> float:
    """
    Computes Expected Calibration Error (ECE) across uniform confidence bins.
    """
    if len(confidences) == 0:
        return 0.0
    bin_boundaries = np.linspace(0.0, 1.0, num_bins + 1)
    ece = 0.0
    total_samples = len(confidences)
    
    for i in range(num_bins):
        bin_lower = bin_boundaries[i]
        bin_upper = bin_boundaries[i + 1]
        
        # In bin mask
        if i == num_bins - 1:
            in_bin = (confidences >= bin_lower) & (confidences <= bin_upper)
        else:
            in_bin = (confidences >= bin_lower) & (confidences < bin_upper)
            
        bin_count = np.sum(in_bin)
        if bin_count > 0:
            bin_acc = np.mean(accuracies[in_bin])
            bin_conf = np.mean(confidences[in_bin])
            ece += (bin_count / total_samples) * np.abs(bin_acc - bin_conf)
            
    return float(ece)

def compute_brier_score(probs: np.ndarray, one_hot_labels: np.ndarray) -> float:
    """
    Computes Brier Score: mean squared error between probabilities and one-hot targets.
    """
    return float(np.mean(np.sum((probs - one_hot_labels) ** 2, axis=-1)))

def compute_nll(probs: np.ndarray, target_indices: np.ndarray, eps: float = 1e-12) -> float:
    """
    Computes Negative Log-Likelihood (NLL).
    """
    probs_clipped = np.clip(probs, eps, 1.0)
    rows = np.arange(len(target_indices))
    correct_probs = probs_clipped[rows, target_indices]
    return float(-np.mean(np.log(correct_probs)))

def compute_r2_score(y_true: np.ndarray, y_pred: np.ndarray) -> float:
    """
    Computes multi-dimensional Coefficient of Determination (R^2).
    """
    y_true = np.asarray(y_true, dtype=np.float64)
    y_pred = np.asarray(y_pred, dtype=np.float64)
    
    ss_res = np.sum((y_true - y_pred) ** 2)
    y_mean = np.mean(y_true, axis=0)
    ss_tot = np.sum((y_true - y_mean) ** 2)
    
    if ss_tot < 1e-12:
        return 1.0 if ss_res < 1e-12 else 0.0
    return float(1.0 - (ss_res / ss_tot))

def compute_mae(y_true: np.ndarray, y_pred: np.ndarray) -> float:
    """Computes Mean Absolute Error."""
    return float(np.mean(np.abs(y_true - y_pred)))

def compute_mse(y_true: np.ndarray, y_pred: np.ndarray) -> float:
    """Computes Mean Squared Error."""
    return float(np.mean((y_true - y_pred) ** 2))

def compute_flapping_rate(states: np.ndarray) -> float:
    """
    Computes flapping rate: reversals in trajectory slope or sign across 3 consecutive turns.
    states: shape (T, D)
    """
    if len(states) < 3:
        return 0.0
    diffs = np.diff(states, axis=0)  # (T-1, D)
    sign_changes = 0
    total_checks = 0
    
    for d in range(states.shape[1]):
        for t in range(len(diffs) - 1):
            if np.abs(diffs[t, d]) > 0.05 and np.abs(diffs[t + 1, d]) > 0.05:
                if (diffs[t, d] * diffs[t + 1, d]) < 0:
                    sign_changes += 1
                total_checks += 1
                
    if total_checks == 0:
        return 0.0
    return float(sign_changes / total_checks)

def compute_contradiction_recovery(states: np.ndarray, target_shock_state: np.ndarray, shock_turn: int = 15, tolerance: float = 0.35) -> float:
    """
    Measures turns required for belief state to reach within tolerance of post-shock state.
    """
    if len(states) <= shock_turn:
        return 1.0
    for t in range(shock_turn, len(states)):
        dist = np.linalg.norm(states[t] - target_shock_state)
        if dist <= tolerance:
            return float(t - shock_turn + 1)
    return float(len(states) - shock_turn)

def compute_mahalanobis_containment(point: np.ndarray, mean: np.ndarray, cov: np.ndarray, chi2_val: float = 12.59) -> bool:
    """
    Evaluates whether point lies inside the 95% confidence ellipsoid for 6 dimensions (chi2_val=12.592).
    """
    diff = point - mean
    try:
        inv_cov = np.linalg.pinv(cov)
        dist_sq = float(np.dot(diff.T, np.dot(inv_cov, diff)))
        return bool(dist_sq <= chi2_val)
    except Exception:
        return False

def compute_percentiles(latencies: List[float]) -> Dict[str, float]:
    """Computes P50, P95, and P99 latency percentiles."""
    arr = np.asarray(latencies, dtype=np.float64)
    if len(arr) == 0:
        return {"p50": 0.0, "p95": 0.0, "p99": 0.0}
    return {
        "p50": float(np.percentile(arr, 50)),
        "p95": float(np.percentile(arr, 95)),
        "p99": float(np.percentile(arr, 99)),
    }
