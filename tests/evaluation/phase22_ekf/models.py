"""
Kalman-Based Semantic State Formation Models for Phase 22-EKF.
Implements:
1. Joint Raw Regression Baseline (M1)
2. Open-Loop Decoupled SSF (M2)
3. Extended Kalman Filter (EKF) with continuous OU prior + 23D measurement update (M3)
4. Unscented Kalman Filter (UKF) with continuous OU prior (M4)
"""
from typing import Dict, List, Tuple, Optional
import numpy as np

from .config import STATE_DIM, FAST_DIMS, SLOW_DIMS

class Model1_JointRawBaseline:
    """Canonical joint linear ridge regression with leaky state smoothing."""
    def __init__(self, alpha: float = 0.35, ridge_lambda: float = 1e-3):
        self.alpha = alpha
        self.ridge_lambda = ridge_lambda
        self.W = None
        self.b = None
        self.z = None

    def fit(self, X: np.ndarray, Y: np.ndarray):
        N, D = X.shape
        X_aug = np.hstack([X, np.ones((N, 1))])
        reg = self.ridge_lambda * np.eye(D + 1)
        reg[-1, -1] = 0.0
        W_aug = np.linalg.solve(X_aug.T @ X_aug + reg, X_aug.T @ Y)
        self.W = W_aug[:-1, :].T # (6, 23)
        self.b = W_aug[-1, :]    # (6,)

    def reset(self, z_init: Optional[np.ndarray] = None):
        self.z = z_init.copy() if z_init is not None else np.array([0.0, 0.2, 0.2, 0.1, 0.5, 0.3])

    def step(self, x: np.ndarray, **kwargs) -> np.ndarray:
        if self.z is None:
            self.reset()
        z_obs = self.W @ x + self.b
        self.z = (1.0 - self.alpha) * self.z + self.alpha * z_obs
        self.z[0:3] = np.clip(self.z[0:3], -1.0, 1.0)
        self.z[3:5] = np.clip(self.z[3:5],  0.0, 1.0)
        self.z[5]   = np.clip(self.z[5],   -1.0, 1.0)
        return self.z.copy()

class Model2_OpenLoopSSF:
    """Decoupled fast projection + open-loop heuristic slow accumulation."""
    def __init__(self, alpha_fast: float = 0.35, beta_slow: float = 0.12, ridge_lambda: float = 1e-3):
        self.alpha_fast = alpha_fast
        self.beta_slow = beta_slow
        self.ridge_lambda = ridge_lambda
        self.W_fast = None
        self.b_fast = None
        self.z = None

    def fit(self, X: np.ndarray, Y: np.ndarray):
        Y_fast = Y[:, FAST_DIMS]
        N, D = X.shape
        X_aug = np.hstack([X, np.ones((N, 1))])
        reg = self.ridge_lambda * np.eye(D + 1)
        reg[-1, -1] = 0.0
        W_aug = np.linalg.solve(X_aug.T @ X_aug + reg, X_aug.T @ Y_fast)
        self.W_fast = W_aug[:-1, :].T # (4, 23)
        self.b_fast = W_aug[-1, :]    # (4,)

    def reset(self, z_init: Optional[np.ndarray] = None):
        self.z = z_init.copy() if z_init is not None else np.array([0.0, 0.2, 0.2, 0.1, 0.5, 0.3])

    def step(self, x: np.ndarray, latency: float = 1.0, pause_ratio: float = 0.3, **kwargs) -> np.ndarray:
        if self.z is None:
            self.reset()
        z_fast_obs = self.W_fast @ x + self.b_fast
        self.z[FAST_DIMS] = (1.0 - self.alpha_fast) * self.z[FAST_DIMS] + self.alpha_fast * z_fast_obs
        self.z[0:3] = np.clip(self.z[0:3], -1.0, 1.0)
        self.z[3]   = np.clip(self.z[3],    0.0, 1.0)
        
        fatigue_input = 0.3 * self.z[0] + 0.3 * self.z[3] + 0.4 * (latency / 3.0)
        self.z[4] = (1.0 - self.beta_slow) * self.z[4] + self.beta_slow * fatigue_input
        self.z[4] = np.clip(self.z[4], 0.0, 1.0)
        
        warmth_input = 0.5 * self.z[1] + 0.3 * self.z[2] + 0.2 * (1.0 - self.z[3])
        self.z[5] = (1.0 - self.beta_slow) * self.z[5] + self.beta_slow * warmth_input
        self.z[5] = np.clip(self.z[5], -1.0, 1.0)
        return self.z.copy()

