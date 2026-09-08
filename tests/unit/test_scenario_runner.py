"""
Unit tests for ScenarioRunner — Phase 8.6 Level 2.

Verifies:
- list_scenarios() returns the four canonical scenarios A–D.
- Scenario A (Conversational Turn): sensory pathway confirmed, in-memory history updated, constraints generated.
- Scenario B (Time Leap & Memory Decay): SimClock advances, slow-loop callback triggers, trace decays.
- Scenario C (Emotional Recovery): High-tension stimulus followed by 50 fast ticks → arousal relaxes.
- Scenario D (Zero Live Data Contamination): SHA-256 hashes of data/ files unchanged after sim ops.
- run_all() executes all scenarios and reports aggregated results.
- get_last_results() returns the most recent run.
"""

from __future__ import annotations

import pytest

from src.core.simulation.runtime import SimulationRuntime
from src.core.simulation.scenario_runner import ScenarioRunner
from src.core.simulation.storage_policy import ActivationSafetyError


def _make_runner() -> tuple[ScenarioRunner, SimulationRuntime]:
    runtime = SimulationRuntime()
    runner = ScenarioRunner(runtime)
    return runner, runtime


# ---------------------------------------------------------------------------
# list_scenarios
# ---------------------------------------------------------------------------

class TestListScenarios:
    def test_returns_four_scenarios(self):
        runner, _ = _make_runner()
        scenarios = runner.list_scenarios()
        assert len(scenarios) == 4

    def test_all_four_ids_present(self):
        runner, _ = _make_runner()
        ids = {s["id"] for s in runner.list_scenarios()}
        assert ids == {"scenario_a", "scenario_b", "scenario_c", "scenario_d"}

    def test_each_scenario_has_name_and_description(self):
        runner, _ = _make_runner()
        for s in runner.list_scenarios():
            assert "name" in s
            assert "description" in s
            assert len(s["name"]) > 0
            assert len(s["description"]) > 0


# ---------------------------------------------------------------------------
# Scenario A: Conversational Turn
# ---------------------------------------------------------------------------

class TestScenarioA:
    def test_scenario_a_passes(self):
        runner, _ = _make_runner()
        result = runner.run_scenario("scenario_a")
        assert result["passed"] is True, f"Scenario A failed: {result['assertions']}"

    def test_sensory_pathway_assertion(self):
        runner, _ = _make_runner()
        result = runner.run_scenario("scenario_a")
        assertions = {a["name"]: a for a in result["assertions"]}
        assert assertions["sensory_pathway_verified"]["passed"] is True

    def test_in_memory_history_updated_assertion(self):
        runner, _ = _make_runner()
        result = runner.run_scenario("scenario_a")
        assertions = {a["name"]: a for a in result["assertions"]}
        assert assertions["in_memory_history_updated"]["passed"] is True

    def test_behavioral_constraints_assertion(self):
        runner, _ = _make_runner()
        result = runner.run_scenario("scenario_a")
        assertions = {a["name"]: a for a in result["assertions"]}
        assert assertions["behavioral_constraints_derived"]["passed"] is True

    def test_output_contains_stimulus_entry(self):
        runner, _ = _make_runner()
        result = runner.run_scenario("scenario_a")
        assert "output" in result
        assert "stimulus" in result["output"]
        assert result["output"]["stimulus"]["pathway"] == "sensory_text"

    def test_elapsed_ms_is_positive(self):
        runner, _ = _make_runner()
        result = runner.run_scenario("scenario_a")
        assert result["elapsed_ms"] > 0


# ---------------------------------------------------------------------------
# Scenario B: Time Leap & Memory Decay
# ---------------------------------------------------------------------------

class TestScenarioB:
    def test_scenario_b_passes(self):
        runner, _ = _make_runner()
        result = runner.run_scenario("scenario_b")
        assert result["passed"] is True, f"Scenario B failed: {result['assertions']}"

    def test_slow_ticks_executed(self):
        runner, _ = _make_runner()
        result = runner.run_scenario("scenario_b")
        assertions = {a["name"]: a for a in result["assertions"]}
        assert assertions["slow_ticks_executed"]["passed"] is True

    def test_trace_weight_decayed(self):
        runner, _ = _make_runner()
        result = runner.run_scenario("scenario_b")
        assertions = {a["name"]: a for a in result["assertions"]}
        assert assertions["trace_weight_decayed"]["passed"] is True

    def test_virtual_time_advanced(self):
        runner, runtime = _make_runner()
        runner.run_scenario("scenario_b")
        # After 3600s time leap, clock should be at or beyond 3600s
        assert runtime.sim_clock.virtual_time_s >= 3600.0


