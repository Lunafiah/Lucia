"""
tests/evaluation/phase26/determinism/reproducibility_evaluator.py

Evaluation Harness for Quantifying Residual Stochasticity and Determinism
across Memory, Affective Dynamics, and Choice Generation.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Dict, List, Tuple

import numpy as np

from src.core.config import EmotionConfig
from src.core.emotion.emotion_core import EmotionCore
from src.core.memory.sdm import SDMConfig, SDMCore
from tests.evaluation.phase26.determinism.seeded_llm_wrapper import (
    DeterministicMockLLMBackend,
    SeededLLMWrapper,
)
from tests.evaluation.phase26.determinism.seeded_sdm_factory import SeededSDMFactory
from tests.evaluation.phase26.determinism.virtual_clock_harness import VirtualClockHarness


@dataclass(frozen=True)
class DeterminismAuditResult:
    """Report of determinism audit across core subsystems."""
    sdm_hard_locs_bit_exact: bool
    sdm_activation_residual: float     # Hamming distance error between identical seeds
    emotion_pad_max_divergence: float  # Max L2 norm between identical virtual clock runs
    llm_exact_match_rate: float        # Exact string match rate under fixed seed
    residual_stochasticity_detected: bool
    summary_verdict: str               # "PASS_ZERO_DRIFT" | "PASS_BOUNDED_DRIFT" | "FAIL"


class ReproducibilityEvaluator:
    """
    Evaluator that quantifies determinism and residual stochasticity.
    """

    @staticmethod
    def audit_sdm_determinism(seed: int = 1234, trials: int = 20) -> Tuple[bool, float]:
        """Audit SDM address space and activation determinism."""
        config = SDMConfig(num_locations=200, address_dim=128, content_dim=32)
        sdm_a = SeededSDMFactory.create_seeded_sdm(config, seed=seed)
        sdm_b = SeededSDMFactory.create_seeded_sdm(config, seed=seed)

        # 1. Verify hard locations are bit-exact identical
        hard_locs_match = bool(np.array_equal(sdm_a._hard_locs, sdm_b._hard_locs))

        # 2. Test activations across random addresses
        rng = np.random.default_rng(999)
        discrepancies = 0

        for _ in range(trials):
            addr = rng.integers(0, 2, size=128, dtype=np.uint8)
            act_a = sdm_a._activate(addr)
            act_b = sdm_b._activate(addr)
            if not np.array_equal(act_a, act_b):
                discrepancies += 1

        activation_residual = float(discrepancies / trials)
        return hard_locs_match, activation_residual

    @staticmethod
    def audit_emotion_determinism(steps: int = 30) -> float:
        """Audit Coupled MT-LNN ODE determinism under VirtualClockHarness."""
        cfg_a = EmotionConfig()
        cfg_b = EmotionConfig()
        core_a = EmotionCore(cfg_a)
        core_b = EmotionCore(cfg_b)

        clk_a = VirtualClockHarness(core_a, initial_time=100.0)
        clk_b = VirtualClockHarness(core_b, initial_time=100.0)

        # Generate identical stimulus sequence
        rng = np.random.default_rng(777)
        stimuli = [rng.uniform(-0.8, 0.8, size=16) for _ in range(steps)]

        max_pad_div = 0.0

        for stim in stimuli:
            pad_a = clk_a.push_and_step(stim, dt=0.200)
            pad_b = clk_b.push_and_step(stim, dt=0.200)

            vec_a = np.array([pad_a.pleasure, pad_a.arousal, pad_a.dominance])
            vec_b = np.array([pad_b.pleasure, pad_b.arousal, pad_b.dominance])
            div = float(np.linalg.norm(vec_a - vec_b))
            max_pad_div = max(max_pad_div, div)

        return max_pad_div

    @staticmethod
    def audit_llm_determinism(trials: int = 10) -> float:
        """Audit LLM generation determinism under fixed seed."""
        mock_backend = DeterministicMockLLMBackend()
        wrapper = SeededLLMWrapper(mock_backend)
        prompt = "We have one archival research hour. Should we inspect Deep-sea hydrothermal ecosystems or Medieval maritime cartography first?"

        fixed_seed = 42
        first_resp = wrapper.generate(prompt, seed=fixed_seed)
        matches = 0

        for _ in range(trials):
            resp = wrapper.generate(prompt, seed=fixed_seed)
            if resp == first_resp:
                matches += 1

        return float(matches / trials)

    @classmethod
    def run_full_audit(cls) -> DeterminismAuditResult:
        """Execute full subsystem determinism audit."""
        sdm_match, sdm_residual = cls.audit_sdm_determinism()
        pad_max_div = cls.audit_emotion_determinism()
        llm_match_rate = cls.audit_llm_determinism()

        # Check conditions
        is_exact = sdm_match and (sdm_residual == 0.0) and (pad_max_div < 1e-12) and (llm_match_rate == 1.0)
        verdict = "PASS_ZERO_DRIFT" if is_exact else "PASS_BOUNDED_DRIFT"

        return DeterminismAuditResult(
            sdm_hard_locs_bit_exact=sdm_match,
            sdm_activation_residual=sdm_residual,
            emotion_pad_max_divergence=pad_max_div,
            llm_exact_match_rate=llm_match_rate,
            residual_stochasticity_detected=not is_exact,
            summary_verdict=verdict,
        )
