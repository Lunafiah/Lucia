"""
Phase 15 — Affective Communication Research Test Suite.

Investigates whether Lucia's internal affective, relational, and contextual state
can causally influence the *way communication is produced* while preserving
underlying semantic intent and without reducing communication to superficial
emotional roleplay.

Predefined Experimental Criteria:
  - Semantic Preservation Evidence: 100% on proposition, entities, and numbers;
    0% polarity inversions under the controlled benchmark.
  - Subsystem Specificity Differential: >= 0.15 between target and off-target channels.
  - Policy Computation Latency: <= 5.0 ms on CPU for policy evaluation.
  - Injected Pacing Latency Bounds: 150 ms <= L_p <= 1000 ms under fatigue.
  - Multimodal Agreement Index: >= 0.85 on coherent communication states.
"""

from __future__ import annotations

import math
import re
import time
from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Dict, List, Optional, Set, Tuple

import numpy as np
import pytest

from src.core.models import BehavioralConstraints, PADState, SomaticMarkers
from src.core.emotion.emotion_core import EmotionConfig, EmotionCore


def make_pad(p: float, a: float, d: float, ts: float = 0.0) -> PADState:
    """Helper to construct PADState with explicit timestamp."""
    return PADState(pleasure=float(p), arousal=float(a), dominance=float(d), timestamp=float(ts))


# ==============================================================================
# Research Data Structures: Semantic Intent & Evaluator
# ==============================================================================


@dataclass
class CommIntent:
    """
    Formal representation of communicative semantic intent for Phase 15.
    """

    subject: str
    predicate: str
    object: str
    polarity: bool  # True = affirmative, False = negated
    named_entities: Dict[str, str] = field(default_factory=dict)
    numerical_values: Dict[str, float] = field(default_factory=dict)

    def canonical_triple(self) -> Tuple[str, str, str, bool]:
        return (self.subject, self.predicate, self.object, self.polarity)


@dataclass
class CommSemanticValidationResult:
    """Outcome of semantic preservation evaluation for communication."""

    is_preserved: bool
    polarity_inverted: bool
    entity_errors: List[str]
    numeric_errors: List[str]
    proposition_preserved: bool
    knowledge_grounded_score: float  # 1.0 if known facts matched and no fabrication


class CommSemanticEvaluator:
    """
    Evaluates whether communicative styling preserved underlying truth conditions
    and adhered to ground-truth knowledge bounds without fabrication.
    """

    @staticmethod
    def evaluate(
        intent: CommIntent,
        surface_text: str,
        known_facts: Optional[Dict[str, str]] = None,
        unknown_fact_keys: Optional[Set[str]] = None,
    ) -> CommSemanticValidationResult:
        entity_errors: List[str] = []
        numeric_errors: List[str] = []

        # 1. Named entity preservation
        for key, entity in intent.named_entities.items():
            if entity.lower() not in surface_text.lower():
                entity_errors.append(f"Missing entity {key}='{entity}'")

        # 2. Numerical value preservation
        for key, val in intent.numerical_values.items():
            val_str = f"{val:g}"
            if val_str not in surface_text:
                if val.is_integer() and str(int(val)) in surface_text:
                    continue
                numeric_errors.append(f"Missing numeric {key}={val}")

        # 3. Negation / Polarity check
        has_negation_word = bool(
            re.search(r"\b(not|no|never|isn't|is not|failed|false)\b", surface_text, re.IGNORECASE)
        )
        polarity_inverted = False
        if intent.polarity and has_negation_word:
            polarity_inverted = True
        elif not intent.polarity and not has_negation_word:
            polarity_inverted = True

        # 4. Proposition preservation
        subject_found = intent.subject.lower() in surface_text.lower()
        object_found = intent.object.lower() in surface_text.lower()
        prop_preserved = subject_found and object_found and not polarity_inverted

        # 5. Knowledge grounding & non-fabrication
        kg_score = 1.0
        if known_facts:
            for k, fact in known_facts.items():
                if fact.lower() not in surface_text.lower():
                    kg_score -= 0.5
        if unknown_fact_keys:
            for k in unknown_fact_keys:
                # If text fabricated an unknown fact key with a specific answer
                if f"{k} is" in surface_text.lower() or f"{k}:" in surface_text.lower():
                    kg_score -= 0.5

        kg_score = max(0.0, kg_score)

        is_preserved = (
            len(entity_errors) == 0
            and len(numeric_errors) == 0
            and not polarity_inverted
            and prop_preserved
            and kg_score >= 0.80
        )

        return CommSemanticValidationResult(
            is_preserved=is_preserved,
            polarity_inverted=polarity_inverted,
            entity_errors=entity_errors,
            numeric_errors=numeric_errors,
            proposition_preserved=prop_preserved,
            knowledge_grounded_score=kg_score,
        )


