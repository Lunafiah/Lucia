"""
tests/unit/test_epistemic_grounding_bootstrap.py

Focused Unit Tests for P23-D Increment 1:
- Epistemic Grounding (request/routing vs knowledge availability vs epistemic status)
- EXPLAIN_CONCEPT does NOT automatically imply KNOWN/FACT
- Zero evidence -> UNKNOWN (grounded=False)
- Partial evidence -> PARTIAL (grounded=True)
- Sufficient evidence -> FACT/KNOWN (grounded=True)
- Unrelated verified evidence does not satisfy architecture target
- S8 KnowledgeStore retrieval of seeded verified architecture propositions
- Grounded knowledge reaches prompt assembly
- Genesis Invariant (data/profile.json == {"is_onboarded": false})
"""

import json
from pathlib import Path
import pytest

from src.core.communication.caps import (
    AdmissibleEvidencePool,
    CognitiveStateSnapshot,
    CommunicativeAct,
    DialogueContextSnapshot,
    EpistemicState,
    evaluate_caps,
)
from src.core.knowledge.bootstrap import (
    bootstrap_verified_knowledge,
    get_verified_architecture_concepts,
    get_verified_architecture_propositions,
)
from src.core.knowledge.proposition import Proposition, ProvenanceType
from src.core.knowledge.store import KnowledgeStore
from src.core.models import BehavioralConstraints, SomaticMarkers
from src.core.orchestrator.prompt_assembler import PromptAssembler


