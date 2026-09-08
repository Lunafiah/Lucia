"""
SimClock — Virtualized, deterministic time provider for Lucia Simulation Environment.

Decouples continuous loops (EmotionCore FastLoop, DecayEngine SlowLoop) from physical
wall-clock time, allowing pause, discrete stepping, and controlled time dilation (1x - 60x).

Requirements: Phase 8 (INV-6, Section 6)
"""

from __future__ import annotations

import logging
import threading
import time
from typing import Callable, List, Optional, Tuple

logger = logging.getLogger("lucia.simulation.sim_clock")


class SimClock:
    """
    Thread-safe virtual clock providing deterministic time stepping and controlled dilation.
    """

    def __init__(
        self,
        fast_loop_cadence_s: float = 0.2,
        slow_loop_cadence_s: float = 60.0,
        start_time_s: float = 0.0,
        initial_time_s: Optional[float] = None,
    ) -> None:
        self._lock = threading.RLock()
        t = initial_time_s if initial_time_s is not None else start_time_s
        self._virtual_time_s = float(t)
        self._is_paused = False
        self._speed_factor = 1.0

        self._fast_loop_cadence_s = float(fast_loop_cadence_s)
        self._slow_loop_cadence_s = float(slow_loop_cadence_s)

        # Accumulators for due work
        self._fast_due_accumulator_s = 0.0
        self._slow_due_accumulator_s = 0.0

        # Callbacks for due work units
        self._fast_tick_callbacks: List[Callable[[float], None]] = []
        self._slow_tick_callbacks: List[Callable[[float], None]] = []

        # Background driver thread for non-paused time advancement
        self._stop_driver_event = threading.Event()
        self._driver_thread: Optional[threading.Thread] = None

    # ------------------------------------------------------------------
    # Time queries
    # ------------------------------------------------------------------

    @property
    def virtual_time_s(self) -> float:
        with self._lock:
            return self._virtual_time_s

    @property
    def is_paused(self) -> bool:
        with self._lock:
            return self._is_paused

    @property
    def speed_factor(self) -> float:
        with self._lock:
            return self._speed_factor

    def now(self) -> float:
        """Return current virtual time in seconds."""
        with self._lock:
            return self._virtual_time_s

    # ------------------------------------------------------------------
    # Work registration
    # ------------------------------------------------------------------

    def register_fast_tick_callback(self, cb: Callable[..., None]) -> None:
        """Register a callback invoked for each due 200ms fast-loop tick with current timestamp."""
        with self._lock:
            if cb not in self._fast_tick_callbacks:
                self._fast_tick_callbacks.append(cb)

    register_fast_tick = register_fast_tick_callback

    def register_slow_tick_callback(self, cb: Callable[..., None]) -> None:
        """Register a callback invoked for each due slow-loop decay tick with elapsed seconds."""
        with self._lock:
            if cb not in self._slow_tick_callbacks:
                self._slow_tick_callbacks.append(cb)

    register_slow_tick = register_slow_tick_callback

    # ------------------------------------------------------------------
    # Clock controls
    # ------------------------------------------------------------------

    def pause(self) -> None:
        """Pause virtual time advancement."""
        with self._lock:
            self._is_paused = True
        logger.info("SimClock paused at virtual_time=%.3fs", self._virtual_time_s)

    def resume(self) -> None:
        """Resume continuous virtual time advancement via background driver."""
        with self._lock:
            self._is_paused = False
            self._ensure_driver_started()
        logger.info("SimClock resumed at virtual_time=%.3fs (speed=%.1fx)", self._virtual_time_s, self._speed_factor)

    def set_speed(self, multiplier: float) -> None:
        """Set virtual time acceleration multiplier (e.g. 0.5 to 60.0)."""
        with self._lock:
            if multiplier <= 0.0:
                raise ValueError("Speed multiplier must be strictly positive")
            self._speed_factor = float(multiplier)
        logger.info("SimClock speed set to %.2fx", multiplier)

    def reset(self, reset_time_s: float = 0.0, target_time_s: Optional[float] = None) -> None:
        """Reset virtual clock to specified timestamp (default 0.0)."""
        t = target_time_s if target_time_s is not None else reset_time_s
        with self._lock:
            self._virtual_time_s = float(t)
            self._fast_due_accumulator_s = 0.0
            self._slow_due_accumulator_s = 0.0
        logger.info("SimClock reset to virtual_time=%.3fs", t)

    def advance(self, elapsed_real_seconds: float) -> Tuple[float, int, int]:
        """Advance time based on elapsed real seconds scaled by speed multiplier if not paused."""
        with self._lock:
            if self._is_paused:
                return self._virtual_time_s, 0, 0
            speed = self._speed_factor
        sim_dt_ms = elapsed_real_seconds * speed * 1000.0
        return self.step(sim_dt_ms)

    # ------------------------------------------------------------------
    # Deterministic Stepping
    # ------------------------------------------------------------------

    def step(self, delta_ms: float, max_fast_ticks: Optional[int] = 50) -> Tuple[float, int, int]:
        """
        Advance virtual time deterministically by delta_ms and execute due work units.
        Returns (new_virtual_time_s, fast_ticks_executed, slow_ticks_executed).
        max_fast_ticks: caps the number of LNN ODE fast ticks solved in a single step (default 50)
        to prevent event loop starvation during large time leaps (e.g. 1 hour = 18,000 ticks).
        """
        if delta_ms < 0.0:
            raise ValueError("delta_ms cannot be negative")

        delta_s = delta_ms / 1000.0
        fast_executed = 0
        slow_executed = 0

        with self._lock:
            self._virtual_time_s += delta_s
            self._fast_due_accumulator_s += delta_s
            self._slow_due_accumulator_s += delta_s

            # Execute due fast loop ticks up to max_fast_ticks
            while self._fast_due_accumulator_s >= self._fast_loop_cadence_s - 1e-9:
                if max_fast_ticks is not None and fast_executed >= max_fast_ticks:
                    self._fast_due_accumulator_s = 0.0
                    break
                self._fast_due_accumulator_s -= self._fast_loop_cadence_s
                current_time = self._virtual_time_s
                for cb in list(self._fast_tick_callbacks):
                    try:
                        import inspect
                        sig = inspect.signature(cb)
                        if len(sig.parameters) >= 2:
                            cb(self._fast_loop_cadence_s, current_time)
                        else:
                            cb(current_time)
                    except Exception as e:
                        logger.exception("Error in fast tick callback: %s", e)
                fast_executed += 1

            # Execute due slow loop decay ticks
            while self._slow_due_accumulator_s >= self._slow_loop_cadence_s - 1e-9:
                elapsed = self._slow_loop_cadence_s
                self._slow_due_accumulator_s -= self._slow_loop_cadence_s
                for cb in list(self._slow_tick_callbacks):
                    try:
                        import inspect
                        sig = inspect.signature(cb)
                        if len(sig.parameters) >= 2:
                            cb(elapsed, self._virtual_time_s)
                        else:
                            cb(elapsed)
                    except Exception as e:
                        logger.exception("Error in slow tick callback: %s", e)
                slow_executed += 1

            new_time = self._virtual_time_s

        return new_time, fast_executed, slow_executed

    def step_fast_tick(self) -> float:
        """Advance virtual time by exactly one fast-loop cadence (e.g. 200ms)."""
        new_time, _, _ = self.step(self._fast_loop_cadence_s * 1000.0)
        return new_time

    def step_slow_tick(self) -> float:
        """Advance virtual time by exactly one slow-loop cadence (e.g. 900s or 60s)."""
        new_time, _, _ = self.step(self._slow_loop_cadence_s * 1000.0)
        return new_time

    # ------------------------------------------------------------------
    # Background Driver Worker
    # ------------------------------------------------------------------

    def _ensure_driver_started(self) -> None:
        if self._driver_thread is None or not self._driver_thread.is_alive():
            self._stop_driver_event.clear()
            self._driver_thread = threading.Thread(
                target=self._driver_loop,
                name="SimClock-Driver",
                daemon=True,
            )
            self._driver_thread.start()

    def _driver_loop(self) -> None:
        """Smoothly steps time forward in real wall-clock increments when not paused."""
        last_wall = time.monotonic()
        while not self._stop_driver_event.is_set():
            time.sleep(0.05)  # 50ms polling resolution
            now_wall = time.monotonic()
            wall_dt = now_wall - last_wall
            last_wall = now_wall

            with self._lock:
                if self._is_paused:
                    continue
                speed = self._speed_factor

            sim_dt_ms = wall_dt * speed * 1000.0
            try:
                self.step(sim_dt_ms)
            except Exception as e:
                logger.error("SimClock driver error: %s", e)

    def shutdown(self) -> None:
        """Stop driver thread cleanly."""
        self._stop_driver_event.set()
        if self._driver_thread is not None and self._driver_thread.is_alive():
            self._driver_thread.join(timeout=1.0)
            self._driver_thread = None
