"""
src/core/emotion/persistence.py

Crash-resilient serialization, atomic checkpointing, and recovery for
Lucia's Persistent Dynamical State (F-02).

Canonical Architecture Constraints:
- Persists canonical dynamical vectors: h_fast in R^32, s_slow in R^16.
- Persists canonical temporal reference: created_at (POSIX UTC float) to calculate
  elapsed physical time between checkpoint and process recovery.
- Atomic commit: writes to temporary file on same filesystem, then os.replace;
  maintains previous valid checkpoint as backup (.json.bak).
- Crash safety: strictly validates schema and vector dimensions before applying state;
  corrupted checkpoints fall back to previous valid backup, or to canonical
  Philia initial baseline if no valid checkpoint exists.
- Lock discipline: zero disk I/O under locks. State snapshotting copies state under
  _step_lock -> _state_lock, releases locks, and then performs disk I/O.
- Substrate neutrality: operates CPU-only with zero GPU allocations.
- One Continuous Life / Anti-branching: persists strictly to local host filesystem.
"""

from __future__ import annotations

import json
import logging
import os
import shutil
import tempfile
import time
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, Optional, Tuple, Union

import numpy as np

logger = logging.getLogger(__name__)

DEFAULT_DYNAMICAL_STATE_PATH = Path("data/dynamical_state.json")
CURRENT_SCHEMA_VERSION = "1.0"
EXPECTED_FAST_DIM = 32
EXPECTED_SLOW_DIM = 16
EXPECTED_HOMEO_DIM = 4


@dataclass
class DynamicalStateSnapshot:
    """
    Immutable snapshot of Lucia's canonical persistent dynamical state.
    """
    h_fast: np.ndarray                      # Fast reactive hidden state in R^32
    s_slow: np.ndarray                      # Slow affective latent field in R^16
    created_at: float                       # POSIX UTC timestamp of checkpoint creation
    m_homeo: Optional[np.ndarray] = None    # Homeostatic somatic markers in R^4
    pad: Optional[Dict[str, float]] = None  # Projection metadata: {pleasure, arousal, dominance}
    schema_version: str = CURRENT_SCHEMA_VERSION

    def to_dict(self) -> Dict[str, Any]:
        """Convert snapshot to JSON-serializable dictionary."""
        data: Dict[str, Any] = {
            "schema_version": self.schema_version,
            "created_at": float(self.created_at),
            "state": {
                "h_fast": [float(x) for x in self.h_fast],
                "s_slow": [float(x) for x in self.s_slow],
            },
        }
        if self.m_homeo is not None:
            data["state"]["m_homeo"] = [float(x) for x in self.m_homeo]
        if self.pad is not None:
            data["state"]["pad"] = {
                "pleasure": float(self.pad.get("pleasure", 0.0)),
                "arousal": float(self.pad.get("arousal", 0.0)),
                "dominance": float(self.pad.get("dominance", 0.0)),
            }
        return data

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> DynamicalStateSnapshot:
        """Construct snapshot from validated dictionary."""
        state_data = data.get("state", {})
        h_fast = np.array(state_data["h_fast"], dtype=np.float64)
        s_slow = np.array(state_data["s_slow"], dtype=np.float64)
        created_at = float(data["created_at"])
        schema_version = str(data.get("schema_version", CURRENT_SCHEMA_VERSION))

        m_homeo = None
        if "m_homeo" in state_data and state_data["m_homeo"] is not None:
            m_homeo = np.array(state_data["m_homeo"], dtype=np.float64)

        pad = None
        if "pad" in state_data and isinstance(state_data["pad"], dict):
            pad = {
                "pleasure": float(state_data["pad"].get("pleasure", 0.0)),
                "arousal": float(state_data["pad"].get("arousal", 0.0)),
                "dominance": float(state_data["pad"].get("dominance", 0.0)),
            }

        return cls(
            h_fast=h_fast,
            s_slow=s_slow,
            created_at=created_at,
            m_homeo=m_homeo,
            pad=pad,
            schema_version=schema_version,
        )


