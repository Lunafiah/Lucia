"""
tests/evaluation/phase23_caps/run_caps_readiness_benchmark.py

Isolated Research Benchmark for Phase 23 CAPS Implementation Readiness Gates:
- R1: InformationSubgoal -> Inquire Compiler
- R2: Internal Goal + Admissible Evidence -> Grounded Outgoing SemanticGraph
- R3: Turn-Level Discourse Entity Retention Contract
- R4: User Assertion Conflict & Provenance Policy
- Determinism: Canonical Serialization Equality on Frozen Input
"""

import copy
import hashlib
import json
import sys
import time
from dataclasses import asdict, dataclass, field
from pathlib import Path
from typing import Any, Dict, List, Optional, Set, Tuple

PROJECT_ROOT = Path("c:/Users/Lunafiah/Desktop/My_project/Lucia")
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from src.core.cognition.contract.arena import TermArena
from src.core.cognition.contract.epistemic import EpistemicStatus, KleeneValue
from src.core.cognition.contract.inference import DisambiguationSubgoal
from src.core.cognition.contract.projection import SymbolTable
from src.core.cognition.contract.terms import EntityTerm, LogicalTerm
from src.core.cognition.kernel.binding import BindingFrame, VAR_0, is_variable
from src.core.cognition.kernel.conflict import ConflictRecord, detect_direct_conflict
from src.core.cognition.kernel.engine import (
    Goal,
    GoalResult,
    INFO_REASON_AMBIGUOUS_REFERENT,
    INFO_REASON_MISSING_PREMISE,
    INFO_REASON_UNGROUNDED_VARIABLE,
    InformationSubgoal,
    ReasoningKernel,
)
from src.core.cognition.kernel.rules import InferenceRule, RuleHead, RuleIndex, RulePremise
from src.core.knowledge.fortification import (
    EpistemicState,
    ProvenanceRecord,
    ScopeBoundary,
    ScopeType,
    SemanticEdge,
    SemanticGraph,
    SemanticNode,
)
from src.core.knowledge.proposition import Proposition, ProvenanceType
from src.core.knowledge.store import KnowledgeStore


# ── R1: InformationSubgoal -> Inquire Compiler Prototype ──────────────────────────

class CommunicativeAct:
    ASSERT = "ASSERT"
    ANSWER = "ANSWER"
    INQUIRE = "INQUIRE"
    CLARIFY = "CLARIFY"
    ACKNOWLEDGE = "ACKNOWLEDGE"
    GREET = "GREET"
    FAREWELL = "FAREWELL"
    REFUSE = "REFUSE"


@dataclass
class CompiledInquireResult:
    act: str
    graph: Optional[SemanticGraph]
    target_predicate_symbol: str
    focus_arg_symbol: str
    epistemic_state: str
    success: bool
    requires_clarification: bool = False
    error: Optional[str] = None


