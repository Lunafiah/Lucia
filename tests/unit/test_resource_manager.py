"""
Unit tests for Resource Manager and Hardware Scaling profiles.
"""

from unittest.mock import patch

import pytest

from src.core.config import MemoryOrchestratorConfig
from src.core.resource_manager import (
    HardwareDetector,
    HardwareTier,
    ResourceProfile,
    get_resource_profile,
)


class TestResourceManager:
    def test_get_resource_profile_explicit_tiers(self):
        laptop = get_resource_profile("laptop")
        assert laptop.tier == HardwareTier.LAPTOP
        assert laptop.n_gpu_layers == 32
        assert laptop.n_ctx == 4096
        assert laptop.loop_cadence_ms == 200

        desktop = get_resource_profile("desktop")
        assert desktop.tier == HardwareTier.DESKTOP
        assert desktop.n_gpu_layers == 45
        assert desktop.n_ctx == 8192

        high_end = get_resource_profile("high_end")
        assert high_end.tier == HardwareTier.HIGH_END
        assert high_end.n_ctx == 16384
        assert high_end.loop_cadence_ms == 100

        cpu = get_resource_profile("cpu")
        assert cpu.tier == HardwareTier.CPU_ONLY
        assert cpu.n_gpu_layers == 0

    def test_hardware_detector_vram_mapping(self):
        with patch.object(HardwareDetector, "detect_vram_mb", return_value=4096):
            tier = HardwareDetector.detect_tier()
            assert tier == HardwareTier.LAPTOP

        with patch.object(HardwareDetector, "detect_vram_mb", return_value=8192):
            tier = HardwareDetector.detect_tier()
            assert tier == HardwareTier.DESKTOP

        with patch.object(HardwareDetector, "detect_vram_mb", return_value=16384):
            tier = HardwareDetector.detect_tier()
            assert tier == HardwareTier.HIGH_END

        with patch.object(HardwareDetector, "detect_vram_mb", return_value=0):
            tier = HardwareDetector.detect_tier()
            assert tier == HardwareTier.CPU_ONLY

    def test_memory_orchestrator_config_from_profile(self):
        cfg = MemoryOrchestratorConfig.from_profile(
            model_path="dummy.gguf",
            profile_name_or_tier="laptop",
            max_history_turns=5,
        )
        assert cfg.model_path == "dummy.gguf"
        assert cfg.n_gpu_layers == 32
        assert cfg.n_ctx == 4096
        assert cfg.max_history_turns == 5
        assert cfg.resting_baseline == (0.25, -0.05, 0.05)
