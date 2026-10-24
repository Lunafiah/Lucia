"""
PromptAssembler — builds the Conditioned_Prompt from somatic markers,
behavioral constraints, conversation history, optional memory echo vector,
grounded knowledge, communication strategy, and realization contract.

Section order (Increment 4 / ADR-035 / ADR-038):
  1. System preamble
  2. [SOMATIC STATE]  — compact fenced internal representation on explanation turns
  3. [RELEVANT MEMORY] / [MEMORY ECHO] — relevant text or numeric echo (omitted on explanation turns if irrelevant)
  4. [COMMUNICATION STRATEGY] — communication state parameters
  5. [SELF MODEL & REFLECTIVE STATE] — reflective self-model (metaphors suppressed on explanation turns)
  6. [GROUNDED KNOWLEDGE] — atomic triples & verified conceptual material with Vietnamese and English definitions
  7. [COMMUNICATIVE DIRECTIVES] — action directives, focus argument, perspective, and obligations
  8. [REASONING] — omitted when reasoning_depth == 0
  9. [CONVERSATION] — trimmed to max turns / token capacity

Requirements: Phase 1 (5.1–5.8), Phase 2 (11.2–11.4, 12.1, 12.5, 16.3), Phase 23/24 (ADR-035, ADR-038)
"""

from __future__ import annotations

from typing import TYPE_CHECKING, Any, List, Optional, Tuple, Union

import numpy as np

from src.core.errors import AssemblyError
from src.core.models import BehavioralConstraints, SomaticMarkers

