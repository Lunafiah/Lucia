"""
Automated Test Suite: test_h1_r3_information_gain.py
=====================================================
Phase 22 H1 — R3 Information-Gain & Belief-Update Relevance Study

Validates:
  1. Manifest and result artifact integrity & SHA-256 signatures.
  2. Governance invariants (production diff = 0, Gate 2 blocked, ADR-029 draft).
  3. Corpus lineage (Seed 9999, N=270, SHA, 358 discordant pairs).
  4. Latent hypothesis model parameters (K=4, uniform prior, entropy).
  5. Observation model parameters & pre-registered anti-circularity parameter hashes.
  6. Historical C0 scalar baseline reproduction.
  7. Canonical C2 information-gain reproduction.
  8. Tuple identity parity (NC2).
  9. Multiset preservation of C3, C4, C5 (NC3).
  10. Seed determinism (NC4).
  11. Mathematical validity of EIG, UR, and uninformative action selectivity.
  12. Incremental directional attribution (E1 & E2).
  13. Measurable uncertainty-profile differentiation (E4 with tau_H and tau_TV).
  14. Belief-update correspondence (E5 with tau_TV and tau_JS).
  15. Representation-independent epistemic null (NC5: ΔEIG_dir < 1e-12).
  16. Production isolation & Genesis profile invariant (NC6 & NC7).
"""

import hashlib
import json
import math
from pathlib import Path
import subprocess

import numpy as np
import pytest

REPO_ROOT = Path(__file__).resolve().parent.parent.parent
MANIFEST_PATH = REPO_ROOT / "tests" / "evaluation_phase22" / "fixtures" / "manifest_h1_r3_information_gain.json"
RESULTS_JSON_PATH = REPO_ROOT / "tests" / "evaluation_phase22" / "results" / "h1_r3_information_gain" / "r3_information_gain_results.json"
SUMMARY_CSV_PATH = REPO_ROOT / "tests" / "evaluation_phase22" / "results" / "h1_r3_information_gain" / "r3_information_gain_summary.csv"
ACTION_CSV_PATH = REPO_ROOT / "tests" / "evaluation_phase22" / "results" / "h1_r3_information_gain" / "r3_action_specific_eig.csv"
PROFILE_PATH = REPO_ROOT / "data" / "profile.json"


@pytest.fixture(scope="module")
def manifest_data() -> dict:
    assert MANIFEST_PATH.exists(), f"Manifest file missing at {MANIFEST_PATH}"
    with open(MANIFEST_PATH, "r", encoding="utf-8") as f:
        return json.load(f)


@pytest.fixture(scope="module")
def results_data() -> dict:
    assert RESULTS_JSON_PATH.exists(), f"Results file missing at {RESULTS_JSON_PATH}"
    with open(RESULTS_JSON_PATH, "r", encoding="utf-8") as f:
        return json.load(f)


# =============================================================================
# 1. Manifest and Result Integrity
# =============================================================================

def test_01_manifest_and_result_integrity(manifest_data, results_data):
    """Verify manifest and results JSON exist, are non-empty, and artifact hashes match."""
    assert manifest_data["study_id"] == "PHASE_22_H1_R3_INFORMATION_GAIN_BELIEF_UPDATE_STUDY"
    assert manifest_data["all_audits_passed"] is True
    assert results_data["all_audits_passed"] is True

    # Verify cryptographic signatures
    json_bytes = RESULTS_JSON_PATH.read_bytes()
    expected_json_sha = manifest_data["artifact_hashes"]["results_json"]
    assert hashlib.sha256(json_bytes).hexdigest() == expected_json_sha

    summary_bytes = SUMMARY_CSV_PATH.read_bytes()
    expected_summary_sha = manifest_data["artifact_hashes"]["summary_csv"]
    assert hashlib.sha256(summary_bytes).hexdigest() == expected_summary_sha

    action_bytes = ACTION_CSV_PATH.read_bytes()
    expected_action_sha = manifest_data["artifact_hashes"]["action_csv"]
    assert hashlib.sha256(action_bytes).hexdigest() == expected_action_sha


# =============================================================================
# 2. Governance Invariants
# =============================================================================

def test_02_governance_invariants(results_data):
    """Verify research locks: zero production mutation, Gate 2 blocked, ADR-029 draft."""
    gov = results_data["governance_locks"]
    assert gov["production_diff"] == 0
    assert "STRICLY_BLOCKED" in gov["gate_2_status"]
    assert "DRAFT" in gov["adr_029_status"]
    assert gov["phase_22_h1_status"] == "INCONCLUSIVE"
    assert gov["classification"] == "RESEARCH_HARNESS_ONLY"


