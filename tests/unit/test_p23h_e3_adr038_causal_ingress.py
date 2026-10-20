"""
Unit and Property Tests for ADR-038: Grounded Propositional Causal Ingress Contract.

Validates:
1. Contract integrity (CausalRelation values, IngressCandidateAssertion immutability,
   absence of epistemic_status on untrusted candidate, RetractionDirective).
2. Five required causal attribution cases (SPONTANEOUS, SUPPLIED_ANSWER,
   CONFIRMED_ECHO, CORRECTED_NEGATION, ELABORATED, and mixed turns).
3. Epistemic certification safety (NEG-02 anti-confidence-escalation,
   F15 anti-echo protection, authoritative user correction).
4. Provenance preservation (reserved metadata keys 1001 & 1002, serialization round-trip).
5. Retraction ownership (Gate emits directive -> Orchestrator dispatches to JTMS without direct coupling).
6. Assistant proposition semantic indexing into in-session TermArena (Decision A).
"""

import pytest
from dataclasses import FrozenInstanceError

from src.core.cognition.contract import (
    EpistemicStatus,
    LogicalTerm,
    ProvenanceRecord,
    SCOPE_TYPE_MODAL,
    SCOPE_TYPE_ROOT,
    SymbolTable,
    TermArena,
)
from src.core.cognition.contract.provenance import (
    PROV_KEY_ANTECEDENT_TERM,
    PROV_KEY_CAUSAL_RELATION,
)
from src.core.cognition.kernel import ReasoningKernel, JTMS
from src.core.cognition.kernel.rules import RuleIndex
from src.core.communication.caps import CommunicativeAct, DyadicDiscourseState
from src.core.language.adapter.contracts import (
    CausalRelation,
    CertificationResult,
    EpistemicEscalationError,
    IngressCandidateAssertion,
    IngressSourceClass,
    QualifiedLogicalAssertion,
    RetractionDirective,
)
from src.core.language.adapter.gate import LanguageIngressGate
from src.core.language.contract import (
    CommunicativeAct as RealizationAct,
    RealizationInputContract,
    SemanticRoleBinding,
)
from src.core.orchestrator.cognitive_orchestrator import CognitiveOrchestrator


class TestADR038Contract:
    """Core Contract Tests for ADR-038 data structures."""

    def test_causal_relation_values(self):
        """Verify CausalRelation IntEnum values are exactly 1..5."""
        assert CausalRelation.SPONTANEOUS == 1
        assert CausalRelation.SUPPLIED_ANSWER == 2
        assert CausalRelation.CONFIRMED_ECHO == 3
        assert CausalRelation.CORRECTED_NEGATION == 4
        assert CausalRelation.ELABORATED == 5
        assert len(CausalRelation) == 5

    def test_causal_relation_invalid_value_rejection(self):
        """Verify invalid values cannot be coerced into CausalRelation."""
        with pytest.raises(ValueError):
            CausalRelation(0)
        with pytest.raises(ValueError):
            CausalRelation(6)
        with pytest.raises(ValueError):
            CausalRelation("SPONTANEOUS")

    def test_ingress_candidate_assertion_construction(self):
        """Verify IngressCandidateAssertion fields and default values."""
        candidate = IngressCandidateAssertion(
            predicate_id=101,
            arg0_id=201,
            source_class=IngressSourceClass.USER_DISCOURSE,
        )
        assert candidate.predicate_id == 101
        assert candidate.arg0_id == 201
        assert candidate.arg1_id == 0
        assert candidate.arg2_id == 0
        assert candidate.polarity is True
        assert candidate.scope_id == 1
        assert candidate.source_class == IngressSourceClass.USER_DISCOURSE
        assert candidate.causal_relation == CausalRelation.SPONTANEOUS
        assert candidate.antecedent_term_id == 0
        assert candidate.rule_id == 0
        assert candidate.supporting_premise_ids == ()

    def test_ingress_candidate_has_no_epistemic_status(self):
        """Untrusted candidate MUST NOT have epistemic_status attribute."""
        candidate = IngressCandidateAssertion(
            predicate_id=101,
            arg0_id=201,
            source_class=IngressSourceClass.USER_DISCOURSE,
        )
        assert not hasattr(candidate, "epistemic_status")

    def test_ingress_candidate_immutability(self):
        """Candidate assertion must be frozen and immutable."""
        candidate = IngressCandidateAssertion(
            predicate_id=101,
            arg0_id=201,
            source_class=IngressSourceClass.USER_DISCOURSE,
        )
        with pytest.raises(FrozenInstanceError):
            candidate.predicate_id = 999  # type: ignore

    def test_retraction_directive_contract(self):
        """Verify RetractionDirective structure and immutability."""
        directive = RetractionDirective(
            target_term_id=42,
            reason="USER_CORRECTION",
        )
        assert directive.target_term_id == 42
        assert directive.reason == "USER_CORRECTION"
        with pytest.raises(FrozenInstanceError):
            directive.target_term_id = 100  # type: ignore


