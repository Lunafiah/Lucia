"""
Property-based tests for Lucia Memory Phase 2 (P19–P30).

Uses Hypothesis with max_examples=200.
"""

import numpy as np
import pytest
from hypothesis import HealthCheck, given, settings
from hypothesis import strategies as st

from src.core.errors import CapacityError
from src.core.memory.affective_memory import (
    AffectiveMemory,
    AffectiveMemoryConfig,
    MemoryTrace,
)
from src.core.memory.decay import DecayConfig, DecayEngine
from src.core.memory.ecphory import EcphoryConfig, EcphoryEngine
from src.core.memory.sdm import SDMConfig, SDMCore
from src.core.models import PADState

settings.register_profile(
    "phase2",
    max_examples=200,
    suppress_health_check=[HealthCheck.too_slow, HealthCheck.filter_too_much],
)
settings.load_profile("phase2")


# ----------------------------------------------------------------------
# Property 19: SDM Write/Read Approximate Inverse
# ----------------------------------------------------------------------
@given(
    content=st.lists(
        st.floats(-1.0, 1.0, allow_nan=False, allow_infinity=False),
        min_size=16,
        max_size=16,
    ).map(lambda lst: np.array(lst, dtype=np.float32))
)
def test_p19_sdm_write_read_approximate_inverse(content: np.ndarray):
    # Feature: lucia-memory-phase2, Property 19: SDM Write/Read Approximate Inverse
    sdm = SDMCore(
        SDMConfig(num_locations=200, address_dim=64, content_dim=16)
    )
    raw_addr = (content >= 0.0).astype(np.uint8)
    address = np.zeros(64, dtype=np.uint8)
    address[:16] = raw_addr

    sdm.write(address, content)
    recovered = sdm.read(address)

    assert recovered.shape == (16,)
    assert np.all(recovered >= -1.0) and np.all(recovered <= 1.0)

    norm_c = np.linalg.norm(content)
    norm_r = np.linalg.norm(recovered)
    if norm_c > 1e-5 and norm_r > 1e-5:
        cosine = np.dot(content, recovered) / (norm_c * norm_r)
        assert cosine > 0.0


# ----------------------------------------------------------------------
# Property 20: SDM Read Bounds Invariant
# ----------------------------------------------------------------------
@given(
    writes=st.lists(
        st.tuples(
            st.lists(st.integers(0, 1), min_size=64, max_size=64).map(
                lambda l: np.array(l, dtype=np.uint8)
            ),
            st.lists(
                st.floats(-1.0, 1.0, allow_nan=False, allow_infinity=False),
                min_size=16,
                max_size=16,
            ).map(lambda l: np.array(l, dtype=np.float32)),
        ),
        min_size=0,
        max_size=5,
    ),
    query_addr=st.lists(st.integers(0, 1), min_size=64, max_size=64).map(
        lambda l: np.array(l, dtype=np.uint8)
    ),
)
def test_p20_sdm_read_bounds_invariant(writes, query_addr):
    # Feature: lucia-memory-phase2, Property 20: SDM Read Bounds Invariant
    sdm = SDMCore(
        SDMConfig(num_locations=100, address_dim=64, content_dim=16)
    )
    for addr, content in writes:
        sdm.write(addr, content)

    result = sdm.read(query_addr)
    assert result.shape == (16,)
    assert result.dtype == np.float32
    assert np.all(result >= -1.0) and np.all(result <= 1.0)


# ----------------------------------------------------------------------
# Property 21: SDM Capacity Enforcement
# ----------------------------------------------------------------------
@given(
    capacity=st.integers(min_value=1, max_value=10),
    num_writes=st.integers(min_value=1, max_value=15),
)
def test_p21_sdm_capacity_enforcement(capacity: int, num_writes: int):
    # Feature: lucia-memory-phase2, Property 21: SDM Capacity Enforcement
    sdm = SDMCore(
        SDMConfig(
            num_locations=100, address_dim=64, content_dim=8, capacity=capacity
        )
    )
    addr = np.zeros(64, dtype=np.uint8)
    content = np.zeros(8, dtype=np.float32)

    written = 0
    for _ in range(num_writes):
        if written < capacity:
            sdm.write(addr, content)
            written += 1
            assert sdm.trace_count == written
        else:
            with pytest.raises(CapacityError):
                sdm.write(addr, content)


