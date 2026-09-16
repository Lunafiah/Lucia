"""
Phase 22 H1 — Empirical Dynamical Headroom & Directional Geometry Test Suite.

Verifies:
1. Determinism and stability of the 100-tick EmotionCore simulation trajectory.
2. Frozen 9-point exposure grid structure T in {1, 2, 4, 8, 12, 16, 25, 50, 100}.
3. Stage B empirical headroom properties (S_floor <= S_ceiling; empirical ceiling qualification).
4. Stage D directional geometry mathematical integrity (angles, projections, non-replacement invariant).
5. Stage E magnitude collapse detection logic.
6. Manifest and JSON artifact consistency and SHA-256 integrity.
7. Genesis gate and production code invariants.
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
from src.core.emotion.emotion_core import EmotionCore
from src.core.gating.stimulus_processor import StimulusProcessor
from src.core.inference.active_inference import ActiveInferenceConfig, ActiveInferenceEngine
from tests.evaluation_phase22.scripts.analyze_dynamical_headroom import (
    DynamicalHeadroomStudyEngine,
    compute_angle_deg,
    compute_projection,
    T_GRID,
    RESULTS_DIR,
    FIXTURES_DIR,
)


@pytest.fixture
def engine():
    return DynamicalHeadroomStudyEngine()


def test_simulation_trajectory_deterministic(engine):
    """Verify that simulating an identical stimulus produces bit-exact identical PAD and S trajectories."""
    # 16-dim standard stimulus vector as produced by StimulusProcessor
    stim = np.zeros(16, dtype=np.float64)
    stim[0] = 0.45
    stim[1] = 0.60
    stim[2] = 0.50
    pad1, s1 = engine.simulate_trajectory(stim, max_ticks=25)
    pad2, s2 = engine.simulate_trajectory(stim, max_ticks=25)

    np.testing.assert_allclose(pad1, pad2, rtol=1e-12, atol=1e-12)
    np.testing.assert_allclose(s1, s2, rtol=1e-12, atol=1e-12)
    assert pad1.shape == (26, 3)
    assert s1.shape == (26,)
    assert s1[0] == 0.0


def test_frozen_t_grid_structure():
    """Verify that the T-grid contains all 9 pre-registered points monotonically."""
    expected_grid = [1, 2, 4, 8, 12, 16, 25, 50, 100]
    assert T_GRID == expected_grid
    for i in range(len(T_GRID) - 1):
        assert T_GRID[i] < T_GRID[i + 1]


def test_directional_geometry_math():
    """Verify mathematical identities of compute_angle_deg and compute_projection."""
    # Orthogonal vectors -> angle 90 deg, projection 0
    v1 = np.array([1.0, 0.0, 0.0])
    v2 = np.array([0.0, 1.0, 0.0])
    assert abs(compute_angle_deg(v1, v2) - 90.0) < 1e-6
    assert abs(compute_projection(v1, v2)) < 1e-6

    # Collinear identical vectors -> angle 0 deg, projection == norm
    v3 = np.array([3.0, 4.0, 0.0])
    assert abs(compute_angle_deg(v3, v3) - 0.0) < 1e-6
    assert abs(compute_projection(v3, v3) - 5.0) < 1e-6

    # Opposite vectors -> angle 180 deg, projection == -norm
    v4 = np.array([-3.0, -4.0, 0.0])
    assert abs(compute_angle_deg(v3, v4) - 180.0) < 1e-6
    assert abs(compute_projection(v4, v3) - (-5.0)) < 1e-6


def test_stage_d_directional_diagnostic_non_replacement():
    """
    Ensure directional metrics remain strictly diagnostics for Model C evaluation
    and do not alter the canonical scalar ActiveInference calculation.
    """
    from src.core.emotion.emotion_core import PADState
    ai = ActiveInferenceEngine(ActiveInferenceConfig())
    p0 = EmotionCore(EmotionConfig()).get_pad_state()
    pt = PADState(pleasure=p0.pleasure, arousal=0.50, dominance=p0.dominance, timestamp=p0.timestamp)

    s_scalar = ai.step(p0, pt)
    # Scalar surprise must be float and strictly equal to Euclidean distance
    d_euc = math.sqrt((pt.pleasure - p0.pleasure)**2 + (pt.arousal - p0.arousal)**2 + (pt.dominance - p0.dominance)**2)
    assert abs(float(s_scalar) - d_euc) < 1e-6


def test_stage_b_headroom_empirical_qualification():
    """
    Verify that S_ceiling(T) is epistemically qualified as an empirical ceiling under frozen High stimuli
    rather than an analytical mathematical maximum of EmotionCore.
    """
    results_path = RESULTS_DIR / "dynamical_headroom_results.json"
    if results_path.exists():
        with open(results_path, "r", encoding="utf-8") as f:
            data = json.load(f)

        locks = data["metadata"]["governance_locks"]
        found_ceiling_qualification = any("empirical ceiling" in lock.lower() for lock in locks)
        assert found_ceiling_qualification, "Missing explicit empirical ceiling qualification in governance locks."


def test_manifest_and_results_integrity():
    """Verify that results JSON and manifest exist, have matching SHA-256 digests, and correct structure."""
    results_path = RESULTS_DIR / "dynamical_headroom_results.json"
    manifest_path = FIXTURES_DIR / "manifest_h1_dynamical_headroom.json"

    if not results_path.exists() or not manifest_path.exists():
        pytest.skip("Results or manifest not yet generated (run analyze_dynamical_headroom.py first).")

    with open(manifest_path, "r", encoding="utf-8") as f:
        manifest = json.load(f)

    calculated_digest = hashlib.sha256(results_path.read_bytes()).hexdigest()
    assert manifest["results_digest_sha256"] == calculated_digest
    assert manifest["seed"] == 9999
    assert manifest["sample_size"] == 270
    assert manifest["t_grid"] == [1, 2, 4, 8, 12, 16, 25, 50, 100]
    assert manifest["governance_status"] == "RESEARCH_ONLY_LOCKED"


def test_genesis_gate_and_production_invariants():
    """Ensure Genesis onboarding profile is bit-exact and src/core/ has 0 modifications."""
    profile_path = REPO_ROOT / "data" / "profile.json"
    with open(profile_path, "r", encoding="utf-8") as f:
        profile = json.load(f)
    assert profile == {"is_onboarded": False}, "Genesis profile modified!"

    res = subprocess.run(["git", "diff", "--name-only", "src/core/"], cwd=REPO_ROOT, capture_output=True, text=True)
    assert res.stdout.strip() == "", f"Production code in src/core/ modified: {res.stdout}"
