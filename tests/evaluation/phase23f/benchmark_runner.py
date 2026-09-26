"""
tests/evaluation/phase23f/benchmark_runner.py

Empirical CPU Benchmark Runner for Phase 23-F Language Adapter Boundary.
Measures:
1. Ingress / Egress Gate evaluation latency (microseconds).
2. Parsing latency across EN, VI, and JA.
3. Realization latency across EN, VI, and JA.
4. End-to-end boundary round-trip latency (Parse -> Fortify -> Realize).
5. Isolated Peak RAM consumption (via tracemalloc).

All numbers are measured directly from execution; no fabricated or hypothetical values.
"""

from __future__ import annotations

import gc
import json
import logging
import os
import platform
import statistics
import time
import tracemalloc
from pathlib import Path
from typing import Any, Dict, List

from src.core.knowledge.fortification import ConservativeSemanticFortifier
from src.core.language.adapter import (
    LanguageDriverRegistry,
    LanguageEgressGate,
    LanguageIngressGate,
)

logger = logging.getLogger(__name__)


def run_latency_trials(func, iterations: int = 100) -> Dict[str, float]:
    """Execute function iterations times without tracemalloc for accurate CPU timing."""
    # Warmup
    for _ in range(10):
        func()

    timings_ms: List[float] = []
    for _ in range(iterations):
        t0 = time.perf_counter()
        func()
        t1 = time.perf_counter()
        timings_ms.append((t1 - t0) * 1000.0)

    timings_ms.sort()
    return {
        "median_ms": round(statistics.median(timings_ms), 4),
        "mean_ms": round(statistics.mean(timings_ms), 4),
        "p95_ms": round(timings_ms[int(iterations * 0.95)], 4),
        "min_ms": round(min(timings_ms), 4),
        "max_ms": round(max(timings_ms), 4),
        "trials": iterations,
    }


def measure_peak_ram(func) -> float:
    """Measure peak additional RAM in MB using isolated tracemalloc."""
    gc.collect()
    tracemalloc.start()
    tracemalloc.reset_peak()
    
    func()
    
    current, peak = tracemalloc.get_traced_memory()
    tracemalloc.stop()
    gc.collect()
    return round(peak / (1024.0 * 1024.0), 6)


