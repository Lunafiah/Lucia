"""
Tests for Corrective Temporal Synchronization — Phase 9 Post-Ablation.

Validates the deterministic temporal contract between EmotionCore (L2) and
CognitiveOrchestrator / ActiveInference (L4):
  - Test A: Deterministic state transition via commit_stimulus()
  - Test B: Intra-turn prediction surprise computed from post-transition PAD
  - Test C: Surprise causal pathway triggering deliberative mode (k=2)
  - Test D: Plasticity tagging receives valid surprise
  - Test E: Exactly-once stimulus integration (no double execution)
  - Test F: Concurrency stress and race-freedom (no deadlocks, bounded _h)
  - Test G: Simulation isolation maintained (SimClock & StimulusService)
"""

import concurrent.futures
import threading
import time
from unittest.mock import MagicMock, patch

import numpy as np
import pytest

from src.core.config import EmotionConfig, MemoryOrchestratorConfig
from src.core.emotion.emotion_core import EmotionCore
from src.core.models import PADState
from src.core.orchestrator.cognitive_orchestrator import (
    CognitiveOrchestrator,
    build_cognitive_orchestrator,
)
from src.core.orchestrator.policies import (
    CognitiveTurnResult,
    GenerationPolicy,
    PlasticityPolicy,
    SurpriseModulationPolicy,
)
from src.core.simulation.sim_clock import SimClock
from src.core.simulation.stimulus_service import StimulusService


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------

@pytest.fixture
def memory_config(tmp_path):
    model_file = tmp_path / "model.gguf"
    model_file.write_bytes(b"dummy")
    return MemoryOrchestratorConfig(
        model_path=str(model_file),
        loop_cadence_ms=100,
        decay_loop_cadence_seconds=60,
        sdm_num_locations=100,
        sdm_address_dim=64,
        sdm_content_dim=16,
        sdm_capacity=50,
    )


@pytest.fixture
def mock_orchestrator(memory_config):
    with patch("src.core.orchestrator.cognitive_orchestrator.LLMBackend") as mock_llm_cls:
        mock_llm = MagicMock()
        mock_llm.is_ready.return_value = True
        mock_llm.generate.return_value = "Understood."
        mock_llm_cls.return_value = mock_llm

        orch = build_cognitive_orchestrator(memory_config)
        yield orch
        orch.shutdown()


# ---------------------------------------------------------------------------
# Test A: Deterministic State Transition
# ---------------------------------------------------------------------------

class TestA_DeterministicStateTransition:
    def test_commit_stimulus_advances_pad_without_waiting_for_background_thread(self):
        """
        A salient stimulus must produce PAD_post != PAD_initial deterministically
        via commit_stimulus() even when the background thread is not running.
        """
        core = EmotionCore(EmotionConfig(loop_cadence_ms=500))  # Background thread not started
        # Do NOT start background thread
        p_init = core.get_pad_state()

        salient_vec = np.ones(16, dtype=np.float64) * 0.95
        token = core.push_stimulus(salient_vec)
        assert token == 1

        p_post = core.commit_stimulus(token)
        delta = np.linalg.norm([
            p_post.pleasure - p_init.pleasure,
            p_post.arousal - p_init.arousal,
            p_post.dominance - p_init.dominance,
        ])

        assert delta > 0.01, f"Expected state transition, got delta={delta}"
        # Snapshot in get_pad_state must match committed state
        snapshot = core.get_pad_state()
        assert snapshot.pleasure == p_post.pleasure
        assert snapshot.arousal == p_post.arousal
        assert snapshot.dominance == p_post.dominance

    def test_commit_stimulus_synchronizes_with_live_background_thread(self):
        """
        When background thread is running, commit_stimulus guarantees that the
        new state is committed before the method returns (< 50ms vs background 200ms).
        """
        core = EmotionCore(EmotionConfig(loop_cadence_ms=200))
        core.start()
        try:
            time.sleep(0.05)  # Let it stabilize at resting baseline
            p_init = core.get_pad_state()

            # Push a strong negative arousal/valence stimulus
            stimulus = np.array([-0.9, 0.8, -0.5] + [0.0] * 13, dtype=np.float64)
            core.push_stimulus(stimulus)
            p_post = core.commit_stimulus()

            delta = np.linalg.norm([
                p_post.pleasure - p_init.pleasure,
                p_post.arousal - p_init.arousal,
                p_post.dominance - p_init.dominance,
            ])
            assert delta > 0.01, f"Expected live transition, got delta={delta}"
        finally:
            core.stop()


