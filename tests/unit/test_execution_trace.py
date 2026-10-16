"""
tests/unit/test_execution_trace.py

Unit tests and verification harness for Blocker 4 — Cognitive Execution Observability.
Validates:
1. Ordered S1-S16 execution trace production on normal cognitive turn.
2. Temporal stage ordering preservation.
3. Injected S3 contract failure localization and downstream DAG propagation.
4. Independent downstream failure separation (non-attribution to S3).
5. Fail-open telemetry resilience (telemetry errors never break cognitive turn).
6. Bounded in-memory trace buffer (FIFO eviction).
7. Read-only non-mutation of cognitive state.
8. Preservation of Genesis and First Activation invariants (INV-8).
9. Telemetry latency and memory overhead benchmarks.
"""

from __future__ import annotations

import json
import os
import sys
import time
import tracemalloc
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

from src.core.config import MemoryOrchestratorConfig
from src.core.orchestrator.cognitive_orchestrator import (
    CognitiveOrchestrator,
    build_cognitive_orchestrator,
)
from src.core.orchestrator.policies import CognitiveTurnResult
from src.core.telemetry.execution_trace import (
    STAGE_CAUSAL_DEPENDENCIES,
    CognitiveExecutionTracer,
    CognitiveTurnTrace,
    ContractResult,
    ExecutionFailureClass,
    ExecutionSpan,
    InvariantResult,
    SpanStatus,
    TraceBuffer,
    get_transitive_ancestors,
)


@pytest.fixture
def test_config(tmp_path):
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
def mock_orchestrator(test_config):
    with patch("src.core.orchestrator.cognitive_orchestrator.LLMBackend") as mock_llm_cls:
        mock_llm = MagicMock()
        mock_llm.is_ready.return_value = True
        mock_llm.generate.return_value = "I am listening with quiet attention."
        mock_llm_cls.return_value = mock_llm

        orch = build_cognitive_orchestrator(test_config)
        yield orch
        orch.shutdown()


