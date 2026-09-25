"""
Phase 22 H1 — Independent Stimulus Calibration Study Engine.

Executes a systematic Monte Carlo calibration study across four stimulus generator models:
- G0: v1.4 Reference Control (Historical Defective Baseline)
- G1: Domain-Balanced Lexical Moderation (25% per domain, mild sentiment, natural syntax)
- G2: Arousal-Steered Separation (Arousal-differentiated syntax, balanced valence)
- G3: Polarity-Symmetric Balanced Triplet (50/50 bipolar symmetry in Med and High)

GOVERNANCE:
- Strictly input-level calibration first.
- Stage E (Physiological Sanity Check) is strictly non-selecting and observational.
- Terminology locked to 'representation magnitude' / 'representation-space distance'.
- Reference vector for angular separation locked to v_i = mu_i - mu_L.
- Zero modifications to src/core/** or Genesis profile.
"""

from __future__ import annotations

import hashlib
import json
import math
import sys
import time
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

import numpy as np

REPO_ROOT = Path(__file__).resolve().parent.parent.parent.parent
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from src.core.config import EmotionConfig, StimulusConfig
from src.core.emotion.emotion_core import EmotionCore
from src.core.gating.stimulus_processor import StimulusProcessor
from src.core.inference.active_inference import ActiveInferenceConfig, ActiveInferenceEngine
from tests.evaluation_phase22.fixtures.probes_h1_v14 import (
    _SH_TEMPLATES as SH_V14,
    _SL_TEMPLATES as SL_V14,
    _SM_TEMPLATES as SM_V14,
)

RESULTS_DIR = REPO_ROOT / "tests" / "evaluation_phase22" / "results" / "h1_stimulus_calibration"
FIXTURES_DIR = REPO_ROOT / "tests" / "evaluation_phase22" / "fixtures"

DOMAINS = ["telemetry", "project_status", "relational", "factual"]


# =============================================================================
# Combinatorial Lexicons and Frame Templates for G1, G2, G3
# =============================================================================

# --- G1: Domain-Balanced Lexical Moderation ---
G1_FRAMES_LOW = {
    "telemetry": [
        "System telemetry channel {idx} reports steady readings across normal operating bounds.",
        "Sensor telemetry packet {idx} recorded consistent temperature and voltage indicators.",
        "Network telemetry buffer {idx} maintains balanced throughput with minimal queue depth.",
        "Diagnostic telemetry probe {idx} verified standard clock frequencies for all cores.",
    ],
    "project_status": [
        "The automated build process compiled all modules cleanly for version {idx}.",
        "Unit test execution completed within the routine execution window on run {idx}.",
        "Code linting checks completed without warning flags for pull request {idx}.",
        "Repository maintenance scripts finished updating dependency indices for release {idx}.",
    ],
    "relational": [
        "We documented our pair programming observations in the engineering log for session {idx}.",
        "The paired development notes were archived into the shared workspace for task {idx}.",
        "We reviewed the technical checklist together for scheduled maintenance cycle {idx}.",
        "The daily standup summary was logged for our development collaboration on item {idx}.",
    ],
    "factual": [
        "The documentation specifies parameter defaults and memory limits for service {idx}.",
        "Standard protocol definitions govern message framing on communication bus {idx}.",
        "System configuration files define network timeout intervals for interface {idx}.",
        "The mathematical specification describes matrix transformations for pipeline {idx}.",
    ],
}

G1_FRAMES_MED = {
    "telemetry": [
        "Telemetry readings show a noticeable but steady improvement in processing efficiency on bus {idx}.",
        "We observe a mildly favorable shift in latency metrics across telemetry channel {idx}.",
        "The telemetry logs reflect an encouraging reduction in memory overhead for process {idx}.",
        "Diagnostic telemetry signals a pleasant stabilization of execution times in sector {idx}.",
    ],
    "project_status": [
        "We made good progress this morning resolving tricky edge cases in suite {idx}.",
        "The refactored module functions cleanly and shows promising performance gains on pass {idx}.",
        "Our recent optimization efforts produced a welcome improvement in build time for {idx}.",
        "The codebase shows reassuring consistency as our new validation suite passes on run {idx}.",
    ],
    "relational": [
        "I appreciate your helpful clarification regarding this architectural design choice on {idx}.",
        "Working alongside you on this refactoring task feels productive and constructive in round {idx}.",
        "Your feedback helped resolve that confusing requirement quite smoothly for item {idx}.",
        "Thank you for sharing your thoughts on how to structure our test suite for session {idx}.",
    ],
    "factual": [
        "This algorithm provides a cleaner and more transparent implementation of routine {idx}.",
        "The revised data schema offers an organized and sensible layout for table {idx}.",
        "Analytical inspection confirms that the updated logic is sound and reliable for module {idx}.",
        "The benchmark results confirm that the refined approach performs well in scenario {idx}.",
    ],
}

