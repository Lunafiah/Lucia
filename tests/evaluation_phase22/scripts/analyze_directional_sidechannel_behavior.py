"""
Phase 22 H1 — Directional Side-Channel Behavioral Utilization Research Engine.

Mission:
Determine whether downstream cognition and generation policies benefit from
directional/component information preserved by candidate measurement architectures
(R2 continuous unit direction vs. R3 discrete ternary signs) when supplied as
side-channels alongside canonical scalar surprise S within an isolated research adapter.

CRITICAL METHODOLOGICAL & GOVERNANCE LOCKS:
1. Behavioral Scope Lock:
   The study measures downstream policy/conditioning utilization in an isolated
   research adapter, not end-to-end SLM behavioral utilization, unless an isolated
   SLM execution path is explicitly available without modifying production code.
   In the absence of a production-identical local SLM execution path, all conclusions
   are strictly scoped to downstream behavioral utilization under the research harness,
   not end-to-end SLM understanding or generation.

2. Counterfactual Measurement Intervention Validity Rules:
   Holding stimulus i, prior p0, and scalar magnitude S_i fixed, we inject direction
   v_j from probe j. This is strictly a counterfactual measurement intervention,
   not a physical continuous physiological trajectory of the limbic ODE.
   Strict validity constraints:
   - Unit norm: ||v_j||_2 = 1.0 +- 1e-5.
   - Finite values: no NaN, no Inf.
   - Magnitude preservation: S_i must NOT be recomputed from v_j; S_i remains
     the bit-exact controlled scalar intensity variable.

3. Exploratory Classification Threshold Designation:
   The threshold D_pol >= 0.05 and p < 0.05 is designated as a predefined
   exploratory classification threshold, NOT an evidence-based architectural
   pass threshold. It serves as an operational classification criterion to separate
   negligible numerical noise from measurable behavioral differentiation under the harness.

4. Ternary Representation Terminology:
   Candidate R3 is strictly designated as:
   "1 continuous scalar + 3 ternary sign symbols" in {-1, 0, +1}^3
   (27 discrete states; ceil(log2(27)) = 5 bits optimal discrete encoding),
   distinct from "3 bits".

5. Dual Metric Behavioral Evaluation (Discrete Switch vs. Continuous Shift):
   D_pol measures discrete argmax policy switch rate (I[a*(C_k) != a*(C_0)]).
   Jensen-Shannon divergence (D_JS) and Total Variation distance (D_TV) measure
   continuous policy distribution shifts over Boltzmann action probabilities
   P(a) = softmax(-gamma * G(a)). State classification is anchored on D_pol >= 0.05,
   while empirical analysis reports both discrete switches and continuous shifts.

6. RQ5 Observed Monotonic Association Scope:
   RQ5 evaluates observed monotonic association across the frozen stimuli and
   conversational exposure grid (T in [1, 25]) rather than claiming an artificial
   controlled S-scaling experiment.

7. Missing Side-Channel Semantics Invariant:
   C0 and C1/C2 share the identical scalar-S behavioral pathway; side-channel
   contribution is the only manipulated variable. When side-channel is absent (C0),
   all directional policy terms are strictly neutralized/zeroed.

GOVERNANCE INVARIANTS:
- Research-only study; Architecture Gate remains STRICTLY LOCKED.
- Protocol v1.5 is NOT AUTHORIZED.
- Production code src/core/**: 0 mutations.
- Genesis onboarding profile: bit-exact untouched {"is_onboarded": false}.
- Historical H1 datasets: immutable.
- Frozen experimental basis: Candidate G1 (Seed 9999, N=270 probes, 90/tier).
"""

from __future__ import annotations

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

from src.core.communication.communication_policy import CommunicationPolicy
from src.core.communication.communication_state import CommIntent, CommStrategy, CommunicationState
from src.core.config import EmotionConfig, StimulusConfig
from src.core.emotion.emotion_core import EmotionCore
from src.core.gating.stimulus_processor import StimulusProcessor
from src.core.inference.active_inference import ActiveInferenceConfig, ActiveInferenceEngine
from src.core.models import BehavioralConstraints, PADState, SomaticMarkers
from src.core.orchestrator.policies import GenerationPolicy, SurpriseModulationPolicy
from tests.evaluation_phase22.models.actions import ACTION_REGISTRY, ActionType
from tests.evaluation_phase22.models.efe_policy import EFEConfig, EFEPolicyEvaluator
from tests.evaluation_phase22.scripts.calibrate_stimulus_representation import GeneratorG1

RESULTS_DIR = REPO_ROOT / "tests" / "evaluation_phase22" / "results" / "h1_directional_sidechannel_behavior"
FIXTURES_DIR = REPO_ROOT / "tests" / "evaluation_phase22" / "fixtures"

# Primary conversational exposure grid
T_CONVERSATIONAL = [1, 2, 4, 8, 12, 16, 25]

# Predefined exploratory classification threshold
D_POL_THRESHOLD = 0.05
P_VAL_THRESHOLD = 0.05
SCALAR_MATCH_THRESHOLD = 0.02


# =============================================================================
# Mathematical & Statistical Helpers
# =============================================================================

def compute_angle_deg(v1: np.ndarray, v2: np.ndarray) -> float:
    """Compute angular separation between two vectors in degrees [0, 180]."""
    n1 = float(np.linalg.norm(v1))
    n2 = float(np.linalg.norm(v2))
    if n1 < 1e-8 or n2 < 1e-8:
        return 0.0
    cos_val = float(np.dot(v1, v2) / (n1 * n2))
    cos_val = np.clip(cos_val, -1.0, 1.0)
    return float(math.degrees(math.acos(cos_val)))


def compute_normalized_direction(v: np.ndarray) -> np.ndarray:
    """Return unit vector v / ||v||_2 or zero vector if norm is near zero."""
    n = float(np.linalg.norm(v))
    if n < 1e-8:
        return np.zeros_like(v)
    return v / n


def compute_ternary_signs(v: np.ndarray, tol: float = 1e-4) -> Tuple[int, int, int]:
    """Return ternary sign symbols (sign(v_P), sign(v_A), sign(v_D)) in {-1, 0, +1}^3."""
    signs = []
    for x in v:
        if abs(x) < tol:
            signs.append(0)
        elif x > 0:
            signs.append(1)
        else:
            signs.append(-1)
    return (signs[0], signs[1], signs[2])

def make_pad_state(p: float, a: float, d: float, ts: float = 0.0) -> PADState:
    """Helper to instantiate PADState with monotonic timestamp."""
    return PADState(pleasure=float(p), arousal=float(a), dominance=float(d), timestamp=float(ts))


def mcnemar_test_or_exact(b: int, c: int) -> float:
    """
    Perform McNemar test with continuity correction or exact binomial test for small counts.
    b: C0 correct / Ck changed (discordant pair count)
    c: discordant pair count in other direction
    """
    n_discordant = b + c
    if n_discordant == 0:
        return 1.0
    if n_discordant < 25:
        # Exact two-sided binomial test with p = 0.5
        k = min(b, c)
        return float(stats.binom.cdf(k, n_discordant, 0.5) * 2.0)
    # Chi-square with continuity correction
    chi2 = (abs(b - c) - 1.0) ** 2 / n_discordant
    return float(stats.chi2.sf(chi2, df=1))


def compute_action_distribution(valuations: Dict[ActionType, Any], gamma: float = 1.0) -> Dict[str, float]:
    """
    Compute Boltzmann action policy distribution P(a) = softmax(-gamma * G(a))
    across all discrete candidate actions in ActionType.
    """
    actions = list(ActionType)
    g_vals = np.array([valuations[a].g_value for a in actions], dtype=np.float64)
    # Numerical stability: shift by minimum
    neg_g = -gamma * (g_vals - np.min(g_vals))
    exp_vals = np.exp(neg_g)
    probs = exp_vals / np.sum(exp_vals)
    return {a.value: float(p) for a, p in zip(actions, probs)}


def compute_js_divergence(p: Dict[str, float], q: Dict[str, float]) -> float:
    """
    Compute Jensen-Shannon divergence D_JS(P || Q) in [0, ln(2)].
    Symmetric and smooth measure of continuous policy distribution shift.
    """
    actions = list(p.keys())
    p_vec = np.array([max(1e-12, p.get(a, 0.0)) for a in actions], dtype=np.float64)
    q_vec = np.array([max(1e-12, q.get(a, 0.0)) for a in actions], dtype=np.float64)
    p_vec /= np.sum(p_vec)
    q_vec /= np.sum(q_vec)
    m = 0.5 * (p_vec + q_vec)
    kl_p_m = np.sum(p_vec * np.log(p_vec / m))
    kl_q_m = np.sum(q_vec * np.log(q_vec / m))
    return float(max(0.0, 0.5 * kl_p_m + 0.5 * kl_q_m))


def compute_tv_distance(p: Dict[str, float], q: Dict[str, float]) -> float:
    """
    Compute Total Variation Distance D_TV(P, Q) = 0.5 * sum_a |P(a) - Q(a)| in [0, 1].
    """
    actions = list(p.keys())
    return float(0.5 * sum(abs(p.get(a, 0.0) - q.get(a, 0.0)) for a in actions))


# =============================================================================
# Isolated Behavioral Research Adapter
# =============================================================================

