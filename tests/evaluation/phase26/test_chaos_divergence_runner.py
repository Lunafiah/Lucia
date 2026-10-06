"""
tests/evaluation/phase26/test_chaos_divergence_runner.py

Unit and integration tests for DynamicChaosRunner:
- Epsilon = 0 yields zero numerical drift (exact zero or sub-epsilon floor)
- Deterministic replay reproducibility under same seed
- Strict positivity and scaling of divergence when epsilon > 0
- Telemetry schema completeness and valid JSON serialization
- Component separation (fast reactive, slow latent, projective PAD)
"""

import json
from pathlib import Path
import pytest
import numpy as np

from tests.evaluation.phase26.chaos_divergence_runner import (
    DynamicChaosRunner,
    RunSummary,
    TrajectoryPoint,
)


def test_null_epsilon_zero_drift_floor():
    """
    Verification that epsilon = 0.0 results in EXACT zero divergence
    between paired replicas stepped under identical stimulus schedules.
    """
    runner = DynamicChaosRunner(
        epsilons=[0.0],
        seeds=[1001],
        timesteps=20,
        dt=0.200,
        output_path=None,
    )
    res = runner.run_benchmark()

    # Max limbic divergence across all 20 steps under eps=0 must be exactly 0.0
    null_stats = res["D_chaos_distributions"]["epsilon_0.0"]
    assert null_stats["max_d_limbic"]["mean"] == 0.0
    assert null_stats["max_d_pad"]["mean"] == 0.0
    assert null_stats["final_d_limbic"]["mean"] == 0.0
    assert res["numerical_tolerance"]["drift_floor_status"] == "EXACT_ZERO"


def test_deterministic_replay_reproducibility():
    """
    Verification that two independent invocations with identical parameters
    and seeds yield bit-exact identical divergence values.
    """
    runner1 = DynamicChaosRunner(
        epsilons=[1e-5],
        seeds=[2002],
        timesteps=15,
        dt=0.200,
        output_path=None,
    )
    res1 = runner1.run_benchmark()

    runner2 = DynamicChaosRunner(
        epsilons=[1e-5],
        seeds=[2002],
        timesteps=15,
        dt=0.200,
        output_path=None,
    )
    res2 = runner2.run_benchmark()

    run1 = res1["raw_runs"][0]
    run2 = res2["raw_runs"][0]

    assert run1["max_d_limbic"] == run2["max_d_limbic"]
    assert run1["final_d_limbic"] == run2["final_d_limbic"]
    assert run1["max_d_pad"] == run2["max_d_pad"]


def test_positive_epsilon_produces_measurable_divergence():
    """
    Verification that injecting epsilon > 0 yields strictly positive,
    measurable divergence across ODE fast, slow, and PAD states.
    """
    runner = DynamicChaosRunner(
        epsilons=[1e-4],
        seeds=[3003],
        timesteps=25,
        dt=0.200,
        output_path=None,
    )
    res = runner.run_benchmark()

    run = res["raw_runs"][0]
    assert run["max_d_limbic"] > 0.0
    assert run["max_d_pad"] > 0.0
    assert run["final_d_limbic"] > 0.0
    assert run["amplification_factor"] > 0.0

    # Verify component trajectory points exist
    traj = run["trajectory"]
    assert len(traj) == 25
    for pt in traj:
        assert pt["d_fast"] >= 0.0
        assert pt["d_slow"] >= 0.0
        assert pt["d_limbic"] >= 0.0
        assert pt["d_pad"] >= 0.0


def test_telemetry_schema_and_serialization(tmp_path):
    """
    Verification that the output telemetry conforms to the formal JSON schema.
    """
    runner = DynamicChaosRunner(
        epsilons=[0.0, 1e-6],
        seeds=[1001, 2002],
        timesteps=10,
        dt=0.200,
        output_path=tmp_path / "test_telemetry.json",
    )
    results = runner.run_benchmark()

    assert "metadata" in results
    assert "numerical_tolerance" in results
    assert "D_chaos_distributions" in results
    assert "raw_runs" in results

    meta = results["metadata"]
    assert meta["timesteps"] == 10
    assert meta["dt_sec"] == 0.200
    assert len(meta["stimulus_turn_steps"]) == 3

    dist = results["D_chaos_distributions"]
    assert "epsilon_0.0" in dist
    assert "epsilon_1e-06" in dist

    # Verify JSON round-trip
    test_json_file = tmp_path / "test_telemetry.json"
    with open(test_json_file, "w", encoding="utf-8") as f:
        json.dump(results, f)

    with open(test_json_file, "r", encoding="utf-8") as f:
        loaded = json.load(f)
    assert len(loaded["raw_runs"]) == 4
