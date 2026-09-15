"""
tests/evaluation_phase18/telemetry.py

Telemetry Recording and Backward Provenance Linker for Lucia Phase 18.
Maintains continuous state tracking, multi-session history, cross-modal synchronization,
and deterministic SHA-256 fingerprinting for every cognitive turn.
"""

from __future__ import annotations

from dataclasses import asdict, dataclass, field
import hashlib
import json
from pathlib import Path
import time
from typing import Any, Dict, List, Optional, Tuple

import numpy as np

from tests.evaluation_phase18.harness import TurnTelemetrySnapshot


@dataclass
class ScenarioExecutionSummary:
    """Summary of all turns executed within a single evaluation scenario."""
    scenario_id: str
    session_id: str
    turn_count: int
    start_timestamp: float
    end_timestamp: float
    output_language: str = "ja-JP"
    
    # Dynamics statistics
    mean_pleasure: float = 0.0
    mean_arousal: float = 0.0
    mean_dominance: float = 0.0
    mean_surprise: float = 0.0
    mean_tension: float = 0.0
    mean_energy: float = 0.0
    
    # Relationship trajectory
    relationship_initial: Dict[str, float] = field(default_factory=dict)
    relationship_final: Dict[str, float] = field(default_factory=dict)
    delta_trust: float = 0.0
    delta_closeness: float = 0.0
    delta_familiarity: float = 0.0
    delta_continuity: float = 0.0
    
    # Latencies
    mean_turn_duration_ms: float = 0.0
    p95_turn_duration_ms: float = 0.0
    max_turn_duration_ms: float = 0.0
    
    # Invariant verification
    max_delta_l2_norm: float = 0.0
    boundary_violations_detected: int = 0
    all_states_bounded: bool = True
    
    # Provenance
    turn_snapshots: List[TurnTelemetrySnapshot] = field(default_factory=list)
    state_fingerprint: str = ""

    def finalize(self) -> None:
        """Compute aggregate metrics across all turns."""
        if not self.turn_snapshots:
            return

        self.turn_count = len(self.turn_snapshots)
        p_vals = [s.pad_committed.get("pleasure", 0.0) for s in self.turn_snapshots]
        a_vals = [s.pad_committed.get("arousal", 0.0) for s in self.turn_snapshots]
        d_vals = [s.pad_committed.get("dominance", 0.0) for s in self.turn_snapshots]
        s_vals = [s.surprise for s in self.turn_snapshots]
        t_vals = [s.homeostatic_markers.get("tension", 0.0) for s in self.turn_snapshots]
        e_vals = [s.homeostatic_markers.get("energy", 1.0) for s in self.turn_snapshots]
        durations = [s.total_turn_duration_ms for s in self.turn_snapshots]
        delta_l2s = [s.delta_l2_norm for s in self.turn_snapshots]

        self.mean_pleasure = float(np.mean(p_vals))
        self.mean_arousal = float(np.mean(a_vals))
        self.mean_dominance = float(np.mean(d_vals))
        self.mean_surprise = float(np.mean(s_vals))
        self.mean_tension = float(np.mean(t_vals))
        self.mean_energy = float(np.mean(e_vals))

        durations_sorted = sorted(durations)
        self.mean_turn_duration_ms = float(np.mean(durations))
        p95_idx = int(len(durations_sorted) * 0.95)
        self.p95_turn_duration_ms = float(durations_sorted[min(p95_idx, len(durations_sorted) - 1)])
        self.max_turn_duration_ms = float(max(durations))

        self.max_delta_l2_norm = float(max(delta_l2s))
        self.boundary_violations_detected = sum(1 for s in self.turn_snapshots if s.boundary_violation)

        # Relationship deltas
        first_rel = self.turn_snapshots[0].relationship_pre
        last_rel = self.turn_snapshots[-1].relationship_post
        self.relationship_initial = first_rel
        self.relationship_final = last_rel
        self.delta_trust = last_rel.get("trust", 0.5) - first_rel.get("trust", 0.5)
        self.delta_closeness = last_rel.get("closeness", 0.1) - first_rel.get("closeness", 0.1)
        self.delta_familiarity = last_rel.get("familiarity", 0.1) - first_rel.get("familiarity", 0.1)
        self.delta_continuity = last_rel.get("continuity", 0.1) - first_rel.get("continuity", 0.1)

        # Check bounds
        bounded = True
        for s in self.turn_snapshots:
            for k, v in s.pad_committed.items():
                if abs(v) > 1.0001:
                    bounded = False
            for k, v in s.homeostatic_markers.items():
                if v < -0.0001 or v > 1.0001:
                    bounded = False
            for k, v in s.relationship_post.items():
                if v < -0.0001 or v > 1.0001:
                    bounded = False
        self.all_states_bounded = bounded

        # Compute scenario state fingerprint
        concat_hashes = "".join([s.state_hash for s in self.turn_snapshots])
        self.state_fingerprint = hashlib.sha256(concat_hashes.encode("utf-8")).hexdigest()

    def to_dict(self) -> Dict[str, Any]:
        data = asdict(self)
        data["turn_snapshots"] = [asdict(s) for s in self.turn_snapshots]
        return data


class TelemetryStore:
    """Saves and indexes scenario telemetry logs in the artifacts directory."""

    def __init__(self, telemetry_dir: Path) -> None:
        self.telemetry_dir = telemetry_dir
        self.telemetry_dir.mkdir(parents=True, exist_ok=True)

    def save_scenario_summary(self, summary: ScenarioExecutionSummary) -> Path:
        """Serialize scenario execution summary to disk."""
        filename = f"{summary.scenario_id}_{summary.session_id}_telemetry.json"
        out_path = self.telemetry_dir / filename
        with open(out_path, "w", encoding="utf-8") as f:
            json.dump(summary.to_dict(), f, indent=2, ensure_ascii=False)
        return out_path
