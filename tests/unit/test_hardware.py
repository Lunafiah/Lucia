"""
Unit tests for host capability detection.
"""

from unittest.mock import patch
import pytest

from src.core.hardware import (
    HostCapabilities,
    detect_host_capabilities,
)


class TestHardwareDetection:
    def test_host_capabilities_to_dict(self):
        caps = HostCapabilities(
            device_name="Test GPU",
            cuda_available=True,
            vram_mb=8192,
            backend="cuda",
            cpu_threads=8,
            cpu_architecture="AMD64",
        )
        d = caps.to_dict()
        assert d["device_name"] == "Test GPU"
        assert d["cuda_available"] is True
        assert d["vram_mb"] == 8192
        assert d["backend"] == "cuda"
        assert d["cpu_threads"] == 8
        assert d["cpu_architecture"] == "AMD64"

    def test_detect_host_capabilities_cpu_fallback(self):
        with patch("torch.cuda.is_available", return_value=False), \
             patch("llama_cpp.llama_supports_gpu_offload", return_value=False, create=True):
            caps = detect_host_capabilities()
            assert caps.cuda_available is False
            assert caps.backend == "cpu"
            assert caps.vram_mb == 0
            assert caps.cpu_threads > 0

    def test_detect_host_capabilities_cuda_path(self):
        with patch("torch.cuda.is_available", return_value=True), \
             patch("torch.cuda.get_device_name", return_value="NVIDIA RTX 4060"), \
             patch("torch.cuda.get_device_properties") as mock_props:
            mock_props.return_value.total_memory = 8 * 1024 * 1024 * 1024
            caps = detect_host_capabilities()
            assert caps.cuda_available is True
            assert caps.backend == "cuda"
            assert caps.device_name == "NVIDIA RTX 4060"
            assert caps.vram_mb == 8192
