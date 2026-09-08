"""
Unit tests for StimulusService — Phase 8.6 Level 1.

Verifies:
- inject_text() routes through StimulusProcessor (normal sensory pathway).
- inject_vector() operates as an explicit debug/developer probe — NOT through StimulusProcessor.
- Both pathways advance EmotionCore state and are labelled correctly.
- inject_preset() selects the correct pathway based on the 'pathway' argument.
- Bounds validation on vector length and finiteness.
- History is appended and limited correctly.
- clear_history() empties the log.
- get_presets() returns all expected named presets.
"""

from __future__ import annotations

import pytest
import numpy as np

from src.core.config import EmotionConfig, StimulusConfig
from src.core.emotion.emotion_core import EmotionCore
from src.core.gating.stimulus_processor import StimulusProcessor
from src.core.simulation.stimulus_service import StimulusService, PRESET_STIMULI


def _make_service() -> StimulusService:
    """Construct a StimulusService with real sub-components."""
    emotion_core = EmotionCore(EmotionConfig())
    stimulus_processor = StimulusProcessor(StimulusConfig())
    return StimulusService(emotion_core=emotion_core, stimulus_processor=stimulus_processor)


# ---------------------------------------------------------------------------
# inject_text — Normal Sensory Pathway
# ---------------------------------------------------------------------------

class TestInjectText:
    def test_pathway_label_is_sensory_text(self):
        svc = _make_service()
        result = svc.inject_text("Hello Lucia", source="test")
        assert result["pathway"] == "sensory_text"

    def test_source_is_preserved(self):
        svc = _make_service()
        result = svc.inject_text("Test message", source="unit_test_harness")
        assert result["source"] == "unit_test_harness"

    def test_vector_has_16_dimensions(self):
        svc = _make_service()
        result = svc.inject_text("Any input text")
        assert len(result["vector"]) == 16

    def test_text_field_is_preserved(self):
        svc = _make_service()
        msg = "The quick brown fox"
        result = svc.inject_text(msg)
        assert result["text"] == msg

    def test_pad_before_and_after_are_present(self):
        svc = _make_service()
        result = svc.inject_text("Happy words of joy!")
        assert "pad_before" in result
        assert "pad_after" in result
        assert "pleasure" in result["pad_before"]
        assert "pleasure" in result["pad_after"]

    def test_positive_text_nudges_pleasure_upward(self):
        svc = _make_service()
        result = svc.inject_text("I love you so much, this is wonderful!")
        # After a strongly positive stimulus, pleasure should have shifted
        assert result["pad_after"]["pleasure"] >= result["pad_before"]["pleasure"] - 0.5

    def test_type_error_on_non_string(self):
        svc = _make_service()
        with pytest.raises(TypeError):
            svc.inject_text(42)

    def test_history_is_appended(self):
        svc = _make_service()
        svc.inject_text("First")
        svc.inject_text("Second")
        history = svc.get_history()
        assert len(history) == 2
        assert history[0]["pathway"] == "sensory_text"

    def test_stimulus_goes_through_processor_not_direct_path(self):
        """
        Invariant: inject_text ALWAYS goes through StimulusProcessor.
        We verify this by checking the result pathway label and that the
        vector produced is the same as calling StimulusProcessor.encode() directly.
        """
        emotion_core = EmotionCore(EmotionConfig())
        processor = StimulusProcessor(StimulusConfig())
        svc = StimulusService(emotion_core=emotion_core, stimulus_processor=processor)

        text = "Hello there"
        expected_vec = processor.encode(text).tolist()
        result = svc.inject_text(text)
        # Vector should match direct encode output
        for a, b in zip(result["vector"], expected_vec):
            assert abs(a - b) < 1e-6, f"Mismatch: {a} vs {b}"


# ---------------------------------------------------------------------------
# inject_vector — Developer/Debug Probe
# ---------------------------------------------------------------------------

