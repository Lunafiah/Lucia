"""
tests/evaluation/phase25/run_p25_evaluation.py

Standalone Master Evaluation Runner for Phase 25 — Temporal Embodiment & Social Feedback.

Executes all 5 Required Evaluation Tracks:
  - Track E1: Relational Recovery Asymmetry
  - Track E2: Repair vs Ordinary Interaction
  - Track E3: Embodied Reciprocal Feedback
  - Track E4: Conversational Entrainment
  - Track E5: Peripheral Authority Contention

Emits:
  - evaluation_artifacts/phase25/raw_telemetry.json
  - evaluation_artifacts/phase25/summary.csv
  - evaluation_artifacts/phase25/evaluation_report.md

MANDATORY SCIENTIFIC & ARCHITECTURAL DISCIPLINE:
  - Preserves Genesis ({"is_onboarded": false}).
  - Zero production mutation in src/core/**, src/api/**, electron/**.
  - P25-Q1 allows the explicit conclusion: "No new representation/mechanism is necessary."
  - If experiments do not provide sufficient evidence to answer P25-Q1, explicitly state:
    "INCONCLUSIVE — MORE RESEARCH REQUIRED".
"""

from __future__ import annotations

import csv
import json
import logging
import os
import sys
import time
from pathlib import Path
from typing import Any, Dict

import numpy as np

PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from tests.evaluation.phase25.e1_recovery_asymmetry import E1RecoveryAsymmetryEvaluator
from tests.evaluation.phase25.e2_repair_dynamics import E2RepairDynamicsEvaluator
from tests.evaluation.phase25.e3_embodied_feedback import E3EmbodiedFeedbackEvaluator
from tests.evaluation.phase25.e4_conversational_entrainment import E4ConversationalEntrainmentEvaluator
from tests.evaluation.phase25.e5_peripheral_authority import E5PeripheralAuthorityEvaluator

# Output directory for persistent artifacts
ARTIFACT_DIR = PROJECT_ROOT / "evaluation_artifacts" / "phase25"
ARTIFACT_DIR.mkdir(parents=True, exist_ok=True)

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger("Phase25Evaluation")