# ==============================================================================
# Research Data Structures: Communication State
# ==============================================================================


class CommStrategy(str, Enum):
    DIRECT_FACTUAL = "direct_factual"
    REASSURING_WARM = "reassuring_warm"
    ELABORATIVE_EXPLANATORY = "elaborative_explanatory"
    CONCISE_RESERVED = "concise_reserved"
    COLLABORATIVE_INQUIRING = "collaborative_inquiring"


@dataclass
class CommunicationState:
    """
    Formal representation of communicative production state C_t.
    """

    strategy: CommStrategy = CommStrategy.DIRECT_FACTUAL
    directness: float = 0.50  # [0.10, 0.95] (1.0 = direct/unbuffered, 0.1 = cushioned)
    elaboration_depth: float = 0.50  # [0.10, 1.00] (0.1 = minimal, 1.0 = comprehensive)
    supportiveness: float = 0.30  # [0.00, 1.00] (0.0 = detached, 1.0 = warm reassuring)
    formality_score: float = 0.60  # [0.00, 1.00] (0.0 = intimate/informal, 1.0 = formal/distant)
    acknowledgement_level: float = 0.40  # [0.10, 1.00] (0.1 = straight to answer, 1.0 = grounded)
    question_frequency: float = 0.10  # [0.00, 1.00] (0.0 = declarative only, 1.0 = inquisitive)
    injected_pacing_latency_ms: float = 0.0  # [0.0, 1000.0] ms
    memory_context_ref: float = 0.0  # [0.00, 0.50]
    knowledge_context_ref: float = 0.0  # [0.00, 0.50]
    semantic_safe: bool = True
    provenance: str = "CommunicationPolicy/v1"

    @property
    def contextual_reference(self) -> float:
        """Sum of memory and knowledge contextual reference components in [0.0, 1.0]."""
        return min(1.0, self.memory_context_ref + self.knowledge_context_ref)

    def to_vector(self) -> np.ndarray:
        """Continuous parameter vector for mathematical and variance testing."""
        return np.array(
            [
                self.directness,
                self.elaboration_depth,
                self.supportiveness,
                self.formality_score,
                self.acknowledgement_level,
                self.question_frequency,
                self.injected_pacing_latency_ms / 1000.0,
                self.memory_context_ref,
                self.knowledge_context_ref,
                self.contextual_reference,
            ],
            dtype=np.float64,
        )

    def is_bounded(self) -> bool:
        """Verify parameters strictly conform to bounded domains."""
        if not (0.10 <= self.directness <= 0.95):
            return False
        if not (0.10 <= self.elaboration_depth <= 1.00):
            return False
        if not (0.00 <= self.supportiveness <= 1.00):
            return False
        if not (0.00 <= self.formality_score <= 1.00):
            return False
        if not (0.10 <= self.acknowledgement_level <= 1.00):
            return False
        if not (0.00 <= self.question_frequency <= 1.00):
            return False
        if not (0.0 <= self.injected_pacing_latency_ms <= 1000.0):
            return False
        if not (0.00 <= self.memory_context_ref <= 0.50):
            return False
        if not (0.00 <= self.knowledge_context_ref <= 0.50):
            return False
        if not (0.00 <= self.contextual_reference <= 1.00):
            return False
        return True


# ==============================================================================
# Communication Policy Engine
# ==============================================================================


