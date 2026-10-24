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
import re
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
from src.core.language.detection import detect_active_language
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
    REQUEST = "REQUEST"        # Direct or indirect request for action/fulfillment
    EXPLAIN_CONCEPT = "EXPLAIN_CONCEPT"            # Direct conceptual explanation/elaboration
    ANSWER_PERSONAL_QUERY = "ANSWER_PERSONAL_QUERY"# Companion preference/self-disclosure
    ACKNOWLEDGE_REACTION = "ACKNOWLEDGE_REACTION"  # Acknowledge emotional reaction/interjection


# ── 1b. Dyadic Discourse Enums & State ──────────────────────────────────────────

class DialoguePhase(str, Enum):
    """Dynamic phase of the ongoing conversational session."""
    OPENING_ENCOUNTER = "OPENING_ENCOUNTER"
    ACTIVE_EXCHANGE = "ACTIVE_EXCHANGE"
    DEEPENING = "DEEPENING"
    CLOSING = "CLOSING"


class FloorStatus(str, Enum):
    """Floor ownership and conversational initiative state."""
    USER_HOLDING = "USER_HOLDING"
    YIELDED_TO_ASSISTANT = "YIELDED_TO_ASSISTANT"
    MUTUAL_OPEN = "MUTUAL_OPEN"


class PragmaticStance(str, Enum):
    """Pragmatic communicative stance adopted by participant in current turn."""
    NEUTRAL = "NEUTRAL"
    GREET_AND_MEET = "GREET_AND_MEET"
    HESITATION = "HESITATION"
    FLOOR_YIELD = "FLOOR_YIELD"
    SHARING = "SHARING"
    INQUIRING = "INQUIRING"
    CLOSING = "CLOSING"
    REQUEST_ACTION = "REQUEST_ACTION"


# ── 1c. Conversational Obligations ──────────────────────────────────────────

class ConversationalObligation(str, Enum):
    """
    Explicit typed conversational fulfillment obligations.
    Guarantees that an ANSWER or substantive speech act carries an unambiguous performance mandate.
    """
    # Existing obligations
    MINIMAL_PRESENCE_CALL = "MINIMAL_PRESENCE_CALL"
    GREET_BACK = "GREET_BACK"
    FAREWELL = "FAREWELL"
    FULFILL_SELF_INTRODUCTION = "FULFILL_SELF_INTRODUCTION"
    REASSURE_AND_GENTLE_INITIATIVE = "REASSURE_AND_GENTLE_INITIATIVE"
    ACKNOWLEDGE_REACTION_ONLY = "ACKNOWLEDGE_REACTION_ONLY"
    FULFILL_CONCEPT_EXPLANATION = "FULFILL_CONCEPT_EXPLANATION"
    FULFILL_PERSONAL_DISCLOSURE = "FULFILL_PERSONAL_DISCLOSURE"
    MUTUAL_ENCOUNTER_ACKNOWLEDGMENT = "MUTUAL_ENCOUNTER_ACKNOWLEDGMENT"
    ATTENTIVE_LISTENING = "ATTENTIVE_LISTENING"

    # Typed obligations for ANSWER branches
    ANSWER_ACTIVITY = "ANSWER_ACTIVITY"
    ANSWER_SELF_EXPLANATION = "ANSWER_SELF_EXPLANATION"
    ANSWER_CAPABILITY = "ANSWER_CAPABILITY"
    ANSWER_IDENTITY = "ANSWER_IDENTITY"
    ANSWER_PRESENCE = "ANSWER_PRESENCE"
    ANSWER_LISTENING = "ANSWER_LISTENING"
    ANSWER_THOUGHTS = "ANSWER_THOUGHTS"
    ANSWER_GENERAL = "ANSWER_GENERAL"


@dataclass
class PendingUserObligation:
    """
    Minimal explicit cross-turn conversational obligation state tracking.
    Enforces bounded lifetime (TTL) and non-revival of arbitrary old requests.
    """
    obligation_type: str
    originating_turn: int
    target_topic: Optional[str] = None
    completed: bool = False
    ttl_turns: int = 2

    @property
    def is_actionable(self) -> bool:
        return not self.completed and self.ttl_turns > 0

    def step_turn(self) -> None:
        if self.ttl_turns > 0:
            self.ttl_turns -= 1


@dataclass(frozen=True)
class DyadicDiscourseState:
    """Tracks dynamic interactive stance and floor relations across turns in a session."""
    dialogue_phase: DialoguePhase = DialoguePhase.OPENING_ENCOUNTER
    floor_status: FloorStatus = FloorStatus.MUTUAL_OPEN
    previous_assistant_act: Optional[str] = None
    previous_user_stance: Optional[str] = None
    unresolved_expectation: Optional[str] = None
    active_assistant_seed_term_id: int = 0
    inquiry_type: Optional[str] = None  # "OPEN", "CLOSED", "STATEMENT"

    def to_dict(self) -> Dict[str, Any]:
        return {
            "dialogue_phase": self.dialogue_phase.value if hasattr(self.dialogue_phase, "value") else str(self.dialogue_phase),
            "floor_status": self.floor_status.value if hasattr(self.floor_status, "value") else str(self.floor_status),
            "previous_assistant_act": self.previous_assistant_act,
            "previous_user_stance": self.previous_user_stance,
            "unresolved_expectation": self.unresolved_expectation,
            "active_assistant_seed_term_id": self.active_assistant_seed_term_id,
            "inquiry_type": self.inquiry_type,
        }


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
    dyadic_state: Optional[DyadicDiscourseState] = None
    previous_assistant_utterance: Optional[str] = None
    pending_user_obligation: Optional[PendingUserObligation] = None


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
    response_depth: str = "short"
    max_tokens_budget: int = 100


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
    pragmatic_stance: Optional[PragmaticStance] = None
    conversational_obligation: Optional[str] = None

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
            "pragmatic_stance": self.pragmatic_stance.value if self.pragmatic_stance else None,
            "conversational_obligation": self.conversational_obligation,
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
            "pragmatic_stance": self.pragmatic_stance.value if self.pragmatic_stance else None,
            "conversational_obligation": self.conversational_obligation,
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


# ── Regex patterns for lexical boundaries and action requests ────────────────
_GREETING_REGEX = re.compile(r"\b(hello|hi|hey|good morning|chào)\b", re.IGNORECASE)
_FAREWELL_REGEX = re.compile(r"\b(bye|goodbye|see you|tạm biệt)\b", re.IGNORECASE)
_SELF_INTRO_PATTERNS = (
    re.compile(r"\b(giới thiệu|kể|chia sẻ)\b.*?\b(bản thân|về mình|về em|mình)\b", re.IGNORECASE),
    re.compile(r"\btự giới thiệu\b", re.IGNORECASE),
    re.compile(r"\b(introduce\s+yourself|tell\s+me\s+about\s+yourself|tell\s+us\s+about\s+yourself)\b", re.IGNORECASE),
)

