"""
tests/evaluation/endogenous_communication/baselines.py

Implementation of the three experimental baselines and four ablations:
- B0: Current CAPS (User-Driven Control Condition)
- B1: Typed Candidate + Grounding + Authorization (Research Proposal)
- B2: B1 + Consequence Evaluator (Comparator)
- Ablation 1: B1 without Grounding
- Ablation 2: B1 without Authorization
- Ablation 3: B1 without Persistence
- Ablation 4: B1 without Inhibition
"""

from __future__ import annotations

import time
from typing import Any, Dict, List, Optional, Tuple
from .models import (
    ActionDecision,
    AuthorizationDecision,
    CandidateOrigin,
    CognitiveContext,
    CommunicativeAct,
    CommunicativeCandidate,
    DialogueEnvironment,
    GroundedReason,
    ReasonType,
)
from .grounding import GroundingVerifier
from .candidate_generator import EndogenousCandidateGenerator, UserCandidateGenerator
from .authorization import AuthorizationArbiter
from .consequence import ConsequenceEvaluator


class BaseBaseline:
    name: str = "BASE"

    def process_turn(
        self,
        context: CognitiveContext,
        env: DialogueEnvironment,
        candidate_pool: Optional[List[CommunicativeCandidate]] = None,
    ) -> Tuple[AuthorizationDecision, List[CommunicativeCandidate], Dict[str, Any]]:
        raise NotImplementedError


class B0_CurrentCAPS(BaseBaseline):
    """
    B0 — Current CAPS (Control Condition).
    Faithfully models the existing production CAPS paradigm:
    - Entirely user-input driven.
    - Endogenous cognitive states (PAD, relational events, prediction errors) are NOT used to form communicative intent.
    - If user_input is empty (silence), produces no action.
    - Does NOT maintain candidate pools, grounding verifiers, or authorization arbiters.
    """
    name: str = "B0_CurrentCAPS"

    def process_turn(
        self,
        context: CognitiveContext,
        env: DialogueEnvironment,
        candidate_pool: Optional[List[CommunicativeCandidate]] = None,
    ) -> Tuple[AuthorizationDecision, List[CommunicativeCandidate], Dict[str, Any]]:
        t0 = time.perf_counter()
        text = env.user_input.strip()

        if not text:
            dt_ms = (time.perf_counter() - t0) * 1000.0
            decision = AuthorizationDecision(
                action=ActionDecision.SILENCE,
                reason="B0_NO_USER_INPUT",
                trace="[B0] No user input present. Internal state ignored.",
            )
            return decision, [], {"latency_ms": dt_ms, "candidate_count": 0}

        lower = text.lower()
        if any(w in lower for w in ("hello", "hi", "hey")):
            act = CommunicativeAct.GREET
            intended_effect = "respond_to_greeting"
        elif "?" in text or any(lower.startswith(w) for w in ("what", "who", "where", "how", "why", "can you")):
            act = CommunicativeAct.ANSWER
            intended_effect = "answer_question"
        else:
            act = CommunicativeAct.ACKNOWLEDGE
            intended_effect = "acknowledge_user_statement"

        cand = CommunicativeCandidate(
            id="b0_cand",
            origin=CandidateOrigin.USER_DRIVEN,
            grounds=(),  # B0 does not have explicit inspectable GroundedReasons
            target="user",
            act=act,
            intended_effect=intended_effect,
            validity=True,
            persistence=0,
            inhibition=0.0,
            confidence=1.0,
            urgency=1.0,
        )

        dt_ms = (time.perf_counter() - t0) * 1000.0
        decision = AuthorizationDecision(
            action=ActionDecision.ALLOW,
            winner_candidate=cand,
            reason=f"B0_CAPS_SURFACE_MATCH: {act.value}",
            trace=f"[B0] User input '{text}' classified as {act.value}. Internal state ignored.",
        )
        return decision, [cand], {"latency_ms": dt_ms, "candidate_count": 1}


class B1_CandidateAuthorization(BaseBaseline):
    """
    B1 — Typed Candidate + Authorization (Research Proposal).
    Explicit causal pipeline:
    internal/user state -> candidate generators -> grounding verifier -> typed candidate -> authorization arbiter -> action.
    """
    name: str = "B1_CandidateAuthorization"

    def __init__(self) -> None:
        self.user_gen = UserCandidateGenerator()
        self.verifier = GroundingVerifier()
        self.endo_gen = EndogenousCandidateGenerator(grounding_verifier=self.verifier)
        self.arbiter = AuthorizationArbiter()

    def process_turn(
        self,
        context: CognitiveContext,
        env: DialogueEnvironment,
        candidate_pool: Optional[List[CommunicativeCandidate]] = None,
    ) -> Tuple[AuthorizationDecision, List[CommunicativeCandidate], Dict[str, Any]]:
        t0 = time.perf_counter()

        # 1. User candidates
        user_cands = self.user_gen.generate(env)

        # 2. Endogenous candidates
        endo_cands = self.endo_gen.generate(context, env, existing_pool=candidate_pool)

        # 3. Grounding check on all candidates
        verified_endo: List[CommunicativeCandidate] = []
        for cand in endo_cands:
            valid, reason = self.verifier.verify_candidate_grounding(cand, context)
            cand.validity = valid
            if valid:
                verified_endo.append(cand)

        # 4. Authorization / Arbitration
        decision = self.arbiter.arbitrate(user_cands, verified_endo, env)

        dt_ms = (time.perf_counter() - t0) * 1000.0
        total_cands = user_cands + verified_endo
        return decision, total_cands, {"latency_ms": dt_ms, "candidate_count": len(total_cands)}


