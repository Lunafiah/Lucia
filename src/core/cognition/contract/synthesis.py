"""
src/core/cognition/contract/synthesis.py

Phase 23-G: Cognitive Core -> Semantic Substrate Intent Graph Synthesis.

Strict Invariants:
1. Reconstructs a clean, language-independent SemanticGraph from flat terms in TermArena.
2. Complete preservation of concept identity, entity identity, scope boundaries,
   epistemic status, and derivation provenance.
3. AMBIGUOUS alternative hypotheses reconstructed into node attributes.
4. Output SemanticGraph is 100% compatible with P23-F Language Adapter realization.
"""

from __future__ import annotations

import logging
from dataclasses import dataclass
from typing import Any, Dict, List, Optional, Set, Tuple

from src.core.cognition.contract.arena import TermArena
from src.core.cognition.contract.epistemic import EpistemicStatus
from src.core.cognition.contract.projection import SymbolTable
from src.core.cognition.contract.terms import (
    SCOPE_TYPE_INTENSIONAL,
    SCOPE_TYPE_MODAL,
    SCOPE_TYPE_NEGATION,
    SCOPE_TYPE_ROOT,
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


@dataclass(frozen=True)
class SynthesisResult:
    """Consolidated outcome of SynthesizeIntentGraph."""
    success: bool
    graph: Optional[SemanticGraph] = None
    node_count: int = 0
    edge_count: int = 0
    error: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        return {
            "success": self.success,
            "node_count": self.node_count,
            "edge_count": self.edge_count,
            "error": self.error,
        }


def _map_scope_type_id(type_id: int) -> ScopeType:
    if type_id == SCOPE_TYPE_NEGATION:
        return ScopeType.NEGATION
    elif type_id == SCOPE_TYPE_MODAL:
        return ScopeType.MODAL
    elif type_id == SCOPE_TYPE_INTENSIONAL:
        return ScopeType.INTENSIONAL
    return ScopeType.ROOT


def SynthesizeIntentGraph(
    arena: TermArena,
    symbol_table: SymbolTable,
    session_id: str = "session:synthesis",
) -> SynthesisResult:
    """
    Synthesize a discrete SemanticGraph (Intent Substrate) from active Cognitive Core terms.
    
    1. Reconstructs ScopeBoundaries.
    2. Reconstructs Entity referent nodes.
    3. Reconstructs Event/predicate nodes and relational SemanticEdges.
    4. Preserves all epistemic states (FACT, INFERRED, AMBIGUOUS, UNKNOWN).
    5. Preserves all derivation provenance links.
    """
    try:
        graph = SemanticGraph(session_id=session_id)

        # 1. Reconstruct Scopes
        for scope_term in arena.all_scopes():
            s_name = symbol_table.get_scope_symbol(scope_term.scope_id) or f"scope:{scope_term.scope_id}"
            parent_name = None
            if scope_term.parent_scope_id > 0:
                parent_name = symbol_table.get_scope_symbol(scope_term.parent_scope_id) or f"scope:{scope_term.parent_scope_id}"
            st = _map_scope_type_id(scope_term.scope_type_id)
            if s_name != "scope:root":
                graph.add_scope(ScopeBoundary(s_name, st, parent_name))

        # 2. Reconstruct Entities
        entity_id_to_nodename: Dict[int, str] = {}
        for entity in arena.active_entities():
            concept_sym = symbol_table.get_concept_symbol(entity.concept_id) or f"c:CONCEPT_{entity.concept_id}"
            node_name = symbol_table.get_node_symbol(entity.entity_id) or f"ent:entity_{entity.entity_id}"
            entity_id_to_nodename[entity.entity_id] = node_name

            scope_name = symbol_table.get_scope_symbol(entity.scope_id) or "scope:root"
            ep_state = entity.epistemic_status.to_epistemic_state()

            node_attrs: Dict[str, Any] = {}
            if entity.epistemic_status == EpistemicStatus.AMBIGUOUS and entity.alternative_concept_ids:
                hyps = [
                    symbol_table.get_concept_symbol(cid) or f"c:CONCEPT_{cid}"
                    for cid in entity.alternative_concept_ids
                ]
                node_attrs["alternative_hypotheses"] = hyps

            node = SemanticNode(
                id=node_name,
                epistemic_state=ep_state,
                concept_symbol=concept_sym,
                scope_id=scope_name,
                is_disambiguated=entity.is_disambiguated,
                attributes=node_attrs,
            )
            graph.add_node(node)

        # 3. Reconstruct Terms (Events / Assertions / Relations)
        for term in arena.active_terms():
            pred_sym = symbol_table.get_concept_symbol(term.predicate_id) or f"c:EVENT_{term.predicate_id}"
            term_node_id = symbol_table.get_term_symbol(term.term_id) or f"node:event_{term.term_id}"
            scope_name = symbol_table.get_scope_symbol(term.scope_id) or "scope:root"
            ep_state = term.epistemic_status.to_epistemic_state()

            # Provenance
            p23e_prov = None
            if term.provenance:
                p23e_prov = term.provenance.to_p23e_provenance(symbol_table)

            node_attrs = {}
            if term.epistemic_status == EpistemicStatus.AMBIGUOUS and term.alternative_concept_ids:
                hyps = [
                    symbol_table.get_concept_symbol(cid) or f"c:CONCEPT_{cid}"
                    for cid in term.alternative_concept_ids
                ]
                node_attrs["alternative_hypotheses"] = hyps

            event_node = SemanticNode(
                id=term_node_id,
                epistemic_state=ep_state,
                concept_symbol=pred_sym,
                scope_id=scope_name,
                polarity=term.polarity,
                is_disambiguated=term.is_disambiguated,
                provenance=p23e_prov,
                attributes=node_attrs,
            )
            graph.add_node(event_node)

            # Reconstruct Edges
            for arg_id, role_id in (
                (term.arg0_id, term.role0_id),
                (term.arg1_id, term.role1_id),
                (term.arg2_id, term.role2_id),
            ):
                if arg_id > 0 and role_id > 0:
                    role_str = symbol_table.get_role_symbol(role_id) or f":ROLE_{role_id}"
                    target_name = (
                        entity_id_to_nodename.get(arg_id)
                        or symbol_table.get_node_symbol(arg_id)
                        or symbol_table.get_term_symbol(arg_id)
                        or f"ent:node_{arg_id}"
                    )
                    # Ensure target exists in graph, else create placeholder
                    if target_name not in graph.nodes:
                        graph.add_node(SemanticNode(
                            id=target_name,
                            epistemic_state=EpistemicState.FACT,
                            concept_symbol="c:REFERENT",
                            scope_id=scope_name,
                        ))

                    src_scope = graph.nodes[term_node_id].scope_id
                    tgt_scope = graph.nodes[target_name].scope_id
                    is_cross = (src_scope != tgt_scope)

                    edge = SemanticEdge(
                        source_id=term_node_id,
                        target_id=target_name,
                        relation_role=role_str,
                        is_cross_scope_link=is_cross,
                    )
                    graph.add_edge(edge)

        return SynthesisResult(
            success=True,
            graph=graph,
            node_count=len(graph.nodes),
            edge_count=len(graph.edges),
        )

    except Exception as e:
        logger.exception("Synthesis error: %s", e)
        return SynthesisResult(
            success=False,
            graph=None,
            node_count=0,
            edge_count=0,
            error=str(e),
        )
