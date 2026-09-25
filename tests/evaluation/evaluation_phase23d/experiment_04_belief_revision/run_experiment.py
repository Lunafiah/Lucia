"""Execution Runner for EXP-04: Belief Revision & Contradiction.

Runs evaluation on UMR-TPG, V-UMR, and DRS-Graph across 10 deterministic scenarios.
Exports metrics to results.json and results.csv.
"""

from __future__ import annotations

import csv
import json
import time
from pathlib import Path
from typing import Any, Dict, List, Set, Type

import sys
from pathlib import Path

# Add project root to sys.path if run directly
project_root = Path(__file__).resolve().parents[4]
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

from tests.evaluation.evaluation_phase23d.experiment_04_belief_revision.metrics import evaluate_run
from tests.evaluation.evaluation_phase23d.experiment_04_belief_revision.models.drs_belief_revision import (
    DRSBeliefEngine,
)
from tests.evaluation.evaluation_phase23d.experiment_04_belief_revision.models.umr_belief_revision import (
    UMRBeliefEngine,
)
from tests.evaluation.evaluation_phase23d.experiment_04_belief_revision.models.vumr_belief_revision import (
    VUMRBeliefEngine,
)


def run_single_scenario(
    engine_cls: Type[Any],
    scenario: Dict[str, Any],
) -> Dict[str, Any]:
    engine = engine_cls()
    all_introduced_ids: Set[str] = set()

    start_time = time.perf_counter()

    # Step 1: Ingest initial assertions
    for ast_data in scenario.get("initial_assertions", []):
        all_introduced_ids.add(ast_data["id"])
        engine.assert_fact(ast_data)

    # Step 2: Sequentially ingest updates
    for update_data in scenario.get("updates", []):
        all_introduced_ids.add(update_data["id"])
        engine.assert_fact(update_data)

    elapsed_ms = (time.perf_counter() - start_time) * 1000.0

    detected_contradictions = engine.get_detected_contradictions()
    actual_states = engine.get_operational_states()
    history_ids = engine.get_history_ids()

    eval_result = evaluate_run(
        detected_contradictions=detected_contradictions,
        actual_states=actual_states,
        retrievable_history_ids=history_ids,
        expected_oracle=scenario["expected_oracle"],
        all_introduced_ids=all_introduced_ids,
        elapsed_ms=elapsed_ms,
    )

    eval_result["scenario_id"] = scenario["id"]
    eval_result["scenario_name"] = scenario["name"]
    return eval_result


def run_all_exp04(
    corpus_path: Path,
    output_dir: Path,
) -> Dict[str, Any]:
    with open(corpus_path, "r", encoding="utf-8") as f:
        corpus = json.load(f)

    scenarios = corpus["scenarios"]
    candidates = {
        "UMR-TPG": UMRBeliefEngine,
        "V-UMR": VUMRBeliefEngine,
        "DRS-Graph": DRSBeliefEngine,
    }

    full_results: Dict[str, Any] = {
        "benchmark": "Phase23D_EXP04_BeliefRevision",
        "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
        "scenario_count": len(scenarios),
        "candidates": {},
    }

    csv_rows: List[Dict[str, Any]] = []

    for cand_name, engine_cls in candidates.items():
        cand_scenario_results: List[Dict[str, Any]] = []
        for sc in scenarios:
            res = run_single_scenario(engine_cls, sc)
            res["candidate"] = cand_name
            cand_scenario_results.append(res)
            csv_rows.append(res)

        # Aggregate metrics across scenarios
        mean_cdr = sum(r["CDR"] for r in cand_scenario_results) / len(cand_scenario_results)
        mean_rc = sum(r["RC"] for r in cand_scenario_results) / len(cand_scenario_results)
        mean_dpa = sum(r["DPA"] for r in cand_scenario_results) / len(cand_scenario_results)
        mean_crr = sum(r["CRR"] for r in cand_scenario_results) / len(cand_scenario_results)
        mean_hrr = sum(r["HRR"] for r in cand_scenario_results) / len(cand_scenario_results)
        mean_lat = sum(r["latency_ms"] for r in cand_scenario_results) / len(cand_scenario_results)
        all_passed = all(r["passed"] for r in cand_scenario_results)

        full_results["candidates"][cand_name] = {
            "mean_CDR": round(mean_cdr, 4),
            "mean_RC": round(mean_rc, 4),
            "mean_DPA": round(mean_dpa, 4),
            "mean_CRR": round(mean_crr, 4),
            "mean_HRR": round(mean_hrr, 4),
            "mean_latency_ms": round(mean_lat, 3),
            "verdict": "PASS" if all_passed else "FAIL",
            "scenario_results": cand_scenario_results,
        }

    # Write results
    output_dir.mkdir(parents=True, exist_ok=True)
    json_path = output_dir / "results.json"
    with open(json_path, "w", encoding="utf-8") as f:
        json.dump(full_results, f, indent=2)

    csv_path = output_dir / "results.csv"
    if csv_rows:
        fieldnames = [
            "candidate",
            "scenario_id",
            "scenario_name",
            "CDR",
            "RC",
            "DPA",
            "CRR",
            "HRR",
            "latency_ms",
            "passed",
        ]
        with open(csv_path, "w", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(csv_rows)

    return full_results


if __name__ == "__main__":
    base_dir = Path(__file__).parent
    corpus_file = base_dir / "dataset" / "corpus.json"
    results_dir = base_dir / "results"
    summary = run_all_exp04(corpus_file, results_dir)

    print("=" * 80)
    print("EXP-04: Belief Revision & Contradiction Evaluation Summary")
    print("=" * 80)
    for c_name, c_data in summary["candidates"].items():
        print(
            f"Candidate: {c_name:<10} | Verdict: {c_data['verdict']:<4} | "
            f"CDR: {c_data['mean_CDR']:.3f} | RC: {c_data['mean_RC']:.3f} | "
            f"DPA: {c_data['mean_DPA']:.3f} | CRR: {c_data['mean_CRR']:.3f} | "
            f"HRR: {c_data['mean_HRR']:.3f} | Latency: {c_data['mean_latency_ms']:.3f}ms"
        )
    print("=" * 80)
