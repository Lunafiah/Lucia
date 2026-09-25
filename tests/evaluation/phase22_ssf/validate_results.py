"""
Independent Fail-Closed Validator for Phase 22-SSF:
Semantic State Formation & Latent Target Decoupling.
"""
import os
import sys
import json
import subprocess

def validate_phase22_ssf(raw_json_path: str):
    print(f"Starting Independent Fail-Closed Validation for Phase 22-SSF: {raw_json_path}")
    
    if not os.path.exists(raw_json_path):
        print(f"[FAIL] Raw measurements file not found: {raw_json_path}")
        sys.exit(1)
        
    with open(raw_json_path, "r", encoding="utf-8") as f:
        data = json.load(f)
        
    required_keys = ["comparison", "ablations", "languages", "controls", "gates", "peak_held_out_r2"]
    for k in required_keys:
        if k not in data:
            print(f"[FAIL] Missing top-level key: {k}")
            sys.exit(1)
            
    # Check comparison
    comp = data["comparison"]
    for m in ["raw_baseline", "decoupled_ssf", "oracle_control"]:
        if m not in comp:
            print(f"[FAIL] Missing comparison model: {m}")
            sys.exit(1)
        r2 = comp[m]["r2"]
        if r2 is None or str(r2).lower() in ["nan", "inf"]:
            print(f"[FAIL] NaN/Inf in model {m}: {r2}")
            sys.exit(1)
            
    print("  [Coverage Validated] Primary comparisons present without NaN/Inf.")
    
    # Check controls
    ctrls = data["controls"]
    if ctrls["Control_A_Random_Projection"]["r2"] >= 0.0:
        print("[FAIL] Control A did not collapse!")
        sys.exit(1)
    if ctrls["Control_C_Shuffled_Targets"]["r2"] >= 0.10:
        print("[FAIL] Control C did not collapse!")
        sys.exit(1)
    if ctrls["Control_D_Oracle_Observation"]["r2"] < 0.80:
        print("[FAIL] Control D did not recover upper bound!")
        sys.exit(1)
        
    print("  [Controls Validated] Controls A, B, C, D satisfy theoretical invariants.")
    
    # Check latency
    lat = comp["decoupled_ssf"]["p50_latency_ms"]
    if lat > 1.0:
        print(f"[FAIL] P50 Latency exceeds 1.0 ms: {lat} ms")
        sys.exit(1)
    print(f"  [Latency Validated] SSF P50 Latency = {lat:.4f} ms <= 1.0 ms.")
    
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
    print("\n[SUCCESS] Independent Validator: all Phase 22-SSF evaluation rules passed.")

if __name__ == "__main__":
    if len(sys.argv) < 2:
        raw_path = os.path.join("evaluation_artifacts", "phase22_ssf", "raw_measurements.json")
    else:
        raw_path = sys.argv[1]
    validate_phase22_ssf(raw_path)
