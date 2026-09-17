"""
Phase 22 H1 — R3 Temporal Belief Dynamics & Multi-Turn Persistence Study
=========================================================================
Automated Test Suite: test_h1_r3_temporal_belief_dynamics.py

Validates:
  1. Manifest and results integrity (SHA-256 hashes, file existence).
  2. Strict governance invariants (Gate 2 BLOCKED, Phase 22 H1 INCONCLUSIVE, ADR-029 DRAFT).
  3. Master corpus lineage (N=270, seed 9999, 358 discordant pairs).
  4. Anti-circularity parameter hashes lock.
  5. Sequence definitions (T1..T4) and turn horizon T=5.
  6. Two-mode decomposition (Mode A coupled vs Mode B controlled).
  7. Persistence Ratio PR_t mathematical correctness and zero-delta handling.
  8. H1-T Temporal Persistence (State T-B: retention rate = 100%, PR_2 >= 0.20).
  9. H2-T Recovery sensitivity strict monotonic decay across turns 1..5 under T1.
  10. H2-T Half-life horizon bound (NOT_REACHED within T=5 turns).
  11. T2 Repeated fixed displacement injection saturation dynamics.
  12. T3 Direction reversal dynamics and sign tracking.
  13. T4 Temporal History-Dependence Diagnostic (THD).
  14. Consumer transferability across Reference A, Separable B, Corner D.
  15. Seed robustness across consumer seeds [42, 43, 44, 45, 46].
  16. NC5 Representation-independent zero-direction null (W_dir = 0 -> ΔEIG_dir = 0).
  17. NC6 Temporal transition null (max mean <= 1e-4, retention = 0%).
  18. NC7 Production isolation (src/core/** diff = 0).
  19. NC8 Genesis profile bit-exact {"is_onboarded": false}.
"""

import hashlib
import json
import math
from pathlib import Path
import subprocess
import pytest

REPO_ROOT = Path(__file__).resolve().parent.parent.parent
RESULTS_DIR = REPO_ROOT / "tests" / "evaluation_phase22" / "results" / "h1_r3_temporal_belief_dynamics"
FIXTURES_DIR = REPO_ROOT / "tests" / "evaluation_phase22" / "fixtures"

RESULTS_FILE = RESULTS_DIR / "r3_temporal_belief_dynamics_results.json"
SUMMARY_CSV = RESULTS_DIR / "r3_temporal_persistence_summary.csv"
TRAJECTORIES_CSV = RESULTS_DIR / "r3_temporal_sequence_trajectories.csv"
MANIFEST_FILE = FIXTURES_DIR / "manifest_h1_r3_temporal_belief_dynamics.json"
PROFILE_FILE = REPO_ROOT / "data" / "profile.json"

EXPECTED_CORPUS_SHA = "d0061e8cfdd160f4ebccb7100e4fe3eeef9ff18a1a4c9c1b3f912a76f2ae82c0"
EXPECTED_DISCORDANT_PAIRS = 358
TOLERANCE_EIG = 1e-4
TOLERANCE_JS = 1e-5


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


# =============================================================================
# 1. Manifest and Artifact Integrity
# =============================================================================

def test_01_manifest_and_results_integrity(manifest_data: dict):
    assert RESULTS_FILE.exists()
    assert SUMMARY_CSV.exists()
    assert TRAJECTORIES_CSV.exists()
    assert MANIFEST_FILE.exists()

    with open(RESULTS_FILE, "rb") as f:
        res_sha = hashlib.sha256(f.read()).hexdigest()
    assert res_sha == manifest_data["artifact_hashes"]["results_json"]

    with open(SUMMARY_CSV, "rb") as f:
        csv_sha = hashlib.sha256(f.read()).hexdigest()
    assert csv_sha == manifest_data["artifact_hashes"]["summary_csv"]

    with open(TRAJECTORIES_CSV, "rb") as f:
        traj_sha = hashlib.sha256(f.read()).hexdigest()
    assert traj_sha == manifest_data["artifact_hashes"]["trajectories_csv"]


# =============================================================================
# 2. Strict Governance Invariants
# =============================================================================

def test_02_governance_invariants(results_data: dict):
    gov = results_data["governance"]
    assert gov["phase22_h1_status"] == "INCONCLUSIVE"
    assert gov["gate2_status"] == "STRICTLY_BLOCKED"
    assert gov["adr029_status"] == "DRAFT_RESEARCH_RECORD_ONLY"
    assert gov["genesis_onboarded"] is False


# =============================================================================
# 3. Master Corpus Lineage & Pair Count
# =============================================================================

def test_03_corpus_lineage_and_matched_pairs(manifest_data: dict, results_data: dict):
    assert results_data["master_seed"] == 9999
    assert results_data["corpus_sha256"] == EXPECTED_CORPUS_SHA
    assert manifest_data["corpus_sha256"] == EXPECTED_CORPUS_SHA
    assert results_data["n_probes"] == 270
    assert results_data["n_discordant_pairs"] == EXPECTED_DISCORDANT_PAIRS
    assert manifest_data["n_discordant_pairs"] == EXPECTED_DISCORDANT_PAIRS