class Model3_EKF:
    """
    Extended Kalman Filter with:
    - Continuous Ornstein-Uhlenbeck limbic prior:
        f(z) = z - gamma * (z - z0) * dt
        F = I - diag(gamma) * dt
        Q = q_noise * I
    - Measurement Model:
        h(z) = H @ z, learned via regularized least squares from z -> x or via observation residual
        or inverted measurement model: y_meas = W_obs @ x + b_obs with innovation y_meas - z_pred.
    """
    def __init__(self, dt: float = 1.0, q_var: float = 0.005, r_var: float = 0.02):
        self.dt = dt
        self.z0 = np.array([0.0, 0.2, 0.2, 0.1, 0.5, 0.3])
        self.gamma = np.array([0.15, 0.10, 0.20, 0.25, 0.10, 0.15])
        
        # State transition Jacobian F
        self.F = np.diag(1.0 - self.gamma * self.dt)
        self.Q = q_var * np.eye(STATE_DIM)
        
        # Inverted observation weights W_obs @ x + b_obs -> z_meas (6D)
        self.W_obs = None
        self.b_obs = None
        self.R = r_var * np.eye(STATE_DIM)
        
        self.z = None
        self.P = None
        
        # Tracking telemetry
        self.last_innovation = np.zeros(STATE_DIM)
        self.last_kalman_gain = np.zeros(STATE_DIM)

    def fit(self, X: np.ndarray, Y: np.ndarray):
        # Learn mapping X (23D) -> Y (6D) to produce measurement coordinate vector
        N, D = X.shape
        X_aug = np.hstack([X, np.ones((N, 1))])
        reg = 1e-3 * np.eye(D + 1)
        reg[-1, -1] = 0.0
        W_aug = np.linalg.solve(X_aug.T @ X_aug + reg, X_aug.T @ Y)
        self.W_obs = W_aug[:-1, :].T # (6, 23)
        self.b_obs = W_aug[-1, :]    # (6,)
        
        # Empirical residual covariance for R
        Y_pred = (X_aug @ W_aug)
        residuals = Y - Y_pred
        cov_res = np.cov(residuals, rowvar=False) + 1e-4 * np.eye(STATE_DIM)
        self.R = cov_res

    def reset(self, z_init: Optional[np.ndarray] = None):
        self.z = z_init.copy() if z_init is not None else self.z0.copy()
        self.P = 0.05 * np.eye(STATE_DIM)

    def step(self, x: np.ndarray, **kwargs) -> np.ndarray:
        if self.z is None:
            self.reset()
        # 1. Predict Step (Continuous OU Drift Prior)
        z_prior = self.z - self.gamma * (self.z - self.z0) * self.dt
        P_prior = self.F @ self.P @ self.F.T + self.Q
        
        # 2. Measurement Coordinate Inversion
        z_meas = self.W_obs @ x + self.b_obs
        
        # 3. Update Step (Innovation & Kalman Gain)
        # H is Identity (6D -> 6D)
        H = np.eye(STATE_DIM)
        y_innov = z_meas - H @ z_prior
        S = H @ P_prior @ H.T + self.R
        K = P_prior @ H.T @ np.linalg.inv(S)
        
        self.z = z_prior + K @ y_innov
        self.P = (np.eye(STATE_DIM) - K @ H) @ P_prior
        
        self.last_innovation = y_innov
        self.last_kalman_gain = np.diag(K)
        
        # Bounded projection
        self.z[0:3] = np.clip(self.z[0:3], -1.0, 1.0)
        self.z[3:5] = np.clip(self.z[3:5],  0.0, 1.0)
        self.z[5]   = np.clip(self.z[5],   -1.0, 1.0)
        return self.z.copy()

