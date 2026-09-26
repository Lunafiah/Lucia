"""
src/core/cognition/contract/matcher.py

Phase 23-G: Logical Term Matcher & Query Operations.

Strict Invariants:
1. Zero natural-language strings; all comparisons use numeric IDs.
2. Zero dynamic allocation when using preallocated output buffers.
3. Strong Kleene truth state evaluation for query results.
"""

from __future__ import annotations

from typing import Iterable, List, Optional

from src.core.cognition.contract.arena import TermArena
from src.core.cognition.contract.epistemic import EpistemicStatus, KleeneValue, kleene_all
from src.core.cognition.contract.terms import BindingSet, LogicalTerm, TermQueryPattern


def EvaluateTermKleene(term: LogicalTerm) -> KleeneValue:
    """
    Evaluate the Strong Kleene truth state of a LogicalTerm based on its epistemic status.
    
    FACT / INFERRED:
      polarity=True  -> TRUE
      polarity=False -> FALSE
    UNKNOWN:
      always -> UNKNOWN
    AMBIGUOUS:
      always -> UNKNOWN (until explicitly disambiguated)
    """
    if not term.is_active:
        return KleeneValue.FALSE

    if term.epistemic_status == EpistemicStatus.UNKNOWN:
        return KleeneValue.UNKNOWN
    elif term.epistemic_status == EpistemicStatus.AMBIGUOUS:
        if term.is_disambiguated:
            return KleeneValue.TRUE if term.polarity else KleeneValue.FALSE
        return KleeneValue.UNKNOWN
    elif term.epistemic_status in (EpistemicStatus.FACT, EpistemicStatus.INFERRED):
        return KleeneValue.TRUE if term.polarity else KleeneValue.FALSE

    return KleeneValue.UNKNOWN


def EvaluateConjunctionKleene(terms: Iterable[LogicalTerm]) -> KleeneValue:
    """Evaluate Strong Kleene conjunction over a sequence of terms."""
    return kleene_all(EvaluateTermKleene(t) for t in terms)


def QueryTermPatternIntoBuffer(
    arena: TermArena,
    pattern: TermQueryPattern,
    out_buffer: List[int],
    bindings: Optional[BindingSet] = None,
) -> int:
    """
    Zero-allocation query execution writing directly into preallocated out_buffer.
    Returns the count of matched terms.
    """
    match_count = 0
    max_cap = len(out_buffer)
    base_dict = bindings.as_dict() if bindings is not None else None

    if pattern.predicate_id is not None and pattern.predicate_id > 0:
        candidate_ids = arena.terms_for_predicate(pattern.predicate_id)
        n = len(candidate_ids)
        i = 0
        while i < n and match_count < max_cap:
            tid = candidate_ids[i]
            term = arena.get_term(tid)
            if term is not None:
                cand_b = BindingSet(_bindings=dict(base_dict)) if base_dict is not None else None
                if pattern.matches(term, cand_b):
                    out_buffer[match_count] = tid
                    match_count += 1
                    if bindings is not None and cand_b is not None and match_count == 1:
                        bindings._bindings.update(cand_b.as_dict())
            i += 1
    else:
        active_list = arena.active_terms()
        n = len(active_list)
        i = 0
        while i < n and match_count < max_cap:
            term = active_list[i]
            cand_b = BindingSet(_bindings=dict(base_dict)) if base_dict is not None else None
            if pattern.matches(term, cand_b):
                out_buffer[match_count] = term.term_id
                match_count += 1
                if bindings is not None and cand_b is not None and match_count == 1:
                    bindings._bindings.update(cand_b.as_dict())
            i += 1

    return match_count


def QueryTermPattern(
    arena: TermArena,
    pattern: TermQueryPattern,
    bindings: Optional[BindingSet] = None,
    out_matches: Optional[List[int]] = None,
) -> List[int]:
    """
    Query the TermArena for terms matching pattern.
    Compares strictly numeric IDs.
    
    If out_matches is provided, writes results into out_matches.
    Otherwise, returns a new list of matching term_ids.
    """
    use_provided_buf = out_matches is not None
    results = out_matches if use_provided_buf else []
    if use_provided_buf:
        results.clear()

    base_dict = bindings.as_dict() if bindings is not None else None

    # Fast indexed candidate lookup if predicate_id is specified
    if pattern.predicate_id is not None and pattern.predicate_id > 0:
        candidate_ids = arena.terms_for_predicate(pattern.predicate_id)
        for tid in candidate_ids:
            term = arena.get_term(tid)
            if term is not None:
                cand_b = BindingSet(_bindings=dict(base_dict)) if base_dict is not None else None
                if pattern.matches(term, cand_b):
                    results.append(tid)
                    if bindings is not None and cand_b is not None and len(results) == 1:
                        bindings._bindings.update(cand_b.as_dict())
    else:
        # Scan active terms
        for term in arena.active_terms():
            cand_b = BindingSet(_bindings=dict(base_dict)) if base_dict is not None else None
            if pattern.matches(term, cand_b):
                results.append(term.term_id)
                if bindings is not None and cand_b is not None and len(results) == 1:
                    bindings._bindings.update(cand_b.as_dict())

    return results


