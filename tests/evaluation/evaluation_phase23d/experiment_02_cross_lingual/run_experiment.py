"""
Phase 23-D — EXP-02: Cross-Lingual Semantic Convergence Runner
Evaluates functional equivalence and SQI across English, Japanese, and Vietnamese
under Oracle Transduction (Mode A) and Rule-Based Transduction (Mode B)
for UMR-TPG (Primary), V-UMR (Secondary), and DRS-Graph (Control).
"""
import os
import json
import csv
import time
from typing import Dict, Any, List
try:
    from .transducers.oracle_transducer import transduce_oracle
    from .transducers.rule_transducer import transduce_rule_based
    from .queries.query_suite import evaluate_query_suite, QUERY_EXTRACTORS
except (ImportError, ValueError):
    import sys
    from pathlib import Path
    _root = Path(__file__).resolve().parent.parent.parent.parent.parent
    if str(_root) not in sys.path:
        sys.path.insert(0, str(_root))
    from tests.evaluation.evaluation_phase23d.experiment_02_cross_lingual.transducers.oracle_transducer import transduce_oracle
    from tests.evaluation.evaluation_phase23d.experiment_02_cross_lingual.transducers.rule_transducer import transduce_rule_based
    from tests.evaluation.evaluation_phase23d.experiment_02_cross_lingual.queries.query_suite import evaluate_query_suite, QUERY_EXTRACTORS


def evaluate_mode(corpus: Dict[str, Any], candidate_name: str, mode: str) -> Dict[str, Any]:
    """Evaluates cross-lingual equivalence for a given candidate under a specified mode."""
    pair_counts = {
        "EN_JA": {"match": 0, "total": 0},
        "EN_VI": {"match": 0, "total": 0},
        "JA_VI": {"match": 0, "total": 0},
    }
    tripartite_matches = 0
    total_queries = 0

    scenarios = corpus["scenarios"]
    per_scenario_details = []

    for scen in scenarios:
        sid = scen["id"]
        # Transduce for all three languages
        if mode == "oracle":
            inst_en = transduce_oracle(scen, candidate_name, "EN")
            inst_ja = transduce_oracle(scen, candidate_name, "JA")
            inst_vi = transduce_oracle(scen, candidate_name, "VI")
        elif mode == "rule_based":
            inst_en = transduce_rule_based(scen["text_en"], "EN", sid, candidate_name)
            inst_ja = transduce_rule_based(scen["text_ja"], "JA", sid, candidate_name)
            inst_vi = transduce_rule_based(scen["text_vi"], "VI", sid, candidate_name)
        else:
            raise ValueError(f"Unknown mode {mode}")

        # Pairwise query evaluations
        res_en_ja = evaluate_query_suite(inst_en, inst_ja)
        res_en_vi = evaluate_query_suite(inst_en, inst_vi)
        res_ja_vi = evaluate_query_suite(inst_ja, inst_vi)

        scen_record = {
            "scenario_id": sid,
            "phenomenon": scen["phenomenon"],
            "pairs": {
                "EN_JA": res_en_ja,
                "EN_VI": res_en_vi,
                "JA_VI": res_ja_vi,
            },
        }

        # Accumulate metrics
        for q_id in QUERY_EXTRACTORS.keys():
            total_queries += 1
            match_en_ja = res_en_ja[q_id]
            match_en_vi = res_en_vi[q_id]
            match_ja_vi = res_ja_vi[q_id]

            if match_en_ja:
                pair_counts["EN_JA"]["match"] += 1
            if match_en_vi:
                pair_counts["EN_VI"]["match"] += 1
            if match_ja_vi:
                pair_counts["JA_VI"]["match"] += 1

            pair_counts["EN_JA"]["total"] += 1
            pair_counts["EN_VI"]["total"] += 1
            pair_counts["JA_VI"]["total"] += 1

            # Tripartite match: all three match simultaneously
            if match_en_ja and match_en_vi and match_ja_vi:
                tripartite_matches += 1

        per_scenario_details.append(scen_record)

    sqi_en_ja = pair_counts["EN_JA"]["match"] / pair_counts["EN_JA"]["total"]
    sqi_en_vi = pair_counts["EN_VI"]["match"] / pair_counts["EN_VI"]["total"]
    sqi_ja_vi = pair_counts["JA_VI"]["match"] / pair_counts["JA_VI"]["total"]
    sqi_overall = (sqi_en_ja + sqi_en_vi + sqi_ja_vi) / 3.0
    fep = tripartite_matches / total_queries

    # Pass/Fail determination
    pass_threshold = 0.92
    verdict = "PASS" if sqi_overall >= pass_threshold else "FAIL"

    return {
        "mode": mode,
        "candidate": candidate_name,
        "verdict": verdict,
        "SQI": {
            "EN_JA": round(sqi_en_ja, 4),
            "EN_VI": round(sqi_en_vi, 4),
            "JA_VI": round(sqi_ja_vi, 4),
            "overall": round(sqi_overall, 4),
        },
        "FEP": round(fep, 4),
        "total_queries_evaluated": total_queries,
        "scenarios_evaluated": len(scenarios),
    }


