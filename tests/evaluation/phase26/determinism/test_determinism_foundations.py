"""
tests/evaluation/phase26/determinism/test_determinism_foundations.py

Unit and integration tests for Phase 26 Determinism Foundations.
Validates SeededSDMFactory, VirtualClockHarness, SeededLLMWrapper,
and executes ReproducibilityEvaluator.
"""

import numpy as np
import pytest

from src.core.config import EmotionConfig
from src.core.emotion.emotion_core import EmotionCore
from src.core.memory.sdm import SDMConfig
from tests.evaluation.phase26.determinism.reproducibility_evaluator import (
    ReproducibilityEvaluator,
)
from tests.evaluation.phase26.determinism.seeded_llm_wrapper import (
    DeterministicMockLLMBackend,
    SeededLLMWrapper,
)
from tests.evaluation.phase26.determinism.seeded_sdm_factory import SeededSDMFactory
from tests.evaluation.phase26.determinism.virtual_clock_harness import VirtualClockHarness


def test_seeded_sdm_factory_bit_exactness():
    config = SDMConfig(num_locations=150, address_dim=64, content_dim=16)
    sdm_1 = SeededSDMFactory.create_seeded_sdm(config, seed=1001)
    sdm_2 = SeededSDMFactory.create_seeded_sdm(config, seed=1001)
    sdm_diff = SeededSDMFactory.create_seeded_sdm(config, seed=2002)

    # Identical seeds must match bit-exact
    assert np.array_equal(sdm_1._hard_locs, sdm_2._hard_locs)

    # Different seeds must differ
    assert not np.array_equal(sdm_1._hard_locs, sdm_diff._hard_locs)

    # Activations must be identical
    addr = np.ones(64, dtype=np.uint8)
    assert np.array_equal(sdm_1._activate(addr), sdm_2._activate(addr))


def test_sdm_topology_cloning():
    config = SDMConfig(num_locations=150, address_dim=64, content_dim=16)
    sdm_orig = SeededSDMFactory.create_seeded_sdm(config, seed=555)

    # Write a trace to sdm_orig
    addr = np.zeros(64, dtype=np.uint8)
    cont = np.ones(16, dtype=np.float32)
    sdm_orig.write(addr, cont)
    assert sdm_orig.trace_count == 1

    # Cloned instance must share topology but be clean
    sdm_clone = SeededSDMFactory.clone_sdm_topology(sdm_orig)
    assert np.array_equal(sdm_clone._hard_locs, sdm_orig._hard_locs)
    assert sdm_clone.trace_count == 0


def test_virtual_clock_harness_determinism():
    core_1 = EmotionCore(EmotionConfig())
    core_2 = EmotionCore(EmotionConfig())

    clock_1 = VirtualClockHarness(core_1, initial_time=50.0)
    clock_2 = VirtualClockHarness(core_2, initial_time=50.0)

    stim = np.array([0.5, 0.2, 0.1] + [0.0] * 13, dtype=np.float64)

    # Step both 5 times with identical stimulus
    for _ in range(5):
        pad_1 = clock_1.push_and_step(stim, dt=0.200)
        pad_2 = clock_2.push_and_step(stim, dt=0.200)

        assert abs(pad_1.pleasure - pad_2.pleasure) < 1e-12
        assert abs(pad_1.arousal - pad_2.arousal) < 1e-12
        assert abs(pad_1.dominance - pad_2.dominance) < 1e-12
        assert pad_1.timestamp == pad_2.timestamp

    # Relaxation test
    conv_1, steps_1, dist_1 = clock_1.relax_to_resting(tolerance=1e-3)
    conv_2, steps_2, dist_2 = clock_2.relax_to_resting(tolerance=1e-3)

    assert conv_1 == conv_2
    assert steps_1 == steps_2
    assert abs(dist_1 - dist_2) < 1e-12


def test_seeded_llm_wrapper_reproducibility():
    mock_backend = DeterministicMockLLMBackend()
    wrapper = SeededLLMWrapper(mock_backend)

    prompt = "We have one archival research hour. Should we inspect Deep-sea hydrothermal ecosystems or Medieval maritime cartography first?"

    # Fixed seed produces identical string
    out_1 = wrapper.generate(prompt, seed=42)
    out_2 = wrapper.generate(prompt, seed=42)
    assert out_1 == out_2

    # Different seeds can diverge
    # Check that wrapper updates tracking
    assert wrapper.call_count == 2
    assert wrapper.last_seed_used == 42


def test_reproducibility_evaluator_audit():
    result = ReproducibilityEvaluator.run_full_audit()

    assert result.sdm_hard_locs_bit_exact is True
    assert result.sdm_activation_residual == 0.0
    assert result.emotion_pad_max_divergence < 1e-12
    assert result.llm_exact_match_rate == 1.0
    assert result.summary_verdict == "PASS_ZERO_DRIFT"
