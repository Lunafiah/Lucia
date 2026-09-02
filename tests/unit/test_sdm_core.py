"""
Unit tests for SDMCore.

Requirements: 1.1–1.6, 2.4, 2.5, 4.1–4.4, 15.1–15.3
"""

import numpy as np
import pytest

from src.core.errors import CapacityError
from src.core.memory.sdm import SDMConfig, SDMCore


class TestSDMConfigValidation:
    def test_num_locations_below_100_raises(self):
        with pytest.raises(ValueError, match="num_locations"):
            SDMConfig(num_locations=99)

    def test_address_dim_below_64_raises(self):
        with pytest.raises(ValueError, match="address_dim"):
            SDMConfig(address_dim=63)

    def test_content_dim_below_8_raises(self):
        with pytest.raises(ValueError, match="content_dim"):
            SDMConfig(content_dim=7)

    def test_hamming_radius_fraction_out_of_range_raises(self):
        with pytest.raises(ValueError, match="hamming_radius_fraction"):
            SDMConfig(hamming_radius_fraction=0.0)
        with pytest.raises(ValueError, match="hamming_radius_fraction"):
            SDMConfig(hamming_radius_fraction=1.0)

    def test_capacity_below_1_raises(self):
        with pytest.raises(ValueError, match="capacity"):
            SDMConfig(capacity=0)


class TestSDMCoreInit:
    def test_arrays_allocated_correctly(self):
        config = SDMConfig(num_locations=150, address_dim=80, content_dim=16)
        sdm = SDMCore(config)
        assert sdm._hard_locs.shape == (150, 80)
        assert sdm._hard_locs.dtype == np.uint8
        assert sdm._accumulator.shape == (150, 16)
        assert sdm._accumulator.dtype == np.float32
        assert np.all(sdm._accumulator == 0.0)
        assert sdm._act_counts.shape == (150,)
        assert sdm.trace_count == 0
        assert sdm.capacity == 10_000

    def test_invalid_config_type_raises(self):
        with pytest.raises(ValueError):
            SDMCore("invalid")


class TestSDMWriteReadDelete:
    def test_write_dimension_mismatch_raises(self):
        config = SDMConfig(num_locations=100, address_dim=64, content_dim=16)
        sdm = SDMCore(config)
        valid_addr = np.zeros(64, dtype=np.uint8)
        valid_content = np.zeros(16, dtype=np.float32)

        with pytest.raises(ValueError, match="address dim"):
            sdm.write(np.zeros(63, dtype=np.uint8), valid_content)

        with pytest.raises(ValueError, match="content dim"):
            sdm.write(valid_addr, np.zeros(15, dtype=np.float32))

    def test_read_dimension_mismatch_raises(self):
        config = SDMConfig(num_locations=100, address_dim=64, content_dim=16)
        sdm = SDMCore(config)
        with pytest.raises(ValueError, match="address dim"):
            sdm.read(np.zeros(32, dtype=np.uint8))

    def test_write_increments_trace_count(self):
        config = SDMConfig(num_locations=100, address_dim=64, content_dim=16)
        sdm = SDMCore(config)
        addr = np.zeros(64, dtype=np.uint8)
        content = np.ones(16, dtype=np.float32)

        tid1 = sdm.write(addr, content)
        assert tid1 == 0
        assert sdm.trace_count == 1

        tid2 = sdm.write(addr, content)
        assert tid2 == 1
        assert sdm.trace_count == 2

    def test_read_on_empty_returns_zeros(self):
        config = SDMConfig(num_locations=100, address_dim=64, content_dim=16)
        sdm = SDMCore(config)
        addr = np.zeros(64, dtype=np.uint8)
        result = sdm.read(addr)
        assert result.shape == (16,)
        assert np.all(result == 0.0)

    def test_write_read_round_trip(self):
        config = SDMConfig(num_locations=200, address_dim=100, content_dim=32)
        sdm = SDMCore(config)
        content = np.random.default_rng(42).uniform(-1.0, 1.0, size=32).astype(np.float32)
        address = np.random.default_rng(42).integers(0, 2, size=100, dtype=np.uint8)

        sdm.write(address, content)
        recovered = sdm.read(address)
        assert recovered.shape == (32,)
        assert np.all(recovered >= -1.0) and np.all(recovered <= 1.0)
        # Direction should align (positive dot product)
        dot = np.dot(content, recovered)
        assert dot > 0

    def test_capacity_enforcement_raises_capacity_error(self):
        config = SDMConfig(num_locations=100, address_dim=64, content_dim=8, capacity=2)
        sdm = SDMCore(config)
        addr = np.zeros(64, dtype=np.uint8)
        content = np.zeros(8, dtype=np.float32)

        sdm.write(addr, content)
        sdm.write(addr, content)
        assert sdm.trace_count == 2

        with pytest.raises(CapacityError) as exc_info:
            sdm.write(addr, content)
        assert exc_info.value.capacity == 2

    def test_delete_removes_trace_and_decrements_count(self):
        config = SDMConfig(num_locations=100, address_dim=64, content_dim=8)
        sdm = SDMCore(config)
        addr = np.zeros(64, dtype=np.uint8)
        content = np.zeros(8, dtype=np.float32)

        tid = sdm.write(addr, content)
        assert sdm.trace_count == 1
        sdm.delete(tid)
        assert sdm.trace_count == 0

    def test_delete_unknown_id_raises_key_error(self):
        config = SDMConfig(num_locations=100, address_dim=64, content_dim=8)
        sdm = SDMCore(config)
        with pytest.raises(KeyError, match="not found"):
            sdm.delete(999)

    def test_memory_usage_bytes(self):
        config = SDMConfig(num_locations=100, address_dim=64, content_dim=16)
        sdm = SDMCore(config)
        expected = (
            sdm._hard_locs.nbytes
            + sdm._accumulator.nbytes
            + sdm._act_counts.nbytes
        )
        assert sdm.memory_usage_bytes() == expected
        assert expected > 0

    def test_fallback_activation_returns_at_least_one_location(self):
        # Setting a tiny radius fraction forces zero locations in radius for opposite vector
        config = SDMConfig(
            num_locations=100,
            address_dim=64,
            content_dim=8,
            hamming_radius_fraction=0.01,
        )
        sdm = SDMCore(config)
        # Even if radius is very small, _activate must return >= 1 location
        addr = np.zeros(64, dtype=np.uint8)
        activated = sdm._activate(addr)
        assert len(activated) >= 1
