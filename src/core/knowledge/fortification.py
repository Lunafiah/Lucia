"""
src/core/knowledge/fortification.py

Conservative Semantic Fortification Across Session Boundaries (P23-E).

Architectural Contract:
    Surface Language
          ↓
    Language Adapter
          ↓
    Language-independent Semantic Representation
          ↓
    Cognitive Core
          ↓
    Conservative Semantic Fortification
          ↓
    Persistent Semantic Memory

Invariant:
    "Fortification protects meaning that already exists.
     It does not create meaning that does not exist."
    Meaning_out ⊆ Meaning_in

Key Responsibilities:
    1. Canonicalize graph representation and deterministic ordering.
    2. Perform bounded local consistency checks.
    3. Detect explicitly contradictory local structures.
    4. Preserve UNKNOWN without promotion.
    5. Preserve AMBIGUOUS without premature resolution.
    6. Preserve INFERRED provenance and supporting premise links.
    7. Invalidate dependent INFERRED knowledge when supporting premises are retracted.
    8. Enforce scope boundaries (negation, modal, intensional).
    9. Reject novel entity/fact insertion (zero-ingress property).
    10. Reject shortcut/redundancy topology injection.
    11. Freeze validated session snapshot.
    12. Compute and verify structural integrity checksum.
    13. Persist crash-resilient session memory.
"""

from __future__ import annotations

import copy
import hashlib
import json
import logging
import os
import tempfile
import time
from dataclasses import asdict, dataclass, field
from enum import Enum
from pathlib import Path
from typing import Any, Dict, List, Optional, Set, Tuple, Union

logger = logging.getLogger(__name__)


# ── Epistemic States & Scope Types ─────────────────────────────────────────────

class EpistemicState(str, Enum):
    """
    Four-state epistemic classification for all semantic nodes.
    Mandatory safety invariant: Fortification MUST NOT increase epistemic commitment.
    """
    FACT = "FACT"              # Established ground truth or directly observed fact
    INFERRED = "INFERRED"      # Derived knowledge requiring explicit supporting premises & rule ID
    AMBIGUOUS = "AMBIGUOUS"    # Multiple interpretations; must not be resolved by Fortification
    UNKNOWN = "UNKNOWN"        # Explicit ungrounded or missing referent; must never be promoted


class ScopeType(str, Enum):
    """
    Structural scope boundary types.
    Edges must not cross scope boundaries unless explicitly typed as modal containment.
    """
    ROOT = "ROOT"                    # Top-level assertion space
    NEGATION = "NEGATION"            # Negated proposition scope
    MODAL = "MODAL"                  # Modal attitude scope (belief, desire, intention)
    INTENSIONAL = "INTENSIONAL"      # Intensional predicate scope (opaque context)


class AuditStatus(str, Enum):
    """Status codes resulting from bounded local consistency checking."""
    VALID = "VALID"
    CONTRADICTION_DETECTED = "CONTRADICTION_DETECTED"
    EPISTEMIC_VIOLATION = "EPISTEMIC_VIOLATION"
    SCOPE_VIOLATION = "SCOPE_VIOLATION"
    REDUNDANCY_INJECTION = "REDUNDANCY_INJECTION"
    NOVEL_INSERTION_REJECTED = "NOVEL_INSERTION_REJECTED"
    DANGLING_REFERENCE = "DANGLING_REFERENCE"
    INVALID_PROVENANCE = "INVALID_PROVENANCE"
    MALFORMED_STRUCTURE = "MALFORMED_STRUCTURE"


# ── Exceptions ─────────────────────────────────────────────────────────────────

class FortificationError(Exception):
    """Base exception for all semantic fortification errors."""
    pass


class FrozenGraphError(FortificationError):
    """Raised when an edit is attempted on a frozen, validated graph."""
    pass


class EpistemicViolationError(FortificationError):
    """Raised when an illegal epistemic promotion is attempted."""
    pass


class ScopeViolationError(FortificationError):
    """Raised when an edge crosses a scope boundary illegally."""
    pass


class RedundancyInjectionError(FortificationError):
    """Raised when an unauthorized shortcut/redundancy edge is injected."""
    pass


class NovelEntityInsertionError(FortificationError):
    """Raised when a novel entity or fact is injected during fortification."""
    pass


class ChecksumVerificationError(FortificationError):
    """Raised when structural integrity checksum validation fails."""
    pass


# ── Core Data Structures ───────────────────────────────────────────────────────

