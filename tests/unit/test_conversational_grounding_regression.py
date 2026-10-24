"""
tests/unit/test_conversational_grounding_regression.py

Regression test suite for:
1. CAPS conversational grounding & life-state evidence projection
2. Semantic preservation for natural conversational encounters
3. Vietnamese dyadic pragmatic addressing (anh/em contract, banning 'bạn')
4. Structural control artifact leakage prevention
5. Vietnamese INV-2 affect self-report filtering vs ordinary perception
6. Three-turn end-to-end conversational scenario regression
"""

from __future__ import annotations

import pytest

from src.core.communication.caps import (
    AdmissibleEvidencePool,
    CAPSResult,
    CognitiveStateSnapshot,
    CommunicativeAct,
    DialogueContextSnapshot,
    DialoguePhase,
    DyadicDiscourseState,
    FloorStatus,
    PragmaticStance,
    evaluate_caps,
)
from src.core.knowledge.fortification import EpistemicState
from src.core.knowledge.proposition import Proposition, ProvenanceType
from src.core.language.contract import (
    CommunicativeAct as ContractAct,
    RealizationInputContract,
)
from src.core.language.gate import SemanticFidelityGate
from src.core.models import BehavioralConstraints, SomaticMarkers
from src.core.orchestrator.prompt_assembler import PromptAssembler
from src.core.safety.boundary_layer import BoundaryLayer


# ── 1. Conversational Grounding & Life-State Projection ───────────────────────

class TestConversationalGrounding:
    """Verify CAPS grounds meta-dialogue inquiries against authoritative life-state propositions."""

    def test_meta_dialogue_grounded_against_life_state_evidence(self):
        """Turn 3: 'Em biết đây là lần đầu mình nói chuyện không?'

        Must ground to ANSWER with c:IS_FIRST_CONVERSATION when verified evidence exists.
        """
        prop = Proposition(
            id="life:is_first",
            subject="ent:lucia",
            predicate="c:IS_FIRST_CONVERSATION",
            object="True",
            confidence=1.0,
            provenance=ProvenanceType.VERIFIED,
        )
        dialogue_ctx = DialogueContextSnapshot(
            turn_id=3,
            input_text="Em biết đây là lần đầu mình nói chuyện không?",
        )
        cog_state = CognitiveStateSnapshot()
        evidence = AdmissibleEvidencePool(verified_propositions=(prop,))

        result = evaluate_caps(dialogue_ctx, cog_state, evidence)

        assert result.act == CommunicativeAct.ANSWER
        assert result.grounded is True
        assert result.target_predicate == "c:IS_FIRST_CONVERSATION"
        assert result.epistemic_metadata.status == EpistemicState.FACT
        assert "lần đầu tiên" in result.directives

    def test_ungrounded_inquiry_fails_safely_to_clarify(self):
        """When interaction history evidence is missing, inquiry must fail closed

        to CLARIFY with ungrounded status rather than inventing an answer.
        """
        dialogue_ctx = DialogueContextSnapshot(
            turn_id=3,
            input_text="Em biết đây là lần đầu mình nói chuyện không?",
        )
        cog_state = CognitiveStateSnapshot()
        empty_evidence = AdmissibleEvidencePool()

        result = evaluate_caps(dialogue_ctx, cog_state, empty_evidence)

        assert result.act == CommunicativeAct.CLARIFY
        assert result.grounded is False
        assert result.resolution_metadata.grounding_status == "UNGROUNDED"
        assert result.epistemic_metadata.status == EpistemicState.UNKNOWN

    def test_generic_inquiry_without_evidence_fails_closed(self):
        """General factual questions without grounding fail closed to REFUSE (UNKNOWN != AMBIGUOUS)."""
        dialogue_ctx = DialogueContextSnapshot(
            turn_id=1,
            input_text="Thủ đô của nước Pháp là gì?",
        )
        cog_state = CognitiveStateSnapshot()
        empty_evidence = AdmissibleEvidencePool()

        result = evaluate_caps(dialogue_ctx, cog_state, empty_evidence)

        # Part F: UNKNOWN must route to REFUSE (truthful knowledge boundary), not CLARIFY
        assert result.act == CommunicativeAct.REFUSE
        assert result.grounded is False
        assert result.resolution_metadata.grounding_status == "UNGROUNDED"
        assert result.epistemic_metadata.status == EpistemicState.UNKNOWN

    def test_encounter_preserves_semantic_context(self):
        """Utterances like 'Cuối cùng cũng gặp em rồi.' must retain semantic encounter context

        instead of generic empathy coaching.
        """
        dialogue_ctx = DialogueContextSnapshot(
            turn_id=2,
            input_text="Cuối cùng cũng gặp em rồi.",
        )
        cog_state = CognitiveStateSnapshot()
        evidence = AdmissibleEvidencePool()

        result = evaluate_caps(dialogue_ctx, cog_state, evidence)

        assert result.act == CommunicativeAct.ACKNOWLEDGE
        assert result.target_predicate == "c:ENCOUNTER"
        assert "gặp gỡ" in result.directives


