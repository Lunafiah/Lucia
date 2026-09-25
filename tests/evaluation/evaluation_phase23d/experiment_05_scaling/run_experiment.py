"""Execution Runner for EXP-05: Scaling & Hardware Feasibility.

Executes benchmark across:
- Scales: N in [1k, 5k, 10k, 25k, 50k, 100k]
- Candidates: UMR-TPG, V-UMR, DRS-Graph
- Measurements: Build latency, 1-hop lookup (p50, p95, p99), 3-hop traversal,
  belief revision, heap and OS RSS memory, bytes/fact, and SLA gates.
Exports results to raw_results.json and summary.md.
"""

from __future__ import annotations

import gc
import json
import os
import sys
import time
import tracemalloc
from pathlib import Path
from typing import Any, Dict, List, Type

# Add project root to sys.path if run directly
project_root = Path(__file__).resolve().parents[4]
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

from tests.evaluation.evaluation_phase23d.experiment_05_scaling.dataset.generator import (
    generate_scaling_facts,
)
from tests.evaluation.evaluation_phase23d.experiment_05_scaling.metrics import (
    compute_percentiles,
    evaluate_sla_gates,
    get_os_memory_mb,
)
from tests.evaluation.evaluation_phase23d.experiment_05_scaling.models.drs_scaling_store import (
    DRSScalingStore,
)
from tests.evaluation.evaluation_phase23d.experiment_05_scaling.models.umr_scaling_store import (
    UMRScalingStore,
)
from tests.evaluation.evaluation_phase23d.experiment_05_scaling.models.vumr_scaling_store import (
    VUMRScalingStore,
)


SCALING_POINTS = [1000, 5000, 10000, 25000, 50000, 100000]

CANDIDATES: Dict[str, Type[Any]] = {
    "UMR-TPG": UMRScalingStore,
    "V-UMR": VUMRScalingStore,
    "DRS-Graph": DRSScalingStore,
}


def evaluate_candidate_at_scale(
    candidate_name: str,
    store_cls: Type[Any],
    facts: List[Dict[str, Any]],
    probes: Dict[str, Any],
) -> Dict[str, Any]:
    """Evaluates a single candidate at a specific fact scale N."""
    gc.collect()
    tracemalloc.start()
    base_ws_mb, base_priv_mb = get_os_memory_mb()

    store = store_cls()

    # 1. Measure Build / Insertion Latency
    t0 = time.perf_counter()
    for fact in facts:
        store.insert_fact(fact)
    t1 = time.perf_counter()
    build_sec = t1 - t0
    throughput_ops = len(facts) / max(1e-6, build_sec)

    # 2. Measure Memory
    post_ws_mb, post_priv_mb = get_os_memory_mb()
    heap_cur_bytes, heap_peak_bytes = tracemalloc.get_traced_memory()
    tracemalloc.stop()

    incremental_ws_mb = max(0.0, post_ws_mb - base_ws_mb)
    heap_mb = heap_cur_bytes / (1024.0 * 1024.0)
    bytes_per_fact = (heap_cur_bytes) / len(facts)

    # 3. Measure 1-Hop Lookup Latency
    lookup_samples_ms: List[float] = []
    for probe in probes["lookup_1hop"]:
        lt0 = time.perf_counter()
        results = store.lookup_1hop(probe["subject"], probe["predicate"])
        lt1 = time.perf_counter()
        lookup_samples_ms.append((lt1 - lt0) * 1000.0)
    lookup_stats = compute_percentiles(lookup_samples_ms)

    # 4. Measure 3-Hop Traversal Latency
    traversal_samples_ms: List[float] = []
    for probe in probes["traversal_3hop"]:
        tt0 = time.perf_counter()
        results = store.traverse_3hop(probe["start_entity"])
        tt1 = time.perf_counter()
        traversal_samples_ms.append((tt1 - tt0) * 1000.0)
    traversal_stats = compute_percentiles(traversal_samples_ms)

    # 5. Measure Belief Revision Latency
    revision_samples_ms: List[float] = []
    for probe in probes["revision"]:
        rt0 = time.perf_counter()
        rev_res = store.revise_belief(probe["contradicting_fact"])
        rt1 = time.perf_counter()
        revision_samples_ms.append((rt1 - rt0) * 1000.0)
    revision_stats = compute_percentiles(revision_samples_ms)

    # 6. Evaluate SLA Gates
    sla_result = evaluate_sla_gates(
        candidate=candidate_name,
        n_facts=len(facts),
        total_rss_mb=post_ws_mb,
        lookup_p95_ms=lookup_stats["p95"],
        revision_p95_ms=revision_stats["p95"],
        vram_mb=0.0,
    )

    del store
    gc.collect()

    return {
        "candidate": candidate_name,
        "n_facts": len(facts),
        "build_time_sec": round(build_sec, 4),
        "throughput_ops_per_sec": round(throughput_ops, 1),
        "memory": {
            "base_working_set_mb": base_ws_mb,
            "post_working_set_mb": post_ws_mb,
            "incremental_working_set_mb": round(incremental_ws_mb, 2),
            "heap_mb": round(heap_mb, 2),
            "bytes_per_fact": round(bytes_per_fact, 1),
        },
        "lookup_1hop_ms": lookup_stats,
        "traversal_3hop_ms": traversal_stats,
        "revision_ms": revision_stats,
        "sla_gates": sla_result,
    }


