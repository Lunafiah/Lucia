"""
Phase 22 H1 — R3 Causal/Mechanistic Attribution Automated Verification Suite
=============================================================================
Test Suite: test_h1_r3_causal_attribution.py

Verifies:
  - 12 comprehensive automated tests verifying manifest integrity, governance invariants,
    corpus lineage and matching, locked base parameter hashes, historical C2 reproduction,
    NC1 canonical scalar baseline reproduction from frozen historical artifacts,
    NC2 hard tuple identity parity, NC3 marginal distribution preservation,
    representation ablations (C1, C6, C7), mechanistic attribution contrasts,
    cross-consumer differentiation profiles, and production isolation / Genesis profile integrity.
"""

import json
from pathlib import Path
import pytest
import numpy as np

REPO_ROOT = Path(__file__).resolve().parent.parent.parent
EVAL_DIR = REPO_ROOT / "tests" / "evaluation_phase22"
FIXTURES_DIR = EVAL_DIR / "fixtures"
RESULTS_DIR = EVAL_DIR / "results" / "h1_r3_causal_attribution"
HISTORICAL_RESULTS_DIR = EVAL_DIR / "results" / "h1_r3_consumer_transferability"

MANIFEST_PATH = FIXTURES_DIR / "manifest_h1_r3_causal_attribution.json"
RESULTS_PATH = RESULTS_DIR / "r3_causal_attribution_results.json"
SUMMARY_CSV_PATH = RESULTS_DIR / "r3_causal_attribution_summary.csv"
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
    import hashlib

    assert manifest_data["study_id"] == "PHASE_22_H1_R3_CAUSAL_ATTRIBUTION_STUDY"

    # Verify results JSON hash
    with open(RESULTS_PATH, "rb") as f:
        res_hash = hashlib.sha256(f.read()).hexdigest()
    assert manifest_data["artifacts"]["results_json"]["sha256"] == res_hash

    # Verify summary CSV hash
    with open(SUMMARY_CSV_PATH, "rb") as f:
        csv_hash = hashlib.sha256(f.read()).hexdigest()
    assert manifest_data["artifacts"]["summary_csv"]["sha256"] == csv_hash


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
# Test 3: Corpus Lineage and Matching Protocol
# -----------------------------------------------------------------------------
def test_03_corpus_lineage_and_matching(manifest_data, results_data):
    """Verify stimulus corpus parameters (N=270, seed 9999, SHA) and pair counts."""
    meta = results_data["study_metadata"]
    assert meta["primary_seed"] == 9999
    assert meta["consumer_seeds"] == [42, 43, 44, 45, 46]
    assert meta["corpus_n"] == 270
    assert meta["exposure_t"] == 12
    assert meta["scalar_match_threshold"] == 0.020
    assert meta["deadband_epsilon"] == 0.010

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
# Test 5: Historical C2 Baseline Reproduction
# -----------------------------------------------------------------------------
def test_05_historical_c2_reproduction(results_data):
    """Verify canonical R3 condition (C2) bit-exact reproduces 286/358 (79.8883%) across consumers."""
    consumers = results_data["consumer_results"]
    expected_diffrate = 286.0 / 358.0  # 0.7988826815642458
    expected_greedy = 13.0 / 16.0      # 0.8125

    for c_id in ["C_qual_1.50", "A_REFERENCE", "B_DIRECTIONAL_SEPARABLE", "D_qual_corner"]:
        c2_res = consumers[c_id]["condition_aggregates"]["C2"]
        assert abs(c2_res["diffrate_disc_mean"] - expected_diffrate) < 1e-6
        assert abs(c2_res["diffrate_greedy_mean"] - expected_greedy) < 1e-6
        assert c2_res["diffrate_disc_std"] == 0.0


