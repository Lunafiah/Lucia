"""
src/core/language/contract.py

Authoritative Data Structures for the Typed Realization Input Contract.
Enforces invariant semantic obligations between Stage S10 (CAPS) and Stage S14 (Verification).
Companion ADR: ADR-035 (Production Realization Boundary & Fail-Closed Semantic Verification).
"""

from __future__ import annotations

import time
import uuid
from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Dict, List, Optional, Sequence, Tuple


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
    REQUEST = "REQUEST"
    EXPLAIN_CONCEPT = "EXPLAIN_CONCEPT"
    ANSWER_PERSONAL_QUERY = "ANSWER_PERSONAL_QUERY"
    ACKNOWLEDGE_REACTION = "ACKNOWLEDGE_REACTION"


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
    canonical_lemma: str           # e.g., "release version 2" / "bản phát hành 2"
    lexical_synonyms: Tuple[str, ...] = field(default_factory=tuple)
    is_required: bool = True       # Whether omission constitutes ARGUMENT_ENTITY_LOSS
    allow_ellipsis: bool = False   # True for grammatical pro-drop (subject ellipsis in VI/JA)

    def matches_text(self, text: str) -> bool:
        """Checks if the canonical lemma or any synonym appears in the text."""
        lowered = text.lower()
        if self.canonical_lemma.lower() in lowered:
            return True
        for syn in self.lexical_synonyms:
            if syn.lower() in lowered:
                return True
        return False


