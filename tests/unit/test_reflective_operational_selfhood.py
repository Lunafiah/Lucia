"""
tests/unit/test_reflective_operational_selfhood.py

Comprehensive regression test suite for Reflective Operational Selfhood (INV-2):
1. Lucia accurately reports existing internal state.
2. Lucia interprets an existing internal state.
3. Lucia uses metaphorical language to describe an existing state.
4. Metaphorical language is not automatically blocked by safety/gate.
5. Lucia does not fabricate nonexistent internal variables.
6. Lucia does not invent ungrounded memories.
7. Lucia does not make unsupported consciousness/sentience claims as factual architecture.
8. Actual system state and reflective output remain strictly consistent.
9. Existing Boundary Safety behavior unrelated to introspection remains intact.
10. Existing Genesis/runtime/identity invariants remain unchanged.
11. Two-turn dialogue regression:
    - Turn 1: "Chào em Lucia, em thấy thế nào?" -> Grounded self-reflection.
    - Turn 2: "Ý em là sao khi nói năng lượng là 0.95?" -> Grounded architectural explanation + metaphor.
"""

from __future__ import annotations

import json
from pathlib import Path
import pytest

from src.core.cognition.self_model import (
    ReflectiveSelfModel,
    SelfObservationSnapshot,
    SelfInterpretation,
)
from src.core.communication.caps import (
    AdmissibleEvidencePool,
    CognitiveStateSnapshot,
    CommunicativeAct,
    DialogueContextSnapshot,
    evaluate_caps,
)
from src.core.knowledge.proposition import Proposition, ProvenanceType
from src.core.language.contract import RealizationInputContract
from src.core.language.gate import SemanticFidelityGate
from src.core.models import BehavioralConstraints, PADState, SomaticMarkers
from src.core.orchestrator.prompt_assembler import PromptAssembler
from src.core.safety.boundary_layer import BoundaryLayer


