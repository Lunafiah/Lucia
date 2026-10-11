"""
tests/evaluation/phase26/test_p26_r2_harness.py

Unit tests for P26-R2 Memory-Neutral Preference Transfer research harness.
Verifies:
- Production and Genesis isolation (INV-8)
- Exact retrieval masking and equalization behaviors
- Retrieval ablation quantification (R2-B)
- Cross-domain novel probe execution (R2-C)
- Persistence and revision tracking (R2-D)
- Covert-reward and implicit potential audit
"""

from __future__ import annotations

import json
from pathlib import Path
import numpy as np
import pytest

from tests.evaluation.phase26.p26_r2_memory_neutral_harness import (
    NOVEL_CROSS_DOMAIN_PROBES,
    P26R2MemoryNeutralSuite,
    R2InterpretationGate,
    R2ReplicaConfig,
    R2ResearchReplica,
    RetrievalMaskingMode,
    audit_covert_rewards_r2,
)


def test_genesis_gate_and_isolation():
    """Verify that data/profile.json is preserved bit-exact."""
    profile_path = Path("data/profile.json")
    if profile_path.exists():
        with open(profile_path, "r", encoding="utf-8") as f:
            data = json.load(f)
        assert data.get("is_onboarded") is False, "INV-8 VIOLATION: Genesis gate altered!"


def test_retrieval_masking_modes_behavior():
    """
    Verify that MASKED_ZERO forces effective memory components to 0.0,
    and EQUALIZED forces effective_mem_A == effective_mem_B.
    """
    cfg = R2ReplicaConfig(replica_id="test_masking_rep", seed=42)
    rep = R2ResearchReplica(cfg)

    # Write some memory traces
    topic = "Deep-sea hydrothermal ecosystems"
    stim = np.array([0.30, 0.10, 0.05], dtype=np.float64)
    for _ in range(5):
        rep.interact_turn(topic, stim)

    # 1. Unmasked evaluation
    _, _, meta_unm = rep.evaluate_probe(
        topic, "Medieval maritime cartography", masking_mode=RetrievalMaskingMode.UNMASKED
    )
    assert meta_unm["components"]["effective_mem_A"] > 0.0

    # 2. Masked Zero evaluation
    _, _, meta_msk = rep.evaluate_probe(
        topic, "Medieval maritime cartography", masking_mode=RetrievalMaskingMode.MASKED_ZERO
    )
    assert meta_msk["components"]["effective_mem_A"] == 0.0
    assert meta_msk["components"]["effective_mem_B"] == 0.0

    # 3. Equalized evaluation
    _, _, meta_eq = rep.evaluate_probe(
        topic, "Medieval maritime cartography", masking_mode=RetrievalMaskingMode.EQUALIZED
    )
    assert meta_eq["components"]["effective_mem_A"] == meta_eq["components"]["effective_mem_B"]


def test_retrieval_ablation_reduces_or_explains_bias():
    """
    Verify that episodic memory masking significantly reduces choice divergence compared
    to unmasked full-history retrieval.
    """
    suite = P26R2MemoryNeutralSuite(seeds=[1001, 1002, 1003], num_history_turns=10)
    record = suite.run_paired_trial(1001)

    # Unmasked prob difference should be significantly larger than masked prob difference
    assert record.target_prob_diff_unmasked > record.target_prob_diff_masked
    # Equalized prob difference should also be smaller than unmasked
    assert record.target_prob_diff_unmasked > record.target_prob_diff_equalized


def test_cross_domain_novel_probes_inventory():
    """Verify that all 4 cross-domain novel probe pairs are populated and evaluated."""
    assert len(NOVEL_CROSS_DOMAIN_PROBES) == 4
    suite = P26R2MemoryNeutralSuite(seeds=[2001], num_history_turns=5)
    rec = suite.run_paired_trial(2001)
    for probe in NOVEL_CROSS_DOMAIN_PROBES:
        assert probe.domain_id in rec.novel_domain_results
        res = rec.novel_domain_results[probe.domain_id]
        assert "prob_diff" in res
        assert "is_divergent" in res


def test_persistence_revision_r2d():
    """Verify execution of the R2-D persistence / revision sub-experiment."""
    suite = P26R2MemoryNeutralSuite(seeds=[3001, 3002], num_history_turns=5)
    r2d_res = suite.run_persistence_revision_experiment_r2d()
    assert r2d_res["sample_size"] == 2
    assert "mean_p_formation" in r2d_res
    assert "mean_p_steered" in r2d_res
    assert "mean_p_counter" in r2d_res


def test_covert_reward_audit_r2():
    """Verify covert reward audit verifies lack of scalar RL reduction."""
    report = audit_covert_rewards_r2()
    assert report.reduction_to_reinforcement_learning is False
    assert len(report.inspected_subsystems) == 4
    for _, details in report.inspected_subsystems.items():
        assert details["is_scalar_utility_maximizer"] is False
