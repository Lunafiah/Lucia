"""
tests/evaluation/phase26/replica_ensemble_manager.py

P26 Blocker 2 — Multi-Turn Replica Ensemble Manager.
Provides isolated research replica orchestration, synchronized multi-turn rollouts,
and cryptographic matched-exposure bookkeeping for Phase 26 evaluation harnesses.

GOVERNANCE & ARCHITECTURAL INVARIANTS:
- TEST-ONLY research infrastructure. Zero changes to src/core/** or electron/**.
- INV-1 (Anti-Branching): Research replicas are isolated test fixtures for evaluation only.
  They are NEVER attached to live Lucia lifecycle, Genesis state, or production user data.
- INV-8 (Genesis Gate): Bit-exact preservation of data/profile.json ({"is_onboarded": false}).
- CRN Boundary: Common Random Numbers (CRN) are used strictly as a variance-reduction
  experimental control; CRN does NOT constitute causal identification.
- Epistemic Scope: Solves strictly replica feasibility and exposure bookkeeping.
  Does NOT claim Claim C1, C2, C3, preference, or individuality.
"""

from __future__ import annotations

import copy
import hashlib
import json
import logging
from dataclasses import asdict, dataclass, field
from pathlib import Path
from typing import Any, Dict, List, Optional, Set, Tuple

import numpy as np

from src.core.config import EmotionConfig
from src.core.emotion.emotion_core import EmotionCore
from src.core.memory.sdm import SDMConfig, SDMCore
from src.core.models import BehavioralConstraints, PADState
from tests.evaluation.phase26.determinism.seeded_llm_wrapper import (
    DeterministicMockLLMBackend,
    SeededLLMWrapper,
)
from tests.evaluation.phase26.determinism.seeded_sdm_factory import SeededSDMFactory
from tests.evaluation.phase26.determinism.virtual_clock_harness import VirtualClockHarness

logger = logging.getLogger("ReplicaEnsembleManager")


class ExposureMismatchError(Exception):
    """Raised when exposure histories between replicas deviate from matched criteria."""
    pass


class ReplicaIsolationError(Exception):
    """Raised when memory aliasing or shared mutable state is detected between replicas."""
    pass


@dataclass
class ExposureRecord:
    """
    Immutable ledger entry recording an exact external presentation event to a replica.
    """
    replica_id: str
    seed: int
    turn_index: int
    virtual_time_sec: float
    input_text: Optional[str]
    stimulus_vector: Optional[List[float]]
    order_index: int
    stimulus_metadata: Dict[str, Any]
    state_fingerprint: str
    output_metadata: Dict[str, Any]
    configuration_version: str = "P26_HARNESS_v0.1"
    crn_identifier: Optional[str] = None

    def compute_exposure_hash(self) -> str:
        """
        Cryptographic SHA-256 hash of the presented exposure contents and timing.
        Used to verify bit-exact exposure matching across replicas.
        """
        hasher = hashlib.sha256()
        hasher.update(str(self.turn_index).encode("utf-8"))
        hasher.update(f"{self.virtual_time_sec:.6f}".encode("utf-8"))
        hasher.update(str(self.input_text or "").encode("utf-8"))
        hasher.update(str(self.order_index).encode("utf-8"))
        if self.stimulus_vector is not None:
            formatted_stim = ",".join(f"{v:.6f}" for v in self.stimulus_vector)
            hasher.update(formatted_stim.encode("utf-8"))
        # Deterministically sort metadata keys
        meta_str = json.dumps(self.stimulus_metadata, sort_keys=True)
        hasher.update(meta_str.encode("utf-8"))
        return hasher.hexdigest()


@dataclass
class ReplicaConfig:
    """
    Configuration specification for instantiating a single research replica.
    """
    replica_id: str
    seed: int
    crn_seed: Optional[int] = None
    emotion_config: Optional[EmotionConfig] = None
    sdm_config: Optional[SDMConfig] = None
    sdm_topology_seed: Optional[int] = None
    initial_virtual_time: float = 0.0
    llm_backend: Optional[Any] = None


