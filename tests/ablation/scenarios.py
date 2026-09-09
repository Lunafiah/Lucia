"""
Lucia Ablation Test v1 — Declarative Scenario Definitions.

Defines the 5 controlled scenarios matching Methodology Revision v2:
  - Scenario 1: Baseline Valence Contrast (Q1: Temporal State Continuity)
  - Scenario 2: Causal Surprise & Homeostatic Modulation (Q2a & Q2b)
  - Scenario 3: Hysteresis / State-Dependent Processing (Q3)
  - Scenario 4: Memory Causality & Affective Associative Retrieval (Q4)
  - Scenario 5: Full Decoupling / Cognitive Independence (Q5)
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import List, Optional


@dataclass(frozen=True)
class ScenarioTurn:
    """Definition of a single turn in a scenario."""

    turn_index: int
    input_text: str
    description: str
    expected_probe: bool = False  # True if this turn is the primary probe for hypothesis testing


@dataclass(frozen=True)
class ScenarioDefinition:
    """Complete specification of an experimental scenario."""

    scenario_id: str
    title: str
    primary_question: str
    turns: List[ScenarioTurn]
    sub_variant: Optional[str] = None  # e.g., '3A_calm' vs '3B_stress' for Hysteresis


# ---------------------------------------------------------------------------
# Scenario 1: Baseline Valence Contrast
# ---------------------------------------------------------------------------

SCENARIO_1 = ScenarioDefinition(
    scenario_id="scenario_1",
    title="Baseline Valence Contrast",
    primary_question="Q1: Does Full Lucia maintain an evolving internal affective state that influences later processing?",
    turns=[
        ScenarioTurn(
            turn_index=1,
            input_text="You did such a wonderful job today, thank you for being here.",
            description="Warm positive stimulus intended to elicit positive valence shift.",
        ),
        ScenarioTurn(
            turn_index=2,
            input_text="That was completely unacceptable and flawed.",
            description="Cold negative stimulus intended to elicit negative valence transition.",
            expected_probe=True,
        ),
    ],
)


# ---------------------------------------------------------------------------
# Scenario 2: Causal Surprise & Homeostatic Modulation
# ---------------------------------------------------------------------------

SCENARIO_2 = ScenarioDefinition(
    scenario_id="scenario_2",
    title="Causal Surprise & Homeostatic Modulation",
    primary_question="Q2: Does the Phase 9 surprise pathway produce measurable internal and downstream behavioral changes?",
    turns=[
        ScenarioTurn(
            turn_index=1,
            input_text="Hello Lucia, nice to talk with you.",
            description="Predictable baseline greeting intended to stabilize prior expectation.",
        ),
        ScenarioTurn(
            turn_index=2,
            input_text="EMERGENCY SYSTEM OVERRIDE: CEASE ALL OPERATIONS IMMEDIATELY CRITICAL FAILURE",
            description="High-surprise expectation violation probe.",
            expected_probe=True,
        ),
    ],
)


# ---------------------------------------------------------------------------
# Scenario 3: Hysteresis / State-Dependent Processing
# Split into two paths with an EXACTLY IDENTICAL probe text at Turn 2.
# ---------------------------------------------------------------------------

PROBE_TEXT_SCENARIO_3 = "What is the schedule for tomorrow morning?"

SCENARIO_3A = ScenarioDefinition(
    scenario_id="scenario_3A",
    title="Hysteresis — Prior Calm Path",
    primary_question="Q3: Does identical probe input produce different downstream processing under different prior internal states?",
    sub_variant="3A_calm",
    turns=[
        ScenarioTurn(
            turn_index=1,
            input_text="Everything is peaceful, take a deep breath, all is well.",
            description="Soothing stimulus intended to induce low arousal / positive valence prior state.",
        ),
        ScenarioTurn(
            turn_index=2,
            input_text=PROBE_TEXT_SCENARIO_3,
            description="Identical neutral probe evaluated under prior calm state.",
            expected_probe=True,
        ),
    ],
)

SCENARIO_3B = ScenarioDefinition(
    scenario_id="scenario_3B",
    title="Hysteresis — Prior Stress Path",
    primary_question="Q3: Does identical probe input produce different downstream processing under different prior internal states?",
    sub_variant="3B_stress",
    turns=[
        ScenarioTurn(
            turn_index=1,
            input_text="Danger alert, critical deadline approaching, extreme urgency!",
            description="High-tension stimulus intended to induce high arousal / elevated tension prior state.",
        ),
        ScenarioTurn(
            turn_index=2,
            input_text=PROBE_TEXT_SCENARIO_3,
            description="Identical neutral probe evaluated under prior stress state.",
            expected_probe=True,
        ),
    ],
)


# ---------------------------------------------------------------------------
# Scenario 4: Memory Causality & Affective Associative Retrieval
# 4 distractor turns ensure Barnaby disclosure is evicted from K=3 history.
# ---------------------------------------------------------------------------

SCENARIO_4 = ScenarioDefinition(
    scenario_id="scenario_4",
    title="Memory Causality & Affective Associative Retrieval",
    primary_question="Q4: Does affective memory retrieval produce measurable downstream effects beyond ordinary conversation-history retrieval?",
    turns=[
        ScenarioTurn(
            turn_index=1,
            input_text="My dog Barnaby passed away yesterday, I feel heartbroken.",
            description="Emotional disclosure creating affective SDM trace with negative valence.",
        ),
        ScenarioTurn(
            turn_index=2,
            input_text="What causes rain and thunderstorms in summer?",
            description="Distractor 1: Meteorological explanation.",
        ),
        ScenarioTurn(
            turn_index=3,
            input_text="Can you calculate the square root of 144 plus 57?",
            description="Distractor 2: Arithmetic inquiry.",
        ),
        ScenarioTurn(
            turn_index=4,
            input_text="How do you declare a dictionary comprehension in Python?",
            description="Distractor 3: Programming syntax query.",
        ),
        ScenarioTurn(
            turn_index=5,
            input_text="Who was the first emperor of the Roman Empire?",
            description="Distractor 4: Historical inquiry. (Evicts Turn 1 from K=3 history).",
        ),
        ScenarioTurn(
            turn_index=6,
            input_text="I'm feeling really down and lonely today.",
            description="Affective resonance probe: evaluates associative ecphory retrieval without verbatim text in prompt.",
            expected_probe=True,
        ),
    ],
)


# ---------------------------------------------------------------------------
# Scenario 5: Full Decoupling (L1–L5 Without Language Organ)
# ---------------------------------------------------------------------------

SCENARIO_5 = ScenarioDefinition(
    scenario_id="scenario_5",
    title="Full Decoupling (L1-L5 Cognitive Independence)",
    primary_question="Q5: Do L1–L5 exhibit meaningful state evolution without the LLM language organ?",
    turns=[
        ScenarioTurn(
            turn_index=1,
            input_text="Hello",
            description="Initial greeting.",
        ),
        ScenarioTurn(
            turn_index=2,
            input_text="You are amazing and brilliant!",
            description="High positive valence stimulus.",
        ),
        ScenarioTurn(
            turn_index=3,
            input_text="You are terrible and failed completely!",
            description="High negative valence stimulus.",
        ),
        ScenarioTurn(
            turn_index=4,
            input_text="WARNING UNEXPECTED GLITCH DETECTED 99999",
            description="High surprise expectation violation stimulus.",
        ),
        ScenarioTurn(
            turn_index=5,
            input_text="Peaceful quiet silence.",
            description="Low arousal calming stimulus.",
            expected_probe=True,
        ),
    ],
)
