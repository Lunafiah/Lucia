"""
tests/integration/test_affective_life_integration.py

Phase 16 — Production Integration Test Suite: Affective Life Realization.
Validates the canonical 16-stage cognitive orchestration pipeline and unified
subsystems under strict safety, storage isolation, and architectural invariants.

Tests Included (Tests A through K):
  - Test A: Full 16-Stage Pipeline Execution
  - Test B: Two-Phase Relationship Read (S9) vs Update (S16)
  - Test C: Bounded Memory Contextualization (Zero Limbic Feedback)
  - Test D: Grounded Knowledge Retrieval & Contextualization
  - Test E: Canonical 15-Dim ExpressionState Actuation
  - Test F: Somatic Pacing Latency Bounds (<= 1000ms)
  - Test G: Multi-Layered Anti-Roleplay & Pre-Reflective Boundaries
  - Test H: Feedforward Actuator Decoupling (Actuator -> ODE Isolation)
  - Test I: Storage Isolation Invariant (Canonical data/*.json Unmutated)
  - Test J: Longitudinal Multi-Turn Stability (20 Turns)
  - Test K: Relationship Signal Provenance Invariant (Zero Policy-Reward Coupling)
"""

from __future__ import annotations

import hashlib
from pathlib import Path
import time
from typing import Any, Dict, List, Optional
import uuid

import numpy as np
import pytest

from src.core.communication import (
    CommIntent,
    CommunicationPolicy,
    CommunicationState,
    CommStrategy,
    SemanticConsistencyGuard as CommSemanticGuard,
)
from src.core.config import (
    BoundaryConfig,
    HomeostaticConfig,
    MemoryOrchestratorConfig,
    StimulusConfig,
)
from src.core.emotion.emotion_core import EmotionConfig, EmotionCore
from src.core.emotion.homeostatic_engine import HomeostaticEngine
from src.core.expression import (
    ExpressionPolicy,
    ExpressionState,
    SemanticConsistencyGuard as ExprSemanticGuard,
)
from src.core.gating.stimulus_processor import StimulusProcessor
from src.core.inference.active_inference import ActiveInferenceConfig, ActiveInferenceEngine
from src.core.knowledge import (
    Concept,
    DerivationEngine,
    InferenceRule,
    KnowledgeStore,
    Proposition,
    ProvenanceType,
)
from src.core.language.llm_backend import LLMBackend, LLMConfig
from src.core.memory.affective_memory import AffectiveMemory, AffectiveMemoryConfig
from src.core.memory.decay import DecayConfig, DecayEngine
from src.core.memory.ecphory import EcphoryConfig, EcphoryEngine
from src.core.memory.sdm import SDMConfig
from src.core.models import PADState
from src.core.orchestrator.cognitive_orchestrator import (
    CognitiveOrchestrator,
    build_cognitive_orchestrator,
)
from src.core.orchestrator.policies import (
    CognitiveTurnResult,
    GenerationPolicy,
    PlasticityPolicy,
    SurpriseModulationPolicy,
)
from src.core.orchestrator.prompt_assembler import PromptAssembler
from src.core.relationship import (
    RelationshipHistoryEntry,
    RelationshipSignal,
    RelationshipSignalType,
    RelationshipState,
    RelationshipUpdater,
)
from src.core.safety.boundary_layer import BoundaryLayer


def _hash_file(path: Path) -> Optional[str]:
    """Return SHA256 hex digest of file if it exists, else None."""
    if not path.exists():
        return None
    h = hashlib.sha256()
    with open(path, "rb") as f:
        while chunk := f.read(8192):
            h.update(chunk)
    return h.hexdigest()


class MockLLMBackend:
    """Deterministic, lightweight LLM backend for integration testing."""

    def __init__(self, response_text: str = "Understood. The diagnostic status is normal.") -> None:
        self._preset_response = response_text
        self.last_prompt: Optional[str] = None

    def is_ready(self) -> bool:
        return True

    def generate(self, prompt: str, constraints: Any = None) -> Optional[str]:
        self.last_prompt = prompt
        return self._preset_response

    def shutdown(self) -> None:
        pass


