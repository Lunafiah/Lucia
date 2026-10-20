"""
src/core/cognition/qualification.py

Phase 23-D: Trigger Qualification Boundary.
Implements the deterministic, stateless qualification filter specified in
DOC-P23D-IMP-SPEC-V1-001 §6.

Strict Invariants:
1. Rejection of Level 1 (Maintenance Dynamics: ODE, decay, LNN trainer) from waking cognition.
2. Rejection of Level 2 (Latent transformation: continuous PAD drift) from waking cognition.
3. User turn priority: orchestrator busy state defers the trigger immediately.
4. Anti-cascading depth = 1: secondary triggers generated during endogenous cycles are deferred.
5. Suppression check: conditions in SUPPRESSED or RESOLVED states cannot qualify.
6. Pure, stateless logic: NOT an event bus, broker, or background scheduler daemon.
"""

from __future__ import annotations

import hashlib
from dataclasses import dataclass, field
from typing import Any, Dict, Optional, Tuple

from src.core.cognition.contract.condition import (
    ConditionStatus,
    ConditionType,
    ResolutionSource,
    UnresolvedCondition,
)
from src.core.cognition.referent_adapter import compute_condition_id


@dataclass(frozen=True)
class CandidateTrigger:
    """Raw, unqualified candidate trigger emitted by an internal substrate."""
    source_subsystem: str         # e.g. "ReasoningKernel", "KnowledgeStore", "RelationshipUpdater"
    taxonomy_level: int           # 1 (Maintenance) | 2 (Latent) | 3 (Epistemic) | 4 (Comm)
    referent_key: str             # Canonical encoded referent string
    condition_type: ConditionType # MISSING_PREMISE | CONTRADICTION | RELATIONAL_RUPTURE
    epoch: int
    payload: Dict[str, Any] = field(default_factory=dict)


@dataclass(frozen=True)
class QualifiedEndogenousTrigger:
    """Vetted, authorized trigger permitted to enter process_endogenous()."""
    trigger_id: str               # Deterministic SHA-256 hash
    condition_id: str             # Linked UnresolvedCondition ID
    condition_type: ConditionType
    referent_key: str
    resolution_source: ResolutionSource
    epoch: int


class TriggerQualificationBoundary:
    """
    Stateless boundary filter evaluating candidate triggers against project taxonomies
    and concurrency invariants.
    """

    @staticmethod
    def qualify(
        candidate: CandidateTrigger,
        condition_ledger: Dict[str, UnresolvedCondition],
        is_orchestrator_busy: bool,
        active_endogenous_depth: int = 0,
    ) -> Tuple[bool, Optional[QualifiedEndogenousTrigger], str]:
        """
        Evaluate candidate trigger. Returns (qualified: bool, trigger: Optional[QualifiedEndogenousTrigger], reason: str).
        """
        # 1. Level-1 Rejection Invariant (Maintenance dynamics NEVER wake cognition)
        if candidate.taxonomy_level == 1:
            return False, None, "REJECTED_LEVEL_1_MAINTENANCE_DYNAMICS"

        # 2. Level-2 Rejection Invariant (Latent transformation is context-only)
        if candidate.taxonomy_level == 2:
            return False, None, "REJECTED_LEVEL_2_CONTEXT_MODULATION_ONLY"

        # 3. Concurrency Check (User turn takes absolute priority)
        if is_orchestrator_busy:
            return False, None, "DEFERRED_ORCHESTRATOR_BUSY"

        # 4. Anti-Cascading Invariant (Max endogenous depth = 1)
        if active_endogenous_depth >= 1:
            return False, None, "DEFERRED_MAX_CASCADE_DEPTH_REACHED"

        # 5. Condition Reference & Status Verification
        expected_cond_id = compute_condition_id(candidate.condition_type, candidate.referent_key)
        condition = condition_ledger.get(expected_cond_id)

        if condition is not None:
            if condition.status == ConditionStatus.SUPPRESSED:
                return False, None, "REJECTED_CONDITION_SUPPRESSED"
            if condition.status == ConditionStatus.RESOLVED:
                return False, None, "REJECTED_CONDITION_ALREADY_RESOLVED"
            res_source = condition.resolution_source
        else:
            # First-time registration of condition
            res_source = (
                ResolutionSource.INTERNAL_SEARCH
                if candidate.condition_type != ConditionType.RELATIONAL_RUPTURE
                else ResolutionSource.EXTERNAL_USER
            )

        # 6. Build deterministic qualified trigger
        trig_payload = f"trigger:{candidate.epoch}:{expected_cond_id}".encode("utf-8")
        trig_id = hashlib.sha256(trig_payload).hexdigest()

        qualified = QualifiedEndogenousTrigger(
            trigger_id=trig_id,
            condition_id=expected_cond_id,
            condition_type=candidate.condition_type,
            referent_key=candidate.referent_key,
            resolution_source=res_source,
            epoch=candidate.epoch,
        )
        return True, qualified, "QUALIFIED"
