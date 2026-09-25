"""
Phase 23 Semantic Formation Microbenchmark v0.2 — Grounding Engine
Implements Track 2 (U2 associative referential grounding under distractor noise) and
Track 6 (U6 autonomous open-domain concept grounding using contextual similarity).
"""
import time
from typing import Dict, List, Optional, Any, Tuple
import numpy as np
from .config import SemanticNode


class ReferentialGroundingEngine:
    """
    Track 2 (U2): Associative SDM-Style Referential Grounding.
    Retrieves episodic anchors in 64-dimensional continuous vector space
    under distractor noise without exact dictionary lookups.
    """

    def __init__(self, dim: int = 64, seed: int = 42):
        self.dim = dim
        self.rng = np.random.RandomState(seed)
        # SDM Episodic Memory: anchor_id -> {label, vector, session, provenance}
        self.memory_anchors: Dict[str, Dict[str, Any]] = {}
        # Distractor traces in SDM
        self.distractor_vectors: List[np.ndarray] = []

    def register_anchor(self, anchor_id: str, label: str, session: int, vector: np.ndarray) -> None:
        """Registers a canonical episodic anchor vector."""
        v_norm = vector / np.linalg.norm(vector)
        self.memory_anchors[anchor_id] = {
            "label": label,
            "session": session,
            "vector": v_norm,
            "provenance": f"S{session}:turn_anchor_{anchor_id}",
        }

    def populate_distractors(self, count: int = 20) -> None:
        """Populates memory pool with random distractor vectors."""
        self.distractor_vectors = []
        for _ in range(count):
            vec = self.rng.randn(self.dim)
            vec /= np.linalg.norm(vec)
            self.distractor_vectors.append(vec)

    def associative_retrieve(self, query_vector: np.ndarray) -> Tuple[Optional[str], float]:
        """
        Performs nearest-neighbor associative retrieval across memory pool
        (anchors + distractors) using cosine similarity.
        Returns (best_anchor_id, best_similarity).
        """
        q_norm = query_vector / np.linalg.norm(query_vector)
        best_sim = -1.0
        best_anchor = None

        # Compare with true anchors
        for anc_id, data in self.memory_anchors.items():
            sim = float(np.dot(q_norm, data["vector"]))
            if sim > best_sim:
                best_sim = sim
                best_anchor = anc_id

        # Compare with distractors (if a distractor is closer, retrieval fails)
        for dist_vec in self.distractor_vectors:
            dist_sim = float(np.dot(q_norm, dist_vec))
            if dist_sim > best_sim:
                best_sim = dist_sim
                best_anchor = None  # Retrieved a distractor, not a valid anchor

        return best_anchor, best_sim

    def autoassociative_project(self, noisy_vector: np.ndarray, tolerance: float = 0.60) -> np.ndarray:
        """
        SDM auto-associative cleanup: projects noisy representation onto nearest
        memory attractor if similarity exceeds attractor basin tolerance.
        """
        anc_id, sim = self.associative_retrieve(noisy_vector)
        if anc_id is not None and sim >= tolerance:
            # Attractor basin collapses noise toward true episodic anchor
            return np.copy(self.memory_anchors[anc_id]["vector"])
        # Outside basin: unprojected noisy state
        return noisy_vector / np.linalg.norm(noisy_vector)

    def compute_longitudinal_drift(self, anchor_id: str, current_vector: np.ndarray) -> float:
        """Computes Euclidean coordinate displacement against canonical anchor."""
        if anchor_id not in self.memory_anchors:
            return 1.0
        orig_vec = self.memory_anchors[anchor_id]["vector"]
        return float(np.linalg.norm(orig_vec - current_vector))


class AutonomousConceptGrounder:
    """
    Track 6 (U6): Autonomous Open-Domain Concept Grounding on 20W Edge.
    Embeds novel concepts into 32-dimensional contextual space and classifies
    them via nearest centroid similarity to held-out category manifolds.
    """

    def __init__(self, dim: int = 32, seed: int = 42):
        self.dim = dim
        self.rng = np.random.RandomState(seed)
        # Predefined category centroids across held-out domains
        domains = [
            "oncology_pathology",
            "orbital_mechanics",
            "polyphonic_musicology",
            "quantum_spectroscopy",
            "metamaterial_physics",
        ]
        self.category_centroids: Dict[str, np.ndarray] = {}
        for d in domains:
            v = self.rng.randn(self.dim)
            self.category_centroids[d] = v / np.linalg.norm(v)

    def ground_concept_context(self, concept_embedding: np.ndarray) -> Tuple[str, float, float]:
        """
        Classifies novel concept embedding against held-out category centroids.
        Returns (parent_category, confidence, latency_ms).
        """
        t0 = time.perf_counter()
        q = concept_embedding / np.linalg.norm(concept_embedding)
        best_cat = "root_domain"
        best_sim = -1.0

        for cat, centroid in self.category_centroids.items():
            sim = float(np.dot(q, centroid))
            if sim > best_sim:
                best_sim = sim
                best_cat = cat

        latency_ms = (time.perf_counter() - t0) * 1000.0
        confidence = float(np.clip((best_sim + 1.0) / 2.0, 0.0, 1.0))
        return best_cat, confidence, latency_ms


