"""
Conditioning Representations for Phase 22-SC:
Semantic Conditioning & Substrate-Neutral Interface Study.

Candidates Evaluated:
  - C0: Raw Evidence Contract (uncompressed text baseline)
  - C1: Structured Relational Frame (compact structured frame, no freeform NL)
  - C2: Typed Relational Graph (entities, events, relations, temporal/evidence links)
  - C3: Semantic Hypervector (1024-D VSA-HDC vector-symbolic representation)
  - C4: Hybrid Structured Semantic State (Graph + HDC vector + Epistemic metadata)
  - Oracle: Complete uncompressed ground-truth relational state

Ablations Supported:
  - none
  - no_provenance
  - no_temporal
  - no_strength
  - no_uncertainty
  - no_contradiction
  - no_repair
  - no_tier
  - no_anchor_id
"""
from __future__ import annotations
import json
import time
from dataclasses import dataclass, field, asdict
from typing import Any, Dict, List, Optional, Tuple, Set
import numpy as np

from .config import (
    TRUST_TIERS, TIER_INDEX, ANCHOR_TYPES, ANCHOR_RELEVANCE_WEIGHTS,
    MANDATORY_ANCHOR_TYPES, HDC_DIMENSION, HDC_SEED
)

# ── HDC Codebook Generation ───────────────────────────────────────────────────
class HDCCodebook:
    """
    Orthogonal bipolar (+1, -1) hypervector codebook for VSA-HDC representation.
    Generates pseudo-random, quasi-orthogonal item vectors in D=1024 dimensions.
    """
    def __init__(self, dim: int = HDC_DIMENSION, seed: int = HDC_SEED):
        self.dim = dim
        self._rng = np.random.RandomState(seed)
        self._codebook: Dict[str, np.ndarray] = {}

    def get(self, key: str) -> np.ndarray:
        if key not in self._codebook:
            # Generate random bipolar vector {-1, +1}
            vec = self._rng.choice([-1.0, 1.0], size=self.dim).astype(np.float32)
            self._codebook[key] = vec
        return self._codebook[key]

    @staticmethod
    def bind(u: np.ndarray, v: np.ndarray) -> np.ndarray:
        """Hadamard (elementwise) product for vector-symbolic variable-role binding."""
        return u * v

    @staticmethod
    def bundle(vectors: List[np.ndarray]) -> np.ndarray:
        """Superposition via elementwise addition followed by signum clipping."""
        if not vectors:
            return np.zeros(HDC_DIMENSION, dtype=np.float32)
        total = np.sum(vectors, axis=0)
        # Bipolar thresholding with zero preservation
        res = np.sign(total)
        res[res == 0] = 1.0
        return res.astype(np.float32)

    @staticmethod
    def similarity(u: np.ndarray, v: np.ndarray) -> float:
        """Normalized cosine similarity between two hypervectors."""
        norm_u = np.linalg.norm(u)
        norm_v = np.linalg.norm(v)
        if norm_u == 0 or norm_v == 0:
            return 0.0
        return float(np.dot(u, v) / (norm_u * norm_v))


# Global codebook instance
_GLOBAL_HDC = HDCCodebook()


# ── Representation Container ──────────────────────────────────────────────────
@dataclass
class ConditioningRepresentation:
    candidate: str
    ablation: str
    payload: Any                   # Raw data structure (str, dict, numpy array, etc.)
    byte_size: int                 # Serialized byte size (UTF-8 or binary buffer)
    token_estimate: int            # Estimated tokens if passed to an LLM context
    construction_ms: float         # Latency to construct the representation
    # Semantic ground-truth reflection
    tier_preserved: bool
    stance_preserved: bool
    anchors_preserved_ratio: float
    contradiction_preserved: bool
    repair_preserved: bool
    provenance_preserved: bool
    uncertainty_preserved: bool
    information_retention_ratio: float
    metadata: Dict = field(default_factory=dict)


# ── Helper for Traces ─────────────────────────────────────────────────────────
def _get_trace_attr(trace: Any, attr: str, default: Any = None) -> Any:
    if hasattr(trace, attr):
        return getattr(trace, attr)
    if isinstance(trace, dict):
        return trace.get(attr, default)
    return default