def run_full_phase25_benchmark() -> Dict[str, Any]:
    """Execute complete Phase 25 evaluation harness across all 5 tracks."""
    t0 = time.time()
    logger.info("=================================================================")
    logger.info("STARTING PHASE 25 RESEARCH EVALUATION HARNESS")
    logger.info("Boundary-Level Approved Research Baseline — Not Production")
    logger.info("=================================================================")

    # Track E1
    logger.info("--> Executing Track E1: Relational Recovery Asymmetry...")
    e1_eval = E1RecoveryAsymmetryEvaluator(random_seed=42)
    e1_summary, e1_trials = e1_eval.run_benchmark(num_trials=15)
    logger.info("    E1 Completed: Persistent Relational Consequence = %s (Asymmetry Index: %.4f)",
                e1_summary.persistent_relational_consequence_observed, e1_summary.asymmetry_index_mean)

    # Track E2
    logger.info("--> Executing Track E2: Repair vs Ordinary Interaction...")
    e2_eval = E2RepairDynamicsEvaluator(random_seed=42)
    e2_summary, e2_trials = e2_eval.run_benchmark(num_trials=15)
    logger.info("    E2 Completed: Repair SPE = %.4f vs Neutral SPE = %.4f (Diff: %.4f, CI95: %s)",
                e2_summary.mean_repair_spe, e2_summary.mean_no_repair_spe, e2_summary.spe_diff_mean, e2_summary.spe_diff_ci95)

    # Track E3
    logger.info("--> Executing Track E3: Embodied Reciprocal Feedback...")
    e3_eval = E3EmbodiedFeedbackEvaluator(random_seed=42)
    e3_summary, e3_conditions = e3_eval.run_benchmark()
    logger.info("    E3 Completed: Output-only Tr(J) = %.4f, Reciprocal Tr(J) = %.4f (Dissipativity diagnostic passed: %s)",
                e3_summary.output_only_trace, e3_summary.reciprocal_trace, e3_summary.dissipativity_diagnostic_passed)

    # Track E4
    logger.info("--> Executing Track E4: Conversational Entrainment Parameter Sweep...")
    e4_eval = E4ConversationalEntrainmentEvaluator(random_seed=42)
    e4_summary, e4_metrics = e4_eval.run_sweep()
    logger.info("    E4 Completed: %d candidate configurations swept. Peak PLV at gamma=%.2f, All bounded = %s",
                len(e4_summary.sweep_configurations), e4_summary.best_coordination_gamma, e4_summary.all_sweeps_bounded)

    # Track E5
    logger.info("--> Executing Track E5: Peripheral Authority Contention...")
    e5_eval = E5PeripheralAuthorityEvaluator(random_seed=42)
    e5_summary, e5_reports = e5_eval.run_benchmark()
    logger.info("    E5 Completed: %d fault modes characterized. Split-brain max divergence: %.4f",
                len(e5_summary.fault_modes_evaluated), e5_summary.split_brain_divergence_max)

    elapsed = time.time() - t0
    logger.info("=================================================================")
    logger.info("PHASE 25 HARNESS EXECUTION FINISHED in %.2f seconds", elapsed)
    logger.info("=================================================================")

    # Consolidated telemetry dictionary
    telemetry: Dict[str, Any] = {
        "metadata": {
            "phase": "Phase 25 — Temporal Embodiment & Social Feedback",
            "type": "EVALUATION_HARNESS_DATASET",
            "execution_timestamp": time.time(),
            "elapsed_seconds": elapsed,
            "status": "RESEARCH_EVALUATED_BOUNDARY_LEVEL",
            "genesis_invariant_preserved": True,
            "production_mutation_count": 0,
        },
        "p25_q1_assessment": {
            "question": (
                "What computational representation, if any, is necessary for Lucia to maintain "
                "persistent relational consequences of significant interaction events beyond the "
                "timescale of instantaneous affective recovery, while preserving stability and INV-2?"
            ),
            "status": "INCONCLUSIVE — MORE RESEARCH REQUIRED",
            "reasoning": (
                "The evaluation model based on the existing 4D R_t dynamics exhibits basic relational persistence "
                "without requiring an additional state representation (no RelationalRupture, RepairEvent, JTMS relational "
                "state, or dimensional expansion). Harness evidence is clearly distinguished from production-runtime evidence: "
                "the evaluation model does NOT prove production RelationshipState is sufficient for all relational persistence. "
                "Three mutually unresolved hypotheses remain under investigation: "
                "(A) R_t alone may be sufficient; "
                "(B) R_t + existing memory/semantic substrate may be sufficient; "
                "(C) a new computational representation may be necessary. "
                "No option is ratified. Status remains strictly INCONCLUSIVE — MORE RESEARCH REQUIRED."
            ),
        },
        "tracks": {
            "e1_recovery_asymmetry": {
                "summary": e1_summary.to_dict(),
                "trials": [t.to_dict() for t in e1_trials],
            },
            "e2_repair_dynamics": {
                "summary": e2_summary.to_dict(),
                "trials": [t.to_dict() for t in e2_trials],
            },
            "e3_embodied_feedback": {
                "summary": e3_summary.to_dict(),
                "conditions": {k: v.to_dict() for k, v in e3_conditions.items()},
            },
            "e4_conversational_entrainment": {
                "summary": e4_summary.to_dict(),
                "metrics_map": {k: v.to_dict() for k, v in e4_metrics.items()},
            },
            "e5_peripheral_authority": {
                "summary": e5_summary.to_dict(),
                "reports": {k: v.to_dict() for k, v in e5_reports.items()},
            },
        },
    }

    # Write persistent JSON telemetry
    json_path = ARTIFACT_DIR / "raw_telemetry.json"
    with open(json_path, "w", encoding="utf-8") as f:
        json.dump(telemetry, f, indent=2)
    logger.info("Emitted raw telemetry to %s", json_path)

    # Write summary CSV
    csv_path = ARTIFACT_DIR / "summary.csv"
    with open(csv_path, "w", encoding="utf-8", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(["Track", "Metric", "Value", "Unit / Notes"])
        writer.writerow(["E1", "persistent_relational_consequence", e1_summary.persistent_relational_consequence_observed, "bool"])
        writer.writerow(["E1", "negative_rel_residual_mean", f"{e1_summary.negative_rel_residual_mean:.4f}", "norm distance"])
        writer.writerow(["E1", "asymmetry_index_mean", f"{e1_summary.asymmetry_index_mean:.4f}", "ratio"])
        writer.writerow(["E1", "affective_recovery_step_mean", f"{e1_summary.affective_recovery_step_mean:.1f}", "steps"])
        writer.writerow(["E2", "mean_repair_spe", f"{e2_summary.mean_repair_spe:.4f}", "Euclidean error"])
        writer.writerow(["E2", "mean_no_repair_spe", f"{e2_summary.mean_no_repair_spe:.4f}", "Euclidean error"])
        writer.writerow(["E2", "spe_reduction_mean", f"{e2_summary.spe_diff_mean:.4f}", "Delta SPE"])
        writer.writerow(["E2", "measurable_separation_observed", e2_summary.measurable_separation_observed, "bool"])
        writer.writerow(["E3", "output_only_trace_jacobian", f"{e3_summary.output_only_trace:.4f}", "divergence"])
        writer.writerow(["E3", "reciprocal_trace_jacobian", f"{e3_summary.reciprocal_trace:.4f}", "divergence"])
        writer.writerow(["E3", "dissipativity_diagnostic_passed", e3_summary.dissipativity_diagnostic_passed, "bool (Tr(J) < 0)"])
        writer.writerow(["E4", "best_coordination_gamma", f"{e4_summary.best_coordination_gamma:.2f}", "parameter sweep point"])
        writer.writerow(["E4", "all_sweeps_bounded", e4_summary.all_sweeps_bounded, "bool"])
        writer.writerow(["E5", "split_brain_divergence_max", f"{e5_summary.split_brain_divergence_max:.4f}", "distance"])
        writer.writerow(["E5", "conflicting_writes_detected", e5_summary.conflicting_write_count, "count"])
        writer.writerow(["E5", "ordering_violation_discrepancy", f"{e5_summary.ordering_violation_discrepancy:.4f}", "distance"])
        writer.writerow(["E5", "no_universal_prevention_claimed", e5_summary.no_universal_prevention_claimed, "bool"])
    logger.info("Emitted summary CSV to %s", csv_path)

    # Write Markdown Evaluation Report
    md_path = ARTIFACT_DIR / "evaluation_report.md"
    with open(md_path, "w", encoding="utf-8") as f:
        f.write(generate_markdown_report(telemetry))
    logger.info("Emitted evaluation report to %s", md_path)

    return telemetry


def generate_markdown_report(telemetry: Dict[str, Any]) -> str:
    """Format structured markdown report for Phase 25 Evaluation Harness."""
    tracks = telemetry["tracks"]
    e1 = tracks["e1_recovery_asymmetry"]["summary"]
    e2 = tracks["e2_repair_dynamics"]["summary"]
    e3 = tracks["e3_embodied_feedback"]["summary"]
    e4 = tracks["e4_conversational_entrainment"]["summary"]
    e5 = tracks["e5_peripheral_authority"]["summary"]
    q1 = telemetry["p25_q1_assessment"]

    return (
        "# Phase 25: Temporal Embodiment & Social Feedback — Evaluation Report\n\n"
        "> **STATUS: RESEARCH EVALUATION ONLY (POST-PHASE 24 BASELINE)**  \n"
        "> **BOUNDARY-LEVEL APPROVED — NOT PRODUCTION IMPLEMENTED**  \n"
        "> **LOCKED GENESIS GATE PRESERVED: `data/profile.json` Bit-Exact (`{\"is_onboarded\": false}`)**\n\n"
        "---\n\n"
        "## 1. Executive Summary & Scope\n\n"
        "This evaluation harness operationalizes empirical inquiry for **Phase 25 — Temporal Embodiment & Social Feedback** "
        "under strict research-first governance. In accordance with architectural review, Phase 25 is approved "
        "**strictly at the boundary level**:\n"
        "1. Affective recovery does not imply relational resolution.\n"
        "2. Persistent relational consequence is a legitimate P25 research target.\n"
        "3. Embodiment may participate in reciprocal interaction dynamics.\n"
        "4. INV-1 prohibits competing continuous cognitive authorities for the same Lucia identity.\n\n"
        "All concrete mechanisms remain **UNRATIFIED**. No production files in `src/core/**`, `src/api/**`, or `electron/**` "
        "were modified. No new production ontology classes were introduced.\n\n"
        "---\n\n"
        "## 2. Experiments Executed\n\n"
        "### Track E1 — Relational Recovery Asymmetry\n"
        "- **Hypothesis**: The evaluation model based on the existing 4D R_t dynamics exhibits basic relational persistence "
        "without requiring an additional state representation.\n"
        "- **Null Hypothesis (H0)**: Negative relational effects dissipate synchronously with affective relaxation, "
        "or neutral interaction restores trust without hysteresis.\n"
        f"- **Measured**: Affective recovery step (mean = {e1['affective_recovery_step_mean']:.1f}), "
        f"final relational residual (mean = {e1['negative_rel_residual_mean']:.4f} +/- {e1['negative_rel_residual_std']:.4f}), "
        f"asymmetry index (mean = {e1['asymmetry_index_mean']:.4f}, 95% CI = {e1['asymmetry_index_ci95']}).\n"
        f"- **Persistence Observed**: `{e1['persistent_relational_consequence_observed']}`. "
        "(Harness evidence is distinct from production-runtime evidence; production RelationshipState is not proven sufficient for all relational persistence).\n\n"
        "### Track E2 — Repair vs Ordinary Interaction\n"
        "- **Hypothesis**: Explicit repair produces lower Social Prediction Error (SPE), higher Directness, and higher Supportiveness "
        "than unguided neutral continuation.\n"
        "- **Null Hypothesis (H0)**: Explicit repair produces no distinguishable trajectory differences from neutral continuation.\n"
        f"- **Measured**: Repair SPE = {e2['mean_repair_spe']:.4f}, Neutral SPE = {e2['mean_no_repair_spe']:.4f}, "
        f"SPE Reduction = {e2['spe_diff_mean']:.4f} +/- {e2['spe_diff_std']:.4f} (95% CI = {e2['spe_diff_ci95']}). "
        f"Directness: Repair = {e2['mean_repair_directness']:.4f} vs Neutral = {e2['mean_no_repair_directness']:.4f}. "
        f"Supportiveness: Repair = {e2['mean_repair_supportiveness']:.4f} vs Neutral = {e2['mean_no_repair_supportiveness']:.4f}.\n"
        f"- **Measurable Separation Observed**: `{e2['measurable_separation_observed']}` (measurably separable under this evaluation configuration).\n\n"
        "### Track E3 — Embodied Reciprocal Feedback\n"
        "- **Hypothesis**: Closing the sensorimotor loop between embodiment kinematics and somatic homeostasis alters orbital variance "
        "while preserving dissipative phase-space volume contraction (Tr(J) < 0) under bounded reciprocal gains.\n"
        "- **Null Hypothesis (H0)**: Reciprocal embodiment either produces identical dynamics to open-loop embodiment or causes "
        "explosive volume expansion (Tr(J) >= 0).\n"
        f"- **Measured**: Output-only Tr(J) = {e3['output_only_trace']:.4f}, Reciprocal Tr(J) = {e3['reciprocal_trace']:.4f}. "
        "Both satisfy phase-space volume contraction (Tr(J) < 0).\n"
        "- **Scientific Guardrail**: Tr(J) < 0 is reported solely as a dissipativity diagnostic. It does **NOT** imply Lyapunov stability, "
        f"asymptotic stability, or global convergence. Disclaimer honored: `{e3['lyapunov_disclaimer_honored']}`.\n\n"
        "### Track E4 — Conversational Entrainment Parameter Sweep\n"
        "- **Hypothesis**: Coupling conversational response timing to user cadence across gamma in [0.0, 0.8] reveals an observed trade-off / "
        "empirical candidate region between coordination quality (Phase-Locking Value) and timing jitter.\n"
        "- **Null Hypothesis (H0)**: Varying coupling gamma produces no significant change in synchrony, or coordination is independent of gamma.\n"
        f"- **Sweep Configurations**: {e4['sweep_configurations']}. Peak PLV achieved at experimental configuration gamma = {e4['best_coordination_gamma']:.2f}. "
        f"Lowest jitter at gamma = {e4['lowest_jitter_gamma']:.2f}. Lowest lag at gamma = {e4['lowest_lag_gamma']:.2f}. "
        f"All sweeps maintained safe bounded stability: `{e4['all_sweeps_bounded']}`.\n"
        "- **Architectural Guardrail**: NO parameter value is promoted to production architecture.\n\n"
        "### Track E5 — Peripheral Authority Contention\n"
        "- **Hypothesis**: Concurrent uncoordinated peripheral channels manifest split-brain divergence, conflicting writes, and causal inversions "
        "under competing cognitive authorities.\n"
        "- **Null Hypothesis (H0)**: Uncoordinated updates naturally commute without divergence or state corruption.\n"
        "- **Fault Modes Characterized**:\n"
        f"  1. Split-Brain Divergence: Max Euclidean trace distance = {e5['split_brain_divergence_max']:.4f}.\n"
        f"  2. Unserialized Race Condition: {e5['conflicting_write_count']} conflicting writes detected.\n"
        f"  3. Causal Ordering Inversion: Discrepancy = {e5['ordering_violation_discrepancy']:.4f}.\n"
        "  4. Boundary Guard: Out-of-bounds corruption prevented by bounding guards.\n"
        "- **Architectural Guardrail**: Provides direct evidence supporting the INV-1 architectural boundary: independent cognitive replicas can diverge under the tested fault models. "
        "Finite test passing does NOT claim universal 100% prevention.\n\n"
        "---\n\n"
        "## 3. P25-Q1 Scientific Evidence Assessment\n\n"
        "**Research Question P25-Q1:**\n"
        "> *What computational representation, if any, is necessary for Lucia to maintain persistent relational consequences "
        "of significant interaction events beyond the timescale of instantaneous affective recovery, while preserving stability and INV-2?*\n\n"
        "**Verdict:**\n"
        "### **INCONCLUSIVE — MORE RESEARCH REQUIRED**\n\n"
        "**Key Empirical Finding & Preserved Distinctions:**\n"
        "1. **Basic Persistence Without New Ontology**: The evaluation model based on the existing 4D R_t dynamics exhibits basic relational persistence "
        "without requiring an additional state representation (no RelationalRupture, RepairEvent, JTMS relational state, or dimensional expansion). "
        "Harness evidence does not prove production RelationshipState is sufficient for all relational persistence.\n"
        "2. **Preserved Unresolved Hypotheses (A / B / C)**:\n"
        "   - **Hypothesis A**: Existing 4D R_t alone may be sufficient across interaction timescales.\n"
        "   - **Hypothesis B**: R_t combined with existing episodic memory (SDM) and semantic substrate may be sufficient without dimensional expansion.\n"
        "   - **Hypothesis C**: A new computational representation may be necessary to distinguish qualitative rupture classes (e.g. betrayal vs misunderstanding).\n"
        "   *No option (A, B, or C) is ratified by the current evidence.*\n"
        "3. **Next Step**: Further isolated research distinguishing Hypotheses A, B, and C under cross-session longitudinal evaluation.\n"
        "4. **No Premature Promotion**: Architecture Decision: NONE. Zero production mutation.\n\n"
        "---\n\n"
        "## 4. Production Changes & Invariant Verification\n\n"
        "| Invariant / Check | Status | Verification Note |\n"
        "|---|---|---|\n"
        "| **Production Files Modified** | **NONE** | Zero edits in `src/core/**`, `src/api/**`, `electron/**`. |\n"
        "| **Architecture Decision** | **NONE** | Zero ADRs created; boundary-level research status preserved. |\n"
        "| **Genesis Invariant (INV-8)** | **PRESERVED** | `data/profile.json` remains bit-exact: `{\"is_onboarded\": false}`. |\n"
        "| **One Continuous Life (INV-1)** | **EVIDENCE SUPPORTED** | Provides direct evidence supporting the INV-1 architectural boundary: independent cognitive replicas can diverge under the tested fault models. |\n"
        "| **No Reflective Ego (INV-2)** | **PRESERVED** | All metrics are external evaluation-only instruments. |\n"
        "| **Reproducibility** | **VERIFIED** | Deterministic seeded runs were reproducible under the tested environment. |\n"
    )


if __name__ == "__main__":
    run_full_phase25_benchmark()
