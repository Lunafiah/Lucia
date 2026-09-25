"""
Laya Verification Adapter for Phase 22-XR Follow-Up.
FAIL-CLOSED PRINCIPLE:
If the real Laya checkpoint weights are missing from the local system,
this adapter strictly emits BLOCKED_OFFLINE_WEIGHTS and terminates the branch.
IT NEVER SUBSTITUTES A HEURISTIC EMULATOR OR LABELS IT AS LAYA.
"""
from typing import Dict, Any, Optional
import time
from .provenance import inspect_laya_model, LayaProvenanceRecord, ProvenanceStatus
from ..schemas import ObservationResult

class LayaVerificationAdapter:
    """
    Adapter interfacing with the external Laya repository.
    Strictly verifies model checkpoint existence and provenance.
    """
    def __init__(self, repo_path: str = "C:/Users/Lunafiah/Desktop/My_project/laya"):
        self.repo_path = repo_path
        self.record: LayaProvenanceRecord = inspect_laya_model(repo_path)
        self.is_ready = self.record.weights_status == ProvenanceStatus.VERIFIED_BY_EXECUTION.value
        self._model = None
        self._tokenizer = None

        if self.is_ready:
            self._load_real_backbone()

    def _load_real_backbone(self):
        """Attempt to load real backbone weights if verified present."""
        try:
            import torch
            from transformers import AutoModelForSequenceClassification, AutoTokenizer
            self._tokenizer = AutoTokenizer.from_pretrained(self.record.checkpoint_path)
            self._model = AutoModelForSequenceClassification.from_pretrained(self.record.checkpoint_path)
            self._model.eval()
        except Exception as e:
            self.is_ready = False
            self.record.weights_status = ProvenanceStatus.UNVERIFIED.value
            self.record.verification_notes += f"; Load failed: {str(e)}"

    def infer_probabilities(self, text: str) -> ObservationResult:
        """
        Runs real backbone inference on text.
        Fails closed with BLOCKED_OFFLINE_WEIGHTS if weights are missing.
        """
        if not self.is_ready:
            return ObservationResult(
                probabilities=[0.0] * 6,
                predicted_category=0,
                latency_ms=0.0,
                memory_vram_mb=0.0,
                memory_ram_mb=0.0,
                provenance=ProvenanceStatus.BLOCKED_OFFLINE_WEIGHTS.value,
                notes=f"Laya inference blocked: {self.record.verification_notes}"
            )

        t0 = time.perf_counter()
        import torch
        with torch.no_grad():
            inputs = self._tokenizer(text, return_tensors="pt", truncation=True, max_length=128)
            outputs = self._model(**inputs)
            logits = outputs.logits[0]
            probs = torch.softmax(logits, dim=-1).cpu().numpy().tolist()

        t_elapsed = (time.perf_counter() - t0) * 1000.0
        pred_cat = int(torch.argmax(logits).item())

        return ObservationResult(
            probabilities=probs,
            predicted_category=pred_cat,
            latency_ms=t_elapsed,
            memory_vram_mb=0.0,
            memory_ram_mb=0.0,
            provenance=ProvenanceStatus.VERIFIED_BY_EXECUTION.value,
            notes="Executed on verified real Laya backbone"
        )
