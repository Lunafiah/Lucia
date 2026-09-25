"""Deterministic Dataset Generator for EXP-05: Scaling & Hardware Feasibility.

Generates realistic structured semantic facts at scale (1k, 5k, 10k, 25k, 50k, 100k):
- Entity references (subjects, objects)
- Relational predicates (social, temporal, spatial, preference, organizational)
- Polarity, valid-time intervals, transaction sequence
- Justification/dependency links (1-hop, 2-hop, 3-hop chains)
- Query probes for 1-hop lookup, 3-hop traversal, and belief revision
"""

from __future__ import annotations

import random
from typing import Any, Dict, List, Tuple


PREDICATES = [
    "LOCATED_IN",
    "HOLDS_ROLE",
    "PREFERS_THEME",
    "INTERACTS_WITH",
    "SCHEDULED_FOR",
    "HAS_ATTRIBUTE",
    "MEMBER_OF",
    "AFFILIATED_WITH",
    "COMMUNICATES_VIA",
    "PARTICIPATES_IN",
    "DEPENDS_ON",
    "AUTHOR_OF",
    "ASSIGNED_TO",
    "SPEAKS_LANGUAGE",
    "WORKS_ON",
]

CONCEIVERS = ["User", "LuciaInference", "Admin"]


def generate_scaling_facts(
    n_facts: int,
    seed: int = 42,
) -> Tuple[List[Dict[str, Any]], Dict[str, Any]]:
    """Generates n_facts deterministic semantic assertions and test probes.

    Returns:
        (facts_list, probes_dict)
    """
    rng = random.Random(seed)
    facts: List[Dict[str, Any]] = []

    # Number of distinct entities scales with N to maintain realistic graph density
    n_entities = max(50, n_facts // 20)
    entities = [f"Entity_{i:05d}" for i in range(n_entities)]
    values = [f"Value_{i:04d}" for i in range(max(20, n_facts // 100))]

    # Track facts by subject to build realistic multi-hop chains
    facts_by_subject: Dict[str, List[str]] = {}
    dependency_chains_3hop: List[Tuple[str, str, str, str]] = []  # (root, d1, d2, d3)

    for i in range(n_facts):
        fact_id = f"F_{i:06d}"
        subj = rng.choice(entities)
        pred = rng.choice(PREDICATES)
        # Object can be another entity (for relational hops) or a value
        if rng.random() < 0.6:
            obj = rng.choice(entities)
        else:
            obj = rng.choice(values)

        polarity = rng.random() > 0.05  # 95% positive, 5% negative
        conceiver = rng.choices(CONCEIVERS, weights=[0.70, 0.20, 0.10])[0]

        # Valid time interval
        start_year = rng.randint(2020, 2026)
        end_year = start_year + rng.randint(1, 5)
        valid_time = (float(start_year), float(end_year))

        # Justification / dependency linking
        justifications: List[str] = []
        if i >= 3 and rng.random() < 0.35:
            # Look for recent preceding facts for dependency
            parent_idx = rng.randint(max(0, i - 100), i - 1)
            parent_id = f"F_{parent_idx:06d}"
            justifications.append(parent_id)

            # Check if we can form a 3-hop chain (root -> d1 -> d2 -> d3)
            parent_fact = facts[parent_idx]
            if parent_fact.get("justifications"):
                grandparent_id = parent_fact["justifications"][0]
                gp_idx = int(grandparent_id.split("_")[1])
                gp_fact = facts[gp_idx]
                if gp_fact.get("justifications"):
                    root_id = gp_fact["justifications"][0]
                    dependency_chains_3hop.append((root_id, grandparent_id, parent_id, fact_id))

        fact_entry = {
            "id": fact_id,
            "predicate": pred,
            "subject": subj,
            "arguments": [subj, obj],
            "polarity": polarity,
            "conceiver": conceiver,
            "valid_time": valid_time,
            "tx_time": i + 1,
            "justifications": justifications,
        }
        facts.append(fact_entry)

        if subj not in facts_by_subject:
            facts_by_subject[subj] = []
        facts_by_subject[subj].append(fact_id)

    # Generate representative query probes
    # 1. 1-hop lookups: select 100 existing (subject, predicate) pairs
    sampled_indices = rng.sample(range(n_facts), min(100, n_facts))
    lookup_1hop_probes = [
        {"subject": facts[idx]["subject"], "predicate": facts[idx]["predicate"], "expected_id": facts[idx]["id"]}
        for idx in sampled_indices
    ]

    # 2. 3-hop traversal probes: select up to 50 entities with multiple outgoing edges
    entities_with_edges = [e for e, f_ids in facts_by_subject.items() if len(f_ids) >= 3]
    sampled_entities = rng.sample(entities_with_edges, min(50, len(entities_with_edges)))
    traversal_3hop_probes = [{"start_entity": e} for e in sampled_entities]

    # 3. Contradiction/revision probes: select up to 20 root facts from 3-hop chains
    revision_probes = []
    if dependency_chains_3hop:
        sampled_chains = rng.sample(
            dependency_chains_3hop, min(20, len(dependency_chains_3hop))
        )
        for root_id, d1, d2, d3 in sampled_chains:
            root_idx = int(root_id.split("_")[1])
            root_fact = facts[root_idx]
            revision_probes.append(
                {
                    "root_id": root_id,
                    "dependent_ids": [d1, d2, d3],
                    "contradicting_fact": {
                        "id": f"REV_{root_id}",
                        "predicate": root_fact["predicate"],
                        "subject": root_fact["subject"],
                        "arguments": [root_fact["subject"], f"ContradictingVal_{root_idx}"],
                        "polarity": True,
                        "conceiver": "Admin",  # High authority to trigger defeat
                        "valid_time": root_fact["valid_time"],
                        "tx_time": n_facts + 10,
                        "justifications": [],
                    },
                }
            )

    probes = {
        "lookup_1hop": lookup_1hop_probes,
        "traversal_3hop": traversal_3hop_probes,
        "revision": revision_probes,
    }

    return facts, probes
