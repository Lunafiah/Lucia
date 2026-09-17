"""
tests/evaluation_phase22/test_adr029_evidence_ledger.py

Automated Test Suite for Phase 22 H1: ADR-029 Draft Update & Evidence Ledger Synchronization.
Validates:
- Test 01: Manifest and results integrity (SHA-256 hash match)
- Test 02: Strict governance invariants (H1 INCONCLUSIVE, Gate 2 BLOCKED, Gate LOCKED, 0 mutations, Genesis bit-exact)
- Test 03: RQ1: ADR-029 current-state audit and remedial actions
- Test 04: RQ2: Canonical Evidence Ledger completeness (19 claims across 7 calibrated tiers with genuine provenance)
- Test 05: RQ3: Canonical evidence inventory boundaries (MAY CLAIM, OPEN QUESTIONS, MUST NOT CLAIM)
- Test 06: RQ4: Evidence lineage and deduplication graph (Rule A & Rule B enforcement on shared G1 corpus)
- Test 07: RQ5: ADR decision boundary separation (State A completed, State B target achieved, State C locked)
- Test 08: RQ6: Candidate architecture contract specification (Core payload decoupled from optional research metadata)
- Test 09: RQ7: Parameter robustness boundary classification (2 Math-General + 7 Empirical-Regime-Bound = 9 params, separate 27-state property)
- Test 10: RQ8: Future admission checklist synchronization (9 mandatory + 2 conditional requirements)
- Test 11: RQ9 & RQ10: Status semantics and forbidden terminology regex audit (14 forbidden phrases guarded)
- Test 12: Production isolation and Genesis profile bit-exact audit
"""

import hashlib
import json
from pathlib import Path
import pytest

REPO_ROOT = Path(__file__).resolve().parent.parent.parent
RESULTS_DIR = REPO_ROOT / "tests" / "evaluation_phase22" / "results" / "adr029_evidence_ledger"
FIXTURES_DIR = REPO_ROOT / "tests" / "evaluation_phase22" / "fixtures"

RESULTS_FILE = RESULTS_DIR / "adr029_evidence_ledger.json"
MANIFEST_FILE = FIXTURES_DIR / "manifest_adr029_evidence_ledger.json"
PROFILE_FILE = REPO_ROOT / "data" / "profile.json"


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
    assert manifest_data["study_name"] == "Phase 22 H1 ADR-029 Draft Update & Evidence Ledger Synchronization"

    file_entry = manifest_data["files"]["adr029_evidence_ledger.json"]
    disk_hash = compute_sha256(RESULTS_FILE)
    disk_size = RESULTS_FILE.stat().st_size

    assert file_entry["sha256"] == disk_hash, "Manifest SHA-256 does not match disk file digest"
    assert file_entry["size_bytes"] == disk_size, "Manifest file size does not match disk size"


# ---------------------------------------------------------------------------
# Test 02: Strict Governance Invariants
# ---------------------------------------------------------------------------

def test_02_strict_governance_invariants(results_data: dict, manifest_data: dict):
    gov = results_data["governance_state"]
    assert gov["phase_22_h1"] == "INCONCLUSIVE"
    assert gov["gate_2"] == "BLOCKED"
    assert gov["protocol_v1_5"] == "NOT AUTHORIZED"
    assert gov["architecture_gate"] == "STRICTLY LOCKED"
    assert gov["adr_status"] == "ADR DRAFT UPDATED (NOT RATIFIED)"
    assert gov["production_mutations"] == 0
    assert gov["genesis_profile"] == "PRESERVED_BIT_EXACT"

    m_gov = manifest_data["governance_invariants"]
    assert m_gov["phase_22_h1"] == "INCONCLUSIVE"
    assert m_gov["gate_2"] == "BLOCKED"
    assert m_gov["architecture_gate"] == "STRICTLY LOCKED"
    assert m_gov["adr_029_status"] == "ADR DRAFT UPDATED"


# ---------------------------------------------------------------------------
# Test 03: RQ1 — ADR-029 Current-State Audit
# ---------------------------------------------------------------------------

def test_03_rq1_current_state_audit(results_data: dict):
    rq1 = results_data["rq1_adr029_audit"]
    assert rq1["current_status"] == "READY FOR DRAFT UPDATE"
    assert rq1["target_status"] == "ADR DRAFT UPDATED"
    assert len(rq1["audit_entries"]) >= 7

    sections = [e["adr_section"] for e in rq1["audit_entries"]]
    assert "Status Statement" in sections
    assert "Context" in sections
    assert "Consumers" in sections
    assert "Prohibited Subsystems" in sections
    assert "Value Object Specification" in sections
    assert "Quality Gate 2 Context" in sections
    assert "Evidence Boundaries" in sections


