"""
src/core/cognition/kernel/binding.py

Phase 23-H: Fixed-Size Bounded Variable Binding Frame.

Strict Invariants:
1. Maximum 8 local variables (indices 0..7).
2. Zero dynamic heap allocation in inner binding/unification operations.
3. Completely numeric: variable IDs are negative integers (-1 to -8), value IDs are positive integers.
4. Bound mask tracking via single integer bitmask (0..255).
"""

from __future__ import annotations

from typing import Any, Dict, List, Optional, Tuple

MAX_VARS: int = 8

# Numeric variable constants: VAR_0 = -1, VAR_1 = -2, ..., VAR_7 = -8
VAR_0: int = -1
VAR_1: int = -2
VAR_2: int = -3
VAR_3: int = -4
VAR_4: int = -5
VAR_5: int = -6
VAR_6: int = -7
VAR_7: int = -8


def is_variable(val: int) -> bool:
    """Return True if val is a variable index in [-8, -1]."""
    return -MAX_VARS <= val <= -1


def var_to_index(var_id: int) -> int:
    """Convert variable ID (-1..-8) to 0-based array index (0..7)."""
    return -(var_id + 1)


def index_to_var(idx: int) -> int:
    """Convert 0-based array index (0..7) to variable ID (-1..-8)."""
    return -(idx + 1)


class BindingFrame:
    """
    Fixed-size variable binding frame for up to 8 variables.
    Preallocated storage; zero heap allocation on bind, query, or reset.
    """
    __slots__ = ("bound_mask", "bindings")

    def __init__(self) -> None:
        self.bound_mask: int = 0
        self.bindings: List[int] = [0] * MAX_VARS

    def is_bound(self, var_idx: int) -> bool:
        """Check if variable at index (0..7) is bound."""
        return (self.bound_mask & (1 << var_idx)) != 0

    def get(self, var_idx: int) -> int:
        """Get bound value for variable index (0..7). Returns 0 if unbound."""
        return self.bindings[var_idx]

    def get_var(self, var_id: int) -> Optional[int]:
        """Get bound value for variable ID (-1..-8). Returns None if unbound."""
        idx = var_to_index(var_id)
        if 0 <= idx < MAX_VARS and (self.bound_mask & (1 << idx)) != 0:
            return self.bindings[idx]
        return None

    def bind(self, var_idx: int, val: int) -> bool:
        """
        Bind variable at index (0..7) to positive integer value.
        If already bound, returns True iff existing binding equals val.
        Returns False on conflicting binding.
        """
        if not (0 <= var_idx < MAX_VARS):
            return False
        mask = 1 << var_idx
        if (self.bound_mask & mask) != 0:
            return self.bindings[var_idx] == val
        self.bindings[var_idx] = val
        self.bound_mask |= mask
        return True

    def bind_var(self, var_id: int, val: int) -> bool:
        """Bind variable ID (-1..-8) to positive integer value."""
        return self.bind(var_to_index(var_id), val)

    def copy_from(self, other: BindingFrame) -> None:
        """In-place copy from another BindingFrame without heap allocation."""
        self.bound_mask = other.bound_mask
        i = 0
        while i < MAX_VARS:
            self.bindings[i] = other.bindings[i]
            i += 1

    def reset(self) -> None:
        """Reset frame in place without deallocating buffer."""
        self.bound_mask = 0
        i = 0
        while i < MAX_VARS:
            self.bindings[i] = 0
            i += 1

    def to_dict(self) -> Dict[int, int]:
        """Convert active bindings to dictionary of var_id -> val."""
        res: Dict[int, int] = {}
        i = 0
        while i < MAX_VARS:
            if (self.bound_mask & (1 << i)) != 0:
                res[index_to_var(i)] = self.bindings[i]
            i += 1
        return res


def unify_value(pat_val: int, term_val: int, frame: BindingFrame) -> bool:
    """
    Unify a single pattern value with a term value under BindingFrame.
    - If pat_val is 0: wildcard or omitted; matches anything.
    - If pat_val is variable (< 0): binds or checks consistency in frame.
    - If pat_val is constant (> 0): must match term_val exactly.
    """
    if pat_val == 0:
        return True
    if is_variable(pat_val):
        return frame.bind(var_to_index(pat_val), term_val)
    return pat_val == term_val


def unify_terms(
    p_pred: int, p_a0: int, p_a1: int, p_a2: int,
    t_pred: int, t_a0: int, t_a1: int, t_a2: int,
    frame: BindingFrame,
) -> bool:
    """
    Unify pattern predicate and arguments with term predicate and arguments.
    Purely numeric; zero allocation.
    """
    if p_pred != t_pred:
        return False
    if not unify_value(p_a0, t_a0, frame):
        return False
    if not unify_value(p_a1, t_a1, frame):
        return False
    if not unify_value(p_a2, t_a2, frame):
        return False
    return True
