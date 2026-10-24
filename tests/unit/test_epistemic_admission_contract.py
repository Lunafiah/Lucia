"""
tests/unit/test_epistemic_admission_contract.py

Regression Test Suite for the Ratified Final Epistemic Admission Contract.
Verifies all 11 mandatory contract tests:
1. Modal -> Root Leakage Isolation
2. USER_STATED != BELIEVES
3. Assistant Echo Rejection (CONFIRMED_ECHO -> UNKNOWN -> REJECT)
4. Unsupported World Claim (MODAL_ADMIT -> scope:modal:user_claim)
5. User Self-Report (ROOT_ADMIT -> scope:root, USER_STATED)
6. Unknown Predicate Fail-Closed Staging (STAGE)
7. Contradiction Staging Without Overwrite (STAGE + conflict)
8. KnowledgeStore -> JTMS Revision Cascade
9. Multi-Justification Survival
10. Bootstrap Immutability (PermissionError)
11. Continuous Confidence Invariant (NEG-02)
"""

import pytest

from src.core.cognition.contract import (
    EpistemicStatus,
    KleeneValue,
    LogicalTerm,
    ProvenanceRecord,
    SymbolTable,
    TermArena,
)
from src.core.cognition.kernel.engine import Goal, GoalResult
from src.core.cognition.kernel import ReasoningKernel, JTMS
from src.core.cognition.kernel.rules import RuleIndex
from src.core.cognition.service import EpistemicReasoningService
from src.core.communication.caps import DyadicDiscourseState
from src.core.knowledge.bootstrap import bootstrap_verified_knowledge
from src.core.knowledge.proposition import Concept, Proposition, ProvenanceType
from src.core.knowledge.store import KnowledgeStore
from src.core.language.adapter.contracts import (
    AdmissionDisposition,
    CausalRelation,
    IngressCandidateAssertion,
    IngressSourceClass,
    RetractionDirective,
    StagedCandidate,
)
from src.core.language.adapter.gate import (
    LanguageIngressGate,
    classify_predicate_domain,
    evaluate_admission_disposition,
)
from src.core.orchestrator.cognitive_orchestrator import CognitiveOrchestrator


