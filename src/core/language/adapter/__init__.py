"""
src/core/language/adapter/__init__.py

Language Adapter Boundary & Semantic Substrate Contract (Phase 23-F).

Public exports for language gating, driver registry, and adapter contracts.
"""

from src.core.language.adapter.contracts import (
    SUPPORTED_LANGUAGES,
    CausalRelation,
    CertificationResult,
    CoverageReport,
    EgressGateBlockedError,
    EpistemicEscalationError,
    EpistemicLeakageError,
    IngressCandidateAssertion,
    IngressGateBlockedError,
    IngressSourceClass,
    LanguageAdapter,
    LanguageAdapterError,
    ParseResult,
    QualifiedLogicalAssertion,
    RealizeResult,
    RetractionDirective,
    SubstrateViolationError,
    SupportedLanguage,
    UnsupportedLanguageError,
)
from src.core.language.adapter.drivers import (
    BaseLanguageDriver,
    EnglishLanguageDriver,
    JapaneseLanguageDriver,
    VietnameseLanguageDriver,
)
from src.core.language.adapter.gate import (
    GateReport,
    GateVerdict,
    LanguageEgressGate,
    LanguageIngressGate,
)
from src.core.language.adapter.registry import LanguageDriverRegistry

__all__ = [
    # Contracts & Types
    "SUPPORTED_LANGUAGES",
    "SupportedLanguage",
    "CausalRelation",
    "IngressSourceClass",
    "IngressCandidateAssertion",
    "RetractionDirective",
    "QualifiedLogicalAssertion",
    "CertificationResult",
    "ParseResult",
    "RealizeResult",
    "CoverageReport",
    "LanguageAdapter",
    # Exceptions
    "LanguageAdapterError",
    "UnsupportedLanguageError",
    "IngressGateBlockedError",
    "EgressGateBlockedError",
    "EpistemicLeakageError",
    "EpistemicEscalationError",
    "SubstrateViolationError",
    # Gates
    "GateVerdict",
    "GateReport",
    "LanguageIngressGate",
    "LanguageEgressGate",
    # Registry
    "LanguageDriverRegistry",
    # Drivers
    "BaseLanguageDriver",
    "EnglishLanguageDriver",
    "VietnameseLanguageDriver",
    "JapaneseLanguageDriver",
]
