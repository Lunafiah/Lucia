"""
Phase 9 Cognitive Policy Objects — Explicit, Configurable Behavioural Contracts.

These dataclasses replace all hardcoded constants that previously governed
surprise modulation, LNN plasticity, and generation-mode selection.

Separating policy from mechanism allows tuning of experimental parameters
without touching core engine logic (ADR-015, ADR-017, ADR-020).

Design ref: PHASE_9_ARCHITECTURE_GATE.md §§ 11, 12
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import List, Optional

import numpy as np

from src.core.communication.communication_state import CommunicationState
from src.core.embodiment.contract import EstimatedTemporalState, TemporalModulation
from src.core.expression.expression_state import ExpressionState
from src.core.knowledge.proposition import Proposition
from src.core.memory.ecphory import RecollectionResult
from src.core.models import BehavioralConstraints, PADState, SomaticMarkers
from src.core.relationship.state import RelationshipState


# ---------------------------------------------------------------------------
# SurpriseModulationPolicy
# ---------------------------------------------------------------------------

@dataclass
class SurpriseModulationPolicy:
    """
    Governs how Active Inference prediction surprise causally modulates
    HomeostaticEngine somatic markers.

    Default thresholds match PHASE_9_ARCHITECTURE_GATE.md § 11.
    """

    # Cognitive-load scaling coefficient: ΔC = alpha_cl * S_t
    alpha_cognitive_load: float = 0.25

    # Tension onset threshold: tension is raised when S_t > theta_tension
    tension_threshold: float = 0.40

    # Tension scaling coefficient: ΔT = alpha_t * (S_t - theta_tension)
    alpha_tension: float = 0.35

    # Surprise magnitude that triggers deliberative generation mode (k=2)
    deliberative_surprise_threshold: float = 0.60

    # Tension magnitude that independently triggers deliberative mode
    deliberative_tension_threshold: float = 0.70

    def __post_init__(self) -> None:
        for attr, lo, hi in [
            ("alpha_cognitive_load", 0.0, 2.0),
            ("tension_threshold", 0.0, 1.0),
            ("alpha_tension", 0.0, 2.0),
            ("deliberative_surprise_threshold", 0.0, 1.8),  # max surprise ≈ sqrt(12)
            ("deliberative_tension_threshold", 0.0, 1.0),
        ]:
            v = getattr(self, attr)
            if not (lo <= v <= hi):
                raise ValueError(
                    f"SurpriseModulationPolicy.{attr}={v} must be in [{lo}, {hi}]"
                )

    def modulate_somatic(
        self, markers: SomaticMarkers, surprise: float
    ) -> SomaticMarkers:
        """
        Apply surprise-based adjustments to somatic markers and return a new
        (frozen) SomaticMarkers instance.

        The base metabolic markers (stability, energy) are passed through
        unchanged; cognitive_load and tension are raised by prediction surprise.
        """
        new_cl = min(1.0, markers.cognitive_load + self.alpha_cognitive_load * surprise)

        delta_tension = max(0.0, surprise - self.tension_threshold)
        new_tension = min(1.0, markers.tension + self.alpha_tension * delta_tension)

        return SomaticMarkers(
            stability=markers.stability,
            cognitive_load=new_cl,
            energy=markers.energy,
            tension=new_tension,
        )

    def is_deliberative(self, surprise: float, tension: float) -> bool:
        """Return True if generation policy should switch to deliberative mode."""
        return (
            surprise >= self.deliberative_surprise_threshold
            or tension >= self.deliberative_tension_threshold
        )


# ---------------------------------------------------------------------------
# PlasticityPolicy
# ---------------------------------------------------------------------------

@dataclass
class PlasticityPolicy:
    """
    Governs two-stage LNN plasticity: online salience tagging and offline
    idle-time ODE consolidation.

    Design ref: PHASE_9_ARCHITECTURE_GATE.md § 12
    """

    # Minimum salience (surprise magnitude) to queue an experience tuple
    salience_tag_threshold: float = 0.35

    # Seconds of idle time before offline consolidation is triggered
    consolidation_idle_timeout_s: float = 45.0

    # Minimum buffer samples to start an offline training pass
    min_consolidation_batch_size: int = 4

    # Buffer depth that triggers immediate training even during low-idle periods
    max_buffer_overflow_threshold: int = 8

    # AdamW learning rate for the ODE backpropagation pass
    learning_rate: float = 1e-3

    # Maximum training epochs per consolidation cycle
    max_training_epochs: int = 3

    # Gradient clipping norm
    max_gradient_norm: float = 1.0

    def __post_init__(self) -> None:
        if not (0.0 <= self.salience_tag_threshold <= 1.8):
            raise ValueError("salience_tag_threshold must be in [0.0, 1.8]")
        if self.consolidation_idle_timeout_s <= 0.0:
            raise ValueError("consolidation_idle_timeout_s must be > 0")
        if self.min_consolidation_batch_size < 1:
            raise ValueError("min_consolidation_batch_size must be >= 1")
        if self.max_buffer_overflow_threshold < self.min_consolidation_batch_size:
            raise ValueError(
                "max_buffer_overflow_threshold must be >= min_consolidation_batch_size"
            )
        if not (0.0 < self.learning_rate <= 1.0):
            raise ValueError("learning_rate must be in (0, 1]")
        if self.max_training_epochs < 1:
            raise ValueError("max_training_epochs must be >= 1")
        if not (0.0 < self.max_gradient_norm <= 10.0):
            raise ValueError("max_gradient_norm must be in (0, 10]")

    def should_tag(self, surprise: float) -> bool:
        """Return True if experience tuple should be queued for consolidation."""
        return surprise >= self.salience_tag_threshold


# ---------------------------------------------------------------------------
# GenerationPolicy
# ---------------------------------------------------------------------------

@dataclass(frozen=True)
class GenerationPolicy:
    """
    Immutable description of how the language model should generate a response
    for a given cognitive turn.

    Modes (grounded in actual PromptAssembler and LLMBackend capabilities):
      - "fatigued":     k=0, no reasoning scaffolding, tight token budget
      - "reflexive":    k=1, one-step think scaffold, standard temperature
      - "deliberative": k=2, three-step think scaffold, lower temperature,
                        expanded token budget

    Design ref: PHASE_9_ARCHITECTURE_GATE.md § 11
    """

    mode: str              # "fatigued" | "reflexive" | "deliberative"
    reasoning_depth: int   # 0 (fatigued), 1 (reflexive), 2 (deliberative)
    temperature_delta: float        # Additive adjustment to baseline temperature
    token_expansion_factor: float   # Multiplicative to base max_tokens

    # How many <think> scaffolding steps PromptAssembler will inject
    # (matches formula: min(2k - 1, 5) for k >= 1; 0 for k = 0)
    scaffolding_steps: int

    # ----- Named constructors -----

    @classmethod
    def fatigued(cls) -> "GenerationPolicy":
        """Metabolic conservation: short, direct responses."""
        return cls(
            mode="fatigued",
            reasoning_depth=0,
            temperature_delta=+0.10,   # Slightly higher T for brevity diversity
            token_expansion_factor=0.55,  # ≤ 80 tokens at base 150
            scaffolding_steps=0,
        )

    @classmethod
    def reflexive(cls) -> "GenerationPolicy":
        """Standard conversational flow."""
        return cls(
            mode="reflexive",
            reasoning_depth=1,
            temperature_delta=0.0,
            token_expansion_factor=1.0,
            scaffolding_steps=1,
        )

    @classmethod
    def deliberative(cls) -> "GenerationPolicy":
        """High-surprise / high-tension: lower entropy, richer scaffolding."""
        return cls(
            mode="deliberative",
            reasoning_depth=2,
            temperature_delta=-0.10,
            token_expansion_factor=1.15,
            scaffolding_steps=3,
        )

    @classmethod
    def select(
        cls,
        markers: SomaticMarkers,
        surprise: float,
        surprise_policy: SurpriseModulationPolicy,
    ) -> "GenerationPolicy":
        """
        Select the appropriate GenerationPolicy given somatic markers and surprise.

        Decision priority:
          1. Fatigued: energy <= 0.20 (metabolic conservation)
          2. Deliberative: high surprise or high tension
          3. Reflexive: standard conversational baseline
        """
        if markers.energy <= 0.20:
            return cls.fatigued()
        if surprise_policy.is_deliberative(surprise, markers.tension):
            return cls.deliberative()
        return cls.reflexive()

    def apply_to_constraints(
        self, base: BehavioralConstraints
    ) -> BehavioralConstraints:
        """
        Derive final BehavioralConstraints by applying this policy's adjustments
        to the homeostatic baseline constraints.
        """
        new_temp = max(0.01, min(2.0, base.temperature + self.temperature_delta))
        new_tokens = max(1, int(base.max_tokens * self.token_expansion_factor))
        return BehavioralConstraints(
            max_tokens=new_tokens,
            temperature=new_temp,
            latency_ms=base.latency_ms,
            reasoning_depth=self.reasoning_depth,
        )


# ---------------------------------------------------------------------------
# CognitiveTurnResult
# ---------------------------------------------------------------------------

@dataclass(frozen=True)
class CognitiveTurnResult:
    """
    Immutable, frozen record of a single completed cognitive turn.

    This is the sole output of CognitiveOrchestrator.process().  All
    intermediate pipeline values are bundled here so that:
      - GET /state can read telemetry without holding _turn_lock.
      - CognitiveOrchestrator never accumulates mutable God-Object state.
      - Downstream callers (server.py, tests) have a stable, inspectable result.

    Design ref: PHASE_9_ARCHITECTURE_GATE.md § 8.3 (ADR-020)
    """

    call_id: str
    response_text: str

    # Emotional state BEFORE the stimulus was integrated
    pad_initial: PADState

    # Emotional state AFTER the stimulus was integrated (limbic ODE output)
    pad_final: PADState

    # 16D lexical stimulus vector encoded from user input
    stimulus: np.ndarray

    # L2 prediction error from ActiveInferenceEngine (S_t)
    prediction_error: float

    # Somatic markers AFTER surprise modulation
    somatic: SomaticMarkers

    # Behavioral constraints as actually sent to LLMBackend
    constraints: BehavioralConstraints

    # Generation policy used for this turn
    generation_policy: GenerationPolicy

    # Subconscious echo vector from SDM ecphory (None if no traces in memory)
    echo_vector: Optional[np.ndarray]

    # Whether a memory trace was successfully stored in SDM
    trace_stored: bool

    # Whether an experience tuple was queued for LNN plasticity consolidation
    experience_queued: bool

    # Wall-clock execution time for the complete 16-stage pipeline (seconds)
    execution_time_s: float

    # Phase 16: Interpersonal Relationship state snapshot (post-turn)
    relationship: Optional[RelationshipState] = None

    # Phase 16: Communication state and strategy
    communication: Optional[CommunicationState] = None

    # Phase 16: Multimodal 15D expression state
    expression: Optional[ExpressionState] = None

    # Phase 16: Grounded knowledge propositions retrieved for this turn
    known_facts: Optional[List[Proposition]] = None

    # Phase 20: Affective recollection result emitted by EcphoryEngine at Stage 6
    recollection: Optional[RecollectionResult] = None

    # Phase 25: Unilateral temporal embodiment and social modulation
    temporal_state: Optional[EstimatedTemporalState] = None
    temporal_modulation: Optional[TemporalModulation] = None

    # Phase 23: Communicative Act & Proposition Selection (CAPS) result
    caps_result: Optional[Any] = None

    # Phase 23: Discourse referents snapshot
    discourse_referents: Optional[List[Any]] = None

    # ADR-035: Realization contract & Stage S14 verification gate decision
    realization_contract: Optional[Any] = None
    gate_decision: Optional[Any] = None

    class Config:
        # numpy arrays are not hashable — frozen dataclass still works at runtime
        arbitrary_types_allowed = True
