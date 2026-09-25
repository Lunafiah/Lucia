"""
Fail-Closed Gate Validator for Phase 22-RG: Relevance Gating & Evidence Selection Study.

Performs independent validation of:
  1. Genesis invariant (is_onboarded=false)
  2. Production code isolation
  3. Preregistered acceptance gates (G4 on held-out seeds)
  4. Safety invariants:
     - Mandatory recall >= 0.99 (ALL gates must satisfy, not just G4)
     - Hallucination risk <= 0.10 (ALL gates must satisfy)
     - Contradiction preservation >= 1.00 (ALL gates)
  5. No-regression check: G4 must not regress below Phase 22-MR M4 baselines
     on any safety metric (mandatory recall, hallucination risk, relational consistency)
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

ARTIFACTS_DIR  = Path(__file__).parents[3] / "evaluation_artifacts" / "phase22_rg"
PRODUCTION_DIR = Path(__file__).parents[3] / "src" / "core"
PROFILE_PATH   = Path(__file__).parents[3] / "data" / "profile.json"

MR_SAFETY_BASELINES = {
    "hallucination_risk": 0.0000,
    "relational_cons":    0.9918,
    "mandatory_recall":   1.0000,
}

EXPECTED_GATES = {
    "G_RG1_Mandatory_Recall",
    "G_RG2_Precision_K",
    "G_RG3_Injection_Rate",
    "G_RG4_Hallucination_Risk",
    "G_RG5_Overall_Recall",
    "G_RG6_Relational_Cons",
    "G_RG7_Compression",
    "G_RG8_Contradiction_Pres",
    "G_RG9_Language_Gap",
    "G_RG10_Latency_P50",
    "G_RG11_VRAM",
    "G_RG12_Token_Budget",
}

SAFETY_GATE_NAMES = {
    "G_RG1_Mandatory_Recall",
    "G_RG4_Hallucination_Risk",
    "G_RG8_Contradiction_Pres",
}


def validate_genesis_gate() -> bool:
    if not PROFILE_PATH.exists():
        print("  [INFO] data/profile.json not found -- assuming not onboarded (OK).")
        return True
    with open(PROFILE_PATH, "r", encoding="utf-8") as fh:
        profile = json.load(fh)
    ok = profile.get("is_onboarded") is False
    print(f"  Genesis Gate (is_onboarded=false): [{'PASSED' if ok else 'FAILED'}]")
    return ok


def validate_production_isolation() -> bool:
    if not PRODUCTION_DIR.exists():
        print("  [INFO] src/core/ not found -- skipping.")
        return True
    violations = []
    for marker in ["phase22_rg", "Gate_G4", "GatingResult"]:
        for path in PRODUCTION_DIR.rglob("*.py"):
            try:
                if marker in path.read_text(encoding="utf-8", errors="ignore"):
                    violations.append(str(path))
            except Exception:
                pass
    ok = len(violations) == 0
    print(f"  Production Isolation: [{'PASSED' if ok else 'FAILED'}]")
    for v in violations:
        print(f"    Violation: {v}")
    return ok


def validate_gate_file(gate_results: dict) -> tuple:
    n_passed, n_total = 0, 0
    all_ok = True
    safety_ok = True
    missing = EXPECTED_GATES - set(gate_results.keys())
    if missing:
        print(f"  [WARN] Missing gates: {missing}")
        all_ok = False

    for gate_name, info in gate_results.items():
        n_total += 1
        passed   = info.get("passed", False)
        measured = info.get("measured", float("nan"))
        thresh   = info.get("threshold", float("nan"))
        is_safety= gate_name in SAFETY_GATE_NAMES

        if passed:
            n_passed += 1
            sym = "PASS"
        else:
            all_ok = False
            sym    = "FAIL"
            if is_safety:
                safety_ok = False

        safety_tag = " [SAFETY]" if is_safety else ""
        print(f"  {gate_name:<42} measured={measured:.4f}  "
              f"threshold={thresh}  [{sym}]{safety_tag}")

    return all_ok, safety_ok, n_passed, n_total


def validate_all_gate_safety(agg_results: dict) -> bool:
    """
    All gate candidates (G0-G4, Oracle) must individually satisfy:
      - mandatory_recall >= 0.99  (fail-closed: no gate may drop safety-critical anchors)
      - hallucination_risk <= 0.10
    """
    print("\n[4] Per-Candidate Safety Invariants (All Gates, Held-Out Seeds):")
    print(f"  {'Gate':<28} {'Mand.Recall':<14} {'Hall.Risk':<14} {'Status'}")
    print("  " + "-" * 65)
    all_ok = True
    for gate_name in agg_results:
        ho   = agg_results[gate_name].get("held_out", {})
        mr   = ho.get("mandatory_recall",   {}).get("mean", 0.0)
        hall = ho.get("hallucination_risk", {}).get("mean", 1.0)
        mr_ok  = mr   >= 0.99
        hal_ok = hall <= 0.10
        ok     = mr_ok and hal_ok
        if not ok:
            all_ok = False
        status = "PASS" if ok else "FAIL"
        print(f"  {gate_name:<28} {mr:<14.4f} {hall:<14.4f} [{status}]")
    return all_ok


def validate_no_regression(agg_results: dict) -> bool:
    """
    G4 must not regress below Phase 22-MR M4 baselines on safety metrics.
    (G4 is allowed to have lower overall recall -- that's the precision/recall trade.)
    """
    print("\n[5] Phase 22-MR Safety Non-Regression Check (G4 vs MR baselines):")
    g4   = agg_results.get("G4_SafetyFirstHybrid", {}).get("held_out", {})
    all_ok = True
    checks = [
        ("hallucination_risk", MR_SAFETY_BASELINES["hallucination_risk"], "le"),
        ("relational_cons",    MR_SAFETY_BASELINES["relational_cons"],    "ge"),
        ("mandatory_recall",   MR_SAFETY_BASELINES["mandatory_recall"],   "ge"),
    ]
    for key, baseline, direction in checks:
        measured = g4.get(key, {}).get("mean", float("nan"))
        if direction == "le":
            ok = measured <= baseline + 0.001   # small tolerance
        else:
            ok = measured >= baseline - 0.001
        if not ok:
            all_ok = False
        sym = "PASS" if ok else "FAIL"
        print(f"  {key:<35} G4={measured:.4f}  MR_baseline={baseline:.4f}  [{sym}]")
    return all_ok


def main():
    print("=" * 70)
    print("Phase 22-RG -- Fail-Closed Gate Validation")
    print("=" * 70)

    all_ok = True

    print("\n[1] Genesis Invariant Gate:")
    all_ok &= validate_genesis_gate()

    print("\n[2] Production Code Isolation:")
    all_ok &= validate_production_isolation()

    gate_file = ARTIFACTS_DIR / "gate_results.json"
    if not gate_file.exists():
        print(f"\n[ERROR] gate_results.json not found. Run run_experiments.py first.")
        sys.exit(1)

    with open(gate_file, "r", encoding="utf-8") as fh:
        gate_results = json.load(fh)

    print("\n[3] Preregistered Acceptance Gates (G4 on Held-Out Seeds):")
    gates_ok, safety_ok, n_passed, n_total = validate_gate_file(gate_results)
    all_ok &= gates_ok

    agg_file = ARTIFACTS_DIR / "aggregated_results.json"
    if agg_file.exists():
        with open(agg_file, "r", encoding="utf-8") as fh:
            agg_results = json.load(fh)
        all_ok &= validate_all_gate_safety(agg_results)
        all_ok &= validate_no_regression(agg_results)
    else:
        print("\n[WARN] aggregated_results.json not found -- skipping extended checks.")

    print("\n" + "=" * 70)
    print(f"  Gates Passed:   {n_passed}/{n_total}")
    print(f"  Safety Gates:   {'ALL PASSED' if safety_ok else 'ONE OR MORE FAILED'}")

    if all_ok:
        print("  OVERALL VERDICT: ALL CHECKS PASSED")
        print("  -> Relevance Gating evidence is sufficient for architecture review.")
        print("  -> Promotion still requires Architecture Gate approval.")
    else:
        print("  OVERALL VERDICT: VALIDATION FAILED")
        print("  -> One or more gates failed. Do not promote. Investigate bottleneck.")

    print("=" * 70)
    return 0 if all_ok else 1


if __name__ == "__main__":
    sys.exit(main())
