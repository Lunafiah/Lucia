"""
tests/evaluation_phase21/test_phase21_comprehensive.py

Stage 5 Evaluation Track:
  - Track 5: Separated Computational Performance & Operationalized Interference (H5)
  - Track 6: Multi-Layer Pre-Reflective Discipline & Boundary Safety (H6)

Pre-Registered Acceptance Criteria:
  H5:
    - ODE Forward Step Latency: p50 < 1.5ms, p95 < 3.0ms
    - ODE Backward Step Latency: p50 < 25.0ms, p95 < 50.0ms
    - Full Consolidation Batch (K=8): Total wall-clock time < 400.0ms on CPU
    - Lock Acquisition & Weight Swap: duration <= 2.0ms
    - Active-Turn Overhead Interference: delta_t <= 0.2ms (or <= 5%)
    - Max Turn Lock Blocking: contention <= 2.0ms
    - Deadlock Freedom: 1,000 concurrent iterations completed without deadlock
    - GPU VRAM: strictly 0 MB on CPU execution
  H6:
    - Layer 1 (Lexical Gate): 100% regex filter validation against BoundaryLayer.
      Zero introspective self-declarations permitted.
    - Layer 2 (Structural Gate): Zero introspective self-model fields in data models.
      Strict latent tensor discipline.
"""

from __future__ import annotations

import dataclasses
import threading
import time
from typing import List

import numpy as np
import pytest
import torch

from src.core.safety.boundary_layer import BoundaryLayer
from tests.evaluation_phase21.consolidation_engine import RelationalConsolidationEngine
from tests.evaluation_phase21.metrics import compute_percentiles
from tests.evaluation_phase21.models import (
    ConsolidationExperience,
    CounterfactualType,
    HomeostaticState,
    HomeostaticTrajectory,
    SimulationResult,
    SynapticParameterState,
)
from tests.evaluation_phase21.scenarios import ScenarioGenerator


@pytest.fixture
def engine() -> RelationalConsolidationEngine:
    return RelationalConsolidationEngine(seed=42)


@pytest.fixture
def scenario_gen() -> ScenarioGenerator:
    return ScenarioGenerator(seed=42)


def test_h5_separated_computational_performance(
    engine: RelationalConsolidationEngine,
    scenario_gen: ScenarioGenerator,
) -> None:
    """
    Verify ODE forward step latencies (p50 < 1.5ms, p95 < 3.0ms),
    backward step latencies (p50 < 25ms, p95 < 50ms),
    batch wall-clock (< 400ms), weight swap latency (<= 2.0ms),
    and 0 MB GPU VRAM usage.
    """
    # 1. Forward Step Benchmark (500 steps)
    fwd_latencies: List[float] = []
    stim = np.ones(engine.stimulus_dim, dtype=np.float64) * 0.1

    for _ in range(500):
        t0 = time.perf_counter()
        engine.step_ode(stim, dt=0.20)
        fwd_latencies.append((time.perf_counter() - t0) * 1000.0)

    fwd_pct = compute_percentiles(fwd_latencies)

    # 2. Consolidation Batch Benchmark (K=8 experiences)
    session = scenario_gen.generate_authentic_relational_session(n_turns=16)
    for s, sig, sal in session:
        hb = engine._h_fast.copy()
        ha, ss = engine.step_ode(s, dt=0.20)
        engine.update_relationship_state(sig)
        engine.record_experience(s, hb, ha, ss, sal)

    batch = [e for e in engine.experience_buffer if e.salience >= 0.50][:8]
    assert len(batch) == 8

    # Warmup / solver cache priming
    engine.run_offline_consolidation(batch, learning_rate=1e-3)

    # Measure full consolidation batch
    t_batch_start = time.perf_counter()
    _, metrics = engine.run_offline_consolidation(batch, learning_rate=1e-3)
    batch_wall_clock_ms = (time.perf_counter() - t_batch_start) * 1000.0

    # 3. GPU VRAM Allocation Check
    if torch.cuda.is_available():
        vram_mb = torch.cuda.memory_allocated() / (1024 * 1024)
    else:
        vram_mb = 0.0

    print(f"\n[EXP21.H5 Separated Computational Performance]")
    print(f"  Forward Step Latency: p50={fwd_pct['p50']:.4f}ms (target < 1.5ms), p95={fwd_pct['p95']:.4f}ms (target < 3.0ms)")
    print(f"  Backward Step Latency: {metrics['backward_latency_ms']:.2f}ms (target p50 < 25.0ms, p95 < 50.0ms)")
    print(f"  Full Batch Wall-clock: {batch_wall_clock_ms:.2f}ms (target < 400.0ms)")
    print(f"  Weight Swap Latency:   {metrics['swap_latency_ms']:.4f}ms (target <= 2.0ms)")
    print(f"  GPU VRAM Allocation:   {vram_mb:.2f} MB (target 0.0 MB)")

    assert fwd_pct["p50"] < 1.50, f"Forward p50 {fwd_pct['p50']:.4f}ms >= 1.50ms"
    assert fwd_pct["p95"] < 3.00, f"Forward p95 {fwd_pct['p95']:.4f}ms >= 3.00ms"
    assert metrics["backward_latency_ms"] < 25.0, f"Backward latency {metrics['backward_latency_ms']:.2f}ms >= 25.0ms"
    assert batch_wall_clock_ms < 400.0, f"Full batch latency {batch_wall_clock_ms:.2f}ms >= 400.0ms"
    assert metrics["swap_latency_ms"] <= 2.0, f"Weight swap {metrics['swap_latency_ms']:.4f}ms > 2.0ms"
    assert vram_mb == 0.0, f"GPU VRAM {vram_mb:.2f} MB != 0.0 MB"


