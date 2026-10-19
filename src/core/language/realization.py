"""
src/core/language/realization.py

Realization layer utilities for voice and language alignment.
Provides deterministic realization of Japanese voice text and English text
from RealizationInputContract and knowledge representations.

Architectural Invariants:
1. Language belongs to realization, NOT cognition or semantic substrate.
2. Production voice language is CANONICALLY Japanese ('ja').
3. Production text language is CANONICALLY English ('en').
4. Multilingual input perception is admitted, but surface realization targets are:
   - Text: 'en'
   - Voice: 'ja'
5. Parallel Decoupling: Voice Japanese realizes directly from semantic/pragmatic state
   (contract & propositions) or parallel Japanese renderer.
   English text is NEVER a semantic intermediate language for Japanese voice.
"""

from __future__ import annotations

import logging
from typing import Any, Optional, Sequence

from src.core.language.contract import (
    CANONICAL_TEXT_OUTPUT_LANGUAGE,
    CANONICAL_VOICE_OUTPUT_LANGUAGE,
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
    Deterministically realize authentic Japanese voice text directly from
    the semantic/pragmatic contract and propositions for the Japanese vocal channel.

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
    user_language: str = CANONICAL_TEXT_OUTPUT_LANGUAGE,
    contract: Optional[RealizationInputContract] = None,
    known_propositions: Optional[Sequence[Any]] = None,
    japanese_voice_text: Optional[str] = None,
) -> RealizationOutput:
    """
    Construct typed RealizationOutput adhering to the Language Contract:
        text.language = target text language (canonical production: "en")
        voice.language = canonical voice language ("ja")

    Both branches realize in parallel:
    - Text branch renders the approved surface response in the target text language.
    - Voice branch renders authentic Japanese voice text directly from semantic/pragmatic state.

    Parameters
    ----------
    safe_response : str
        Approved textual response in target text language.
    user_language : str
        ISO 639-1 code of target text language (defaults to "en").
    contract : RealizationInputContract | None
        Authoritative realization contract.
    known_propositions : Sequence[Any] | None
        Grounded propositions.
    japanese_voice_text : str | None
        Optional turn-specific Japanese voice realization text.

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
        # When text itself is Japanese, voice can directly share verified Japanese prose
        voice_content = safe_response
    else:
        # Voice realizes directly from semantic/pragmatic state or parallel renderer
        if japanese_voice_text and japanese_voice_text.strip():
            voice_content = japanese_voice_text.strip()
        else:
            voice_content = realize_japanese_voice_text(contract, known_propositions)

    voice_out = VoiceRealization(
        content=voice_content,
        language=CANONICAL_VOICE_OUTPUT_LANGUAGE,
    )

    return RealizationOutput(
        text=text_out,
        voice=voice_out,
    )

