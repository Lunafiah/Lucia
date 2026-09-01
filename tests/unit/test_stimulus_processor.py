"""
Unit tests for StimulusProcessor.
Requirements: 4.1, 4.2, 4.6, 4.7, 4.9, 4.10
"""

from __future__ import annotations

import warnings

import numpy as np
import pytest

from src.core.config import StimulusConfig
from src.core.gating.stimulus_processor import StimulusProcessor


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------

@pytest.fixture
def sp() -> StimulusProcessor:
    return StimulusProcessor(StimulusConfig(vector_dim=16))


@pytest.fixture
def sp3() -> StimulusProcessor:
    """Minimum valid vector_dim."""
    return StimulusProcessor(StimulusConfig(vector_dim=3))


# ---------------------------------------------------------------------------
# Initialisation / config validation (Req 4.10)
# ---------------------------------------------------------------------------

class TestInit:
    def test_vector_dim_2_raises(self):
        with pytest.raises(ValueError, match="vector_dim"):
            StimulusProcessor(StimulusConfig(vector_dim=2))

    def test_vector_dim_0_raises(self):
        with pytest.raises(ValueError):
            StimulusProcessor(StimulusConfig(vector_dim=0))

    def test_vector_dim_negative_raises(self):
        with pytest.raises(ValueError):
            StimulusProcessor(StimulusConfig(vector_dim=-5))

    def test_vector_dim_3_succeeds(self, sp3):
        v = sp3.encode("hello")
        assert v.shape == (3,)

    def test_vector_dim_16_default(self, sp):
        v = sp.encode("hello")
        assert v.shape == (16,)

    def test_vector_dim_32_succeeds(self):
        sp32 = StimulusProcessor(StimulusConfig(vector_dim=32))
        v = sp32.encode("hello")
        assert v.shape == (32,)


# ---------------------------------------------------------------------------
# Empty input (Req 4.6)
# ---------------------------------------------------------------------------

class TestEmptyInput:
    def test_empty_string_returns_zero_vector(self, sp):
        v = sp.encode("")
        assert v.shape == (16,)
        assert np.all(v == 0.0)

    def test_empty_string_no_warning(self, sp):
        with warnings.catch_warnings():
            warnings.simplefilter("error")
            sp.encode("")   # must not emit any warning

    def test_empty_string_dim3(self, sp3):
        v = sp3.encode("")
        assert v.shape == (3,)
        assert np.all(v == 0.0)

    def test_whitespace_only_not_empty(self, sp):
        # Whitespace is non-empty text, so floor is applied
        v = sp.encode("   ")
        assert v.shape == (16,)
        # dim-0 through dim-2 should have |value| >= 1e-7
        for i in range(3):
            assert abs(v[i]) >= 1e-7


# ---------------------------------------------------------------------------
# Truncation (Req 4.7)
# ---------------------------------------------------------------------------

class TestTruncation:
    def test_4097_chars_emits_warning(self, sp):
        long_text = "a" * 4097
        with pytest.warns(UserWarning, match="truncated"):
            sp.encode(long_text)

    def test_4096_chars_no_warning(self, sp):
        text = "a " * 2048   # 4096 characters exactly
        with warnings.catch_warnings():
            warnings.simplefilter("error")
            sp.encode(text)

    def test_warning_message_contains_counts(self, sp):
        long_text = "hello " * 1000  # > 4096 chars
        with pytest.warns(UserWarning) as record:
            sp.encode(long_text)
        msg = str(record[0].message)
        assert "4096" in msg                    # limit
        assert str(len(long_text)) in msg       # original length

    def test_truncation_does_not_change_output_shape(self, sp):
        long_text = "x " * 5000
        with warnings.catch_warnings():
            warnings.simplefilter("ignore")
            v = sp.encode(long_text)
        assert v.shape == (16,)


# ---------------------------------------------------------------------------
# Output bounds (Req 4.2)
# ---------------------------------------------------------------------------

