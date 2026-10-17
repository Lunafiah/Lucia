"""
Unit and Integration Tests for Lucia Awakening Lifecycle.

Governing Specifications:
- ADR-034 (ARCH-034: Identity Authority, Instance Exclusivity & Anti-Branching Boundary)
- Genesis Semantic & Protocol Contract (G1–G4)
- INV-1 (One Continuous Life)
- INV-8 (Genesis Gate Invariant: Simulation != Activation; Live state untouched)

Targeted Test Coverage:
A. NOT_BORN → Birth → BORN → Activation → ACTIVE
B. BORN + INACTIVE → Activation → ACTIVE
C. Existing Genesis evidence is never regenerated
D. Birth failure prevents Activation
E. Activation failure after Birth leaves BORN + INACTIVE
F. ENDED rejects Awakening and cannot Re-Genesis
G. Repeated Awaken on ACTIVE is safe/idempotent according to the existing contract
H. UI / API routes: POST /lifecycle/awaken and GET /lifecycle/status
I. Invariant Guard: Live repo profile.json remains {"is_onboarded": false} and no live commitment exists.
"""

from __future__ import annotations

import json
import os
from pathlib import Path
from unittest.mock import MagicMock
import pytest
from starlette.testclient import TestClient

import src.api.server as api_module
from src.core.identity.genesis import (
    GenesisCommitment,
    GenesisVerificationOutcome,
    OntologyState,
    RuntimeState,
    TerminalLifecycleError,
    execute_genesis,
    mark_lifecycle_ended,
    verify_genesis,
)
from src.core.identity.operator_genesis import (
    OperatorPreconditionError,
)
from src.core.identity.awakening import (
    AwakeningResult,
    awaken_companion,
    get_awakening_status,
)
from src.core.models import PADState

SAMPLE_UUID = "c1d2e3f4-a5b6-7c8d-9e0f-1a2b3c4d5e6f"
SAMPLE_BORN_AT = "2026-10-17T12:00:00.000000Z"
SAMPLE_COMMIT = "e" * 40


@pytest.fixture
def isolated_workspace(tmp_path: Path):
    """Provide isolated test directory with un-onboarded profile for unit testing."""
    ws = tmp_path / "awakening_workspace"
    data_dir = ws / "data"
    data_dir.mkdir(parents=True, exist_ok=True)
    profile_path = data_dir / "profile.json"
    profile_path.write_text(json.dumps({"is_onboarded": False}), encoding="utf-8")
    return ws


