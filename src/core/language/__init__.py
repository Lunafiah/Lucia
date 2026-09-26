"""
src/core/language/__init__.py

Lucia Language Subsystem.
Includes Local LLM Backend and Phase 23-F Language Adapter Boundary.
"""

from src.core.language.adapter import (
    SUPPORTED_LANGUAGES,
    BaseLanguageDriver,
    CoverageReport,
    EgressGateBlockedError,
    EnglishLanguageDriver,
    EpistemicLeakageError,
    GateReport,
    GateVerdict,
    IngressGateBlockedError,
    JapaneseLanguageDriver,
    LanguageAdapter,
    LanguageAdapterError,
    LanguageDriverRegistry,
    LanguageEgressGate,
    LanguageIngressGate,
    ParseResult,
    RealizeResult,
    SubstrateViolationError,
    SupportedLanguage,
    UnsupportedLanguageError,
    VietnameseLanguageDriver,
)
from src.core.language.llm_backend import LLMBackend

__all__ = [
    "LLMBackend",
    "SUPPORTED_LANGUAGES",
    "SupportedLanguage",
    "ParseResult",
    "RealizeResult",
    "CoverageReport",
    "LanguageAdapter",
    "LanguageAdapterError",
    "UnsupportedLanguageError",
    "IngressGateBlockedError",
    "EgressGateBlockedError",
    "EpistemicLeakageError",
    "SubstrateViolationError",
    "GateVerdict",
    "GateReport",
    "LanguageIngressGate",
    "LanguageEgressGate",
    "LanguageDriverRegistry",
    "BaseLanguageDriver",
    "EnglishLanguageDriver",
    "VietnameseLanguageDriver",
    "JapaneseLanguageDriver",
]
