"""
Cognitive Execution Trace Subsystem.

Execution and state diagnostic observability for the serialized S1–S16 cognitive pipeline:
    Turn -> S1 -> S2 -> ... -> S16

Invariants:
- Execution & state diagnostic only (NOT a reasoning trace, no CoT, no prompts, no memories).
- Zero disk or network I/O in the cognitive execution path.
- Read-only with respect to cognitive state.
- Fail-open: Telemetry exceptions never disrupt the cognitive turn.
- Lightweight, CPU-only; no LLM or GPU dependencies.
- Bounded memory footprint via in-memory circular buffer.
- Conservative causal attribution (first_causal_failure_candidate + DAG propagation).
"""

from __future__ import annotations

import collections
from dataclasses import dataclass, field
from enum import Enum
import logging
import threading
import time
from typing import Any, Dict, List, Optional, Set, Union
import uuid

logger = logging.getLogger("lucia.telemetry.execution_trace")


# ---------------------------------------------------------------------------
# Enums & Failure Taxonomy
# ---------------------------------------------------------------------------

class SpanStatus(str, Enum):
    SUCCESS = "SUCCESS"
    FAILURE = "FAILURE"
    SKIPPED = "SKIPPED"
    DEGRADED = "DEGRADED"


class ContractResult(str, Enum):
    SATISFIED = "SATISFIED"
    VIOLATED = "VIOLATED"
    NOT_APPLICABLE = "N/A"


class InvariantResult(str, Enum):
    SATISFIED = "SATISFIED"
    VIOLATED = "VIOLATED"
    NOT_APPLICABLE = "N/A"


class ExecutionFailureClass(str, Enum):
    HARD_EXECUTION_FAILURE = "HARD_EXECUTION_FAILURE"
    TIMEOUT = "TIMEOUT"
    CONTRACT_VIOLATION = "CONTRACT_VIOLATION"
    INVARIANT_VIOLATION = "INVARIANT_VIOLATION"
    INVALID_STATE_TRANSITION = "INVALID_STATE_TRANSITION"
    ABNORMAL_NUMERICAL_DYNAMICS = "ABNORMAL_NUMERICAL_DYNAMICS"
    DOWNSTREAM_PROPAGATED_FAILURE = "DOWNSTREAM_PROPAGATED_FAILURE"
    BEHAVIORAL_ANOMALY = "BEHAVIORAL_ANOMALY"


# ---------------------------------------------------------------------------
# Causal Dependency Graph (DAG) for Stages S1–S16
# ---------------------------------------------------------------------------

STAGE_CAUSAL_DEPENDENCIES: Dict[str, Set[str]] = {
    "S1": set(),
    "S2": set(),
    "S3": {"S1"},
    "S4": {"S2", "S3"},
    "S5": {"S3", "S4"},
    "S6": {"S1", "S3"},
    "S7": {"S6"},
    "S8": {"S1"},
    "S9": set(),
    "S10": {"S3", "S5", "S9"},
    "S11": {"S5", "S7", "S8", "S10"},
    "S12": {"S5", "S10"},
    "S13": {"S11"},
    "S14": {"S13"},
    "S15": {"S3", "S5", "S9"},
    "S16": {"S1", "S3", "S4"},
}


def get_transitive_ancestors(stage_id: str) -> Set[str]:
    """Return all transitive causal ancestors for a given stage sequence ID."""
    ancestors: Set[str] = set()
    queue = list(STAGE_CAUSAL_DEPENDENCIES.get(stage_id, set()))
    while queue:
        curr = queue.pop()
        if curr not in ancestors:
            ancestors.add(curr)
            queue.extend(STAGE_CAUSAL_DEPENDENCIES.get(curr, set()))
    return ancestors


# ---------------------------------------------------------------------------
# Data Models
# ---------------------------------------------------------------------------

