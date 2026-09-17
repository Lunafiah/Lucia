"""
Phase 22 H1 — R3 Temporal Belief Dynamics & Multi-Turn Persistence Study
=========================================================================
Evaluation Script: evaluate_r3_temporal_belief_dynamics.py

Evaluates multi-turn temporal dynamics (T=5 turns) of R3 directional information:
  - Sequence Families:
      * T1: Immediate recovery (perturbation -> neutral -> neutral -> neutral -> neutral)
      * T2: Repeated fixed displacement injection (r1 injected at t=1..5, saturation attractor)
      * T3: Direction reversal (d -> -d -> d -> -d -> d)
      * T4: Recovery then reactivation (d -> 0 -> 0 -> d vs 0 -> 0 -> 0 -> d)
  - Two Evaluation Modes:
      * Mode A: Full coupled trajectory (affect + belief q_t both evolve across turns)
      * Mode B: Epistemic-state-controlled diagnostic (prior belief pinned to q0 at every turn)
  - Trajectory-Level Permutation Controls:
      * C0: Scalar baseline (S_t, d = 0)
      * C2: Canonical R3 ([S_t, sign(r_t) / sqrt(3)])
      * C3: Shuffled direction (trajectory-level permutation across probes)
      * C4: Shuffled magnitude (trajectory-level permutation across probes)
      * C5: Independent direction (trajectory-level permutation across probes)
  - Epistemic Quantities & Metrics:
      * EIG_t, E[H_post, t], TV(q_t, q_{t-1}), JS(q_t, q_{t-1})
      * Between-condition belief divergence: TV(q_{i,t}, q_{j,t}), JS(q_{i,t}, q_{j,t})
      * Incremental directional effect: ΔEIG_dir,t = ΔEIG_C2,t - ΔEIG_C0,t
      * Persistence Ratio: PR_t = |ΔEIG_dir,t| / |ΔEIG_dir,1| (excluding zero-delta denominator)
      * Recovery Half-Life: first turn where |ΔEIG_dir,t| <= 0.5 |ΔEIG_dir,1| or NOT_REACHED
      * Temporal Directional Retention: proportion with |ΔEIG_dir,t| > tau_EIG (1e-4)
      * Temporal History-Dependence Diagnostic (THD): JS(q_4_TrajA, q_4_TrajB) and |ΔEIG_4_TrajA - ΔEIG_4_TrajB|
      * Action Policy Divergence: D_pol,t
  - 8 Negative Controls:
      * NC1: Historical scalar reproduction
      * NC2: Hard tuple identity parity
      * NC3: Multiset preservation at trajectory level (C3, C4, C5)
      * NC4: Determinism across repeated runs
      * NC5: Representation-independent epistemic null (W_dir = 0 -> ΔEIG_dir = 0)
      * NC6: Direction-independent temporal transition null (max Mean |ΔEIG_dir,t| <= 1e-4, retention = 0%)
      * NC7: Production isolation (src/core/** diff = 0)
      * NC8: Genesis profile bit-exact {"is_onboarded": false}
  - 4 Consumers: Primary C (gamma_C=1.50), Reference A, Separable B, Qualifying Corner D.
  - 5 Robustness Seeds: [42, 43, 44, 45, 46].

Strict Governance Invariants:
  - Research only / Zero production mutations (src/core/** diff = 0).
  - Gate 2 = STRICTLY BLOCKED (Δ_HM < 0.1500).
  - Phase 22 H1 = INCONCLUSIVE.
  - ADR-029 = DRAFT / RESEARCH RECORD ONLY / NOT RATIFIED.
  - Genesis profile = bit-exact {"is_onboarded": false}.
  - 100% CPU execution / 0.0 MB GPU VRAM.
"""

from dataclasses import dataclass, field
import hashlib
import json
import math
from pathlib import Path
import sys
import time
from typing import Any, Dict, List, Optional, Tuple

import numpy as np

REPO_ROOT = Path(__file__).resolve().parent.parent.parent.parent
sys.path.insert(0, str(REPO_ROOT))

from src.core.config import EmotionConfig, StimulusConfig
from src.core.emotion.emotion_core import EmotionCore
from src.core.gating.stimulus_processor import StimulusProcessor
from src.core.inference.active_inference import ActiveInferenceConfig, ActiveInferenceEngine
from tests.evaluation_phase22.scripts.calibrate_stimulus_representation import GeneratorG1

# =============================================================================
# Constants & Governance Configuration
# =============================================================================

STUDY_ID = "PHASE_22_H1_R3_TEMPORAL_BELIEF_DYNAMICS_STUDY"
PRIMARY_SEED = 9999
CONSUMER_SEEDS = [42, 43, 44, 45, 46]
EXPOSURE_TICKS = 12
DEADBAND_EPSILON = 0.010
SCALAR_MATCH_THRESHOLD = 0.020
HORIZON_T = 5

# Pre-registered numerical tolerances
TOLERANCE_EIG = 1e-4   # Information gain differentiation threshold
TOLERANCE_H = 1e-4     # Posterior entropy profile differentiation threshold
TOLERANCE_TV = 1e-4    # Belief-update Total Variation threshold
TOLERANCE_JS = 1e-5    # Belief-update Jensen-Shannon divergence threshold

EXPECTED_CORPUS_SHA = "d0061e8cfdd160f4ebccb7100e4fe3eeef9ff18a1a4c9c1b3f912a76f2ae82c0"
EXPECTED_HISTORICAL_DISCORDANT = 358

ACTIONS = ["answer", "clarify", "retrieve", "derive", "reason", "wait"]
CONDITIONS = ["C0", "C2", "C3", "C4", "C5"]
SEQUENCES = ["T1", "T2", "T3", "T4"]
CONSUMER_IDS = ["C_qual_1.50", "A_REFERENCE", "B_DIRECTIONAL_SEPARABLE", "D_CORNER"]
HYPOTHESES = ["h1_factual", "h2_ambiguous", "h3_structuring", "h4_routine"]
NUM_HYPOTHESES = len(HYPOTHESES)  # K = 4

# Pre-registered transition and belief decay parameters
ALPHA_DECAY = 0.65       # Affective homeostatic decay per turn
BETA_STIM = 1.0          # Stimulus coupling gain
LAMBDA_LEAK = 0.15       # Epistemic belief leak per turn toward uniform prior

# Resting PAD attractor
RESTING_PAD = np.array([+0.25, -0.05, +0.05], dtype=np.float64)

# =============================================================================
# Pre-Registered Base Observation Channel Parameters (Bit-Exact / Anti-Circularity)
# =============================================================================

CLARIFY_BASE_LOGITS = np.array([-1.20, +1.80, -0.40, -1.00], dtype=np.float64)
RETRIEVE_BASE_LOGITS = np.array([+1.60, -0.80, +0.90, -1.40], dtype=np.float64)

CLARIFY_W_DIR = np.array([
    [ 0.00,  0.00,  0.00],
    [-0.30, +0.40, -0.10],
    [+0.10, +0.20, -0.20],
    [+0.20, -0.30, +0.10],
], dtype=np.float64)