class Model4_UKF:
    """
    Unscented Kalman Filter with scaled unscented transform over continuous OU dynamics.
    Handles non-linear bounding and covariance propagation.
    """
    def __init__(self, dt: float = 1.0, alpha: float = 1e-3, beta: float = 2.0, kappa: float = 0.0):
        self.dt = dt
        self.n = STATE_DIM
        self.z0 = np.array([0.0, 0.2, 0.2, 0.1, 0.5, 0.3])
        self.gamma = np.array([0.15, 0.10, 0.20, 0.25, 0.10, 0.15])
        
        self.alpha = alpha
        self.beta = beta
        self.kappa = kappa
        self.lam = self.alpha**2 * (self.n + self.kappa) - self.n
        
        # Weights for mean and covariance
        self.Wm = np.full(2 * self.n + 1, 0.5 / (self.n + self.lam))
        self.Wc = np.full(2 * self.n + 1, 0.5 / (self.n + self.lam))
        self.Wm[0] = self.lam / (self.n + self.lam)
        self.Wc[0] = self.lam / (self.n + self.lam) + (1.0 - self.alpha**2 + self.beta)
        
        self.Q = 0.005 * np.eye(self.n)
        self.R = None
        self.W_obs = None
        self.b_obs = None
        
        self.z = None
        self.P = None

    def fit(self, X: np.ndarray, Y: np.ndarray):
        N, D = X.shape
        X_aug = np.hstack([X, np.ones((N, 1))])
        reg = 1e-3 * np.eye(D + 1)
        reg[-1, -1] = 0.0
        W_aug = np.linalg.solve(X_aug.T @ X_aug + reg, X_aug.T @ Y)
        self.W_obs = W_aug[:-1, :].T
        self.b_obs = W_aug[-1, :]
        
        Y_pred = X_aug @ W_aug
        residuals = Y - Y_pred
        self.R = np.cov(residuals, rowvar=False) + 1e-4 * np.eye(self.n)

    def reset(self, z_init: Optional[np.ndarray] = None):
        self.z = z_init.copy() if z_init is not None else self.z0.copy()
        self.P = 0.05 * np.eye(self.n)

    def _generate_sigma_points(self, mean: np.ndarray, cov: np.ndarray) -> np.ndarray:
        sigmas = np.zeros((2 * self.n + 1, self.n))
        sigmas[0] = mean
        # Matrix square root
        sqrt_cov = np.linalg.cholesky((self.n + self.lam) * cov)
        for i in range(self.n):
            sigmas[i + 1] = mean + sqrt_cov[:, i]
            sigmas[self.n + i + 1] = mean - sqrt_cov[:, i]
        return sigmas

    def step(self, x: np.ndarray, **kwargs) -> np.ndarray:
        if self.z is None:
            self.reset()
        # 1. Generate Sigma Points
        sigmas = self._generate_sigma_points(self.z, self.P)
        
        # 2. Propagate through OU dynamics
        sigmas_f = np.zeros_like(sigmas)
        for i in range(len(sigmas)):
            sigmas_f[i] = sigmas[i] - self.gamma * (sigmas[i] - self.z0) * self.dt
            
        # Predicted state & covariance
        z_prior = np.sum(self.Wm[:, None] * sigmas_f, axis=0)
        P_prior = self.Q.copy()
        for i in range(len(sigmas_f)):
            diff = sigmas_f[i] - z_prior
            P_prior += self.Wc[i] * np.outer(diff, diff)
            
        # 3. Measurement Update
        z_meas = self.W_obs @ x + self.b_obs
        
        # Observation sigma points
        sigmas_h = sigmas_f # H is identity
        z_h_mean = z_prior.copy()
        
        # Innovation covariance S & cross covariance Pxz
        S = self.R.copy()
        Pxz = np.zeros((self.n, self.n))
        for i in range(len(sigmas_h)):
            diff_z = sigmas_f[i] - z_prior
            diff_h = sigmas_h[i] - z_h_mean
            S += self.Wc[i] * np.outer(diff_h, diff_h)
            Pxz += self.Wc[i] * np.outer(diff_z, diff_h)
            
        K = Pxz @ np.linalg.inv(S)
        y_innov = z_meas - z_h_mean
        
        self.z = z_prior + K @ y_innov
        self.P = P_prior - K @ S @ K.T
        
        # Bounded projection
        self.z[0:3] = np.clip(self.z[0:3], -1.0, 1.0)
        self.z[3:5] = np.clip(self.z[3:5],  0.0, 1.0)
        self.z[5]   = np.clip(self.z[5],   -1.0, 1.0)
        return self.z.copy()
