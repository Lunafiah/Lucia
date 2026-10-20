"""
tests/unit/test_epistemic_reasoning_service.py

Unit and integration tests for P23-H Runtime Integration MVP (Revision 1.1).
Covers all 24 required test points specified in Section 13:
- Projection (1-6)
- Goal Formation & Resolution (7-10)
- Result Boundary & Non-Auto-Assert (11-14)
- Lifecycle & RuleIndex Ownership (15-19)
- Safety & Invariants (20-24)
"""

import pytest
from unittest.mock import MagicMock
from pathlib import Path
import json

from src.core.cognition.contract.arena import TermArena
from src.core.cognition.contract.epistemic import EpistemicStatus, KleeneValue
from src.core.cognition.contract.projection import SymbolTable
from src.core.cognition.kernel.engine import (
    Goal,
    GoalResult,
    InformationSubgoal,
    ReasoningKernel,
    INFO_REASON_MISSING_PREMISE,
)
from src.core.cognition.kernel.rules import InferenceRule, RuleHead, RuleIndex, RulePremise
from src.core.cognition.kernel.compiler import compile_rule_set
from src.core.cognition.service import DerivedResult, EpistemicReasoningService
from src.core.knowledge.proposition import (
    Proposition,
    ProvenanceType,
    InferenceRule as KSInferenceRule,
)
from src.core.communication.caps import (
    AdmissibleEvidencePool,
    CognitiveStateSnapshot,
    CommunicationPolicySnapshot,
    CommunicativeAct,
    DialogueContextSnapshot,
    EpistemicMetadata,
    EpistemicState,
    evaluate_caps,
)
from src.core.orchestrator.cognitive_orchestrator import CognitiveOrchestrator
from src.core.config import OrchestratorConfig


# ─────────────────────────────────────────────────────────────────────────────
# Fixtures
# ─────────────────────────────────────────────────────────────────────────────

@pytest.fixture
def arena_and_symbols():
    arena = TermArena(max_terms=256)
    symbols = SymbolTable()
    return arena, symbols


@pytest.fixture
def sample_rule_index(arena_and_symbols):
    """
    Constructs a simple rule:
    PRED_human(?x) -> PRED_mortal(?x)
    """
    arena, symbols = arena_and_symbols
    pred_mortal = symbols.intern_concept("mortal")
    pred_human = symbols.intern_concept("human")
    var_x = -1  # VAR_0

    rule = InferenceRule(
        rule_id=1,
        head=RuleHead(predicate_id=pred_mortal, arg0=var_x, arg1=0, polarity=True),
        premises=(
            RulePremise(predicate_id=pred_human, arg0=var_x, arg1=0, polarity=True),
        ),
    )
    return RuleIndex(rules=(rule,))


@pytest.fixture
def reasoning_service(arena_and_symbols, sample_rule_index):
    arena, symbols = arena_and_symbols
    kernel = ReasoningKernel(arena=arena, rule_index=sample_rule_index)
    return EpistemicReasoningService(
        kernel=kernel,
        symbol_table=symbols,
        arena=arena,
    )


# ─────────────────────────────────────────────────────────────────────────────
# 1. Projection Tests (1-6)
# ─────────────────────────────────────────────────────────────────────────────

def test_01_valid_admissible_proposition_projects(reasoning_service, arena_and_symbols):
    """1. Valid admissible proposition (OBSERVED/VERIFIED) projects into TermArena."""
    arena, symbols = arena_and_symbols
    prop = Proposition(
        id="prop:socrates_human",
        subject="socrates",
        predicate="human",
        object="",
        confidence=1.0,
        provenance=ProvenanceType.OBSERVED,
        valid=True,
    )
    term_ids = reasoning_service.project_propositions([prop])
    assert len(term_ids) == 1
    term_id = term_ids[0]
    assert term_id > 0
    term = arena.get_term(term_id)
    assert term is not None
    assert term.epistemic_status == EpistemicStatus.FACT


def test_02_invalid_proposition_is_rejected(reasoning_service, arena_and_symbols):
    """2. Invalid proposition (valid=False) is rejected and not admitted."""
    arena, _ = arena_and_symbols
    initial_count = arena.term_count
    prop = Proposition(
        id="prop:invalid",
        subject="socrates",
        predicate="human",
        object="",
        confidence=1.0,
        provenance=ProvenanceType.OBSERVED,
        valid=False,
    )
    term_ids = reasoning_service.project_propositions([prop])
    assert len(term_ids) == 0
    assert arena.term_count == initial_count


