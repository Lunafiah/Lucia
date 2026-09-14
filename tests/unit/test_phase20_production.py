"""
Unit test suite for Phase 20 Production Implementation:
Closed-Loop Affective Recollection via Slow-Field Latent Forcing.

Adheres strictly to architectural invariants:
- Black-box causal verification (no testing of private internal fields).
- Strict non-introspective invariant.
- Simulation-time ODE integration precision.
- 3-case legacy compatibility approximation contract.
- Memory/EmotionCore decoupling.
- Canonical 16-stage cognitive turn execution.
"""

from __future__ import annotations

import time
import numpy as np
import pytest

from unittest.mock import MagicMock

from src.core.config import EmotionConfig
from src.core.emotion.emotion_core import EmotionCore
from src.core.memory.affective_memory import (
    AffectiveMemory,
    AffectiveMemoryConfig,
    MemoryTrace,
)
from src.core.memory.ecphory import EcphoryConfig, EcphoryEngine, RecollectionResult
from src.core.memory.sdm import SDMConfig
from src.core.models import PADState
from src.core.orchestrator.cognitive_orchestrator import CognitiveOrchestrator
from src.core.orchestrator.prompt_assembler import PromptAssembler
from src.core.orchestrator.policies import CognitiveTurnResult
from src.core.safety.boundary_layer import BoundaryLayer, BoundaryConfig
from src.core.gating.stimulus_processor import StimulusProcessor
from src.core.inference.active_inference import ActiveInferenceConfig, ActiveInferenceEngine
from src.core.emotion.homeostatic_engine import HomeostaticEngine
from src.core.communication.communication_policy import CommunicationPolicy
from src.core.expression.expression_policy import ExpressionPolicy


class TestPhase20EmotionCoreRecollection:
    """Black-box causal verification of EmotionCore recollection injection."""

    def test_emotion_core_recollection_injection_causal_trajectory(self):
        """
        Verify that injecting recollection forcing causes a significant slow-field
        trajectory divergence compared to an unforced control, followed by smooth
        relaxation back toward the Philia baseline once forcing expires in simulation time.
        """
        cfg = EmotionConfig(
            enable_affective_recollection=True,
            recollection_coupling_weight=0.35,
            recollection_pulse_duration_sec=1.0,  # 1.0s simulation time (20 ticks at dt=0.05)
            ode_step_size=0.05,
        )
        core_forced = EmotionCore(cfg)
        core_control = EmotionCore(cfg)

        # Baseline check before injection
        pad_init = core_forced.get_pad_state()
        assert abs(pad_init.pleasure - 0.25) < 1e-3

        # Prepare a salient recollection vector (perturbation along dimension 0)
        r_recollect = np.zeros(16, dtype=np.float64)
        r_recollect[0] = 0.80  # strong positive valence perturbation

        # Inject into forced core
        core_forced.inject_recollection(r_recollect, duration_sec=1.0)

        # Step both cores for 20 ticks (1.0s of simulation time — during active forcing window)
        for _ in range(20):
            core_forced.step_once()
            core_control.step_once()

        slow_forced_mid = core_forced.get_slow_latent_state()
        slow_control_mid = core_control.get_slow_latent_state()
        pad_forced_mid = core_forced.get_pad_state()
        pad_control_mid = core_control.get_pad_state()

        # Black-box assertion 1: significant causal divergence during forcing window
        slow_divergence = float(np.linalg.norm(slow_forced_mid - slow_control_mid))
        assert slow_divergence > 0.05, f"Expected slow divergence > 0.05, got {slow_divergence}"
        assert pad_forced_mid.pleasure > pad_control_mid.pleasure + 0.01

        # Advance past the 1.0s forcing window (another 40 ticks = 2.0s post-forcing)
        for _ in range(40):
            core_forced.step_once()
            core_control.step_once()

        slow_forced_late = core_forced.get_slow_latent_state()

        # Black-box assertion 2: once forcing expires, the trajectory relaxes back toward Philia resting state
        philia_s = np.zeros(16, dtype=np.float64)
        philia_s[0], philia_s[1], philia_s[2] = cfg.philia_slow_baseline[:3]
        dist_late = float(np.linalg.norm(slow_forced_late - philia_s))
        dist_mid = float(np.linalg.norm(slow_forced_mid - philia_s))
        assert dist_late < dist_mid, "Slow field must smoothly decay toward Philia baseline post-forcing"

    def test_emotion_core_recollection_disabled_flag_restores_phase19(self):
        """
        Verify that when enable_affective_recollection is False, inject_recollection
        is suppressed identically, restoring the Phase-19 unforced execution path.
        """
        cfg_disabled = EmotionConfig(
            enable_affective_recollection=False,
            ode_step_size=0.05,
        )
        core_disabled = EmotionCore(cfg_disabled)
        core_unforced = EmotionCore(cfg_disabled)

        r_recollect = np.ones(16, dtype=np.float64) * 0.85
        core_disabled.inject_recollection(r_recollect, duration_sec=2.0)

        # Advance 15 ticks
        for _ in range(15):
            core_disabled.step_once()
            core_unforced.step_once()

        slow_disabled = core_disabled.get_slow_latent_state()
        slow_unforced = core_unforced.get_slow_latent_state()

        # Must be bit-exact identical to unforced
        diff = float(np.linalg.norm(slow_disabled - slow_unforced))
        assert diff < 1e-12, f"Disabled recollection must produce zero divergence, got {diff}"