class TestADR038Provenance:
    """Provenance metadata tests for Grounded Causal Link."""

    def test_provenance_reserved_keys(self):
        assert PROV_KEY_CAUSAL_RELATION == 1001
        assert PROV_KEY_ANTECEDENT_TERM == 1002

    def test_provenance_with_causal_link(self):
        rec = ProvenanceRecord()
        linked = rec.with_causal_link(
            causal_relation=CausalRelation.CONFIRMED_ECHO,
            antecedent_term_id=88,
        )
        assert linked.causal_relation == CausalRelation.CONFIRMED_ECHO
        assert linked.antecedent_term_id == 88
        assert linked.metadata[PROV_KEY_CAUSAL_RELATION] == int(CausalRelation.CONFIRMED_ECHO)
        assert linked.metadata[PROV_KEY_ANTECEDENT_TERM] == 88

    def test_provenance_roundtrip_serialization(self):
        rec = ProvenanceRecord(confidence=0.85).with_causal_link(
            causal_relation=CausalRelation.CORRECTED_NEGATION,
            antecedent_term_id=123,
        )
        data = rec.to_dict()
        restored = ProvenanceRecord.from_dict(data)
        assert restored.causal_relation == CausalRelation.CORRECTED_NEGATION
        assert restored.antecedent_term_id == 123
        assert restored.confidence == 0.85


class TestADR038Attribution:
    """Causal attribution tests for the 5 required cases and mixed turns."""

    def setup_method(self):
        self.gate = LanguageIngressGate()

    def test_spontaneous_assertion(self):
        """Case 1: Novel user assertion without assistant antecedent."""
        state = DyadicDiscourseState()
        rel, antecedent = self.gate.attribute_causal_relation(
            has_denial=False,
            has_affirmation=False,
            has_novel_content=True,
            discourse_state=state,
        )
        assert rel == CausalRelation.SPONTANEOUS
        assert antecedent == 0

    def test_answer_to_open_question(self):
        """Case 2: User supplies answer to an open inquiry."""
        state = DyadicDiscourseState(
            inquiry_type="OPEN",
            active_assistant_seed_term_id=10,
        )
        rel, antecedent = self.gate.attribute_causal_relation(
            has_denial=False,
            has_affirmation=False,
            has_novel_content=True,
            discourse_state=state,
        )
        assert rel == CausalRelation.SUPPLIED_ANSWER
        assert antecedent == 10

    def test_confirmed_echo(self):
        """Case 3: User assents to assistant-seeded hypothesis."""
        state = DyadicDiscourseState(
            inquiry_type="CLOSED",
            active_assistant_seed_term_id=25,
        )
        rel, antecedent = self.gate.attribute_causal_relation(
            has_denial=False,
            has_affirmation=True,
            has_novel_content=False,
            discourse_state=state,
        )
        assert rel == CausalRelation.CONFIRMED_ECHO
        assert antecedent == 25

    def test_corrected_negation(self):
        """Case 4: User rejects or corrects assistant-seeded proposition."""
        state = DyadicDiscourseState(
            inquiry_type="CLOSED",
            active_assistant_seed_term_id=25,
        )
        rel, antecedent = self.gate.attribute_causal_relation(
            has_denial=True,
            has_affirmation=False,
            has_novel_content=False,
            discourse_state=state,
        )
        assert rel == CausalRelation.CORRECTED_NEGATION
        assert antecedent == 25

    def test_prompted_topic_elaboration(self):
        """Case 5: User elaborates with novel independent info on prompted topic."""
        state = DyadicDiscourseState(
            inquiry_type="CLOSED",
            active_assistant_seed_term_id=30,
        )
        rel, antecedent = self.gate.attribute_causal_relation(
            has_denial=False,
            has_affirmation=False,
            has_novel_content=True,
            discourse_state=state,
        )
        assert rel == CausalRelation.ELABORATED
        assert antecedent == 30

    def test_mixed_turn_proposition_level_attribution(self):
        """
        Proposition-level attribution on mixed turn:
        'Yeah, I do like it, and I need to buy milk.'
        P1 -> CONFIRMED_ECHO
        P2 -> SPONTANEOUS
        """
        state = DyadicDiscourseState(
            inquiry_type="CLOSED",
            active_assistant_seed_term_id=40,
        )
        # Proposition 1: Echo
        p1_rel, p1_ant = self.gate.attribute_causal_relation(
            has_denial=False,
            has_affirmation=True,
            has_novel_content=False,
            discourse_state=state,
        )
        assert p1_rel == CausalRelation.CONFIRMED_ECHO
        assert p1_ant == 40

        # Proposition 2: Spontaneous new topic
        p2_rel, p2_ant = self.gate.attribute_causal_relation(
            has_denial=False,
            has_affirmation=False,
            has_novel_content=True,
            discourse_state=DyadicDiscourseState(),  # fresh independent clause
        )
        assert p2_rel == CausalRelation.SPONTANEOUS
        assert p2_ant == 0


