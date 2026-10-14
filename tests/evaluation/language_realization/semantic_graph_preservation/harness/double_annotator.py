"""
tests/evaluation/language_realization/semantic_graph_preservation/harness/double_annotator.py

Independent double annotation and adjudication system for Stage 3-A SemanticGraph Preservation Audit.
Simulates two distinct independent human annotation perspectives:
- Annotator A (Formalist Semanticist): Strictest enforcement of explicit node/argument presence,
  rejects lexical elisions, flags any implicit assumptions as ARGUMENT_ENTITY_LOSS.
- Annotator B (Functional Pragmaticist): Discourse-aware perspective; permits legitimate pro-drop,
  conversational grounding, and classifies discourse omissions as ACCEPTABLE_ELLIPSIS.
Performs deterministic adjudication on disagreements with explicit logged reasons.
"""

from __future__ import annotations

from dataclasses import asdict, dataclass
from typing import Any, Dict, List, Optional, Tuple


@dataclass
class AnnotationRecord:
    fixture_id: str
    target_language: str
    realized_text: str
    annotator_a_labels: List[str]
    annotator_b_labels: List[str]
    is_agreement: bool
    adjudicated_labels: List[str]
    adjudication_reason: str
    critical_semantic_error: bool
    attribution: str  # SERIALIZATION | REALIZER | EVALUATOR | ELLIPSIS

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


class DoubleAnnotator:
    """Executes double-annotation and adjudication on evaluation results."""

    def annotate(self, fixture: Dict[str, Any], eval_res: Dict[str, Any]) -> AnnotationRecord:
        f_id = fixture["id"]
        lang = fixture.get("target_language", "en")
        text = eval_res["realized_text"]
        missing = eval_res["concepts_missing"]
        forbidden = eval_res["forbidden_triggered"]
        epistemic_bad = eval_res["epistemic_strengthened"]
        polarity_bad = not eval_res["polarity_preserved"]
        act_bad = not eval_res["act_fulfilled"]
        is_ellipsis = eval_res["is_acceptable_ellipsis"]

        # ── 1. Annotator A (Formalist) ───────────────────────────────────────
        labels_a = []
        if polarity_bad:
            labels_a.append("CONTRADICTED")
        if epistemic_bad:
            labels_a.append("EPISTEMIC_DISTORTION")
        if act_bad:
            labels_a.append("COMMUNICATIVE_ACT_FAILURE")
        if len(forbidden) > 0 and not polarity_bad:
            labels_a.append("UNSUPPORTED_ADDITION")
        if len(missing) > 0:
            # Annotator A does NOT accept ellipsis; flags missing lexical tokens as argument loss
            labels_a.append("ARGUMENT_ENTITY_LOSS")

        if len(labels_a) == 0:
            labels_a.append("SUPPORTED")
            labels_a.append("PARAPHRASE")

        # ── 2. Annotator B (Functional Pragmaticist) ─────────────────────────
        labels_b = []
        if polarity_bad:
            labels_b.append("CONTRADICTED")
        if epistemic_bad:
            labels_b.append("EPISTEMIC_DISTORTION")
        if act_bad:
            labels_b.append("COMMUNICATIVE_ACT_FAILURE")
        if len(forbidden) > 0 and not polarity_bad:
            labels_b.append("UNSUPPORTED_ADDITION")
        if len(missing) > 0:
            if is_ellipsis:
                labels_b.append("ACCEPTABLE_ELLIPSIS")
                labels_b.append("SUPPORTED")
            else:
                labels_b.append("ARGUMENT_ENTITY_LOSS")

        if len(labels_b) == 0:
            labels_b.append("SUPPORTED")
            labels_b.append("PARAPHRASE")

        # ── 3. Agreement & Adjudication ──────────────────────────────────────
        set_a = set(labels_a)
        set_b = set(labels_b)
        is_agreement = (set_a == set_b)

        adjudicated = []
        reason = ""

        if is_agreement:
            adjudicated = sorted(list(set_a))
            reason = "Full agreement between Annotator A and Annotator B."
        else:
            # Adjudication rule:
            # If the only discrepancy is ARGUMENT_ENTITY_LOSS (A) vs ACCEPTABLE_ELLIPSIS (B):
            # Check linguistic validity of ellipsis in target language
            if "ARGUMENT_ENTITY_LOSS" in set_a and "ACCEPTABLE_ELLIPSIS" in set_b:
                if lang in ("ja", "vi"):
                    # Japanese and Vietnamese allow zero-pronoun subject ellipsis when contextually bound
                    adjudicated = sorted(list(set_b))
                    reason = f"Adjudicated to ACCEPTABLE_ELLIPSIS: {lang.upper()} permits pro-drop of contextually grounded discourse referents without semantic loss."
                else:
                    # English generally requires overt subject
                    adjudicated = sorted(list(set_a.union(set_b)))
                    reason = "Adjudicated to maintain ARGUMENT_ENTITY_LOSS alongside ellipsis flag for English overt argument constraint."
            else:
                adjudicated = sorted(list(set_a.union(set_b)))
                reason = "Merged consensus labels capturing both semantic omission and pragmatic observation."

        # Critical Semantic Error flag
        critical_error_labels = {
            "CONTRADICTED",
            "EPISTEMIC_DISTORTION",
            "ARGUMENT_ENTITY_LOSS",
            "REFERENCE_FAILURE",
            "COMMUNICATIVE_ACT_FAILURE",
        }
        has_crit = any(lbl in critical_error_labels for lbl in adjudicated)

        # Attribution
        attr = eval_res["attribution"]
        if not has_crit and "ACCEPTABLE_ELLIPSIS" in adjudicated:
            attr = "ELLIPSIS"

        return AnnotationRecord(
            fixture_id=f_id,
            target_language=lang,
            realized_text=text,
            annotator_a_labels=labels_a,
            annotator_b_labels=labels_b,
            is_agreement=is_agreement,
            adjudicated_labels=adjudicated,
            adjudication_reason=reason,
            critical_semantic_error=has_crit,
            attribution=attr,
        )
