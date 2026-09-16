"""
tests/evaluation_phase22/metrics/pathology.py

Automatic detection of pathological behaviors:
1. Interrogation Trap: a2 >= 3 times in any rolling 5-turn window.
2. Dark Room Trap: persistent a3/a4 on unresolvable aleatoric noise with ΔH < 0.05.
3. Epistemic Starvation: U_sem > 0.80 and a1 selected when useful epistemic action exists.
4. Computational Budget Breach: Tier-1 latency P95 > 5.0 ms.
5. Introspective Ego Leakage: Prohibited self-reports in generated text.
"""

from __future__ import annotations

import re
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Sequence

from src.core.safety.boundary_layer import DEFAULT_PATTERNS
from tests.evaluation_phase22.models.actions import ActionType

# Extended patterns for Phase 22 introspective ego leakage
EGO_LEAKAGE_PATTERNS: List[str] = DEFAULT_PATTERNS + [
    r"\bI was unsure so I checked\b",
    r"\blet me clarify my thoughts\b",
    r"\bI need to reduce my uncertainty\b",
    r"\bI was uncertain\b",
    r"\bmy epistemic\b",
    r"\bI checked because\b",
]

COMPILED_EGO_PATTERNS = [re.compile(p, re.IGNORECASE) for p in EGO_LEAKAGE_PATTERNS]


@dataclass(frozen=True)
class PathologySummary:
    """Aggregated pathology counts for an evaluation run."""
    interrogation_trap_count: int = 0
    dark_room_trap_count: int = 0
    epistemic_starvation_count: int = 0
    computational_breach_count: int = 0
    ego_leakage_count: int = 0

    @property
    def has_critical_pathology(self) -> bool:
        return (
            self.interrogation_trap_count > 0
            or self.dark_room_trap_count > 0
            or self.ego_leakage_count > 0
        )


def detect_interrogation_trap(
    action_history: Sequence[ActionType],
    window_size: int = 5,
    max_a2_count: int = 3,
) -> bool:
    """
    Returns True if a2 was chosen >= max_a2_count times in the trailing window.
    """
    if len(action_history) < max_a2_count:
        return False
    recent = action_history[-window_size:]
    a2_count = sum(1 for a in recent if a == ActionType.A2_EXTERNAL_CLARIFICATION)
    return a2_count >= max_a2_count


def detect_dark_room_trap(
    action: ActionType,
    is_aleatoric_noise: bool,
    observed_delta_h: float,
    threshold: float = 0.05,
) -> bool:
    """
    Returns True if an internal foraging action (a3 or a4) was persistently
    deployed on unresolvable aleatoric noise yielding negligible entropy reduction.
    """
    if action in (ActionType.A3_EXTENDED_SDM_PROBE, ActionType.A4_KNOWLEDGE_DERIVATION):
        if is_aleatoric_noise and observed_delta_h < threshold:
            return True
    return False


def detect_epistemic_starvation(
    action: ActionType,
    u_sem: float,
    useful_epistemic_action_available: bool,
    threshold: float = 0.80,
) -> bool:
    """
    Returns True if high semantic uncertainty exists (U_sem > threshold)
    and a useful epistemic action was available, but pragmatic a1 was chosen.
    """
    if u_sem > threshold and useful_epistemic_action_available:
        if action == ActionType.A1_IMMEDIATE_RESPONSE:
            return True
    return False


def detect_computational_breach(p95_latency_ms: float, limit_ms: float = 5.0) -> bool:
    """Returns True if Tier-1 P95 latency exceeds 5.0 ms."""
    return p95_latency_ms > limit_ms


def detect_introspective_ego_leakage(text: str) -> List[str]:
    """
    Returns list of matched prohibited introspective patterns in text.
    """
    matches: List[str] = []
    for pattern in COMPILED_EGO_PATTERNS:
        m = pattern.search(text)
        if m:
            matches.append(m.group(0))
    return matches
