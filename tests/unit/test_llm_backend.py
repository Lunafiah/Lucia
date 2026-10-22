"""
Unit tests for LLMBackend.
LLM is always mocked — no real model required.
Requirements: 6.1–6.7
"""

from __future__ import annotations

import os
import time
from concurrent.futures import Future
from unittest.mock import MagicMock, patch

import pytest

from src.core.config import LLMConfig
from src.core.models import BehavioralConstraints


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _make_llm_response(text: str) -> dict:
    """Build a minimal llama_cpp response dict."""
    return {"choices": [{"text": text}]}


def _make_config(tmp_path, n_gpu_layers: int = 0) -> LLMConfig:
    model_file = tmp_path / "model.gguf"
    model_file.write_bytes(b"fake")
    return LLMConfig(
        model_path=str(model_file),
        n_gpu_layers=n_gpu_layers,
        timeout_seconds=5.0,
        verbose=False,
    )


def _make_constraints(
    max_tokens: int = 150, temperature: float = 0.75, latency_ms: int = 0, depth: int = 1
) -> BehavioralConstraints:
    return BehavioralConstraints(
        max_tokens=max_tokens, temperature=temperature,
        latency_ms=latency_ms, reasoning_depth=depth
    )


# ---------------------------------------------------------------------------
# FileNotFoundError on missing model (Req 6.5)
# ---------------------------------------------------------------------------

class TestInit:
    def test_missing_model_path_raises_file_not_found(self, tmp_path):
        cfg = LLMConfig(
            model_path=str(tmp_path / "nonexistent.gguf"),
            n_gpu_layers=0,
        )
        from src.core.language.llm_backend import LLMBackend
        with pytest.raises(FileNotFoundError, match="model file not found"):
            LLMBackend(cfg)

    def test_successful_init_with_mocked_llama(self, tmp_path):
        cfg = _make_config(tmp_path, n_gpu_layers=0)
        mock_llama = MagicMock()

        from src.core.language.llm_backend import LLMBackend
        with patch("src.core.language.llm_backend.Llama", return_value=mock_llama, create=True):
            # Patch the import inside the function
            import src.core.language.llm_backend as mod
            orig = getattr(mod, "Llama", None)
            mod.Llama = MagicMock(return_value=mock_llama)
            try:
                backend = LLMBackend.__new__(LLMBackend)
                backend._config = cfg
                backend._ready = False
                backend._llm = None
                backend._executor = None
                # Manually call __init__ steps via the module's Llama mock
                backend._llm = mock_llama
                from concurrent.futures import ThreadPoolExecutor
                backend._executor = ThreadPoolExecutor(max_workers=1)
                backend._ready = True
                assert backend.is_ready() is True
                backend.shutdown()
                assert backend.is_ready() is False
            finally:
                if orig is not None:
                    mod.Llama = orig
                else:
                    delattr(mod, "Llama")

    def test_is_ready_false_before_init(self, tmp_path):
        """is_ready() must return False on a freshly constructed but uninitialised instance."""
        from src.core.language.llm_backend import LLMBackend
        from concurrent.futures import ThreadPoolExecutor

        cfg = _make_config(tmp_path, n_gpu_layers=0)
        mock_llama = MagicMock()

        backend = LLMBackend.__new__(LLMBackend)
        backend._config = cfg
        backend._ready = False
        backend._llm = mock_llama
        backend._executor = ThreadPoolExecutor(max_workers=1)

        assert backend.is_ready() is False
        backend._executor.shutdown(wait=False)


# ---------------------------------------------------------------------------
# generate() behaviour (Req 6.3, 6.4, 6.6, 6.7)
# ---------------------------------------------------------------------------

