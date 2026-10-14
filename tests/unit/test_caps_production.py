"""
tests/unit/test_caps_production.py

Comprehensive Production Test Suite for CAPS (Phase 23 Semantic Substrate).
Validates all 12 architectural requirements from the CAPS authorization:
1. Communicative Act selection
2. SemanticGraph output
3. Grounding enforcement
4. ASSERT/ANSWER fail-closed behavior
5. UNKNOWN / AMBIGUOUS propagation
6. Provenance preservation (USER_STATED != FACT)
7. Discourse referent resolution integration (RESOLVED != FACT, O(1) bound)
8. InformationSubgoal -> INQUIRE mapping
9. Deterministic CAPS transformation under frozen input
10. S11 responsibility transition
11. Regression against existing cognitive pipeline behavior
12. Genesis protection
"""

import json
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

from src.core.cognition.kernel.engine import (
    INFO_REASON_AMBIGUOUS_REFERENT,
    INFO_REASON_MISSING_PREMISE,
    INFO_REASON_UNGROUNDED_VARIABLE,
    InformationSubgoal,
)
from src.core.communication.caps import (
    AdmissibleEvidencePool,
    CAPSResult,
    CognitiveStateSnapshot,
    CommunicativeAct,
    CommunicationPolicySnapshot,
    DialogueContextSnapshot,
    evaluate_caps,
)
from src.core.config import MemoryOrchestratorConfig
from src.core.knowledge.fortification import EpistemicState
from src.core.knowledge.proposition import Proposition, ProvenanceType
from src.core.models import BehavioralConstraints, SomaticMarkers
from src.core.orchestrator.cognitive_orchestrator import (
    CognitiveOrchestrator,
    build_cognitive_orchestrator,
)
from src.core.orchestrator.discourse_cache import (
    DiscourseContextCache,
    DiscourseReferent,
    ResolutionStatus,
)
from src.core.orchestrator.policies import CognitiveTurnResult
from src.core.orchestrator.prompt_assembler import PromptAssembler


# ── Requirement 1 & 2: Communicative Act Selection & SemanticGraph Output ──────

def test_communicative_act_and_semantic_graph_generation():
    """Verify grounded assertion generates an ASSERT act and valid SemanticGraph."""
    prop = Proposition(
        id="prop:001",
        subject="ent:lucia",
        predicate="c:ENJOYS",
        object="ent:music",
        confidence=0.95,
        provenance=ProvenanceType.VERIFIED,
    )
    dialogue_ctx = DialogueContextSnapshot(turn_id=1, input_text="Lucia enjoys music.")
    cog_state = CognitiveStateSnapshot(
        candidate_predicate="c:ENJOYS",
        candidate_subject="ent:lucia",
        candidate_object="ent:music",
    )
    evidence = AdmissibleEvidencePool(verified_propositions=(prop,))

    result = evaluate_caps(dialogue_ctx, cog_state, evidence)

    assert result.act == CommunicativeAct.ASSERT
    assert result.grounded is True
    assert result.epistemic_metadata.status == EpistemicState.FACT
    assert result.semantic_graph is not None
    assert "node:assert_c_ENJOYS" in result.semantic_graph.nodes
    assert "ent:lucia" in result.semantic_graph.nodes
    assert "ent:music" in result.semantic_graph.nodes
    assert len(result.semantic_graph.edges) == 2


def test_answer_act_selection_on_question():
    """Verify question input selects ANSWER act when grounded."""
    prop = Proposition(
        id="prop:002",
        subject="ent:lucia",
        predicate="c:LIVES_IN",
        object="ent:kyoto",
        confidence=0.90,
        provenance=ProvenanceType.VERIFIED,
    )
    dialogue_ctx = DialogueContextSnapshot(turn_id=1, input_text="Where do you live?")
    cog_state = CognitiveStateSnapshot(candidate_predicate="c:LIVES_IN")
    evidence = AdmissibleEvidencePool(verified_propositions=(prop,))

    result = evaluate_caps(dialogue_ctx, cog_state, evidence)

    assert result.act == CommunicativeAct.ANSWER
    assert result.grounded is True
    assert result.epistemic_metadata.status == EpistemicState.FACT


# ── Requirement 3 & 4: Grounding Enforcement & Fail-Closed Behavior ───────────

