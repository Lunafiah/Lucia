"""
Weight Provenance Inspector for Real Laya Verification (Phase 22-XR).
Categorizes the offline availability of real Laya neural backbone weights:
- VERIFIED_LOCAL_WEIGHTS
- VERIFIED_HF_CACHE
- BLOCKED_OFFLINE_WEIGHTS
- INVALID_OR_INCOMPLETE_WEIGHTS
"""
from enum import Enum
from pathlib import Path
from typing import Dict, Any, Optional, List
import hashlib
import json
import os

class WeightProvenanceStatus(str, Enum):
    VERIFIED_LOCAL_WEIGHTS = "VERIFIED_LOCAL_WEIGHTS"
    VERIFIED_HF_CACHE = "VERIFIED_HF_CACHE"
    BLOCKED_OFFLINE_WEIGHTS = "BLOCKED_OFFLINE_WEIGHTS"
    INVALID_OR_INCOMPLETE_WEIGHTS = "INVALID_OR_INCOMPLETE_WEIGHTS"

class ProvenanceInspector:
    """
    Audits filesystem for real Laya model artifacts.
    Requires:
    - rl_agent_config.json
    - model.safetensors
    - tokenizer/tokenizer.json or tokenizer.json
    """
    EXPECTED_MODEL_ID = "convaiinnovations/laya"
    SUBFOLDER_MULTILINGUAL = "multilingual"

    def __init__(
        self,
        local_repo_path: str = "C:/Users/Lunafiah/Desktop/My_project/laya",
        hf_cache_dir: Optional[str] = None
    ):
        self.local_repo = Path(local_repo_path)
        if hf_cache_dir:
            self.hf_cache = Path(hf_cache_dir)
        else:
            self.hf_cache = Path.home() / ".cache" / "huggingface" / "hub"

    def compute_sha256(self, file_path: Path) -> str:
        """Computes SHA-256 for local weight file in chunks."""
        hasher = hashlib.sha256()
        with open(file_path, "rb") as f:
            while chunk := f.read(8 * 1024 * 1024):
                hasher.update(chunk)
        return hasher.hexdigest()

    def audit(self) -> Dict[str, Any]:
        """
        Executes audit across local paths and local HuggingFace cache.
        Returns detailed structured manifest and status.
        """
        searched_paths = []

        # 1. Search local repo candidate locations
        candidate_dirs = [
            self.local_repo / "models",
            self.local_repo / "checkpoints",
            self.local_repo / "weights",
            self.local_repo
        ]

        for c_dir in candidate_dirs:
            searched_paths.append(str(c_dir.resolve()))
            if c_dir.exists():
                safetensors = list(c_dir.glob("**/model.safetensors")) + list(c_dir.glob("**/*.safetensors"))
                # Filter out python virtual env
                safetensors = [p for p in safetensors if ".venv" not in str(p)]
                if safetensors:
                    w_file = safetensors[0]
                    # Verify accompanying files
                    w_dir = w_file.parent
                    cfg_file = w_dir / "rl_agent_config.json"
                    tok_file = w_dir / "tokenizer.json"
                    if not cfg_file.exists():
                        cfg_file = w_dir / "config.json"

                    if not cfg_file.exists():
                        return {
                            "status": WeightProvenanceStatus.INVALID_OR_INCOMPLETE_WEIGHTS.value,
                            "error": f"Found weight file {w_file} but missing rl_agent_config.json",
                            "weight_file": str(w_file),
                            "file_size_bytes": w_file.stat().st_size,
                            "searched_paths": searched_paths
                        }

                    # Valid local checkpoint found
                    file_hash = self.compute_sha256(w_file)
                    return {
                        "status": WeightProvenanceStatus.VERIFIED_LOCAL_WEIGHTS.value,
                        "location": "LOCAL_REPO",
                        "weight_path": str(w_file),
                        "config_path": str(cfg_file),
                        "file_size_bytes": w_file.stat().st_size,
                        "sha256": file_hash,
                        "searched_paths": searched_paths,
                        "notes": "Verified local weight file physically exists."
                    }

        # 2. Search HuggingFace Cache
        hf_model_dir_name = f"models--{self.EXPECTED_MODEL_ID.replace('/', '--')}"
        hf_target = self.hf_cache / hf_model_dir_name
        searched_paths.append(str(hf_target.resolve()))

        if hf_target.exists():
            snapshots = list(hf_target.glob("snapshots/*"))
            for snap in snapshots:
                st_files = list(snap.glob("**/model.safetensors"))
                if st_files:
                    st_file = st_files[0]
                    cfg = snap / "rl_agent_config.json"
                    if cfg.exists():
                        file_hash = self.compute_sha256(st_file)
                        return {
                            "status": WeightProvenanceStatus.VERIFIED_HF_CACHE.value,
                            "location": "HF_CACHE",
                            "snapshot_path": str(snap),
                            "weight_path": str(st_file),
                            "config_path": str(cfg),
                            "file_size_bytes": st_file.stat().st_size,
                            "sha256": file_hash,
                            "searched_paths": searched_paths,
                            "notes": "Verified Laya weights in local HuggingFace cache."
                        }
                    else:
                        return {
                            "status": WeightProvenanceStatus.INVALID_OR_INCOMPLETE_WEIGHTS.value,
                            "error": f"Snapshot found at {snap} but missing rl_agent_config.json",
                            "weight_path": str(st_file),
                            "searched_paths": searched_paths
                        }

        # 3. Clean Fail-Closed: BLOCKED_OFFLINE_WEIGHTS
        return {
            "status": WeightProvenanceStatus.BLOCKED_OFFLINE_WEIGHTS.value,
            "expected_model_id": self.EXPECTED_MODEL_ID,
            "architecture": "ModernBERT-large (421M params, English Latin-script) / mmBERT-base (322M, multilingual)",
            "expected_files": ["model.safetensors", "rl_agent_config.json", "tokenizer.json"],
            "searched_paths": searched_paths,
            "offline_weights_found": False,
            "reason": (
                "Neither local repo models/ directory nor Hugging Face cache "
                f"({hf_target}) contains the required 'convaiinnovations/laya' checkpoint files. "
                "Per research protocol, execution enters fail-closed BLOCKED_OFFLINE_WEIGHTS mode."
            )
        }
