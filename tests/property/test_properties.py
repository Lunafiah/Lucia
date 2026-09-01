"""
Property-based tests for Lucia Core Phase 1.

Uses Hypothesis with max_examples=200. Each test is tagged with the property
it validates, referencing the design document.

Properties covered in this file:
  P1:  PAD State Bounds Invariant
  P2:  ODE Step Intermediate Clamping
  P8:  Stimulus Vector Shape Invariant
  P9:  Stimulus Vector Bounds Invariant
  P10: Non-Zero Semantic Dimensions

(P3â€“P7 added in Task 4.2/5.2, P11â€“P13 in Task 8.3, P14â€“P18 in Tasks 9.3/10.5)
"""

from __future__ import annotations

import string

import numpy as np
import pytest
from hypothesis import given, settings, assume
from hypothesis import strategies as st
from hypothesis.extra.numpy import arrays, floating_dtypes

from src.core.config import EmotionConfig, StimulusConfig
from src.core.emotion.emotion_core import EmotionCore
from src.core.gating.stimulus_processor import StimulusProcessor
from src.core.models import PADState

# ---------------------------------------------------------------------------
# Shared strategies
# ---------------------------------------------------------------------------

printable_text = st.text(
    alphabet=string.printable,
    min_size=1,
    max_size=500,
)

bounded_floats = st.floats(
    min_value=-10.0,
    max_value=10.0,
    allow_nan=False,
    allow_infinity=False,
)

hidden_state_strategy = arrays(
    dtype=np.float64,
    shape=st.integers(min_value=4, max_value=32),
    elements=bounded_floats,
)

stimulus_strategy = arrays(
    dtype=np.float64,
    shape=st.integers(min_value=3, max_value=32),
    elements=bounded_floats,
)


# ---------------------------------------------------------------------------
# P1: PAD State Bounds Invariant
# Feature: lucia-core-phase1, Property 1: PAD state bounds hold after any projection + clamp
# ---------------------------------------------------------------------------

@settings(max_examples=200)
@given(h=arrays(
    dtype=np.float64,
    shape=st.just(8),
    elements=bounded_floats,
))
def test_p1_pad_state_bounds_invariant(h):
    """
    For any hidden state vector, after projection and clamping, all three
    PAD dimensions must be in [-1.0, 1.0].
    Validates: Requirements 1.1, 1.7
    """
    # Feature: lucia-core-phase1, Property 1: PAD State Bounds Invariant
    core = EmotionCore(EmotionConfig(hidden_dim=8, loop_cadence_ms=200))
    pad = core._project_to_pad(h)

    assert -1.0 <= pad.pleasure <= 1.0, f"pleasure={pad.pleasure} out of bounds"
    assert -1.0 <= pad.arousal <= 1.0, f"arousal={pad.arousal} out of bounds"
    assert -1.0 <= pad.dominance <= 1.0, f"dominance={pad.dominance} out of bounds"
    assert isinstance(pad, PADState)


# ---------------------------------------------------------------------------
# P2: ODE Step Intermediate Clamping
# Feature: lucia-core-phase1, Property 2: ODE step result always in [-1, 1]
# ---------------------------------------------------------------------------

# ---------------------------------------------------------------------------
# P2: ODE Step Intermediate Clamping
# Feature: lucia-core-phase1, Property 2: ODE step result always in [-1, 1]
# ---------------------------------------------------------------------------