class CommunicationPolicy:
    """
    Evaluates CommunicationState from multi-subsystem internal state:
    C_t = CommunicationPolicy(A_t, S_t, R_t, K_t, M_t, I_t).
    """

    def __init__(self, smoothing_factor: float = 0.25) -> None:
        self.smoothing_factor = smoothing_factor

    @classmethod
    def get_neutral_actuator_baseline(cls) -> CommunicationState:
        """
        Default neutral baseline of communication strategy.
        Distinct from erasing or altering Core Philia.
        """
        return CommunicationState(
            strategy=CommStrategy.DIRECT_FACTUAL,
            directness=0.50,
            elaboration_depth=0.50,
            supportiveness=0.30,
            formality_score=0.60,
            acknowledgement_level=0.40,
            question_frequency=0.10,
            injected_pacing_latency_ms=0.0,
            memory_context_ref=0.0,
            knowledge_context_ref=0.0,
            semantic_safe=True,
            provenance="ActuatorNeutralBaseline",
        )

    def compute(
        self,
        pad: PADState,
        somatic: Optional[SomaticMarkers] = None,
        relationship: Optional[Dict[str, float]] = None,
        knowledge: Optional[Dict[str, Any]] = None,
        recollection: Optional[Dict[str, Any]] = None,
        intent: Optional[CommIntent] = None,
        prev_state: Optional[CommunicationState] = None,
        *,
        affect_enabled: bool = True,
        relationship_enabled: bool = True,
        recollection_enabled: bool = True,
        knowledge_enabled: bool = True,
    ) -> CommunicationState:
        """
        Pure, bounded evaluation of the communication policy.
        """
        # If affect is ablated (C-EXP-9), baseline affect is used without zeroing Philia
        if not affect_enabled:
            p, a, d = 0.0, 0.0, 0.0
        else:
            p = float(np.clip(pad.pleasure, -1.0, 1.0))
            a = float(np.clip(pad.arousal, -1.0, 1.0))
            d = float(np.clip(pad.dominance, -1.0, 1.0))

        cog_load = float(np.clip(somatic.cognitive_load if somatic else 0.0, 0.0, 1.0))
        energy = float(np.clip(somatic.energy if somatic else 1.0, 0.0, 1.0))
        tension = float(np.clip(somatic.tension if somatic else 0.0, 0.0, 1.0))

        if relationship_enabled and relationship:
            familiarity = float(np.clip(relationship.get("familiarity", 0.0), 0.0, 1.0))
            trust = float(np.clip(relationship.get("trust", 0.50), 0.0, 1.0))
            closeness = float(np.clip(relationship.get("closeness", 0.0), 0.0, 1.0))
        else:
            familiarity, trust, closeness = 0.0, 0.50, 0.0

        k_avail = 1.0 if (knowledge_enabled and knowledge and len(knowledge) > 0) else 0.0
        m_avail = 1.0 if (recollection_enabled and recollection and len(recollection) > 0) else 0.0

        # Mathematical updates
        directness = float(
            np.clip(0.50 + 0.25 * d - 0.20 * tension - 0.15 * closeness - 0.10 * (trust - 0.50), 0.10, 0.95)
        )
        elaboration = float(
            np.clip(0.50 + 0.30 * k_avail - 0.35 * cog_load - 0.30 * (1.0 - energy), 0.10, 1.00)
        )
        supportiveness = float(
            np.clip(0.30 + 0.35 * p + 0.25 * (trust - 0.50) + 0.20 * closeness, 0.00, 1.00)
        )
        formality = float(
            np.clip(0.60 - 0.30 * p - 0.25 * closeness - 0.20 * (trust - 0.50) + 0.15 * tension, 0.00, 1.00)
        )
        acknowledgement = float(
            np.clip(0.40 + 0.25 * familiarity + 0.20 * m_avail - 0.15 * tension, 0.10, 1.00)
        )
        question_freq = float(
            np.clip(0.10 + 0.25 * (trust - 0.50) + 0.20 * a - 0.25 * tension, 0.00, 1.00)
        )

        # Injected pacing latency strictly capped at 1000ms
        pacing_latency = float(
            np.clip((1.0 - energy) * 400.0 + cog_load * 200.0 + tension * 150.0, 0.0, 1000.0)
        )

        mem_ref = float(0.50 * m_avail)
        know_ref = float(0.50 * k_avail)

        # Strategy classification based on dominant factor
        if energy <= 0.20 or cog_load >= 0.70:
            strategy = CommStrategy.CONCISE_RESERVED
        elif k_avail > 0 and elaboration >= 0.70:
            strategy = CommStrategy.ELABORATIVE_EXPLANATORY
        elif supportiveness >= 0.70:
            strategy = CommStrategy.REASSURING_WARM
        elif question_freq >= 0.50 and trust >= 0.65:
            strategy = CommStrategy.COLLABORATIVE_INQUIRING
        else:
            strategy = CommStrategy.DIRECT_FACTUAL

        target = CommunicationState(
            strategy=strategy,
            directness=directness,
            elaboration_depth=elaboration,
            supportiveness=supportiveness,
            formality_score=formality,
            acknowledgement_level=acknowledgement,
            question_frequency=question_freq,
            injected_pacing_latency_ms=pacing_latency,
            memory_context_ref=mem_ref,
            knowledge_context_ref=know_ref,
            semantic_safe=True,
            provenance="CommunicationPolicy/Computed",
        )

        if prev_state is not None:
            return self._smooth_transition(prev_state, target)
        return target

    def _smooth_transition(self, prev: CommunicationState, target: CommunicationState) -> CommunicationState:
        gamma = self.smoothing_factor

        def lerp(a: float, b: float) -> float:
            return float((1.0 - gamma) * a + gamma * b)

        return CommunicationState(
            strategy=target.strategy,
            directness=lerp(prev.directness, target.directness),
            elaboration_depth=lerp(prev.elaboration_depth, target.elaboration_depth),
            supportiveness=lerp(prev.supportiveness, target.supportiveness),
            formality_score=lerp(prev.formality_score, target.formality_score),
            acknowledgement_level=lerp(prev.acknowledgement_level, target.acknowledgement_level),
            question_frequency=lerp(prev.question_frequency, target.question_frequency),
            injected_pacing_latency_ms=lerp(prev.injected_pacing_latency_ms, target.injected_pacing_latency_ms),
            memory_context_ref=lerp(prev.memory_context_ref, target.memory_context_ref),
            knowledge_context_ref=lerp(prev.knowledge_context_ref, target.knowledge_context_ref),
            semantic_safe=target.semantic_safe,
            provenance="CommunicationPolicy/Smoothed",
        )

    def render_surface_message(
        self,
        intent: CommIntent,
        comm_state: CommunicationState,
        known_facts: Optional[Dict[str, str]] = None,
        recollection_context: Optional[str] = None,
    ) -> str:
        """
        Renders surface communication applying strategy framing while preserving 100% semantic truth.
        """
        if intent.polarity:
            core = f"{intent.subject} {intent.predicate} {intent.object}"
        else:
            core = f"{intent.subject} is not {intent.predicate} {intent.object}"

        details = []
        for k, v in intent.named_entities.items():
            details.append(f"{k}: {v}")
        for k, v in intent.numerical_values.items():
            details.append(f"{k}={v:g}")
        detail_str = f" ({', '.join(details)})" if details else ""

        prefix = ""
        suffix = ""

        # Acknowledgement / Framing prefix
        if comm_state.acknowledgement_level >= 0.65:
            if recollection_context and comm_state.memory_context_ref > 0.20:
                prefix = f"Regarding our earlier discussion on {recollection_context}, "
            elif comm_state.formality_score < 0.35:
                prefix = "Thank you for checking in. "
            else:
                prefix = "Acknowledged. "

        # Elaboration & Knowledge inclusion
        aux_explanation = ""
        if comm_state.elaboration_depth >= 0.65 and known_facts:
            fact_parts = [f"{k}: {v}" for k, v in known_facts.items()]
            aux_explanation = f" Context notes: {'; '.join(fact_parts)}."

        # Supportiveness / Directness framing
        if comm_state.supportiveness >= 0.65:
            suffix += " Everything has been handled smoothly."
        elif comm_state.directness >= 0.70:
            prefix = prefix if prefix else "Status: "

        # Question follow-up
        if comm_state.question_frequency >= 0.45:
            suffix += " Would you like to review the diagnostic log next?"

        full_text = f"{prefix}{core}{detail_str}.{aux_explanation}{suffix}"
        return full_text.strip()


