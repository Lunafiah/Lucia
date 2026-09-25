"""
tests/evaluation_phase22/test_h1_r3_architecture_integration.py

Automated Test Suite for Phase 22 H1: R3 Architecture Integration Feasibility Study.
Validates:
- Manifest and cryptographic hashes
- Governance invariants (H1 INCONCLUSIVE, Gate 2 BLOCKED, Protocol v1.5 NOT AUTHORIZED, Gate LOCKED)
- Pipeline placement (Stage S4 ActiveInferenceEngine, Value Object transport)
- Semantic ownership (Dedicated Value Object recommended, SRP alignment)
- Research interface shape (1 continuous float + 27 discrete states in {-1, 0, +1}^3)
- Canonical scalar preservation (formal invariance derivation & deterministic verification S_new == S_canonical)
- Downstream consumption classifications (8 subsystems strictly scoped)
- Behavioral evidence boundary (Research Adapter vs End-to-End SLM)
- Short-timescale compatibility (T in {1, 2, 4, 8, 12})
- Zero / sign-jitter semantics (deadband hypothesis)
- Future R2 compatibility (R3 derivable from R2 via deterministic sign projection)
- Prediction residual vs bodily displacement (r_T != Delta_p)
- Active Inference semantics (quadratic residual metric correspondence)
- Architecture boundary & ADR readiness (READY FOR ADR DRAFT while Gate remains LOCKED)
- Architecture Options Matrix (Options A-E), Invariants (INV-1 to INV-9), Failure Modes (FM-01 to FM-12)
"""

import hashlib
import json
import math
from pathlib import Path
import pytest

REPO_ROOT = Path(__file__).resolve().parent.parent.parent
RESULTS_DIR = REPO_ROOT / "tests" / "evaluation_phase22" / "results" / "h1_r3_architecture_integration"
FIXTURES_DIR = REPO_ROOT / "tests" / "evaluation_phase22" / "fixtures"

RESULTS_FILE = RESULTS_DIR / "r3_architecture_integration_results.json"
MANIFEST_FILE = FIXTURES_DIR / "manifest_h1_r3_architecture_integration.json"


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


def compute_sha256(path: Path) -> str:
    with open(path, "rb") as f:
        return hashlib.sha256(f.read()).hexdigest()


# ---------------------------------------------------------------------------
# Test 01: Manifest and Results Integrity
# ---------------------------------------------------------------------------

def test_01_manifest_and_results_integrity(manifest_data: dict):
    assert manifest_data["manifest_version"] == "1.0"
    assert manifest_data["study_name"] == "Phase 22 H1 R3 Architecture Integration Feasibility Study"

    file_entry = manifest_data["files"]["r3_architecture_integration_results.json"]
    expected_sha = file_entry["sha256"]
    actual_sha = compute_sha256(RESULTS_FILE)
    assert actual_sha == expected_sha, f"SHA-256 mismatch: expected {expected_sha}, got {actual_sha}"
    assert file_entry["size_bytes"] == RESULTS_FILE.stat().st_size


# ---------------------------------------------------------------------------
# Test 02: Governance Invariants
# ---------------------------------------------------------------------------

def test_02_governance_invariants(results_data: dict, manifest_data: dict):
    gov = results_data["metadata"]["governance"]
    assert gov["phase_22_h1"] == "INCONCLUSIVE"
    assert gov["gate_2"] == "BLOCKED"
    assert gov["protocol_v1_5"] == "NOT AUTHORIZED"
    assert gov["architecture_gate"] == "STRICTLY LOCKED"
    assert gov["src_core_mutations"] == 0
    assert gov["genesis_profile"] == "PRESERVED_BIT_EXACT"
    assert "Delta_HM = 0.0685 < 0.1500" in gov["gate_2_metric"]

    # Check Genesis profile on disk
    profile_path = REPO_ROOT / "data" / "profile.json"
    if profile_path.exists():
        with open(profile_path, "r", encoding="utf-8") as f:
            profile = json.load(f)
            assert profile.get("is_onboarded") is False


# ---------------------------------------------------------------------------
# Test 03: RQ1 Pipeline Placement
# ---------------------------------------------------------------------------

def test_03_rq1_pipeline_placement(results_data: dict):
    rq1 = results_data["rq1_pipeline_placement"]
    assert rq1["canonical_producer"] == "ActiveInferenceEngine"
    assert "Stage S4" in rq1["earliest_creation_point"]
    assert "ActiveInferenceEngine.step()" in rq1["earliest_creation_point"]

    stages = {s["stage"]: s for s in rq1["pipeline_stages"]}
    assert stages["S1"]["r3_status"] == "DOES_NOT_EXIST"
    assert stages["S3"]["r3_status"] == "DOES_NOT_EXIST"
    assert stages["S4"]["r3_status"] == "EARLIEST_VALID_CREATION_POINT"
    assert stages["S10"]["r3_status"] == "PRIMARY_DOWNSTREAM_CONSUMER"
    assert stages["S11"]["r3_status"] == "PRIMARY_DOWNSTREAM_CONSUMER"
    assert stages["S13"]["r3_status"] == "PROHIBITED_NON_CONSUMER"

    # Non-consumers
    prohibited = " ".join(rq1["prohibited_non_consumers"])
    assert "EmotionCore ODE Hidden State h(t)" in prohibited
    assert "BoundaryLayer" in prohibited
    assert "StabilityEvaluator" in prohibited
    assert "Somatic Load" in prohibited


