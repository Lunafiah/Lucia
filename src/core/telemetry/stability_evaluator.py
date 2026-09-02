"""Limbic Stability Evaluator and Health Monitoring Engine."""
import math
import threading
import time
from collections import deque
from dataclasses import asdict, dataclass
from typing import Any, Deque, Dict, List, Optional
import numpy as np


@dataclass
class StabilitySnapshot:
    """Statistical snapshot of Lucia's runtime and emotional stability."""
    lsi: float  # Limbic Stability Index in [0.0, 1.0]
    status: str  # "nominal", "recovering", "degraded"
    fast_loop_jitter_mean_ms: float
    fast_loop_jitter_max_ms: float
    ode_velocity_variance: float
    free_energy_surprise_mean: float
    free_energy_surprise_std: float
    sdm_saturation_pct: float
    recovery_count: int
    uptime_seconds: float
    timestamp: float

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


class StabilityEvaluator:
    """Continuously evaluates Fast-Loop timing, ODE divergence, and prediction surprise."""

    def __init__(
        self,
        nominal_tick_ms: float = 200.0,
        window_size: int = 100,
        max_sdm_capacity: int = 1000,
    ) -> None:
        self._nominal_tick_s = nominal_tick_ms / 1000.0
        self._window_size = window_size
        self._max_sdm_capacity = max_sdm_capacity
        self._start_time = time.monotonic()
        self._lock = threading.Lock()

        # Rolling buffers
        self._tick_times: Deque[float] = deque(maxlen=window_size)
        self._velocities: Deque[float] = deque(maxlen=window_size)
        self._surprises: Deque[float] = deque(maxlen=window_size)

        # Trackers
        self._last_tick_time: Optional[float] = None
        self._last_hidden_norm: Optional[float] = None
        self._recovery_count: int = 0
        self._last_sdm_count: int = 0

    def record_tick(self, hidden_state_norm: Optional[float] = None) -> None:
        """Record a Fast-Loop ODE tick."""
        now = time.monotonic()
        with self._lock:
            if self._last_tick_time is not None:
                dt = now - self._last_tick_time
                self._tick_times.append(dt)

                if hidden_state_norm is not None and self._last_hidden_norm is not None and dt > 0:
                    v = abs(hidden_state_norm - self._last_hidden_norm) / dt
                    self._velocities.append(v)

            self._last_tick_time = now
            if hidden_state_norm is not None:
                self._last_hidden_norm = hidden_state_norm

    def record_surprise(self, surprise_value: float) -> None:
        """Record a prediction surprise value from Active Inference."""
        with self._lock:
            if not math.isnan(surprise_value) and not math.isinf(surprise_value):
                self._surprises.append(float(surprise_value))

    def update_sdm_count(self, count: int) -> None:
        """Update active SDM memory count."""
        with self._lock:
            self._last_sdm_count = max(0, count)

    def record_recovery_event(self) -> None:
        """Record an automatic ODE stall or numerical recovery event."""
        with self._lock:
            self._recovery_count += 1

    def get_snapshot(self) -> StabilitySnapshot:
        """Compute and return the current stability snapshot."""
        now = time.monotonic()
        with self._lock:
            uptime = now - self._start_time

            # 1. Jitter
            if len(self._tick_times) >= 2:
                diffs = [abs(dt - self._nominal_tick_s) * 1000.0 for dt in self._tick_times]
                jitter_mean = float(np.mean(diffs))
                jitter_max = float(np.max(diffs))
            else:
                jitter_mean = 0.0
                jitter_max = 0.0

            # 2. ODE Velocity Variance
            if len(self._velocities) >= 2:
                vel_var = float(np.var(list(self._velocities)))
            else:
                vel_var = 0.0

            # 3. Free Energy Surprise
            if len(self._surprises) >= 2:
                surprise_mean = float(np.mean(list(self._surprises)))
                surprise_std = float(np.std(list(self._surprises)))
            elif len(self._surprises) == 1:
                surprise_mean = float(self._surprises[0])
                surprise_std = 0.0
            else:
                surprise_mean = 0.0
                surprise_std = 0.0

            # 4. SDM Saturation
            saturation = min(1.0, self._last_sdm_count / max(1, self._max_sdm_capacity))
            saturation_pct = saturation * 100.0

            # 5. Composite Limbic Stability Index (LSI in [0.0, 1.0])
            jitter_term = math.exp(-jitter_mean / 50.0)
            vel_term = math.exp(-min(10.0, vel_var))
            sat_term = 1.0 - (saturation * 0.5)

            lsi = (0.4 * jitter_term) + (0.4 * vel_term) + (0.2 * sat_term)
            lsi = max(0.0, min(1.0, lsi))

            # Status classification
            if lsi >= 0.75:
                status = "nominal"
            elif lsi >= 0.45:
                status = "recovering"
            else:
                status = "degraded"

            return StabilitySnapshot(
                lsi=round(lsi, 3),
                status=status,
                fast_loop_jitter_mean_ms=round(jitter_mean, 2),
                fast_loop_jitter_max_ms=round(jitter_max, 2),
                ode_velocity_variance=round(vel_var, 4),
                free_energy_surprise_mean=round(surprise_mean, 4),
                free_energy_surprise_std=round(surprise_std, 4),
                sdm_saturation_pct=round(saturation_pct, 1),
                recovery_count=self._recovery_count,
                uptime_seconds=round(uptime, 1),
                timestamp=now,
            )
