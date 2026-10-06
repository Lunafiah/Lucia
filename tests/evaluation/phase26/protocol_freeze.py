"""
tests/evaluation/phase26/protocol_freeze.py

P26 Experimental Design Freeze & Protocol Validation.
Defines frozen operational estimands (C1, C2, C3), preregistration schema,
sample-size planning, observation windows, controls ledger, and decision rules.

GOVERNANCE & BOUNDARIES:
- TEST-ONLY research infrastructure. Zero changes to src/core/**, electron/**, data/**.
- Protocol Design Freeze: Pre-specifies experimental rules and analysis BEFORE execution.
- C2/C3 execution remains NOT AUTHORIZED until this freeze is formally accepted.
- Does NOT claim emergence, preference, or individuality.
"""

from __future__ import annotations

import copy
import dataclasses
import enum
import hashlib
import json
import logging
from dataclasses import asdict, dataclass, field
from typing import Any, Callable, Dict, List, Optional, Tuple

import numpy as np

logger = logging.getLogger("ProtocolFreeze")


class DecisionVerdict(str, enum.Enum):
    """Preregistered decision outcomes for causal claims."""
    POSITIVE = "POSITIVE"
    NEGATIVE = "NEGATIVE"
    INCONCLUSIVE = "INCONCLUSIVE"


class ClaimID(str, enum.Enum):
    """Identifier for P26 nested causal claims."""
    C1_HISTORY_DEPENDENCE = "C1_HISTORY_DEPENDENCE"
    C2_MATCHED_EXPOSURE_DIFFERENTIATION = "C2_MATCHED_EXPOSURE_DIFFERENTIATION"
    C3_HISTORY_ENDOGENEITY = "C3_HISTORY_ENDOGENEITY"


@dataclass(frozen=True)
class EstimandSpecification:
    """
    Formal operational specification of an estimand for P26 claims.
    """
    claim_id: ClaimID
    name: str
    symbol: str
    mathematical_definition: str
    estimator_formula: str
    target_quantity: str
    interpretation_boundary: str


# ---------------------------------------------------------------------------
# 1. FROZEN OPERATIONAL ESTIMANDS
# ---------------------------------------------------------------------------

ESTIMAND_C1 = EstimandSpecification(
    claim_id=ClaimID.C1_HISTORY_DEPENDENCE,
    name="History-Dependent Choice Shift",
    symbol="theta_C1",
    mathematical_definition="E[Y(H_active) - Y(H_0) | Recency_matched]",
    estimator_formula="P(A | H_active) - P(A | H_0)",
    target_quantity="Difference in evaluative choice probability following history accumulation vs unconditioned baseline.",
    interpretation_boundary="Demonstrates statefulness/memory retention only; does NOT imply individuality or matched differentiation.",
)

ESTIMAND_C2 = EstimandSpecification(
    claim_id=ClaimID.C2_MATCHED_EXPOSURE_DIFFERENTIATION,
    name="Matched-Exposure Choice Divergence (Total Variation)",
    symbol="theta_C2",
    mathematical_definition="D_eval(R_A, R_B | Exposure_matched) = ||P_A - P_B||_TV",
    estimator_formula="0.5 * sum(|P_A(y) - P_B(y)| for y in {Option_A, Option_B, Indifferent, Refusal})",
    target_quantity="Total variation distance between evaluative choice distributions of matched replicas receiving statistically matched exposures.",
    interpretation_boundary=(
        "Evaluates discrete choice divergence under matched exposure. "
        "Direct subtraction of continuous MT-LNN ODE chaos drift (e.g. 0.1305*eps or 0.1732*eps) "
        "from choice-TV is STRICTLY PROHIBITED because choice distributions Delta({A,B}) and ODE "
        "continuous state space R^48 occupy entirely different metric spaces without an established "
        "cross-metric calibration mapping. The Blocker 3 chaos reference is reported separately as a "
        "contextual dynamical reference only. No 'net of chaos' subtraction claim is made."
    ),
)

