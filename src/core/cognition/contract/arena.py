"""
src/core/cognition/contract/arena.py

Phase 23-G: Preallocated Term Arena for Static Memory Management.

Strict Invariants:
1. Zero dynamic allocation in the inner reasoning loop.
2. Fixed-capacity preallocation for terms, entities, and scopes.
3. Explicit error result when capacity is exceeded; NEVER silently truncate.
4. Clean fast retraction and dependency registration without reallocation.
"""

from __future__ import annotations

from typing import Dict, List, Optional, Tuple

from src.core.cognition.contract.epistemic import EpistemicStatus
from src.core.cognition.contract.provenance import ProvenanceRecord
from src.core.cognition.contract.terms import (
    EntityTerm,
    LogicalTerm,
    SCOPE_TYPE_ROOT,
    ScopeTerm,
)


class ArenaCapacityExceededError(Exception):
    """Raised when TermArena capacity is exceeded; prevents silent truncation."""
    pass


class TermArena:
    """
    Preallocated static arena for LogicalTerms, EntityTerms, and ScopeTerms.
    Enforces zero dynamic reallocation in the inner reasoning loop.
    """

    def __init__(
        self,
        max_terms: int = 4096,
        max_entities: int = 2048,
        max_scopes: int = 512,
    ) -> None:
        self.max_terms: int = max_terms
        self.max_entities: int = max_entities
        self.max_scopes: int = max_scopes

        # Preallocated storage slots
        self._term_slots: List[Optional[LogicalTerm]] = [None] * max_terms
        self._entity_slots: List[Optional[EntityTerm]] = [None] * max_entities
        self._scope_slots: List[Optional[ScopeTerm]] = [None] * max_scopes

        self._term_count: int = 0
        self._entity_count: int = 0
        self._scope_count: int = 0

        # Term index lookups: 1-indexed term_id -> slot index (term_id - 1)
        # Fast index: predicate_id -> list of term_ids
        self._predicate_index: Dict[int, List[int]] = {}
        # Forward dependency tracking for cascade invalidation: premise_id -> list of dependent term_ids
        self._dependents: Dict[int, List[int]] = {}

        # Preallocated scratch buffer for matching / queries (zero allocation during query)
        self._match_scratch: List[int] = [0] * max_terms

        # Default root scope (scope_id = 1)
        self.allocate_scope(scope_type_id=SCOPE_TYPE_ROOT, parent_scope_id=0)

    @property
    def term_count(self) -> int:
        return self._term_count

    @property
    def entity_count(self) -> int:
        return self._entity_count

    @property
    def scope_count(self) -> int:
        return self._scope_count

    def allocate_scope(self, scope_type_id: int = SCOPE_TYPE_ROOT, parent_scope_id: int = 0) -> int:
        """Allocate a new scope slot. Returns numeric scope_id (1-indexed)."""
        if self._scope_count >= self.max_scopes:
            raise ArenaCapacityExceededError(
                f"Scope capacity exceeded: {self._scope_count}/{self.max_scopes}"
            )
        scope_id = self._scope_count + 1
        scope = ScopeTerm(
            scope_id=scope_id,
            scope_type_id=scope_type_id,
            parent_scope_id=parent_scope_id,
        )
        self._scope_slots[self._scope_count] = scope
        self._scope_count += 1
        return scope_id

    def allocate_entity(
        self,
        concept_id: int,
        scope_id: int = 1,
        epistemic_status: EpistemicStatus = EpistemicStatus.FACT,
        alternative_concept_ids: Tuple[int, ...] = (),
        is_disambiguated: bool = False,
    ) -> int:
        """Allocate a new entity slot. Returns numeric entity_id (1-indexed)."""
        if self._entity_count >= self.max_entities:
            raise ArenaCapacityExceededError(
                f"Entity capacity exceeded: {self._entity_count}/{self.max_entities}"
            )
        entity_id = self._entity_count + 1
        entity = EntityTerm(
            entity_id=entity_id,
            concept_id=concept_id,
            scope_id=scope_id,
            epistemic_status=epistemic_status,
            alternative_concept_ids=alternative_concept_ids,
            is_active=True,
            is_disambiguated=is_disambiguated,
        )
        self._entity_slots[self._entity_count] = entity
        self._entity_count += 1
        return entity_id

    def allocate_term(
        self,
        predicate_id: int,
        arg0_id: int,
        arg1_id: int = 0,
        arg2_id: int = 0,
        role0_id: int = 0,
        role1_id: int = 0,
        role2_id: int = 0,
        scope_id: int = 1,
        epistemic_status: EpistemicStatus = EpistemicStatus.FACT,
        polarity: bool = True,
        rule_id: int = 0,
        premise_ids: Tuple[int, ...] = (),
        provenance: Optional[ProvenanceRecord] = None,
        is_disambiguated: bool = False,
        alternative_concept_ids: Tuple[int, ...] = (),
    ) -> int:
        """Allocate a new logical term slot. Returns numeric term_id (1-indexed)."""
        if self._term_count >= self.max_terms:
            raise ArenaCapacityExceededError(
                f"LogicalTerm capacity exceeded: {self._term_count}/{self.max_terms}"
            )
        term_id = self._term_count + 1
        term = LogicalTerm(
            term_id=term_id,
            predicate_id=predicate_id,
            arg0_id=arg0_id,
            arg1_id=arg1_id,
            arg2_id=arg2_id,
            role0_id=role0_id,
            role1_id=role1_id,
            role2_id=role2_id,
            scope_id=scope_id,
            epistemic_status=epistemic_status,
            polarity=polarity,
            rule_id=rule_id,
            premise_ids=premise_ids,
            provenance=provenance,
            is_active=True,
            is_disambiguated=is_disambiguated,
            alternative_concept_ids=alternative_concept_ids,
        )
        self._term_slots[self._term_count] = term
        self._term_count += 1

        # Update fast index
        if predicate_id not in self._predicate_index:
            self._predicate_index[predicate_id] = []
        self._predicate_index[predicate_id].append(term_id)

        # Register forward dependencies for JTMS cascade invalidation
        for pid in premise_ids:
            if pid not in self._dependents:
                self._dependents[pid] = []
            self._dependents[pid].append(term_id)

        return term_id

    def get_term(self, term_id: int) -> Optional[LogicalTerm]:
        if 1 <= term_id <= self._term_count:
            return self._term_slots[term_id - 1]
        return None

    def get_entity(self, entity_id: int) -> Optional[EntityTerm]:
        if 1 <= entity_id <= self._entity_count:
            return self._entity_slots[entity_id - 1]
        return None

    def get_scope(self, scope_id: int) -> Optional[ScopeTerm]:
        if 1 <= scope_id <= self._scope_count:
            return self._scope_slots[scope_id - 1]
        return None

    def retract_term(self, term_id: int) -> bool:
        term = self.get_term(term_id)
        if term and term.is_active:
            term.is_active = False
            return True
        return False

    def get_dependents(self, term_id: int) -> List[int]:
        """Return list of term IDs directly justified by this premise term_id."""
        return self._dependents.get(term_id, [])

    def terms_for_predicate(self, predicate_id: int) -> List[int]:
        return self._predicate_index.get(predicate_id, [])

    def active_terms(self) -> List[LogicalTerm]:
        return [
            self._term_slots[i]  # type: ignore[misc]
            for i in range(self._term_count)
            if self._term_slots[i] is not None and self._term_slots[i].is_active  # type: ignore[union-attr]
        ]

    def all_terms(self) -> List[LogicalTerm]:
        return [
            self._term_slots[i]  # type: ignore[misc]
            for i in range(self._term_count)
            if self._term_slots[i] is not None
        ]

    def active_entities(self) -> List[EntityTerm]:
        return [
            self._entity_slots[i]  # type: ignore[misc]
            for i in range(self._entity_count)
            if self._entity_slots[i] is not None and self._entity_slots[i].is_active  # type: ignore[union-attr]
        ]

    def all_entities(self) -> List[EntityTerm]:
        return [
            self._entity_slots[i]  # type: ignore[misc]
            for i in range(self._entity_count)
            if self._entity_slots[i] is not None
        ]

    def all_scopes(self) -> List[ScopeTerm]:
        return [
            self._scope_slots[i]  # type: ignore[misc]
            for i in range(self._scope_count)
            if self._scope_slots[i] is not None
        ]

    def get_match_scratch_slice(self, length: int) -> List[int]:
        """Return preallocated match scratch buffer slice without memory allocation."""
        return self._match_scratch[:length]

    def reset(self) -> None:
        """Reset arena without deallocating buffer memory."""
        for i in range(self._term_count):
            self._term_slots[i] = None
        for i in range(self._entity_count):
            self._entity_slots[i] = None
        for i in range(self._scope_count):
            self._scope_slots[i] = None

        self._term_count = 0
        self._entity_count = 0
        self._scope_count = 0
        self._predicate_index.clear()
        self._dependents.clear()

        # Re-add default root scope
        self.allocate_scope(scope_type_id=SCOPE_TYPE_ROOT, parent_scope_id=0)
