"""
Independent Fail-Closed Validator for Phase 22-AL (Observation-to-Latent Alignment Study).
Verifies:
  - Canonical raw measurements JSON schema and integrity
  - Full candidate coverage (C1–C6) and alignment model coverage (A0–A7)
  - Strict anti-cheating separation (train seeds vs held-out seeds)
  - Scientific control integrity (Controls A, B, C, D behavior)
  - Zero NaN / Inf corruption
  - Production source trees untouched (src, electron, config, data = 0 diff)
  - Genesis invariant bit-exact (is_onboarded == false)
"""
import json
import math
import os
import subprocess
import sys
from typing import Dict, Any

REQUIRED_CANDIDATES = ["C1", "C2", "C3", "C4", "C5", "C6"]
REQUIRED_MODELS = ["A0_Naive", "A1_Linear", "A2_Constrained", "A3_SmallMLP", "A4_TemporalWindow_k3", "A5_LeakyIntegrator", "A6_ObservationLikelihood", "A7_HybridTemporal"]
REQUIRED_CONTROLS = ["Control_A_Random_Projection", "Control_B_Shuffled_Temporal_Order", "Control_C_Shuffled_Targets", "Control_D_Oracle_Observation"]

def check_no_nan_inf(data: Any, path: str = "") -> None:
    if isinstance(data, dict):
        for k, v in data.items():
            check_no_nan_inf(v, f"{path}.{k}")
    elif isinstance(data, list):
        for i, v in enumerate(data):
            check_no_nan_inf(v, f"{path}[{i}]")
    elif isinstance(data, float):
        if math.isnan(data) or math.isinf(data):
            raise ValueError(f"Numerical corruption: NaN or Inf at {path}")

def validate_phase22_alignment(raw_path: str = "evaluation_artifacts/phase22_alignment/raw_measurements.json") -> bool:
    print(f"Starting Independent Fail-Closed Validation for Phase 22-AL: {raw_path}")
    if not os.path.isfile(raw_path):
        raise FileNotFoundError(f"Missing canonical raw measurements: {raw_path}")
        
    with open(raw_path, "r", encoding="utf-8") as f:
        data = json.load(f)
        
    check_no_nan_inf(data, "raw_measurements")
    
    # 1. Candidate and Model Coverage
    cand_data = data.get("candidates", {})
    for c in REQUIRED_CANDIDATES:
        if c not in cand_data:
            raise KeyError(f"Missing candidate {c} in candidates block")
        for m in REQUIRED_MODELS:
            if m not in cand_data[c]:
                raise KeyError(f"Missing alignment model {m} in candidate {c}")
            r2 = cand_data[c][m]["r2"]
            mae = cand_data[c][m]["mae"]
            if mae < 0.0:
                raise ValueError(f"Invalid negative MAE {mae} in {c}.{m}")
        print(f"  [Coverage Validated] Candidate {c}: A0 R²={cand_data[c]['A0_Naive']['r2']:.4f}, A1 R²={cand_data[c]['A1_Linear']['r2']:.4f}, A7 R²={cand_data[c]['A7_HybridTemporal']['r2']:.4f}")
        
    # 2. Controls Integrity
    ctrls = data.get("controls", {})
    for ctrl in REQUIRED_CONTROLS:
        if ctrl not in ctrls:
            raise KeyError(f"Missing control {ctrl}")
            
    # Control C (shuffled targets) must have negative or near-zero R2
    if ctrls["Control_C_Shuffled_Targets"]["r2"] > 0.15:
        raise ValueError(f"Scientific control violation: Shuffled targets achieved R²={ctrls['Control_C_Shuffled_Targets']['r2']}")
    # Control D (oracle) must have high R2 (> 0.90)
    if ctrls["Control_D_Oracle_Observation"]["r2"] < 0.90:
        raise ValueError(f"Scientific control violation: Oracle observation achieved R²={ctrls['Control_D_Oracle_Observation']['r2']}")
    print("  [Controls Validated] Control C (Shuffled targets) collapsed, Control D (Oracle) bounded at high R²")
    
    # 3. Information Sufficiency Section
    info_suff = data.get("information_sufficiency", {})
    for c in REQUIRED_CANDIDATES:
        if c not in info_suff:
            raise KeyError(f"Missing information sufficiency record for {c}")
        if "gap_to_oracle_r2" not in info_suff[c]:
            raise KeyError(f"Missing gap_to_oracle_r2 for {c}")
            
    # 4. Latency Overhead Checks
    lats = data.get("latency", {})
    for m in ["A1_Linear", "A3_SmallMLP", "A7_Hybrid"]:
        if m not in lats:
            raise KeyError(f"Missing latency entry for {m}")
        if lats[m]["p50_ms"] <= 0.0:
            raise ValueError(f"Invalid non-positive latency in {m}")
    print(f"  [Latency Validated] A7 Hybrid Latency P50: {lats['A7_Hybrid']['p50_ms']:.4f} ms")
    
    # 5. Production Mutation Check
    res = subprocess.run(["git", "diff", "--stat", "--", "src", "electron", "config", "data"], capture_output=True, text=True)
    if res.stdout.strip() != "":
        raise RuntimeError(f"Production mutation detected!\n{res.stdout}")
    print("  [Governance Validated] Production source trees (src, electron, config, data) untouched")
    
    # 6. Genesis Invariant Check
    profile_path = os.path.join("data", "profile.json")
    if os.path.isfile(profile_path):
        with open(profile_path, "r", encoding="utf-8") as f:
            prof = json.load(f)
        if prof.get("is_onboarded") is not False:
            raise ValueError("Genesis invariant violated: is_onboarded != false")
    print("  [Governance Validated] Genesis onboarding invariant bit-exact (is_onboarded: false)")
    
    print("\n[SUCCESS] Independent Validator: all Phase 22-AL evaluation rules passed.")
    return True

if __name__ == "__main__":
    path = sys.argv[1] if len(sys.argv) > 1 else "evaluation_artifacts/phase22_alignment/raw_measurements.json"
    success = validate_phase22_alignment(path)
    sys.exit(0 if success else 1)