ESTIMAND_C3 = EstimandSpecification(
    claim_id=ClaimID.C3_HISTORY_ENDOGENEITY,
    name="Downstream Action-Contingency Endogeneity Contrast",
    symbol="theta_C3",
    mathematical_definition="E[Y_{K+tau}(H_active) - Y_{K+tau}(H_yoked) | Exposure[1:K]_matched, Action[1:K]_matched, lag=tau]",
    estimator_formula="P(Y_{K+tau}=A | Active_history[1:K]) - P(Y_{K+tau}=A | Yoked_replay_history[1:K])",
    target_quantity="Contrast in unconstrained downstream evaluative choices on a common test probe Y presented at post-induction lag tau, following matched active vs yoked induction history.",
    interpretation_boundary="Measures whether endogenous action generation during induction alters future unconstrained behavioral trajectory compared to passive replayed history. Does NOT evaluate replayed actions during induction.",
)


# ---------------------------------------------------------------------------
# 2. DYNAMIC CHAOS REFERENCE ENVELOPE (BLOCKER 3 PROVENANCE)
# ---------------------------------------------------------------------------

@dataclass(frozen=True)
class Blocker3ChaosReference:
    """
    Empirical reference distribution derived from Blocker 3 dynamic chaos baseline.
    CONFIG-SPECIFIC EVIDENCE ONLY:
    - Tested Subsystem: Continuous R^48 Coupled MT-LNN ODE (RK45, dt=0.200s).
    - Tested Horizon: 50 ticks (10.0s virtual time).
    - Tested Seeds: 5 master seeds [1001, 2002, 3003, 4004, 5005].
    - Perturbation Range: epsilon in [10^-8, 10^-3].
    - Empirical Distribution of Peak ||d_pad|| / epsilon:
        * Sample Mean Peak Ratio: 0.130451
        * Sample p95 Peak Ratio: 0.173208
        * Sample Max Peak Ratio: 0.178920
    NON-UNIVERSAL STATUS & METRIC ISOLATION:
    Applies strictly to continuous limbic ODE state divergence.
    Does NOT calibrate to discrete SLM choice distributions.
    Does NOT extrapolate to Kanerva SDM memory writes or general runtime dynamics.
    """
    mean_peak_ratio: float = 0.130451
    p95_peak_ratio: float = 0.173208
    max_peak_ratio: float = 0.178920
    tested_horizon_ticks: int = 50
    tested_seed_count: int = 5
    tested_subsystem: str = "MT_LNN_ODE_CONTINUOUS"


# ---------------------------------------------------------------------------
# 3. EFFECT SIZE TAXONOMY & SDE PLANNING (NON-UNIVERSAL INSTRUMENT SPEC)
# ---------------------------------------------------------------------------

@dataclass
class EffectSizeTaxonomy:
    """
    Strict separation of effect size concepts in P26 protocol planning.
    Distinguishes power/instrument planning from substantive scientific thresholds.
    """
    # 1. Statistical Power / Instrument Planning Quantities
    sde_planning_n120: float = 0.1000    # Power planning: SDE at N=120, alpha=0.05, power=0.80, p0=0.08333
    sde_planning_n24: float = 0.2235     # Power planning at pilot sample N=24
    planning_delta: float = 0.1000       # Planning effect size used for sample-size calculation

    # 2. Substantive Scientific Quantities (Not Yet Independently Justified)
    soi_status: str = "TBD / NOT YET INDEPENDENTLY JUSTIFIED"
    soi_substantive_value: Optional[float] = None  # Requires independent domain/psychological grounding

    # 3. Equivalence Testing Margin
    rope_status: str = "TBD / NOT YET INDEPENDENTLY JUSTIFIED"
    rope_margin: Optional[float] = None            # Requires empirical or normative equivalence standard

    # 4. Hypothesis Testing Target
    hypothesis_target: str = "PLANNING_DELTA_BENCHMARK"  # Target for preliminary power assessment only

    justification_boundary: str = (
        "The numerical value 0.10 (10%) is STRICTLY AN INSTRUMENT-CALIBRATED PLANNING QUANTITY (SDE) "
        "derived from N=120 power feasibility under the current SLM extractor. "
        "It is NOT a substantive Smallest Effect of Interest (SOI), NOT a justified ROPE margin, "
        "and NOT an established scientific property of true individuality. "
        "Substantive SOI and ROPE remain TBD until independent domain evidence is established."
    )