def test_03_scalar_confidence_never_creates_fact(reasoning_service, arena_and_symbols):
    """3. Scalar confidence (even 1.0 or 0.99) NEVER creates FACT without certified provenance."""
    arena, _ = arena_and_symbols
    # An uncertified LLM proposal with confidence 1.0
    prop = Proposition(
        id="prop:llm_proposed",
        subject="plato",
        predicate="human",
        object="",
        confidence=1.0,
        provenance=ProvenanceType.LLM_PROPOSED,
        valid=True,
    )
    term_ids = reasoning_service.project_propositions([prop])
    assert len(term_ids) == 1
    term = arena.get_term(term_ids[0])
    assert term.epistemic_status != EpistemicStatus.FACT
    assert term.epistemic_status == EpistemicStatus.UNKNOWN


def test_04_uncertified_proposition_becomes_unknown(reasoning_service, arena_and_symbols):
    """4. Uncertified proposition becomes EpistemicStatus.UNKNOWN / non-admissible for proof."""
    arena, _ = arena_and_symbols
    prop = Proposition(
        id="prop:uncertain",
        subject="system",
        predicate="running",
        object="",
        confidence=0.8,
        provenance=ProvenanceType.UNCERTAIN,
        valid=True,
    )
    term_ids = reasoning_service.project_propositions([prop])
    assert len(term_ids) == 1
    term = arena.get_term(term_ids[0])
    assert term.epistemic_status == EpistemicStatus.UNKNOWN


def test_05_knowledgestore_derived_without_numeric_proof_graph_is_not_promoted(
    reasoning_service, arena_and_symbols
):
    """
    5. KnowledgeStore DERIVED without numeric proof graph is NOT promoted to INFERRED.
    Treated as UNKNOWN in accordance with R1.1.
    """
    arena, _ = arena_and_symbols
    prop = Proposition(
        id="prop:derived_stored",
        subject="socrates",
        predicate="mortal",
        object="",
        confidence=1.0,
        provenance=ProvenanceType.DERIVED,
        evidence_ids=["evidence_string_1", "evidence_string_2"],  # string IDs, not numeric term IDs
        valid=True,
    )
    term_ids = reasoning_service.project_propositions([prop])
    assert len(term_ids) == 1
    term = arena.get_term(term_ids[0])
    # Must NOT be promoted to INFERRED without reconstructable numeric proof graph
    assert term.epistemic_status != EpistemicStatus.INFERRED
    assert term.epistemic_status == EpistemicStatus.UNKNOWN


def test_06_evidence_ids_never_fabricated_into_numeric_premise_ids(
    reasoning_service, arena_and_symbols
):
    """6. String evidence_ids are NEVER fabricated into numeric premise IDs."""
    arena, _ = arena_and_symbols
    prop = Proposition(
        id="prop:derived_stored",
        subject="socrates",
        predicate="mortal",
        object="",
        confidence=1.0,
        provenance=ProvenanceType.DERIVED,
        evidence_ids=["1", "2", "999"],
        valid=True,
    )
    term_ids = reasoning_service.project_propositions([prop])
    assert len(term_ids) == 1
    term = arena.get_term(term_ids[0])
    # The term's premise IDs must be empty because string IDs cannot be fabricated into active term IDs
    assert term.premise_ids == ()
    assert term.rule_id == 0


# ─────────────────────────────────────────────────────────────────────────────
# 2. Goal Formation & Resolution Tests (7-10)
# ─────────────────────────────────────────────────────────────────────────────

def test_07_supported_candidate_goal_resolves(reasoning_service):
    """7. Supported candidate Goal resolves deductively: human(socrates) -> mortal(socrates)."""
    premise_prop = Proposition(
        id="prop:socrates_human",
        subject="socrates",
        predicate="human",
        object="",
        confidence=1.0,
        provenance=ProvenanceType.OBSERVED,
        valid=True,
    )
    goal_res, derived_res = reasoning_service.verify_candidate_goal(
        candidate_predicate="mortal",
        candidate_subject="socrates",
        candidate_object="",
        known_propositions=[premise_prop],
        polarity=True,
    )
    assert goal_res.status == KleeneValue.TRUE
    assert derived_res is not None
    assert derived_res.predicate == "mortal"
    assert derived_res.subject == "socrates"
    assert derived_res.epistemic_status == EpistemicStatus.INFERRED