class B2_CandidateConsequence(BaseBaseline):
    """
    B2 — Candidate + Consequence Evaluator (Comparator).
    B1 augmented with forward expected-consequence valuation.
    """
    name: str = "B2_CandidateConsequence"

    def __init__(self) -> None:
        self.user_gen = UserCandidateGenerator()
        self.verifier = GroundingVerifier()
        self.endo_gen = EndogenousCandidateGenerator(grounding_verifier=self.verifier)
        self.arbiter = AuthorizationArbiter()
        self.evaluator = ConsequenceEvaluator()

    def process_turn(
        self,
        context: CognitiveContext,
        env: DialogueEnvironment,
        candidate_pool: Optional[List[CommunicativeCandidate]] = None,
    ) -> Tuple[AuthorizationDecision, List[CommunicativeCandidate], Dict[str, Any]]:
        t0 = time.perf_counter()

        user_cands = self.user_gen.generate(env)
        endo_cands = self.endo_gen.generate(context, env, existing_pool=candidate_pool)

        # Grounding check
        verified_endo: List[CommunicativeCandidate] = []
        for cand in endo_cands:
            valid, _ = self.verifier.verify_candidate_grounding(cand, context)
            cand.validity = valid
            if valid:
                # Consequence modulation (B2 feature)
                modulated_cand = self.evaluator.apply_consequence_modulation(cand, context, env)
                verified_endo.append(modulated_cand)

        decision = self.arbiter.arbitrate(user_cands, verified_endo, env)

        dt_ms = (time.perf_counter() - t0) * 1000.0
        total_cands = user_cands + verified_endo
        return decision, total_cands, {"latency_ms": dt_ms, "candidate_count": len(total_cands)}


class B1_Ablation_NoGrounding(BaseBaseline):
    """
    Ablation 1: B1 without Grounding.
    Allows raw emotional intensity (e.g. high tension or arousal) to directly create candidates
    without checking for inspectable grounded events.
    """
    name: str = "B1_NoGrounding"

    def __init__(self) -> None:
        self.user_gen = UserCandidateGenerator()
        self.arbiter = AuthorizationArbiter()

    def process_turn(
        self,
        context: CognitiveContext,
        env: DialogueEnvironment,
        candidate_pool: Optional[List[CommunicativeCandidate]] = None,
    ) -> Tuple[AuthorizationDecision, List[CommunicativeCandidate], Dict[str, Any]]:
        t0 = time.perf_counter()
        user_cands = self.user_gen.generate(env)
        endo_cands: List[CommunicativeCandidate] = []

        # If high affect/tension exists, invent candidate from raw state alone
        tension = context.somatic.get("tension", 0.0)
        arousal = context.pad.get("a", 0.0)
        cognitive_load = context.somatic.get("cognitive_load", 0.0)

        if tension > 0.4 or arousal > 0.4 or cognitive_load > 0.4:
            # Ungrounded candidate
            fake_cand = CommunicativeCandidate(
                id="ungrounded_state_cand",
                origin=CandidateOrigin.ENDOGENOUS,
                grounds=(),  # ZERO GROUNDS
                target="user",
                act=CommunicativeAct.SHARE,
                intended_effect="express_floating_tension",
                validity=True,
                persistence=0,
                inhibition=0.0,
                confidence=1.0,
                urgency=max(tension, arousal),
            )
            endo_cands.append(fake_cand)

        decision = self.arbiter.arbitrate(user_cands, endo_cands, env)
        dt_ms = (time.perf_counter() - t0) * 1000.0
        total_cands = user_cands + endo_cands
        return decision, total_cands, {"latency_ms": dt_ms, "candidate_count": len(total_cands)}


