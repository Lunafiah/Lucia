"""
tests/evaluation_phase22/test_h1_r3_architectural_semantics.py

Automated Test Suite for Phase 22 H1: R3 Architectural Semantics & Downstream Integration Study.
Validates:
- Manifest and results integrity (SHA-256 hash match)
- Strict governance invariants (H1 INCONCLUSIVE, Gate 2 BLOCKED, Gate LOCKED, 0 mutations)
- RQ1: Open-ended evaluation of 5 candidate semantic descriptors (dual-aspect as candidate interpretation)
- RQ2: Unidirectional ownership boundary (S4 Producer -> Value Object -> Passive Transport -> Explicit Consumers)
- RQ3: Consumer semantics classification across 10 subsystems (adapter-scoped evidence vs untested/unjustified)
- RQ4: Magnitude / direction complementarity under matched-magnitude conditions (358 pairs)
- RQ5: Encoding semantics (3 discrete ternary coordinate dimensions vs 27 states / 4.755 bits capacity)
- RQ6: Temporal metadata candidate semantics (T as dynamical maturity, w_exp as research-harness policy rule)
- RQ7: Policy boundary models (Model A NOT JUSTIFIED / HIGH-RISK, Model B-D consistent, 5 critical risks)
- RQ8: Formal invariant ledger strictly audited into 3 tiers (4 Proven, 5 Research-Harness, 4 Proposed Future)
- RQ9: Information loss boundary mapping across 6 dimensions
- RQ10: Dynamic ADR-029 readiness state (READY_FOR_DRAFT_UPDATE under strictly locked Architecture Gate)
"""

import hashlib
import json
import math
from pathlib import Path
import pytest

REPO_ROOT = Path(__file__).resolve().parent.parent.parent
RESULTS_DIR = REPO_ROOT / "tests" / "evaluation_phase22" / "results" / "h1_r3_architectural_semantics"
FIXTURES_DIR = REPO_ROOT / "tests" / "evaluation_phase22" / "fixtures"

RESULTS_FILE = RESULTS_DIR / "r3_architectural_semantics_results.json"
MANIFEST_FILE = FIXTURES_DIR / "manifest_h1_r3_architectural_semantics.json"


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
    assert manifest_data["study_name"] == "Phase 22 H1 R3 Architectural Semantics & Downstream Integration Study"

    file_entry = manifest_data["files"]["r3_architectural_semantics_results.json"]
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
    assert "S_M = 0.5792" in gov["gate_2_metric"]
    assert "S_H = 0.6477" in gov["gate_2_metric"]

    # Manifest governance sync
    m_gov = manifest_data["governance_invariants"]
    assert m_gov["phase_22_h1"] == "INCONCLUSIVE"
    assert m_gov["gate_2"] == "BLOCKED"
    assert m_gov["protocol_v1_5"] == "NOT AUTHORIZED"
    assert m_gov["architecture_gate"] == "STRICTLY LOCKED"
    assert m_gov["genesis_profile"] == "PRESERVED_BIT_EXACT"
    assert m_gov["src_core_mutations"] == 0

    # Genesis profile on disk
    profile_path = REPO_ROOT / "data" / "profile.json"
    if profile_path.exists():
        with open(profile_path, "r", encoding="utf-8") as f:
            profile = json.load(f)
            assert profile.get("is_onboarded") is False


# ---------------------------------------------------------------------------
# Test 03: RQ1 Open-Ended Candidate Semantic Descriptors
# ---------------------------------------------------------------------------

