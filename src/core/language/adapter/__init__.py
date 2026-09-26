"""
src/core/language/adapter/__init__.py

Language Adapter Boundary & Semantic Substrate Contract (Phase 23-F).

Public exports for language gating, driver registry, and adapter contracts.
"""

from src.core.language.adapter.contracts import (
    SUPPORTED_LANGUAGES,
    CoverageReport,
    EgressGateBlockedError,
    EpistemicLeakageError,
    IngressGateBlockedError,
    LanguageAdapter,
    LanguageAdapterError,
    ParseResult,
    RealizeResult,
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