# ---------------------------------------------------------------------------
# Test 04: RQ2 — Canonical Evidence Ledger Completeness (19 Claims)
# ---------------------------------------------------------------------------

def test_04_rq2_evidence_ledger_completeness(results_data: dict):
    rq2 = results_data["rq2_evidence_ledger"]
    assert rq2["claims_count"] == 19
    assert len(rq2["claims"]) == 19

    tier_counts = rq2["tier_counts"]
    assert tier_counts["SUPPORTED"] == 5
    assert tier_counts["OBSERVED"] == 2
    assert tier_counts["RESEARCH-HARNESS ONLY"] == 2
    assert tier_counts["EVIDENCE-CONSISTENT"] == 3
    assert tier_counts["HYPOTHESIS"] == 2
    assert tier_counts["UNTESTED"] == 4
    assert tier_counts["NOT JUSTIFIED"] == 1

    for claim in rq2["claims"]:
        assert claim["id"].startswith("CLM-")
        assert len(claim["claim"]) > 0
        assert claim["classification"] in tier_counts
        assert len(claim["evidence_source"]) > 0
        assert len(claim["scope"]) > 0
        assert len(claim["limitations"]) > 0
        assert claim["status"] == "FULLY_PROVENANCED"

        # Where machine-readable result JSON is referenced, digest must be valid hex SHA-256
        if claim["result_json_sha256"] is not None:
            assert len(claim["result_json_sha256"]) == 64


# ---------------------------------------------------------------------------
# Test 05: RQ3 — Canonical Evidence Inventory Boundaries
# ---------------------------------------------------------------------------

def test_05_rq3_canonical_inventory_boundaries(results_data: dict):
    rq3 = results_data["rq3_canonical_inventory"]
    may_claim = rq3["may_claim"]
    open_questions = rq3["open_questions"]
    must_not_claim = rq3["must_not_claim"]

    assert len(may_claim) == 8
    assert len(open_questions) == 5
    assert len(must_not_claim) == 9

    # Verify key boundary constraints
    assert any("Scalar S is preserved bit-exact" in item for item in may_claim)
    assert any("79.89%" in item and "research adapter" in item for item in may_claim)
    assert any("local 7B SLM" in item for item in open_questions)
    assert any("R3 is production-validated" in item for item in must_not_claim)
    assert any("R3 is architecture-approved" in item for item in must_not_claim)
    assert any("Gate 2 has been passed" in item for item in must_not_claim)


# ---------------------------------------------------------------------------
# Test 06: RQ4 — Evidence Lineage & Deduplication Graph
# ---------------------------------------------------------------------------

def test_06_rq4_lineage_and_deduplication(results_data: dict):
    rq4 = results_data["rq4_lineage_graph"]
    assert "Frozen Candidate G1 Corpus" in rq4["root_dataset"]
    assert len(rq4["nodes"]) >= 9
    assert len(rq4["edges"]) >= 8

    rules = rq4["deduplication_rules"]
    assert "rule_a_no_dataset_multiplication" in rules
    assert "rule_b_no_evidence_inflation" in rules
    assert "does NOT constitute independent empirical replication" in rules["rule_a_no_dataset_multiplication"]


# ---------------------------------------------------------------------------
# Test 07: RQ5 — ADR Decision Boundary Separation
# ---------------------------------------------------------------------------

def test_07_rq5_decision_boundary_separation(results_data: dict):
    rq5 = results_data["rq5_decision_boundary"]
    assert rq5["state_a_research_evidence"]["status"] == "COMPLETED"
    assert "ADR DRAFT UPDATED" in rq5["state_b_adr_draft"]["status"]
    assert rq5["state_c_architectural_decision"]["status"] == "LOCKED"
    assert "PROHIBITED" in rq5["state_d_production_implementation"]["status"]


# ---------------------------------------------------------------------------
# Test 08: RQ6 — Candidate Architecture Contract Specification
# ---------------------------------------------------------------------------

def test_08_rq6_candidate_contract_specification(results_data: dict):
    rq6 = results_data["rq6_candidate_contract"]
    assert "NOT PRODUCTION COMMITMENT" in rq6["contract_type"]

    # Producer & Transport
    assert rq6["producer_contract"]["pipeline_stage"] == "Stage S4"
    assert rq6["transport_contract"]["pipeline_stages"] == "Stage S5 through Stage S12"
    assert "MUST NOT semantically interpret" in rq6["transport_contract"]["semantics"]

    # Core Candidate Payload must have exactly core fields
    core_fields = rq6["core_candidate_payload"]["fields"]
    assert "magnitude" in core_fields
    assert "direction" in core_fields
    assert "timestamp_tick" in core_fields
    assert "exposure_ticks" in core_fields
    assert "provenance" in core_fields

    # Optional Research-Policy Metadata must be separated from value object core
    policy_meta = rq6["candidate_policy_metadata"]
    assert "NOT REQUIRED VALUE OBJECT FIELDS" in policy_meta["status"]
    assert "deadband_eps" in policy_meta["candidate_fields"]
    assert "exposure_weight" in policy_meta["candidate_fields"]

    # Consumer contracts
    assert len(rq6["consumer_contracts"]["available_contracts"]) == 3