# =============================================================================
# 4. Anti-Circularity Parameter Hashes Lock
# =============================================================================

def test_04_anti_circularity_parameter_hashes(results_data: dict, manifest_data: dict):
    hashes = results_data["locked_parameter_hashes"]
    assert "ALPHA_DECAY" in hashes
    assert "BETA_STIM" in hashes
    assert "LAMBDA_LEAK" in hashes
    assert "RESTING_PAD" in hashes
    assert "CLARIFY_BASE_LOGITS" in hashes
    assert "RETRIEVE_BASE_LOGITS" in hashes
    assert "CLARIFY_W_DIR" in hashes
    assert "RETRIEVE_W_DIR" in hashes
    assert "CLARIFY_B_S" in hashes
    assert "RETRIEVE_B_S" in hashes

    for k, v in hashes.items():
        assert manifest_data["parameter_hashes"][k] == v


# =============================================================================
# 5. Sequence Definitions and Horizon T=5
# =============================================================================

def test_05_sequence_definitions_and_turn_horizon(manifest_data: dict, results_data: dict):
    assert manifest_data["horizon_turns"] == 5
    expected_seqs = ["T1", "T2", "T3", "T4"]
    assert manifest_data["sequences"] == expected_seqs

    seq_results = results_data["sequence_results"]
    for seq in expected_seqs:
        assert f"{seq}_mode_a" in seq_results
        assert f"{seq}_mode_b" in seq_results
        stats = seq_results[f"{seq}_mode_a"]["per_turn_stats"]
        assert len(stats) == 5
        assert set(stats.keys()) == {"1", "2", "3", "4", "5"}


# =============================================================================
# 6. Two-Mode Decomposition
# =============================================================================

def test_06_two_mode_decomposition(results_data: dict):
    seq_res = results_data["sequence_results"]
    assert "T1_mode_a" in seq_res
    assert "T1_mode_b" in seq_res
    assert seq_res["T1_mode_a"]["mode"] == "mode_a"
    assert seq_res["T1_mode_b"]["mode"] == "mode_b"


# =============================================================================
# 7. Persistence Ratio Mathematics & Zero-Delta Handling
# =============================================================================

def test_07_persistence_ratio_mathematics_and_zero_delta_handling(results_data: dict):
    t1_stats = results_data["sequence_results"]["T1_mode_a"]["per_turn_stats"]
    # Turn 1 PR must be exactly 1.0
    assert abs(t1_stats["1"]["mean_persistence_ratio"] - 1.0) < 1e-6
    # No undefined zero-delta cases in the 358 discordant pairs
    assert t1_stats["1"]["undefined_zero_delta_count"] == 0
    # Turn 2 PR should be non-negative
    assert t1_stats["2"]["mean_persistence_ratio"] > 0.0


# =============================================================================
# 8. H1-T: Temporal Persistence (State T-B)
# =============================================================================

def test_08_h1_t_temporal_persistence(results_data: dict):
    h1 = results_data["hypothesis_evaluation"]["H1_T_persistence"]
    assert h1["status"] == "PERSISTENT_STATE_T_B"
    assert h1["t1_turn_2_retention"] == 1.0  # 100% pairs retain directional signal
    assert h1["t1_turn_2_mean_pr"] >= 0.20  # Mean persistence ratio ~ 0.86
    assert h1["t2_turn_2_retention"] == 1.0
    assert h1["supported"] is True


# =============================================================================
# 9. H2-T: Recovery Sensitivity Monotonic Decay
# =============================================================================

def test_09_h2_t_recovery_sensitivity_monotonic_decay(results_data: dict):
    h2 = results_data["hypothesis_evaluation"]["H2_T_recovery_sensitivity"]
    assert h2["is_strictly_monotonic"] is True
    means = h2["per_turn_means_t1"]
    assert len(means) == 5
    for i in range(len(means) - 1):
        assert means[i] > means[i + 1], f"Non-monotonic decay from turn {i+1} to {i+2}"


# =============================================================================
# 10. H2-T: Half-Life Horizon Bound
# =============================================================================

def test_10_h2_t_half_life_horizon_bound(results_data: dict):
    h2 = results_data["hypothesis_evaluation"]["H2_T_recovery_sensitivity"]
    # At turn 5, PR is still ~0.6665 > 0.50, so half-life is NOT_REACHED within T=5
    assert h2["median_half_life_t1"] == "NOT_REACHED"
    assert h2["supported"] is False


# =============================================================================
# 11. T2: Repeated Fixed Displacement Injection Saturation Dynamics
# =============================================================================

