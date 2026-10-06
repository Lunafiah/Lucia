"""
tests/evaluation/phase26/determinism/virtual_clock_harness.py

Evaluation-Only Virtual Clock Harness for Phase 26.
Controls ODE time progression deterministically without real-time thread jitter.

GOVERNANCE:
- Does NOT modify src/core/emotion/emotion_core.py.
- Uses canonical EmotionCore.step_once(custom_timestamp=...) designed for SimClock.
- Guarantees bit-exact identical PAD trajectories for identical input sequences.
"""

from __future__ import annotations

from typing import List, Optional, Tuple

import numpy as np

from src.core.emotion.emotion_core import EmotionCore
from src.core.models import PADState


class VirtualClockHarness:
    """
    Simulated clock controller that drives EmotionCore synchronously in evaluation mode.
    """

    def __init__(self, core: EmotionCore, initial_time: float = 0.0) -> None:
        self.core = core
        self.current_time = float(initial_time)
        self.trajectory_history: List[Tuple[float, PADState]] = []

    def step(self, dt: float = 0.200) -> PADState:
        """
        Advance ODE by exactly one tick with constant dt.
        Thread-safe; executes synchronously under EmotionCore._step_lock.
        """
        self.current_time += float(dt)
        pad = self.core.step_once(custom_timestamp=self.current_time)
        self.trajectory_history.append((self.current_time, pad))
        return pad

    def push_and_step(self, stimulus_vector: np.ndarray, dt: float = 0.200) -> PADState:
        """
        Inject a stimulus vector and immediately advance the ODE by one tick.
        """
        self.core.push_stimulus(stimulus_vector)
        return self.step(dt=dt)

    def relax_to_resting(
        self,
        max_steps: int = 150,
        dt: float = 0.200,
        tolerance: float = 1e-3,
    ) -> Tuple[bool, int, float]:
        """
        Advance the ODE with zero stimulus until the system relaxes to Philia resting baseline.
        Returns: (converged, steps_taken, final_distance).
        """
        steps = 0
        final_dist = self.core.get_attractor_distance()

        while steps < max_steps:
            if final_dist <= tolerance:
                return True, steps, final_dist

            self.step(dt=dt)
            steps += 1
            final_dist = self.core.get_attractor_distance()

        converged = bool(final_dist <= tolerance)
        return converged, steps, final_dist