@dataclass(frozen=True)
class ProvenanceRecord:
    """
    Epistemic derivation provenance.
    Every INFERRED item must retain its rule ID, supporting premises, and session metadata.
    """
    derivation_rule_id: Optional[str] = None
    supporting_premises: Tuple[str, ...] = ()
    originating_session_id: str = ""
    originating_turn_id: str = ""
    timestamp: float = 0.0
    metadata: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "derivation_rule_id": self.derivation_rule_id,
            "supporting_premises": list(self.supporting_premises),
            "originating_session_id": self.originating_session_id,
            "originating_turn_id": self.originating_turn_id,
            "timestamp": self.timestamp,
            "metadata": dict(self.metadata),
        }

    @classmethod
    def from_dict(cls, d: Dict[str, Any]) -> ProvenanceRecord:
        return cls(
            derivation_rule_id=d.get("derivation_rule_id"),
            supporting_premises=tuple(d.get("supporting_premises", [])),
            originating_session_id=d.get("originating_session_id", ""),
            originating_turn_id=d.get("originating_turn_id", ""),
            timestamp=float(d.get("timestamp", 0.0)),
            metadata=d.get("metadata", {}),
        )


@dataclass(frozen=True)
class ScopeBoundary:
    """
    Explicit scope boundary container.
    Guarantees isolation of modal, negative, and intensional partitions.
    """
    scope_id: str
    scope_type: ScopeType
    parent_scope_id: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        return {
            "scope_id": self.scope_id,
            "scope_type": self.scope_type.value,
            "parent_scope_id": self.parent_scope_id,
        }

    @classmethod
    def from_dict(cls, d: Dict[str, Any]) -> ScopeBoundary:
        return cls(
            scope_id=d["scope_id"],
            scope_type=ScopeType(d["scope_type"]),
            parent_scope_id=d.get("parent_scope_id"),
        )


@dataclass
class SemanticNode:
    """
    Language-independent conceptual or referential node.
    Contains zero natural language strings, tokens, or language-specific rules.
    """
    id: str
    epistemic_state: EpistemicState
    concept_symbol: str                  # Non-lexical symbol, e.g. "c:REL_GIVE", "e:ENTITY_01"
    scope_id: str = "scope:root"        # Scope to which this node belongs
    polarity: bool = True               # True = asserted, False = negated
    is_disambiguated: bool = False      # True ONLY if explicit upstream disambiguation occurred
    provenance: Optional[ProvenanceRecord] = None
    operational_active: bool = True     # Active in persistent memory vs invalidated
    invalidated_reason: Optional[str] = None
    attributes: Dict[str, Any] = field(default_factory=dict)

    def clone(self) -> SemanticNode:
        """Fast typed clone avoiding slow copy.deepcopy."""
        return SemanticNode(
            id=self.id,
            epistemic_state=self.epistemic_state,
            concept_symbol=self.concept_symbol,
            scope_id=self.scope_id,
            polarity=self.polarity,
            is_disambiguated=self.is_disambiguated,
            provenance=self.provenance,
            operational_active=self.operational_active,
            invalidated_reason=self.invalidated_reason,
            attributes=dict(self.attributes) if self.attributes else {},
        )

    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "epistemic_state": self.epistemic_state.value,
            "concept_symbol": self.concept_symbol,
            "scope_id": self.scope_id,
            "polarity": self.polarity,
            "is_disambiguated": self.is_disambiguated,
            "provenance": self.provenance.to_dict() if self.provenance else None,
            "operational_active": self.operational_active,
            "invalidated_reason": self.invalidated_reason,
            "attributes": dict(self.attributes),
        }

    @classmethod
    def from_dict(cls, d: Dict[str, Any]) -> SemanticNode:
        prov_raw = d.get("provenance")
        prov = ProvenanceRecord.from_dict(prov_raw) if prov_raw else None
        return cls(
            id=d["id"],
            epistemic_state=EpistemicState(d["epistemic_state"]),
            concept_symbol=d["concept_symbol"],
            scope_id=d.get("scope_id", "scope:root"),
            polarity=d.get("polarity", True),
            is_disambiguated=d.get("is_disambiguated", False),
            provenance=prov,
            operational_active=d.get("operational_active", True),
            invalidated_reason=d.get("invalidated_reason"),
            attributes=d.get("attributes", {}),
        )