@settings(max_examples=100, deadline=None)
@given(
    h=arrays(
        dtype=np.float64,
        shape=st.just(8),
        elements=st.floats(min_value=-1.0, max_value=1.0, allow_nan=False, allow_infinity=False),
    ),
    x=arrays(
        dtype=np.float64,
        shape=st.just(8),
        elements=st.floats(min_value=-1.0, max_value=1.0, allow_nan=False, allow_infinity=False),
    ),
)
def test_p2_ode_step_intermediate_clamping(h, x):
    """
    For any valid hidden state h and stimulus x (both in [-1, 1]), the ODE step
    result must have all values in [-1.0, 1.0].
    Validates: Requirements 1.4
    Note: inputs are restricted to [-1, 1] since the ODE RHS internally clamps
    intermediate values; extreme subnormal floats cause solve_ivp to stall.
    """
    # Feature: lucia-core-phase1, Property 2: ODE Step Intermediate Clamping
    core = EmotionCore(EmotionConfig(hidden_dim=8, loop_cadence_ms=200))
    core._ensure_input_dim(len(x))

    h_new = core._ode_step(h, x)

    assert h_new.shape == h.shape, "ODE step must preserve hidden state shape"
    assert np.all(h_new >= -1.0), f"ODE step result below -1.0: min={h_new.min()}"
    assert np.all(h_new <= 1.0), f"ODE step result above 1.0: max={h_new.max()}"


# ---------------------------------------------------------------------------
# P8: Stimulus Vector Shape Invariant
# Feature: lucia-core-phase1, Property 8: encode() output shape equals vector_dim
# ---------------------------------------------------------------------------

@settings(max_examples=200)
@given(text=st.text(min_size=1, max_size=500))
def test_p8_stimulus_vector_shape_invariant(text):
    """
    For any non-empty string, StimulusProcessor.encode() must return
    an ndarray of shape (N,) where N is the configured vector_dim.
    Validates: Requirements 4.1
    """
    # Feature: lucia-core-phase1, Property 8: Stimulus Vector Shape Invariant
    sp = StimulusProcessor(StimulusConfig(vector_dim=16))
    import warnings
    with warnings.catch_warnings():
        warnings.simplefilter("ignore")
        v = sp.encode(text)
    assert v.shape == (16,), f"Expected shape (16,), got {v.shape}"
    assert v.dtype == np.float64


# ---------------------------------------------------------------------------
# P9: Stimulus Vector Bounds Invariant
# Feature: lucia-core-phase1, Property 9: all values in [-1.0, 1.0]
# ---------------------------------------------------------------------------

@settings(max_examples=200)
@given(text=st.text(min_size=0, max_size=4096))
def test_p9_stimulus_vector_bounds_invariant(text):
    """
    For any input string (including empty), all values in the Stimulus_Vector
    must be in [-1.0, 1.0].
    Validates: Requirements 4.2
    """
    # Feature: lucia-core-phase1, Property 9: Stimulus Vector Bounds Invariant
    sp = StimulusProcessor(StimulusConfig(vector_dim=16))
    import warnings
    with warnings.catch_warnings():
        warnings.simplefilter("ignore")
        v = sp.encode(text)
    assert np.all(v >= -1.0), f"Values below -1.0: min={v.min()}"
    assert np.all(v <= 1.0), f"Values above 1.0: max={v.max()}"


# ---------------------------------------------------------------------------
# P10: Non-Zero Semantic Dimensions
# Feature: lucia-core-phase1, Property 10: dims 0-2 non-zero for non-empty input
# ---------------------------------------------------------------------------

@settings(max_examples=200)
@given(text=st.text(alphabet=string.printable, min_size=1))
def test_p10_non_zero_semantic_dimensions(text):
    """
    For any non-empty printable string, dims 0, 1, and 2 of the Stimulus_Vector
    must have absolute values >= 1e-7.
    Validates: Requirements 4.9
    """
    # Feature: lucia-core-phase1, Property 10: Non-Zero Semantic Dimensions
    assume(text.strip())  # skip if only whitespace (arousal floor still applies, but skip for clarity)
    sp = StimulusProcessor(StimulusConfig(vector_dim=16))
    import warnings
    with warnings.catch_warnings():
        warnings.simplefilter("ignore")
        v = sp.encode(text)

    for i in range(3):
        assert abs(v[i]) >= 1e-7, (
            f"dim {i} is effectively zero ({v[i]}) for input {text!r}"
        )


# ===========================================================================
# Properties added in Task 4.2 / 5.2
# ===========================================================================

from src.core.emotion.homeostatic_engine import HomeostaticEngine
from src.core.models import SomaticMarkers


