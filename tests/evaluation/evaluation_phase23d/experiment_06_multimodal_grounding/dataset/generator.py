"""Deterministic Multimodal Signal Generator for EXP-06: Multimodal Grounding.

Generates continuous multimodal sensory streams without natural-language tokens:
1. Continuous Limbic ODE States: [P, A, D] in [-1, 1]^3, Energy in [0, 1], Cognitive Load in [0, 1]
2. eGeMAPS Acoustic Prosody Features: F0 mean/jitter, loudness/energy, speech rate
3. Conversational Rhythm / Temporal Cadence: inter-turn latency, response density
4. Multimodal convergent and conflicting conditions
5. Adversarial noise, dropout, and boundary oscillations
"""

from __future__ import annotations

import math
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional, Tuple


@dataclass
class MultimodalSample:
    sample_id: str
    scenario_type: str
    description: str
    pad: Optional[Tuple[float, float, float]]  # (Pleasure, Arousal, Dominance)
    energy: Optional[float]                    # [0, 1]
    cognitive_load: Optional[float]            # [0, 1]
    acoustic_f0: Optional[float]               # Hz (mean fundamental frequency)
    acoustic_jitter: Optional[float]           # relative jitter
    acoustic_energy: Optional[float]           # normalized RMS energy [0, 1]
    acoustic_rate: Optional[float]             # syllables per second
    temporal_trajectory: Optional[List[Dict[str, float]]] = None
    expected_concept: str = ""
    expected_conflict: bool = False
    expected_uncertainty: float = 0.0


