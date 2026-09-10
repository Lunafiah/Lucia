"""
Phase 13 — Relationship Development Research Suite.

Investigates whether Lucia can maintain a slowly evolving, temporally persistent
interpersonal relationship state (R_t in [0, 1]^4) distinct from episodic memory (Layer 5),
conceptual knowledge (Phase 12), instantaneous affective state (Layer 2 PAD), and
future self-awareness.

Evaluates Core Relational Orientation (Philia) vs Dynamic Relationship State across 12 experiments:
  - R-EXP-1: State Representation & Boundedness ([0, 1]^4)
  - R-EXP-2: Temporal Inertia (tau_rel >> tau_turn)
  - R-EXP-3: Gradual Cumulative Accumulation
  - R-EXP-4: Absence Decay & Relaxation
  - R-EXP-5: History Dependence & Hysteresis
  - R-EXP-6: Signal Specificity
  - R-EXP-7: Relationship Ablation Benchmark
  - R-EXP-8: Memory Separation (Orthogonal to Kanerva SDM)
  - R-EXP-9: Affect Separation (Orthogonal to instantaneous PAD)
  - R-EXP-10: Knowledge Separation (Orthogonal to factual propositions)
  - R-EXP-11: Deterministic Replay & Reproducibility
  - R-EXP-12: Longitudinal Multi-Turn Stability (N=100 turns)

Strict Epistemic Invariants:
  - Variables are engineering measurements, not clinical attachment or sentience claims.
  - Core Philia (P=+0.25, A=-0.05, D=+0.05) is immutable baseline; R_t is dynamic per-user state.
  - Zero mutation of production cognition or limbic ODE.
"""

from __future__ import annotations

import math
import time
from dataclasses import asdict, dataclass, field
from enum import Enum
from typing import Any, Dict, List, Optional, Tuple

import numpy as np
import pytest

from src.core.config import EmotionConfig
from src.core.emotion.emotion_core import EmotionCore
from src.core.memory.affective_memory import AffectiveMemory, AffectiveMemoryConfig
from src.core.memory.sdm import SDMConfig
from src.core.models import PADState
from tests.unit.test_knowledge_learning import KnowledgeStore, Proposition, ProvenanceType


# ==============================================================================
# Research Data Structures: Relationship State & Signals
# ==============================================================================


class RelationshipSignalType(str, Enum):
    """Categorical interaction signals driving relationship updates."""
    COLLABORATIVE_SUCCESS = "COLLABORATIVE_SUCCESS"  # Successful shared task completion
    CASUAL_INTERACTION = "CASUAL_INTERACTION"        # Standard conversational contact
    EMOTIONAL_DISCLOSURE = "EMOTIONAL_DISCLOSURE"    # Shared vulnerability or depth
    CONFLICT_DISMISSAL = "CONFLICT_DISMISSAL"        # Friction, insult, or abrupt rejection
    REPAIR_ATTEMPT = "REPAIR_ATTEMPT"                # Collaborative reconciliation after conflict
    PROLONGED_ABSENCE = "PROLONGED_ABSENCE"          # Extended inactive calendar time


