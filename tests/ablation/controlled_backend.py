"""
ControlledLLMBackend — deterministic mock LLM for harness verification ONLY.

CRITICAL INVARIANT:
This module is strictly for unit testing the experimental harness (tests/ablation/test_ablation_experiments.py).
It is NEVER used as experimental evidence in the actual ablation test matrix.
Configurations A-D in the real ablation test matrix MUST use the verified real local GGUF model via CUDA.
"""

from __future__ import annotations

import logging
from typing import Optional

from src.core.config import LLMConfig
from src.core.models import BehavioralConstraints

logger = logging.getLogger(__name__)


class ControlledLLMBackend:
    """
    Deterministic canned-response LLM backend for ablation harness validation.

    Does NOT load GGUF weights, does NOT initialize CUDA, and does NOT execute
    generative inference. Used exclusively in automated pytest suites to verify
    pipeline wiring, scenario orchestration, and metric calculation.
    """

    def __init__(self, config: Optional[LLMConfig] = None) -> None:
        self._config = config or LLMConfig(model_path="dummy/mock.gguf")
        self._ready = True
        self.call_count = 0
        self.last_prompt = ""
        self.last_constraints: Optional[BehavioralConstraints] = None

    def generate(
        self,
        prompt: str,
        constraints: Optional[BehavioralConstraints] = None,
    ) -> Optional[str]:
        """Return a deterministic, predictable response for harness unit tests."""
        if not self._ready:
            return None

        self.call_count += 1
        self.last_prompt = prompt
        self.last_constraints = constraints

        # Extract last user line if available
        last_line = prompt.strip().split("\n")[-1]
        return f"[HARNESS_MOCK_RESPONSE: turn={self.call_count} input='{last_line[:30]}']"

    def is_ready(self) -> bool:
        return self._ready

    def shutdown(self) -> None:
        self._ready = False
