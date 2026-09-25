"""
Controlled Ladder of Alignment and State Formation Models (A0 through A7)
for Phase 22-AL.
A0: Naive baseline direct mapping
A1: Ridge Linear Projection (W e_t + b)
A2: Constrained Projection (bounded tanh output)
A3: Small Calibration MLP (2-layer, 32 hidden units, CPU-native)
A4: Temporal Window Multi-Frame Projector ([e_{t-k}, ..., e_t])
A5: Leaky State Estimator (z_t = (1-alpha)*z_{t-1} + alpha*f(e_t))
A6: Observation-Likelihood State Estimator (Bayesian likelihood inversion)
A7: Hybrid Temporal Alignment (temporal integration + bounded projection + Bucy-Kalman filter)
"""
from typing import Dict, List, Tuple, Optional, Any
import numpy as np

from .config import STATE_DIM

class AlignmentModelBase:
    def __init__(self, name: str):
        self.name = name
        self.is_fitted = False
        self.param_count = 0

    def fit(self, X: np.ndarray, y: np.ndarray) -> None:
        self.is_fitted = True

    def predict(self, x: np.ndarray, prev_z: Optional[np.ndarray] = None) -> np.ndarray:
        raise NotImplementedError

# A0: Naive baseline direct identity mapping
class AlignmentA0Naive(AlignmentModelBase):
    def __init__(self):
        super().__init__("A0_Naive")
        self.param_count = 0
        self.is_fitted = True

    def predict(self, x: np.ndarray, prev_z: Optional[np.ndarray] = None) -> np.ndarray:
        return np.asarray(x, dtype=np.float64).copy()

# A1: Ridge Linear Projection (W e_t + b)
class AlignmentA1Linear(AlignmentModelBase):
    def __init__(self, input_dim: int = STATE_DIM, output_dim: int = STATE_DIM, alpha: float = 1.0):
        super().__init__("A1_Linear")
        self.input_dim = input_dim
        self.output_dim = output_dim
        self.alpha = alpha
        self.W = np.eye(output_dim, input_dim)
        self.b = np.zeros(output_dim)
        self.param_count = input_dim * output_dim + output_dim

    def fit(self, X: np.ndarray, y: np.ndarray) -> None:
        # X: (N, D_in), y: (N, D_out)
        N = X.shape[0]
        X_aug = np.hstack([X, np.ones((N, 1))])
        reg = self.alpha * np.eye(X_aug.shape[1])
        reg[-1, -1] = 0.0 # Don't penalize bias
        try:
            params = np.linalg.solve(X_aug.T @ X_aug + reg, X_aug.T @ y)
        except np.linalg.LinAlgError:
            params = np.linalg.pinv(X_aug.T @ X_aug + reg) @ (X_aug.T @ y)
        self.W = params[:-1, :].T
        self.b = params[-1, :]
        self.is_fitted = True

    def predict(self, x: np.ndarray, prev_z: Optional[np.ndarray] = None) -> np.ndarray:
        return self.W @ x + self.b

# A2: Constrained Bounded Projection (normalized tanh output)
class AlignmentA2Constrained(AlignmentModelBase):
    def __init__(self, input_dim: int = STATE_DIM, output_dim: int = STATE_DIM, alpha: float = 1.0):
        super().__init__("A2_Constrained")
        self.linear = AlignmentA1Linear(input_dim, output_dim, alpha)
        self.param_count = self.linear.param_count

    def fit(self, X: np.ndarray, y: np.ndarray) -> None:
        # Pre-inverse tanh target clipping to [-0.95, 0.95]
        y_clip = np.clip(y, -0.95, 0.95)
        y_arctanh = np.arctanh(y_clip)
        self.linear.fit(X, y_arctanh)
        self.is_fitted = True

    def predict(self, x: np.ndarray, prev_z: Optional[np.ndarray] = None) -> np.ndarray:
        raw = self.linear.predict(x)
        out = np.tanh(raw)
        # Bounded coordinate ranges
        out[3:5] = np.clip((out[3:5] + 1.0) / 2.0, 0.0, 1.0)
        return out