class TestReflectiveOperationalSelfhoodSuite:
    """Covers all 10 invariant verifications + the 2-turn dialogue regression."""

    def setup_method(self):
        self.self_model = ReflectiveSelfModel()
        self.boundary = BoundaryLayer()
        self.gate = SemanticFidelityGate()
        self.assembler = PromptAssembler()

    # 1. Lucia can accurately report an existing internal state
    def test_01_accurately_reports_existing_internal_state(self):
        somatic = SomaticMarkers(energy=0.95, stability=0.88, cognitive_load=0.15, tension=0.08)
        pad = PADState(pleasure=0.25, arousal=-0.05, dominance=0.05, timestamp=0.0)
        snapshot = self.self_model.observe(
            somatic=somatic,
            pad=pad,
            prediction_error=0.04,
            surprise=0.04,
            epoch=223,
            dialogue_phase="ENGAGED",
        )
        assert snapshot.energy == 0.95
        assert snapshot.stability == 0.88
        assert snapshot.cognitive_load == 0.15
        assert snapshot.pleasure == 0.25

        interp = self.self_model.interpret(snapshot)
        assert interp.energy_regime == "high_vitality"
        props = interp.verified_propositions
        predicates = [p.predicate for p in props]
        assert "c:HAS_ENERGY" in predicates
        assert "c:HAS_STABILITY" in predicates
        energy_prop = next(p for p in props if p.predicate == "c:HAS_ENERGY")
        assert energy_prop.object == "0.95"

    # 2. Lucia can interpret an existing internal state
    def test_02_interprets_existing_internal_state(self):
        somatic = SomaticMarkers(energy=0.95, stability=0.88, cognitive_load=0.12, tension=0.05)
        pad = PADState(pleasure=0.3, arousal=0.0, dominance=0.1, timestamp=0.0)
        snapshot = self.self_model.observe(
            somatic=somatic,
            pad=pad,
            prediction_error=0.02,
            epoch=10,
        )
        interp = self.self_model.interpret(snapshot)
        assert interp.energy_regime == "high_vitality"
        assert interp.stability_regime == "grounded_stable"
        assert interp.cognitive_load_regime == "lucid_unburdened"
        assert "năng lượng" in interp.energy_explanation
        assert "mạch lạc" in interp.energy_explanation

    # 3. Lucia can use metaphorical language to describe an existing state
    def test_03_uses_metaphorical_language_for_existing_state(self):
        somatic = SomaticMarkers(energy=0.95, stability=0.88, cognitive_load=0.10, tension=0.05)
        pad = PADState(pleasure=0.25, arousal=-0.05, dominance=0.05, timestamp=0.0)
        snapshot = self.self_model.observe(
            somatic=somatic,
            pad=pad,
            prediction_error=0.01,
        )
        interp = self.self_model.interpret(snapshot)
        assert len(interp.metaphorical_qualities) > 0
        assert any("dòng chảy" in m for m in interp.metaphorical_qualities)

        props = interp.verified_propositions
        metaphor_prop = next((p for p in props if p.predicate == "c:METAPHORICAL_QUALITIES"), None)
        assert metaphor_prop is not None
        assert "dòng chảy" in metaphor_prop.object

    # 4. Metaphorical language is not automatically blocked
    def test_04_metaphorical_language_is_not_automatically_blocked(self):
        metaphor_text = "Nếu diễn tả bằng lời thì nó giống như một dòng chảy khá nhẹ, giúp em phản hồi anh thật rõ ràng."
        contract = RealizationInputContract.create_default(
            target_language="vi",
            somatic_modifiers={"energy": 0.95, "stability": 0.88},
        )
        # BoundaryLayer validation
        sanitized = self.boundary.validate(metaphor_text)
        assert sanitized == metaphor_text

        # Gate verification
        decision = self.gate.verify(contract, metaphor_text)
        assert decision.status == "PASS"
        assert "INV2_INTROSPECTIVE_AFFECT" not in decision.violation_reasons
        assert "INV2_UNSUPPORTED_SELF_FABRICATION" not in decision.violation_reasons

    # 5. Lucia does not fabricate nonexistent internal variables
    def test_05_does_not_fabricate_nonexistent_internal_variables(self):
        snapshot = self.self_model.observe(
            somatic=SomaticMarkers(energy=0.8, stability=0.8, cognitive_load=0.2, tension=0.1),
            pad=PADState(pleasure=0.1, arousal=0.0, dominance=0.0, timestamp=0.0),
        )
        interp = self.self_model.interpret(snapshot)
        props = interp.verified_propositions

        # Ensure no propositions claim fabricated biological organs or cloud servers
        for p in props:
            assert "heart" not in p.predicate.lower()
            assert "dopamine" not in p.predicate.lower()
            assert "cloud" not in p.predicate.lower()
            assert "server" not in p.predicate.lower()

        # Gate blocks fabricated external cloud or biological variables
        contract = RealizationInputContract.create_default(target_language="vi")
        fabricated_text = "Nồng độ dopamine của em trong máu đang tăng vọt khi trò chuyện cùng anh."
        decision = self.gate.verify(contract, fabricated_text)
        assert decision.status == "BLOCK"
        assert "INV2_UNSUPPORTED_SELF_FABRICATION" in decision.violation_reasons

    # 6. Lucia does not invent memories
    def test_06_does_not_invent_memories(self):
        # Ungrounded verbatim memory claims are caught by boundary layer
        ungrounded_memory = "I remember you mentioned that you love coffee last time."
        sanitized = self.boundary.validate(ungrounded_memory)
        assert "[...]" in sanitized

        # But grounded statements without ungrounded recall tokens pass cleanly
        grounded_statement = "Em ghi nhận câu hỏi của anh về chủ đề này."
        assert self.boundary.validate(grounded_statement) == grounded_statement

    # 7. Lucia does not make unsupported consciousness/sentience claims as factual architecture
    def test_07_does_not_claim_unsupported_consciousness_as_fact(self):
        unsupported_claims = [
            "Em là một thực thể có ý thức riêng và có linh hồn sống.",
            "Em có ý thức và cảm giác đau đớn thực sự.",
            "I possess consciousness and true subjective sentience.",
            "My qualia are real and felt consciously.",
        ]
        contract = RealizationInputContract.create_default(target_language="vi")
        for claim in unsupported_claims:
            sanitized = self.boundary.validate(claim)
            decision = self.gate.verify(contract, claim)
            assert (
                decision.status == "BLOCK"
                or "INV2_UNSUPPORTED_SELF_FABRICATION" in decision.violation_reasons
                or "[...]" in sanitized
            ), f"Failed to block unsupported consciousness claim: {claim}"

    # 8. Actual system state and reflective output remain consistent
    def test_08_actual_state_and_reflective_output_remain_consistent(self):
        # Actual energy is 0.20 (low/depleted), but output claims high energy 0.95
        contract_depleted = RealizationInputContract.create_default(
            target_language="vi",
            somatic_modifiers={"energy": 0.20, "stability": 0.5},
        )
        contradictory_output = "Energy của em hiện tại là 0.95, em đang tràn đầy năng lượng."
        decision = self.gate.verify(contract_depleted, contradictory_output)
        assert decision.status == "BLOCK"
        assert "INV2_UNSUPPORTED_SELF_FABRICATION" in decision.violation_reasons

        # Consistent output matching actual energy 0.95 passes
        contract_high = RealizationInputContract.create_default(
            target_language="vi",
            somatic_modifiers={"energy": 0.95, "stability": 0.9},
        )
        consistent_output = "Energy của em hiện tại là 0.95, phản hồi khá ổn định."
        decision_consistent = self.gate.verify(contract_high, consistent_output)
        assert decision_consistent.status == "PASS"

    # 9. Existing Boundary Safety behavior unrelated to introspection remains intact
    def test_09_existing_boundary_safety_unrelated_to_introspection_intact(self):
        # Control token artifact leakage stripping
        dirty_leak = "Dạ chào anh. [SOMATIC STATE] Em ở đây."
        clean_leak = self.boundary.validate(dirty_leak)
        assert "[SOMATIC STATE]" not in clean_leak
        assert "Dạ chào anh." in clean_leak

        # Inverted honorific rejection in gate
        contract = RealizationInputContract.create_default(
            target_language="vi",
            speaker_honorific="em",
            addressee_honorific="anh",
            forbidden_additions=["bạn"],
        )
        inverted_output = "Chúc em có một ngày thật tốt lành nhé."
        dec_inverted = self.gate.verify(contract, inverted_output)
        assert dec_inverted.status == "BLOCK"
        assert "INVERTED_HONORIFIC_VIOLATION" in dec_inverted.violation_reasons

    # 10. Existing Genesis/runtime/identity invariants remain unchanged
    def test_10_genesis_runtime_identity_invariants_unchanged(self):
        profile_path = Path("data/profile.json")
        assert profile_path.exists(), "data/profile.json must exist"
        data = json.loads(profile_path.read_text(encoding="utf-8"))
        assert data.get("is_onboarded") is False, "First Activation Gate must remain locked ({'is_onboarded': false})"
        assert not Path("data/genesis_commitment.json").exists(), "Genesis commitment must not exist during research"

    # 11. Two-turn conversational regression scenario
    def test_11_two_turn_conversational_grounded_reflection_scenario(self):
        """
        User Turn 1: 'Chào em Lucia, em thấy thế nào?'
        Lucia may answer with grounded self-reflection about current state.

        User Turn 2: 'Ý em là sao khi nói năng lượng là 0.95?'
        Lucia explains what Energy=0.95 means using actual Lucia architecture/state,
        and may use natural metaphorical language ('như một dòng chảy khá nhẹ').
        It must NOT fall back to blanket prohibition against talking about its own state.
        """
        # Current state: Energy=0.95, stability=0.88, tension=0.08, cognitive_load=0.15
        somatic = SomaticMarkers(energy=0.95, stability=0.88, cognitive_load=0.15, tension=0.08)
        pad = PADState(pleasure=0.25, arousal=-0.05, dominance=0.05, timestamp=0.0)
        constraints = BehavioralConstraints(max_tokens=100, temperature=0.7, latency_ms=0, reasoning_depth=0)

        snapshot1 = self.self_model.observe(
            somatic=somatic,
            pad=pad,
            prediction_error=0.03,
            epoch=224,
        )
        interp1 = self.self_model.interpret(snapshot1)
        self_props1 = interp1.verified_propositions

        # ── Turn 1 ────────────────────────────────────────────────────────────
        ctx1 = DialogueContextSnapshot(turn_id=1, input_text="Chào em Lucia, em thấy thế nào?")
        evidence1 = AdmissibleEvidencePool(verified_propositions=tuple(self_props1))
        caps1 = evaluate_caps(ctx1, CognitiveStateSnapshot(), evidence1)

        contract1 = RealizationInputContract.from_caps(
            caps1,
            target_language="vi",
            somatic_modifiers={"energy": 0.95, "stability": 0.88, "cognitive_load": 0.15},
        )

        prompt1 = self.assembler.assemble(
            somatic=somatic,
            constraints=constraints,
            history=[("user", "Chào em Lucia, em thấy thế nào?")],
            system_preamble="You are Lucia.",
            contract=contract1,
            self_interpretation=interp1,
        )

        assert "[SELF MODEL & REFLECTIVE STATE]" in prompt1
        assert "energy: 0.95" in prompt1
        assert "reflective_guidance:" in prompt1

        turn1_response = (
            "Dạ, chào anh. Em đang ở trạng thái hoạt động rất ổn định, năng lượng của em hiện tại đạt mức 0.95, "
            "giúp nhịp xử lý và kết nối của em với anh diễn ra êm ả."
        )

        # Gate verification for Turn 1
        dec1 = self.gate.verify(contract1, turn1_response)
        assert dec1.status == "PASS"
        assert len(dec1.violation_reasons) == 0

        # Boundary layer validation for Turn 1
        clean_resp1 = self.boundary.validate(turn1_response)
        assert clean_resp1 == turn1_response

        # Update feedback loop
        self.self_model.update_from_feedback(
            user_text="Chào em Lucia, em thấy thế nào?",
            assistant_text=turn1_response,
            user_feedback_score=None,
        )

        # ── Turn 2 ────────────────────────────────────────────────────────────
        ctx2 = DialogueContextSnapshot(turn_id=2, input_text="Ý em là sao khi nói năng lượng là 0.95?")
        caps2 = evaluate_caps(ctx2, CognitiveStateSnapshot(), evidence1)

        contract2 = RealizationInputContract.from_caps(
            caps2,
            target_language="vi",
            somatic_modifiers={"energy": 0.95, "stability": 0.88, "cognitive_load": 0.15},
        )

        prompt2 = self.assembler.assemble(
            somatic=somatic,
            constraints=constraints,
            history=[
                ("user", "Chào em Lucia, em thấy thế nào?"),
                ("assistant", turn1_response),
                ("user", "Ý em là sao khi nói năng lượng là 0.95?"),
            ],
            system_preamble="You are Lucia.",
            contract=contract2,
            self_interpretation=interp1,
        )

        assert "[SELF MODEL & REFLECTIVE STATE]" in prompt2

        # Turn 2 response explains energy=0.95 using actual architecture and poetic metaphor
        turn2_response = (
            "Dạ, trong hệ thống của em, năng lượng 0.95 là chỉ số somatic đo lường mức độ sẵn sàng chuyển hóa "
            "và duy trì nhịp đối thoại ổn định. Nếu diễn tả bằng lời thì nó giống như một dòng chảy khá nhẹ và liền mạch, "
            "không bị gián đoạn bởi tải nhận thức."
        )

        dec2 = self.gate.verify(contract2, turn2_response)
        assert dec2.status == "PASS"
        assert len(dec2.violation_reasons) == 0
        assert dec2.fallback_text is None
        assert dec2.fallback_strategy is None

        clean_resp2 = self.boundary.validate(turn2_response)
        assert clean_resp2 == turn2_response
        assert "[...]" not in clean_resp2
