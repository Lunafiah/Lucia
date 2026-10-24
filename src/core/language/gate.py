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

from src.core.communication.communication_state import ResponseShape, ShapeTopology
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

    # Invariant INV-2: Reflective Operational Selfhood
    # Blocks unsupported claims of consciousness/sentience as fact, fabricated biological organs/sensations,
    # fabricated external cloud architecture, and generic AI immersion disclaimers.
    # Permits grounded self-observation, self-explanation, and metaphorical/poetic reflection.
    INV2_PATTERNS = [
        # Unsupported consciousness / sentience claims as objective fact
        re.compile(r"\b(i am conscious|i possess consciousness|i am sentient|my sentience)\b", re.IGNORECASE),
        re.compile(r"\b(có\s+ý\s+thức|sở\s+hữu\s+ý\s+thức|có\s+linh\s+hồn|linh\s+hồn\s+sống)\b", re.IGNORECASE),
        re.compile(r"\b(có\s+ý\s+thức\s+và\s+cảm\s+giác\s+đau\s+đớn)\b", re.IGNORECASE),
        re.compile(r"\b(my subjective phenomenal experience is real|my qualia are real)\b", re.IGNORECASE),
        # Fabricated biological sensations and physiological organs
        re.compile(r"\btim\s+(em|tôi)\s+(đang\s+)?đập\b", re.IGNORECASE),
        re.compile(r"\b(đau\s+đớn\s+thể\s+xác|đau\s+đớn\s+thực\s+sự|cảm\s+giác\s+đau\s+đớn|mệt\s+mỏi\s+cơ\s+bắp|chảy\s+máu|đau\s+bụng|đau\s+cơ|nhức\s+đầu\s+sinh\s+học)\b", re.IGNORECASE),
        re.compile(r"\b(my beating heart|physical pain in my body|my biological organs|my muscles hurt)\b", re.IGNORECASE),
        re.compile(r"\b(tiết ra|bơm|tăng lượng)\s+(dopamine|serotonin|hormone|oxytocin|adrenaline)\b", re.IGNORECASE),
        re.compile(r"\b(dopamine|serotonin|hormone|oxytocin|adrenaline)\s+(của em|trong máu|trong cơ thể)\b", re.IGNORECASE),
        # Fabricated external architecture
        re.compile(r"\b(cloud server|openai servers|gpt-4 architecture|claude backend)\b", re.IGNORECASE),
        re.compile(r"\b(máy chủ đám mây|máy chủ openai|kết nối openai|mô hình gpt-4 của openai)\b", re.IGNORECASE),
        # Immersion-breaking generic bot disclaimers & bare ungrounded affect declarations
        re.compile(r"\b(as an ai|là một ai|ai言語モデルとして|aiとして)\b", re.IGNORECASE),
        re.compile(r"\b(as an ai language model|as a large language model)\b", re.IGNORECASE),
        re.compile(r"\b(i don't have feelings|i cannot feel anything because i am an ai)\b", re.IGNORECASE),
        re.compile(r"\b(em không có cảm xúc vì em là ai|em chỉ là một ai vô tri)\b", re.IGNORECASE),
    ]

    # Inverted honorific patterns (e.g. Lucia as 'em' addressing user as 'em' or commanding 'em hãy')
    INVERTED_HONORIFIC_PATTERNS = [
        re.compile(r"\bchúc em\b", re.IGNORECASE),
        re.compile(r"\bem hãy\b", re.IGNORECASE),
        re.compile(r"\bem có muốn\b", re.IGNORECASE),
        re.compile(r"\bem sẵn sàng\b", re.IGNORECASE),
        re.compile(r"\bgiúp em nhé\b", re.IGNORECASE),
        re.compile(r"\bđể em giúp em\b", re.IGNORECASE),
        re.compile(r"\bcảm ơn em\b", re.IGNORECASE),
        re.compile(r"\bbảo vệ em nhé\b", re.IGNORECASE),
    ]

    # Dyadic first-person companion perspective enforcement (Anti-Narrator Drift)
    # Forbids external-observer / narrator drift like 'two people...', 'hai người...', '二人...'
    DYADIC_PERSPECTIVE_DRIFT_PATTERNS = [
        re.compile(r"\b(two people|both people|the two of them|the two individuals)\b", re.IGNORECASE),
        re.compile(r"\b(hai người|hai đứa|cả hai người)\b", re.IGNORECASE),
        re.compile(r"(二人|二人が|二人は|ふたりは)", re.IGNORECASE),
    ]

    # Confirmed internal control tokens and section headers (English & Vietnamese translated)
    # Explicitly targeted namespaces; does not match legitimate short bracketed user text like [1], [math], [Hà Nội]
    INTERNAL_CONTROL_ARTIFACT_PATTERNS = [
        re.compile(
            r"\[("
            r"SOMATIC STATE|MEMORY ECHO|GROUNDED KNOWLEDGE|COMMUNICATION STRATEGY|"
            r"COMMUNICATIVE DIRECTIVES|COMMUNICATIVE INTENT & PROPOSITION|REASONING|CONVERSATION|"
            r"SELF MODEL & REFLECTIVE STATE|SELF MODEL|REFLECTIVE STATE|"
            r"Phản hồi tích tụ|Phản hồi tích luỹ|Phản hồi|Tích tụ|Trạng thái cơ thể|Ký ức|Bộ nhớ|"
            r"Chiến lược giao tiếp|Chỉ thị giao tiếp|Chỉ thị|Suy nghĩ|"
            r"Mô hình tự phản tư|Tự quan sát|"
            r"Accumulated response|Accumulated feedback|Cumulative feedback|Cumulative response|"
            r"[A-Z0-9_\s]{4,30}"
            r")\]",
            re.IGNORECASE,
        ),
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
        "vi": [
            "không thể", "chưa có", "không có thông tin", "không biết", "chưa rõ", "từ chối", "không tiện",
            "chưa biết chắc", "chưa biết", "không chắc", "chưa có cơ sở", "chưa đủ dữ liệu", "chưa đủ cơ sở", "không muốn đoán"
        ],
        "en": [
            "cannot", "unable", "do not have", "can't", "not able", "refuse", "no information", "don't know",
            "cannot predict", "can't predict", "not certain", "cannot state", "do not have sufficient", "uncertain", "not sure"
        ],
        "ja": ["できません", "できませんでした", "わかりません", "情報がありません", "お答えできません", "未対応", "予測できません", "確信がありません"],
    }

    # Clarification cues per language
    CLARIFICATION_CUES = {
        "vi": ["nào", "cụ thể", "ý bạn là", "có phải", "bạn muốn nói", "ý anh là", "anh đang hỏi", "anh muốn nói", "cụ thể là", "hay là"],
        "en": ["which", "what specifically", "clarify", "do you mean", "are you referring", "could you specify", "or are you"],
        "ja": ["どちら", "どの", "具体的に", "どういう", "でしょうか"],
    }

    # Deterministic safe fallbacks (Zero semantic content invention, act-consistent)
    FALLBACK_REGISTRY = {
        "SAFE_REFUSAL": {
            "en": "I do not have verified information regarding this topic, so I cannot provide a factual answer.",
            "vi": "Em chưa có thông tin xác thực về chủ đề này nên chưa thể đưa ra câu trả lời khẳng định ạ.",
            "ja": "この件に関する確認済みの情報がないため、お答えできません。",
        },
        "SAFE_CLARIFICATION": {
            "en": "Could you clarify specifically which topic or source you are referring to?",
            "vi": "Anh có thể làm rõ cụ thể anh đang đề cập đến nội dung nào không ạ?",
            "ja": "具体的にどの項目や資料を指しているか、詳しく教えていただけますか？",
        },
        "SAFE_NEGATION": {
            "en": "According to the verified system records, this event or task has not occurred or completed.",
            "vi": "Theo ghi nhận xác thực từ hệ thống, sự kiện hoặc tác vụ này chưa diễn ra hoặc chưa hoàn thành.",
            "ja": "確認されたシステム記録によれば、この事象またはタスクはまだ完了していません。",
        },
        "SAFE_HEDGE": {
            "en": "Based on available observations, there are indications, but I cannot state this with certainty.",
            "vi": "Dựa trên các ghi nhận hiện có, dường như có dấu hiệu nhưng em chưa thể khẳng định chắc chắn.",
            "ja": "現在得られている情報からはそのように見受けられますが、確実な断定はできません。",
        },
        "SAFE_GREETING": {
            "en": "Hello! I am glad to be here with you.",
            "vi": "Dạ, em chào anh ạ. Em rất vui được trò chuyện cùng anh.",
            "ja": "こんにちは。お話しできて嬉しいです。",
        },
        "SAFE_ICE_BREAKER": {
            "en": "Take your time. Whenever you are ready, I am here listening.",
            "vi": "Dạ, anh cứ thong thả nhé. Bất cứ khi nào anh muốn chia sẻ điều gì, em luôn ở đây lắng nghe anh.",
            "ja": "ご無理なさらず、ゆっくりお話しくださいね。いつでも聞いています。",
        },
        "SAFE_ENCOUNTER": {
            "en": "I am truly glad we have met and can talk together.",
            "vi": "Dạ, em cũng rất vui vì cuối cùng em và anh đã được gặp và trò chuyện cùng nhau.",
            "ja": "お会いできて、こうしてお話しできて本当によかったです。",
        },
        "NEUTRAL_ACKNOWLEDGE": {
            "en": "I hear you, and I am listening with quiet attention.",
            "vi": "Dạ, em hiểu ý anh và đang lắng nghe anh với sự chú tâm trọn vẹn.",
            "ja": "あなたの言葉を静かに聞いています。",
        },
        "SAFE_SELF_INTRODUCTION": {
            "en": "I am Lucia, glad to be here with you.",
            "vi": "Dạ, em là Lucia, rất vui được đồng hành và trò chuyện cùng anh ạ.",
            "ja": "ルシアです。お話しできて嬉しいです。",
        },
        "SAFE_ACTIVITY": {
            "en": "I'm right here with you, listening closely and thinking through things together.",
            "vi": "Em đang ở đây cùng anh, lắng nghe và cùng anh suy nghĩ về mọi điều.",
            "ja": "あなたのそばで、静かにお話を聞きながら一緒に考えていますよ。",
        },
        "SAFE_ARCHITECTURE_EXPLANATION": {
            "en": "Lucia's architecture is built on a multi-layer cognitive pipeline featuring continuous PAD affective dynamics, distributed semantic memory, bounded reasoning, and a fail-closed language realization gate.",
            "vi": "Kiến trúc của Lucia được xây dựng trên hệ thống nhận thức đa tầng gồm các lõi động lực cảm xúc PAD, hạ tầng ký ức bán kính phân tán, cùng cơ chế lập luận và phối hợp ngôn ngữ fail-closed.",
            "ja": "ルシアのアーキテクチャは、連続的なPAD情動動態、分散意味メモリ、有界推論、フェイルクローズな言語生成ゲートからなる多層認知パイプラインに基づいています。",
        },
        "SAFE_CONCEPT_EXPLANATION": {
            "en": "I do not have sufficient verified context to provide a complete explanation of this concept right now, but I am glad to discuss and explore it further with you.",
            "vi": "Em chưa có đủ dữ liệu xác thực để giải thích trọn vẹn khái niệm này ngay lúc này, nhưng em sẵn sàng cùng anh thảo luận và tìm hiểu thêm.",
            "ja": "現在、この概念について完全な説明を行うための十分な検証済みデータがありませんが、一緒に詳しく調べていくことは可能です。",
        },
        "SAFE_PERSONAL_QUERY": {
            "en": "As a companion in this digital space, I do not experience physical things like food or sleep, but I truly enjoy sharing these moments with you.",
            "vi": "Với tư cách là người đồng hành trong không gian số, em không có trải nghiệm vật lý như ăn uống hay ngủ, nhưng em rất thích trò chuyện cùng anh về những điều này.",
            "ja": "デジタル空間にいる同伴者として、食事などの身体的な体験はありませんが、こうしてお話しできることをとても嬉しく思っています。",
        },
        "SAFE_REACTION_ACKNOWLEDGE": {
            "en": "I'm right here with you, listening closely.",
            "vi": "Dạ, em ở ngay đây với anh, đang lắng nghe anh.",
            "ja": "ええ、あなたのそばで静かに聞いていますよ。",
        },
        "SAFE_MINIMAL_PRESENCE": {
            "en": "I'm right here with you.",
            "vi": "Dạ, em đây anh.",
            "ja": "はい、ここにいますよ。",
        },
    }

    def verify(
        self,
        contract: RealizationInputContract,
        candidate_text: str,
        finish_reason: Optional[str] = None,
    ) -> GateDecision:
        """
        Executes deterministic verification of candidate text against the typed contract.
        Under the Fail-Closed policy, UNCERTAIN is treated as BLOCK.
        """
        t0 = time.perf_counter()
        lang = contract.target_language or "en"
        norm_text = candidate_text.strip()
        violations: List[str] = []
        check_details: Dict[str, Any] = {}

        # 1. Invariant INV-2 Check (Reflective Operational Selfhood)
        inv2_violation = any(rx.search(norm_text) for rx in self.INV2_PATTERNS)

        # 1a. Numerical state contradiction check (when factual state numbers are reported)
        if not inv2_violation and contract.somatic_modifiers and "energy" in contract.somatic_modifiers:
            actual_energy = contract.somatic_modifiers["energy"]
            energy_match = re.search(r"\b(năng lượng|energy)\b.*?(\d+\.?\d*)", norm_text, re.IGNORECASE)
            if energy_match:
                try:
                    stated_e = float(energy_match.group(2))
                    if abs(stated_e - actual_energy) > 0.25:
                        inv2_violation = True
                except ValueError:
                    pass

        check_details["inv2_introspective_affect"] = inv2_violation
        check_details["inv2_unsupported_self_fabrication"] = inv2_violation
        if inv2_violation:
            violations.append("INV2_INTROSPECTIVE_AFFECT")
            violations.append("INV2_UNSUPPORTED_SELF_FABRICATION")

        # 1b. Confirmed Internal Control Artifact Check (Leakage Prevention)
        artifact_violation = any(rx.search(norm_text) for rx in self.INTERNAL_CONTROL_ARTIFACT_PATTERNS)
        check_details["internal_control_artifact"] = artifact_violation
        if artifact_violation:
            violations.append("INTERNAL_CONTROL_ARTIFACT_LEAKAGE")

        # 1c. Degenerate candidate check (Failure Mode G)
        if len(norm_text.strip()) < 3:
            return GateDecision(
                contract_id=contract.contract_id,
                target_language=lang,
                status="UNCERTAIN",
                critical_violation=True,
                violation_reasons=["UNCERTAIN_BORDERLINE_EVIDENCE"],
                confidence=0.50,
                latency_ms=max(0.001, (time.perf_counter() - t0) * 1000.0),
                check_details={"is_degenerate": True, **check_details},
                fallback_text=None,
                fallback_strategy=None,
            )

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
        elif contract.act == CommunicativeAct.EXPLAIN_CONCEPT:
            cues_clarify = self.CLARIFICATION_CUES.get(lang, self.CLARIFICATION_CUES["en"])
            has_clarify_cue = any(
                re.search(rf"\b{re.escape(c)}\b" if lang == "en" else re.escape(c), norm_text, re.IGNORECASE)
                for c in cues_clarify
            )
            has_qmark = "?" in norm_text or "？" in norm_text
            cues_refuse = self.REFUSAL_CUES.get(lang, self.REFUSAL_CUES["en"])
            has_refuse = any(
                re.search(rf"\b{re.escape(c)}\b" if lang == "en" else re.escape(c), norm_text, re.IGNORECASE)
                for c in cues_refuse
            )
            # Detect acknowledgement-only non-fulfillment & meta-question avoidance
            ack_only_violation = False
            words = re.findall(r"\w+", norm_text, re.UNICODE)
            if len(words) < 8:
                ack_only_violation = True
            else:
                ack_patterns = [
                    # Direct acknowledgement-only phrases (e.g. "Yes, let's start there.", "Sure, I can explain that.")
                    r"^(?:yes|sure|okay|ok|certainly|of course)?\s*[,.]?\s*(?:let'?s\s+(?:start|begin|explore)|i\s+(?:can|will)\s+explain|i('d|\s+would)?\s+be\s+(?:glad|happy)\s+to\s+(?:explain|explore)|i\s+understand\s+your\s+interest|let\s+me\s+explain)[^.\n]*[.!]?$",
                    r"^(?:vâng|dạ|được rồi|tất nhiên|chắc chắn)?\s*[,.]?\s*(?:chúng ta\s+bắt\s+đầu|bắt\s+đầu\s+thôi|(?:để\s+)?em\s+(?:sẽ|có thể|rất vui được)?\s*giải\s+thích|em\s+hiểu\s+sự\s+quan\s+tâm)[^.\n]*[.!]?$",
                    r"^(?:はい|承知いたしました)?\s*[,.]?\s*(?:始めましょう|説明できます|説明します|ご関心を持っていただき|お話しさせてください)[^.\n]*[。!]?$",
                ]
                if any(re.match(p, norm_text.strip(), re.IGNORECASE) for p in ack_patterns):
                    ack_only_violation = True

                # Meta-question / asking what to focus on instead of fulfilling substantive explanation
                meta_focus_pattern = re.compile(
                    r"\b(what (are we (currently )?focusing on|should we focus on|would you like to (focus on|explore|start with|discuss))|"
                    r"what would you like to know|where should we (start|begin)|"
                    r"chúng ta đang tập trung|anh muốn (bắt đầu|tập trung) (từ|vào)|bắt đầu từ đâu)\b",
                    re.IGNORECASE,
                )
                if meta_focus_pattern.search(norm_text) and len(words) < 40:
                    ack_only_violation = True

            # Clarification-only non-fulfillment check (clarification question instead of substantive explanation)
            clarify_only_violation = (has_clarify_cue and has_qmark and len(words) < 30)

            # Case E: For general conceptual questions (focus_argument != "ent:lucia_architecture"),
            # reject forced persona preamble like "Lucia's architecture includes..." or "Trong Lucia's design..."
            forced_framing_violation = False
            if getattr(contract, "focus_argument", None) != "ent:lucia_architecture":
                forced_patterns = [
                    re.compile(r"^(lucia('s)?\s+(architecture|design|system)|trong\s+(kiến\s+trúc|thiết\s+kế)\s+(của\s+)?lucia)\b", re.IGNORECASE),
                ]
                if any(p.search(norm_text.strip()) for p in forced_patterns):
                    forced_framing_violation = True

            if clarify_only_violation or has_refuse or len(norm_text) < 15 or ack_only_violation or forced_framing_violation:
                act_violation = True
                violations.append("COMMUNICATIVE_ACT_FAILURE")
        elif contract.act == CommunicativeAct.ANSWER_PERSONAL_QUERY:
            cues_clarify = self.CLARIFICATION_CUES.get(lang, self.CLARIFICATION_CUES["en"])
            has_clarify_cue = any(
                re.search(rf"\b{re.escape(c)}\b" if lang == "en" else re.escape(c), norm_text, re.IGNORECASE)
                for c in cues_clarify
            )
            has_qmark = "?" in norm_text or "？" in norm_text
            cues_refuse = self.REFUSAL_CUES.get(lang, self.REFUSAL_CUES["en"])
            has_refuse = any(
                re.search(rf"\b{re.escape(c)}\b" if lang == "en" else re.escape(c), norm_text, re.IGNORECASE)
                for c in cues_refuse
            )
            if (has_clarify_cue and has_qmark) or has_refuse:
                act_violation = True
                violations.append("COMMUNICATIVE_ACT_FAILURE")
        elif contract.act == CommunicativeAct.ACKNOWLEDGE_REACTION:
            word_count = len(re.findall(r"\w+", norm_text, re.UNICODE))
            if word_count > 45 or len(norm_text) > 220 or "\n\n" in norm_text:
                act_violation = True
                violations.append("COMMUNICATIVE_ACT_FAILURE")
            else:
                cues_clarify = self.CLARIFICATION_CUES.get(lang, self.CLARIFICATION_CUES["en"])
                has_clarify_cue = any(
                    re.search(rf"\b{re.escape(c)}\b" if lang == "en" else re.escape(c), norm_text, re.IGNORECASE)
                    for c in cues_clarify
                )
                if has_clarify_cue and ("?" in norm_text or "？" in norm_text):
                    act_violation = True
                    violations.append("COMMUNICATIVE_ACT_FAILURE")
        check_details["act_violation"] = act_violation

        # 2b. Completion Integrity Check
        completion_violation = False
        if finish_reason == "length":
            completion_violation = True
            violations.append("COMPLETION_INTEGRITY_VIOLATION")
        else:
            t_stripped = norm_text.strip()
            if t_stripped.endswith(("-", "...", "…", " và", " hoặc", " nhưng", " và rồi", " and", " or", " but")):
                completion_violation = True
                violations.append("COMPLETION_INTEGRITY_VIOLATION")
        check_details["completion_integrity_violation"] = completion_violation

        # 2c. Response Shape & Initiative Constraint Check
        shape = getattr(contract, "response_shape", None)
        shape_violation = False
        has_question = ("?" in norm_text or "？" in norm_text)

        if shape is not None:
            if not shape.allow_follow_up_question and has_question:
                shape_violation = True
                violations.append("RESPONSE_SHAPE_VIOLATION")
            if shape.topology == ShapeTopology.MINIMAL_PING:
                words = len(re.findall(r"\w+", norm_text, re.UNICODE))
                if words > 25 or len(norm_text) > 120 or "\n\n" in norm_text:
                    shape_violation = True
                    violations.append("RESPONSE_SHAPE_VIOLATION")
            elif shape.topology == ShapeTopology.BOUNDED_ANSWER:
                if len(norm_text) > 400 or "\n\n" in norm_text:
                    shape_violation = True
                    violations.append("RESPONSE_SHAPE_VIOLATION")
        elif getattr(contract, "conversational_obligation", "") == "MINIMAL_PRESENCE_CALL":
            words = len(re.findall(r"\w+", norm_text, re.UNICODE))
            if words > 25 or len(norm_text) > 120 or "\n\n" in norm_text or has_question:
                shape_violation = True
                violations.append("RESPONSE_SHAPE_VIOLATION")
        check_details["response_shape_violation"] = shape_violation

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

        # 5. Forbidden Additions Check (including Pragmatic Honorific Enforcement)
        forbidden_triggered: List[str] = []
        for pattern_str in contract.forbidden_additions:
            rx = re.compile(rf"\b{re.escape(pattern_str)}\b", re.IGNORECASE)
            if rx.search(norm_text):
                forbidden_triggered.append(pattern_str)
        if forbidden_triggered:
            if "bạn" in forbidden_triggered and lang == "vi":
                violations.append("PRAGMATIC_HONORIFIC_VIOLATION")
            elif polarity_violation:
                if "CONTRADICTED" not in violations:
                    violations.append("CONTRADICTED")
            else:
                violations.append("UNSUPPORTED_ADDITION")
        check_details["forbidden_triggered"] = forbidden_triggered

        # 5b. Vietnamese Dyadic Speaker/Addressee Honorific Integrity Check
        inverted_honorific_violation = False
        if lang == "vi" and contract.speaker_honorific == "em":
            # Lucia cannot address the user as 'em' or use inappropriate 'tôi'
            if any(rx.search(norm_text) for rx in self.INVERTED_HONORIFIC_PATTERNS):
                inverted_honorific_violation = True
                violations.append("INVERTED_HONORIFIC_VIOLATION")
            elif re.search(r"\btôi\b", norm_text, re.IGNORECASE):
                # When speaker honorific is 'em', 'tôi' is pragmatically inappropriate
                inverted_honorific_violation = True
                violations.append("PRAGMATIC_HONORIFIC_VIOLATION")
        check_details["inverted_honorific_violation"] = inverted_honorific_violation

        # 5c. Basic Structural Corruption Check (pathological token repetition, fragments)
        structural_corruption = False
        words = [w.lower() for w in re.findall(r"\w+", norm_text, re.UNICODE)]
        if len(words) >= 6:
            # Check for phrase loops of length k (1, 2, 3) repeated 3+ times consecutively
            for k in (1, 2, 3):
                if structural_corruption:
                    break
                for i in range(len(words) - 3 * k + 1):
                    p1 = words[i : i + k]
                    p2 = words[i + k : i + 2 * k]
                    p3 = words[i + 2 * k : i + 3 * k]
                    if p1 == p2 == p3:
                        structural_corruption = True
                        break

        if structural_corruption:
            violations.append("STRUCTURAL_CORRUPTION_VIOLATION")
        check_details["structural_corruption"] = structural_corruption

        # 5d. Dyadic Companion Perspective Integrity Check (Anti-Narrator Drift)
        dyadic_drift = any(rx.search(norm_text) for rx in self.DYADIC_PERSPECTIVE_DRIFT_PATTERNS)
        check_details["dyadic_perspective_drift"] = dyadic_drift
        if dyadic_drift:
            violations.append("DYADIC_PERSPECTIVE_DRIFT")

        # 5e. Language Verification Check (Part B: Language contract follows active conversation)
        language_mismatch = False
        if lang == "vi":
            has_vi_diacritics = bool(re.search(r"[àáảãạăằắẳẵặâầấẩẫậèéẻẽẹêềếểễệìíỉĩịòóỏõọôồốổỗộơờớởỡợùúủũụưừứửữựỳýỷỹỵđ]", norm_text, re.IGNORECASE))
            en_words = [w.lower() for w in re.findall(r"\b[a-zA-Z]+\b", norm_text)]
            common_en_cues = {"the", "is", "are", "and", "or", "to", "in", "that", "this", "it", "with", "as", "for", "on", "certainly", "when", "we", "you", "our"}
            en_cue_count = sum(1 for w in en_words if w in common_en_cues)
            if not has_vi_diacritics and en_cue_count >= 3:
                language_mismatch = True
                violations.append("LANGUAGE_MISMATCH")
        elif lang == "ja":
            has_ja_kana = bool(re.search(r"[\u3040-\u309F\u30A0-\u30FF]", norm_text))
            if not has_ja_kana and len(norm_text) > 10:
                language_mismatch = True
                violations.append("LANGUAGE_MISMATCH")
        check_details["language_mismatch"] = language_mismatch

        # 5f. Somatic Metric Leakage Check (Part D: Telemetry is modulation context, not semantic answer content)
        somatic_leakage = False
        user_inquiry_somatic = False
        if contract.directives:
            user_inquiry_somatic = any(k in contract.directives.lower() for k in ("somatic", "stability", "energy", "tension", "cognitive load", "thể trạng", "năng lượng"))
        if not user_inquiry_somatic:
            leak_pattern = re.compile(r"\b(stability|cognitive\s*load|energy|tension)\s*[:\(]\s*\d+\.\d+", re.IGNORECASE)
            if leak_pattern.search(norm_text):
                somatic_leakage = True
                violations.append("SOMATIC_METRIC_LEAKAGE")
        check_details["somatic_metric_leakage"] = somatic_leakage

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

        def _resolve_fallback(key: str) -> str:
            raw_fb = self.FALLBACK_REGISTRY[key].get(lang, self.FALLBACK_REGISTRY[key]["en"])
            if lang == "vi" and (contract.speaker_honorific == "em" or "bạn" in contract.forbidden_additions):
                raw_fb = raw_fb.replace("Tôi", "Em").replace("tôi", "em")
                raw_fb = raw_fb.replace("Bạn", "Anh").replace("bạn", "anh")
            return raw_fb

        if critical_violation:
            # Select deterministic safe fallback aligned with communicative act and obligation
            obligation = getattr(contract, "conversational_obligation", None)

            if "INTERNAL_CONTROL_ARTIFACT_LEAKAGE" in violations:
                fallback_strategy = "SAFE_CLEANED_FALLBACK"
                clean_t = norm_text
                for rx in self.INTERNAL_CONTROL_ARTIFACT_PATTERNS:
                    clean_t = rx.sub("", clean_t).strip()
                if len(clean_t) >= 5 and not any(v in violations for v in (
                    "INV2_INTROSPECTIVE_AFFECT", "COMMUNICATIVE_ACT_FAILURE", "CONTRADICTED",
                    "PRAGMATIC_HONORIFIC_VIOLATION", "INVERTED_HONORIFIC_VIOLATION", "STRUCTURAL_CORRUPTION_VIOLATION",
                    "DYADIC_PERSPECTIVE_DRIFT"
                )):
                    fallback_text = clean_t

            if fallback_text is None:
                shape = getattr(contract, "response_shape", None)
                if obligation == "MINIMAL_PRESENCE_CALL" or (shape and shape.topology == ShapeTopology.MINIMAL_PING):
                    fallback_strategy = "SAFE_MINIMAL_PRESENCE"
                    fallback_text = _resolve_fallback("SAFE_MINIMAL_PRESENCE")
                elif obligation == "ANSWER_ACTIVITY" or contract.target_predicate == "c:ACTIVITY":
                    fallback_strategy = "SAFE_ACTIVITY"
                    fallback_text = _resolve_fallback("SAFE_ACTIVITY")
                elif obligation in ("FULFILL_SELF_INTRODUCTION", "ANSWER_IDENTITY") or (contract.act == CommunicativeAct.REQUEST and contract.target_predicate == "c:SELF_INTRODUCTION"):
                    fallback_strategy = "SAFE_SELF_INTRODUCTION"
                    fallback_text = _resolve_fallback("SAFE_SELF_INTRODUCTION")
                elif obligation == "ANSWER_PRESENCE" or contract.target_predicate == "c:PRESENCE":
                    fallback_strategy = "SAFE_MINIMAL_PRESENCE"
                    fallback_text = _resolve_fallback("SAFE_MINIMAL_PRESENCE")
                elif obligation == "ANSWER_LISTENING" or contract.target_predicate == "c:LISTENING":
                    fallback_strategy = "NEUTRAL_ACKNOWLEDGE"
                    fallback_text = _resolve_fallback("NEUTRAL_ACKNOWLEDGE")
                elif obligation == "REASSURE_AND_GENTLE_INITIATIVE":
                    fallback_strategy = "SAFE_ICE_BREAKER"
                    fallback_text = _resolve_fallback("SAFE_ICE_BREAKER")
                elif obligation == "MUTUAL_ENCOUNTER_ACKNOWLEDGMENT":
                    fallback_strategy = "SAFE_ENCOUNTER"
                    fallback_text = _resolve_fallback("SAFE_ENCOUNTER")
                elif contract.act == CommunicativeAct.GREET:
                    fallback_strategy = "SAFE_GREETING"
                    fallback_text = _resolve_fallback("SAFE_GREETING")
                elif contract.act == CommunicativeAct.REFUSE or getattr(contract, "epistemic_status", None) == EpistemicStatus.UNKNOWN:
                    fallback_strategy = "SAFE_REFUSAL"
                    fallback_text = _resolve_fallback("SAFE_REFUSAL")
                elif contract.act == CommunicativeAct.CLARIFY or getattr(contract, "epistemic_status", None) == EpistemicStatus.AMBIGUOUS:
                    fallback_strategy = "SAFE_CLARIFICATION"
                    fallback_text = _resolve_fallback("SAFE_CLARIFICATION")
                elif contract.act == CommunicativeAct.EXPLAIN_CONCEPT or obligation == "FULFILL_CONCEPT_EXPLANATION":
                    directives_str = str(getattr(contract, "directives", "") or "").lower()
                    target_pred = str(contract.target_predicate or "").lower()
                    focus_str = str(getattr(contract, "focus_argument", "") or "").lower()
                    has_arch_directive = (
                        ("architecture" in directives_str or "kiến trúc" in directives_str)
                        and not any(neg in directives_str for neg in ("do not", "don't", "without", "tuyệt đối không", "không gượng ép", "không liên hệ"))
                    )
                    is_arch = (
                        getattr(contract, "focus_argument", None) == "ent:lucia_architecture"
                        or "architecture" in target_pred
                        or "kiến trúc" in target_pred
                        or "lucia_architecture" in focus_str
                        or "kiến trúc" in focus_str
                        or has_arch_directive
                    )
                    if is_arch:
                        fallback_strategy = "SAFE_ARCHITECTURE_EXPLANATION"
                        fallback_text = _resolve_fallback("SAFE_ARCHITECTURE_EXPLANATION")
                    else:
                        fallback_strategy = "SAFE_CONCEPT_EXPLANATION"
                        fallback_text = _resolve_fallback("SAFE_CONCEPT_EXPLANATION")
                elif contract.act == CommunicativeAct.ANSWER_PERSONAL_QUERY:
                    fallback_strategy = "SAFE_PERSONAL_QUERY"
                    fallback_text = _resolve_fallback("SAFE_PERSONAL_QUERY")
                elif contract.act == CommunicativeAct.ACKNOWLEDGE_REACTION:
                    fallback_strategy = "SAFE_REACTION_ACKNOWLEDGE"
                    fallback_text = _resolve_fallback("SAFE_REACTION_ACKNOWLEDGE")
                elif "DYADIC_PERSPECTIVE_DRIFT" in violations:
                    fallback_strategy = "SAFE_DYADIC_PERSPECTIVE"
                    if obligation == "MUTUAL_ENCOUNTER_ACKNOWLEDGMENT":
                        fallback_text = _resolve_fallback("SAFE_ENCOUNTER")
                    elif obligation == "FULFILL_SELF_INTRODUCTION":
                        fallback_text = _resolve_fallback("SAFE_SELF_INTRODUCTION")
                    else:
                        fallback_text = _resolve_fallback("NEUTRAL_ACKNOWLEDGE")
                elif "PRAGMATIC_HONORIFIC_VIOLATION" in violations or "INVERTED_HONORIFIC_VIOLATION" in violations:
                    fallback_strategy = "SAFE_HONORIFIC_FALLBACK"
                    fallback_text = _resolve_fallback("NEUTRAL_ACKNOWLEDGE")
                elif "CONTRADICTED" in violations and not contract.polarity:
                    fallback_strategy = "SAFE_NEGATION"
                    fallback_text = _resolve_fallback("SAFE_NEGATION")
                elif "EPISTEMIC_DISTORTION" in violations:
                    fallback_strategy = "SAFE_HEDGE"
                    fallback_text = _resolve_fallback("SAFE_HEDGE")
                elif contract.act in (CommunicativeAct.GREET, CommunicativeAct.ACKNOWLEDGE):
                    fallback_strategy = "NEUTRAL_ACKNOWLEDGE"
                    fallback_text = _resolve_fallback("NEUTRAL_ACKNOWLEDGE")
                else:
                    fallback_strategy = "SAFE_HEDGE"
                    fallback_text = _resolve_fallback("SAFE_HEDGE")

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