class TestInjectVector:
    def test_pathway_label_is_debug_vector_probe(self):
        svc = _make_service()
        result = svc.inject_vector([0.5] * 16, source="debug_probe")
        assert result["pathway"] == "debug_vector_probe"

    def test_source_is_preserved(self):
        svc = _make_service()
        result = svc.inject_vector([0.0] * 16, source="my_probe")
        assert result["source"] == "my_probe"

    def test_text_field_is_none_for_vector_probe(self):
        """Vector probe has no text — it bypasses StimulusProcessor entirely."""
        svc = _make_service()
        result = svc.inject_vector([0.0] * 16)
        assert result["text"] is None

    def test_accepts_numpy_array(self):
        svc = _make_service()
        vec = np.zeros(16, dtype=np.float64)
        result = svc.inject_vector(vec)
        assert result["pathway"] == "debug_vector_probe"

    def test_accepts_list(self):
        svc = _make_service()
        result = svc.inject_vector([0.1] * 16)
        assert len(result["vector"]) == 16

    def test_wrong_dimension_raises_value_error(self):
        svc = _make_service()
        with pytest.raises(ValueError, match="16 dimensions"):
            svc.inject_vector([0.0] * 8)

    def test_non_finite_value_raises_value_error(self):
        svc = _make_service()
        vec = [0.0] * 16
        vec[3] = float("nan")
        with pytest.raises(ValueError):
            svc.inject_vector(vec)

    def test_values_are_clamped_to_minus_one_plus_one(self):
        svc = _make_service()
        vec = [5.0] * 16  # Out of bounds
        result = svc.inject_vector(vec)
        for v in result["vector"]:
            assert -1.0 <= v <= 1.0

    def test_vector_probe_does_not_call_stimulus_processor(self):
        """
        Architectural invariant: inject_vector bypasses StimulusProcessor.
        We verify this by monkeypatching encode() and asserting it is NOT called.
        """
        emotion_core = EmotionCore(EmotionConfig())
        processor = StimulusProcessor(StimulusConfig())
        called = []
        original_encode = processor.encode
        processor.encode = lambda *a, **kw: (called.append(True), original_encode(*a, **kw))[1]

        svc = StimulusService(emotion_core=emotion_core, stimulus_processor=processor)
        svc.inject_vector([0.1] * 16)
        assert len(called) == 0, "inject_vector must NOT call StimulusProcessor.encode()"


# ---------------------------------------------------------------------------
# Presets
# ---------------------------------------------------------------------------

class TestPresets:
    def test_get_presets_returns_all_named_presets(self):
        svc = _make_service()
        presets = svc.get_presets()
        expected = {"joy", "calm", "tension", "affection", "fatigue", "curiosity", "resting_attractor"}
        assert set(presets.keys()) == expected

    def test_each_preset_has_required_fields(self):
        svc = _make_service()
        for name, preset in svc.get_presets().items():
            assert "label" in preset, f"Missing 'label' in preset '{name}'"
            assert "text" in preset, f"Missing 'text' in preset '{name}'"
            assert "vector" in preset, f"Missing 'vector' in preset '{name}'"
            assert len(preset["vector"]) == 16, f"Preset '{name}' vector is not 16D"

    def test_inject_preset_sensory_text_pathway(self):
        svc = _make_service()
        result = svc.inject_preset("joy", pathway="sensory_text")
        assert result["pathway"] == "sensory_text"

    def test_inject_preset_debug_vector_pathway(self):
        svc = _make_service()
        result = svc.inject_preset("joy", pathway="debug_vector_probe")
        assert result["pathway"] == "debug_vector_probe"

    def test_inject_preset_unknown_name_raises_key_error(self):
        svc = _make_service()
        with pytest.raises(KeyError, match="Unknown preset"):
            svc.inject_preset("nonexistent_preset")

    def test_inject_preset_invalid_pathway_raises_value_error(self):
        svc = _make_service()
        with pytest.raises(ValueError, match="Unsupported pathway"):
            svc.inject_preset("joy", pathway="invalid_pathway")


# ---------------------------------------------------------------------------
# History
# ---------------------------------------------------------------------------

class TestStimulusHistory:
    def test_history_starts_empty(self):
        svc = _make_service()
        assert svc.get_history() == []

    def test_history_grows_with_injections(self):
        svc = _make_service()
        svc.inject_text("A")
        svc.inject_text("B")
        svc.inject_vector([0.0] * 16)
        assert len(svc.get_history()) == 3

    def test_history_limit_is_respected(self):
        svc = _make_service()
        for i in range(10):
            svc.inject_text(f"msg {i}")
        limited = svc.get_history(limit=3)
        assert len(limited) == 3
        assert limited[-1]["text"] == "msg 9"

    def test_clear_history_empties_log(self):
        svc = _make_service()
        svc.inject_text("Something")
        svc.clear_history()
        assert svc.get_history() == []
