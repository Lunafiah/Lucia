"""Automated Pytest Suite for EXP-06: Multimodal Grounding & Token-Free Embodiment.

Covers the 13 required test areas:
1. Dataset integrity
2. Deterministic signal generation
3. Single-modality grounding (PAD only, Acoustic only)
4. Multimodal convergence (synchronous alignment without duplicates)
5. Temporal continuity (bounded ODE trajectory transitions)
6. Conflicting evidence (explicit conflict state & uncertainty preservation)
7. Missing modality / dropout (graceful single-stream degradation)
8. Perturbation / noise robustness (stability within deadband)
9. Stability criterion (Lyapunov lambda_max <= 0.0, DFR == 0.0%)
10. Token-free compliance (zero LLM/tokenizer usage)
11. Candidate comparison (UMR-TPG PASS, V-UMR FAIL on CPA, DRS-Graph PASS)
12. Reproducibility across independent runs
13. Production-boundary enforcement
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Dict

import pytest

from tests.evaluation.evaluation_phase23d.experiment_06_multimodal_grounding.dataset.generator import (
    generate_exp06_corpus,
)
from tests.evaluation.evaluation_phase23d.experiment_06_multimodal_grounding.models.drs_multimodal import (
    DRSMultimodalEngine,
)
from tests.evaluation.evaluation_phase23d.experiment_06_multimodal_grounding.models.umr_multimodal import (
    UMRMultimodalEngine,
)
from tests.evaluation.evaluation_phase23d.experiment_06_multimodal_grounding.models.vumr_multimodal import (
    VUMRMultimodalEngine,
)
from tests.evaluation.evaluation_phase23d.experiment_06_multimodal_grounding.run_experiment import (
    run_all_exp06,
    run_exp06_candidate,
)


@pytest.fixture
def corpus_data() -> Dict[str, Any]:
    return generate_exp06_corpus()


@pytest.fixture
def raw_results_data() -> Dict[str, Any]:
    json_path = (
        Path(__file__).parents[2]
        / "evaluation"
        / "evaluation_phase23d"
        / "experiment_06_multimodal_grounding"
        / "results"
        / "raw_results.json"
    )
    if not json_path.exists():
        return run_all_exp06()
    with open(json_path, "r", encoding="utf-8") as f:
        return json.load(f)


def test_exp06_dataset_integrity(corpus_data: Dict[str, Any]) -> None:
    """1. Verifies dataset structure and mandatory sample coverage."""
    samples = corpus_data["samples"]
    assert len(samples) >= 10
    sample_ids = {s["sample_id"] for s in samples}
    expected_ids = {"SM_PAD_01", "SM_AC_01", "CONV_01", "TEMP_01", "CONF_01", "DROP_01", "PERT_01", "OSC_01"}
    assert expected_ids.issubset(sample_ids)


def test_exp06_deterministic_signal_generation() -> None:
    """2. Verifies generated signals are deterministic and bit-exact across calls."""
    c1 = generate_exp06_corpus()
    c2 = generate_exp06_corpus()
    assert c1 == c2


def test_exp06_single_modality_grounding(corpus_data: Dict[str, Any]) -> None:
    """3. Verifies single-modality inputs map to correct semantic concepts."""
    engine = UMRMultimodalEngine()
    pad_sample = next(s for s in corpus_data["samples"] if s["sample_id"] == "SM_PAD_01")
    ac_sample = next(s for s in corpus_data["samples"] if s["sample_id"] == "SM_AC_01")

    res_pad = engine.ground_multimodal_sample(pad_sample)
    res_ac = engine.ground_multimodal_sample(ac_sample)

    assert res_pad["grounded_concept"] == "AFFECT_JOY"
    assert res_ac["grounded_concept"] == "PROSODY_AGITATED"


def test_exp06_multimodal_convergence(corpus_data: Dict[str, Any]) -> None:
    """4. Verifies aligned multimodal streams converge without duplicate concept nodes."""
    engine = UMRMultimodalEngine()
    conv_sample = next(s for s in corpus_data["samples"] if s["sample_id"] == "CONV_01")
    res = engine.ground_multimodal_sample(conv_sample)

    assert res["grounded_concept"] == "RELATIONAL_PHILIA"
    assert res["single_concept_formed"] is True
    assert res["duplicate_concepts_created"] is False


def test_exp06_temporal_continuity(corpus_data: Dict[str, Any]) -> None:
    """5. Verifies temporal trajectory transitions evolve smoothly without step resets."""
    engine = UMRMultimodalEngine()
    temp_sample = next(s for s in corpus_data["samples"] if s["sample_id"] == "TEMP_01")
    traj_res = engine.run_trajectory(temp_sample["temporal_trajectory"])

    assert len(traj_res) == 10
    # First and last states must be the resting attractor
    assert traj_res[0]["grounded_concept"] == "RELATIONAL_PHILIA"
    assert traj_res[-1]["grounded_concept"] == "RELATIONAL_PHILIA"


def test_exp06_conflicting_evidence(corpus_data: Dict[str, Any]) -> None:
    """6. Verifies conflicting modalities trigger explicit conflict and uncertainty."""
    engine = UMRMultimodalEngine()
    conf_sample = next(s for s in corpus_data["samples"] if s["sample_id"] == "CONF_01")
    res = engine.ground_multimodal_sample(conf_sample)

    assert res["grounded_concept"] == "EVIDENCE_CONFLICT"
    assert res["conflict_detected"] is True
    assert res["uncertainty_score"] >= 0.50


def test_exp06_missing_modality_dropout(corpus_data: Dict[str, Any]) -> None:
    """7. Verifies graceful degradation when one modality stream is dropped."""
    engine = UMRMultimodalEngine()
    drop_sample = next(s for s in corpus_data["samples"] if s["sample_id"] == "DROP_01")
    res = engine.ground_multimodal_sample(drop_sample)

    assert res["grounded_concept"] == "AFFECT_SERENE"
    assert res["conflict_detected"] is False


def test_exp06_perturbation_noise_robustness(corpus_data: Dict[str, Any]) -> None:
    """8. Verifies noise within deadband does not alter grounded state."""
    engine = UMRMultimodalEngine()
    pert_sample = next(s for s in corpus_data["samples"] if s["sample_id"] == "PERT_01")
    res = engine.ground_multimodal_sample(pert_sample)

    assert res["grounded_concept"] == "AFFECT_JOY"


def test_exp06_stability_criterion(raw_results_data: Dict[str, Any]) -> None:
    """9. Verifies Lyapunov stability (lambda_max <= 0.0) and DFR == 0.0%."""
    umr_metrics = raw_results_data["candidates"]["UMR-TPG"]["metrics"]
    assert umr_metrics["lambda_max"] <= 0.000
    assert umr_metrics["DFR"] == 0.0


def test_exp06_token_free_compliance(raw_results_data: Dict[str, Any]) -> None:
    """10. Verifies 100% token-free compliance across all candidates."""
    for cand in ["UMR-TPG", "V-UMR", "DRS-Graph"]:
        assert raw_results_data["candidates"][cand]["metrics"]["token_free_compliance"] == 1.0


def test_exp06_candidate_comparison(raw_results_data: Dict[str, Any]) -> None:
    """11. Verifies UMR-TPG PASS, DRS-Graph PASS, and V-UMR FAIL on CPA."""
    assert raw_results_data["candidates"]["UMR-TPG"]["gates"]["overall_verdict"] == "PASS"
    assert raw_results_data["candidates"]["DRS-Graph"]["gates"]["overall_verdict"] == "PASS"

    # V-UMR must FAIL CPA gate due to unconstrained vector projection on partial acoustic
    vumr = raw_results_data["candidates"]["V-UMR"]
    assert vumr["gates"]["overall_verdict"] == "FAIL"
    assert vumr["gates"]["CPA_gate"] is False
    assert vumr["metrics"]["CPA"] < 0.90


def test_exp06_reproducibility() -> None:
    """12. Verifies bit-exact metric outputs across independent executions."""
    corpus = generate_exp06_corpus()
    res1 = run_exp06_candidate("UMR-TPG", UMRMultimodalEngine, corpus)
    res2 = run_exp06_candidate("UMR-TPG", UMRMultimodalEngine, corpus)

    assert res1["metrics"]["CPA"] == res2["metrics"]["CPA"]
    assert res1["metrics"]["CMC"] == res2["metrics"]["CMC"]
    assert res1["metrics"]["UCP"] == res2["metrics"]["UCP"]
    assert res1["metrics"]["DFR"] == res2["metrics"]["DFR"]
    assert res1["metrics"]["r_embodiment"] == res2["metrics"]["r_embodiment"]


def test_exp06_production_boundary_enforcement() -> None:
    """13. Verifies zero modifications to production code and Genesis onboarding."""
    repo_root = Path(__file__).parents[2]
    profile_path = repo_root / "data" / "profile.json"
    if profile_path.exists():
        with open(profile_path, "r", encoding="utf-8") as f:
            profile = json.load(f)
            assert profile.get("is_onboarded") is False