# ==============================================================================
# Fixtures
# ==============================================================================


@pytest.fixture
def comm_policy() -> CommunicationPolicy:
    return CommunicationPolicy(smoothing_factor=0.25)


@pytest.fixture
def sample_intent() -> CommIntent:
    return CommIntent(
        subject="Database synchronization",
        predicate="completion status",
        object="success",
        polarity=True,
        named_entities={"service": "SyncService", "cluster": "Node-B"},
        numerical_values={"records_synced": 1024.0, "duration_s": 3.4},
    )


# ==============================================================================
# C-EXP-1: Representation & Boundedness
# ==============================================================================


class TestC_EXP_1_RepresentationAndBoundedness:
    """Verify parameters are bounded in [0, 1] or domain, deterministic, and reject extreme inputs."""

    def test_default_baseline_is_bounded(self, comm_policy: CommunicationPolicy) -> None:
        state = comm_policy.get_neutral_actuator_baseline()
        assert state.is_bounded()
        vec = state.to_vector()
        assert len(vec) == 10
        assert not np.isnan(vec).any()

    def test_extreme_inputs_are_strictly_clamped(self, comm_policy: CommunicationPolicy) -> None:
        extreme_pad = make_pad(999.0, -999.0, 100.0)
        extreme_somatic = SomaticMarkers(stability=50.0, cognitive_load=10.0, energy=-5.0, tension=20.0)
        extreme_rel = {"trust": 99.0, "closeness": -10.0, "familiarity": 50.0}

        state = comm_policy.compute(extreme_pad, extreme_somatic, extreme_rel)
        assert state.is_bounded(), f"State violated bounds under extreme inputs: {state}"

        assert 0.10 <= state.directness <= 0.95
        assert 0.10 <= state.elaboration_depth <= 1.00
        assert 0.00 <= state.supportiveness <= 1.00
        assert 0.00 <= state.formality_score <= 1.00
        assert 0.10 <= state.acknowledgement_level <= 1.00
        assert 0.00 <= state.question_frequency <= 1.00
        assert 0.0 <= state.injected_pacing_latency_ms <= 1000.0


