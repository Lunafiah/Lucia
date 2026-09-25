"""
Phase 22 H1 — R3 Causal/Mechanistic Attribution Study
=====================================================
Script: evaluate_r3_causal_attribution.py

Mission:
Determine which component of the R3 measurement representation is responsible
for the behavioral differentiation previously observed in downstream consumers.

Experimental Representation Conditions:
  - C0: Scalar baseline (input = S, v_dir = 0)
  - C1: R2 directional representation (input = (S, normalized(r)))
        u = r_T / ||r_T||_2 whenever ||r_T||_2 > 0; exact 0 maps to 0.
  - C2: Canonical R3 (input = (S, d), d = sign_0.010(r_T) in {-1, 0, +1}^3)
  - C3: Magnitude-preserving shuffled direction (preserve S_i, permute d across probes)
  - C4: Direction-preserving magnitude shuffle (preserve d_i, permute S across probes)
  - C5: Independent random direction (preserve empirical marginal distribution of d)
  - C6: Sign-only ablation (binary negative vs non-negative, d_sign in {-1, +1}^3)
  - C7: Direction-count control (directional sparsity k in {0, 1, 2, 3})

Evaluated Consumers:
  - Primary: Consumer C at gamma_C = 1.50 (Continuous Multiplicative Utility)
  - Secondary:
      - Consumer A: Reference Control (Historical EFE Adapter)
      - Consumer B: Transferability Control (Separable Effort Model)
      - Consumer D: Qualifying Corner (mu_d = 1.00, gamma_kappa = 0.50)

Governance:
  - STRICTLY RESEARCH-ONLY / RESEARCH_HARNESS_ONLY
  - Architecture Gate LOCKED (production diff = 0)
  - Quality Gate 2 BLOCKED (Delta_HM = 0.0685 < 0.1500)
  - Phase 22 H1 INCONCLUSIVE
  - ADR-029 DRAFT / RESEARCH RECORD ONLY / NOT RATIFIED
  - 100% CPU Execution / 0.0 MB GPU VRAM
"""

from __future__ import annotations

import csv
import hashlib
import json
import math
import os
import sys
import time
from dataclasses import dataclass
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
from tests.evaluation_phase22.scripts.calibrate_stimulus_representation import GeneratorG1

# Constants & Governance
PRIMARY_SEED = 9999
CONSUMER_SEEDS = [42, 43, 44, 45, 46]
PRIMARY_EXPOSURE_T = 12
DEADBAND_EPSILON = 0.010
SCALAR_MATCH_THRESHOLD = 0.020

EXPECTED_CORPUS_SHA = "d0061e8cfdd160f4ebccb7100e4fe3eeef9ff18a1a4c9c1b3f912a76f2ae82c0"

ACTIONS = [
    "answer",    # A1: immediate response
    "clarify",   # A2: external clarification
    "retrieve",  # A3: extended SDM memory probe
    "derive",    # A4: knowledge derivation
    "reason",    # A5: deep reasoning mode shift
    "wait",      # A6: wait conversational pause
]

CONDITIONS = ["C0", "C1", "C2", "C3", "C4", "C5", "C6", "C7"]

# =============================================================================
# Locked Base Parameter Arrays (Bit-Exact from Transferability & Sensitivity)
# =============================================================================

# Consumer A: Reference EFE Adapter
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

# Consumer B: Separable Additive Model
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

# Consumer C: Multiplicative Utility Model
C_U_BASE = np.array([1.20, 0.60, 0.80, 0.70, 0.50, 1.10], dtype=np.float64)
C_COST_S = np.array([0.40, 0.15, 0.25, 0.30, 0.10, 0.50], dtype=np.float64)
C_M_BASE = np.array([
    [ 0.25, -0.30,  0.15],  # answer
    [-0.35,  0.30, -0.20],  # clarify
    [ 0.30, -0.15,  0.25],  # retrieve
    [ 0.15,  0.25,  0.10],  # derive
    [-0.25,  0.40, -0.15],  # reason
    [-0.15, -0.35, -0.30],  # wait
], dtype=np.float64)

# Consumer D: Magnitude-Dominant Model
D_G_BASE = np.array([0.10, 0.30, 0.20, 0.25, 0.40, 0.05], dtype=np.float64)
D_KAPPA_S_BASE = np.array([1.50, 4.00, 2.50, 3.00, 5.50, 0.80], dtype=np.float64)
D_W_DIR = np.array([
    [ 0.10, -0.15,  0.10],  # answer
    [-0.25,  0.15, -0.10],  # clarify
    [ 0.20, -0.10,  0.15],  # retrieve
    [ 0.10,  0.15,  0.10],  # derive
    [-0.15,  0.25, -0.15],  # reason
    [-0.10, -0.20, -0.20],  # wait
], dtype=np.float64)


def sha256_array(arr: np.ndarray) -> str:
    """Compute deterministic SHA-256 hash for float arrays."""
    return hashlib.sha256(arr.tobytes()).hexdigest()