class ResearchReplica:
    """
    An isolated, reproducible evaluation instance containing distinct limbic,
    memory, clock, and language subsystems.
    """

    def __init__(
        self,
        config: ReplicaConfig,
        shared_sdm_topology: Optional[SDMCore] = None,
    ) -> None:
        self.replica_id = config.replica_id
        self.seed = config.seed
        self.crn_seed = config.crn_seed
        self.turn_index = 0

        # 1. Isolated EmotionCore
        self.emotion_config = config.emotion_config or EmotionConfig()
        self.emotion_core = EmotionCore(self.emotion_config)

        # 2. Isolated VirtualClockHarness
        self.clock = VirtualClockHarness(
            self.emotion_core, initial_time=config.initial_virtual_time
        )

        # 3. Isolated SDMCore
        self.sdm_config = config.sdm_config or SDMConfig(
            num_locations=200, address_dim=128, content_dim=32, capacity=1000
        )
        if shared_sdm_topology is not None:
            # Clone topology (shared coordinates) but isolated memory accumulators
            self.sdm = SeededSDMFactory.clone_sdm_topology(
                shared_sdm_topology, config=self.sdm_config
            )
        else:
            topo_seed = (
                config.sdm_topology_seed
                if config.sdm_topology_seed is not None
                else config.seed
            )
            self.sdm = SeededSDMFactory.create_seeded_sdm(
                self.sdm_config, seed=topo_seed
            )

        # 4. Isolated LLM Wrapper
        backend = config.llm_backend or DeterministicMockLLMBackend()
        self.llm = SeededLLMWrapper(backend, default_seed=config.seed)

        # 5. Internal Stateful Evaluation PRNG Generator
        self.rng: np.random.Generator = np.random.default_rng(config.seed)

        # 6. Exposure History Ledger
        self.exposure_history: List[ExposureRecord] = []

    @property
    def current_virtual_time(self) -> float:
        return self.clock.current_time

    def compute_state_fingerprint(self) -> str:
        """
        Computes an immutable cryptographic SHA-256 fingerprint of the replica's
        internal limbic ODE, PAD coordinates, clock, and memory accumulation state.
        """
        hasher = hashlib.sha256()
        hasher.update(str(self.turn_index).encode("utf-8"))
        hasher.update(f"{self.current_virtual_time:.6f}".encode("utf-8"))

        pad = self.emotion_core.get_pad_state()
        hasher.update(
            f"P:{pad.pleasure:.8f},A:{pad.arousal:.8f},D:{pad.dominance:.8f}".encode("utf-8")
        )

        # Limbic ODE internal states
        hasher.update(self.emotion_core._h_fast.tobytes())
        hasher.update(self.emotion_core._s_slow.tobytes())

        # SDM memory state
        hasher.update(str(self.sdm.trace_count).encode("utf-8"))
        hasher.update(self.sdm._accumulator.tobytes())

        return hasher.hexdigest()

    def record_exposure(
        self,
        input_text: Optional[str],
        stimulus_vector: Optional[np.ndarray],
        order_index: int,
        stimulus_metadata: Dict[str, Any],
        output_metadata: Dict[str, Any],
    ) -> ExposureRecord:
        """
        Appends an exposure event to the replica's immutable audit history.
        """
        stim_list = stimulus_vector.tolist() if stimulus_vector is not None else None
        state_fp = self.compute_state_fingerprint()

        crn_id = f"CRN_SEED_{self.crn_seed}" if self.crn_seed is not None else None

        record = ExposureRecord(
            replica_id=self.replica_id,
            seed=self.seed,
            turn_index=self.turn_index,
            virtual_time_sec=self.current_virtual_time,
            input_text=input_text,
            stimulus_vector=stim_list,
            order_index=order_index,
            stimulus_metadata=dict(stimulus_metadata),
            state_fingerprint=state_fp,
            output_metadata=dict(output_metadata),
            crn_identifier=crn_id,
        )
        self.exposure_history.append(record)
        return record


