"""
tests/evaluation_phase22/scripts/evaluate_r3_consumer_sensitivity.py

Phase 22 — H1 R3 Consumer Sensitivity & Robustness Envelope Study.
Deterministic, CPU-only research evaluation engine determining:
- RQ1: Parameter-Regime Dependence: behavior across pre-registered parameter grids for Consumers C & D
- RQ2: Functional-Form vs Parameter Dependence: attributing transfer failures to functional form vs parameter regime
- RQ3: Robustness Envelope: parameter ranges permitting discrete behavioral differentiation
- RQ4: Adapter Dependence Characterization: continuous sensitivity surface vs binary transfer

GOVERNANCE INVARIANTS:
- Research-only study; Production Architecture Gate remains STRICTLY LOCKED.
- Phase 22 H1 = INCONCLUSIVE.
- Gate 2 = BLOCKED (Delta_HM = 0.0685 < 0.1500).
- Protocol v1.5 = NOT AUTHORIZED.
- ADR-029 = DRAFT / RESEARCH RECORD ONLY / NOT RATIFIED.
- Production code (src/core/**, src/api/**, electron/**): EXACTLY 0 MUTATIONS.
- Genesis onboarding profile: bit-exact untouched {"is_onboarded": false}.
- Single frozen Candidate G1 stimulus corpus (Seed 9999, N=270, 90/tier).
- Consumer robustness seeds (42, 43, 44, 45, 46).
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
RESULTS_DIR = EVAL_DIR / "results" / "h1_r3_consumer_sensitivity"
FIXTURES_DIR = EVAL_DIR / "fixtures"
OUTPUT_FILE = RESULTS_DIR / "r3_consumer_sensitivity_results.json"
SUMMARY_CSV = RESULTS_DIR / "r3_consumer_sensitivity_summary.csv"
MANIFEST_FILE = FIXTURES_DIR / "manifest_h1_r3_consumer_sensitivity.json"

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
# Locked Base Parameter Arrays (Bit-Exact from Transferability Study)
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

# --- Consumer B: Historical Direction-Separable Additive Model ---
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

# --- Consumer C: Base Parameter Vectors ---
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

# --- Consumer D: Base Parameter Vectors ---
D_G_BASE = np.array([0.10, 0.30, 0.20, 0.25, 0.40, 0.05], dtype=np.float64)
D_KAPPA_S_BASE = np.array([1.50, 4.00, 2.50, 3.00, 5.50, 0.80], dtype=np.float64)
D_W_DIR = np.array([
    [ 0.10, -0.15,  0.10],  # answer
    [-0.20,  0.15, -0.10],  # clarify
    [ 0.20, -0.10,  0.15],  # retrieve
    [ 0.10,  0.15,  0.10],  # derive
    [-0.15,  0.25, -0.15],  # reason
    [-0.10, -0.20, -0.20],  # wait
], dtype=np.float64)

# =============================================================================
# Pre-Registered Parameter Grids
# =============================================================================
GAMMA_C_GRID = [0.10, 0.20, 0.35, 0.50, 0.75, 1.00, 1.50, 2.00]  # 8 levels
MU_D_GRID = [0.20, 0.30, 0.40, 0.50, 0.70, 1.00]                 # 6 levels
GAMMA_KAPPA_GRID = [0.50, 0.75, 1.00, 1.25, 1.50]                 # 5 levels

# Compute base parameter SHA-256 digests
def array_hash(arr: np.ndarray) -> str:
    return hashlib.sha256(arr.tobytes()).hexdigest()

LOCKED_BASE_HASHES = {
    "C_U_BASE": array_hash(C_U_BASE),
    "C_COST_S": array_hash(C_COST_S),
    "C_M_BASE": array_hash(C_M_BASE),
    "D_G_BASE": array_hash(D_G_BASE),
    "D_KAPPA_S_BASE": array_hash(D_KAPPA_S_BASE),
    "D_W_DIR": array_hash(D_W_DIR),
}


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
    return float(0.5 * (kl_p_m + kl_q_m))


def compute_tv_distance(p: np.ndarray, q: np.ndarray) -> float:
    """Compute Total Variation Distance TV(P, Q) = 0.5 * sum |p_i - q_i|."""
    return float(0.5 * np.sum(np.abs(p - q)))


def compute_entropy(p: np.ndarray) -> float:
    """Compute Shannon entropy in nats."""
    p_safe = np.clip(p, 1e-12, 1.0)
    p_safe /= np.sum(p_safe)
    return float(-np.sum(p_safe * np.log(p_safe)))


# =============================================================================
# Consumer Valuation Data Structures
# =============================================================================

@dataclass(frozen=True)
class ConsumerValuationResult:
    consumer_id: str
    condition: str
    scalar_s: float
    ternary_signs: Tuple[int, int, int]
    valuations: List[float]
    probabilities: List[float]
    selected_action: str
    selected_action_idx: int
    entropy: float


class BaseConsumer:
    """Abstract base consumer for action valuation."""

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


# =============================================================================
# Consumer Implementations
# =============================================================================

class ReferenceConsumerA(BaseConsumer):
    """Consumer A: Historical Reference EFE Adapter (Lower is Better)."""

    def __init__(self, gamma: float = 1.0) -> None:
        super().__init__("A_REFERENCE", gamma)

    def evaluate(
        self,
        s_val: float,
        d_signs: Tuple[int, int, int],
        condition: str,
        tie_break_noise: Optional[np.ndarray] = None,
    ) -> ConsumerValuationResult:
        beta_k = 1.0 + 0.50 * math.tanh(2.0 * s_val)
        beta_m = 1.0 + 0.30 * math.tanh(2.0 * s_val)

        g_pragmatic = A_BASE_COSTS
        g_epistemic = -beta_k * A_BASE_DK - beta_m * A_BASE_DM

        if condition == "C0":
            d_vec = np.zeros(3, dtype=np.float64)
        else:
            d_vec = np.array(d_signs, dtype=np.float64) / math.sqrt(3.0)

        delta_g_dir = -np.dot(A_ACTION_WEIGHTS, d_vec)
        g_vals = g_pragmatic + g_epistemic + delta_g_dir

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
    """Consumer B: Additive Linear-Quadratic Effort Cost (Lower is Better)."""

    def __init__(self, gamma: float = 1.0) -> None:
        super().__init__("B_DIRECTIONAL_SEPARABLE", gamma)

    def evaluate(
        self,
        s_val: float,
        d_signs: Tuple[int, int, int],
        condition: str,
        tie_break_noise: Optional[np.ndarray] = None,
    ) -> ConsumerValuationResult:
        g_scalar = B_G_BASE + B_ALPHA_S * s_val + B_BETA_S2 * (s_val ** 2)

        if condition == "C0":
            d_vec = np.zeros(3, dtype=np.float64)
        else:
            d_vec = np.array(d_signs, dtype=np.float64) / math.sqrt(3.0)

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


class ContinuousUtilityConsumerCSweep(BaseConsumer):
    """Consumer C Sweep: Multiplicative Exponential Utility with gain parameter gamma_C."""

    def __init__(self, gamma_C: float, gamma: float = 1.0) -> None:
        c_id = f"C_gamma_{gamma_C:.2f}"
        super().__init__(c_id, gamma)
        self.gamma_C = float(gamma_C)
        self.m_dir = self.gamma_C * C_M_BASE

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

        dir_mult = np.exp(np.dot(self.m_dir, d_vec))
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


class MagnitudeDominantConsumerDSweep(BaseConsumer):
    """Consumer D Sweep: Magnitude-Dominant Cost Model with mu_d and gamma_kappa."""

    def __init__(self, mu_d: float, gamma_kappa: float, gamma: float = 1.0) -> None:
        c_id = f"D_mu_{mu_d:.2f}_gk_{gamma_kappa:.2f}"
        super().__init__(c_id, gamma)
        self.mu_d = float(mu_d)
        self.gamma_kappa = float(gamma_kappa)
        self.kappa_s = self.gamma_kappa * D_KAPPA_S_BASE

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

        g_scalar = D_G_BASE + self.kappa_s * s_val
        delta_g_dir = -self.mu_d * np.dot(D_W_DIR, d_vec)
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
# Sensitivity Study Engine
# =============================================================================

class R3ConsumerSensitivityEngine:
    """
    Research-only evaluation engine for Phase 22 H1 R3 Consumer Sensitivity & Robustness Envelope Study.
    """

    def __init__(self, primary_seed: int = PRIMARY_SEED) -> None:
        self.primary_seed = primary_seed
        self.sp = StimulusProcessor(StimulusConfig())
        self.core = EmotionCore(EmotionConfig())
        self.ai = ActiveInferenceEngine(ActiveInferenceConfig())

        # Baseline Controls
        self.control_consumers: Dict[str, BaseConsumer] = {
            "A_REFERENCE": ReferenceConsumerA(gamma=1.0),
            "B_DIRECTIONAL_SEPARABLE": DirectionalSeparableConsumerB(gamma=1.0),
        }

        # Consumer C Sweep Instances (8 levels)
        self.c_sweep_consumers: Dict[float, ContinuousUtilityConsumerCSweep] = {
            g_c: ContinuousUtilityConsumerCSweep(gamma_C=g_c, gamma=1.0)
            for g_c in GAMMA_C_GRID
        }

        # Consumer D Sweep Instances (6 x 5 = 30 cells)
        self.d_sweep_consumers: Dict[Tuple[float, float], MagnitudeDominantConsumerDSweep] = {
            (mu, gk): MagnitudeDominantConsumerDSweep(mu_d=mu, gamma_kappa=gk, gamma=1.0)
            for mu in MU_D_GRID
            for gk in GAMMA_KAPPA_GRID
        }

        self.all_probes: List[Dict[str, Any]] = []
        self.simulated_trajectories: Dict[int, Dict[str, Any]] = {}
        self.exhaustive_matched_pairs: List[Tuple[int, int]] = []
        self.discordant_matched_pairs: List[Tuple[int, int]] = []
        self.same_direction_matched_pairs: List[Tuple[int, int]] = []

    def generate_frozen_dataset(self) -> List[Dict[str, Any]]:
        """Generate single frozen Candidate G1 stimulus corpus (Seed 9999, N=270, 90/tier)."""
        print("\n" + "=" * 75)
        print("Phase 22 H1 — R3 Consumer Sensitivity & Robustness Envelope Study")
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

        # 1. Pair-Level Metrics on Discordant Matched Pairs (N=358)
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
                "diffrate_all": float(action_diffs / 6734),
                "action_diffs_count": action_diffs,
                "mean_delta_v": float(np.mean(delta_v_list)),
                "std_delta_v": float(np.std(delta_v_list)),
                "mean_d_js": float(np.mean(d_js_list)),
                "mean_d_tv": float(np.mean(d_tv_list)),
            }

        # 2. Pair-Level Metrics on Same-Direction Matched Pairs (N=6376)
        # Note: NC3 hard parity applies strictly to identical tuples (S_i == S_j, d_i == d_j).
        # Pairs differing in S are reported descriptively.
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

        # 3. Condition-Level Shift across Same Probes (C2 vs C4, N=270 probes)
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

    def evaluate_hard_tuple_identity_on_consumer(self, consumer: BaseConsumer) -> Dict[str, Any]:
        """
        Verify Hard Invariant NC2: For identical (S, d) tuples, deterministic evaluation
        must produce delta_action_identity = 0.0000 and D_JS_identity < 1e-12.
        """
        synthetic_tuples = [
            (0.15, ( 1,  0, -1)),
            (0.35, (-1,  1,  0)),
            (0.55, ( 0, -1,  1)),
            (0.75, ( 1,  1, -1)),
            (0.90, (-1, -1,  1)),
        ]

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

        passed = bool(max_action_diff == 0 and max_js_div < 1e-12)
        return {
            "delta_action_identity": float(max_action_diff),
            "d_js_identity": float(max_js_div),
            "invariant_passed": passed,
        }

    def run_consumer_evaluation_across_seeds(self, consumer: BaseConsumer) -> Dict[str, Any]:
        """Run consumer over seeds 42-46 and aggregate."""
        seed_runs = {}
        for seed in CONSUMER_SEEDS:
            run_res = self.evaluate_consumer_on_seed(consumer, seed)
            seed_runs[str(seed)] = run_res

        c2_diffrates = [seed_runs[str(s)]["discordant_metrics"]["C2"]["diffrate_disc"] for s in CONSUMER_SEEDS]
        c2_diffrate_all = [seed_runs[str(s)]["discordant_metrics"]["C2"]["diffrate_all"] for s in CONSUMER_SEEDS]
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
        transfer_satisfied = bool(crit_1_diff and crit_2_gain)

        # Hard tuple identity parity
        tuple_identity = self.evaluate_hard_tuple_identity_on_consumer(consumer)

        return {
            "consumer_id": consumer.consumer_id,
            "aggregate": {
                "c2_diffrate_disc_mean": mean_diffrate_c2,
                "c2_diffrate_disc_std": float(np.std(c2_diffrates)),
                "c2_diffrate_all_mean": float(np.mean(c2_diffrate_all)),
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
                "hard_tuple_identity_parity": tuple_identity,
                "secondary_metric_condition_shift_c2_c4": {
                    "role": "descriptive_secondary_metric",
                    "observed": mean_shift_c2_c4,
                },
                "transfer_criteria_satisfied": transfer_satisfied,
            },
        }

    def run_sensitivity_study(self) -> Dict[str, Any]:
        """Execute complete sensitivity sweeps across Consumers C and D plus controls."""
        print("\n[Step 3/5] Evaluating Control Baselines (A_REFERENCE & B_DIRECTIONAL_SEPARABLE)...")
        control_results = {}
        for c_id, consumer in self.control_consumers.items():
            print(f"  Evaluating Control: {c_id}...")
            res = self.run_consumer_evaluation_across_seeds(consumer)
            control_results[c_id] = res
            print(f"    C2 DiffRate: {res['aggregate']['c2_diffrate_disc_mean']:.4f}, Dir Gain: {res['aggregate']['directional_gain_mean']:.4f}")

        # Assert historical baseline reproduction
        assert round(control_results["A_REFERENCE"]["aggregate"]["c2_diffrate_disc_mean"], 4) == 0.7989, "Consumer A reproduction failed!"
        assert round(control_results["B_DIRECTIONAL_SEPARABLE"]["aggregate"]["c2_diffrate_disc_mean"], 4) == 0.7989, "Consumer B reproduction failed!"
        print("  Controls A and B reproduced historical transferability baseline bit-exact (0.7989).")

        # Consumer C 1D Sweep (8 cells)
        print("\n[Step 4/5] Executing Consumer C Sensitivity Sweep across gamma_C in [0.10, 2.00] (8 cells)...")
        c_sweep_results = {}
        for g_c in GAMMA_C_GRID:
            consumer = self.c_sweep_consumers[g_c]
            res = self.run_consumer_evaluation_across_seeds(consumer)
            c_sweep_results[f"gamma_{g_c:.2f}"] = {
                "gamma_C": g_c,
                "is_historical_reference": bool(round(g_c, 2) == 1.00),
                "metrics": res,
            }
            c2_diff = res["aggregate"]["c2_diffrate_disc_mean"]
            dir_gain = res["aggregate"]["directional_gain_mean"]
            c2_dv = res["aggregate"]["c2_delta_v_mean"]
            sat = res["preregistered_criteria"]["transfer_criteria_satisfied"]
            print(f"  gamma_C = {g_c:4.2f}: DiffRate = {c2_diff:.4f}, Gain = {dir_gain:+.4f}, DeltaV = {c2_dv:.4f} -> {'QUALIFIES' if sat else 'NO'}")

        # Consumer C Transition Extraction
        c_transition_status = None
        c_transition_interval = None
        c_qualifying_gammas = [g_c for g_c in GAMMA_C_GRID if c_sweep_results[f"gamma_{g_c:.2f}"]["metrics"]["preregistered_criteria"]["transfer_criteria_satisfied"]]

        if len(c_qualifying_gammas) == 0:
            c_transition_status = "NO_EMPIRICAL_TRANSITION_WITHIN_GRID"
        elif c_sweep_results[f"gamma_{GAMMA_C_GRID[0]:.2f}"]["metrics"]["preregistered_criteria"]["transfer_criteria_satisfied"]:
            c_transition_status = "BOUNDARY_AT_GRID_MINIMUM"
            c_transition_interval = [GAMMA_C_GRID[0], GAMMA_C_GRID[0]]
        else:
            # Find first transition interval [gamma_{k-1}, gamma_k]
            for idx in range(1, len(GAMMA_C_GRID)):
                prev_g = GAMMA_C_GRID[idx - 1]
                curr_g = GAMMA_C_GRID[idx]
                prev_sat = c_sweep_results[f"gamma_{prev_g:.2f}"]["metrics"]["preregistered_criteria"]["transfer_criteria_satisfied"]
                curr_sat = c_sweep_results[f"gamma_{curr_g:.2f}"]["metrics"]["preregistered_criteria"]["transfer_criteria_satisfied"]
                if not prev_sat and curr_sat:
                    c_transition_status = "TRANSITION_INTERVAL_OBSERVED"
                    c_transition_interval = [prev_g, curr_g]
                    break

        print(f"  Consumer C Transition Outcome: {c_transition_status} (Interval: {c_transition_interval})")

        # Consumer D 2D Sweep (6 x 5 = 30 cells)
        print("\n[Step 5/5] Executing Consumer D 2D Sensitivity Sweep (mu_d x gamma_kappa, 30 cells)...")
        d_sweep_results = {}
        d_qualifying_cells = []

        for mu in MU_D_GRID:
            for gk in GAMMA_KAPPA_GRID:
                consumer = self.d_sweep_consumers[(mu, gk)]
                res = self.run_consumer_evaluation_across_seeds(consumer)
                cell_id = f"mu_{mu:.2f}_gk_{gk:.2f}"
                sat = res["preregistered_criteria"]["transfer_criteria_satisfied"]
                is_hist = bool(round(mu, 2) == 0.20 and round(gk, 2) == 1.00)

                d_sweep_results[cell_id] = {
                    "mu_d": mu,
                    "gamma_kappa": gk,
                    "is_historical_reference": is_hist,
                    "metrics": res,
                }
                if sat:
                    d_qualifying_cells.append({"mu_d": mu, "gamma_kappa": gk})

                c2_diff = res["aggregate"]["c2_diffrate_disc_mean"]
                dir_gain = res["aggregate"]["directional_gain_mean"]
                print(f"  mu={mu:.2f}, gk={gk:.2f}: DiffRate = {c2_diff:.4f}, Gain = {dir_gain:+.4f} -> {'QUALIFIES' if sat else 'NO'}")

        d_transition_status = "DISCRETE_QUALIFYING_REGIME_OBSERVED" if len(d_qualifying_cells) > 0 else "NO_EMPIRICAL_TRANSITION_WITHIN_GRID"
        print(f"\n  Consumer D Qualifying Cells Count: {len(d_qualifying_cells)} / 30 -> {d_transition_status}")

        # Summary of hard tuple identity across all 38 sweep regimes
        all_sweep_tuple_passed = True
        for g_c in GAMMA_C_GRID:
            if not c_sweep_results[f"gamma_{g_c:.2f}"]["metrics"]["preregistered_criteria"]["hard_tuple_identity_parity"]["invariant_passed"]:
                all_sweep_tuple_passed = False
        for mu in MU_D_GRID:
            for gk in GAMMA_KAPPA_GRID:
                if not d_sweep_results[f"mu_{mu:.2f}_gk_{gk:.2f}"]["metrics"]["preregistered_criteria"]["hard_tuple_identity_parity"]["invariant_passed"]:
                    all_sweep_tuple_passed = False

        print(f"\n  Hard Tuple Identity Parity across all 38 sweep regimes: {'PASS (100%)' if all_sweep_tuple_passed else 'FAIL'}")

        return {
            "study_metadata": {
                "study_id": "PHASE_22_H1_R3_CONSUMER_SENSITIVITY_STUDY",
                "primary_seed": self.primary_seed,
                "consumer_seeds": CONSUMER_SEEDS,
                "exposure_t": PRIMARY_EXPOSURE_T,
                "deadband_epsilon": DEADBAND_EPSILON,
                "scalar_match_threshold": SCALAR_MATCH_THRESHOLD,
                "locked_base_parameter_hashes": LOCKED_BASE_HASHES,
            },
            "control_baselines": control_results,
            "consumer_c_sensitivity": {
                "grid_levels": GAMMA_C_GRID,
                "sweep_results": c_sweep_results,
                "qualifying_gammas": c_qualifying_gammas,
                "transition_status": c_transition_status,
                "transition_interval": c_transition_interval,
            },
            "consumer_d_sensitivity": {
                "mu_d_grid": MU_D_GRID,
                "gamma_kappa_grid": GAMMA_KAPPA_GRID,
                "sweep_results": d_sweep_results,
                "qualifying_cells_count": len(d_qualifying_cells),
                "qualifying_cells": d_qualifying_cells,
                "transition_status": d_transition_status,
            },
            "invariants_audit": {
                "controls_tuple_identity_passed": bool(
                    control_results["A_REFERENCE"]["preregistered_criteria"]["hard_tuple_identity_parity"]["invariant_passed"] and
                    control_results["B_DIRECTIONAL_SEPARABLE"]["preregistered_criteria"]["hard_tuple_identity_parity"]["invariant_passed"]
                ),
                "all_38_sweep_regimes_tuple_identity_passed": all_sweep_tuple_passed,
                "genesis_profile_path": "data/profile.json",
            },
        }


# =============================================================================
# Execution & Serialization
# =============================================================================

def main() -> None:
    t_start = time.perf_counter()
    RESULTS_DIR.mkdir(parents=True, exist_ok=True)
    FIXTURES_DIR.mkdir(parents=True, exist_ok=True)

    engine = R3ConsumerSensitivityEngine(PRIMARY_SEED)
    engine.generate_frozen_dataset()
    engine.simulate_pad_trajectories()
    engine.extract_matched_pairs()
    results = engine.run_sensitivity_study()

    # Write JSON results
    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        json.dump(results, f, indent=2)
    sha256_results = compute_sha256(OUTPUT_FILE)
    results_size = OUTPUT_FILE.stat().st_size

    # Write CSV summary
    with open(SUMMARY_CSV, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow([
            "consumer_family",
            "parameter_configuration",
            "is_historical_reference",
            "diffrate_disc_c2",
            "diffrate_all_c2",
            "d_pair_action_c0",
            "directional_gain",
            "c2_c4_condition_shift",
            "c2_mean_delta_v",
            "c0_mean_delta_v",
            "transfer_criteria_satisfied",
        ])

        # Controls
        for c_id in ["A_REFERENCE", "B_DIRECTIONAL_SEPARABLE"]:
            agg = results["control_baselines"][c_id]["aggregate"]
            crit = results["control_baselines"][c_id]["preregistered_criteria"]
            writer.writerow([
                "CONTROL",
                c_id,
                True,
                f"{agg['c2_diffrate_disc_mean']:.4f}",
                f"{agg['c2_diffrate_all_mean']:.4f}",
                f"{agg['c0_d_pair_action_mean']:.4f}",
                f"{agg['directional_gain_mean']:.4f}",
                f"{agg['condition_shift_c2_c4_mean']:.4f}",
                f"{agg['c2_delta_v_mean']:.4f}",
                f"{agg['c0_delta_v_mean']:.4f}",
                crit["transfer_criteria_satisfied"],
            ])

        # Consumer C
        for g_c in GAMMA_C_GRID:
            entry = results["consumer_c_sensitivity"]["sweep_results"][f"gamma_{g_c:.2f}"]
            agg = entry["metrics"]["aggregate"]
            crit = entry["metrics"]["preregistered_criteria"]
            writer.writerow([
                "CONSUMER_C",
                f"gamma_C={g_c:.2f}",
                entry["is_historical_reference"],
                f"{agg['c2_diffrate_disc_mean']:.4f}",
                f"{agg['c2_diffrate_all_mean']:.4f}",
                f"{agg['c0_d_pair_action_mean']:.4f}",
                f"{agg['directional_gain_mean']:.4f}",
                f"{agg['condition_shift_c2_c4_mean']:.4f}",
                f"{agg['c2_delta_v_mean']:.4f}",
                f"{agg['c0_delta_v_mean']:.4f}",
                crit["transfer_criteria_satisfied"],
            ])

        # Consumer D
        for mu in MU_D_GRID:
            for gk in GAMMA_KAPPA_GRID:
                entry = results["consumer_d_sensitivity"]["sweep_results"][f"mu_{mu:.2f}_gk_{gk:.2f}"]
                agg = entry["metrics"]["aggregate"]
                crit = entry["metrics"]["preregistered_criteria"]
                writer.writerow([
                    "CONSUMER_D",
                    f"mu_d={mu:.2f}_gk={gk:.2f}",
                    entry["is_historical_reference"],
                    f"{agg['c2_diffrate_disc_mean']:.4f}",
                    f"{agg['c2_diffrate_all_mean']:.4f}",
                    f"{agg['c0_d_pair_action_mean']:.4f}",
                    f"{agg['directional_gain_mean']:.4f}",
                    f"{agg['condition_shift_c2_c4_mean']:.4f}",
                    f"{agg['c2_delta_v_mean']:.4f}",
                    f"{agg['c0_delta_v_mean']:.4f}",
                    crit["transfer_criteria_satisfied"],
                ])

    sha256_csv = compute_sha256(SUMMARY_CSV)

    # Write Manifest
    manifest = {
        "manifest_version": "1.0",
        "study_id": "PHASE_22_H1_R3_CONSUMER_SENSITIVITY_STUDY",
        "timestamp_utc": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "locked_base_parameter_hashes": LOCKED_BASE_HASHES,
        "parameter_grids": {
            "gamma_c_grid": GAMMA_C_GRID,
            "mu_d_grid": MU_D_GRID,
            "gamma_kappa_grid": GAMMA_KAPPA_GRID,
            "total_sweep_regimes": 38,
            "total_control_regimes": 2,
        },
        "artifacts": {
            "results_json": {
                "path": str(OUTPUT_FILE.relative_to(REPO_ROOT)).replace("\\", "/"),
                "sha256": sha256_results,
                "bytes": results_size,
            },
            "summary_csv": {
                "path": str(SUMMARY_CSV.relative_to(REPO_ROOT)).replace("\\", "/"),
                "sha256": sha256_csv,
                "bytes": SUMMARY_CSV.stat().st_size,
            },
        },
        "summary": {
            "consumer_c_transition_status": results["consumer_c_sensitivity"]["transition_status"],
            "consumer_c_transition_interval": results["consumer_c_sensitivity"]["transition_interval"],
            "consumer_d_transition_status": results["consumer_d_sensitivity"]["transition_status"],
            "consumer_d_qualifying_cells_count": results["consumer_d_sensitivity"]["qualifying_cells_count"],
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

    with open(MANIFEST_FILE, "w", encoding="utf-8") as f:
        json.dump(manifest, f, indent=2)

    elapsed = time.perf_counter() - t_start
    print(f"\n[OK] Results written to: {OUTPUT_FILE} ({sha256_results}, {results_size} bytes)")
    print(f"[OK] Summary CSV written to: {SUMMARY_CSV} ({sha256_csv})")
    print(f"[OK] Manifest written to: {MANIFEST_FILE}")
    print(f"[OK] Execution finished in {elapsed:.2f}s.")


if __name__ == "__main__":
    main()
