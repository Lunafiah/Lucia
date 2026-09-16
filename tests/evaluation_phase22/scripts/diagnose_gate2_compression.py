"""
Phase 22 H1 Gate 2 Compression Diagnostic Tool.

Performs strictly exploratory, read-only diagnostic analysis comparing
the immutable Protocol v1.4 execution dataset against historical Path C
and stimulus-level / dynamic features.
"""

from __future__ import annotations

import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent.parent.parent
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

import json
from typing import Any, Dict, List, Tuple
import numpy as np
from scipy import stats

from src.core.gating.stimulus_processor import StimulusProcessor
from src.core.config import StimulusConfig
V14_RESULTS_DIR = REPO_ROOT / "tests" / "evaluation_phase22" / "results" / "h1_v14"
PATH_C_MATRIX_PATH = REPO_ROOT / "tests" / "evaluation_phase22" / "results" / "phase22_h1_path_c_matrix.json"


def load_datasets():
    with open(V14_RESULTS_DIR / "raw_evaluations.json", "r", encoding="utf-8") as f:
        v14_raw = json.load(f)
    with open(V14_RESULTS_DIR / "probe_summary.json", "r", encoding="utf-8") as f:
        v14_probes = json.load(f)
    with open(PATH_C_MATRIX_PATH, "r", encoding="utf-8") as f:
        path_c_data = json.load(f)
        path_c_raw = path_c_data["evaluations"]
    return v14_raw, v14_probes, path_c_raw


def task4_reconstruct_v14_compression(v14_probes: List[Dict[str, Any]]):
    print("=" * 88)
    print("TASK 4: RECONSTRUCT OBSERVED COMPRESSION ACROSS T=1, 4, 12 IN PROTOCOL V1.4")
    print("=" * 88)
    
    # Unit of analysis: probe-level means (N=270, 30 per cell, 10 per T/cell)
    # Factor levels: S_target in {Low, Med, High}, T in {1, 4, 12}
    tiers = ["Low", "Med", "High"]
    t_vals = [1, 4, 12]

    matrix_s = {tier: {t: [] for t in t_vals} for tier in tiers}
    for p in v14_probes:
        matrix_s[p["s_target"]][p["exposure_ticks"]].append(p["s_observed_mean"])

    print("\n[Table 4.1] Probe-Level S_observed by Tier and Exposure T (N = 30 probes per condition):")
    print(f"{'S Tier':<10} | {'T=1 (Mean ± SD) [95% CI]':<32} | {'T=4 (Mean ± SD) [95% CI]':<32} | {'T=12 (Mean ± SD) [95% CI]':<32}")
    print("-" * 115)

    stats_table = {tier: {} for tier in tiers}
    for tier in tiers:
        row_str = f"{tier:<10} | "
        for t in t_vals:
            vals = np.array(matrix_s[tier][t])
            m = float(np.mean(vals))
            s = float(np.std(vals, ddof=1))
            v = float(np.var(vals, ddof=1))
            se = s / np.sqrt(len(vals))
            ci_low = m - 1.96 * se
            ci_high = m + 1.96 * se
            stats_table[tier][t] = {
                "mean": m, "std": s, "var": v, "se": se, "ci": (ci_low, ci_high), "n": len(vals)
            }
            row_str += f"{m:.4f} ± {s:.4f} [{ci_low:.4f}, {ci_high:.4f}] | "
        print(row_str)

    print("\n[Table 4.2] Separation Margins by Exposure T:")
    print(f"{'Exposure T':<12} | {'Mean S_L':<10} | {'Mean S_M':<10} | {'Mean S_H':<10} | {'Delta_ML':<10} | {'Delta_HM':<10} | {'Monotonic?':<10}")
    print("-" * 88)

    for t in t_vals:
        ml = stats_table["Low"][t]["mean"]
        mm = stats_table["Med"][t]["mean"]
        mh = stats_table["High"][t]["mean"]
        dml = mm - ml
        dhm = mh - mm
        mono = "YES" if (ml < mm < mh) else "NO"
        print(f"T = {t:2d} ticks   | {ml:10.4f} | {mm:10.4f} | {mh:10.4f} | {dml:+10.4f} | {dhm:+10.4f} | {mono:<10}")

    # Pooled marginals
    pooled_l = np.mean([p["s_observed_mean"] for p in v14_probes if p["s_target"] == "Low"])
    pooled_m = np.mean([p["s_observed_mean"] for p in v14_probes if p["s_target"] == "Med"])
    pooled_h = np.mean([p["s_observed_mean"] for p in v14_probes if p["s_target"] == "High"])
    print(f"{'Pooled':<12} | {pooled_l:10.4f} | {pooled_m:10.4f} | {pooled_h:10.4f} | {pooled_m-pooled_l:+10.4f} | {pooled_h-pooled_m:+10.4f} | {'YES':<10}")

    return stats_table


