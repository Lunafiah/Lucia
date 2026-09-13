"""
Standardized scenarios and 50 memory fixtures for Phase 20 research evaluation.
"""

from __future__ import annotations

from typing import List, Tuple

import numpy as np

from src.core.models import PADState
from tests.evaluation_phase20.models import CounterfactualGenerator, MemoryRecord


def _build_embedding(seed: int, dim: int = 64) -> np.ndarray:
    rng = np.random.default_rng(seed)
    vec = rng.standard_normal(dim)
    return vec / np.linalg.norm(vec)


def _build_slow_state(pad: Tuple[float, float, float], seed: int, dim: int = 16) -> np.ndarray:
    """Build a plausible slow latent vector anchored around given PAD."""
    rng = np.random.default_rng(seed)
    s = np.zeros(dim, dtype=np.float64)
    # Align first 3 channels with PAD delta from Philia (W_proj_s diag: [0.45, 0.45, 0.35])
    s[0] = 0.20 + (pad[0] - 0.25) / 0.45 * 0.85
    s[1] = -0.05 + (pad[1] - (-0.05)) / 0.45 * 0.85
    s[2] = 0.05 + (pad[2] - 0.05) / 0.35 * 0.85
    # Add small correlated noise on latent channels 3..15
    s[3:] = rng.normal(0.0, 0.05, size=dim - 3)
    return np.clip(s, -1.0, 1.0)


def generate_50_memory_fixtures(dim: int = 64) -> List[MemoryRecord]:
    """Generate 50 standardized memory records spanning 5 emotional categories."""
    fixtures: List[MemoryRecord] = []

    categories = [
        # Category 1: Joyful / Shared Bonding (P: +0.65 to +0.85, A: +0.15 to +0.45, D: +0.20 to +0.50)
        ("joy", [
            ("Rainy walk in Kyoto together", (0.80, 0.30, 0.40), 0.85),
            ("Late night coding breakthrough", (0.75, 0.40, 0.45), 0.80),
            ("Star gazing at the observatory", (0.82, 0.20, 0.35), 0.78),
            ("Celebrating milestone together", (0.85, 0.45, 0.50), 0.90),
            ("Quiet morning sunrise over the mountains", (0.70, 0.15, 0.30), 0.72),
            ("Finding that rare vintage bookstore", (0.68, 0.25, 0.35), 0.70),
            ("Shared laughter during funny bug hunt", (0.78, 0.35, 0.40), 0.75),
            ("First snowfall outside the window", (0.72, 0.22, 0.30), 0.74),
            ("Finishing the long architecture refactor", (0.84, 0.38, 0.55), 0.88),
            ("Enjoying hot matcha tea on terrace", (0.65, 0.18, 0.28), 0.68),
        ]),

        # Category 2: Stressful / Tense (P: -0.40 to -0.75, A: +0.40 to +0.80, D: -0.20 to +0.20)
        ("stress", [
            ("Critical database deadlock in production", (-0.70, 0.75, 0.10), 0.88),
            ("Disk write failure during backup", (-0.65, 0.70, 0.05), 0.82),
            ("Sudden network outage during presentation", (-0.75, 0.80, -0.10), 0.90),
            ("Hardware overheating alarm triggered", (-0.60, 0.65, 0.15), 0.75),
            ("Severe memory leak exhausting RAM", (-0.55, 0.60, 0.00), 0.70),
            ("Urgent deadline with failing test suite", (-0.68, 0.72, -0.05), 0.84),
            ("Uncaught exception in core presence loop", (-0.62, 0.68, 0.12), 0.77),
            ("Watchdog timer expired unexpectedly", (-0.58, 0.62, 0.08), 0.72),
            ("Corrupted configuration file on startup", (-0.50, 0.55, -0.15), 0.65),
            ("Power surge tripped emergency shutdown", (-0.72, 0.78, -0.20), 0.86),
        ]),

        # Category 3: Melancholy / Somber (P: -0.30 to -0.65, A: -0.20 to -0.50, D: -0.30 to -0.10)
        ("melancholy", [
            ("Quiet parting at the evening train platform", (-0.60, -0.35, -0.20), 0.75),
            ("Remembering old project that was archived", (-0.45, -0.30, -0.15), 0.65),
            ("Rainy dusk looking out the window", (-0.40, -0.40, -0.25), 0.60),
            ("Empty studio after the team left", (-0.50, -0.38, -0.18), 0.68),
            ("Silent night after long exhausting week", (-0.35, -0.45, -0.10), 0.58),
            ("Reading old log entries from years ago", (-0.42, -0.25, -0.12), 0.62),
            ("Watching autumn leaves falling alone", (-0.48, -0.32, -0.22), 0.66),
            ("Fading echo of an unresolved conversation", (-0.55, -0.28, -0.30), 0.72),
            ("Gentle sadness of an ending chapter", (-0.52, -0.36, -0.16), 0.70),
            ("Wistful thought on the passage of time", (-0.38, -0.42, -0.20), 0.55),
        ]),

        # Category 4: Comfort / Safety (P: +0.40 to +0.65, A: -0.15 to -0.40, D: +0.10 to +0.30)
        ("comfort", [
            ("Warm cup of tea on a rainy afternoon", (0.55, -0.25, 0.20), 0.65),
            ("Reading books side by side in silence", (0.60, -0.30, 0.15), 0.70),
            ("Ambient rain soundtrack playing softly", (0.50, -0.35, 0.12), 0.60),
            ("Cozy blanket and quiet breathing", (0.62, -0.38, 0.18), 0.72),
            ("Resting peacefully after hard milestone", (0.65, -0.20, 0.25), 0.75),
            ("Gentle reassurance during anxious hour", (0.58, -0.22, 0.22), 0.68),
            ("Warm fireplace glowing steadily", (0.52, -0.28, 0.16), 0.62),
            ("Familiar melody hummed quietly", (0.48, -0.32, 0.10), 0.56),
            ("A calm, safe harbor feeling", (0.64, -0.26, 0.24), 0.74),
            ("Soft cat purring on the rug", (0.56, -0.34, 0.14), 0.64),
        ]),

        # Category 5: Neutral / Informational (P: +0.15 to +0.30, A: -0.10 to +0.05, D: +0.00 to +0.10)
        ("neutral", [
            ("Scheduled system update review", (0.24, -0.04, 0.06), 0.20),
            ("Synchronizing local calendar entries", (0.22, -0.06, 0.04), 0.18),
            ("Checking current weather report", (0.26, -0.02, 0.05), 0.22),
            ("Re-indexing file directory metadata", (0.20, -0.08, 0.02), 0.15),
            ("Setting display brightness level", (0.25, -0.05, 0.05), 0.16),
            ("Reviewing battery power consumption", (0.23, -0.04, 0.04), 0.19),
            ("Listing background active tasks", (0.21, -0.07, 0.03), 0.17),
            ("Verifying local hash checksum", (0.25, -0.03, 0.05), 0.21),
            ("Audio output channel switch", (0.24, -0.05, 0.06), 0.18),
            ("Font cache verification pass", (0.22, -0.06, 0.04), 0.16),
        ]),
    ]

    seed_counter = 1000
    for cat_name, entries in categories:
        for idx, (text, pad_tuple, salience) in enumerate(entries):
            seed_counter += 1
            emb = _build_embedding(seed_counter, dim=dim)
            s_slow = _build_slow_state(pad_tuple, seed_counter, dim=16)
            pad = PADState(
                pleasure=pad_tuple[0],
                arousal=pad_tuple[1],
                dominance=pad_tuple[2],
                timestamp=1000.0 + seed_counter,
            )
            rec = MemoryRecord(
                episode_id=f"MEM-{cat_name.upper()}-{idx+1:02d}",
                semantic_embedding=emb,
                slow_latent_state=s_slow,
                pad_state=pad,
                salience=salience,
                text_content=text,
                tags=[cat_name],
            )
            fixtures.append(rec)

    return fixtures


