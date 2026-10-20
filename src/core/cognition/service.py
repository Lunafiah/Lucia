"""
src/core/cognition/service.py

Phase 23-H Bounded Reasoning Substrate Runtime Integration Service.
Implements the EpistemicReasoningService contract specified in:
DOC-P23H-RUNTIME-INTEGRATION-SPEC-R1-001 (Revision 1.1).

Architectural Role:
    Acts as an on-demand cognitive coordinator between Stage S8 Knowledge Retrieval
    and Stage S10b CAPS Proposition Selection.
    
Strict Invariants:
1. Zero dynamic heap allocation in inner reasoning loop (delegates to frozen ReasoningKernel).
2. Ephemeral projection: KnowledgeStore propositions are projected into TermArena
   strictly for the session lifetime without persistent TermIDs.
3. Discrete K3: Operates purely under Strong Kleene 3-valued logic.
4. On-demand execution: Invoked only when an active candidate goal exists.
5. Epistemic qualification: TRUE derivation emits transient DerivedResult (INFERRED),
   NOT automatic ASSERT authorization. Logical truth != conversational assertibility.
6. Invariant NEG-02: Zero scalar confidence thresholding (confidence is never used
   to escalate propositions to FACT).
7. ADR-038 Invariant: KnowledgeStore DERIVED propositions lacking active numeric proof DAGs
   are not certified as INFERRED; they remain UNKNOWN at the kernel boundary.
"""

from __future__ import annotations

import logging
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional, Sequence, Tuple

from src.core.cognition.contract.arena import TermArena
from src.core.cognition.contract.epistemic import EpistemicStatus, KleeneValue
from src.core.cognition.contract.projection import SymbolTable
from src.core.cognition.contract.terms import LogicalTerm
from src.core.cognition.kernel.engine import (
    Goal,
    GoalResult,
    InformationSubgoal,
    ReasoningKernel,
)
from src.core.knowledge.proposition import Proposition, ProvenanceType

logger = logging.getLogger(__name__)


@dataclass(frozen=True)
class DerivedResult:
    """
    Transient derived proposition resulting from deductive goal resolution in P23-H.
    
    Strict Invariants:
    1. Epistemic status is strictly EpistemicStatus.INFERRED (never FACT).
    2. Carries numeric rule_id and premise_ids referencing active terms in TermArena.
    3. Retains symbolic proposition representation for downstream CAPS deliberation.
    4. Ephemeral in-memory only: zero automatic persistence to KnowledgeStore.
    """
    term_id: int
    subject: str
    predicate: str
    object: str
    rule_id: int
    premise_ids: Tuple[int, ...]
    epistemic_status: EpistemicStatus = EpistemicStatus.INFERRED
    polarity: bool = True

    def to_transient_proposition(self) -> Proposition:
        """
        Convert to transient Proposition for AdmissibleEvidencePool in CAPS.
        Never written to disk; remains transient in RAM.
        """
        return Proposition(
            id=f"transient:derived:{self.term_id}",
            subject=self.subject,
            predicate=self.predicate,
            object=self.object,
            confidence=1.0,
            provenance=ProvenanceType.DERIVED,
            evidence_ids=[f"term:{pid}" for pid in self.premise_ids],
            valid=True,
        )


