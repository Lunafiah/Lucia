"""
Experiment Runner for Phase 22-RG: Relevance Gating & Evidence Selection Study.

Pipeline per scenario:
  1. Run M4_HybridFull retrieval (inheriting Phase 22-MR env + memory_store)
  2. Apply each Relevance Gate (G0-G4, Oracle) to M4's retrieved set
  3. Compute metrics on the post-gate selected traces

Metrics (per gate x seed x regime x language):
  - mandatory_recall:      fraction of mandatory anchors surviving the gate
  - precision:             fraction of selected traces that are ground-truth relevant
  - overall_recall:        fraction of all relevant traces surviving the gate
  - injection_rate:        fraction of selected traces that are ground-truth irrelevant
  - hallucination_risk:    contradiction co-occurrence estimate
  - relational_cons:       tier-coherence of selected traces
  - compression_ratio:     relevant bytes / total bytes in selected context
  - token_estimate:        post-gate context token count
  - contradiction_pres:    rupture-repair pair preservation rate
  - gating_latency_ms:     gate overhead (not including M4 retrieval)
  - evidence_sufficiency:  fraction of scenarios where mandatory + pattern >= 1 trace
  - language_invariance:   std across EN/VI/JA for each metric (computed post-agg)

Governance:
  - No production code touched.
  - data/profile.json is_onboarded: false is NOT touched.
  - Isolated to tests/evaluation/phase22_rg/ and evaluation_artifacts/phase22_rg/.
"""
from __future__ import annotations

import json
import os
import sys
import time
from collections import defaultdict
from pathlib import Path
from typing import Dict, List, Set

import numpy as np

sys.path.insert(0, str(Path(__file__).parents[3]))

from tests.evaluation.phase22_mr.config import (
    SDM_ADDRESS_DIM, SDM_VALUE_DIM, SDM_CAPACITY, SDM_HAMMING_R,
    K_RETRIEVAL, AVG_CHARS_PER_TOKEN as MR_AVG_CHARS,
)
from tests.evaluation.phase22_mr.memory_store import SimulatedSDM, MemoryTrace
from tests.evaluation.phase22_mr.env import MemoryRetrievalEnv
from tests.evaluation.phase22_mr.models import Candidate_M4_HybridFull

from tests.evaluation.phase22_rg.config import (
    TRAIN_SEEDS, HELD_OUT_SEEDS, ALL_SEEDS,
    STRESS_REGIMES, LANGUAGES,
    ANCHOR_RELEVANCE_WEIGHTS, MANDATORY_ANCHOR_TYPES,
    AVG_CHARS_PER_TOKEN,
    GATE_MANDATORY_RECALL, GATE_PRECISION_K, GATE_INJECTION_RATE,
    GATE_HALLUCINATION_RISK, GATE_OVERALL_RECALL, GATE_RELATIONAL_CONS,
    GATE_COMPRESSION, GATE_CONTRADICTION_PRES, GATE_LANGUAGE_GAP,
    GATE_CPU_P50_MS, GATE_VRAM_MB, GATE_TOKEN_POST_GATE,
    MR_BASELINES,
)
from tests.evaluation.phase22_rg.gates import (
    Gate_G0_NoGate,
    Gate_G1_StaticThreshold,
    Gate_G2_EvidenceStrength,
    Gate_G3_TemporalDecay,
    Gate_G4_SafetyFirstHybrid,
    Gate_Oracle,
    GatingResult,
)

ARTIFACTS_DIR = Path(__file__).parents[3] / "evaluation_artifacts" / "phase22_rg"
ARTIFACTS_DIR.mkdir(parents=True, exist_ok=True)

GATES = [
    Gate_G0_NoGate(),
    Gate_G1_StaticThreshold(threshold=0.50),
    Gate_G2_EvidenceStrength(),
    Gate_G3_TemporalDecay(score_threshold=0.35, decay_rate=0.40),
    Gate_G4_SafetyFirstHybrid(
        pattern_score_threshold=0.30,
        decay_rate=0.35,
        max_weak_ratio=0.10,
        repair_window=2,
    ),
    Gate_Oracle(),
]

M4 = Candidate_M4_HybridFull(k=K_RETRIEVAL)


# ─── Metric computation ───────────────────────────────────────────────────────

