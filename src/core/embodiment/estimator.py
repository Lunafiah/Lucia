"""
src/core/embodiment/estimator.py

Replaceable State Estimation Boundary for Phase 25.
Defines the `TemporalStateEstimator` protocol and implementations:
  1. `LeakyTemporalEstimator`: Discrete-time leaky integrator baseline.
  2. `BucyKalmanEstimator`: Candidate sensor-estimation mechanism derived from prior P22 evidence.

Epistemic Guardrail:
  Bucy-Kalman is explicitly documented as a candidate sensor-estimation mechanism
  derived from prior P22 evidence, NOT a canonical P22 mechanism, preserving canonical
  P22-XR and P22-EKF terminology.
"""

from __future__ import annotations

import logging
import threading
import time
from typing import Optional, Protocol, runtime_checkable

import numpy as np

from src.core.embodiment.contract import EstimatedTemporalState, TemporalObservation

logger = logging.getLogger(__name__)


@runtime_checkable
class TemporalStateEstimator(Protocol):
    """
    Modular estimation boundary decoupling raw sensory observations from internal state.
    """

    def update(self, observation: TemporalObservation) -> EstimatedTemporalState:
        """Process a new observation and return the updated state estimate."""
        ...

    def reset(self) -> None:
        """Reset estimator to default prior conditions."""
        ...


class LeakyTemporalEstimator:
    """
    Standard discrete-time leaky-integrator baseline.
    Estimates user latency and tempo ratio using exponential moving average:
      s_{t+1} = (1 - lambda) * s_t + lambda * x_t
    """

    def __init__(
        self,
        leakage: float = 0.20,
        default_latency_ms: float = 400.0,
        default_tempo_ratio: float = 1.0,
    ) -> None:
        self.leakage = float(np.clip(leakage, 0.05, 0.50))
        self.default_latency_ms = float(default_latency_ms)
        self.default_tempo_ratio = float(default_tempo_ratio)

        self._current_latency_ms = self.default_latency_ms
        self._current_tempo_ratio = self.default_tempo_ratio
        self._sample_count = 0
        self._lock = threading.Lock()

    def update(self, observation: TemporalObservation) -> EstimatedTemporalState:
        with self._lock:
            lam = self.leakage

            # If extensive idle time passed (>60s), relax partially toward default prior
            if observation.dt_idle_seconds > 60.0:
                relax_factor = min(1.0, observation.dt_idle_seconds / 300.0)
                self._current_latency_ms = (
                    (1.0 - relax_factor) * self._current_latency_ms
                    + relax_factor * self.default_latency_ms
                )
                self._current_tempo_ratio = (
                    (1.0 - relax_factor) * self._current_tempo_ratio
                    + relax_factor * self.default_tempo_ratio
                )

            # Update latency estimate with bounding [100, 3000] ms
            target_lat = float(np.clip(observation.user_latency_ms, 100.0, 3000.0))
            self._current_latency_ms = (1.0 - lam) * self._current_latency_ms + lam * target_lat

            # Update tempo ratio estimate with bounding [0.70, 1.30]
            target_tempo = float(np.clip(observation.speech_tempo_ratio, 0.70, 1.30))
            self._current_tempo_ratio = (1.0 - lam) * self._current_tempo_ratio + lam * target_tempo

            self._sample_count += 1
            confidence = min(1.0, self._sample_count / 5.0)

            # Rhythm stability is high when latency is consistent and pauses are normative
            latency_deviation = abs(self._current_latency_ms - target_lat) / max(1.0, self._current_latency_ms)
            rhythm_stability = float(np.clip(1.0 - latency_deviation, 0.10, 1.0))

            return EstimatedTemporalState(
                estimated_user_latency_ms=self._current_latency_ms,
                estimated_tempo_ratio=self._current_tempo_ratio,
                rhythm_stability=rhythm_stability,
                confidence=confidence,
                estimator_id="LeakyTemporalEstimator",
                timestamp=observation.timestamp,
            )

    def reset(self) -> None:
        with self._lock:
            self._current_latency_ms = self.default_latency_ms
            self._current_tempo_ratio = self.default_tempo_ratio
            self._sample_count = 0


class BucyKalmanEstimator:
    """
    Continuous-discrete linear Kalman filter observer.
    Designated strictly as a candidate sensor-estimation mechanism derived from prior P22 evidence.
    Tracks state vector x = [latency_ms, tempo_ratio]^T with estimation error covariance P.
    """

    def __init__(
        self,
        default_latency_ms: float = 400.0,
        default_tempo_ratio: float = 1.0,
        process_noise_q: float = 10.0,
        measurement_noise_r: float = 100.0,
    ) -> None:
        self.default_latency_ms = float(default_latency_ms)
        self.default_tempo_ratio = float(default_tempo_ratio)
        self.q = float(process_noise_q)
        self.r = float(measurement_noise_r)

        # State vector: [latency_ms, tempo_ratio]
        self._x = np.array([self.default_latency_ms, self.default_tempo_ratio], dtype=np.float64)
        # Covariance matrix P
        self._p = np.array([[100.0, 0.0], [0.0, 0.05]], dtype=np.float64)
        self._sample_count = 0
        self._lock = threading.Lock()

    def update(self, observation: TemporalObservation) -> EstimatedTemporalState:
        with self._lock:
            # 1. Prediction step
            # State transition matrix F is identity (random walk prior)
            # Process noise Q added based on dt_idle
            dt_factor = max(1.0, min(10.0, observation.dt_idle_seconds / 5.0))
            q_mat = np.array([[self.q * dt_factor, 0.0], [0.0, (self.q * 1e-4) * dt_factor]], dtype=np.float64)
            p_pred = self._p + q_mat

            # 2. Measurement update
            z = np.array([
                float(np.clip(observation.user_latency_ms, 100.0, 3000.0)),
                float(np.clip(observation.speech_tempo_ratio, 0.70, 1.30)),
            ], dtype=np.float64)

            # Measurement noise R
            r_mat = np.array([[self.r, 0.0], [0.0, self.r * 1e-4]], dtype=np.float64)

            # Kalman gain K = P_pred * (P_pred + R)^(-1)
            s_mat = p_pred + r_mat
            k_gain = p_pred @ np.linalg.inv(s_mat)

            # Innovation y = z - x_pred
            y_innov = z - self._x
            self._x = self._x + k_gain @ y_innov
            self._p = (np.eye(2) - k_gain) @ p_pred

            # Bounding clamp
            self._x[0] = float(np.clip(self._x[0], 100.0, 3000.0))
            self._x[1] = float(np.clip(self._x[1], 0.70, 1.30))

            self._sample_count += 1
            confidence = min(1.0, self._sample_count / 5.0)

            # Trace of covariance as uncertainty metric
            uncertainty = float(np.trace(self._p))
            stability = float(np.clip(1.0 / (1.0 + uncertainty / 100.0), 0.10, 1.0))

            return EstimatedTemporalState(
                estimated_user_latency_ms=self._x[0],
                estimated_tempo_ratio=self._x[1],
                rhythm_stability=stability,
                confidence=confidence,
                estimator_id="BucyKalmanEstimator (Candidate)",
                timestamp=observation.timestamp,
            )

    def reset(self) -> None:
        with self._lock:
            self._x = np.array([self.default_latency_ms, self.default_tempo_ratio], dtype=np.float64)
            self._p = np.array([[100.0, 0.0], [0.0, 0.05]], dtype=np.float64)
            self._sample_count = 0
