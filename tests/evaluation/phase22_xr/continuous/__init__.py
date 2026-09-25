"""
Continuous User Belief, Dynamics, Filtering, and Trajectory Density Forecasting.
Formulates z_user(t) in R^6 with inertial relaxation Gamma and continuous covariance propagation.
"""
from typing import Dict, List, Tuple, Optional, Any
import numpy as np

STATE_DIM = 6
DIM_NAMES = ["load", "agency", "valence", "urgency", "receptive", "alignment"]

class ContinuousUserState:
    """Represents internal continuous user belief state."""
    def __init__(self, z: np.ndarray, P: np.ndarray, timestamp: float = 0.0):
        self.z = np.clip(z, -1.0, 1.0)
        # Urgency & receptive in [0, 1]
        self.z[3:5] = np.clip(self.z[3:5], 0.0, 1.0)
        self.P = P.copy()
        self.timestamp = timestamp

class ContinuousDynamics:
    """Continuous ODE drift dynamics: dz = -Gamma(z - z0)*dt."""
    def __init__(self, z0: Optional[np.ndarray] = None, gamma: Optional[np.ndarray] = None):
        self.z0 = z0 if z0 is not None else np.array([0.0, 0.2, 0.2, 0.1, 0.5, 0.3])
        self.gamma = gamma if gamma is not None else np.array([0.15, 0.10, 0.20, 0.25, 0.10, 0.15])
        self.Q = np.eye(STATE_DIM) * 0.04

    def step_drift(self, z: np.ndarray, dt: float = 1.0) -> np.ndarray:
        return z - self.gamma * (z - self.z0) * dt

    def propagate_covariance(self, P: np.ndarray, dt: float = 1.0) -> np.ndarray:
        phi = np.diag(np.exp(-self.gamma * dt))
        return np.dot(phi, np.dot(P, phi.T)) + self.Q * dt


class BucyKalmanFilter:
    """
    Continuous-Discrete Bucy-Kalman User Belief Filter.
    Updates continuous belief z with calibrated observation innovation.
    """
    def __init__(self, dynamics: Optional[ContinuousDynamics] = None):
        self.dynamics = dynamics or ContinuousDynamics()
        self.state = ContinuousUserState(self.dynamics.z0.copy(), np.eye(STATE_DIM) * 0.2)

    def reset(self):
        self.state = ContinuousUserState(self.dynamics.z0.copy(), np.eye(STATE_DIM) * 0.2)

    def update(self, obs_vector: np.ndarray, confidence: float, dt: float = 1.0) -> ContinuousUserState:
        # 1. Time Update (Drift)
        z_minus = self.dynamics.step_drift(self.state.z, dt)
        P_minus = self.dynamics.propagate_covariance(self.state.P, dt)
        
        # 2. Measurement Update
        H = np.eye(STATE_DIM)
        # Measurement variance R scaled by confidence
        r_val = (1.0 - max(min(confidence, 0.99), 0.05)) * 0.4 + 0.06
        R = np.eye(STATE_DIM) * r_val
        
        # Kalman Gain K = P_minus * (P_minus + R)^-1
        S = P_minus + R
        K = np.dot(P_minus, np.linalg.pinv(S))
        
        # Innovation y - z_minus
        # Scale observation probes into coordinate space
        y = obs_vector.copy()
        y[0:3] = y[0:3] * 2.0 - 1.0
        y[5]   = y[5] * 2.0 - 1.0
        # dims 3 and 4 remain in [0, 1]
        
        innovation = y - z_minus
        z_post = z_minus + np.dot(K, innovation)
        P_post = np.dot(np.eye(STATE_DIM) - np.dot(K, H), P_minus)
        
        self.state = ContinuousUserState(z_post, P_post, self.state.timestamp + dt)
        return self.state


class ContinuousTrajectoryForecaster:
    """
    Continuous prospective trajectory density forecasting.
    Replaces discrete prediction trees by propagating mean and covariance.
    """
    def __init__(self, dynamics: Optional[ContinuousDynamics] = None):
        self.dynamics = dynamics or ContinuousDynamics()

    def forecast(self, current_state: ContinuousUserState, horizon: int = 3, dt: float = 1.0) -> Dict[str, Any]:
        means = []
        covs = []
        z_curr = current_state.z.copy()
        P_curr = current_state.P.copy()
        
        for _ in range(horizon):
            z_curr = self.dynamics.step_drift(z_curr, dt)
            P_curr = self.dynamics.propagate_covariance(P_curr, dt)
            means.append(np.clip(z_curr.copy(), -1.0, 1.0))
            covs.append(P_curr.copy())
            
        return {
            "horizon": horizon,
            "means": means,
            "covariances": covs,
        }