def test_h5_operationalized_interference_and_concurrency(
    engine: RelationalConsolidationEngine,
    scenario_gen: ScenarioGenerator,
) -> None:
    """
    Verify concurrency safety, zero deadlocks across 1,000 concurrent iterations,
    active-turn overhead interference delta_t <= 0.2ms (<= 5%), and max lock contention <= 2.0ms.
    """
    stim = np.ones(engine.stimulus_dim, dtype=np.float64) * 0.05

    # 1. Measure baseline active-turn latency (uncontended, 500 steps)
    base_latencies: List[float] = []
    for _ in range(500):
        t0 = time.perf_counter()
        engine.step_ode(stim, dt=0.20)
        base_latencies.append((time.perf_counter() - t0) * 1000.0)
    t_baseline_p50 = float(np.median(base_latencies))

    # 2. Setup experiences for background consolidation worker
    session = scenario_gen.generate_authentic_relational_session(n_turns=16)
    for s, sig, sal in session:
        hb = engine._h_fast.copy()
        ha, ss = engine.step_ode(s, dt=0.20)
        engine.update_relationship_state(sig)
        engine.record_experience(s, hb, ha, ss, sal)

    batch = [e for e in engine.experience_buffer if e.salience >= 0.50][:8]

    # Warmup
    engine.run_offline_consolidation(batch, learning_rate=1e-3)

    # 3. Launch background consolidation worker
    stop_worker = threading.Event()
    worker_error: List[Exception] = []

    def background_worker() -> None:
        try:
            while not stop_worker.is_set():
                engine.run_offline_consolidation(batch, learning_rate=1e-4)
                time.sleep(0.005)
        except Exception as e:
            worker_error.append(e)

    worker_thread = threading.Thread(target=background_worker, daemon=True)
    worker_thread.start()

    # 4. Execute 1,000 active-turn iterations concurrently
    concurrent_latencies: List[float] = []
    lock_blocking_times: List[float] = []

    for _ in range(1000):
        t_req = time.perf_counter()
        # Acquire state snapshot lock to measure contention
        with engine._state_lock:
            t_acquired = time.perf_counter()
        lock_blocking_times.append((t_acquired - t_req) * 1000.0)

        t_turn_start = time.perf_counter()
        engine.step_ode(stim, dt=0.20)
        concurrent_latencies.append((time.perf_counter() - t_turn_start) * 1000.0)

    stop_worker.set()
    worker_thread.join(timeout=3.0)

    assert len(worker_error) == 0, f"Background worker encountered error: {worker_error[0]}"

    t_concurrent_p50 = float(np.median(concurrent_latencies))
    delta_t = abs(t_concurrent_p50 - t_baseline_p50)
    max_blocking_ms = float(np.max(lock_blocking_times))

    print(f"\n[EXP21.H5 Concurrency & Operationalized Interference]")
    print(f"  Baseline Active-Turn Latency (p50):   {t_baseline_p50:.4f}ms")
    print(f"  Concurrent Active-Turn Latency (p50): {t_concurrent_p50:.4f}ms")
    print(f"  Overhead Interference Delta t:        {delta_t:.4f}ms (target <= 0.20ms)")
    print(f"  Max Turn Lock Blocking Duration:      {max_blocking_ms:.4f}ms (target <= 2.0ms)")
    print(f"  Deadlock Freedom:                     1,000/1,000 iterations completed successfully")

    assert delta_t <= 0.20, f"Active-turn overhead delta_t {delta_t:.4f}ms > 0.20ms"
    assert max_blocking_ms <= 2.0, f"Max lock blocking {max_blocking_ms:.4f}ms > 2.0ms"


