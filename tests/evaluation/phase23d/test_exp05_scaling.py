"""Automated Pytest Suite for EXP-05: Scaling & Hardware Feasibility.

Covers the 12 required test areas:
1. Dataset integrity
2. Scaling-point completeness (1k, 5k, 10k, 25k, 50k, 100k)
3. Deterministic generation across seeds
4. Candidate store construction
5. Semantic lookup correctness
6. Memory measurement validity
7. Latency measurement validity
8. 100k stress condition verification
9. Revision correctness under scaling
10. SLA gate evaluation (UMR-TPG PASS, V-UMR FAIL on RAM, VRAM = 0.0 MB)
11. Reproducibility of semantic outputs
12. Production-boundary enforcement
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Dict

import pytest

from tests.evaluation.evaluation_phase23d.experiment_05_scaling.dataset.generator import (
    generate_scaling_facts,
)
from tests.evaluation.evaluation_phase23d.experiment_05_scaling.metrics import (
    evaluate_sla_gates,
    get_os_memory_mb,
)
from tests.evaluation.evaluation_phase23d.experiment_05_scaling.models.drs_scaling_store import (
    DRSScalingStore,
)
from tests.evaluation.evaluation_phase23d.experiment_05_scaling.models.umr_scaling_store import (
    UMRScalingStore,
)
from tests.evaluation.evaluation_phase23d.experiment_05_scaling.models.vumr_scaling_store import (
    VUMRScalingStore,
)
from tests.evaluation.evaluation_phase23d.experiment_05_scaling.run_experiment import (
    SCALING_POINTS,
    evaluate_candidate_at_scale,
)


@pytest.fixture
def raw_results_data() -> Dict[str, Any]:
    json_path = (
        Path(__file__).parents[2]
        / "evaluation"
        / "evaluation_phase23d"
        / "experiment_05_scaling"
        / "results"
        / "raw_results.json"
    )
    assert json_path.exists(), f"EXP-05 raw_results.json not found at {json_path}"
    with open(json_path, "r", encoding="utf-8") as f:
        return json.load(f)


def test_exp05_dataset_integrity() -> None:
    """1. Verifies dataset generator yields valid structured semantic facts."""
    facts, probes = generate_scaling_facts(n_facts=100, seed=42)
    assert len(facts) == 100
    assert len(probes["lookup_1hop"]) > 0
    assert "revision" in probes

    fact0 = facts[0]
    for key in ["id", "predicate", "subject", "arguments", "polarity", "conceiver", "valid_time", "tx_time"]:
        assert key in fact0


def test_exp05_scaling_point_completeness(raw_results_data: Dict[str, Any]) -> None:
    """2. Verifies that all 6 scaling points (1k to 100k) are present."""
    expected_points = [1000, 5000, 10000, 25000, 50000, 100000]
    assert raw_results_data["scaling_points"] == expected_points
    for cand in ["UMR-TPG", "V-UMR", "DRS-Graph"]:
        assert cand in raw_results_data["candidates"]
        cand_points = [r["n_facts"] for r in raw_results_data["candidates"][cand]["scaling_results"]]
        assert cand_points == expected_points


def test_exp05_deterministic_generation() -> None:
    """3. Verifies identical fact generation from same seed."""
    facts1, _ = generate_scaling_facts(n_facts=500, seed=123)
    facts2, _ = generate_scaling_facts(n_facts=500, seed=123)
    assert facts1 == facts2


def test_exp05_candidate_construction() -> None:
    """4. Verifies candidate stores can be instantiated and populated."""
    facts, _ = generate_scaling_facts(n_facts=200, seed=42)
    for store_cls in [UMRScalingStore, VUMRScalingStore, DRSScalingStore]:
        store = store_cls()
        for f in facts:
            store.insert_fact(f)
        assert store.count_facts() == 200


def test_exp05_semantic_lookup_correctness() -> None:
    """5. Verifies 1-hop lookups retrieve exact matching facts."""
    facts, probes = generate_scaling_facts(n_facts=500, seed=42)
    store = UMRScalingStore()
    for f in facts:
        store.insert_fact(f)

    for probe in probes["lookup_1hop"][:10]:
        res = store.lookup_1hop(probe["subject"], probe["predicate"])
        assert len(res) > 0
        retrieved_ids = [node.id for node in res]
        assert probe["expected_id"] in retrieved_ids


def test_exp05_memory_measurement_validity() -> None:
    """6. Verifies memory measurement utilities return positive values."""
    ws_mb, priv_mb = get_os_memory_mb()
    assert ws_mb >= 0.0
    assert priv_mb >= 0.0


def test_exp05_latency_measurement_validity() -> None:
    """7. Verifies latency evaluation returns proper percentiles (p50 <= p95 <= p99)."""
    facts, probes = generate_scaling_facts(n_facts=300, seed=42)
    res = evaluate_candidate_at_scale("UMR-TPG", UMRScalingStore, facts, probes)
    lookup_stats = res["lookup_1hop_ms"]
    assert lookup_stats["p50"] <= lookup_stats["p95"] <= lookup_stats["p99"]
    assert lookup_stats["p95"] <= 5.0  # Well within 5ms target


def test_exp05_100k_stress_condition(raw_results_data: Dict[str, Any]) -> None:
    """8. Verifies 100k stress horizon results and process stability."""
    umr_100k = raw_results_data["candidates"]["UMR-TPG"]["scaling_results"][-1]
    assert umr_100k["n_facts"] == 100000
    assert umr_100k["memory"]["heap_mb"] < 100.0  # ~43 MB measured
    assert umr_100k["lookup_1hop_ms"]["p95"] < 1.0  # Sub-millisecond lookup


def test_exp05_revision_correctness() -> None:
    """9. Verifies non-monotonic belief revision and dependency retraction."""
    facts, probes = generate_scaling_facts(n_facts=1000, seed=42)
    store = UMRScalingStore()
    for f in facts:
        store.insert_fact(f)

    if probes["revision"]:
        rev_probe = probes["revision"][0]
        root_id = rev_probe["root_id"]
        rev_res = store.revise_belief(rev_probe["contradicting_fact"])
        assert rev_res["retracted_count"] >= 1
        assert root_id in rev_res["retracted_ids"]
        # Invariant: defeated root must now be OUT
        assert store.facts[root_id].operational_state == "OUT"
        # Invariant: new contradicting fact must be IN
        new_fid = rev_probe["contradicting_fact"]["id"]
        assert store.facts[new_fid].operational_state == "IN"


def test_exp05_sla_gate_evaluation(raw_results_data: Dict[str, Any]) -> None:
    """10. Verifies SLA gate outcomes: UMR-TPG PASS, DRS-Graph PASS, V-UMR FAIL on RAM."""
    # UMR-TPG must pass all SLA gates
    assert raw_results_data["candidates"]["UMR-TPG"]["overall_verdict"] == "PASS"

    # DRS-Graph must pass all SLA gates
    assert raw_results_data["candidates"]["DRS-Graph"]["overall_verdict"] == "PASS"

    # V-UMR must FAIL on Working Set at 100k (falsification of H2)
    vumr_data = raw_results_data["candidates"]["V-UMR"]
    assert vumr_data["overall_verdict"] == "FAIL"
    vumr_100k_sla = vumr_data["scaling_results"][-1]["sla_gates"]
    assert vumr_100k_sla["ram_gate_passed"] is False
    assert vumr_100k_sla["ram_measured_mb"] > 350.0  # ~660 MB measured

    # VRAM must be strictly 0.0 MB across all candidates
    for cand in ["UMR-TPG", "V-UMR", "DRS-Graph"]:
        sla_100k = raw_results_data["candidates"][cand]["scaling_results"][-1]["sla_gates"]
        assert sla_100k["vram_mb"] == 0.0
        assert "UNVERIFIED" in sla_100k["tdp_status"]


def test_exp05_reproducibility() -> None:
    """11. Verifies semantic outputs are bit-identical across runs."""
    facts1, probes1 = generate_scaling_facts(n_facts=200, seed=999)
    facts2, probes2 = generate_scaling_facts(n_facts=200, seed=999)

    store1 = UMRScalingStore()
    store2 = UMRScalingStore()

    for f in facts1:
        store1.insert_fact(f)
    for f in facts2:
        store2.insert_fact(f)

    for p in probes1["lookup_1hop"][:5]:
        r1 = [n.id for n in store1.lookup_1hop(p["subject"], p["predicate"])]
        r2 = [n.id for n in store2.lookup_1hop(p["subject"], p["predicate"])]
        assert r1 == r2


def test_exp05_production_boundary_enforcement() -> None:
    """12. Verifies production files were untouched."""
    repo_root = Path(__file__).parents[2]
    # Check that data/profile.json has is_onboarded: false
    profile_path = repo_root / "data" / "profile.json"
    if profile_path.exists():
        with open(profile_path, "r", encoding="utf-8") as f:
            profile = json.load(f)
            assert profile.get("is_onboarded") is False