class TestAwakeningLifecycleCore:
    """Core domain tests for awaken_companion orchestrator."""

    def test_A_not_born_to_birth_to_active(self, isolated_workspace):
        """A. First-time Lucia: NOT_BORN -> Genesis Birth -> BORN + INACTIVE -> First Activation -> BORN + ACTIVE."""
        c_path = isolated_workspace / "data" / "genesis_commitment.json"
        p_path = isolated_workspace / "data" / "profile.json"

        # Verify initial state is NOT_BORN
        initial_verif = verify_genesis(commitment_path=c_path, profile_path=p_path)
        assert initial_verif.outcome == GenesisVerificationOutcome.NOT_FOUND
        assert initial_verif.ontology_state == OntologyState.NOT_BORN

        activation_called = False

        def _activate():
            nonlocal activation_called
            activation_called = True

        result = awaken_companion(
            confirm_ceremony=True,
            user_name="Luna",
            companion_name="Lucia",
            workspace_dir=isolated_workspace,
            commitment_path=c_path,
            profile_path=p_path,
            genesis_commit=SAMPLE_COMMIT,
            instance_uuid=SAMPLE_UUID,
            born_at=SAMPLE_BORN_AT,
            is_runtime_active=False,
            activate_runtime_fn=_activate,
        )

        # Assert full awakening
        assert result.status == "awakened"
        assert result.ontology_state == OntologyState.BORN.value
        assert result.runtime_state == RuntimeState.ACTIVE.value
        assert result.genesis_performed is True
        assert result.activation_performed is True
        assert activation_called is True

        # Assert durable commitment exists and is verified
        assert c_path.exists()
        post_verif = verify_genesis(commitment_path=c_path, profile_path=p_path)
        assert post_verif.outcome == GenesisVerificationOutcome.VERIFIED_BORN
        assert post_verif.ontology_state == OntologyState.BORN

    def test_B_born_inactive_to_active(self, isolated_workspace):
        """B. Existing Lucia: BORN + INACTIVE -> First Activation -> BORN + ACTIVE (no second Birth)."""
        c_path = isolated_workspace / "data" / "genesis_commitment.json"
        p_path = isolated_workspace / "data" / "profile.json"

        # Pre-create valid durable Genesis commitment (BORN + INACTIVE)
        pre_commit = execute_genesis(
            instance_uuid=SAMPLE_UUID,
            born_at=SAMPLE_BORN_AT,
            genesis_commit=SAMPLE_COMMIT,
            workspace_dir=isolated_workspace,
            commitment_path=c_path,
            profile_path=p_path,
        )
        assert c_path.exists()

        activation_called = False

        def _activate():
            nonlocal activation_called
            activation_called = True

        result = awaken_companion(
            confirm_ceremony=True,
            user_name="Luna",
            companion_name="Lucia",
            workspace_dir=isolated_workspace,
            commitment_path=c_path,
            profile_path=p_path,
            is_runtime_active=False,
            activate_runtime_fn=_activate,
        )

        assert result.status == "activated"
        assert result.ontology_state == OntologyState.BORN.value
        assert result.runtime_state == RuntimeState.ACTIVE.value
        assert result.genesis_performed is False  # Never perform Genesis Birth again!
        assert result.activation_performed is True
        assert activation_called is True
        assert result.genesis_root_hash == pre_commit.genesis_root_hash

    def test_C_existing_genesis_evidence_never_regenerated(self, isolated_workspace):
        """C. Existing Genesis evidence is strictly immutable and never regenerated."""
        c_path = isolated_workspace / "data" / "genesis_commitment.json"
        p_path = isolated_workspace / "data" / "profile.json"

        execute_genesis(
            instance_uuid=SAMPLE_UUID,
            born_at=SAMPLE_BORN_AT,
            genesis_commit=SAMPLE_COMMIT,
            workspace_dir=isolated_workspace,
            commitment_path=c_path,
            profile_path=p_path,
        )

        original_bytes = c_path.read_bytes()
        original_mtime = c_path.stat().st_mtime_ns

        # Call awaken multiple times
        awaken_companion(
            confirm_ceremony=True,
            workspace_dir=isolated_workspace,
            commitment_path=c_path,
            profile_path=p_path,
            is_runtime_active=False,
            activate_runtime_fn=lambda: None,
        )

        assert c_path.read_bytes() == original_bytes
        assert c_path.stat().st_mtime_ns == original_mtime

    def test_D_birth_failure_prevents_activation(self, isolated_workspace):
        """D. Birth failure prevents Activation; instance remains NOT_BORN."""
        c_path = isolated_workspace / "data" / "genesis_commitment.json"
        p_path = isolated_workspace / "data" / "profile.json"

        activation_called = False

        def _activate():
            nonlocal activation_called
            activation_called = True

        # confirm_ceremony=False must fail closed
        with pytest.raises(OperatorPreconditionError) as exc_info:
            awaken_companion(
                confirm_ceremony=False,
                workspace_dir=isolated_workspace,
                commitment_path=c_path,
                profile_path=p_path,
                genesis_commit=SAMPLE_COMMIT,
                is_runtime_active=False,
                activate_runtime_fn=_activate,
            )

        assert "requires explicit confirmation" in str(exc_info.value)
        assert activation_called is False
        assert not c_path.exists()

        verif = verify_genesis(commitment_path=c_path, profile_path=p_path)
        assert verif.outcome == GenesisVerificationOutcome.NOT_FOUND

    def test_E_activation_failure_after_birth_leaves_born_inactive(self, isolated_workspace):
        """E. Activation failure after Birth preserves BORN + INACTIVE and allows retry without re-Genesis."""
        c_path = isolated_workspace / "data" / "genesis_commitment.json"
        p_path = isolated_workspace / "data" / "profile.json"

        # Attempt 1: Activation fails
        def _failing_activate():
            raise RuntimeError("Hardware activation pipeline failed!")

        with pytest.raises(RuntimeError) as exc_info:
            awaken_companion(
                confirm_ceremony=True,
                user_name="Luna",
                companion_name="Lucia",
                workspace_dir=isolated_workspace,
                commitment_path=c_path,
                profile_path=p_path,
                genesis_commit=SAMPLE_COMMIT,
                instance_uuid=SAMPLE_UUID,
                born_at=SAMPLE_BORN_AT,
                is_runtime_active=False,
                activate_runtime_fn=_failing_activate,
            )

        assert "Hardware activation pipeline failed!" in str(exc_info.value)

        # Invariant: durable commitment is PRESERVED on disk!
        assert c_path.exists()
        verif = verify_genesis(commitment_path=c_path, profile_path=p_path)
        assert verif.outcome == GenesisVerificationOutcome.VERIFIED_BORN
        assert verif.ontology_state == OntologyState.BORN

        # Attempt 2: Operator retries with working activation
        retry_activated = False

        def _working_activate():
            nonlocal retry_activated
            retry_activated = True

        retry_result = awaken_companion(
            confirm_ceremony=True,
            workspace_dir=isolated_workspace,
            commitment_path=c_path,
            profile_path=p_path,
            is_runtime_active=False,
            activate_runtime_fn=_working_activate,
        )

        assert retry_result.status == "activated"
        assert retry_result.genesis_performed is False  # Did NOT repeat Genesis!
        assert retry_result.activation_performed is True
        assert retry_activated is True

    def test_F_ended_rejects_awakening_and_cannot_regenesis(self, isolated_workspace):
        """F. ENDED instance strictly rejects Awakening and cannot Re-Genesis."""
        c_path = isolated_workspace / "data" / "genesis_commitment.json"
        p_path = isolated_workspace / "data" / "profile.json"

        execute_genesis(
            instance_uuid=SAMPLE_UUID,
            born_at=SAMPLE_BORN_AT,
            genesis_commit=SAMPLE_COMMIT,
            workspace_dir=isolated_workspace,
            commitment_path=c_path,
            profile_path=p_path,
        )
        mark_lifecycle_ended(commitment_path=c_path, profile_path=p_path)

        verif = verify_genesis(commitment_path=c_path, profile_path=p_path)
        assert verif.ontology_state == OntologyState.ENDED

        with pytest.raises(TerminalLifecycleError) as exc_info:
            awaken_companion(
                confirm_ceremony=True,
                workspace_dir=isolated_workspace,
                commitment_path=c_path,
                profile_path=p_path,
                is_runtime_active=False,
                activate_runtime_fn=lambda: None,
            )

        assert "terminal state" in str(exc_info.value).lower()
        assert "permanently prohibited" in str(exc_info.value).lower()

    def test_G_repeated_awaken_on_active_is_safe_idempotent(self, isolated_workspace):
        """G. Repeated Awaken on an already ACTIVE instance is safe and idempotent."""
        c_path = isolated_workspace / "data" / "genesis_commitment.json"
        p_path = isolated_workspace / "data" / "profile.json"

        execute_genesis(
            instance_uuid=SAMPLE_UUID,
            born_at=SAMPLE_BORN_AT,
            genesis_commit=SAMPLE_COMMIT,
            workspace_dir=isolated_workspace,
            commitment_path=c_path,
            profile_path=p_path,
        )

        # Call awaken with is_runtime_active=True
        activation_called = False

        def _activate():
            nonlocal activation_called
            activation_called = True

        result = awaken_companion(
            confirm_ceremony=True,
            workspace_dir=isolated_workspace,
            commitment_path=c_path,
            profile_path=p_path,
            is_runtime_active=True,
            activate_runtime_fn=_activate,
        )

        assert result.status == "already_active"
        assert result.ontology_state == OntologyState.BORN.value
        assert result.runtime_state == RuntimeState.ACTIVE.value
        assert result.genesis_performed is False
        assert result.activation_performed is False
        assert activation_called is False