@dataclass
class ExecutionSpan:
    """
    Diagnostic execution span for an individual S1–S16 stage.

    Contains exclusively bounded, allowlisted diagnostic scalars.
    Never stores prompts, CoT, completions, or raw memories.
    """
    span_id: str
    sequence_id: str                 # "S1", "S2", ..., "S16"
    stage_name: str                  # e.g. "SensoryEncoding"
    start_time_ns: int
    module_id: Optional[str] = None
    module_version: Optional[str] = None
    end_time_ns: Optional[int] = None
    duration_ms: float = 0.0
    status: SpanStatus = SpanStatus.SUCCESS
    contract_result: ContractResult = ContractResult.SATISFIED
    invariant_result: InvariantResult = InvariantResult.SATISFIED
    state_summary: Dict[str, Any] = field(default_factory=dict)
    failure_class: Optional[ExecutionFailureClass] = None
    failure_detail: Optional[str] = None
    causal_parent: Optional[str] = None
    is_primary_candidate: bool = False
    propagated_from: Optional[str] = None

    def set_summary(self, summary: Dict[str, Any]) -> None:
        """Record allowlisted scalar metrics safely."""
        try:
            for k, v in summary.items():
                if isinstance(v, (int, bool)) or v is None:
                    self.state_summary[k] = v
                elif isinstance(v, float):
                    self.state_summary[k] = round(v, 6)
                elif isinstance(v, str):
                    # Enforce strict bounded string length for enum/status representations
                    self.state_summary[k] = v[:61] + "..." if len(v) > 64 else v
        except Exception as exc:
            logger.debug("ExecutionSpan.set_summary error: %s", exc)

    def record_contract(
        self,
        satisfied: bool,
        failure_class: ExecutionFailureClass = ExecutionFailureClass.CONTRACT_VIOLATION,
        detail: Optional[str] = None,
    ) -> None:
        """Record contract evaluation outcome."""
        try:
            if not satisfied:
                self.contract_result = ContractResult.VIOLATED
                self.status = SpanStatus.FAILURE
                self.failure_class = failure_class
                self.failure_detail = detail
            else:
                self.contract_result = ContractResult.SATISFIED
        except Exception as exc:
            logger.debug("ExecutionSpan.record_contract error: %s", exc)

    def record_invariant(
        self,
        satisfied: bool,
        failure_class: ExecutionFailureClass = ExecutionFailureClass.INVARIANT_VIOLATION,
        detail: Optional[str] = None,
    ) -> None:
        """Record invariant evaluation outcome."""
        try:
            if not satisfied:
                self.invariant_result = InvariantResult.VIOLATED
                self.status = SpanStatus.FAILURE
                self.failure_class = failure_class
                self.failure_detail = detail
            else:
                self.invariant_result = InvariantResult.SATISFIED
        except Exception as exc:
            logger.debug("ExecutionSpan.record_invariant error: %s", exc)

    def to_dict(self) -> Dict[str, Any]:
        """Convert span to serializable diagnostic dictionary."""
        return {
            "span_id": self.span_id,
            "sequence_id": self.sequence_id,
            "stage_name": self.stage_name,
            "module_id": self.module_id,
            "module_version": self.module_version,
            "start_time_ns": self.start_time_ns,
            "end_time_ns": self.end_time_ns,
            "duration_ms": round(self.duration_ms, 4),
            "status": self.status.value,
            "contract_result": self.contract_result.value,
            "invariant_result": self.invariant_result.value,
            "state_summary": dict(self.state_summary),
            "failure_class": self.failure_class.value if self.failure_class else None,
            "failure_detail": self.failure_detail,
            "causal_parent": self.causal_parent,
            "is_primary_candidate": self.is_primary_candidate,
            "propagated_from": self.propagated_from,
        }


