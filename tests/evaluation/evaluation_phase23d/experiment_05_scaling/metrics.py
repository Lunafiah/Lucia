"""Hardware and Performance Metrics for EXP-05: Scaling & Hardware Feasibility.

Measures:
- Resident Set Size (RSS) and Private Working Set via Windows API
- Python heap allocation via tracemalloc
- Single-core query, traversal, insertion, and revision latencies (mean, p50, p95, p99)
- SLA Gate evaluations against preregistered engineering hypotheses
"""

from __future__ import annotations

import ctypes
import os
import sys
import tracemalloc
from ctypes import wintypes
from typing import Any, Dict, List, Optional, Tuple


class PROCESS_MEMORY_COUNTERS_EX(ctypes.Structure):
    _fields_ = [
        ("cb", wintypes.DWORD),
        ("PageFaultCount", wintypes.DWORD),
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


def get_os_memory_mb() -> Tuple[float, float]:
    """Returns (working_set_mb, private_usage_mb) for current process on Windows.

    Falls back to (0.0, 0.0) if platform is non-Windows or API fails.
    """
    if sys.platform != "win32":
        return 0.0, 0.0
    try:
        GetProcessMemoryInfo = ctypes.windll.psapi.GetProcessMemoryInfo
        GetProcessMemoryInfo.argtypes = [
            wintypes.HANDLE,
            ctypes.POINTER(PROCESS_MEMORY_COUNTERS_EX),
            wintypes.DWORD,
        ]
        GetProcessMemoryInfo.restype = wintypes.BOOL

        handle = ctypes.windll.kernel32.GetCurrentProcess()
        counters = PROCESS_MEMORY_COUNTERS_EX()
        counters.cb = ctypes.sizeof(PROCESS_MEMORY_COUNTERS_EX)
        if GetProcessMemoryInfo(handle, ctypes.byref(counters), counters.cb):
            ws_mb = counters.WorkingSetSize / (1024.0 * 1024.0)
            priv_mb = counters.PrivateUsage / (1024.0 * 1024.0)
            return round(ws_mb, 2), round(priv_mb, 2)
    except Exception:
        pass
    return 0.0, 0.0


def compute_percentiles(values: List[float]) -> Dict[str, float]:
    """Computes mean, p50, p95, p99, min, max for a list of latency samples."""
    if not values:
        return {"mean": 0.0, "p50": 0.0, "p95": 0.0, "p99": 0.0, "min": 0.0, "max": 0.0}

    sorted_vals = sorted(values)
    n = len(sorted_vals)

    def p(pct: float) -> float:
        k = (n - 1) * pct
        f = int(k)
        c = min(f + 1, n - 1)
        d0 = sorted_vals[f] * (c - k)
        d1 = sorted_vals[c] * (k - f)
        return d0 + d1

    mean_val = sum(sorted_vals) / n
    return {
        "mean": round(mean_val, 4),
        "p50": round(p(0.50), 4),
        "p95": round(p(0.95), 4),
        "p99": round(p(0.99), 4),
        "min": round(sorted_vals[0], 4),
        "max": round(sorted_vals[-1], 4),
    }


def evaluate_sla_gates(
    candidate: str,
    n_facts: int,
    total_rss_mb: float,
    lookup_p95_ms: float,
    revision_p95_ms: float,
    vram_mb: float,
) -> Dict[str, Any]:
    """Evaluates candidate against the preregistered Phase 23-D engineering gates."""
    # RAM gate at 100k facts: UMR-TPG <= 200MB, V-UMR <= 350MB, DRS-Graph <= 250MB
    ram_target = 200.0 if candidate == "UMR-TPG" else (350.0 if candidate == "V-UMR" else 250.0)
    ram_pass = total_rss_mb <= ram_target if n_facts == 100000 else True

    # Latency gates: 1-hop lookup p95 <= 5.0ms, belief revision p95 <= 2.0ms
    lookup_pass = lookup_p95_ms <= 5.0
    revision_pass = revision_p95_ms <= 2.0

    # VRAM gate: strictly 0.0 MB
    vram_pass = vram_mb == 0.0

    # Physical 20W TDP is unverified because package power measurement is unavailable
    tdp_status = "UNVERIFIED (hardware power meter absent in test environment)"

    overall_pass = ram_pass and lookup_pass and revision_pass and vram_pass

    return {
        "candidate": candidate,
        "n_facts": n_facts,
        "ram_target_mb": ram_target,
        "ram_measured_mb": total_rss_mb,
        "ram_gate_passed": ram_pass,
        "lookup_p95_ms": lookup_p95_ms,
        "lookup_gate_passed": lookup_pass,
        "revision_p95_ms": revision_p95_ms,
        "revision_gate_passed": revision_pass,
        "vram_mb": vram_mb,
        "vram_gate_passed": vram_pass,
        "tdp_status": tdp_status,
        "overall_sla_passed": overall_pass,
    }
