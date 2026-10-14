"""
src/core/orchestrator/discourse_cache.py

Production implementation of the Discourse Referent Retention Contract (Phase 23 Gate).
Architecturally ratified via DISCOURSE_REFERENT_RETENTION_RATIFICATION.md.

Invariants:
1. Ownership: Owned strictly by CognitiveOrchestrator / turn coordination layer.
2. Boundedness: Maximum N active referents (provisional N=16). Zero unbounded growth.
3. Determinism: Bit-exact salience decay, threshold eviction, and candidate resolution.
4. Separation of Concerns:
   Reference resolution status (RESOLVED, AMBIGUOUS, UNKNOWN, TYPE_MISMATCH)
   is strictly distinct from Epistemic status (FACT, INFERRED, AMBIGUOUS, UNKNOWN).
   RESOLVED != FACT.
"""

from __future__ import annotations

import hashlib
import json
from dataclasses import asdict, dataclass, field
from enum import Enum
from typing import Any, Dict, List, Optional, Sequence, Tuple


class ResolutionStatus(str, Enum):
    """
    Status of discourse referent resolution across active conversational entities.
    NOTE: Reference resolution state != Epistemic state.
    RESOLVED indicates a referent entity is unambiguously bound in discourse;
    it does NOT imply the proposition concerning that entity is an epistemic FACT.
    """
    RESOLVED = "RESOLVED"
    AMBIGUOUS = "AMBIGUOUS"
    UNKNOWN = "UNKNOWN"
    TYPE_MISMATCH = "TYPE_MISMATCH"


@dataclass(frozen=True)
class DiscourseReferent:
    """
    Represents an active entity referent tracked in discourse context across turns.
    """
    entity_id: str
    concept_id: str
    salience: float
    turn_introduced: int
    last_referenced_turn: int
    grammatical_role: str = ":ARG0"
    gender: Optional[str] = None
    animacy: Optional[str] = None

    def decayed(self, gamma: float) -> DiscourseReferent:
        """Apply deterministic multiplicative exponential decay."""
        return DiscourseReferent(
            entity_id=self.entity_id,
            concept_id=self.concept_id,
            salience=round(self.salience * gamma, 6),
            turn_introduced=self.turn_introduced,
            last_referenced_turn=self.last_referenced_turn,
            grammatical_role=self.grammatical_role,
            gender=self.gender,
            animacy=self.animacy,
        )

    def refreshed(
        self,
        turn: int,
        role: str = ":ARG0",
        boost: float = 1.0,
    ) -> DiscourseReferent:
        """Refresh salience upon being re-mentioned in the current turn."""
        return DiscourseReferent(
            entity_id=self.entity_id,
            concept_id=self.concept_id,
            salience=min(1.0, round(boost, 6)),
            turn_introduced=self.turn_introduced,
            last_referenced_turn=turn,
            grammatical_role=role,
            gender=self.gender,
            animacy=self.animacy,
        )

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


