"""Resource and hardware measurement utility for Phase 22-XR-L."""

import os
import platform
import sys
import time
from typing import Any, Dict, Optional


def measure_hardware_environment() -> Dict[str, Any]:
    """Capture host hardware, OS, CPU, RAM, and runtime library environment."""
    info: Dict[str, Any] = {
        "os_platform": platform.platform(),
        "python_version": sys.version,
        "cpu_model": platform.processor(),
        "cpu_count_logical": os.cpu_count(),
        "torch_version": None,
        "transformers_version": None,
        "cuda_available": False,
        "gpu_model": None,
        "vram_mb": 0.0,
        "total_ram_gb": None,
    }

    try:
        import psutil
        mem = psutil.virtual_memory()
        info["total_ram_gb"] = round(mem.total / (1024**3), 2)
    except Exception:
        pass

    try:
        import torch
        info["torch_version"] = torch.__version__
        info["cuda_available"] = torch.cuda.is_available()
        if torch.cuda.is_available():
            info["gpu_model"] = torch.cuda.get_device_name(0)
            info["vram_mb"] = round(torch.cuda.get_device_properties(0).total_memory / (1024**2), 2)
    except Exception:
        pass

    try:
        import transformers
        info["transformers_version"] = transformers.__version__
    except Exception:
        pass

    return info
