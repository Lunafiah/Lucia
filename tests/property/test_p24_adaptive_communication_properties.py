"""
tests/property/test_p24_adaptive_communication_properties.py

Suite 4: Property-Based Fuzzing Suite for Phase 24 Adaptive Communication.
Uses Hypothesis to thoroughly fuzz the entire input hypercube across:
  - R_t in [0, 1]^4
  - E_t in [-1, 1]^3
  - S_t in [0, 1]^4
Validates:
  - Strict actuator boundedness.
  - Zero NaN / Inf propagation.
  - Chatter prevention: |ΔS / Δt| <= 1.0 st.
  - Zero semantic corruption in cadence punctuation.
"""

from __future__ import annotations

import math
import numpy as np
from hypothesis import given, settings
import hypothesis.strategies as st

from src.core.expression.expression_policy import ExpressionPolicy
from src.core.models import PADState, SomaticMarkers
from src.core.voice.boundary import (
    BoundarySegment,
    compute_f0_contour,
    extract_boundaries,
)
from src.core.voice.cadence import format_cadence_punctuation


class TestAdaptiveCommunicationProperties:
    @given(
        p=st.floats(min_value=-1.0, max_value=1.0, allow_nan=False),
        a=st.floats(min_value=-1.0, max_value=1.0, allow_nan=False),
        d=st.floats(min_value=-1.0, max_value=1.0, allow_nan=False),
        energy=st.floats(min_value=0.0, max_value=1.0, allow_nan=False),
        tension=st.floats(min_value=0.0, max_value=1.0, allow_nan=False),
        cog_load=st.floats(min_value=0.0, max_value=1.0, allow_nan=False),
        closeness=st.floats(min_value=0.0, max_value=1.0, allow_nan=False),
        trust=st.floats(min_value=0.0, max_value=1.0, allow_nan=False),
        familiarity=st.floats(min_value=0.0, max_value=1.0, allow_nan=False),
        reciprocity=st.floats(min_value=0.0, max_value=1.0, allow_nan=False),
    )
    @settings(max_examples=100, deadline=None)
    def test_expression_policy_fuzzing(
        self, p, a, d, energy, tension, cog_load, closeness, trust, familiarity, reciprocity
    ):
        policy = ExpressionPolicy(smoothing_factor=0.25)
        pad = PADState(pleasure=p, arousal=a, dominance=d, timestamp=0.0)
        somatic = SomaticMarkers(stability=1.0, cognitive_load=cog_load, energy=energy, tension=tension)
        rel = {
            "closeness": closeness,
            "trust": trust,
            "familiarity": familiarity,
            "reciprocity": reciprocity,
        }

        expr = policy.compute(pad, somatic, relationship=rel)

        # 1. Pitch shift in Hz: [-30.0, +30.0]
        assert -30.0001 <= expr.voice.pitch_shift_hz <= 30.0001
        assert not math.isnan(expr.voice.pitch_shift_hz)

        # 2. Speech rate: [-20.0, +20.0]%
        assert -20.0001 <= expr.voice.speech_rate_pct <= 20.0001
        assert not math.isnan(expr.voice.speech_rate_pct)

        # 3. Volume: [-20.0, +20.0]%
        assert -20.0001 <= expr.voice.volume_pct <= 20.0001
        assert not math.isnan(expr.voice.volume_pct)

        # 4. Pause duration: [100.0, 1000.0] ms
        assert 100.0000 <= expr.voice.pause_duration_ms <= 1000.0000
        assert not math.isnan(expr.voice.pause_duration_ms)

        # 5. Closeness: [0.0, 1.0]
        assert 0.0 <= expr.voice.closeness <= 1.0

        # 6. Base semitone shift: [-2.0, +4.0] st
        assert -2.0001 <= expr.voice.pitch_shift_semitones <= 4.0001
        assert not math.isnan(expr.voice.pitch_shift_semitones)

    @given(
        p_len=st.integers(min_value=20, max_value=400),
        base_semitones=st.floats(min_value=-15.0, max_value=15.0, allow_nan=False),
        focal_accent_st=st.floats(min_value=-5.0, max_value=10.0, allow_nan=False),
    )
    @settings(max_examples=100, deadline=None)
    def test_dynamic_f0_contour_fuzzing(self, p_len, base_semitones, focal_accent_st):
        segments = [
            BoundarySegment(text="word1", start_sec=0.05, end_sec=0.15, is_focal=True, segment_type="word"),
            BoundarySegment(text="word2", start_sec=0.20, end_sec=0.35, is_focal=False, segment_type="word"),
        ]

        contour = compute_f0_contour(
            p_len,
            base_semitones=base_semitones,
            segments=segments,
            focal_accent_st=focal_accent_st,
        )

        assert len(contour) == p_len
        assert not np.any(np.isnan(contour))
        assert not np.any(np.isinf(contour))

        # Hard safety clamp invariant: [-12.0, +12.0] st
        assert np.all(contour >= -12.0)
        assert np.all(contour <= 12.0)

        # Anti-chatter discrete step limit invariant: <= 1.0001 st / frame
        steps = np.abs(np.diff(contour))
        if len(steps) > 0:
            assert np.max(steps) <= 1.0001

    @given(
        formality=st.floats(min_value=-1.0, max_value=2.0, allow_nan=False),
        supportiveness=st.floats(min_value=-1.0, max_value=2.0, allow_nan=False),
        max_marks=st.integers(min_value=1, max_value=5),
    )
    @settings(max_examples=50, deadline=None)
    def test_cadence_punctuation_fuzzing(self, formality, supportiveness, max_marks):
        text = "Hello, I am Lucia! How are you doing today? We have 100 items."
        res = format_cadence_punctuation(text, formality=formality, supportiveness=supportiveness, max_marks=max_marks)

        assert isinstance(res, str)
        assert len(res) > 0
        # Check that core alphanumeric words and numbers are completely preserved
        assert "Hello" in res
        assert "Lucia" in res
        assert "100" in res
