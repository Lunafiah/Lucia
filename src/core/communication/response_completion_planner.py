"""
src/core/communication/response_completion_planner.py

Response Completion Planner for P23-D Adaptive Generation Headroom Architecture.
Preserves the architectural distinction:
    ResponseDepth ≠ CompletionCapacity

- ResponseDepth (HOW MUCH PRESENCE):
  Language-neutral, communicative stance (MINIMAL, SHORT, MEDIUM, DEEP).
- CompletionCapacity (GENERATION HEADROOM):
  Language-calibrated, epistemic-bounded token capacity required to conclude
  the utterance cleanly without mid-sentence truncation or excessive runaway space.

Key Guarantees:
1. Deterministic & bounded: Pure functional evaluation, zero side-effects.
2. Epistemically constrained: UNKNOWN produces tightly bounded capacity;
   capacity scales with verified facet coverage, never raw proposition counts.
3. Language-aware: Empirically calibrated density profile (EN, VI, JA) without
   freezing benchmarks into rigid invariants.
4. Continuation-preserving: Active pending obligations preserve semantic workload
   across turns even if continuation cues contain no technical keywords.
5. Context-headroom aware: Capacity is strictly clamped by context window limits.
6. Somatic modulation: Affect/homeostasis modulates expression capacity;
   it does not alter grounded truth.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
import math
from typing import Any, Dict, List, Optional, Sequence, Set, Tuple

from src.core.communication.communication_state import (
    ResponseDepth,
    ResponseShape,
    ShapeTopology,
)
from src.core.models import SomaticMarkers


@dataclass(frozen=True)
class LanguageDensityProfile:
    """
    Empirically-calibrated, bounded language density profile.
    Translates language-neutral semantic units (words / concept clauses)
    into expected subword tokens under BPE tokenization.
    """
    language: str
    tokens_per_word_conversational: float
    tokens_per_word_technical: float
    tokens_per_char_ideographic: float
    min_sentence_tokens: int
    avg_sentence_tokens: int
    framing_overhead_tokens: int
    density_multiplier: float  # Relative expansion multiplier vs standard English baseline


# Calibration registry based on empirical BPE measurements (LFM2.5-1.2B-Instruct)
DEFAULT_LANGUAGE_DENSITY_PROFILES: Dict[str, LanguageDensityProfile] = {
    "en": LanguageDensityProfile(
        language="en",
        tokens_per_word_conversational=1.30,
        tokens_per_word_technical=1.65,
        tokens_per_char_ideographic=0.25,
        min_sentence_tokens=15,
        avg_sentence_tokens=25,
        framing_overhead_tokens=15,
        density_multiplier=1.00,
    ),
    "vi": LanguageDensityProfile(
        language="vi",
        tokens_per_word_conversational=2.90,
        tokens_per_word_technical=3.25,
        tokens_per_char_ideographic=0.68,
        min_sentence_tokens=35,
        avg_sentence_tokens=65,
        framing_overhead_tokens=35,
        density_multiplier=2.60,
    ),
    "ja": LanguageDensityProfile(
        language="ja",
        tokens_per_word_conversational=2.00,
        tokens_per_word_technical=2.40,
        tokens_per_char_ideographic=0.70,
        min_sentence_tokens=25,
        avg_sentence_tokens=45,
        framing_overhead_tokens=25,
        density_multiplier=1.60,
    ),
}


@dataclass(frozen=True)
class CompletionPlan:
    """Deterministic output of ResponseCompletionPlanner."""
    completion_capacity: int  # Authoritative max_tokens_budget for LLM generation
    recommended_max_sentences: Optional[int] = None
    diagnostic_metadata: Dict[str, Any] = field(default_factory=dict)


class ResponseCompletionPlanner:
    """
    Authoritative communicative realization capacity planner.
    Calculates legitimate generation headroom without reverting to a static
    ResponseDepth -> fixed max_tokens mapping.
    """

    def __init__(
        self,
        density_profiles: Optional[Dict[str, LanguageDensityProfile]] = None,
        default_safety_headroom: int = 64,
    ) -> None:
        self._density_profiles = density_profiles or DEFAULT_LANGUAGE_DENSITY_PROFILES
        self._safety_headroom = default_safety_headroom

    def get_density_profile(self, language: Optional[str]) -> LanguageDensityProfile:
        lang = (language or "en").lower().strip()
        return self._density_profiles.get(lang, self._density_profiles["en"])

    def plan(
        self,
        *,
        epistemic_status: Any,
        available_facets: int = 0,
        required_facets: int = 0,
        response_shape: Optional[ResponseShape] = None,
        response_depth: ResponseDepth = ResponseDepth.SHORT,
        conversational_obligation: Optional[str] = None,
        target_language: str = "en",
        context_headroom: Optional[int] = None,
        somatic_markers: Optional[SomaticMarkers] = None,
        focus_argument: Optional[str] = None,
        is_continuation: bool = False,
    ) -> CompletionPlan:
        """
        Calculates the authoritative completion capacity (max_tokens_budget).
        """
        profile = self.get_density_profile(target_language)
        ep_str = (
            epistemic_status.value
            if hasattr(epistemic_status, "value")
            else str(epistemic_status or "").upper()
        )
        ob_str = str(conversational_obligation or "").strip()
        depth = response_depth if isinstance(response_depth, ResponseDepth) else ResponseDepth.SHORT
        shape = response_shape or ResponseShape()

        meta: Dict[str, Any] = {
            "target_language": profile.language,
            "epistemic_status": ep_str,
            "available_facets": available_facets,
            "required_facets": required_facets,
            "response_depth": depth.value,
            "conversational_obligation": ob_str,
            "is_continuation": is_continuation,
        }

        # ------------------------------------------------------------------
        # 1. Epistemic Boundary Check: UNKNOWN is strictly bounded
        # ------------------------------------------------------------------
        if ep_str in ("UNKNOWN", "AMBIGUOUS", "REFUSE"):
            # Refusal or honest boundary statement: 1-2 concise sentences
            # English ~45-55 tokens, Vietnamese ~90-125 tokens, Japanese ~65-90 tokens
            base_capacity = int(profile.avg_sentence_tokens * 1.5 + profile.framing_overhead_tokens)
            base_capacity = max(35, min(140 if profile.language == "vi" else 65, base_capacity))
            recommended_sentences = 2
            meta["branch"] = "UNKNOWN_BOUNDED"
            capacity = self._apply_somatic_and_headroom(
                base_capacity, somatic_markers, context_headroom, meta
            )
            return CompletionPlan(
                completion_capacity=capacity,
                recommended_max_sentences=recommended_sentences,
                diagnostic_metadata=meta,
            )

        # ------------------------------------------------------------------
        # 2. Presence & Minimal Utterances
        # ------------------------------------------------------------------
        if (
            ob_str in ("MINIMAL_PRESENCE_CALL", "ACKNOWLEDGE_REACTION_ONLY")
            or shape.topology == ShapeTopology.MINIMAL_PING
            or depth == ResponseDepth.MINIMAL
        ):
            base_capacity = int(profile.min_sentence_tokens + profile.framing_overhead_tokens)
            # VI: 35 + 35 = 70; EN: 15 + 15 = 30
            base_capacity = max(25, min(80 if profile.language == "vi" else 45, base_capacity))
            recommended_sentences = 1
            meta["branch"] = "MINIMAL_PRESENCE"
            capacity = self._apply_somatic_and_headroom(
                base_capacity, somatic_markers, context_headroom, meta
            )
            return CompletionPlan(
                completion_capacity=capacity,
                recommended_max_sentences=recommended_sentences,
                diagnostic_metadata=meta,
            )

        # ------------------------------------------------------------------
        # 3. Direct Bounded Answers (Activity, Greeting, Simple Q&A)
        # ------------------------------------------------------------------
        if ob_str in ("ANSWER_ACTIVITY", "GREET_BACK", "MUTUAL_ENCOUNTER_ACKNOWLEDGMENT"):
            # 1-2 bounded sentences without unsolicited expansion
            base_capacity = int(profile.avg_sentence_tokens * 1.6 + profile.framing_overhead_tokens)
            # VI: 65 * 1.6 + 35 = 139; EN: 25 * 1.6 + 15 = 55
            base_capacity = max(40, min(160 if profile.language == "vi" else 75, base_capacity))
            recommended_sentences = 2
            meta["branch"] = "BOUNDED_ACTIVITY_OR_GREETING"
            capacity = self._apply_somatic_and_headroom(
                base_capacity, somatic_markers, context_headroom, meta
            )
            return CompletionPlan(
                completion_capacity=capacity,
                recommended_max_sentences=recommended_sentences,
                diagnostic_metadata=meta,
            )

        # ------------------------------------------------------------------
        # 4. Conceptual Explanation / Substantive Inquiry Workload
        # ------------------------------------------------------------------
        is_concept_explanation = (
            ob_str == "FULFILL_CONCEPT_EXPLANATION"
            or shape.topology == ShapeTopology.STRUCTURED_EXPLANATION
            or focus_argument is not None
            or is_continuation
        )

        if is_concept_explanation:
            # Effective facets: determine workload from verified coverage
            effective_facets = max(1, available_facets)
            if focus_argument in ("ent:lucia_architecture", "lucia_architecture"):
                # Full architecture covers 5 subsystems
                effective_facets = max(available_facets, 5 if available_facets >= 3 else available_facets)

            # Check PARTIAL epistemic status
            if ep_str == "PARTIAL":
                # Bounded to supported facets (1-2) + boundary disclaimer
                # VI: ~260-320 tokens; EN: ~110-150 tokens
                facet_budget = effective_facets * profile.avg_sentence_tokens * 1.1
                base_capacity = int(facet_budget + profile.avg_sentence_tokens + profile.framing_overhead_tokens)
                base_capacity = min(360 if profile.language == "vi" else 170, base_capacity)
                recommended_sentences = min(4, effective_facets + 2)
                meta["branch"] = "PARTIAL_CONCEPT_EXPLANATION"
                capacity = self._apply_somatic_and_headroom(
                    base_capacity, somatic_markers, context_headroom, meta
                )
                return CompletionPlan(
                    completion_capacity=capacity,
                    recommended_max_sentences=recommended_sentences,
                    diagnostic_metadata=meta,
                )

            # KNOWN / FACT conceptual explanation
            # Differentiate by depth and facet count
            if depth == ResponseDepth.SHORT:
                # 2-3 sentences highlighting main points
                base_capacity = int(profile.avg_sentence_tokens * 2.5 + profile.framing_overhead_tokens)
                recommended_sentences = 3
                meta["branch"] = "SHORT_CONCEPT_EXPLANATION"
            elif depth == ResponseDepth.MEDIUM:
                # Single structured paragraph covering 1-3 facets
                facet_factor = min(3, effective_facets)
                base_capacity = int(
                    profile.avg_sentence_tokens * 1.6 * facet_factor + profile.framing_overhead_tokens + 40
                )
                recommended_sentences = 4
                meta["branch"] = "MEDIUM_CONCEPT_EXPLANATION"
            else:
                # ResponseDepth.DEEP
                # Multi-facet comprehensive explanation
                if effective_facets >= 3:
                    # Multi-facet (e.g. 5-layer Whole Brain Architecture)
                    # VI: ~700-800 tokens; EN: ~360-440 tokens
                    sentences_needed = effective_facets * 1.5  # ~7.5 sentences for 5 facets
                    tech_sentence_tokens = int(profile.avg_sentence_tokens * 1.35)
                    base_capacity = int(
                        sentences_needed * tech_sentence_tokens
                        + profile.framing_overhead_tokens
                        + (120 if profile.language == "vi" else 90)  # synthesis headroom
                    )
                    recommended_sentences = int(sentences_needed)
                    meta["branch"] = "DEEP_MULTI_FACET_EXPLANATION"
                else:
                    # Single-facet deep explanation (DEEP + low workload)
                    # Does NOT receive multi-facet 700+ budget!
                    # VI: ~380-450 tokens; EN: ~180-230 tokens
                    sentences_needed = 4
                    tech_sentence_tokens = int(profile.avg_sentence_tokens * 1.35)
                    base_capacity = int(
                        sentences_needed * tech_sentence_tokens
                        + profile.framing_overhead_tokens
                        + (60 if profile.language == "vi" else 40)
                    )
                    recommended_sentences = sentences_needed
                    meta["branch"] = "DEEP_SINGLE_FACET_EXPLANATION"

            capacity = self._apply_somatic_and_headroom(
                base_capacity, somatic_markers, context_headroom, meta
            )
            return CompletionPlan(
                completion_capacity=capacity,
                recommended_max_sentences=recommended_sentences,
                diagnostic_metadata=meta,
            )

        # ------------------------------------------------------------------
        # 5. General Conversational Fallback by ResponseDepth
        # ------------------------------------------------------------------
        depth_word_estimates = {
            ResponseDepth.MINIMAL: 15,
            ResponseDepth.SHORT: 35,
            ResponseDepth.MEDIUM: 70,
            ResponseDepth.DEEP: 130,
        }
        word_count = depth_word_estimates.get(depth, 35)
        raw_tokens = word_count * profile.tokens_per_word_conversational + profile.framing_overhead_tokens
        base_capacity = int(raw_tokens)
        recommended_sentences = {
            ResponseDepth.MINIMAL: 1,
            ResponseDepth.SHORT: 2,
            ResponseDepth.MEDIUM: 4,
            ResponseDepth.DEEP: 6,
        }.get(depth, 2)
        meta["branch"] = f"GENERAL_{depth.value.upper()}"

        capacity = self._apply_somatic_and_headroom(
            base_capacity, somatic_markers, context_headroom, meta
        )
        return CompletionPlan(
            completion_capacity=capacity,
            recommended_max_sentences=recommended_sentences,
            diagnostic_metadata=meta,
        )

    def _apply_somatic_and_headroom(
        self,
        base_capacity: int,
        somatic: Optional[SomaticMarkers],
        context_headroom: Optional[int],
        meta: Dict[str, Any],
    ) -> int:
        capacity = float(base_capacity)

        # 1. Somatic Modulation
        if somatic is not None:
            # Low energy conservation
            if somatic.energy <= 0.10:
                # Acute emergency exhaustion: hard ceiling
                capacity = min(capacity, 120.0 if meta.get("target_language") == "vi" else 65.0)
                meta["somatic_acute_floor_applied"] = True
            elif somatic.energy <= 0.20:
                capacity *= 0.75
                meta["somatic_energy_attenuation"] = 0.75

            # High cognitive load / tension
            if somatic.cognitive_load >= 0.75:
                capacity *= 0.85
                meta["somatic_load_attenuation"] = 0.85

        final_capacity = int(math.ceil(capacity))

        # 2. Context Headroom Clamping
        if context_headroom is not None:
            safe_headroom = max(35, context_headroom - self._safety_headroom)
            if final_capacity > safe_headroom:
                meta["headroom_clamped"] = True
                meta["unclamped_capacity"] = final_capacity
                meta["safe_headroom"] = safe_headroom
                final_capacity = safe_headroom

        meta["final_capacity"] = final_capacity
        return final_capacity
