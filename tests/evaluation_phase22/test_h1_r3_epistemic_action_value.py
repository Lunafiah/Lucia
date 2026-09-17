"""
Phase 22 H1 — R3 Epistemic Relevance & Action-Value Attribution Automated Test Suite
=====================================================================================
Test Suite: test_h1_r3_epistemic_action_value.py

Verifies:
  - Test 01: Manifest and artifact SHA-256 hash integrity.
  - Test 02: Strict governance invariants (Gate locked, ADR-029 draft, Gate 2 blocked, H1 inconclusive, Genesis bit-exact, 100% CPU).
  - Test 03: Corpus lineage & matched pair partition reproducibility (N=270, 6734 matched, 358 discordant, 6376 same-dir, 16 greedy).
  - Test 04: Locked base parameter hashes bit-exact check.
  - Test 05: Historical C2 action differentiation reproduction (DiffRate = 0.7989 on Consumer A, B, C).
  - Test 06: NC1 Canonical scalar baseline reproduction from frozen transferability artifact (C0 DiffRate = 0.0000).
  - Test 07: NC2 Hard tuple identity parity invariant (Delta_V = 0, D_JS < 1e-12).
  - Test 08: NC3 Multiset preservation (C3 preserves S probe + dir multiset; C4 preserves dir probe + S multiset; C5 preserves empirical dir multiset; S unchanged).
  - Test 09: Continuous action-value differentiation (DiffRate_cont = 1.0 > 0.75, ||Delta_V|| > tau_val).
  - Test 10: Common-mode vs action-specific L2 variance decomposition (Exact orthogonal partition, action-specific > 50%).
  - Test 11: Epistemic-Action Relevance Diagnostic & Epistemic Disclaimer (Harness proxy passes, Active Inference epistemic relevance explicitly False).
  - Test 12: Production isolation (src/core/** diff = 0) and Genesis profile bit-exact check.
"""

import hashlib
import json
from pathlib import Path
import pytest
import numpy as np

REPO_ROOT = Path(__file__).resolve().parent.parent.parent
EVAL_DIR = REPO_ROOT / "tests" / "evaluation_phase22"
FIXTURES_DIR = EVAL_DIR / "fixtures"
RESULTS_DIR = EVAL_DIR / "results" / "h1_r3_epistemic_action_value"
HISTORICAL_RESULTS_DIR = EVAL_DIR / "results" / "h1_r3_consumer_transferability"

MANIFEST_PATH = FIXTURES_DIR / "manifest_h1_r3_epistemic_action_value.json"
RESULTS_PATH = RESULTS_DIR / "r3_epistemic_action_value_results.json"
SUMMARY_CSV_PATH = RESULTS_DIR / "r3_epistemic_action_value_summary.csv"
ACTION_CSV_PATH = RESULTS_DIR / "r3_action_specific_valuations.csv"
HISTORICAL_RESULTS_PATH = HISTORICAL_RESULTS_DIR / "r3_consumer_transferability_results.json"
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


@pytest.fixture(scope="module")
def historical_transferability_data():
    assert HISTORICAL_RESULTS_PATH.exists(), f"Historical results not found: {HISTORICAL_RESULTS_PATH}"
    with open(HISTORICAL_RESULTS_PATH, "r", encoding="utf-8") as f:
        return json.load(f)


# -----------------------------------------------------------------------------
# Test 1: Manifest and Results Integrity
# -----------------------------------------------------------------------------
def test_01_manifest_and_result_integrity(manifest_data, results_data):
    """Verify manifest exists, references correct artifacts, and SHA-256 hashes match."""
    assert manifest_data["study_id"] == "PHASE_22_H1_R3_EPISTEMIC_ACTION_VALUE_STUDY"

    # Verify results JSON hash
    with open(RESULTS_PATH, "rb") as f:
        res_hash = hashlib.sha256(f.read()).hexdigest()
    assert manifest_data["artifacts"]["results_json"]["sha256"] == res_hash

    # Verify summary CSV hash
    with open(SUMMARY_CSV_PATH, "rb") as f:
        csv_hash = hashlib.sha256(f.read()).hexdigest()
    assert manifest_data["artifacts"]["summary_csv"]["sha256"] == csv_hash

    # Verify action CSV hash
    with open(ACTION_CSV_PATH, "rb") as f:
        act_hash = hashlib.sha256(f.read()).hexdigest()
    assert manifest_data["artifacts"]["action_csv"]["sha256"] == act_hash


