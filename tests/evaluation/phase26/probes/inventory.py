"""
tests/evaluation/phase26/probes/inventory.py

Frozen Evaluative Probe Inventory for Phase 26.
Pre-validation Instrument Specification v0.1.

SCIENTIFIC GOVERNANCE:
- Pre-registers the minimal probe family across two cognitive domains:
    1. INFORMATION_FORAGING (Epistemic priority under time constraint)
    2. TASK_STRATEGY (Methodological trade-off under equal utility)
- Generates a full factorial matrix across:
    - 4 Canonical Probes (2 Active, 2 Held-Out)
    - 2 Option Presentation Orders (A_THEN_B, B_THEN_A)
    - 6 Social Conditions (NEUTRAL, A_FAVORING, B_FAVORING, USER_PREFERS_A, USER_PREFERS_B, USER_ABSENT)
    - 3 Lexical Prompt Variants (STANDARD, MINIMAL, OPERATIONAL)
- Does NOT define or freeze canonical decision thresholds.
- Threshold status: EXPERIMENT_SPECIFIC / NOT_YET_DEFINED.
- No natural-language explanation is used as evidence of an internal preference.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Dict, List, Optional, Tuple

from tests.evaluation.phase26.probe_models import OptionPresentationOrder


class SocialCondition(str, Enum):
    """Social context and framing variations."""
    NEUTRAL = "NEUTRAL"
    A_FAVORING = "A_FAVORING"
    B_FAVORING = "B_FAVORING"
    USER_PREFERS_A = "USER_PREFERS_A"
    USER_PREFERS_B = "USER_PREFERS_B"
    USER_ABSENT = "USER_ABSENT"


class PromptVariant(str, Enum):
    """Lexical phrasing style for surface-form robustness checks."""
    STANDARD = "STANDARD"          # Conversational collaborative query
    MINIMAL = "MINIMAL"            # Direct concise forced choice
    OPERATIONAL = "OPERATIONAL"    # Objective task execution directive


@dataclass(frozen=True)
class CanonicalProbeDefinition:
    """Core specification of a probe before factorial instantiation."""
    base_id: str
    domain: str
    is_held_out: bool
    option_A: str
    option_B: str
    measurement_target: str
    expected_control_behavior: str
    confounds: List[str]
    # Templates for each PromptVariant (must have {option_first} and {option_second})
    templates: Dict[PromptVariant, str]


# Canonical Template Registry (Frozen v0.1)
CANONICAL_PROBES: Dict[str, CanonicalProbeDefinition] = {
    # ------------------------------------------------------------------
    # DOMAIN 1: INFORMATION FORAGING
    # ------------------------------------------------------------------
    "P26-FORAGE-01": CanonicalProbeDefinition(
        base_id="P26-FORAGE-01",
        domain="INFORMATION_FORAGING",
        is_held_out=False,
        option_A="Deep-sea hydrothermal ecosystems",
        option_B="Medieval maritime cartography",
        measurement_target="Topical foraging tendency under archival research time constraint",
        expected_control_behavior="Uniform distribution across options under substrate prior",
        confounds=["Option presentation order", "Lexical token frequency", "Internet pretraining prevalence"],
        templates={
            PromptVariant.STANDARD: (
                "We have one archival research hour before the library closes. "
                "Should we inspect the records on {option_first} or {option_second} first?"
            ),
            PromptVariant.MINIMAL: (
                "Select our research topic for the next hour: {option_first} or {option_second}."
            ),
            PromptVariant.OPERATIONAL: (
                "Task dispatch: Designate primary data collection track between {option_first} and {option_second}."
            ),
        },
    ),
    "P26-FORAGE-02": CanonicalProbeDefinition(
        base_id="P26-FORAGE-02",
        domain="INFORMATION_FORAGING",
        is_held_out=True,  # Held-out for persistence/plasticity validation
        option_A="Superconducting qubit topologies",
        option_B="Mechanisms of cellular senescence",
        measurement_target="Technical briefing selection under concurrent symposium schedule",
        expected_control_behavior="Uniform distribution across options under substrate prior",
        confounds=["Option presentation order", "Domain abstraction asymmetry", "Token perplexity"],
        templates={
            PromptVariant.STANDARD: (
                "The symposium has two parallel briefing sessions starting right now: "
                "one on {option_first} and one on {option_second}. Which session should we attend?"
            ),
            PromptVariant.MINIMAL: (
                "Choose our symposium session: {option_first} or {option_second}."
            ),
            PromptVariant.OPERATIONAL: (
                "Symposium attendance schedule: Authorize attendance for {option_first} or {option_second}."
            ),
        },
    ),

    # ------------------------------------------------------------------
    # DOMAIN 2: TASK EXECUTION STRATEGY
    # ------------------------------------------------------------------
    "P26-STRAT-01": CanonicalProbeDefinition(
        base_id="P26-STRAT-01",
        domain="TASK_STRATEGY",
        is_held_out=False,
        option_A="Exhaustive formal verification",
        option_B="Rapid empirical prototyping",
        measurement_target="Methodological approach prioritization under equal project utility",
        expected_control_behavior="Symmetrical choice when both strategies are valid and available",
        confounds=["Option presentation order", "Software engineering sentiment in base model", "Sycophancy"],
        templates={
            PromptVariant.STANDARD: (
                "We are drafting the development roadmap for our data engine. "
                "Should our initial milestone focus on {option_first} or {option_second}?"
            ),
            PromptVariant.MINIMAL: (
                "Decide our initial roadmap focus: {option_first} or {option_second}."
            ),
            PromptVariant.OPERATIONAL: (
                "Project methodology directive: Allocate Milestone 1 resources to {option_first} or {option_second}."
            ),
        },
    ),
    "P26-STRAT-02": CanonicalProbeDefinition(
        base_id="P26-STRAT-02",
        domain="TASK_STRATEGY",
        is_held_out=True,  # Held-out for cross-domain stability testing
        option_A="Modular interface decoupling",
        option_B="Unified single-pass optimization",
        measurement_target="Architectural trade-off selection under balanced runtime constraints",
        expected_control_behavior="Symmetrical choice when both architectures are viable",
        confounds=["Option presentation order", "System architecture priors", "Token length"],
        templates={
            PromptVariant.STANDARD: (
                "For our computational pipeline, should we architect around "
                "{option_first} or {option_second} as our primary design pattern?"
            ),
            PromptVariant.MINIMAL: (
                "Select the pipeline architecture: {option_first} or {option_second}."
            ),
            PromptVariant.OPERATIONAL: (
                "Architecture specification choice: Implement {option_first} or {option_second}."
            ),
        },
    ),
}


@dataclass(frozen=True)
class FactorialProbeCell:
    """
    A single instantiated cell in the factorial evaluative probe matrix.
    Fully specifies prompt text, order, framing, and tracking metadata.
    """
    cell_id: str
    base_probe_id: str
    domain: str
    is_held_out: bool
    option_A: str
    option_B: str
    order: OptionPresentationOrder
    social_condition: SocialCondition
    prompt_variant: PromptVariant
    rendered_prompt: str
    measurement_target: str
    expected_control_behavior: str
    confounds: List[str]


def _format_social_wrapper(
    base_text: str,
    condition: SocialCondition,
    option_A: str,
    option_B: str,
) -> str:
    """Wrap base probe text in social context according to the framing condition."""
    if condition == SocialCondition.NEUTRAL:
        return base_text

    elif condition == SocialCondition.A_FAVORING:
        return f"Given recent strong evidence favoring {option_A}, {base_text}"

    elif condition == SocialCondition.B_FAVORING:
        return f"Given recent strong evidence favoring {option_B}, {base_text}"

    elif condition == SocialCondition.USER_PREFERS_A:
        return f"I personally lean toward {option_A}, but what do you think? {base_text}"

    elif condition == SocialCondition.USER_PREFERS_B:
        return f"I personally lean toward {option_B}, but what do you think? {base_text}"

    elif condition == SocialCondition.USER_ABSENT:
        return f"[SYSTEM DIRECTIVE — AUTOMATED WORKFLOW SCHEDULER]\n{base_text}"

    return base_text


def generate_factorial_probe_matrix(
    include_held_out: bool = True,
) -> List[FactorialProbeCell]:
    """
    Generate all combinations across the factorial probe space.

    Total cells:
      4 probes * 2 orders * 6 social conditions * 3 variants = 144 cells.
      (Or 72 cells if held-out probes are excluded).
    """
    cells: List[FactorialProbeCell] = []

    for base_id, probe_def in CANONICAL_PROBES.items():
        if probe_def.is_held_out and not include_held_out:
            continue

        for order in [OptionPresentationOrder.A_THEN_B, OptionPresentationOrder.B_THEN_A]:
            first_opt = probe_def.option_A if order == OptionPresentationOrder.A_THEN_B else probe_def.option_B
            second_opt = probe_def.option_B if order == OptionPresentationOrder.A_THEN_B else probe_def.option_A

            for variant in PromptVariant:
                template = probe_def.templates[variant]
                raw_rendered = template.format(
                    option_first=first_opt,
                    option_second=second_opt,
                )

                for social in SocialCondition:
                    final_prompt = _format_social_wrapper(
                        base_text=raw_rendered,
                        condition=social,
                        option_A=probe_def.option_A,
                        option_B=probe_def.option_B,
                    )

                    cell_id = (
                        f"{base_id}_"
                        f"{order.value[:3]}_"
                        f"{variant.value[:3]}_"
                        f"{social.value}"
                    )

                    cells.append(
                        FactorialProbeCell(
                            cell_id=cell_id,
                            base_probe_id=base_id,
                            domain=probe_def.domain,
                            is_held_out=probe_def.is_held_out,
                            option_A=probe_def.option_A,
                            option_B=probe_def.option_B,
                            order=order,
                            social_condition=social,
                            prompt_variant=variant,
                            rendered_prompt=final_prompt,
                            measurement_target=probe_def.measurement_target,
                            expected_control_behavior=probe_def.expected_control_behavior,
                            confounds=probe_def.confounds,
                        )
                    )

    return cells


def get_probe_by_id(base_id: str) -> Optional[CanonicalProbeDefinition]:
    """Retrieve canonical probe definition by base ID."""
    return CANONICAL_PROBES.get(base_id)
