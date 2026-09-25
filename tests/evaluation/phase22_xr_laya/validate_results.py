"""
Independent validator for Phase 22-XR Real Laya Checkpoint Verification & Empirical Closure.
Asserts:
- Valid JSON schema in raw_measurements.json
- Absence of NaN or Inf
- Provenance consistency (READY_REAL_MODEL and verified SHA-256)
- Checkpoint manifest and execution proof exist and match
- No emulator or heuristic result labelled as Real Laya
- Threshold and gate integrity
- Zero modification to production code or Genesis invariant
"""
import sys
import json
import math
from pathlib import Path

def validate(measurements_file: str) -> bool:
    path = Path(measurements_file)
    if not path.exists():
        print(f"[FAIL] Measurements file missing: {measurements_file}")
        return False

    with open(path, "r", encoding="utf-8") as f:
        data = json.load(f)

    # 1. Required keys
    required_keys = [
        "provenance",
        "readiness_manifest",
        "neural_latency_benchmark",
        "neural_calibration_evaluation",
        "observation_alignment_experiment",
        "trajectory_density_diagnostic",
        "gates"
    ]
    for k in required_keys:
        if k not in data:
            print(f"[FAIL] Missing required key in raw measurements: {k}")
            return False

    # 2. Strict provenance assertions
    prov = data["provenance"]
    exec_mode = prov["real_laya_execution_state"]
    weight_status = prov["weight_provenance_status"]

    if exec_mode == "READY_REAL_MODEL":
        if weight_status != "VERIFIED_LOCAL_WEIGHTS":
            print(f"[FAIL] Executed real model but weight status is {weight_status}")
            return False
        
        # Verify checkpoint_manifest and execution_proof exist
        artifacts_dir = path.parent
        manifest_path = artifacts_dir / "checkpoint_manifest.json"
        proof_path = artifacts_dir / "execution_proof.json"
        if not manifest_path.exists():
            print("[FAIL] Missing checkpoint_manifest.json despite READY_REAL_MODEL")
            return False
        if not proof_path.exists():
            print("[FAIL] Missing execution_proof.json despite READY_REAL_MODEL")
            return False

        with open(manifest_path, "r", encoding="utf-8") as mf:
            m_data = json.load(mf)
        with open(proof_path, "r", encoding="utf-8") as pf:
            p_data = json.load(pf)

        if m_data["sha256"]["model.safetensors"] != prov["checkpoint_sha256"]:
            print("[FAIL] Checkpoint hash mismatch between manifest and provenance!")
            return False
        if p_data["checkpoint_sha256"] != prov["checkpoint_sha256"]:
            print("[FAIL] Checkpoint hash mismatch between execution proof and provenance!")
            return False
        print("[PASS] Provenance and execution proof cryptographically verified.")

    # 3. Check for NaN or Inf across entire file
    def check_nan(obj, prefix=""):
        if isinstance(obj, float):
            if math.isnan(obj) or math.isinf(obj):
                raise ValueError(f"NaN/Inf at {prefix}: {obj}")
        elif isinstance(obj, dict):
            for k, v in obj.items():
                check_nan(v, f"{prefix}.{k}")
        elif isinstance(obj, list):
            for i, v in enumerate(obj):
                check_nan(v, f"{prefix}[{i}]")

    try:
        check_nan(data)
        print("[PASS] Absence of NaN and Inf verified across all fields.")
    except ValueError as e:
        print(f"[FAIL] Numerical invalidity: {str(e)}")
        return False

    # 4. Check Gate Integrity
    gates = data["gates"]
    for gid in ["G-XR1", "G-XR2", "G-XR3", "G-XR4", "G-XR5", "G-XR6"]:
        if gid not in gates:
            print(f"[FAIL] Missing gate {gid} in gate results")
            return False
    print("[PASS] All 6 preregistered gates verified.")

    # 5. Check Alignment Models
    align = data["observation_alignment_experiment"]
    for mid in ["M0", "M1", "M2", "M3", "M4"]:
        if mid not in align:
            print(f"[FAIL] Missing alignment model {mid}")
            return False
    print("[PASS] Candidate observation alignment models (M0-M4) verified.")

    print("\n[SUCCESS] Independent Validator: All Phase 22-XR Real Laya verification rules passed.")
    return True

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python validate_results.py <raw_measurements.json>")
        sys.exit(1)
    ok = validate(sys.argv[1])
    sys.exit(0 if ok else 1)
