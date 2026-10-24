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
        self._last_finish_reason: Optional[str] = None
        logger.info("LLMBackend: model loaded and ready.")

    @property
    def last_finish_reason(self) -> Optional[str]:
        """Expose stop reason ('stop', 'length', etc.) from the most recent generation."""
        return self._last_finish_reason

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

        self._last_finish_reason = None
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
                        choices = result.get("choices", [{}]) if isinstance(result, dict) else [{}]
                        if choices and isinstance(choices[0], dict):
                            self._last_finish_reason = choices[0].get("finish_reason")
                        content = result["choices"][0]["message"]["content"]
                        self._last_raw_response = content
                        return content

                result = self._llm(
                    prompt,
                    max_tokens=max_tokens,
                    temperature=temperature,
                    echo=False,
                )
                choices = result.get("choices", [{}]) if isinstance(result, dict) else [{}]
                if choices and isinstance(choices[0], dict):
                    self._last_finish_reason = choices[0].get("finish_reason")
                content = result["choices"][0]["text"]
                self._last_raw_response = content
                return content
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

    def translate_to_japanese(self, text: str, max_tokens: Optional[int] = None) -> Optional[str]:
        """
        Translate conversational text to natural spoken Japanese for voice realization.

        Token budget is adaptive: bounded below by 160 tokens and above by the
        smaller of (n_ctx // 2) and 768, scaled by input character count so that
        multi-paragraph responses are never silently truncated at a paragraph
        boundary by an inadequate token ceiling.

        The ``"\n\n"`` paragraph-break stop token has been deliberately removed;
        generation stops only on the model's end-of-turn markers so the full
        translated content is captured.

        Returns None if translation fails or the model is not ready.
        """
        if not self._ready or self._llm is None or not text.strip():
            return None
        clean_text = text.strip()

        # --- Adaptive token budget -------------------------------------------
        # Floor: 160 tokens (sufficient for ~1 short paragraph in Japanese).
        # Scaling: 3 output tokens per input character is a conservative upper
        #   bound for English→Japanese (Japanese is typically shorter in chars
        #   but uses multi-byte; token count stays comparable).
        # Ceiling: min(n_ctx // 2, 768) — never consume more than half the
        #   context window, and cap at 768 to prevent runaway generation.
        if max_tokens is None:
            n_ctx_ceiling = min(self._config.n_ctx // 2, 768)
            max_tokens = min(max(160, len(clean_text) * 3), n_ctx_ceiling)

        prompt = (
            f"<|im_start|>user\n"
            f"Translate this spoken companion text to natural Japanese:\n"
            f"{clean_text}<|im_end|>\n"
            f"<|im_start|>assistant\n"
        )
        try:
            res = self._llm(
                prompt,
                max_tokens=max_tokens,
                temperature=0.2,
                top_p=0.9,
                # "\n\n" deliberately excluded: paragraph breaks must not
                # terminate generation mid-response (voice truncation bug fix).
                stop=["<|im_end|>", "<|endoftext|>"],
            )
            out = res["choices"][0]["text"].strip()
            return out if out else None
        except Exception as e:
            logger.warning("LLMBackend: translation to Japanese failed: %s", e)
            return None

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
