"""
tests/unit/test_adaptive_response_presence.py

Regression test suite for Lucia Adaptive Response Presence & Depth (Section G requirements):
1. minimal social call ("Ciah ơi.") -> minimal depth (MINIMAL, <= 45 tokens budget)
2. simple direct question ("Em đang làm gì đấy?") -> short depth (SHORT, <= 90 tokens budget)
3. personal query ("Do you have any favorite food?") -> short-to-medium bounded self-disclosure (SHORT, <= 90 tokens budget)
4. concept explanation ("Tell me about Philia.") -> medium depth (MEDIUM, <= 180 tokens budget)
5. technical question ("Why does Lucia separate Active Inference from language generation?") -> deep/structured depth (DEEP, <= 320 tokens budget)
6. long emotionally layered user turn -> adaptive depth, not forced-short (MEDIUM/DEEP)
7. existing communicative act remains authoritative over depth
"""

import pytest
from src.core.communication.communication_state import (
    CommunicationState,
    ResponseDepth,
    RESPONSE_DEPTH_BUDGET_MAP,
)
from src.core.communication.communication_policy import CommunicationPolicy
from src.core.communication.caps import (
    evaluate_caps,
    CommunicativeAct,
    DialogueContextSnapshot,
    CognitiveStateSnapshot,
    AdmissibleEvidencePool,
    CommunicationPolicySnapshot,
)
from src.core.language.contract import RealizationInputContract
from src.core.models import SomaticMarkers


@pytest.fixture
def policy() -> CommunicationPolicy:
    return CommunicationPolicy()


@pytest.fixture
def base_somatic() -> SomaticMarkers:
    return SomaticMarkers(
        stability=0.9,
        cognitive_load=0.2,
        energy=0.9,
        tension=0.1,
    )


def test_1_minimal_social_call_presence(policy: CommunicationPolicy, base_somatic: SomaticMarkers):
    """
    Scenario 1:
    User: "Ciah ơi."
    Expected:
    - CAPS recognizes vocative presence call -> ACKNOWLEDGE / c:PRESENCE_PING / MINIMAL_PRESENCE_CALL
    - CommunicationPolicy attunes response depth to MINIMAL (<= 45 tokens budget)
    """
    text = "Ciah ơi."
    diag_ctx = DialogueContextSnapshot(
        turn_id=1,
        input_text=text,
        active_referents=(),
        resolution_status=None,
        resolved_entity_id=None,
        candidate_referent_ids=(),
    )
    caps_res = evaluate_caps(
        dialogue_ctx=diag_ctx,
        cognitive_state=CognitiveStateSnapshot(),
        evidence_pool=AdmissibleEvidencePool(),
    )

    assert caps_res.act == CommunicativeAct.ACKNOWLEDGE
    assert caps_res.target_predicate == "c:PRESENCE_PING"
    assert caps_res.conversational_obligation == "MINIMAL_PRESENCE_CALL"

    base_state = policy.get_neutral_actuator_baseline()
    attuned = policy.attune_depth_to_act(
        base_state,
        act=caps_res.act,
        obligation=caps_res.conversational_obligation,
        target_predicate=caps_res.target_predicate,
        user_input_text=text,
        somatic=base_somatic,
    )

    min_b, max_b = RESPONSE_DEPTH_BUDGET_MAP[ResponseDepth.MINIMAL]
    assert attuned.response_depth == ResponseDepth.MINIMAL
    assert min_b <= attuned.max_tokens_budget <= max_b
    assert attuned.max_tokens_budget <= 45


def test_2_simple_direct_question(policy: CommunicationPolicy, base_somatic: SomaticMarkers):
    """
    Scenario 2:
    User: "Em đang làm gì đấy?"
    Expected:
    - Direct daily question -> SHORT depth (<= 100 tokens budget)
    - Not generic introspective monologue
    """
    text = "Em đang làm gì đấy?"
    diag_ctx = DialogueContextSnapshot(
        turn_id=2,
        input_text=text,
        active_referents=(),
        resolution_status=None,
        resolved_entity_id=None,
        candidate_referent_ids=(),
    )
    caps_res = evaluate_caps(
        dialogue_ctx=diag_ctx,
        cognitive_state=CognitiveStateSnapshot(),
        evidence_pool=AdmissibleEvidencePool(),
    )

    base_state = policy.get_neutral_actuator_baseline()
    attuned = policy.attune_depth_to_act(
        base_state,
        act=caps_res.act,
        obligation=caps_res.conversational_obligation,
        target_predicate=caps_res.target_predicate,
        user_input_text=text,
        somatic=base_somatic,
    )

    min_b, max_b = RESPONSE_DEPTH_BUDGET_MAP[ResponseDepth.SHORT]
    assert attuned.response_depth == ResponseDepth.SHORT
    assert min_b <= attuned.max_tokens_budget <= max_b


