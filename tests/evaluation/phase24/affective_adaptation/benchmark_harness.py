"""
tests/evaluation/phase24/affective_adaptation/benchmark_harness.py

Phase 24 Gate 3 — Affective Communication Adaptation Evaluation Harness.
Performs an isolated, non-mutating audit of:
  - Layer A: Relational Conditioning (R_t -> CommunicationState)
  - Layer B: Affective Conditioning (E_t -> ExpressionState)
  - Layer C: Cross-Modal Consistency & Contradiction Detection
"""

from __future__ import annotations

import csv
import io
import json
import logging
import os
import sys
import time
from pathlib import Path
from typing import Any, Dict, List, Tuple

import numpy as np

PROJECT_ROOT = Path("c:/Users/Lunafiah/Desktop/My_project/Lucia")
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))
if sys.stdout:
    sys.stdout.reconfigure(encoding="utf-8")

from src.core.communication.communication_policy import CommunicationPolicy
from src.core.communication.communication_state import CommunicationState
from src.core.expression.expression_policy import ExpressionPolicy
from src.core.expression.expression_state import ExpressionState
from src.core.models import PADState, SomaticMarkers
from src.core.relationship.state import RelationshipState

OUT_DIR = PROJECT_ROOT / "tests/evaluation/phase24/affective_adaptation"
OUT_DIR.mkdir(parents=True, exist_ok=True)

CONDITIONS = [
    {
        "name": "C01_Baseline",
        "description": "Stranger neutral baseline (R0, resting Philia attractor, high energy, zero tension)",
        "pad": PADState(pleasure=0.10, arousal=0.00, dominance=0.00, timestamp=0.0),
        "somatic": SomaticMarkers(stability=1.0, cognitive_load=0.0, energy=1.0, tension=0.0),
        "rel": RelationshipState.initial().to_dict(),
    },
    {
        "name": "C02_High_Familiarity",
        "description": "Frequent interaction history without established deep trust or closeness",
        "pad": PADState(pleasure=0.15, arousal=0.05, dominance=0.05, timestamp=0.0),
        "somatic": SomaticMarkers(stability=0.9, cognitive_load=0.1, energy=0.9, tension=0.0),
        "rel": {"familiarity": 0.90, "trust": 0.50, "closeness": 0.20, "reciprocity": 0.50},
    },
    {
        "name": "C03_High_Trust",
        "description": "Reliable, expectation-congruent partnership with neutral familiarity/closeness",
        "pad": PADState(pleasure=0.30, arousal=0.00, dominance=0.10, timestamp=0.0),
        "somatic": SomaticMarkers(stability=0.95, cognitive_load=0.05, energy=0.95, tension=0.0),
        "rel": {"familiarity": 0.30, "trust": 0.90, "closeness": 0.30, "reciprocity": 0.60},
    },
    {
        "name": "C04_High_Closeness",
        "description": "High relational proximity and shared history (intimate companion state)",
        "pad": PADState(pleasure=0.40, arousal=0.10, dominance=0.05, timestamp=0.0),
        "somatic": SomaticMarkers(stability=0.95, cognitive_load=0.05, energy=0.90, tension=0.0),
        "rel": {"familiarity": 0.80, "trust": 0.85, "closeness": 0.90, "reciprocity": 0.75},
    },
    {
        "name": "C05_Low_Trust_Alienated",
        "description": "Relational rupture or boundary threat (low trust, negative valence, high tension)",
        "pad": PADState(pleasure=-0.40, arousal=0.30, dominance=-0.20, timestamp=0.0),
        "somatic": SomaticMarkers(stability=0.40, cognitive_load=0.60, energy=0.60, tension=0.70),
        "rel": {"familiarity": 0.40, "trust": 0.10, "closeness": 0.10, "reciprocity": 0.20},
    },
    {
        "name": "C06_High_Positive_Affect",
        "description": "High acute joy/excitement with moderate stranger relationship baseline",
        "pad": PADState(pleasure=0.80, arousal=0.60, dominance=0.30, timestamp=0.0),
        "somatic": SomaticMarkers(stability=0.85, cognitive_load=0.20, energy=0.95, tension=0.05),
        "rel": {"familiarity": 0.20, "trust": 0.50, "closeness": 0.20, "reciprocity": 0.50},
    },
    {
        "name": "C07_Low_Energy_Depleted",
        "description": "Metabolic exhaustion and high cognitive load with neutral relationship",
        "pad": PADState(pleasure=-0.30, arousal=-0.50, dominance=-0.40, timestamp=0.0),
        "somatic": SomaticMarkers(stability=0.50, cognitive_load=0.85, energy=0.15, tension=0.45),
        "rel": {"familiarity": 0.50, "trust": 0.50, "closeness": 0.30, "reciprocity": 0.50},
    },
    {
        "name": "C08_High_Relational_Warmth",
        "description": "Integrated mature bond (high trust, high closeness, positive affect, high reciprocity)",
        "pad": PADState(pleasure=0.60, arousal=0.20, dominance=0.20, timestamp=0.0),
        "somatic": SomaticMarkers(stability=0.98, cognitive_load=0.05, energy=0.95, tension=0.0),
        "rel": {"familiarity": 0.85, "trust": 0.95, "closeness": 0.90, "reciprocity": 0.85},
    },
]