def run_full_benchmark(output_dir: Path) -> Dict[str, Any]:
    """Run comprehensive benchmark across all Phase 23-F components."""
    registry = LanguageDriverRegistry.create_default_registry()
    ingress_gate = LanguageIngressGate()
    egress_gate = LanguageEgressGate()
    fortifier = ConservativeSemanticFortifier()

    en_text = "User solves the problem"
    vi_text = "Anh người dùng giải quyết cái vấn đề"
    ja_text = "ユーザーが問題を解決した"

    # Pre-parse graphs for realization benchmark
    graph_en = ingress_gate.admit_and_parse(en_text, "en", registry).graph
    graph_vi = ingress_gate.admit_and_parse(vi_text, "vi", registry).graph
    graph_ja = ingress_gate.admit_and_parse(ja_text, "ja", registry).graph

    # 1. Gate Latency Benchmarks
    gate_admit_fn = lambda: ingress_gate.evaluate_language("en")
    gate_reject_fn = lambda: ingress_gate.evaluate_language("fr")
    egress_gate_fn = lambda: egress_gate.evaluate_target_language("vi")

    ingress_admit_perf = run_latency_trials(gate_admit_fn, iterations=200)
    ingress_reject_perf = run_latency_trials(gate_reject_fn, iterations=200)
    egress_perf = run_latency_trials(egress_gate_fn, iterations=200)

    # 2. Parse Latency Benchmarks
    parse_en_fn = lambda: ingress_gate.admit_and_parse(en_text, "en", registry)
    parse_vi_fn = lambda: ingress_gate.admit_and_parse(vi_text, "vi", registry)
    parse_ja_fn = lambda: ingress_gate.admit_and_parse(ja_text, "ja", registry)

    parse_en_perf = run_latency_trials(parse_en_fn, iterations=100)
    parse_vi_perf = run_latency_trials(parse_vi_fn, iterations=100)
    parse_ja_perf = run_latency_trials(parse_ja_fn, iterations=100)

    # 3. Realization Latency Benchmarks
    realize_en_fn = lambda: egress_gate.admit_and_realize(graph_en, "en", registry)
    realize_vi_fn = lambda: egress_gate.admit_and_realize(graph_vi, "vi", registry)
    realize_ja_fn = lambda: egress_gate.admit_and_realize(graph_ja, "ja", registry)

    realize_en_perf = run_latency_trials(realize_en_fn, iterations=100)
    realize_vi_perf = run_latency_trials(realize_vi_fn, iterations=100)
    realize_ja_perf = run_latency_trials(realize_ja_fn, iterations=100)

    # 4. End-to-End Round-Trip Benchmark (Parse -> Fortify -> Realize)
    def round_trip_en_to_vi():
        res = ingress_gate.admit_and_parse(en_text, "en", registry)
        f_graph, _ = fortifier.fortify_session(res.graph)
        return egress_gate.admit_and_realize(f_graph, "vi", registry)

    def round_trip_ja_to_en():
        res = ingress_gate.admit_and_parse(ja_text, "ja", registry)
        f_graph, _ = fortifier.fortify_session(res.graph)
        return egress_gate.admit_and_realize(f_graph, "en", registry)

    round_trip_en_vi_perf = run_latency_trials(round_trip_en_to_vi, iterations=50)
    round_trip_ja_en_perf = run_latency_trials(round_trip_ja_to_en, iterations=50)

    # 5. RAM Measurements
    ram_ingress = measure_peak_ram(lambda: [ingress_gate.evaluate_language("en") for _ in range(50)])
    ram_parse_en = measure_peak_ram(lambda: [ingress_gate.admit_and_parse(en_text, "en", registry) for _ in range(20)])
    ram_parse_vi = measure_peak_ram(lambda: [ingress_gate.admit_and_parse(vi_text, "vi", registry) for _ in range(20)])
    ram_parse_ja = measure_peak_ram(lambda: [ingress_gate.admit_and_parse(ja_text, "ja", registry) for _ in range(20)])
    ram_realize = measure_peak_ram(lambda: [egress_gate.admit_and_realize(graph_en, "vi", registry) for _ in range(20)])
    ram_round_trip = measure_peak_ram(round_trip_en_to_vi)

    results = {
        "benchmark_timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
        "hardware": {
            "platform": platform.platform(),
            "processor": platform.processor(),
            "python_version": platform.python_version(),
            "vram_mb": 0.0,
        },
        "gates": {
            "ingress_admitted_latency": ingress_admit_perf,
            "ingress_rejected_latency": ingress_reject_perf,
            "egress_latency": egress_perf,
            "peak_ram_mb": ram_ingress,
        },
        "parsing": {
            "english": parse_en_perf,
            "vietnamese": parse_vi_perf,
            "japanese": parse_ja_perf,
            "peak_ram_mb": {
                "en": ram_parse_en,
                "vi": ram_parse_vi,
                "ja": ram_parse_ja,
            },
        },
        "realization": {
            "english": realize_en_perf,
            "vietnamese": realize_vi_perf,
            "japanese": realize_ja_perf,
            "peak_ram_mb": ram_realize,
        },
        "round_trip_end_to_end": {
            "en_to_vi": round_trip_en_vi_perf,
            "ja_to_en": round_trip_ja_en_perf,
            "peak_ram_mb": ram_round_trip,
        },
    }

    # Save to JSON
    output_dir.mkdir(parents=True, exist_ok=True)
    json_path = output_dir / "benchmark_results.json"
    with open(json_path, "w", encoding="utf-8") as f:
        json.dump(results, f, indent=2)

    logger.info("Saved benchmark results to %s", json_path)
    return results


if __name__ == "__main__":
    output_dir = Path("evaluation_artifacts/phase23f")
    results = run_full_benchmark(output_dir)
    print("\n=== Phase 23-F Measured Benchmark Summary ===")
    print(f"Ingress Gate Latency (Admit): {results['gates']['ingress_admitted_latency']['median_ms'] * 1000.0:.2f} µs")
    print(f"Ingress Gate Latency (Reject): {results['gates']['ingress_rejected_latency']['median_ms'] * 1000.0:.2f} µs")
    print(f"Parse Latency (EN): {results['parsing']['english']['median_ms']:.4f} ms")
    print(f"Parse Latency (VI): {results['parsing']['vietnamese']['median_ms']:.4f} ms")
    print(f"Parse Latency (JA): {results['parsing']['japanese']['median_ms']:.4f} ms")
    print(f"Realize Latency (VI): {results['realization']['vietnamese']['median_ms']:.4f} ms")
    print(f"Round-Trip Latency (EN->Fortify->VI): {results['round_trip_end_to_end']['en_to_vi']['median_ms']:.4f} ms")
    print(f"Peak RAM (Round-Trip): {results['round_trip_end_to_end']['peak_ram_mb']:.4f} MB")
    print(f"GPU VRAM: {results['hardware']['vram_mb']:.1f} MB")
