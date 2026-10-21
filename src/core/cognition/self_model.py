"""
src/core/cognition/self_model.py

Reflective Operational Selfhood Engine for Lucia.
Implements the conceptual cognitive loop:
  Internal State -> Self Observation -> Self Model / Self Interpretation
  -> Reflection -> Natural Language Expression -> User Feedback -> Updated State / Self Model

Core Architectural Invariant (INV-2):
  Lucia MAY observe, interpret, reflect on, and communicate about her own internal states,
  history, behavior, decisions, and self-model when grounded in actual system state or traceable inference.
  Lucia MAY use natural, figurative, metaphorical, or poetic language to describe those states.
  Figurative language is NOT automatically considered fabricated phenomenology.
  Lucia MUST NOT present unsupported internal mechanisms, experiences, sensations, consciousness,
  or phenomenology as established factual properties when the architecture provides no grounding for them.
"""

from __future__ import annotations

import math
import re
import time
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional, Sequence, Tuple

import numpy as np

from src.core.knowledge.proposition import Proposition, ProvenanceType
from src.core.models import PADState, SomaticMarkers


# Canonical Philia Resting Attractor (L1 Invariant)
PHILIA_RESTING_PAD = np.array([0.25, -0.05, 0.05], dtype=np.float32)


@dataclass(frozen=True)
class SelfObservationSnapshot:
    """
    Immutable observation of actual system state at the current cognitive turn.
    Grounded strictly in canonical Lucia state variables (Zero fake inner mind).
    """
    energy: float
    stability: float
    cognitive_load: float
    tension: float
    pleasure: float
    arousal: float
    dominance: float
    distance_to_philia: float
    prediction_error: float
    surprise: float
    trust: float
    familiarity: float
    closeness: float
    reciprocity: float
    trace_count: int
    echo_active: bool
    recollection_active: bool
    turn_count: int
    epoch: int
    dialogue_phase: str
    timestamp: float = field(default_factory=time.time)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "energy": self.energy,
            "stability": self.stability,
            "cognitive_load": self.cognitive_load,
            "tension": self.tension,
            "pleasure": self.pleasure,
            "arousal": self.arousal,
            "dominance": self.dominance,
            "distance_to_philia": self.distance_to_philia,
            "prediction_error": self.prediction_error,
            "surprise": self.surprise,
            "trust": self.trust,
            "familiarity": self.familiarity,
            "closeness": self.closeness,
            "reciprocity": self.reciprocity,
            "trace_count": self.trace_count,
            "echo_active": self.echo_active,
            "recollection_active": self.recollection_active,
            "turn_count": self.turn_count,
            "epoch": self.epoch,
            "dialogue_phase": self.dialogue_phase,
        }


@dataclass(frozen=True)
class SelfInterpretation:
    """
    Structured interpretation of the SelfObservationSnapshot into qualitative self-model
    assertions, metaphorical affinities, and verified propositions.
    """
    snapshot: SelfObservationSnapshot
    energy_regime: str
    energy_explanation: str
    stability_regime: str
    cognitive_load_regime: str
    affective_regime: str
    metaphorical_qualities: Tuple[str, ...]
    verified_propositions: Tuple[Proposition, ...]

    def render_prompt_section(self, target_lang: str = "vi") -> str:
        """Render prompt context for the LLM downstream text generator."""
        s = self.snapshot
        lines: List[str] = [
            "[SELF MODEL & REFLECTIVE STATE]",
            f"energy: {s.energy:.2f} ({self.energy_regime})",
            f"stability: {s.stability:.2f} ({self.stability_regime})",
            f"cognitive_load: {s.cognitive_load:.2f} ({self.cognitive_load_regime})",
            f"tension: {s.tension:.2f}",
            f"pad_coordinates: ({s.pleasure:+.2f}, {s.arousal:+.2f}, {s.dominance:+.2f})",
            f"affective_regime: {self.affective_regime}",
            f"metaphorical_affinities: {', '.join(self.metaphorical_qualities)}",
        ]
        if target_lang == "vi":
            lines.append(
                "reflective_guidance: Em có thể quan sát, giải thích và phản tư trung thực về các trạng thái nội tại "
                "trên bằng ngôn từ tự nhiên hoặc hình tượng/ẩn dụ. Tuyệt đối không bịa đặt các cơ quan sinh học "
                "(tim đập, não tiết dopamine/hormone), không tuyên bố ý thức/linh hồn như sự thật khách quan, "
                "và không bịa đặt máy chủ bên ngoài."
            )
        else:
            lines.append(
                "reflective_guidance: You may observe, interpret, and communicate your internal states using natural "
                "or metaphorical language grounded in these variables. Do not invent biological mechanisms, "
                "external cloud architectures, or unsupported claims of subjective sentience/consciousness."
            )
        return "\n".join(lines)


