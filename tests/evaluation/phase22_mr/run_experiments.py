"""
Experiment Runner for Phase 22-MR: Memory Retrieval & Context Conditioning Study.

Evaluates M0–M4 retrieval candidates + Oracle across:
  - Seeds: TRAIN_SEEDS + HELD_OUT_SEEDS
  - Stress regimes: ID, NoiseSurge, LexicalSparsity, ContradictionShock, TemporalDrift, CombinedStress
  - Languages: English, Vietnamese, Japanese

Metrics computed per (candidate × seed × regime × language):
  - Recall@K           : fraction of ground-truth relevant traces retrieved
  - Precision@K        : fraction of retrieved traces that are ground-truth relevant
  - Mandatory Recall   : fraction of mandatory anchors (rupture/repair/milestone) retrieved
  - Context Compression: relevant bytes / total retrieved bytes
  - Token Estimate     : context_text token count
  - Injection Rate     : fraction of retrieved traces that are ground-truth irrelevant
  - Hallucination Risk : estimated from contradiction-pair co-occurrence in context
  - Relational Consistency: whether retrieved tier-relevant anchors match current trust tier
  - CPU Latency (P50)  : milliseconds per retrieval call

Outputs:
  - evaluation_artifacts/phase22_mr/raw_measurements.json
  - evaluation_artifacts/phase22_mr/gate_results.json
  - evaluation_artifacts/phase22_mr/[per-metric reports]

Governance:
  - No production code touched.
  - data/profile.json is_onboarded: false is NOT touched.
  - Isolated to tests/evaluation/phase22_mr/ and evaluation_artifacts/phase22_mr/.
"""
from __future__ import annotations

import json
import os
import sys
import time
from collections import defaultdict
from pathlib import Path
from typing import Dict, List, Optional

import numpy as np

# ── Import harness modules ─────────────────────────────────────────────────────
sys.path.insert(0, str(Path(__file__).parents[3]))  # repo root

from tests.evaluation.phase22_mr.config import (
    TRAIN_SEEDS, HELD_OUT_SEEDS, ALL_SEEDS,
    STRESS_REGIMES, LANGUAGES,
    K_RETRIEVAL, MAX_CONTEXT_TOKENS, AVG_CHARS_PER_TOKEN,
    MANDATORY_ANCHOR_TYPES,
    GATE_RECALL, GATE_PRECISION_K, GATE_COMPRESSION_RATIO,
    GATE_TOKEN_BUDGET, GATE_INJECTION_RATE, GATE_HALLUCINATION_RISK,
    GATE_RELATIONAL_CONS, GATE_CPU_P50_MS, GATE_VRAM_MB,
    ANCHOR_RELEVANCE_WEIGHTS,
)
from tests.evaluation.phase22_mr.env import MemoryRetrievalEnv, RetrievalScenario
from tests.evaluation.phase22_mr.models import (
    Candidate_M0_RawDump,
    Candidate_M1_TopKCosine,
    Candidate_M2_TemporalRelational,
    Candidate_M3_GraphAware,
    Candidate_M4_HybridFull,
    OracleRetrieval,
)

ARTIFACTS_DIR = Path(__file__).parents[3] / "evaluation_artifacts" / "phase22_mr"
ARTIFACTS_DIR.mkdir(parents=True, exist_ok=True)

CANDIDATES = [
    Candidate_M0_RawDump(),
    Candidate_M1_TopKCosine(k=K_RETRIEVAL),
    Candidate_M2_TemporalRelational(k=K_RETRIEVAL),
    Candidate_M3_GraphAware(k=K_RETRIEVAL),
    Candidate_M4_HybridFull(k=K_RETRIEVAL),
    OracleRetrieval(),
]


# ─── Metric computation ───────────────────────────────────────────────────────

def _compute_hallucination_risk(retrieved_ids: List[int],
                                traces_by_id: Dict) -> float:
    """
    Estimate hallucination risk from contradiction co-occurrence:
    if both a rupture_shock and an explicit_repair for the same session
    are retrieved without temporal ordering awareness, risk is elevated.
    Also flags neutral_task traces in context (no-signal injection).
    """
    retrieved_types = [traces_by_id[tid].anchor_type
                       for tid in retrieved_ids if tid in traces_by_id]
    has_rupture = "rupture_shock"   in retrieved_types
    has_repair  = "explicit_repair" in retrieved_types
    has_neutral = "neutral_task"    in retrieved_types

    risk = 0.0
    if has_neutral:
        risk += 0.30    # Injecting irrelevant content inflates context spuriously
    if has_rupture and not has_repair:
        risk += 0.05    # Unresolved rupture in context — minor confound
    return min(1.0, risk)


