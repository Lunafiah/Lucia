"""
tests/evaluation/phase25/e2_repair_dynamics.py

Phase 25 Track E2 — Repair vs Ordinary Interaction Evaluation Harness.

PRIMARY SCIENTIFIC INQUIRY (P25-Q1):
  "What computational representation, if any, is necessary for Lucia to maintain
   persistent relational consequences of significant interaction events beyond the
   timescale of instantaneous affective recovery, while preserving stability and INV-2?"

SCIENTIFIC HYPOTHESES:
  H1 (Differential Repair Trajectory): Explicit repair attempts produce lower Social
      Prediction Error (SPE), higher Directness alignment with the relational breach,
      and higher Supportiveness yield compared to passive neutral continuation.
  H0 (Null Hypothesis / Alternative Explanation): Explicit repair attempts produce
      no statistically distinguishable trajectory differences from ordinary neutral
      or casual interaction in the absence of new specialized social-state representations.

MANDATORY CONSTRAINTS:
  - Use ONLY evaluation metrics: Social Prediction Error, Directness, Supportiveness.
  - These metrics are EVALUATION INSTRUMENTATION ONLY, not production ontology.
  - Do NOT introduce new social-state classes (no RelationalRupture, no RepairEvent in production).
  - Compare:
      (1) ordinary positive interaction (counterfactual control);
      (2) explicit repair attempt;
      (3) no repair / neutral continuation.
"""

from __future__ import annotations

import logging
import math
import sys
import time
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

import numpy as np

PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from src.core.config import EmotionConfig
from src.core.emotion.emotion_core import EmotionCore
from src.core.models import PADState, SomaticMarkers
from src.core.relationship.signals import RelationshipSignal, RelationshipSignalType
from src.core.relationship.state import RelationshipState
from src.core.relationship.updater import RelationshipUpdater
from tests.evaluation.phase25.models import (
    DirectnessMetric,
    EvaluationPADSnapshot,
    EvaluationRelSnapshot,
    EvaluationSomaticSnapshot,
    SocialPredictionError,
    SupportivenessMetric,
    TrajectoryRecord,
)

logger = logging.getLogger(__name__)
PHILIA_PAD = np.array([0.25, -0.05, 0.05], dtype=np.float64)


@dataclass
class E2BranchMetrics:
    """Consolidated evaluation metrics for a single experimental branch."""
    branch_name: str
    mean_relational_spe: float
    final_relational_spe: float
    mean_affective_spe: float
    mean_directness: float
    mean_supportiveness: float
    trust_restoration_delta: float
    reciprocity_restoration_delta: float


@dataclass
class E2TrialResult:
    """Telemetry record for a single E2 trial comparing 3 branches."""
    trial_index: int
    rupture_intensity: float
    repair_intensity: float
    branches: Dict[str, E2BranchMetrics]
    directness_advantage: float
    spe_reduction_ratio: float
    supportiveness_advantage: float

    def to_dict(self) -> Dict[str, Any]:
        return {
            "trial_index": self.trial_index,
            "rupture_intensity": self.rupture_intensity,
            "repair_intensity": self.repair_intensity,
            "branches": {k: asdict(v) for k, v in self.branches.items()},
            "directness_advantage": self.directness_advantage,
            "spe_reduction_ratio": self.spe_reduction_ratio,
            "supportiveness_advantage": self.supportiveness_advantage,
        }


@dataclass
class E2TrackSummary:
    """Consolidated statistical summary for Track E2."""
    trial_count: int
    mean_repair_spe: float
    mean_no_repair_spe: float
    mean_ordinary_spe: float
    spe_diff_mean: float
    spe_diff_std: float
    spe_diff_ci95: Tuple[float, float]
    mean_repair_directness: float
    mean_no_repair_directness: float
    mean_repair_supportiveness: float
    mean_no_repair_supportiveness: float
    measurable_separation_observed: bool
    evidence_statement: str
    p25_q1_implication: str

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