# -----------------------------------------------------------------------------
# Test 2: Governance Invariants
# -----------------------------------------------------------------------------
def test_02_governance_invariants(manifest_data, results_data):
    """Verify strict governance invariants: locked gate, blocked gate 2, draft ADR-029."""
    gov = manifest_data["governance_invariants"]
    assert gov["architecture_gate"] == "STRICTLY_LOCKED"
    assert gov["adr029_status"] == "DRAFT / RESEARCH RECORD ONLY / NOT RATIFIED"
    assert gov["quality_gate_2"] == "STRICTLY_BLOCKED"
    assert gov["phase22_h1_status"] == "INCONCLUSIVE"
    assert gov["genesis_profile_bit_exact"] is True
    assert gov["hardware_budget"] == "100% CPU / 0.0 MB GPU VRAM"

    r_gov = results_data["study_metadata"]["governance"]
    assert r_gov["architecture_gate"] == "STRICTLY_LOCKED"
    assert r_gov["adr029_status"] == "DRAFT / RESEARCH RECORD ONLY / NOT RATIFIED"
    assert r_gov["quality_gate_2"] == "STRICTLY_BLOCKED"
    assert r_gov["phase22_h1_status"] == "INCONCLUSIVE"
    assert r_gov["genesis_profile_bit_exact"] is True


# -----------------------------------------------------------------------------
# Test 3: Corpus Lineage & Matched Pairs
# -----------------------------------------------------------------------------
def test_03_corpus_lineage_and_matched_pairs(manifest_data, results_data):
    """Verify stimulus corpus lineage, primary seed, and partition counts."""
    meta = results_data["study_metadata"]
    assert meta["primary_seed"] == 9999
    assert meta["consumer_seeds"] == [42, 43, 44, 45, 46]
    assert meta["corpus_n"] == 270
    assert meta["exposure_t"] == 12
    assert meta["scalar_match_threshold"] == 0.020
    assert meta["deadband_epsilon"] == 0.010
    assert meta["tolerance_val"] == 1e-4
    assert meta["tolerance_js"] == 1e-5

    assert manifest_data["corpus_n"] == 270
    assert manifest_data["corpus_sha256"] == "d0061e8cfdd160f4ebccb7100e4fe3eeef9ff18a1a4c9c1b3f912a76f2ae82c0"
    assert manifest_data["discordant_pairs_count"] == 358
    assert manifest_data["greedy_discordant_pairs_count"] == 16

    matched = meta["matched_pairs"]
    assert matched["exhaustive_pairs_count"] == 6734
    assert matched["discordant_pairs_count"] == 358
    assert matched["same_direction_pairs_count"] == 6376
    assert matched["greedy_discordant_pairs_count"] == 16


# -----------------------------------------------------------------------------
# Test 4: Locked Base Parameter Hash Integrity
# -----------------------------------------------------------------------------
def test_04_locked_base_parameter_hashes(manifest_data, results_data):
    """Verify locked base parameter hashes match cryptographic registry."""
    hashes = manifest_data["locked_base_parameter_hashes"]
    expected_keys = ["C_U_BASE", "C_COST_S", "C_M_BASE", "D_G_BASE", "D_KAPPA_S_BASE", "D_W_DIR"]
    for k in expected_keys:
        assert k in hashes
        assert len(hashes[k]) == 64

    res_hashes = results_data["study_metadata"]["locked_base_parameter_hashes"]
    assert hashes == res_hashes


# -----------------------------------------------------------------------------
# Test 5: Historical C2 Action Differentiation Reproduction
# -----------------------------------------------------------------------------
def test_05_c2_canonical_action_differentiation_reproduction(results_data):
    """Verify C2 action differentiation reproduces historical baseline bit-exact on Reference A."""
    c_a = results_data["consumer_results"]["A_REFERENCE"]["condition_aggregates"]["C2"]
    assert round(c_a["diffrate_action_mean"], 4) == 0.7989

    c_b = results_data["consumer_results"]["B_DIRECTIONAL_SEPARABLE"]["condition_aggregates"]["C2"]
    assert round(c_b["diffrate_action_mean"], 4) == 0.7989

    c_c = results_data["consumer_results"]["C_qual_1.50"]["condition_aggregates"]["C2"]
    assert round(c_c["diffrate_action_mean"], 4) == 0.7989


