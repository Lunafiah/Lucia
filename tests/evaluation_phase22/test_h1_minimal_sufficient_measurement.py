"""
Automated Verification Suite for Phase 22 H1 Minimal Sufficient Measurement
Architecture Research.

Validates:
1. Manifest integrity and SHA-256 hash match against results and script.
2. Governance invariants (0 src/core mutations, Genesis bit-exact, v1.5 locked).
3. RQ1: Information decomposition of scalar collapse pairs.
4. RQ2 & RQ3: Ablations A0–A8 and representations R0–R5 evaluated without composite ranking.
5. RQ4: Component necessity showing Arousal divergence and opposing Pleasure divergence.
6. RQ5: Directional sufficiency analysis without claiming architectural equivalence.
7. RQ6: Hybrid scalar + side-channel evaluation.
8. RQ7: Conversational timescale viability across T in {1, 2, 4, 8, 12, 16, 25}.
9. RQ8: Prediction-error semantics distinction preserved.
10. RQ9: Non-composite minimality assessment and final governance state.
"""

from __future__ import annotations

import hashlib
import json
from pathlib import Path
import pytest

REPO_ROOT = Path(__file__).resolve().parent.parent.parent
RESULTS_FILE = REPO_ROOT / "tests" / "evaluation_phase22" / "results" / "h1_minimal_sufficient_measurement" / "minimal_sufficient_results.json"
MANIFEST_FILE = REPO_ROOT / "tests" / "evaluation_phase22" / "fixtures" / "manifest_h1_minimal_sufficient_measurement.json"
SCRIPT_FILE = REPO_ROOT / "tests" / "evaluation_phase22" / "scripts" / "analyze_minimal_sufficient_measurement.py"
GENESIS_PROFILE = REPO_ROOT / "data" / "profile.json"


@pytest.fixture(scope="module")
def study_data():
    assert RESULTS_FILE.exists(), f"Results file does not exist: {RESULTS_FILE}"
    with open(RESULTS_FILE, "r", encoding="utf-8") as f:
        return json.load(f)


@pytest.fixture(scope="module")
def manifest_data():
    assert MANIFEST_FILE.exists(), f"Manifest file does not exist: {MANIFEST_FILE}"
    with open(MANIFEST_FILE, "r", encoding="utf-8") as f:
        return json.load(f)


def test_manifest_integrity(manifest_data):
    """Verify SHA-256 hashes in manifest match disk files exactly."""
    file_hashes = manifest_data["file_hashes"]

    # Verify script hash
    with open(SCRIPT_FILE, "rb") as f:
        actual_script_hash = hashlib.sha256(f.read()).hexdigest()
    assert actual_script_hash == file_hashes["script_hash"], "Script SHA-256 mismatch against manifest"

    # Verify results hash
    with open(RESULTS_FILE, "rb") as f:
        actual_results_hash = hashlib.sha256(f.read()).hexdigest()
    assert actual_results_hash == file_hashes["results_hash"], "Results SHA-256 mismatch against manifest"


def test_governance_invariants(manifest_data):
    """Verify core governance invariants are strictly respected."""
    invariants = manifest_data["governance_invariants"]
    assert invariants["src_core_mutations"] == 0
    assert invariants["genesis_onboarding_bit_exact"] is True
    assert invariants["protocol_v15_authorized"] is False
    assert invariants["architecture_gate_locked"] is True

    # Verify Genesis profile bit-exact
    with open(GENESIS_PROFILE, "r", encoding="utf-8") as f:
        profile_content = f.read().strip()
    assert profile_content == '{"is_onboarded": false}', "Genesis onboarding profile was modified!"


def test_rq1_information_decomposition(study_data):
    """Verify information decomposition of scalar collapse pairs at T=12."""
    rq1 = study_data["rq1_information_decomposition"]["results_by_exposure_t"]["12"]
    assert rq1["mh_collapse_count"] == 358
    assert rq1["mh_mean_angle_deg"] > 80.0
    assert rq1["mh_mean_vector_distance"] > 0.80
    assert rq1["mh_mean_diff_pleasure"] > 0.50
    assert rq1["mh_mean_diff_arousal"] > 0.25