@dataclass
class InputEvent:
    """
    Representation of an external conversational or sensory stimulus presented to a replica.
    """
    input_text: Optional[str] = None
    stimulus_vector: Optional[np.ndarray] = None
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class TurnResult:
    """
    Result of a single multi-turn execution step for a replica.
    """
    replica_id: str
    turn_index: int
    virtual_time_sec: float
    pad_state: PADState
    attractor_distance: float
    generated_text: Optional[str]
    state_fingerprint: str
    exposure_record: ExposureRecord


@dataclass
class IsolationAuditResult:
    """
    Verification report confirming absence of object aliasing or shared mutable state.
    """
    is_isolated: bool
    num_replicas_checked: int
    aliased_components: List[str] = field(default_factory=list)
    mutation_bleed_detected: bool = False
    details: Dict[str, Any] = field(default_factory=dict)


@dataclass
class EquivalenceValidationReport:
    """
    Detailed audit result confirming whether exposure histories across replicas
    are strictly matched.
    """
    is_matched: bool
    total_turns_evaluated: int
    first_mismatch_turn: Optional[int] = None
    mismatched_replicas: List[str] = field(default_factory=list)
    mismatch_type: Optional[str] = None
    discrepancy_details: Dict[str, Any] = field(default_factory=dict)


class ExposureEquivalenceValidator:
    """
    Test-only validator verifying that exposure histories across replicas
    satisfy matched-exposure criteria.
    """

    @staticmethod
    def validate(
        histories: Dict[str, List[ExposureRecord]],
        allowed_differences: Optional[Dict[str, List[str]]] = None,
    ) -> EquivalenceValidationReport:
        """
        Validates bit-exact matching of exposure histories across replicas.

        Parameters
        ----------
        histories : Dict[str, List[ExposureRecord]]
            Mapping of replica_id to list of ExposureRecords.
        allowed_differences : Optional[Dict[str, List[str]]]
            Keys are turn indices as str; values are allowed divergent fields
            (e.g., {"turn_1": ["input_text"]}).
        """
        if not histories:
            return EquivalenceValidationReport(
                is_matched=True, total_turns_evaluated=0
            )

        replica_ids = sorted(histories.keys())
        first_rep_id = replica_ids[0]
        base_history = histories[first_rep_id]
        total_turns = len(base_history)

        allowed_diffs = allowed_differences or {}

        # 1. Verify identical turn lengths
        for r_id in replica_ids[1:]:
            if len(histories[r_id]) != total_turns:
                return EquivalenceValidationReport(
                    is_matched=False,
                    total_turns_evaluated=min(total_turns, len(histories[r_id])),
                    first_mismatch_turn=min(total_turns, len(histories[r_id])),
                    mismatched_replicas=[first_rep_id, r_id],
                    mismatch_type="TURN_COUNT_MISMATCH",
                    discrepancy_details={
                        "expected_turn_count": total_turns,
                        "observed_turn_count": len(histories[r_id]),
                    },
                )

        # 2. Verify turn-by-turn matched exposure
        for turn_idx in range(total_turns):
            turn_key = f"turn_{turn_idx}"
            allowed_fields = set(allowed_diffs.get(turn_key, []))

            base_rec = base_history[turn_idx]

            for r_id in replica_ids[1:]:
                rec = histories[r_id][turn_idx]

                # Virtual time match
                if "virtual_time_sec" not in allowed_fields:
                    if abs(base_rec.virtual_time_sec - rec.virtual_time_sec) > 1e-9:
                        return EquivalenceValidationReport(
                            is_matched=False,
                            total_turns_evaluated=turn_idx + 1,
                            first_mismatch_turn=turn_idx,
                            mismatched_replicas=[first_rep_id, r_id],
                            mismatch_type="VIRTUAL_TIME_MISMATCH",
                            discrepancy_details={
                                "base_virtual_time": base_rec.virtual_time_sec,
                                "replica_virtual_time": rec.virtual_time_sec,
                            },
                        )

                # Order index match
                if "order_index" not in allowed_fields:
                    if base_rec.order_index != rec.order_index:
                        return EquivalenceValidationReport(
                            is_matched=False,
                            total_turns_evaluated=turn_idx + 1,
                            first_mismatch_turn=turn_idx,
                            mismatched_replicas=[first_rep_id, r_id],
                            mismatch_type="ORDER_INDEX_MISMATCH",
                            discrepancy_details={
                                "base_order": base_rec.order_index,
                                "replica_order": rec.order_index,
                            },
                        )

                # Input text match
                if "input_text" not in allowed_fields:
                    if base_rec.input_text != rec.input_text:
                        return EquivalenceValidationReport(
                            is_matched=False,
                            total_turns_evaluated=turn_idx + 1,
                            first_mismatch_turn=turn_idx,
                            mismatched_replicas=[first_rep_id, r_id],
                            mismatch_type="INPUT_TEXT_MISMATCH",
                            discrepancy_details={
                                "base_input": base_rec.input_text,
                                "replica_input": rec.input_text,
                            },
                        )

                # Stimulus vector match
                if "stimulus_vector" not in allowed_fields:
                    if (base_rec.stimulus_vector is None) != (rec.stimulus_vector is None):
                        return EquivalenceValidationReport(
                            is_matched=False,
                            total_turns_evaluated=turn_idx + 1,
                            first_mismatch_turn=turn_idx,
                            mismatched_replicas=[first_rep_id, r_id],
                            mismatch_type="STIMULUS_PRESENCE_MISMATCH",
                        )
                    if base_rec.stimulus_vector is not None and rec.stimulus_vector is not None:
                        v1 = np.array(base_rec.stimulus_vector)
                        v2 = np.array(rec.stimulus_vector)
                        if not np.allclose(v1, v2, atol=1e-9):
                            return EquivalenceValidationReport(
                                is_matched=False,
                                total_turns_evaluated=turn_idx + 1,
                                first_mismatch_turn=turn_idx,
                                mismatched_replicas=[first_rep_id, r_id],
                                mismatch_type="STIMULUS_VECTOR_MISMATCH",
                                discrepancy_details={
                                    "max_abs_diff": float(np.max(np.abs(v1 - v2)))
                                },
                            )

                # Metadata match
                if "stimulus_metadata" not in allowed_fields:
                    if base_rec.stimulus_metadata != rec.stimulus_metadata:
                        return EquivalenceValidationReport(
                            is_matched=False,
                            total_turns_evaluated=turn_idx + 1,
                            first_mismatch_turn=turn_idx,
                            mismatched_replicas=[first_rep_id, r_id],
                            mismatch_type="METADATA_MISMATCH",
                            discrepancy_details={
                                "base_metadata": base_rec.stimulus_metadata,
                                "replica_metadata": rec.stimulus_metadata,
                            },
                        )

        return EquivalenceValidationReport(
            is_matched=True, total_turns_evaluated=total_turns
        )