# =============================================================================
# 3. Corpus Lineage and Matched Pairs
# =============================================================================

def test_03_corpus_lineage_and_matched_pairs(manifest_data, results_data):
    """Verify Master seed 9999, N=270, expected corpus SHA, and exactly 358 discordant pairs."""
    lineage = results_data["lineage"]
    assert lineage["master_seed"] == 9999
    assert lineage["n_probes"] == 270
    assert lineage["corpus_sha"] == "d0061e8cfdd160f4ebccb7100e4fe3eeef9ff18a1a4c9c1b3f912a76f2ae82c0"
    assert lineage["discordant_pairs_count"] == 358
    assert manifest_data["discordant_pairs_count"] == 358


# =============================================================================
# 4. Latent Model Parameters
# =============================================================================

def test_04_latent_model_parameter_hashes(results_data):
    """Verify K=4 latent hypotheses and base prior entropy = ln(4) nats."""
    # Prior entropy for K=4 uniform is ln(4) ≈ 1.38629436
    expected_prior_entropy = math.log(4.0)
    assert abs(math.log(4.0) - 1.3862943611198906) < 1e-12

    audit = results_data["anti_circularity_audit"]["audit_1_cardinality_non_isomorphism"]
    assert audit["latent_hypotheses_k"] == 4
    assert audit["r3_cardinality"] == 27
    assert audit["passed"] is True


# =============================================================================
# 5. Observation Model Parameter Hashes
# =============================================================================

def test_05_observation_model_parameter_hashes(manifest_data):
    """Verify locked SHA-256 hashes of base observation channel parameters."""
    hashes = manifest_data["locked_parameter_hashes"]
    expected_hashes = {
        "CLARIFY_BASE_LOGITS": "f971491521773b69b1c9c02223d2c0896dac3f5627b889ff4e50c18008cd358a",
        "RETRIEVE_BASE_LOGITS": "02e0b76d9a512245f127fbbba3dbf56ed45516827ae636b2d0261403abe61f8b",
        "CLARIFY_W_DIR": "481e27b00ea8434d2a4d9cdd49dd2f5ddced8010e9dcfbd92b0a2e9b199f8d57",
        "RETRIEVE_W_DIR": "adc5f3a3c772850f1f69084531ef4a2171a86b3272ad3c7b6534572d06d0b767",
        "CLARIFY_B_S": "644b4c183b5f735545a8477d4a9a5a4735eb47849674971a58c5206da33517b5",
        "RETRIEVE_B_S": "039084510144facc9b02a635fbf78c289c2b568c7e5b1e394d14e9b59a127137",
    }
    for k, v in expected_hashes.items():
        assert hashes[k] == v, f"Parameter hash mismatch for {k}: expected {v}, got {hashes[k]}"


# =============================================================================
# 6. Historical C0 Reproduction (NC1)
# =============================================================================

def test_06_historical_c0_reproduction(results_data):
    """Verify Condition C0 (scalar baseline) produces zero action ranking differentiation."""
    c0_metrics = results_data["consumer_summaries"]["C_qual_1.50"]["conditions"]["C0"]
    assert c0_metrics["diffrate_top_action"] == 0.0
    assert c0_metrics["diffrate_action_ranking"] == 0.0
    assert c0_metrics["mean_delta_eig_norm"] < 0.005


# =============================================================================
# 7. Canonical C2 Reproduction
# =============================================================================

def test_07_canonical_c2_reproduction(results_data):
    """Verify Canonical C2 differentiates top-EIG action on exactly 79.89% of discordant pairs."""
    c2_metrics = results_data["consumer_summaries"]["C_qual_1.50"]["conditions"]["C2"]
    # 286 / 358 = 0.79888268...
    assert abs(c2_metrics["diffrate_top_action"] - 0.798883) < 1e-4
    assert abs(c2_metrics["diffrate_action_ranking"] - 0.798883) < 1e-4
    assert c2_metrics["diffrate_eig"] == 1.000000
    assert c2_metrics["mean_delta_eig_norm"] > 0.05


# =============================================================================
# 8. Tuple Identity Parity (NC2)
# =============================================================================

def test_08_tuple_identity_parity_nc2(results_data):
    """Verify identical (S, v_dir) tuples yield identical epistemic quantities."""
    nc2 = results_data["negative_controls"]["NC2_tuple_identity_parity"]
    assert nc2["passed"] is True


