"""
Unit and Property Tests for Phase 22 H1 Independent Stimulus Calibration Study.

Verifies:
1. Deterministic text generation across seeds.
2. Value bounds and clipping guarantees [-1, 1].
3. Locked reference vector angular separation formula.
4. Manifest integrity and SHA-256 payload digests.
5. Domain balance in calibrated generators.
6. Preservation of historical benchmarks and Genesis profile.
"""

import hashlib
import json
from pathlib import Path
import numpy as np
import pytest

from src.core.config import StimulusConfig
from src.core.gating.stimulus_processor import StimulusProcessor
from tests.evaluation_phase22.scripts.calibrate_stimulus_representation import (
    GeneratorG0,
    GeneratorG1,
    GeneratorG2,
    GeneratorG3,
    compute_locked_angular_separation,
    DOMAINS,
)

REPO_ROOT = Path(__file__).resolve().parent.parent.parent
RESULTS_DIR = REPO_ROOT / "tests" / "evaluation_phase22" / "results" / "h1_stimulus_calibration"
FIXTURES_DIR = REPO_ROOT / "tests" / "evaluation_phase22" / "fixtures"


@pytest.fixture
def sp():
    return StimulusProcessor(StimulusConfig())


def test_generators_deterministic_reproducibility(sp):
    """Verify that identical seeds produce bit-exact identical texts and vectors."""
    for GenClass in [GeneratorG0, GeneratorG1, GeneratorG2, GeneratorG3]:
        gen = GenClass(sp)
        rng1 = np.random.default_rng(42)
        rng2 = np.random.default_rng(42)

        for tier in ["Low", "Med", "High"]:
            txt1, dom1 = gen.generate_text(tier, rng1, 1)
            txt2, dom2 = gen.generate_text(tier, rng2, 1)
            assert txt1 == txt2
            assert dom1 == dom2

            v1 = sp.encode(txt1)[:3]
            v2 = sp.encode(txt2)[:3]
            np.testing.assert_array_equal(v1, v2)


def test_generator_output_bounds(sp):
    """Verify all generator outputs satisfy [-1, 1] clipping and finite values."""
    for GenClass in [GeneratorG1, GeneratorG2, GeneratorG3]:
        gen = GenClass(sp)
        rng = np.random.default_rng(123)

        for tier in ["Low", "Med", "High"]:
            for i in range(20):
                txt, _ = gen.generate_text(tier, rng, i + 1)
                vec = sp.encode(txt)
                assert np.all(vec >= -1.0)
                assert np.all(vec <= 1.0)
                assert np.all(np.isfinite(vec))
                # Non-zero floor on dims 0..2
                for d in range(3):
                    assert abs(vec[d]) >= 1e-7


def test_locked_angular_separation_formula():
    """Verify that angular separation uses v_i = mu_i - mu_L and computes exact angle."""
    mu_L = np.array([0.0, 0.0, 1.0])
    mu_M = np.array([0.5, 0.0, 1.0])  # v_M = [0.5, 0.0, 0.0]
    mu_H = np.array([0.0, 0.5, 1.0])  # v_H = [0.0, 0.5, 0.0]

    res = compute_locked_angular_separation(mu_L, mu_M, mu_H)
    np.testing.assert_allclose(res["v_M"], [0.5, 0.0, 0.0])
    np.testing.assert_allclose(res["v_H"], [0.0, 0.5, 0.0])
    assert abs(res["angle_deg"] - 90.0) < 1e-6
    assert abs(res["cos_theta"] - 0.0) < 1e-6


def test_domain_balance_in_generators(sp):
    """Verify that G1, G2, G3 sample domains uniformly."""
    for GenClass in [GeneratorG1, GeneratorG2, GeneratorG3]:
        gen = GenClass(sp)
        rng = np.random.default_rng(777)
        counts = {d: 0 for d in DOMAINS}
        N = 400

        for i in range(N):
            _, dom = gen.generate_text("Med", rng, i + 1)
            counts[dom] += 1

        # Each domain should receive roughly 25% (>= 60 out of 400)
        for d in DOMAINS:
            assert counts[d] >= 60, f"Domain {d} underrepresented in {GenClass.__name__}: {counts[d]}"


def test_manifest_and_results_integrity():
    """Verify that calibration results and manifest exist and have matching SHA-256 hashes."""
    results_path = RESULTS_DIR / "calibration_results.json"
    manifest_path = FIXTURES_DIR / "manifest_h1_stimulus_calibration.json"

    assert results_path.exists(), "calibration_results.json missing"
    assert manifest_path.exists(), "manifest_h1_stimulus_calibration.json missing"

    results_data = json.loads(results_path.read_text(encoding="utf-8"))
    manifest_data = json.loads(manifest_path.read_text(encoding="utf-8"))

    expected_hash = hashlib.sha256(results_path.read_bytes()).hexdigest()
    assert manifest_data["results_digest_sha256"] == expected_hash

    # Ensure all 4 candidates are present in results
    assert "G0" in results_data["candidates"]
    assert "G1" in results_data["candidates"]
    assert "G2" in results_data["candidates"]
    assert "G3" in results_data["candidates"]


def test_genesis_and_historical_preservation():
    """Verify Genesis profile is bit-exact and historical benchmark data is intact."""
    genesis_path = REPO_ROOT / "data" / "profile.json"
    assert genesis_path.exists()
    assert json.loads(genesis_path.read_text(encoding="utf-8")) == {"is_onboarded": False}

    # Verify historical Path C and v1.4 data files exist
    path_c = REPO_ROOT / "tests" / "evaluation_phase22" / "results" / "phase22_h1_path_c_matrix.json"
    assert path_c.exists()
    v14_manifest = REPO_ROOT / "tests" / "evaluation_phase22" / "fixtures" / "manifest_h1_v14.json"
    assert v14_manifest.exists()