def test_03_rq1_open_ended_candidate_descriptors(results_data: dict):
    rq1 = results_data["rq1_semantic_identity"]
    candidates = rq1["candidates"]
    assert len(candidates) == 5

    desc_ids = [c["id"] for c in candidates]
    assert desc_ids == ["DESC-1", "DESC-2", "DESC-3", "DESC-4", "DESC-5"]

    # Verify no preset conclusion as sole descriptor
    statuses = [c["status"] for c in candidates]
    assert "REJECTED_AS_SOLE_DESCRIPTOR" in statuses
    assert "CANDIDATE_INTERPRETATION_EVALUATED" in statuses
    assert "FUNCTIONAL_INTERPRETATION_ONLY" in statuses

    # Dual-aspect concept evaluated as candidate interpretation
    syn = rq1["synthesized_candidate_interpretation"]
    assert syn["governance_status"] == "CANDIDATE_EVALUATION__NOT_PRODUCTION_RATIFIED"
    assert "Canonical Scalar Physiological Surprise" in syn["primary_aspect"]
    assert "Ternary Directional Annotation" in syn["auxiliary_aspect"]


# ---------------------------------------------------------------------------
# Test 04: RQ2 Ownership Boundary and Transport Graph
# ---------------------------------------------------------------------------

def test_04_rq2_ownership_boundary(results_data: dict):
    rq2 = results_data["rq2_ownership_boundary"]
    graph = rq2["ownership_graph"]

    assert graph["ActiveInferenceEngine"]["role"] == "SOLE_PRODUCER_CANDIDATE"
    assert "Stage S4" in graph["ActiveInferenceEngine"]["stage"]

    assert graph["PhysiologicalSurprise"]["role"] == "IMMUTABLE_VALUE_OBJECT_CANDIDATE"
    assert "Transport Artifact across S5-S12" in graph["PhysiologicalSurprise"]["stage"]

    assert graph["CognitiveOrchestrator"]["role"] == "COORDINATOR_TRANSPORT_ONLY"
    assert graph["DownstreamConsumers"]["role"] == "EXPLICIT_CONTRACT_CONSUMERS"

    assert "unidirectional" in rq2["boundary_rule"].lower()


# ---------------------------------------------------------------------------
# Test 05: RQ3 Downstream Consumer Semantics (Exact 10 Subsystems)
# ---------------------------------------------------------------------------

def test_05_rq3_ten_subsystems_consumer_semantics(results_data: dict):
    rq3 = results_data["rq3_consumer_semantics"]
    assert rq3["subsystems_evaluated"] == 10
    classes = rq3["classifications"]

    # EFE & Communication Strategy are adapter-only
    assert classes["EFE_Action_Valuation"]["classification"] == "EVIDENCE-CONSISTENT (RESEARCH ADAPTER ONLY)"
    assert classes["Communication_Strategy"]["classification"] == "EVIDENCE-CONSISTENT (RESEARCH ADAPTER ONLY)"

    # Clarification, Depth, Relationship are NOT JUSTIFIED
    assert classes["Clarification_Policy"]["classification"] == "NOT JUSTIFIED"
    assert classes["Reasoning_Depth"]["classification"] == "NOT JUSTIFIED"
    assert classes["Relationship_Update"]["classification"] == "NOT JUSTIFIED"

    # Prompt conditioning and memory formation are hypotheses / untested
    assert classes["Prompt_Conditioning"]["classification"] == "HYPOTHESIS / UNTESTED"
    assert classes["Memory_Formation"]["classification"] == "HYPOTHESIS / UNTESTED"

    # SLM, Avatar, Expression are UNTESTED
    assert classes["SLM_Generation"]["classification"] == "UNTESTED"
    assert classes["Affective_Expression"]["classification"] == "UNTESTED"
    assert classes["Avatar_Embodiment"]["classification"] == "UNTESTED"

    # Verify summary counts: Exactly 0 SUPPORTED (no end-to-end production evidence)
    counts = rq3["summary_counts"]
    assert counts["SUPPORTED"] == 0
    assert counts["EVIDENCE_CONSISTENT__RESEARCH_ADAPTER_ONLY"] == 2
    assert counts["NOT_JUSTIFIED"] == 3
    assert counts["HYPOTHESIS__UNTESTED"] == 2
    assert counts["UNTESTED"] == 3


# ---------------------------------------------------------------------------
# Test 06: RQ4 Magnitude / Direction Complementarity
# ---------------------------------------------------------------------------