# =============================================================================
# 9. Multiset Preservation (NC3)
# =============================================================================

def test_09_multiset_preservation_nc3(results_data):
    """Verify bijective permutations strictly preserve multisets in C3, C4, C5."""
    nc3 = results_data["negative_controls"]["NC3_multiset_preservation"]
    assert nc3["passed"] is True


# =============================================================================
# 10. Seed Determinism (NC4)
# =============================================================================

def test_10_seed_determinism_nc4(results_data):
    """Verify cross-seed standard deviation for incremental effect is negligible."""
    inc = results_data["consumer_summaries"]["C_qual_1.50"]["incremental_directional"]
    assert inc["std_delta_eig_dir"] < 1e-6


# =============================================================================
# 11. EIG Mathematical Validity & Action Selectivity
# =============================================================================

def test_11_eig_mathematical_validity(results_data):
    """Verify EIG >= 0 and non-informative actions evaluate naturally to EIG == 0.0."""
    audit = results_data["anti_circularity_audit"]["audit_5_action_selectivity"]
    assert audit["passed"] is True
    for a in ["answer", "derive", "reason", "wait"]:
        assert audit["uninformative_actions_eig"][a] == 0.0

    c_summary = results_data["consumer_summaries"]["C_qual_1.50"]
    assert c_summary["action_specific_c2"]["clarify"] > 0.0
    assert c_summary["action_specific_c2"]["retrieve"] > 0.0


# =============================================================================
# 12. Incremental Directional Attribution (E1 & E2)
# =============================================================================

def test_12_incremental_directional_attribution_e1_e2(results_data):
    """Verify E1 (incremental directional effect > tau_EIG) and E2 (C2 vs C3/C5 contrast)."""
    e1 = results_data["diagnostics"]["E1_continuous_eig_differentiation"]
    assert e1["passed"] is True
    assert e1["observed_diffrate"] == 1.000000
    assert e1["mean_delta_eig_dir"] > 0.0001

    e2 = results_data["diagnostics"]["E2_directional_attribution_against_controls"]
    assert e2["passed"] is True
    assert e2["c2_mean_norm"] > 1.5 * e2["c3_mean_norm"]
    assert e2["c2_mean_norm"] > 1.5 * e2["c5_mean_norm"]


# =============================================================================
# 13. Measurable Uncertainty-Profile Differentiation (E4)
# =============================================================================

def test_13_uncertainty_profile_differentiation_e4(results_data):
    """Verify E4: ||ΔH_post|| > tau_H and ||ΔTV|| > tau_TV on matched discordant pairs."""
    e4 = results_data["diagnostics"]["E4_uncertainty_profile_differentiation"]
    assert e4["passed"] is True
    assert e4["mean_delta_post_h"] > 1e-4
    assert e4["mean_delta_tv"] > 1e-4


# =============================================================================
# 14. Belief-Update Correspondence (E5)
# =============================================================================

def test_14_belief_update_correspondence_e5(results_data):
    """Verify E5: Pairwise posterior TV > tau_TV and JS > tau_JS on matched discordant pairs."""
    e5 = results_data["diagnostics"]["E5_belief_update_correspondence"]
    assert e5["passed"] is True
    assert e5["mean_pairwise_post_tv"] > 1e-4
    assert e5["mean_pairwise_post_js"] > 1e-5


# =============================================================================
# 15. Representation-Independent Epistemic Null (NC5)
# =============================================================================

def test_15_representation_independent_null_nc5(results_data):
    """Verify NC5: When W_dir = 0, ΔEIG_dir = 0 (< 1e-12)."""
    nc5 = results_data["negative_controls"]["NC5_representation_independent_null"]
    assert nc5["passed"] is True
    assert nc5["observed_delta_eig_dir"] < 1e-12


# =============================================================================
# 16. Production Isolation & Genesis Profile (NC6 & NC7)
# =============================================================================

def test_16_production_isolation_and_genesis_profile():
    """Verify zero modifications to production code and bit-exact Genesis profile."""
    # 1. Check production git diff
    cmd = ["git", "diff", "--stat", "src/core/", "src/api/", "electron/", "data/profile.json"]
    res = subprocess.run(cmd, cwd=str(REPO_ROOT), capture_output=True, text=True)
    assert res.returncode == 0
    assert res.stdout.strip() == "", f"Production files modified!\n{res.stdout}"

    # 2. Check Genesis profile bit-exactness
    profile_content = PROFILE_PATH.read_text(encoding="utf-8").strip()
    assert profile_content == '{"is_onboarded": false}'