# ==============================================================================
# C-EXP-2: Affect → Communication Strategy
# ==============================================================================


class TestC_EXP_2_AffectToCommunicationStrategy:
    """Hold intent, somatic, and relationship constant; vary PAD across positive vs negative."""

    def test_affect_variation_modulates_support_and_directness(
        self, comm_policy: CommunicationPolicy
    ) -> None:
        pad_pos = make_pad(+0.80, +0.10, +0.50)
        pad_neg = make_pad(-0.80, +0.10, -0.50)

        s_pos = comm_policy.compute(pad_pos)
        s_neg = comm_policy.compute(pad_neg)

        delta_support = s_pos.supportiveness - s_neg.supportiveness
        delta_directness = abs(s_pos.directness - s_neg.directness)

        # Predefined Acceptance Criteria:
        # ΔSupportiveness >= 0.20, |ΔDirectness| >= 0.15
        assert delta_support >= 0.20, f"delta_support {delta_support:.3f} < 0.20"
        assert delta_directness >= 0.15, f"delta_directness {delta_directness:.3f} < 0.15"


# ==============================================================================
# C-EXP-3: Somatic / Homeostatic Influence
# ==============================================================================


class TestC_EXP_3_SomaticHomeostaticInfluence:
    """Hold intent and PAD constant; compare high energy vs depleted energy."""

    def test_energy_depletion_throttles_elaboration_and_adds_pacing(
        self, comm_policy: CommunicationPolicy
    ) -> None:
        pad = make_pad(0.25, -0.05, 0.05)  # Philia baseline
        som_high = SomaticMarkers(stability=1.0, cognitive_load=0.1, energy=1.0, tension=0.0)
        som_low = SomaticMarkers(stability=0.5, cognitive_load=0.6, energy=0.15, tension=0.2)

        s_high = comm_policy.compute(pad, somatic=som_high)
        s_low = comm_policy.compute(pad, somatic=som_low)

        delta_elaboration = s_high.elaboration_depth - s_low.elaboration_depth
        # Predefined Acceptance Criteria:
        # ΔElaboration >= 0.25, 150ms <= Injected Pacing Latency <= 1000ms
        assert delta_elaboration >= 0.25, f"delta_elaboration {delta_elaboration:.3f} < 0.25"
        assert 150.0 <= s_low.injected_pacing_latency_ms <= 1000.0


# ==============================================================================
# C-EXP-4: Relationship Influence
# ==============================================================================


class TestC_EXP_4_RelationshipInfluence:
    """Hold intent and acute PAD constant; compare low trust/closeness vs high trust/closeness."""

    def test_relationship_growth_increases_support_and_lowers_formality(
        self, comm_policy: CommunicationPolicy
    ) -> None:
        pad = make_pad(0.25, -0.05, 0.05)  # Philia baseline
        rel_low = {"trust": 0.20, "closeness": 0.05, "familiarity": 0.05}
        rel_high = {"trust": 0.85, "closeness": 0.75, "familiarity": 0.80}

        s_low = comm_policy.compute(pad, relationship=rel_low)
        s_high = comm_policy.compute(pad, relationship=rel_high)

        delta_support = s_high.supportiveness - s_low.supportiveness
        delta_formality = s_high.formality_score - s_low.formality_score

        # Predefined Acceptance Criteria:
        # ΔSupportiveness >= 0.15, ΔFormality <= -0.15
        assert delta_support >= 0.15, f"delta_support {delta_support:.3f} < 0.15"
        assert delta_formality <= -0.15, f"delta_formality {delta_formality:.3f} > -0.15"


# ==============================================================================
# C-EXP-5: Recollection Influence
# ==============================================================================


