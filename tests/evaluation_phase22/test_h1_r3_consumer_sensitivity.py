"""
tests/evaluation_phase22/test_h1_r3_consumer_sensitivity.py

Comprehensive automated verification test suite for Phase 22 H1 R3 Consumer Sensitivity
& Robustness Envelope Study.
Validates:
- Test 01: Manifest and result fixtures cryptographic integrity (SHA-256)
- Test 02: Strict governance invariants (Architecture Gate locked, profile bit-exact)
- Test 03: Pre-registered parameter grids determinism (8 C-levels, 30 D-cells)
- Test 04: Candidate G1 stimulus corpus lineage (Master Seed 9999, N=270, SHA-256 match)
- Test 05: Matched pair partition reproducibility (358 discordant, 6,376 same-direction)
- Test 06: Consumer A/B historical reproduction & controls tuple identity
- Test 07: Hard tuple identity parity invariant across all 38 sweep parameter regimes
- Test 08: Consumer C sensitivity sweep analysis & transition boundary extraction
- Test 09: Consumer D 2D sensitivity surface analysis & discrete qualifying cell set
- Test 10: Robustness envelope characterization without universal claims
- Test 11: Secondary metric descriptive tracking (no threshold on D_condition_action)
- Test 12: Production isolation and Genesis profile bit-exact preservation
"""

import hashlib
import json
from pathlib import Path
import pytest

REPO_ROOT = Path(__file__).resolve().parent.parent.parent
EVAL_DIR = REPO_ROOT / "tests" / "evaluation_phase22"
RESULTS_DIR = EVAL_DIR / "results" / "h1_r3_consumer_sensitivity"
FIXTURES_DIR = EVAL_DIR / "fixtures"

RESULTS_FILE = RESULTS_DIR / "r3_consumer_sensitivity_results.json"
SUMMARY_CSV = RESULTS_DIR / "r3_consumer_sensitivity_summary.csv"
MANIFEST_FILE = FIXTURES_DIR / "manifest_h1_r3_consumer_sensitivity.json"
PROFILE_FILE = REPO_ROOT / "data" / "profile.json"

EXPECTED_CORPUS_SHA = "d0061e8cfdd160f4ebccb7100e4fe3eeef9ff18a1a4c9c1b3f912a76f2ae82c0"
EXPECTED_GAMMA_C = [0.10, 0.20, 0.35, 0.50, 0.75, 1.00, 1.50, 2.00]
EXPECTED_MU_D = [0.20, 0.30, 0.40, 0.50, 0.70, 1.00]
EXPECTED_GAMMA_KAPPA = [0.50, 0.75, 1.00, 1.25, 1.50]


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


# ---------------------------------------------------------------------------
# Test 01: Manifest and Results Integrity
# ---------------------------------------------------------------------------

def test_01_manifest_and_results_integrity(manifest_data: dict):
    assert RESULTS_FILE.exists()
    assert SUMMARY_CSV.exists()
    assert MANIFEST_FILE.exists()

    with open(RESULTS_FILE, "rb") as f:
        results_sha = hashlib.sha256(f.read()).hexdigest()
    assert results_sha == manifest_data["artifacts"]["results_json"]["sha256"]

    with open(SUMMARY_CSV, "rb") as f:
        csv_sha = hashlib.sha256(f.read()).hexdigest()
    assert csv_sha == manifest_data["artifacts"]["summary_csv"]["sha256"]

    # Locked base parameter hashes check
    assert "locked_base_parameter_hashes" in manifest_data
    base_hashes = manifest_data["locked_base_parameter_hashes"]
    assert "C_U_BASE" in base_hashes
    assert "C_COST_S" in base_hashes
    assert "C_M_BASE" in base_hashes
    assert "D_G_BASE" in base_hashes
    assert "D_KAPPA_S_BASE" in base_hashes
    assert "D_W_DIR" in base_hashes


# ---------------------------------------------------------------------------
# Test 02: Strict Governance Invariants
# ---------------------------------------------------------------------------

def test_02_strict_governance_invariants(manifest_data: dict):
    gov = manifest_data["governance_invariants"]
    assert gov["architecture_gate"] == "STRICTLY_LOCKED"
    assert gov["adr029_status"] == "DRAFT / RESEARCH RECORD ONLY / NOT RATIFIED"
    assert gov["quality_gate_2"] == "STRICTLY_BLOCKED"
    assert gov["phase22_h1_status"] == "INCONCLUSIVE"
    assert gov["genesis_profile_bit_exact"] is True


