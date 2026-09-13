"""
Data models and counterfactual generators for Phase 20 Affective Recollection research.
"""

from __future__ import annotations

import time
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional, Tuple

import numpy as np

from src.core.models import PADState


@dataclass
class MemoryRecord:
    """
    Affective memory record M_k = <e_k, s_enc_k, p_enc_k, sigma_k, t_enc_k>.
    
    Contains semantic representation, MT-LNN slow latent snapshot,
    PAD coordinate at encoding, salience, and timestamp.
    """
    episode_id: str
    semantic_embedding: np.ndarray  # R^{D_e}, normalized ||e||_2 = 1.0
    slow_latent_state: np.ndarray   # R^{16}, snapshot of s_slow
    pad_state: PADState             # Committed PAD at encoding
    salience: float                 # sigma in [0, 1]
    timestamp: float = field(default_factory=time.monotonic)
    text_content: str = ""
    tags: List[str] = field(default_factory=list)

    def __post_init__(self) -> None:
        # Ensure semantic embedding is normalized
        norm = np.linalg.norm(self.semantic_embedding)
        if norm > 1e-12:
            self.semantic_embedding = self.semantic_embedding / norm
        else:
            self.semantic_embedding = np.zeros_like(self.semantic_embedding)


class CounterfactualGenerator:
    """
    Generates controlled counterfactual transformations of authentic memory records.
    
    Directly addresses Phase 11's core vector-dependence vulnerability by providing:
      1. Wrong-memory trace: authentic memory from a completely orthogonal episode.
      2. Shuffled latent trace: permuted dimensions of s_enc (matched norm & component distribution,
         destroyed dimension-specific identity).
      3. Matched-norm random Gaussian vector: random vector with exactly matched L2 norm.
    """

    @staticmethod
    def create_wrong_memory(target: MemoryRecord, store: List[MemoryRecord]) -> MemoryRecord:
        """Find the memory in the store that has the lowest semantic similarity to target."""
        best_candidate = None
        min_sim = float("inf")
        for mem in store:
            if mem.episode_id == target.episode_id:
                continue
            sim = float(np.dot(target.semantic_embedding, mem.semantic_embedding))
            if sim < min_sim:
                min_sim = sim
                best_candidate = mem
        if best_candidate is None:
            raise ValueError("Memory store must contain at least 2 records to select wrong memory.")
        return best_candidate

    @staticmethod
    def create_shuffled_trace(target: MemoryRecord, seed: int = 101) -> MemoryRecord:
        """Permute slow latent dimensions, preserving exact component values and norm."""
        rng = np.random.default_rng(seed)
        shuffled_s = target.slow_latent_state.copy()
        rng.shuffle(shuffled_s)
        # Ensure it is not accidentally identical to the original
        if np.allclose(shuffled_s, target.slow_latent_state):
            shuffled_s = np.roll(shuffled_s, 1)

        return MemoryRecord(
            episode_id=f"{target.episode_id}_shuffled",
            semantic_embedding=target.semantic_embedding.copy(),
            slow_latent_state=shuffled_s,
            pad_state=target.pad_state,
            salience=target.salience,
            timestamp=target.timestamp,
            text_content=f"[SHUFFLED] {target.text_content}",
            tags=target.tags + ["counterfactual_shuffled"],
        )

    @staticmethod
    def create_matched_norm_random(target: MemoryRecord, seed: int = 202) -> MemoryRecord:
        """Generate random Gaussian vector scaled to match ||s_enc - s*_philia||_2."""
        rng = np.random.default_rng(seed)
        target_norm = float(np.linalg.norm(target.slow_latent_state))
        
        # Sample standard normal
        rand_v = rng.standard_normal(len(target.slow_latent_state))
        rand_norm = float(np.linalg.norm(rand_v))
        if rand_norm > 1e-12:
            scaled_v = rand_v * (target_norm / rand_norm)
        else:
            scaled_v = np.zeros_like(rand_v)

        return MemoryRecord(
            episode_id=f"{target.episode_id}_random",
            semantic_embedding=target.semantic_embedding.copy(),
            slow_latent_state=scaled_v,
            pad_state=target.pad_state,
            salience=target.salience,
            timestamp=target.timestamp,
            text_content=f"[RANDOM_VECTOR] {target.text_content}",
            tags=target.tags + ["counterfactual_random"],
        )


@dataclass
class RecollectionTelemetry:
    """Human-interpretable telemetry record for each recollection event."""
    cue_text: str
    retrieved_id: str
    semantic_score: float
    ecphoric_score: float
    composite_affinity: float
    gating_passed: bool
    activation_weight: float
    r_slow_norm: float
    dominant_channel: Tuple[int, float]
    initial_pad: Tuple[float, float, float]
    peak_pad: Tuple[float, float, float]
    delta_pad_auc: float
    somatic_latency_ms: float
    communication_mode: str
    half_life_s: float
    restoration_error: float

    def format_trace(self) -> str:
        """Format as human-interpretable trace block matching Section 12."""
        return (
            "[PHASE 20 RECOLLECTION TRACE]\n"
            f"├─ Cue Input:           \"{self.cue_text}\"\n"
            f"├─ Retrieved Trace:     Episode_ID={self.retrieved_id} (Affinity={self.composite_affinity:.4f}, Passed={self.gating_passed})\n"
            f"├─ Affinity Score:      Semantic={self.semantic_score:.4f}, Ecphoric={self.ecphoric_score:.4f}, Composite={self.composite_affinity:.4f}\n"
            f"├─ Slow Perturbation:   ||r_slow|| = {self.r_slow_norm:.4f} (Channel s[{self.dominant_channel[0]}]={self.dominant_channel[1]:+.4f})\n"
            f"├─ Trajectory Impact:   Pleasure: {self.initial_pad[0]:.3f} -> {self.peak_pad[0]:.3f}, Arousal: {self.initial_pad[1]:.3f} -> {self.peak_pad[1]:.3f} (Delta_AUC = {self.delta_pad_auc:.4f})\n"
            f"├─ Downstream Pacing:   Somatic Latency +{self.somatic_latency_ms:.1f}ms, Comm Mode: {self.communication_mode}\n"
            f"└─ Attractor Return:    Unforced idle relaxation t_half = {self.half_life_s:.1f}s -> Philia error: {self.restoration_error:.6f}"
        )
