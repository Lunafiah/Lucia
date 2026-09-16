"""
Phase 22 H1 — Gate 2 Resolution Study Test Suite.

Verifies:
1. Conversational exposure grid constraint (T in {1, 2, 4, 8, 12, 16, 25}).
2. Component-wise effect size (Cohen's d) and confidence interval mathematical validity.
3. Directional geometry diagnostic properties and angular separation identities.
4. Candidate diagnostics classification and Candidate 6 prediction-residual designation.
5. Exact scoped phrasing for RQ3 empirical gate evaluation.
6. Manifest and JSON results SHA-256 digest integrity.
7. Genesis onboarding bit-exact invariant and zero production code mutations.
"""

import hashlib
import json
import math
import subprocess
from pathlib import Path
import numpy as np
import pytest

REPO_ROOT = Path(__file__).resolve().parent.parent.parent

from src.core.config import EmotionConfig, StimulusConfig
from src.core.emotion.emotion_core import EmotionCore, PADState
from src.core.inference.active_inference import ActiveInferenceConfig, ActiveInferenceEngine
from tests.evaluation_phase22.scripts.analyze_gate2_resolution import (
    Gate2ResolutionStudyEngine,
    compute_angle_deg,
    compute_projection,
    compute_cohens_d,
    compute_diff_ci95,
    T_CONVERSATIONAL,
    T_EXPLORATORY,
    RESULTS_DIR,
    FIXTURES_DIR,
)


@pytest.fixture
def engine():
    return Gate2ResolutionStudyEngine()


def test_conversational_exposure_grid():
    """Verify that the primary conversational grid consists strictly of T <= 25."""
    assert T_CONVERSATIONAL == [1, 2, 4, 8, 12, 16, 25]
    for t in T_CONVERSATIONAL:
        assert t <= 25, f"T={t} exceeds conversational threshold of 25 ticks!"
    assert T_EXPLORATORY == [50, 100]


def test_cohens_d_and_ci_math():
    """Verify mathematical properties of compute_cohens_d and compute_diff_ci95."""
    # Identical distributions -> Cohen's d = 0, CI centered at 0
    d = compute_cohens_d(0.5, 0.5, 0.1, 0.1)
    assert abs(d) < 1e-9
    ci_low, ci_high = compute_diff_ci95(0.5, 0.5, 0.1, 0.1, 90, 90)
    assert abs((ci_low + ci_high) / 2.0) < 1e-9
    assert ci_low < 0 < ci_high

    # Clear separation -> positive Cohen's d
    d2 = compute_cohens_d(0.2, 0.6, 0.1, 0.1)
    assert d2 > 3.0
    ci2_low, ci2_high = compute_diff_ci95(0.2, 0.6, 0.1, 0.1, 90, 90)
    assert ci2_low > 0.35 and ci2_high < 0.45


def test_directional_geometry_bounds():
    """Verify angular values lie strictly in [0, 180] degrees and projection identities."""
    v1 = np.array([1.0, 2.0, 3.0])
    v2 = np.array([-1.0, -2.0, -3.0])
    v3 = np.array([0.0, 0.0, 0.0])

    assert abs(compute_angle_deg(v1, v2) - 180.0) < 1e-6
    assert abs(compute_angle_deg(v1, v1) - 0.0) < 1e-6
    assert compute_angle_deg(v1, v3) == 0.0  # Zero norm handling
    assert compute_projection(v1, v3) == 0.0


def test_directional_diagnostics_non_replacement():
    """
    Ensure directional metrics remain strictly diagnostic and do not alter
    the canonical Active Inference scalar surprise calculation.
    """
    ai = ActiveInferenceEngine(ActiveInferenceConfig())
    p0 = EmotionCore(EmotionConfig()).get_pad_state()
    pt = PADState(pleasure=p0.pleasure, arousal=0.50, dominance=p0.dominance, timestamp=p0.timestamp)

    s_scalar = ai.step(p0, pt)
    d_euc = math.sqrt((pt.pleasure - p0.pleasure)**2 + (pt.arousal - p0.arousal)**2 + (pt.dominance - p0.dominance)**2)
    assert abs(float(s_scalar) - d_euc) < 1e-6


def test_rq4_candidate_diagnostics_classification():
    """Verify that all 6 candidate diagnostics are properly classified."""
    results_path = RESULTS_DIR / "gate2_resolution_results.json"
    if not results_path.exists():
        pytest.skip("Results not yet generated.")

    with open(results_path, "r", encoding="utf-8") as f:
        data = json.load(f)

    candidates = data["table_d_candidate_diagnostics"]
    assert len(candidates) == 6

    valid_roles = {
        "diagnostic only (canonical Active Inference baseline)",
        "diagnostic only",
        "potentially suitable for future architecture research",
        "invalid / unstable",
    }
    for c in candidates:
        assert c["role_classification"] in valid_roles or c["status_verdict"] in valid_roles

    # Candidate 6 must be explicitly designated as a prediction-residual diagnostic
    cand6 = candidates[5]
    assert "Prediction-Residual" in cand6["name"] or "prediction residual" in cand6["weaknesses"].lower()


def test_rq3_scoped_verdict_wording():
    """Verify that RQ3 uses the exact mandatory scoped phrasing."""
    results_path = RESULTS_DIR / "gate2_resolution_results.json"
    if not results_path.exists():
        pytest.skip("Results not yet generated.")

    with open(results_path, "r", encoding="utf-8") as f:
        data = json.load(f)

    verdict = data["rq3_evaluation"]["scoped_verdict"]
    expected_fragment = "Current dual Gate 2 thresholds are not simultaneously achieved for T <= 25 under the frozen G1 stimulus set and current scalar S measurement."
    assert expected_fragment in verdict, f"Unexpected RQ3 verdict: {verdict}"


def test_manifest_and_results_integrity():
    """Verify that results JSON and manifest exist, have matching SHA-256 digests, and correct structure."""
    results_path = RESULTS_DIR / "gate2_resolution_results.json"
    manifest_path = FIXTURES_DIR / "manifest_h1_gate2_resolution.json"

    if not results_path.exists() or not manifest_path.exists():
        pytest.skip("Results or manifest not yet generated.")

    with open(manifest_path, "r", encoding="utf-8") as f:
        manifest = json.load(f)

    calculated_digest = hashlib.sha256(results_path.read_bytes()).hexdigest()
    assert manifest["results_digest_sha256"] == calculated_digest
    assert manifest["seed"] == 9999
    assert manifest["sample_size"] == 270
    assert manifest["conversational_grid"] == [1, 2, 4, 8, 12, 16, 25]
    assert manifest["governance_status"] == "RESEARCH_ONLY_LOCKED"


def test_genesis_gate_and_production_invariants():
    """Ensure Genesis onboarding profile is bit-exact and src/core/ has 0 modifications."""
    profile_path = REPO_ROOT / "data" / "profile.json"
    with open(profile_path, "r", encoding="utf-8") as f:
        profile = json.load(f)
    assert profile == {"is_onboarded": False}, "Genesis profile modified!"

    res = subprocess.run(["git", "diff", "--name-only", "src/core/"], cwd=REPO_ROOT, capture_output=True, text=True)
    assert res.stdout.strip() == "", f"Production code in src/core/ modified: {res.stdout}"
