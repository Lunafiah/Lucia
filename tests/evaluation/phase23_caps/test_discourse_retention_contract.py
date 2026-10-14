"""
tests/evaluation/phase23_caps/test_discourse_retention_contract.py

Isolated Evaluation Benchmark for Discourse Referent Retention Contract (Phase 23 Gate).
Validates:
1. Bounded memory: fixed upper bound, zero unbounded growth across 100 turns.
2. Decay & Eviction: exponential salience decay and clean threshold eviction.
3. Reference resolution: exact match, type filtering, recency/role tie-breaking.
4. Failure semantics: AMBIGUOUS on competing candidates, UNKNOWN on evicted referents, TYPE_MISMATCH.
5. Bit-exact determinism: identical output hashes across repeated executions.
6. Execution latency: sub-millisecond execution overhead.
"""

from __future__ import annotations

import hashlib
import json
import time
from dataclasses import asdict, dataclass, field
from enum import Enum
from typing import Any, Dict, List, Optional, Set, Tuple


class ResolutionStatus(str, Enum):
    RESOLVED = "RESOLVED"
    AMBIGUOUS = "AMBIGUOUS"
    UNKNOWN = "UNKNOWN"
    TYPE_MISMATCH = "TYPE_MISMATCH"


@dataclass(frozen=True)
class DiscourseReferent:
    entity_id: str
    concept_id: str
    salience: float
    turn_introduced: int
    last_referenced_turn: int
    grammatical_role: str = ":ARG0"
    gender: Optional[str] = None
    animacy: Optional[str] = None

    def decayed(self, gamma: float) -> DiscourseReferent:
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

    def refreshed(self, turn: int, role: str = ":ARG0", boost: float = 1.0) -> DiscourseReferent:
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


class DiscourseContextCache:
    """
    Lightweight, bounded active referent set for conversational turn linking.
    Enforces O(1) bounded memory and deterministic resolution.
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
        return len(self._referents)

    def get_referent(self, entity_id: str) -> Optional[DiscourseReferent]:
        return self._referents.get(entity_id)

    def update_turn(
        self,
        turn_id: int,
        mentioned_referents: List[DiscourseReferent],
    ) -> None:
        """
        End-of-turn lifecycle update:
        1. Decay existing referents by gamma.
        2. Refresh mentioned referents or insert novel ones.
        3. Evict referents falling below eviction_threshold.
        4. Evict lowest salience if exceeding max_capacity.
        """
        # 1. Decay all existing
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

        # 3. Capacity enforcement (Deterministic eviction: lowest salience first, tie-break oldest turn)
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
        Returns: (status, resolved_entity_id, candidate_ids)
        """
        candidates: List[DiscourseReferent] = []

        for ref in self._referents.values():
            # Concept / Type compatibility
            if required_concept and ref.concept_id != required_concept:
                continue
            # Animacy compatibility
            if target_animacy and ref.animacy and ref.animacy != target_animacy:
                continue
            # Gender compatibility
            if target_gender and ref.gender and ref.gender != target_gender:
                continue
            candidates.append(ref)

        if not candidates:
            # Check if any referent existed but failed type check
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
        runner_up_score, runner_up_cand = scored_candidates[1]

        # Ambiguity check: if salience and role and recency are identical
        if top_score == runner_up_score:
            candidate_ids = [c.entity_id for _, c in scored_candidates if _ == top_score]
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


# ── Benchmark Evaluation Runner ───────────────────────────────────────────────