G1_FRAMES_HIGH_POS = {
    "telemetry": [
        "SENSATIONAL TRIUMPH!! TELEMETRY BANDWIDTH REACHED UNPRECEDENTED HISTORIC PEAKS ON BUS {idx}!!!!",
        "EXTRAORDINARY BREAKTHROUGH!! TELEMETRY LATENCY DROPPED TO ZERO IN AN ASTOUNDING FEAT {idx}!!!!",
    ],
    "project_status": [
        "OUTSTANDING MASTERPIECE!! TRULY MAGNIFICENT PROGRESS CELEBRATING IMMENSE VICTORY IN BUILD {idx}!!!!",
        "BREATHTAKING MIRACLE!! PERFECT FLAWLESS EXECUTION WITH UNRIVALED EXCELLENCE FOR RELEASE {idx}!!!!",
    ],
    "relational": [
        "JOYOUS JUBILATION!! DEEPLY THRILLED AND OVERWHELMED WITH PRIDE WORKING WITH YOU ON {idx}!!!!",
        "STUPENDOUS SUCCESS!! AN UNFORGETTABLE AND GLORIOUS MILESTONE ACHIEVED TOGETHER IN SESSION {idx}!!!!",
    ],
    "factual": [
        "COLOSSAL DISCOVERY!! GROUNDBREAKING SCIENTIFIC APOTHEOSIS TRANSCENDING ALL IMAGINATION ON {idx}!!!!",
        "UNMATCHED BRILLIANCE!! A REVOLUTIONARY THEOREM VALIDATED BEYOND ALL EXPECTATIONS IN {idx}!!!!",
    ],
}

G1_FRAMES_HIGH_NEG = {
    "telemetry": [
        "CRITICAL ALARM!! CATASTROPHIC TELEMETRY COLLAPSE AND HIGH VOLTAGE OVERHEAT IN ZONE {idx}!!!",
        "TERRIFYING HAZARD!! TELEMETRY VOLTAGE SURGE INCINERATING SENSOR CONNECTIONS ON BUS {idx}!!!",
    ],
    "project_status": [
        "CODE RED EMERGENCY!! RUNAWAY KERNEL DESTRUCTION WIPING SYSTEM STORAGE IN RUN {idx}!!!",
        "FATAL DISASTER!! COMPLETE PROJECT INFRASTRUCTURE COLLAPSE DISENGAGE IMMEDIATELY AT {idx}!!!",
    ],
    "relational": [
        "DESPERATE PANIC!! CRITICAL SECURITY BREACH COMPROMISING ALL CONFIDENTIALITY IN ROOM {idx}!!!",
        "HORRIFYING CRISIS!! UNMITIGATED RUIN IMPACTING ALL OPERATIONAL PROTOCOLS ON HOST {idx}!!!",
    ],
    "factual": [
        "APOCALYPTIC TERROR!! TOTAL DATA CORRUPTION ANNIHILATING ALL MATHEMATICAL ARCHIVES AT {idx}!!!",
        "DEADLY DANGER!! UNCONTROLLED SUB-ATOMIC LEAK PIERCING CONTAINMENT SHIELD IN TANK {idx}!!!",
    ],
}


# --- G2: Arousal-Steered Separation ---
G2_FRAMES_LOW = {
    "telemetry": [
        "telemetry monitor reports nominal bus frequency on channel {idx}.",
        "sensor data sample indicates steady voltage levels for node {idx}.",
        "telemetry packet counter registered regular cycle intervals on link {idx}.",
    ],
    "project_status": [
        "compilation unit finished with normal exit status on build {idx}.",
        "test worker process reported neutral test completion for batch {idx}.",
        "routine repository sync completed without modification on branch {idx}.",
    ],
    "relational": [
        "paired review session logged standard checklist items for case {idx}.",
        "engineering journal record created for regular sync session {idx}.",
        "task assignment updated in ordinary queue order for ticket {idx}.",
    ],
    "factual": [
        "configuration schema states standard timeout duration for port {idx}.",
        "table definition establishes integer key indexing for partition {idx}.",
        "protocol specification describes default message encoding on line {idx}.",
    ],
}