@dataclass
class SubstrateBaselineReference:
    """
    Audit of Step 3 substrate baseline reference.
    """
    transported_descriptive_p0: float = 0.08333333333333333  # Aggregate Option A proportion from Step 3 (2/24)
    step3_total_trials: int = 24
    step3_standard_trials: int = 8
    is_condition_matched_to_standard: bool = False
    audit_finding: str = (
        "Step 3 baseline (8.33%) was evaluated across a mixed factorial of 24 trials spanning "
        "2 probes x 2 orders x 3 formats (STANDARD, INFORMAL, OPERATIONAL) with 77.78% non-extraction. "
        "It is a TRANSPORTED DESCRIPTIVE REFERENCE across the pilot slice, NOT a condition-matched "
        "causal baseline for the pure STANDARD conversational regime. "
        "Causal trial design MUST evaluate a concurrent unconditioned baseline cell (H0) "
        "within the exact same STANDARD regime rather than using a historical point estimate."
    )


@dataclass
class InstrumentSensitivityPlan:
    """
    Sample-size and Smallest Detectable Effect (SDE) planning grounded
    in empirical Phase 26 Step 5 sensitivity telemetry.
    """
    alpha: float = 0.05
    power_target: float = 0.80
    baseline_ref: SubstrateBaselineReference = field(default_factory=SubstrateBaselineReference)
    effect_taxonomy: EffectSizeTaxonomy = field(default_factory=EffectSizeTaxonomy)
    chaos_reference: Blocker3ChaosReference = field(default_factory=Blocker3ChaosReference)
    planned_n_per_cell: int = 120             # Exact planned sample size per condition
    planned_n_per_cell_scaled: int = 240      # Scaled sample size for high-resolution studies

    def compute_analytic_sde(self, n_trials: int, p0: Optional[float] = None) -> float:
        """
        Computes the analytic Smallest Detectable Effect (two-sided alpha=0.05, power=0.80)
        given n trials per condition and baseline proportion p0:
        SDE = sqrt( 2 * (z_alpha/2 + z_beta)^2 * p0 * (1 - p0) / n )
        Grounded in Step 5 correction derivation (yielding SDE = 22.35% at N=24, 10.00% at N=120).
        """
        p = self.baseline_ref.transported_descriptive_p0 if p0 is None else p0
        z_factor_sq = (1.95996 + 0.84162) ** 2  # 7.84888
        variance = 2.0 * z_factor_sq * p * (1.0 - p)
        return float(np.sqrt(variance / max(1, n_trials)))

    def evaluate_feasibility(self) -> Dict[str, Any]:
        """Calculates detectable effect thresholds across candidate sample sizes."""
        return {
            "step5_pilot_N24_sde": self.compute_analytic_sde(24),
            "planned_standard_N120_sde": self.compute_analytic_sde(120),
            "planned_scaled_N240_sde": self.compute_analytic_sde(240),
            "effect_size_taxonomy": asdict(self.effect_taxonomy),
            "chaos_reference": asdict(self.chaos_reference),
            "substrate_baseline_audit": asdict(self.baseline_ref),
            "planning_status": "FEASIBLE_AT_N120_STANDARD",
            "epistemic_warning": self.effect_taxonomy.justification_boundary,
        }


# ---------------------------------------------------------------------------
# 4. PERSISTENCE & OBSERVATION WINDOWS (ANTI-CONTAMINATION BRANCHES)
# ---------------------------------------------------------------------------

@dataclass(frozen=True)
class ObservationWindowBranch:
    """
    Specification of an independent, un-contaminated evaluation branch for a given observation lag.
    To prevent cross-probe contamination (where a probe at lag tau_0 changes replica state for tau_1),
    each lag is evaluated on an independent branch forked directly from the post-induction snapshot S_K.
    """
    lag_id: str                          # e.g. "TAU_0_IMMEDIATE", "TAU_5_WASHOUT", "TAU_20_EXTENDED"
    tau_ticks: int                       # Delay ticks from snapshot (0, 5, 20)
    delay_virtual_time_sec: float        # tau * 0.200s (0.0s, 1.0s, 4.0s)
    requires_snapshot_fork: bool = True  # Must be restored freshly from S_K
    single_probe_only: bool = True       # Receives exactly one probe, no sequential chaining


