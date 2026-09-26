"""
tests/evaluation/phase23e/benchmark_runner.py

Empirical Benchmark Runner for Phase 23-E:
Conservative Semantic Fortification Across Session Boundaries.

Measures:
- Consolidation latency (min, median/p50, p95, p99, max) across scale levels.
- Peak additional RAM consumption via tracemalloc.
- Zero-Ingress Property (Fortification-Originated Unsupported Insertion Rate).
- Epistemic Safety Invariant.
- Comparison against TARGET (<=15 MB, <=10 ms) and HARD CEILING (>30 MB, >25 ms).
"""

from __future__ import annotations

import json
import os
import platform
import time
import tracemalloc
from pathlib import Path
from typing import Any, Dict, List, Tuple

import numpy as np

from src.core.knowledge.fortification import (
    AuditStatus,
    ConservativeSemanticFortifier,
    EpistemicState,
    ProvenanceRecord,
    ScopeBoundary,
    ScopeType,
    SemanticEdge,
    SemanticGraph,
    SemanticNode,
)

TARGET_LATENCY_MS: float = 10.0
TARGET_RAM_MB: float = 15.0
HARD_CEILING_LATENCY_MS: float = 25.0
HARD_CEILING_RAM_MB: float = 30.0

ARTIFACTS_DIR = Path("evaluation_artifacts/phase23e")


def generate_synthetic_semantic_graph(
    num_nodes: int,
    num_edges: int,
    inferred_ratio: float = 0.2,
    ambiguous_ratio: float = 0.05,
    unknown_ratio: float = 0.05,
    seed: int = 42,
) -> SemanticGraph:
    """
    Generates an abstract, language-independent semantic graph fixture.
    Purely symbolic: zero natural language strings, zero token dependencies.
    """
    rng = np.random.RandomState(seed)
    graph = SemanticGraph(session_id=f"benchmark_sess_{seed}")

    # Add child scopes
    graph.add_scope(ScopeBoundary("scope:modal_1", ScopeType.MODAL, "scope:root"))
    graph.add_scope(ScopeBoundary("scope:neg_1", ScopeType.NEGATION, "scope:root"))

    scopes = ["scope:root", "scope:modal_1", "scope:neg_1"]

    num_inferred = int(num_nodes * inferred_ratio)
    num_ambig = int(num_nodes * ambiguous_ratio)
    num_unknown = int(num_nodes * unknown_ratio)
    num_facts = num_nodes - (num_inferred + num_ambig + num_unknown)

    # 1. Generate FACT nodes
    fact_ids: List[str] = []
    for i in range(num_facts):
        nid = f"n_fact_{i:05d}"
        fact_ids.append(nid)
        scope = scopes[i % len(scopes)]
        graph.add_node(SemanticNode(
            id=nid,
            epistemic_state=EpistemicState.FACT,
            concept_symbol=f"c:sym_{i:05d}",
            scope_id=scope,
            polarity=True,
            attributes={"dim": [float(i % 10), float((i * 3) % 10)]},
        ))

    # 2. Generate INFERRED nodes with valid supporting premises
    inferred_ids: List[str] = []
    for i in range(num_inferred):
        nid = f"n_inf_{i:05d}"
        inferred_ids.append(nid)
        scope = scopes[(num_facts + i) % len(scopes)]
        k = min(len(fact_ids), (i % 3) + 1) if fact_ids else 0
        premises = tuple(fact_ids[j % len(fact_ids)] for j in range(i, i + k)) if k > 0 else ()
        graph.add_node(SemanticNode(
            id=nid,
            epistemic_state=EpistemicState.INFERRED,
            concept_symbol=f"c:inf_sym_{i:05d}",
            scope_id=scope,
            polarity=True,
            provenance=ProvenanceRecord(
                derivation_rule_id=f"rule:r_{i % 10:02d}",
                supporting_premises=premises,
                originating_session_id=graph.session_id,
                originating_turn_id="turn_01",
                timestamp=time.time(),
            ),
        ))

    # 3. Generate AMBIGUOUS nodes
    for i in range(num_ambig):
        nid = f"n_ambig_{i:05d}"
        scope = scopes[(num_facts + num_inferred + i) % len(scopes)]
        graph.add_node(SemanticNode(
            id=nid,
            epistemic_state=EpistemicState.AMBIGUOUS,
            concept_symbol=f"c:amb_sym_{i:05d}",
            scope_id=scope,
            attributes={"candidates": [f"c:cand_{i}_a", f"c:cand_{i}_b"]},
        ))

    # 4. Generate UNKNOWN nodes
    for i in range(num_unknown):
        nid = f"n_unk_{i:05d}"
        scope = scopes[(num_facts + num_inferred + num_ambig + i) % len(scopes)]
        graph.add_node(SemanticNode(
            id=nid,
            epistemic_state=EpistemicState.UNKNOWN,
            concept_symbol="c:sym_unknown",
            scope_id=scope,
        ))

    # 5. Generate intra-scope edges
    edge_roles = [":ARG0", ":ARG1", ":ARG2", ":manner", ":attribute", ":temporal"]
    nodes_by_scope: Dict[str, List[str]] = {}
    for n in graph.nodes.values():
        nodes_by_scope.setdefault(n.scope_id, []).append(n.id)

    edges_added = 0
    attempts = 0
    max_attempts = num_edges * 10

    while edges_added < num_edges and attempts < max_attempts:
        attempts += 1
        s = rng.choice(scopes)
        scope_nodes = nodes_by_scope.get(s, [])
        if len(scope_nodes) < 2:
            continue
        src_id = rng.choice(scope_nodes)
        tgt_id = rng.choice(scope_nodes)
        if src_id == tgt_id:
            continue
        role = rng.choice(edge_roles)
        graph.add_edge(SemanticEdge(source_id=src_id, target_id=tgt_id, relation_role=role))
        edges_added += 1

    return graph


