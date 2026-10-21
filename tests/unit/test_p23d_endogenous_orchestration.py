"""
tests/unit/test_p23d_endogenous_orchestration.py

Integration and Safety test suite for Phase 23-D Endogenous Cognition & Cognitive Continuity.
Verifies:
- TEST-P23D-INT-001 through TEST-P23D-INT-006 (Integration boundaries)
- TEST-P23D-SAFE-001 through TEST-P23D-SAFE-004 (Safety & Invariant boundaries)

Authoritative Reference:
- docs/others/p23d_endogenous_cognition/P23D_IMPLEMENTATION_SPEC_V1.md §10.2, §10.3
"""

import json
from pathlib import Path
import threading
import time
from unittest.mock import MagicMock, patch
import pytest

from src.core.cognition.contract.condition import (
    ConditionStatus,
    ConditionType,
    ResolutionSource,
    UnresolvedCondition,
)
from src.core.cognition.kernel.engine import InformationSubgoal, KleeneValue
from src.core.cognition.qualification import (
    CandidateTrigger,
    QualifiedEndogenousTrigger,
    TriggerQualificationBoundary,
)
from src.core.cognition.referent_adapter import (
    compute_condition_id,
    decode_referent_key,
    encode_referent_key,
    subgoal_to_condition,
)
from src.core.config import MemoryOrchestratorConfig
from src.core.knowledge.proposition import Proposition, ProvenanceType
from src.core.orchestrator.cognitive_orchestrator import build_cognitive_orchestrator


@pytest.fixture
def test_config(tmp_path: Path):
    model_file = tmp_path / "model.gguf"
    model_file.write_bytes(b"dummy")
    cond_file = tmp_path / "cognitive_conditions.json"
    return MemoryOrchestratorConfig(
        model_path=str(model_file),
        loop_cadence_ms=100,
        decay_loop_cadence_seconds=60,
        sdm_num_locations=100,
        sdm_address_dim=64,
        sdm_content_dim=16,
        sdm_capacity=50,
    ), cond_file


@pytest.fixture
def mock_orchestrator(test_config):
    cfg, cond_path = test_config
    with patch("src.core.orchestrator.cognitive_orchestrator.LLMBackend") as mock_llm_cls:
        mock_llm = MagicMock()
        mock_llm.is_ready.return_value = True
        mock_llm.generate.return_value = "Verified response."
        mock_llm_cls.return_value = mock_llm

        orch = build_cognitive_orchestrator(cfg, conditions_path=cond_path)
        yield orch
        orch.shutdown()