# ---------------------------------------------------------------------------
# Scenario C: Emotional Recovery
# ---------------------------------------------------------------------------

class TestScenarioC:
    def test_scenario_c_passes(self):
        runner, _ = _make_runner()
        result = runner.run_scenario("scenario_c")
        assert result["passed"] is True, f"Scenario C failed: {result['assertions']}"

    def test_arousal_relaxed_assertion(self):
        runner, _ = _make_runner()
        result = runner.run_scenario("scenario_c")
        assertions = {a["name"]: a for a in result["assertions"]}
        assert assertions["arousal_relaxed"]["passed"] is True

    def test_initial_and_recovered_pad_returned(self):
        runner, _ = _make_runner()
        result = runner.run_scenario("scenario_c")
        assert "initial_pad" in result
        assert "recovered_pad" in result

    def test_initial_arousal_reflects_tension(self):
        runner, _ = _make_runner()
        result = runner.run_scenario("scenario_c")
        # After tension stimulus, arousal should be non-trivially elevated
        assert result["initial_pad"]["arousal"] > -0.2


# ---------------------------------------------------------------------------
# Scenario D: Zero Live Data Contamination
# ---------------------------------------------------------------------------

class TestScenarioD:
    def test_scenario_d_passes(self):
        runner, _ = _make_runner()
        result = runner.run_scenario("scenario_d")
        assert result["passed"] is True, f"Scenario D failed: {result['assertions']}"

    def test_live_activation_blocked_assertion(self):
        runner, _ = _make_runner()
        result = runner.run_scenario("scenario_d")
        assertions = {a["name"]: a for a in result["assertions"]}
        assert assertions["live_activation_blocked_at_runtime_boundary"]["passed"] is True

    def test_chat_history_bit_identical_assertion(self):
        runner, _ = _make_runner()
        result = runner.run_scenario("scenario_d")
        assertions = {a["name"]: a for a in result["assertions"]}
        assert assertions["chat_history_bit_identical"]["passed"] is True

    def test_profile_bit_identical_assertion(self):
        runner, _ = _make_runner()
        result = runner.run_scenario("scenario_d")
        assertions = {a["name"]: a for a in result["assertions"]}
        assert assertions["profile_bit_identical"]["passed"] is True

    def test_files_checked_paths_reported(self):
        runner, _ = _make_runner()
        result = runner.run_scenario("scenario_d")
        assert "files_checked" in result
        assert len(result["files_checked"]) == 2


# ---------------------------------------------------------------------------
# run_all
# ---------------------------------------------------------------------------

class TestRunAll:
    def test_run_all_returns_all_four_results(self):
        runner, _ = _make_runner()
        summary = runner.run_all()
        assert "scenarios" in summary
        assert set(summary["scenarios"].keys()) == {"scenario_a", "scenario_b", "scenario_c", "scenario_d"}

    def test_run_all_all_passed_flag_is_true(self):
        runner, _ = _make_runner()
        summary = runner.run_all()
        assert summary["all_passed"] is True, f"Not all scenarios passed: {summary['scenarios']}"

    def test_run_all_timestamp_is_positive(self):
        runner, _ = _make_runner()
        summary = runner.run_all()
        assert summary["timestamp"] > 0

    def test_get_last_results_reflects_run_all(self):
        runner, _ = _make_runner()
        summary = runner.run_all()
        last = runner.get_last_results()
        assert last["all_passed"] == summary["all_passed"]

    def test_get_last_results_empty_before_run(self):
        runner, _ = _make_runner()
        last = runner.get_last_results()
        assert isinstance(last, dict)
        # Initially empty
        assert last == {}


# ---------------------------------------------------------------------------
# Unknown scenario ID
# ---------------------------------------------------------------------------

class TestUnknownScenario:
    def test_unknown_scenario_raises_value_error(self):
        runner, _ = _make_runner()
        with pytest.raises(ValueError, match="Unknown scenario ID"):
            runner.run_scenario("scenario_xyz")
