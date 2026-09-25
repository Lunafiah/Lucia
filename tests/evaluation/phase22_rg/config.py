"""
Configuration and Preregistered Thresholds for Phase 22-RG:
Relevance Gating & Evidence Selection Study.

Research Question:
    "Can a post-retrieval Relevance Gate reduce irrelevant-memory injection
     (from 40% to <= 5%) while preserving mandatory anchor recall (>= 99%),
     zero hallucination risk, and relational consistency?"

Gate Candidates (applied AFTER M4 HybridFull retrieval):
    G0 — No gate (M4 baseline pass-through)
    G1 — Static relevance threshold gate
    G2 — Evidence-strength gating (anchor type classification)
    G3 — Confidence + temporal decay gating
    G4 — Safety-first hybrid gate (the proposed architecture)
    Oracle — Perfect ground-truth filter

Preregistered Acceptance Gates:
    G_RG1: Mandatory Anchor Recall     >= 0.99  (safety-critical: rupture/repair/milestone)
    G_RG2: Precision@K                 >= 0.80  (was 0.3159 in Phase 22-MR -- primary target)
    G_RG3: Injection Rate              <= 0.05  (was 0.3999 in Phase 22-MR -- primary target)
    G_RG4: Hallucination Risk          <= 0.10  (must not degrade from 0.0000 baseline)
    G_RG5: Overall Recall              >= 0.85  (cannot sacrifice too much recall for precision)
    G_RG6: Relational Consistency      >= 0.85  (must not degrade from 0.9918 baseline)
    G_RG7: Context Compression Ratio   >= 0.70  (was 0.4115 -- primary target)
    G_RG8: Contradiction Preservation  >= 1.00  (rupture/repair pairs always preserved together)
    G_RG9: Language Invariance Max Gap <= 0.05  (max metric spread EN/VI/JA)
    G_RG10: CPU Latency P50            <= 2.0 ms (stricter than MR: gating must be ultra-light)
    G_RG11: GPU VRAM                   == 0 MB
    G_RG12: Token Budget Post-Gate     <= 300   (tighter budget: gate should compress context)

Baselines from Phase 22-MR (M4 HybridFull, Held-Out Seeds):
    Recall        = 1.0000
    Precision     = 0.3159
    Mandatory Rec = 1.0000
    Injection     = 0.3999
    Hall. Risk    = 0.0000
    Rel. Cons     = 0.9918
    Latency P50   = 0.3548 ms
    Token P95     = 472
    Compression   = 0.4115
"""
from typing import Dict, List

# ── Experimental splits ───────────────────────────────────────────────────────
TRAIN_SEEDS    = [42, 137, 618]
HELD_OUT_SEEDS = [1024, 2026]
ALL_SEEDS      = TRAIN_SEEDS + HELD_OUT_SEEDS

STRESS_REGIMES = [
    "ID",
    "NoiseSurge",
    "LexicalSparsity",
    "ContradictionShock",
    "TemporalDrift",
    "CombinedStress",
]

LANGUAGES = ["English", "Vietnamese", "Japanese"]

# ── Anchor taxonomy (inherited from MR) ──────────────────────────────────────
ANCHOR_TYPES = [
    "milestone_bonding",
    "pattern_collaborative",
    "rupture_shock",
    "explicit_repair",
    "weak_positive",
    "weak_negative",
    "neutral_task",
]

# Oracle ground-truth relevance weights (from Phase 22-MR config)
ANCHOR_RELEVANCE_WEIGHTS: Dict[str, float] = {
    "milestone_bonding":      1.00,
    "pattern_collaborative":  0.80,
    "rupture_shock":          1.00,
    "explicit_repair":        0.90,
    "weak_positive":          0.20,
    "weak_negative":          0.20,
    "neutral_task":           0.00,
}

# Safety-critical anchors that MUST survive any gate
MANDATORY_ANCHOR_TYPES = {"rupture_shock", "explicit_repair", "milestone_bonding"}

# ── Preregistered Acceptance Gates ────────────────────────────────────────────
GATE_MANDATORY_RECALL    = 0.99   # G_RG1: Rupture/repair/milestone never dropped
GATE_PRECISION_K         = 0.80   # G_RG2: Main precision target
GATE_INJECTION_RATE      = 0.05   # G_RG3: Main injection rate target
GATE_HALLUCINATION_RISK  = 0.10   # G_RG4: Must not worsen vs MR baseline 0.00
GATE_OVERALL_RECALL      = 0.85   # G_RG5: Some recall sacrifice is acceptable
GATE_RELATIONAL_CONS     = 0.85   # G_RG6: Must not degrade from 0.9918
GATE_COMPRESSION         = 0.70   # G_RG7: Context compression target
GATE_CONTRADICTION_PRES  = 1.00   # G_RG8: Rupture+repair pairs preserved together
GATE_LANGUAGE_GAP        = 0.05   # G_RG9: Max spread across EN/VI/JA
GATE_CPU_P50_MS          = 2.0    # G_RG10: Gating overhead SLA
GATE_VRAM_MB             = 0.0    # G_RG11: CPU-only
GATE_TOKEN_POST_GATE     = 300    # G_RG12: Post-gate context token budget

# ── Phase 22-MR baselines (must not regress below) ───────────────────────────
MR_BASELINES = {
    "recall":             1.0000,
    "precision":          0.3159,
    "mandatory_recall":   1.0000,
    "injection_rate":     0.3999,
    "hallucination_risk": 0.0000,
    "relational_cons":    0.9918,
    "latency_ms_p50":     0.3548,
    "token_p95":          472.0,
    "compression":        0.4115,
}

# ── Evidence Contract parameters ──────────────────────────────────────────────
# Minimum evidence that constitutes "sufficient context" for SLM conditioning
EVIDENCE_CONTRACT = {
    "min_mandatory_traces": 0,      # All present mandatory traces must appear
    "min_pattern_traces":   0,      # At least 0 pattern traces (may have none)
    "max_weak_signal_ratio": 0.10,  # At most 10% of context may be weak signals
    "require_tier_coherence": True, # Context must not contradict current tier
}

# SDM simulation parameters (matches MR harness exactly for reproducibility)
SDM_ADDRESS_DIM  = 64
SDM_VALUE_DIM    = 32
SDM_CAPACITY     = 128
SDM_HAMMING_R    = 8
K_RETRIEVAL      = 5
AVG_CHARS_PER_TOKEN = 4
