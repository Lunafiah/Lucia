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
DEFAULT_EPOCH_MANIFEST_PATH = Path("data/epoch_manifest.json")
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
    epoch_id: Optional[int] = None          # Logical epoch sequence ID

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
        if self.epoch_id is not None:
            data["epoch_id"] = int(self.epoch_id)
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
        epoch_id = int(data["epoch_id"]) if "epoch_id" in data and data["epoch_id"] is not None else None

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
            epoch_id=epoch_id,
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

    # Optional epoch_id
    if "epoch_id" in data and data["epoch_id"] is not None:
        epoch_id = data["epoch_id"]
        if not isinstance(epoch_id, int) or epoch_id < 0:
            return False, f"Invalid 'epoch_id' in checkpoint: {epoch_id}"

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


# ---------------------------------------------------------------------------
# Commit Barrier & Consistency Detection (Option D/F, F-02)
# ---------------------------------------------------------------------------

@dataclass
class EpochManifest:
    """
    Commit barrier manifest recording synchronized logical epoch across persistent stores.
    Provides consistency detection and crash-safe rollback boundaries (not atomic transactions).
    """
    epoch_id: int
    t_checkpoint: float
    stores: Dict[str, int]
    schema_version: str = CURRENT_SCHEMA_VERSION

    def to_dict(self) -> Dict[str, Any]:
        return {
            "schema_version": self.schema_version,
            "epoch_id": int(self.epoch_id),
            "t_checkpoint": float(self.t_checkpoint),
            "stores": {str(k): int(v) for k, v in self.stores.items()},
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> EpochManifest:
        stores_data = data.get("stores", {})
        stores = {str(k): int(v) for k, v in stores_data.items()} if isinstance(stores_data, dict) else {}
        return cls(
            epoch_id=int(data.get("epoch_id", 0)),
            t_checkpoint=float(data.get("t_checkpoint", 0.0)),
            stores=stores,
            schema_version=str(data.get("schema_version", CURRENT_SCHEMA_VERSION)),
        )


def save_epoch_manifest(
    manifest: EpochManifest,
    filepath: Optional[Union[str, Path]] = None,
    storage_policy: Optional[Any] = None,
) -> Path:
    """
    Atomically persist EpochManifest as commit barrier.
    """
    target = Path(filepath) if filepath else DEFAULT_EPOCH_MANIFEST_PATH
    if storage_policy is not None and hasattr(storage_policy, "assert_write_permitted"):
        storage_policy.assert_write_permitted(target)

    target.parent.mkdir(parents=True, exist_ok=True)
    temp_fd, temp_path = tempfile.mkstemp(
        dir=str(target.parent),
        prefix="epoch_manifest_",
        suffix=".tmp",
    )
    try:
        with os.fdopen(temp_fd, "w", encoding="utf-8") as f:
            json.dump(manifest.to_dict(), f, indent=2, ensure_ascii=False)
        os.replace(temp_path, target)
        logger.debug("Successfully committed epoch manifest %s with epoch=%d", target, manifest.epoch_id)
    except Exception as e:
        if os.path.exists(temp_path):
            try:
                os.remove(temp_path)
            except OSError:
                pass
        logger.error("Failed to commit epoch manifest %s: %s", target, e)
        raise

    return target


def load_epoch_manifest(
    filepath: Optional[Union[str, Path]] = None,
) -> Optional[EpochManifest]:
    """
    Load and parse EpochManifest from disk. Returns None if missing or corrupted.
    """
    target = Path(filepath) if filepath else DEFAULT_EPOCH_MANIFEST_PATH
    if not target.exists():
        return None
    try:
        with open(target, "r", encoding="utf-8") as f:
            data = json.load(f)
        if not isinstance(data, dict):
            return None
        if "epoch_id" not in data or "t_checkpoint" not in data:
            return None
        return EpochManifest.from_dict(data)
    except Exception as e:
        logger.warning("Failed to load epoch manifest at %s: %s", target, e)
        return None


def read_epoch_from_file(filepath: Path) -> Optional[int]:
    """
    Safely extract epoch_id from a store JSON file if present and valid.
    """
    if not filepath.exists():
        return None
    try:
        with open(filepath, "r", encoding="utf-8") as f:
            data = json.load(f)
        if isinstance(data, dict):
            val = data.get("epoch_id")
            if val is not None and isinstance(val, (int, float)):
                return int(val)
    except Exception:
        pass
    return None


def verify_and_reconcile_stores(
    relationship_path: Optional[Union[str, Path]] = None,
    dynamical_path: Optional[Union[str, Path]] = None,
    manifest_path: Optional[Union[str, Path]] = None,
) -> None:
    """
    Deterministic consistency verification and rollback reconciliation protocol (F-02).
    
    Guarantees:
    1. If a crash occurred after updating a store but before the commit barrier (manifest)
       was written, detects that the store's epoch > committed epoch, and rolls back the
       uncommitted store using its .bak file.
    2. If a store is corrupted (malformed JSON), automatically restores valid .bak.
    3. If stores have divergent epochs without a manifest, restores .bak to find the
       common coherent epoch, preventing silent merging of unrelated epochs.
    """
    rel_p = Path(relationship_path) if relationship_path else Path("data/relationship.json")
    dyn_p = Path(dynamical_path) if dynamical_path else DEFAULT_DYNAMICAL_STATE_PATH
    man_p = Path(manifest_path) if manifest_path else DEFAULT_EPOCH_MANIFEST_PATH

    manifest = load_epoch_manifest(man_p)

    def _is_valid_json(p: Path) -> bool:
        if not p.exists():
            return False
        try:
            with open(p, "r", encoding="utf-8") as f:
                json.load(f)
            return True
        except Exception:
            return False

    # 1. Recover corrupted primaries from valid backups first
    for target in (rel_p, dyn_p):
        if target.exists() and not _is_valid_json(target):
            bak = target.with_suffix(".json.bak")
            if bak.exists() and _is_valid_json(bak):
                logger.warning("Primary store %s is corrupted; restoring from backup %s", target, bak)
                shutil.copy2(bak, target)

    # 2. Check against manifest commit barrier if present
    if manifest is not None:
        committed_epoch = manifest.epoch_id
        for target, store_key in ((rel_p, "relationship"), (dyn_p, "dynamical_state")):
            if target.exists():
                ep = read_epoch_from_file(target)
                if ep is not None and ep > committed_epoch:
                    # Uncommitted state written prior to crash
                    bak = target.with_suffix(".json.bak")
                    if bak.exists() and _is_valid_json(bak):
                        bak_ep = read_epoch_from_file(bak)
                        if bak_ep is None or bak_ep <= committed_epoch:
                            logger.warning(
                                "Store %s epoch %d exceeds committed epoch %d; rolling back to %s (epoch %s)",
                                target, ep, committed_epoch, bak, bak_ep,
                            )
                            shutil.copy2(bak, target)
    else:
        # 3. No manifest present: check for epoch mismatch between primaries
        if rel_p.exists() and dyn_p.exists():
            rel_ep = read_epoch_from_file(rel_p)
            dyn_ep = read_epoch_from_file(dyn_p)
            if rel_ep is not None and dyn_ep is not None and rel_ep != dyn_ep:
                logger.warning(
                    "Detected epoch divergence without manifest: relationship epoch=%d, dynamical epoch=%d",
                    rel_ep, dyn_ep,
                )
                if rel_ep > dyn_ep:
                    rel_bak = rel_p.with_suffix(".json.bak")
                    if rel_bak.exists() and read_epoch_from_file(rel_bak) == dyn_ep:
                        logger.warning("Rolling back relationship store to match dynamical store epoch %d", dyn_ep)
                        shutil.copy2(rel_bak, rel_p)
                elif dyn_ep > rel_ep:
                    dyn_bak = dyn_p.with_suffix(".json.bak")
                    if dyn_bak.exists() and read_epoch_from_file(dyn_bak) == rel_ep:
                        logger.warning("Rolling back dynamical store to match relationship store epoch %d", rel_ep)
                        shutil.copy2(dyn_bak, dyn_p)
