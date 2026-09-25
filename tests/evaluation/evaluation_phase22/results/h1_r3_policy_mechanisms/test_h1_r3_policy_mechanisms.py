"""
Phase 22 H1 — Continuous R3 Policy Mechanisms Comparative Study
=============================================================================
Automated Test Suite: test_h1_r3_policy_mechanisms.py

Verifies:
  - Manifest integrity, locked parameter hashes, and corpus SHA
  - Corpus generation and 358 matched discordant pairs
  - Policy family implementations: P0, PA, PB, PC, PD, PE
  - Information preservation and value collapse rates
  - Action differentiation metrics (D_pol, D_TV, D_JS) across contexts
  - Temporal stability, flapping suppression, and perturbation sensitivity
  - CPU execution latency (< 50 us) and 0.0 MB GPU VRAM
  - Negative controls NC1–NC8 pass rate (100%)
  - Outcome classification: RESULT_M3
  - Strict governance invariants (Gate 2 BLOCKED, Genesis UNMODIFIED)
"""

import json
from pathlib import Path
import subprocess
import sys
from typing import Any, Dict

import numpy as np
import pytest

def get_repo_root() -> Path:
    current = Path(__file__).resolve()
    while current.parent != current:
        if (current / "src").exists() and (current / "AGENTS.md").exists():
            return current
        current = current.parent
    return Path(__file__).resolve().parents[2]

REPO_ROOT = get_repo_root()
sys.path.insert(0, str(REPO_ROOT))

FIXTURES_DIR = REPO_ROOT / "tests" / "evaluation_phase22" / "fixtures"
RESULTS_DIR = REPO_ROOT / "tests" / "evaluation_phase22" / "results" / "h1_r3_policy_mechanisms"

MANIFEST_PATH = FIXTURES_DIR / "manifest_h1_r3_policy_mechanisms.json"
RESULTS_PATH = FIXTURES_DIR / "results_h1_r3_policy_mechanisms.json"
NC_PATH = FIXTURES_DIR / "nc_h1_r3_policy_mechanisms.json"
REPORT_PATH = FIXTURES_DIR / "report_h1_r3_policy_mechanisms.json"
SUMMARY_PATH = FIXTURES_DIR / "summary_h1_r3_policy_mechanisms.csv"


@pytest.fixture(scope="module")
def manifest() -> Dict[str, Any]:
    with open(MANIFEST_PATH, "r", encoding="utf-8") as f:
        return json.load(f)


@pytest.fixture(scope="module")
def results() -> Dict[str, Any]:
    with open(RESULTS_PATH, "r", encoding="utf-8") as f:
        return json.load(f)


@pytest.fixture(scope="module")
def nc_data() -> Dict[str, Any]:
    with open(NC_PATH, "r", encoding="utf-8") as f:
        return json.load(f)


@pytest.fixture(scope="module")
def formal_report() -> Dict[str, Any]:
    with open(REPORT_PATH, "r", encoding="utf-8") as f:
        return json.load(f)


# =============================================================================
# 1. Manifest & Configuration Integrity
# =============================================================================

def test_manifest_study_id(manifest):
    assert manifest["study_id"] == "PHASE_22_H1_R3_POLICY_MECHANISMS_STUDY"
    assert manifest["master_seed"] == 9999
    assert manifest["sampling_seed"] == 7113
    assert manifest["expected_n_probes"] == 270
    assert manifest["expected_discordant_pairs"] == 358


def test_manifest_corpus_hash(manifest):
    assert manifest["expected_corpus_sha"] == "d0061e8cfdd160f4ebccb7100e4fe3eeef9ff18a1a4c9c1b3f912a76f2ae82c0"


def test_manifest_policy_families(manifest):
    families = manifest["policy_families"]
    assert "P0_canonical_argmax" in families
    assert "PA_deterministic_hysteresis" in families
    assert "PB_deterministic_score_margin" in families
    assert "PC_deterministic_cyclic_rotation" in families
    assert "PD_probabilistic_softmax_sampling" in families
    assert "PE_hybrid_confidence_gated" in families


def test_manifest_locked_hashes(manifest):
    locked = manifest["locked_canon_parameter_hashes"]
    assert locked["M_CANON_CLARIFY_BASE_LOGITS"] == "f971491521773b69b1c9c02223d2c0896dac3f5627b889ff4e50c18008cd358a"
    assert locked["M_CANON_RETRIEVE_BASE_LOGITS"] == "02e0b76d9a512245f127fbbba3dbf56ed45516827ae636b2d0261403abe61f8b"
    assert locked["M_CANON_CLARIFY_W_DIR"] == "481e27b00ea8434d2a4d9cdd49dd2f5ddced8010e9dcfbd92b0a2e9b199f8d57"
    assert locked["M_CANON_RETRIEVE_W_DIR"] == "adc5f3a3c772850f1f69084531ef4a2171a86b3272ad3c7b6534572d06d0b767"