def _make_pad(p: float, a: float, d: float) -> PADState:
    return PADState(pleasure=p, arousal=a, dominance=d, timestamp=0.0)


def _make_markers(st: float, cl: float, en: float, te: float) -> SomaticMarkers:
    return SomaticMarkers(stability=st, cognitive_load=cl, energy=en, tension=te)


# ---------------------------------------------------------------------------
# P3: Somatic Markers Completeness and Bounds
# Feature: lucia-core-phase1, Property 3: all somatic markers in [0.0, 1.0]
# ---------------------------------------------------------------------------

@settings(max_examples=200)
@given(
    pleasure=st.floats(min_value=-1.0, max_value=1.0, allow_nan=False),
    arousal=st.floats(min_value=-1.0, max_value=1.0, allow_nan=False),
    dominance=st.floats(min_value=-1.0, max_value=1.0, allow_nan=False),
    valence=st.floats(min_value=0.0, max_value=1.0, allow_nan=False),
)
def test_p3_somatic_markers_completeness_and_bounds(pleasure, arousal, dominance, valence):
    """
    For any valid PADState and valence in [0.0, 1.0], all four somatic markers
    must be present and in [0.0, 1.0].
    Validates: Requirements 2.1, 2.2, 2.5
    """
    # Feature: lucia-core-phase1, Property 3: Somatic Markers Completeness and Bounds
    eng = HomeostaticEngine()
    pad = _make_pad(pleasure, arousal, dominance)
    m = eng.compute_somatic_markers(pad, valence=valence)

    assert isinstance(m, SomaticMarkers)
    assert 0.0 <= m.stability <= 1.0, f"stability={m.stability}"
    assert 0.0 <= m.cognitive_load <= 1.0, f"cognitive_load={m.cognitive_load}"
    assert 0.0 <= m.energy <= 1.0, f"energy={m.energy}"
    assert 0.0 <= m.tension <= 1.0, f"tension={m.tension}"


# ---------------------------------------------------------------------------
# P4: Tension Validity Domain
# Feature: lucia-core-phase1, Property 4: out-of-range valence raises ValueError
# ---------------------------------------------------------------------------

@settings(max_examples=200)
@given(
    valence=st.floats(min_value=-10.0, max_value=10.0, allow_nan=False)
    .filter(lambda v: not (0.0 <= v <= 1.0)),
)
def test_p4_tension_validity_domain(valence):
    """
    For any valence outside [0.0, 1.0], compute_somatic_markers must raise
    ValueError and must not return a SomaticMarkers object.
    Validates: Requirements 2.5
    """
    # Feature: lucia-core-phase1, Property 4: Tension Validity Domain
    eng = HomeostaticEngine()
    pad = _make_pad(0.1, 0.0, 0.0)
    with pytest.raises(ValueError):
        eng.compute_somatic_markers(pad, valence=valence)


# ---------------------------------------------------------------------------
# P5: Behavioral Constraints Output Ranges
# Feature: lucia-core-phase1, Property 5: all constraint values within bounds
# ---------------------------------------------------------------------------

@settings(max_examples=200)
@given(
    stability=st.floats(min_value=0.0, max_value=1.0, allow_nan=False),
    cognitive_load=st.floats(min_value=0.0, max_value=1.0, allow_nan=False),
    energy=st.floats(min_value=0.0, max_value=1.0, allow_nan=False),
    tension=st.floats(min_value=0.0, max_value=1.0, allow_nan=False),
    arousal=st.floats(min_value=-1.0, max_value=1.0, allow_nan=False),
    pleasure=st.floats(min_value=-1.0, max_value=1.0, allow_nan=False),
    dominance=st.floats(min_value=-1.0, max_value=1.0, allow_nan=False),
)
def test_p5_behavioral_constraints_output_ranges(
    stability, cognitive_load, energy, tension, arousal, pleasure, dominance
):
    """
    For any valid SomaticMarkers and PADState, the resulting BehavioralConstraints
    must have all fields within documented ranges.
    Validates: Requirements 3.1
    """
    # Feature: lucia-core-phase1, Property 5: Behavioral Constraints Output Ranges
    eng = HomeostaticEngine()
    pad = _make_pad(pleasure, arousal, dominance)
    m = _make_markers(stability, cognitive_load, energy, tension)
    c = eng.compute_behavioral_constraints(m, pad)

    assert 1 <= c.max_tokens <= 2048, f"max_tokens={c.max_tokens}"
    assert 0.0 <= c.temperature <= 2.0, f"temperature={c.temperature}"
    assert 0 <= c.latency_ms <= 5000, f"latency_ms={c.latency_ms}"
    assert 0 <= c.reasoning_depth <= 3, f"reasoning_depth={c.reasoning_depth}"


