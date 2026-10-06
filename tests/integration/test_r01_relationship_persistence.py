"""
tests/integration/test_r01_relationship_persistence.py

Verification test suite for R-01 Remediation:
- Verifies that build_cognitive_orchestrator wires RelationshipUpdater with persistence path.
- Verifies live multi-turn relationship updates are persisted to disk.
- Verifies cold-restart recovery: non-baseline relationship state is restored across process/orchestrator restarts.
"""

from pathlib import Path
from unittest.mock import MagicMock, patch

import numpy as np
import pytest

from src.core.config import MemoryOrchestratorConfig
from src.core.models import BehavioralConstraints
from src.core.orchestrator.cognitive_orchestrator import (
    build_cognitive_orchestrator,
)
from src.core.relationship.persistence import (
    DEFAULT_RELATIONSHIP_PATH,
    load_relationship,
    save_relationship,
)
from src.core.relationship.state import RelationshipState


@pytest.fixture
def test_config(tmp_path):
    model_file = tmp_path / "model.gguf"
    model_file.write_bytes(b"dummy")
    return MemoryOrchestratorConfig(
        model_path=str(model_file),
        loop_cadence_ms=100,
        decay_loop_cadence_seconds=60,
        sdm_num_locations=100,
        sdm_address_dim=64,
        sdm_content_dim=16,
        sdm_capacity=50,
    )


@pytest.fixture
def mock_llm_patch():
    with patch("src.core.orchestrator.cognitive_orchestrator.LLMBackend") as mock_llm_cls:
        mock_llm = MagicMock()
        mock_llm.is_ready.return_value = True
        mock_llm.generate.return_value = "Acknowledged with warmth."
        mock_llm_cls.return_value = mock_llm
        yield mock_llm


def test_r01_default_storage_path_wired(test_config, mock_llm_patch):
    """build_cognitive_orchestrator defaults to DEFAULT_RELATIONSHIP_PATH."""
    orch = build_cognitive_orchestrator(test_config)
    try:
        assert orch.relationship_updater is not None
        assert orch.relationship_updater.storage_path == DEFAULT_RELATIONSHIP_PATH
    finally:
        orch.shutdown()


def test_r01_live_multiturn_persists_to_disk(tmp_path, test_config, mock_llm_patch):
    """Multi-turn interaction updates relationship state and persists to disk."""
    rel_file = tmp_path / "relationship.json"
    assert not rel_file.exists()

    orch = build_cognitive_orchestrator(
        test_config,
        relationship_storage_path=rel_file,
    )

    try:
        # Initial state should be baseline
        init_state = orch.relationship_updater.get_state()
        assert init_state.familiarity == 0.0
        assert len(orch.relationship_updater.history) == 0

        # Turn 1
        res1 = orch.process("Hello Lucia!")
        assert res1 is not None

        # Relationship file must now exist on disk
        assert rel_file.exists(), "relationship.json was not persisted on Turn 1"
        disk_state_1 = load_relationship(rel_file)
        assert disk_state_1.familiarity > init_state.familiarity
        assert len(orch.relationship_updater.history) == 1

        # Turn 2
        res2 = orch.process("It is wonderful working with you today.")
        assert res2 is not None

        disk_state_2 = load_relationship(rel_file)
        assert disk_state_2.familiarity > disk_state_1.familiarity
        assert len(orch.relationship_updater.history) == 2
    finally:
        orch.shutdown()


def test_r01_cold_restart_recovers_accumulated_state(tmp_path, test_config, mock_llm_patch):
    """
    Cold-restart test:
    1. Seed a non-baseline relationship state to disk (e.g. from prior sessions).
    2. Build a brand new CognitiveOrchestrator instance (simulating fresh process startup).
    3. Verify that the new orchestrator loads the non-baseline state rather than RelationshipState.initial().
    4. Verify that turn processing continues from the accumulated state and persists forward.
    """
    rel_file = tmp_path / "relationship.json"

    # 1. Create a non-baseline relationship state representing an established bond
    prior_state = RelationshipState(
        familiarity=0.72,
        trust=0.85,
        closeness=0.68,
        reciprocity=0.75,
    )
    save_relationship(prior_state, filepath=rel_file)
    assert rel_file.exists()

    # 2. Cold-restart: Instantiate a new orchestrator pointing to the persisted file
    cold_orch = build_cognitive_orchestrator(
        test_config,
        relationship_storage_path=rel_file,
    )

    try:
        # 3. Verify state upon startup before any turns are executed
        loaded_state = cold_orch.relationship_updater.get_state()
        baseline_state = RelationshipState.initial()

        # Must NOT be baseline
        assert loaded_state.familiarity == pytest.approx(0.72)
        assert loaded_state.trust == pytest.approx(0.85)
        assert loaded_state.closeness == pytest.approx(0.68)
        assert loaded_state.reciprocity == pytest.approx(0.75)
        assert loaded_state.familiarity != baseline_state.familiarity

        # 4. Process a turn and confirm continuation
        res = cold_orch.process("Good morning, Lucia.")
        assert res is not None

        post_turn_state = cold_orch.relationship_updater.get_state()
        assert post_turn_state.familiarity > loaded_state.familiarity

        # Disk must reflect the turn update
        disk_state = load_relationship(rel_file)
        assert disk_state.familiarity == pytest.approx(post_turn_state.familiarity)
        assert disk_state.familiarity > 0.72
    finally:
        cold_orch.shutdown()