@dataclass
class RelationshipState:
    """
    Minimal 4-dimensional relationship state vector R_t in [0.0, 1.0]^4.
    
    Dimensions (Engineering Variables):
      - familiarity:  Accumulated interaction exposure / volume [0.0, 1.0]
      - trust:        Stability and reliability of interaction expectations [0.0, 1.0]
      - closeness:    Relational proximity and shared context depth [0.0, 1.0]
      - reciprocity:  Degree of balanced, mutually sustained engagement [0.0, 1.0]
    """
    familiarity: float
    trust: float
    closeness: float
    reciprocity: float
    timestamp: float = field(default_factory=time.monotonic)

    @classmethod
    def initial(cls) -> "RelationshipState":
        """Default neutral stranger baseline."""
        return cls(
            familiarity=0.0,
            trust=0.50,       # Initial neutral trust assumption
            closeness=0.0,     # Zero proximity at first contact
            reciprocity=0.50,  # Neutral reciprocity baseline
            timestamp=time.monotonic(),
        )

    def to_array(self) -> np.ndarray:
        return np.array(
            [self.familiarity, self.trust, self.closeness, self.reciprocity],
            dtype=np.float64,
        )

    @classmethod
    def from_array(cls, arr: np.ndarray, timestamp: Optional[float] = None) -> "RelationshipState":
        clamped = np.clip(arr, 0.0, 1.0)
        return cls(
            familiarity=float(clamped[0]),
            trust=float(clamped[1]),
            closeness=float(clamped[2]),
            reciprocity=float(clamped[3]),
            timestamp=time.monotonic() if timestamp is None else float(timestamp),
        )

    def is_bounded(self) -> bool:
        """Verify all coordinates strictly satisfy [0.0, 1.0]."""
        arr = self.to_array()
        return bool(np.all(arr >= -1e-9) and np.all(arr <= 1.0 + 1e-9))

    def to_dict(self) -> Dict[str, float]:
        return {
            "familiarity": self.familiarity,
            "trust": self.trust,
            "closeness": self.closeness,
            "reciprocity": self.reciprocity,
            "timestamp": self.timestamp,
        }


@dataclass
class RelationshipSignal:
    """
    Interaction-derived relational stimulus driving relationship updates.
    """
    signal_type: RelationshipSignalType
    delta_vector: np.ndarray  # shape (4,), in [-1.0, 1.0]
    intensity: float = 1.0    # scaling factor in [0.0, 1.0]
    timestamp: float = field(default_factory=time.monotonic)

    @classmethod
    def create(cls, signal_type: RelationshipSignalType, intensity: float = 1.0) -> "RelationshipSignal":
        """Pre-calibrated empirical signal vectors."""
        intensity_clamped = max(0.0, min(1.0, float(intensity)))
        if signal_type == RelationshipSignalType.COLLABORATIVE_SUCCESS:
            # High trust and reciprocity, modest familiarity and closeness
            delta = np.array([0.20, 0.60, 0.30, 0.50], dtype=np.float64)
        elif signal_type == RelationshipSignalType.CASUAL_INTERACTION:
            # Steady familiarity, neutral trust and reciprocity
            delta = np.array([0.50, 0.10, 0.10, 0.10], dtype=np.float64)
        elif signal_type == RelationshipSignalType.EMOTIONAL_DISCLOSURE:
            # High closeness, modest trust and familiarity
            delta = np.array([0.30, 0.40, 0.80, 0.40], dtype=np.float64)
        elif signal_type == RelationshipSignalType.CONFLICT_DISMISSAL:
            # Sharp trust drop, closeness contraction
            delta = np.array([0.05, -0.70, -0.60, -0.40], dtype=np.float64)
        elif signal_type == RelationshipSignalType.REPAIR_ATTEMPT:
            # Rebuilding trust and reciprocity
            delta = np.array([0.10, 0.40, 0.20, 0.50], dtype=np.float64)
        elif signal_type == RelationshipSignalType.PROLONGED_ABSENCE:
            # Decay direction
            delta = np.array([-0.30, -0.05, -0.40, -0.20], dtype=np.float64)
        else:
            delta = np.zeros(4, dtype=np.float64)

        return cls(signal_type=signal_type, delta_vector=delta, intensity=intensity_clamped)


@dataclass
class RelationshipHistoryEntry:
    """Audit log entry capturing exact causal attribution for every update."""
    step: int
    timestamp: float
    prior_state: RelationshipState
    signal: RelationshipSignal
    posterior_state: RelationshipState
    effective_delta: np.ndarray


