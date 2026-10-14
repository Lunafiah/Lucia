"""
src/core/communication/caps.py

Production implementation of Communicative Act & Proposition Selection (CAPS).
Phase 23 Semantic Substrate — Communicative Boundary Contract.

Architecturally ratified via:
- P23_CAPS_BOUNDARY_CONTRACT_DESIGN.md
- CAPS_IMPLEMENTATION_CONTRACT.md
- CAPS_IMPLEMENTATION_RATIFICATION.md

Boundary Scope:
    Cognitive / dialogue state + Admissible evidence
        ↓
      CAPS
        ↓
    WHAT TO COMMUNICATE:
        - Communicative Act
        - Grounded SemanticGraph (language-independent)
        - Epistemic Metadata
        - Provenance Metadata
        - Resolution / Admissibility Result

Strict Invariants:
1. WHAT vs HOW separation: CAPS owns WHAT to communicate. Downstream language
   realization / SLM owns HOW to express it.
2. Grounding Invariant: CAPS SHALL NOT emit an ASSERT or ANSWER proposition as an
   asserted claim unless the proposition has admissible grounding.
   Missing grounding fails closed to INQUIRE or REFUSE.
3. Reference Resolution != Epistemic State:
   RESOLVED != FACT.
   Resolving a referent binds discourse identity; it never upgrades a hypothesis to FACT.
4. Provenance Policy:
   USER_STATED != FACT.
   User assertions are retained with USER_STATED provenance and do not automatically
   claim FACT. Contradictions trigger CLARIFY to prevent silent overwrites.
5. Determinism: Bit-exact serialization and canonical hashing on frozen input.
"""

from __future__ import annotations

import hashlib
import json
from dataclasses import asdict, dataclass, field
from enum import Enum
from typing import Any, Dict, List, Optional, Sequence, Set, Tuple

from src.core.cognition.kernel.engine import (
    INFO_REASON_AMBIGUOUS_REFERENT,
    INFO_REASON_MISSING_PREMISE,
    INFO_REASON_UNGROUNDED_VARIABLE,
    InformationSubgoal,
)
from src.core.knowledge.fortification import (
    EpistemicState,
    ProvenanceRecord,
    ScopeBoundary,
    ScopeType,
    SemanticEdge,
    SemanticGraph,
    SemanticNode,
)
from src.core.knowledge.proposition import Proposition, ProvenanceType
from src.core.orchestrator.discourse_cache import DiscourseReferent, ResolutionStatus


# ── 1. Communicative Acts ────────────────────────────────────────────────────────

class CommunicativeAct(str, Enum):
    """
    Language-independent communicative act categories ratified under CAPS contract.
    """
    ASSERT = "ASSERT"          # State a grounded, verified proposition
    ANSWER = "ANSWER"          # Direct grounded response to a query
    INQUIRE = "INQUIRE"        # Pose question to resolve missing premise/variable
    CLARIFY = "CLARIFY"        # Request disambiguation between competing candidates/conflicts
    ACKNOWLEDGE = "ACKNOWLEDGE"# Confirm receipt or social attunement
    GREET = "GREET"            # Conversational opening
    FAREWELL = "FAREWELL"      # Conversational closing
    REFUSE = "REFUSE"          # Fail-closed refusal when grounding is absent or invalid


# ── 2. Input Snapshots ───────────────────────────────────────────────────────────

@dataclass(frozen=True)
class DialogueContextSnapshot:
    """Snapshot of current turn conversational & discourse state."""
    turn_id: int
    input_text: str
    active_referents: Sequence[DiscourseReferent] = field(default_factory=tuple)
    resolution_status: ResolutionStatus = ResolutionStatus.UNKNOWN
    resolved_entity_id: Optional[str] = None
    candidate_referent_ids: Sequence[str] = field(default_factory=tuple)


@dataclass(frozen=True)
class CognitiveStateSnapshot:
    """Snapshot of internal cognitive candidate goals and physiological state."""
    candidate_predicate: Optional[str] = None
    candidate_subject: Optional[str] = None
    candidate_object: Optional[str] = None
    polarity: bool = True
    active_goal_id: Optional[str] = None
    internal_confidence: Optional[float] = None