def test_06_rq4_magnitude_direction_complementarity(results_data: dict):
    rq4 = results_data["rq4_magnitude_direction_complementarity"]
    basis = rq4["evidence_basis"]

    assert basis["collapse_pairs_evaluated"] == 358
    assert basis["scalar_differentiation_rate"] == 0.0
    assert abs(basis["directional_differentiation_rate"] - 0.7989) < 0.001
    assert abs(basis["near_zero_transition_concentration"] - 0.8447) < 0.001
    assert basis["high_magnitude_transitions_count"] == 0

    # Calibrated language lock check
    conclusion = rq4["calibrated_conclusion"]
    assert "Evidence is consistent with magnitude and direction carrying complementary information under the evaluated conditions" in conclusion

    guardrail = rq4["interpretation_guardrail"]
    assert "NOT an established global architectural semantic fact" in guardrail


# ---------------------------------------------------------------------------
# Test 07: RQ5 Direction Encoding Semantics (Coordinates vs Capacity)
# ---------------------------------------------------------------------------

def test_07_rq5_direction_encoding_semantics(results_data: dict):
    rq5 = results_data["rq5_direction_encoding_semantics"]
    assert "CRITICAL DISTINCTION" in rq5["distinction_note"]

    encodings = {e["encoding"]: e for e in rq5["encodings"]}
    assert len(encodings) == 6

    # Ternary Sign Vector: 3 discrete ternary coordinate dimensions vs 27 states / ~4.755 bits
    ternary = encodings["Ternary Sign Vector sign(r)"]
    assert ternary["coordinate_dimensions"] == 3
    assert ternary["degrees_of_freedom"] == "3 independent discrete ternary DOF"
    assert ternary["state_space_size"] == "27 discrete states"
    assert "4.755 bits" in ternary["information_capacity"]

    # Hybrid R3: 1 scalar + 3 discrete ternary coordinates
    r3 = encodings["Scalar + Ternary Sign R3 = [S, sign(r)]"]
    assert r3["coordinate_dimensions"] == "1 scalar + 3 discrete ternary coordinates"
    assert "3 discrete directional DOF" in r3["degrees_of_freedom"]
    assert "36.755 bits" in r3["information_capacity"]


# ---------------------------------------------------------------------------
# Test 08: RQ6 Temporal Semantics & Exposure Metadata
# ---------------------------------------------------------------------------

def test_08_rq6_temporal_semantics(results_data: dict):
    rq6 = results_data["rq6_temporal_semantics"]
    evals = {item["item"]: item for item in rq6["candidate_semantics_evaluations"]}

    assert evals["timestamp_tick"]["classification"] == "PROVENANCE_METADATA"
    assert evals["exposure_ticks (T)"]["classification"] == "DYNAMICAL_MATURITY_METADATA"
    assert evals["exposure_confidence (w_exp = min(T/12, 1))"]["classification"] == "RESEARCH_HARNESS_POLICY_METADATA"
    assert evals["deadband_state (eps = 0.010)"]["classification"] == "MEASUREMENT_CLEANING_METADATA"

    finding = rq6["calibrated_finding"]
    assert "dynamical maturity indicator under current MT-LNN dynamics" in finding
    assert "research-harness policy weighting rule" in finding


# ---------------------------------------------------------------------------
# Test 09: RQ7 Policy Boundary Models and Architectural Risks
# ---------------------------------------------------------------------------

def test_09_rq7_policy_boundary_models(results_data: dict):
    rq7 = results_data["rq7_policy_boundary"]
    models = {m["model"].split(":")[0]: m for m in rq7["models_evaluated"]}

    # Model A is HIGH RISK / NOT JUSTIFIED
    assert models["Model A"]["risk_profile"] == "HIGH_RISK / NOT JUSTIFIED"
    assert "circular feedback" in models["Model A"]["evaluation"].lower()

    # Model B, C, D are consistent
    assert "CONSISTENT" in models["Model B"]["risk_profile"]
    assert "CONSISTENT" in models["Model C"]["risk_profile"]
    assert "CONSISTENT" in models["Model D"]["risk_profile"]

    # Target architecture
    assert "Hybrid Model C + Model D" in rq7["recommended_target_architecture"]

    # Architectural risks cataloged
    risks = [r["risk"] for r in rq7["architectural_risks"]]
    assert "Circular Feedback" in risks
    assert "Semantic Bleed" in risks
    assert "Accidental Self-Reported Affect" in risks
    assert "Premature SLM Conditioning" in risks
    assert "Loss of Fallback Identity" in risks


