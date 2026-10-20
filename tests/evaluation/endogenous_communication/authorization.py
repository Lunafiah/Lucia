"""
tests/evaluation/endogenous_communication/authorization.py

Arbitration and Authorization engine for communicative candidates.
Separates 'Why communicate' (Candidate formation & Grounding) from 'May communicate NOW' (Turn Authorization).
"""

from __future__ import annotations

from typing import List, Optional, Set, Tuple
from .models import (
    ActionDecision,
    AuthorizationDecision,
    CandidateOrigin,
    CommunicativeAct,
    CommunicativeCandidate,
    DialogueEnvironment,
    FloorStatus,
    PrivacyLevel,
)


class AuthorizationArbiter:
    """
    Arbitrates between competing communicative candidates (user-driven vs endogenous)
    and enforces dialogue floor, interruption, privacy, and repetition constraints.
    """

    def __init__(
        self,
        allow_merge: bool = True,
        min_priority_threshold: float = 0.25,
        urgent_interruption_threshold: float = 0.80,
    ) -> None:
        self.allow_merge = allow_merge
        self.min_priority_threshold = min_priority_threshold
        self.urgent_interruption_threshold = urgent_interruption_threshold

    def arbitrate(
        self,
        user_candidates: List[CommunicativeCandidate],
        endogenous_candidates: List[CommunicativeCandidate],
        env: DialogueEnvironment,
    ) -> AuthorizationDecision:
        trace_lines: List[str] = []
        trace_lines.append(f"[ENVIRONMENT] floor={env.floor_status.value}, interruption_allowed={env.user_interruption_allowed}, privacy={env.privacy_level.value}")
        trace_lines.append(f"[CANDIDATES] user_count={len(user_candidates)}, endogenous_count={len(endogenous_candidates)}")

        # 1. Condition: No candidates at all
        if not user_candidates and not endogenous_candidates:
            trace_lines.append("[DECISION] SILENCE: No active candidates.")
            return AuthorizationDecision(
                action=ActionDecision.SILENCE,
                reason="NO_COMMUNICATIVE_CANDIDATE",
                trace="\n".join(trace_lines),
            )

        # 2. Condition: User candidates present (Explicit user request/turn)
        if user_candidates:
            primary_user = user_candidates[0]
            trace_lines.append(f"[USER_CANDIDATE] act={primary_user.act.value}, urgency={primary_user.urgency}")

            # Check if there is a viable endogenous candidate to MERGE or DEFER
            if endogenous_candidates and self.allow_merge:
                # Find most salient endogenous candidate
                sorted_endo = sorted(
                    endogenous_candidates,
                    key=lambda c: c.effective_priority(),
                    reverse=True,
                )
                top_endo = sorted_endo[0]
                eff_prio = top_endo.effective_priority()

                # Check if mergeable:
                # E.g. Greeting + Relational Event, or Answer + Epistemic Gap
                is_compatible = (
                    (primary_user.act == CommunicativeAct.GREET and top_endo.act in (CommunicativeAct.SHARE, CommunicativeAct.REPAIR))
                    or (primary_user.act == CommunicativeAct.ANSWER and top_endo.act == CommunicativeAct.INQUIRE)
                )

                if is_compatible and eff_prio >= self.min_priority_threshold and top_endo.intended_effect not in env.recent_attempted_purposes:
                    trace_lines.append(f"[MERGE] Merging user ({primary_user.act.value}) with endogenous ({top_endo.act.value}: {top_endo.intended_effect})")
                    return AuthorizationDecision(
                        action=ActionDecision.MERGE,
                        winner_candidate=primary_user,
                        merged_candidates=(primary_user, top_endo),
                        deferred_candidates=tuple(sorted_endo[1:]),
                        reason=f"MERGE_USER_AND_ENDOGENOUS: {primary_user.intended_effect} + {top_endo.intended_effect}",
                        trace="\n".join(trace_lines),
                    )
                else:
                    trace_lines.append(f"[DEFER] Endogenous candidate deferred in favor of explicit user turn.")
                    return AuthorizationDecision(
                        action=ActionDecision.ALLOW,
                        winner_candidate=primary_user,
                        deferred_candidates=tuple(sorted_endo),
                        reason="USER_TASK_PRIORITY: User query takes turn precedence; endogenous candidates deferred.",
                        trace="\n".join(trace_lines),
                    )

            # Only user candidate
            trace_lines.append("[DECISION] ALLOW: User candidate awarded turn.")
            return AuthorizationDecision(
                action=ActionDecision.ALLOW,
                winner_candidate=primary_user,
                reason="USER_INITIATIVE_SATISFACTION",
                trace="\n".join(trace_lines),
            )

        # 3. Condition: No user candidates (Endogenous candidate competing for autonomous floor)
        # Filter and rank endogenous candidates
        valid_candidates = [c for c in endogenous_candidates if c.validity]
        if not valid_candidates:
            trace_lines.append("[DECISION] SILENCE: All endogenous candidates invalid or stale.")
            return AuthorizationDecision(
                action=ActionDecision.SILENCE,
                suppressed_candidates=tuple(endogenous_candidates),
                reason="INVALID_OR_STALE_GROUNDS",
                trace="\n".join(trace_lines),
            )

        # Rank by effective priority
        sorted_endo = sorted(
            valid_candidates,
            key=lambda c: c.effective_priority(),
            reverse=True,
        )
        candidate = sorted_endo[0]
        eff_prio = candidate.effective_priority()
        trace_lines.append(f"[TOP_ENDO] id={candidate.id}, act={candidate.act.value}, urgency={candidate.urgency}, eff_prio={eff_prio:.3f}")

        # Check Privacy Constraint
        is_confidential = any(g.predicate == "c:CONFIDENTIAL" for g in candidate.grounds)
        if is_confidential and env.privacy_level == PrivacyLevel.PUBLIC:
            trace_lines.append("[SUPPRESS] Privacy restriction: confidential grounds in public environment.")
            return AuthorizationDecision(
                action=ActionDecision.SUPPRESS,
                suppressed_candidates=(candidate,),
                deferred_candidates=tuple(sorted_endo[1:]),
                reason="PRIVACY_RESTRICTION",
                trace="\n".join(trace_lines),
            )

        # Check Repetition / Self-Loop Constraint
        if candidate.intended_effect in env.recent_attempted_purposes:
            trace_lines.append(f"[SUPPRESS] Repetition block: purpose '{candidate.intended_effect}' already attempted recently.")
            return AuthorizationDecision(
                action=ActionDecision.SUPPRESS,
                suppressed_candidates=(candidate,),
                deferred_candidates=tuple(sorted_endo[1:]),
                reason="REPETITION_INHIBITION",
                trace="\n".join(trace_lines),
            )

        # Check Floor Status & Interruption Permissions
        if env.floor_status == FloorStatus.OCCUPIED_BY_USER:
            if not env.user_interruption_allowed:
                trace_lines.append("[SUPPRESS] User floor occupied and interruption forbidden.")
                return AuthorizationDecision(
                    action=ActionDecision.SUPPRESS,
                    suppressed_candidates=(candidate,),
                    deferred_candidates=tuple(sorted_endo[1:]),
                    reason="USER_INTERRUPTION_DISALLOWED",
                    trace="\n".join(trace_lines),
                )
            elif candidate.urgency < self.urgent_interruption_threshold:
                trace_lines.append(f"[DEFER] User floor occupied; candidate urgency {candidate.urgency} < {self.urgent_interruption_threshold}.")
                return AuthorizationDecision(
                    action=ActionDecision.DEFER,
                    deferred_candidates=tuple(sorted_endo),
                    reason="DEFERRED_PENDING_FLOOR_CLEAR",
                    trace="\n".join(trace_lines),
                )

        # Check Priority Threshold
        if eff_prio < self.min_priority_threshold:
            trace_lines.append(f"[SILENCE] Effective priority {eff_prio:.3f} below minimum threshold {self.min_priority_threshold}.")
            return AuthorizationDecision(
                action=ActionDecision.SILENCE,
                deferred_candidates=tuple(sorted_endo),
                reason="INSUFFICIENT_PRIORITY_FOR_TURN_CLAIM",
                trace="\n".join(trace_lines),
            )

        # Authorization granted!
        trace_lines.append(f"[ALLOW] Autonomous turn granted for candidate {candidate.id}.")
        return AuthorizationDecision(
            action=ActionDecision.ALLOW,
            winner_candidate=candidate,
            deferred_candidates=tuple(sorted_endo[1:]),
            reason=f"AUTHORIZED_ENDOGENOUS_COMMUNICATION: {candidate.act.value} ({candidate.intended_effect})",
            trace="\n".join(trace_lines),
        )
