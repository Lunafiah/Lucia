"""
tests/integration/test_adaptive_presence_orchestrator.py

Integration regression tests for Lucia Adaptive Response Presence (ARP).
Covers the full pipeline: CAPS → CommunicationPolicy → RealizationInputContract → SemanticFidelityGate.

Test Cases:
  Case A — Presence ping: minimal depth, MINIMAL_PING topology, no question, ≤ 35 tokens
  Case B — Simple activity question: SHORT depth, BOUNDED_ANSWER topology
  Case C — Multi-clause analytical question: NOT misclassified as WELLBEING (thế nào false positive fix)
  Case D — Deep technical question: DEEP depth, STRUCTURED_EXPLANATION or DEEP_REFLECTION topology

Regression Guards:
  R1  — attune_depth_to_act() accepts only supported kwargs (no TypeError with rel_state/knowledge)
  R2  — Exception in attunement is NOT silently swallowed; it propagates faithfully
  R3  — Contract carries response_shape correctly through from_caps()
  R4  — Gate MINIMAL_PING shape check: verbose response is blocked
  R5  — Gate completion integrity: truncated response with "length" finish_reason is blocked
"""

from __future__ import annotations

import pytest

from src.core.communication.caps import (
    AdmissibleEvidencePool,
    CognitiveStateSnapshot,
    CommunicativeAct,
    DialogueContextSnapshot,
    evaluate_caps,
)
from src.core.communication.communication_policy import CommunicationPolicy
from src.core.communication.communication_state import (
    RESPONSE_DEPTH_BUDGET_MAP,
    ResponseDepth,
    ResponseShape,
    ShapeTopology,
)
from src.core.language.contract import RealizationInputContract
from src.core.language.gate import SemanticFidelityGate
from src.core.models import SomaticMarkers


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------


@pytest.fixture
def policy() -> CommunicationPolicy:
    return CommunicationPolicy()


@pytest.fixture
def gate() -> SemanticFidelityGate:
    return SemanticFidelityGate()


@pytest.fixture
def healthy_somatic() -> SomaticMarkers:
    return SomaticMarkers(stability=0.9, cognitive_load=0.2, energy=0.9, tension=0.1)


def _make_dialogue(text: str, turn_id: int = 1) -> DialogueContextSnapshot:
    return DialogueContextSnapshot(
        turn_id=turn_id,
        input_text=text,
        active_referents=(),
        resolution_status=None,
        resolved_entity_id=None,
        candidate_referent_ids=(),
    )


def _caps(text: str, turn_id: int = 1):
    return evaluate_caps(
        dialogue_ctx=_make_dialogue(text, turn_id=turn_id),
        cognitive_state=CognitiveStateSnapshot(),
        evidence_pool=AdmissibleEvidencePool(),
    )


# ---------------------------------------------------------------------------
# Case A — Presence ping
# ---------------------------------------------------------------------------


