"""
Unit tests for DecayEngine.

Requirements: 7.1–7.9, 8.1–8.6
"""

import time
from unittest.mock import patch

import numpy as np
import pytest

from src.core.memory.affective_memory import (
    AffectiveMemory,
    AffectiveMemoryConfig,
)
from src.core.memory.decay import DecayConfig, DecayEngine
from src.core.memory.sdm import SDMConfig
from src.core.models import PADState


@pytest.fixture
def memory():
    cfg = AffectiveMemoryConfig(
        sdm_config=SDMConfig(num_locations=100, address_dim=64, content_dim=16),
        m=16,
    )
    return AffectiveMemory(cfg)


class TestDecayConfigValidation:
    def test_cadence_below_60_raises(self):
        with pytest.raises(ValueError, match="loop_cadence_seconds"):
            DecayConfig(loop_cadence_seconds=59)

    def test_base_decay_rate_out_of_range_raises(self):
        with pytest.raises(ValueError, match="base_decay_rate"):
            DecayConfig(base_decay_rate=0.0)
        with pytest.raises(ValueError, match="base_decay_rate"):
            DecayConfig(base_decay_rate=1.0)

    def test_viability_threshold_out_of_range_raises(self):
        with pytest.raises(ValueError, match="viability_threshold"):
            DecayConfig(viability_threshold=0.0)
        with pytest.raises(ValueError, match="viability_threshold"):
            DecayConfig(viability_threshold=1.0)

    def test_invalid_engine_config_type_raises(self, memory):
        with pytest.raises(ValueError):
            DecayEngine(memory, "invalid")


class TestDecayCalculations:
    def test_emotional_intensity_calculation(self, memory):
        engine = DecayEngine(memory, DecayConfig())
        # Arousal = 0 -> intensity = 0
        pad_zero = PADState(pleasure=0.5, arousal=0.0, dominance=0.0, timestamp=0.0)
        assert engine._emotional_intensity(pad_zero) == 0.0

        # High arousal and pleasure
        pad_high = PADState(pleasure=1.0, arousal=1.0, dominance=1.0, timestamp=0.0)
        # raw = 1.0 * (1.0 + 0.1) = 1.1 -> clipped to 1.0
        assert engine._emotional_intensity(pad_high) == 1.0

    def test_high_intensity_trace_decays_slower(self, memory):
        cfg = DecayConfig(base_decay_rate=0.01)
        engine = DecayEngine(memory, cfg)

        pad_high = PADState(pleasure=0.9, arousal=0.9, dominance=0.5, timestamp=0.0)
        pad_low = PADState(pleasure=0.0, arousal=0.1, dominance=0.0, timestamp=0.0)

        rate_high = engine._decay_rate(pad_high)
        rate_low = engine._decay_rate(pad_low)

        assert rate_high < rate_low

    def test_decay_tick_reduces_weight(self, memory):
        engine = DecayEngine(memory, DecayConfig(base_decay_rate=0.001))
        content = np.zeros(16, dtype=np.float32)
        pad = PADState(pleasure=0.0, arousal=0.0, dominance=0.0, timestamp=0.0)
        tid = memory.store(content, pad)

        assert memory.get_trace(tid).decay_weight == 1.0
        engine._apply_decay_tick(elapsed_seconds=100.0)

        # intensity = 0 -> decay_rate = 0.001 * (1 - 0) = 0.001
        # new_weight = 1.0 - 0.001 * 100 = 0.9
        assert pytest.approx(memory.get_trace(tid).decay_weight, abs=1e-4) == 0.9

    def test_trace_below_viability_is_purged(self, memory):
        engine = DecayEngine(
            memory, DecayConfig(base_decay_rate=0.01, viability_threshold=0.1)
        )
        content = np.zeros(16, dtype=np.float32)
        pad = PADState(pleasure=0.0, arousal=0.0, dominance=0.0, timestamp=0.0)
        tid = memory.store(content, pad)

        # Apply enough decay to bring weight <= 0.1
        engine._apply_decay_tick(elapsed_seconds=100.0)
        # weight would be 1.0 - 0.01 * 100 = 0.0 <= 0.1 -> purged
        assert len(memory.get_all_traces()) == 0


class TestDecayEngineLifecycle:
    def test_start_and_stop_lifecycle(self, memory):
        engine = DecayEngine(memory, DecayConfig(loop_cadence_seconds=60))
        assert not engine.is_alive()
        engine.start()
        assert engine.is_alive()
        engine.stop()
        assert not engine.is_alive()

    def test_exception_in_tick_does_not_crash_thread(self, memory):
        engine = DecayEngine(memory, DecayConfig(loop_cadence_seconds=60))
        content = np.zeros(16, dtype=np.float32)
        pad = PADState.resting()
        memory.store(content, pad)

        with patch.object(
            engine, "_apply_decay_tick", side_effect=[RuntimeError("boom"), None]
        ):
            # Run worker iteration directly
            engine.start()
            time.sleep(0.1)
            assert engine.is_alive()
            engine.stop()
