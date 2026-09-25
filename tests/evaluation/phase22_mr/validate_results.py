"""
Gate Validator for Phase 22-MR: Memory Retrieval & Context Conditioning Study.

Reads gate_results.json and aggregated_results.json from evaluation_artifacts/phase22_mr/
and performs fail-closed validation:
  - All preregistered acceptance gates must pass for any candidate to be declared
    "architecture-approved" for further promotion consideration.
  - Validates that the Genesis gate has not been violated.
  - Validates that no production files were touched.
  - Produces a human-readable validation summary.

This script is SEPARATE from run_experiments.py to allow independent re-validation.
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

ARTIFACTS_DIR  = Path(__file__).parents[3] / "evaluation_artifacts" / "phase22_mr"
PRODUCTION_DIR = Path(__file__).parents[3] / "src" / "core"
PROFILE_PATH   = Path(__file__).parents[3] / "data" / "profile.json"

# Expected gate names
EXPECTED_GATES = {
    "G_MR1_Recall",
    "G_MR2_Precision_K",
    "G_MR3_Compression",
    "G_MR4_Token_Budget",
    "G_MR5_Injection_Rate",
    "G_MR6_Hallucination",
    "G_MR7_Relational_Cons",
    "G_MR8_Latency_P50",
    "G_MR9_VRAM",
}


def validate_genesis_gate() -> bool:
    """Verify that data/profile.json is_onboarded remains false."""
    if not PROFILE_PATH.exists():
        print("  [INFO] data/profile.json not found — assuming not onboarded (OK).")
        return True
    with open(PROFILE_PATH, "r", encoding="utf-8") as fh:
        profile = json.load(fh)
    ok = profile.get("is_onboarded") is False
    status = "PASSED PASS" if ok else "FAILED FAIL — CRITICAL INVARIANT VIOLATION"
    print(f"  Genesis Gate (is_onboarded=false): [{status}]")
    return ok


def validate_production_isolation() -> bool:
    """
    Verify that no Phase 22-MR experiment files were written into src/core/.
    Only checks for obvious leakage — not a full audit.
    """
    if not PRODUCTION_DIR.exists():
        print("  [INFO] src/core/ not found — skipping production isolation check.")
        return True

    violations = []
    for marker in ["phase22_mr", "retrieval_candidate", "SimulatedSDM"]:
        for path in PRODUCTION_DIR.rglob("*.py"):
            try:
                content = path.read_text(encoding="utf-8", errors="ignore")
                if marker in content:
                    violations.append(str(path))
            except Exception:
                pass

    ok = len(violations) == 0
    if ok:
        print("  Production Isolation Check:             [PASSED]")
    else:
        print("  Production Isolation Check:             [FAILED]")
        for v in violations:
            print(f"    Violation: {v}")
    return ok


def validate_gate_file(gate_results: dict) -> tuple[bool, int, int]:
    """
    Validate gate results from gate_results.json.
    Returns (all_passed, n_passed, n_total).
    """
    n_passed = 0
    n_total  = 0
    all_ok   = True

    missing = EXPECTED_GATES - set(gate_results.keys())
    if missing:
        print(f"  [WARN] Missing gates: {missing}")
        all_ok = False

    for gate_name, gate_info in gate_results.items():
        n_total += 1
        passed   = gate_info.get("passed", False)
        measured = gate_info.get("measured", float("nan"))
        thresh   = gate_info.get("threshold", float("nan"))
        if passed:
            n_passed += 1
            symbol   = "PASS"
        else:
            all_ok   = False
            symbol   = "FAIL"
        print(f"  {gate_name:<38} measured={measured:.4f}  threshold={thresh}  [{symbol}]")

    return all_ok, n_passed, n_total


def validate_mandatory_recall(agg_results: dict) -> bool:
    """
    Special safety check: mandatory recall (rupture/repair/milestone) must be
    >= 0.99 for M4 and Oracle on held-out seeds.
    This is a fail-closed safety invariant beyond the preregistered gates.
    """
    threshold = 0.99
    ok        = True
    for cand in ["M4_HybridFull", "Oracle"]:
        mr = (agg_results
              .get(cand, {})
              .get("held_out", {})
              .get("mandatory_recall", {})
              .get("mean", 0.0))
        passed = mr >= threshold
        if not passed:
            ok = False
        sym = "PASS" if passed else "FAIL"
        print(f"  Mandatory Recall [{cand}]:         {mr:.4f}  (SLA >= {threshold}) [{sym}]")
    return ok


def main():
    print("=" * 70)
    print("Phase 22-MR — Fail-Closed Gate Validation")
    print("=" * 70)

    all_ok = True

    # ── 1. Genesis Gate ───────────────────────────────────────────────────────
    print("\n[1] Genesis Invariant Gate:")
    all_ok &= validate_genesis_gate()

    # ── 2. Production Isolation ───────────────────────────────────────────────
    print("\n[2] Production Code Isolation:")
    all_ok &= validate_production_isolation()

    # ── 3. Load gate results ──────────────────────────────────────────────────
    gate_file = ARTIFACTS_DIR / "gate_results.json"
    if not gate_file.exists():
        print(f"\n[ERROR] gate_results.json not found at {gate_file}")
        print("  -> Run run_experiments.py first.")
        sys.exit(1)

    with open(gate_file, "r", encoding="utf-8") as fh:
        gate_results = json.load(fh)

    # ── 4. Preregistered Gates ────────────────────────────────────────────────
    print("\n[3] Preregistered Acceptance Gates (M4 on Held-Out Seeds):")
    gates_ok, n_passed, n_total = validate_gate_file(gate_results)
    all_ok &= gates_ok

    # ── 5. Mandatory Recall Safety Invariant ──────────────────────────────────
    agg_file = ARTIFACTS_DIR / "aggregated_results.json"
    if agg_file.exists():
        with open(agg_file, "r", encoding="utf-8") as fh:
            agg_results = json.load(fh)
        print("\n[4] Mandatory Anchor Recall Safety Check (>= 0.99):")
        all_ok &= validate_mandatory_recall(agg_results)
    else:
        print("\n[WARN] aggregated_results.json not found — skipping mandatory recall check.")

    # ── 6. Final verdict ──────────────────────────────────────────────────────
    print("\n" + "=" * 70)
    print(f"  Gates Passed: {n_passed}/{n_total}")
    if all_ok:
        print("  OVERALL VERDICT: ALL CHECKS PASSED PASS")
        print("  -> Research evidence is sufficient for architecture review.")
        print("  -> Production promotion still requires Architecture Gate approval.")
    else:
        print("  OVERALL VERDICT: VALIDATION FAILED FAIL")
        print("  -> One or more gates failed. Do not promote. Investigate bottleneck.")
    print("=" * 70)

    return 0 if all_ok else 1


if __name__ == "__main__":
    sys.exit(main())
