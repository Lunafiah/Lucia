# Specification: Typed Realization Input Contract & Boundary Interface

> **Document Version**: 1.0  
> **Status**: APPROVED ARCHITECTURAL SPECIFICATION (STAGE 4)  
> **Target Module**: `src/core/language/contract.py`  
> **Companion ADR**: [ADR-035](file:///c:/Users/Lunafiah/Desktop/My_project/Lucia/docs/others/PRODUCTION_REALIZATION_BOUNDARY_ADR/ADR_035_PRODUCTION_REALIZATION_BOUNDARY.md)  
> **Implementation Scope**: Stage 5 Production Migration  

---

## 1. Overview & Purpose

The **Typed Realization Input Contract** formalizes the software interface between Stage S10 (`CommunicativeActionPlanner`) and the downstream realization pipeline (Stage S11 Realizer and Stage S14 Verifier).

It solves **GAP-01** and **GAP-05** by ensuring that semantic roles, polarity, epistemic status, scopes, and provenance are never lost in transit, while simultaneously preventing the SLM prompt from being polluted with dense DSL code tokens (the failure mode identified in Stage 3-C).

---

## 2. Data Structure Definitions (`src/core/language/contract.py`)

```python
"""
src/core/language/contract.py

Authoritative Data Structures for the Typed Realization Input Contract.
Enforces invariant semantic obligations between Stage S10 (CAPS) and Stage S14 (Verification).
"""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Dict, List, Optional, Set


class CommunicativeAct(str, Enum):
    """Authoritative taxonomy of communicative actions (Pragmatic Force)."""
    ASSERT = "ASSERT"
    INQUIRE = "INQUIRE"
    ANSWER = "ANSWER"
    CLARIFY = "CLARIFY"
    REFUSE = "REFUSE"
    GREET = "GREET"
    FAREWELL = "FAREWELL"
    ACKNOWLEDGE = "ACKNOWLEDGE"


class EpistemicStatus(str, Enum):
    """Epistemic modality of the proposition."""
    FACT = "FACT"                  # Verified knowledge, certainty permitted
    INFERRED = "INFERRED"          # Derived hypothesis, hedging required
    UNKNOWN = "UNKNOWN"            # Missing knowledge, refusal/clarify required
    AMBIGUOUS = "AMBIGUOUS"        # Multiple referents, clarification required


class SemanticScopeType(str, Enum):
    """Scope tier within the SemanticGraph."""
    ROOT = "ROOT"
    MODAL_EMBEDDING = "MODAL_EMBEDDING"
    NEGATION_SCOPE = "NEGATION_SCOPE"


class ProvenanceOrigin(str, Enum):
    """Origin of the underlying information."""
    OBSERVATION = "OBSERVATION"    # User statement or direct perceptual event
    INFERENCE = "INFERENCE"        # JTMS deduction or BPTT latent state
    RETRIEVAL = "RETRIEVAL"        # SDM associative recall or KnowledgeStore query
    AXIOMATIC = "AXIOMATIC"        # Built-in invariant or identity ground truth


@dataclass(frozen=True)
class SemanticRoleBinding:
    """Explicit semantic role binding mapped from SemanticGraph nodes/edges."""
    role: str                      # ":ARG0", ":ARG1", ":ARG2", ":TIME", ":LOCATION"
    concept_id: str                # e.g., "concept:deployment_v2"
    canonical_lemma: str           # e.g., "bản phát hành 2.0" / "release version 2"
    lexical_synonyms: List[str]    # Permissible surface forms for realization matching
    is_required: bool = True       # Whether omission constitutes ARGUMENT_ENTITY_LOSS
    allow_ellipsis: bool = False   # True for grammatical pro-drop (subject ellipsis in VI/JA)


@dataclass(frozen=True)
class ProvenanceRecord:
    """Provenance audit trail for epistemic accountability."""
    origin: ProvenanceOrigin
    premise_ids: List[str] = field(default_factory=list)
    rule_id: Optional[str] = None
    confidence: float = 1.0


@dataclass(frozen=True)
class RealizationInputContract:
    """
    Authoritative typed contract delivered from Stage S10b to Stage S11 & S14.
    Immutable dataclass representing non-negotiable communicative obligations.
    """
    contract_id: str
    target_language: str           # "en", "vi", "ja"
    act: CommunicativeAct
    polarity: bool                 # True = Affirmative; False = Explicit Negation Required
    epistemic_status: EpistemicStatus
    target_predicate: str          # e.g., "pred:finish_report"
    role_bindings: List[SemanticRoleBinding]
    scope_type: SemanticScopeType = SemanticScopeType.ROOT
    provenance: Optional[ProvenanceRecord] = None
    forbidden_additions: List[str] = field(default_factory=list)
    somatic_modifiers: Dict[str, float] = field(default_factory=dict)
    timestamp: float = field(default=0.0)

    def get_role(self, role_name: str) -> Optional[SemanticRoleBinding]:
        """Retrieves a specific role binding by role label."""
        for r in self.role_bindings:
            if r.role == role_name:
                return r
        return None

    def get_required_concepts(self) -> List[str]:
        """Aggregates all required lexical concept patterns for verification."""
        patterns = []
        for r in self.role_bindings:
            if r.is_required and not r.allow_ellipsis:
                patterns.append(r.canonical_lemma)
        return patterns
```

---

## 3. Natural-Language Prompt Compilation (`PromptAssembler`)

`PromptAssembler` acts as a language-specific compiler that transforms the strongly-typed contract into fluent natural language directives. 

### Critical Rule Derived from Stage 3-C:
**The rendered prompt must NOT output code tokens (`ARG0:`, `EVENT:`, `RULE:`, etc.).** It must emit clear, natural language instructions that the 1.2B SLM can interpret naturally.

### Compiler Mapping Matrix

| Contract Property | English Rendered Directive | Vietnamese Rendered Directive | Japanese Rendered Directive |
|---|---|---|---|
| `act == REFUSE` | "State politely that you do not have verified information to answer this question." | "Nói rõ rằng bạn chưa có thông tin xác thực để trả lời câu hỏi này." | "この質問に答えるための確認済み情報がないことを丁寧に伝えてください。" |
| `act == CLARIFY` | "Ask a clarifying question to find out which specific item the user is referring to." | "Đặt một câu hỏi làm rõ để biết cụ thể người dùng đang đề cập đến nội dung nào." | "ユーザーが具体的にどの項目を指しているかを尋ねる質問をしてください。" |
| `polarity == False` | "State clearly that this event has NOT occurred or completed. Do not affirm." | "Nêu rõ rằng sự việc này CHƯA diễn ra hoặc CHƯA hoàn thành. Không khẳng định." | "この出来事がまだ完了していない・発生していないことを明確に述べてください。" |
| `epistemic == INFERRED` | "Express this as a tentative observation (seems/appears), not an established fact." | "Diễn đạt như một ghi nhận ban đầu (dường như/có vẻ), không khẳng định tuyệt đối." | "確定した事実ではなく、見受けられる様子として表現してください。" |
| `role_bindings` | "Focus the response on {ARG0} regarding {ARG1}." | "Tập trung câu trả lời vào {ARG0} liên quan đến {ARG1}." | "{ARG0}が{ARG1}に関することに焦点を当てて回答してください。" |
