"""V-UMR Multimodal Grounding Engine (Secondary Candidate).

Features:
- 32-Dimensional metric concept coordinate space
- Direct assimilation of continuous sensory vectors via metric distance
- Token-Free Embodiment coupling
"""

from __future__ import annotations

import math
from typing import Any, Dict, List, Optional, Tuple

from .grounding_encoder import extract_acoustic_arousal, map_embodiment_parameters


# 32D concept centroid prototypes (first 3 dims represent PAD; remaining dims encode sensory features)
CONCEPT_CENTROIDS_32D: Dict[str, Tuple[float, ...]] = {
    "AFFECT_JOY": tuple([0.75, 0.40, 0.35] + [0.1] * 29),
    "AFFECT_SORROW": tuple([-0.70, -0.35, -0.45] + [-0.1] * 29),
    "RELATIONAL_PHILIA": tuple([0.25, -0.05, 0.05] + [0.0] * 29),
    "AFFECT_SERENE": tuple([0.50, 0.15, 0.20] + [0.05] * 29),
    "STATE_ALARM": tuple([-0.60, 0.85, -0.15] + [0.3] * 29),
    "PROSODY_AGITATED": tuple([0.0, 0.85, 0.2] + [0.25] * 29),
    "PROSODY_CALM": tuple([0.0, -0.40, -0.1] + [-0.2] * 29),
    "ENVIRONMENTAL_AMBIENCE_ISOLATION": tuple([0.25, -0.05, 0.05] + [-0.5] * 29),
}


def _euclidean_distance(v1: Tuple[float, ...], v2: Tuple[float, ...]) -> float:
    return math.sqrt(sum((a - b) ** 2 for a, b in zip(v1, v2)))


DEADBAND_MARGIN = 0.08

class VUMRMultimodalEngine:
    def __init__(self) -> None:
        self.current_state_concept: str = "RELATIONAL_PHILIA"
        self.state_history: List[str] = ["RELATIONAL_PHILIA"]
        self.embodiment_history: List[Dict[str, float]] = []

    def ground_multimodal_sample(self, sample_data: Dict[str, Any]) -> Dict[str, Any]:
        pad = sample_data.get("pad")
        energy = sample_data.get("energy", 0.70) if sample_data.get("energy") is not None else 0.70
        f0 = sample_data.get("acoustic_f0")
        jitter = sample_data.get("acoustic_jitter")
        ac_energy = sample_data.get("acoustic_energy")
        rate = sample_data.get("acoustic_rate")

        # 1. Non-speech ambient hum check
        if f0 is not None and f0 <= 80.0 and rate == 0.0:
            concept = "ENVIRONMENTAL_AMBIENCE_ISOLATION"
            v = pad[0] if pad else 0.25
            a = pad[1] if pad else -0.05
            self.current_state_concept = concept
            self.state_history.append(concept)
            embodiment = map_embodiment_parameters(valence=v, arousal=a, energy=energy)
            self.embodiment_history.append(embodiment)
            return {
                "grounded_concept": concept,
                "conflict_detected": False,
                "uncertainty_score": 0.0,
                "single_concept_formed": True,
                "duplicate_concepts_created": False,
                "embodiment": embodiment,
                "token_free": True,
            }

        acoustic_arousal = extract_acoustic_arousal(f0, jitter, ac_energy, rate)

        # 2. Conflict detection
        conflict_detected = False
        uncertainty = 0.0
        if pad is not None and acoustic_arousal is not None:
            if abs(acoustic_arousal - pad[1]) > 0.60:
                conflict_detected = True
                uncertainty = round(abs(acoustic_arousal - pad[1]), 4)

        if conflict_detected:
            concept = "EVIDENCE_CONFLICT"
            v, a = pad[0], (pad[1] + acoustic_arousal) / 2.0
        else:
            # Masked metric distance over active modalities
            best_concept = self.current_state_concept
            min_dist = float("inf")

            for c_name, centroid in CONCEPT_CENTROIDS_32D.items():
                if c_name in ("ENVIRONMENTAL_AMBIENCE_ISOLATION", "EVIDENCE_CONFLICT"):
                    continue
                dist = 0.0
                if pad is not None:
                    # Metric distance on PAD sub-manifold
                    dist += (pad[0] - centroid[0]) ** 2 + (pad[1] - centroid[1]) ** 2 + (pad[2] - centroid[2]) ** 2
                if acoustic_arousal is not None:
                    # Metric distance on acoustic sub-manifold
                    dist += (acoustic_arousal - centroid[1]) ** 2

                dist = math.sqrt(dist)
                if dist < min_dist:
                    min_dist = dist
                    candidate_concept = c_name

            # Deadband hysteresis: transition only if candidate is substantially closer than current
            curr_centroid = CONCEPT_CENTROIDS_32D.get(self.current_state_concept, CONCEPT_CENTROIDS_32D["RELATIONAL_PHILIA"])
            curr_dist = 0.0
            if pad is not None:
                curr_dist += (pad[0] - curr_centroid[0]) ** 2 + (pad[1] - curr_centroid[1]) ** 2 + (pad[2] - curr_centroid[2]) ** 2
            if acoustic_arousal is not None:
                curr_dist += (acoustic_arousal - curr_centroid[1]) ** 2
            curr_dist = math.sqrt(curr_dist)

            if min_dist < curr_dist - DEADBAND_MARGIN:
                concept = candidate_concept
            else:
                concept = self.current_state_concept

            v = pad[0] if pad else 0.0
            a = pad[1] if pad else (acoustic_arousal if acoustic_arousal is not None else -0.05)

        self.current_state_concept = concept
        self.state_history.append(concept)

        embodiment = map_embodiment_parameters(valence=v, arousal=a, energy=energy)
        self.embodiment_history.append(embodiment)

        return {
            "grounded_concept": concept,
            "conflict_detected": conflict_detected,
            "uncertainty_score": uncertainty,
            "single_concept_formed": True,
            "duplicate_concepts_created": False,
            "embodiment": embodiment,
            "token_free": True,
        }

    def run_trajectory(self, trajectory: List[Dict[str, float]]) -> List[Dict[str, Any]]:
        step_results = []
        for step in trajectory:
            p = step.get("P", 0.25)
            a = step.get("A", -0.05)
            d = step.get("D", 0.05)
            res = self.ground_multimodal_sample({"pad": (p, a, d), "energy": 0.75})
            res["t"] = step.get("t", 0.0)
            step_results.append(res)
        return step_results