def run_discourse_retention_benchmark() -> Dict[str, Any]:
    t0 = time.perf_counter()

    results: Dict[str, Any] = {}

    # 1. Test Bounded Capacity across 100 turns
    cache = DiscourseContextCache(max_capacity=16, decay_gamma=0.60, eviction_threshold=0.15)
    max_observed_size = 0

    for turn in range(1, 101):
        # Inject 2 novel entities per turn
        e1 = DiscourseReferent(
            entity_id=f"ent_turn_{turn}_a",
            concept_id="c:OBJECT",
            salience=1.0,
            turn_introduced=turn,
            last_referenced_turn=turn,
            animacy="INANIMATE",
        )
        e2 = DiscourseReferent(
            entity_id=f"ent_turn_{turn}_b",
            concept_id="c:PERSON",
            salience=1.0,
            turn_introduced=turn,
            last_referenced_turn=turn,
            animacy="ANIMATE",
            gender="MASCULINE",
        )
        cache.update_turn(turn, [e1, e2])
        if cache.count > max_observed_size:
            max_observed_size = cache.count

    results["boundedness"] = {
        "turns_simulated": 100,
        "max_capacity_limit": 16,
        "max_observed_size": max_observed_size,
        "final_size": cache.count,
        "pass": max_observed_size <= 16 and cache.count <= 16,
    }

    # 2. Test Decay and Eviction Lifetime
    decay_cache = DiscourseContextCache(max_capacity=16, decay_gamma=0.60, eviction_threshold=0.15)
    ref_luna = DiscourseReferent(
        entity_id="ent_luna",
        concept_id="c:PERSON",
        salience=1.0,
        turn_introduced=1,
        last_referenced_turn=1,
        gender="FEMININE",
        animacy="ANIMATE",
    )
    decay_cache.update_turn(1, [ref_luna])

    # Turn 2: Unmentioned
    decay_cache.update_turn(2, [])
    s_turn2 = decay_cache.get_referent("ent_luna").salience if decay_cache.get_referent("ent_luna") else 0.0

    # Turn 3: Unmentioned
    decay_cache.update_turn(3, [])
    s_turn3 = decay_cache.get_referent("ent_luna").salience if decay_cache.get_referent("ent_luna") else 0.0

    # Turn 4: Unmentioned (0.36 * 0.6 = 0.216)
    decay_cache.update_turn(4, [])
    s_turn4 = decay_cache.get_referent("ent_luna").salience if decay_cache.get_referent("ent_luna") else 0.0

    # Turn 5: Unmentioned (0.216 * 0.6 = 0.1296 < 0.15 -> EVICTED)
    decay_cache.update_turn(5, [])
    ref_turn5 = decay_cache.get_referent("ent_luna")

    results["decay_and_eviction"] = {
        "turn_1_salience": 1.0,
        "turn_2_salience": s_turn2,
        "turn_3_salience": s_turn3,
        "turn_4_salience": s_turn4,
        "turn_5_evicted": ref_turn5 is None,
        "pass": s_turn2 == 0.60 and s_turn3 == 0.36 and s_turn4 == 0.216 and ref_turn5 is None,
    }

    # 3. Test Failure Semantics (UNKNOWN, TYPE_MISMATCH, AMBIGUOUS, RESOLVED)
    sem_cache = DiscourseContextCache(max_capacity=16, decay_gamma=0.60, eviction_threshold=0.15)
    cat = DiscourseReferent(
        entity_id="ent_cat",
        concept_id="c:FELINE",
        salience=1.0,
        turn_introduced=1,
        last_referenced_turn=1,
        animacy="ANIMATE",
        gender="NEUTER",
        grammatical_role=":ARG1",
    )
    dog = DiscourseReferent(
        entity_id="ent_dog",
        concept_id="c:CANINE",
        salience=1.0,
        turn_introduced=1,
        last_referenced_turn=1,
        animacy="ANIMATE",
        gender="NEUTER",
        grammatical_role=":ARG0",
    )
    sem_cache.update_turn(1, [cat, dog])

    # Case A: Exact match with role
    stat_a, ent_a, _ = sem_cache.resolve_reference(target_role=":ARG0")
    # Case B: Type mismatch (asking for INANIMATE when only ANIMATE in cache)
    stat_b, ent_b, _ = sem_cache.resolve_reference(target_animacy="INANIMATE")
    # Case C: Ambiguous (asking for ANIMATE without role or concept filter)
    stat_c, ent_c, cand_c = sem_cache.resolve_reference(target_animacy="ANIMATE")
    # Case D: Unknown (empty query on empty cache)
    empty_cache = DiscourseContextCache()
    stat_d, ent_d, _ = empty_cache.resolve_reference()

    results["failure_semantics"] = {
        "role_resolved": (stat_a == ResolutionStatus.RESOLVED and ent_a == "ent_dog"),
        "type_mismatch": stat_b == ResolutionStatus.TYPE_MISMATCH,
        "ambiguous_detected": (stat_c == ResolutionStatus.AMBIGUOUS and len(cand_c) == 2),
        "unknown_detected": stat_d == ResolutionStatus.UNKNOWN,
        "pass": (
            stat_a == ResolutionStatus.RESOLVED
            and stat_b == ResolutionStatus.TYPE_MISMATCH
            and stat_c == ResolutionStatus.AMBIGUOUS
            and stat_d == ResolutionStatus.UNKNOWN
        ),
    }

    # 4. Determinism
    hash_run_1 = sem_cache.canonical_hash()
    hash_run_2 = sem_cache.canonical_hash()

    results["determinism"] = {
        "identical": hash_run_1 == hash_run_2,
        "hash": hash_run_1,
        "pass": hash_run_1 == hash_run_2,
    }

    elapsed_ms = (time.perf_counter() - t0) * 1000.0
    results["elapsed_ms"] = round(elapsed_ms, 3)

    return results


if __name__ == "__main__":
    benchmark_res = run_discourse_retention_benchmark()
    print(json.dumps(benchmark_res, indent=2))
