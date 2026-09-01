"""
StimulusProcessor — encodes raw UTF-8 text into a normalized Stimulus_Vector.

The vector feeds the EmotionCore's LNN ODE solver at each update step.
Dimensions:
  0  — valence  (VADER compound score, [-1.0, 1.0])
  1  — arousal  (punctuation density + cap ratio + token/sentence density, [0.0, 1.0])
  2  — semantic density (unique-token ratio mapped to [-1.0, 1.0])
  3+ — zero-padded (reserved for Phase 2 extensions)

All output values are clipped to [-1.0, 1.0].  For non-empty input the first
three dimensions are guaranteed to have |value| >= 1e-7 (Requirement 4.9).
"""

from __future__ import annotations

import re
import string
import warnings
from typing import Optional

import numpy as np
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer

from src.core.config import StimulusConfig

# ---------------------------------------------------------------------------
# Constants for arousal normalisation
# ---------------------------------------------------------------------------
# Reference: a single plain declarative sentence produces these values;
# they map to arousal = 0.0.  We cap practical max at the values below
# so the score is always in [0.0, 1.0].
_AROUSAL_PUNCT_MAX = 0.20      # punctuation chars / total chars
_AROUSAL_CAP_MAX = 0.40        # uppercase letters / total letters
_AROUSAL_TPS_REF = 15.0        # reference tokens-per-sentence for baseline
_AROUSAL_TPS_MAX = 60.0        # tokens-per-sentence that maps to 1.0

# Minimum absolute value enforced on dims 0-2 for non-empty input
_DIM_FLOOR = 1e-7

# Compiled regex for sentence splitting (split on . ! ? followed by space/end)
_SENTENCE_SPLIT = re.compile(r"(?<=[.!?])\s+")


class StimulusProcessor:
    """
    Encodes raw text into a fixed-length normalised Stimulus_Vector.

    Parameters
    ----------
    config : StimulusConfig
        vector_dim >= 3  (raised at init if violated)
        char_limit > 0   (characters processed before truncation)
    """

    def __init__(self, config: Optional[StimulusConfig] = None) -> None:
        if config is None:
            config = StimulusConfig()
        # StimulusConfig.__post_init__ already validated; re-check here for
        # defensive safety in case the object was mutated after construction.
        if not isinstance(config.vector_dim, int) or config.vector_dim < 3:
            raise ValueError(
                f"StimulusConfig.vector_dim must be an integer >= 3, "
                f"got {config.vector_dim!r}"
            )
        self._config = config
        self._analyzer = SentimentIntensityAnalyzer()

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def encode(self, text: str) -> np.ndarray:
        """
        Encode *text* into a Stimulus_Vector of shape (vector_dim,).

        Empty string → zero vector (no warning).
        String > char_limit → truncated with a warnings.warn().
        All values clipped to [-1.0, 1.0].
        For non-empty input, |dim 0|, |dim 1|, |dim 2| >= 1e-7.
        """
        N = self._config.vector_dim

        # --- Empty input ---
        if not text:
            return np.zeros(N, dtype=np.float64)

        # --- Truncation ---
        if len(text) > self._config.char_limit:
            warnings.warn(
                f"StimulusProcessor: input truncated from {len(text)} to "
                f"{self._config.char_limit} characters.",
                stacklevel=2,
            )
            text = text[: self._config.char_limit]

        vec = np.zeros(N, dtype=np.float64)

        # --- Dimension 0: valence (VADER compound, already [-1, 1]) ---
        scores = self._analyzer.polarity_scores(text)
        vec[0] = float(scores["compound"])

        # --- Dimension 1: arousal ---
        vec[1] = self._compute_arousal(text)

        # --- Dimension 2: semantic density → mapped to [-1, 1] ---
        density_01 = self._compute_semantic_density(text)   # [0.0, 1.0]
        vec[2] = density_01 * 2.0 - 1.0                     # → [-1.0, 1.0]

        # --- Enforce non-zero floor on dims 0-2 for non-empty input ---
        for i in range(3):
            if abs(vec[i]) < _DIM_FLOOR:
                # Preserve sign; if zero use positive floor
                vec[i] = _DIM_FLOOR if vec[i] >= 0 else -_DIM_FLOOR

        # --- Final clip ---
        np.clip(vec, -1.0, 1.0, out=vec)

        return vec

    # ------------------------------------------------------------------
    # Private helpers
    # ------------------------------------------------------------------

    def _compute_arousal(self, text: str) -> float:
        """
        Compute arousal in [0.0, 1.0] from three surface features:
          - punctuation density  (punct chars / total chars)
          - capitalisation ratio (uppercase letters / total letters)
          - tokens-per-sentence  (normalised against reference)
        """
        if not text:
            return 0.0

        total_chars = max(len(text), 1)

        # Punctuation density
        punct_chars = sum(1 for c in text if c in string.punctuation)
        punct_density = min(punct_chars / total_chars, _AROUSAL_PUNCT_MAX) / _AROUSAL_PUNCT_MAX

        # Capitalisation ratio (letters only)
        letters = [c for c in text if c.isalpha()]
        if letters:
            cap_ratio = min(
                sum(1 for c in letters if c.isupper()) / len(letters),
                _AROUSAL_CAP_MAX
            ) / _AROUSAL_CAP_MAX
        else:
            cap_ratio = 0.0

        # Tokens-per-sentence
        sentences = [s.strip() for s in _SENTENCE_SPLIT.split(text) if s.strip()]
        if not sentences:
            sentences = [text]
        tokens_total = len(text.split())
        avg_tps = tokens_total / max(len(sentences), 1)
        # Baseline: _AROUSAL_TPS_REF maps to 0 contribution;
        # above ref maps proportionally to [0, 1] capped at max.
        if avg_tps <= _AROUSAL_TPS_REF:
            tps_score = 0.0
        else:
            tps_score = min(
                (avg_tps - _AROUSAL_TPS_REF) / (_AROUSAL_TPS_MAX - _AROUSAL_TPS_REF),
                1.0,
            )

        # Weighted average (equal weights)
        arousal = (punct_density + cap_ratio + tps_score) / 3.0
        return float(np.clip(arousal, 0.0, 1.0))

    def _compute_semantic_density(self, text: str) -> float:
        """
        Unique-token ratio: unique_tokens / total_tokens → [0.0, 1.0].

        A single-word text has density 1.0 (all tokens unique).
        All-same-word text has density approaching 0.0.
        """
        tokens = text.lower().split()
        if not tokens:
            return 0.0
        density = len(set(tokens)) / len(tokens)
        return float(np.clip(density, 0.0, 1.0))