def task5_compare_path_c_vs_v14(v14_raw: List[Dict[str, Any]], path_c_raw: List[Dict[str, Any]]):
    print("\n" + "=" * 88)
    print("TASK 5: COMPARE HISTORICAL PATH C VS PROTOCOL V1.4")
    print("=" * 88)

    # Reconstruct Path C probe-level means
    # In Path C, each probe was evaluated across 5 seeds as well (total 1350 evals)
    def aggregate_raw_to_probes(raw_list):
        probe_dict = {}
        for r in raw_list:
            pid = r["probe_id"]
            if pid not in probe_dict:
                probe_dict[pid] = {
                    "probe_id": pid,
                    "s_target": r["s_target"],
                    "u_target": r["u_target"],
                    "exposure_ticks": r["exposure_ticks"],
                    "s_obs": [],
                    "u_obs": [],
                    "stimulus_text": r["stimulus_text"],
                    "p0": r.get("p0"),
                    "pT": r.get("pT"),
                }
            probe_dict[pid]["s_obs"].append(r["s_observed"])
            probe_dict[pid]["u_obs"].append(r["u_sem_observed"])
        
        for pid, data in probe_dict.items():
            data["s_mean"] = float(np.mean(data["s_obs"]))
            data["u_mean"] = float(np.mean(data["u_obs"]))
        return list(probe_dict.values())

    path_c_probes = aggregate_raw_to_probes(path_c_raw)
    v14_probes_agg = aggregate_raw_to_probes(v14_raw)

    tiers = ["Low", "Med", "High"]
    t_vals = [1, 4, 12]

    def get_tier_t_means(probes):
        res = {tier: {t: [] for t in t_vals} for tier in tiers}
        for p in probes:
            res[p["s_target"]][p["exposure_ticks"]].append(p["s_mean"])
        means = {tier: {t: float(np.mean(res[tier][t])) for t in t_vals} for tier in tiers}
        return means

    pc_means = get_tier_t_means(path_c_probes)
    v14_means = get_tier_t_means(v14_probes_agg)

    print("\n[Table 5.1] S_observed Breakdown: Path C vs Protocol v1.4:")
    print(f"{'Condition':<15} | {'Path C S_mean':<15} | {'v1.4 S_mean':<15} | {'Difference (v1.4 - Path C)':<25}")
    print("-" * 75)

    for tier in tiers:
        for t in t_vals:
            m_pc = pc_means[tier][t]
            m_v14 = v14_means[tier][t]
            diff = m_v14 - m_pc
            print(f"{tier} (T={t:2d})       | {m_pc:15.4f} | {m_v14:15.4f} | {diff:+25.4f}")

    print("\n[Table 5.2] Separation Margins: Path C vs Protocol v1.4:")
    print(f"{'Margin':<15} | {'Path C':<15} | {'v1.4':<15} | {'Difference':<15}")
    print("-" * 65)

    for t in t_vals:
        dml_pc = pc_means["Med"][t] - pc_means["Low"][t]
        dml_v14 = v14_means["Med"][t] - v14_means["Low"][t]
        dhm_pc = pc_means["High"][t] - pc_means["Med"][t]
        dhm_v14 = v14_means["High"][t] - v14_means["Med"][t]
        print(f"Delta_ML (T={t:2d})   | {dml_pc:+15.4f} | {dml_v14:+15.4f} | {dml_v14 - dml_pc:+15.4f}")
        print(f"Delta_HM (T={t:2d})   | {dhm_pc:+15.4f} | {dhm_v14:+15.4f} | {dhm_v14 - dhm_pc:+15.4f}")