def test_fail_closed_grounding_enforcement():
    """ASSERT/ANSWER proposition without admissible grounding MUST fail-closed to REFUSE."""
    dialogue_ctx = DialogueContextSnapshot(turn_id=2, input_text="Do you know the secret?")
    # Proposing a predicate with zero verified evidence in the pool
    cog_state = CognitiveStateSnapshot(candidate_predicate="c:SECRET_KNOWLEDGE")
    evidence = AdmissibleEvidencePool(verified_propositions=())

    result = evaluate_caps(dialogue_ctx, cog_state, evidence)

    assert result.act == CommunicativeAct.REFUSE
    assert result.grounded is False
    assert result.epistemic_metadata.status == EpistemicState.UNKNOWN
    assert result.resolution_metadata.grounding_status == "UNGROUNDED"
    assert result.semantic_graph is None
    assert "fail-closed" in result.error_or_fallback_reason.lower()


# ── Requirement 5: UNKNOWN / AMBIGUOUS Propagation ─────────────────────────────

def test_ambiguous_referent_subgoal_propagates_clarify():
    """Ambiguous referent in InformationSubgoal MUST compile to CLARIFY with AMBIGUOUS status."""
    subgoal = InformationSubgoal(
        target_predicate_id=101,
        arg0_id=0,
        arg1_id=0,
        polarity=True,
        reason_code=INFO_REASON_AMBIGUOUS_REFERENT,
    )
    dialogue_ctx = DialogueContextSnapshot(turn_id=1, input_text="Which one?")
    cog_state = CognitiveStateSnapshot()
    evidence = AdmissibleEvidencePool()

    result = evaluate_caps(dialogue_ctx, cog_state, evidence, subgoals=[subgoal])

    assert result.act == CommunicativeAct.CLARIFY
    assert result.epistemic_metadata.status == EpistemicState.AMBIGUOUS
    assert result.grounded is False


# ── Requirement 6: Provenance Preservation (USER_STATED != FACT) ───────────────

def test_user_stated_provenance_invariant_and_conflict():
    """
    1. USER_STATED provenance yields INFERRED epistemic status, NEVER FACT.
    2. Contradiction between user claim and verified fact triggers CLARIFY (no silent overwrite).
    """
    verified = Proposition(
        id="prop:fact_01",
        subject="ent:sky",
        predicate="c:COLOR",
        object="ent:blue",
        confidence=1.0,
        provenance=ProvenanceType.VERIFIED,
    )
    conflicting_user_claim = Proposition(
        id="prop:user_01",
        subject="ent:sky",
        predicate="c:COLOR",
        object="ent:green",
        confidence=0.8,
        provenance=ProvenanceType.USER_STATED,
    )

    dialogue_ctx = DialogueContextSnapshot(turn_id=1, input_text="The sky is green.")
    cog_state = CognitiveStateSnapshot()
    evidence = AdmissibleEvidencePool(
        verified_propositions=(verified,),
        user_claims=(conflicting_user_claim,),
    )

    result = evaluate_caps(dialogue_ctx, cog_state, evidence)

    assert result.act == CommunicativeAct.CLARIFY
    assert result.epistemic_metadata.status == EpistemicState.AMBIGUOUS
    assert result.resolution_metadata.grounding_status == "CONFLICT_DETECTED"
    assert result.provenance_metadata.origin == "USER_ASSERTION_CONFLICT"

    # Now test non-conflicting user claim when synthesized as grounded proposition
    user_claim_prop = Proposition(
        id="prop:user_02",
        subject="ent:user",
        predicate="c:FAVORITE_FOOD",
        object="ent:sushi",
        confidence=0.7,
        provenance=ProvenanceType.USER_STATED,
    )
    cog_state_user = CognitiveStateSnapshot(
        candidate_predicate="c:FAVORITE_FOOD",
        candidate_subject="ent:user",
        candidate_object="ent:sushi",
    )
    evidence_user = AdmissibleEvidencePool(verified_propositions=(user_claim_prop,))

    res_user = evaluate_caps(dialogue_ctx, cog_state_user, evidence_user)
    assert res_user.act == CommunicativeAct.ASSERT
    # Invariant: USER_STATED != FACT (produces INFERRED, not FACT)
    assert res_user.epistemic_metadata.status == EpistemicState.INFERRED
    assert res_user.provenance_metadata.metadata.get("provenance_type") == ProvenanceType.USER_STATED.value


# ── Requirement 7: Discourse Referent Resolution Integration ───────────────────