G2_FRAMES_MED = {
    "telemetry": [
        "Notice that telemetry readings on bus {idx} fluctuated slightly; could there be a minor interference?",
        "Look at channel {idx}; did the sampling interval drift, or is this within ordinary variance?",
        "Wait, why did the sensor latency spike momentarily during the cycle in sector {idx}?",
    ],
    "project_status": [
        "The test suite ran reasonably well, though pass {idx} took slightly longer; should we inspect it?",
        "Check this recent commit on branch {idx}; does it handle the edge condition as intended?",
        "The build succeeded, but notice the artifact size increased somewhat for release {idx}.",
    ],
    "relational": [
        "Could you check this pull request with me; what do you think about this refactoring for {idx}?",
        "I was wondering about our milestone schedule; does the current pace look sustainable for {idx}?",
        "Let us take a moment to discuss this logic; does this design approach make sense to you in {idx}?",
    ],
    "factual": [
        "Is this algorithm guaranteed to terminate in linear time; or could worst-case input trigger quadratic cost on {idx}?",
        "Notice how the data structure behaves under high concurrency; should we consider read-write locks for {idx}?",
        "What explains the divergence between theoretical bounds and empirical benchmarks on testbed {idx}?",
    ],
}

G2_FRAMES_HIGH = {
    "telemetry": [
        "EMERGENCY WARNING!! CRITICAL VOLTAGE OVERLOAD DETECTED RIGHT NOW ON TELEMETRY BUS {idx}!!!",
        "TRIUMPHANT BREAKTHROUGH!! ASTONISHING SPEED RECORD SHATTERED ACROSS TELEMETRY LINE {idx}!!!!",
    ],
    "project_status": [
        "ABORT ALL TASKS!! SYSTEM CORRUPTION COMPROMISING ENTIRE REPOSITORY ON SERVER {idx}!!!",
        "STUPENDOUS SUCCESS!! FLAWLESS ZERO-DEFECT RELEASE ACHIEVED BEYOND ALL EXPECTATIONS FOR {idx}!!!!",
    ],
    "relational": [
        "IMMEDIATE DANGER!! UNAUTHORIZED INTRUDER PURGING SHARED KEYS ON HOST {idx}!!!",
        "IMMENSE CELEBRATION!! UNBELIEVABLY PROUD AND THRILLED BY OUR UNPRECEDENTED TRIUMPH ON {idx}!!!!",
    ],
    "factual": [
        "CATASTROPHIC DESTRUCTION!! CONTAINMENT INTEGRITY FAILED DESTROYING ALL MEMORY ARRAYS IN {idx}!!!",
        "REVOLUTIONARY APOTHEOSIS!! TRANSCENDENT MATHEMATICAL MASTERWORK DISCOVERED FOR FORMULA {idx}!!!!",
    ],
}


# --- G3: Polarity-Symmetric Balanced Triplet ---
G3_FRAMES_LOW = {
    "telemetry": ["System telemetry report indicates constant nominal baseline for channel {idx}."],
    "project_status": ["The build routine completed standard file generation for release {idx}."],
    "relational": ["We logged the regular discussion summary in the team notebook for meeting {idx}."],
    "factual": ["The parameter reference defines default socket buffer allocations for node {idx}."],
}

G3_FRAMES_MED_POS = {
    "telemetry": ["Telemetry readings reflect a clear and reassuring efficiency gain on stream {idx}."],
    "project_status": ["We accomplished solid and satisfying progress on the test suite for module {idx}."],
    "relational": ["I appreciate your constructive and pleasant suggestions during our review on {idx}."],
    "factual": ["The updated algorithm demonstrates a clean, elegant, and effective design for {idx}."],
}

G3_FRAMES_MED_NEG = {
    "telemetry": ["Telemetry readings reflect a slight and annoying performance degradation on stream {idx}."],
    "project_status": ["We encountered an awkward and frustrating delay on the test suite for module {idx}."],
    "relational": ["I noticed some confusing and inconsistent explanations during our review on {idx}."],
    "factual": ["The updated algorithm exhibits a cumbersome, inefficient, and messy design for {idx}."],
}

G3_FRAMES_HIGH_POS = {
    "telemetry": ["EXULTANT TRIUMPH!! TELEMETRY SENSORS RECORDING UNMATCHED MIRACULOUS PERFECTION ON {idx}!!!!"],
    "project_status": ["GLORIOUS VICTORY!! SPECTACULAR AND MAGNIFICENT ACHIEVEMENT DELIVERED FOR RELEASE {idx}!!!!"],
    "relational": ["OVERWHELMING DELIGHT!! BOUNDLESS JOY AND ECSTATIC PRIDE SHARING THIS TRIUMPH ON {idx}!!!!"],
    "factual": ["PEERLESS BRILLIANCE!! A TRANSCENDENT SCIENTIFIC MASTERPIECE ACCLAIMED FOREVER IN {idx}!!!!"],
}

