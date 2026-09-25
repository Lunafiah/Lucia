"""DRS-Graph Belief Revision Engine (Control Candidate).

Features:
- Discourse Representation Theory (DRT) Box-Universe Conditions
- Box-level accessibility and subordinate implication dependencies
- Formal condition clash detection within accessible discourse universe
- Non-destructive revision with bitemporal box preservation
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional, Set, Tuple

from .umr_belief_revision import AUTHORITY_RANKS


@dataclass
class DRSBoxCondition:
    id: str
    box_id: str
    predicate: str
    arguments: List[str]
    polarity: bool
    conceiver: str
    valid_time: Tuple[float, float]
    tx_time: int
    operational_state: str = "IN"
    justifications: List[str] = field(default_factory=list)
    defeater: Optional[str] = None


class DRSBeliefEngine:
    def __init__(self) -> None:
        self.conditions: Dict[str, DRSBoxCondition] = {}
        self.detected_contradictions: List[Tuple[str, str]] = []
        self.subordinate_links: Dict[str, Set[str]] = {}  # premise -> dependents
        self.box_history: List[Dict[str, Any]] = []

    def _intervals_overlap(
        self, int1: Tuple[float, float], int2: Tuple[float, float]
    ) -> bool:
        start1, end1 = int1
        start2, end2 = int2
        return max(start1, start2) < min(end1, end2)

    def _is_clash(self, c1: DRSBoxCondition, c2: DRSBoxCondition) -> bool:
        if c1.predicate != c2.predicate:
            return False
        if not c1.arguments or not c2.arguments:
            return False
        if c1.arguments[0] != c2.arguments[0]:
            return False
        if not self._intervals_overlap(c1.valid_time, c2.valid_time):
            return False

        # Direct negation
        if c1.arguments == c2.arguments and c1.polarity != c2.polarity:
            return True

        # Mutually exclusive functional property values
        if len(c1.arguments) > 1 and len(c2.arguments) > 1:
            if c1.arguments[1] != c2.arguments[1] and c1.polarity and c2.polarity:
                return True

        return False

    def _propagate_box_invalidation(self, defeated_id: str) -> None:
        queue = [defeated_id]
        visited = {defeated_id}

        while queue:
            curr = queue.pop(0)
            dependents = self.subordinate_links.get(curr, set())
            for dep_id in dependents:
                dep_cond = self.conditions.get(dep_id)
                if dep_cond and dep_cond.operational_state == "IN":
                    dep_cond.operational_state = "OUT"
                    dep_cond.defeater = curr
                    if dep_id not in visited:
                        visited.add(dep_id)
                        queue.append(dep_id)

    def assert_fact(self, data: Dict[str, Any]) -> None:
        cond = DRSBoxCondition(
            id=data["id"],
            box_id=f"B_{data['id']}",
            predicate=data["predicate"],
            arguments=list(data["arguments"]),
            polarity=bool(data["polarity"]),
            conceiver=str(data["conceiver"]),
            valid_time=(float(data["valid_time"][0]), float(data["valid_time"][1])),
            tx_time=int(data["tx_time"]),
            operational_state="IN",
            justifications=list(data.get("justifications", [])),
            defeater=None,
        )

        # Check justifications
        for premise_id in cond.justifications:
            premise = self.conditions.get(premise_id)
            if premise is None or premise.operational_state == "OUT":
                cond.operational_state = "OUT"
                cond.defeater = premise_id
                break

        # Register subordinate dependencies
        for premise_id in cond.justifications:
            if premise_id not in self.subordinate_links:
                self.subordinate_links[premise_id] = set()
            self.subordinate_links[premise_id].add(cond.id)

        # Check clashes in accessible universe
        in_conditions = [
            c for c in self.conditions.values() if c.operational_state == "IN" and c.id != cond.id
        ]

        for existing in in_conditions:
            if self._is_clash(existing, cond):
                self.detected_contradictions.append((existing.id, cond.id))

                rank_existing = AUTHORITY_RANKS.get(existing.conceiver, 50)
                rank_new = AUTHORITY_RANKS.get(cond.conceiver, 50)

                if rank_new >= rank_existing:
                    existing.operational_state = "OUT"
                    existing.defeater = cond.id
                    self._propagate_box_invalidation(existing.id)
                else:
                    cond.operational_state = "OUT"
                    cond.defeater = existing.id
                    self._propagate_box_invalidation(cond.id)
                    break

        self.conditions[cond.id] = cond
        self.box_history.append(
            {
                "tx": cond.tx_time,
                "box_id": cond.box_id,
                "id": cond.id,
                "state": cond.operational_state,
            }
        )

    def get_operational_states(self) -> Dict[str, str]:
        return {c.id: c.operational_state for c in self.conditions.values()}

    def get_history_ids(self) -> Set[str]:
        return set(self.conditions.keys())

    def get_detected_contradictions(self) -> List[Tuple[str, str]]:
        return list(self.detected_contradictions)
