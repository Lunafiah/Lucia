"""
tests/unit/test_universal_epistemic_and_concept_expansion.py

Focused Unit Tests for P23-D Increment 3:
- Universal Epistemic Grounding:
  - Non-architecture queries (e.g., RAM/VRAM, Wakanda) with no evidence evaluate to UNKNOWN and grounded=False.
  - Partial evidence evaluates to PARTIAL.
  - Full evidence evaluates to FACT/KNOWN and grounded=True.
  - False-FACT hole is eliminated.
- Explanatory Concept Material Expansion:
  - PromptAssembler receives verified Concept objects and injects substantive semantic material
    (name, definition, properties, relations, provenance) alongside relational triples.
- Continuation Preservation:
  - Continuation turn inherits pending obligation topic and verified concepts.
- Epistemic Completion Planning Bounding:
  - UNKNOWN explanation request is clamped to concise boundary capacity (~110 tokens) rather than 1400+ tokens.
- Genesis Invariant:
  - data/profile.json remains bit-exact.
"""

from __future__ import annotations

import json
from pathlib import Path
import pytest

from src.core.communication.caps import (
    AdmissibleEvidencePool,
    CognitiveStateSnapshot,
    CommunicativeAct,
    DialogueContextSnapshot,
    EpistemicState,
    PendingUserObligation,
    evaluate_caps,
)
from src.core.communication.response_completion_planner import ResponseCompletionPlanner
from src.core.knowledge.bootstrap import (
    bootstrap_verified_knowledge,
    get_verified_architecture_concepts,
    get_verified_architecture_propositions,
)
from src.core.knowledge.proposition import Concept, Proposition, ProvenanceType
from src.core.knowledge.store import KnowledgeStore
from src.core.models import BehavioralConstraints, SomaticMarkers
from src.core.orchestrator.prompt_assembler import PromptAssembler


