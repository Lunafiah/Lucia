"""
Hardware and resource telemetry collector for CPU/GPU SLM benchmark.
Measures:
- Windows Process Working Set (RAM) and Peak Working Set via K32GetProcessMemoryInfo
- GPU VRAM (used, free, peak), GPU Utilization, Temperature, Power Draw (Watts), Clock via nvidia-smi
- Background thread sampler to capture peak/average during generation window.
"""

from __future__ import annotations

import ctypes
import ctypes.wintypes
import os
import shutil
import subprocess
import threading
import time
from dataclasses import asdict, dataclass, field
from typing import Any, Dict, List, Optional


class PROCESS_MEMORY_COUNTERS_EX(ctypes.Structure):
    _fields_ = [
        ("cb", ctypes.wintypes.DWORD),
        ("PageFaultCount", ctypes.wintypes.DWORD),
        ("PeakWorkingSetSize", ctypes.c_size_t),
        ("WorkingSetSize", ctypes.c_size_t),
        ("QuotaPeakPagedPoolUsage", ctypes.c_size_t),
        ("QuotaPagedPoolUsage", ctypes.c_size_t),
        ("QuotaPeakNonPagedPoolUsage", ctypes.c_size_t),
        ("QuotaNonPagedPoolUsage", ctypes.c_size_t),
        ("PagefileUsage", ctypes.c_size_t),
        ("PeakPagefileUsage", ctypes.c_size_t),
        ("PrivateUsage", ctypes.c_size_t),
    ]


@dataclass
class TelemetrySnapshot:
    timestamp: float
    process_ram_mb: float
    peak_process_ram_mb: float
    gpu_available: bool = False
    gpu_name: str = "UNKNOWN"
    gpu_vram_used_mb: Optional[float] = None
    gpu_vram_free_mb: Optional[float] = None
    gpu_vram_total_mb: Optional[float] = None
    gpu_utilization_pct: Optional[float] = None
    gpu_mem_utilization_pct: Optional[float] = None
    gpu_temperature_c: Optional[float] = None
    gpu_power_watts: Optional[float] = None
    gpu_clock_mhz: Optional[float] = None
    cpu_thread_count: int = 1

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


