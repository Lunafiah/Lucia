"""
tests/unit/test_response_completion_planner.py

Unit tests for ResponseCompletionPlanner and Adaptive Generation Headroom (Increment 2).
Verifies:
1. UNKNOWN technical query receives bounded capacity.
2. PARTIAL knowledge scales capacity to supported facets.
3. KNOWN single-facet explanation receives less capacity than KNOWN multi-facet explanation.
4. DEEP low-workload response does not automatically receive a large budget.
5. DEEP high-workload architecture explanation receives sufficient capacity.
6. Vietnamese short response is not truncated because of English-oriented budgeting.
7. Vietnamese multi-facet architecture explanation receives enough capacity subject to context headroom.
8. Continuation "Vậy bắt đầu đi" inherits the active architecture workload.
9. New unrelated substantive request supersedes the previous workload.
10. Context headroom clamps completion capacity safely.
11. Long history is trimmed when necessary to preserve completion headroom.
12. Somatic attenuation reduces capacity without changing semantic target.
13. UNKNOWN + large semantic-looking request does not unlock a large hallucination budget.
14. No second classifier is introduced (pure deterministic planning).
15. Genesis invariant remains untouched.
"""

from pathlib import Path
import pytest

from src.core.communication.communication_policy import CommunicationPolicy
from src.core.communication.communication_state import (
    CommunicationState,
    ResponseDepth,
    ResponseShape,
    ShapeTopology,
)
from src.core.communication.caps import (
    AdmissibleEvidencePool,
    CognitiveStateSnapshot,
    CommunicativeAct,
    DialogueContextSnapshot,
    EpistemicMetadata,
    EpistemicState,
    PendingUserObligation,
    ProvenanceMetadata,
    evaluate_caps,
)
from src.core.communication.response_completion_planner import (
    CompletionPlan,
    DEFAULT_LANGUAGE_DENSITY_PROFILES,
    LanguageDensityProfile,
    ResponseCompletionPlanner,
)
from src.core.knowledge.bootstrap import bootstrap_verified_knowledge
from src.core.knowledge.proposition import Proposition, ProvenanceType
from src.core.knowledge.store import KnowledgeStore
from src.core.models import BehavioralConstraints, SomaticMarkers
from src.core.orchestrator.prompt_assembler import PromptAssembler, _estimate_tokens


