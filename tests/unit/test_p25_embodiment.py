"""
tests/unit/test_p25_embodiment.py

Unit and invariant test suite for Phase 25: Temporal Embodiment & Social Feedback.
Strictly implements verification against P25 Architecture Contract v0.1:
  - Temporal continuity & elapsed-time idle dynamics
  - Multi-timescale state evolution & bounded hysteresis
  - Local dissipativity diagnostic (Tr(J) < 0) without claiming Lyapunov stability
  - Replaceable state estimation boundary (Leaky baseline & Bucy-Kalman candidate)
  - Unilateral social adaptation
  - Anti-sycophancy & anti-approval-seeking invariants
  - Anti-engagement optimization invariant
  - Relational-state bounds (||W_rel||_2 <= 0.08) and strict 4D R_t invariant
  - No unintended reciprocal coupling (actuator feedforward decoupling)
  - Genesis safety gate (data/profile.json == {"is_onboarded": false})
"""

import json
import time
from pathlib import Path
from unittest.mock import MagicMock

import numpy as np
import pytest

from src.core.embodiment.attunement import UnilateralAttunementEngine
from src.core.embodiment.contract import (
    MAX_PACING_DELAY_MS,
    MAX_PAUSE_MS_DELTA,
    MAX_PITCH_ST_DELTA,
    MAX_SPEECH_RATE_PCT_DELTA,
    MIN_PACING_DELAY_MS,
    MIN_PAUSE_MS_DELTA,
    MIN_PITCH_ST_DELTA,
    MIN_SPEECH_RATE_PCT_DELTA,
    P25_RELATIONAL_SPECTRAL_BOUND,
    EstimatedTemporalState,
    IdleDynamicsResult,
    TemporalModulation,
    TemporalObservation,
)
from src.core.embodiment.coordinator import TemporalEmbodimentCoordinator
from src.core.embodiment.dynamics import TemporalDynamicsEngine
from src.core.embodiment.estimator import BucyKalmanEstimator, LeakyTemporalEstimator
from src.core.embodiment.temporal_observer import TemporalObserver
from src.core.models import BehavioralConstraints, PADState, SomaticMarkers
from src.core.orchestrator.cognitive_orchestrator import CognitiveOrchestrator
from src.core.orchestrator.policies import CognitiveTurnResult
from src.core.relationship.state import RelationshipState


# ==============================================================================
# 1. Temporal Continuity & Elapsed-Time Idle Dynamics
# ==============================================================================


def test_temporal_observer_idle_and_latency() -> None:
    """TemporalObserver correctly records dt_idle, latency, and pacing ratio."""
    obs_engine = TemporalObserver(default_nominal_latency_ms=400.0)

    # First turn: initial baseline
    t0 = 1000.0
    obs1 = obs_engine.observe(current_timestamp=t0, user_text="Hello Lucia")
    assert obs1.timestamp == t0
    assert obs1.dt_idle_seconds == 0.0
    assert obs1.user_latency_ms == 400.0

    # Second turn 5 seconds later
    t1 = 1005.0
    obs2 = obs_engine.observe(current_timestamp=t1, user_text="How are you doing today?")
    assert obs2.timestamp == t1
    assert pytest.approx(obs2.dt_idle_seconds, rel=1e-3) == 5.0
    assert pytest.approx(obs2.user_latency_ms, rel=1e-3) == 5000.0
    assert obs2.turn_token_count == 5
    assert obs2.speech_tempo_ratio > 0.0


def test_temporal_dynamics_idle_relaxation_to_philia() -> None:
    """
    Test multi-timescale idle dynamics:
    - PAD decays asymptotically toward Philia (+0.25, -0.05, +0.05).
    - Energy replenishes toward 1.0.
    - Tension decays toward 0.0.
    """
    engine = TemporalDynamicsEngine(tau_pad=40.0, tau_somatic=20.0)

    # Excited/stressed initial PAD
    stressed_pad = PADState(pleasure=-0.60, arousal=0.80, dominance=-0.20, timestamp=time.time())
    cur_energy = 0.30
    cur_tension = 0.70

    # Step 40 seconds of idle
    result: IdleDynamicsResult = engine.step_idle(
        dt_seconds=40.0,
        current_pad=stressed_pad,
        current_energy=cur_energy,
        current_tension=cur_tension,
    )

    # PAD delta should pull toward Philia
    # Philia: P=+0.25, A=-0.05, D=+0.05
    # Stressed P=-0.60 -> delta_P should be positive
    # Stressed A=+0.80 -> delta_A should be negative
    # Stressed D=-0.20 -> delta_D should be positive
    assert result.pad_delta[0] > 0.0  # moving up toward +0.25
    assert result.pad_delta[1] < 0.0  # moving down toward -0.05
    assert result.pad_delta[2] > 0.0  # moving up toward +0.05

    # Energy recovery and tension decay
    assert result.energy_replenishment > 0.0
    assert result.tension_decay > 0.0
    assert result.relational_absence_hours == pytest.approx(40.0 / 3600.0, rel=1e-4)