_REACTION_PATTERNS = (
    re.compile(r"\b(oh\s+my(\s+gosh|\s+god)?|omg|oh\s+wow|wow|whoa|gosh|oh\s+really|really\?|no\s+way|that's\s+amazing|that's\s+cool|i\s+see|aha|ouch|yikes|oh\s+dear|dear\s+me)\b", re.IGNORECASE),
    re.compile(r"\b(thật\s+(sao|á|vậy|thế)|trời\s+(ơi|ạ)|thế\s+(á|à)|vậy\s+hả|chà|ôi\s+(chao|trời)|hay\s+quá|tuyệt\s+vời|ghê\s+vậy|đỉnh\s+vậy)\b", re.IGNORECASE),
    re.compile(r"(へえ|すごい|まさか|本当|本当ですか|そうなんだ|あら)", re.IGNORECASE),
)

_EXPLANATION_PATTERNS = (
    re.compile(r"\b(explain(\s+about|\s+to\s+me|\s+more)?|can\s+you\s+explain|could\s+you\s+explain|please\s+explain|elaborate(\s+on)?|tell\s+me(\s+more)?\s+about|meaning\s+of|definition\s+of|understand\s+more\s+about)\b", re.IGNORECASE),
    re.compile(r"\b(interested\s+in\b.*?\bexplain)\b", re.IGNORECASE),
    re.compile(r"\b(how\s+does\s+.+\s+work|what\s+does\s+.+\s+mean|what\s+is\s+meant\s+by)\b", re.IGNORECASE),
    re.compile(r"\b(why\s+does\b.*?\b(?:separate|use|have|work|operate|rely))\b", re.IGNORECASE),
    re.compile(r"\b(tại\s+sao\b.*?\b(?:tách|dùng|sử\s+dụng|hoạt\s+động))\b", re.IGNORECASE),
    re.compile(r"\b(giải\s+thích(\s+về|\s+thêm|\s+cho)?|nói\s+rõ\s+hơn(\s+về)?|kể\s+rõ\s+hơn(\s+về)?|thế\s+nào\s+là|hoạt\s+động\s+(thế\s+nào|như\s+thế\s+nào)|hiểu\s+thêm\s+về)\b", re.IGNORECASE),
    re.compile(r"(説明して|詳しく教えて|について教えて|とは何|どういう意味)", re.IGNORECASE),
    # Case E: Comparative and conceptual difference questions
    re.compile(r"\b(khác\s+nhau\s+(?:thế\s+nào|như\s+thế\s+nào|ra\s+sao)|sự\s+khác\s+nhau\s+(?:giữa|của)?|so\s+sánh\b|phân\s+biệt\b)", re.IGNORECASE),
    re.compile(r"\b(what\s+is\s+the\s+difference\s+between|how\s+(?:are|do)\s+.+?\s+differ(?:ent)?|difference\s+between|compare\b)", re.IGNORECASE),
    re.compile(r"\b((?:kiến\s+trúc|hệ\s+thống|cơ\s+chế|mô\s+hình)\b.*?\b(?:như\s+thế\s+nào|ra\s+sao|thế\s+nào))\b", re.IGNORECASE),
    re.compile(r"\b(how\s+is\s+.+?\s+(?:structured|architected|organized)|what\s+is\s+the\s+architecture\s+of)\b", re.IGNORECASE),
    re.compile(r"(違いは何|どう違|比較して)", re.IGNORECASE),
)

_CONTINUATION_PATTERNS = (
    re.compile(r"\b(bắt\s+đầu(\s+đi|\s+nào|\s+nhé)?|tiếp\s+tục(\s+đi|\s+nào|\s+nhé)?|nói\s+tiếp(\s+đi|\s+nào)?|tiếp\s+đi|triển\s+khai\s+đi|nói\s+đi)\b", re.IGNORECASE),
    re.compile(r"\b(go\s+ahead|let['’]?s\s+start|start\s+please|continue(\s+please)?|begin|go\s+on|please\s+start)\b", re.IGNORECASE),
    re.compile(r"(始めて|続けて|さあ始めて|どうぞ)", re.IGNORECASE),
)

_VOCATIVE_PRESENCE_PATTERNS = (
    re.compile(r"^(?:ciah|lucia|em)\s+ơi[\.\?\!\s]*$", re.IGNORECASE),
    re.compile(r"^ơi\s+(?:ciah|lucia|em)[\.\?\!\s]*$", re.IGNORECASE),
    re.compile(r"^(?:ciah|lucia)[\?\!\.\s]*$", re.IGNORECASE),
    re.compile(r"^(?:are\s+you\s+there|you\s+there)[\?\!\.\s]*$", re.IGNORECASE),
    re.compile(r"^(?:ルシア|ねえルシア|ルシアちゃん)[\?\!\.\s]*$", re.IGNORECASE),
)

_PERSONAL_QUERY_PATTERNS = (
    re.compile(r"\b(favor(?:ite|ite)\s+(?:food|dish|color|music|song|book|movie|thing)|any\s+favor(?:ite|ite)|your\s+favor(?:ite|ite))\b", re.IGNORECASE),
    re.compile(r"\b(what\s+do\s+you\s+like|do\s+you\s+like|what\s+are\s+your\s+hobbies|any\s+hobbies|what\s+do\s+you\s+enjoy|what\s+do\s+you\s+prefer)\b", re.IGNORECASE),
    re.compile(r"\b(do\s+you\s+(?:eat|drink|sleep|dream))\b", re.IGNORECASE),
    re.compile(r"\b(món\s+(?:ăn\s+)?(?:yêu\s+thích|thích\s+nhất|nào)|thích\s+(?:ăn|làm|nghe|đọc|uống)\s+gì|sở\s+thích|màu\s+yêu\s+thích)\b", re.IGNORECASE),
    re.compile(r"\b((?:em|bạn)\s+có\s+thích|(?:em|bạn)\s+thích\s+gì|(?:em|bạn)\s+có\s+(?:ăn|uống|ngủ|mơ))\b", re.IGNORECASE),
    re.compile(r"(好きな(?:食べ物|色|曲|こと)|趣味|何が好き|好きですか)", re.IGNORECASE),
)


def _is_self_introduction_request(text: str) -> bool:
    """Detect natural language requests for self-introduction."""
    return any(p.search(text) for p in _SELF_INTRO_PATTERNS)


def _is_continuation_cue(text: str) -> bool:
    """Detect natural conversational continuation cues (e.g. 'Vậy bắt đầu đi', 'Go ahead')."""
    return any(p.search(text) for p in _CONTINUATION_PATTERNS)


def _is_reaction(text: str) -> bool:
    """Detect conversational reactions, exclamations, and emotional interjections."""
    return any(p.search(text) for p in _REACTION_PATTERNS)


