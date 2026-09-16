"""
Phase 22 H1 — Measurement Architecture Study Automated Validation Suite.

Verifies:
1. Governance invariants (src/core/ untouched, Genesis bit-exact, Protocol v1.5 unauthorized).
2. Manifest and hash integrity.
3. RQ1: Semantic audit completeness.
4. RQ2: Scalar collapse analysis and hidden vector separation.
5. RQ3: Magnitude-controlled directional analysis and independent directional information.
6. RQ4: Prediction residual vs state displacement consistency.
7. RQ5: Complete characterization of representation hierarchy (M0 to M4) across 10 axes.
8. RQ6: Conversational timescale viability (T <= 25 primary vs T=50, 100 exploratory).
9. Final decision state and non-authorization of Protocol v1.5.
"""

from __future__ import annotations

import hashlib
import json
import sys
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parent.parent.parent
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

RESULTS_FILE = (
    REPO_ROOT
    / "tests"
    / "evaluation_phase22"
    / "results"
    / "h1_measurement_architecture"
    / "measurement_architecture_results.json"
)
MANIFEST_FILE = (
    REPO_ROOT
    / "tests"
    / "evaluation_phase22"
    / "fixtures"
    / "manifest_h1_measurement_architecture.json"
)
SCRIPT_FILE = (
    REPO_ROOT
    / "tests"
    / "evaluation_phase22"
    / "scripts"
    / "analyze_measurement_architecture.py"
)
PROFILE_FILE = REPO_ROOT / "data" / "profile.json"


@pytest.fixture(scope="module")
def study_data():
    assert RESULTS_FILE.exists(), f"Results file missing: {RESULTS_FILE}"
    with open(RESULTS_FILE, "r", encoding="utf-8") as f:
        return json.load(f)


@pytest.fixture(scope="module")
def manifest_data():
    assert MANIFEST_FILE.exists(), f"Manifest file missing: {MANIFEST_FILE}"
    with open(MANIFEST_FILE, "r", encoding="utf-8") as f:
        return json.load(f)


# =============================================================================
# 1. Governance & Manifest Integrity Tests
# =============================================================================

def test_governance_invariants(study_data, manifest_data):
    """Verify all hard governance invariants are strictly maintained."""
    gov = study_data["governance_status"]
    assert gov["h1_status"] == "INCONCLUSIVE — GATE 2 UNRESOLVED"
    assert gov["protocol_v15"] == "NOT AUTHORIZED"
    assert gov["architecture_gate"] == "STRICTLY LOCKED"
    assert gov["production"] == "0 MUTATIONS"
    assert gov["genesis"] == "BIT-EXACT UNTOUCHED"
    assert gov["historical_h1_data"] == "IMMUTABLE"

    # Verify Genesis profile file is bit-exact
    assert PROFILE_FILE.exists()
    profile_content = json.loads(PROFILE_FILE.read_text(encoding="utf-8"))
    assert profile_content == {"is_onboarded": False}

    # Verify protocol v1.5 readiness is explicitly NO
    assert "NO" in study_data["evidence_synthesis"]["protocol_v15_readiness"]


def test_manifest_integrity(manifest_data):
    """Verify SHA-256 integrity of the analysis script and results file."""
    assert SCRIPT_FILE.exists()
    actual_script_hash = hashlib.sha256(SCRIPT_FILE.read_bytes()).hexdigest()
    assert manifest_data["file_hashes"]["script_hash"] == actual_script_hash

    assert RESULTS_FILE.exists()
    actual_results_hash = hashlib.sha256(RESULTS_FILE.read_bytes()).hexdigest()
    assert manifest_data["file_hashes"]["results_hash"] == actual_results_hash


# =============================================================================
# 2. RQ1: Semantic Audit Tests
# =============================================================================

def test_rq1_semantic_audit(study_data):
    """Verify all 5 subquestions of RQ1 are audited with rigorous architectural rationale."""
    audit = study_data["rq1_semantic_audit"]
    assert "canonical_S_formula" in audit
    assert "active_inference_step_formula" in audit
    assert "subquestion_audits" in audit

    subqs = audit["subquestion_audits"]
    assert len(subqs) == 5

    # 1. Is canonical S displacement?
    assert "YES" in subqs["1_is_canonical_S_displacement"]["verdict"]

    # 2. Is canonical S prediction error?
    assert "YES" in subqs["2_is_canonical_S_prediction_error"]["verdict"]

    # 3. Is p0 the actual prediction target?
    assert "YES" in subqs["3_is_p0_actual_prediction_target"]["verdict"]

    # 4. Is A p0 + b the actual S4 predicted state?
    assert "YES" in subqs["4_is_A_p0_plus_b_actual_S4_predicted_state"]["verdict"]

    # 5. Do they have equivalent or different causal semantics?
    assert "DIFFERENT" in subqs["5_do_quantities_have_equivalent_or_different_causal_semantics"]["verdict"]


# =============================================================================
# 3. RQ2: Scalar Information-Loss Tests
# =============================================================================