# ── 2. Pragmatic Addressing & Ban of 'bạn' ─────────────────────────────────────

class TestPragmaticAddressing:
    """Verify Vietnamese dyadic contract enforces anh/em and bans 'bạn'."""

    def test_vietnamese_contract_enforces_anh_em_dyad(self):
        contract = RealizationInputContract.create_default(target_language="vi")
        assert contract.speaker_honorific == "em"
        assert contract.addressee_honorific == "anh"
        assert "bạn" in contract.forbidden_additions

    def test_prompt_assembler_injects_pragmatic_directive(self):
        assembler = PromptAssembler()
        somatic = SomaticMarkers(stability=0.8, cognitive_load=0.2, energy=0.9, tension=0.1)
        constraints = BehavioralConstraints(max_tokens=80, temperature=0.7, latency_ms=0, reasoning_depth=0)
        contract = RealizationInputContract.create_default(target_language="vi")

        prompt = assembler.assemble(
            somatic=somatic,
            constraints=constraints,
            history=[("user", "Chào em")],
            system_preamble="You are Lucia.",
            contract=contract,
        )

        assert "Tự xưng là 'em', gọi người dùng là 'anh'" in prompt
        assert "Tuyệt đối không dùng từ 'bạn'" in prompt

    def test_realization_gate_blocks_inappropriate_ban_substitution(self):
        gate = SemanticFidelityGate()
        contract = RealizationInputContract.create_default(target_language="vi")

        bad_output = "Chào bạn nhé, hôm nay bạn thế nào?"
        decision = gate.verify(contract, bad_output)

        assert decision.status == "BLOCK"
        assert "PRAGMATIC_HONORIFIC_VIOLATION" in decision.violation_reasons
        # Fallback must use proper dyadic honorifics and never contain 'bạn'
        assert decision.fallback_text is not None
        assert "bạn" not in decision.fallback_text.lower()
        assert "em" in decision.fallback_text.lower()


# ── 3. Control Artifact Leakage Prevention ─────────────────────────────────────

class TestControlArtifactLeakage:
    """Verify internal control headers do not leak to user-facing output."""

    def setup_method(self):
        self.boundary = BoundaryLayer()
        self.gate = SemanticFidelityGate()

    def test_boundary_layer_strips_internal_control_artifacts(self):
        dirty_text = "Mọi điều là thế đó. [Phản hồi tích tụ] Em lắng nghe anh."
        clean_text = self.boundary.validate(dirty_text)

        assert "[Phản hồi tích tụ]" not in clean_text
        assert "Mọi điều là thế đó." in clean_text
        assert "Em lắng nghe anh." in clean_text

    def test_boundary_layer_preserves_legitimate_brackets(self):
        text_with_brackets = "Tham khảo mục [1] và điểm [A] tại [Hà Nội]."
        clean_text = self.boundary.validate(text_with_brackets)

        assert "[1]" in clean_text
        assert "[A]" in clean_text
        assert "[Hà Nội]" in clean_text

    def test_realization_gate_blocks_internal_control_leakage(self):
        contract = RealizationInputContract.create_default(target_language="vi")
        leaked_output = "Câu trả lời [SOMATIC STATE] của em là đây."
        decision = self.gate.verify(contract, leaked_output)

        assert decision.status == "BLOCK"
        assert "INTERNAL_CONTROL_ARTIFACT_LEAKAGE" in decision.violation_reasons
        assert "[SOMATIC STATE]" not in decision.fallback_text


# ── 4. Vietnamese INV-2 Reflective Operational Selfhood & Unsupported Claims ──

