"""Evaluation Metrics for EXP-04: Belief Revision & Contradiction.

Calculates:
- Contradiction Detection Recall (CDR)
- Revision Correctness (RC)
- Dependency Propagation Accuracy (DPA)
- Collateral Retraction Rate (CRR)
- Historical Retention Rate (HRR)
"""

from __future__ import annotations

from typing import Any, Dict, List, Set, Tuple


def normalize_pair(a: str, b: str) -> Tuple[str, str]:
    return (a, b) if a <= b else (b, a)


def compute_cdr(
    detected_pairs: List[Tuple[str, str]],
    oracle_pairs: List[Tuple[str, str]],
) -> float:
    """Computes Contradiction Detection Recall (CDR)."""
    if not oracle_pairs:
        return 1.0  # Vacuously true if no contradictions exist in oracle
    norm_detected = {normalize_pair(p[0], p[1]) for p in detected_pairs}
    norm_oracle = {normalize_pair(p[0], p[1]) for p in oracle_pairs}
    matched = norm_detected.intersection(norm_oracle)
    return len(matched) / len(norm_oracle)


def compute_rc(
    actual_states: Dict[str, str],
    oracle_states: Dict[str, str],
) -> float:
    """Computes Revision Correctness (RC) across all assertions."""
    if not oracle_states:
        return 1.0
    correct = 0
    for ast_id, expected_state in oracle_states.items():
        if actual_states.get(ast_id) == expected_state:
            correct += 1
    return correct / len(oracle_states)


def compute_dpa(
    actual_states: Dict[str, str],
    expected_retracted_deps: List[str],
) -> float:
    """Computes Dependency Propagation Accuracy (DPA)."""
    if not expected_retracted_deps:
        return 1.0  # No dependent beliefs to retract
    correctly_retracted = sum(
        1 for d_id in expected_retracted_deps if actual_states.get(d_id) == "OUT"
    )
    return correctly_retracted / len(expected_retracted_deps)


def compute_crr(
    actual_states: Dict[str, str],
    unaffected_in: List[str],
) -> float:
    """Computes Collateral Retraction Rate (CRR).

    Target is 0.0 (no unaffected belief should be retracted).
    """
    if not unaffected_in:
        return 0.0
    erroneously_retracted = sum(
        1 for u_id in unaffected_in if actual_states.get(u_id) == "OUT"
    )
    return erroneously_retracted / len(unaffected_in)


def compute_hrr(
    retrievable_history_ids: Set[str],
    total_introduced_ids: Set[str],
) -> float:
    """Computes Historical Retention Rate (HRR).

    Target is 1.0 (all historical assertions must be retrievable from the audit ledger).
    """
    if not total_introduced_ids:
        return 1.0
    retained = retrievable_history_ids.intersection(total_introduced_ids)
    return len(retained) / len(total_introduced_ids)


def evaluate_run(
    detected_contradictions: List[Tuple[str, str]],
    actual_states: Dict[str, str],
    retrievable_history_ids: Set[str],
    expected_oracle: Dict[str, Any],
    all_introduced_ids: Set[str],
    elapsed_ms: float,
) -> Dict[str, Any]:
    """Computes full metric report for a scenario execution."""
    oracle_contradictions = [
        (p[0], p[1]) for p in expected_oracle.get("contradictions", [])
    ]
    oracle_states = expected_oracle.get("final_states", {})
    retracted_deps = expected_oracle.get("retracted_dependencies", [])
    unaffected_in = expected_oracle.get("unaffected_in", [])

    cdr = compute_cdr(detected_contradictions, oracle_contradictions)
    rc = compute_rc(actual_states, oracle_states)
    dpa = compute_dpa(actual_states, retracted_deps)
    crr = compute_crr(actual_states, unaffected_in)
    hrr = compute_hrr(retrievable_history_ids, all_introduced_ids)

    # Check falsification conditions
    passed_falsification = (
        cdr >= 0.98
        and rc >= 0.98
        and dpa == 1.0
        and crr == 0.0
        and hrr == 1.0
    )

    return {
        "CDR": round(cdr, 4),
        "RC": round(rc, 4),
        "DPA": round(dpa, 4),
        "CRR": round(crr, 4),
        "HRR": round(hrr, 4),
        "latency_ms": round(elapsed_ms, 3),
        "passed": passed_falsification,
    }