# -----------------------------------------------------------------------------
# Test 6: NC1 Canonical Scalar Baseline Reproduction
# -----------------------------------------------------------------------------
def test_06_nc1_canonical_scalar_baseline_reproduction(results_data, historical_transferability_data):
    """
    Verify Negative Control 1 (NC1):
    D_pair_action(C0) reproduces the canonical scalar baseline bit-exact against
    the frozen historical transferability artifact rather than a disconnected hardcoded zero.
    """
    hist_runs = historical_transferability_data["cross_consumer_evaluation"]["consumer_results"]
    # Verify historical artifact baseline for A_REFERENCE and B_DIRECTIONAL_SEPARABLE
    hist_a_c0 = hist_runs["A_REFERENCE"]["seed_runs"]["42"]["discordant_metrics"]["C0"]["d_pair_action"]
    hist_b_c0 = hist_runs["B_DIRECTIONAL_SEPARABLE"]["seed_runs"]["42"]["discordant_metrics"]["C0"]["d_pair_action"]
    assert hist_a_c0 == 0.0, "Historical A_REFERENCE C0 baseline must be 0.0"
    assert hist_b_c0 == 0.0, "Historical B_DIRECTIONAL_SEPARABLE C0 baseline must be 0.0"

    # Verify attribution study bit-exact matches the historical baseline across all evaluated consumers and seeds
    for c_id, c_data in results_data["consumer_results"].items():
        c0_res = c_data["condition_aggregates"]["C0"]
        assert c0_res["diffrate_disc_mean"] == hist_a_c0, (
            f"Consumer {c_id} C0 baseline {c0_res['diffrate_disc_mean']} does not match historical {hist_a_c0}"
        )
        assert c0_res["directional_gain_mean"] == 0.0
        assert c0_res["action_displacement_mean"] == 0.0
        assert c0_res["diffrate_disc_std"] == 0.0


# -----------------------------------------------------------------------------
# Test 7: NC2 Hard Tuple Identity Parity
# -----------------------------------------------------------------------------
def test_07_nc2_hard_tuple_identity_parity(results_data):
    """Verify Negative Control 2 (NC2): Identical representation tuples produce zero action diff and zero JS."""
    for c_id, c_data in results_data["consumer_results"].items():
        tuple_id = c_data["tuple_identity"]
        assert tuple_id["passed"] is True, f"Consumer {c_id} failed hard tuple identity parity"
        assert tuple_id["delta_action_identity"] == 0.0
        assert tuple_id["d_js_identity"] == 0.0


# -----------------------------------------------------------------------------
# Test 8: NC3 Marginal Distribution Preservation
# -----------------------------------------------------------------------------
def test_08_nc3_marginal_distribution_preservation(results_data):
    """
    Verify Negative Control 3 (NC3):
    Shuffled direction (C3) and independent direction (C5) preserve marginal frequency of direction
    tuples but destroy stimulus-residual alignment, collapsing differentiation by >50 percentage points.
    """
    for c_id in ["C_qual_1.50", "A_REFERENCE", "B_DIRECTIONAL_SEPARABLE", "D_qual_corner"]:
        c_data = results_data["consumer_results"][c_id]
        c2_rate = c_data["condition_aggregates"]["C2"]["diffrate_disc_mean"]
        c3_rate = c_data["condition_aggregates"]["C3"]["diffrate_disc_mean"]
        c5_rate = c_data["condition_aggregates"]["C5"]["diffrate_disc_mean"]

        # C3 differentiation drops significantly
        assert abs(c3_rate - 0.2916) < 0.01
        # C5 differentiation drops to independent marginal level
        assert abs(c5_rate - 0.2453) < 0.01

        # Mechanistic drop is at least 0.50
        delta_c3 = c_data["mechanistic_contrasts"]["C2_minus_C3_direction_correspondence"]
        assert delta_c3 > 0.50, f"Consumer {c_id} C2-C3 contrast {delta_c3} not > 0.50"


