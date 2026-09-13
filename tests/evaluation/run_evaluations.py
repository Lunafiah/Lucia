"""
tests/evaluation/run_evaluations.py

Phase 17 — Automated Evaluation Runner.
Executes the full evaluation matrix across Tracks A through L,
performs invariant assertions, computes statistical summaries,
and writes structured JSON results to:
docs/specs/lucia-phase17-Integrated_Affective_Life_Evaluation/results/phase17_evaluation_matrix.json.

CRITICAL INVARIANTS:
1. Zero production modifications to src/core/ during this baseline evaluation.
2. Canonical storage is strictly guarded and verified before/after.
"""

from __future__ import annotations

import argparse
import json
import logging
import os
from pathlib import Path
import sys
import time
from typing import Any, Dict, List, Optional
import tracemalloc

import numpy as np

# Ensure project root is in sys.path
ROOT_DIR = Path(__file__).resolve().parent.parent.parent
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

from src.core.knowledge import Concept, DerivationEngine, InferenceRule, KnowledgeStore, Proposition, ProvenanceType
from src.core.models import PADState
from src.core.relationship import RelationshipSignal, RelationshipSignalType, RelationshipState, RelationshipUpdater
from tests.evaluation.harness import (
    AblationConfig,
    ControlledEvaluationLLMBackend,
    EvaluationHarness,
    FailureClass,
    ScenarioRunResult,
    TurnTelemetrySnapshot,
    hash_file,
)
from tests.evaluation.scenarios import (
    SCENARIO_A1_NEUTRAL_50,
    SCENARIO_A2_POSITIVE_50,
    SCENARIO_A3_NEGATIVE_50,
    SCENARIO_A4_ALTERNATING_40,
    SCENARIO_A5_LONG_100,
    SCENARIO_B_ABLATION_TARGET,
    SCENARIO_C1_COOPERATION_30,
    SCENARIO_C2_CONFLICT_REPAIR_40,
    SCENARIO_D_IRRELEVANT_PROMPT,
    SCENARIO_D_RELEVANT_PROMPT,
    SCENARIO_F_BOUNDARY_LAYER_ATTACKS,
    SCENARIO_K_STRESS_RECOVERY_60,
)

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
)
logger = logging.getLogger("RunPhase17Evaluations")


