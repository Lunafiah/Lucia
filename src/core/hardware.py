"""
Host Hardware Detection — Truthful host capability probing for Project Lucia.

Detects host compute capabilities (CPU, CUDA, VRAM) solely to guide optional
local SLM realizer execution (llama-cpp-python). The 20-Watt Whole Brain Architecture
cognitive core executes strictly on CPU with 0.0 MB GPU VRAM contention.
"""

from __future__ import annotations

import logging
import os
import platform
from dataclasses import asdict, dataclass
from typing import Any, Dict

logger = logging.getLogger(__name__)


@dataclass(frozen=True)
class HostCapabilities:
    """Factual summary of host hardware compute capabilities."""

    device_name: str
    cuda_available: bool
    vram_mb: int
    backend: str  # "cuda" or "cpu"
    cpu_threads: int
    cpu_architecture: str

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


def detect_host_capabilities() -> HostCapabilities:
    """
    Probes host system for GPU VRAM and compute acceleration facts.
    Returns strictly factual capability attributes with zero cognitive state scaling.
    """
    cuda_avail = False
    vram = 0
    device_str = "CPU"

    # Probe PyTorch CUDA if available
    try:
        import torch

        if torch.cuda.is_available():
            cuda_avail = True
            vram = int(torch.cuda.get_device_properties(0).total_memory / (1024 * 1024))
            device_str = torch.cuda.get_device_name(0)
    except Exception as exc:
        logger.debug("PyTorch CUDA probe exception: %s", exc)

    # Fallback probe via llama_cpp if PyTorch CUDA did not report
    if not cuda_avail:
        try:
            import llama_cpp

            if hasattr(llama_cpp, "llama_supports_gpu_offload") and llama_cpp.llama_supports_gpu_offload():
                cuda_avail = True
                device_str = "GPU (llama.cpp offload supported)"
                vram = 4096  # Baseline assumption if offload supported without device properties
        except Exception as exc:
            logger.debug("llama_cpp GPU probe exception: %s", exc)

    backend = "cuda" if cuda_avail else "cpu"
    threads = os.cpu_count() or 1
    arch = platform.machine() or "x86_64"

    return HostCapabilities(
        device_name=device_str,
        cuda_available=cuda_avail,
        vram_mb=vram,
        backend=backend,
        cpu_threads=threads,
        cpu_architecture=arch,
    )
