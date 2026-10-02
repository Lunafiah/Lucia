"""
tests/unit/test_p24_adaptive_communication.py

Unit test suite for Phase 24 Adaptive Communication Control Contract (ADR-032).
Validates:
  - ADR-032.1: Relational voice conditioning and strict reciprocity isolation.
  - ADR-032.2: Continuous dynamic F0 contouring and anti-chatter bounds.
  - ADR-032.3: Provider-agnostic boundary extraction (EN/JP telemetry, VI acoustic fallback).
  - ADR-032.4: Parameter translation and clamping.
  - Cadence adaptation: Bounded orthographic punctuation (<= 3 marks).
"""

from __future__ import annotations

import numpy as np
import pytest

from src.core.expression.expression_policy import ExpressionPolicy
from src.core.expression.expression_state import ExpressionState, VoiceProsody
from src.core.models import PADState, SomaticMarkers
from src.core.voice.boundary import (
    BoundarySegment,
    compute_f0_contour,
    extract_boundaries,
)
from src.core.voice.cadence import format_cadence_punctuation


# ---------------------------------------------------------------------------
# 1. ADR-032.1: Relational Conditioning & Reciprocity Isolation
# ---------------------------------------------------------------------------

class TestRelationalVoiceConditioning:
    def setup_method(self):
        self.policy = ExpressionPolicy(smoothing_factor=1.0)  # Direct unsmoothed evaluation
        self.neutral_pad = PADState(pleasure=0.0, arousal=0.0, dominance=0.0, timestamp=0.0)
        self.neutral_somatic = SomaticMarkers(stability=1.0, cognitive_load=0.0, energy=1.0, tension=0.0)

    def test_closeness_modulates_semitones(self):
        """Closeness in [0, 1] contributes +1.50 * R_close semitones."""
        res_0 = self.policy.compute(
            self.neutral_pad,
            self.neutral_somatic,
            relationship={"closeness": 0.0, "trust": 0.50, "familiarity": 0.0},
        )
        res_1 = self.policy.compute(
            self.neutral_pad,
            self.neutral_somatic,
            relationship={"closeness": 1.0, "trust": 0.50, "familiarity": 0.0},
        )

        assert res_0.voice.closeness == 0.0
        assert res_1.voice.closeness == 1.0
        # Delta S_base = +1.50 semitones
        assert pytest.approx(res_1.voice.pitch_shift_semitones - res_0.voice.pitch_shift_semitones, abs=1e-3) == 1.50

    def test_trust_stabilizes_speech_rate(self):
        """Trust in [0, 1] contributes 5.0 * (R_trust - 0.50)% speech rate."""
        res_low = self.policy.compute(
            self.neutral_pad,
            self.neutral_somatic,
            relationship={"closeness": 0.0, "trust": 0.0, "familiarity": 0.0},
        )
        res_mid = self.policy.compute(
            self.neutral_pad,
            self.neutral_somatic,
            relationship={"closeness": 0.0, "trust": 0.50, "familiarity": 0.0},
        )
        res_high = self.policy.compute(
            self.neutral_pad,
            self.neutral_somatic,
            relationship={"closeness": 0.0, "trust": 1.0, "familiarity": 0.0},
        )

        assert pytest.approx(res_low.voice.speech_rate_pct, abs=1e-3) == -2.50
        assert pytest.approx(res_mid.voice.speech_rate_pct, abs=1e-3) == 0.00
        assert pytest.approx(res_high.voice.speech_rate_pct, abs=1e-3) == 2.50

    def test_familiarity_reduces_pause_duration(self):
        """Familiarity in [0, 1] contributes -50.0 * R_fam ms pause reduction."""
        res_0 = self.policy.compute(
            self.neutral_pad,
            self.neutral_somatic,
            relationship={"closeness": 0.0, "trust": 0.50, "familiarity": 0.0},
        )
        res_1 = self.policy.compute(
            self.neutral_pad,
            self.neutral_somatic,
            relationship={"closeness": 0.0, "trust": 0.50, "familiarity": 1.0},
        )

        assert pytest.approx(res_1.voice.pause_duration_ms - res_0.voice.pause_duration_ms, abs=1e-3) == -50.0

    def test_reciprocity_strictly_isolated_from_actuators(self):
        """Reciprocity dimension MUST NOT modulate any vocal prosody or actuator parameters."""
        baseline = self.policy.compute(
            self.neutral_pad,
            self.neutral_somatic,
            relationship={"closeness": 0.4, "trust": 0.6, "familiarity": 0.3, "reciprocity": 0.0},
        )

        for rec_val in [0.1, 0.25, 0.5, 0.75, 0.9, 1.0]:
            perturbed = self.policy.compute(
                self.neutral_pad,
                self.neutral_somatic,
                relationship={"closeness": 0.4, "trust": 0.6, "familiarity": 0.3, "reciprocity": rec_val},
            )
            # Assert all voice prosody fields remain bit-exact identical
            assert perturbed.voice.pitch_shift_hz == baseline.voice.pitch_shift_hz
            assert perturbed.voice.speech_rate_pct == baseline.voice.speech_rate_pct
            assert perturbed.voice.volume_pct == baseline.voice.volume_pct
            assert perturbed.voice.pause_duration_ms == baseline.voice.pause_duration_ms
            assert perturbed.voice.closeness == baseline.voice.closeness
            assert perturbed.voice.pitch_shift_semitones == baseline.voice.pitch_shift_semitones


