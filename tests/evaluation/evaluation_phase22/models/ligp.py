"""
tests/evaluation_phase22/models/ligp.py

Local Expected Information Gain Proxy (LIGP).
Evaluates prospective information gain without LLM meta-prompting,
without PAD variance terms, and completely decoupled from prediction surprise S_t.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, Optional

from tests.evaluation_phase22.models.actions import ActionType


@dataclass(frozen=True)
class LIGPConfig:
    """Configurable weights for knowledge and memory information gain."""
    w_k: float = 1.0  # Weight on propositional knowledge entropy reduction
    w_m: float = 1.0  # Weight on associative memory competition entropy reduction

    def __post_init__(self) -> None:
        if self.w_k < 0.0 or self.w_m < 0.0:
            raise ValueError("LIGP weights must be non-negative.")


def compute_expected_information_gain(
    action: ActionType,
    delta_h_knowledge: float,
    delta_h_memory: float,
    config: Optional[LIGPConfig] = None,
) -> float:
    """
    Compute Local Expected Information Gain:
    EIG(a) = w_k * ΔH_Knowledge(a) + w_m * ΔH_Memory(a)

    Where an action does not affect a substrate, its contribution is strictly zero:
    - a1: purely pragmatic, EIG = 0.0
    - a2: affects knowledge only, delta_h_memory = 0.0
    - a3: affects memory only, delta_h_knowledge = 0.0
    - a4: affects knowledge only, delta_h_memory = 0.0
    - a5: hybrid contradiction resolution, may reduce knowledge contradiction entropy
    - a6: somatic pause, EIG = 0.0
    """
    cfg = config if config is not None else LIGPConfig()

    eff_delta_k = 0.0
    eff_delta_m = 0.0

    if action in (ActionType.A2_EXTERNAL_CLARIFICATION, ActionType.A4_KNOWLEDGE_DERIVATION):
        eff_delta_k = max(0.0, float(delta_h_knowledge))
    elif action == ActionType.A3_EXTENDED_SDM_PROBE:
        eff_delta_m = max(0.0, float(delta_h_memory))
    elif action == ActionType.A5_DEEP_REASONING_MODE_SHIFT:
        # Deliberative resolution of propositional contradiction
        eff_delta_k = max(0.0, float(delta_h_knowledge))
    elif action in (ActionType.A1_IMMEDIATE_RESPONSE, ActionType.A6_WAIT_CONVERSATIONAL_PAUSE):
        # Non-epistemic actions do not reduce epistemic entropy
        eff_delta_k = 0.0
        eff_delta_m = 0.0

    eig = cfg.w_k * eff_delta_k + cfg.w_m * eff_delta_m
    return float(max(0.0, eig))
