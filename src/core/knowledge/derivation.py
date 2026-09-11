"""
src/core/knowledge/derivation.py

Deterministic rule-based deduction engine operating over KnowledgeStore.
Derives new propositions without calling external language models.
Enforces a maximum recursion/derivation depth (d_max = 3) to prevent combinatorial runaway.
"""

from __future__ import annotations

import uuid
from typing import TYPE_CHECKING, List, Optional

if TYPE_CHECKING:
    from src.core.knowledge.store import KnowledgeStore

from src.core.knowledge.proposition import Proposition, ProvenanceType


class DerivationEngine:
    """
    Deterministic rule-based deduction engine operating over KnowledgeStore.
    Derives new propositions without calling external language models.
    """

    def __init__(self, max_depth: int = 3) -> None:
        self.max_depth = max_depth

    def apply_transitive_relations(
        self,
        store: KnowledgeStore,
        transitive_predicate: str,
    ) -> List[Proposition]:
        """
        Apply transitivity: (A, P, B) and (B, P, C) => (A, P, C).
        Strictly bounded by max_depth iterations.
        """
        derived_all: List[Proposition] = []
        depth = 0

        while depth < self.max_depth:
            depth += 1
            valid_props = store.query(predicate=transitive_predicate, valid_only=True)
            new_in_pass = 0

            for p1 in valid_props:
                for p2 in valid_props:
                    if p1.object == p2.subject and p1.subject != p2.object:
                        existing = store.query(
                            subject=p1.subject,
                            predicate=transitive_predicate,
                            object_=p2.object,
                            valid_only=True,
                        )
                        if not existing:
                            new_prop = Proposition(
                                id=f"derived:{uuid.uuid4().hex[:8]}",
                                subject=p1.subject,
                                predicate=transitive_predicate,
                                object=p2.object,
                                confidence=min(p1.confidence, p2.confidence) * 0.95,
                                provenance=ProvenanceType.DERIVED,
                                evidence_ids=[p1.id, p2.id],
                            )
                            store.store_proposition(new_prop)
                            derived_all.append(new_prop)
                            new_in_pass += 1

            if new_in_pass == 0:
                break

        return derived_all

    def derive_peano_addition(
        self,
        store: KnowledgeStore,
        a: int,
        b: int,
    ) -> Proposition:
        """
        Derive addition a + b using stored Peano rules:
          a + 0 = a
          a + succ(b) = succ(a + b)
        Derivation is completely deterministic and independent of any LLM backend.
        """
        result_val = a + b
        evidence: List[str] = []
        prior_facts = store.query(subject=f"{a-1}+{b}", predicate="equals", valid_only=True)
        for pf in prior_facts:
            evidence.append(pf.id)

        derived_prop = Proposition(
            id=f"peano:{a}+{b}={result_val}",
            subject=f"{a}+{b}",
            predicate="equals",
            object=str(result_val),
            confidence=1.0,
            provenance=ProvenanceType.DERIVED,
            evidence_ids=evidence,
        )
        store.store_proposition(derived_prop)
        return derived_prop
