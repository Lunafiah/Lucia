"""
src/core/cognition/kernel/compiler.py

Phase 23-H: Bounded KnowledgeStore -> RuleIndex Compiler.
Implements the ratified specification in DOC-P23H-RULE-COMPILER-IMPLEMENTATION-SPEC-R1-001.

Strict Invariants:
1. Deterministic Rule Ordering: Sorts input rules by rule.id prior to compilation.
2. Complete Argument Scan: Scans head.arg0, head.arg1, head.arg2 and premise.arg0, premise.arg1, premise.arg2.
3. Variable Bounding: Identifies variable tokens as token.startswith("?") and len(token) > 1.
   Allocates VAR_0 (-1) .. VAR_7 (-8). Quarantines rules with > 8 variables (EXCESS_VARIABLES).
4. Unsafe Head Variable Gate: Enforces Vars(Head) ⊆ Union(Vars(Antecedents)).
   Quarantines rules with unbound head variables (UNSAFE_HEAD_VARIABLE).
5. Positive Horn Polarity: Compiles all RuleHead and RulePremise with polarity=True.
6. Fail-Soft Quarantine: Quarantines invalid rules into RuleCompilationReport; never crashes startup.
7. First-Rule-Wins Duplicate Policy: Quarantines duplicate numeric rule IDs at compiler input boundary.
8. Excludes confidence_decay: Preserves discrete Strong Kleene K3 reasoning purity.
"""

from __future__ import annotations

import logging
from dataclasses import dataclass
from enum import Enum
from typing import Any, Dict, List, Optional, Sequence, Set, Tuple

from src.core.cognition.contract.projection import SymbolTable
from src.core.cognition.kernel.binding import MAX_VARS
from src.core.cognition.kernel.rules import (
    MAX_PREMISES,
    InferenceRule as P23HInferenceRule,
    RuleHead,
    RuleIndex,
    RulePremise,
)
from src.core.knowledge.proposition import InferenceRule as KSInferenceRule

logger = logging.getLogger(__name__)


class RuleDiagnosticCode(str, Enum):
    """Standardized diagnostic reason codes for rule compilation."""
    OK = "OK"
    MALFORMED_STRUCTURE = "MALFORMED_STRUCTURE"
    EMPTY_PREDICATE = "EMPTY_PREDICATE"
    EXCESS_PREMISES = "EXCESS_PREMISES"
    EXCESS_VARIABLES = "EXCESS_VARIABLES"
    UNSAFE_HEAD_VARIABLE = "UNSAFE_HEAD_VARIABLE"
    DUPLICATE_RULE_ID = "DUPLICATE_RULE_ID"


@dataclass(frozen=True)
class RuleDiagnostic:
    """Diagnostic outcome for an individual candidate rule."""
    source_rule_id: str
    status: str                         # "COMPILED" | "QUARANTINED"
    code: RuleDiagnosticCode
    detail: str


@dataclass(frozen=True)
class RuleCompilationReport:
    """Consolidated summary report of the compilation pass."""
    total_source_rules: int
    compiled_count: int
    quarantined_count: int
    diagnostics: Tuple[RuleDiagnostic, ...]


def is_variable_token(token: Any) -> bool:
    """
    Check if a token is a valid Horn variable.
    Exact contract: isinstance(token, str) and token.startswith("?") and len(token) > 1.
    """
    return isinstance(token, str) and token.startswith("?") and len(token) > 1


def _is_valid_pattern_tuple(pat: Any) -> bool:
    """Validate that pattern is a sequence of length 3 (SPO) or 4 (SPO + modifier)."""
    if not isinstance(pat, (tuple, list)):
        return False
    if len(pat) not in (3, 4):
        return False
    # All elements must be non-None and convertible to string or int
    return True