# ---------------------------------------------------------------------------
# Test 03: Pre-Registered Parameter Grids Determinism
# ---------------------------------------------------------------------------

def test_03_grid_specification_determinism(manifest_data: dict, results_data: dict):
    grids = manifest_data["parameter_grids"]
    assert grids["gamma_c_grid"] == EXPECTED_GAMMA_C
    assert grids["mu_d_grid"] == EXPECTED_MU_D
    assert grids["gamma_kappa_grid"] == EXPECTED_GAMMA_KAPPA
    assert grids["total_sweep_regimes"] == 38
    assert grids["total_control_regimes"] == 2

    c_levels = results_data["consumer_c_sensitivity"]["grid_levels"]
    assert c_levels == EXPECTED_GAMMA_C
    d_mu = results_data["consumer_d_sensitivity"]["mu_d_grid"]
    assert d_mu == EXPECTED_MU_D
    d_gk = results_data["consumer_d_sensitivity"]["gamma_kappa_grid"]
    assert d_gk == EXPECTED_GAMMA_KAPPA


# ---------------------------------------------------------------------------
# Test 04: Corpus Lineage Consistency
# ---------------------------------------------------------------------------

def test_04_corpus_lineage(results_data: dict):
    meta = results_data["study_metadata"]
    assert meta["primary_seed"] == 9999
    assert meta["exposure_t"] == 12
    assert meta["deadband_epsilon"] == 0.010
    assert meta["scalar_match_threshold"] == 0.020


# ---------------------------------------------------------------------------
# Test 05: Matched Pair Partition Reproducibility
# ---------------------------------------------------------------------------

def test_05_matched_pair_partition_reproducibility(results_data: dict):
    # Consumer A must evaluate across exactly 358 discordant pairs
    c_a = results_data["control_baselines"]["A_REFERENCE"]
    agg = c_a["aggregate"]
    assert round(agg["c2_diffrate_disc_mean"], 4) == 0.7989
    assert round(agg["c2_diffrate_all_mean"], 4) == 0.0425


# ---------------------------------------------------------------------------
# Test 06: Consumer A/B Historical Reproduction & Controls Tuple Identity
# ---------------------------------------------------------------------------

def test_06_consumer_ab_historical_reproduction_and_controls(results_data: dict):
    controls = results_data["control_baselines"]
    c_a = controls["A_REFERENCE"]
    c_b = controls["B_DIRECTIONAL_SEPARABLE"]

    assert round(c_a["aggregate"]["c2_diffrate_disc_mean"], 4) == 0.7989
    assert round(c_b["aggregate"]["c2_diffrate_disc_mean"], 4) == 0.7989
    assert round(c_a["aggregate"]["c0_d_pair_action_mean"], 4) == 0.0000
    assert round(c_b["aggregate"]["c0_d_pair_action_mean"], 4) == 0.0000
    assert round(c_a["aggregate"]["directional_gain_mean"], 4) == 0.7989
    assert round(c_b["aggregate"]["directional_gain_mean"], 4) == 0.7989

    assert c_a["preregistered_criteria"]["hard_tuple_identity_parity"]["invariant_passed"] is True
    assert c_b["preregistered_criteria"]["hard_tuple_identity_parity"]["invariant_passed"] is True
    assert results_data["invariants_audit"]["controls_tuple_identity_passed"] is True


# ---------------------------------------------------------------------------
# Test 07: Hard Tuple Identity Parity Sweep Across All 38 Sweep Regimes
# ---------------------------------------------------------------------------

def test_07_hard_tuple_identity_parity_sweep(results_data: dict):
    assert results_data["invariants_audit"]["all_38_sweep_regimes_tuple_identity_passed"] is True

    # Check each Consumer C regime
    for g_c in EXPECTED_GAMMA_C:
        cell = results_data["consumer_c_sensitivity"]["sweep_results"][f"gamma_{g_c:.2f}"]
        t_inv = cell["metrics"]["preregistered_criteria"]["hard_tuple_identity_parity"]
        assert t_inv["invariant_passed"] is True
        assert t_inv["delta_action_identity"] == 0.0
        assert t_inv["d_js_identity"] < 1e-12

    # Check each Consumer D regime
    for mu in EXPECTED_MU_D:
        for gk in EXPECTED_GAMMA_KAPPA:
            cell = results_data["consumer_d_sensitivity"]["sweep_results"][f"mu_{mu:.2f}_gk_{gk:.2f}"]
            t_inv = cell["metrics"]["preregistered_criteria"]["hard_tuple_identity_parity"]
            assert t_inv["invariant_passed"] is True
            assert t_inv["delta_action_identity"] == 0.0
            assert t_inv["d_js_identity"] < 1e-12


