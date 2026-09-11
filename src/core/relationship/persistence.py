"""
src/core/relationship/persistence.py

Atomic JSON serialization and persistence for the Relationship Subsystem.
Ensures crash-resilient disk writes and isolated test storage support.
"""

from __future__ import annotations

import json
import logging
import os
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
) -> Path:
    """
    Atomically persist RelationshipState and update history to disk.
    Guarantees no corrupted or half-written JSON files.
    """
    target = Path(filepath) if filepath else DEFAULT_RELATIONSHIP_PATH
    target.parent.mkdir(parents=True, exist_ok=True)

    data = {
        "version": "1.0",
        "state": state.to_dict(),
        "history": history or [],
    }

    temp_fd, temp_path = tempfile.mkstemp(
        dir=str(target.parent),
        prefix="relationship_",
        suffix=".tmp",
    )
    try:
        with os.fdopen(temp_fd, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
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
    Load RelationshipState from disk. If file does not exist, return default neutral baseline.
    """
    target = Path(filepath) if filepath else DEFAULT_RELATIONSHIP_PATH

    if not target.exists():
        logger.info("Relationship file %s does not exist; returning initial neutral state.", target)
        return RelationshipState.initial()

    try:
        with open(target, "r", encoding="utf-8") as f:
            data = json.load(f)
        state_dict = data.get("state", {})
        state = RelationshipState.from_dict(state_dict)
        logger.info("Loaded RelationshipState from %s: %s", target, state_dict)
        return state
    except Exception as e:
        logger.error("Failed to load RelationshipState from %s: %s; returning initial state.", target, e)
        return RelationshipState.initial()
