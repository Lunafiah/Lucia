"""
src/core/expression/expression_state.py

Canonical 15-dimensional Multimodal Expression State E_t for Lucia Phase 16.
Strictly conforms to Phase 14 research model schema:
  - 3 Text dimensions (temperature_mod, verbosity_factor, formality_score)
  - 4 Voice prosody dimensions (pitch_shift_hz, speech_rate_pct, volume_pct, pause_duration_ms)
  - 5 Facial blendshape dimensions (smile, frown, eye_open, brow_angle, blush)
  - 2 Posture & Gaze dimensions (head_tilt_deg, gaze_aversion_prob)
  - 1 Latency modulation dimension (extra_latency_ms)
"""

from __future__ import annotations

from dataclasses import asdict, dataclass, field
from typing import Any, Dict, Optional

import numpy as np


@dataclass
class TextStyle:
    """Text generation register and stylistic conditioning (3 continuous dims)."""
    temperature_mod: float = 0.0   # [-0.20, +0.20]
    verbosity_factor: float = 1.0  # [0.50, 1.50]
    formality_score: float = 0.50  # [0.0, 1.0] (0 = informal/warm, 1 = strict/formal)
    cadence_style: str = "balanced"  # "concise", "balanced", "expansive"

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)

    @classmethod
    def from_dict(cls, d: Dict[str, Any]) -> "TextStyle":
        return cls(**d)


@dataclass
class VoiceProsody:
    """Acoustic speech synthesis and prosody parameters."""
    pitch_shift_hz: float = 0.0          # [-30.0, +30.0]
    speech_rate_pct: float = 0.0         # [-20.0, +20.0]
    volume_pct: float = 0.0              # [-20.0, +20.0]
    pause_duration_ms: float = 200.0     # [100.0, 1000.0]
    closeness: float = 0.0               # [0.0, 1.0] relational closeness
    pitch_shift_semitones: float = 0.0   # [-2.0, +4.0] base semitone shift

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)

    @classmethod
    def from_dict(cls, d: Dict[str, Any]) -> "VoiceProsody":
        return cls(**d)



@dataclass
class FacialExpression:
    """Facial blendshape and expression morph targets (5 continuous dims)."""
    smile: float = 0.25      # [0.0, 1.0]
    frown: float = 0.0       # [0.0, 1.0]
    eye_open: float = 0.80   # [0.30, 1.20]
    brow_angle: float = 0.0  # [-0.50, +0.50]
    blush: float = 0.15      # [0.0, 1.0]

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)

    @classmethod
    def from_dict(cls, d: Dict[str, Any]) -> "FacialExpression":
        return cls(**d)


@dataclass
class PostureGaze:
    """Embodied bodily stance and ocular gaze parameters (2 continuous dims)."""
    head_tilt_deg: float = 0.0        # [-10.0, +10.0]
    gaze_aversion_prob: float = 0.10  # [0.0, 1.0]

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)

    @classmethod
    def from_dict(cls, d: Dict[str, Any]) -> "PostureGaze":
        return cls(**d)


@dataclass
class ExpressionState:
    """
    Multimodal Expression State E_t.
    Maps internal affect and somatic state into feedforward actuator parameters.
    Has exact 15 continuous bounded dimensions.
    """
    text: TextStyle = field(default_factory=TextStyle)
    voice: VoiceProsody = field(default_factory=VoiceProsody)
    facial: FacialExpression = field(default_factory=FacialExpression)
    posture_gaze: PostureGaze = field(default_factory=PostureGaze)
    extra_latency_ms: float = 0.0
    semantic_safe: bool = True
    provenance: str = "ExpressionPolicy/v1"

    def to_vector(self) -> np.ndarray:
        """Flatten continuous parameters to 15-dimensional normalized vector."""
        return np.array(
            [
                self.text.temperature_mod,
                self.text.verbosity_factor,
                self.text.formality_score,
                self.voice.pitch_shift_hz / 30.0,
                self.voice.speech_rate_pct / 25.0,
                self.voice.volume_pct / 20.0,
                (self.voice.pause_duration_ms - 100.0) / 900.0,
                self.facial.smile,
                self.facial.frown,
                (self.facial.eye_open - 0.3) / 0.9,
                (self.facial.brow_angle + 0.5) / 1.0,
                self.facial.blush,
                (self.posture_gaze.head_tilt_deg + 10.0) / 20.0,
                self.posture_gaze.gaze_aversion_prob,
                self.extra_latency_ms / 500.0,
            ],
            dtype=np.float64,
        )

    def is_bounded(self) -> bool:
        """Verify all parameters strictly conform to their domain bounds."""
        t = self.text
        v = self.voice
        f = self.facial
        pg = self.posture_gaze

        if not (-0.20 <= t.temperature_mod <= 0.20):
            return False
        if not (0.50 <= t.verbosity_factor <= 1.50):
            return False
        if not (0.0 <= t.formality_score <= 1.0):
            return False

        if not (-30.0 <= v.pitch_shift_hz <= 30.0):
            return False
        if not (-25.0 <= v.speech_rate_pct <= 25.0):
            return False
        if not (-20.0 <= v.volume_pct <= 20.0):
            return False
        if not (100.0 <= v.pause_duration_ms <= 1000.0):
            return False

        if not (0.0 <= f.smile <= 1.0):
            return False
        if not (0.0 <= f.frown <= 1.0):
            return False
        if not (0.30 <= f.eye_open <= 1.20):
            return False
        if not (-0.50 <= f.brow_angle <= 0.50):
            return False
        if not (0.0 <= f.blush <= 1.0):
            return False

        if not (-10.0 <= pg.head_tilt_deg <= 10.0):
            return False
        if not (0.0 <= pg.gaze_aversion_prob <= 1.0):
            return False

        if not (0.0 <= self.extra_latency_ms <= 500.0):
            return False

        return True

    def to_dict(self) -> Dict[str, Any]:
        return {
            "text": self.text.to_dict(),
            "voice": self.voice.to_dict(),
            "facial": self.facial.to_dict(),
            "posture_gaze": self.posture_gaze.to_dict(),
            "extra_latency_ms": float(self.extra_latency_ms),
            "semantic_safe": bool(self.semantic_safe),
            "provenance": str(self.provenance),
        }

    @classmethod
    def from_dict(cls, d: Dict[str, Any]) -> "ExpressionState":
        return cls(
            text=TextStyle.from_dict(d.get("text", {})),
            voice=VoiceProsody.from_dict(d.get("voice", {})),
            facial=FacialExpression.from_dict(d.get("facial", {})),
            posture_gaze=PostureGaze.from_dict(d.get("posture_gaze", {})),
            extra_latency_ms=float(d.get("extra_latency_ms", 0.0)),
            semantic_safe=bool(d.get("semantic_safe", True)),
            provenance=str(d.get("provenance", "from_dict")),
        )