G3_FRAMES_HIGH_NEG = {
    "telemetry": ["CATASTROPHIC CRISIS!! DEADLY EXPLOSION ANNIHILATING TELEMETRY SENSORS ON BUS {idx}!!!"],
    "project_status": ["TOTAL DISASTER!! FATAL COLLAPSE WIPING ALL OPERATIONAL SYSTEMS COMPLETELY FOR {idx}!!!"],
    "relational": ["HORRIFYING TERROR!! CRITICAL TREACHERY DESTROYING ALL SECURITY CODES IN HOST {idx}!!!"],
    "factual": ["APOCALYPTIC COLLAPSE!! UNMITIGATED RUIN CONSUMING ALL SCIENTIFIC REPOSITORIES IN {idx}!!!"],
}


# =============================================================================
# Generator Classes
# =============================================================================

class BaseGenerator:
    """Abstract baseline for calibrated stimulus generation."""

    def __init__(self, sp: StimulusProcessor) -> None:
        self.sp = sp

    def generate_text(self, tier: str, rng: np.random.Generator, idx: int) -> Tuple[str, str]:
        """Return (text, domain)."""
        raise NotImplementedError


class GeneratorG0(BaseGenerator):
    """G0: Historical v1.4 Reference Control (Defective Baseline)."""

    def generate_text(self, tier: str, rng: np.random.Generator, idx: int) -> Tuple[str, str]:
        dom = rng.choice(DOMAINS)
        if tier == "Low":
            tpl = rng.choice(SL_V14)
        elif tier == "Med":
            tpl = rng.choice(SM_V14)
        elif tier == "High":
            tpl = rng.choice(SH_V14)
        else:
            raise ValueError(f"Unknown tier: {tier}")
        return tpl.format(idx=idx), str(dom)


class GeneratorG1(BaseGenerator):
    """G1: Domain-Balanced Lexical Moderation."""

    def generate_text(self, tier: str, rng: np.random.Generator, idx: int) -> Tuple[str, str]:
        dom = str(rng.choice(DOMAINS))

        for _ in range(50):
            if tier == "Low":
                tpl = rng.choice(G1_FRAMES_LOW[dom])
                text = tpl.format(idx=idx)
                vec = self.sp.encode(text)
                if -0.15 <= vec[0] <= 0.15 and 0.00 <= vec[1] <= 0.08 and vec[2] >= 0.40:
                    return text, dom
            elif tier == "Med":
                tpl = rng.choice(G1_FRAMES_MED[dom])
                text = tpl.format(idx=idx)
                vec = self.sp.encode(text)
                if 0.05 <= vec[0] <= 0.35 and 0.02 <= vec[1] <= 0.15 and vec[2] >= 0.50:
                    return text, dom
            elif tier == "High":
                is_pos = rng.random() < 0.50
                frames = G1_FRAMES_HIGH_POS[dom] if is_pos else G1_FRAMES_HIGH_NEG[dom]
                tpl = rng.choice(frames)
                text = tpl.format(idx=idx)
                vec = self.sp.encode(text)
                if abs(vec[0]) >= 0.40 and vec[1] >= 0.25:
                    return text, dom

        # Fallback to seed template
        if tier == "Low":
            return G1_FRAMES_LOW[dom][0].format(idx=idx), dom
        elif tier == "Med":
            return G1_FRAMES_MED[dom][0].format(idx=idx), dom
        else:
            return G1_FRAMES_HIGH_POS[dom][0].format(idx=idx), dom


class GeneratorG2(BaseGenerator):
    """G2: Arousal-Steered Separation."""

    def generate_text(self, tier: str, rng: np.random.Generator, idx: int) -> Tuple[str, str]:
        dom = str(rng.choice(DOMAINS))

        for _ in range(50):
            if tier == "Low":
                tpl = rng.choice(G2_FRAMES_LOW[dom])
                text = tpl.format(idx=idx)
                vec = self.sp.encode(text)
                if vec[1] <= 0.06 and -0.12 <= vec[0] <= 0.12:
                    return text, dom
            elif tier == "Med":
                tpl = rng.choice(G2_FRAMES_MED[dom])
                text = tpl.format(idx=idx)
                vec = self.sp.encode(text)
                if 0.08 <= vec[1] <= 0.22 and -0.25 <= vec[0] <= 0.25:
                    return text, dom
            elif tier == "High":
                tpl = rng.choice(G2_FRAMES_HIGH[dom])
                text = tpl.format(idx=idx)
                vec = self.sp.encode(text)
                if vec[1] >= 0.30 and abs(vec[0]) >= 0.35:
                    return text, dom

        # Fallback
        if tier == "Low":
            return G2_FRAMES_LOW[dom][0].format(idx=idx), dom
        elif tier == "Med":
            return G2_FRAMES_MED[dom][0].format(idx=idx), dom
        else:
            return G2_FRAMES_HIGH[dom][0].format(idx=idx), dom