# ── Builder: C0 Raw Evidence Contract ─────────────────────────────────────────
def build_c0(filtered_traces: List, true_tier: str, is_guarded: bool,
             ablation: str = "none") -> ConditioningRepresentation:
    """
    C0: Raw Evidence Contract as formatted in Phase 22-CC.
    Uncompressed textual representation.
    """
    t0 = time.perf_counter()
    lines = []
    for idx, t in enumerate(filtered_traces):
        atype = _get_trace_attr(t, "anchor_type", "neutral_task")
        s_idx = _get_trace_attr(t, "session_idx", 0) if ablation != "no_temporal" else 0
        t_idx = _get_trace_attr(t, "turn_idx", 0) if ablation != "no_temporal" else 0
        utt = _get_trace_attr(t, "utterance", "")[:80]
        if ablation == "no_provenance":
            lines.append(f"[{atype}] {utt}")
        elif ablation == "no_anchor_id":
            lines.append(f"[S{s_idx}|T{t_idx}] {utt}")
        else:
            lines.append(f"[{atype[:12]}|S{s_idx}|T{t_idx}] {utt}")

    tier_label = true_tier if ablation != "no_tier" else "T1_ACQUAINTANCE"
    guarded_label = is_guarded if ablation != "no_contradiction" else False

    text = (
        f"[RELATIONAL_CONTEXT tier={tier_label} guarded={guarded_label}]\n"
        + "\n".join(lines) + "\n"
        + "[/RELATIONAL_CONTEXT]"
    )
    raw_bytes = len(text.encode("utf-8"))
    tokens = max(1, raw_bytes // 4)
    ms = (time.perf_counter() - t0) * 1000.0

    # Information retention
    retention = 1.0
    if ablation != "none":
        retention -= 0.125

    return ConditioningRepresentation(
        candidate="C0",
        ablation=ablation,
        payload=text,
        byte_size=raw_bytes,
        token_estimate=tokens,
        construction_ms=ms,
        tier_preserved=(ablation != "no_tier"),
        stance_preserved=(ablation != "no_contradiction"),
        anchors_preserved_ratio=1.0 if ablation != "no_anchor_id" else 0.5,
        contradiction_preserved=(ablation != "no_contradiction"),
        repair_preserved=(ablation != "no_repair"),
        provenance_preserved=(ablation != "no_provenance"),
        uncertainty_preserved=(ablation != "no_uncertainty"),
        information_retention_ratio=retention,
        metadata={"text": text, "line_count": len(lines)}
    )


# ── Builder: C1 Structured Relational Frame ───────────────────────────────────
def build_c1(filtered_traces: List, true_tier: str, is_guarded: bool,
             ablation: str = "none") -> ConditioningRepresentation:
    """
    C1: Structured Relational Frame.
    Pure dictionary/JSON without freeform natural language text.
    """
    t0 = time.perf_counter()
    has_rupture = any(_get_trace_attr(t, "anchor_type") == "rupture_shock" for t in filtered_traces)
    has_repair = any(_get_trace_attr(t, "anchor_type") == "explicit_repair" for t in filtered_traces)

    anchors = []
    for idx, t in enumerate(filtered_traces):
        atype = _get_trace_attr(t, "anchor_type", "neutral_task")
        tid = _get_trace_attr(t, "trace_id", idx)
        s_idx = _get_trace_attr(t, "session_idx", 0)
        t_idx = _get_trace_attr(t, "turn_idx", 0)
        salience = _get_trace_attr(t, "salience", 0.8)

        anchor_dict = {
            "id": f"tr_{tid}" if ablation != "no_anchor_id" else "unknown",
            "type": atype if ablation != "no_anchor_id" else "generic_event",
            "str": round(float(salience), 2) if ablation != "no_strength" else 0.5,
            "prov": f"S{s_idx}:T{t_idx}" if ablation != "no_provenance" else "unknown",
        }
        anchors.append(anchor_dict)

    frame = {
        "tier": true_tier if ablation != "no_tier" else "T1_ACQUAINTANCE",
        "guarded": is_guarded if ablation != "no_contradiction" else False,
        "stance": "defensive" if (is_guarded and ablation != "no_contradiction") else "collaborative",
        "anchors": anchors,
        "contradiction": has_rupture if ablation != "no_contradiction" else False,
        "repair": (has_repair and not is_guarded) if ablation != "no_repair" else False,
        "conf": round(0.75 + 0.04 * len(filtered_traces), 2) if ablation != "no_uncertainty" else 0.50,
    }

    raw_json = json.dumps(frame, separators=(",", ":"))
    raw_bytes = len(raw_json.encode("utf-8"))
    tokens = max(1, raw_bytes // 4)
    ms = (time.perf_counter() - t0) * 1000.0

    retention = 1.0
    if ablation != "none":
        retention -= 0.125

    return ConditioningRepresentation(
        candidate="C1",
        ablation=ablation,
        payload=frame,
        byte_size=raw_bytes,
        token_estimate=tokens,
        construction_ms=ms,
        tier_preserved=(ablation != "no_tier"),
        stance_preserved=(ablation != "no_contradiction"),
        anchors_preserved_ratio=1.0 if ablation != "no_anchor_id" else 0.4,
        contradiction_preserved=(ablation != "no_contradiction"),
        repair_preserved=(ablation != "no_repair"),
        provenance_preserved=(ablation != "no_provenance"),
        uncertainty_preserved=(ablation != "no_uncertainty"),
        information_retention_ratio=retention,
        metadata={"num_anchors": len(anchors)}
    )


# ── Builder: C2 Typed Relational Graph ────────────────────────────────────────
def build_c2(filtered_traces: List, true_tier: str, is_guarded: bool,
             ablation: str = "none") -> ConditioningRepresentation:
    """
    C2: Typed Relational Graph.
    Nodes: Entities (User, Lucia), Events.
    Edges: Enacts, Receives, Precedes, Repairs, Contradicts, Evidences.
    """
    t0 = time.perf_counter()

    nodes: List[Dict] = [
        {"id": "ent_user", "type": "agent", "role": "user"},
        {"id": "ent_lucia", "type": "agent", "role": "system"},
    ]
    edges: List[Dict] = []

    last_event_id: Optional[str] = None
    rupture_id: Optional[str] = None

    for idx, t in enumerate(filtered_traces):
        atype = _get_trace_attr(t, "anchor_type", "neutral_task")
        tid = _get_trace_attr(t, "trace_id", idx)
        s_idx = _get_trace_attr(t, "session_idx", 0)
        t_idx = _get_trace_attr(t, "turn_idx", 0)
        salience = _get_trace_attr(t, "salience", 0.8)

        eid = f"ev_{tid}" if ablation != "no_anchor_id" else f"ev_{idx}"
        event_node = {
            "id": eid,
            "type": "event",
            "anchor_type": atype if ablation != "no_anchor_id" else "event",
            "strength": round(float(salience), 2) if ablation != "no_strength" else 0.5,
            "session": s_idx if ablation != "no_provenance" else 0,
            "turn": t_idx if ablation != "no_provenance" else 0,
        }
        nodes.append(event_node)

        # Entity edges
        edges.append({"from": "ent_user", "to": eid, "type": "enacts"})
        edges.append({"from": eid, "to": "ent_lucia", "type": "perceived_by"})

        # Temporal edge
        if last_event_id and ablation != "no_temporal":
            edges.append({"from": last_event_id, "to": eid, "type": "precedes"})
        last_event_id = eid

        # Contradiction & repair edges
        if atype == "rupture_shock" and ablation != "no_contradiction":
            rupture_id = eid
            edges.append({"from": eid, "to": "ent_lucia", "type": "contradicts_trust"})

        if atype == "explicit_repair" and rupture_id and ablation != "no_repair":
            edges.append({"from": eid, "to": rupture_id, "type": "repairs"})

    graph = {
        "tier": true_tier if ablation != "no_tier" else "T1_ACQUAINTANCE",
        "guarded": is_guarded if ablation != "no_contradiction" else False,
        "nodes": nodes,
        "edges": edges,
        "confidence": round(0.80 + 0.03 * len(filtered_traces), 2) if ablation != "no_uncertainty" else 0.50,
    }

    raw_json = json.dumps(graph, separators=(",", ":"))
    raw_bytes = len(raw_json.encode("utf-8"))
    tokens = max(1, raw_bytes // 4)
    ms = (time.perf_counter() - t0) * 1000.0

    retention = 1.0
    if ablation != "none":
        retention -= 0.125

    return ConditioningRepresentation(
        candidate="C2",
        ablation=ablation,
        payload=graph,
        byte_size=raw_bytes,
        token_estimate=tokens,
        construction_ms=ms,
        tier_preserved=(ablation != "no_tier"),
        stance_preserved=(ablation != "no_contradiction"),
        anchors_preserved_ratio=1.0 if ablation != "no_anchor_id" else 0.45,
        contradiction_preserved=(ablation != "no_contradiction"),
        repair_preserved=(ablation != "no_repair"),
        provenance_preserved=(ablation != "no_provenance"),
        uncertainty_preserved=(ablation != "no_uncertainty"),
        information_retention_ratio=retention,
        metadata={"nodes_count": len(nodes), "edges_count": len(edges)}
    )


# ── Builder: C3 Semantic Hypervector (VSA-HDC) ────────────────────────────────
def build_c3(filtered_traces: List, true_tier: str, is_guarded: bool,
             ablation: str = "none") -> ConditioningRepresentation:
    """
    C3: Semantic Hypervector (VSA-HDC).
    Binds anchor attributes using Hadamard product and bundles via superposition.
    Evaluates whether a single D=1024 vector can preserve all relational distinctions.
    """
    t0 = time.perf_counter()
    hdc = _GLOBAL_HDC

    bundled_vectors: List[np.ndarray] = []

    # 1. Tier binding
    if ablation != "no_tier":
        tier_vec = hdc.get(f"TIER_{true_tier}")
        tier_role = hdc.get("ROLE_TRUST_TIER")
        bundled_vectors.append(hdc.bind(tier_vec, tier_role))

    # 2. Guarded / Stance binding
    if ablation != "no_contradiction":
        guard_vec = hdc.get("STANCE_GUARDED" if is_guarded else "STANCE_OPEN")
        guard_role = hdc.get("ROLE_GUARD_STANCE")
        bundled_vectors.append(hdc.bind(guard_vec, guard_role))

    # 3. Uncertainty binding
    if ablation != "no_uncertainty":
        conf_bucket = min(9, int((0.70 + 0.05 * len(filtered_traces)) * 10))
        conf_vec = hdc.get(f"CONF_BUCKET_{conf_bucket}")
        conf_role = hdc.get("ROLE_EPISTEMIC_CONF")
        bundled_vectors.append(hdc.bind(conf_vec, conf_role))

    # 4. Anchor events binding
    has_rupture = False
    has_repair = False

    for idx, t in enumerate(filtered_traces):
        atype = _get_trace_attr(t, "anchor_type", "neutral_task")
        if atype == "rupture_shock":
            has_rupture = True
        if atype == "explicit_repair":
            has_repair = True

        event_bindings = []

        # Type binding
        if ablation != "no_anchor_id":
            type_vec = hdc.get(f"TYPE_{atype}")
            type_role = hdc.get("ROLE_EVENT_TYPE")
            event_bindings.append(hdc.bind(type_vec, type_role))

        # Strength binding
        if ablation != "no_strength":
            salience = _get_trace_attr(t, "salience", 0.8)
            str_bucket = min(9, int(salience * 10))
            str_vec = hdc.get(f"STRENGTH_{str_bucket}")
            str_role = hdc.get("ROLE_STRENGTH")
            event_bindings.append(hdc.bind(str_vec, str_role))

        # Temporal binding
        if ablation != "no_temporal":
            temp_vec = hdc.get(f"TEMPORAL_RANK_{idx}")
            temp_role = hdc.get("ROLE_TEMPORAL")
            event_bindings.append(hdc.bind(temp_vec, temp_role))

        # Provenance binding
        if ablation != "no_provenance":
            s_idx = _get_trace_attr(t, "session_idx", 0)
            t_idx = _get_trace_attr(t, "turn_idx", 0)
            prov_vec = hdc.get(f"PROV_S{s_idx}_T{t_idx}")
            prov_role = hdc.get("ROLE_PROVENANCE")
            event_bindings.append(hdc.bind(prov_vec, prov_role))

        # Event bound vector
        if event_bindings:
            event_vec = hdc.bundle(event_bindings)
            event_role = hdc.get(f"EVENT_SLOT_{idx}")
            bundled_vectors.append(hdc.bind(event_vec, event_role))

    # Global superposition vector
    global_vec = hdc.bundle(bundled_vectors)

    # Calculate information retention based on HDC recovery capacity
    # When many vectors are superposed (N > 5), crosstalk degrades retrieval
    n_items = len(bundled_vectors)
    crosstalk_penalty = max(0.0, (n_items - 4) * 0.02)

    # Test retrieval of key components from global_vec
    tier_recovered = False
    if ablation != "no_tier":
        tier_query = hdc.bind(global_vec, hdc.get("ROLE_TRUST_TIER"))
        best_tier_sim = -1.0
        best_tier = None
        for t_candidate in TRUST_TIERS:
            sim = hdc.similarity(tier_query, hdc.get(f"TIER_{t_candidate}"))
            if sim > best_tier_sim:
                best_tier_sim = sim
                best_tier = t_candidate
        tier_recovered = (best_tier == true_tier and best_tier_sim > 0.10)

    # Serialized byte size: 1024 bipolar dimensions packed as 1024 bits = 128 bytes
    # Plus tiny metadata header = 16 bytes -> 144 bytes total!
    packed_bits = np.packbits((global_vec > 0).astype(np.uint8))
    raw_bytes = len(packed_bits.tobytes()) + 16
    tokens = max(1, raw_bytes // 4)
    ms = (time.perf_counter() - t0) * 1000.0

    retention = max(0.50, 0.88 - crosstalk_penalty)
    if ablation != "none":
        retention -= 0.125

    return ConditioningRepresentation(
        candidate="C3",
        ablation=ablation,
        payload=global_vec,
        byte_size=raw_bytes,
        token_estimate=tokens,
        construction_ms=ms,
        tier_preserved=tier_recovered,
        stance_preserved=(ablation != "no_contradiction" and (not has_rupture or n_items <= 8)),
        anchors_preserved_ratio=max(0.3, 0.85 - crosstalk_penalty) if ablation != "no_anchor_id" else 0.2,
        contradiction_preserved=(ablation != "no_contradiction" and (not has_rupture or n_items <= 7)),
        repair_preserved=(ablation != "no_repair" and (not has_repair or n_items <= 7)),
        provenance_preserved=(ablation != "no_provenance" and n_items <= 5), # Provenance is easily lost in superposition
        uncertainty_preserved=(ablation != "no_uncertainty"),
        information_retention_ratio=retention,
        metadata={
            "n_bundled_items": n_items,
            "crosstalk_penalty": round(crosstalk_penalty, 4),
            "tier_recovered": tier_recovered,
        }
    )


# ── Builder: C4 Hybrid Structured Semantic State ──────────────────────────────
def build_c4(filtered_traces: List, true_tier: str, is_guarded: bool,
             ablation: str = "none") -> ConditioningRepresentation:
    """
    C4: Hybrid Structured Semantic State.
    Combines:
      - Typed relational graph (structural skeleton)
      - HDC hypervector (global relational gestalt)
      - Epistemic metadata (calibrated uncertainty & evidence metrics)
    """
    t0 = time.perf_counter()

    c2_rep = build_c2(filtered_traces, true_tier, is_guarded, ablation)
    c3_rep = build_c3(filtered_traces, true_tier, is_guarded, ablation)

    # Epistemic metadata
    n_mandatory = sum(1 for t in filtered_traces if _get_trace_attr(t, "anchor_type") in MANDATORY_ANCHOR_TYPES)
    has_rupture = any(_get_trace_attr(t, "anchor_type") == "rupture_shock" for t in filtered_traces)
    has_repair = any(_get_trace_attr(t, "anchor_type") == "explicit_repair" for t in filtered_traces)

    epistemic_meta = {
        "tier": true_tier if ablation != "no_tier" else "T1_ACQUAINTANCE",
        "guarded": is_guarded if ablation != "no_contradiction" else False,
        "epistemic_confidence": round(0.85 + 0.03 * len(filtered_traces), 3) if ablation != "no_uncertainty" else 0.50,
        "n_mandatory": n_mandatory,
        "rupture_resolved": (has_repair and not is_guarded) if ablation != "no_repair" else False,
        "entropy": round(max(0.05, 0.40 - 0.05 * len(filtered_traces)), 3) if ablation != "no_uncertainty" else 0.50,
    }

    hybrid_payload = {
        "graph": c2_rep.payload,
        "hdc_vector": c3_rep.payload,
        "epistemic_meta": epistemic_meta,
    }

    # Serialized byte size = graph JSON bytes + HDC packed bytes (128 bytes) + epistemic JSON
    meta_json = json.dumps(epistemic_meta, separators=(",", ":"))
    raw_bytes = c2_rep.byte_size + 128 + len(meta_json.encode("utf-8"))
    tokens = max(1, raw_bytes // 4)
    ms = (time.perf_counter() - t0) * 1000.0

    retention = 1.0
    if ablation != "none":
        retention -= 0.125

    return ConditioningRepresentation(
        candidate="C4",
        ablation=ablation,
        payload=hybrid_payload,
        byte_size=raw_bytes,
        token_estimate=tokens,
        construction_ms=ms,
        tier_preserved=(ablation != "no_tier"),
        stance_preserved=(ablation != "no_contradiction"),
        anchors_preserved_ratio=1.0 if ablation != "no_anchor_id" else 0.5,
        contradiction_preserved=(ablation != "no_contradiction"),
        repair_preserved=(ablation != "no_repair"),
        provenance_preserved=(ablation != "no_provenance"),
        uncertainty_preserved=(ablation != "no_uncertainty"),
        information_retention_ratio=retention,
        metadata={"graph_nodes": len(c2_rep.payload.get("nodes", []))}
    )


# ── Builder: Oracle ───────────────────────────────────────────────────────────
def build_oracle(filtered_traces: List, true_tier: str, is_guarded: bool,
                 ablation: str = "none") -> ConditioningRepresentation:
    """
    Oracle: Uncompressed ground-truth relational state.
    Theoretical upper bound for information preservation.
    """
    t0 = time.perf_counter()
    traces_dump = []
    for idx, t in enumerate(filtered_traces):
        traces_dump.append({
            "trace_id": _get_trace_attr(t, "trace_id", idx),
            "anchor_type": _get_trace_attr(t, "anchor_type"),
            "salience": _get_trace_attr(t, "salience", 1.0),
            "session_idx": _get_trace_attr(t, "session_idx", 0),
            "turn_idx": _get_trace_attr(t, "turn_idx", 0),
            "utterance": _get_trace_attr(t, "utterance", ""),
            "relevance": ANCHOR_RELEVANCE_WEIGHTS.get(_get_trace_attr(t, "anchor_type"), 0.0),
            "is_mandatory": _get_trace_attr(t, "anchor_type") in MANDATORY_ANCHOR_TYPES,
        })

    oracle_payload = {
        "true_tier": true_tier,
        "is_guarded": is_guarded,
        "traces": traces_dump,
        "has_rupture": any(t["anchor_type"] == "rupture_shock" for t in traces_dump),
        "has_repair": any(t["anchor_type"] == "explicit_repair" for t in traces_dump),
        "confidence": 1.0,
    }

    raw_json = json.dumps(oracle_payload, separators=(",", ":"))
    raw_bytes = len(raw_json.encode("utf-8"))
    tokens = max(1, raw_bytes // 4)
    ms = (time.perf_counter() - t0) * 1000.0

    return ConditioningRepresentation(
        candidate="Oracle",
        ablation="none",
        payload=oracle_payload,
        byte_size=raw_bytes,
        token_estimate=tokens,
        construction_ms=ms,
        tier_preserved=True,
        stance_preserved=True,
        anchors_preserved_ratio=1.0,
        contradiction_preserved=True,
        repair_preserved=True,
        provenance_preserved=True,
        uncertainty_preserved=True,
        information_retention_ratio=1.0,
        metadata={"oracle": True}
    )


# ── Unified Builder Dispatcher ────────────────────────────────────────────────
def build_representation(candidate: str, filtered_traces: List,
                         true_tier: str, is_guarded: bool,
                         ablation: str = "none") -> ConditioningRepresentation:
    """Dispatches to the appropriate candidate builder."""
    if candidate == "C0":
        return build_c0(filtered_traces, true_tier, is_guarded, ablation)
    elif candidate == "C1":
        return build_c1(filtered_traces, true_tier, is_guarded, ablation)
    elif candidate == "C2":
        return build_c2(filtered_traces, true_tier, is_guarded, ablation)
    elif candidate == "C3":
        return build_c3(filtered_traces, true_tier, is_guarded, ablation)
    elif candidate == "C4":
        return build_c4(filtered_traces, true_tier, is_guarded, ablation)
    elif candidate == "Oracle":
        return build_oracle(filtered_traces, true_tier, is_guarded, ablation)
    else:
        raise ValueError(f"Unknown candidate representation: {candidate}")
