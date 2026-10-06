"""
tests/evaluation/phase26/determinism/seeded_sdm_factory.py

Evaluation-Only Seeded SDM Factory for Phase 26.
Ensures deterministic, bit-exact Kanerva Sparse Distributed Memory address spaces.

GOVERNANCE:
- Does NOT modify src/core/memory/sdm.py.
- Resolves the unseeded np.random.default_rng() limitation strictly in test harness.
- Guarantees matched replicas share bit-exact identical hard location coordinates.
"""

from __future__ import annotations

import copy
from typing import Optional

import numpy as np

from src.core.memory.sdm import SDMConfig, SDMCore


class SeededSDMFactory:
    """
    Factory for instantiating SDMCore instances with deterministic address spaces.
    """

    @staticmethod
    def create_seeded_sdm(config: SDMConfig, seed: int = 42) -> SDMCore:
        """
        Create an SDMCore instance with hard locations drawn deterministically from *seed*.
        """
        sdm = SDMCore(config)
        # Deterministically re-generate hard locations using the provided seed
        rng = np.random.default_rng(seed)
        sdm._hard_locs = rng.integers(
            0, 2, size=(sdm._num_locations, sdm._D), dtype=np.uint8
        )
        return sdm

    @staticmethod
    def clone_sdm_topology(source_sdm: SDMCore, config: Optional[SDMConfig] = None) -> SDMCore:
        """
        Create a new, clean SDMCore instance sharing the exact hard location topology
        of *source_sdm*, but with empty memory traces and accumulators.
        """
        cfg = config if config is not None else source_sdm._config
        new_sdm = SDMCore(cfg)
        new_sdm._hard_locs = np.copy(source_sdm._hard_locs)
        return new_sdm