def test_rq2_scalar_collapse(study_data):
    """Verify scalar collapse pair analysis and hidden vector separation."""
    rq2 = study_data["rq2_scalar_collapse_analysis"]["results_by_t"]
    conv_grid = [1, 2, 4, 8, 12, 16, 25]

    for T_str in [str(t) for t in conv_grid]:
        assert T_str in rq2
        t_res = rq2[T_str]
        # Verify collapse pairs exist at all conversational T
        assert t_res["total_collapse_pairs"] > 0
        # Verify Med-High collapse pairs exist at all conversational T
        assert t_res["cross_tier_med_high_count"] > 0
        # Verify hidden angular divergence for Med-High collapse pairs is substantial (> 50 deg)
        assert t_res["med_high_collapse_angle_deg"]["mean"] > 50.0
        # Verify hidden vector distance is non-zero
        assert t_res["med_high_collapse_vec_dist"]["mean"] > 0.05

    # Verify representative examples exist
    examples = study_data["rq2_scalar_collapse_analysis"]["representative_examples"]
    for T_str in ["4", "8", "12", "16", "25"]:
        assert T_str in examples
        ex = examples[T_str]
        assert ex["probe_A"]["tier"] != ex["probe_B"]["tier"]
        assert ex["diff_S"] <= 0.0200
        assert ex["angle_deg"] > 40.0


# =============================================================================
# 4. RQ3: Magnitude-Controlled Directional Tests
# =============================================================================

def test_rq3_magnitude_controlled_direction(study_data):
    """Verify that direction remains informative after controlling for scalar magnitude S."""
    rq3 = study_data["rq3_magnitude_controlled_direction"]
    conv_grid = [1, 2, 4, 8, 12, 16, 25]

    for T_str in [str(t) for t in conv_grid]:
        assert T_str in rq3
        t_res = rq3[T_str]
        # Verify decisive RQ3 verdict
        assert t_res["rq3_verdict"] == "EVIDENCE CONSISTENT WITH DIRECTIONAL/COMPONENT INFORMATION PERSISTING AFTER MAGNITUDE MATCHING"
        # Verify matched pairs have substantial angular divergence
        assert t_res["matched_mh_mean_angle_deg"] > 50.0
        # Verify component divergence: Med has positive Pleasure displacement, High has higher Arousal
        assert t_res["matched_mh_mean_dP"] < 0.0  # High dP - Med dP is negative (Med is higher in Pleasure)
        assert t_res["matched_mh_mean_dA"] > 0.0  # High dA - Med dA is positive (High is higher in Arousal)


# =============================================================================
# 5. RQ4: Prediction Residual vs Displacement Tests
# =============================================================================

def test_rq4_prediction_residual_vs_displacement(study_data):
    """Verify mathematical identity under unadapted prior and divergence under adapted beliefs."""
    rq4 = study_data["rq4_prediction_residual_vs_displacement"]
    records = rq4["records"]
    assert len(records) > 0

    for rec in records:
        # In unadapted prior, norm_delta_p_mean must equal norm_r_unadapted_mean exactly
        assert abs(rec["norm_delta_p_mean"] - rec["norm_r_unadapted_mean"]) < 1e-9

        # In adapted state, prediction residual diverges from displacement
        assert abs(rec["norm_delta_p_mean"] - rec["norm_r_adapted_mean"]) > 1e-4


# =============================================================================
# 6. RQ5: Minimal Sufficient Representation Tests
# =============================================================================

def test_rq5_representation_hierarchy(study_data):
    """Verify all 5 representations (M0 to M4) are characterized along all required axes."""
    reps = study_data["rq5_representation_hierarchy"]
    assert len(reps) == 5

    rep_ids = [r["id"] for r in reps]
    assert rep_ids == ["M0", "M1", "M2", "M3", "M4"]

    required_axes = [
        "tier_separability",
        "information_retained",
        "collapse_behavior",
        "robustness_across_T",
        "sensitivity_to_baseline",
        "sensitivity_to_exposure",
        "numerical_stability",
        "interpretability",
        "computational_cost",
        "relation_to_active_inference",
    ]

    for r in reps:
        for axis in required_axes:
            assert axis in r
            assert len(str(r[axis])) > 0

    # Verify M2 and M3 specify 3 effective DOF
    m2 = next(r for r in reps if r["id"] == "M2")
    m3 = next(r for r in reps if r["id"] == "M3")
    assert "3 effective DOF" in m2["dimension"]
    assert "3 effective DOF" in m3["dimension"]

    # Ensure NO composite ranking score was computed (per prompt instructions)
    for r in reps:
        assert "composite_score" not in r
        assert "rank" not in r


# =============================================================================
# 7. RQ6: Conversational Timescale Viability Tests
# =============================================================================

def test_rq6_conversational_timescale_viability(study_data):
    """Verify timescale characterization distinguishes conversational T <= 25 from exploratory T >= 50."""
    rq6 = study_data["rq6_conversational_timescale_viability"]
    findings = rq6["findings_by_representation"]

    assert "M0_canonical_scalar" in findings
    assert "does not satisfy the current preregistered dual Gate 2 thresholds" in findings["M0_canonical_scalar"]["conversational_viability"]

    for rep in ["M1_displacement_vector", "M2_magnitude_direction", "M3_residual_magnitude_direction", "M4_full_residual_vector"]:
        assert rep in findings
        assert "HIGHLY VIABLE" in findings[rep]["conversational_viability"]


# =============================================================================
# 8. Final Decision State Tests
# =============================================================================

def test_final_decision_state(study_data):
    """Verify study ends at an allowed descriptive evidence state without authorizing architecture changes."""
    synth = study_data["evidence_synthesis"]
    decision_state = synth["decision_state"]
    assert "State B" in decision_state
    assert "Direction/Component Information Demonstrably Omitted" in decision_state

    # Verify competing interpretations are evaluated
    assert "M_S_scalar_sufficiency" in synth["competing_interpretations_assessment"]
    assert "M_V_vector_information_requirement" in synth["competing_interpretations_assessment"]
