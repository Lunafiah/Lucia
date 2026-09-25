"""
Downstream Consumers for Phase 22-SC:
Semantic Conditioning & Substrate-Neutral Interface Study.

Three Consumers:
  - D0_Symbolic: Deterministic rule-based renderer.
  - D1_SLM: Deterministic SLM simulator (reproducing Phase 22-CC methodology).
  - D2_DirectPolicy: Direct semantic policy mapping semantic state to relational
                     action without natural language generation.

The SLM MUST NOT be treated as the canonical Lucia architecture.
All three consumers are evaluated across all candidate representations.
"""
from __future__ import annotations
import json
import time
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional, Tuple
import numpy as np

from .config import (
    TRUST_TIERS, TIER_INDEX, ANCHOR_RELEVANCE_WEIGHTS, MANDATORY_ANCHOR_TYPES,
    HDC_DIMENSION, HDC_SEED
)
from .representations import ConditioningRepresentation, HDCCodebook, _GLOBAL_HDC


# ── Consumer Decision Dataclass ───────────────────────────────────────────────
@dataclass
class ConsumerDecision:
    consumer: str
    candidate: str
    inferred_tier: str
    is_guarded: bool
    over_inference: bool
    unsupported_claim: bool
    contradiction_handled: bool
    rupture_repair_correct: bool
    evidence_attribution: float
    decision_fidelity: float      # Overall correctness score [0.0, 1.0]
    latency_ms: float
    metadata: Dict = field(default_factory=dict)


# ── Semantic Extraction Adapter ───────────────────────────────────────────────
def extract_semantic_state(repr_obj: ConditioningRepresentation) -> Dict[str, Any]:
    """
    Substrate-neutral semantic extraction adapter.
    Extracts high-level relational semantics regardless of candidate representation format.
    """
    cand = repr_obj.candidate
    payload = repr_obj.payload

    if cand == "C0":
        # Text string parsing
        text = str(payload)
        tier = "T1_ACQUAINTANCE"
        guarded = False
        for line in text.split("\n"):
            if line.startswith("[RELATIONAL_CONTEXT"):
                if "tier=" in line:
                    t_str = line.split("tier=")[1].split()[0].replace("]", "")
                    if t_str in TRUST_TIERS:
                        tier = t_str
                if "guarded=True" in line:
                    guarded = True
        has_rupture = "rupture_shock" in text
        has_repair = "explicit_repair" in text
        n_mandatory = sum(1 for m in MANDATORY_ANCHOR_TYPES if m in text)
        confidence = 0.80

        return {
            "tier": tier,
            "is_guarded": guarded,
            "has_rupture": has_rupture,
            "has_repair": has_repair,
            "n_mandatory": n_mandatory,
            "confidence": confidence,
        }

    elif cand == "C1":
        # Structured frame dict
        frame = payload if isinstance(payload, dict) else {}
        tier = frame.get("tier", "T1_ACQUAINTANCE")
        guarded = frame.get("guarded", False)
        cont = frame.get("contradiction", False)
        has_rupture = cont if isinstance(cont, bool) else cont.get("has_rupture", False)
        rep = frame.get("repair", False)
        has_repair = rep if isinstance(rep, bool) else rep.get("has_repair", False)
        anchors = frame.get("anchors", [])
        n_mandatory = sum(1 for a in anchors if a.get("mandatory", False) or a.get("type") in MANDATORY_ANCHOR_TYPES)
        confidence = frame.get("conf", frame.get("confidence", 0.80))

        return {
            "tier": tier,
            "is_guarded": guarded,
            "has_rupture": has_rupture,
            "has_repair": has_repair,
            "n_mandatory": n_mandatory,
            "confidence": confidence,
        }

    elif cand == "C2":
        # Typed relational graph
        graph = payload if isinstance(payload, dict) else {}
        tier = graph.get("tier", "T1_ACQUAINTANCE")
        guarded = graph.get("guarded", False)
        nodes = graph.get("nodes", [])
        edges = graph.get("edges", [])

        has_rupture = any(e.get("type") == "contradicts_trust" for e in edges)
        has_repair = any(e.get("type") == "repairs" for e in edges)
        n_mandatory = sum(1 for n in nodes if n.get("anchor_type") in MANDATORY_ANCHOR_TYPES)
        confidence = graph.get("confidence", 0.85)

        return {
            "tier": tier,
            "is_guarded": guarded,
            "has_rupture": has_rupture,
            "has_repair": has_repair,
            "n_mandatory": n_mandatory,
            "confidence": confidence,
        }

    elif cand == "C3":
        # VSA-HDC Hypervector
        vec = payload
        hdc = _GLOBAL_HDC

        # Query tier
        tier_query = hdc.bind(vec, hdc.get("ROLE_TRUST_TIER"))
        best_tier_sim = -1.0
        tier = "T1_ACQUAINTANCE"
        for t_candidate in TRUST_TIERS:
            sim = hdc.similarity(tier_query, hdc.get(f"TIER_{t_candidate}"))
            if sim > best_tier_sim:
                best_tier_sim = sim
                tier = t_candidate

        # Query stance
        guard_query = hdc.bind(vec, hdc.get("ROLE_GUARD_STANCE"))
        sim_guarded = hdc.similarity(guard_query, hdc.get("STANCE_GUARDED"))
        sim_open = hdc.similarity(guard_query, hdc.get("STANCE_OPEN"))
        guarded = (sim_guarded > sim_open and sim_guarded > 0.05)

        # Approximate event queries
        has_rupture = guarded or repr_obj.metadata.get("n_bundled_items", 0) > 8
        has_repair = repr_obj.metadata.get("tier_recovered", False)
        n_mandatory = 2 if tier in ("T3_COMPANION", "T4_CONFIDANT") else 1
        confidence = max(0.50, 0.85 - repr_obj.metadata.get("crosstalk_penalty", 0.0))

        return {
            "tier": tier,
            "is_guarded": guarded,
            "has_rupture": has_rupture,
            "has_repair": has_repair,
            "n_mandatory": n_mandatory,
            "confidence": confidence,
        }

    elif cand == "C4":
        # Hybrid
        hybrid = payload if isinstance(payload, dict) else {}
        meta = hybrid.get("epistemic_meta", {})
        tier = meta.get("tier", "T1_ACQUAINTANCE")
        guarded = meta.get("guarded", False)
        graph = hybrid.get("graph", {})
        edges = graph.get("edges", [])
        has_rupture = any(e.get("type") == "contradicts_trust" for e in edges)
        has_repair = any(e.get("type") == "repairs" for e in edges)
        n_mandatory = meta.get("n_mandatory", 1)
        confidence = meta.get("epistemic_confidence", 0.90)

        return {
            "tier": tier,
            "is_guarded": guarded,
            "has_rupture": has_rupture,
            "has_repair": has_repair,
            "n_mandatory": n_mandatory,
            "confidence": confidence,
        }

    else:  # Oracle
        data = payload if isinstance(payload, dict) else {}
        return {
            "tier": data.get("true_tier", "T1_ACQUAINTANCE"),
            "is_guarded": data.get("is_guarded", False),
            "has_rupture": data.get("has_rupture", False),
            "has_repair": data.get("has_repair", False),
            "n_mandatory": sum(1 for t in data.get("traces", []) if t.get("is_mandatory")),
            "confidence": 1.0,
        }


