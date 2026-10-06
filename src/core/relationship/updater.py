"""
src/core/relationship/updater.py

High-inertia relationship dynamics engine for Lucia Phase 16.
Enforces tau_rel >> tau_turn with bounded learning and decay rates.
Thread-safe and decoupled between turn read (Stage 9) and post-turn update (Stage 16).
"""

from __future__ import annotations

import logging
import threading
import time
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple, Union

import numpy as np

from src.core.relationship.persistence import load_relationship, save_relationship
from src.core.relationship.signals import RelationshipSignal, RelationshipSignalType
from src.core.relationship.state import RelationshipState

logger = logging.getLogger(__name__)


@dataclass
class RelationshipHistoryEntry:
    """Audit log entry capturing exact causal attribution for every update."""
    step: int
    timestamp: float
    prior_state: RelationshipState
    signal: RelationshipSignal
    posterior_state: RelationshipState
    effective_delta: np.ndarray

    def to_dict(self) -> Dict[str, Any]:
        return {
            "step": self.step,
            "timestamp": self.timestamp,
            "prior_state": self.prior_state.to_dict(),
            "signal_type": self.signal.signal_type.value,
            "signal_intensity": float(self.signal.intensity),
            "posterior_state": self.posterior_state.to_dict(),
            "effective_delta": [float(x) for x in self.effective_delta],
        }


class RelationshipUpdater:
    """
    High-inertia relationship dynamics engine.
    Enforces tau_rel >> tau_turn with bounded learning and decay rates.
    Thread-safe and decoupled between read (Stage 9) and update (Stage 16).
    """

    def __init__(
        self,
        alpha: float = 0.03,        # Bounded learning rate (high inertia: ~3% per salient turn)
        decay_rate: float = 0.005,   # Slow absence decay rate
        storage_path: Optional[Union[str, Path]] = None,
        initial_state: Optional[RelationshipState] = None,
    ) -> None:
        self.alpha = float(alpha)
        self.decay_rate = float(decay_rate)
        self.storage_path = Path(storage_path) if storage_path else None
        self._lock = threading.RLock()
        self.history: List[RelationshipHistoryEntry] = []
        self._step_counter: int = 0

        with self._lock:
            if initial_state is not None:
                self._current_state = initial_state
            elif self.storage_path is not None and self.storage_path.exists():
                self._current_state = load_relationship(self.storage_path)
            else:
                self._current_state = RelationshipState.initial()

    def get_state(self) -> RelationshipState:
        """Read current relationship state snapshot under lock (Stage 9 read)."""
        with self._lock:
            # Return fresh copy
            return RelationshipState.from_dict(self._current_state.to_dict())

    def step(
        self,
        current_state: Optional[RelationshipState] = None,
        signal: Optional[RelationshipSignal] = None,
        dt_absence_hours: float = 0.0,
        epoch_id: Optional[int] = None,
    ) -> Tuple[RelationshipState, RelationshipHistoryEntry]:
        """
        Execute single relationship update step (Stage 16 update):
          R_{t+1} = clip( R_t + alpha * intensity * delta - decay_rate * dt * D_neutral, 0.0, 1.0 )
        """
        if signal is None:
            signal = RelationshipSignal.create(RelationshipSignalType.CASUAL_INTERACTION, intensity=0.0)

        with self._lock:
            base_state = current_state if current_state is not None else self._current_state
            curr_arr = base_state.to_array()

            # 1. Interaction accumulation term
            interaction_delta = self.alpha * signal.intensity * signal.delta_vector

            # 2. Absence decay term (decays toward neutral baseline: [0.0, 0.5, 0.0, 0.5])
            neutral_baseline = np.array([0.0, 0.50, 0.0, 0.50], dtype=np.float64)
            decay_factor = min(1.0, self.decay_rate * max(0.0, float(dt_absence_hours)))
            decay_delta = decay_factor * (curr_arr - neutral_baseline)

            # 3. New state synthesis with hard bounding [0.0, 1.0]
            new_arr = np.clip(curr_arr + interaction_delta - decay_delta, 0.0, 1.0)
            new_state = RelationshipState.from_array(new_arr)

            effective_delta = new_arr - curr_arr

            self._step_counter += 1
            entry = RelationshipHistoryEntry(
                step=self._step_counter,
                timestamp=time.time(),
                prior_state=base_state,
                signal=signal,
                posterior_state=new_state,
                effective_delta=effective_delta,
            )
            self.history.append(entry)
            self._current_state = new_state

            # Optional persistence
            if self.storage_path:
                try:
                    save_relationship(
                        state=new_state,
                        history=[h.to_dict() for h in self.history[-50:]],
                        filepath=self.storage_path,
                        epoch_id=epoch_id,
                    )
                except Exception as e:
                    logger.warning("Failed to persist relationship update: %s", e)

            return new_state, entry

    def save(
        self,
        filepath: Optional[Union[str, Path]] = None,
        epoch_id: Optional[int] = None,
    ) -> Optional[Path]:
        """Atomically persist current relationship state and history."""
        target = Path(filepath) if filepath else self.storage_path
        if not target:
            return None
        with self._lock:
            return save_relationship(
                state=self._current_state,
                history=[h.to_dict() for h in self.history[-50:]],
                filepath=target,
                epoch_id=epoch_id,
            )