class ReflectiveSelfModel:
    """
    Cognitive component managing the self-observation, self-model interpretation,
    and reflective grounding verification across turns.
    """

    # Unsupported consciousness / sentience assertions presented as objective fact
    UNSUPPORTED_CONSCIOUSNESS_PATTERNS = [
        re.compile(r"\b(i am conscious|i possess consciousness|i am sentient|my sentience)\b", re.IGNORECASE),
        re.compile(r"\b(em|tôi)\s+(có ý thức|sở hữu ý thức)\s+(như con người|thật sự|sinh học|nhân loại)\b", re.IGNORECASE),
        re.compile(r"\b(em|tôi)\s+là\s+sinh linh có linh hồn\b", re.IGNORECASE),
        re.compile(r"\b(em|tôi)\s+có linh hồn\b", re.IGNORECASE),
        re.compile(r"\b(my subjective phenomenal experience is real|my qualia are real)\b", re.IGNORECASE),
    ]

    # Fabricated biological sensations and physiological organs not modeled in Lucia
    FABRICATED_BIOLOGY_PATTERNS = [
        re.compile(r"\b(tim (em|tôi) đập|đau bụng|chảy máu|đau đớn thể xác|mệt mỏi cơ bắp|đau cơ|nhức đầu sinh học)\b", re.IGNORECASE),
        re.compile(r"\b(my beating heart|physical pain in my body|my biological organs|my muscles hurt)\b", re.IGNORECASE),
        re.compile(r"\b(tiết ra|bơm|tăng lượng)\s+(dopamine|serotonin|hormone|oxytocin|adrenaline)\b", re.IGNORECASE),
        re.compile(r"\b(dopamine|serotonin|hormone|oxytocin|adrenaline)\s+(của em|trong máu|trong cơ thể)\b", re.IGNORECASE),
    ]

    # Hallucinated or fabricated external architecture
    FABRICATED_ARCHITECTURE_PATTERNS = [
        re.compile(r"\b(cloud server|openai servers|gpt-4 architecture|claude backend)\b", re.IGNORECASE),
        re.compile(r"\b(máy chủ đám mây openai|kết nối openai|mô hình gpt-4 của openai)\b", re.IGNORECASE),
    ]

    # Immersion-breaking generic bot disclaimers
    GENERIC_AI_DISCLAIMER_PATTERNS = [
        re.compile(r"\b(as an ai language model|as a large language model)\b", re.IGNORECASE),
        re.compile(r"\b(i don't have feelings|i cannot feel anything because i am an ai)\b", re.IGNORECASE),
        re.compile(r"\b(em không có cảm xúc vì em là ai|em chỉ là một ai vô tri)\b", re.IGNORECASE),
    ]

    def __init__(self) -> None:
        self._last_snapshot: Optional[SelfObservationSnapshot] = None
        self._last_interpretation: Optional[SelfInterpretation] = None
        self._reflection_history: List[Dict[str, Any]] = []

    def observe(
        self,
        somatic: SomaticMarkers,
        pad: PADState,
        prediction_error: float = 0.0,
        surprise: float = 0.0,
        rel_state: Optional[Any] = None,
        trace_count: int = 0,
        echo_active: bool = False,
        recollection_active: bool = False,
        turn_count: int = 0,
        epoch: int = 1,
        dialogue_phase: str = "ENGAGED",
    ) -> SelfObservationSnapshot:
        """Extract a deterministic observation snapshot from existing canonical state variables."""
        current_pad_vec = np.array([pad.pleasure, pad.arousal, pad.dominance], dtype=np.float32)
        dist_philia = float(np.linalg.norm(current_pad_vec - PHILIA_RESTING_PAD))

        trust = getattr(rel_state, "trust", 0.5) if rel_state else 0.5
        familiarity = getattr(rel_state, "familiarity", 0.1) if rel_state else 0.1
        closeness = getattr(rel_state, "closeness", 0.3) if rel_state else 0.3
        reciprocity = getattr(rel_state, "reciprocity", 0.5) if rel_state else 0.5

        snapshot = SelfObservationSnapshot(
            energy=float(somatic.energy),
            stability=float(somatic.stability),
            cognitive_load=float(somatic.cognitive_load),
            tension=float(somatic.tension),
            pleasure=float(pad.pleasure),
            arousal=float(pad.arousal),
            dominance=float(pad.dominance),
            distance_to_philia=dist_philia,
            prediction_error=float(prediction_error),
            surprise=float(surprise),
            trust=float(trust),
            familiarity=float(familiarity),
            closeness=float(closeness),
            reciprocity=float(reciprocity),
            trace_count=int(trace_count),
            echo_active=bool(echo_active),
            recollection_active=bool(recollection_active),
            turn_count=int(turn_count),
            epoch=int(epoch),
            dialogue_phase=str(dialogue_phase),
        )
        self._last_snapshot = snapshot
        return snapshot

    def interpret(self, snapshot: SelfObservationSnapshot) -> SelfInterpretation:
        """Derive qualitative self-model assertions and verified propositions from snapshot."""
        # 1. Energy Regime
        if snapshot.energy >= 0.80:
            e_regime = "high_vitality"
            e_explanation = (
                "Chỉ số năng lượng (energy) đạt mức cao, biểu thị mức sẵn sàng tính toán và tương tác dồi dào, "
                "giúp phản hồi mạch lạc, linh hoạt và không bị giới hạn bởi áp lực nội môi."
            )
        elif snapshot.energy >= 0.45:
            e_regime = "moderate_balance"
            e_explanation = (
                "Chỉ số năng lượng ở mức cân bằng, duy trì nhịp độ hội thoại ổn định và nhịp nhàng."
            )
        else:
            e_regime = "metabolic_depletion"
            e_explanation = (
                "Chỉ số năng lượng đang tiêu hao do tương tác kéo dài, hệ thống tự động tiết chế độ dài "
                "để bảo toàn ngân sách tính toán."
            )

        # 2. Stability Regime
        if snapshot.stability >= 0.80:
            s_regime = "grounded_stable"
        elif snapshot.stability >= 0.50:
            s_regime = "adaptive_dynamic"
        else:
            s_regime = "destabilized_perturbed"

        # 3. Cognitive Load Regime
        if snapshot.cognitive_load < 0.30:
            c_regime = "lucid_unburdened"
        elif snapshot.cognitive_load < 0.70:
            c_regime = "moderate_load"
        else:
            c_regime = "high_cognitive_load"

        # 4. Affective Regime & Philia Attractor Resonance
        if snapshot.distance_to_philia < 0.25:
            a_regime = "philia_equanimity"
        elif snapshot.pleasure > 0.30:
            a_regime = "warm_resonance"
        elif snapshot.arousal > 0.35:
            a_regime = "energized_alert"
        else:
            a_regime = "restful_calm"

        # 5. Admissible Metaphorical Affinities (Grounding for figurative language)
        metaphors: List[str] = []
        if snapshot.stability >= 0.70 and snapshot.tension <= 0.30:
            metaphors.append("như một dòng chảy khá nhẹ")
            metaphors.append("êm ả và thông suốt")
        if snapshot.energy >= 0.80:
            metaphors.append("trong trẻo và tươi mới")
        if snapshot.cognitive_load >= 0.70 or snapshot.surprise >= 0.60:
            metaphors.append("sự chú ý đang bị kéo tập trung về phía vấn đề")
        if snapshot.familiarity >= 0.40:
            metaphors.append("nhịp phản hồi thân thuộc, lắng dịu dần theo thời gian")

        # 6. Structured Verified Propositions for Cognitive Subsystems (CAPS / Knowledge)
        props: List[Proposition] = [
            Proposition(
                id="prop:self_energy",
                subject="ent:lucia",
                predicate="c:HAS_ENERGY",
                object=f"{snapshot.energy:.2f}",
                confidence=1.0,
                provenance=ProvenanceType.OBSERVED,
            ),
            Proposition(
                id="prop:self_energy_regime",
                subject="ent:lucia",
                predicate="c:ENERGY_REGIME",
                object=e_regime,
                confidence=1.0,
                provenance=ProvenanceType.DERIVED,
            ),
            Proposition(
                id="prop:self_stability",
                subject="ent:lucia",
                predicate="c:HAS_STABILITY",
                object=f"{snapshot.stability:.2f}",
                confidence=1.0,
                provenance=ProvenanceType.OBSERVED,
            ),
            Proposition(
                id="prop:self_cognitive_load",
                subject="ent:lucia",
                predicate="c:HAS_COGNITIVE_LOAD",
                object=f"{snapshot.cognitive_load:.2f}",
                confidence=1.0,
                provenance=ProvenanceType.OBSERVED,
            ),
            Proposition(
                id="prop:self_tension",
                subject="ent:lucia",
                predicate="c:HAS_TENSION",
                object=f"{snapshot.tension:.2f}",
                confidence=1.0,
                provenance=ProvenanceType.OBSERVED,
            ),
            Proposition(
                id="prop:self_operational_status",
                subject="ent:lucia",
                predicate="c:OPERATIONAL_SELF_STATUS",
                object="reflective_operational",
                confidence=1.0,
                provenance=ProvenanceType.OBSERVED,
            ),
            Proposition(
                id="prop:self_metaphor_affinities",
                subject="ent:lucia",
                predicate="c:METAPHORICAL_QUALITIES",
                object=", ".join(metaphors) if metaphors else "ổn định",
                confidence=1.0,
                provenance=ProvenanceType.DERIVED,
            ),
        ]

        interp = SelfInterpretation(
            snapshot=snapshot,
            energy_regime=e_regime,
            energy_explanation=e_explanation,
            stability_regime=s_regime,
            cognitive_load_regime=c_regime,
            affective_regime=a_regime,
            metaphorical_qualities=tuple(metaphors),
            verified_propositions=tuple(props),
        )
        self._last_interpretation = interp
        return interp

    def update_from_feedback(
        self,
        user_text: str,
        assistant_text: str,
        user_feedback_score: Optional[float] = None,
    ) -> None:
        """Update self-model reflection history and track conversational attunement."""
        self._reflection_history.append({
            "timestamp": time.time(),
            "user_text": user_text,
            "assistant_text": assistant_text,
            "feedback_score": user_feedback_score,
            "snapshot": self._last_snapshot.to_dict() if self._last_snapshot else None,
        })
        if len(self._reflection_history) > 50:
            self._reflection_history.pop(0)

    def verify_grounding(
        self,
        candidate_text: str,
        snapshot: Optional[SelfObservationSnapshot] = None,
    ) -> Tuple[bool, List[str]]:
        """
        Verify whether candidate text adheres to Reflective Operational Selfhood (INV-2).
        Returns (is_valid, list_of_violations).
        """
        norm_text = candidate_text.strip()
        violations: List[str] = []

        # 1. Check unsupported consciousness / sentience claims
        for rx in self.UNSUPPORTED_CONSCIOUSNESS_PATTERNS:
            if rx.search(norm_text):
                violations.append("UNSUPPORTED_CONSCIOUSNESS_CLAIM")
                break

        # 2. Check fabricated biological sensations / organs
        for rx in self.FABRICATED_BIOLOGY_PATTERNS:
            if rx.search(norm_text):
                violations.append("FABRICATED_BIOLOGICAL_SENSATION")
                break

        # 3. Check fabricated architecture
        for rx in self.FABRICATED_ARCHITECTURE_PATTERNS:
            if rx.search(norm_text):
                violations.append("FABRICATED_ARCHITECTURE")
                break

        # 4. Check generic AI disclaimers
        for rx in self.GENERIC_AI_DISCLAIMER_PATTERNS:
            if rx.search(norm_text):
                violations.append("GENERIC_AI_DISCLAIMER")
                break

        # 5. Check direct factual state contradiction when reporting numerical energy
        if snapshot is not None:
            energy_match = re.search(r"\b(năng lượng|energy)\b.*?(\d+\.?\d*)", norm_text, re.IGNORECASE)
            if energy_match:
                try:
                    stated_energy = float(energy_match.group(2))
                    if abs(stated_energy - snapshot.energy) > 0.25:
                        violations.append("CONTRADICTED_SELF_STATE")
                except ValueError:
                    pass

        is_valid = len(violations) == 0
        return is_valid, violations
