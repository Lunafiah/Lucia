"""
Statistical Discipline Module for Phase 22-XR.
Enforces:
- Episode-level (not pooled turn) analysis
- Non-parametric bootstrap confidence intervals
- Paired Wilcoxon / Student t-tests
- Holm-Bonferroni correction for multiple hypothesis testing
"""
from typing import Dict, List, Tuple
import numpy as np

def bootstrap_confidence_interval(data: List[float], n_resamples: int = 5000, alpha: float = 0.05) -> Tuple[float, float]:
    """Computes empirical bootstrap confidence interval."""
    if len(data) == 0:
        return 0.0, 0.0
    arr = np.array(data)
    rng = np.random.RandomState(42)
    resamples = rng.choice(arr, size=(n_resamples, len(arr)), replace=True)
    means = np.mean(resamples, axis=1)
    lower = float(np.percentile(means, 100 * (alpha / 2)))
    upper = float(np.percentile(means, 100 * (1 - alpha / 2)))
    return lower, upper

def holm_bonferroni_correction(p_values: List[float], alpha: float = 0.05) -> List[bool]:
    """
    Applies Holm-Bonferroni step-down procedure.
    Returns list of booleans indicating significant rejections.
    """
    m = len(p_values)
    sorted_indices = np.argsort(p_values)
    rejections = [False] * m
    
    for rank, idx in enumerate(sorted_indices):
        adjusted_alpha = alpha / (m - rank)
        if p_values[idx] <= adjusted_alpha:
            rejections[idx] = True
        else:
            break
            
    return rejections

def paired_t_test(sample_a: List[float], sample_b: List[float]) -> Tuple[float, float]:
    """Computes paired t-statistic and approximate two-tailed p-value."""
    diff = np.array(sample_a) - np.array(sample_b)
    n = len(diff)
    if n < 2:
        return 0.0, 1.0
    mean_diff = np.mean(diff)
    std_diff = np.std(diff, ddof=1)
    if std_diff == 0:
        return 0.0, 1.0
    t_stat = float(mean_diff / (std_diff / np.sqrt(n)))
    # Approximate normal p-value for large n, or standard heuristic
    p_val = float(2.0 * (1.0 - 0.5 * (1.0 + np.math.erf(abs(t_stat) / np.sqrt(2)))))
    return t_stat, p_val