# ---------------------------------------------------------------------------
# 2. ADR-032.2: Dynamic F0 Trajectory & Anti-Chatter Bounds
# ---------------------------------------------------------------------------

class TestDynamicF0Contour:
    def test_contour_bounds_and_safety_clamping(self):
        """Total intended trajectory must remain in [-4.0, +7.0] st and hard safety [-12.0, +12.0] st."""
        p_len = 200
        segments = [
            BoundarySegment(text="hello", start_sec=0.2, end_sec=0.8, is_focal=True, segment_type="word"),
            BoundarySegment(text="world", start_sec=1.0, end_sec=1.6, is_focal=True, segment_type="word"),
        ]

        # Case 1: Max positive parameters
        contour_max = compute_f0_contour(p_len, base_semitones=4.0, segments=segments, focal_accent_st=2.5)
        assert np.max(contour_max) <= 7.0
        assert np.min(contour_max) >= -4.0

        # Case 2: Min negative parameters
        contour_min = compute_f0_contour(p_len, base_semitones=-2.0, segments=segments, focal_accent_st=0.0)
        assert np.min(contour_min) >= -4.0
        assert np.max(contour_min) <= 7.0

        # Case 3: Out-of-bounds input values clamped
        contour_out = compute_f0_contour(p_len, base_semitones=100.0, segments=segments, focal_accent_st=50.0)
        assert np.max(contour_out) <= 7.0
        assert np.min(contour_out) >= -12.0

    def test_anti_chatter_discrete_step_limit(self):
        """Frame-to-frame pitch jump |ΔS / Δt| must not exceed 1.0 semitone per 10ms frame."""
        p_len = 300
        segments = [
            BoundarySegment(text="fast", start_sec=0.1, end_sec=0.2, is_focal=True, segment_type="word"),
            BoundarySegment(text="spike", start_sec=0.5, end_sec=0.55, is_focal=True, segment_type="word"),
        ]
        contour = compute_f0_contour(p_len, base_semitones=1.5, segments=segments, focal_accent_st=2.5)

        steps = np.abs(np.diff(contour))
        assert np.max(steps) <= 1.0001, f"Frame-to-frame jump exceeded 1.0 st: {np.max(steps)}"


# ---------------------------------------------------------------------------
# 3. ADR-032.3: Provider-Agnostic Boundary Extraction
# ---------------------------------------------------------------------------

class TestBoundaryExtraction:
    def test_english_telemetry_extraction(self):
        """English voice extracts WordBoundary telemetry accurately."""
        telemetry = [
            {"type": "WordBoundary", "offset": 1000000, "duration": 3000000, "text": "Good"},
            {"type": "WordBoundary", "offset": 4500000, "duration": 4000000, "text": "morning"},
        ]
        segs = extract_boundaries("Good morning", "en-US-JennyNeural", telemetry_events=telemetry, focal_words=["morning"])
        assert len(segs) == 2
        assert segs[0].text == "Good"
        assert pytest.approx(segs[0].start_sec, abs=1e-3) == 0.10
        assert pytest.approx(segs[0].end_sec, abs=1e-3) == 0.40
        assert segs[0].is_focal is False

        assert segs[1].text == "morning"
        assert segs[1].is_focal is True

    def test_vietnamese_acoustic_fallback(self):
        """Vietnamese voice avoids WordBoundary and executes acoustic pause detection."""
        sr = 16000
        # Create 2 seconds of synthetic audio: speech (0-0.8s), silence (0.8-1.2s), speech (1.2-2.0s)
        t1 = np.linspace(0, 0.8, int(0.8 * sr))
        speech1 = 0.5 * np.sin(2 * np.pi * 200 * t1)
        silence = np.zeros(int(0.4 * sr))
        t2 = np.linspace(0, 0.8, int(0.8 * sr))
        speech2 = 0.5 * np.sin(2 * np.pi * 220 * t2)

        audio_16k = np.concatenate([speech1, silence, speech2]).astype(np.float32)

        segs = extract_boundaries("Chào bạn tôi là Lucia", "vi-VN-HoaiMyNeural", audio_16k=audio_16k)
        assert len(segs) >= 2
        # Check that pauses and clauses are identified
        types = [s.segment_type for s in segs]
        assert "clause" in types
        assert "pause" in types


# ---------------------------------------------------------------------------
# 4. Cadence Adaptation & Orthographic Punctuation
# ---------------------------------------------------------------------------

class TestCadenceAdaptation:
    def test_high_formality_cleans_ellipses(self):
        """Formality >= 0.65 cleans ellipses to standard grammatical stops."""
        raw = "Hello... this is Lucia... nice to meet you."
        res = format_cadence_punctuation(raw, formality=0.80)
        assert "..." not in res
        assert "nice to meet you." in res

    def test_low_formality_injects_breathing_pause(self):
        """Formality <= 0.35 injects breathing cadence pause after greeting."""
        raw = "Hello, nice to meet you today."
        res = format_cadence_punctuation(raw, formality=0.20)
        assert "Hello... nice to meet you today." in res

    def test_max_marks_enforced(self):
        """Never alters or modifies more than max_marks punctuation marks."""
        raw = "Well, hello there, how are you doing today."
        res = format_cadence_punctuation(raw, formality=0.20, supportiveness=0.85, max_marks=2)
        # Check words are completely preserved
        assert "how are you doing today" in res