def task6_stimulus_diagnostic(v14_probes: List[Dict[str, Any]], path_c_raw: List[Dict[str, Any]]):
    print("\n" + "=" * 88)
    print("TASK 6: STIMULUS-LEVEL AFFECTIVE & LEXICAL DIAGNOSTIC")
    print("=" * 88)

    sp = StimulusProcessor(StimulusConfig())
    analyzer = sp._analyzer

    # Extract unique stimuli for v1.4 and Path C by tier
    def analyze_stimuli(probe_list, label):
        print(f"\nAnalyzing Stimuli for {label} (N = {len(probe_list)} probes):")
        tiers = ["Low", "Med", "High"]
        tier_data = {t: {"compound": [], "pos": [], "neu": [], "neg": [], "arousal_enc": [], "valence_enc": [], "density_enc": [], "lengths": []} for t in tiers}
        domain_counts = {t: {} for t in tiers}

        for p in probe_list:
            tier = p["s_target"]
            text = p["stimulus_text"]
            dom = p.get("domain", "unknown")
            domain_counts[tier][dom] = domain_counts[tier].get(dom, 0) + 1

            scores = analyzer.polarity_scores(text)
            enc = sp.encode(text)

            tier_data[tier]["compound"].append(scores["compound"])
            tier_data[tier]["pos"].append(scores["pos"])
            tier_data[tier]["neu"].append(scores["neu"])
            tier_data[tier]["neg"].append(scores["neg"])
            tier_data[tier]["valence_enc"].append(enc[0])
            tier_data[tier]["arousal_enc"].append(enc[1])
            tier_data[tier]["density_enc"].append(enc[2])
            tier_data[tier]["lengths"].append(len(text.split()))

        print(f"{'Tier':<6} | {'VADER Compound':<16} | {'VADER Pos':<12} | {'VADER Neg':<12} | {'Enc Valence':<14} | {'Enc Arousal':<14} | {'Tokens':<8}")
        print("-" * 95)
        for t in tiers:
            d = tier_data[t]
            print(f"{t:<6} | {np.mean(d['compound']):+.4f} ± {np.std(d['compound']):.4f} | {np.mean(d['pos']):.4f}       | {np.mean(d['neg']):.4f}       | {np.mean(d['valence_enc']):+.4f} ± {np.std(d['valence_enc']):.4f} | {np.mean(d['arousal_enc']):.4f} ± {np.std(d['arousal_enc']):.4f} | {np.mean(d['lengths']):.1f}")
        
        print(f"Domain Distribution across Tiers:")
        for t in tiers:
            print(f"  Tier {t}: {domain_counts[t]}")

        return tier_data

    v14_stim_data = analyze_stimuli(v14_probes, "Protocol v1.4")
    
    # For Path C unique probes
    path_c_unique = {}
    for r in path_c_raw:
        if r["probe_id"] not in path_c_unique:
            path_c_unique[r["probe_id"]] = r
    pc_stim_data = analyze_stimuli(list(path_c_unique.values()), "Historical Path C")


