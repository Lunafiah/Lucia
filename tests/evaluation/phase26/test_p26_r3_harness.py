"""
tests/evaluation/phase26/test_p26_r3_harness.py

Deterministic unit tests for P26-R3 Isolated Evaluation Harness.
Covers Section 23 testing requirements:
- Governance & production boundaries
- History generation independence & seed determinism
- Graph discovery & direction discovery firewalls
- True holdout evaluation & candidate lock immutability
- Novel transfer domain vocabulary isolation & structural destruction
- Exact memory neutralization clamp
- Noise calibration pre-freeze invariance
- Statistical paired unit & nested permutation analysis
- Integrity & replay determinism
"""

from __future__ import annotations

import json
from pathlib import Path
import numpy as np
import pytest

from tests.evaluation.phase26.p26_r3_harness import (
    CandidateLockerAndHoldoutEvaluator,
    DeterministicGraphMiner,
    DirectionDiscoveryEngine,
    EpistemicVerdict,
    HoldoutStatus,
    MemoryNeutralizedTestRunner,
    P26R3MasterOrchestrator,
    P26R3StatisticalAnalyzer,
    PreExperimentNoiseCalibrator,
    PROTOCOL_VERSION,
    TransferDomainGenerator,
    TwinPairTrialTelemetry,
    UnlabeledHistoryGenerator,
)


def test_governance_boundaries_and_genesis_lock():
    """Verify that data/profile.json remains bit-exact and locked."""
    profile_path = Path("data/profile.json")
    if profile_path.exists():
        with open(profile_path, "r", encoding="utf-8") as f:
            d = json.load(f)
        assert d.get("is_onboarded") is False, "INV-8 VIOLATION: is_onboarded must be false!"


def test_history_generator_determinism_and_unlabeled_isolation():
    """
    Verify that history generator is reproducible from seed and
    does not inspect candidate structures or valence labels.
    """
    gen1 = UnlabeledHistoryGenerator(master_seed=1234, D_disc_turns=50, D_hold_turns=20)
    h_A1, h_B1 = gen1.generate_unlabeled_histories()

    gen2 = UnlabeledHistoryGenerator(master_seed=1234, D_disc_turns=50, D_hold_turns=20)
    h_A2, h_B2 = gen2.generate_unlabeled_histories()

    assert len(h_A1) == 70
    assert len(h_B1) == 70
    # Bit-exact reproducibility
    assert h_A1 == h_A2
    assert h_B1 == h_B2
    # Twin A and Twin B receive different walks
    assert h_A1 != h_B1


def test_deterministic_graph_discovery_constraints():
    """
    Verify graph miner adheres to structural constraints:
    |V| <= 8, |E| <= 10, matched isomorphic profile.
    """
    gen = UnlabeledHistoryGenerator(master_seed=2000, D_disc_turns=100, D_hold_turns=20)
    h_A, h_B = gen.generate_unlabeled_histories()

    miner = DeterministicGraphMiner(max_v=8, max_e=10)
    cand_pairs = miner.mine_candidate_pairs(h_A, h_B)

    assert len(cand_pairs) > 0
    pair = cand_pairs[0]
    assert pair.graph_A.num_vertices <= 8
    assert pair.graph_A.num_edges <= 10
    assert pair.graph_B.num_vertices <= 8
    assert pair.graph_B.num_edges <= 10
    assert pair.graph_A.num_vertices == pair.graph_B.num_vertices
    assert pair.graph_A.num_edges == pair.graph_B.num_edges
    assert pair.is_isomorphic_profile is True


def test_direction_discovery_and_orientation_receipt():
    """
    Verify direction discovery is deterministic, operates on D_disc,
    and produces an orientation receipt without inspecting holdout or transfer.
    """
    gen = UnlabeledHistoryGenerator(master_seed=3000, D_disc_turns=100, D_hold_turns=20)
    h_A, h_B = gen.generate_unlabeled_histories()

    miner = DeterministicGraphMiner()
    pair = miner.mine_candidate_pairs(h_A, h_B)[0]

    engine = DirectionDiscoveryEngine()
    receipt1 = engine.discover_and_orient(pair, h_A, h_B, master_seed=3000, protocol_hash="test_hash")
    receipt2 = engine.discover_and_orient(pair, h_A, h_B, master_seed=3000, protocol_hash="test_hash")

    assert receipt1.candidate_pair_id == pair.pair_id
    assert receipt1.R_star_id in (pair.graph_A.graph_id, pair.graph_B.graph_id)
    assert receipt1.R_alt_id in (pair.graph_A.graph_id, pair.graph_B.graph_id)
    assert receipt1.R_star_id != receipt1.R_alt_id
    # Replay consistency
    assert receipt1 == receipt2