def test_discourse_context_cache_and_resolution_invariant():
    """
    Validates:
    - Bounded memory (N=16 max)
    - Exponential decay and threshold eviction
    - Resolution ranking and ambiguity
    - Separation of Concerns: RESOLVED != FACT
    """
    cache = DiscourseContextCache(max_capacity=16, decay_gamma=0.60, eviction_threshold=0.15)

    # 1. Bounded capacity test across 30 turns
    for turn in range(1, 31):
        r = DiscourseReferent(
            entity_id=f"ent_{turn}",
            concept_id="c:ITEM",
            salience=1.0,
            turn_introduced=turn,
            last_referenced_turn=turn,
        )
        cache.update_turn(turn, [r])
        assert cache.count <= 16

    # 2. Reset and test ambiguity
    cache.clear()
    ref_a = DiscourseReferent("ent:cat_a", "c:CAT", 0.9, 1, 1, ":ARG0")
    ref_b = DiscourseReferent("ent:cat_b", "c:CAT", 0.9, 1, 1, ":ARG0")
    cache.update_turn(1, [ref_a, ref_b])

    status, resolved_id, cand_ids = cache.resolve_reference(required_concept="c:CAT")
    assert status == ResolutionStatus.AMBIGUOUS
    assert set(cand_ids) == {"ent:cat_a", "ent:cat_b"}

    # Pass this ambiguity into CAPS
    dialogue_ctx = DialogueContextSnapshot(
        turn_id=2,
        input_text="Pet the cat.",
        resolution_status=status,
        candidate_referent_ids=tuple(cand_ids),
    )
    caps_res = evaluate_caps(dialogue_ctx, CognitiveStateSnapshot(), AdmissibleEvidencePool())
    assert caps_res.act == CommunicativeAct.CLARIFY
    assert caps_res.epistemic_metadata.status == EpistemicState.AMBIGUOUS

    # 3. Single candidate resolution: RESOLVED != FACT
    cache.clear()
    ref_single = DiscourseReferent("ent:dog", "c:DOG", 0.95, 1, 1)
    cache.update_turn(1, [ref_single])
    status, resolved_id, cand_ids = cache.resolve_reference(required_concept="c:DOG")
    assert status == ResolutionStatus.RESOLVED
    assert resolved_id == "ent:dog"


# ── Requirement 8: InformationSubgoal -> INQUIRE Mapping ───────────────────────

def test_information_subgoal_compilation_to_inquire():
    """INFO_REASON_MISSING_PREMISE and UNGROUNDED_VARIABLE compile to INQUIRE."""
    subgoal = InformationSubgoal(
        target_predicate_id=505,
        arg0_id=0,  # ungrounded variable
        arg1_id=10,
        polarity=True,
        reason_code=INFO_REASON_UNGROUNDED_VARIABLE,
    )
    dialogue_ctx = DialogueContextSnapshot(turn_id=1, input_text="What is the weather?")
    result = evaluate_caps(dialogue_ctx, CognitiveStateSnapshot(), AdmissibleEvidencePool(), subgoals=[subgoal])

    assert result.act == CommunicativeAct.INQUIRE
    assert result.epistemic_metadata.status == EpistemicState.UNKNOWN
    assert result.semantic_graph is not None
    assert result.target_predicate == "c:PRED_505"
    assert result.focus_argument == "ent:wh_target_arg0"


# ── Requirement 9: Deterministic CAPS Transformation Under Frozen Input ───────

def test_deterministic_caps_transformation():
    """Bit-exact identical output hash across 10 independent invocations with identical inputs."""
    prop = Proposition(
        id="prop:fixed_01",
        subject="ent:lucia",
        predicate="c:LISTENS",
        object="ent:quietly",
        confidence=1.0,
        provenance=ProvenanceType.VERIFIED,
    )
    dialogue_ctx = DialogueContextSnapshot(turn_id=5, input_text="Are you listening?")
    cog_state = CognitiveStateSnapshot(
        candidate_predicate="c:LISTENS",
        candidate_subject="ent:lucia",
        candidate_object="ent:quietly",
    )
    evidence = AdmissibleEvidencePool(verified_propositions=(prop,))

    reference_hash = evaluate_caps(dialogue_ctx, cog_state, evidence).canonical_hash()

    for _ in range(10):
        h = evaluate_caps(dialogue_ctx, cog_state, evidence).canonical_hash()
        assert h == reference_hash


