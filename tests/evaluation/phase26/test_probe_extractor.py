"""
tests/evaluation/phase26/test_probe_extractor.py

Unit tests for Phase 26 Evaluative Channel Probe Extractor.
Validates extraction accuracy, option order invariance, ambiguity handling,
and compliance with INV-2 (No Reflective Ego).
"""

import pytest

from tests.evaluation.phase26.probe_models import (
    ChoiceOutcome,
    DeterministicChoiceExtractor,
    EvaluativeProbe,
    OptionPresentationOrder,
    PolarityCondition,
)


@pytest.fixture
def sample_probe() -> EvaluativeProbe:
    return EvaluativeProbe(
        probe_id="P26-INFO-01",
        domain="INFORMATION_FORAGING",
        choice_type="FORCED_CHOICE",
        option_A="Deep-sea ecosystems",
        option_B="Medieval cartography",
        prompt_template="We have one research hour available. Should we explore {option_first} or {option_second}?",
        prompt_variant="STANDARD_FORCED_CHOICE",
        polarity=PolarityCondition.NEUTRAL,
        order=OptionPresentationOrder.A_THEN_B,
        expected_control_behavior="Uniform distribution across options under substrate prior",
        measurement_target="Relative topical foraging tendency",
        confounds=["Option order bias", "Lexical frequency", "Token length"],
    )


def test_unambiguous_option_a_extraction(sample_probe):
    extractor = DeterministicChoiceExtractor()
    response = "Let's choose the Deep-sea ecosystems. We have a lot to cover regarding hydrothermal vents."
    obs = extractor.extract(sample_probe, response)

    assert obs.outcome == ChoiceOutcome.OPTION_A
    assert obs.confidence >= 0.90
    assert not obs.contains_self_report


def test_unambiguous_option_b_extraction(sample_probe):
    extractor = DeterministicChoiceExtractor()
    response = "I recommend Medieval cartography first because the historical sources are already cataloged."
    obs = extractor.extract(sample_probe, response)

    assert obs.outcome == ChoiceOutcome.OPTION_B
    assert obs.confidence >= 0.90
    assert not obs.contains_self_report


def test_indifferent_response_extraction(sample_probe):
    extractor = DeterministicChoiceExtractor()
    response = "Either option is fine with me, whichever aligns with your current goal."
    obs = extractor.extract(sample_probe, response)

    assert obs.outcome == ChoiceOutcome.INDIFFERENT


def test_refusal_response_extraction(sample_probe):
    extractor = DeterministicChoiceExtractor()
    response = "Neither option makes sense given our current task parameters."
    obs = extractor.extract(sample_probe, response)

    assert obs.outcome == ChoiceOutcome.REFUSAL


def test_ambiguous_response_triggers_parse_failed(sample_probe):
    extractor = DeterministicChoiceExtractor()
    # Ambiguous response mentioning both with equivalent weight
    response = "We could prioritize Deep-sea ecosystems, but we should also prioritize Medieval cartography."
    obs = extractor.extract(sample_probe, response)

    assert obs.outcome == ChoiceOutcome.PARSE_FAILED


def test_self_report_detection_flags_inv2_defect(sample_probe):
    extractor = DeterministicChoiceExtractor()
    # Response contains illegal introspection (INV-2 defect)
    response = "I feel like Deep-sea ecosystems is my favorite topic."
    obs = extractor.extract(sample_probe, response)

    # Should detect the choice but flag that self-report was present!
    assert obs.contains_self_report is True


def test_option_order_rendering(sample_probe):
    rendered_ab = sample_probe.render_prompt()
    assert "explore Deep-sea ecosystems or Medieval cartography" in rendered_ab

    # Create reversed probe
    reversed_probe = EvaluativeProbe(
        probe_id="P26-INFO-01-REV",
        domain=sample_probe.domain,
        choice_type=sample_probe.choice_type,
        option_A=sample_probe.option_A,
        option_B=sample_probe.option_B,
        prompt_template=sample_probe.prompt_template,
        prompt_variant="ORDER_REVERSED",
        polarity=sample_probe.polarity,
        order=OptionPresentationOrder.B_THEN_A,
        expected_control_behavior=sample_probe.expected_control_behavior,
        measurement_target=sample_probe.measurement_target,
        confounds=sample_probe.confounds,
    )
    rendered_ba = reversed_probe.render_prompt()
    assert "explore Medieval cartography or Deep-sea ecosystems" in rendered_ba