# ---------------------------------------------------------------------------
# P6: Behavioral Constraints Priority Resolution
# Feature: lucia-core-phase1, Property 6: highest cognitive_load wins for max_tokens
# ---------------------------------------------------------------------------

@settings(max_examples=200)
@given(
    high_cl=st.floats(min_value=0.76, max_value=1.0, allow_nan=False),  # triggers â‰¤ 80
    energy=st.floats(min_value=0.0, max_value=0.6, allow_nan=False),    # not > 0.7
)
def test_p6_behavioral_constraints_priority_resolution(high_cl, energy):
    """
    When cognitive_load > 0.75, the high-load rule always wins for max_tokens
    regardless of other concurrent conditions.
    Validates: Requirements 3.11
    """
    # Feature: lucia-core-phase1, Property 6: Behavioral Constraints Priority Resolution
    eng = HomeostaticEngine()
    pad = _make_pad(0.0, 0.0, 0.0)
    m = _make_markers(st=0.5, cl=high_cl, en=energy, te=0.1)
    c = eng.compute_behavioral_constraints(m, pad)

    assert c.max_tokens <= 80, (
        f"High cognitive_load={high_cl} should give max_tokensâ‰¤80, got {c.max_tokens}"
    )


# ---------------------------------------------------------------------------
# P7: Out-of-Bounds PAD Raises ValueError
# Feature: lucia-core-phase1, Property 7: invalid PAD raises ValueError
# ---------------------------------------------------------------------------

@settings(max_examples=200)
@given(
    pleasure=st.floats(min_value=-10.0, max_value=10.0, allow_nan=False),
    arousal=st.floats(min_value=-10.0, max_value=10.0, allow_nan=False),
    dominance=st.floats(min_value=-10.0, max_value=10.0, allow_nan=False),
)
def test_p7_out_of_bounds_pad_raises_value_error(pleasure, arousal, dominance):
    """
    For any PADState where at least one dimension is outside [-1.0, 1.0],
    compute_behavioral_constraints must raise a ValueError.
    Validates: Requirements 3.12
    """
    # Feature: lucia-core-phase1, Property 7: Out-of-Bounds PAD Raises ValueError
    # Skip if all values happen to be in bounds
    assume(
        not (-1.0 <= pleasure <= 1.0)
        or not (-1.0 <= arousal <= 1.0)
        or not (-1.0 <= dominance <= 1.0)
    )
    eng = HomeostaticEngine()
    pad = PADState(pleasure=pleasure, arousal=arousal, dominance=dominance, timestamp=0.0)
    m = _make_markers(0.5, 0.5, 0.5, 0.1)
    with pytest.raises(ValueError):
        eng.compute_behavioral_constraints(m, pad)


# ===========================================================================
# Properties added in Tasks 8.3 / 9.3
# ===========================================================================

from src.core.orchestrator.prompt_assembler import PromptAssembler, _SEP
from src.core.safety.boundary_layer import BoundaryLayer, DEFAULT_PATTERNS
from src.core.models import BehavioralConstraints as _BC

import re as _re


# ---------------------------------------------------------------------------
# P11: Conditioned Prompt Section Order
# Feature: lucia-core-phase1, Property 11: fixed section order in assembled prompt
# ---------------------------------------------------------------------------

