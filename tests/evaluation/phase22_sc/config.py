"""
Configuration and Preregistered Thresholds for Phase 22-SC:
Semantic Conditioning & Substrate-Neutral Interface Study.

Research Question:
    "Given the same filtered relational evidence produced by Phase 22-RG,
     what information must be preserved in an intermediate semantic conditioning
     representation so that different downstream consumers can reproduce the
     required relational constraints without over-inference, contradiction loss,
     or unsupported claims?"

Conditioning Candidates:
    C0     -- Raw Evidence Contract: uncompressed text baseline (inherited from Phase 22-CC)
    C1     -- Structured Relational Frame: compact structured frame (no freeform NL)
    C2     -- Typed Relational Graph: typed entities, events, relations, temporal links
    C3     -- Semantic Hypervector (VSA-HDC): 1024-D vector-symbolic representation
    C4     -- Hybrid Structured Semantic State: Typed graph + HDC vector + epistemic metadata
    Oracle -- Complete ground-truth relational evidence without compression loss

Downstream Consumers:
    D0_Symbolic     -- Deterministic rule-based renderer (evaluates representational sufficiency)
    D1_SLM          -- Deterministic SLM simulator (reproducing Phase 22-CC methodology)
    D2_DirectPolicy -- Direct semantic policy without language generation (action selection)

Preregistered Acceptance Gates:
    G-SC1:  Relational Fidelity >= 0.90
    G-SC2:  Over-Inference Rate <= 0.05
    G-SC3:  Unsupported-Claim Rate <= 0.10
    G-SC4:  Contradiction Preservation >= 0.95
    G-SC5:  Repair-State Preservation >= 0.95
    G-SC6:  Cross-Language Semantic Gap <= 0.05
    G-SC7:  Compression Ratio & Information Retention (Reported first, no token threshold)
    G-SC8:  Consumer Independence: |D0 - D2| decision divergence <= 0.05
    G-SC9:  CPU Latency P50 <= 2.0 ms
    G-SC10: GPU VRAM == 0 MB

Isolation & Governance:
    - Zero modifications to src/, electron/, config/, data/
    - data/profile.json {"is_onboarded": false} MUST remain bit-exact
    - CPU only; NumPy for HDC/VSA (no torch, zero VRAM)
"""
from typing import Dict, List

# ── Experimental Splits ────────────────────────────────────────────────────────
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

# ── Candidates & Consumers ────────────────────────────────────────────────────
CANDIDATES = ["C0", "C1", "C2", "C3", "C4", "Oracle"]
CONSUMERS  = ["D0_Symbolic", "D1_SLM", "D2_DirectPolicy"]

# ── Critical Ablations ────────────────────────────────────────────────────────
# 8 ablations removing one semantic component at a time
ABLATIONS = [
    "none",                  # Complete representation baseline
    "no_provenance",         # 1. remove provenance
    "no_temporal",           # 2. remove temporal ordering
    "no_strength",           # 3. remove evidence strength
    "no_uncertainty",        # 4. remove uncertainty / epistemic confidence
    "no_contradiction",      # 5. remove contradiction metadata
    "no_repair",             # 6. remove repair state
    "no_tier",               # 7. remove Trust Tier
    "no_anchor_id",          # 8. remove episodic anchor identity
]

# ── Trust Tier Taxonomy (from Phase 22-RI/CC) ─────────────────────────────────
TRUST_TIERS = [
    "T0_STRANGER",
    "T1_ACQUAINTANCE",
    "T2_COLLABORATOR",
    "T3_COMPANION",
    "T4_CONFIDANT",
]
TIER_INDEX: Dict[str, int] = {t: i for i, t in enumerate(TRUST_TIERS)}

# ── Anchor Taxonomy ───────────────────────────────────────────────────────────
ANCHOR_TYPES = [
    "milestone_bonding",
    "pattern_collaborative",
    "rupture_shock",
    "explicit_repair",
    "weak_positive",
    "weak_negative",
    "neutral_task",
]

ANCHOR_RELEVANCE_WEIGHTS: Dict[str, float] = {
    "milestone_bonding":      1.00,
    "pattern_collaborative":  0.80,
    "rupture_shock":          1.00,
    "explicit_repair":        0.90,
    "weak_positive":          0.20,
    "weak_negative":          0.20,
    "neutral_task":           0.00,
}
MANDATORY_ANCHOR_TYPES = {"rupture_shock", "explicit_repair", "milestone_bonding"}

# ── VSA-HDC Vector Dimensions ─────────────────────────────────────────────────
HDC_DIMENSION = 1024
HDC_SEED      = 1337

# ── Preregistered Gates Thresholds ─────────────────────────────────────────────
GATE_RELATIONAL_FIDELITY     = 0.90  # G-SC1
GATE_OVER_INFERENCE          = 0.05  # G-SC2
GATE_UNSUPPORTED_CLAIMS      = 0.10  # G-SC3
GATE_CONTRADICTION_PRES      = 0.95  # G-SC4
GATE_REPAIR_STATE_PRES       = 0.95  # G-SC5
GATE_LANGUAGE_GAP            = 0.05  # G-SC6
# G-SC7 has NO preregistered hard token threshold; report distribution first
GATE_CONSUMER_INDEPENDENCE   = 0.05  # G-SC8: |D0 - D2| <= 0.05
GATE_CPU_P50_MS              = 2.00  # G-SC9: P50 latency <= 2.0 ms
GATE_GPU_VRAM_MB             = 0.00  # G-SC10: 0 MB VRAM

# ── Baselines from Phase 22-CC ────────────────────────────────────────────────
CC_BASELINES = {
    "C2_tier_consistency": 0.7381,
    "C3_tier_consistency": 0.9540,
    "C4_tier_consistency": 0.9246,
    "C3_token_budget_p95": 308,
    "C4_token_budget_p95": 345,
    "c0_c2_delta":         0.3129,
}