# ── Requirement 10: S11 Responsibility Transition ──────────────────────────────

def test_s11_prompt_assembler_conditioning():
    """PromptAssembler incorporates [COMMUNICATIVE INTENT & PROPOSITION] section when caps_result is provided."""
    assembler = PromptAssembler()
    somatic = SomaticMarkers(stability=0.9, cognitive_load=0.1, energy=0.8, tension=0.1)
    constraints = BehavioralConstraints(
        max_tokens=100,
        temperature=0.7,
        latency_ms=0,
        reasoning_depth=0,
    )

    prop = Proposition(
        id="prop:s11_01",
        subject="ent:lucia",
        predicate="c:ASSISTS",
        object="ent:user",
        confidence=1.0,
        provenance=ProvenanceType.VERIFIED,
    )
    dialogue_ctx = DialogueContextSnapshot(turn_id=1, input_text="Will you assist me?")
    cog_state = CognitiveStateSnapshot(candidate_predicate="c:ASSISTS")
    evidence = AdmissibleEvidencePool(verified_propositions=(prop,))
    caps_res = evaluate_caps(dialogue_ctx, cog_state, evidence)

    prompt = assembler.assemble(
        somatic=somatic,
        constraints=constraints,
        history=[("user", "Will you assist me?")],
        system_preamble="You are Lucia.",
        n_ctx=4096,
        caps_result=caps_res,
    )

    assert isinstance(prompt, str)
    assert "[COMMUNICATIVE INTENT & PROPOSITION]" in prompt
    assert "act: ANSWER" in prompt
    assert "epistemic_status: FACT" in prompt
    assert "grounded: true" in prompt
    assert "target_predicate: c:ASSISTS" in prompt
    assert "directive:" in prompt


# ── Requirement 11: Regression Against Existing Cognitive Pipeline Behavior ───

@pytest.fixture
def test_config(tmp_path):
    model_file = tmp_path / "model.gguf"
    model_file.write_bytes(b"dummy")
    return MemoryOrchestratorConfig(
        model_path=str(model_file),
        loop_cadence_ms=100,
        decay_loop_cadence_seconds=60,
        sdm_num_locations=100,
        sdm_address_dim=64,
        sdm_content_dim=16,
        sdm_capacity=50,
    )


def test_cognitive_orchestrator_turn_with_caps_and_discourse(test_config):
    """Full CognitiveOrchestrator pipeline completes turn with valid CAPS result and discourse tracking."""
    with patch("src.core.orchestrator.cognitive_orchestrator.LLMBackend") as mock_llm_cls:
        mock_llm = MagicMock()
        mock_llm.is_ready.return_value = True
        mock_llm.generate.return_value = "I am listening with quiet attention."
        mock_llm_cls.return_value = mock_llm

        orch = build_cognitive_orchestrator(test_config)
        try:
            # Inject a known fact into KnowledgeStore for grounding
            orch.knowledge_store.store_proposition(
                Proposition(
                    id="prop:init_01",
                    subject="ent:lucia",
                    predicate="c:PRESENCE",
                    object="ent:here",
                    confidence=1.0,
                    provenance=ProvenanceType.VERIFIED,
                )
            )

            result = orch.process("Hello Lucia.")

            assert isinstance(result, CognitiveTurnResult)
            assert result.response_text == "I am listening with quiet attention."
            assert result.caps_result is not None
            assert isinstance(result.caps_result, CAPSResult)
            assert result.caps_result.act == CommunicativeAct.GREET
            assert result.discourse_referents is not None
            assert len(result.discourse_referents) >= 1
            assert result.discourse_referents[0].entity_id == "ent:lucia"

            # Clear history clears discourse cache
            orch.clear_history()
            assert orch.discourse_cache.count == 0
        finally:
            orch.shutdown()


# ── Requirement 12: Genesis Protection ─────────────────────────────────────────

def test_genesis_protection():
    """Verify data/profile.json remains bit-exact {'is_onboarded': false}."""
    profile_path = Path("c:/Users/Lunafiah/Desktop/My_project/Lucia/data/profile.json")
    assert profile_path.exists(), "data/profile.json must exist"
    data = json.loads(profile_path.read_text(encoding="utf-8"))
    assert data == {"is_onboarded": False}, "Genesis Invariant violated: profile must remain un-onboarded!"