def _is_explanation_request(text: str) -> bool:
    """Detect natural language requests for conceptual explanation or elaboration."""
    return any(p.search(text) for p in _EXPLANATION_PATTERNS)


def _is_personal_query(text: str) -> bool:
    """Detect personal preference, habit, or companion self-disclosure questions."""
    return any(p.search(text) for p in _PERSONAL_QUERY_PATTERNS)


def _is_vocative_presence_call(text: str) -> bool:
    """Detect minimal vocative social presence pings (e.g., 'Ciah ơi.', 'Lucia ơi')."""
    return any(p.search(text) for p in _VOCATIVE_PRESENCE_PATTERNS)


_WELLBEING_PATTERNS: Tuple[re.Pattern, ...] = (
    re.compile(r"\b(how\s+are\s+you|how\s+do\s+you\s+feel|how\s+are\s+things|how['’]s\s+it\s+going|how\s+is\s+it\s+going|how\s+have\s+you\s+been|how\s+is\s+your\s+day)\b", re.IGNORECASE),
    re.compile(r"\b(khỏe\s+không|có\s+khỏe\s+không|dạo\s+này\s+khỏe\s+không)\b", re.IGNORECASE),
    re.compile(r"\b(hôm\s+nay|dạo\s+này|sức\s+khỏe|tâm\s+trạng|mọi\s+chuyện|mọi\s+việc)\s+.*?\b(thế\s+nào|ra\s+sao)\b", re.IGNORECASE),
    re.compile(r"\b(em|anh|bạn|mình)\s+.*?\b(thế\s+nào|ra\s+sao)\b", re.IGNORECASE),
    re.compile(r"\b(cảm\s+thấy|trong\s+người)\s+(thế\s+nào|ra\s+sao)\b", re.IGNORECASE),
    re.compile(r"\b(thế\s+nào|ra\s+sao)\s+rồi\b", re.IGNORECASE),
    re.compile(r"^(?:em|anh|bạn)?\s*(?:thế\s+nào|ra\s+sao)[\?\!\.\s]*$", re.IGNORECASE),
)

_ANALYTICAL_EXCLUSION_PATTERNS: Tuple[re.Pattern, ...] = (
    re.compile(r"\b(cân\s+bằng|giải\s+quyết|xử\s+lý|vận\s+hành|hoạt\s+động|tính\s+toán|thực\s+hiện|phát\s+triển|thiết\s+kế)\b", re.IGNORECASE),
    re.compile(r"\b(làm\s+(?:sao|thế\s+nào)|nhìn\s+nhận\s+(?:thế\s+nào|ra\s+sao)|hiểu\s+(?:thế\s+nào|ra\s+sao))\b", re.IGNORECASE),
)


def _is_wellbeing_inquiry(text: str) -> bool:
    """Detect personal or relational wellbeing inquiries without capturing analytical 'thế nào'."""
    if any(p.search(text) for p in _ANALYTICAL_EXCLUSION_PATTERNS):
        return False
    return any(p.search(text) for p in _WELLBEING_PATTERNS)


