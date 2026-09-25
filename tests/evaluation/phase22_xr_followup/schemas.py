"""
Follow-up Schemas for Phase 22-XR Follow-Up Evaluation.
"""
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Any
import numpy as np

# Strict Provenance States
PROVENANCE_VERIFIED_BY_EXECUTION = "VERIFIED_BY_EXECUTION"
PROVENANCE_BLOCKED_OFFLINE_WEIGHTS = "BLOCKED_OFFLINE_WEIGHTS"
PROVENANCE_CLAIMED_BY_UPSTREAM = "CLAIMED_BY_UPSTREAM"
PROVENANCE_UNVERIFIED = "UNVERIFIED"

@dataclass
class ObservationResult:
    """Neutral observation primitive output contract."""
    probabilities: np.ndarray       # Probability simplex over options [M]
    confidence: float              # Calibrated confidence (max_p or normalized entropy)
    raw_logits: Optional[np.ndarray] = None
    latency_ms: float = 0.0
    provenance: str = PROVENANCE_UNVERIFIED
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
class TrajectoryDensityForecast:
    """Continuous predictive density forecast."""
    horizon: int
    mean_trajectory: List[np.ndarray]     # [z_hat(t+1), ..., z_hat(t+H)]
    cov_trajectory: List[np.ndarray]      # [P(t+1), ..., P(t+H)]
    log_generalized_variance: List[float] # [ln det(P(t+1)), ...]
    latency_us: float = 0.0
