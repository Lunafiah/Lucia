"""
Shared frozen dataclasses for Lucia Core Phase 1.

These are the canonical data types passed between all pipeline modules.
No module should define its own copy of these types.
"""

from __future__ import annotations

import time
from dataclasses import dataclass
from datetime import datetime


@dataclass(frozen=True)
class PADState:
    """
    Three-dimensional continuous emotional state in PAD space.

    All dimensions are bounded to [-1.0, 1.0]:
      - pleasure:   valence of the current interaction
      - arousal:    activation / intensity level
      - dominance:  sense of control in context
      - timestamp:  monotonic time (time.monotonic()) of the last update
    """

    pleasure: float
    arousal: float
    dominance: float
    timestamp: float

    @classmethod
    def resting(
        cls,
        pleasure: float = 0.1,
        arousal: float = 0.0,
        dominance: float = 0.0,
    ) -> "PADState":
        """Return a resting-baseline PADState with the current monotonic timestamp."""
        return cls(
            pleasure=pleasure,
            arousal=arousal,
            dominance=dominance,
            timestamp=time.monotonic(),
        )

    def to_dict(self) -> dict[str, float]:
        """Return dictionary representation of PADState."""
        return {
            "pleasure": float(self.pleasure),
            "arousal": float(self.arousal),
            "dominance": float(self.dominance),
            "timestamp": float(self.timestamp),
        }


@dataclass(frozen=True)
class SomaticMarkers:
    """
    Four derived scalar values computed from PADState by the HomeostaticEngine.

    All values are bounded to [0.0, 1.0]:
      - stability:       overall system equilibrium
      - cognitive_load:  accumulated processing burden
      - energy:          available response capacity
      - tension:         conflict between incoming stimulus and current pleasure
    """

    stability: float
    cognitive_load: float
    energy: float
    tension: float


@dataclass(frozen=True)
class BehavioralConstraints:
    """
    Generation parameters derived from SomaticMarkers by the HomeostaticEngine.

    These directly condition LLM_Backend calls:
      - max_tokens:      maximum tokens to generate (int, 1–2048)
      - temperature:     sampling temperature (float, 0.0–2.0)
      - latency_ms:      artificial delay before generation (int, 0–5000)
      - reasoning_depth: chain-of-thought depth (int, 0–3)
    """

    max_tokens: int
    temperature: float
    latency_ms: int
    reasoning_depth: int


# Sentinel default — no threshold condition active (Requirement 3.10)
_DEFAULT_CONSTRAINTS = BehavioralConstraints(
    max_tokens=150,
    temperature=0.75,
    latency_ms=0,
    reasoning_depth=1,
)


def default_behavioral_constraints() -> BehavioralConstraints:
    """Return the default BehavioralConstraints (no threshold condition active)."""
    return _DEFAULT_CONSTRAINTS


@dataclass
class SoftBlockEvent:
    """
    Record of a single Boundary_Layer Soft_Block substitution event.

    Logged whenever a Meta-Self-Awareness_Pattern is detected and replaced.
    """

    pattern_matched: str
    original_span: str
    substituted_text: str
    utc_timestamp: datetime