# ---------------------------------------------------------------------------
# Test 10: RQ8 Invariant Ledger across Three Tiers
# ---------------------------------------------------------------------------

def test_10_rq8_invariant_ledger(results_data: dict):
    rq8 = results_data["rq8_invariant_ledger"]
    assert rq8["total_invariants_audited"] == 13

    # Tier 1: Proven Invariants (4)
    proven = rq8["proven_invariants"]
    assert len(proven) == 4
    proven_ids = [inv["id"] for inv in proven]
    assert proven_ids == ["INV-P1", "INV-P2", "INV-P3", "INV-P4"]
    for inv in proven:
        assert inv["status"] == "PROVEN_INVARIANT"

    # Tier 2: Research-Harness Invariants (5)
    rh = rq8["research_harness_invariants"]
    assert len(rh) == 5
    rh_ids = [inv["id"] for inv in rh]
    assert rh_ids == ["INV-RH1", "INV-RH2", "INV-RH3", "INV-RH4", "INV-RH5"]
    for inv in rh:
        assert inv["status"] == "RESEARCH_HARNESS_INVARIANT"

    # Tier 3: Proposed Future Integration Invariants (4)
    future = rq8["proposed_future_invariants"]
    assert len(future) == 4
    future_ids = [inv["id"] for inv in future]
    assert future_ids == ["INV-F1", "INV-F2", "INV-F3", "INV-F4"]
    for inv in future:
        assert inv["status"] == "PROPOSED_FUTURE_INTEGRATION_INVARIANT"


# ---------------------------------------------------------------------------
# Test 11: RQ9 Information Loss Boundary Mapping
# ---------------------------------------------------------------------------

def test_11_rq9_information_loss_boundary(results_data: dict):
    rq9 = results_data["rq9_information_loss_boundary"]
    loss_matrix = rq9["information_loss_matrix"]
    assert len(loss_matrix) == 6

    dims = {row["information_dimension"]: row for row in loss_matrix}

    # Magnitude preserved exact in both
    mag_key = [k for k in dims if "Magnitude" in k][0]
    assert "PRESERVED_EXACT" in dims[mag_key]["scalar_only_path"]
    assert "PRESERVED_EXACT" in dims[mag_key]["r3_sidechannel_path"]

    # Component polarity lost in scalar, preserved discrete in R3
    pol_key = [k for k in dims if "Polarity" in k][0]
    assert "COMPLETELY_LOST" in dims[pol_key]["scalar_only_path"]
    assert "PRESERVED_DISCRETE" in dims[pol_key]["r3_sidechannel_path"]

    # Intra-octant angle lost in both
    oct_key = [k for k in dims if "Intra-Octant" in k][0]
    assert "COMPLETELY_LOST" in dims[oct_key]["scalar_only_path"]
    assert "COMPLETELY_LOST" in dims[oct_key]["r3_sidechannel_path"]


# ---------------------------------------------------------------------------
# Test 12: RQ10 Dynamic ADR Readiness and Locked Production Gate
# ---------------------------------------------------------------------------

def test_12_rq10_dynamic_adr_readiness(results_data: dict):
    rq10 = results_data["rq10_adr_readiness"]
    checklist = rq10["readiness_checklist"]

    # All 12 criteria verified True
    assert len(checklist) == 12
    assert all(checklist.values()) is True

    # Dynamically assigned status
    assert rq10["assigned_status"] == "READY_FOR_DRAFT_UPDATE"
    assert rq10["production_architecture_gate"] == "STRICTLY LOCKED"
    assert rq10["adr_ratification_status"] == "NOT RATIFIED / DRAFT RECORD ONLY"
    assert "STRICTLY LOCKED" in rq10["operational_meaning"]
