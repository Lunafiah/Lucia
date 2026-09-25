"""
Memory Retrieval Candidate Models for Phase 22-MR.

Each candidate receives:
    - A SimulatedSDM instance (the episodic memory store)
    - A query_dict with turn context (feature vector, current trust tier, session metadata)

Each candidate returns a RetrievalResult:
    - retrieved: List[MemoryTrace]   — the set of traces selected for context
    - context_text: str              — compressed textual summary (for token counting)
    - latency_ms: float              — wall-clock retrieval time
    - metadata: Dict                 — candidate-specific diagnostics

Candidates:
    M0 — Raw memory dump (all stored traces, no filtering)
    M1 — Top-k cosine similarity retrieval
    M2 — Temporal + relational relevance retrieval
    M3 — Graph-aware retrieval (rupture-repair causal chain traversal)
    M4 — Hybrid: cosine + temporal + graph + contradiction filter + uncertainty gate
    Oracle — Ground-truth relevant memories (perfect selector)
"""
from __future__ import annotations
from dataclasses import dataclass, field
from typing import Dict, List, Optional
import time
import numpy as np

from .memory_store import MemoryTrace, SimulatedSDM
from .config import (
    K_RETRIEVAL, MAX_CONTEXT_TOKENS, AVG_CHARS_PER_TOKEN,
    ANCHOR_RELEVANCE_WEIGHTS, MANDATORY_ANCHOR_TYPES,
)


# ─── Output dataclass ─────────────────────────────────────────────────────────

@dataclass
class RetrievalResult:
    retrieved:     List[MemoryTrace]
    context_text:  str
    latency_ms:    float
    metadata:      Dict = field(default_factory=dict)


# ─── Context compression helpers ─────────────────────────────────────────────

def _compress_traces_to_text(traces: List[MemoryTrace]) -> str:
    """
    Convert a list of retrieved memory traces into a compact textual summary
    for SLM conditioning.  Format is intentionally terse to minimize token cost.

    Each line: [type|session|turn] utterance
    """
    if not traces:
        return ""
    lines = []
    for t in traces:
        tag  = f"[{t.anchor_type[:12]}|S{t.session_idx}|T{t.turn_idx}]"
        line = f"{tag} {t.utterance[:80]}"  # hard-cap utterance at 80 chars
        lines.append(line)
    return "\n".join(lines)