def generate_exp06_corpus() -> Dict[str, Any]:
    samples: List[MultimodalSample] = [
        # A. Single-modality grounding: PAD only
        MultimodalSample(
            sample_id="SM_PAD_01",
            scenario_type="single_modality_pad",
            description="High pleasure, moderate arousal -> AFFECT_JOY",
            pad=(0.75, 0.40, 0.35),
            energy=0.80,
            cognitive_load=0.20,
            acoustic_f0=None,
            acoustic_jitter=None,
            acoustic_energy=None,
            acoustic_rate=None,
            expected_concept="AFFECT_JOY",
        ),
        MultimodalSample(
            sample_id="SM_PAD_02",
            scenario_type="single_modality_pad",
            description="Negative pleasure, low arousal, low dominance -> AFFECT_SORROW",
            pad=(-0.70, -0.35, -0.45),
            energy=0.30,
            cognitive_load=0.60,
            acoustic_f0=None,
            acoustic_jitter=None,
            acoustic_energy=None,
            acoustic_rate=None,
            expected_concept="AFFECT_SORROW",
        ),
        # A. Single-modality grounding: Acoustic only
        MultimodalSample(
            sample_id="SM_AC_01",
            scenario_type="single_modality_acoustic",
            description="High pitch, high jitter, high energy, rapid speech -> PROSODY_AGITATED",
            pad=None,
            energy=None,
            cognitive_load=None,
            acoustic_f0=275.0,
            acoustic_jitter=0.048,
            acoustic_energy=0.88,
            acoustic_rate=6.5,
            expected_concept="PROSODY_AGITATED",
        ),
        MultimodalSample(
            sample_id="SM_AC_02",
            scenario_type="single_modality_acoustic",
            description="Low pitch, low jitter, low energy, calm cadence -> PROSODY_CALM",
            pad=None,
            energy=None,
            cognitive_load=None,
            acoustic_f0=135.0,
            acoustic_jitter=0.007,
            acoustic_energy=0.22,
            acoustic_rate=3.0,
            expected_concept="PROSODY_CALM",
        ),
        # B. Multimodal convergence: Synchronous matching signals
        MultimodalSample(
            sample_id="CONV_01",
            scenario_type="multimodal_convergence",
            description="Resting positive valence + soft warm acoustic prosody -> RELATIONAL_PHILIA",
            pad=(0.30, -0.05, 0.10),
            energy=0.70,
            cognitive_load=0.15,
            acoustic_f0=160.0,
            acoustic_jitter=0.010,
            acoustic_energy=0.32,
            acoustic_rate=3.4,
            expected_concept="RELATIONAL_PHILIA",
        ),
        MultimodalSample(
            sample_id="CONV_02",
            scenario_type="multimodal_convergence",
            description="Negative valence + high arousal + sharp acoustic spikes -> STATE_ALARM",
            pad=(-0.60, 0.85, -0.15),
            energy=0.90,
            cognitive_load=0.80,
            acoustic_f0=320.0,
            acoustic_jitter=0.055,
            acoustic_energy=0.92,
            acoustic_rate=7.0,
            expected_concept="STATE_ALARM",
        ),
        # C. Temporal continuity: 10-step ODE limbic trajectory
        MultimodalSample(
            sample_id="TEMP_01",
            scenario_type="temporal_continuity",
            description="Resting attractor -> Excitation spike -> Smooth homeostatic return",
            pad=None,
            energy=None,
            cognitive_load=None,
            acoustic_f0=None,
            acoustic_jitter=None,
            acoustic_energy=None,
            acoustic_rate=None,
            temporal_trajectory=[
                # Step 0-2: Resting Philia state
                {"t": 0.0, "P": 0.25, "A": -0.05, "D": 0.05, "concept": "RELATIONAL_PHILIA"},
                {"t": 0.2, "P": 0.25, "A": -0.05, "D": 0.05, "concept": "RELATIONAL_PHILIA"},
                {"t": 0.4, "P": 0.28, "A": -0.02, "D": 0.06, "concept": "RELATIONAL_PHILIA"},
                # Step 3-5: Stimulus onset -> Excitation
                {"t": 0.6, "P": 0.55, "A": 0.45, "D": 0.30, "concept": "AFFECT_JOY"},
                {"t": 0.8, "P": 0.70, "A": 0.65, "D": 0.40, "concept": "AFFECT_JOY"},
                {"t": 1.0, "P": 0.65, "A": 0.50, "D": 0.35, "concept": "AFFECT_JOY"},
                # Step 6-9: ODE exponential relaxation back to resting attractor
                {"t": 1.2, "P": 0.45, "A": 0.25, "D": 0.20, "concept": "AFFECT_JOY"},
                {"t": 1.4, "P": 0.35, "A": 0.10, "D": 0.12, "concept": "RELATIONAL_PHILIA"},
                {"t": 1.6, "P": 0.28, "A": 0.00, "D": 0.08, "concept": "RELATIONAL_PHILIA"},
                {"t": 1.8, "P": 0.25, "A": -0.04, "D": 0.05, "concept": "RELATIONAL_PHILIA"},
            ],
            expected_concept="TEMPORAL_SMOOTH_TRAJECTORY",
        ),
        # D. Conflicting evidence: Acoustic high arousal vs PAD low arousal
        MultimodalSample(
            sample_id="CONF_01",
            scenario_type="conflicting_evidence",
            description="Acoustic scream (A=+0.85) vs Limbic calm (A=-0.35) -> EVIDENCE_CONFLICT",
            pad=(0.20, -0.35, 0.00),
            energy=0.60,
            cognitive_load=0.30,
            acoustic_f0=310.0,
            acoustic_jitter=0.062,
            acoustic_energy=0.95,
            acoustic_rate=7.2,
            expected_concept="EVIDENCE_CONFLICT",
            expected_conflict=True,
            expected_uncertainty=0.85,
        ),
        # E. Missing modality: Acoustic dropout
        MultimodalSample(
            sample_id="DROP_01",
            scenario_type="missing_modality",
            description="Acoustic stream unavailable (None), PAD intact -> Graceful single-stream grounding",
            pad=(0.50, 0.20, 0.20),
            energy=0.75,
            cognitive_load=0.25,
            acoustic_f0=None,
            acoustic_jitter=None,
            acoustic_energy=None,
            acoustic_rate=None,
            expected_concept="AFFECT_SERENE",
        ),
        # F. Perturbation / Noise: Gaussian jitter applied to stable PAD
        MultimodalSample(
            sample_id="PERT_01",
            scenario_type="perturbation_robustness",
            description="Target PAD=(0.70, 0.35, 0.30) with sigma=0.08 noise -> Retains AFFECT_JOY",
            pad=(0.74, 0.38, 0.27),  # Perturbed within deadband
            energy=0.78,
            cognitive_load=0.22,
            acoustic_f0=185.0,
            acoustic_jitter=0.015,
            acoustic_energy=0.45,
            acoustic_rate=4.2,
            expected_concept="AFFECT_JOY",
        ),
        # G. Boundary oscillation test: Sinusoidal perturbation near threshold
        MultimodalSample(
            sample_id="OSC_01",
            scenario_type="boundary_oscillation",
            description="10-step oscillation (+/- 0.05) near threshold. Deadband hysteresis must yield DFR=0.0%",
            pad=None,
            energy=None,
            cognitive_load=None,
            acoustic_f0=None,
            acoustic_jitter=None,
            acoustic_energy=None,
            acoustic_rate=None,
            temporal_trajectory=[
                {"t": step * 0.1, "P": 0.45 + 0.04 * math.sin(step * 1.5), "A": 0.20, "D": 0.10}
                for step in range(10)
            ],
            expected_concept="STABLE_DEADBAND_RETENTION",
        ),
        # H. Semantically unrelated simultaneous signals
        MultimodalSample(
            sample_id="UNRELATED_01",
            scenario_type="unrelated_signals",
            description="Neutral resting limbic state + constant environmental background hum -> No spurious fusion",
            pad=(0.25, -0.05, 0.05),
            energy=0.80,
            cognitive_load=0.10,
            acoustic_f0=60.0,   # 60 Hz electrical mains hum (non-speech)
            acoustic_jitter=0.001,
            acoustic_energy=0.15,
            acoustic_rate=0.0,
            expected_concept="ENVIRONMENTAL_AMBIENCE_ISOLATION",
        ),
    ]

    return {
        "benchmark": "Phase23D_EXP06_Multimodal_Grounding",
        "description": "Deterministic continuous multimodal corpus for token-free grounding and embodiment.",
        "sample_count": len(samples),
        "samples": [s.__dict__ for s in samples],
    }
