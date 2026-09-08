import pytest
from fastapi.testclient import TestClient
import src.api.server as server


@pytest.fixture(scope="module")
def client():
    # Initialize server in simulation mode
    server.init_server(mode="simulation", port=8765)
    return TestClient(server.app)


def test_runtime_descriptor(client):
    response = client.get("/runtime/descriptor")
    assert response.status_code == 200
    data = response.json()
    assert data["mode"] == "simulation"
    assert data["is_live"] is False
    assert data["is_simulated"] is True
    assert "capabilities" in data
    assert "virtual_clock" in data["capabilities"]


def test_runtime_snapshot(client):
    response = client.get("/runtime/snapshot")
    assert response.status_code == 200
    data = response.json()
    assert "pad" in data
    assert "somatic" in data
    assert "constraints" in data
    assert "clock" in data
    assert "storage" in data
    assert data["storage"]["storage_type"] == "InMemoryIsolated"


def test_sim_clock_endpoints(client):
    # Step
    res = client.post("/sim/clock/step", json={"delta_ms": 400})
    assert res.status_code == 200
    assert abs(res.json()["virtual_time_s"] - 0.4) < 1e-4

    # Pause
    res = client.post("/sim/clock/pause")
    assert res.status_code == 200
    assert res.json()["is_paused"] is True

    # Speed
    res = client.post("/sim/clock/speed", json={"multiplier": 5.0})
    assert res.status_code == 200
    assert res.json()["speed_factor"] == 5.0

    # Resume
    res = client.post("/sim/clock/resume")
    assert res.status_code == 200
    assert res.json()["is_paused"] is False

    # Reset
    res = client.post("/sim/clock/reset", json={"reset_time_s": 0.0})
    assert res.status_code == 200
    assert res.json()["virtual_time_s"] == 0.0


def test_stimulus_text_injection(client):
    res = client.post("/sim/stimulus/inject-text", json={"text": "A calm warm greeting", "source": "desktop_ui"})
    assert res.status_code == 200
    data = res.json()
    assert data["status"] == "ok"
    assert data["pathway"] == "sensory_text"
    assert "pad_after" in data


def test_stimulus_vector_probe_injection(client):
    vector = [0.5, 0.2] + [0.0] * 14
    res = client.post("/sim/stimulus/inject-vector", json={"vector": vector, "source": "debug_probe"})
    assert res.status_code == 200
    data = res.json()
    assert data["status"] == "ok"
    assert data["pathway"] == "debug_vector_probe"
    assert data["source"] == "debug_probe"


def test_stimulus_presets_and_history(client):
    # Get presets
    res = client.get("/sim/stimulus/presets")
    assert res.status_code == 200
    assert "calm" in res.json()["presets"]

    # Inject preset
    res = client.post("/sim/stimulus/preset", json={"preset": "calm", "pathway": "sensory_text"})
    assert res.status_code == 200
    assert res.json()["status"] == "ok"

    # History
    res = client.get("/sim/stimulus/history?limit=10")
    assert res.status_code == 200
    history = res.json()["history"]
    assert len(history) > 0


def test_scenarios_endpoints(client):
    # List scenarios
    res = client.get("/sim/scenarios/list")
    assert res.status_code == 200
    scenarios = res.json()["scenarios"]
    assert len(scenarios) >= 4

    # Run scenario A
    res = client.post("/sim/scenarios/run", json={"scenario_id": "scenario_a"})
    assert res.status_code == 200
    results = res.json()["results"]
    assert len(results) == 1
    assert results[0]["passed"] is True

    # Get results cache
    res = client.get("/sim/scenarios/results")
    assert res.status_code == 200
    assert len(res.json()["results"]) >= 1


def test_simulation_chat(client):
    res = client.post("/sim/chat", json={"input": "Hello Lucia in sandbox"})
    assert res.status_code == 200
    data = res.json()
    assert "response" in data
    assert data["call_id"].startswith("sim_")
