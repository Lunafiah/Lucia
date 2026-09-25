"""
Target Ontology Architectures for Phase 22-ONT.
Implements:
1. Ontology 1 (O1): Legacy 6D joint state regression (Baseline)
2. Ontology 2 (O2): 4D Observable Interaction State (u_obs in R^4) + 2D Heuristic Slow Memory (m in R^2)
3. Ontology 3 (O3): 4D Observable State (u_obs via EKF) + Relational/Somatic Consolidation (Attractor Memory dynamics)
"""
from typing import Dict, List, Tuple, Optional
import numpy as np

class Ontology1_Legacy6D:
    """O1: Legacy single-timescale 6D state estimator."""
    def __init__(self, alpha: float = 0.35, ridge_lambda: float = 1e-3):
        self.alpha = alpha
        self.ridge_lambda = ridge_lambda
        self.W = None
        self.b = None
        self.z = None

    def fit(self, X: np.ndarray, Y_6d: np.ndarray):
        N, D = X.shape
        X_aug = np.hstack([X, np.ones((N, 1))])
        reg = self.ridge_lambda * np.eye(D + 1)
        reg[-1, -1] = 0.0
        W_aug = np.linalg.solve(X_aug.T @ X_aug + reg, X_aug.T @ Y_6d)
        self.W = W_aug[:-1, :].T # (6, 23)
        self.b = W_aug[-1, :]    # (6,)

    def reset(self, z_init: Optional[np.ndarray] = None):
        self.z = z_init.copy() if z_init is not None else np.array([0.0, 0.2, 0.2, 0.1, 0.5, 0.3])

    def step(self, x: np.ndarray) -> np.ndarray:
        if self.z is None:
            self.reset()
        z_obs = self.W @ x + self.b
        self.z = (1.0 - self.alpha) * self.z + self.alpha * z_obs
        self.z[0:3] = np.clip(self.z[0:3], -1.0, 1.0)
        self.z[3:5] = np.clip(self.z[3:5],  0.0, 1.0)
        self.z[5]   = np.clip(self.z[5],   -1.0, 1.0)
        return self.z.copy()

class Ontology2_Decoupled4D2D:
    """O2: 4D Observable Interaction State (u in R^4) + 2D Slow Memory (m in R^2)."""
    def __init__(self, alpha_u: float = 0.35, beta_m: float = 0.12, ridge_lambda: float = 1e-3):
        self.alpha_u = alpha_u
        self.beta_m = beta_m
        self.ridge_lambda = ridge_lambda
        self.W_u = None
        self.b_u = None
        self.u = None
        self.m = None

    def fit(self, X: np.ndarray, U_4d: np.ndarray):
        N, D = X.shape
        X_aug = np.hstack([X, np.ones((N, 1))])
        reg = self.ridge_lambda * np.eye(D + 1)
        reg[-1, -1] = 0.0
        W_aug = np.linalg.solve(X_aug.T @ X_aug + reg, X_aug.T @ U_4d)
        self.W_u = W_aug[:-1, :].T # (4, 23)
        self.b_u = W_aug[-1, :]    # (4,)

    def reset(self, u_init: Optional[np.ndarray] = None, m_init: Optional[np.ndarray] = None):
        self.u = u_init.copy() if u_init is not None else np.array([0.0, 0.2, 0.2, 0.1])
        self.m = m_init.copy() if m_init is not None else np.array([0.5, 0.3])

    def step(self, x: np.ndarray) -> Tuple[np.ndarray, np.ndarray]:
        if self.u is None or self.m is None:
            self.reset()
            
        # 1. 4D Observable update
        u_obs = self.W_u @ x + self.b_u
        self.u = (1.0 - self.alpha_u) * self.u + self.alpha_u * u_obs
        self.u[0:3] = np.clip(self.u[0:3], -1.0, 1.0)
        self.u[3]   = np.clip(self.u[3],    0.0, 1.0)
        
        # 2. 2D Slow accumulation
        m_input = np.array([
            0.15 * self.u[0] + 0.15 * self.u[3], # Fatigue ~ Load & Urgency
            0.20 * self.u[1] + 0.05 * self.u[2]  # Warmth ~ Valence & Agency
        ])
        self.m = (1.0 - self.beta_m) * self.m + self.beta_m * m_input
        self.m[0] = np.clip(self.m[0],  0.0, 1.0)
        self.m[1] = np.clip(self.m[1], -1.0, 1.0)
        return self.u.copy(), self.m.copy()