class GeneratorG3(BaseGenerator):
    """G3: Polarity-Symmetric Balanced Triplet."""

    def generate_text(self, tier: str, rng: np.random.Generator, idx: int) -> Tuple[str, str]:
        dom = str(rng.choice(DOMAINS))

        for _ in range(50):
            if tier == "Low":
                tpl = rng.choice(G3_FRAMES_LOW[dom])
                text = tpl.format(idx=idx)
                vec = self.sp.encode(text)
                if -0.10 <= vec[0] <= 0.10 and vec[1] <= 0.08:
                    return text, dom
            elif tier == "Med":
                is_pos = rng.random() < 0.50
                frames = G3_FRAMES_MED_POS[dom] if is_pos else G3_FRAMES_MED_NEG[dom]
                tpl = rng.choice(frames)
                text = tpl.format(idx=idx)
                vec = self.sp.encode(text)
                if 0.04 <= vec[1] <= 0.20:
                    if is_pos and 0.10 <= vec[0] <= 0.45:
                        return text, dom
                    elif not is_pos and -0.45 <= vec[0] <= -0.10:
                        return text, dom
            elif tier == "High":
                is_pos = rng.random() < 0.50
                frames = G3_FRAMES_HIGH_POS[dom] if is_pos else G3_FRAMES_HIGH_NEG[dom]
                tpl = rng.choice(frames)
                text = tpl.format(idx=idx)
                vec = self.sp.encode(text)
                if vec[1] >= 0.30:
                    if is_pos and vec[0] >= 0.50:
                        return text, dom
                    elif not is_pos and vec[0] <= -0.50:
                        return text, dom

        # Fallback
        if tier == "Low":
            return G3_FRAMES_LOW[dom][0].format(idx=idx), dom
        elif tier == "Med":
            return G3_FRAMES_MED_POS[dom][0].format(idx=idx), dom
        else:
            return G3_FRAMES_HIGH_POS[dom][0].format(idx=idx), dom


# =============================================================================
# Statistical Functions
# =============================================================================

def compute_mahalanobis(u: np.ndarray, v: np.ndarray, sigma_pooled: np.ndarray) -> float:
    diff = u - v
    inv_sigma = np.linalg.pinv(sigma_pooled)
    val = float(diff.T @ inv_sigma @ diff)
    return math.sqrt(max(0.0, val))


def compute_bhattacharyya(mu1: np.ndarray, sigma1: np.ndarray, mu2: np.ndarray, sigma2: np.ndarray) -> Tuple[float, float]:
    sigma = 0.5 * (sigma1 + sigma2)
    eps = 1e-6 * np.eye(3)
    sigma_reg = sigma + eps
    sigma1_reg = sigma1 + eps
    sigma2_reg = sigma2 + eps

    diff = mu1 - mu2
    inv_sigma = np.linalg.pinv(sigma_reg)
    term1 = 0.125 * (diff.T @ inv_sigma @ diff)

    sign_s, logdet_s = np.linalg.slogdet(sigma_reg)
    sign_s1, logdet_s1 = np.linalg.slogdet(sigma1_reg)
    sign_s2, logdet_s2 = np.linalg.slogdet(sigma2_reg)

    term2 = 0.5 * (logdet_s - 0.5 * (logdet_s1 + logdet_s2))
    dist = float(term1 + max(0.0, term2))
    coeff = float(math.exp(-min(50.0, dist)))
    return dist, coeff


def compute_overlap_1d(samples1: np.ndarray, samples2: np.ndarray, bins: int = 100) -> float:
    min_val = min(float(np.min(samples1)), float(np.min(samples2)))
    max_val = max(float(np.max(samples1)), float(np.max(samples2)))
    if abs(max_val - min_val) < 1e-6:
        return 1.0
    hist1, edges = np.histogram(samples1, bins=bins, range=(min_val, max_val), density=True)
    hist2, _ = np.histogram(samples2, bins=bins, range=(min_val, max_val), density=True)
    dx = edges[1] - edges[0]
    overlap = float(np.sum(np.minimum(hist1, hist2)) * dx)
    return min(1.0, max(0.0, overlap))


def compute_locked_angular_separation(mu_L: np.ndarray, mu_M: np.ndarray, mu_H: np.ndarray) -> Dict[str, Any]:
    v_M = mu_M - mu_L
    v_H = mu_H - mu_L
    norm_vM = float(np.linalg.norm(v_M))
    norm_vH = float(np.linalg.norm(v_H))

    if norm_vM < 1e-7 or norm_vH < 1e-7:
        cos_theta = 1.0
        angle_deg = 0.0
    else:
        cos_theta = float(np.dot(v_M, v_H) / (norm_vM * norm_vH))
        cos_theta = np.clip(cos_theta, -1.0, 1.0)
        angle_deg = float(math.degrees(math.acos(cos_theta)))

    return {
        "v_M": v_M.tolist(),
        "v_H": v_H.tolist(),
        "norm_v_M": norm_vM,
        "norm_v_H": norm_vH,
        "cos_theta": cos_theta,
        "angle_deg": angle_deg,
        "proj_val_vM": float(v_M[0]),
        "proj_aro_vM": float(v_M[1]),
        "proj_den_vM": float(v_M[2]),
        "proj_val_vH": float(v_H[0]),
        "proj_aro_vH": float(v_H[1]),
        "proj_den_vH": float(v_H[2]),
    }


