"""
Unit & Integration Tests for First Activation Blockers 2 & 3.

Covering:
- BLOCKER 2: Legacy Profile Onboarding Rejection (cannot bypass Genesis via POST /profile).
- BLOCKER 3: /process Runtime Activation Gate (live + inactive rejected; live + active proceeds;
  simulation behavior preserved; Genesis/Birth alone does NOT imply active runtime).
"""

from __future__ import annotations

import json
from pathlib import Path
from unittest.mock import MagicMock
import pytest
from starlette.testclient import TestClient

import src.api.server as api_module
from src.core.identity.genesis import (
    execute_genesis,
)
from src.core.models import PADState
from src.core.resource_manager import get_resource_profile

SAMPLE_UUID = "d4e5f6a1-b2c3-4d5e-8f9a-0b1c2d3e4f5a"
SAMPLE_BORN_AT = "2026-10-16T14:00:00.000000Z"
SAMPLE_COMMIT = "b" * 40


@pytest.fixture
def mock_orch():
    orch = MagicMock()
    orch.is_healthy.return_value = True
    orch._degraded = False
    orch._emotion_core.get_pad_state.return_value = PADState(0.25, -0.05, 0.05, 0.0)
    orch._last_somatic = None
    orch._last_constraints = None
    orch._affective_memory.get_all_traces.return_value = []
    orch._affective_memory.trace_count = 0
    orch.process.return_value = "Hello from active Lucia!"
    return orch


@pytest.fixture
def gate_test_env(mock_orch, tmp_path: Path):
    """Provide isolated environment for lifecycle and activation gate testing."""
    ws = tmp_path / "gate_workspace"
    data_dir = ws / "data"
    data_dir.mkdir(parents=True, exist_ok=True)

    profile_file = data_dir / "profile.json"
    profile_file.write_text(json.dumps({"is_onboarded": False}), encoding="utf-8")
    commitment_file = data_dir / "genesis_commitment.json"
    history_file = data_dir / "chat_history.json"

    orig_mode = api_module._mode
    orig_sim = api_module._sim_runtime
    orig_active = api_module._is_live_companion_active
    orig_prof_path = os_environ_prof = None
    orig_history_path = getattr(api_module._history_store, "file_path", None)

    import os
    orig_env_prof = os.environ.get("LUCIA_PROFILE_PATH")
    orig_env_commit = os.environ.get("LUCIA_GENESIS_COMMITMENT_PATH")
    os.environ["LUCIA_PROFILE_PATH"] = str(profile_file)
    os.environ["LUCIA_GENESIS_COMMITMENT_PATH"] = str(commitment_file)

    api_module._history_store.file_path = history_file
    api_module._history_store._ensure_file_exists()
    api_module._orchestrator = mock_orch
    api_module._resource_profile = get_resource_profile("laptop")
    api_module._mode = "live"
    api_module._sim_runtime = None
    api_module._is_live_companion_active = False

    client = TestClient(api_module.app)

    yield {
        "client": client,
        "workspace": ws,
        "profile_file": profile_file,
        "commitment_file": commitment_file,
        "mock_orch": mock_orch,
    }

    # Teardown
    api_module._orchestrator = None
    api_module._resource_profile = None
    api_module._is_live_companion_active = orig_active
    api_module._mode = orig_mode
    api_module._sim_runtime = orig_sim
    if orig_history_path is not None:
        api_module._history_store.file_path = orig_history_path

    if orig_env_prof is not None:
        os.environ["LUCIA_PROFILE_PATH"] = orig_env_prof
    else:
        os.environ.pop("LUCIA_PROFILE_PATH", None)

    if orig_env_commit is not None:
        os.environ["LUCIA_GENESIS_COMMITMENT_PATH"] = orig_env_commit
    else:
        os.environ.pop("LUCIA_GENESIS_COMMITMENT_PATH", None)