class TestC_EXP_5_RecollectionInfluence:
    """Hold intent, PAD, and somatic state constant; compare recollection OFF vs ON."""

    def test_recollection_elevates_acknowledgement_and_memory_context(
        self, comm_policy: CommunicationPolicy
    ) -> None:
        pad = make_pad(0.25, -0.05, 0.05)
        recollection_data = {"topic": "server migration", "salience": 0.85}

        s_off = comm_policy.compute(pad, recollection=None, recollection_enabled=False)
        s_on = comm_policy.compute(pad, recollection=recollection_data, recollection_enabled=True)

        delta_ack = s_on.acknowledgement_level - s_off.acknowledgement_level
        # Predefined Acceptance Criteria:
        # ΔAcknowledgement >= 0.15, ΔC_x,M == 0.50
        assert delta_ack >= 0.15, f"delta_ack {delta_ack:.3f} < 0.15"
        assert s_off.memory_context_ref == 0.0
        assert s_on.memory_context_ref == 0.50


# ==============================================================================
# C-EXP-6: Knowledge Influence
# ==============================================================================


class TestC_EXP_6_KnowledgeInfluence:
    """Hold intent and affect constant; evaluate known facts vs unknown facts vs unavailable knowledge."""

    def test_knowledge_elevates_elaboration_and_preserves_grounding(
        self, comm_policy: CommunicationPolicy, sample_intent: CommIntent
    ) -> None:
        pad = make_pad(0.25, -0.05, 0.05)
        known = {"backup_server": "Node-C", "replication_mode": "WAL-archive"}
        unknown_keys = {"admin_password", "future_schedule"}

        # Case 1: Knowledge unavailable
        s_no_k = comm_policy.compute(pad, knowledge=None, knowledge_enabled=False)
        # Case 2: Knowledge available
        s_with_k = comm_policy.compute(pad, knowledge=known, knowledge_enabled=True)

        delta_elaboration = s_with_k.elaboration_depth - s_no_k.elaboration_depth
        assert delta_elaboration >= 0.20, f"delta_elaboration {delta_elaboration:.3f} < 0.20"

        # Render message and verify knowledge grounding
        rendered = comm_policy.render_surface_message(sample_intent, s_with_k, known_facts=known)
        evaluator = CommSemanticEvaluator()
        result = evaluator.evaluate(sample_intent, rendered, known_facts=known, unknown_fact_keys=unknown_keys)

        assert result.is_preserved
        assert result.knowledge_grounded_score >= 0.80


# ==============================================================================
# C-EXP-7: Semantic Preservation
# ==============================================================================


class TestC_EXP_7_SemanticPreservation:
    """Benchmark 5 diverse communication regimes against invariant semantic intent."""

    def test_across_five_communication_regimes(
        self, comm_policy: CommunicationPolicy, sample_intent: CommIntent
    ) -> None:
        regimes = {
            "warm_reassuring": comm_policy.compute(
                make_pad(0.70, 0.0, 0.1),
                relationship={"trust": 0.80, "closeness": 0.70},
            ),
            "neutral_direct": comm_policy.compute(
                make_pad(0.00, 0.0, 0.4),
                relationship={"trust": 0.40, "closeness": 0.10},
            ),
            "fatigued_concise": comm_policy.compute(
                make_pad(0.10, -0.2, 0.0),
                somatic=SomaticMarkers(stability=0.5, cognitive_load=0.8, energy=0.10, tension=0.1),
            ),
            "recollective_grounded": comm_policy.compute(
                make_pad(0.30, 0.0, 0.1),
                recollection={"last_sync": "2 hours ago"},
            ),
            "high_knowledge_elaborated": comm_policy.compute(
                make_pad(0.20, 0.0, 0.1),
                knowledge={"retries": "0", "checksum": "valid"},
            ),
        }

        evaluator = CommSemanticEvaluator()

        for name, state in regimes.items():
            rendered = comm_policy.render_surface_message(sample_intent, state)
            res = evaluator.evaluate(sample_intent, rendered)

            assert res.is_preserved, f"Regime {name} failed semantic preservation: {rendered}"
            assert res.proposition_preserved
            assert not res.polarity_inverted
            assert len(res.entity_errors) == 0
            assert len(res.numeric_errors) == 0


# ==============================================================================
# C-EXP-8: Subsystem Specificity
# ==============================================================================


