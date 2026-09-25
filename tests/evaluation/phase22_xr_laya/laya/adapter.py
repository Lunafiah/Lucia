"""
Strict Fail-Closed Real Laya Adapter.
Enforces:
- Only valid execution states: READY_REAL_MODEL, BLOCKED_CHECKPOINT_ACQUISITION, or INVALID_LOCAL_CHECKPOINT.
- Zero fallback emulation.
- Refusal to fabricate synthetic probability vectors.
"""
from typing import Dict, List, Any, Optional, Union
import time
from pathlib import Path
from .provenance import ProvenanceInspector, WeightProvenanceStatus

class RealLayaAdapter:
    """
    Adapter interfacing directly with the external Laya repository runtime.
    Strictly fail-closed: If weights do not exist locally, it blocks.
    """
    def __init__(self, laya_repo_path: str = "C:/Users/Lunafiah/Desktop/My_project/laya"):
        self.inspector = ProvenanceInspector(local_repo_path=laya_repo_path)
        self.audit_result = self.inspector.audit()
        self.status = self.audit_result["status"]
        
        self.agent = None
        self.tokenizer = None
        self.model = None

        if self.status in [WeightProvenanceStatus.VERIFIED_LOCAL_WEIGHTS.value, WeightProvenanceStatus.VERIFIED_HF_CACHE.value]:
            self._init_real_agent()
        else:
            self.execution_state = "BLOCKED_CHECKPOINT_ACQUISITION"

    def _init_real_agent(self):
        """Initializes Laya agent from verified local weight path."""
        try:
            import sys
            import importlib.util
            laya_repo = str(self.inspector.local_repo.resolve())
            laya_init = self.inspector.local_repo / "laya" / "__init__.py"
            
            spec = importlib.util.spec_from_file_location("real_laya", str(laya_init))
            real_laya = importlib.util.module_from_spec(spec)
            sys.modules["real_laya"] = real_laya
            if laya_repo not in sys.path:
                sys.path.insert(0, laya_repo)
            spec.loader.exec_module(real_laya)

            weight_path = self.audit_result.get("weight_path")
            checkpoint_dir = str(Path(weight_path).parent)
            self.agent = real_laya.load(model_id_or_path=checkpoint_dir)
            self.execution_state = "READY_REAL_MODEL"
        except Exception as e:
            self.execution_state = "INVALID_LOCAL_CHECKPOINT"
            self.audit_result["load_error"] = str(e)

    def is_ready(self) -> bool:
        return self.execution_state == "READY_REAL_MODEL"

    def predict_choice(self, state: Union[str, List[Dict]], question: str, options: List[str]) -> Dict[str, Any]:
        """
        Runs real Laya inference for multiple choice questions.
        Fails closed if weights were not loaded.
        """
        if not self.is_ready():
            return {
                "execution_state": self.execution_state,
                "status": self.status,
                "probabilities": None,
                "error": f"Cannot execute inference: adapter is in state '{self.execution_state}'. Reason: {self.audit_result.get('reason')}"
            }

        t0 = time.perf_counter()
        q = {
            "action": {
                "instructions": question,
                "type": "choice",
                "criteria": options
            }
        }
        result = self.agent.predict(state=state, questions=q)
        latency_ms = (time.perf_counter() - t0) * 1000.0

        ans = result["answers"]["action"]
        return {
            "execution_state": "READY_REAL_MODEL",
            "choice": ans["choice"],
            "probabilities": ans["probabilities"],
            "confidence": ans["confidence"],
            "answer_confidence": ans.get("answer_confidence"),
            "latency_ms": latency_ms,
            "provenance": "VERIFIED_BY_EXECUTION"
        }