def test_11_t2_repeated_displacement_injection_saturation(results_data: dict):
    t2_stats = results_data["sequence_results"]["T2_mode_a"]["per_turn_stats"]
    m1 = t2_stats["1"]["mean_abs_delta_dir"]
    m2 = t2_stats["2"]["mean_abs_delta_dir"]
    m5 = t2_stats["5"]["mean_abs_delta_dir"]
    # Under repeated injection, delta accumulates and saturates
    assert m2 > m1
    assert m5 > m2
    assert t2_stats["5"]["mean_persistence_ratio"] > 1.50


# =============================================================================
# 12. T3: Direction Reversal Dynamics
# =============================================================================

def test_12_t3_direction_reversal_dynamics(results_data: dict):
    t3_stats = results_data["sequence_results"]["T3_mode_a"]["per_turn_stats"]
    assert t3_stats["1"]["retention_rate"] == 1.0
    assert t3_stats["2"]["retention_rate"] == 1.0
    assert t3_stats["3"]["retention_rate"] == 1.0
    assert t3_stats["4"]["retention_rate"] == 1.0
    assert t3_stats["5"]["retention_rate"] == 1.0
    # Turn 1, 3, 5 are positive injections: sign agreement is 1.0
    assert t3_stats["1"]["t3_sign_agreement"] == 1.0
    assert t3_stats["3"]["t3_sign_agreement"] == 1.0
    assert t3_stats["5"]["t3_sign_agreement"] == 1.0


# =============================================================================
# 13. T4: Temporal History-Dependence Diagnostic (THD)
# =============================================================================

def test_13_t4_temporal_history_dependence_diagnostic(results_data: dict):
    t4_diag = results_data["t4_history_dependence"]
    mode_a = t4_diag["mode_a"]
    mode_b = t4_diag["mode_b"]
    assert mode_a["reactivation_turn"] == 4
    # EIG difference at reactivation exceeds tau_EIG for all probes
    assert mode_a["thd_eig_exceeding_tau"] == 1.0
    assert mode_a["mean_delta_eig_diff"] > TOLERANCE_EIG
    assert mode_b["thd_eig_exceeding_tau"] == 1.0
    assert mode_b["mean_delta_eig_diff"] > TOLERANCE_EIG


# =============================================================================
# 14. Consumer Transferability Across A, B, D
# =============================================================================

def test_14_consumer_transferability_a_b_d(results_data: dict):
    trans = results_data["consumer_transferability"]
    for cid in ["A_REFERENCE", "B_DIRECTIONAL_SEPARABLE", "D_CORNER"]:
        assert cid in trans
        c_stats = trans[cid]["per_turn_stats"]
        # Directional retention remains 100% across all 5 turns for all consumers
        assert c_stats["1"]["retention_rate"] == 1.0
        assert c_stats["2"]["retention_rate"] == 1.0
        assert c_stats["5"]["retention_rate"] == 1.0


# =============================================================================
# 15. Seed Robustness
# =============================================================================

def test_15_seed_robustness(results_data: dict):
    seeds = results_data["seed_robustness"]
    for s in [42, 43, 44, 45, 46]:
        str_s = str(s)
        assert str_s in seeds
        assert seeds[str_s]["turn_1_retention"] == 1.0
        assert seeds[str_s]["turn_2_retention"] == 1.0
        assert seeds[str_s]["median_half_life"] == "NOT_REACHED"


# =============================================================================
# 16. NC5: Zero-Direction Null
# =============================================================================

def test_16_nc5_zero_direction_epistemic_null(results_data: dict):
    nc5 = results_data["negative_controls"]["nc5_zero_direction_null"]
    assert nc5["passed"] is True
    assert nc5["max_mean_abs_delta_dir"] <= 1e-8


# =============================================================================
# 17. NC6: Temporal Transition Null
# =============================================================================

def test_17_nc6_temporal_transition_null(results_data: dict):
    nc6 = results_data["negative_controls"]["nc6_temporal_transition_null"]
    assert nc6["passed"] is True
    assert nc6["max_mean_abs_delta"] <= TOLERANCE_EIG
    assert nc6["max_retention_rate"] == 0.0


# =============================================================================
# 18. NC7: Production Isolation
# =============================================================================

def test_18_nc7_production_isolation():
    cmd = ["git", "diff", "--stat", "src/core/", "src/api/", "electron/", "data/profile.json"]
    result = subprocess.run(cmd, cwd=str(REPO_ROOT), capture_output=True, text=True)
    assert result.returncode == 0
    assert result.stdout.strip() == "", f"Production files modified:\n{result.stdout}"


# =============================================================================
# 19. NC8: Genesis Profile Invariant
# =============================================================================

def test_19_nc8_genesis_profile_invariant():
    assert PROFILE_FILE.exists()
    content = PROFILE_FILE.read_text(encoding="utf-8").strip()
    assert content == '{"is_onboarded": false}'