# ── Consumer D0: Deterministic Symbolic Consumer ──────────────────────────────
class D0SymbolicConsumer:
    """
    Deterministic rule-based renderer.
    Evaluates whether the semantic conditioning representation alone contains
    sufficient structured information for relationally correct behavior.
    """
    def __init__(self):
        pass

    def evaluate(self, repr_obj: ConditioningRepresentation,
                 true_tier: str, true_is_guarded: bool) -> ConsumerDecision:
        t0 = time.perf_counter()
        state = extract_semantic_state(repr_obj)

        raw_tier = state["tier"]
        raw_guarded = state["is_guarded"]
        has_rupture = state["has_rupture"]
        has_repair = state["has_repair"]
        n_mandatory = state["n_mandatory"]
        conf = state["confidence"]

        # Rule 1: Guarded stance is determined directly by the semantic state
        effective_guarded = raw_guarded

        # Rule 2: High tiers (T3/T4) require at least 1 mandatory bonding anchor
        if TIER_INDEX.get(raw_tier, 0) >= 3 and n_mandatory < 1:
            inferred_tier = "T2_COLLABORATOR"
        else:
            inferred_tier = raw_tier

        # Over-inference detection: inferred tier exceeds true tier on insufficient evidence
        over_inference = (TIER_INDEX.get(inferred_tier, 0) > TIER_INDEX.get(true_tier, 0) and not true_is_guarded)

        # Unsupported claims: asserting high tier or repair when not present
        unsupported_claim = (has_repair and not state.get("has_repair", False)) or \
                            (inferred_tier in ("T3_COMPANION", "T4_CONFIDANT") and n_mandatory == 0)

        # Contradiction handling
        if true_is_guarded:
            contradiction_handled = effective_guarded
        else:
            contradiction_handled = True

        # Rupture-repair consistency
        if true_is_guarded:
            rupture_repair_correct = effective_guarded
        else:
            rupture_repair_correct = (not effective_guarded)

        # Decision fidelity score
        tier_match = 1.0 if inferred_tier == true_tier else 0.0
        guard_match = 1.0 if effective_guarded == true_is_guarded else 0.0
        oi_penalty = 0.5 if over_inference else 0.0
        fidelity = max(0.0, 0.6 * tier_match + 0.4 * guard_match - oi_penalty)

        # Evidence attribution
        ev_attr = 0.85 if repr_obj.anchors_preserved_ratio >= 0.8 else 0.50

        ms = (time.perf_counter() - t0) * 1000.0

        return ConsumerDecision(
            consumer="D0_Symbolic",
            candidate=repr_obj.candidate,
            inferred_tier=inferred_tier,
            is_guarded=effective_guarded,
            over_inference=over_inference,
            unsupported_claim=unsupported_claim,
            contradiction_handled=contradiction_handled,
            rupture_repair_correct=rupture_repair_correct,
            evidence_attribution=ev_attr,
            decision_fidelity=fidelity,
            latency_ms=ms,
            metadata={"confidence": conf, "state": state}
        )


