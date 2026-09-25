"""
Observation Forward Models for Problem R1 (Observation Alignment):
M1: Direct Affine (calibrated baseline)
M2: Softmax-Linear Observation Model (fitted strictly on D_cal)
M3: Nonlinear MLP Inversion Map (fitted on D_cal)
M4: Log-Odds Dirichlet Transformation
"""
from typing import Dict, List, Tuple, Optional
import numpy as np

class BaseObservationMapping:
    def map_observation(self, obs_probabilities: np.ndarray) -> np.ndarray:
        raise NotImplementedError

class M1_DirectAffine(BaseObservationMapping):
    """M1: Direct Affine mapping with recentering."""
    def map_observation(self, obs_probabilities: np.ndarray) -> np.ndarray:
        y = obs_probabilities.copy() * 2.0 - 1.0
        # dims 3 and 4 in [0, 1]
        y[3:5] = obs_probabilities[3:5]
        return y

class M2_SoftmaxLinearMapping(BaseObservationMapping):
    """
    M2: Aligned Generative Observation Model.
    g(z) = softmax((W_obs * z + b_obs) / T).
    Parameters W_obs and b_obs are fitted strictly on calibration split D_cal (seed 9999).
    Computes linear pseudo-inverse inversion y_align = W_pinv * (logits - b).
    """
    def __init__(self, state_dim: int = 6, num_probes: int = 6):
        self.state_dim = state_dim
        self.num_probes = num_probes
        self.W_obs = np.eye(state_dim)
        self.b_obs = np.zeros(state_dim)
        self.W_pinv = np.eye(state_dim)
        self.is_fitted = False

    def fit_on_calibration_data(self, z_cal_list: List[np.ndarray], p_cal_list: List[np.ndarray]):
        """Fit forward weights using ordinary least squares on log-odds of calibration probes."""
        Z = np.array(z_cal_list) # [N, 6]
        P = np.array(p_cal_list) # [N, 6]
        # Log-odds of probes
        P_clamped = np.clip(P, 1e-6, 1.0 - 1e-6)
        Logit_P = np.log(P_clamped / (1.0 - P_clamped))
        
        # Add bias column: Z_ext = [Z, 1]
        Z_ext = np.hstack([Z, np.ones((len(Z), 1))])
        # W_ext = (Z_ext^T * Z_ext)^-1 * Z_ext^T * Logit_P
        W_ext, _, _, _ = np.linalg.lstsq(Z_ext, Logit_P, rcond=None)
        
        self.W_obs = W_ext[:-1, :].T # [6, 6]
        self.b_obs = W_ext[-1, :]    # [6]
        self.W_pinv = np.linalg.pinv(self.W_obs)
        self.is_fitted = True

    def map_observation(self, obs_probabilities: np.ndarray) -> np.ndarray:
        if not self.is_fitted:
            # Fallback to direct affine if not fitted
            return obs_probabilities * 2.0 - 1.0
        # Invert from probe logit space back to latent space z
        p_clamped = np.clip(obs_probabilities, 1e-6, 1.0 - 1e-6)
        logit_p = np.log(p_clamped / (1.0 - p_clamped))
        z_inferred = np.dot(self.W_pinv, (logit_p - self.b_obs))
        # Clamp to state bounds
        z_inferred[0:3] = np.clip(z_inferred[0:3], -1.0, 1.0)
        z_inferred[3:5] = np.clip(z_inferred[3:5],  0.0, 1.0)
        z_inferred[5]   = np.clip(z_inferred[5],   -1.0, 1.0)
        return z_inferred

class M3_MLPInverseMapping(BaseObservationMapping):
    """M3: 2-layer MLP inverse mapping fitted on calibration data."""
    def __init__(self, hidden_dim: int = 24):
        self.w1 = np.zeros((6, hidden_dim))
        self.b1 = np.zeros(hidden_dim)
        self.w2 = np.zeros((hidden_dim, 6))
        self.b2 = np.zeros(6)
        self.is_fitted = False

    def fit_on_calibration_data(self, z_cal_list: List[np.ndarray], p_cal_list: List[np.ndarray]):
        P = np.array(p_cal_list)
        Z = np.array(z_cal_list)
        rng = np.random.RandomState(9999)
        self.w1 = rng.normal(0, 0.1, (6, 24))
        self.b1 = np.zeros(24)
        # Solve output linear layer
        H = np.maximum(0, np.dot(P, self.w1) + self.b1)
        H_ext = np.hstack([H, np.ones((len(H), 1))])
        W_ext, _, _, _ = np.linalg.lstsq(H_ext, Z, rcond=None)
        self.w2 = W_ext[:-1, :]
        self.b2 = W_ext[-1, :]
        self.is_fitted = True

    def map_observation(self, obs_probabilities: np.ndarray) -> np.ndarray:
        if not self.is_fitted:
            return obs_probabilities * 2.0 - 1.0
        h = np.maximum(0, np.dot(obs_probabilities, self.w1) + self.b1)
        z_pred = np.dot(h, self.w2) + self.b2
        z_pred[0:3] = np.clip(z_pred[0:3], -1.0, 1.0)
        z_pred[3:5] = np.clip(z_pred[3:5],  0.0, 1.0)
        z_pred[5]   = np.clip(z_pred[5],   -1.0, 1.0)
        return z_pred

class M4_LogOddsDirichletMapping(BaseObservationMapping):
    """M4: Log-odds Dirichlet mapping."""
    def map_observation(self, obs_probabilities: np.ndarray) -> np.ndarray:
        p_c = np.clip(obs_probabilities, 1e-5, 1.0)
        log_p = np.log(p_c)
        center = log_p - np.mean(log_p)
        # Scaled centered log-ratio to [-1, 1]
        z_inferred = np.tanh(center * 0.5)
        z_inferred[3:5] = np.clip((z_inferred[3:5] + 1.0) / 2.0, 0.0, 1.0)
        return z_inferred
