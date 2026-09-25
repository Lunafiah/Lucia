"""UMR-TPG Scaling Semantic Store (Primary Candidate).

Features:
- Concept node graph using __slots__ for minimal memory overhead
- O(1) hash-based 1-hop indexing by (subject, predicate)
- Multi-hop adjacency traversal
- Localized JTMS dependency retraction
- Invariant: Zero GPU VRAM impact (100% CPU edge execution)
"""

from __future__ import annotations

from typing import Any, Dict, List, Optional, Set, Tuple


class UMRFactNode:
    __slots__ = (
        "id",
        "predicate",
        "subject",
        "arguments",
        "polarity",
        "conceiver",
        "valid_time",
        "tx_time",
        "operational_state",
        "justifications",
        "dependents",
        "defeater",
    )

    def __init__(
        self,
        id: str,
        predicate: str,
        subject: str,
        arguments: List[str],
        polarity: bool,
        conceiver: str,
        valid_time: Tuple[float, float],
        tx_time: int,
        justifications: List[str],
    ) -> None:
        self.id = id
        self.predicate = predicate
        self.subject = subject
        self.arguments = arguments
        self.polarity = polarity
        self.conceiver = conceiver
        self.valid_time = valid_time
        self.tx_time = tx_time
        self.operational_state = "IN"
        self.justifications = justifications
        self.dependents: List[str] = []
        self.defeater: Optional[str] = None


class UMRScalingStore:
    def __init__(self) -> None:
        self.facts: Dict[str, UMRFactNode] = {}
        # (subject, predicate) -> list of fact IDs
        self.subj_pred_index: Dict[Tuple[str, str], List[str]] = {}
        # subject -> list of (predicate, object_entity, fact_id)
        self.entity_out_edges: Dict[str, List[Tuple[str, str, str]]] = {}
        # premise_id -> list of dependent fact_ids
        self.dependency_graph: Dict[str, List[str]] = {}

    def insert_fact(self, data: Dict[str, Any]) -> None:
        node = UMRFactNode(
            id=data["id"],
            predicate=data["predicate"],
            subject=data["subject"],
            arguments=data["arguments"],
            polarity=data["polarity"],
            conceiver=data["conceiver"],
            valid_time=data["valid_time"],
            tx_time=data["tx_time"],
            justifications=data.get("justifications", []),
        )

        self.facts[node.id] = node

        # 1-hop index
        key = (node.subject, node.predicate)
        if key not in self.subj_pred_index:
            self.subj_pred_index[key] = []
        self.subj_pred_index[key].append(node.id)

        # Out-edges for multi-hop graph traversal
        if len(node.arguments) > 1:
            obj = node.arguments[1]
            if node.subject not in self.entity_out_edges:
                self.entity_out_edges[node.subject] = []
            self.entity_out_edges[node.subject].append((node.predicate, obj, node.id))

        # Dependency graph registration
        for premise_id in node.justifications:
            if premise_id not in self.dependency_graph:
                self.dependency_graph[premise_id] = []
            self.dependency_graph[premise_id].append(node.id)
            premise_node = self.facts.get(premise_id)
            if premise_node:
                premise_node.dependents.append(node.id)

    def lookup_1hop(self, subject: str, predicate: str) -> List[UMRFactNode]:
        """O(1) semantic role lookup."""
        key = (subject, predicate)
        fact_ids = self.subj_pred_index.get(key, [])
        return [self.facts[fid] for fid in fact_ids if self.facts[fid].operational_state == "IN"]

    def traverse_3hop(self, start_entity: str) -> List[str]:
        """3-hop relational traversal starting from start_entity."""
        visited_facts: List[str] = []
        current_entities = {start_entity}

        for _ in range(3):
            next_entities: Set[str] = set()
            for entity in current_entities:
                out_edges = self.entity_out_edges.get(entity, [])
                for _, obj, fact_id in out_edges:
                    node = self.facts.get(fact_id)
                    if node and node.operational_state == "IN":
                        visited_facts.append(fact_id)
                        next_entities.add(obj)
            current_entities = next_entities
            if not current_entities:
                break

        return visited_facts

    def revise_belief(self, contradicting_data: Dict[str, Any]) -> Dict[str, Any]:
        """Detects contradiction against existing fact, retracts premise & propagates across DAG."""
        subj = contradicting_data["subject"]
        pred = contradicting_data["predicate"]
        key = (subj, pred)

        retracted_ids: List[str] = []
        existing_ids = self.subj_pred_index.get(key, [])

        for eid in existing_ids:
            old_node = self.facts.get(eid)
            if old_node and old_node.operational_state == "IN":
                # Contradiction: old premise becomes OUT
                old_node.operational_state = "OUT"
                old_node.defeater = contradicting_data["id"]
                retracted_ids.append(old_node.id)

                # Propagate retraction across downstream dependency DAG
                queue = list(self.dependency_graph.get(old_node.id, []))
                visited = set(queue)
                while queue:
                    dep_id = queue.pop(0)
                    dep_node = self.facts.get(dep_id)
                    if dep_node and dep_node.operational_state == "IN":
                        dep_node.operational_state = "OUT"
                        dep_node.defeater = old_node.id
                        retracted_ids.append(dep_node.id)
                        for next_dep in self.dependency_graph.get(dep_id, []):
                            if next_dep not in visited:
                                visited.add(next_dep)
                                queue.append(next_dep)

        # Ingest the new winning assertion
        self.insert_fact(contradicting_data)

        return {
            "retracted_count": len(retracted_ids),
            "retracted_ids": retracted_ids,
            "new_fact_id": contradicting_data["id"],
        }

    def count_facts(self) -> int:
        return len(self.facts)