# ---------------------------------------------------------------------------
# Test 04: RQ2 Semantic Ownership & RQ3 Interface Shape
# ---------------------------------------------------------------------------

def test_04_rq2_rq3_semantic_ownership_and_interface(results_data: dict):
    rq2 = results_data["rq2_semantic_ownership"]
    owners = rq2["candidate_owners"]
    assert owners["EmotionCore"]["verdict"] == "NOT_RECOMMENDED"
    assert owners["ActiveInferenceEngine"]["verdict"] == "PRODUCER_ONLY"
    assert owners["CognitiveOrchestrator"]["verdict"] == "COORDINATOR_TRANSPORT_ONLY"
    assert owners["Dedicated_Value_Object"]["verdict"] == "RECOMMENDED_ARCHITECTURE"

    rq3 = results_data["rq3_interface_shape"]
    assert rq3["class_name"] == "PhysiologicalSurprise"
    fields = rq3["fields"]
    assert "magnitude" in fields
    assert "direction" in fields
    assert "provenance" in fields
    assert "exposure_ticks" in fields
    assert fields["magnitude"]["type"] == "float"
    assert fields["direction"]["discrete_states"] == 27
    assert rq3["storage_vs_dof"]["mathematical_degrees_of_freedom"] == (
        "1 continuous degree of freedom (magnitude S in R_>=0) + 27 discrete sign states in {-1, 0, +1}^3."
    )


# ---------------------------------------------------------------------------
# Test 05: RQ4 Canonical Scalar Preservation Invariance
# ---------------------------------------------------------------------------

def test_05_rq4_canonical_scalar_preservation(results_data: dict):
    rq4 = results_data["rq4_scalar_preservation"]
    assert rq4["status"] == "VERIFIED_BIT_EXACT_IDENTITY"
    for record in rq4["test_verification"]:
        assert record["bit_exact_match"] is True
        assert record["delta"] == 0.0
        r = record["residual"]
        expected_norm = math.sqrt(sum(x**2 for x in r))
        assert abs(record["s_canonical"] - expected_norm) < 1e-12
        assert abs(record["s_new"] - expected_norm) < 1e-12


# ---------------------------------------------------------------------------
# Test 06: RQ5 Downstream Consumption Map
# ---------------------------------------------------------------------------

def test_06_rq5_downstream_consumption_map(results_data: dict):
    rq5 = results_data["rq5_downstream_consumption_map"]
    subs = rq5["subsystem_evaluations"]

    assert subs["CognitiveLoad_Modulation"]["classification"] == "NOT_RECOMMENDED"
    assert subs["ReasoningDepth_Selection"]["classification"] == "OPTIONAL__NOT_STRONGLY_SUPPORTED"
    assert subs["EFE_Action_Valuation"]["classification"] == "RECOMMENDED"
    assert subs["Communication_Strategy"]["classification"] == "RECOMMENDED"
    assert subs["Prompt_Conditioning"]["classification"] == "RECOMMENDED_QUALITATIVE_ONLY"
    assert subs["Response_Synthesis_SLM"]["classification"] == "NOT_YET_TESTED"
    assert subs["Affective_Expression_Multimodal"]["classification"] == "NOT_YET_TESTED"
    assert subs["Future_Embodiment"]["classification"] == "NOT_YET_TESTED"


# ---------------------------------------------------------------------------
# Test 07: RQ6 Behavioral Evidence Boundary
# ---------------------------------------------------------------------------

def test_07_rq6_behavioral_adapter_boundary(results_data: dict):
    rq6 = results_data["rq6_behavioral_adapter_boundary"]
    assert len(rq6["established_in_research_adapter"]) >= 4
    assert len(rq6["untested_and_unproven_for_slm"]) >= 4
    assert "Research Adapter Evidence != End-to-End Layer 6 SLM Evidence" in rq6["boundary_principle"]


# ---------------------------------------------------------------------------
# Test 08: RQ7 Short-Timescale Compatibility
# ---------------------------------------------------------------------------