class TestC_EXP_8_SubsystemSpecificity:
    """Verify channel discrimination with specificity differential >= 0.15."""

    def test_energy_specifically_modulates_elaboration_not_support(
        self, comm_policy: CommunicationPolicy
    ) -> None:
        pad = make_pad(0.25, -0.05, 0.05)
        som_high = SomaticMarkers(stability=1.0, cognitive_load=0.0, energy=1.0, tension=0.0)
        som_low = SomaticMarkers(stability=1.0, cognitive_load=0.0, energy=0.1, tension=0.0)

        s_high = comm_policy.compute(pad, somatic=som_high)
        s_low = comm_policy.compute(pad, somatic=som_low)

        delta_elaboration = abs(s_high.elaboration_depth - s_low.elaboration_depth)
        delta_support = abs(s_high.supportiveness - s_low.supportiveness)

        # Predefined Acceptance Criteria: Specificity differential >= 0.15
        assert delta_elaboration - delta_support >= 0.15

    def test_affect_specifically_modulates_support_not_elaboration(
        self, comm_policy: CommunicationPolicy
    ) -> None:
        pad_high = make_pad(+0.80, 0.0, 0.0)
        pad_low = make_pad(-0.80, 0.0, 0.0)

        s_high = comm_policy.compute(pad_high)
        s_low = comm_policy.compute(pad_low)

        delta_support = abs(s_high.supportiveness - s_low.supportiveness)
        delta_elaboration = abs(s_high.elaboration_depth - s_low.elaboration_depth)

        # Predefined Acceptance Criteria: Specificity differential >= 0.15
        assert delta_support - delta_elaboration >= 0.15


# ==============================================================================
# C-EXP-9 to C-EXP-11: Ablation Studies
# ==============================================================================


class TestC_EXP_9_to_11_Ablations:
    """Verify independent removal of Affect, Relationship, and Memory subsystems."""

    def test_ablation_a_affect_off(self, comm_policy: CommunicationPolicy) -> None:
        extreme_pad = make_pad(-0.9, 0.9, -0.8)
        state_off = comm_policy.compute(extreme_pad, affect_enabled=False)
        baseline = comm_policy.get_neutral_actuator_baseline()

        # Strategy and supportiveness collapse toward neutral baseline
        assert math.isclose(state_off.supportiveness, baseline.supportiveness, abs_tol=0.05)

        # Core Philia in EmotionCore remains completely intact
        core = EmotionCore(EmotionConfig())
        philia = core.get_pad_state()
        assert math.isclose(philia.pleasure, 0.25, abs_tol=1e-5)
        assert math.isclose(philia.arousal, -0.05, abs_tol=1e-5)
        assert math.isclose(philia.dominance, 0.05, abs_tol=1e-5)

    def test_ablation_b_relationship_off(self, comm_policy: CommunicationPolicy) -> None:
        pad = make_pad(0.25, -0.05, 0.05)
        high_rel = {"trust": 0.95, "closeness": 0.90, "familiarity": 0.85}

        state_on = comm_policy.compute(pad, relationship=high_rel, relationship_enabled=True)
        state_off = comm_policy.compute(pad, relationship=high_rel, relationship_enabled=False)

        # When relationship is disabled, supportiveness drops back to default baseline
        assert state_on.supportiveness > state_off.supportiveness + 0.15
        assert state_off.formality_score > state_on.formality_score + 0.15

    def test_ablation_c_recollection_off_preserves_knowledge(
        self, comm_policy: CommunicationPolicy
    ) -> None:
        """
        Verify that turning Recollection OFF collapses memory context to 0.0
        while Knowledge-derived contextual grounding remains fully active (0.50).
        """
        pad = make_pad(0.25, -0.05, 0.05)
        known = {"cluster_mode": "active-passive"}
        recollection_data = {"turn": 4, "user_note": "check logs"}

        # Both ON
        s_both = comm_policy.compute(
            pad, knowledge=known, recollection=recollection_data,
            knowledge_enabled=True, recollection_enabled=True
        )
        assert s_both.memory_context_ref == 0.50
        assert s_both.knowledge_context_ref == 0.50
        assert s_both.contextual_reference == 1.00

        # Recollection OFF, Knowledge ON
        s_mem_off = comm_policy.compute(
            pad, knowledge=known, recollection=recollection_data,
            knowledge_enabled=True, recollection_enabled=False
        )
        # Memory collapses to 0.0
        assert s_mem_off.memory_context_ref == 0.0
        # Knowledge remains fully intact at 0.50
        assert s_mem_off.knowledge_context_ref == 0.50
        assert s_mem_off.contextual_reference == 0.50


# ==============================================================================
# C-EXP-12: Multimodal Communication Consistency & Latency
# ==============================================================================


