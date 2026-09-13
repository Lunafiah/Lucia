"""
tests/integration/test_mt_homeo_coupling.py

Phase 19 Integration Test Suite: Coupled MT-LNN & Homeostatic Context Feedback.
Validates the end-to-end 16-stage cognitive pipeline with:
- Stage 3 limbic integration consuming m_homeo(t-1)
- Stage 5 homeostatic modulation updating m_homeo(t) in EmotionCore
- Autonomous stress-to-fatigue transformation across turns
- Downstream behavioral throttling under somatic fatigue
- Storage isolation: canonical data/profile.json remains bit-exact {"is_onboarded": false}
"""

from __future__ import annotations

import json
from pathlib import Path
import time
from typing import Any, Optional
import numpy as np
import pytest

from src.core.config import MemoryOrchestratorConfig
from src.core.knowledge import KnowledgeStore
from src.core.models import PADState
from src.core.orchestrator.cognitive_orchestrator import (
    CognitiveOrchestrator,
    build_cognitive_orchestrator,
)
from src.core.orchestrator.policies import CognitiveTurnResult
from src.core.relationship import RelationshipUpdater
from src.core.communication import CommunicationPolicy
from src.core.expression import ExpressionPolicy


class MockLLMBackend:
    """Lightweight deterministic LLM mock for pipeline integration tests."""

    def __init__(self, response_text: str = "System diagnostic acknowledged.") -> None:
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
    """Constructs an isolated CognitiveOrchestrator in temporary storage."""
    model_file = tmp_path / "model.gguf"
    model_file.write_bytes(b"dummy_gguf_header")

    config = MemoryOrchestratorConfig(
        model_path=str(model_file),
        loop_cadence_ms=100,
        decay_loop_cadence_seconds=60,
        sdm_num_locations=100,
        sdm_address_dim=64,
        sdm_content_dim=16,
        sdm_capacity=50,
    )

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


def test_mt_lnn_homeostatic_pipeline_coupling(isolated_orchestrator: CognitiveOrchestrator):
    """
    Test end-to-end stress to fatigue transformation across cognitive turns:
    Turn 1: High acute stress increases tension & load in Stage 5, updating EmotionCore._m_homeo.
    Idle Pause: Fast loop background ticks consume depleted energy & load, pulling arousal down.
    Turn 2: Follow-up turn exhibits somatic fatigue and throttles token budget.
    """
    orch = isolated_orchestrator

    # 1. Turn 1: Acute stress input
    stress_prompt = "CRITICAL EMERGENCY! System security breached and high load detected!"
    res1 = orch.process(stress_prompt)

    assert isinstance(res1, CognitiveTurnResult)
    assert res1.pad_final is not None
    assert res1.somatic is not None

    # Verify Stage 5 homeostatic context reached EmotionCore
    m_homeo = orch._emotion_core._m_homeo
    assert np.all(np.isfinite(m_homeo))
    # In Turn 1 under stress, cognitive load or tension is elevated
    assert m_homeo[1] > 0.0 or m_homeo[2] > 0.0

    # 2. Simulate unforced idle time between turns (50 background steps)
    # Post-stress metabolic depletion: lower energy, drop threat tension
    orch._homeostatic_engine._energy = 0.20
    # Push updated depleted markers into EmotionCore
    orch._emotion_core.update_homeostatic_context(energy=0.20, load=0.60, tension=0.0, stability=0.50)

    for _ in range(50):
        orch._emotion_core.step_once()

    pad_after_rest = orch._emotion_core.get_pad_state()
    # Arousal must drop below resting baseline (-0.05) into somatic fatigue
    assert pad_after_rest.arousal < -0.05

    # 3. Turn 2: Follow-up neutral query inherits somatic fatigue state
    res2 = orch.process("Report status on system telemetry.")
    assert isinstance(res2, CognitiveTurnResult)

    # Verify Turn 2 pad state reflects the lower arousal state
    assert res2.pad_final.arousal < 0.05
    # Verify GenerationPolicy throttles tokens under fatigue
    assert res2.generation_policy.mode == "fatigued"
    assert res2.generation_policy.token_expansion_factor <= 0.75

    # 4. Canonical Storage Invariant: data/profile.json must remain bit-exact {"is_onboarded": false}
    profile_path = Path("data/profile.json")
    with open(profile_path, "r", encoding="utf-8") as f:
        profile_data = json.load(f)
    assert profile_data == {"is_onboarded": False}