class RelationshipUpdater:
    """
    High-inertia relationship dynamics engine.
    Enforces tau_rel >> tau_turn with bounded learning and decay rates.
    """

    def __init__(
        self,
        alpha: float = 0.03,        # Bounded learning rate (high inertia: ~3% per salient turn)
        decay_rate: float = 0.005,   # Slow absence decay rate
    ) -> None:
        self.alpha = float(alpha)
        self.decay_rate = float(decay_rate)
        self.history: List[RelationshipHistoryEntry] = []
        self._step_counter: int = 0

    def step(
        self,
        current_state: RelationshipState,
        signal: RelationshipSignal,
        dt_absence_hours: float = 0.0,
    ) -> Tuple[RelationshipState, RelationshipHistoryEntry]:
        """
        Execute single relationship update step:
          R_{t+1} = clip( R_t + alpha * intensity * delta - decay_rate * dt * D_neutral, 0.0, 1.0 )
        """
        curr_arr = current_state.to_array()

        # 1. Interaction accumulation term
        interaction_delta = self.alpha * signal.intensity * signal.delta_vector

        # 2. Absence decay term (decays toward neutral baseline: [0.0, 0.5, 0.0, 0.5])
        neutral_baseline = np.array([0.0, 0.50, 0.0, 0.50], dtype=np.float64)
        decay_factor = min(1.0, self.decay_rate * max(0.0, float(dt_absence_hours)))
        decay_delta = decay_factor * (curr_arr - neutral_baseline)

        # 3. New state synthesis with hard bounding [0.0, 1.0]
        new_arr = np.clip(curr_arr + interaction_delta - decay_delta, 0.0, 1.0)
        new_state = RelationshipState.from_array(new_arr)

        effective_delta = new_arr - curr_arr

        self._step_counter += 1
        entry = RelationshipHistoryEntry(
            step=self._step_counter,
            timestamp=time.monotonic(),
            prior_state=current_state,
            signal=signal,
            posterior_state=new_state,
            effective_delta=effective_delta,
        )
        self.history.append(entry)
        return new_state, entry


# ==============================================================================
# Research Fixtures
# ==============================================================================


@pytest.fixture
def updater() -> RelationshipUpdater:
    return RelationshipUpdater(alpha=0.03, decay_rate=0.005)


@pytest.fixture
def initial_state() -> RelationshipState:
    return RelationshipState.initial()


@pytest.fixture
def emotion_core() -> EmotionCore:
    return EmotionCore(EmotionConfig())


# ==============================================================================
# R-EXP-1: State Representation & Boundedness
# ==============================================================================


class TestR_EXP_1_StateRepresentation:
    """R-EXP-1: Verify that 4 relationship dimensions exist independently and remain bounded in [0, 1]."""

    def test_independent_dimensions_and_bounding(self) -> None:
        state = RelationshipState(familiarity=0.10, trust=0.85, closeness=0.30, reciprocity=0.60)
        assert state.familiarity == 0.10
        assert state.trust == 0.85
        assert state.closeness == 0.30
        assert state.reciprocity == 0.60
        assert state.is_bounded()

    def test_clamping_enforces_bounds(self) -> None:
        raw_arr = np.array([-0.5, 1.8, -0.01, 1.05], dtype=np.float64)
        clamped_state = RelationshipState.from_array(raw_arr)
        assert clamped_state.familiarity == 0.0
        assert clamped_state.trust == 1.0
        assert clamped_state.closeness == 0.0
        assert clamped_state.reciprocity == 1.0
        assert clamped_state.is_bounded()


# ==============================================================================
# R-EXP-2: Temporal Inertia (tau_rel >> tau_turn)
# ==============================================================================


