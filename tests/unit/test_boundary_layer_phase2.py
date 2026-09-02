"""
Unit tests for BoundaryLayer Phase 2 recall pattern extensions.

Requirements: 12.2, 12.3
"""

import pytest

from src.core.safety.boundary_layer import BoundaryLayer


@pytest.fixture
def layer():
    return BoundaryLayer()


class TestBoundaryLayerPhase2Patterns:
    @pytest.mark.parametrize(
        "phrase",
        [
            "I remember",
            "I recall",
            "last time",
            "you mentioned",
            "you said",
            "I know from before",
            "previously you",
            "my memory",
        ],
    )
    def test_phase2_pattern_triggers_soft_block(self, layer, phrase):
        raw_text = f"Yes, {phrase} that the sun is bright."
        safe_text = layer.validate(raw_text)
        assert phrase not in safe_text
        assert "[...]" in safe_text

    @pytest.mark.parametrize(
        "variation",
        [
            "I RECALL",
            "i recall",
            "I Recall",
            "i ReCaLl",
        ],
    )
    def test_patterns_are_case_insensitive(self, layer, variation):
        raw_text = f"{variation} the exact coordinates."
        safe_text = layer.validate(raw_text)
        assert variation not in safe_text
        assert "[...]" in safe_text

    def test_clean_response_passes_through(self, layer):
        text = "The quick brown fox jumps over the lazy dog."
        assert layer.validate(text) == text
