"""
src/core/relationship/signals.py

Structured interaction signals driving relationship updates.
In accordance with Phase 16 promotion decisions, production accepts explicit,
structured categorical signals to prevent unvalidated heuristic NLP runaway.
"""

from __future__ import annotations

import time
from dataclasses import dataclass, field
from enum import Enum
from typing import Dict, Optional

import numpy as np


class RelationshipSignalType(str, Enum):
    """Categorical interaction signals driving relationship updates."""
    COLLABORATIVE_SUCCESS = "COLLABORATIVE_SUCCESS"  # Successful shared task completion
    CASUAL_INTERACTION = "CASUAL_INTERACTION"        # Standard conversational contact
    EMOTIONAL_DISCLOSURE = "EMOTIONAL_DISCLOSURE"    # Shared vulnerability or depth
    CONFLICT_DISMISSAL = "CONFLICT_DISMISSAL"        # Friction, insult, or abrupt rejection
    REPAIR_ATTEMPT = "REPAIR_ATTEMPT"                # Collaborative reconciliation after conflict
    PROLONGED_ABSENCE = "PROLONGED_ABSENCE"          # Extended inactive calendar time


@dataclass
class RelationshipSignal:
    """
    Interaction-derived relational stimulus driving relationship updates.
    """
    signal_type: RelationshipSignalType
    delta_vector: np.ndarray  # shape (4,), in [-1.0, 1.0]
    intensity: float = 1.0    # scaling factor in [0.0, 1.0]
    timestamp: float = field(default_factory=time.time)

    @classmethod
    def create(cls, signal_type: RelationshipSignalType, intensity: float = 1.0) -> "RelationshipSignal":
        """Pre-calibrated empirical signal vectors."""
        intensity_clamped = max(0.0, min(1.0, float(intensity)))
        if signal_type == RelationshipSignalType.COLLABORATIVE_SUCCESS:
            # High trust and reciprocity, modest familiarity and closeness
            delta = np.array([0.20, 0.60, 0.30, 0.50], dtype=np.float64)
        elif signal_type == RelationshipSignalType.CASUAL_INTERACTION:
            # Steady familiarity, neutral trust and reciprocity
            delta = np.array([0.50, 0.10, 0.10, 0.10], dtype=np.float64)
        elif signal_type == RelationshipSignalType.EMOTIONAL_DISCLOSURE:
            # High closeness, modest trust and familiarity
            delta = np.array([0.30, 0.40, 0.80, 0.40], dtype=np.float64)
        elif signal_type == RelationshipSignalType.CONFLICT_DISMISSAL:
            # Sharp trust drop, closeness contraction
            delta = np.array([0.05, -0.70, -0.60, -0.40], dtype=np.float64)
        elif signal_type == RelationshipSignalType.REPAIR_ATTEMPT:
            # Rebuilding trust and reciprocity
            delta = np.array([0.10, 0.40, 0.20, 0.50], dtype=np.float64)
        elif signal_type == RelationshipSignalType.PROLONGED_ABSENCE:
            # Decay direction
            delta = np.array([-0.30, -0.05, -0.40, -0.20], dtype=np.float64)
        else:
            delta = np.zeros(4, dtype=np.float64)

        return cls(signal_type=signal_type, delta_vector=delta, intensity=intensity_clamped)