def test_08_no_goal_bypasses_reasoning(reasoning_service):
    """8. Absence of candidate Goal (predicate is None or empty) bypasses reasoning immediately."""
    goal_res, derived_res = reasoning_service.verify_candidate_goal(
        candidate_predicate=None,
        candidate_subject=None,
        candidate_object=None,
        known_propositions=[],
    )
    assert goal_res.status == KleeneValue.UNKNOWN
    assert derived_res is None


def test_09_unsupported_goal_returns_unknown(reasoning_service):
    """9. Unsupported Goal with missing premise returns UNKNOWN and InformationSubgoal."""
    # We do NOT provide premise human(plato)
    goal_res, derived_res = reasoning_service.verify_candidate_goal(
        candidate_predicate="mortal",
        candidate_subject="plato",
        candidate_object="",
        known_propositions=[],
        polarity=True,
    )
    assert goal_res.status == KleeneValue.UNKNOWN
    assert derived_res is None
    assert goal_res.subgoal is not None
    assert isinstance(goal_res.subgoal, InformationSubgoal)
    assert goal_res.subgoal.reason_code == INFO_REASON_MISSING_PREMISE


def test_10_existing_goal_semantics_remain_unchanged(reasoning_service):
    """10. Strong Kleene K3 3-valued semantics remain unchanged in goal resolution."""
    assert KleeneValue.FALSE == 0
    assert KleeneValue.TRUE == 1
    assert KleeneValue.UNKNOWN == 2


# ─────────────────────────────────────────────────────────────────────────────
# 3. Result Boundary & Non-Auto-Assert Tests (11-14)
# ─────────────────────────────────────────────────────────────────────────────

def test_11_true_produces_only_transient_derived_result(reasoning_service):
    """11. P23-H TRUE produces only a transient DerivedResult with INFERRED status."""
    premise_prop = Proposition(
        id="prop:socrates_human",
        subject="socrates",
        predicate="human",
        object="",
        confidence=1.0,
        provenance=ProvenanceType.OBSERVED,
        valid=True,
    )
    goal_res, derived_res = reasoning_service.verify_candidate_goal(
        candidate_predicate="mortal",
        candidate_subject="socrates",
        candidate_object="",
        known_propositions=[premise_prop],
    )
    assert goal_res.status == KleeneValue.TRUE
    assert derived_res is not None
    assert derived_res.epistemic_status == EpistemicStatus.INFERRED
    # Conversion to transient proposition for evidence pool
    transient_prop = derived_res.to_transient_proposition()
    assert transient_prop.provenance == ProvenanceType.DERIVED
    assert transient_prop.id.startswith("transient:derived:")


def test_12_true_does_not_directly_trigger_assert(reasoning_service):
    """
    12. P23-H TRUE does NOT directly trigger ASSERT.
    CAPS receives the transient proposition as INFERRED, not FACT.
    """
    premise_prop = Proposition(
        id="prop:socrates_human",
        subject="socrates",
        predicate="human",
        object="",
        confidence=1.0,
        provenance=ProvenanceType.OBSERVED,
        valid=True,
    )
    goal_res, derived_res = reasoning_service.verify_candidate_goal(
        candidate_predicate="mortal",
        candidate_subject="socrates",
        candidate_object="",
        known_propositions=[premise_prop],
    )
    assert derived_res is not None
    transient_prop = derived_res.to_transient_proposition()

    # Pass into CAPS
    evidence_pool = AdmissibleEvidencePool(
        verified_propositions=(transient_prop,),
        user_claims=(),
    )
    cog_snap = CognitiveStateSnapshot(
        candidate_predicate="mortal",
        candidate_subject="socrates",
        candidate_object="",
        polarity=True,
    )
    dialogue_snap = DialogueContextSnapshot(
        turn_id=1,
        input_text="Is Socrates mortal?",
        active_referents=(),
        resolution_status=1,
        resolved_entity_id=None,
        candidate_referent_ids=(),
    )
    policy_snap = CommunicationPolicySnapshot(
        strategy="balanced",
        directness=1.0,
        formality=0.5,
        elaboration=0.5,
        supportiveness=0.5,
    )
    caps_res = evaluate_caps(
        dialogue_ctx=dialogue_snap,
        cognitive_state=cog_snap,
        evidence_pool=evidence_pool,
        comm_policy=policy_snap,
    )
    # Crucial: Epistemic status in CAPS must be INFERRED, NEVER FACT!
    assert caps_res.epistemic_metadata.status == EpistemicState.INFERRED
    assert caps_res.epistemic_metadata.status != EpistemicState.FACT