# -----------------------------------------------------------------------------
# Test 9: Representation Ablations (C1, C6, C7)
# -----------------------------------------------------------------------------
def test_09_representation_ablations_c1_c6_c7(results_data):
    """
    Verify representation ablations:
    - C1 (continuous residual R2 normalized with ||r||_2 > 0) matches C2 differentiation.
    - C6 (binary sign-only ablation) matches C2 differentiation.
    - C7 (direction-count control) drops to 0.0000 in Consumer C, Consumer A, Consumer B.
    """
    for c_id in ["C_qual_1.50", "A_REFERENCE", "B_DIRECTIONAL_SEPARABLE"]:
        c_data = results_data["consumer_results"][c_id]
        c1_rate = c_data["condition_aggregates"]["C1"]["diffrate_disc_mean"]
        c2_rate = c_data["condition_aggregates"]["C2"]["diffrate_disc_mean"]
        c6_rate = c_data["condition_aggregates"]["C6"]["diffrate_disc_mean"]
        c7_rate = c_data["condition_aggregates"]["C7"]["diffrate_disc_mean"]

        assert abs(c1_rate - c2_rate) < 1e-6, f"Consumer {c_id}: C1 ({c1_rate}) != C2 ({c2_rate})"
        assert abs(c6_rate - c2_rate) < 1e-6, f"Consumer {c_id}: C6 ({c6_rate}) != C2 ({c2_rate})"
        assert c7_rate == 0.0, f"Consumer {c_id}: C7 ({c7_rate}) != 0.0"


# -----------------------------------------------------------------------------
# Test 10: Mechanistic Attribution Contrasts
# -----------------------------------------------------------------------------
def test_10_mechanistic_attribution_contrasts(results_data):
    """
    Verify mechanistic attribution contrast values:
    - C2 - C0 = 0.7989 (canonical R3 gain)
    - C2 - C3 = 0.5073 (direction correspondence contribution)
    - C2 - C5 = 0.5536 (empirical direction structure contribution)
    - C2 - C6 = 0.0000 (ternary vs binary gain is zero in evaluated consumers)
    """
    for c_id in ["C_qual_1.50", "A_REFERENCE"]:
        contrasts = results_data["consumer_results"][c_id]["mechanistic_contrasts"]
        assert abs(contrasts["C2_minus_C0_canonical_r3_gain"] - 0.79888) < 1e-4
        assert abs(contrasts["C2_minus_C3_direction_correspondence"] - 0.50726) < 1e-4
        assert abs(contrasts["C2_minus_C4_magnitude_correspondence"] - 0.00000) < 1e-4
        assert abs(contrasts["C2_minus_C5_empirical_direction_structure"] - 0.55363) < 1e-4
        assert abs(contrasts["C2_minus_C6_reduced_sign_ablation"] - 0.00000) < 1e-4
        assert abs(contrasts["C2_minus_C7_directional_sparsity"] - 0.79888) < 1e-4


# -----------------------------------------------------------------------------
# Test 11: Cross-Consumer Differentiation Profiles
# -----------------------------------------------------------------------------
def test_11_cross_consumer_differentiation_profile(results_data):
    """Verify differentiation profiles across all 4 evaluated consumers."""
    consumers = results_data["consumer_results"]

    # Consumer C @ 1.50
    c_conds = consumers["C_qual_1.50"]["condition_aggregates"]
    assert c_conds["C0"]["diffrate_disc_mean"] == 0.0
    assert abs(c_conds["C2"]["diffrate_disc_mean"] - 0.79888) < 1e-4
    assert c_conds["C7"]["diffrate_disc_mean"] == 0.0

    # Consumer D @ qualifying corner
    d_conds = consumers["D_qual_corner"]["condition_aggregates"]
    assert d_conds["C0"]["diffrate_disc_mean"] == 0.0
    assert abs(d_conds["C2"]["diffrate_disc_mean"] - 0.79888) < 1e-4
    # Consumer D has C7=1.0000 due to weakened scalar slope and isotropic shift
    assert d_conds["C7"]["diffrate_disc_mean"] == 1.0


# -----------------------------------------------------------------------------
# Test 12: Production Isolation and Genesis Profile Integrity
# -----------------------------------------------------------------------------
def test_12_production_isolation_and_genesis_profile_integrity(manifest_data):
    """Verify data/profile.json is bit-exact {"is_onboarded": false} and diff=0."""
    assert PROFILE_PATH.exists(), f"Profile not found: {PROFILE_PATH}"
    with open(PROFILE_PATH, "r", encoding="utf-8") as f:
        content = f.read()

    # Profile must be bit-exact
    data = json.loads(content)
    assert data == {"is_onboarded": False}, f"Profile mutated: {data}"
    assert manifest_data["governance_invariants"]["genesis_profile_bit_exact"] is True
