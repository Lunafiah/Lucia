"""
Observation Alignment Research Experiment (Phase 22-XR).
Isolates:
  H1 — Continuous Dynamics (can continuous state model track when observations are aligned?)
  H2 — Observation Alignment (can categorical probe observations be mapped to continuous latent coordinates?)
  H3 — Real Laya Contribution (held fail-closed under BLOCKED_OFFLINE_WEIGHTS)

Evaluates:
  M0: Naive Heuristic (y = 2p - 1, H = I)
  M1: Learned Linear Map (z ≈ Wp + b)
  M2: Constrained Linear Map (Log-odds transform)
  M3: Bounded Neural Calibration Layer (6 -> 24 -> 6 MLP)
  M4: Synthetic Oracle (Exact inverse of simulator coupling)
"""
from typing import Dict, List, Tuple, Any, Optional
import numpy as np
import time

from .models import (
    BaseObservationMapping,
    M0_NaiveHeuristic,
    M1_LearnedLinear,
    M2_ConstrainedLinear,
    M3_BoundedMLPCalibration,
    M4_SyntheticOracle
)

STATE_DIM = 6
PROBE_DIM = 6

def compute_r2_per_dim(y_true: np.ndarray, y_pred: np.ndarray) -> Tuple[List[float], float, float]:
    """Returns (r2_per_dim, mean_r2, median_r2)."""
    var_true = np.var(y_true, axis=0)
    mse = np.mean((y_true - y_pred)**2, axis=0)
    r2_list = []
    for m, v in zip(mse, var_true):
        if v > 1e-6:
            r2_list.append(float(1.0 - (m / v)))
        else:
            r2_list.append(1.0 if m < 1e-6 else -100.0)
    return r2_list, float(np.mean(r2_list)), float(np.median(r2_list))

def compute_correlation_per_dim(y_true: np.ndarray, y_pred: np.ndarray) -> List[float]:
    corrs = []
    for d in range(STATE_DIM):
        c = np.corrcoef(y_true[:, d], y_pred[:, d])[0, 1]
        corrs.append(float(0.0 if np.isnan(c) else c))
    return corrs

class BucyKalmanTracker:
    """Continuous Bucy-Kalman filter in R^6 coupled with an observation mapping."""
    def __init__(self, mapping: BaseObservationMapping):
        self.mapping = mapping
        self.z0 = np.array([0.0, 0.2, 0.2, 0.1, 0.5, 0.3])
        self.gamma = np.array([0.15, 0.10, 0.20, 0.25, 0.10, 0.15])
        self.Q = np.eye(STATE_DIM) * 0.05
        self.z = self.z0.copy()
        self.P = np.eye(STATE_DIM) * 0.2

    def reset(self):
        self.z = self.z0.copy()
        self.P = np.eye(STATE_DIM) * 0.2

    def step(self, probe_probs: np.ndarray, confidence: float = 0.8, dt: float = 1.0) -> Tuple[np.ndarray, np.ndarray]:
        y_obs = self.mapping.invert(probe_probs)

        # Time update (ODE drift)
        phi = np.diag(np.exp(-self.gamma * dt))
        z_prior = self.z0 + np.dot(phi, (self.z - self.z0))
        P_prior = np.dot(phi, np.dot(self.P, phi.T)) + self.Q * dt

        # Measurement update
        R = np.eye(STATE_DIM) * ((1.0 - max(min(confidence, 0.99), 0.05)) * 0.35 + 0.04)
        S = P_prior + R
        K = np.dot(P_prior, np.linalg.pinv(S))
        innov = y_obs - z_prior

        self.z = z_prior + np.dot(K, innov)
        self.P = np.dot(np.eye(STATE_DIM) - K, P_prior)

        # Bound constraints
        self.z[0:3] = np.clip(self.z[0:3], -1.0, 1.0)
        self.z[3:5] = np.clip(self.z[3:5],  0.0, 1.0)
        self.z[5]   = np.clip(self.z[5],   -1.0, 1.0)
        return self.z.copy(), self.P.copy()