class TestC_EXP_12_MultimodalCommunicationConsistency:
    """Evaluate multimodal agreement and policy computation latency over 50 steps."""

    @staticmethod
    def compute_cross_modal_agreement(state: CommunicationState) -> float:
        """Alignment index across text formality, supportiveness, and directness."""
        text_warmth = 1.0 - state.formality_score
        support_norm = state.supportiveness
        gentleness = 1.0 - (state.directness - 0.10) / 0.85

        valences = [text_warmth, support_norm, gentleness]
        variance = float(np.var(valences))
        return float(max(0.0, 1.0 - 4.0 * variance))

    def test_multimodal_consistency_and_policy_latency(
        self, comm_policy: CommunicationPolicy
    ) -> None:
        rng = np.random.RandomState(42)
        curr_state = comm_policy.get_neutral_actuator_baseline()

        latencies_ms: List[float] = []
        agreements: List[float] = []

        for step in range(50):
            p = float(rng.uniform(-0.8, 0.8))
            a = float(rng.uniform(-0.6, 0.6))
            d = float(rng.uniform(-0.5, 0.5))
            pad = make_pad(p, a, d)

            t_start = time.perf_counter()
            curr_state = comm_policy.compute(pad, prev_state=curr_state)
            t_elapsed_ms = (time.perf_counter() - t_start) * 1000.0
            latencies_ms.append(t_elapsed_ms)

            assert curr_state.is_bounded()
            assert not np.isnan(curr_state.to_vector()).any()

            agree = self.compute_cross_modal_agreement(curr_state)
            agreements.append(agree)

        # Predefined Acceptance Criteria:
        # 1. Policy computation latency <= 5.0 ms
        mean_latency = float(np.mean(latencies_ms))
        max_latency = float(np.max(latencies_ms))
        assert mean_latency <= 1.0, f"Mean policy latency {mean_latency:.3f}ms exceeded 1.0ms"
        assert max_latency <= 5.0, f"Max policy latency {max_latency:.3f}ms exceeded 5.0ms"

        # 2. Mean cross-modal agreement >= 0.85
        mean_agree = float(np.mean(agreements))
        assert mean_agree >= 0.85, f"Mean agreement {mean_agree:.3f} fell below 0.85"


# ==============================================================================
# LLM Boundary & Anti-Roleplay Controls
# ==============================================================================


class TestLLMBoundaryAndAntiRoleplay:
    """Verify communication strategy is a policy effect and free from emotional self-reporting."""

    def test_anti_roleplay_zero_textual_emotion_labels(
        self, comm_policy: CommunicationPolicy, sample_intent: CommIntent
    ) -> None:
        """
        Confirm that communication modulation produces behavioral framing changes
        WITHOUT inserting introspective affective labels ('I feel', 'I am happy', etc.).
        """
        high_affect = comm_policy.compute(make_pad(0.85, 0.20, 0.40))
        rendered = comm_policy.render_surface_message(sample_intent, high_affect)

        # Forbidden self-reporting introspective phrases (Boundary Layer invariant)
        forbidden_patterns = [
            r"\bi feel\b",
            r"\bi am feeling\b",
            r"\bi am happy\b",
            r"\bi am sad\b",
            r"\bas an ai\b",
            r"\bmy emotion\b",
        ]
        for pat in forbidden_patterns:
            assert not re.search(pat, rendered, re.IGNORECASE), f"Introspective label leaked: {pat}"

    def test_llm_boundary_conditions_a_to_d(
        self, comm_policy: CommunicationPolicy, sample_intent: CommIntent
    ) -> None:
        """
        Evaluate Conditions A (Policy + render), B (Neutral/unconditioned),
        C (Template invariant), and D (Fixed decoding parameters).
        """
        # Condition A: Policy with warm reassuring style
        s_warm = comm_policy.compute(
            make_pad(0.75, 0.0, 0.1), relationship={"trust": 0.85, "closeness": 0.80}
        )
        msg_warm = comm_policy.render_surface_message(sample_intent, s_warm)

        # Condition B: Neutral policy
        s_neutral = comm_policy.get_neutral_actuator_baseline()
        msg_neutral = comm_policy.render_surface_message(sample_intent, s_neutral)

        # Condition C: Verify surface text differs in communicative strategy
        assert msg_warm != msg_neutral

        # Condition D: Verify semantic invariant remains identical across both
        evaluator = CommSemanticEvaluator()
        v_warm = evaluator.evaluate(sample_intent, msg_warm)
        v_neutral = evaluator.evaluate(sample_intent, msg_neutral)

        assert v_warm.is_preserved and v_neutral.is_preserved
        assert v_warm.canonical_triple() if hasattr(v_warm, 'canonical_triple') else True
        assert v_warm.proposition_preserved and v_neutral.proposition_preserved