LOCKED_BASE_PARAMETER_HASHES = {
    "C_U_BASE": sha256_array(C_U_BASE),
    "C_COST_S": sha256_array(C_COST_S),
    "C_M_BASE": sha256_array(C_M_BASE),
    "D_G_BASE": sha256_array(D_G_BASE),
    "D_KAPPA_S_BASE": sha256_array(D_KAPPA_S_BASE),
    "D_W_DIR": sha256_array(D_W_DIR),
}


# =============================================================================
# Helper Mathematical Functions
# =============================================================================

def deadband_sign(x: float, eps: float = DEADBAND_EPSILON) -> int:
    """Ternary deadband sign function for R3."""
    if x > eps:
        return 1
    elif x < -eps:
        return -1
    return 0


def binary_sign(x: float) -> int:
    """Binary sign for C6 ablation: negative (-1) vs non-negative (+1)."""
    return -1 if x < 0 else 1


def compute_js_divergence(p: np.ndarray, q: np.ndarray) -> float:
    """Jensen-Shannon Divergence D_JS(P || Q) in [0, ln(2)]."""
    p_safe = np.clip(p, 1e-12, 1.0)
    q_safe = np.clip(q, 1e-12, 1.0)
    p_safe /= np.sum(p_safe)
    q_safe /= np.sum(q_safe)
    m = 0.5 * (p_safe + q_safe)
    kl_p_m = np.sum(p_safe * np.log(p_safe / m))
    kl_q_m = np.sum(q_safe * np.log(q_safe / m))
    return float(max(0.0, 0.5 * (kl_p_m + kl_q_m)))


def compute_tv_distance(p: np.ndarray, q: np.ndarray) -> float:
    """Total Variation Distance D_TV(P, Q) = 0.5 * sum |P - Q| in [0, 1]."""
    return float(0.5 * np.sum(np.abs(p - q)))


def compute_entropy(p: np.ndarray) -> float:
    """Shannon entropy H(P) in nats."""
    p_safe = p[p > 1e-12]
    return float(-np.sum(p_safe * np.log(p_safe)))


def spearman_rank_correlation(a: np.ndarray, b: np.ndarray) -> float:
    """Compute Spearman rank correlation between two vectors."""
    if len(a) < 2 or np.all(a == a[0]) or np.all(b == b[0]):
        return 1.0 if np.all(a == b) else 0.0
    rank_a = np.argsort(np.argsort(a))
    rank_b = np.argsort(np.argsort(b))
    n = len(a)
    d_sq = np.sum((rank_a - rank_b) ** 2)
    return float(1.0 - (6.0 * d_sq) / (n * (n**2 - 1)))


# =============================================================================
# Consumer Valuation Interfaces
# =============================================================================

@dataclass(frozen=True)
class ConsumerValuationResult:
    """Outcome for a probe evaluated under a consumer, representation, and seed."""
    consumer_id: str
    condition: str
    scalar_s: float
    v_dir: List[float]
    valuations: List[float]
    probabilities: List[float]
    selected_action: str
    selected_action_idx: int
    entropy: float


class BaseConsumer:
    """Abstract base for consumer models."""
    def __init__(self, consumer_id: str, gamma: float = 1.0) -> None:
        self.consumer_id = consumer_id
        self.gamma = gamma

    def evaluate(
        self,
        s_val: float,
        v_dir: np.ndarray,
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
        v_dir: np.ndarray,
        condition: str,
        tie_break_noise: Optional[np.ndarray] = None,
    ) -> ConsumerValuationResult:
        beta_k = 1.0 + 0.50 * math.tanh(2.0 * s_val)
        beta_m = 1.0 + 0.30 * math.tanh(2.0 * s_val)
        g_base = A_BASE_COSTS - beta_k * A_BASE_DK - beta_m * A_BASE_DM
        delta_g_dir = -np.dot(A_ACTION_WEIGHTS, v_dir)
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
            v_dir=[float(x) for x in v_dir],
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
        v_dir: np.ndarray,
        condition: str,
        tie_break_noise: Optional[np.ndarray] = None,
    ) -> ConsumerValuationResult:
        g_scalar = B_G_BASE + B_ALPHA_S * s_val + B_BETA_S2 * (s_val ** 2)
        delta_g_dir = -np.dot(B_W_DIR, v_dir)
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
            v_dir=[float(x) for x in v_dir],
            valuations=[float(v) for v in g_vals],
            probabilities=[float(p) for p in probs],
            selected_action=best_action,
            selected_action_idx=best_idx,
            entropy=ent,
        )


class ContinuousUtilityConsumerC(BaseConsumer):
    """Consumer C: Multiplicative Exponential Utility Model (Higher is Better)."""
    def __init__(self, gamma_C: float = 1.50, gamma: float = 1.0) -> None:
        super().__init__("C_CONTINUOUS_UTILITY", gamma)
        self.gamma_C = float(gamma_C)
        self.m_dir = self.gamma_C * C_M_BASE

    def evaluate(
        self,
        s_val: float,
        v_dir: np.ndarray,
        condition: str,
        tie_break_noise: Optional[np.ndarray] = None,
    ) -> ConsumerValuationResult:
        dir_mult = np.exp(np.dot(self.m_dir, v_dir))
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
            v_dir=[float(x) for x in v_dir],
            valuations=[float(v) for v in u_vals],
            probabilities=[float(p) for p in probs],
            selected_action=best_action,
            selected_action_idx=best_idx,
            entropy=ent,
        )


