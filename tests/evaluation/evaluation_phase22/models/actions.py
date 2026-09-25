"""
tests/evaluation_phase22/models/actions.py

Discrete action space A = {a1, a2, a3, a4, a5, a6} for Phase 22.
Enforces strict distinction between external, internal, and somatic actions.
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from typing import Optional


class ActionType(str, Enum):
    """The six discrete actions specified in Phase 22 Protocol v1.2."""
    A1_IMMEDIATE_RESPONSE = "a1_immediate_response"
    A2_EXTERNAL_CLARIFICATION = "a2_external_clarification"
    A3_EXTENDED_SDM_PROBE = "a3_extended_sdm_probe"
    A4_KNOWLEDGE_DERIVATION = "a4_knowledge_derivation"
    A5_DEEP_REASONING_MODE_SHIFT = "a5_deep_reasoning_mode_shift"
    A6_WAIT_CONVERSATIONAL_PAUSE = "a6_wait_conversational_pause"


@dataclass(frozen=True)
class ActionMetadata:
    """Static metadata and defaults for each action."""
    action_type: ActionType
    code: str
    is_external: bool
    is_epistemic: bool
    base_compute_cost: float
    base_pragmatic_value: float
    description: str


ACTION_REGISTRY = {
    ActionType.A1_IMMEDIATE_RESPONSE: ActionMetadata(
        action_type=ActionType.A1_IMMEDIATE_RESPONSE,
        code="a1",
        is_external=False,
        is_epistemic=False,
        base_compute_cost=0.05,
        base_pragmatic_value=1.0,
        description="Immediate pragmatic response without information acquisition.",
    ),
    ActionType.A2_EXTERNAL_CLARIFICATION: ActionMetadata(
        action_type=ActionType.A2_EXTERNAL_CLARIFICATION,
        code="a2",
        is_external=True,
        is_epistemic=True,
        base_compute_cost=0.10,
        base_pragmatic_value=0.0,
        description="Ask user clarification via MockExternalOracle; incurs social cost.",
    ),
    ActionType.A3_EXTENDED_SDM_PROBE: ActionMetadata(
        action_type=ActionType.A3_EXTENDED_SDM_PROBE,
        code="a3",
        is_external=False,
        is_epistemic=True,
        base_compute_cost=0.25,
        base_pragmatic_value=0.0,
        description="Expand SDM Hamming search radius (451 -> 470) to resolve ecphory competition.",
    ),
    ActionType.A4_KNOWLEDGE_DERIVATION: ActionMetadata(
        action_type=ActionType.A4_KNOWLEDGE_DERIVATION,
        code="a4",
        is_external=False,
        is_epistemic=True,
        base_compute_cost=0.20,
        base_pragmatic_value=0.0,
        description="Perform bounded deterministic symbolic derivation (depth d <= 3).",
    ),
    ActionType.A5_DEEP_REASONING_MODE_SHIFT: ActionMetadata(
        action_type=ActionType.A5_DEEP_REASONING_MODE_SHIFT,
        code="a5",
        is_external=False,
        is_epistemic=True,  # Hybrid epistemic/pragmatic
        base_compute_cost=0.50,
        base_pragmatic_value=0.70,
        description="Shift to deliberative mode (k=2, 3 scaffolding steps) to resolve contradiction.",
    ),
    ActionType.A6_WAIT_CONVERSATIONAL_PAUSE: ActionMetadata(
        action_type=ActionType.A6_WAIT_CONVERSATIONAL_PAUSE,
        code="a6",
        is_external=False,
        is_epistemic=False,
        base_compute_cost=0.05,
        base_pragmatic_value=0.60,
        description="Simulated somatic conversational pause (L_p in [200, 1000] ms) for metabolic recovery.",
    ),
}