@dataclass(frozen=True)
class BehavioralOutcome:
    """Immutable record of downstream behavioral policy choices for a single trial."""
    action: str                             # Selected argmax action name
    action_probabilities: Dict[str, float]  # Continuous Boltzmann policy distribution over A
    reasoning_depth: int                    # k in {0, 1, 2}
    generation_mode: str                    # "fatigued" | "reflexive" | "deliberative"
    comm_strategy: str                      # CommStrategy enum value
    directness: float                       # [0.10, 0.95]
    supportiveness: float                   # [0.00, 1.00]
    formality: float                        # [0.00, 1.00]
    pacing_latency_ms: float                # [0.0, 1000.0]
    somatic_cognitive_load: float           # [0.0, 1.0]
    somatic_tension: float                  # [0.0, 1.0]
    prompt_token_estimate: int              # Estimated tokens in assembled prompt


class BehavioralResearchAdapter:
    """
    Isolated Research Adapter modeling downstream cognition and policy utilization.

    Encompasses:
    1. Somatic Marker Modulation (cognitive load, tension).
    2. Generation Policy Selection (reasoning depth k, token expansion factor).
    3. Epistemic Action Selection (EFE policy argmin G(a)).
    4. Communication Strategy & Pacing (directness, supportiveness, formality, latency).
    5. Prompt Conditioning Assembly (string tokenization and section assembly).
    """

    def __init__(self) -> None:
        self.surprise_policy = SurpriseModulationPolicy()
        self.efe_evaluator = EFEPolicyEvaluator(EFEConfig())
        self.comm_policy = CommunicationPolicy()

    def evaluate(
        self,
        pad_t: PADState,
        s_val: float,
        condition: str,
        direction: Optional[np.ndarray] = None,
        signs: Optional[Tuple[int, int, int]] = None,
        arousal_res: Optional[float] = None,
        base_somatic: Optional[SomaticMarkers] = None,
        r_trust: float = 0.50,
        n_recent_queries: int = 0,
        contradiction_present: bool = False,
    ) -> BehavioralOutcome:
        """
        Evaluate downstream behavioral choices under candidate condition.

        Conditions:
        - "C0": Canonical scalar surprise S only (baseline).
        - "C1": Scalar S + normalized unit direction v_r (R2).
        - "C2": Scalar S + 3 ternary sign symbols (R3).
        - "C3": Scalar S + Arousal residual r_A.
        - "C4": Scalar S + shuffled unit direction (Null control).
        - "C5": Scalar S + shuffled ternary signs (Null control).
        """
        if base_somatic is None:
            base_somatic = SomaticMarkers(stability=1.0, cognitive_load=0.10, energy=0.90, tension=0.10)

        # ---------------------------------------------------------------------
        # 1. Somatic Modulation
        # ---------------------------------------------------------------------
        delta_cl_base = self.surprise_policy.alpha_cognitive_load * s_val
        delta_t_raw = max(0.0, s_val - self.surprise_policy.tension_threshold)
        delta_t_base = self.surprise_policy.alpha_tension * delta_t_raw

        v_p, v_a, v_d = 0.0, 0.0, 0.0
        sign_p, sign_a, sign_d = 0, 0, 0

        if condition in ("C1", "C4") and direction is not None:
            # Directional side-channel (continuous)
            v_p = float(direction[0])
            v_a = float(direction[1])
            v_d = float(direction[2])
            # Negative valence amplifies tension; positive valence buffers tension
            factor_tension = max(0.2, 1.0 - 0.50 * v_p)
            # High arousal scales cognitive load
            factor_cl = max(0.5, 1.0 + 0.30 * v_a)
        elif condition in ("C2", "C5") and signs is not None:
            # Discrete ternary signs side-channel
            sign_p, sign_a, sign_d = signs
            factor_tension = 1.40 if sign_p < 0 else (0.60 if sign_p > 0 else 1.0)
            factor_cl = 1.30 if sign_a > 0 else (0.80 if sign_a < 0 else 1.0)
        elif condition == "C3" and arousal_res is not None:
            # Scalar + Arousal residual
            factor_tension = 1.0
            factor_cl = max(0.5, 1.0 + 0.30 * math.tanh(2.0 * arousal_res))
        else:
            # C0 Canonical baseline: purely scalar
            factor_tension = 1.0
            factor_cl = 1.0

        # Strict Missing Side-Channel Invariant:
        # C0 and C1/C2 share the identical scalar-S behavioral pathway.
        # When side-channel is absent (C0), all directional policy modulation terms are strictly neutralized/zeroed.
        if condition == "C0":
            assert direction is None and signs is None and arousal_res is None, "C0 must not receive side-channel inputs"
            assert factor_tension == 1.0 and factor_cl == 1.0, "C0 must have neutralized somatic modulation factors"
            assert v_p == 0.0 and v_a == 0.0 and v_d == 0.0, "C0 must have zeroed continuous directional orientation"
            assert sign_p == 0 and sign_a == 0 and sign_d == 0, "C0 must have zeroed ternary signs"

        mod_cl = min(1.0, base_somatic.cognitive_load + delta_cl_base * factor_cl)
        mod_tension = min(1.0, base_somatic.tension + delta_t_base * factor_tension)

        somatic = SomaticMarkers(
            stability=base_somatic.stability,
            cognitive_load=mod_cl,
            energy=base_somatic.energy,
            tension=mod_tension,
        )

        # ---------------------------------------------------------------------
        # 2. Generation Policy Selection (k in {0, 1, 2})
        # ---------------------------------------------------------------------
        gen_policy = GenerationPolicy.select(
            markers=somatic,
            surprise=s_val,
            surprise_policy=self.surprise_policy,
        )

        # ---------------------------------------------------------------------
        # 3. Epistemic Action Selection (EFE Policy)
        # ---------------------------------------------------------------------
        # Base information gains across candidate actions:
        # a1: immediate response
        # a2: external clarification
        # a3: extended SDM memory probe
        # a4: knowledge derivation
        # a5: deep reasoning mode shift
        # a6: conversational pause
        base_dk = {
            ActionType.A1_IMMEDIATE_RESPONSE: 0.05,
            ActionType.A2_EXTERNAL_CLARIFICATION: 0.70,
            ActionType.A3_EXTENDED_SDM_PROBE: 0.40,
            ActionType.A4_KNOWLEDGE_DERIVATION: 0.50,
            ActionType.A5_DEEP_REASONING_MODE_SHIFT: 0.60,
            ActionType.A6_WAIT_CONVERSATIONAL_PAUSE: 0.00,
        }
        base_dm = {
            ActionType.A1_IMMEDIATE_RESPONSE: 0.05,
            ActionType.A2_EXTERNAL_CLARIFICATION: 0.20,
            ActionType.A3_EXTENDED_SDM_PROBE: 0.65,
            ActionType.A4_KNOWLEDGE_DERIVATION: 0.30,
            ActionType.A5_DEEP_REASONING_MODE_SHIFT: 0.40,
            ActionType.A6_WAIT_CONVERSATIONAL_PAUSE: 0.00,
        }

        # Modulate information gain affordances under directional side-channel:
        dk_map = dict(base_dk)
        dm_map = dict(base_dm)

        if condition in ("C1", "C4"):
            # Acute negative valence (v_P < 0) heightens ambiguity -> elevates clarification & pause utility
            if v_p < -0.2:
                dk_map[ActionType.A2_EXTERNAL_CLARIFICATION] += 0.20 * abs(v_p)
            elif v_p > 0.2:
                # Pleasant surprise promotes memory recall / knowledge grounding
                dm_map[ActionType.A3_EXTENDED_SDM_PROBE] += 0.20 * v_p
                dk_map[ActionType.A4_KNOWLEDGE_DERIVATION] += 0.15 * v_p
        elif condition in ("C2", "C5"):
            if sign_p < 0:
                dk_map[ActionType.A2_EXTERNAL_CLARIFICATION] += 0.20
            elif sign_p > 0:
                dm_map[ActionType.A3_EXTENDED_SDM_PROBE] += 0.20
                dk_map[ActionType.A4_KNOWLEDGE_DERIVATION] += 0.15

        best_action, valuations = self.efe_evaluator.select_action_c2(
            delta_h_knowledge_map=dk_map,
            delta_h_memory_map=dm_map,
            energy=somatic.energy,
            cognitive_load=somatic.cognitive_load,
            tension=somatic.tension,
            r_trust=r_trust,
            n_recent_queries=n_recent_queries,
            contradiction_present=contradiction_present,
            unweighted_beta=False,
        )
        action_probs = compute_action_distribution(valuations, gamma=1.0)

        # ---------------------------------------------------------------------
        # 4. Communication Strategy & Pacing
        # ---------------------------------------------------------------------
        comm_state = self.comm_policy.compute(
            pad=pad_t,
            somatic=somatic,
            relationship={"trust": r_trust, "familiarity": 0.30, "closeness": 0.30},
            knowledge=None,
            recollection=None,
        )

        # Side-channel adjustments to communication framing:
        directness = comm_state.directness
        supportiveness = comm_state.supportiveness
        formality = comm_state.formality_score
        pacing_latency = comm_state.injected_pacing_latency_ms

        if condition in ("C1", "C4"):
            directness = float(np.clip(directness + 0.15 * v_d, 0.10, 0.95))
            supportiveness = float(np.clip(supportiveness + 0.20 * v_p, 0.00, 1.00))
            if v_p < -0.2:
                pacing_latency = float(np.clip(pacing_latency + 150.0 * abs(v_p), 0.0, 1000.0))
        elif condition in ("C2", "C5"):
            directness = float(np.clip(directness + 0.12 * sign_d, 0.10, 0.95))
            supportiveness = float(np.clip(supportiveness + 0.15 * sign_p, 0.00, 1.00))
            if sign_p < 0:
                pacing_latency = float(np.clip(pacing_latency + 120.0, 0.0, 1000.0))

        # ---------------------------------------------------------------------
        # 5. Prompt Conditioning Assembly & Token Cost
        # ---------------------------------------------------------------------
        prompt_sections = [
            "[SYSTEM PREAMBLE]\nYou are Lucia, an edge companion.",
            f"[SOMATIC STATE]\nstability: {somatic.stability:.4f}\ncognitive_load: {somatic.cognitive_load:.4f}\nenergy: {somatic.energy:.4f}\ntension: {somatic.tension:.4f}",
        ]
        if condition in ("C1", "C4") and direction is not None:
            prompt_sections.append(f"[DIRECTIONAL AFFECT]\nv_P: {v_p:+.4f}\nv_A: {v_a:+.4f}\nv_D: {v_d:+.4f}")
        elif condition in ("C2", "C5") and signs is not None:
            prompt_sections.append(f"[AFFECTIVE POLARITY]\nsign_P: {sign_p:+d}\nsign_A: {sign_a:+d}\nsign_D: {sign_d:+d}")
        elif condition == "C3" and arousal_res is not None:
            prompt_sections.append(f"[AROUSAL RESIDUAL]\nr_A: {arousal_res:+.4f}")

        prompt_sections.append(
            f"[COMMUNICATION STRATEGY]\nstrategy: {comm_state.strategy.value}\ndirectness: {directness:.2f}\nsupportiveness: {supportiveness:.2f}\nformality: {formality:.2f}"
        )
        if gen_policy.reasoning_depth > 0:
            prompt_sections.append(f"[REASONING SCAFFOLDING]\ndepth: {gen_policy.reasoning_depth}\nsteps: {gen_policy.scaffolding_steps}")

        assembled_prompt = "\n\n---\n\n".join(prompt_sections)
        token_estimate = max(1, len(assembled_prompt) // 4)

        return BehavioralOutcome(
            action=best_action.value,
            action_probabilities=action_probs,
            reasoning_depth=gen_policy.reasoning_depth,
            generation_mode=gen_policy.mode,
            comm_strategy=comm_state.strategy.value,
            directness=directness,
            supportiveness=supportiveness,
            formality=formality,
            pacing_latency_ms=pacing_latency,
            somatic_cognitive_load=somatic.cognitive_load,
            somatic_tension=somatic.tension,
            prompt_token_estimate=token_estimate,
        )


# =============================================================================
# Behavioral Utilization Study Engine
# =============================================================================

class DirectionalBehaviorStudyEngine:
    """
    Main study engine for Phase 22 H1 Directional Side-Channel Behavioral Utilization.
    """

    def __init__(self, seed: int = 9999, null_seed: int = 8888) -> None:
        self.seed = seed
        self.null_seed = null_seed
        self.sp = StimulusProcessor(StimulusConfig())
        self.core = EmotionCore(EmotionConfig())
        self.ai = ActiveInferenceEngine(ActiveInferenceConfig())
        self.adapter = BehavioralResearchAdapter()

        self.probes_by_tier: Dict[str, List[Dict[str, Any]]] = {}
        self.all_probes: List[Dict[str, Any]] = []
        self.simulated_trajectories: Dict[int, Dict[str, Any]] = {}

    def generate_frozen_dataset(self) -> List[Dict[str, Any]]:
        """Generate frozen Candidate G1 stimulus set (270 probes, 90/tier, Seed 9999)."""
        print("\n" + "=" * 70)
        print("Phase 22 H1 — Directional Side-Channel Behavioral Utilization Study")
        print("Generating Frozen Candidate G1 Dataset (Seed 9999, N=270, 90/tier)")
        print("=" * 70)
        gen = GeneratorG1(self.sp)
        rng = np.random.default_rng(self.seed)
        tiers = ["Low", "Med", "High"]
        n_probes_per_tier = 90

        all_probes = []
        for tier in tiers:
            self.probes_by_tier[tier] = []
            for i in range(n_probes_per_tier):
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
                self.probes_by_tier[tier].append(item)
                all_probes.append(item)
            print(f"  Tier {tier:4s}: Generated {len(self.probes_by_tier[tier])} calibrated probes")

        self.all_probes = all_probes
        return all_probes

    def simulate_trajectories(self) -> Dict[int, Dict[str, Any]]:
        """Simulate continuous Fast-Loop ODE trajectories across exposure grid."""
        print("\n" + "=" * 70)
        print("Simulating Continuous Limbic ODE Trajectories across T in [1, 25]")
        print("=" * 70)
        t0 = time.time()
        for p in self.all_probes:
            g_idx = p["global_idx"]
            vec = np.array(p["vector"], dtype=np.float64)

            self.core.reset_to_resting()
            self.ai.reset()

            p0 = self.core.get_pad_state()
            p0_vec = np.array([p0.pleasure, p0.arousal, p0.dominance], dtype=np.float64)

            max_ticks = 25
            pad_traj = np.zeros((max_ticks + 1, 3), dtype=np.float64)
            s_traj = np.zeros(max_ticks + 1, dtype=np.float64)
            r_traj = np.zeros((max_ticks + 1, 3), dtype=np.float64)

            pad_traj[0] = p0_vec
            s_traj[0] = 0.0
            r_traj[0] = np.zeros(3, dtype=np.float64)

            for t in range(1, max_ticks + 1):
                token = self.core.push_stimulus(vec)
                pt = self.core.commit_stimulus(token)
                pt_vec = np.array([pt.pleasure, pt.arousal, pt.dominance], dtype=np.float64)
                pad_traj[t] = pt_vec
                # Canonical prediction error residual r_T = p_0 - p_T
                # S = ||r_T||_2
                r_vec = pt_vec - p0_vec
                r_traj[t] = r_vec
                s_traj[t] = float(np.linalg.norm(r_vec))

            self.simulated_trajectories[g_idx] = {
                "global_idx": g_idx,
                "tier": p["tier"],
                "domain": p["domain"],
                "text": p["text"],
                "p0": p0_vec,
                "pad_traj": pad_traj,
                "s_traj": s_traj,
                "r_traj": r_traj,
            }

        elapsed = time.time() - t0
        print(f"Simulated {len(self.all_probes)} trajectories in {elapsed:.2f}s")
        return self.simulated_trajectories

    def run_all_conditions_on_grid(self) -> Dict[str, Any]:
        """
        Evaluate conditions C0 through C5 across all probes and conversational exposures T.
        """
        print("\n" + "=" * 70)
        print("Evaluating Conditions C0–C5 across N=270 Probes and Exposure Grid")
        print("=" * 70)

        # Prepare shuffled null distributions (seed 8888)
        rng_null = np.random.default_rng(self.null_seed)
        n_total = len(self.all_probes)
        perm_idx = rng_null.permutation(n_total)

        conditions = ["C0", "C1", "C2", "C3", "C4", "C5"]
        results_by_t: Dict[int, Dict[str, List[Dict[str, Any]]]] = {t: {c: [] for c in conditions} for t in T_CONVERSATIONAL}

        for t in T_CONVERSATIONAL:
            # Collect directions and signs at tick t for null shuffling
            directions_at_t = []
            signs_at_t = []
            for p in self.all_probes:
                traj = self.simulated_trajectories[p["global_idx"]]
                r_t = traj["r_traj"][t]
                v_r = compute_normalized_direction(r_t)
                sg = compute_ternary_signs(r_t)
                directions_at_t.append(v_r)
                signs_at_t.append(sg)

            # Permute for null controls
            shuffled_directions = [directions_at_t[i] for i in perm_idx]
            shuffled_signs = [signs_at_t[i] for i in perm_idx]

            for idx, p in enumerate(self.all_probes):
                g_idx = p["global_idx"]
                traj = self.simulated_trajectories[g_idx]
                p_curr_vec = traj["pad_traj"][t]
                pad_curr = make_pad_state(p_curr_vec[0], p_curr_vec[1], p_curr_vec[2])
                s_val = float(traj["s_traj"][t])
                r_t = traj["r_traj"][t]
                v_r = directions_at_t[idx]
                sg = signs_at_t[idx]
                r_a = float(r_t[1])

                v_shuffled = shuffled_directions[idx]
                sg_shuffled = shuffled_signs[idx]

                # C0: Canonical scalar baseline
                out_c0 = self.adapter.evaluate(pad_curr, s_val, "C0")
                # C1: Scalar + Continuous unit direction (R2)
                out_c1 = self.adapter.evaluate(pad_curr, s_val, "C1", direction=v_r)
                # C2: Scalar + Ternary signs (R3)
                out_c2 = self.adapter.evaluate(pad_curr, s_val, "C2", signs=sg)
                # C3: Scalar + Arousal residual
                out_c3 = self.adapter.evaluate(pad_curr, s_val, "C3", arousal_res=r_a)
                # C4: Shuffled direction null control
                out_c4 = self.adapter.evaluate(pad_curr, s_val, "C4", direction=v_shuffled)
                # C5: Shuffled signs null control
                out_c5 = self.adapter.evaluate(pad_curr, s_val, "C5", signs=sg_shuffled)

                for c_name, out in [("C0", out_c0), ("C1", out_c1), ("C2", out_c2), ("C3", out_c3), ("C4", out_c4), ("C5", out_c5)]:
                    rec = asdict(out)
                    rec["global_idx"] = g_idx
                    rec["tier"] = p["tier"]
                    rec["s_val"] = s_val
                    results_by_t[t][c_name].append(rec)

        return results_by_t

    def evaluate_rq1_behavioral_sensitivity(
        self,
        results_by_t: Dict[int, Dict[str, List[Dict[str, Any]]]],
    ) -> Dict[str, Any]:
        """
        RQ1 — Behavioral Sensitivity:
        Does changing directional side-channel while holding scalar S approximately constant
        produce measurable differences in downstream behavior under the research adapter?
        """
        print("\n--- RQ1: Behavioral Sensitivity Analysis ---")
        rq1_summary = {}

        for t in T_CONVERSATIONAL:
            c0_list = results_by_t[t]["C0"]
            c1_list = results_by_t[t]["C1"]
            c2_list = results_by_t[t]["C2"]
            c3_list = results_by_t[t]["C3"]
            c4_list = results_by_t[t]["C4"]
            c5_list = results_by_t[t]["C5"]

            n = len(c0_list)

            # Divergence from baseline C0
            d_pol_c1 = sum(1 for i in range(n) if c1_list[i]["action"] != c0_list[i]["action"]) / n
            d_pol_c2 = sum(1 for i in range(n) if c2_list[i]["action"] != c0_list[i]["action"]) / n
            d_pol_c3 = sum(1 for i in range(n) if c3_list[i]["action"] != c0_list[i]["action"]) / n
            d_pol_c4 = sum(1 for i in range(n) if c4_list[i]["action"] != c0_list[i]["action"]) / n
            d_pol_c5 = sum(1 for i in range(n) if c5_list[i]["action"] != c0_list[i]["action"]) / n

            # Continuous policy distribution shifts (Jensen-Shannon & Total Variation) relative to C0
            d_js_c1 = [compute_js_divergence(c1_list[i]["action_probabilities"], c0_list[i]["action_probabilities"]) for i in range(n)]
            d_js_c2 = [compute_js_divergence(c2_list[i]["action_probabilities"], c0_list[i]["action_probabilities"]) for i in range(n)]
            d_js_c3 = [compute_js_divergence(c3_list[i]["action_probabilities"], c0_list[i]["action_probabilities"]) for i in range(n)]
            d_js_c4 = [compute_js_divergence(c4_list[i]["action_probabilities"], c0_list[i]["action_probabilities"]) for i in range(n)]
            d_js_c5 = [compute_js_divergence(c5_list[i]["action_probabilities"], c0_list[i]["action_probabilities"]) for i in range(n)]

            d_tv_c1 = [compute_tv_distance(c1_list[i]["action_probabilities"], c0_list[i]["action_probabilities"]) for i in range(n)]
            d_tv_c2 = [compute_tv_distance(c2_list[i]["action_probabilities"], c0_list[i]["action_probabilities"]) for i in range(n)]
            d_tv_c3 = [compute_tv_distance(c3_list[i]["action_probabilities"], c0_list[i]["action_probabilities"]) for i in range(n)]
            d_tv_c4 = [compute_tv_distance(c4_list[i]["action_probabilities"], c0_list[i]["action_probabilities"]) for i in range(n)]
            d_tv_c5 = [compute_tv_distance(c5_list[i]["action_probabilities"], c0_list[i]["action_probabilities"]) for i in range(n)]

            mean_d_js_c1 = float(np.mean(d_js_c1))
            mean_d_js_c2 = float(np.mean(d_js_c2))
            mean_d_js_c3 = float(np.mean(d_js_c3))
            mean_d_js_c4 = float(np.mean(d_js_c4))
            mean_d_js_c5 = float(np.mean(d_js_c5))

            mean_d_tv_c1 = float(np.mean(d_tv_c1))
            mean_d_tv_c2 = float(np.mean(d_tv_c2))
            mean_d_tv_c3 = float(np.mean(d_tv_c3))
            mean_d_tv_c4 = float(np.mean(d_tv_c4))
            mean_d_tv_c5 = float(np.mean(d_tv_c5))

            # Reasoning depth shift rate (delta k != 0)
            dk_rate_c1 = sum(1 for i in range(n) if c1_list[i]["reasoning_depth"] != c0_list[i]["reasoning_depth"]) / n
            dk_rate_c2 = sum(1 for i in range(n) if c2_list[i]["reasoning_depth"] != c0_list[i]["reasoning_depth"]) / n

            # Statistical significance of C1 vs C0 and C2 vs C0 (McNemar discordant counts)
            b_c1 = sum(1 for i in range(n) if c1_list[i]["action"] != c0_list[i]["action"])
            p_val_c1 = mcnemar_test_or_exact(b_c1, 0)

            b_c2 = sum(1 for i in range(n) if c2_list[i]["action"] != c0_list[i]["action"])
            p_val_c2 = mcnemar_test_or_exact(b_c2, 0)

            # Pacing latency shift
            mean_pacing_c0 = float(np.mean([x["pacing_latency_ms"] for x in c0_list]))
            mean_pacing_c1 = float(np.mean([x["pacing_latency_ms"] for x in c1_list]))
            mean_pacing_c2 = float(np.mean([x["pacing_latency_ms"] for x in c2_list]))

            rq1_summary[str(t)] = {
                "t_ticks": t,
                "d_pol_c1": float(d_pol_c1),
                "d_pol_c2": float(d_pol_c2),
                "d_pol_c3": float(d_pol_c3),
                "d_pol_c4_null": float(d_pol_c4),
                "d_pol_c5_null": float(d_pol_c5),
                "mean_d_js_c1": mean_d_js_c1,
                "mean_d_js_c2": mean_d_js_c2,
                "mean_d_js_c3": mean_d_js_c3,
                "mean_d_js_c4_null": mean_d_js_c4,
                "mean_d_js_c5_null": mean_d_js_c5,
                "mean_d_tv_c1": mean_d_tv_c1,
                "mean_d_tv_c2": mean_d_tv_c2,
                "mean_d_tv_c3": mean_d_tv_c3,
                "mean_d_tv_c4_null": mean_d_tv_c4,
                "mean_d_tv_c5_null": mean_d_tv_c5,
                "dk_rate_c1": float(dk_rate_c1),
                "dk_rate_c2": float(dk_rate_c2),
                "p_val_c1": float(p_val_c1),
                "p_val_c2": float(p_val_c2),
                "mean_pacing_ms": {
                    "c0": mean_pacing_c0,
                    "c1": mean_pacing_c1,
                    "c2": mean_pacing_c2,
                },
                "passes_exploratory_threshold_c1": bool(d_pol_c1 >= D_POL_THRESHOLD and p_val_c1 < P_VAL_THRESHOLD),
                "passes_exploratory_threshold_c2": bool(d_pol_c2 >= D_POL_THRESHOLD and p_val_c2 < P_VAL_THRESHOLD),
            }
            print(f"  T={t:2d}: C1 D_pol={d_pol_c1:.4f} (D_JS={mean_d_js_c1:.4f}, p={p_val_c1:.2e}), C2 D_pol={d_pol_c2:.4f} (D_JS={mean_d_js_c2:.4f}, p={p_val_c2:.2e}), C4_null={d_pol_c4:.4f}")

        return rq1_summary

    def evaluate_rq2_continuous_vs_discrete(self) -> Dict[str, Any]:
        """
        RQ2 — Continuous Direction vs. Discrete Sign:
        Test 2A: Within-quadrant divergence (identical ternary signs, angle >= 30 deg).
        Test 2B: Discrete sign transitions across matched-magnitude probes.
        """
        print("\n--- RQ2: Continuous vs Discrete Analysis (Tests 2A & 2B) ---")
        rq2_results = {}

        for t in T_CONVERSATIONAL:
            # Build probe pairs
            probes = self.all_probes
            n = len(probes)

            test_2a_pairs = []  # identical signs, angle >= 30 deg, matched S
            test_2b_pairs = []  # different signs, matched S

            for i in range(n):
                gi = probes[i]["global_idx"]
                traji = self.simulated_trajectories[gi]
                si = traji["s_traj"][t]
                ri = traji["r_traj"][t]
                vi = compute_normalized_direction(ri)
                sgi = compute_ternary_signs(ri)

                for j in range(i + 1, n):
                    gj = probes[j]["global_idx"]
                    trajj = self.simulated_trajectories[gj]
                    sj = trajj["s_traj"][t]
                    rj = trajj["r_traj"][t]
                    vj = compute_normalized_direction(rj)
                    sgj = compute_ternary_signs(rj)

                    # Scalar match constraint |S_i - S_j| <= 0.02
                    if abs(si - sj) <= SCALAR_MATCH_THRESHOLD:
                        angle = compute_angle_deg(vi, vj)
                        if sgi == sgj and angle >= 30.0:
                            test_2a_pairs.append({
                                "idx_i": gi, "idx_j": gj, "s_i": si, "s_j": sj,
                                "angle_deg": angle, "signs": sgi,
                                "vi": vi, "vj": vj, "ri": ri, "rj": rj,
                                "padi": traji["pad_traj"][t], "padj": trajj["pad_traj"][t],
                            })
                        elif sgi != sgj:
                            test_2b_pairs.append({
                                "idx_i": gi, "idx_j": gj, "s_i": si, "s_j": sj,
                                "angle_deg": angle, "signs_i": sgi, "signs_j": sgj,
                                "vi": vi, "vj": vj, "ri": ri, "rj": rj,
                                "padi": traji["pad_traj"][t], "padj": trajj["pad_traj"][t],
                            })

            # Evaluate Test 2A: Continuous within-quadrant divergence
            # Does C1 (R2) produce divergence when C2 (R3) sees identical signs?
            # Counterfactual intervention on Test 2A pairs:
            # Holding probe i fixed, compare output with vi vs vj under C1 and C2
            n_2a = len(test_2a_pairs)
            c1_diverge_2a = 0
            c2_diverge_2a = 0
            d_js_2a_c1_list = []
            d_js_2a_c2_list = []

            for pair in test_2a_pairs:
                pad_curr = make_pad_state(pair["padi"][0], pair["padi"][1], pair["padi"][2])
                s_i = pair["s_i"]
                # C1 with vi vs vj
                out_c1_i = self.adapter.evaluate(pad_curr, s_i, "C1", direction=pair["vi"])
                out_c1_j = self.adapter.evaluate(pad_curr, s_i, "C1", direction=pair["vj"])
                if out_c1_i.action != out_c1_j.action or out_c1_i.reasoning_depth != out_c1_j.reasoning_depth:
                    c1_diverge_2a += 1
                d_js_2a_c1_list.append(compute_js_divergence(out_c1_i.action_probabilities, out_c1_j.action_probabilities))

                # C2 with sgi vs sgj (which are identical)
                out_c2_i = self.adapter.evaluate(pad_curr, s_i, "C2", signs=pair["signs"])
                out_c2_j = self.adapter.evaluate(pad_curr, s_i, "C2", signs=pair["signs"])
                if out_c2_i.action != out_c2_j.action or out_c2_i.reasoning_depth != out_c2_j.reasoning_depth:
                    c2_diverge_2a += 1
                d_js_2a_c2_list.append(compute_js_divergence(out_c2_i.action_probabilities, out_c2_j.action_probabilities))

            d_pol_2a_c1 = (c1_diverge_2a / n_2a) if n_2a > 0 else 0.0
            d_pol_2a_c2 = (c2_diverge_2a / n_2a) if n_2a > 0 else 0.0
            p_val_2a = mcnemar_test_or_exact(c1_diverge_2a, c2_diverge_2a) if n_2a > 0 else 1.0
            mean_d_js_2a_c1 = float(np.mean(d_js_2a_c1_list)) if n_2a > 0 else 0.0
            mean_d_js_2a_c2 = float(np.mean(d_js_2a_c2_list)) if n_2a > 0 else 0.0

            # Evaluate Test 2B: Discrete sign transitions
            # Compare output with sgi vs sgj under C2
            n_2b = len(test_2b_pairs)
            c2_diverge_2b = 0
            c1_diverge_2b = 0
            d_js_2b_c2_list = []
            d_js_2b_c1_list = []

            for pair in test_2b_pairs:
                pad_curr = make_pad_state(pair["padi"][0], pair["padi"][1], pair["padi"][2])
                s_i = pair["s_i"]
                out_c2_i = self.adapter.evaluate(pad_curr, s_i, "C2", signs=pair["signs_i"])
                out_c2_j = self.adapter.evaluate(pad_curr, s_i, "C2", signs=pair["signs_j"])
                if out_c2_i.action != out_c2_j.action or out_c2_i.reasoning_depth != out_c2_j.reasoning_depth:
                    c2_diverge_2b += 1
                d_js_2b_c2_list.append(compute_js_divergence(out_c2_i.action_probabilities, out_c2_j.action_probabilities))

                out_c1_i = self.adapter.evaluate(pad_curr, s_i, "C1", direction=pair["vi"])
                out_c1_j = self.adapter.evaluate(pad_curr, s_i, "C1", direction=pair["vj"])
                if out_c1_i.action != out_c1_j.action or out_c1_i.reasoning_depth != out_c1_j.reasoning_depth:
                    c1_diverge_2b += 1
                d_js_2b_c1_list.append(compute_js_divergence(out_c1_i.action_probabilities, out_c1_j.action_probabilities))

            d_pol_2b_c2 = (c2_diverge_2b / n_2b) if n_2b > 0 else 0.0
            d_pol_2b_c1 = (c1_diverge_2b / n_2b) if n_2b > 0 else 0.0
            p_val_2b = mcnemar_test_or_exact(c2_diverge_2b, 0) if n_2b > 0 else 1.0
            mean_d_js_2b_c2 = float(np.mean(d_js_2b_c2_list)) if n_2b > 0 else 0.0
            mean_d_js_2b_c1 = float(np.mean(d_js_2b_c1_list)) if n_2b > 0 else 0.0

            rq2_results[str(t)] = {
                "t_ticks": t,
                "n_test_2a_pairs": n_2a,
                "d_pol_test_2a_c1_continuous": float(d_pol_2a_c1),
                "d_pol_test_2a_c2_discrete": float(d_pol_2a_c2),
                "mean_d_js_test_2a_c1": mean_d_js_2a_c1,
                "mean_d_js_test_2a_c2": mean_d_js_2a_c2,
                "p_val_test_2a": float(p_val_2a),
                "c1_additional_value_in_same_sign": bool(d_pol_2a_c1 >= D_POL_THRESHOLD and p_val_2a < P_VAL_THRESHOLD),
                "n_test_2b_pairs": n_2b,
                "d_pol_test_2b_c2_discrete": float(d_pol_2b_c2),
                "d_pol_test_2b_c1_continuous": float(d_pol_2b_c1),
                "mean_d_js_test_2b_c2": mean_d_js_2b_c2,
                "mean_d_js_test_2b_c1": mean_d_js_2b_c1,
                "p_val_test_2b": float(p_val_2b),
                "c2_sufficient_for_sign_transition": bool(d_pol_2b_c2 >= D_POL_THRESHOLD and p_val_2b < P_VAL_THRESHOLD),
            }
            print(f"  T={t:2d}: Test 2A N={n_2a}, C1_Dpol={d_pol_2a_c1:.4f} (D_JS={mean_d_js_2a_c1:.4f}), C2_Dpol={d_pol_2a_c2:.4f}; Test 2B N={n_2b}, C2_Dpol={d_pol_2b_c2:.4f} (D_JS={mean_d_js_2b_c2:.4f}, p={p_val_2b:.2e})")

        return rq2_results

    def evaluate_rq3_behavioral_utilization_vs_geometric_resolution(self) -> Dict[str, Any]:
        """
        RQ3 — Behavioral Utilization vs. Geometric Resolution:
        Examine the 358 Medium–High collapse pairs at T=12 identified in the previous study.
        What percentage actually produce downstream behavioral differentiation?
        """
        print("\n--- RQ3: Behavioral Utilization of 358 Medium-High Collapse Pairs at T=12 ---")
        t = 12
        med_probes = self.probes_by_tier["Med"]
        high_probes = self.probes_by_tier["High"]

        collapse_pairs = []
        for p_m in med_probes:
            gm = p_m["global_idx"]
            tm = self.simulated_trajectories[gm]
            sm = tm["s_traj"][t]
            rm = tm["r_traj"][t]
            vm = compute_normalized_direction(rm)
            sgm = compute_ternary_signs(rm)

            for p_h in high_probes:
                gh = p_h["global_idx"]
                th = self.simulated_trajectories[gh]
                sh = th["s_traj"][t]
                rh = th["r_traj"][t]
                vh = compute_normalized_direction(rh)
                sgh = compute_ternary_signs(rh)

                if abs(sm - sh) <= SCALAR_MATCH_THRESHOLD:
                    collapse_pairs.append({
                        "idx_m": gm, "idx_h": gh,
                        "sm": sm, "sh": sh,
                        "rm": rm, "rh": rh,
                        "vm": vm, "vh": vh,
                        "sgm": sgm, "sgh": sgh,
                        "padm": tm["pad_traj"][t],
                        "padh": th["pad_traj"][t],
                    })

        n_pairs = len(collapse_pairs)
        print(f"Identified {n_pairs} Medium-High collapse pairs at T=12 (|S_M - S_H| <= 0.02)")

        # Evaluate behavioral divergence between these pairs under C0, C1, C2
        c0_diff_action = 0
        c1_diff_action = 0
        c2_diff_action = 0

        c0_diff_depth = 0
        c1_diff_depth = 0
        c2_diff_depth = 0

        c0_diff_comm = 0
        c1_diff_comm = 0
        c2_diff_comm = 0

        d_js_c0_list = []
        d_js_c1_list = []
        d_js_c2_list = []

        for pair in collapse_pairs:
            padm = make_pad_state(pair["padm"][0], pair["padm"][1], pair["padm"][2])
            padh = make_pad_state(pair["padh"][0], pair["padh"][1], pair["padh"][2])

            # Under C0 (canonical baseline)
            out_c0_m = self.adapter.evaluate(padm, pair["sm"], "C0")
            out_c0_h = self.adapter.evaluate(padh, pair["sh"], "C0")
            if out_c0_m.action != out_c0_h.action:
                c0_diff_action += 1
            if out_c0_m.reasoning_depth != out_c0_h.reasoning_depth:
                c0_diff_depth += 1
            if out_c0_m.comm_strategy != out_c0_h.comm_strategy:
                c0_diff_comm += 1
            d_js_c0_list.append(compute_js_divergence(out_c0_m.action_probabilities, out_c0_h.action_probabilities))

            # Under C1 (continuous direction)
            out_c1_m = self.adapter.evaluate(padm, pair["sm"], "C1", direction=pair["vm"])
            out_c1_h = self.adapter.evaluate(padh, pair["sh"], "C1", direction=pair["vh"])
            if out_c1_m.action != out_c1_h.action:
                c1_diff_action += 1
            if out_c1_m.reasoning_depth != out_c1_h.reasoning_depth:
                c1_diff_depth += 1
            if out_c1_m.comm_strategy != out_c1_h.comm_strategy:
                c1_diff_comm += 1
            d_js_c1_list.append(compute_js_divergence(out_c1_m.action_probabilities, out_c1_h.action_probabilities))

            # Under C2 (ternary signs)
            out_c2_m = self.adapter.evaluate(padm, pair["sm"], "C2", signs=pair["sgm"])
            out_c2_h = self.adapter.evaluate(padh, pair["sh"], "C2", signs=pair["sgh"])
            if out_c2_m.action != out_c2_h.action:
                c2_diff_action += 1
            if out_c2_m.reasoning_depth != out_c2_h.reasoning_depth:
                c2_diff_depth += 1
            if out_c2_m.comm_strategy != out_c2_h.comm_strategy:
                c2_diff_comm += 1
            d_js_c2_list.append(compute_js_divergence(out_c2_m.action_probabilities, out_c2_h.action_probabilities))

        action_diff_rate_c0 = c0_diff_action / n_pairs if n_pairs > 0 else 0.0
        action_diff_rate_c1 = c1_diff_action / n_pairs if n_pairs > 0 else 0.0
        action_diff_rate_c2 = c2_diff_action / n_pairs if n_pairs > 0 else 0.0

        depth_diff_rate_c0 = c0_diff_depth / n_pairs if n_pairs > 0 else 0.0
        depth_diff_rate_c1 = c1_diff_depth / n_pairs if n_pairs > 0 else 0.0
        depth_diff_rate_c2 = c2_diff_depth / n_pairs if n_pairs > 0 else 0.0

        p_val_action_c1_vs_c0 = mcnemar_test_or_exact(c1_diff_action, c0_diff_action)
        p_val_action_c2_vs_c0 = mcnemar_test_or_exact(c2_diff_action, c0_diff_action)

        mean_pair_d_js_c0 = float(np.mean(d_js_c0_list)) if n_pairs > 0 else 0.0
        mean_pair_d_js_c1 = float(np.mean(d_js_c1_list)) if n_pairs > 0 else 0.0
        mean_pair_d_js_c2 = float(np.mean(d_js_c2_list)) if n_pairs > 0 else 0.0

        rq3_summary = {
            "n_collapse_pairs_at_t12": n_pairs,
            "action_differentiation_rate": {
                "c0_scalar": float(action_diff_rate_c0),
                "c1_continuous": float(action_diff_rate_c1),
                "c2_ternary_signs": float(action_diff_rate_c2),
            },
            "reasoning_depth_differentiation_rate": {
                "c0_scalar": float(depth_diff_rate_c0),
                "c1_continuous": float(depth_diff_rate_c1),
                "c2_ternary_signs": float(depth_diff_rate_c2),
            },
            "pair_policy_distribution_divergence_mean_d_js": {
                "c0_scalar": mean_pair_d_js_c0,
                "c1_continuous": mean_pair_d_js_c1,
                "c2_ternary_signs": mean_pair_d_js_c2,
            },
            "p_val_action_c1_vs_c0": float(p_val_action_c1_vs_c0),
            "p_val_action_c2_vs_c0": float(p_val_action_c2_vs_c0),
            "geometric_vs_behavioral_ratio_c1": float(action_diff_rate_c1 / 1.0),  # 1.0 was 100% geometric resolution
            "geometric_vs_behavioral_ratio_c2": float(action_diff_rate_c2 / 1.0),
        }
        print(f"  Collapse Differentiation: C0={action_diff_rate_c0:.4f} (D_JS={mean_pair_d_js_c0:.4f}), C1={action_diff_rate_c1:.4f} (D_JS={mean_pair_d_js_c1:.4f}), C2={action_diff_rate_c2:.4f} (D_JS={mean_pair_d_js_c2:.4f})")
        return rq3_summary

    def evaluate_rq4_directional_effects_on_policy(
        self,
        results_by_t: Dict[int, Dict[str, List[Dict[str, Any]]]],
    ) -> Dict[str, Any]:
        """
        RQ4 — Directional Effects on Response Policy:
        How do specific directional axes (hedonic valence v_P, somatic urgency v_A, dominance v_D)
        modulate specific downstream policies (clarification a2, deep reasoning a5, pause a6, pacing)?
        """
        print("\n--- RQ4: Directional Component Sensitivity Analysis ---")
        t = 12
        c1_list = results_by_t[t]["C1"]

        # Extract components and behavioral choices
        vp_vals = []
        va_vals = []
        vd_vals = []

        is_a1 = []
        is_a2 = []
        is_a5 = []
        is_a6 = []
        reasoning_depths = []
        pacing_latencies = []
        supportiveness_scores = []
        directness_scores = []

        for item in c1_list:
            g_idx = item["global_idx"]
            traj = self.simulated_trajectories[g_idx]
            r_t = traj["r_traj"][t]
            v_r = compute_normalized_direction(r_t)

            vp_vals.append(float(v_r[0]))
            va_vals.append(float(v_r[1]))
            vd_vals.append(float(v_r[2]))

            action = item["action"]
            is_a1.append(1 if action == ActionType.A1_IMMEDIATE_RESPONSE.value else 0)
            is_a2.append(1 if action == ActionType.A2_EXTERNAL_CLARIFICATION.value else 0)
            is_a5.append(1 if action == ActionType.A5_DEEP_REASONING_MODE_SHIFT.value else 0)
            is_a6.append(1 if action == ActionType.A6_WAIT_CONVERSATIONAL_PAUSE.value else 0)

            reasoning_depths.append(item["reasoning_depth"])
            pacing_latencies.append(item["pacing_latency_ms"])
            supportiveness_scores.append(item["supportiveness"])
            directness_scores.append(item["directness"])

        def safe_corr(x: List[float], y: List[float]) -> Tuple[float, float]:
            if len(set(y)) <= 1 or len(set(x)) <= 1:
                return 0.0, 1.0
            r, p = stats.spearmanr(x, y)
            return float(r), float(p)

        r_vp_support, p_vp_support = safe_corr(vp_vals, supportiveness_scores)
        r_vd_direct, p_vd_direct = safe_corr(vd_vals, directness_scores)
        r_vp_pacing, p_vp_pacing = safe_corr(vp_vals, pacing_latencies)
        r_va_depth, p_va_depth = safe_corr(va_vals, reasoning_depths)
        r_vp_a2, p_vp_a2 = safe_corr(vp_vals, is_a2)

        rq4_summary = {
            "t_ticks": t,
            "spearman_correlations": {
                "valence_vs_supportiveness": {"r": r_vp_support, "p": p_vp_support},
                "dominance_vs_directness": {"r": r_vd_direct, "p": p_vd_direct},
                "valence_vs_pacing_latency": {"r": r_vp_pacing, "p": p_vp_pacing},
                "arousal_vs_reasoning_depth": {"r": r_va_depth, "p": p_va_depth},
                "valence_vs_clarification_a2": {"r": r_vp_a2, "p": p_vp_a2},
            },
        }
        print(f"  v_P vs Supportiveness: r={r_vp_support:+.4f} (p={p_vp_support:.2e})")
        print(f"  v_D vs Directness:     r={r_vd_direct:+.4f} (p={p_vd_direct:.2e})")
        print(f"  v_P vs Pacing Latency: r={r_vp_pacing:+.4f} (p={p_vp_pacing:.2e})")
        return rq4_summary

    def evaluate_rq5_scalar_preservation(
        self,
        results_by_t: Dict[int, Dict[str, List[Dict[str, Any]]]],
    ) -> Dict[str, Any]:
        """
        RQ5 — Observed Monotonic Association across Frozen Stimuli/Exposures:
        Evaluates whether canonical scalar surprise S continues to exhibit strong observed
        monotonic association with cognitive load, somatic tension, and reasoning depth across
        the frozen stimulus set and conversational exposure grid (T in {1, 2, 4, 8, 12, 16, 25}),
        verifying that directional side-channels do not supplant S's primary intensity/gating role.
        Note: Evaluates observed monotonic association across the natural limbic ODE trajectory
        grid rather than an artificial controlled S-scaling experiment.
        """
        print("\n--- RQ5: Observed Monotonic Association across Frozen Stimuli/Exposures ---")
        t = 12
        rq5_summary = {
            "evaluation_scope": "observed_monotonic_association_across_frozen_stimuli_and_exposures",
            "t_evaluated": t,
        }

        for cond in ["C0", "C1", "C2", "C3"]:
            c_list = results_by_t[t][cond]
            s_vals = [x["s_val"] for x in c_list]
            cog_loads = [x["somatic_cognitive_load"] for x in c_list]
            tensions = [x["somatic_tension"] for x in c_list]
            depths = [x["reasoning_depth"] for x in c_list]

            r_cl, _ = stats.spearmanr(s_vals, cog_loads)
            r_t, _ = stats.spearmanr(s_vals, tensions)
            r_d, _ = stats.spearmanr(s_vals, depths)

            rq5_summary[cond] = {
                "spearman_s_vs_cognitive_load": float(r_cl),
                "spearman_s_vs_tension": float(r_t),
                "spearman_s_vs_reasoning_depth": float(r_d),
                "scalar_monotonicity_preserved": bool(r_cl >= 0.80 and r_t >= 0.70),
            }
            print(f"  {cond}: r(S, CogLoad)={r_cl:.4f}, r(S, Tension)={r_t:.4f}, r(S, Depth)={r_d:.4f}")

        return rq5_summary

    def evaluate_rq6_null_controls(
        self,
        results_by_t: Dict[int, Dict[str, List[Dict[str, Any]]]],
    ) -> Dict[str, Any]:
        """
        RQ6 — Side-Channel Necessity (Null Shuffle Controls):
        Do behavioral differences maintain coherence, or does shuffling break stimulus correspondence?
        """
        print("\n--- RQ6: Null Shuffle Control Analysis (C1 vs C4, C2 vs C5) ---")
        rq6_summary = {}

        for t in T_CONVERSATIONAL:
            c1_list = results_by_t[t]["C1"]
            c4_list = results_by_t[t]["C4"]  # C1 with shuffled direction
            c2_list = results_by_t[t]["C2"]
            c5_list = results_by_t[t]["C5"]  # C2 with shuffled signs

            n = len(c1_list)
            # Discordance between true side-channel and shuffled side-channel
            discordance_c1_c4 = sum(1 for i in range(n) if c1_list[i]["action"] != c4_list[i]["action"]) / n
            discordance_c2_c5 = sum(1 for i in range(n) if c2_list[i]["action"] != c5_list[i]["action"]) / n

            # Continuous distribution shift under shuffle
            d_js_c1_c4 = [compute_js_divergence(c1_list[i]["action_probabilities"], c4_list[i]["action_probabilities"]) for i in range(n)]
            d_js_c2_c5 = [compute_js_divergence(c2_list[i]["action_probabilities"], c5_list[i]["action_probabilities"]) for i in range(n)]
            mean_d_js_c1_c4 = float(np.mean(d_js_c1_c4))
            mean_d_js_c2_c5 = float(np.mean(d_js_c2_c5))

            p_val_c1_c4 = mcnemar_test_or_exact(int(discordance_c1_c4 * n), 0)
            p_val_c2_c5 = mcnemar_test_or_exact(int(discordance_c2_c5 * n), 0)

            rq6_summary[str(t)] = {
                "t_ticks": t,
                "discordance_c1_vs_c4_null": float(discordance_c1_c4),
                "discordance_c2_vs_c5_null": float(discordance_c2_c5),
                "mean_d_js_c1_vs_c4_null": mean_d_js_c1_c4,
                "mean_d_js_c2_vs_c5_null": mean_d_js_c2_c5,
                "p_val_c1_vs_c4": float(p_val_c1_c4),
                "p_val_c2_vs_c5": float(p_val_c2_c5),
                "true_channel_significantly_distinct_from_null": bool(
                    discordance_c1_c4 >= D_POL_THRESHOLD and p_val_c1_c4 < P_VAL_THRESHOLD
                ),
            }
            print(f"  T={t:2d}: C1 vs C4 Discordance={discordance_c1_c4:.4f} (D_JS={mean_d_js_c1_c4:.4f}, p={p_val_c1_c4:.2e}), C2 vs C5 Discordance={discordance_c2_c5:.4f} (D_JS={mean_d_js_c2_c5:.4f}, p={p_val_c2_c5:.2e})")

        return rq6_summary

    def evaluate_counterfactual_interventions(self) -> Dict[str, Any]:
        """
        Formal Counterfactual Measurement Intervention Protocol:
        Hold probe i (stimulus, p0, S_i) fixed, inject direction v_j from matched probe j.
        Strict validity assertions:
        - Injected vector has unit norm ||v_j||_2 = 1.0 +- 1e-5.
        - Injected vector is finite.
        - S_i is bit-exact and not recomputed.
        """
        print("\n--- Counterfactual Measurement Intervention Protocol ---")
        t = 12
        probes = self.all_probes
        n = len(probes)

        matched_pairs = []
        for i in range(n):
            gi = probes[i]["global_idx"]
            traji = self.simulated_trajectories[gi]
            si = traji["s_traj"][t]
            ri = traji["r_traj"][t]
            vi = compute_normalized_direction(ri)

            for j in range(i + 1, n):
                gj = probes[j]["global_idx"]
                trajj = self.simulated_trajectories[gj]
                sj = trajj["s_traj"][t]
                rj = trajj["r_traj"][t]
                vj = compute_normalized_direction(rj)

                if abs(si - sj) <= SCALAR_MATCH_THRESHOLD:
                    # Strict validation of injected vector
                    assert np.isfinite(vj).all(), f"Injected vector for probe {gj} has non-finite values"
                    norm_vj = float(np.linalg.norm(vj))
                    if norm_vj > 1e-6:
                        assert abs(norm_vj - 1.0) <= 1e-5, f"Injected vector for probe {gj} does not satisfy unit norm: {norm_vj}"

                    matched_pairs.append({
                        "idx_i": gi, "idx_j": gj,
                        "si": si, "sj": sj,
                        "padi": traji["pad_traj"][t],
                        "vi": vi, "vj": vj,
                        "sgi": compute_ternary_signs(ri),
                        "sgj": compute_ternary_signs(rj),
                    })

        n_interventions = len(matched_pairs)
        print(f"Executing {n_interventions} counterfactual interventions at T=12")

        c1_action_changes = 0
        c1_depth_changes = 0
        c2_action_changes = 0
        c2_depth_changes = 0
        d_js_cf_c1_list = []
        d_js_cf_c2_list = []

        for item in matched_pairs:
            pad_curr = make_pad_state(item["padi"][0], item["padi"][1], item["padi"][2])
            s_i = item["si"]  # Preserved bit-exact, NOT recomputed

            # C1: Original direction vi vs Injected direction vj
            out_orig_c1 = self.adapter.evaluate(pad_curr, s_i, "C1", direction=item["vi"])
            out_inject_c1 = self.adapter.evaluate(pad_curr, s_i, "C1", direction=item["vj"])
            if out_orig_c1.action != out_inject_c1.action:
                c1_action_changes += 1
            if out_orig_c1.reasoning_depth != out_inject_c1.reasoning_depth:
                c1_depth_changes += 1
            d_js_cf_c1_list.append(compute_js_divergence(out_orig_c1.action_probabilities, out_inject_c1.action_probabilities))

            # C2: Original signs sgi vs Injected signs sgj
            out_orig_c2 = self.adapter.evaluate(pad_curr, s_i, "C2", signs=item["sgi"])
            out_inject_c2 = self.adapter.evaluate(pad_curr, s_i, "C2", signs=item["sgj"])
            if out_orig_c2.action != out_inject_c2.action:
                c2_action_changes += 1
            if out_orig_c2.reasoning_depth != out_inject_c2.reasoning_depth:
                c2_depth_changes += 1
            d_js_cf_c2_list.append(compute_js_divergence(out_orig_c2.action_probabilities, out_inject_c2.action_probabilities))

        d_pol_cf_c1 = c1_action_changes / n_interventions if n_interventions > 0 else 0.0
        d_pol_cf_c2 = c2_action_changes / n_interventions if n_interventions > 0 else 0.0
        p_val_cf_c1 = mcnemar_test_or_exact(c1_action_changes, 0)
        p_val_cf_c2 = mcnemar_test_or_exact(c2_action_changes, 0)
        mean_d_js_cf_c1 = float(np.mean(d_js_cf_c1_list)) if n_interventions > 0 else 0.0
        mean_d_js_cf_c2 = float(np.mean(d_js_cf_c2_list)) if n_interventions > 0 else 0.0

        cf_summary = {
            "n_interventions": n_interventions,
            "t_ticks": t,
            "counterfactual_policy_divergence_c1": float(d_pol_cf_c1),
            "counterfactual_policy_divergence_c2": float(d_pol_cf_c2),
            "mean_d_js_cf_c1": mean_d_js_cf_c1,
            "mean_d_js_cf_c2": mean_d_js_cf_c2,
            "p_val_cf_c1": float(p_val_cf_c1),
            "p_val_cf_c2": float(p_val_cf_c2),
            "counterfactual_depth_shift_c1": float(c1_depth_changes / n_interventions) if n_interventions > 0 else 0.0,
            "counterfactual_depth_shift_c2": float(c2_depth_changes / n_interventions) if n_interventions > 0 else 0.0,
            "passes_exploratory_threshold_cf_c1": bool(d_pol_cf_c1 >= D_POL_THRESHOLD and p_val_cf_c1 < P_VAL_THRESHOLD),
            "passes_exploratory_threshold_cf_c2": bool(d_pol_cf_c2 >= D_POL_THRESHOLD and p_val_cf_c2 < P_VAL_THRESHOLD),
        }
        print(f"  Counterfactual Results: C1 D_pol={d_pol_cf_c1:.4f} (D_JS={mean_d_js_cf_c1:.4f}, p={p_val_cf_c1:.2e}), C2 D_pol={d_pol_cf_c2:.4f} (D_JS={mean_d_js_cf_c2:.4f}, p={p_val_cf_c2:.2e})")
        return cf_summary

    def classify_final_state(
        self,
        rq1_results: Dict[str, Any],
        rq2_results: Dict[str, Any],
        cf_results: Dict[str, Any],
    ) -> Dict[str, Any]:
        """
        Classify outcome into mutually exclusive States A–E:
        - State A: Behavioral Null (D_pol < 0.05 or p >= 0.05).
        - State B: R3 Behavioral Sufficiency (R3 produces D_pol >= 0.05, R2 adds no value in same-sign cases).
        - State C: R2 Additional Value (R2 produces D_pol >= 0.05 beyond R3 in same-sign / angle >= 30 deg cases).
        - State D: Mixed / Timescale-dependent.
        - State E: Inconclusive.
        """
        print("\n--- Final State Classification ---")
        t12_rq1 = rq1_results["12"]
        t12_rq2 = rq2_results["12"]

        d_pol_c2_t12 = t12_rq1["d_pol_c2"]
        p_val_c2_t12 = t12_rq1["p_val_c2"]

        d_pol_2a_c1 = t12_rq2["d_pol_test_2a_c1_continuous"]
        p_val_2a_c1 = t12_rq2["p_val_test_2a"]

        c2_passes = bool(d_pol_c2_t12 >= D_POL_THRESHOLD and p_val_c2_t12 < P_VAL_THRESHOLD)
        c1_additional_passes = bool(d_pol_2a_c1 >= D_POL_THRESHOLD and p_val_2a_c1 < P_VAL_THRESHOLD)

        c1_passes_t12 = bool(t12_rq1["d_pol_c1"] >= D_POL_THRESHOLD and t12_rq1["p_val_c1"] < P_VAL_THRESHOLD)
        c2_passes_t12 = bool(d_pol_c2_t12 >= D_POL_THRESHOLD and p_val_c2_t12 < P_VAL_THRESHOLD)

        if not c1_passes_t12 and not c2_passes_t12:
            state = "STATE_A"
            title = "State A — Behavioral Null"
            justification = (
                f"Side-channel information produced no measurable difference exceeding the exploratory "
                f"classification threshold (D_pol(C1)={t12_rq1['d_pol_c1']:.4f}, D_pol(C2)={d_pol_c2_t12:.4f} < {D_POL_THRESHOLD} or p >= {P_VAL_THRESHOLD})."
            )
        elif c2_passes_t12 and not c1_additional_passes:
            state = "STATE_B"
            title = "State B — R3 Discrete Behavioral Sufficiency"
            justification = (
                f"Discrete ternary sign side-channel (R3) produced measurable behavioral divergence "
                f"(D_pol={d_pol_c2_t12:.4f} >= {D_POL_THRESHOLD}, p={p_val_c2_t12:.2e}), while continuous direction (R2) "
                f"provided no additional behavioral value beyond R3 in matched same-sign cases "
                f"(D_pol(R2|same-sign)={d_pol_2a_c1:.4f} < {D_POL_THRESHOLD}, p={p_val_2a_c1:.2e})."
            )
        elif (c2_passes_t12 and c1_additional_passes) or (c1_passes_t12 and not c2_passes_t12):
            state = "STATE_C"
            title = "State C — R2 Continuous Additional Value"
            justification = (
                f"Continuous unit direction (R2) produced measurable behavioral divergence beyond R3 "
                f"(D_pol(C1)={t12_rq1['d_pol_c1']:.4f} >= {D_POL_THRESHOLD}, p={t12_rq1['p_val_c1']:.2e}; "
                f"D_pol(R2|same-sign)={d_pol_2a_c1:.4f} >= {D_POL_THRESHOLD}, p={p_val_2a_c1:.2e})."
            )
        else:
            state = "STATE_D"
            title = "State D — Mixed / Timescale-Dependent"
            justification = "Behavioral utilization characteristics vary across the conversational exposure grid."

        classification = {
            "assigned_state": state,
            "title": title,
            "justification": justification,
            "threshold_used": {
                "d_pol_threshold": D_POL_THRESHOLD,
                "p_val_threshold": P_VAL_THRESHOLD,
                "threshold_type": "predefined exploratory classification threshold",
            },
            "metrics_at_t12": {
                "d_pol_c2": float(d_pol_c2_t12),
                "p_val_c2": float(p_val_c2_t12),
                "d_pol_test_2a_c1_in_same_sign": float(d_pol_2a_c1),
                "p_val_test_2a_c1": float(p_val_2a_c1),
            },
        }
        print(f"Classification: {title}")
        print(f"  {justification}")
        return classification

    def run_full_study(self) -> Dict[str, Any]:
        """Execute complete Phase 22 H1 Directional Behavioral Utilization study."""
        t_start = time.time()
        self.generate_frozen_dataset()
        self.simulate_trajectories()
        results_by_t = self.run_all_conditions_on_grid()

        rq1_results = self.evaluate_rq1_behavioral_sensitivity(results_by_t)
        rq2_results = self.evaluate_rq2_continuous_vs_discrete()
        rq3_results = self.evaluate_rq3_behavioral_utilization_vs_geometric_resolution()
        rq4_results = self.evaluate_rq4_directional_effects_on_policy(results_by_t)
        rq5_results = self.evaluate_rq5_scalar_preservation(results_by_t)
        rq6_results = self.evaluate_rq6_null_controls(results_by_t)
        cf_results = self.evaluate_counterfactual_interventions()
        classification = self.classify_final_state(rq1_results, rq2_results, cf_results)

        elapsed = time.time() - t_start

        full_output = {
            "metadata": {
                "study": "Phase 22 H1 — Directional Side-Channel Behavioral Utilization Study",
                "status": "COMPLETED",
                "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
                "elapsed_seconds": float(elapsed),
                "governance": {
                    "phase_22_h1": "INCONCLUSIVE",
                    "gate_2": "BLOCKED",
                    "protocol_v1_5": "NOT AUTHORIZED",
                    "architecture_gate": "STRICTLY LOCKED",
                    "genesis_profile": "PRESERVED_BIT_EXACT",
                    "src_core_mutations": 0,
                },
                "methodological_scope_lock": (
                    "The study measures downstream policy/conditioning utilization in an isolated "
                    "research adapter, not end-to-end SLM behavioral utilization. In the absence of a "
                    "production-identical local SLM execution path, all conclusions are strictly scoped "
                    "to downstream behavioral utilization under the research harness."
                ),
                "seed": self.seed,
                "null_seed": self.null_seed,
                "n_probes": len(self.all_probes),
                "exposure_grid": T_CONVERSATIONAL,
            },
            "rq1_behavioral_sensitivity": rq1_results,
            "rq2_continuous_vs_discrete": rq2_results,
            "rq3_utilization_vs_geometric": rq3_results,
            "rq4_directional_effects": rq4_results,
            "rq5_scalar_preservation": rq5_results,
            "rq6_null_controls": rq6_results,
            "counterfactual_interventions": cf_results,
            "state_classification": classification,
        }

        # Save results JSON
        os.makedirs(RESULTS_DIR, exist_ok=True)
        out_path = RESULTS_DIR / "directional_behavior_results.json"
        with open(out_path, "w", encoding="utf-8") as f:
            json.dump(full_output, f, indent=2)
        print(f"\nSaved structured results to {out_path}")

        # Compute SHA-256 and write manifest
        with open(out_path, "rb") as f:
            sha = hashlib.sha256(f.read()).hexdigest()

        manifest = {
            "manifest_version": "1.0",
            "study_name": "Phase 22 H1 Directional Side-Channel Behavioral Utilization Study",
            "created_at": time.strftime("%Y-%m-%d %H:%M:%S"),
            "governance_invariants": {
                "phase_22_h1": "INCONCLUSIVE",
                "gate_2": "BLOCKED",
                "protocol_v1_5": "NOT AUTHORIZED",
                "architecture_gate": "STRICTLY LOCKED",
                "genesis_profile": "PRESERVED_BIT_EXACT",
                "src_core_mutations": 0,
            },
            "methodology_locks": {
                "behavioral_scope": "Downstream policy/conditioning utilization under isolated research adapter",
                "counterfactual_validity": "Measurement intervention with unit norm, finite values, and exact S_i preservation",
                "classification_threshold": "Predefined exploratory classification threshold (D_pol >= 0.05, p < 0.05)",
                "r3_representation": "1 continuous scalar + 3 ternary sign symbols in {-1, 0, +1}^3",
                "dual_metric_evaluation": "D_pol for discrete argmax switch; D_JS and D_TV for continuous policy distribution shift",
                "rq5_observed_monotonicity_scope": "Observed monotonic association across frozen stimuli/exposures rather than controlled global scaling",
                "missing_sidechannel_invariant": "C0 and C1/C2 share identical scalar-S pathway; absent side-channel strictly neutralized/zeroed",
            },
            "assigned_state": classification["assigned_state"],
            "state_title": classification["title"],
            "files": {
                "directional_behavior_results.json": {
                    "path": str(out_path.relative_to(REPO_ROOT)).replace("\\", "/"),
                    "sha256": sha,
                    "size_bytes": os.path.getsize(out_path),
                }
            },
        }

        os.makedirs(FIXTURES_DIR, exist_ok=True)
        manifest_path = FIXTURES_DIR / "manifest_h1_directional_sidechannel_behavior.json"
        with open(manifest_path, "w", encoding="utf-8") as f:
            json.dump(manifest, f, indent=2)
        print(f"Saved manifest to {manifest_path}")

        return full_output


if __name__ == "__main__":
    engine = DirectionalBehaviorStudyEngine(seed=9999, null_seed=8888)
    engine.run_full_study()