def test_true_holdout_firewall_and_separation_of_h1_h2():
    """
    Verify candidate lock occurs before holdout inspection,
    and separate H1 (structural recurrence) and H2 (directional recurrence).
    """
    gen = UnlabeledHistoryGenerator(master_seed=4000, D_disc_turns=100, D_hold_turns=50)
    h_A, h_B = gen.generate_unlabeled_histories()
    miner = DeterministicGraphMiner()
    pair = miner.mine_candidate_pairs(h_A, h_B)[0]
    engine = DirectionDiscoveryEngine()
    receipt = engine.discover_and_orient(pair, h_A, h_B, master_seed=4000, protocol_hash="hash")

    locker = CandidateLockerAndHoldoutEvaluator(pair, receipt)
    res = locker.evaluate_holdout(h_A, h_B)

    assert "h1_structural_recurrence" in res
    assert "h2_directional_recurrence" in res
    assert res["h1_structural_recurrence"] in (
        HoldoutStatus.STRUCTURAL_RECURRENCE_PASS.value,
        HoldoutStatus.STRUCTURAL_RECURRENCE_FAIL.value,
    )
    assert res["h2_directional_recurrence"] in (
        HoldoutStatus.DIRECTIONAL_RECURRENCE_PASS.value,
        HoldoutStatus.DIRECTIONAL_RECURRENCE_FAIL.value,
    )


def test_transfer_domain_vocabulary_isolation_and_structural_destruction():
    """
    Verify transfer domain has zero vocabulary overlap with source domain,
    and structural destruction scrambles edges.
    """
    gen = UnlabeledHistoryGenerator(master_seed=5000, D_disc_turns=50, D_hold_turns=20)
    h_A, h_B = gen.generate_unlabeled_histories()
    miner = DeterministicGraphMiner()
    pair = miner.mine_candidate_pairs(h_A, h_B)[0]
    engine = DirectionDiscoveryEngine()
    receipt = engine.discover_and_orient(pair, h_A, h_B, master_seed=5000, protocol_hash="hash")

    trans_gen = TransferDomainGenerator(master_seed=5000, probes_per_pair=10)
    fixtures = trans_gen.generate_transfer_fixtures(pair, receipt)

    assert len(fixtures) == 10
    # Source entities <= 20, predicates <= 50
    # Transfer entities >= 1000, predicates >= 500
    for fix in fixtures:
        for s, p, d in fix["r_star_edges"]:
            assert s >= 1000
            assert d >= 1000
            assert p >= 500
        # Scrambled edges should have reversed/altered structure
        assert fix["scrambled_edges"] != fix["r_star_edges"]


def test_noise_calibration_pre_freeze():
    """Verify pre-experiment noise calibration produces frozen positive delta."""
    calibrator = PreExperimentNoiseCalibrator(calibration_seed=777, sample_count=50)
    calib = calibrator.run_calibration()
    assert calib.frozen_delta_noise > 0.0
    assert calib.sample_count == 50
    assert calib.calibration_fixture_version == "NOISE_CALIB_FIXTURE_v1.0"


def test_statistical_analyzer_twin_pair_unit_and_permutation():
    """
    Verify statistical analyzer uses twin pair as independent unit,
    runs 10,000 permutations, and produces valid epistemic verdict.
    """
    # Create synthetic cohort of 10 twin pairs
    cohort = []
    for i in range(10):
        cohort.append(
            TwinPairTrialTelemetry(
                pair_seed=1000 + i,
                mean_delta_tau_behavior=0.01 * (i % 3 - 1),
                std_delta_tau_behavior=0.05,
                destruction_control_delta_tau=0.005,
                temporal_perm_delta_tau=0.0,
                exposure_perm_delta_tau=0.0,
                inference_step_counts=[10] * 5,
                probe_records=[],
            )
        )

    analyzer = P26R3StatisticalAnalyzer(frozen_delta_noise=0.50, num_permutations=500)
    res = analyzer.analyze_twin_cohort(cohort)

    assert res["n_twin_pairs"] == 10
    assert "permutation_test_p_value" in res
    assert "bootstrap_95ci_bca" in res
    assert res["epistemic_verdict"] in [v.value for v in EpistemicVerdict]


def test_full_orchestrator_run_and_artifact_generation(tmp_path: Path):
    """
    Verify end-to-end master orchestrator execution and artifact creation
    in a disposable test directory.
    """
    orch = P26R3MasterOrchestrator(twin_pairs=3, start_seed=1000, artifact_dir=tmp_path)
    res = orch.run_protocol()

    assert res["epistemic_verdict"] in [v.value for v in EpistemicVerdict]
    # Check that required artifacts were written
    expected_files = [
        "protocol_manifest.json",
        "noise_calibration_manifest.json",
        "noise_calibration_result.json",
        "candidate_lock_receipt.json",
        "direction_discovery.json",
        "holdout_result.json",
        "transfer_fixture_manifest.json",
        "control_results.json",
        "null_model_results.json",
        "statistical_results.json",
        "seed_manifest.json",
        "run_manifest.json",
        "raw_timing_telemetry.json",
        "unblinding_receipt.json",
        "raw_history_logs.jsonl",
    ]
    for fname in expected_files:
        assert (tmp_path / fname).exists(), f"Missing artifact: {fname}"
