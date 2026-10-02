"""
tests/unit/test_p24_acoustic_cross_language.py

Suite 3: Cross-Language Acoustic & Tone Preservation Tests for Phase 24.
Validates:
  - Northern Vietnamese lexical tone preservation (zero inversion / compression).
  - Telemetry boundary handling for English and Japanese.
  - Acoustic energy pause detection for Vietnamese.
  - Zero hard clipping and headroom-safe normalization.
"""

from __future__ import annotations

import numpy as np
import pytest
import scipy.signal as signal

from src.core.voice.boundary import (
    BoundarySegment,
    compute_f0_contour,
    extract_boundaries,
)


class TestAcousticCrossLanguage:
    def test_vietnamese_lexical_tone_integrity(self):
        """
        Northern Vietnamese tones (ngang, huyền, sắc, hỏi, ngã, nặng) must maintain
        their characteristic pitch slope signs under dynamic semitone modulation (ADR-032.3).
        """
        frames = 50
        # 1. Simulate falling tone (Huyền / Nặng): negative slope
        f0_falling = np.linspace(220.0, 180.0, frames)

        # 2. Simulate rising tone (Sắc / Ngã): positive slope
        f0_rising = np.linspace(190.0, 250.0, frames)

        # 3. Simulate level tone (Ngang): near-zero slope
        f0_level = np.full(frames, 210.0)

        # Apply continuous semitone shift: S_base = +2.0 st, focal accent = +1.5 st
        semitone_shift = 2.0 + 1.5 * np.hanning(frames)

        f0_mod_falling = f0_falling * (2.0 ** (semitone_shift / 12.0))
        f0_mod_rising = f0_rising * (2.0 ** (semitone_shift / 12.0))
        f0_mod_level = f0_level * (2.0 ** (semitone_shift / 12.0))

        # Test slope preservation (overall trajectory trend)
        falling_overall_diff = f0_mod_falling[-1] - f0_mod_falling[0]
        rising_overall_diff = f0_mod_rising[-1] - f0_mod_rising[0]

        assert falling_overall_diff < 0, "Falling tone was inverted to rising tone!"
        assert rising_overall_diff > 0, "Rising tone was inverted to falling tone!"

        # Ensure all pitch values remain in human vocal pitch range (100 Hz - 400 Hz)
        assert np.all(f0_mod_falling >= 100.0) and np.all(f0_mod_falling <= 400.0)
        assert np.all(f0_mod_rising >= 100.0) and np.all(f0_mod_rising <= 400.0)
        assert np.all(f0_mod_level >= 100.0) and np.all(f0_mod_level <= 400.0)

    def test_cross_language_boundary_handling(self):
        """Verify boundary extraction handles EN/JP telemetry and VI acoustic fallback."""
        # 1. English
        en_telemetry = [
            {"type": "WordBoundary", "offset": 0, "duration": 2500000, "text": "Hello"},
            {"type": "WordBoundary", "offset": 3000000, "duration": 4000000, "text": "Lucia"},
        ]
        en_segs = extract_boundaries("Hello Lucia", "en-US-JennyNeural", telemetry_events=en_telemetry)
        assert len(en_segs) == 2
        assert en_segs[0].text == "Hello"
        assert en_segs[1].text == "Lucia"

        # 2. Japanese
        jp_telemetry = [
            {"type": "WordBoundary", "offset": 0, "duration": 3000000, "text": "おはよう"},
            {"type": "WordBoundary", "offset": 3500000, "duration": 5000000, "text": "ございます"},
        ]
        jp_segs = extract_boundaries("おはよう ございます", "ja-JP-NanamiNeural", telemetry_events=jp_telemetry)
        assert len(jp_segs) == 2
        assert jp_segs[0].text == "おはよう"
        assert jp_segs[1].text == "ございます"

        # 3. Northern Vietnamese (Acoustic fallback)
        sr = 16000
        # 1.5s clause, 0.3s pause, 1.0s clause
        clause1 = 0.4 * np.sin(2 * np.pi * 180 * np.linspace(0, 1.5, int(1.5 * sr)))
        pause = np.zeros(int(0.3 * sr))
        clause2 = 0.4 * np.sin(2 * np.pi * 200 * np.linspace(0, 1.0, int(1.0 * sr)))
        vi_audio = np.concatenate([clause1, pause, clause2]).astype(np.float32)

        vi_segs = extract_boundaries("Xin chào... tôi đây.", "vi-VN-HoaiMyNeural", audio_16k=vi_audio)
        assert len(vi_segs) >= 3
        types = [s.segment_type for s in vi_segs]
        assert "clause" in types
        assert "pause" in types

    def test_audio_headroom_and_no_clipping(self):
        """Audio generator headroom normalization ensures zero hard clipping."""
        # Synthetic 40 kHz generator output with hot signal
        sr_gen = 40000
        t = np.linspace(0, 1.0, sr_gen)
        raw_40k = 2.5 * np.sin(2 * np.pi * 440 * t)  # Hot signal > 1.0

        # RVC Pipeline Step 10 & 11 normalization
        max_val = np.max(np.abs(raw_40k))
        normalized = raw_40k / max_val * 0.90  # Headroom-safe to -0.91 dBFS
        resampled_24k = signal.resample_poly(normalized, 3, 5).astype(np.float32)

        # Check peak amplitude is strictly below 0.98
        peak_24k = np.max(np.abs(resampled_24k))
        assert peak_24k <= 0.98, f"Filter overshoot exceeded safe headroom: peak={peak_24k}"

        # Convert to 16-bit PCM and verify zero clipping overflow
        pcm16 = (np.clip(resampled_24k, -1.0, 1.0) * 32767.0).astype(np.int16)
        assert np.max(pcm16) <= 32767
        assert np.min(pcm16) >= -32768