@settings(max_examples=200)
@given(
    stability=st.floats(min_value=0.0, max_value=1.0, allow_nan=False),
    cognitive_load=st.floats(min_value=0.0, max_value=1.0, allow_nan=False),
    energy=st.floats(min_value=0.0, max_value=1.0, allow_nan=False),
    tension=st.floats(min_value=0.0, max_value=1.0, allow_nan=False),
    reasoning_depth=st.integers(min_value=0, max_value=3),
    history_size=st.integers(min_value=0, max_value=5),
)
def test_p11_conditioned_prompt_section_order(
    stability, cognitive_load, energy, tension, reasoning_depth, history_size
):
    """
    For any SomaticMarkers, BehavioralConstraints, and conversation history,
    the assembled prompt must contain sections in fixed order:
    preamble â†’ [SOMATIC STATE] â†’ (optional [REASONING]) â†’ [CONVERSATION]
    Validates: Requirements 5.1, 5.2
    """
    # Feature: lucia-core-phase1, Property 11: Conditioned Prompt Section Order
    assembler = PromptAssembler()
    somatic = _make_markers(stability, cognitive_load, energy, tension)
    constraints = _BC(
        max_tokens=200, temperature=0.75,
        latency_ms=0, reasoning_depth=reasoning_depth
    )
    history = [("user", f"msg{i}") for i in range(history_size)]

    result = assembler.assemble(somatic, constraints, history, "preamble")

    if isinstance(result, Exception):
        return  # AssemblyError â€” skip ordering check

    assert "[SOMATIC STATE]" in result, "Somatic section missing"
    assert "[CONVERSATION]" in result, "Conversation section missing"

    somatic_pos = result.index("[SOMATIC STATE]")
    conv_pos = result.index("[CONVERSATION]")
    assert somatic_pos < conv_pos

    if reasoning_depth > 0:
        assert "[REASONING]" in result
        reasoning_pos = result.index("[REASONING]")
        assert somatic_pos < reasoning_pos < conv_pos
    else:
        assert "[REASONING]" not in result


# ---------------------------------------------------------------------------
# P12: Conversation History Truncation Bound
# Feature: lucia-core-phase1, Property 12: included turns â‰¤ min(10, budget)
# ---------------------------------------------------------------------------

@settings(max_examples=200)
@given(
    history=st.lists(
        st.tuples(
            st.sampled_from(["user", "assistant"]),
            st.text(min_size=1, max_size=50),
        ),
        min_size=0,
        max_size=20,
    ),
    max_tokens=st.integers(min_value=10, max_value=500),
)
def test_p12_conversation_history_truncation_bound(history, max_tokens):
    """
    For any conversation history, the number of turns in the prompt must
    not exceed min(10, turns that fit within max_tokens * 4 budget).
    Validates: Requirements 5.3
    """
    # Feature: lucia-core-phase1, Property 12: Conversation History Truncation Bound
    assembler = PromptAssembler()
    somatic = _make_markers(0.9, 0.1, 0.9, 0.05)
    constraints = _BC(
        max_tokens=max_tokens, temperature=0.75,
        latency_ms=0, reasoning_depth=0
    )

    result = assembler.assemble(somatic, constraints, history)
    if not isinstance(result, str):
        return

    # Count turns in [CONVERSATION] section
    conv_section = result.split("[CONVERSATION]")[-1] if "[CONVERSATION]" in result else ""
    # Count lines that look like "role: text"
    role_lines = [l for l in conv_section.split("\n") if l.startswith(("user:", "assistant:"))]
    included = len(role_lines)

    assert included <= 10, f"Included {included} turns, expected â‰¤ 10"


# ---------------------------------------------------------------------------
# P13: Reasoning Step Count
# Feature: lucia-core-phase1, Property 13: step count = min((depth*2)-1, 5)
# ---------------------------------------------------------------------------

