"""
Seeds and Stress Configuration Module for Phase 22-XR.
"""
from dataclasses import dataclass, field
from typing import List, Dict, Any

# Primary Evaluation Seeds
EVAL_SEEDS: List[int] = [42, 137, 618, 1024, 2026]

@dataclass
class StressConfig:
    """Stress testing regime configuration."""
    name: str
    observation_noise: float = 0.05
    lexical_sparsity: float = 0.0
    contradiction_turn: int = -1
    transition_drift: float = 0.0
    description: str = ""

REGIMES: Dict[str, StressConfig] = {
    "ID": StressConfig(
        name="ID",
        observation_noise=0.05,
        lexical_sparsity=0.0,
        contradiction_turn=-1,
        transition_drift=0.0,
        description="In-distribution canonical baseline"
    ),
    "NoiseSurge": StressConfig(
        name="NoiseSurge",
        observation_noise=0.35,
        lexical_sparsity=0.0,
        contradiction_turn=-1,
        transition_drift=0.0,
        description="DS-1: High noise surge on sensory observations"
    ),
    "LexicalSparsity": StressConfig(
        name="LexicalSparsity",
        observation_noise=0.05,
        lexical_sparsity=0.70,
        contradiction_turn=-1,
        transition_drift=0.0,
        description="DS-4: Degraded 1-2 word utterances and ellipses"
    ),
    "ContradictionShock": StressConfig(
        name="ContradictionShock",
        observation_noise=0.05,
        lexical_sparsity=0.0,
        contradiction_turn=15,
        transition_drift=0.0,
        description="DS-3: Ground-truth state reversal at turn 15"
    ),
    "TemporalDrift": StressConfig(
        name="TemporalDrift",
        observation_noise=0.05,
        lexical_sparsity=0.0,
        contradiction_turn=-1,
        transition_drift=0.40,
        description="DS-2: Shift in state transition dynamics"
    ),
    "CombinedStress": StressConfig(
        name="CombinedStress",
        observation_noise=0.30,
        lexical_sparsity=0.50,
        contradiction_turn=15,
        transition_drift=0.30,
        description="DS-Combined: Simultaneous noise, sparsity, shock, and drift"
    ),
}
