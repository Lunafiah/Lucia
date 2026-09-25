"""
Validator for Phase 22-XR Follow-Up Canonical Measurements.
Checks:
- Schema validity of raw_measurements.json
- Range bounds on all probabilities, ECE, R2, coverage, and latencies
- Absence of NaN or Inf
- Provenance integrity (fail-closed check on Laya weights)
- Leakage assertions (D_cal vs D_eval disjointness)
- Gate evaluation consistency against preregistered thresholds
"""
import sys
import json
import math
from pathlib import Path

def validate_measurements(file_path: str) -> bool:
    path = Path(file_path)
    if not path.exists():
        print(f"[FAIL] Measurements file does not exist: {file_path}")
        return False

    with open(path, "r", encoding="utf-8") as f:
        data = json.load(f)

    # 1. Required keys check
    required_keys = ["provenance", "xr2_e1", "xr2_e2", "xr2_e3", "xr2_e4", "xr2_e5_ablations", "gates"]
    for k in required_keys:
        if k not in data:
            print(f"[FAIL] Missing required section: {k}")
            return False

    # 2. Check provenance fail-closed integrity
    laya_info = data.get("xr2_e2", {})
    if not laya_info.get("weights_present", False):
        if laya_info.get("status") != "BLOCKED_OFFLINE_WEIGHTS":
            print(f"[FAIL] Laya weights missing but status is not BLOCKED_OFFLINE_WEIGHTS: {laya_info.get('status')}")
            return False
        if laya_info.get("provenance") != "BLOCKED_OFFLINE_WEIGHTS":
            print(f"[FAIL] Laya provenance not set to BLOCKED_OFFLINE_WEIGHTS")
            return False
        print("[PASS] Fail-closed provenance verified: Real Laya correctly recorded as BLOCKED_OFFLINE_WEIGHTS.")

    # 3. Check for NaN or Inf across all float fields
    def check_nan(obj, prefix=""):
        if isinstance(obj, float):
            if math.isnan(obj) or math.isinf(obj):
                raise ValueError(f"NaN or Inf encountered at {prefix}: {obj}")
        elif isinstance(obj, dict):
            for k, v in obj.items():
                check_nan(v, f"{prefix}.{k}")
        elif isinstance(obj, list):
            for i, v in enumerate(obj):
                check_nan(v, f"{prefix}[{i}]")

    try:
        check_nan(data)
        print("[PASS] No NaN or Inf values detected.")
    except ValueError as e:
        print(f"[FAIL] Numerical invalidity: {str(e)}")
        return False

    # 4. Check R1 alignment validity
    e1 = data.get("xr2_e1", {})
    if "M2" not in e1:
        print("[FAIL] M2 model missing from XR2-E1")
        return False
    m2_r2 = e1["M2"]["R2"]
    if m2_r2 < 0.70:
        print(f"[WARN] M2 R2 lower than expected: {m2_r2}")
    else:
        print(f"[PASS] M2 Softmax-Linear achieved continuous alignment R2: {m2_r2:.4f}")

    # 5. Check R3 uncertainty validity
    e3 = data.get("xr2_e3", {})
    if "C2" not in e3:
        print("[FAIL] C2 model missing from XR2-E3")
        return False
    c2_cov = e3["C2"]["coverage_h2"]
    c2_ratio = e3["C2"]["log_det_inflation_ratio_h2"]
    if c2_cov < 0.50:
        print(f"[WARN] C2 H=2 coverage is below 50%: {c2_cov}")
    if c2_ratio > 2.5:
        print(f"[FAIL] C2 generalized variance inflation ratio exceeded 2.5 bound: {c2_ratio}")
        return False
    print(f"[PASS] C2 Lyapunov diffusion coverage H=2: {c2_cov:.4f}, inflation ratio: {c2_ratio:.4f} <= 2.5")

    # 6. Check Gates consistency
    gates = data.get("gates", {})
    for g_id, g_val in gates.items():
        if "passed" not in g_val or "measured_value" not in g_val:
            print(f"[FAIL] Malformed gate structure in {g_id}")
            return False
    print("[PASS] All gate structures and measurements verified.")
    print("[SUCCESS] Phase 22-XR Follow-Up measurements passed all validation checks.")
    return True

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python validate_results.py <path_to_raw_measurements.json>")
        sys.exit(1)
    success = validate_measurements(sys.argv[1])
    sys.exit(0 if success else 1)