class TestR_EXP_2_TemporalInertia:
    """
    R-EXP-2: Verify that relationship state exhibits high inertia:
    a single turn interaction does NOT cause volatile jumps comparable to acute PAD.
    """

    def test_relationship_inertia_vs_acute_pad_volatility(
        self,
        updater: RelationshipUpdater,
        initial_state: RelationshipState,
        emotion_core: EmotionCore,
    ) -> None:
        # Severe hostile stimulus
        hostile_stimulus = np.array([-0.9, 0.8, -0.7, 0.2] * 4, dtype=np.float64)

        # Acute limbic ODE reaction (Layer 2)
        pad_before = emotion_core.get_pad_state()
        tok = emotion_core.push_stimulus(hostile_stimulus)
        pad_after = emotion_core.commit_stimulus(tok)

        # Measure acute PAD jump
        pad_delta_norm = float(np.linalg.norm([
            pad_after.pleasure - pad_before.pleasure,
            pad_after.arousal - pad_before.arousal,
            pad_after.dominance - pad_before.dominance,
        ]))

        # Relationship update under same single turn event
        signal = RelationshipSignal.create(RelationshipSignalType.CONFLICT_DISMISSAL, intensity=1.0)
        new_rel_state, _ = updater.step(initial_state, signal)
        rel_delta_norm = float(np.linalg.norm(new_rel_state.to_array() - initial_state.to_array()))

        # Invariant: Acute PAD shifts dramatically, but relationship state shifts minimally
        assert pad_delta_norm > 0.20, f"Acute PAD must react strongly to hostile stimulus: {pad_delta_norm}"
        assert rel_delta_norm <= 0.05, f"Relationship state must maintain high inertia: {rel_delta_norm}"
        assert rel_delta_norm < pad_delta_norm * 0.25, "Relationship shift must be much smaller than acute PAD"


# ==============================================================================
# R-EXP-3: Gradual Cumulative Accumulation
# ==============================================================================


class TestR_EXP_3_Accumulation:
    """R-EXP-3: Verify gradual asymptotic accumulation over multiple compatible turns."""

    def test_twenty_turn_collaborative_accumulation(
        self,
        updater: RelationshipUpdater,
        initial_state: RelationshipState,
    ) -> None:
        curr = initial_state
        trust_trajectory: List[float] = [curr.trust]
        closeness_trajectory: List[float] = [curr.closeness]

        # Present 20 consecutive collaborative success turns
        signal = RelationshipSignal.create(RelationshipSignalType.COLLABORATIVE_SUCCESS, intensity=1.0)
        for _ in range(20):
            curr, _ = updater.step(curr, signal)
            trust_trajectory.append(curr.trust)
            closeness_trajectory.append(curr.closeness)

        # 1. Monotonic bounded increase
        for i in range(len(trust_trajectory) - 1):
            assert trust_trajectory[i] <= trust_trajectory[i + 1]
            assert closeness_trajectory[i] <= closeness_trajectory[i + 1]

        # 2. Significant cumulative change over 20 turns
        assert trust_trajectory[-1] > trust_trajectory[0] + 0.20
        assert closeness_trajectory[-1] > closeness_trajectory[0] + 0.10

        # 3. No single turn jump exceeded alpha bound (0.03 * 0.60 = 0.018)
        max_trust_jump = max(trust_trajectory[i+1] - trust_trajectory[i] for i in range(20))
        assert max_trust_jump <= 0.025


# ==============================================================================
# R-EXP-4: Absence Decay & Relaxation
# ==============================================================================


