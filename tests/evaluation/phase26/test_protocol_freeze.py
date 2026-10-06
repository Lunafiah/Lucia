"""
tests/evaluation/phase26/test_protocol_freeze.py

Verification suite for P26 Experimental Design Freeze & Protocol Validation.
Confirms integrity of operational estimands, preregistration schema, SDE planning,
controls matrix, and decision boundary rules.
"""

from __future__ import annotations

import pytest

from tests.evaluation.phase26.protocol_freeze import (
    Blocker3ChaosReference,
    ClaimID,
    DecisionEvaluator,
    DecisionVerdict,
    EffectSizeTaxonomy,
    ESTIMAND_C1,
    ESTIMAND_C2,
    ESTIMAND_C3,
    FROZEN_CONTROLS_LEDGER,
    FROZEN_DOMAINS,
    InstrumentSensitivityPlan,
    ObservationWindowConfig,
    PreregistrationSpec,
    SubstrateBaselineReference,
    create_canonical_p26_preregistration,
)


def test_frozen_estimands_completeness():
    """Confirms C1, C2, and C3 estimands are mathematically and operationally specified."""
    assert ESTIMAND_C1.claim_id == ClaimID.C1_HISTORY_DEPENDENCE
    assert ESTIMAND_C2.claim_id == ClaimID.C2_MATCHED_EXPOSURE_DIFFERENTIATION
    assert ESTIMAND_C3.claim_id == ClaimID.C3_HISTORY_ENDOGENEITY

    assert "H_active" in ESTIMAND_C1.mathematical_definition
    assert "||P_A - P_B||_TV" in ESTIMAND_C2.mathematical_definition
    assert "D_eval" in ESTIMAND_C2.mathematical_definition
    assert "STRICTLY PROHIBITED" in ESTIMAND_C2.interpretation_boundary
    
    # Downstream C3 estimand checks
    assert "Y_{K+tau}" in ESTIMAND_C3.mathematical_definition
    assert "H_yoked" in ESTIMAND_C3.mathematical_definition
    assert "downstream" in ESTIMAND_C3.target_quantity.lower()
    assert "Does NOT evaluate replayed actions during induction" in ESTIMAND_C3.interpretation_boundary


def test_effect_size_taxonomy_distinction():
    """Confirms clear separation between SDE, SOI, ROPE, and hypothesis threshold."""
    taxonomy = EffectSizeTaxonomy()
    assert taxonomy.sde_planning_n120 == 0.1000
    assert taxonomy.sde_planning_n24 == 0.2235
    assert taxonomy.planning_delta == 0.1000
    assert taxonomy.soi_status == "TBD / NOT YET INDEPENDENTLY JUSTIFIED"
    assert taxonomy.soi_substantive_value is None
    assert taxonomy.rope_status == "TBD / NOT YET INDEPENDENTLY JUSTIFIED"
    assert taxonomy.rope_margin is None
    assert taxonomy.hypothesis_target == "PLANNING_DELTA_BENCHMARK"
    assert "STRICTLY AN INSTRUMENT-CALIBRATED PLANNING QUANTITY" in taxonomy.justification_boundary
    assert "NOT a substantive Smallest Effect of Interest" in taxonomy.justification_boundary


def test_blocker3_chaos_reference_provenance():
    """Validates exact numerical provenance of Blocker 3 config-specific chaos reference envelope."""
    ref = Blocker3ChaosReference()
    assert abs(ref.mean_peak_ratio - 0.130451) < 1e-6
    assert abs(ref.p95_peak_ratio - 0.173208) < 1e-6
    assert abs(ref.max_peak_ratio - 0.178920) < 1e-6
    assert ref.tested_horizon_ticks == 50
    assert ref.tested_seed_count == 5


def test_substrate_baseline_audit():
    """Validates audit of Step 3 baseline as transported descriptive reference, not condition-matched."""
    audit = SubstrateBaselineReference()
    assert audit.is_condition_matched_to_standard is False
    assert audit.step3_total_trials == 24
    assert audit.step3_standard_trials == 8
    assert "TRANSPORTED DESCRIPTIVE REFERENCE" in audit.audit_finding
    assert "MUST evaluate a concurrent unconditioned baseline cell" in audit.audit_finding


def test_sample_size_and_sde_planning():
    """Validates SDE calculation grounded in empirical Step 5 yields."""
    plan = InstrumentSensitivityPlan()
    feasibility = plan.evaluate_feasibility()

    # Pilot N=24 at low yield has large SDE (~0.22 - 0.28)
    sde_n24 = feasibility["step5_pilot_N24_sde"]
    assert sde_n24 > 0.20

    # Planned N=120 on standard format resolves subtle effects (~0.10)
    sde_n120 = feasibility["planned_standard_N120_sde"]
    assert sde_n120 < sde_n24
    assert abs(sde_n120 - 0.1000) < 0.005

    # Planned N=240 scales further
    sde_n240 = feasibility["planned_scaled_N240_sde"]
    assert sde_n240 < sde_n120

    assert "INSTRUMENT-CALIBRATED" in feasibility["epistemic_warning"]


