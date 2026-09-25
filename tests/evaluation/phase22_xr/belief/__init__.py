"""
Belief Filter Modules:
1. DiscreteBayesFilter: 5-state categorical simplex filter from Phase 22-X (flapping failure mode).
2. ContinuousUserBeliefFilter: Continuous Bucy-Kalman / Neural ODE filter in R^6 (Phase 22-XR proposal).
"""
from typing import Dict, List, Optional, Tuple
import numpy as np
import time
from ..schemas import ContinuousBeliefState, DiscreteBeliefState, ObservationResult
from ..config import STATE_DIM

class DiscreteBayesFilter:
    """
    Categorical Bayesian Belief Filter (replicates P22-X baseline).
    Updates a discrete distribution over 5 latent states: b_t in Delta^4.
    Computes argmax state which suffers from boundary flapping.
    """
    def __init__(self, num_states: int = 5):
        self.num_states = num_states
        self.b = np.ones(num_states) / num_states
        # Stationary 1st-order transition matrix T*
        self.T = np.array([
            [0.75, 0.10, 0.05, 0.05, 0.05],
            [0.15, 0.70, 0.05, 0.05, 0.05],
            [0.10, 0.05, 0.70, 0.05, 0.10],
            [0.05, 0.10, 0.05, 0.75, 0.05],
            [0.20, 0.20, 0.20, 0.10, 0.30],
        ], dtype=np.float64)

    def reset(self):
        self.b = np.ones(self.num_states) / self.num_states

    def update(self, obs_probs: np.ndarray) -> DiscreteBeliefState:
        # Time predict: b_minus = b * T
        b_minus = np.dot(self.b, self.T)
        # Likelihood mapping from 6 probes to 5 states
        likelihood = np.ones(self.num_states)
        likelihood[0] = obs_probs[0] * 0.8 + 0.1 # FOCUSED
        likelihood[1] = obs_probs[1] * 0.8 + 0.1 # EXPLORATORY
        likelihood[2] = obs_probs[0] * 0.9 + 0.1 # OVERLOAD
        likelihood[3] = obs_probs[2] * 0.8 + 0.1 # AFFECTIVE
        likelihood[4] = 0.3                      # AMBIGUOUS
        
        # Bayes update
        unnorm = b_minus * likelihood
        self.b = unnorm / (np.sum(unnorm) + 1e-12)
        dominant_idx = int(np.argmax(self.b))
        return DiscreteBeliefState(b_simplex=self.b.copy(), dominant_state_idx=dominant_idx)


class ContinuousUserBeliefFilter:
    """
    Continuous Bucy-Kalman / Neural ODE User Belief Filter in R^6.
    Propagates continuous latent belief z_user(t) with inertial relaxation Gamma
    and measurement innovation from calibrated observation probabilities.
    """
    def __init__(
        self,
        dim: int = STATE_DIM,
        z0: Optional[np.ndarray] = None,
        gamma: Optional[np.ndarray] = None,
    ):
        self.dim = dim
        self.z0 = z0 if z0 is not None else np.array([0.0, 0.2, 0.2, 0.1, 0.5, 0.3])
        self.gamma = gamma if gamma is not None else np.array([0.15, 0.10, 0.20, 0.25, 0.10, 0.15])
        
        # State mean and covariance
        self.z = self.z0.copy()
        self.P = np.eye(dim) * 0.2
        self.Q = np.eye(dim) * 0.05  # process noise
        self.last_t = 0.0

    def reset(self):
        self.z = self.z0.copy()
        self.P = np.eye(self.dim) * 0.2
        self.last_t = 0.0

    def update(self, obs_result: ObservationResult, dt: float = 1.0) -> ContinuousBeliefState:
        # 1. Continuous Time Drift (ODE Integration): dz = -Gamma(z - z0)*dt
        z_minus = self.z - self.gamma * (self.z - self.z0) * dt
        # Covariance propagation: P_minus = Phi * P * Phi^T + Q
        phi = np.diag(np.exp(-self.gamma * dt))
        P_minus = np.dot(phi, np.dot(self.P, phi.T)) + self.Q * dt
        
        # 2. Measurement Innovation
        # Measurement matrix H = I (probes directly observe 6 latent dimensions)
        H = np.eye(self.dim)
        # Measurement covariance R derived from observation confidence
        # Lower confidence = higher measurement variance
        conf = max(min(obs_result.confidence, 0.99), 0.05)
        r_scalar = (1.0 - conf) * 0.5 + 0.05
        R = np.eye(self.dim) * r_scalar
        
        # Kalman Gain: K = P_minus * H^T * (H * P_minus * H^T + R)^-1
        S = P_minus + R
        K = np.dot(P_minus, np.linalg.inv(S))
        
        # Observed vector mapped to [-1, 1]
        y = obs_result.probabilities * 2.0 - 1.0
        # For urgency and receptive, range is [0, 1]
        y[3:5] = obs_result.probabilities[3:5]
        
        # State update
        innovation = y - z_minus
        self.z = z_minus + np.dot(K, innovation)
        self.P = np.dot(np.eye(self.dim) - np.dot(K, H), P_minus)
        
        # Numerical bounds clipping
        self.z[0:3] = np.clip(self.z[0:3], -1.0, 1.0)
        self.z[3:5] = np.clip(self.z[3:5],  0.0, 1.0)
        self.z[5]   = np.clip(self.z[5],   -1.0, 1.0)
        
        self.last_t += dt
        return ContinuousBeliefState(z_mean=self.z.copy(), covariance=self.P.copy(), timestamp=self.last_t)
