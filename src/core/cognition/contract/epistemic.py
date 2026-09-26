"""
src/core/cognition/contract/epistemic.py

Phase 23-G: Epistemic Status & Three-Valued Strong Kleene Logic.

Strict Invariants:
1. Four Epistemic States: FACT, INFERRED, AMBIGUOUS, UNKNOWN.
2. Strong Kleene three-valued semantics (TRUE, FALSE, UNKNOWN).
   - FALSE ∧ UNKNOWN = FALSE
   - TRUE ∧ UNKNOWN = UNKNOWN
   - UNKNOWN ∧ UNKNOWN = UNKNOWN
3. Never automatically promote UNKNOWN -> FACT/INFERRED.
4. Zero string dependency; numeric enum representations.
"""

from __future__ import annotations

from enum import IntEnum
from typing import Any, Iterable, Union

from src.core.knowledge.fortification import EpistemicState


class EpistemicStatus(IntEnum):
    """
    Epistemic status for all logical terms and entities in the Cognitive Core.
    Strictly numeric (IntEnum) to prevent string operations inside Core reasoning.
    """
    FACT = 1         # Grounded fact or direct perception
    INFERRED = 2     # Derived conclusion with mandatory rule ID & premise justification
    AMBIGUOUS = 3    # Competing alternative hypotheses; must not collapse prematurely
    UNKNOWN = 4      # Epistemically ungrounded / missing referent; must never be promoted

    @classmethod
    def from_epistemic_state(cls, state: Union[EpistemicState, str, int]) -> EpistemicStatus:
        """Map from P23-E EpistemicState or raw value to numeric EpistemicStatus."""
        if isinstance(state, EpistemicStatus):
            return state
        if isinstance(state, EpistemicState):
            state_val = state.value
        elif isinstance(state, str):
            state_val = state.upper()
        elif isinstance(state, int):
            return cls(state)
        else:
            raise ValueError(f"Cannot convert {state!r} to EpistemicStatus")

        if state_val == "FACT":
            return cls.FACT
        elif state_val == "INFERRED":
            return cls.INFERRED
        elif state_val == "AMBIGUOUS":
            return cls.AMBIGUOUS
        elif state_val == "UNKNOWN":
            return cls.UNKNOWN
        else:
            raise ValueError(f"Unknown epistemic state: {state_val}")

    def to_epistemic_state(self) -> EpistemicState:
        """Convert back to P23-E EpistemicState for substrate compatibility."""
        if self == EpistemicStatus.FACT:
            return EpistemicState.FACT
        elif self == EpistemicStatus.INFERRED:
            return EpistemicState.INFERRED
        elif self == EpistemicStatus.AMBIGUOUS:
            return EpistemicState.AMBIGUOUS
        elif self == EpistemicStatus.UNKNOWN:
            return EpistemicState.UNKNOWN
        raise ValueError(f"Invalid EpistemicStatus value: {self}")


class KleeneValue(IntEnum):
    """
    Strong Kleene Three-Valued Logic semantics:
    FALSE (0), TRUE (1), UNKNOWN (2).
    """
    FALSE = 0
    TRUE = 1
    UNKNOWN = 2


def kleene_and(a: KleeneValue, b: KleeneValue) -> KleeneValue:
    """
    Strong Kleene Conjunction (∧).
    
    Truth Table:
    FALSE ∧ FALSE   = FALSE
    FALSE ∧ TRUE    = FALSE
    FALSE ∧ UNKNOWN = FALSE
    TRUE  ∧ FALSE   = FALSE
    TRUE  ∧ TRUE    = TRUE
    TRUE  ∧ UNKNOWN = UNKNOWN
    UNKNOWN ∧ FALSE   = FALSE
    UNKNOWN ∧ TRUE    = UNKNOWN
    UNKNOWN ∧ UNKNOWN = UNKNOWN
    """
    if a == KleeneValue.FALSE or b == KleeneValue.FALSE:
        return KleeneValue.FALSE
    if a == KleeneValue.UNKNOWN or b == KleeneValue.UNKNOWN:
        return KleeneValue.UNKNOWN
    return KleeneValue.TRUE


def kleene_or(a: KleeneValue, b: KleeneValue) -> KleeneValue:
    """
    Strong Kleene Disjunction (∨).
    
    Truth Table:
    TRUE  ∨ anything = TRUE
    anything ∨ TRUE  = TRUE
    FALSE ∨ FALSE    = FALSE
    FALSE ∨ UNKNOWN  = UNKNOWN
    UNKNOWN ∨ FALSE  = UNKNOWN
    UNKNOWN ∨ UNKNOWN = UNKNOWN
    """
    if a == KleeneValue.TRUE or b == KleeneValue.TRUE:
        return KleeneValue.TRUE
    if a == KleeneValue.UNKNOWN or b == KleeneValue.UNKNOWN:
        return KleeneValue.UNKNOWN
    return KleeneValue.FALSE


def kleene_not(a: KleeneValue) -> KleeneValue:
    """
    Strong Kleene Negation (¬).
    
    Truth Table:
    ¬FALSE   = TRUE
    ¬TRUE    = FALSE
    ¬UNKNOWN = UNKNOWN
    """
    if a == KleeneValue.TRUE:
        return KleeneValue.FALSE
    if a == KleeneValue.FALSE:
        return KleeneValue.TRUE
    return KleeneValue.UNKNOWN


def kleene_all(values: Iterable[KleeneValue]) -> KleeneValue:
    """Evaluate Strong Kleene conjunction across an iterable of values."""
    result = KleeneValue.TRUE
    for v in values:
        if v == KleeneValue.FALSE:
            return KleeneValue.FALSE
        if v == KleeneValue.UNKNOWN:
            result = KleeneValue.UNKNOWN
    return result


def kleene_any(values: Iterable[KleeneValue]) -> KleeneValue:
    """Evaluate Strong Kleene disjunction across an iterable of values."""
    result = KleeneValue.FALSE
    for v in values:
        if v == KleeneValue.TRUE:
            return KleeneValue.TRUE
        if v == KleeneValue.UNKNOWN:
            result = KleeneValue.UNKNOWN
    return result