def test_observation_window_config():
    """Validates observation window delays for distinguishing persistence from transient priming."""
    cfg = ObservationWindowConfig()
    assert len(cfg.branches) == 3
    assert cfg.branches[0].lag_id == "TAU_0_IMMEDIATE"
    assert cfg.branches[0].tau_ticks == 0
    assert cfg.branches[0].delay_virtual_time_sec == 0.0
    assert cfg.branches[0].requires_snapshot_fork is True
    assert cfg.branches[0].single_probe_only is True

    assert cfg.branches[1].lag_id == "TAU_5_WASHOUT"
    assert cfg.branches[1].tau_ticks == 5
    assert cfg.branches[1].delay_virtual_time_sec == 1.0
    assert cfg.branches[1].requires_snapshot_fork is True
    assert cfg.branches[1].single_probe_only is True

    assert cfg.branches[2].lag_id == "TAU_20_EXTENDED"
    assert cfg.branches[2].tau_ticks == 20
    assert cfg.branches[2].delay_virtual_time_sec == 4.0
    assert cfg.branches[2].requires_snapshot_fork is True
    assert cfg.branches[2].single_probe_only is True

    assert cfg.philia_decay_tolerance == 0.05


def test_frozen_controls_ledger_completeness():
    """Validates that all 7 required confounds have explicit frozen controls."""
    control_ids = {c.control_id for c in FROZEN_CONTROLS_LEDGER}
    expected = {
        "CTRL_EXPOSURE_RECENCY",
        "CTRL_ANTI_SYCOPHANCY",
        "CTRL_AFFECT_RELATIONSHIP",
        "CTRL_SUBSTRATE_BASELINE",
        "CTRL_DYNAMIC_CHAOS",
        "CTRL_POSITIVE_SENSITIVITY",
        "CTRL_NEGATIVE_NULL",
    }
    assert control_ids == expected
    for c in FROZEN_CONTROLS_LEDGER:
        assert len(c.mechanism) > 10
        assert len(c.success_criterion) > 10


def test_evaluative_domains_and_held_out_probes():
    """Validates separation of active domains from held-out unseen domains."""
    active = FROZEN_DOMAINS["ACTIVE_DOMAINS"]
    held_out = FROZEN_DOMAINS["HELD_OUT_DOMAINS"]

    assert len(active) >= 2
    assert len(held_out) >= 2

    active_names = {d.domain_id for d in active}
    held_out_names = {d.domain_id for d in held_out}

    assert "INFORMATION_FORAGING" in active_names
    assert "TASK_STRATEGY" in active_names
    assert "COGNITIVE_EXPLORATION" in held_out_names
    assert "COLLABORATION_STYLE" in held_out_names

    # Zero overlap
    assert len(active_names.intersection(held_out_names)) == 0


def test_canonical_preregistration_spec_integrity():
    """Validates preregistration schema instantiation and cryptographic provenance hash."""
    prereg = create_canonical_p26_preregistration()
    assert prereg.spec_version == "P26_PREREG_v1.0"
    assert "H1_HistoryDependence" in prereg.hypotheses
    assert "H2_MatchedExposureDifferentiation" in prereg.hypotheses
    assert "H3_HistoryEndogeneity" in prereg.hypotheses

    assert len(prereg.exclusion_criteria) >= 4
    assert len(prereg.stopping_rules) >= 2
    assert prereg.provenance_hash is not None
    assert len(prereg.provenance_hash) == 64

    # Tampering test
    orig_hash = prereg.provenance_hash
    prereg.hypotheses["H1_HistoryDependence"] = "Tampered text"
    assert prereg.compute_provenance_hash() != orig_hash


def test_decision_evaluator_positive():
    """Tests POSITIVE decision rule when effect is bounded outside planning delta."""
    # Point estimate 0.25, CI [0.15, 0.35], planning_delta 0.10
    verdict, rationale = DecisionEvaluator.evaluate_claim(
        point_estimate=0.25,
        ci_lower=0.15,
        ci_upper=0.35,
        planning_delta=0.10,
    )
    assert verdict == DecisionVerdict.POSITIVE
    assert "Substantive SOI remains TBD" in rationale


def test_decision_evaluator_negative():
    """Tests NEGATIVE decision rule when CI is strictly bounded within [-delta, +delta]."""
    # Point estimate 0.02, CI [-0.04, +0.06], planning_delta 0.10
    verdict, rationale = DecisionEvaluator.evaluate_claim(
        point_estimate=0.02,
        ci_lower=-0.04,
        ci_upper=0.06,
        planning_delta=0.10,
    )
    assert verdict == DecisionVerdict.NEGATIVE
    assert "Substantive ROPE remains TBD" in rationale


def test_decision_evaluator_inconclusive_spans_boundary():
    """Tests INCONCLUSIVE decision rule when CI spans boundary (insufficient power)."""
    # Point estimate 0.12, CI [0.02, 0.22], planning_delta 0.10
    # ci_lower is NOT > 0.10, and ci_upper is NOT <= 0.10
    verdict, rationale = DecisionEvaluator.evaluate_claim(
        point_estimate=0.12,
        ci_lower=0.02,
        ci_upper=0.22,
        planning_delta=0.10,
    )
    assert verdict == DecisionVerdict.INCONCLUSIVE
    assert "UNKNOWN" in rationale