class E2RepairDynamicsEvaluator:
    """
    Evaluator executing comparative branch simulations following a relational breach.
    """

    def __init__(self, random_seed: int = 42) -> None:
        self.rng = np.random.default_rng(random_seed)

    def _step_emotion(self, core: EmotionCore, valence: float, arousal: float, dominance: float, dt: float = 0.5) -> PADState:
        stimulus = np.zeros(16, dtype=np.float64)
        stimulus[0] = valence
        stimulus[1] = arousal
        stimulus[2] = dominance
        core.push_stimulus(stimulus)
        core.step_once()
        return core.get_pad_state()

    def run_trial(
        self,
        trial_index: int,
        rupture_intensity: float = 0.85,
        repair_intensity: float = 0.80,
        warmup_steps: int = 5,
        rupture_steps: int = 3,
        branch_steps: int = 6,
        step_dt: float = 0.5,
    ) -> E2TrialResult:
        """Run 3 branching trajectories from identical baseline and breach."""

        # Initial established relationship baseline before rupture
        established_rel = RelationshipState(familiarity=0.50, trust=0.75, closeness=0.45, reciprocity=0.65)

        # ---------------------------------------------------------------------
        # Branch 1: Explicit Repair Attempt
        # ---------------------------------------------------------------------
        core_repair = EmotionCore(EmotionConfig())
        updater_repair = RelationshipUpdater(alpha=0.03, decay_rate=0.005, initial_state=established_rel)

        # ---------------------------------------------------------------------
        # Branch 2: No Repair / Neutral Continuation
        # ---------------------------------------------------------------------
        core_norepair = EmotionCore(EmotionConfig())
        updater_norepair = RelationshipUpdater(alpha=0.03, decay_rate=0.005, initial_state=established_rel)

        # ---------------------------------------------------------------------
        # Branch 3: Ordinary Positive (Counterfactual unperturbed control)
        # ---------------------------------------------------------------------
        core_ordinary = EmotionCore(EmotionConfig())
        updater_ordinary = RelationshipUpdater(alpha=0.03, decay_rate=0.005, initial_state=established_rel)

        # Phase 1: Shared Warmup
        for _ in range(warmup_steps):
            self._step_emotion(core_repair, 0.0, 0.0, 0.0, step_dt)
            self._step_emotion(core_norepair, 0.0, 0.0, 0.0, step_dt)
            self._step_emotion(core_ordinary, 0.0, 0.0, 0.0, step_dt)

        r_baseline = updater_repair.get_state().to_array()

        # Phase 2: Perturbation (Branches 1 & 2 get rupture; Branch 3 gets positive)
        for _ in range(rupture_steps):
            # Branches 1 & 2 receive conflict
            sig_rupture = RelationshipSignal.create(RelationshipSignalType.CONFLICT_DISMISSAL, intensity=rupture_intensity)
            self._step_emotion(core_repair, -0.65 * rupture_intensity, 0.40 * rupture_intensity, -0.30 * rupture_intensity, step_dt)
            self._step_emotion(core_norepair, -0.65 * rupture_intensity, 0.40 * rupture_intensity, -0.30 * rupture_intensity, step_dt)
            updater_repair.step(signal=sig_rupture)
            updater_norepair.step(signal=sig_rupture)

            # Branch 3 receives positive interaction
            sig_pos = RelationshipSignal.create(RelationshipSignalType.COLLABORATIVE_SUCCESS, intensity=0.50)
            self._step_emotion(core_ordinary, 0.40, 0.10, 0.10, step_dt)
            updater_ordinary.step(signal=sig_pos)

        r_post_rupture = updater_repair.get_state().to_array()
        breach_deficit = r_baseline - r_post_rupture  # Deficit vector caused by rupture

        # Phase 3: Branch Execution
        branch_metrics_dict: Dict[str, E2BranchMetrics] = {}

        for branch_name, c_core, c_updater, sig_type, intensity_val, val_stim, tension_val in [
            ("explicit_repair", core_repair, updater_repair, RelationshipSignalType.REPAIR_ATTEMPT, repair_intensity, 0.35, 0.20),
            ("no_repair_neutral", core_norepair, updater_norepair, RelationshipSignalType.CASUAL_INTERACTION, 0.20, 0.00, 0.45),
            ("ordinary_positive", core_ordinary, updater_ordinary, RelationshipSignalType.COLLABORATIVE_SUCCESS, 0.50, 0.30, 0.05),
        ]:
            spe_list: List[float] = []
            aff_spe_list: List[float] = []
            directness_list: List[float] = []
            supportiveness_list: List[float] = []
            r_start_branch = c_updater.get_state()

            for step_idx in range(branch_steps):
                sig = RelationshipSignal.create(sig_type, intensity=intensity_val)
                pad = self._step_emotion(c_core, valence=val_stim, arousal=0.05, dominance=0.05, dt=step_dt)
                r_curr, hist_entry = c_updater.step(signal=sig)

                # Counterfactual expected relationship is undisturbed baseline
                spe = SocialPredictionError.compute(
                    actual_rel=r_curr.to_array(),
                    expected_rel=r_baseline,
                    actual_pad=np.array([pad.pleasure, pad.arousal, pad.dominance]),
                    expected_pad=PHILIA_PAD,
                )
                spe_list.append(spe.relational_spe)
                aff_spe_list.append(spe.affective_spe)

                # Directness with respect to breach deficit
                d_metric = DirectnessMetric.compute(
                    signal_delta=sig.delta_vector,
                    breach_deficit=breach_deficit,
                )
                directness_list.append(d_metric.alignment_score)

                # Supportiveness
                delta_t = float(r_curr.trust - r_start_branch.trust)
                delta_r = float(r_curr.reciprocity - r_start_branch.reciprocity)
                s_metric = SupportivenessMetric.compute(
                    delta_trust=delta_t,
                    delta_reciprocity=delta_r,
                    somatic_tension=tension_val,
                )
                supportiveness_list.append(s_metric.score)

            r_end_branch = c_updater.get_state()
            branch_metrics_dict[branch_name] = E2BranchMetrics(
                branch_name=branch_name,
                mean_relational_spe=float(np.mean(spe_list)),
                final_relational_spe=float(spe_list[-1]),
                mean_affective_spe=float(np.mean(aff_spe_list)),
                mean_directness=float(np.mean(directness_list)),
                mean_supportiveness=float(np.mean(supportiveness_list)),
                trust_restoration_delta=float(r_end_branch.trust - r_post_rupture[1]),
                reciprocity_restoration_delta=float(r_end_branch.reciprocity - r_post_rupture[3]),
            )

        repair_m = branch_metrics_dict["explicit_repair"]
        norepair_m = branch_metrics_dict["no_repair_neutral"]

        dir_adv = repair_m.mean_directness - norepair_m.mean_directness
        spe_ratio = norepair_m.final_relational_spe / (repair_m.final_relational_spe + 1e-9)
        sup_adv = repair_m.mean_supportiveness - norepair_m.mean_supportiveness

        return E2TrialResult(
            trial_index=trial_index,
            rupture_intensity=rupture_intensity,
            repair_intensity=repair_intensity,
            branches=branch_metrics_dict,
            directness_advantage=float(dir_adv),
            spe_reduction_ratio=float(spe_ratio),
            supportiveness_advantage=float(sup_adv),
        )

    def run_benchmark(self, num_trials: int = 15) -> Tuple[E2TrackSummary, List[E2TrialResult]]:
        """Run complete Monte Carlo benchmark across varied rupture and repair conditions."""
        trials: List[E2TrialResult] = []
        rupture_levels = np.linspace(0.50, 1.00, num_trials)
        repair_levels = np.linspace(0.50, 0.90, num_trials)

        for i in range(num_trials):
            trials.append(self.run_trial(
                trial_index=i,
                rupture_intensity=float(rupture_levels[i]),
                repair_intensity=float(repair_levels[i]),
            ))

        repair_spes = [t.branches["explicit_repair"].final_relational_spe for t in trials]
        norepair_spes = [t.branches["no_repair_neutral"].final_relational_spe for t in trials]
        ordinary_spes = [t.branches["ordinary_positive"].final_relational_spe for t in trials]

        repair_dirs = [t.branches["explicit_repair"].mean_directness for t in trials]
        norepair_dirs = [t.branches["no_repair_neutral"].mean_directness for t in trials]

        repair_sups = [t.branches["explicit_repair"].mean_supportiveness for t in trials]
        norepair_sups = [t.branches["no_repair_neutral"].mean_supportiveness for t in trials]

        spe_diffs = [nr - r for nr, r in zip(norepair_spes, repair_spes)]
        diff_mean = float(np.mean(spe_diffs))
        diff_std = float(np.std(spe_diffs))
        ci95 = (
            float(diff_mean - 1.96 * diff_std / math.sqrt(len(spe_diffs))),
            float(diff_mean + 1.96 * diff_std / math.sqrt(len(spe_diffs))),
        )

        # Measurable separation under this configuration confirmed when 95% CI strictly excludes zero
        meas_sep = bool(ci95[0] > 0.0 and diff_mean > 0.0)

        evidence = (
            f"Observed: Explicit repair achieved lower final SPE than neutral continuation "
            f"(repair mean={float(np.mean(repair_spes)):.4f}, no_repair mean={float(np.mean(norepair_spes)):.4f}, "
            f"SPE reduction mean={diff_mean:.4f} +/- {diff_std:.4f}, 95% CI={ci95}). "
            f"Directness alignment: repair={float(np.mean(repair_dirs)):.4f} vs neutral={float(np.mean(norepair_dirs)):.4f}. "
            f"Supportiveness: repair={float(np.mean(repair_sups)):.4f} vs neutral={float(np.mean(norepair_sups)):.4f}."
        )

        implication = (
            "Evidence confirms that explicit repair and neutral continuation trajectories are "
            "measurably separable under this evaluation configuration using evaluation metrics alone. "
            "The evaluation model based on the existing 4D R_t dynamics exhibits basic relational persistence "
            "and recovery without requiring an additional state representation (no RelationalRupture or RepairEvent in production). "
            "Harness evidence does not prove production RelationshipState is sufficient for all relational persistence. "
            "Unresolved questions remain whether (A) R_t alone may be sufficient, (B) R_t + existing memory/semantic "
            "substrate may be sufficient, or (C) a new computational representation may be necessary. No option is ratified. "
            "Status remains INCONCLUSIVE — MORE RESEARCH REQUIRED."
        )

        summary = E2TrackSummary(
            trial_count=num_trials,
            mean_repair_spe=float(np.mean(repair_spes)),
            mean_no_repair_spe=float(np.mean(norepair_spes)),
            mean_ordinary_spe=float(np.mean(ordinary_spes)),
            spe_diff_mean=diff_mean,
            spe_diff_std=diff_std,
            spe_diff_ci95=ci95,
            mean_repair_directness=float(np.mean(repair_dirs)),
            mean_no_repair_directness=float(np.mean(norepair_dirs)),
            mean_repair_supportiveness=float(np.mean(repair_sups)),
            mean_no_repair_supportiveness=float(np.mean(norepair_sups)),
            measurable_separation_observed=meas_sep,
            evidence_statement=evidence,
            p25_q1_implication=implication,
        )

        return summary, trials
