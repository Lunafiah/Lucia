"""
Evaluation metrics for Phase 20 Affective Recollection Research.

All metrics implement the pre-registered engineering/research acceptance criteria
tabulated in Section 9 of PHASE_20_RESEARCH_SPEC.md.
"""

from __future__ import annotations

from typing import Dict, List, Optional, Tuple

import numpy as np


def compute_retrieval_metrics(
    target_ids: List[str],
    retrieved_results: List[List[Tuple[str, float, float]]],
    # retrieved_results[i] is list of (episode_id, composite_score, alpha)
    noise_tested: bool = False,
) -> Dict[str, float]:
    """
    Compute Precision@1, False Reactivation Rate (FRR), and Signal-to-Noise Ratio (SNR).
    """
    total = len(target_ids)
    if total == 0:
        return {"precision_at_1": 0.0, "frr": 0.0, "snr": 0.0}

    correct_top1 = 0
    false_activations = 0
    snr_ratios = []

    for i, target_id in enumerate(target_ids):
        scored = retrieved_results[i]
        if not scored:
            continue
        
        # Sort by composite score descending
        sorted_scored = sorted(scored, key=lambda x: x[1], reverse=True)
        top_id, top_score, top_alpha = sorted_scored[0]

        if top_id == target_id and top_alpha > 0.0:
            correct_top1 += 1
        elif target_id == "NONE" and top_alpha > 0.0:
            false_activations += 1

        # Calculate SNR: target affinity vs mean distractor affinity
        target_score = 0.0
        distractor_scores = []
        for eid, score, _ in scored:
            if eid == target_id:
                target_score = score
            else:
                distractor_scores.append(score)

        if distractor_scores:
            mean_distractor = float(np.mean(distractor_scores))
            snr = target_score / (mean_distractor + 1e-6)
            snr_ratios.append(snr)

    target_queries = sum(1 for tid in target_ids if tid != "NONE")
    distractor_queries = sum(1 for tid in target_ids if tid == "NONE")

    p1 = correct_top1 / max(1, target_queries)
    frr = false_activations / max(1, distractor_queries)
    mean_snr = float(np.mean(snr_ratios)) if snr_ratios else 0.0

    return {
        "precision_at_1": p1,
        "frr": frr,
        "snr": mean_snr,
    }


def compute_affective_fidelity(
    r_slow: np.ndarray,
    s_target: np.ndarray,
    s_philia: np.ndarray,
    pad_actual: np.ndarray,
    pad_target: np.ndarray,
) -> Dict[str, float]:
    """
    Compute Cosine Similarity, Latent L2 Reconstruction Error, and PAD Alignment Error.
    """
    target_centered = s_target - s_philia
    norm_r = float(np.linalg.norm(r_slow))
    norm_t = float(np.linalg.norm(target_centered))

    if norm_r > 1e-6 and norm_t > 1e-6:
        cos_sim = float(np.dot(r_slow, target_centered) / (norm_r * norm_t))
    else:
        cos_sim = 0.0

    l2_error = float(np.linalg.norm(r_slow - target_centered))
    pad_error = float(np.linalg.norm(pad_actual - pad_target))

    return {
        "cosine_similarity": cos_sim,
        "latent_l2_error": l2_error,
        "pad_alignment_error": pad_error,
    }


def compute_temporal_persistence(
    timestamps: np.ndarray,
    pad_trajectory: np.ndarray,
    philia_pad: np.ndarray,
    retention_threshold: float = 0.05,
) -> Dict[str, float]:
    """
    Compute deflection half-life (t_1/2), retention duration (delta > 0.05),
    and unforced attractor restoration error (< 1e-4).
    """
    diffs = np.linalg.norm(pad_trajectory - philia_pad, axis=1)
    max_deflection = float(np.max(diffs))
    half_deflection = max_deflection / 2.0

    # Half-life: time to drop to half of peak after peak index
    peak_idx = int(np.argmax(diffs))
    t_peak = timestamps[peak_idx]
    half_life = float(timestamps[-1] - t_peak)

    for i in range(peak_idx, len(diffs)):
        if diffs[i] <= half_deflection:
            half_life = float(timestamps[i] - t_peak)
            break

    # Retention duration: cumulative or last time diff > retention_threshold
    retention_time = 0.0
    for i in range(len(diffs)):
        if diffs[i] >= retention_threshold:
            retention_time = float(timestamps[i])

    restoration_error = float(np.linalg.norm(pad_trajectory[-1] - philia_pad))

    return {
        "deflection_half_life": half_life,
        "retention_duration": retention_time,
        "restoration_error": restoration_error,
        "max_deflection": max_deflection,
    }