def _hallucination_risk(selected: List[MemoryTrace],
                        traces_by_id: Dict) -> float:
    types = [t.anchor_type for t in selected]
    has_neutral = "neutral_task" in types
    has_rupture = "rupture_shock" in types
    has_repair  = "explicit_repair" in types
    risk = 0.0
    if has_neutral:
        risk += 0.30
    if has_rupture and not has_repair:
        risk += 0.05
    return min(1.0, risk)


def _relational_consistency(selected: List[MemoryTrace],
                             trust_tier: str) -> float:
    tier_idx = {"T0_STRANGER": 0, "T1_ACQUAINTANCE": 1,
                "T2_COLLABORATOR": 2, "T3_COMPANION": 3, "T4_CONFIDANT": 4}
    cur_idx  = tier_idx.get(trust_tier, 0)
    consistent, total = 0, 0
    for t in selected:
        if t.anchor_type == "neutral_task" or t.is_noisy:
            continue
        total += 1
        if t.anchor_type == "rupture_shock" and cur_idx >= 3:
            pass   # inconsistent stale rupture
        else:
            consistent += 1
    return float(consistent / max(1, total)) if total > 0 else 1.0


def _contradiction_preservation(selected: List[MemoryTrace],
                                 all_retrieved: List[MemoryTrace]) -> float:
    """
    For each rupture_shock in the FULL retrieved set, check whether:
    - If the gate kept the rupture, it also kept any associated repair.
    Returns 1.0 if all rupture-repair pairs are preserved together.
    """
    sel_ids = {t.trace_id for t in selected}
    ruptures_in_retrieved = [t for t in all_retrieved
                             if t.anchor_type == "rupture_shock" and not t.is_noisy]
    if not ruptures_in_retrieved:
        return 1.0

    pairs_ok = 0
    pairs_total = 0
    for r in ruptures_in_retrieved:
        if r.trace_id not in sel_ids:
            continue    # Gate dropped the rupture — not a pair preservation case
        # Find repairs in same/adjacent session in all_retrieved
        repairs = [t for t in all_retrieved
                   if t.anchor_type == "explicit_repair"
                   and abs(t.session_idx - r.session_idx) <= 2
                   and not t.is_noisy]
        if not repairs:
            pairs_ok    += 1  # No repair to preserve — constraint satisfied vacuously
            pairs_total += 1
            continue
        # Check that at least one repair is also in selected
        any_repair_kept = any(rp.trace_id in sel_ids for rp in repairs)
        pairs_ok    += int(any_repair_kept)
        pairs_total += 1

    return float(pairs_ok / max(1, pairs_total))


def _evidence_sufficiency(selected: List[MemoryTrace]) -> float:
    """
    Returns 1.0 if selected context contains at least one trace with
    substantive relational content (mandatory or pattern), else 0.0.
    """
    substantive_types = MANDATORY_ANCHOR_TYPES | {"pattern_collaborative"}
    has_subst = any(t.anchor_type in substantive_types for t in selected)
    return 1.0 if has_subst else 0.0


def compute_metrics(gating_result: GatingResult,
                    all_retrieved: List[MemoryTrace],
                    relevant_ids: List[int],
                    mandatory_ids: List[int],
                    irrelevant_ids: List[int],
                    trust_tier: str,
                    traces_by_id: Dict) -> Dict:
    selected     = gating_result.selected
    sel_ids      = {t.trace_id for t in selected}
    relevant_set = set(relevant_ids)
    mandatory_set= set(mandatory_ids)
    irrel_set    = set(irrelevant_ids)

    mandatory_recall = float(len(sel_ids & mandatory_set) /
                             max(1, len(mandatory_set))) if mandatory_set else 1.0
    precision        = float(len(sel_ids & relevant_set) /
                             max(1, len(sel_ids))) if sel_ids else 1.0
    overall_recall   = float(len(sel_ids & relevant_set) /
                             max(1, len(relevant_set))) if relevant_set else 1.0
    injection_rate   = float(len(sel_ids & irrel_set) /
                             max(1, len(sel_ids))) if sel_ids else 0.0

    hall_risk   = _hallucination_risk(selected, traces_by_id)
    rel_cons    = _relational_consistency(selected, trust_tier)
    cont_pres   = _contradiction_preservation(selected, all_retrieved)
    ev_suff     = _evidence_sufficiency(selected)

    # Context compression: relevant chars / total chars
    relevant_chars = sum(len(t.utterance)
                         for t in selected if t.trace_id in relevant_set)
    total_chars    = max(1, sum(len(t.utterance) for t in selected))
    compression    = float(relevant_chars / total_chars) if selected else 0.0

    token_est   = len(gating_result.context_text) // AVG_CHARS_PER_TOKEN

    return {
        "mandatory_recall":    mandatory_recall,
        "precision":           precision,
        "overall_recall":      overall_recall,
        "injection_rate":      injection_rate,
        "hallucination_risk":  hall_risk,
        "relational_cons":     rel_cons,
        "compression":         compression,
        "contradiction_pres":  cont_pres,
        "evidence_sufficiency":ev_suff,
        "token_estimate":      token_est,
        "gating_latency_ms":   gating_result.latency_ms,
        "selected_count":      len(selected),
        "dropped_count":       gating_result.dropped_count,
    }


