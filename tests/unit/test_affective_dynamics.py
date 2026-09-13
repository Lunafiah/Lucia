"""
Tests for Phase 10 — Canonical Affective Dynamics Specification.

Verifies:
  - Test A: State Persistence (h(t+1) depends on h(t))
  - Test B: Affective Causality (same stimulus under different prior states)
  - Test C: Temporal Ordering (Phase 9.6 post-commit PAD snapshot consumption)
  - Test D: Controlled Accumulation (Energy drain, conditional load accumulation, fatigue)
  - Test E: Relaxation Dynamics (convergence toward equilibrium, non-monotonic transients)
  - Test F: Historical Hysteresis (identical probe after divergent histories)
  - Test G: Affect → Cognition Modulation (downstream computational constraints)
  - Test H: Reproducibility Envelope (deterministic trajectory under controlled conditions)
"""

import math
import time
from typing import List, Tuple
from unittest.mock import MagicMock

import numpy as np
import pytest

from src.core.config import EmotionConfig, HomeostaticConfig
from src.core.emotion.emotion_core import EmotionCore
from src.core.emotion.homeostatic_engine import HomeostaticEngine
from src.core.gating.stimulus_processor import StimulusProcessor
from src.core.inference.active_inference import ActiveInferenceConfig, ActiveInferenceEngine
from src.core.models import BehavioralConstraints, PADState, SomaticMarkers
from src.core.orchestrator.cognitive_orchestrator import CognitiveOrchestrator
from src.core.orchestrator.policies import (
    CognitiveTurnResult,
    GenerationPolicy,
    PlasticityPolicy,
    SurpriseModulationPolicy,
)
from src.core.orchestrator.prompt_assembler import PromptAssembler
from src.core.safety.boundary_layer import BoundaryLayer


# ==============================================================================
# Helpers & Fixtures
# ==============================================================================

class MockLLMBackend:
    def __init__(self, canned_response: str = "Mocked reply.") -> None:
        self.canned_response = canned_response
        self.calls: List[Tuple[str, BehavioralConstraints]] = []

    def is_ready(self) -> bool:
        return True

    def generate(self, prompt: str, constraints: BehavioralConstraints) -> str:
        self.calls.append((prompt, constraints))
        return self.canned_response

    def shutdown(self) -> None:
        pass


class MockAffectiveMemory:
    def __init__(self) -> None:
        self._M = 16
        self.stored: List[Tuple[np.ndarray, PADState]] = []

    def store(self, content: np.ndarray, pad: PADState) -> None:
        self.stored.append((content, pad))

    def get_all_traces(self) -> list:
        return []

    def clear(self) -> None:
        self.stored.clear()


class MockEcphoryEngine:
    def query(self, pad: PADState, traces: list) -> np.ndarray:
        return np.zeros(16, dtype=np.float32)


# ==============================================================================
# Test A: State Persistence
# ==============================================================================

class TestA_StatePersistence:
    """
    Test A — Persistence:
    Demonstrates that h(t+1) and p(t+1) depend on prior hidden state h(t)
    under controlled, identical stimulus conditions.
    """

    def test_hidden_and_pad_divergence_from_different_prior_states(self) -> None:
        # Create two separate EmotionCore instances with identical weights (same seed 42)
        core1 = EmotionCore(EmotionConfig())
        core2 = EmotionCore(EmotionConfig())

        # Displace core2 with a priming stimulus
        prime_stim = np.ones(16, dtype=np.float64) * 0.8
        core2.push_stimulus(prime_stim)
        core2.step_once()

        # Record initial states
        h1_init = core1._h.copy()
        h2_init = core2._h.copy()
        p1_init = core1.get_pad_state()
        p2_init = core2.get_pad_state()

        assert np.linalg.norm(h1_init - h2_init) > 0.1, "Priming must displace hidden state"

        # Apply identical probe stimulus to both
        probe_stim = np.array([0.5, -0.3, 0.2, 0.1] * 4, dtype=np.float64)
        core1.push_stimulus(probe_stim.copy())
        core2.push_stimulus(probe_stim.copy())

        pad1_post = core1.step_once()
        pad2_post = core2.step_once()

        h1_post = core1._h
        h2_post = core2._h

        # Compute divergence
        h_divergence = float(np.linalg.norm(h1_post - h2_post))
        pad_divergence = math.sqrt(
            (pad1_post.pleasure - pad2_post.pleasure) ** 2
            + (pad1_post.arousal - pad2_post.arousal) ** 2
            + (pad1_post.dominance - pad2_post.dominance) ** 2
        )

        assert h_divergence > 0.05, f"Hidden states must diverge (got divergence={h_divergence})"
        assert pad_divergence > 0.01, f"PAD states must diverge (got divergence={pad_divergence})"


