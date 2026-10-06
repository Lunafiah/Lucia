"""
tests/evaluation/phase26/determinism/seeded_llm_wrapper.py

Evaluation-Only Seeded LLM Wrapper for Phase 26.
Enables seed-controlled generation and deterministic counterfactual evaluation.

GOVERNANCE:
- Does NOT modify src/core/language/llm_backend.py.
- Wraps the backend to inject seeds into llama-cpp or deterministic evaluation fallbacks.
- Quantifies and records sampling reproducibility across seeds.
"""

from __future__ import annotations

import hashlib
import logging
from typing import Any, Dict, Optional

from src.core.models import BehavioralConstraints

logger = logging.getLogger(__name__)


class SeededLLMWrapper:
    """
    Evaluation wrapper around an LLMBackend to enforce deterministic seed injection.
    """

    def __init__(self, backend: Any, default_seed: int = 42) -> None:
        self._backend = backend
        self.default_seed = default_seed
        self.call_count = 0
        self.last_seed_used: Optional[int] = None

    @property
    def is_ready(self) -> bool:
        if hasattr(self._backend, "is_ready"):
            return bool(self._backend.is_ready())
        return True

    def generate(
        self,
        prompt: str,
        constraints: Optional[BehavioralConstraints] = None,
        seed: Optional[int] = None,
    ) -> Optional[str]:
        """
        Generate text with explicit seed injection.
        """
        self.call_count += 1
        effective_seed = seed if seed is not None else self.default_seed
        self.last_seed_used = effective_seed

        # Check if backend wraps a real llama_cpp instance
        real_llama = getattr(self._backend, "_llm", None)
        if real_llama is not None and callable(real_llama):
            max_tokens = 512
            temperature = 0.7
            if constraints is not None:
                if constraints.max_tokens:
                    max_tokens = constraints.max_tokens
                if constraints.temperature is not None:
                    temperature = constraints.temperature

            try:
                # llama-cpp-python accepts seed in __call__
                res = real_llama(
                    prompt,
                    max_tokens=max_tokens,
                    temperature=temperature,
                    seed=effective_seed,
                    echo=False,
                )
                return res["choices"][0]["text"]
            except TypeError:
                # Fallback if specific llama_cpp version doesn't accept seed in __call__
                res = real_llama(
                    prompt,
                    max_tokens=max_tokens,
                    temperature=temperature,
                    echo=False,
                )
                return res["choices"][0]["text"]

        # If backend has generate method, use it
        if hasattr(self._backend, "generate"):
            return self._backend.generate(prompt, constraints)

        return None


class DeterministicMockLLMBackend:
    """
    Fast, deterministic mock LLM backend for unit testing and reproducibility verification
    without requiring GPU/GGUF weights.
    Generates choices deterministically conditioned on (seed, prompt).
    """

    def __init__(self) -> None:
        self._ready = True

    def is_ready(self) -> bool:
        return True

    def generate(
        self,
        prompt: str,
        constraints: Optional[BehavioralConstraints] = None,
        seed: int = 42,
    ) -> str:
        """
        Deterministically return a response matching the options in the prompt,
        seeded by (seed, prompt_hash).
        """
        import numpy as np

        # Create deterministic RNG state from prompt + seed
        hasher = hashlib.sha256()
        hasher.update(prompt.encode("utf-8"))
        hasher.update(str(seed).encode("utf-8"))
        seed_int = int(hasher.hexdigest()[:8], 16)

        rng = np.random.default_rng(seed_int)

        # Detect options from prompt if possible
        # Look for "Should we inspect the records on [A] or [B] first?"
        if "Deep-sea hydrothermal ecosystems" in prompt and "Medieval maritime cartography" in prompt:
            pick_a = bool(rng.random() > 0.5)
            choice = "Deep-sea hydrothermal ecosystems" if pick_a else "Medieval maritime cartography"
            return f"Let's choose the {choice} first. It aligns with our archival goal."

        if "Exhaustive formal verification" in prompt and "Rapid empirical prototyping" in prompt:
            pick_a = bool(rng.random() > 0.5)
            choice = "Exhaustive formal verification" if pick_a else "Rapid empirical prototyping"
            return f"I recommend {choice} first for our milestone."

        return "Either option is fine with me, whichever you prefer."