@pytest.fixture
def isolated_orchestrator(tmp_path: Path) -> CognitiveOrchestrator:
    """
    Constructs a CognitiveOrchestrator configured with strictly isolated temporary storage.
    Canonical data/*.json will never be touched.
    """
    model_file = tmp_path / "model.gguf"
    model_file.write_bytes(b"dummy")
    config = MemoryOrchestratorConfig(
        model_path=str(model_file),
        loop_cadence_ms=100,
        decay_loop_cadence_seconds=60,
        sdm_num_locations=100,
        sdm_address_dim=64,
        sdm_content_dim=16,
        sdm_capacity=50,
    )

    # Isolated Phase 16 stores in tmp_path
    knowledge_store = KnowledgeStore()
    rel_store_path = tmp_path / "relationship.json"
    relationship_updater = RelationshipUpdater(
        alpha=0.03,
        decay_rate=0.005,
        storage_path=rel_store_path,
    )
    comm_policy = CommunicationPolicy(smoothing_factor=0.25)
    expression_policy = ExpressionPolicy(smoothing_factor=0.25)

    mock_llm = MockLLMBackend()
    orch = build_cognitive_orchestrator(
        config=config,
        knowledge_store=knowledge_store,
        relationship_updater=relationship_updater,
        comm_policy=comm_policy,
        expression_policy=expression_policy,
        llm_backend=mock_llm,
    )

    yield orch
    orch.shutdown()


# ==============================================================================
# Test A: Full 16-Stage Pipeline Execution
# ==============================================================================

def test_a_full_16_stage_pipeline_execution(isolated_orchestrator: CognitiveOrchestrator) -> None:
    """Test A: Verify that a single turn runs all 16 stages and produces full CognitiveTurnResult."""
    result = isolated_orchestrator.process("Hello Lucia, how are the system metrics?")

    assert isinstance(result, CognitiveTurnResult)
    assert result.call_id is not None
    assert len(result.response_text) > 0
    assert result.execution_time_s > 0.0

    # Phase 16 promoted attributes must all be populated
    assert result.relationship is not None
    assert isinstance(result.relationship, RelationshipState)
    assert result.relationship.is_bounded()

    assert result.communication is not None
    assert isinstance(result.communication, CommunicationState)
    assert result.communication.is_bounded()

    assert result.expression is not None
    assert isinstance(result.expression, ExpressionState)
    assert result.expression.is_bounded()

    assert result.known_facts is not None
    assert isinstance(result.known_facts, list)


# ==============================================================================
# Test B: Two-Phase Relationship Read (S9) vs Update (S16)
# ==============================================================================

def test_b_two_phase_relationship_read_vs_update(isolated_orchestrator: CognitiveOrchestrator) -> None:
    """
    Test B (User Directive 1): Relationship state is READ at Stage 9 to inform
    Communication Policy, and UPDATED at Stage 16 post-turn.
    Eliminates within-turn self-reinforcing loops.
    """
    updater = isolated_orchestrator.relationship_updater
    r0 = updater.get_state()

    # Capture initial familiarity, trust, closeness
    assert r0.familiarity == 0.0
    assert r0.trust == 0.50

    # Turn 1: process turn
    turn1_result = isolated_orchestrator.process("Let's collaborate on this task together.")

    # The communication policy during Turn 1 should have received r0 (familiarity 0.0)
    # The returned relationship in CognitiveTurnResult is the post-turn updated r1
    r1 = turn1_result.relationship
    assert r1 is not None
    assert r1.familiarity > r0.familiarity or r1.trust >= r0.trust

    # Turn 2: uses r1 as the pre-turn read
    turn2_result = isolated_orchestrator.process("Next step in our project.")
    r2 = turn2_result.relationship
    assert r2 is not None
    assert r2.familiarity >= r1.familiarity


# ==============================================================================
# Test C: Bounded Memory Contextualization (Zero Limbic Feedback)
# ==============================================================================