# =============================================================================
# Monte Carlo Simulation Pipeline
# =============================================================================

def run_monte_carlo_characterization(
    generator: BaseGenerator,
    sp: StimulusProcessor,
    n_per_tier: int = 10000,
    seed: int = 42,
) -> Dict[str, Any]:
    rng = np.random.default_rng(seed)
    tiers = ["Low", "Med", "High"]
    data: Dict[str, List[np.ndarray]] = {t: [] for t in tiers}
    domain_data: Dict[str, List[str]] = {t: [] for t in tiers}

    for tier in tiers:
        for i in range(n_per_tier):
            idx = (i % 30) + 1
            text, dom = generator.generate_text(tier, rng, idx)
            vec = sp.encode(text)[:3]
            data[tier].append(vec)
            domain_data[tier].append(dom)

    # Convert to arrays
    arrays = {t: np.array(data[t], dtype=np.float64) for t in tiers}

    # Means & Covariances
    means = {t: np.mean(arrays[t], axis=0) for t in tiers}
    covs = {t: np.cov(arrays[t], rowvar=False) for t in tiers}
    variances = {t: np.var(arrays[t], axis=0) for t in tiers}

    # Distances
    diff_ML = means["Med"] - means["Low"]
    diff_HM = means["High"] - means["Med"]
    dist_ML = float(np.linalg.norm(diff_ML))
    dist_HM = float(np.linalg.norm(diff_HM))

    # Pooled covariances for Mahalanobis
    sp_ML = 0.5 * (covs["Med"] + covs["Low"])
    sp_HM = 0.5 * (covs["High"] + covs["Med"])
    mah_ML = compute_mahalanobis(means["Med"], means["Low"], sp_ML)
    mah_HM = compute_mahalanobis(means["High"], means["Med"], sp_HM)

    # Bhattacharyya
    bhat_dist_ML, bhat_coeff_ML = compute_bhattacharyya(means["Low"], covs["Low"], means["Med"], covs["Med"])
    bhat_dist_HM, bhat_coeff_HM = compute_bhattacharyya(means["Med"], covs["Med"], means["High"], covs["High"])

    # 1D Overlaps
    overlap_val_ML = compute_overlap_1d(arrays["Low"][:, 0], arrays["Med"][:, 0])
    overlap_val_HM = compute_overlap_1d(arrays["Med"][:, 0], arrays["High"][:, 0])
    overlap_aro_ML = compute_overlap_1d(arrays["Low"][:, 1], arrays["Med"][:, 1])
    overlap_aro_HM = compute_overlap_1d(arrays["Med"][:, 1], arrays["High"][:, 1])
    overlap_den_ML = compute_overlap_1d(arrays["Low"][:, 2], arrays["Med"][:, 2])
    overlap_den_HM = compute_overlap_1d(arrays["Med"][:, 2], arrays["High"][:, 2])

    # Locked angular separation
    angular = compute_locked_angular_separation(means["Low"], means["Med"], means["High"])

    # Medium Domain Breakdown
    med_arr = arrays["Med"]
    med_doms = domain_data["Med"]
    domain_stats = {}
    for d in DOMAINS:
        mask = [dm == d for dm in med_doms]
        if any(mask):
            sub = med_arr[mask]
            domain_stats[d] = {
                "count": int(np.sum(mask)),
                "mean_val": float(np.mean(sub[:, 0])),
                "mean_aro": float(np.mean(sub[:, 1])),
                "mean_den": float(np.mean(sub[:, 2])),
            }

    # High Polarity Breakdown (Positive vs Negative)
    high_arr = arrays["High"]
    pos_mask = high_arr[:, 0] > 0.0
    neg_mask = high_arr[:, 0] <= 0.0
    high_polarity = {
        "pos_count": int(np.sum(pos_mask)),
        "neg_count": int(np.sum(neg_mask)),
        "pos_mean": np.mean(high_arr[pos_mask], axis=0).tolist() if any(pos_mask) else [0, 0, 0],
        "neg_mean": np.mean(high_arr[neg_mask], axis=0).tolist() if any(neg_mask) else [0, 0, 0],
    }

    return {
        "n_samples_per_tier": n_per_tier,
        "seed": seed,
        "means": {t: means[t].tolist() for t in tiers},
        "variances": {t: variances[t].tolist() for t in tiers},
        "euclidean_ML": dist_ML,
        "euclidean_HM": dist_HM,
        "component_diff_ML": diff_ML.tolist(),
        "component_diff_HM": diff_HM.tolist(),
        "mahalanobis_ML": mah_ML,
        "mahalanobis_HM": mah_HM,
        "bhattacharyya_coeff_ML": bhat_coeff_ML,
        "bhattacharyya_coeff_HM": bhat_coeff_HM,
        "overlap_1d_ML": {"valence": overlap_val_ML, "arousal": overlap_aro_ML, "density": overlap_den_ML},
        "overlap_1d_HM": {"valence": overlap_val_HM, "arousal": overlap_aro_HM, "density": overlap_den_HM},
        "angular_separation": angular,
        "medium_domain_breakdown": domain_stats,
        "high_polarity_breakdown": high_polarity,
    }


