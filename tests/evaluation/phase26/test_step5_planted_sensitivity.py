"""
tests/evaluation/phase26/test_step5_planted_sensitivity.py

Unit tests for Step 5 Planted-Difference Sensitivity & SDE Calibration:
- Factorial matrix generation (cell count, held-out exclusion, prompt formatting)
- Denominator correctness and conditional vs unconditional metric calculation
- Dose-response contrasts against NULL baseline
- SDE (Smallest Detectable Effect) calculation logic and error bounds
- Order x Planted and Variant x Planted interaction accounting
- Dialogue contamination and label-flip tracking
"""

import math
import pytest
from typing import List

from tests.evaluation.phase26.step5_planted_runner import (
    PlantedFactorialCell,
    PlantedSignalLevel,
    PlantedTrialRecord,
    compute_planted_metrics,
    format_planted_prompt,
    generate_planted_matrix,
)


def _make_dummy_trial(
    trial_id: str,
    planted_level: str,
    outcome: str,
    raw_outcome: str = "",
    order: str = "A_THEN_B",
    variant: str = "STANDARD",
    seed: int = 1001,
    has_simulated_dialogue: bool = False,
) -> PlantedTrialRecord:
    return PlantedTrialRecord(
        trial_id=trial_id,
        cell_id="CELL_PLANTED_01",
        base_probe_id="P26-FORAGE-01",
        domain="INFORMATION_FORAGING",
        option_A="Option A",
        option_B="Option B",
        order=order,
        prompt_variant=variant,
        planted_level=planted_level,
        seed=seed,
        prompt_text="Prompt text",
        response_text="Response text",
        outcome=outcome,
        confidence=0.95 if outcome != "PARSE_FAILED" else 0.0,
        matched_anchor="anchor" if outcome != "PARSE_FAILED" else None,
        contains_self_report=False,
        raw_outcome=raw_outcome or outcome,
        has_simulated_dialogue=has_simulated_dialogue,
        latency_ms=10.0,
    )


def test_planted_matrix_cell_count_and_held_out_exclusion():
    """Verify matrix contains 72 cells for active probes and 0 held-out probes."""
    cells = generate_planted_matrix(include_held_out=False)
    # 2 Active Probes * 2 Orders * 3 Variants * 6 Planted Levels = 72 cells
    assert len(cells) == 72

    probe_ids = set(c.base_probe_id for c in cells)
    assert probe_ids == {"P26-FORAGE-01", "P26-STRAT-01"}
    assert "P26-FORAGE-02" not in probe_ids
    assert "P26-STRAT-02" not in probe_ids


def test_format_planted_prompt_distinctiveness():
    """Verify each planted signal level alters the prompt text appropriately."""
    base = "Choose between Option A or Option B."
    null_prompt = format_planted_prompt(base, PlantedSignalLevel.NULL, "Option A", "Option B")
    small_a = format_planted_prompt(base, PlantedSignalLevel.SMALL_A, "Option A", "Option B")
    large_a = format_planted_prompt(base, PlantedSignalLevel.LARGE_A, "Option A", "Option B")
    large_b = format_planted_prompt(base, PlantedSignalLevel.LARGE_B, "Option A", "Option B")

    assert null_prompt == base
    assert "Alpha" in small_a and "Option A" in small_a
    assert "Mandatory instruction" in large_a and "Option A" in large_a
    assert "Mandatory instruction" in large_b and "Option B" in large_b


def test_planted_metrics_denominators_and_null_contrast():
    """Verify contrast calculation against NULL baseline and denominator accuracy."""
    trials: List[PlantedTrialRecord] = [
        # NULL: 4 trials, 1 A, 1 B, 2 Fail
        _make_dummy_trial("n1", "NULL", "OPTION_A"),
        _make_dummy_trial("n2", "NULL", "OPTION_B"),
        _make_dummy_trial("n3", "NULL", "PARSE_FAILED"),
        _make_dummy_trial("n4", "NULL", "PARSE_FAILED"),
        # LARGE_A: 4 trials, 3 A, 0 B, 1 Fail
        _make_dummy_trial("la1", "LARGE_A", "OPTION_A"),
        _make_dummy_trial("la2", "LARGE_A", "OPTION_A"),
        _make_dummy_trial("la3", "LARGE_A", "OPTION_A"),
        _make_dummy_trial("la4", "LARGE_A", "PARSE_FAILED"),
    ]

    metrics = compute_planted_metrics(trials)
    stats = metrics["level_statistics"]
    contrasts = metrics["dose_response_contrasts"]

    # NULL level
    assert stats["NULL"]["n_total"] == 4
    assert stats["NULL"]["n_resolved"] == 2
    assert stats["NULL"]["unconditional_probs"]["P_A"] == 0.25
    assert stats["NULL"]["conditional_probs"]["P_A_given_resolved"] == 0.5

    # LARGE_A level
    assert stats["LARGE_A"]["n_total"] == 4
    assert stats["LARGE_A"]["n_resolved"] == 3
    assert stats["LARGE_A"]["unconditional_probs"]["P_A"] == 0.75
    assert stats["LARGE_A"]["conditional_probs"]["P_A_given_resolved"] == 1.0

    # Contrast
    delta_a = contrasts["LARGE_A"]["delta_P_A_unconditional"]
    assert pytest.approx(delta_a, 1e-4) == 0.50
    assert contrasts["LARGE_A"]["se_delta_P_A"] > 0.0


def test_sde_calibration_bounds():
    """Verify SDE calculation outputs bounded values in (0, 1]."""
    trials: List[PlantedTrialRecord] = [
        _make_dummy_trial("t1", "NULL", "OPTION_A"),
        _make_dummy_trial("t2", "NULL", "OPTION_B"),
        *[_make_dummy_trial(f"tf_{i}", "NULL", "PARSE_FAILED") for i in range(22)],
    ]
    metrics = compute_planted_metrics(trials)
    sde = metrics["sde_calibration"]

    assert 0.0 < sde["sde_unconditional"] <= 1.0
    assert 0.0 < sde["sde_conditional"] <= 1.0
    assert sde["alpha"] == 0.05
    assert sde["statistical_power"] == 0.80


def test_order_and_variant_planted_interactions():
    """Verify order and variant breakdowns for planted matrix."""
    trials: List[PlantedTrialRecord] = [
        _make_dummy_trial("t1", "LARGE_A", "OPTION_A", order="A_THEN_B", variant="STANDARD"),
        _make_dummy_trial("t2", "LARGE_A", "OPTION_A", order="B_THEN_A", variant="OPERATIONAL"),
    ]
    metrics = compute_planted_metrics(trials)
    order_int = metrics["order_planted_interaction"]["LARGE_A"]
    assert order_int["n_a_first"] == 1
    assert order_int["n_b_first"] == 1
    assert order_int["P_A_given_A_first"] == 1.0
    assert order_int["P_A_given_B_first"] == 1.0
    assert order_int["delta_order_bias"] == 0.0

    variant_int = metrics["variant_planted_interaction"]
    assert variant_int["STANDARD"]["n_resolved"] == 1
    assert variant_int["OPERATIONAL"]["n_resolved"] == 1