def run_alignment_experiments(
    train_data: Tuple[np.ndarray, np.ndarray],
    test_episodes: List[Any],
    shift_episodes: Optional[List[Any]] = None
) -> Dict[str, Any]:
    """
    Executes comparison across M0, M1, M2, M3, M4.
    """
    p_train, z_train = train_data

    candidates: Dict[str, BaseObservationMapping] = {
        "M0": M0_NaiveHeuristic(),
        "M1": M1_LearnedLinear(),
        "M2": M2_ConstrainedLinear(),
        "M3": M3_BoundedMLPCalibration(),
        "M4": M4_SyntheticOracle()
    }

    results = {}

    for m_id, model in candidates.items():
        t_fit_start = time.perf_counter()
        model.fit(p_train, z_train)
        fit_time_ms = (time.perf_counter() - t_fit_start) * 1000.0

        # Evaluate direct mapping accuracy on held-out test data
        all_true = []
        all_direct_pred = []
        all_filtered_pred = []
        latencies_direct = []
        latencies_kalman = []

        flapping_episodes = []
        contradiction_recovery_turns = []

        tracker = BucyKalmanTracker(model)

        for ep in test_episodes:
            tracker.reset()
            ep_states = []
            for i, step in enumerate(ep.steps):
                # 1. Direct inversion
                t0 = time.perf_counter()
                z_direct = model.invert(step.probe_probs)
                latencies_direct.append((time.perf_counter() - t0) * 1000.0)

                # 2. Continuous tracking
                t1 = time.perf_counter()
                z_filt, _ = tracker.step(step.probe_probs, step.confidence, step.dt)
                latencies_kalman.append((time.perf_counter() - t1) * 1000.0)

                all_true.append(step.z_true)
                all_direct_pred.append(z_direct)
                all_filtered_pred.append(z_filt)
                ep_states.append(z_filt)

                # Contradiction check: if step has abrupt reversal
                if i > 5 and np.linalg.norm(step.z_true - ep.steps[i-1].z_true) > 1.2:
                    # Measure recovery
                    recovered = False
                    for f in range(1, 4):
                        if i + f < len(ep.steps):
                            f_step = ep.steps[i + f]
                            fz, _ = tracker.step(f_step.probe_probs, f_step.confidence, f_step.dt)
                            if np.linalg.norm(fz - f_step.z_true) < 0.4:
                                contradiction_recovery_turns.append(f)
                                recovered = True
                                break
                    if not recovered:
                        contradiction_recovery_turns.append(3.0)

            # Flapping rate across adjacent velocity reversals
            diffs = np.diff(ep_states, axis=0)
            flaps, total = 0, 0
            for k in range(len(diffs) - 1):
                for d in range(STATE_DIM):
                    if diffs[k, d] * diffs[k+1, d] < 0 and (abs(diffs[k, d]) > 0.25 or abs(diffs[k+1, d]) > 0.25):
                        flaps += 1
                    total += 1
            flapping_episodes.append(flaps / max(1, total))

        y_true_arr = np.array(all_true)
        y_direct_arr = np.array(all_direct_pred)
        y_filt_arr = np.array(all_filtered_pred)

        # Direct metrics
        r2_dims_direct, mean_r2_direct, med_r2_direct = compute_r2_per_dim(y_true_arr, y_direct_arr)
        mse_direct = float(np.mean((y_true_arr - y_direct_arr)**2))
        mae_direct = float(np.mean(np.abs(y_true_arr - y_direct_arr)))
        corr_direct = compute_correlation_per_dim(y_true_arr, y_direct_arr)

        # Filtered continuous metrics
        r2_dims_filt, mean_r2_filt, med_r2_filt = compute_r2_per_dim(y_true_arr, y_filt_arr)
        mse_filt = float(np.mean((y_true_arr - y_filt_arr)**2))
        mae_filt = float(np.mean(np.abs(y_true_arr - y_filt_arr)))

        # Evaluate performance under distribution shift if provided
        shift_mse = None
        if shift_episodes:
            shift_true, shift_pred = [], []
            for ep in shift_episodes:
                for step in ep.steps:
                    shift_true.append(step.z_true)
                    shift_pred.append(model.invert(step.probe_probs))
            shift_mse = float(np.mean((np.array(shift_true) - np.array(shift_pred))**2))

        results[m_id] = {
            "model_name": model.name,
            "parameter_count": model.parameter_count,
            "fit_time_ms": fit_time_ms,
            "direct_inversion": {
                "r2_per_dimension": [round(x, 4) for x in r2_dims_direct],
                "mean_r2": round(mean_r2_direct, 4),
                "median_r2": round(med_r2_direct, 4),
                "mse": round(mse_direct, 6),
                "mae": round(mae_direct, 6),
                "correlation_per_dim": [round(x, 4) for x in corr_direct],
                "latency_p50_ms": round(float(np.median(latencies_direct)), 5),
                "latency_p99_ms": round(float(np.percentile(latencies_direct, 99)), 5)
            },
            "continuous_filtering": {
                "r2_per_dimension": [round(x, 4) for x in r2_dims_filt],
                "mean_r2": round(mean_r2_filt, 4),
                "median_r2": round(med_r2_filt, 4),
                "mse": round(mse_filt, 6),
                "mae": round(mae_filt, 6),
                "flapping_rate": round(float(np.mean(flapping_episodes)), 4),
                "contradiction_recovery_turns": round(float(np.mean(contradiction_recovery_turns)), 2) if contradiction_recovery_turns else 1.0,
                "latency_kalman_p50_ms": round(float(np.median(latencies_kalman)), 5)
            },
            "distribution_shift_mse": round(shift_mse, 6) if shift_mse is not None else None,
            "numerical_stability": {
                "no_nan": not bool(np.isnan(y_direct_arr).any() or np.isnan(y_filt_arr).any()),
                "no_inf": not bool(np.isinf(y_direct_arr).any() or np.isinf(y_filt_arr).any())
            }
        }

    return results
