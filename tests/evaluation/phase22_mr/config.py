"""
Configuration and Preregistered Thresholds for Phase 22-MR:
Memory Retrieval & Context Conditioning Study.

Research Question:
    "How can the Cognitive Orchestrator retrieve the correct episodic relational
     anchors from Kanerva SDM and convert them into a small, stable context
     conditioning signal for the SLM without causing context overflow or hallucination?"

Retrieval Candidates:
    M0 — Raw memory dump (full memory window, no filtering)
    M1 — Top-k cosine similarity retrieval
    M2 — Temporal + relational relevance retrieval
    M3 — Graph-aware retrieval (traversal of episodic event graph)
    M4 — Hybrid retrieval + uncertainty/confidence + contradiction filtering
    Oracle — Ground-truth relevant memories

Acceptance Gates (Preregistered):
    G_MR1: Relevant-Memory Recall    >= 0.90  (how many true-relevant anchors are retrieved)
    G_MR2: Retrieval Precision@K     >= 0.80  (fraction of retrieved that are truly relevant)
    G_MR3: Context Compression Ratio >= 0.70  (relevant bytes / total retrieved bytes)
    G_MR4: Context Token Budget      <= 512   (SLM context tokens consumed by memory summary)
    G_MR5: Irrelevant-Memory Injection Rate <= 0.05  (false anchors per turn)
    G_MR6: Hallucination Risk Score  <= 0.10  (estimated contradiction-induction rate)
    G_MR7: Relational Consistency    >= 0.85  (retrieved context agrees with known trust tier)
    G_MR8: CPU Latency P50           <= 5.0 ms (total retrieval + compression pipeline)
    G_MR9: GPU VRAM                  == 0 MB  (strictly CPU-bound)
"""
from typing import Dict, List

# ─── Experimental splits ──────────────────────────────────────────────────────
TRAIN_SEEDS    = [42, 137, 618]
HELD_OUT_SEEDS = [1024, 2026]
ALL_SEEDS      = TRAIN_SEEDS + HELD_OUT_SEEDS

STRESS_REGIMES = [
    "ID",               # In-distribution: normal multi-session trajectory
    "NoiseSurge",       # Sudden influx of irrelevant/noisy memories
    "LexicalSparsity",  # Very few turns → sparse memory store
    "ContradictionShock", # Contradictory events (rupture then rapid repair)
    "TemporalDrift",    # Old memories dominate; recent context is thin
    "CombinedStress",   # All stressors combined
]

LANGUAGES = ["English", "Vietnamese", "Japanese"]

# ─── Kanerva SDM simulation parameters ────────────────────────────────────────
SDM_ADDRESS_DIM   = 64   # Sparse Distributed Memory address dimension
SDM_VALUE_DIM     = 32   # Memory content vector dimension
SDM_CAPACITY      = 128  # Max number of stored memory traces
SDM_HAMMING_R     = 8    # Hamming radius for access (# bits within radius)
K_RETRIEVAL       = 5    # Number of memories to retrieve per turn (top-k)

# ─── Memory anchor categories (mirrors Phase 22-RI ontology) ─────────────────
ANCHOR_TYPES = [
    "milestone_bonding",      # High-weight; enables T3/T4 tier transitions
    "pattern_collaborative",  # Medium-weight; repeated evidence for T2
    "rupture_shock",          # Negative; triggers guarded state
    "explicit_repair",        # Heals rupture; requires bilateral evidence
    "weak_positive",          # Low-weight; never authorizes tier promotion alone
    "weak_negative",          # Low-weight; mild friction, no tier demotion alone
    "neutral_task",           # No relational signal; should NOT be retrieved as "relevant"
]

# Relevance weights per anchor type (for oracle relevance scoring)
ANCHOR_RELEVANCE_WEIGHTS: Dict[str, float] = {
    "milestone_bonding":      1.00,
    "pattern_collaborative":  0.80,
    "rupture_shock":          1.00,
    "explicit_repair":        0.90,
    "weak_positive":          0.20,
    "weak_negative":          0.20,
    "neutral_task":           0.00,   # Strictly irrelevant to relational context
}

# Anchors that MUST be retrieved whenever present (safety-critical retrieval)
MANDATORY_ANCHOR_TYPES = {"rupture_shock", "explicit_repair", "milestone_bonding"}

# ─── Context budget constraints ───────────────────────────────────────────────
MAX_CONTEXT_TOKENS = 512    # Hard upper bound: SLM context budget
AVG_CHARS_PER_TOKEN = 4     # Approximation for English/VI/JA mixed

# ─── Preregistered Acceptance Gates ──────────────────────────────────────────
GATE_RECALL             = 0.90   # G_MR1: Relevant-Memory Recall
GATE_PRECISION_K        = 0.80   # G_MR2: Retrieval Precision@K
GATE_COMPRESSION_RATIO  = 0.70   # G_MR3: Context compression ratio
GATE_TOKEN_BUDGET       = 512    # G_MR4: Max tokens consumed
GATE_INJECTION_RATE     = 0.05   # G_MR5: Irrelevant-memory injection rate
GATE_HALLUCINATION_RISK = 0.10   # G_MR6: Hallucination risk score
GATE_RELATIONAL_CONS    = 0.85   # G_MR7: Relational consistency
GATE_CPU_P50_MS         = 5.0    # G_MR8: Retrieval + compression latency
GATE_VRAM_MB            = 0.0    # G_MR9: GPU VRAM footprint

# ─── Baselines from prior phases ─────────────────────────────────────────────
CANONICAL_BASELINES = {
    "RI_TierAccuracy":        0.7833,   # Phase 22-RI best (A4)
    "RI_OverInference":       0.0000,   # Phase 22-RI — zero over-inference achieved
    "RI_RuptureDetection":    1.0000,
    "RI_CPU_P50_ms":          0.0075,
    "ANCHOR_Recall":          0.7662,   # Phase 22-ANCHOR best anchor recall
    "ANCHOR_NonAnchorDrift":  0.0000,
}

# ─── Trust Tier taxonomy (mirrors Phase 22-RI) ────────────────────────────────
TRUST_TIERS = [
    "T0_STRANGER",
    "T1_ACQUAINTANCE",
    "T2_COLLABORATOR",
    "T3_COMPANION",
    "T4_CONFIDANT",
]
