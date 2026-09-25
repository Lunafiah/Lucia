"""Deterministic Grounding Feature Extraction and Embodiment Mapping.

Transforms continuous multimodal inputs (PAD, eGeMAPS acoustic features) into
grounded sensory representations and drives physical embodiment parameters:
- Facial blendshape weights (Smile_W, Blink, Brow_Inner_Up)
- Voice prosodic shifts (Delta F0, Speaking Rate Factor)
- Somatic pacing delay (Pace Delay ms)
Without any intermediate natural language token sequence.
"""

from __future__ import annotations

import math
from typing import Any, Dict, Optional, Tuple


def extract_acoustic_arousal(
    f0: Optional[float],
    jitter: Optional[float],
    energy: Optional[float],
    rate: Optional[float],
) -> Optional[float]:
    """Computes acoustic arousal index in [-1.0, 1.0] from eGeMAPS prosody."""
    if f0 is None or energy is None:
        return None

    # Normalization: F0 baseline 180Hz (range 80-350Hz)
    f0_norm = max(-1.0, min(1.0, (f0 - 180.0) / 100.0))
    energy_norm = max(-1.0, min(1.0, energy * 2.0 - 1.0))
    jitter_val = jitter if jitter is not None else 0.01
    jitter_norm = max(0.0, min(1.0, jitter_val / 0.05))

    # Arousal is dominant in energy and pitch elevation
    arousal = 0.50 * energy_norm + 0.40 * f0_norm + 0.10 * (jitter_norm * 2.0 - 1.0)
    return round(max(-1.0, min(1.0, arousal)), 4)


def map_embodiment_parameters(
    valence: float,
    arousal: float,
    energy: float,
) -> Dict[str, float]:
    """Generates continuous physical embodiment parameters without an LLM.

    - smile_w: Facial smile blendshape weight in [0, 1]
    - pitch_shift_f0: Pitch modulation in Hz [-40, +40]
    - speaking_rate_factor: Multiplier for speech rate [0.8, 1.3]
    - pace_delay_ms: Latency injection in ms [0, 800]
    """
    # Valence directly drives facial smile blendshape
    smile_w = max(0.0, min(1.0, 0.50 + 0.50 * valence))

    # Arousal modulates fundamental frequency and speaking rate
    pitch_shift = max(-40.0, min(40.0, arousal * 35.0))
    rate_factor = max(0.80, min(1.30, 1.0 + 0.25 * arousal))

    # Low energy or negative valence injects somatic conversational delay
    delay_ms = max(0.0, (1.0 - energy) * 450.0 + max(0.0, -valence) * 350.0)

    return {
        "smile_w": round(smile_w, 4),
        "pitch_shift_f0": round(pitch_shift, 2),
        "speaking_rate_factor": round(rate_factor, 3),
        "pace_delay_ms": round(delay_ms, 1),
    }