class TestAwakeningAPIRoutes:
    """Integration tests for FastAPI endpoints: POST /lifecycle/awaken & GET /lifecycle/status."""

    @pytest.fixture
    def api_env(self, tmp_path: Path):
        ws = tmp_path / "api_test_workspace"
        data_dir = ws / "data"
        data_dir.mkdir(parents=True, exist_ok=True)
        profile_file = data_dir / "profile.json"
        profile_file.write_text(json.dumps({"is_onboarded": False}), encoding="utf-8")
        commitment_file = data_dir / "genesis_commitment.json"

        orig_mode = api_module._mode
        orig_sim = api_module._sim_runtime
        orig_active = api_module._is_live_companion_active
        orig_prof_env = os.environ.get("LUCIA_PROFILE_PATH")
        orig_commit_env = os.environ.get("LUCIA_GENESIS_COMMITMENT_PATH")
        orig_ws_env = os.environ.get("LUCIA_WORKSPACE_PATH")

        os.environ["LUCIA_PROFILE_PATH"] = str(profile_file)
        os.environ["LUCIA_GENESIS_COMMITMENT_PATH"] = str(commitment_file)
        os.environ["LUCIA_WORKSPACE_PATH"] = str(ws)

        mock_orch = MagicMock()
        mock_orch.is_healthy.return_value = True
        api_module._orchestrator = mock_orch
        api_module._mode = "live"
        api_module._sim_runtime = None
        api_module._is_live_companion_active = False

        client = TestClient(api_module.app)

        yield {
            "client": client,
            "workspace": ws,
            "profile_file": profile_file,
            "commitment_file": commitment_file,
        }

        # Cleanup
        api_module._orchestrator = None
        api_module._is_live_companion_active = orig_active
        api_module._mode = orig_mode
        api_module._sim_runtime = orig_sim

        if orig_prof_env is not None:
            os.environ["LUCIA_PROFILE_PATH"] = orig_prof_env
        else:
            os.environ.pop("LUCIA_PROFILE_PATH", None)

        if orig_commit_env is not None:
            os.environ["LUCIA_GENESIS_COMMITMENT_PATH"] = orig_commit_env
        else:
            os.environ.pop("LUCIA_GENESIS_COMMITMENT_PATH", None)

        if orig_ws_env is not None:
            os.environ["LUCIA_WORKSPACE_PATH"] = orig_ws_env
        else:
            os.environ.pop("LUCIA_WORKSPACE_PATH", None)

    def test_api_status_endpoint(self, api_env):
        """GET /lifecycle/status returns accurate ontology and runtime state."""
        client = api_env["client"]
        res = client.get("/lifecycle/status")
        assert res.status_code == 200
        data = res.json()
        assert data["outcome"] == GenesisVerificationOutcome.NOT_FOUND.value
        assert data["ontology_state"] == OntologyState.NOT_BORN.value
        assert data["runtime_state"] == RuntimeState.INACTIVE.value
        assert data["is_onboarded"] is False

    def test_api_awaken_first_time(self, api_env):
        """POST /lifecycle/awaken on NOT_BORN executes Birth and First Activation."""
        client = api_env["client"]

        payload = {
            "user_name": "OperatorLuna",
            "companion_name": "Lucia",
            "confirm_ceremony": True,
        }
        res = client.post("/lifecycle/awaken", json=payload)
        assert res.status_code == 200
        data = res.json()

        assert data["status"] == "awakened"
        assert data["ontology_state"] == OntologyState.BORN.value
        assert data["runtime_state"] == RuntimeState.ACTIVE.value
        assert data["genesis_performed"] is True
        assert data["activation_performed"] is True
        assert api_module._is_live_companion_active is True

        # Check GET /lifecycle/status reflects active companion
        status_res = client.get("/lifecycle/status")
        assert status_res.status_code == 200
        status_data = status_res.json()
        assert status_data["outcome"] == GenesisVerificationOutcome.VERIFIED_BORN.value
        assert status_data["ontology_state"] == OntologyState.BORN.value
        assert status_data["runtime_state"] == RuntimeState.ACTIVE.value

    def test_api_awaken_idempotent_when_already_active(self, api_env):
        """POST /lifecycle/awaken on already ACTIVE instance is safe and idempotent."""
        client = api_env["client"]

        # First awaken
        res1 = client.post("/lifecycle/awaken", json={"confirm_ceremony": True})
        assert res1.status_code == 200
        assert res1.json()["status"] == "awakened"

        # Second awaken
        res2 = client.post("/lifecycle/awaken", json={"confirm_ceremony": True})
        assert res2.status_code == 200
        assert res2.json()["status"] == "already_active"
        assert res2.json()["genesis_performed"] is False
        assert res2.json()["activation_performed"] is False

    def test_api_simulation_mode_blocks_awakening(self, api_env):
        """Simulation mode strictly forbids awakening ceremony (403 Forbidden)."""
        client = api_env["client"]
        api_module._mode = "simulation"

        res = client.post("/lifecycle/awaken", json={"confirm_ceremony": True})
        assert res.status_code == 403
        assert "simulation mode" in res.json()["detail"].lower()

    def test_api_ended_lifecycle_returns_410_gone(self, api_env):
        """POST /lifecycle/awaken on ENDED lifecycle returns 410 GONE."""
        client = api_env["client"]

        # First awaken to BORN + ACTIVE
        res = client.post("/lifecycle/awaken", json={"confirm_ceremony": True})
        assert res.status_code == 200

        # Terminate lifecycle
        end_res = client.post("/lifecycle/end")
        assert end_res.status_code == 200

        # Attempt to re-awaken
        re_awaken = client.post("/lifecycle/awaken", json={"confirm_ceremony": True})
        assert re_awaken.status_code == 410
        assert "terminal state" in re_awaken.json()["detail"].lower()


class TestRepositoryInvariantProtection:
    """Strict verification of Invariant INV-8: Live repository state is never mutated during tests."""

    def test_live_repository_remains_untouched(self):
        """Verify live repository profile.json remains {"is_onboarded": false} and no live commitment exists."""
        live_profile = Path("data/profile.json")
        assert live_profile.exists()
        assert live_profile.read_text(encoding="utf-8").strip() == '{"is_onboarded": false}'

        live_commitment = Path("data/genesis_commitment.json")
        assert not live_commitment.exists()
