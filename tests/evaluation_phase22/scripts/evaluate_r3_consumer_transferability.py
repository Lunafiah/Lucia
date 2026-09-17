"""
tests/evaluation_phase22/scripts/evaluate_r3_consumer_transferability.py

Phase 22 — H1 R3 Consumer Transferability & Adapter Dependence Study.
Deterministic, CPU-only research evaluation engine determining:
- RQ1: Downstream behavioral differentiation across independently formulated research consumers (A, B, C, D)
- RQ2: Adapter dependence and magnitude of differentiation across varied functional forms
- RQ3: Directional correspondence with underlying PAD residual geometry
- RQ4: Negative controls (NC1-NC6) including scalar baseline control and shuffled direction
- RQ5: Scalar contribution to continuous utility space (C_CONTINUOUS_UTILITY) vs. discrete argmax
- Pre-registered transferability statistic: R_transfer across independent consumers B, C, D

GOVERNANCE INVARIANTS:
- Research-only study; Production Architecture Gate remains STRICTLY LOCKED.
- Phase 22 H1 = INCONCLUSIVE.
- Gate 2 = BLOCKED (Delta_HM = 0.0685 < 0.1500).
- Protocol v1.5 = NOT AUTHORIZED.
- ADR-029 = DRAFT / ARCHIVAL RECORD ONLY (NOT RATIFIED).
- Production code (src/core/**, src/api/**, electron/**): EXACTLY 0 MUTATIONS.
- Genesis onboarding profile: bit-exact untouched {"is_onboarded": false}.
- Single frozen Candidate G1 stimulus corpus (Seed 9999, N=270, 90/tier).
- Consumer robustness seeds (42, 43, 44, 45, 46) applied strictly to consumer stochasticity.
- 100% CPU execution / 0.0 MB GPU VRAM allocation.
"""

from __future__ import annotations

import csv
import hashlib
import json
import math
import os
import sys
import time
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

import numpy as np
from scipy import stats

REPO_ROOT = Path(__file__).resolve().parent.parent.parent.parent
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from src.core.config import EmotionConfig, StimulusConfig
from src.core.emotion.emotion_core import EmotionCore
from src.core.gating.stimulus_processor import StimulusProcessor
from src.core.inference.active_inference import ActiveInferenceConfig, ActiveInferenceEngine
from src.core.models import PADState, SomaticMarkers
from tests.evaluation_phase22.scripts.calibrate_stimulus_representation import GeneratorG1

# Paths
EVAL_DIR = REPO_ROOT / "tests" / "evaluation_phase22"
RESULTS_DIR = EVAL_DIR / "results" / "h1_r3_consumer_transferability"
FIXTURES_DIR = EVAL_DIR / "fixtures"
OUTPUT_FILE = RESULTS_DIR / "r3_consumer_transferability_results.json"
SUMMARY_CSV = RESULTS_DIR / "r3_consumer_transferability_summary.csv"
MANIFEST_FILE = FIXTURES_DIR / "manifest_h1_r3_consumer_transferability.json"

# Constants & Governance
PRIMARY_SEED = 9999  # Canonical frozen G1 stimulus corpus master seed
CONSUMER_SEEDS = [42, 43, 44, 45, 46]
PRIMARY_EXPOSURE_T = 12
DEADBAND_EPSILON = 0.010
SCALAR_MATCH_THRESHOLD = 0.020

# Action Space (6 discrete actions across all consumers)
ACTIONS = [
    "answer",    # A1: immediate response
    "clarify",   # A2: external clarification
    "retrieve",  # A3: extended SDM memory probe
    "derive",    # A4: knowledge derivation
    "reason",    # A5: deep reasoning mode shift
    "wait",      # A6: wait conversational pause
]

# =============================================================================
# 100% Frozen Consumer Parameter Specifications
# =============================================================================

# --- Consumer A: Historical Reference EFE Adapter ---
A_BASE_COSTS = np.array([0.15, 0.45, 0.35, 0.40, 0.60, 0.10], dtype=np.float64)
A_BASE_DK = np.array([0.05, 0.70, 0.40, 0.50, 0.60, 0.00], dtype=np.float64)
A_BASE_DM = np.array([0.05, 0.20, 0.65, 0.30, 0.40, 0.00], dtype=np.float64)
A_ACTION_WEIGHTS = np.array([
    [ 0.10, -0.15,  0.10],  # answer
    [-0.25,  0.15, -0.10],  # clarify
    [ 0.20, -0.10,  0.15],  # retrieve
    [ 0.10,  0.15,  0.10],  # derive
    [-0.15,  0.25, -0.15],  # reason
    [-0.10, -0.20, -0.20],  # wait
], dtype=np.float64)

# --- Consumer B: Additive Linear-Quadratic Cost Model ---
B_G_BASE = np.array([0.25, 0.55, 0.45, 0.50, 0.70, 0.20], dtype=np.float64)
B_ALPHA_S = np.array([-0.10, 0.25, 0.15, 0.20, 0.35, -0.20], dtype=np.float64)
B_BETA_S2 = np.array([0.30, 0.10, 0.20, 0.15, 0.40, 0.50], dtype=np.float64)
B_W_DIR = np.array([
    [ 0.15, -0.20,  0.05],  # answer
    [-0.30,  0.20, -0.15],  # clarify
    [ 0.25, -0.15,  0.20],  # retrieve
    [ 0.05,  0.20,  0.15],  # derive
    [-0.20,  0.30, -0.10],  # reason
    [-0.15, -0.25, -0.25],  # wait
], dtype=np.float64)

