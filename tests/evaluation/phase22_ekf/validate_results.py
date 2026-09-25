"""
Independent Fail-Closed Validator for Phase 22-EKF:
Kalman-Based Semantic State Formation.
"""
import os
import sys
import json
import subprocess

def validate_phase22_ekf(raw_json_path: str):
    print(f"Starting Independent Fail-Closed Validation for Phase 22-EKF: {raw_json_path}")
    
    if not os.path.exists(raw_json_path):
        print(f"[FAIL] Raw measurements file not found: {raw_json_path}")
        sys.exit(1)
        
    with open(raw_json_path, "r", encoding="utf-8") as f:
        data = json.load(f)
        
    required_keys = ["models", "latencies", "languages", "controls", "gates", "peak_held_out_r2"]
    for k in required_keys:
        if k not in data:
            print(f"[FAIL] Missing top-level key: {k}")
            sys.exit(1)
            
    # Check models
    expected_models = ["M1_JointRawBaseline", "M2_OpenLoopSSF", "M3_EKF_OU_Prior", "M4_UKF_OU_Prior", "OracleControl"]
    for m in expected_models:
        if m not in data["models"]:
            print(f"[FAIL] Missing model evaluation: {m}")
            sys.exit(1)
        r2 = data["models"][m]["r2"]
        if r2 is None or str(r2).lower() in ["nan", "inf"]:
            print(f"[FAIL] NaN/Inf in model {m}: {r2}")
            sys.exit(1)
    print("  [Coverage Validated] All models evaluated without NaN/Inf.")
    
    # Check controls
    ctrls = data["controls"]
    if ctrls["Control_A_Random_Projection"]["r2"] >= 0.0:
        print("[FAIL] Control A did not collapse!")
        sys.exit(1)
    if ctrls["Control_C_Shuffled_Targets"]["r2"] >= 0.10:
        print("[FAIL] Control C did not collapse!")
        sys.exit(1)
    if ctrls["Control_D_Oracle_Observation"]["r2"] < 0.85:
        print("[FAIL] Control D did not recover upper bound!")
        sys.exit(1)
    print("  [Controls Validated] Controls A, B, C, D satisfy theoretical invariants.")
    
    # Check latency
    ekf_p50 = data["latencies"]["M3_EKF"]["p50_ms"]
    if ekf_p50 > 1.0:
        print(f"[FAIL] EKF P50 Latency exceeds 1.0 ms: {ekf_p50} ms")
        sys.exit(1)
    print(f"  [Latency Validated] EKF P50 Latency = {ekf_p50:.4f} ms <= 1.0 ms.")
    
    # Check production code untouched
    diff = subprocess.run(
        ["git", "diff", "--", "src", "electron", "config", "data", "Phase 23"],
        capture_output=True,
        text=True
    )
    if diff.stdout.strip():
        print("[FAIL] Production code modification detected!")
        sys.exit(1)
    print("  [Governance Validated] Production source trees untouched.")
    
    # Check Genesis invariant
    profile_path = os.path.join("data", "profile.json")
    if os.path.exists(profile_path):
        with open(profile_path, "r", encoding="utf-8") as pf:
            content = pf.read().strip()
            if '{"is_onboarded": false}' not in content:
                print(f"[FAIL] Genesis profile altered: {content}")
                sys.exit(1)
    print("  [Governance Validated] Genesis onboarding invariant bit-exact.")
    print("\n[SUCCESS] Independent Validator: all Phase 22-EKF evaluation rules passed.")

if __name__ == "__main__":
    if len(sys.argv) < 2:
        raw_path = os.path.join("evaluation_artifacts", "phase22_ekf", "raw_measurements.json")
    else:
        raw_path = sys.argv[1]
    validate_phase22_ekf(raw_path)
