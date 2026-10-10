"""
src/core/embodiment/coordinator.py

Phase 25 Temporal Embodiment Coordinator.
Coordinates the end-to-end unilateral baseline:
  Observation -> State Estimation -> Temporal Dynamics -> Bounded Social Attunement -> P24 Conditioning.
Thread-safe and decoupled.
"""

from __future__ import annotations

import logging
import threading
import time
from typing import Optional, Tuple

import numpy as np

from src.core.embodiment.attunement import UnilateralAttunementEngine
from src.core.embodiment.contract import (
    EstimatedTemporalState,
    IdleDynamicsResult,
    TemporalModulation,
    TemporalObservation,
)
from src.core.embodiment.dynamics import TemporalDynamicsEngine
from src.core.embodiment.estimator import (
    BucyKalmanEstimator,
    LeakyTemporalEstimator,
    TemporalStateEstimator,
)
from src.core.embodiment.temporal_observer import TemporalObserver
from src.core.models import BehavioralConstraints, PADState, SomaticMarkers
from src.core.relationship.state import RelationshipState

logger = logging.getLogger(__name__)


class TemporalEmbodimentCoordinator:
    """
    Main entry point coordinating Phase 25 temporal embodiment and social adaptation.
    """

    def __init__(
        self,
        observer: Optional[TemporalObserver] = None,
        estimator: Optional[TemporalStateEstimator] = None,
        dynamics: Optional[TemporalDynamicsEngine] = None,
        attunement: Optional[UnilateralAttunementEngine] = None,
        use_candidate_estimator: bool = False,
    ) -> None:
        self.observer = observer if observer is not None else TemporalObserver()

        if estimator is not None:
            self.estimator = estimator
        elif use_candidate_estimator:
            self.estimator = BucyKalmanEstimator()
        else:
            self.estimator = LeakyTemporalEstimator()

        self.dynamics = dynamics if dynamics is not None else TemporalDynamicsEngine()
        self.attunement = attunement if attunement is not None else UnilateralAttunementEngine()

        self._lock = threading.RLock()
        self._latest_observation: Optional[TemporalObservation] = None
        self._latest_estimated_state: Optional[EstimatedTemporalState] = None
        self._latest_modulation: Optional[TemporalModulation] = None

    def process_turn_start(
        self,
        current_timestamp: Optional[float] = None,
        user_text: str = "",
        explicit_user_latency_ms: Optional[float] = None,
        audio_duration_ms: Optional[float] = None,
        pause_duration_ms: Optional[float] = None,
        current_pad: Optional[PADState] = None,
        current_energy: float = 1.0,
        current_tension: float = 0.0,
    ) -> Tuple[TemporalObservation, EstimatedTemporalState, Optional[IdleDynamicsResult]]:
        """
        Executed at turn start: extracts temporal observation, steps idle dynamics,
        and updates temporal state estimation.
        """
        with self._lock:
            # 1. Observe incoming cues
            obs = self.observer.observe(
                current_timestamp=current_timestamp,
                user_text=user_text,
                explicit_user_latency_ms=explicit_user_latency_ms,
                audio_duration_ms=audio_duration_ms,
                pause_duration_ms=pause_duration_ms,
            )
            self._latest_observation = obs

            # 2. Idle dynamics if elapsed time passed
            idle_result: Optional[IdleDynamicsResult] = None
            if obs.dt_idle_seconds > 0.0 and current_pad is not None:
                idle_result = self.dynamics.step_idle(
                    dt_seconds=obs.dt_idle_seconds,
                    current_pad=current_pad,
                    current_energy=current_energy,
                    current_tension=current_tension,
                )

            # 3. Update state estimate
            est = self.estimator.update(obs)
            self._latest_estimated_state = est

            return obs, est, idle_result

    def compute_attunement_modulation(
        self,
        rel_state: Optional[RelationshipState] = None,
        somatic: Optional[SomaticMarkers] = None,
        base_constraints: Optional[BehavioralConstraints] = None,
    ) -> TemporalModulation:
        """
        Computes unilateral attunement modulation to adjust conversational pacing
        and downstream P24 expression parameters.
        """
        with self._lock:
            est = self._latest_estimated_state
            if est is None:
                # Fallback to default state if called without prior observation
                obs = TemporalObservation(timestamp=time.time())
                est = self.estimator.update(obs)
                self._latest_estimated_state = est

            mod = self.attunement.compute_modulation(
                estimated_state=est,
                rel_state=rel_state,
                somatic=somatic,
                base_constraints=base_constraints,
            )
            self._latest_modulation = mod
            return mod

    def get_latest_modulation(self) -> Optional[TemporalModulation]:
        with self._lock:
            return self._latest_modulation

    def reset(self) -> None:
        """Reset temporal state for clean lifecycle or testing."""
        with self._lock:
            self.observer.reset()
            self.estimator.reset()
            self._latest_observation = None
            self._latest_estimated_state = None
            self._latest_modulation = None
