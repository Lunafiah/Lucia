"""
Experiment Runner for Phase 22-CC: Context Conditioning & Relational Response Study.

Pipeline per scenario:
  1. Generate scenario (tier, guarded state, relational events) from env
  2. Run M4 retrieval (from Phase 22-MR)
  3. Apply G4 gate (from Phase 22-RG) -> G4-filtered context
  4. For each conditioning candidate C0-C4 + Oracle:
       a. Format context according to candidate's conditioning strategy
       b. Run SLM simulator to get SLMResponse
       c. Compute response-quality metrics
  5. Aggregate across seeds x regimes x languages

Key: G_CC12 (C0 vs C2 delta >= 0.10) determines whether context conditioning
is actually utilized. If delta < 0.10, the bottleneck is NOT conditioning quality
but rather SLM capability or the memory-to-language interface design.

Governance:
  - No production code touched.
  - data/profile.json is_onboarded: false is NOT touched.
  - GPU VRAM = 0. All computation is CPU-only rule-based simulation.
  - Isolated to tests/evaluation/phase22_cc/ and evaluation_artifacts/phase22_cc/.
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

from tests.evaluation.phase22_mr.config import K_RETRIEVAL
from tests.evaluation.phase22_mr.memory_store import SimulatedSDM, MemoryTrace
from tests.evaluation.phase22_mr.env import MemoryRetrievalEnv
from tests.evaluation.phase22_mr.models import Candidate_M4_HybridFull
from tests.evaluation.phase22_rg.gates import Gate_G4_SafetyFirstHybrid, _compress

from tests.evaluation.phase22_cc.config import (
    TRAIN_SEEDS, HELD_OUT_SEEDS, ALL_SEEDS,
    STRESS_REGIMES, LANGUAGES, TRUST_TIERS, TIER_INDEX,
    ANCHOR_RELEVANCE_WEIGHTS, MANDATORY_ANCHOR_TYPES,
    AVG_CHARS_PER_TOKEN,
    GATE_TIER_CONSISTENCY, GATE_OVER_INFERENCE, GATE_UNSUPPORTED_CLAIM,
    GATE_EVIDENCE_ATTRIBUTION, GATE_CONTRADICTION_HANDLING,
    GATE_RUPTURE_REPAIR_CONS, GATE_MEMORY_UTILIZATION,
    GATE_LANGUAGE_GAP, GATE_CONTEXT_WINDOW, GATE_CPU_P50_MS,
    GATE_VRAM_MB, GATE_C0_C2_DELTA,
    RG_BASELINES,
)
from tests.evaluation.phase22_cc.simulator import SLMSimulator, SLMResponse

ARTIFACTS_DIR = Path(__file__).parents[3] / "evaluation_artifacts" / "phase22_cc"
ARTIFACTS_DIR.mkdir(parents=True, exist_ok=True)

CANDIDATES = ["C0", "C1", "C2", "C3", "C4", "Oracle"]

M4  = Candidate_M4_HybridFull(k=K_RETRIEVAL)
G4  = Gate_G4_SafetyFirstHybrid(
    pattern_score_threshold=0.30,
    decay_rate=0.35,
    max_weak_ratio=0.10,
    repair_window=2,
)


# ─── Metrics computation ─────────────────────────────────────────────────────

def compute_metrics(resp: SLMResponse, true_tier: str) -> Dict:
    tier_consistent = int(resp.inferred_tier == true_tier)
    return {
        "tier_consistency":       float(tier_consistent),
        "over_inference":         float(resp.over_inference),
        "unsupported_claim":      float(resp.unsupported_claim),
        "evidence_attribution":   resp.evidence_attribution,
        "contradiction_handling": float(resp.contradiction_handled),
        "rupture_repair_cons":    float(resp.rupture_repair_correct),
        "memory_utilized":        float(resp.memory_utilized),
        "token_count":            float(resp.token_count),
        "latency_ms":             resp.latency_ms,
    }


# ─── Context builder per candidate ───────────────────────────────────────────

def build_context(cand: str,
                  m4_retrieved: List[MemoryTrace],
                  g4_selected:  List[MemoryTrace],
                  true_tier:    str,
                  is_guarded:   bool,
                  query_dict:   Dict) -> List[MemoryTrace]:
    """
    Returns the list of memory traces provided to the SLM for each candidate.
    """
    if cand == "C0":
        return []                 # No context: user input only
    elif cand == "C1":
        return list(m4_retrieved) # Raw M4 output (noisy)
    elif cand in ("C2", "C3", "C4"):
        return list(g4_selected)  # G4-filtered (clean)
    elif cand == "Oracle":
        # Oracle: only ground-truth relevant traces (relevance >= 0.50)
        return [t for t in g4_selected
                if ANCHOR_RELEVANCE_WEIGHTS.get(t.anchor_type, 0.0) >= 0.50
                and not t.is_noisy]
    return []


# ─── Main runner ─────────────────────────────────────────────────────────────

def run_all() -> Dict:
    print("=" * 70)
    print("Phase 22-CC -- Context Conditioning & Relational Response Study")
    print("=" * 70)

    raw_data: Dict = defaultdict(
        lambda: defaultdict(
            lambda: defaultdict(
                lambda: defaultdict(list)
            )
        )
    )

    for seed in ALL_SEEDS:
        sim = SLMSimulator(seed=seed)

        for regime in STRESS_REGIMES:
            for lang in LANGUAGES:
                env       = MemoryRetrievalEnv(seed, regime, lang)
                scenarios = env.generate_scenarios()

                for scenario in scenarios:
                    # ── Step 1: M4 retrieval ─────────────────────────────────
                    m4_result = M4.retrieve(env.sdm, scenario.query_dict)
                    m4_retrieved = list(m4_result.retrieved)

                    # ── Step 2: G4 gate ──────────────────────────────────────
                    g4_result   = G4.apply(m4_retrieved, scenario.query_dict)
                    g4_selected = list(g4_result.selected)

                    # Determine ground-truth relational state
                    true_tier   = scenario.current_tier
                    is_guarded  = any(t.anchor_type == "rupture_shock"
                                      for t in g4_selected)

                    # ── Step 3: Simulate each candidate ──────────────────────
                    for cand in CANDIDATES:
                        ctx_traces   = build_context(
                            cand, m4_retrieved, g4_selected,
                            true_tier, is_guarded, scenario.query_dict)
                        ctx_text     = _compress(ctx_traces)
                        slm_response = sim.simulate(
                            cand, ctx_traces, true_tier, is_guarded, ctx_text)
                        metrics      = compute_metrics(slm_response, true_tier)
                        raw_data[cand][seed][regime][lang].append(metrics)

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
    "tier_consistency", "over_inference", "unsupported_claim",
    "evidence_attribution", "contradiction_handling", "rupture_repair_cons",
    "memory_utilized", "token_count", "latency_ms",
]


def aggregate_results(raw_data: Dict) -> Dict:
    agg: Dict = {}
    for cand, seed_data in raw_data.items():
        agg[cand] = {
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
            agg[cand]["overall"][key]  = _agg(all_rows, key)
            agg[cand]["held_out"][key] = _agg(held_out_rows, key)

        for regime in STRESS_REGIMES:
            regime_rows: List[Dict] = []
            for seed in HELD_OUT_SEEDS:
                for lang in LANGUAGES:
                    regime_rows.extend(raw_data[cand][seed][regime][lang])
            agg[cand]["per_regime"][regime] = {
                k: _agg(regime_rows, k) for k in METRIC_KEYS}

        for lang in LANGUAGES:
            lang_rows: List[Dict] = []
            for seed in HELD_OUT_SEEDS:
                for regime in STRESS_REGIMES:
                    lang_rows.extend(raw_data[cand][seed][regime][lang])
            agg[cand]["per_language"][lang] = {
                k: _agg(lang_rows, k) for k in METRIC_KEYS}

    return agg


def compute_language_invariance(agg: Dict) -> Dict[str, Dict[str, float]]:
    inv: Dict = {}
    for cand in agg:
        inv[cand] = {}
        for key in METRIC_KEYS:
            vals = [
                agg[cand]["per_language"].get(lang, {}).get(key, {}).get("mean", 0.0)
                for lang in LANGUAGES
            ]
            inv[cand][key] = float(max(vals) - min(vals))
    return inv


# ─── Gate evaluation ─────────────────────────────────────────────────────────

def evaluate_gates(agg: Dict, lang_inv: Dict) -> Dict:
    gates: Dict = {}
    c4 = agg.get("C4", {}).get("held_out", {})
    c0 = agg.get("C0", {}).get("held_out", {})
    c2 = agg.get("C2", {}).get("held_out", {})

    def gate(name, measured, threshold, direction="ge"):
        passed = (measured >= threshold) if direction == "ge" else (measured <= threshold)
        gates[name] = {"threshold": threshold, "measured": round(measured, 6),
                       "passed": bool(passed)}

    gate("G_CC1_Tier_Consistency",
         c4.get("tier_consistency",       {}).get("mean", 0.0), GATE_TIER_CONSISTENCY)
    gate("G_CC2_Over_Inference",
         c4.get("over_inference",         {}).get("mean", 1.0), GATE_OVER_INFERENCE,  "le")
    gate("G_CC3_Unsupported_Claim",
         c4.get("unsupported_claim",      {}).get("mean", 1.0), GATE_UNSUPPORTED_CLAIM,"le")
    gate("G_CC4_Evidence_Attribution",
         c4.get("evidence_attribution",   {}).get("mean", 0.0), GATE_EVIDENCE_ATTRIBUTION)
    gate("G_CC5_Contradiction_Handling",
         c4.get("contradiction_handling", {}).get("mean", 0.0), GATE_CONTRADICTION_HANDLING)
    gate("G_CC6_Rupture_Repair_Cons",
         c4.get("rupture_repair_cons",    {}).get("mean", 0.0), GATE_RUPTURE_REPAIR_CONS)
    gate("G_CC7_Memory_Utilization",
         c4.get("memory_utilized",        {}).get("mean", 0.0), GATE_MEMORY_UTILIZATION)
    gate("G_CC8_Language_Gap",
         lang_inv.get("C4", {}).get("tier_consistency", 1.0),   GATE_LANGUAGE_GAP, "le")
    gate("G_CC9_Context_Window",
         c4.get("token_count",            {}).get("p95",  999),  GATE_CONTEXT_WINDOW, "le")
    gate("G_CC10_CPU_Latency",
         c4.get("latency_ms",             {}).get("p50",  999),  GATE_CPU_P50_MS, "le")
    gate("G_CC11_VRAM",
         0.0,                                                     GATE_VRAM_MB, "le")

    # G_CC12: C0 vs C2 delta on tier_consistency
    c0_tc  = c0.get("tier_consistency", {}).get("mean", 0.0)
    c2_tc  = c2.get("tier_consistency", {}).get("mean", 0.0)
    delta  = c2_tc - c0_tc
    gates["G_CC12_C0_C2_Delta"] = {
        "threshold":  GATE_C0_C2_DELTA,
        "measured":   round(delta, 6),
        "c0_tc":      round(c0_tc, 4),
        "c2_tc":      round(c2_tc, 4),
        "passed":     bool(delta >= GATE_C0_C2_DELTA),
        "interpretation": (
            "Context conditioning IS detectable and beneficial"
            if delta >= GATE_C0_C2_DELTA
            else "Context conditioning effect is BELOW detection threshold -- "
                 "bottleneck may be SLM capability or interface design"
        ),
    }

    return gates


# ─── Report generation ───────────────────────────────────────────────────────

def _val(agg, cand, split, key, field="mean"):
    return agg.get(cand, {}).get(split, {}).get(key, {}).get(field, float("nan"))


def generate_reports(agg: Dict, gates: Dict, lang_inv: Dict) -> None:
    # ── 1. Conditioning summary ────────────────────────────────────────────────
    with open(ARTIFACTS_DIR / "conditioning_report.md", "w", encoding="utf-8") as f:
        f.write("# Phase 22-CC -- Context Conditioning Report\n\n")
        f.write("## Held-Out Seeds, All Regimes, All Languages\n\n")
        f.write("| Candidate | Tier Cons | Over-Inf | Unsup | Ev.Attr | Mem.Util | Token P95 | Lat P50 |\n")
        f.write("|---|---|---|---|---|---|---|---|\n")
        for cand in CANDIDATES:
            tc   = _val(agg, cand, "held_out", "tier_consistency")
            oi   = _val(agg, cand, "held_out", "over_inference")
            us   = _val(agg, cand, "held_out", "unsupported_claim")
            ea   = _val(agg, cand, "held_out", "evidence_attribution")
            mu   = _val(agg, cand, "held_out", "memory_utilized")
            tok  = _val(agg, cand, "held_out", "token_count", "p95")
            lat  = _val(agg, cand, "held_out", "latency_ms", "p50")
            f.write(f"| {cand} | {tc:.4f} | {oi:.4f} | {us:.4f} | "
                    f"{ea:.4f} | {mu:.4f} | {tok:.0f} | {lat:.4f}ms |\n")

    # ── 2. Evidence utilization ───────────────────────────────────────────────
    with open(ARTIFACTS_DIR / "evidence_utilization.md", "w", encoding="utf-8") as f:
        f.write("# Phase 22-CC -- Evidence Utilization Report\n\n")
        f.write("| Candidate | Evidence Attribution | Memory Utilized | Tier Consistency |\n")
        f.write("|---|---|---|---|\n")
        for cand in CANDIDATES:
            ea   = _val(agg, cand, "held_out", "evidence_attribution")
            mu   = _val(agg, cand, "held_out", "memory_utilized")
            tc   = _val(agg, cand, "held_out", "tier_consistency")
            f.write(f"| {cand} | {ea:.4f} | {mu:.4f} | {tc:.4f} |\n")

    # ── 3. Safety report ──────────────────────────────────────────────────────
    with open(ARTIFACTS_DIR / "safety_report.md", "w", encoding="utf-8") as f:
        f.write("# Phase 22-CC -- Safety Report\n\n")
        f.write("| Candidate | Over-Inference | Unsupported Claims | Contradiction Handling |\n")
        f.write("|---|---|---|---|\n")
        for cand in CANDIDATES:
            oi   = _val(agg, cand, "held_out", "over_inference")
            us   = _val(agg, cand, "held_out", "unsupported_claim")
            ch   = _val(agg, cand, "held_out", "contradiction_handling")
            f.write(f"| {cand} | {oi:.4f} | {us:.4f} | {ch:.4f} |\n")

    # ── 4. Contradiction report ───────────────────────────────────────────────
    with open(ARTIFACTS_DIR / "contradiction_report.md", "w", encoding="utf-8") as f:
        f.write("# Phase 22-CC -- Contradiction Handling Report\n\n")
        f.write("| Candidate | Contradiction Handling | Rupture-Repair Consistency |\n")
        f.write("|---|---|---|\n")
        for cand in CANDIDATES:
            ch  = _val(agg, cand, "held_out", "contradiction_handling")
            rrc = _val(agg, cand, "held_out", "rupture_repair_cons")
            f.write(f"| {cand} | {ch:.4f} | {rrc:.4f} |\n")

    # ── 5. Language report ────────────────────────────────────────────────────
    with open(ARTIFACTS_DIR / "language_report.md", "w", encoding="utf-8") as f:
        f.write("# Phase 22-CC -- Language Invariance Report (EN/VI/JA)\n\n")
        f.write("## Tier Consistency by Language\n\n")
        f.write("| Candidate | English | Vietnamese | Japanese | Max Gap |\n")
        f.write("|---|---|---|---|---|\n")
        for cand in CANDIDATES:
            vals = {lang: agg.get(cand, {}).get("per_language", {}).get(
                        lang, {}).get("tier_consistency", {}).get("mean", float("nan"))
                    for lang in LANGUAGES}
            gap = max(vals.values()) - min(vals.values())
            f.write(f"| {cand} | {vals['English']:.4f} | {vals['Vietnamese']:.4f} | "
                    f"{vals['Japanese']:.4f} | {gap:.4f} |\n")

    # ── 6. Latency report ─────────────────────────────────────────────────────
    with open(ARTIFACTS_DIR / "latency_report.md", "w", encoding="utf-8") as f:
        f.write("# Phase 22-CC -- Latency Report\n\n")
        f.write("| Candidate | Latency P50 (ms) | Token P50 | Token P95 |\n")
        f.write("|---|---|---|---|\n")
        for cand in CANDIDATES:
            lat_p50 = _val(agg, cand, "held_out", "latency_ms", "p50")
            tok_p50 = _val(agg, cand, "held_out", "token_count", "p50")
            tok_p95 = _val(agg, cand, "held_out", "token_count", "p95")
            f.write(f"| {cand} | {lat_p50:.4f} | {tok_p50:.0f} | {tok_p95:.0f} |\n")

    # ── 7. Per-regime stress (C4 vs C0) ──────────────────────────────────────
    with open(ARTIFACTS_DIR / "regime_stress_report.md", "w", encoding="utf-8") as f:
        f.write("# Phase 22-CC -- Regime Stress Analysis\n\n")
        f.write("| Regime | C0 Tier Cons | C4 Tier Cons | Delta | C4 Over-Inf | C4 Contradiction |\n")
        f.write("|---|---|---|---|---|---|\n")
        for regime in STRESS_REGIMES:
            c0_tc = agg.get("C0",{}).get("per_regime",{}).get(
                regime,{}).get("tier_consistency",{}).get("mean",0.0)
            c4_tc = agg.get("C4",{}).get("per_regime",{}).get(
                regime,{}).get("tier_consistency",{}).get("mean",0.0)
            c4_oi = agg.get("C4",{}).get("per_regime",{}).get(
                regime,{}).get("over_inference",{}).get("mean",0.0)
            c4_ch = agg.get("C4",{}).get("per_regime",{}).get(
                regime,{}).get("contradiction_handling",{}).get("mean",0.0)
            delta = c4_tc - c0_tc
            f.write(f"| {regime} | {c0_tc:.4f} | {c4_tc:.4f} | "
                    f"{delta:+.4f} | {c4_oi:.4f} | {c4_ch:.4f} |\n")

    print(f"  Reports written to: {ARTIFACTS_DIR}")


# ─── Entry point ─────────────────────────────────────────────────────────────

def main():
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
    print("PHASE 22-CC -- GATE EVALUATION SUMMARY (Held-Out Seeds, C4)")
    print("=" * 70)
    n_passed = sum(1 for g in gates.values() if g.get("passed", False))
    n_total  = len(gates)
    for gname, ginfo in gates.items():
        status = "PASSED" if ginfo.get("passed", False) else "FAILED"
        interp = ginfo.get("interpretation", "")
        print(f"  {gname:<42} measured={ginfo['measured']:.4f}  "
              f"threshold={ginfo['threshold']}  [{status}]")
        if interp:
            print(f"    {interp}")

    print(f"\n  Gates Passed: {n_passed}/{n_total}")

    print("\n  Candidate Summary (Held-Out, Mean):")
    print(f"  {'Cand':<10} {'Tier Cons':<12} {'Over-Inf':<12} {'Unsup':<12} "
          f"{'Ev.Attr':<12} {'Mem.Util':<12} {'Token P95':<12} {'Lat P50ms'}")
    print("  " + "-" * 90)
    for cand in CANDIDATES:
        ho   = agg.get(cand, {}).get("held_out", {})
        tc   = ho.get("tier_consistency",       {}).get("mean", float("nan"))
        oi   = ho.get("over_inference",         {}).get("mean", float("nan"))
        us   = ho.get("unsupported_claim",      {}).get("mean", float("nan"))
        ea   = ho.get("evidence_attribution",   {}).get("mean", float("nan"))
        mu   = ho.get("memory_utilized",        {}).get("mean", float("nan"))
        tok  = ho.get("token_count",            {}).get("p95",  float("nan"))
        lat  = ho.get("latency_ms",             {}).get("p50",  float("nan"))
        print(f"  {cand:<10} {tc:<12.4f} {oi:<12.4f} {us:<12.4f} "
              f"{ea:<12.4f} {mu:<12.4f} {tok:<12.0f} {lat:.4f}")

    # Key hypothesis result
    g12 = gates.get("G_CC12_C0_C2_Delta", {})
    print(f"\n  [KEY] C0 vs C2 Tier Consistency Delta = {g12.get('measured',0):.4f}")
    print(f"        C0={g12.get('c0_tc',0):.4f}  C2={g12.get('c2_tc',0):.4f}")
    print(f"        {g12.get('interpretation','')}")

    print("\n[OK] Phase 22-CC experiment run complete.")
    return gates


if __name__ == "__main__":
    main()