class TestOutputBounds:
    def test_all_values_in_range(self, sp):
        texts = [
            "hello world",
            "WHAT?!?! THIS IS AMAZING!!!",
            "the quick brown fox",
            "I hate everything terrible awful disaster ruin",
            "a",
        ]
        for text in texts:
            v = sp.encode(text)
            assert np.all(v >= -1.0) and np.all(v <= 1.0), (
                f"Out-of-range values for {text!r}: min={v.min()}, max={v.max()}"
            )

    def test_values_dtype_float64(self, sp):
        v = sp.encode("hello world")
        assert v.dtype == np.float64


# ---------------------------------------------------------------------------
# Valence (Req 4.3) — dim 0
# ---------------------------------------------------------------------------

class TestValence:
    def test_strongly_positive_sentence_dim0_positive(self, sp):
        v = sp.encode("I love this! It is absolutely wonderful and amazing!")
        assert v[0] > 0, f"Expected positive valence, got {v[0]}"

    def test_strongly_negative_sentence_dim0_negative(self, sp):
        v = sp.encode("I hate this terrible awful disaster ruin everything.")
        assert v[0] < 0, f"Expected negative valence, got {v[0]}"

    def test_neutral_sentence_dim0_near_zero(self, sp):
        v = sp.encode("The table is on the floor.")
        # Should be near zero — VADER compound for neutral text
        assert -0.3 <= v[0] <= 0.3, f"Expected near-zero valence, got {v[0]}"


# ---------------------------------------------------------------------------
# Non-zero dims 0-2 for non-empty input (Req 4.9)
# ---------------------------------------------------------------------------

class TestNonZeroDims:
    def test_short_word_dims_nonzero(self, sp):
        v = sp.encode("hello")
        for i in range(3):
            assert abs(v[i]) >= 1e-7, (
                f"dim {i} should be non-zero, got {v[i]}"
            )

    def test_sentence_dims_nonzero(self, sp):
        v = sp.encode("The quick brown fox jumps over the lazy dog.")
        for i in range(3):
            assert abs(v[i]) >= 1e-7

    def test_single_char_dims_nonzero(self, sp):
        v = sp.encode("a")
        for i in range(3):
            assert abs(v[i]) >= 1e-7

    def test_dims_beyond_2_are_zero_padded(self, sp):
        v = sp.encode("hello world")
        assert np.all(v[3:] == 0.0), "Dims 3+ should be zero-padded"


# ---------------------------------------------------------------------------
# Arousal (Req 4.4) — dim 1
# ---------------------------------------------------------------------------

class TestArousal:
    def test_high_punctuation_increases_arousal(self, sp):
        calm = sp.encode("The weather is nice today.")
        excited = sp.encode("WHAT?!?! No way!!! This is INSANE!!!!")
        assert excited[1] > calm[1], (
            f"Expected excited arousal > calm: {excited[1]} vs {calm[1]}"
        )

    def test_arousal_non_negative(self, sp):
        texts = ["hello", "abc def", "test sentence here", "a b c"]
        for t in texts:
            v = sp.encode(t)
            assert v[1] >= -1e-7, f"Arousal should not be negative: {v[1]}"


# ---------------------------------------------------------------------------
# Semantic density (Req 4.5) — dim 2
# ---------------------------------------------------------------------------

class TestSemanticDensity:
    def test_all_same_tokens_low_density(self, sp):
        # All same word → unique ratio → 0 → dim2 maps to -1+floor ≈ -1
        v = sp.encode("a a a a a a a a a a")
        assert v[2] < 0, f"Expected low (negative) semantic density, got {v[2]}"

    def test_all_unique_tokens_high_density(self, sp):
        # All unique words → density = 1 → dim2 = 1.0
        v = sp.encode("apple banana cherry date elderberry fig grape honeydew")
        assert v[2] > 0, f"Expected high (positive) semantic density, got {v[2]}"
