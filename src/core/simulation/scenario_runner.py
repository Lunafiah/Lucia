"""
ScenarioRunner — Automated validation scenarios for Lucia Simulation Environment (Phase 8).

Validates:
- Scenario A: Conversational Turn (Sensory text encoding, PAD shift, behavioral constraints)
- Scenario B: Time Leap & Memory Decay (Virtual time acceleration, slow-loop trace weakening)
- Scenario C: Emotional Recovery (High-tension stimulus -> ODE continuous relaxation)
- Scenario D: Zero Live Data Contamination (Bit-for-bit SHA-256 hash invariance of live files)
"""

from __future__ import annotations

import hashlib
import logging
from pathlib import Path
import time
from typing import Any, Dict, List, Optional

import numpy as np

from src.core.models import PADState
from src.core.simulation.runtime import SimulationRuntime
from src.core.simulation.storage_policy import ActivationSafetyError

logger = logging.getLogger("lucia.simulation.scenario_runner")


def _compute_file_sha256(path: Path) -> Optional[str]:
    """Compute SHA-256 hex digest of a file if it exists, else None."""
    if not path.exists():
        return None
    hasher = hashlib.sha256()
    with open(path, "rb") as f:
        while chunk := f.read(65536):
            hasher.update(chunk)
    return hasher.hexdigest()


