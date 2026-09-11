"""
src/core/communication/communication_policy.py

Communication Policy engine for Lucia Phase 16.
Maps internal PAD, somatic, relationship, knowledge, and bounded memory contextualization
into a 10-dimensional CommunicationState and discrete CommStrategy.

Pre-Reflective Operational Invariant:
  - Does NOT alter or inject vectors into L2 ODE hidden state h.
  - Bounded memory contextualization couples memory retrieval evidence (Phase 11)
    with contextual communication evidence (Phase 15).
  - Pacing latency modulation is strictly capped at 1000 ms.
"""

from __future__ import annotations

import logging
from typing import Any, Dict, Optional

import numpy as np

from src.core.communication.communication_state import (
    CommIntent,
    CommunicationState,
    CommStrategy,
)
from src.core.models import PADState, SomaticMarkers

logger = logging.getLogger(__name__)


class CommunicationPolicy:
    """
    Evaluates CommunicationState from multi-subsystem internal state:
    C_t = CommunicationPolicy(A_t, S_t, R_t, K_t, M_t).
    """

    def __init__(self, smoothing_factor: float = 0.25) -> None:
        self.smoothing_factor = float(smoothing_factor)

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
        recollection: Optional[Dict[str, Any]] = None,  # Bounded memory contextualization
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
        Used for bounded, deterministic testing and controlled generation templates.
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
