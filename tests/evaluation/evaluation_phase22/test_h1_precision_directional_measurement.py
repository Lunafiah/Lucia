"""
Automated Verification Suite for Phase 22 H1 Precision-Weighted & Directional
Measurement Architecture Research.

Validates:
1. Manifest integrity and SHA-256 hash match against results and script.
2. Governance invariants (0 src/core mutations, Genesis bit-exact, v1.5 locked).
3. RQ1: M0–M5 representation matrix characterization (3 effective DOF for M2/M3, no composite score).
4. RQ2: Predefined precision structures Pi_0–Pi_3 evaluated with guardrails preserved.
5. RQ3: Component-wise statistical separation (Pleasure vs Arousal divergence).
6. RQ4: Directional persistence under magnitude matching with exact required verdict string.
7. RQ5: Mathematical identity under unadapted prior and empirical divergence under adapted prior.
8. RQ6: Evidence inventory & conceptual compatibility classification (no claimed validation).
9. RQ7: Scoped viability of M0 and conversational viability of vector representations across T <= 25.
10. RQ8: Architectural semantics distinguishing physiological surprise from epistemic uncertainty.
"""

from __future__ import annotations

import hashlib
import json
from pathlib import Path
import pytest

REPO_ROOT = Path(__file__).resolve().parent.parent.parent
RESULTS_FILE = REPO_ROOT / "tests" / "evaluation_phase22" / "results" / "h1_precision_directional_measurement" / "precision_directional_results.json"
MANIFEST_FILE = REPO_ROOT / "tests" / "evaluation_phase22" / "fixtures" / "manifest_h1_precision_directional_measurement.json"
SCRIPT_FILE = REPO_ROOT / "tests" / "evaluation_phase22" / "scripts" / "analyze_precision_directional_measurement.py"
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


def test_rq1_representation_matrix(study_data):
    """Verify M0-M5 representation matrix properties (3 effective DOF for M2/M3, no composite score)."""
    reps = study_data["rq1_representations"]
    assert len(reps) == 6
    rep_ids = [r["id"] for r in reps]
    assert rep_ids == ["M0", "M1", "M2", "M3", "M4", "M5"]

    # Verify M2 and M3 have 3 effective DOF
    m2 = next(r for r in reps if r["id"] == "M2")
    m3 = next(r for r in reps if r["id"] == "M3")
    assert m2["effective_dof"] == 3
    assert m3["effective_dof"] == 3
    assert "3 effective DOF" in m2["dimension"]
    assert "3 effective DOF" in m3["dimension"]

    # Verify NO composite score was computed
    for r in reps:
        assert "composite_score" not in r
        assert "winner" not in r


def test_rq2_precision_candidates_evaluated(study_data):
    """Verify all 4 predefined precision structures are evaluated with guardrails preserved."""
    rq2 = study_data["rq2_precision_weighting"]
    cands = rq2["precision_candidates_definitions"]
    assert "Pi_0_identity" in cands
    assert "Pi_1_arousal_exploratory" in cands
    assert "Pi_2_geometric_headroom" in cands
    assert "Pi_3_mt_lnn_coupled" in cands

    # Verify Pi_1 guardrail note
    pi1_note = cands["Pi_1_arousal_exploratory"]["guardrail_note"]
    assert "Unvalidated exploratory theoretical candidate" in pi1_note
    assert "NOT be claimed as evidence for higher physiological importance of Arousal" in pi1_note

    # Verify Pi_2 guardrail note
    pi2_note = cands["Pi_2_geometric_headroom"]["guardrail_note"]
    assert "NOT automatically biological precision" in pi2_note

    # Verify T=12 results for all 4 candidates
    t12_cands = rq2["results_by_exposure_t"]["12"]["candidates"]
    assert len(t12_cands) == 4
    # Pi_0 fails Gate 2 HM
    assert t12_cands["Pi_0_identity"]["gate2_hm_pass"] is False
    # Pi_2 fails Gate 2 HM
    assert t12_cands["Pi_2_geometric_headroom"]["gate2_hm_pass"] is False
    # Pi_3 fails Gate 2 HM
    assert t12_cands["Pi_3_mt_lnn_coupled"]["gate2_hm_pass"] is False


