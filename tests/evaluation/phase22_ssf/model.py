"""
Semantic State Formation (SSF) with Latent Target Decoupling.
Decouples state estimation into:
1. Fast States (z0-z3): Direct regularized projection from semantic polarity + interaction timing + temporal cadence.
2. Slow States (z4-z5): Autonomous continuous temporal somatic accumulation, NOT direct observation inversion.
"""
from typing import Dict, List, Tuple, Optional
import numpy as np

from .config import STATE_DIM, FAST_DIMS, SLOW_DIMS

class SemanticStateFormationDecoupled:
    """
    Decoupled SSF Layer:
    - Fits fast projection: W_fast @ e_t + b_fast -> z_fast (z0, z1, z2, z3)
    - Maintains slow integration: z_slow_t = (1 - beta)*z_slow_{t-1} + beta * g(z_fast_t, e_inter_t)
    - Emits unified continuous state: z_hat = [z0..z5]
    """
    def __init__(self, alpha_fast: float = 0.35, beta_slow: float = 0.12, ridge_lambda: float = 1e-3):
        self.alpha_fast = alpha_fast
        self.beta_slow = beta_slow
        self.ridge_lambda = ridge_lambda
        
        self.W_fast = None
        self.b_fast = None
        self.z_state = None

    def fit(self, X: np.ndarray, Y: np.ndarray):
        # Y has shape (N, 6). Extract fast coordinates (z0, z1, z2, z3)
        Y_fast = Y[:, FAST_DIMS]
        N, D = X.shape
        X_aug = np.hstack([X, np.ones((N, 1))])
        reg = self.ridge_lambda * np.eye(D + 1)
        reg[-1, -1] = 0.0 # Don't penalize bias
        
        W_aug = np.linalg.solve(X_aug.T @ X_aug + reg, X_aug.T @ Y_fast)
        self.W_fast = W_aug[:-1, :].T # shape (4, D)
        self.b_fast = W_aug[-1, :]    # shape (4,)

    def reset_state(self, z_init: Optional[np.ndarray] = None):
        if z_init is not None:
            self.z_state = z_init.copy()
        else:
            self.z_state = np.array([0.0, 0.2, 0.2, 0.1, 0.5, 0.3], dtype=np.float64)

    def step(self, x_features: np.ndarray, interaction_latency: float = 1.0, pause_ratio: float = 0.3) -> np.ndarray:
        if self.z_state is None:
            self.reset_state()
            
        # 1. Fast State Estimation (z0: load, z1: val, z2: agency, z3: urgency)
        z_fast_obs = self.W_fast @ x_features + self.b_fast
        
        # Leaky filtering on fast states
        self.z_state[FAST_DIMS] = (1.0 - self.alpha_fast) * self.z_state[FAST_DIMS] + self.alpha_fast * z_fast_obs
        
        # Bounded projection
        self.z_state[0:3] = np.clip(self.z_state[0:3], -1.0, 1.0)
        self.z_state[3]   = np.clip(self.z_state[3],    0.0, 1.0)
        
        # 2. Slow State Autonomous Somatic Accumulation (z4: fatigue, z5: warmth)
        # Metabolic fatigue accumulates with cognitive load & urgency, moderated by pause ratio & response latency
        fatigue_input = 0.3 * self.z_state[0] + 0.3 * self.z_state[3] + 0.4 * (interaction_latency / 3.0)
        self.z_state[4] = (1.0 - self.beta_slow) * self.z_state[4] + self.beta_slow * fatigue_input
        self.z_state[4] = np.clip(self.z_state[4], 0.0, 1.0)
        
        # Relational warmth accumulates with sustained positive valence, smooth turn-taking, and low confrontation
        warmth_input = 0.5 * self.z_state[1] + 0.3 * self.z_state[2] + 0.2 * (1.0 - self.z_state[3])
        self.z_state[5] = (1.0 - self.beta_slow) * self.z_state[5] + self.beta_slow * warmth_input
        self.z_state[5] = np.clip(self.z_state[5], -1.0, 1.0)
        
        return self.z_state.copy()

class RawBaselineModel:
    """Direct un-decoupled baseline projection."""
    def __init__(self, ridge_lambda: float = 1e-3):
        self.ridge_lambda = ridge_lambda
        self.W = None
        self.b = None
        self.z_state = None

    def fit(self, X: np.ndarray, Y: np.ndarray):
        N, D = X.shape
        X_aug = np.hstack([X, np.ones((N, 1))])
        reg = self.ridge_lambda * np.eye(D + 1)
        reg[-1, -1] = 0.0
        W_aug = np.linalg.solve(X_aug.T @ X_aug + reg, X_aug.T @ Y)
        self.W = W_aug[:-1, :].T
        self.b = W_aug[-1, :]

    def reset_state(self, z_init: Optional[np.ndarray] = None):
        if z_init is not None:
            self.z_state = z_init.copy()
        else:
            self.z_state = np.array([0.0, 0.2, 0.2, 0.1, 0.5, 0.3], dtype=np.float64)

    def step(self, x: np.ndarray) -> np.ndarray:
        if self.z_state is None:
            self.reset_state()
        z_obs = self.W @ x + self.b
        self.z_state = 0.65 * self.z_state + 0.35 * z_obs
        self.z_state[0:3] = np.clip(self.z_state[0:3], -1.0, 1.0)
        self.z_state[3:5] = np.clip(self.z_state[3:5],  0.0, 1.0)
        self.z_state[5]   = np.clip(self.z_state[5],   -1.0, 1.0)
        return self.z_state.copy()
