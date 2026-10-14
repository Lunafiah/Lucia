"""
tests/evaluation/language_realization/cpu_gpu_slm/run_benchmark.py

Main executable driver for the Lucia CPU-SLM vs GPU-SLM Language Realization Benchmark.
"""

from __future__ import annotations

import argparse
import logging
import os
import shutil
import subprocess
import sys
import time
from pathlib import Path

# Ensure UTF-8 output on Windows terminal
if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding="utf-8")
        sys.stderr.reconfigure(encoding="utf-8")
    except Exception:
        pass

PROJECT_ROOT = Path("c:/Users/Lunafiah/Desktop/My_project/Lucia")
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from tests.evaluation.language_realization.cpu_gpu_slm.harness.reporter import BenchmarkReporter
from tests.evaluation.language_realization.cpu_gpu_slm.harness.runner import BenchmarkRunner

logging.basicConfig(
    level=logging.INFO,
    format="[%(asctime)s] %(levelname)s [%(name)s] %(message)s",
    datefmt="%H:%M:%S",
)
logger = logging.getLogger("run_benchmark")


def query_hardware_info() -> dict:
    info = {
        "gpu_name": "UNKNOWN",
        "driver_version": "UNKNOWN",
        "cuda_version": "UNKNOWN",
        "vram_total_mb": 4096,
    }
    if shutil.which("nvidia-smi") is not None:
        try:
            res = subprocess.run(
                ["nvidia-smi", "--query-gpu=name,driver_version,memory.total", "--format=csv,noheader,nounits"],
                capture_output=True,
                text=True,
                timeout=5,
                check=True,
            )
            parts = [p.strip() for p in res.stdout.strip().split(",")]
            if len(parts) >= 3:
                info["gpu_name"] = parts[0]
                info["driver_version"] = parts[1]
                info["vram_total_mb"] = float(parts[2])
            res_full = subprocess.run(["nvidia-smi"], capture_output=True, text=True, timeout=5)
            import re
            m = re.search(r"CUDA Version:\s*([\d\.]+)", res_full.stdout)
            if m:
                info["cuda_version"] = m.group(1)
        except Exception as e:
            logger.warning("Failed querying nvidia-smi: %s", e)
    return info


def main() -> None:
    parser = argparse.ArgumentParser(description="Lucia CPU vs GPU SLM Benchmark Harness")
    parser.add_argument("--quick", action="store_true", help="Run a quick verification smoke benchmark (12 fixtures)")
    parser.add_argument("--cold-only", action="store_true", help="Run only cold-start benchmark")
    parser.add_argument("--warm-only", action="store_true", help="Run only warm-path benchmark")
    parser.add_argument("--sustained-only", action="store_true", help="Run only sustained benchmark")
    parser.add_argument("--sustained-requests", type=int, default=50, help="Number of sustained interaction requests (default: 50)")
    parser.add_argument("--clean-results", action="store_true", help="Clear previous raw results before running")
    args = parser.parse_args()

    results_dir = Path("tests/evaluation/language_realization/cpu_gpu_slm/results")
    reports_dir = Path("tests/evaluation/language_realization/cpu_gpu_slm/reports")
    raw_results_file = results_dir / "raw_observations.jsonl"

    if args.clean_results and raw_results_file.exists():
        raw_results_file.unlink()
        logger.info("Cleared prior results file: %s", raw_results_file)

    runner = BenchmarkRunner(
        model_path="models/LFM2.5-1.2B-Instruct-Q4_K_M.gguf",
        fixtures_path="tests/evaluation/language_realization/cpu_gpu_slm/fixtures/semantic_fixtures.json",
        output_dir=str(results_dir),
    )

    if args.quick:
        # Use a 12-fixture subset covering all 3 languages and minimal pairs
        runner.fixtures = runner.fixtures[:12]
        logger.info("Quick mode enabled: evaluating subset of %d fixtures", len(runner.fixtures))

    hw_info = query_hardware_info()
    logger.info("Hardware detected: %s | Driver: %s | VRAM: %s MiB", hw_info["gpu_name"], hw_info["driver_version"], hw_info["vram_total_mb"])

    # 1. Cold Start
    if not args.warm_only and not args.sustained_only:
        runner.run_cold_protocol()

    # 2. Warm Paired
    if not args.cold_only and not args.sustained_only:
        runner.run_warm_protocol(iterations_per_fixture=1)
        runner.run_cpu_coload_protocol(sample_size=6 if not args.quick else 3)

    # 3. Sustained Interaction
    if not args.cold_only and not args.warm_only:
        sustained_count = 20 if args.quick else args.sustained_requests
        runner.run_sustained_protocol(request_count=sustained_count)

    # 4. Generate Manifest and Report
    logger.info("Synthesizing statistics and generating benchmark manifest and report...")
    reporter = BenchmarkReporter(
        results_file=str(raw_results_file),
        manifest_file=str(reports_dir / "manifest.json"),
        report_file=str(reports_dir / "BENCHMARK_REPORT.md"),
    )
    reporter.build_manifest(hw_info)
    report_text = reporter.generate_report(hw_info)

    # Mirror report into docs/others/cpu_gpu_slm_benchmark/ for canonical non-phase documentation compliance
    docs_dir = Path("docs/others/cpu_gpu_slm_benchmark")
    docs_dir.mkdir(parents=True, exist_ok=True)
    with open(docs_dir / "BENCHMARK_REPORT.md", "w", encoding="utf-8") as f:
        f.write(report_text)
    shutil.copy(reports_dir / "manifest.json", docs_dir / "manifest.json")
    logger.info("Mirrored report and manifest to %s", docs_dir)

    print("\n" + "="*80)
    print("BENCHMARK EXECUTION COMPLETE")
    print(f"Results saved to: {raw_results_file}")
    print(f"Report saved to:  {reports_dir / 'BENCHMARK_REPORT.md'}")
    print(f"Mirrored in:      {docs_dir / 'BENCHMARK_REPORT.md'}")
    print("="*80 + "\n")


if __name__ == "__main__":
    main()