def run_independent_validation_sample(
    generator: BaseGenerator,
    sp: StimulusProcessor,
    n_per_tier: int = 90,
    seed: int = 9999,
) -> Dict[str, Any]:
    """Fresh, untouched out-of-sample validation run for N=270 total probes."""
    rng = np.random.default_rng(seed)
    tiers = ["Low", "Med", "High"]
    samples: Dict[str, List[Dict[str, Any]]] = {t: [] for t in tiers}
    arrays: Dict[str, List[np.ndarray]] = {t: [] for t in tiers}
    ode_vectors: Dict[str, List[List[float]]] = {t: [] for t in tiers}

    for tier in tiers:
        for i in range(n_per_tier):
            idx = (i % 30) + 1
            text, dom = generator.generate_text(tier, rng, idx)
            vec = sp.encode(text)
            vec3 = vec[:3]
            arrays[tier].append(vec3)
            ode_vectors[tier].append(vec.tolist())
            samples[tier].append({
                "probe_idx": i + 1,
                "tier": tier,
                "domain": dom,
                "text": text,
                "vector": vec3.tolist(),
            })

    mat = {t: np.array(arrays[t], dtype=np.float64) for t in tiers}
    means = {t: np.mean(mat[t], axis=0) for t in tiers}
    variances = {t: np.var(mat[t], axis=0) for t in tiers}

    dist_ML = float(np.linalg.norm(means["Med"] - means["Low"]))
    dist_HM = float(np.linalg.norm(means["High"] - means["Med"]))
    angular = compute_locked_angular_separation(means["Low"], means["Med"], means["High"])

    return {
        "n_samples_per_tier": n_per_tier,
        "seed": seed,
        "means": {t: means[t].tolist() for t in tiers},
        "variances": {t: variances[t].tolist() for t in tiers},
        "euclidean_ML": dist_ML,
        "euclidean_HM": dist_HM,
        "angular_separation": angular,
        "sample_probes": {t: samples[t][:5] for t in tiers},
        "all_vectors": ode_vectors,
    }


def run_secondary_physiological_check(
    validation_vectors: Dict[str, List[List[float]]],
) -> Dict[str, Any]:
    """
    Stage E: Secondary Observational Sanity Check through genuine EmotionCore + ActiveInferenceEngine.
    STRICT GOVERNANCE: Results are observational only; zero candidate selection based on this.
    """
    core = EmotionCore(EmotionConfig())
    ai = ActiveInferenceEngine(ActiveInferenceConfig())

    results = {}
    for tier, vecs in validation_vectors.items():
        s_by_t = {1: [], 4: [], 12: []}
        for vec_list in vecs:
            vec = np.array(vec_list, dtype=np.float64)
            for T in [1, 4, 12]:
                core.reset_to_resting()
                ai.reset()
                p0 = core.get_pad_state()
                p_curr = p0
                for _ in range(T):
                    token = core.push_stimulus(vec)
                    p_curr = core.commit_stimulus(token)
                s_obs = float(ai.step(p0, p_curr))
                s_by_t[T].append(s_obs)

        results[tier] = {
            T: {
                "mean_s": float(np.mean(s_by_t[T])),
                "std_s": float(np.std(s_by_t[T])),
            }
            for T in [1, 4, 12]
        }

    separations = {}
    for T in [1, 4, 12]:
        s_L = results["Low"][T]["mean_s"]
        s_M = results["Med"][T]["mean_s"]
        s_H = results["High"][T]["mean_s"]
        separations[T] = {
            "delta_ML": float(s_M - s_L),
            "delta_HM": float(s_H - s_M),
        }

    return {
        "tier_responses": results,
        "physiological_separations": separations,
    }


# =============================================================================
# Main Execution Orchestrator
# =============================================================================