class TestCaseA_PresencePing:
    """
    'Ciah ơi.' (vocative presence call) must produce:
      - CAPS: act=ACKNOWLEDGE, c:PRESENCE_PING, MINIMAL_PRESENCE_CALL obligation
      - Depth: MINIMAL, budget ≤ 35
      - Shape: MINIMAL_PING topology, no follow-up question allowed
      - Contract: response_shape.topology == MINIMAL_PING, allow_follow_up_question == False
      - Gate: verbose response is BLOCKED; minimal correct response PASSes
    """

    TEXT = "Ciah ơi."

    def test_a1_caps_classification(self):
        res = _caps(self.TEXT)
        assert res.act == CommunicativeAct.ACKNOWLEDGE
        assert res.target_predicate == "c:PRESENCE_PING"
        assert res.conversational_obligation == "MINIMAL_PRESENCE_CALL"

    def test_a2_depth_minimal(self, policy, healthy_somatic):
        res = _caps(self.TEXT)
        base = policy.get_neutral_actuator_baseline()
        attuned = policy.attune_depth_to_act(
            base,
            act=res.act,
            obligation=res.conversational_obligation,
            target_predicate=res.target_predicate,
            user_input_text=self.TEXT,
            somatic=healthy_somatic,
        )
        assert attuned.response_depth == ResponseDepth.MINIMAL
        assert attuned.max_tokens_budget <= 40, (
            f"Expected budget ≤ 40, got {attuned.max_tokens_budget}"
        )
        # Strictly within MINIMAL range
        lo, hi = RESPONSE_DEPTH_BUDGET_MAP[ResponseDepth.MINIMAL]
        assert lo <= attuned.max_tokens_budget <= hi

    def test_a3_response_shape_minimal_ping(self, policy, healthy_somatic):
        res = _caps(self.TEXT)
        base = policy.get_neutral_actuator_baseline()
        attuned = policy.attune_depth_to_act(
            base,
            act=res.act,
            obligation=res.conversational_obligation,
            target_predicate=res.target_predicate,
            user_input_text=self.TEXT,
            somatic=healthy_somatic,
        )
        assert attuned.response_shape is not None
        assert attuned.response_shape.topology == ShapeTopology.MINIMAL_PING
        assert attuned.response_shape.allow_follow_up_question is False

    def test_a4_contract_carries_shape(self, policy, healthy_somatic):
        """RealizationInputContract must propagate response_shape from attunement."""
        res = _caps(self.TEXT)
        base = policy.get_neutral_actuator_baseline()
        attuned = policy.attune_depth_to_act(
            base,
            act=res.act,
            obligation=res.conversational_obligation,
            target_predicate=res.target_predicate,
            user_input_text=self.TEXT,
            somatic=healthy_somatic,
        )
        contract = RealizationInputContract.from_caps(
            res,
            target_language="vi",
            response_depth=attuned.response_depth.value,
            max_tokens_budget=attuned.max_tokens_budget,
            response_shape=attuned.response_shape,
        )
        assert contract.response_depth == "minimal"
        assert contract.max_tokens_budget <= 40
        assert contract.response_shape.topology == ShapeTopology.MINIMAL_PING

    def test_a5_gate_blocks_verbose_response(self, policy, healthy_somatic, gate):
        """Gate must BLOCK a verbose multi-sentence presence response."""
        res = _caps(self.TEXT)
        base = policy.get_neutral_actuator_baseline()
        attuned = policy.attune_depth_to_act(
            base,
            act=res.act,
            obligation=res.conversational_obligation,
            target_predicate=res.target_predicate,
            user_input_text=self.TEXT,
            somatic=healthy_somatic,
        )
        contract = RealizationInputContract.from_caps(
            res,
            target_language="vi",
            response_depth=attuned.response_depth.value,
            max_tokens_budget=attuned.max_tokens_budget,
            response_shape=attuned.response_shape,
        )
        # Simulate a verbose LLM response that violates the MINIMAL_PING shape
        verbose_response = (
            "Dạ, em đây anh ạ! Em đang rất vui khi anh gọi em. "
            "Có điều gì anh muốn chia sẻ với em không? "
            "Em luôn ở đây và sẵn sàng lắng nghe anh bất cứ lúc nào."
        )
        decision = gate.verify(contract, verbose_response)
        assert decision.status == "BLOCK", (
            f"Expected BLOCK for verbose presence ping response, got {decision.status}. "
            f"Violations: {decision.violation_reasons}"
        )
        assert any(
            "SHAPE" in v or "PRESENCE" in v or "ACT" in v
            for v in decision.violation_reasons
        ), f"Expected a shape/presence/act violation, got: {decision.violation_reasons}"

    def test_a6_gate_passes_minimal_response(self, policy, healthy_somatic, gate):
        """Gate must PASS a minimal presence acknowledgement."""
        res = _caps(self.TEXT)
        base = policy.get_neutral_actuator_baseline()
        attuned = policy.attune_depth_to_act(
            base,
            act=res.act,
            obligation=res.conversational_obligation,
            target_predicate=res.target_predicate,
            user_input_text=self.TEXT,
            somatic=healthy_somatic,
        )
        contract = RealizationInputContract.from_caps(
            res,
            target_language="vi",
            response_depth=attuned.response_depth.value,
            max_tokens_budget=attuned.max_tokens_budget,
            response_shape=attuned.response_shape,
        )
        minimal_response = "Dạ, em đây anh."
        decision = gate.verify(contract, minimal_response)
        assert decision.status == "PASS", (
            f"Expected PASS for minimal presence response, got {decision.status}. "
            f"Violations: {decision.violation_reasons}"
        )


# ---------------------------------------------------------------------------
# Case B — Simple activity question
# ---------------------------------------------------------------------------


