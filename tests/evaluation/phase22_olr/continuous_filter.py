"""
Continuous User Dynamics Filter & Trajectory Forecaster for Phase 22-OLR.
Reuses the exact continuous Bucy-Kalman filter in R^6 supported in Phase 22-XR,
along with Lyapunov-matched diffusion forecasting.

This module is identical across all candidate observation architectures,
guaranteeing an apples-to-apples comparison of observation frontends.
"""
from typing import Dict, List, Optional, Tuple
import numpy as np
import time

from .config import STATE_DIM, P23_INTERFACE_DIM
from .schemas import FilterStepResult, TrajectoryForecastResult, ObservationOutput

Z0_DEFAULT = np.array([0.0, 0.2, 0.2, 0.1, 0.5, 0.3], dtype=np.float64)
GAMMA_DEFAULT = np.array([0.15, 0.10, 0.20, 0.25, 0.10, 0.15], dtype=np.float64)

class ContinuousUserBeliefFilterOLR:
    """
    Continuous Bucy-Kalman User Belief Filter in R^6.
    Propagates continuous latent belief z_user(t) with inertial relaxation Gamma
    and updates via observation evidence vector and covariance R.
    """
    def __init__(
        self,
        dim: int = STATE_DIM,
        z0: Optional[np.ndarray] = None,
        gamma: Optional[np.ndarray] = None,
    ):
        self.dim = dim
        self.z0 = z0 if z0 is not None else Z0_DEFAULT.copy()
        self.gamma = gamma if gamma is not None else GAMMA_DEFAULT.copy()
        
        self.z = self.z0.copy()
        self.P = np.eye(dim) * 0.2
        self.Q = np.eye(dim) * 0.05  # Continuous process noise
        self.turn = 0
        self.last_t = 0.0

    def reset(self):
        self.z = self.z0.copy()
        self.P = np.eye(self.dim) * 0.2
        self.turn = 0
        self.last_t = 0.0

    def step(self, obs: ObservationOutput, z_true: np.ndarray, dt: float = 1.0) -> FilterStepResult:
        t0 = time.perf_counter()
        self.turn += 1
        
        # 1. Continuous Prior Integration: dz = -Gamma(z - z0)*dt
        z_prior = self.z - self.gamma * (self.z - self.z0) * dt
        phi = np.diag(np.exp(-self.gamma * dt))
        P_prior = np.dot(phi, np.dot(self.P, phi.T)) + self.Q * dt
        
        # 2. Measurement Innovation
        # Observation state candidate is projected_latent_state in R^6
        z_obs = obs.projected_latent_state.copy()
        R = obs.noise_covariance.copy()
        
        # Ensure R is at least 6x6 symmetric positive definite
        if R.shape != (self.dim, self.dim):
            R = np.eye(self.dim) * ((1.0 - obs.confidence) * 0.5 + 0.05)
            
        H = np.eye(self.dim)
        S = P_prior + R
        
        try:
            K = np.dot(P_prior, np.linalg.inv(S))
        except np.linalg.LinAlgError:
            K = np.dot(P_prior, np.linalg.pinv(S))
            
        innovation = z_obs - z_prior
        self.z = z_prior + np.dot(K, innovation)
        self.P = np.dot(np.eye(self.dim) - np.dot(K, H), P_prior)
        
        # Ensure covariance symmetry and positive definiteness
        self.P = 0.5 * (self.P + self.P.T)
        min_eig = np.min(np.linalg.eigvalsh(self.P))
        if min_eig < 1e-4:
            self.P += np.eye(self.dim) * (1e-4 - min_eig)
            
        # Numerical bounds clipping
        self.z[0:3] = np.clip(self.z[0:3], -1.0, 1.0)
        self.z[3:5] = np.clip(self.z[3:5],  0.0, 1.0)
        self.z[5]   = np.clip(self.z[5],   -1.0, 1.0)
        
        filter_latency_ms = (time.perf_counter() - t0) * 1000.0
        total_latency_ms = obs.encoder_latency_ms + obs.projection_latency_ms + filter_latency_ms
        
        # Downstream P23 Interface: psi_user in R^12 = [z_mean, diag(covariance)]
        psi_user = np.concatenate([self.z, np.diag(self.P)])
        
        self.last_t += dt
        return FilterStepResult(
            turn=self.turn,
            z_prior=z_prior,
            z_post=self.z.copy(),
            covariance_post=self.P.copy(),
            psi_user=psi_user,
            z_true=z_true.copy(),
            filter_latency_ms=filter_latency_ms,
            total_pipeline_latency_ms=total_latency_ms,
            innovation=innovation,
        )

    def forecast_trajectory(self, horizon: int = 2, dt: float = 1.0) -> TrajectoryForecastResult:
        """
        Generates multi-step predictive trajectories using Lyapunov-matched diffusion.
        """
        forecast_means = []
        forecast_covs = []
        containment = []
        
        curr_z = self.z.copy()
        curr_p = self.P.copy()
        
        # Base log det for ratio
        base_log_det = float(np.linalg.slogdet(self.P)[1])
        
        for h in range(1, horizon + 1):
            curr_z = curr_z - self.gamma * (curr_z - self.z0) * dt
            phi = np.diag(np.exp(-self.gamma * dt))
            # Lyapunov matched diffusion (C2 approach from P22-XR)
            q_diff = self.Q * (1.0 + 0.5 * h) * dt
            curr_p = np.dot(phi, np.dot(curr_p, phi.T)) + q_diff
            curr_p = 0.5 * (curr_p + curr_p.T)
            
            forecast_means.append(curr_z.copy())
            forecast_covs.append(curr_p.copy())
            
        final_log_det = float(np.linalg.slogdet(forecast_covs[-1])[1])
        log_det_ratio = float((final_log_det - base_log_det) / (np.abs(base_log_det) + 1e-6))
        
        return TrajectoryForecastResult(
            horizon=horizon,
            forecast_mean=np.array(forecast_means),
            forecast_covariances=np.array(forecast_covs),
            is_contained_in_ellipsoid=containment,
            log_det_ratio=log_det_ratio,
        )