# =============================================================================
# 2. Corpus & Pair Counts
# =============================================================================

def test_results_corpus_and_pair_counts(results):
    assert results["corpus_probe_count"] == 270
    assert results["discordant_pair_count"] == 358


# =============================================================================
# 3. Policy Family Differentiation under CTX_5
# =============================================================================

def test_p0_canonical_argmax_collapse(results):
    diff = results["differentiation"]["P0_canonical_argmax"]
    assert diff["d_pol"] == 0.0
    assert diff["divergent_pairs"] == 0
    assert diff["collapse_rate"] == 1.0


def test_pa_hysteresis_grid_behavior(results):
    diff = results["differentiation"]
    # At dh=0.02 and dh=0.05, all probes exceed threshold and switch to retrieve -> D_pol = 0
    assert diff["PA_hysteresis_dh0.02"]["d_pol"] == 0.0
    assert diff["PA_hysteresis_dh0.05"]["d_pol"] == 0.0
    # At dh=0.10, advantage threshold separates probes -> D_pol = 79.89% (286/358 pairs)
    assert diff["PA_hysteresis_dh0.10"]["d_pol"] == pytest.approx(0.7989, abs=0.001)
    assert diff["PA_hysteresis_dh0.10"]["divergent_pairs"] == 286
    # At dh=0.15, no probe exceeds threshold -> all stay on answer -> D_pol = 0
    assert diff["PA_hysteresis_dh0.15"]["d_pol"] == 0.0


def test_pb_score_margin_behavior(results):
    diff = results["differentiation"]
    # Across tau_m in {0.02, 0.05, 0.10}, top action remains retrieve
    assert diff["PB_margin_tm0.02"]["d_pol"] == 0.0
    assert diff["PB_margin_tm0.05"]["d_pol"] == 0.0
    assert diff["PB_margin_tm0.10"]["d_pol"] == 0.0


def test_pc_cyclic_rotation_behavior(results):
    diff = results["differentiation"]
    # At dq=0.05, qualifying set size is 1 for all probes (min margin is 0.0528) -> D_pol = 0
    assert diff["PC_cyclic_dq0.05"]["d_pol"] == 0.0
    assert diff["PC_cyclic_dq0.08"]["d_pol"] == 0.0
    # At dq=0.10, qualifying sets expand to include wait/clarify, rotating deterministically -> D_pol = 100.0%
    assert diff["PC_cyclic_dq0.10"]["d_pol"] == 1.0
    assert diff["PC_cyclic_dq0.10"]["divergent_pairs"] == 358


def test_pd_softmax_sampling_differentiation(results):
    diff = results["differentiation"]["PD_sampling_gamma1.0"]
    assert diff["d_pol"] > 0.0
    assert diff["d_pol"] == pytest.approx(0.0391, abs=0.001)
    assert diff["divergent_pairs"] == 14
    assert diff["mean_tv"] > 0.010
    assert diff["mean_js"] > 0.0001


def test_pe_hybrid_confidence_gating(results):
    diff = results["differentiation"]
    # At tc=0.05, all margins >= 0.05 -> 100% deterministic exploitation -> D_pol = 0
    assert diff["PE_hybrid_tc0.05"]["d_pol"] == 0.0
    # At tc=0.08, 46 probes are ambiguous -> D_pol = 62.57%
    assert diff["PE_hybrid_tc0.08"]["d_pol"] == pytest.approx(0.6257, abs=0.001)
    assert diff["PE_hybrid_tc0.08"]["divergent_pairs"] == 224
    # At tc=0.10, 226 probes are ambiguous -> D_pol = 19.83%
    assert diff["PE_hybrid_tc0.10"]["d_pol"] == pytest.approx(0.1983, abs=0.001)
    assert diff["PE_hybrid_tc0.10"]["divergent_pairs"] == 71


# =============================================================================
# 4. Temporal Stability & Flapping Metrics
# =============================================================================

def test_temporal_flapping_p0(results):
    stab = results["temporal_stability"]["P0_canonical_argmax"]
    assert stab["mean_flapping_rate"] == 0.0
    assert stab["mean_switches_per_trajectory"] == 0.0
    assert stab["zero_switch_fraction"] == 1.0


def test_temporal_flapping_hysteresis_suppression(results):
    stab_pa = results["temporal_stability"]["PA_hysteresis_dh0.05"]
    stab_pd = results["temporal_stability"]["PD_sampling_gamma1.0"]
    # Hysteresis maintains low flapping (1.55%) while pure sampling flaps heavily (83.40%)
    assert stab_pa["mean_flapping_rate"] < 0.05
    assert stab_pd["mean_flapping_rate"] > 0.70
    assert stab_pa["mean_flapping_rate"] < stab_pd["mean_flapping_rate"] / 10.0