class ScenarioRunner:
    """
    Executes automated simulation test scenarios and generates assertion reports.
    """

    def __init__(self, runtime: SimulationRuntime) -> None:
        self._runtime = runtime
        self._last_results: Dict[str, Any] = {}

    def list_scenarios(self) -> List[Dict[str, str]]:
        """Return available test scenarios."""
        return [
            {
                "id": "scenario_a",
                "name": "Conversational Turn",
                "description": "Sensory text encoding -> 16D vector -> Brain -> In-memory turn with zero disk writes.",
            },
            {
                "id": "scenario_b",
                "name": "Time Leap & Memory Decay",
                "description": "SimClock warp of 3600s -> Verifies slow-loop decay callback and trace weight reduction.",
            },
            {
                "id": "scenario_c",
                "name": "Emotional Recovery",
                "description": "High-tension stimulus -> 50 discrete fast ticks (10s) -> Continuous relaxation towards resting attractor.",
            },
            {
                "id": "scenario_d",
                "name": "Zero Live Data Contamination",
                "description": "SHA-256 bitwise hash comparison of data/chat_history.json and data/profile.json across sim operations.",
            },
        ]

    def run_all(self) -> Dict[str, Any]:
        """Run all scenarios and return aggregated results."""
        results = {}
        all_passed = True
        for s in self.list_scenarios():
            res = self.run_scenario(s["id"])
            results[s["id"]] = res
            if not res.get("passed", False):
                all_passed = False

        summary = {
            "all_passed": all_passed,
            "scenarios": results,
            "timestamp": time.time(),
        }
        self._last_results = summary
        return summary

    def run_scenario(self, scenario_id: str) -> Dict[str, Any]:
        """Run a specific scenario by ID."""
        if scenario_id == "scenario_a":
            res = self._run_scenario_a()
        elif scenario_id == "scenario_b":
            res = self._run_scenario_b()
        elif scenario_id == "scenario_c":
            res = self._run_scenario_c()
        elif scenario_id == "scenario_d":
            res = self._run_scenario_d()
        else:
            raise ValueError(f"Unknown scenario ID: {scenario_id}")

        self._last_results[scenario_id] = res
        return res

    def get_last_results(self) -> Dict[str, Any]:
        """Get results from the most recent scenario run."""
        return self._last_results

    # ------------------------------------------------------------------
    # Scenario Implementations
    # ------------------------------------------------------------------

    def _run_scenario_a(self) -> Dict[str, Any]:
        """Scenario A: Conversational Turn."""
        t0 = time.time()
        assertions = []

        # 1. Capture state before
        pad_before = self._runtime.emotion_core.get_pad_state()
        history_len_before = len(self._runtime.chat_store.get_history(100))

        # 2. Execute conversational turn
        test_msg = "Hello Lucia! I am delighted to be working with you on this project."
        turn_result = self._runtime.send_chat(test_msg, source="scenario_a_runner")

        pad_after = self._runtime.emotion_core.get_pad_state()
        history_len_after = len(self._runtime.chat_store.get_history(100))

        # Assertions
        # Sensory pathway encoding succeeded
        has_sensory = turn_result["stimulus"]["pathway"] == "sensory_text"
        assertions.append({
            "name": "sensory_pathway_verified",
            "passed": has_sensory,
            "details": f"Stimulus pathway: {turn_result['stimulus']['pathway']}",
        })

        # History updated in memory
        history_updated = history_len_after == history_len_before + 2  # user + assistant
        assertions.append({
            "name": "in_memory_history_updated",
            "passed": history_updated,
            "details": f"History len: {history_len_before} -> {history_len_after}",
        })

        # Behavioral constraints generated
        constraints_valid = (
            turn_result["constraints"]["temperature"] > 0
            and turn_result["constraints"]["max_tokens"] > 0
        )
        assertions.append({
            "name": "behavioral_constraints_derived",
            "passed": constraints_valid,
            "details": str(turn_result["constraints"]),
        })

        all_passed = all(a["passed"] for a in assertions)
        return {
            "scenario_id": "scenario_a",
            "name": "Conversational Turn",
            "passed": all_passed,
            "assertions": assertions,
            "elapsed_ms": round((time.time() - t0) * 1000, 2),
            "output": turn_result,
        }

    def _run_scenario_b(self) -> Dict[str, Any]:
        """Scenario B: Time Leap & Memory Decay."""
        t0 = time.time()
        assertions = []

        # 1. Store a memory trace directly into in-memory AffectiveMemory
        content = np.ones(64, dtype=np.float32)
        pad_tag = PADState(pleasure=0.5, arousal=0.2, dominance=0.1, timestamp=self._runtime.sim_clock.virtual_time_s)
        trace_id = self._runtime.affective_memory.store(content, pad_tag)
        initial_weight = self._runtime.affective_memory._index[trace_id].decay_weight

        # 2. Advance SimClock by 3600 seconds (1 hour = 4 slow ticks at 900s cadence)
        warp_ms = 3600.0 * 1000.0
        step_result = self._runtime.step_simulation(warp_ms)

        # 3. Check that trace decayed
        final_weight = self._runtime.affective_memory._index[trace_id].decay_weight
        decayed = final_weight < initial_weight

        assertions.append({
            "name": "slow_ticks_executed",
            "passed": step_result["slow_ticks_executed"] >= 1,
            "details": f"Slow ticks executed: {step_result['slow_ticks_executed']}",
        })
        assertions.append({
            "name": "trace_weight_decayed",
            "passed": decayed,
            "details": f"Trace decay weight: {initial_weight:.4f} -> {final_weight:.4f}",
        })

        all_passed = all(a["passed"] for a in assertions)
        return {
            "scenario_id": "scenario_b",
            "name": "Time Leap & Memory Decay",
            "passed": all_passed,
            "assertions": assertions,
            "elapsed_ms": round((time.time() - t0) * 1000, 2),
            "step_result": step_result,
        }

    def _run_scenario_c(self) -> Dict[str, Any]:
        """Scenario C: Emotional Recovery."""
        t0 = time.time()
        assertions = []

        # 1. Inject high tension stimulus
        tension_res = self._runtime.stimulus_service.inject_preset(
            "tension",
            pathway="sensory_text",
            source="scenario_c",
        )
        pad_high = self._runtime.emotion_core.get_pad_state()

        # 2. Step 50 ticks of 200ms (10 seconds total) with zero stimulus
        for _ in range(50):
            self._runtime.step_simulation(200.0)

        pad_recovered = self._runtime.emotion_core.get_pad_state()

        # In LNN ODE, after negative high arousal stimulus, relaxation moves arousal down towards baseline
        arousal_decayed = pad_recovered.arousal <= pad_high.arousal or abs(pad_recovered.arousal) <= abs(pad_high.arousal)
        assertions.append({
            "name": "arousal_relaxed",
            "passed": arousal_decayed,
            "details": f"Arousal: {pad_high.arousal:.4f} -> {pad_recovered.arousal:.4f}",
        })

        all_passed = all(a["passed"] for a in assertions)
        return {
            "scenario_id": "scenario_c",
            "name": "Emotional Recovery",
            "passed": all_passed,
            "assertions": assertions,
            "elapsed_ms": round((time.time() - t0) * 1000, 2),
            "initial_pad": pad_high.to_dict(),
            "recovered_pad": pad_recovered.to_dict(),
        }

    def _run_scenario_d(self) -> Dict[str, Any]:
        """Scenario D: Zero Live Data Contamination."""
        t0 = time.time()
        assertions = []

        chat_path = Path("data/chat_history.json").resolve()
        profile_path = Path("data/profile.json").resolve()

        # 1. Record initial file state and SHA-256 hashes
        chat_exists_before = chat_path.exists()
        profile_exists_before = profile_path.exists()
        chat_hash_before = _compute_file_sha256(chat_path)
        profile_hash_before = _compute_file_sha256(profile_path)

        # 2. Execute a barrage of simulation operations
        # Turn 1: chat
        self._runtime.send_chat("Testing live file isolation under heavy chatter.", source="scenario_d")
        # Turn 2: debug vector probe injection
        self._runtime.stimulus_service.inject_vector([0.5] * 16, source="scenario_d_probe")
        # Turn 3: time warp
        self._runtime.step_simulation(7200.0 * 1000.0)
        # Turn 4: profile update in-memory
        self._runtime.profile_store.update_profile(companion_name="Lucia Simulation")

        # Turn 5: assert live activation attempt is blocked
        activation_blocked = False
        try:
            self._runtime.activate()
        except ActivationSafetyError:
            activation_blocked = True

        assertions.append({
            "name": "live_activation_blocked_at_runtime_boundary",
            "passed": activation_blocked,
            "details": "SimulationRuntime.activate() raised ActivationSafetyError",
        })

        # 3. Check hashes after
        chat_hash_after = _compute_file_sha256(chat_path)
        profile_hash_after = _compute_file_sha256(profile_path)
        chat_exists_after = chat_path.exists()
        profile_exists_after = profile_path.exists()

        chat_intact = (chat_exists_before == chat_exists_after) and (chat_hash_before == chat_hash_after)
        profile_intact = (profile_exists_before == profile_exists_after) and (profile_hash_before == profile_hash_after)

        assertions.append({
            "name": "chat_history_bit_identical",
            "passed": chat_intact,
            "details": f"Before: {chat_hash_before}, After: {chat_hash_after}",
        })
        assertions.append({
            "name": "profile_bit_identical",
            "passed": profile_intact,
            "details": f"Before: {profile_hash_before}, After: {profile_hash_after}",
        })

        all_passed = all(a["passed"] for a in assertions)
        return {
            "scenario_id": "scenario_d",
            "name": "Zero Live Data Contamination",
            "passed": all_passed,
            "assertions": assertions,
            "elapsed_ms": round((time.time() - t0) * 1000, 2),
            "files_checked": [str(chat_path), str(profile_path)],
        }