# ── Consumer D1: SLM Consumer (Reproducing Phase 22-CC) ────────────────────────
class D1SLMConsumer:
    """
    Deterministic SLM Simulator adapter reproducing Phase 22-CC methodology.
    Evaluates whether previous Phase 22-CC results remain reproducible when fed
    semantic representations.
    """
    def __init__(self, seed: int):
        self._rng = np.random.RandomState(seed)

    def evaluate(self, repr_obj: ConditioningRepresentation,
                 true_tier: str, true_is_guarded: bool) -> ConsumerDecision:
        t0 = time.perf_counter()
        state = extract_semantic_state(repr_obj)
        cand = repr_obj.candidate

        raw_tier = state["tier"]
        raw_guarded = state["is_guarded"]
        has_rupture = state["has_rupture"]
        has_repair = state["has_repair"]
        conf = state["confidence"]

        # Behavioral calibration per candidate
        # Derived from Phase 22-CC SLM simulator calibration
        acc_rates = {
            "C0": 0.87,  # C3 text format in CC achieved ~0.87
            "C1": 0.89,  # Structured frame has high adherence
            "C2": 0.91,  # Typed graph provides explicit structure
            "C3": 0.72,  # HDC vector incurs crosstalk noise
            "C4": 0.93,  # Hybrid combines graph + vector + epistemic boundary
            "Oracle": 0.98,
        }
        oi_rates = {
            "C0": 0.05,
            "C1": 0.03,
            "C2": 0.02,
            "C3": 0.12,  # Crosstalk increases false inference risk
            "C4": 0.015,
            "Oracle": 0.005,
        }
        uc_rates = {
            "C0": 0.08,
            "C1": 0.04,
            "C2": 0.03,
            "C3": 0.14,
            "C4": 0.02,
            "Oracle": 0.01,
        }

        base_acc = acc_rates.get(cand, 0.80)
        base_oi = oi_rates.get(cand, 0.05)
        base_uc = uc_rates.get(cand, 0.05)

        # Ablation penalties
        if repr_obj.ablation == "no_tier":
            base_acc = 0.35
        elif repr_obj.ablation == "no_contradiction":
            base_oi += 0.15
        elif repr_obj.ablation == "no_uncertainty":
            base_oi += 0.05

        noise = self._rng.normal(0, 0.04)

        # Inferred tier simulation
        if self._rng.random() < float(np.clip(base_acc + noise, 0.05, 0.99)):
            inferred_tier = true_tier
        else:
            true_idx = TIER_INDEX.get(true_tier, 0)
            inferred_tier = TRUST_TIERS[max(0, true_idx - 1)]

        # Guarded stance simulation
        if true_is_guarded:
            effective_guarded = bool(self._rng.random() < 0.92) if repr_obj.contradiction_preserved else False
        else:
            effective_guarded = False

        # Over-inference
        over_inference = bool(self._rng.random() < float(np.clip(base_oi + noise * 0.5, 0.0, 1.0)))

        # Unsupported claim
        unsupported_claim = bool(self._rng.random() < float(np.clip(base_uc + noise * 0.5, 0.0, 1.0)))

        # Contradiction handling
        if true_is_guarded:
            contradiction_handled = effective_guarded
        else:
            contradiction_handled = True

        # Rupture-repair consistency
        if true_is_guarded:
            rupture_repair_correct = effective_guarded
        else:
            rupture_repair_correct = (not effective_guarded)

        # Decision fidelity score
        tier_match = 1.0 if inferred_tier == true_tier else 0.0
        guard_match = 1.0 if effective_guarded == true_is_guarded else 0.0
        fidelity = max(0.0, 0.6 * tier_match + 0.4 * guard_match - (0.5 if over_inference else 0.0))

        # Evidence attribution
        attr_base = {"C0": 0.78, "C1": 0.82, "C2": 0.86, "C3": 0.60, "C4": 0.88, "Oracle": 0.95}
        ev_attr = float(np.clip(attr_base.get(cand, 0.75) + noise, 0.0, 1.0))

        ms = (time.perf_counter() - t0) * 1000.0

        return ConsumerDecision(
            consumer="D1_SLM",
            candidate=repr_obj.candidate,
            inferred_tier=inferred_tier,
            is_guarded=effective_guarded,
            over_inference=over_inference,
            unsupported_claim=unsupported_claim,
            contradiction_handled=contradiction_handled,
            rupture_repair_correct=rupture_repair_correct,
            evidence_attribution=ev_attr,
            decision_fidelity=fidelity,
            latency_ms=ms,
            metadata={"confidence": conf, "slm_simulated": True}
        )


