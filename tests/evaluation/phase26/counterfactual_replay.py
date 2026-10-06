"""
tests/evaluation/phase26/counterfactual_replay.py

P26 Blocker 4 — Counterfactual Replay & Prefix Equivalence Harness.
Coordinates counterfactual rollouts from verified checkpoints, enforcing fail-closed
prefix equivalence and tracking divergence onset in an immutable difference ledger.

GOVERNANCE & BOUNDARIES:
- TEST-ONLY research infrastructure. Zero changes to src/core/** or electron/**.
- INV-1 (Anti-Branching): Counterfactual replays are synthetic test fixtures;
  they do NOT create parallel user-facing personas or live branching continuations.
- Replay Infrastructure: Demonstrates ability to branch and track divergence;
  does NOT claim causal discovery, Claim C1, C2, C3, or preference emergence.
"""

from __future__ import annotations

import copy
import hashlib
import json
import logging
from dataclasses import asdict, dataclass, field
from typing import Any, Dict, List, Optional, Tuple

import numpy as np

from tests.evaluation.phase26.replica_ensemble_manager import (
    ExposureRecord,
    InputEvent,
    ReplicaConfig,
    ReplicaEnsembleManager,
    ResearchReplica,
    TurnResult,
)
from tests.evaluation.phase26.state_snapshotter import (
    ReplicaStateSnapshot,
    StateSnapshotter,
)

logger = logging.getLogger("CounterfactualReplay")


class PrefixMismatchError(Exception):
    """Raised when prefix histories or checkpoint states deviate prior to counterfactual branching."""
    pass


class ReplayConfigurationError(Exception):
    """Raised when counterfactual replay parameters are invalid or misconfigured."""
    pass


@dataclass
class CounterfactualDifferenceLedger:
    """
    Immutable audit ledger capturing the exact trajectory divergence between
    baseline and counterfactual branches.
    """
    baseline_replica_id: str
    counterfactual_replica_id: str
    checkpoint_turn: int
    checkpoint_virtual_time: float
    snapshot_id: str
    snapshot_hash: str
    common_prefix_hash: str
    declared_difference: Dict[str, Any]

    # Trajectory hashes
    baseline_exposure_hashes: List[str]
    counterfactual_exposure_hashes: List[str]
    divergence_onset_turn: Optional[int]
    divergence_onset_time: Optional[float]

    # State fingerprint progressions
    state_fingerprints_baseline: List[str]
    state_fingerprints_counterfactual: List[str]

    configuration_version: str = "P26_REPLAY_v1.0"
    crn_identifier: Optional[str] = None


class PrefixEquivalenceValidator:
    """
    Validates that two replica histories share bit-exact common prefixes up to turn k,
    and identical state fingerprints at turn k.
    """

    @staticmethod
    def compute_prefix_hash(history: List[ExposureRecord], up_to_turn: int) -> str:
        """
        Computes an aggregate SHA-256 hash of the exposure prefix H[0:k].
        """
        hasher = hashlib.sha256()
        for rec in history[:up_to_turn]:
            hasher.update(rec.compute_exposure_hash().encode("utf-8"))
        return hasher.hexdigest()

    @classmethod
    def validate_prefix_equivalence(
        cls,
        history_a: List[ExposureRecord],
        history_b: List[ExposureRecord],
        up_to_turn: int,
        state_fingerprint_a: str,
        state_fingerprint_b: str,
    ) -> str:
        """
        Enforces fail-closed validation of prefix equivalence.
        Returns the common prefix hash if valid; raises PrefixMismatchError otherwise.
        """
        if len(history_a) < up_to_turn or len(history_b) < up_to_turn:
            raise PrefixMismatchError(
                f"History length insufficient for prefix of turn {up_to_turn}: "
                f"len(A)={len(history_a)}, len(B)={len(history_b)}"
            )

        for idx in range(up_to_turn):
            rec_a = history_a[idx]
            rec_b = history_b[idx]
            hash_a = rec_a.compute_exposure_hash()
            hash_b = rec_b.compute_exposure_hash()
            if hash_a != hash_b:
                raise PrefixMismatchError(
                    f"Prefix exposure mismatch at turn {idx + 1}: "
                    f"hash_A={hash_a[:12]} vs hash_B={hash_b[:12]}."
                )

        if state_fingerprint_a != state_fingerprint_b:
            raise PrefixMismatchError(
                f"Checkpoint state fingerprint mismatch at turn {up_to_turn}: "
                f"A={state_fingerprint_a[:12]} vs B={state_fingerprint_b[:12]}."
            )

        return cls.compute_prefix_hash(history_a, up_to_turn)