def run_scaling_benchmark(
    scaling_points: List[int] = SCALING_POINTS,
    seed: int = 42,
    output_dir: Path | None = None,
) -> Dict[str, Any]:
    """Runs the complete EXP-05 scaling suite across all candidate architectures."""
    benchmark_results: Dict[str, Any] = {
        "benchmark": "Phase23D_EXP05_Scaling_Hardware_Feasibility",
        "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
        "hardware_profile": {
            "target_envelope": "20-Watt CPU",
            "vram_allocation": "0.0 MB (Strict CPU Execution)",
            "tdp_measurement": "UNVERIFIED (hardware power meter absent in environment)",
            "platform": sys.platform,
        },
        "scaling_points": scaling_points,
        "candidates": {},
    }

    print(f"Starting EXP-05 Benchmark across {len(scaling_points)} scales: {scaling_points}")

    for cand_name, store_cls in CANDIDATES.items():
        print(f"\n--- Evaluating Candidate: {cand_name} ---")
        cand_results = []
        for n in scaling_points:
            print(f"  Generating dataset for N={n}...")
            facts, probes = generate_scaling_facts(n_facts=n, seed=seed)
            print(f"  Benchmarking {cand_name} at N={n}...")
            res = evaluate_candidate_at_scale(cand_name, store_cls, facts, probes)
            cand_results.append(res)
            print(
                f"    N={n:<6} | Heap: {res['memory']['heap_mb']:>6.2f}MB | "
                f"1-Hop p95: {res['lookup_1hop_ms']['p95']:>5.3f}ms | "
                f"Rev p95: {res['revision_ms']['p95']:>5.3f}ms | "
                f"SLA: {'PASS' if res['sla_gates']['overall_sla_passed'] else 'FAIL'}"
            )

        # Compute scaling metrics (1k -> 100k)
        res_1k = cand_results[0]
        res_100k = cand_results[-1]

        mem_ratio = (
            res_100k["memory"]["heap_mb"] / max(0.01, res_1k["memory"]["heap_mb"])
        )
        lat_ratio = (
            res_100k["lookup_1hop_ms"]["p95"] / max(0.0001, res_1k["lookup_1hop_ms"]["p95"])
        )

        all_sla_passed = all(r["sla_gates"]["overall_sla_passed"] for r in cand_results)

        benchmark_results["candidates"][cand_name] = {
            "scaling_results": cand_results,
            "scaling_analysis_1k_to_100k": {
                "memory_growth_ratio": round(mem_ratio, 2),
                "lookup_latency_growth_ratio": round(lat_ratio, 2),
                "heap_100k_mb": res_100k["memory"]["heap_mb"],
                "rss_100k_mb": res_100k["memory"]["post_working_set_mb"],
                "bytes_per_fact_100k": res_100k["memory"]["bytes_per_fact"],
                "lookup_p95_100k_ms": res_100k["lookup_1hop_ms"]["p95"],
                "revision_p95_100k_ms": res_100k["revision_ms"]["p95"],
            },
            "overall_verdict": "PASS" if all_sla_passed else "FAIL",
        }

    # Save artifacts
    if output_dir is not None:
        output_dir.mkdir(parents=True, exist_ok=True)
        json_file = output_dir / "raw_results.json"
        with open(json_file, "w", encoding="utf-8") as f:
            json.dump(benchmark_results, f, indent=2)

        # Generate markdown summary
        md_file = output_dir / "summary.md"
        with open(md_file, "w", encoding="utf-8") as f:
            f.write(_generate_summary_markdown(benchmark_results))

    return benchmark_results