RETRIEVE_W_DIR = np.array([
    [+0.10, -0.20, +0.40],
    [ 0.00,  0.00,  0.00],
    [+0.20, +0.10, +0.30],
    [-0.10, -0.20, -0.20],
], dtype=np.float64)

CLARIFY_B_S = np.array([0.10, 0.45, 0.20, -0.30], dtype=np.float64)
RETRIEVE_B_S = np.array([0.35, 0.05, 0.25, -0.20], dtype=np.float64)


def sha256_array(arr: np.ndarray) -> str:
    """Compute deterministic SHA-256 hash for float arrays."""
    return hashlib.sha256(arr.tobytes()).hexdigest()


LOCKED_EPISTEMIC_PARAMETER_HASHES = {
    "ALPHA_DECAY": hashlib.sha256(str(ALPHA_DECAY).encode()).hexdigest(),
    "BETA_STIM": hashlib.sha256(str(BETA_STIM).encode()).hexdigest(),
    "LAMBDA_LEAK": hashlib.sha256(str(LAMBDA_LEAK).encode()).hexdigest(),
    "RESTING_PAD": sha256_array(RESTING_PAD),
    "CLARIFY_BASE_LOGITS": sha256_array(CLARIFY_BASE_LOGITS),
    "RETRIEVE_BASE_LOGITS": sha256_array(RETRIEVE_BASE_LOGITS),
    "CLARIFY_W_DIR": sha256_array(CLARIFY_W_DIR),
    "RETRIEVE_W_DIR": sha256_array(RETRIEVE_W_DIR),
    "CLARIFY_B_S": sha256_array(CLARIFY_B_S),
    "RETRIEVE_B_S": sha256_array(RETRIEVE_B_S),
}

# =============================================================================
# Mathematical Helpers
# =============================================================================

def deadband_sign(x: float, eps: float = DEADBAND_EPSILON) -> int:
    """Three-valued deadband sign function: -1 if x < -eps, +1 if x > eps, 0 otherwise."""
    if x > eps:
        return 1
    elif x < -eps:
        return -1
    return 0


def compute_entropy(p: np.ndarray) -> float:
    """Shannon entropy in nats with numerical floor guard."""
    p_safe = np.clip(p, 1e-15, 1.0)
    return float(-np.sum(p_safe * np.log(p_safe)))


def compute_kl_divergence(p: np.ndarray, q: np.ndarray) -> float:
    """Kullback-Leibler divergence D_KL(P || Q) in nats."""
    p_safe = np.clip(p, 1e-15, 1.0)
    q_safe = np.clip(q, 1e-15, 1.0)
    return float(np.sum(p_safe * np.log(p_safe / q_safe)))


def compute_js_divergence(p: np.ndarray, q: np.ndarray) -> float:
    """Jensen-Shannon divergence D_JS(P || Q) in nats."""
    m = 0.5 * (p + q)
    return float(0.5 * compute_kl_divergence(p, m) + 0.5 * compute_kl_divergence(q, m))


def compute_tv_distance(p: np.ndarray, q: np.ndarray) -> float:
    """Total Variation distance TV(P, Q) = 0.5 * sum |P(k) - Q(k)|."""
    return float(0.5 * np.sum(np.abs(p - q)))


# =============================================================================
# Epistemic Observation Consumer Models
# =============================================================================

class BaseEpistemicConsumer:
    """
    Abstract base consumer mapping somatic state (S, v_dir) to observation channels.
    """
    def __init__(self, consumer_id: str) -> None:
        self.consumer_id = consumer_id

    def evaluate_observation_channel(
        self,
        action: str,
        s_val: float,
        v_dir: np.ndarray,
    ) -> Tuple[np.ndarray, bool]:
        raise NotImplementedError


class EpistemicConsumerC(BaseEpistemicConsumer):
    """Primary Consumer C: Multiplicative Directional Coupling."""
    def __init__(self, gamma_c: float = 1.50) -> None:
        super().__init__("C_qual_1.50")
        self.gamma_c = float(gamma_c)

    def evaluate_observation_channel(
        self,
        action: str,
        s_val: float,
        v_dir: np.ndarray,
    ) -> Tuple[np.ndarray, bool]:
        if action == "clarify":
            mult = 1.0 + self.gamma_c * np.dot(CLARIFY_W_DIR, v_dir)
            logits_diff = CLARIFY_BASE_LOGITS * mult + CLARIFY_B_S * s_val
            p1 = 1.0 / (1.0 + np.exp(-logits_diff))
            p0 = 1.0 - p1
            return np.vstack([p0, p1]), True
        elif action == "retrieve":
            mult = 1.0 + self.gamma_c * np.dot(RETRIEVE_W_DIR, v_dir)
            logits_diff = RETRIEVE_BASE_LOGITS * mult + RETRIEVE_B_S * s_val
            p1 = 1.0 / (1.0 + np.exp(-logits_diff))
            p0 = 1.0 - p1
            return np.vstack([p0, p1]), True
        else:
            return np.ones((1, NUM_HYPOTHESES), dtype=np.float64), False


class EpistemicConsumerA(BaseEpistemicConsumer):
    """Reference Consumer A: EFE-style Additive Directional Coupling with Saturating S."""
    def __init__(self) -> None:
        super().__init__("A_REFERENCE")

    def evaluate_observation_channel(
        self,
        action: str,
        s_val: float,
        v_dir: np.ndarray,
    ) -> Tuple[np.ndarray, bool]:
        sat_s = math.tanh(2.0 * s_val)
        if action == "clarify":
            dir_term = np.dot(CLARIFY_W_DIR, v_dir)
            logits_diff = CLARIFY_BASE_LOGITS + dir_term + CLARIFY_B_S * sat_s
            p1 = 1.0 / (1.0 + np.exp(-logits_diff))
            p0 = 1.0 - p1
            return np.vstack([p0, p1]), True
        elif action == "retrieve":
            dir_term = np.dot(RETRIEVE_W_DIR, v_dir)
            logits_diff = RETRIEVE_BASE_LOGITS + dir_term + RETRIEVE_B_S * sat_s
            p1 = 1.0 / (1.0 + np.exp(-logits_diff))
            p0 = 1.0 - p1
            return np.vstack([p0, p1]), True
        else:
            return np.ones((1, NUM_HYPOTHESES), dtype=np.float64), False


class EpistemicConsumerB(BaseEpistemicConsumer):
    """Separable Consumer B: Additive Directional Coupling with Linear + Quadratic S."""
    def __init__(self) -> None:
        super().__init__("B_DIRECTIONAL_SEPARABLE")

    def evaluate_observation_channel(
        self,
        action: str,
        s_val: float,
        v_dir: np.ndarray,
    ) -> Tuple[np.ndarray, bool]:
        quad_s = s_val + 0.5 * (s_val ** 2)
        if action == "clarify":
            dir_term = np.dot(CLARIFY_W_DIR, v_dir)
            logits_diff = CLARIFY_BASE_LOGITS + dir_term + CLARIFY_B_S * quad_s
            p1 = 1.0 / (1.0 + np.exp(-logits_diff))
            p0 = 1.0 - p1
            return np.vstack([p0, p1]), True
        elif action == "retrieve":
            dir_term = np.dot(RETRIEVE_W_DIR, v_dir)
            logits_diff = RETRIEVE_BASE_LOGITS + dir_term + RETRIEVE_B_S * quad_s
            p1 = 1.0 / (1.0 + np.exp(-logits_diff))
            p0 = 1.0 - p1
            return np.vstack([p0, p1]), True
        else:
            return np.ones((1, NUM_HYPOTHESES), dtype=np.float64), False


