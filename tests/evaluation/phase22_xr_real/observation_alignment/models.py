"""Observation-to-latent alignment estimators for Phase 22-XR-L.

Investigates:
A0: Identity / Naive Mapping (the invalid baseline y = 2p - 1, H = I)
A1: Linear Alignment (p_laya -> Ridge/LinearRegression -> z_hat)
A2: Nonlinear Alignment (p_laya -> Bounded MLP -> z_hat)
"""

from typing import Any, Dict, Optional
import numpy as np


class BaseAlignmentModel:
    """Base interface for observation alignment models."""

    def fit(self, P: np.ndarray, Z: np.ndarray) -> "BaseAlignmentModel":
        raise NotImplementedError

    def predict(self, P: np.ndarray) -> np.ndarray:
        raise NotImplementedError


class NaiveAlignment(BaseAlignmentModel):
    """A0: Heuristic naive baseline (y = 2p - 1, H = I).
    
    Treated as an unaligned observation-coordinate mismatch.
    """

    def fit(self, P: np.ndarray, Z: np.ndarray) -> "NaiveAlignment":
        # Fixed heuristic, no training
        return self

    def predict(self, P: np.ndarray) -> np.ndarray:
        # P is (N, 6) in [0, 1] simplex
        # Naive mapping: y = 2p - 1 in [-1, 1]
        return 2.0 * P - 1.0


class LinearAlignment(BaseAlignmentModel):
    """A1: Linear / Ridge regression mapping from simplex to latent space."""

    def __init__(self, alpha: float = 1e-3):
        self.alpha = alpha
        self.W: Optional[np.ndarray] = None  # (6, 6)
        self.b: Optional[np.ndarray] = None  # (6,)

    def fit(self, P: np.ndarray, Z: np.ndarray) -> "LinearAlignment":
        # Ridge regression: (P^T P + alpha * I)^(-1) P^T Z with bias
        N, D_in = P.shape
        _, D_out = Z.shape
        P_bias = np.hstack([P, np.ones((N, 1))])
        I_reg = np.eye(D_in + 1)
        I_reg[-1, -1] = 0.0  # Do not regularize bias
        
        # Solve (P_b^T P_b + alpha * I) W_b = P_b^T Z
        lhs = P_bias.T @ P_bias + self.alpha * I_reg
        rhs = P_bias.T @ Z
        try:
            W_all = np.linalg.solve(lhs, rhs)
        except np.linalg.LinAlgError:
            W_all = np.linalg.pinv(lhs) @ rhs

        self.W = W_all[:-1, :]
        self.b = W_all[-1, :]
        return self

    def predict(self, P: np.ndarray) -> np.ndarray:
        if self.W is None or self.b is None:
            raise RuntimeError("LinearAlignment model is not fitted.")
        return P @ self.W + self.b


class NonlinearMLPAlignment(BaseAlignmentModel):
    """A2: Lightweight bounded MLP alignment model (6 -> 24 -> 6)."""

    def __init__(self, hidden_dim: int = 24, lr: float = 0.01, epochs: int = 250, seed: int = 42):
        self.hidden_dim = hidden_dim
        self.lr = lr
        self.epochs = epochs
        self.seed = seed
        self.W1: Optional[np.ndarray] = None
        self.b1: Optional[np.ndarray] = None
        self.W2: Optional[np.ndarray] = None
        self.b2: Optional[np.ndarray] = None

    def fit(self, P: np.ndarray, Z: np.ndarray) -> "NonlinearMLPAlignment":
        rng = np.random.default_rng(self.seed)
        N, D_in = P.shape
        _, D_out = Z.shape

        # Initialize weights (Xavier/He)
        self.W1 = rng.normal(0, np.sqrt(2.0 / D_in), (D_in, self.hidden_dim))
        self.b1 = np.zeros((1, self.hidden_dim))
        self.W2 = rng.normal(0, np.sqrt(2.0 / self.hidden_dim), (self.hidden_dim, D_out))
        self.b2 = np.zeros((1, D_out))

        # Train with Adam or SGD with momentum
        for epoch in range(self.epochs):
            # Forward pass
            h_pre = P @ self.W1 + self.b1
            h = np.tanh(h_pre)  # Bounded non-linearity
            y_hat = h @ self.W2 + self.b2

            # Loss: MSE
            diff = y_hat - Z
            grad_y = (2.0 / N) * diff

            # Backprop
            grad_W2 = h.T @ grad_y
            grad_b2 = np.sum(grad_y, axis=0, keepdims=True)

            grad_h = grad_y @ self.W2.T
            grad_h_pre = grad_h * (1.0 - h**2)

            grad_W1 = P.T @ grad_h_pre
            grad_b1 = np.sum(grad_h_pre, axis=0, keepdims=True)

            # Update
            self.W2 -= self.lr * grad_W2
            self.b2 -= self.lr * grad_b2
            self.W1 -= self.lr * grad_W1
            self.b1 -= self.lr * grad_b1

        return self

    def predict(self, P: np.ndarray) -> np.ndarray:
        if self.W1 is None or self.W2 is None:
            raise RuntimeError("NonlinearMLPAlignment model is not fitted.")
        h = np.tanh(P @ self.W1 + self.b1)
        return h @ self.W2 + self.b2
