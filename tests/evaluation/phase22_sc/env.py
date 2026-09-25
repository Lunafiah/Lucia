"""
Simulation Environment Adapter for Phase 22-SC:
Semantic Conditioning & Substrate-Neutral Interface Study.

Reuses the multi-session simulation environment from Phase 22-MR and the
M4 retrieval + G4 gate pipeline from Phase 22-RG.
Produces clean, G4-filtered relational evidence packages for semantic representation
builders without modifying any upstream logic.
"""
from __future__ import annotations
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Dict, List, Tuple

# Reusable upstream imports
sys.path.insert(0, str(Path(__file__).parents[3]))
from tests.evaluation.phase22_mr.config import K_RETRIEVAL
from tests.evaluation.phase22_mr.memory_store import SimulatedSDM, MemoryTrace
from tests.evaluation.phase22_mr.env import MemoryRetrievalEnv, RetrievalScenario
from tests.evaluation.phase22_mr.models import Candidate_M4_HybridFull
from tests.evaluation.phase22_rg.gates import Gate_G4_SafetyFirstHybrid

from .config import STRESS_REGIMES, LANGUAGES, ANCHOR_RELEVANCE_WEIGHTS, MANDATORY_ANCHOR_TYPES


@dataclass
class ScenarioEvaluationData:
    """Packaged scenario evaluation context for semantic conditioning."""
    scenario: RetrievalScenario
    raw_m4_traces: List[MemoryTrace]
    filtered_traces: List[MemoryTrace]
    true_tier: str
    is_guarded: bool
    relevant_ids: List[int]
    mandatory_ids: List[int]


class SemanticConditioningEnv:
    """
    Simulation harness for Phase 22-SC.
    Generates scenarios and runs M4 retrieval followed by G4 relevance gating.
    """
    def __init__(self, seed: int, stress_regime: str, language: str):
        self.seed = seed
        self.stress_regime = stress_regime
        self.language = language

        # Upstream components
        self.mr_env = MemoryRetrievalEnv(seed, stress_regime, language)
        self.m4 = Candidate_M4_HybridFull(k=K_RETRIEVAL)
        self.g4 = Gate_G4_SafetyFirstHybrid(
            pattern_score_threshold=0.30,
            decay_rate=0.35,
            max_weak_ratio=0.10,
            repair_window=2,
        )

    def generate_evaluation_packages(self) -> List[ScenarioEvaluationData]:
        """
        Runs the full upstream pipeline for each scenario:
          1. Generate scenario from MR env
          2. Run M4 retrieval over SDM
          3. Apply G4 gating over retrieved traces
          4. Package filtered relational evidence
        """
        scenarios = self.mr_env.generate_scenarios()
        packages = []

        for sc in scenarios:
            m4_res = self.m4.retrieve(self.mr_env.sdm, sc.query_dict)
            raw_traces = list(m4_res.retrieved)

            g4_res = self.g4.apply(raw_traces, sc.query_dict)
            filtered = list(g4_res.selected)

            true_tier = sc.current_tier
            # Invariant: Guarded stance triggered if rupture_shock is in filtered evidence
            is_guarded = any(t.anchor_type == "rupture_shock" for t in filtered)

            packages.append(ScenarioEvaluationData(
                scenario=sc,
                raw_m4_traces=raw_traces,
                filtered_traces=filtered,
                true_tier=true_tier,
                is_guarded=is_guarded,
                relevant_ids=sc.relevant_trace_ids,
                mandatory_ids=sc.mandatory_trace_ids,
            ))

        return packages
