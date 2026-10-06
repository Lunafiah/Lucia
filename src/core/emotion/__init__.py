"""
src/core/emotion/__init__.py

Limbic dynamics, Coupled MT-LNN ODE, Philia attractor, and state persistence.
"""

from src.core.emotion.emotion_core import EmotionCore
from src.core.emotion.persistence import (
    CURRENT_SCHEMA_VERSION,
    DEFAULT_DYNAMICAL_STATE_PATH,
    DynamicalStateSnapshot,
    load_dynamical_checkpoint,
    save_dynamical_checkpoint,
    validate_checkpoint_dict,
)

__all__ = [
    "CURRENT_SCHEMA_VERSION",
    "DEFAULT_DYNAMICAL_STATE_PATH",
    "DynamicalStateSnapshot",
    "EmotionCore",
    "load_dynamical_checkpoint",
    "save_dynamical_checkpoint",
    "validate_checkpoint_dict",
]