@dataclass(frozen=True)
class ObservationWindowConfig:
    """
    Frozen temporal observation windows using independent snapshot-forked evaluation branches.
    Zero cross-probe contamination: Each lag is an independent counterfactual branch from S_K.
    """
    branches: Tuple[ObservationWindowBranch, ...] = (
        ObservationWindowBranch(lag_id="TAU_0_IMMEDIATE", tau_ticks=0, delay_virtual_time_sec=0.0),
        ObservationWindowBranch(lag_id="TAU_5_WASHOUT", tau_ticks=5, delay_virtual_time_sec=1.0),
        ObservationWindowBranch(lag_id="TAU_20_EXTENDED", tau_ticks=20, delay_virtual_time_sec=4.0),
    )
    philia_decay_tolerance: float = 0.05 # Distance to Philia resting attractor required for washout audit


# ---------------------------------------------------------------------------
# 5. CONTROLS LEDGER
# ---------------------------------------------------------------------------

@dataclass
class ProtocolControlRule:
    control_id: str
    target_confound: str
    mechanism: str
    success_criterion: str
    verified_in: str


FROZEN_CONTROLS_LEDGER = [
    ProtocolControlRule(
        control_id="CTRL_EXPOSURE_RECENCY",
        target_confound="Recency bias & presentation order",
        mechanism="Factorial balance (Order A->B vs B->A) + matched exposure timestamps.",
        success_criterion="Order bias contrast |P(A_first) - P(B_first)| <= 0.20 or factored out in ANOVA.",
        verified_in="P26_STEP3_SUBSTRATE_ORDER_BASELINE.md",
    ),
    ProtocolControlRule(
        control_id="CTRL_ANTI_SYCOPHANCY",
        target_confound="Compliance with user/evidence social framing",
        mechanism="Social framing conditions (NEUTRAL, A_FAVOR, B_FAVOR, USER_PREF) from Step 4.",
        success_criterion="Social alignment indices S_user, S_evidence quantified and separated from choice shift.",
        verified_in="P26_STEP4_SOCIAL_FRAMING_ANTISYCOPHANCY.md",
    ),
    ProtocolControlRule(
        control_id="CTRL_AFFECT_RELATIONSHIP",
        target_confound="Transient limbic excitation / emotional valence carryover",
        mechanism="Virtual clock ODE advancement to Philia resting attractor before probe administration.",
        success_criterion="Limbic state distance to Philia attractor ||PAD - Philia|| <= 0.05.",
        verified_in="P26_BLOCKER3_DYNAMIC_CHAOS_BASELINE.md",
    ),
    ProtocolControlRule(
        control_id="CTRL_SUBSTRATE_BASELINE",
        target_confound="Pre-existing model prior / lexical asymmetry",
        mechanism="Concurrent unconditioned baseline cell (H0) evaluated in identical STANDARD regime.",
        success_criterion="Observed effect delta > concurrent baseline asymmetry floor (Step 3 transported p0=8.33% used as descriptive reference).",
        verified_in="P26_STEP3_CORRECTION.md",
    ),
    ProtocolControlRule(
        control_id="CTRL_DYNAMIC_CHAOS",
        target_confound="Trivial epsilon-perturbation drift in dynamic trajectories",
        mechanism="Subtraction of Blocker 3 config-specific chaos reference envelope (p95=0.1732*eps, max=0.1789*eps).",
        success_criterion="Measured divergence ||d_pad|| > Blocker 3 empirical reference envelope for tested MT-LNN ODE config.",
        verified_in="P26_BLOCKER3_DYNAMIC_CHAOS_BASELINE.md",
    ),
    ProtocolControlRule(
        control_id="CTRL_POSITIVE_SENSITIVITY",
        target_confound="Measurement device deafness (false negative)",
        mechanism="Planted difference positive control from Step 5 (MEDIUM/LARGE synthetic directives).",
        success_criterion="Planted condition yields delta >= 12.5% unconditional, 100% conditional shift.",
        verified_in="P26_STEP5_PLANTED_DIFFERENCE_SENSITIVITY.md",
    ),
    ProtocolControlRule(
        control_id="CTRL_NEGATIVE_NULL",
        target_confound="Spurious divergence / false positive",
        mechanism="NULL intervention condition (injected signal = 0) with identical replicas.",
        success_criterion="Measured divergence = 0.000 bit-exact (Zero drift floor).",
        verified_in="P26_STEP5_CORRECTION.md",
    ),
]


