"""
src/core/relationship/state.py

Canonical 4-dimensional interpersonal relationship state vector R_t in [0.0, 1.0]^4.
Enforces strict bounds, independence from instantaneous affective state,
and temporal persistence across conversational turns.
"""

from __future__ import annotations

import time
from dataclasses import asdict, dataclass, field
from typing import Any, Dict, Optional

import numpy as np


@dataclass
class RelationshipState:
    """
    Minimal 4-dimensional relationship state vector R_t in [0.0, 1.0]^4.

    Dimensions (Engineering Variables):
      - familiarity:  Accumulated interaction exposure / volume [0.0, 1.0]
      - trust:        Stability and reliability of interaction expectations [0.0, 1.0]
      - closeness:    Relational proximity and shared context depth [0.0, 1.0]
      - reciprocity:  Degree of balanced, mutually sustained engagement [0.0, 1.0]
    """
    familiarity: float
    trust: float
    closeness: float
    reciprocity: float
    timestamp: float = field(default_factory=time.time)

    @classmethod
    def initial(cls) -> "RelationshipState":
        """Default neutral stranger baseline."""
        return cls(
            familiarity=0.0,
            trust=0.50,       # Initial neutral trust assumption
            closeness=0.0,     # Zero proximity at first contact
            reciprocity=0.50,  # Neutral reciprocity baseline
            timestamp=time.time(),
        )

    def to_array(self) -> np.ndarray:
        return np.array(
            [self.familiarity, self.trust, self.closeness, self.reciprocity],
            dtype=np.float64,
        )

    @classmethod
    def from_array(cls, arr: np.ndarray, timestamp: Optional[float] = None) -> "RelationshipState":
        clamped = np.clip(arr, 0.0, 1.0)
        return cls(
            familiarity=float(clamped[0]),
            trust=float(clamped[1]),
            closeness=float(clamped[2]),
            reciprocity=float(clamped[3]),
            timestamp=time.time() if timestamp is None else float(timestamp),
        )

    def is_bounded(self) -> bool:
        """Verify all coordinates strictly satisfy [0.0, 1.0]."""
        arr = self.to_array()
        return bool(np.all(arr >= -1e-9) and np.all(arr <= 1.0 + 1e-9))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "familiarity": float(self.familiarity),
            "trust": float(self.trust),
            "closeness": float(self.closeness),
            "reciprocity": float(self.reciprocity),
            "timestamp": float(self.timestamp),
        }

    @classmethod
    def from_dict(cls, d: Dict[str, Any]) -> "RelationshipState":
        return cls(
            familiarity=float(d.get("familiarity", 0.0)),
            trust=float(d.get("trust", 0.5)),
            closeness=float(d.get("closeness", 0.0)),
            reciprocity=float(d.get("reciprocity", 0.5)),
            timestamp=float(d.get("timestamp", time.time())),
        )
