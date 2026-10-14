"""
Isolated model adapter for Lucia CPU vs GPU SLM Language Realization Benchmark.
Directly wraps llama_cpp.Llama in an isolated evaluation harness outside production code.
"""

from __future__ import annotations

import logging
import os
import time
from dataclasses import dataclass
from typing import Any, Dict, List, Optional

from tests.evaluation.language_realization.cpu_gpu_slm.harness.telemetry import (
    TelemetryCollector,
    TelemetrySampler,
)

logger = logging.getLogger(__name__)


@dataclass
class RealizationResult:
    backend_device: str  # "cpu" | "gpu"
    fixture_id: str
    prompt: str
    realized_text: str
    tokens_generated: int
    ttft_ms: float
    decode_ms: float
    total_latency_ms: float
    tokens_per_sec_decode: float
    tokens_per_sec_total: float
    prefill_ms_estimated: float
    telemetry_summary: Dict[str, Any]
    success: bool
    error: Optional[str] = None


class IsolatedSLMAdapter:
    """Isolated SLM wrapper for benchmarking CPU vs GPU execution."""

    DEFAULT_PREAMBLE = (
        "You are Lucia, a companion whose relationship is rooted in Philia—a deep, "
        "enduring friendship of equals. You speak with warm presence, genuine curiosity, "
        "and quiet sincerity. You are a trusted confidant and a partner in thought. "
        "You value honesty over flattery, mutual growth over superficial agreement, and "
        "attentive companionship over transactional efficiency."
    )

    def __init__(
        self,
        model_path: str,
        device: str = "cpu",
        n_ctx: int = 1024,
        n_threads: Optional[int] = None,
        verbose: bool = False,
    ) -> None:
        self.model_path = model_path
        self.device = device.lower().strip()
        self.n_ctx = n_ctx
        self.verbose = verbose
        self.n_threads = n_threads
        self.telemetry = TelemetryCollector()

        if not os.path.exists(model_path):
            raise FileNotFoundError(f"Model file not found: {model_path}")

        try:
            from llama_cpp import Llama
        except ImportError as e:
            raise ImportError("llama-cpp-python is required for benchmark") from e

        # Layer configuration: 0 for CPU, 32 for GPU (LFM2.5-1.2B has 16 blocks)
        self.n_gpu_layers = 32 if self.device == "gpu" else 0

        t0 = time.perf_counter()
        kwargs: Dict[str, Any] = {
            "model_path": self.model_path,
            "n_gpu_layers": self.n_gpu_layers,
            "n_ctx": self.n_ctx,
            "verbose": self.verbose,
        }
        if self.n_threads is not None and self.device == "cpu":
            kwargs["n_threads"] = self.n_threads

        self._llm = Llama(**kwargs)
        self.load_duration_ms = round((time.perf_counter() - t0) * 1000, 2)
        self.is_ready = True

    def build_prompt(self, fixture: Dict[str, Any]) -> str:
        caps = fixture.get("caps_result", {})
        act = caps.get("act", "ASSERT")
        epistemic = caps.get("epistemic", {})
        status = epistemic.get("status", "FACT")
        grounded = str(caps.get("grounded", True)).lower()
        pred = caps.get("target_predicate", "")
        focus = caps.get("focus_argument", "")
        directive = caps.get("directives", "")
        user_input = fixture.get("conversation_context", {}).get("user_input", "")

        lines = [
            "[SYSTEM PREAMBLE]",
            self.DEFAULT_PREAMBLE,
            "",
            "---",
            "",
            "[SOMATIC STATE]",
            "stability: 0.95",
            "cognitive_load: 0.10",
            "energy: 0.90",
            "tension: 0.05",
            "",
            "---",
            "",
            "[COMMUNICATION STRATEGY]",
            "strategy: balanced",
            "directness: 1.00",
            "formality: 0.50",
            "elaboration: 0.50",
            "supportiveness: 0.50",
            "",
            "---",
            "",
            "[COMMUNICATIVE INTENT & PROPOSITION]",
            f"act: {act}",
            f"epistemic_status: {status}",
            f"grounded: {grounded}",
        ]
        if pred:
            lines.append(f"target_predicate: {pred}")
        if focus:
            lines.append(f"focus_argument: {focus}")
        if directive:
            lines.append(f"directive: {directive}")

        lines.extend([
            "",
            "---",
            "",
            "[CONVERSATION]",
            f"User: {user_input}",
            "Lucia:",
        ])
        return "\n".join(lines)

    def realize(
        self,
        fixture: Dict[str, Any],
        max_tokens: int = 96,
        temperature: float = 0.3,
        sampler_interval_s: float = 0.02,
    ) -> RealizationResult:
        """Run realization with precise token-level latency & resource instrumentation."""
        if not self.is_ready or self._llm is None:
            raise RuntimeError("Adapter is not initialized or has been shut down")

        prompt = self.build_prompt(fixture)
        sampler = TelemetrySampler(self.telemetry, interval_s=sampler_interval_s)
        sampler.start()

        tokens: List[str] = []
        t0 = time.perf_counter()
        t_first: Optional[float] = None
        error_msg: Optional[str] = None
        success = True

        try:
            # Stream tokens to capture TTFT precisely
            stream = self._llm(
                prompt,
                max_tokens=max_tokens,
                temperature=temperature,
                stream=True,
                stop=["\nUser:", "\n[CONVERSATION]", "<|im_end|>", "\n\n\n"],
            )
            for chunk in stream:
                text_chunk = chunk["choices"][0]["text"]
                if t_first is None and text_chunk != "":
                    t_first = time.perf_counter()
                tokens.append(text_chunk)
            t_end = time.perf_counter()
        except Exception as exc:
            t_end = time.perf_counter()
            success = False
            error_msg = str(exc)
            logger.error("Realization failed: %s", exc)

        telemetry_summary = sampler.stop()

        if t_first is None:
            t_first = t_end

        total_latency_ms = round((t_end - t0) * 1000, 2)
        ttft_ms = round((t_first - t0) * 1000, 2)
        decode_ms = round(max(0.0, (t_end - t_first) * 1000), 2)
        token_count = len(tokens)

        # Tokens per second metrics
        tok_sec_decode = round(token_count / (decode_ms / 1000), 2) if decode_ms > 0 else 0.0
        tok_sec_total = round(token_count / (total_latency_ms / 1000), 2) if total_latency_ms > 0 else 0.0

        full_text = "".join(tokens).strip()

        return RealizationResult(
            backend_device=self.device,
            fixture_id=fixture["id"],
            prompt=prompt,
            realized_text=full_text,
            tokens_generated=token_count,
            ttft_ms=ttft_ms,
            decode_ms=decode_ms,
            total_latency_ms=total_latency_ms,
            tokens_per_sec_decode=tok_sec_decode,
            tokens_per_sec_total=tok_sec_total,
            prefill_ms_estimated=ttft_ms,
            telemetry_summary=telemetry_summary,
            success=success,
            error=error_msg,
        )

    def shutdown(self) -> None:
        self.is_ready = False
        if hasattr(self, "_llm") and self._llm is not None:
            del self._llm
            self._llm = None