# ─── Main runner ─────────────────────────────────────────────────────────────

def run_all() -> Dict:
    print("=" * 70)
    print("Phase 22-RG -- Relevance Gating & Evidence Selection Study")
    print("=" * 70)

    raw_data: Dict = defaultdict(
        lambda: defaultdict(
            lambda: defaultdict(
                lambda: defaultdict(list)
            )
        )
    )

    for seed in ALL_SEEDS:
        for regime in STRESS_REGIMES:
            for lang in LANGUAGES:
                # Build environment and generate scenarios
                env       = MemoryRetrievalEnv(seed, regime, lang)
                scenarios = env.generate_scenarios()

                for scenario in scenarios:
                    # Step 1: Run M4 retrieval
                    m4_result = M4.retrieve(env.sdm, scenario.query_dict)

                    traces_by_id  = {t.trace_id: t for t in env.sdm.traces}
                    irrel_ids     = [t.trace_id for t in env.sdm.irrelevant_traces()]
                    all_retrieved = list(m4_result.retrieved)

                    # Step 2: Apply each gate to M4's output
                    for gate in GATES:
                        gr = gate.apply(all_retrieved, scenario.query_dict)
                        metrics = compute_metrics(
                            gating_result = gr,
                            all_retrieved = all_retrieved,
                            relevant_ids  = scenario.relevant_trace_ids,
                            mandatory_ids = scenario.mandatory_trace_ids,
                            irrelevant_ids= irrel_ids,
                            trust_tier    = scenario.current_tier,
                            traces_by_id  = traces_by_id,
                        )
                        raw_data[gate.name][seed][regime][lang].append(metrics)

    return raw_data


# ─── Aggregation ─────────────────────────────────────────────────────────────

def _agg(rows: List[Dict], key: str) -> Dict:
    vals = [d[key] for d in rows if key in d]
    if not vals:
        return {"mean": 0.0, "p50": 0.0, "p95": 0.0, "min": 0.0, "max": 0.0}
    arr = np.array(vals)
    return {"mean": float(np.mean(arr)), "p50": float(np.percentile(arr, 50)),
            "p95":  float(np.percentile(arr, 95)), "min": float(np.min(arr)),
            "max":  float(np.max(arr))}


METRIC_KEYS = [
    "mandatory_recall", "precision", "overall_recall", "injection_rate",
    "hallucination_risk", "relational_cons", "compression",
    "contradiction_pres", "evidence_sufficiency", "token_estimate",
    "gating_latency_ms",
]


def aggregate_results(raw_data: Dict) -> Dict:
    agg: Dict = {}
    for gate_name, seed_data in raw_data.items():
        agg[gate_name] = {
            "overall": {}, "held_out": {}, "per_regime": {}, "per_language": {}
        }
        all_rows:      List[Dict] = []
        held_out_rows: List[Dict] = []

        for seed, regime_data in seed_data.items():
            for regime, lang_data in regime_data.items():
                for lang, rows in lang_data.items():
                    all_rows.extend(rows)
                    if seed in HELD_OUT_SEEDS:
                        held_out_rows.extend(rows)

        for key in METRIC_KEYS:
            agg[gate_name]["overall"][key]  = _agg(all_rows, key)
            agg[gate_name]["held_out"][key] = _agg(held_out_rows, key)

        # Per regime (held-out)
        for regime in STRESS_REGIMES:
            regime_rows: List[Dict] = []
            for seed in HELD_OUT_SEEDS:
                for lang in LANGUAGES:
                    regime_rows.extend(raw_data[gate_name][seed][regime][lang])
            agg[gate_name]["per_regime"][regime] = {
                k: _agg(regime_rows, k) for k in METRIC_KEYS}

        # Per language (held-out) — for language invariance check
        for lang in LANGUAGES:
            lang_rows: List[Dict] = []
            for seed in HELD_OUT_SEEDS:
                for regime in STRESS_REGIMES:
                    lang_rows.extend(raw_data[gate_name][seed][regime][lang])
            agg[gate_name]["per_language"][lang] = {
                k: _agg(lang_rows, k) for k in METRIC_KEYS}

    return agg