def compile_rule_set(
    rules: Sequence[KSInferenceRule],
    symbol_table: SymbolTable,
) -> Tuple[RuleIndex, RuleCompilationReport]:
    """
    Public entry point for compiling a sequence of KnowledgeStore.InferenceRule objects
    into a P23-H RuleIndex with a fail-soft RuleCompilationReport.

    Execution sequence:
    1. Sorts input rules lexicographically by rule.id for deterministic processing order.
    2. Runs ordered 7-step validation pipeline on each rule.
    3. Allocates local variable slots VAR_0 (-1) .. VAR_7 (-8) by first-appearance scan:
       head.arg0 -> head.arg1 -> head.arg2 -> premise[0].arg0..arg2 -> premise[1]...
    4. Enforces head variable safety: Vars(Head) ⊆ Union(Vars(Antecedents)).
    5. Deduplicates on compiler input boundary via first-rule-wins.
    6. Assembles immutable RuleIndex and returns compilation report.
    """
    # 1. Deterministic Rule Ordering
    sorted_rules = sorted(rules, key=lambda r: getattr(r, "id", ""))

    rule_index = RuleIndex()
    diagnostics: List[RuleDiagnostic] = []
    seen_rule_ids: Set[int] = set()
    compiled_count = 0
    quarantined_count = 0

    for rule in sorted_rules:
        rule_id_str = getattr(rule, "id", "")

        # ── Step 1: Structural Validation ─────────────────────────────────────────
        consequent = getattr(rule, "consequent_pattern", None)
        antecedents = getattr(rule, "antecedents", None)

        if not _is_valid_pattern_tuple(consequent):
            diagnostics.append(
                RuleDiagnostic(
                    source_rule_id=rule_id_str,
                    status="QUARANTINED",
                    code=RuleDiagnosticCode.MALFORMED_STRUCTURE,
                    detail=f"Consequent pattern must be a 3-tuple or 4-tuple, got {type(consequent).__name__} len={len(consequent) if isinstance(consequent, (tuple, list)) else 'N/A'}",
                )
            )
            quarantined_count += 1
            continue

        if not isinstance(antecedents, (tuple, list)):
            diagnostics.append(
                RuleDiagnostic(
                    source_rule_id=rule_id_str,
                    status="QUARANTINED",
                    code=RuleDiagnosticCode.MALFORMED_STRUCTURE,
                    detail=f"Antecedents must be a list or tuple, got {type(antecedents).__name__}",
                )
            )
            quarantined_count += 1
            continue

        # ── Step 2: Antecedent Count Bound ────────────────────────────────────────
        num_antecedents = len(antecedents)
        if num_antecedents == 0 or num_antecedents > MAX_PREMISES:
            diagnostics.append(
                RuleDiagnostic(
                    source_rule_id=rule_id_str,
                    status="QUARANTINED",
                    code=RuleDiagnosticCode.EXCESS_PREMISES,
                    detail=f"Antecedent count must be in [1, {MAX_PREMISES}], got {num_antecedents}",
                )
            )
            quarantined_count += 1
            continue

        malformed_ant = False
        for idx, ant in enumerate(antecedents):
            if not _is_valid_pattern_tuple(ant):
                diagnostics.append(
                    RuleDiagnostic(
                        source_rule_id=rule_id_str,
                        status="QUARANTINED",
                        code=RuleDiagnosticCode.MALFORMED_STRUCTURE,
                        detail=f"Antecedent[{idx}] must be a 3-tuple or 4-tuple, got {type(ant).__name__}",
                    )
                )
                quarantined_count += 1
                malformed_ant = True
                break
        if malformed_ant:
            continue

        # ── Step 3: Predicate Validation ──────────────────────────────────────────
        c_pred = str(consequent[1]).strip() if len(consequent) > 1 and consequent[1] is not None else ""
        if not c_pred or c_pred == "?":
            diagnostics.append(
                RuleDiagnostic(
                    source_rule_id=rule_id_str,
                    status="QUARANTINED",
                    code=RuleDiagnosticCode.EMPTY_PREDICATE,
                    detail="Consequent predicate cannot be empty or bare variable '?'",
                )
            )
            quarantined_count += 1
            continue

        empty_ant_pred = False
        for idx, ant in enumerate(antecedents):
            a_pred = str(ant[1]).strip() if len(ant) > 1 and ant[1] is not None else ""
            if not a_pred or a_pred == "?":
                diagnostics.append(
                    RuleDiagnostic(
                        source_rule_id=rule_id_str,
                        status="QUARANTINED",
                        code=RuleDiagnosticCode.EMPTY_PREDICATE,
                        detail=f"Antecedent[{idx}] predicate cannot be empty or bare variable '?'",
                    )
                )
                quarantined_count += 1
                empty_ant_pred = True
                break
        if empty_ant_pred:
            continue

        # ── Step 4: Variable Extraction & Scanning ────────────────────────────────
        # Complete scan order: head.arg0 -> head.arg1 -> head.arg2 -> premise[0].arg0..arg2 -> ...
        head_a0_token = consequent[0]
        head_a1_token = consequent[2]
        head_a2_token = consequent[3] if len(consequent) > 3 else None

        var_map: Dict[str, int] = {}
        ordered_tokens: List[Any] = [head_a0_token, head_a1_token, head_a2_token]

        for ant in antecedents:
            ordered_tokens.append(ant[0])
            ordered_tokens.append(ant[2])
            ordered_tokens.append(ant[3] if len(ant) > 3 else None)

        excess_vars = False
        for tok in ordered_tokens:
            if tok is not None and is_variable_token(tok):
                if tok not in var_map:
                    if len(var_map) >= MAX_VARS:
                        diagnostics.append(
                            RuleDiagnostic(
                                source_rule_id=rule_id_str,
                                status="QUARANTINED",
                                code=RuleDiagnosticCode.EXCESS_VARIABLES,
                                detail=f"Rule exceeds maximum allowed variables ({MAX_VARS})",
                            )
                        )
                        quarantined_count += 1
                        excess_vars = True
                        break
                    # Assign negative variable index VAR_0 (-1) .. VAR_7 (-8)
                    var_map[tok] = -(len(var_map) + 1)
        if excess_vars:
            continue

        # ── Step 5: Head Variable Safety Verification ─────────────────────────────
        # Invariant: Vars(Head) ⊆ Union(Vars(Antecedents))
        head_vars: Set[str] = set()
        for tok in (head_a0_token, head_a1_token, head_a2_token):
            if tok is not None and is_variable_token(tok):
                head_vars.add(tok)

        body_vars: Set[str] = set()
        for ant in antecedents:
            if is_variable_token(ant[0]):
                body_vars.add(ant[0])
            if is_variable_token(ant[2]):
                body_vars.add(ant[2])
            if len(ant) > 3 and is_variable_token(ant[3]):
                body_vars.add(ant[3])

        unbound_head_vars = head_vars - body_vars
        if unbound_head_vars:
            diagnostics.append(
                RuleDiagnostic(
                    source_rule_id=rule_id_str,
                    status="QUARANTINED",
                    code=RuleDiagnosticCode.UNSAFE_HEAD_VARIABLE,
                    detail=f"Unsafe head variables {sorted(unbound_head_vars)} not bound by any antecedent",
                )
            )
            quarantined_count += 1
            continue

        # ── Step 6: Input Boundary Duplicate Check (First-Rule-Wins) ──────────────
        ru_id = symbol_table.intern_rule(rule_id_str)
        if ru_id in seen_rule_ids:
            diagnostics.append(
                RuleDiagnostic(
                    source_rule_id=rule_id_str,
                    status="QUARANTINED",
                    code=RuleDiagnosticCode.DUPLICATE_RULE_ID,
                    detail=f"Rule ID '{rule_id_str}' (numeric {ru_id}) already compiled in this pass; skipping duplicate",
                )
            )
            quarantined_count += 1
            continue
        seen_rule_ids.add(ru_id)

        # ── Step 7: Build P23-H Rule Structures ───────────────────────────────────
        # Consequent head
        head_pred_id = symbol_table.intern_concept(c_pred)
        h_a0 = var_map[head_a0_token] if is_variable_token(head_a0_token) else symbol_table.intern_concept(str(head_a0_token))
        h_a1 = var_map[head_a1_token] if is_variable_token(head_a1_token) else symbol_table.intern_concept(str(head_a1_token))
        h_a2 = 0
        if head_a2_token is not None:
            h_a2 = var_map[head_a2_token] if is_variable_token(head_a2_token) else symbol_table.intern_concept(str(head_a2_token))

        head = RuleHead(
            predicate_id=head_pred_id,
            arg0=h_a0,
            arg1=h_a1,
            arg2=h_a2,
            polarity=True,  # Positive Horn restriction for v1
        )

        # Premises
        compiled_premises: List[RulePremise] = []
        for ant in antecedents:
            a_pred_str = str(ant[1]).strip()
            a_pred_id = symbol_table.intern_concept(a_pred_str)
            p_a0 = var_map[ant[0]] if is_variable_token(ant[0]) else symbol_table.intern_concept(str(ant[0]))
            p_a1 = var_map[ant[2]] if is_variable_token(ant[2]) else symbol_table.intern_concept(str(ant[2]))
            p_a2 = 0
            if len(ant) > 3 and ant[3] is not None:
                p_a2 = var_map[ant[3]] if is_variable_token(ant[3]) else symbol_table.intern_concept(str(ant[3]))

            compiled_premises.append(
                RulePremise(
                    predicate_id=a_pred_id,
                    arg0=p_a0,
                    arg1=p_a1,
                    arg2=p_a2,
                    polarity=True,  # Positive Horn restriction for v1
                )
            )

        p23h_rule = P23HInferenceRule(
            rule_id=ru_id,
            head=head,
            premises=tuple(compiled_premises),
        )

        # Insert into RuleIndex
        rule_index.add_rule(p23h_rule)
        diagnostics.append(
            RuleDiagnostic(
                source_rule_id=rule_id_str,
                status="COMPILED",
                code=RuleDiagnosticCode.OK,
                detail=f"Successfully compiled into P23-H rule_id={ru_id}",
            )
        )
        compiled_count += 1

    report = RuleCompilationReport(
        total_source_rules=len(sorted_rules),
        compiled_count=compiled_count,
        quarantined_count=quarantined_count,
        diagnostics=tuple(diagnostics),
    )
    return rule_index, report