class Ontology3_MultiTimescaleConsolidation:
    """
    O3: Multi-Timescale Semantic State Formation:
    - Layer A: 4D Observable Interaction State (u in R^4) tracked via EKF with continuous OU prior.
    - Layer B: Relational/Somatic Memory Consolidation via attractor dynamics:
        m_t = (1 - eta)*m_{t-1} + eta * Attractor(u_t) + synaptic_drift
        Warmth decays smoothly toward Philia resting attractor (+0.30) during silence.
    """
    def __init__(self, dt: float = 1.0, q_var: float = 0.005, r_var: float = 0.02, eta_slow: float = 0.08):
        self.dt = dt
        self.eta_slow = eta_slow
        self.u0 = np.array([0.0, 0.2, 0.2, 0.1])
        self.gamma_u = np.array([0.15, 0.10, 0.20, 0.25])
        self.F_u = np.diag(1.0 - self.gamma_u * self.dt)
        self.Q_u = q_var * np.eye(4)
        
        self.W_u = None
        self.b_u = None
        self.R_u = r_var * np.eye(4)
        
        self.u = None
        self.P_u = None
        
        # Slow Relational Memory (Fatigue m0, Warmth m1)
        self.m = None
        self.m_resting = np.array([0.5, 0.3]) # Philia-like resting attractor
        self.gamma_m = np.array([0.05, 0.05])

    def fit(self, X: np.ndarray, U_4d: np.ndarray):
        N, D = X.shape
        X_aug = np.hstack([X, np.ones((N, 1))])
        reg = 1e-3 * np.eye(D + 1)
        reg[-1, -1] = 0.0
        W_aug = np.linalg.solve(X_aug.T @ X_aug + reg, X_aug.T @ U_4d)
        self.W_u = W_aug[:-1, :].T # (4, 23)
        self.b_u = W_aug[-1, :]    # (4,)
        
        U_pred = X_aug @ W_aug
        res = U_4d - U_pred
        self.R_u = np.cov(res, rowvar=False) + 1e-4 * np.eye(4)

    def reset(self, u_init: Optional[np.ndarray] = None, m_init: Optional[np.ndarray] = None):
        self.u = u_init.copy() if u_init is not None else self.u0.copy()
        self.P_u = 0.05 * np.eye(4)
        self.m = m_init.copy() if m_init is not None else self.m_resting.copy()

    def step(self, x: np.ndarray) -> Tuple[np.ndarray, np.ndarray, np.ndarray]:
        if self.u is None or self.m is None:
            self.reset()
            
        # 1. Layer A: 4D EKF Step
        u_prior = self.u - self.gamma_u * (self.u - self.u0) * self.dt
        P_prior = self.F_u @ self.P_u @ self.F_u.T + self.Q_u
        
        u_meas = self.W_u @ x + self.b_u
        y_innov = u_meas - u_prior
        S = P_prior + self.R_u
        K = P_prior @ np.linalg.inv(S)
        
        self.u = u_prior + K @ y_innov
        self.P_u = (np.eye(4) - K) @ P_prior
        
        self.u[0:3] = np.clip(self.u[0:3], -1.0, 1.0)
        self.u[3]   = np.clip(self.u[3],    0.0, 1.0)
        
        # 2. Layer B: Multi-timescale Relational Memory Consolidation
        # Somatic interaction signal driving attractor shifts
        somatic_drive = np.array([
            0.12 * self.u[0] + 0.12 * self.u[3],
            0.18 * self.u[1] + 0.06 * self.u[2]
        ])
        
        # Drift toward resting attractor + somatic drive
        dm = -self.gamma_m * (self.m - self.m_resting) * self.dt + somatic_drive
        self.m = self.m + dm
        self.m[0] = np.clip(self.m[0],  0.0, 1.0)
        self.m[1] = np.clip(self.m[1], -1.0, 1.0)
        
        # Uncertainty diagonal
        u_sigma = np.sqrt(np.diag(self.P_u))
        return self.u.copy(), self.m.copy(), u_sigma
