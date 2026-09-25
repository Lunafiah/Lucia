"""
Phase 23 Semantic Formation Microbenchmark v0.2 — Configuration & Types
Defines schemas, gates, seeds, and constants for audited P23 benchmark evaluation.
"""
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Any, Set, Tuple
import numpy as np

# Preregistered evaluation seeds
SEEDS: List[int] = [42, 1337, 2026, 7113, 8421]

# 12 Master Acceptance Gates (v0.2 Audited)
GATES_V02: Dict[str, Dict[str, Any]] = {
    "G-MB-1": {
        "name": "Structural Graph Validity Rate (SGVR)",
        "track": "Track 1 (U1)",
        "target": 0.950,
        "operator": ">=",
        "falsification": 0.800,
        "unit": "ratio",
    },
    "G-MB-2": {
        "name": "Causal Formation Sensitivity (CFS)",
        "track": "Track 1 (U1)",
        "target": 0.800,
        "operator": ">=",
        "falsification": 0.600,
        "unit": "sensitivity",
    },
    "G-MB-3": {
        "name": "Referential Grounding Precision (RGP)",
        "track": "Track 2 (U2)",
        "target": 0.900,
        "operator": ">=",
        "falsification": 0.800,
        "unit": "precision",
    },
    "G-MB-4": {
        "name": "50-Turn Longitudinal Drift (D50)",
        "track": "Track 2 (U2)",
        "target": 0.050,
        "operator": "<=",
        "falsification": 0.150,
        "unit": "displacement",
    },
    "G-MB-5": {
        "name": "Nested Proposition Fidelity @ D=3 (RF3)",
        "track": "Track 3 (U3)",
        "target": 0.850,
        "operator": ">=",
        "falsification": 0.700,
        "unit": "accuracy",
    },
    "G-MB-6": {
        "name": "Negation Polarity Accuracy (NPA)",
        "track": "Track 3 (U3)",
        "target": 0.950,
        "operator": ">=",
        "falsification": 0.850,
        "unit": "accuracy",
    },
    "G-MB-7": {
        "name": "Decision Flapping Rate (DFR)",
        "track": "Track 4 (U4)",
        "target": 0.050,
        "operator": "<=",
        "falsification": 0.100,
        "unit": "ratio",
    },
    "G-MB-8": {
        "name": "Limbic Lyapunov Exponent (lambda_max)",
        "track": "Track 4 (U4)",
        "target": 0.000,
        "operator": "<=",
        "falsification": 0.001,
        "unit": "exponent",
    },
    "G-MB-9": {
        "name": "Fact Retention After Delta (RUF)",
        "track": "Track 5 (U5)",
        "target": 0.980,
        "operator": ">=",
        "falsification": 0.900,
        "unit": "ratio",
    },
    "G-MB-10": {
        "name": "Historical Semantic Drift (Delta_drift)",
        "track": "Track 5 (U5)",
        "target": 0.050,
        "operator": "<=",
        "falsification": 0.150,
        "unit": "divergence",
    },
    "G-MB-11": {
        "name": "Taxonomic Placement Accuracy (TPA)",
        "track": "Track 6 (U6)",
        "target": 0.800,
        "operator": ">=",
        "falsification": 0.650,
        "unit": "accuracy",
    },
    "G-MB-12": {
        "name": "Hardware Execution SLA (CPU P50 ms & VRAM MB)",
        "track": "Hardware",
        "target_latency_ms": 5.0,
        "target_vram_mb": 0.0,
        "operator": "<=",
        "falsification_latency_ms": 30.0,
        "unit": "ms / MB",
    },
}

# Standard Thematic Roles
THEMATIC_ROLES = [
    "AGENT",
    "PATIENT",
    "THEME",
    "BENEFICIARY",
    "EXPERIENCER",
    "INSTRUMENT",
    "LOCATION",
    "TEMPORAL_ANCHOR",
    "PURPOSE",
]

# Dialogue Acts
DIALOGUE_ACTS = [
    "INFORM",
    "PROPOSE",
    "CLARIFY_QUERY",
    "ASSERT_BOUNDARY",
    "ACKNOWLEDGE",
    "REPAIR_BILATERAL",
    "CHECK_STATE",
]

# Trust Tiers inherited from Phase 22
TRUST_TIERS = [
    "T0_STRANGER",
    "T1_ACQUAINTANCE",
    "T2_COLLABORATOR",
    "T3_COMPANION",
    "T4_CONFIDANT",
]


@dataclass
class ContinuousCognitiveState:
    """Continuous internal cognitive & physiological state of Lucia."""
    pad: np.ndarray             # [P, A, D] in [-1, 1]^3
    somatic_energy: float       # in [0.0, 1.0]
    relational_trust: float     # in [0.0, 1.0]
    epistemic_entropy: float    # in [0.0, 2.0] nats
    active_breach: bool = False
    bilateral_repair: bool = False


@dataclass
class CommunicativeIntention:
    """Explicit communicative intention causally derived from cognitive state."""
    act_type: str
    target_entities: List[str]
    affective_drive: np.ndarray  # [P, A, D] in [-1, 1]^3
    relational_tier: str         # T0..T4
    epistemic_confidence: float  # [0.0, 1.0]
    is_guarded: bool = False
    has_rupture: bool = False
    has_repair: bool = False
    urgency: float = 0.5
    target_cardinality: int = 3
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class SemanticNode:
    """Individual node in the semantic graph."""
    node_id: str
    node_type: str  # entity | event | concept | predicate | modifier
    label: str
    provenance_anchor: Optional[str] = None  # Reference to persistent episodic anchor
    attributes: Dict[str, Any] = field(default_factory=dict)
    salience: float = 1.0
    negated: bool = False
    epistemic_modality: str = "FACTUAL"  # FACTUAL | CERTAIN | POSSIBLE | DOUBTFUL | COUNTERFACTUAL
    vector: Optional[np.ndarray] = None


@dataclass
class SemanticEdge:
    """Typed directed relation between semantic nodes."""
    source_id: str
    target_id: str
    relation_type: str  # thematic role (AGENT, PATIENT, etc.) or cognitive relation
    weight: float = 1.0
    attributes: Dict[str, Any] = field(default_factory=dict)


@dataclass
class SemanticGraph:
    """Variable-size grounded compositional semantic state."""
    nodes: Dict[str, SemanticNode] = field(default_factory=dict)
    edges: List[SemanticEdge] = field(default_factory=list)
    gestalt_vector: Optional[np.ndarray] = None  # HDC hypervector binding
    epistemic_confidence: float = 1.0
    intention_source: Optional[CommunicativeIntention] = None

    def add_node(self, node: SemanticNode) -> None:
        self.nodes[node.node_id] = node

    def add_edge(self, edge: SemanticEdge) -> None:
        self.edges.append(edge)

    def get_neighbors(self, node_id: str) -> List[Tuple[str, str]]:
        """Returns list of (target_id, relation_type)."""
        return [(e.target_id, e.relation_type) for e in self.edges if e.source_id == node_id]

    def clone(self) -> "SemanticGraph":
        """Deep clone of the semantic graph."""
        import copy
        return copy.deepcopy(self)