def compile_subgoal_to_inquire(
    subgoal: InformationSubgoal,
    symbol_table: SymbolTable,
    session_id: str = "session:inquire_test",
) -> CompiledInquireResult:
    """
    Deterministic compiler transforming an InformationSubgoal into an INQUIRE SemanticGraph.
    """
    if subgoal.reason_code == INFO_REASON_AMBIGUOUS_REFERENT:
        # Ambiguous referent requires CLARIFY rather than pure INQUIRE
        return CompiledInquireResult(
            act=CommunicativeAct.CLARIFY,
            graph=None,
            target_predicate_symbol="",
            focus_arg_symbol="",
            epistemic_state=EpistemicState.AMBIGUOUS.value,
            success=True,
            requires_clarification=True,
        )

    pred_sym = symbol_table.get_concept_symbol(subgoal.target_predicate_id)
    if not pred_sym:
        pred_sym = f"c:PRED_{subgoal.target_predicate_id}"

    graph = SemanticGraph(session_id=session_id)

    # Predicate / event node representing the questioned relation
    event_id = f"node:inquire_{subgoal.target_predicate_id}"
    event_node = SemanticNode(
        id=event_id,
        epistemic_state=EpistemicState.UNKNOWN,
        concept_symbol=pred_sym,
        polarity=subgoal.polarity,
    )
    graph.add_node(event_node)

    # Arg0 resolution
    focus_sym = ""
    if subgoal.arg0_id > 0 and not is_variable(subgoal.arg0_id):
        arg0_sym = symbol_table.get_node_symbol(subgoal.arg0_id) or f"ent:entity_{subgoal.arg0_id}"
        arg0_node = SemanticNode(
            id=arg0_sym,
            epistemic_state=EpistemicState.FACT,
            concept_symbol=arg0_sym,
        )
        graph.add_node(arg0_node)
        graph.add_edge(SemanticEdge(source_id=event_id, target_id=arg0_sym, relation_role=":ARG0"))
        focus_sym = arg0_sym
    else:
        # Ungrounded arg0 is the question focus
        wh_node_id = "ent:wh_target_arg0"
        wh_node = SemanticNode(
            id=wh_node_id,
            epistemic_state=EpistemicState.UNKNOWN,
            concept_symbol="c:UNKNOWN_REFERENT",
        )
        graph.add_node(wh_node)
        graph.add_edge(SemanticEdge(source_id=event_id, target_id=wh_node_id, relation_role=":ARG0"))
        focus_sym = wh_node_id

    # Arg1 resolution if present
    if subgoal.arg1_id > 0:
        if not is_variable(subgoal.arg1_id):
            arg1_sym = symbol_table.get_node_symbol(subgoal.arg1_id) or f"ent:entity_{subgoal.arg1_id}"
            arg1_node = SemanticNode(
                id=arg1_sym,
                epistemic_state=EpistemicState.FACT,
                concept_symbol=arg1_sym,
            )
            graph.add_node(arg1_node)
            graph.add_edge(SemanticEdge(source_id=event_id, target_id=arg1_sym, relation_role=":ARG1"))
        else:
            wh_node_id = "ent:wh_target_arg1"
            wh_node = SemanticNode(
                id=wh_node_id,
                epistemic_state=EpistemicState.UNKNOWN,
                concept_symbol="c:UNKNOWN_REFERENT",
            )
            graph.add_node(wh_node)
            graph.add_edge(SemanticEdge(source_id=event_id, target_id=wh_node_id, relation_role=":ARG1"))

    return CompiledInquireResult(
        act=CommunicativeAct.INQUIRE,
        graph=graph,
        target_predicate_symbol=pred_sym,
        focus_arg_symbol=focus_sym,
        epistemic_state=EpistemicState.UNKNOWN.value,
        success=True,
    )


# ── R2: Internal Goal + Admissible Evidence -> Grounded SemanticGraph Prototype ───

@dataclass
class GroundedPropositionResult:
    act: str
    graph: Optional[SemanticGraph]
    epistemic_state: str
    grounded: bool
    refused_assertion: bool = False
    evidence_provenance: Optional[Dict[str, Any]] = None
    error: Optional[str] = None