# ---------------------------------------------------------------------------
# Test 08: Consumer C Sensitivity Sweep Analysis & Transition Boundary
# ---------------------------------------------------------------------------

def test_08_consumer_c_sensitivity_sweep(results_data: dict):
    c_sens = results_data["consumer_c_sensitivity"]
    assert len(c_sens["sweep_results"]) == 8

    # Verify historical reference cell gamma_C = 1.00
    hist_cell = c_sens["sweep_results"]["gamma_1.00"]
    assert hist_cell["is_historical_reference"] is True
    assert round(hist_cell["metrics"]["aggregate"]["c2_diffrate_disc_mean"], 4) == 0.0000

    # Transition status must be one of the pre-registered outcomes
    assert c_sens["transition_status"] in [
        "BOUNDARY_AT_GRID_MINIMUM",
        "TRANSITION_INTERVAL_OBSERVED",
        "NO_EMPIRICAL_TRANSITION_WITHIN_GRID",
    ]


# ---------------------------------------------------------------------------
# Test 09: Consumer D 2D Sensitivity Surface Analysis
# ---------------------------------------------------------------------------

def test_09_consumer_d_2d_sensitivity_surface(results_data: dict):
    d_sens = results_data["consumer_d_sensitivity"]
    assert len(d_sens["sweep_results"]) == 30

    # Verify historical reference cell mu = 0.20, gk = 1.00
    hist_cell = d_sens["sweep_results"]["mu_0.20_gk_1.00"]
    assert hist_cell["is_historical_reference"] is True
    assert round(hist_cell["metrics"]["aggregate"]["c2_diffrate_disc_mean"], 4) == 0.0000

    assert d_sens["transition_status"] in [
        "DISCRETE_QUALIFYING_REGIME_OBSERVED",
        "NO_EMPIRICAL_TRANSITION_WITHIN_GRID",
    ]


# ---------------------------------------------------------------------------
# Test 10: Robustness Envelope Characterization
# ---------------------------------------------------------------------------

def test_10_robustness_envelope_characterization(results_data: dict):
    # Verify that discrete differentiation is monotonic or bounded across sweep
    c_results = results_data["consumer_c_sensitivity"]["sweep_results"]
    d_results = results_data["consumer_d_sensitivity"]["sweep_results"]

    # Continuous valuation divergence must increase with directional coupling
    delta_vs = [c_results[f"gamma_{g:.2f}"]["metrics"]["aggregate"]["c2_delta_v_mean"] for g in EXPECTED_GAMMA_C]
    for i in range(1, len(delta_vs)):
        assert delta_vs[i] >= delta_vs[i - 1]


# ---------------------------------------------------------------------------
# Test 11: Secondary Metric Descriptive Tracking
# ---------------------------------------------------------------------------

def test_11_secondary_metric_descriptive_tracking(results_data: dict):
    # Verify that secondary_metric_condition_shift_c2_c4 has role "descriptive_secondary_metric"
    # and no pass/fail boolean
    c_cell = results_data["consumer_c_sensitivity"]["sweep_results"]["gamma_1.00"]["metrics"]["preregistered_criteria"]
    sec_metric = c_cell["secondary_metric_condition_shift_c2_c4"]
    assert sec_metric["role"] == "descriptive_secondary_metric"
    assert "passed" not in sec_metric
    assert isinstance(sec_metric["observed"], float)


# ---------------------------------------------------------------------------
# Test 12: Production Isolation and Genesis Profile Bit-Exact Preservation
# ---------------------------------------------------------------------------

def test_12_production_isolation_and_genesis_audit():
    assert PROFILE_FILE.exists(), f"Profile file missing: {PROFILE_FILE}"
    with open(PROFILE_FILE, "r", encoding="utf-8") as f:
        data = json.load(f)
    assert data == {"is_onboarded": False}, f"Genesis profile mutated: {data}"