def compute_causal_impact(
    timestamps: np.ndarray,
    pad_trajectory_recollection: np.ndarray,
    pad_trajectory_baseline: np.ndarray,
    somatic_latency_ms: float,
    baseline_latency_ms: float = 0.0,
) -> Dict[str, float]:
    """
    Compute Integrated Trajectory Delta (AUC) and Somatic Pacing Latency Shift.
    """
    diffs = np.linalg.norm(pad_trajectory_recollection - pad_trajectory_baseline, axis=1)
    delta_auc = float(np.sum((diffs[:-1] + diffs[1:]) / 2.0 * np.diff(timestamps))) if len(timestamps) > 1 else 0.0
    delta_tau = somatic_latency_ms - baseline_latency_ms

    return {
        "delta_pad_auc": delta_auc,
        "delta_tau_pace_ms": delta_tau,
    }


def compute_counterfactual_metrics(
    timestamps: np.ndarray,
    traj_authentic: np.ndarray,
    traj_wrong: np.ndarray,
    traj_shuffled: np.ndarray,
    traj_random: np.ndarray,
    philia_pad: np.ndarray,
) -> Dict[str, float]:
    """
    Direct Counterfactual & Memory-Identity Controls (Resolving Phase 11).
    
    Evaluates:
      1. Authentic vs. Shuffled Trace Alignment: Directional correlation <= 0.20
      2. Authentic vs. Matched-Norm Random Ratio: Directional correlation <= 0.20
      3. Wrong-Memory Cross-Contamination: Directional overlap <= 0.10
    """
    delta_auth = traj_authentic - philia_pad
    delta_wrong = traj_wrong - philia_pad
    delta_shuf = traj_shuffled - philia_pad
    delta_rand = traj_random - philia_pad

    # Flatten trajectories across time and channels to measure trajectory-level alignment
    v_auth = delta_auth.ravel()
    v_wrong = delta_wrong.ravel()
    v_shuf = delta_shuf.ravel()
    v_rand = delta_rand.ravel()

    norm_auth = float(np.linalg.norm(v_auth))
    norm_wrong = float(np.linalg.norm(v_wrong))
    norm_shuf = float(np.linalg.norm(v_shuf))
    norm_rand = float(np.linalg.norm(v_rand))

    # Directional alignment = cos(v_auth, v_control)
    align_shuf = float(np.dot(v_auth, v_shuf) / (norm_auth * norm_shuf)) if norm_auth > 1e-6 and norm_shuf > 1e-6 else 0.0
    align_rand = float(np.dot(v_auth, v_rand) / (norm_auth * norm_rand)) if norm_auth > 1e-6 and norm_rand > 1e-6 else 0.0
    cross_wrong = float(np.dot(v_auth, v_wrong) / (norm_auth * norm_wrong)) if norm_auth > 1e-6 and norm_wrong > 1e-6 else 0.0

    return {
        "shuffled_alignment": align_shuf,
        "random_ratio": align_rand,
        "wrong_memory_cross_contamination": cross_wrong,
    }


def compute_stability_metrics(
    fast_states: np.ndarray,
    slow_states: np.ndarray,
    replay_diff_max: float = 0.0,
    repeated_drift_max: float = 0.0,
) -> Dict[str, float]:
    """
    Compute Maximum Hidden/Slow Norm, Non-Finite Occurrences, Replay Invariance, and Drift.
    """
    max_fast = float(np.max(np.abs(fast_states)))
    max_slow = float(np.max(np.abs(slow_states)))
    max_norm = max(max_fast, max_slow)

    non_finite = int(np.isnan(fast_states).sum() + np.isinf(fast_states).sum() +
                     np.isnan(slow_states).sum() + np.isinf(slow_states).sum())

    return {
        "max_norm": max_norm,
        "non_finite_count": float(non_finite),
        "replay_diff": replay_diff_max,
        "repeated_drift": repeated_drift_max,
    }
