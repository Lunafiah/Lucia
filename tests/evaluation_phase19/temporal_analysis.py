"""
Quantitative Analysis and Curve Fitting Routines for Phase 19.

Provides mathematical evaluation tools:
    - Biexponential vs Monoexponential least-squares fitting
    - Akaike Information Criterion (AIC) computation
    - Effective relaxation half-life calculation
    - Hysteresis path-divergence quantification
    - Phase-space Jacobian divergence & Lyapunov contraction checking
"""

from __future__ import annotations

from typing import Dict, List, Optional, Tuple

import numpy as np
from scipy.optimize import curve_fit


def mono_exp(t: np.ndarray, a: float, tau: float, c: float) -> np.ndarray:
    return a * np.exp(-t / np.maximum(tau, 1e-4)) + c


def bi_exp(t: np.ndarray, a1: float, tau1: float, a2: float, tau2: float, c: float) -> np.ndarray:
    t1 = np.maximum(tau1, 1e-4)
    t2 = np.maximum(tau2, 1e-4)
    return a1 * np.exp(-t / t1) + a2 * np.exp(-t / t2) + c


def compute_aic(n: int, rss: float, k: int) -> float:
    """Akaike Information Criterion with small-sample correction (AICc)."""
    if rss <= 0.0 or n <= k + 1:
        return 1e9
    return n * np.log(rss / n) + 2 * k + (2 * k * (k + 1)) / (n - k - 1)


def fit_relaxation_curves(times: np.ndarray, values: np.ndarray) -> Dict[str, any]:
    """
    Fits both monoexponential and biexponential decay curves to a time series.
    Returns estimated time constants, R^2, and AIC comparison.
    """
    n = len(times)
    t = np.array(times, dtype=np.float64) - times[0]
    y = np.array(values, dtype=np.float64)

    y_span = y[0] - y[-1]
    y_inf = y[-1]

    # --- Monoexponential Fit ---
    mono_p0 = [y_span, max(1.0, t[-1] / 5.0), y_inf]
    mono_bounds = ([-2.0, 0.01, -1.0], [2.0, max(1000.0, t[-1] * 5.0), 1.0])
    try:
        popt_mono, _ = curve_fit(mono_exp, t, y, p0=mono_p0, bounds=mono_bounds, maxfev=5000)
        y_pred_mono = mono_exp(t, *popt_mono)
        rss_mono = float(np.sum((y - y_pred_mono) ** 2))
        ss_tot = float(np.sum((y - np.mean(y)) ** 2))
        r2_mono = 1.0 - (rss_mono / max(ss_tot, 1e-9))
        aic_mono = compute_aic(n, rss_mono, k=3)
        tau_mono = float(popt_mono[1])
    except Exception:
        aic_mono = 1e9
        r2_mono = 0.0
        tau_mono = 0.0

    # --- Biexponential Fit ---
    bi_p0 = [y_span * 0.6, 1.0, y_span * 0.4, 60.0, y_inf]
    bi_bounds = ([-2.0, 0.01, -2.0, 5.0, -1.0], [2.0, 20.0, 2.0, 1000.0, 1.0])
    try:
        popt_bi, _ = curve_fit(bi_exp, t, y, p0=bi_p0, bounds=bi_bounds, maxfev=10000)
        y_pred_bi = bi_exp(t, *popt_bi)
        rss_bi = float(np.sum((y - y_pred_bi) ** 2))
        ss_tot = float(np.sum((y - np.mean(y)) ** 2))
        r2_bi = 1.0 - (rss_bi / max(ss_tot, 1e-9))
        aic_bi = compute_aic(n, rss_bi, k=5)
        tau1 = float(min(popt_bi[1], popt_bi[3]))
        tau2 = float(max(popt_bi[1], popt_bi[3]))
    except Exception:
        aic_bi = 1e9
        r2_bi = 0.0
        tau1, tau2 = 0.0, 0.0

    delta_aic = aic_mono - aic_bi  # Positive indicates biexponential is superior

    return {
        "n_samples": n,
        "tau_mono": tau_mono,
        "r2_mono": max(0.0, r2_mono),
        "aic_mono": aic_mono,
        "tau_fast": tau1,
        "tau_slow": tau2,
        "r2_bi": max(0.0, r2_bi),
        "aic_bi": aic_bi,
        "delta_aic": delta_aic,
        "tau_ratio": (tau2 / tau1) if tau1 > 0 else 0.0,
        "biexponential_preferred": (delta_aic >= 10.0 and r2_bi > r2_mono),
    }


def compute_half_life(times: np.ndarray, values: np.ndarray) -> float:
    """Computes empirical half-life t_1/2 where value crosses 50% of the initial deviation."""
    t = np.array(times, dtype=np.float64)
    y = np.array(values, dtype=np.float64)
    v_start = y[0]
    v_end = y[-1]
    target = v_start - 0.5 * (v_start - v_end)

    for i in range(len(y) - 1):
        if (y[i] - target) * (y[i + 1] - target) <= 0:
            # Linear interpolation
            dt = t[i + 1] - t[i]
            dy = y[i + 1] - y[i]
            frac = (target - y[i]) / dy if abs(dy) > 1e-9 else 0.0
            return float(t[i] + frac * dt - t[0])
    return float(t[-1] - t[0])


def compute_hysteresis_metrics(pad_a_series: List[np.ndarray], pad_b_series: List[np.ndarray]) -> Dict[str, float]:
    """Computes point-by-point Euclidean divergence between two trajectories."""
    min_len = min(len(pad_a_series), len(pad_b_series))
    diffs = [
        float(np.linalg.norm(pad_a_series[i] - pad_b_series[i]))
        for i in range(min_len)
    ]
    return {
        "max_divergence": float(max(diffs)) if diffs else 0.0,
        "mean_divergence": float(np.mean(diffs)) if diffs else 0.0,
        "final_divergence": float(diffs[-1]) if diffs else 0.0,
    }


def evaluate_jacobian_divergence(
    model: any,
    h_fast: np.ndarray,
    s_slow: np.ndarray,
    eps: float = 1e-5,
) -> float:
    """
    Computes numerical trace of the coupled Jacobian matrix Tr(J) = div(F).
    Negative divergence guarantees dissipative contraction and absence of explosive limit cycles.
    """
    Hf = len(h_fast)
    Hs = len(s_slow)
    zero_x = np.zeros(model._config.stimulus_dim)
    m_homeo = model._m_homeo

    # Base derivative
    dh0, ds0 = model._ode_step(h_fast, s_slow, zero_x, m_homeo, dt=0.01)
    f0 = np.concatenate([(dh0 - h_fast) / 0.01, (ds0 - s_slow) / 0.01])

    trace = 0.0

    # Perturb h_fast coordinates
    for i in range(Hf):
        h_pert = h_fast.copy()
        h_pert[i] += eps
        dh_pert, ds_pert = model._ode_step(h_pert, s_slow, zero_x, m_homeo, dt=0.01)
        f_pert = np.concatenate([(dh_pert - h_pert) / 0.01, (ds_pert - s_slow) / 0.01])
        trace += (f_pert[i] - f0[i]) / eps

    # Perturb s_slow coordinates
    for j in range(Hs):
        s_pert = s_slow.copy()
        s_pert[j] += eps
        dh_pert, ds_pert = model._ode_step(h_fast, s_pert, zero_x, m_homeo, dt=0.01)
        f_pert = np.concatenate([(dh_pert - h_fast) / 0.01, (ds_pert - s_pert) / 0.01])
        trace += (f_pert[Hf + j] - f0[Hf + j]) / eps

    return float(trace)
