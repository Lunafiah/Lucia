"""
Data Schemas and Provenance Records for Phase 22-OLR.
Enforces strict provenance, metadata tracking, and field separation.
"""
from dataclasses import dataclass, field, asdict
from typing import Dict, List, Optional, Any
import numpy as np

@dataclass
class ObservationProvenance:
    candidate_id: str
    implementation_revision: str
    seed: int
    stress_regime: str
    language: str
    model_name: str
    execution_mode: str
    weights_provenance: str
    timestamp_iso: str

@dataclass
class ObservationOutput:
    # Semantic evidence vector in R^d_y
    evidence_vector: np.ndarray
    # Observation noise covariance matrix R in R^(d_y x d_y)
    noise_covariance: np.ndarray
    # Probability distribution on simplex if categorical, else normalized confidence vector
    probabilities: np.ndarray
    # Projected continuous user-state candidate z_obs in R^6
    projected_latent_state: np.ndarray
    # Confidence score [0, 1]
    confidence: float
    # Observation encoder latency (ms)
    encoder_latency_ms: float
    # Calibration/projection latency (ms)
    projection_latency_ms: float
    # Provenance
    provenance: ObservationProvenance

@dataclass
class FilterStepResult:
    turn: int
    # Prior state z_prior in R^6
    z_prior: np.ndarray
    # Updated state z_post in R^6
    z_post: np.ndarray
    # Updated covariance Sigma in R^(6x6)
    covariance_post: np.ndarray
    # Downstream P23 Interface vector psi_user in R^12
    psi_user: np.ndarray
    # True user state z* in R^6
    z_true: np.ndarray
    # Timing
    filter_latency_ms: float
    total_pipeline_latency_ms: float
    # Innovation vector (y - H z_prior)
    innovation: np.ndarray

@dataclass
class TrajectoryForecastResult:
    horizon: int
    forecast_mean: np.ndarray      # (horizon, 6)
    forecast_covariances: np.ndarray # (horizon, 6, 6)
    is_contained_in_ellipsoid: List[bool]
    log_det_ratio: float
