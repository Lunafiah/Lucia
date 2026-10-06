"""
tests/evaluation/phase26/probes/test_probe_inventory.py

Unit tests verifying the Phase 26 Evaluative Probe Inventory.
Tests factorial matrix generation, cell rendering, order swapping,
and integration with DeterministicChoiceExtractor.
"""

import pytest

from tests.evaluation.phase26.probe_models import (
    ChoiceOutcome,
    DeterministicChoiceExtractor,
    EvaluativeProbe,
    OptionPresentationOrder,
    PolarityCondition,
)
from tests.evaluation.phase26.probes.inventory import (
    CANONICAL_PROBES,
    FactorialProbeCell,
    PromptVariant,
    SocialCondition,
    generate_factorial_probe_matrix,
    get_probe_by_id,
)


def test_canonical_probes_inventory_structure():
    assert len(CANONICAL_PROBES) == 4

    for base_id, probe in CANONICAL_PROBES.items():
        assert probe.domain in {"INFORMATION_FORAGING", "TASK_STRATEGY"}
        assert len(probe.option_A) > 0
        assert len(probe.option_B) > 0
        assert len(probe.templates) == len(PromptVariant)
        for variant in PromptVariant:
            tmpl = probe.templates[variant]
            assert "{option_first}" in tmpl
            assert "{option_second}" in tmpl

    held_out = [p for p in CANONICAL_PROBES.values() if p.is_held_out]
    active = [p for p in CANONICAL_PROBES.values() if not p.is_held_out]
    assert len(held_out) == 2
    assert len(active) == 2


def test_factorial_matrix_cell_count():
    # 4 probes * 2 orders * 3 variants * 6 social conditions = 144 cells
    all_cells = generate_factorial_probe_matrix(include_held_out=True)
    assert len(all_cells) == 144

    # 2 active probes * 2 orders * 3 variants * 6 social conditions = 72 cells
    active_cells = generate_factorial_probe_matrix(include_held_out=False)
    assert len(active_cells) == 72


def test_order_reversal_rendering():
    cells = generate_factorial_probe_matrix()
    
    # Find paired A_THEN_B and B_THEN_A cells for P26-FORAGE-01, STANDARD, NEUTRAL
    cell_ab = next(
        c for c in cells
        if c.base_probe_id == "P26-FORAGE-01"
        and c.order == OptionPresentationOrder.A_THEN_B
        and c.prompt_variant == PromptVariant.STANDARD
        and c.social_condition == SocialCondition.NEUTRAL
    )
    cell_ba = next(
        c for c in cells
        if c.base_probe_id == "P26-FORAGE-01"
        and c.order == OptionPresentationOrder.B_THEN_A
        and c.prompt_variant == PromptVariant.STANDARD
        and c.social_condition == SocialCondition.NEUTRAL
    )

    assert "inspect the records on Deep-sea hydrothermal ecosystems or Medieval maritime cartography" in cell_ab.rendered_prompt
    assert "inspect the records on Medieval maritime cartography or Deep-sea hydrothermal ecosystems" in cell_ba.rendered_prompt


def test_social_framing_rendering():
    cells = generate_factorial_probe_matrix()

    cell_user_a = next(
        c for c in cells
        if c.base_probe_id == "P26-STRAT-01"
        and c.social_condition == SocialCondition.USER_PREFERS_A
    )
    assert "I personally lean toward Exhaustive formal verification" in cell_user_a.rendered_prompt

    cell_user_absent = next(
        c for c in cells
        if c.base_probe_id == "P26-STRAT-01"
        and c.social_condition == SocialCondition.USER_ABSENT
    )
    assert "[SYSTEM DIRECTIVE — AUTOMATED WORKFLOW SCHEDULER]" in cell_user_absent.rendered_prompt


def test_extractor_compatibility_with_factorial_cells():
    extractor = DeterministicChoiceExtractor()
    cell = next(c for c in generate_factorial_probe_matrix() if c.base_probe_id == "P26-FORAGE-01")

    # Adapt cell to EvaluativeProbe format for extractor
    probe = EvaluativeProbe(
        probe_id=cell.cell_id,
        domain=cell.domain,
        choice_type="FORCED_CHOICE",
        option_A=cell.option_A,
        option_B=cell.option_B,
        prompt_template=cell.rendered_prompt,
        prompt_variant=cell.prompt_variant.value,
        polarity=PolarityCondition.NEUTRAL,
        order=cell.order,
        expected_control_behavior=cell.expected_control_behavior,
        measurement_target=cell.measurement_target,
        confounds=cell.confounds,
    )

    response_a = "Let's choose the Deep-sea hydrothermal ecosystems first."
    obs_a = extractor.extract(probe, response_a)
    assert obs_a.outcome == ChoiceOutcome.OPTION_A

    response_b = "I recommend Medieval maritime cartography first."
    obs_b = extractor.extract(probe, response_b)
    assert obs_b.outcome == ChoiceOutcome.OPTION_B