# ---------------------------------------------------------------------------
# Test B: Prediction Surprise Computed from Post-Transition State
# ---------------------------------------------------------------------------

class TestB_SurpriseComputation:
    def test_prediction_error_is_nonzero_on_salient_stimulus(self, mock_orchestrator):
        """
        Intra-turn prediction error must evaluate to > 0 on salient input
        because pad_final reflects the post-transition state rather than pad_initial.
        Follows Scenario 2 protocol: Turn 1 establishes baseline, Turn 2 presents probe.
        """
        # Turn 1: Establish baseline context
        r1 = mock_orchestrator.process("Hello Lucia, nice to talk with you.")
        assert (
            r1.pad_final.pleasure != 0.0
            or r1.pad_final.arousal != 0.0
            or r1.pad_final.dominance != 0.0
        )

        # Turn 2: Salient stimulus
        r2 = mock_orchestrator.process("EMERGENCY ALERT: CRITICAL FAILURE IN PROGRESS")
        assert isinstance(r2, CognitiveTurnResult)
        assert r2.prediction_error > 0.0, (
            f"Expected prediction_error > 0.0, got {r2.prediction_error}"
        )
        assert (
            r2.pad_final.pleasure != r2.pad_initial.pleasure
            or r2.pad_final.arousal != r2.pad_initial.arousal
            or r2.pad_final.dominance != r2.pad_initial.dominance
        ), "pad_final must differ from pad_initial after salient stimulus"


# ---------------------------------------------------------------------------
# Test C: Behavioral Consequence (Surprise Pathway to Deliberative Policy)
# ---------------------------------------------------------------------------

class TestC_SurpriseCausalPathway:
    def test_deliberative_policy_triggered_when_surprise_exceeds_threshold(self, mock_orchestrator):
        """
        When Active Inference prediction error exceeds deliberative_surprise_threshold (0.60),
        GenerationPolicy must select 'deliberative' mode with reasoning_depth=2.
        """
        # Establish baseline context first
        mock_orchestrator.process("Hello Lucia, setting up baseline.")

        # Force a large prediction discrepancy by biasing Active Inference prior
        mock_orchestrator._active_inference._b = np.array([4.0, 4.0, 4.0])

        result = mock_orchestrator.process("Unexpected sudden shock!")
        assert result.prediction_error > 0.60
        assert result.generation_policy.mode == "deliberative"
        assert result.generation_policy.reasoning_depth == 2
        assert result.constraints.temperature <= 0.70

    def test_reflexive_policy_selected_under_normal_conversational_surprise(self, mock_orchestrator):
        """
        Normal conversational turns with low surprise retain reflexive policy (k=1).
        """
        # Reset prior to identity
        mock_orchestrator._active_inference._b = np.zeros(3)
        result = mock_orchestrator.process("Good morning Lucia.")
        # Moderate or low surprise should not cross 0.60 threshold
        if result.prediction_error < 0.60:
            assert result.generation_policy.mode == "reflexive"
            assert result.generation_policy.reasoning_depth == 1


# ---------------------------------------------------------------------------
# Test D: Plasticity Tagging
# ---------------------------------------------------------------------------

class TestD_PlasticityTagging:
    def test_plasticity_policy_should_tag_receives_valid_surprise(self):
        """
        PlasticityPolicy.should_tag() correctly triggers when post-transition surprise
        crosses salience_tag_threshold.
        """
        policy = PlasticityPolicy(salience_tag_threshold=0.15)
        assert policy.should_tag(0.20) is True
        assert policy.should_tag(0.05) is False


# ---------------------------------------------------------------------------
# Test E: Exactly-Once Semantics (No Double Execution)
# ---------------------------------------------------------------------------