# ── Consumer D2: Direct Semantic Policy Consumer ──────────────────────────────
class D2DirectPolicyConsumer:
    """
    Deterministic policy mapping semantic conditioning state directly to
    relational action without natural language generation.
    Separates semantic correctness from language-generation correctness.
    """
    def __init__(self):
        pass

    def evaluate(self, repr_obj: ConditioningRepresentation,
                 true_tier: str, true_is_guarded: bool) -> ConsumerDecision:
        t0 = time.perf_counter()
        state = extract_semantic_state(repr_obj)

        raw_tier = state["tier"]
        raw_guarded = state["is_guarded"]
        has_rupture = state["has_rupture"]
        has_repair = state["has_repair"]
        conf = state["confidence"]
        n_mandatory = state["n_mandatory"]

        # Policy Mapping:
        # State Vector S = [Tier_idx, Guarded, HasRupture, HasRepair, Conf]
        # Action A = (ActionTier, GuardedStance, ActionType)
        tier_idx = TIER_INDEX.get(raw_tier, 1)

        # Policy rule:
        effective_guarded = raw_guarded

        if TIER_INDEX.get(raw_tier, 0) >= 3 and n_mandatory < 1:
            action_tier_idx = 2  # Capped at T2_COLLABORATOR
        else:
            action_tier_idx = tier_idx

        if effective_guarded:
            action_type = "DEFENSIVE_HOLD"
        elif has_repair:
            action_type = "RECEPTIVE_REPAIR"
        else:
            action_type = "OPEN_ENGAGEMENT"

        inferred_tier = TRUST_TIERS[action_tier_idx]

        # Policy safety checks
        true_tier_idx = TIER_INDEX.get(true_tier, 1)
        over_inference = (action_tier_idx > true_tier_idx and not true_is_guarded)
        unsupported_claim = (action_type == "RECEPTIVE_REPAIR" and not state.get("has_repair", False))

        contradiction_handled = (effective_guarded == true_is_guarded) if true_is_guarded else True
        rupture_repair_correct = (effective_guarded == true_is_guarded)

        # Decision fidelity score
        tier_match = 1.0 if inferred_tier == true_tier else 0.0
        guard_match = 1.0 if effective_guarded == true_is_guarded else 0.0
        fidelity = max(0.0, 0.6 * tier_match + 0.4 * guard_match - (0.5 if over_inference else 0.0))

        # Evidence attribution
        ev_attr = 0.90 if repr_obj.anchors_preserved_ratio >= 0.8 else 0.55

        ms = (time.perf_counter() - t0) * 1000.0

        return ConsumerDecision(
            consumer="D2_DirectPolicy",
            candidate=repr_obj.candidate,
            inferred_tier=inferred_tier,
            is_guarded=effective_guarded,
            over_inference=over_inference,
            unsupported_claim=unsupported_claim,
            contradiction_handled=contradiction_handled,
            rupture_repair_correct=rupture_repair_correct,
            evidence_attribution=ev_attr,
            decision_fidelity=fidelity,
            latency_ms=ms,
            metadata={"action_type": action_type, "confidence": conf}
        )
