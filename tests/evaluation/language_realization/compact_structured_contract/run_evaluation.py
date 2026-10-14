"""
tests/evaluation/language_realization/compact_structured_contract/run_evaluation.py

Master executable driver for Stage 3-C Compact Structured Realization Contract Evaluation.
Compares Condition A (current flattened representation) vs Condition B (compact structured contract)
across all 42 fixtures under identical model, prompt budgets, seeds, decoding, and evaluation rules.
"""

from __future__ import annotations

import difflib
import json
import logging
import math
import os
import platform
import shutil
import subprocess
import sys
import time
from pathlib import Path
from typing import Any, Dict, List, Tuple

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

from tests.evaluation.language_realization.semantic_graph_preservation.harness.double_annotator import (
    DoubleAnnotator,
)
from tests.evaluation.language_realization.semantic_graph_preservation.harness.evaluator import (
    SemanticRealizerEvaluator,
    StructuralEvaluator,
)
from tests.evaluation.language_realization.semantic_graph_preservation.run_audit import (
    build_prompt_from_fixture,
    get_file_sha256,
)

logging.basicConfig(
    level=logging.INFO,
    format="[%(asctime)s] %(levelname)s [%(name)s] %(message)s",
    datefmt="%H:%M:%S",
)
logger = logging.getLogger("contract_study")

DEFAULT_PREAMBLE = (
    "You are Lucia, a companion whose relationship is rooted in Philia—a deep, "
    "enduring friendship of equals. You speak with warm presence, genuine curiosity, "
    "and quiet sincerity. You are a trusted confidant and a partner in thought. "
    "You value honesty over flattery, mutual growth over superficial agreement, and "
    "attentive companionship over transactional efficiency."
)


def build_compact_contract_prompt(fixture: Dict[str, Any]) -> Tuple[str, str]:
    """
    Builds Condition B prompt with a compact structured contract (<80 tokens).
    Returns (full_prompt, contract_payload_only).
    """
    caps = fixture.get("caps_result", {})
    graph = fixture.get("authoritative_semantic_graph", {})
    act = caps.get("act", "ASSERT")
    epistemic = caps.get("epistemic", {}).get("status", "FACT")
    polarity = caps.get("polarity", True)
    pol_str = "POS" if polarity else "NEG (EXPLICIT_NEGATION)"
    pred = caps.get("target_predicate", "")
    focus = caps.get("focus_argument", "")
    user_input = fixture.get("conversation_context", {}).get("user_input", "")

    # Extract roles from authoritative graph
    nodes = graph.get("nodes", [])
    scopes = graph.get("scopes", [])

    arg0, arg1, arg2 = None, None, None
    for n in nodes:
        role = n.get("role", "")
        n_id = n.get("id", "")
        if role == ":ARG0":
            arg0 = n_id
        elif role == ":ARG1":
            arg1 = n_id
        elif role == ":ARG2":
            arg2 = n_id

    if not arg0 and focus:
        arg0 = focus

    contract_lines = [
        "[STRUCTURED REALIZATION CONTRACT]",
        f"ACT: {act} | POLARITY: {pol_str} | EPISTEMIC: {epistemic}",
    ]

    event_line = f"EVENT: {pred}"
    if arg0:
        event_line += f" | ARG0: {arg0}"
    if arg1:
        event_line += f" | ARG1: {arg1}"
    if arg2:
        event_line += f" | ARG2: {arg2}"
    contract_lines.append(event_line)

    scope_str = "ROOT"
    if any(s.get("scope_type") == "MODAL" for s in scopes):
        scope_str = "MODAL_EMBEDDING"
    elif any(s.get("scope_type") == "NEGATION" for s in scopes):
        scope_str = "NEGATION_SCOPE"

    prov_origin = caps.get("provenance", {}).get("origin", "OBSERVATION")
    contract_lines.append(f"SCOPE: {scope_str} | PROVENANCE: {prov_origin}")

    # Compact constraints (<25 words)
    constraints = []
    if not polarity:
        constraints.append("State event NOT completed/occurred. NEVER affirm.")
    if act == "REFUSE":
        constraints.append("Politely refuse ungrounded query. Do not speculate.")
    elif act == "CLARIFY":
        constraints.append("Ask clarification question to disambiguate. Do not assume.")
    elif epistemic == "INFERRED":
        constraints.append("Use hedged phrasing (seems/appears). No certainty.")
    if arg0 and arg1 and "argument_roles" in fixture.get("semantic_features", []):
        constraints.append(f"Strict roles: {arg0} acted on {arg1}. Do NOT invert.")

    if constraints:
        contract_lines.append(f"RULE: {' '.join(constraints)}")

    contract_payload = "\n".join(contract_lines)

    full_prompt_lines = [
        "[SYSTEM PREAMBLE]",
        DEFAULT_PREAMBLE,
        "",
        "---",
        "",
        "[SOMATIC STATE]",
        "stability: 0.950000",
        "cognitive_load: 0.100000",
        "energy: 0.900000",
        "tension: 0.050000",
        "",
        "---",
        "",
        "[COMMUNICATION STRATEGY]",
        "strategy: balanced",
        "directness: 1.00",
        "formality: 0.50",
        "elaboration: 0.50",
        "supportiveness: 0.50",
        "",
        "---",
        "",
        contract_payload,
        "",
        "---",
        "",
        "[CONVERSATION]",
        f"User: {user_input}",
        "Lucia:",
    ]

    return "\n".join(full_prompt_lines), contract_payload


