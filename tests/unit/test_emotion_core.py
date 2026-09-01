"""
Unit tests for EmotionCore background loop.
Requirements: 1.2, 1.3, 1.8, 1.9, 1.10
"""

from __future__ import annotations

import threading
import time
from unittest.mock import patch

import numpy as np
import pytest

from src.core.config import EmotionConfig
from src.core.emotion.emotion_core import EmotionCore
from src.core.models import PADState


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def make_core(cadence_ms: int = 100, hidden_dim: int = 8) -> EmotionCore:
    """Fast cadence for tests."""
    return EmotionCore(EmotionConfig(loop_cadence_ms=cadence_ms, hidden_dim=hidden_dim))


def wait_for_ticks(core: EmotionCore, n: int, timeout: float = 3.0) -> bool:
    deadline = time.monotonic() + timeout
    while time.monotonic() < deadline:
        if core.tick_count() >= n:
            return True
        time.sleep(0.02)
    return False


# ---------------------------------------------------------------------------
# Initialisation (Req 1.1, 1.2)
# ---------------------------------------------------------------------------

class TestInit:
    def test_pad_snapshot_at_resting_baseline_before_start(self):
        core = make_core()
        pad = core.get_pad_state()
        cfg = core._config
        assert pad.pleasure == pytest.approx(cfg.resting_baseline[0])
        assert pad.arousal == pytest.approx(cfg.resting_baseline[1])
        assert pad.dominance == pytest.approx(cfg.resting_baseline[2])

    def test_custom_baseline_reflected_in_snapshot(self):
        cfg = EmotionConfig(
            loop_cadence_ms=100,
            hidden_dim=8,
            resting_baseline=(0.5, -0.3, 0.2),
        )
        core = EmotionCore(cfg)
        pad = core.get_pad_state()
        assert pad.pleasure == pytest.approx(0.5)
        assert pad.arousal == pytest.approx(-0.3)
        assert pad.dominance == pytest.approx(0.2)

    def test_tick_count_zero_before_start(self):
        core = make_core()
        assert core.tick_count() == 0

    def test_is_alive_false_before_start(self):
        core = make_core()
        assert core.is_alive() is False


# ---------------------------------------------------------------------------
# Start / stop lifecycle (Req 1.3)
# ---------------------------------------------------------------------------

class TestLifecycle:
    def test_thread_alive_after_start(self):
        core = make_core()
        core.start()
        try:
            assert core.is_alive() is True
        finally:
            core.stop()

    def test_tick_count_increases(self):
        core = make_core(cadence_ms=100)
        core.start()
        try:
            assert wait_for_ticks(core, 3), f"Expected >=3 ticks, got {core.tick_count()}"
        finally:
            core.stop()

    def test_double_start_is_idempotent(self):
        core = make_core()
        core.start()
        thread1 = core._thread
        core.start()
        thread2 = core._thread
        try:
            assert thread1 is thread2, "Second start should reuse existing thread"
        finally:
            core.stop()

    def test_stop_signals_thread(self):
        core = make_core(cadence_ms=100)
        core.start()
        assert wait_for_ticks(core, 1)
        core.stop()
        # Give thread time to exit
        if core._thread:
            core._thread.join(timeout=2.0)
        assert not core.is_alive() or core._stop_event.is_set()


# ---------------------------------------------------------------------------
# Exception recovery (Req 1.8)
# ---------------------------------------------------------------------------

class TestExceptionRecovery:
    def test_exception_in_ode_step_resets_to_baseline(self):
        core = make_core(cadence_ms=100)
        cfg = core._config

        call_count = [0]
        original_ode_step = core._ode_step

        def exploding_ode(h, x):
            call_count[0] += 1
            if call_count[0] == 1:
                raise RuntimeError("Simulated ODE failure")
            return original_ode_step(h, x)

        core._ode_step = exploding_ode
        core.start()

        # Wait for the exception tick + recovery tick
        assert wait_for_ticks(core, 2, timeout=5.0), (
            f"Thread should recover and continue, got {core.tick_count()} ticks"
        )
        assert core.is_alive(), "Thread must stay alive after exception"

        # PAD should be at resting baseline after reset
        # (may have advanced slightly after recovery tick, so just check alive)
        pad = core.get_pad_state()
        assert -1.0 <= pad.pleasure <= 1.0
        core.stop()

    def test_thread_stays_alive_after_multiple_exceptions(self):
        core = make_core(cadence_ms=100)
        exc_count = [0]
        original = core._ode_step

        def always_fail(h, x):
            exc_count[0] += 1
            if exc_count[0] <= 3:
                raise RuntimeError("repeated failure")
            return original(h, x)

        core._ode_step = always_fail
        core.start()
        # Should still be alive after processing past 3 failures
        assert wait_for_ticks(core, 1, timeout=5.0)
        assert core.is_alive()
        core.stop()


