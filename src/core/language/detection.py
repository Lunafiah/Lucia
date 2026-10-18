"""
src/core/language/detection.py

Runtime language detection for surface realization input.
Deterministically classifies user active language into supported languages ('en', 'vi', 'ja').

Architectural Invariant:
Language belongs strictly to the realization boundary, NOT cognition.
"""

from __future__ import annotations

import re

# Japanese kana range: Hiragana (U+3040..U+309F) and Katakana (U+30A0..U+30FF)
_JA_KANA_REGEX = re.compile(r"[\u3040-\u309F\u30A0-\u30FF]")

# Vietnamese diacritics pattern (lower & upper case)
_VI_DIACRITICS_REGEX = re.compile(
    r"[àáảãạăằắẳẵặâầấẩẫậèéẻẽẹêềếểễệìíỉĩịòóỏõọôồốổỗộơờớởỡợùúủũụưừứửữựỳýỷỹỵđ"
    r"ÀÁẢÃẠĂẰẮẲẴẶÂẦẤẨẪẬÈÉẺẼẸÊỀẾỂỄỆÌÍỈĨỊÒÓỎÕỌÔỒỐỔỖỘƠỜỚỞỠỢÙÚỦŨỤƯỪỨỬỮỰỲÝỶỸỴĐ]"
)


def detect_active_language(text: str) -> str:
    """
    Detect the active language from user input text.
    Returns ISO 639-1 code: 'ja', 'vi', or 'en' (default fallback).

    Parameters
    ----------
    text : str
        Surface text from user input.

    Returns
    -------
    str
        'ja', 'vi', or 'en'
    """
    if not text or not text.strip():
        return "en"

    # 1. Japanese check: any Hiragana or Katakana confirms Japanese surface text
    if _JA_KANA_REGEX.search(text):
        return "ja"

    # 2. Vietnamese check: presence of characteristic Vietnamese tonal/vowel diacritics
    if _VI_DIACRITICS_REGEX.search(text):
        return "vi"

    # 3. Default fallback: English
    return "en"
