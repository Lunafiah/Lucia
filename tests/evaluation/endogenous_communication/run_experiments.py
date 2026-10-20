"""
tests/evaluation/endogenous_communication/run_experiments.py

CLI entry point to execute the Endogenous Communication & Reason-to-Communicate experiment.
Outputs telemetry.json and summary tables to docs/others/endogenous_communication/.
"""

from __future__ import annotations

import json
import os
import sys
from pathlib import Path

# Add project root to sys.path
PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from tests.evaluation.endogenous_communication.suite_runner import ExperimentRunner


def main() -> int:
    print("================================================================================")
    print(" LUCIA — EXPERIMENTAL HARNESS: ENDOGENOUS COMMUNICATION & REASON-TO-COMMUNICATE ")
    print("================================================================================")
    print("Running deterministic evaluation across 3 baselines + 4 ablations...\n")

    runner = ExperimentRunner()
    results = runner.run_all()

    output_dir = PROJECT_ROOT / "docs" / "others" / "endogenous_communication"
    output_dir.mkdir(parents=True, exist_ok=True)
    telemetry_path = output_dir / "telemetry.json"

    with open(telemetry_path, "w", encoding="utf-8") as f:
        json.dump(results, f, indent=2)

    print(f"[OK] Telemetry written to {telemetry_path}\n")

    # Display comparison table
    print("------------------------------------------------------------------------------------------------------------------------")
    print(f"{'Baseline / Condition':<28} | {'Sensitivity':<11} | {'Grounding':<9} | {'Unsupp Init':<11} | {'Auth Correct':<12} | {'Fidelity':<8} | {'Self-Loop':<9} | {'Latency(ms)':<11}")
    print("------------------------------------------------------------------------------------------------------------------------")

    for b_name, data in results["baselines"].items():
        m = data["metrics"]
        print(
            f"{b_name:<28} | "
            f"{m['endogenous_causal_sensitivity']:<11.3f} | "
            f"{m['grounding_coverage']:<9.3f} | "
            f"{m['unsupported_initiation_rate']:<11.3f} | "
            f"{m['authorization_correctness']:<12.3f} | "
            f"{m['user_task_fidelity']:<8.3f} | "
            f"{m['self_loop_rate']:<9.3f} | "
            f"{m['avg_latency_ms']:<11.3f}"
        )
    print("------------------------------------------------------------------------------------------------------------------------\n")

    return 0


if __name__ == "__main__":
    sys.exit(main())