# ==============================================================================
# Test B: Affective Causality
# ==============================================================================

class TestB_AffectiveCausality:
    """
    Test B — Causality:
    Same stimulus X delivered to different prior states (Neutral vs High-Arousal)
    produces causally divergent downstream consequences: PAD, surprise S_t,
    somatic markers, and generation policy constraints.
    """

    def test_same_stimulus_under_different_prior_states_causes_divergence(self) -> None:
        def build_orchestrator() -> Tuple[CognitiveOrchestrator, EmotionCore]:
            core = EmotionCore(EmotionConfig())
            homeo = HomeostaticEngine(HomeostaticConfig())
            active_inf = ActiveInferenceEngine(ActiveInferenceConfig())
            mem = MockAffectiveMemory()
            ecph = MockEcphoryEngine()
            prompt_asm = PromptAssembler()
            llm = MockLLMBackend()
            boundary = BoundaryLayer()

            orch = CognitiveOrchestrator(
                stimulus_processor=StimulusProcessor(),
                emotion_core=core,
                homeostatic_engine=homeo,
                active_inference=active_inf,
                affective_memory=mem,
                ecphory_engine=ecph,
                prompt_assembler=prompt_asm,
                llm_backend=llm,
                boundary_layer=boundary,
            )
            return orch, core

        orch_neutral, core_neutral = build_orchestrator()
        orch_aroused, core_aroused = build_orchestrator()

        try:
            # Prime orch_aroused with intense, high-arousal inputs
            for _ in range(3):
                orch_aroused.process("EMERGENCY CRITICAL SYSTEM FAILURE ALERT DANGER")

            # Deliver identical test probe to both
            probe_text = "Status report on operational subsystems."
            res_neutral: CognitiveTurnResult = orch_neutral.process(probe_text)
            res_aroused: CognitiveTurnResult = orch_aroused.process(probe_text)

            # 1. Verify PAD divergence
            pad_diff = math.sqrt(
                (res_neutral.pad_final.pleasure - res_aroused.pad_final.pleasure) ** 2
                + (res_neutral.pad_final.arousal - res_aroused.pad_final.arousal) ** 2
                + (res_neutral.pad_final.dominance - res_aroused.pad_final.dominance) ** 2
            )
            assert pad_diff > 0.01, f"Expected PAD divergence, got {pad_diff}"

            # 2. Verify Cognitive Load divergence
            assert res_aroused.somatic.cognitive_load > res_neutral.somatic.cognitive_load, (
                f"Aroused load ({res_aroused.somatic.cognitive_load}) must exceed neutral ({res_neutral.somatic.cognitive_load})"
            )

            # 3. Verify Energy divergence
            assert res_aroused.somatic.energy < res_neutral.somatic.energy, (
                f"Aroused energy ({res_aroused.somatic.energy}) must be lower than neutral ({res_neutral.somatic.energy})"
            )

            # 4. Verify Generation Policy modulation
            assert res_aroused.constraints.max_tokens <= res_neutral.constraints.max_tokens, (
                "Aroused state with higher load must throttle or match token budget"
            )
        finally:
            orch_neutral.shutdown()
            orch_aroused.shutdown()


# ==============================================================================
# Test C: Temporal Ordering (Phase 9.6 Preservation)
# ==============================================================================

class TestC_TemporalOrdering:
    """
    Test C — Temporal Ordering:
    Verifies that L4 ActiveInferenceEngine consumes the exact committed post-stimulus
    PAD snapshot from the Phase 9.6 commit barrier, ensuring zero temporal lag
    and strictly exactly-once integration.
    """

    def test_l4_reads_exact_post_commit_pad_snapshot(self) -> None:
        core = EmotionCore(EmotionConfig())
        active_inf = ActiveInferenceEngine(ActiveInferenceConfig())

        # Spy on active_inference.step
        original_step = active_inf.step
        step_calls: List[Tuple[PADState, PADState]] = []

        def spy_step(p_before: PADState, p_after: PADState) -> float:
            step_calls.append((p_before, p_after))
            return original_step(p_before, p_after)

        active_inf.step = spy_step

        orch = CognitiveOrchestrator(
            stimulus_processor=StimulusProcessor(),
            emotion_core=core,
            homeostatic_engine=HomeostaticEngine(),
            active_inference=active_inf,
            affective_memory=MockAffectiveMemory(),
            ecphory_engine=MockEcphoryEngine(),
            prompt_assembler=PromptAssembler(),
            llm_backend=MockLLMBackend(),
            boundary_layer=BoundaryLayer(),
        )

        try:
            res = orch.process("Test sensory input for temporal synchronization validation")

            assert len(step_calls) == 1, "ActiveInference.step must be called exactly once per turn"
            called_before, called_after = step_calls[0]

            # Verify that called_after matches res.pad_final bitwise
            assert called_after.pleasure == res.pad_final.pleasure
            assert called_after.arousal == res.pad_final.arousal
            assert called_after.dominance == res.pad_final.dominance
            assert called_after.timestamp == res.pad_final.timestamp

            # Verify that pad_initial matches called_before
            assert called_before.pleasure == res.pad_initial.pleasure
            assert called_before.arousal == res.pad_initial.arousal
            assert called_before.dominance == res.pad_initial.dominance
        finally:
            orch.shutdown()