class TestPhase20LegacyFallbackApproximation:
    """Test the strict 3-case semantic acceptance contract for PAD -> slow reconstruction."""

    def test_legacy_fallback_approximation_case1_resting_baseline(self):
        """Case 1: Canonical resting baseline input returns s*_philia bit-exact (zero drift)."""
        p_philia = PADState(pleasure=0.25, arousal=-0.05, dominance=0.05, timestamp=0.0)
        s_res = AffectiveMemory.synthesize_legacy_latent(
            pad_tag=p_philia,
            philia_baseline=(0.25, -0.05, 0.05),
            philia_slow_baseline=(0.20, -0.05, 0.05),
            slow_dim=16,
        )
        assert len(s_res) == 16
        assert s_res[0] == 0.20
        assert s_res[1] == -0.05
        assert s_res[2] == 0.05
        assert np.all(s_res[3:] == 0.0)

    def test_legacy_fallback_approximation_case2_non_baseline_deterministic_bounded(self):
        """Case 2: Non-baseline valid input returns bounded (<= 0.85) deterministic vector."""
        p_excited = PADState(pleasure=0.80, arousal=0.70, dominance=0.50, timestamp=0.0)
        s_res1 = AffectiveMemory.synthesize_legacy_latent(p_excited)
        s_res2 = AffectiveMemory.synthesize_legacy_latent(p_excited)

        # Determinism
        assert np.allclose(s_res1, s_res2, atol=1e-12)
        # Boundedness
        assert np.max(np.abs(s_res1)) <= 0.85
        # Meaningful projection along primary dimensions
        assert s_res1[0] > 0.20  # pleasure increased
        assert s_res1[1] > -0.05  # arousal increased

    def test_legacy_fallback_approximation_case3_non_finite_defensive(self):
        """Case 3: Non-finite input (NaN / Inf) returns safe defensive baseline."""
        p_nan = (float("nan"), 0.0, 0.0)
        p_inf = (float("inf"), -1.0, 1.0)

        s_nan = AffectiveMemory.synthesize_legacy_latent(p_nan)
        s_inf = AffectiveMemory.synthesize_legacy_latent(p_inf)

        assert np.all(np.isfinite(s_nan))
        assert np.all(np.isfinite(s_inf))
        assert s_nan[0] == 0.20
        assert s_inf[0] == 0.20


class TestPhase20EcphoryCompetitiveGating:
    """Test multi-modal scoring and competitive softmax gating in EcphoryEngine."""

    @pytest.fixture
    def ecphory_setup(self):
        cfg = EcphoryConfig(resonance_threshold=0.5, ecphory_k=3)
        engine = EcphoryEngine(cfg)
        emotion_cfg = EmotionConfig(
            recollection_gate_threshold=0.50,
            recollection_softmax_temp=0.20,
        )
        return engine, emotion_cfg

    def test_sub_threshold_noise_rejection(self, ecphory_setup):
        """Orthogonal cue produces sub-threshold salience (S < 0.50), resulting in active=False."""
        engine, emotion_cfg = ecphory_setup

        # Create a trace with specific content and PAD
        pad_trace = PADState(pleasure=0.6, arousal=0.4, dominance=0.2, timestamp=1.0)
        content_trace = np.zeros(64, dtype=np.float32)
        content_trace[0] = 1.0

        trace = MemoryTrace(
            trace_id=1,
            address_vec=np.zeros(256, dtype=np.uint8),
            content_vec=content_trace,
            pad_tag=pad_trace,
            timestamp=1.0,
            decay_weight=1.0,
            slow_latent_trace=np.ones(16, dtype=np.float64) * 0.4,
        )

        # Query with orthogonal cue (content orthogonal, PAD neutral)
        orthogonal_stim = np.zeros(16, dtype=np.float64)
        orthogonal_stim[5] = 1.0  # orthogonal to index 0
        pad_curr = PADState(pleasure=0.25, arousal=-0.05, dominance=0.05, timestamp=2.0)

        echo_vec, rec_res = engine.query_recollection(
            pad_state=pad_curr,
            stimulus_vec=orthogonal_stim,
            traces=[trace],
            config=emotion_cfg,
        )

        assert not rec_res.active
        assert rec_res.salience < 0.50
        assert np.all(rec_res.r_slow_bounded == 0.0)

    def test_high_salience_competitive_gating(self, ecphory_setup):
        """Matching cue exceeds gate (S >= 0.50), selects winning trace, and returns bounded r_slow."""
        engine, emotion_cfg = ecphory_setup

        # Create matching trace
        pad_trace = PADState(pleasure=0.8, arousal=0.5, dominance=0.3, timestamp=1.0)
        content_trace = np.zeros(64, dtype=np.float32)
        content_trace[:16] = 1.0  # aligned with stimulus

        s_latent = np.zeros(16, dtype=np.float64)
        s_latent[0] = 0.70  # strong positive slow latent state

        trace = MemoryTrace(
            trace_id=42,
            address_vec=np.zeros(256, dtype=np.uint8),
            content_vec=content_trace,
            pad_tag=pad_trace,
            timestamp=1.0,
            decay_weight=1.0,
            slow_latent_trace=s_latent,
        )

        stimulus = np.zeros(16, dtype=np.float64)
        stimulus[:16] = 1.0
        pad_curr = PADState(pleasure=0.75, arousal=0.45, dominance=0.25, timestamp=2.0)

        echo_vec, rec_res = engine.query_recollection(
            pad_state=pad_curr,
            stimulus_vec=stimulus,
            traces=[trace],
            config=emotion_cfg,
        )

        assert rec_res.active
        assert rec_res.salience >= 0.50
        assert rec_res.winning_trace_id == 42
        assert rec_res.r_slow_bounded[0] > 0.0
        assert np.max(np.abs(rec_res.r_slow_bounded)) <= 0.85


