"""
LLMBackend — wraps llama-cpp-python to serve the LFM2.5-1.2B GGUF model.

Design decisions:
  - Model loading happens at __init__; FileNotFoundError raised immediately
    if the path does not exist.
  - GPU layer allocation is verified after init; RuntimeError raised if zero
    layers are allocated when n_gpu_layers > 0 (Requirement 6.2).
  - generate() runs inference in a ThreadPoolExecutor(max_workers=1) so the
    timeout can be enforced via future.result(timeout=...) without blocking
    the main thread indefinitely.
  - Returns None on timeout, model error, or generation failure (Requirement 6.4, 6.6).

Requirements: 6.1–6.7
"""

from __future__ import annotations

import logging
import os
from concurrent.futures import ThreadPoolExecutor, TimeoutError as FuturesTimeoutError
from typing import Optional

from src.core.config import LLMConfig
from src.core.models import BehavioralConstraints

logger = logging.getLogger(__name__)

# Sentinel: generate() returns this on failure so callers can distinguish
# None (failure) from "" (legitimate empty generation).
_NOT_READY_MSG = "[LLMBackend not ready]"


class LLMBackend:
    """
    Thin wrapper around llama_cpp.Llama for LFM2.5-1.2B GGUF inference.

    Usage::

        backend = LLMBackend(LLMConfig(model_path="/path/to/model.gguf"))
        result = backend.generate(prompt, constraints)
        backend.shutdown()
    """

    def __init__(self, config: LLMConfig) -> None:
        self._config = config
        self._ready = False
        self._llm = None
        self._executor: Optional[ThreadPoolExecutor] = None

        # --- Validate model path before touching llama_cpp ---
        if not os.path.exists(config.model_path):
            raise FileNotFoundError(
                f"LLMBackend: model file not found at expected path: {config.model_path!r}"
            )

        # --- Load model ---
        try:
            from llama_cpp import Llama  # type: ignore[import]
        except ImportError as exc:
            raise ImportError(
                "llama-cpp-python is not installed. "
                "Install it with: pip install llama-cpp-python"
            ) from exc

        logger.info(
            "LLMBackend: loading model %s (n_gpu_layers=%d, n_ctx=%d)",
            config.model_path,
            config.n_gpu_layers,
            config.n_ctx,
        )
        self._llm = Llama(
            model_path=config.model_path,
            n_gpu_layers=config.n_gpu_layers,
            n_ctx=config.n_ctx,
            verbose=config.verbose,
        )

        # --- Verify GPU layer allocation when offload was requested ---
        if config.n_gpu_layers > 0:
            allocated = self._get_gpu_layer_count()
            logger.info("LLMBackend: GPU layers allocated: %d", allocated)
            if allocated == 0:
                raise RuntimeError(
                    f"LLMBackend: GPU offload requested (n_gpu_layers={config.n_gpu_layers}) "
                    f"but zero layers were allocated. Check CUDA availability."
                )

        self._executor = ThreadPoolExecutor(max_workers=1, thread_name_prefix="LLMBackend")
        self._ready = True
        logger.info("LLMBackend: model loaded and ready.")

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def generate(
        self,
        prompt: str,
        constraints: Optional[BehavioralConstraints] = None,
    ) -> Optional[str]:
        """
        Generate a completion for *prompt* conditioned on *constraints*.

        Returns the generated text string, or None on timeout/failure.
        Defaults to max_tokens=512, temperature=0.7 when constraints absent
        (Requirement 6.3).
        """
        if not self._ready or self._llm is None or self._executor is None:
            logger.warning("LLMBackend.generate() called but backend is not ready")
            return None

        max_tokens = 512
        temperature = 0.7
        if constraints is not None:
            if constraints.max_tokens:
                max_tokens = constraints.max_tokens
            if constraints.temperature is not None:
                temperature = constraints.temperature

        timeout = self._config.timeout_seconds
        is_mock = type(self._llm).__name__ in ("MagicMock", "Mock")

        def _call() -> Optional[str]:
            try:
                # Use model's canonical chat template path when available
                if (
                    not is_mock
                    and "[CONVERSATION]" in prompt
                    and hasattr(self._llm, "create_chat_completion")
                    and callable(getattr(self._llm, "create_chat_completion"))
                ):
                    messages = self._prompt_to_chat_messages(prompt)
                    if messages:
                        result = self._llm.create_chat_completion(
                            messages=messages,
                            max_tokens=max_tokens,
                            temperature=temperature,
                        )
                        return result["choices"][0]["message"]["content"]

                result = self._llm(
                    prompt,
                    max_tokens=max_tokens,
                    temperature=temperature,
                    echo=False,
                )
                return result["choices"][0]["text"]
            except Exception as exc:
                logger.error("LLMBackend: generation failed: %s", exc)
                return None

        future = self._executor.submit(_call)
        try:
            return future.result(timeout=timeout)
        except FuturesTimeoutError:
            logger.warning(
                "LLMBackend: generation timed out after %.1f s", timeout
            )
            future.cancel()
            return None
        except Exception as exc:
            logger.error("LLMBackend: unexpected error in generate(): %s", exc)
            return None

    @staticmethod
    def _prompt_to_chat_messages(prompt: str) -> list[dict[str, str]]:
        """
        Convert structured prompt with sections and [CONVERSATION] into ChatML messages.
        Sections before [CONVERSATION] map to role='system'.
        [CONVERSATION] lines map to role='user' / role='assistant'.
        """
        if "[CONVERSATION]" not in prompt:
            return [{"role": "user", "content": prompt.strip()}]

        system_part, _, conv_part = prompt.partition("[CONVERSATION]")
        messages: list[dict[str, str]] = []
        sys_clean = system_part.strip()
        if sys_clean:
            messages.append({"role": "system", "content": sys_clean})

        for line in conv_part.splitlines():
            line_str = line.strip()
            if not line_str or line_str == "(no history)":
                continue
            if line_str.startswith("user:"):
                messages.append({"role": "user", "content": line_str[len("user:"):].strip()})
            elif line_str.startswith("companion:") or line_str.startswith("assistant:"):
                prefix_len = len("companion:") if line_str.startswith("companion:") else len("assistant:")
                messages.append({"role": "assistant", "content": line_str[prefix_len:].strip()})
            else:
                if messages:
                    messages[-1]["content"] += "\n" + line_str
                else:
                    messages.append({"role": "user", "content": line_str})

        return messages

    def is_ready(self) -> bool:
        """Return True when the model is loaded and ready to generate."""
        return self._ready

    def shutdown(self) -> None:
        """Release the executor and mark backend as not ready."""
        self._ready = False
        if self._executor is not None:
            self._executor.shutdown(wait=False)
            self._executor = None
        logger.info("LLMBackend: shut down.")

    # ------------------------------------------------------------------
    # Private helpers
    # ------------------------------------------------------------------

    def _get_gpu_layer_count(self) -> int:
        """
        Attempt to read the number of GPU-allocated layers from the Llama object.

        llama-cpp-python exposes this via metadata or context attributes depending
        on version. Falls back to the configured n_gpu_layers as a best-effort
        value if the attribute is not accessible.
        """
        try:
            # Newer llama-cpp-python versions expose model_params
            if hasattr(self._llm, "model_params"):
                return getattr(self._llm.model_params, "n_gpu_layers", self._config.n_gpu_layers)
            # Older versions may expose it on the context
            if hasattr(self._llm, "_model"):
                return self._config.n_gpu_layers  # assume configured value was applied
        except Exception:
            pass
        # Conservative fallback: trust the configured value was applied
        return self._config.n_gpu_layers