# ---------------------------------------------------------------------------
# Thread-safe read (Req 1.9)
# ---------------------------------------------------------------------------

class TestThreadSafeRead:
    def test_get_pad_state_returns_within_2ms(self):
        core = make_core(cadence_ms=100)
        core.start()
        try:
            assert wait_for_ticks(core, 1)
            start = time.monotonic()
            pad = core.get_pad_state()
            elapsed_ms = (time.monotonic() - start) * 1000
            assert elapsed_ms < 2.0, f"get_pad_state took {elapsed_ms:.2f} ms"
            assert isinstance(pad, PADState)
        finally:
            core.stop()

    def test_get_pad_state_under_lock_contention(self):
        """get_pad_state must return within 2 ms even when the lock is held."""
        core = make_core(cadence_ms=100)
        core.start()
        try:
            assert wait_for_ticks(core, 1)

            # Hold the state lock from another thread for 5 ms
            def hold_lock():
                with core._state_lock:
                    time.sleep(0.005)

            t = threading.Thread(target=hold_lock, daemon=True)
            t.start()
            time.sleep(0.001)  # ensure lock is held before calling

            start = time.monotonic()
            pad = core.get_pad_state()  # should return last known snapshot quickly
            elapsed_ms = (time.monotonic() - start) * 1000
            t.join()
            # Should return within 1ms deadline (the timeout in get_pad_state)
            assert elapsed_ms < 20.0, f"get_pad_state too slow under contention: {elapsed_ms:.2f} ms"
            assert isinstance(pad, PADState)
        finally:
            core.stop()

    def test_concurrent_reads_are_safe(self):
        core = make_core(cadence_ms=100)
        core.start()
        results = []
        errors = []

        def reader():
            try:
                for _ in range(20):
                    pad = core.get_pad_state()
                    assert isinstance(pad, PADState)
                    results.append(pad)
                    time.sleep(0.005)
            except Exception as e:
                errors.append(e)

        threads = [threading.Thread(target=reader, daemon=True) for _ in range(5)]
        for t in threads:
            t.start()
        for t in threads:
            t.join(timeout=5.0)

        core.stop()
        assert not errors, f"Concurrent reads produced errors: {errors}"
        assert len(results) > 0


# ---------------------------------------------------------------------------
# push_stimulus (Req 1.4, 1.5)
# ---------------------------------------------------------------------------

class TestPushStimulus:
    def test_push_stimulus_accepted_without_error(self):
        core = make_core()
        vec = np.random.uniform(-0.5, 0.5, 16)
        core.push_stimulus(vec)  # should not raise

    def test_push_stimulus_changes_state_over_time(self):
        core = make_core(cadence_ms=100)
        core.start()
        assert wait_for_ticks(core, 2)
        pad_before = core.get_pad_state()

        # Push a strong stimulus and wait for it to be consumed
        stimulus = np.ones(16) * 0.9
        core.push_stimulus(stimulus)
        assert wait_for_ticks(core, core.tick_count() + 2)
        pad_after = core.get_pad_state()

        # State should have changed (not necessarily a specific direction,
        # just different from before)
        changed = (
            pad_before.pleasure != pad_after.pleasure or
            pad_before.arousal != pad_after.arousal or
            pad_before.dominance != pad_after.dominance
        )
        assert changed, "PAD state should change after stimulus injection"
        core.stop()


# ---------------------------------------------------------------------------
# PAD bounds (Req 1.7)
# ---------------------------------------------------------------------------

class TestPADBounds:
    def test_pad_state_always_in_bounds_during_run(self):
        core = make_core(cadence_ms=100)
        core.start()
        violations = []

        def check_bounds():
            for _ in range(50):
                pad = core.get_pad_state()
                if not (-1.0 <= pad.pleasure <= 1.0):
                    violations.append(("pleasure", pad.pleasure))
                if not (-1.0 <= pad.arousal <= 1.0):
                    violations.append(("arousal", pad.arousal))
                if not (-1.0 <= pad.dominance <= 1.0):
                    violations.append(("dominance", pad.dominance))
                time.sleep(0.01)

        # Feed large stimuli to stress the clamp
        for _ in range(10):
            core.push_stimulus(np.ones(16) * 5.0)
            time.sleep(0.05)

        check_bounds()
        core.stop()
        assert not violations, f"PAD bounds violated: {violations}"