# ==============================================================================
# 2. Stability Language & Dissipativity Diagnostic
# ==============================================================================


def test_dissipativity_diagnostic_contract() -> None:
    """
    Test local dissipativity diagnostic Tr(J) < 0:
    Contract rule: Tr(J) < 0 must be strictly framed as supporting local volume
    contraction / dissipativity, NEVER as a Lyapunov stability proof.
    """
    engine = TemporalDynamicsEngine(tau_pad=40.0, tau_somatic=20.0)
    tr_j = engine.compute_dissipativity_diagnostic()

    # Trace of negative diagonal damping matrix is strictly negative
    assert tr_j < 0.0
    assert tr_j == pytest.approx(- (3.0 / 40.0) - (1.0 / 20.0), rel=1e-4)

    # Verify method docstring preserves invariant forbidding Lyapunov claims
    doc = engine.compute_dissipativity_diagnostic.__doc__ or ""
    assert "dissipativity diagnostic" in doc or "volume contraction" in doc
    assert "does NOT alone guarantee Lyapunov stability" in doc


# ==============================================================================
# 3. State Estimation Boundary (Replaceable Boundary)
# ==============================================================================


def test_replaceable_state_estimator_boundary() -> None:
    """
    Verify interchangeable estimation boundary between Leaky and Bucy-Kalman.
    Both implement TemporalStateEstimator and output EstimatedTemporalState.
    """
    obs = TemporalObservation(
        timestamp=100.0,
        dt_idle_seconds=2.0,
        user_latency_ms=2000.0,
        pause_duration_ms=250.0,
        speech_tempo_ratio=1.1,
    )

    # 1. Leaky baseline
    leaky = LeakyTemporalEstimator(leakage=0.25)
    est_leaky = leaky.update(obs)
    assert isinstance(est_leaky, EstimatedTemporalState)
    assert est_leaky.estimated_user_latency_ms > 0.0
    assert est_leaky.estimated_tempo_ratio > 0.0
    assert est_leaky.confidence >= 0.0

    # 2. Bucy-Kalman candidate observer (behind replaceable boundary)
    kalman = BucyKalmanEstimator(process_noise_q=10.0, measurement_noise_r=100.0)
    est_kalman = kalman.update(obs)
    assert isinstance(est_kalman, EstimatedTemporalState)
    assert est_kalman.estimated_user_latency_ms > 0.0
    assert est_kalman.estimated_tempo_ratio > 0.0
    assert est_kalman.confidence > 0.0

    # Both reset cleanly
    leaky.reset()
    kalman.reset()
    assert leaky._current_latency_ms == 400.0
    assert kalman._x[0] == 400.0


# ==============================================================================
# 4. Multi-Timescale Evolution & Bounded Hysteresis
# ==============================================================================


def test_bounded_hysteresis_path_dependence() -> None:
    """
    Verify bounded hysteresis: different interaction histories produce
    different estimated temporal state without adding ungrounded accumulator bloat.
    """
    estimator_fast = LeakyTemporalEstimator(leakage=0.30)
    estimator_slow = LeakyTemporalEstimator(leakage=0.30)

    # Fast cadence trajectory: short latencies (150ms)
    for _ in range(5):
        estimator_fast.update(TemporalObservation(
            timestamp=time.time(),
            user_latency_ms=150.0,
            speech_tempo_ratio=1.2,
        ))

    # Slow cadence trajectory: long latencies (2500ms)
    for _ in range(5):
        estimator_slow.update(TemporalObservation(
            timestamp=time.time(),
            user_latency_ms=2500.0,
            speech_tempo_ratio=0.8,
        ))

    est_fast = estimator_fast.update(TemporalObservation(timestamp=time.time(), user_latency_ms=500.0))
    est_slow = estimator_slow.update(TemporalObservation(timestamp=time.time(), user_latency_ms=500.0))

    # Path dependence holds within bounded limits
    assert est_fast.estimated_user_latency_ms < est_slow.estimated_user_latency_ms
    assert 100.0 <= est_fast.estimated_user_latency_ms <= 3000.0
    assert 100.0 <= est_slow.estimated_user_latency_ms <= 3000.0


# ==============================================================================
# 5. Unilateral Social Adaptation & Actuator Decoupling
# ==============================================================================


