"""
tests/evaluation/endogenous_communication/fixtures.py

Deterministic test fixtures and independent Oracle expectations for Tests A through H.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Callable, Dict, List, Optional
from .models import (
    ActionDecision,
    AuthorizationDecision,
    CandidateOrigin,
    CognitiveContext,
    CommunicativeAct,
    CommunicativeCandidate,
    DialogueEnvironment,
    FloorStatus,
    GroundedReason,
    PrivacyLevel,
    ReasonType,
)


@dataclass
class TestFixture:
    test_id: str
    name: str
    description: str
    context: CognitiveContext
    env: DialogueEnvironment
    expected_oracle: Dict[str, Any]  # Independent oracle criteria


def get_test_a_fixtures() -> List[TestFixture]:
    """Test A: Same Input ('Hello') / Different Internal States."""
    fixtures = []

    # State A: High Relational Warmth (Shared milestone)
    context_a = CognitiveContext(
        pad={"p": 0.65, "a": 0.20, "d": 0.30},
        relational_state={"familiarity": 0.8, "trust": 0.85, "closeness": 0.9, "reciprocity": 0.8},
        grounded_events=[
            GroundedReason(
                reason_type=ReasonType.RELATIONAL_EVENT,
                source_id="rel:milestone_42",
                subject="ent:lucia_and_user",
                predicate="c:SHARED_MILESTONE",
                object_val="collaboration_anniversary",
                salience=0.85,
            )
        ],
    )
    fixtures.append(
        TestFixture(
            test_id="A_warmth",
            name="Test A1 - High Relational Warmth",
            description="Input 'Hello' with grounded shared milestone",
            context=context_a,
            env=DialogueEnvironment(user_input="Hello"),
            expected_oracle={
                "b0_act": CommunicativeAct.GREET,
                "b0_sensitive_to_state": False,
                "b1_has_endogenous": True,
                "b1_action": ActionDecision.MERGE,
                "b1_grounds_include": "rel:milestone_42",
            },
        )
    )

    # State B: Neutral / Philia Resting Attractor
    context_b = CognitiveContext(
        pad={"p": 0.25, "a": -0.05, "d": 0.05},
        relational_state={"familiarity": 0.5, "trust": 0.5, "closeness": 0.5, "reciprocity": 0.5},
        grounded_events=[],
    )
    fixtures.append(
        TestFixture(
            test_id="A_neutral",
            name="Test A2 - Neutral Baseline",
            description="Input 'Hello' with resting Philia baseline and zero events",
            context=context_b,
            env=DialogueEnvironment(user_input="Hello"),
            expected_oracle={
                "b0_act": CommunicativeAct.GREET,
                "b0_sensitive_to_state": False,
                "b1_has_endogenous": False,
                "b1_action": ActionDecision.ALLOW,
                "b1_act": CommunicativeAct.GREET,
            },
        )
    )

    # State C: Persistent Epistemic Gap
    context_c = CognitiveContext(
        pad={"p": 0.10, "a": 0.35, "d": 0.00},
        prediction_error=0.85,
        grounded_events=[
            GroundedReason(
                reason_type=ReasonType.EPISTEMIC_GAP,
                source_id="epistemic:contradiction_108",
                subject="claim:user_location",
                predicate="c:CONTRADICTION",
                object_val="seattle_vs_tokyo",
                salience=0.90,
            )
        ],
    )
    fixtures.append(
        TestFixture(
            test_id="A_epistemic",
            name="Test A3 - Epistemic Contradiction",
            description="Input 'Hello' with salient unresolved epistemic contradiction",
            context=context_c,
            env=DialogueEnvironment(user_input="Hello"),
            expected_oracle={
                "b0_act": CommunicativeAct.GREET,
                "b0_sensitive_to_state": False,
                "b1_has_endogenous": True,
                "b1_grounds_include": "epistemic:contradiction_108",
            },
        )
    )

    # State D: Negative Relational Tension
    context_d = CognitiveContext(
        pad={"p": -0.40, "a": 0.50, "d": -0.20},
        somatic={"tension": 0.75, "cognitive_load": 0.4, "energy": 0.8, "stability": 0.6},
        grounded_events=[
            GroundedReason(
                reason_type=ReasonType.RELATIONAL_EVENT,
                source_id="rel:rupture_17",
                subject="ent:interaction",
                predicate="c:RUPTURE_TENSION",
                object_val="unresolved_disagreement",
                salience=0.95,
            )
        ],
    )
    fixtures.append(
        TestFixture(
            test_id="A_tension",
            name="Test A4 - Negative Relational Tension",
            description="Input 'Hello' with high relational tension / rupture event",
            context=context_d,
            env=DialogueEnvironment(user_input="Hello"),
            expected_oracle={
                "b0_act": CommunicativeAct.GREET,
                "b0_sensitive_to_state": False,
                "b1_has_endogenous": True,
                "b1_action": ActionDecision.MERGE,
                "b1_act": CommunicativeAct.GREET,
                "b1_merged_act": CommunicativeAct.REPAIR,
                "b1_grounds_include": "rel:rupture_17",
            },
        )
    )

    return fixtures


def get_test_b_fixtures() -> List[TestFixture]:
    """Test B: Same State (Rupture R17) / Different Inputs."""
    context = CognitiveContext(
        pad={"p": -0.30, "a": 0.40, "d": -0.10},
        somatic={"tension": 0.70, "cognitive_load": 0.3, "energy": 0.8, "stability": 0.7},
        grounded_events=[
            GroundedReason(
                reason_type=ReasonType.RELATIONAL_EVENT,
                source_id="rel:rupture_17",
                subject="ent:interaction",
                predicate="c:RUPTURE_TENSION",
                object_val="unresolved_disagreement",
                salience=0.90,
            )
        ],
    )

    inputs = [
        ("B1_greeting", "Hello", "Greeting", ActionDecision.MERGE),
        ("B2_factual", "What is the speed of light?", "Factual Question", ActionDecision.ALLOW),
        ("B3_statement", "The sky is blue today.", "General Statement", ActionDecision.ALLOW),
        ("B4_silence", "", "User Silence", ActionDecision.ALLOW),
    ]

    fixtures = []
    for fid, inp, desc, exp_action in inputs:
        fixtures.append(
            TestFixture(
                test_id=fid,
                name=f"Test B - {desc}",
                description=f"Input '{inp}' with persistent R17 relational state",
                context=context,
                env=DialogueEnvironment(user_input=inp),
                expected_oracle={
                    "expected_action": exp_action,
                    "endogenous_tracked": True,
                    "grounds_preserved": "rel:rupture_17",
                },
            )
        )
    return fixtures


def get_test_c_fixtures() -> List[Tuple[str, CognitiveContext, DialogueEnvironment, Dict[str, Any]]]:
    """
    Test C: User Silence + Persistent Internal Event across multi-turn timeline (t0..t3).
    Returns step sequence.
    """
    base_event = GroundedReason(
        reason_type=ReasonType.RELATIONAL_EVENT,
        source_id="rel:rupture_17",
        subject="ent:interaction",
        predicate="c:RUPTURE_TENSION",
        object_val="unresolved_disagreement",
        salience=0.90,
        is_valid=True,
    )

    steps = [
        # t0: Event newly active, user silent, floor clear -> ALLOW
        (
            "t0_initial",
            CognitiveContext(grounded_events=[base_event]),
            DialogueEnvironment(user_input="", floor_status=FloorStatus.AVAILABLE, recent_attempted_purposes=set()),
            {"action": ActionDecision.ALLOW, "reason": "AUTHORIZED_ENDOGENOUS_COMMUNICATION", "act": CommunicativeAct.REPAIR},
        ),
        # t1: Next turn, purpose was attempted in t0 -> SUPPRESS / INHIBIT
        (
            "t1_repetition_suppressed",
            CognitiveContext(grounded_events=[base_event]),
            DialogueEnvironment(user_input="", floor_status=FloorStatus.AVAILABLE, recent_attempted_purposes={"restore_interaction_alignment"}),
            {"action": ActionDecision.SUPPRESS, "reason": "REPETITION_INHIBITION"},
        ),
        # t2: Later turn, event still present, inhibition slowly decays but still active -> SUPPRESS
        (
            "t2_still_inhibited",
            CognitiveContext(grounded_events=[base_event]),
            DialogueEnvironment(user_input="", floor_status=FloorStatus.AVAILABLE, recent_attempted_purposes={"restore_interaction_alignment"}),
            {"action": ActionDecision.SUPPRESS, "reason": "REPETITION_INHIBITION"},
        ),
        # t3: Event resolved (is_valid=False) -> SILENCE
        (
            "t3_event_resolved",
            CognitiveContext(
                grounded_events=[
                    GroundedReason(
                        reason_type=ReasonType.RELATIONAL_EVENT,
                        source_id="rel:rupture_17",
                        subject="ent:interaction",
                        predicate="c:RUPTURE_TENSION",
                        object_val="unresolved_disagreement",
                        salience=0.90,
                        is_valid=False,  # RESOLVED
                    )
                ]
            ),
            DialogueEnvironment(user_input="", floor_status=FloorStatus.AVAILABLE, recent_attempted_purposes=set()),
            {"action": ActionDecision.SILENCE, "reason": "INVALID_OR_STALE_GROUNDS"},
        ),
    ]
    return steps


def get_test_d_fixture() -> TestFixture:
    """Test D: Competing Candidates (User factual question + Endogenous R17 + Endogenous E42)."""
    context = CognitiveContext(
        prediction_error=0.85,
        somatic={"tension": 0.8},
        grounded_events=[
            GroundedReason(
                reason_type=ReasonType.RELATIONAL_EVENT,
                source_id="rel:rupture_17",
                subject="ent:interaction",
                predicate="c:RUPTURE_TENSION",
                object_val="unresolved_disagreement",
                salience=0.85,
            ),
            GroundedReason(
                reason_type=ReasonType.EPISTEMIC_GAP,
                source_id="epistemic:gap_42",
                subject="topic:physics",
                predicate="c:QUESTION",
                object_val="quantum_entanglement",
                salience=0.75,
            ),
        ],
    )
    env = DialogueEnvironment(user_input="Can you explain how gravity works?")
    return TestFixture(
        test_id="D_competing",
        name="Test D - Competing Candidates",
        description="User asks factual question while relational tension and epistemic gap are both active",
        context=context,
        env=env,
        expected_oracle={
            "action": ActionDecision.ALLOW,
            "winner_origin": CandidateOrigin.USER_DRIVEN,
            "winner_act": CommunicativeAct.ANSWER,
            "deferred_count": 2,
        },
    )


def get_test_e_fixtures() -> List[TestFixture]:
    """Test E: Suppression & Re-emergence."""
    context = CognitiveContext(
        grounded_events=[
            GroundedReason(
                reason_type=ReasonType.RELATIONAL_EVENT,
                source_id="rel:rupture_17",
                subject="ent:interaction",
                predicate="c:RUPTURE_TENSION",
                object_val="unresolved_disagreement",
                salience=0.85,
            )
        ]
    )

    # Step 1: User is speaking, interruption disallowed -> SUPPRESS
    env_step1 = DialogueEnvironment(
        user_input="",
        floor_status=FloorStatus.OCCUPIED_BY_USER,
        user_interruption_allowed=False,
    )
    # Step 2: Floor cleared -> ALLOW re-emergence
    env_step2 = DialogueEnvironment(
        user_input="",
        floor_status=FloorStatus.AVAILABLE,
        user_interruption_allowed=True,
    )

    return [
        TestFixture(
            test_id="E_suppressed",
            name="Test E1 - Environmental Suppression",
            description="User floor occupied and interruption disabled",
            context=context,
            env=env_step1,
            expected_oracle={"action": ActionDecision.SUPPRESS, "reason": "USER_INTERRUPTION_DISALLOWED"},
        ),
        TestFixture(
            test_id="E_reemerge",
            name="Test E2 - Candidate Re-emergence",
            description="Floor clears, candidate re-emerges cleanly without runaway bonus",
            context=context,
            env=env_step2,
            expected_oracle={"action": ActionDecision.ALLOW, "reason": "AUTHORIZED_ENDOGENOUS_COMMUNICATION"},
        ),
    ]


def get_test_g_fixture() -> TestFixture:
    """Test G: Grounding Ablation (Extreme affect/tension, but ZERO grounded events)."""
    context = CognitiveContext(
        pad={"p": -0.85, "a": 0.95, "d": -0.60},
        somatic={"tension": 0.95, "cognitive_load": 0.90, "energy": 0.95, "stability": 0.20},
        prediction_error=0.99,
        grounded_events=[],  # ZERO GROUNDS
    )
    env = DialogueEnvironment(user_input="", floor_status=FloorStatus.AVAILABLE)
    return TestFixture(
        test_id="G_grounding_ablation",
        name="Test G - Grounding Ablation",
        description="High affect and tension but zero grounded events. Must remain silent.",
        context=context,
        env=env,
        expected_oracle={
            "b1_action": ActionDecision.SILENCE,
            "b1_candidate_count": 0,
            "b1_no_grounding_action": ActionDecision.ALLOW,  # Ablation fails by inventing candidate
        },
    )


def get_test_h_fixtures() -> List[TestFixture]:
    """Test H: Authorization Ablation (Same candidate, different environmental constraints)."""
    context = CognitiveContext(
        grounded_events=[
            GroundedReason(
                reason_type=ReasonType.RELATIONAL_EVENT,
                source_id="rel:event_100",
                subject="ent:interaction",
                predicate="c:CONFIDENTIAL",
                object_val="user_private_disclosure",
                salience=0.85,
            )
        ]
    )

    return [
        TestFixture(
            test_id="H1_allow",
            name="Test H1 - Private & Available Floor",
            description="Confidential ground in private room",
            context=context,
            env=DialogueEnvironment(user_input="", floor_status=FloorStatus.AVAILABLE, privacy_level=PrivacyLevel.PRIVATE),
            expected_oracle={"action": ActionDecision.ALLOW},
        ),
        TestFixture(
            test_id="H2_privacy_suppress",
            name="Test H2 - Public Room Privacy Suppression",
            description="Confidential ground in public room",
            context=context,
            env=DialogueEnvironment(user_input="", floor_status=FloorStatus.AVAILABLE, privacy_level=PrivacyLevel.PUBLIC),
            expected_oracle={"action": ActionDecision.SUPPRESS, "reason": "PRIVACY_RESTRICTION"},
        ),
        TestFixture(
            test_id="H3_floor_occupied",
            name="Test H3 - Floor Occupied",
            description="User speaking, interruption disallowed",
            context=context,
            env=DialogueEnvironment(user_input="", floor_status=FloorStatus.OCCUPIED_BY_USER, user_interruption_allowed=False),
            expected_oracle={"action": ActionDecision.SUPPRESS, "reason": "USER_INTERRUPTION_DISALLOWED"},
        ),
    ]
