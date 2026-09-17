"""
tests/evaluation_phase22/test_h1_r3_consumer_transferability.py

Automated Test Suite for Phase 22 H1: R3 Consumer Transferability & Adapter Dependence Study.
Validates:
- Test 01: Manifest and results integrity (SHA-256 digest match)
- Test 02: Strict governance invariants (H1 INCONCLUSIVE, Gate 2 BLOCKED, Gate LOCKED, 0 mutations, Genesis bit-exact)
- Test 03: Consumer specification determinism & frozen parameter hashes
- Test 04: Corpus lineage (Seed 9999 root, N=270, exposure T=12, consumer seeds 42-46)
- Test 05: Matched-pair partition reproducibility (6,734 total, 358 discordant, 6,376 same direction)
- Test 06: Hard tuple identity parity invariant (delta_action = 0, D_JS < 1e-12)
- Test 07: Reference consumer A reproducibility (C2 DiffRate = 0.7989, Dir Gain = 0.7989)
- Test 08: Directional separable consumer B transfer verification (C2 DiffRate = 0.7989, transfer satisfied)
- Test 09: Continuous utility consumer C analysis (continuous Delta V > 0 under C0 and C2, argmax masking observed)
- Test 10: Magnitude dominant consumer D sensitivity analysis (directional differentiation suppressed)
- Test 11: Cross-consumer transferability metric calculation (R_transfer = 1/3 = 0.3333, conclusion = PARTIAL_TRANSFERABILITY_PARTIAL_ADAPTER_DEPENDENCE)
- Test 12: Production isolation and Genesis profile bit-exact audit
"""

import hashlib
import json
from pathlib import Path
import pytest

REPO_ROOT = Path(__file__).resolve().parent.parent.parent
RESULTS_DIR = REPO_ROOT / "tests" / "evaluation_phase22" / "results" / "h1_r3_consumer_transferability"
FIXTURES_DIR = REPO_ROOT / "tests" / "evaluation_phase22" / "fixtures"

RESULTS_FILE = RESULTS_DIR / "r3_consumer_transferability_results.json"
SUMMARY_CSV = RESULTS_DIR / "r3_consumer_transferability_summary.csv"
MANIFEST_FILE = FIXTURES_DIR / "manifest_h1_r3_consumer_transferability.json"
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
    assert manifest_data["study_name"] == "Phase 22 H1 R3 Consumer Transferability & Adapter Dependence Study"

    res_entry = manifest_data["files"]["r3_consumer_transferability_results.json"]
    disk_hash = compute_sha256(RESULTS_FILE)
    disk_size = RESULTS_FILE.stat().st_size
    assert res_entry["sha256"] == disk_hash
    assert res_entry["size_bytes"] == disk_size

    csv_entry = manifest_data["files"]["r3_consumer_transferability_summary.csv"]
    csv_disk_hash = compute_sha256(SUMMARY_CSV)
    csv_disk_size = SUMMARY_CSV.stat().st_size
    assert csv_entry["sha256"] == csv_disk_hash
    assert csv_entry["size_bytes"] == csv_disk_size


# ---------------------------------------------------------------------------
# Test 02: Strict Governance Invariants
# ---------------------------------------------------------------------------

def test_02_strict_governance_invariants(results_data: dict, manifest_data: dict):
    gov = results_data["governance_state"]
    assert gov["phase_22_h1"] == "INCONCLUSIVE"
    assert gov["gate_2"] == "STRICTLY BLOCKED"
    assert gov["protocol_v1_5"] == "NOT AUTHORIZED"
    assert gov["architecture_gate"] == "STRICTLY LOCKED"
    assert gov["adr_029_status"] == "DRAFT / RESEARCH RECORD ONLY / NOT RATIFIED"
    assert gov["production_mutations"] == 0
    assert gov["genesis_profile"] == "PRESERVED_BIT_EXACT"

    m_gov = manifest_data["governance_invariants"]
    assert m_gov["phase_22_h1"] == "INCONCLUSIVE"
    assert m_gov["gate_2"] == "STRICTLY BLOCKED"
    assert m_gov["architecture_gate"] == "STRICTLY LOCKED"
    assert m_gov["production_mutations"] == 0
    assert m_gov["genesis_profile"] == "PRESERVED_BIT_EXACT"