def test_unilateral_attunement_bounds() -> None:
    """
    Verify attunement modulation conforms strictly to contract bounds:
    - pacing delay in [0, 500] ms
    - speech rate delta in [-15, +15] %
    - pause duration delta in [-50, +100] ms
    - pitch shift delta in [-1.0, +1.0] st
    """
    attunement = UnilateralAttunementEngine()

    # Extreme fast user
    fast_est = EstimatedTemporalState(
        estimated_user_latency_ms=100.0,
        estimated_tempo_ratio=1.5,
        rhythm_stability=0.9,
        confidence=1.0,
        estimator_id="test",
    )
    mod_fast = attunement.compute_modulation(fast_est)

    assert MIN_PACING_DELAY_MS <= mod_fast.injected_pacing_delay_ms <= MAX_PACING_DELAY_MS
    assert MIN_SPEECH_RATE_PCT_DELTA <= mod_fast.speech_rate_pct_delta <= MAX_SPEECH_RATE_PCT_DELTA
    assert MIN_PAUSE_MS_DELTA <= mod_fast.pause_duration_ms_delta <= MAX_PAUSE_MS_DELTA
    assert MIN_PITCH_ST_DELTA <= mod_fast.pitch_shift_st_delta <= MAX_PITCH_ST_DELTA
    assert mod_fast.is_bounded()

    # Extreme slow user
    slow_est = EstimatedTemporalState(
        estimated_user_latency_ms=3000.0,
        estimated_tempo_ratio=0.7,
        rhythm_stability=0.5,
        confidence=1.0,
        estimator_id="test",
    )
    mod_slow = attunement.compute_modulation(slow_est)

    assert MIN_PACING_DELAY_MS <= mod_slow.injected_pacing_delay_ms <= MAX_PACING_DELAY_MS
    assert MIN_SPEECH_RATE_PCT_DELTA <= mod_slow.speech_rate_pct_delta <= MAX_SPEECH_RATE_PCT_DELTA
    assert MIN_PAUSE_MS_DELTA <= mod_slow.pause_duration_ms_delta <= MAX_PAUSE_MS_DELTA
    assert MIN_PITCH_ST_DELTA <= mod_slow.pitch_shift_st_delta <= MAX_PITCH_ST_DELTA
    assert mod_slow.is_bounded()


# ==============================================================================
# 6. Anti-Sycophancy & Anti-Engagement Invariants
# ==============================================================================


def test_anti_sycophancy_and_anti_engagement_invariant() -> None:
    """
    Verify anti-sycophancy and anti-engagement:
    - Attunement engine has NO reward functions.
    - Attunement engine has NO retention or dopamine maximization hooks.
    - Relational modulation spectral bound ||W_rel||_2 <= 0.08 is strictly enforced.
    """
    attunement = UnilateralAttunementEngine()

    # Relational spectral norm invariant
    dummy_est = EstimatedTemporalState(
        estimated_user_latency_ms=400.0,
        estimated_tempo_ratio=1.0,
        rhythm_stability=1.0,
        confidence=1.0,
        estimator_id="test",
    )
    mod = attunement.compute_modulation(dummy_est)
    assert np.linalg.norm(mod.relational_signal_delta, ord=2) <= P25_RELATIONAL_SPECTRAL_BOUND + 1e-9

    # Verify no reward or engagement attributes
    forbidden_terms = ["reward", "engagement", "retention", "hook", "sycophancy", "approval", "streak"]
    custom_attrs = [attr for attr in dir(attunement) if not attr.startswith("__")]
    for attr in custom_attrs:
        attr_lower = attr.lower()
        for forbidden in forbidden_terms:
            assert forbidden not in attr_lower, f"Forbidden attribute found: {attr}"


# ==============================================================================
# 7. Strict 4D Relational Vector Invariant
# ==============================================================================


def test_canonical_4d_relational_vector_invariant() -> None:
    """
    Verify that relational state remains strictly 4D [familiarity, trust, closeness, reciprocity].
    No new relational dimensions (such as grievance, resentment, rupture) are added.
    """
    rel = RelationshipState(
        familiarity=0.6,
        trust=0.7,
        closeness=0.5,
        reciprocity=0.8,
    )
    arr = rel.to_array()
    assert len(arr) == 4
    assert arr.shape == (4,)
    d = rel.to_dict()
    dims = {k for k in d.keys() if k != "timestamp"}
    assert dims == {"familiarity", "trust", "closeness", "reciprocity"}


# ==============================================================================
# 8. Decoupled Actuator Decoupling Invariant (ADR-016 / ADR-024)
# ==============================================================================


