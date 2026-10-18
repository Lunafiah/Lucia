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
from src.core.language.contract import (
    CommunicativeAct,
    EpistemicStatus,
    ProvenanceOrigin,
    ProvenanceRecord,
    RealizationInputContract,
    RealizationOutput,
    SemanticRoleBinding,
    SemanticScopeType,
    TextRealization,
    VoiceRealization,
)
from src.core.language.detection import detect_active_language
from src.core.language.realization import (
    construct_realization_output,
    realize_japanese_voice_text,
)
from src.core.language.gate import (
    GateDecision,
    SemanticFidelityGate,
)
from src.core.language.llm_backend import LLMBackend

__all__ = [
    "LLMBackend",
    "RealizationInputContract",
    "RealizationOutput",
    "TextRealization",
    "VoiceRealization",
    "detect_active_language",
    "realize_japanese_voice_text",
    "construct_realization_output",
    "SemanticRoleBinding",
    "ProvenanceRecord",
    "CommunicativeAct",
    "EpistemicStatus",
    "SemanticScopeType",
    "ProvenanceOrigin",
    "SemanticFidelityGate",
    "GateDecision",
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