@dataclass(frozen=True)
class AdmissibleEvidencePool:
    """Pool of verified and user-asserted knowledge accessible for grounding."""
    verified_propositions: Sequence[Proposition] = field(default_factory=tuple)
    user_claims: Sequence[Proposition] = field(default_factory=tuple)


@dataclass(frozen=True)
class CommunicationPolicySnapshot:
    """Phase 16 communicative attunement parameters for S11 conditioning."""
    strategy: str = "balanced"
    directness: float = 1.0
    formality: float = 0.5
    elaboration: float = 0.5
    supportiveness: float = 0.5


# ── 3. Metadata Structures ───────────────────────────────────────────────────────

@dataclass(frozen=True)
class EpistemicMetadata:
    """Epistemic status and grounding classification of the selected proposition."""
    status: EpistemicState
    confidence: Optional[float] = None
    is_grounded: bool = False

    def to_dict(self) -> Dict[str, Any]:
        return {
            "status": self.status.value,
            "confidence": self.confidence,
            "is_grounded": self.is_grounded,
        }


@dataclass(frozen=True)
class ProvenanceMetadata:
    """Detailed provenance tracking for verifiable lineage."""
    origin: str
    premise_ids: Sequence[str] = field(default_factory=tuple)
    rule_id: Optional[str] = None
    session_id: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "origin": self.origin,
            "premise_ids": list(self.premise_ids),
            "rule_id": self.rule_id,
            "session_id": self.session_id,
            "metadata": dict(self.metadata),
        }


@dataclass(frozen=True)
class ResolutionAdmissibilityMetadata:
    """Discourse resolution and grounding validation outcome."""
    resolution_status: ResolutionStatus
    resolved_entity_id: Optional[str] = None
    candidate_referent_ids: Sequence[str] = field(default_factory=tuple)
    grounding_status: str = "UNCHECKED"
    failure_reason: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        return {
            "resolution_status": self.resolution_status.value,
            "resolved_entity_id": self.resolved_entity_id,
            "candidate_referent_ids": list(self.candidate_referent_ids),
            "grounding_status": self.grounding_status,
            "failure_reason": self.failure_reason,
        }


# ── 4. CAPS Result ───────────────────────────────────────────────────────────────

@dataclass
class CAPSResult:
    """
    Consolidated output of Communicative Act & Proposition Selection.
    Specifies WHAT to communicate at the cognitive boundary.
    """
    act: CommunicativeAct
    semantic_graph: Optional[SemanticGraph]
    epistemic_metadata: EpistemicMetadata
    provenance_metadata: ProvenanceMetadata
    resolution_metadata: ResolutionAdmissibilityMetadata
    grounded: bool
    target_predicate: Optional[str] = None
    focus_argument: Optional[str] = None
    directives: str = ""
    error_or_fallback_reason: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        return {
            "act": self.act.value,
            "has_semantic_graph": self.semantic_graph is not None,
            "epistemic": self.epistemic_metadata.to_dict(),
            "provenance": self.provenance_metadata.to_dict(),
            "resolution": self.resolution_metadata.to_dict(),
            "grounded": self.grounded,
            "target_predicate": self.target_predicate,
            "focus_argument": self.focus_argument,
            "directives": self.directives,
            "error_or_fallback_reason": self.error_or_fallback_reason,
        }

    def canonical_hash(self) -> str:
        """Deterministic bit-exact SHA-256 hash representation of CAPS decision."""
        payload = {
            "act": self.act.value,
            "epistemic": self.epistemic_metadata.to_dict(),
            "provenance": self.provenance_metadata.to_dict(),
            "resolution": self.resolution_metadata.to_dict(),
            "grounded": self.grounded,
            "target_predicate": self.target_predicate,
            "focus_argument": self.focus_argument,
            "directives": self.directives,
            "error": self.error_or_fallback_reason,
        }
        serialized = json.dumps(payload, sort_keys=True)
        return hashlib.sha256(serialized.encode("utf-8")).hexdigest()


# ── 5. Graph Builders ────────────────────────────────────────────────────────────