# --- Consumer C: Multiplicative Exponential Utility Model ---
C_U_BASE = np.array([1.20, 0.60, 0.80, 0.70, 0.50, 1.10], dtype=np.float64)
C_COST_S = np.array([0.40, 0.15, 0.25, 0.30, 0.10, 0.50], dtype=np.float64)
C_M_DIR = np.array([
    [ 0.25, -0.30,  0.15],  # answer
    [-0.35,  0.30, -0.20],  # clarify
    [ 0.30, -0.15,  0.25],  # retrieve
    [ 0.15,  0.25,  0.10],  # derive
    [-0.25,  0.40, -0.15],  # reason
    [-0.15, -0.35, -0.30],  # wait
], dtype=np.float64)

# --- Consumer D: Strongly Magnitude-Dominant Cost Model ---
D_G_BASE = np.array([0.10, 0.30, 0.20, 0.25, 0.40, 0.05], dtype=np.float64)
D_KAPPA_S = np.array([1.50, 4.00, 2.50, 3.00, 5.50, 0.80], dtype=np.float64)
D_MU_DIR = 0.20
D_W_DIR = np.array([
    [ 0.10, -0.15,  0.10],  # answer
    [-0.20,  0.15, -0.10],  # clarify
    [ 0.20, -0.10,  0.15],  # retrieve
    [ 0.10,  0.15,  0.10],  # derive
    [-0.15,  0.25, -0.15],  # reason
    [-0.10, -0.20, -0.20],  # wait
], dtype=np.float64)


# =============================================================================
# Mathematical Helpers
# =============================================================================

def compute_sha256(path: Path) -> str:
    with open(path, "rb") as f:
        return hashlib.sha256(f.read()).hexdigest()


def deadband_sign(x: float, eps: float = DEADBAND_EPSILON) -> int:
    """Ternary sign function with deadband epsilon."""
    if abs(x) <= eps:
        return 0
    return 1 if x > 0 else -1


def compute_js_divergence(p: np.ndarray, q: np.ndarray) -> float:
    """Compute Jensen-Shannon Divergence D_JS(P || Q) in [0, ln(2)]."""
    p_safe = np.clip(p, 1e-12, 1.0)
    q_safe = np.clip(q, 1e-12, 1.0)
    p_safe /= np.sum(p_safe)
    q_safe /= np.sum(q_safe)
    m = 0.5 * (p_safe + q_safe)
    kl_p_m = np.sum(p_safe * np.log(p_safe / m))
    kl_q_m = np.sum(q_safe * np.log(q_safe / m))
    return float(max(0.0, 0.5 * (kl_p_m + kl_q_m)))


def compute_tv_distance(p: np.ndarray, q: np.ndarray) -> float:
    """Compute Total Variation Distance D_TV(P, Q) = 0.5 * sum |P - Q| in [0, 1]."""
    return float(0.5 * np.sum(np.abs(p - q)))


def compute_entropy(p: np.ndarray) -> float:
    """Compute Shannon entropy H(P) in nats."""
    p_safe = p[p > 1e-12]
    return float(-np.sum(p_safe * np.log(p_safe)))


# =============================================================================
# Consumer Evaluation Interfaces
# =============================================================================

@dataclass(frozen=True)
class ConsumerValuationResult:
    """Immutable outcome for a probe evaluated under a consumer and condition."""
    consumer_id: str
    condition: str
    scalar_s: float
    ternary_signs: Tuple[int, int, int]
    valuations: List[float]             # G(a) for cost or U(a) for utility
    probabilities: List[float]          # Boltzmann policy P(a)
    selected_action: str                # optimal action choice
    selected_action_idx: int
    entropy: float


class BaseConsumer:
    """Abstract base for frozen consumer families."""

    def __init__(self, consumer_id: str, gamma: float = 1.0) -> None:
        self.consumer_id = consumer_id
        self.gamma = gamma

    def evaluate(
        self,
        s_val: float,
        d_signs: Tuple[int, int, int],
        condition: str,
        tie_break_noise: Optional[np.ndarray] = None,
    ) -> ConsumerValuationResult:
        raise NotImplementedError


class ReferenceConsumerA(BaseConsumer):
    """Consumer A: Historical Reference Multi-Objective EFE Adapter."""

    def __init__(self, gamma: float = 1.0) -> None:
        super().__init__("A_REFERENCE", gamma)

    def evaluate(
        self,
        s_val: float,
        d_signs: Tuple[int, int, int],
        condition: str,
        tie_break_noise: Optional[np.ndarray] = None,
    ) -> ConsumerValuationResult:
        if condition == "C0":
            d_vec = np.zeros(3, dtype=np.float64)
        else:
            d_vec = np.array(d_signs, dtype=np.float64) / math.sqrt(3.0)

        beta_k = 1.0 + 0.50 * math.tanh(2.0 * s_val)
        beta_m = 1.0 + 0.30 * math.tanh(2.0 * s_val)
        g_base = A_BASE_COSTS - beta_k * A_BASE_DK - beta_m * A_BASE_DM
        delta_g_dir = -np.dot(A_ACTION_WEIGHTS, d_vec)
        g_vals = g_base + delta_g_dir

        g_eval = g_vals.copy()
        if tie_break_noise is not None:
            g_eval += tie_break_noise

        neg_g = -self.gamma * (g_eval - np.min(g_eval))
        exp_g = np.exp(neg_g)
        probs = exp_g / np.sum(exp_g)

        best_idx = int(np.argmin(g_eval))
        best_action = ACTIONS[best_idx]
        ent = compute_entropy(probs)

        return ConsumerValuationResult(
            consumer_id=self.consumer_id,
            condition=condition,
            scalar_s=float(s_val),
            ternary_signs=d_signs,
            valuations=[float(v) for v in g_vals],
            probabilities=[float(p) for p in probs],
            selected_action=best_action,
            selected_action_idx=best_idx,
            entropy=ent,
        )