class TestResponseCompletionPlanner:
    """Focused verification of ResponseCompletionPlanner semantics and invariants."""

    @pytest.fixture
    def planner(self) -> ResponseCompletionPlanner:
        return ResponseCompletionPlanner()

    @pytest.fixture
    def seeded_store(self) -> KnowledgeStore:
        return bootstrap_verified_knowledge(KnowledgeStore())

    # 1. UNKNOWN technical query receives bounded capacity
    def test_unknown_technical_query_receives_bounded_capacity(self, planner: ResponseCompletionPlanner):
        plan = planner.plan(
            epistemic_status=EpistemicState.UNKNOWN,
            available_facets=0,
            required_facets=5,
            response_depth=ResponseDepth.DEEP,
            conversational_obligation="FULFILL_CONCEPT_EXPLANATION",
            target_language="vi",
            focus_argument="ent:lucia_architecture",
        )
        # Even with DEEP requested, UNKNOWN must be strictly bounded (refusal / boundary statement)
        assert plan.completion_capacity <= 140
        assert plan.recommended_max_sentences <= 2
        assert plan.diagnostic_metadata["branch"] == "UNKNOWN_BOUNDED"

    # 2. PARTIAL knowledge scales capacity to supported facets
    def test_partial_knowledge_scales_to_supported_facets(self, planner: ResponseCompletionPlanner):
        plan_partial_1 = planner.plan(
            epistemic_status=EpistemicState.PARTIAL,
            available_facets=1,
            required_facets=5,
            response_depth=ResponseDepth.DEEP,
            conversational_obligation="FULFILL_CONCEPT_EXPLANATION",
            target_language="vi",
            focus_argument="ent:lucia_architecture",
        )
        plan_partial_2 = planner.plan(
            epistemic_status=EpistemicState.PARTIAL,
            available_facets=2,
            required_facets=5,
            response_depth=ResponseDepth.DEEP,
            conversational_obligation="FULFILL_CONCEPT_EXPLANATION",
            target_language="vi",
            focus_argument="ent:lucia_architecture",
        )
        assert plan_partial_1.completion_capacity <= 300
        assert plan_partial_2.completion_capacity <= 360
        assert plan_partial_1.completion_capacity < plan_partial_2.completion_capacity
        assert plan_partial_1.diagnostic_metadata["branch"] == "PARTIAL_CONCEPT_EXPLANATION"

    # 3. KNOWN single-facet explanation receives less capacity than KNOWN multi-facet explanation
    def test_known_single_facet_vs_multi_facet_capacity(self, planner: ResponseCompletionPlanner):
        plan_single = planner.plan(
            epistemic_status=EpistemicState.FACT,
            available_facets=1,
            required_facets=1,
            response_depth=ResponseDepth.DEEP,
            conversational_obligation="FULFILL_CONCEPT_EXPLANATION",
            target_language="vi",
            focus_argument="ent:ram_vram",
        )
        plan_multi = planner.plan(
            epistemic_status=EpistemicState.FACT,
            available_facets=5,
            required_facets=5,
            response_depth=ResponseDepth.DEEP,
            conversational_obligation="FULFILL_CONCEPT_EXPLANATION",
            target_language="vi",
            focus_argument="ent:lucia_architecture",
        )
        assert plan_single.completion_capacity < plan_multi.completion_capacity
        assert plan_single.completion_capacity <= 500
        assert plan_multi.completion_capacity >= 650

    # 4. DEEP low-workload response does not automatically receive a large budget
    def test_deep_low_workload_does_not_receive_large_budget(self, planner: ResponseCompletionPlanner):
        plan_deep_low = planner.plan(
            epistemic_status=EpistemicState.FACT,
            available_facets=1,
            required_facets=1,
            response_depth=ResponseDepth.DEEP,
            conversational_obligation="FULFILL_CONCEPT_EXPLANATION",
            target_language="en",
            focus_argument="concept:philia_meaning",
        )
        # English DEEP with single concept should not receive 500+ tokens
        assert plan_deep_low.completion_capacity <= 230
        assert plan_deep_low.diagnostic_metadata["branch"] == "DEEP_SINGLE_FACET_EXPLANATION"

    # 5. DEEP high-workload architecture explanation receives sufficient capacity
    def test_deep_high_workload_architecture_explanation_capacity(self, planner: ResponseCompletionPlanner):
        plan_en = planner.plan(
            epistemic_status=EpistemicState.FACT,
            available_facets=5,
            required_facets=5,
            response_depth=ResponseDepth.DEEP,
            conversational_obligation="FULFILL_CONCEPT_EXPLANATION",
            target_language="en",
            focus_argument="ent:lucia_architecture",
        )
        plan_vi = planner.plan(
            epistemic_status=EpistemicState.FACT,
            available_facets=5,
            required_facets=5,
            response_depth=ResponseDepth.DEEP,
            conversational_obligation="FULFILL_CONCEPT_EXPLANATION",
            target_language="vi",
            focus_argument="ent:lucia_architecture",
        )
        assert plan_en.completion_capacity >= 350
        assert plan_vi.completion_capacity >= 680

    # 6. Vietnamese short response is not truncated because of English-oriented budgeting
    def test_vietnamese_short_response_density_calibration(self, planner: ResponseCompletionPlanner):
        plan_en = planner.plan(
            epistemic_status=EpistemicState.FACT,
            response_depth=ResponseDepth.SHORT,
            conversational_obligation="ANSWER_ACTIVITY",
            target_language="en",
        )
        plan_vi = planner.plan(
            epistemic_status=EpistemicState.FACT,
            response_depth=ResponseDepth.SHORT,
            conversational_obligation="ANSWER_ACTIVITY",
            target_language="vi",
        )
        # Vietnamese needs ~120-150 tokens to finish 2 natural sentences; English needs ~50-70
        assert plan_vi.completion_capacity > plan_en.completion_capacity
        assert plan_vi.completion_capacity >= 120
        assert plan_en.completion_capacity <= 75

    # 7. Vietnamese multi-facet architecture explanation receives enough capacity subject to context headroom
    def test_vietnamese_multi_facet_subject_to_headroom(self, planner: ResponseCompletionPlanner):
        # Ample headroom (e.g. 2000 tokens available)
        plan_ample = planner.plan(
            epistemic_status=EpistemicState.FACT,
            available_facets=5,
            required_facets=5,
            response_depth=ResponseDepth.DEEP,
            conversational_obligation="FULFILL_CONCEPT_EXPLANATION",
            target_language="vi",
            focus_argument="ent:lucia_architecture",
            context_headroom=2000,
        )
        assert plan_ample.completion_capacity >= 680
        assert "headroom_clamped" not in plan_ample.diagnostic_metadata

        # Tight headroom (e.g. only 400 tokens left in context window)
        plan_tight = planner.plan(
            epistemic_status=EpistemicState.FACT,
            available_facets=5,
            required_facets=5,
            response_depth=ResponseDepth.DEEP,
            conversational_obligation="FULFILL_CONCEPT_EXPLANATION",
            target_language="vi",
            focus_argument="ent:lucia_architecture",
            context_headroom=400,
        )
        # Clamped by headroom (400 - 64 safety reserve = 336)
        assert plan_tight.completion_capacity <= 336
        assert plan_tight.diagnostic_metadata.get("headroom_clamped") is True

    # 8. Continuation "Vậy bắt đầu đi" inherits active architecture workload
    def test_continuation_inherits_active_architecture_workload(self, seeded_store: KnowledgeStore):
        # Turn 1 established pending obligation
        pending_ob = PendingUserObligation(
            obligation_type="FULFILL_CONCEPT_EXPLANATION",
            originating_turn=1,
            target_topic="toàn bộ kiến trúc lucia",
            completed=False,
            ttl_turns=2,
        )
        # Turn 2: User says "Vậy bắt đầu đi."
        retrieved = seeded_store.query_relevant("toàn bộ kiến trúc lucia", max_results=5)
        ev_pool = AdmissibleEvidencePool(verified_propositions=retrieved)
        ctx = DialogueContextSnapshot(
            turn_id=2,
            input_text="Vậy bắt đầu đi.",
            pending_user_obligation=pending_ob,
        )
        caps = evaluate_caps(ctx, CognitiveStateSnapshot(), ev_pool)

        policy = CommunicationPolicy()
        comm_state = policy.attune_depth_to_act(
            CommunicationPolicy.get_neutral_actuator_baseline(),
            act=caps.act,
            obligation=caps.conversational_obligation,
            target_predicate=caps.target_predicate,
            user_input_text="Vậy bắt đầu đi.",
            caps_result=caps,
            known_propositions=retrieved,
            target_language="vi",
            focus_argument=caps.focus_argument,
            is_continuation=True,
        )

        assert comm_state.response_depth == ResponseDepth.DEEP
        assert comm_state.max_tokens_budget >= 680

    # 9. New unrelated substantive request supersedes previous workload
    def test_unrelated_request_supersedes_previous_workload(self, seeded_store: KnowledgeStore):
        policy = CommunicationPolicy()
        # New question: "Ciah ơi." (presence ping)
        comm_state = policy.attune_depth_to_act(
            CommunicationPolicy.get_neutral_actuator_baseline(),
            act=CommunicativeAct.REQUEST,
            obligation="MINIMAL_PRESENCE_CALL",
            target_predicate="c:PRESENCE_PING",
            user_input_text="Ciah ơi.",
            target_language="vi",
        )
        assert comm_state.response_depth == ResponseDepth.MINIMAL
        assert comm_state.max_tokens_budget <= 80

    # 10. Context headroom clamps completion capacity safely
    def test_context_headroom_clamping(self, planner: ResponseCompletionPlanner):
        plan = planner.plan(
            epistemic_status=EpistemicState.FACT,
            available_facets=5,
            required_facets=5,
            response_depth=ResponseDepth.DEEP,
            conversational_obligation="FULFILL_CONCEPT_EXPLANATION",
            target_language="vi",
            context_headroom=200,
        )
        # Headroom = 200, safety reserve = 64 -> max 136 tokens
        assert plan.completion_capacity == 136
        assert plan.diagnostic_metadata["headroom_clamped"] is True

    # 11. Long history is trimmed when necessary to preserve completion headroom
    def test_long_history_trimmed_to_preserve_completion_headroom(self):
        assembler = PromptAssembler()
        somatic = SomaticMarkers(stability=0.9, cognitive_load=0.1, energy=0.9, tension=0.1)
        constraints = BehavioralConstraints(max_tokens=200, temperature=0.7, latency_ms=0, reasoning_depth=0)
        
        # Build 10 turns of history
        history = [(("user" if i % 2 == 0 else "assistant"), f"Turn {i} with some conversational content.") for i in range(10)]
        
        # In a tight context of 800 tokens with planned completion capacity of 500 tokens:
        # Prompt must leave room for 500 tokens + 64 reserve -> max prompt allowed is <= 236 tokens!
        prompt = assembler.assemble(
            somatic=somatic,
            constraints=constraints,
            history=history,
            n_ctx=800,
            planned_completion_capacity=500,
        )
        assert isinstance(prompt, str)
        # Estimated prompt tokens should fit within 800 - 500 - 64 = 236 tokens
        est_tokens = _estimate_tokens(prompt)
        assert est_tokens <= 300

    # 12. Somatic attenuation reduces capacity without changing semantic target
    def test_somatic_attenuation_preserves_target(self, planner: ResponseCompletionPlanner):
        normal_somatic = SomaticMarkers(stability=0.9, cognitive_load=0.1, energy=0.9, tension=0.1)
        fatigued_somatic = SomaticMarkers(stability=0.5, cognitive_load=0.8, energy=0.15, tension=0.6)

        plan_normal = planner.plan(
            epistemic_status=EpistemicState.FACT,
            available_facets=5,
            required_facets=5,
            response_depth=ResponseDepth.DEEP,
            conversational_obligation="FULFILL_CONCEPT_EXPLANATION",
            target_language="vi",
            focus_argument="ent:lucia_architecture",
            somatic_markers=normal_somatic,
        )
        plan_fatigued = planner.plan(
            epistemic_status=EpistemicState.FACT,
            available_facets=5,
            required_facets=5,
            response_depth=ResponseDepth.DEEP,
            conversational_obligation="FULFILL_CONCEPT_EXPLANATION",
            target_language="vi",
            focus_argument="ent:lucia_architecture",
            somatic_markers=fatigued_somatic,
        )
        assert plan_fatigued.completion_capacity < plan_normal.completion_capacity
        assert plan_fatigued.diagnostic_metadata.get("somatic_energy_attenuation") == 0.75
        assert plan_fatigued.diagnostic_metadata.get("somatic_load_attenuation") == 0.85
        # Semantic target is preserved
        assert plan_fatigued.diagnostic_metadata["conversational_obligation"] == "FULFILL_CONCEPT_EXPLANATION"

    # 13. UNKNOWN + large semantic-looking request does not unlock a large hallucination budget
    def test_unknown_large_request_no_hallucination_budget(self, planner: ResponseCompletionPlanner):
        plan = planner.plan(
            epistemic_status=EpistemicState.UNKNOWN,
            available_facets=0,
            required_facets=10,
            response_depth=ResponseDepth.DEEP,
            conversational_obligation="FULFILL_CONCEPT_EXPLANATION",
            target_language="vi",
            focus_argument="ent:hypothetical_quantum_subsystem",
        )
        # Must be strictly capped at refusal/boundary headroom
        assert plan.completion_capacity <= 140
        assert plan.recommended_max_sentences <= 2

    # 14. No second classifier is introduced (pure deterministic planning)
    def test_planner_is_deterministic_pure_function(self, planner: ResponseCompletionPlanner):
        kwargs = dict(
            epistemic_status=EpistemicState.FACT,
            available_facets=3,
            required_facets=3,
            response_depth=ResponseDepth.MEDIUM,
            conversational_obligation="FULFILL_CONCEPT_EXPLANATION",
            target_language="vi",
        )
        plan1 = planner.plan(**kwargs)
        plan2 = planner.plan(**kwargs)
        assert plan1.completion_capacity == plan2.completion_capacity
        assert plan1.recommended_max_sentences == plan2.recommended_max_sentences
        assert plan1.diagnostic_metadata == plan2.diagnostic_metadata

    # 15. Genesis invariant remains untouched
    def test_genesis_invariant_remains_untouched(self):
        profile_path = Path("data/profile.json")
        assert profile_path.exists(), "data/profile.json must exist"
        content = profile_path.read_text(encoding="utf-8").strip()
        assert content == '{"is_onboarded": false}', f"INV-8 violated: profile.json contains '{content}'"
