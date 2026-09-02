"""Unit tests for StabilityEvaluator and Limbic Stability Index (LSI)."""
import time
import pytest
from src.core.telemetry.stability_evaluator import StabilityEvaluator, StabilitySnapshot


class TestStabilityEvaluator:
    def test_initial_snapshot(self):
        evaluator = StabilityEvaluator()
        snap = evaluator.get_snapshot()

        assert isinstance(snap, StabilitySnapshot)
        assert 0.0 <= snap.lsi <= 1.0
        assert snap.status in ["nominal", "recovering", "degraded"]
        assert snap.fast_loop_jitter_mean_ms >= 0.0
        assert snap.recovery_count == 0

    def test_record_ticks_and_jitter(self):
        evaluator = StabilityEvaluator(nominal_tick_ms=200.0)

        # Simulate 10 evenly spaced ticks ~200ms apart
        for i in range(10):
            evaluator.record_tick(hidden_state_norm=1.0 + (i * 0.01))
            time.sleep(0.01)  # small delta for test

        snap = evaluator.get_snapshot()
        assert snap.uptime_seconds >= 0.0
        assert snap.ode_velocity_variance >= 0.0
        assert snap.lsi > 0.0

    def test_surprise_and_sdm_saturation(self):
        evaluator = StabilityEvaluator(max_sdm_capacity=100)
        evaluator.record_surprise(0.12)
        evaluator.record_surprise(0.18)
        evaluator.update_sdm_count(50)

        snap = evaluator.get_snapshot()
        assert snap.sdm_saturation_pct == 50.0
        assert 0.10 <= snap.free_energy_surprise_mean <= 0.20
        assert snap.free_energy_surprise_std > 0.0

    def test_recovery_event_increment(self):
        evaluator = StabilityEvaluator()
        evaluator.record_recovery_event()
        evaluator.record_recovery_event()

        snap = evaluator.get_snapshot()
        assert snap.recovery_count == 2
        d = snap.to_dict()
        assert d["recovery_count"] == 2
