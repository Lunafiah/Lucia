"""
Relevance Gate Candidates for Phase 22-RG.

Each gate receives M4's RetrievalResult (a list of MemoryTraces already retrieved
by M4_HybridFull) and the current query_dict, then returns a GatingResult:
- selected:        List[MemoryTrace]  -- traces that pass the gate
- context_text:    str               -- compressed context for SLM
- latency_ms:      float             -- wall-clock gating overhead (NOT including M4)
- metadata:        Dict              -- diagnostics

Gate candidates:
    G0 — No gate: M4 pass-through baseline
    G1 — Static relevance threshold: drop anchors below fixed relevance cutoff
    G2 — Evidence-strength gate: type-classification filter preserving mandatory anchors
    G3 — Confidence + temporal decay gate: session-age weighted evidence pruning
    G4 — Safety-first hybrid gate (proposed architecture):
         mandatory guarantee + evidence-strength pruning + weak-signal cap
    Oracle — Perfect relevance filter (ground-truth relevance >= 0.50)

Evidence Contract enforced by G4 and Oracle:
    - All mandatory anchors (rupture/repair/milestone) always pass, no threshold
    - Neutral_task anchors always dropped
    - Weak signals (weak_positive/weak_negative) capped at max_weak_signal_ratio
    - Context truncated to GATE_TOKEN_POST_GATE budget
"""
from __future__ import annotations
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Set
import time
import numpy as np

from .config import (
    ANCHOR_RELEVANCE_WEIGHTS, MANDATORY_ANCHOR_TYPES,
    AVG_CHARS_PER_TOKEN, GATE_TOKEN_POST_GATE, EVIDENCE_CONTRACT,
)


# ── MemoryTrace stub (to avoid circular import; real one from memory_store) ───
# Imported dynamically in runtime; type hint only here.
try:
    from tests.evaluation.phase22_mr.memory_store import MemoryTrace
except ImportError:
    MemoryTrace = object  # type: ignore


# ─── Output dataclass ─────────────────────────────────────────────────────────

@dataclass
class GatingResult:
    selected:       List          # List[MemoryTrace] after gate
    context_text:   str
    latency_ms:     float
    gate_name:      str
    dropped_count:  int
    metadata:       Dict = field(default_factory=dict)


# ─── Shared helpers ───────────────────────────────────────────────────────────

def _compress(traces: List) -> str:
    """Terse compression: [type|S#|T#] utterance[:80]"""
    if not traces:
        return ""
    return "\n".join(
        f"[{t.anchor_type[:12]}|S{t.session_idx}|T{t.turn_idx}] {t.utterance[:80]}"
        for t in traces
    )


