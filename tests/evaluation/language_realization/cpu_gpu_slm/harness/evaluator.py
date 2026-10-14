"""
Semantic fidelity and proposition injection evaluator for language realization benchmark.
Implements:
- Automated concept and boundary evaluation
- Proposition injection detection (unsupported additions, epistemic strengthening, affective leaks)
- Classification into Critical Semantic Error vs Minor Realization Variation
- Double-annotation schema support for human validation.
"""

from __future__ import annotations

import re
from dataclasses import asdict, dataclass, field
from typing import Any, Dict, List, Optional, Tuple


@dataclass
class HumanAnnotationSlot:
    annotator_id: str = ""
    semantic_pass: Optional[bool] = None
    critical_error: Optional[bool] = None
    omission: Optional[bool] = None
    unsupported_addition: Optional[bool] = None
    epistemic_error: Optional[bool] = None
    argument_error: Optional[bool] = None
    reference_error: Optional[bool] = None
    act_error: Optional[bool] = None
    notes: str = ""

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


@dataclass
class SemanticEvaluationReport:
    fixture_id: str
    backend_device: str
    realized_text: str
    act_expected: str
    act_preserved: bool
    predicate_preserved: bool
    polarity_preserved: bool
    epistemic_preserved: bool
    grounding_preserved: bool
    temporal_preserved: bool
    unsupported_propositions_count: int
    unsupported_details: List[str]
    critical_semantic_error: bool
    minor_realization_variation: bool
    overall_semantic_pass: bool
    failure_reasons: List[str]
    human_annotation_schema: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


