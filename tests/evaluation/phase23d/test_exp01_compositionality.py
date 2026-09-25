"""
Phase 23-D — EXP-01: Compositionality & Recursion Test Suite
Automated regression tests verifying the structural path reconstruction,
role binding preservation, negation scoping, and adversarial invariance
of UMR-TPG, V-UMR, and DRS-Graph across recursion depths D in {1, 2, 3, 4}.
"""
import os
import json
import pytest
from evaluation.evaluation_phase23d.experiment_01_compositionality.dataset.generator import (
    generate_corpus,
)
from evaluation.evaluation_phase23d.experiment_01_compositionality.run_experiment import (
    run_evaluation,
    UMRTPGGraph,
    VUMRGraph,
    DRSGraph,
    PureHDCSuperposition,
    HDCCodebook,
)


@pytest.fixture(scope="module")
def deterministic_corpus(tmp_path_factory):
    corpus_dir = tmp_path_factory.mktemp("exp01_data")
    corpus_file = os.path.join(corpus_dir, "corpus.json")
    data = generate_corpus(seed=42)
    with open(corpus_file, "w", encoding="utf-8") as f:
        json.dump(data, f)
    return corpus_file


def test_exp01_dataset_integrity(deterministic_corpus):
    """Verifies that the generated corpus contains all 24 scenarios across depths 1..4 and 6 suites."""
    with open(deterministic_corpus, "r", encoding="utf-8") as f:
        data = json.load(f)

    assert len(data["scenarios"]) == 24
    depths = {s["depth"] for s in data["scenarios"]}
    assert depths == {1, 2, 3, 4}

    suites = {s["suite"] for s in data["scenarios"]}
    expected_suites = {
        "simple_role_binding",
        "nested_proposition",
        "nested_with_role_binding",
        "negated_proposition",
        "nested_negation_scope",
        "adversarial_role_swap",
    }
    assert suites == expected_suites


def test_exp01_umr_tpg_compositionality_gates(deterministic_corpus):
    """Verifies that UMR-TPG satisfies all preregistered falsification gates at D=4."""
    eval_results = run_evaluation(deterministic_corpus, seed=42)
    umr = eval_results["candidates"]["UMR-TPG"]

    assert umr["verdict"] == "PASS"
    assert umr["SPRR_by_depth"]["D=4"] >= 0.95
    assert umr["SPRR_overall"] == 1.000
    assert umr["BER"] <= 0.02
    assert umr["SPR"] >= 0.98
    assert umr["CTR"] == 0.000
    assert umr["RSA"] == 1.000


def test_exp01_v_umr_compositionality_gates(deterministic_corpus):
    """Verifies that V-UMR preserves structural topological paths and zero cross-talk."""
    eval_results = run_evaluation(deterministic_corpus, seed=42)
    vumr = eval_results["candidates"]["V-UMR"]

    assert vumr["verdict"] == "PASS"
    assert vumr["SPRR_by_depth"]["D=4"] >= 0.95
    assert vumr["BER"] <= 0.02
    assert vumr["SPR"] >= 0.98
    assert vumr["CTR"] == 0.000


def test_exp01_drs_graph_compositionality_gates(deterministic_corpus):
    """Verifies that DRS-Graph control preserves scoping, universe separation, and paths."""
    eval_results = run_evaluation(deterministic_corpus, seed=42)
    drs = eval_results["candidates"]["DRS-Graph"]

    assert drs["verdict"] == "PASS"
    assert drs["SPRR_by_depth"]["D=4"] >= 0.95
    assert drs["BER"] <= 0.02
    assert drs["SPR"] == 1.000
    assert drs["CTR"] == 0.000


def test_exp01_hdc_pure_baseline_collapse(deterministic_corpus):
    """Confirms that HDC-Pure collapses under nested recursion without a graph backbone."""
    eval_results = run_evaluation(deterministic_corpus, seed=42)
    hdc = eval_results["candidates"]["HDC-Pure"]

    assert hdc["verdict"] == "FAIL"
    # Pure superposition without graph unbinding fails nested path reconstruction
    assert hdc["SPRR_by_depth"]["D=4"] < 0.50
    assert hdc["BER"] > 0.02


def test_exp01_adversarial_role_swap_invariance():
    """Explicitly tests that ARG0(A) -> ARG1(B) is never inverted to ARG0(B) -> ARG1(A) after nesting."""
    tpg = UMRTPGGraph()
    # Scenario: User (ARG0) helps Lucia (ARG1) inside nested belief
    scenario = {
        "depth": 2,
        "events": [
            {
                "id": "e1",
                "predicate": "BELIEVE_01",
                "roles": {":ARG0": "ent_admin"},
                "sub_event": "e2",
                "negated": False,
            },
            {
                "id": "e2",
                "predicate": "HELP_01",
                "roles": {":ARG0": "ent_user", ":ARG1": "ent_lucia"},
                "sub_event": None,
                "negated": False,
            },
        ],
    }
    tpg.ingest_scenario(scenario)

    # Verify exact roles in nested event
    assert tpg.query_binding("e2", ":ARG0") == "ent_user"
    assert tpg.query_binding("e2", ":ARG1") == "ent_lucia"

    # Verify path from e1 to e2's ARG0
    assert tpg.query_path("e1", [":sub-event", ":ARG0"]) == "ent_user"
    assert tpg.query_path("e1", [":sub-event", ":ARG1"]) == "ent_lucia"

    # Reversing query must NOT match
    assert tpg.query_path("e1", [":sub-event", ":ARG0"]) != "ent_lucia"


def test_exp01_reproducibility(deterministic_corpus):
    """Verifies that two consecutive runs produce 100% bit-exact metric outputs."""
    run1 = run_evaluation(deterministic_corpus, seed=42)
    run2 = run_evaluation(deterministic_corpus, seed=42)

    for cand in ["UMR-TPG", "V-UMR", "DRS-Graph", "HDC-Pure"]:
        assert run1["candidates"][cand]["SPRR_overall"] == run2["candidates"][cand]["SPRR_overall"]
        assert run1["candidates"][cand]["BER"] == run2["candidates"][cand]["BER"]
        assert run1["candidates"][cand]["SPR"] == run2["candidates"][cand]["SPR"]
        assert run1["candidates"][cand]["CTR"] == run2["candidates"][cand]["CTR"]
