"""
tests/evaluation_phase22/test_h1_measurement_architecture_decision.py

Validation suite for Phase 22 H1 Measurement Architecture Decision Study.

Verifies:
1. Manifest and results file integrity (SHA-256 match, schema completeness).
2. Strict governance invariants (H1 INCONCLUSIVE, Gate 2 BLOCKED, 0 mutations).
3. Historical source artifacts immutability.
4. Candidate measurement representations M0-M5 definitions and mathematical DOF.
5. RQ1 Evidence Consolidation matrix classifications (no composite score).
6. RQ2 Scalar sufficiency boundary (intensity/gating preserved vs directional collapse).
7. RQ3 R3 sufficiency boundary (geometric collapse != behavioral sufficiency != global minimality != production necessity).
8. RQ4 R2 incremental value in tested same-sign regime (zero incremental divergence).
9. RQ6 Gate 2 reconciliation (Gate 2 remains BLOCKED, not retroactively solved).
10. RQ9 Decision state evaluation consistency with predefined decision rules (NOT Architecture Approved).
"""

from __future__ import annotations

import hashlib
import json
from pathlib import Path
import pytest

REPO_ROOT = Path(__file__).resolve().parent.parent.parent
RESULTS_FILE = REPO_ROOT / "tests" / "evaluation_phase22" / "results" / "h1_measurement_architecture_decision" / "measurement_architecture_decision_results.json"
MANIFEST_FILE = REPO_ROOT / "tests" / "evaluation_phase22" / "fixtures" / "manifest_h1_measurement_architecture_decision.json"
GENESIS_PROFILE = REPO_ROOT / "data" / "profile.json"


@pytest.fixture(scope="module")
def results_data() -> dict:
    assert RESULTS_FILE.exists(), f"Results file missing: {RESULTS_FILE}"
    with open(RESULTS_FILE, "r", encoding="utf-8") as f:
        return json.load(f)


@pytest.fixture(scope="module")
def manifest_data() -> dict:
    assert MANIFEST_FILE.exists(), f"Manifest file missing: {MANIFEST_FILE}"
    with open(MANIFEST_FILE, "r", encoding="utf-8") as f:
        return json.load(f)


def test_01_manifest_and_file_integrity(results_data: dict, manifest_data: dict):
    """Test 1: Verify manifest exists, valid JSON, and SHA-256 matches bit-exact."""
    with open(RESULTS_FILE, "rb") as f:
        computed_sha = hashlib.sha256(f.read()).hexdigest()

    manifest_sha = manifest_data["files"]["measurement_architecture_decision_results.json"]["sha256"]
    assert computed_sha == manifest_sha, f"SHA-256 mismatch: {computed_sha} != {manifest_sha}"
    assert results_data["metadata"]["status"] == "COMPLETED"


def test_02_governance_invariants(results_data: dict, manifest_data: dict):
    """Test 2: Verify all strict governance invariants remain locked."""
    gov = results_data["metadata"]["governance"]
    assert gov["phase_22_h1"] == "INCONCLUSIVE"
    assert gov["gate_2"] == "BLOCKED"
    assert gov["protocol_v1_5"] == "NOT AUTHORIZED"
    assert gov["architecture_gate"] == "STRICTLY LOCKED"
    assert gov["src_core_mutations"] == 0
    assert gov["genesis_profile"] == "PRESERVED_BIT_EXACT"

    # Verify genesis profile on disk
    assert GENESIS_PROFILE.exists()
    with open(GENESIS_PROFILE, "r", encoding="utf-8") as f:
        profile = json.load(f)
    assert profile.get("is_onboarded") is False


def test_03_historical_source_artifacts_immutable(manifest_data: dict):
    """Test 3: Verify all historical source result files exist and match manifest hashes."""
    source_files = manifest_data["source_files"]
    for filename, info in source_files.items():
        file_path = REPO_ROOT / info["path"]
        assert file_path.exists(), f"Source file missing: {file_path}"
        with open(file_path, "rb") as f:
            computed_sha = hashlib.sha256(f.read()).hexdigest()
        assert computed_sha == info["sha256"], f"Source file SHA mismatch for {filename}"


def test_04_candidate_representations_defined(results_data: dict):
    """Test 4: Verify candidate measurement representations M0-M5 definitions and mathematical DOF."""
    candidates = results_data["candidate_definitions"]
    for c_id in ["M0", "M1", "M2", "M3", "M4", "M5"]:
        assert c_id in candidates, f"Candidate {c_id} missing from definitions"

    # M0: 1 continuous scalar, 1 DOF
    assert candidates["M0"]["stored_elements"] == 1
    assert candidates["M0"]["mathematical_dof"] == 1

    # M1: 1 continuous float + 3 ternary symbols in {-1, 0, 1}^3, 27 states
    assert candidates["M1"]["stored_elements"] == 4
    assert candidates["M1"]["mathematical_dof"] == 1
    assert candidates["M1"]["discrete_states"] == 27
    assert "3 bits" not in candidates["M1"]["dof_breakdown"].lower() or "distinct from '3 bits'" in candidates["M1"]["dof_breakdown"]

    # M2: 4 stored floats, 3 mathematical DOF
    assert candidates["M2"]["stored_elements"] == 4
    assert candidates["M2"]["mathematical_dof"] == 3

    # M3: 3 continuous Cartesian coordinates, 3 DOF
    assert candidates["M3"]["stored_elements"] == 3
    assert candidates["M3"]["mathematical_dof"] == 3

    # M4: Prediction-residual vector with semantic distinctions
    assert candidates["M4"]["stored_elements"] == 3
    distinctions = candidates["M4"]["semantic_distinctions"]
    assert "resting_state_displacement" in distinctions
    assert "prediction_residual" in distinctions
    assert "scalar_norm" in distinctions

    # M5: Exploratory precision candidate unvalidated
    assert candidates["M5"]["status"] == "EXPLORATORY_CANDIDATE_UNVALIDATED"