def run_single_scale_benchmark(
    num_nodes: int,
    num_edges: int,
    num_iterations: int = 30,
    seed: int = 42,
) -> Dict[str, Any]:
    """
    Executes benchmark for a given scale configuration.
    Separates pure latency profiling from tracemalloc memory tracing
    to prevent tracemalloc stack-recording overhead from polluting latency SLA measurements.
    """
    fortifier = ConservativeSemanticFortifier()

    # Warmup
    warmup_graph = generate_synthetic_semantic_graph(num_nodes, num_edges, seed=seed)
    fortifier.fortify_session(warmup_graph)

    # 1. Clean Latency Measurement Pass
    latencies_ms: List[float] = []
    for it in range(num_iterations):
        test_graph = generate_synthetic_semantic_graph(num_nodes, num_edges, seed=seed + it)

        # Invariant baseline tracking
        initial_node_ids = set(test_graph.nodes.keys())

        t0 = time.perf_counter()
        fortified_graph, audit = fortifier.fortify_session(test_graph)
        t1 = time.perf_counter()

        iteration_latency_ms = (t1 - t0) * 1000.0
        latencies_ms.append(iteration_latency_ms)

        # Invariant checks:
        assert audit.is_valid is True
        assert fortified_graph.is_frozen is True
        assert fortified_graph.verify_checksum() is True

        # Verify Zero-Ingress Property (Zero novel entity insertion):
        final_node_ids = set(fortified_graph.nodes.keys())
        novel_nodes = final_node_ids - initial_node_ids
        assert len(novel_nodes) == 0, f"Novel nodes inserted: {novel_nodes}"

        # Verify Epistemic Safety Invariant:
        for nid in initial_node_ids:
            init_state = test_graph.get_node(nid).epistemic_state
            final_state = fortified_graph.get_node(nid).epistemic_state
            if init_state == EpistemicState.UNKNOWN:
                assert final_state == EpistemicState.UNKNOWN
            elif init_state == EpistemicState.AMBIGUOUS:
                assert final_state == EpistemicState.AMBIGUOUS

    # 2. Clean Memory Measurement Pass (Isolated tracemalloc)
    tracemalloc.start()
    baseline_mem = tracemalloc.get_traced_memory()[0]

    mem_graph = generate_synthetic_semantic_graph(num_nodes, num_edges, seed=seed + 999)
    fortifier.fortify_session(mem_graph)

    _, peak_mem = tracemalloc.get_traced_memory()
    tracemalloc.stop()

    peak_add_ram_bytes = max(0, peak_mem - baseline_mem)
    peak_ram_mb = peak_add_ram_bytes / (1024.0 * 1024.0)

    p50_latency = float(np.percentile(latencies_ms, 50))
    p95_latency = float(np.percentile(latencies_ms, 95))
    p99_latency = float(np.percentile(latencies_ms, 99))
    min_latency = float(np.min(latencies_ms))
    max_latency = float(np.max(latencies_ms))

    # Evaluate against TARGET and HARD CEILING
    latency_target_met = p50_latency <= TARGET_LATENCY_MS
    latency_ceiling_met = p95_latency <= HARD_CEILING_LATENCY_MS
    ram_target_met = peak_ram_mb <= TARGET_RAM_MB
    ram_ceiling_met = peak_ram_mb <= HARD_CEILING_RAM_MB

    status = "PASS_TARGET" if (latency_target_met and ram_target_met) else (
        "PASS_WITHIN_HARD_CEILING" if (latency_ceiling_met and ram_ceiling_met) else "FAIL_RESOURCE_BUDGET"
    )

    return {
        "num_nodes": num_nodes,
        "num_edges": num_edges,
        "num_iterations": num_iterations,
        "latency_ms": {
            "min": round(min_latency, 4),
            "p50_median": round(p50_latency, 4),
            "p95": round(p95_latency, 4),
            "p99": round(p99_latency, 4),
            "max": round(max_latency, 4),
        },
        "peak_ram_mb": round(peak_ram_mb, 4),
        "target": {
            "latency_ms": TARGET_LATENCY_MS,
            "ram_mb": TARGET_RAM_MB,
        },
        "hard_ceiling": {
            "latency_ms": HARD_CEILING_LATENCY_MS,
            "ram_mb": HARD_CEILING_RAM_MB,
        },
        "gates": {
            "latency_target_met": latency_target_met,
            "ram_target_met": ram_target_met,
            "latency_ceiling_met": latency_ceiling_met,
            "ram_ceiling_met": ram_ceiling_met,
        },
        "invariants": {
            "fortification_originated_unsupported_insertion_rate": 0.0,
            "epistemic_safety_invariant_satisfied": True,
            "structural_checksum_verified": True,
        },
        "status": status,
    }


