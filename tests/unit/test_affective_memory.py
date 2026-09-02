"""
Unit tests for AffectiveMemory.

Requirements: 5.1–5.8, 6.1–6.5, 15.4, 15.5
"""

import numpy as np
import pytest

from src.core.memory.affective_memory import (
    AffectiveMemory,
    AffectiveMemoryConfig,
)
from src.core.memory.sdm import SDMConfig
from src.core.models import PADState


class TestAffectiveMemoryConfigValidation:
    def test_m_mismatch_with_sdm_content_dim_raises(self):
        sdm_cfg = SDMConfig(content_dim=64)
        with pytest.raises(ValueError, match="must match"):
            AffectiveMemoryConfig(sdm_config=sdm_cfg, m=32)

    def test_invalid_config_type_raises(self):
        with pytest.raises(ValueError):
            AffectiveMemory("invalid")


class TestAffectiveMemoryOperations:
    def test_empty_memory_get_all_traces_returns_empty_list(self):
        cfg = AffectiveMemoryConfig(
            sdm_config=SDMConfig(num_locations=100, address_dim=64, content_dim=16),
            m=16,
        )
        mem = AffectiveMemory(cfg)
        assert mem.get_all_traces() == []

    def test_store_wrong_dimension_raises_value_error(self):
        cfg = AffectiveMemoryConfig(
            sdm_config=SDMConfig(num_locations=100, address_dim=64, content_dim=16),
            m=16,
        )
        mem = AffectiveMemory(cfg)
        pad = PADState.resting()
        with pytest.raises(ValueError, match="content_vector dim"):
            mem.store(np.zeros(15, dtype=np.float32), pad)

    def test_store_out_of_range_pad_raises_value_error(self):
        cfg = AffectiveMemoryConfig(
            sdm_config=SDMConfig(num_locations=100, address_dim=64, content_dim=16),
            m=16,
        )
        mem = AffectiveMemory(cfg)
        content = np.zeros(16, dtype=np.float32)

        with pytest.raises(ValueError, match="pleasure"):
            mem.store(content, PADState(1.5, 0.0, 0.0, 0.0))

        with pytest.raises(ValueError, match="arousal"):
            mem.store(content, PADState(0.0, -1.5, 0.0, 0.0))

        with pytest.raises(ValueError, match="dominance"):
            mem.store(content, PADState(0.0, 0.0, 2.0, 0.0))

    def test_store_returns_sequential_ids(self):
        cfg = AffectiveMemoryConfig(
            sdm_config=SDMConfig(num_locations=100, address_dim=64, content_dim=16),
            m=16,
        )
        mem = AffectiveMemory(cfg)
        pad = PADState(0.2, 0.3, -0.1, 100.0)
        content = np.ones(16, dtype=np.float32)

        id1 = mem.store(content, pad)
        id2 = mem.store(content, pad)
        assert id1 == 0
        assert id2 == 1
        assert len(mem.get_all_traces()) == 2

    def test_get_trace_returns_exact_data(self):
        cfg = AffectiveMemoryConfig(
            sdm_config=SDMConfig(num_locations=100, address_dim=64, content_dim=16),
            m=16,
        )
        mem = AffectiveMemory(cfg)
        pad = PADState(0.5, -0.3, 0.1, 12345.0)
        content = np.linspace(-1.0, 1.0, 16, dtype=np.float32)

        trace_id = mem.store(content, pad)
        trace = mem.get_trace(trace_id)

        assert trace.trace_id == trace_id
        assert trace.pad_tag == pad
        assert trace.decay_weight == 1.0
        assert np.allclose(trace.content_vec, content)
        assert trace.address_vec.shape == (64,)

    def test_get_trace_unknown_id_raises_key_error(self):
        cfg = AffectiveMemoryConfig(
            sdm_config=SDMConfig(num_locations=100, address_dim=64, content_dim=16),
            m=16,
        )
        mem = AffectiveMemory(cfg)
        with pytest.raises(KeyError, match="not found"):
            mem.get_trace(999)

    def test_eviction_on_capacity_overflow(self):
        cfg = AffectiveMemoryConfig(
            sdm_config=SDMConfig(
                num_locations=100, address_dim=64, content_dim=8, capacity=3
            ),
            m=8,
        )
        mem = AffectiveMemory(cfg)
        pad = PADState.resting()
        content = np.zeros(8, dtype=np.float32)

        id0 = mem.store(content, pad)
        id1 = mem.store(content, pad)
        id2 = mem.store(content, pad)

        assert len(mem.get_all_traces()) == 3

        # Artificially weaken trace 1 so it becomes the lowest decay_weight
        mem.get_trace(id1).decay_weight = 0.2

        # Storing a 4th trace should evict trace 1
        id3 = mem.store(content, pad)

        traces = mem.get_all_traces()
        assert len(traces) == 3
        trace_ids = {t.trace_id for t in traces}
        assert id1 not in trace_ids
        assert id0 in trace_ids
        assert id2 in trace_ids
        assert id3 in trace_ids

    def test_index_memory_usage_bytes(self):
        cfg = AffectiveMemoryConfig(
            sdm_config=SDMConfig(num_locations=100, address_dim=64, content_dim=16),
            m=16,
        )
        mem = AffectiveMemory(cfg)
        pad = PADState.resting()
        content = np.zeros(16, dtype=np.float32)

        assert mem.index_memory_usage_bytes() == 0
        mem.store(content, pad)
        assert mem.index_memory_usage_bytes() > 0
