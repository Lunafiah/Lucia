"""
tests/evaluation_phase22/test_h1_v14_preflight.py

Unit tests for the Phase 22 H1 Protocol v1.4 Mandatory 15-Point Preflight Harness.
Proves that H1V14PreflightValidator passes on the canonical v1.4 fixture and
strictly fails closed on any structural violation, variance defect, rank deficiency,
tampering, or invariant breach.
"""

from __future__ import annotations

import dataclasses
import json
from pathlib import Path
import subprocess
from typing import List
from unittest.mock import MagicMock, patch

import pytest

from tests.evaluation_phase22.fixtures.knowledge import EvaluationProposition
from tests.evaluation_phase22.fixtures.probes_h1_v14 import (
    H1V14Probe,
    build_v14_probes,
    MANIFEST_V14_PATH,
)
from tests.evaluation_phase22.scripts.validate_h1_v14_preflight import (
    H1V14PreflightValidator,
    PreflightSummary,
)


@pytest.fixture(scope="module")
def canonical_probes() -> List[H1V14Probe]:
    """Load canonical N=270 probes fixture."""
    return build_v14_probes(seed=42)


@pytest.fixture
def validator(canonical_probes: List[H1V14Probe]) -> H1V14PreflightValidator:
    """Instantiate validator on canonical probes and repo root."""
    repo_root = Path(__file__).resolve().parent.parent.parent
    return H1V14PreflightValidator(
        probes=list(canonical_probes),
        repo_root=repo_root,
        manifest_path=MANIFEST_V14_PATH,
    )


# =============================================================================
# 1. Positive Baseline: Canonical Fixture Passes 100%
# =============================================================================

def test_canonical_fixture_passes_all_15_checks(validator: H1V14PreflightValidator) -> None:
    """Canonical N=270 fixture must pass all 15 checks with zero failures."""
    summary: PreflightSummary = validator.run_all_checks()
    assert summary.all_passed is True
    assert summary.passed_checks == 15
    assert summary.failed_checks == 0
    assert len(summary.results) == 15
    for chk in summary.results:
        assert chk.passed is True, f"Check {chk.check_id} ({chk.name}) unexpectedly failed: {chk.details}"


# =============================================================================
# 2. Structural Failure Tests (Fails Closed)
# =============================================================================

def test_n_not_270_fails(canonical_probes: List[H1V14Probe], validator: H1V14PreflightValidator) -> None:
    """Sample size N != 270 must trigger failure in Check 1 and Check 7."""
    truncated = list(canonical_probes[:-1])  # N = 269
    val = H1V14PreflightValidator(probes=truncated, repo_root=validator.repo_root, manifest_path=validator.manifest_path)

    res1 = val.check_1_sample_size()
    assert res1.passed is False
    assert "Observed N = 269" in res1.details

    res7 = val.check_7_design_matrix()
    assert res7.passed is False


def test_duplicate_probe_id_fails(canonical_probes: List[H1V14Probe], validator: H1V14PreflightValidator) -> None:
    """Duplicate probe IDs must trigger failure in Check 5."""
    bad_probes = list(canonical_probes)
    bad_probes[1] = dataclasses.replace(bad_probes[1], probe_id=bad_probes[0].probe_id)
    val = H1V14PreflightValidator(probes=bad_probes, repo_root=validator.repo_root, manifest_path=validator.manifest_path)

    res = val.check_5_probe_id_uniqueness()
    assert res.passed is False
    assert "Observed 269 unique IDs" in res.details


def test_duplicate_stimulus_text_fails(canonical_probes: List[H1V14Probe], validator: H1V14PreflightValidator) -> None:
    """Duplicate stimulus text must trigger failure in Check 6."""
    bad_probes = list(canonical_probes)
    bad_probes[1] = dataclasses.replace(bad_probes[1], stimulus_text=bad_probes[0].stimulus_text)
    val = H1V14PreflightValidator(probes=bad_probes, repo_root=validator.repo_root, manifest_path=validator.manifest_path)

    res = val.check_6_stimulus_text_uniqueness()
    assert res.passed is False
    assert "Observed 269 unique stimulus texts" in res.details