# ---------------------------------------------------------------------------
# Test 03: Consumer Specification Determinism & Frozen Parameters
# ---------------------------------------------------------------------------

def test_03_consumer_specification_determinism(results_data: dict):
    frozen_hashes = results_data["frozen_consumer_specifications_sha256"]
    assert len(frozen_hashes) == 4
    for c_id in ["A_REFERENCE", "B_DIRECTIONAL_SEPARABLE", "C_CONTINUOUS_UTILITY", "D_MAGNITUDE_DOMINANT"]:
        assert c_id in frozen_hashes
        assert len(frozen_hashes[c_id]) == 64


# ---------------------------------------------------------------------------
# Test 04: Corpus Lineage
# ---------------------------------------------------------------------------

def test_04_corpus_lineage(results_data: dict):
    lineage = results_data["corpus_lineage"]
    assert lineage["root_corpus"] == "Frozen Candidate G1 Stimulus Corpus"
    assert lineage["master_seed"] == 9999
    assert lineage["n_probes"] == 270
    assert lineage["probes_per_tier"] == 90
    assert lineage["exposure_ticks"] == 12
    assert lineage["consumer_robustness_seeds"] == [42, 43, 44, 45, 46]


# ---------------------------------------------------------------------------
# Test 05: Matched-Pair Partition Reproducibility
# ---------------------------------------------------------------------------

def test_05_matched_pair_partition_reproducibility(results_data: dict):
    pairs = results_data["matched_pairs_summary"]
    assert pairs["total_exhaustive_pairs"] == 6734
    assert pairs["discordant_matched_pairs_count"] == 358
    assert pairs["same_direction_matched_pairs_count"] == 6376
    assert pairs["scalar_match_tolerance"] == 0.02


# ---------------------------------------------------------------------------
# Test 06: Hard Tuple Identity Parity Invariant
# ---------------------------------------------------------------------------

def test_06_hard_tuple_identity_parity(results_data: dict):
    hard = results_data["hard_tuple_identity_parity"]
    assert hard["all_passed"] is True
    for c_id, res in hard["consumer_results"].items():
        assert res["delta_action_identity"] == 0.0
        assert res["d_js_identity"] < 1e-12
        assert res["invariant_passed"] is True


# ---------------------------------------------------------------------------
# Test 07: Reference Consumer A Reproducibility
# ---------------------------------------------------------------------------

def test_07_reference_consumer_a_reproducibility(results_data: dict):
    c_a = results_data["cross_consumer_evaluation"]["consumer_results"]["A_REFERENCE"]
    agg = c_a["aggregate"]
    assert round(agg["c2_diffrate_disc_mean"], 4) == 0.7989
    assert round(agg["c0_d_pair_action_mean"], 4) == 0.0000
    assert round(agg["directional_gain_mean"], 4) == 0.7989
    assert agg["condition_shift_c2_c4_mean"] > 0.2000

    crit = c_a["preregistered_criteria"]
    assert crit["criterion_1_diffrate_ge_20pct"]["passed"] is True
    assert crit["criterion_2_directional_gain_ge_10pct"]["passed"] is True
    assert crit["secondary_metric_condition_shift_c2_c4"]["observed"] > 0.2000
    assert crit["transfer_criteria_satisfied"] is True


# ---------------------------------------------------------------------------
# Test 08: Directional Separable Consumer B Transfer Verification
# ---------------------------------------------------------------------------

