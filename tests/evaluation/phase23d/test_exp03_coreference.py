"""
Phase 23-D — EXP-03: Reference Resolution & Zero-Anaphora Test Suite
Automated regression tests verifying entity persistence, CEAF-e, B-cubed,
zero-anaphora non-hallucination, Vietnamese kinship perspective tracking,
and representation vs resolution attribution.
"""
import os
import json
import pytest
from tests.evaluation.evaluation_phase23d.experiment_03_coreference.run_experiment import (
    run_exp03_evaluation,
)
from tests.evaluation.evaluation_phase23d.experiment_03_coreference.models.umr_coreference import (
    UMRCoreferenceSubstrate,
)


@pytest.fixture(scope="module")
def corpus_path():
    base_dir = os.path.dirname(__file__)
    return os.path.join(
        base_dir,
        "..",
        "evaluation_phase23d",
        "experiment_03_coreference",
        "dataset",
        "corpus.json",
    )


def test_exp03_dataset_integrity(corpus_path):
    """Verifies that the coreference corpus contains 10 scenarios covering all specified phenomena."""
    with open(corpus_path, "r", encoding="utf-8") as f:
        data = json.load(f)

    assert len(data["scenarios"]) == 10
    phenomena = {s["phenomenon"] for s in data["scenarios"]}
    expected_phenomena = {
        "english_overt_pronoun",
        "japanese_omitted_subject",
        "japanese_omitted_object",
        "japanese_unresolved_zero",
        "vietnamese_kinship_persistent",
        "vietnamese_perspective_shift",
        "long_reference_chain",
        "competing_antecedents",
        "ambiguous_antecedent",
        "multi_event_persistence",
    }
    assert phenomena == expected_phenomena


def test_exp03_representation_gates(corpus_path):
    """Verifies that under Representation Mode, all candidates achieve CEAF_e_F1 >= 0.82 and EPR >= 0.95."""
    res = run_exp03_evaluation(corpus_path)
    rep_res = res["representation_capability"]

    for cand in ["UMR-TPG", "V-UMR", "DRS-Graph"]:
        d = rep_res[cand]
        assert d["verdict"] == "PASS"
        assert d["CEAF_e_F1"] >= 0.82
        assert d["B3_F1"] >= 0.85
        assert d["EPR"] >= 0.95
        assert d["URP"] >= 0.90
        assert d["RSA"] == 1.0


def test_exp03_resolution_gates(corpus_path):
    """Verifies that under Resolution Mode, all candidates satisfy the evaluation gates on controlled cases."""
    res = run_exp03_evaluation(corpus_path)
    res_res = res["resolution_capability"]

    for cand in ["UMR-TPG", "V-UMR", "DRS-Graph"]:
        d = res_res[cand]
        assert d["verdict"] == "PASS"
        assert d["CEAF_e_F1"] >= 0.82
        assert d["B3_F1"] >= 0.85
        assert d["EPR"] >= 0.95
        assert d["URP"] >= 0.90


def test_exp03_japanese_zero_anaphora_no_hallucination(corpus_path):
    """Verifies that Japanese pro-drop without context evidence yields UNKNOWN_ENTITY and zero hallucination."""
    with open(corpus_path, "r", encoding="utf-8") as f:
        data = json.load(f)

    scen_04 = next(s for s in data["scenarios"] if s["id"] == "C04")
    sub = UMRCoreferenceSubstrate()
    pred = sub.run_resolution_mode(scen_04)

    assert "UNKNOWN_ENTITY" in pred
    assert "m1" in pred["UNKNOWN_ENTITY"]
    assert "ent_lucia" not in pred
    assert "ent_user" not in pred


def test_exp03_vietnamese_perspective_no_spurious_merger(corpus_path):
    """Verifies that different speakers using the honorific 'em' are not merged into a single cluster."""
    with open(corpus_path, "r", encoding="utf-8") as f:
        data = json.load(f)

    scen_06 = next(s for s in data["scenarios"] if s["id"] == "C06")
    sub = UMRCoreferenceSubstrate()
    pred = sub.run_resolution_mode(scen_06)

    # Lucia is m1, Admin is m4. They must NOT be in the same cluster!
    cluster_lucia = None
    cluster_admin = None
    for cid, m_list in pred.items():
        if "m1" in m_list:
            cluster_lucia = cid
        if "m4" in m_list:
            cluster_admin = cid

    assert cluster_lucia is not None
    assert cluster_admin is not None
    assert cluster_lucia != cluster_admin, "Spurious merger detected between distinct entities using honorific 'em'!"


def test_exp03_ambiguity_preserved(corpus_path):
    """Verifies that ambiguous pronouns without sufficient evidence are retained as AMBIGUOUS_UNRESOLVED."""
    with open(corpus_path, "r", encoding="utf-8") as f:
        data = json.load(f)

    scen_09 = next(s for s in data["scenarios"] if s["id"] == "C09")
    sub = UMRCoreferenceSubstrate()
    pred = sub.run_resolution_mode(scen_09)

    assert "AMBIGUOUS_UNRESOLVED" in pred
    assert "m3" in pred["AMBIGUOUS_UNRESOLVED"]


def test_exp03_reproducibility(corpus_path):
    """Verifies that two consecutive runs produce 100% bit-exact outputs."""
    run1 = run_exp03_evaluation(corpus_path)
    run2 = run_exp03_evaluation(corpus_path)

    assert run1["representation_capability"] == run2["representation_capability"]
    assert run1["resolution_capability"] == run2["resolution_capability"]