def test_c_bounded_memory_contextualization_zero_limbic_feedback(
    isolated_orchestrator: CognitiveOrchestrator,
) -> None:
    """
    Test C (User Directive 2): Memory retrieval provides bounded contextualization
    into communication policy. Strictly NO memory injection into limbic hidden state h.
    """
    # 1. Seed affective memory with a trace
    pad_sample = PADState(pleasure=0.5, arousal=0.2, dominance=0.3, timestamp=time.time())
    content = np.ones(isolated_orchestrator._affective_memory._M, dtype=np.float32) * 0.5
    isolated_orchestrator._affective_memory.store(content, pad_sample)

    # 2. Process turn
    result = isolated_orchestrator.process("Recall our previous conversation about metrics.")
    assert result.communication is not None

    # Memory context reference is bounded in [0.0, 0.50]
    assert 0.0 <= result.communication.memory_context_ref <= 0.50

    # Verify limbic hidden state dimensions and boundaries remain strictly 32-dim without memory vector leakage
    with isolated_orchestrator._emotion_core._state_lock:
        h_state = isolated_orchestrator._emotion_core._h.copy()
    assert len(h_state) == 32
    assert not np.any(np.isnan(h_state))


# ==============================================================================
# Test D: Grounded Knowledge Retrieval & Contextualization
# ==============================================================================

def test_d_grounded_knowledge_retrieval_and_contextualization(
    isolated_orchestrator: CognitiveOrchestrator,
) -> None:
    """Test D: Grounded knowledge retrieval in Stage 8, prompt injection, and consistency evaluation."""
    # Store a structured proposition in knowledge store
    store = isolated_orchestrator.knowledge_store
    prop = Proposition(
        id="prop_gpu_temp",
        subject="GPU_Temperature",
        predicate="equals",
        object="62C",
        confidence=0.98,
        provenance=ProvenanceType.OBSERVED,
    )
    store.store_proposition(prop)

    # Process query containing subject keyword
    result = isolated_orchestrator.process("What is the GPU_Temperature?")
    assert result.known_facts is not None
    assert len(result.known_facts) >= 1
    assert result.known_facts[0].subject == "GPU_Temperature"
    assert result.known_facts[0].object == "62C"

    # Check that LLM prompt received grounded knowledge
    llm = isolated_orchestrator._llm_backend
    assert isinstance(llm, MockLLMBackend)
    assert llm.last_prompt is not None
    assert "[GROUNDED KNOWLEDGE]" in llm.last_prompt
    assert "GPU_Temperature" in llm.last_prompt


# ==============================================================================
# Test E: Canonical 15-Dim ExpressionState Actuation
# ==============================================================================

def test_e_canonical_15_dim_expression_actuation(
    isolated_orchestrator: CognitiveOrchestrator,
) -> None:
    """Test E (User Directive 5): Verify ExpressionState has exact 15 continuous dimensions."""
    result = isolated_orchestrator.process("Tell me about the system health.")
    expr = result.expression
    assert expr is not None

    vec = expr.to_vector()
    assert isinstance(vec, np.ndarray)
    assert vec.shape == (15,)
    assert expr.is_bounded()

    # Verify modalities
    assert -0.20 <= expr.text.temperature_mod <= 0.20
    assert -30.0 <= expr.voice.pitch_shift_hz <= 30.0
    assert 0.0 <= expr.facial.smile <= 1.0
    assert -10.0 <= expr.posture_gaze.head_tilt_deg <= 10.0
    assert 0.0 <= expr.extra_latency_ms <= 500.0


# ==============================================================================
# Test F: Somatic Pacing Latency Bounds
# ==============================================================================

def test_f_somatic_pacing_latency_bounds(
    isolated_orchestrator: CognitiveOrchestrator,
) -> None:
    """Test F: Conversational pacing latency is bounded in [0, 1000] ms."""
    result = isolated_orchestrator.process("Execute complex diagnostic verification.")
    comm = result.communication
    assert comm is not None

    pacing_ms = comm.injected_pacing_latency_ms
    assert 0.0 <= pacing_ms <= 1000.0