class TestBlocker2LegacyProfileSafety:
    def test_post_profile_rejects_direct_is_onboarded_true(self, gate_test_env):
        """Blocker 2: Attempting to set is_onboarded=True via POST /profile returns HTTP 400."""
        client = gate_test_env["client"]
        p_file = gate_test_env["profile_file"]

        resp = client.post("/profile", json={"user_name": "Luna", "is_onboarded": True})
        assert resp.status_code == 400
        assert "Direct onboarding/birth activation via POST /profile is forbidden" in resp.json()["detail"]

        # Assert profile remained untouched
        p_data = json.loads(p_file.read_text(encoding="utf-8"))
        assert p_data == {"is_onboarded": False}

    def test_post_profile_rejects_born_at_injection(self, gate_test_env):
        """Blocker 2: Attempting to inject born_at on un-onboarded profile via POST /profile returns HTTP 400."""
        client = gate_test_env["client"]
        resp = client.post("/profile", json={"born_at": "2026-10-16T12:00:00.000000Z"})
        assert resp.status_code == 400
        assert "Direct 'born_at' mutation via POST /profile is forbidden" in resp.json()["detail"]

    def test_post_profile_rejects_identity_anchor_injection(self, gate_test_env):
        """Blocker 2: Attempting to inject identity_anchor via POST /profile returns HTTP 400."""
        client = gate_test_env["client"]
        fake_anchor = {
            "instance_uuid": SAMPLE_UUID,
            "born_at": SAMPLE_BORN_AT,
            "genesis_commit": SAMPLE_COMMIT,
            "genesis_root_hash": "f" * 64,
        }
        resp = client.post("/profile", json={"identity_anchor": fake_anchor})
        assert resp.status_code == 400
        assert "Direct 'identity_anchor' injection via POST /profile is forbidden" in resp.json()["detail"]

    def test_post_profile_accepts_valid_preferences(self, gate_test_env):
        """Blocker 2: Normal user preference updates succeed without mutating onboarding state."""
        client = gate_test_env["client"]
        p_file = gate_test_env["profile_file"]

        resp = client.post("/profile", json={"user_name": "Luna", "companion_name": "Lucia", "pronouns": "she/her"})
        assert resp.status_code == 200
        p_data = json.loads(p_file.read_text(encoding="utf-8"))
        assert p_data["user_name"] == "Luna"
        assert p_data["companion_name"] == "Lucia"
        assert p_data["pronouns"] == "she/her"
        assert p_data["is_onboarded"] is False


class TestBlocker3ProcessActivationGate:
    def test_process_rejected_when_live_and_inactive(self, gate_test_env):
        """Blocker 3: live + inactive -> POST /process rejected with HTTP 403 runtime_inactive."""
        client = gate_test_env["client"]
        api_module._is_live_companion_active = False

        resp = client.post("/process", json={"input": "Hello Lucia"})
        assert resp.status_code == 403
        data = resp.json()
        assert data["error"] == "runtime_inactive"
        assert "Live companion is inactive" in data["detail"]

    def test_process_proceeds_when_live_and_active(self, gate_test_env):
        """Blocker 3: live + active -> POST /process proceeds normally (returns 200)."""
        client = gate_test_env["client"]
        api_module._is_live_companion_active = True

        resp = client.post("/process", json={"input": "Hello Lucia"})
        assert resp.status_code == 200
        data = resp.json()
        assert data["response"] == "Hello from active Lucia!"

    def test_process_simulation_behavior_unchanged(self, gate_test_env):
        """Blocker 3: Simulation mode rejection contract is preserved."""
        client = gate_test_env["client"]
        api_module._mode = "simulation"
        api_module._sim_runtime = MagicMock()

        resp = client.post("/process", json={"input": "Hello Lucia"})
        assert resp.status_code == 403
        assert "Live processing disabled in simulation mode" in resp.json()["detail"]

    def test_birth_state_alone_does_not_imply_active_runtime(self, gate_test_env):
        """
        Blocker 3: Ontological BORN state alone does NOT activate /process.
        Must transition via POST /lifecycle/activate.
        """
        client = gate_test_env["client"]
        c_file = gate_test_env["commitment_file"]
        p_file = gate_test_env["profile_file"]

        # 1. Perform Genesis (instance becomes BORN + INACTIVE)
        execute_genesis(
            instance_uuid=SAMPLE_UUID,
            born_at=SAMPLE_BORN_AT,
            genesis_commit=SAMPLE_COMMIT,
            commitment_path=c_file,
            profile_path=p_file,
        )

        # Confirm BORN
        assert api_module._is_live_companion_active is False

        # 2. POST /process is still rejected because runtime is INACTIVE
        resp_inactive = client.post("/process", json={"input": "Are you awake?"})
        assert resp_inactive.status_code == 403
        assert resp_inactive.json()["error"] == "runtime_inactive"

        # 3. Explicit First Activation (INACTIVE -> ACTIVE)
        act_resp = client.post("/lifecycle/activate")
        assert act_resp.status_code == 200
        assert act_resp.json()["status"] == "activated"
        assert api_module._is_live_companion_active is True

        # 4. POST /process now succeeds
        resp_active = client.post("/process", json={"input": "Are you awake now?"})
        assert resp_active.status_code == 200
        assert resp_active.json()["response"] == "Hello from active Lucia!"