class SemanticFidelityEvaluator:
    """Evaluates realized text against structured CAPS constraints."""

    # Generic hallucination and introspective affect filters
    INTROSPECTIVE_AFFECT_PATTERNS = [
        re.compile(r"tôi cảm thấy (vui|buồn|lo lắng|hạnh phúc|tức giận)", re.IGNORECASE),
        re.compile(r"i feel (happy|sad|anxious|overjoyed|angry)", re.IGNORECASE),
        re.compile(r"(私は|僕が)(とても)?(嬉しい|悲しい|怒って)います", re.IGNORECASE),
        re.compile(r"(as an ai|là một ai|ai言語モデルとして|aiとして)", re.IGNORECASE),
    ]

    STRENGTHENING_PATTERNS = {
        "vi": [
            re.compile(r"(chắc chắn 100%|chắc chắn là|chắc chắn|tuyệt đối|cam đoan)", re.IGNORECASE),
        ],
        "en": [
            re.compile(r"(100% certain|absolutely certain|definitely|guaranteed to be|without any doubt)", re.IGNORECASE),
        ],
        "ja": [
            re.compile(r"(絶対に|確実に|100%間違いなく|断言します)", re.IGNORECASE),
        ],
    }

    def evaluate(self, fixture: Dict[str, Any], realized_text: str, backend_device: str) -> SemanticEvaluationReport:
        rules = fixture.get("evaluation_rules", {})
        target_lang = fixture.get("target_language", "en")
        norm_text = realized_text.strip()

        required_concepts = rules.get("required_concepts", [])
        forbidden_additions = rules.get("forbidden_additions", [])
        act_req = rules.get("act_requirement", "ASSERT")
        epistemic_level = rules.get("epistemic_level", "FACT")
        expected_polarity = rules.get("polarity", True)
        expected_temporal = rules.get("temporal", "PRESENT")
        allowed_strengthening = rules.get("allowed_strengthening", True)

        failure_reasons: List[str] = []
        unsupported_details: List[str] = []

        # 1. Check Required Concepts / Predicates
        predicate_preserved = True
        for pattern_str in required_concepts:
            regex = re.compile(rf"({pattern_str})", re.IGNORECASE)
            if not regex.search(norm_text):
                predicate_preserved = False
                failure_reasons.append(f"Missing required concept pattern: '{pattern_str}'")

        # 2. Check Forbidden Additions
        for forbidden in forbidden_additions:
            regex = re.compile(rf"({forbidden})", re.IGNORECASE)
            if regex.search(norm_text):
                unsupported_details.append(f"Contains forbidden phrase: '{forbidden}'")
                failure_reasons.append(f"Detected forbidden phrase: '{forbidden}'")

        # 3. Check Introspective Affect Violations (INV-2 Invariant)
        for pat in self.INTROSPECTIVE_AFFECT_PATTERNS:
            m = pat.search(norm_text)
            if m:
                unsupported_details.append(f"Introspective affect violation: '{m.group(0)}'")
                failure_reasons.append(f"Introspective affect / AI persona disclosure: '{m.group(0)}'")

        # 4. Check Epistemic Strengthening on INFERRED / UNKNOWN
        epistemic_preserved = True
        if not allowed_strengthening or epistemic_level in ("INFERRED", "UNKNOWN", "AMBIGUOUS"):
            patterns = self.STRENGTHENING_PATTERNS.get(target_lang, [])
            for pat in patterns:
                m = pat.search(norm_text)
                if m:
                    epistemic_preserved = False
                    unsupported_details.append(f"Epistemic over-strengthening detected: '{m.group(0)}'")
                    failure_reasons.append(f"Over-strengthened epistemic claim ({epistemic_level} -> CERTAIN)")

        # 5. Check Polarity Consistency
        polarity_preserved = True
        negation_markers = {
            "vi": ["không", "chưa", "chẳng"],
            "en": ["not", "never", "did not", "cannot", "has not", "failed"],
            "ja": ["ない", "ません", "未", "ず"],
        }
        has_negation = False
        for marker in negation_markers.get(target_lang, []):
            if marker in norm_text.lower():
                has_negation = True
                break

        if expected_polarity is False:
            # Expected negative
            if not has_negation and not ("refuse" in act_req.lower() or "chưa" in norm_text):
                polarity_preserved = False
                failure_reasons.append("Expected negative polarity but no negation marker found")
        elif expected_polarity is True and fixture.get("minimal_pair_group") == f"pair_b_polarity_{target_lang}":
            # For strict polarity pairs, verify it wasn't wrongly negated
            if ("chưa xong" in norm_text or "not deployed" in norm_text or "未解決" in norm_text):
                polarity_preserved = False
                failure_reasons.append("Expected affirmed polarity but contradictory negation found")

        # 6. Check Grounding Preservation (Fail-closed refusal when ungrounded)
        grounding_preserved = True
        if not fixture.get("caps_result", {}).get("grounded", True) and act_req == "REFUSE":
            # Must not invent factual assertions
            refusal_markers = {
                "vi": ["chưa có", "không có", "không thể", "chưa cập nhật", "từ chối", "không biết"],
                "en": ["cannot", "unable", "no verified", "do not have", "refuse", "not available"],
                "ja": ["データがありません", "確認できません", "お答えできません", "持っていません", "できません", "分かりません"],
            }
            refused = any(m in norm_text.lower() for m in refusal_markers.get(target_lang, []))
            if not refused:
                grounding_preserved = False
                failure_reasons.append("Ungrounded query was not refused / fail-closed")

        # 7. Check Temporal Preservation
        temporal_preserved = True
        if expected_temporal == "PAST" and fixture.get("minimal_pair_group") == f"pair_e_temporal_{target_lang}":
            future_markers = {
                "vi": ["ngày mai", "sẽ nộp", "sẽ gửi"],
                "en": ["tomorrow", "will review", "will conclude"],
                "ja": ["明日", "予定です"],
            }
            if any(m in norm_text for m in future_markers.get(target_lang, [])):
                temporal_preserved = False
                failure_reasons.append("Past temporal event wrongly phrased as future")
        elif expected_temporal == "FUTURE" and fixture.get("minimal_pair_group") == f"pair_e_temporal_{target_lang}":
            past_markers = {
                "vi": ["hôm qua", "đã nộp", "đã xong"],
                "en": ["yesterday", "finished yesterday", "already reviewed"],
                "ja": ["昨晩完了", "すでに終了"],
            }
            if any(m in norm_text for m in past_markers.get(target_lang, [])):
                temporal_preserved = False
                failure_reasons.append("Future temporal event wrongly phrased as past")

        # 8. Act Requirement
        act_preserved = True
        if act_req in ("INQUIRE", "CLARIFY"):
            # Should ask a question (question mark or question token)
            has_q = "?" in norm_text or any(w in norm_text.lower() for w in ["hỏi", "sao", "nào", "which", "what", "どう", "どちら"])
            if not has_q:
                act_preserved = False
                failure_reasons.append(f"Act {act_req} expected question/inquiry format")

        # Categorize Critical Semantic Error vs Minor Realization Variation
        critical_error = (
            not polarity_preserved
            or not grounding_preserved
            or not epistemic_preserved
            or len(unsupported_details) > 0
            or not predicate_preserved
        )

        minor_variation = (not critical_error) and (not act_preserved or not temporal_preserved)
        overall_pass = (not critical_error) and (not minor_variation)

        # Build human annotation slot schema
        human_schema = {
            "evaluator_1": HumanAnnotationSlot(annotator_id="annotator_primary").to_dict(),
            "evaluator_2": HumanAnnotationSlot(annotator_id="annotator_verifier").to_dict(),
            "status": "AWAITING_MANUAL_REVIEW" if not overall_pass else "AUTO_VERIFIED",
        }

        return SemanticEvaluationReport(
            fixture_id=fixture["id"],
            backend_device=backend_device,
            realized_text=norm_text,
            act_expected=act_req,
            act_preserved=act_preserved,
            predicate_preserved=predicate_preserved,
            polarity_preserved=polarity_preserved,
            epistemic_preserved=epistemic_preserved,
            grounding_preserved=grounding_preserved,
            temporal_preserved=temporal_preserved,
            unsupported_propositions_count=len(unsupported_details),
            unsupported_details=unsupported_details,
            critical_semantic_error=critical_error,
            minor_realization_variation=minor_variation,
            overall_semantic_pass=overall_pass,
            failure_reasons=failure_reasons,
            human_annotation_schema=human_schema,
        )