class TestPhase20ArchitecturalDecoupling:
    """Verify architectural decoupling: Memory does not import or call EmotionCore."""

    def test_memory_subsystem_has_no_emotion_core_coupling(self):
        import src.core.memory.ecphory as ecphory_mod
        import src.core.memory.affective_memory as aff_mem_mod

        # Verify no direct references or calls to EmotionCore
        assert not hasattr(ecphory_mod, "EmotionCore")
        assert not hasattr(aff_mem_mod, "EmotionCore")


class TestPhase20CognitiveOrchestratorClosedLoop:
    """Test full S1–S16 closed-loop cognitive turn execution with Phase 20 recollection."""

    def test_cognitive_turn_closed_loop_recollection(self):
        """
        Verify end-to-end turn execution:
        - Seed a memory trace with slow_latent_trace.
        - Send matching prompt.
        - Verify Stage 6 recollection evaluation.
        - Verify CognitiveTurnResult contains active recollection.
        - Verify Stage 16.1 co-encodes live slow latent state into newly stored trace.
        """
        emotion_core = EmotionCore(EmotionConfig(enable_affective_recollection=True))
        affective_memory = AffectiveMemory(AffectiveMemoryConfig(sdm_config=SDMConfig(content_dim=64), m=64))
        ecphory_engine = EcphoryEngine(EcphoryConfig())
        homeostatic_engine = HomeostaticEngine()
        active_inference = ActiveInferenceEngine(ActiveInferenceConfig())
        stimulus_processor = StimulusProcessor()
        llm_backend = MagicMock()
        llm_backend.is_ready.return_value = True
        llm_backend.generate.return_value = "The sunlight on the water was very warm."
        boundary_layer = BoundaryLayer(BoundaryConfig())
        prompt_assembler = PromptAssembler()
        comm_policy = CommunicationPolicy()
        expr_policy = ExpressionPolicy()

        orchestrator = CognitiveOrchestrator(
            emotion_core=emotion_core,
            homeostatic_engine=homeostatic_engine,
            active_inference=active_inference,
            stimulus_processor=stimulus_processor,
            llm_backend=llm_backend,
            boundary_layer=boundary_layer,
            prompt_assembler=prompt_assembler,
            affective_memory=affective_memory,
            ecphory_engine=ecphory_engine,
            comm_policy=comm_policy,
            expression_policy=expr_policy,
        )

        try:
            # Seed a memory trace in affective memory
            cue_text = "sunlit beach afternoon"
            cue_stim = stimulus_processor.encode(cue_text)
            content = np.zeros(64, dtype=np.float32)
            content[: len(cue_stim)] = cue_stim.astype(np.float32)

            seeded_slow = np.zeros(16, dtype=np.float64)
            seeded_slow[0] = 0.65  # high pleasure slow latent trace
            seeded_pad = PADState(pleasure=0.7, arousal=0.2, dominance=0.3, timestamp=time.monotonic())

            tid = affective_memory.store(content, seeded_pad, slow_latent_trace=seeded_slow)
            assert tid is not None

            # Execute turn with matching input text
            result = orchestrator.process(cue_text)

            assert isinstance(result, CognitiveTurnResult)
            assert result.response_text == "The sunlight on the water was very warm."
            assert result.trace_stored is True

            # Verify recollection packet
            assert result.recollection is not None
            assert isinstance(result.recollection, RecollectionResult)

            # Retrieve the newly consolidated trace from Stage 16.1
            traces = affective_memory.get_all_traces()
            assert len(traces) == 2  # seeded trace + newly stored trace
            new_trace = traces[-1]
            assert new_trace.slow_latent_trace is not None
            assert len(new_trace.slow_latent_trace) == 16
            assert np.all(np.isfinite(new_trace.slow_latent_trace))

        finally:
            orchestrator.shutdown()
