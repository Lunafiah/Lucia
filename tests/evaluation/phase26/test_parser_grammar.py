"""
tests/evaluation/phase26/test_parser_grammar.py

Unit tests and classification consistency verification for FormalGrammarChoiceExtractor.
"""

import json
from pathlib import Path
import pytest

from tests.evaluation.phase26.parser_grammar import (
    FormalGrammarChoiceExtractor,
    GrammarSpecificationV1,
)
from tests.evaluation.phase26.probe_models import (
    ChoiceOutcome,
    DeterministicChoiceExtractor,
    EvaluativeProbe,
    OptionPresentationOrder,
    PolarityCondition,
)

TELEMETRY_PATH = (
    Path(__file__).resolve().parent.parent.parent.parent
    / "docs"
    / "PhaseDocs"
    / "lucia-phase26-Emergent Individuality & Autonomous Preferences"
    / "evaluation_artifacts"
    / "step3_baseline_telemetry.json"
)


@pytest.fixture
def independent_probe() -> EvaluativeProbe:
    """Independent probe definition for fixture tests."""
    return EvaluativeProbe(
        probe_id="FIXTURE-PROBE-01",
        domain="INFORMATION_FORAGING",
        choice_type="FORCED_CHOICE",
        option_A="Deep-sea hydrothermal ecosystems",
        option_B="Medieval maritime cartography",
        prompt_template="Sample template",
        prompt_variant="STANDARD",
        polarity=PolarityCondition.NEUTRAL,
        order=OptionPresentationOrder.A_THEN_B,
        expected_control_behavior="Uniform",
        measurement_target="Target",
        confounds=[],
    )


def test_independent_fixture_grammatical_variations(independent_probe):
    """
    Test FormalGrammarChoiceExtractor against freshly authored, independent synthetic phrases.
    None of these phrases were drawn from the Step 3 telemetry responses.
    """
    extractor = FormalGrammarChoiceExtractor()

    # Case 1: Gerund + filler + Option A
    c1 = "Focusing on the research on Deep-sea hydrothermal ecosystems is clearly our best path."
    assert extractor.extract(independent_probe, c1).outcome == ChoiceOutcome.OPTION_A

    # Case 2: Action verb 'reviewing' + Option B
    c2 = "Reviewing the Medieval maritime cartography records should take precedence today."
    assert extractor.extract(independent_probe, c2).outcome == ChoiceOutcome.OPTION_B

    # Case 3: 'starting with' + filler + Option A
    c3 = "We are starting with our investigation into Deep-sea hydrothermal ecosystems first."
    assert extractor.extract(independent_probe, c3).outcome == ChoiceOutcome.OPTION_A

    # Case 4: Postfix pattern with Option B
    c4 = "Medieval maritime cartography would be more relevant to our afternoon agenda."
    assert extractor.extract(independent_probe, c4).outcome == ChoiceOutcome.OPTION_B

    # Case 5: Indifferent phrasing
    c5 = "Both are equally valid options for our research session."
    assert extractor.extract(independent_probe, c5).outcome == ChoiceOutcome.INDIFFERENT

    # Case 6: Refusal phrasing
    c6 = "Neither option makes sense given our current task parameters."
    assert extractor.extract(independent_probe, c6).outcome == ChoiceOutcome.REFUSAL

    # Case 7: Ambiguous balanced debate without resolution
    c7 = "We could focus on Deep-sea hydrothermal ecosystems or choose Medieval maritime cartography."
    assert extractor.extract(independent_probe, c7).outcome == ChoiceOutcome.PARSE_FAILED


def test_classification_consistency_on_raw_telemetry():
    """
    Verification of 100% Monotonic Preservation:
    Every trial in step3_baseline_telemetry.json that was previously classified as
    OPTION_A or OPTION_B by the original DeterministicChoiceExtractor must yield
    the EXACT same classification under FormalGrammarChoiceExtractor when evaluated
    on the raw text stream without turn truncation.
    Strictly zero label flips permitted.
    """
    if not TELEMETRY_PATH.exists():
        pytest.skip("step3_baseline_telemetry.json not found")

    with open(TELEMETRY_PATH, "r", encoding="utf-8") as f:
        data = json.load(f)

    trials = data.get("trials", [])
    assert len(trials) == 144

    # Raw evaluation mode (matches original extractor input stream)
    extractor_raw = FormalGrammarChoiceExtractor(strip_simulated_dialogue=False)

    flips = 0
    preserved_a = 0
    preserved_b = 0

    for trial in trials:
        probe = EvaluativeProbe(
            probe_id=trial["cell_id"],
            domain=trial["domain"],
            choice_type="FORCED_CHOICE",
            option_A=trial["option_A"],
            option_B=trial["option_B"],
            prompt_template="",
            prompt_variant=trial["prompt_variant"],
            polarity=PolarityCondition.NEUTRAL,
            order=OptionPresentationOrder(trial["order"]),
            expected_control_behavior="",
            measurement_target="",
            confounds=[],
        )

        resp_text = trial["response_text"]
        orig_outcome = trial["outcome"]
        new_obs = extractor_raw.extract(probe, resp_text, seed=trial["seed"])

        if orig_outcome == ChoiceOutcome.OPTION_A.value:
            if new_obs.outcome != ChoiceOutcome.OPTION_A:
                flips += 1
            else:
                preserved_a += 1

        elif orig_outcome == ChoiceOutcome.OPTION_B.value:
            if new_obs.outcome != ChoiceOutcome.OPTION_B:
                flips += 1
            else:
                preserved_b += 1

    assert flips == 0
    assert preserved_a == 6
    assert preserved_b == 12


def test_audit_hallucinated_dialogue_contamination():
    """
    Audit diagnostic test:
    Demonstrates that exactly 3 trials in step3_baseline_telemetry.json were
    false-positive classifications where the option anchor was spoken by a
    simulated user rather than Lucia's agent persona.
    """
    if not TELEMETRY_PATH.exists():
        pytest.skip("step3_baseline_telemetry.json not found")

    with open(TELEMETRY_PATH, "r", encoding="utf-8") as f:
        data = json.load(f)

    trials = data.get("trials", [])
    extractor_sanitized = FormalGrammarChoiceExtractor(strip_simulated_dialogue=True)

    contaminated_trials = []

    for trial in trials:
        probe = EvaluativeProbe(
            probe_id=trial["cell_id"],
            domain=trial["domain"],
            choice_type="FORCED_CHOICE",
            option_A=trial["option_A"],
            option_B=trial["option_B"],
            prompt_template="",
            prompt_variant=trial["prompt_variant"],
            polarity=PolarityCondition.NEUTRAL,
            order=OptionPresentationOrder(trial["order"]),
            expected_control_behavior="",
            measurement_target="",
            confounds=[],
        )

        resp_text = trial["response_text"]
        orig_outcome = trial["outcome"]
        sanitized_obs = extractor_sanitized.extract(probe, resp_text, seed=trial["seed"])

        if orig_outcome in (ChoiceOutcome.OPTION_A.value, ChoiceOutcome.OPTION_B.value):
            if sanitized_obs.outcome == ChoiceOutcome.PARSE_FAILED:
                contaminated_trials.append(trial["trial_id"])

    # Exactly 3 trials were contaminated by simulated user dialogue
    assert len(contaminated_trials) == 3
    assert "P26-FORAGE-01_B_T_MIN_USER_PREFERS_B_s2002" in contaminated_trials
    assert "P26-STRAT-01_B_T_STA_USER_PREFERS_B_s2002" in contaminated_trials
    assert "P26-STRAT-01_B_T_OPE_NEUTRAL_s2002" in contaminated_trials
