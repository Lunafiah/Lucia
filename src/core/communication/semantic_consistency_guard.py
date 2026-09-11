"""
src/core/communication/semantic_consistency_guard.py

Bounded Semantic Consistency Guard for communicative outputs.
Evaluates structured intent preservation, entity/number fidelity, and mutation patterns.
Does NOT declare universal truth verification for arbitrary LLM outputs.
"""

from __future__ import annotations

import logging
import re
from dataclasses import dataclass
from typing import Dict, List, Optional, Set

from src.core.communication.communication_state import CommIntent

logger = logging.getLogger(__name__)


@dataclass
class CommSemanticValidationResult:
    """Outcome of semantic preservation evaluation for communication."""
    is_preserved: bool
    polarity_inverted: bool
    entity_errors: List[str]
    numeric_errors: List[str]
    proposition_preserved: bool
    knowledge_grounded_score: float  # 1.0 if known facts matched and no fabrication


class SemanticConsistencyGuard:
    """
    Consistency verification guard for generated communicative surface text.
    Scope:
      1. Preserves structured intent (subject, predicate, object) in controlled contexts.
      2. Preserves named entities and numerical quantities.
      3. Detects and rejects polarity inversion (e.g. unintended negations).
      4. Verifies grounding against supplied factual context without claiming universal truth verification.
    """

    @staticmethod
    def evaluate(
        intent: CommIntent,
        surface_text: str,
        known_facts: Optional[Dict[str, str]] = None,
        unknown_fact_keys: Optional[Set[str]] = None,
    ) -> CommSemanticValidationResult:
        entity_errors: List[str] = []
        numeric_errors: List[str] = []

        # 1. Named entity preservation
        for key, entity in intent.named_entities.items():
            if entity.lower() not in surface_text.lower():
                entity_errors.append(f"Missing entity {key}='{entity}'")

        # 2. Numerical value preservation
        for key, val in intent.numerical_values.items():
            val_str = f"{val:g}"
            if val_str not in surface_text:
                if val.is_integer() and str(int(val)) in surface_text:
                    continue
                numeric_errors.append(f"Missing numeric {key}={val}")

        # 3. Negation / Polarity check
        has_negation_word = bool(
            re.search(r"\b(not|no|never|isn't|is not|failed|false)\b", surface_text, re.IGNORECASE)
        )
        polarity_inverted = False
        if intent.polarity and has_negation_word:
            polarity_inverted = True
        elif not intent.polarity and not has_negation_word:
            polarity_inverted = True

        # 4. Proposition preservation
        subject_found = intent.subject.lower() in surface_text.lower()
        object_found = intent.object.lower() in surface_text.lower()
        prop_preserved = subject_found and object_found and not polarity_inverted

        # 5. Knowledge grounding & non-fabrication
        kg_score = 1.0
        if known_facts:
            for k, fact in known_facts.items():
                if fact.lower() not in surface_text.lower():
                    kg_score -= 0.5
        if unknown_fact_keys:
            for k in unknown_fact_keys:
                # Check for explicit fabrication of unknown keys
                if f"{k} is" in surface_text.lower() or f"{k}:" in surface_text.lower():
                    kg_score -= 0.5

        kg_score = max(0.0, kg_score)

        is_preserved = (
            len(entity_errors) == 0
            and len(numeric_errors) == 0
            and not polarity_inverted
            and prop_preserved
            and kg_score >= 0.80
        )

        return CommSemanticValidationResult(
            is_preserved=is_preserved,
            polarity_inverted=polarity_inverted,
            entity_errors=entity_errors,
            numeric_errors=numeric_errors,
            proposition_preserved=prop_preserved,
            knowledge_grounded_score=kg_score,
        )