@dataclass
class CognitiveTurnTrace:
    """
    Diagnostic trace for a complete serialized cognitive turn.
    """
    trace_id: str
    turn_id: int
    call_id: str
    start_time_ns: int
    end_time_ns: Optional[int] = None
    duration_ms: float = 0.0
    spans: List[ExecutionSpan] = field(default_factory=list)
    first_causal_failure_candidate: Optional[str] = None
    overall_status: SpanStatus = SpanStatus.SUCCESS
    failed_stages: Set[str] = field(default_factory=set)

    def add_span(self, span: ExecutionSpan) -> None:
        """
        Add span and evaluate conservative causal attribution.
        """
        try:
            self.spans.append(span)

            is_failure = (
                span.status == SpanStatus.FAILURE
                or span.contract_result == ContractResult.VIOLATED
                or span.invariant_result == InvariantResult.VIOLATED
                or span.failure_class is not None
            )

            if is_failure:
                self.overall_status = SpanStatus.FAILURE

                if self.first_causal_failure_candidate is None:
                    # First causal failure candidate in the turn
                    span.is_primary_candidate = True
                    span.propagated_from = None
                    self.first_causal_failure_candidate = span.sequence_id
                    self.failed_stages.add(span.sequence_id)
                else:
                    # Check whether failure propagates from an upstream failed ancestor
                    ancestors = get_transitive_ancestors(span.sequence_id)
                    failed_ancestors = ancestors.intersection(self.failed_stages)

                    if failed_ancestors:
                        span.is_primary_candidate = False
                        span.propagated_from = self.first_causal_failure_candidate
                        span.failure_class = ExecutionFailureClass.DOWNSTREAM_PROPAGATED_FAILURE
                        self.failed_stages.add(span.sequence_id)
                    else:
                        # Independent failure
                        span.is_primary_candidate = False
                        span.propagated_from = None
                        self.failed_stages.add(span.sequence_id)
        except Exception as exc:
            logger.debug("CognitiveTurnTrace.add_span error: %s", exc)

    def get_span(self, sequence_id: str) -> Optional[ExecutionSpan]:
        """Lookup an execution span by sequence ID (e.g. 'S1', 'S3')."""
        for s in self.spans:
            if s.sequence_id == sequence_id:
                return s
        return None

    def close(self) -> None:
        """Finalize turn trace duration."""
        try:
            if self.end_time_ns is None:
                self.end_time_ns = time.perf_counter_ns()
                self.duration_ms = (self.end_time_ns - self.start_time_ns) / 1_000_000.0
        except Exception as exc:
            logger.debug("CognitiveTurnTrace.close error: %s", exc)

    def to_dict(self) -> Dict[str, Any]:
        """Convert trace to serializable diagnostic dictionary."""
        return {
            "trace_id": self.trace_id,
            "turn_id": self.turn_id,
            "call_id": self.call_id,
            "start_time_ns": self.start_time_ns,
            "end_time_ns": self.end_time_ns,
            "duration_ms": round(self.duration_ms, 4),
            "first_causal_failure_candidate": self.first_causal_failure_candidate,
            "overall_status": self.overall_status.value,
            "spans_count": len(self.spans),
            "spans": [s.to_dict() for s in self.spans],
        }


# ---------------------------------------------------------------------------
# In-Memory Bounded Trace Buffer
# ---------------------------------------------------------------------------

class TraceBuffer:
    """
    In-memory, thread-safe, bounded circular buffer for CognitiveTurnTrace objects.
    Enforces maximum capacity (default: 100 turns) and executes zero disk or network I/O.
    """

    def __init__(self, capacity: int = 100):
        self._capacity = max(1, int(capacity))
        self._buffer: collections.deque[CognitiveTurnTrace] = collections.deque(maxlen=self._capacity)
        self._lock = threading.Lock()

    @property
    def capacity(self) -> int:
        return self._capacity

    def append(self, trace: CognitiveTurnTrace) -> None:
        try:
            with self._lock:
                self._buffer.append(trace)
        except Exception as exc:
            logger.debug("TraceBuffer.append error: %s", exc)

    def get_latest(self) -> Optional[CognitiveTurnTrace]:
        try:
            with self._lock:
                return self._buffer[-1] if self._buffer else None
        except Exception as exc:
            logger.debug("TraceBuffer.get_latest error: %s", exc)
            return None

    def get_all(self) -> List[CognitiveTurnTrace]:
        try:
            with self._lock:
                return list(self._buffer)
        except Exception as exc:
            logger.debug("TraceBuffer.get_all error: %s", exc)
            return []

    def get_recent(self, limit: int = 10) -> List[CognitiveTurnTrace]:
        try:
            with self._lock:
                items = list(self._buffer)
                return items[-limit:] if limit > 0 else []
        except Exception as exc:
            logger.debug("TraceBuffer.get_recent error: %s", exc)
            return []

    def __len__(self) -> int:
        with self._lock:
            return len(self._buffer)

    def clear(self) -> None:
        with self._lock:
            self._buffer.clear()


# ---------------------------------------------------------------------------
# Span Context Manager & Tracer Coordinator
# ---------------------------------------------------------------------------

