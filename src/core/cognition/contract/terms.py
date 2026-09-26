"""
src/core/cognition/contract/terms.py

Phase 23-G: Logical Flat Term Store Data Structures.

Strict Invariants:
1. Zero natural-language strings inside terms.
2. All concept, role, entity, scope, and term identifiers are integers.
3. Every INFERRED term carries rule_id and premise references.
4. Support for AMBIGUOUS competing candidate representations.
5. Support for variable binding without string keys.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional, Tuple

from src.core.cognition.contract.epistemic import EpistemicStatus, KleeneValue
from src.core.cognition.contract.provenance import ProvenanceRecord


# Scope type constants (numeric)
SCOPE_TYPE_ROOT = 1
SCOPE_TYPE_NEGATION = 2
SCOPE_TYPE_MODAL = 3
SCOPE_TYPE_INTENSIONAL = 4


@dataclass
class ScopeTerm:
    """
    Language-independent structural scope definition.
    All IDs are purely numeric.
    """
    scope_id: int
    scope_type_id: int = SCOPE_TYPE_ROOT
    parent_scope_id: int = 0  # 0 indicates root or no parent

    def to_dict(self) -> Dict[str, Any]:
        return {
            "scope_id": self.scope_id,
            "scope_type_id": self.scope_type_id,
            "parent_scope_id": self.parent_scope_id,
        }

    @classmethod
    def from_dict(cls, d: Dict[str, Any]) -> ScopeTerm:
        return cls(
            scope_id=int(d["scope_id"]),
            scope_type_id=int(d.get("scope_type_id", SCOPE_TYPE_ROOT)),
            parent_scope_id=int(d.get("parent_scope_id", 0)),
        )


@dataclass
class EntityTerm:
    """
    Language-independent entity referent.
    All IDs are purely numeric.
    """
    entity_id: int
    concept_id: int
    scope_id: int = 1
    epistemic_status: EpistemicStatus = EpistemicStatus.FACT
    alternative_concept_ids: Tuple[int, ...] = ()
    is_active: bool = True
    is_disambiguated: bool = False

    def to_dict(self) -> Dict[str, Any]:
        return {
            "entity_id": self.entity_id,
            "concept_id": self.concept_id,
            "scope_id": self.scope_id,
            "epistemic_status": self.epistemic_status.value,
            "alternative_concept_ids": list(self.alternative_concept_ids),
            "is_active": self.is_active,
            "is_disambiguated": self.is_disambiguated,
        }

    @classmethod
    def from_dict(cls, d: Dict[str, Any]) -> EntityTerm:
        return cls(
            entity_id=int(d["entity_id"]),
            concept_id=int(d["concept_id"]),
            scope_id=int(d.get("scope_id", 1)),
            epistemic_status=EpistemicStatus(d.get("epistemic_status", EpistemicStatus.FACT.value)),
            alternative_concept_ids=tuple(int(x) for x in d.get("alternative_concept_ids", ())),
            is_active=bool(d.get("is_active", True)),
            is_disambiguated=bool(d.get("is_disambiguated", False)),
        )


@dataclass
class LogicalTerm:
    """
    Language-independent flat logical term.
    Represents an n-ary relational assertion or event frame using numeric IDs.
    
    Fields:
        term_id: Unique positive integer identifier for this term.
        predicate_id: Numeric concept identifier for relation / event.
        arg0_id: Numeric entity or term identifier for primary argument.
        arg1_id: Numeric entity or term identifier for secondary argument (0 if none).
        arg2_id: Numeric entity or term identifier for tertiary argument (0 if none).
        role0_id: Numeric semantic role identifier for arg0 (e.g. :ARG0).
        role1_id: Numeric semantic role identifier for arg1 (e.g. :ARG1).
        role2_id: Numeric semantic role identifier for arg2 (0 if none).
        scope_id: Numeric scope container identifier (default 1 for root).
        epistemic_status: Epistemic classification (FACT, INFERRED, AMBIGUOUS, UNKNOWN).
        polarity: Boolean affirmation (True) vs negation (False).
        rule_id: Numeric identifier of inference rule if INFERRED (0 if FACT).
        premise_ids: Tuple of term IDs serving as premises for this inference.
        provenance: Full numeric provenance record.
        is_active: Whether this term is currently valid vs invalidated by non-monotonic retraction.
        is_disambiguated: Whether explicit upstream disambiguation occurred.
        alternative_concept_ids: Competing interpretations if AMBIGUOUS.
    """
    term_id: int
    predicate_id: int
    arg0_id: int
    arg1_id: int = 0
    arg2_id: int = 0
    role0_id: int = 0
    role1_id: int = 0
    role2_id: int = 0
    scope_id: int = 1
    epistemic_status: EpistemicStatus = EpistemicStatus.FACT
    polarity: bool = True
    rule_id: int = 0
    premise_ids: Tuple[int, ...] = ()
    provenance: Optional[ProvenanceRecord] = None
    is_active: bool = True
    is_disambiguated: bool = False
    alternative_concept_ids: Tuple[int, ...] = ()

    def to_dict(self) -> Dict[str, Any]:
        return {
            "term_id": self.term_id,
            "predicate_id": self.predicate_id,
            "arg0_id": self.arg0_id,
            "arg1_id": self.arg1_id,
            "arg2_id": self.arg2_id,
            "role0_id": self.role0_id,
            "role1_id": self.role1_id,
            "role2_id": self.role2_id,
            "scope_id": self.scope_id,
            "epistemic_status": self.epistemic_status.value,
            "polarity": self.polarity,
            "rule_id": self.rule_id,
            "premise_ids": list(self.premise_ids),
            "provenance": self.provenance.to_dict() if self.provenance else None,
            "is_active": self.is_active,
            "is_disambiguated": self.is_disambiguated,
            "alternative_concept_ids": list(self.alternative_concept_ids),
        }

    @classmethod
    def from_dict(cls, d: Dict[str, Any]) -> LogicalTerm:
        prov = ProvenanceRecord.from_dict(d["provenance"]) if d.get("provenance") else None
        return cls(
            term_id=int(d["term_id"]),
            predicate_id=int(d["predicate_id"]),
            arg0_id=int(d["arg0_id"]),
            arg1_id=int(d.get("arg1_id", 0)),
            arg2_id=int(d.get("arg2_id", 0)),
            role0_id=int(d.get("role0_id", 0)),
            role1_id=int(d.get("role1_id", 0)),
            role2_id=int(d.get("role2_id", 0)),
            scope_id=int(d.get("scope_id", 1)),
            epistemic_status=EpistemicStatus(d.get("epistemic_status", EpistemicStatus.FACT.value)),
            polarity=bool(d.get("polarity", True)),
            rule_id=int(d.get("rule_id", 0)),
            premise_ids=tuple(int(p) for p in d.get("premise_ids", ())),
            provenance=prov,
            is_active=bool(d.get("is_active", True)),
            is_disambiguated=bool(d.get("is_disambiguated", False)),
            alternative_concept_ids=tuple(int(x) for x in d.get("alternative_concept_ids", ())),
        )


@dataclass
class BindingSet:
    """
    Numeric variable bindings mapping variable index -> value ID.
    Negative integers (e.g. -1 for ?X, -2 for ?Y) represent variable slots.
    """
    _bindings: Dict[int, int] = field(default_factory=dict)

    def bind(self, var_id: int, val_id: int) -> bool:
        """
        Bind variable var_id to val_id.
        Returns True if successful, False if already bound to a conflicting value.
        """
        existing = self._bindings.get(var_id)
        if existing is not None:
            return existing == val_id
        self._bindings[var_id] = val_id
        return True

    def get(self, var_id: int) -> Optional[int]:
        return self._bindings.get(var_id)

    def clone(self) -> BindingSet:
        return BindingSet(_bindings=dict(self._bindings))

    def clear(self) -> None:
        self._bindings.clear()

    def as_dict(self) -> Dict[int, int]:
        return dict(self._bindings)


@dataclass
class TermQueryPattern:
    """
    Query pattern for retrieving terms from the flat term store.
    Any None field is treated as a wildcard.
    Negative integers represent variable slots to be unified with BindingSet.
    """
    predicate_id: Optional[int] = None
    arg0_id: Optional[int] = None
    arg1_id: Optional[int] = None
    arg2_id: Optional[int] = None
    role0_id: Optional[int] = None
    role1_id: Optional[int] = None
    role2_id: Optional[int] = None
    scope_id: Optional[int] = None
    epistemic_status: Optional[EpistemicStatus] = None
    polarity: Optional[bool] = None
    is_active: Optional[bool] = True

    def matches(self, term: LogicalTerm, bindings: Optional[BindingSet] = None) -> bool:
        """
        Check if term matches this pattern using strictly numeric comparisons.
        Updates bindings if variable slots are present and match succeeds.
        """
        if self.is_active is not None and term.is_active != self.is_active:
            return False
        if self.polarity is not None and term.polarity != self.polarity:
            return False
        if self.epistemic_status is not None and term.epistemic_status != self.epistemic_status:
            return False
        if self.scope_id is not None and term.scope_id != self.scope_id:
            return False

        # Helper to match an ID or variable
        def _match_val(pat_val: Optional[int], term_val: int) -> bool:
            if pat_val is None:
                return True
            if pat_val < 0:
                if bindings is None:
                    return True
                return bindings.bind(pat_val, term_val)
            return pat_val == term_val

        if not _match_val(self.predicate_id, term.predicate_id):
            return False
        if not _match_val(self.arg0_id, term.arg0_id):
            return False
        if not _match_val(self.arg1_id, term.arg1_id):
            return False
        if not _match_val(self.arg2_id, term.arg2_id):
            return False
        if not _match_val(self.role0_id, term.role0_id):
            return False
        if not _match_val(self.role1_id, term.role1_id):
            return False
        if not _match_val(self.role2_id, term.role2_id):
            return False

        return True