def test_05_rq1_evidence_consolidation_matrix(results_data: dict):
    """Test 5: Verify RQ1 Evidence Consolidation matrix classifications."""
    rq1 = results_data["rq1_evidence_consolidation"]
    valid_classifications = {
        "SUPPORTED_FOR_INTENSITY__INSUFFICIENT_FOR_DIRECTION",
        "SUPPORTED_FOR_FUTURE_ARCHITECTURAL_CONSIDERATION",
        "SUPPORTED_GEOMETRICALLY__UNPROVEN_BEHAVIORAL_INCREMENT",
        "SUFFICIENT_BUT_NOT_MINIMAL",
        "SEMANTICALLY_AUTHENTIC_PREDICTION_ERROR",
        "EXPLORATORY_CANDIDATE_UNVALIDATED",
    }
    for cand_key, cand_data in rq1.items():
        assert cand_data["evidence_classification"] in valid_classifications, f"Invalid classification for {cand_key}"
        assert "information_retained" in cand_data
        assert "information_discarded" in cand_data
        assert "collapse_resolution" in cand_data
        assert "behavioral_utilization" in cand_data


def test_06_rq2_scalar_sufficiency_boundary(results_data: dict):
    """Test 6: Verify RQ2 scalar sufficiency boundary documents both utility and limitation."""
    rq2 = results_data["rq2_scalar_sufficiency_boundary"]
    assert len(rq2["what_scalar_m0_can_explain"]) >= 3
    assert len(rq2["what_scalar_m0_cannot_explain"]) >= 3
    assert "NOT useless" in rq2["preservation_status"]


def test_07_rq3_r3_sufficiency_boundary(results_data: dict):
    """Test 7: Verify RQ3 R3 boundary asserts four-way distinction."""
    rq3 = results_data["rq3_r3_sufficiency_boundary"]
    scopes = rq3["scope_distinctions"]
    assert "geometric_collapse_resolution" in scopes
    assert "short_exposure_limitation" in scopes
    assert "behavioral_sufficiency" in scopes
    assert "NOT GLOBALLY MINIMAL" in scopes["global_minimality_status"]
    assert "UNPROVEN" in scopes["production_necessity_status"]
    assert len(rq3["unresolved_aspects"]) >= 3


def test_08_rq4_r2_incremental_value(results_data: dict):
    """Test 8: Verify RQ4 R2 incremental value in tested same-sign regime."""
    rq4 = results_data["rq4_r2_incremental_value"]
    t2a = rq4["test_2a_within_quadrant_findings"]
    assert t2a["pairs_with_large_angle"] == 0
    assert t2a["d_pol_c1_in_same_sign"] == 0.0
    assert t2a["p_value"] == 1.0
    assert "no incremental behavioral divergence was observed" in t2a["empirical_verdict"]
    assert "avoids a generalized conclusion that R2 has no incremental value" in rq4["scope_limitation"]


def test_09_rq6_gate2_reconciliation(results_data: dict):
    """Test 9: Verify RQ6 Gate 2 remains BLOCKED and no retroactive passing claim is made."""
    rq6 = results_data["rq6_gate2_reconciliation"]
    assert rq6["gate_2_status"] == "BLOCKED"
    assert rq6["does_failure_invalidate_directional_info"] is False
    assert rq6["can_directional_info_be_retained_without_claiming_gate_2_passed"] is True
    assert "dedicated, newly ratified research protocol" in rq6["protocol_requirement"]
    assert "benchmark_values" in rq6
    assert rq6["benchmark_values"]["S_M"] == 0.5792
    assert rq6["benchmark_values"]["S_H"] == 0.6477
    assert rq6["benchmark_values"]["Delta_HM"] == 0.0685


def test_10_decision_state_evaluation_consistency(results_data: dict, manifest_data: dict):
    """Test 10: Verify decision state is consistently evaluated from decision rules and NOT Architecture Approved."""
    dec = results_data["rq9_decision_state"]
    rules = dec["rule_evaluations"]

    # Verify decision rules consistency:
    # If scalar_sufficient is False, D0 cannot be selected
    assert rules["rule_1_scalar_sufficient"] is False
    assert dec["assigned_state"] != "D0"

    # If r2_incremental_value_demonstrated is False, D2 cannot be selected
    assert rules["rule_2_r2_incremental_value_demonstrated"] is False
    assert dec["assigned_state"] != "D2"

    # If full_vector_necessary is False, D3 cannot be selected
    assert rules["rule_3_full_vector_necessary"] is False
    assert dec["assigned_state"] != "D3"

    # If evidence is sufficient and R3 supported at conversational exposure -> D1
    if rules["rule_5_evidence_sufficient_for_consideration"] and rules["rule_4_r3_supported_at_conversational_exposure"]:
        assert dec["assigned_state"] == "D1"

    assert manifest_data["decision_state"] == dec["assigned_state"]
    assert manifest_data["architecture_approval_status"] == "NOT_APPROVED__RESEARCH_CONSIDERATION_ONLY"
    assert "NOT be described as 'Architecture Approved'" in dec["governance_lock"]
