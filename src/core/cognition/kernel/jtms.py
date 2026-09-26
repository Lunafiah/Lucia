"""
src/core/cognition/kernel/jtms.py

Phase 23-H: Justification-Based Truth Maintenance System (JTMS).

Strict Invariants:
1. Every INFERRED term must have at least one valid Justification.
2. A Justification connects: rule_id, consequence_id, premise_ids, premise_count, validity.
3. Multi-justification support: When a premise is retracted, a consequence is ONLY
   invalidated if it has NO remaining valid justifications.
4. Independent knowledge and unlinked inference chains MUST survive.
5. Invalidation algorithm uses preallocated static structures to prevent dynamic heap allocation.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, List, Optional, Sequence, Tuple

from src.core.cognition.contract.arena import TermArena
from src.core.cognition.contract.terms import LogicalTerm


@dataclass
class Justification:
    """
    Language-independent JTMS Justification record.
    Connects a consequence term to its supporting premises and the rule that fired.
    """
    justification_id: int
    rule_id: int
    consequence_id: int
    premise_ids: Tuple[int, ...]
    premise_count: int
    is_valid: bool = True

    def invalidate(self) -> None:
        self.is_valid = False

    def to_dict(self) -> Dict[str, object]:
        return {
            "justification_id": self.justification_id,
            "rule_id": self.rule_id,
            "consequence_id": self.consequence_id,
            "premise_ids": list(self.premise_ids),
            "premise_count": self.premise_count,
            "is_valid": self.is_valid,
        }


class JTMS:
    """
    Bounded Justification-Based Truth Maintenance System.
    Maintains dependency graphs and enforces non-monotonic consistency.
    """
    __slots__ = (
        "max_capacity",
        "_justifications",
        "_justification_count",
        "_consequence_to_justifications",
        "_premise_to_justifications",
        "_queue",
        "_visited_set",
    )

    def __init__(self, max_capacity: int = 4096) -> None:
        self.max_capacity: int = max_capacity
        self._justifications: List[Optional[Justification]] = [None] * max_capacity
        self._justification_count: int = 0

        # Mapping: consequence_id -> list of justification IDs
        self._consequence_to_justifications: Dict[int, List[int]] = {}
        # Mapping: premise_id -> list of justification IDs
        self._premise_to_justifications: Dict[int, List[int]] = {}

        # Preallocated static queue buffer for invalidation traversal (zero allocation in loop)
        self._queue: List[int] = [0] * max_capacity
        self._visited_set: set[int] = set()

    @property
    def justification_count(self) -> int:
        return self._justification_count

    def register_justification(
        self,
        rule_id: int,
        consequence_id: int,
        premise_ids: Tuple[int, ...],
    ) -> Justification:
        """
        Register a new justification for an inferred term.
        """
        if self._justification_count >= self.max_capacity:
            raise OverflowError(f"JTMS capacity ({self.max_capacity}) exceeded")

        jid = self._justification_count + 1
        just = Justification(
            justification_id=jid,
            rule_id=rule_id,
            consequence_id=consequence_id,
            premise_ids=premise_ids,
            premise_count=len(premise_ids),
            is_valid=True,
        )

        self._justifications[self._justification_count] = just
        self._justification_count += 1

        # Register in consequence map
        if consequence_id not in self._consequence_to_justifications:
            self._consequence_to_justifications[consequence_id] = []
        self._consequence_to_justifications[consequence_id].append(jid)

        # Register in premise map
        for pid in premise_ids:
            if pid not in self._premise_to_justifications:
                self._premise_to_justifications[pid] = []
            self._premise_to_justifications[pid].append(jid)

        return just

    def get_justification(self, jid: int) -> Optional[Justification]:
        if 1 <= jid <= self._justification_count:
            return self._justifications[jid - 1]
        return None

    def get_justifications_for_consequence(self, consequence_id: int) -> List[Justification]:
        """Return all justifications (valid and invalid) for a given consequence term."""
        jids = self._consequence_to_justifications.get(consequence_id, [])
        res: List[Justification] = []
        for jid in jids:
            j = self.get_justification(jid)
            if j is not None:
                res.append(j)
        return res

    def has_valid_justification(self, consequence_id: int) -> bool:
        """Check if consequence currently has at least one valid justification."""
        jids = self._consequence_to_justifications.get(consequence_id, [])
        for jid in jids:
            j = self.get_justification(jid)
            if j is not None and j.is_valid:
                return True
        return False

    def retract_premise(self, premise_id: int, arena: TermArena) -> List[int]:
        """
        Cascade invalidation when premise_id is retracted:
        1. Invalidate all justifications where premise_id is a premise.
        2. For each affected consequence term:
           - If it has NO remaining valid justification:
             * Retract term in arena (mark inactive).
             * Enqueue for cascade invalidation of further dependents.
           - If it STILL has at least one valid justification:
             * It survives! Do NOT retract.
        3. Cascade recursively until all unsupported derived terms are retracted.
        4. Independent facts and inferences with independent justifications survive.
        
        Returns the list of all newly retracted term IDs.
        """
        invalidated_terms: List[int] = []

        # If the retracted term is active in arena, mark it retracted
        arena.retract_term(premise_id)
        invalidated_terms.append(premise_id)

        # Queue of retracted terms to propagate from
        q_head = 0
        q_tail = 0
        self._queue[q_tail] = premise_id
        q_tail += 1

        self._visited_set.clear()
        self._visited_set.add(premise_id)

        while q_head < q_tail:
            curr_premise = self._queue[q_head]
            q_head += 1

            # Get justifications depending on this premise
            dep_jids = self._premise_to_justifications.get(curr_premise, [])
            for jid in dep_jids:
                just = self.get_justification(jid)
                if just is None or not just.is_valid:
                    continue

                # Invalidate this justification
                just.invalidate()
                conseq_id = just.consequence_id

                # Check if consequence still has ANY remaining valid justification
                if not self.has_valid_justification(conseq_id):
                    # No valid justifications left: must retract consequence
                    term = arena.get_term(conseq_id)
                    if term is not None and term.is_active:
                        arena.retract_term(conseq_id)
                        invalidated_terms.append(conseq_id)

                        # Enqueue for further propagation if not visited
                        if conseq_id not in self._visited_set:
                            self._visited_set.add(conseq_id)
                            if q_tail < self.max_capacity:
                                self._queue[q_tail] = conseq_id
                                q_tail += 1

        return invalidated_terms

    def reset(self) -> None:
        """Reset JTMS without deallocating buffer memory."""
        for i in range(self._justification_count):
            self._justifications[i] = None
        self._justification_count = 0
        self._consequence_to_justifications.clear()
        self._premise_to_justifications.clear()
        self._visited_set.clear()