def validate_checkpoint_dict(data: Any) -> Tuple[bool, Optional[str]]:
    """
    Completely validate a deserialized JSON object against the F-02 schema.
    Returns (True, None) if fully valid, or (False, reason) if invalid.
    """
    if not isinstance(data, dict):
        return False, "Checkpoint root must be a JSON object"

    # Schema version
    version = data.get("schema_version")
    if version != CURRENT_SCHEMA_VERSION:
        return False, f"Incompatible schema version: expected '{CURRENT_SCHEMA_VERSION}', got '{version}'"

    # Temporal reference
    created_at = data.get("created_at")
    if not isinstance(created_at, (int, float)) or not np.isfinite(created_at) or created_at <= 0.0:
        return False, f"Invalid or non-positive created_at timestamp: {created_at}"

    # State payload
    state = data.get("state")
    if not isinstance(state, dict):
        return False, "Missing 'state' object in checkpoint"

    # h_fast validation (R^32)
    h_fast = state.get("h_fast")
    if not isinstance(h_fast, list):
        return False, "'h_fast' must be a list of floats"
    if len(h_fast) != EXPECTED_FAST_DIM:
        return False, f"'h_fast' dimension mismatch: expected {EXPECTED_FAST_DIM}, got {len(h_fast)}"
    for idx, val in enumerate(h_fast):
        if not isinstance(val, (int, float)) or not np.isfinite(val):
            return False, f"Non-finite value in 'h_fast' at index {idx}: {val}"
        if not (-1.0 <= float(val) <= 1.0):
            return False, f"Out-of-bounds value in 'h_fast' at index {idx}: {val} not in [-1.0, 1.0]"

    # s_slow validation (R^16)
    s_slow = state.get("s_slow")
    if not isinstance(s_slow, list):
        return False, "'s_slow' must be a list of floats"
    if len(s_slow) != EXPECTED_SLOW_DIM:
        return False, f"'s_slow' dimension mismatch: expected {EXPECTED_SLOW_DIM}, got {len(s_slow)}"
    for idx, val in enumerate(s_slow):
        if not isinstance(val, (int, float)) or not np.isfinite(val):
            return False, f"Non-finite value in 's_slow' at index {idx}: {val}"
        if not (-1.0 <= float(val) <= 1.0):
            return False, f"Out-of-bounds value in 's_slow' at index {idx}: {val} not in [-1.0, 1.0]"

    # Optional m_homeo validation (R^4)
    if "m_homeo" in state and state["m_homeo"] is not None:
        m_homeo = state["m_homeo"]
        if not isinstance(m_homeo, list) or len(m_homeo) != EXPECTED_HOMEO_DIM:
            return False, f"'m_homeo' must be a list of {EXPECTED_HOMEO_DIM} floats"
        for idx, val in enumerate(m_homeo):
            if not isinstance(val, (int, float)) or not np.isfinite(val) or not (0.0 <= float(val) <= 1.0):
                return False, f"Invalid value in 'm_homeo' at index {idx}: {val}"

    # Optional pad validation
    if "pad" in state and state["pad"] is not None:
        pad = state["pad"]
        if not isinstance(pad, dict):
            return False, "'pad' must be a dict"
        for dim in ("pleasure", "arousal", "dominance"):
            val = pad.get(dim)
            if not isinstance(val, (int, float)) or not np.isfinite(val) or not (-1.0 <= float(val) <= 1.0):
                return False, f"Invalid PAD coordinate '{dim}': {val}"

    return True, None


def save_dynamical_checkpoint(
    snapshot: DynamicalStateSnapshot,
    filepath: Optional[Union[str, Path]] = None,
    storage_policy: Optional[Any] = None,
) -> Path:
    """
    Atomically persist a DynamicalStateSnapshot to disk.
    
    Guarantees:
    - Pre-validates serialized payload before writing.
    - Writes to temporary file on target parent directory, then atomically replaces.
    - Preserves existing valid checkpoint as backup (.json.bak) before replacing.
    - Cleans up temporary file on any error.
    """
    target = Path(filepath) if filepath else DEFAULT_DYNAMICAL_STATE_PATH
    if storage_policy is not None and hasattr(storage_policy, "assert_write_permitted"):
        storage_policy.assert_write_permitted(target)

    target.parent.mkdir(parents=True, exist_ok=True)
    backup_path = target.with_suffix(".json.bak")

    payload = snapshot.to_dict()
    is_valid, err = validate_checkpoint_dict(payload)
    if not is_valid:
        raise ValueError(f"Cannot save invalid dynamical checkpoint: {err}")

    temp_fd, temp_path = tempfile.mkstemp(
        dir=str(target.parent),
        prefix="dynamical_state_",
        suffix=".tmp",
    )
    try:
        with os.fdopen(temp_fd, "w", encoding="utf-8") as f:
            json.dump(payload, f, indent=2, ensure_ascii=False)

        # If primary target exists, preserve it as previous valid backup
        if target.exists():
            try:
                shutil.copy2(target, backup_path)
            except Exception as e:
                logger.warning("Could not backup previous checkpoint %s: %s", target, e)

        os.replace(temp_path, target)
        logger.debug("Successfully saved dynamical state checkpoint to %s", target)
    except Exception as e:
        if os.path.exists(temp_path):
            try:
                os.remove(temp_path)
            except OSError:
                pass
        logger.error("Failed to save dynamical state checkpoint to %s: %s", target, e)
        raise

    return target


def load_dynamical_checkpoint(
    filepath: Optional[Union[str, Path]] = None,
) -> Optional[DynamicalStateSnapshot]:
    """
    Load and completely validate a DynamicalStateSnapshot from disk.
    
    Fallback resolution:
    1. Attempts to load and validate target file.
    2. If target is corrupted or invalid, attempts to load and validate backup file (.json.bak).
    3. If neither target nor backup is valid, returns None (falls back to canonical initial baseline).
    """
    target = Path(filepath) if filepath else DEFAULT_DYNAMICAL_STATE_PATH
    backup_path = target.with_suffix(".json.bak")

    def _try_load(path: Path) -> Optional[DynamicalStateSnapshot]:
        if not path.exists():
            return None
        try:
            with open(path, "r", encoding="utf-8") as f:
                data = json.load(f)
            is_valid, err = validate_checkpoint_dict(data)
            if not is_valid:
                logger.warning("Dynamical checkpoint at %s failed validation: %s", path, err)
                return None
            return DynamicalStateSnapshot.from_dict(data)
        except Exception as e:
            logger.warning("Failed to parse dynamical checkpoint at %s: %s", path, e)
            return None

    # 1. Primary checkpoint
    if target.exists():
        snapshot = _try_load(target)
        if snapshot is not None:
            logger.info("Successfully loaded primary dynamical checkpoint from %s", target)
            return snapshot
        logger.warning(
            "Primary dynamical checkpoint at %s corrupted or invalid; attempting fallback to %s",
            target,
            backup_path,
        )

    # 2. Previous valid backup checkpoint
    if backup_path.exists():
        snapshot = _try_load(backup_path)
        if snapshot is not None:
            logger.info("Successfully recovered dynamical state from backup checkpoint %s", backup_path)
            return snapshot
        logger.warning("Backup dynamical checkpoint at %s also invalid or unreadable", backup_path)

    # 3. No valid checkpoint exists
    logger.info(
        "No valid dynamical checkpoint available at %s (or backup); using default initialization path",
        target,
    )
    return None