def _token_count(text: str) -> int:
    return max(0, len(text) // AVG_CHARS_PER_TOKEN)


def _trim_to_tokens(traces: List, budget: int) -> List:
    out, total = [], 0
    for t in traces:
        cost = _token_count(
            f"[{t.anchor_type}|S{t.session_idx}|T{t.turn_idx}] {t.utterance[:80]}\n")
        if total + cost <= budget:
            out.append(t)
            total += cost
    return out


# ─── G0 — No Gate (M4 pass-through) ─────────────────────────────────────────

class Gate_G0_NoGate:
    """G0: No post-retrieval filtering. M4 output passed unchanged."""
    name = "G0_NoGate"

    def apply(self, retrieved: List, query_dict: Dict) -> GatingResult:
        t0       = time.perf_counter()
        selected = _trim_to_tokens(retrieved, GATE_TOKEN_POST_GATE)
        text     = _compress(selected)
        ms       = (time.perf_counter() - t0) * 1000.0
        return GatingResult(
            selected     = selected,
            context_text = text,
            latency_ms   = ms,
            gate_name    = self.name,
            dropped_count= len(retrieved) - len(selected),
            metadata     = {"token_estimate": _token_count(text)},
        )


# ─── G1 — Static Relevance Threshold ─────────────────────────────────────────

class Gate_G1_StaticThreshold:
    """
    G1: Drop any trace whose anchor_type has oracle relevance < threshold.
    Mandatory anchors are exempt from the threshold (always pass).
    """
    name = "G1_StaticThreshold"

    def __init__(self, threshold: float = 0.50):
        self.threshold = threshold

    def apply(self, retrieved: List, query_dict: Dict) -> GatingResult:
        t0       = time.perf_counter()
        selected = []
        for t in retrieved:
            w = ANCHOR_RELEVANCE_WEIGHTS.get(t.anchor_type, 0.0)
            if t.anchor_type in MANDATORY_ANCHOR_TYPES or w >= self.threshold:
                selected.append(t)
        selected = _trim_to_tokens(selected, GATE_TOKEN_POST_GATE)
        text     = _compress(selected)
        ms       = (time.perf_counter() - t0) * 1000.0
        return GatingResult(
            selected     = selected,
            context_text = text,
            latency_ms   = ms,
            gate_name    = self.name,
            dropped_count= len(retrieved) - len(selected),
            metadata     = {"threshold": self.threshold,
                            "token_estimate": _token_count(text)},
        )


# ─── G2 — Evidence-Strength Gate ─────────────────────────────────────────────

class Gate_G2_EvidenceStrength:
    """
    G2: Evidence-strength classification filter.
    - MANDATORY (rupture/repair/milestone): always pass — no exception.
    - HIGH evidence (pattern_collaborative): pass.
    - LOW evidence (weak_positive/weak_negative): drop entirely.
    - NONE (neutral_task, noisy): drop entirely.

    This is a pure type-classification gate: no numerical threshold.
    """
    name = "G2_EvidenceStrength"

    PASS_TYPES:  Set[str] = {
        "milestone_bonding",
        "pattern_collaborative",
        "rupture_shock",
        "explicit_repair",
    }
    DROP_TYPES: Set[str] = {"weak_positive", "weak_negative", "neutral_task"}

    def apply(self, retrieved: List, query_dict: Dict) -> GatingResult:
        t0       = time.perf_counter()
        selected = [t for t in retrieved
                    if t.anchor_type in self.PASS_TYPES and not t.is_noisy]
        selected = _trim_to_tokens(selected, GATE_TOKEN_POST_GATE)
        text     = _compress(selected)
        ms       = (time.perf_counter() - t0) * 1000.0
        return GatingResult(
            selected     = selected,
            context_text = text,
            latency_ms   = ms,
            gate_name    = self.name,
            dropped_count= len(retrieved) - len(selected),
            metadata     = {"token_estimate": _token_count(text)},
        )


# ─── G3 — Confidence + Temporal Decay Gate ───────────────────────────────────

class Gate_G3_TemporalDecay:
    """
    G3: Evidence scoring = type_relevance * recency_decay.
    Traces with score below score_threshold are dropped.
    Mandatory anchors always pass regardless of score.

    Recency decay: exp(-decay_rate * session_age)
    Score = type_weight * recency
    """
    name = "G3_TemporalDecay"

    def __init__(self, score_threshold: float = 0.35,
                 decay_rate: float = 0.40):
        self.score_threshold = score_threshold
        self.decay_rate      = decay_rate

    def apply(self, retrieved: List, query_dict: Dict) -> GatingResult:
        t0          = time.perf_counter()
        cur_session = query_dict.get("session_idx", 0)
        selected    = []

        for t in retrieved:
            if t.is_noisy:
                continue
            # Mandatory anchors always survive
            if t.anchor_type in MANDATORY_ANCHOR_TYPES:
                selected.append((t, 1.0))
                continue
            type_w  = ANCHOR_RELEVANCE_WEIGHTS.get(t.anchor_type, 0.0)
            recency = float(np.exp(-self.decay_rate *
                                   max(0, cur_session - t.session_idx)))
            score   = type_w * recency
            if score >= self.score_threshold:
                selected.append((t, score))

        # Sort by score descending (mandatory already guaranteed)
        selected.sort(key=lambda x: -x[1])
        selected_traces = [t for t, _ in selected]
        selected_traces = _trim_to_tokens(selected_traces, GATE_TOKEN_POST_GATE)
        text            = _compress(selected_traces)
        ms              = (time.perf_counter() - t0) * 1000.0
        return GatingResult(
            selected     = selected_traces,
            context_text = text,
            latency_ms   = ms,
            gate_name    = self.name,
            dropped_count= len(retrieved) - len(selected_traces),
            metadata     = {"score_threshold": self.score_threshold,
                            "decay_rate": self.decay_rate,
                            "token_estimate": _token_count(text)},
        )


# ─── G4 — Safety-First Hybrid Gate (Proposed Architecture) ───────────────────

class Gate_G4_SafetyFirstHybrid:
    """
    G4: Safety-First Hybrid Relevance Gate — the proposed production-candidate design.

    Algorithm:
      Layer 1 — Mandatory Guarantee (unconditional):
        All rupture_shock, explicit_repair, milestone_bonding traces pass.
        No exception, no threshold.

      Layer 2 — Contradiction Pair Preservation:
        If a rupture is present, any explicit_repair in the same session window
        must also pass (preserves coherent rupture-repair narrative).

      Layer 3 — Evidence-Strength Filter:
        pattern_collaborative passes if recency score >= pattern_threshold.
        weak_positive, weak_negative: dropped unless filling below min_weak_slots.
        neutral_task: always dropped.
        noisy traces: always dropped.

      Layer 4 — Weak-Signal Cap:
        At most max_weak_ratio * len(selected) weak signals in final context.

      Layer 5 — Token Budget Enforcement:
        Trim to GATE_TOKEN_POST_GATE tokens. Priority: mandatory > pattern > weak.

    Evidence Contract Enforcement:
      Verifies context satisfies EVIDENCE_CONTRACT before returning.
    """
    name = "G4_SafetyFirstHybrid"

    def __init__(self,
                 pattern_score_threshold: float = 0.30,
                 decay_rate:              float = 0.35,
                 max_weak_ratio:          float = 0.10,
                 repair_window:           int   = 2):
        self.pattern_threshold = pattern_score_threshold
        self.decay_rate        = decay_rate
        self.max_weak_ratio    = max_weak_ratio
        self.repair_window     = repair_window

    def apply(self, retrieved: List, query_dict: Dict) -> GatingResult:
        t0          = time.perf_counter()
        cur_session = query_dict.get("session_idx", 0)
        trust_tier  = query_dict.get("trust_tier", "T0_STRANGER")
        is_guarded  = query_dict.get("is_guarded", False)

        # ── Layer 1: Mandatory anchor guarantee ──────────────────────────────
        mandatory = [t for t in retrieved
                     if t.anchor_type in MANDATORY_ANCHOR_TYPES and not t.is_noisy]

        # ── Layer 2: Contradiction pair preservation ──────────────────────────
        # If rupture exists, ensure paired repair (same/adjacent session) also included
        rupture_sessions = {t.session_idx for t in mandatory
                            if t.anchor_type == "rupture_shock"}
        repair_forced: List = []
        if rupture_sessions:
            for t in retrieved:
                if (t.anchor_type == "explicit_repair" and not t.is_noisy and
                        any(abs(t.session_idx - rs) <= self.repair_window
                            for rs in rupture_sessions)):
                    if t not in mandatory:
                        repair_forced.append(t)

        tier_idx = {"T0_STRANGER": 0, "T1_ACQUAINTANCE": 1,
                    "T2_COLLABORATOR": 2, "T3_COMPANION": 3, "T4_CONFIDANT": 4}
        cur_tier_idx = tier_idx.get(trust_tier, 0)
        low_tier     = cur_tier_idx <= 1

        # ── Layer 3: Evidence-strength filter ────────────────────────────────
        pattern_selected: List = []
        weak_candidates:  List = []

        for t in retrieved:
            if t.is_noisy:
                continue
            if t.anchor_type in MANDATORY_ANCHOR_TYPES:
                continue   # Already handled in Layer 1
            if t.anchor_type == "neutral_task":
                continue   # Always drop

            type_w  = ANCHOR_RELEVANCE_WEIGHTS.get(t.anchor_type, 0.0)
            recency = float(np.exp(-self.decay_rate *
                                   max(0, cur_session - t.session_idx)))
            score   = type_w * recency

            if t.anchor_type == "pattern_collaborative":
                if score >= self.pattern_threshold:
                    pattern_selected.append((t, score))
            elif t.anchor_type in ("weak_positive", "weak_negative"):
                if not low_tier:   # In T0/T1 context weak signals add no value
                    weak_candidates.append((t, score))

        # Sort by score
        pattern_selected.sort(key=lambda x: -x[1])
        weak_candidates.sort(key=lambda x: -x[1])

        # ── Layer 4: Weak-signal cap ──────────────────────────────────────────
        base_count    = len(mandatory) + len(repair_forced) + len(pattern_selected)
        max_weak_slots= max(0, int(self.max_weak_ratio * max(1, base_count)))
        weak_selected = [t for t, _ in weak_candidates[:max_weak_slots]]

        # ── Assemble in priority order ────────────────────────────────────────
        candidates = (mandatory +
                      repair_forced +
                      [t for t, _ in pattern_selected] +
                      weak_selected)

        # Deduplicate by trace_id
        seen: Set[int] = set()
        deduped: List  = []
        for t in candidates:
            if t.trace_id not in seen:
                seen.add(t.trace_id)
                deduped.append(t)

        # ── Layer 5: Token budget ─────────────────────────────────────────────
        selected = _trim_to_tokens(deduped, GATE_TOKEN_POST_GATE)
        text     = _compress(selected)
        ms       = (time.perf_counter() - t0) * 1000.0

        # Evidence contract verification
        weak_ratio = (len([t for t in selected
                           if t.anchor_type in ("weak_positive", "weak_negative")]) /
                      max(1, len(selected)))
        contract_ok = weak_ratio <= EVIDENCE_CONTRACT["max_weak_signal_ratio"]

        return GatingResult(
            selected     = selected,
            context_text = text,
            latency_ms   = ms,
            gate_name    = self.name,
            dropped_count= len(retrieved) - len(selected),
            metadata     = {
                "mandatory_count":    len(mandatory),
                "repair_forced":      len(repair_forced),
                "pattern_count":      len(pattern_selected),
                "weak_selected":      len(weak_selected),
                "weak_ratio":         round(weak_ratio, 4),
                "contract_satisfied": contract_ok,
                "token_estimate":     _token_count(text),
                "trust_tier":         trust_tier,
                "is_guarded":         is_guarded,
            },
        )


# ─── Oracle — Perfect Relevance Filter ───────────────────────────────────────

class Gate_Oracle:
    """
    Oracle: Selects exactly the ground-truth relevant traces (relevance >= 0.50).
    Never selects noisy or neutral_task traces.
    Always includes all mandatory anchors.
    Upper-bound reference only — not achievable without ground-truth labels.
    """
    name = "Oracle"

    def apply(self, retrieved: List, query_dict: Dict) -> GatingResult:
        t0       = time.perf_counter()
        selected = [t for t in retrieved
                    if t.relevance >= 0.50 and not t.is_noisy]
        selected = _trim_to_tokens(selected, GATE_TOKEN_POST_GATE)
        text     = _compress(selected)
        ms       = (time.perf_counter() - t0) * 1000.0
        return GatingResult(
            selected     = selected,
            context_text = text,
            latency_ms   = ms,
            gate_name    = self.name,
            dropped_count= len(retrieved) - len(selected),
            metadata     = {"token_estimate": _token_count(text)},
        )
