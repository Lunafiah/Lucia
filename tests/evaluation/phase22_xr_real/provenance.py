"""Provenance verification and inspection for Real Laya checkpoint and repository."""

import hashlib
import json
import os
import platform
import sys
from pathlib import Path
from typing import Any, Dict, Optional, Tuple

from tests.evaluation.phase22_xr_real.config import (
    ARTIFACTS_DIR,
    EXPECTED_BASE_MODEL,
    LAYA_CHECKPOINT_ID,
    LAYA_REPO_DIR,
)


def get_git_commit(repo_path: Path) -> Optional[str]:
    """Retrieve git HEAD commit if available."""
    head_file = repo_path / ".git" / "HEAD"
    if not head_file.exists():
        return None
    try:
        content = head_file.read_text(encoding="utf-8").strip()
        if content.startswith("ref:"):
            ref_path = repo_path / ".git" / content.split(" ", 1)[1].strip()
            if ref_path.exists():
                return ref_path.read_text(encoding="utf-8").strip()
        else:
            return content
    except Exception:
        return None
    return None


def calculate_sha256(filepath: Path, max_bytes: int = 10 * 1024 * 1024) -> str:
    """Calculate SHA256 of a file (or first max_bytes for large files)."""
    hasher = hashlib.sha256()
    with open(filepath, "rb") as f:
        chunk = f.read(65536)
        bytes_read = 0
        while chunk and bytes_read < max_bytes:
            hasher.update(chunk)
            bytes_read += len(chunk)
            chunk = f.read(65536)
    return hasher.hexdigest()


def audit_laya_offline_weights() -> Dict[str, Any]:
    """Inspect local repository and HF cache for genuine Laya neural weights."""
    status: Dict[str, Any] = {
        "status": "BLOCKED_OFFLINE_WEIGHTS",
        "checkpoint_id": LAYA_CHECKPOINT_ID,
        "base_model": EXPECTED_BASE_MODEL,
        "laya_repo_exists": LAYA_REPO_DIR.exists(),
        "git_commit": None,
        "weight_files_found": [],
        "hf_cache_found": False,
        "weight_bytes": 0,
        "has_weights": False,
        "details": "",
    }

    if LAYA_REPO_DIR.exists():
        status["git_commit"] = get_git_commit(LAYA_REPO_DIR)
        
        # Check repo paths for safetensors or bin files
        candidate_paths = [
            LAYA_REPO_DIR / "model.safetensors",
            LAYA_REPO_DIR / "pytorch_model.bin",
            LAYA_REPO_DIR / "weights" / "model.safetensors",
            LAYA_REPO_DIR / "checkpoints",
            LAYA_REPO_DIR / "models",
        ]
        
        for p in candidate_paths:
            if p.is_file() and p.stat().st_size > 10 * 1024 * 1024:
                status["weight_files_found"].append({
                    "path": str(p),
                    "size_bytes": p.stat().st_size,
                    "sha256_head": calculate_sha256(p),
                })
                status["weight_bytes"] += p.stat().st_size
            elif p.is_dir():
                for sub in p.glob("**/*"):
                    if sub.is_file() and (sub.suffix in [".safetensors", ".bin"] or "weight" in sub.name) and sub.stat().st_size > 10 * 1024 * 1024:
                        status["weight_files_found"].append({
                            "path": str(sub),
                            "size_bytes": sub.stat().st_size,
                            "sha256_head": calculate_sha256(sub),
                        })
                        status["weight_bytes"] += sub.stat().st_size

    # Check Hugging Face hub cache directory
    hf_home = os.environ.get("HF_HOME")
    if not hf_home:
        user_home = Path.home()
        hf_cache = user_home / ".cache" / "huggingface" / "hub"
    else:
        hf_cache = Path(hf_home) / "hub"

    if hf_cache.exists():
        laya_cache_dirs = list(hf_cache.glob("*laya*")) + list(hf_cache.glob("*convaiinnovations--laya*"))
        if laya_cache_dirs:
            status["hf_cache_found"] = True
            for d in laya_cache_dirs:
                for f in d.glob("**/*"):
                    if f.is_file() and f.stat().st_size > 10 * 1024 * 1024:
                        status["weight_files_found"].append({
                            "path": str(f),
                            "size_bytes": f.stat().st_size,
                            "sha256_head": calculate_sha256(f),
                        })
                        status["weight_bytes"] += f.stat().st_size

    if status["weight_files_found"] and status["weight_bytes"] > 100 * 1024 * 1024:
        status["has_weights"] = True
        status["status"] = "READY_REAL_MODEL"
        status["details"] = f"Found {len(status['weight_files_found'])} weight file(s), total {status['weight_bytes']} bytes."
    else:
        status["has_weights"] = False
        status["status"] = "BLOCKED_OFFLINE_WEIGHTS"
        status["details"] = (
            f"No offline weights (>100MB safetensors/bin) found for {LAYA_CHECKPOINT_ID} "
            f"in {LAYA_REPO_DIR} or HF cache {hf_cache}. Fail-closed invariant activated."
        )

    return status


def create_model_manifest_and_provenance() -> Tuple[Dict[str, Any], Dict[str, Any]]:
    """Generate model_manifest.json and provenance.json dictionaries."""
    weight_audit = audit_laya_offline_weights()
    
    provenance = {
        "evaluation_phase": "Phase 22-XR-L",
        "task": "Real Laya Observation Verification",
        "execution_mode": weight_audit["status"],
        "checkpoint_id": LAYA_CHECKPOINT_ID,
        "base_model": EXPECTED_BASE_MODEL,
        "laya_repository": {
            "path": str(LAYA_REPO_DIR),
            "exists": weight_audit["laya_repo_exists"],
            "git_commit": weight_audit["git_commit"],
        },
        "weights_present": weight_audit["has_weights"],
        "weight_files": weight_audit["weight_files_found"],
        "system_environment": {
            "os": platform.platform(),
            "python_version": sys.version,
            "architecture": platform.architecture(),
            "machine": platform.machine(),
            "processor": platform.processor(),
        },
        "fail_closed_triggered": not weight_audit["has_weights"],
        "fail_closed_reason": weight_audit["details"],
    }

    manifest = {
        "model_id": LAYA_CHECKPOINT_ID,
        "base_architecture": "ModernBERT-large (421M parameters)",
        "intended_task": "Categorical Next-Action Probe (6 classes)",
        "output_format": "Logits / Softmax over 6 discrete action categories",
        "required_files": [
            "config.json",
            "model.safetensors",
            "tokenizer.json",
            "tokenizer_config.json",
            "rl_agent_config.json"
        ],
        "local_availability": {
            "status": weight_audit["status"],
            "verified_offline": weight_audit["has_weights"],
            "sha256": [f["sha256_head"] for f in weight_audit["weight_files_found"]] if weight_audit["weight_files_found"] else None,
        },
        "research_invariants": {
            "fail_closed_rule": "If weights are missing, DO NOT substitute emulator or call cloud API. Report BLOCKED_OFFLINE_WEIGHTS.",
            "emulation_forbidden": True,
            "production_impact": "Zero. src/core/** and electron/** untouched."
        }
    }

    return provenance, manifest


if __name__ == "__main__":
    prov, man = create_model_manifest_and_provenance()
    print(json.dumps(prov, indent=2))