def _generate_summary_markdown(results: Dict[str, Any]) -> str:
    lines = [
        "# EXP-05: Scaling & Hardware Feasibility Summary Table",
        "",
        f"> **Generated:** {results['timestamp']}  ",
        f"> **Hardware Envelope:** {results['hardware_profile']['target_envelope']}  ",
        f"> **VRAM Impact:** {results['hardware_profile']['vram_allocation']}  ",
        f"> **TDP Status:** `{results['hardware_profile']['tdp_measurement']}`  ",
        "",
        "---",
        "",
        "## 1. 100k Horizon Scaling Overview",
        "",
        "| Candidate | Verdict | Heap at 100k (MB) | WorkingSet at 100k (MB) | Bytes/Fact | Lookup p95 (ms) | Traversal p95 (ms) | Revision p95 (ms) |",
        "|---|---|---|---|---|---|---|---|",
    ]

    for cand_name, cand_data in results["candidates"].items():
        analysis = cand_data["scaling_analysis_1k_to_100k"]
        last_res = cand_data["scaling_results"][-1]
        lines.append(
            f"| **{cand_name}** | **`{cand_data['overall_verdict']}`** | "
            f"{analysis['heap_100k_mb']:.1f} MB | {analysis['rss_100k_mb']:.1f} MB | "
            f"{analysis['bytes_per_fact_100k']:.1f} B | {analysis['lookup_p95_100k_ms']:.3f} ms | "
            f"{last_res['traversal_3hop_ms']['p95']:.3f} ms | {analysis['revision_p95_100k_ms']:.3f} ms |"
        )

    lines.extend([
        "",
        "---",
        "",
        "## 2. Scaling Progression by Fact Count (N)",
        "",
        "| Fact Count (N) | Candidate | Heap (MB) | WorkingSet (MB) | 1-Hop Lookup p50 (ms) | 1-Hop Lookup p95 (ms) | Revision p95 (ms) |",
        "|---|---|---|---|---|---|---|",
    ])

    for n_idx, n in enumerate(results["scaling_points"]):
        for cand_name, cand_data in results["candidates"].items():
            r = cand_data["scaling_results"][n_idx]
            lines.append(
                f"| {n:,} | {cand_name} | {r['memory']['heap_mb']:.1f} MB | "
                f"{r['memory']['post_working_set_mb']:.1f} MB | {r['lookup_1hop_ms']['p50']:.4f} ms | "
                f"{r['lookup_1hop_ms']['p95']:.4f} ms | {r['revision_ms']['p95']:.4f} ms |"
            )

    return "\n".join(lines)


if __name__ == "__main__":
    out_dir = Path(__file__).parent / "results"
    run_scaling_benchmark(output_dir=out_dir)