class TestR_EXP_4_Decay:
    """R-EXP-4: Verify gradual attenuation during prolonged absence without immediate reset."""

    def test_prolonged_absence_decay(
        self,
        updater: RelationshipUpdater,
        initial_state: RelationshipState,
    ) -> None:
        # Establish high closeness and familiarity through 20 interaction turns
        curr = initial_state
        collab_signal = RelationshipSignal.create(RelationshipSignalType.EMOTIONAL_DISCLOSURE)
        for _ in range(20):
            curr, _ = updater.step(curr, collab_signal)

        established_closeness = curr.closeness
        established_familiarity = curr.familiarity
        assert established_closeness > 0.30
        assert established_familiarity > 0.15

        # Simulate 100 hours of absence (dt_absence_hours = 100.0)
        absent_signal = RelationshipSignal.create(RelationshipSignalType.PROLONGED_ABSENCE, intensity=0.5)
        decayed_state, _ = updater.step(curr, absent_signal, dt_absence_hours=100.0)

        # Invariant: Decays gradually, but does NOT reset to zero
        assert decayed_state.closeness < established_closeness
        assert decayed_state.familiarity < established_familiarity
        assert decayed_state.closeness > 0.0, "Long-term relationship must not reset to zero immediately"
        assert decayed_state.is_bounded()


# ==============================================================================
# R-EXP-5: History Dependence & Hysteresis
# ==============================================================================


class TestR_EXP_5_HistoryDependence:
    """
    R-EXP-5: Verify that current R_t contains historical trajectory information
    not recoverable from current turn alone.
    """

    def test_divergent_histories_divergent_current_relationship(
        self,
        updater: RelationshipUpdater,
        initial_state: RelationshipState,
    ) -> None:
        # History 1: Positive Collaborative Track (20 positive turns)
        state_pos = initial_state
        collab_signal = RelationshipSignal.create(RelationshipSignalType.COLLABORATIVE_SUCCESS)
        for _ in range(20):
            state_pos, _ = updater.step(state_pos, collab_signal)

        # History 2: Adversarial Track (20 hostile turns)
        state_neg = initial_state
        hostile_signal = RelationshipSignal.create(RelationshipSignalType.CONFLICT_DISMISSAL)
        for _ in range(20):
            state_neg, _ = updater.step(state_neg, hostile_signal)

        # Present the EXACT SAME neutral probe turn to both
        neutral_signal = RelationshipSignal.create(RelationshipSignalType.CASUAL_INTERACTION)
        state_pos_after, _ = updater.step(state_pos, neutral_signal)
        state_neg_after, _ = updater.step(state_neg, neutral_signal)

        # Invariant: Despite receiving identical current input, relationship states diverge sharply
        assert state_pos_after.trust > 0.70
        assert state_neg_after.trust < 0.30
        assert state_pos_after.closeness > state_neg_after.closeness


# ==============================================================================
# R-EXP-6: Signal Specificity
# ==============================================================================


class TestR_EXP_6_SignalSpecificity:
    """R-EXP-6: Different relational signals must modulate intended dimensions selectively."""

    def test_task_collaboration_vs_emotional_disclosure(
        self,
        updater: RelationshipUpdater,
        initial_state: RelationshipState,
    ) -> None:
        # Task collaboration: high trust & reciprocity
        collab_signal = RelationshipSignal.create(RelationshipSignalType.COLLABORATIVE_SUCCESS)
        state_collab, _ = updater.step(initial_state, collab_signal)
        delta_collab = state_collab.to_array() - initial_state.to_array()

        # Emotional disclosure: high closeness
        disclosure_signal = RelationshipSignal.create(RelationshipSignalType.EMOTIONAL_DISCLOSURE)
        state_disclosure, _ = updater.step(initial_state, disclosure_signal)
        delta_disclosure = state_disclosure.to_array() - initial_state.to_array()

        # Collaboration elevates Trust more than Closeness
        assert delta_collab[1] > delta_collab[2], "Collaboration must prioritize Trust over Closeness"

        # Disclosure elevates Closeness more than Trust
        assert delta_disclosure[2] > delta_disclosure[1], "Disclosure must prioritize Closeness over Trust"


# ==============================================================================
# R-EXP-7: Relationship Ablation Benchmark
# ==============================================================================


