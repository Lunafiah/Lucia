"""
Metrics and Statistical Discipline for Phase 22-XR Follow-Up.
Includes:
- Calibration: ECE, Brier, NLL
- Continuous Belief: R2, MSE, MAE
- Dynamic Stability: Flapping rate, Contradiction recovery turns
- Forecast: Mahalanobis Coverage (H=1, 2, 3), Generalized Variance (log det P), Sharpness
- Statistics: Episode-level bootstrap confidence intervals, paired differences.
"""
from typing import List, Dict, Any, Tuple
import numpy as np
from scipy import stats

def compute_ece(probs: np.ndarray, labels: np.ndarray, n_bins: int = 10) -> float:
    """Computes Expected Calibration Error over predicted top-class probabilities."""
    if len(probs) == 0:
        return 0.0
    confidences = np.max(probs, axis=1)
    predictions = np.argmax(probs, axis=1)
    accuracies = (predictions == labels).astype(float)

    bin_boundaries = np.linspace(0, 1, n_bins + 1)
    ece = 0.0
    n_samples = len(probs)

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

def compute_brier(probs: np.ndarray, labels: np.ndarray) -> float:
    """Computes multiclass Brier score."""
    if len(probs) == 0:
        return 0.0
    n_classes = probs.shape[1]
    one_hot = np.zeros_like(probs)
    for i, l in enumerate(labels):
        if 0 <= l < n_classes:
            one_hot[i, l] = 1.0
    return float(np.mean(np.sum((probs - one_hot) ** 2, axis=1)))

def compute_nll(probs: np.ndarray, labels: np.ndarray, eps: float = 1e-12) -> float:
    """Computes negative log-likelihood."""
    if len(probs) == 0:
        return 0.0
    clipped = np.clip(probs, eps, 1.0)
    log_probs = np.log(clipped)
    nll = 0.0
    for i, l in enumerate(labels):
        if 0 <= l < clipped.shape[1]:
            nll -= log_probs[i, l]
    return float(nll / len(labels))

def compute_continuous_metrics(y_true: np.ndarray, y_pred: np.ndarray) -> Dict[str, float]:
    """
    Computes R2, MSE, MAE between ground truth z* and filtered state z_hat.
    Supports multidimensional arrays (averaged across coordinates).
    """
    if len(y_true) == 0:
        return {"r2": 0.0, "mse": 0.0, "mae": 0.0}

    mse = float(np.mean((y_true - y_pred) ** 2))
    mae = float(np.mean(np.abs(y_true - y_pred)))

    # Compute variance of ground truth per dimension
    var_true = np.var(y_true, axis=0)
    mse_per_dim = np.mean((y_true - y_pred) ** 2, axis=0)
    
    # Avoid zero division
    r2_per_dim = []
    for vt, me in zip(var_true, mse_per_dim):
        if vt > 1e-8:
            r2_per_dim.append(1.0 - (me / vt))
        else:
            r2_per_dim.append(1.0 if me < 1e-8 else -100.0)
    
    r2 = float(np.mean(r2_per_dim))
    return {"r2": r2, "mse": mse, "mae": mae}

def compute_flapping_rate(states: List[np.ndarray], threshold: float = 0.25) -> float:
    """
    Computes directional flapping rate (rapid sign reversals in gradient/velocity).
    """
    if len(states) < 3:
        return 0.0
    diffs = np.diff(states, axis=0)
    flaps = 0
    total_checks = 0
    for i in range(len(diffs) - 1):
        for dim in range(diffs.shape[1]):
            d1 = diffs[i, dim]
            d2 = diffs[i+1, dim]
            if (d1 * d2 < 0) and (abs(d1) > threshold or abs(d2) > threshold):
                flaps += 1
            total_checks += 1
    return float(flaps / max(1, total_checks))

def compute_mahalanobis_coverage(
    actual: np.ndarray, mean: np.ndarray, cov: np.ndarray, quantile_target: float = 0.80
) -> bool:
    """
    Checks if actual state is within Chi-Square quantile ellipsoid of (mean, cov).
    Dim = 6 -> Chi2 df = 6. Target 0.80 -> critical val ~ 8.558.
    """
    dim = len(mean)
    diff = actual - mean
    try:
        inv_cov = np.linalg.pinv(cov)
        dist_sq = float(diff.T @ inv_cov @ diff)
    except Exception:
        return False
    critical_val = stats.chi2.ppf(quantile_target, df=dim)
    return bool(dist_sq <= critical_val)

def bootstrap_ci(
    values: List[float], n_bootstrap: int = 1000, alpha: float = 0.05
) -> Tuple[float, float, float]:
    """Computes bootstrap mean and (1-alpha) confidence interval."""
    if len(values) == 0:
        return (0.0, 0.0, 0.0)
    arr = np.array(values)
    mean_val = float(np.mean(arr))
    if len(arr) == 1:
        return (mean_val, mean_val, mean_val)
    boot_means = []
    rng = np.random.RandomState(42)
    for _ in range(n_bootstrap):
        sample = rng.choice(arr, size=len(arr), replace=True)
        boot_means.append(np.mean(sample))
    lower = float(np.percentile(boot_means, 100 * (alpha / 2)))
    upper = float(np.percentile(boot_means, 100 * (1 - alpha / 2)))
    return (mean_val, lower, upper)
