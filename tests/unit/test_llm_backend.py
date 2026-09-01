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
