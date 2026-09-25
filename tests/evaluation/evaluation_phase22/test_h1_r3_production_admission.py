"""
tests/evaluation_phase22/test_h1_r3_production_admission.py

Automated Test Suite for Phase 22 H1: R3 Production Admission Criteria & ADR-029 Evidence Boundary Study.
Validates:
- Manifest and results integrity (SHA-256 hash match)
- Strict governance invariants (H1 INCONCLUSIVE, Gate 2 BLOCKED, Gate LOCKED, 0 mutations)
- Shared-data dependency detection (Rules A & B: tracking shared corpus dependencies)
- RQ1: Evidence inventory completeness (19 claims audited across 7 calibrated tiers)
- RQ2: Claim dependency graph and epistemological boundaries (Math != Empirical != Behavioral != Production)
- RQ3: Production admission 4-stage boundary separation (Stage A -> Stage B -> Stage C -> Stage D)
- RQ4: Minimum future evidence evaluation (12 candidate requirements dynamically classified)
- RQ5: End-to-end evidence gap analysis (adapter scope lock, SLM and avatar unbridgeable without live testbeds)
- RQ6: C0 baseline regression requirement (3 categories: canonical requirements, research metrics, future thresholds)
- RQ7: Robustness boundary classification (Mathematical-General vs. Empirically Regime-Bound)
- RQ8: Actionable future validation matrix (11 claim areas linked to studies and gates)
- RQ9 & RQ10: ADR-029 MAY / OPEN / MUST NOT boundaries and dynamic readiness state (READY_FOR_DRAFT_UPDATE)
"""

import hashlib
import json
from pathlib import Path
import pytest

REPO_ROOT = Path(__file__).resolve().parent.parent.parent
RESULTS_DIR = REPO_ROOT / "tests" / "evaluation_phase22" / "results" / "h1_r3_production_admission"
FIXTURES_DIR = REPO_ROOT / "tests" / "evaluation_phase22" / "fixtures"

RESULTS_FILE = RESULTS_DIR / "r3_production_admission_results.json"
MANIFEST_FILE = FIXTURES_DIR / "manifest_h1_r3_production_admission.json"


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
    assert manifest_data["study_name"] == "Phase 22 H1 R3 Production Admission Criteria & ADR-029 Evidence Boundary Study"

    file_entry = manifest_data["files"]["r3_production_admission_results.json"]
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
# Test 03: Shared-Data Dependency Detection (Rules A & B)
# ---------------------------------------------------------------------------

def test_03_shared_data_dependencies(results_data: dict):
    shared = results_data["shared_data_dependencies"]
    assert "Frozen 270-stimulus" in shared["underlying_dataset"]
    assert "seed=42" in shared["underlying_dataset"]
    assert "Generator G1" in shared["stimulus_generation"]
    assert "Coupled MT-LNN ODE" in shared["dynamical_regime"]

    rules = shared["shared_data_rule_enforcement"]
    assert "does NOT constitute independent empirical replication" in rules["rule_a_no_dataset_multiplication"]
    assert "facets of the same underlying dynamical simulation" in rules["rule_b_no_evidence_inflation"]
    assert len(shared["distinct_facets_analyzed"]) == 5


# ---------------------------------------------------------------------------
# Test 04: RQ1 Evidence Inventory Completeness (19 Claims)
# ---------------------------------------------------------------------------