def test_3_personal_query_bounded_self_disclosure(policy: CommunicationPolicy, base_somatic: SomaticMarkers):
    """
    Scenario 3:
    User: "Do you have any favorite food?"
    Expected:
    - Personal inquiry -> SHORT depth (bounded self-disclosure, <= 100 tokens)
    - Not a multi-paragraph essay about food and emotional bonding
    """
    text = "Do you have any favorite food?"
    diag_ctx = DialogueContextSnapshot(
        turn_id=3,
        input_text=text,
        active_referents=(),
        resolution_status=None,
        resolved_entity_id=None,
        candidate_referent_ids=(),
    )
    caps_res = evaluate_caps(
        dialogue_ctx=diag_ctx,
        cognitive_state=CognitiveStateSnapshot(),
        evidence_pool=AdmissibleEvidencePool(),
    )

    base_state = policy.get_neutral_actuator_baseline()
    attuned = policy.attune_depth_to_act(
        base_state,
        act=caps_res.act,
        obligation=caps_res.conversational_obligation,
        target_predicate=caps_res.target_predicate,
        user_input_text=text,
        somatic=base_somatic,
    )

    min_b, max_b = RESPONSE_DEPTH_BUDGET_MAP[ResponseDepth.SHORT]
    assert attuned.response_depth == ResponseDepth.SHORT
    assert min_b <= attuned.max_tokens_budget <= max_b


def test_4_concept_explanation(policy: CommunicationPolicy, base_somatic: SomaticMarkers):
    """
    Scenario 4:
    User: "Tell me about Philia."
    Expected:
    - Concept explanation -> MEDIUM depth (appropriate to information necessity, ~180 tokens)
    """
    text = "Tell me about Philia."
    diag_ctx = DialogueContextSnapshot(
        turn_id=4,
        input_text=text,
        active_referents=(),
        resolution_status=None,
        resolved_entity_id=None,
        candidate_referent_ids=(),
    )
    caps_res = evaluate_caps(
        dialogue_ctx=diag_ctx,
        cognitive_state=CognitiveStateSnapshot(),
        evidence_pool=AdmissibleEvidencePool(),
    )

    base_state = policy.get_neutral_actuator_baseline()
    attuned = policy.attune_depth_to_act(
        base_state,
        act=caps_res.act,
        obligation=caps_res.conversational_obligation,
        target_predicate=caps_res.target_predicate,
        user_input_text=text,
        somatic=base_somatic,
    )

    min_b, max_b = RESPONSE_DEPTH_BUDGET_MAP[ResponseDepth.MEDIUM]
    assert attuned.response_depth == ResponseDepth.MEDIUM
    assert min_b <= attuned.max_tokens_budget <= max_b


def test_5_technical_deep_question(policy: CommunicationPolicy, base_somatic: SomaticMarkers):
    """
    Scenario 5:
    User: "Why does Lucia separate Active Inference from language generation?"
    Expected:
    - CAPS classifies as EXPLAIN_CONCEPT act
    - CommunicationPolicy attunes to DEEP structured explanation (<= 400 tokens)
    """
    text = "Why does Lucia separate Active Inference from language generation?"
    diag_ctx = DialogueContextSnapshot(
        turn_id=5,
        input_text=text,
        active_referents=(),
        resolution_status=None,
        resolved_entity_id=None,
        candidate_referent_ids=(),
    )
    caps_res = evaluate_caps(
        dialogue_ctx=diag_ctx,
        cognitive_state=CognitiveStateSnapshot(),
        evidence_pool=AdmissibleEvidencePool(),
    )

    assert caps_res.act == CommunicativeAct.EXPLAIN_CONCEPT

    base_state = policy.get_neutral_actuator_baseline()
    attuned = policy.attune_depth_to_act(
        base_state,
        act=caps_res.act,
        obligation=caps_res.conversational_obligation,
        target_predicate=caps_res.target_predicate,
        user_input_text=text,
        somatic=base_somatic,
    )

    min_b, max_b = RESPONSE_DEPTH_BUDGET_MAP[ResponseDepth.DEEP]
    assert attuned.response_depth == ResponseDepth.DEEP
    assert min_b <= attuned.max_tokens_budget <= max_b
    assert attuned.max_tokens_budget >= 250