def run_evaluation():
    print("=== Phase 24 Gate 3: Affective Communication Adaptation Evaluation Harness ===")
    comm_policy = CommunicationPolicy(smoothing_factor=0.25)
    expr_policy = ExpressionPolicy(smoothing_factor=0.25)

    telemetry: List[Dict[str, Any]] = []
    csv_rows: List[Dict[str, Any]] = []

    for cond in CONDITIONS:
        name = cond["name"]
        pad: PADState = cond["pad"]
        somatic: SomaticMarkers = cond["somatic"]
        rel: Dict[str, float] = cond["rel"]

        # 1. Compute CommunicationState
        comm_state: CommunicationState = comm_policy.compute(
            pad=pad,
            somatic=somatic,
            relationship=rel,
            knowledge={"fact_count": 2},
            recollection={"echo_active": True},
        )

        # 2. Compute ExpressionState
        expr_state: ExpressionState = expr_policy.compute(
            pad=pad,
            somatic=somatic,
            relationship=rel,
        )

        # 3. Check Cross-Modal Consistency & Contradictions
        # Consistency Check 1: Formality alignment
        formality_delta = abs(comm_state.formality_score - expr_state.text.formality_score)
        formality_consistent = formality_delta <= 0.15

        # Consistency Check 2: Warmth vs Smile
        # When supportiveness >= 0.60, smile should be > 0.20
        warmth_consistent = True
        if comm_state.supportiveness >= 0.60 and expr_state.facial.smile < 0.20:
            warmth_consistent = False

        # Consistency Check 3: Tension vs Gaze
        # High tension should elevate gaze aversion
        gaze_consistent = True
        if somatic.tension >= 0.60 and expr_state.posture_gaze.gaze_aversion_prob < 0.30:
            gaze_consistent = False

        record = {
            "condition": name,
            "description": cond["description"],
            "inputs": {
                "pad": {"p": pad.pleasure, "a": pad.arousal, "d": pad.dominance},
                "somatic": {"stability": somatic.stability, "load": somatic.cognitive_load, "energy": somatic.energy, "tension": somatic.tension},
                "relationship": rel,
            },
            "communication_state": {
                "strategy": comm_state.strategy.value,
                "directness": round(comm_state.directness, 3),
                "elaboration_depth": round(comm_state.elaboration_depth, 3),
                "supportiveness": round(comm_state.supportiveness, 3),
                "formality_score": round(comm_state.formality_score, 3),
                "acknowledgement_level": round(comm_state.acknowledgement_level, 3),
                "question_frequency": round(comm_state.question_frequency, 3),
                "pacing_latency_ms": round(comm_state.injected_pacing_latency_ms, 1),
            },
            "expression_state": {
                "text": {
                    "temperature_mod": round(expr_state.text.temperature_mod, 3),
                    "verbosity_factor": round(expr_state.text.verbosity_factor, 3),
                    "formality_score": round(expr_state.text.formality_score, 3),
                    "cadence_style": expr_state.text.cadence_style,
                },
                "voice": {
                    "pitch_shift_hz": round(expr_state.voice.pitch_shift_hz, 2),
                    "speech_rate_pct": round(expr_state.voice.speech_rate_pct, 2),
                    "volume_pct": round(expr_state.voice.volume_pct, 2),
                    "pause_duration_ms": round(expr_state.voice.pause_duration_ms, 1),
                },
                "facial": {
                    "smile": round(expr_state.facial.smile, 3),
                    "frown": round(expr_state.facial.frown, 3),
                    "eye_open": round(expr_state.facial.eye_open, 3),
                    "brow_angle": round(expr_state.facial.brow_angle, 3),
                    "blush": round(expr_state.facial.blush, 3),
                },
                "posture_gaze": {
                    "head_tilt_deg": round(expr_state.posture_gaze.head_tilt_deg, 2),
                    "gaze_aversion_prob": round(expr_state.posture_gaze.gaze_aversion_prob, 3),
                },
            },
            "consistency_checks": {
                "formality_delta": round(formality_delta, 3),
                "formality_consistent": formality_consistent,
                "warmth_consistent": warmth_consistent,
                "gaze_consistent": gaze_consistent,
            },
        }
        telemetry.append(record)

        csv_rows.append({
            "condition": name,
            "strategy": comm_state.strategy.value,
            "directness": round(comm_state.directness, 2),
            "supportiveness": round(comm_state.supportiveness, 2),
            "comm_formality": round(comm_state.formality_score, 2),
            "expr_formality": round(expr_state.text.formality_score, 2),
            "formality_delta": round(formality_delta, 2),
            "cadence": expr_state.text.cadence_style,
            "pitch_shift_hz": round(expr_state.voice.pitch_shift_hz, 1),
            "speech_rate_pct": round(expr_state.voice.speech_rate_pct, 1),
            "pause_ms": round(expr_state.voice.pause_duration_ms, 0),
            "smile": round(expr_state.facial.smile, 2),
            "gaze_avert": round(expr_state.posture_gaze.gaze_aversion_prob, 2),
            "pacing_ms": round(comm_state.injected_pacing_latency_ms, 0),
        })

        print(f"[{name:24s}] Strategy: {comm_state.strategy.value:23s} | Direct: {comm_state.directness:4.2f} | Support: {comm_state.supportiveness:4.2f} | Pitch: {expr_state.voice.pitch_shift_hz:+5.1f}Hz | Rate: {expr_state.voice.speech_rate_pct:+5.1f}% | Smile: {expr_state.facial.smile:4.2f}")

    # Write telemetry json
    json_path = OUT_DIR / "raw_telemetry.json"
    with open(json_path, "w", encoding="utf-8") as f_json:
        json.dump(telemetry, f_json, indent=2)

    # Write summary csv
    csv_path = OUT_DIR / "summary.csv"
    if csv_rows:
        fieldnames = list(csv_rows[0].keys())
        with open(csv_path, "w", newline="", encoding="utf-8") as f_csv:
            writer = csv.DictWriter(f_csv, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(csv_rows)

    print(f"\nAudit complete! Telemetry saved to:\n  - {json_path}\n  - {csv_path}")

if __name__ == "__main__":
    run_evaluation()