# ----------------------------------------------------------------------
# Property 22: Affective Memory Store/Retrieve Round Trip
# ----------------------------------------------------------------------
@given(
    content=st.lists(
        st.floats(-1.0, 1.0, allow_nan=False, allow_infinity=False),
        min_size=16,
        max_size=16,
    ).map(lambda l: np.array(l, dtype=np.float32)),
    p=st.floats(-1.0, 1.0, allow_nan=False, allow_infinity=False),
    a=st.floats(-1.0, 1.0, allow_nan=False, allow_infinity=False),
    d=st.floats(-1.0, 1.0, allow_nan=False, allow_infinity=False),
)
def test_p22_affective_memory_store_retrieve_round_trip(content, p, a, d):
    # Feature: lucia-memory-phase2, Property 22: Affective Memory Store/Retrieve Round Trip
    cfg = AffectiveMemoryConfig(
        sdm_config=SDMConfig(num_locations=100, address_dim=64, content_dim=16),
        m=16,
    )
    mem = AffectiveMemory(cfg)
    pad = PADState(pleasure=p, arousal=a, dominance=d, timestamp=123.0)

    trace_id = mem.store(content, pad)
    retrieved = mem.get_trace(trace_id)

    assert retrieved.trace_id == trace_id
    assert retrieved.pad_tag == pad
    assert retrieved.decay_weight == 1.0
    assert np.allclose(retrieved.content_vec, content)


# ----------------------------------------------------------------------
# Property 23: Decay Monotonicity
# ----------------------------------------------------------------------
@given(
    initial_weight=st.floats(0.0, 1.0, allow_nan=False, allow_infinity=False),
    base_rate=st.floats(1e-5, 0.99, allow_nan=False, allow_infinity=False),
    p=st.floats(-1.0, 1.0, allow_nan=False, allow_infinity=False),
    a=st.floats(-1.0, 1.0, allow_nan=False, allow_infinity=False),
    d=st.floats(-1.0, 1.0, allow_nan=False, allow_infinity=False),
    elapsed=st.floats(0.0, 86400.0, allow_nan=False, allow_infinity=False),
)
def test_p23_decay_monotonicity(initial_weight, base_rate, p, a, d, elapsed):
    # Feature: lucia-memory-phase2, Property 23: Decay Monotonicity
    mem = AffectiveMemory(
        AffectiveMemoryConfig(
            sdm_config=SDMConfig(num_locations=100, address_dim=64, content_dim=8),
            m=8,
        )
    )
    engine = DecayEngine(mem, DecayConfig(base_decay_rate=base_rate))
    pad = PADState(p, a, d, 0.0)

    rate = engine._decay_rate(pad)
    new_weight = float(np.clip(initial_weight - rate * elapsed, 0.0, 1.0))

    assert new_weight <= initial_weight + 1e-9
    assert 0.0 <= new_weight <= 1.0


# ----------------------------------------------------------------------
# Property 24: High-Intensity Traces Decay Slower
# ----------------------------------------------------------------------
@given(
    a_high=st.floats(0.5, 1.0, allow_nan=False, allow_infinity=False),
    p_high=st.floats(0.5, 1.0, allow_nan=False, allow_infinity=False),
    a_low=st.floats(0.0, 0.2, allow_nan=False, allow_infinity=False),
    p_low=st.floats(0.0, 0.2, allow_nan=False, allow_infinity=False),
    base_rate=st.floats(1e-4, 0.1, allow_nan=False, allow_infinity=False),
)
def test_p24_high_intensity_traces_decay_slower(
    a_high, p_high, a_low, p_low, base_rate
):
    # Feature: lucia-memory-phase2, Property 24: High-Intensity Traces Decay Slower
    mem = AffectiveMemory(
        AffectiveMemoryConfig(
            sdm_config=SDMConfig(num_locations=100, address_dim=64, content_dim=8),
            m=8,
        )
    )
    engine = DecayEngine(mem, DecayConfig(base_decay_rate=base_rate))

    pad_high = PADState(p_high, a_high, 0.0, 0.0)
    pad_low = PADState(p_low, a_low, 0.0, 0.0)

    intensity_high = engine._emotional_intensity(pad_high)
    intensity_low = engine._emotional_intensity(pad_low)

    if intensity_high > intensity_low:
        rate_high = engine._decay_rate(pad_high)
        rate_low = engine._decay_rate(pad_low)
        assert rate_high < rate_low