def run_exp02_evaluation(corpus_path: str) -> Dict[str, Any]:
    with open(corpus_path, "r", encoding="utf-8") as f:
        corpus = json.load(f)

    candidates = ["UMR-TPG", "V-UMR", "DRS-Graph"]
    results: Dict[str, Any] = {
        "metadata": {
            "experiment": "EXP-02_cross_lingual_convergence",
            "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
            "languages": ["EN", "JA", "VI"],
            "total_scenarios": len(corpus["scenarios"]),
            "queries_per_scenario": 10,
        },
        "oracle_transduction": {},
        "rule_based_transduction": {},
        "concept_alignment": "UNVERIFIED (Requires external neural XS2match aligner not present in offline edge environment)",
        "layer_partition": {
            "Layer_A_Representation": "Evaluated via Oracle Transduction",
            "Layer_B_Transduction": "Evaluated via Rule-Based Transduction",
            "Layer_C_Functional_Equivalence": "Measured via SQI and FEP",
        },
        "failure_classification": {},
    }

    # 1. Oracle Mode (Representation capability)
    for cand in candidates:
        res = evaluate_mode(corpus, cand, mode="oracle")
        results["oracle_transduction"][cand] = res

    # 2. Rule-Based Mode (Transduction feasibility)
    for cand in candidates:
        res = evaluate_mode(corpus, cand, mode="rule_based")
        results["rule_based_transduction"][cand] = res

    # 3. Layered Failure Classification
    for cand in candidates:
        oracle_v = results["oracle_transduction"][cand]["verdict"]
        rule_v = results["rule_based_transduction"][cand]["verdict"]

        rep_fail = (oracle_v == "FAIL")
        trans_fail = (rule_v == "FAIL" and oracle_v == "PASS")
        equiv_fail = (results["oracle_transduction"][cand]["FEP"] < 0.90)

        results["failure_classification"][cand] = {
            "representation_failure": rep_fail,
            "transduction_failure": trans_fail,
            "functional_equivalence_failure": equiv_fail,
            "scientific_implication": (
                "Substrate successfully represents cross-lingual functional equivalence under correct semantic input."
                if oracle_v == "PASS" else
                "Substrate fundamentally fails cross-lingual functional equivalence."
            ),
        }

    return results


def export_exp02_results(results: Dict[str, Any], output_dir: str):
    os.makedirs(output_dir, exist_ok=True)
    json_path = os.path.join(output_dir, "results.json")
    csv_path = os.path.join(output_dir, "results.csv")

    with open(json_path, "w", encoding="utf-8") as f:
        json.dump(results, f, indent=2)

    with open(csv_path, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(["Mode", "Candidate", "Verdict", "SQI_Overall", "SQI_EN_JA", "SQI_EN_VI", "SQI_JA_VI", "FEP"])
        for mode_key, mode_title in [("oracle_transduction", "Oracle"), ("rule_based_transduction", "Rule-Based")]:
            for cand, d in results[mode_key].items():
                writer.writerow([
                    mode_title,
                    cand,
                    d["verdict"],
                    d["SQI"]["overall"],
                    d["SQI"]["EN_JA"],
                    d["SQI"]["EN_VI"],
                    d["SQI"]["JA_VI"],
                    d["FEP"],
                ])


if __name__ == "__main__":
    base_dir = os.path.dirname(__file__)
    corpus_file = os.path.join(base_dir, "dataset", "parallel_corpus.json")
    out_dir = os.path.join(base_dir, "results")

    res = run_exp02_evaluation(corpus_file)
    export_exp02_results(res, out_dir)
    print("EXP-02 completed successfully. Results saved to:", out_dir)
    for mode in ["oracle_transduction", "rule_based_transduction"]:
        print(f"\n--- {mode.upper()} ---")
        for cand, d in res[mode].items():
            print(f"[{d['verdict']}] {cand}: Overall SQI={d['SQI']['overall']} | FEP={d['FEP']}")
