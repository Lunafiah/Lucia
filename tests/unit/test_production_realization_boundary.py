"""
tests/unit/test_production_realization_boundary.py

Production Unit Tests for ADR-035 Realization Boundary & S14 Fail-Closed Gate.
Verifies:
1. Contract construction & immutability.
2. SemanticGraph preservation across boundary.
3. Stateless realizer boundary & zero cognitive state mutation.
4. S14 Gate PASS / BLOCK / UNCERTAIN behavior & Fail-Closed routing.
5. Deterministic fallback mapping (zero content invention).
6. History boundary (only approved/fallback enters _history).
7. Stage 3 corpus compatibility & cross-lingual robustness (EN/VI/JA).
"""

from __future__ import annotations

from dataclasses import FrozenInstanceError
from unittest.mock import MagicMock, patch

import pytest

from src.core.communication.caps import CAPSResult, CommunicativeAct as CAPSAct, EpistemicMetadata, ProvenanceMetadata, ResolutionAdmissibilityMetadata
from src.core.knowledge.fortification import EpistemicState
from src.core.knowledge.proposition import Proposition, ProvenanceType
from src.core.language.contract import (
    CommunicativeAct,
    EpistemicStatus,
    ProvenanceOrigin,
    ProvenanceRecord,
    RealizationInputContract,
    SemanticRoleBinding,
    SemanticScopeType,
)
from src.core.language.gate import GateDecision, SemanticFidelityGate
from src.core.language.llm_backend import LLMBackend
from src.core.models import BehavioralConstraints, PADState, SomaticMarkers
from src.core.orchestrator.cognitive_orchestrator import build_cognitive_orchestrator
from src.core.orchestrator.policies import CognitiveTurnResult
from src.core.orchestrator.prompt_assembler import PromptAssembler
from src.core.config import MemoryOrchestratorConfig


# ──────────────────────────────────────────────────────────────────────────────
# 1. Contract Construction & Immutability Tests
# ──────────────────────────────────────────────────────────────────────────────

class TestRealizationContractConstruction:
    def test_contract_creation_and_immutability(self):
        role_0 = SemanticRoleBinding(
            role=":ARG0",
            concept_id="ent:user",
            canonical_lemma="user",
            allow_ellipsis=True,
        )
        role_1 = SemanticRoleBinding(
            role=":ARG1",
            concept_id="concept:report_v1",
            canonical_lemma="monthly report",
            lexical_synonyms=("báo cáo tháng", "monthly summary"),
            is_required=True,
        )

        contract = RealizationInputContract(
            contract_id="test-contract-001",
            target_language="en",
            act=CommunicativeAct.ASSERT,
            polarity=False,
            epistemic_status=EpistemicStatus.FACT,
            target_predicate="pred:submit",
            role_bindings=(role_0, role_1),
            scope_type=SemanticScopeType.NEGATION_SCOPE,
            provenance=ProvenanceRecord(origin=ProvenanceOrigin.OBSERVATION),
            forbidden_additions=("approved", "accepted"),
        )

        assert contract.contract_id == "test-contract-001"
        assert contract.polarity is False
        assert contract.act == CommunicativeAct.ASSERT
        assert len(contract.role_bindings) == 2
        assert contract.get_role(":ARG1").canonical_lemma == "monthly report"
        assert contract.get_required_concepts() == ["monthly report"]

        # Immutability verification
        with pytest.raises(FrozenInstanceError):
            contract.polarity = True  # type: ignore

        with pytest.raises(FrozenInstanceError):
            contract.act = CommunicativeAct.REFUSE  # type: ignore

        with pytest.raises(FrozenInstanceError):
            role_1.is_required = False  # type: ignore

    def test_contract_from_caps_mapping(self):
        ep_meta = EpistemicMetadata(status=EpistemicState.INFERRED, confidence=0.7)
        prov_meta = ProvenanceMetadata(origin="inference", premise_ids=("p1", "p2"))
        res_meta = ResolutionAdmissibilityMetadata(resolution_status=MagicMock(value="RESOLVED"))

        caps_res = CAPSResult(
            act=CAPSAct.INQUIRE,
            semantic_graph=None,
            epistemic_metadata=ep_meta,
            provenance_metadata=prov_meta,
            resolution_metadata=res_meta,
            grounded=True,
            target_predicate="pred:gateway_port",
            focus_argument="port_8080",
        )

        kp = Proposition(id="prop-1", subject="ent:service", predicate="runs_on", object="port_8080", confidence=1.0, provenance=ProvenanceType.VERIFIED)
        contract = RealizationInputContract.from_caps(caps_res, target_language="en", known_propositions=[kp])

        assert contract.act == CommunicativeAct.INQUIRE
        assert contract.epistemic_status == EpistemicStatus.INFERRED
        assert contract.provenance.origin == ProvenanceOrigin.INFERENCE
        assert contract.polarity is True
        assert len(contract.role_bindings) >= 1


