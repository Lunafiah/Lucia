import pytest
from src.core.simulation.runtime import SimulationRuntime
from src.core.simulation.storage_policy import (
    ActivationSafetyError,
    InMemoryChatHistoryStore,
    InMemoryProfileStore,
    StoragePolicy,
)


class TestSimulationRuntime:
    def test_runtime_lifecycle_initialization(self):
        runtime = SimulationRuntime()
        assert runtime.state == "SIMULATING"
        assert not runtime.is_live
        assert runtime.is_simulated

    def test_runtime_activation_safety_exception(self):
        runtime = SimulationRuntime()
        # Direct attempt to invoke live activation on simulation runtime MUST raise ActivationSafetyError
        with pytest.raises(ActivationSafetyError):
            runtime.activate()

    def test_in_memory_chat_history_isolation(self):
        store = InMemoryChatHistoryStore()
        assert store.get_turns() == []

        turn_id = store.add_turn(
            user_input="Hello in simulation",
            response_text="Hello, observer",
            pad_before={"pleasure": 0.25, "arousal": -0.05, "dominance": 0.05},
            pad_after={"pleasure": 0.30, "arousal": 0.00, "dominance": 0.10},
        )
        assert turn_id is not None
        assert len(store.get_turns()) == 2
        assert store.get_turns()[0]["content"] == "Hello in simulation"

        # Clearing turns
        store.clear()
        assert store.get_turns() == []

    def test_in_memory_profile_store_isolation(self):
        store = InMemoryProfileStore()
        assert not store.is_onboarded()
        assert store.get_profile()["user_name"] == "Developer"

        store.save_profile({"user_name": "Alice", "is_onboarded": True})
        assert store.is_onboarded()
        assert store.get_profile()["user_name"] == "Alice"

    def test_runtime_stimulus_text_injection(self):
        runtime = SimulationRuntime()
        res = runtime.inject_sensory_text("Good morning, Lucia! I am happy to see you.", source="desktop_ui")

        assert res["pathway"] == "sensory_text"
        assert "pad_after" in res
        assert res["pad_after"]["pleasure"] > 0.0

    def test_runtime_vector_probe_injection(self):
        runtime = SimulationRuntime()
        vector_16d = [0.6, 0.4, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0]
        res = runtime.inject_vector_probe(vector_16d, source="debug_probe")

        assert res["pathway"] == "debug_vector_probe"
        assert res["source"] == "debug_probe"
        assert "pad_after" in res

    def test_runtime_snapshot(self):
        runtime = SimulationRuntime()
        snap = runtime.get_snapshot()

        assert "runtime" in snap
        assert snap["runtime"]["mode"] == "simulation"
        assert snap["runtime"]["is_live"] is False
        assert "pad" in snap
        assert "somatic" in snap
        assert "constraints" in snap
        assert "clock" in snap
        assert "storage" in snap
        assert snap["storage"]["storage_type"] == "InMemoryIsolated"