def synthesize_grounded_proposition(
    goal: Goal,
    knowledge_store: KnowledgeStore,
    symbol_table: SymbolTable,
    session_id: str = "session:prop_test",
) -> GroundedPropositionResult:
    """
    Transforms an internal goal + admissible evidence into an outgoing Grounded SemanticGraph.
    Enforces the Grounding Invariant:
    CAPS SHALL NOT emit an ASSERT or ANSWER proposition as an asserted claim unless the proposition has admissible grounding.
    """
    pred_sym = symbol_table.get_concept_symbol(goal.predicate_id) or f"c:PRED_{goal.predicate_id}"
    arg0_sym = symbol_table.get_node_symbol(goal.arg0_id) or f"ent:entity_{goal.arg0_id}"

    # Search for matching proposition in KnowledgeStore
    matching_props = knowledge_store.query(subject=arg0_sym, predicate=pred_sym, valid_only=True)

    if not matching_props:
        # Invariant enforced: No admissible grounding -> CANNOT emit ASSERT or ANSWER
        return GroundedPropositionResult(
            act=CommunicativeAct.INQUIRE,
            graph=None,
            epistemic_state=EpistemicState.UNKNOWN.value,
            grounded=False,
            refused_assertion=True,
            error="Grounding Invariant Enforced: No admissible knowledge evidence found for goal.",
        )

    best_prop = matching_props[0]

    # Build SemanticGraph from admissible evidence
    graph = SemanticGraph(session_id=session_id)
    event_id = f"node:assert_{goal.predicate_id}"

    prov = ProvenanceRecord(
        derivation_rule_id=None,
        supporting_premises=(best_prop.id,),
        originating_session_id=session_id,
        metadata={"provenance_type": best_prop.provenance.value, "confidence": best_prop.confidence},
    )

    event_node = SemanticNode(
        id=event_id,
        epistemic_state=EpistemicState.FACT,
        concept_symbol=pred_sym,
        polarity=goal.polarity,
        provenance=prov,
    )
    graph.add_node(event_node)

    # Arg0
    arg0_node = SemanticNode(id=arg0_sym, epistemic_state=EpistemicState.FACT, concept_symbol=arg0_sym)
    graph.add_node(arg0_node)
    graph.add_edge(SemanticEdge(source_id=event_id, target_id=arg0_sym, relation_role=":ARG0"))

    # Arg1 from stored object
    arg1_sym = best_prop.object
    arg1_node = SemanticNode(id=arg1_sym, epistemic_state=EpistemicState.FACT, concept_symbol=arg1_sym)
    graph.add_node(arg1_node)
    graph.add_edge(SemanticEdge(source_id=event_id, target_id=arg1_sym, relation_role=":ARG1"))

    return GroundedPropositionResult(
        act=CommunicativeAct.ANSWER,
        graph=graph,
        epistemic_state=EpistemicState.FACT.value,
        grounded=True,
        refused_assertion=False,
        evidence_provenance=best_prop.to_dict(),
    )


# ── R3: Turn-Level Discourse Entity Retention ─────────────────────────────────────

@dataclass
class DiscourseReferent:
    entity_id: str
    concept_symbol: str
    last_turn_active: int
    salience_score: float  # [0.0, 1.0]


class BoundedDiscourseCache:
    """
    Minimal bounded discourse referent cache for multi-turn anaphora tracking.
    """
    def __init__(self, max_referents: int = 8, decay_per_turn: float = 0.25):
        self._max = max_referents
        self._decay = decay_per_turn
        self._cache: Dict[str, DiscourseReferent] = {}

    def update_turn(self, turn_id: int, entities: List[Tuple[str, str]]) -> None:
        # Decay existing
        for ref in list(self._cache.values()):
            ref.salience_score -= self._decay
            if ref.salience_score <= 0.0:
                del self._cache[ref.entity_id]

        # Add newly active
        for ent_id, concept_sym in entities:
            self._cache[ent_id] = DiscourseReferent(
                entity_id=ent_id,
                concept_symbol=concept_sym,
                last_turn_active=turn_id,
                salience_score=1.0,
            )

        # Evict if capacity exceeded (lowest salience first)
        if len(self._cache) > self._max:
            sorted_items = sorted(self._cache.values(), key=lambda r: r.salience_score)
            excess = len(self._cache) - self._max
            for r in sorted_items[:excess]:
                del self._cache[r.entity_id]

    def get_most_salient(self) -> Optional[DiscourseReferent]:
        if not self._cache:
            return None
        return max(self._cache.values(), key=lambda r: r.salience_score)

    def contains(self, entity_id: str) -> bool:
        return entity_id in self._cache


# ── R4: User Assertion Conflict & Provenance Policy ───────────────────────────────