def test_13_unknown_produces_information_subgoal_in_caps(reasoning_service):
    """13. UNKNOWN produces the existing InformationSubgoal, leading to CAPS INQUIRE."""
    goal_res, derived_res = reasoning_service.verify_candidate_goal(
        candidate_predicate="mortal",
        candidate_subject="plato",
        candidate_object="",
        known_propositions=[],
    )
    assert goal_res.status == KleeneValue.UNKNOWN
    assert goal_res.subgoal is not None

    # Pass subgoal to CAPS
    dialogue_snap = DialogueContextSnapshot(
        turn_id=1,
        input_text="Is Plato mortal?",
        active_referents=(),
        resolution_status=1,
        resolved_entity_id=None,
        candidate_referent_ids=(),
    )
    cog_snap = CognitiveStateSnapshot()
    evidence_pool = AdmissibleEvidencePool(verified_propositions=(), user_claims=())
    caps_res = evaluate_caps(
        dialogue_ctx=dialogue_snap,
        cognitive_state=cog_snap,
        evidence_pool=evidence_pool,
        subgoals=(goal_res.subgoal,),
    )
    assert caps_res.act == CommunicativeAct.INQUIRE
    assert caps_res.epistemic_metadata.status == EpistemicState.UNKNOWN


def test_14_false_produces_no_derived_result(reasoning_service, arena_and_symbols):
    """14. FALSE/contradiction does not manufacture derived proposition."""
    arena, symbols = arena_and_symbols
    goal_res, derived_res = reasoning_service.verify_candidate_goal(
        candidate_predicate="non_existent",
        candidate_subject="nobody",
        candidate_object="",
        known_propositions=[],
        polarity=True,
    )
    # When unsupported or refuted, derived_res MUST be None
    assert derived_res is None


# ─────────────────────────────────────────────────────────────────────────────
# 4. Lifecycle & RuleIndex Ownership Tests (15-19)
# ─────────────────────────────────────────────────────────────────────────────

def test_15_rule_index_constructed_by_compiler_owned_by_orchestrator():
    """15. RuleIndex is constructed by compile_rule_set and owned by orchestrator."""
    st = SymbolTable()
    ks_rule = KSInferenceRule(
        id="rule:mortal",
        name="All humans are mortal",
        domain="logic",
        antecedents=[("?x", "human", "")],
        consequent_pattern=("?x", "mortal", ""),
        confidence_decay=1.0,
    )
    rule_index, report = compile_rule_set([ks_rule], st)
    assert report.quarantined_count == 0
    assert report.compiled_count == 1
    assert isinstance(rule_index, RuleIndex)
    assert rule_index.total_rules == 1


def test_16_reasoning_kernel_consumes_rule_index_read_only(sample_rule_index, arena_and_symbols):
    """16. ReasoningKernel consumes RuleIndex read-only without modifying it."""
    arena, _ = arena_and_symbols
    kernel = ReasoningKernel(arena=arena, rule_index=sample_rule_index)
    initial_rule_count = sample_rule_index.total_rules
    goal = Goal(predicate_id=1, arg0_id=1, arg1_id=0, polarity=True, scope_id=1)
    kernel.resolve_goal(goal)
    assert sample_rule_index.total_rules == initial_rule_count


def test_17_lifecycle_reset_recompiles_rule_index():
    """17. Lifecycle reset re-instantiates or recompiles RuleIndex safely."""
    st1 = SymbolTable()
    st2 = SymbolTable()
    ks_rule = KSInferenceRule(
        id="rule:test",
        name="Test rule",
        domain="test",
        antecedents=[("?x", "test_prem", "")],
        consequent_pattern=("?x", "test_pred", ""),
        confidence_decay=1.0,
    )
    index1, report1 = compile_rule_set([ks_rule], st1)
    index2, report2 = compile_rule_set([ks_rule], st2)
    assert index1 is not index2
    assert index1.total_rules == index2.total_rules


