"""
Benchmark Runner and Telemetry Recorder for Phase 19 Research Experiments.

Executes standardized scenario trajectories, coordinates virtual time,
and logs fine-grained time-series telemetry across multiple horizons.
"""

from __future__ import annotations

import time
from dataclasses import dataclass, field
from typing import List, Optional, Tuple

import numpy as np

from tests.evaluation_phase19.multi_timescale_model import MultiTimescaleEmotionCore
from tests.evaluation_phase19.scenarios import ScenarioTrajectory


@dataclass
class TelemetrySnapshot:
    t: float
    tick: int
    step_name: str
    pad: Tuple[float, float, float]
    dist_philia: float
    h_fast_norm: float
    s_slow_norm: float
    energy: float
    cognitive_load: float
    tension: float
    stability: float
    step_latency_ms: float = 0.0


@dataclass
class ScenarioResult:
    scenario_id: str
    description: str
    snapshots: List[TelemetrySnapshot]
    total_ticks: int
    elapsed_sim_time: float
    execution_wall_time: float
    mean_step_latency_ms: float
    max_step_latency_ms: float
    metadata: dict = field(default_factory=dict)


class Phase19BenchmarkRunner:
    """Orchestrates scenario execution and telemetry logging in isolated virtual time."""

    def __init__(self, tick_dt: float = 0.20) -> None:
        self.tick_dt = tick_dt  # 200 ms standard cadence

    def run_trajectory(
        self,
        model: MultiTimescaleEmotionCore,
        scenario: ScenarioTrajectory,
        record_idle_interval: int = 1,
    ) -> ScenarioResult:
        """
        Executes a ScenarioTrajectory on the given MultiTimescaleEmotionCore.
        Advances time deterministically tick-by-tick.
        """
        snapshots: List[TelemetrySnapshot] = []
        step_latencies: List[float] = []
        sim_time = 0.0
        wall_start = time.perf_counter()

        for step_idx, step in enumerate(scenario.steps):
            # Update homeostatic overrides if specified
            if step.homeo_override is not None:
                e, c, t_val, s = step.homeo_override
                model.update_homeostatic_context(e, c, t_val, s)

            # Inject stimulus
            tok = model.push_stimulus(step.vector)

            # Advance ODE
            t0 = time.perf_counter()
            pad = model.commit_stimulus(tok)
            step_lat = (time.perf_counter() - t0) * 1000.0
            step_latencies.append(step_lat)
            sim_time += self.tick_dt

            # Snapshot
            p_tuple = (pad.pleasure, pad.arousal, pad.dominance)
            d_phil = model.get_attractor_distance()
            hf_norm = float(np.linalg.norm(model.get_fast_state()))
            ss_norm = float(np.linalg.norm(model.get_slow_state()))

            snap = TelemetrySnapshot(
                t=sim_time,
                tick=model.tick_count(),
                step_name=step.name,
                pad=p_tuple,
                dist_philia=d_phil,
                h_fast_norm=hf_norm,
                s_slow_norm=ss_norm,
                energy=float(model._m_homeo[0]),
                cognitive_load=float(model._m_homeo[1]),
                tension=float(model._m_homeo[2]),
                stability=float(model._m_homeo[3]),
                step_latency_ms=step_lat,
            )
            snapshots.append(snap)

            # Unforced idle progression if requested
            if step.idle_after_seconds > 0:
                idle_ticks = int(round(step.idle_after_seconds / self.tick_dt))
                for idle_i in range(idle_ticks):
                    t0_idle = time.perf_counter()
                    pad_idle = model.step_once()
                    lat_idle = (time.perf_counter() - t0_idle) * 1000.0
                    step_latencies.append(lat_idle)
                    sim_time += self.tick_dt

                    # Periodically record snapshots during long idle intervals
                    if (idle_i + 1) % record_idle_interval == 0 or idle_i == idle_ticks - 1:
                        p_idle = (pad_idle.pleasure, pad_idle.arousal, pad_idle.dominance)
                        snapshots.append(
                            TelemetrySnapshot(
                                t=sim_time,
                                tick=model.tick_count(),
                                step_name=f"{step.name}_idle_{idle_i+1}",
                                pad=p_idle,
                                dist_philia=model.get_attractor_distance(),
                                h_fast_norm=float(np.linalg.norm(model.get_fast_state())),
                                s_slow_norm=float(np.linalg.norm(model.get_slow_state())),
                                energy=float(model._m_homeo[0]),
                                cognitive_load=float(model._m_homeo[1]),
                                tension=float(model._m_homeo[2]),
                                stability=float(model._m_homeo[3]),
                                step_latency_ms=lat_idle,
                            )
                        )

        total_wall = time.perf_counter() - wall_start
        mean_lat = float(np.mean(step_latencies)) if step_latencies else 0.0
        max_lat = float(np.max(step_latencies)) if step_latencies else 0.0

        return ScenarioResult(
            scenario_id=scenario.scenario_id,
            description=scenario.description,
            snapshots=snapshots,
            total_ticks=model.tick_count(),
            elapsed_sim_time=sim_time,
            execution_wall_time=total_wall,
            mean_step_latency_ms=mean_lat,
            max_step_latency_ms=max_lat,
        )
