"""
src/core/relationship/__init__.py

Public domain exports for Lucia Phase 16 Relationship Subsystem.
"""

from src.core.relationship.persistence import load_relationship, save_relationship
from src.core.relationship.signals import RelationshipSignal, RelationshipSignalType
from src.core.relationship.state import RelationshipState
from src.core.relationship.updater import RelationshipHistoryEntry, RelationshipUpdater

__all__ = [
    "RelationshipState",
    "RelationshipSignalType",
    "RelationshipSignal",
    "RelationshipHistoryEntry",
    "RelationshipUpdater",
    "save_relationship",
    "load_relationship",
]