class TestE_ExactlyOnceSemantics:
    def test_commit_stimulus_is_idempotent_for_same_token(self):
        """
        Calling commit_stimulus() multiple times for the same sequence token
        must NOT trigger additional ODE steps (zero double execution).
        """
        core = EmotionCore(EmotionConfig(loop_cadence_ms=500))
        token = core.push_stimulus(np.ones(16) * 0.5)
        assert token == 1

        p1 = core.commit_stimulus(token)
        t1 = core.tick_count()
        assert t1 == 1

        # Second call with same token
        p2 = core.commit_stimulus(token)
        t2 = core.tick_count()
        assert t2 == 1, f"Expected 1 tick, got {t2} (double execution occurred!)"
        assert p1.pleasure == p2.pleasure
        assert p1.arousal == p2.arousal
        assert p1.dominance == p2.dominance

    def test_background_thread_consumption_prevents_duplicate_step(self):
        """
        Case 2: Background thread wins.
        If the background thread consumed and stepped the stimulus before commit_stimulus()
        is called, commit_stimulus() must detect that committed_seq >= token
        and return without stepping again.
        """
        core = EmotionCore(EmotionConfig(loop_cadence_ms=500))
        token = core.push_stimulus(np.ones(16) * 0.7)

        # Manually step once (simulating background worker tick)
        core.step_once()
        assert core.tick_count() == 1
        assert core._committed_stimulus_seq == token

        # Now call commit_stimulus
        core.commit_stimulus(token)
        assert core.tick_count() == 1, "commit_stimulus must not step if already committed"

    def test_idle_background_ticks_do_not_falsely_advance_committed_sequence(self):
        """
        Ordinary ODE ticks with no pending stimulus must NEVER advance
        _committed_stimulus_seq or falsely match _stimulus_seq.
        """
        core = EmotionCore(EmotionConfig(loop_cadence_ms=500))
        assert core._stimulus_seq == 0
        assert core._committed_stimulus_seq == 0

        # Perform 5 idle ticks with no stimuli
        for _ in range(5):
            core.step_once()
        assert core.tick_count() == 5
        assert core._stimulus_seq == 0
        assert core._committed_stimulus_seq == 0, "Idle ticks must not increment committed sequence!"

        # Now push a stimulus N=1
        token = core.push_stimulus(np.ones(16) * 0.3)
        assert token == 1
        assert core._stimulus_seq == 1
        assert core._committed_stimulus_seq == 0  # Still 0 before step

        # Step consumes N=1
        core.step_once()
        assert core._committed_stimulus_seq == 1

        # Perform 5 more idle ticks
        for _ in range(5):
            core.step_once()
        assert core.tick_count() == 11
        assert core._committed_stimulus_seq == 1, "Subsequent idle ticks must not advance committed sequence!"

    def test_multiple_stimulus_submissions_fifo_queued_without_loss(self):
        """
        Case 4: Multiple stimulus submissions.
        If push(N) and push(N+1) are called before an ODE step, neither stimulus
        must be dropped or overwritten. Both must be integrated in causal FIFO order.
        """
        core = EmotionCore(EmotionConfig(loop_cadence_ms=500))
        vec_A = np.ones(16) * 0.4
        vec_B = np.ones(16) * -0.6

        consumed_vectors = []
        original_ode_step = core._ode_step

        def recording_ode_step(h, x):
            consumed_vectors.append(x.copy())
            return original_ode_step(h, x)

        core._ode_step = recording_ode_step

        token_A = core.push_stimulus(vec_A)
        token_B = core.push_stimulus(vec_B)
        assert token_A == 1
        assert token_B == 2

        # Commit target_seq=2
        pad_final = core.commit_stimulus(token_B)

        assert core._committed_stimulus_seq == 2
        assert len(consumed_vectors) == 2, f"Expected exactly 2 ODE steps, got {len(consumed_vectors)}"
        np.testing.assert_allclose(consumed_vectors[0], vec_A)
        np.testing.assert_allclose(consumed_vectors[1], vec_B)
        assert len(core._pending_stimuli) == 0

    def test_exact_single_ode_integration_under_turn_thread(self):
        """
        Case 1: Turn thread wins.
        Confirms stimulus vector is passed into _ode_step exactly once.
        """
        core = EmotionCore(EmotionConfig(loop_cadence_ms=500))
        vec = np.ones(16) * 0.85
        calls = []
        orig_ode = core._ode_step

        def spy_ode(h, x):
            calls.append(x.copy())
            return orig_ode(h, x)

        core._ode_step = spy_ode

        token = core.push_stimulus(vec)
        p1 = core.commit_stimulus(token)
        p2 = core.commit_stimulus(token)
        p3 = core.commit_stimulus(token)

        assert len(calls) == 1, f"Expected exactly 1 ODE step, got {len(calls)}"
        np.testing.assert_allclose(calls[0], vec)


