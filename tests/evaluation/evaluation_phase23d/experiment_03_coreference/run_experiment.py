"""
Phase 23-D — EXP-03: Reference Resolution & Zero-Anaphora Runner
Evaluates UMR-TPG, V-UMR, and DRS-Graph across 10 discourse phenomena
measuring B3_F1, CEAF_e_F1, CRA, URP, EPR, and RSA under
Representation (Mode A) and Resolution (Mode B) conditions.
"""
from typing import Dict, List, Any
import os
import json
import csv
import time
import numpy as np

try:
    from .metrics import (
        compute_b3,
        compute_ceaf_e,
        compute_resolution_accuracy,
        compute_unknown_precision,
        compute_entity_persistence_rate,
        compute_reference_switch_accuracy,
    )
    from .models.umr_coreference import UMRCoreferenceSubstrate
    from .models.vumr_coreference import VUMRCoreferenceSubstrate
    from .models.drs_coreference import DRSGraphCoreferenceSubstrate
except (ImportError, ValueError):
    import sys
    from pathlib import Path
    _root = Path(__file__).resolve().parent.parent.parent.parent.parent
    if str(_root) not in sys.path:
        sys.path.insert(0, str(_root))
    from tests.evaluation.evaluation_phase23d.experiment_03_coreference.metrics import (
        compute_b3,
        compute_ceaf_e,
        compute_resolution_accuracy,
        compute_unknown_precision,
        compute_entity_persistence_rate,
        compute_reference_switch_accuracy,
    )
    from tests.evaluation.evaluation_phase23d.experiment_03_coreference.models.umr_coreference import (
        UMRCoreferenceSubstrate,
    )
    from tests.evaluation.evaluation_phase23d.experiment_03_coreference.models.vumr_coreference import (
        VUMRCoreferenceSubstrate,
    )
    from tests.evaluation.evaluation_phase23d.experiment_03_coreference.models.drs_coreference import (
        DRSGraphCoreferenceSubstrate,
    )


def instantiate_substrate(candidate_name: str):
    if candidate_name == "UMR-TPG":
        return UMRCoreferenceSubstrate()
    elif candidate_name == "V-UMR":
        return VUMRCoreferenceSubstrate()
    elif candidate_name == "DRS-Graph":
        return DRSGraphCoreferenceSubstrate()
    raise ValueError(f"Unknown candidate {candidate_name}")


def evaluate_candidate(corpus: Dict[str, Any], candidate_name: str, mode: str) -> Dict[str, Any]:
    scenarios = corpus["scenarios"]

    b3_p_list, b3_r_list, b3_f1_list = [], [], []
    ceaf_p_list, ceaf_r_list, ceaf_f1_list = [], [], []
    cra_list = []
    urp_list = []
    epr_list = []
    rsa_list = []

    per_scenario = []

    for scen in scenarios:
        sub = instantiate_substrate(candidate_name)
        gold = scen["gold_clusters"]

        if mode == "representation":
            pred = sub.run_representation_mode(scen)
        elif mode == "resolution":
            pred = sub.run_resolution_mode(scen)
        else:
            raise ValueError(f"Unknown mode {mode}")

        b3_p, b3_r, b3_f1 = compute_b3(gold, pred)
        ceaf_p, ceaf_r, ceaf_f1 = compute_ceaf_e(gold, pred)
        cra = compute_resolution_accuracy(gold, pred)
        urp = compute_unknown_precision(gold, pred)
        epr = compute_entity_persistence_rate(gold, pred)
        rsa = compute_reference_switch_accuracy(gold, pred)

        b3_p_list.append(b3_p)
        b3_r_list.append(b3_r)
        b3_f1_list.append(b3_f1)
        ceaf_p_list.append(ceaf_p)
        ceaf_r_list.append(ceaf_r)
        ceaf_f1_list.append(ceaf_f1)
        cra_list.append(cra)
        urp_list.append(urp)
        epr_list.append(epr)
        rsa_list.append(rsa)

        per_scenario.append({
            "id": scen["id"],
            "phenomenon": scen["phenomenon"],
            "b3_f1": round(b3_f1, 4),
            "ceaf_e_f1": round(ceaf_f1, 4),
            "cra": round(cra, 4),
            "urp": round(urp, 4),
            "epr": round(epr, 4),
            "rsa": round(rsa, 4),
        })

    mean_b3_f1 = float(np.mean(b3_f1_list))
    mean_ceaf_f1 = float(np.mean(ceaf_f1_list))
    mean_cra = float(np.mean(cra_list))
    mean_urp = float(np.mean(urp_list))
    mean_epr = float(np.mean(epr_list))
    mean_rsa = float(np.mean(rsa_list))

    # Gate verification: CEAF_e_F1 >= 0.82, EPR >= 0.95, URP >= 0.90
    verdict = "PASS" if (mean_ceaf_f1 >= 0.82 and mean_epr >= 0.95 and mean_urp >= 0.90) else "FAIL"

    return {
        "candidate": candidate_name,
        "mode": mode,
        "verdict": verdict,
        "B3_F1": round(mean_b3_f1, 4),
        "CEAF_e_F1": round(mean_ceaf_f1, 4),
        "CRA": round(mean_cra, 4),
        "URP": round(mean_urp, 4),
        "EPR": round(mean_epr, 4),
        "RSA": round(mean_rsa, 4),
        "per_scenario": per_scenario,
    }


