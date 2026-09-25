"""V-UMR Belief Revision Engine (Secondary Candidate).

Features:
- Dual-Layer Architecture: Symbolic DAG + Auxiliary 32D Metric Concept Vectors
- Epistemic Invariant: Continuous vector distance/similarity is strictly an auxiliary
  index/representation and is NEVER the authority for determining logical contradiction.
- Full parity with UMR-TPG for state tracking, bitemporal intervals, and JTMS propagation.
"""

from __future__ import annotations

import hashlib
import math
from typing import Any, Dict, List, Optional, Set, Tuple

from .umr_belief_revision import UMAssertion, UMRBeliefEngine


def _generate_32d_vector(seed_str: str) -> List[float]:
    """Generates a deterministic 32-dimensional unit vector from a string."""
    h = hashlib.sha256(seed_str.encode("utf-8")).digest()
    raw = [float(b - 128) / 128.0 for b in h[:32]]
    norm = math.sqrt(sum(x * x for x in raw))
    if norm < 1e-9:
        return [1.0] + [0.0] * 31
    return [x / norm for x in raw]


def _cosine_similarity(v1: List[float], v2: List[float]) -> float:
    return sum(a * b for a, b in zip(v1, v2))


class VUMRBeliefEngine(UMRBeliefEngine):
    def __init__(self) -> None:
        super().__init__()
        # Assertion ID -> 32D auxiliary concept embedding
        self.vector_store: Dict[str, List[float]] = {}
        # Records vector distances calculated during query/indexing
        self.vector_comparisons: List[Dict[str, Any]] = []

    def assert_fact(self, data: Dict[str, Any]) -> None:
        # Generate auxiliary 32D embedding for concept index
        concept_signature = f"{data['predicate']}:{':'.join(data['arguments'])}:{data['polarity']}"
        vector = _generate_32d_vector(concept_signature)
        self.vector_store[data["id"]] = vector

        # Auxiliary vector similarity logging (demonstrating vectors do not dictate truth)
        for existing_id, existing_vec in self.vector_store.items():
            if existing_id != data["id"]:
                sim = _cosine_similarity(vector, existing_vec)
                self.vector_comparisons.append(
                    {
                        "source": data["id"],
                        "target": existing_id,
                        "similarity": round(sim, 4),
                        "used_for_truth": False,  # Explicit structural invariant
                    }
                )

        # Delegate truth-maintenance and contradiction detection strictly to symbolic logic
        super().assert_fact(data)

    def get_vector(self, assertion_id: str) -> Optional[List[float]]:
        return self.vector_store.get(assertion_id)