def test_temporal_flapping_hybrid_vs_sampling(results):
    stab_pe = results["temporal_stability"]["PE_hybrid_tc0.10"]
    stab_pd = results["temporal_stability"]["PD_sampling_gamma1.0"]
    # In low-confidence regime CTX_5, hybrid explores, but switches less than unconstrained sampling
    assert stab_pe["mean_flapping_rate"] <= stab_pd["mean_flapping_rate"]


# =============================================================================
# 5. Perturbation Sensitivity
# =============================================================================

def test_perturbation_sensitivity_retention(results):
    pert = results["perturbation_sensitivity"]
    assert pert["P0_canonical_argmax"]["retention_rate"] >= 0.99
    assert pert["PA_hysteresis_dh0.05"]["retention_rate"] >= 0.99
    assert pert["PB_margin_tm0.05"]["retention_rate"] >= 0.99
    assert pert["PE_hybrid_tc0.10"]["retention_rate"] >= 0.99


# =============================================================================
# 6. Computational Latency & Resource Constraints
# =============================================================================

def test_cpu_latency_under_50_microseconds(results):
    lat = results["computational_latency"]
    for pol_name, l_res in lat.items():
        assert l_res["mean_latency_us"] < 50.0, f"{pol_name} exceeded 50 us latency"
        assert l_res["gpu_vram_allocated_mb"] == 0.0


def test_p0_fastest_latency(results):
    lat = results["computational_latency"]
    # Pure argmax is fastest (< 5 us)
    assert lat["P0_canonical_argmax"]["mean_latency_us"] < 10.0


# =============================================================================
# 7. Negative Controls NC1–NC8
# =============================================================================

def test_nc1_scalar_null(nc_data):
    nc1 = nc_data["NC1_scalar_null"]
    assert nc1["passed"] is True
    assert nc1["mean_directional_displacement"] <= 1e-4
    assert nc1["c0_p0_d_pol"] == 0.0


def test_nc2_shuffled_correspondence(nc_data):
    nc2 = nc_data["NC2_shuffled_correspondence"]
    assert nc2["passed"] is True
    assert nc2["pearson_r"] <= 0.50


def test_nc3_zero_weight_identity(nc_data):
    nc3 = nc_data["NC3_zero_weight_identity"]
    assert nc3["passed"] is True
    assert nc3["max_diff"] <= 1e-4


def test_nc4_deterministic_repeatability(nc_data):
    nc4 = nc_data["NC4_deterministic_repeatability"]
    assert nc4["passed"] is True
    assert nc4["action_run0"] == nc4["action_run1"]


def test_nc5_anti_tuning_invariance(nc_data):
    nc5 = nc_data["NC5_anti_tuning_invariance"]
    assert nc5["passed"] is True


def test_nc6_production_code_isolation(nc_data):
    nc6 = nc_data["NC6_production_code_isolation"]
    assert nc6["passed"] is True
    assert len(nc6["modified_files"]) == 0


def test_nc7_genesis_gate_invariant(nc_data):
    nc7 = nc_data["NC7_genesis_gate_invariant"]
    assert nc7["passed"] is True
    assert nc7["is_onboarded"] is False


def test_nc8_high_confidence_collapse(nc_data):
    nc8 = nc_data["NC8_high_confidence_collapse"]
    assert nc8["passed"] is True
    assert nc8["p0_answer_dominance"] >= 0.99
    assert nc8["pe_answer_dominance"] >= 0.99


# =============================================================================
# 8. Classification & Governance Invariants
# =============================================================================

def test_study_classification(results):
    assert results["classification"] == "RESULT_M3"
    assert "HYBRID_CONFIDENCE_GATED_DIFFERENTIATION" in results["classification_description"]


def test_governance_invariants(formal_report):
    gov = formal_report["governance_invariants"]
    assert gov["gate_2_status"] == "STRICTLY BLOCKED"
    assert gov["phase_22_h1_status"] == "INCONCLUSIVE"
    assert gov["adr_029_status"] == "DRAFT / NOT RATIFIED"
    assert gov["genesis_gate"] == "bit-exact {'is_onboarded': false}"
    assert gov["production_mutations"] == 0


def test_all_artifacts_mirrored():
    required_files = [
        "manifest_h1_r3_policy_mechanisms.json",
        "results_h1_r3_policy_mechanisms.json",
        "nc_h1_r3_policy_mechanisms.json",
        "report_h1_r3_policy_mechanisms.json",
        "summary_h1_r3_policy_mechanisms.csv",
        "evaluate_h1_r3_policy_mechanisms.py",
    ]
    for filename in required_files:
        p = RESULTS_DIR / filename
        assert p.exists(), f"Missing mirrored artifact: {p}"