class TestUniversalEpistemicGrounding:
    """Verifies that every explanation request goes through universal concept coverage evaluation."""

    def test_non_architecture_explanation_zero_evidence_is_unknown(self):
        """
        Case E proof: 'RAM với VRAM khác nhau thế nào?' with no verified RAM/VRAM evidence
        MUST NOT fall into false-FACT. Must produce UNKNOWN and grounded=False.
        """
        ctx = DialogueContextSnapshot(turn_id=1, input_text="RAM với VRAM khác nhau thế nào?")
        cog = CognitiveStateSnapshot()
        # Evidence pool has only architecture propositions; NO RAM/VRAM propositions
        verified_props = tuple(get_verified_architecture_propositions())
        pool = AdmissibleEvidencePool(verified_propositions=verified_props, user_claims=())

        result = evaluate_caps(dialogue_ctx=ctx, cognitive_state=cog, evidence_pool=pool)

        assert result.act == CommunicativeAct.EXPLAIN_CONCEPT
        assert result.conversational_obligation == "FULFILL_CONCEPT_EXPLANATION"
        # Non-architecture concept with 0 matching evidence must be UNKNOWN
        assert result.epistemic_metadata.status == EpistemicState.UNKNOWN
        assert result.grounded is False
        assert result.resolution_metadata.grounding_status == "UNGROUNDED"
        assert result.focus_argument is None
        assert "chưa có thông tin xác thực trong cơ sở tri thức" in result.directives

    def test_wakanda_explanation_zero_evidence_is_unknown(self):
        """
        Case F proof: 'Wakanda có kiến trúc máy tính như thế nào?' must evaluate to UNKNOWN and grounded=False.
        """
        ctx = DialogueContextSnapshot(turn_id=1, input_text="Wakanda có kiến trúc máy tính như thế nào?")
        cog = CognitiveStateSnapshot()
        verified_props = tuple(get_verified_architecture_propositions())
        pool = AdmissibleEvidencePool(verified_propositions=verified_props, user_claims=())

        result = evaluate_caps(dialogue_ctx=ctx, cognitive_state=cog, evidence_pool=pool)

        assert result.act == CommunicativeAct.EXPLAIN_CONCEPT
        assert result.epistemic_metadata.status == EpistemicState.UNKNOWN
        assert result.grounded is False
        assert result.resolution_metadata.grounding_status == "UNGROUNDED"

    def test_non_architecture_explanation_with_partial_evidence(self):
        """Non-architecture explanation with 1-2 verified propositions produces PARTIAL."""
        ctx = DialogueContextSnapshot(turn_id=1, input_text="Giải thích về giao thức UDP và TCP.")
        cog = CognitiveStateSnapshot()
        sparse_props = (
            Proposition(
                id="prop:udp_proto",
                subject="ent:udp",
                predicate="c:IS_A",
                object="concept:transport_protocol",
                confidence=1.0,
                provenance=ProvenanceType.VERIFIED,
            ),
        )
        pool = AdmissibleEvidencePool(verified_propositions=sparse_props, user_claims=())

        result = evaluate_caps(dialogue_ctx=ctx, cognitive_state=cog, evidence_pool=pool)

        assert result.act == CommunicativeAct.EXPLAIN_CONCEPT
        assert result.epistemic_metadata.status == EpistemicState.PARTIAL
        assert result.grounded is True
        assert result.resolution_metadata.grounding_status == "CONVERSATIONAL_CONTEXT"

    def test_non_architecture_explanation_with_sufficient_evidence(self):
        """Non-architecture explanation with >2 verified propositions produces FACT/KNOWN."""
        ctx = DialogueContextSnapshot(turn_id=1, input_text="Giải thích về giao thức TCP.")
        cog = CognitiveStateSnapshot()
        full_props = (
            Proposition(id="p1", subject="ent:tcp", predicate="c:IS_A", object="concept:protocol", confidence=1.0, provenance=ProvenanceType.VERIFIED),
            Proposition(id="p2", subject="ent:tcp", predicate="c:HAS_HANDSHAKE", object="concept:three_way", confidence=1.0, provenance=ProvenanceType.VERIFIED),
            Proposition(id="p3", subject="ent:tcp", predicate="c:ENSURES", object="concept:reliability", confidence=1.0, provenance=ProvenanceType.VERIFIED),
        )
        pool = AdmissibleEvidencePool(verified_propositions=full_props, user_claims=())

        result = evaluate_caps(dialogue_ctx=ctx, cognitive_state=cog, evidence_pool=pool)

        assert result.act == CommunicativeAct.EXPLAIN_CONCEPT
        assert result.epistemic_metadata.status == EpistemicState.FACT
        assert result.grounded is True
        assert result.resolution_metadata.grounding_status == "CONVERSATIONAL_CONTEXT"

    def test_architecture_explanation_sufficient_evidence(self):
        """Lucia architecture explanation with verified bootstrap produces FACT and grounded=True."""
        ctx = DialogueContextSnapshot(turn_id=1, input_text="Giải thích toàn bộ kiến trúc Lucia cho anh.")
        cog = CognitiveStateSnapshot()
        verified_props = tuple(get_verified_architecture_propositions())
        pool = AdmissibleEvidencePool(verified_propositions=verified_props, user_claims=())

        result = evaluate_caps(dialogue_ctx=ctx, cognitive_state=cog, evidence_pool=pool)

        assert result.act == CommunicativeAct.EXPLAIN_CONCEPT
        assert result.focus_argument == "ent:lucia_architecture"
        assert result.epistemic_metadata.status == EpistemicState.FACT
        assert result.grounded is True