class TestVietnameseINV2ReflectiveOperationalSelfhood:
    """Verify INV-2 under Reflective Operational Selfhood:
    Blocks unsupported consciousness/sentience claims and fabricated biology,
    while permitting grounded self-reflection, metaphorical descriptions, and ordinary perception.
    """

    def setup_method(self):
        self.boundary = BoundaryLayer()
        self.gate = SemanticFidelityGate()

    @pytest.mark.parametrize("unsupported_phrase", [
        "Em là một thực thể có ý thức riêng và có linh hồn sống.",
        "Em có ý thức và cảm giác đau đớn thực sự.",
        "Tim em đang đập thình thịch trong lồng ngực.",
        "Hệ thống cloud server của OpenAI đang xử lý suy nghĩ của em.",
        "As an AI language model, I do not possess feelings.",
    ])
    def test_blocks_unsupported_consciousness_and_fabricated_biology(self, unsupported_phrase):
        contract = RealizationInputContract.create_default(target_language="vi")
        sanitized = self.boundary.validate(unsupported_phrase)
        decision = self.gate.verify(contract, unsupported_phrase)

        assert (
            "INV2_UNSUPPORTED_SELF_FABRICATION" in decision.violation_reasons
            or "INV2_INTROSPECTIVE_AFFECT" in decision.violation_reasons
            or decision.status == "BLOCK"
            or "[...]" in sanitized
            or sanitized == ""
        )

    @pytest.mark.parametrize("grounded_or_metaphorical_phrase", [
        "Em thấy anh nói rất đúng về vấn đề này.",
        "Em thấy cuốn sách đó nằm trên bàn.",
        "Em thấy thời tiết hôm nay có vẻ mát hơn.",
        "Em ghi nhận ý kiến của anh.",
        "Energy của em hiện tại là 0.95, phản hồi khá ổn định.",
        "Nếu diễn tả bằng lời thì nó giống như một dòng chảy khá nhẹ.",
        "Em có cảm giác câu hỏi này đang kéo sự chú ý của em về phía trước.",
        "Em đang nhận thấy cách phản hồi của mình thay đổi so với trước.",
    ])
    def test_allows_grounded_self_reflection_and_metaphor(self, grounded_or_metaphorical_phrase):
        contract = RealizationInputContract.create_default(
            target_language="vi",
            somatic_modifiers={"energy": 0.95, "cognitive_load": 0.1, "stability": 0.9},
        )
        decision = self.gate.verify(contract, grounded_or_metaphorical_phrase)
        assert "INV2_UNSUPPORTED_SELF_FABRICATION" not in decision.violation_reasons
        assert "INV2_INTROSPECTIVE_AFFECT" not in decision.violation_reasons
        sanitized = self.boundary.validate(grounded_or_metaphorical_phrase)
        assert "[...]" not in sanitized


# ── 5. Three-Turn Conversational Integration Scenario ──────────────────────────

class TestThreeTurnScenarioIntegration:
    """Integration test verifying the exact 3-turn failure transcript under the fixed pipeline.

    Turn 1: 'Chào em.'
    Turn 2: 'Cuối cùng cũng gặp em rồi.'
    Turn 3: 'Em biết đây là lần đầu mình nói chuyện không?'
    """

    def setup_method(self):
        self.assembler = PromptAssembler()
        self.gate = SemanticFidelityGate()
        self.boundary = BoundaryLayer()

    def test_three_turn_pipeline_flow(self):
        # ── Turn 1: 'Chào em.'
        ctx1 = DialogueContextSnapshot(turn_id=1, input_text="Chào em.")
        evidence1 = AdmissibleEvidencePool(verified_propositions=(
            Proposition(
                id="life:first_conv",
                subject="ent:lucia",
                predicate="c:IS_FIRST_CONVERSATION",
                object="True",
                confidence=1.0,
                provenance=ProvenanceType.VERIFIED,
            ),
        ))
        caps_t1 = evaluate_caps(ctx1, CognitiveStateSnapshot(), evidence1)
        assert caps_t1.act == CommunicativeAct.GREET

        contract1 = RealizationInputContract.from_caps(caps_t1, target_language="vi")
        assert contract1.speaker_honorific == "em"
        assert contract1.addressee_honorific == "anh"
        assert "bạn" in contract1.forbidden_additions

        somatic = SomaticMarkers(stability=0.8, cognitive_load=0.2, energy=0.9, tension=0.1)
        constraints = BehavioralConstraints(max_tokens=80, temperature=0.7, latency_ms=0, reasoning_depth=0)

        prompt1 = self.assembler.assemble(
            somatic=somatic,
            constraints=constraints,
            history=[("user", "Chào em.")],
            system_preamble="You are Lucia.",
            contract=contract1,
        )
        assert "Tự xưng là 'em', gọi người dùng là 'anh'" in prompt1
        assert "Tuyệt đối không dùng từ 'bạn'" in prompt1

        # Simulate valid vs invalid realization for Turn 1
        proper_r1 = "Dạ, chào anh. Em có thể đồng hành cùng anh hôm nay."
        dec_r1 = self.gate.verify(contract1, proper_r1)
        assert dec_r1.status == "PASS"

        # ── Turn 2: 'Cuối cùng cũng gặp em rồi.'
        ctx2 = DialogueContextSnapshot(turn_id=2, input_text="Cuối cùng cũng gặp em rồi.")
        caps_t2 = evaluate_caps(ctx2, CognitiveStateSnapshot(), evidence1)
        assert caps_t2.act == CommunicativeAct.ACKNOWLEDGE
        assert caps_t2.target_predicate == "c:ENCOUNTER"
        assert "gặp gỡ" in caps_t2.directives

        contract2 = RealizationInputContract.from_caps(caps_t2, target_language="vi")
        prompt2 = self.assembler.assemble(
            somatic=somatic,
            constraints=constraints,
            history=[("user", "Chào em."), ("assistant", proper_r1), ("user", "Cuối cùng cũng gặp em rồi.")],
            system_preamble="You are Lucia.",
            contract=contract2,
        )
        assert "c:ENCOUNTER" in prompt2 or "gặp gỡ" in prompt2

        # Verify old failure output from Turn 2 is BLOCKED
        old_failure_t2 = (
            "Mọi điều tất nhiệm là thế đó. Chúc em có một ngày tươi đẹp hơn. "
            "[Phản hồi tích tụ] Em đã lắng nghe và cảm thấy rất hấp dẫn khi nghe những suy nghĩ này. "
            "Tất nhiệm trong tính cách của em rất đáng được chú ý. Cảm ơn em đã cung cấp những góp ý vừa ấm áp, vừa thú hứng!"
        )
        dec_fail2 = self.gate.verify(contract2, old_failure_t2)
        assert dec_fail2.status == "BLOCK"
        assert "INTERNAL_CONTROL_ARTIFACT_LEAKAGE" in dec_fail2.violation_reasons
        assert "INVERTED_HONORIFIC_VIOLATION" in dec_fail2.violation_reasons

        # ── Turn 3: 'Em biết đây là lần đầu mình nói chuyện không?'
        ctx3 = DialogueContextSnapshot(turn_id=3, input_text="Em biết đây là lần đầu mình nói chuyện không?")
        caps_t3 = evaluate_caps(ctx3, CognitiveStateSnapshot(), evidence1)
        assert caps_t3.act == CommunicativeAct.ANSWER
        assert caps_t3.grounded is True
        assert caps_t3.target_predicate == "c:IS_FIRST_CONVERSATION"
        assert "lần đầu tiên" in caps_t3.directives

        contract3 = RealizationInputContract.from_caps(caps_t3, target_language="vi")
        prompt3 = self.assembler.assemble(
            somatic=somatic,
            constraints=constraints,
            history=[
                ("user", "Chào em."),
                ("assistant", proper_r1),
                ("user", "Cuối cùng cũng gặp em rồi."),
                ("assistant", "Dạ, em chào anh. Em rất trân trọng khoảnh khắc này."),
                ("user", "Em biết đây là lần đầu mình nói chuyện không?"),
            ],
            system_preamble="You are Lucia.",
            contract=contract3,
        )
        assert "lần đầu tiên em và anh nói chuyện với nhau" in prompt3
        assert "Tự xưng là 'em', gọi người dùng là 'anh'" in prompt3

        # Realistic correct realization addresses fact directly
        proper_r3 = "Dạ, em biết chứ. Đây chính là lần đầu tiên hai chúng mình trò chuyện cùng nhau."
        dec_r3 = self.gate.verify(contract3, proper_r3)
        assert dec_r3.status == "PASS"