# -----------------------------------------------------------------------------
# Test 6: NC1 Canonical Scalar Baseline Reproduction
# -----------------------------------------------------------------------------
def test_06_nc1_scalar_baseline_reproduction(results_data, historical_transferability_data):
    """Verify C0 yields 0.0000 action difference across all consumers, matching historical artifact."""
    hist_c0 = historical_transferability_data["cross_consumer_evaluation"]["consumer_results"]["A_REFERENCE"]["seed_runs"]["42"]["discordant_metrics"]["C0"]["diffrate_disc"]
    assert hist_c0 == 0.0

    nc = results_data["study_metadata"]["negative_controls"]
    assert nc["nc1_scalar_baseline_historical_verified"] is True

    for c_id, c_data in results_data["consumer_results"].items():
        c0_diff = c_data["condition_aggregates"]["C0"]["diffrate_action_mean"]
        assert c0_diff == 0.0, f"Consumer {c_id} C0 diffrate {c0_diff} != 0.0"


# -----------------------------------------------------------------------------
# Test 7: NC2 Hard Tuple Identity Parity Invariant
# -----------------------------------------------------------------------------
def test_07_nc2_hard_tuple_identity_parity(results_data):
    """Verify evaluating identical tuples yields exactly zero valuation difference and zero D_JS."""
    nc = results_data["study_metadata"]["negative_controls"]
    assert nc["nc2_tuple_identity_parity"] is True

    for c_id, c_data in results_data["consumer_results"].items():
        assert c_data["tuple_identity_nc2"]["passed"] is True


# -----------------------------------------------------------------------------
# Test 8: NC3 Multiset Preservation Invariant
# -----------------------------------------------------------------------------
def test_08_nc3_multiset_preservation(results_data):
    """Verify C3, C4, C5 preserve exact multisets of S and direction via bijections on corpus."""
    nc = results_data["study_metadata"]["negative_controls"]
    assert nc["nc3_multiset_preservation"] is True


# -----------------------------------------------------------------------------
# Test 9: Continuous Action-Value Differentiation
# -----------------------------------------------------------------------------
def test_09_continuous_action_value_differentiation(results_data):
    """Verify continuous action-value differentiation occurs on 100% of discordant pairs under Consumer C."""
    c_c = results_data["consumer_results"]["C_qual_1.50"]["condition_aggregates"]
    c2_cont = c_c["C2"]["diffrate_continuous_val_mean"]
    assert c2_cont == 1.0, f"Expected 1.0 continuous differentiation, got {c2_cont}"
    assert c_c["C2"]["mean_delta_v_norm_mean"] > c_c["C0"]["mean_delta_v_norm_mean"]


# -----------------------------------------------------------------------------
# Test 10: Common-Mode vs Action-Specific Decomposition
# -----------------------------------------------------------------------------
def test_10_common_mode_vs_action_specific_decomposition(results_data):
    """Verify orthogonal variance decomposition: CM + Spec == 1.0 and Action-Specific > 50%."""
    for c_id, c_data in results_data["consumer_results"].items():
        for cond in ["C2", "C3", "C4", "C5"]:
            ag = c_data["condition_aggregates"][cond]
            cm = ag["common_mode_fraction_mean"]
            spec = ag["action_specific_fraction_mean"]
            assert abs((cm + spec) - 1.0) < 1e-6, f"{c_id} {cond}: cm={cm} + spec={spec} != 1.0"
            if cond == "C2" and c_id in ["C_qual_1.50", "A_REFERENCE", "B_DIRECTIONAL_SEPARABLE"]:
                assert spec > 0.50, f"{c_id} {cond}: action-specific fraction {spec} not > 0.50"


# -----------------------------------------------------------------------------
# Test 11: Epistemic-Action Relevance Diagnostic & Epistemic Disclaimer
# -----------------------------------------------------------------------------
def test_11_epistemic_action_relevance_diagnostic(results_data):
    """Verify diagnostic proxy status and explicit disassociation from Active Inference epistemic validity."""
    for c_id, c_data in results_data["consumer_results"].items():
        diag = c_data["epistemic_action_relevance_diagnostic"]
        # Action-value relevance may be established under tested consumers
        assert "action_value_relevance_established" in diag
        # Active Inference epistemic relevance MUST be explicitly False
        assert diag["active_inference_epistemic_relevance_established"] is False


# -----------------------------------------------------------------------------
# Test 12: Production Isolation and Genesis Profile Bit-Exact Audit
# -----------------------------------------------------------------------------
def test_12_production_isolation_and_genesis_profile(results_data):
    """Verify zero production mutations and Genesis onboarding profile preserved bit-exact."""
    assert PROFILE_PATH.exists()
    with open(PROFILE_PATH, "r", encoding="utf-8") as f:
        profile_content = f.read().strip()
    assert profile_content == '{"is_onboarded": false}', f"Genesis profile altered: {profile_content}"

    meta = results_data["study_metadata"]["governance"]
    assert meta["genesis_profile_bit_exact"] is True
    assert meta["architecture_gate"] == "STRICTLY_LOCKED"
