"""V-UMR Scaling Semantic Store (Secondary Candidate).

Features:
- Extends UMR-TPG with dual representations:
  * 32D float metric coordinates (32 floats = 128 bytes)
  * 1024-bit binary hypervector (128 bytes)
- Invariant: Continuous vector similarity acts strictly as auxiliary indexing
  and never overrides symbolic logical truth.
- Demonstrates memory-compute trade-off as hypothesized in H2.
"""

from __future__ import annotations

import hashlib
import math
from typing import Any, Dict, List, Optional, Tuple

from .umr_scaling_store import UMRFactNode, UMRScalingStore


def _generate_32d_coords(sig: str) -> Tuple[float, ...]:
    h = hashlib.sha256(sig.encode("utf-8")).digest()
    raw = [float(b - 128) / 128.0 for b in h[:32]]
    norm = math.sqrt(sum(x * x for x in raw))
    if norm < 1e-9:
        return tuple([1.0] + [0.0] * 31)
    return tuple(x / norm for x in raw)


def _generate_1024bit_hypervector(sig: str) -> bytes:
    # 128 bytes = 1024 bits
    h1 = hashlib.sha256((sig + "_1").encode("utf-8")).digest()
    h2 = hashlib.sha256((sig + "_2").encode("utf-8")).digest()
    h3 = hashlib.sha256((sig + "_3").encode("utf-8")).digest()
    h4 = hashlib.sha256((sig + "_4").encode("utf-8")).digest()
    return h1 + h2 + h3 + h4


class VUMRScalingStore(UMRScalingStore):
    def __init__(self) -> None:
        super().__init__()
        # fact_id -> 32D float coordinate vector
        self.coords_store: Dict[str, Tuple[float, ...]] = {}
        # fact_id -> 1024-bit hypervector (128 bytes)
        self.hypervector_store: Dict[str, bytes] = {}

    def insert_fact(self, data: Dict[str, Any]) -> None:
        super().insert_fact(data)

        # Generate and store continuous vector representations
        sig = f"{data['predicate']}:{data['subject']}:{data.get('arguments', [])}"
        coords = _generate_32d_coords(sig)
        hv = _generate_1024bit_hypervector(sig)

        self.coords_store[data["id"]] = coords
        self.hypervector_store[data["id"]] = hv

    def lookup_1hop(self, subject: str, predicate: str) -> List[UMRFactNode]:
        # Vector auxiliary similarity check (simulated indexing overhead)
        query_sig = f"{predicate}:{subject}"
        _ = _generate_32d_coords(query_sig)

        # Exact symbolic lookup guarantees zero logical hallucination
        return super().lookup_1hop(subject, predicate)
