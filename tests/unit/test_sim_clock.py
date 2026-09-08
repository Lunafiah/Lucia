import pytest
from src.core.simulation.sim_clock import SimClock


class TestSimClock:
    def test_clock_initialization(self):
        clock = SimClock(initial_time_s=10.0)
        assert clock.virtual_time_s == 10.0
        assert not clock.is_paused
        assert clock.speed_factor == 1.0

    def test_clock_step_discrete(self):
        clock = SimClock(initial_time_s=0.0)
        fast_calls = []
        slow_calls = []

        clock.register_fast_tick(lambda dt, vt: fast_calls.append((dt, vt)))
        clock.register_slow_tick(lambda dt, vt: slow_calls.append((dt, vt)))

        # Step by 200ms
        clock.step(delta_ms=200)
        assert abs(clock.virtual_time_s - 0.2) < 1e-5
        assert len(fast_calls) == 1
        assert len(slow_calls) == 0

        # Step by 1000ms (5 fast ticks)
        clock.step(delta_ms=1000)
        assert abs(clock.virtual_time_s - 1.2) < 1e-5
        assert len(fast_calls) == 6
        assert len(slow_calls) == 0

    def test_clock_pause_resume(self):
        clock = SimClock(initial_time_s=0.0)
        fast_calls = []
        clock.register_fast_tick(lambda dt, vt: fast_calls.append(vt))

        clock.pause()
        assert clock.is_paused

        # Advancing while paused does nothing
        clock.advance(elapsed_real_seconds=1.0)
        assert clock.virtual_time_s == 0.0
        assert len(fast_calls) == 0

        # Resume and advance
        clock.resume()
        assert not clock.is_paused
        clock.advance(elapsed_real_seconds=0.4)
        assert abs(clock.virtual_time_s - 0.4) < 1e-5
        assert len(fast_calls) == 2

    def test_clock_speed_dilation(self):
        clock = SimClock(initial_time_s=0.0)
        clock.set_speed(5.0)
        assert clock.speed_factor == 5.0

        # 0.2s real time * 5.0 speed = 1.0s virtual time (5 fast ticks of 0.2s)
        clock.advance(elapsed_real_seconds=0.2)
        assert abs(clock.virtual_time_s - 1.0) < 1e-5

    def test_clock_slow_tick_execution(self):
        clock = SimClock(initial_time_s=0.0)
        slow_calls = []
        clock.register_slow_tick(lambda dt, vt: slow_calls.append((dt, vt)))

        # Step by 65s (should trigger 1 slow tick of 60s, leaves 5s in accumulator)
        clock.step(delta_ms=65000)
        assert abs(clock.virtual_time_s - 65.0) < 1e-5
        assert len(slow_calls) == 1
        assert slow_calls[0][0] == 60.0

    def test_clock_reset(self):
        clock = SimClock(initial_time_s=100.0)
        clock.step(delta_ms=5000)
        assert clock.virtual_time_s > 100.0

        clock.reset(target_time_s=0.0)
        assert clock.virtual_time_s == 0.0
        assert clock._fast_due_accumulator_s == 0.0
        assert clock._slow_due_accumulator_s == 0.0

    def test_max_fast_ticks_protection(self):
        clock = SimClock(initial_time_s=0.0)
        fast_calls = []
        clock.register_fast_tick(lambda dt, vt: fast_calls.append(vt))

        # Leap forward by 1 hour (3600s = 18,000 fast ticks if unchecked)
        clock.step(delta_ms=3600 * 1000, max_fast_ticks=25)
        assert abs(clock.virtual_time_s - 3600.0) < 1e-5
        # Fast calls capped at 25 instead of 18,000
        assert len(fast_calls) == 25