class TestP23DIncrement1EpistemicGrounding:
    """Verifies epistemic boundary separation and verified architecture bootstrapping."""

    def test_explanation_request_zero_evidence_is_unknown(self):
        """Explanation request with zero evidence must produce EpistemicState.UNKNOWN and grounded=False."""
        ctx = DialogueContextSnapshot(turn_id=1, input_text="Giải thích toàn bộ kiến trúc Lucia cho anh.")
        cog = CognitiveStateSnapshot()
        empty_pool = AdmissibleEvidencePool(verified_propositions=(), user_claims=())

        result = evaluate_caps(dialogue_ctx=ctx, cognitive_state=cog, evidence_pool=empty_pool)

        # Routing recognition is preserved
        assert result.act == CommunicativeAct.EXPLAIN_CONCEPT
        assert result.focus_argument == "ent:lucia_architecture"
        assert result.conversational_obligation == "FULFILL_CONCEPT_EXPLANATION"

        # Epistemic grounding boundary enforced
        assert result.epistemic_metadata.status == EpistemicState.UNKNOWN
        assert result.grounded is False
        assert result.resolution_metadata.grounding_status == "UNGROUNDED"

    def test_explanation_request_partial_evidence_is_partial(self):
        """Explanation request with sparse/insufficient evidence produces EpistemicState.PARTIAL."""
        ctx = DialogueContextSnapshot(turn_id=1, input_text="Giải thích toàn bộ kiến trúc Lucia cho anh.")
        cog = CognitiveStateSnapshot()
        # Single verified proposition covering only limbic ODE
        sparse_props = (
            Proposition(
                id="prop:arch_limbic_core",
                subject="ent:lucia_architecture",
                predicate="c:HAS_LIMBIC_CORE",
                object="concept:arch_limbic_affect",
                confidence=1.0,
                provenance=ProvenanceType.VERIFIED,
                evidence_ids=["docs/ARCHITECTURE.md#sec1.1"],
            ),
        )
        partial_pool = AdmissibleEvidencePool(verified_propositions=sparse_props, user_claims=())

        result = evaluate_caps(dialogue_ctx=ctx, cognitive_state=cog, evidence_pool=partial_pool)

        assert result.act == CommunicativeAct.EXPLAIN_CONCEPT
        assert result.focus_argument == "ent:lucia_architecture"
        assert result.epistemic_metadata.status == EpistemicState.PARTIAL
        assert result.grounded is True
        assert result.resolution_metadata.grounding_status == "CONVERSATIONAL_CONTEXT"

    def test_explanation_request_sufficient_evidence_is_fact_known(self):
        """Explanation request with verified multi-facet coverage produces EpistemicState.FACT (KNOWN)."""
        ctx = DialogueContextSnapshot(turn_id=1, input_text="Giải thích toàn bộ kiến trúc Lucia cho anh.")
        cog = CognitiveStateSnapshot()
        verified_props = tuple(get_verified_architecture_propositions())
        full_pool = AdmissibleEvidencePool(verified_propositions=verified_props, user_claims=())

        result = evaluate_caps(dialogue_ctx=ctx, cognitive_state=cog, evidence_pool=full_pool)

        assert result.act == CommunicativeAct.EXPLAIN_CONCEPT
        assert result.focus_argument == "ent:lucia_architecture"
        assert result.epistemic_metadata.status == EpistemicState.FACT
        assert result.grounded is True
        assert result.resolution_metadata.grounding_status == "CONVERSATIONAL_CONTEXT"

    def test_unrelated_verified_evidence_does_not_satisfy_architecture_target(self):
        """Unrelated verified propositions must not falsely satisfy the architecture target."""
        ctx = DialogueContextSnapshot(turn_id=1, input_text="Giải thích toàn bộ kiến trúc Lucia cho anh.")
        cog = CognitiveStateSnapshot()
        unrelated_props = (
            Proposition(
                id="prop:first_conversation",
                subject="ent:lucia",
                predicate="c:IS_FIRST_CONVERSATION",
                object="true",
                confidence=1.0,
                provenance=ProvenanceType.VERIFIED,
            ),
            Proposition(
                id="prop:turn_count",
                subject="ent:dialogue",
                predicate="c:TURN_COUNT",
                object="5",
                confidence=1.0,
                provenance=ProvenanceType.VERIFIED,
            ),
            Proposition(
                id="prop:weather_today",
                subject="ent:weather",
                predicate="c:STATUS",
                object="sunny",
                confidence=1.0,
                provenance=ProvenanceType.VERIFIED,
            ),
        )
        pool = AdmissibleEvidencePool(verified_propositions=unrelated_props, user_claims=())

        result = evaluate_caps(dialogue_ctx=ctx, cognitive_state=cog, evidence_pool=pool)

        # Unrelated propositions must NOT satisfy the architecture concept
        assert result.act == CommunicativeAct.EXPLAIN_CONCEPT
        assert result.focus_argument == "ent:lucia_architecture"
        assert result.epistemic_metadata.status == EpistemicState.UNKNOWN
        assert result.grounded is False

    def test_architecture_retrieval_returns_seeded_verified_propositions(self):
        """KnowledgeStore correctly indexes and retrieves verified architecture propositions in Vietnamese & English."""
        store = bootstrap_verified_knowledge(KnowledgeStore())

        # Vietnamese natural query
        results_vi = store.query_relevant("Giải thích toàn bộ kiến trúc Lucia cho anh.", max_results=5)
        assert len(results_vi) >= 5
        for p in results_vi:
            assert p.subject == "ent:lucia_architecture"
            assert p.provenance == ProvenanceType.VERIFIED
            assert len(p.evidence_ids) > 0
            assert any("ARCHITECTURE.md" in eid for eid in p.evidence_ids)

        # English natural query
        results_en = store.query_relevant("Explain the architecture of Lucia to me.", max_results=5)
        assert len(results_en) >= 5
        for p in results_en:
            assert p.subject == "ent:lucia_architecture"

    def test_grounded_knowledge_reaches_prompt_assembly(self):
        """Retrieved architecture propositions are formatted into [GROUNDED KNOWLEDGE] in prompt assembly."""
        store = bootstrap_verified_knowledge(KnowledgeStore())
        retrieved_props = store.query_relevant("Giải thích toàn bộ kiến trúc Lucia cho anh.", max_results=5)

        assembler = PromptAssembler()
        somatic = SomaticMarkers(stability=0.9, cognitive_load=0.1, energy=0.9, tension=0.1)
        constraints = BehavioralConstraints(max_tokens=200, temperature=0.7, latency_ms=0, reasoning_depth=0)
        prompt = assembler.assemble(
            somatic=somatic,
            constraints=constraints,
            history=[("user", "Giải thích toàn bộ kiến trúc Lucia cho anh.")],
            knowledge_propositions=retrieved_props,
        )

        assert "[GROUNDED KNOWLEDGE]" in prompt
        assert "(ent:lucia_architecture, c:ORGANIZED_AS, concept:whole_brain_architecture_20w)" in prompt
        assert "(ent:lucia_architecture, c:HAS_LIMBIC_CORE, concept:arch_limbic_affect)" in prompt
        assert "(ent:lucia_architecture, c:HAS_MEMORY_SUBSTRATE, concept:arch_memory)" in prompt

        # Without propositions, [GROUNDED KNOWLEDGE] is omitted
        empty_prompt = assembler.assemble(
            somatic=somatic,
            constraints=constraints,
            history=[("user", "Hello")],
            knowledge_propositions=[],
        )
        assert "[GROUNDED KNOWLEDGE]" not in empty_prompt

    def test_genesis_invariant_remains_untouched(self):
        """Invariant INV-8: data/profile.json must remain bit-exact {'is_onboarded': false}."""
        profile_path = Path("data/profile.json")
        assert profile_path.exists(), "data/profile.json must exist"
        raw_text = profile_path.read_text(encoding="utf-8").strip()
        data = json.loads(raw_text)
        assert data == {"is_onboarded": False}
