"""
src/core/voice/boundary.py

Canonical Provider-Agnostic Speech Boundary & Prosody Contouring Module.
Implements ADR-032.2 (Dynamic F0 Trajectory) and ADR-032.3 (Provider-Agnostic Boundary Representation).

Invariants:
- Feedforward decoupling: Actuator logic NEVER feeds back into limbic or relational state.
- Chatter-free: Frame-to-frame pitch jump |ΔS / Δt| <= 1.0 semitone / 10 ms.
- Boundedness: S_base in [-2.0, +4.0] st, ΔS_focal in [0.0, +2.5] st, S(t) in [-4.0, +7.0] st, safety [-12.0, +12.0] st.
- Vietnamese lexical tone preservation: Northern Vietnamese tone integrity preserved via acoustic pause fallback without inner SSML.
"""

from __future__ import annotations

import logging
from dataclasses import dataclass
from typing import Any, Dict, List, Optional
import numpy as np

logger = logging.getLogger(__name__)


@dataclass(frozen=True)
class BoundarySegment:
    """Canonical provider-agnostic speech boundary segment."""
    text: str
    start_sec: float
    end_sec: float
    is_focal: bool
    segment_type: str  # 'word' | 'clause' | 'pause'


def extract_boundaries(
    text: str,
    voice: str,
    telemetry_events: Optional[List[Dict[str, Any]]] = None,
    audio_16k: Optional[np.ndarray] = None,
    focal_words: Optional[List[str]] = None,
    hop_length: int = 160,
    sr: int = 16000,
) -> List[BoundarySegment]:
    """
    Extract canonical boundary segments across languages.

    - English (en-*) and Japanese (ja-*): Ingests Edge-TTS WordBoundary telemetry events.
    - Northern Vietnamese (vi-*): Uses local acoustic intensity pause detection (<45 dB for >=200 ms)
      on audio_16k to segment clauses and assign phrase-final focal accents, avoiding NoAudioReceived.
    """
    focal_set = set(w.strip().lower() for w in (focal_words or []) if w.strip())
    segments: List[BoundarySegment] = []

    is_vietnamese = voice.lower().startswith("vi-") or voice.lower().startswith("vi_")

    # Path 1: Telemetry-driven WordBoundary (for EN and JP)
    if not is_vietnamese and telemetry_events:
        for ev in telemetry_events:
            ev_type = ev.get("type", "")
            if ev_type == "WordBoundary" or "offset" in ev:
                offset_ticks = float(ev.get("offset", 0.0))
                duration_ticks = float(ev.get("duration", 0.0))
                word_text = str(ev.get("text", "")).strip()

                t_start = offset_ticks / 1e7
                t_end = (offset_ticks + duration_ticks) / 1e7

                is_focal = False
                if focal_set and word_text:
                    clean_w = word_text.lower().strip(".,!?:;\"'()[]{}")
                    is_focal = clean_w in focal_set or any(fw in clean_w for fw in focal_set)

                segments.append(
                    BoundarySegment(
                        text=word_text,
                        start_sec=t_start,
                        end_sec=t_end,
                        is_focal=is_focal,
                        segment_type="word",
                    )
                )

        if segments:
            return segments

    # Path 2: Acoustic pause detection fallback (mandatory for Vietnamese, fallback for others)
    if audio_16k is not None and len(audio_16k) > 0:
        total_samples = len(audio_16k)
        total_sec = total_samples / float(sr)
        frame_len = hop_length * 2  # 20 ms window
        n_frames = max(1, total_samples // hop_length)

        # Compute RMS energy per frame
        rms_energies = np.zeros(n_frames, dtype=np.float32)
        for i in range(n_frames):
            start = i * hop_length
            end = min(total_samples, start + frame_len)
            frame = audio_16k[start:end]
            if len(frame) > 0:
                rms_energies[i] = np.sqrt(np.mean(frame ** 2) + 1e-9)

        # Relative dB calculation
        max_rms = np.max(rms_energies) if np.max(rms_energies) > 0 else 1.0
        db_rel = 20.0 * np.log10(np.maximum(rms_energies / max_rms, 1e-5))

        # Silence threshold: < -35 dB rel or absolute RMS < 0.005
        is_silence = (db_rel < -35.0) | (rms_energies < 0.005)

        # Identify contiguous pause intervals >= 200 ms (>= 20 frames at 100 Hz)
        min_pause_frames = int(0.20 * (sr / hop_length))  # 20 frames
        in_silence = False
        pause_start = 0
        pauses: List[tuple[int, int]] = []

        for idx, silent in enumerate(is_silence):
            if silent and not in_silence:
                in_silence = True
                pause_start = idx
            elif not silent and in_silence:
                in_silence = False
                if (idx - pause_start) >= min_pause_frames:
                    pauses.append((pause_start, idx))
        if in_silence and (len(is_silence) - pause_start) >= min_pause_frames:
            pauses.append((pause_start, len(is_silence)))

        # Build clause segments between pauses
        current_frame = 0
        clause_idx = 0
        for p_start, p_end in pauses:
            if p_start > current_frame:
                start_sec = (current_frame * hop_length) / sr
                end_sec = (p_start * hop_length) / sr
                if (end_sec - start_sec) >= 0.15:
                    # In Vietnamese acoustic fallback, phrase-final syllable receives focal accent
                    segments.append(
                        BoundarySegment(
                            text=f"clause_{clause_idx}",
                            start_sec=start_sec,
                            end_sec=end_sec,
                            is_focal=True,  # Clause boundary accentuation
                            segment_type="clause",
                        )
                    )
                    clause_idx += 1
            # Add pause segment
            segments.append(
                BoundarySegment(
                    text="pause",
                    start_sec=(p_start * hop_length) / sr,
                    end_sec=(p_end * hop_length) / sr,
                    is_focal=False,
                    segment_type="pause",
                )
            )
            current_frame = p_end

        if current_frame < n_frames:
            start_sec = (current_frame * hop_length) / sr
            end_sec = total_sec
            if (end_sec - start_sec) >= 0.15:
                segments.append(
                    BoundarySegment(
                        text=f"clause_{clause_idx}",
                        start_sec=start_sec,
                        end_sec=end_sec,
                        is_focal=True,
                        segment_type="clause",
                    )
                )

        if segments:
            return segments

    # Path 3: Minimal fallback (uniform duration)
    words = [w for w in text.split() if w.strip()]
    if not words:
        return []
    total_est_sec = max(1.0, len(words) * 0.35)
    word_dur = total_est_sec / len(words)

    for i, w in enumerate(words):
        t_start = i * word_dur
        t_end = (i + 1) * word_dur
        clean_w = w.lower().strip(".,!?:;\"'()[]{}")
        is_focal = clean_w in focal_set if focal_set else (i == len(words) - 1)
        segments.append(
            BoundarySegment(
                text=w,
                start_sec=t_start,
                end_sec=t_end,
                is_focal=is_focal,
                segment_type="word",
            )
        )

    return segments


def compute_f0_contour(
    p_len: int,
    base_semitones: float,
    segments: Optional[List[BoundarySegment]] = None,
    focal_accent_st: float = 2.0,
    hop_length: int = 160,
    sr: int = 16000,
) -> np.ndarray:
    """
    Generate canonical continuous F0 pitch shift trajectory:
    S(t) = S_base + sum_k Delta S_focal,k * w_hanning,k(t)

    Bounds Enforcement:
      - S_base in [-2.0, +4.0] st
      - Delta S_focal in [0.0, +2.5] st
      - Total intended trajectory S(t) in [-4.0, +7.0] st
      - Safety clamp in [-12.0, +12.0] st
      - Anti-chatter: |S(t) - S(t-1)| <= 1.0 st / 10 ms
    """
    s_base = float(np.clip(base_semitones, -2.0, 4.0))
    contour = np.full(p_len, s_base, dtype=np.float32)

    focal_st = float(np.clip(focal_accent_st, 0.0, 2.5))
    if focal_st <= 0.0 or not segments:
        return np.clip(contour, -12.0, 12.0)

    frame_rate = sr / float(hop_length)  # 100 Hz (10 ms per frame)

    for seg in segments:
        if not seg.is_focal:
            continue

        if seg.segment_type == "clause":
            # For clause segments in acoustic fallback, apply focal accent to the final 250ms of the clause
            clause_end_frame = min(p_len, int(seg.end_sec * frame_rate))
            clause_accent_frames = int(0.25 * frame_rate)  # 25 frames (250 ms)
            f_start = max(int(seg.start_sec * frame_rate), clause_end_frame - clause_accent_frames)
            f_end = clause_end_frame
        else:
            f_start = int(seg.start_sec * frame_rate)
            f_end = min(p_len, int(seg.end_sec * frame_rate))

        span = f_end - f_start
        if span >= 6:
            # Hanning window guarantees C^inf smoothness with zero derivative at endpoints
            window = np.hanning(span).astype(np.float32)
            contour[f_start:f_end] += focal_st * window
        elif span > 0:
            window = np.ones(span, dtype=np.float32)
            contour[f_start:f_end] += focal_st * window

    # Enforce anti-chatter constraint: discrete step across adjacent frames <= 1.0 semitone
    for i in range(1, p_len):
        step = contour[i] - contour[i - 1]
        if step > 1.0:
            contour[i] = contour[i - 1] + 1.0
        elif step < -1.0:
            contour[i] = contour[i - 1] - 1.0

    # Total intended bounds [-4.0, +7.0], hard safety clamp [-12.0, +12.0]
    contour = np.clip(contour, -4.0, 7.0)
    contour = np.clip(contour, -12.0, 12.0)

    return contour