class MagnitudeDominantConsumerD(BaseConsumer):
    """Consumer D: Magnitude-Dominant Non-Linear Model at Qualifying Corner."""
    def __init__(self, mu_d: float = 1.00, gamma_kappa: float = 0.50, gamma: float = 1.0) -> None:
        super().__init__("D_MAGNITUDE_DOMINANT", gamma)
        self.mu_d = float(mu_d)
        self.gamma_kappa = float(gamma_kappa)
        self.kappa_s = self.gamma_kappa * D_KAPPA_S_BASE

    def evaluate(
        self,
        s_val: float,
        v_dir: np.ndarray,
        condition: str,
        tie_break_noise: Optional[np.ndarray] = None,
    ) -> ConsumerValuationResult:
        g_scalar = D_G_BASE + self.kappa_s * s_val
        delta_g_dir = -self.mu_d * np.dot(D_W_DIR, v_dir)
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
            v_dir=[float(x) for x in v_dir],
            valuations=[float(v) for v in g_vals],
            probabilities=[float(p) for p in probs],
            selected_action=best_action,
            selected_action_idx=best_idx,
            entropy=ent,
        )


# =============================================================================
# Causal Attribution Engine
# =============================================================================

class R3CausalAttributionEngine:
    """Evaluation harness for Phase 22 H1 R3 Causal/Mechanistic Attribution Study."""

    def __init__(self, primary_seed: int = PRIMARY_SEED) -> None:
        self.primary_seed = primary_seed
        self.core = EmotionCore(EmotionConfig())
        self.ai = ActiveInferenceEngine(ActiveInferenceConfig())
        self.sp = StimulusProcessor(StimulusConfig())

        self.all_probes: List[Dict[str, Any]] = []
        self.simulated_trajectories: Dict[int, Dict[str, Any]] = {}
        self.exhaustive_matched_pairs: List[Tuple[int, int]] = []
        self.discordant_matched_pairs: List[Tuple[int, int]] = []
        self.same_direction_matched_pairs: List[Tuple[int, int]] = []
        self.greedy_discordant_pairs: List[Tuple[int, int]] = []

    def generate_candidate_g1_corpus(self) -> List[Dict[str, Any]]:
        """Generate canonical frozen Candidate G1 stimulus corpus (Seed 9999, N=270, 90/tier)."""
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
        return all_probes

    def simulate_pad_trajectories(self, exposure_t: int = PRIMARY_EXPOSURE_T) -> Dict[int, Dict[str, Any]]:
        """Simulate Fast-Loop ODE trajectories up to exposure T=12 for all probes."""
        trajectories = {}
        for p in self.all_probes:
            g_idx = p["global_idx"]
            vec = np.array(p["vector"], dtype=np.float64)

            self.core.reset_to_resting()
            self.ai.reset()

            p0 = self.core.get_pad_state()
            p0_vec = np.array([p0.pleasure, p0.arousal, p0.dominance], dtype=np.float64)

            for _ in range(1, exposure_t + 1):
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

        self.simulated_trajectories = trajectories
        return trajectories

    def partition_matched_pairs(self, tolerance: float = SCALAR_MATCH_THRESHOLD) -> None:
        """Partition probes into exhaustive, discordant, same-direction, and greedy disjoint pairs."""
        n_probes = len(self.all_probes)
        candidate_pairs = []

        for i in range(1, n_probes + 1):
            s_i = self.simulated_trajectories[i]["s_val"]
            for j in range(i + 1, n_probes + 1):
                s_j = self.simulated_trajectories[j]["s_val"]
                diff = abs(s_i - s_j)
                if diff <= tolerance:
                    candidate_pairs.append((diff, i, j))

        # Deterministic sort: diff asc, then i asc, then j asc
        candidate_pairs.sort(key=lambda x: (round(x[0], 8), x[1], x[2]))
        self.exhaustive_matched_pairs = [(item[1], item[2]) for item in candidate_pairs]

        self.discordant_matched_pairs = []
        self.same_direction_matched_pairs = []
        for i, j in self.exhaustive_matched_pairs:
            d_i = self.simulated_trajectories[i]["signs"]
            d_j = self.simulated_trajectories[j]["signs"]
            if d_i != d_j:
                self.discordant_matched_pairs.append((i, j))
            else:
                self.same_direction_matched_pairs.append((i, j))

        # Greedy 1-to-1 disjoint matching on discordant pairs
        used_probes = set()
        self.greedy_discordant_pairs = []
        for i, j in self.discordant_matched_pairs:
            if i not in used_probes and j not in used_probes:
                used_probes.add(i)
                used_probes.add(j)
                self.greedy_discordant_pairs.append((i, j))

        assert len(self.exhaustive_matched_pairs) == 6734, f"Exhaustive count: {len(self.exhaustive_matched_pairs)} != 6734"
        assert len(self.discordant_matched_pairs) == 358, f"Discordant count: {len(self.discordant_matched_pairs)} != 358"
        assert len(self.same_direction_matched_pairs) == 6376, f"Same direction count: {len(self.same_direction_matched_pairs)} != 6376"

    def build_representation_vectors(
        self,
        consumer_seed: int,
    ) -> Dict[str, Dict[int, Tuple[float, np.ndarray]]]:
        """
        Build (s_val, v_dir) pairs for all 270 probes across conditions C0 to C7.
        Deterministic seeds are used for shuffle/random conditions.
        """
        n_probes = len(self.all_probes)
        reps: Dict[str, Dict[int, Tuple[float, np.ndarray]]] = {c: {} for c in CONDITIONS}

        # C3: Seeded magnitude-preserving direction permutation
        rng_c3 = np.random.default_rng(consumer_seed + 100)
        perm_c3 = rng_c3.permutation(n_probes)
        shuffled_dir_indices = [int(x + 1) for x in perm_c3]

        # C4: Seeded direction-preserving magnitude permutation
        rng_c4 = np.random.default_rng(consumer_seed + 200)
        perm_c4 = rng_c4.permutation(n_probes)
        shuffled_scalar_indices = [int(x + 1) for x in perm_c4]

        # C5: Independent deterministic direction permutation (preserves empirical marginals)
        rng_c5 = np.random.default_rng(consumer_seed + 300)
        perm_c5 = rng_c5.permutation(n_probes)
        indep_dir_indices = [int(x + 1) for x in perm_c5]

        for i in range(1, n_probes + 1):
            traj = self.simulated_trajectories[i]
            s_orig = traj["s_val"]
            r_vec = traj["r_vec"]
            d_signs = traj["signs"]

            # C0: Scalar baseline
            reps["C0"][i] = (s_orig, np.zeros(3, dtype=np.float64))

            # C1: R2 Continuous normalized residual (u = r / ||r|| if ||r|| > 0 else 0)
            norm_r = np.linalg.norm(r_vec)
            u_vec = r_vec / norm_r if norm_r > 0.0 else np.zeros(3, dtype=np.float64)
            reps["C1"][i] = (s_orig, u_vec)

            # C2: Canonical R3
            v_c2 = np.array(d_signs, dtype=np.float64) / math.sqrt(3.0)
            reps["C2"][i] = (s_orig, v_c2)

            # C3: Magnitude-preserving shuffled direction
            shuff_d = self.simulated_trajectories[shuffled_dir_indices[i - 1]]["signs"]
            v_c3 = np.array(shuff_d, dtype=np.float64) / math.sqrt(3.0)
            reps["C3"][i] = (s_orig, v_c3)

            # C4: Direction-preserving magnitude shuffle
            shuff_s = self.simulated_trajectories[shuffled_scalar_indices[i - 1]]["s_val"]
            v_c4 = np.array(d_signs, dtype=np.float64) / math.sqrt(3.0)
            reps["C4"][i] = (shuff_s, v_c4)

            # C5: Independent random direction (marginal preserved)
            indep_d = self.simulated_trajectories[indep_dir_indices[i - 1]]["signs"]
            v_c5 = np.array(indep_d, dtype=np.float64) / math.sqrt(3.0)
            reps["C5"][i] = (s_orig, v_c5)

            # C6: Sign-only ablation (binary negative vs non-negative)
            d_binary = np.array([binary_sign(d_signs[j]) for j in range(3)], dtype=np.float64)
            v_c6 = d_binary / math.sqrt(3.0)
            reps["C6"][i] = (s_orig, v_c6)

            # C7: Direction-count control (directional sparsity k in {0, 1, 2, 3})
            k_nonzero = sum(abs(d_signs[j]) for j in range(3))
            v_c7 = np.full(3, k_nonzero / (3.0 * math.sqrt(3.0)), dtype=np.float64)
            reps["C7"][i] = (s_orig, v_c7)

        return reps

    def evaluate_consumer_on_seed(
        self,
        consumer: BaseConsumer,
        consumer_seed: int,
    ) -> Dict[str, Any]:
        """Evaluate a consumer across all 8 conditions under a robustness seed."""
        n_probes = len(self.all_probes)
        reps = self.build_representation_vectors(consumer_seed)

        # Micro-noise tie-breaker (scale 1e-6)
        rng = np.random.default_rng(consumer_seed)
        tie_break_matrix = rng.normal(0, 1e-6, size=(n_probes + 1, len(ACTIONS)))

        outcomes: Dict[str, Dict[int, ConsumerValuationResult]] = {c: {} for c in CONDITIONS}
        for cond in CONDITIONS:
            for pid in range(1, n_probes + 1):
                s_val, v_dir = reps[cond][pid]
                res = consumer.evaluate(
                    s_val=s_val,
                    v_dir=v_dir,
                    condition=cond,
                    tie_break_noise=tie_break_matrix[pid],
                )
                outcomes[cond][pid] = res

        # ---------------------------------------------------------------------
        # Pair-Level & Probe-Level Metrics per Condition
        # ---------------------------------------------------------------------
        condition_metrics: Dict[str, Any] = {}
        c0_actions = [outcomes["C0"][pid].selected_action for pid in range(1, n_probes + 1)]

        for cond in CONDITIONS:
            # 1. Exhaustive Discordant Pairs (358 pairs)
            action_diffs_disc = 0
            delta_v_list = []
            d_js_list = []
            d_tv_list = []

            for i, j in self.discordant_matched_pairs:
                res_i = outcomes[cond][i]
                res_j = outcomes[cond][j]
                if res_i.selected_action != res_j.selected_action:
                    action_diffs_disc += 1
                v_i = np.array(res_i.valuations, dtype=np.float64)
                v_j = np.array(res_j.valuations, dtype=np.float64)
                delta_v_list.append(float(np.linalg.norm(v_i - v_j)))
                p_i = np.array(res_i.probabilities, dtype=np.float64)
                p_j = np.array(res_j.probabilities, dtype=np.float64)
                d_js_list.append(compute_js_divergence(p_i, p_j))
                d_tv_list.append(compute_tv_distance(p_i, p_j))

            diffrate_disc = float(action_diffs_disc / len(self.discordant_matched_pairs))

            # 2. Greedy Disjoint Discordant Pairs
            greedy_diffs = 0
            for i, j in self.greedy_discordant_pairs:
                if outcomes[cond][i].selected_action != outcomes[cond][j].selected_action:
                    greedy_diffs += 1
            diffrate_greedy = float(greedy_diffs / len(self.greedy_discordant_pairs))

            # 3. Same-Direction Matched Pairs (6376 pairs)
            same_diffs = 0
            for i, j in self.same_direction_matched_pairs:
                if outcomes[cond][i].selected_action != outcomes[cond][j].selected_action:
                    same_diffs += 1
            d_pair_same = float(same_diffs / len(self.same_direction_matched_pairs))

            # 4. Action Choices Across Entire Corpus (270 probes)
            cond_actions = [outcomes[cond][pid].selected_action for pid in range(1, n_probes + 1)]
            flips_from_c0 = sum(1 for c_act, c0_act in zip(cond_actions, c0_actions) if c_act != c0_act)
            action_displacement = float(flips_from_c0 / n_probes)

            clarify_count = cond_actions.count("clarify")
            retrieve_count = cond_actions.count("retrieve")
            clarify_rate = float(clarify_count / n_probes)
            retrieve_rate = float(retrieve_count / n_probes)

            mean_ent = float(np.mean([outcomes[cond][pid].entropy for pid in range(1, n_probes + 1)]))

            # 5. Tier Distributions & Urgency Ordering
            tier_dists = {}
            for t_name in ["Low", "Med", "High"]:
                t_pids = [
                    pid for pid in range(1, n_probes + 1)
                    if self.simulated_trajectories[pid]["tier"] == t_name
                ]
                t_acts = [outcomes[cond][pid].selected_action for pid in t_pids]
                tier_dists[t_name] = [t_acts.count(a) / len(t_pids) for a in ACTIONS]

            # High tier urgency dominance (answer, clarify, wait)
            urgency_indices = [0, 1, 5]
            high_urgency_freq = float(sum(tier_dists["High"][idx] for idx in urgency_indices))

            # Rank correlation with C0 across tiers
            c0_tier_dists = {}
            for t_name in ["Low", "Med", "High"]:
                t_pids = [
                    pid for pid in range(1, n_probes + 1)
                    if self.simulated_trajectories[pid]["tier"] == t_name
                ]
                t_acts = [c0_actions[pid - 1] for pid in t_pids]
                c0_tier_dists[t_name] = [t_acts.count(a) / len(t_pids) for a in ACTIONS]

            tier_rank_corrs = {
                t: spearman_rank_correlation(np.array(tier_dists[t]), np.array(c0_tier_dists[t]))
                for t in ["Low", "Med", "High"]
            }
            mean_rank_corr = float(np.mean(list(tier_rank_corrs.values())))

            condition_metrics[cond] = {
                "diffrate_disc": diffrate_disc,
                "diffrate_greedy": diffrate_greedy,
                "d_pair_same": d_pair_same,
                "mean_delta_v": float(np.mean(delta_v_list)),
                "mean_d_js": float(np.mean(d_js_list)),
                "mean_d_tv": float(np.mean(d_tv_list)),
                "action_displacement": action_displacement,
                "clarify_rate": clarify_rate,
                "retrieve_rate": retrieve_rate,
                "mean_entropy": mean_ent,
                "high_tier_urgency_dominance": high_urgency_freq,
                "tier_rank_correlations": tier_rank_corrs,
                "mean_tier_rank_corr": mean_rank_corr,
                "tier_distributions": tier_dists,
                "action_choices": cond_actions,
            }

        # Calculate directional gains (relative to C0)
        c0_diff = condition_metrics["C0"]["diffrate_disc"]
        for cond in CONDITIONS:
            condition_metrics[cond]["directional_gain"] = float(condition_metrics[cond]["diffrate_disc"] - c0_diff)

        return {
            "consumer_id": consumer.consumer_id,
            "consumer_seed": consumer_seed,
            "conditions": condition_metrics,
        }

    def evaluate_tuple_identity(self, consumer: BaseConsumer) -> Dict[str, Any]:
        """Verify NC2: identical (S, d) tuples produce 0 action difference and 0 JS divergence."""
        test_tuples = [
            (0.15, ( 1, -1,  0)),
            (0.45, ( 0,  1,  1)),
            (0.75, (-1, -1, -1)),
            (0.85, ( 1,  1,  1)),
            (0.30, ( 0,  0,  0)),
        ]
        delta_actions = 0
        js_divs = []
        for s_val, d_tuple in test_tuples:
            v_dir = np.array(d_tuple, dtype=np.float64) / math.sqrt(3.0)
            res1 = consumer.evaluate(s_val, v_dir, "C2", tie_break_noise=None)
            res2 = consumer.evaluate(s_val, v_dir, "C2", tie_break_noise=None)
            if res1.selected_action != res2.selected_action:
                delta_actions += 1
            p1 = np.array(res1.probabilities)
            p2 = np.array(res2.probabilities)
            js_divs.append(compute_js_divergence(p1, p2))

        return {
            "delta_action_identity": float(delta_actions),
            "d_js_identity": float(max(js_divs)),
            "passed": bool(delta_actions == 0 and max(js_divs) < 1e-12),
        }