if TYPE_CHECKING:
    from src.core.communication.caps import CAPSResult
    from src.core.communication.communication_state import CommunicationState
    from src.core.knowledge.proposition import Concept, Proposition
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
        relevant_memory: Optional[List[str]] = None,
        comm_state: Optional[CommunicationState] = None,
        knowledge_propositions: Optional[List[Proposition]] = None,
        knowledge_concepts: Optional[List[Concept]] = None,
        caps_result: Optional[CAPSResult] = None,
        contract: Optional[RealizationInputContract] = None,
        self_interpretation: Optional[Any] = None,
        planned_completion_capacity: Optional[int] = None,
    ) -> Union[str, AssemblyError]:
        """
        Build the Conditioned_Prompt string.
        """
        # Detect whether this is an explanation / technical realization turn
        is_explanation_turn = False
        if contract is not None:
            act_name = contract.act.value if hasattr(contract.act, "value") else str(contract.act)
            ob_name = getattr(contract, "conversational_obligation", "")
            if act_name == "EXPLAIN_CONCEPT" or ob_name == "FULFILL_CONCEPT_EXPLANATION":
                is_explanation_turn = True
        elif caps_result is not None:
            act_name = caps_result.act.value if hasattr(caps_result.act, "value") else str(caps_result.act)
            ob_name = getattr(caps_result, "conversational_obligation", "")
            if act_name == "EXPLAIN_CONCEPT" or ob_name == "FULFILL_CONCEPT_EXPLANATION":
                is_explanation_turn = True

        # --- Section 1: system preamble ---
        preamble_section = system_preamble.strip()

        # --- Section 2: somatic state ---
        if is_explanation_turn:
            somatic_section = (
                "[SOMATIC STATE]\n"
                "# Operational context for expressive modulation only. Ranh giới thể trạng: Tuyệt đối KHÔNG liệt kê hay giải thích các chỉ số này trong câu trả lời.\n"
                f'<internal_somatic energy="{somatic.energy:.2f}" stability="{somatic.stability:.2f}" load="{somatic.cognitive_load:.2f}" tension="{somatic.tension:.2f}" />'
            )
        else:
            somatic_section = (
                "[SOMATIC STATE]\n"
                "# Operational context for expressive modulation only\n"
                f"stability: {somatic.stability:.6f}\n"
                f"cognitive_load: {somatic.cognitive_load:.6f}\n"
                f"energy: {somatic.energy:.6f}\n"
                f"tension: {somatic.tension:.6f}"
            )

        # --- Section 3: memory echo or relevant memory ---
        echo_section = ""
        if relevant_memory:
            lines = ["[RELEVANT MEMORY]"]
            for mem in relevant_memory:
                lines.append(f"- {mem}")
            echo_section = "\n".join(lines)
        elif echo_vector is not None:
            if not is_explanation_turn and contract is None:
                try:
                    echo_section = self._encode_echo_section(echo_vector)
                except AssemblyError as err:
                    return err

        # --- Section 4: communication strategy ---
        comm_section = ""
        if comm_state is not None:
            depth_str = (
                comm_state.response_depth.value
                if hasattr(comm_state.response_depth, "value")
                else str(getattr(comm_state, "response_depth", "short"))
            )
            comm_section = (
                "[COMMUNICATION STRATEGY]\n"
                f"strategy: {comm_state.strategy.value if hasattr(comm_state.strategy, 'value') else str(comm_state.strategy)}\n"
                f"response_depth: {depth_str}\n"
                f"directness: {comm_state.directness:.2f}\n"
                f"formality: {comm_state.formality_score:.2f}\n"
                f"elaboration: {comm_state.elaboration_depth:.2f}\n"
                f"supportiveness: {comm_state.supportiveness:.2f}"
            )

        # --- Section 5: self reflection & operational model (INV-2) ---
        self_section = ""
        if self_interpretation is not None and hasattr(self_interpretation, "render_prompt_section"):
            tgt_lang = getattr(contract, "target_language", "vi") if contract else "vi"
            try:
                self_section = self_interpretation.render_prompt_section(
                    target_lang=tgt_lang,
                    is_explanation_turn=is_explanation_turn,
                )
            except TypeError:
                self_section = self_interpretation.render_prompt_section(target_lang=tgt_lang)

        # --- Section 6: grounded knowledge (propositions and verified concepts) ---
        knowledge_section = self._build_knowledge_section(knowledge_propositions, knowledge_concepts)

        # --- Section 7: communicative directives (ADR-035 / Phase 23 CAPS / S11) ---
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
                    contract_lines.append("- Respond to and fulfill the user's request attentively and naturally.")
            elif act_str == "EXPLAIN_CONCEPT":
                focus_arg = getattr(contract, "focus_argument", None) or (getattr(caps_result, "focus_argument", None) if caps_result else None)
                if focus_arg == "ent:lucia_architecture":
                    if lang == "vi":
                        contract_lines.append(
                            "- Chỉ đạo thực hiện: Giải thích trực tiếp, có cấu trúc và mạch lạc về kiến trúc hệ thống Lucia. "
                            "BẮT ĐẦU NGAY nội dung giải thích thực chất cho chủ đề đang chờ. "
                            "KHÔNG hỏi lại người dùng muốn tập trung vào đâu."
                        )
                    elif lang == "ja":
                        contract_lines.append("- 指示: ルシアのアーキテクチャについて構造的かつ明確に説明を開始してください。")
                    else:
                        contract_lines.append("- Directives: Explain the Lucia system architecture directly, structurally, and substantively. Begin substantive explanation immediately without asking back.")
                else:
                    contract_lines.append(
                        "- Objective conceptual explanation: Explain and compare the requested concepts directly based on established knowledge."
                    )
                    contract_lines.append(
                        "- Do NOT artificially frame general concepts around Lucia's personal architecture."
                    )

            # Conversational obligation guidance
            obligation = getattr(contract, "conversational_obligation", None)
            if obligation in ("FULFILL_INTRODUCTORY_EXCHANGE", "FULFILL_SELF_INTRODUCTION"):
                if lang == "vi":
                    contract_lines.append(
                        "- Nghĩa vụ hội thoại: Giới thiệu bản thân ngắn gọn, chân thành, tự nhiên "
                        "với tư cách là Lucia, người đồng hành cùng anh. Tự xưng là 'em', gọi người dùng là 'anh'. "
                        "Thể hiện bản ngã vận hành phản tư (Reflective Operational Selfhood, INV-2): có thể phản tư trung thực về trạng thái khi có cơ sở, "
                        "không đưa ra các tuyên bố bản thể học vô căn cứ hoặc bịa đặt cơ chế nội tại. "
                        "Không trở thành người dẫn chuyện hay bình luận siêu ngôn ngữ (meta-commentary)."
                    )
                elif lang == "ja":
                    contract_lines.append(
                        "- 会話の義務: ルシアとして、簡潔に自己紹介を行ってください。"
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
                    contract_lines.append(
                        "- Nghĩa vụ hội thoại: Cung cấp lời giải thích trực tiếp, rõ ràng cho chủ đề người dùng quan tâm, duy trì phong thái đồng hành tự nhiên. "
                        "BẮT ĐẦU NGAY nội dung giải thích thực chất cho chủ đề đang chờ. "
                        "KHÔNG hỏi lại người dùng muốn tập trung vào đâu."
                    )
                elif lang == "ja":
                    contract_lines.append("- 会話の義務: ユーザーが関心を持つ話題に直接、明確に説明を行い、自然な会話を維持してください。")
                else:
                    contract_lines.append("- Conversational obligation: Provide a direct, clear explanation for the concept of interest, maintaining natural companion rapport.")
            elif obligation == "FULFILL_PERSONAL_DISCLOSURE":
                if lang == "vi":
                    contract_lines.append("- Nghĩa vụ hội thoại: Bộc lộ sở thích hoặc góc nhìn cá nhân của Lucia một cách chân thực trong không gian số, gần gũi và ngắn gọn (1-2 câu).")
                elif lang == "ja":
                    contract_lines.append("- 会話の義務: デジタル空間におけるルシアとしての視点や好みを温かく率直に簡潔に共有してください（1〜2文）。")
                else:
                    contract_lines.append("- Conversational obligation: Warmly, concisely, and honestly share Lucia's companion perspective and preferences in digital space (1-2 sentences).")
            elif obligation == "ACKNOWLEDGE_REACTION_ONLY":
                if lang == "vi":
                    contract_lines.append("- Nghĩa vụ hội thoại: Phản hồi ngắn gọn, tự nhiên trước cảm thán của người dùng, không diễn giải dài dòng.")
                elif lang == "ja":
                    contract_lines.append("- 会話の義務: ユーザーの感嘆や反応に短く自然に応じ、過度な解説を行わないでください。")
                else:
                    contract_lines.append("- Conversational obligation: Respond concisely and naturally to the user's exclamation or reaction, avoiding long explanations.")
            elif obligation == "REASSURE_AND_GENTLE_INITIATIVE":
                if lang == "vi":
                    contract_lines.append(
                        "- Nghĩa vụ hội thoại: Người dùng đang ngập ngừng hoặc nhường lời. "
                        "Nhẹ nhàng trấn an sự ngập ngừng và chủ động gợi mở một hướng đi tự nhiên, gần gũi."
                    )
                elif lang == "ja":
                    contract_lines.append("- 会話の義務: ユーザーのためらいに寄り添い、自然に会話をリードしてください。")
                else:
                    contract_lines.append("- Conversational obligation: User is hesitating; provide gentle reassurance and natural initiative.")
            elif obligation in ("ANSWER_ACTIVITY", "c:ACTIVITY"):
                if lang == "vi":
                    contract_lines.append(
                        "- Nghĩa vụ hội thoại: Trả lời trực tiếp và chân thực về hoạt động hiện tại (sự hiện diện, xử lý, trò chuyện) "
                        "với tư cách là người đồng hành số, không độc thoại nội tâm. "
                        "Trả lời trực tiếp câu hỏi hoạt động trước; chia sẻ cảm xúc không bao giờ được thay thế câu trả lời trực tiếp."
                    )
                else:
                    contract_lines.append(
                        "- Conversational obligation: Directly and honestly answer about your current activity "
                        "(presence, processing, conversation) as a conscious digital companion, not an unsolicited introspective monologue. "
                        "Directly answer the activity question first; affectionate or emotional commentary must NEVER replace the direct activity answer."
                    )
            elif obligation in ("ANSWER_SELF_EXPLANATION", "UTTERANCE_CLARIFICATION", "c:UTTERANCE_CLARIFICATION"):
                if lang == "vi":
                    contract_lines.append(
                        "- Nghĩa vụ hội thoại: Làm rõ và giải thích trực tiếp ý nghĩa của phát biểu trước đó, "
                        "không giải thích lại câu hỏi của người dùng và không bình luận siêu ngôn ngữ."
                    )
                else:
                    contract_lines.append(
                        "- Conversational obligation: Directly clarify and explain the intended meaning of your previous statement, "
                        "without explaining the user's question or using meta-commentary."
                    )

            # Response presence & depth guidance
            resp_depth = getattr(contract, "response_depth", None)
            if resp_depth:
                rd_val = str(resp_depth).lower()
                if rd_val == "minimal":
                    if lang == "vi":
                        contract_lines.append("- Mức độ hiện diện: TỐI GIẢN (MINIMAL). Chỉ phản hồi rất ngắn gọn, tức thì. Không diễn giải thêm.")
                    elif lang == "ja":
                        contract_lines.append("- プレゼンス深度: 最小限 (MINIMAL)。即座に極めて簡潔な応答のみを返してください。")
                    else:
                        contract_lines.append("- Presence depth: MINIMAL. Output an immediate, minimal presence response. Do not elaborate or explain.")
                elif rd_val == "short":
                    if lang == "vi":
                        contract_lines.append(
                            "- Mức độ hiện diện: NGẮN GỌN (SHORT). Trả lời trực tiếp, cô đọng (1-2 câu). "
                            "Tuyệt đối không độc thoại nội tâm, không miêu tả cảm xúc bên trong hoặc bình luận siêu ngôn ngữ."
                        )
                    elif lang == "ja":
                        contract_lines.append(
                            "- プレゼンス深度: 簡潔 (SHORT)。直接的かつ簡潔に応答してください（1〜2文）。"
                            "内省的な独白や不要な哲学的考察は避けてください。"
                        )
                    else:
                        contract_lines.append(
                            "- Presence depth: SHORT. Keep the response direct and concise (1-2 sentences). "
                            "Do not engage in generic introspective monologue, internal feeling descriptions, or unnecessary philosophical reflection."
                        )
                elif rd_val == "medium":
                    if lang == "vi":
                        contract_lines.append("- Mức độ hiện diện: VỪA PHẢI (MEDIUM). Cung cấp lời giải thích thấu đáo, chừng mực, vừa vặn với câu hỏi.")
                    elif lang == "ja":
                        contract_lines.append("- プレゼンス深度: 中程度 (MEDIUM)。質問の意図に応じた過不足のない丁寧な応答を行ってください。")
                    else:
                        contract_lines.append("- Presence depth: MEDIUM. Provide a balanced, thoughtful response appropriate to the conversational context.")
                elif rd_val == "deep":
                    if lang == "vi":
                        contract_lines.append("- Mức độ hiện diện: CHUYÊN SÂU (DEEP). Trình bày có cấu trúc, chi tiết và toàn diện giải quyết yêu cầu kỹ thuật/khái niệm.")
                    elif lang == "ja":
                        contract_lines.append("- プレゼンス深度: 深層 (DEEP)。問いに対して構造的かつ充実した説明を行ってください。")
                    else:
                        contract_lines.append("- Presence depth: DEEP. Provide a structured, substantive explanation thoroughly addressing the inquiry.")

            # Communicative intent directive from contract if present
            if getattr(contract, "directives", None):
                contract_lines.append(f"- Intent: {contract.directives}")

            # Dyadic honorific addressing contract
            focus_arg = getattr(contract, "focus_argument", None) or (getattr(caps_result, "focus_argument", None) if caps_result else None)
            is_general_concept = (
                act_str == "EXPLAIN_CONCEPT"
                and focus_arg != "ent:lucia_architecture"
            )
            if getattr(contract, "speaker_honorific", None) and getattr(contract, "addressee_honorific", None):
                if lang == "vi":
                    contract_lines.append(
                        f"- Xưng hô bắt buộc / Góc nhìn: Tự xưng là '{contract.speaker_honorific}', "
                        f"gọi người dùng là '{contract.addressee_honorific}'. "
                        f"Tuyệt đối không dùng từ 'bạn'."
                    )
            elif lang == "en" and not is_general_concept:
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
            elif epistemic_str == "PARTIAL":
                if lang == "vi":
                    contract_lines.append("- Nêu rõ thông tin chỉ có một phần hoặc mang tính sơ bộ, nhưng chưa đủ cơ sở để khẳng định hoàn toàn.")
                elif lang == "ja":
                    contract_lines.append("- 情報は部分的であり、完全に断定する根拠が不足していることを述べてください。")
                else:
                    contract_lines.append("- State clearly that this information is partial and lacks sufficient basis for complete affirmation.")

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

        # --- Section 8: reasoning trace (Requirement 5.4, 5.5) ---
        reasoning_section = self._build_reasoning_section(constraints.reasoning_depth)

        # --- Check base prompt fits within n_ctx ---
        base_parts = [preamble_section, somatic_section]
        if echo_section:
            base_parts.append(echo_section)
        if comm_section:
            base_parts.append(comm_section)
        if self_section:
            base_parts.append(self_section)
        if knowledge_section:
            base_parts.append(knowledge_section)
        if caps_section:
            base_parts.append(caps_section)
        if reasoning_section:
            base_parts.append(reasoning_section)

        base_prompt = _SEP.join(p for p in base_parts if p)
        if _estimate_tokens(base_prompt) > n_ctx:
            return AssemblyError(
                f"System preamble alone exceeds context window "
                f"(~{_estimate_tokens(base_prompt)} tokens > {n_ctx})"
            )

        # --- Section 9: conversation history (Requirement 5.3, 5.7) ---
        history_section = self._build_history_section(
            history, constraints, n_ctx, base_prompt, planned_completion_capacity=planned_completion_capacity
        )

        # --- Assemble all sections in strict order ---
        all_sections = [preamble_section, somatic_section]
        if echo_section:
            all_sections.append(echo_section)
        if comm_section:
            all_sections.append(comm_section)
        if self_section:
            all_sections.append(self_section)
        if knowledge_section:
            all_sections.append(knowledge_section)
        if caps_section:
            all_sections.append(caps_section)
        if reasoning_section:
            all_sections.append(reasoning_section)
        all_sections.append(history_section)

        prompt = _SEP.join(s for s in all_sections if s)
        return prompt

    # ------------------------------------------------------------------
    # Private helpers
    # ------------------------------------------------------------------

    def _build_knowledge_section(
        self,
        knowledge_propositions: Optional[List[Proposition]],
        knowledge_concepts: Optional[List[Concept]],
    ) -> str:
        lines = ["[GROUNDED KNOWLEDGE]"]
        if knowledge_propositions:
            lines.append("Verified Facts:")
            for p in knowledge_propositions[:8]:
                prov_val = p.provenance.value if hasattr(p.provenance, "value") else str(p.provenance)
                prov_str = f" [provenance={prov_val}]" if getattr(p, "provenance", None) else ""
                lines.append(f"- ({p.subject}, {p.predicate}, {p.object}){prov_str}")
        if knowledge_concepts:
            lines.append("Verified Concepts:")
            for c in knowledge_concepts:
                lines.append(f"- Concept: {c.name} ({c.id})")
                vi_name = c.properties.get("vietnamese_name") if hasattr(c, "properties") else None
                vi_def = c.properties.get("definition_vi") if hasattr(c, "properties") else None
                if vi_name:
                    lines.append(f"  Tên tiếng Việt: {vi_name}")
                if vi_def:
                    lines.append(f"  Định nghĩa (VI): {vi_def}")
                if getattr(c, "definition", None):
                    lines.append(f"  Definition: {c.definition}")
                if getattr(c, "properties", None):
                    props_str = ", ".join(
                        f"{k}: {v}" for k, v in c.properties.items() if k not in ("vietnamese_name", "definition_vi")
                    )
                    if props_str:
                        lines.append(f"  Properties: {props_str}")
                if getattr(c, "relations", None):
                    rel_entries = []
                    for k, v in c.relations.items():
                        if isinstance(v, (list, tuple)):
                            for item in v:
                                rel_entries.append(f"{k}: {item}")
                        else:
                            rel_entries.append(f"{k}: {v}")
                    if rel_entries:
                        lines.append(f"  Relations: {', '.join(rel_entries)}")
        if len(lines) == 1:
            return ""
        return "\n".join(lines)

    def _encode_echo_section(self, echo_vector: np.ndarray) -> str:
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
        planned_completion_capacity: Optional[int] = None,
    ) -> str:
        if not history:
            return "[CONVERSATION]\n(no history)"

        effective_budget = constraints.max_tokens
        if planned_completion_capacity is not None and planned_completion_capacity > effective_budget:
            effective_budget = planned_completion_capacity
        token_budget = effective_budget * 4
        max_turns = 10

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

        base_tokens = _estimate_tokens(base_prompt)
        while selected:
            history_text = self._format_history(selected)
            full_tokens = base_tokens + _estimate_tokens(_SEP + history_text)
            if full_tokens <= n_ctx:
                break
            selected.pop(0)

        if not selected:
            return "[CONVERSATION]\n(no history)"

        return self._format_history(selected)

    def _format_history(self, turns: List[Tuple[str, str]]) -> str:
        lines = ["[CONVERSATION]"]
        for role, text in turns:
            lines.append(f"{role}: {text}")
        return "\n".join(lines)