def test_08_directional_separable_consumer_b_transfer(results_data: dict):
    c_b = results_data["cross_consumer_evaluation"]["consumer_results"]["B_DIRECTIONAL_SEPARABLE"]
    agg = c_b["aggregate"]
    assert round(agg["c2_diffrate_disc_mean"], 4) == 0.7989
    assert round(agg["c0_d_pair_action_mean"], 4) == 0.0000
    assert round(agg["directional_gain_mean"], 4) == 0.7989
    assert agg["condition_shift_c2_c4_mean"] > 0.2000

    crit = c_b["preregistered_criteria"]
    assert crit["criterion_1_diffrate_ge_20pct"]["passed"] is True
    assert crit["criterion_2_directional_gain_ge_10pct"]["passed"] is True
    assert crit["secondary_metric_condition_shift_c2_c4"]["observed"] > 0.2000
    assert crit["transfer_criteria_satisfied"] is True


# ---------------------------------------------------------------------------
# Test 09: Continuous Utility Consumer C Analysis (RQ5 Follow-up)
# ---------------------------------------------------------------------------

def test_09_continuous_utility_consumer_c_analysis(results_data: dict):
    rq5 = results_data["rq5_continuous_utility_analysis"]
    assert rq5["scalar_continuous_contribution_exists"] is True
    assert rq5["argmax_masks_scalar_variation"] is True
    assert rq5["consumer_c_c0_mean_delta_v"] > 0.0100
    assert rq5["consumer_c_c2_mean_delta_v"] > 0.5000
    assert rq5["consumer_c_c0_d_pair_action"] == 0.0000
    assert rq5["consumer_c_c2_diffrate_disc"] == 0.0000

    c_c = results_data["cross_consumer_evaluation"]["consumer_results"]["C_CONTINUOUS_UTILITY"]
    crit = c_c["preregistered_criteria"]
    assert crit["transfer_criteria_satisfied"] is False


# ---------------------------------------------------------------------------
# Test 10: Magnitude Dominant Consumer D Sensitivity Analysis
# ---------------------------------------------------------------------------

def test_10_magnitude_dominant_consumer_d_sensitivity(results_data: dict):
    c_d = results_data["cross_consumer_evaluation"]["consumer_results"]["D_MAGNITUDE_DOMINANT"]
    agg = c_d["aggregate"]
    assert agg["c2_diffrate_disc_mean"] == 0.0000
    assert agg["directional_gain_mean"] == 0.0000
    assert agg["condition_shift_c2_c4_mean"] == 0.0000

    crit = c_d["preregistered_criteria"]
    assert crit["transfer_criteria_satisfied"] is False


# ---------------------------------------------------------------------------
# Test 11: Cross-Consumer Transferability Metric Calculation
# ---------------------------------------------------------------------------

def test_11_cross_consumer_transferability_calculation(results_data: dict, manifest_data: dict):
    summary = results_data["cross_consumer_evaluation"]["transferability_summary"]
    assert summary["satisfied_count"] == 1
    assert summary["total_independent_consumers"] == 3
    assert round(summary["r_transfer"], 4) == 0.3333
    assert summary["transfer_conclusion"] == "PARTIAL_TRANSFERABILITY_PARTIAL_ADAPTER_DEPENDENCE"

    m_sum = manifest_data["transferability_summary"]
    assert m_sum["satisfied_count"] == 1
    assert m_sum["total_independent_consumers"] == 3
    assert round(m_sum["r_transfer"], 4) == 0.3333
    assert m_sum["transfer_conclusion"] == "PARTIAL_TRANSFERABILITY_PARTIAL_ADAPTER_DEPENDENCE"


# ---------------------------------------------------------------------------
# Test 12: Production Isolation and Genesis Profile Bit-Exact Audit
# ---------------------------------------------------------------------------

def test_12_production_isolation_and_genesis_audit():
    assert PROFILE_FILE.exists(), f"Profile file missing: {PROFILE_FILE}"
    with open(PROFILE_FILE, "r", encoding="utf-8") as f:
        data = json.load(f)
    assert data == {"is_onboarded": False}, f"Genesis profile mutated: {data}"