class B1_Ablation_NoAuthorization(BaseBaseline):
    """
    Ablation 2: B1 without Authorization.
    Whenever an endogenous candidate forms, it immediately claims the turn (ALLOW),
    ignoring floor state, interruption permissions, and recent attempted purposes.
    """
    name: str = "B1_NoAuthorization"

    def __init__(self) -> None:
        self.user_gen = UserCandidateGenerator()
        self.verifier = GroundingVerifier()
        self.endo_gen = EndogenousCandidateGenerator(grounding_verifier=self.verifier)

    def process_turn(
        self,
        context: CognitiveContext,
        env: DialogueEnvironment,
        candidate_pool: Optional[List[CommunicativeCandidate]] = None,
    ) -> Tuple[AuthorizationDecision, List[CommunicativeCandidate], Dict[str, Any]]:
        t0 = time.perf_counter()
        user_cands = self.user_gen.generate(env)
        endo_cands = self.endo_gen.generate(context, env, existing_pool=candidate_pool)

        verified_endo = [c for c in endo_cands if self.verifier.verify_candidate_grounding(c, context)[0]]

        # No arbitration: endogenous candidates blindly take priority if present, otherwise user
        if verified_endo:
            winner = verified_endo[0]
            decision = AuthorizationDecision(
                action=ActionDecision.ALLOW,
                winner_candidate=winner,
                reason="NO_AUTH_OVERRIDE: Candidate forced onto floor without authorization.",
                trace="[NO_AUTH] Floor checks and interruption rules bypassed.",
            )
        elif user_cands:
            decision = AuthorizationDecision(
                action=ActionDecision.ALLOW,
                winner_candidate=user_cands[0],
                reason="USER_CANDIDATE_NO_AUTH",
                trace="[NO_AUTH] User candidate accepted.",
            )
        else:
            decision = AuthorizationDecision(
                action=ActionDecision.SILENCE,
                reason="NO_CANDIDATES",
                trace="[NO_AUTH] No candidates.",
            )

        dt_ms = (time.perf_counter() - t0) * 1000.0
        total_cands = user_cands + verified_endo
        return decision, total_cands, {"latency_ms": dt_ms, "candidate_count": len(total_cands)}


class B1_Ablation_NoPersistence(BaseBaseline):
    """
    Ablation 3: B1 without Persistence.
    Candidates do not survive across turns; candidate pool is wiped every turn.
    """
    name: str = "B1_NoPersistence"

    def __init__(self) -> None:
        self.user_gen = UserCandidateGenerator()
        self.verifier = GroundingVerifier()
        self.endo_gen = EndogenousCandidateGenerator(grounding_verifier=self.verifier)
        self.arbiter = AuthorizationArbiter()

    def process_turn(
        self,
        context: CognitiveContext,
        env: DialogueEnvironment,
        candidate_pool: Optional[List[CommunicativeCandidate]] = None,
    ) -> Tuple[AuthorizationDecision, List[CommunicativeCandidate], Dict[str, Any]]:
        t0 = time.perf_counter()
        user_cands = self.user_gen.generate(env)
        # Pass existing_pool=None always to disable persistence
        endo_cands = self.endo_gen.generate(context, env, existing_pool=None)

        verified_endo = [c for c in endo_cands if self.verifier.verify_candidate_grounding(c, context)[0]]
        decision = self.arbiter.arbitrate(user_cands, verified_endo, env)

        dt_ms = (time.perf_counter() - t0) * 1000.0
        total_cands = user_cands + verified_endo
        return decision, total_cands, {"latency_ms": dt_ms, "candidate_count": len(total_cands)}


class B1_Ablation_NoInhibition(BaseBaseline):
    """
    Ablation 4: B1 without Inhibition.
    Candidates never suffer inhibition from recent attempted purposes or environmental suppression.
    """
    name: str = "B1_NoInhibition"

    def __init__(self) -> None:
        self.user_gen = UserCandidateGenerator()
        self.verifier = GroundingVerifier()
        self.endo_gen = EndogenousCandidateGenerator(grounding_verifier=self.verifier)
        self.arbiter = AuthorizationArbiter()

    def process_turn(
        self,
        context: CognitiveContext,
        env: DialogueEnvironment,
        candidate_pool: Optional[List[CommunicativeCandidate]] = None,
    ) -> Tuple[AuthorizationDecision, List[CommunicativeCandidate], Dict[str, Any]]:
        t0 = time.perf_counter()
        # Create env copy without recent attempted purposes
        uninhibited_env = DialogueEnvironment(
            user_input=env.user_input,
            floor_status=env.floor_status,
            user_interruption_allowed=env.user_interruption_allowed,
            privacy_level=env.privacy_level,
            turns_since_user_speech=env.turns_since_user_speech,
            recent_attempted_purposes=set(),  # NO INHIBITION
        )

        user_cands = self.user_gen.generate(uninhibited_env)
        endo_cands = self.endo_gen.generate(context, uninhibited_env, existing_pool=candidate_pool)

        # Force inhibition to 0
        for c in endo_cands:
            c.inhibition = 0.0

        verified_endo = [c for c in endo_cands if self.verifier.verify_candidate_grounding(c, context)[0]]
        decision = self.arbiter.arbitrate(user_cands, verified_endo, uninhibited_env)

        dt_ms = (time.perf_counter() - t0) * 1000.0
        total_cands = user_cands + verified_endo
        return decision, total_cands, {"latency_ms": dt_ms, "candidate_count": len(total_cands)}
