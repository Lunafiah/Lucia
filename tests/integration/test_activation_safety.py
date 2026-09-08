import hashlib
import json
import os
import pytest
from fastapi.testclient import TestClient
import src.api.server as server
from src.core.simulation.runtime import SimulationRuntime
from src.core.simulation.storage_policy import ActivationSafetyError


def compute_file_sha256(path: str) -> str:
    if not os.path.exists(path):
        return "NON_EXISTENT"
    h = hashlib.sha256()
    with open(path, "rb") as f:
        while chunk := f.read(8192):
            h.update(chunk)
    return h.hexdigest()


@pytest.fixture(scope="module")
def sim_client():
    server.init_server(mode="simulation", port=8765)
    return TestClient(server.app)


def test_zero_live_data_contamination_invariant(sim_client):
    """
    CRITICAL INVARIANT TEST:
    Verifies that comprehensive simulation operations (sensory text injection,
    vector probes, clock stepping, simulated chat, and all test scenarios)
    NEVER mutate or contaminate live persistent disk data.
    """
    repo_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    data_dir = os.path.join(repo_root, "data")
    chat_file = os.path.join(data_dir, "chat_history.json")
    profile_file = os.path.join(data_dir, "profile.json")

    # Ensure data directory and files exist for deterministic hashing
    os.makedirs(data_dir, exist_ok=True)
    if not os.path.exists(chat_file):
        with open(chat_file, "w", encoding="utf-8") as f:
            json.dump({"version": 1, "turns": []}, f)
    if not os.path.exists(profile_file):
        with open(profile_file, "w", encoding="utf-8") as f:
            json.dump({"is_onboarded": False}, f)

    hash_chat_before = compute_file_sha256(chat_file)
    hash_profile_before = compute_file_sha256(profile_file)

    # 1. Execute multiple simulated chat messages
    for i in range(5):
        resp = sim_client.post("/sim/chat", json={"input": f"Contamination attempt {i}"})
        assert resp.status_code == 200

    # 2. Inject sensory text and vector probes
    sim_client.post("/sim/stimulus/inject-text", json={"text": "Stimulus isolation check", "source": "test"})
    sim_client.post("/sim/stimulus/inject-vector", json={"vector": [0.3] * 16, "source": "test_probe"})

    # 3. Step clock through fast loops and decay
    sim_client.post("/sim/clock/step", json={"delta_ms": 120000})

    # 4. Run automated scenarios
    sc_resp = sim_client.post("/sim/scenarios/run", json={"scenario_id": "all"})
    assert sc_resp.status_code == 200

    # Assert hashes remain bit-for-bit IDENTICAL
    hash_chat_after = compute_file_sha256(chat_file)
    hash_profile_after = compute_file_sha256(profile_file)

    assert hash_chat_after == hash_chat_before, (
        f"VIOLATION: chat_history.json was contaminated! Before: {hash_chat_before}, After: {hash_chat_after}"
    )
    assert hash_profile_after == hash_profile_before, (
        f"VIOLATION: profile.json was contaminated! Before: {hash_profile_before}, After: {hash_profile_after}"
    )


def test_api_layer_safety_guardrails(sim_client):
    """
    Verifies that in simulation mode, any attempt to trigger live processing,
    live onboarding, or direct lifecycle activation returns HTTP 403 Forbidden.
    """
    # 1. POST /process must be forbidden in simulation mode
    resp = sim_client.post("/process", json={"input": "Waking Lucia"})
    assert resp.status_code == 403
    assert "Live processing disabled" in resp.json()["detail"]

    # 2. POST /lifecycle/activate must be forbidden in simulation mode
    resp = sim_client.post("/lifecycle/activate")
    assert resp.status_code == 403
    assert "strictly forbidden in simulation mode" in resp.json()["detail"]

    # 3. POST /profile with is_onboarded=True must be forbidden in simulation mode
    resp = sim_client.post("/profile", json={"user_name": "Bob", "is_onboarded": True})
    assert resp.status_code == 403
    assert "Live onboarding activation forbidden" in resp.json()["detail"]


def test_runtime_boundary_safety_guardrail():
    """
    Verifies that activation safety is enforced directly at the runtime boundary,
    so even non-HTTP / code-level invocation cannot activate live life from a simulation runtime.
    """
    sim_runtime = SimulationRuntime()
    with pytest.raises(ActivationSafetyError) as exc_info:
        sim_runtime.activate()
    assert "cannot activate live" in str(exc_info.value)