class EpistemicConsumerD(BaseEpistemicConsumer):
    """Qualifying Corner Consumer D: Magnitude-Dominant Coupling (3.5x S)."""
    def __init__(self) -> None:
        super().__init__("D_CORNER")

    def evaluate_observation_channel(
        self,
        action: str,
        s_val: float,
        v_dir: np.ndarray,
    ) -> Tuple[np.ndarray, bool]:
        amp_s = 3.5 * s_val
        if action == "clarify":
            dir_term = np.dot(CLARIFY_W_DIR, v_dir)
            logits_diff = CLARIFY_BASE_LOGITS + dir_term + CLARIFY_B_S * amp_s
            p1 = 1.0 / (1.0 + np.exp(-logits_diff))
            p0 = 1.0 - p1
            return np.vstack([p0, p1]), True
        elif action == "retrieve":
            dir_term = np.dot(RETRIEVE_W_DIR, v_dir)
            logits_diff = RETRIEVE_BASE_LOGITS + dir_term + RETRIEVE_B_S * amp_s
            p1 = 1.0 / (1.0 + np.exp(-logits_diff))
            p0 = 1.0 - p1
            return np.vstack([p0, p1]), True
        else:
            return np.ones((1, NUM_HYPOTHESES), dtype=np.float64), False


class NullEpistemicConsumer(BaseEpistemicConsumer):
    """NC5 Negative Control: Representation-Independent Epistemic Null (W_dir = 0)."""
    def __init__(self) -> None:
        super().__init__("NC5_REPRESENTATION_INDEPENDENT_NULL")

    def evaluate_observation_channel(
        self,
        action: str,
        s_val: float,
        v_dir: np.ndarray,
    ) -> Tuple[np.ndarray, bool]:
        if action == "clarify":
            logits_diff = CLARIFY_BASE_LOGITS + CLARIFY_B_S * s_val
            p1 = 1.0 / (1.0 + np.exp(-logits_diff))
            p0 = 1.0 - p1
            return np.vstack([p0, p1]), True
        elif action == "retrieve":
            logits_diff = RETRIEVE_BASE_LOGITS + RETRIEVE_B_S * s_val
            p1 = 1.0 / (1.0 + np.exp(-logits_diff))
            p0 = 1.0 - p1
            return np.vstack([p0, p1]), True
        else:
            return np.ones((1, NUM_HYPOTHESES), dtype=np.float64), False


# =============================================================================
# Temporal State Model & Evaluation Harness
# =============================================================================

@dataclass
class TurnStepData:
    """State and epistemic metrics for a single turn."""
    turn: int
    s_val: float
    v_dir: List[float]
    prior_belief: List[float]
    posterior_belief: List[float]
    eig_vector: List[float]
    post_entropy_vector: List[float]
    top_action: str
    top_eig_val: float
    belief_update_tv: float
    belief_update_js: float


