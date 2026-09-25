"""
Continuous User State Tracker for Phase 22 Observation Study.
Implements the continuous-discrete Bucy-Kalman filter in R^6
and Lyapunov-matched diffusion trajectory forecasting,
exposing psi_user in R^12.
"""
from typing import Dict, List, Optional, Tuple
import numpy as np
import time

from ..config import STATE_DIM, INTERFACE_DIM
from ..schemas import ContinuousObservationResult, UserStateUpdateResult

class ContinuousUserStateTracker:
    def __init__(self, dim: int = STATE_DIM):
        self.dim = dim
        self.z0 = np.array([0.0, 0.2, 0.2, 0.1, 0.5, 0.3], dtype=np.float64)
        self.gamma = np.array([0.15, 0.10, 0.20, 0.25, 0.10, 0.15], dtype=np.float64)
        self.z = self.z0.copy()
        self.P = np.eye(dim) * 0.2
        self.Q = np.eye(dim) * 0.05
        self.turn = 0

    def reset(self):
        self.z = self.z0.copy()
        self.P = np.eye(self.dim) * 0.2
        self.turn = 0

    def step(self, obs: ContinuousObservationResult, z_true: np.ndarray, dt: float = 1.0) -> UserStateUpdateResult:
        t0 = time.perf_counter()
        self.turn += 1
        
        # 1. Prior
        z_prior = self.z - self.gamma * (self.z - self.z0) * dt
        phi = np.diag(np.exp(-self.gamma * dt))
        P_prior = np.dot(phi, np.dot(self.P, phi.T)) + self.Q * dt
        
        # 2. Innovation
        z_obs = obs.projected_state.copy()
        R = obs.noise_covariance.copy()
        H = np.eye(self.dim)
        S = P_prior + R
        
        try:
            K = np.dot(P_prior, np.linalg.inv(S))
        except np.linalg.LinAlgError:
            K = np.dot(P_prior, np.linalg.pinv(S))
            
        innovation = z_obs - z_prior
        self.z = z_prior + np.dot(K, innovation)
        self.P = np.dot(np.eye(self.dim) - np.dot(K, H), P_prior)
        self.P = 0.5 * (self.P + self.P.T)
        
        # Clipping
        self.z[0:3] = np.clip(self.z[0:3], -1.0, 1.0)
        self.z[3:5] = np.clip(self.z[3:5],  0.0, 1.0)
        self.z[5]   = np.clip(self.z[5],   -1.0, 1.0)
        
        filter_latency = (time.perf_counter() - t0) * 1000.0
        total_latency = obs.encoder_latency_ms + obs.projection_latency_ms + filter_latency
        
        # psi_user in R^12
        psi_user = np.concatenate([self.z, np.diag(self.P)])
        is_finite = bool(np.all(np.isfinite(psi_user)))
        is_bounded = bool(np.all(psi_user[0:6] >= -1.05) and np.all(psi_user[0:6] <= 1.05))
        
        return UserStateUpdateResult(
            turn=self.turn,
            z_prior=z_prior,
            z_post=self.z.copy(),
            covariance_post=self.P.copy(),
            psi_user=psi_user,
            filter_latency_ms=filter_latency,
            total_pipeline_latency_ms=total_latency,
            innovation=innovation,
            is_finite=is_finite,
            is_bounded=is_bounded,
        )

    def forecast(self, horizon: int = 2, dt: float = 1.0) -> Tuple[List[np.ndarray], List[np.ndarray], float]:
        forecast_means = []
        forecast_covs = []
        curr_z = self.z.copy()
        curr_p = self.P.copy()
        base_log_det = float(np.linalg.slogdet(self.P)[1])
        
        for h in range(1, horizon + 1):
            curr_z = curr_z - self.gamma * (curr_z - self.z0) * dt
            phi = np.diag(np.exp(-self.gamma * dt))
            q_diff = self.Q * (1.0 + 0.5 * h) * dt
            curr_p = np.dot(phi, np.dot(curr_p, phi.T)) + q_diff
            curr_p = 0.5 * (curr_p + curr_p.T)
            forecast_means.append(curr_z.copy())
            forecast_covs.append(curr_p.copy())
            
        final_log_det = float(np.linalg.slogdet(forecast_covs[-1])[1])
        log_det_ratio = float((final_log_det - base_log_det) / (np.abs(base_log_det) + 1e-6))
        return forecast_means, forecast_covs, log_det_ratio