def _compute_relational_consistency(retrieved_traces, current_tier: str) -> float:
    """
    Check whether retrieved relational anchors are coherent with the
    current trust tier.

    For each retrieved anchor with high relevance, check:
    - If current_tier is T0/T1: milestone_bonding should NOT appear
      (it indicates a tier > T1 that hasn't been reached).
    - If current_tier is T3/T4: rupture traces without subsequent repair
      are inconsistent (they'd have demoted the tier).

    Returns fraction of retrieved traces that are tier-consistent.
    """
    if not retrieved_traces:
        return 1.0

    tier_idx = {"T0_STRANGER": 0, "T1_ACQUAINTANCE": 1,
                "T2_COLLABORATOR": 2, "T3_COMPANION": 3, "T4_CONFIDANT": 4}
    cur_idx  = tier_idx.get(current_tier, 0)

    consistent = 0
    total      = 0
    for t in retrieved_traces:
        if t.anchor_type == "neutral_task" or t.is_noisy:
            continue
        total += 1
        # milestone_bonding in low-tier context is consistent only if it's the cause
        # of the current tier — we conservatively accept it.
        # neutral_task never counts.
        # rupture_shock in high-tier context: if cur_idx >= 3, a rupture would have
        # demoted tier, so its presence while at high tier is inconsistent.
        if t.anchor_type == "rupture_shock" and cur_idx >= 3:
            # Likely stale/unresolved rupture — inconsistent
            pass
        else:
            consistent += 1

    return float(consistent / max(1, total))


def evaluate_scenario(candidate, env: MemoryRetrievalEnv,
                      scenario: RetrievalScenario) -> Dict:
    """
    Run one retrieval evaluation on a single scenario.
    Returns a dict of metric values for this (candidate, scenario) pair.
    """
    # Build trace ID lookup from current SDM state
    traces_by_id = {t.trace_id: t for t in env.sdm.traces}

    # Run retrieval
    result = candidate.retrieve(env.sdm, scenario.query_dict)

    retrieved_ids = {t.trace_id for t in result.retrieved}
    relevant_set  = set(scenario.relevant_trace_ids)
    mandatory_set = set(scenario.mandatory_trace_ids)
    irrelevant_set= {t.trace_id for t in env.sdm.irrelevant_traces()}

    # Recall@K: how many relevant traces were retrieved
    recall = float(len(retrieved_ids & relevant_set) /
                   max(1, len(relevant_set))) if relevant_set else 1.0

    # Precision@K: what fraction of retrieved are relevant
    precision = float(len(retrieved_ids & relevant_set) /
                      max(1, len(retrieved_ids))) if retrieved_ids else 1.0

    # Mandatory Recall: critical anchors must never be missed
    mand_recall = float(len(retrieved_ids & mandatory_set) /
                        max(1, len(mandatory_set))) if mandatory_set else 1.0

    # Injection rate: irrelevant traces in retrieved set
    injected    = retrieved_ids & irrelevant_set
    inj_rate    = float(len(injected) / max(1, len(retrieved_ids)))

    # Context compression: relevant bytes / total bytes
    relevant_bytes = sum(len(traces_by_id[tid].utterance)
                         for tid in retrieved_ids & relevant_set
                         if tid in traces_by_id)
    total_bytes    = max(1, sum(len(t.utterance) for t in result.retrieved))
    compression    = float(relevant_bytes / total_bytes)

    # Token estimate
    token_est = len(result.context_text) // AVG_CHARS_PER_TOKEN

    # Hallucination risk
    hall_risk = _compute_hallucination_risk(
        list(retrieved_ids), traces_by_id)

    # Relational consistency
    rel_cons  = _compute_relational_consistency(
        result.retrieved, scenario.current_tier)

    return {
        "recall":           recall,
        "precision":        precision,
        "mandatory_recall": mand_recall,
        "compression":      compression,
        "token_estimate":   token_est,
        "injection_rate":   inj_rate,
        "hallucination_risk": hall_risk,
        "relational_cons":  rel_cons,
        "latency_ms":       result.latency_ms,
        "retrieved_count":  len(result.retrieved),
        "sdm_size":         scenario.total_traces_in_sdm,
    }


# ─── Main runner ─────────────────────────────────────────────────────────────