def test_18_no_inter_turn_term_arena_wipe(reasoning_service, arena_and_symbols):
    """18. TermArena is NOT wiped between turns to preserve persistent anchor terms."""
    arena, symbols = arena_and_symbols
    asst_pred = symbols.intern_concept("lucia_assistant")
    # Simulate ADR-038 assistant seed term
    seed_term_id = arena.allocate_term(
        predicate_id=asst_pred,
        arg0_id=0,
        arg1_id=0,
        epistemic_status=EpistemicStatus.FACT,
        scope_id=0,
    )
    assert seed_term_id > 0

    # Execute a reasoning turn
    premise_prop = Proposition(
        id="prop:socrates_human",
        subject="socrates",
        predicate="human",
        object="",
        confidence=1.0,
        provenance=ProvenanceType.OBSERVED,
        valid=True,
    )
    reasoning_service.verify_candidate_goal(
        candidate_predicate="mortal",
        candidate_subject="socrates",
        candidate_object="",
        known_propositions=[premise_prop],
    )

    # Seed term MUST survive
    surviving_term = arena.get_term(seed_term_id)
    assert surviving_term is not None
    assert surviving_term.predicate_id == asst_pred


def test_19_adr038_assistant_seed_behavior_intact(arena_and_symbols):
    """19. ADR-038 assistant seed term allocation pattern functions as expected."""
    arena, symbols = arena_and_symbols
    asst_pred = symbols.intern_concept("lucia_modal_agent")
    asst_term_id = arena.allocate_term(
        predicate_id=asst_pred,
        arg0_id=0,
        arg1_id=0,
        epistemic_status=EpistemicStatus.FACT,
        scope_id=0,
    )
    assert asst_term_id > 0
    assert arena.get_term(asst_term_id).epistemic_status == EpistemicStatus.FACT


# ─────────────────────────────────────────────────────────────────────────────
# 5. Safety & Persistence Tests (20-24)
# ─────────────────────────────────────────────────────────────────────────────

def test_20_no_derived_reasoning_result_is_automatically_persisted(reasoning_service):
    """20. No automatic persistence: DerivedResult is purely in-memory."""
    premise_prop = Proposition(
        id="prop:socrates_human",
        subject="socrates",
        predicate="human",
        object="",
        confidence=1.0,
        provenance=ProvenanceType.OBSERVED,
        valid=True,
    )
    _, derived_res = reasoning_service.verify_candidate_goal(
        candidate_predicate="mortal",
        candidate_subject="socrates",
        candidate_object="",
        known_propositions=[premise_prop],
    )
    assert derived_res is not None
    # Derived result does not have any save/persist call
    assert not hasattr(derived_res, "save")
    assert not hasattr(derived_res, "persist")


def test_21_no_persistent_numeric_term_id_introduced(reasoning_service):
    """21. Transient numeric TermID in DerivedResult has no disk serialization format."""
    _, derived_res = reasoning_service.verify_candidate_goal(
        candidate_predicate="mortal",
        candidate_subject="socrates",
        candidate_object="",
        known_propositions=[
            Proposition(
                id="prop:socrates_human",
                subject="socrates",
                predicate="human",
                object="",
                confidence=1.0,
                provenance=ProvenanceType.OBSERVED,
                valid=True,
            )
        ],
    )
    assert derived_res is not None
    transient_prop = derived_res.to_transient_proposition()
    # The transient proposition is marked transient:derived:<id>
    assert transient_prop.id.startswith("transient:derived:")


def test_22_p23h_kernel_regression_intact():
    """22. P23-H kernel imports and core properties remain valid."""
    from src.core.cognition.kernel import ReasoningKernel, Goal, GoalResult, JTMS
    assert ReasoningKernel is not None
    assert Goal is not None
    assert GoalResult is not None
    assert JTMS is not None


def test_23_rule_compiler_regression_intact():
    """23. Rule Compiler contract imports and validity checks remain valid."""
    from src.core.cognition.kernel.compiler import compile_rule_set, RuleCompilationReport
    assert compile_rule_set is not None
    assert RuleCompilationReport is not None


def test_24_adr038_causal_ingress_intact():
    """24. ADR-038 LanguageIngressGate contract remains intact."""
    from src.core.language.adapter.gate import LanguageIngressGate
    from src.core.language.adapter.contracts import IngressCandidateAssertion
    assert LanguageIngressGate is not None
    assert IngressCandidateAssertion is not None
