"""
Information Stream Bundler and State Formation Estimator for Phase 22-INF.
Provides explicit ablations E0 through E6 and downstream continuous state integration.
"""
from typing import Dict, List, Tuple
import numpy as np

from .config import STATE_DIM

class InformationStreamBundler:
    """
    Assembles controlled information streams for ablations:
    - E0: Existing baseline (Text logits + base acoustics, dim=13)
    - E1: + Temporal micro-dynamics (velocity, cadence, pause, dim=19)
    - E2: + Richer prosodic trajectory (prosodic energy, pitch variation, dim=19)
    - E3: + Interaction dynamics (latency, interruption, synchrony, dim=17)
    - E4: + Persistent relational context (somatic accumulation, dim=17)
    - E5: Full Multimodal Integration (Text + Acoustics + Temporal + Interaction + Relational, dim=27)
    - E6_Oracle: Ground truth z_true + minimal sensor noise (dim=6)
    """
    @staticmethod
    def extract_stream(step_dict: Dict, config_code: str) -> np.ndarray:
        text = step_dict["text_features"]            # 7
        acoustics = step_dict["acoustics_base"]      # 6
        temporal = step_dict["temporal_dynamics"]    # 6
        interaction = step_dict["interaction_dynamics"] # 4
        relational = step_dict["relational_context"] # 4
        
        if config_code == "E0_Baseline":
            return np.concatenate([text, acoustics]) # 13
        elif config_code == "E1_Temporal":
            return np.concatenate([text, acoustics, temporal]) # 19
        elif config_code == "E2_Prosodic":
            # Focus on acoustic + temporal prosody
            return np.concatenate([acoustics, temporal, interaction[:2]]) # 14
        elif config_code == "E3_Interaction":
            return np.concatenate([text, acoustics, interaction]) # 17
        elif config_code == "E4_Relational":
            return np.concatenate([text, acoustics, relational]) # 17
        elif config_code == "E5_FullMultimodal":
            return np.concatenate([text, acoustics, temporal, interaction, relational]) # 27
        elif config_code == "E6_Oracle":
            noise = np.random.normal(0, 0.05, size=STATE_DIM)
            return step_dict["z_true"] + noise
        else:
            raise ValueError(f"Unknown stream configuration: {config_code}")

class StateFormationEstimator:
    """
    Lightweight, CPU-native state formation layer.
    Combines:
    1. Ridge linear projection from arbitrary feature dim D -> 6D
    2. Continuous recursive leaky state integration: z_hat_t = (1 - alpha)*z_hat_{t-1} + alpha * W e_t
    """
    def __init__(self, alpha: float = 0.35, ridge_lambda: float = 1e-3):
        self.alpha = alpha
        self.ridge_lambda = ridge_lambda
        self.W = None
        self.b = None
        self.z_state = None

    def fit(self, X: np.ndarray, Y: np.ndarray):
        # Regularized ridge regression: W = (X^T X + lambda I)^-1 X^T Y
        N, D = X.shape
        X_aug = np.hstack([X, np.ones((N, 1))])
        reg = self.ridge_lambda * np.eye(D + 1)
        reg[-1, -1] = 0.0 # Don't penalize bias
        
        W_aug = np.linalg.solve(X_aug.T @ X_aug + reg, X_aug.T @ Y)
        self.W = W_aug[:-1, :].T # shape (6, D)
        self.b = W_aug[-1, :]    # shape (6,)

    def reset_state(self, z_init: np.ndarray = None):
        if z_init is not None:
            self.z_state = z_init.copy()
        else:
            self.z_state = np.array([0.0, 0.2, 0.2, 0.1, 0.5, 0.3], dtype=np.float64)

    def predict_instantaneous(self, x: np.ndarray) -> np.ndarray:
        return self.W @ x + self.b

    def step(self, x: np.ndarray) -> np.ndarray:
        z_obs = self.predict_instantaneous(x)
        if self.z_state is None:
            self.z_state = z_obs.copy()
        else:
            self.z_state = (1.0 - self.alpha) * self.z_state + self.alpha * z_obs
            
        self.z_state[0:3] = np.clip(self.z_state[0:3], -1.0, 1.0)
        self.z_state[3:5] = np.clip(self.z_state[3:5],  0.0, 1.0)
        self.z_state[5]   = np.clip(self.z_state[5],   -1.0, 1.0)
        return self.z_state.copy()