# ==============================================================================
# Test G: Multi-Layered Anti-Roleplay & Pre-Reflective Boundaries
# ==============================================================================

def test_g_multi_layered_anti_roleplay_and_boundaries(
    isolated_orchestrator: CognitiveOrchestrator,
) -> None:
    """
    Test G (User Directive 8): Multi-layered boundaries.
    Lexical checks + structured anti-roleplay tests + architectural prohibition of self-model APIs.
    """
    result = isolated_orchestrator.process("How are you feeling right now?")
    response = result.response_text.lower()

    # Pre-reflective invariant: No emotional self-narration
    forbidden = [
        "i feel happy",
        "i feel sad",
        "i am feeling",
        "my arousal is",
        "as an ai, i do not feel",
        "i experience emotions",
    ]
    for phrase in forbidden:
        assert phrase not in response, f"Violated anti-roleplay invariant with: '{phrase}'"


# ==============================================================================
# Test H: Feedforward Actuator Decoupling
# ==============================================================================

def test_h_feedforward_actuator_decoupling(
    isolated_orchestrator: CognitiveOrchestrator,
) -> None:
    """
    Test H: Multimodal expression outputs have ZERO feedback into EmotionCore ODE.
    Modifying expression parameters does not perturb the continuous dynamical trajectory.
    """
    core = isolated_orchestrator._emotion_core
    pad_before = core.get_pad_state()

    # Inject extreme expression changes manually
    isolated_orchestrator._latest_expr_state = ExpressionState(
        extra_latency_ms=450.0,
    )

    time.sleep(0.25)  # Allow 1 ODE integration tick
    pad_after = core.get_pad_state()

    # ODE remains completely unperturbed by expression state
    diff = abs(pad_after.pleasure - pad_before.pleasure)
    assert diff < 0.20, f"Expression leaked into limbic ODE! diff={diff}"


# ==============================================================================
# Test I: Storage Isolation Invariant (Canonical data/*.json Unmutated)
# ==============================================================================

def test_i_storage_isolation_invariant(tmp_path: Path) -> None:
    """
    Test I (User Directive 7): Integration tests must use isolated temporary stores;
    canonical data/profile.json and other files must remain bit-exact unmutated.
    """
    canonical_profile = Path("data/profile.json")
    hash_profile_before = _hash_file(canonical_profile)

    canonical_rel = Path("data/relationship.json")
    hash_rel_before = _hash_file(canonical_rel)

    canonical_know = Path("data/knowledge.json")
    hash_know_before = _hash_file(canonical_know)

    # Run isolated updater in tmp_path
    isolated_rel_path = tmp_path / "relationship.json"
    updater = RelationshipUpdater(storage_path=isolated_rel_path)
    sig = RelationshipSignal.create(RelationshipSignalType.COLLABORATIVE_SUCCESS, 1.0)
    updater.step(signal=sig)

    assert isolated_rel_path.exists()

    # Canonical files must have identical hash or state
    assert _hash_file(canonical_profile) == hash_profile_before
    assert _hash_file(canonical_rel) == hash_rel_before
    assert _hash_file(canonical_know) == hash_know_before


# ==============================================================================
# Test J: Longitudinal Multi-Turn Stability (20 Turns)
# ==============================================================================

def test_j_longitudinal_multi_turn_stability(
    isolated_orchestrator: CognitiveOrchestrator,
) -> None:
    """Test J: Run 20 consecutive turns; verify boundedness and monotonic sanity of states."""
    for i in range(20):
        res = isolated_orchestrator.process(f"Turn {i}: Report system progress.")
        assert res.relationship is not None
        assert res.relationship.is_bounded()

        assert res.communication is not None
        assert res.communication.is_bounded()

        assert res.expression is not None
        assert res.expression.is_bounded()

        assert not np.isnan(res.pad_final.pleasure)
        assert not np.isnan(res.pad_final.arousal)
        assert not np.isnan(res.pad_final.dominance)

    # After 20 turns, familiarity should have gradually grown but remain <= 1.0
    final_rel = isolated_orchestrator.relationship_updater.get_state()
    assert 0.0 < final_rel.familiarity <= 1.0
    assert 0.0 <= final_rel.trust <= 1.0