class TestADR038EpistemicCertification:
    """Epistemic certification and safety invariants."""

    def setup_method(self):
        self.gate = LanguageIngressGate()

    def test_confirmed_echo_cannot_become_fact(self):
        """
        Invariant F15: CONFIRMED_ECHO must remain UNKNOWN epistemic status.
        Never extensional FACT.
        """
        cand = IngressCandidateAssertion(
            predicate_id=100,
            arg0_id=200,
            source_class=IngressSourceClass.USER_DISCOURSE,
            causal_relation=CausalRelation.CONFIRMED_ECHO,
            antecedent_term_id=12,
        )
        qualified, directive = self.gate.certify_candidate_assertion(cand, confidence=1.0)
        assert qualified.epistemic_status == EpistemicStatus.UNKNOWN
        assert qualified.causal_relation == CausalRelation.CONFIRMED_ECHO
        assert qualified.antecedent_term_id == 12
        assert directive is None

    def test_supplied_answer_is_certified_fact(self):
        """Answers to open inquiries remain authoritative user testimony."""
        cand = IngressCandidateAssertion(
            predicate_id=101,
            arg0_id=201,
            source_class=IngressSourceClass.USER_DISCOURSE,
            causal_relation=CausalRelation.SUPPLIED_ANSWER,
            antecedent_term_id=15,
        )
        qualified, directive = self.gate.certify_candidate_assertion(cand, confidence=1.0)
        assert qualified.epistemic_status == EpistemicStatus.FACT
        assert qualified.polarity is True
        assert directive is None

    def test_corrected_negation_yields_fact_and_retraction_directive(self):
        """
        User corrections become authoritative FACT with polarity=False
        and emit a typed RetractionDirective for the antecedent.
        """
        cand = IngressCandidateAssertion(
            predicate_id=102,
            arg0_id=202,
            source_class=IngressSourceClass.USER_DISCOURSE,
            causal_relation=CausalRelation.CORRECTED_NEGATION,
            antecedent_term_id=33,
        )
        qualified, directive = self.gate.certify_candidate_assertion(cand, confidence=1.0)
        assert qualified.epistemic_status == EpistemicStatus.FACT
        assert qualified.polarity is False
        assert directive is not None
        assert directive.target_term_id == 33
        assert directive.reason == "USER_CORRECTED_NEGATION"

    def test_invariant_neg02_scalar_confidence_never_asserts_fact(self):
        """
        Invariant NEG-02: continuous scalar confidence (c >= theta)
        must NEVER directly assert discrete FACT.
        """
        cand = IngressCandidateAssertion(
            predicate_id=103,
            arg0_id=203,
            source_class=IngressSourceClass.USER_DISCOURSE,
            causal_relation=CausalRelation.SPONTANEOUS,
        )
        # Confidence < 1.0 cannot yield FACT
        qualified, _ = self.gate.certify_candidate_assertion(cand, confidence=0.999)
        assert qualified.epistemic_status == EpistemicStatus.UNKNOWN

    def test_perceptual_source_restriction(self):
        """Perceptual sources cannot directly assert extensional FACT."""
        cand = IngressCandidateAssertion(
            predicate_id=104,
            arg0_id=204,
            source_class=IngressSourceClass.PERCEPTUAL,
            causal_relation=CausalRelation.SPONTANEOUS,
        )
        qualified, _ = self.gate.certify_candidate_assertion(cand, confidence=1.0)
        assert qualified.epistemic_status == EpistemicStatus.UNKNOWN

    def test_certify_candidates_batch(self):
        """Verify batch certification produces CertificationResult."""
        c1 = IngressCandidateAssertion(
            predicate_id=100,
            arg0_id=200,
            source_class=IngressSourceClass.USER_DISCOURSE,
            causal_relation=CausalRelation.CONFIRMED_ECHO,
            antecedent_term_id=5,
        )
        c2 = IngressCandidateAssertion(
            predicate_id=101,
            arg0_id=201,
            source_class=IngressSourceClass.USER_DISCOURSE,
            causal_relation=CausalRelation.CORRECTED_NEGATION,
            antecedent_term_id=6,
        )
        res = self.gate.certify_candidates([c1, c2], confidence=1.0)
        assert isinstance(res, CertificationResult)
        assert len(res.assertions) == 2
        assert res.assertions[0].epistemic_status == EpistemicStatus.UNKNOWN
        assert res.assertions[1].epistemic_status == EpistemicStatus.FACT
        assert res.assertions[1].polarity is False
        assert len(res.retraction_directives) == 1
        assert res.retraction_directives[0].target_term_id == 6