def _evaluate_concept_coverage(
    target_concept: Optional[str],
    input_text: str,
    evidence_pool: AdmissibleEvidencePool,
) -> Tuple[EpistemicState, bool, int]:
    """
    Evaluates factual knowledge availability and coverage for a requested concept.
    Separates conversational request routing from epistemic grounding.

    Returns:
        (EpistemicState, is_grounded, matching_proposition_count)
    """
    if not evidence_pool or not evidence_pool.verified_propositions:
        return EpistemicState.UNKNOWN, False, 0

    target_norm = (target_concept or "").strip().lower()
    matching_props = []

    if target_norm in ("ent:lucia_architecture", "lucia_architecture"):
        # Explicit matching for Lucia architecture propositions
        for p in evidence_pool.verified_propositions:
            subj = getattr(p, "subject", "").lower()
            obj = getattr(p, "object", "").lower()
            if subj == "ent:lucia_architecture" or obj == "ent:lucia_architecture":
                matching_props.append(p)
            elif "lucia_architecture" in subj:
                matching_props.append(p)

        distinct_predicates = {getattr(p, "predicate", "") for p in matching_props}
        facet_count = len(distinct_predicates)

        if facet_count == 0:
            return EpistemicState.UNKNOWN, False, 0
        elif facet_count <= 2:
            return EpistemicState.PARTIAL, True, facet_count
        else:
            return EpistemicState.FACT, True, facet_count
    else:
        # General concept: inspect verified propositions for matching subject/object
        text_lower = input_text.lower()
        for p in evidence_pool.verified_propositions:
            subj_clean = getattr(p, "subject", "").lower().replace("ent:", "")
            obj_clean = getattr(p, "object", "").lower().replace("ent:", "").replace("concept:", "")
            # Skip generic conversational/somatic propositions
            if subj_clean in ("dialogue", "relationship", "somatic") or obj_clean in ("true", "false"):
                continue
            if (subj_clean and subj_clean in text_lower) or (obj_clean and obj_clean in text_lower):
                matching_props.append(p)

        count = len(matching_props)
        if count == 0:
            return EpistemicState.UNKNOWN, False, 0
        elif count <= 2:
            return EpistemicState.PARTIAL, True, count
        else:
            return EpistemicState.FACT, True, count


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

    # Compound-opening check: Substantive encounter, questions, or requests must not collapse into bare GREET
    substantive_encounter_cues = (
        "gặp em", "gặp nhau", "gặp được", "cuối cùng cũng", "finally met", "finally meet",
        "nice to meet", "gặp lại", "mới gặp",
    )
    has_substantive_encounter = any(cue in input_lower for cue in substantive_encounter_cues)
    has_meta_inquiry = any(cue in input_lower for cue in (
        "lần đầu", "first time", "first conversation", "nói chuyện chưa", "từng gặp",
        "từng nói chuyện", "gặp nhau chưa", "quen nhau bao lâu", "mới gặp",
        "bao nhiêu lần", "bao lâu rồi", "how long have we", "have we spoken",
    ))
    has_action_request = _is_self_introduction_request(input_lower)
    # Question check: only substantive if query words exist beyond bare greeting
    has_substantive_question = (
        ("?" in input_lower or "？" in input_lower)
        and any(w in input_lower for w in ("what", "who", "where", "why", "how", "when", "gì", "ai", "đâu", "sao", "không"))
    )
    has_substantive_clause = has_substantive_encounter or has_meta_inquiry or has_substantive_question or has_action_request

    # Vocative presence call check (e.g., "Ciah ơi.", "Lucia ơi", "ơi em")
    if _is_vocative_presence_call(input_lower) and not has_substantive_clause:
        return CAPSResult(
            act=CommunicativeAct.ACKNOWLEDGE,
            semantic_graph=None,
            epistemic_metadata=EpistemicMetadata(status=EpistemicState.FACT, is_grounded=True),
            provenance_metadata=ProvenanceMetadata(origin="VOCATIVE_PRESENCE_CALL", session_id=session_id),
            resolution_metadata=ResolutionAdmissibilityMetadata(
                resolution_status=dialogue_ctx.resolution_status,
                grounding_status="CONVERSATIONAL_CONTEXT",
            ),
            grounded=True,
            target_predicate="c:PRESENCE_PING",
            focus_argument="ent:lucia",
            pragmatic_stance=PragmaticStance.GREET_AND_MEET,
            conversational_obligation="MINIMAL_PRESENCE_CALL",
            directives="Acknowledge the user's presence call with immediate, minimal presence (e.g., 'Em đây.' / 'I'm here.'). Do not elaborate, introspect, or explain.",
        )

    # Lexical boundary-safe greeting check (prevents English 'hi' matching inside Vietnamese 'thiệu')
    if _GREETING_REGEX.search(input_lower):
        if not has_substantive_clause:
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
                pragmatic_stance=PragmaticStance.GREET_AND_MEET,
                conversational_obligation="GREET_BACK",
                directives="Acknowledge conversational opening warmly and attentively.",
            )

    # Lexical boundary-safe farewell check
    if _FAREWELL_REGEX.search(input_lower):
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
            pragmatic_stance=PragmaticStance.CLOSING,
            conversational_obligation="FAREWELL",
            directives="Conclude conversation gently.",
        )

    # ── Priority 5: Candidate Proposition Grounding Invariant (Gate R2) ───────────
    has_explanation_or_continuation = (
        _is_explanation_request(input_lower)
        or (
            dialogue_ctx.pending_user_obligation is not None
            and dialogue_ctx.pending_user_obligation.is_actionable
            and _is_continuation_cue(input_lower)
        )
    )
    if cognitive_state.candidate_predicate and not has_explanation_or_continuation:
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
        # Note: USER_STATED != FACT; DERIVED / INFERRED != FACT
        if matching_prop.provenance in (
            ProvenanceType.USER_STATED,
            ProvenanceType.DERIVED,
            ProvenanceType.INFERRED,
        ):
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

    # ── Priority 6: Conversational Flow & Discourse Grounding ───────────────────────
    input_lower = dialogue_ctx.input_text.lower().strip()

    # 6.1 Meta-Conversational & Life-State Inquiries (e.g., first conversation, meeting history, interaction count)
    meta_history_cues = (
        "lần đầu", "first time", "first conversation", "nói chuyện chưa", "từng gặp",
        "từng nói chuyện", "gặp nhau chưa", "quen nhau bao lâu", "mới gặp",
        "bao nhiêu lần", "bao lâu rồi", "how long have we", "have we spoken",
    )
    if any(cue in input_lower for cue in meta_history_cues):
        # Look up verified life-state propositions in evidence pool
        first_conv_prop = None
        turn_count_prop = None
        fam_prop = None
        for p in evidence_pool.verified_propositions:
            if not getattr(p, "valid", True):
                continue
            pred = getattr(p, "predicate", "")
            if pred == "c:IS_FIRST_CONVERSATION":
                first_conv_prop = p
            elif pred == "c:TURN_COUNT":
                turn_count_prop = p
            elif pred == "c:FAMILIARITY_LEVEL":
                fam_prop = p

        if any(term in input_lower for term in ("lần đầu", "first time", "first conversation", "mới gặp", "nói chuyện chưa")):
            if first_conv_prop is not None:
                is_first = (str(first_conv_prop.object).lower() == "true")
                if is_first:
                    directive = "Xác nhận từ góc nhìn đồng hành ngôi thứ nhất rằng đây là lần đầu tiên em và anh nói chuyện với nhau."
                else:
                    directive = "Xác nhận từ góc nhìn đồng hành ngôi thứ nhất rằng em và anh đã từng trò chuyện với nhau trước đây, không phải lần đầu."
                return CAPSResult(
                    act=CommunicativeAct.ANSWER,
                    semantic_graph=None,
                    epistemic_metadata=EpistemicMetadata(status=EpistemicState.FACT, confidence=1.0, is_grounded=True),
                    provenance_metadata=ProvenanceMetadata(
                        origin="LIFE_STATE_VERIFIED",
                        premise_ids=(first_conv_prop.id,),
                        session_id=session_id,
                    ),
                    resolution_metadata=ResolutionAdmissibilityMetadata(
                        resolution_status=ResolutionStatus.RESOLVED,
                        resolved_entity_id="ent:lucia",
                        grounding_status="GROUNDED",
                    ),
                    grounded=True,
                    target_predicate="c:IS_FIRST_CONVERSATION",
                    focus_argument="ent:lucia",
                    directives=directive,
                )
            else:
                # Evidence missing: fail-closed with CLARIFY rather than allowing SLM to invent
                return CAPSResult(
                    act=CommunicativeAct.CLARIFY,
                    semantic_graph=None,
                    epistemic_metadata=EpistemicMetadata(status=EpistemicState.UNKNOWN, confidence=None, is_grounded=False),
                    provenance_metadata=ProvenanceMetadata(origin="MISSING_LIFE_STATE", session_id=session_id),
                    resolution_metadata=ResolutionAdmissibilityMetadata(
                        resolution_status=ResolutionStatus.UNKNOWN,
                        grounding_status="UNGROUNDED",
                        failure_reason="No verified interaction history found in evidence pool.",
                    ),
                    grounded=False,
                    directives="Hỏi lại để làm rõ vì chưa có dữ liệu xác thực về lịch sử tương tác.",
                )

    # 6.1b Request for Action (Self-Introduction)
    # Speech Act: REQUEST, Requested Action: c:SELF_INTRODUCTION, Obligation: FULFILL_SELF_INTRODUCTION
    if _is_self_introduction_request(input_lower):
        return CAPSResult(
            act=CommunicativeAct.REQUEST,
            semantic_graph=None,
            epistemic_metadata=EpistemicMetadata(status=EpistemicState.FACT, is_grounded=True),
            provenance_metadata=ProvenanceMetadata(origin="CONVERSATIONAL_REQUEST", session_id=session_id),
            resolution_metadata=ResolutionAdmissibilityMetadata(
                resolution_status=dialogue_ctx.resolution_status,
                grounding_status="CONVERSATIONAL_CONTEXT",
            ),
            grounded=True,
            target_predicate="c:SELF_INTRODUCTION",
            focus_argument="ent:lucia",
            pragmatic_stance=PragmaticStance.REQUEST_ACTION,
            conversational_obligation="FULFILL_SELF_INTRODUCTION",
            directives="Giới thiệu bản thân một cách ngắn gọn, chân thành, tự nhiên với tư cách là Lucia; xưng em, gọi anh.",
        )

    # Pure punctuation / hesitation check
    if re.fullmatch(r"[\s\?\!\.\,\…\—\-]+", dialogue_ctx.input_text):
        return CAPSResult(
            act=CommunicativeAct.ACKNOWLEDGE,
            semantic_graph=None,
            epistemic_metadata=EpistemicMetadata(status=EpistemicState.FACT, is_grounded=False),
            provenance_metadata=ProvenanceMetadata(origin="CONVERSATIONAL_HESITATION", session_id=session_id),
            resolution_metadata=ResolutionAdmissibilityMetadata(
                resolution_status=dialogue_ctx.resolution_status,
                grounding_status="CONVERSATIONAL_CONTEXT",
            ),
            grounded=False,
            target_predicate="c:CONVERSATIONAL_HESITATION",
            focus_argument="ent:dialogue",
            pragmatic_stance=PragmaticStance.FLOOR_YIELD,
            conversational_obligation="REASSURE_AND_GENTLE_INITIATIVE",
            directives="Nhẹ nhàng hỏi thăm và gợi mở tự nhiên khi nhận thấy sự bối rối hoặc ngập ngừng từ người dùng; xưng hô phù hợp.",
        )

    # 6.1c-0 Continuation of Pending User Obligation (e.g., "Vậy bắt đầu đi", "Go ahead")
    if dialogue_ctx.pending_user_obligation and dialogue_ctx.pending_user_obligation.is_actionable:
        if _is_continuation_cue(input_lower):
            pending_ob = dialogue_ctx.pending_user_obligation
            topic_str = f" regarding {pending_ob.target_topic}" if pending_ob.target_topic else ""
            is_pending_arch = bool(
                pending_ob.target_topic
                and any(k in pending_ob.target_topic.lower() for k in ("kiến trúc", "architecture"))
            )
            focus_arg = "ent:lucia_architecture" if is_pending_arch else None
            target_concept = focus_arg or pending_ob.target_topic
            ep_status, is_gr, _ = _evaluate_concept_coverage(
                target_concept=target_concept,
                input_text=pending_ob.target_topic or input_lower,
                evidence_pool=evidence_pool,
            )
            return CAPSResult(
                act=CommunicativeAct.EXPLAIN_CONCEPT if ("EXPLAN" in pending_ob.obligation_type) else CommunicativeAct.ANSWER,
                semantic_graph=None,
                epistemic_metadata=EpistemicMetadata(status=ep_status, is_grounded=is_gr),
                provenance_metadata=ProvenanceMetadata(origin="PENDING_OBLIGATION_CONTINUATION", session_id=session_id),
                resolution_metadata=ResolutionAdmissibilityMetadata(
                    resolution_status=dialogue_ctx.resolution_status,
                    grounding_status="CONVERSATIONAL_CONTEXT" if is_gr else "UNGROUNDED",
                    failure_reason=None if is_gr else "Pending concept explanation lacks verified grounding in knowledge base.",
                ),
                grounded=is_gr,
                target_predicate="c:CONCEPT_EXPLANATION" if ("EXPLAN" in pending_ob.obligation_type) else "c:CONTINUATION",
                focus_argument=focus_arg,
                pragmatic_stance=PragmaticStance.SHARING,
                conversational_obligation=pending_ob.obligation_type,
                directives=(
                    f"Directly begin and fulfill the pending substantive explanation requested by the user{topic_str}. "
                    "Deliver the substantive explanation immediately; do NOT merely acknowledge, do NOT ask what to focus on, "
                    "and do NOT ask the user to restate the topic."
                ),
            )

    # 6.1c Conversational Reaction / Interjection Check (e.g., "oh my", "wow", "thật sao")
    # Speech Act: ACKNOWLEDGE_REACTION, Obligation: ACKNOWLEDGE_REACTION_ONLY
    if _is_reaction(input_lower):
        return CAPSResult(
            act=CommunicativeAct.ACKNOWLEDGE_REACTION,
            semantic_graph=None,
            epistemic_metadata=EpistemicMetadata(status=EpistemicState.FACT, is_grounded=True),
            provenance_metadata=ProvenanceMetadata(origin="CONVERSATIONAL_REACTION", session_id=session_id),
            resolution_metadata=ResolutionAdmissibilityMetadata(
                resolution_status=dialogue_ctx.resolution_status,
                grounding_status="CONVERSATIONAL_CONTEXT",
            ),
            grounded=True,
            target_predicate="c:USER_REACTION",
            focus_argument=None,
            pragmatic_stance=PragmaticStance.NEUTRAL,
            conversational_obligation="ACKNOWLEDGE_REACTION_ONLY",
            directives="Acknowledge the user's reaction warmly and attentively in the present moment without unprompted long expositions, unless actively continuing an established conversational topic.",
        )

    # 6.1d Conceptual Explanation & Elaboration Requests
    # Speech Act: EXPLAIN_CONCEPT, Obligation: FULFILL_CONCEPT_EXPLANATION
    if _is_explanation_request(input_lower):
        active_lang = detect_active_language(dialogue_ctx.input_text)
        has_arch_kw = any(k in input_lower for k in ("kiến trúc", "architecture", "toàn bộ kiến trúc", "アーキテクチャ"))
        has_self_ref = any(k in input_lower for k in ("lucia", "em", "your", "toàn bộ kiến trúc", "của em"))
        is_arch = has_arch_kw and has_self_ref
        focus_arg = "ent:lucia_architecture" if is_arch else None

        ep_status, is_gr, cov_count = _evaluate_concept_coverage(
            target_concept=focus_arg,
            input_text=dialogue_ctx.input_text,
            evidence_pool=evidence_pool,
        )

        if ep_status == EpistemicState.FACT:
            if is_arch:
                if active_lang == "vi":
                    directives = "Giải thích trực tiếp, rõ ràng và mạch lạc về kiến trúc và các tầng nhận thức chính của Lucia một cách chu đáo, không hỏi lại hay né tránh."
                else:
                    directives = "Directly and clearly explain the architecture and cognitive pipeline of Lucia thoughtfully without unnecessary clarification questions or avoidance."
            else:
                if active_lang == "vi":
                    directives = (
                        "Trực tiếp giải thích và so sánh khách quan, chính xác khái niệm được yêu cầu dựa trên kiến thức xác thực đã có. "
                        "Preserve the user's semantic target without artificially framing general concepts around Lucia's personal architecture, games, or gameplay unless specifically requested by the user."
                    )
                else:
                    directives = (
                        "Directly, objectively, and accurately explain and compare the requested concept in its own right based on verified knowledge. "
                        "Preserve the user's semantic target without artificially framing general concepts around Lucia's personal architecture, games, or gameplay unless specifically requested by the user."
                    )
        elif ep_status == EpistemicState.PARTIAL:
            if is_arch:
                if active_lang == "vi":
                    directives = "Giải thích các tầng nhận thức đã được xác thực của Lucia, và nêu rõ các khía cạnh còn lại chưa đủ thông tin để khẳng định. Tuyệt đối không bịa đặt."
                else:
                    directives = "Explain the verified cognitive layers of Lucia based on available evidence, and clearly state what remains unconfirmed. Do not fabricate."
            else:
                if active_lang == "vi":
                    directives = (
                        "Giải thích các phần đã được xác thực của khái niệm này dựa trên kiến thức hiện có, và nêu rõ những phần còn lại chưa có đủ thông tin xác thực. Tuyệt đối không bịa đặt."
                    )
                else:
                    directives = (
                        "Explain the verified portions of this concept based on available evidence, and clearly state what remains unconfirmed. Do not fabricate."
                    )
        else:  # UNKNOWN
            if is_arch:
                if active_lang == "vi":
                    directives = "Nêu rõ ràng và chân thành rằng em chưa có thông tin xác thực để giải thích về kiến trúc này. Tuyệt đối không bịa đặt, và không hỏi lại làm rõ vì câu hỏi đã rõ nghĩa."
                else:
                    directives = "Politely and honestly state that you do not have verified knowledge about this architecture. Do not fabricate, and do not ask for clarification."
            else:
                if active_lang == "vi":
                    directives = (
                        "Nêu rõ ràng và chân thành rằng em chưa có thông tin xác thực trong cơ sở tri thức để giải thích hoặc so sánh về khái niệm này. Tuyệt đối không bịa đặt, không suy đoán và không hỏi lại làm rõ vì câu hỏi đã rõ nghĩa."
                    )
                else:
                    directives = (
                        "Politely and honestly state that you do not have verified knowledge in your knowledge base to explain or compare this concept. Do not fabricate, do not speculate, and do not ask for clarification."
                    )

        return CAPSResult(
            act=CommunicativeAct.EXPLAIN_CONCEPT,
            semantic_graph=None,
            epistemic_metadata=EpistemicMetadata(status=ep_status, is_grounded=is_gr),
            provenance_metadata=ProvenanceMetadata(origin="CONCEPT_EXPLANATION", session_id=session_id),
            resolution_metadata=ResolutionAdmissibilityMetadata(
                resolution_status=dialogue_ctx.resolution_status,
                grounding_status="CONVERSATIONAL_CONTEXT" if is_gr else "UNGROUNDED",
                failure_reason=None if is_gr else "Concept lacks verified grounding in knowledge base.",
            ),
            grounded=is_gr,
            target_predicate="c:CONCEPT_EXPLANATION",
            focus_argument=focus_arg,
            pragmatic_stance=PragmaticStance.SHARING,
            conversational_obligation="FULFILL_CONCEPT_EXPLANATION",
            directives=directives,
        )

    # 6.1e Personal Preference & Companion Self-Disclosure Inquiries
    # Speech Act: ANSWER_PERSONAL_QUERY, Obligation: FULFILL_PERSONAL_DISCLOSURE
    if _is_personal_query(input_lower):
        return CAPSResult(
            act=CommunicativeAct.ANSWER_PERSONAL_QUERY,
            semantic_graph=None,
            epistemic_metadata=EpistemicMetadata(status=EpistemicState.FACT, is_grounded=True),
            provenance_metadata=ProvenanceMetadata(origin="COMPANION_SELF_DISCLOSURE", session_id=session_id),
            resolution_metadata=ResolutionAdmissibilityMetadata(
                resolution_status=dialogue_ctx.resolution_status,
                grounding_status="CONVERSATIONAL_CONTEXT",
            ),
            grounded=True,
            target_predicate="c:PERSONAL_QUERY",
            focus_argument="ent:lucia",
            pragmatic_stance=PragmaticStance.SHARING,
            conversational_obligation="FULFILL_PERSONAL_DISCLOSURE",
            directives="Respond to the user's personal query with genuine companion self-disclosure, reflecting your digital companion existence and preferences warmly without fabricating biological organs or physical bodily functions.",
        )

    # 6.2 Conversational Questions (Inquiries)
    is_question = (
        "?" in dialogue_ctx.input_text
        or "？" in dialogue_ctx.input_text
        or any(input_lower.startswith(w) for w in (
            "what", "who", "where", "why", "how", "when", "can you", "could you",
            "are you", "do you", "tell me", "bạn là", "em là", "bạn có", "em có"
        ))
        or any(w in input_lower for w in ("tell me about", "kể cho", "nói về"))
    )

    if is_question:
        # Distinguish semantic role of conversational questions
        if any(term in input_lower for term in ("who are you", "bạn là ai", "em là ai", "bạn tên gì", "em tên gì", "tên em là gì")):
            directive = "Answer the user's question about your identity and nature as a companion directly and warmly."
            return CAPSResult(
                act=CommunicativeAct.ANSWER,
                semantic_graph=None,
                epistemic_metadata=EpistemicMetadata(status=EpistemicState.FACT, is_grounded=True),
                provenance_metadata=ProvenanceMetadata(origin="COMPANION_IDENTITY", session_id=session_id),
                resolution_metadata=ResolutionAdmissibilityMetadata(
                    resolution_status=dialogue_ctx.resolution_status,
                    grounding_status="CONVERSATIONAL_CONTEXT",
                ),
                grounded=True,
                target_predicate="c:IDENTITY",
                focus_argument="ent:lucia",
                directives=directive,
                conversational_obligation=ConversationalObligation.ANSWER_IDENTITY.value,
            )
        elif any(term in input_lower for term in ("doing", "làm gì", "đang làm")):
            directive = "Answer the user's question about your current activity and presence with the user directly and warmly."
            return CAPSResult(
                act=CommunicativeAct.ANSWER,
                semantic_graph=None,
                epistemic_metadata=EpistemicMetadata(status=EpistemicState.FACT, is_grounded=True),
                provenance_metadata=ProvenanceMetadata(origin="COMPANION_ACTIVITY", session_id=session_id),
                resolution_metadata=ResolutionAdmissibilityMetadata(
                    resolution_status=dialogue_ctx.resolution_status,
                    grounding_status="CONVERSATIONAL_CONTEXT",
                ),
                grounded=True,
                target_predicate="c:ACTIVITY",
                focus_argument="ent:lucia",
                directives=directive,
                conversational_obligation=ConversationalObligation.ANSWER_ACTIVITY.value,
            )
        elif any(term in input_lower for term in ("what can you do", "có thể làm gì", "giúp được gì")):
            directive = "Answer the user's question about your capabilities and ways you can engage together."
            return CAPSResult(
                act=CommunicativeAct.ANSWER,
                semantic_graph=None,
                epistemic_metadata=EpistemicMetadata(status=EpistemicState.FACT, is_grounded=True),
                provenance_metadata=ProvenanceMetadata(origin="COMPANION_CAPABILITY", session_id=session_id),
                resolution_metadata=ResolutionAdmissibilityMetadata(
                    resolution_status=dialogue_ctx.resolution_status,
                    grounding_status="CONVERSATIONAL_CONTEXT",
                ),
                grounded=True,
                target_predicate="c:CAPABILITY",
                focus_argument="ent:lucia",
                directives=directive,
                conversational_obligation=ConversationalObligation.ANSWER_CAPABILITY.value,
            )
        elif any(term in input_lower for term in ("where are you", "ở đâu")):
            directive = "Answer the user's question regarding your presence in this companion space."
            return CAPSResult(
                act=CommunicativeAct.ANSWER,
                semantic_graph=None,
                epistemic_metadata=EpistemicMetadata(status=EpistemicState.FACT, is_grounded=True),
                provenance_metadata=ProvenanceMetadata(origin="COMPANION_PRESENCE", session_id=session_id),
                resolution_metadata=ResolutionAdmissibilityMetadata(
                    resolution_status=dialogue_ctx.resolution_status,
                    grounding_status="CONVERSATIONAL_CONTEXT",
                ),
                grounded=True,
                target_predicate="c:PRESENCE",
                focus_argument="ent:lucia",
                directives=directive,
                conversational_obligation=ConversationalObligation.ANSWER_PRESENCE.value,
            )
        elif any(term in input_lower for term in ("listening", "nghe không", "đang nghe")):
            directive = "Answer confirming your active presence and attentive listening to the user."
            return CAPSResult(
                act=CommunicativeAct.ANSWER,
                semantic_graph=None,
                epistemic_metadata=EpistemicMetadata(status=EpistemicState.FACT, is_grounded=True),
                provenance_metadata=ProvenanceMetadata(origin="COMPANION_ATTENTION", session_id=session_id),
                resolution_metadata=ResolutionAdmissibilityMetadata(
                    resolution_status=dialogue_ctx.resolution_status,
                    grounding_status="CONVERSATIONAL_CONTEXT",
                ),
                grounded=True,
                target_predicate="c:ATTENTION",
                focus_argument="ent:lucia",
                directives=directive,
                conversational_obligation=ConversationalObligation.ANSWER_LISTENING.value,
            )
        elif _is_wellbeing_inquiry(input_lower):
            directive = "Answer the user's inquiry regarding your current state and presence warmly, engaging with genuine companion attentiveness."
            return CAPSResult(
                act=CommunicativeAct.ANSWER,
                semantic_graph=None,
                epistemic_metadata=EpistemicMetadata(status=EpistemicState.FACT, is_grounded=True),
                provenance_metadata=ProvenanceMetadata(origin="COMPANION_STATE", session_id=session_id),
                resolution_metadata=ResolutionAdmissibilityMetadata(
                    resolution_status=dialogue_ctx.resolution_status,
                    grounding_status="CONVERSATIONAL_CONTEXT",
                ),
                grounded=True,
                target_predicate="c:WELLBEING",
                focus_argument="ent:lucia",
                directives=directive,
                conversational_obligation=ConversationalObligation.ANSWER_GENERAL.value,
            )
        elif any(term in input_lower for term in (
            "what are you thinking", "what's on your mind", "what is on your mind",
            "đang nghĩ gì", "nghĩ gì", "suy nghĩ gì", "nghĩ sao", "thấy sao",
            "quan điểm", "cân bằng", "nhìn nhận", "nghĩ thế nào", "thấy thế nào"
        )):
            directive = "Answer the user's question regarding your thoughts, sharing your gentle reflections and attentive presence in this conversation."
            return CAPSResult(
                act=CommunicativeAct.ANSWER,
                semantic_graph=None,
                epistemic_metadata=EpistemicMetadata(status=EpistemicState.FACT, is_grounded=True),
                provenance_metadata=ProvenanceMetadata(origin="COMPANION_REFLECTION", session_id=session_id),
                resolution_metadata=ResolutionAdmissibilityMetadata(
                    resolution_status=dialogue_ctx.resolution_status,
                    grounding_status="CONVERSATIONAL_CONTEXT",
                ),
                grounded=True,
                target_predicate="c:THOUGHTS",
                focus_argument="ent:lucia",
                directives=directive,
                conversational_obligation=ConversationalObligation.ANSWER_THOUGHTS.value,
            )
        elif any(term in input_lower for term in ("ý em là", "ý là sao", "what do you mean", "mean by", "mean when")):
            if dialogue_ctx.previous_assistant_utterance:
                prev_text = dialogue_ctx.previous_assistant_utterance.strip()
                directive = (
                    f"The user is asking what you meant by your previous statement: \"{prev_text}\". "
                    "Directly clarify and explain what you meant by that statement warmly, clearly, and thoughtfully without meta-commentary about the question itself."
                )
                pred_label = "c:UTTERANCE_CLARIFICATION"
            else:
                directive = "Answer explaining your grounded internal state or prior statement using natural, thoughtful language grounded in actual system context without meta-commentary."
                pred_label = "c:SELF_EXPLANATION"
            return CAPSResult(
                act=CommunicativeAct.ANSWER,
                semantic_graph=None,
                epistemic_metadata=EpistemicMetadata(status=EpistemicState.FACT, is_grounded=True),
                provenance_metadata=ProvenanceMetadata(origin="COMPANION_SELF_MODEL", session_id=session_id),
                resolution_metadata=ResolutionAdmissibilityMetadata(
                    resolution_status=dialogue_ctx.resolution_status,
                    grounding_status="CONVERSATIONAL_CONTEXT",
                ),
                grounded=True,
                target_predicate=pred_label,
                focus_argument="ent:lucia",
                directives=directive,
                conversational_obligation=ConversationalObligation.ANSWER_SELF_EXPLANATION.value,
            )
        else:
            # Epistemic Boundary (Part F): UNKNOWN != AMBIGUOUS.
            # Check if this inquiry is genuinely ambiguous (competing referents/interpretations) vs unknown factual query.
            is_ambiguous = (
                dialogue_ctx.resolution_status == ResolutionStatus.AMBIGUOUS
                or (dialogue_ctx.candidate_referent_ids and len(dialogue_ctx.candidate_referent_ids) > 1)
                or bool(re.search(r"\b(hay là|hay|hoặc|or|which one|cái nào)\b", input_lower) and ("?" in dialogue_ctx.input_text or "？" in dialogue_ctx.input_text))
            )
            active_lang = detect_active_language(dialogue_ctx.input_text)
            if is_ambiguous:
                dir_msg = (
                    "Hỏi câu làm rõ ngắn gọn nhất để xác định người dùng đang hỏi về khía cạnh hay đối tượng cụ thể nào trong các khả năng. Tuyệt đối không tự ý bịa đặt câu trả lời."
                    if active_lang == "vi"
                    else "Ask the minimum clarification required to identify which specific interpretation or referent the user is asking about. Do NOT fabricate an answer."
                )
                return CAPSResult(
                    act=CommunicativeAct.CLARIFY,
                    semantic_graph=None,
                    epistemic_metadata=EpistemicMetadata(status=EpistemicState.AMBIGUOUS, confidence=None, is_grounded=False),
                    provenance_metadata=ProvenanceMetadata(origin="DISCOURSE_AMBIGUITY", session_id=session_id),
                    resolution_metadata=ResolutionAdmissibilityMetadata(
                        resolution_status=ResolutionStatus.AMBIGUOUS,
                        grounding_status="NOT_REQUIRED",
                    ),
                    grounded=False,
                    directives=dir_msg,
                )
            else:
                # UNKNOWN: Question is unambiguous, but verified grounding is absent in knowledge base.
                # Must NOT route to CLARIFY. Emit REFUSE / truthful epistemic boundary statement.
                dir_msg = (
                    "Nêu rõ ràng, chân thực và từ tốn rằng em chưa có thông tin xác thực để trả lời câu hỏi này. Tuyệt đối không bịa đặt, và không hỏi lại làm rõ vì câu hỏi đã rõ nghĩa."
                    if active_lang == "vi"
                    else "State clearly, thoughtfully, and truthfully that you do not have sufficient verified information to answer this question. Do NOT fabricate, and do NOT ask for clarification since the question is unambiguous."
                )
                return CAPSResult(
                    act=CommunicativeAct.REFUSE,
                    semantic_graph=None,
                    epistemic_metadata=EpistemicMetadata(status=EpistemicState.UNKNOWN, confidence=None, is_grounded=False),
                    provenance_metadata=ProvenanceMetadata(origin="UNGROUNDED_INQUIRY", session_id=session_id),
                    resolution_metadata=ResolutionAdmissibilityMetadata(
                        resolution_status=dialogue_ctx.resolution_status,
                        grounding_status="UNGROUNDED",
                        failure_reason="Factual inquiry lacks verified grounding in knowledge base or life-state.",
                    ),
                    grounded=False,
                    directives=dir_msg,
                )

    # 6.3 Conversational Statements (ACKNOWLEDGE with preserved semantic context)
    encounter_cues = (
        "gặp em", "gặp nhau", "gặp được", "cuối cùng cũng", "finally met", "finally meet",
        "nice to meet", "gặp lại", "mới gặp", "hello", "xin chào", "chào em", "chào bạn",
        "hi lucia", "hey lucia", "good morning", "good afternoon", "good evening",
    )
    if any(cue in input_lower for cue in encounter_cues):
        return CAPSResult(
            act=CommunicativeAct.ACKNOWLEDGE,
            semantic_graph=None,
            epistemic_metadata=EpistemicMetadata(status=EpistemicState.FACT, is_grounded=False),
            provenance_metadata=ProvenanceMetadata(origin="CONVERSATIONAL_ENCOUNTER", session_id=session_id),
            resolution_metadata=ResolutionAdmissibilityMetadata(
                resolution_status=dialogue_ctx.resolution_status,
                grounding_status="CONVERSATIONAL_CONTEXT",
            ),
            grounded=False,
            target_predicate="c:ENCOUNTER",
            focus_argument="ent:lucia",
            pragmatic_stance=PragmaticStance.GREET_AND_MEET,
            conversational_obligation="MUTUAL_ENCOUNTER_ACKNOWLEDGMENT",
            directives="Đáp lại lời chào gặp gỡ một cách nhã nhặn, tự nhiên; ghi nhận khoảnh khắc gặp gỡ để bắt đầu cuộc trò chuyện và lắng nghe chia sẻ.",
        )

    # Hesitation & Floor-Yielding Cues (User yields the floor or expresses conversational hesitation)
    hesitation_cues = (
        "chẳng biết phải nói gì", "không biết phải nói gì", "chẳng biết nói gì", "không biết nói gì",
        "chưa biết nói gì", "chưa biết phải nói gì", "biết nói gì đây", "biết nói gì bây giờ",
        "don't know what to say", "not sure what to say", "lost for words", "speechless",
        "ngại quá", "hơi ngại", "lúng túng", "ngập ngừng",
    )
    if any(cue in input_lower for cue in hesitation_cues):
        return CAPSResult(
            act=CommunicativeAct.ACKNOWLEDGE,
            semantic_graph=None,
            epistemic_metadata=EpistemicMetadata(status=EpistemicState.FACT, is_grounded=False),
            provenance_metadata=ProvenanceMetadata(origin="CONVERSATIONAL_HESITATION", session_id=session_id),
            resolution_metadata=ResolutionAdmissibilityMetadata(
                resolution_status=dialogue_ctx.resolution_status,
                grounding_status="CONVERSATIONAL_CONTEXT",
            ),
            grounded=False,
            target_predicate="c:CONVERSATIONAL_HESITATION",
            focus_argument="ent:dialogue",
            pragmatic_stance=PragmaticStance.FLOOR_YIELD,
            conversational_obligation="REASSURE_AND_GENTLE_INITIATIVE",
            directives="Nhẹ nhàng trấn an sự ngập ngừng của người dùng và chủ động mở ra một hướng gợi mở tự nhiên, không phán xét, không áp lực.",
        )

    activity_cues = ("đi làm", "đi học", "mệt", "vừa mới", "đang đọc", "đi dạo", "nghỉ ngơi", "làm việc", "walk", "tired")
    if any(cue in input_lower for cue in activity_cues):
        return CAPSResult(
            act=CommunicativeAct.ACKNOWLEDGE,
            semantic_graph=None,
            epistemic_metadata=EpistemicMetadata(status=EpistemicState.FACT, is_grounded=False),
            provenance_metadata=ProvenanceMetadata(origin="CONVERSATIONAL_SHARING", session_id=session_id),
            resolution_metadata=ResolutionAdmissibilityMetadata(
                resolution_status=dialogue_ctx.resolution_status,
                grounding_status="CONVERSATIONAL_CONTEXT",
            ),
            grounded=False,
            target_predicate="c:USER_SHARING",
            focus_argument="ent:user",
            pragmatic_stance=PragmaticStance.SHARING,
            conversational_obligation="ATTENTIVE_LISTENING",
            directives="Acknowledge user sharing attentively with calm listening engagement.",
        )

    # Default conversational flow acknowledgment: preserve semantic context without empathy coaching
    return CAPSResult(
        act=CommunicativeAct.ACKNOWLEDGE,
        semantic_graph=None,
        epistemic_metadata=EpistemicMetadata(status=EpistemicState.FACT, is_grounded=False),
        provenance_metadata=ProvenanceMetadata(origin="CONVERSATIONAL_FLOW", session_id=session_id),
        resolution_metadata=ResolutionAdmissibilityMetadata(
            resolution_status=dialogue_ctx.resolution_status,
            grounding_status="CONVERSATIONAL_CONTEXT",
        ),
        grounded=False,
        pragmatic_stance=PragmaticStance.NEUTRAL,
        conversational_obligation="ATTENTIVE_LISTENING",
        directives="Acknowledge user input attentively with calm listening engagement.",
    )