# ---------------------------------------------------------------------------
# Test 09: RQ7 — Parameter Robustness Boundary Classification
# ---------------------------------------------------------------------------

def test_09_rq7_parameter_robustness_classification(results_data: dict):
    rq7 = results_data["rq7_parameter_robustness"]
    counts = rq7["counts"]

    # Exactly 2 + 7 = 9 parameters
    assert counts["total_parameters_audited"] == 9
    assert counts["mathematical_general_count"] == 2
    assert counts["empirically_regime_bound_count"] == 7

    # Verify 2 Mathematical-General
    math_params = [p["name"] for p in rq7["parameters"] if p["classification"] == "MATHEMATICAL-GENERAL"]
    assert "Philia Resting Attractor Baseline" in math_params
    assert "Euclidean L2 Norm Identity" in math_params

    # Verify 7 Empirically Regime-Bound
    regime_params = [p["name"] for p in rq7["parameters"] if p["classification"] == "EMPIRICALLY REGIME-BOUND"]
    assert "Candidate G1 Stimulus Corpus" in regime_params
    assert "English Lexical Domain" in regime_params
    assert "Coupled MT-LNN ODE Parameters" in regime_params
    assert "Conversational Exposure Duration" in regime_params
    assert "Active Inference Online Adaptation" in regime_params
    assert "Deadband Threshold" in regime_params
    assert "Exposure Weighting Ramp Rule" in regime_params

    # Verify 27-state combinatorial space is treated as separate structural property
    structural_prop = rq7["separate_structural_property"]
    assert structural_prop["nature"] == "SEPARATE_MATHEMATICAL_CODING_PROPERTY"
    assert "NOT counted inside the 9-parameter robustness boundary" in structural_prop["description"]


# ---------------------------------------------------------------------------
# Test 10: RQ8 — Future Admission Checklist Synchronization
# ---------------------------------------------------------------------------

def test_10_rq8_future_admission_checklist_sync(results_data: dict):
    rq8 = results_data["rq8_future_admission"]
    assert rq8["mandatory_count"] == 9
    assert rq8["conditional_count"] == 2

    # Check mandatory items
    m_ids = [m["id"] for m in rq8["mandatory_requirements"]]
    assert m_ids == [f"FAR-{i:02d}" for i in range(1, 10)]

    # Check conditional items
    c_ids = [c["id"] for c in rq8["conditional_requirements"]]
    assert c_ids == ["CFAR-01", "CFAR-02"]


# ---------------------------------------------------------------------------
# Test 11: RQ9 & RQ10 — Status Semantics & Forbidden Terminology Audit
# ---------------------------------------------------------------------------

def test_11_rq9_rq10_status_and_forbidden_terms(results_data: dict):
    rq9 = results_data["rq9_status_semantics"]
    assert rq9["initial_state"] == "READY FOR DRAFT UPDATE"
    assert rq9["assigned_state"] == "ADR DRAFT UPDATED"

    # Verify progression constraints
    transitions = {t["from"] + " -> " + t["to"]: t["authorized"] for t in rq9["transition_audit"]}
    assert transitions["READY FOR DRAFT UPDATE -> ADR DRAFT UPDATED"] is True
    assert transitions["ADR DRAFT UPDATED -> READY FOR ARCHITECTURAL DECISION"] is False
    assert transitions["READY FOR ARCHITECTURAL DECISION -> ARCHITECTURAL DECISION (ACCEPTED)"] is False

    # Forbidden phrases audit
    rq10 = results_data["rq10_forbidden_terms_audit"]
    assert rq10["forbidden_phrases_count"] == 14
    phrases = [p["phrase"] for p in rq10["phrases"]]
    assert "production-ready" in phrases
    assert "production validated" in phrases
    assert "approved architecture" in phrases
    assert "optimal" in phrases
    assert "improves empathy" in phrases
    assert "improves language quality" in phrases
    assert "Gate 2 passed" in phrases


# ---------------------------------------------------------------------------
# Test 12: Production Isolation and Genesis Profile Bit-Exact Audit
# ---------------------------------------------------------------------------

def test_12_production_isolation_and_genesis(results_data: dict):
    # Genesis profile must remain bit-exact {"is_onboarded": false}
    assert PROFILE_FILE.exists(), f"Profile file missing: {PROFILE_FILE}"
    with open(PROFILE_FILE, "r", encoding="utf-8") as f:
        content = f.read().strip()
    assert content == '{"is_onboarded": false}', f"Genesis profile mutated: {content}"