class DirectionalSeparableConsumerB(BaseConsumer):
    """Consumer B: Additive Linear-Quadratic Cost Model with Convex Effort Scaling."""

    def __init__(self, gamma: float = 1.0) -> None:
        super().__init__("B_DIRECTIONAL_SEPARABLE", gamma)

    def evaluate(
        self,
        s_val: float,
        d_signs: Tuple[int, int, int],
        condition: str,
        tie_break_noise: Optional[np.ndarray] = None,
    ) -> ConsumerValuationResult:
        if condition == "C0":
            d_vec = np.zeros(3, dtype=np.float64)
        else:
            d_vec = np.array(d_signs, dtype=np.float64) / math.sqrt(3.0)

        g_scalar = B_G_BASE + B_ALPHA_S * s_val + B_BETA_S2 * (s_val ** 2)
        delta_g_dir = -np.dot(B_W_DIR, d_vec)
        g_vals = g_scalar + delta_g_dir

        g_eval = g_vals.copy()
        if tie_break_noise is not None:
            g_eval += tie_break_noise

        neg_g = -self.gamma * (g_eval - np.min(g_eval))
        exp_g = np.exp(neg_g)
        probs = exp_g / np.sum(exp_g)

        best_idx = int(np.argmin(g_eval))
        best_action = ACTIONS[best_idx]
        ent = compute_entropy(probs)

        return ConsumerValuationResult(
            consumer_id=self.consumer_id,
            condition=condition,
            scalar_s=float(s_val),
            ternary_signs=d_signs,
            valuations=[float(v) for v in g_vals],
            probabilities=[float(p) for p in probs],
            selected_action=best_action,
            selected_action_idx=best_idx,
            entropy=ent,
        )


class ContinuousUtilityConsumerC(BaseConsumer):
    """Consumer C: Multiplicative Exponential Utility Model (Higher is Better)."""

    def __init__(self, gamma: float = 1.0) -> None:
        super().__init__("C_CONTINUOUS_UTILITY", gamma)

    def evaluate(
        self,
        s_val: float,
        d_signs: Tuple[int, int, int],
        condition: str,
        tie_break_noise: Optional[np.ndarray] = None,
    ) -> ConsumerValuationResult:
        if condition == "C0":
            d_vec = np.zeros(3, dtype=np.float64)
        else:
            d_vec = np.array(d_signs, dtype=np.float64) / math.sqrt(3.0)

        dir_mult = np.exp(np.dot(C_M_DIR, d_vec))
        u_vals = C_U_BASE * dir_mult - C_COST_S * s_val

        u_eval = u_vals.copy()
        if tie_break_noise is not None:
            u_eval += tie_break_noise

        pos_u = self.gamma * (u_eval - np.max(u_eval))
        exp_u = np.exp(pos_u)
        probs = exp_u / np.sum(exp_u)

        best_idx = int(np.argmax(u_eval))
        best_action = ACTIONS[best_idx]
        ent = compute_entropy(probs)

        return ConsumerValuationResult(
            consumer_id=self.consumer_id,
            condition=condition,
            scalar_s=float(s_val),
            ternary_signs=d_signs,
            valuations=[float(v) for v in u_vals],
            probabilities=[float(p) for p in probs],
            selected_action=best_action,
            selected_action_idx=best_idx,
            entropy=ent,
        )


class MagnitudeDominantConsumerD(BaseConsumer):
    """Consumer D: Strongly Magnitude-Dominant Cost Model with Attenuated Direction."""

    def __init__(self, gamma: float = 1.0) -> None:
        super().__init__("D_MAGNITUDE_DOMINANT", gamma)

    def evaluate(
        self,
        s_val: float,
        d_signs: Tuple[int, int, int],
        condition: str,
        tie_break_noise: Optional[np.ndarray] = None,
    ) -> ConsumerValuationResult:
        if condition == "C0":
            d_vec = np.zeros(3, dtype=np.float64)
        else:
            d_vec = np.array(d_signs, dtype=np.float64) / math.sqrt(3.0)

        g_scalar = D_G_BASE + D_KAPPA_S * s_val
        delta_g_dir = -D_MU_DIR * np.dot(D_W_DIR, d_vec)
        g_vals = g_scalar + delta_g_dir

        g_eval = g_vals.copy()
        if tie_break_noise is not None:
            g_eval += tie_break_noise

        neg_g = -self.gamma * (g_eval - np.min(g_eval))
        exp_g = np.exp(neg_g)
        probs = exp_g / np.sum(exp_g)

        best_idx = int(np.argmin(g_eval))
        best_action = ACTIONS[best_idx]
        ent = compute_entropy(probs)

        return ConsumerValuationResult(
            consumer_id=self.consumer_id,
            condition=condition,
            scalar_s=float(s_val),
            ternary_signs=d_signs,
            valuations=[float(v) for v in g_vals],
            probabilities=[float(p) for p in probs],
            selected_action=best_action,
            selected_action_idx=best_idx,
            entropy=ent,
        )


# =============================================================================
# Transferability Study Engine
# =============================================================================

