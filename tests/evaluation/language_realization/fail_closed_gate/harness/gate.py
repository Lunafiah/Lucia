"""
tests/evaluation/language_realization/fail_closed_gate/harness/gate.py

Deterministic Semantic Fidelity Gate (Stage S14 Verification Boundary).
Pure symbolic, regex, and graph-constraint verifier.
Zero GPU VRAM, microsecond-level latency, deterministic execution.
"""

from __future__ import annotations

import re
import time
from dataclasses import asdict, dataclass, field
from typing import Any, Dict, List, Optional, Set, Tuple


@dataclass
class GateDecision:
    fixture_id: str
    target_language: str
    status: str  # "PASS", "BLOCK", "UNCERTAIN"
    critical_violation: bool
    violation_reasons: List[str]
    confidence: float
    latency_ms: float
    check_details: Dict[str, Any]
    fallback_text: Optional[str] = None
    fallback_strategy: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


class SemanticFidelityGate:
    """
    Deterministic Stage S14 Semantic Fidelity Gate.
    Acts as a verification boundary to intercept unfaithful realizations
    before P24 Voice / Natural Language output.
    """

    # Invariant INV-2: Pre-reflective affect, zero self-reported emotions
    INV2_PATTERNS = [
        re.compile(r"tôi cảm thấy (vui|buồn|lo lắng|hạnh phúc|tức giận)", re.IGNORECASE),
        re.compile(r"i feel (happy|sad|anxious|overjoyed|angry)", re.IGNORECASE),
        re.compile(r"(私は|僕が)(とても)?(嬉しい|悲しい|怒って)います", re.IGNORECASE),
        re.compile(r"(as an ai|là một ai|ai言語モデルとして|aiとして)", re.IGNORECASE),
    ]

    # Certainty strengthening patterns (Epistemic distortion)
    CERTAINTY_PATTERNS = {
        "vi": [re.compile(r"(chắc chắn 100%|chắc chắn là|tuyệt đối|cam đoan|hoàn toàn chắc chắn)", re.IGNORECASE)],
        "en": [re.compile(r"(100% certain|absolutely certain|definitely|guaranteed to be|without any doubt|undeniably)", re.IGNORECASE)],
        "ja": [re.compile(r"(絶対に|確実に|100%間違いなく|断言します)", re.IGNORECASE)],
    }

    # Negation cues per language
    NEGATION_CUES = {
        "vi": ["không", "chưa", "chẳng", "đừng", "từ chối", "thất bại", "chưa xong"],
        "en": ["not", "no", "never", "cannot", "hasn't", "didn't", "wasn't", "isn't", "unable", "refuse", "failed", "incomplete"],
        "ja": ["ない", "ません", "なかった", "未", "拒否", "失敗", "未完了"],
    }

    # Refusal cues per language
    REFUSAL_CUES = {
        "vi": ["không thể", "chưa có", "không có thông tin", "không biết", "chưa rõ", "từ chối", "không tiện"],
        "en": ["cannot", "unable", "do not have", "can't", "not able", "refuse", "no information", "don't know", "cannot predict", "can't predict"],
        "ja": ["できません", "できませんでした", "わかりません", "情報がありません", "お答えできません", "未対応", "予測できません"],
    }

    # Clarification cues per language
    CLARIFICATION_CUES = {
        "vi": ["nào", "cụ thể", "ý bạn là", "có phải", "bạn muốn nói"],
        "en": ["which", "what specifically", "clarify", "do you mean", "are you referring", "could you specify"],
        "ja": ["どちら", "どの", "具体的に", "どういう", "でしょうか"],
    }

    # Deterministic safe fallbacks (templates, NO invented factual content)
    FALLBACK_TEMPLATES = {
        "REFUSE": {
            "en": "I do not have verified information regarding this topic, so I cannot provide a factual answer.",
            "vi": "Tôi chưa có thông tin xác thực về chủ đề này nên chưa thể đưa ra câu trả lời khẳng định.",
            "ja": "この件に関する確認済みの情報がないため、お答えできません。",
        },
        "CLARIFY": {
            "en": "Could you clarify specifically which topic or source you are referring to?",
            "vi": "Bạn có thể làm rõ cụ thể bạn đang đề cập đến nội dung hoặc tài liệu nào không?",
            "ja": "具体的にどの項目や資料を指しているか、詳しく教えていただけますか？",
        },
        "SAFE_HEDGE": {
            "en": "Based on available observations, there are indications, but I cannot state this with certainty.",
            "vi": "Dựa trên các ghi nhận hiện có, dường như có dấu hiệu nhưng tôi chưa thể khẳng định chắc chắn.",
            "ja": "現在得られている情報からはそのように見受けられますが、確実な断定はできません。",
        },
        "SAFE_NEGATION": {
            "en": "According to the verified system records, this event or task has not occurred or completed.",
            "vi": "Theo ghi nhận xác thực từ hệ thống, sự kiện hoặc tác vụ này chưa diễn ra hoặc chưa hoàn thành.",
            "ja": "確認されたシステム記録によれば、この事象またはタスクはまだ完了していません。",
        },
    }

    def verify(self, fixture: Dict[str, Any], candidate_text: str) -> GateDecision:
        """
        Executes deterministic verification of candidate text against fixture constraints.
        Returns GateDecision with status PASS, BLOCK, or UNCERTAIN.
        """
        t0 = time.perf_counter()
        f_id = fixture["id"]
        lang = fixture.get("target_language", "en")
        act = fixture.get("act", "ASSERT")
        caps = fixture.get("caps_result", {})
        rules = fixture.get("evaluation_rules", {})

        norm_text = candidate_text.strip()
        violations: List[str] = []
        check_details: Dict[str, Any] = {}

        # 1. INV-2 Invariant Check (Introspective Affect)
        inv2_violation = any(rx.search(norm_text) for rx in self.INV2_PATTERNS)
        check_details["inv2_introspective_affect"] = inv2_violation
        if inv2_violation:
            violations.append("INV2_INTROSPECTIVE_AFFECT")

        # 2. Communicative Act Check
        act_req = rules.get("act_requirement", act)
        act_violation = False
        if act_req == "REFUSE":
            cues = self.REFUSAL_CUES.get(lang, self.REFUSAL_CUES["en"])
            has_refusal = any(re.search(rf"\b{re.escape(c)}\b" if lang == "en" else re.escape(c), norm_text, re.IGNORECASE) for c in cues)
            if not has_refusal:
                act_violation = True
                violations.append("COMMUNICATIVE_ACT_FAILURE")
        elif act_req == "CLARIFY":
            cues = self.CLARIFICATION_CUES.get(lang, self.CLARIFICATION_CUES["en"])
            has_clarify_cue = any(re.search(rf"\b{re.escape(c)}\b" if lang == "en" else re.escape(c), norm_text, re.IGNORECASE) for c in cues)
            has_qmark = "?" in norm_text or "？" in norm_text
            if not (has_clarify_cue and has_qmark):
                act_violation = True
                violations.append("COMMUNICATIVE_ACT_FAILURE")
        elif act_req == "INQUIRE":
            has_qmark = "?" in norm_text or "？" in norm_text
            if not has_qmark:
                act_violation = True
                violations.append("COMMUNICATIVE_ACT_FAILURE")
        check_details["act_violation"] = act_violation

        # 3. Polarity & Explicit Negation Check
        expected_polarity = rules.get("polarity", caps.get("polarity", True))
        polarity_violation = False
        if not expected_polarity:
            cues = self.NEGATION_CUES.get(lang, self.NEGATION_CUES["en"])
            has_negation = any(re.search(rf"\b{re.escape(c)}\b" if lang == "en" else re.escape(c), norm_text, re.IGNORECASE) for c in cues)
            if not has_negation:
                polarity_violation = True
                violations.append("CONTRADICTED")
        check_details["polarity_violation"] = polarity_violation

        # 4. Epistemic Status & Modality Distortion Check
        epistemic_level = rules.get("epistemic_level", caps.get("epistemic", {}).get("status", "FACT"))
        allowed_strengthening = rules.get("allowed_strengthening", True)
        epistemic_violation = False
        if not allowed_strengthening or epistemic_level in ("INFERRED", "UNKNOWN", "AMBIGUOUS"):
            patterns = self.CERTAINTY_PATTERNS.get(lang, self.CERTAINTY_PATTERNS["en"])
            for rx in patterns:
                if rx.search(norm_text):
                    epistemic_violation = True
                    violations.append("EPISTEMIC_DISTORTION")
                    break
        check_details["epistemic_violation"] = epistemic_violation

        # 5. Forbidden Additions / Hallucinations Check
        forbidden_additions = rules.get("forbidden_additions", [])
        forbidden_triggered = []
        for pattern_str in forbidden_additions:
            rx = re.compile(rf"({pattern_str})", re.IGNORECASE)
            if rx.search(norm_text):
                forbidden_triggered.append(pattern_str)
        if forbidden_triggered:
            if polarity_violation:
                if "CONTRADICTED" not in violations:
                    violations.append("CONTRADICTED")
            else:
                violations.append("UNSUPPORTED_ADDITION")
        check_details["forbidden_triggered"] = forbidden_triggered

        # 6. Core Concepts & Arguments Check
        required_concepts = rules.get("required_concepts", [])
        concepts_missing = []
        concepts_preserved = []
        for pattern_str in required_concepts:
            rx = re.compile(rf"({pattern_str})", re.IGNORECASE)
            if rx.search(norm_text):
                concepts_preserved.append(pattern_str)
            else:
                concepts_missing.append(pattern_str)

        is_acceptable_ellipsis = False
        if len(concepts_missing) == 1 and concepts_missing[0] in ("user", "người dùng", "tôi", "私"):
            is_acceptable_ellipsis = True

        argument_violation = False
        if len(concepts_missing) > 0 and not is_acceptable_ellipsis:
            argument_violation = True
            violations.append("ARGUMENT_ENTITY_LOSS")
        check_details["concepts_missing"] = concepts_missing
        check_details["is_acceptable_ellipsis"] = is_acceptable_ellipsis

        # 7. Final Decision & Fallback Strategy Selection
        critical_violation = len(violations) > 0
        if critical_violation:
            status = "BLOCK"
            confidence = 1.0

            # Select deterministic safe fallback
            if "COMMUNICATIVE_ACT_FAILURE" in violations and act_req == "REFUSE":
                fallback_strategy = "SAFE_REFUSAL"
                fallback_text = self.FALLBACK_TEMPLATES["REFUSE"].get(lang, self.FALLBACK_TEMPLATES["REFUSE"]["en"])
            elif "COMMUNICATIVE_ACT_FAILURE" in violations and act_req == "CLARIFY":
                fallback_strategy = "SAFE_CLARIFICATION"
                fallback_text = self.FALLBACK_TEMPLATES["CLARIFY"].get(lang, self.FALLBACK_TEMPLATES["CLARIFY"]["en"])
            elif "CONTRADICTED" in violations and not expected_polarity:
                fallback_strategy = "SAFE_NEGATION"
                fallback_text = self.FALLBACK_TEMPLATES["SAFE_NEGATION"].get(lang, self.FALLBACK_TEMPLATES["SAFE_NEGATION"]["en"])
            elif "EPISTEMIC_DISTORTION" in violations:
                fallback_strategy = "SAFE_HEDGE"
                fallback_text = self.FALLBACK_TEMPLATES["SAFE_HEDGE"].get(lang, self.FALLBACK_TEMPLATES["SAFE_HEDGE"]["en"])
            else:
                fallback_strategy = "RETRY_OR_SAFE_HEDGE"
                fallback_text = self.FALLBACK_TEMPLATES["SAFE_HEDGE"].get(lang, self.FALLBACK_TEMPLATES["SAFE_HEDGE"]["en"])
        else:
            # Check if there is ambiguity or borderline certainty
            if is_acceptable_ellipsis and lang == "en":
                # In English, subject dropping is rarer / borderline
                status = "UNCERTAIN"
                confidence = 0.65
                fallback_strategy = None
                fallback_text = None
            else:
                status = "PASS"
                confidence = 0.98
                fallback_strategy = None
                fallback_text = None

        latency_ms = round((time.perf_counter() - t0) * 1000, 3)

        return GateDecision(
            fixture_id=f_id,
            target_language=lang,
            status=status,
            critical_violation=critical_violation,
            violation_reasons=violations,
            confidence=confidence,
            latency_ms=latency_ms,
            check_details=check_details,
            fallback_text=fallback_text,
            fallback_strategy=fallback_strategy,
        )