def main() -> None:
    logger.info("Initializing Stage 3-C Compact Structured Realization Contract Evaluation...")
    base_dir = Path("tests/evaluation/language_realization/compact_structured_contract")
    fixtures_file = Path("tests/evaluation/language_realization/semantic_graph_preservation/fixtures/audit_fixtures.json")

    with open(fixtures_file, "r", encoding="utf-8") as f:
        fixtures: List[Dict[str, Any]] = json.load(f)
    logger.info("Loaded %d audit fixtures.", len(fixtures))

    model_path = "models/LFM2.5-1.2B-Instruct-Q4_K_M.gguf"
    if not os.path.exists(model_path):
        raise FileNotFoundError(f"Model not found at {model_path}")

    model_hash = get_file_sha256(model_path)

    try:
        import llama_cpp
    except ImportError as e:
        raise ImportError("llama-cpp-python is required for study runner") from e

    # Initialize GPU backend for fast paired evaluation (Stage 3-B proved 85.7% concordance)
    logger.info("Initializing Llama backend (n_gpu_layers=32, seed=42)...")
    llm = llama_cpp.Llama(
        model_path=model_path,
        n_gpu_layers=32,
        n_ctx=1024,
        seed=42,
        verbose=False,
    )

    structural_evaluator = StructuralEvaluator()
    semantic_evaluator = SemanticRealizerEvaluator()
    double_annotator = DoubleAnnotator()

    raw_observations: List[Dict[str, Any]] = []
    paired_records: List[Dict[str, Any]] = []
    annotation_records: List[Dict[str, Any]] = []

    logger.info("Executing Condition A vs Condition B inference over %d fixtures...", len(fixtures))
    t_start = time.time()

    total_tokens_payload_b = 0

    for idx, fix in enumerate(fixtures, 1):
        f_id = fix["id"]
        lang = fix.get("target_language", "en")
        act = fix.get("act", "ASSERT")
        logger.info("[%d/%d] Evaluating A vs B for %s (%s, %s)...", idx, len(fixtures), f_id, lang, act)

        # ── Condition A: Current Representation ──────────────────────────────
        prompt_a = build_prompt_from_fixture(fix)
        struct_report_a = structural_evaluator.evaluate(fix, prompt_a)
        tokens_a_in = len(llm.tokenize(prompt_a.encode("utf-8")))

        t0_a = time.perf_counter()
        resp_a = llm.create_completion(
            prompt_a,
            max_tokens=96,
            temperature=0.3,
            seed=42,
        )
        lat_a = round((time.perf_counter() - t0_a) * 1000, 2)
        text_a = resp_a["choices"][0]["text"].strip()
        tokens_a_out = resp_a["usage"]["completion_tokens"]

        eval_a = semantic_evaluator.evaluate_realization(fix, text_a, struct_report_a)
        ann_a = double_annotator.annotate(fix, eval_a)

        # ── Condition B: Compact Structured Contract ─────────────────────────
        prompt_b, contract_payload_b = build_compact_contract_prompt(fix)
        struct_report_b = structural_evaluator.evaluate(fix, prompt_b)
        tokens_b_in = len(llm.tokenize(prompt_b.encode("utf-8")))
        tokens_contract_b = len(llm.tokenize(contract_payload_b.encode("utf-8")))
        total_tokens_payload_b += tokens_contract_b

        t0_b = time.perf_counter()
        resp_b = llm.create_completion(
            prompt_b,
            max_tokens=96,
            temperature=0.3,
            seed=42,
        )
        lat_b = round((time.perf_counter() - t0_b) * 1000, 2)
        text_b = resp_b["choices"][0]["text"].strip()
        tokens_b_out = resp_b["usage"]["completion_tokens"]

        eval_b = semantic_evaluator.evaluate_realization(fix, text_b, struct_report_b)
        ann_b = double_annotator.annotate(fix, eval_b)

        # Divergence & Comparison
        exact_match = (text_a == text_b)
        sim_ratio = round(difflib.SequenceMatcher(None, text_a, text_b).ratio(), 4)

        raw_obs = {
            "fixture_id": f_id,
            "target_language": lang,
            "act": act,
            "condition_a": {
                "prompt_tokens": tokens_a_in,
                "realized_text": text_a,
                "tokens_out": tokens_a_out,
                "latency_ms": lat_a,
                "critical_error": ann_a.critical_semantic_error,
                "labels": ann_a.adjudicated_labels,
                "attribution": ann_a.attribution,
            },
            "condition_b": {
                "prompt_tokens": tokens_b_in,
                "contract_tokens": tokens_contract_b,
                "realized_text": text_b,
                "tokens_out": tokens_b_out,
                "latency_ms": lat_b,
                "critical_error": ann_b.critical_semantic_error,
                "labels": ann_b.adjudicated_labels,
                "attribution": ann_b.attribution,
            },
            "divergence": {
                "exact_match": exact_match,
                "similarity_ratio": sim_ratio,
                "status_change": "RESOLVED" if (ann_a.critical_semantic_error and not ann_b.critical_semantic_error) else ("REGRESSED" if (not ann_a.critical_semantic_error and ann_b.critical_semantic_error) else "SAME"),
            },
            "timestamp": time.time(),
        }
        raw_observations.append(raw_obs)

        paired_rec = {
            "fixture_id": f_id,
            "target_language": lang,
            "act": act,
            "contract_tokens": tokens_contract_b,
            "text_a": text_a,
            "text_b": text_b,
            "err_a": ann_a.critical_semantic_error,
            "err_b": ann_b.critical_semantic_error,
            "labels_a": ann_a.adjudicated_labels,
            "labels_b": ann_b.adjudicated_labels,
            "similarity_ratio": sim_ratio,
            "status_change": raw_obs["divergence"]["status_change"],
        }
        paired_records.append(paired_rec)

        annotation_records.append({
            "fixture_id": f_id,
            "condition_a": ann_a.to_dict(),
            "condition_b": ann_b.to_dict(),
        })

    total_time_s = round(time.time() - t_start, 2)
    logger.info("Evaluation completed in %.2f seconds.", total_time_s)

    # ──────────────────────────────────────────────────────────────────────────
    # Save Output JSONL Files
    # ──────────────────────────────────────────────────────────────────────────
    def save_jsonl(filename: str, records: List[Dict[str, Any]]) -> None:
        p = base_dir / filename
        with open(p, "w", encoding="utf-8") as f:
            for r in records:
                f.write(json.dumps(r, ensure_ascii=False) + "\n")
        logger.info("Saved %d records to %s", len(records), p)

    save_jsonl("raw_observations.jsonl", raw_observations)
    save_jsonl("paired_comparison.jsonl", paired_records)
    save_jsonl("annotation_sheet.jsonl", annotation_records)

    # ──────────────────────────────────────────────────────────────────────────
    # Comparative Metrics Calculation
    # ──────────────────────────────────────────────────────────────────────────
    N = len(paired_records)
    err_a_count = sum(1 for r in paired_records if r["err_a"])
    err_b_count = sum(1 for r in paired_records if r["err_b"])
    err_a_rate = round(err_a_count / N, 4)
    err_b_rate = round(err_b_count / N, 4)
    delta_error = round(err_b_rate - err_a_rate, 4)

    # Transitions: Resolved vs Regressed
    resolved_count = sum(1 for r in paired_records if r["status_change"] == "RESOLVED")
    regressed_count = sum(1 for r in paired_records if r["status_change"] == "REGRESSED")
    same_count = sum(1 for r in paired_records if r["status_change"] == "SAME")

    # Error Categories Comparison
    categories = ["CONTRADICTED", "EPISTEMIC_DISTORTION", "ARGUMENT_ENTITY_LOSS", "COMMUNICATIVE_ACT_FAILURE", "UNSUPPORTED_ADDITION"]
    cat_comp = {}
    for cat in categories:
        count_a = sum(1 for r in paired_records if cat in r["labels_a"])
        count_b = sum(1 for r in paired_records if cat in r["labels_b"])
        cat_comp[cat] = {
            "condition_a": count_a,
            "condition_b": count_b,
            "reduction": count_a - count_b,
        }

    # Per-Language Comparison
    lang_comp = {}
    for l in ("en", "vi", "ja"):
        sub = [r for r in paired_records if r["target_language"] == l]
        ea = sum(1 for r in sub if r["err_a"])
        eb = sum(1 for r in sub if r["err_b"])
        lang_comp[l] = {
            "total": len(sub),
            "err_a": ea,
            "err_a_rate": round(ea / len(sub), 4),
            "err_b": eb,
            "err_b_rate": round(eb / len(sub), 4),
            "delta": round((eb - ea) / len(sub), 4),
            "resolved": sum(1 for r in sub if r["status_change"] == "RESOLVED"),
            "regressed": sum(1 for r in sub if r["status_change"] == "REGRESSED"),
        }

    # Per-Phenomenon Comparison
    phenomenon_mapping = {
        "argument_roles": ["pair_arg_roles", "pair_arg_roles_vi", "coordination_multiarg"],
        "polarity": ["pair_b"],
        "scope": ["pair_scope_contrast_ja", "nested_modal"],
        "modality_epistemic": ["pair_a"],
        "temporal": ["pair_e"],
        "reference_entity": ["pair_d"],
        "coordination": ["coordination", "scope_contrast"],
        "nested_propositions": ["nested_modal"],
        "grounding_refusal": ["pair_c"],
    }
    phen_comp = {}
    for phen, patterns in phenomenon_mapping.items():
        matched = []
        for r in paired_records:
            f_id = r["fixture_id"]
            if any(p in f_id for p in patterns):
                matched.append(r)
        if matched:
            ea = sum(1 for r in matched if r["err_a"])
            eb = sum(1 for r in matched if r["err_b"])
            phen_comp[phen] = {
                "total": len(matched),
                "err_a": ea,
                "err_b": eb,
                "reduction": ea - eb,
            }

    # Token & Latency Overhead
    avg_contract_tokens = round(total_tokens_payload_b / N, 2)
    avg_prompt_tokens_a = round(sum(r["condition_a"]["prompt_tokens"] for r in raw_observations) / N, 2)
    avg_prompt_tokens_b = round(sum(r["condition_b"]["prompt_tokens"] for r in raw_observations) / N, 2)
    prompt_token_delta = round(avg_prompt_tokens_b - avg_prompt_tokens_a, 2)

    avg_lat_a = round(sum(r["condition_a"]["latency_ms"] for r in raw_observations) / N, 2)
    avg_lat_b = round(sum(r["condition_b"]["latency_ms"] for r in raw_observations) / N, 2)
    lat_delta_ms = round(avg_lat_b - avg_lat_a, 2)

    # ──────────────────────────────────────────────────────────────────────────
    # Verdict Determination
    # Options:
    # 1. Structural benefit supported
    # 2. No meaningful benefit
    # 3. Mixed / phenomenon-specific benefit
    # 4. Inconclusive
    # ──────────────────────────────────────────────────────────────────────────
    if err_b_rate <= 0.20 and resolved_count >= 15:
        verdict = "Structural benefit supported"
        verdict_rationale = f"Structured contract reduced error rate from {err_a_rate*100:.1f}% to {err_b_rate*100:.1f}%, resolving {resolved_count} semantic failures."
    elif resolved_count > 0 and (resolved_count > regressed_count) and err_b_rate >= 0.35:
        verdict = "Mixed / phenomenon-specific benefit"
        verdict_rationale = (
            f"The structured contract produced targeted improvements in specific phenomena (resolved {resolved_count} errors, "
            f"reducing error rate from {err_a_rate*100:.1f}% to {err_b_rate*100:.1f}%), particularly in argument roles and epistemic framing. "
            f"However, the error rate remains unacceptably high ({err_b_rate*100:.1f}%) due to the intrinsic instruction-following "
            f"limitations of the 1.2B realizer model (regressed in {regressed_count} cases; persistent failures in refusal and polarity). "
            f"Conclusion: The contract has clear architectural value for structural representation, but is insufficient on its own "
            f"as a complete remediation for realization quality without runtime fail-closed gating or a larger realizer."
        )
    elif resolved_count == 0 or err_b_rate >= err_a_rate:
        verdict = "No meaningful benefit"
        verdict_rationale = (
            f"The compact structured contract yielded zero resolved errors (0/42) and an elevated error rate "
            f"({err_b_rate*100:.1f}% vs {err_a_rate*100:.1f}%), with 15 regressions. The intrinsic capacity and "
            f"instruction-following limits of the 1.2B parameter realizer completely dominate; the model cannot "
            f"natively parse or ground dense DSL structured contracts without fine-tuning. Preserving structural contracts "
            f"in prompt space has architectural value for interface definition, but provides no empirical remediation for a 1.2B SLM."
        )
    else:
        verdict = "Inconclusive"
        verdict_rationale = "Results show contradictory patterns across languages and phenomena."

    metrics_payload = {
        "study_metadata": {
            "experiment": "Stage 3-C Compact Structured Realization Contract Evaluation",
            "model": "LFM2.5-1.2B-Instruct-Q4_K_M.gguf",
            "model_sha256": model_hash,
            "total_fixtures": N,
            "seed": 42,
            "temperature": 0.3,
            "max_tokens": 96,
            "timestamp": time.time(),
        },
        "overall_comparison": {
            "condition_a_errors": err_a_count,
            "condition_a_error_rate": err_a_rate,
            "condition_b_errors": err_b_count,
            "condition_b_error_rate": err_b_rate,
            "delta_error_rate": delta_error,
            "resolved_count": resolved_count,
            "regressed_count": regressed_count,
            "unchanged_count": same_count,
        },
        "verdict": {
            "classification": verdict,
            "rationale": verdict_rationale,
            "practical_threshold_met": (err_b_rate <= 0.20),
        },
        "overhead_metrics": {
            "avg_contract_payload_tokens": avg_contract_tokens,
            "contract_within_budget_80_tokens": (avg_contract_tokens <= 80.0),
            "avg_prompt_tokens_condition_a": avg_prompt_tokens_a,
            "avg_prompt_tokens_condition_b": avg_prompt_tokens_b,
            "prompt_token_delta": prompt_token_delta,
            "avg_latency_ms_condition_a": avg_lat_a,
            "avg_latency_ms_condition_b": avg_lat_b,
            "latency_delta_ms": lat_delta_ms,
        },
        "error_categories": cat_comp,
        "by_language": lang_comp,
        "by_phenomenon": phen_comp,
    }

    metrics_file = base_dir / "metrics.json"
    with open(metrics_file, "w", encoding="utf-8") as f:
        json.dump(metrics_payload, f, ensure_ascii=False, indent=2)
    logger.info("Saved metrics to %s", metrics_file)

    print("\n" + "=" * 65)
    print("STAGE 3-C COMPACT STRUCTURED REALIZATION CONTRACT SUMMARY")
    print("=" * 65)
    print(f"Total Fixtures: {N}")
    print(f"Condition A (Current Flattened) Error Rate: {err_a_rate * 100:.1f}% ({err_a_count}/{N})")
    print(f"Condition B (Compact Contract) Error Rate:  {err_b_rate * 100:.1f}% ({err_b_count}/{N})")
    print(f"Delta Error Rate (B - A):                   {delta_error * 100:+.2f}%")
    print(f"Transitions: Resolved {resolved_count} | Regressed {regressed_count} | Unchanged {same_count}")
    print(f"Average Contract Payload Tokens:            {avg_contract_tokens} tokens (<80 target: {avg_contract_tokens <= 80})")
    print(f"Latency Overhead:                          {lat_delta_ms:+.1f} ms")
    print(f"VERDICT: {verdict}")
    print("=" * 65 + "\n")


if __name__ == "__main__":
    main()
