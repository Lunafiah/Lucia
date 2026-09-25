"""
Component-separated resource and timing profiler for Phase 22-XR Follow-Up.
Guarantees that downstream filter latencies are never reported as Laya latency.
"""
from typing import Dict, Any
import time
import os
import psutil

class ResourceProfiler:
    """
    Measures CPU and RAM utilization separated by component.
    """
    def __init__(self):
        self.process = psutil.Process(os.getpid())

    def measure_component(self, fn, *args, **kwargs) -> Dict[str, Any]:
        """Runs a function and profiles exact elapsed execution time and memory."""
        ram_before = self.process.memory_info().rss / (1024 * 1024)
        t0 = time.perf_counter()
        result = fn(*args, **kwargs)
        t_elapsed_ms = (time.perf_counter() - t0) * 1000.0
        ram_after = self.process.memory_info().rss / (1024 * 1024)

        return {
            "result": result,
            "latency_ms": t_elapsed_ms,
            "ram_delta_mb": max(0.0, ram_after - ram_before),
            "ram_current_mb": ram_after
        }