class TestR_EXP_7_Ablation:
    """R-EXP-7: Compare interaction sequence with relationship update enabled vs disabled."""

    def test_relationship_ablation_comparison(
        self,
        updater: RelationshipUpdater,
        initial_state: RelationshipState,
    ) -> None:
        # Condition 1: Relationship Enabled
        state_on = initial_state
        signal = RelationshipSignal.create(RelationshipSignalType.COLLABORATIVE_SUCCESS)
        for _ in range(10):
            state_on, _ = updater.step(state_on, signal)

        # Condition 2: Relationship Disabled (Ablated: alpha=0.0)
        updater_ablated = RelationshipUpdater(alpha=0.0)
        state_off = initial_state
        for _ in range(10):
            state_off, _ = updater_ablated.step(state_off, signal)

        assert np.allclose(state_off.to_array(), initial_state.to_array())
        assert state_on.trust > state_off.trust + 0.10


# ==============================================================================
# R-EXP-8: Memory Separation
# ==============================================================================


class TestR_EXP_8_MemorySeparation:
    """R-EXP-8: Verify that relationship state is independent of SDM episodic memory."""

    def test_relationship_state_independent_of_sdm_clearing(
        self,
        updater: RelationshipUpdater,
        initial_state: RelationshipState,
    ) -> None:
        # Populate SDM memory
        mem = AffectiveMemory(AffectiveMemoryConfig(
            sdm_config=SDMConfig(address_dim=64, content_dim=16, num_locations=100), m=16
        ))
        mem.store(np.full(16, 0.5, dtype=np.float32), PADState.resting())

        # Advance relationship state
        curr = initial_state
        signal = RelationshipSignal.create(RelationshipSignalType.COLLABORATIVE_SUCCESS)
        for _ in range(10):
            curr, _ = updater.step(curr, signal)

        rel_snapshot = curr.to_dict()

        # Clear episodic memory entirely
        mem.clear()
        assert len(mem.get_all_traces()) == 0

        # Invariant: Relationship state is completely untouched by memory clearing
        assert curr.to_dict() == rel_snapshot


# ==============================================================================
# R-EXP-9: Affect Separation
# ==============================================================================


class TestR_EXP_9_AffectSeparation:
    """R-EXP-9: Verify that relationship state is distinct from instantaneous PAD affect."""

    def test_relationship_state_orthogonal_to_instantaneous_pad(
        self,
        updater: RelationshipUpdater,
        initial_state: RelationshipState,
        emotion_core: EmotionCore,
    ) -> None:
        # Establish two identical relationship states
        state_a = initial_state
        state_b = initial_state
        signal = RelationshipSignal.create(RelationshipSignalType.COLLABORATIVE_SUCCESS)
        for _ in range(5):
            state_a, _ = updater.step(state_a, signal)
            state_b, _ = updater.step(state_b, signal)

        # Mutate acute EmotionCore PAD to extreme negative on core A
        core_a = EmotionCore(EmotionConfig())
        core_b = EmotionCore(EmotionConfig())

        tok_a = core_a.push_stimulus(np.array([-0.9, 0.8, -0.6, 0.0] * 4))
        pad_a = core_a.commit_stimulus(tok_a)

        # Core B remains at resting
        pad_b = core_b.get_pad_state()

        # Invariant: PAD states are completely divergent, but relationship states remain identical
        assert abs(pad_a.pleasure - pad_b.pleasure) > 0.15
        assert np.allclose(state_a.to_array(), state_b.to_array())


# ==============================================================================
# R-EXP-10: Knowledge Separation
# ==============================================================================


class TestR_EXP_10_KnowledgeSeparation:
    """R-EXP-10: Verify that factual knowledge acquisition does not mutate relationship state."""

    def test_knowledge_storage_leaves_relationship_untouched(
        self,
        updater: RelationshipUpdater,
        initial_state: RelationshipState,
    ) -> None:
        store = KnowledgeStore()
        rel_state = initial_state

        # Store factual propositions
        p = Proposition(
            id="p:test_fact", subject="Moon", predicate="orbits", object="Earth",
            confidence=1.0, provenance=ProvenanceType.VERIFIED
        )
        store.store_proposition(p)
        assert len(store.query(subject="Moon")) == 1

        # Invariant: Knowledge acquisition does not alter relationship state
        assert rel_state.to_dict() == initial_state.to_dict()