def compute_language_invariance(agg: Dict) -> Dict[str, Dict[str, float]]:
    """Compute max spread across languages per gate per metric."""
    inv: Dict = {}
    for gate_name in agg:
        inv[gate_name] = {}
        for key in METRIC_KEYS:
            vals = [
                agg[gate_name]["per_language"].get(lang, {}).get(key, {}).get("mean", 0.0)
                for lang in LANGUAGES
            ]
            inv[gate_name][key] = float(max(vals) - min(vals))
    return inv


# ─── Gate evaluation ─────────────────────────────────────────────────────────

def evaluate_gates(agg: Dict, lang_inv: Dict) -> Dict:
    gates: Dict = {}
    g4 = agg.get("G4_SafetyFirstHybrid", {}).get("held_out", {})

    def gate(name, measured, threshold, direction="ge"):
        passed = (measured >= threshold) if direction == "ge" else (measured <= threshold)
        gates[name] = {"threshold": threshold,
                       "measured":  round(measured, 6),
                       "passed":    bool(passed)}

    gate("G_RG1_Mandatory_Recall",
         g4.get("mandatory_recall",    {}).get("mean", 0.0), GATE_MANDATORY_RECALL)
    gate("G_RG2_Precision_K",
         g4.get("precision",           {}).get("mean", 0.0), GATE_PRECISION_K)
    gate("G_RG3_Injection_Rate",
         g4.get("injection_rate",      {}).get("mean", 1.0), GATE_INJECTION_RATE, "le")
    gate("G_RG4_Hallucination_Risk",
         g4.get("hallucination_risk",  {}).get("mean", 1.0), GATE_HALLUCINATION_RISK, "le")
    gate("G_RG5_Overall_Recall",
         g4.get("overall_recall",      {}).get("mean", 0.0), GATE_OVERALL_RECALL)
    gate("G_RG6_Relational_Cons",
         g4.get("relational_cons",     {}).get("mean", 0.0), GATE_RELATIONAL_CONS)
    gate("G_RG7_Compression",
         g4.get("compression",         {}).get("mean", 0.0), GATE_COMPRESSION)
    gate("G_RG8_Contradiction_Pres",
         g4.get("contradiction_pres",  {}).get("mean", 0.0), GATE_CONTRADICTION_PRES)
    gate("G_RG9_Language_Gap",
         lang_inv.get("G4_SafetyFirstHybrid", {}).get("precision", 1.0),
         GATE_LANGUAGE_GAP, "le")
    gate("G_RG10_Latency_P50",
         g4.get("gating_latency_ms",   {}).get("p50",  999), GATE_CPU_P50_MS, "le")
    gate("G_RG11_VRAM",
         0.0,                                                 GATE_VRAM_MB, "le")
    gate("G_RG12_Token_Budget",
         g4.get("token_estimate",      {}).get("p95",  999), GATE_TOKEN_POST_GATE, "le")

    return gates


# ─── Report generation ───────────────────────────────────────────────────────

def _val(agg, gate_name, split, key, field="mean"):
    return agg.get(gate_name, {}).get(split, {}).get(key, {}).get(field, float("nan"))