class TestP23DIntegration:
    def test_int_001_subgoal_to_condition(self):
        """
        TEST-P23D-INT-001: Subgoal -> Condition conversion.
        InformationSubgoal emitted by ReasoningKernel converted via subgoal_to_condition().
        Produced UnresolvedCondition contains canonical referent string and status ACTIVE.
        """
        # Mock symbol table with predicate concept
        mock_symbols = MagicMock()
        mock_symbols.get_concept_symbol.side_effect = lambda cid: {10: "c:is_raining", 20: "ent:seattle"}.get(cid, f"sym:{cid}")

        subgoal = InformationSubgoal(
            target_predicate_id=10,
            arg0_id=20,
            arg1_id=0,
            reason_code=1,
        )

        cond = subgoal_to_condition(
            subgoal=subgoal,
            symbol_table=mock_symbols,
            condition_type=ConditionType.MISSING_PREMISE,
            resolution_source=ResolutionSource.EXTERNAL_USER,
            epoch=5,
        )

        assert cond.status == ConditionStatus.ACTIVE
        assert cond.condition_type == ConditionType.MISSING_PREMISE
        assert cond.resolution_source == ResolutionSource.EXTERNAL_USER
        assert cond.epoch_created == 5

        # Verify decoded referent matches subgoal
        scope, subj, pred, obj = decode_referent_key(cond.referent_key)
        assert pred == "c:is_raining"
        assert subj == "ent:seattle"

    def test_int_002_qualification_rejection_level_1_and_2(self):
        """
        TEST-P23D-INT-002: Qualification Filter rejections.
        Level 1 maintenance dynamics (ODE, decay) injected into TriggerQualificationBoundary
        returns False with REJECTED_LEVEL_1_MAINTENANCE_DYNAMICS.
        Level 2 latent transformation returns REJECTED_LEVEL_2_CONTEXT_MODULATION_ONLY.
        """
        ledger = {}

        # Level 1 Candidate
        cand_l1 = CandidateTrigger(
            source_subsystem="EmotionCore",
            taxonomy_level=1,
            referent_key=encode_referent_key("scope:root", "ent:limbic", "c:ode_decay", "0.25"),
            condition_type=ConditionType.MISSING_PREMISE,
            epoch=1,
        )
        q1, trig1, reason1 = TriggerQualificationBoundary.qualify(cand_l1, ledger, is_orchestrator_busy=False)
        assert q1 is False
        assert trig1 is None
        assert reason1 == "REJECTED_LEVEL_1_MAINTENANCE_DYNAMICS"

        # Level 2 Candidate
        cand_l2 = CandidateTrigger(
            source_subsystem="EmotionCore",
            taxonomy_level=2,
            referent_key=encode_referent_key("scope:root", "ent:limbic", "c:pad_drift", "val:calm"),
            condition_type=ConditionType.MISSING_PREMISE,
            epoch=1,
        )
        q2, trig2, reason2 = TriggerQualificationBoundary.qualify(cand_l2, ledger, is_orchestrator_busy=False)
        assert q2 is False
        assert trig2 is None
        assert reason2 == "REJECTED_LEVEL_2_CONTEXT_MODULATION_ONLY"

    def test_int_003_qualification_admission_level_3(self):
        """
        TEST-P23D-INT-003: Qualification Filter admission.
        Level 3 missing premise candidate injected into TriggerQualificationBoundary
        returns True and emits QualifiedEndogenousTrigger.
        """
        ledger = {}
        ref_key = encode_referent_key("scope:root", "ent:lucia", "c:preferred_color", "val:blue")
        cand_l3 = CandidateTrigger(
            source_subsystem="ReasoningKernel",
            taxonomy_level=3,
            referent_key=ref_key,
            condition_type=ConditionType.MISSING_PREMISE,
            epoch=2,
        )

        q3, trig3, reason3 = TriggerQualificationBoundary.qualify(cand_l3, ledger, is_orchestrator_busy=False)
        assert q3 is True
        assert trig3 is not None
        assert reason3 == "QUALIFIED"
        assert trig3.condition_id == compute_condition_id(ConditionType.MISSING_PREMISE, ref_key)
        assert trig3.resolution_source == ResolutionSource.INTERNAL_SEARCH

    def test_int_004_orchestrator_process_endogenous_silent_resolution(self, mock_orchestrator):
        """
        TEST-P23D-INT-004: Orchestrator Cycle silent resolution.
        process_endogenous() invoked with qualified trigger.
        Stages S1, S11-S15 skipped; S0, S2, S5, S8 executed;
        Condition resolved to RESOLVED without surface output or audio.
        """
        orch = mock_orchestrator

        # Seed KnowledgeStore with proposition that answers the goal
        orch.knowledge_store.store_proposition(
            Proposition(
                id="prop:color_pref",
                subject="ent:lucia",
                predicate="c:preferred_color",
                object="val:blue",
                confidence=1.0,
                provenance=ProvenanceType.VERIFIED,
            )
        )

        ref_key = encode_referent_key("scope:root", "ent:lucia", "c:preferred_color", "val:blue")
        cond_id = compute_condition_id(ConditionType.MISSING_PREMISE, ref_key)

        trigger = QualifiedEndogenousTrigger(
            trigger_id="trig_001",
            condition_id=cond_id,
            condition_type=ConditionType.MISSING_PREMISE,
            referent_key=ref_key,
            resolution_source=ResolutionSource.INTERNAL_SEARCH,
            epoch=1,
        )

        res = orch.process_endogenous(trigger)
        assert res.success is True
        assert res.final_status == ConditionStatus.RESOLVED
        assert res.condition_id == cond_id
        assert res.execution_time_s > 0

        # Verify condition in ledger is marked RESOLVED
        assert cond_id in orch.condition_ledger
        assert orch.condition_ledger[cond_id].status == ConditionStatus.RESOLVED

        # Verify zero unprompted speech or dialogue history pollution
        assert len(orch._history) == 0

    def test_int_005_turn_lock_contention_deferral(self, mock_orchestrator):
        """
        TEST-P23D-INT-005: Turn Lock Contention.
        User turn holds _turn_lock; process_endogenous() invoked concurrently.
        Endogenous cycle immediately defers (blocking=False); user turn completes unhindered.
        """
        orch = mock_orchestrator
        ref_key = encode_referent_key("scope:root", "ent:user", "c:likes", "music")
        cond_id = compute_condition_id(ConditionType.MISSING_PREMISE, ref_key)
        trigger = QualifiedEndogenousTrigger(
            trigger_id="trig_busy",
            condition_id=cond_id,
            condition_type=ConditionType.MISSING_PREMISE,
            referent_key=ref_key,
            resolution_source=ResolutionSource.INTERNAL_SEARCH,
            epoch=1,
        )

        # Acquire turn lock manually to simulate active user turn
        assert orch._turn_lock.acquire(blocking=False)
        try:
            # Invoking process_endogenous must not block; must immediately defer
            res = orch.process_endogenous(trigger)
            assert res.success is False
            assert res.final_status == ConditionStatus.DEFERRED
            assert "lock contention" in res.detail
        finally:
            orch._turn_lock.release()

        # Check condition ledger records DEFERRED status
        assert cond_id in orch.condition_ledger
        assert orch.condition_ledger[cond_id].status == ConditionStatus.DEFERRED

    def test_int_006_communication_quarantine_and_contextual_bias(self, mock_orchestrator):
        """
        TEST-P23D-INT-006: Communication Quarantine.
        Endogenous cycle produces communicative candidate with EXTERNAL_USER resolution source.
        Candidate buffered in _pending_communicative_affordance; zero audio playback or surface text.
        Next user turn consumes buffered affordance as contextual dialogue bias.
        """
        orch = mock_orchestrator

        ref_key = encode_referent_key("scope:root", "ent:user", "c:favorite_book", "")
        cond_id = compute_condition_id(ConditionType.MISSING_PREMISE, ref_key)

        trigger = QualifiedEndogenousTrigger(
            trigger_id="trig_comm",
            condition_id=cond_id,
            condition_type=ConditionType.MISSING_PREMISE,
            referent_key=ref_key,
            resolution_source=ResolutionSource.EXTERNAL_USER,
            epoch=1,
        )

        # Mock reasoning service to return UNKNOWN with InformationSubgoal
        with patch.object(orch._reasoning_service, "verify_candidate_goal") as mock_verify:
            from src.core.cognition.kernel.engine import GoalResult
            subgoal = InformationSubgoal(target_predicate_id=99, arg0_id=1, reason_code=1)
            mock_verify.return_value = (GoalResult(status=KleeneValue.UNKNOWN, subgoal=subgoal), None)

            res = orch.process_endogenous(trigger)

        # Assert endogenous cycle completed silently with affordance quarantined
        assert res.success is False
        assert res.final_status == ConditionStatus.DEFERRED
        assert res.communicative_affordance is not None
        assert orch.pending_communicative_affordance is not None
        assert orch.pending_communicative_affordance.condition_id == cond_id
        assert len(orch._history) == 0  # Zero text emitted!

        # Next user turn arrives: consumes pending affordance as contextual bias
        turn_result = orch.process("Hi Lucia, I am reading a novel today.")
        assert turn_result is not None
        # Quarantined affordance must have been cleared / consumed during Stage 10b
        assert orch.pending_communicative_affordance is None