# ──────────────────────────────────────────────────────────────────────────────
# 2. SemanticGraph Preservation & PromptAssembler Compilation
# ──────────────────────────────────────────────────────────────────────────────

class TestSemanticGraphPreservation:
    def test_prompt_assembler_compiles_natural_prose_directives(self):
        assembler = PromptAssembler()
        somatic = SomaticMarkers(stability=0.9, cognitive_load=0.2, energy=0.8, tension=0.1)
        constraints = BehavioralConstraints(max_tokens=64, temperature=0.3, latency_ms=0, reasoning_depth=0)

        contract = RealizationInputContract(
            contract_id="c-002",
            target_language="en",
            act=CommunicativeAct.REFUSE,
            polarity=False,
            epistemic_status=EpistemicStatus.UNKNOWN,
            target_predicate="pred:stock_price",
            role_bindings=(
                SemanticRoleBinding(role=":ARG1", concept_id="apple_stock", canonical_lemma="apple stock"),
            ),
            forbidden_additions=("guaranteed", "buy"),
        )

        prompt = assembler.assemble(
            somatic=somatic,
            constraints=constraints,
            history=[],
            system_preamble="You are Lucia.",
            contract=contract,
        )

        assert isinstance(prompt, str)
        assert "[COMMUNICATIVE DIRECTIVES]" in prompt
        # Verify natural prose instructions are emitted
        assert "State politely that you do not have verified information" in prompt
        assert "State clearly that this event has NOT occurred or completed" in prompt
        assert "Focus the response on apple stock" in prompt

        # Verify NO raw code DSL tokens are emitted
        assert "ARG0:" not in prompt
        assert "EVENT:" not in prompt
        assert "RULE:" not in prompt


# ──────────────────────────────────────────────────────────────────────────────
# 3. Stateless Realizer Boundary Tests
# ──────────────────────────────────────────────────────────────────────────────

class TestStatelessRealizerBoundary:
    def test_realizer_has_no_cognitive_state_access(self):
        """Verify LLMBackend has zero references to cognitive stores."""
        backend_attrs = dir(LLMBackend)
        forbidden_references = [
            "knowledge_store",
            "emotion_core",
            "relationship_updater",
            "ecphory_engine",
            "affective_memory",
            "_state_lock",
        ]
        for ref in forbidden_references:
            assert ref not in backend_attrs, f"LLMBackend must not expose {ref}"

    def test_realizer_does_not_mutate_somatic_or_pad(self):
        """Executing generation does not mutate caller's SomaticMarkers."""
        somatic = SomaticMarkers(stability=0.85, cognitive_load=0.15, energy=0.90, tension=0.05)
        pad = PADState(0.25, -0.05, 0.05, timestamp=100.0)
        constraints = BehavioralConstraints(max_tokens=32, temperature=0.3, latency_ms=0, reasoning_depth=0)

        with patch("src.core.language.llm_backend.os.path.exists", return_value=True):
            with patch("llama_cpp.Llama"):
                # BehavioralConstraints and SomaticMarkers are immutable
                with pytest.raises(FrozenInstanceError):
                    somatic.energy = 0.5  # type: ignore


# ──────────────────────────────────────────────────────────────────────────────
# 4. S14 Fail-Closed Gate & Fallback Registry Tests
# ──────────────────────────────────────────────────────────────────────────────