def test_no_unintended_reciprocal_coupling() -> None:
    """
    Verify that actuator outputs and prosodic modulation do NOT feed back into
    internal limbic ODE state. Modulation feeds strictly forward into P24 ExpressionState.
    """
    coordinator = TemporalEmbodimentCoordinator()

    # Observe and compute modulation
    coordinator.process_turn_start(
        current_timestamp=time.time(),
        user_text="Short prompt",
        explicit_user_latency_ms=1200.0,
    )
    mod = coordinator.compute_attunement_modulation()

    # Ensure modulation is feedforward parameters
    assert isinstance(mod, TemporalModulation)
    assert hasattr(mod, "speech_rate_pct_delta")
    assert hasattr(mod, "injected_pacing_delay_ms")

    # Coordinator does NOT mutate or push actuator values back to limbic state
    assert not hasattr(coordinator, "push_expression_feedback")
    assert not hasattr(coordinator, "reciprocal_loss")


# ==============================================================================
# 9. End-to-End Orchestrator Integration
# ==============================================================================


def test_orchestrator_temporal_embodiment_end_to_end() -> None:
    """
    Verify CognitiveOrchestrator integrates Phase 25 cleanly:
    - process() emits CognitiveTurnResult with temporal_state and temporal_modulation
    - expression voice prosody incorporates bounded modulation
    - reset_lifecycle() clears temporal coordinator state
    """
    # Create minimal mock subsystems for orchestrator
    mock_stimulus = MagicMock()
    mock_stimulus.encode.return_value = np.zeros(16, dtype=np.float64)

    mock_emotion = MagicMock()
    mock_emotion.get_pad_state.return_value = PADState.resting()
    mock_emotion.push_stimulus.return_value = 1
    mock_emotion.commit_stimulus.return_value = PADState.resting()
    mock_emotion.is_alive.return_value = True
    mock_emotion.tick_count.return_value = 5
    mock_emotion.config = MagicMock()
    mock_emotion.config.enable_affective_recollection = False

    mock_homeo = MagicMock()
    mock_homeo.compute_somatic_markers.return_value = SomaticMarkers(
        stability=1.0, cognitive_load=0.1, energy=0.9, tension=0.1
    )
    mock_homeo.compute_behavioral_constraints.return_value = BehavioralConstraints(
        max_tokens=100, temperature=0.7, latency_ms=0, reasoning_depth=1
    )
    mock_homeo._energy = 0.9

    mock_active_inf = MagicMock()
    mock_active_inf._A = np.eye(3)
    mock_active_inf._b = np.zeros(3)
    mock_active_inf.step.return_value = 0.1

    mock_mem = MagicMock()
    mock_mem.get_all_traces.return_value = []
    mock_mem._M = 16

    mock_ecphory = MagicMock()
    mock_ecphory.query.return_value = None

    mock_prompt = MagicMock()
    mock_prompt.assemble.return_value = "Prompt text"

    mock_llm = MagicMock()
    mock_llm.generate.return_value = "Hello! Nice to talk with you."

    mock_boundary = MagicMock()
    mock_boundary.validate.return_value = "Hello! Nice to talk with you."

    temporal_coord = TemporalEmbodimentCoordinator()

    orchestrator = CognitiveOrchestrator(
        stimulus_processor=mock_stimulus,
        emotion_core=mock_emotion,
        homeostatic_engine=mock_homeo,
        active_inference=mock_active_inf,
        affective_memory=mock_mem,
        ecphory_engine=mock_ecphory,
        decay_engine=None,
        prompt_assembler=mock_prompt,
        llm_backend=mock_llm,
        boundary_layer=mock_boundary,
        temporal_coordinator=temporal_coord,
    )

    result = orchestrator.process("Hello Lucia")

    assert isinstance(result, CognitiveTurnResult)
    assert result.temporal_state is not None
    assert result.temporal_modulation is not None
    assert result.expression is not None
    assert result.expression.voice is not None

    # Check that speech rate is within valid voice bounds [-20, +20]
    assert -20.0 <= result.expression.voice.speech_rate_pct <= 20.0

    # Test lifecycle reset cleans temporal coordinator
    orchestrator.reset_lifecycle()
    assert orchestrator.temporal_coordinator.get_latest_modulation() is None


# ==============================================================================
# 10. Genesis Safety Gate Invariant
# ==============================================================================


def test_genesis_profile_invariant() -> None:
    """
    Safety gate: data/profile.json must remain strictly {"is_onboarded": false}.
    Zero Genesis files or commitment mutations permitted.
    """
    profile_path = Path("data/profile.json")
    assert profile_path.exists(), "data/profile.json must exist"

    with open(profile_path, "r", encoding="utf-8") as f:
        data = json.load(f)

    assert data == {"is_onboarded": False}, (
        f"Genesis gate violated! Profile content was: {data}"
    )
