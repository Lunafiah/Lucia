"""
src/core/embodiment/contract.py

Authoritative Data Models and Boundary Contracts for Phase 25.
Defines the unilateral baseline data structures:
  External Interaction -> Temporal Observation -> State Estimation ->
  Temporal/Affective Dynamics -> Homeostatic + Bounded Relational Adaptation ->
  P24 Expression Conditioning -> Lucia Output.
"""

from __future__ import annotations

import time
from dataclasses import dataclass, field
from typing import Any, Dict, Optional

import numpy as np

# Strict Tier 2 Relational Attractor Spectral Bound
P25_RELATIONAL_SPECTRAL_BOUND: float = 0.08

# Pacing adjustment limits (ms)
MIN_PACING_DELAY_MS: int = 0
MAX_PACING_DELAY_MS: int = 500

# Speech rate percentage adjustment limits (%)
MIN_SPEECH_RATE_PCT_DELTA: float = -15.0
MAX_SPEECH_RATE_PCT_DELTA: float = 15.0

# Pause duration adjustment limits (ms)
MIN_PAUSE_MS_DELTA: float = -50.0
MAX_PAUSE_MS_DELTA: float = 100.0

# Pitch shift adjustment limits (semitones)
MIN_PITCH_ST_DELTA: float = -1.0
MAX_PITCH_ST_DELTA: float = 1.0


@dataclass(frozen=True)
class TemporalObservation:
    """
    Exogenous temporal observation extracted from incoming user turn.
    """
    timestamp: float
    dt_idle_seconds: float = 0.0
    user_latency_ms: float = 400.0
    speech_tempo_ratio: float = 1.0
    pause_duration_ms: float = 200.0
    turn_token_count: int = 10
    punct_density: float = 0.05

    def to_dict(self) -> Dict[str, Any]:
        return {
            "timestamp": float(self.timestamp),
            "dt_idle_seconds": float(self.dt_idle_seconds),
            "user_latency_ms": float(self.user_latency_ms),
            "speech_tempo_ratio": float(self.speech_tempo_ratio),
            "pause_duration_ms": float(self.pause_duration_ms),
            "turn_token_count": int(self.turn_token_count),
            "punct_density": float(self.punct_density),
        }


@dataclass(frozen=True)
class EstimatedTemporalState:
    """
    Estimated temporal/social interaction state produced by a replaceable estimator.
    """
    estimated_user_latency_ms: float
    estimated_tempo_ratio: float
    rhythm_stability: float  # [0.0, 1.0]
    confidence: float        # [0.0, 1.0]
    estimator_id: str
    timestamp: float = field(default_factory=time.time)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "estimated_user_latency_ms": float(self.estimated_user_latency_ms),
            "estimated_tempo_ratio": float(self.estimated_tempo_ratio),
            "rhythm_stability": float(self.rhythm_stability),
            "confidence": float(self.confidence),
            "estimator_id": str(self.estimator_id),
            "timestamp": float(self.timestamp),
        }


@dataclass(frozen=True)
class TemporalModulation:
    """
    Unilateral modulation signals applied to homeostatic constraints,
    P24 expression policy, and bounded relational updater.
    """
    injected_pacing_delay_ms: int
    speech_rate_pct_delta: float
    pause_duration_ms_delta: float
    pitch_shift_st_delta: float
    relational_signal_delta: np.ndarray  # shape (4,) in [-0.08, +0.08]

    def is_bounded(self) -> bool:
        """Verify strict adherence to all architectural bounds."""
        pacing_ok = MIN_PACING_DELAY_MS <= self.injected_pacing_delay_ms <= MAX_PACING_DELAY_MS
        rate_ok = MIN_SPEECH_RATE_PCT_DELTA <= self.speech_rate_pct_delta <= MAX_SPEECH_RATE_PCT_DELTA
        pause_ok = MIN_PAUSE_MS_DELTA <= self.pause_duration_ms_delta <= MAX_PAUSE_MS_DELTA
        pitch_ok = MIN_PITCH_ST_DELTA <= self.pitch_shift_st_delta <= MAX_PITCH_ST_DELTA

        # Verify relational delta is strictly 4D and satisfies spectral norm bound
        rel_shape_ok = self.relational_signal_delta.shape == (4,)
        rel_norm = float(np.linalg.norm(self.relational_signal_delta))
        rel_norm_ok = rel_norm <= (P25_RELATIONAL_SPECTRAL_BOUND + 1e-6)

        return bool(pacing_ok and rate_ok and pause_ok and pitch_ok and rel_shape_ok and rel_norm_ok)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "injected_pacing_delay_ms": int(self.injected_pacing_delay_ms),
            "speech_rate_pct_delta": float(self.speech_rate_pct_delta),
            "pause_duration_ms_delta": float(self.pause_duration_ms_delta),
            "pitch_shift_st_delta": float(self.pitch_shift_st_delta),
            "relational_signal_delta": [float(x) for x in self.relational_signal_delta],
            "bounded": self.is_bounded(),
        }


@dataclass(frozen=True)
class IdleDynamicsResult:
    """
    State adjustments produced by elapsed physical time during idle intervals.
    """
    dt_seconds: float
    pad_delta: np.ndarray          # shape (3,) relaxation toward Philia
    energy_replenishment: float    # increase in somatic energy
    tension_decay: float           # reduction in somatic tension
    relational_absence_hours: float
    dissipativity_diagnostic: float  # Tr(J) strictly as local volume-contraction diagnostic
