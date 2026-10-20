"""
src/core/cognition/referent_adapter.py

Phase 23-D: Collision-free Canonical Referent Key & InformationSubgoal Adapter.
Implements the canonical structured JSON tuple serialization rule specified in
DOC-P23D-IMP-SPEC-V1-001 §4.

Strict Invariants:
1. Zero delimiter collision: encodes [scope, subject, predicate, object] via JSON tuple.
2. Token normalization: lowercase and stripped of leading/trailing whitespace.
3. Unambiguous bidirectional round-trip: decode_referent_key(encode_referent_key(...)) == (...).
4. Deterministic condition_id: SHA-256 hex digest of f"{condition_type}:{referent_key}".
"""

from __future__ import annotations

import hashlib
import json
from typing import Tuple

from src.core.cognition.contract.condition import (
    ConditionStatus,
    ConditionType,
    ResolutionSource,
    UnresolvedCondition,
)
from src.core.cognition.contract.projection import SymbolTable
from src.core.cognition.kernel.engine import InformationSubgoal


def encode_referent_key(
    scope: str,
    subject: str,
    predicate: str,
    object_: str = "",
) -> str:
    """
    Encode an epistemic referent into a collision-free canonical JSON tuple string.
    Normalizes all tokens to lowercase and strips extraneous whitespace.
    Scope defaults to 'scope:root' if empty.
    """
    s_norm = subject.strip().lower() if subject else ""
    p_norm = predicate.strip().lower() if predicate else ""
    o_norm = object_.strip().lower() if object_ else ""
    sc_norm = scope.strip().lower() if scope else "scope:root"

    # Deterministic compact JSON list guarantees zero delimiter ambiguity
    return json.dumps([sc_norm, s_norm, p_norm, o_norm], separators=(",", ":"), ensure_ascii=False)


def decode_referent_key(referent_key: str) -> Tuple[str, str, str, str]:
    """
    Decode a canonical referent key back into (scope, subject, predicate, object).
    Raises ValueError if string is malformed or not a 4-element list.
    """
    try:
        tokens = json.loads(referent_key)
    except Exception as exc:
        raise ValueError(f"Malformed referent key (JSON parse error): {referent_key}") from exc

    if not isinstance(tokens, list) or len(tokens) != 4:
        raise ValueError(f"Malformed referent key (expected 4-element list): {referent_key}")

    return (str(tokens[0]), str(tokens[1]), str(tokens[2]), str(tokens[3]))


def compute_condition_id(
    condition_type: ConditionType,
    referent_key: str,
) -> str:
    """
    Compute deterministic SHA-256 condition_id from condition type and canonical referent key.
    """
    payload = f"{condition_type.value}:{referent_key}".encode("utf-8")
    return hashlib.sha256(payload).hexdigest()


def subgoal_to_condition(
    subgoal: InformationSubgoal,
    symbol_table: SymbolTable,
    epoch: int = 0,
    resolution_source: ResolutionSource = ResolutionSource.INTERNAL_SEARCH,
    condition_type: ConditionType = ConditionType.MISSING_PREMISE,
) -> UnresolvedCondition:
    """
    Translate a P23-H numeric InformationSubgoal into an immutable UnresolvedCondition.
    Uses SymbolTable to resolve string concepts from numeric term IDs.
    """
    pred_sym = symbol_table.get_concept_symbol(subgoal.target_predicate_id) or f"c:pred_{subgoal.target_predicate_id}"
    a0_sym = symbol_table.get_concept_symbol(subgoal.arg0_id) if subgoal.arg0_id != 0 else ""
    a1_sym = symbol_table.get_concept_symbol(subgoal.arg1_id) if subgoal.arg1_id != 0 else ""
    scope_sym = f"scope:{subgoal.scope_id}" if subgoal.scope_id != 0 else "scope:root"

    ref_key = encode_referent_key(scope_sym, a0_sym, pred_sym, a1_sym)
    cond_id = compute_condition_id(condition_type, ref_key)

    return UnresolvedCondition(
        condition_id=cond_id,
        condition_type=condition_type,
        referent_key=ref_key,
        status=ConditionStatus.ACTIVE,
        resolution_source=resolution_source,
        epoch_created=epoch,
    )
