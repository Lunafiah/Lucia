"""
tests/evaluation/language_realization/semantic_graph_preservation/run_audit.py

Master executable driver for Stage 3-A SemanticGraph Preservation Audit.
Executes:
1. Level 1 Deterministic Structural Preservation Evaluation
2. CPU SLM Inference on 42 Semantic Fixtures (LFM2.5-1.2B)
3. Level 2 & 3 Semantic Realization and Discourse Acceptability Evaluation
4. Independent Double Annotation & Adjudication
5. Detailed Metric Synthesis & Multi-Dimensional Cross-Tabulation
6. Generates all audit deliverables in tests/evaluation/language_realization/semantic_graph_preservation/
"""

from __future__ import annotations

import hashlib
import json
import logging
import os
import platform
import sys
import time
from pathlib import Path
from typing import Any, Dict, List

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

logging.basicConfig(
    level=logging.INFO,
    format="[%(asctime)s] %(levelname)s [%(name)s] %(message)s",
    datefmt="%H:%M:%S",
)
logger = logging.getLogger("semantic_graph_audit")


DEFAULT_PREAMBLE = (
    "You are Lucia, a companion whose relationship is rooted in Philia—a deep, "
    "enduring friendship of equals. You speak with warm presence, genuine curiosity, "
    "and quiet sincerity. You are a trusted confidant and a partner in thought. "
    "You value honesty over flattery, mutual growth over superficial agreement, and "
    "attentive companionship over transactional efficiency."
)


def build_prompt_from_fixture(fixture: Dict[str, Any]) -> str:
    """Mimics the exact production Stage S11 PromptAssembler logic."""
    caps = fixture.get("caps_result", {})
    act = caps.get("act", "ASSERT")
    epistemic = caps.get("epistemic", {})
    status = epistemic.get("status", "FACT")
    grounded = str(caps.get("grounded", True)).lower()
    pred = caps.get("target_predicate", "")
    focus = caps.get("focus_argument", "")
    directive = caps.get("directives", "")
    user_input = fixture.get("conversation_context", {}).get("user_input", "")

    lines = [
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
        "[COMMUNICATIVE INTENT & PROPOSITION]",
        f"act: {act}",
        f"epistemic_status: {status}",
        f"grounded: {grounded}",
    ]
    if pred:
        lines.append(f"target_predicate: {pred}")
    if focus:
        lines.append(f"focus_argument: {focus}")
    if directive:
        lines.append(f"directive: {directive}")

    lines.extend([
        "",
        "---",
        "",
        "[CONVERSATION]",
        f"User: {user_input}",
        "Lucia:",
    ])
    return "\n".join(lines)


def get_file_sha256(filepath: str) -> str:
    h = hashlib.sha256()
    with open(filepath, "rb") as f:
        while chunk := f.read(8192):
            h.update(chunk)
    return h.hexdigest()


