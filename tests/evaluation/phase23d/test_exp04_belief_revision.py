"""Automated Pytest Suite for EXP-04: Belief Revision & Contradiction.

Verifies:
- Dataset integrity (10 preregistered scenarios)
- UMR-TPG preregistered gates (CDR >= 0.98, DPA = 1.0, CRR = 0, HRR = 1.0)
- V-UMR auxiliary vector isolation (vectors are NOT source of truth for contradiction)
- DRS-Graph box-condition accessibility & dependency gates
- Falsification tests:
  1. Temporal disjoint intervals do NOT trigger contradiction
  2. Multi-hop retraction propagation completes without truncation
  3. Collateral retraction rate is strictly 0.0 across 50 background facts
  4. Repeated revision preserves complete audit provenance
- Bit-exact reproducibility across independent runs
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Dict

import pytest

from tests.evaluation.evaluation_phase23d.experiment_04_belief_revision.dataset.generator import (
    generate_exp04_corpus,
)
from tests.evaluation.evaluation_phase23d.experiment_04_belief_revision.models.drs_belief_revision import (
    DRSBeliefEngine,
)
from tests.evaluation.evaluation_phase23d.experiment_04_belief_revision.models.umr_belief_revision import (
    UMRBeliefEngine,
)
from tests.evaluation.evaluation_phase23d.experiment_04_belief_revision.models.vumr_belief_revision import (
    VUMRBeliefEngine,
)
from tests.evaluation.evaluation_phase23d.experiment_04_belief_revision.run_experiment import (
    run_all_exp04,
    run_single_scenario,
)


@pytest.fixture
def corpus_data() -> Dict[str, Any]:
    corpus_path = (
        Path(__file__).parents[2]
        / "evaluation"
        / "evaluation_phase23d"
        / "experiment_04_belief_revision"
        / "dataset"
        / "corpus.json"
    )
    if not corpus_path.exists():
        return generate_exp04_corpus()
    with open(corpus_path, "r", encoding="utf-8") as f:
        return json.load(f)


def test_exp04_dataset_integrity(corpus_data: Dict[str, Any]) -> None:
    """Verifies that all 10 preregistered scenarios exist with complete specifications."""
    scenarios = corpus_data["scenarios"]
    assert len(scenarios) == 10, f"Expected 10 scenarios, got {len(scenarios)}"

    expected_ids = {f"SC{i:02d}" for i in range(1, 11)}
    actual_ids = {s["id"] for s in scenarios}
    assert actual_ids == expected_ids

    for sc in scenarios:
        assert "id" in sc
        assert "name" in sc
        assert "initial_assertions" in sc
        assert "updates" in sc
        assert "expected_oracle" in sc
        oracle = sc["expected_oracle"]
        assert "contradictions" in oracle
        assert "final_states" in oracle
        assert "history_count" in oracle


def test_exp04_umr_tpg_gates(corpus_data: Dict[str, Any]) -> None:
    """Evaluates UMR-TPG against preregistered gates."""
    for sc in corpus_data["scenarios"]:
        res = run_single_scenario(UMRBeliefEngine, sc)
        assert res["CDR"] >= 0.98, f"UMR CDR failed on {sc['id']}: {res['CDR']}"
        assert res["RC"] >= 0.98, f"UMR RC failed on {sc['id']}: {res['RC']}"
        assert res["DPA"] == 1.0, f"UMR DPA failed on {sc['id']}: {res['DPA']}"
        assert res["CRR"] == 0.0, f"UMR CRR failed on {sc['id']}: {res['CRR']}"
        assert res["HRR"] == 1.0, f"UMR HRR failed on {sc['id']}: {res['HRR']}"
        assert res["passed"] is True


def test_exp04_vumr_gates_and_auxiliary_vector_separation(corpus_data: Dict[str, Any]) -> None:
    """Evaluates V-UMR and verifies continuous vectors are NOT authority for truth."""
    engine = VUMRBeliefEngine()

    for sc in corpus_data["scenarios"]:
        res = run_single_scenario(VUMRBeliefEngine, sc)
        assert res["CDR"] >= 0.98
        assert res["RC"] >= 0.98
        assert res["DPA"] == 1.0
        assert res["CRR"] == 0.0
        assert res["HRR"] == 1.0
        assert res["passed"] is True

    # Test an instance directly to inspect vector comparison audit trail
    sc01 = corpus_data["scenarios"][0]
    for a in sc01["initial_assertions"]:
        engine.assert_fact(a)
    for u in sc01["updates"]:
        engine.assert_fact(u)

    # Invariant: all vector comparisons must explicitly have used_for_truth == False
    assert len(engine.vector_comparisons) > 0
    for comp in engine.vector_comparisons:
        assert comp["used_for_truth"] is False, (
            "FALSIFICATION FAILURE: Continuous vector similarity was used as authority for truth!"
        )


def test_exp04_drs_graph_gates(corpus_data: Dict[str, Any]) -> None:
    """Evaluates DRS-Graph control candidate against all gates."""
    for sc in corpus_data["scenarios"]:
        res = run_single_scenario(DRSBeliefEngine, sc)
        assert res["CDR"] >= 0.98
        assert res["RC"] >= 0.98
        assert res["DPA"] == 1.0
        assert res["CRR"] == 0.0
        assert res["HRR"] == 1.0
        assert res["passed"] is True


def test_exp04_falsification_temporal_disjoint_no_conflict(corpus_data: Dict[str, Any]) -> None:
    """SC06: Non-overlapping temporal intervals must NOT be flagged as contradiction."""
    sc06 = next(s for s in corpus_data["scenarios"] if s["id"] == "SC06")
    engine = UMRBeliefEngine()

    for a in sc06["initial_assertions"]:
        engine.assert_fact(a)
    for u in sc06["updates"]:
        engine.assert_fact(u)

    # Must detect 0 contradictions
    assert len(engine.get_detected_contradictions()) == 0
    states = engine.get_operational_states()
    # Both must remain IN
    assert states["SC06_A1"] == "IN"
    assert states["SC06_A2"] == "IN"


def test_exp04_falsification_multi_hop_propagation(corpus_data: Dict[str, Any]) -> None:
    """SC04: Defeat of A must propagate across A -> B -> C without premature halt."""
    sc04 = next(s for s in corpus_data["scenarios"] if s["id"] == "SC04")
    engine = UMRBeliefEngine()

    for a in sc04["initial_assertions"]:
        engine.assert_fact(a)
    for u in sc04["updates"]:
        engine.assert_fact(u)

    states = engine.get_operational_states()
    assert states["SC04_A"] == "OUT"
    assert states["SC04_B"] == "OUT"
    assert states["SC04_C"] == "OUT"
    assert states["SC04_A_DEFEAT"] == "IN"


def test_exp04_falsification_collateral_retraction_zero(corpus_data: Dict[str, Any]) -> None:
    """SC10: Revision of target premise must leave 50 background facts completely IN."""
    sc10 = next(s for s in corpus_data["scenarios"] if s["id"] == "SC10")
    engine = UMRBeliefEngine()

    for a in sc10["initial_assertions"]:
        engine.assert_fact(a)
    for u in sc10["updates"]:
        engine.assert_fact(u)

    states = engine.get_operational_states()
    # Target assertions
    assert states["SC10_TARGET_P"] == "OUT"
    assert states["SC10_TARGET_D"] == "OUT"
    assert states["SC10_TARGET_DEFEAT"] == "IN"

    # All 50 background assertions must remain IN
    for i in range(50):
        bg_id = f"SC10_BG_{i:02d}"
        assert states[bg_id] == "IN", f"Collateral retraction on {bg_id}!"


def test_exp04_falsification_repeated_revision_and_provenance(corpus_data: Dict[str, Any]) -> None:
    """SC09: P -> NOT P -> P must preserve all 3 transaction records in history."""
    sc09 = next(s for s in corpus_data["scenarios"] if s["id"] == "SC09")
    engine = UMRBeliefEngine()

    for a in sc09["initial_assertions"]:
        engine.assert_fact(a)
    for u in sc09["updates"]:
        engine.assert_fact(u)

    states = engine.get_operational_states()
    assert states["SC09_P1"] == "OUT"
    assert states["SC09_P2"] == "OUT"
    assert states["SC09_P3"] == "IN"

    history = engine.get_history_ids()
    assert history == {"SC09_P1", "SC09_P2", "SC09_P3"}
    assert len(engine.tx_history) == 3


def test_exp04_reproducibility() -> None:
    """Confirms bit-exact metric outputs across two independent executions."""
    corpus_file = (
        Path(__file__).parents[2]
        / "evaluation"
        / "evaluation_phase23d"
        / "experiment_04_belief_revision"
        / "dataset"
        / "corpus.json"
    )
    tmp_out = (
        Path(__file__).parents[2]
        / "evaluation"
        / "evaluation_phase23d"
        / "experiment_04_belief_revision"
        / "results"
    )

    run1 = run_all_exp04(corpus_file, tmp_out)
    run2 = run_all_exp04(corpus_file, tmp_out)

    for cand in ["UMR-TPG", "V-UMR", "DRS-Graph"]:
        assert run1["candidates"][cand]["mean_CDR"] == run2["candidates"][cand]["mean_CDR"]
        assert run1["candidates"][cand]["mean_RC"] == run2["candidates"][cand]["mean_RC"]
        assert run1["candidates"][cand]["mean_DPA"] == run2["candidates"][cand]["mean_DPA"]
        assert run1["candidates"][cand]["mean_CRR"] == run2["candidates"][cand]["mean_CRR"]
        assert run1["candidates"][cand]["mean_HRR"] == run2["candidates"][cand]["mean_HRR"]
        assert run1["candidates"][cand]["verdict"] == run2["candidates"][cand]["verdict"]