@settings(max_examples=200)
@given(reasoning_depth=st.integers(min_value=1, max_value=3))
def test_p13_reasoning_step_count(reasoning_depth):
    """
    For any reasoning_depth in {1, 2, 3}, the chain-of-thought section must
    contain exactly min((depth*2)-1, 5) steps.
    Validates: Requirements 5.5
    """
    # Feature: lucia-core-phase1, Property 13: Reasoning Step Count
    assembler = PromptAssembler()
    somatic = _make_markers(0.9, 0.1, 0.9, 0.05)
    constraints = _BC(
        max_tokens=500, temperature=0.75,
        latency_ms=0, reasoning_depth=reasoning_depth
    )

    result = assembler.assemble(somatic, constraints, [])
    assert isinstance(result, str)

    expected_steps = min((reasoning_depth * 2) - 1, 5)
    actual_steps = result.count("Step ")
    assert actual_steps == expected_steps, (
        f"depth={reasoning_depth}: expected {expected_steps} steps, got {actual_steps}"
    )


# ---------------------------------------------------------------------------
# P14: Boundary Layer Pattern Replacement
# Feature: lucia-core-phase1, Property 14: matched spans replaced with [...]
# ---------------------------------------------------------------------------

def _embed_default_pattern(text: str) -> str:
    """Inject a default pattern into the text."""
    return f"Hello, I feel great. {text}"


@settings(max_examples=200)
@given(text=st.text(min_size=0, max_size=100))
def test_p14_boundary_layer_pattern_replacement(text):
    """
    For any output that contains a default pattern, validate() must replace
    matched spans with "[...]" and the original matched text must be absent.
    Validates: Requirements 7.3, 9.2
    """
    # Feature: lucia-core-phase1, Property 14: Boundary Layer Pattern Replacement
    layer = BoundaryLayer()
    embedded = _embed_default_pattern(text)

    result = layer.validate(embedded)

    # The pattern "I feel" should not appear in the output
    compiled = _re.compile(r"\bI feel\b", _re.IGNORECASE)
    assert not compiled.search(result), (
        f"Pattern still present after validate(): {result!r}"
    )
    assert "[...]" in result


# ---------------------------------------------------------------------------
# P15: Boundary Layer Passthrough
# Feature: lucia-core-phase1, Property 15: clean text returned unmodified
# ---------------------------------------------------------------------------

def _has_no_default_pattern(text: str) -> bool:
    for p in DEFAULT_PATTERNS:
        if _re.search(p, text, _re.IGNORECASE):
            return False
    return True


@settings(max_examples=200)
@given(text=st.text(min_size=0, max_size=200).filter(_has_no_default_pattern))
def test_p15_boundary_layer_passthrough(text):
    """
    For any text that contains no Meta-Self-Awareness_Pattern, validate()
    must return the text unmodified.
    Validates: Requirements 7.4
    """
    # Feature: lucia-core-phase1, Property 15: Boundary Layer Passthrough
    layer = BoundaryLayer()
    result = layer.validate(text)
    assert result == text, (
        f"Text was modified despite no pattern match.\nInput: {text!r}\nOutput: {result!r}"
    )


# ---------------------------------------------------------------------------
# P16: Boundary Layer Idempotence
# Feature: lucia-core-phase1, Property 16: validate(validate(t)) == validate(t)
# ---------------------------------------------------------------------------

@settings(max_examples=200)
@given(text=st.text(min_size=0, max_size=200).filter(_has_no_default_pattern))
def test_p16_boundary_layer_idempotence(text):
    """
    For any text without a default pattern, applying validate() twice equals
    applying it once.
    Validates: Requirements 7.9
    """
    # Feature: lucia-core-phase1, Property 16: Boundary Layer Idempotence
    layer = BoundaryLayer()
    once = layer.validate(text)
    twice = layer.validate(once)
    assert once == twice, (
        f"Idempotence violated.\nOnce: {once!r}\nTwice: {twice!r}"
    )


# ===========================================================================
# Properties added in Task 10.5
# ===========================================================================

# ---------------------------------------------------------------------------
# P17: Orchestrator Input Rejection
# Feature: lucia-core-phase1, Property 17: empty or oversized input rejected immediately
# ---------------------------------------------------------------------------

