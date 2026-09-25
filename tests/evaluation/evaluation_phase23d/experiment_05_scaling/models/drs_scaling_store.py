"""DRS-Graph Scaling Semantic Store (Control Candidate).

Features:
- Discourse Representation Theory (DRT) box partitions
- Conditions encapsulated in DRS boxes with structural indirection
- Condition indexing by accessible universe
- Subordinate implication dependency propagation
- Measures structural nesting overhead as hypothesized in H3.
"""

from __future__ import annotations

from typing import Any, Dict, List, Optional, Set, Tuple


class DRSConditionNode:
    __slots__ = (
        "id",
        "box_id",
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
        box_id: str,
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
        self.box_id = box_id
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


class DRSBox:
    __slots__ = ("box_id", "condition_ids", "subordinate_boxes")

    def __init__(self, box_id: str) -> None:
        self.box_id = box_id
        self.condition_ids: List[str] = []
        self.subordinate_boxes: List[str] = []


class DRSScalingStore:
    def __init__(self) -> None:
        self.conditions: Dict[str, DRSConditionNode] = {}
        self.boxes: Dict[str, DRSBox] = {}
        self.subj_pred_index: Dict[Tuple[str, str], List[str]] = {}
        self.entity_out_edges: Dict[str, List[Tuple[str, str, str]]] = {}
        self.subordinate_links: Dict[str, List[str]] = {}  # premise -> dependents

    def insert_fact(self, data: Dict[str, Any]) -> None:
        box_id = f"Box_{data['subject']}"
        if box_id not in self.boxes:
            self.boxes[box_id] = DRSBox(box_id)

        node = DRSConditionNode(
            id=data["id"],
            box_id=box_id,
            predicate=data["predicate"],
            subject=data["subject"],
            arguments=data["arguments"],
            polarity=data["polarity"],
            conceiver=data["conceiver"],
            valid_time=data["valid_time"],
            tx_time=data["tx_time"],
            justifications=data.get("justifications", []),
        )

        self.conditions[node.id] = node
        self.boxes[box_id].condition_ids.append(node.id)

        # 1-hop index
        key = (node.subject, node.predicate)
        if key not in self.subj_pred_index:
            self.subj_pred_index[key] = []
        self.subj_pred_index[key].append(node.id)

        # Relational edges
        if len(node.arguments) > 1:
            obj = node.arguments[1]
            if node.subject not in self.entity_out_edges:
                self.entity_out_edges[node.subject] = []
            self.entity_out_edges[node.subject].append((node.predicate, obj, node.id))

        # Subordinate implication links
        for premise_id in node.justifications:
            if premise_id not in self.subordinate_links:
                self.subordinate_links[premise_id] = []
            self.subordinate_links[premise_id].append(node.id)
            premise = self.conditions.get(premise_id)
            if premise:
                premise.dependents.append(node.id)

    def lookup_1hop(self, subject: str, predicate: str) -> List[DRSConditionNode]:
        """Lookup condition within the subject's box universe."""
        key = (subject, predicate)
        c_ids = self.subj_pred_index.get(key, [])
        return [self.conditions[cid] for cid in c_ids if self.conditions[cid].operational_state == "IN"]

    def traverse_3hop(self, start_entity: str) -> List[str]:
        visited_facts: List[str] = []
        current_entities = {start_entity}

        for _ in range(3):
            next_entities: Set[str] = set()
            for entity in current_entities:
                out_edges = self.entity_out_edges.get(entity, [])
                for _, obj, fact_id in out_edges:
                    node = self.conditions.get(fact_id)
                    if node and node.operational_state == "IN":
                        visited_facts.append(fact_id)
                        next_entities.add(obj)
            current_entities = next_entities
            if not current_entities:
                break

        return visited_facts

    def revise_belief(self, contradicting_data: Dict[str, Any]) -> Dict[str, Any]:
        subj = contradicting_data["subject"]
        pred = contradicting_data["predicate"]
        key = (subj, pred)

        retracted_ids: List[str] = []
        existing_ids = self.subj_pred_index.get(key, [])

        for eid in existing_ids:
            old_node = self.conditions.get(eid)
            if old_node and old_node.operational_state == "IN":
                old_node.operational_state = "OUT"
                old_node.defeater = contradicting_data["id"]
                retracted_ids.append(old_node.id)

                queue = list(self.subordinate_links.get(old_node.id, []))
                visited = set(queue)
                while queue:
                    dep_id = queue.pop(0)
                    dep_node = self.conditions.get(dep_id)
                    if dep_node and dep_node.operational_state == "IN":
                        dep_node.operational_state = "OUT"
                        dep_node.defeater = old_node.id
                        retracted_ids.append(dep_node.id)
                        for next_dep in self.subordinate_links.get(dep_id, []):
                            if next_dep not in visited:
                                visited.add(next_dep)
                                queue.append(next_dep)

        self.insert_fact(contradicting_data)

        return {
            "retracted_count": len(retracted_ids),
            "retracted_ids": retracted_ids,
            "new_fact_id": contradicting_data["id"],
        }

    def count_facts(self) -> int:
        return len(self.conditions)
