"""
src/core/language/realization.py

Realization layer utilities for voice and language alignment.
Provides deterministic realization of Japanese voice text from RealizationInputContract
and knowledge representations.

Architectural Invariants:
1. Language belongs to realization, NOT cognition.
2. Lucia's voice language is ALWAYS Japanese ('ja').
3. Voice input to TTS must be authentic Japanese realization text, never arbitrary
   English or Vietnamese text.
"""

from __future__ import annotations

import logging
from typing import Any, Optional, Sequence

from src.core.language.contract import (
    CommunicativeAct,
    EpistemicStatus,
    RealizationInputContract,
    RealizationOutput,
    TextRealization,
    VoiceRealization,
)
from src.core.language.gate import SemanticFidelityGate

logger = logging.getLogger(__name__)

# Japanese vocal realization baseline templates mapped to communicative acts
_JA_VOCAL_ACT_TEMPLATES = {
    CommunicativeAct.GREET: "こんにちは、ルシアです。お会いできて嬉しいです。",
    CommunicativeAct.FAREWELL: "それでは、またお話ししましょうね。",
    CommunicativeAct.REFUSE: SemanticFidelityGate.FALLBACK_REGISTRY["SAFE_REFUSAL"]["ja"],
    CommunicativeAct.CLARIFY: SemanticFidelityGate.FALLBACK_REGISTRY["SAFE_CLARIFICATION"]["ja"],
    CommunicativeAct.INQUIRE: SemanticFidelityGate.FALLBACK_REGISTRY["SAFE_CLARIFICATION"]["ja"],
    CommunicativeAct.ACKNOWLEDGE: SemanticFidelityGate.FALLBACK_REGISTRY["NEUTRAL_ACKNOWLEDGE"]["ja"],
}


def realize_japanese_voice_text(
    contract: Optional[RealizationInputContract],
    known_propositions: Optional[Sequence[Any]] = None,
) -> str:
    """
    Deterministically realize authentic Japanese voice text for the Japanese neural vocal channel.

    Parameters
    ----------
    contract : RealizationInputContract | None
        Authoritative communicative contract for the turn.
    known_propositions : Sequence[Any] | None
        Grounded propositions if present.

    Returns
    -------
    str
        Natural Japanese prose suitable for ja-JP-NanamiNeural and RVC VaresaGIJP synthesis.
    """
    if contract is None:
        return SemanticFidelityGate.FALLBACK_REGISTRY["NEUTRAL_ACKNOWLEDGE"]["ja"]

    # 1. Communicative Act Check: Direct mapping for explicit communicative acts
    if contract.act in _JA_VOCAL_ACT_TEMPLATES:
        return _JA_VOCAL_ACT_TEMPLATES[contract.act]

    # 2. Negation Check: If polarity is False, voice must express negation
    if not contract.polarity:
        return SemanticFidelityGate.FALLBACK_REGISTRY["SAFE_NEGATION"]["ja"]

    # 3. Epistemic Status Check: If inferred, voice must express hedging
    if contract.epistemic_status == EpistemicStatus.INFERRED:
        return SemanticFidelityGate.FALLBACK_REGISTRY["SAFE_HEDGE"]["ja"]

    # 4. Proposition grounding check if available
    if known_propositions:
        # Check predicate patterns
        p0 = known_propositions[0]
        pred = getattr(p0, "predicate", "") or ""
        pred_upper = str(pred).upper()
        if "SOLVE" in pred_upper:
            return "問題を解決しました。"
        if "ASSIST" in pred_upper or "HELP" in pred_upper:
            return "ルシアがユーザーを支援します。"
        if "READ" in pred_upper or "BOOK" in pred_upper:
            return "読書について確認しました。"

    # 5. Default affirmative/assertive baseline
    return SemanticFidelityGate.FALLBACK_REGISTRY["NEUTRAL_ACKNOWLEDGE"]["ja"]


def construct_realization_output(
    safe_response: str,
    user_language: str,
    contract: Optional[RealizationInputContract] = None,
    known_propositions: Optional[Sequence[Any]] = None,
    japanese_voice_text: Optional[str] = None,
) -> RealizationOutput:
    """
    Construct typed RealizationOutput adhering to the Language Contract:
        text.language = user_active_language
        voice.language = "ja"

    Parameters
    ----------
    safe_response : str
        Approved textual response in user's active language.
    user_language : str
        ISO 639-1 code of user active language ('en', 'vi', 'ja').
    contract : RealizationInputContract | None
        Authoritative realization contract.
    known_propositions : Sequence[Any] | None
        Grounded propositions.
    japanese_voice_text : str | None
        Optional translated/synthesized authentic Japanese text for this specific turn.

    Returns
    -------
    RealizationOutput
        Immutable realization output separating text from voice.
    """
    text_out = TextRealization(
        content=safe_response,
        language=user_language,
    )

    if user_language == "ja":
        # When user text is Japanese, voice text directly uses the verified Japanese response
        voice_content = safe_response
    else:
        # When user text is English or Vietnamese, use turn-specific Japanese voice text if available,
        # otherwise deterministically fall back to authentic communicative act template.
        if japanese_voice_text and japanese_voice_text.strip():
            voice_content = japanese_voice_text.strip()
        else:
            voice_content = realize_japanese_voice_text(contract, known_propositions)

    voice_out = VoiceRealization(
        content=voice_content,
        language="ja",
    )

    return RealizationOutput(
        text=text_out,
        voice=voice_out,
    )
