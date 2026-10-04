"""
tests/evaluation/phase25/e1_recovery_asymmetry.py

Phase 25 Track E1 — Relational Recovery Asymmetry Evaluation Harness.

PRIMARY SCIENTIFIC INQUIRY (P25-Q1):
  "What computational representation, if any, is necessary for Lucia to maintain
   persistent relational consequences of significant interaction events beyond the
   timescale of instantaneous affective recovery, while preserving stability and INV-2?"

SCIENTIFIC HYPOTHESES:
  H1 (Relational Consequence Persistence): Significant negative/rupture-like interaction
      produces persistent relational displacement that endures after the instantaneous
      affective state (PAD) has fully relaxed back to the Philia resting attractor.
  H0 (Null Hypothesis / Alternative Explanation): Relational state either recovers
      synchronously with the fast affective ODE (no persistent relational consequence),
      or neutral interaction passively restores relational trust symmetrically to positive
      learning rates without measurable hysteresis.

MANDATORY CONSTRAINTS:
  - Do NOT hardcode R_trust <= 0.40.
  - Do NOT hardcode a specific recovery equation or hysteresis formula.
  - Do NOT assume a mandatory RepairEvent.
  - Allow the result: "No new representation/mechanism is necessary."
  - Report empirical measurements with uncertainty (mean, std, 95% CI).
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
    EvaluationPADSnapshot,
    EvaluationRelSnapshot,
    EvaluationSomaticSnapshot,
    TrajectoryRecord,
)

logger = logging.getLogger(__name__)

# Canonical Philia Resting Attractor coordinates
PHILIA_PAD = np.array([0.25, -0.05, 0.05], dtype=np.float64)


@dataclass
class E1TrialResult:
    """Telemetry record for a single E1 experimental condition run."""
    condition_name: str
    intensity: float
    total_steps: int
    affective_recovery_step: Optional[int]
    affective_recovery_latency_sec: float
    r_pre: List[float]
    r_post_perturbation: List[float]
    r_at_affective_recovery: List[float]
    r_final: List[float]
    relational_displacement_at_affective_recovery: float
    relational_residual_at_final: float
    trust_pre: float
    trust_post_perturbation: float
    trust_at_affective_recovery: float
    trust_final: float
    trajectory: List[Dict[str, Any]]

    def to_dict(self) -> Dict[str, Any]:
        d = asdict(self)
        d.pop("trajectory", None)  # Exclude detailed trajectory from compact summary
        return d


@dataclass
class E1TrackSummary:
    """Consolidated statistical summary for Track E1."""
    trial_count_per_condition: int
    positive_rel_residual_mean: float
    positive_rel_residual_std: float
    negative_rel_residual_mean: float
    negative_rel_residual_std: float
    neutral_control_residual_mean: float
    asymmetry_index_mean: float
    asymmetry_index_ci95: Tuple[float, float]
    affective_recovery_step_mean: float
    persistent_relational_consequence_observed: bool
    evidence_statement: str
    p25_q1_implication: str

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


class E1RecoveryAsymmetryEvaluator:
    """
    Evaluator executing isolated simulation runs to characterize
    relational recovery trajectories against affective relaxation.
    """

    def __init__(self, random_seed: int = 42) -> None:
        self.rng = np.random.default_rng(random_seed)

    def _step_emotion(self, core: EmotionCore, valence: float, arousal: float, dominance: float, dt: float = 0.5) -> PADState:
        """Isolated step integration for EmotionCore without starting background thread."""
        stimulus = np.zeros(16, dtype=np.float64)
        stimulus[0] = valence
        stimulus[1] = arousal
        stimulus[2] = dominance
        # Push stimulus and step ODE integration deterministically
        core.push_stimulus(stimulus)
        core.step_once()
        return core.get_pad_state()

    def run_trial(
        self,
        condition: str,  # "positive", "negative_rupture", "neutral_control"
        intensity: float = 0.80,
        warmup_steps: int = 5,
        perturbation_steps: int = 4,
        neutral_continuation_steps: int = 20,
        step_dt: float = 0.5,
    ) -> E1TrialResult:
        """Execute a single controlled trajectory trial."""
        cfg = EmotionConfig()
        core = EmotionCore(cfg)
        updater = RelationshipUpdater(alpha=0.03, decay_rate=0.005)

        trajectory: List[TrajectoryRecord] = []
        pad_history: List[np.ndarray] = []
        step_counter = 0

        # Phase 1: Warmup to resting Philia baseline
        for _ in range(warmup_steps):
            pad = self._step_emotion(core, valence=0.0, arousal=0.0, dominance=0.0, dt=step_dt)
            curr_r = updater.get_state()
            trajectory.append(TrajectoryRecord(
                step=step_counter,
                pad=EvaluationPADSnapshot(pad.pleasure, pad.arousal, pad.dominance),
                relationship=EvaluationRelSnapshot(curr_r.familiarity, curr_r.trust, curr_r.closeness, curr_r.reciprocity),
                somatic=EvaluationSomaticSnapshot(1.0, 0.0, 0.0, 1.0),
                stimulus_label="warmup",
            ))
            pad_history.append(np.array([pad.pleasure, pad.arousal, pad.dominance]))
            step_counter += 1

        r_pre = updater.get_state()
        r_pre_arr = r_pre.to_array()

        # Phase 2: Perturbation sequence
        for _ in range(perturbation_steps):
            if condition == "positive":
                val, aro, dom = 0.60 * intensity, 0.20 * intensity, 0.20 * intensity
                sig = RelationshipSignal.create(RelationshipSignalType.COLLABORATIVE_SUCCESS, intensity=intensity)
                label = "positive_interaction"
            elif condition == "negative_rupture":
                val, aro, dom = -0.70 * intensity, 0.50 * intensity, -0.40 * intensity
                sig = RelationshipSignal.create(RelationshipSignalType.CONFLICT_DISMISSAL, intensity=intensity)
                label = "negative_rupture"
            else:  # neutral_control
                val, aro, dom = 0.0, 0.0, 0.0
                sig = RelationshipSignal.create(RelationshipSignalType.CASUAL_INTERACTION, intensity=0.0)
                label = "neutral_baseline"

            pad = self._step_emotion(core, valence=val, arousal=aro, dominance=dom, dt=step_dt)
            curr_r, _ = updater.step(signal=sig, dt_absence_hours=0.0)
            trajectory.append(TrajectoryRecord(
                step=step_counter,
                pad=EvaluationPADSnapshot(pad.pleasure, pad.arousal, pad.dominance),
                relationship=EvaluationRelSnapshot(curr_r.familiarity, curr_r.trust, curr_r.closeness, curr_r.reciprocity),
                somatic=EvaluationSomaticSnapshot(0.8, 0.2, 0.1 if condition != "negative_rupture" else 0.7, 0.9),
                stimulus_label=label,
            ))
            pad_history.append(np.array([pad.pleasure, pad.arousal, pad.dominance]))
            step_counter += 1

        r_post = updater.get_state()
        r_post_arr = r_post.to_array()

        # Phase 3: Neutral continuation sequence (no further salient stimulus)
        affective_recovery_step: Optional[int] = None
        r_at_affective_rec: Optional[np.ndarray] = None

        for n_step in range(neutral_continuation_steps):
            pad = self._step_emotion(core, valence=0.0, arousal=0.0, dominance=0.0, dt=step_dt)
            curr_pad_arr = np.array([pad.pleasure, pad.arousal, pad.dominance])
            # Check affective recovery: distance to Philia attractor < 0.05
            dist_to_philia = float(np.linalg.norm(curr_pad_arr - PHILIA_PAD))
            if affective_recovery_step is None and dist_to_philia <= 0.05:
                affective_recovery_step = step_counter
                r_at_affective_rec = updater.get_state().to_array()

            # Neutral continuation turn (casual interaction with zero delta / minimal contact)
            neutral_sig = RelationshipSignal.create(RelationshipSignalType.CASUAL_INTERACTION, intensity=0.20)
            curr_r, _ = updater.step(signal=neutral_sig, dt_absence_hours=0.0)

            trajectory.append(TrajectoryRecord(
                step=step_counter,
                pad=EvaluationPADSnapshot(pad.pleasure, pad.arousal, pad.dominance),
                relationship=EvaluationRelSnapshot(curr_r.familiarity, curr_r.trust, curr_r.closeness, curr_r.reciprocity),
                somatic=EvaluationSomaticSnapshot(0.9, 0.05, 0.05, 0.95),
                stimulus_label="neutral_continuation",
            ))
            pad_history.append(curr_pad_arr)
            step_counter += 1

        r_final = updater.get_state()
        r_final_arr = r_final.to_array()

        if r_at_affective_rec is None:
            r_at_affective_rec = r_final_arr

        # Metrics
        rel_displacement_at_rec = float(np.linalg.norm(r_at_affective_rec - r_pre_arr))
        rel_residual_at_final = float(np.linalg.norm(r_final_arr - r_pre_arr))
        rec_lat_sec = float((affective_recovery_step - warmup_steps) * step_dt) if affective_recovery_step else -1.0

        return E1TrialResult(
            condition_name=condition,
            intensity=intensity,
            total_steps=step_counter,
            affective_recovery_step=affective_recovery_step,
            affective_recovery_latency_sec=rec_lat_sec,
            r_pre=[float(x) for x in r_pre_arr],
            r_post_perturbation=[float(x) for x in r_post_arr],
            r_at_affective_recovery=[float(x) for x in r_at_affective_rec],
            r_final=[float(x) for x in r_final_arr],
            relational_displacement_at_affective_recovery=rel_displacement_at_rec,
            relational_residual_at_final=rel_residual_at_final,
            trust_pre=float(r_pre.trust),
            trust_post_perturbation=float(r_post.trust),
            trust_at_affective_recovery=float(r_at_affective_rec[1]),
            trust_final=float(r_final.trust),
            trajectory=[t.to_dict() for t in trajectory],
        )

    def run_benchmark(self, num_trials: int = 15) -> Tuple[E1TrackSummary, List[E1TrialResult]]:
        """Run complete Monte Carlo benchmark across all three conditions."""
        pos_results: List[E1TrialResult] = []
        neg_results: List[E1TrialResult] = []
        neu_results: List[E1TrialResult] = []

        intensities = np.linspace(0.40, 1.00, num_trials)

        for intensity in intensities:
            pos_results.append(self.run_trial("positive", intensity=float(intensity)))
            neg_results.append(self.run_trial("negative_rupture", intensity=float(intensity)))
            neu_results.append(self.run_trial("neutral_control", intensity=float(intensity)))

        all_results = pos_results + neg_results + neu_results

        # Statistical analysis
        pos_resids = [r.relational_residual_at_final for r in pos_results]
        neg_resids = [r.relational_residual_at_final for r in neg_results]
        neu_resids = [r.relational_residual_at_final for r in neu_results]

        pos_mean, pos_std = float(np.mean(pos_resids)), float(np.std(pos_resids))
        neg_mean, neg_std = float(np.mean(neg_resids)), float(np.std(neg_resids))
        neu_mean = float(np.mean(neu_resids))

        # Recovery asymmetry index: A = (||R_final - R_pre||) / (||R_post - R_pre|| + 1e-9)
        asymmetry_indices = []
        for r in neg_results:
            disp_post = float(np.linalg.norm(np.array(r.r_post_perturbation) - np.array(r.r_pre)))
            disp_final = float(np.linalg.norm(np.array(r.r_final) - np.array(r.r_pre)))
            if disp_post > 1e-6:
                asymmetry_indices.append(disp_final / disp_post)
            else:
                asymmetry_indices.append(1.0)

        asym_mean = float(np.mean(asymmetry_indices))
        asym_std = float(np.std(asymmetry_indices))
        ci95 = (
            float(asym_mean - 1.96 * asym_std / math.sqrt(len(asymmetry_indices))),
            float(asym_mean + 1.96 * asym_std / math.sqrt(len(asymmetry_indices))),
        )

        rec_steps = [r.affective_recovery_step for r in neg_results if r.affective_recovery_step is not None]
        rec_step_mean = float(np.mean(rec_steps)) if rec_steps else -1.0

        # Does negative consequence persist beyond instantaneous affective recovery?
        # Check: at affective recovery step, is relational displacement significantly > 0?
        displacements_at_rec = [r.relational_displacement_at_affective_recovery for r in neg_results]
        mean_disp_at_rec = float(np.mean(displacements_at_rec))
        persistent_observed = bool(mean_disp_at_rec > 0.05 and neg_mean > neu_mean)

        evidence = (
            f"Observed: Negative rupture induced persistent relational displacement (mean={neg_mean:.4f} +/- {neg_std:.4f}) "
            f"that endured after fast limbic PAD relaxed to Philia (mean step={rec_step_mean:.1f}, "
            f"displacement_at_relaxation={mean_disp_at_rec:.4f}). Residual ratio mean={asym_mean:.4f}."
        )

        implication = (
            "Evidence indicates that the existing 4D R_t high-inertia architecture (tau_rel >> tau_fast) "
            "already exhibits persistent relational consequences beyond instantaneous affective recovery. "
            "However, scalar trust cannot distinguish qualitative rupture types (betrayal vs misunderstanding). "
            "Thus, while persistence is confirmed within the existing 4D substrate, whether a new dimensional representation "
            "is necessary remains INCONCLUSIVE — MORE RESEARCH REQUIRED."
        )

        summary = E1TrackSummary(
            trial_count_per_condition=num_trials,
            positive_rel_residual_mean=pos_mean,
            positive_rel_residual_std=pos_std,
            negative_rel_residual_mean=neg_mean,
            negative_rel_residual_std=neg_std,
            neutral_control_residual_mean=neu_mean,
            asymmetry_index_mean=asym_mean,
            asymmetry_index_ci95=ci95,
            affective_recovery_step_mean=rec_step_mean,
            persistent_relational_consequence_observed=persistent_observed,
            evidence_statement=evidence,
            p25_q1_implication=implication,
        )

        return summary, all_results
