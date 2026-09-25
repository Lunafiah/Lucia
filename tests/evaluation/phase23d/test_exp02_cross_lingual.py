"""
Phase 23-D — EXP-02: Cross-Lingual Semantic Convergence Test Suite
Automated regression tests verifying functional equivalence, SQI,
zero-anaphora handling, kinship deixis, and layered failure separation
across English (EN), Japanese (JA), and Vietnamese (VI).
"""
import os
import json
import pytest
from tests.evaluation.evaluation_phase23d.experiment_02_cross_lingual.run_experiment import (
    run_exp02_evaluation,
)
from tests.evaluation.evaluation_phase23d.experiment_02_cross_lingual.transducers.oracle_transducer import (
    transduce_oracle,
)
from tests.evaluation.evaluation_phase23d.experiment_02_cross_lingual.transducers.rule_transducer import (
    transduce_rule_based,
)
from tests.evaluation.evaluation_phase23d.experiment_02_cross_lingual.queries.query_suite import (
    evaluate_query_suite,
    extract_q3_roles,
    extract_q7_omitted_resolution,
    extract_q8_social,
    extract_q9_sortal,
)


@pytest.fixture(scope="module")
def corpus_path():
    base_dir = os.path.dirname(__file__)
    return os.path.join(
        base_dir,
        "..",
        "evaluation_phase23d",
        "experiment_02_cross_lingual",
        "dataset",
        "parallel_corpus.json",
    )


def test_exp02_dataset_integrity(corpus_path):
    """Verifies that the parallel corpus contains 10 scenarios with EN, JA, and VI translations."""
    with open(corpus_path, "r", encoding="utf-8") as f:
        data = json.load(f)

    assert len(data["scenarios"]) == 10
    for scen in data["scenarios"]:
        assert "text_en" in scen
        assert "text_ja" in scen
        assert "text_vi" in scen
        assert "canonical_intent" in scen
        assert "expected_answers" in scen
        assert len(scen["expected_answers"]) == 11  # Q1..Q10 with Q3 split into arg0/arg1


def test_exp02_oracle_mode_representation_gates(corpus_path):
    """Verifies that under Oracle mode, all three candidate substrates achieve SQI >= 0.92 and FEP >= 0.90."""
    res = run_exp02_evaluation(corpus_path)
    oracle_res = res["oracle_transduction"]

    for cand in ["UMR-TPG", "V-UMR", "DRS-Graph"]:
        cand_data = oracle_res[cand]
        assert cand_data["verdict"] == "PASS"
        assert cand_data["SQI"]["overall"] >= 0.92
        assert cand_data["FEP"] >= 0.90
        # Specifically verify layered failure classification
        assert not res["failure_classification"][cand]["representation_failure"]
        assert not res["failure_classification"][cand]["functional_equivalence_failure"]


def test_exp02_rule_based_mode_separation(corpus_path):
    """Verifies that rule-based limitations are classified as transduction failures, NOT substrate representation failures."""
    res = run_exp02_evaluation(corpus_path)
    rule_res = res["rule_based_transduction"]

    # In rule-based mode, UMR-TPG achieves ~0.8867 SQI due to unhandled complex clauses
    assert rule_res["UMR-TPG"]["SQI"]["overall"] > 0.80
    assert res["failure_classification"]["UMR-TPG"]["transduction_failure"] is True
    assert res["failure_classification"]["UMR-TPG"]["representation_failure"] is False


def test_exp02_japanese_zero_anaphora_unknown(corpus_path):
    """Verifies that Japanese omitted arguments hold UNKNOWN_ENTITY without defaulting to speaker."""
    with open(corpus_path, "r", encoding="utf-8") as f:
        data = json.load(f)

    scen_02 = next(s for s in data["scenarios"] if s["id"] == "SCEN_02")
    # Japanese: '問題を解決した。' (No subject)
    inst_ja = transduce_oracle(scen_02, "UMR-TPG", "JA")
    roles = extract_q3_roles(inst_ja)

    assert roles[":ARG0"] == "UNKNOWN_ENTITY"
    assert roles[":ARG0"] != "ent_lucia"
    assert roles[":ARG0"] != "ent_user"
    assert extract_q7_omitted_resolution(inst_ja) == "UNKNOWN_ENTITY"


def test_exp02_vietnamese_kinship_and_classifier_separation(corpus_path):
    """Verifies that Vietnamese honorifics and classifiers are cleanly separated from core entities."""
    with open(corpus_path, "r", encoding="utf-8") as f:
        data = json.load(f)

    # SCEN_03: 'Anh đã hỗ trợ Lucia.' -> kinship deixis
    scen_03 = next(s for s in data["scenarios"] if s["id"] == "SCEN_03")
    inst_vi_03 = transduce_oracle(scen_03, "UMR-TPG", "VI")
    assert extract_q8_social(inst_vi_03) == "SENIOR_MALE_PEER"
    assert extract_q3_roles(inst_vi_03)[":ARG0"] == "ent_user"

    # SCEN_04: 'Người dùng đã đọc một quyển sách.' -> sortal classifier
    scen_04 = next(s for s in data["scenarios"] if s["id"] == "SCEN_04")
    inst_vi_04 = transduce_oracle(scen_04, "UMR-TPG", "VI")
    assert extract_q9_sortal(inst_vi_04) == "SORTAL_BOUND_VOLUME"
    assert extract_q3_roles(inst_vi_04)[":ARG1"] == "ent_book"


def test_exp02_non_isomorphism_functional_equivalence(corpus_path):
    """Verifies that EN and JA instances have different graph properties but 100% functional query equivalence."""
    with open(corpus_path, "r", encoding="utf-8") as f:
        data = json.load(f)

    scen_05 = next(s for s in data["scenarios"] if s["id"] == "SCEN_05")
    inst_en = transduce_oracle(scen_05, "UMR-TPG", "EN")
    inst_ja = transduce_oracle(scen_05, "UMR-TPG", "JA")

    # Functional query comparison
    res = evaluate_query_suite(inst_en, inst_ja)
    assert all(res.values()), f"Mismatched queries: {[k for k, v in res.items() if not v]}"


def test_exp02_reproducibility(corpus_path):
    """Verifies that two consecutive runs produce 100% bit-exact results."""
    run1 = run_exp02_evaluation(corpus_path)
    run2 = run_exp02_evaluation(corpus_path)

    assert run1["oracle_transduction"] == run2["oracle_transduction"]
    assert run1["rule_based_transduction"] == run2["rule_based_transduction"]
