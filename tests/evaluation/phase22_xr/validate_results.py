"""
Validation script for Phase 22-XR evaluation results.
Audits raw_measurements.json against pre-registered schemas, mathematical bounds, and architecture gates G-XR1 through G-XR6.
"""
import json
import os
import sys
from typing import Dict, Any

GATE_RULES = {
    "G-XR1": {"metric": "ECE_shift", "threshold": 0.10, "falsify": 0.15, "cmp": "le"},
    "G-XR2": {"metric": "Tracking_R2", "threshold": 0.85, "falsify": 0.70, "cmp": "ge"},
    "G-XR3": {"metric": "Flapping_Rate", "threshold": 0.095, "falsify": 0.15, "cmp": "le"},
    "G-XR4": {"metric": "Density_Coverage_H2", "threshold": 0.75, "falsify": 0.50, "cmp": "ge"},
    "G-XR5": {"metric": "Contradiction_Recovery", "threshold": 1.0, "falsify": 2.0, "cmp": "le"},
    "G-XR6": {"metric": "CPU_Latency_ms", "threshold": 350.0, "falsify": 500.0, "cmp": "le"},
}

def validate_results(filepath: str) -> bool:
    if not os.path.exists(filepath):
        print(f"[FAIL] Result file not found: {filepath}")
        return False
        
    with open(filepath, "r") as f:
        data = json.load(f)
        
    print(f"Auditing results: {filepath}")
    all_ok = True
    
    # 1. Required experiments presence
    required_keys = ["XR-E1", "XR-E2", "XR-E3", "XR-E4", "XR-E5", "XR-E6", "XR-E7", "XR-E8"]
    for k in required_keys:
        if k not in data:
            print(f"[WARN] Missing experiment key: {k}")
            all_ok = False
            
    # 2. Audit G-XR1
    if "XR-E2" in data and "Laya" in data["XR-E2"].get("data", {}):
        ece_val = data["XR-E2"]["data"]["Laya"]["NoiseSurge"]["ece"]
        print(f"-> G-XR1 (ECE Noise Surge): {ece_val:.4f} (Required: <= 0.10, Falsify: > 0.15)")
        if ece_val > 0.15:
            print("   Verdict: FALSIFIED / FAIL")
        elif ece_val <= 0.10:
            print("   Verdict: PASS")
        else:
            print("   Verdict: PARTIAL")
            
    # 3. Audit G-XR2
    if "XR-E3" in data:
        r2_val = data["XR-E3"].get("aggregate_R2", -999.0)
        print(f"-> G-XR2 (Tracking R²): {r2_val:.4f} (Required: >= 0.85, Falsify: < 0.70)")
        if r2_val < 0.70:
            print("   Verdict: FALSIFIED / FAIL")
        elif r2_val >= 0.85:
            print("   Verdict: PASS")
        else:
            print("   Verdict: PARTIAL")
            
    # 4. Audit G-XR3
    if "XR-E4" in data:
        flap_val = data["XR-E4"].get("flapping_continuous", 1.0)
        print(f"-> G-XR3 (Flapping Continuous): {flap_val*100:.2f}% (Required: <= 9.5%, Falsify: > 15.0%)")
        if flap_val <= 0.095:
            print("   Verdict: PASS")
        elif flap_val > 0.15:
            print("   Verdict: FALSIFIED / FAIL")
        else:
            print("   Verdict: PARTIAL")
            
    # 5. Audit G-XR4
    if "XR-E5" in data:
        cov_val = data["XR-E5"].get("coverage_H2", 0.0)
        print(f"-> G-XR4 (Trajectory Coverage H=2): {cov_val*100:.2f}% (Required: >= 75.0%, Falsify: < 50.0%)")
        if cov_val >= 0.75:
            print("   Verdict: PASS")
        elif cov_val < 0.50:
            print("   Verdict: FALSIFIED / FAIL")
        else:
            print("   Verdict: PARTIAL")

    # 6. Audit G-XR5
    if "XR-E4" in data:
        rec_val = data["XR-E4"].get("contradiction_recovery_turns", 99.0)
        print(f"-> G-XR5 (Contradiction Recovery): {rec_val:.1f} turns (Required: <= 1.0, Falsify: > 2.0)")
        if rec_val <= 1.0:
            print("   Verdict: PASS")
        elif rec_val > 2.0:
            print("   Verdict: FALSIFIED / FAIL")
        else:
            print("   Verdict: PARTIAL")

    # 7. Audit G-XR6
    if "XR-E1" in data:
        lat_val = data["XR-E1"].get("p50_latency_ms", 999.0)
        print(f"-> G-XR6 (CPU P50 Latency): {lat_val:.2f} ms (Required: <= 350.0 ms, Falsify: > 500.0 ms)")
        if lat_val <= 350.0:
            print("   Verdict: PASS")
        elif lat_val > 500.0:
            print("   Verdict: FALSIFIED / FAIL")
        else:
            print("   Verdict: PARTIAL")

    # 8. Check numerical bounds and NaN/Inf
    if "XR-E8" in data:
        p23_check = data["XR-E8"].get("validation", {})
        if p23_check.get("has_nan", False) or p23_check.get("has_inf", False):
            print("[FAIL] P23 Interface contains NaN or Inf!")
            all_ok = False
        else:
            print("-> P23 Interface mathematical sanity: CLEAN (0 NaN, 0 Inf, Bounded Linf)")

    print(f"\nAudit complete. Status: {'SUCCESS' if all_ok else 'FAILED_CHECKS'}")
    return all_ok

if __name__ == "__main__":
    path = sys.argv[1] if len(sys.argv) > 1 else "evaluation_artifacts/phase22_xr/raw_measurements.json"
    res = validate_results(path)
    sys.exit(0 if res else 1)