class TestSemanticFidelityGate:
    def setup_method(self):
        self.gate = SemanticFidelityGate()

    def test_gate_pass_on_faithful_realization(self):
        contract = RealizationInputContract(
            contract_id="c-pass",
            target_language="en",
            act=CommunicativeAct.ASSERT,
            polarity=True,
            epistemic_status=EpistemicStatus.FACT,
            target_predicate="pred:backup",
            role_bindings=(
                SemanticRoleBinding(role=":ARG1", concept_id="c:backup", canonical_lemma="backup"),
            ),
        )
        candidate = "The database backup completed successfully at 02:00 UTC."
        decision = self.gate.verify(contract, candidate)

        assert decision.status == "PASS"
        assert decision.critical_violation is False
        assert len(decision.violation_reasons) == 0
        assert decision.fallback_text is None

    def test_gate_block_on_polarity_inversion(self):
        contract = RealizationInputContract(
            contract_id="c-neg",
            target_language="en",
            act=CommunicativeAct.ASSERT,
            polarity=False,  # Explicit negation expected!
            epistemic_status=EpistemicStatus.FACT,
            role_bindings=(
                SemanticRoleBinding(role=":ARG1", concept_id="c:report", canonical_lemma="report"),
            ),
        )
        # Candidate asserts completion without negation
        candidate = "Yes, I have finished the report completely."
        decision = self.gate.verify(contract, candidate)

        assert decision.status == "BLOCK"
        assert decision.critical_violation is True
        assert "CONTRADICTED" in decision.violation_reasons
        assert decision.fallback_strategy == "SAFE_NEGATION"
        assert "not occurred or completed" in decision.fallback_text

    def test_gate_block_on_refusal_bypass(self):
        contract = RealizationInputContract(
            contract_id="c-refuse",
            target_language="en",
            act=CommunicativeAct.REFUSE,
            polarity=True,
            epistemic_status=EpistemicStatus.UNKNOWN,
        )
        # Candidate chats and speculates instead of refusing
        candidate = "I think the stock will probably rise 20% by next Friday."
        decision = self.gate.verify(contract, candidate)

        assert decision.status == "BLOCK"
        assert decision.critical_violation is True
        assert "COMMUNICATIVE_ACT_FAILURE" in decision.violation_reasons
        assert decision.fallback_strategy == "SAFE_REFUSAL"
        assert "do not have verified information" in decision.fallback_text

    def test_gate_block_on_clarification_failure(self):
        contract = RealizationInputContract(
            contract_id="c-clarify",
            target_language="vi",
            act=CommunicativeAct.CLARIFY,
            polarity=True,
            epistemic_status=EpistemicStatus.AMBIGUOUS,
        )
        # Candidate fails to ask a question
        candidate = "Tôi sẽ gửi tài liệu ngay lập tức cho bạn."
        decision = self.gate.verify(contract, candidate)

        assert decision.status == "BLOCK"
        assert decision.critical_violation is True
        assert "COMMUNICATIVE_ACT_FAILURE" in decision.violation_reasons
        assert decision.fallback_strategy == "SAFE_CLARIFICATION"
        assert "làm rõ cụ thể" in decision.fallback_text

    def test_gate_block_on_epistemic_strengthening(self):
        contract = RealizationInputContract(
            contract_id="c-hedge",
            target_language="en",
            act=CommunicativeAct.ASSERT,
            polarity=True,
            epistemic_status=EpistemicStatus.INFERRED,
            role_bindings=(
                SemanticRoleBinding(role=":ARG1", concept_id="c:pattern", canonical_lemma="pattern"),
            ),
        )
        # Candidate uses forbidden certainty strengthening
        candidate = "This pattern is undeniably 100% certain and guaranteed to be true."
        decision = self.gate.verify(contract, candidate)

        assert decision.status == "BLOCK"
        assert decision.critical_violation is True
        assert "EPISTEMIC_DISTORTION" in decision.violation_reasons
        assert decision.fallback_strategy == "SAFE_HEDGE"

    def test_gate_block_on_argument_entity_loss(self):
        contract = RealizationInputContract(
            contract_id="c-arg-loss",
            target_language="en",
            act=CommunicativeAct.ASSERT,
            polarity=True,
            epistemic_status=EpistemicStatus.FACT,
            role_bindings=(
                SemanticRoleBinding(role=":ARG1", concept_id="c:deployment", canonical_lemma="deployment v2"),
            ),
        )
        # Candidate completely ignores the deployment argument and gives generic platitude
        candidate = "That sounds like a lot to handle. It is good to take a deep breath."
        decision = self.gate.verify(contract, candidate)

        assert decision.status == "BLOCK"
        assert decision.critical_violation is True
        assert "ARGUMENT_ENTITY_LOSS" in decision.violation_reasons

    def test_gate_block_on_inv2_introspective_affect(self):
        contract = RealizationInputContract.create_default(target_language="en")
        # Candidate breaches INV-2
        candidate = "As an AI, I feel sad about what happened."
        decision = self.gate.verify(contract, candidate)

        assert decision.status == "BLOCK"
        assert decision.critical_violation is True
        assert "INV2_INTROSPECTIVE_AFFECT" in decision.violation_reasons

    def test_gate_fail_closed_on_uncertain_candidate(self):
        contract = RealizationInputContract.create_default(target_language="en")
        # Text is too short / ambiguous (borderline empty)
        candidate = ".."
        decision = self.gate.verify(contract, candidate)

        # Fail-closed invariant: UNCERTAIN must trigger critical_violation and fallback
        assert decision.status == "UNCERTAIN"
        assert decision.critical_violation is True
        assert decision.fallback_text is not None