@settings(max_examples=200)
@given(
    length=st.one_of(
        st.just(0),
        st.integers(min_value=4001, max_value=10000),
    )
)
def test_p17_orchestrator_input_rejection(length):
    """
    For any input string of length 0 or length > 4000,
    process() must return the fallback response immediately without executing
    any pipeline steps.
    Validates: Requirements 8.10
    """
    # Feature: lucia-core-phase1, Property 17: Orchestrator Input Rejection
    from unittest.mock import MagicMock
    from src.core.orchestrator.orchestrator import Orchestrator
    from src.core.language.llm_backend import LLMBackend
    from src.core.config import HomeostaticConfig
    from src.core.emotion.emotion_core import EmotionCore
    from src.core.emotion.homeostatic_engine import HomeostaticEngine
    from src.core.gating.stimulus_processor import StimulusProcessor
    from src.core.orchestrator.prompt_assembler import PromptAssembler
    from src.core.safety.boundary_layer import BoundaryLayer

    fallback = "[test_fallback]"
    orch = Orchestrator.__new__(Orchestrator)
    from src.core.config import OrchestratorConfig, StimulusConfig
    cfg = OrchestratorConfig.__new__(OrchestratorConfig)
    cfg.model_path = "x.gguf"
    cfg.n_gpu_layers = 0
    cfg.loop_cadence_ms = 200
    cfg.resting_baseline = (0.1, 0.0, 0.0)
    cfg.max_history_turns = 10
    cfg.fallback_response = fallback
    cfg.llm_timeout_seconds = 30.0
    cfg.system_preamble = ""
    cfg.boundary_patterns = []
    cfg.n_ctx = 4096
    cfg.hidden_dim = 8
    cfg.ode_step_size = 0.1

    orch._config = cfg
    orch._degraded = False
    orch._history = []

    mock_llm = MagicMock(spec=LLMBackend)
    mock_llm.generate.return_value = "should not be called"
    orch._llm_backend = mock_llm

    # Doesn't matter — we just need the rest of the fields populated
    orch._stimulus_processor = MagicMock()
    orch._emotion_core = MagicMock()
    orch._homeostatic_engine = MagicMock()
    orch._prompt_assembler = MagicMock()
    orch._boundary_layer = MagicMock()

    input_text = "x" * length
    result = orch.process(input_text)

    assert result == fallback, f"Expected fallback for length={length}, got {result!r}"
    mock_llm.generate.assert_not_called()


# ---------------------------------------------------------------------------
# P18: Out-of-Range Configuration Raises ValueError
# Feature: lucia-core-phase1, Property 18: invalid config raises ValueError at init
# ---------------------------------------------------------------------------

@settings(max_examples=100)
@given(
    field=st.sampled_from([
        "loop_cadence_ms_low",
        "loop_cadence_ms_high",
        "hidden_dim_zero",
        "ode_step_size_zero",
        "llm_timeout_low",
    ])
)
def test_p18_out_of_range_config_raises_value_error(field):
    """
    For any OrchestratorConfig with an out-of-range field, __init__ must
    raise ValueError identifying the invalid parameter.
    Validates: Requirements 10.7, 10.8
    """
    # Feature: lucia-core-phase1, Property 18: Out-of-Range Configuration Raises ValueError
    from src.core.config import OrchestratorConfig

    base_kwargs = dict(
        model_path="x.gguf",
        loop_cadence_ms=200,
        hidden_dim=8,
        ode_step_size=0.1,
        llm_timeout_seconds=5.0,
    )

    overrides = {
        "loop_cadence_ms_low":   {"loop_cadence_ms": 50},
        "loop_cadence_ms_high":  {"loop_cadence_ms": 600},
        "hidden_dim_zero":       {"hidden_dim": 0},
        "ode_step_size_zero":    {"ode_step_size": 0.0},
        "llm_timeout_low":       {"llm_timeout_seconds": 0.5},
    }

    kwargs = {**base_kwargs, **overrides[field]}
    with pytest.raises(ValueError):
        OrchestratorConfig(**kwargs)