def run_exp03_evaluation(corpus_path: str) -> Dict[str, Any]:
    with open(corpus_path, "r", encoding="utf-8") as f:
        corpus = json.load(f)

    candidates = ["UMR-TPG", "V-UMR", "DRS-Graph"]
    results: Dict[str, Any] = {
        "metadata": {
            "experiment": "EXP-03_reference_resolution_and_zero_anaphora",
            "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
            "total_scenarios": len(corpus["scenarios"]),
            "candidates": candidates,
        },
        "representation_capability": {},
        "resolution_capability": {},
        "failure_cases": [],
        "layer_attribution": {
            "Layer_A_Representation": "Evaluated via Mode A (Gold entity assignments)",
            "Layer_B_Resolution": "Evaluated via Mode B (Deterministic anaphora resolution)",
        },
    }

    # 1. Representation Mode (Layer A)
    for cand in candidates:
        results["representation_capability"][cand] = evaluate_candidate(corpus, cand, mode="representation")

    # 2. Resolution Mode (Layer B)
    for cand in candidates:
        results["resolution_capability"][cand] = evaluate_candidate(corpus, cand, mode="resolution")

    return results


def export_exp03_results(results: Dict[str, Any], output_dir: str):
    os.makedirs(output_dir, exist_ok=True)
    json_path = os.path.join(output_dir, "results.json")
    csv_path = os.path.join(output_dir, "results.csv")

    with open(json_path, "w", encoding="utf-8") as f:
        json.dump(results, f, indent=2)

    with open(csv_path, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(["Mode", "Candidate", "Verdict", "CEAF_e_F1", "B3_F1", "CRA", "URP", "EPR", "RSA"])
        for mode_key, mode_title in [("representation_capability", "Representation"), ("resolution_capability", "Resolution")]:
            for cand, d in results[mode_key].items():
                writer.writerow([
                    mode_title,
                    cand,
                    d["verdict"],
                    d["CEAF_e_F1"],
                    d["B3_F1"],
                    d["CRA"],
                    d["URP"],
                    d["EPR"],
                    d["RSA"],
                ])


if __name__ == "__main__":
    base_dir = os.path.dirname(__file__)
    corpus_file = os.path.join(base_dir, "dataset", "corpus.json")
    out_dir = os.path.join(base_dir, "results")

    res = run_exp03_evaluation(corpus_file)
    export_exp03_results(res, out_dir)
    print("EXP-03 completed successfully. Results saved to:", out_dir)
    for mode in ["representation_capability", "resolution_capability"]:
        print(f"\n--- {mode.upper()} ---")
        for cand, d in res[mode].items():
            print(f"[{d['verdict']}] {cand}: CEAF_e_F1={d['CEAF_e_F1']} | B3_F1={d['B3_F1']} | CRA={d['CRA']} | URP={d['URP']} | EPR={d['EPR']} | RSA={d['RSA']}")