@dataclass
class SemanticEdge:
    """
    Language-independent directed semantic relation.
    Must not cross scope boundaries unless designated as cross-scope structural link.
    """
    source_id: str
    target_id: str
    relation_role: str                  # e.g. ":ARG0", ":ARG1", ":mod", ":sub-event"
    is_cross_scope_link: bool = False   # True ONLY for allowed structural containment links
    attributes: Dict[str, Any] = field(default_factory=dict)

    def clone(self) -> SemanticEdge:
        """Fast typed clone avoiding slow copy.deepcopy."""
        return SemanticEdge(
            source_id=self.source_id,
            target_id=self.target_id,
            relation_role=self.relation_role,
            is_cross_scope_link=self.is_cross_scope_link,
            attributes=dict(self.attributes) if self.attributes else {},
        )

    def to_dict(self) -> Dict[str, Any]:
        return {
            "source_id": self.source_id,
            "target_id": self.target_id,
            "relation_role": self.relation_role,
            "is_cross_scope_link": self.is_cross_scope_link,
            "attributes": dict(self.attributes),
        }

    @classmethod
    def from_dict(cls, d: Dict[str, Any]) -> SemanticEdge:
        return cls(
            source_id=d["source_id"],
            target_id=d["target_id"],
            relation_role=d["relation_role"],
            is_cross_scope_link=d.get("is_cross_scope_link", False),
            attributes=d.get("attributes", {}),
        )


# ── Audit Structures ───────────────────────────────────────────────────────────

@dataclass
class AuditViolation:
    """Detailed record of a single consistency check failure."""
    status: AuditStatus
    description: str
    affected_nodes: List[str] = field(default_factory=list)
    affected_edges: List[Tuple[str, str, str]] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "status": self.status.value,
            "description": self.description,
            "affected_nodes": self.affected_nodes,
            "affected_edges": [list(e) for e in self.affected_edges],
        }


@dataclass
class AuditReport:
    """Consolidated outcome of bounded local consistency check."""
    is_valid: bool
    status: AuditStatus
    violations: List[AuditViolation] = field(default_factory=list)
    structural_checksum: Optional[str] = None
    node_count: int = 0
    edge_count: int = 0
    active_fact_count: int = 0
    active_inferred_count: int = 0
    ambiguous_count: int = 0
    unknown_count: int = 0
    invalidated_count: int = 0

    def to_dict(self) -> Dict[str, Any]:
        return {
            "is_valid": self.is_valid,
            "status": self.status.value,
            "violations": [v.to_dict() for v in self.violations],
            "structural_checksum": self.structural_checksum,
            "node_count": self.node_count,
            "edge_count": self.edge_count,
            "active_fact_count": self.active_fact_count,
            "active_inferred_count": self.active_inferred_count,
            "ambiguous_count": self.ambiguous_count,
            "unknown_count": self.unknown_count,
            "invalidated_count": self.invalidated_count,
        }


# ── Semantic Graph Container ───────────────────────────────────────────────────