class EpistemicReasoningService:
    """
    On-demand cognitive reasoning coordinator bridging Stage S8 and Stage S10b.
    """

    def __init__(
        self,
        kernel: ReasoningKernel,
        symbol_table: SymbolTable,
        arena: TermArena,
    ) -> None:
        self._kernel = kernel
        self._symbol_table = symbol_table
        self._arena = arena

    @property
    def kernel(self) -> ReasoningKernel:
        return self._kernel

    @property
    def symbol_table(self) -> SymbolTable:
        return self._symbol_table

    @property
    def arena(self) -> TermArena:
        return self._arena

    def project_propositions(
        self,
        propositions: Sequence[Proposition],
    ) -> List[int]:
        """
        Projects admissible propositions from KnowledgeStore into TermArena.
        
        Strict Rules:
        - If not prop.valid or prop.superseded_by is not None: EXCLUDED.
        - confidence is excluded from discrete logic premises (NEG-02).
        - Provenance qualification:
          - VERIFIED / OBSERVED -> EpistemicStatus.FACT
          - USER_STATED -> EpistemicStatus.FACT (spontaneous direct testimony in local scope)
          - DERIVED -> EpistemicStatus.UNKNOWN (per R1.1 § 3.2: lacks active numeric premise DAG)
          - LLM_PROPOSED / UNCERTAIN -> EpistemicStatus.UNKNOWN
          - CONTRADICTED -> EXCLUDED
        - Reuses matching active terms in arena to prevent unbounded slot consumption.
        """
        allocated_ids: List[int] = []
        for prop in propositions:
            if not prop.valid or prop.superseded_by is not None:
                continue

            # Epistemic status mapping under ADR-038 & NEG-02
            if prop.provenance in (ProvenanceType.VERIFIED, ProvenanceType.OBSERVED):
                assigned_status = EpistemicStatus.FACT
            elif prop.provenance == ProvenanceType.USER_STATED:
                assigned_status = EpistemicStatus.FACT
            elif prop.provenance == ProvenanceType.DERIVED:
                # Per R1.1 § 3.2: KnowledgeStore DERIVED without numeric proof graph
                # cannot be certified as INFERRED. Assigned UNKNOWN.
                assigned_status = EpistemicStatus.UNKNOWN
            elif prop.provenance in (ProvenanceType.LLM_PROPOSED, ProvenanceType.UNCERTAIN):
                assigned_status = EpistemicStatus.UNKNOWN
            else:
                # CONTRADICTED or unhandled
                continue

            pred_id = self._symbol_table.intern_concept(prop.predicate)
            a0_id = self._symbol_table.intern_concept(prop.subject)
            a1_id = self._symbol_table.intern_concept(prop.object) if prop.object else 0

            # Check if matching term already exists in arena
            existing = self._find_matching_term(pred_id, a0_id, a1_id, assigned_status)
            if existing is not None:
                allocated_ids.append(existing.term_id)
                continue

            try:
                tid = self._arena.allocate_term(
                    predicate_id=pred_id,
                    arg0_id=a0_id,
                    arg1_id=a1_id,
                    epistemic_status=assigned_status,
                    polarity=True,
                )
                allocated_ids.append(tid)
            except Exception as exc:
                logger.warning("EpistemicReasoningService: failed to allocate term: %s", exc)

        return allocated_ids

    def _find_matching_term(
        self,
        pred_id: int,
        a0_id: int,
        a1_id: int,
        epistemic_status: EpistemicStatus,
        polarity: bool = True,
        scope_id: int = 1,
    ) -> Optional[LogicalTerm]:
        for tid in self._arena.terms_for_predicate(pred_id):
            t = self._arena.get_term(tid)
            if (
                t is not None
                and t.is_active
                and t.arg0_id == a0_id
                and t.arg1_id == a1_id
                and t.polarity == polarity
                and t.scope_id == scope_id
                and t.epistemic_status == epistemic_status
            ):
                return t
        return None

    def verify_candidate_goal(
        self,
        candidate_predicate: Optional[str],
        candidate_subject: Optional[str],
        candidate_object: Optional[str],
        known_propositions: Sequence[Proposition],
        polarity: bool = True,
    ) -> Tuple[GoalResult, Optional[DerivedResult]]:
        """
        Verify a candidate proposition using backward goal-directed reasoning.
        
        Returns:
            (GoalResult, Optional[DerivedResult])
            If candidate_predicate is None: returns (GoalResult(UNKNOWN), None) [Bypass]
        """
        if not candidate_predicate:
            # Bypass reasoning when no candidate Goal exists
            return (
                GoalResult(status=KleeneValue.UNKNOWN),
                None,
            )

        # 1. Project known propositions into arena
        self.project_propositions(known_propositions)

        # 2. Form typed numeric Goal
        pred_id = self._symbol_table.intern_concept(candidate_predicate)
        a0_id = self._symbol_table.intern_concept(candidate_subject) if candidate_subject else 0
        a1_id = self._symbol_table.intern_concept(candidate_object) if candidate_object else 0

        goal = Goal(
            predicate_id=pred_id,
            arg0_id=a0_id,
            arg1_id=a1_id,
            polarity=polarity,
            scope_id=1,
        )

        # 3. Invoke frozen ReasoningKernel
        goal_result = self._kernel.resolve_goal(goal)

        # 4. Handle result
        derived_result = None
        if goal_result.status == KleeneValue.TRUE and goal_result.term_id > 0:
            derived_result = DerivedResult(
                term_id=goal_result.term_id,
                subject=candidate_subject or "",
                predicate=candidate_predicate,
                object=candidate_object or "",
                rule_id=goal_result.rule_id,
                premise_ids=goal_result.premise_ids,
                epistemic_status=EpistemicStatus.INFERRED,
                polarity=polarity,
            )

        return (goal_result, derived_result)