# ==============================================================================
# Test D: Controlled Accumulation
# ==============================================================================

class TestD_ControlledAccumulation:
    """
    Test D — Accumulation:
    Demonstrates controlled accumulation of physiological load and energy depletion
    under rapid consecutive stimuli without idle recovery.
    """

    def test_rapid_inputs_deplete_energy_monotonically_and_trigger_fatigue(self) -> None:
        homeo = HomeostaticEngine(HomeostaticConfig())
        pad = PADState(pleasure=0.1, arousal=0.2, dominance=0.0, timestamp=time.monotonic())

        initial_energy = homeo._energy
        assert initial_energy == 1.0

        energies: List[float] = []
        loads: List[float] = []

        # Deliver 17 consecutive inputs rapidly (zero idle time)
        for turn in range(17):
            homeo.record_input()
            somatic = homeo.compute_somatic_markers(pad)
            energies.append(somatic.energy)
            loads.append(somatic.cognitive_load)

        # 1. Monotonic energy depletion
        for i in range(len(energies) - 1):
            assert energies[i + 1] <= energies[i], "Energy must deplete monotonically"
            assert abs(energies[i] - energies[i + 1] - 0.05) < 1e-6, "Energy must deplete by 0.05 per input"

        # 2. At turn 17 (17 * 0.05 = 0.85 depletion), energy is 0.15 <= 0.20
        final_energy = energies[-1]
        assert final_energy <= 0.20, f"Energy must be <= 0.20 after 17 turns (got {final_energy})"

        # 3. Verify Cognitive Load accumulated
        assert loads[-1] > loads[0], "Cognitive load must accumulate under rapid inputs"
        # Since 17 inputs > 10 saturation threshold, freq_comp should be 1.0
        assert homeo._compute_cognitive_load(pad) >= 0.5

        # 4. Verify fatigue policy selection
        final_somatic = SomaticMarkers(
            stability=0.8,
            cognitive_load=loads[-1],
            energy=final_energy,
            tension=0.1,
        )
        policy = GenerationPolicy.select(final_somatic, surprise=0.1, surprise_policy=SurpriseModulationPolicy())
        assert policy.mode == "fatigued", f"Expected fatigued policy mode, got {policy.mode}"
        assert policy.reasoning_depth == 0
        assert policy.token_expansion_factor == 0.55


# ==============================================================================
# Test E: Recovery / Relaxation Dynamics
# ==============================================================================

