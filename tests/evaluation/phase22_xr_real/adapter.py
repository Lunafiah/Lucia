"""Adapter for Real Laya backbone.

Strictly enforces fail-closed behavior:
- If real neural weights are absent, enters and reports BLOCKED_OFFLINE_WEIGHTS.
- NEVER substitutes an emulator or fake heuristic as Real Laya.
"""

from typing import Any, Dict, List, Optional
import numpy as np

from tests.evaluation.phase22_xr_real.config import (
    CLASSES,
    LAYA_CHECKPOINT_ID,
    NUM_CLASSES,
)
from tests.evaluation.phase22_xr_real.provenance import audit_laya_offline_weights


class RealLayaAdapter:
    """Adapter strictly managing the Real Laya Neural Backbone."""

    def __init__(self, device: str = "cpu"):
        self.device = device
        self.checkpoint_id = LAYA_CHECKPOINT_ID
        self.classes = CLASSES
        self.num_classes = NUM_CLASSES
        
        self.audit = audit_laya_offline_weights()
        self.is_ready = self.audit["has_weights"]
        self.status = self.audit["status"]
        self.model = None
        self.tokenizer = None

        if self.is_ready:
            self._load_real_backbone()

    def _load_real_backbone(self) -> None:
        """Attempt to load real weights using transformers and PyTorch."""
        try:
            import torch
            from transformers import AutoModelForSequenceClassification, AutoTokenizer

            # Load strictly from local cache or verified weight path
            # Offline only: local_files_only=True
            self.tokenizer = AutoTokenizer.from_pretrained(
                self.checkpoint_id, local_files_only=True
            )
            self.model = AutoModelForSequenceClassification.from_pretrained(
                self.checkpoint_id, local_files_only=True
            )
            self.model.to(self.device)
            self.model.eval()
            self.status = "READY_REAL_MODEL"
        except Exception as e:
            self.is_ready = False
            self.status = "BLOCKED_OFFLINE_WEIGHTS"
            self.model = None
            self.tokenizer = None
            self.audit["details"] = f"Failed to load weights offline: {str(e)}"

    def infer(self, text: str) -> Dict[str, Any]:
        """Perform real neural inference.
        
        Raises RuntimeError if model weights are not loaded.
        No emulation is permitted under any circumstances.
        """
        if not self.is_ready or self.model is None:
            raise RuntimeError(
                f"Cannot perform real inference: Laya is in state '{self.status}'. "
                f"Fail-closed invariant forbids emulation or cloud fallback."
            )

        import torch
        import torch.nn.functional as F

        with torch.no_grad():
            inputs = self.tokenizer(
                text, return_tensors="pt", truncation=True, max_length=512
            ).to(self.device)
            outputs = self.model(**inputs)
            logits = outputs.logits.squeeze(0).cpu().numpy()
            probs = F.softmax(outputs.logits, dim=-1).squeeze(0).cpu().numpy()

        pred_idx = int(np.argmax(probs))
        confidence = float(probs[pred_idx])

        return {
            "logits": logits.tolist(),
            "probabilities": probs.tolist(),
            "predicted_class": self.classes[pred_idx],
            "confidence": confidence,
            "is_simplex": bool(np.isclose(np.sum(probs), 1.0, atol=1e-5) and np.all(probs >= 0.0)),
        }