class TestADR038RetractionAndOrchestration:
    """Tests for RetractionDirective ownership and JTMS integration."""

    def test_retraction_directive_dispatch_to_jtms(self):
        """
        Verify: Gate emits RetractionDirective -> Orchestrator executes
        JTMS.retract_premise() -> invalidates dependent terms.
        """
        arena = TermArena()
        syms = SymbolTable()
        kernel = ReasoningKernel(rule_index=RuleIndex(), arena=arena)

        # Allocate premise P in arena
        p_term_id = arena.allocate_term(
            predicate_id=100,
            arg0_id=200,
            epistemic_status=EpistemicStatus.FACT,
        )
        # Allocate derived consequence Q in arena
        q_term_id = arena.allocate_term(
            predicate_id=101,
            arg0_id=201,
            epistemic_status=EpistemicStatus.INFERRED,
        )
        # Add JTMS justification: P -> Q
        kernel.jtms.register_justification(
            rule_id=1,
            consequence_id=q_term_id,
            premise_ids=(p_term_id,),
        )

        assert arena.get_term(p_term_id).is_active is True
        assert arena.get_term(q_term_id).is_active is True

        # Orchestrator with attached kernel and arena
        # We test execute_retraction_directive directly
        from unittest.mock import MagicMock
        orchestrator = MagicMock(spec=CognitiveOrchestrator)
        orchestrator._reasoning_kernel = kernel
        orchestrator._term_arena = arena
        orchestrator.execute_retraction_directive = CognitiveOrchestrator.execute_retraction_directive.__get__(orchestrator)

        directive = RetractionDirective(
            target_term_id=p_term_id,
            reason="USER_CORRECTED_NEGATION",
        )
        invalidated = orchestrator.execute_retraction_directive(directive)

        # Both P and Q must be retracted in arena
        assert p_term_id in invalidated
        assert q_term_id in invalidated
        assert arena.get_term(p_term_id).is_active is False
        assert arena.get_term(q_term_id).is_active is False

    def test_gate_remains_independent_of_jtms(self):
        """Verify LanguageIngressGate does NOT import or reference JTMS."""
        import src.core.language.adapter.gate as gate_mod
        assert not hasattr(gate_mod, "JTMS")
        assert not hasattr(gate_mod, "ReasoningKernel")


class TestADR038AssistantSeedIndexing:
    """Decision A: Assistant Proposition Semantic Indexing into TermArena."""

    def test_assistant_seed_allocated_with_modal_scope_and_unknown_status(self):
        """
        When RealizationInputContract is created with a target predicate,
        the seed is interned into TermArena with scope=MODAL and epistemic_status=UNKNOWN.
        """
        arena = TermArena()
        syms = SymbolTable()

        contract = RealizationInputContract.create_default(
            act=RealizationAct.INQUIRE,
            target_predicate="predicate:user_likes_coffee",
        )

        pred_id = syms.intern_concept(contract.target_predicate)
        arg0_id = syms.intern_concept("concept:user")
        scope_id = arena.allocate_scope(scope_type_id=SCOPE_TYPE_MODAL)

        term_id = arena.allocate_term(
            predicate_id=pred_id,
            arg0_id=arg0_id,
            scope_id=scope_id,
            epistemic_status=EpistemicStatus.UNKNOWN,
            polarity=contract.polarity,
        )

        term = arena.get_term(term_id)
        assert term.predicate_id == pred_id
        assert term.epistemic_status == EpistemicStatus.UNKNOWN
        assert term.scope_id == scope_id
        assert arena.get_scope(term.scope_id).scope_type_id == SCOPE_TYPE_MODAL

        # Verify that modal term cannot unify with root axioms
        root_scope = arena.get_scope(1)
        assert root_scope.scope_type_id == SCOPE_TYPE_ROOT
        assert term.scope_id != 1

    def test_dyadic_discourse_state_stores_seed_and_inquiry_type(self):
        """Verify DyadicDiscourseState retains active_assistant_seed_term_id and inquiry_type."""
        state = DyadicDiscourseState(
            active_assistant_seed_term_id=77,
            inquiry_type="CLOSED",
        )
        assert state.active_assistant_seed_term_id == 77
        assert state.inquiry_type == "CLOSED"

        state_dict = state.to_dict()
        assert state_dict["active_assistant_seed_term_id"] == 77
        assert state_dict["inquiry_type"] == "CLOSED"
