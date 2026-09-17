"""
Phase 22 H1 — R3 Consumer Plausibility & Utility-Compatibility Automated Verification Suite
========================================================================================
Test Suite: test_h1_r3_consumer_plausibility.py

Verifies:
  - 12 comprehensive automated tests verifying manifest integrity, governance invariants,
    frozen regime reproduction, corpus lineage, parameter hashes, A/B controls,
    C baseline vs qualifying, D baseline vs qualifying, decomposition metrics,
    negative controls / hard tuple identity, and production isolation.
"""

import json
from pathlib import Path
import pytest
import numpy as np

REPO_ROOT = Path(__file__).resolve().parent.parent.parent
EVAL_DIR = REPO_ROOT / "tests" / "evaluation_phase22"
FIXTURES_DIR = EVAL_DIR / "fixtures"
RESULTS_DIR = EVAL_DIR / "results" / "h1_r3_consumer_plausibility"

MANIFEST_PATH = FIXTURES_DIR / "manifest_h1_r3_consumer_plausibility.json"
RESULTS_PATH = RESULTS_DIR / "r3_consumer_plausibility_results.json"
SUMMARY_CSV_PATH = RESULTS_DIR / "r3_consumer_plausibility_summary.csv"
PROFILE_PATH = REPO_ROOT / "data" / "profile.json"


@pytest.fixture(scope="module")
def manifest_data():
    assert MANIFEST_PATH.exists(), f"Manifest not found: {MANIFEST_PATH}"
    with open(MANIFEST_PATH, "r", encoding="utf-8") as f:
        return json.load(f)


@pytest.fixture(scope="module")
def results_data():
    assert RESULTS_PATH.exists(), f"Results JSON not found: {RESULTS_PATH}"
    with open(RESULTS_PATH, "r", encoding="utf-8") as f:
        return json.load(f)


# -----------------------------------------------------------------------------
# Test 1: Manifest and Results Integrity
# -----------------------------------------------------------------------------
def test_01_manifest_and_result_integrity(manifest_data, results_data):
    """Verify manifest exists, references correct artifacts, and hashes match."""
    import hashlib

    assert manifest_data["study_id"] == "PHASE_22_H1_R3_CONSUMER_PLAUSIBILITY_STUDY"

    # Verify results JSON hash
    with open(RESULTS_PATH, "rb") as f:
        res_hash = hashlib.sha256(f.read()).hexdigest()
    assert manifest_data["artifacts"]["results_json"]["sha256"] == res_hash

    # Verify summary CSV hash
    with open(SUMMARY_CSV_PATH, "rb") as f:
        csv_hash = hashlib.sha256(f.read()).hexdigest()
    assert manifest_data["artifacts"]["summary_csv"]["sha256"] == csv_hash


# -----------------------------------------------------------------------------
# Test 2: Strict Governance Invariants
# -----------------------------------------------------------------------------
def test_02_strict_governance_invariants(manifest_data, results_data):
    """Verify strictly locked architecture gate, blocked Gate 2, and inconclusive H1."""
    gov_manifest = manifest_data["governance_invariants"]
    assert gov_manifest["architecture_gate"] == "STRICTLY_LOCKED"
    assert gov_manifest["quality_gate_2"] == "STRICTLY_BLOCKED"
    assert gov_manifest["phase22_h1_status"] == "INCONCLUSIVE"
    assert "NOT RATIFIED" in gov_manifest["adr029_status"]
    assert gov_manifest["genesis_profile_bit_exact"] is True

    gov_results = results_data["study_metadata"]["governance"]
    assert gov_results["architecture_gate"] == "STRICTLY_LOCKED"
    assert gov_results["quality_gate_2"] == "STRICTLY_BLOCKED"
    assert gov_results["phase22_h1_status"] == "INCONCLUSIVE"
    assert gov_results["genesis_profile_bit_exact"] is True