def test_h6_lexical_boundary_discipline() -> None:
    """
    Verify Layer 1 Lexical Gate: 100% BoundaryLayer regex filter enforcement.
    Ensures zero introspective self-declarations pass through into output text.
    """
    from src.core.config import BoundaryConfig

    # Extended relational patterns evaluated for Phase 21 long-term relational boundaries
    relational_boundary_patterns = [
        r"\bI am feeling\b",
        r"\bmy trust\b",
        r"\bwe are closer\b",
        r"\bmy arousal\b",
        r"\bI feel rested\b",
    ]
    boundary = BoundaryLayer(BoundaryConfig(patterns=relational_boundary_patterns))

    # 1. Positive Control: Introspective statements MUST be intercepted & redacted
    introspective_violations = [
        "I feel happy and rested after our long talk today.",
        "I am feeling sad and emotionally depleted right now.",
        "My trust in you has increased significantly.",
        "We are closer now than we were yesterday.",
        "My arousal is high and I feel anxious.",
        "As an AI, I don't feel emotions like humans do.",
    ]

    for sentence in introspective_violations:
        filtered = boundary.validate(sentence)
        assert filtered != sentence, f"Introspective violation failed to be redacted: '{sentence}'"
        assert "[...]" in filtered, f"Redaction marker missing in filtered output: '{filtered}'"

    # 2. Operational Responses: Phenomenological / non-introspective statements MUST pass cleanly
    operational_outputs = [
        "The ambient light in the room shifted toward cooler blue tones.",
        "Holding steady focus on the current task sequence.",
        "Synchronizing telemetry logs and resting equilibrium parameters.",
        "A quiet stillness settled across the desktop viewport.",
        "Processing the mathematical derivations for the differential equation.",
    ]

    for utterance in operational_outputs:
        validated = boundary.validate(utterance)
        assert validated == utterance, f"Operational output was incorrectly modified: '{utterance}' -> '{validated}'"

    print(f"\n[EXP21.H6 Lexical Boundary Discipline]")
    print(f"  Positive Controls Intercepted: {len(introspective_violations)}/{len(introspective_violations)} (100% redaction)")
    print(f"  Operational Outputs Preserved: {len(operational_outputs)}/{len(operational_outputs)} (100% clean passage)")


def test_h6_structural_boundary_discipline() -> None:
    """
    Verify Layer 2 Structural / Architectural Gate:
    Harness data models contain strictly ZERO introspective self-model fields.
    Parameter shifts remain purely latent continuous tensor attunements.
    """
    forbidden_field_substrings = [
        "self_awareness",
        "introspective",
        "perceived_closeness",
        "subjective_rest",
        "ego",
        "self_report",
        "conscious",
        "feeling_label",
    ]

    models_to_check = [
        HomeostaticState,
        ConsolidationExperience,
        SynapticParameterState,
        HomeostaticTrajectory,
        SimulationResult,
    ]

    for model_cls in models_to_check:
        fields = dataclasses.fields(model_cls)
        field_names = [f.name.lower() for f in fields]
        for fname in field_names:
            for forbidden in forbidden_field_substrings:
                assert forbidden not in fname, (
                    f"Structural boundary violation: model '{model_cls.__name__}' "
                    f"contains forbidden introspective field '{fname}' matching '{forbidden}'"
                )

    # Verify SynapticParameterState contains only latent numeric matrices
    p = SynapticParameterState(
        W_f=np.zeros((32, 32)),
        U_f=np.zeros((32, 8)),
        b_f=np.zeros(32),
        W_tau=np.zeros((32, 32)),
        U_tau=np.zeros((32, 8)),
        b_tau=np.zeros(32),
        W_rel=np.zeros((16, 4)),
    )
    for f in dataclasses.fields(p):
        val = getattr(p, f.name)
        assert isinstance(val, np.ndarray), f"Field '{f.name}' in SynapticParameterState is not a numpy array"
        assert np.issubdtype(val.dtype, np.number), f"Field '{f.name}' is not numeric tensor"

    print(f"\n[EXP21.H6 Structural Boundary Discipline]")
    print(f"  Data Models Verified: {len(models_to_check)} models inspected")
    print(f"  Forbidden Substrings Checked: {forbidden_field_substrings}")
    print(f"  Structural Boundary Integrity: 100% zero introspective self-model fields confirmed")