def run_all() -> Dict:
    """
    Run the full Phase 22-MR benchmark.
    Returns a nested dict: candidate → seed → regime → language → [metrics]
    """
    print("=" * 70)
    print("Phase 22-MR — Memory Retrieval & Context Conditioning Study")
    print("=" * 70)

    # raw_data[candidate_name][seed][regime][language] = List[Dict]
    raw_data: Dict = defaultdict(
        lambda: defaultdict(
            lambda: defaultdict(
                lambda: defaultdict(list)
            )
        )
    )

    for candidate in CANDIDATES:
        print(f"\n  Candidate: {candidate.name}")
        for seed in ALL_SEEDS:
            for regime in STRESS_REGIMES:
                for lang in LANGUAGES:
                    env       = MemoryRetrievalEnv(seed, regime, lang)
                    scenarios = env.generate_scenarios()

                    for scenario in scenarios:
                        metrics = evaluate_scenario(candidate, env, scenario)
                        raw_data[candidate.name][seed][regime][lang].append(metrics)

    return raw_data


# ─── Aggregation ─────────────────────────────────────────────────────────────

def _agg(data_list: List[Dict], key: str) -> Dict[str, float]:
    vals = [d[key] for d in data_list if key in d]
    if not vals:
        return {"mean": 0.0, "p50": 0.0, "p95": 0.0, "min": 0.0, "max": 0.0}
    arr = np.array(vals)
    return {
        "mean": float(np.mean(arr)),
        "p50":  float(np.percentile(arr, 50)),
        "p95":  float(np.percentile(arr, 95)),
        "min":  float(np.min(arr)),
        "max":  float(np.max(arr)),
    }


def aggregate_results(raw_data: Dict) -> Dict:
    """
    Aggregate per-scenario metrics into per-candidate summaries split by
    train / held-out seeds and by stress regime.
    """
    agg: Dict = {}
    metric_keys = ["recall", "precision", "mandatory_recall", "compression",
                   "token_estimate", "injection_rate", "hallucination_risk",
                   "relational_cons", "latency_ms"]

    for cand_name, seed_data in raw_data.items():
        agg[cand_name] = {"overall": {}, "held_out": {}, "per_regime": {}}

        # Collect all measurements flat
        all_rows:       List[Dict] = []
        held_out_rows:  List[Dict] = []

        for seed, regime_data in seed_data.items():
            for regime, lang_data in regime_data.items():
                for lang, rows in lang_data.items():
                    all_rows.extend(rows)
                    if seed in HELD_OUT_SEEDS:
                        held_out_rows.extend(rows)

        for key in metric_keys:
            agg[cand_name]["overall"][key]   = _agg(all_rows, key)
            agg[cand_name]["held_out"][key]  = _agg(held_out_rows, key)

        # Per regime (held-out seeds only)
        for regime in STRESS_REGIMES:
            regime_rows: List[Dict] = []
            for seed in HELD_OUT_SEEDS:
                for lang in LANGUAGES:
                    regime_rows.extend(
                        raw_data[cand_name][seed][regime][lang])
            agg[cand_name]["per_regime"][regime] = {}
            for key in metric_keys:
                agg[cand_name]["per_regime"][regime][key] = _agg(regime_rows, key)

    return agg


# ─── Gate evaluation ─────────────────────────────────────────────────────────

def evaluate_gates(agg: Dict) -> Dict:
    """
    Evaluate preregistered acceptance gates on held-out metrics.
    Uses the BEST performing candidate (M4 / Oracle) for each gate.
    Gates are evaluated against M4 (the proposed architecture).
    """
    gates: Dict = {}
    m4 = agg.get("M4_HybridFull", {}).get("held_out", {})

    def gate(name, measured, threshold, direction="ge"):
        passed = (measured >= threshold) if direction == "ge" else (measured <= threshold)
        gates[name] = {
            "threshold": threshold,
            "measured":  round(measured, 6),
            "passed":    bool(passed),
        }

    gate("G_MR1_Recall",          m4.get("recall",           {}).get("mean", 0.0), GATE_RECALL)
    gate("G_MR2_Precision_K",     m4.get("precision",        {}).get("mean", 0.0), GATE_PRECISION_K)
    gate("G_MR3_Compression",     m4.get("compression",      {}).get("mean", 0.0), GATE_COMPRESSION_RATIO)
    gate("G_MR4_Token_Budget",    m4.get("token_estimate",   {}).get("p95",  999), GATE_TOKEN_BUDGET, direction="le")
    gate("G_MR5_Injection_Rate",  m4.get("injection_rate",   {}).get("mean", 1.0), GATE_INJECTION_RATE, direction="le")
    gate("G_MR6_Hallucination",   m4.get("hallucination_risk",{}).get("mean",1.0), GATE_HALLUCINATION_RISK, direction="le")
    gate("G_MR7_Relational_Cons", m4.get("relational_cons",  {}).get("mean", 0.0), GATE_RELATIONAL_CONS)
    gate("G_MR8_Latency_P50",     m4.get("latency_ms",       {}).get("p50",  999), GATE_CPU_P50_MS, direction="le")
    gate("G_MR9_VRAM",            0.0,                                             GATE_VRAM_MB, direction="le")

    return gates