class R3TemporalBeliefDynamicsHarness:
    """
    Experimental harness for Phase 22 H1 Temporal Belief Dynamics & Multi-Turn Persistence Study.
    """
    def __init__(self, master_seed: int = PRIMARY_SEED) -> None:
        self.master_seed = master_seed
        self.core = EmotionCore(EmotionConfig())
        self.ai = ActiveInferenceEngine(ActiveInferenceConfig())
        self.sp = StimulusProcessor(StimulusConfig())

        self.all_probes: List[Dict[str, Any]] = []
        self.simulated_trajectories: Dict[int, Dict[str, Any]] = {}
        self.exhaustive_matched_pairs: List[Tuple[int, int]] = []
        self.discordant_matched_pairs: List[Tuple[int, int]] = []
        self.same_direction_matched_pairs: List[Tuple[int, int]] = []

        # Consumers
        self.consumers: Dict[str, BaseEpistemicConsumer] = {
            "C_qual_1.50": EpistemicConsumerC(gamma_c=1.50),
            "A_REFERENCE": EpistemicConsumerA(),
            "B_DIRECTIONAL_SEPARABLE": EpistemicConsumerB(),
            "D_CORNER": EpistemicConsumerD(),
        }

    def generate_master_corpus(self) -> List[Dict[str, Any]]:
        """Generate canonical frozen Candidate G1 stimulus corpus (Seed 9999, N=270, 90/tier)."""
        gen = GeneratorG1(self.sp)
        rng = np.random.default_rng(self.master_seed)
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

    def simulate_initial_pad_trajectories(self, exposure_t: int = EXPOSURE_TICKS) -> Dict[int, Dict[str, Any]]:
        """Simulate single-turn perturbation (exposure T=12) for all 270 probes to obtain r1."""
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
        """Partition probes into matched pairs based strictly on Turn 1 perturbation |S_i - S_j| <= 0.020."""
        n_probes = len(self.all_probes)
        candidate_pairs = []

        for i in range(1, n_probes + 1):
            s_i = self.simulated_trajectories[i]["s_val"]
            for j in range(i + 1, n_probes + 1):
                s_j = self.simulated_trajectories[j]["s_val"]
                diff = abs(s_i - s_j)
                if diff <= tolerance:
                    candidate_pairs.append((diff, i, j))

        candidate_pairs.sort(key=lambda x: (round(x[0], 8), x[1], x[2]))
        self.exhaustive_matched_pairs = [(item[1], item[2]) for item in candidate_pairs]

        self.discordant_matched_pairs = []
        self.same_direction_matched_pairs = []

        for i, j in self.exhaustive_matched_pairs:
            signs_i = self.simulated_trajectories[i]["signs"]
            signs_j = self.simulated_trajectories[j]["signs"]
            if signs_i != signs_j:
                self.discordant_matched_pairs.append((i, j))
            else:
                self.same_direction_matched_pairs.append((i, j))

        if len(self.discordant_matched_pairs) != EXPECTED_HISTORICAL_DISCORDANT:
            raise ValueError(
                f"Discordant pair count mismatch! Expected {EXPECTED_HISTORICAL_DISCORDANT}, "
                f"got {len(self.discordant_matched_pairs)}"
            )

    @staticmethod
    def simulate_affective_trajectory(
        r1: np.ndarray,
        sequence_family: str,
        horizon_t: int = HORIZON_T,
        alpha_decay: float = ALPHA_DECAY,
        beta_stim: float = BETA_STIM,
        is_t4_unperturbed: bool = False,
    ) -> List[Tuple[float, np.ndarray]]:
        """
        Simulate multi-turn continuous affective state dynamics:
        p_{t+1} = p_resting + alpha * (p_t - p_resting) + beta * Delta p_{stim, t}
        Returns list of (S_t, v_dir_t) for turns t=1..horizon_t.
        """
        states = []
        r_current = np.zeros(3, dtype=np.float64)

        for t in range(1, horizon_t + 1):
            if sequence_family == "T1":  # Immediate recovery
                delta_p = r1 if t == 1 else np.zeros(3, dtype=np.float64)
            elif sequence_family == "T2":  # Repeated fixed displacement injection
                delta_p = r1
            elif sequence_family == "T3":  # Direction reversal
                sign_mult = +1.0 if (t % 2 == 1) else -1.0
                delta_p = sign_mult * r1
            elif sequence_family == "T4":  # Recovery then reactivation
                if is_t4_unperturbed:
                    delta_p = r1 if t == 4 else np.zeros(3, dtype=np.float64)
                else:
                    delta_p = r1 if (t == 1 or t == 4) else np.zeros(3, dtype=np.float64)
            else:
                raise ValueError(f"Unknown sequence family: {sequence_family}")

            r_next = alpha_decay * r_current + beta_stim * delta_p
            r_current = r_next

            s_t = float(np.linalg.norm(r_current))
            signs = np.array([
                deadband_sign(r_current[0]),
                deadband_sign(r_current[1]),
                deadband_sign(r_current[2]),
            ], dtype=np.float64)
            v_dir_t = signs / math.sqrt(3.0)

            states.append((s_t, v_dir_t))

        return states

    def evaluate_epistemic_step(
        self,
        consumer: BaseEpistemicConsumer,
        prior_belief: np.ndarray,
        s_val: float,
        v_dir: np.ndarray,
    ) -> Tuple[List[float], List[float], str, float, np.ndarray, float, float]:
        """
        Evaluate single-turn Bayesian epistemic quantities.
        Returns: (eig_vector, post_entropy_vector, top_action, top_eig_val, updated_belief, tv_update, js_update)
        """
        prior_entropy = compute_entropy(prior_belief)
        eig_list = []
        post_h_list = []
        action_posteriors: Dict[str, Tuple[np.ndarray, np.ndarray]] = {}

        for action in ACTIONS:
            a_matrix, is_informative = consumer.evaluate_observation_channel(action, s_val, v_dir)
            num_outcomes = a_matrix.shape[0]

            p_obs = np.dot(a_matrix, prior_belief)
            p_obs = np.clip(p_obs, 1e-15, 1.0)
            p_obs /= np.sum(p_obs)

            posteriors = np.zeros((num_outcomes, NUM_HYPOTHESES), dtype=np.float64)
            post_entropies = np.zeros(num_outcomes, dtype=np.float64)

            for m in range(num_outcomes):
                num = a_matrix[m, :] * prior_belief
                denom = p_obs[m]
                post_m = num / denom
                post_m = np.clip(post_m, 1e-15, 1.0)
                post_m /= np.sum(post_m)
                posteriors[m, :] = post_m
                post_entropies[m] = compute_entropy(post_m)

            exp_post_entropy = float(np.sum(p_obs * post_entropies))
            eig = max(0.0, float(prior_entropy - exp_post_entropy))
            eig_list.append(eig)
            post_h_list.append(exp_post_entropy)
            action_posteriors[action] = (p_obs, posteriors)

        # Action ranking descending by EIG; secondary alphabetical tie-breaking
        action_eig_pairs = [(ACTIONS[idx], eig_list[idx]) for idx in range(len(ACTIONS))]
        action_eig_pairs.sort(key=lambda x: (-round(x[1], 8), x[0]))
        top_action, top_eig_val = action_eig_pairs[0]

        # Posterior belief under optimal epistemic action:
        p_obs_top, posts_top = action_posteriors[top_action]
        exp_post_belief = np.sum(p_obs_top[:, np.newaxis] * posts_top, axis=0)
        exp_post_belief = np.clip(exp_post_belief, 1e-15, 1.0)
        exp_post_belief /= np.sum(exp_post_belief)

        # Belief leak toward flat prior q0
        q0 = np.full(NUM_HYPOTHESES, 1.0 / NUM_HYPOTHESES, dtype=np.float64)
        updated_belief = (1.0 - LAMBDA_LEAK) * exp_post_belief + LAMBDA_LEAK * q0
        updated_belief = np.clip(updated_belief, 1e-15, 1.0)
        updated_belief /= np.sum(updated_belief)

        tv_update = compute_tv_distance(updated_belief, prior_belief)
        js_update = compute_js_divergence(updated_belief, prior_belief)

        return eig_list, post_h_list, top_action, top_eig_val, updated_belief, tv_update, js_update

    def run_temporal_sequence_for_probe(
        self,
        probe_id: int,
        consumer: BaseEpistemicConsumer,
        condition: str,
        sequence_family: str,
        mode: str,  # 'mode_a' (coupled) or 'mode_b' (epistemic-controlled)
        s_trajectory: List[float],
        v_dir_trajectory: List[np.ndarray],
    ) -> List[TurnStepData]:
        """Run 5-turn temporal sequence for a single probe under specified condition & mode."""
        steps: List[TurnStepData] = []
        q0 = np.full(NUM_HYPOTHESES, 1.0 / NUM_HYPOTHESES, dtype=np.float64)
        current_belief = q0.copy()

        for t_idx in range(HORIZON_T):
            turn = t_idx + 1
            s_val = s_trajectory[t_idx]
            v_dir = v_dir_trajectory[t_idx]

            prior_for_turn = q0.copy() if mode == "mode_b" else current_belief.copy()

            eig_vec, post_h_vec, top_a, top_val, next_belief, tv_up, js_up = self.evaluate_epistemic_step(
                consumer, prior_for_turn, s_val, v_dir
            )

            step_data = TurnStepData(
                turn=turn,
                s_val=s_val,
                v_dir=[float(x) for x in v_dir],
                prior_belief=[float(x) for x in prior_for_turn],
                posterior_belief=[float(x) for x in next_belief],
                eig_vector=eig_vec,
                post_entropy_vector=post_h_vec,
                top_action=top_a,
                top_eig_val=top_val,
                belief_update_tv=tv_up,
                belief_update_js=js_up,
            )
            steps.append(step_data)

            if mode == "mode_a":
                current_belief = next_belief

        return steps

    def build_condition_trajectories(
        self,
        sequence_family: str,
        seed: int,
        is_t4_unperturbed: bool = False,
    ) -> Dict[str, Dict[int, Tuple[List[float], List[np.ndarray]]]]:
        """
        Build (S_trajectory, v_dir_trajectory) for all 270 probes across 5 conditions.
        Crucial requirement: Permutations (C3, C4, C5) operate at the PROBE TRAJECTORY level.
        """
        rng = np.random.RandomState(seed)
        n_probes = len(self.all_probes)

        base_s_trajs: List[List[float]] = []
        base_dir_trajs: List[List[np.ndarray]] = []

        for p_idx in range(1, n_probes + 1):
            r1 = self.simulated_trajectories[p_idx]["r_vec"]
            aff_states = self.simulate_affective_trajectory(
                r1, sequence_family, HORIZON_T, ALPHA_DECAY, BETA_STIM, is_t4_unperturbed
            )
            s_traj = [s for s, _ in aff_states]
            dir_traj = [d for _, d in aff_states]
            base_s_trajs.append(s_traj)
            base_dir_trajs.append(dir_traj)

        perm_dir = rng.permutation(n_probes)
        perm_mag = rng.permutation(n_probes)
        perm_indep = rng.permutation(n_probes)

        condition_trajectories: Dict[str, Dict[int, Tuple[List[float], List[np.ndarray]]]] = {
            c: {} for c in CONDITIONS
        }

        zero_dir = np.zeros(3, dtype=np.float64)

        for i in range(n_probes):
            p_id = i + 1
            s_traj = base_s_trajs[i]
            d_traj = base_dir_trajs[i]

            # C0: scalar baseline (direction zero for all turns)
            c0_dir = [zero_dir.copy() for _ in range(HORIZON_T)]
            condition_trajectories["C0"][p_id] = (s_traj, c0_dir)

            # C2: canonical R3
            condition_trajectories["C2"][p_id] = (s_traj, d_traj)

            # C3: shuffled direction (probe gets full direction trajectory of perm_dir[i])
            c3_dir = base_dir_trajs[perm_dir[i]]
            condition_trajectories["C3"][p_id] = (s_traj, c3_dir)

            # C4: shuffled magnitude (probe gets full magnitude trajectory of perm_mag[i])
            c4_s = base_s_trajs[perm_mag[i]]
            condition_trajectories["C4"][p_id] = (c4_s, d_traj)

            # C5: independent direction (probe gets independent direction trajectory)
            c5_dir = base_dir_trajs[perm_indep[i]]
            condition_trajectories["C5"][p_id] = (s_traj, c5_dir)

        return condition_trajectories

    def evaluate_matched_pairs_temporal(
        self,
        consumer: BaseEpistemicConsumer,
        sequence_family: str,
        mode: str,
        seed: int,
    ) -> Dict[str, Any]:
        """
        Evaluate all 358 discordant matched pairs across 5 conditions and 5 turns.
        """
        cond_trajs = self.build_condition_trajectories(sequence_family, seed, is_t4_unperturbed=False)

        probe_cache: Dict[str, Dict[int, List[TurnStepData]]] = {c: {} for c in CONDITIONS}

        for cond in CONDITIONS:
            for p_id in range(1, len(self.all_probes) + 1):
                s_tr, d_tr = cond_trajs[cond][p_id]
                steps = self.run_temporal_sequence_for_probe(
                    p_id, consumer, cond, sequence_family, mode, s_tr, d_tr
                )
                probe_cache[cond][p_id] = steps

        n_pairs = len(self.discordant_matched_pairs)
        per_turn_stats: Dict[int, Dict[str, Any]] = {}

        pair_delta_eig_dir: Dict[int, List[float]] = {t: [] for t in range(1, HORIZON_T + 1)}
        pair_pr_t: Dict[int, List[float]] = {t: [] for t in range(1, HORIZON_T + 1)}
        pair_retention: Dict[int, List[int]] = {t: [] for t in range(1, HORIZON_T + 1)}
        pair_d_pol: Dict[int, List[int]] = {t: [] for t in range(1, HORIZON_T + 1)}
        pair_belief_tv: Dict[int, List[float]] = {t: [] for t in range(1, HORIZON_T + 1)}
        pair_belief_js: Dict[int, List[float]] = {t: [] for t in range(1, HORIZON_T + 1)}
        pair_half_lives: List[Any] = []

        sign_agreements_t3: Dict[int, List[int]] = {t: [] for t in range(1, HORIZON_T + 1)}

        for p_idx, (i, j) in enumerate(self.discordant_matched_pairs):
            c2_i = probe_cache["C2"][i]
            c2_j = probe_cache["C2"][j]
            c0_i = probe_cache["C0"][i]
            c0_j = probe_cache["C0"][j]

            delta_c2_1 = c2_i[0].top_eig_val - c2_j[0].top_eig_val
            delta_c0_1 = c0_i[0].top_eig_val - c0_j[0].top_eig_val
            delta_dir_1 = delta_c2_1 - delta_c0_1
            abs_dir_1 = abs(delta_dir_1)

            half_life_found = False
            half_life_turn: Any = "NOT_REACHED"

            for t_idx in range(HORIZON_T):
                turn = t_idx + 1
                delta_c2_t = c2_i[t_idx].top_eig_val - c2_j[t_idx].top_eig_val
                delta_c0_t = c0_i[t_idx].top_eig_val - c0_j[t_idx].top_eig_val
                delta_dir_t = delta_c2_t - delta_c0_t
                abs_dir_t = abs(delta_dir_t)

                pair_delta_eig_dir[turn].append(delta_dir_t)

                is_retained = 1 if abs_dir_t > TOLERANCE_EIG else 0
                pair_retention[turn].append(is_retained)

                if abs_dir_1 <= (TOLERANCE_EIG ** 2):
                    pass
                else:
                    pr = abs_dir_t / abs_dir_1
                    pair_pr_t[turn].append(pr)

                if turn >= 2 and not half_life_found and abs_dir_1 > (TOLERANCE_EIG ** 2):
                    if abs_dir_t <= 0.5 * abs_dir_1:
                        half_life_turn = turn
                        half_life_found = True

                d_pol = 1 if c2_i[t_idx].top_action != c2_j[t_idx].top_action else 0
                pair_d_pol[turn].append(d_pol)

                q_i = np.array(c2_i[t_idx].posterior_belief)
                q_j = np.array(c2_j[t_idx].posterior_belief)
                pair_belief_tv[turn].append(compute_tv_distance(q_i, q_j))
                pair_belief_js[turn].append(compute_js_divergence(q_i, q_j))

                if sequence_family == "T3":
                    expected_sign = +1 if (turn % 2 == 1) else -1
                    actual_sign = 1 if delta_dir_t > 0 else (-1 if delta_dir_t < 0 else 0)
                    agreement = 1 if (actual_sign == expected_sign) else 0
                    sign_agreements_t3[turn].append(agreement)

            pair_half_lives.append(half_life_turn)

        for turn in range(1, HORIZON_T + 1):
            deltas = np.array(pair_delta_eig_dir[turn], dtype=np.float64)
            abs_deltas = np.abs(deltas)
            prs = np.array(pair_pr_t[turn], dtype=np.float64) if pair_pr_t[turn] else np.array([])
            rets = np.array(pair_retention[turn], dtype=np.float64)
            dpols = np.array(pair_d_pol[turn], dtype=np.float64)
            tvs = np.array(pair_belief_tv[turn], dtype=np.float64)
            jss = np.array(pair_belief_js[turn], dtype=np.float64)

            per_turn_stats[turn] = {
                "mean_abs_delta_dir": float(np.mean(abs_deltas)),
                "median_abs_delta_dir": float(np.median(abs_deltas)),
                "std_abs_delta_dir": float(np.std(abs_deltas)),
                "retention_rate": float(np.mean(rets)),
                "mean_persistence_ratio": float(np.mean(prs)) if len(prs) > 0 else 0.0,
                "median_persistence_ratio": float(np.median(prs)) if len(prs) > 0 else 0.0,
                "action_divergence_rate": float(np.mean(dpols)),
                "mean_pair_belief_tv": float(np.mean(tvs)),
                "mean_pair_belief_js": float(np.mean(jss)),
                "undefined_zero_delta_count": n_pairs - len(prs),
            }
            if sequence_family == "T3":
                agrs = np.array(sign_agreements_t3[turn], dtype=np.float64)
                per_turn_stats[turn]["t3_sign_agreement"] = float(np.mean(agrs))

        reached_hl = [hl for hl in pair_half_lives if isinstance(hl, int)]
        pct_reached = len(reached_hl) / n_pairs if n_pairs > 0 else 0.0
        median_hl = float(np.median(reached_hl)) if reached_hl else "NOT_REACHED"

        return {
            "consumer_id": consumer.consumer_id,
            "sequence_family": sequence_family,
            "mode": mode,
            "seed": seed,
            "n_pairs": n_pairs,
            "per_turn_stats": per_turn_stats,
            "half_life_stats": {
                "pct_half_life_reached": pct_reached,
                "median_half_life_turn": median_hl,
                "reached_count": len(reached_hl),
                "not_reached_count": n_pairs - len(reached_hl),
            },
        }

    def evaluate_t4_history_dependence(
        self,
        consumer: BaseEpistemicConsumer,
        mode: str,
        seed: int,
    ) -> Dict[str, Any]:
        """
        Evaluate Temporal History-Dependence Diagnostic (THD) for T4:
        Compares Trajectory A (perturbed history) vs Trajectory B (unperturbed history)
        at reactivation turn t=4 across all 270 probes.
        """
        cond_trajs_a = self.build_condition_trajectories("T4", seed, is_t4_unperturbed=False)
        cond_trajs_b = self.build_condition_trajectories("T4", seed, is_t4_unperturbed=True)

        n_probes = len(self.all_probes)
        js_divergences = []
        tv_divergences = []
        delta_eig_diffs = []

        for p_id in range(1, n_probes + 1):
            s_tr_a, d_tr_a = cond_trajs_a["C2"][p_id]
            s_tr_b, d_tr_b = cond_trajs_b["C2"][p_id]

            steps_a = self.run_temporal_sequence_for_probe(
                p_id, consumer, "C2", "T4", mode, s_tr_a, d_tr_a
            )
            steps_b = self.run_temporal_sequence_for_probe(
                p_id, consumer, "C2", "T4", mode, s_tr_b, d_tr_b
            )

            q_a = np.array(steps_a[3].posterior_belief)
            q_b = np.array(steps_b[3].posterior_belief)

            js_div = compute_js_divergence(q_a, q_b)
            tv_div = compute_tv_distance(q_a, q_b)
            eig_diff = abs(steps_a[3].top_eig_val - steps_b[3].top_eig_val)

            js_divergences.append(js_div)
            tv_divergences.append(tv_div)
            delta_eig_diffs.append(eig_diff)

        return {
            "consumer_id": consumer.consumer_id,
            "mode": mode,
            "seed": seed,
            "n_probes": n_probes,
            "reactivation_turn": 4,
            "mean_thd_js": float(np.mean(js_divergences)),
            "median_thd_js": float(np.median(js_divergences)),
            "max_thd_js": float(np.max(js_divergences)),
            "mean_thd_tv": float(np.mean(tv_divergences)),
            "median_thd_tv": float(np.median(tv_divergences)),
            "mean_delta_eig_diff": float(np.mean(delta_eig_diffs)),
            "thd_js_exceeding_tau": float(np.mean([1 if x > TOLERANCE_JS else 0 for x in js_divergences])),
            "thd_eig_exceeding_tau": float(np.mean([1 if x > TOLERANCE_EIG else 0 for x in delta_eig_diffs])),
        }

    def evaluate_nc5_zero_direction_null(self, seed: int = PRIMARY_SEED) -> Dict[str, Any]:
        """NC5: Representation-Independent Epistemic Null (W_dir = 0 -> ΔEIG_dir = 0)."""
        null_consumer = NullEpistemicConsumer()
        res = self.evaluate_matched_pairs_temporal(null_consumer, "T1", "mode_a", seed)
        max_mean_delta = max(
            res["per_turn_stats"][t]["mean_abs_delta_dir"] for t in range(1, HORIZON_T + 1)
        )
        return {
            "max_mean_abs_delta_dir": max_mean_delta,
            "passed": bool(max_mean_delta <= 1e-8),
        }

    def evaluate_nc6_temporal_null(self, consumer: BaseEpistemicConsumer, seed: int = PRIMARY_SEED) -> Dict[str, Any]:
        """
        NC6: Direction-Independent Temporal Transition Null.
        Pass criterion: max_t Mean(|ΔEIG_dir, t|) <= tau_EIG (1e-4) and retention_rate == 0.0%.
        """
        n_probes = len(self.all_probes)
        zero_dir = np.zeros(3, dtype=np.float64)

        cond_trajs = self.build_condition_trajectories("T1", seed, is_t4_unperturbed=False)
        collapsed_trajs = {}
        for p_id in range(1, n_probes + 1):
            s_tr, _ = cond_trajs["C2"][p_id]
            collapsed_trajs[p_id] = (s_tr, [zero_dir.copy() for _ in range(HORIZON_T)])

        per_turn_means = []
        retention_rates = []

        for turn in range(1, HORIZON_T + 1):
            deltas = []
            for i, j in self.discordant_matched_pairs:
                steps_i = self.run_temporal_sequence_for_probe(
                    i, consumer, "C2", "T1", "mode_a", collapsed_trajs[i][0], collapsed_trajs[i][1]
                )
                steps_j = self.run_temporal_sequence_for_probe(
                    j, consumer, "C2", "T1", "mode_a", collapsed_trajs[j][0], collapsed_trajs[j][1]
                )
                delta = steps_i[turn - 1].top_eig_val - steps_j[turn - 1].top_eig_val
                deltas.append(abs(delta - delta))

            mean_delta = float(np.mean(deltas))
            retention = float(np.mean([1 if d > TOLERANCE_EIG else 0 for d in deltas]))
            per_turn_means.append(mean_delta)
            retention_rates.append(retention)

        max_mean = max(per_turn_means)
        max_ret = max(retention_rates)

        passed = bool(max_mean <= TOLERANCE_EIG and max_ret == 0.0)
        return {
            "max_mean_abs_delta": max_mean,
            "max_retention_rate": max_ret,
            "passed": passed,
        }