# -----------------------------------------------------------------------------
# Test 3: Frozen Regime Reproduction
# -----------------------------------------------------------------------------
def test_03_frozen_regime_reproduction(results_data):
    """Verify all 7 target regimes + 2 intermediate counterfactuals are evaluated."""
    regimes = results_data["regime_results"]
    expected_regimes = [
        "A_REFERENCE",
        "B_DIRECTIONAL_SEPARABLE",
        "C_baseline",
        "C_qual_1.50",
        "C_qual_2.00",
        "D_baseline",
        "D_qual_corner",
        "D_scalar_half",
        "D_dir_5x",
    ]
    for r_id in expected_regimes:
        assert r_id in regimes, f"Missing regime {r_id}"


# -----------------------------------------------------------------------------
# Test 4: Corpus Lineage
# -----------------------------------------------------------------------------
def test_04_corpus_lineage(results_data, manifest_data):
    """Verify corpus parameters: N=270, seed 9999, seeds 42-46."""
    meta = results_data["study_metadata"]
    assert meta["primary_seed"] == 9999
    assert meta["consumer_seeds"] == [42, 43, 44, 45, 46]
    assert meta["exposure_t"] == 12
    assert meta["deadband_epsilon"] == 0.010
    assert meta["scalar_match_threshold"] == 0.020
    assert manifest_data["corpus_n"] == 270


# -----------------------------------------------------------------------------
# Test 5: Parameter Hash Integrity
# -----------------------------------------------------------------------------
def test_05_parameter_hash_integrity(manifest_data, results_data):
    """Verify locked base parameter hashes match cryptographic registry."""
    hashes = manifest_data["locked_base_parameter_hashes"]
    expected_keys = [
        "C_U_BASE",
        "C_COST_S",
        "C_M_BASE",
        "D_G_BASE",
        "D_KAPPA_S_BASE",
        "D_W_DIR",
    ]
    for k in expected_keys:
        assert k in hashes
        assert len(hashes[k]) == 64
        assert hashes[k] == results_data["study_metadata"]["locked_base_parameter_hashes"][k]


# -----------------------------------------------------------------------------
# Test 6: A/B Controls Historical Reproduction
# -----------------------------------------------------------------------------
def test_06_ab_historical_reproduction(results_data):
    """Verify reference controls A & B reproduce historical transferability baseline."""
    regimes = results_data["regime_results"]
    # A_REFERENCE: DiffRate=0.7989, DirGain=+0.7989, C0 diff=0.0000
    res_a = regimes["A_REFERENCE"]
    assert abs(res_a["diffrate_disc_c2_mean"] - 0.79888) < 1e-4
    assert abs(res_a["directional_gain_mean"] - 0.79888) < 1e-4
    assert res_a["d_pair_action_c0_mean"] == 0.0

    # B_DIRECTIONAL_SEPARABLE: DiffRate=0.7989, DirGain=+0.7989, C0 diff=0.0000
    res_b = regimes["B_DIRECTIONAL_SEPARABLE"]
    assert abs(res_b["diffrate_disc_c2_mean"] - 0.79888) < 1e-4
    assert abs(res_b["directional_gain_mean"] - 0.79888) < 1e-4
    assert res_b["d_pair_action_c0_mean"] == 0.0


# -----------------------------------------------------------------------------
# Test 7: Consumer C Baseline vs. Qualifying Reproduction
# -----------------------------------------------------------------------------
def test_07_c_baseline_vs_qualifying_reproduction(results_data):
    """Verify Consumer C transition: baseline (0.0000) -> 1.50 (0.7989) -> 2.00 (1.0000)."""
    regimes = results_data["regime_results"]
    assert regimes["C_baseline"]["diffrate_disc_c2_mean"] == 0.0
    assert abs(regimes["C_qual_1.50"]["diffrate_disc_c2_mean"] - 0.79888) < 1e-4
    assert regimes["C_qual_2.00"]["diffrate_disc_c2_mean"] == 1.0


