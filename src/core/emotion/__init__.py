"""
src/core/emotion/__init__.py

Limbic dynamics, Coupled MT-LNN ODE, Philia attractor, and state persistence.
"""

from src.core.emotion.emotion_core import EmotionCore
from src.core.emotion.persistence import (
    CURRENT_SCHEMA_VERSION,
    DEFAULT_DYNAMICAL_STATE_PATH,
    DEFAULT_EPOCH_MANIFEST_PATH,
    DynamicalStateSnapshot,
    EpochManifest,
    StoreReconciliationReport,
    load_dynamical_checkpoint,
    load_epoch_manifest,
    save_dynamical_checkpoint,
    save_epoch_manifest,
    validate_checkpoint_dict,
    verify_and_reconcile_stores,
)

__all__ = [
    "CURRENT_SCHEMA_VERSION",
    "DEFAULT_DYNAMICAL_STATE_PATH",
    "DEFAULT_EPOCH_MANIFEST_PATH",
    "DynamicalStateSnapshot",
    "EmotionCore",
    "EpochManifest",
    "StoreReconciliationReport",
    "load_dynamical_checkpoint",
    "load_epoch_manifest",
    "save_dynamical_checkpoint",
    "save_epoch_manifest",
    "validate_checkpoint_dict",
    "verify_and_reconcile_stores",
]