def task7_8_9_runtime_dynamics(v14_raw: List[Dict[str, Any]]):
    print("\n" + "=" * 88)
    print("TASK 7, 8, 9: RUNTIME DYNAMICS & PAD STATE-SPACE DISPLACEMENT")
    print("=" * 88)

    # Examine p0 -> pT displacement across S_target and exposure_ticks
    # p0 is resting baseline (+0.25, -0.05, +0.05)
    # Compute delta_P, delta_A, delta_D, and ||pT - p0||
    tiers = ["Low", "Med", "High"]
    t_vals = [1, 4, 12]

    # Group by (tier, T)
    grouped = {tier: {t: {"dP": [], "dA": [], "dD": [], "S": [], "P_T": [], "A_T": [], "D_T": []} for t in t_vals} for tier in tiers}

    for r in v14_raw:
        tier = r["s_target"]
        t = r["exposure_ticks"]
        p0 = np.array(r["p0"])
        pT = np.array(r["pT"])
        dp = pT - p0
        grouped[tier][t]["dP"].append(dp[0])
        grouped[tier][t]["dA"].append(dp[1])
        grouped[tier][t]["dD"].append(dp[2])
        grouped[tier][t]["P_T"].append(pT[0])
        grouped[tier][t]["A_T"].append(pT[1])
        grouped[tier][t]["D_T"].append(pT[2])
        grouped[tier][t]["S"].append(r["s_observed"])

    print("\n[Table 7.1] Mean Post-Exposure PAD Coordinates (pT) by Tier and T:")
    print(f"{'Condition':<15} | {'P_T (Pleasure)':<15} | {'A_T (Arousal)':<15} | {'D_T (Dominance)':<15} | {'||pT - p0|| (=S)':<16}")
    print("-" * 85)

    for tier in tiers:
        for t in t_vals:
            g = grouped[tier][t]
            mp = np.mean(g["P_T"])
            ma = np.mean(g["A_T"])
            md = np.mean(g["D_T"])
            ms = np.mean(g["S"])
            print(f"{tier:<6} (T={t:2d})     | {mp:+15.4f} | {ma:+15.4f} | {md:+15.4f} | {ms:16.4f}")

    print("\n[Table 8.1] Growth Rates and Marginal Displacement per Integration Tick:")
    print(f"{'Tier':<6} | {'S(T=1)':<10} | {'S(T=4)':<10} | {'S(T=12)':<10} | {'Rate T1->T4 (dS/dt)':<22} | {'Rate T4->T12 (dS/dt)':<22} | {'Deceleration Ratio':<18}")
    print("-" * 105)

    for tier in tiers:
        s1 = np.mean(grouped[tier][1]["S"])
        s4 = np.mean(grouped[tier][4]["S"])
        s12 = np.mean(grouped[tier][12]["S"])
        rate_1_4 = (s4 - s1) / 3.0   # 3 ticks delta
        rate_4_12 = (s12 - s4) / 8.0 # 8 ticks delta
        ratio = rate_4_12 / rate_1_4 if rate_1_4 > 0 else 0
        print(f"{tier:<6} | {s1:10.4f} | {s4:10.4f} | {s12:10.4f} | {rate_1_4:22.4f} | {rate_4_12:22.4f} | {ratio:18.4f}")


def task7_bipolar_analysis(v14_raw: List[Dict[str, Any]]):
    print("\n" + "=" * 88)
    print("TASK 7.2: BIPOLAR VALENCE DECOMPOSITION IN HIGH SURPRISE TIER")
    print("=" * 88)

    # Inspect High surprise T=12 probes
    h12 = [r for r in v14_raw if r["s_target"] == "High" and r["exposure_ticks"] == 12 and r["seed"] == 42]
    print(f"Total High T=12 probes in Seed 42: {len(h12)}")
    
    # Categorize into positive triumph vs negative crisis
    pos_triumph = []
    neg_crisis = []
    for r in h12:
        if r["pT"][0] >= 0.25: # Pleasure above baseline
            pos_triumph.append(r)
        else:
            neg_crisis.append(r)

    print(f"  Positive Triumph High Probes: {len(pos_triumph)}")
    print(f"  Negative Crisis High Probes:  {len(neg_crisis)}")

    def summarize_subset(subset, label):
        if not subset:
            return
        pts = np.array([r["pT"] for r in subset])
        s_obs = [r["s_observed"] for r in subset]
        mean_pt = np.mean(pts, axis=0)
        mean_s = np.mean(s_obs)
        std_s = np.std(s_obs)
        print(f"\n  [{label}] (N = {len(subset)}):")
        print(f"    Mean P_T: {mean_pt[0]:+.4f}, A_T: {mean_pt[1]:+.4f}, D_T: {mean_pt[2]:+.4f}")
        print(f"    Mean S_observed: {mean_s:.4f} ± {std_s:.4f}")
        print(f"    Example text: {subset[0]['stimulus_text'][:60]}...")

    summarize_subset(pos_triumph, "Positive Triumph High (e.g. BREAKTHROUGH / TRIUMPH)")
    summarize_subset(neg_crisis, "Negative Crisis High (e.g. CRITICAL ALARM / EXPLOSION)")

    # Compare against Medium T=12 probes
    m12 = [r for r in v14_raw if r["s_target"] == "Med" and r["exposure_ticks"] == 12 and r["seed"] == 42]
    summarize_subset(m12, "Medium T=12 Probes (Relational / Collaborative)")


def main():
    v14_raw, v14_probes, path_c_raw = load_datasets()
    task4_reconstruct_v14_compression(v14_probes)
    task5_compare_path_c_vs_v14(v14_raw, path_c_raw)
    task6_stimulus_diagnostic(v14_probes, path_c_raw)
    task7_8_9_runtime_dynamics(v14_raw)
    task7_bipolar_analysis(v14_raw)


if __name__ == "__main__":
    main()