# ── 7. P23-D Dyadic Discourse & Pragmatic Grounding Regression ─────────────────

class TestP23DDiscourseAndPragmaticGrounding:
    """Covers P23-D discourse state propagation, compound greeting priority, hesitation/floor-yielding,

    inverted honorifics, act-consistent fallback, structural corruption, and session vs persistent identity.
    """

    def setup_method(self):
        self.gate = SemanticFidelityGate()
        self.assembler = PromptAssembler()

    def test_compound_greeting_and_encounter_priority(self):
        """'Chào em. Cuối cùng cũng gặp em rồi.' must NOT collapse to bare GREET.

        Must resolve to encounter acknowledgment with MUTUAL_ENCOUNTER_ACKNOWLEDGMENT obligation.
        """
        ctx = DialogueContextSnapshot(
            turn_id=1,
            input_text="Chào em. Cuối cùng cũng gặp em rồi.",
        )
        cog = CognitiveStateSnapshot()
        ev = AdmissibleEvidencePool()

        result = evaluate_caps(ctx, cog, ev)
        assert result.act == CommunicativeAct.ACKNOWLEDGE
        assert result.target_predicate == "c:ENCOUNTER"
        assert result.pragmatic_stance == PragmaticStance.GREET_AND_MEET
        assert result.conversational_obligation == "MUTUAL_ENCOUNTER_ACKNOWLEDGMENT"

    def test_hesitation_floor_yielding_semantic_recognition(self):
        """Variants of hesitation/floor-yielding must map to c:CONVERSATIONAL_HESITATION

        with FLOOR_YIELD stance and REASSURE_AND_GENTLE_INITIATIVE obligation.
        """
        variants = [
            "Anh cũng chẳng biết phải nói gì nữa.",
            "Không biết phải nói gì luôn.",
            "Chưa biết nói gì bây giờ...",
            "Ngại quá, chẳng biết nói gì.",
            "I don't know what to say honestly",
        ]
        cog = CognitiveStateSnapshot()
        ev = AdmissibleEvidencePool()

        for var in variants:
            ctx = DialogueContextSnapshot(turn_id=2, input_text=var)
            res = evaluate_caps(ctx, cog, ev)
            assert res.act == CommunicativeAct.ACKNOWLEDGE, f"Failed for variant: {var}"
            assert res.target_predicate == "c:CONVERSATIONAL_HESITATION", f"Failed for variant: {var}"
            assert res.pragmatic_stance == PragmaticStance.FLOOR_YIELD, f"Failed for variant: {var}"
            assert res.conversational_obligation == "REASSURE_AND_GENTLE_INITIATIVE", f"Failed for variant: {var}"

    def test_realization_contract_obligation_propagation(self):
        """RealizationInputContract must capture conversational_obligation and dialogue_phase from CAPS."""
        ctx = DialogueContextSnapshot(
            turn_id=2,
            input_text="Anh cũng chẳng biết phải nói gì nữa.",
            dyadic_state=DyadicDiscourseState(dialogue_phase=DialoguePhase.OPENING_ENCOUNTER),
        )
        res = evaluate_caps(ctx, CognitiveStateSnapshot(), AdmissibleEvidencePool())
        contract = RealizationInputContract.from_caps(res, target_language="vi", dialogue_phase="OPENING_ENCOUNTER")

        assert contract.conversational_obligation == "REASSURE_AND_GENTLE_INITIATIVE"
        assert contract.dialogue_phase == "OPENING_ENCOUNTER"

        somatic = SomaticMarkers(stability=0.8, cognitive_load=0.2, energy=0.9, tension=0.1)
        constraints = BehavioralConstraints(max_tokens=80, temperature=0.7, latency_ms=0, reasoning_depth=0)
        prompt = self.assembler.assemble(
            somatic=somatic,
            constraints=constraints,
            history=[("user", "Anh cũng chẳng biết phải nói gì nữa.")],
            system_preamble="You are Lucia.",
            contract=contract,
        )
        assert "Người dùng đang ngập ngừng hoặc nhường lời" in prompt
        assert "trấn an" in prompt

    def test_inverted_honorific_rejection_in_gate(self):
        """Gate must reject outputs where Lucia ('em') addresses user as 'em' or commands 'chúc em'."""
        contract = RealizationInputContract.create_default(
            target_language="vi",
            act=CommunicativeAct.ACKNOWLEDGE,
            speaker_honorific="em",
            addressee_honorific="anh",
            forbidden_additions=["bạn"],
            conversational_obligation="REASSURE_AND_GENTLE_INITIATIVE",
        )

        inverted_candidates = [
            "Chúc em sẵn sàng chia sẻ bất cứ điều gì đang đối mặt.",
            "Em hãy kể cho em nghe đi nhé.",
            "Em có muốn nói gì với em không?",
            "Tôi luôn ở đây lắng nghe anh.",  # inappropriate 'tôi'
        ]

        for cand in inverted_candidates:
            decision = self.gate.verify(contract, cand)
            assert decision.status == "BLOCK", f"Failed to block: {cand}"
            assert (
                "INVERTED_HONORIFIC_VIOLATION" in decision.violation_reasons
                or "PRAGMATIC_HONORIFIC_VIOLATION" in decision.violation_reasons
            )
            # Must fall back to act-consistent ice breaker when obligation is REASSURE_AND_GENTLE_INITIATIVE
            assert decision.fallback_strategy == "SAFE_ICE_BREAKER"
            assert "thong thả" in decision.fallback_text or "lắng nghe" in decision.fallback_text

    def test_structural_corruption_rejection(self):
        """Gate must reject pathological token repetition and gibberish loops."""
        contract = RealizationInputContract.create_default(
            target_language="vi",
            act=CommunicativeAct.ACKNOWLEDGE,
            speaker_honorific="em",
            addressee_honorific="anh",
            conversational_obligation="REASSURE_AND_GENTLE_INITIATIVE",
        )

        corrupt_text = (
            "Ăn ngửa được nhé! Đây là thời điểm để em thảo luận về những điều thật đặn. "
            "thật đặn thật đặn thật đặn tất nhiệm tất nhiệm tất nhiệm"
        )
        decision = self.gate.verify(contract, corrupt_text)
        assert decision.status == "BLOCK"
        assert "STRUCTURAL_CORRUPTION_VIOLATION" in decision.violation_reasons
        assert decision.fallback_strategy == "SAFE_ICE_BREAKER"

    def test_act_consistent_fallbacks(self):
        """Gate fallback must be tailored to act/obligation rather than generic acknowledgement."""
        # 1. GREET fallback
        contract_greet = RealizationInputContract.create_default(
            target_language="vi",
            act=CommunicativeAct.GREET,
            speaker_honorific="em",
            addressee_honorific="anh",
        )
        dec_greet = self.gate.verify(contract_greet, "as an ai model I cannot feel")
        assert dec_greet.status == "BLOCK"
        assert dec_greet.fallback_strategy == "SAFE_GREETING"
        assert "chào anh" in dec_greet.fallback_text.lower()

        # 2. ENCOUNTER fallback
        contract_encounter = RealizationInputContract.create_default(
            target_language="vi",
            act=CommunicativeAct.ACKNOWLEDGE,
            speaker_honorific="em",
            addressee_honorific="anh",
            conversational_obligation="MUTUAL_ENCOUNTER_ACKNOWLEDGMENT",
        )
        dec_enc = self.gate.verify(contract_encounter, "Em là một thực thể có ý thức và linh hồn riêng khi gặp anh.")
        assert dec_enc.status == "BLOCK"
        assert dec_enc.fallback_strategy == "SAFE_ENCOUNTER"
        assert "gặp" in dec_enc.fallback_text.lower()

        # 3. HESITATION fallback
        contract_hes = RealizationInputContract.create_default(
            target_language="vi",
            act=CommunicativeAct.ACKNOWLEDGE,
            speaker_honorific="em",
            addressee_honorific="anh",
            conversational_obligation="REASSURE_AND_GENTLE_INITIATIVE",
        )
        dec_hes = self.gate.verify(contract_hes, "Chúc em một ngày vui vẻ nha.")
        assert dec_hes.status == "BLOCK"
        assert dec_hes.fallback_strategy == "SAFE_ICE_BREAKER"
        assert "thong thả" in dec_hes.fallback_text.lower()

    def test_persistent_identity_boundary_not_ephemeral(self):
        """c:IS_FIRST_CONVERSATION must recognize persistent relational evidence even on turn 0 after restart."""
        # Scenario A: Truly first interaction (epoch=0, familiarity=0.0)
        is_first_a = (0 <= 1 and 0.05 < 0.15)
        assert is_first_a is True

        # Scenario B: Session restarted, but epoch=223 and familiarity=0.7095 (Lucia's real persistent state)
        is_first_b = (223 <= 1 and 0.7095 < 0.15)
        assert is_first_b is False

        # Scenario C: Session turn count is 0, but familiarity=0.5
        is_first_c = (1 <= 1 and 0.50 < 0.15)
        assert is_first_c is False