class TestExplanatoryConceptMaterialExpansion:
    """Verifies that PromptAssembler injects substantive semantic concept material."""

    def test_prompt_assembler_injects_rich_concept_definitions_and_properties(self):
        """PromptAssembler must inject concept name, definition, properties, and relations alongside triples."""
        store = bootstrap_verified_knowledge(KnowledgeStore())
        propositions = store.query_relevant("Giải thích toàn bộ kiến trúc Lucia cho anh.", max_results=6)
        concepts = get_verified_architecture_concepts()

        assembler = PromptAssembler()
        somatic = SomaticMarkers(stability=0.9, cognitive_load=0.1, energy=0.9, tension=0.1)
        constraints = BehavioralConstraints(max_tokens=500, temperature=0.7, latency_ms=0, reasoning_depth=0)

        prompt = assembler.assemble(
            somatic=somatic,
            constraints=constraints,
            history=[("user", "Giải thích toàn bộ kiến trúc Lucia cho anh.")],
            knowledge_propositions=propositions,
            knowledge_concepts=concepts,
            planned_completion_capacity=500,
        )

        assert "[GROUNDED KNOWLEDGE]" in prompt
        # Verify atomic relational triples
        assert "(ent:lucia_architecture, c:ORGANIZED_AS, concept:whole_brain_architecture_20w)" in prompt
        assert "[provenance=VERIFIED]" in prompt

        # Verify substantive concept material (NOT just raw IDs)
        assert "Concept: Lucia Technical Architecture (concept:lucia_architecture)" in prompt
        assert "20-Watt Whole Brain Architecture organizing continuous limbic dynamics" in prompt
        assert "power_budget: 20W, paradigm: Whole Brain Architecture" in prompt
        assert "has_subsystem: concept:arch_perception" in prompt

        assert "Concept: Perception & Sensory Ingress Subsystem (concept:arch_perception)" in prompt
        assert "faster-whisper STT and text" in prompt

        assert "Concept: Continuous Limbic Dynamics Subsystem (concept:arch_limbic_affect)" in prompt
        assert "Ordinary Differential Equation (ODE) within a Coupled MT-LNN" in prompt
        assert "attractor: philia" in prompt

        assert "Concept: Cognitive Core & Reasoning Subsystem (concept:arch_cognition)" in prompt
        assert "Strong Kleene K3" in prompt
        assert "JTMS" in prompt

        assert "Concept: Associative Memory & Relational Dynamics Subsystem (concept:arch_memory)" in prompt
        assert "Kanerva Sparse Distributed Memory (SDM)" in prompt

        assert "Concept: Presentation & Language Realization Subsystem (concept:arch_realization)" in prompt
        assert "ADR-035 Fail-Closed Semantic Fidelity Gate" in prompt


class TestContinuationPreservation:
    """Verifies that continuation turns preserve explanatory concept material and workload."""

    def test_continuation_preserves_concept_coverage_and_epistemic_status(self):
        """Continuation of pending architecture obligation preserves epistemic FACT status."""
        pending_ob = PendingUserObligation(
            obligation_type="FULFILL_CONCEPT_EXPLANATION",
            originating_turn=1,
            target_topic="ent:lucia_architecture",
            completed=False,
            ttl_turns=2,
        )
        ctx = DialogueContextSnapshot(
            turn_id=2,
            input_text="Vậy bắt đầu đi.",
            pending_user_obligation=pending_ob,
        )
        cog = CognitiveStateSnapshot()
        verified_props = tuple(get_verified_architecture_propositions())
        pool = AdmissibleEvidencePool(verified_propositions=verified_props, user_claims=())

        result = evaluate_caps(dialogue_ctx=ctx, cognitive_state=cog, evidence_pool=pool)

        assert result.act == CommunicativeAct.EXPLAIN_CONCEPT
        assert result.focus_argument == "ent:lucia_architecture"
        assert result.epistemic_metadata.status == EpistemicState.FACT
        assert result.grounded is True
        assert result.provenance_metadata.origin == "PENDING_OBLIGATION_CONTINUATION"


class TestEpistemicCompletionCapacityClamping:
    """Verifies that UNKNOWN epistemic requests are strictly bounded in generation capacity."""

    def test_unknown_explanation_capacity_is_clamped(self):
        """When epistemic status is UNKNOWN, ResponseCompletionPlanner clamps capacity to boundary budget."""
        planner = ResponseCompletionPlanner()
        plan_vi = planner.plan(
            epistemic_status=EpistemicState.UNKNOWN,
            available_facets=0,
            required_facets=3,
            conversational_obligation="FULFILL_CONCEPT_EXPLANATION",
            target_language="vi",
        )
        # Clamped to concise refusal/boundary statement (~90-125 tokens), NOT deep 1400 tokens
        assert plan_vi.diagnostic_metadata["branch"] == "UNKNOWN_BOUNDED"
        assert plan_vi.completion_capacity <= 140
        assert plan_vi.completion_capacity >= 50

        plan_en = planner.plan(
            epistemic_status=EpistemicState.UNKNOWN,
            available_facets=0,
            required_facets=3,
            conversational_obligation="FULFILL_CONCEPT_EXPLANATION",
            target_language="en",
        )
        assert plan_en.diagnostic_metadata["branch"] == "UNKNOWN_BOUNDED"
        assert plan_en.completion_capacity <= 65


class TestGenesisInvariant:
    """Verifies INV-8: Genesis gate remains strictly locked."""

    def test_genesis_profile_locked(self):
        profile_path = Path("data/profile.json")
        assert profile_path.exists()
        data = json.loads(profile_path.read_text(encoding="utf-8").strip())
        assert data == {"is_onboarded": False}