def run_full_benchmark_suite() -> Dict[str, Any]:
    """
    Runs the complete multi-scale benchmark suite.
    """
    ARTIFACTS_DIR.mkdir(parents=True, exist_ok=True)

    scales = [
        {"name": "Small (Session Dialog)", "nodes": 20, "edges": 30, "iterations": 40},
        {"name": "Medium (Extended Session)", "nodes": 100, "edges": 150, "iterations": 30},
        {"name": "Large (Multi-Session Consolidation)", "nodes": 500, "edges": 800, "iterations": 20},
        {"name": "Stress (High-Density Graph)", "nodes": 1000, "edges": 2000, "iterations": 10},
    ]

    hardware_info = {
        "platform": platform.platform(),
        "processor": platform.processor(),
        "python_version": platform.python_version(),
        "machine": platform.machine(),
    }

    results: Dict[str, Any] = {
        "benchmark": "Phase 23-E Conservative Semantic Fortification Across Session Boundaries",
        "timestamp": time.time(),
        "hardware": hardware_info,
        "scales": {},
    }

    print("\n" + "=" * 70)
    print("PHASE 23-E CONSERVATIVE SEMANTIC FORTIFICATION BENCHMARK")
    print(f"Platform: {hardware_info['platform']} | Python: {hardware_info['python_version']}")
    print(f"Target: <= {TARGET_RAM_MB} MB RAM, <= {TARGET_LATENCY_MS} ms Latency")
    print(f"Hard Ceiling: <= {HARD_CEILING_RAM_MB} MB RAM, <= {HARD_CEILING_LATENCY_MS} ms Latency")
    print("=" * 70)

    for scale in scales:
        scale_name = scale["name"]
        print(f"\nEvaluating {scale_name} ({scale['nodes']} nodes, {scale['edges']} edges)...")
        scale_res = run_single_scale_benchmark(
            num_nodes=scale["nodes"],
            num_edges=scale["edges"],
            num_iterations=scale["iterations"],
        )
        results["scales"][scale_name] = scale_res

        lat = scale_res["latency_ms"]
        print(f"  -> Median Latency: {lat['p50_median']} ms (p95: {lat['p95']} ms, max: {lat['max']} ms)")
        print(f"  -> Peak Add. RAM:  {scale_res['peak_ram_mb']} MB")
        print(f"  -> Status:         {scale_res['status']}")

    # Save to JSON
    output_path = ARTIFACTS_DIR / "benchmark_results.json"
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(results, f, indent=2)
    print(f"\n[Artifact] Benchmark results written to {output_path}")

    return results


if __name__ == "__main__":
    run_full_benchmark_suite()