@dataclass(frozen=True)
class ProvenanceRecord:
    """Provenance audit trail for epistemic accountability."""
    origin: ProvenanceOrigin
    premise_ids: Tuple[str, ...] = field(default_factory=tuple)
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
    target_predicate: Optional[str] = None
    role_bindings: Tuple[SemanticRoleBinding, ...] = field(default_factory=tuple)
    scope_type: SemanticScopeType = SemanticScopeType.ROOT
    provenance: Optional[ProvenanceRecord] = None
    forbidden_additions: Tuple[str, ...] = field(default_factory=tuple)
    somatic_modifiers: Dict[str, float] = field(default_factory=dict)
    directives: Optional[str] = None
    speaker_honorific: Optional[str] = None
    addressee_honorific: Optional[str] = None
    conversational_obligation: Optional[str] = None
    dialogue_phase: Optional[str] = None
    timestamp: float = field(default_factory=time.time)

    def get_role(self, role_name: str) -> Optional[SemanticRoleBinding]:
        """Retrieves a specific role binding by role label."""
        for r in self.role_bindings:
            if r.role == role_name:
                return r
        return None

    def get_required_concepts(self) -> List[str]:
        """Aggregates all required lexical concept patterns for verification."""
        patterns: List[str] = []
        for r in self.role_bindings:
            if r.is_required and not r.allow_ellipsis:
                patterns.append(r.canonical_lemma)
        return patterns

    @classmethod
    def create_default(
        cls,
        target_language: str = "en",
        act: CommunicativeAct = CommunicativeAct.ASSERT,
        directives: Optional[str] = None,
        speaker_honorific: Optional[str] = None,
        addressee_honorific: Optional[str] = None,
        forbidden_additions: Optional[Sequence[str]] = None,
        conversational_obligation: Optional[str] = None,
        dialogue_phase: Optional[str] = None,
        target_predicate: Optional[str] = None,
        somatic_modifiers: Optional[Dict[str, float]] = None,
    ) -> RealizationInputContract:
        """Creates a safe baseline contract when no explicit proposition is active."""
        spk = speaker_honorific if speaker_honorific is not None else ("em" if target_language == "vi" else None)
        addr = addressee_honorific if addressee_honorific is not None else ("anh" if target_language == "vi" else None)
        forbid = list(forbidden_additions) if forbidden_additions else []
        if target_language == "vi" and "bạn" not in forbid:
            forbid.append("bạn")
        return cls(
            contract_id=str(uuid.uuid4()),
            target_language=target_language,
            act=act,
            polarity=True,
            epistemic_status=EpistemicStatus.FACT,
            target_predicate=target_predicate,
            role_bindings=(),
            scope_type=SemanticScopeType.ROOT,
            provenance=ProvenanceRecord(origin=ProvenanceOrigin.OBSERVATION),
            forbidden_additions=tuple(forbid),
            somatic_modifiers=somatic_modifiers or {},
            directives=directives,
            speaker_honorific=spk,
            addressee_honorific=addr,
            conversational_obligation=conversational_obligation,
            dialogue_phase=dialogue_phase,
            timestamp=time.time(),
        )

    @classmethod
    def from_caps(
        cls,
        caps_result: Any,
        target_language: str = "en",
        known_propositions: Optional[Sequence[Any]] = None,
        forbidden_additions: Optional[Sequence[str]] = None,
        speaker_honorific: Optional[str] = None,
        addressee_honorific: Optional[str] = None,
        dialogue_phase: Optional[str] = None,
        somatic_modifiers: Optional[Dict[str, float]] = None,
    ) -> RealizationInputContract:
        """
        Constructs a typed RealizationInputContract from a Stage S10 CAPSResult.
        """
        # Map communicative act
        act_val = caps_result.act.value if hasattr(caps_result.act, "value") else str(caps_result.act)
        try:
            act_enum = CommunicativeAct(act_val)
        except ValueError:
            act_enum = CommunicativeAct.ASSERT

        # Map epistemic status
        epistemic_raw = "FACT"
        if hasattr(caps_result, "epistemic_metadata") and caps_result.epistemic_metadata:
            meta = caps_result.epistemic_metadata
            epistemic_raw = meta.status.value if hasattr(meta.status, "value") else str(meta.status)
        try:
            epistemic_enum = EpistemicStatus(epistemic_raw)
        except ValueError:
            epistemic_enum = EpistemicStatus.FACT

        # Map provenance
        prov_origin = ProvenanceOrigin.OBSERVATION
        premise_ids: Tuple[str, ...] = ()
        rule_id: Optional[str] = None
        confidence = 1.0
        if hasattr(caps_result, "provenance_metadata") and caps_result.provenance_metadata:
            pm = caps_result.provenance_metadata
            p_orig_str = str(pm.origin).upper()
            if "INFER" in p_orig_str:
                prov_origin = ProvenanceOrigin.INFERENCE
            elif "RETRIEVAL" in p_orig_str:
                prov_origin = ProvenanceOrigin.RETRIEVAL
            elif "AXIOM" in p_orig_str:
                prov_origin = ProvenanceOrigin.AXIOMATIC
            premise_ids = tuple(pm.premise_ids) if hasattr(pm, "premise_ids") else ()
            rule_id = getattr(pm, "rule_id", None)

        prov_rec = ProvenanceRecord(
            origin=prov_origin,
            premise_ids=premise_ids,
            rule_id=rule_id,
            confidence=confidence,
        )

        # Polarity determination
        polarity = True
        # Check if graph or caps explicitly negates
        if hasattr(caps_result, "polarity"):
            polarity = bool(caps_result.polarity)

        # Extract role bindings from SemanticGraph or known_propositions
        roles: List[SemanticRoleBinding] = []
        target_predicate = getattr(caps_result, "target_predicate", None)
        focus_arg = getattr(caps_result, "focus_argument", None)

        # If semantic graph is present, extract explicit graph nodes and edges
        sg = getattr(caps_result, "semantic_graph", None)
        scope_type = SemanticScopeType.ROOT
        if sg is not None:
            nodes = getattr(sg, "nodes", {})
            edges = getattr(sg, "edges", [])
            scopes = getattr(sg, "scopes", {})

            for sc in scopes.values():
                sc_type_val = getattr(sc, "scope_type", None)
                sc_str = sc_type_val.value if hasattr(sc_type_val, "value") else str(sc_type_val)
                if sc_str == "NEGATION":
                    scope_type = SemanticScopeType.NEGATION_SCOPE
                    polarity = False
                elif sc_str == "MODAL":
                    scope_type = SemanticScopeType.MODAL_EMBEDDING

            for e in edges:
                role_name = getattr(e, "relation_role", ":ARG1")
                tgt_id = getattr(e, "target_id", "")
                if tgt_id in nodes:
                    n = nodes[tgt_id]
                    concept_sym = getattr(n, "concept_symbol", tgt_id)
                    roles.append(
                        SemanticRoleBinding(
                            role=role_name,
                            concept_id=tgt_id,
                            canonical_lemma=concept_sym,
                            lexical_synonyms=(),
                            is_required=True,
                            allow_ellipsis=(target_language in ("vi", "ja") and role_name == ":ARG0"),
                        )
                    )

        # If roles empty but known propositions provided and target_predicate matches, populate ARG0 / ARG1
        if not roles and known_propositions and target_predicate:
            matching_kp = None
            for p in known_propositions:
                if getattr(p, "predicate", None) == target_predicate:
                    matching_kp = p
                    break

            if matching_kp is not None:
                if hasattr(matching_kp, "subject") and matching_kp.subject:
                    roles.append(
                        SemanticRoleBinding(
                            role=":ARG0",
                            concept_id=matching_kp.subject,
                            canonical_lemma=matching_kp.subject.replace("ent:", ""),
                            allow_ellipsis=(target_language in ("vi", "ja")),
                        )
                    )
                if hasattr(matching_kp, "object") and matching_kp.object:
                    roles.append(
                        SemanticRoleBinding(
                            role=":ARG1",
                            concept_id=matching_kp.object,
                            canonical_lemma=matching_kp.object.replace("ent:", ""),
                            allow_ellipsis=False,
                        )
                    )

        # If focus argument present and not in roles
        if focus_arg and not any(r.concept_id == focus_arg or r.canonical_lemma == focus_arg for r in roles):
            synonyms: Tuple[str, ...] = ()
            if focus_arg in ("ent:lucia", "lucia"):
                synonyms = ("lucia", "i", "me", "my", "em", "tôi", "watashi")
            roles.append(
                SemanticRoleBinding(
                    role=":ARG0" if not roles else ":ARG1",
                    concept_id=focus_arg,
                    canonical_lemma=focus_arg.replace("ent:", ""),
                    lexical_synonyms=synonyms,
                    allow_ellipsis=(target_language in ("vi", "ja")),
                )
            )

        spk = speaker_honorific if speaker_honorific is not None else ("em" if target_language == "vi" else None)
        addr = addressee_honorific if addressee_honorific is not None else ("anh" if target_language == "vi" else None)
        forbid_list = list(forbidden_additions) if forbidden_additions else []
        if target_language == "vi" and "bạn" not in forbid_list:
            forbid_list.append("bạn")
        forbidden_tuple = tuple(forbid_list)
        caps_directives = getattr(caps_result, "directives", None) or None
        obligation = getattr(caps_result, "conversational_obligation", None)

        return cls(
            contract_id=str(uuid.uuid4()),
            target_language=target_language,
            act=act_enum,
            polarity=polarity,
            epistemic_status=epistemic_enum,
            target_predicate=target_predicate,
            role_bindings=tuple(roles),
            scope_type=scope_type,
            provenance=prov_rec,
            forbidden_additions=forbidden_tuple,
            somatic_modifiers=somatic_modifiers or {},
            directives=caps_directives,
            speaker_honorific=spk,
            addressee_honorific=addr,
            conversational_obligation=obligation,
            dialogue_phase=dialogue_phase,
            timestamp=time.time(),
        )