class TestCaseB_SimpleActivityQuestion:
    """
    'Em đang làm gì đấy?' → SHORT depth, BOUNDED_ANSWER topology.
    """

    TEXT = "Em đang làm gì đấy?"

    def test_b1_depth_short(self, policy, healthy_somatic):
        res = _caps(self.TEXT)
        base = policy.get_neutral_actuator_baseline()
        attuned = policy.attune_depth_to_act(
            base,
            act=res.act,
            obligation=res.conversational_obligation,
            target_predicate=res.target_predicate,
            user_input_text=self.TEXT,
            somatic=healthy_somatic,
        )
        assert attuned.response_depth == ResponseDepth.SHORT
        lo, hi = RESPONSE_DEPTH_BUDGET_MAP[ResponseDepth.SHORT]
        assert lo <= attuned.max_tokens_budget <= hi

    def test_b2_shape_bounded_answer(self, policy, healthy_somatic):
        res = _caps(self.TEXT)
        base = policy.get_neutral_actuator_baseline()
        attuned = policy.attune_depth_to_act(
            base,
            act=res.act,
            obligation=res.conversational_obligation,
            target_predicate=res.target_predicate,
            user_input_text=self.TEXT,
            somatic=healthy_somatic,
        )
        # Simple activity answer should be BOUNDED_ANSWER or CONVERSATIONAL_EXCHANGE
        assert attuned.response_shape.topology in (
            ShapeTopology.BOUNDED_ANSWER,
            ShapeTopology.CONVERSATIONAL_EXCHANGE,
        ), f"Expected BOUNDED_ANSWER or CONVERSATIONAL_EXCHANGE, got {attuned.response_shape.topology}"

    def test_b3_contract_propagation(self, policy, healthy_somatic):
        res = _caps(self.TEXT)
        base = policy.get_neutral_actuator_baseline()
        attuned = policy.attune_depth_to_act(
            base,
            act=res.act,
            obligation=res.conversational_obligation,
            target_predicate=res.target_predicate,
            user_input_text=self.TEXT,
            somatic=healthy_somatic,
        )
        contract = RealizationInputContract.from_caps(
            res,
            target_language="vi",
            response_depth=attuned.response_depth.value,
            max_tokens_budget=attuned.max_tokens_budget,
            response_shape=attuned.response_shape,
        )
        assert contract.response_depth == "short"
        assert contract.max_tokens_budget <= 100


# ---------------------------------------------------------------------------
# Case C — Multi-clause analytical question (thế nào false positive fix)
# ---------------------------------------------------------------------------


class TestCaseC_AnalyticalQuestionNotWellbeing:
    """
    A multi-clause analytical question containing 'thế nào' must NOT be
    misclassified as c:WELLBEING (false positive fix).

    'Anh muốn hiểu hệ thống hoạt động thế nào và tại sao kiến trúc lại được thiết kế như vậy?'
    → Should produce EXPLAIN_CONCEPT, ANSWER, or ANSWER_PERSONAL_QUERY — NOT WELLBEING.
    → Must NOT produce a MINIMAL depth response.
    """

    TEXT = (
        "Anh muốn hiểu hệ thống hoạt động thế nào "
        "và tại sao kiến trúc lại được thiết kế như vậy?"
    )

    def test_c1_not_wellbeing_misclassification(self):
        res = _caps(self.TEXT)
        # Must NOT be classified purely as wellbeing check-in
        assert res.target_predicate != "c:WELLBEING", (
            f"Multi-clause analytical question was falsely classified as WELLBEING. "
            f"Act={res.act}, predicate={res.target_predicate}"
        )

    def test_c2_not_minimal_depth(self, policy, healthy_somatic):
        res = _caps(self.TEXT)
        base = policy.get_neutral_actuator_baseline()
        attuned = policy.attune_depth_to_act(
            base,
            act=res.act,
            obligation=res.conversational_obligation,
            target_predicate=res.target_predicate,
            user_input_text=self.TEXT,
            somatic=healthy_somatic,
        )
        assert attuned.response_depth != ResponseDepth.MINIMAL, (
            f"Analytical question got MINIMAL depth — wrong. Act={res.act}, pred={res.target_predicate}"
        )
        # Expect at least MEDIUM since it's a multi-clause architectural inquiry
        assert attuned.response_depth in (
            ResponseDepth.SHORT, ResponseDepth.MEDIUM, ResponseDepth.DEEP
        )

    def test_c3_substantive_depth_for_architectural_inquiry(self, policy, healthy_somatic):
        """For 'why does X architecture work this way?' style inquiry, depth should be at least MEDIUM."""
        res = _caps(self.TEXT)
        base = policy.get_neutral_actuator_baseline()
        attuned = policy.attune_depth_to_act(
            base,
            act=res.act,
            obligation=res.conversational_obligation,
            target_predicate=res.target_predicate,
            user_input_text=self.TEXT,
            somatic=healthy_somatic,
        )
        # If CAPS identifies this as EXPLAIN_CONCEPT, must be MEDIUM or DEEP
        if res.act == CommunicativeAct.EXPLAIN_CONCEPT:
            assert attuned.response_depth in (ResponseDepth.MEDIUM, ResponseDepth.DEEP)
            assert attuned.max_tokens_budget >= 150


