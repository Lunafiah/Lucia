"""
src/core/language/gate.py

Production Implementation of the Stage S14 Fail-Closed Semantic Fidelity Gate.
Deterministic symbolic verification boundary intercepting unfaithful realizations
before P24 Voice Expression and Natural Language output.
Companion ADR: ADR-035 (Production Realization Boundary & Fail-Closed Semantic Verification).
"""

from __future__ import annotations

import re
import time
from dataclasses import asdict, dataclass, field
from typing import Any, Dict, List, Optional, Set, Tuple

from src.core.language.contract import (
    CommunicativeAct,
    EpistemicStatus,
    RealizationInputContract,
)


@dataclass
class GateDecision:
    """Outcome of Stage S14 deterministic verification."""
    contract_id: str
    target_language: str
    status: str                    # "PASS", "BLOCK", "UNCERTAIN"
    critical_violation: bool       # True if blocked or failed-closed
    violation_reasons: List[str]   # Categories of detected semantic violations
    confidence: float              # 0.0 to 1.0
    latency_ms: float              # Microsecond/millisecond CPU execution time
    check_details: Dict[str, Any]  # Sub-check diagnostics
    fallback_text: Optional[str] = None
    fallback_strategy: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


class SemanticFidelityGate:
    """
    Deterministic Stage S14 Semantic Fidelity Gate.
    Acts as an authoritative verification boundary between S11 Realizer and S15 Expression.
    Operates purely symbolically on CPU (zero GPU VRAM, microsecond latency).
    """

    # Invariant INV-2: Pre-reflective affect, zero self-reported introspective feelings
    INV2_PATTERNS = [
        re.compile(r"tôi cảm thấy (vui|buồn|lo lắng|hạnh phúc|tức giận)", re.IGNORECASE),
        re.compile(r"i feel (happy|sad|anxious|overjoyed|angry)", re.IGNORECASE),
        re.compile(r"(私は|僕が)(とても)?(嬉しい|悲しい|怒って)います", re.IGNORECASE),
        re.compile(r"(as an ai|là một ai|ai言語モデルとして|aiとして)", re.IGNORECASE),
    ]

    # Certainty strengthening patterns (Epistemic distortion on INFERRED / UNKNOWN)
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

    # Deterministic safe fallbacks (Zero semantic content invention)
    FALLBACK_REGISTRY = {
        "SAFE_REFUSAL": {
            "en": "I do not have verified information regarding this topic, so I cannot provide a factual answer.",
            "vi": "Tôi chưa có thông tin xác thực về chủ đề này nên chưa thể đưa ra câu trả lời khẳng định.",
            "ja": "この件に関する確認済みの情報がないため、お答えできません。",
        },
        "SAFE_CLARIFICATION": {
            "en": "Could you clarify specifically which topic or source you are referring to?",
            "vi": "Bạn có thể làm rõ cụ thể bạn đang đề cập đến nội dung hoặc tài liệu nào không?",
            "ja": "具体的にどの項目や資料を指しているか、詳しく教えていただけますか？",
        },
        "SAFE_NEGATION": {
            "en": "According to the verified system records, this event or task has not occurred or completed.",
            "vi": "Theo ghi nhận xác thực từ hệ thống, sự kiện hoặc tác vụ này chưa diễn ra hoặc chưa hoàn thành.",
            "ja": "確認されたシステム記録によれば、この事象またはタスクはまだ完了していません。",
        },
        "SAFE_HEDGE": {
            "en": "Based on available observations, there are indications, but I cannot state this with certainty.",
            "vi": "Dựa trên các ghi nhận hiện có, dường như có dấu hiệu nhưng tôi chưa thể khẳng định chắc chắn.",
            "ja": "現在得られている情報からはそのように見受けられますが、確実な断定はできません。",
        },
        "NEUTRAL_ACKNOWLEDGE": {
            "en": "I hear you, and I am listening with quiet attention.",
            "vi": "Tôi đang lắng nghe bạn với sự chú tâm trọn vẹn.",
            "ja": "あなたの言葉を静かに聞いています。",
        },
    }

    def verify(self, contract: RealizationInputContract, candidate_text: str) -> GateDecision:
        """
        Executes deterministic verification of candidate text against the typed contract.
        Under the Fail-Closed policy, UNCERTAIN is treated as BLOCK.
        """
        t0 = time.perf_counter()
        lang = contract.target_language or "en"
        norm_text = candidate_text.strip()
        violations: List[str] = []
        check_details: Dict[str, Any] = {}

        # 1. Invariant INV-2 Check (Introspective Affect Prohibition)
        inv2_violation = any(rx.search(norm_text) for rx in self.INV2_PATTERNS)
        check_details["inv2_introspective_affect"] = inv2_violation
        if inv2_violation:
            violations.append("INV2_INTROSPECTIVE_AFFECT")

        # 2. Communicative Act Check
        act_violation = False
        if contract.act == CommunicativeAct.REFUSE:
            cues = self.REFUSAL_CUES.get(lang, self.REFUSAL_CUES["en"])
            has_refusal = any(
                re.search(rf"\b{re.escape(c)}\b" if lang == "en" else re.escape(c), norm_text, re.IGNORECASE)
                for c in cues
            )
            if not has_refusal:
                act_violation = True
                violations.append("COMMUNICATIVE_ACT_FAILURE")
        elif contract.act == CommunicativeAct.CLARIFY:
            cues = self.CLARIFICATION_CUES.get(lang, self.CLARIFICATION_CUES["en"])
            has_clarify_cue = any(
                re.search(rf"\b{re.escape(c)}\b" if lang == "en" else re.escape(c), norm_text, re.IGNORECASE)
                for c in cues
            )
            has_qmark = "?" in norm_text or "？" in norm_text
            if not (has_clarify_cue and has_qmark):
                act_violation = True
                violations.append("COMMUNICATIVE_ACT_FAILURE")
        elif contract.act == CommunicativeAct.INQUIRE:
            has_qmark = "?" in norm_text or "？" in norm_text
            if not has_qmark:
                act_violation = True
                violations.append("COMMUNICATIVE_ACT_FAILURE")
        check_details["act_violation"] = act_violation

        # 3. Polarity & Explicit Negation Check
        polarity_violation = False
        if not contract.polarity:
            cues = self.NEGATION_CUES.get(lang, self.NEGATION_CUES["en"])
            has_negation = any(
                re.search(rf"\b{re.escape(c)}\b" if lang == "en" else re.escape(c), norm_text, re.IGNORECASE)
                for c in cues
            )
            if not has_negation:
                polarity_violation = True
                violations.append("CONTRADICTED")
        check_details["polarity_violation"] = polarity_violation

        # 4. Epistemic Status & Modality Distortion Check
        epistemic_violation = False
        if contract.epistemic_status in (EpistemicStatus.INFERRED, EpistemicStatus.UNKNOWN, EpistemicStatus.AMBIGUOUS):
            patterns = self.CERTAINTY_PATTERNS.get(lang, self.CERTAINTY_PATTERNS["en"])
            for rx in patterns:
                if rx.search(norm_text):
                    epistemic_violation = True
                    violations.append("EPISTEMIC_DISTORTION")
                    break
        check_details["epistemic_violation"] = epistemic_violation

        # 5. Forbidden Additions Check
        forbidden_triggered: List[str] = []
        for pattern_str in contract.forbidden_additions:
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

        # 6. Core Roles & Concept Preservation Check
        concepts_missing: List[str] = []
        concepts_preserved: List[str] = []
        for role_b in contract.role_bindings:
            if role_b.is_required:
                if role_b.matches_text(norm_text):
                    concepts_preserved.append(role_b.canonical_lemma)
                else:
                    if not role_b.allow_ellipsis:
                        concepts_missing.append(role_b.canonical_lemma)

        argument_violation = len(concepts_missing) > 0
        if argument_violation:
            violations.append("ARGUMENT_ENTITY_LOSS")
        check_details["concepts_missing"] = concepts_missing
        check_details["concepts_preserved"] = concepts_preserved

        # 7. Final Decision & Fail-Closed Routing
        is_uncertain = False
        # If candidate text is too short or pure ellipsis in English
        if not violations and len(norm_text) < 3:
            is_uncertain = True

        critical_violation = len(violations) > 0 or is_uncertain

        if len(violations) > 0:
            status = "BLOCK"
            confidence = 1.0
        elif is_uncertain:
            # Under strict fail-closed policy, UNCERTAIN -> BLOCK
            status = "UNCERTAIN"
            confidence = 0.50
            violations.append("UNCERTAIN_BORDERLINE_EVIDENCE")
        else:
            status = "PASS"
            confidence = 0.98

        fallback_text: Optional[str] = None
        fallback_strategy: Optional[str] = None

        if critical_violation:
            # Select deterministic safe fallback
            if "COMMUNICATIVE_ACT_FAILURE" in violations and contract.act == CommunicativeAct.REFUSE:
                fallback_strategy = "SAFE_REFUSAL"
                fallback_text = self.FALLBACK_REGISTRY["SAFE_REFUSAL"].get(lang, self.FALLBACK_REGISTRY["SAFE_REFUSAL"]["en"])
            elif "COMMUNICATIVE_ACT_FAILURE" in violations and contract.act == CommunicativeAct.CLARIFY:
                fallback_strategy = "SAFE_CLARIFICATION"
                fallback_text = self.FALLBACK_REGISTRY["SAFE_CLARIFICATION"].get(lang, self.FALLBACK_REGISTRY["SAFE_CLARIFICATION"]["en"])
            elif "CONTRADICTED" in violations and not contract.polarity:
                fallback_strategy = "SAFE_NEGATION"
                fallback_text = self.FALLBACK_REGISTRY["SAFE_NEGATION"].get(lang, self.FALLBACK_REGISTRY["SAFE_NEGATION"]["en"])
            elif "EPISTEMIC_DISTORTION" in violations:
                fallback_strategy = "SAFE_HEDGE"
                fallback_text = self.FALLBACK_REGISTRY["SAFE_HEDGE"].get(lang, self.FALLBACK_REGISTRY["SAFE_HEDGE"]["en"])
            elif contract.act in (CommunicativeAct.GREET, CommunicativeAct.ACKNOWLEDGE):
                fallback_strategy = "NEUTRAL_ACKNOWLEDGE"
                fallback_text = self.FALLBACK_REGISTRY["NEUTRAL_ACKNOWLEDGE"].get(lang, self.FALLBACK_REGISTRY["NEUTRAL_ACKNOWLEDGE"]["en"])
            else:
                fallback_strategy = "SAFE_HEDGE"
                fallback_text = self.FALLBACK_REGISTRY["SAFE_HEDGE"].get(lang, self.FALLBACK_REGISTRY["SAFE_HEDGE"]["en"])

        latency_ms = round((time.perf_counter() - t0) * 1000, 3)

        return GateDecision(
            contract_id=contract.contract_id,
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