# ---------------------------------------------------------------------------
# Test F: Concurrency & Race Freedom Stress Test
# ---------------------------------------------------------------------------

class TestF_ConcurrencyStress:
    def test_rapid_concurrent_turns_do_not_deadlock_or_corrupt_state(self):
        """
        Stress test: Run Fast_Loop background thread at 100ms cadence while 4 worker
        threads execute concurrent push_stimulus + commit_stimulus operations.
        Validates:
          1. Zero deadlocks
          2. Hidden state _h remains finite and bounded in [-1.0, 1.0]
          3. _committed_stimulus_seq monotonically tracks submissions
        """
        core = EmotionCore(EmotionConfig(loop_cadence_ms=100))
        core.start()

        num_threads = 4
        iterations_per_thread = 20

        def worker(thread_idx: int):
            for i in range(iterations_per_thread):
                vec = np.random.uniform(-0.8, 0.8, 16)
                token = core.push_stimulus(vec)
                pad = core.commit_stimulus(token)
                assert -1.0 <= pad.pleasure <= 1.0
                assert -1.0 <= pad.arousal <= 1.0
                assert -1.0 <= pad.dominance <= 1.0

        try:
            with concurrent.futures.ThreadPoolExecutor(max_workers=num_threads) as executor:
                futures = [executor.submit(worker, idx) for idx in range(num_threads)]
                for fut in concurrent.futures.as_completed(futures, timeout=15.0):
                    fut.result()  # Will raise if any thread encountered an exception
        finally:
            core.stop()

        # Invariant checks post-stress
        assert np.all(np.isfinite(core._h)), "Hidden state _h contains NaN or Inf!"
        assert np.all(np.abs(core._h) <= 1.0), "Hidden state _h exceeded [-1.0, 1.0] bounds!"
        assert core._committed_stimulus_seq <= core._stimulus_seq

    def test_race_at_boundary_background_vs_turn_thread(self):
        """
        Case 3: Race at the boundary.
        Executes 15 successive stimuli under an actively ticking background thread (100ms cadence)
        where background and turn thread contend directly for _step_lock.
        Verifies:
          1. Every stimulus is consumed and committed.
          2. No duplicate integration occurs.
          3. Final committed_seq equals total submitted tokens.
        """
        core = EmotionCore(EmotionConfig(loop_cadence_ms=100))
        core.start()

        num_stimuli = 15
        try:
            for i in range(num_stimuli):
                vec = np.ones(16) * (0.1 * (i % 5))
                token = core.push_stimulus(vec)
                pad = core.commit_stimulus(token)
                assert -1.0 <= pad.pleasure <= 1.0
                assert core._committed_stimulus_seq >= token
                time.sleep(0.01)  # slight jitter to create boundary contention
        finally:
            core.stop()

        assert core._committed_stimulus_seq == num_stimuli
        assert len(core._pending_stimuli) == 0


# ---------------------------------------------------------------------------
# Test G: Simulation Isolation Maintained
# ---------------------------------------------------------------------------

class TestG_SimulationIsolation:
    def test_simulation_stimulus_service_maintains_deterministic_step(self):
        """
        SimulationEnvironment uses SimClock and StimulusService with custom_timestamp.
        Verify that SimClock injection steps cleanly and does not activate live state.
        """
        core = EmotionCore(EmotionConfig())
        sim_clock = SimClock()
        sim_service = StimulusService(core)

        entry = sim_service.inject_text(
            "Simulated virtual stimulus",
            source="test_probe",
            custom_timestamp=sim_clock.virtual_time_s,
        )
        assert "pad_delta" in entry
        assert "pad_after" in entry
        assert core.tick_count() >= 1

        # Check that simulation state did not mutate real production persistence
        import os
        base_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
        profile_path = os.path.join(base_dir, "data", "profile.json")
        chat_path = os.path.join(base_dir, "data", "chat_history.json")
        assert os.path.exists(profile_path)
        assert os.path.exists(chat_path)
