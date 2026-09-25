"""
Data schemas and interfaces for Phase 22 Observation Layer Study.
"""
from dataclasses import dataclass, field
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
class ContinuousObservationResult:
    evidence_vector: np.ndarray      # y in R^d_y
    noise_covariance: np.ndarray     # R in R^(d_y x d_y)
    probabilities: np.ndarray        # probs in Delta^(K-1) or normalized
    projected_state: np.ndarray      # z_obs in R^6
    confidence: float                # [0, 1]
    encoder_latency_ms: float
    projection_latency_ms: float
    provenance: ObservationProvenance

@dataclass
class UserStateUpdateResult:
    turn: int
    z_prior: np.ndarray              # R^6
    z_post: np.ndarray               # R^6
    covariance_post: np.ndarray      # R^(6x6)
    psi_user: np.ndarray             # R^12
    filter_latency_ms: float
    total_pipeline_latency_ms: float
    innovation: np.ndarray           # R^6
    is_finite: bool
    is_bounded: bool