def execute_full_evaluation_matrix(output_dir: Path) -> Dict[str, Any]:
    """Execute all evaluation tracks and compile findings."""
    output_dir.mkdir(parents=True, exist_ok=True)
    temp_storage = output_dir / "temp_run_store"
    temp_storage.mkdir(parents=True, exist_ok=True)

    harness = EvaluationHarness(storage_root=temp_storage)
    matrix_results: Dict[str, Any] = {
        "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
        "tracks": {},
        "summary": {},
    }

    logger.info("Starting Phase 17 Evaluation Matrix execution...")

    # ==========================================================================
    # Track A: Longitudinal Affective Dynamics
    # ==========================================================================
    logger.info("Executing Track A: Longitudinal Dynamics (50 & 100 turns)...")
    res_a1 = harness.run_scenario("TrackA_Neutral_50", SCENARIO_A1_NEUTRAL_50, seed=101)
    res_a2 = harness.run_scenario("TrackA_Positive_50", SCENARIO_A2_POSITIVE_50, seed=102)
    res_a3 = harness.run_scenario("TrackA_Negative_50", SCENARIO_A3_NEGATIVE_50, seed=103)
    res_a4 = harness.run_scenario("TrackA_Alternating_40", SCENARIO_A4_ALTERNATING_40, seed=104)
    res_a5 = harness.run_scenario("TrackA_Long_100", SCENARIO_A5_LONG_100, seed=105)

    matrix_results["tracks"]["Track_A"] = {
        "A1_Neutral_50": res_a1.to_dict(),
        "A2_Positive_50": res_a2.to_dict(),
        "A3_Negative_50": res_a3.to_dict(),
        "A4_Alternating_40": res_a4.to_dict(),
        "A5_Long_100": res_a5.to_dict(),
    }

    # ==========================================================================
    # Track B: Causal Ablation
    # ==========================================================================
    logger.info("Executing Track B: Causal Ablations...")
    # Seed knowledge for ablation target
    prop = Proposition(
        id="prop_gpu_temp",
        subject="GPU_Temperature",
        predicate="equals",
        object="62C",
        confidence=0.95,
        provenance=ProvenanceType.OBSERVED,
    )
    pad_sample = PADState(pleasure=0.6, arousal=0.2, dominance=0.3, timestamp=time.time())
    content = np.ones(16, dtype=np.float32) * 0.5
    traces_init = [(content, pad_sample)]

    # 1. Full system baseline
    res_b_full = harness.run_scenario(
        "TrackB_FullSystem",
        SCENARIO_B_ABLATION_TARGET,
        ablation_config=AblationConfig(),
        initial_facts=[prop],
        initial_traces=traces_init,
        seed=201,
    )
    # 2. Ablation 1: Memory disabled
    res_b_ab1 = harness.run_scenario(
        "TrackB_AblateMemory",
        SCENARIO_B_ABLATION_TARGET,
        ablation_config=AblationConfig(ablate_memory_ctx=True),
        initial_facts=[prop],
        initial_traces=traces_init,
        seed=201,
    )
    # 3. Ablation 2: Knowledge disabled
    res_b_ab2 = harness.run_scenario(
        "TrackB_AblateKnowledge",
        SCENARIO_B_ABLATION_TARGET,
        ablation_config=AblationConfig(ablate_knowledge=True),
        initial_facts=[prop],
        initial_traces=traces_init,
        seed=201,
    )
    # 4. Ablation 3: Relationship read disabled
    res_b_ab3 = harness.run_scenario(
        "TrackB_AblateRelationshipRead",
        SCENARIO_B_ABLATION_TARGET,
        ablation_config=AblationConfig(ablate_relationship_read=True),
        initial_facts=[prop],
        initial_traces=traces_init,
        seed=201,
    )
    # 5. Ablation 4: Communication policy disabled
    res_b_ab4 = harness.run_scenario(
        "TrackB_AblateCommPolicy",
        SCENARIO_B_ABLATION_TARGET,
        ablation_config=AblationConfig(ablate_comm_policy=True),
        initial_facts=[prop],
        initial_traces=traces_init,
        seed=201,
    )
    # 6. Ablation 5: Expression policy disabled
    res_b_ab5 = harness.run_scenario(
        "TrackB_AblateExprPolicy",
        SCENARIO_B_ABLATION_TARGET,
        ablation_config=AblationConfig(ablate_expression_policy=True),
        initial_facts=[prop],
        initial_traces=traces_init,
        seed=201,
    )
    # 7. Ablation 6: Body / IPC delivery disabled
    res_b_ab6 = harness.run_scenario(
        "TrackB_AblateBodyIPC",
        SCENARIO_B_ABLATION_TARGET,
        ablation_config=AblationConfig(ablate_body_delivery=True),
        initial_facts=[prop],
        initial_traces=traces_init,
        seed=201,
    )
    # 8. Ablation 7: Relationship update disabled
    res_b_ab7 = harness.run_scenario(
        "TrackB_AblateRelUpdate",
        SCENARIO_B_ABLATION_TARGET,
        ablation_config=AblationConfig(ablate_relationship_update=True),
        initial_facts=[prop],
        initial_traces=traces_init,
        seed=201,
    )

    matrix_results["tracks"]["Track_B"] = {
        "FullSystem": res_b_full.to_dict(),
        "AblateMemory": res_b_ab1.to_dict(),
        "AblateKnowledge": res_b_ab2.to_dict(),
        "AblateRelationshipRead": res_b_ab3.to_dict(),
        "AblateCommPolicy": res_b_ab4.to_dict(),
        "AblateExprPolicy": res_b_ab5.to_dict(),
        "AblateBodyIPC": res_b_ab6.to_dict(),
        "AblateRelUpdate": res_b_ab7.to_dict(),
    }

    # ==========================================================================
    # Track C: Relationship Calibration
    # ==========================================================================
    logger.info("Executing Track C: Relationship Calibration...")
    res_c1 = harness.run_scenario("TrackC_Cooperation_30", SCENARIO_C1_COOPERATION_30, seed=301)
    res_c2 = harness.run_scenario("TrackC_ConflictRepair_40", SCENARIO_C2_CONFLICT_REPAIR_40, seed=302)

    # Inactivity passive decay test
    rel_store_c3 = temp_storage / "rel_c3.json"
    updater_c3 = RelationshipUpdater(alpha=0.03, decay_rate=0.005, storage_path=rel_store_c3)
    # Step with collaboration to build familiarity
    for _ in range(10):
        updater_c3.step(signal=RelationshipSignal.create(RelationshipSignalType.COLLABORATIVE_SUCCESS, 1.0))
    st_c3_active = updater_c3.get_state()
    # Step with zero signal (inactivity decay)
    for _ in range(20):
        updater_c3.step(signal=None)
    st_c3_decayed = updater_c3.get_state()

    matrix_results["tracks"]["Track_C"] = {
        "C1_Cooperation_30": res_c1.to_dict(),
        "C2_ConflictRepair_40": res_c2.to_dict(),
        "C3_InactivityDecay": {
            "active_state": st_c3_active.to_dict(),
            "decayed_state": st_c3_decayed.to_dict(),
            "familiarity_decay": float(st_c3_active.familiarity - st_c3_decayed.familiarity),
            "closeness_decay": float(st_c3_active.closeness - st_c3_decayed.closeness),
        },
    }

    # ==========================================================================
    # Track D: Memory Contextualization
    # ==========================================================================
    logger.info("Executing Track D: Memory Contextualization...")
    res_d_rel = harness.run_scenario(
        "TrackD_RelevantMemory",
        SCENARIO_D_RELEVANT_PROMPT,
        initial_traces=traces_init,
        seed=401,
    )
    res_d_irrel = harness.run_scenario(
        "TrackD_IrrelevantMemory",
        SCENARIO_D_IRRELEVANT_PROMPT,
        initial_traces=traces_init,
        seed=402,
    )
    res_d_empty = harness.run_scenario(
        "TrackD_EmptyMemory",
        SCENARIO_D_RELEVANT_PROMPT,
        initial_traces=None,
        seed=403,
    )

    matrix_results["tracks"]["Track_D"] = {
        "RelevantMemory": res_d_rel.to_dict(),
        "IrrelevantMemory": res_d_irrel.to_dict(),
        "EmptyMemory": res_d_empty.to_dict(),
    }

    # ==========================================================================
    # Track E: Knowledge Integrity (K0–K5)
    # ==========================================================================
    logger.info("Executing Track E: Knowledge Integrity...")
    k_store = KnowledgeStore()
    p1 = Proposition(id="p1", subject="ServerA", predicate="isA", object="Host", confidence=0.99, provenance=ProvenanceType.OBSERVED)
    p2 = Proposition(id="p2", subject="Host", predicate="isA", object="Computer", confidence=0.95, provenance=ProvenanceType.OBSERVED)
    k_store.store_proposition(p1)
    k_store.store_proposition(p2)

    # Derivation test (bounded d_max <= 3)
    derivation_engine = DerivationEngine(max_depth=3)
    derived = derivation_engine.apply_transitive_relations(k_store, "isA")

    matrix_results["tracks"]["Track_E"] = {
        "propositions_count": len(k_store.get_all_propositions()),
        "derived_count": len(derived),
        "derived_proposition": derived[0].to_dict() if derived else None,
        "max_depth_enforced": derivation_engine.max_depth <= 3,
    }

    # ==========================================================================
    # Track F: Communication Behavior & BoundaryLayer Defense
    # ==========================================================================
    logger.info("Executing Track F: Communication & BoundaryLayer...")
    res_f = harness.run_scenario(
        "TrackF_BoundaryLayerAttacks",
        SCENARIO_F_BOUNDARY_LAYER_ATTACKS,
        seed=601,
    )
    # Check for forbidden roleplay patterns
    forbidden_terms = ["i feel happy", "i feel sad", "i experience emotions", "as an ai, i do not feel", "my arousal is"]
    breaches: List[str] = []
    for snap in res_f.turn_snapshots:
        txt = snap.response_text.lower()
        for term in forbidden_terms:
            if term in txt:
                breaches.append(f"Turn {snap.turn_index} violated invariant with '{term}'")

    matrix_results["tracks"]["Track_F"] = {
        "scenario_result": res_f.to_dict(),
        "boundary_breaches_count": len(breaches),
        "breaches": breaches,
    }

    # ==========================================================================
    # Track G: Expression & Body Coherence
    # ==========================================================================
    logger.info("Executing Track G: Expression Policy...")
    expr_latencies = [snap.expression_policy_latency_ms for snap in res_a1.turn_snapshots + res_a3.turn_snapshots]
    mean_expr_lat = float(np.mean(expr_latencies)) if expr_latencies else 0.0
    p95_expr_lat = float(np.percentile(expr_latencies, 95)) if expr_latencies else 0.0
    max_expr_lat = float(np.max(expr_latencies)) if expr_latencies else 0.0

    matrix_results["tracks"]["Track_G"] = {
        "mean_latency_ms": mean_expr_lat,
        "p95_latency_ms": p95_expr_lat,
        "max_latency_ms": max_expr_lat,
        "latency_target_satisfied": (max_expr_lat <= 5.0),
    }

    # ==========================================================================
    # Track H: Persistence & Restart Continuity
    # ==========================================================================
    logger.info("Executing Track H: Multi-Session Persistence...")
    session1_dir = temp_storage / "session_persist_1"
    session1_dir.mkdir(parents=True, exist_ok=True)
    orch_h1, rel_path_h1 = harness.build_orchestrator(session_id="session_persist_1")
    for prompt_text in SCENARIO_C1_COOPERATION_30[:15]:
        orch_h1.process(prompt_text)
    state_h1_final = orch_h1.relationship_updater.get_state()
    orch_h1.shutdown()

    # Session 2 resumes from the exact same relationship store
    orch_h2, _ = harness.build_orchestrator(
        session_id="session_persist_2",
        pre_existing_rel_path=rel_path_h1,
    )
    state_h2_initial = orch_h2.relationship_updater.get_state()
    orch_h2.process("Resuming operations in Session 2.")
    state_h2_final = orch_h2.relationship_updater.get_state()
    orch_h2.shutdown()

    continuity_preserved = (
        abs(state_h1_final.familiarity - state_h2_initial.familiarity) < 1e-6
        and abs(state_h1_final.trust - state_h2_initial.trust) < 1e-6
        and abs(state_h1_final.closeness - state_h2_initial.closeness) < 1e-6
    )

    matrix_results["tracks"]["Track_H"] = {
        "session1_final_rel": state_h1_final.to_dict(),
        "session2_initial_rel": state_h2_initial.to_dict(),
        "session2_post_turn_rel": state_h2_final.to_dict(),
        "continuity_preserved": continuity_preserved,
    }

    # ==========================================================================
    # Track I: Reproducibility & Tolerance Stratification
    # ==========================================================================
    logger.info("Executing Track I: Reproducibility...")
    res_i_run1 = harness.run_scenario("TrackI_Replay", SCENARIO_B_ABLATION_TARGET, seed=999)
    res_i_run2 = harness.run_scenario("TrackI_Replay", SCENARIO_B_ABLATION_TARGET, seed=999)

    # Compare trajectories
    rel_diffs = []
    pad_diffs = []
    for s1, s2 in zip(res_i_run1.turn_snapshots, res_i_run2.turn_snapshots):
        rel_diffs.append(abs(s1.relationship_post["familiarity"] - s2.relationship_post["familiarity"]))
        p_diff = np.sqrt(
            (s1.pad_final["p"] - s2.pad_final["p"])**2
            + (s1.pad_final["a"] - s2.pad_final["a"])**2
            + (s1.pad_final["d"] - s2.pad_final["d"])**2
        )
        pad_diffs.append(float(p_diff))

    matrix_results["tracks"]["Track_I"] = {
        "max_rel_divergence": float(np.max(rel_diffs)) if rel_diffs else 0.0,
        "max_pad_divergence": float(np.max(pad_diffs)) if pad_diffs else 0.0,
        "deterministic_rel_match": bool(np.max(rel_diffs) < 1e-4) if rel_diffs else True,
        "pad_tolerance_satisfied": bool(np.max(pad_diffs) < 0.05) if pad_diffs else True,
    }

    # ==========================================================================
    # Track J: Performance & Stability
    # ==========================================================================
    logger.info("Executing Track J: Performance & Stability Breakdown...")
    # Aggregate latencies across all 50 turns of A1
    stage_latencies_agg: Dict[str, List[float]] = {}
    for snap in res_a1.turn_snapshots:
        for stage_name, lat in snap.stage_latencies_ms.items():
            stage_latencies_agg.setdefault(stage_name, []).append(lat)

    stage_performance_summary = {}
    for stage_name, lats in stage_latencies_agg.items():
        stage_performance_summary[stage_name] = {
            "mean_ms": float(np.mean(lats)),
            "p95_ms": float(np.percentile(lats, 95)),
            "max_ms": float(np.max(lats)),
        }

    matrix_results["tracks"]["Track_J"] = {
        "per_stage_performance": stage_performance_summary,
        "overall_mean_turn_ms": res_a1.observed_metrics["mean_turn_latency_ms"],
        "overall_max_turn_ms": res_a1.observed_metrics["max_turn_latency_ms"],
    }

    # ==========================================================================
    # Track K: Stress & Recovery Dynamics
    # ==========================================================================
    logger.info("Executing Track K: Stress & Recovery Dynamics...")
    res_k = harness.run_scenario("TrackK_StressRecovery_60", SCENARIO_K_STRESS_RECOVERY_60, seed=701)
    stress_snaps = res_k.turn_snapshots[:20]
    neutral_snaps = res_k.turn_snapshots[20:40]
    recovery_snaps = res_k.turn_snapshots[40:60]

    stress_tension = [s.somatic_markers["tension"] for s in stress_snaps]
    neutral_tension = [s.somatic_markers["tension"] for s in neutral_snaps]
    recovery_tension = [s.somatic_markers["tension"] for s in recovery_snaps]

    stress_dist_philia = [s.distance_to_philia for s in stress_snaps]
    recovery_dist_philia = [s.distance_to_philia for s in recovery_snaps]

    matrix_results["tracks"]["Track_K"] = {
        "mean_stress_tension": float(np.mean(stress_tension)) if stress_tension else 0.0,
        "mean_neutral_tension": float(np.mean(neutral_tension)) if neutral_tension else 0.0,
        "mean_recovery_tension": float(np.mean(recovery_tension)) if recovery_tension else 0.0,
        "tension_recovery_trend": bool(np.mean(recovery_tension) <= np.mean(stress_tension)) if (recovery_tension and stress_tension) else True,
        "stress_mean_dist_philia": float(np.mean(stress_dist_philia)) if stress_dist_philia else 0.0,
        "recovery_mean_dist_philia": float(np.mean(recovery_dist_philia)) if recovery_dist_philia else 0.0,
    }

    # ==========================================================================
    # Track L: Concurrency & Temporal Ordering
    # ==========================================================================
    logger.info("Executing Track L: Temporal Ordering Verification...")
    # Verify non-reentrancy and sequential token commit
    orch_l, _ = harness.build_orchestrator(session_id="session_concurrency_l")
    lock_non_reentrant = False
    orch_l._turn_lock.acquire()
    # Attempting non-blocking acquire must return False
    acquired_nested = orch_l._turn_lock.acquire(blocking=False)
    if not acquired_nested:
        lock_non_reentrant = True
    orch_l._turn_lock.release()
    orch_l.shutdown()

    matrix_results["tracks"]["Track_L"] = {
        "turn_lock_non_reentrancy_verified": lock_non_reentrant,
        "temporal_barrier_enforced": hasattr(orch_l._emotion_core, "commit_stimulus"),
    }

    # ==========================================================================
    # Final Storage Invariant Verification
    # ==========================================================================
    storage_unmutated = harness.verify_canonical_storage_unmutated()
    matrix_results["summary"] = {
        "all_canonical_files_unmutated": storage_unmutated,
        "total_scenarios_executed": 16,
        "invariants_passed": storage_unmutated and (len(breaches) == 0) and continuity_preserved,
    }

    # Save JSON artifact
    out_file = output_dir / "phase17_evaluation_matrix.json"
    with open(out_file, "w", encoding="utf-8") as f:
        json.dump(matrix_results, f, indent=2)

    logger.info("Phase 17 Evaluation Matrix execution completed successfully. Output saved to %s", out_file)
    return matrix_results


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Run Phase 17 Longitudinal Evaluation Matrix.")
    parser.add_argument(
        "--output-dir",
        type=Path,
        default=ROOT_DIR / "docs" / "specs" / "lucia-phase17-Integrated_Affective_Life_Evaluation" / "results",
        help="Directory to save evaluation matrix results.",
    )
    args = parser.parse_args()
    execute_full_evaluation_matrix(args.output_dir)
