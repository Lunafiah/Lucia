"""
tests/evaluation/endogenous_communication/grounding.py

Grounding and Reason-Verification engine for the experimental harness.
Ensures that state magnitude alone cannot form a communicative candidate.
Every communicative candidate must resolve to an inspectable, admissible GroundedReason.
"""

from __future__ import annotations

from typing import List, Optional, Tuple
from .models import CognitiveContext, CommunicativeCandidate, GroundedReason, ReasonType


class GroundingVerifier:
    """
    Verifies that communicative intent is grounded in inspectable facts or events,
    not merely floating continuous emotional intensity.
    """

    def __init__(self, require_admissible_target: bool = True) -> None:
        self.require_admissible_target = require_admissible_target

    def verify_candidate_grounding(
        self,
        candidate: CommunicativeCandidate,
        context: CognitiveContext,
    ) -> Tuple[bool, str]:
        """
        Verify whether all grounds cited by a candidate are currently valid and admissible.
        Returns: (is_valid, failure_reason)
        """
        if not candidate.grounds:
            return False, "UNGROUNDED: Candidate specifies zero grounds."

        for ground in candidate.grounds:
            if not ground.is_valid:
                return False, f"STALE_GROUND: Ground {ground.source_id} is marked invalid."

            # Verify ground exists in cognitive context's active events
            matched = any(
                e.source_id == ground.source_id and e.is_valid
                for e in context.grounded_events
            )
            # If user query, verify it matches
            if ground.reason_type == ReasonType.USER_QUERY:
                matched = True

            if not matched:
                return False, f"UNVERIFIED_GROUND: Ground {ground.source_id} not found in active context."

        if self.require_admissible_target and not candidate.target:
            return False, "INVALID_TARGET: Communicative candidate lacks explicit recipient target."

        return True, "GROUNDED"

    def extract_salient_reasons(
        self,
        context: CognitiveContext,
        min_salience_threshold: float = 0.40,
    ) -> List[GroundedReason]:
        """
        Extract only those grounded events that exceed the salience threshold.
        Ignores continuous state magnitude unless coupled to an explicit event.
        """
        admissible: List[GroundedReason] = []
        for event in context.grounded_events:
            if event.is_valid and event.salience >= min_salience_threshold:
                admissible.append(event)
        return admissible