class ReplicaEnsembleManager:
    """
    Orchestrates an ensemble of isolated research replicas for multi-turn
    evaluation harnesses under synchronous virtual clocks.
    """

    def __init__(self, shared_sdm_topology_seed: Optional[int] = 42) -> None:
        self.shared_sdm_topology_seed = shared_sdm_topology_seed
        self._shared_topology: Optional[SDMCore] = None
        self._replicas: Dict[str, ResearchReplica] = {}
        self.current_turn = 0

        if shared_sdm_topology_seed is not None:
            # Baseline topology used to ensure replicas have identical address spaces
            dummy_cfg = SDMConfig(
                num_locations=200, address_dim=128, content_dim=32, capacity=1000
            )
            self._shared_topology = SeededSDMFactory.create_seeded_sdm(
                dummy_cfg, seed=shared_sdm_topology_seed
            )

    @property
    def replica_count(self) -> int:
        return len(self._replicas)

    @property
    def replica_ids(self) -> List[str]:
        return sorted(self._replicas.keys())

    def create_replica(self, config: ReplicaConfig) -> ResearchReplica:
        """
        Creates and registers a single isolated research replica.
        """
        if config.replica_id in self._replicas:
            raise ValueError(f"Replica '{config.replica_id}' already exists in ensemble.")

        replica = ResearchReplica(config, shared_sdm_topology=self._shared_topology)
        self._replicas[config.replica_id] = replica
        return replica

    def create_ensemble(self, configs: List[ReplicaConfig]) -> Dict[str, ResearchReplica]:
        """
        Creates and registers a full ensemble of research replicas.
        """
        created = {}
        for cfg in configs:
            created[cfg.replica_id] = self.create_replica(cfg)
        return created

    def get_replica(self, replica_id: str) -> ResearchReplica:
        """
        Retrieves a registered replica by ID.
        """
        if replica_id not in self._replicas:
            raise KeyError(f"Replica '{replica_id}' not found in ensemble.")
        return self._replicas[replica_id]

    def verify_isolation(self) -> IsolationAuditResult:
        """
        Performs an active audit ensuring no object aliasing, shared memory references,
        or cross-replica tensor mutation bleeds exist.
        """
        replicas = list(self._replicas.values())
        n = len(replicas)
        if n < 2:
            return IsolationAuditResult(is_isolated=True, num_replicas_checked=n)

        aliased: List[str] = []
        details: Dict[str, Any] = {}

        # 1. Object Identity Checks
        for i in range(n):
            for j in range(i + 1, n):
                r1 = replicas[i]
                r2 = replicas[j]
                pair_tag = f"{r1.replica_id}_vs_{r2.replica_id}"

                if r1.emotion_core is r2.emotion_core:
                    aliased.append(f"{pair_tag}:emotion_core")
                if r1.clock is r2.clock:
                    aliased.append(f"{pair_tag}:clock")
                if r1.sdm is r2.sdm:
                    aliased.append(f"{pair_tag}:sdm")
                if r1.llm is r2.llm:
                    aliased.append(f"{pair_tag}:llm")

                # Underlying tensor identities
                if r1.emotion_core._h_fast is r2.emotion_core._h_fast:
                    aliased.append(f"{pair_tag}:emotion_fast_state")
                if r1.emotion_core._s_slow is r2.emotion_core._s_slow:
                    aliased.append(f"{pair_tag}:emotion_slow_state")
                if r1.sdm._accumulator is r2.sdm._accumulator:
                    aliased.append(f"{pair_tag}:sdm_accumulator")
                if r1.sdm._act_counts is r2.sdm._act_counts:
                    aliased.append(f"{pair_tag}:sdm_act_counts")

        # 2. Mutation Bleed Test (Non-destructive check on clone/ephemeral vector)
        mutation_bleed = False
        r_first = replicas[0]
        r_second = replicas[1]

        # Snapshot initial states
        orig_fast_second = np.copy(r_second.emotion_core._h_fast)
        orig_accum_second = np.copy(r_second.sdm._accumulator)

        # Mutate first replica's states directly
        r_first.emotion_core._h_fast[0] += 0.5
        r_first.sdm._accumulator[0, 0] += 1.0

        # Check second replica
        if not np.array_equal(r_second.emotion_core._h_fast, orig_fast_second):
            mutation_bleed = True
            aliased.append("mutation_bleed:emotion_fast_state")
        if not np.array_equal(r_second.sdm._accumulator, orig_accum_second):
            mutation_bleed = True
            aliased.append("mutation_bleed:sdm_accumulator")

        # Revert mutation on first replica
        r_first.emotion_core._h_fast[0] -= 0.5
        r_first.sdm._accumulator[0, 0] -= 1.0

        is_isolated = (len(aliased) == 0) and (not mutation_bleed)
        return IsolationAuditResult(
            is_isolated=is_isolated,
            num_replicas_checked=n,
            aliased_components=aliased,
            mutation_bleed_detected=mutation_bleed,
            details=details,
        )

    def step_turn(
        self,
        inputs: Dict[str, InputEvent],
        dt_sec: float = 0.200,
        sub_steps: int = 1,
    ) -> Dict[str, TurnResult]:
        """
        Executes a single synchronized multi-turn step across all replicas.
        Replicas are processed in deterministic alphabetical order by replica_id.

        Parameters
        ----------
        inputs : Dict[str, InputEvent]
            Mapping of replica_id to the specific InputEvent presented to it.
        dt_sec : float
            Virtual clock time delta per sub-step.
        sub_steps : int
            Number of ODE integration steps per turn.
        """
        results: Dict[str, TurnResult] = {}
        target_ids = (
            [r_id for r_id in self.replica_ids if r_id in inputs]
            if inputs
            else self.replica_ids
        )

        for r_id in target_ids:
            replica = self._replicas[r_id]
            replica.turn_index += 1
            event = inputs.get(r_id, InputEvent())

            # 1. Sensory / Stimulus Injection
            if event.stimulus_vector is not None:
                replica.emotion_core.push_stimulus(event.stimulus_vector)

            # 2. Synchronous ODE advancement
            for _ in range(sub_steps):
                pad = replica.clock.step(dt=dt_sec)

            # 3. Optional Language Generation
            generated_text: Optional[str] = None
            if event.input_text:
                # Conditioning with replica-specific or CRN seed
                effective_seed = (
                    replica.crn_seed if replica.crn_seed is not None else replica.seed
                )
                generated_text = replica.llm.generate(
                    event.input_text, seed=effective_seed
                )

            # 4. State capture & exposure recording
            attr_dist = replica.emotion_core.get_attractor_distance()
            out_meta = {
                "generated_text": generated_text,
                "attractor_distance": attr_dist,
            }

            exposure_rec = replica.record_exposure(
                input_text=event.input_text,
                stimulus_vector=event.stimulus_vector,
                order_index=replica.turn_index,
                stimulus_metadata=event.metadata,
                output_metadata=out_meta,
            )

            results[r_id] = TurnResult(
                replica_id=r_id,
                turn_index=replica.turn_index,
                virtual_time_sec=replica.current_virtual_time,
                pad_state=pad,
                attractor_distance=attr_dist,
                generated_text=generated_text,
                state_fingerprint=exposure_rec.state_fingerprint,
                exposure_record=exposure_rec,
            )

        if self._replicas:
            self.current_turn = max(r.turn_index for r in self._replicas.values())

        return results

    def step_identical_turn(
        self,
        event: InputEvent,
        dt_sec: float = 0.200,
        sub_steps: int = 1,
    ) -> Dict[str, TurnResult]:
        """
        Presents an identical InputEvent simultaneously to all replicas.
        """
        identical_inputs = {r_id: event for r_id in self.replica_ids}
        return self.step_turn(identical_inputs, dt_sec=dt_sec, sub_steps=sub_steps)

    def advance_virtual_time(
        self,
        dt_sec: float = 0.200,
        ticks: int = 1,
    ) -> Dict[str, PADState]:
        """
        Advances the virtual clock for all replicas without presenting new external inputs.
        """
        pad_states: Dict[str, PADState] = {}
        for r_id in self.replica_ids:
            replica = self._replicas[r_id]
            for _ in range(ticks):
                pad = replica.clock.step(dt=dt_sec)
            pad_states[r_id] = pad
        return pad_states

    def get_all_exposure_histories(self) -> Dict[str, List[ExposureRecord]]:
        """
        Returns full exposure history lists for all replicas.
        """
        return {r_id: list(rep.exposure_history) for r_id, rep in self._replicas.items()}

    def validate_matched_exposure(
        self,
        allowed_differences: Optional[Dict[str, List[str]]] = None,
    ) -> EquivalenceValidationReport:
        """
        Validates whether all replicas in the ensemble share bit-exact matched exposure.
        """
        histories = self.get_all_exposure_histories()
        return ExposureEquivalenceValidator.validate(
            histories, allowed_differences=allowed_differences
        )

    def teardown(self) -> None:
        """
        Cleanly disposes of all replica instances and resets ensemble state.
        """
        for replica in self._replicas.values():
            replica.exposure_history.clear()
        self._replicas.clear()
        self.current_turn = 0
        logger.info("ReplicaEnsembleManager teardown completed successfully.")
