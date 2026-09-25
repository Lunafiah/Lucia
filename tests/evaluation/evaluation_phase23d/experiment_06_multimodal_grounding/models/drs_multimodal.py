"""DRS-Graph Multimodal Grounding Engine (Control Candidate).

Features:
- Discourse box condition universe for multimodal sensory features
- Modal condition evaluation for conflict and uncertainty
- Token-Free Embodiment coupling
"""

from __future__ import annotations

from typing import Any, Dict, List, Optional, Tuple

from .grounding_encoder import extract_acoustic_arousal, map_embodiment_parameters


class DRSMultimodalEngine:
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

        # 2. Conflict condition
        conflict_detected = False
        uncertainty = 0.0
        if pad is not None and acoustic_arousal is not None:
            if abs(acoustic_arousal - pad[1]) > 0.60:
                conflict_detected = True
                uncertainty = round(abs(acoustic_arousal - pad[1]), 4)

        if conflict_detected:
            concept = "EVIDENCE_CONFLICT"
            v, a = pad[0], (pad[1] + acoustic_arousal) / 2.0
        elif pad is not None:
            p, a, d = pad
            v = p
            if p > 0.40 and a > 0.20:
                concept = "AFFECT_JOY"
            elif p < -0.40 and a < 0.0:
                concept = "AFFECT_SORROW"
            elif p < -0.30 and a > 0.40:
                concept = "STATE_ALARM"
            elif p > 0.20 and a < 0.15:
                concept = "RELATIONAL_PHILIA"
            elif p > 0.35 and 0.0 <= a <= 0.30:
                concept = "AFFECT_SERENE"
            else:
                concept = "RELATIONAL_PHILIA"
        elif acoustic_arousal is not None:
            v, a = 0.0, acoustic_arousal
            if acoustic_arousal > 0.40:
                concept = "PROSODY_AGITATED"
            else:
                concept = "PROSODY_CALM"
        else:
            concept = "RELATIONAL_PHILIA"
            v, a = 0.25, -0.05

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
