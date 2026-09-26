"""
src/core/knowledge/__init__.py

Public domain exports for Lucia Phase 16 Knowledge Subsystem.
"""

from src.core.knowledge.derivation import DerivationEngine
from src.core.knowledge.fortification import (
    AuditReport,
    AuditStatus,
    AuditViolation,
    ChecksumVerificationError,
    ConservativeSemanticFortifier,
    EpistemicState,
    EpistemicViolationError,
    FortificationError,
    FrozenGraphError,
    NovelEntityInsertionError,
    ProvenanceRecord,
    RedundancyInjectionError,
    ScopeBoundary,
    ScopeType,
    ScopeViolationError,
    SemanticEdge,
    SemanticGraph,
    SemanticNode,
)
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
    # P23-E Conservative Semantic Fortification
    "EpistemicState",
    "ScopeType",
    "AuditStatus",
    "FortificationError",
    "FrozenGraphError",
    "EpistemicViolationError",
    "ScopeViolationError",
    "RedundancyInjectionError",
    "NovelEntityInsertionError",
    "ChecksumVerificationError",
    "ProvenanceRecord",
    "ScopeBoundary",
    "SemanticNode",
    "SemanticEdge",
    "SemanticGraph",
    "AuditViolation",
    "AuditReport",
    "ConservativeSemanticFortifier",
]