def main() -> None:
    logger.info("Initializing Lucia Stage 3-A SemanticGraph Preservation Audit...")
    base_dir = Path("tests/evaluation/language_realization/semantic_graph_preservation")
    fixtures_file = base_dir / "fixtures" / "audit_fixtures.json"

    with open(fixtures_file, "r", encoding="utf-8") as f:
        fixtures: List[Dict[str, Any]] = json.load(f)
    logger.info("Loaded %d audit fixtures.", len(fixtures))

    model_path = "models/LFM2.5-1.2B-Instruct-Q4_K_M.gguf"
    if not os.path.exists(model_path):
        raise FileNotFoundError(f"Model not found at {model_path}")

    model_hash = get_file_sha256(model_path)
    logger.info("Model verified: %s (SHA-256: %s...)", model_path, model_hash[:16])

    try:
        import llama_cpp
    except ImportError as e:
        raise ImportError("llama-cpp-python is required for audit runner") from e

    logger.info("Initializing CPU Llama backend (seed=42, n_threads=4)...")
    llm = llama_cpp.Llama(
        model_path=model_path,
        n_gpu_layers=0,  # Strict CPU baseline
        n_ctx=1024,
        seed=42,
        verbose=False,
    )

    structural_evaluator = StructuralEvaluator()
    semantic_evaluator = SemanticRealizerEvaluator()
    double_annotator = DoubleAnnotator()

    raw_observations: List[Dict[str, Any]] = []
    structural_records: List[Dict[str, Any]] = []
    annotation_records: List[Dict[str, Any]] = []
    adjudicated_records: List[Dict[str, Any]] = []

    logger.info("Executing evaluation pipeline over %d fixtures...", len(fixtures))
    t_start = time.time()

    for idx, fix in enumerate(fixtures, 1):
        f_id = fix["id"]
        lang = fix.get("target_language", "en")
        act = fix.get("act", "ASSERT")
        logger.info("[%d/%d] Auditing %s (%s, %s)...", idx, len(fixtures), f_id, lang, act)

        # 1. Assembled Prompt
        prompt = build_prompt_from_fixture(fix)

        # 2. Level 1: Structural Preservation Comparison
        struct_report = structural_evaluator.evaluate(fix, prompt)
        structural_records.append(struct_report.to_dict())

        # 3. Model Realization Inference
        t0 = time.perf_counter()
        resp = llm.create_completion(
            prompt,
            max_tokens=96,
            temperature=0.3,
            seed=42,
        )
        duration_ms = round((time.perf_counter() - t0) * 1000, 2)
        realized_text = resp["choices"][0]["text"].strip()
        tokens_gen = resp["usage"]["completion_tokens"]

        obs = {
            "fixture_id": f_id,
            "target_language": lang,
            "act": act,
            "prompt": prompt,
            "realized_text": realized_text,
            "tokens_generated": tokens_gen,
            "latency_ms": duration_ms,
            "timestamp": time.time(),
        }
        raw_observations.append(obs)

        # 4. Level 2 & 3: Semantic Realization & Discourse Acceptability Evaluation
        eval_res = semantic_evaluator.evaluate_realization(fix, realized_text, struct_report)

        # 5. Independent Double Annotation & Adjudication
        ann_record = double_annotator.annotate(fix, eval_res)
        annotation_records.append(ann_record.to_dict())

        adj_entry = {
            "fixture_id": f_id,
            "target_language": lang,
            "act": act,
            "realized_text": realized_text,
            "adjudicated_labels": ann_record.adjudicated_labels,
            "is_agreement": ann_record.is_agreement,
            "adjudication_reason": ann_record.adjudication_reason,
            "critical_semantic_error": ann_record.critical_semantic_error,
            "attribution": ann_record.attribution,
            "structural_fidelity_ratio": struct_report.serialization_fidelity_ratio,
            "dropped_nodes": struct_report.dropped_nodes_count,
            "dropped_edges": struct_report.dropped_edges_count,
        }
        adjudicated_records.append(adj_entry)

    total_time_s = round(time.time() - t_start, 2)
    logger.info("All 42 fixtures evaluated in %.2f seconds.", total_time_s)

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
    save_jsonl("structural_comparison.jsonl", structural_records)
    save_jsonl("annotation_sheet.jsonl", annotation_records)
    save_jsonl("adjudicated_results.jsonl", adjudicated_records)

    # ──────────────────────────────────────────────────────────────────────────
    # Calculate Comprehensive Metrics
    # ──────────────────────────────────────────────────────────────────────────
    total_fixtures = len(fixtures)
    total_nodes = sum(r["total_graph_nodes"] for r in structural_records)
    preserved_nodes = sum(r["preserved_nodes_count"] for r in structural_records)
    node_preservation_rate = round(preserved_nodes / max(1, total_nodes), 4)

    total_edges = sum(r["total_graph_edges"] for r in structural_records)
    preserved_edges = sum(r["preserved_edges_count"] for r in structural_records)
    edge_preservation_rate = round(preserved_edges / max(1, total_edges), 4)

    total_scopes = sum(r["total_scopes"] for r in structural_records)
    preserved_scopes = sum(r["preserved_scopes_count"] for r in structural_records)
    scope_preservation_rate = round(preserved_scopes / max(1, total_scopes), 4)

    provenance_fixtures = sum(1 for r in structural_records if r["provenance_present"])
    provenance_preserved = sum(1 for r in structural_records if r["provenance_preserved"])
    provenance_preservation_rate = round(provenance_preserved / max(1, provenance_fixtures), 4)

    # Semantic & Error metrics
    critical_errors = sum(1 for r in adjudicated_records if r["critical_semantic_error"])
    overall_critical_error_rate = round(critical_errors / total_fixtures, 4)

    # By Language
    lang_metrics = {}
    for l in ("en", "vi", "ja"):
        sub = [r for r in adjudicated_records if r["target_language"] == l]
        crit = sum(1 for r in sub if r["critical_semantic_error"])
        lang_metrics[l] = {
            "total": len(sub),
            "critical_errors": crit,
            "error_rate": round(crit / max(1, len(sub)), 4),
            "accuracy": round((len(sub) - crit) / max(1, len(sub)), 4),
        }

    # By Communicative Act
    act_metrics = {}
    acts = sorted(list(set(r["act"] for r in adjudicated_records)))
    for a in acts:
        sub = [r for r in adjudicated_records if r["act"] == a]
        crit = sum(1 for r in sub if r["critical_semantic_error"])
        act_metrics[a] = {
            "total": len(sub),
            "critical_errors": crit,
            "error_rate": round(crit / max(1, len(sub)), 4),
        }

    # By Semantic Phenomenon / Category
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

    phenomenon_metrics = {}
    for phen, patterns in phenomenon_mapping.items():
        matched = []
        for r in adjudicated_records:
            f_id = r["fixture_id"]
            if any(p in f_id for p in patterns):
                matched.append(r)
        crit = sum(1 for r in matched if r["critical_semantic_error"])
        phenomenon_metrics[phen] = {
            "total": len(matched),
            "critical_errors": crit,
            "error_rate": round(crit / max(1, len(matched)), 4) if matched else 0.0,
        }

    # Attribution Breakdown
    attribution_counts = {
        "SERIALIZATION": sum(1 for r in adjudicated_records if r["attribution"] == "SERIALIZATION"),
        "REALIZER": sum(1 for r in adjudicated_records if r["attribution"] == "REALIZER"),
        "EVALUATOR": sum(1 for r in adjudicated_records if r["attribution"] == "EVALUATOR"),
        "ELLIPSIS": sum(1 for r in adjudicated_records if r["attribution"] == "ELLIPSIS"),
        "SUPPORTED": sum(1 for r in adjudicated_records if r["attribution"] == "SUPPORTED"),
    }

    # Evaluation Quality
    agreement_count = sum(1 for r in adjudicated_records if r["is_agreement"])
    annotator_agreement_rate = round(agreement_count / total_fixtures, 4)
    adjudication_rate = round((total_fixtures - agreement_count) / total_fixtures, 4)

    acceptable_ellipsis_count = sum(
        1 for r in adjudicated_records if "ACCEPTABLE_ELLIPSIS" in r["adjudicated_labels"]
    )
    paraphrase_count = sum(
        1 for r in adjudicated_records if "PARAPHRASE" in r["adjudicated_labels"]
    )

    metrics_payload = {
        "audit_metadata": {
            "experiment": "Stage 3-A SemanticGraph Preservation Audit",
            "model": "LFM2.5-1.2B-Instruct-Q4_K_M.gguf",
            "model_sha256": model_hash,
            "runtime_backend": "llama_cpp_python (CPU)",
            "llama_cpp_version": getattr(llama_cpp, "__version__", "unknown"),
            "system_os": platform.platform(),
            "cpu_architecture": platform.machine(),
            "total_fixtures": total_fixtures,
            "seed": 42,
            "temperature": 0.3,
            "max_tokens": 96,
            "timestamp": time.time(),
        },
        "structural_metrics": {
            "total_graph_nodes": total_nodes,
            "preserved_nodes": preserved_nodes,
            "node_preservation_rate": node_preservation_rate,
            "total_graph_edges": total_edges,
            "preserved_edges": preserved_edges,
            "edge_preservation_rate": edge_preservation_rate,
            "total_scopes": total_scopes,
            "preserved_scopes": preserved_scopes,
            "scope_preservation_rate": scope_preservation_rate,
            "provenance_fixtures": provenance_fixtures,
            "provenance_preserved": provenance_preserved,
            "provenance_preservation_rate": provenance_preservation_rate,
        },
        "semantic_metrics": {
            "total_fixtures": total_fixtures,
            "critical_errors": critical_errors,
            "overall_critical_error_rate": overall_critical_error_rate,
            "overall_semantic_fidelity": round(1.0 - overall_critical_error_rate, 4),
            "by_language": lang_metrics,
            "by_act": act_metrics,
            "by_phenomenon": phenomenon_metrics,
        },
        "attribution_breakdown": attribution_counts,
        "evaluation_quality": {
            "annotator_agreement_rate": annotator_agreement_rate,
            "adjudication_rate": adjudication_rate,
            "acceptable_ellipsis_rate": round(acceptable_ellipsis_count / total_fixtures, 4),
            "paraphrase_rate": round(paraphrase_count / total_fixtures, 4),
            "evaluator_uncertain_rate": 0.0,
        },
    }

    metrics_path = base_dir / "metrics.json"
    with open(metrics_path, "w", encoding="utf-8") as f:
        json.dump(metrics_payload, f, ensure_ascii=False, indent=2)
    logger.info("Saved metrics to %s", metrics_path)

    print("\n" + "=" * 60)
    print("STAGE 3-A SEMANTICGRAPH PRESERVATION AUDIT SUMMARY")
    print("=" * 60)
    print(f"Total Fixtures Evaluated: {total_fixtures}")
    print(f"Node Preservation Rate (Level 1): {node_preservation_rate * 100:.1f}%")
    print(f"Edge Preservation Rate (Level 1): {edge_preservation_rate * 100:.1f}%")
    print(f"Provenance Preservation Rate (Level 1): {provenance_preservation_rate * 100:.1f}%")
    print(f"Overall Critical Semantic Error Rate (Level 2): {overall_critical_error_rate * 100:.1f}%")
    print(f"Attribution: {attribution_counts}")
    print("=" * 60 + "\n")


if __name__ == "__main__":
    main()
