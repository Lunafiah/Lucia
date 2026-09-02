"""
DecayEngine — time-based trace weakening and slow loop lifecycle.

Runs a slow-loop background thread that applies time-based decay to all stored
Memory_Traces and purges traces falling below viability.

Requirements: 7.1–7.9, 8.1–8.6
"""

from __future__ import annotations

import logging
import threading
import time
from dataclasses import dataclass
from typing import List

import numpy as np

from src.core.memory.affective_memory import AffectiveMemory
from src.core.models import PADState

logger = logging.getLogger(__name__)


@dataclass
class DecayConfig:
    """
    Configuration for DecayEngine.

    Parameters
    ----------
    base_decay_rate : float
        Decay rate per second in (0.0, 1.0).
    viability_threshold : float
        Decay weight threshold below which traces are purged in (0.0, 1.0).
    loop_cadence_seconds : int
        Sleep interval between decay ticks in seconds (>= 60).
    """

    base_decay_rate: float = 0.0001
    viability_threshold: float = 0.05
    loop_cadence_seconds: int = 3600

    def __post_init__(self) -> None:
        if self.loop_cadence_seconds < 60:
            raise ValueError(
                f"loop_cadence_seconds ({self.loop_cadence_seconds}) must be >= 60"
            )
        if not (0.0 < self.base_decay_rate < 1.0):
            raise ValueError(
                f"base_decay_rate ({self.base_decay_rate}) must be in (0.0, 1.0)"
            )
        if not (0.0 < self.viability_threshold < 1.0):
            raise ValueError(
                f"viability_threshold ({self.viability_threshold}) must be in (0.0, 1.0)"
            )


class DecayEngine:
    """
    Background worker that weakens trace weights over time and purges expired traces.
    """

    def __init__(self, memory: AffectiveMemory, config: DecayConfig) -> None:
        if not isinstance(config, DecayConfig):
            raise ValueError("config must be a DecayConfig instance")
        config.__post_init__()
        self._memory = memory
        self._config = config
        self._stop_event = threading.Event()
        self._thread: threading.Thread | None = None

    def _emotional_intensity(self, pad_tag: PADState) -> float:
        """
        Compute emotional intensity in [0.0, 1.0] from PAD tag:
        intensity = clip(|arousal| * (|pleasure| + 0.1), 0.0, 1.0)
        """
        raw = abs(pad_tag.arousal) * (abs(pad_tag.pleasure) + 0.1)
        return float(np.clip(raw, 0.0, 1.0))

    def _decay_rate(self, pad_tag: PADState) -> float:
        """
        Compute per-second decay rate modulated by emotional intensity:
        decay_rate = base_decay_rate * (1.0 - emotional_intensity)
        """
        return self._config.base_decay_rate * (
            1.0 - self._emotional_intensity(pad_tag)
        )

    def _apply_decay_tick(self, elapsed_seconds: float) -> None:
        """
        Apply decay to all indexed traces and purge those below viability threshold.
        Entire operation is performed atomically under _index_lock.
        """
        to_purge: List[int] = []

        with self._memory._index_lock:
            for trace_id, trace in list(self._memory._index.items()):
                rate = self._decay_rate(trace.pad_tag)
                new_weight = trace.decay_weight - rate * elapsed_seconds
                trace.decay_weight = float(np.clip(new_weight, 0.0, 1.0))
                if trace.decay_weight <= self._config.viability_threshold:
                    to_purge.append(trace_id)

            for trace_id in to_purge:
                self._memory.delete_trace(trace_id)

        logger.info(
            "Decay tick: elapsed=%.1fs purged=%d remaining=%d",
            elapsed_seconds,
            len(to_purge),
            len(self._memory._index),
        )

    def _slow_loop_worker(self) -> None:
        """
        Daemon thread worker for the slow loop.
        """
        last_tick = time.monotonic()
        while not self._stop_event.is_set():
            self._stop_event.wait(timeout=self._config.loop_cadence_seconds)
            if self._stop_event.is_set():
                break

            now = time.monotonic()
            elapsed = now - last_tick
            last_tick = now

            try:
                self._apply_decay_tick(elapsed)
            except Exception:
                logger.error("Decay_Engine tick failed", exc_info=True)

    def start(self) -> None:
        """
        Start the background slow loop daemon thread.
        """
        self._stop_event.clear()
        self._thread = threading.Thread(
            target=self._slow_loop_worker,
            daemon=True,
            name="DecayEngine-SlowLoop",
        )
        self._thread.start()

        deadline = time.monotonic() + 2.0
        while time.monotonic() < deadline:
            if self._thread.is_alive():
                return
            time.sleep(0.05)
        raise RuntimeError("Decay_Engine Slow_Loop failed to start within 2 seconds")

    def stop(self) -> None:
        """
        Stop the slow loop daemon thread and join it (5-second timeout).
        """
        self._stop_event.set()
        if self._thread is not None:
            self._thread.join(timeout=5.0)
            self._thread = None

    def is_alive(self) -> bool:
        """
        Return True if the background thread is currently running.
        """
        return self._thread is not None and self._thread.is_alive()
