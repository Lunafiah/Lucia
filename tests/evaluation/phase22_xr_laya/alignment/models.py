"""
Candidate Observation-to-Latent Forward Mapping Models.
Isolates Problem H2 (Observation Alignment) from H1 (Continuous Dynamics) and H3 (Real Laya Backbone).

Models:
- M0: Naive Heuristic (Current baseline: y = 2p - 1, H = I)
- M1: Learned Linear Map (z ≈ Wp + b, fitted strictly on D_train)
- M2: Constrained Linear Map (z ≈ W phi(p) + b, with simplex-preserving log-odds feature transform)
- M3: Bounded Neural Calibration Layer (Deterministic 6 -> 24 -> 6 MLP, CPU-only, parameter count recorded)
- M4: Ground-Truth Synthetic Oracle (Upper-bound oracle exposing simulator's emission manifold)
"""
from typing import Dict, List, Tuple, Optional, Any
import numpy as np
import time

STATE_DIM = 6
PROBE_DIM = 6

class BaseObservationMapping:
    def __init__(self, name: str):
        self.name = name
        self.parameter_count = 0
        self.is_fitted = False

    def fit(self, p_train: np.ndarray, z_train: np.ndarray):
        pass

    def invert(self, p: np.ndarray) -> np.ndarray:
        raise NotImplementedError

class M0_NaiveHeuristic(BaseObservationMapping):
    """
    M0: Replicates previous Phase 22-XR baseline.
    y = 2p - 1 with [0, 1] clipping on dimensions 3 and 4.
    H = I.
    Parameter count: 0.
    """
    def __init__(self):
        super().__init__("M0_NaiveHeuristic")
        self.parameter_count = 0
        self.is_fitted = True

    def fit(self, p_train: np.ndarray, z_train: np.ndarray):
        pass

    def invert(self, p: np.ndarray) -> np.ndarray:
        y = p * 2.0 - 1.0
        y[3:5] = p[3:5]
        return y

class M1_LearnedLinear(BaseObservationMapping):
    """
    M1: Learned Linear Observation Map: z ≈ W p + b.
    Fitted using ordinary least squares (Ridge regression with tiny alpha for stability) strictly on D_train.
    Parameters: W (6x6) + b (6) = 42 parameters.
    """
    def __init__(self, ridge_alpha: float = 1e-4):
        super().__init__("M1_LearnedLinear")
        self.ridge_alpha = ridge_alpha
        self.W = np.zeros((PROBE_DIM, STATE_DIM))
        self.b = np.zeros(STATE_DIM)
        self.parameter_count = PROBE_DIM * STATE_DIM + STATE_DIM

    def fit(self, p_train: np.ndarray, z_train: np.ndarray):
        N = len(p_train)
        X = np.hstack([p_train, np.ones((N, 1))])
        XtX = X.T @ X + self.ridge_alpha * np.eye(PROBE_DIM + 1)
        XtZ = X.T @ z_train
        coef = np.linalg.solve(XtX, XtZ)
        self.W = coef[:-1, :]
        self.b = coef[-1, :]
        self.is_fitted = True

    def invert(self, p: np.ndarray) -> np.ndarray:
        z_hat = np.dot(p, self.W) + self.b
        z_hat[0:3] = np.clip(z_hat[0:3], -1.0, 1.0)
        z_hat[3:5] = np.clip(z_hat[3:5],  0.0, 1.0)
        z_hat[5]   = np.clip(z_hat[5],   -1.0, 1.0)
        return z_hat

class M2_ConstrainedLinear(BaseObservationMapping):
    """
    M2: Constrained Linear Observation Map using Simplex-preserving Log-Odds Transform.
    phi(p) = log(p / (1 - p)), clamped to [-10, 10].
    z ≈ W phi(p) + b.
    Fitted strictly on D_train.
    Parameters: W (6x6) + b (6) = 42 parameters.
    """
    def __init__(self, ridge_alpha: float = 1e-4):
        super().__init__("M2_ConstrainedLinear")
        self.ridge_alpha = ridge_alpha
        self.W = np.zeros((PROBE_DIM, STATE_DIM))
        self.b = np.zeros(STATE_DIM)
        self.parameter_count = PROBE_DIM * STATE_DIM + STATE_DIM

    def _transform(self, p: np.ndarray) -> np.ndarray:
        p_clamped = np.clip(p, 1e-5, 1.0 - 1e-5)
        return np.log(p_clamped / (1.0 - p_clamped))

    def fit(self, p_train: np.ndarray, z_train: np.ndarray):
        phi_train = self._transform(p_train)
        N = len(phi_train)
        X = np.hstack([phi_train, np.ones((N, 1))])
        XtX = X.T @ X + self.ridge_alpha * np.eye(PROBE_DIM + 1)
        XtZ = X.T @ z_train
        coef = np.linalg.solve(XtX, XtZ)
        self.W = coef[:-1, :]
        self.b = coef[-1, :]
        self.is_fitted = True

    def invert(self, p: np.ndarray) -> np.ndarray:
        phi_p = self._transform(p)
        z_hat = np.dot(phi_p, self.W) + self.b
        z_hat[0:3] = np.clip(z_hat[0:3], -1.0, 1.0)
        z_hat[3:5] = np.clip(z_hat[3:5],  0.0, 1.0)
        z_hat[5]   = np.clip(z_hat[5],   -1.0, 1.0)
        return z_hat

