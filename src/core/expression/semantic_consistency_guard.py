"""
src/core/expression/semantic_consistency_guard.py

Bounded Semantic Consistency Guard for expressive outputs.
Evaluates structured intent preservation, entity/number fidelity, and mutation patterns.
Does NOT declare universal truth verification for arbitrary LLM outputs.
"""

from __future__ import annotations

import logging
import re
from dataclasses import dataclass, field
from typing import Dict, List, Optional

logger = logging.getLogger(__name__)


@dataclass
class SemanticIntent:
    """
    Formal representation of communicative semantic intent.
    Guarantees that semantic truth conditions (who, what, polarity, facts)
    remain well-defined independently of affective surface realizations.
    """
    subject: str
    predicate: str
    object: str
    polarity: bool = True  # True = affirmative, False = negated
    named_entities: Dict[str, str] = field(default_factory=dict)
    numerical_values: Dict[str, float] = field(default_factory=dict)

    def to_canonical_proposition(self) -> str:
        prefix = "" if self.polarity else "NOT "
        return f"{prefix}({self.subject}, {self.predicate}, {self.object})"


@dataclass
class SemanticValidationResult:
    """Outcome of semantic preservation evaluation."""
    is_preserved: bool
    polarity_inverted: bool
    entity_errors: List[str]
    numeric_errors: List[str]
    proposition_preserved: bool


class SemanticConsistencyGuard:
    """
    Consistency verification guard for expressive surface text.
    Scope:
      1. Preserves structured intent (subject, predicate, object) in controlled contexts.
      2. Preserves named entities and numerical quantities.
      3. Detects and rejects polarity inversion (e.g. unintended negations).
    """

    @staticmethod
    def evaluate(intent: SemanticIntent, surface_text: str) -> SemanticValidationResult:
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

        is_preserved = (
            len(entity_errors) == 0
            and len(numeric_errors) == 0
            and not polarity_inverted
            and prop_preserved
        )

        return SemanticValidationResult(
            is_preserved=is_preserved,
            polarity_inverted=polarity_inverted,
            entity_errors=entity_errors,
            numeric_errors=numeric_errors,
            proposition_preserved=prop_preserved,
        )