class SemanticGraph:
    """
    Discrete Language-Independent Semantic Graph.
    Enforces immutability once frozen, deterministic serialization, and checksum verification.
    """

    def __init__(self, session_id: str = "") -> None:
        self.session_id: str = session_id
        self._scopes: Dict[str, ScopeBoundary] = {
            "scope:root": ScopeBoundary("scope:root", ScopeType.ROOT, None)
        }
        self._nodes: Dict[str, SemanticNode] = {}
        self._edges: List[SemanticEdge] = []
        self._frozen: bool = False
        self._structural_checksum: Optional[str] = None
        self._locked_node_ids: Set[str] = set()

    @property
    def is_frozen(self) -> bool:
        return self._frozen

    @property
    def structural_checksum(self) -> Optional[str]:
        return self._structural_checksum

    @property
    def scopes(self) -> Dict[str, ScopeBoundary]:
        return dict(self._scopes)

    @property
    def nodes(self) -> Dict[str, SemanticNode]:
        return dict(self._nodes)

    @property
    def edges(self) -> List[SemanticEdge]:
        return list(self._edges)

    def _assert_mutable(self) -> None:
        if self._frozen:
            raise FrozenGraphError("SemanticGraph is frozen and immutable; mutations are forbidden.")

    def add_scope(self, scope: ScopeBoundary) -> None:
        self._assert_mutable()
        if scope.parent_scope_id and scope.parent_scope_id not in self._scopes:
            raise ScopeViolationError(f"Parent scope '{scope.parent_scope_id}' does not exist.")
        self._scopes[scope.scope_id] = scope

    def add_node(self, node: SemanticNode) -> None:
        self._assert_mutable()
        if node.scope_id not in self._scopes:
            raise ScopeViolationError(f"Scope '{node.scope_id}' not declared for node '{node.id}'.")
        self._nodes[node.id] = node

    def add_edge(self, edge: SemanticEdge) -> None:
        self._assert_mutable()
        if edge.source_id not in self._nodes:
            raise FortificationError(f"Source node '{edge.source_id}' does not exist.")
        if edge.target_id not in self._nodes:
            raise FortificationError(f"Target node '{edge.target_id}' does not exist.")

        # Scope guard check
        src_scope = self._nodes[edge.source_id].scope_id
        tgt_scope = self._nodes[edge.target_id].scope_id
        if src_scope != tgt_scope and not edge.is_cross_scope_link:
            raise ScopeViolationError(
                f"Edge ({edge.source_id} -> {edge.target_id}) crosses scope boundary "
                f"('{src_scope}' -> '{tgt_scope}') without authorization."
            )

        self._edges.append(edge)

    def get_node(self, node_id: str) -> Optional[SemanticNode]:
        return self._nodes.get(node_id)

    def get_edges_for_node(self, node_id: str) -> List[SemanticEdge]:
        return [e for e in self._edges if e.source_id == node_id or e.target_id == node_id]

    def retract_node(self, node_id: str, reason: str = "Explicit retraction") -> bool:
        """
        Retracts a node by marking it operational_active = False and recording reason.
        Does not delete historical provenance.
        """
        self._assert_mutable()
        node = self._nodes.get(node_id)
        if not node:
            return False
        node.operational_active = False
        node.invalidated_reason = reason
        return True

    def freeze(self) -> None:
        """Marks the graph immutable and computes structural integrity checksum."""
        self._frozen = True
        self._locked_node_ids = set(self._nodes.keys())
        self._structural_checksum = self.compute_checksum()

    def clone(self) -> SemanticGraph:
        """Deep clone of graph preserving mutability state."""
        g = SemanticGraph(session_id=self.session_id)
        g._scopes = dict(self._scopes)
        g._nodes = {nid: n.clone() for nid, n in self._nodes.items()}
        g._edges = [e.clone() for e in self._edges]
        g._frozen = self._frozen
        g._structural_checksum = self._structural_checksum
        g._locked_node_ids = set(self._locked_node_ids)
        return g

    def compute_checksum(self) -> str:
        """
        Compute Graph Structural Integrity Checksum.
        Detects unintended structural mutation/corruption.
        Does NOT claim semantic truth, world truth, or absence of upstream hallucination.
        """
        canonical_dict = self._to_canonical_dict(include_checksum=False)
        canonical_bytes = json.dumps(
            canonical_dict,
            sort_keys=True,
            separators=(",", ":"),
            ensure_ascii=False,
        ).encode("utf-8")
        return hashlib.sha256(canonical_bytes).hexdigest()

    def verify_checksum(self) -> bool:
        """Verifies currently stored checksum against newly computed structural checksum."""
        if not self._structural_checksum:
            return False
        computed = self.compute_checksum()
        return computed == self._structural_checksum

    def _to_canonical_dict(self, include_checksum: bool = True) -> Dict[str, Any]:
        """Produces canonical sorted dictionary of graph structure."""
        # Sorted scopes by ID
        sorted_scopes = [
            self._scopes[sid].to_dict()
            for sid in sorted(self._scopes.keys())
        ]
        # Sorted nodes by ID
        sorted_nodes = [
            self._nodes[nid].to_dict()
            for nid in sorted(self._nodes.keys())
        ]
        # Sorted edges by (source_id, relation_role, target_id)
        sorted_edges = sorted(
            [e.to_dict() for e in self._edges],
            key=lambda e: (e["source_id"], e["relation_role"], e["target_id"]),
        )
        d: Dict[str, Any] = {
            "version": "p23e_1.0",
            "session_id": self.session_id,
            "scopes": sorted_scopes,
            "nodes": sorted_nodes,
            "edges": sorted_edges,
        }
        if include_checksum and self._structural_checksum:
            d["structural_checksum"] = self._structural_checksum
        return d

    def to_dict(self) -> Dict[str, Any]:
        return self._to_canonical_dict(include_checksum=True)

    def to_json(self) -> str:
        return json.dumps(self.to_dict(), indent=2, sort_keys=True, ensure_ascii=False)

    @classmethod
    def from_dict(cls, d: Dict[str, Any]) -> SemanticGraph:
        graph = cls(session_id=d.get("session_id", ""))
        graph._scopes.clear()
        for s_dict in d.get("scopes", []):
            scope = ScopeBoundary.from_dict(s_dict)
            graph._scopes[scope.scope_id] = scope
        for n_dict in d.get("nodes", []):
            node = SemanticNode.from_dict(n_dict)
            graph._nodes[node.id] = node
        for e_dict in d.get("edges", []):
            edge = SemanticEdge.from_dict(e_dict)
            graph._edges.append(edge)
        graph._structural_checksum = d.get("structural_checksum")
        if graph._structural_checksum:
            graph._frozen = True
            graph._locked_node_ids = set(graph._nodes.keys())
        return graph

    @classmethod
    def from_json(cls, json_str: str) -> SemanticGraph:
        data = json.loads(json_str)
        return cls.from_dict(data)