class DiscourseContextCache:
    """
    Lightweight, bounded active referent set for conversational turn linking.
    Owned by CognitiveOrchestrator.
    Enforces O(1) bounded memory and deterministic resolution.
    
    Provisional parameters (ratified under contract):
    - max_capacity: 16
    - decay_gamma: 0.60
    - eviction_threshold: 0.15
    """

    def __init__(
        self,
        max_capacity: int = 16,
        decay_gamma: float = 0.60,
        eviction_threshold: float = 0.15,
    ) -> None:
        self.max_capacity = max_capacity
        self.decay_gamma = decay_gamma
        self.eviction_threshold = eviction_threshold
        self._referents: Dict[str, DiscourseReferent] = {}

    @property
    def count(self) -> int:
        """Current number of active referents."""
        return len(self._referents)

    def get_referent(self, entity_id: str) -> Optional[DiscourseReferent]:
        """Lookup active referent by entity ID."""
        return self._referents.get(entity_id)

    def get_all_referents(self) -> List[DiscourseReferent]:
        """Return all active referents sorted deterministically by entity_id."""
        return [self._referents[k] for k in sorted(self._referents.keys())]

    def clear(self) -> None:
        """Clear all referents (e.g. upon conversation reset / Clear Screen)."""
        self._referents.clear()

    def update_turn(
        self,
        turn_id: int,
        mentioned_referents: Sequence[DiscourseReferent],
    ) -> None:
        """
        End-of-turn lifecycle update:
        1. Decay existing referents by gamma.
        2. Refresh mentioned referents or insert novel ones.
        3. Evict referents falling below eviction_threshold.
        4. Evict lowest salience if exceeding max_capacity (tie-break oldest turn).
        """
        # 1. Decay all existing referents
        new_pool: Dict[str, DiscourseReferent] = {}
        for eid, ref in self._referents.items():
            decayed_ref = ref.decayed(self.decay_gamma)
            if decayed_ref.salience >= self.eviction_threshold:
                new_pool[eid] = decayed_ref

        # 2. Insert or refresh mentioned referents
        for ref in mentioned_referents:
            if ref.entity_id in new_pool:
                existing = new_pool[ref.entity_id]
                new_pool[ref.entity_id] = existing.refreshed(
                    turn=turn_id,
                    role=ref.grammatical_role,
                    boost=1.0,
                )
            else:
                new_pool[ref.entity_id] = ref

        # 3. Capacity enforcement: deterministic eviction of lowest salience
        if len(new_pool) > self.max_capacity:
            sorted_refs = sorted(
                new_pool.values(),
                key=lambda r: (r.salience, r.last_referenced_turn, r.turn_introduced),
            )
            to_remove = len(new_pool) - self.max_capacity
            for i in range(to_remove):
                del new_pool[sorted_refs[i].entity_id]

        self._referents = new_pool

    def resolve_reference(
        self,
        target_role: Optional[str] = None,
        target_gender: Optional[str] = None,
        target_animacy: Optional[str] = None,
        required_concept: Optional[str] = None,
    ) -> Tuple[ResolutionStatus, Optional[str], List[str]]:
        """
        Deterministic reference resolution across active referents.
        Returns: (ResolutionStatus, Optional[resolved_entity_id], List[candidate_ids])

        Resolution Invariant:
        - RESOLVED indicates referent identity in discourse.
        - RESOLVED does NOT imply epistemic FACT.
        """
        candidates: List[DiscourseReferent] = []

        for ref in self._referents.values():
            if required_concept and ref.concept_id != required_concept:
                continue
            if target_animacy and ref.animacy and ref.animacy != target_animacy:
                continue
            if target_gender and ref.gender and ref.gender != target_gender:
                continue
            candidates.append(ref)

        if not candidates:
            # Check if any referent existed in cache but failed type/feature check
            if required_concept or target_animacy or target_gender:
                if len(self._referents) > 0:
                    return ResolutionStatus.TYPE_MISMATCH, None, []
            return ResolutionStatus.UNKNOWN, None, []

        if len(candidates) == 1:
            return ResolutionStatus.RESOLVED, candidates[0].entity_id, [candidates[0].entity_id]

        # Multiple candidates: deterministic ranking
        # 1. Salience score (descending)
        # 2. Role matching target_role (if provided)
        # 3. Recency (last_referenced_turn descending)
        scored_candidates = []
        for c in candidates:
            role_match_score = 1.0 if (target_role and c.grammatical_role == target_role) else 0.0
            score = (round(c.salience, 4), role_match_score, c.last_referenced_turn)
            scored_candidates.append((score, c))

        scored_candidates.sort(key=lambda x: x[0], reverse=True)

        top_score, top_cand = scored_candidates[0]
        runner_up_score, _ = scored_candidates[1]

        # Ambiguity check: if salience, role, and recency are identical
        if top_score == runner_up_score:
            candidate_ids = [c.entity_id for score, c in scored_candidates if score == top_score]
            return ResolutionStatus.AMBIGUOUS, None, candidate_ids

        return ResolutionStatus.RESOLVED, top_cand.entity_id, [top_cand.entity_id]

    def canonical_hash(self) -> str:
        """Bit-exact hash representation of current discourse state."""
        ordered = sorted(self._referents.items(), key=lambda x: x[0])
        serialized = json.dumps(
            [{k: asdict(v)} for k, v in ordered],
            sort_keys=True,
        )
        return hashlib.sha256(serialized.encode("utf-8")).hexdigest()