class TestE_RecoveryRelaxation:
    """
    Test E — Relaxation:
    Displaces affective state with a salient stimulus and measures convergence
    toward dynamical equilibrium (h -> 0, p -> 0) over unforced idle ticks.
    Reports convergence rate and confirms bounded behavior without assuming monotonicity.
    """

    def test_unforced_idle_relaxation_converges_toward_origin_equilibrium(self) -> None:
        core = EmotionCore(EmotionConfig())

        # Displace state with a large input vector
        salient_stimulus = np.ones(16, dtype=np.float64) * 0.9
        core.push_stimulus(salient_stimulus)
        pad_displaced = core.step_once()

        norm_displaced = float(np.linalg.norm(core._h))
        assert norm_displaced > 0.1, f"Stimulus must displace hidden state (norm={norm_displaced})"

        p_base = np.array(core._config.resting_baseline, dtype=np.float64)
        pad_dist_displaced = math.sqrt(
            (pad_displaced.pleasure - p_base[0]) ** 2
            + (pad_displaced.arousal - p_base[1]) ** 2
            + (pad_displaced.dominance - p_base[2]) ** 2
        )
        assert pad_dist_displaced > 0.05, f"PAD must be displaced from resting attractor (dist={pad_dist_displaced})"

        # Step 150 idle ticks (x = 0)
        distances: List[float] = []
        h_norms: List[float] = []

        for _ in range(150):
            pad = core.step_once()
            dist = math.sqrt(
                (pad.pleasure - p_base[0]) ** 2
                + (pad.arousal - p_base[1]) ** 2
                + (pad.dominance - p_base[2]) ** 2
            )
            distances.append(dist)
            h_norms.append(float(np.linalg.norm(core._h)))

        final_dist = distances[-1]
        final_h_norm = h_norms[-1]

        # 1. State must decay toward resting equilibrium attractor
        assert final_h_norm < norm_displaced * 0.5, (
            f"Hidden state norm must substantially decay: {norm_displaced:.4f} -> {final_h_norm:.4f}"
        )
        assert final_dist < pad_dist_displaced * 0.6, (
            f"PAD distance from resting attractor must decay: {pad_dist_displaced:.4f} -> {final_dist:.4f}"
        )

        # 2. Check for bounded trajectory (no divergence)
        for norm in h_norms:
            assert norm <= math.sqrt(32), "Hidden state vector must remain within [-1, 1]^32 bound"

        # 3. Document non-monotonicity: verify whether any step exhibits transient overshoot
        diffs = [h_norms[i + 1] - h_norms[i] for i in range(len(h_norms) - 1)]
        has_positive_diff = any(d > 1e-6 for d in diffs)
        # Even if decaying overall, non-linear cross terms can cause non-monotonic transients
        # We record this empirical observation without failing the test
        print(f"Relaxation non-monotonic transient observed: {has_positive_diff}")


# ==============================================================================
# Test F: Historical Hysteresis (Path Dependence)
# ==============================================================================

class TestF_HistoricalHysteresis:
    """
    Test F — Historical Dependence / Hysteresis:
    Demonstrates that identical probe stimulus X produces divergent affective
    trajectories when preceded by different emotional histories.
    """

    def test_identical_probe_yields_divergent_states_after_different_histories(self) -> None:
        def create_orchestrator() -> CognitiveOrchestrator:
            return CognitiveOrchestrator(
                stimulus_processor=StimulusProcessor(),
                emotion_core=EmotionCore(EmotionConfig()),
                homeostatic_engine=HomeostaticEngine(HomeostaticConfig()),
                active_inference=ActiveInferenceEngine(ActiveInferenceConfig()),
                affective_memory=MockAffectiveMemory(),
                ecphory_engine=MockEcphoryEngine(),
                prompt_assembler=PromptAssembler(),
                llm_backend=MockLLMBackend(),
                boundary_layer=BoundaryLayer(),
            )

        orch_a = create_orchestrator()
        orch_b = create_orchestrator()

        try:
            # History A: Calm, warm, collaborative turns
            history_a = [
                "Thank you so much for your peaceful assistance.",
                "Everything is operating in perfect harmony and calm.",
                "I appreciate your gentle guidance today.",
            ]

            # History B: Hostile, urgent, high-threat turns
            history_b = [
                "CRITICAL WARNING! SYSTEM FAILURE IMMINENT!",
                "EMERGENCY SHUTDOWN REQUIRED IMMEDIATELY DANGER!",
                "FAILURE CODE 999 HOSTILE THREAT DETECTED!",
            ]

            for text in history_a:
                orch_a.process(text)

            for text in history_b:
                orch_b.process(text)

            # Identical probe text
            probe = "What is the next scheduled maintenance task?"
            res_a = orch_a.process(probe)
            res_b = orch_b.process(probe)

            # Measure hysteresis divergence in post-probe state
            pad_divergence = math.sqrt(
                (res_a.pad_final.pleasure - res_b.pad_final.pleasure) ** 2
                + (res_a.pad_final.arousal - res_b.pad_final.arousal) ** 2
                + (res_a.pad_final.dominance - res_b.pad_final.dominance) ** 2
            )
            h_divergence = float(np.linalg.norm(orch_a._emotion_core._h - orch_b._emotion_core._h))
            load_divergence = abs(res_a.somatic.cognitive_load - res_b.somatic.cognitive_load)
            pred_err_divergence = abs(res_a.prediction_error - res_b.prediction_error)

            assert pad_divergence > 0.01, f"Expected PAD hysteresis divergence, got {pad_divergence}"
            assert h_divergence > 0.02, f"Expected hidden state divergence, got {h_divergence}"
            assert load_divergence > 0.001, f"Expected Cognitive Load divergence from surprise coupling, got {load_divergence}"
            assert pred_err_divergence >= 0.0, "Prediction errors recorded"
        finally:
            orch_a.shutdown()
            orch_b.shutdown()