def test_08_rq7_short_timescale_compatibility(results_data: dict):
    rq7 = results_data["rq7_short_timescale_compatibility"]
    lim = rq7["empirical_limitation"]
    assert "968" in lim["T_1"]
    assert "682" in lim["T_2"]
    assert "66" in lim["T_4"]
    assert "66" in lim["T_8"]
    assert "0" in lim["T_12_plus"]

    policies = rq7["evaluated_policies"]
    assert "Policy_1_Unconditional_Exposure" in policies
    assert "Policy_2_Gated_Exposure" in policies
    assert "Policy_3_Exposure_Annotated" in policies
    assert "Policy_4_R2_Extension_Path" in policies
    assert policies["Policy_3_Exposure_Annotated"]["verdict"] == "RECOMMENDED_CANDIDATE"


# ---------------------------------------------------------------------------
# Test 09: RQ8 Zero/Sign-Jitter & RQ10 Residual vs Displacement
# ---------------------------------------------------------------------------

def test_09_rq8_rq10_jitter_and_residual_semantics(results_data: dict):
    rq8 = results_data["rq8_zero_sign_jitter_semantics"]
    assert rq8["proposed_deadband_model"]["candidate_epsilon"] == 0.01
    assert "RESEARCH_HYPOTHESIS" in rq8["proposed_deadband_model"]["status"]

    rq10 = results_data["rq10_residual_vs_displacement"]
    assert "179.5 degrees" in rq10["empirical_divergence"]
    assert "r_T = p_hat_T - p_T" in rq10["architectural_invariant"]
    assert "NEVER from bodily displacement Delta_p" in rq10["architectural_invariant"]


# ---------------------------------------------------------------------------
# Test 10: RQ9 Future R2 Compatibility via Deterministic Sign Projection
# ---------------------------------------------------------------------------

def test_10_rq9_future_r2_compatibility(results_data: dict):
    rq9 = results_data["rq9_future_r2_compatibility"]
    assert rq9["status"] == "DERIVABLE_VIA_DETERMINISTIC_SIGN_PROJECTION"
    assert "deterministic sign projection of the directional components" in rq9["mathematical_property"]

    # Verify projections
    for test_p in rq9["projection_verification"]:
        assert test_p["identical"] is True
        assert test_p["r3_from_residual"] == test_p["r3_from_vhat"]


# ---------------------------------------------------------------------------
# Test 11: RQ11 Active Inference Semantics (Lock Terminology)
# ---------------------------------------------------------------------------

def test_11_rq11_active_inference_semantics(results_data: dict):
    rq11 = results_data["rq11_active_inference_compatibility"]
    claims = {c["claim"]: c for c in rq11["claims_and_evidence"]}

    # Ensure F proportional to 1/2 S^2 is strictly qualified
    quad_key = [k for k in claims if "F proportional to 1/2 S^2" in k][0]
    assert claims[quad_key]["classification"] == "SUPPORTED_AS_SPECIFIC_METRIC_CORRESPONDENCE"
    assert "NOT a universal identity" in claims[quad_key]["justification"]

    # Ensure dFE/dp is strictly qualified
    grad_key = [k for k in claims if "dFE/dp proportional to -r" in k][0]
    assert claims[grad_key]["classification"] == "SUPPORTED_UNDER_QUADRATIC_RESIDUAL_ASSUMPTION"
    assert "not a general claim" in claims[grad_key]["justification"]


# ---------------------------------------------------------------------------
# Test 12: RQ12 ADR Readiness & Architecture Gate Locking
# ---------------------------------------------------------------------------

def test_12_rq12_adr_readiness_and_gate_locking(results_data: dict, manifest_data: dict):
    rq12 = results_data["rq12_adr_readiness"]
    assert rq12["status"] == "READY_FOR_ADR_DRAFT"
    assert manifest_data["adr_readiness_state"] == "READY_FOR_ADR_DRAFT"

    criteria = rq12["readiness_criteria"]
    assert all(criteria.values()) is True
    assert len(criteria) == 10

    op_meaning = rq12["operational_meaning"]
    assert "CRITICAL: Being 'READY FOR ADR DRAFT' does NOT imply Architecture Gate approval" in op_meaning
    assert "The Production Architecture Gate remains STRICTLY LOCKED" in op_meaning
    assert "DRAFT / NOT RATIFIED / NOT IMPLEMENTED" in op_meaning


# ---------------------------------------------------------------------------
# Test 13: Options Matrix, Invariants, and Failure Modes
# ---------------------------------------------------------------------------

def test_13_options_matrix_invariants_failure_modes(results_data: dict):
    matrix = results_data["architecture_options_matrix"]
    assert len(matrix) == 9  # 9 dimensions

    invariants = results_data["architecture_invariants"]
    assert len(invariants) == 9
    inv_ids = {inv["id"] for inv in invariants}
    assert inv_ids == {f"INV-{i}" for i in range(1, 10)}

    failure_modes = results_data["failure_modes"]
    assert len(failure_modes) == 12
    fm_ids = {fm["id"] for fm in failure_modes}
    assert fm_ids == {f"FM-{i:02d}" for i in range(1, 13)}