# Canonical production realization targets (ADR-035 / Phase 23 Production Output Simplification)
CANONICAL_TEXT_OUTPUT_LANGUAGE: str = "en"
CANONICAL_VOICE_OUTPUT_LANGUAGE: str = "ja"


@dataclass(frozen=True)
class TextRealization:
    """
    Surface text output adhering to canonical production language.
    Production default is CANONICAL_TEXT_OUTPUT_LANGUAGE ('en').
    """
    content: str
    language: str = CANONICAL_TEXT_OUTPUT_LANGUAGE


@dataclass(frozen=True)
class VoiceRealization:
    """
    Japanese voice realization for neural TTS/RVC playback.
    Production default is CANONICAL_VOICE_OUTPUT_LANGUAGE ('ja').
    """
    content: str   # Japanese text to synthesize
    language: str = CANONICAL_VOICE_OUTPUT_LANGUAGE


@dataclass(frozen=True)
class RealizationOutput:
    """
    Structured realization output separating textual response from vocal actuation.

    RealizationOutput
    ├── text
    │   └── language = CANONICAL_TEXT_OUTPUT_LANGUAGE ("en")
    │
    └── voice
        └── language = CANONICAL_VOICE_OUTPUT_LANGUAGE ("ja")

    Architectural Invariant:
    Both text and voice branches realize in parallel from language-independent
    semantic and pragmatic state (RealizationInputContract & Grounded Propositions).
    Neither branch acts as a semantic intermediary for the other.
    """
    text: TextRealization
    voice: VoiceRealization

    def to_dict(self) -> Dict[str, Any]:
        return {
            "text": {
                "content": self.text.content,
                "language": self.text.language,
            },
            "voice": {
                "content": self.voice.content,
                "language": self.voice.language,
            },
        }