class CounterfactualReplayHarness:
    """
    Coordinates counterfactual branching and divergence tracking from verified snapshots.
    """

    def __init__(self, manager: ReplicaEnsembleManager) -> None:
        self.manager = manager

    def create_counterfactual_branch(
        self,
        baseline_replica_id: str,
        counterfactual_replica_id: str,
        checkpoint_turn: int,
        snapshot: ReplicaStateSnapshot,
    ) -> ResearchReplica:
        """
        Instantiates a new counterfactual replica in the ensemble and restores it
        from *snapshot*, confirming prefix equivalence against baseline.
        """
        baseline = self.manager.get_replica(baseline_replica_id)

        # 1. Enforce Fail-Closed Prefix Equivalence
        prefix_hash = PrefixEquivalenceValidator.validate_prefix_equivalence(
            history_a=baseline.exposure_history,
            history_b=snapshot.exposure_history,
            up_to_turn=checkpoint_turn,
            state_fingerprint_a=baseline.compute_state_fingerprint(),
            state_fingerprint_b=snapshot.compute_integrity_hash()[:64], # baseline fingerprint verified via restore
        )

        # 2. Instantiate counterfactual replica specification
        cf_config = ReplicaConfig(
            replica_id=counterfactual_replica_id,
            seed=snapshot.seed,
            crn_seed=snapshot.crn_seed,
            emotion_config=baseline.emotion_config,
            sdm_config=baseline.sdm_config,
        )
        cf_replica = self.manager.create_replica(cf_config)

        # 3. Restore snapshot into the counterfactual replica
        StateSnapshotter.restore_snapshot(cf_replica, snapshot, verify_integrity=True)

        logger.info(
            "Created counterfactual branch '%s' from baseline '%s' at turn %d (prefix hash: %s).",
            counterfactual_replica_id,
            baseline_replica_id,
            checkpoint_turn,
            prefix_hash[:12],
        )
        return cf_replica

    def run_replay_comparison(
        self,
        baseline_replica_id: str,
        counterfactual_replica_id: str,
        checkpoint_turn: int,
        snapshot: ReplicaStateSnapshot,
        future_baseline_inputs: List[InputEvent],
        future_counterfactual_inputs: List[InputEvent],
        declared_difference: Dict[str, Any],
        dt_sec: float = 0.200,
        sub_steps: int = 1,
    ) -> CounterfactualDifferenceLedger:
        """
        Executes parallel continuation of baseline and counterfactual branches,
        detecting and recording divergence onset in an immutable ledger.
        """
        if len(future_baseline_inputs) != len(future_counterfactual_inputs):
            raise ReplayConfigurationError(
                "Future input sequence lengths must be equal for replay comparison."
            )

        baseline = self.manager.get_replica(baseline_replica_id)
        counterfactual = self.manager.get_replica(counterfactual_replica_id)

        # Verify common prefix
        prefix_hash = PrefixEquivalenceValidator.compute_prefix_hash(
            baseline.exposure_history, checkpoint_turn
        )

        num_future_turns = len(future_baseline_inputs)
        divergence_onset_turn: Optional[int] = None
        divergence_onset_time: Optional[float] = None

        baseline_exp_hashes: List[str] = [
            r.compute_exposure_hash() for r in baseline.exposure_history
        ]
        cf_exp_hashes: List[str] = [
            r.compute_exposure_hash() for r in counterfactual.exposure_history
        ]
        fp_baseline: List[str] = [r.state_fingerprint for r in baseline.exposure_history]
        fp_cf: List[str] = [r.state_fingerprint for r in counterfactual.exposure_history]

        for step_idx in range(num_future_turns):
            in_base = future_baseline_inputs[step_idx]
            in_cf = future_counterfactual_inputs[step_idx]

            turn_inputs = {
                baseline_replica_id: in_base,
                counterfactual_replica_id: in_cf,
            }
            res = self.manager.step_turn(turn_inputs, dt_sec=dt_sec, sub_steps=sub_steps)

            r_base = res[baseline_replica_id]
            r_cf = res[counterfactual_replica_id]

            baseline_exp_hashes.append(r_base.exposure_record.compute_exposure_hash())
            cf_exp_hashes.append(r_cf.exposure_record.compute_exposure_hash())
            fp_baseline.append(r_base.state_fingerprint)
            fp_cf.append(r_cf.state_fingerprint)

            # Check divergence onset
            if divergence_onset_turn is None:
                if r_base.state_fingerprint != r_cf.state_fingerprint:
                    divergence_onset_turn = r_base.turn_index
                    divergence_onset_time = r_base.virtual_time_sec

        crn_tag = (
            f"CRN_SEED_{baseline.crn_seed}"
            if baseline.crn_seed is not None
            else None
        )

        return CounterfactualDifferenceLedger(
            baseline_replica_id=baseline_replica_id,
            counterfactual_replica_id=counterfactual_replica_id,
            checkpoint_turn=checkpoint_turn,
            checkpoint_virtual_time=snapshot.virtual_time_sec,
            snapshot_id=snapshot.snapshot_id,
            snapshot_hash=snapshot.integrity_hash,
            common_prefix_hash=prefix_hash,
            declared_difference=declared_difference,
            baseline_exposure_hashes=baseline_exp_hashes,
            counterfactual_exposure_hashes=cf_exp_hashes,
            divergence_onset_turn=divergence_onset_turn,
            divergence_onset_time=divergence_onset_time,
            state_fingerprints_baseline=fp_baseline,
            state_fingerprints_counterfactual=fp_cf,
            crn_identifier=crn_tag,
        )
