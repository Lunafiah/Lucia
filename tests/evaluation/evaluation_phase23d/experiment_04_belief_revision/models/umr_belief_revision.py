"""UMR-TPG Belief Revision Engine (Primary Candidate).

Features:
- Explicit Justification DAG (JTMS)
- Bitemporal Interval Representation (valid_time vs tx_time)
- Operational State Ledger (IN / OUT)
- Deterministic Contradiction Detection
- Recursive Multi-Hop Retraction Propagation
- Immutable Historical Retention (HRR = 1.0)
- Zero Collateral Retraction (CRR = 0.0)
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional, Set, Tuple


AUTHORITY_RANKS: Dict[str, int] = {
    "Admin": 100,
    "BillingSystem": 60,
    "User": 50,
    "LuciaInference": 40,
    "SystemSeed": 30,
    "Guest": 10,
}


@dataclass
class UMAssertion:
    id: str
    predicate: str
    arguments: List[str]
    polarity: bool
    conceiver: str
    valid_time: Tuple[float, float]
    tx_time: int
    operational_state: str = "IN"  # "IN" | "OUT"
    justifications: List[str] = field(default_factory=list)
    defeater: Optional[str] = None


class UMRBeliefEngine:
    def __init__(self) -> None:
        self.ledger: Dict[str, UMAssertion] = {}
        self.tx_history: List[Dict[str, Any]] = []
        self.detected_contradictions: List[Tuple[str, str]] = []
        # premise_id -> set of dependent assertion_ids
        self.dependency_graph: Dict[str, Set[str]] = {}

    def _intervals_overlap(
        self, int1: Tuple[float, float], int2: Tuple[float, float]
    ) -> bool:
        start1, end1 = int1
        start2, end2 = int2
        # Intervals overlap if the intersection is non-empty
        # For open/half-open or closed intervals: max(s1, s2) < min(e1, e2)
        # If [2023, 2024] and [2025, 2026] -> max(2023, 2025)=2025 < min(2024, 2026)=2024 is False
        return max(start1, start2) < min(end1, end2)

    def _is_contradiction(
        self, ast1: UMAssertion, ast2: UMAssertion
    ) -> bool:
        """Determines if two assertions conflict logically or functionally."""
        if ast1.predicate != ast2.predicate:
            return False

        if not ast1.arguments or not ast2.arguments:
            return False

        # Must refer to the same primary subject entity
        if ast1.arguments[0] != ast2.arguments[0]:
            return False

        # Valid-time intervals must overlap
        if not self._intervals_overlap(ast1.valid_time, ast2.valid_time):
            return False

        # Condition 1: Direct negation (same arguments, opposite polarities)
        if ast1.arguments == ast2.arguments and ast1.polarity != ast2.polarity:
            return True

        # Condition 2: Mutually exclusive functional property values
        # e.g., LOCATED_IN(User, DaNang) vs LOCATED_IN(User, Tokyo)
        if len(ast1.arguments) > 1 and len(ast2.arguments) > 1:
            if ast1.arguments[1] != ast2.arguments[1] and ast1.polarity and ast2.polarity:
                return True

        return False

    def _propagate_retraction(self, defeated_id: str) -> None:
        """Recursively propagates retraction to all downstream dependents."""
        queue = [defeated_id]
        visited = {defeated_id}

        while queue:
            curr_id = queue.pop(0)
            dependents = self.dependency_graph.get(curr_id, set())
            for dep_id in dependents:
                dep_ast = self.ledger.get(dep_id)
                if dep_ast and dep_ast.operational_state == "IN":
                    dep_ast.operational_state = "OUT"
                    dep_ast.defeater = curr_id
                    if dep_id not in visited:
                        visited.add(dep_id)
                        queue.append(dep_id)

    def assert_fact(self, data: Dict[str, Any]) -> None:
        """Ingests a new assertion into the bitemporal belief ledger."""
        ast = UMAssertion(
            id=data["id"],
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

        # Check justifications: if any premise is currently OUT, this assertion cannot be IN
        for premise_id in ast.justifications:
            premise = self.ledger.get(premise_id)
            if premise is None or premise.operational_state == "OUT":
                ast.operational_state = "OUT"
                ast.defeater = premise_id
                break

        # Register dependencies
        for premise_id in ast.justifications:
            if premise_id not in self.dependency_graph:
                self.dependency_graph[premise_id] = set()
            self.dependency_graph[premise_id].add(ast.id)

        # Check for contradictions against currently IN assertions
        in_assertions = [
            a for a in self.ledger.values() if a.operational_state == "IN" and a.id != ast.id
        ]

        for existing in in_assertions:
            if self._is_contradiction(existing, ast):
                self.detected_contradictions.append((existing.id, ast.id))

                # Authority resolution
                rank_existing = AUTHORITY_RANKS.get(existing.conceiver, 50)
                rank_new = AUTHORITY_RANKS.get(ast.conceiver, 50)

                if rank_new >= rank_existing:
                    # New assertion defeats existing assertion
                    existing.operational_state = "OUT"
                    existing.defeater = ast.id
                    self._propagate_retraction(existing.id)
                else:
                    # Existing assertion has higher authority; new assertion is defeated
                    ast.operational_state = "OUT"
                    ast.defeater = existing.id
                    self._propagate_retraction(ast.id)
                    break

        # Commit to permanent ledger (historical retention)
        self.ledger[ast.id] = ast
        self.tx_history.append(
            {
                "step": ast.tx_time,
                "action": "ASSERT",
                "id": ast.id,
                "operational_state": ast.operational_state,
                "defeater": ast.defeater,
            }
        )

    def get_operational_states(self) -> Dict[str, str]:
        return {ast.id: ast.operational_state for ast in self.ledger.values()}

    def get_history_ids(self) -> Set[str]:
        return set(self.ledger.keys())

    def get_detected_contradictions(self) -> List[Tuple[str, str]]:
        return list(self.detected_contradictions)