def test_rq3_component_separation(study_data):
    """Verify independent component analysis shows Arousal separation and Pleasure divergence."""
    rq3 = study_data["rq3_component_wise"]["results_by_exposure_t"]
    t12_comps = rq3["12"]["components"]
    assert "Pleasure" in t12_comps
    assert "Arousal" in t12_comps
    assert "Dominance" in t12_comps

    # Arousal High vs Med has large positive effect size
    arousal_d = t12_comps["Arousal"]["comparisons"]["High_vs_Med"]["cohens_d"]
    assert arousal_d > 8.0, f"Expected Arousal Cohen's d > 8.0, got {arousal_d}"

    # Pleasure High vs Med has negative difference
    pleasure_diff = t12_comps["Pleasure"]["comparisons"]["High_vs_Med"]["diff_mean"]
    assert pleasure_diff < 0.0, f"Expected Pleasure diff < 0.0, got {pleasure_diff}"


def test_rq4_directional_magnitude_matched(study_data):
    """Verify directional persistence under magnitude matching with exact required verdict string."""
    rq4 = study_data["rq4_directional_magnitude_matched"]["results_by_exposure_t"]
    for t_str in ["1", "2", "4", "8", "12", "16", "25"]:
        t_res = rq4[t_str]
        assert t_res["rq4_verdict"] == "EVIDENCE CONSISTENT WITH DIRECTIONAL/COMPONENT INFORMATION PERSISTING AFTER MAGNITUDE MATCHING"
        if t_res["matched_mh_pairs_count"] > 0:
            assert t_res["matched_mh_mean_angle_deg"] > 45.0


def test_rq5_displacement_vs_residual(study_data):
    """Verify unadapted identity r_T = -Delta_p and adapted divergence."""
    rq5 = study_data["rq5_displacement_vs_residual"]["results_by_exposure_t"]
    t12 = rq5["12"]["tiers"]["Med"]
    # Unadapted norm difference must be zero (< 1e-9)
    assert t12["max_unadapted_norm_diff"] < 1e-9
    # Adapted residual must diverge from displacement
    assert t12["mean_adapted_divergence_diff"] > 0.01


def test_rq6_homeostatic_inventory(study_data):
    """Verify RQ6 evidence inventory & conceptual compatibility classification (no validation claimed)."""
    rq6 = study_data["rq6_homeostatic_relevance"]
    assert rq6["conceptual_status_classification"] == "B — Plausible future research direction, but currently unsupported by validated production evidence"
    assert "No parameter fitting performed" in rq6["guardrail_compliance"]
    assert "no claims of biological validation made" in rq6["guardrail_compliance"]


def test_rq7_conversational_timescale_viability(study_data):
    """Verify scoped viability of M0 and viability of vector representations across T <= 25."""
    rq7 = study_data["rq7_conversational_timescale"]["findings_by_representation"]
    m0_viability = rq7["M0_canonical_scalar"]["conversational_viability"]
    assert "M0 does not satisfy the current preregistered dual Gate 2 thresholds at T <= 25" in m0_viability

    for rep in ["M1_displacement_vector", "M2_magnitude_direction", "M3_residual_magnitude_direction", "M4_full_residual_vector"]:
        assert "HIGHLY VIABLE" in rq7[rep]["conversational_viability"]


def test_rq8_architectural_semantics(study_data):
    """Verify distinction between physiological surprise and epistemic uncertainty."""
    rq8 = study_data["rq8_architectural_semantics"]
    assert "physiological_surprise" in rq8["conceptual_distinction"]
    assert "epistemic_uncertainty" in rq8["conceptual_distinction"]


def test_final_synthesis_and_governance(study_data):
    """Verify final synthesis state, locked gate, and unauthorized v1.5."""
    synth = study_data["final_synthesis"]
    assert synth["final_state"] == "State B — Direction/Component Information Demonstrably Omitted Under Scalar S"
    assert synth["protocol_v15_status"] == "NOT AUTHORIZED"
    assert synth["architecture_gate_status"] == "STRICTLY LOCKED"
    assert synth["production_mutation_status"] == "0 mutations allowed / 0 performed"