# A3: Small Calibration MLP (2-layer: 6 -> 32 -> 6 with ReLU, CPU native)
class AlignmentA3SmallMLP(AlignmentModelBase):
    def __init__(self, input_dim: int = STATE_DIM, hidden_dim: int = 32, output_dim: int = STATE_DIM):
        super().__init__("A3_SmallMLP")
        self.input_dim = input_dim
        self.hidden_dim = hidden_dim
        self.output_dim = output_dim
        self.param_count = (input_dim * hidden_dim + hidden_dim) + (hidden_dim * output_dim + output_dim)
        
        # Init weights with Xavier
        rng = np.random.RandomState(42)
        self.W1 = rng.randn(hidden_dim, input_dim) * np.sqrt(2.0 / input_dim)
        self.b1 = np.zeros(hidden_dim)
        self.W2 = rng.randn(output_dim, hidden_dim) * np.sqrt(2.0 / hidden_dim)
        self.b2 = np.zeros(output_dim)

    def fit(self, X: np.ndarray, y: np.ndarray, epochs: int = 40, lr: float = 0.01, batch_size: int = 64) -> None:
        N = X.shape[0]
        rng = np.random.RandomState(42)
        for ep in range(epochs):
            indices = rng.permutation(N)
            for start in range(0, N, batch_size):
                end = min(start + batch_size, N)
                idx = indices[start:end]
                xb = X[idx]
                yb = y[idx]
                
                # Forward
                h = np.maximum(0, xb @ self.W1.T + self.b1) # ReLU
                pred = h @ self.W2.T + self.b2
                
                # Backprop
                grad_out = (pred - yb) / len(idx)
                grad_W2 = grad_out.T @ h
                grad_b2 = np.sum(grad_out, axis=0)
                
                grad_h = grad_out @ self.W2
                grad_h[h <= 0] = 0.0 # ReLU derivative
                grad_W1 = grad_h.T @ xb
                grad_b1 = np.sum(grad_h, axis=0)
                
                # Update
                self.W2 -= lr * grad_W2
                self.b2 -= lr * grad_b2
                self.W1 -= lr * grad_W1
                self.b1 -= lr * grad_b1
        self.is_fitted = True

    def predict(self, x: np.ndarray, prev_z: Optional[np.ndarray] = None) -> np.ndarray:
        h = np.maximum(0, self.W1 @ x + self.b1)
        out = self.W2 @ h + self.b2
        out[0:3] = np.clip(out[0:3], -1.0, 1.0)
        out[3:5] = np.clip(out[3:5], 0.0, 1.0)
        out[5]   = np.clip(out[5], -1.0, 1.0)
        return out

# A4: Temporal Window Multi-Frame Linear Projector ([e_{t-k}, ..., e_t])
class AlignmentA4TemporalWindow(AlignmentModelBase):
    def __init__(self, window_size: int = 3, feature_dim: int = STATE_DIM, output_dim: int = STATE_DIM):
        super().__init__(f"A4_TemporalWindow_k{window_size}")
        self.k = window_size
        self.feature_dim = feature_dim
        self.total_input_dim = feature_dim * window_size
        self.linear = AlignmentA1Linear(self.total_input_dim, output_dim)
        self.param_count = self.linear.param_count

    def fit(self, X_windowed: np.ndarray, y: np.ndarray) -> None:
        self.linear.fit(X_windowed, y)
        self.is_fitted = True

    def predict(self, x_windowed: np.ndarray, prev_z: Optional[np.ndarray] = None) -> np.ndarray:
        out = self.linear.predict(x_windowed)
        out[0:3] = np.clip(out[0:3], -1.0, 1.0)
        out[3:5] = np.clip(out[3:5], 0.0, 1.0)
        out[5]   = np.clip(out[5], -1.0, 1.0)
        return out

