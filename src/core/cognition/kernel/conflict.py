"""
src/core/cognition/kernel/conflict.py

Phase 23-H: Direct Contradiction and Conflict Detection.

Strict Invariants:
1. P(e) = TRUE and ¬P(e) = TRUE must not silently overwrite each other.
2. Direct contradictions produce an explicit ConflictRecord.
3. No heuristic conflict resolution; no silent recency preference.
4. Purely numeric comparisons; zero string operations.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, Optional

from src.core.cognition.contract.arena import TermArena
from src.core.cognition.contract.terms import LogicalTerm


@dataclass(frozen=True)
class ConflictRecord:
    """
    Record of direct contradiction between two polar assertions:
    P(e) vs ¬P(e).
    """
    predicate_id: int
    arg0_id: int
    arg1_id: int = 0
    arg2_id: int = 0
    existing_term_id: int = 0
    conflicting_term_id: int = 0
    existing_polarity: bool = True
    new_polarity: bool = False

    def to_dict(self) -> Dict[str, object]:
        return {
            "predicate_id": self.predicate_id,
            "arg0_id": self.arg0_id,
            "arg1_id": self.arg1_id,
            "arg2_id": self.arg2_id,
            "existing_term_id": self.existing_term_id,
            "conflicting_term_id": self.conflicting_term_id,
            "existing_polarity": self.existing_polarity,
            "new_polarity": self.new_polarity,
        }


def detect_direct_conflict(
    arena: TermArena,
    predicate_id: int,
    arg0_id: int,
    arg1_id: int = 0,
    arg2_id: int = 0,
    polarity: bool = True,
    scope_id: int = 1,
) -> Optional[ConflictRecord]:
    """
    Inspect arena for an active term with identical predicate and arguments
    but opposite polarity within the same scope.
    
    Returns ConflictRecord if contradiction detected, None otherwise.
    """
    candidate_ids = arena.terms_for_predicate(predicate_id)
    for tid in candidate_ids:
        term = arena.get_term(tid)
        if term is None or not term.is_active:
            continue
        if term.scope_id != scope_id:
            continue
        if (
            term.arg0_id == arg0_id
            and term.arg1_id == arg1_id
            and term.arg2_id == arg2_id
            and term.polarity != polarity
        ):
            return ConflictRecord(
                predicate_id=predicate_id,
                arg0_id=arg0_id,
                arg1_id=arg1_id,
                arg2_id=arg2_id,
                existing_term_id=term.term_id,
                conflicting_term_id=0,
                existing_polarity=term.polarity,
                new_polarity=polarity,
            )
    return None
