"""
Unit tests for EcphoryEngine.

Requirements: 9.1–9.9, 10.1–10.7
"""

import numpy as np
import pytest

from src.core.memory.affective_memory import MemoryTrace
from src.core.memory.ecphory import EcphoryConfig, EcphoryEngine
from src.core.models import PADState


class TestEcphoryConfigValidation:
    def test_resonance_threshold_out_of_range_raises(self):
        with pytest.raises(ValueError, match="resonance_threshold"):
            EcphoryConfig(resonance_threshold=1.1)
        with pytest.raises(ValueError, match="resonance_threshold"):
            EcphoryConfig(resonance_threshold=-0.1)

    def test_ecphory_k_out_of_range_raises(self):
        with pytest.raises(ValueError, match="ecphory_k"):
            EcphoryConfig(ecphory_k=0)
        with pytest.raises(ValueError, match="ecphory_k"):
            EcphoryConfig(ecphory_k=51)

    def test_viability_threshold_out_of_range_raises(self):
        with pytest.raises(ValueError, match="viability_threshold"):
            EcphoryConfig(viability_threshold=0.0)
        with pytest.raises(ValueError, match="viability_threshold"):
            EcphoryConfig(viability_threshold=1.0)

    def test_invalid_config_type_raises(self):
        with pytest.raises(ValueError):
            EcphoryEngine("invalid")


class TestEcphoryQuery:
    def test_query_zero_magnitude_pad_returns_none(self):
        engine = EcphoryEngine(EcphoryConfig())
        pad_zero = PADState(0.0, 0.0, 0.0, 0.0)
        traces = [
            MemoryTrace(
                trace_id=0,
                address_vec=np.zeros(64, dtype=np.uint8),
                content_vec=np.ones(16, dtype=np.float32),
                pad_tag=PADState(0.5, 0.5, 0.5, 0.0),
                timestamp=0.0,
                decay_weight=1.0,
            )
        ]
        assert engine.query(pad_zero, traces) is None

    def test_query_out_of_range_pad_raises_value_error(self):
        engine = EcphoryEngine(EcphoryConfig())
        traces = []
        with pytest.raises(ValueError, match="pleasure"):
            engine.query(PADState(1.5, 0.0, 0.0, 0.0), traces)
        with pytest.raises(ValueError, match="arousal"):
            engine.query(PADState(0.0, -2.0, 0.0, 0.0), traces)
        with pytest.raises(ValueError, match="dominance"):
            engine.query(PADState(0.0, 0.0, 1.1, 0.0), traces)

    def test_query_empty_traces_returns_none(self):
        engine = EcphoryEngine(EcphoryConfig())
        pad = PADState(0.5, 0.5, 0.5, 0.0)
        assert engine.query(pad, []) is None

    def test_query_below_viability_traces_ignored(self):
        engine = EcphoryEngine(EcphoryConfig(viability_threshold=0.1))
        pad = PADState(0.5, 0.5, 0.5, 0.0)
        traces = [
            MemoryTrace(
                trace_id=0,
                address_vec=np.zeros(64, dtype=np.uint8),
                content_vec=np.ones(16, dtype=np.float32),
                pad_tag=PADState(0.5, 0.5, 0.5, 0.0),
                timestamp=0.0,
                decay_weight=0.05,  # <= 0.1
            )
        ]
        assert engine.query(pad, traces) is None

    def test_query_qualifying_traces_returns_echo_vector(self):
        engine = EcphoryEngine(
            EcphoryConfig(resonance_threshold=0.5, ecphory_k=3)
        )
        pad = PADState(1.0, 0.0, 0.0, 0.0)
        # Perfectly aligned pad tag -> resonance = 1.0 > 0.5
        content = np.array([0.5, -0.5, 1.0, -1.0], dtype=np.float32)
        traces = [
            MemoryTrace(
                trace_id=0,
                address_vec=np.zeros(64, dtype=np.uint8),
                content_vec=content,
                pad_tag=PADState(1.0, 0.0, 0.0, 0.0),
                timestamp=0.0,
                decay_weight=1.0,
            )
        ]
        echo = engine.query(pad, traces)
        assert echo is not None
        assert echo.shape == (4,)
        assert np.allclose(echo, content)
        assert echo.dtype == np.float32

    def test_top_k_exclusion_of_lower_resonance_traces(self):
        engine = EcphoryEngine(
            EcphoryConfig(resonance_threshold=0.0, ecphory_k=2)
        )
        query_pad = PADState(1.0, 0.0, 0.0, 0.0)

        # 3 traces with distinct alignments with (1, 0, 0)
        # Trace 0: (1.0, 0.0, 0.0) -> cos = 1.0
        # Trace 1: (0.8, 0.6, 0.0) -> cos = 0.8
        # Trace 2: (0.1, 0.99, 0.0) -> cos = 0.1
        t0 = MemoryTrace(
            0,
            np.zeros(4, dtype=np.uint8),
            np.array([10.0, 0.0], dtype=np.float32),
            PADState(1.0, 0.0, 0.0, 0.0),
            0.0,
            1.0,
        )
        t1 = MemoryTrace(
            1,
            np.zeros(4, dtype=np.uint8),
            np.array([0.0, 10.0], dtype=np.float32),
            PADState(0.8, 0.6, 0.0, 0.0),
            0.0,
            1.0,
        )
        t2 = MemoryTrace(
            2,
            np.zeros(4, dtype=np.uint8),
            np.array([-50.0, -50.0], dtype=np.float32),
            PADState(0.1, 0.99, 0.0, 0.0),
            0.0,
            1.0,
        )

        # Query with all 3 traces: only t0 and t1 should contribute (top 2)
        echo_3 = engine.query(query_pad, [t0, t1, t2])
        echo_2 = engine.query(query_pad, [t0, t1])

        assert echo_3 is not None
        assert echo_2 is not None
        assert np.allclose(echo_3, echo_2)
