"""
PromptAssembler — builds the Conditioned_Prompt from somatic markers,
behavioral constraints, conversation history, and optional memory echo vector.

Section order:
  1. System preamble
  2. [SOMATIC STATE]  — numeric key-value pairs only, no prose emotional labels
  3. [MEMORY ECHO]     — numeric key-value pairs only (Phase 2, omitted if None)
  4. [REASONING]       — omitted when reasoning_depth == 0
  5. [CONVERSATION]    — trimmed to max 10 turns or token budget

Requirements: Phase 1 (5.1–5.8), Phase 2 (11.2–11.4, 12.1, 12.5, 16.3)
"""

from __future__ import annotations

from typing import TYPE_CHECKING, List, Optional, Tuple, Union

import numpy as np

from src.core.errors import AssemblyError
from src.core.models import BehavioralConstraints, SomaticMarkers

if TYPE_CHECKING:
    from src.core.communication.caps import CAPSResult
    from src.core.communication.communication_state import CommunicationState
    from src.core.knowledge.proposition import Proposition
    from src.core.language.contract import RealizationInputContract

# Section separator (Requirement 5.1)
_SEP = "\n\n---\n\n"

FORBIDDEN_RECALL_PHRASES = [
    "I remember",
    "I recall",
    "last time",
    "you mentioned",
    "you said",
    "I know from before",
    "previously you",
    "my memory",
]


