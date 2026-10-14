"""
Benchmark runner orchestrating cold-start, warm, sustained, and CPU-co-load experiments.
Saves raw telemetry and semantic evaluations to JSONL results.
"""

from __future__ import annotations

import json
import logging
import os
import random
import time
from dataclasses import asdict
from pathlib import Path
from typing import Any, Dict, List, Optional

from tests.evaluation.language_realization.cpu_gpu_slm.harness.adapter import (
    IsolatedSLMAdapter,
    RealizationResult,
)
from tests.evaluation.language_realization.cpu_gpu_slm.harness.co_load import (
    CPUCoLoadWorker,
)
from tests.evaluation.language_realization.cpu_gpu_slm.harness.evaluator import (
    SemanticEvaluationReport,
    SemanticFidelityEvaluator,
)

logger = logging.getLogger(__name__)


class BenchmarkRunner:
    """Orchestrates all experimental benchmark protocols."""

    def __init__(
        self,
        model_path: str = "models/LFM2.5-1.2B-Instruct-Q4_K_M.gguf",
        fixtures_path: str = "tests/evaluation/language_realization/cpu_gpu_slm/fixtures/semantic_fixtures.json",
        output_dir: str = "tests/evaluation/language_realization/cpu_gpu_slm/results",
    ) -> None:
        self.model_path = model_path
        self.fixtures_path = Path(fixtures_path)
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
        self.evaluator = SemanticFidelityEvaluator()

        with open(self.fixtures_path, "r", encoding="utf-8") as f:
            self.fixtures: List[Dict[str, Any]] = json.load(f)

        self.results_file = self.output_dir / "raw_observations.jsonl"

    def _append_observation(self, observation: Dict[str, Any]) -> None:
        with open(self.results_file, "a", encoding="utf-8") as f:
            f.write(json.dumps(observation, ensure_ascii=False) + "\n")

    def run_cold_protocol(self) -> Dict[str, Any]:
        """Runs cold-start measurement on CPU and GPU."""
        logger.info("Executing Cold Start Benchmark Protocol...")
        cold_data: Dict[str, Any] = {}

        for device in ("cpu", "gpu"):
            t0 = time.perf_counter()
            adapter = IsolatedSLMAdapter(model_path=self.model_path, device=device)
            load_ms = adapter.load_duration_ms

            # First realization
            first_fixture = self.fixtures[0]
            res = adapter.realize(first_fixture, max_tokens=64)
            eval_report = self.evaluator.evaluate(first_fixture, res.realized_text, device)
            adapter.shutdown()

            obs = {
                "experiment": "cold_start",
                "device": device,
                "fixture_id": first_fixture["id"],
                "model_load_ms": load_ms,
                "ttft_ms": res.ttft_ms,
                "total_latency_ms": res.total_latency_ms,
                "tokens_generated": res.tokens_generated,
                "success": res.success,
                "realized_text": res.realized_text,
                "semantic_eval": eval_report.to_dict(),
                "telemetry": res.telemetry_summary,
                "timestamp": time.time(),
            }
            self._append_observation(obs)
            cold_data[device] = obs

        return cold_data

    def run_warm_protocol(self, iterations_per_fixture: int = 1) -> List[Dict[str, Any]]:
        """Runs warm benchmark across all fixtures on CPU and GPU with batch size 1."""
        logger.info("Executing Warm Benchmark Protocol...")
        warm_observations: List[Dict[str, Any]] = []

        for device in ("cpu", "gpu"):
            logger.info("Initializing %s adapter for warm benchmark...", device.upper())
            adapter = IsolatedSLMAdapter(model_path=self.model_path, device=device)

            # Warmup runs (2 requests)
            logger.info("Running warm-up sequence for %s...", device)
            for w in range(2):
                adapter.realize(self.fixtures[0], max_tokens=16)

            # Iterate through all fixtures
            for fixture in self.fixtures:
                for it in range(iterations_per_fixture):
                    res = adapter.realize(fixture, max_tokens=96)
                    eval_report = self.evaluator.evaluate(fixture, res.realized_text, device)

                    obs = {
                        "experiment": "warm_paired",
                        "device": device,
                        "fixture_id": fixture["id"],
                        "target_language": fixture["target_language"],
                        "act": fixture["act"],
                        "iteration": it,
                        "ttft_ms": res.ttft_ms,
                        "decode_ms": res.decode_ms,
                        "total_latency_ms": res.total_latency_ms,
                        "tokens_generated": res.tokens_generated,
                        "tokens_per_sec_decode": res.tokens_per_sec_decode,
                        "tokens_per_sec_total": res.tokens_per_sec_total,
                        "realized_text": res.realized_text,
                        "success": res.success,
                        "error": res.error,
                        "semantic_eval": eval_report.to_dict(),
                        "telemetry": res.telemetry_summary,
                        "timestamp": time.time(),
                    }
                    self._append_observation(obs)
                    warm_observations.append(obs)

            adapter.shutdown()

        return warm_observations

    def run_cpu_coload_protocol(self, sample_size: int = 6) -> List[Dict[str, Any]]:
        """Measures CPU performance under simulated background cognitive co-load."""
        logger.info("Executing CPU Co-Load Contention Protocol...")
        observations: List[Dict[str, Any]] = []

        adapter = IsolatedSLMAdapter(model_path=self.model_path, device="cpu")
        co_worker = CPUCoLoadWorker(thread_count=2, load_fraction=0.85)

        # Warmup
        adapter.realize(self.fixtures[0], max_tokens=16)

        try:
            co_worker.start()
            test_subset = self.fixtures[:sample_size]

            for fixture in test_subset:
                res = adapter.realize(fixture, max_tokens=96)
                eval_report = self.evaluator.evaluate(fixture, res.realized_text, "cpu")

                obs = {
                    "experiment": "cpu_coload_contention",
                    "device": "cpu_coload",
                    "fixture_id": fixture["id"],
                    "target_language": fixture["target_language"],
                    "act": fixture["act"],
                    "ttft_ms": res.ttft_ms,
                    "decode_ms": res.decode_ms,
                    "total_latency_ms": res.total_latency_ms,
                    "tokens_generated": res.tokens_generated,
                    "tokens_per_sec_decode": res.tokens_per_sec_decode,
                    "tokens_per_sec_total": res.tokens_per_sec_total,
                    "realized_text": res.realized_text,
                    "success": res.success,
                    "semantic_eval": eval_report.to_dict(),
                    "telemetry": res.telemetry_summary,
                    "timestamp": time.time(),
                }
                self._append_observation(obs)
                observations.append(obs)
        finally:
            co_worker.stop()
            adapter.shutdown()

        return observations

    def run_sustained_protocol(self, request_count: int = 60) -> List[Dict[str, Any]]:
        """Runs 50–100 sustained consecutive requests per device to test stability, thermal drift, and memory growth."""
        logger.info("Executing Sustained Interaction Protocol (%d requests per device)...", request_count)
        observations: List[Dict[str, Any]] = []

        fixture_cycle = self.fixtures * ((request_count // len(self.fixtures)) + 1)

        for device in ("cpu", "gpu"):
            logger.info("Starting sustained run on %s...", device.upper())
            adapter = IsolatedSLMAdapter(model_path=self.model_path, device=device)

            for req_idx in range(request_count):
                fixture = fixture_cycle[req_idx]
                res = adapter.realize(fixture, max_tokens=64)
                eval_report = self.evaluator.evaluate(fixture, res.realized_text, device)

                obs = {
                    "experiment": "sustained_stability",
                    "device": device,
                    "request_index": req_idx,
                    "fixture_id": fixture["id"],
                    "target_language": fixture["target_language"],
                    "ttft_ms": res.ttft_ms,
                    "decode_ms": res.decode_ms,
                    "total_latency_ms": res.total_latency_ms,
                    "tokens_generated": res.tokens_generated,
                    "tokens_per_sec_decode": res.tokens_per_sec_decode,
                    "realized_text": res.realized_text,
                    "success": res.success,
                    "semantic_eval": eval_report.to_dict(),
                    "telemetry": res.telemetry_summary,
                    "timestamp": time.time(),
                }
                self._append_observation(obs)
                observations.append(obs)

            adapter.shutdown()

        return observations