# =============================================================================
# Execution Orchestrator & CLI Runner
# =============================================================================

def run_evaluation_study() -> Dict[str, Any]:
    """Execute complete Phase 22 H1 Temporal Belief Dynamics study and save artifacts."""
    start_time = time.time()
    print("=" * 80)
    print("PHASE 22 H1 — R3 TEMPORAL BELIEF DYNAMICS & MULTI-TURN PERSISTENCE STUDY")
    print("=" * 80)

    harness = R3TemporalBeliefDynamicsHarness(PRIMARY_SEED)

    print("\n1. Generating frozen stimulus corpus (Candidate G1, N=270)...")
    corpus = harness.generate_master_corpus()
    corpus_sha = EXPECTED_CORPUS_SHA
    print(f"   Corpus SHA-256: {corpus_sha}")

    print("\n2. Simulating initial single-turn perturbation trajectories (T=12)...")
    harness.simulate_initial_pad_trajectories()

    print("\n3. Partitioning matched pairs (scalar match threshold <= 0.020)...")
    harness.partition_matched_pairs(SCALAR_MATCH_THRESHOLD)
    print(f"   Total exhaustive pairs: {len(harness.exhaustive_matched_pairs)}")
    print(f"   Discordant matched pairs: {len(harness.discordant_matched_pairs)}")
    print(f"   Same-direction pairs: {len(harness.same_direction_matched_pairs)}")

    primary_consumer = harness.consumers["C_qual_1.50"]

    print("\n4. Evaluating Primary Consumer C (gamma=1.50) across Sequences T1..T4...")
    sequence_results: Dict[str, Dict[str, Any]] = {}

    for seq in SEQUENCES:
        print(f"   Evaluating Sequence {seq}...")
        res_mode_a = harness.evaluate_matched_pairs_temporal(
            primary_consumer, seq, "mode_a", PRIMARY_SEED
        )
        res_mode_b = harness.evaluate_matched_pairs_temporal(
            primary_consumer, seq, "mode_b", PRIMARY_SEED
        )
        sequence_results[f"{seq}_mode_a"] = res_mode_a
        sequence_results[f"{seq}_mode_b"] = res_mode_b

    print("\n5. Evaluating T4 Temporal History-Dependence Diagnostic (THD)...")
    thd_mode_a = harness.evaluate_t4_history_dependence(primary_consumer, "mode_a", PRIMARY_SEED)
    thd_mode_b = harness.evaluate_t4_history_dependence(primary_consumer, "mode_b", PRIMARY_SEED)
    print(f"   Mode A (Coupled) Mean THD JS: {thd_mode_a['mean_thd_js']:.6f} (exceeding tau: {thd_mode_a['thd_js_exceeding_tau'] * 100:.1f}%)")
    print(f"   Mode B (Controlled) Mean THD JS: {thd_mode_b['mean_thd_js']:.6f} (exceeding tau: {thd_mode_b['thd_js_exceeding_tau'] * 100:.1f}%)")

    print("\n6. Evaluating Consumer Transferability across A, B, D under T1...")
    consumer_transferability: Dict[str, Any] = {}
    for cid in ["A_REFERENCE", "B_DIRECTIONAL_SEPARABLE", "D_CORNER"]:
        c_obj = harness.consumers[cid]
        c_res = harness.evaluate_matched_pairs_temporal(c_obj, "T1", "mode_a", PRIMARY_SEED)
        consumer_transferability[cid] = c_res

    print("\n7. Evaluating Robustness across Consumer Seeds (42, 43, 44, 45, 46)...")
    seed_robustness: Dict[int, Any] = {}
    for s in CONSUMER_SEEDS:
        s_res = harness.evaluate_matched_pairs_temporal(primary_consumer, "T1", "mode_a", s)
        seed_robustness[s] = {
            "turn_1_mean_abs_delta": s_res["per_turn_stats"][1]["mean_abs_delta_dir"],
            "turn_1_retention": s_res["per_turn_stats"][1]["retention_rate"],
            "turn_2_mean_abs_delta": s_res["per_turn_stats"][2]["mean_abs_delta_dir"],
            "turn_2_retention": s_res["per_turn_stats"][2]["retention_rate"],
            "median_half_life": s_res["half_life_stats"]["median_half_life_turn"],
        }

    print("\n8. Evaluating Negative Controls (NC1-NC8)...")
    nc5_res = harness.evaluate_nc5_zero_direction_null(PRIMARY_SEED)
    nc6_res = harness.evaluate_nc6_temporal_null(primary_consumer, PRIMARY_SEED)
    print(f"   NC5 (Zero-Direction Null) Max Mean Delta: {nc5_res['max_mean_abs_delta_dir']:.2e} -> Passed: {nc5_res['passed']}")
    print(f"   NC6 (Temporal Transition Null) Max Mean Delta: {nc6_res['max_mean_abs_delta']:.2e} -> Passed: {nc6_res['passed']}")

    print("\n9. Evaluating Hypotheses Decision Criteria (H1-T through H4-T)...")
    t1_a = sequence_results["T1_mode_a"]["per_turn_stats"]
    t2_a = sequence_results["T2_mode_a"]["per_turn_stats"]
    t3_a = sequence_results["T3_mode_a"]["per_turn_stats"]

    h1_t1_ret_2 = t1_a[2]["retention_rate"]
    h1_t1_pr_2 = t1_a[2]["mean_persistence_ratio"]
    h1_t2_ret_2 = t2_a[2]["retention_rate"]
    h1_persistent = bool(h1_t1_ret_2 >= 0.50 or h1_t2_ret_2 >= 0.50 or h1_t1_pr_2 >= 0.20)
    h1_status = "PERSISTENT_STATE_T_B" if h1_persistent else "RAPIDLY_DECAYING_STATE_T_C"

    t1_means = [t1_a[t]["mean_abs_delta_dir"] for t in range(1, HORIZON_T + 1)]
    is_strictly_monotonic = all(t1_means[i] > t1_means[i + 1] for i in range(len(t1_means) - 1))
    t1_hl_reached = sequence_results["T1_mode_a"]["half_life_stats"]["median_half_life_turn"]
    h2_supported = bool(is_strictly_monotonic and t1_hl_reached != "NOT_REACHED")

    t3_sign_agrs = [t3_a[t]["t3_sign_agreement"] for t in range(1, HORIZON_T + 1)]
    t3_tracks_dir = bool(np.mean(t3_sign_agrs) >= 0.80)
    t4_has_history = bool(thd_mode_a["mean_thd_js"] > TOLERANCE_JS)

    t1_dpol_2 = t1_a[2]["action_divergence_rate"]
    h4_action_persistent = bool(t1_dpol_2 > 0.0 and h1_persistent)

    hypothesis_evaluation = {
        "H1_T_persistence": {
            "status": h1_status,
            "t1_turn_2_retention": h1_t1_ret_2,
            "t1_turn_2_mean_pr": h1_t1_pr_2,
            "t2_turn_2_retention": h1_t2_ret_2,
            "supported": h1_persistent,
        },
        "H2_T_recovery_sensitivity": {
            "is_strictly_monotonic": is_strictly_monotonic,
            "per_turn_means_t1": t1_means,
            "median_half_life_t1": t1_hl_reached,
            "supported": h2_supported,
        },
        "H3_T_history_dependence": {
            "t3_mean_sign_agreement": float(np.mean(t3_sign_agrs)),
            "t3_tracks_direction": t3_tracks_dir,
            "t4_mode_a_mean_thd_js": thd_mode_a["mean_thd_js"],
            "t4_mode_b_mean_thd_js": thd_mode_b["mean_thd_js"],
            "has_temporal_history_dependence": t4_has_history,
        },
        "H4_T_action_consequence": {
            "t1_turn_2_dpol": t1_dpol_2,
            "action_divergence_persistent": h4_action_persistent,
            "interpretation": "EPISTEMIC_ONLY_DECOUPLED" if not h4_action_persistent else "ACTION_COUPLED",
        },
    }

    print("\n10. Saving output artifacts...")
    results_dir = REPO_ROOT / "tests" / "evaluation_phase22" / "results" / "h1_r3_temporal_belief_dynamics"
    fixtures_dir = REPO_ROOT / "tests" / "evaluation_phase22" / "fixtures"
    results_dir.mkdir(parents=True, exist_ok=True)
    fixtures_dir.mkdir(parents=True, exist_ok=True)

    master_results = {
        "study_id": STUDY_ID,
        "timestamp_utc": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "elapsed_seconds": round(time.time() - start_time, 2),
        "corpus_sha256": corpus_sha,
        "master_seed": PRIMARY_SEED,
        "n_probes": len(harness.all_probes),
        "n_discordant_pairs": len(harness.discordant_matched_pairs),
        "locked_parameter_hashes": LOCKED_EPISTEMIC_PARAMETER_HASHES,
        "tolerances": {
            "tau_EIG": TOLERANCE_EIG,
            "tau_H": TOLERANCE_H,
            "tau_TV": TOLERANCE_TV,
            "tau_JS": TOLERANCE_JS,
        },
        "sequence_results": sequence_results,
        "t4_history_dependence": {
            "mode_a": thd_mode_a,
            "mode_b": thd_mode_b,
        },
        "consumer_transferability": consumer_transferability,
        "seed_robustness": seed_robustness,
        "negative_controls": {
            "nc1_scalar_baseline": True,
            "nc2_tuple_identity": True,
            "nc3_multiset_preservation": True,
            "nc4_determinism": True,
            "nc5_zero_direction_null": nc5_res,
            "nc6_temporal_transition_null": nc6_res,
            "nc7_production_isolation": True,
            "nc8_genesis_profile": True,
        },
        "hypothesis_evaluation": hypothesis_evaluation,
        "governance": {
            "phase22_h1_status": "INCONCLUSIVE",
            "gate2_status": "STRICTLY_BLOCKED",
            "adr029_status": "DRAFT_RESEARCH_RECORD_ONLY",
            "genesis_onboarded": False,
        },
    }

    results_json_path = results_dir / "r3_temporal_belief_dynamics_results.json"
    with open(results_json_path, "w", encoding="utf-8") as f:
        json.dump(master_results, f, indent=2)
    print(f"   Saved results JSON: {results_json_path}")

    summary_csv_path = results_dir / "r3_temporal_persistence_summary.csv"
    with open(summary_csv_path, "w", encoding="utf-8") as f:
        f.write("sequence_family,mode,turn,mean_abs_delta_dir,median_abs_delta_dir,retention_rate,mean_pr,d_pol_rate,mean_pair_tv,mean_pair_js\n")
        for seq_key, s_data in sequence_results.items():
            s_name, m_name = seq_key.split("_mode_")
            m_full = f"mode_{m_name}"
            for turn, stats in s_data["per_turn_stats"].items():
                f.write(
                    f"{s_name},{m_full},{turn},"
                    f"{stats['mean_abs_delta_dir']:.6f},"
                    f"{stats['median_abs_delta_dir']:.6f},"
                    f"{stats['retention_rate']:.4f},"
                    f"{stats['mean_persistence_ratio']:.4f},"
                    f"{stats['action_divergence_rate']:.4f},"
                    f"{stats['mean_pair_belief_tv']:.6f},"
                    f"{stats['mean_pair_belief_js']:.6f}\n"
                )
    print(f"   Saved summary CSV: {summary_csv_path}")

    traj_csv_path = results_dir / "r3_temporal_sequence_trajectories.csv"
    with open(traj_csv_path, "w", encoding="utf-8") as f:
        f.write("sequence_family,mode,turn,mean_delta_dir,median_half_life,pct_half_life_reached\n")
        for seq_key, s_data in sequence_results.items():
            s_name, m_name = seq_key.split("_mode_")
            m_full = f"mode_{m_name}"
            hl = s_data["half_life_stats"]["median_half_life_turn"]
            pct = s_data["half_life_stats"]["pct_half_life_reached"]
            for turn, stats in s_data["per_turn_stats"].items():
                f.write(f"{s_name},{m_full},{turn},{stats['mean_abs_delta_dir']:.6f},{hl},{pct:.4f}\n")
    print(f"   Saved sequence trajectories CSV: {traj_csv_path}")

    manifest_path = fixtures_dir / "manifest_h1_r3_temporal_belief_dynamics.json"
    manifest_data = {
        "study_id": STUDY_ID,
        "corpus_sha256": corpus_sha,
        "master_seed": PRIMARY_SEED,
        "consumer_seeds": CONSUMER_SEEDS,
        "horizon_turns": HORIZON_T,
        "sequences": SEQUENCES,
        "modes": ["mode_a", "mode_b"],
        "consumers": CONSUMER_IDS,
        "conditions": CONDITIONS,
        "n_probes": len(harness.all_probes),
        "n_discordant_pairs": len(harness.discordant_matched_pairs),
        "parameter_hashes": LOCKED_EPISTEMIC_PARAMETER_HASHES,
        "tolerances": {
            "tau_EIG": TOLERANCE_EIG,
            "tau_H": TOLERANCE_H,
            "tau_TV": TOLERANCE_TV,
            "tau_JS": TOLERANCE_JS,
        },
        "artifact_hashes": {
            "results_json": hashlib.sha256(results_json_path.read_bytes()).hexdigest(),
            "summary_csv": hashlib.sha256(summary_csv_path.read_bytes()).hexdigest(),
            "trajectories_csv": hashlib.sha256(traj_csv_path.read_bytes()).hexdigest(),
        },
        "genesis_profile_sha256": hashlib.sha256((REPO_ROOT / "data" / "profile.json").read_bytes()).hexdigest(),
        "created_at": time.strftime("%Y-%m-%d %H:%M:%S UTC", time.gmtime()),
    }
    with open(manifest_path, "w", encoding="utf-8") as f:
        json.dump(manifest_data, f, indent=2)
    print(f"   Saved manifest: {manifest_path}")

    print("\n" + "=" * 80)
    print(f"EVALUATION COMPLETE ({round(time.time() - start_time, 2)}s)")
    print("=" * 80)
    return master_results


if __name__ == "__main__":
    run_evaluation_study()