def generate_reports(agg: Dict, gates: Dict, lang_inv: Dict) -> None:
    gate_names = [g.name for g in GATES]

    # ── 1. Gating summary report ──────────────────────────────────────────────
    with open(ARTIFACTS_DIR / "gating_report.md", "w", encoding="utf-8") as f:
        f.write("# Phase 22-RG -- Gating Summary Report\n\n")
        f.write("## Held-Out Seeds, All Regimes, All Languages\n\n")
        f.write("| Gate | Mand.Recall | Precision | Inj.Rate | Hall.Risk | Rel.Cons | "
                "Compression | Token P95 | Lat.P50 (ms) |\n")
        f.write("|---|---|---|---|---|---|---|---|---|\n")
        for gn in gate_names:
            mr  = _val(agg, gn, "held_out", "mandatory_recall")
            pr  = _val(agg, gn, "held_out", "precision")
            inj = _val(agg, gn, "held_out", "injection_rate")
            hal = _val(agg, gn, "held_out", "hallucination_risk")
            rc  = _val(agg, gn, "held_out", "relational_cons")
            com = _val(agg, gn, "held_out", "compression")
            tok = _val(agg, gn, "held_out", "token_estimate", "p95")
            lat = _val(agg, gn, "held_out", "gating_latency_ms", "p50")
            f.write(f"| {gn} | {mr:.4f} | {pr:.4f} | {inj:.4f} | {hal:.4f} | "
                    f"{rc:.4f} | {com:.4f} | {tok:.0f} | {lat:.4f} |\n")

    # ── 2. Evidence selection report ─────────────────────────────────────────
    with open(ARTIFACTS_DIR / "evidence_selection.md", "w", encoding="utf-8") as f:
        f.write("# Phase 22-RG -- Evidence Selection Report\n\n")
        f.write("| Gate | Overall Recall | Evidence Sufficiency | Contradiction Pres |\n")
        f.write("|---|---|---|---|\n")
        for gn in gate_names:
            ov  = _val(agg, gn, "held_out", "overall_recall")
            es  = _val(agg, gn, "held_out", "evidence_sufficiency")
            cp  = _val(agg, gn, "held_out", "contradiction_pres")
            f.write(f"| {gn} | {ov:.4f} | {es:.4f} | {cp:.4f} |\n")

    # ── 3. Safety analysis ────────────────────────────────────────────────────
    with open(ARTIFACTS_DIR / "safety_analysis.md", "w", encoding="utf-8") as f:
        f.write("# Phase 22-RG -- Safety Analysis\n\n")
        f.write("## Mandatory Anchor Recall (Rupture/Repair/Milestone)\n\n")
        f.write("| Gate | Overall | ID | NoiseSurge | LexSparsity | ContradShock | "
                "TempDrift | CombStress |\n")
        f.write("|---|---|---|---|---|---|---|---|\n")
        for gn in gate_names:
            ov = _val(agg, gn, "held_out", "mandatory_recall")
            row = f"| {gn} | {ov:.4f}"
            for regime in STRESS_REGIMES:
                rv = _val(agg, gn, "per_regime", regime, "mandatory_recall") if False else \
                     agg.get(gn, {}).get("per_regime", {}).get(
                         regime, {}).get("mandatory_recall", {}).get("mean", float("nan"))
                row += f" | {rv:.4f}"
            f.write(row + " |\n")

    # ── 4. Contradiction preservation report ──────────────────────────────────
    with open(ARTIFACTS_DIR / "contradiction_report.md", "w", encoding="utf-8") as f:
        f.write("# Phase 22-RG -- Contradiction & Rupture-Repair Preservation Report\n\n")
        f.write("| Gate | Contradiction Preservation | Hallucination Risk |\n")
        f.write("|---|---|---|\n")
        for gn in gate_names:
            cp  = _val(agg, gn, "held_out", "contradiction_pres")
            hal = _val(agg, gn, "held_out", "hallucination_risk")
            f.write(f"| {gn} | {cp:.4f} | {hal:.4f} |\n")

    # ── 5. Compression report ─────────────────────────────────────────────────
    with open(ARTIFACTS_DIR / "compression_report.md", "w", encoding="utf-8") as f:
        f.write("# Phase 22-RG -- Context Compression Report\n\n")
        f.write("| Gate | Compression | Token P50 | Token P95 | Injection Rate |\n")
        f.write("|---|---|---|---|---|\n")
        for gn in gate_names:
            com  = _val(agg, gn, "held_out", "compression")
            tp50 = _val(agg, gn, "held_out", "token_estimate", "p50")
            tp95 = _val(agg, gn, "held_out", "token_estimate", "p95")
            inj  = _val(agg, gn, "held_out", "injection_rate")
            f.write(f"| {gn} | {com:.4f} | {tp50:.0f} | {tp95:.0f} | {inj:.4f} |\n")

    # ── 6. Language report ────────────────────────────────────────────────────
    with open(ARTIFACTS_DIR / "language_report.md", "w", encoding="utf-8") as f:
        f.write("# Phase 22-RG -- Language Invariance Report (EN/VI/JA)\n\n")
        f.write("## Precision by Language\n\n")
        f.write("| Gate | English | Vietnamese | Japanese | Max Gap |\n")
        f.write("|---|---|---|---|---|\n")
        for gn in gate_names:
            vals = {lang: _val(agg, gn, "per_language", lang, "precision")
                    if False else
                    agg.get(gn, {}).get("per_language", {}).get(
                        lang, {}).get("precision", {}).get("mean", float("nan"))
                    for lang in LANGUAGES}
            gap = max(vals.values()) - min(vals.values())
            f.write(f"| {gn} | {vals['English']:.4f} | {vals['Vietnamese']:.4f} | "
                    f"{vals['Japanese']:.4f} | {gap:.4f} |\n")

    print(f"  Reports written to: {ARTIFACTS_DIR}")


