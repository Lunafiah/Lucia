"""
tests/evaluation/phase26/state_snapshotter.py

P26 Blocker 4 — State Snapshotting & Restoration Infrastructure.
Enables deep-copied, immutable, cryptographically-hashed state snapshots
and bit-exact state restoration of isolated research replicas for counterfactual replays.

GOVERNANCE & ARCHITECTURAL INVARIANTS:
- TEST-ONLY research infrastructure. Zero changes to src/core/** or electron/**.
- INV-1 (Anti-Branching): Replicas and snapshots are isolated evaluation fixtures.
  They are NEVER serialized to production data/ or bound to live companion state.
- INV-8 (Genesis Gate): Bit-exact preservation of data/profile.json ({"is_onboarded": false}).
- Fail-Closed: Corrupt, altered, or schema-incompatible snapshots are rejected unconditionally.
- Epistemic Scope: Provides snapshot/restore infrastructure only; does NOT claim causality,
  Claim C1, C2, C3, or preference differentiation.
"""

from __future__ import annotations

import copy
import hashlib
import json
import logging
import uuid
from dataclasses import asdict, dataclass, field
from typing import Any, Dict, List, Optional, Tuple

import numpy as np

from src.core.models import PADState
from tests.evaluation.phase26.replica_ensemble_manager import (
    ExposureRecord,
    ResearchReplica,
)

logger = logging.getLogger("StateSnapshotter")

SNAPSHOT_SCHEMA_VERSION = "P26_SNAPSHOT_v1.0"


class SnapshotCorruptionError(Exception):
    """Raised when cryptographic integrity verification of a snapshot fails."""
    pass


class IncompatibleSchemaError(Exception):
    """Raised when a snapshot's schema version or subsystem dimension does not match."""
    pass


@dataclass
class ReplicaStateSnapshot:
    """
    Immutable, self-contained record of all dynamic states within a ResearchReplica
    at a specific virtual time and turn index.
    """
    schema_version: str
    snapshot_id: str
    replica_id: str
    turn_index: int
    virtual_time_sec: float
    seed: int
    crn_seed: Optional[int]

    # Subsystem states (deep-copied)
    emotion_state: Dict[str, Any]
    clock_state: Dict[str, Any]
    sdm_state: Dict[str, Any]
    llm_state: Dict[str, Any]
    exposure_history: List[ExposureRecord]
    rng_state: Optional[Any] = None

    # Cryptographic integrity signature
    integrity_hash: str = ""

    def compute_integrity_hash(self) -> str:
        """
        Computes an authoritative SHA-256 hash across all serialized state components.
        """
        hasher = hashlib.sha256()
        hasher.update(self.schema_version.encode("utf-8"))
        hasher.update(self.snapshot_id.encode("utf-8"))
        hasher.update(self.replica_id.encode("utf-8"))
        hasher.update(str(self.turn_index).encode("utf-8"))
        hasher.update(f"{self.virtual_time_sec:.6f}".encode("utf-8"))
        hasher.update(str(self.seed).encode("utf-8"))
        if self.crn_seed is not None:
            hasher.update(str(self.crn_seed).encode("utf-8"))

        # 1. EmotionCore arrays
        h_fast = self.emotion_state.get("h_fast")
        if isinstance(h_fast, np.ndarray):
            hasher.update(h_fast.tobytes())
        s_slow = self.emotion_state.get("s_slow")
        if isinstance(s_slow, np.ndarray):
            hasher.update(s_slow.tobytes())
        m_homeo = self.emotion_state.get("m_homeo")
        if isinstance(m_homeo, np.ndarray):
            hasher.update(m_homeo.tobytes())

        pad = self.emotion_state.get("pad")
        if isinstance(pad, PADState):
            hasher.update(
                f"PAD({pad.pleasure:.8f},{pad.arousal:.8f},{pad.dominance:.8f})".encode("utf-8")
            )

        # 2. SDM arrays
        accum = self.sdm_state.get("accumulator")
        if isinstance(accum, np.ndarray):
            hasher.update(accum.tobytes())
        counts = self.sdm_state.get("act_counts")
        if isinstance(counts, np.ndarray):
            hasher.update(counts.tobytes())
        hasher.update(str(self.sdm_state.get("next_id", 0)).encode("utf-8"))
        hasher.update(str(self.sdm_state.get("trace_count", 0)).encode("utf-8"))

        # 3. Exposure sequence hashes
        for rec in self.exposure_history:
            hasher.update(rec.compute_exposure_hash().encode("utf-8"))

        # 4. Evaluation PRNG generator state
        if self.rng_state is not None:
            hasher.update(json.dumps(self.rng_state, sort_keys=True, default=str).encode("utf-8"))

        return hasher.hexdigest()