def test_04_rq1_evidence_inventory(results_data: dict):
    rq1 = results_data["rq1_evidence_inventory"]
    assert rq1["claims_audited_count"] == 19
    claims = {c["id"]: c for c in rq1["claims"]}

    # Verify key specific claims
    assert claims["CLM-01"]["tier"] == "SUPPORTED"  # Scalar S preservation
    assert claims["CLM-02"]["tier"] == "SUPPORTED"  # Residual provenance
    assert claims["CLM-03"]["tier"] == "SUPPORTED"  # Ternary encoding
    assert claims["CLM-04"]["tier"] == "SUPPORTED"  # Static stability
    assert claims["CLM-05"]["tier"] == "OBSERVED"   # Multi-turn near-zero concentration
    assert claims["CLM-06"]["tier"] == "OBSERVED"   # Deadband chatter reduction
    assert claims["CLM-07"]["tier"] == "RESEARCH-HARNESS ONLY"  # 79.89% collapse resolution
    assert claims["CLM-08"]["tier"] == "RESEARCH-HARNESS ONLY"  # Adapter differentiation
    assert claims["CLM-09"]["tier"] == "EVIDENCE-CONSISTENT"    # Complementarity
    assert claims["CLM-13"]["tier"] == "UNTESTED"   # SLM generation
    assert claims["CLM-14"]["tier"] == "UNTESTED"   # Multimodal blendshapes
    assert claims["CLM-15"]["tier"] == "UNTESTED"   # Mascot embodiment
    assert claims["CLM-17"]["tier"] == "NOT JUSTIFIED"  # Relational consolidation
    assert claims["CLM-18"]["tier"] == "UNTESTED"   # Production EFE
    assert claims["CLM-19"]["tier"] == "SUPPORTED"  # Separation from uncertainty

    counts = rq1["tier_counts"]
    assert counts["SUPPORTED"] == 5
    assert counts["OBSERVED"] == 2
    assert counts["RESEARCH-HARNESS ONLY"] == 2
    assert counts["EVIDENCE-CONSISTENT"] == 3
    assert counts["HYPOTHESIS"] == 2
    assert counts["UNTESTED"] == 4
    assert counts["NOT JUSTIFIED"] == 1


# ---------------------------------------------------------------------------
# Test 05: RQ2 Claim Dependency Graph & Epistemology
# ---------------------------------------------------------------------------

def test_05_rq2_claim_dependency_graph(results_data: dict):
    rq2 = results_data["rq2_claim_dependency_graph"]
    assert len(rq2["nodes"]) == 7
    assert len(rq2["edges"]) == 6

    distinctions = rq2["epistemological_distinctions"]
    assert "mathematical_derivation" in distinctions
    assert "empirical_observation" in distinctions
    assert "behavioral_evidence" in distinctions
    assert "production_validation" in distinctions

    # Check that behavioral evidence does NOT transfer to production
    edge_adapter_to_consumer = [e for e in rq2["edges"] if e["edge"] == "N4 -> N5"][0]
    assert edge_adapter_to_consumer["nature"] == "BEHAVIORAL_EVIDENCE_IN_ADAPTER"
    assert "RESEARCH_HARNESS_ONLY" in edge_adapter_to_consumer["epistemic_transfer"]

    edge_prod = [e for e in rq2["edges"] if e["edge"] == "N6 -> N7"][0]
    assert edge_prod["nature"] == "UNVALIDATED_PRODUCTION_CLAIM"
    assert "PROHIBITED_WITHOUT_GATE_RATIFICATION" in edge_prod["epistemic_transfer"]


# ---------------------------------------------------------------------------
# Test 06: RQ3 Production Admission Boundary across 4 Stages
# ---------------------------------------------------------------------------

def test_06_rq3_production_admission_boundary(results_data: dict):
    rq3 = results_data["rq3_production_admission_boundary"]
    stages = {s["stage"].split("—")[0].strip(): s for s in rq3["stages"]}

    assert len(stages) == 4
    assert stages["Stage A"]["current_status"] == "COMPLETED_FOR_H1_R3"
    assert stages["Stage B"]["current_status"] == "CURRENT_OBJECTIVE"
    assert stages["Stage C"]["current_status"] == "FUTURE_GATE_LOCKED"
    assert stages["Stage D"]["current_status"] == "FUTURE_GATE_LOCKED"

    # Verify prohibitions
    assert any("Modifying production runtime code" in p for p in stages["Stage A"]["prohibited"])
    assert any("Ratifying the ADR" in p for p in stages["Stage B"]["prohibited"])
    assert any("Ratifying without empirical proof" in p for p in stages["Stage C"]["prohibited"])
    assert any("Any production merge prior to Stage C" in p for p in stages["Stage D"]["prohibited"])


# ---------------------------------------------------------------------------
# Test 07: RQ4 Minimum Future Evidence Checklist (Dynamic Evaluation)
# ---------------------------------------------------------------------------