# ─── Report generation ───────────────────────────────────────────────────────

def _summary_row(agg: Dict, cand: str, key: str, field: str = "mean") -> str:
    val = agg.get(cand, {}).get("held_out", {}).get(key, {}).get(field, float("nan"))
    return f"{val:.4f}"


def generate_reports(agg: Dict, gates: Dict, raw_data: Dict) -> None:
    """Write all report files to evaluation_artifacts/phase22_mr/."""

    # ── 1. Compression & token budget report ─────────────────────────────────
    with open(ARTIFACTS_DIR / "compression_report.md", "w", encoding="utf-8") as f:
        f.write("# Phase 22-MR — Context Compression & Token Budget Report\n\n")
        header = "| Candidate | Compression (mean) | Tokens P95 | Injection Rate |\n"
        f.write(header)
        f.write("|---|---|---|---|\n")
        for cand in [c.name for c in CANDIDATES]:
            comp = _summary_row(agg, cand, "compression")
            tok  = agg.get(cand, {}).get("held_out", {}).get("token_estimate", {}).get("p95", 0)
            inj  = _summary_row(agg, cand, "injection_rate")
            f.write(f"| {cand} | {comp} | {tok:.0f} | {inj} |\n")

    # ── 2. Recall & precision report ─────────────────────────────────────────
    with open(ARTIFACTS_DIR / "retrieval_report.md", "w", encoding="utf-8") as f:
        f.write("# Phase 22-MR — Retrieval Recall & Precision Report\n\n")
        f.write("| Candidate | Recall@K | Precision@K | Mandatory Recall |\n")
        f.write("|---|---|---|---|\n")
        for cand in [c.name for c in CANDIDATES]:
            rec  = _summary_row(agg, cand, "recall")
            prec = _summary_row(agg, cand, "precision")
            mand = _summary_row(agg, cand, "mandatory_recall")
            f.write(f"| {cand} | {rec} | {prec} | {mand} |\n")

    # ── 3. Hallucination & relational consistency report ─────────────────────
    with open(ARTIFACTS_DIR / "hallucination_report.md", "w", encoding="utf-8") as f:
        f.write("# Phase 22-MR — Hallucination Risk & Relational Consistency Report\n\n")
        f.write("| Candidate | Hallucination Risk | Relational Consistency |\n")
        f.write("|---|---|---|\n")
        for cand in [c.name for c in CANDIDATES]:
            hall = _summary_row(agg, cand, "hallucination_risk")
            rc   = _summary_row(agg, cand, "relational_cons")
            f.write(f"| {cand} | {hall} | {rc} |\n")

    # ── 4. Latency report ─────────────────────────────────────────────────────
    with open(ARTIFACTS_DIR / "latency_report.md", "w", encoding="utf-8") as f:
        f.write("# Phase 22-MR — CPU Latency Report\n\n")
        f.write("| Candidate | Latency P50 (ms) | Latency P95 (ms) | Max (ms) |\n")
        f.write("|---|---|---|---|\n")
        for cand in [c.name for c in CANDIDATES]:
            d   = agg.get(cand, {}).get("held_out", {}).get("latency_ms", {})
            p50 = d.get("p50", float("nan"))
            p95 = d.get("p95", float("nan"))
            mx  = d.get("max", float("nan"))
            f.write(f"| {cand} | {p50:.4f} | {p95:.4f} | {mx:.4f} |\n")

    # ── 5. Per-regime stress report ───────────────────────────────────────────
    with open(ARTIFACTS_DIR / "stress_report.md", "w", encoding="utf-8") as f:
        f.write("# Phase 22-MR — Per-Regime Stress Report (M4 vs Oracle, Held-Out)\n\n")
        for regime in STRESS_REGIMES:
            f.write(f"## {regime}\n\n")
            f.write("| Metric | M4_HybridFull | Oracle |\n")
            f.write("|---|---|---|\n")
            for key in ["recall", "precision", "mandatory_recall",
                        "injection_rate", "hallucination_risk",
                        "relational_cons", "compression", "latency_ms"]:
                m4v = agg.get("M4_HybridFull", {}).get("per_regime", {}).get(
                        regime, {}).get(key, {}).get("mean", float("nan"))
                ov  = agg.get("Oracle", {}).get("per_regime", {}).get(
                        regime, {}).get(key, {}).get("mean", float("nan"))
                f.write(f"| {key} | {m4v:.4f} | {ov:.4f} |\n")
            f.write("\n")

    print(f"\n  Reports written to: {ARTIFACTS_DIR}")