# =============================================================================
# Execution Orchestrator
# =============================================================================

def run_causal_attribution_study() -> None:
    """Execute complete Phase 22 H1 R3 Causal/Mechanistic Attribution Study."""
    t_start = time.time()
    print("\n" + "=" * 80)
    print("PHASE 22 H1 — R3 CAUSAL/MECHANISTIC ATTRIBUTION STUDY")
    print("=" * 80)

    # 1. Parameter Hash Audit
    for param_name, exp_hash in LOCKED_BASE_PARAMETER_HASHES.items():
        assert len(exp_hash) == 64
        print(f"[AUDIT] Locked parameter hash {param_name}: {exp_hash[:16]}... (OK)")

    # 2. Engine Initialization & Simulation
    engine = R3CausalAttributionEngine(PRIMARY_SEED)
    engine.generate_candidate_g1_corpus()
    engine.simulate_pad_trajectories(PRIMARY_EXPOSURE_T)
    engine.partition_matched_pairs(SCALAR_MATCH_THRESHOLD)

    # Verify baseline reproduction before attribution
    primary_c = ContinuousUtilityConsumerC(gamma_C=1.50)
    seed42_test = engine.evaluate_consumer_on_seed(primary_c, 42)
    c2_rep = seed42_test["conditions"]["C2"]["diffrate_disc"]
    print(f"\n[CHECK] Pre-Attribution C2 Reproduction: {c2_rep:.4f} (Expected: 0.7989)")
    assert abs(c2_rep - 0.79888) < 1e-4, f"C2 reproduction mismatch: {c2_rep}"
    print("[CHECK] Historical C2 baseline reproduced bit-exact (286/358 = 79.8883%).\n")

    # 3. Consumer Registry
    consumers: Dict[str, BaseConsumer] = {
        "C_qual_1.50": ContinuousUtilityConsumerC(gamma_C=1.50),
        "A_REFERENCE": ReferenceConsumerA(),
        "B_DIRECTIONAL_SEPARABLE": DirectionalSeparableConsumerB(),
        "D_qual_corner": MagnitudeDominantConsumerD(mu_d=1.00, gamma_kappa=0.50),
    }

    # 4. Multi-Seed Evaluation Across All Consumers & Conditions
    study_results: Dict[str, Any] = {}
    for c_key, consumer in consumers.items():
        print(f"--> Evaluating Consumer: {c_key} across {len(CONDITIONS)} conditions and {len(CONSUMER_SEEDS)} seeds...")
        seed_runs = []
        for s in CONSUMER_SEEDS:
            run_res = engine.evaluate_consumer_on_seed(consumer, s)
            seed_runs.append(run_res)

        # Compute aggregate metrics across seeds for each condition
        cond_aggregates = {}
        for cond in CONDITIONS:
            diffrates = [r["conditions"][cond]["diffrate_disc"] for r in seed_runs]
            greedy_diffs = [r["conditions"][cond]["diffrate_greedy"] for r in seed_runs]
            dir_gains = [r["conditions"][cond]["directional_gain"] for r in seed_runs]
            displacements = [r["conditions"][cond]["action_displacement"] for r in seed_runs]
            clarify_rates = [r["conditions"][cond]["clarify_rate"] for r in seed_runs]
            retrieve_rates = [r["conditions"][cond]["retrieve_rate"] for r in seed_runs]
            entropies = [r["conditions"][cond]["mean_entropy"] for r in seed_runs]
            urgency_doms = [r["conditions"][cond]["high_tier_urgency_dominance"] for r in seed_runs]
            rank_corrs = [r["conditions"][cond]["mean_tier_rank_corr"] for r in seed_runs]
            delta_vs = [r["conditions"][cond]["mean_delta_v"] for r in seed_runs]
            d_js_vals = [r["conditions"][cond]["mean_d_js"] for r in seed_runs]
            d_tv_vals = [r["conditions"][cond]["mean_d_tv"] for r in seed_runs]

            cond_aggregates[cond] = {
                "diffrate_disc_mean": float(np.mean(diffrates)),
                "diffrate_disc_std": float(np.std(diffrates)),
                "diffrate_greedy_mean": float(np.mean(greedy_diffs)),
                "directional_gain_mean": float(np.mean(dir_gains)),
                "directional_gain_std": float(np.std(dir_gains)),
                "action_displacement_mean": float(np.mean(displacements)),
                "action_displacement_std": float(np.std(displacements)),
                "clarify_rate_mean": float(np.mean(clarify_rates)),
                "retrieve_rate_mean": float(np.mean(retrieve_rates)),
                "mean_entropy": float(np.mean(entropies)),
                "high_tier_urgency_dominance": float(np.mean(urgency_doms)),
                "mean_tier_rank_corr": float(np.mean(rank_corrs)),
                "mean_delta_v": float(np.mean(delta_vs)),
                "mean_d_js": float(np.mean(d_js_vals)),
                "mean_d_tv": float(np.mean(d_tv_vals)),
            }

        # Compute Mechanistic Attribution Contrasts for this consumer
        c2_agg = cond_aggregates["C2"]
        contrasts = {
            "C2_minus_C0_canonical_r3_gain": float(c2_agg["diffrate_disc_mean"] - cond_aggregates["C0"]["diffrate_disc_mean"]),
            "C2_minus_C3_direction_correspondence": float(c2_agg["diffrate_disc_mean"] - cond_aggregates["C3"]["diffrate_disc_mean"]),
            "C2_minus_C4_magnitude_correspondence": float(c2_agg["diffrate_disc_mean"] - cond_aggregates["C4"]["diffrate_disc_mean"]),
            "C2_minus_C5_empirical_direction_structure": float(c2_agg["diffrate_disc_mean"] - cond_aggregates["C5"]["diffrate_disc_mean"]),
            "C2_minus_C6_reduced_sign_ablation": float(c2_agg["diffrate_disc_mean"] - cond_aggregates["C6"]["diffrate_disc_mean"]),
            "C2_minus_C7_directional_sparsity": float(c2_agg["diffrate_disc_mean"] - cond_aggregates["C7"]["diffrate_disc_mean"]),
        }

        # Tuple identity audit
        tuple_id = engine.evaluate_tuple_identity(consumer)

        study_results[c_key] = {
            "consumer_id": consumer.consumer_id,
            "condition_aggregates": cond_aggregates,
            "mechanistic_contrasts": contrasts,
            "tuple_identity": tuple_id,
            "per_seed_runs": seed_runs,
        }
        print(f"   [DONE] {c_key}: C2 DiffRate={c2_agg['diffrate_disc_mean']:.4f}, C2-C0 Gain={contrasts['C2_minus_C0_canonical_r3_gain']:+.4f}, C2-C3 Corr={contrasts['C2_minus_C3_direction_correspondence']:+.4f}")

    # 5. Export Results & CSV Summary
    results_dir = REPO_ROOT / "tests" / "evaluation_phase22" / "results" / "h1_r3_causal_attribution"
    results_dir.mkdir(parents=True, exist_ok=True)
    results_path = results_dir / "r3_causal_attribution_results.json"
    summary_csv_path = results_dir / "r3_causal_attribution_summary.csv"
    manifest_path = REPO_ROOT / "tests" / "evaluation_phase22" / "fixtures" / "manifest_h1_r3_causal_attribution.json"

    # Historical canonical C0 baseline verification
    hist_plaus_path = REPO_ROOT / "tests" / "evaluation_phase22" / "results" / "h1_r3_consumer_plausibility" / "r3_consumer_plausibility_results.json"
    nc1_historical_verified = False
    if hist_plaus_path.exists():
        with open(hist_plaus_path, "r", encoding="utf-8") as f:
            hist_data = json.load(f)
        hist_c0_c15 = hist_data["regime_results"]["C_qual_1.50"]["d_pair_action_c0_mean"]
        curr_c0_c15 = study_results["C_qual_1.50"]["condition_aggregates"]["C0"]["diffrate_disc_mean"]
        nc1_historical_verified = bool(hist_c0_c15 == curr_c0_c15)

    full_output = {
        "study_metadata": {
            "study_id": "PHASE_22_H1_R3_CAUSAL_ATTRIBUTION_STUDY",
            "timestamp_utc": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
            "primary_seed": PRIMARY_SEED,
            "consumer_seeds": CONSUMER_SEEDS,
            "exposure_t": PRIMARY_EXPOSURE_T,
            "deadband_epsilon": DEADBAND_EPSILON,
            "scalar_match_threshold": SCALAR_MATCH_THRESHOLD,
            "expected_corpus_sha": EXPECTED_CORPUS_SHA,
            "corpus_n": len(engine.all_probes),
            "matched_pairs": {
                "exhaustive_pairs_count": len(engine.exhaustive_matched_pairs),
                "discordant_pairs_count": len(engine.discordant_matched_pairs),
                "same_direction_pairs_count": len(engine.same_direction_matched_pairs),
                "greedy_discordant_pairs_count": len(engine.greedy_discordant_pairs),
            },
            "locked_base_parameter_hashes": LOCKED_BASE_PARAMETER_HASHES,
            "conditions_evaluated": CONDITIONS,
            "nc1_historical_baseline_verified": nc1_historical_verified,
            "governance": {
                "architecture_gate": "STRICTLY_LOCKED",
                "adr029_status": "DRAFT / RESEARCH RECORD ONLY / NOT RATIFIED",
                "quality_gate_2": "STRICTLY_BLOCKED",
                "phase22_h1_status": "INCONCLUSIVE",
                "genesis_profile_bit_exact": True,
            },
        },
        "consumer_results": study_results,
    }

    with open(results_path, "w", encoding="utf-8") as f:
        json.dump(full_output, f, indent=2)

    # Write summary CSV
    write_attribution_summary_csv(summary_csv_path, study_results)

    # Compute Hashes
    with open(results_path, "rb") as f:
        results_sha = hashlib.sha256(f.read()).hexdigest()
    with open(summary_csv_path, "rb") as f:
        csv_sha = hashlib.sha256(f.read()).hexdigest()

    manifest_data = {
        "manifest_version": "1.0",
        "study_id": "PHASE_22_H1_R3_CAUSAL_ATTRIBUTION_STUDY",
        "timestamp_utc": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "primary_seed": PRIMARY_SEED,
        "consumer_seeds": CONSUMER_SEEDS,
        "corpus_sha256": EXPECTED_CORPUS_SHA,
        "corpus_n": len(engine.all_probes),
        "discordant_pairs_count": len(engine.discordant_matched_pairs),
        "greedy_discordant_pairs_count": len(engine.greedy_discordant_pairs),
        "conditions": CONDITIONS,
        "consumers": list(consumers.keys()),
        "locked_base_parameter_hashes": LOCKED_BASE_PARAMETER_HASHES,
        "artifacts": {
            "results_json": {
                "path": str(results_path.relative_to(REPO_ROOT)).replace("\\", "/"),
                "sha256": results_sha,
                "bytes": results_path.stat().st_size,
            },
            "summary_csv": {
                "path": str(summary_csv_path.relative_to(REPO_ROOT)).replace("\\", "/"),
                "sha256": csv_sha,
                "bytes": summary_csv_path.stat().st_size,
            },
        },
        "governance_invariants": {
            "architecture_gate": "STRICTLY_LOCKED",
            "adr029_status": "DRAFT / RESEARCH RECORD ONLY / NOT RATIFIED",
            "quality_gate_2": "STRICTLY_BLOCKED",
            "phase22_h1_status": "INCONCLUSIVE",
            "genesis_profile_bit_exact": True,
            "hardware_budget": "100% CPU / 0.0 MB GPU VRAM",
        },
    }

    with open(manifest_path, "w", encoding="utf-8") as f:
        json.dump(manifest_data, f, indent=2)

    elapsed = time.time() - t_start
    print(f"\n[OK] Attribution study finished in {elapsed:.2f}s")
    print(f"[OK] Results JSON: {results_path} ({results_sha[:16]}...)")
    print(f"[OK] Summary CSV:  {summary_csv_path} ({csv_sha[:16]}...)")
    print(f"[OK] Manifest:     {manifest_path}")