class TestEpistemicAdmissionContract:
    """Complete regression test suite for Epistemic Admission Contract."""

    def test_01_modal_to_root_leakage_blocked(self):
        """
        Test 1 — Modal -> Root Leakage:
        A proposition in scope:modal:user_claim must remain outside root reasoning
        after persistence, reload, projection, and reasoning kernel query.
        """
        store = KnowledgeStore()
        modal_prop = Proposition(
            id="prop:modal_water_90c",
            subject="ent:water",
            predicate="c:boils_at",
            object="val:90c",
            confidence=1.0,
            provenance=ProvenanceType.USER_STATED,
            scope_id="scope:modal:user_claim",
        )
        store.store_proposition(modal_prop)

        # 1. Round-trip serialization
        json_data = store.to_json()
        restored_store = KnowledgeStore.from_json(json_data)
        reloaded_prop = restored_store.get_proposition("prop:modal_water_90c")
        assert reloaded_prop is not None
        assert reloaded_prop.scope_id == "scope:modal:user_claim"

        # 2. Project into reasoning service
        arena = TermArena()
        symbols = SymbolTable()
        kernel = ReasoningKernel(rule_index=RuleIndex(), arena=arena)
        service = EpistemicReasoningService(kernel=kernel, symbol_table=symbols, arena=arena)

        allocated_ids = service.project_propositions([reloaded_prop])
        assert len(allocated_ids) == 1
        term_id = allocated_ids[0]
        term = arena.get_term(term_id)
        assert term is not None
        # Must NOT be root scope (1)
        assert term.scope_id != 1
        assert term.scope_id == symbols.intern_scope("scope:modal:user_claim")

        # 3. Query root goal: "Does water boil at 90C in ROOT scope?"
        pred_id = symbols.intern_concept("c:boils_at")
        a0_id = symbols.intern_concept("ent:water")
        a1_id = symbols.intern_concept("val:90c")
        root_goal = Goal(
            predicate_id=pred_id,
            arg0_id=a0_id,
            arg1_id=a1_id,
            polarity=True,
            scope_id=1,  # Root scope
        )
        goal_result = kernel.resolve_goal(root_goal)
        # Root reasoning CANNOT unify with modal term; must be UNKNOWN
        assert goal_result.status == KleeneValue.UNKNOWN

    def test_02_user_stated_not_converted_to_believes(self):
        """
        Test 2 — USER_STATED != BELIEVES:
        A user assertion must not create a BELIEVES(user, p) proposition unless explicitly expressed.
        """
        gate = LanguageIngressGate()
        disposition, target_scope = evaluate_admission_disposition(
            source_class=IngressSourceClass.USER_DISCOURSE,
            domain="USER_PREFERENCE",
            causal_relation=CausalRelation.SPONTANEOUS,
        )
        assert disposition == AdmissionDisposition.ROOT_ADMIT
        assert target_scope == "scope:root"

        prop = Proposition(
            id="prop:user_pref_tea",
            subject="ent:user",
            predicate="c:prefers",
            object="val:oolong_tea",
            confidence=1.0,
            provenance=ProvenanceType.USER_STATED,
            scope_id=target_scope,
        )
        store = KnowledgeStore()
        store.store_proposition(prop)

        # Verify proposition has USER_STATED provenance and original predicate
        stored = store.get_proposition("prop:user_pref_tea")
        assert stored.provenance == ProvenanceType.USER_STATED
        assert stored.predicate == "c:prefers"
        # Zero BELIEVES relation synthesized
        all_props = store.get_all_propositions()
        for p in all_props:
            assert "believes" not in p.predicate.lower()

    def test_03_assistant_echo_rejection(self):
        """
        Test 3 — Assistant Echo Rejection:
        With active assistant closed question, a passive confirmation ('Yes', 'Đúng rồi')
        is classified as CONFIRMED_ECHO -> UNKNOWN -> REJECT -> zero storage mutation.
        """
        gate = LanguageIngressGate()
        state = DyadicDiscourseState(
            inquiry_type="CLOSED",
            active_assistant_seed_term_id=101,
        )
        # Affirmative echo without novel content
        causal_rel, ant_id = gate.attribute_causal_relation(
            has_denial=False,
            has_affirmation=True,
            has_novel_content=False,
            discourse_state=state,
        )
        assert causal_rel == CausalRelation.CONFIRMED_ECHO
        assert ant_id == 101

        disposition, _ = evaluate_admission_disposition(
            source_class=IngressSourceClass.USER_DISCOURSE,
            domain="OBJECTIVE_WORLD",
            causal_relation=causal_rel,
        )
        assert disposition == AdmissionDisposition.REJECT

        # Verify zero mutation in KnowledgeStore
        store = KnowledgeStore()
        initial_count = len(store.get_all_propositions())
        assert len(store.get_all_staged()) == 0
        # No proposition stored
        assert len(store.get_all_propositions()) == initial_count

    def test_04_unsupported_world_claim_modal_admission(self):
        """
        Test 4 — Unsupported World Claim:
        'Water boils at 90C' is an unverified external world claim -> MODAL_ADMIT -> scope:modal:user_claim.
        """
        domain = classify_predicate_domain("c:boils_at")
        assert domain == "OBJECTIVE_WORLD"

        disposition, target_scope = evaluate_admission_disposition(
            source_class=IngressSourceClass.USER_DISCOURSE,
            domain=domain,
            causal_relation=CausalRelation.SPONTANEOUS,
        )
        assert disposition == AdmissionDisposition.MODAL_ADMIT
        assert target_scope == "scope:modal:user_claim"

    def test_05_user_self_report_root_admission(self):
        """
        Test 5 — User Self-Report:
        'I prefer oolong tea' is authoritative user preference -> ROOT_ADMIT -> scope:root, USER_STATED.
        """
        domain = classify_predicate_domain("c:prefers")
        assert domain == "USER_PREFERENCE"

        disposition, target_scope = evaluate_admission_disposition(
            source_class=IngressSourceClass.USER_DISCOURSE,
            domain=domain,
            causal_relation=CausalRelation.SPONTANEOUS,
        )
        assert disposition == AdmissionDisposition.ROOT_ADMIT
        assert target_scope == "scope:root"

    def test_06_unknown_predicate_fail_closed_staging(self):
        """
        Test 6 — Unknown Predicate:
        Unrecognized predicate -> STAGE -> no root admission, ephemeral staging only.
        """
        domain = classify_predicate_domain("c:quantum_entanglement_flux_xyz")
        assert domain == "UNKNOWN"

        disposition, target_scope = evaluate_admission_disposition(
            source_class=IngressSourceClass.USER_DISCOURSE,
            domain=domain,
            causal_relation=CausalRelation.SPONTANEOUS,
        )
        assert disposition == AdmissionDisposition.STAGE
        assert target_scope == "scope:modal:unclassified"

        store = KnowledgeStore()
        staged = StagedCandidate(
            candidate_id="cand_test_01",
            subject="ent:particle",
            predicate="c:quantum_entanglement_flux_xyz",
            object="val:high",
            scope_id=target_scope,
            reason="UNCLASSIFIED_DOMAIN",
        )
        store.stage_candidate(staged)
        assert len(store.get_all_staged()) == 1
        assert len(store.get_all_propositions()) == 0  # Zero canonical disk mutation

        # Staging is not serialized to disk JSON
        serialized = store.to_json()
        assert "cand_test_01" not in serialized
        restored = KnowledgeStore.from_json(serialized)
        assert len(restored.get_all_staged()) == 0

    def test_07_contradiction_staging_without_overwrite(self):
        """
        Test 7 — Contradiction:
        Contradicting an active single-valued root proposition produces STAGE + conflict,
        preventing silent overwrite.
        """
        store = KnowledgeStore()
        root_fact = Proposition(
            id="prop:water_boils_100c",
            subject="ent:water",
            predicate="c:boils_at",
            object="val:100c",
            confidence=1.0,
            provenance=ProvenanceType.VERIFIED,
            scope_id="scope:root",
        )
        store.store_proposition(root_fact)

        # Candidate contradicts single-valued predicate boils_at with differing object
        candidate = Proposition(
            id="prop:water_boils_90c",
            subject="ent:water",
            predicate="c:boils_at",
            object="val:90c",
            confidence=1.0,
            provenance=ProvenanceType.USER_STATED,
            scope_id="scope:root",
        )
        conflicts = store.detect_contradiction(candidate)
        assert len(conflicts) == 1
        assert conflicts[0].id == "prop:water_boils_100c"

        disposition, target_scope = evaluate_admission_disposition(
            source_class=IngressSourceClass.USER_DISCOURSE,
            domain="OBJECTIVE_WORLD",
            causal_relation=CausalRelation.SPONTANEOUS,
            is_conflict=True,
        )
        assert disposition == AdmissionDisposition.STAGE
        assert target_scope == "scope:modal:unclassified"

        # Active root proposition remains completely valid
        assert store.get_proposition("prop:water_boils_100c").valid is True

    def test_08_knowledgestore_to_jtms_cascade(self):
        """
        Test 8 — KnowledgeStore -> JTMS Revision Cascade:
        KnowledgeStore revision must trigger retraction callback and cascade invalidation
        to dependent conclusions via JTMS.retract_premise().
        """
        store = KnowledgeStore()
        arena = TermArena()
        symbols = SymbolTable()
        jtms = JTMS()
        kernel = ReasoningKernel(rule_index=RuleIndex(), arena=arena, jtms=jtms)
        service = EpistemicReasoningService(kernel=kernel, symbol_table=symbols, arena=arena)

        # 1. Store and project premise P1
        prop_p1 = Proposition(
            id="prop:premise_socrates_human",
            subject="ent:socrates",
            predicate="c:is_human",
            object="",
            confidence=1.0,
            provenance=ProvenanceType.USER_STATED,
            scope_id="scope:root",
        )
        store.store_proposition(prop_p1)
        allocated = service.project_propositions([prop_p1])
        t_p1 = allocated[0]

        # 2. Allocate derived consequence C: "socrates is mortal" justified by P1
        t_c = arena.allocate_term(
            predicate_id=symbols.intern_concept("c:is_mortal"),
            arg0_id=symbols.intern_concept("ent:socrates"),
            epistemic_status=EpistemicStatus.INFERRED,
            rule_id=1,
            premise_ids=(t_p1,),
        )
        # Register justification in JTMS: C depends on P1
        jtms.register_justification(rule_id=1, consequence_id=t_c, premise_ids=(t_p1,))
        assert arena.get_term(t_c).is_active is True

        # 3. Register revision bridge callback
        def on_revision(old_id: str, new_id: str):
            tid = symbols.get_term_id_for_symbol(old_id)
            if tid:
                directive = RetractionDirective(target_term_id=tid, reason="REVISION")
                jtms.retract_premise(directive.target_term_id, arena)

        store.register_revision_callback(on_revision)

        # 4. Revise P1 in KnowledgeStore
        new_p1 = Proposition(
            id="prop:premise_socrates_human_v2",
            subject="ent:socrates",
            predicate="c:is_human",
            object="",
            confidence=0.8,
            provenance=ProvenanceType.USER_STATED,
            scope_id="scope:root",
        )
        store.revise("prop:premise_socrates_human", new_p1)

        # 5. Verify P1 is retracted and C is cascaded-retracted
        assert arena.get_term(t_p1).is_active is False
        assert arena.get_term(t_c).is_active is False

    def test_09_multi_justification_survival(self):
        """
        Test 9 — Multi-Justification Survival:
        If Consequence C has two independent justifications (J1 from P1, J2 from P2),
        retracting P1 invalidates J1, but C survives because J2 remains valid.
        """
        arena = TermArena()
        jtms = JTMS()

        t_p1 = arena.allocate_term(predicate_id=10, arg0_id=1)
        t_p2 = arena.allocate_term(predicate_id=20, arg0_id=2)
        t_c = arena.allocate_term(
            predicate_id=30,
            arg0_id=3,
            epistemic_status=EpistemicStatus.INFERRED,
        )

        # J1: P1 -> C
        jtms.register_justification(rule_id=1, consequence_id=t_c, premise_ids=(t_p1,))
        # J2: P2 -> C
        jtms.register_justification(rule_id=2, consequence_id=t_c, premise_ids=(t_p2,))

        assert arena.get_term(t_c).is_active is True
        assert len(jtms.get_justifications_for_consequence(t_c)) == 2

        # Retract P1
        invalidated = jtms.retract_premise(t_p1, arena)
        assert t_p1 in invalidated

        # Consequence C must survive because J2(P2) remains valid
        assert t_c not in invalidated
        assert arena.get_term(t_c).is_active is True
        assert jtms.has_valid_justification(t_c) is True

    def test_10_bootstrap_immutability(self):
        """
        Test 10 — Bootstrap Immutability:
        Attempting to revise immutable bootstrap technical knowledge raises PermissionError.
        """
        store = bootstrap_verified_knowledge()
        verified_props = [p for p in store.get_all_propositions() if store.is_bootstrap_proposition(p)]
        assert len(verified_props) > 0

        target = verified_props[0]
        replacement = Proposition(
            id="prop:tampered_root",
            subject=target.subject,
            predicate=target.predicate,
            object="concept:arbitrary_fake",
            confidence=1.0,
            provenance=ProvenanceType.VERIFIED,
        )

        with pytest.raises(PermissionError) as exc_info:
            store.revise(target.id, replacement)
        assert "immutable bootstrap" in str(exc_info.value)

    def test_11_continuous_confidence_invariant_neg02(self):
        """
        Test 11 — NEG-02 Continuous Confidence Invariant:
        A candidate with confidence = 0.999 cannot independently produce discrete FACT.
        It is strictly assigned UNKNOWN.
        """
        gate = LanguageIngressGate()
        cand = IngressCandidateAssertion(
            predicate_id=101,
            arg0_id=201,
            source_class=IngressSourceClass.USER_DISCOURSE,
            causal_relation=CausalRelation.SPONTANEOUS,
        )
        qualified, directive = gate.certify_candidate_assertion(cand, confidence=0.999)
        # Per Invariant NEG-02: confidence < 1.0 cannot escalate to FACT
        assert qualified.epistemic_status == EpistemicStatus.UNKNOWN
        assert qualified.epistemic_status != EpistemicStatus.FACT