# A5: Leaky State Estimator (z_t = (1 - alpha) * z_{t-1} + alpha * f(e_t))
class AlignmentA5LeakyIntegrator(AlignmentModelBase):
    def __init__(self, alpha: float = 0.35, base_model: Optional[AlignmentModelBase] = None):
        super().__init__(f"A5_Leaky_a{int(alpha*100)}")
        self.alpha = alpha
        self.base_model = base_model if base_model is not None else AlignmentA1Linear()
        self.param_count = self.base_model.param_count + 1

    def fit(self, X: np.ndarray, y: np.ndarray) -> None:
        self.base_model.fit(X, y)
        self.is_fitted = True

    def predict(self, x: np.ndarray, prev_z: Optional[np.ndarray] = None) -> np.ndarray:
        instant_pred = self.base_model.predict(x)
        if prev_z is None:
            return instant_pred
        z_smooth = (1.0 - self.alpha) * prev_z + self.alpha * instant_pred
        z_smooth[0:3] = np.clip(z_smooth[0:3], -1.0, 1.0)
        z_smooth[3:5] = np.clip(z_smooth[3:5], 0.0, 1.0)
        z_smooth[5]   = np.clip(z_smooth[5], -1.0, 1.0)
        return z_smooth

# A6: Observation-Likelihood State Estimator (Inverted probabilistic Bayesian likelihood)
class AlignmentA6ObservationLikelihood(AlignmentModelBase):
    def __init__(self, dim: int = STATE_DIM):
        super().__init__("A6_ObservationLikelihood")
        self.dim = dim
        self.H = np.eye(dim) # Forward observation map: e = H z + v
        self.R = np.eye(dim) * 0.10 # Measurement noise covariance
        self.linear = AlignmentA1Linear(dim, dim)
        self.param_count = self.linear.param_count

    def fit(self, X: np.ndarray, y: np.ndarray) -> None:
        self.linear.fit(X, y)
        # Compute empirical residual covariance R = Cov(X - H y)
        preds = np.array([self.linear.predict(x) for x in X])
        residuals = preds - y
        self.R = np.cov(residuals.T) + 1e-4 * np.eye(self.dim)
        self.is_fitted = True

    def predict(self, x: np.ndarray, prev_z: Optional[np.ndarray] = None) -> np.ndarray:
        # Prior is prev_z or baseline attractor
        z_prior = prev_z if prev_z is not None else np.array([0.0, 0.2, 0.2, 0.1, 0.5, 0.3])
        P_prior = np.eye(self.dim) * 0.20
        
        # Inverted observation mapping
        z_meas = self.linear.predict(x)
        
        # Bayesian Gauss-Markov fusion:
        # K = P_prior @ (P_prior + R)^-1
        try:
            K = P_prior @ np.linalg.inv(P_prior + self.R)
        except np.linalg.LinAlgError:
            K = P_prior @ np.linalg.pinv(P_prior + self.R)
            
        z_post = z_prior + K @ (z_meas - z_prior)
        z_post[0:3] = np.clip(z_post[0:3], -1.0, 1.0)
        z_post[3:5] = np.clip(z_post[3:5], 0.0, 1.0)
        z_post[5]   = np.clip(z_post[5], -1.0, 1.0)
        return z_post

# A7: Hybrid Temporal Alignment (Multi-Frame + MLP + Bounded Output + Bucy-Kalman Update)
class AlignmentA7Hybrid(AlignmentModelBase):
    def __init__(self, window_size: int = 3, dim: int = STATE_DIM):
        super().__init__("A7_HybridTemporal")
        self.k = window_size
        self.dim = dim
        self.window_mlp = AlignmentA3SmallMLP(input_dim=dim * window_size, hidden_dim=32, output_dim=dim)
        self.leaky = AlignmentA5LeakyIntegrator(alpha=0.40, base_model=self.window_mlp)
        self.param_count = self.window_mlp.param_count + 2

    def fit(self, X_windowed: np.ndarray, y: np.ndarray) -> None:
        self.window_mlp.fit(X_windowed, y, epochs=40)
        self.is_fitted = True

    def predict(self, x_windowed: np.ndarray, prev_z: Optional[np.ndarray] = None) -> np.ndarray:
        instant = self.window_mlp.predict(x_windowed)
        if prev_z is None:
            return instant
        out = (1.0 - 0.40) * prev_z + 0.40 * instant
        out[0:3] = np.clip(out[0:3], -1.0, 1.0)
        out[3:5] = np.clip(out[3:5], 0.0, 1.0)
        out[5]   = np.clip(out[5], -1.0, 1.0)
        return out