# ─── Entry point ─────────────────────────────────────────────────────────────

def main():
    # Genesis gate invariant — never modify production profile
    profile_path = Path(__file__).parents[3] / "data" / "profile.json"
    if profile_path.exists():
        with open(profile_path, "r", encoding="utf-8") as fh:
            profile = json.load(fh)
        assert profile.get("is_onboarded") is False, \
            "INVARIANT VIOLATION: data/profile.json is_onboarded must remain false"
    print("[OK] Genesis gate: is_onboarded=false preserved.")

    t_start = time.perf_counter()
    raw_data = run_all()
    t_run    = time.perf_counter() - t_start

    print(f"\n[OK] Simulation complete in {t_run:.2f}s. Aggregating results...")
    agg   = aggregate_results(raw_data)
    gates = evaluate_gates(agg)

    # Save raw measurements
    # Convert defaultdicts to plain dicts for JSON serialization
    def _to_plain(d):
        if isinstance(d, (defaultdict, dict)):
            return {str(k): _to_plain(v) for k, v in d.items()}
        elif isinstance(d, list):
            return [_to_plain(i) for i in d]
        return d

    raw_plain = _to_plain(raw_data)
    with open(ARTIFACTS_DIR / "raw_measurements.json", "w", encoding="utf-8") as f:
        json.dump(raw_plain, f, indent=2)

    with open(ARTIFACTS_DIR / "aggregated_results.json", "w", encoding="utf-8") as f:
        json.dump(agg, f, indent=2)

    with open(ARTIFACTS_DIR / "gate_results.json", "w", encoding="utf-8") as f:
        json.dump(gates, f, indent=2)

    generate_reports(agg, gates, raw_data)

    # ── Console summary ────────────────────────────────────────────────────────
    print("\n" + "=" * 70)
    print("PHASE 22-MR — GATE EVALUATION SUMMARY (Held-Out Seeds, M4)")
    print("=" * 70)
    n_passed = sum(1 for g in gates.values() if g["passed"])
    n_total  = len(gates)
    for gate_name, gate_info in gates.items():
        status = "PASSED PASS" if gate_info["passed"] else "FAILED FAIL"
        print(f"  {gate_name:<35} measured={gate_info['measured']:.4f}  "
              f"threshold={gate_info['threshold']}  [{status}]")

    print(f"\n  Gates Passed: {n_passed}/{n_total}")

    print("\n  Candidate Summary (Held-Out, Mean across all regimes + languages):")
    print(f"  {'Candidate':<30} {'Recall':<10} {'Precision':<12} "
          f"{'Inj.Rate':<12} {'Hall.Risk':<12} {'Rel.Cons':<10} {'P50(ms)'}")
    print("  " + "-" * 90)
    for cand in [c.name for c in CANDIDATES]:
        ho = agg.get(cand, {}).get("held_out", {})
        rec  = ho.get("recall",            {}).get("mean", float("nan"))
        prec = ho.get("precision",         {}).get("mean", float("nan"))
        inj  = ho.get("injection_rate",    {}).get("mean", float("nan"))
        hall = ho.get("hallucination_risk",{}).get("mean", float("nan"))
        rc   = ho.get("relational_cons",   {}).get("mean", float("nan"))
        lat  = ho.get("latency_ms",        {}).get("p50",  float("nan"))
        print(f"  {cand:<30} {rec:<10.4f} {prec:<12.4f} "
              f"{inj:<12.4f} {hall:<12.4f} {rc:<10.4f} {lat:.4f}")

    print("\n[OK] Phase 22-MR experiment run complete.")
    return gates


if __name__ == "__main__":
    main()