def evaluate_user_assertion_policy(
    user_claim: Proposition,
    knowledge_store: KnowledgeStore,
) -> Dict[str, Any]:
    """
    Audits the policy: provenance/source != epistemic truth status.
    USER_STATED is an admissible grounding source, but does NOT automatically grant epistemic FACT.
    When user assertion conflicts with existing verified knowledge, detects contradiction.
    """
    # Check provenance
    is_user_provenance = (user_claim.provenance == ProvenanceType.USER_STATED)
    
    # Conflict detection
    conflicts = knowledge_store.detect_contradiction(user_claim)
    
    if conflicts:
        # Invariant: Conflict must NOT silently overwrite
        conflict = conflicts[0]
        return {
            "policy_verdict": "CONFLICT_DETECTED",
            "epistemic_status": EpistemicState.AMBIGUOUS.value,
            "action_required": CommunicativeAct.CLARIFY,
            "existing_fact_preserved": conflict.to_dict(),
            "candidate_user_claim": user_claim.to_dict(),
            "silent_overwrite_prevented": True,
        }
    
    # Non-conflicting user assertion
    # Crucial Invariant: Even if uncontradicted, user claim is stored with USER_STATED provenance,
    # NOT promoted to verified ground truth without corroboration.
    return {
        "policy_verdict": "STORED_AS_USER_ASSERTION",
        "epistemic_status": EpistemicState.INFERRED.value,  # Inferred contextual belief, NOT FACT
        "action_required": CommunicativeAct.ACKNOWLEDGE,
        "provenance_retained": user_claim.provenance.value,
        "automatic_fact_promotion_prevented": True,
    }


# ── Main Test Runner ─────────────────────────────────────────────────────────────

