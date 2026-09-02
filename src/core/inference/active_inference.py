"""
Active Inference Engine — Short-horizon Free Energy Minimization.

Maintains a 3x3 linear generative model of PAD transitions (Belief State)
and updates it per conversation turn via analytic gradient descent with
KL-regularization toward identity.

Requirements: Phase 4 (1.1–1.5, 2.1–2.8, 3.1–3.5)
"""

from __future__ import annotations

import logging
from dataclasses import dataclass
from typing import Dict, Optional

import numpy as np

from src.core.models import PADState

logger = logging.getLogger(__name__)


@dataclass
class ActiveInferenceConfig:
    """
    Configuration for ActiveInferenceEngine.

    Parameters
    ----------
    kl_weight : float
        Weight on the KL-regularization term (L2 penalty pulling A toward identity).
        Must be in [0.0, 1.0]. Default: 0.01.
    learning_rate : float
        Learning rate for the analytic gradient update.
        Must be in (0.0, 1.0]. Default: 1e-3.
    """

    kl_weight: float = 0.01
    learning_rate: float = 1e-3

    def __post_init__(self) -> None:
        if not (0.0 <= self.kl_weight <= 1.0):
            raise ValueError(
                f"ActiveInferenceConfig.kl_weight ({self.kl_weight}) must be in [0.0, 1.0]"
            )
        if not (0.0 < self.learning_rate <= 1.0):
            raise ValueError(
                f"ActiveInferenceConfig.learning_rate ({self.learning_rate}) must be in (0.0, 1.0]"
            )


class ActiveInferenceEngine:
    """
    Online generative model predicting PAD emotional transitions.
    """

    def __init__(self, config: Optional[ActiveInferenceConfig] = None) -> None:
        if config is None:
            config = ActiveInferenceConfig()
        config.__post_init__()
        self._config = config

        self._A: np.ndarray = np.eye(3, dtype=np.float64)
        self._b: np.ndarray = np.zeros(3, dtype=np.float64)
        self._I: np.ndarray = np.eye(3, dtype=np.float64)

    def reset(self) -> None:
        """
        Reset belief state back to identity matrix and zero bias.
        """
        self._A = np.eye(3, dtype=np.float64)
        self._b = np.zeros(3, dtype=np.float64)

    def get_belief_state(self) -> Dict[str, np.ndarray]:
        """
        Return the internal belief state matrices.
        """
        return {"A_matrix": self._A, "b_vector": self._b}

    def step(self, pad_before: PADState, pad_after: PADState) -> float:
        """
        Perform one inference step:
        1. Validates input bounds.
        2. Computes predicted next PAD state and prediction error.
        3. Updates belief state (A and b) via gradient descent with KL regularization.
        4. Clips A to [-2.0, 2.0].

        Returns
        -------
        float
            Pre-update prediction error (L2 norm).
        """
        # Validate input bounds
        for name, state in [("pad_before", pad_before), ("pad_after", pad_after)]:
            for dim, val in [
                ("pleasure", state.pleasure),
                ("arousal", state.arousal),
                ("dominance", state.dominance),
            ]:
                if not (-1.0 <= val <= 1.0):
                    raise ValueError(
                        f"{name}.{dim}={val} is outside valid range [-1.0, 1.0]"
                    )

        p = np.array(
            [pad_before.pleasure, pad_before.arousal, pad_before.dominance],
            dtype=np.float64,
        )
        q = np.array(
            [pad_after.pleasure, pad_after.arousal, pad_after.dominance],
            dtype=np.float64,
        )

        # Early exit if pad_before is zero vector
        if np.linalg.norm(p) == 0.0:
            return 0.0

        # Prediction: q_hat = A @ p + b
        predicted = self._A @ p + self._b
        delta = predicted - q
        pred_error = float(np.linalg.norm(delta))

        # Analytic gradients of Free Energy = ||A*p + b - q||^2 + kl_weight * ||A - I||_F^2
        # dFE/dA = 2 * delta * p^T + 2 * kl_weight * (A - I)
        # dFE/db = 2 * delta
        dFE_dA = 2.0 * np.outer(delta, p) + 2.0 * self._config.kl_weight * (
            self._A - self._I
        )
        dFE_db = 2.0 * delta

        # Gradient descent step
        lr = self._config.learning_rate
        self._A -= lr * dFE_dA
        self._b -= lr * dFE_db

        # Bounded invariant: clip A to [-2.0, 2.0]
        self._A = np.clip(self._A, -2.0, 2.0)

        return pred_error