class TelemetryCollector:
    """Collects system RAM and GPU telemetry on Windows."""

    def __init__(self) -> None:
        self._has_nvidia_smi = shutil.which("nvidia-smi") is not None
        self._gpu_name = self._detect_gpu_name() if self._has_nvidia_smi else "NONE"
        self._pmc = PROCESS_MEMORY_COUNTERS_EX()
        self._pmc.cb = ctypes.sizeof(PROCESS_MEMORY_COUNTERS_EX)
        self._kernel32 = ctypes.windll.kernel32
        self._current_process = self._kernel32.GetCurrentProcess()

        # Configure K32GetProcessMemoryInfo signature
        self._get_mem_info = self._kernel32.K32GetProcessMemoryInfo
        self._get_mem_info.argtypes = [
            ctypes.wintypes.HANDLE,
            ctypes.POINTER(PROCESS_MEMORY_COUNTERS_EX),
            ctypes.wintypes.DWORD,
        ]
        self._get_mem_info.restype = ctypes.wintypes.BOOL

    def _detect_gpu_name(self) -> str:
        try:
            res = subprocess.run(
                ["nvidia-smi", "--query-gpu=name", "--format=csv,noheader"],
                capture_output=True,
                text=True,
                timeout=3,
                check=True,
            )
            return res.stdout.strip()
        except Exception:
            return "NVIDIA GPU (unidentified)"

    def get_process_ram(self) -> tuple[float, float]:
        """Returns (WorkingSetSize_MB, PeakWorkingSetSize_MB)."""
        ret = self._get_mem_info(
            self._current_process,
            ctypes.byref(self._pmc),
            self._pmc.cb,
        )
        if ret:
            ram_mb = round(self._pmc.WorkingSetSize / (1024 * 1024), 2)
            peak_ram_mb = round(self._pmc.PeakWorkingSetSize / (1024 * 1024), 2)
            return ram_mb, peak_ram_mb
        return 0.0, 0.0

    def query_gpu(self) -> Dict[str, Optional[float]]:
        if not self._has_nvidia_smi:
            return {
                "gpu_vram_total_mb": None,
                "gpu_vram_used_mb": None,
                "gpu_vram_free_mb": None,
                "gpu_utilization_pct": None,
                "gpu_mem_utilization_pct": None,
                "gpu_temperature_c": None,
                "gpu_power_watts": None,
                "gpu_clock_mhz": None,
            }
        try:
            cmd = [
                "nvidia-smi",
                "--query-gpu=memory.total,memory.used,memory.free,utilization.gpu,utilization.memory,temperature.gpu,power.draw,clocks.current.graphics",
                "--format=csv,noheader,nounits",
            ]
            res = subprocess.run(cmd, capture_output=True, text=True, timeout=3, check=True)
            parts = [p.strip() for p in res.stdout.strip().split(",")]
            return {
                "gpu_vram_total_mb": float(parts[0]) if len(parts) > 0 and parts[0] != "[Not Supported]" else None,
                "gpu_vram_used_mb": float(parts[1]) if len(parts) > 1 and parts[1] != "[Not Supported]" else None,
                "gpu_vram_free_mb": float(parts[2]) if len(parts) > 2 and parts[2] != "[Not Supported]" else None,
                "gpu_utilization_pct": float(parts[3]) if len(parts) > 3 and parts[3] != "[Not Supported]" else None,
                "gpu_mem_utilization_pct": float(parts[4]) if len(parts) > 4 and parts[4] != "[Not Supported]" else None,
                "gpu_temperature_c": float(parts[5]) if len(parts) > 5 and parts[5] != "[Not Supported]" else None,
                "gpu_power_watts": float(parts[6]) if len(parts) > 6 and parts[6] != "[Not Supported]" else None,
                "gpu_clock_mhz": float(parts[7]) if len(parts) > 7 and parts[7] != "[Not Supported]" else None,
            }
        except Exception:
            return {
                "gpu_vram_total_mb": None,
                "gpu_vram_used_mb": None,
                "gpu_vram_free_mb": None,
                "gpu_utilization_pct": None,
                "gpu_mem_utilization_pct": None,
                "gpu_temperature_c": None,
                "gpu_power_watts": None,
                "gpu_clock_mhz": None,
            }

    def take_snapshot(self) -> TelemetrySnapshot:
        ram_mb, peak_ram_mb = self.get_process_ram()
        gpu_data = self.query_gpu()
        threads = threading.active_count()
        return TelemetrySnapshot(
            timestamp=time.time(),
            process_ram_mb=ram_mb,
            peak_process_ram_mb=peak_ram_mb,
            gpu_available=self._has_nvidia_smi,
            gpu_name=self._gpu_name,
            gpu_vram_used_mb=gpu_data["gpu_vram_used_mb"],
            gpu_vram_free_mb=gpu_data["gpu_vram_free_mb"],
            gpu_vram_total_mb=gpu_data["gpu_vram_total_mb"],
            gpu_utilization_pct=gpu_data["gpu_utilization_pct"],
            gpu_mem_utilization_pct=gpu_data["gpu_mem_utilization_pct"],
            gpu_temperature_c=gpu_data["gpu_temperature_c"],
            gpu_power_watts=gpu_data["gpu_power_watts"],
            gpu_clock_mhz=gpu_data["gpu_clock_mhz"],
            cpu_thread_count=threads,
        )


class TelemetrySampler:
    """Samples telemetry in a background thread to calculate peak/average during inference."""

    def __init__(self, collector: TelemetryCollector, interval_s: float = 0.05) -> None:
        self._collector = collector
        self._interval_s = interval_s
        self._stop_event = threading.Event()
        self._thread: Optional[threading.Thread] = None
        self._samples: List[TelemetrySnapshot] = []

    def start(self) -> None:
        self._samples.clear()
        self._stop_event.clear()
        self._thread = threading.Thread(target=self._run, daemon=True, name="TelemetrySampler")
        self._thread.start()

    def _run(self) -> None:
        while not self._stop_event.is_set():
            snap = self._collector.take_snapshot()
            self._samples.append(snap)
            time.sleep(self._interval_s)

    def stop(self) -> Dict[str, Any]:
        self._stop_event.set()
        if self._thread is not None:
            self._thread.join(timeout=1.0)
            self._thread = None

        if not self._samples:
            snap = self._collector.take_snapshot()
            self._samples.append(snap)

        peak_vram = max((s.gpu_vram_used_mb for s in self._samples if s.gpu_vram_used_mb is not None), default=None)
        peak_ram = max(s.process_ram_mb for s in self._samples)
        valid_powers = [s.gpu_power_watts for s in self._samples if s.gpu_power_watts is not None]
        avg_power = round(sum(valid_powers) / len(valid_powers), 2) if valid_powers else None
        valid_gpu_utils = [s.gpu_utilization_pct for s in self._samples if s.gpu_utilization_pct is not None]
        avg_gpu_util = round(sum(valid_gpu_utils) / len(valid_gpu_utils), 1) if valid_gpu_utils else None

        return {
            "sample_count": len(self._samples),
            "peak_process_ram_mb": peak_ram,
            "peak_gpu_vram_mb": peak_vram,
            "avg_gpu_power_watts": avg_power,
            "avg_gpu_utilization_pct": avg_gpu_util,
            "first_sample": self._samples[0].to_dict(),
            "last_sample": self._samples[-1].to_dict(),
        }