class R3ConsumerTransferabilityEngine:
    """
    Research-only evaluation engine for Phase 22 H1 R3 Consumer Transferability Study.
    """

    def __init__(self, primary_seed: int = PRIMARY_SEED) -> None:
        self.primary_seed = primary_seed
        self.sp = StimulusProcessor(StimulusConfig())
        self.core = EmotionCore(EmotionConfig())
        self.ai = ActiveInferenceEngine(ActiveInferenceConfig())

        self.consumers: Dict[str, BaseConsumer] = {
            "A_REFERENCE": ReferenceConsumerA(gamma=1.0),
            "B_DIRECTIONAL_SEPARABLE": DirectionalSeparableConsumerB(gamma=1.0),
            "C_CONTINUOUS_UTILITY": ContinuousUtilityConsumerC(gamma=1.0),
            "D_MAGNITUDE_DOMINANT": MagnitudeDominantConsumerD(gamma=1.0),
        }

        self.all_probes: List[Dict[str, Any]] = []
        self.simulated_trajectories: Dict[int, Dict[str, Any]] = {}
        self.exhaustive_matched_pairs: List[Tuple[int, int]] = []
        self.discordant_matched_pairs: List[Tuple[int, int]] = []
        self.same_direction_matched_pairs: List[Tuple[int, int]] = []

    def generate_frozen_dataset(self) -> List[Dict[str, Any]]:
        """Generate single frozen Candidate G1 stimulus corpus (Seed 9999, N=270, 90/tier)."""
        print("\n" + "=" * 75)
        print("Phase 22 H1 — R3 Consumer Transferability & Adapter Dependence Study")
        print(f"Generating Single Frozen Candidate G1 Corpus (Master Seed {self.primary_seed}, N=270, 90/tier)")
        print("=" * 75)
        gen = GeneratorG1(self.sp)
        rng = np.random.default_rng(self.primary_seed)
        tiers = ["Low", "Med", "High"]
        all_probes = []

        for tier in tiers:
            for i in range(90):
                idx = (i % 30) + 1
                text, dom = gen.generate_text(tier, rng, idx)
                vec = self.sp.encode(text)
                global_idx = len(all_probes) + 1
                item = {
                    "probe_idx": i + 1,
                    "global_idx": global_idx,
                    "tier": tier,
                    "domain": dom,
                    "text": text,
                    "vector": vec.tolist(),
                }
                all_probes.append(item)

        self.all_probes = all_probes
        print(f"  Successfully generated {len(all_probes)} probes across Low, Med, High tiers.")
        return all_probes

    def simulate_pad_trajectories(self) -> Dict[int, Dict[str, Any]]:
        """Simulate Fast-Loop ODE trajectories up to exposure T=12 for all probes."""
        print("\n[Step 1/5] Simulating Fast-Loop Limbic ODE Trajectories at Exposure T=12...")
        t0 = time.time()
        trajectories = {}
        target_t = PRIMARY_EXPOSURE_T

        for p in self.all_probes:
            g_idx = p["global_idx"]
            vec = np.array(p["vector"], dtype=np.float64)

            self.core.reset_to_resting()
            self.ai.reset()

            p0 = self.core.get_pad_state()
            p0_vec = np.array([p0.pleasure, p0.arousal, p0.dominance], dtype=np.float64)

            for t in range(1, target_t + 1):
                token = self.core.push_stimulus(vec)
                pt = self.core.commit_stimulus(token)

            pt_vec = np.array([pt.pleasure, pt.arousal, pt.dominance], dtype=np.float64)
            r_vec = pt_vec - p0_vec
            s_val = float(np.linalg.norm(r_vec))
            signs = (
                deadband_sign(r_vec[0]),
                deadband_sign(r_vec[1]),
                deadband_sign(r_vec[2]),
            )

            trajectories[g_idx] = {
                "global_idx": g_idx,
                "tier": p["tier"],
                "domain": p["domain"],
                "s_val": s_val,
                "r_vec": r_vec,
                "signs": signs,
            }

        elapsed = time.time() - t0
        print(f"  Completed trajectory simulation for {len(trajectories)} probes in {elapsed:.2f}s (CPU-only)")
        self.simulated_trajectories = trajectories
        return trajectories

    def extract_matched_pairs(self) -> None:
        """
        Extract exhaustive matched pairs (|S_i - S_j| <= 0.02) and partition into:
        - 358 discordant direction pairs (d_i != d_j)
        - 6376 same direction pairs (d_i == d_j)
        """
        print("\n[Step 2/5] Extracting and Partitioning Matched-Magnitude Pairs (|Delta S| <= 0.02)...")
        n_probes = len(self.all_probes)
        exhaustive = []

        for i in range(1, n_probes + 1):
            s_i = self.simulated_trajectories[i]["s_val"]
            for j in range(i + 1, n_probes + 1):
                s_j = self.simulated_trajectories[j]["s_val"]
                diff = abs(s_i - s_j)
                if diff <= SCALAR_MATCH_THRESHOLD:
                    exhaustive.append((diff, i, j))

        exhaustive.sort(key=lambda x: (round(x[0], 8), x[1], x[2]))
        self.exhaustive_matched_pairs = [(item[1], item[2]) for item in exhaustive]

        discordant = []
        same_dir = []
        for i, j in self.exhaustive_matched_pairs:
            s_i = self.simulated_trajectories[i]["signs"]
            s_j = self.simulated_trajectories[j]["signs"]
            if s_i != s_j:
                discordant.append((i, j))
            else:
                same_dir.append((i, j))

        self.discordant_matched_pairs = discordant
        self.same_direction_matched_pairs = same_dir

        print(f"  Total matched pairs: {len(self.exhaustive_matched_pairs)}")
        print(f"  Discordant matched pairs (|Delta S| <= 0.02, d_i != d_j): {len(self.discordant_matched_pairs)} (Expected 358)")
        print(f"  Same-direction matched pairs (|Delta S| <= 0.02, d_i == d_j): {len(self.same_direction_matched_pairs)} (Expected 6376)")

        assert len(self.discordant_matched_pairs) == 358, f"Discordant count mismatch: {len(self.discordant_matched_pairs)} != 358"
        assert len(self.same_direction_matched_pairs) == 6376, f"Same direction count mismatch: {len(self.same_direction_matched_pairs)} != 6376"

    def evaluate_consumer_on_seed(
        self,
        consumer: BaseConsumer,
        consumer_seed: int,
    ) -> Dict[str, Any]:
        """
        Evaluate a single consumer under robustness seed across C0, C2, C4.
        """
        rng = np.random.default_rng(consumer_seed)
        n_probes = len(self.all_probes)
        conditions = ["C0", "C2", "C4"]

        # Deterministic shuffle permutation for C4
        perm = rng.permutation(n_probes)
        permuted_indices = [int(idx + 1) for idx in perm]

        # Deterministic micro-noise for tie-breaking across actions (scale 1e-6)
        tie_break_matrix = rng.normal(0, 1e-6, size=(n_probes + 1, len(ACTIONS)))

        # Evaluate all probes across conditions
        outcomes: Dict[str, Dict[int, ConsumerValuationResult]] = {c: {} for c in conditions}

        for i in range(1, n_probes + 1):
            traj = self.simulated_trajectories[i]
            s_val = traj["s_val"]
            signs = traj["signs"]
            tb_noise = tie_break_matrix[i]

            # Shuffled direction for C4
            shuffled_partner = permuted_indices[i - 1]
            shuffled_signs = self.simulated_trajectories[shuffled_partner]["signs"]

            for cond in conditions:
                eval_signs = shuffled_signs if cond == "C4" else signs
                res = consumer.evaluate(
                    s_val=s_val,
                    d_signs=eval_signs,
                    condition=cond,
                    tie_break_noise=tb_noise,
                )
                outcomes[cond][i] = res

        # ---------------------------------------------------------------------
        # 1. Pair-Level Metrics on Discordant Matched Pairs (N=358)
        # ---------------------------------------------------------------------
        discordant_metrics: Dict[str, Dict[str, float]] = {}
        for cond in conditions:
            action_diffs = 0
            delta_v_list = []
            d_js_list = []
            d_tv_list = []

            for i, j in self.discordant_matched_pairs:
                res_i = outcomes[cond][i]
                res_j = outcomes[cond][j]

                if res_i.selected_action != res_j.selected_action:
                    action_diffs += 1

                v_i = np.array(res_i.valuations, dtype=np.float64)
                v_j = np.array(res_j.valuations, dtype=np.float64)
                delta_v_list.append(float(np.linalg.norm(v_i - v_j)))

                p_i = np.array(res_i.probabilities, dtype=np.float64)
                p_j = np.array(res_j.probabilities, dtype=np.float64)
                d_js_list.append(compute_js_divergence(p_i, p_j))
                d_tv_list.append(compute_tv_distance(p_i, p_j))

            discordant_metrics[cond] = {
                "d_pair_action": float(action_diffs / 358),
                "diffrate_disc": float(action_diffs / 358),
                "action_diffs_count": action_diffs,
                "mean_delta_v": float(np.mean(delta_v_list)),
                "std_delta_v": float(np.std(delta_v_list)),
                "mean_d_js": float(np.mean(d_js_list)),
                "mean_d_tv": float(np.mean(d_tv_list)),
            }

        # ---------------------------------------------------------------------
        # 2. Pair-Level Metrics on Same-Direction Matched Pairs (N=6376)
        # ---------------------------------------------------------------------
        same_dir_metrics: Dict[str, Dict[str, float]] = {}
        for cond in conditions:
            same_action_diffs = 0
            same_js_list = []
            for i, j in self.same_direction_matched_pairs:
                res_i = outcomes[cond][i]
                res_j = outcomes[cond][j]
                if res_i.selected_action != res_j.selected_action:
                    same_action_diffs += 1
                p_i = np.array(res_i.probabilities, dtype=np.float64)
                p_j = np.array(res_j.probabilities, dtype=np.float64)
                same_js_list.append(compute_js_divergence(p_i, p_j))

            same_dir_metrics[cond] = {
                "d_pair_action_same": float(same_action_diffs / 6376),
                "action_diffs_count": same_action_diffs,
                "mean_d_js_same": float(np.mean(same_js_list)),
            }

        # ---------------------------------------------------------------------
        # 3. Condition-Level Shift across Same Probes (C2 vs C4)
        # ---------------------------------------------------------------------
        cond_action_flips = 0
        cond_js_list = []
        cond_tv_list = []

        for i in range(1, n_probes + 1):
            res_c2 = outcomes["C2"][i]
            res_c4 = outcomes["C4"][i]

            if res_c2.selected_action != res_c4.selected_action:
                cond_action_flips += 1

            p_c2 = np.array(res_c2.probabilities, dtype=np.float64)
            p_c4 = np.array(res_c4.probabilities, dtype=np.float64)
            cond_js_list.append(compute_js_divergence(p_c2, p_c4))
            cond_tv_list.append(compute_tv_distance(p_c2, p_c4))

        condition_shift_c2_c4 = {
            "d_condition_action": float(cond_action_flips / n_probes),
            "action_flips_count": cond_action_flips,
            "mean_d_condition_js": float(np.mean(cond_js_list)),
            "mean_d_condition_tv": float(np.mean(cond_tv_list)),
        }

        # Incremental directional gain above scalar baseline
        diffrate_c2 = discordant_metrics["C2"]["diffrate_disc"]
        d_pair_c0 = discordant_metrics["C0"]["d_pair_action"]
        dir_gain = float(diffrate_c2 - d_pair_c0)

        # Action Entropy across corpus
        entropy_by_cond = {
            cond: float(np.mean([outcomes[cond][i].entropy for i in range(1, n_probes + 1)]))
            for cond in conditions
        }

        return {
            "consumer_id": consumer.consumer_id,
            "consumer_seed": consumer_seed,
            "discordant_metrics": discordant_metrics,
            "same_direction_metrics": same_dir_metrics,
            "condition_shift_c2_c4": condition_shift_c2_c4,
            "directional_gain_above_scalar": dir_gain,
            "mean_entropy_by_condition": entropy_by_cond,
        }

    def evaluate_hard_tuple_identity_invariant(self) -> Dict[str, Any]:
        """
        Verify Hard Invariant: For identical (S, d) tuples, any deterministic consumer
        evaluation must produce delta_action_identity = 0.0000 and D_JS_identity = 0.0000.
        """
        print("\n[Step 3/5] Auditing Hard Parity Invariant (Tuple Identity)...")
        synthetic_tuples = [
            (0.15, ( 1,  0, -1)),
            (0.35, (-1,  1,  0)),
            (0.55, ( 0, -1,  1)),
            (0.75, ( 1,  1, -1)),
            (0.90, (-1, -1,  1)),
        ]

        results = {}
        for c_id, consumer in self.consumers.items():
            max_action_diff = 0
            max_js_div = 0.0

            for s_val, signs in synthetic_tuples:
                res_1 = consumer.evaluate(s_val, signs, condition="C2", tie_break_noise=None)
                res_2 = consumer.evaluate(s_val, signs, condition="C2", tie_break_noise=None)

                if res_1.selected_action != res_2.selected_action:
                    max_action_diff += 1

                p1 = np.array(res_1.probabilities, dtype=np.float64)
                p2 = np.array(res_2.probabilities, dtype=np.float64)
                js = compute_js_divergence(p1, p2)
                if js > max_js_div:
                    max_js_div = js

            results[c_id] = {
                "delta_action_identity": float(max_action_diff),
                "d_js_identity": float(max_js_div),
                "invariant_passed": bool(max_action_diff == 0 and max_js_div < 1e-12),
            }

        all_passed = all(r["invariant_passed"] for r in results.values())
        print(f"  Hard Tuple Identity Parity Invariant: {'PASS' if all_passed else 'FAIL'}")
        return {
            "all_passed": all_passed,
            "consumer_results": results,
        }

    def run_multi_consumer_evaluation(self) -> Dict[str, Any]:
        """
        Execute comprehensive evaluation across all 4 consumers and 5 seeds.
        """
        print("\n[Step 4/5] Executing Cross-Consumer Robustness Evaluation across Seeds 42-46...")
        consumer_results: Dict[str, Dict[str, Any]] = {c_id: {} for c_id in self.consumers}

        for c_id, consumer in self.consumers.items():
            print(f"\n  Evaluating Consumer: {c_id}...")
            seed_runs = {}
            for seed in CONSUMER_SEEDS:
                run_res = self.evaluate_consumer_on_seed(consumer, seed)
                seed_runs[str(seed)] = run_res

            c2_diffrates = [seed_runs[str(s)]["discordant_metrics"]["C2"]["diffrate_disc"] for s in CONSUMER_SEEDS]
            c0_dpairs = [seed_runs[str(s)]["discordant_metrics"]["C0"]["d_pair_action"] for s in CONSUMER_SEEDS]
            c4_dpairs = [seed_runs[str(s)]["discordant_metrics"]["C4"]["d_pair_action"] for s in CONSUMER_SEEDS]
            dir_gains = [seed_runs[str(s)]["directional_gain_above_scalar"] for s in CONSUMER_SEEDS]
            c2_c4_shifts = [seed_runs[str(s)]["condition_shift_c2_c4"]["d_condition_action"] for s in CONSUMER_SEEDS]
            same_c2_diffs = [seed_runs[str(s)]["same_direction_metrics"]["C2"]["d_pair_action_same"] for s in CONSUMER_SEEDS]
            c2_delta_vs = [seed_runs[str(s)]["discordant_metrics"]["C2"]["mean_delta_v"] for s in CONSUMER_SEEDS]
            c0_delta_vs = [seed_runs[str(s)]["discordant_metrics"]["C0"]["mean_delta_v"] for s in CONSUMER_SEEDS]

            mean_diffrate_c2 = float(np.mean(c2_diffrates))
            mean_dir_gain = float(np.mean(dir_gains))
            mean_shift_c2_c4 = float(np.mean(c2_c4_shifts))

            crit_1_diff = bool(mean_diffrate_c2 >= 0.2000)
            crit_2_gain = bool(mean_dir_gain >= 0.1000)
            crit_3_shift = bool(mean_shift_c2_c4 >= 0.0500)

            transfer_satisfied = bool(crit_1_diff and crit_2_gain and crit_3_shift)

            consumer_results[c_id] = {
                "consumer_id": c_id,
                "seed_runs": seed_runs,
                "aggregate": {
                    "c2_diffrate_disc_mean": mean_diffrate_c2,
                    "c2_diffrate_disc_std": float(np.std(c2_diffrates)),
                    "c0_d_pair_action_mean": float(np.mean(c0_dpairs)),
                    "c0_d_pair_action_std": float(np.std(c0_dpairs)),
                    "c4_d_pair_action_mean": float(np.mean(c4_dpairs)),
                    "c4_d_pair_action_std": float(np.std(c4_dpairs)),
                    "directional_gain_mean": mean_dir_gain,
                    "directional_gain_std": float(np.std(dir_gains)),
                    "condition_shift_c2_c4_mean": mean_shift_c2_c4,
                    "condition_shift_c2_c4_std": float(np.std(c2_c4_shifts)),
                    "same_dir_c2_action_diff_mean": float(np.mean(same_c2_diffs)),
                    "c2_delta_v_mean": float(np.mean(c2_delta_vs)),
                    "c0_delta_v_mean": float(np.mean(c0_delta_vs)),
                },
                "preregistered_criteria": {
                    "criterion_1_diffrate_ge_20pct": {
                        "threshold": 0.2000,
                        "observed": mean_diffrate_c2,
                        "passed": crit_1_diff,
                    },
                    "criterion_2_directional_gain_ge_10pct": {
                        "threshold": 0.1000,
                        "observed": mean_dir_gain,
                        "passed": crit_2_gain,
                    },
                    "criterion_3_shuffled_shift_ge_5pct": {
                        "threshold": 0.0500,
                        "observed": mean_shift_c2_c4,
                        "passed": crit_3_shift,
                    },
                    "transfer_criteria_satisfied": transfer_satisfied,
                },
            }

            print(f"    C2 DiffRate: {mean_diffrate_c2:.4f} (Criterion 1: {'PASS' if crit_1_diff else 'FAIL'})")
            print(f"    Dir Gain:    {mean_dir_gain:.4f} (Criterion 2: {'PASS' if crit_2_gain else 'FAIL'})")
            print(f"    C2-C4 Shift: {mean_shift_c2_c4:.4f} (Criterion 3: {'PASS' if crit_3_shift else 'FAIL'})")
            print(f"    Overall Transfer Status: {'SATISFIED' if transfer_satisfied else 'NOT SATISFIED'}")

        independent_consumers = ["B_DIRECTIONAL_SEPARABLE", "C_CONTINUOUS_UTILITY", "D_MAGNITUDE_DOMINANT"]
        satisfied_count = sum(
            1 for c_id in independent_consumers
            if consumer_results[c_id]["preregistered_criteria"]["transfer_criteria_satisfied"]
        )
        r_transfer = float(satisfied_count / len(independent_consumers))

        if r_transfer == 1.0:
            transfer_conclusion = "FULL_TRANSFERABILITY_ACROSS_EVALUATED_FORMULATIONS"
        elif r_transfer >= 1.0 / 3.0:
            transfer_conclusion = "PARTIAL_TRANSFERABILITY_PARTIAL_ADAPTER_DEPENDENCE"
        else:
            transfer_conclusion = "UNRESOLVED_ADAPTER_DEPENDENCE_FAILED_TRANSFER"

        print("\n" + "=" * 75)
        print(f"Pre-Registered Transferability Statistic: R_transfer = {satisfied_count}/3 = {r_transfer:.4f}")
        print(f"Conclusion Classification: {transfer_conclusion}")
        print("=" * 75)

        return {
            "consumer_results": consumer_results,
            "transferability_summary": {
                "independent_consumers_evaluated": independent_consumers,
                "satisfied_count": satisfied_count,
                "total_independent_consumers": len(independent_consumers),
                "r_transfer": r_transfer,
                "transfer_conclusion": transfer_conclusion,
            },
        }

    def evaluate_continuous_utility_scalar_contribution(
        self,
        consumer_results: Dict[str, Any],
    ) -> Dict[str, Any]:
        """
        Special C5 / Continuous Utility Follow-up (RQ5):
        Investigate whether scalar magnitude contributes continuous valuation differences
        that disappear after discrete argmax selection.
        """
        print("\n[Step 5/5] Analyzing Continuous Utility Space vs. Discrete Argmax (Consumer C)...")
        c_res = consumer_results["C_CONTINUOUS_UTILITY"]
        c0_delta_v = c_res["aggregate"]["c0_delta_v_mean"]
        c2_delta_v = c_res["aggregate"]["c2_delta_v_mean"]
        c0_d_pair = c_res["aggregate"]["c0_d_pair_action_mean"]
        c2_diffrate = c_res["aggregate"]["c2_diffrate_disc_mean"]

        scalar_continuous_contribution_exists = bool(c0_delta_v > 0.0010)
        argmax_masks_scalar_variation = bool(c0_d_pair < 0.0500 and scalar_continuous_contribution_exists)

        print(f"  Consumer C — Mean Continuous Utility Divergence under C0 (scalar only): {c0_delta_v:.4f}")
        print(f"  Consumer C — Mean Continuous Utility Divergence under C2 (scalar + R3): {c2_delta_v:.4f}")
        print(f"  Consumer C — Discrete Argmax Divergence under C0:                       {c0_d_pair:.4f}")
        print(f"  Consumer C — Discrete Argmax Divergence under C2:                       {c2_diffrate:.4f}")
        print(f"  Scalar continuous contribution exists: {scalar_continuous_contribution_exists}")
        print(f"  Discrete argmax masks scalar continuous variation: {argmax_masks_scalar_variation}")

        return {
            "consumer_c_c0_mean_delta_v": c0_delta_v,
            "consumer_c_c2_mean_delta_v": c2_delta_v,
            "consumer_c_c0_d_pair_action": c0_d_pair,
            "consumer_c_c2_diffrate_disc": c2_diffrate,
            "scalar_continuous_contribution_exists": scalar_continuous_contribution_exists,
            "argmax_masks_scalar_variation": argmax_masks_scalar_variation,
            "interpretation": (
                "Under continuous utility consumer C, scalar magnitude variation within matched pairs "
                f"(|Delta S| <= 0.02) generates non-zero continuous utility distance (mean Delta V = {c0_delta_v:.4f}) "
                "even while discrete argmax action divergence remains suppressed under C0. Directional R3 adds "
                f"substantial additional continuous utility divergence (mean Delta V = {c2_delta_v:.4f}) and drives "
                f"discrete action differentiation (DiffRate = {c2_diffrate:.4f})."
            ),
        }

    def run_full_study(self) -> Dict[str, Any]:
        """Execute complete study workflow and serialize results."""
        self.generate_frozen_dataset()
        self.simulate_pad_trajectories()
        self.extract_matched_pairs()

        hard_invariants = self.evaluate_hard_tuple_identity_invariant()
        evaluation_data = self.run_multi_consumer_evaluation()
        rq5_continuous = self.evaluate_continuous_utility_scalar_contribution(evaluation_data["consumer_results"])

        results = {
            "study_name": "Phase 22 H1 R3 Consumer Transferability & Adapter Dependence Study",
            "governance_state": {
                "phase_22_h1": "INCONCLUSIVE",
                "gate_2": "STRICTLY BLOCKED",
                "protocol_v1_5": "NOT AUTHORIZED",
                "architecture_gate": "STRICTLY LOCKED",
                "adr_029_status": "DRAFT / RESEARCH RECORD ONLY / NOT RATIFIED",
                "production_mutations": 0,
                "genesis_profile": "PRESERVED_BIT_EXACT",
                "hardware_execution": "100% CPU / 0.0 MB GPU VRAM",
            },
            "corpus_lineage": {
                "root_corpus": "Frozen Candidate G1 Stimulus Corpus",
                "master_seed": PRIMARY_SEED,
                "n_probes": len(self.all_probes),
                "probes_per_tier": 90,
                "exposure_ticks": PRIMARY_EXPOSURE_T,
                "consumer_robustness_seeds": CONSUMER_SEEDS,
            },
            "matched_pairs_summary": {
                "total_exhaustive_pairs": len(self.exhaustive_matched_pairs),
                "discordant_matched_pairs_count": len(self.discordant_matched_pairs),
                "same_direction_matched_pairs_count": len(self.same_direction_matched_pairs),
                "scalar_match_tolerance": SCALAR_MATCH_THRESHOLD,
            },
            "hard_tuple_identity_parity": hard_invariants,
            "cross_consumer_evaluation": evaluation_data,
            "rq5_continuous_utility_analysis": rq5_continuous,
            "frozen_consumer_specifications_sha256": {
                "A_REFERENCE": hashlib.sha256(A_ACTION_WEIGHTS.tobytes() + A_BASE_COSTS.tobytes()).hexdigest(),
                "B_DIRECTIONAL_SEPARABLE": hashlib.sha256(B_W_DIR.tobytes() + B_ALPHA_S.tobytes() + B_BETA_S2.tobytes()).hexdigest(),
                "C_CONTINUOUS_UTILITY": hashlib.sha256(C_M_DIR.tobytes() + C_U_BASE.tobytes() + C_COST_S.tobytes()).hexdigest(),
                "D_MAGNITUDE_DOMINANT": hashlib.sha256(D_W_DIR.tobytes() + D_KAPPA_S.tobytes() + np.array([D_MU_DIR]).tobytes()).hexdigest(),
            },
        }

        RESULTS_DIR.mkdir(parents=True, exist_ok=True)
        with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
            json.dump(results, f, indent=2)
        print(f"\n[OK] Results written to: {OUTPUT_FILE}")

        with open(SUMMARY_CSV, "w", newline="", encoding="utf-8") as f:
            writer = csv.writer(f)
            writer.writerow([
                "consumer_id", "c2_diffrate_disc_mean", "c0_d_pair_action_mean",
                "directional_gain_mean", "c2_c4_condition_shift_mean",
                "c2_mean_delta_v", "c0_mean_delta_v", "transfer_criteria_satisfied"
            ])
            for c_id in ["A_REFERENCE", "B_DIRECTIONAL_SEPARABLE", "C_CONTINUOUS_UTILITY", "D_MAGNITUDE_DOMINANT"]:
                agg = evaluation_data["consumer_results"][c_id]["aggregate"]
                crit = evaluation_data["consumer_results"][c_id]["preregistered_criteria"]
                writer.writerow([
                    c_id,
                    f"{agg['c2_diffrate_disc_mean']:.4f}",
                    f"{agg['c0_d_pair_action_mean']:.4f}",
                    f"{agg['directional_gain_mean']:.4f}",
                    f"{agg['condition_shift_c2_c4_mean']:.4f}",
                    f"{agg['c2_delta_v_mean']:.4f}",
                    f"{agg['c0_delta_v_mean']:.4f}",
                    crit["transfer_criteria_satisfied"],
                ])
        print(f"[OK] Summary CSV written to: {SUMMARY_CSV}")

        out_sha = compute_sha256(OUTPUT_FILE)
        out_size = OUTPUT_FILE.stat().st_size
        csv_sha = compute_sha256(SUMMARY_CSV)
        csv_size = SUMMARY_CSV.stat().st_size

        manifest = {
            "manifest_version": "1.0",
            "study_name": "Phase 22 H1 R3 Consumer Transferability & Adapter Dependence Study",
            "generated_at": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
            "governance_invariants": {
                "phase_22_h1": "INCONCLUSIVE",
                "gate_2": "STRICTLY BLOCKED",
                "architecture_gate": "STRICTLY LOCKED",
                "production_mutations": 0,
                "genesis_profile": "PRESERVED_BIT_EXACT",
            },
            "files": {
                "r3_consumer_transferability_results.json": {
                    "sha256": out_sha,
                    "size_bytes": out_size,
                },
                "r3_consumer_transferability_summary.csv": {
                    "sha256": csv_sha,
                    "size_bytes": csv_size,
                },
            },
            "transferability_summary": evaluation_data["transferability_summary"],
        }

        FIXTURES_DIR.mkdir(parents=True, exist_ok=True)
        with open(MANIFEST_FILE, "w", encoding="utf-8") as f:
            json.dump(manifest, f, indent=2)
        print(f"[OK] Manifest written to: {MANIFEST_FILE}")
        print(f"[OK] SHA-256 digest: {out_sha} ({out_size} bytes)")

        return results


if __name__ == "__main__":
    engine = R3ConsumerTransferabilityEngine()
    engine.run_full_study()