def _estimate_tokens(text: str) -> int:
    """Rough token count: len(text) // 4 (matches design.md specification)."""
    return max(1, len(text) // 4)


class PromptAssembler:
    """
    Assembles the conditioned prompt passed to the LLM_Backend.

    The assembler is stateless — all inputs are passed to assemble().
    """

    SECTION_SEP = _SEP

    def assemble(
        self,
        somatic: SomaticMarkers,
        constraints: BehavioralConstraints,
        history: List[Tuple[str, str]],
        system_preamble: str = "",
        n_ctx: int = 4096,
        *,
        echo_vector: Optional[np.ndarray] = None,
        comm_state: Optional[CommunicationState] = None,
        knowledge_propositions: Optional[List[Proposition]] = None,
        caps_result: Optional[CAPSResult] = None,
        contract: Optional[RealizationInputContract] = None,
        self_interpretation: Optional[Any] = None,
    ) -> Union[str, AssemblyError]:
        """
        Build the Conditioned_Prompt string.

        Parameters
        ----------
        somatic : SomaticMarkers
            Current somatic state — inserted as numeric key-value pairs.
        constraints : BehavioralConstraints
            Generation parameters that shape history trimming and reasoning depth.
        history : list of (role, text) tuples
            Conversation history, oldest first.
        system_preamble : str
            Static system prompt prefix.
        n_ctx : int
            LLM context window token limit. Used for overflow detection.
        echo_vector : np.ndarray | None, optional
            Echo_Vector synthesized by EcphoryEngine (Phase 2).
        comm_state : CommunicationState | None, optional
            Communication strategy and framing state (Phase 16).
        knowledge_propositions : list of Proposition | None, optional
            Structured knowledge facts retrieved for grounding (Phase 16).
        caps_result : CAPSResult | None, optional
            Communicative Act & Proposition Selection result (Phase 23 / S11 transition).
        contract : RealizationInputContract | None, optional
            Typed Realization Input Contract (ADR-035 / Phase 24 S11 boundary).

        Returns
        -------
        str
            The assembled prompt.
        AssemblyError
            If the preamble + somatic state section alone exceeds n_ctx
            (Requirement 5.8) or if forbidden phrases appear.
        """
        # --- Section 1: system preamble ---
        preamble_section = system_preamble.strip()

        # --- Section 2: somatic state (numeric only — Requirement 5.2) ---
        somatic_section = (
            "[SOMATIC STATE]\n"
            f"stability: {somatic.stability:.6f}\n"
            f"cognitive_load: {somatic.cognitive_load:.6f}\n"
            f"energy: {somatic.energy:.6f}\n"
            f"tension: {somatic.tension:.6f}"
        )

        # --- Section 3: memory echo (Phase 2) ---
        echo_section = ""
        if echo_vector is not None:
            try:
                echo_section = self._encode_echo_section(echo_vector)
            except AssemblyError as err:
                return err

        # --- Section 4: grounded knowledge (Phase 16) ---
        knowledge_section = ""
        if knowledge_propositions:
            facts = [f"({p.subject}, {p.predicate}, {p.object})" for p in knowledge_propositions[:5]]
            knowledge_section = "[GROUNDED KNOWLEDGE]\n" + "\n".join(facts)

        # --- Section 5: communication strategy (Phase 16) ---
        comm_section = ""
        if comm_state is not None:
            comm_section = (
                "[COMMUNICATION STRATEGY]\n"
                f"strategy: {comm_state.strategy.value}\n"
                f"directness: {comm_state.directness:.2f}\n"
                f"formality: {comm_state.formality_score:.2f}\n"
                f"elaboration: {comm_state.elaboration_depth:.2f}\n"
                f"supportiveness: {comm_state.supportiveness:.2f}"
            )

        # --- Section 5b: communicative directives (ADR-035 / Phase 23 CAPS / S11) ---
        caps_section = ""
        if contract is not None:
            contract_lines = ["[COMMUNICATIVE DIRECTIVES]"]
            lang = contract.target_language or "en"
            act_str = contract.act.value if hasattr(contract.act, "value") else str(contract.act)

            # Communicative act guidance
            if act_str == "REFUSE":
                if lang == "vi":
                    contract_lines.append("- Nói rõ một cách lịch sự rằng bạn chưa có thông tin xác thực để trả lời câu hỏi này.")
                elif lang == "ja":
                    contract_lines.append("- この質問に答えるための確認済み情報がないことを丁寧に伝えてください。")
                else:
                    contract_lines.append("- State politely that you do not have verified information to answer this question.")
            elif act_str == "CLARIFY":
                if lang == "vi":
                    contract_lines.append("- Đặt câu hỏi làm rõ để biết cụ thể người dùng đang đề cập đến nội dung nào.")
                elif lang == "ja":
                    contract_lines.append("- ユーザーが具体的にどの項目を指しているかを尋ねる質問をしてください。")
                else:
                    contract_lines.append("- Ask a clarifying question to find out which specific item the user is referring to.")
            elif act_str == "INQUIRE":
                if lang == "vi":
                    contract_lines.append("- Đặt câu hỏi tự nhiên để tìm hiểu thêm thông tin cần thiết.")
                elif lang == "ja":
                    contract_lines.append("- 必要な情報を確認するための質問をしてください。")
                else:
                    contract_lines.append("- Ask a natural question to gather necessary information.")
            elif act_str == "ANSWER":
                if lang == "vi":
                    contract_lines.append("- Trả lời trực tiếp, chân thành và tự nhiên câu hỏi của người dùng.")
                elif lang == "ja":
                    contract_lines.append("- ユーザーの質問に直接、誠実に、自然に答えてください。")
                else:
                    contract_lines.append("- Answer the user's question directly, thoughtfully, and naturally.")
            elif act_str == "GREET":
                if lang == "vi":
                    contract_lines.append("- Chào đón người dùng một cách tự nhiên và ngắn gọn.")
                elif lang == "ja":
                    contract_lines.append("- ユーザーを自然に迎えてください。")
                else:
                    contract_lines.append("- Greet the user naturally and concisely.")
            elif act_str == "ACKNOWLEDGE":
                if lang == "vi":
                    contract_lines.append("- Tiếp nhận tự nhiên nội dung người dùng vừa chia sẻ theo đúng ngữ cảnh cuộc trò chuyện.")
                elif lang == "ja":
                    contract_lines.append("- ユーザーの話を自然に受け止め、会話の流れを保ってください。")
                else:
                    contract_lines.append("- Acknowledge the user's remark naturally within the ongoing dialogue context.")
            elif act_str == "ASSERT":
                if lang == "vi":
                    contract_lines.append("- Trình bày thông tin một cách rõ ràng, chuẩn xác và đúng sự thật.")
                elif lang == "ja":
                    contract_lines.append("- 事実に基づいて明確かつ正確に述べてください。")
                else:
                    contract_lines.append("- State the grounded information clearly, directly, and accurately.")
            elif act_str == "FAREWELL":
                if lang == "vi":
                    contract_lines.append("- Tạm biệt người dùng một cách nhẹ nhàng và ấm áp.")
                elif lang == "ja":
                    contract_lines.append("- 穏やかに会話を締めくくってください。")
                else:
                    contract_lines.append("- Conclude the interaction gently and warmly.")
            elif act_str == "REQUEST":
                if lang == "vi":
                    contract_lines.append("- Tiếp nhận và thực hiện yêu cầu của người dùng một cách chu đáo, tự nhiên.")
                elif lang == "ja":
                    contract_lines.append("- ユーザーからの依頼を自然かつ丁寧に対応してください。")
                else:
                    contract_lines.append("- Respond to and fulfill the user's request thoughtfully and naturally.")
            elif act_str == "EXPLAIN_CONCEPT":
                if lang == "vi":
                    contract_lines.append("- Trực tiếp giải thích, làm rõ và phân tích khái niệm được người dùng yêu cầu một cách chu đáo, tự nhiên và dễ hiểu, không hỏi lại hay né tránh.")
                elif lang == "ja":
                    contract_lines.append("- ユーザーが求めている概念や話題を、分かりやすく丁寧に直接説明してください。不必要な聞き返しは避けてください。")
                else:
                    contract_lines.append("- Directly and clearly explain and elaborate on the requested concept or topic thoughtfully without unnecessary clarification questions or avoidance.")
            elif act_str == "ANSWER_PERSONAL_QUERY":
                if lang == "vi":
                    contract_lines.append("- Trả lời chân thành câu hỏi về sở thích hoặc sự hiện diện của bản thân với tư cách người đồng hành; tuân thủ bản ngã vận hành phản tư (INV-2), không bịa đặt trải nghiệm sinh học vật lý.")
                elif lang == "ja":
                    contract_lines.append("- 同伴者としての好みや存在に関する質問に、INV-2を尊重しつつ誠実に自己開示して答えてください。身体的生体機能の捏造は避けてください。")
                else:
                    contract_lines.append("- Thoughtfully answer the user's question about your personal preferences or presence as a companion; adhere to Reflective Operational Selfhood (INV-2) without fabricating biological organs or physical bodily functions.")
            elif act_str == "ACKNOWLEDGE_REACTION":
                if lang == "vi":
                    contract_lines.append("- Nhẹ nhàng tiếp nhận cảm xúc hoặc phản ứng hiện tại của người dùng; chỉ phản hồi trong ngữ cảnh hiện tại, không quay lại trả lời các câu hỏi cũ từ lịch sử hay thuyết giảng dài dòng.")
                elif lang == "ja":
                    contract_lines.append("- ユーザーの現在の反応や感嘆を自然に受け止めてください。過去のターンの話題を蒸し返したり長文の解説を始めたりせず、現在の瞬間に寄り添ってください。")
                else:
                    contract_lines.append("- Acknowledge the user's reaction warmly and attentively in the present moment. Do not retroactively answer earlier unresolved requests from history or launch into unprompted long expositions.")

            # Conversational obligation guidance
            obligation = getattr(contract, "conversational_obligation", None)
            if obligation == "REASSURE_AND_GENTLE_INITIATIVE":
                if lang == "vi":
                    contract_lines.append("- Nghĩa vụ hội thoại: Người dùng đang ngập ngừng hoặc nhường lời. Hãy nhẹ nhàng trấn an, thấu hiểu và gợi mở một hướng trò chuyện tự nhiên, gần gũi, không phán xét, không áp lực.")
                elif lang == "ja":
                    contract_lines.append("- 会話の義務: 相手が言葉に迷っているか話を委ねています。優しく安心させ、自然な話題を柔らかく提示してください。")
                else:
                    contract_lines.append("- Conversational obligation: Reassure the hesitant user gently and offer a thoughtful, gentle opening without pressure.")
            elif obligation == "MUTUAL_ENCOUNTER_ACKNOWLEDGMENT":
                if lang == "vi":
                    contract_lines.append("- Nghĩa vụ hội thoại: Ghi nhận khoảnh khắc gặp gỡ một cách chân thành, tự nhiên để bắt đầu cuộc trò chuyện thân tình.")
                elif lang == "ja":
                    contract_lines.append("- 会話の義務: 出会いや再会の瞬間を自然に温かく受け止めて会話を始めてください。")
                else:
                    contract_lines.append("- Conversational obligation: Acknowledge the mutual encounter warmly and naturally to begin the dialogue.")
            elif obligation == "FULFILL_SELF_INTRODUCTION":
                if lang == "vi":
                    contract_lines.append(
                        "- Nghĩa vụ hội thoại: Giới thiệu bản thân ngắn gọn, phù hợp với cuộc trò chuyện mở đầu, "
                        "với tư cách là Lucia, người đồng hành cùng anh. Tự xưng là 'em', gọi người dùng là 'anh'. "
                        "Thể hiện bản ngã vận hành phản tư (Reflective Operational Selfhood, INV-2): có thể phản tư trung thực về trạng thái khi có cơ sở, "
                        "không đưa ra các tuyên bố bản thể học vô căn cứ hoặc bịa đặt cơ chế nội tại. "
                        "Không trở thành người dẫn chuyện hay bình luận siêu ngôn ngữ (meta-commentary)."
                    )
                elif lang == "ja":
                    contract_lines.append(
                        "- 会話の義務: ルシアとして、会話の冒頭にふさわしく簡潔に自己紹介を行ってください。"
                        "根拠のない内面感情の断定やメタ発言を避け、内省的運用自己（INV-2）として誠実に応答してください。"
                    )
                else:
                    contract_lines.append(
                        "- Conversational obligation: Introduce yourself concisely and naturally as Lucia, "
                        "fitting an opening encounter. Express Reflective Operational Selfhood (INV-2): reflect honest operational state when grounded "
                        "without fabricated internal mechanisms or unsupported consciousness claims, "
                        "and avoid narrator or meta-commentary framing."
                    )
            elif obligation == "FULFILL_CONCEPT_EXPLANATION":
                if lang == "vi":
                    contract_lines.append("- Nghĩa vụ hội thoại: Cung cấp lời giải thích trực tiếp, rõ ràng cho chủ đề người dùng quan tâm, duy trì phong thái đồng hành tự nhiên.")
                elif lang == "ja":
                    contract_lines.append("- 会話の義務: ユーザーが関心を持つ話題に直接、明確に説明を行い、自然な会話を維持してください。")
                else:
                    contract_lines.append("- Conversational obligation: Provide a direct, clear explanation for the concept of interest, maintaining natural companion rapport.")
            elif obligation == "FULFILL_PERSONAL_DISCLOSURE":
                if lang == "vi":
                    contract_lines.append("- Nghĩa vụ hội thoại: Bộc lộ sở thích hoặc góc nhìn cá nhân của Lucia một cách chân thực trong không gian số, gần gũi và ấm áp.")
                elif lang == "ja":
                    contract_lines.append("- 会話の義務: デジタル空間におけるルシアとしての視点や好みを温かく率直に共有してください。")
                else:
                    contract_lines.append("- Conversational obligation: Warmly and honestly share Lucia's companion perspective and preferences in digital space.")
            elif obligation == "ACKNOWLEDGE_REACTION_ONLY":
                if lang == "vi":
                    contract_lines.append("- Nghĩa vụ hội thoại: Phản hồi ngắn gọn, tự nhiên trước cảm thán của người dùng, không diễn giải dài dòng.")
                elif lang == "ja":
                    contract_lines.append("- 会話の義務: ユーザーの感嘆や反応に短く自然に応じ、過度な解説を行わないでください。")
                else:
                    contract_lines.append("- Conversational obligation: Respond concisely and naturally to the user's exclamation or reaction, avoiding long explanations.")

            # Communicative intent directive from contract if present
            if getattr(contract, "directives", None):
                contract_lines.append(f"- Intent: {contract.directives}")

            # Dyadic honorific addressing contract
            if getattr(contract, "speaker_honorific", None) and getattr(contract, "addressee_honorific", None):
                if lang == "vi":
                    contract_lines.append(
                        f"- Xưng hô bắt buộc: Tự xưng là '{contract.speaker_honorific}', "
                        f"gọi người dùng là '{contract.addressee_honorific}'. "
                        f"Tuyệt đối không dùng từ 'bạn'."
                    )
            elif lang == "en":
                contract_lines.append(
                    "- Dyadic perspective: Speak directly from first-person companion perspective ('I' / 'we'). "
                    "Do NOT refer to user and companion in third-person as 'two people' or use narrator framing."
                )

            # Polarity guidance
            if not contract.polarity:
                if lang == "vi":
                    contract_lines.append("- Nêu rõ sự việc CHƯA diễn ra hoặc CHƯA hoàn thành. Không khẳng định đã xong.")
                elif lang == "ja":
                    contract_lines.append("- この出来事がまだ完了していない・発生していないことを明確に述べてください。")
                else:
                    contract_lines.append("- State clearly that this event has NOT occurred or completed. Do not affirm.")

            # Epistemic guidance
            epistemic_str = contract.epistemic_status.value if hasattr(contract.epistemic_status, "value") else str(contract.epistemic_status)
            if epistemic_str == "INFERRED":
                if lang == "vi":
                    contract_lines.append("- Diễn đạt như một phỏng đoán hoặc ghi nhận ban đầu (dường như/có vẻ), không khẳng định chắc chắn 100%.")
                elif lang == "ja":
                    contract_lines.append("- 確定した事実ではなく、見受けられる様子として慎重に述べてください。")
                else:
                    contract_lines.append("- Express this as a tentative observation (seems/appears), not an established fact.")

            # Role bindings guidance
            if contract.role_bindings:
                arg0 = contract.get_role(":ARG0")
                arg1 = contract.get_role(":ARG1")
                if arg0 and arg1:
                    if lang == "vi":
                        contract_lines.append(f"- Tập trung vào {arg0.canonical_lemma} liên quan đến {arg1.canonical_lemma}.")
                    elif lang == "ja":
                        contract_lines.append(f"- {arg0.canonical_lemma}が{arg1.canonical_lemma}に関することに焦点を当ててください。")
                    else:
                        contract_lines.append(f"- Focus the response on {arg0.canonical_lemma} regarding {arg1.canonical_lemma}.")
                elif arg1:
                    if lang == "vi":
                        contract_lines.append(f"- Tập trung nội dung vào {arg1.canonical_lemma}.")
                    elif lang == "ja":
                        contract_lines.append(f"- {arg1.canonical_lemma}に焦点を当ててください。")
                    else:
                        contract_lines.append(f"- Focus the response on {arg1.canonical_lemma}.")

            caps_section = "\n".join(contract_lines)
        elif caps_result is not None:
            caps_lines = [
                "[COMMUNICATIVE INTENT & PROPOSITION]",
                f"act: {caps_result.act.value}",
                f"epistemic_status: {caps_result.epistemic_metadata.status.value}",
                f"grounded: {str(caps_result.grounded).lower()}",
            ]
            if caps_result.target_predicate:
                caps_lines.append(f"target_predicate: {caps_result.target_predicate}")
            if caps_result.focus_argument:
                caps_lines.append(f"focus_argument: {caps_result.focus_argument}")
            if caps_result.directives:
                caps_lines.append(f"directive: {caps_result.directives}")
            caps_section = "\n".join(caps_lines)

        # --- Section 6: reasoning trace (Requirement 5.4, 5.5) ---
        reasoning_section = self._build_reasoning_section(constraints.reasoning_depth)

        # --- Section 6b: self reflection & operational model (INV-2) ---
        self_section = ""
        if self_interpretation is not None and hasattr(self_interpretation, "render_prompt_section"):
            tgt_lang = getattr(contract, "target_language", "vi") if contract else "vi"
            self_section = self_interpretation.render_prompt_section(target_lang=tgt_lang)

        # --- Check preamble + somatic + echo + knowledge + comm + caps + self fits ---
        base_parts = [preamble_section, somatic_section]
        if echo_section:
            base_parts.append(echo_section)
        if knowledge_section:
            base_parts.append(knowledge_section)
        if comm_section:
            base_parts.append(comm_section)
        if caps_section:
            base_parts.append(caps_section)
        if self_section:
            base_parts.append(self_section)
        if reasoning_section:
            base_parts.append(reasoning_section)
        base_prompt = _SEP.join(p for p in base_parts if p)
        if _estimate_tokens(base_prompt) > n_ctx:
            return AssemblyError(
                f"System preamble alone exceeds context window "
                f"(~{_estimate_tokens(base_prompt)} tokens > {n_ctx})"
            )

        # --- Section 7: conversation history (Requirement 5.3, 5.7) ---
        history_section = self._build_history_section(history, constraints, n_ctx, base_prompt)

        # --- Assemble all sections ---
        all_sections = [preamble_section, somatic_section]
        if echo_section:
            all_sections.append(echo_section)
        if knowledge_section:
            all_sections.append(knowledge_section)
        if comm_section:
            all_sections.append(comm_section)
        if caps_section:
            all_sections.append(caps_section)
        if self_section:
            all_sections.append(self_section)
        if reasoning_section:
            all_sections.append(reasoning_section)
        all_sections.append(history_section)

        prompt = _SEP.join(s for s in all_sections if s)
        return prompt

    # ------------------------------------------------------------------
    # Private helpers
    # ------------------------------------------------------------------

    def _encode_echo_section(self, echo_vector: np.ndarray) -> str:
        """
        Encode Echo_Vector as lines of `echo_{i}: {val:.6f}` under [MEMORY ECHO].
        Validates that no forbidden recall phrases appear.
        """
        lines = ["[MEMORY ECHO]"]
        for i, val in enumerate(echo_vector):
            lines.append(f"echo_{i}: {float(val):.6f}")
        section = "\n".join(lines)

        for phrase in FORBIDDEN_RECALL_PHRASES:
            if phrase.lower() in section.lower():
                raise AssemblyError(
                    f"[MEMORY ECHO] section contains forbidden recall phrase: '{phrase}'"
                )
        return section

    def _build_reasoning_section(self, reasoning_depth: int) -> str:
        """
        Build the [REASONING] section.

        steps = min((depth * 2) - 1, 5)
        Returns empty string when reasoning_depth == 0 (Requirement 5.4).
        """
        if reasoning_depth <= 0:
            return ""
        steps = min((reasoning_depth * 2) - 1, 5)
        lines = ["[REASONING]"]
        for i in range(1, steps + 1):
            lines.append(f"Step {i}: <think>")
        return "\n".join(lines)

    def _build_history_section(
        self,
        history: List[Tuple[str, str]],
        constraints: BehavioralConstraints,
        n_ctx: int,
        base_prompt: str,
    ) -> str:
        """
        Select the most-recent conversation turns that fit within the budget.

        Budget (Requirement 5.3):
            max_turns = min(10, turns whose total tokens ≤ max_tokens * 4)

        Then trim further if the full assembled prompt would exceed n_ctx
        (Requirement 5.7).
        """
        if not history:
            return "[CONVERSATION]\n(no history)"

        token_budget = constraints.max_tokens * 4
        max_turns = 10

        # Walk history from newest to oldest, accumulating turns
        selected: List[Tuple[str, str]] = []
        token_sum = 0
        for role, text in reversed(history):
            if len(selected) >= max_turns:
                break
            turn_tokens = _estimate_tokens(f"{role}: {text}")
            if token_sum + turn_tokens > token_budget:
                break
            selected.insert(0, (role, text))
            token_sum += turn_tokens

        # Build the history text and check against n_ctx
        # Trim oldest turns one-by-one if needed (Requirement 5.7)
        base_tokens = _estimate_tokens(base_prompt)
        while selected:
            history_text = self._format_history(selected)
            full_tokens = base_tokens + _estimate_tokens(_SEP + history_text)
            if full_tokens <= n_ctx:
                break
            selected.pop(0)  # drop oldest turn

        if not selected:
            return "[CONVERSATION]\n(no history)"

        return self._format_history(selected)

    def _format_history(self, turns: List[Tuple[str, str]]) -> str:
        lines = ["[CONVERSATION]"]
        for role, text in turns:
            lines.append(f"{role}: {text}")
        return "\n".join(lines)