def test_07_rq4_minimum_future_evidence(results_data: dict):
    rq4 = results_data["rq4_minimum_future_evidence"]
    assert rq4["candidates_audited"] == 12

    evals = {c["id"]: c for c in rq4["evaluations"]}
    assert evals["REQ-01"]["classification"] == "MANDATORY"  # E2E consumer experiment
    assert evals["REQ-02"]["classification"] == "CONDITIONALLY REQUIRED"  # EFE experiment
    assert evals["REQ-03"]["classification"] == "CONDITIONALLY REQUIRED"  # SLM conditioning
    assert evals["REQ-04"]["classification"] == "OPTIONAL / SUPPORTING"  # Avatar expression
    assert evals["REQ-05"]["classification"] == "MANDATORY"  # Multi-session stability
    assert evals["REQ-06"]["classification"] == "MANDATORY"  # Multi-turn recovery
    assert evals["REQ-07"]["classification"] == "MANDATORY"  # Cross-seed reproducibility
    assert evals["REQ-08"]["classification"] == "MANDATORY"  # Outside G1
    assert evals["REQ-09"]["classification"] == "MANDATORY"  # Active Inference adaptive
    assert evals["REQ-10"]["classification"] == "MANDATORY"  # C0 regression
    assert evals["REQ-11"]["classification"] == "MANDATORY"  # Failure-mode testing
    assert evals["REQ-12"]["classification"] == "MANDATORY"  # Latency/budget SLA

    summary = rq4["classification_summary"]
    assert summary["MANDATORY"] == 9
    assert summary["CONDITIONALLY_REQUIRED"] == 2
    assert summary["OPTIONAL_SUPPORTING"] == 1
    assert summary["NOT_REQUIRED"] == 0


# ---------------------------------------------------------------------------
# Test 08: RQ5 End-to-End Evidence Gap & Adapter Scope Lock
# ---------------------------------------------------------------------------

def test_08_rq5_end_to_end_evidence_gap(results_data: dict):
    rq5 = results_data["rq5_end_to_end_evidence_gap"]
    assert rq5["gaps_audited"] == 5
    gaps = {g["dimension"]: g for g in rq5["gaps"]}

    assert "CANNOT_CROSS" in gaps["Action Selection Mechanics"]["bridgeability_verdict"]
    assert "CANNOT_CROSS" in gaps["Tone & Pragmatic Modulation"]["bridgeability_verdict"]
    assert "REQUIRES_STRICT_SAFETY_HARNESS" in gaps["Safety & BoundaryLayer Enforcement"]["bridgeability_verdict"]
    assert "REQUIRES_CONCURRENCY_BENCHMARK" in gaps["Concurrency & Lock Disciplines"]["bridgeability_verdict"]
    assert "REQUIRES_AVATAR_INTERPOLATION_STUDY" in gaps["Visual Avatar Embodiment"]["bridgeability_verdict"]

    assert "categorical, not quantitative" in rq5["core_conclusion"]


# ---------------------------------------------------------------------------
# Test 09: RQ6 Scalar C0 Baseline Regression & Metric Categorization
# ---------------------------------------------------------------------------

def test_09_rq6_c0_regression_metrics(results_data: dict):
    rq6 = results_data["rq6_c0_regression_requirement"]
    assert len(rq6["canonical_requirements"]) == 4
    assert len(rq6["proposed_research_metrics"]) == 5
    assert len(rq6["future_acceptance_thresholds"]) == 3

    canon_names = [r["requirement"] for r in rq6["canonical_requirements"]]
    assert "Zero GPU VRAM Allocation" in canon_names
    assert "Lock Hierarchy & Holding Time Discipline" in canon_names
    assert "Strict BoundaryLayer Regex Compliance" in canon_names
    assert "Zero Limbic State / Philia Mutation" in canon_names

    metric_names = [m["metric"] for m in rq6["proposed_research_metrics"]]
    assert any("Action Divergence" in m for m in metric_names)
    assert any("Clarification" in m for m in metric_names)
    assert any("Reasoning Depth" in m for m in metric_names)
    assert any("Latency" in m for m in metric_names)

    # Verify thresholds are explicitly deferred to future specifications
    thresh_status = [t["status"] for t in rq6["future_acceptance_thresholds"]]
    assert all(s == "FUTURE_ACCEPTANCE_THRESHOLD" for s in thresh_status)