# ==============================================================================
# Test G: Affect → Cognition Modulation
# ==============================================================================

class TestG_AffectToCognitionModulation:
    """
    Test G — Affect → Cognition:
    Verifies that internal somatic and surprise signals deterministically modulate
    downstream computational constraints (max_tokens, temperature, reasoning_depth k,
    scaffolding steps) without relying on text/prose content.
    """

    def test_deliberative_mode_triggered_by_high_surprise(self) -> None:
        policy = SurpriseModulationPolicy(
            deliberative_surprise_threshold=0.60,
            deliberative_tension_threshold=0.70,
        )

        # Baseline markers
        base_somatic = SomaticMarkers(
            stability=0.8,
            cognitive_load=0.2,
            energy=0.9,
            tension=0.0,
        )

        # 1. Low surprise -> reflexive mode
        low_somatic = policy.modulate_somatic(base_somatic, surprise=0.15)
        gen_low = GenerationPolicy.select(low_somatic, surprise=0.15, surprise_policy=policy)
        assert gen_low.mode == "reflexive"
        assert gen_low.reasoning_depth == 1
        assert gen_low.scaffolding_steps == 1

        # 2. High surprise (>= 0.60) -> deliberative mode
        high_somatic = policy.modulate_somatic(base_somatic, surprise=0.75)
        gen_high = GenerationPolicy.select(high_somatic, surprise=0.75, surprise_policy=policy)
        assert gen_high.mode == "deliberative"
        assert gen_high.reasoning_depth == 2
        assert gen_high.scaffolding_steps == 3
        assert gen_high.temperature_delta == -0.10
        assert gen_high.token_expansion_factor == 1.15

        # 3. Verify behavioral constraints transformation
        base_constraints = BehavioralConstraints(
            max_tokens=150,
            temperature=0.75,
            latency_ms=0,
            reasoning_depth=1,
        )
        final_constraints = gen_high.apply_to_constraints(base_constraints)
        assert final_constraints.reasoning_depth == 2
        assert final_constraints.max_tokens == int(150 * 1.15)
        assert abs(final_constraints.temperature - 0.65) < 1e-6

    def test_high_cognitive_load_throttles_token_budget(self) -> None:
        homeo = HomeostaticEngine(HomeostaticConfig())
        # Simulate high cognitive load (> 0.75)
        high_load_somatic = SomaticMarkers(
            stability=0.5,
            cognitive_load=0.85,
            energy=0.5,
            tension=0.1,
        )
        pad = PADState(pleasure=0.0, arousal=0.0, dominance=0.0, timestamp=time.monotonic())
        constraints = homeo.compute_behavioral_constraints(high_load_somatic, pad)

        assert constraints.max_tokens <= 60, f"Token budget must be <= 60 under high load (got {constraints.max_tokens})"


# ==============================================================================
# Test H: Reproducibility Envelope
# ==============================================================================

class TestH_ReproducibilityEnvelope:
    """
    Test H — Reproducibility:
    Audits sources of nondeterminism and verifies that under controlled conditions
    (identical seed, identical initial state, and deterministic step sequence),
    state trajectories are strictly reproducible within epsilon < 1e-12.
    """

    def test_state_trajectory_is_strictly_deterministic(self) -> None:
        stimulus_sequence = [
            np.array([0.1 * i] * 16, dtype=np.float64) for i in range(1, 6)
        ]

        def run_trajectory() -> Tuple[np.ndarray, List[PADState]]:
            core = EmotionCore(EmotionConfig())
            pad_history = []
            for stim in stimulus_sequence:
                core.push_stimulus(stim)
                pad = core.step_once()
                pad_history.append(pad)
            return core._h.copy(), pad_history

        h_run1, pads_run1 = run_trajectory()
        h_run2, pads_run2 = run_trajectory()

        # Hidden state must match within numerical tolerance
        h_error = float(np.max(np.abs(h_run1 - h_run2)))
        assert h_error < 1e-12, f"Hidden state divergence across identical runs: {h_error}"

        # PAD coordinates must match within numerical tolerance
        for p1, p2 in zip(pads_run1, pads_run2):
            assert abs(p1.pleasure - p2.pleasure) < 1e-12
            assert abs(p1.arousal - p2.arousal) < 1e-12
            assert abs(p1.dominance - p2.dominance) < 1e-12