def build_inquire_graph(
    predicate_symbol: str,
    focus_arg_symbol: str,
    known_arg_symbol: Optional[str] = None,
    session_id: str = "session:inquire",
    polarity: bool = True,
) -> SemanticGraph:
    """Build a language-independent SemanticGraph representing an inquiry."""
    graph = SemanticGraph(session_id=session_id)
    event_id = f"node:inquire_{predicate_symbol.replace(':', '_')}"
    event_node = SemanticNode(
        id=event_id,
        epistemic_state=EpistemicState.UNKNOWN,
        concept_symbol=predicate_symbol,
        polarity=polarity,
    )
    graph.add_node(event_node)

    # Focus node (the unknown variable being queried)
    focus_node = SemanticNode(
        id=focus_arg_symbol,
        epistemic_state=EpistemicState.UNKNOWN,
        concept_symbol="c:UNKNOWN_REFERENT",
    )
    graph.add_node(focus_node)
    graph.add_edge(SemanticEdge(source_id=event_id, target_id=focus_arg_symbol, relation_role=":ARG0"))

    # Known grounding node if present
    if known_arg_symbol:
        known_node = SemanticNode(
            id=known_arg_symbol,
            epistemic_state=EpistemicState.FACT,
            concept_symbol=known_arg_symbol,
        )
        graph.add_node(known_node)
        graph.add_edge(SemanticEdge(source_id=event_id, target_id=known_arg_symbol, relation_role=":ARG1"))

    return graph


def build_assertion_graph(
    predicate_symbol: str,
    subject_symbol: str,
    object_symbol: str,
    provenance: ProvenanceRecord,
    epistemic_state: EpistemicState = EpistemicState.FACT,
    session_id: str = "session:assert",
    polarity: bool = True,
) -> SemanticGraph:
    """Build a language-independent SemanticGraph representing a grounded assertion."""
    graph = SemanticGraph(session_id=session_id)
    event_id = f"node:assert_{predicate_symbol.replace(':', '_')}"
    event_node = SemanticNode(
        id=event_id,
        epistemic_state=epistemic_state,
        concept_symbol=predicate_symbol,
        polarity=polarity,
        provenance=provenance,
    )
    graph.add_node(event_node)

    # Subject (ARG0)
    subj_node = SemanticNode(
        id=subject_symbol,
        epistemic_state=epistemic_state,
        concept_symbol=subject_symbol,
    )
    graph.add_node(subj_node)
    graph.add_edge(SemanticEdge(source_id=event_id, target_id=subject_symbol, relation_role=":ARG0"))

    # Object (ARG1)
    obj_node = SemanticNode(
        id=object_symbol,
        epistemic_state=epistemic_state,
        concept_symbol=object_symbol,
    )
    graph.add_node(obj_node)
    graph.add_edge(SemanticEdge(source_id=event_id, target_id=object_symbol, relation_role=":ARG1"))

    return graph


# ── 6. Functional Transformation: evaluate_caps ─────────────────────────────────

