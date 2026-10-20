"""
src/core/cognition/condition_persistence.py

Phase 23-D: Crash-safe, atomic persistence and recovery for UnresolvedCondition.
Enforces the ratified storage authority in data/cognitive_conditions.json
and data/cognitive_conditions.json.bak.

Strict Invariants:
1. Atomic writes via temporary file creation and atomic replacement (os.replace).
2. Existing valid file backed up to .json.bak before replacement.
3. Fail-closed recovery: primary -> backup -> quarantine (.corrupt) -> empty list.
4. Corrupted records are quarantined and NEVER promoted into active memory.
5. Zero dependency on or mutation of data/profile.json (INV-8 Genesis Gate).
"""

from __future__ import annotations

import json
import logging
import os
import shutil
import tempfile
import time
from pathlib import Path
from typing import List, Optional, Sequence, Union

from src.core.cognition.contract.condition import UnresolvedCondition

logger = logging.getLogger(__name__)

DEFAULT_CONDITIONS_PATH = Path("data/cognitive_conditions.json")


def save_conditions(
    conditions: Sequence[UnresolvedCondition],
    filepath: Optional[Union[str, Path]] = None,
) -> Path:
    """
    Atomically persist a sequence of UnresolvedConditions to disk.
    Creates a temporary file, backs up the existing target to .json.bak,
    and atomically replaces the target.
    """
    target = Path(filepath) if filepath else DEFAULT_CONDITIONS_PATH
    target.parent.mkdir(parents=True, exist_ok=True)
    backup_path = target.with_suffix(".json.bak")

    payload = {
        "version": "1.0",
        "conditions": [c.to_dict() for c in conditions],
    }

    temp_fd, temp_path = tempfile.mkstemp(
        dir=str(target.parent),
        prefix="conditions_",
        suffix=".tmp",
    )
    try:
        with os.fdopen(temp_fd, "w", encoding="utf-8") as f:
            json.dump(payload, f, indent=2, ensure_ascii=False)

        # Preserve primary as valid backup before atomic replacement
        if target.exists():
            try:
                shutil.copy2(target, backup_path)
            except Exception as e:
                logger.warning("Could not backup cognitive conditions %s to %s: %s", target, backup_path, e)

        os.replace(temp_path, target)
        logger.debug("Successfully persisted %d conditions to %s", len(conditions), target)
    except Exception as e:
        if os.path.exists(temp_path):
            try:
                os.remove(temp_path)
            except OSError:
                pass
        logger.error("Failed to save cognitive conditions to %s: %s", target, e)
        raise

    return target


def load_conditions(
    filepath: Optional[Union[str, Path]] = None,
) -> List[UnresolvedCondition]:
    """
    Load UnresolvedConditions from disk with strict fallback resolution:
    1. Attempt to load and validate primary target file.
       If file does not exist, return [] (clean bootstrap).
    2. If primary target is corrupted or malformed, attempt to load backup (.json.bak).
    3. If both primary and backup fail or are corrupted, quarantine the corrupted
       primary file to .corrupt_<timestamp>.json, log an alert, and return [] (fail-closed).
    """
    target = Path(filepath) if filepath else DEFAULT_CONDITIONS_PATH
    backup_path = target.with_suffix(".json.bak")

    if not target.exists() and not backup_path.exists():
        logger.debug("Conditions file %s does not exist; initializing empty ledger.", target)
        return []

    def _parse_file(path: Path) -> Optional[List[UnresolvedCondition]]:
        if not path.exists():
            return None
        try:
            with open(path, "r", encoding="utf-8") as f:
                data = json.load(f)
            if not isinstance(data, dict):
                return None
            cond_dicts = data.get("conditions")
            if not isinstance(cond_dicts, list):
                return None
            results: List[UnresolvedCondition] = []
            for cd in cond_dicts:
                results.append(UnresolvedCondition.from_dict(cd))
            return results
        except Exception as exc:
            logger.warning("Failed parsing condition file at %s: %s", path, exc)
            return None

    # Step 1: Try primary file
    if target.exists():
        primary_conditions = _parse_file(target)
        if primary_conditions is not None:
            logger.info("Loaded %d cognitive conditions from %s", len(primary_conditions), target)
            return primary_conditions
        logger.error("Primary condition file %s is corrupted or invalid", target)

    # Step 2: Try backup file
    if backup_path.exists():
        backup_conditions = _parse_file(backup_path)
        if backup_conditions is not None:
            logger.warning("Recovered %d cognitive conditions from backup %s", len(backup_conditions), backup_path)
            return backup_conditions
        logger.error("Backup condition file %s is also corrupted or invalid", backup_path)

    # Step 3: Quarantine corrupted file and fail-closed
    if target.exists():
        corrupt_quarantine_path = target.parent / f"{target.stem}.corrupt_{int(time.time())}.json"
        try:
            shutil.move(str(target), str(corrupt_quarantine_path))
            logger.error("Quarantined corrupted condition file %s to %s", target, corrupt_quarantine_path)
        except Exception as exc:
            logger.error("Failed to quarantine corrupted file %s: %s", target, exc)

    logger.warning("Condition persistence recovery failed-closed; returning empty ledger.")
    return []