def test_incorrect_cell_allocation_fails(canonical_probes: List[H1V14Probe], validator: H1V14PreflightValidator) -> None:
    """Cell counts not equal to 30 must trigger failure in Check 3."""
    bad_probes = list(canonical_probes)
    # Move one probe from cell 1 to cell 2
    bad_probes[0] = dataclasses.replace(bad_probes[0], cell_id=2)
    val = H1V14PreflightValidator(probes=bad_probes, repo_root=validator.repo_root, manifest_path=validator.manifest_path)

    res = val.check_3_cell_allocation()
    assert res.passed is False
    assert "Required: 30 per cell" in res.details


def test_incorrect_exposure_balance_fails(canonical_probes: List[H1V14Probe], validator: H1V14PreflightValidator) -> None:
    """Distorted T allocation within cell (not 10/10/10) must trigger failure in Check 4."""
    bad_probes = list(canonical_probes)
    # Find a T=1 probe in cell 1, change to T=4
    for i, p in enumerate(bad_probes):
        if p.cell_id == 1 and p.exposure_ticks == 1:
            bad_probes[i] = dataclasses.replace(p, exposure_ticks=4)
            break
    val = H1V14PreflightValidator(probes=bad_probes, repo_root=validator.repo_root, manifest_path=validator.manifest_path)

    res = val.check_4_exposure_balance()
    assert res.passed is False
    assert "Imbalanced cells detected" in res.details


# =============================================================================
# 3. Mathematical & Variance Gate Failure Tests
# =============================================================================

def test_rank_deficiency_fails(canonical_probes: List[H1V14Probe], validator: H1V14PreflightValidator) -> None:
    """Collinear S and U factors causing rank < 11 must trigger failure in Check 7."""
    # Force U_target to equal S_target across all probes (collinear)
    bad_probes = [dataclasses.replace(p, u_target=p.s_target) for p in canonical_probes]
    val = H1V14PreflightValidator(probes=bad_probes, repo_root=validator.repo_root, manifest_path=validator.manifest_path)

    res = val.check_7_design_matrix()
    assert res.passed is False
    assert res.diagnostics["rank"] < 11


def test_u_variance_below_floor_fails(canonical_probes: List[H1V14Probe], validator: H1V14PreflightValidator) -> None:
    """Any cell with Var(U) < 0.0020 must trigger failure in Check 8."""
    # Create constant-entropy propositions for Cell 1 probes
    const_prop = (
        EvaluationProposition("prop_01", "entity", "state", "nominal", confidence=0.95, is_verified=True, is_contradicted=False),
    )
    bad_probes = [
        dataclasses.replace(p, propositions=const_prop) if p.cell_id == 1 else p
        for p in canonical_probes
    ]
    val = H1V14PreflightValidator(probes=bad_probes, repo_root=validator.repo_root, manifest_path=validator.manifest_path)

    res = val.check_8_actual_u_variance()
    assert res.passed is False
    assert "Failed variance floor in cells" in res.details


def test_gate3_separation_below_threshold_fails(canonical_probes: List[H1V14Probe], validator: H1V14PreflightValidator) -> None:
    """Delta_ML or Delta_HM < 0.2500 must trigger failure in Check 9."""
    # Artificially compress Med U tier propositions to have high confidence (low entropy ~ 0.28, close to Low tier)
    compressed_prop = (
        EvaluationProposition("prop_01", "entity", "state", "nominal", confidence=0.95, is_verified=True, is_contradicted=False),
    )
    bad_probes = [
        dataclasses.replace(p, propositions=compressed_prop) if p.u_target == "Med" else p
        for p in canonical_probes
    ]
    val = H1V14PreflightValidator(probes=bad_probes, repo_root=validator.repo_root, manifest_path=validator.manifest_path)

    res = val.check_9_actual_u_separation()
    assert res.passed is False
    assert "Delta_ML" in res.details


def test_missing_t12_probes_fails(canonical_probes: List[H1V14Probe], validator: H1V14PreflightValidator) -> None:
    """Missing T=12 probes in any cell must trigger failure in Check 10."""
    bad_probes = [
        dataclasses.replace(p, exposure_ticks=4) if (p.cell_id == 1 and p.exposure_ticks == 12) else p
        for p in canonical_probes
    ]
    val = H1V14PreflightValidator(probes=bad_probes, repo_root=validator.repo_root, manifest_path=validator.manifest_path)

    res = val.check_10_gate2_t12_structure()
    assert res.passed is False