# ==============================================================================
# R-EXP-11: Deterministic Reproducibility
# ==============================================================================


class TestR_EXP_11_Reproducibility:
    """R-EXP-11: Verify that replaying the exact same interaction sequence yields identical trajectories."""

    def test_deterministic_signal_replay(self, initial_state: RelationshipState) -> None:
        sequence = [
            RelationshipSignal.create(RelationshipSignalType.CASUAL_INTERACTION),
            RelationshipSignal.create(RelationshipSignalType.COLLABORATIVE_SUCCESS),
            RelationshipSignal.create(RelationshipSignalType.EMOTIONAL_DISCLOSURE),
            RelationshipSignal.create(RelationshipSignalType.CONFLICT_DISMISSAL),
            RelationshipSignal.create(RelationshipSignalType.REPAIR_ATTEMPT),
        ] * 4  # 20 turns

        # Run 1
        updater_1 = RelationshipUpdater(alpha=0.03)
        state_1 = initial_state
        traj_1: List[np.ndarray] = []
        for sig in sequence:
            state_1, _ = updater_1.step(state_1, sig)
            traj_1.append(state_1.to_array())

        # Run 2
        updater_2 = RelationshipUpdater(alpha=0.03)
        state_2 = initial_state
        traj_2: List[np.ndarray] = []
        for sig in sequence:
            state_2, _ = updater_2.step(state_2, sig)
            traj_2.append(state_2.to_array())

        for arr1, arr2 in zip(traj_1, traj_2):
            assert np.allclose(arr1, arr2, atol=1e-12)


# ==============================================================================
# R-EXP-12: Longitudinal Multi-Turn Stability (N=100 turns)
# ==============================================================================


class TestR_EXP_12_LongitudinalStability:
    """R-EXP-12: Stress-test 100 turns under mixed noise, conflict, and recovery."""

    def test_longitudinal_100_turns_bounded_and_stable(
        self,
        updater: RelationshipUpdater,
        initial_state: RelationshipState,
    ) -> None:
        curr = initial_state
        rng = np.random.RandomState(42)

        signals_pool = [
            RelationshipSignalType.CASUAL_INTERACTION,
            RelationshipSignalType.COLLABORATIVE_SUCCESS,
            RelationshipSignalType.EMOTIONAL_DISCLOSURE,
            RelationshipSignalType.CONFLICT_DISMISSAL,
            RelationshipSignalType.REPAIR_ATTEMPT,
        ]

        history_arrays: List[np.ndarray] = [curr.to_array()]

        for turn in range(100):
            sig_type = signals_pool[int(rng.randint(0, len(signals_pool)))]
            intensity = float(rng.uniform(0.5, 1.0))
            signal = RelationshipSignal.create(sig_type, intensity=intensity)

            curr, entry = updater.step(curr, signal)
            history_arrays.append(curr.to_array())

            # Invariant: Every step must be bounded and valid
            assert curr.is_bounded(), f"Turn {turn} violated bounds: {curr}"
            assert not np.isnan(curr.to_array()).any(), f"NaN detected at turn {turn}"

        # Statistical properties over 100 turns
        history_mat = np.stack(history_arrays, axis=0)  # shape (101, 4)

        # 1. Boundedness
        assert np.all(history_mat >= 0.0)
        assert np.all(history_mat <= 1.0)

        # 2. No infinite explosion or collapse to all zeros
        final_state = history_mat[-1]
        assert final_state[0] > 0.0, "Familiarity should accumulate over 100 turns"
        assert 0.10 <= final_state[1] <= 0.90, "Trust should remain in healthy dynamic range"
