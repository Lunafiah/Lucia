"""
Resource Manager — Dynamic Hardware Scaling and Auto-Tuning for Lucia.

Detects available hardware (VRAM, GPU, CPU) and selects or applies
tailored resource profiles ranging from low-power laptops (e.g. 4GB RTX 3050 Ti)
to high-end workstations (e.g. 16GB+ RTX 4090).
"""

from __future__ import annotations

import logging
import os
from dataclasses import dataclass
from enum import Enum
from typing import Optional

logger = logging.getLogger(__name__)


class HardwareTier(str, Enum):
    LAPTOP = "laptop"          # Tier 1: 4GB-6GB VRAM (e.g. RTX 3050 Ti Laptop)
    DESKTOP = "desktop"        # Tier 2: 8GB-12GB VRAM (e.g. RTX 4060 / 4070)
    HIGH_END = "high_end"      # Tier 3: 16GB+ VRAM (e.g. RTX 3090 / 4090 / A6000)
    CPU_ONLY = "cpu_only"      # Tier 0: No discrete GPU detected


@dataclass(frozen=True)
class ResourceProfile:
    tier: HardwareTier
    name: str
    description: str
    vram_mb: int
    n_gpu_layers: int
    n_ctx: int
    loop_cadence_ms: int
    sdm_num_locations: int
    sdm_capacity: int
    decay_loop_cadence_seconds: int
    ui_poll_interval_ms: int


# Pre-configured profiles
PROFILES = {
    HardwareTier.LAPTOP: ResourceProfile(
        tier=HardwareTier.LAPTOP,
        name="Laptop Optimized (4-6GB VRAM)",
        description="Preserves VRAM buffer for OS, cool & quiet CPU loop, 4K context.",
        vram_mb=4096,
        n_gpu_layers=32,
        n_ctx=4096,
        loop_cadence_ms=200,
        sdm_num_locations=1_000,
        sdm_capacity=10_000,
        decay_loop_cadence_seconds=3600,
        ui_poll_interval_ms=500,
    ),
    HardwareTier.DESKTOP: ResourceProfile(
        tier=HardwareTier.DESKTOP,
        name="Desktop Standard (8-12GB VRAM)",
        description="Full GPU offload, 8K context, fluid 150ms emotional ODE.",
        vram_mb=8192,
        n_gpu_layers=45,
        n_ctx=8192,
        loop_cadence_ms=150,
        sdm_num_locations=5_000,
        sdm_capacity=50_000,
        decay_loop_cadence_seconds=1800,
        ui_poll_interval_ms=500,
    ),
    HardwareTier.HIGH_END: ResourceProfile(
        tier=HardwareTier.HIGH_END,
        name="High-End Workstation (16GB+ VRAM)",
        description="Full unconstrained GPU offload, 16K context, 100ms ultra-smooth ODE.",
        vram_mb=16384,
        n_gpu_layers=99,
        n_ctx=16384,
        loop_cadence_ms=100,
        sdm_num_locations=20_000,
        sdm_capacity=100_000,
        decay_loop_cadence_seconds=900,
        ui_poll_interval_ms=250,
    ),
    HardwareTier.CPU_ONLY: ResourceProfile(
        tier=HardwareTier.CPU_ONLY,
        name="CPU Fallback",
        description="CPU-only execution, low thread wakeups, 2K context.",
        vram_mb=0,
        n_gpu_layers=0,
        n_ctx=2048,
        loop_cadence_ms=250,
        sdm_num_locations=500,
        sdm_capacity=5_000,
        decay_loop_cadence_seconds=3600,
        ui_poll_interval_ms=1000,
    ),
}


class HardwareDetector:
    """
    Probes system hardware to detect GPU VRAM and recommend optimal hardware tier.
    """

    @staticmethod
    def detect_vram_mb() -> int:
        """
        Query available VRAM in megabytes using llama_cpp / CUDA where available.
        """
        try:
            import importlib
            llama_cpp = importlib.import_module("llama_cpp")
            if hasattr(llama_cpp, "llama_supports_gpu_offload") and llama_cpp.llama_supports_gpu_offload():
                # Test device 0 info via PyTorch if installed, or fallback to default
                try:
                    torch = importlib.import_module("torch")
                    if hasattr(torch, "cuda") and torch.cuda.is_available():
                        total_mem = torch.cuda.get_device_properties(0).total_memory
                        return int(total_mem / (1024 * 1024))
                except Exception:
                    pass
                # Default assume at least 4GB if GPU offload is supported
                return 4096
        except Exception as e:
            logger.debug("GPU detection exception: %s", e)
        return 0

    @classmethod
    def detect_tier(cls) -> HardwareTier:
        """
        Auto-detect the appropriate hardware tier.
        """
        vram = cls.detect_vram_mb()
        if vram <= 0:
            return HardwareTier.CPU_ONLY
        elif vram <= 6144:  # <= 6GB
            return HardwareTier.LAPTOP
        elif vram <= 13000:  # 8GB-12GB
            return HardwareTier.DESKTOP
        else:  # 16GB+
            return HardwareTier.HIGH_END


def get_resource_profile(
    profile_name_or_tier: str | HardwareTier = "auto",
    vram_override_mb: Optional[int] = None,
) -> ResourceProfile:
    """
    Retrieve a ResourceProfile by name or auto-detect based on host hardware.
    """
    if isinstance(profile_name_or_tier, str):
        val = profile_name_or_tier.strip().lower()
        if val in ("auto", "auto_detect", ""):
            tier = HardwareDetector.detect_tier()
        elif val in ("laptop", "tier1"):
            tier = HardwareTier.LAPTOP
        elif val in ("desktop", "tier2"):
            tier = HardwareTier.DESKTOP
        elif val in ("high_end", "ultra", "tier3"):
            tier = HardwareTier.HIGH_END
        elif val in ("cpu", "cpu_only"):
            tier = HardwareTier.CPU_ONLY
        else:
            tier = HardwareDetector.detect_tier()
    else:
        tier = profile_name_or_tier

    profile = PROFILES.get(tier, PROFILES[HardwareTier.LAPTOP])
    logger.info("Selected Lucia Resource Profile: %s (%s)", profile.name, profile.tier.value)
    return profile