def evaluate_caps(
    dialogue_ctx: DialogueContextSnapshot,
    cognitive_state: CognitiveStateSnapshot,
    evidence_pool: AdmissibleEvidencePool,
    subgoals: Optional[Sequence[InformationSubgoal]] = None,
    comm_policy: Optional[CommunicationPolicySnapshot] = None,
    session_id: str = "session:caps",
) -> CAPSResult:
    """
    Core functional transformation implementing the ratified CAPS boundary contract.
    Decides WHAT to communicate given the current cognitive and dialogue state.
    """
    # ── Priority 1: InformationSubgoal -> Inquire/Clarify Compiler (Gate R1) ──────
    if subgoals and len(subgoals) > 0:
        active_subgoal = subgoals[0]
        if active_subgoal.reason_code == INFO_REASON_AMBIGUOUS_REFERENT:
            # Ambiguous referent requires CLARIFY
            return CAPSResult(
                act=CommunicativeAct.CLARIFY,
                semantic_graph=None,
                epistemic_metadata=EpistemicMetadata(
                    status=EpistemicState.AMBIGUOUS,
                    confidence=None,
                    is_grounded=False,
                ),
                provenance_metadata=ProvenanceMetadata(
                    origin="REASONING_SUBGOAL",
                    metadata={"reason_code": active_subgoal.reason_code},
                    session_id=session_id,
                ),
                resolution_metadata=ResolutionAdmissibilityMetadata(
                    resolution_status=ResolutionStatus.AMBIGUOUS,
                    grounding_status="NOT_REQUIRED",
                ),
                grounded=False,
                directives="Request clarification between competing ambiguous entity referents.",
            )

        # Missing premise or ungrounded variable -> INQUIRE
        pred_sym = f"c:PRED_{active_subgoal.target_predicate_id}"
        wh_arg = "ent:wh_target_arg0" if active_subgoal.arg0_id <= 0 else f"ent:entity_{active_subgoal.arg0_id}"
        known_arg = f"ent:entity_{active_subgoal.arg1_id}" if active_subgoal.arg1_id > 0 else None

        inquire_graph = build_inquire_graph(
            predicate_symbol=pred_sym,
            focus_arg_symbol=wh_arg,
            known_arg_symbol=known_arg,
            session_id=session_id,
            polarity=active_subgoal.polarity,
        )

        return CAPSResult(
            act=CommunicativeAct.INQUIRE,
            semantic_graph=inquire_graph,
            epistemic_metadata=EpistemicMetadata(
                status=EpistemicState.UNKNOWN,
                confidence=None,
                is_grounded=False,
            ),
            provenance_metadata=ProvenanceMetadata(
                origin="REASONING_SUBGOAL",
                metadata={"reason_code": active_subgoal.reason_code},
                session_id=session_id,
            ),
            resolution_metadata=ResolutionAdmissibilityMetadata(
                resolution_status=ResolutionStatus.UNKNOWN,
                grounding_status="NOT_REQUIRED",
            ),
            grounded=False,
            target_predicate=pred_sym,
            focus_argument=wh_arg,
            directives="Pose inquiry to resolve missing premise or ungrounded variable.",
        )

    # ── Priority 2: Discourse Ambiguity Handling (Gate R3) ────────────────────────
    if dialogue_ctx.resolution_status == ResolutionStatus.AMBIGUOUS:
        return CAPSResult(
            act=CommunicativeAct.CLARIFY,
            semantic_graph=None,
            epistemic_metadata=EpistemicMetadata(
                status=EpistemicState.AMBIGUOUS,
                confidence=None,
                is_grounded=False,
            ),
            provenance_metadata=ProvenanceMetadata(
                origin="DISCOURSE_AMBIGUITY",
                session_id=session_id,
            ),
            resolution_metadata=ResolutionAdmissibilityMetadata(
                resolution_status=ResolutionStatus.AMBIGUOUS,
                candidate_referent_ids=dialogue_ctx.candidate_referent_ids,
                grounding_status="NOT_REQUIRED",
            ),
            grounded=False,
            directives=f"Request disambiguation between competing candidates: {list(dialogue_ctx.candidate_referent_ids)}.",
        )

    if dialogue_ctx.resolution_status == ResolutionStatus.TYPE_MISMATCH:
        return CAPSResult(
            act=CommunicativeAct.CLARIFY,
            semantic_graph=None,
            epistemic_metadata=EpistemicMetadata(
                status=EpistemicState.AMBIGUOUS,
                confidence=None,
                is_grounded=False,
            ),
            provenance_metadata=ProvenanceMetadata(
                origin="DISCOURSE_TYPE_MISMATCH",
                session_id=session_id,
            ),
            resolution_metadata=ResolutionAdmissibilityMetadata(
                resolution_status=ResolutionStatus.TYPE_MISMATCH,
                grounding_status="NOT_REQUIRED",
                failure_reason="No discourse referent matches requested entity constraints.",
            ),
            grounded=False,
            directives="Clarify entity reference due to semantic/type mismatch in discourse context.",
        )

    # ── Priority 3: User Assertion & Contradiction Policy (Gate R4) ───────────────
    if evidence_pool.user_claims:
        for claim in evidence_pool.user_claims:
            # Check contradiction against verified propositions
            contradiction_found = False
            conflicting_prop = None
            for vprop in evidence_pool.verified_propositions:
                if (
                    vprop.subject == claim.subject
                    and vprop.predicate == claim.predicate
                    and vprop.object != claim.object
                    and vprop.valid
                ):
                    contradiction_found = True
                    conflicting_prop = vprop
                    break

            if contradiction_found:
                # Contradiction detected: prevent silent overwrite -> CLARIFY
                return CAPSResult(
                    act=CommunicativeAct.CLARIFY,
                    semantic_graph=None,
                    epistemic_metadata=EpistemicMetadata(
                        status=EpistemicState.AMBIGUOUS,
                        confidence=claim.confidence,
                        is_grounded=False,
                    ),
                    provenance_metadata=ProvenanceMetadata(
                        origin="USER_ASSERTION_CONFLICT",
                        premise_ids=(claim.id, conflicting_prop.id) if conflicting_prop else (claim.id,),
                        session_id=session_id,
                        metadata={
                            "user_claim": claim.to_dict(),
                            "conflicting_verified_prop": conflicting_prop.to_dict() if conflicting_prop else None,
                        },
                    ),
                    resolution_metadata=ResolutionAdmissibilityMetadata(
                        resolution_status=dialogue_ctx.resolution_status,
                        grounding_status="CONFLICT_DETECTED",
                        failure_reason="User claim directly contradicts verified knowledge base.",
                    ),
                    grounded=False,
                    directives="Clarify contradiction between user statement and verified knowledge.",
                )

    # ── Priority 4: Conversational Openings & Closings ────────────────────────────
    input_lower = dialogue_ctx.input_text.lower().strip()
    if any(greet in input_lower for greet in ("hello", "hi", "hey", "good morning", "chào")):
        return CAPSResult(
            act=CommunicativeAct.GREET,
            semantic_graph=None,
            epistemic_metadata=EpistemicMetadata(status=EpistemicState.FACT, is_grounded=True),
            provenance_metadata=ProvenanceMetadata(origin="CONVERSATIONAL_FLOW", session_id=session_id),
            resolution_metadata=ResolutionAdmissibilityMetadata(
                resolution_status=dialogue_ctx.resolution_status,
                grounding_status="NOT_REQUIRED",
            ),
            grounded=True,
            directives="Acknowledge conversational opening warmly and attentively.",
        )

    if any(farewell in input_lower for farewell in ("bye", "goodbye", "see you", "tạm biệt")):
        return CAPSResult(
            act=CommunicativeAct.FAREWELL,
            semantic_graph=None,
            epistemic_metadata=EpistemicMetadata(status=EpistemicState.FACT, is_grounded=True),
            provenance_metadata=ProvenanceMetadata(origin="CONVERSATIONAL_FLOW", session_id=session_id),
            resolution_metadata=ResolutionAdmissibilityMetadata(
                resolution_status=dialogue_ctx.resolution_status,
                grounding_status="NOT_REQUIRED",
            ),
            grounded=True,
            directives="Conclude conversation gently.",
        )

    # ── Priority 5: Candidate Proposition Grounding Invariant (Gate R2) ───────────
    if cognitive_state.candidate_predicate:
        # Candidate proposition proposed for assertion/answer
        matching_prop: Optional[Proposition] = None
        for p in evidence_pool.verified_propositions:
            if (
                p.predicate == cognitive_state.candidate_predicate
                and (not cognitive_state.candidate_subject or p.subject == cognitive_state.candidate_subject)
                and (not cognitive_state.candidate_object or p.object == cognitive_state.candidate_object)
                and p.valid
            ):
                matching_prop = p
                break

        if not matching_prop:
            # Fail-Closed Grounding Invariant:
            # Missing grounding prevents ASSERT or ANSWER. Emits REFUSE or INQUIRE.
            return CAPSResult(
                act=CommunicativeAct.REFUSE,
                semantic_graph=None,
                epistemic_metadata=EpistemicMetadata(
                    status=EpistemicState.UNKNOWN,
                    confidence=None,
                    is_grounded=False,
                ),
                provenance_metadata=ProvenanceMetadata(
                    origin="GROUNDING_REFUSAL",
                    session_id=session_id,
                ),
                resolution_metadata=ResolutionAdmissibilityMetadata(
                    resolution_status=dialogue_ctx.resolution_status,
                    grounding_status="UNGROUNDED",
                    failure_reason="Grounding Invariant Enforced: No admissible knowledge evidence found.",
                ),
                grounded=False,
                target_predicate=cognitive_state.candidate_predicate,
                focus_argument=cognitive_state.candidate_subject,
                error_or_fallback_reason="Ungrounded assertion rejected; fail-closed.",
                directives="Decline ungrounded factual assertion; state uncertainty accurately.",
            )

        # Admissible evidence found: synthesize grounded proposition
        prov_record = ProvenanceRecord(
            derivation_rule_id=None,
            supporting_premises=(matching_prop.id,),
            originating_session_id=session_id,
            metadata={"provenance_type": matching_prop.provenance.value, "confidence": matching_prop.confidence},
        )

        subj_sym = matching_prop.subject
        obj_sym = matching_prop.object
        pred_sym = matching_prop.predicate

        # Epistemic status depends on evidence provenance:
        # Note: USER_STATED != FACT
        if matching_prop.provenance == ProvenanceType.USER_STATED:
            epistemic_status = EpistemicState.INFERRED
        else:
            epistemic_status = EpistemicState.FACT

        assert_graph = build_assertion_graph(
            predicate_symbol=pred_sym,
            subject_symbol=subj_sym,
            object_symbol=obj_sym,
            provenance=prov_record,
            epistemic_state=epistemic_status,
            session_id=session_id,
            polarity=cognitive_state.polarity,
        )

        # Decide between ASSERT and ANSWER
        selected_act = CommunicativeAct.ANSWER if "?" in dialogue_ctx.input_text else CommunicativeAct.ASSERT

        return CAPSResult(
            act=selected_act,
            semantic_graph=assert_graph,
            epistemic_metadata=EpistemicMetadata(
                status=epistemic_status,
                confidence=matching_prop.confidence,
                is_grounded=True,
            ),
            provenance_metadata=ProvenanceMetadata(
                origin="KNOWLEDGE_STORE",
                premise_ids=(matching_prop.id,),
                session_id=session_id,
                metadata={"provenance_type": matching_prop.provenance.value},
            ),
            resolution_metadata=ResolutionAdmissibilityMetadata(
                resolution_status=dialogue_ctx.resolution_status,
                resolved_entity_id=dialogue_ctx.resolved_entity_id or subj_sym,
                grounding_status="GROUNDED",
            ),
            grounded=True,
            target_predicate=pred_sym,
            focus_argument=subj_sym,
            directives=f"Express grounded claim ({subj_sym}, {pred_sym}, {obj_sym}) accurately without exceeding facts.",
        )

    # ── Priority 5: Conversational Flow Defaults ───────────────────────────────────
    input_lower = dialogue_ctx.input_text.lower().strip()
    if any(greet in input_lower for greet in ("hello", "hi", "hey", "good morning", "chào")):
        return CAPSResult(
            act=CommunicativeAct.GREET,
            semantic_graph=None,
            epistemic_metadata=EpistemicMetadata(status=EpistemicState.FACT, is_grounded=True),
            provenance_metadata=ProvenanceMetadata(origin="CONVERSATIONAL_FLOW", session_id=session_id),
            resolution_metadata=ResolutionAdmissibilityMetadata(
                resolution_status=dialogue_ctx.resolution_status,
                grounding_status="NOT_REQUIRED",
            ),
            grounded=True,
            directives="Acknowledge conversational opening warmly and attentively.",
        )

    if any(farewell in input_lower for farewell in ("bye", "goodbye", "see you", "tạm biệt")):
        return CAPSResult(
            act=CommunicativeAct.FAREWELL,
            semantic_graph=None,
            epistemic_metadata=EpistemicMetadata(status=EpistemicState.FACT, is_grounded=True),
            provenance_metadata=ProvenanceMetadata(origin="CONVERSATIONAL_FLOW", session_id=session_id),
            resolution_metadata=ResolutionAdmissibilityMetadata(
                resolution_status=dialogue_ctx.resolution_status,
                grounding_status="NOT_REQUIRED",
            ),
            grounded=True,
            directives="Conclude conversation gently.",
        )

    # Default fallback: ACKNOWLEDGE
    return CAPSResult(
        act=CommunicativeAct.ACKNOWLEDGE,
        semantic_graph=None,
        epistemic_metadata=EpistemicMetadata(status=EpistemicState.FACT, is_grounded=True),
        provenance_metadata=ProvenanceMetadata(origin="CONVERSATIONAL_FLOW", session_id=session_id),
        resolution_metadata=ResolutionAdmissibilityMetadata(
            resolution_status=dialogue_ctx.resolution_status,
            grounding_status="NOT_REQUIRED",
        ),
        grounded=True,
        directives="Acknowledge user input attentively with empathic listening.",
    )