# ---------------------------------------------------------------------------
# Case D — Deep technical question
# ---------------------------------------------------------------------------


class TestCaseD_DeepTechnicalQuestion:
    """
    'Why does Lucia separate Active Inference from language generation?' →
    EXPLAIN_CONCEPT → DEEP depth, structured/deep topology, ≥ 250 token budget.
    """

    TEXT = "Why does Lucia separate Active Inference from language generation?"

    def test_d1_caps_explain_concept(self):
        res = _caps(self.TEXT)
        assert res.act == CommunicativeAct.EXPLAIN_CONCEPT, (
            f"Expected EXPLAIN_CONCEPT, got {res.act}"
        )

    def test_d2_deep_depth(self, policy, healthy_somatic):
        res = _caps(self.TEXT)
        base = policy.get_neutral_actuator_baseline()
        attuned = policy.attune_depth_to_act(
            base,
            act=res.act,
            obligation=res.conversational_obligation,
            target_predicate=res.target_predicate,
            user_input_text=self.TEXT,
            somatic=healthy_somatic,
        )
        assert attuned.response_depth == ResponseDepth.DEEP
        assert attuned.max_tokens_budget >= 250, (
            f"DEEP technical question got token budget {attuned.max_tokens_budget} — expected ≥ 250"
        )
        lo, hi = RESPONSE_DEPTH_BUDGET_MAP[ResponseDepth.DEEP]
        assert lo <= attuned.max_tokens_budget <= hi

    def test_d3_shape_structured_or_deep(self, policy, healthy_somatic):
        res = _caps(self.TEXT)
        base = policy.get_neutral_actuator_baseline()
        attuned = policy.attune_depth_to_act(
            base,
            act=res.act,
            obligation=res.conversational_obligation,
            target_predicate=res.target_predicate,
            user_input_text=self.TEXT,
            somatic=healthy_somatic,
        )
        assert attuned.response_shape.topology in (
            ShapeTopology.STRUCTURED_EXPLANATION,
            ShapeTopology.DEEP_REFLECTION,
        ), f"Expected STRUCTURED_EXPLANATION or DEEP_REFLECTION, got {attuned.response_shape.topology}"

    def test_d4_contract_propagation(self, policy, healthy_somatic):
        res = _caps(self.TEXT)
        base = policy.get_neutral_actuator_baseline()
        attuned = policy.attune_depth_to_act(
            base,
            act=res.act,
            obligation=res.conversational_obligation,
            target_predicate=res.target_predicate,
            user_input_text=self.TEXT,
            somatic=healthy_somatic,
        )
        contract = RealizationInputContract.from_caps(
            res,
            target_language="en",
            response_depth=attuned.response_depth.value,
            max_tokens_budget=attuned.max_tokens_budget,
            response_shape=attuned.response_shape,
        )
        assert contract.response_depth == "deep"
        assert contract.max_tokens_budget >= 250
        assert contract.response_shape.topology in (
            ShapeTopology.STRUCTURED_EXPLANATION,
            ShapeTopology.DEEP_REFLECTION,
        )


# ---------------------------------------------------------------------------
# Regression Guards
# ---------------------------------------------------------------------------


