"""
SDMCore — Kanerva's Sparse Distributed Memory backed by dense NumPy arrays.

Implements fixed-capacity hard-location address space with distributed
Hamming-distance read/write.

Requirements: 1.1–1.6, 2.1–2.6, 3.1–3.5, 4.1–4.5, 15.1–15.3
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Dict

import numpy as np

from src.core.errors import CapacityError


@dataclass
class SDMConfig:
    """
    Configuration for SDMCore.

    Parameters
    ----------
    num_locations : int
        Number of hard locations in address space (>= 100).
    address_dim : int
        Dimensionality D of address space (>= 64).
    content_dim : int
        Dimensionality M of content vectors (>= 8).
    hamming_radius_fraction : float
        Activation radius as fraction of address_dim, in (0.0, 1.0).
    capacity : int
        Maximum number of active traces (>= 1).
    """

    num_locations: int = 1_000
    address_dim: int = 1_000
    content_dim: int = 64
    hamming_radius_fraction: float = 0.451
    capacity: int = 10_000

    def __post_init__(self) -> None:
        if self.num_locations < 100:
            raise ValueError(
                f"num_locations ({self.num_locations}) must be >= 100"
            )
        if self.address_dim < 64:
            raise ValueError(
                f"address_dim ({self.address_dim}) must be >= 64"
            )
        if self.content_dim < 8:
            raise ValueError(
                f"content_dim ({self.content_dim}) must be >= 8"
            )
        if not (0.0 < self.hamming_radius_fraction < 1.0):
            raise ValueError(
                f"hamming_radius_fraction ({self.hamming_radius_fraction}) must be in (0.0, 1.0)"
            )
        if self.capacity < 1:
            raise ValueError(
                f"capacity ({self.capacity}) must be >= 1"
            )


class SDMCore:
    """
    Sparse Distributed Memory (Kanerva architecture) implemented with NumPy.
    """

    def __init__(self, config: SDMConfig) -> None:
        # Validate config (calls __post_init__ or validates fields directly)
        if not isinstance(config, SDMConfig):
            raise ValueError("config must be an SDMConfig instance")
        config.__post_init__()
        self._config = config
        self._num_locations = config.num_locations
        self._D = config.address_dim
        self._M = config.content_dim
        self._hamming_radius = int(self._D * config.hamming_radius_fraction)

        # Allocate internal arrays
        rng = np.random.default_rng()
        self._hard_locs: np.ndarray = rng.integers(
            0, 2, size=(self._num_locations, self._D), dtype=np.uint8
        )
        self._accumulator: np.ndarray = np.zeros(
            (self._num_locations, self._M), dtype=np.float32
        )
        self._act_counts: np.ndarray = np.zeros(
            self._num_locations, dtype=np.int64
        )

        self._trace_addresses: Dict[int, np.ndarray] = {}
        self._next_id: int = 0

    @property
    def capacity(self) -> int:
        """Maximum number of traces allowed."""
        return self._config.capacity

    @property
    def trace_count(self) -> int:
        """Current number of stored traces."""
        return len(self._trace_addresses)

    def _hamming_distances(self, address: np.ndarray) -> np.ndarray:
        """
        Compute Hamming distance from address to all hard locations.
        Since hard locations and address are uint8 (0/1), XOR sum gives distance.
        """
        xor = self._hard_locs ^ address[np.newaxis, :]
        return xor.sum(axis=1)

    def _activate(self, address: np.ndarray) -> np.ndarray:
        """
        Return indices of activated hard locations within hamming radius.
        Falls back to the single closest location if none are within radius.
        """
        distances = self._hamming_distances(address)
        mask = distances <= self._hamming_radius
        if mask.any():
            return np.where(mask)[0]
        return np.array([int(np.argmin(distances))], dtype=np.int64)

    def write(self, address: np.ndarray, content: np.ndarray) -> int:
        """
        Write content at address.

        Parameters
        ----------
        address : np.ndarray
            Binary address vector of shape (D,), uint8 with values {0, 1}.
        content : np.ndarray
            Content vector of shape (M,), float.

        Returns
        -------
        int
            Monotonically increasing trace_id.
        """
        if address.shape != (self._D,):
            raise ValueError(
                f"address dim {address.shape[0]} != expected {self._D}"
            )
        if content.shape != (self._M,):
            raise ValueError(
                f"content dim {content.shape[0]} != expected {self._M}"
            )
        if self.trace_count >= self.capacity:
            preview = str(address[:8].tolist())
            raise CapacityError(
                capacity=self.capacity,
                address_preview=preview,
            )

        activated = self._activate(address)
        self._accumulator[activated] += content.astype(np.float32)
        self._act_counts[activated] += 1

        trace_id = self._next_id
        self._next_id += 1
        self._trace_addresses[trace_id] = address.copy()
        return trace_id

    def read(self, address: np.ndarray) -> np.ndarray:
        """
        Read content vector from address.

        Parameters
        ----------
        address : np.ndarray
            Binary address vector of shape (D,).

        Returns
        -------
        np.ndarray
            Recovered content vector of shape (M,), clipped to [-1.0, 1.0].
        """
        if address.shape != (self._D,):
            raise ValueError(
                f"address dim {address.shape[0]} != expected {self._D}"
            )

        activated = self._activate(address)
        counts = self._act_counts[activated]
        total_count = counts.sum()
        if total_count == 0:
            return np.zeros(self._M, dtype=np.float32)

        rows = self._accumulator[activated]
        weighted_sum = (rows * counts[:, np.newaxis]).sum(axis=0)
        result = weighted_sum / total_count
        return np.clip(result, -1.0, 1.0).astype(np.float32)

    def delete(self, trace_id: int) -> None:
        """
        Delete a trace by ID.
        Note: Accumulator rows are intentionally NOT zeroed on delete.
        """
        if trace_id not in self._trace_addresses:
            raise KeyError(f"trace_id {trace_id} not found in SDM store")
        self._trace_addresses.pop(trace_id)

    def clear(self) -> None:
        """
        Reset memory accumulators, trace addresses, and trace counter to initial empty state.
        """
        self._trace_addresses.clear()
        self._accumulator.fill(0.0)
        self._act_counts.fill(0)
        self._next_id = 0

    def memory_usage_bytes(self) -> int:
        """Return total memory in bytes used by internal arrays."""
        return (
            self._hard_locs.nbytes
            + self._accumulator.nbytes
            + self._act_counts.nbytes
        )