# ----------------------------------------------------------------------
# Property 25: Ecphory Determinism
# ----------------------------------------------------------------------
@given(
    p=st.floats(-1.0, 1.0, allow_nan=False, allow_infinity=False),
    a=st.floats(-1.0, 1.0, allow_nan=False, allow_infinity=False),
    d=st.floats(-1.0, 1.0, allow_nan=False, allow_infinity=False),
    num_traces=st.integers(0, 8),
)
def test_p25_ecphory_determinism(p, a, d, num_traces):
    # Feature: lucia-memory-phase2, Property 25: Ecphory Determinism
    engine = EcphoryEngine(EcphoryConfig())
    pad = PADState(p, a, d, 0.0)

    traces = [
        MemoryTrace(
            trace_id=i,
            address_vec=np.zeros(16, dtype=np.uint8),
            content_vec=np.ones(8, dtype=np.float32) * (i + 1),
            pad_tag=PADState(
                (i % 3 - 1) * 0.5, ((i + 1) % 3 - 1) * 0.5, 0.0, float(i)
            ),
            timestamp=float(i * 10),
            decay_weight=1.0 / (i + 1),
        )
        for i in range(num_traces)
    ]

    res1 = engine.query(pad, traces)
    res2 = engine.query(pad, traces)

    if res1 is None:
        assert res2 is None
    else:
        assert res2 is not None
        assert np.array_equal(res1, res2)


# ----------------------------------------------------------------------
# Property 26: Echo Vector Bounds Invariant
# ----------------------------------------------------------------------
@given(
    content_vals=st.lists(
        st.floats(-1.0, 1.0, allow_nan=False, allow_infinity=False),
        min_size=8,
        max_size=8,
    ).map(lambda l: np.array(l, dtype=np.float32)),
    p=st.floats(0.2, 1.0, allow_nan=False, allow_infinity=False),
    a=st.floats(0.2, 1.0, allow_nan=False, allow_infinity=False),
    d=st.floats(0.2, 1.0, allow_nan=False, allow_infinity=False),
)
def test_p26_echo_vector_bounds_invariant(content_vals, p, a, d):
    # Feature: lucia-memory-phase2, Property 26: Echo Vector Bounds Invariant
    engine = EcphoryEngine(
        EcphoryConfig(resonance_threshold=0.5, ecphory_k=5)
    )
    pad = PADState(p, a, d, 0.0)
    # Trace perfectly matching PAD state ensures resonance > 0.5
    traces = [
        MemoryTrace(
            trace_id=0,
            address_vec=np.zeros(16, dtype=np.uint8),
            content_vec=content_vals,
            pad_tag=pad,
            timestamp=0.0,
            decay_weight=1.0,
        )
    ]

    echo = engine.query(pad, traces)
    assert echo is not None
    assert echo.shape == (8,)
    assert echo.dtype == np.float32
    assert np.all(echo >= -1.0) and np.all(echo <= 1.0)


# ----------------------------------------------------------------------
# Property 27: Ecphory Top-K Constraint
# ----------------------------------------------------------------------
def test_p27_ecphory_top_k_constraint():
    # Feature: lucia-memory-phase2, Property 27: Ecphory Top-K Constraint
    k = 3
    engine = EcphoryEngine(
        EcphoryConfig(resonance_threshold=0.0, ecphory_k=k)
    )
    query_pad = PADState(1.0, 0.0, 0.0, 0.0)

    # 5 traces (K+2) with strictly decreasing resonance scores with query_pad
    # cos scores: 1.0, 0.8, 0.6, 0.4, 0.2
    cos_angles = [0.0, 0.6435, 0.9273, 1.1593, 1.3694]
    traces = []
    for i, angle in enumerate(cos_angles):
        p_val = float(np.cos(angle))
        a_val = float(np.sin(angle))
        traces.append(
            MemoryTrace(
                trace_id=i,
                address_vec=np.zeros(8, dtype=np.uint8),
                content_vec=np.ones(4, dtype=np.float32) * (i + 1),
                pad_tag=PADState(p_val, a_val, 0.0, 0.0),
                timestamp=0.0,
                decay_weight=1.0,
            )
        )

    all_echo = engine.query(query_pad, traces)
    top_k_echo = engine.query(query_pad, traces[:k])

    assert all_echo is not None
    assert top_k_echo is not None
    assert np.allclose(all_echo, top_k_echo)