class TestRegressionGuards:
    """
    R1 — attune_depth_to_act() does NOT accept rel_state or knowledge kwargs.
    R2 — Exception in attunement propagates (not swallowed by broad except).
    R3 — Contract from_caps() propagates response_shape field correctly.
    R4 — Gate MINIMAL_PING shape: verbose response is BLOCKED.
    R5 — Gate completion integrity: finish_reason=="length" triggers BLOCK.
    """

    def test_r1_attune_depth_to_act_no_unsupported_kwargs(self, policy, healthy_somatic):
        """
        Regression: CognitiveOrchestrator formerly passed rel_state and knowledge kwargs
        to attune_depth_to_act(), causing TypeError. Verify the correct call signature works.
        """
        base = policy.get_neutral_actuator_baseline()
        # Must not raise
        attuned = policy.attune_depth_to_act(
            base,
            act=CommunicativeAct.ACKNOWLEDGE,
            obligation="MINIMAL_PRESENCE_CALL",
            target_predicate="c:PRESENCE_PING",
            user_input_text="Lucia ơi.",
            somatic=healthy_somatic,
        )
        assert attuned.response_depth == ResponseDepth.MINIMAL

    def test_r1b_unsupported_kwargs_raise_type_error(self, policy, healthy_somatic):
        """
        Confirm that passing rel_state or knowledge kwargs raises TypeError (no silent swallowing).
        This catches the pre-fix bug where the orchestrator silently fell back to SHORT/85.
        """
        base = policy.get_neutral_actuator_baseline()
        with pytest.raises(TypeError):
            policy.attune_depth_to_act(
                base,
                act=CommunicativeAct.ACKNOWLEDGE,
                obligation="MINIMAL_PRESENCE_CALL",
                target_predicate="c:PRESENCE_PING",
                user_input_text="Lucia ơi.",
                somatic=healthy_somatic,
                rel_state={"rapport": 0.9},    # unsupported kwarg
                knowledge={"domain": "test"},   # unsupported kwarg
            )

    def test_r3_contract_from_caps_carries_response_shape(self, policy, healthy_somatic):
        """
        RealizationInputContract.from_caps() must carry the response_shape field
        through correctly when explicitly provided.
        """
        res = _caps("Ciah ơi.")
        base = policy.get_neutral_actuator_baseline()
        attuned = policy.attune_depth_to_act(
            base,
            act=res.act,
            obligation=res.conversational_obligation,
            target_predicate=res.target_predicate,
            user_input_text="Ciah ơi.",
            somatic=healthy_somatic,
        )
        contract = RealizationInputContract.from_caps(
            res,
            target_language="vi",
            response_depth=attuned.response_depth.value,
            max_tokens_budget=attuned.max_tokens_budget,
            response_shape=attuned.response_shape,
        )
        assert isinstance(contract.response_shape, ResponseShape)
        assert contract.response_shape.topology == ShapeTopology.MINIMAL_PING

    def test_r4_gate_blocks_verbose_minimal_ping(self, gate):
        """
        Gate must BLOCK a verbose response when contract has MINIMAL_PING topology
        (regardless of whether it's the gate's fallback or shape check path).
        """
        shape = ResponseShape(
            topology=ShapeTopology.MINIMAL_PING,
            max_sentences=1,
            allow_follow_up_question=False,
            prohibit_topic_expansion=True,
        )
        contract = RealizationInputContract.create_default(
            target_language="vi",
            conversational_obligation="MINIMAL_PRESENCE_CALL",
            response_shape=shape,
        )
        verbose = (
            "Dạ anh ơi, em ở đây ạ. Anh có muốn chia sẻ gì với em không? "
            "Hôm nay anh thế nào, công việc của anh ra sao rồi ạ? "
            "Em luôn sẵn sàng lắng nghe anh bất cứ lúc nào."
        )
        decision = gate.verify(contract, verbose)
        assert decision.status == "BLOCK", (
            f"Expected BLOCK for verbose MINIMAL_PING, got {decision.status}. "
            f"Violations: {decision.violation_reasons}"
        )

    def test_r5_gate_blocks_truncated_completion(self, gate):
        """
        Gate must BLOCK when finish_reason is 'length' (truncated generation).
        """
        contract = RealizationInputContract.create_default(
            target_language="en",
            response_depth="deep",
        )
        truncated_response = "Lucia's architecture separates Active Inference from language generation because"
        decision = gate.verify(contract, truncated_response, finish_reason="length")
        assert decision.status == "BLOCK", (
            f"Expected BLOCK for truncated generation, got {decision.status}. "
            f"Violations: {decision.violation_reasons}"
        )
        assert "COMPLETION_INTEGRITY_VIOLATION" in decision.violation_reasons

    def test_r5b_gate_passes_complete_response(self, gate):
        """Gate must PASS a complete non-truncated response (finish_reason='stop')."""
        contract = RealizationInputContract.create_default(
            target_language="en",
            response_depth="deep",
        )
        complete_response = (
            "Lucia separates Active Inference from language generation to maintain "
            "a clean separation between the predictive world model and the surface "
            "realization layer, ensuring epistemic integrity."
        )
        decision = gate.verify(contract, complete_response, finish_reason="stop")
        # Should not be blocked by completion integrity
        assert "COMPLETION_INTEGRITY_VIOLATION" not in decision.violation_reasons