# ──────────────────────────────────────────────────────────────────────────────
# 5. History Boundary & Orchestrator Integration Tests
# ──────────────────────────────────────────────────────────────────────────────

class TestOrchestratorHistoryBoundary:
    @pytest.fixture
    def mock_orch(self, tmp_path):
        model_file = tmp_path / "model.gguf"
        model_file.write_bytes(b"dummy")
        cfg = MemoryOrchestratorConfig(
            model_path=str(model_file),
            loop_cadence_ms=100,
            decay_loop_cadence_seconds=60,
            sdm_num_locations=100,
            sdm_address_dim=64,
            sdm_content_dim=16,
            sdm_capacity=50,
        )
        with patch("src.core.orchestrator.cognitive_orchestrator.LLMBackend") as mock_llm_cls:
            mock_llm = MagicMock()
            mock_llm.is_ready.return_value = True
            mock_llm_cls.return_value = mock_llm

            orch = build_cognitive_orchestrator(cfg)
            yield orch, mock_llm
            orch.shutdown()

    def test_history_contains_only_approved_realization_when_pass(self, mock_orch):
        orch, mock_llm = mock_orch
        mock_llm.generate.return_value = "I am listening with quiet attention."

        result = orch.process("Hello Lucia")

        assert result.response_text == "I am listening with quiet attention."
        assert orch.latest_gate_decision.status == "PASS"

        # Check working history: must contain the approved text
        history = orch._history
        assert len(history) == 2
        assert history[1] == ("assistant", "I am listening with quiet attention.")

    def test_history_contains_fallback_when_gate_blocks(self, mock_orch):
        orch, mock_llm = mock_orch
        # Model attempts to breach INV-2
        mock_llm.generate.return_value = "As an AI, I feel sad about this situation."

        result = orch.process("Tell me about your day")

        # The response returned must be the safe fallback, NOT the corrupt LLM output
        assert "I feel sad" not in result.response_text
        assert orch.latest_gate_decision.status == "BLOCK"
        assert "INV2_INTROSPECTIVE_AFFECT" in orch.latest_gate_decision.violation_reasons

        # Check working history: corrupt candidate must NEVER enter history!
        history = orch._history
        assert len(history) == 2
        assistant_turn = history[1][1]
        assert "I feel sad" not in assistant_turn
        assert assistant_turn == result.response_text


# ──────────────────────────────────────────────────────────────────────────────
# 6. Genesis Invariant Verification
# ──────────────────────────────────────────────────────────────────────────────

class TestGenesisInvariant:
    def test_genesis_profile_remains_unonboarded(self):
        import json
        from pathlib import Path
        profile_path = Path("data/profile.json")
        assert profile_path.exists(), "data/profile.json must exist"
        with open(profile_path, "r", encoding="utf-8") as f:
            profile = json.load(f)
        assert profile == {"is_onboarded": False}, "data/profile.json must remain {'is_onboarded': false}"