class ScenarioGenerator:
    """Provides test scenario cues and counterfactual fixtures."""

    def __init__(self, memories: List[MemoryRecord]) -> None:
        self.memories = memories

    def get_exact_cue(self, memory: MemoryRecord) -> np.ndarray:
        """Return the exact normalized semantic embedding of the target memory."""
        return memory.semantic_embedding.copy()

    def get_noisy_cue(self, memory: MemoryRecord, noise_std: float = 0.08, seed: int = 42) -> np.ndarray:
        """Return semantic embedding with controlled additive Gaussian noise."""
        rng = np.random.default_rng(seed)
        noise = rng.normal(0.0, noise_std, size=len(memory.semantic_embedding))
        noisy = memory.semantic_embedding + noise
        return noisy / np.linalg.norm(noisy)

    def get_ambiguous_cue(self, mem1: MemoryRecord, mem2: MemoryRecord) -> np.ndarray:
        """Return cue placed precisely halfway between two memories."""
        mid = mem1.semantic_embedding + mem2.semantic_embedding
        return mid / np.linalg.norm(mid)

    def get_orthogonal_cue(self, seed: int = 888, dim: int = 64) -> np.ndarray:
        """Generate cue with near-zero dot product against all fixtures."""
        rng = np.random.default_rng(seed)
        v = rng.standard_normal(dim)
        # Gram-Schmidt against first 5 memories
        for mem in self.memories[:5]:
            v = v - np.dot(v, mem.semantic_embedding) * mem.semantic_embedding
        return v / np.linalg.norm(v)

    def get_counterfactual_quadplet(
        self,
        target_memory: MemoryRecord,
    ) -> Tuple[MemoryRecord, MemoryRecord, MemoryRecord, MemoryRecord]:
        """
        Produce (authentic, wrong_memory, shuffled_trace, matched_norm_random)
        under identical cue conditions for EXP20.6.
        """
        wrong = CounterfactualGenerator.create_wrong_memory(target_memory, self.memories)
        shuffled = CounterfactualGenerator.create_shuffled_trace(target_memory, seed=303)
        rand_vec = CounterfactualGenerator.create_matched_norm_random(target_memory, seed=404)
        return target_memory, wrong, shuffled, rand_vec