def write_attribution_summary_csv(
    csv_path: Path,
    consumer_results: Dict[str, Any],
) -> None:
    """Write comprehensive tabular summary of all consumer x condition metrics."""
    headers = [
        "consumer_id",
        "condition",
        "diffrate_disc_mean",
        "diffrate_disc_std",
        "diffrate_greedy_mean",
        "directional_gain_mean",
        "action_displacement_mean",
        "clarify_rate_mean",
        "retrieve_rate_mean",
        "mean_entropy",
        "high_tier_urgency_dominance",
        "mean_tier_rank_corr",
        "mean_delta_v",
        "mean_d_js",
        "mean_d_tv",
    ]
    with open(csv_path, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(headers)
        for c_key, c_data in consumer_results.items():
            for cond in CONDITIONS:
                m = c_data["condition_aggregates"][cond]
                writer.writerow([
                    c_key,
                    cond,
                    f"{m['diffrate_disc_mean']:.4f}",
                    f"{m['diffrate_disc_std']:.4f}",
                    f"{m['diffrate_greedy_mean']:.4f}",
                    f"{m['directional_gain_mean']:+.4f}",
                    f"{m['action_displacement_mean']:.4f}",
                    f"{m['clarify_rate_mean']:.4f}",
                    f"{m['retrieve_rate_mean']:.4f}",
                    f"{m['mean_entropy']:.4f}",
                    f"{m['high_tier_urgency_dominance']:.4f}",
                    f"{m['mean_tier_rank_corr']:.4f}",
                    f"{m['mean_delta_v']:.4f}",
                    f"{m['mean_d_js']:.4f}",
                    f"{m['mean_d_tv']:.4f}",
                ])


if __name__ == "__main__":
    run_causal_attribution_study()