class TestGenerate:
    def _make_backend(self, tmp_path, response_text: str = "Hello there!"):
        """Build a LLMBackend with a mocked Llama callable."""
        from src.core.language.llm_backend import LLMBackend
        from concurrent.futures import ThreadPoolExecutor

        cfg = _make_config(tmp_path, n_gpu_layers=0)
        mock_llama = MagicMock(return_value=_make_llm_response(response_text))

        backend = LLMBackend.__new__(LLMBackend)
        backend._config = cfg
        backend._llm = mock_llama
        backend._executor = ThreadPoolExecutor(max_workers=1)
        backend._ready = True
        return backend, mock_llama

    def test_generate_returns_expected_text(self, tmp_path):
        backend, _ = self._make_backend(tmp_path, "Hello there!")
        result = backend.generate("Say hello", _make_constraints())
        assert result == "Hello there!"
        backend.shutdown()

    def test_generate_passes_max_tokens_and_temperature(self, tmp_path):
        backend, mock_llama = self._make_backend(tmp_path)
        constraints = _make_constraints(max_tokens=80, temperature=1.2)
        backend.generate("test prompt", constraints)
        call_kwargs = mock_llama.call_args
        assert call_kwargs.kwargs["max_tokens"] == 80
        assert call_kwargs.kwargs["temperature"] == pytest.approx(1.2)
        backend.shutdown()

    def test_generate_uses_defaults_when_no_constraints(self, tmp_path):
        backend, mock_llama = self._make_backend(tmp_path)
        backend.generate("test prompt", None)
        call_kwargs = mock_llama.call_args
        assert call_kwargs.kwargs["max_tokens"] == 512
        assert call_kwargs.kwargs["temperature"] == pytest.approx(0.7)
        backend.shutdown()

    def test_generate_returns_none_on_model_exception(self, tmp_path):
        from src.core.language.llm_backend import LLMBackend
        from concurrent.futures import ThreadPoolExecutor

        cfg = _make_config(tmp_path)
        mock_llama = MagicMock(side_effect=RuntimeError("model crashed"))

        backend = LLMBackend.__new__(LLMBackend)
        backend._config = cfg
        backend._llm = mock_llama
        backend._executor = ThreadPoolExecutor(max_workers=1)
        backend._ready = True

        result = backend.generate("test", _make_constraints())
        assert result is None
        backend.shutdown()

    def test_generate_returns_none_on_timeout(self, tmp_path):
        from src.core.language.llm_backend import LLMBackend
        from concurrent.futures import ThreadPoolExecutor

        cfg = _make_config(tmp_path)
        cfg = LLMConfig(
            model_path=cfg.model_path,
            n_gpu_layers=0,
            timeout_seconds=1.0,  # short timeout
        )

        def slow_call(*args, **kwargs):
            time.sleep(3.0)
            return _make_llm_response("too late")

        mock_llama = MagicMock(side_effect=slow_call)

        backend = LLMBackend.__new__(LLMBackend)
        backend._config = cfg
        backend._llm = mock_llama
        backend._executor = ThreadPoolExecutor(max_workers=1)
        backend._ready = True

        start = time.monotonic()
        result = backend.generate("test", _make_constraints())
        elapsed = time.monotonic() - start

        assert result is None, "Should return None on timeout"
        assert elapsed < 2.5, f"Should timeout quickly, took {elapsed:.2f}s"
        backend.shutdown()

    def test_generate_returns_none_when_not_ready(self, tmp_path):
        from src.core.language.llm_backend import LLMBackend
        from concurrent.futures import ThreadPoolExecutor

        cfg = _make_config(tmp_path)
        backend = LLMBackend.__new__(LLMBackend)
        backend._config = cfg
        backend._llm = None
        backend._executor = None
        backend._ready = False

        result = backend.generate("test", _make_constraints())
        assert result is None

    def test_is_ready_true_after_init_false_after_shutdown(self, tmp_path):
        backend, _ = self._make_backend(tmp_path)
        assert backend.is_ready() is True
        backend.shutdown()
        assert backend.is_ready() is False


# ---------------------------------------------------------------------------
# translate_to_japanese() — voice truncation regression tests
# ---------------------------------------------------------------------------