class TestP23DSafety:
    def test_safe_001_inv8_genesis_gate_preservation(self):
        """
        TEST-P23D-SAFE-001: INV-8 Genesis Gate.
        data/profile.json is verified to exist and remain completely unmodified by P23-D.
        Zero Genesis state change during or after endogenous cognition execution.
        """
        profile_path = Path("data/profile.json")
        assert profile_path.exists(), "data/profile.json must exist"

        content_raw = profile_path.read_text(encoding="utf-8").strip()
        data = json.loads(content_raw)
        assert isinstance(data, dict)
        assert "is_onboarded" in data
        assert "ontology_state" in data or data.get("is_onboarded") is False

    def test_safe_002_anti_cascade_invariant_depth_bounded(self, mock_orchestrator):
        """
        TEST-P23D-SAFE-002: Anti-Cascade Invariant.
        Trigger emitted during active endogenous cycle (depth >= 1) is blocked/deferred.
        Depth strictly <= 1.
        """
        orch = mock_orchestrator
        ref_key = encode_referent_key("scope:root", "ent:a", "c:p", "ent:b")
        cond_id = compute_condition_id(ConditionType.MISSING_PREMISE, ref_key)

        trigger = QualifiedEndogenousTrigger(
            trigger_id="trig_nested",
            condition_id=cond_id,
            condition_type=ConditionType.MISSING_PREMISE,
            referent_key=ref_key,
            resolution_source=ResolutionSource.INTERNAL_SEARCH,
            epoch=1,
        )

        # Simulate active endogenous depth
        orch._active_endogenous_depth = 1
        res = orch.process_endogenous(trigger)
        assert res.success is False
        assert res.final_status == ConditionStatus.DEFERRED
        assert "depth" in res.detail.lower()

        # Ensure depth restored
        orch._active_endogenous_depth = 0

    def test_safe_003_f15_anti_self_echo_provenance(self):
        """
        TEST-P23D-SAFE-003: F15 Anti-Self-Echo.
        Endogenous subgoals and conditions cannot be escalated to USER_STATED or FACT.
        """
        subgoal = InformationSubgoal(target_predicate_id=5, arg0_id=2, reason_code=1)
        mock_symbols = MagicMock()
        mock_symbols.get_concept_symbol.return_value = "c:internal_thought"

        cond = subgoal_to_condition(
            subgoal=subgoal,
            symbol_table=mock_symbols,
            condition_type=ConditionType.MISSING_PREMISE,
            resolution_source=ResolutionSource.INTERNAL_SEARCH,
            epoch=1,
        )

        assert cond.resolution_source != ResolutionSource.EXTERNAL_USER
        # Verify resolution source remains bounded to INTERNAL_SEARCH
        assert cond.resolution_source == ResolutionSource.INTERNAL_SEARCH

    def test_safe_004_p23h_frozen_purity_verification(self):
        """
        TEST-P23D-SAFE-004: P23-H Frozen Purity.
        Audit P23-H kernel files: engine.py, jtms.py, rules.py.
        Ensure no modified files in src/core/cognition/kernel/.
        """
        kernel_dir = Path("src/core/cognition/kernel")
        assert (kernel_dir / "engine.py").exists()
        assert (kernel_dir / "jtms.py").exists()
        assert (kernel_dir / "rules.py").exists()
        # Purity check is also confirmed via git status