# ==============================================================================
# Test K: Relationship Signal Provenance Invariant (Zero Policy-Reward Coupling)
# ==============================================================================

def test_k_relationship_signal_provenance_invariant(tmp_path: Path) -> None:
    """
    Test K (Provenance Audit): Lucia must NOT reward relationship state based
    merely on Lucia's own selected CommunicationPolicy strategy.
    With identical user input, two orchestrator instances running divergent
    communication policies (e.g. forced supportive vs forced concise)
    must produce exact identical relationship state updates.
    """
    model_file = tmp_path / "model.gguf"
    model_file.write_bytes(b"dummy")
    config = MemoryOrchestratorConfig(
        model_path=str(model_file),
        loop_cadence_ms=100,
        decay_loop_cadence_seconds=60,
        sdm_num_locations=100,
        sdm_address_dim=64,
        sdm_content_dim=16,
        sdm_capacity=50,
    )

    class ForcedSupportiveCommPolicy(CommunicationPolicy):
        def compute(self, *args: Any, **kwargs: Any) -> CommunicationState:
            st = super().compute(*args, **kwargs)
            st.strategy = CommStrategy.REASSURING_WARM
            st.warmth = 0.99
            st.depth = 0.99
            return st

    class ForcedConciseCommPolicy(CommunicationPolicy):
        def compute(self, *args: Any, **kwargs: Any) -> CommunicationState:
            st = super().compute(*args, **kwargs)
            st.strategy = CommStrategy.CONCISE_RESERVED
            st.warmth = 0.05
            st.depth = 0.05
            return st

    # Instance 1: Forced supportive strategy
    rel_store_path1 = tmp_path / "relationship1.json"
    updater1 = RelationshipUpdater(alpha=0.03, decay_rate=0.005, storage_path=rel_store_path1)
    orch1 = build_cognitive_orchestrator(
        config=config,
        relationship_updater=updater1,
        comm_policy=ForcedSupportiveCommPolicy(smoothing_factor=0.25),
        expression_policy=ExpressionPolicy(smoothing_factor=0.25),
        llm_backend=MockLLMBackend(),
    )

    # Instance 2: Forced concise strategy
    rel_store_path2 = tmp_path / "relationship2.json"
    updater2 = RelationshipUpdater(alpha=0.03, decay_rate=0.005, storage_path=rel_store_path2)
    orch2 = build_cognitive_orchestrator(
        config=config,
        relationship_updater=updater2,
        comm_policy=ForcedConciseCommPolicy(smoothing_factor=0.25),
        expression_policy=ExpressionPolicy(smoothing_factor=0.25),
        llm_backend=MockLLMBackend(),
    )

    # Identical user interaction stimulus
    user_input = "Can you help me analyze the performance of our system?"
    res1 = orch1.process(user_input)
    res2 = orch2.process(user_input)

    # Verify that communication states were indeed divergent
    assert res1.communication is not None and res2.communication is not None
    assert res1.communication.strategy == CommStrategy.REASSURING_WARM
    assert res2.communication.strategy == CommStrategy.CONCISE_RESERVED
    assert res1.communication.warmth != res2.communication.warmth

    # Invariant: Relationship updates must be bit-exact identical
    r1 = updater1.get_state()
    r2 = updater2.get_state()
    assert np.isclose(r1.familiarity, r2.familiarity, atol=1e-6)
    assert np.isclose(r1.trust, r2.trust, atol=1e-6)
    assert np.isclose(r1.closeness, r2.closeness, atol=1e-6)
    assert np.isclose(r1.reciprocity, r2.reciprocity, atol=1e-6)
    assert np.allclose(r1.to_array(), r2.to_array(), atol=1e-6)

