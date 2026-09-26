"""
src/core/cognition/contract/projection.py

Phase 23-G: Semantic Substrate -> Cognitive Core Projection Layer.

Strict Invariants:
1. Strips all string representations; maps concepts, roles, scopes, and entities
   to compact numeric integer IDs via SymbolTable.
2. Complete epistemic fidelity: FACT, INFERRED, AMBIGUOUS, UNKNOWN preserved.
3. Preserves all derivation provenance (rule_id, supporting premises).
4. AMBIGUOUS alternative hypotheses preserved as numeric alternative_concept_ids.
5. Deterministic projection across parallel cross-lingual substrate graphs.
"""

from __future__ import annotations

import logging
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional, Set, Tuple

from src.core.cognition.contract.arena import ArenaCapacityExceededError, TermArena
from src.core.cognition.contract.epistemic import EpistemicStatus
from src.core.cognition.contract.provenance import ProvenanceRecord
from src.core.cognition.contract.terms import (
    EntityTerm,
    LogicalTerm,
    SCOPE_TYPE_INTENSIONAL,
    SCOPE_TYPE_MODAL,
    SCOPE_TYPE_NEGATION,
    SCOPE_TYPE_ROOT,
    ScopeTerm,
)
from src.core.knowledge.fortification import (
    EpistemicState,
    ScopeBoundary,
    ScopeType,
    SemanticEdge,
    SemanticGraph,
    SemanticNode,
)

logger = logging.getLogger(__name__)


class SymbolTable:
    """
    Bidirectional symbol table mapping string symbols in the Semantic Substrate
    to compact integer identifiers for the Cognitive Core.
    """

    def __init__(self) -> None:
        self._concept_to_id: Dict[str, int] = {}
        self._id_to_concept: Dict[int, str] = {}
        self._next_concept_id: int = 100

        self._role_to_id: Dict[str, int] = {}
        self._id_to_role: Dict[int, str] = {}
        self._next_role_id: int = 1

        self._node_to_id: Dict[str, int] = {}
        self._id_to_node: Dict[int, str] = {}
        self._next_node_id: int = 1

        self._scope_to_id: Dict[str, int] = {"scope:root": 1}
        self._id_to_scope: Dict[int, str] = {1: "scope:root"}
        self._next_scope_id: int = 2

        self._rule_to_id: Dict[str, int] = {}
        self._id_to_rule: Dict[int, str] = {}
        self._next_rule_id: int = 1

        # Term ID tracking: term_id -> node_id string
        self._term_id_to_symbol: Dict[int, str] = {}
        self._symbol_to_term_id: Dict[str, int] = {}

    def intern_concept(self, symbol: str) -> int:
        sym = symbol.strip()
        if sym not in self._concept_to_id:
            cid = self._next_concept_id
            self._next_concept_id += 1
            self._concept_to_id[sym] = cid
            self._id_to_concept[cid] = sym
            return cid
        return self._concept_to_id[sym]

    def get_concept_symbol(self, cid: int) -> Optional[str]:
        return self._id_to_concept.get(cid)

    def intern_role(self, role: str) -> int:
        r = role.strip()
        if r not in self._role_to_id:
            rid = self._next_role_id
            self._next_role_id += 1
            self._role_to_id[r] = rid
            self._id_to_role[rid] = r
            return rid
        return self._role_to_id[r]

    def get_role_symbol(self, rid: int) -> Optional[str]:
        return self._id_to_role.get(rid)

    def intern_node(self, node_id: str) -> int:
        nid = node_id.strip()
        if nid not in self._node_to_id:
            uid = self._next_node_id
            self._next_node_id += 1
            self._node_to_id[nid] = uid
            self._id_to_node[uid] = nid
            return uid
        return self._node_to_id[nid]

    def get_node_symbol(self, uid: int) -> Optional[str]:
        return self._id_to_node.get(uid)

    def intern_scope(self, scope_id: str) -> int:
        sid = scope_id.strip()
        if sid not in self._scope_to_id:
            sc_id = self._next_scope_id
            self._next_scope_id += 1
            self._scope_to_id[sid] = sc_id
            self._id_to_scope[sc_id] = sid
            return sc_id
        return self._scope_to_id[sid]

    def get_scope_symbol(self, sc_id: int) -> Optional[str]:
        return self._id_to_scope.get(sc_id)

    def intern_rule(self, rule_id: str) -> int:
        r = rule_id.strip()
        if r not in self._rule_to_id:
            ru_id = self._next_rule_id
            self._next_rule_id += 1
            self._rule_to_id[r] = ru_id
            self._id_to_rule[ru_id] = r
            return ru_id
        return self._rule_to_id[r]

    def get_rule_symbol(self, ru_id: int) -> Optional[str]:
        return self._id_to_rule.get(ru_id)

    def register_term_id(self, term_id: int, node_symbol: str) -> None:
        self._term_id_to_symbol[term_id] = node_symbol
        self._symbol_to_term_id[node_symbol] = term_id

    def get_term_symbol(self, term_id: int) -> Optional[str]:
        return self._term_id_to_symbol.get(term_id)

    def get_term_id_for_symbol(self, node_symbol: str) -> Optional[int]:
        return self._symbol_to_term_id.get(node_symbol)


