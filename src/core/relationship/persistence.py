"""
src/core/relationship/persistence.py

Atomic JSON serialization and persistence for the Relationship Subsystem.
Ensures crash-resilient disk writes and isolated test storage support.
"""

from __future__ import annotations

import json
import logging
import os
import shutil
import tempfile
from pathlib import Path
from typing import Any, Dict, List, Optional, Union

from src.core.relationship.state import RelationshipState

logger = logging.getLogger(__name__)

DEFAULT_RELATIONSHIP_PATH = Path("data/relationship.json")


def save_relationship(
    state: RelationshipState,
    history: Optional[List[Dict[str, Any]]] = None,
    filepath: Optional[Union[str, Path]] = None,
    epoch_id: Optional[int] = None,
) -> Path:
    """
    Atomically persist RelationshipState and update history to disk.
    Guarantees no corrupted or half-written JSON files.
    Preserves previous valid state in .json.bak before replacing.
    """
    target = Path(filepath) if filepath else DEFAULT_RELATIONSHIP_PATH
    target.parent.mkdir(parents=True, exist_ok=True)
    backup_path = target.with_suffix(".json.bak")

    data: Dict[str, Any] = {
        "version": "1.0",
        "state": state.to_dict(),
        "history": history or [],
    }
    if epoch_id is not None:
        data["epoch_id"] = int(epoch_id)

    temp_fd, temp_path = tempfile.mkstemp(
        dir=str(target.parent),
        prefix="relationship_",
        suffix=".tmp",
    )
    try:
        with os.fdopen(temp_fd, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2, ensure_ascii=False)

        # Preserve primary as valid backup before atomic replacement
        if target.exists():
            try:
                shutil.copy2(target, backup_path)
            except Exception as e:
                logger.warning("Could not backup previous relationship state %s: %s", target, e)

        os.replace(temp_path, target)
        logger.debug("Successfully saved RelationshipState to %s", target)
    except Exception as e:
        if os.path.exists(temp_path):
            try:
                os.remove(temp_path)
            except OSError:
                pass
        logger.error("Failed to save RelationshipState to %s: %s", target, e)
        raise

    return target


def load_relationship(
    filepath: Optional[Union[str, Path]] = None,
) -> RelationshipState:
    """
    Load RelationshipState from disk.
    Fallback resolution:
    1. Attempts to load and validate target file.
    2. If target is corrupted or invalid, attempts to load backup file (.json.bak).
    3. If neither target nor backup is valid, returns initial neutral state.
    """
    target = Path(filepath) if filepath else DEFAULT_RELATIONSHIP_PATH
    backup_path = target.with_suffix(".json.bak")

    def _try_load(path: Path) -> Optional[RelationshipState]:
        if not path.exists():
            return None
        try:
            with open(path, "r", encoding="utf-8") as f:
                data = json.load(f)
            if not isinstance(data, dict):
                return None
            state_dict = data.get("state")
            if not isinstance(state_dict, dict):
                return None
            return RelationshipState.from_dict(state_dict)
        except Exception as e:
            logger.warning("Failed to load RelationshipState from %s: %s", path, e)
            return None

    # 1. Try primary target
    if target.exists():
        state = _try_load(target)
        if state is not None:
            logger.info("Loaded RelationshipState from %s", target)
            return state
        logger.warning("Primary relationship file at %s corrupted; attempting fallback to %s", target, backup_path)

    # 2. Try backup
    if backup_path.exists():
        state = _try_load(backup_path)
        if state is not None:
            logger.info("Recovered RelationshipState from backup %s", backup_path)
            return state
        logger.warning("Backup relationship file at %s also unreadable", backup_path)

    # 3. Default neutral baseline
    logger.info("No valid relationship file at %s (or backup); returning initial neutral state.", target)
    return RelationshipState.initial()


def load_relationship_epoch(
    filepath: Optional[Union[str, Path]] = None,
) -> Optional[int]:
    """
    Read epoch_id from relationship store if present and valid.
    """
    target = Path(filepath) if filepath else DEFAULT_RELATIONSHIP_PATH
    if not target.exists():
        return None
    try:
        with open(target, "r", encoding="utf-8") as f:
            data = json.load(f)
        if isinstance(data, dict):
            val = data.get("epoch_id")
            if val is not None and isinstance(val, (int, float)):
                return int(val)
    except Exception:
        pass
    return None