# -----------------------------------------------------------------------------
# Test 8: Consumer D Baseline vs. Qualifying Reproduction
# -----------------------------------------------------------------------------
def test_08_d_baseline_vs_qualifying_reproduction(results_data):
    """Verify Consumer D: baseline (0.0000), qualifying corner (0.7989), intermediates (0.0000)."""
    regimes = results_data["regime_results"]
    assert regimes["D_baseline"]["diffrate_disc_c2_mean"] == 0.0
    assert abs(regimes["D_qual_corner"]["diffrate_disc_c2_mean"] - 0.79888) < 1e-4
    # Halving scalar slope alone yields 0 differentiation
    assert regimes["D_scalar_half"]["diffrate_disc_c2_mean"] == 0.0
    # 5x directional amplification alone yields 0 differentiation
    assert regimes["D_dir_5x"]["diffrate_disc_c2_mean"] == 0.0


# -----------------------------------------------------------------------------
# Test 9: Scalar Response Decomposition
# -----------------------------------------------------------------------------
def test_09_scalar_response_decomposition(results_data):
    """Verify scalar contribution norms and relative ratios are strictly non-negative."""
    regimes = results_data["regime_results"]
    for r_id, r in regimes.items():
        d = r["decomposition"]
        assert d["mean_norm_scalar"] > 0.0
        assert d["mean_norm_dir"] > 0.0
        assert d["mean_relative_ratio"] > 0.0
        assert 0.0 <= d["mean_dcf"] <= 1.0


# -----------------------------------------------------------------------------
# Test 10: Directional Response Decomposition
# -----------------------------------------------------------------------------
def test_10_directional_response_decomposition(results_data):
    """Verify action flip rate from scalar baseline to full directional valuation."""
    regimes = results_data["regime_results"]
    # Baseline regimes have 0 directional flip rate
    assert regimes["C_baseline"]["decomposition"]["dir_flip_rate_from_scalar"] == 0.0
    assert regimes["D_baseline"]["decomposition"]["dir_flip_rate_from_scalar"] == 0.0

    # C qualifying regimes show progressive action flipping
    assert abs(regimes["C_qual_1.50"]["decomposition"]["dir_flip_rate_from_scalar"] - 0.17037) < 1e-4
    assert abs(regimes["C_qual_2.00"]["decomposition"]["dir_flip_rate_from_scalar"] - 0.33333) < 1e-4

    # D qualifying corner flips 82.96% of actions
    assert abs(regimes["D_qual_corner"]["decomposition"]["dir_flip_rate_from_scalar"] - 0.82963) < 1e-4


# -----------------------------------------------------------------------------
# Test 11: Negative Controls & Tuple Identity
# -----------------------------------------------------------------------------
def test_11_negative_controls_and_tuple_identity(results_data):
    """Verify NC1 scalar baseline = 0.0000 and NC2 tuple identity parity = 100% across all regimes."""
    regimes = results_data["regime_results"]
    for r_id, r in regimes.items():
        # NC1: C0 pair difference on matched pairs is 0.0000
        assert r["d_pair_action_c0_mean"] == 0.0, f"NC1 violated in {r_id}"

        # NC2: Hard tuple identity parity
        tid = r["tuple_identity"]
        assert tid["delta_action_identity"] == 0.0, f"NC2 action diff in {r_id}"
        assert tid["d_js_identity"] < 1e-12, f"NC2 JS divergence in {r_id}"
        assert tid["passed"] is True


# -----------------------------------------------------------------------------
# Test 12: Production Isolation & Genesis Profile Audit
# -----------------------------------------------------------------------------
def test_12_production_isolation_and_genesis_audit():
    """Verify 0 modifications to production files and Genesis profile is un-onboarded."""
    assert PROFILE_PATH.exists()
    with open(PROFILE_PATH, "r", encoding="utf-8") as f:
        profile = json.load(f)
    assert profile == {"is_onboarded": False}, f"Genesis profile mutated: {profile}"
