"""
Representative CPU co-load generator for testing CPU contention against SLM realization.
Simulates Lucia's background limbic loop (ODEs, matrix projections, ecphory vector matching).
"""

from __future__ import annotations

import math
import threading
import time
from typing import Optional


class CPUCoLoadWorker:
    """Simulates realistic CPU contention from background cognitive dynamics."""

    def __init__(self, thread_count: int = 2, load_fraction: float = 0.8) -> None:
        self.thread_count = thread_count
        self.load_fraction = max(0.1, min(1.0, load_fraction))
        self._stop_event = threading.Event()
        self._threads: list[threading.Thread] = []

    def start(self) -> None:
        self._stop_event.clear()
        self._threads.clear()
        for i in range(self.thread_count):
            t = threading.Thread(
                target=self._worker_loop,
                daemon=True,
                name=f"CPUCoLoad-{i}",
            )
            self._threads.append(t)
            t.start()

    def _worker_loop(self) -> None:
        chunk_ms = 0.05
        busy_time = chunk_ms * self.load_fraction
        sleep_time = chunk_ms * (1.0 - self.load_fraction)

        # Simulation matrix
        dim = 64
        matrix = [[math.sin(i * j) for j in range(dim)] for i in range(dim)]

        while not self._stop_event.is_set():
            t0 = time.perf_counter()
            # Perform continuous math operations representative of limbic LNN ODE integration
            while time.perf_counter() - t0 < busy_time:
                for r in range(dim):
                    for c in range(dim):
                        matrix[r][c] = (matrix[r][c] * 0.99) + math.cos(r + c) * 0.01
            if sleep_time > 0:
                time.sleep(sleep_time)

    def stop(self) -> None:
        self._stop_event.set()
        for t in self._threads:
            t.join(timeout=1.0)
        self._threads.clear()