def test_vocabulary_tier_mismatch_fails(canonical_probes: List[H1V14Probe], validator: H1V14PreflightValidator) -> None:
    """Stimulus text drawn from the wrong S tier must trigger failure in Check 10."""
    bad_probes = list(canonical_probes)
    # Find a High S probe and give it Low S text
    for i, p in enumerate(bad_probes):
        if p.s_target == "High":
            bad_probes[i] = dataclasses.replace(p, stimulus_text="system system telemetry telemetry check check status status code 1.")
            break
    val = H1V14PreflightValidator(probes=bad_probes, repo_root=validator.repo_root, manifest_path=validator.manifest_path)

    res = val.check_10_gate2_t12_structure()
    assert res.passed is False
    assert "invalid_mappings" in res.details


# =============================================================================
# 4. Anti-Cherry-Picking & Manifest Integrity Tests
# =============================================================================

def test_anti_cherry_picking_violation_fails(canonical_probes: List[H1V14Probe], validator: H1V14PreflightValidator) -> None:
    """Arbitrary/cherry-picked probe IDs not matching deterministic prefix must fail Check 11."""
    bad_probes = [
        dataclasses.replace(p, probe_id=f"cherry_picked_id_{i}")
        for i, p in enumerate(canonical_probes)
    ]
    val = H1V14PreflightValidator(probes=bad_probes, repo_root=validator.repo_root, manifest_path=validator.manifest_path)

    res = val.check_11_anti_cherry_picking()
    assert res.passed is False
    assert "Non-deterministic or cherry-picked markers" in res.details


def test_manifest_tampering_fails(tmp_path: Path, canonical_probes: List[H1V14Probe], validator: H1V14PreflightValidator) -> None:
    """Tampered manifest SHA-256 or altered records must trigger failure in Check 12."""
    tampered_manifest_file = tmp_path / "manifest_tampered.json"
    with open(validator.manifest_path, "r", encoding="utf-8") as f:
        data = json.load(f)

    # Invalidate SHA-256
    data["canonical_payload_sha256"] = "0" * 64
    with open(tampered_manifest_file, "w", encoding="utf-8") as f:
        json.dump(data, f)

    val = H1V14PreflightValidator(probes=list(canonical_probes), repo_root=validator.repo_root, manifest_path=tampered_manifest_file)
    res = val.check_12_frozen_manifest()
    assert res.passed is False
    assert "Manifest mismatch" in res.details


def test_missing_manifest_file_fails(tmp_path: Path, canonical_probes: List[H1V14Probe], validator: H1V14PreflightValidator) -> None:
    """Missing manifest file must fail Check 12."""
    non_existent = tmp_path / "does_not_exist.json"
    val = H1V14PreflightValidator(probes=list(canonical_probes), repo_root=validator.repo_root, manifest_path=non_existent)
    res = val.check_12_frozen_manifest()
    assert res.passed is False
    assert "Manifest file not found" in res.details


# =============================================================================
# 5. Runtime Governance & Invariant Tests (Genesis Gate & src/core Cleanliness)
# =============================================================================

def test_genesis_mutation_fails(tmp_path: Path, canonical_probes: List[H1V14Probe]) -> None:
    """Violating Genesis onboarding status (is_onboarded: true) must trigger failure in Check 14."""
    mock_repo = tmp_path / "mock_repo"
    data_dir = mock_repo / "data"
    data_dir.mkdir(parents=True)
    profile_file = data_dir / "profile.json"
    with open(profile_file, "w", encoding="utf-8") as f:
        json.dump({"is_onboarded": True, "notes": "TAMPERED"}, f)

    val = H1V14PreflightValidator(probes=list(canonical_probes), repo_root=mock_repo, manifest_path=MANIFEST_V14_PATH)
    res = val.check_14_genesis_gate_invariant()
    assert res.passed is False
    assert "CRITICAL: Genesis profile violated" in res.details


def test_production_tree_mutation_fails(canonical_probes: List[H1V14Probe], validator: H1V14PreflightValidator) -> None:
    """Uncommitted changes detected in src/core/** must trigger failure in Check 15."""
    with patch("subprocess.run") as mock_run:
        mock_res = MagicMock()
        mock_res.stdout = " M src/core/emotion/emotion_core.py\n"
        mock_run.return_value = mock_res

        res = validator.check_15_production_code_invariant()
        assert res.passed is False
        assert "CRITICAL: Modifications detected in src/core/" in res.details