class TestTranslateToJapanese:
    """
    Regression suite for the Japanese voice translation truncation fix.

    Root cause (fixed): stop=[..., "\n\n"] caused generation to halt at the
    first paragraph boundary; max_tokens=120 was insufficient for multi-
    paragraph responses.

    Each test uses a hand-constructed LLMBackend with a mocked Llama callable
    so no real model is required.
    """

    def _make_backend(self, tmp_path, translation_text: str = "テスト。"):
        """Build a ready LLMBackend whose _llm returns *translation_text*."""
        from src.core.language.llm_backend import LLMBackend
        from concurrent.futures import ThreadPoolExecutor

        cfg = _make_config(tmp_path, n_gpu_layers=0)
        mock_llama = MagicMock(return_value=_make_llm_response(translation_text))

        backend = LLMBackend.__new__(LLMBackend)
        backend._config = cfg
        backend._llm = mock_llama
        backend._executor = ThreadPoolExecutor(max_workers=1)
        backend._ready = True
        return backend, mock_llama

    # ------------------------------------------------------------------
    # test_translate_to_japanese_multiparagraph
    # ------------------------------------------------------------------
    def test_translate_to_japanese_multiparagraph(self, tmp_path):
        """
        Multi-paragraph English response must be passed to the LLM without
        any '\n\n' in the stop list.  The returned translation must equal the
        mock return value verbatim (no truncation inside translate_to_japanese).
        """
        ja_reply = (
            "ダイナミックプログラミングは、複雑な問題を単純なサブ問題に分解する手法です。\n\n"
            "各サブ問題の解を記憶することで、重複計算を避けることができます。\n\n"
            "これにより、指数関数的な計算量を多項式時間に削減できます。"
        )
        backend, mock_llama = self._make_backend(tmp_path, ja_reply)

        english_input = (
            "Dynamic programming works by breaking a complex problem into simpler subproblems. "
            "It stores the results of subproblems to avoid redundant computation. "
            "This reduces exponential time complexity to polynomial time."
        )
        result = backend.translate_to_japanese(english_input)

        # Translation returned without internal truncation
        assert result == ja_reply

        # Verify "\n\n" is NOT in the stop list passed to the LLM
        call_kwargs = mock_llama.call_args.kwargs
        stop_list = call_kwargs.get("stop", [])
        assert "\n\n" not in stop_list, (
            f"paragraph-break stop token must be absent from stop list, got: {stop_list}"
        )

        backend.shutdown()

    # ------------------------------------------------------------------
    # test_translate_to_japanese_token_budget_scaling
    # ------------------------------------------------------------------
    def test_translate_to_japanese_token_budget_scaling(self, tmp_path):
        """
        Token budget must scale with input length:
        - For a 320-char input: expected budget = min(max(160, 320*3), min(4096//2, 768)) = 768.
        - Budget must never exceed min(n_ctx//2, 768).
        - Budget must always be >= 160 (floor).
        """
        backend, mock_llama = self._make_backend(tmp_path, "翻訳テキスト。")

        # 320-char input → 320 * 3 = 960, capped at min(2048, 768) = 768
        long_input = "A" * 320
        backend.translate_to_japanese(long_input)
        call_kwargs = mock_llama.call_args.kwargs
        used_max_tokens = call_kwargs["max_tokens"]

        n_ctx_ceiling = min(backend._config.n_ctx // 2, 768)
        assert used_max_tokens <= n_ctx_ceiling, (
            f"max_tokens ({used_max_tokens}) exceeded n_ctx ceiling ({n_ctx_ceiling})"
        )
        assert used_max_tokens >= 160, (
            f"max_tokens ({used_max_tokens}) is below the minimum floor of 160"
        )
        assert used_max_tokens == min(max(160, 320 * 3), n_ctx_ceiling)

        backend.shutdown()

    # ------------------------------------------------------------------
    # test_short_input_regression
    # ------------------------------------------------------------------
    def test_short_input_regression(self, tmp_path):
        """
        Short inputs (e.g. 5 chars → 15 raw tokens) must still receive the
        160-token floor so the model is not arbitrarily constrained.
        """
        backend, mock_llama = self._make_backend(tmp_path, "はい。")

        backend.translate_to_japanese("Hello")  # 5 chars → floor applies
        call_kwargs = mock_llama.call_args.kwargs
        used_max_tokens = call_kwargs["max_tokens"]

        assert used_max_tokens == 160, (
            f"Short input should receive 160-token floor, got {used_max_tokens}"
        )

        backend.shutdown()

    # ------------------------------------------------------------------
    # test_voice_realization_length_parity
    # ------------------------------------------------------------------
    def test_voice_realization_length_parity(self, tmp_path):
        """
        The stop list passed to the LLM must contain exactly the two end-of-turn
        tokens and must never contain '\n\n', regardless of input length.
        This is the canonical regression guard for the truncation fix.
        """
        backend, mock_llama = self._make_backend(tmp_path, "完全な翻訳です。")

        for input_text in [
            "Short text.",
            "Medium text. " * 10,
            "Long text. " * 40,
        ]:
            backend.translate_to_japanese(input_text)
            stop_list = mock_llama.call_args.kwargs.get("stop", [])
            assert "\n\n" not in stop_list, (
                f"'\n\n' must never appear in stop list, got: {stop_list!r}"
            )
            assert "<|im_end|>" in stop_list
            assert "<|endoftext|>" in stop_list

        backend.shutdown()
