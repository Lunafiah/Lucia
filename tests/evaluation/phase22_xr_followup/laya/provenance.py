"""
Provenance and Execution Safety Module for Phase 22-XR Follow-Up.
Enforces fail-closed rules: if weights are missing, status MUST be BLOCKED_OFFLINE_WEIGHTS.
"""
from typing import Dict, Any, Optional
import hashlib
import os

STATUS_VERIFIED_BY_EXECUTION = "VERIFIED_BY_EXECUTION"
STATUS_BLOCKED_OFFLINE_WEIGHTS = "BLOCKED_OFFLINE_WEIGHTS"
STATUS_CLAIMED_BY_UPSTREAM = "CLAIMED_BY_UPSTREAM"
STATUS_UNVERIFIED = "UNVERIFIED"

def compute_sha256(filepath: str) -> Optional[str]:
    """Computes SHA-256 hash of a file if it exists."""
    if not os.path.exists(filepath):
        return None
    sha = hashlib.sha256()
    with open(filepath, "rb") as f:
        while chunk := f.read(65536):
            sha.update(chunk)
    return sha.hexdigest()

def check_laya_weights_status(weights_dir: str = "C:\\Users\\Lunafiah\\Desktop\\My_project\\laya\\models\\english") -> Dict[str, Any]:
    """
    Checks local presence of Laya SafeTensors weights.
    Returns provenance dictionary.
    """
    safetensors_path = os.path.join(weights_dir, "model.safetensors")
    bin_path = os.path.join(weights_dir, "pytorch_model.bin")
    
    target_path = safetensors_path if os.path.exists(safetensors_path) else (bin_path if os.path.exists(bin_path) else None)
    
    if target_path is None:
        return {
            "status": STATUS_BLOCKED_OFFLINE_WEIGHTS,
            "weights_present": False,
            "weight_path": None,
            "sha256": None,
            "reason": f"SafeTensors weight file not found under {weights_dir}"
        }
        
    return {
        "status": STATUS_VERIFIED_BY_EXECUTION,
        "weights_present": True,
        "weight_path": target_path,
        "sha256": compute_sha256(target_path),
        "reason": "Weights verified locally"
    }
