"""
src/core/embodiment/__init__.py

Phase 25 — Temporal Embodiment & Social Feedback Subsystem.
Implements the canonical unilateral baseline of temporal continuity, multi-timescale
state dynamics, bounded social attunement, and P24 expression conditioning.

Invariants:
  - Canonical 4D R_t in [0.0, 1.0]^4 (familiarity, trust, closeness, reciprocity).
  - Unilateral adaptation only: observed user signal -> state estimation -> adaptation.
  - Reciprocal coupling is strictly unproven (C2 BLOCKED, H-B UNPROVEN; synchrony != causality).
  - Zero reflective ego (INV-2); zero cloud dependencies (INV-5); Genesis gate bit-exact (INV-8).
"""

from src.core.embodiment.attunement import UnilateralAttunementEngine
from src.core.embodiment.contract import (
    EstimatedTemporalState,
    P25_RELATIONAL_SPECTRAL_BOUND,
    TemporalModulation,
    TemporalObservation,
)
from src.core.embodiment.coordinator import TemporalEmbodimentCoordinator
from src.core.embodiment.dynamics import TemporalDynamicsEngine
from src.core.embodiment.estimator import (
    BucyKalmanEstimator,
    LeakyTemporalEstimator,
    TemporalStateEstimator,
)
from src.core.embodiment.temporal_observer import TemporalObserver

__all__ = [
    "TemporalObservation",
    "EstimatedTemporalState",
    "TemporalModulation",
    "P25_RELATIONAL_SPECTRAL_BOUND",
    "TemporalObserver",
    "TemporalStateEstimator",
    "LeakyTemporalEstimator",
    "BucyKalmanEstimator",
    "TemporalDynamicsEngine",
    "UnilateralAttunementEngine",
    "TemporalEmbodimentCoordinator",
]