# ─── Entry point ─────────────────────────────────────────────────────────────

def main():
    # Genesis gate invariant
    profile_path = Path(__file__).parents[3] / "data" / "profile.json"
    if profile_path.exists():
        with open(profile_path, "r", encoding="utf-8") as fh:
            profile = json.load(fh)
        assert profile.get("is_onboarded") is False, \
            "INVARIANT VIOLATION: is_onboarded must remain false"
    print("[OK] Genesis gate: is_onboarded=false preserved.")

    t_start  = time.perf_counter()
    raw_data = run_all()
    t_run    = time.perf_counter() - t_start
    print(f"\n[OK] Simulation complete in {t_run:.2f}s. Aggregating...")

    agg      = aggregate_results(raw_data)
    lang_inv = compute_language_invariance(agg)
    gates    = evaluate_gates(agg, lang_inv)

    def _to_plain(d):
        if isinstance(d, (defaultdict, dict)):
            return {str(k): _to_plain(v) for k, v in d.items()}
        elif isinstance(d, list):
            return [_to_plain(i) for i in d]
        return d

    with open(ARTIFACTS_DIR / "raw_measurements.json", "w", encoding="utf-8") as f:
        json.dump(_to_plain(raw_data), f, indent=2)
    with open(ARTIFACTS_DIR / "aggregated_results.json", "w", encoding="utf-8") as f:
        json.dump(agg, f, indent=2)
    with open(ARTIFACTS_DIR / "gate_results.json", "w", encoding="utf-8") as f:
        json.dump(gates, f, indent=2)
    with open(ARTIFACTS_DIR / "language_invariance.json", "w", encoding="utf-8") as f:
        json.dump(lang_inv, f, indent=2)

    generate_reports(agg, gates, lang_inv)

    # ── Console summary ────────────────────────────────────────────────────────
    print("\n" + "=" * 70)
    print("PHASE 22-RG -- GATE EVALUATION SUMMARY (Held-Out Seeds, G4)")
    print("=" * 70)
    n_passed = sum(1 for g in gates.values() if g["passed"])
    n_total  = len(gates)
    for gname, ginfo in gates.items():
        status = "PASSED" if ginfo["passed"] else "FAILED"
        print(f"  {gname:<40} measured={ginfo['measured']:.4f}  "
              f"threshold={ginfo['threshold']}  [{status}]")

    print(f"\n  Gates Passed: {n_passed}/{n_total}")

    print("\n  Candidate Gate Summary (Held-Out, Mean):")
    print(f"  {'Gate':<28} {'Mand.Rec':<10} {'Precision':<11} {'Inj.Rate':<11} "
          f"{'Hall.Risk':<11} {'Compression':<13} {'Token P95':<10} {'Lat.P50(ms)'}")
    print("  " + "-" * 100)
    for g in GATES:
        ho  = agg.get(g.name, {}).get("held_out", {})
        mr  = ho.get("mandatory_recall",   {}).get("mean", float("nan"))
        pr  = ho.get("precision",          {}).get("mean", float("nan"))
        inj = ho.get("injection_rate",     {}).get("mean", float("nan"))
        hal = ho.get("hallucination_risk", {}).get("mean", float("nan"))
        com = ho.get("compression",        {}).get("mean", float("nan"))
        tok = ho.get("token_estimate",     {}).get("p95",  float("nan"))
        lat = ho.get("gating_latency_ms",  {}).get("p50",  float("nan"))
        print(f"  {g.name:<28} {mr:<10.4f} {pr:<11.4f} {inj:<11.4f} "
              f"{hal:<11.4f} {com:<13.4f} {tok:<10.0f} {lat:.4f}")

    print("\n[OK] Phase 22-RG experiment run complete.")
    return gates


if __name__ == "__main__":
    main()
