"""
Phase 23-D — EXP-03: V-UMR Coreference Model
Extends UMR-TPG with 32D metric recency coordinates.
"""
from typing import Dict, List, Any
import numpy as np
from .umr_coreference import UMRCoreferenceSubstrate


class VUMRCoreferenceSubstrate(UMRCoreferenceSubstrate):
    """Vector-augmented UMR coreference substrate."""

    def __init__(self):
        super().__init__()
        self.vectors: Dict[str, np.ndarray] = {}

    def run_representation_mode(self, scenario: Dict[str, Any]) -> Dict[str, List[str]]:
        clusters = super().run_representation_mode(scenario)
        # Assign 32D random normal embedding per cluster
        for cid in clusters:
            h = abs(hash(cid)) % (2**32)
            rng = np.random.RandomState(h)
            self.vectors[cid] = rng.normal(0.0, 1.0, size=32)
        return clusters

    def run_resolution_mode(self, scenario: Dict[str, Any]) -> Dict[str, List[str]]:
        clusters = super().run_resolution_mode(scenario)
        for cid in clusters:
            h = abs(hash(cid)) % (2**32)
            rng = np.random.RandomState(h)
            self.vectors[cid] = rng.normal(0.0, 1.0, size=32)
        return clusters