class _SpanContext:
    """Context manager for stage-level span execution."""

    def __init__(
        self,
        tracer: CognitiveExecutionTracer,
        sequence_id: str,
        stage_name: str,
        module_id: Optional[str] = None,
        module_version: Optional[str] = None,
        causal_parent: Optional[str] = None,
    ):
        self._tracer = tracer
        self._sequence_id = sequence_id
        self._stage_name = stage_name
        self._module_id = module_id
        self._module_version = module_version
        self._causal_parent = causal_parent
        self._span: Optional[ExecutionSpan] = None

    def __enter__(self) -> ExecutionSpan:
        try:
            span_id = f"span_{uuid.uuid4().hex[:12]}"
            self._span = ExecutionSpan(
                span_id=span_id,
                sequence_id=self._sequence_id,
                stage_name=self._stage_name,
                module_id=self._module_id,
                module_version=self._module_version,
                start_time_ns=time.perf_counter_ns(),
                causal_parent=self._causal_parent,
            )
        except Exception as exc:
            logger.debug("_SpanContext.__enter__ error: %s", exc)
            self._span = ExecutionSpan(
                span_id="dummy",
                sequence_id=self._sequence_id,
                stage_name=self._stage_name,
                start_time_ns=time.perf_counter_ns(),
            )
        return self._span

    def __exit__(self, exc_type, exc_val, exc_tb) -> bool:
        try:
            if self._span is not None:
                end_ns = time.perf_counter_ns()
                self._span.end_time_ns = end_ns
                self._span.duration_ms = (end_ns - self._span.start_time_ns) / 1_000_000.0

                if exc_type is not None:
                    self._span.status = SpanStatus.FAILURE
                    if self._span.failure_class is None:
                        self._span.failure_class = ExecutionFailureClass.HARD_EXECUTION_FAILURE
                    self._span.failure_detail = f"{exc_type.__name__}: {str(exc_val)}"

                trace = self._tracer.active_trace
                if trace is not None:
                    trace.add_span(self._span)
        except Exception as exc:
            logger.debug("_SpanContext.__exit__ error: %s", exc)

        # Do NOT suppress exceptions raised by the cognitive stage itself
        return False


class NullSpanContext:
    """Fallback no-op context manager when span creation fails (fail-open guarantee)."""

    def __init__(self, sequence_id: str = "SX", stage_name: str = "Unknown"):
        self._span = ExecutionSpan(
            span_id="dummy_null_span",
            sequence_id=sequence_id,
            stage_name=stage_name,
            start_time_ns=time.perf_counter_ns(),
        )

    def __enter__(self) -> ExecutionSpan:
        return self._span

    def __exit__(self, exc_type, exc_val, exc_tb) -> bool:
        return False


class CognitiveExecutionTracer:
    """
    Coordinator for cognitive execution tracing.

    Guarantees:
    - Pure in-memory execution; zero disk/network I/O.
    - Fail-open: Telemetry errors are caught and logged, never failing the cognitive turn.
    - Read-only: Does not mutate any cognitive or embodiment state.
    """

    def __init__(
        self,
        buffer: Optional[TraceBuffer] = None,
        buffer_capacity: int = 100,
        trace_buffer: Optional[TraceBuffer] = None,
    ):
        resolved_buf = buffer if buffer is not None else trace_buffer
        self._buffer = resolved_buf if resolved_buf is not None else TraceBuffer(capacity=buffer_capacity)
        self._active_trace: Optional[CognitiveTurnTrace] = None
        self._lock = threading.Lock()

    @property
    def buffer(self) -> TraceBuffer:
        return self._buffer

    @property
    def active_trace(self) -> Optional[CognitiveTurnTrace]:
        with self._lock:
            return self._active_trace

    def start_turn(self, turn_id: int, call_id: str) -> Optional[CognitiveTurnTrace]:
        """Start a new turn trace."""
        try:
            trace_id = f"trace_{uuid.uuid4().hex[:16]}"
            trace = CognitiveTurnTrace(
                trace_id=trace_id,
                turn_id=turn_id,
                call_id=call_id,
                start_time_ns=time.perf_counter_ns(),
            )
            with self._lock:
                self._active_trace = trace
            return trace
        except Exception as exc:
            logger.debug("CognitiveExecutionTracer.start_turn error: %s", exc)
            return None

    def span(
        self,
        sequence_id: str,
        stage_name: str,
        module_id: Optional[str] = None,
        module_version: Optional[str] = None,
        causal_parent: Optional[str] = None,
    ) -> Union[_SpanContext, NullSpanContext]:
        """Context manager for an individual stage span."""
        try:
            return _SpanContext(
                tracer=self,
                sequence_id=sequence_id,
                stage_name=stage_name,
                module_id=module_id,
                module_version=module_version,
                causal_parent=causal_parent,
            )
        except Exception as exc:
            logger.debug("CognitiveExecutionTracer.span error: %s", exc)
            return NullSpanContext(sequence_id=sequence_id, stage_name=stage_name)

    def end_turn(self) -> Optional[CognitiveTurnTrace]:
        """Finalize the active turn trace and record it to the bounded buffer."""
        try:
            with self._lock:
                trace = self._active_trace
                self._active_trace = None

            if trace is not None:
                trace.close()
                self._buffer.append(trace)
                return trace
            return None
        except Exception as exc:
            logger.debug("CognitiveExecutionTracer.end_turn error: %s", exc)
            return None
