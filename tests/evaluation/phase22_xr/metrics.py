"""
Metrics and Statistical Utilities for Phase 22-XR.
"""
from typing import Dict, List, Tuple
import numpy as np

def compute_ece(probs: np.ndarray, labels: np.ndarray, n_bins: int = 15) -> float:
    """Expected Calibration Error with uniform binning."""
    if len(probs) == 0:
        return 0.0
    confidences = np.max(probs, axis=1)
    predictions = np.argmax(probs, axis=1)
    accuracies = (predictions == labels).astype(np.float64)
    
    bin_boundaries = np.linspace(0, 1, n_bins + 1)
    ece = 0.0
    for i in range(n_bins):
        bin_lower = bin_boundaries[i]
        bin_upper = bin_boundaries[i + 1]
        in_bin = (confidences > bin_lower) & (confidences <= bin_upper)
        prop_in_bin = np.mean(in_bin)
        if prop_in_bin > 0:
            accuracy_in_bin = np.mean(accuracies[in_bin])
            avg_confidence_in_bin = np.mean(confidences[in_bin])
            ece += np.abs(avg_confidence_in_bin - accuracy_in_bin) * prop_in_bin
    return float(ece)

def compute_brier_score(probs: np.ndarray, labels: np.ndarray) -> float:
    """Multi-class Brier score."""
    n_samples, n_classes = probs.shape
    one_hot = np.zeros((n_samples, n_classes))
    for i, l in enumerate(labels):
        one_hot[i, l] = 1.0
    return float(np.mean(np.sum((probs - one_hot) ** 2, axis=1)))

def compute_nll(probs: np.ndarray, labels: np.ndarray) -> float:
    """Negative log likelihood."""
    eps = 1e-12
    nlls = []
    for i, l in enumerate(labels):
        nlls.append(-np.log(probs[i, l] + eps))
    return float(np.mean(nlls))

def compute_r2_score(y_true: np.ndarray, y_pred: np.ndarray) -> float:
    """Coefficient of determination R^2."""
    ss_res = np.sum((y_true - y_pred) ** 2)
    ss_tot = np.sum((y_true - np.mean(y_true, axis=0)) ** 2)
    if ss_tot == 0:
        return 1.0
    return float(1.0 - (ss_res / ss_tot))

def compute_flapping_rate(states: List[int]) -> float:
    """Proportion of adjacent turns alternating state (s_A -> s_B -> s_A)."""
    if len(states) < 3:
        return 0.0
    flaps = 0
    for i in range(len(states) - 2):
        if states[i] == states[i+2] and states[i] != states[i+1]:
            flaps += 1
    return float(flaps / (len(states) - 2))

def compute_ellipsoid_coverage(y_true: np.ndarray, mean_pred: np.ndarray, cov_pred: np.ndarray, quantile: float = 0.90) -> bool:
    """Check if y_true falls within the confidence ellipsoid."""
    diff = y_true - mean_pred
    inv_cov = np.linalg.pinv(cov_pred)
    mahalanobis_dist = float(np.dot(diff, np.dot(inv_cov, diff)))
    # Chi-square critical value for 6 degrees of freedom at 0.90 is 10.64
    chi2_val_90 = 10.64
    return mahalanobis_dist <= chi2_val_90

def bootstrap_ci(data: List[float], n_bootstrap: int = 2000, alpha: float = 0.05) -> Tuple[float, float]:
    """Non-parametric bootstrap confidence interval."""
    if len(data) == 0:
        return 0.0, 0.0
    arr = np.array(data)
    boot_means = []
    rng = np.random.RandomState(42)
    for _ in range(n_bootstrap):
        sample = rng.choice(arr, size=len(arr), replace=True)
        boot_means.append(np.mean(sample))
    lower = float(np.percentile(boot_means, 100 * (alpha / 2)))
    upper = float(np.percentile(boot_means, 100 * (1 - alpha / 2)))
    return lower, upper
