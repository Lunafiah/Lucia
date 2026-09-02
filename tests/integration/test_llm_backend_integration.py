"""
GPU/model integration tests for LLMBackend.

All tests in this file are skipped unless the LUCIA_MODEL_PATH environment
variable is set to a valid GGUF model path.

Usage:
    $env:LUCIA_MODEL_PATH = "C:/models/lfm2.5-1.2b-q4_k_m.gguf"
    pytest tests/integration/test_llm_backend_integration.py -v

Requirements: 6.1–6.3
"""

from __future__ import annotations

import os

import pytest

# ---------------------------------------------------------------------------
# Skip guard — all tests in this file are skipped without the model path
# ---------------------------------------------------------------------------

MODEL_PATH = os.environ.get("LUCIA_MODEL_PATH", "")

pytestmark = pytest.mark.skipif(
    not MODEL_PATH,
    reason=(
        "LUCIA_MODEL_PATH environment variable not set. "
        "Set it to the path of a valid GGUF model file to run GPU integration tests. "
        "Example: $env:LUCIA_MODEL_PATH = 'C:/models/lfm2.5-1.2b-q4_k_m.gguf'"
    ),
)


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _make_llm_config(n_gpu_layers: int = 32):
    from src.core.config import LLMConfig
    return LLMConfig(
        model_path=MODEL_PATH,
        n_gpu_layers=n_gpu_layers,
        n_ctx=2048,
        timeout_seconds=60.0,
        verbose=False,
    )


def _make_constraints(max_tokens: int = 50, temperature: float = 0.7):
    from src.core.models import BehavioralConstraints
    return BehavioralConstraints(
        max_tokens=max_tokens,
        temperature=temperature,
        latency_ms=0,
        reasoning_depth=1,
    )


# ---------------------------------------------------------------------------
# Requirement 6.1: model loads successfully from configured path
# ---------------------------------------------------------------------------

class TestLLMBackendInit:
    def test_init_succeeds_with_valid_model(self):
        """LLMBackend.__init__() succeeds when LUCIA_MODEL_PATH is a valid GGUF."""
        from src.core.language.llm_backend import LLMBackend
        cfg = _make_llm_config()
        backend = LLMBackend(cfg)
        try:
            assert backend.is_ready() is True
        finally:
            backend.shutdown()

    def test_is_ready_true_after_init(self):
        """is_ready() returns True immediately after successful __init__."""
        from src.core.language.llm_backend import LLMBackend
        backend = LLMBackend(_make_llm_config())
        try:
            assert backend.is_ready() is True
        finally:
            backend.shutdown()


# ---------------------------------------------------------------------------
# Requirement 6.2: GPU layer count >= 1 when offload requested
# ---------------------------------------------------------------------------

class TestGPULayerAllocation:
    def test_gpu_layers_allocated_when_requested(self):
        """
        When n_gpu_layers > 0 and a CUDA-capable GPU is available,
        at least one layer must be allocated.
        """
        from src.core.language.llm_backend import LLMBackend
        cfg = _make_llm_config(n_gpu_layers=32)
        try:
            backend = LLMBackend(cfg)
            allocated = backend._get_gpu_layer_count()
            assert allocated >= 1, (
                f"Expected >= 1 GPU layer, got {allocated}. "
                "Check that CUDA is available and the model fits in VRAM."
            )
            backend.shutdown()
        except RuntimeError as e:
            pytest.skip(f"GPU not available or layers not allocated: {e}")


# ---------------------------------------------------------------------------
# Requirement 6.3: generate() returns non-empty string
# ---------------------------------------------------------------------------

class TestLLMGenerate:
    def test_generate_returns_non_empty_string(self):
        """generate() returns a non-empty string for a simple prompt."""
        from src.core.language.llm_backend import LLMBackend
        backend = LLMBackend(_make_llm_config())
        try:
            result = backend.generate("Hello, how are you?", _make_constraints(max_tokens=30))
            assert result is not None, "generate() returned None"
            assert isinstance(result, str), f"Expected str, got {type(result)}"
            assert len(result.strip()) > 0, "generate() returned empty string"
        finally:
            backend.shutdown()

    def test_generate_respects_max_tokens(self):
        """Output is roughly bounded by max_tokens."""
        from src.core.language.llm_backend import LLMBackend
        backend = LLMBackend(_make_llm_config())
        try:
            result = backend.generate(
                "Tell me a very long story about everything.",
                _make_constraints(max_tokens=10),
            )
            if result:
                # 10 tokens ~ 40 chars; allow generous margin
                assert len(result) < 200, (
                    f"Output seems too long for max_tokens=10: {len(result)} chars"
                )
        finally:
            backend.shutdown()

    def test_is_ready_false_after_shutdown(self):
        """is_ready() returns False after shutdown()."""
        from src.core.language.llm_backend import LLMBackend
        backend = LLMBackend(_make_llm_config())
        backend.shutdown()
        assert backend.is_ready() is False


# ---------------------------------------------------------------------------
# Phase 2: MemoryAugmentedOrchestrator GPU Smoke Test
# ---------------------------------------------------------------------------

class TestMemoryAugmentedOrchestratorGPU:
    def test_phase2_smoke_test_with_gpu(self):
        """End-to-end memory pipeline with real GPU model."""
        from src.core.config import MemoryOrchestratorConfig
        from src.core.orchestrator.orchestrator import MemoryAugmentedOrchestrator

        config = MemoryOrchestratorConfig(
            model_path=MODEL_PATH,
            n_gpu_layers=32,
            n_ctx=2048,
            loop_cadence_ms=100,
            decay_loop_cadence_seconds=60,
        )
        orch = MemoryAugmentedOrchestrator(config)
        try:
            resp = orch.process("Hello, I am testing the memory system.")
            assert isinstance(resp, str)
            assert len(resp.strip()) > 0
            traces = orch._affective_memory.get_all_traces()
            assert len(traces) == 1
        finally:
            orch.shutdown()