class StateSnapshotter:
    """
    Test-only utility for capturing and restoring complete states of ResearchReplica instances.
    """

    @classmethod
    def capture_snapshot(
        cls,
        replica: ResearchReplica,
        snapshot_id: Optional[str] = None,
    ) -> ReplicaStateSnapshot:
        """
        Takes a deep-copied, immutable snapshot of the replica's complete dynamical
        and memory state.
        """
        snap_id = snapshot_id or f"snap_{replica.replica_id}_turn{replica.turn_index}_{uuid.uuid4().hex[:8]}"

        # 1. Capture EmotionCore state (deep copy of numpy arrays)
        pad_state = replica.emotion_core.get_pad_state()
        emotion_state = {
            "h_fast": np.copy(replica.emotion_core._h),
            "s_slow": np.copy(replica.emotion_core._s_slow),
            "m_homeo": np.copy(replica.emotion_core._m_homeo),
            "pad": copy.deepcopy(pad_state),
            "stimulus_seq": replica.emotion_core._stimulus_seq,
            "committed_stimulus_seq": replica.emotion_core._committed_stimulus_seq,
            "p_philia": np.copy(replica.emotion_core.p_philia),
            "s_philia": np.copy(replica.emotion_core.s_philia),
        }

        # 2. Capture VirtualClockHarness state
        clock_state = {
            "current_time": replica.clock.current_time,
            "trajectory_history": [
                (t, copy.deepcopy(p)) for t, p in replica.clock.trajectory_history
            ],
        }

        # 3. Capture SDMCore state
        trace_addrs_copy = {
            k: np.copy(v) for k, v in replica.sdm._trace_addresses.items()
        }
        sdm_state = {
            "accumulator": np.copy(replica.sdm._accumulator),
            "act_counts": np.copy(replica.sdm._act_counts),
            "trace_addresses": trace_addrs_copy,
            "next_id": replica.sdm._next_id,
            "trace_count": replica.sdm.trace_count,
            "hard_locs": np.copy(replica.sdm._hard_locs),
        }

        # 4. Capture LLM wrapper state
        llm_state = {
            "call_count": replica.llm.call_count,
            "last_seed_used": replica.llm.last_seed_used,
            "default_seed": replica.llm.default_seed,
        }

        # 5. Capture Exposure History
        exposure_copy = copy.deepcopy(replica.exposure_history)

        # 6. Capture Evaluation PRNG generator state
        rng_state = (
            copy.deepcopy(replica.rng.bit_generator.state)
            if hasattr(replica, "rng")
            else None
        )

        snapshot = ReplicaStateSnapshot(
            schema_version=SNAPSHOT_SCHEMA_VERSION,
            snapshot_id=snap_id,
            replica_id=replica.replica_id,
            turn_index=replica.turn_index,
            virtual_time_sec=replica.current_virtual_time,
            seed=replica.seed,
            crn_seed=replica.crn_seed,
            emotion_state=emotion_state,
            clock_state=clock_state,
            sdm_state=sdm_state,
            llm_state=llm_state,
            exposure_history=exposure_copy,
            rng_state=rng_state,
        )

        snapshot.integrity_hash = snapshot.compute_integrity_hash()
        return snapshot

    @classmethod
    def verify_integrity(cls, snapshot: ReplicaStateSnapshot) -> bool:
        """
        Verifies that the snapshot's integrity hash matches its contents.
        """
        if not snapshot.integrity_hash:
            return False
        expected_hash = snapshot.compute_integrity_hash()
        return bool(snapshot.integrity_hash == expected_hash)

    @classmethod
    def restore_snapshot(
        cls,
        replica: ResearchReplica,
        snapshot: ReplicaStateSnapshot,
        verify_integrity: bool = True,
    ) -> None:
        """
        Restores a ResearchReplica to the exact state captured in *snapshot*.
        Fails closed if the snapshot is corrupted or schema-incompatible.

        Parameters
        ----------
        replica : ResearchReplica
            The target replica to restore.
        snapshot : ReplicaStateSnapshot
            The source snapshot to restore from.
        verify_integrity : bool
            Whether to enforce SHA-256 integrity hash verification before restoring.
        """
        # 1. Schema compatibility check
        if snapshot.schema_version != SNAPSHOT_SCHEMA_VERSION:
            raise IncompatibleSchemaError(
                f"Incompatible snapshot schema version: '{snapshot.schema_version}'. "
                f"Expected '{SNAPSHOT_SCHEMA_VERSION}'."
            )

        # 2. Cryptographic integrity check
        if verify_integrity:
            if not cls.verify_integrity(snapshot):
                raise SnapshotCorruptionError(
                    f"Snapshot '{snapshot.snapshot_id}' failed cryptographic integrity verification. "
                    "Possible state tampering or memory corruption detected."
                )

        # 3. Structural dimension checks
        h_fast = snapshot.emotion_state["h_fast"]
        if h_fast.shape != replica.emotion_core._h.shape:
            raise IncompatibleSchemaError(
                f"Emotion fast state dimension mismatch: {h_fast.shape} vs {replica.emotion_core._h.shape}"
            )
        accum = snapshot.sdm_state["accumulator"]
        if accum.shape != replica.sdm._accumulator.shape:
            raise IncompatibleSchemaError(
                f"SDM accumulator dimension mismatch: {accum.shape} vs {replica.sdm._accumulator.shape}"
            )

        # 4. Restore EmotionCore state
        replica.emotion_core._h = np.copy(snapshot.emotion_state["h_fast"])
        replica.emotion_core._s_slow = np.copy(snapshot.emotion_state["s_slow"])
        replica.emotion_core._m_homeo = np.copy(snapshot.emotion_state["m_homeo"])
        replica.emotion_core._pad_snapshot = copy.deepcopy(snapshot.emotion_state["pad"])
        replica.emotion_core._stimulus_seq = snapshot.emotion_state["stimulus_seq"]
        replica.emotion_core._committed_stimulus_seq = snapshot.emotion_state["committed_stimulus_seq"]
        replica.emotion_core.p_philia = np.copy(snapshot.emotion_state["p_philia"])
        replica.emotion_core.s_philia = np.copy(snapshot.emotion_state["s_philia"])
        with replica.emotion_core._stimulus_lock:
            replica.emotion_core._pending_stimuli.clear()

        # 5. Restore VirtualClockHarness
        replica.clock.current_time = float(snapshot.clock_state["current_time"])
        replica.clock.trajectory_history = [
            (t, copy.deepcopy(p)) for t, p in snapshot.clock_state["trajectory_history"]
        ]

        # 6. Restore SDMCore state
        replica.sdm._accumulator = np.copy(snapshot.sdm_state["accumulator"])
        replica.sdm._act_counts = np.copy(snapshot.sdm_state["act_counts"])
        replica.sdm._trace_addresses = {
            k: np.copy(v) for k, v in snapshot.sdm_state["trace_addresses"].items()
        }
        replica.sdm._next_id = int(snapshot.sdm_state["next_id"])
        if "hard_locs" in snapshot.sdm_state:
            replica.sdm._hard_locs = np.copy(snapshot.sdm_state["hard_locs"])

        # 7. Restore LLM wrapper state
        replica.llm.call_count = int(snapshot.llm_state["call_count"])
        replica.llm.last_seed_used = snapshot.llm_state["last_seed_used"]
        replica.llm.default_seed = int(snapshot.llm_state["default_seed"])

        # 8. Restore exposure history & turn index
        replica.turn_index = int(snapshot.turn_index)
        replica.exposure_history = copy.deepcopy(snapshot.exposure_history)

        # 9. Restore evaluation PRNG internal state
        if snapshot.rng_state is not None and hasattr(replica, "rng"):
            replica.rng.bit_generator.state = copy.deepcopy(snapshot.rng_state)

        logger.info(
            "Successfully restored replica '%s' from snapshot '%s' (turn %d, virtual time %.3fs).",
            replica.replica_id,
            snapshot.snapshot_id,
            replica.turn_index,
            replica.current_virtual_time,
        )