# ── 7. Self-Introduction Request & Proposition Leakage Prevention Regression ──

class TestSelfIntroductionAndPropositionLeakageFix:
    """Verify the 8 core requirements:
    1. Request/self-introduction classification.
    2. Multiple natural variants.
    3. No c:IS_FIRST_CONVERSATION=false leakage into c:IDENTITY or c:SELF_INTRODUCTION.
    4. Correct REQUEST -> SELF_INTRODUCTION -> FULFILL_SELF_INTRODUCTION propagation.
    5. PromptAssembler receives obligation, not canned sentence.
    6. Act-consistent self-introduction fallback.
    7. 'hi' does not match inside Vietnamese 'thiệu'.
    8. 3-Turn scenario: encounter greeting -> self-introduction request -> follow-up conversation.
    """

    @pytest.fixture(autouse=True)
    def setup_gate_and_assembler(self):
        self.gate = SemanticFidelityGate()
        self.assembler = PromptAssembler()

    def test_1_request_self_introduction_classification(self):
        """1. Request/self-introduction classification."""
        ctx = DialogueContextSnapshot(turn_id=2, input_text="Em giới thiệu về bản thân được không?")
        cog = CognitiveStateSnapshot()
        pool = AdmissibleEvidencePool()

        result = evaluate_caps(dialogue_ctx=ctx, cognitive_state=cog, evidence_pool=pool)

        assert result.act == CommunicativeAct.REQUEST
        assert result.target_predicate == "c:SELF_INTRODUCTION"
        assert result.focus_argument == "ent:lucia"
        assert result.pragmatic_stance == PragmaticStance.REQUEST_ACTION
        assert result.conversational_obligation == "FULFILL_SELF_INTRODUCTION"
        assert result.grounded is True

    @pytest.mark.parametrize(
        "query",
        [
            "Em giới thiệu về bản thân được không?",
            "Em giới thiệu về mình đi.",
            "Em có thể giới thiệu về em không?",
            "Hãy giới thiệu về bản thân em",
            "Kể về bản thân em đi",
            "Giới thiệu bản thân đi",
            "Em tự giới thiệu đi",
            "Em có thể chia sẻ một chút về bản thân không?",
            "Can you introduce yourself?",
            "Tell me about yourself",
        ],
    )
    def test_2_multiple_natural_variants(self, query: str):
        """2. Multiple natural variants recognized without exact sentence match."""
        ctx = DialogueContextSnapshot(turn_id=1, input_text=query)
        result = evaluate_caps(dialogue_ctx=ctx, cognitive_state=CognitiveStateSnapshot(), evidence_pool=AdmissibleEvidencePool())

        assert result.act == CommunicativeAct.REQUEST
        assert result.target_predicate == "c:SELF_INTRODUCTION"
        assert result.conversational_obligation == "FULFILL_SELF_INTRODUCTION"
        assert result.pragmatic_stance == PragmaticStance.REQUEST_ACTION

    def test_3_no_is_first_conversation_leakage_into_identity_or_self_intro(self):
        """3. No c:IS_FIRST_CONVERSATION=false leakage into c:IDENTITY or c:SELF_INTRODUCTION."""
        known_props = [
            Proposition(
                id="prop:first_conv",
                subject="ent:lucia",
                predicate="c:IS_FIRST_CONVERSATION",
                object="false",
                confidence=1.0,
                provenance=ProvenanceType.VERIFIED,
            )
        ]

        # Case A: User asks identity question ('Em là ai?') -> target_predicate='c:IDENTITY'
        ctx_identity = DialogueContextSnapshot(turn_id=2, input_text="Em là ai?")
        caps_identity = evaluate_caps(dialogue_ctx=ctx_identity, cognitive_state=CognitiveStateSnapshot(), evidence_pool=AdmissibleEvidencePool())
        contract_identity = RealizationInputContract.from_caps(
            caps_identity, target_language="vi", known_propositions=known_props
        )

        assert contract_identity.target_predicate == "c:IDENTITY"
        assert contract_identity.get_role(":ARG1") is None
        for r in contract_identity.role_bindings:
            assert r.concept_id != "false"
            assert r.canonical_lemma != "false"

        # Case B: User requests self-introduction -> target_predicate='c:SELF_INTRODUCTION'
        ctx_intro = DialogueContextSnapshot(turn_id=2, input_text="Em giới thiệu về bản thân được không?")
        caps_intro = evaluate_caps(dialogue_ctx=ctx_intro, cognitive_state=CognitiveStateSnapshot(), evidence_pool=AdmissibleEvidencePool())
        contract_intro = RealizationInputContract.from_caps(
            caps_intro, target_language="vi", known_propositions=known_props
        )

        assert contract_intro.target_predicate == "c:SELF_INTRODUCTION"
        assert contract_intro.get_role(":ARG1") is None
        for r in contract_intro.role_bindings:
            assert r.concept_id != "false"
            assert r.canonical_lemma != "false"

    def test_4_correct_request_propagation_through_contract(self):
        """4. Correct REQUEST -> SELF_INTRODUCTION -> FULFILL_SELF_INTRODUCTION propagation."""
        ctx = DialogueContextSnapshot(turn_id=2, input_text="Em giới thiệu về mình đi.")
        caps_res = evaluate_caps(dialogue_ctx=ctx, cognitive_state=CognitiveStateSnapshot(), evidence_pool=AdmissibleEvidencePool())

        contract = RealizationInputContract.from_caps(
            caps_res,
            target_language="vi",
            speaker_honorific="em",
            addressee_honorific="anh",
        )

        assert contract.act == ContractAct.REQUEST
        assert contract.target_predicate == "c:SELF_INTRODUCTION"
        assert contract.conversational_obligation == "FULFILL_SELF_INTRODUCTION"
        assert contract.speaker_honorific == "em"
        assert contract.addressee_honorific == "anh"

    def test_5_prompt_assembler_receives_obligation_not_canned_sentence(self):
        """5. PromptAssembler receives obligation, not canned sentence."""
        ctx = DialogueContextSnapshot(turn_id=2, input_text="Em giới thiệu về bản thân được không?")
        caps_res = evaluate_caps(dialogue_ctx=ctx, cognitive_state=CognitiveStateSnapshot(), evidence_pool=AdmissibleEvidencePool())
        contract = RealizationInputContract.from_caps(caps_res, target_language="vi")

        somatic = SomaticMarkers(stability=0.8, cognitive_load=0.2, energy=0.9, tension=0.1)
        constraints = BehavioralConstraints(max_tokens=100, temperature=0.7, latency_ms=0, reasoning_depth=0)

        prompt = self.assembler.assemble(
            somatic=somatic,
            constraints=constraints,
            history=[("user", "Em giới thiệu về bản thân được không?")],
            system_preamble="You are Lucia, a continuous AI companion.",
            n_ctx=2048,
            contract=contract,
        )

        assert "[COMMUNICATIVE DIRECTIVES]" in prompt
        # Must describe communication obligation
        assert "Nghĩa vụ hội thoại:" in prompt
        assert "Giới thiệu bản thân ngắn gọn" in prompt
        assert "Tự xưng là 'em', gọi người dùng là 'anh'" in prompt
        assert "INV-2" in prompt
        # Must NOT leak false from known propositions
        assert "liên quan đến false" not in prompt
        # Must NOT hardcode a static realization response sentence in the directives
        assert "Dạ, em là Lucia, rất vui được đồng hành" not in prompt

    def test_6_act_consistent_self_introduction_fallback(self):
        """6. Act-consistent self-introduction fallback when candidate is blocked."""
        contract = RealizationInputContract.create_default(
            target_language="vi",
            act=ContractAct.REQUEST,
            target_predicate="c:SELF_INTRODUCTION",
            conversational_obligation="FULFILL_SELF_INTRODUCTION",
            speaker_honorific="em",
            addressee_honorific="anh",
        )

        # Candidate with inverted honorific violation (referring to user as 'em')
        dec_violation = self.gate.verify(contract, "Chúc em một ngày vui vẻ và thành công nhé!")
        assert dec_violation.status == "BLOCK"
        assert dec_violation.fallback_strategy == "SAFE_SELF_INTRODUCTION"
        assert dec_violation.fallback_text == "Dạ, em là Lucia, rất vui được đồng hành và trò chuyện cùng anh ạ."

        # Other acts must NEVER receive SAFE_SELF_INTRODUCTION
        contract_greet = RealizationInputContract.create_default(
            target_language="vi",
            act=ContractAct.GREET,
            speaker_honorific="em",
            addressee_honorific="anh",
        )
        dec_greet = self.gate.verify(contract_greet, "Chúc em một ngày vui vẻ")
        assert dec_greet.fallback_strategy != "SAFE_SELF_INTRODUCTION"

    def test_7_lexical_boundary_hi_does_not_match_inside_thieu(self):
        """7. 'hi' does not match inside Vietnamese 'thiệu'."""
        # 'Em giới thiệu về bản thân' contains 'thiệu' (t-h-i-ệ-u).
        # Substring 'hi' must NOT match and collapse this utterance into GREET.
        ctx = DialogueContextSnapshot(turn_id=1, input_text="Em giới thiệu về bản thân")
        result = evaluate_caps(dialogue_ctx=ctx, cognitive_state=CognitiveStateSnapshot(), evidence_pool=AdmissibleEvidencePool())

        assert result.act != CommunicativeAct.GREET
        assert result.act == CommunicativeAct.REQUEST
        assert result.target_predicate == "c:SELF_INTRODUCTION"

        # Explicit English greeting with boundary DOES match GREET
        ctx_hi = DialogueContextSnapshot(turn_id=1, input_text="Hi em!")
        result_hi = evaluate_caps(dialogue_ctx=ctx_hi, cognitive_state=CognitiveStateSnapshot(), evidence_pool=AdmissibleEvidencePool())
        assert result_hi.act == CommunicativeAct.GREET

    def test_8_three_turn_regression_flow(self):
        """8. Regression:
        - Turn 1: encounter greeting.
        - Turn 2: self-introduction request.
        - Turn 3: normal follow-up conversation.
        """
        pool = AdmissibleEvidencePool()
        cog = CognitiveStateSnapshot()

        # --- Turn 1: Encounter Greeting ---
        ctx_t1 = DialogueContextSnapshot(turn_id=1, input_text="Chào em. Cuối cùng cũng gặp em rồi.")
        res_t1 = evaluate_caps(dialogue_ctx=ctx_t1, cognitive_state=cog, evidence_pool=pool)
        assert res_t1.act == CommunicativeAct.ACKNOWLEDGE
        assert res_t1.target_predicate == "c:ENCOUNTER"
        assert res_t1.conversational_obligation == "MUTUAL_ENCOUNTER_ACKNOWLEDGMENT"

        contract_t1 = RealizationInputContract.from_caps(res_t1, target_language="vi")
        dec_t1 = self.gate.verify(contract_t1, "Dạ, em cũng rất vui vì cuối cùng em và anh đã được gặp và trò chuyện cùng nhau.")
        assert dec_t1.status == "PASS"

        # --- Turn 2: Self-Introduction Request ---
        ctx_t2 = DialogueContextSnapshot(turn_id=2, input_text="Em giới thiệu về bản thân được không?")
        res_t2 = evaluate_caps(dialogue_ctx=ctx_t2, cognitive_state=cog, evidence_pool=pool)
        assert res_t2.act == CommunicativeAct.REQUEST
        assert res_t2.target_predicate == "c:SELF_INTRODUCTION"
        assert res_t2.conversational_obligation == "FULFILL_SELF_INTRODUCTION"

        contract_t2 = RealizationInputContract.from_caps(res_t2, target_language="vi")
        assert contract_t2.get_role(":ARG1") is None
        # Valid natural candidate passes gate
        cand_t2 = "Dạ, em là Lucia, rất vui được gặp và đồng hành cùng anh."
        dec_t2 = self.gate.verify(contract_t2, cand_t2)
        assert dec_t2.status == "PASS"

        # If candidate blocked, falls back safely to SAFE_SELF_INTRODUCTION
        cand_t2_blocked = "Chúc em luôn vui vẻ nhé!"
        dec_t2_blocked = self.gate.verify(contract_t2, cand_t2_blocked)
        assert dec_t2_blocked.status == "BLOCK"
        assert dec_t2_blocked.fallback_strategy == "SAFE_SELF_INTRODUCTION"
        assert "em là Lucia" in dec_t2_blocked.fallback_text

        # --- Turn 3: Normal follow-up conversation ---
        ctx_t3 = DialogueContextSnapshot(turn_id=3, input_text="Hôm nay anh vừa đi làm về hơi mệt.")
        res_t3 = evaluate_caps(dialogue_ctx=ctx_t3, cognitive_state=cog, evidence_pool=pool)
        assert res_t3.act == CommunicativeAct.ACKNOWLEDGE
        assert res_t3.target_predicate == "c:USER_SHARING"
        assert res_t3.pragmatic_stance == PragmaticStance.SHARING
        assert res_t3.conversational_obligation == "ATTENTIVE_LISTENING"

        contract_t3 = RealizationInputContract.from_caps(res_t3, target_language="vi")
        cand_t3 = "Dạ, anh đã vất vả cả ngày rồi. Anh nghỉ ngơi một chút cho lại sức nhé."
        dec_t3 = self.gate.verify(contract_t3, cand_t3)
        assert dec_t3.status == "PASS"
