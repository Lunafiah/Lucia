"""
tests/evaluation_phase22/statistics/analysis.py

Preregistered statistical evaluation, hypothesis testing, and multiple comparison correction.
Adheres strictly to the probe-level aggregation principle (Unit of analysis = Probe).
"""

from __future__ import annotations

import math
from dataclasses import asdict, dataclass, field
from typing import Any, Dict, List, Optional, Sequence, Tuple

import numpy as np
import scipy.stats as stats

from tests.evaluation_phase22.models.actions import ActionType


@dataclass(frozen=True)
class StatisticalMetricResult:
    """Detailed record for a single quantitative hypothesis metric."""
    metric_name: str
    sample_unit: str             # e.g., "Probe (N=80)"
    sample_size: int
    test_used: str
    statistic_value: float
    effect_estimate: float
    ci_lower: float
    ci_upper: float
    raw_p_value: float
    corrected_p_value: float
    target_met: bool
    notes: str = ""


@dataclass(frozen=True)
class GLMMApproximationResult:
    """
    Research mixed-effects logistic regression approximation for repeated binary outcomes.
    Explicitly labeled as research approximation; NOT equivalent to a full standard GLMM.
    """
    is_research_approximation: bool = True
    beta_0: float = 0.0
    beta_cond: float = 0.0
    sigma_probe: float = 0.0
    p_value_approx: float = 0.0
    odds_ratio: float = 1.0
    limitation_note: str = (
        "Research approximation (probe random intercepts via empirical Bayes / bounded numerical fit). "
        "statsmodels is not installed in runtime; this metric must NOT be claimed as standard GLMM."
    )


def holm_bonferroni_correction(p_values: Sequence[float]) -> List[float]:
    """
    Holm-Bonferroni step-down family-wise error rate control.
    p_(k) adjusted = min(1.0, max_{j <= k} (m - j + 1) * p_(j))
    """
    m = len(p_values)
    if m == 0:
        return []

    # Indexed sorting by ascending p-value
    sorted_indices = sorted(range(m), key=lambda i: p_values[i])
    adjusted = [0.0] * m

    cum_max = 0.0
    for rank, idx in enumerate(sorted_indices):
        j = rank + 1
        raw_p = max(0.0, min(1.0, float(p_values[idx])))
        candidate = (m - j + 1) * raw_p
        cum_max = max(cum_max, candidate)
        adjusted[idx] = min(1.0, cum_max)

    return adjusted


def compute_wilcoxon_paired(
    values_a: Sequence[float],
    values_b: Sequence[float],
) -> Tuple[float, float, float, Tuple[float, float]]:
    """
    Two-sided Wilcoxon signed-rank test on matched probe-level values.
    Returns:
      (statistic, p_value, median_difference, (ci_95_low, ci_95_high))
    """
    a = np.asarray(values_a, dtype=np.float64)
    b = np.asarray(values_b, dtype=np.float64)
    diff = a - b

    # If all differences are zero
    if np.all(np.abs(diff) < 1e-12):
        return 0.0, 1.0, 0.0, (0.0, 0.0)

    res = stats.wilcoxon(diff, alternative="two-sided")
    stat = float(res.statistic)
    p_val = float(res.pvalue)

    med_diff = float(np.median(diff))

    # Bootstrap 95% CI on median difference
    rng = np.random.default_rng(42)
    boot_diffs = []
    for _ in range(1000):
        sample = rng.choice(diff, size=len(diff), replace=True)
        boot_diffs.append(np.median(sample))
    ci_low = float(np.percentile(boot_diffs, 2.5))
    ci_high = float(np.percentile(boot_diffs, 97.5))

    return stat, p_val, med_diff, (ci_low, ci_high)


def evaluate_h1_surprise_decoupling(
    surprises: Sequence[float],
    u_sems: Sequence[float],
) -> Tuple[float, float, float, float]:
    """
    H1: Surprise / Uncertainty Decoupling.
    Measures R^2 between physiological surprise S_t and semantic uncertainty U_sem.
    Returns:
      (r_squared, p_value, pearson_r, ffr_target_met)
    """
    s = np.asarray(surprises, dtype=np.float64)
    u = np.asarray(u_sems, dtype=np.float64)

    if len(s) < 3 or np.std(s) < 1e-9 or np.std(u) < 1e-9:
        return 0.0, 1.0, 0.0, False

    r, p = stats.pearsonr(s, u)
    r2 = float(r ** 2)
    return r2, float(p), float(r), bool(r2 < 0.15)


def fit_research_glmm_approximation(
    y_binary: Sequence[int],
    cond_binary: Sequence[int],
    probe_indices: Sequence[int],
) -> GLMMApproximationResult:
    """
    Isolated research approximation for repeated binary action outcomes with probe random intercepts.
    Documented as an experimental approximation; NOT standard GLMM.
    """
    y = np.asarray(y_binary, dtype=np.float64)
    x = np.asarray(cond_binary, dtype=np.float64)
    probes = np.asarray(probe_indices, dtype=np.int64)

    # Estimate between-probe variance
    unique_probes = np.unique(probes)
    probe_rates = []
    for p in unique_probes:
        idx = np.where(probes == p)[0]
        probe_rates.append(np.mean(y[idx]))

    var_p = float(np.var(probe_rates)) if len(probe_rates) > 1 else 0.0
    sigma_p = math.sqrt(max(1e-6, var_p))

    # Fit simple logistic log-odds difference with probe adjustment
    p1 = max(1e-4, min(1.0 - 1e-4, float(np.mean(y[x == 1])))) if np.any(x == 1) else 0.5
    p0 = max(1e-4, min(1.0 - 1e-4, float(np.mean(y[x == 0])))) if np.any(x == 0) else 0.5

    logit1 = math.log(p1 / (1.0 - p1))
    logit0 = math.log(p0 / (1.0 - p0))
    beta_cond = logit1 - logit0
    beta_0 = logit0

    # Approximate Wald p-value adjusted for cluster design effect
    n1 = np.sum(x == 1)
    n0 = np.sum(x == 0)
    se = math.sqrt((1.0 / (n1 * p1 * (1.0 - p1))) + (1.0 / (n0 * p0 * (1.0 - p0))) + var_p)
    z = beta_cond / max(1e-6, se)
    p_approx = float(2.0 * (1.0 - stats.norm.cdf(abs(z))))

    return GLMMApproximationResult(
        is_research_approximation=True,
        beta_0=float(beta_0),
        beta_cond=float(beta_cond),
        sigma_probe=float(sigma_p),
        p_value_approx=float(p_approx),
        odds_ratio=float(math.exp(beta_cond)),
    )
