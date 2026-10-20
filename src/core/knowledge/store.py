"""
src/core/knowledge/store.py

Thread-safe symbolic knowledge repository supporting structured storage, indexed retrieval,
non-destructive contradiction handling, and JSON serialization.
"""

from __future__ import annotations

import json
import logging
import threading
import time
from typing import Any, Dict, List, Optional, Set

from src.core.knowledge.proposition import Concept, InferenceRule, Proposition, ProvenanceType

logger = logging.getLogger(__name__)


class KnowledgeStore:
    """
    Symbolic knowledge repository supporting structured storage, indexed retrieval,
    non-destructive contradiction handling, and thread safety.
    """

    def __init__(self) -> None:
        self._store_lock = threading.RLock()
        self._propositions: Dict[str, Proposition] = {}
        self._concepts: Dict[str, Concept] = {}
        self._rules: Dict[str, InferenceRule] = {}
        self._revision_history: List[Dict[str, Any]] = []
        self._spo_index: Dict[Tuple[str, str, str], str] = {}

    def store_proposition(self, prop: Proposition) -> str:
        """
        Store a proposition in the knowledge store with idempotent (S, P, O) deduplication.
        If an identical valid triple with matching provenance exists, returns the existing ID.
        """
        with self._store_lock:
            if not prop.valid:
                self._propositions[prop.id] = prop
                return prop.id

            key = (prop.subject.strip().lower(), prop.predicate.strip().lower(), prop.object.strip().lower())
            existing_id = self._spo_index.get(key)
            if existing_id is not None and existing_id in self._propositions:
                existing_prop = self._propositions[existing_id]
                if existing_prop.valid:
                    # Idempotent deduplication: identical proposition returns existing_id
                    return existing_id

            self._propositions[prop.id] = prop
            self._spo_index[key] = prop.id
            return prop.id

    def get_proposition(self, prop_id: str) -> Optional[Proposition]:
        with self._store_lock:
            return self._propositions.get(prop_id)

    def get_all_propositions(self) -> List[Proposition]:
        with self._store_lock:
            return list(self._propositions.values())

    def store_concept(self, concept: Concept) -> str:
        with self._store_lock:
            self._concepts[concept.id] = concept
            return concept.id

    def get_concept(self, concept_id: str) -> Optional[Concept]:
        with self._store_lock:
            return self._concepts.get(concept_id)

    def get_all_concepts(self) -> List[Concept]:
        with self._store_lock:
            return list(self._concepts.values())

    def store_rule(self, rule: InferenceRule) -> str:
        with self._store_lock:
            self._rules[rule.id] = rule
            return rule.id

    def get_rule(self, rule_id: str) -> Optional[InferenceRule]:
        with self._store_lock:
            return self._rules.get(rule_id)

    def get_all_rules(self) -> List[InferenceRule]:
        with self._store_lock:
            return list(self._rules.values())

    def get_revision_history(self) -> List[Dict[str, Any]]:
        with self._store_lock:
            return list(self._revision_history)

    def append_revision_history(self, entry: Dict[str, Any]) -> None:
        with self._store_lock:
            self._revision_history.append(entry)

    def query(
        self,
        subject: Optional[str] = None,
        predicate: Optional[str] = None,
        object_: Optional[str] = None,
        valid_only: bool = True,
    ) -> List[Proposition]:
        """
        Query propositions matching (Subject, Predicate, Object) patterns.
        Runs entirely symbolically without LLM invocation.
        """
        with self._store_lock:
            results = []
            for prop in self._propositions.values():
                if valid_only and not prop.valid:
                    continue
                if subject is not None and prop.subject != subject:
                    continue
                if predicate is not None and prop.predicate != predicate:
                    continue
                if object_ is not None and prop.object != object_:
                    continue
                results.append(prop)
            return results

    def query_relevant(self, context_text: str, max_results: int = 5) -> List[Proposition]:
        """
        Retrieve propositions whose subject, predicate, or object appear in context_text.
        Used for bounded, pre-reflective knowledge grounding in CognitiveOrchestrator Stage 8.
        """
        with self._store_lock:
            text_lower = context_text.lower()
            scored_props = []
            for prop in self._propositions.values():
                if not prop.valid:
                    continue
                score = 0.0
                subj_clean = prop.subject.lower().replace("ent:", "")
                obj_clean = prop.object.lower().replace("ent:", "")
                pred_clean = prop.predicate.lower().replace("c:", "")

                if prop.subject.lower() in text_lower or (subj_clean and subj_clean in text_lower):
                    score += 2.0
                if prop.object.lower() in text_lower or (obj_clean and obj_clean in text_lower):
                    score += 1.5
                if prop.predicate.lower() in text_lower or (pred_clean and pred_clean in text_lower):
                    score += 0.5

                if score > 0.0:
                    scored_props.append((score * prop.confidence, prop))

            # Sort descending by score*confidence
            scored_props.sort(key=lambda x: x[0], reverse=True)
            return [p for _, p in scored_props[:max_results]]

    def detect_contradiction(self, candidate: Proposition) -> List[Proposition]:
        """
        Detect existing valid propositions that directly conflict with the candidate.
        For functional/single-valued predicates (e.g. has_color, equals, capital_of),
        differing objects with the same subject and predicate constitute a contradiction.
        """
        single_valued_predicates = {
            "equals", "has_shape", "has_color", "capital_of", "successor_of", "father_of"
        }
        with self._store_lock:
            conflicts = []
            for existing in self._propositions.values():
                if not existing.valid:
                    continue
                if existing.subject == candidate.subject and existing.predicate == candidate.predicate:
                    if existing.predicate in single_valued_predicates and existing.object != candidate.object:
                        conflicts.append(existing)
            return conflicts

    def revise(self, old_prop_id: str, new_prop: Proposition, reason: str = "Verified update") -> str:
        """
        Non-destructive belief revision:
        Marks the old proposition as invalid (CONTRADICTED), links it to the new proposition,
        and preserves full historical provenance without deletion.
        """
        with self._store_lock:
            old_prop = self._propositions.get(old_prop_id)
            if old_prop is None:
                raise KeyError(f"Proposition {old_prop_id} not found for revision")

            old_prop.valid = False
            old_prop.provenance = ProvenanceType.CONTRADICTED
            old_prop.superseded_by = new_prop.id

            new_prop.evidence_ids.append(old_prop_id)
            self._propositions[new_prop.id] = new_prop

            old_key = (old_prop.subject.strip().lower(), old_prop.predicate.strip().lower(), old_prop.object.strip().lower())
            new_key = (new_prop.subject.strip().lower(), new_prop.predicate.strip().lower(), new_prop.object.strip().lower())
            if self._spo_index.get(old_key) == old_prop_id:
                del self._spo_index[old_key]
            if new_prop.valid:
                self._spo_index[new_key] = new_prop.id

            self._revision_history.append({
                "timestamp": time.time(),
                "old_id": old_prop_id,
                "new_id": new_prop.id,
                "reason": reason,
                "previous_tuple": old_prop.to_tuple(),
                "new_tuple": new_prop.to_tuple(),
            })
            return new_prop.id

    def to_json(self) -> str:
        """Serialize complete knowledge graph to JSON string."""
        with self._store_lock:
            data = {
                "propositions": [p.to_dict() for p in self._propositions.values()],
                "concepts": [c.to_dict() for c in self._concepts.values()],
                "rules": [
                    {
                        "id": r.id,
                        "name": r.name,
                        "domain": r.domain,
                        "antecedents": r.antecedents,
                        "consequent_pattern": r.consequent_pattern,
                        "confidence_decay": r.confidence_decay,
                    }
                    for r in self._rules.values()
                ],
                "revision_history": self._revision_history,
            }
            return json.dumps(data, indent=2)

    @classmethod
    def from_json(cls, json_str: str) -> "KnowledgeStore":
        """Deserialize knowledge graph from JSON string."""
        data = json.loads(json_str)
        store = cls()
        for p_dict in data.get("propositions", []):
            prop = Proposition.from_dict(p_dict)
            store._propositions[prop.id] = prop
            if prop.valid:
                key = (prop.subject.strip().lower(), prop.predicate.strip().lower(), prop.object.strip().lower())
                store._spo_index[key] = prop.id
        for c_dict in data.get("concepts", []):
            concept = Concept.from_dict(c_dict)
            store._concepts[concept.id] = concept
        for r_dict in data.get("rules", []):
            rule = InferenceRule(
                id=r_dict["id"],
                name=r_dict["name"],
                domain=r_dict["domain"],
                antecedents=[tuple(a) for a in r_dict["antecedents"]],
                consequent_pattern=tuple(r_dict["consequent_pattern"]),
                confidence_decay=r_dict.get("confidence_decay", 0.95),
            )
            store._rules[rule.id] = rule
        store._revision_history = data.get("revision_history", [])
        return store