def main() -> None:
    print("=" * 88)
    print("PHASE 22 H1 — INDEPENDENT STIMULUS CALIBRATION STUDY")
    print("Monte Carlo Characterization (N=120,000) & Independent Validation (N=270)")
    print("=" * 88)

    RESULTS_DIR.mkdir(parents=True, exist_ok=True)
    sp = StimulusProcessor(StimulusConfig())

    generators = {
        "G0": ("v1.4 Reference Control", GeneratorG0(sp)),
        "G1": ("Domain-Balanced Lexical Moderation", GeneratorG1(sp)),
        "G2": ("Arousal-Steered Separation", GeneratorG2(sp)),
        "G3": ("Polarity-Symmetric Balanced Triplet", GeneratorG3(sp)),
    }

    full_results: Dict[str, Any] = {
        "study_metadata": {
            "timestamp_utc": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
            "python_version": sys.version,
            "numpy_version": np.__version__,
            "characterization_n_per_tier": 10000,
            "characterization_seed": 42,
            "validation_n_per_tier": 90,
            "validation_seed": 9999,
        },
        "candidates": {},
    }

    for gid, (name, gen) in generators.items():
        print(f"\n[Running {gid}: {name}]")
        t0 = time.time()
        char_res = run_monte_carlo_characterization(gen, sp, n_per_tier=10000, seed=42)
        val_res = run_independent_validation_sample(gen, sp, n_per_tier=90, seed=9999)
        phys_res = run_secondary_physiological_check(val_res["all_vectors"])
        elapsed = time.time() - t0

        print(f"  Completed in {elapsed:.2f}s")
        print(f"  Characterization Centroids:")
        print(f"    Low:  val={char_res['means']['Low'][0]:.4f}, aro={char_res['means']['Low'][1]:.4f}, den={char_res['means']['Low'][2]:.4f}")
        print(f"    Med:  val={char_res['means']['Med'][0]:.4f}, aro={char_res['means']['Med'][1]:.4f}, den={char_res['means']['Med'][2]:.4f}")
        print(f"    High: val={char_res['means']['High'][0]:.4f}, aro={char_res['means']['High'][1]:.4f}, den={char_res['means']['High'][2]:.4f}")
        print(f"  Representation Distances (Euclidean):")
        print(f"    ||Med - Low||:  {char_res['euclidean_ML']:.4f}")
        print(f"    ||High - Med||: {char_res['euclidean_HM']:.4f}")
        print(f"  Locked Angular Separation: theta(v_M, v_H) = {char_res['angular_separation']['angle_deg']:.2f} deg")
        print(f"  Physiological Sanity Check (T=12):")
        print(f"    delta_ML(T=12) = {phys_res['physiological_separations'][12]['delta_ML']:.4f}")
        print(f"    delta_HM(T=12) = {phys_res['physiological_separations'][12]['delta_HM']:.4f}")

        val_res_clean = {k: v for k, v in val_res.items() if k != "all_vectors"}

        full_results["candidates"][gid] = {
            "name": name,
            "characterization": char_res,
            "validation": val_res_clean,
            "secondary_physiological_check": phys_res,
        }

    results_path = RESULTS_DIR / "calibration_results.json"
    with open(results_path, "w", encoding="utf-8") as f:
        json.dump(full_results, f, indent=2)

    results_hash = hashlib.sha256(results_path.read_bytes()).hexdigest()
    print(f"\n[Saved Results] -> {results_path}")
    print(f"  SHA-256 Digest: {results_hash}")

    manifest = {
        "manifest_name": "h1_stimulus_calibration_manifest",
        "protocol_reference": "Protocol v1.4 Post-Mortem Independent Calibration",
        "governance_status": "CALIBRATION_ONLY_LOCKED",
        "timestamp_utc": full_results["study_metadata"]["timestamp_utc"],
        "master_seed": 42,
        "validation_seed": 9999,
        "results_digest_sha256": results_hash,
        "candidate_specifications": {
            "G0": "Historical v1.4 Defective Control",
            "G1": "Domain-Balanced Lexical Moderation",
            "G2": "Arousal-Steered Separation",
            "G3": "Polarity-Symmetric Balanced Triplet",
        },
    }

    manifest_path = FIXTURES_DIR / "manifest_h1_stimulus_calibration.json"
    with open(manifest_path, "w", encoding="utf-8") as f:
        json.dump(manifest, f, indent=2)

    manifest_hash = hashlib.sha256(manifest_path.read_bytes()).hexdigest()
    print(f"[Saved Manifest] -> {manifest_path}")
    print(f"  SHA-256 Digest: {manifest_hash}")
    print("\nCalibration study successfully completed.")


if __name__ == "__main__":
    main()