def test_rq2_rq3_ablation_results(study_data):
    """Verify predefined ablation results at T=12 without composite ranking."""
    ablations = study_data["rq2_rq3_ablations"]["results_t12"]

    # A0 (Full vector) has 0 MH collapses
    assert ablations["A0_full_vector"]["mh_collapses"] == 0

    # A4 (Magnitude only) has 358 MH collapses
    assert ablations["A4_magnitude_only"]["mh_collapses"] == 358

    # A3 (Remove Dominance) has 0 MH collapses (proving Dominance is not strictly needed for collapse resolution)
    assert ablations["A3_remove_dominance"]["mh_collapses"] == 0

    # A2 (Remove Arousal) has collapses because Arousal provides major separation
    assert ablations["A2_remove_arousal"]["mh_collapses"] > 0

    # A5 (Sign only) has 0 MH collapses
    assert ablations["A5_sign_only"]["mh_collapses"] == 0


def test_rq4_component_necessity(study_data):
    """Verify component necessity analysis: Arousal is highly discriminative, Pleasure opposes."""
    comps = study_data["rq4_component_necessity"]

    assert "Pleasure" in comps
    assert "Arousal" in comps
    assert "Dominance" in comps

    # Arousal Cohen's d > 8.0
    assert comps["Arousal"]["cohens_d_hm"] > 8.0
    assert "Empirically discriminative under the frozen evaluation regime" in comps["Arousal"]["necessity_verdict"]

    # Pleasure Cohen's d is negative (opposite direction)
    assert comps["Pleasure"]["cohens_d_hm"] < 0.0

    # Dominance is common-mode / small effect
    assert abs(comps["Dominance"]["cohens_d_hm"]) < 2.0


def test_rq5_directional_sufficiency(study_data):
    """Verify directional sufficiency analysis."""
    rq5 = study_data["rq5_directional_sufficiency"]
    assert rq5["R0_scalar_magnitude"]["mh_collapses_t12"] == 358
    assert rq5["R4_magnitude_plus_direction"]["mh_collapses_t12"] == 0
    assert rq5["R5_full_vector_residual"]["mh_collapses_t12"] == 0


def test_rq6_side_channel_architecture(study_data):
    """Verify scalar + side-channel hybrid analysis."""
    side_channels = study_data["rq6_side_channel_architecture"]
    assert side_channels["S_plus_sign_r"]["mh_collapses_t12"] == 0
    assert side_channels["S_plus_unit_direction"]["mh_collapses_t12"] == 0
    assert side_channels["S_plus_arousal_component"]["mh_collapses_t12"] == 0
    assert side_channels["S_plus_pleasure_arousal"]["mh_collapses_t12"] == 0


def test_rq7_conversational_timescale(study_data):
    """Verify conversational timescale viability: R0 collapses across T <= 25, R2 has 0 collapses, R3 resolves by T=12."""
    rq7 = study_data["rq7_conversational_timescale"]
    for t_str in ["1", "2", "4", "8", "12", "16", "25"]:
        t_data = rq7[t_str]
        assert t_data["r0_scalar_collapses"] > 0
        assert t_data["r2_dir_collapses"] == 0
        assert t_data["r3_sign_collapses"] <= t_data["r0_scalar_collapses"]
        if int(t_str) >= 12:
            assert t_data["r3_sign_collapses"] == 0


def test_rq8_prediction_error_semantics(study_data):
    """Verify prediction-error semantics vs bodily displacement."""
    rq8 = study_data["rq8_prediction_error_semantics"]
    assert "Under unadapted initial persistence prior" in rq8["mathematical_identity_under_unadapted_beliefs"]
    assert "179.5 degrees" in rq8["empirical_divergence_under_adapted_beliefs"]
    assert "MUST preserve prediction-residual semantics" in rq8["canonical_interpretation_requirement"]


def test_rq9_minimality_and_final_state(study_data):
    """Verify minimality evaluation and final state classification."""
    minimality = study_data["rq9_minimality_assessment"]
    r3_eval = next(m for m in minimality if m["id"] == "R3")
    assert "POTENTIALLY MINIMALLY SUFFICIENT" in r3_eval["verdict"]

    r5_eval = next(m for m in minimality if m["id"] == "R5")
    assert "SUFFICIENT BUT NOT MINIMAL" in r5_eval["verdict"]

    synth = study_data["final_synthesis"]
    assert synth["final_state"] == "State B — Minimal Side-Channel Appears Sufficient to Avoid Collapse"
    assert synth["protocol_v15_status"] == "NOT AUTHORIZED"
    assert synth["architecture_gate_status"] == "STRICTLY LOCKED"
    assert synth["production_mutation_status"] == "0 mutations allowed / 0 performed"