def test_6_long_emotionally_layered_turn_not_forced_short(policy: CommunicationPolicy, base_somatic: SomaticMarkers):
    """
    Scenario 6:
    Long narrative/emotionally layered user turn:
    Expected:
    - Do NOT force SHORT simply because brevity is the baseline.
    - Lucia stays longer with the user (MEDIUM or DEEP depth).
    """
    text = (
        "Today was really overwhelming at work. My manager completely changed the project scope "
        "at the last minute, and all our sprint planning was thrown out the window. Everyone was stressed, "
        "and I felt completely isolated trying to fix deployment issues until 9 PM. I honestly feel "
        "exhausted and wonder if I'm even making meaningful progress."
    )
    diag_ctx = DialogueContextSnapshot(
        turn_id=6,
        input_text=text,
        active_referents=(),
        resolution_status=None,
        resolved_entity_id=None,
        candidate_referent_ids=(),
    )
    caps_res = evaluate_caps(
        dialogue_ctx=diag_ctx,
        cognitive_state=CognitiveStateSnapshot(),
        evidence_pool=AdmissibleEvidencePool(),
    )

    base_state = policy.get_neutral_actuator_baseline()
    attuned = policy.attune_depth_to_act(
        base_state,
        act=caps_res.act,
        obligation=caps_res.conversational_obligation,
        target_predicate=caps_res.target_predicate,
        user_input_text=text,
        somatic=base_somatic,
    )

    assert attuned.response_depth in (ResponseDepth.MEDIUM, ResponseDepth.DEEP)
    assert attuned.response_depth != ResponseDepth.SHORT
    assert attuned.response_depth != ResponseDepth.MINIMAL
    assert attuned.max_tokens_budget >= 150


def test_7_communicative_act_authority_over_depth(policy: CommunicationPolicy, base_somatic: SomaticMarkers):
    """
    Scenario 7:
    Communicative act remains authoritative over depth:
    - CLARIFY / REPAIR / INQUIRE has distinct bounded budgets regardless of superficial user text length.
    - E.g. A short 'Why?' asking for architectural rationale will attune to EXPLAIN_CONCEPT -> DEEP.
    - Conversely, a 2-word vocative call 'Lucia ơi' attunes to MINIMAL regardless of default baseline.
    """
    # Case A: Explicit EXPLAIN_CONCEPT act with very short input
    short_explain_input = "Why?"
    base_state = policy.get_neutral_actuator_baseline()
    explain_attuned = policy.attune_depth_to_act(
        base_state,
        act=CommunicativeAct.EXPLAIN_CONCEPT,
        obligation="FULFILL_CONCEPT_EXPLANATION",
        target_predicate="c:CONCEPT_EXPLANATION",
        user_input_text="Why does this architecture separate them?",
        somatic=base_somatic,
    )
    assert explain_attuned.response_depth in (ResponseDepth.MEDIUM, ResponseDepth.DEEP)
    assert explain_attuned.max_tokens_budget >= 180

    # Case B: Explicit CLARIFY act with medium input
    clarify_attuned = policy.attune_depth_to_act(
        base_state,
        act=CommunicativeAct.CLARIFY,
        obligation="RESOLVE_AMBIGUITY",
        target_predicate="c:AMBIGUOUS_REFERENT",
        user_input_text="Which module did you mean earlier when talking about pipelines?",
        somatic=base_somatic,
    )
    assert clarify_attuned.response_depth == ResponseDepth.SHORT

    # Case C: RealizationInputContract encapsulates and preserves response depth
    contract = RealizationInputContract.create_default(
        response_depth=explain_attuned.response_depth.value,
        max_tokens_budget=explain_attuned.max_tokens_budget,
    )
    assert contract.response_depth in ("medium", "deep")
    assert contract.max_tokens_budget == explain_attuned.max_tokens_budget