@dataclass(frozen=True)
class ProjectionResult:
    """Consolidated outcome of projecting a SemanticGraph to Cognitive Core terms."""
    success: bool
    term_count: int
    entity_count: int
    scope_count: int
    arena: TermArena
    symbol_table: SymbolTable
    error: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        return {
            "success": self.success,
            "term_count": self.term_count,
            "entity_count": self.entity_count,
            "scope_count": self.scope_count,
            "error": self.error,
        }


def _map_scope_type(st: ScopeType) -> int:
    if st == ScopeType.ROOT:
        return SCOPE_TYPE_ROOT
    elif st == ScopeType.NEGATION:
        return SCOPE_TYPE_NEGATION
    elif st == ScopeType.MODAL:
        return SCOPE_TYPE_MODAL
    elif st == ScopeType.INTENSIONAL:
        return SCOPE_TYPE_INTENSIONAL
    return SCOPE_TYPE_ROOT


def ProjectGraphToTerms(
    graph: SemanticGraph,
    arena: TermArena,
    symbol_table: Optional[SymbolTable] = None,
) -> ProjectionResult:
    """
    Project a P23-F SemanticGraph substrate into the preallocated TermArena.
    
    1. Scopes are registered as ScopeTerms.
    2. Entities (arguments/referents) are registered as EntityTerms.
    3. Events/predicates and relations are registered as LogicalTerms.
    4. Epistemic states (FACT, INFERRED, AMBIGUOUS, UNKNOWN) are preserved strictly.
    5. Derivation provenance (rule ID, supporting premises) is converted to numeric IDs.
    """
    if symbol_table is None:
        symbol_table = SymbolTable()

    try:
        # 1. Project Scopes
        scope_map: Dict[str, int] = {}
        for s_id, s_boundary in sorted(graph.scopes.items()):
            num_scope_id = symbol_table.intern_scope(s_id)
            scope_map[s_id] = num_scope_id
            parent_num = symbol_table.intern_scope(s_boundary.parent_scope_id) if s_boundary.parent_scope_id else 0
            if s_id != "scope:root":
                arena.allocate_scope(
                    scope_type_id=_map_scope_type(s_boundary.scope_type),
                    parent_scope_id=parent_num,
                )

        # Classify nodes: Event/Relation nodes vs Entity nodes
        # Nodes with outgoing edges or concept symbols starting with c:SOLVE, c:ASSIST, c:LIKE, c:VISIT
        outgoing_edges: Dict[str, List[SemanticEdge]] = {}
        incoming_edges: Dict[str, List[SemanticEdge]] = {}
        for edge in graph.edges:
            outgoing_edges.setdefault(edge.source_id, []).append(edge)
            incoming_edges.setdefault(edge.target_id, []).append(edge)

        entity_node_ids: Set[str] = set()
        event_node_ids: Set[str] = set()

        for n_id, node in graph.nodes.items():
            if n_id.startswith("ent:") or (n_id not in outgoing_edges and n_id in incoming_edges):
                entity_node_ids.add(n_id)
            else:
                event_node_ids.add(n_id)

        # If a graph has only nodes without edges, treat all as entities unless concept implies predicate
        if not graph.edges and not event_node_ids:
            entity_node_ids = set(graph.nodes.keys())

        # 2. Project Entities
        node_to_entity_id: Dict[str, int] = {}
        for n_id in sorted(entity_node_ids):
            node = graph.nodes[n_id]
            cid = symbol_table.intern_concept(node.concept_symbol)
            sc_id = scope_map.get(node.scope_id, 1)
            ep_status = EpistemicStatus.from_epistemic_state(node.epistemic_state)

            alt_cids: Tuple[int, ...] = ()
            if node.epistemic_state == EpistemicState.AMBIGUOUS:
                alt_hyps = node.attributes.get("alternative_hypotheses", [])
                alt_cids = tuple(symbol_table.intern_concept(h) for h in alt_hyps)

            ent_id = arena.allocate_entity(
                concept_id=cid,
                scope_id=sc_id,
                epistemic_status=ep_status,
                alternative_concept_ids=alt_cids,
                is_disambiguated=node.is_disambiguated,
            )
            node_to_entity_id[n_id] = ent_id
            symbol_table.intern_node(n_id)

        # 3. Project LogicalTerms (Events / Relational Assertions)
        # Sort event nodes deterministically
        for n_id in sorted(event_node_ids):
            node = graph.nodes[n_id]
            pred_cid = symbol_table.intern_concept(node.concept_symbol)
            sc_id = scope_map.get(node.scope_id, 1)
            ep_status = EpistemicStatus.from_epistemic_state(node.epistemic_state)

            # Extract roles and arguments
            edges = outgoing_edges.get(n_id, [])
            arg0_id = 0
            role0_id = 0
            arg1_id = 0
            role1_id = 0
            arg2_id = 0
            role2_id = 0

            # Sort edges for deterministic slot assignment (:ARG0, :ARG1, :ARG2, :cause, etc.)
            sorted_edges = sorted(edges, key=lambda e: e.relation_role)
            for idx, edge in enumerate(sorted_edges[:3]):
                rid = symbol_table.intern_role(edge.relation_role)
                target_ent = node_to_entity_id.get(edge.target_id, 0)
                if target_ent == 0:
                    # Target might be another event node or interned node
                    target_ent = symbol_table.intern_node(edge.target_id)

                if idx == 0:
                    arg0_id = target_ent
                    role0_id = rid
                elif idx == 1:
                    arg1_id = target_ent
                    role1_id = rid
                elif idx == 2:
                    arg2_id = target_ent
                    role2_id = rid

            # Ambiguity handling on event node
            alt_cids = ()
            if node.epistemic_state == EpistemicState.AMBIGUOUS:
                alt_hyps = node.attributes.get("alternative_hypotheses", [])
                alt_cids = tuple(symbol_table.intern_concept(h) for h in alt_hyps)

            # Provenance mapping
            num_prov: Optional[ProvenanceRecord] = None
            rule_id = 0
            premise_ids: Tuple[int, ...] = ()
            if node.provenance:
                num_prov = ProvenanceRecord.from_p23e_provenance(node.provenance, symbol_table)
                rule_id = num_prov.rule_id
                premise_ids = num_prov.supporting_premise_ids

            term_id = arena.allocate_term(
                predicate_id=pred_cid,
                arg0_id=arg0_id,
                arg1_id=arg1_id,
                arg2_id=arg2_id,
                role0_id=role0_id,
                role1_id=role1_id,
                role2_id=role2_id,
                scope_id=sc_id,
                epistemic_status=ep_status,
                polarity=node.polarity,
                rule_id=rule_id,
                premise_ids=premise_ids,
                provenance=num_prov,
                is_disambiguated=node.is_disambiguated,
                alternative_concept_ids=alt_cids,
            )
            symbol_table.register_term_id(term_id, n_id)

        return ProjectionResult(
            success=True,
            term_count=arena.term_count,
            entity_count=arena.entity_count,
            scope_count=arena.scope_count,
            arena=arena,
            symbol_table=symbol_table,
        )

    except ArenaCapacityExceededError as e:
        return ProjectionResult(
            success=False,
            term_count=arena.term_count,
            entity_count=arena.entity_count,
            scope_count=arena.scope_count,
            arena=arena,
            symbol_table=symbol_table,
            error=str(e),
        )
    except Exception as e:
        logger.exception("Projection error: %s", e)
        return ProjectionResult(
            success=False,
            term_count=arena.term_count,
            entity_count=arena.entity_count,
            scope_count=arena.scope_count,
            arena=arena,
            symbol_table=symbol_table,
            error=str(e),
        )