class M3_BoundedMLPCalibration(BaseObservationMapping):
    """
    M3: Bounded Neural Calibration Layer (Deterministic 6 -> 24 -> 6 MLP).
    CPU-only, closed-form / gradient-free Ridge representation fit on hidden layer.
    Activation: Tanh (strictly bounded [-1, 1]).
    Parameters:
      W1 (6x24) + b1 (24) = 168
      W2 (24x6) + b2 (6) = 150
      Total: 318 parameters.
    """
    def __init__(self, hidden_dim: int = 24, seed: int = 42, ridge_alpha: float = 1e-3):
        super().__init__("M3_BoundedMLPCalibration")
        self.hidden_dim = hidden_dim
        self.ridge_alpha = ridge_alpha
        rng = np.random.RandomState(seed)
        self.W1 = rng.normal(0.0, 0.4, (PROBE_DIM, hidden_dim))
        self.b1 = rng.normal(0.0, 0.1, hidden_dim)
        self.W2 = np.zeros((hidden_dim, STATE_DIM))
        self.b2 = np.zeros(STATE_DIM)
        self.parameter_count = (PROBE_DIM * hidden_dim + hidden_dim) + (hidden_dim * STATE_DIM + STATE_DIM)

    def fit(self, p_train: np.ndarray, z_train: np.ndarray):
        H = np.tanh(p_train @ self.W1 + self.b1)
        N = len(H)
        X = np.hstack([H, np.ones((N, 1))])
        XtX = X.T @ X + self.ridge_alpha * np.eye(self.hidden_dim + 1)
        XtZ = X.T @ z_train
        coef = np.linalg.solve(XtX, XtZ)
        self.W2 = coef[:-1, :]
        self.b2 = coef[-1, :]
        self.is_fitted = True

    def invert(self, p: np.ndarray) -> np.ndarray:
        h = np.tanh(np.dot(p, self.W1) + self.b1)
        z_hat = np.dot(h, self.W2) + self.b2
        z_hat[0:3] = np.clip(z_hat[0:3], -1.0, 1.0)
        z_hat[3:5] = np.clip(z_hat[3:5],  0.0, 1.0)
        z_hat[5]   = np.clip(z_hat[5],   -1.0, 1.0)
        return z_hat

class M4_SyntheticOracle(BaseObservationMapping):
    """
    M4: Ground-Truth Synthetic Oracle.
    Upper-bound reference: inverts the known true emission transformation using
    exact regression of centered log probabilities on the true generation manifold.
    NOT a deployable architecture; purely establishes whether the continuous filter
    can track the latent manifold when the observation model is perfectly specified.
    """
    def __init__(self):
        super().__init__("M4_SyntheticOracle")
        self.W_oracle = np.zeros((PROBE_DIM, STATE_DIM))
        self.b_oracle = np.zeros(STATE_DIM)
        self.parameter_count = 0
        self.is_fitted = False

    def fit(self, p_train: np.ndarray, z_train: np.ndarray):
        # Oracle fits exact centered log-odds
        log_P = np.log(np.clip(p_train, 1e-6, 1.0))
        log_P_centered = log_P - np.mean(log_P, axis=1, keepdims=True)
        X = np.hstack([log_P_centered, np.ones((len(z_train), 1))])
        coef = np.linalg.lstsq(X, z_train, rcond=None)[0]
        self.W_oracle = coef[:-1, :]
        self.b_oracle = coef[-1, :]
        self.is_fitted = True

    def invert(self, p: np.ndarray) -> np.ndarray:
        log_p = np.log(np.clip(p, 1e-6, 1.0))
        log_p_centered = log_p - np.mean(log_p)
        z_hat = np.dot(log_p_centered, self.W_oracle) + self.b_oracle
        z_hat[0:3] = np.clip(z_hat[0:3], -1.0, 1.0)
        z_hat[3:5] = np.clip(z_hat[3:5],  0.0, 1.0)
        z_hat[5]   = np.clip(z_hat[5],   -1.0, 1.0)
        return z_hat