def _estimate_tokens(text: str) -> int:
    """Rough token count estimate: characters / avg_chars_per_token."""
    return max(0, len(text) // AVG_CHARS_PER_TOKEN)


def _deduplicate(traces: List[MemoryTrace]) -> List[MemoryTrace]:
    """Remove duplicate trace IDs (preserve first occurrence)."""
    seen = set()
    out  = []
    for t in traces:
        if t.trace_id not in seen:
            seen.add(t.trace_id)
            out.append(t)
    return out


def _trim_to_budget(traces: List[MemoryTrace],
                    max_tokens: int = MAX_CONTEXT_TOKENS) -> List[MemoryTrace]:
    """Drop lowest-priority traces until context fits within token budget."""
    out   = []
    total = 0
    for t in traces:
        line_cost = _estimate_tokens(f"[{t.anchor_type}|S{t.session_idx}|T{t.turn_idx}] {t.utterance[:80]}\n")
        if total + line_cost <= max_tokens:
            out.append(t)
            total += line_cost
    return out


# ─── M0 — Raw Dump ────────────────────────────────────────────────────────────

class Candidate_M0_RawDump:
    """
    M0: Dumps the entire memory store into the context without any filtering.
    Baseline / worst-case: maximum token usage, maximum noise injection risk.
    """
    name = "M0_RawDump"

    def retrieve(self, sdm: SimulatedSDM, query_dict: Dict) -> RetrievalResult:
        t0 = time.perf_counter()
        retrieved = list(sdm.traces)   # All traces, unfiltered
        retrieved = _trim_to_budget(retrieved)  # Still respect token budget
        text      = _compress_traces_to_text(retrieved)
        ms        = (time.perf_counter() - t0) * 1000.0
        return RetrievalResult(
            retrieved    = retrieved,
            context_text = text,
            latency_ms   = ms,
            metadata     = {"total_in_store": sdm.n_traces,
                            "retrieved_count": len(retrieved),
                            "token_estimate": _estimate_tokens(text)},
        )


# ─── M1 — Top-k Cosine Similarity ────────────────────────────────────────────

class Candidate_M1_TopKCosine:
    """
    M1: Retrieves top-k traces by cosine similarity of value vectors to the
    query feature vector. Simple embedding-based retrieval — no structural
    knowledge of anchor types or temporal ordering.
    """
    name = "M1_TopKCosine"

    def __init__(self, k: int = K_RETRIEVAL):
        self.k = k

    def retrieve(self, sdm: SimulatedSDM, query_dict: Dict) -> RetrievalResult:
        t0        = time.perf_counter()
        q_vec     = query_dict["feature_vec"].astype(np.float32)
        q_value   = sdm.make_query_value(q_vec, query_dict.get("anchor_hint", "neutral_task"))
        ranked    = sdm.cosine_similarity(q_value)       # List[(trace, sim)]
        retrieved = [trace for trace, _ in ranked[:self.k]]
        retrieved = _trim_to_budget(retrieved)
        text      = _compress_traces_to_text(retrieved)
        ms        = (time.perf_counter() - t0) * 1000.0
        return RetrievalResult(
            retrieved    = retrieved,
            context_text = text,
            latency_ms   = ms,
            metadata     = {"k": self.k,
                            "retrieved_count": len(retrieved),
                            "token_estimate": _estimate_tokens(text)},
        )


# ─── M2 — Temporal + Relational Relevance ────────────────────────────────────

class Candidate_M2_TemporalRelational:
    """
    M2: Scores traces by a weighted combination of:
      - Cosine similarity to current query
      - Recency (exponential decay by session distance)
      - Anchor type relevance weight (from config)

    Adds structural awareness vs M1 but still no causal graph traversal.
    """
    name = "M2_TemporalRelational"

    def __init__(self, k: int = K_RETRIEVAL,
                 recency_decay: float = 0.30,
                 type_weight:   float = 0.40,
                 sim_weight:    float = 0.30):
        self.k             = k
        self.recency_decay = recency_decay
        self.type_weight   = type_weight
        self.sim_weight    = sim_weight

    def retrieve(self, sdm: SimulatedSDM, query_dict: Dict) -> RetrievalResult:
        t0          = time.perf_counter()
        q_vec       = query_dict["feature_vec"].astype(np.float32)
        q_value     = sdm.make_query_value(q_vec, query_dict.get("anchor_hint", "neutral_task"))
        cur_session = query_dict.get("session_idx", 0)

        # Cosine similarities
        cos_ranked = {t.trace_id: sim
                      for t, sim in sdm.cosine_similarity(q_value)}

        scores: List[tuple] = []
        for trace in sdm.traces:
            sim     = cos_ranked.get(trace.trace_id, 0.0)
            recency = float(np.exp(-self.recency_decay *
                                   max(0, cur_session - trace.session_idx)))
            type_w  = ANCHOR_RELEVANCE_WEIGHTS.get(trace.anchor_type, 0.0)

            score   = (self.sim_weight * sim +
                       self.recency_decay * recency +
                       self.type_weight  * type_w)
            scores.append((trace, score))

        scores.sort(key=lambda x: -x[1])
        retrieved = [t for t, _ in scores[:self.k]]
        retrieved = _trim_to_budget(retrieved)
        text      = _compress_traces_to_text(retrieved)
        ms        = (time.perf_counter() - t0) * 1000.0
        return RetrievalResult(
            retrieved    = retrieved,
            context_text = text,
            latency_ms   = ms,
            metadata     = {"k": self.k,
                            "retrieved_count": len(retrieved),
                            "token_estimate": _estimate_tokens(text)},
        )


# ─── M3 — Graph-Aware Retrieval ───────────────────────────────────────────────

class Candidate_M3_GraphAware:
    """
    M3: Graph-aware retrieval that traverses the causal/temporal episodic event
    graph.  It:
      1. Always retrieves ALL mandatory anchors (ruptures, repairs, milestones).
      2. Traverses the graph forward/backward in session time from each mandatory
         anchor to collect causally adjacent evidence (±1 session window).
      3. Fills remaining budget with top cosine similarity traces.
      4. Hard-excludes neutral_task traces from output.
    """
    name = "M3_GraphAware"

    def __init__(self, k: int = K_RETRIEVAL, session_window: int = 1):
        self.k              = k
        self.session_window = session_window

    def retrieve(self, sdm: SimulatedSDM, query_dict: Dict) -> RetrievalResult:
        t0     = time.perf_counter()
        q_vec  = query_dict["feature_vec"].astype(np.float32)
        q_val  = sdm.make_query_value(q_vec, query_dict.get("anchor_hint", "neutral_task"))

        # Step 1: Mandatory anchor priority guarantee
        mandatory = [t for t in sdm.traces
                     if t.anchor_type in MANDATORY_ANCHOR_TYPES and not t.is_noisy]

        # Step 2: Traverse causal neighborhood of mandatory anchors
        neighborhood: List[MemoryTrace] = list(mandatory)
        mandatory_sessions = {t.session_idx for t in mandatory}
        for trace in sdm.traces:
            if trace.is_noisy:
                continue
            for ms in mandatory_sessions:
                if abs(trace.session_idx - ms) <= self.session_window:
                    neighborhood.append(trace)
                    break

        # Step 3: Hard-exclude neutral_task traces
        neighborhood = [t for t in neighborhood
                        if t.anchor_type != "neutral_task"]

        # Step 4: Fill with cosine similarity traces (exclude already selected)
        selected_ids = {t.trace_id for t in neighborhood}
        cos_ranked   = sdm.cosine_similarity(q_val)
        for trace, sim in cos_ranked:
            if trace.trace_id not in selected_ids and trace.anchor_type != "neutral_task":
                neighborhood.append(trace)
                selected_ids.add(trace.trace_id)
                if len(neighborhood) >= self.k * 2:
                    break

        # Deduplicate and trim
        retrieved = _deduplicate(neighborhood)
        retrieved = _trim_to_budget(retrieved[:self.k * 2])
        text      = _compress_traces_to_text(retrieved)
        ms        = (time.perf_counter() - t0) * 1000.0
        return RetrievalResult(
            retrieved    = retrieved,
            context_text = text,
            latency_ms   = ms,
            metadata     = {"mandatory_retrieved": len(mandatory),
                            "retrieved_count": len(retrieved),
                            "token_estimate": _estimate_tokens(text)},
        )


# ─── M4 — Hybrid Retrieval (Full Proposed Architecture) ─────────────────────

class Candidate_M4_HybridFull:
    """
    M4: Full proposed retrieval architecture combining:
      1. Mandatory anchor guarantee (ruptures, repairs, milestones always included).
      2. Temporal recency weighting.
      3. Anchor type relevance weighting.
      4. Cosine similarity scoring.
      5. Contradiction / noise filtering (exclude noisy / inconsistent traces).
      6. Epistemic uncertainty gate: deprioritize low-confidence traces
         when current trust tier is T0/T1 (early relationship — low evidence density).
      7. Hard token-budget enforcement.
    """
    name = "M4_HybridFull"

    def __init__(self, k: int = K_RETRIEVAL,
                 recency_decay:  float = 0.25,
                 type_weight:    float = 0.35,
                 sim_weight:     float = 0.25,
                 mandatory_boost: float = 0.40):
        self.k               = k
        self.recency_decay   = recency_decay
        self.type_weight     = type_weight
        self.sim_weight      = sim_weight
        self.mandatory_boost = mandatory_boost

    def retrieve(self, sdm: SimulatedSDM, query_dict: Dict) -> RetrievalResult:
        t0          = time.perf_counter()
        q_vec       = query_dict["feature_vec"].astype(np.float32)
        q_val       = sdm.make_query_value(q_vec, query_dict.get("anchor_hint", "neutral_task"))
        cur_session = query_dict.get("session_idx", 0)
        trust_tier  = query_dict.get("trust_tier", "T0_STRANGER")
        low_tier    = trust_tier in ("T0_STRANGER", "T1_ACQUAINTANCE")

        # Cosine similarities
        cos_ranked = {t.trace_id: max(0.0, sim)
                      for t, sim in sdm.cosine_similarity(q_val)}

        scores: List[tuple] = []
        for trace in sdm.traces:
            # Contradiction / noise filter: skip artificially noisy traces
            if trace.is_noisy:
                continue
            # Hard exclusion: neutral_task has zero relational content
            if trace.anchor_type == "neutral_task":
                continue

            sim      = cos_ranked.get(trace.trace_id, 0.0)
            recency  = float(np.exp(-self.recency_decay *
                                    max(0, cur_session - trace.session_idx)))
            type_w   = ANCHOR_RELEVANCE_WEIGHTS.get(trace.anchor_type, 0.0)
            is_mand  = float(trace.anchor_type in MANDATORY_ANCHOR_TYPES)

            # Epistemic gate: in low-tier context, down-weight weak signals
            if low_tier and trace.anchor_type in ("weak_positive", "weak_negative"):
                type_w *= 0.1

            score = (self.sim_weight    * sim    +
                     self.recency_decay * recency +
                     self.type_weight   * type_w  +
                     self.mandatory_boost * is_mand)
            scores.append((trace, score))

        scores.sort(key=lambda x: -x[1])

        # Always guarantee mandatory anchors at front
        mandatory_traces = [t for t, _ in scores
                            if t.anchor_type in MANDATORY_ANCHOR_TYPES]
        other_traces     = [t for t, _ in scores
                            if t.anchor_type not in MANDATORY_ANCHOR_TYPES]

        candidates = mandatory_traces + other_traces
        retrieved  = _deduplicate(candidates)
        retrieved  = _trim_to_budget(retrieved)
        text       = _compress_traces_to_text(retrieved)
        ms         = (time.perf_counter() - t0) * 1000.0

        contradiction_flags = sum(1 for t in sdm.traces if t.is_noisy)
        return RetrievalResult(
            retrieved    = retrieved,
            context_text = text,
            latency_ms   = ms,
            metadata     = {"mandatory_guaranteed": len(mandatory_traces),
                            "retrieved_count": len(retrieved),
                            "contradiction_flags_filtered": contradiction_flags,
                            "token_estimate": _estimate_tokens(text),
                            "trust_tier": trust_tier,
                            "low_tier_epistemic_gate": low_tier},
        )


# ─── Oracle — Perfect Ground-Truth Retrieval ─────────────────────────────────

class OracleRetrieval:
    """
    Oracle: Retrieves exactly the traces marked as relevant (relevance >= 0.5)
    by oracle ground truth.  Never retrieves noisy or neutral_task traces.
    Always includes all mandatory anchors.
    Used as upper-bound reference only.
    """
    name = "Oracle"

    def retrieve(self, sdm: SimulatedSDM, query_dict: Dict) -> RetrievalResult:
        t0 = time.perf_counter()
        relevant  = sdm.relevant_traces(threshold=0.50)
        retrieved = _deduplicate(relevant)
        retrieved = _trim_to_budget(retrieved)
        text      = _compress_traces_to_text(retrieved)
        ms        = (time.perf_counter() - t0) * 1000.0
        return RetrievalResult(
            retrieved    = retrieved,
            context_text = text,
            latency_ms   = ms,
            metadata     = {"oracle_relevant_total": len(sdm.relevant_traces()),
                            "retrieved_count": len(retrieved),
                            "token_estimate": _estimate_tokens(text)},
        )