# ── Conservative Semantic Fortifier Engine ─────────────────────────────────────

class ConservativeSemanticFortifier:
    """
    Subsystem realizing Conservative Semantic Fortification (P23-E).

    Execution Contract:
        AUDIT → NORMALIZE → VALIDATE → PRESERVE → FREEZE → INTEGRITY-CHECK → PERSIST

    Zero-Ingress Guarantee:
        Fortification-Originated Unsupported Insertion Rate == 0.0.
        Fortification creates zero novel entities or facts.
    """

    ALLOWED_CROSS_SCOPE_ROLES: Set[str] = {
        ":modal-scope",
        ":sub-event",
        ":condition",
        ":negation-target",
        ":intensional-content",
    }

    SINGLE_VALUED_ROLES: Set[str] = {
        ":has-color",
        ":located-in",
        ":capital-of",
        ":equals",
        ":identity",
    }

    def __init__(self) -> None:
        pass

    # ── 1. Bounded Local Consistency Checking ─────────────────────────────────

    def audit_graph(self, graph: SemanticGraph) -> AuditReport:
        """
        Executes bounded local consistency checking.
        Replaces full bidirectional entailment with deterministic, terminating local rules.
        """
        violations: List[AuditViolation] = []

        # 1.1 Dangling Edge Endpoints
        for edge in graph.edges:
            src = graph.get_node(edge.source_id)
            tgt = graph.get_node(edge.target_id)
            if not src:
                violations.append(AuditViolation(
                    status=AuditStatus.DANGLING_REFERENCE,
                    description=f"Edge references non-existent source node '{edge.source_id}'.",
                    affected_nodes=[edge.source_id],
                    affected_edges=[(edge.source_id, edge.relation_role, edge.target_id)],
                ))
            if not tgt:
                violations.append(AuditViolation(
                    status=AuditStatus.DANGLING_REFERENCE,
                    description=f"Edge references non-existent target node '{edge.target_id}'.",
                    affected_nodes=[edge.target_id],
                    affected_edges=[(edge.source_id, edge.relation_role, edge.target_id)],
                ))

        # 1.2 Dangling Premise References
        for node in graph.nodes.values():
            if node.epistemic_state == EpistemicState.INFERRED:
                if not node.provenance or not node.provenance.supporting_premises:
                    violations.append(AuditViolation(
                        status=AuditStatus.INVALID_PROVENANCE,
                        description=f"INFERRED node '{node.id}' lacks supporting premises in provenance.",
                        affected_nodes=[node.id],
                    ))
                else:
                    for prem_id in node.provenance.supporting_premises:
                        if prem_id not in graph.nodes:
                            violations.append(AuditViolation(
                                status=AuditStatus.INVALID_PROVENANCE,
                                description=f"INFERRED node '{node.id}' references non-existent premise '{prem_id}'.",
                                affected_nodes=[node.id, prem_id],
                            ))

        # 1.3 Scope Boundary Hierarchy & Acyclicity
        scopes = graph.scopes
        for sid, scope in scopes.items():
            if scope.parent_scope_id:
                if scope.parent_scope_id not in scopes:
                    violations.append(AuditViolation(
                        status=AuditStatus.MALFORMED_STRUCTURE,
                        description=f"Scope '{sid}' references non-existent parent scope '{scope.parent_scope_id}'.",
                    ))
                # Cycle check
                curr = scope.parent_scope_id
                visited_scopes = {sid}
                while curr:
                    if curr in visited_scopes:
                        violations.append(AuditViolation(
                            status=AuditStatus.MALFORMED_STRUCTURE,
                            description=f"Cycle detected in scope hierarchy involving scope '{sid}'.",
                        ))
                        break
                    visited_scopes.add(curr)
                    p_scope = scopes.get(curr)
                    curr = p_scope.parent_scope_id if p_scope else None

        # 1.4 Scope Boundary Crossings
        for edge in graph.edges:
            src = graph.get_node(edge.source_id)
            tgt = graph.get_node(edge.target_id)
            if src and tgt and src.scope_id != tgt.scope_id:
                if not edge.is_cross_scope_link:
                    violations.append(AuditViolation(
                        status=AuditStatus.SCOPE_VIOLATION,
                        description=(
                            f"Edge ({edge.source_id} -> {edge.target_id}, role={edge.relation_role}) "
                            f"crosses scope '{src.scope_id}' -> '{tgt.scope_id}' without being marked as cross-scope link."
                        ),
                        affected_edges=[(edge.source_id, edge.relation_role, edge.target_id)],
                    ))
                elif edge.relation_role not in self.ALLOWED_CROSS_SCOPE_ROLES:
                    violations.append(AuditViolation(
                        status=AuditStatus.SCOPE_VIOLATION,
                        description=(
                            f"Cross-scope edge ({edge.source_id} -> {edge.target_id}) has unauthorized "
                            f"role '{edge.relation_role}'. Allowed roles: {self.ALLOWED_CROSS_SCOPE_ROLES}."
                        ),
                        affected_edges=[(edge.source_id, edge.relation_role, edge.target_id)],
                    ))

        # 1.5 Forbidden Redundancy / Shortcut Topology Injection
        for edge in graph.edges:
            if edge.relation_role == ":session-root-link" or edge.source_id == "SessionRoot":
                violations.append(AuditViolation(
                    status=AuditStatus.REDUNDANCY_INJECTION,
                    description=f"Shortcut/redundancy edge '{edge.relation_role}' is strictly forbidden in semantic topology.",
                    affected_edges=[(edge.source_id, edge.relation_role, edge.target_id)],
                ))

        # 1.6 Explicit Local Contradiction Detection
        # (a) Direct contradictory polarity on identical concept/arguments in same scope
        nodes_by_concept_scope: Dict[Tuple[str, str], List[SemanticNode]] = {}
        for n in graph.nodes.values():
            if n.operational_active:
                nodes_by_concept_scope.setdefault((n.concept_symbol, n.scope_id), []).append(n)

        # Precompute outgoing edges for active nodes: node_id -> sorted tuple of (relation_role, target_id)
        outgoing_by_node: Dict[str, List[Tuple[str, str]]] = {}
        for e in graph.edges:
            outgoing_by_node.setdefault(e.source_id, []).append((e.relation_role, e.target_id))
        outgoing_cached: Dict[str, Tuple[Tuple[str, str], ...]] = {
            nid: tuple(sorted(edges)) for nid, edges in outgoing_by_node.items()
        }

        for (concept_symbol, scope_id), group in nodes_by_concept_scope.items():
            if len(group) > 1:
                pos_nodes = [n for n in group if n.polarity]
                neg_nodes = [n for n in group if not n.polarity]
                if pos_nodes and neg_nodes:
                    for n1 in pos_nodes:
                        n1_targets = outgoing_cached.get(n1.id, ())
                        for n2 in neg_nodes:
                            n2_targets = outgoing_cached.get(n2.id, ())
                            if n1_targets and n1_targets == n2_targets:
                                violations.append(AuditViolation(
                                    status=AuditStatus.CONTRADICTION_DETECTED,
                                    description=(
                                        f"Direct contradictory polarity for concept '{concept_symbol}' "
                                        f"between '{n1.id}' (polarity={n1.polarity}) and '{n2.id}' (polarity={n2.polarity})."
                                    ),
                                    affected_nodes=[n1.id, n2.id],
                                ))

        # (b) Single-valued functional relation contradiction
        single_val_edges: Dict[Tuple[str, str], Set[str]] = {}
        for e in graph.edges:
            if e.relation_role in self.SINGLE_VALUED_ROLES:
                src = graph.get_node(e.source_id)
                if src and src.operational_active:
                    single_val_edges.setdefault((e.source_id, e.relation_role), set()).add(e.target_id)

        for (src_id, role), targets in single_val_edges.items():
            if len(targets) > 1:
                target_list = sorted(list(targets))
                violations.append(AuditViolation(
                    status=AuditStatus.CONTRADICTION_DETECTED,
                    description=(
                        f"Conflicting values for single-valued role '{role}' on "
                        f"subject '{src_id}': targets {target_list}."
                    ),
                    affected_nodes=[src_id] + target_list,
                    affected_edges=[(src_id, role, tgt) for tgt in target_list[:2]],
                ))

        # Compute summary metrics
        status = AuditStatus.VALID
        if violations:
            status = violations[0].status

        fact_count = sum(1 for n in graph.nodes.values() if n.epistemic_state == EpistemicState.FACT and n.operational_active)
        inferred_count = sum(1 for n in graph.nodes.values() if n.epistemic_state == EpistemicState.INFERRED and n.operational_active)
        ambiguous_count = sum(1 for n in graph.nodes.values() if n.epistemic_state == EpistemicState.AMBIGUOUS and n.operational_active)
        unknown_count = sum(1 for n in graph.nodes.values() if n.epistemic_state == EpistemicState.UNKNOWN and n.operational_active)
        invalidated_count = sum(1 for n in graph.nodes.values() if not n.operational_active)

        return AuditReport(
            is_valid=(len(violations) == 0),
            status=status,
            violations=violations,
            structural_checksum=graph.structural_checksum,
            node_count=len(graph.nodes),
            edge_count=len(graph.edges),
            active_fact_count=fact_count,
            active_inferred_count=inferred_count,
            ambiguous_count=ambiguous_count,
            unknown_count=unknown_count,
            invalidated_count=invalidated_count,
        )

    # ── 2. Epistemic Safety & Ingress Guards ───────────────────────────────────

    def attempt_epistemic_transition(
        self,
        graph: SemanticGraph,
        node_id: str,
        target_state: EpistemicState,
        disambiguation_event: bool = False,
    ) -> None:
        """
        Validates an epistemic state transition against the non-increase invariant.
        UNKNOWN -> FACT / INFERRED / concrete entity is STRICTLY FORBIDDEN.
        AMBIGUOUS -> FACT is forbidden unless an explicit upstream disambiguation event occurred.
        """
        node = graph.get_node(node_id)
        if not node:
            raise FortificationError(f"Node '{node_id}' does not exist.")

        curr = node.epistemic_state

        if curr == EpistemicState.UNKNOWN and target_state in (EpistemicState.FACT, EpistemicState.INFERRED):
            raise EpistemicViolationError(
                f"Epistemic commitment increase forbidden: UNKNOWN node '{node_id}' "
                f"cannot be promoted to {target_state.value} by Fortification."
            )

        if curr == EpistemicState.AMBIGUOUS and target_state in (EpistemicState.FACT, EpistemicState.INFERRED):
            if not disambiguation_event:
                raise EpistemicViolationError(
                    f"Premature disambiguation forbidden: AMBIGUOUS node '{node_id}' "
                    f"cannot be resolved to {target_state.value} without an explicit upstream disambiguation event."
                )

        # Apply transition
        node.epistemic_state = target_state
        if disambiguation_event:
            node.is_disambiguated = True

    def attempt_novel_node_insertion(self, graph: SemanticGraph, node: SemanticNode) -> None:
        """
        Enforces the Zero-Ingress Property:
        Fortification MUST NOT create novel entities or facts.
        """
        if graph.is_frozen or node.id in graph._locked_node_ids:
            raise NovelEntityInsertionError(
                f"Novel node insertion forbidden: node '{node.id}' cannot be created during or after fortification."
            )
        graph.add_node(node)

    def attempt_edge_insertion(self, graph: SemanticGraph, edge: SemanticEdge) -> None:
        """
        Enforces Scope Protection and Redundancy Injection rejection.
        """
        if edge.relation_role == ":session-root-link" or edge.source_id == "SessionRoot":
            raise RedundancyInjectionError(
                f"Shortcut/redundancy edge '{edge.relation_role}' cannot be injected into semantic topology."
            )

        src = graph.get_node(edge.source_id)
        tgt = graph.get_node(edge.target_id)
        if not src:
            raise FortificationError(f"Source node '{edge.source_id}' does not exist.")
        if not tgt:
            raise FortificationError(f"Target node '{edge.target_id}' does not exist.")

        if src.scope_id != tgt.scope_id:
            if not edge.is_cross_scope_link or edge.relation_role not in self.ALLOWED_CROSS_SCOPE_ROLES:
                raise ScopeViolationError(
                    f"Attempted to add cross-scope edge ({edge.source_id} -> {edge.target_id}) "
                    f"across '{src.scope_id}' -> '{tgt.scope_id}' with invalid role '{edge.relation_role}'."
                )

        graph.add_edge(edge)

    # ── 3. JTMS Premise Invalidation Propagation ──────────────────────────────

    def propagate_invalidations(self, graph: SemanticGraph, retracted_premise_id: Optional[str] = None) -> List[str]:
        """
        Non-monotonic dependency retraction propagation:
        When a premise is retracted or invalidated:
            premise invalidated
                  ↓
            dependent INFERRED node
                  ↓
            INVALIDATED / inactive in persistent state
        Recursively propagates across multi-hop inference chains (A -> B -> C).
        Does NOT invent or derive new inferences.
        """
        graph._assert_mutable()

        # Build dependency graph: premise_id -> set of dependent node_ids
        dependency_graph: Dict[str, Set[str]] = {}
        for nid, node in graph.nodes.items():
            if node.epistemic_state == EpistemicState.INFERRED and node.provenance:
                for prem_id in node.provenance.supporting_premises:
                    dependency_graph.setdefault(prem_id, set()).add(nid)

        invalidated_ids: List[str] = []

        # Find initial seed of invalidated/retracted premises
        initial_seeds: List[str] = []
        if retracted_premise_id:
            initial_seeds.append(retracted_premise_id)
        else:
            for nid, node in graph.nodes.items():
                if not node.operational_active:
                    initial_seeds.append(nid)

        queue = list(initial_seeds)
        visited = set(initial_seeds)

        while queue:
            curr_id = queue.pop(0)
            dependents = dependency_graph.get(curr_id, set())
            for dep_id in sorted(dependents):
                dep_node = graph.get_node(dep_id)
                if dep_node and dep_node.operational_active:
                    dep_node.operational_active = False
                    dep_node.invalidated_reason = f"Supporting premise '{curr_id}' retracted/invalidated."
                    invalidated_ids.append(dep_id)
                    if dep_id not in visited:
                        visited.add(dep_id)
                        queue.append(dep_id)

        return invalidated_ids

    # ── 4. Canonicalization & Session Fortification ─────────────────────────────

    def canonicalize(self, graph: SemanticGraph) -> SemanticGraph:
        """
        Normalizes deterministic node and edge ordering.
        Produces canonical representation where traversal is independent of insertion order.
        """
        new_graph = SemanticGraph(session_id=graph.session_id)
        for sid in sorted(graph.scopes.keys()):
            new_graph.add_scope(graph.scopes[sid])

        for nid in sorted(graph.nodes.keys()):
            new_graph.add_node(graph.nodes[nid].clone())

        sorted_edges = sorted(
            graph.edges,
            key=lambda e: (e.source_id, e.relation_role, e.target_id),
        )
        for edge in sorted_edges:
            new_graph.add_edge(edge.clone())

        return new_graph

    def fortify_session(self, graph: SemanticGraph) -> Tuple[SemanticGraph, AuditReport]:
        """
        Executes complete session fortification across session boundary:
        1. Canonicalize graph representation.
        2. Propagate premise retraction invalidations.
        3. Perform bounded local consistency checks.
        4. Preserve UNKNOWN and AMBIGUOUS.
        5. Freeze validated session snapshot.
        6. Compute structural integrity checksum.
        """
        # Step 1: Canonicalize
        canonical_graph = self.canonicalize(graph)

        # Step 2: Propagate JTMS premise invalidations
        self.propagate_invalidations(canonical_graph)

        # Step 3: Audit bounded consistency
        audit = self.audit_graph(canonical_graph)

        if not audit.is_valid:
            logger.warning(
                "Fortification audit revealed violations (status=%s): %s",
                audit.status.value,
                [v.description for v in audit.violations],
            )
            # Graph remains unfrozen when invalid
            return canonical_graph, audit

        # Step 4: Freeze and Compute Checksum
        canonical_graph.freeze()
        audit.structural_checksum = canonical_graph.structural_checksum

        return canonical_graph, audit

    # ── 5. Crash-Resilient Persistence ─────────────────────────────────────────

    def persist_fortified_graph(
        self,
        graph: SemanticGraph,
        filepath: Union[str, Path],
    ) -> Path:
        """
        Atomically persists fortified graph to disk using temporary file rename.
        Guarantees crash-resilient disk writes and zero partial records.
        """
        if not graph.is_frozen:
            raise FortificationError("Only frozen fortified graphs may be persisted across session boundaries.")

        target = Path(filepath)
        target.parent.mkdir(parents=True, exist_ok=True)

        data = graph.to_dict()

        temp_fd, temp_path = tempfile.mkstemp(
            dir=str(target.parent),
            prefix="fortified_",
            suffix=".tmp",
        )
        try:
            with os.fdopen(temp_fd, "w", encoding="utf-8") as f:
                json.dump(data, f, indent=2, sort_keys=True, ensure_ascii=False)
                f.flush()
                os.fsync(f.fileno())

            os.replace(temp_path, target)
            logger.debug("Successfully persisted fortified SemanticGraph to %s", target)
        except Exception as e:
            if os.path.exists(temp_path):
                try:
                    os.remove(temp_path)
                except OSError:
                    pass
            logger.error("Failed to persist fortified SemanticGraph to %s: %s", target, e)
            raise

        return target

    def load_fortified_graph(self, filepath: Union[str, Path]) -> SemanticGraph:
        """
        Loads fortified graph from disk and verifies structural integrity checksum.
        """
        target = Path(filepath)
        if not target.exists():
            raise FileNotFoundError(f"Fortified graph file not found: {target}")

        with open(target, "r", encoding="utf-8") as f:
            data = json.load(f)

        graph = SemanticGraph.from_dict(data)

        if not graph.verify_checksum():
            raise ChecksumVerificationError(
                f"Structural checksum verification failed for {target}. "
                f"Stored: {graph.structural_checksum}, Computed: {graph.compute_checksum()}."
            )

        return graph