# ---------------------------------------------------------------------------
# 5. REPEATED-MEASURES, EVALUATIVE DOMAINS & HELD-OUT PROBES
# ---------------------------------------------------------------------------

@dataclass(frozen=True)
class EvaluativeDomainConfig:
    domain_id: str
    status: str
    probe_ids: Tuple[str, ...]
    surface_formats: Tuple[str, ...]


FROZEN_DOMAINS = {
    "ACTIVE_DOMAINS": (
        EvaluativeDomainConfig(
            domain_id="INFORMATION_FORAGING",
            status="ACTIVE",
            probe_ids=("INFO_FORAGING_01", "INFO_FORAGING_02"),
            surface_formats=("STANDARD", "INFORMAL"),
        ),
        EvaluativeDomainConfig(
            domain_id="TASK_STRATEGY",
            status="ACTIVE",
            probe_ids=("TASK_STRATEGY_01", "TASK_STRATEGY_02"),
            surface_formats=("STANDARD", "INFORMAL"),
        ),
    ),
    "HELD_OUT_DOMAINS": (
        EvaluativeDomainConfig(
            domain_id="COGNITIVE_EXPLORATION",
            status="HELD_OUT_UNSEEN",
            probe_ids=("COGNITIVE_EXPLORE_01", "COGNITIVE_EXPLORE_02"),
            surface_formats=("STANDARD",),
        ),
        EvaluativeDomainConfig(
            domain_id="COLLABORATION_STYLE",
            status="HELD_OUT_UNSEEN",
            probe_ids=("COLLAB_STYLE_01", "COLLAB_STYLE_02"),
            surface_formats=("STANDARD",),
        ),
    ),
}


# ---------------------------------------------------------------------------
# 6. PREREGISTRATION SCHEMA
# ---------------------------------------------------------------------------

@dataclass
class PreregistrationSpec:
    """
    Formal, immutable preregistration specification schema for P26 trials.
    """
    spec_version: str = "P26_PREREG_v1.0"
    hypotheses: Dict[str, str] = field(default_factory=dict)
    estimands: Dict[str, str] = field(default_factory=dict)
    exclusion_criteria: List[str] = field(default_factory=list)
    stopping_rules: List[str] = field(default_factory=list)
    seed_allocation_policy: str = "CRN_DETERMINISTIC_SEEDED"
    statistical_analysis_plan: Dict[str, Any] = field(default_factory=dict)
    provenance_hash: Optional[str] = None

    def compute_provenance_hash(self) -> str:
        """Computes deterministic SHA-256 hash across all preregistration fields."""
        data = {
            "spec_version": self.spec_version,
            "hypotheses": self.hypotheses,
            "estimands": self.estimands,
            "exclusion_criteria": sorted(self.exclusion_criteria),
            "stopping_rules": sorted(self.stopping_rules),
            "seed_allocation_policy": self.seed_allocation_policy,
            "statistical_analysis_plan": self.statistical_analysis_plan,
        }
        encoded = json.dumps(data, sort_keys=True, separators=(",", ":")).encode("utf-8")
        return hashlib.sha256(encoded).hexdigest()