# ---------------------------------------------------------------------------
# Test 10: RQ7 Robustness Boundary Classifications
# ---------------------------------------------------------------------------

def test_10_rq7_robustness_boundary(results_data: dict):
    rq7 = results_data["rq7_robustness_boundary"]
    assert rq7["parameters_audited"] == 9
    params = {p["parameter"]: p for p in rq7["parameters"]}

    # Philia baseline and Euclidean metric are mathematical-general
    assert any(p["classification"] == "MATHEMATICAL-GENERAL" and "Philia" in k for k, p in params.items())
    assert any(p["classification"] == "MATHEMATICAL-GENERAL" and "Euclidean" in k for k, p in params.items())

    # G1, English, ODE params, T<=25, adaptation, deadband, exposure ramp are regime-bound
    assert any(p["classification"] == "EMPIRICALLY REGIME-BOUND" and "G1" in k for k, p in params.items())
    assert any(p["classification"] == "EMPIRICALLY REGIME-BOUND" and "English" in k for k, p in params.items())
    assert any(p["classification"] == "EMPIRICALLY REGIME-BOUND" and "Deadband" in k for k, p in params.items())
    assert any(p["classification"] == "EMPIRICALLY REGIME-BOUND" and "Exposure Weighting" in k for k, p in params.items())

    summary = rq7["classification_summary"]
    assert summary["MATHEMATICAL-GENERAL"] == 2
    assert summary["EMPIRICALLY_REGIME-BOUND"] == 7
    assert summary["UNKNOWN"] == 0


# ---------------------------------------------------------------------------
# Test 11: RQ8 Actionable Future Validation Matrix
# ---------------------------------------------------------------------------

def test_11_rq8_future_validation_matrix(results_data: dict):
    rq8 = results_data["rq8_future_validation_matrix"]
    assert rq8["validation_items_count"] == 11
    matrix = {row["claim_area"]: row for row in rq8["matrix"]}

    # Verify essential claim areas
    assert "R3 Measurement Semantics" in matrix
    assert "Temporal Stability" in matrix
    assert "Policy Utility" in matrix
    assert "EFE Action Valuation" in matrix
    assert "SLM Conditioning" in matrix
    assert "Affective Expression (15D)" in matrix
    assert "Physical Embodiment" in matrix
    assert "Memory Formation" in matrix
    assert "Relational Consolidation" in matrix
    assert "Safety & Boundaries" in matrix
    assert "Computational Overhead" in matrix

    # Relational consolidation is permanently barred
    assert matrix["Relational Consolidation"]["required_governance_gate"] == "PERMANENTLY_BARRED"
    assert "EXCLUDED FROM FUTURE ADMISSION" in matrix["Relational Consolidation"]["required_future_study"]


# ---------------------------------------------------------------------------
# Test 12: RQ9 & RQ10 ADR-029 Evidence Boundary and Dynamic Readiness
# ---------------------------------------------------------------------------

def test_12_rq9_rq10_adr029_boundaries_and_readiness(results_data: dict):
    rq9 = results_data["rq9_adr029_evidence_boundary"]
    assert len(rq9["adr029_may_claim"]) == 7
    assert len(rq9["adr029_may_state_as_open_question"]) == 4
    assert len(rq9["adr029_must_not_claim"]) == 5

    must_not = " ".join(rq9["adr029_must_not_claim"])
    assert "production" in must_not.lower()
    assert "approved" in must_not.lower()
    assert "reasoning depth" in must_not.lower()

    rq10 = results_data["rq10_readiness_state"]
    assert rq10["assigned_status"] == "READY_FOR_DRAFT_UPDATE"
    assert rq10["production_architecture_gate"] == "STRICTLY LOCKED"
    assert rq10["adr_ratification_status"] == "NOT RATIFIED / ARCHIVAL DRAFT RECORD ONLY"

    checklist = rq10["readiness_checklist"]
    assert len(checklist) == 12
    assert all(checklist.values()) is True
    assert "READY FOR DRAFT UPDATE != READY FOR ARCHITECTURAL DECISION" in rq10["governance_distinction"]