class TestCognitiveExecutionTrace:
    """Test suite for S1-S16 cognitive execution trace."""

    def test_01_normal_turn_produces_ordered_s1_s16_trace(self, mock_orchestrator):
        """1. A normal turn produces the expected ordered S1-S16 trace with 16 spans."""
        result = mock_orchestrator.process("Hello Lucia, how is your day?")

        assert isinstance(result, CognitiveTurnResult)
        assert result.execution_trace is not None
        trace = result.execution_trace
        assert isinstance(trace, CognitiveTurnTrace)

        # Check turn identification
        assert trace.call_id == result.call_id
        assert isinstance(trace.turn_id, int)
        assert trace.overall_status == SpanStatus.SUCCESS
        assert trace.first_causal_failure_candidate is None

        # Check all 16 stages exist in exact sequence
        expected_stages = [f"S{i}" for i in range(1, 17)]
        span_stages = [s.sequence_id for s in trace.spans]
        assert span_stages == expected_stages

        # Check each span has required fields, duration, and status
        for span in trace.spans:
            assert span.status == SpanStatus.SUCCESS
            assert span.duration_ms >= 0.0
            assert span.contract_result in (ContractResult.SATISFIED, ContractResult.NOT_APPLICABLE)
            assert span.invariant_result in (InvariantResult.SATISFIED, InvariantResult.NOT_APPLICABLE)
            assert span.failure_class is None
            assert span.propagated_from is None
            assert isinstance(span.state_summary, dict)

        # Confirm diagnostics are bounded and strictly non-introspective
        for span in trace.spans:
            for k, v in span.state_summary.items():
                if isinstance(v, str):
                    assert len(v) <= 128, f"Summary string for key {k} is excessively long ({len(v)} chars)"
                # Ensure no forbidden dumps
                assert "prompt" not in k.lower() or k == "prompt_len"
                assert "raw_completion" not in k.lower()
                assert "chain_of_thought" not in k.lower()
                assert "internal_monologue" not in k.lower()

        # Check latest trace retrieval on orchestrator
        latest = mock_orchestrator.get_latest_trace()
        assert latest is trace

    def test_02_stage_ordering_is_strictly_preserved(self, mock_orchestrator):
        """2. Stage ordering is preserved: monotonic timestamps across S1-S16."""
        result = mock_orchestrator.process("Preserve ordering test.")
        trace = result.execution_trace
        assert trace is not None

        spans = trace.spans
        assert len(spans) == 16

        for i in range(len(spans)):
            span = spans[i]
            assert span.start_time_ns <= span.end_time_ns, (
                f"Span {span.sequence_id} start_time_ns ({span.start_time_ns}) > end_time_ns ({span.end_time_ns})"
            )
            if i > 0:
                prev_span = spans[i - 1]
                assert prev_span.start_time_ns <= span.start_time_ns, (
                    f"Stage {prev_span.sequence_id} start ({prev_span.start_time_ns}) after "
                    f"Stage {span.sequence_id} start ({span.start_time_ns})"
                )

    def test_03_injected_s3_contract_failure_attribution(self):
        """
        3. Injected S3 contract failure identifies:
           - S3 as first_causal_failure_candidate
           - Downstream failures as propagated where DAG dependency exists (e.g. S4).
        """
        tracer = CognitiveExecutionTracer()
        tracer.start_turn(turn_id=1, call_id="test-turn-s3-fail")

        # Stage S1 succeeds
        with tracer.span("S1", "SensoryInput"):
            pass

        # Stage S2 succeeds
        with tracer.span("S2", "PriorExpectation"):
            pass

        # Stage S3 fails on contract
        with tracer.span("S3", "LimbicIntegration", causal_parent="S1") as s3_span:
            s3_span.record_contract(
                satisfied=False,
                failure_class=ExecutionFailureClass.CONTRACT_VIOLATION,
                detail="S3 limbic contract violated: ODE delta out of bounds",
            )

        # Stage S4 fails as a result of S3 invalid output
        with tracer.span("S4", "PredictionSurprise", causal_parent="S2") as s4_span:
            s4_span.record_contract(
                satisfied=False,
                failure_class=ExecutionFailureClass.CONTRACT_VIOLATION,
                detail="S4 cannot evaluate surprise with invalid limbic output",
            )

        # Stage S5 succeeds
        with tracer.span("S5", "HomeostaticModulation", causal_parent="S4"):
            pass

        trace = tracer.end_turn()

        assert trace.overall_status == SpanStatus.FAILURE
        assert trace.first_causal_failure_candidate == "S3"

        s3 = trace.get_span("S3")
        assert s3 is not None
        assert s3.status == SpanStatus.FAILURE
        assert s3.is_primary_candidate is True
        assert s3.propagated_from is None
        assert s3.failure_class == ExecutionFailureClass.CONTRACT_VIOLATION

        s4 = trace.get_span("S4")
        assert s4 is not None
        assert s4.status == SpanStatus.FAILURE
        assert s4.is_primary_candidate is False
        assert s4.propagated_from == "S3"
        assert s4.failure_class == ExecutionFailureClass.DOWNSTREAM_PROPAGATED_FAILURE

    def test_04_independent_downstream_failure_not_attributed_to_s3(self):
        """
        4. Independent downstream failure is not incorrectly attributed to S3.
           S9 has NO causal dependency on S3 in the DAG.
           If S3 fails AND S9 fails independently, S9 must NOT be marked propagated_from="S3".
        """
        tracer = CognitiveExecutionTracer()
        tracer.start_turn(turn_id=1, call_id="test-turn-independent-fail")

        # S3 has causal ancestor S1.
        # S9 (Knowledge / Relational read) has no upstream dependency on S3.
        assert "S3" not in get_transitive_ancestors("S9")

        with tracer.span("S1", "SensoryInput"):
            pass
        with tracer.span("S2", "PriorExpectation"):
            pass

        # S3 fails
        with tracer.span("S3", "LimbicIntegration", causal_parent="S1") as s3_span:
            s3_span.record_contract(
                satisfied=False,
                failure_class=ExecutionFailureClass.CONTRACT_VIOLATION,
                detail="S3 numerical deviation",
            )

        # S9 fails independently with an invalid state transition
        with tracer.span("S9", "RelationalContext", causal_parent=None) as s9_span:
            s9_span.record_contract(
                satisfied=False,
                failure_class=ExecutionFailureClass.INVALID_STATE_TRANSITION,
                detail="S9 store corrupted",
            )

        trace = tracer.end_turn()

        assert trace.overall_status == SpanStatus.FAILURE
        assert trace.first_causal_failure_candidate == "S3"

        s3 = trace.get_span("S3")
        assert s3.is_primary_candidate is True
        assert s3.propagated_from is None

        s9 = trace.get_span("S9")
        # S9 is NOT propagated from S3 because S9 is not a downstream child of S3
        assert s9.propagated_from is None
        assert s9.failure_class == ExecutionFailureClass.INVALID_STATE_TRANSITION

    def test_05_telemetry_failure_does_not_fail_cognitive_turn(self, test_config):
        """5. Telemetry failure does not fail the cognitive turn (fail-open invariant)."""
        class FaultyTracer(CognitiveExecutionTracer):
            """Tracer that raises exceptions on every method call."""
            def start_turn(self, turn_id: int, call_id: str) -> None:
                raise RuntimeError("Faulty tracer: deliberate explosion in start_turn")

            def end_turn(self) -> None:
                raise RuntimeError("Faulty tracer: deliberate explosion in end_turn")

            def span(self, sequence_id: str, stage_name: str, **kwargs):
                raise RuntimeError("Faulty tracer: deliberate explosion in span")

        with patch("src.core.orchestrator.cognitive_orchestrator.LLMBackend") as mock_llm_cls:
            mock_llm = MagicMock()
            mock_llm.is_ready.return_value = True
            mock_llm.generate.return_value = "Cognitive turn succeeds despite telemetry failure."
            mock_llm_cls.return_value = mock_llm

            orch = build_cognitive_orchestrator(
                test_config,
                execution_tracer=FaultyTracer(),
            )
            try:
                # Orchestrator process() must not raise and must complete the turn
                result = orch.process("Test fail-open telemetry")
                assert result.response_text == "Cognitive turn succeeds despite telemetry failure."
                assert result.call_id is not None
            finally:
                orch.shutdown()

    def test_06_trace_buffer_remains_strictly_bounded(self):
        """6. Trace buffer remains bounded: FIFO eviction at capacity limit."""
        capacity = 5
        buffer = TraceBuffer(capacity=capacity)

        # Push 15 traces
        for i in range(15):
            tracer = CognitiveExecutionTracer(trace_buffer=buffer)
            tracer.start_turn(turn_id=i, call_id=f"call-{i:03d}")
            with tracer.span("S1", "SensoryInput"):
                pass
            tracer.end_turn()

        assert len(buffer) == capacity
        traces = buffer.get_recent(100)
        assert len(traces) == capacity

        # Verify FIFO: the retained turns should be the latest 5 (call-010 to call-014)
        retained_ids = [t.call_id for t in traces]
        expected_ids = [f"call-{i:03d}" for i in range(10, 15)]
        assert retained_ids == expected_ids

    def test_07_instrumentation_does_not_mutate_cognitive_state(self, mock_orchestrator):
        """7. Instrumentation is strictly read-only and does not mutate cognitive state."""
        # Record initial internal state
        initial_history_len = len(mock_orchestrator._history)

        result = mock_orchestrator.process("Testing non-mutation invariant.")

        # Confirm response text and generation policy are intact
        assert result.response_text == "I am listening with quiet attention."
        assert len(mock_orchestrator._history) == initial_history_len + 2

        # Trace exists and was recorded without affecting result fields
        assert result.execution_trace is not None
        assert result.execution_trace.overall_status == SpanStatus.SUCCESS

    def test_08_no_genesis_or_first_activation_triggered_by_tracing(self, mock_orchestrator):
        """
        8. No Genesis or First Activation behavior is triggered by tracing.
           Confirms data/profile.json remains {"is_onboarded": false} and
           data/genesis_commitment.json remains absent.
        """
        profile_path = Path("data/profile.json")
        commitment_path = Path("data/genesis_commitment.json")

        assert profile_path.exists(), "data/profile.json must exist"
        with open(profile_path, "r", encoding="utf-8") as f:
            profile_before = json.load(f)

        assert profile_before.get("is_onboarded") is False
        assert not commitment_path.exists(), "data/genesis_commitment.json must NOT exist"

        # Execute cognitive turns with execution tracing active
        mock_orchestrator.process("Observation check 1")
        mock_orchestrator.process("Observation check 2")

        # Verify invariants strictly hold post-execution
        with open(profile_path, "r", encoding="utf-8") as f:
            profile_after = json.load(f)

        assert profile_after == profile_before
        assert profile_after.get("is_onboarded") is False
        assert not commitment_path.exists(), "genesis_commitment.json was created during tracing!"

    def test_09_telemetry_overhead_benchmark(self, mock_orchestrator):
        """
        Measure basic overhead:
        - Latency per turn (target < 5ms trace overhead per turn).
        - Memory allocations per turn.
        """
        # Warm-up turn
        mock_orchestrator.process("Warmup")

        # Measure 20 turns
        n_turns = 20
        tracemalloc.start()
        snapshot_start = tracemalloc.take_snapshot()
        t_start = time.perf_counter()

        for i in range(n_turns):
            result = mock_orchestrator.process(f"Benchmark turn {i}")
            assert result.execution_trace is not None

        elapsed_total_s = time.perf_counter() - t_start
        snapshot_end = tracemalloc.take_snapshot()
        tracemalloc.stop()

        avg_latency_ms = (elapsed_total_s / n_turns) * 1000.0

        # Measure telemetry-specific span execution time
        last_trace = mock_orchestrator.get_latest_trace()
        assert last_trace is not None
        span_durations_sum = sum(s.duration_ms for s in last_trace.spans)

        # Calculate memory delta
        stats = snapshot_end.compare_to(snapshot_start, "lineno")
        total_mem_delta_kb = sum(stat.size_diff for stat in stats) / 1024.0

        print(f"\n--- Cognitive Execution Trace Overhead ---")
        print(f"Total turns: {n_turns}")
        print(f"Avg total turn latency (mock LLM): {avg_latency_ms:.2f} ms")
        print(f"Sum of S1-S16 span durations: {span_durations_sum:.2f} ms")
        print(f"Memory delta across {n_turns} turns: {total_mem_delta_kb:.2f} KB")
        print(f"Memory delta per turn: {total_mem_delta_kb / n_turns:.2f} KB")

        # Basic assertion: trace operations should not cause memory explosions (< 500KB per turn)
        assert (total_mem_delta_kb / n_turns) < 500.0