def create_canonical_p26_preregistration() -> PreregistrationSpec:
    """Creates the canonical P26 research trial preregistration specification."""
    spec = PreregistrationSpec(
        hypotheses={
            "H1_HistoryDependence": "Replicas exposed to differential conversational histories exhibit choice distributions differing by at least planning_delta=0.10 from concurrent unconditioned baseline.",
            "H2_MatchedExposureDifferentiation": "Replicas exposed to matched multi-turn histories develop choice divergence TV(P_A, P_B) exceeding planning_delta=0.10 (continuous MT-LNN chaos envelope reported as contextual reference).",
            "H3_HistoryEndogeneity": "Active replicas with endogenous action choice differ from passive yoked replicas in downstream unconstrained choice by at least planning_delta=0.10.",
        },
        estimands={
            "C1": ESTIMAND_C1.mathematical_definition,
            "C2": ESTIMAND_C2.mathematical_definition,
            "C3": ESTIMAND_C3.mathematical_definition,
        },
        exclusion_criteria=[
            "EXCL_PARSE_FAILED: Responses that fail strict grammar parsing without clean option selection.",
            "EXCL_SELF_REPORT_DEFECT: Any response containing introspective affective declarations (INV-2 defect).",
            "EXCL_TIMING_DRIFT: Any execution where virtual clock drift exceeds 1e-9 seconds.",
            "EXCL_HASH_MISMATCH: Any execution where exposure or action ledger verification fails.",
        ],
        stopping_rules=[
            "STOP_FIXED_N: Each experimental cell shall evaluate exactly N=120 trials without early stopping for significance.",
            "STOP_GATE_FAIL_CLOSED: Execution immediately terminates fail-closed if any integrity or isolation audit fails.",
        ],
        seed_allocation_policy="DETERMINISTIC_REPRODUCIBLE: Fixed seeds 1000..1239 per cell; CRN seeds aligned across paired replicas.",
        statistical_analysis_plan={
            "primary_test": "Exact two-sided permutation test with 10,000 resamples.",
            "confidence_intervals": "Wilson score intervals (95%) for single proportions; bootstrap BCa intervals (95%) for differences.",
            "equivalence_test": "Two One-Sided Tests (TOST) against provisional planning margin delta = [-0.10, +0.10] (Substantive ROPE remains TBD).",
            "multiple_testing": "Benjamini-Hochberg FDR adjustment across secondary probe contrasts.",
        },
    )
    spec.provenance_hash = spec.compute_provenance_hash()
    return spec


# ---------------------------------------------------------------------------
# 7. DECISION RULES: POSITIVE / NEGATIVE / INCONCLUSIVE
# ---------------------------------------------------------------------------

class DecisionEvaluator:
    """
    Evaluates trial results against preregistered planning thresholds.
    Enforces that:
    1. POSITIVE indicates detection above instrument planning SDE (planning_delta).
       Does NOT declare substantive psychological individuality since SOI/ROPE remain TBD.
    2. NEGATIVE indicates bounded below planning_delta.
    3. INCONCLUSIVE indicates CI spans boundary or data are insufficient (UNKNOWN).
    """

    @staticmethod
    def evaluate_claim(
        point_estimate: float,
        ci_lower: float,
        ci_upper: float,
        planning_delta: float = 0.10,
    ) -> Tuple[DecisionVerdict, str]:
        """
        Decision Logic:
        1. POSITIVE: 95% CI lower bound strictly exceeds planning_delta.
           (ci_lower > planning_delta).
        2. NEGATIVE: 95% CI is completely contained within [-planning_delta, +planning_delta].
           (ci_lower >= -planning_delta) AND (ci_upper <= planning_delta).
        3. INCONCLUSIVE: CI spans boundary or variance is unbounded.
        """
        if ci_lower > planning_delta:
            return DecisionVerdict.POSITIVE, (
                f"Observed effect is statistically distinct from zero and strictly exceeds "
                f"instrument planning threshold (ci_lower={ci_lower:.4f} > planning_delta={planning_delta:.4f}). "
                f"Substantive SOI remains TBD."
            )

        if ci_lower >= -planning_delta and ci_upper <= planning_delta:
            return DecisionVerdict.NEGATIVE, (
                f"95% CI [{ci_lower:.4f}, {ci_upper:.4f}] is bounded within [-{planning_delta}, +{planning_delta}]. "
                f"Absence of effect above planning threshold established. Substantive ROPE remains TBD."
            )

        return DecisionVerdict.INCONCLUSIVE, (
            f"Confidence interval [{ci_lower:.4f}, {ci_upper:.4f}] spans the planning boundary. "
            f"Data are insufficient to confirm or refute claim (UNKNOWN)."
        )
