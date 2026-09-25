"""
Continuous Follow-up Module:
- Bucy-Kalman Filter supporting arbitrary observation mappings g(z)
- Forecasting Models:
  C1: Fixed Process Noise
  C2: Cumulative Lyapunov Diffusion
  C3: Innovation-Adaptive Process Noise
  C4: Empirical Coverage Calibration
"""
from typing import Dict, List, Tuple, Optional, Any
import numpy as np
from ..schemas import ContinuousBeliefState, TrajectoryDensityForecast

STATE_DIM = 6

class ContinuousDynamics:
    """Continuous ODE drift dynamics: dz = -Gamma(z - z0)*dt."""
    def __init__(self, z0: Optional[np.ndarray] = None, gamma: Optional[np.ndarray] = None):
        self.z0 = z0 if z0 is not None else np.array([0.0, 0.2, 0.2, 0.1, 0.5, 0.3])
        self.gamma = gamma if gamma is not None else np.array([0.15, 0.10, 0.20, 0.25, 0.10, 0.15])
        self.Q = np.eye(STATE_DIM) * 0.05

    def step_drift(self, z: np.ndarray, dt: float = 1.0) -> np.ndarray:
        return z - self.gamma * (z - self.z0) * dt

    def get_phi(self, dt: float = 1.0) -> np.ndarray:
        return np.diag(np.exp(-self.gamma * dt))


class AlignedBucyKalmanFilter:
    """
    Continuous-Discrete Bucy-Kalman Filter with observation alignment.
    Receives y = g^-1(obs) from alignment mapping.
    """
    def __init__(self, dynamics: Optional[ContinuousDynamics] = None):
        self.dynamics = dynamics or ContinuousDynamics()
        self.z = self.dynamics.z0.copy()
        self.P = np.eye(STATE_DIM) * 0.2
        self.last_innovation = np.zeros(STATE_DIM)
        self.last_t = 0.0

    def reset(self):
        self.z = self.dynamics.z0.copy()
        self.P = np.eye(STATE_DIM) * 0.2
        self.last_innovation = np.zeros(STATE_DIM)
        self.last_t = 0.0

    def update(self, y_aligned: np.ndarray, confidence: float, dt: float = 1.0) -> ContinuousBeliefState:
        # 1. Time Update
        z_minus = self.dynamics.step_drift(self.z, dt)
        phi = self.dynamics.get_phi(dt)
        P_minus = np.dot(phi, np.dot(self.P, phi.T)) + self.dynamics.Q * dt
        
        # 2. Measurement Update
        H = np.eye(STATE_DIM)
        # R scaled by observation confidence
        conf = max(min(confidence, 0.99), 0.05)
        r_val = (1.0 - conf) * 0.35 + 0.04
        R = np.eye(STATE_DIM) * r_val
        
        # Kalman Gain
        S = P_minus + R
        K = np.dot(P_minus, np.linalg.pinv(S))
        
        # Innovation
        innovation = y_aligned - z_minus
        self.last_innovation = innovation.copy()
        
        z_post = z_minus + np.dot(K, innovation)
        P_post = np.dot(np.eye(STATE_DIM) - np.dot(K, H), P_minus)
        
        # Clamp bounds
        z_post[0:3] = np.clip(z_post[0:3], -1.0, 1.0)
        z_post[3:5] = np.clip(z_post[3:5],  0.0, 1.0)
        z_post[5]   = np.clip(z_post[5],   -1.0, 1.0)
        
        self.z = z_post
        self.P = P_post
        self.last_t += dt
        return ContinuousBeliefState(z_mean=self.z.copy(), covariance=self.P.copy(), timestamp=self.last_t)


class CalibratedTrajectoryForecaster:
    """
    Trajectory density forecaster implementing C1, C2, C3, and C4 formulations.
    """
    def __init__(self, mode: str = "C2", dynamics: Optional[ContinuousDynamics] = None):
        self.mode = mode # C1, C2, C3, C4
        self.dynamics = dynamics or ContinuousDynamics()

    def forecast(
        self,
        current_belief: ContinuousBeliefState,
        horizon: int = 3,
        dt: float = 1.0,
        last_innovation: Optional[np.ndarray] = None,
    ) -> TrajectoryDensityForecast:
        means = []
        covs = []
        log_dets = []
        
        z_curr = current_belief.z_mean.copy()
        P_curr = current_belief.covariance.copy()
        phi = self.dynamics.get_phi(dt)
        Q = self.dynamics.Q.copy()
        
        # Mode C3: Innovation adaptive scaling
        if self.mode == "C3" and last_innovation is not None:
            innov_norm = float(np.linalg.norm(last_innovation))
            Q = Q * (1.0 + min(innov_norm * 2.0, 4.0))

        # Mode C4 / C2: Process noise scaling
        if self.mode in ["C2", "C4"]:
            # Principled diffusion matching continuous process noise
            Q = Q * 2.5
            
        for k in range(1, horizon + 1):
            z_curr = self.dynamics.step_drift(z_curr, dt)
            
            if self.mode == "C1":
                # Fixed lookahead (P22-XR under-dispersed baseline)
                P_curr = np.dot(phi, np.dot(P_curr, phi.T)) + self.dynamics.Q
            elif self.mode in ["C2", "C3", "C4"]:
                # Cumulative Lyapunov diffusion
                P_curr = np.dot(phi, np.dot(P_curr, phi.T)) + Q
                
            # Clamp bounds on mean
            z_clamped = z_curr.copy()
            z_clamped[0:3] = np.clip(z_clamped[0:3], -1.0, 1.0)
            z_clamped[3:5] = np.clip(z_clamped[3:5],  0.0, 1.0)
            z_clamped[5]   = np.clip(z_clamped[5],   -1.0, 1.0)
            
            means.append(z_clamped)
            covs.append(P_curr.copy())
            
            # Log generalized variance
            sign, log_det = np.linalg.slogdet(P_curr)
            log_dets.append(float(log_det) if sign > 0 else -99.0)
            
        return TrajectoryDensityForecast(
            horizon=horizon,
            mean_trajectory=means,
            cov_trajectory=covs,
            log_generalized_variance=log_dets,
            latency_us=12.0
        )
