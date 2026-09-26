"""
src/core/cognition/kernel/rules.py

Phase 23-H: Static Rule Representation & Predicate-Based Rule Index.

Strict Invariants:
1. Maximum 8 local variables (VAR_0 = -1 .. VAR_7 = -8).
2. Maximum 4 premises per rule.
3. Maximum 3 arguments per term/premise (arg0, arg1, arg2).
4. Strictly numeric IDs: rule_id > 0, predicate_id > 0, argument IDs (entity/concept/variable).
5. Rules are read-only and static during reasoning.
6. Rule lookup uses head-predicate index rather than scanning all rules.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List, Optional, Sequence, Tuple

from src.core.cognition.kernel.binding import MAX_VARS, is_variable

MAX_PREMISES: int = 4
MAX_ARGS: int = 3


@dataclass(frozen=True)
class RuleHead:
    """
    Head (consequence pattern) of an inference rule.
    Arguments can be positive constants or negative variables (VAR_0..VAR_7).
    """
    predicate_id: int
    arg0: int
    arg1: int = 0
    arg2: int = 0
    polarity: bool = True

    def __post_init__(self) -> None:
        if self.predicate_id <= 0:
            raise ValueError(f"RuleHead predicate_id must be positive integer, got {self.predicate_id}")
        for arg in (self.arg0, self.arg1, self.arg2):
            if arg < 0 and not is_variable(arg):
                raise ValueError(f"Invalid variable ID {arg} in RuleHead (allowed: {-MAX_VARS}..-1)")


@dataclass(frozen=True)
class RulePremise:
    """
    Premise (antecedent pattern) of an inference rule.
    Arguments can be positive constants or negative variables (VAR_0..VAR_7).
    """
    predicate_id: int
    arg0: int
    arg1: int = 0
    arg2: int = 0
    polarity: bool = True

    def __post_init__(self) -> None:
        if self.predicate_id <= 0:
            raise ValueError(f"RulePremise predicate_id must be positive integer, got {self.predicate_id}")
        for arg in (self.arg0, self.arg1, self.arg2):
            if arg < 0 and not is_variable(arg):
                raise ValueError(f"Invalid variable ID {arg} in RulePremise (allowed: {-MAX_VARS}..-1)")


@dataclass(frozen=True)
class InferenceRule:
    """
    Static, bounded Horn-style inference rule:
    Premises[0] ∧ Premises[1] ∧ ... ∧ Premises[k-1] → Head
    
    Limits:
    - len(premises) <= MAX_PREMISES (4)
    - distinct variables used <= MAX_VARS (8)
    - rule_id > 0 (numeric)
    """
    rule_id: int
    head: RuleHead
    premises: Tuple[RulePremise, ...]

    def __post_init__(self) -> None:
        if self.rule_id <= 0:
            raise ValueError(f"InferenceRule rule_id must be positive integer, got {self.rule_id}")
        if not (1 <= len(self.premises) <= MAX_PREMISES):
            raise ValueError(
                f"InferenceRule must have 1..{MAX_PREMISES} premises, got {len(self.premises)}"
            )

        # Validate total unique variables
        var_set = set()
        for arg in (self.head.arg0, self.head.arg1, self.head.arg2):
            if is_variable(arg):
                var_set.add(arg)
        for p in self.premises:
            for arg in (p.arg0, p.arg1, p.arg2):
                if is_variable(arg):
                    var_set.add(arg)
        if len(var_set) > MAX_VARS:
            raise ValueError(
                f"InferenceRule uses {len(var_set)} variables; maximum allowed is {MAX_VARS}"
            )


class RuleIndex:
    """
    Static index of inference rules keyed by head predicate_id.
    Enables O(1) predicate lookup without scanning all rules in working memory.
    Read-only during the reasoning cycle.
    """
    __slots__ = ("_rules_by_head_pred", "_rules_by_id", "_all_rules")

    def __init__(self, rules: Sequence[InferenceRule] = ()) -> None:
        self._rules_by_head_pred: Dict[int, List[InferenceRule]] = {}
        self._rules_by_id: Dict[int, InferenceRule] = {}
        self._all_rules: List[InferenceRule] = []

        for rule in rules:
            self.add_rule(rule)

    def add_rule(self, rule: InferenceRule) -> None:
        """Add rule to index (call during initialization/setup, not during inner reasoning loop)."""
        if rule.rule_id in self._rules_by_id:
            raise ValueError(f"Duplicate rule_id={rule.rule_id} in RuleIndex")

        self._rules_by_id[rule.rule_id] = rule
        self._all_rules.append(rule)

        pred_id = rule.head.predicate_id
        if pred_id not in self._rules_by_head_pred:
            self._rules_by_head_pred[pred_id] = []
        self._rules_by_head_pred[pred_id].append(rule)

    def get_rules_for_head(self, predicate_id: int) -> List[InferenceRule]:
        """Fast indexed lookup for rules deriving predicate_id. Returns empty list if none."""
        return self._rules_by_head_pred.get(predicate_id, [])

    def get_rule_by_id(self, rule_id: int) -> Optional[InferenceRule]:
        """Lookup rule by numeric ID."""
        return self._rules_by_id.get(rule_id)

    @property
    def total_rules(self) -> int:
        return len(self._all_rules)

    def all_rules(self) -> List[InferenceRule]:
        return list(self._all_rules)
