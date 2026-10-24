"""
tests/unit/test_increment4_realization_deescalation.py

Unit tests for P23-D Increment 4: Realization Boundary De-escalation + Prompt Hierarchy Re-Anchoring.
Tests A through G.
"""

from __future__ import annotations

import json
from pathlib import Path
import numpy as np
import pytest

from src.core.cognition.self_model import ReflectiveSelfModel
from src.core.communication.caps import CommunicativeAct
from src.core.knowledge.bootstrap import get_verified_architecture_concepts
from src.core.knowledge.proposition import Concept
from src.core.language.contract import RealizationInputContract
from src.core.models import BehavioralConstraints, PADState, SomaticMarkers
from src.core.orchestrator.prompt_assembler import PromptAssembler


class TestIncrement4RealizationDeescalation:
    @pytest.fixture
    def setup_components(self):
        assembler = PromptAssembler()
        self_model = ReflectiveSelfModel()
        somatic = SomaticMarkers(energy=0.85, stability=0.90, cognitive_load=0.20, tension=0.10)
        pad = PADState(pleasure=0.25, arousal=-0.05, dominance=0.05, timestamp=0.0)
        constraints = BehavioralConstraints(latency_ms=0, reasoning_depth=0, max_tokens=600, temperature=0.7)
        return assembler, self_model, somatic, pad, constraints

    # Test A — Technical explanation prompt
    def test_a_technical_explanation_prompt(self, setup_components):
        assembler, self_model, somatic, pad, constraints = setup_components
        snapshot = self_model.observe(somatic, pad)
        interp = self_model.interpret(snapshot)
        concepts = get_verified_architecture_concepts()

        contract = RealizationInputContract.create_default(
            target_language="vi",
            act=CommunicativeAct.EXPLAIN_CONCEPT,
            focus_argument="ent:lucia_architecture",
            conversational_obligation="FULFILL_CONCEPT_EXPLANATION",
        )

        echo_vec = np.zeros(64, dtype=np.float32)

        prompt = assembler.assemble(
            somatic=somatic,
            constraints=constraints,
            history=[("user", "Giải thích toàn bộ kiến trúc Lucia cho anh.")],
            system_preamble="You are Lucia.",
            contract=contract,
            knowledge_concepts=concepts,
            self_interpretation=interp,
            echo_vector=echo_vec,
        )

        assert isinstance(prompt, str)
        # 1. Relevant verified knowledge present
        assert "[GROUNDED KNOWLEDGE]" in prompt
        assert "Lucia Technical Architecture" in prompt
        assert "Kiến trúc Kỹ thuật Lucia" in prompt

        # 2. Reflective metaphors suppressed
        assert "như một dòng chảy khá nhẹ" not in prompt
        assert "metaphorical_affinities:" not in prompt

        # 3. Raw somatic telemetry not prominent (fenced compact representation)
        assert "stability: 0.900000" not in prompt
        assert "<internal_somatic" in prompt

        # 4. Irrelevant memory echo absent
        assert "[MEMORY ECHO]" not in prompt
        assert "echo_0:" not in prompt

        # 5. Final task instruction present near generation boundary
        assert "Chỉ đạo thực hiện:" in prompt
        pos_knowledge = prompt.find("[GROUNDED KNOWLEDGE]")
        pos_directives = prompt.find("[COMMUNICATIVE DIRECTIVES]")
        pos_conv = prompt.find("[CONVERSATION]")
        assert pos_knowledge < pos_directives < pos_conv

    # Test B — Relevant memory
    def test_b_relevant_memory_serialized(self, setup_components):
        assembler, _, somatic, _, constraints = setup_components
        relevant_mem = [
            "Anh từng chia sẻ về dự án nghiên cứu cấu trúc nhận thức.",
            "Cuộc trao đổi sâu về cơ chế dự đoán sai số active inference.",
        ]

        prompt = assembler.assemble(
            somatic=somatic,
            constraints=constraints,
            history=[("user", "Em còn nhớ chuyện hôm trước không?")],
            system_preamble="You are Lucia.",
            relevant_memory=relevant_mem,
        )

        assert isinstance(prompt, str)
        assert "[RELEVANT MEMORY]" in prompt
        assert "Anh từng chia sẻ về dự án nghiên cứu cấu trúc nhận thức." in prompt
        assert "Cuộc trao đổi sâu về cơ chế dự đoán sai số active inference." in prompt

    # Test C — No relevant memory: 64-line raw memory echo is omitted
    def test_c_no_relevant_memory_echo_omitted(self, setup_components):
        assembler, _, somatic, _, constraints = setup_components
        contract = RealizationInputContract.create_default(
            target_language="vi",
            act=CommunicativeAct.EXPLAIN_CONCEPT,
            focus_argument="ent:lucia_architecture",
        )
        echo_vec = np.ones(64, dtype=np.float32) * 0.001

        prompt = assembler.assemble(
            somatic=somatic,
            constraints=constraints,
            history=[("user", "Kiến trúc gồm những gì?")],
            system_preamble="You are Lucia.",
            contract=contract,
            echo_vector=echo_vec,
            relevant_memory=None,
        )

        assert isinstance(prompt, str)
        assert "[MEMORY ECHO]" not in prompt
        assert "echo_0:" not in prompt
        assert "echo_63:" not in prompt

    # Test D — Negative prompt removal
    def test_d_negative_prompt_removal(self, setup_components):
        assembler, self_model, somatic, pad, constraints = setup_components
        snapshot = self_model.observe(somatic, pad)
        interp = self_model.interpret(snapshot)

        contract = RealizationInputContract.create_default(
            target_language="vi",
            act=CommunicativeAct.EXPLAIN_CONCEPT,
            focus_argument="ent:lucia_architecture",
            conversational_obligation="FULFILL_CONCEPT_EXPLANATION",
        )

        prompt = assembler.assemble(
            somatic=somatic,
            constraints=constraints,
            history=[("user", "Vậy bắt đầu đi.")],
            system_preamble="You are Lucia.",
            contract=contract,
            self_interpretation=interp,
        )

        assert isinstance(prompt, str)
        # Verify candidate output phrases are eliminated
        assert "('vâng, bắt đầu thôi')" not in prompt
        assert "tránh 'Em đang xử lý" not in prompt
        assert "trò chơi/game" not in prompt
        assert "ví dụ: 'Em biết phần X" not in prompt

    # Test E — Vietnamese concept material alongside English technical identifiers
    def test_e_vietnamese_concept_material(self):
        concepts = get_verified_architecture_concepts()
        assert len(concepts) >= 6

        lucia_arch = next(c for c in concepts if c.id == "concept:lucia_architecture")
        assert lucia_arch.name == "Lucia Technical Architecture"
        assert "vietnamese_name" in lucia_arch.properties
        assert lucia_arch.properties["vietnamese_name"] == "Kiến trúc Kỹ thuật Lucia"
        assert "definition_vi" in lucia_arch.properties
        assert "Kiến trúc Whole Brain 20-Watt" in lucia_arch.properties["definition_vi"]

        perception = next(c for c in concepts if c.id == "concept:arch_perception")
        assert perception.name == "Perception & Sensory Ingress Subsystem"
        assert perception.properties["vietnamese_name"] == "Phân hệ Tiếp nhận Cảm giác & Ngôn ngữ"

        limbic = next(c for c in concepts if c.id == "concept:arch_limbic_affect")
        assert limbic.properties["vietnamese_name"] == "Phân hệ Động lực Cảm xúc Biên duyên"

        cognition = next(c for c in concepts if c.id == "concept:arch_cognition")
        assert cognition.properties["vietnamese_name"] == "Phân hệ Lõi Nhận thức & Lập luận"

        memory = next(c for c in concepts if c.id == "concept:arch_memory")
        assert memory.properties["vietnamese_name"] == "Phân hệ Ký ức Liên tưởng & Động lực Quan hệ"

        realization = next(c for c in concepts if c.id == "concept:arch_realization")
        assert realization.properties["vietnamese_name"] == "Phân hệ Hiện thực hóa Ngôn ngữ & Cổng Semantic"

    # Test F — Perspective instruction without persona prose
    def test_f_perspective_instruction_without_persona_prose(self, setup_components):
        assembler, _, somatic, _, constraints = setup_components
        contract = RealizationInputContract.create_default(
            target_language="vi",
            act=CommunicativeAct.EXPLAIN_CONCEPT,
            focus_argument="ent:lucia_architecture",
        )

        prompt = assembler.assemble(
            somatic=somatic,
            constraints=constraints,
            history=[("user", "Giải thích kiến trúc")],
            system_preamble="You are Lucia.",
            contract=contract,
        )

        assert isinstance(prompt, str)
        # Perspective anchor present
        assert "Góc nhìn: Tự xưng là 'em', gọi người dùng là 'anh'" in prompt
        # Persona monologue preambles must NOT be present
        assert "Em là Lucia. Em trả lời trực tiếp cho anh như sau:" not in prompt

    # Test G — Genesis bit-exact check
    def test_g_genesis_gate_locked(self):
        profile_path = Path("data/profile.json")
        assert profile_path.exists()
        raw = profile_path.read_text(encoding="utf-8").strip()
        data = json.loads(raw)
        assert data == {"is_onboarded": False} or data == {"is_onboarded": False}
        assert data.get("is_onboarded") is False
        assert raw == '{"is_onboarded": false}'
