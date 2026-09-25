"""
P22-XR Schemas: Data structures for isolated evaluation harness.
"""
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Any
import numpy as np

@dataclass
class ObservationResult:
    """Neutral observation primitive output contract."""
    probabilities: np.ndarray       # Probability simplex over options [k] or multi-probe [M]
    confidence: float              # Calibrated confidence (max_p or normalized entropy)
    raw_logits: Optional[np.ndarray] = None
    latency_ms: float = 0.0
    status: str = "SUCCESS"        # SUCCESS, DEGRADED, BLOCKED, NOT_AVAILABLE
    metadata: Dict[str, Any] = field(default_factory=dict)

@dataclass
class SimUserStep:
    """Environment step output containing ground truth, emission, and metadata."""
    turn: int
    true_latent_state: np.ndarray  # z*(t) in R^6
    utterance: str
    acoustic_features: np.ndarray  # x^obs in R^6
    true_intent: str
    true_intent_idx: int
    ds_regime: str
    episode_id: int
    metadata: Dict[str, Any] = field(default_factory=dict)

@dataclass
class ContinuousBeliefState:
    """Continuous user belief state representation."""
    z_mean: np.ndarray             # Mean estimate in R^6
    covariance: np.ndarray         # Uncertainty covariance P in R^(6x6)
    timestamp: float = 0.0

@dataclass
class DiscreteBeliefState:
    """Discrete Bayesian belief representation."""
    b_simplex: np.ndarray          # Probability over discrete states (e.g., Delta^4)
    dominant_state_idx: int

@dataclass
class TrajectoryDensityForecast:
    """Continuous predictive density forecast."""
    horizon: int
    mean_trajectory: List[np.ndarray]     # [z_hat(t+1), ..., z_hat(t+H)]
    cov_trajectory: List[np.ndarray]      # [P(t+1), ..., P(t+H)]
    latency_us: float = 0.0

@dataclass
class DiscreteTreeForecast:
    """Discrete tree forecast."""
    horizon: int
    branching_factor: int
    leaves_count: int
    leaf_paths: List[List[int]]
    leaf_probabilities: List[float]
    latency_us: float = 0.0

@dataclass
class IntentPredictionResult:
    """Intent prediction or interpretation result."""
    predicted_intent: str
    predicted_intent_idx: int
    top2_indices: List[int]
    probabilities: np.ndarray      # over 8 intent classes
    mode: str                      # "prospective" or "post_observation"
