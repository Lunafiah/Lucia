"""
src/core/knowledge/__init__.py

Public domain exports for Lucia Phase 16 Knowledge Subsystem.
"""

from src.core.knowledge.derivation import DerivationEngine
from src.core.knowledge.persistence import load_knowledge, save_knowledge
from src.core.knowledge.proposition import (
    Concept,
    InferenceRule,
    Proposition,
    ProvenanceType,
)
from src.core.knowledge.store import KnowledgeStore

__all__ = [
    "ProvenanceType",
    "Proposition",
    "Concept",
    "InferenceRule",
    "KnowledgeStore",
    "DerivationEngine",
    "save_knowledge",
    "load_knowledge",
]
