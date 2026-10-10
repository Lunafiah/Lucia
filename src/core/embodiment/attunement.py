"""
src/core/embodiment/attunement.py

Unilateral Bounded Social Attunement Engine for Phase 25.
Computes unilateral behavioral and expressive modulation based on estimated temporal state:
  - Injected pacing delay adjustments (clamped [0, 500] ms)
  - Speech tempo percentage modulation (clamped [-15.0%, +15.0%])
  - Pause duration modulation (clamped [-50.0, +100.0] ms)
  - Relational delta respecting ||W_rel||_2 <= 0.08 bound and 4D canonical representation

Safety & Governance Guardrails:
  - Anti-Sycophancy: Attunement modifies pacing and prosody only; it never compromises truth,
    reasons deceitfully, or alters facts to please the user.
  - Anti-Engagement Optimization: No retention gamification or reward maximization.
    When user or agent exhibits fatigue, attunement increases pause duration and rests.
"""

from __future__ import annotations

import logging
from typing import Optional

import numpy as np

from src.core.embodiment.contract import (
    MAX_PACING_DELAY_MS,
    MAX_PAUSE_MS_DELTA,
    MAX_PITCH_ST_DELTA,
    MAX_SPEECH_RATE_PCT_DELTA,
    MIN_PACING_DELAY_MS,
    MIN_PAUSE_MS_DELTA,
    MIN_PITCH_ST_DELTA,
    MIN_SPEECH_RATE_PCT_DELTA,
    P25_RELATIONAL_SPECTRAL_BOUND,
    EstimatedTemporalState,
    TemporalModulation,
)
from src.core.models import BehavioralConstraints, SomaticMarkers
from src.core.relationship.state import RelationshipState

logger = logging.getLogger(__name__)


class UnilateralAttunementEngine:
    """
    Computes unilateral temporal and social attunement modulations.
    """

    def __init__(
        self,
        nominal_target_latency_ms: float = 400.0,
        nominal_tempo_ratio: float = 1.0,
        pacing_gain: float = 0.15,
        tempo_gain: float = 10.0,
    ) -> None:
        self.nominal_target_latency_ms = float(nominal_target_latency_ms)
        self.nominal_tempo_ratio = float(nominal_tempo_ratio)
        self.pacing_gain = float(pacing_gain)
        self.tempo_gain = float(tempo_gain)

    def compute_modulation(
        self,
        estimated_state: EstimatedTemporalState,
        rel_state: Optional[RelationshipState] = None,
        somatic: Optional[SomaticMarkers] = None,
        base_constraints: Optional[BehavioralConstraints] = None,
    ) -> TemporalModulation:
        """
        Compute unilateral attunement modulation parameters.
        """
        # 1. Pacing delay modulation
        # If user latency is longer than nominal, Lucia slows down to match pacing;
        # if user latency is shorter, Lucia shortens pacing delay gently.
        lat_diff = estimated_state.estimated_user_latency_ms - self.nominal_target_latency_ms
        pacing_adjustment = int(self.pacing_gain * lat_diff * estimated_state.confidence)

        # Anti-engagement / homeostatic safeguard: if energy is depleted, inject extra pause delay
        if somatic is not None and somatic.energy < 0.30:
            pacing_adjustment += int(100.0 * (0.30 - somatic.energy))

        injected_pacing = int(np.clip(pacing_adjustment, MIN_PACING_DELAY_MS, MAX_PACING_DELAY_MS))

        # 2. Speech tempo modulation
        # Gentle entrainment toward user cadence ratio (clamped [-15%, +15%])
        tempo_diff = estimated_state.estimated_tempo_ratio - self.nominal_tempo_ratio
        speech_rate_delta = float(
            np.clip(
                self.tempo_gain * tempo_diff * estimated_state.confidence,
                MIN_SPEECH_RATE_PCT_DELTA,
                MAX_SPEECH_RATE_PCT_DELTA,
            )
        )

        # 3. Pause duration modulation
        # Longer pauses when rhythm stability is low or cognitive load is high
        pause_delta = 0.0
        if estimated_state.rhythm_stability < 0.50:
            pause_delta += 40.0 * (0.50 - estimated_state.rhythm_stability)
        if somatic is not None and somatic.cognitive_load > 0.70:
            pause_delta += 30.0 * (somatic.cognitive_load - 0.70)
        pause_delta = float(np.clip(pause_delta, MIN_PAUSE_MS_DELTA, MAX_PAUSE_MS_DELTA))

        # 4. Subtle prosodic pitch shift delta (clamped [-1.0, +1.0] semitones)
        # Warm subtle pitch lift if trust is high and rhythm is stable
        trust = rel_state.trust if rel_state else 0.50
        pitch_delta = 0.0
        if trust > 0.60 and estimated_state.rhythm_stability > 0.60:
            pitch_delta = min(0.50, 0.30 * (trust - 0.60) * estimated_state.rhythm_stability)
        pitch_delta = float(np.clip(pitch_delta, MIN_PITCH_ST_DELTA, MAX_PITCH_ST_DELTA))

        # 5. Relational delta respecting ||W_rel||_2 <= 0.08
        # High rhythm stability under comfortable pacing slightly nurtures familiarity and reciprocity
        # Strictly 4-dimensional: [familiarity, trust, closeness, reciprocity]
        rel_delta = np.zeros(4, dtype=np.float64)
        if estimated_state.confidence > 0.40 and estimated_state.rhythm_stability > 0.50:
            d_fam = 0.02 * estimated_state.confidence
            d_trust = 0.01 * (trust >= 0.50)
            d_close = 0.01 * (estimated_state.rhythm_stability > 0.70)
            d_rec = 0.02 * estimated_state.rhythm_stability
            raw_delta = np.array([d_fam, d_trust, d_close, d_rec], dtype=np.float64)
            norm = float(np.linalg.norm(raw_delta))
            if norm > P25_RELATIONAL_SPECTRAL_BOUND:
                raw_delta = raw_delta * (P25_RELATIONAL_SPECTRAL_BOUND / norm)
            rel_delta = raw_delta

        modulation = TemporalModulation(
            injected_pacing_delay_ms=injected_pacing,
            speech_rate_pct_delta=speech_rate_delta,
            pause_duration_ms_delta=pause_delta,
            pitch_shift_st_delta=pitch_delta,
            relational_signal_delta=rel_delta,
        )

        assert modulation.is_bounded(), "Attunement modulation violated bounds invariant"
        return modulation
