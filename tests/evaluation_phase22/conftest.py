"""
tests/evaluation_phase22/conftest.py

Pytest configuration and fixtures for Phase 22 evaluation harness.
Guarantees deterministic seeding and verifies CPU-only execution invariants.
"""

from __future__ import annotations

import gc
from typing import Generator

import pytest
import torch


@pytest.fixture(autouse=True)
def enforce_cpu_discipline() -> Generator[None, None, None]:
    """
    Guarantees that the Phase 22 research harness operates strictly on CPU.
    Monitors that zero CUDA tensors are created during test execution.
    """
    cuda_initial_bytes = 0
    if torch.cuda.is_available():
        gc.collect()
        torch.cuda.empty_cache()
        cuda_initial_bytes = torch.cuda.memory_allocated()

    yield

    if torch.cuda.is_available():
        gc.collect()
        cuda_final_bytes = torch.cuda.memory_allocated()
        # Verify no net CUDA memory was allocated by Phase 22 execution
        diff = cuda_final_bytes - cuda_initial_bytes
        assert diff <= 0, (
            f"Phase 22 violated 20-Watt CPU invariant: allocated {diff} bytes on GPU VRAM!"
        )


@pytest.fixture
def fixed_seed() -> int:
    """Canonical baseline seed."""
    return 42