# ----------------------------------------------------------------------
# Property 30: No-Timeline Invariant — Timestamp Independence
# ----------------------------------------------------------------------
@given(
    timestamps=st.lists(
        st.floats(0.0, 1e6, allow_nan=False, allow_infinity=False),
        min_size=4,
        max_size=4,
    )
)
def test_p30_timestamp_independence(timestamps):
    # Feature: lucia-memory-phase2, Property 30: No-Timeline Invariant — Timestamp Independence
    engine = EcphoryEngine(EcphoryConfig(resonance_threshold=0.0, ecphory_k=4))
    query_pad = PADState(0.5, 0.5, 0.5, 1000.0)

    traces_orig = [
        MemoryTrace(
            trace_id=i,
            address_vec=np.zeros(8, dtype=np.uint8),
            content_vec=np.array([float(i), float(-i)], dtype=np.float32),
            pad_tag=PADState(0.5, 0.5, 0.5, 0.0),
            timestamp=float(i * 100),
            decay_weight=1.0,
        )
        for i in range(4)
    ]

    traces_permuted = [
        MemoryTrace(
            trace_id=i,
            address_vec=np.zeros(8, dtype=np.uint8),
            content_vec=np.array([float(i), float(-i)], dtype=np.float32),
            pad_tag=PADState(0.5, 0.5, 0.5, 0.0),
            timestamp=timestamps[i],  # different timestamp
            decay_weight=1.0,
        )
        for i in range(4)
    ]

    echo_orig = engine.query(query_pad, traces_orig)
    echo_perm = engine.query(query_pad, traces_permuted)

    assert echo_orig is not None
    assert echo_perm is not None
    assert np.allclose(echo_orig, echo_perm)


# ----------------------------------------------------------------------
# Property 28: No-Recall Language in Echo Section
# ----------------------------------------------------------------------
@given(
    echo_vector=st.lists(
        st.floats(-1.0, 1.0, allow_nan=False, allow_infinity=False),
        min_size=64,
        max_size=64,
    ).map(lambda l: np.array(l, dtype=np.float32))
)
def test_p28_no_recall_language_in_echo_section(echo_vector):
    # Feature: lucia-memory-phase2, Property 28: No-Recall Language in Echo Section
    from src.core.orchestrator.prompt_assembler import (
        FORBIDDEN_RECALL_PHRASES,
        PromptAssembler,
    )

    assembler = PromptAssembler()
    encoded = assembler._encode_echo_section(echo_vector)

    assert "[MEMORY ECHO]" in encoded
    for phrase in FORBIDDEN_RECALL_PHRASES:
        assert phrase.lower() not in encoded.lower()


# ----------------------------------------------------------------------
# Property 29: Echo Section Present <-> Non-None Echo Vector
# ----------------------------------------------------------------------
@given(
    echo_opt=st.one_of(
        st.none(),
        st.lists(
            st.floats(-1.0, 1.0, allow_nan=False, allow_infinity=False),
            min_size=16,
            max_size=16,
        ).map(lambda l: np.array(l, dtype=np.float32)),
    )
)
def test_p29_echo_section_presence(echo_opt):
    # Feature: lucia-memory-phase2, Property 29: Echo Section Present <-> Non-None Echo Vector
    from src.core.models import BehavioralConstraints, SomaticMarkers
    from src.core.orchestrator.prompt_assembler import PromptAssembler

    assembler = PromptAssembler()
    somatic = SomaticMarkers(0.8, 0.2, 0.9, 0.1)
    constraints = BehavioralConstraints(150, 0.75, 0, 1)

    prompt = assembler.assemble(
        somatic=somatic,
        constraints=constraints,
        history=[],
        echo_vector=echo_opt,
    )

    if echo_opt is None:
        assert "[MEMORY ECHO]" not in prompt
        assert "echo_" not in prompt
    else:
        assert "[MEMORY ECHO]" in prompt
        assert "echo_0:" in prompt