def run_all_readiness_gates() -> Dict[str, Any]:
    results = {}

    # Initialize shared components
    symbol_table = SymbolTable()
    PRED_SOLVE = symbol_table.intern_concept("c:SOLVE_PROBLEM")
    PRED_PREFERS = symbol_table.intern_concept("c:PREFERS")
    PRED_CANINE = symbol_table.intern_concept("c:CANINE")
    ENT_LUCIA = symbol_table.intern_node("ent:lucia")
    ENT_USER = symbol_table.intern_node("ent:user")
    CONCEPT_READING = symbol_table.intern_concept("c:READING")

    # --- Test R1: InformationSubgoal -> Inquire ---
    subgoal = InformationSubgoal(
        target_predicate_id=PRED_CANINE,
        arg0_id=ENT_USER,
        arg1_id=0,
        polarity=True,
        reason_code=INFO_REASON_MISSING_PREMISE,
    )
    r1_res = compile_subgoal_to_inquire(subgoal, symbol_table)
    
    # Ambiguous subgoal test
    ambig_subgoal = InformationSubgoal(
        target_predicate_id=PRED_CANINE,
        arg0_id=ENT_USER,
        arg1_id=0,
        reason_code=INFO_REASON_AMBIGUOUS_REFERENT,
    )
    r1_ambig_res = compile_subgoal_to_inquire(ambig_subgoal, symbol_table)

    r1_pass = (
        r1_res.success
        and r1_res.act == CommunicativeAct.INQUIRE
        and r1_res.graph is not None
        and len(r1_res.graph.nodes) == 2
        and r1_ambig_res.act == CommunicativeAct.CLARIFY
    )
    results["R1"] = {
        "verdict": "PASS" if r1_pass else "FAIL",
        "act_emitted": r1_res.act,
        "nodes_generated": len(r1_res.graph.nodes) if r1_res.graph else 0,
        "edges_generated": len(r1_res.graph.edges) if r1_res.graph else 0,
        "ambiguous_case_act": r1_ambig_res.act,
    }

    # --- Test R2: Internal Goal -> Grounded SemanticGraph ---
    kstore = KnowledgeStore()
    prop_verified = Proposition(
        id="prop_01",
        subject="ent:user",
        predicate="c:PREFERS",
        object="c:READING",
        confidence=1.0,
        provenance=ProvenanceType.VERIFIED,
        valid=True,
    )
    kstore.store_proposition(prop_verified)

    # Grounded query
    goal_grounded = Goal(predicate_id=PRED_PREFERS, arg0_id=ENT_USER)
    r2_grounded = synthesize_grounded_proposition(goal_grounded, kstore, symbol_table)

    # Ungrounded query (must refuse ASSERT)
    PRED_SECRET = symbol_table.intern_concept("c:SECRET")
    goal_ungrounded = Goal(predicate_id=PRED_SECRET, arg0_id=ENT_USER)
    r2_ungrounded = synthesize_grounded_proposition(goal_ungrounded, kstore, symbol_table)

    r2_pass = (
        r2_grounded.grounded
        and r2_grounded.act == CommunicativeAct.ANSWER
        and r2_grounded.graph is not None
        and r2_ungrounded.refused_assertion
        and r2_ungrounded.act == CommunicativeAct.INQUIRE
    )
    results["R2"] = {
        "verdict": "PASS" if r2_pass else "FAIL",
        "grounded_act": r2_grounded.act,
        "grounded_nodes": len(r2_grounded.graph.nodes) if r2_grounded.graph else 0,
        "ungrounded_refused_assertion": r2_ungrounded.refused_assertion,
        "ungrounded_fallback_act": r2_ungrounded.act,
    }

    # --- Test R3: Discourse Entity Retention ---
    cache = BoundedDiscourseCache(max_referents=3, decay_per_turn=0.5)
    cache.update_turn(turn_id=1, entities=[("ent:task_backup", "c:TASK")])
    t1_check = cache.contains("ent:task_backup")
    cache.update_turn(turn_id=2, entities=[("ent:file_notes", "c:FILE")])
    t2_check = cache.contains("ent:task_backup")  # Still active (salience 0.5)
    cache.update_turn(turn_id=3, entities=[("ent:server_01", "c:SERVER")])
    t3_check = not cache.contains("ent:task_backup")  # Decayed to 0.0 -> evicted

    r3_pass = t1_check and t2_check and t3_check
    results["R3"] = {
        "verdict": "PASS" if r3_pass else "FAIL",
        "turn_1_retained": t1_check,
        "turn_2_retained": t2_check,
        "turn_3_decay_eviction": t3_check,
    }

    # --- Test R4: User Assertion Conflict Policy ---
    prop_existing = Proposition(
        id="prop_color_01",
        subject="ent:lucia_eyes",
        predicate="has_color",
        object="blue",
        confidence=1.0,
        provenance=ProvenanceType.VERIFIED,
        valid=True,
    )
    kstore.store_proposition(prop_existing)

    user_claim_conflict = Proposition(
        id="prop_user_01",
        subject="ent:lucia_eyes",
        predicate="has_color",
        object="green",
        confidence=0.8,
        provenance=ProvenanceType.USER_STATED,
        valid=True,
    )
    r4_conflict = evaluate_user_assertion_policy(user_claim_conflict, kstore)

    user_claim_nonconflict = Proposition(
        id="prop_user_02",
        subject="ent:user",
        predicate="likes_food",
        object="ramen",
        confidence=0.9,
        provenance=ProvenanceType.USER_STATED,
        valid=True,
    )
    r4_nonconflict = evaluate_user_assertion_policy(user_claim_nonconflict, kstore)

    r4_pass = (
        r4_conflict["silent_overwrite_prevented"]
        and r4_conflict["action_required"] == CommunicativeAct.CLARIFY
        and r4_nonconflict["automatic_fact_promotion_prevented"]
        and r4_nonconflict["epistemic_status"] != EpistemicState.FACT.value
    )
    results["R4"] = {
        "verdict": "PASS" if r4_pass else "FAIL",
        "conflict_prevented_silent_overwrite": r4_conflict["silent_overwrite_prevented"],
        "conflict_action": r4_conflict["action_required"],
        "nonconflict_fact_promotion_prevented": r4_nonconflict["automatic_fact_promotion_prevented"],
        "nonconflict_epistemic_status": r4_nonconflict["epistemic_status"],
    }

    # --- Determinism Check ---
    # CAPS(input) == CAPS(input) for frozen input
    r2_run1 = synthesize_grounded_proposition(goal_grounded, kstore, symbol_table)
    r2_run2 = synthesize_grounded_proposition(goal_grounded, kstore, symbol_table)
    hash1 = hashlib.sha256(json.dumps(r2_run1.graph.to_dict(), sort_keys=True).encode()).hexdigest()
    hash2 = hashlib.sha256(json.dumps(r2_run2.graph.to_dict(), sort_keys=True).encode()).hexdigest()
    results["Determinism"] = {
        "identical": (hash1 == hash2),
        "hash_1": hash1,
        "hash_2": hash2,
    }

    return results


if __name__ == "__main__":
    t0 = time.perf_counter()
    res = run_all_readiness_gates()
    elapsed_ms = (time.perf_counter() - t0) * 1000
    print(json.dumps(res, indent=2))
    print(f"Elapsed: {elapsed_ms:.2f} ms")
