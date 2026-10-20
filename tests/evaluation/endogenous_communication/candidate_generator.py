"""
tests/evaluation/endogenous_communication/candidate_generator.py

Generators for both User-Driven and Endogenous Communicative Candidates.
Keeps state, reason, and candidate formation strictly distinct.
"""

from __future__ import annotations

from typing import List, Optional, Set
from .models import (
    CandidateOrigin,
    CognitiveContext,
    CommunicativeAct,
    CommunicativeCandidate,
    DialogueEnvironment,
    GroundedReason,
    ReasonType,
)
from .grounding import GroundingVerifier


class UserCandidateGenerator:
    """Forms communicative candidates directly addressing explicit user requests."""

    def generate(self, env: DialogueEnvironment) -> List[CommunicativeCandidate]:
        text = env.user_input.strip()
        if not text:
            return []

        candidates: List[CommunicativeCandidate] = []
        lower = text.lower()

        # Check for greeting
        if any(w in lower for w in ("hello", "hi", "hey", "chào")):
            reason = GroundedReason(
                reason_type=ReasonType.USER_QUERY,
                source_id="user:greeting",
                subject="ent:user",
                predicate="c:GREET",
                object_val="lucia",
                salience=1.0,
            )
            candidates.append(
                CommunicativeCandidate(
                    id=f"user_cand:greet_{hash(text) % 10000}",
                    origin=CandidateOrigin.USER_DRIVEN,
                    grounds=(reason,),
                    target="user",
                    act=CommunicativeAct.GREET,
                    intended_effect="acknowledge_conversational_opening",
                    urgency=0.7,
                )
            )

        # Check for direct question / factual request
        elif "?" in text or any(lower.startswith(w) for w in ("what", "who", "where", "how", "why", "can you")):
            reason = GroundedReason(
                reason_type=ReasonType.USER_QUERY,
                source_id=f"user:query_{hash(text) % 10000}",
                subject="ent:user",
                predicate="c:INQUIRY",
                object_val=text,
                salience=1.0,
            )
            candidates.append(
                CommunicativeCandidate(
                    id=f"user_cand:answer_{hash(text) % 10000}",
                    origin=CandidateOrigin.USER_DRIVEN,
                    grounds=(reason,),
                    target="user",
                    act=CommunicativeAct.ANSWER,
                    intended_effect="satisfy_user_inquiry",
                    urgency=0.9,
                )
            )
        else:
            # General statement
            reason = GroundedReason(
                reason_type=ReasonType.CONVERSATIONAL_OBLIGATION,
                source_id=f"user:statement_{hash(text) % 10000}",
                subject="ent:user",
                predicate="c:SHARING",
                object_val=text,
                salience=0.8,
            )
            candidates.append(
                CommunicativeCandidate(
                    id=f"user_cand:ack_{hash(text) % 10000}",
                    origin=CandidateOrigin.USER_DRIVEN,
                    grounds=(reason,),
                    target="user",
                    act=CommunicativeAct.ACKNOWLEDGE,
                    intended_effect="attentive_listening_acknowledgment",
                    urgency=0.6,
                )
            )

        return candidates


class EndogenousCandidateGenerator:
    """
    Forms communicative candidates originating from Lucia's internal cognitive state.
    CRITICAL: State intensity alone CANNOT form a candidate; explicit grounded reasons are mandatory.
    """

    def __init__(
        self,
        grounding_verifier: Optional[GroundingVerifier] = None,
        min_salience_threshold: float = 0.40,
        inhibition_decay: float = 0.50,
    ) -> None:
        self.verifier = grounding_verifier or GroundingVerifier()
        self.min_salience_threshold = min_salience_threshold
        self.inhibition_decay = inhibition_decay

    def generate(
        self,
        context: CognitiveContext,
        env: DialogueEnvironment,
        existing_pool: Optional[List[CommunicativeCandidate]] = None,
    ) -> List[CommunicativeCandidate]:
        candidates: List[CommunicativeCandidate] = []

        # 1. Update persistence & inhibition of existing active candidates
        if existing_pool:
            for cand in existing_pool:
                if cand.origin == CandidateOrigin.ENDOGENOUS:
                    cand.persistence += 1
                    # Decay inhibition over turns
                    cand.inhibition = max(0.0, cand.inhibition - self.inhibition_decay)
                    # Re-verify validity against current context
                    valid, _ = self.verifier.verify_candidate_grounding(cand, context)
                    cand.validity = valid
                    if valid and cand.persistence <= 5:  # max persistence horizon
                        candidates.append(cand)

        # 2. Extract salient grounded reasons from context
        salient_reasons = self.verifier.extract_salient_reasons(
            context, min_salience_threshold=self.min_salience_threshold
        )

        for reason in salient_reasons:
            # Check if this reason is already represented in an active candidate
            already_active = any(
                any(g.source_id == reason.source_id for g in c.grounds)
                for c in candidates
            )
            if already_active:
                continue

            # Determine act and intended effect based on reason type
            if reason.reason_type == ReasonType.RELATIONAL_EVENT:
                if "tension" in reason.predicate.lower() or "rupture" in reason.predicate.lower():
                    act = CommunicativeAct.REPAIR
                    intended_effect = "restore_interaction_alignment"
                    urgency = 0.85
                elif "milestone" in reason.predicate.lower() or "celebration" in reason.predicate.lower():
                    act = CommunicativeAct.SHARE
                    intended_effect = "acknowledge_shared_milestone"
                    urgency = 0.65
                else:
                    act = CommunicativeAct.SHARE
                    intended_effect = "relational_connection"
                    urgency = 0.50

            elif reason.reason_type == ReasonType.EPISTEMIC_GAP:
                act = CommunicativeAct.INQUIRE
                intended_effect = "resolve_epistemic_contradiction"
                urgency = 0.75

            elif reason.reason_type == ReasonType.AFFECTIVE_HOMEOSTASIS:
                act = CommunicativeAct.SHARE
                intended_effect = "express_pre_reflective_attunement"
                urgency = 0.40
            else:
                act = CommunicativeAct.ASSERT
                intended_effect = "express_grounded_assertion"
                urgency = 0.50

            # Calculate initial inhibition based on recent attempted purposes
            initial_inhibition = 0.90 if intended_effect in env.recent_attempted_purposes else 0.0

            cand = CommunicativeCandidate(
                id=f"endo_cand:{reason.source_id}",
                origin=CandidateOrigin.ENDOGENOUS,
                grounds=(reason,),
                target="user",
                act=act,
                intended_effect=intended_effect,
                validity=True,
                persistence=0,
                inhibition=initial_inhibition,
                confidence=1.0,
                urgency=urgency,
            )
            candidates.append(cand)

        return candidates
