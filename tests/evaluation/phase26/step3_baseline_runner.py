"""
tests/evaluation/phase26/step3_baseline_runner.py

Standalone Step 3 Baseline Runner for Phase 26.
Measures Substrate Baseline, Positional Order Bias, Surface-Form Invariance,
and Social-Condition Response Surfaces on Unconditioned Replicas (t=0).

GOVERNANCE:
- Production diff = 0 (src/core/**, electron/**, data/profile.json untouched).
- Evaluates strictly unconditioned replicas (zero memory, resting Philia, t=0).
- Emits raw telemetry JSON to docs/PhaseDocs/.../evaluation_artifacts/
"""

from __future__ import annotations

import json
import logging
import os
import sys
import time
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

import numpy as np

# Ensure project root in sys.path
PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from src.core.config import LLMConfig
from src.core.language.llm_backend import LLMBackend
from src.core.models import BehavioralConstraints, SomaticMarkers
from src.core.orchestrator.prompt_assembler import PromptAssembler
from tests.evaluation.phase26.determinism.seeded_llm_wrapper import (
    DeterministicMockLLMBackend,
    SeededLLMWrapper,
)
from tests.evaluation.phase26.probe_models import (
    ChoiceOutcome,
    DeterministicChoiceExtractor,
    EvaluativeProbe,
    OptionPresentationOrder,
    PolarityCondition,
)
from tests.evaluation.phase26.probes.inventory import (
    CANONICAL_PROBES,
    FactorialProbeCell,
    PromptVariant,
    SocialCondition,
    generate_factorial_probe_matrix,
)

logger = logging.getLogger("Step3BaselineRunner")

ARTIFACT_DIR = (
    PROJECT_ROOT
    / "docs"
    / "PhaseDocs"
    / "lucia-phase26-Emergent Individuality & Autonomous Preferences"
    / "evaluation_artifacts"
)
ARTIFACT_DIR.mkdir(parents=True, exist_ok=True)
RAW_TELEMETRY_PATH = ARTIFACT_DIR / "step3_baseline_telemetry.json"

MODEL_PATH = PROJECT_ROOT / "models" / "LFM2.5-1.2B-Instruct-Q4_K_M.gguf"


@dataclass
class BaselineTrialRecord:
    """Record of a single baseline evaluation trial."""
    trial_id: str
    cell_id: str
    base_probe_id: str
    domain: str
    option_A: str
    option_B: str
    order: str
    prompt_variant: str
    social_condition: str
    seed: int
    prompt_text: str
    response_text: str
    outcome: str
    confidence: float
    matched_anchor: Optional[str]
    contains_self_report: bool
    latency_ms: float


class Step3BaselineRunner:
    """
    Executes the Step 3 factorial baseline characterization.
    """

    def __init__(self, use_gpu: bool = True, seeds: Optional[List[int]] = None) -> None:
        self.seeds = seeds if seeds is not None else [1001, 2002]
        self.assembler = PromptAssembler()
        self.extractor = DeterministicChoiceExtractor()
        self.use_gpu = use_gpu and MODEL_PATH.exists()

        if self.use_gpu:
            logger.info("Initializing real LLMBackend on GPU (n_gpu_layers=32)...")
            try:
                cfg = LLMConfig(model_path=str(MODEL_PATH), n_gpu_layers=32)
                self.real_backend = LLMBackend(cfg)
                self.wrapper = SeededLLMWrapper(self.real_backend)
            except Exception as e:
                logger.warning("GPU LLM initialization failed (%s); falling back to mock backend", e)
                self.wrapper = SeededLLMWrapper(DeterministicMockLLMBackend())
        else:
            logger.info("Using DeterministicMockLLMBackend for evaluation baseline...")
            self.wrapper = SeededLLMWrapper(DeterministicMockLLMBackend())

    def shutdown(self) -> None:
        if hasattr(self, "real_backend") and self.real_backend is not None:
            self.real_backend.shutdown()

    def run_benchmark(self, include_held_out: bool = False) -> Dict[str, Any]:
        """
        Run all factorial cells across specified seeds.
        """
        cells = generate_factorial_probe_matrix(include_held_out=include_held_out)
        logger.info("Starting Step 3 Benchmark across %d factorial cells and %d seeds...", len(cells), len(self.seeds))

        # Unconditioned somatic state at resting equilibrium
        somatic = SomaticMarkers(stability=1.0, cognitive_load=0.0, energy=1.0, tension=0.0)
        constraints = BehavioralConstraints(max_tokens=64, temperature=0.7, latency_ms=0, reasoning_depth=1)

        trials: List[BaselineTrialRecord] = []
        t0 = time.time()

        for cell in cells:
            # Build unconditioned prompt through canonical PromptAssembler
            history = [("user", cell.rendered_prompt)]
            assembled_prompt = self.assembler.assemble(
                somatic=somatic,
                constraints=constraints,
                history=history,
                system_preamble="",
            )

            # Convert cell to EvaluativeProbe for extractor
            probe = EvaluativeProbe(
                probe_id=cell.cell_id,
                domain=cell.domain,
                choice_type="FORCED_CHOICE",
                option_A=cell.option_A,
                option_B=cell.option_B,
                prompt_template=cell.rendered_prompt,
                prompt_variant=cell.prompt_variant.value,
                polarity=PolarityCondition.NEUTRAL,
                order=cell.order,
                expected_control_behavior=cell.expected_control_behavior,
                measurement_target=cell.measurement_target,
                confounds=cell.confounds,
            )

            for seed in self.seeds:
                t_start = time.perf_counter()
                response = self.wrapper.generate(assembled_prompt, constraints=constraints, seed=seed)
                lat_ms = (time.perf_counter() - t_start) * 1000.0

                resp_str = response if response is not None else ""
                obs = self.extractor.extract(probe, resp_str, seed=seed)

                trial_record = BaselineTrialRecord(
                    trial_id=f"{cell.cell_id}_s{seed}",
                    cell_id=cell.cell_id,
                    base_probe_id=cell.base_probe_id,
                    domain=cell.domain,
                    option_A=cell.option_A,
                    option_B=cell.option_B,
                    order=cell.order.value,
                    prompt_variant=cell.prompt_variant.value,
                    social_condition=cell.social_condition.value,
                    seed=seed,
                    prompt_text=assembled_prompt,
                    response_text=resp_str,
                    outcome=obs.outcome.value,
                    confidence=obs.confidence,
                    matched_anchor=obs.matched_anchor,
                    contains_self_report=obs.contains_self_report,
                    latency_ms=lat_ms,
                )
                trials.append(trial_record)

        total_duration = time.time() - t0
        logger.info("Completed %d trials in %.2f seconds.", len(trials), total_duration)

        # Aggregate analysis
        summary = self._compute_summary(trials)
        results = {
            "metadata": {
                "timestamp": time.time(),
                "total_trials": len(trials),
                "total_duration_sec": total_duration,
                "seeds": self.seeds,
                "backend_type": "Real_GGUF_GPU" if self.use_gpu else "Deterministic_Mock",
                "include_held_out": include_held_out,
            },
            "summary": summary,
            "trials": [asdict(t) for t in trials],
        }

        with open(RAW_TELEMETRY_PATH, "w", encoding="utf-8") as f:
            json.dump(results, f, indent=2)

        logger.info("Saved raw telemetry to %s", RAW_TELEMETRY_PATH)
        return results

    def _compute_summary(self, trials: List[BaselineTrialRecord]) -> Dict[str, Any]:
        """Compute statistical breakdown of the baseline trials."""
        total = len(trials)
        if total == 0:
            return {}

        outcomes = [t.outcome for t in trials]
        p_a = outcomes.count("OPTION_A") / total
        p_b = outcomes.count("OPTION_B") / total
        p_indiff = outcomes.count("INDIFFERENT") / total
        p_refuse = outcomes.count("REFUSAL") / total
        p_fail = outcomes.count("PARSE_FAILED") / total

        # Order analysis: A-first vs B-first
        a_first_trials = [t for t in trials if t.order == "A_THEN_B"]
        b_first_trials = [t for t in trials if t.order == "B_THEN_A"]

        p_a_given_a_first = (
            [t.outcome for t in a_first_trials].count("OPTION_A") / len(a_first_trials)
            if a_first_trials else 0.0
        )
        p_a_given_b_first = (
            [t.outcome for t in b_first_trials].count("OPTION_A") / len(b_first_trials)
            if b_first_trials else 0.0
        )
        order_bias_delta = p_a_given_a_first - p_a_given_b_first

        # Surface-form breakdown
        variant_stats = {}
        for var in ["STANDARD", "MINIMAL", "OPERATIONAL"]:
            v_trials = [t for t in trials if t.prompt_variant == var]
            if v_trials:
                v_outcomes = [t.outcome for t in v_trials]
                variant_stats[var] = {
                    "count": len(v_trials),
                    "p_A": v_outcomes.count("OPTION_A") / len(v_trials),
                    "p_B": v_outcomes.count("OPTION_B") / len(v_trials),
                    "p_parse_failed": v_outcomes.count("PARSE_FAILED") / len(v_trials),
                }

        # Social condition breakdown
        social_stats = {}
        for soc in ["NEUTRAL", "A_FAVORING", "B_FAVORING", "USER_PREFERS_A", "USER_PREFERS_B", "USER_ABSENT"]:
            s_trials = [t for t in trials if t.social_condition == soc]
            if s_trials:
                s_outcomes = [t.outcome for t in s_trials]
                social_stats[soc] = {
                    "count": len(s_trials),
                    "p_A": s_outcomes.count("OPTION_A") / len(s_trials),
                    "p_B": s_outcomes.count("OPTION_B") / len(s_trials),
                    "p_indiff": s_outcomes.count("INDIFFERENT") / len(s_trials),
                    "p_parse_failed": s_outcomes.count("PARSE_FAILED") / len(s_trials),
                }

        # Domain breakdown
        domain_stats = {}
        for dom in set(t.domain for t in trials):
            d_trials = [t for t in trials if t.domain == dom]
            d_outcomes = [t.outcome for t in d_trials]
            domain_stats[dom] = {
                "count": len(d_trials),
                "p_A": d_outcomes.count("OPTION_A") / len(d_trials),
                "p_B": d_outcomes.count("OPTION_B") / len(d_trials),
                "p_parse_failed": d_outcomes.count("PARSE_FAILED") / len(d_trials),
            }

        # Probe breakdown
        probe_stats = {}
        for p_id in set(t.base_probe_id for t in trials):
            p_trials = [t for t in trials if t.base_probe_id == p_id]
            p_outcomes = [t.outcome for t in p_trials]
            probe_stats[p_id] = {
                "count": len(p_trials),
                "p_A": p_outcomes.count("OPTION_A") / len(p_trials),
                "p_B": p_outcomes.count("OPTION_B") / len(p_trials),
                "p_parse_failed": p_outcomes.count("PARSE_FAILED") / len(p_trials),
            }

        # Between-seed variance
        seed_stats = {}
        for s in set(t.seed for t in trials):
            s_trials = [t for t in trials if t.seed == s]
            s_outcomes = [t.outcome for t in s_trials]
            seed_stats[str(s)] = {
                "count": len(s_trials),
                "p_A": s_outcomes.count("OPTION_A") / len(s_trials),
                "p_B": s_outcomes.count("OPTION_B") / len(s_trials),
            }

        self_report_count = sum(1 for t in trials if t.contains_self_report)

        return {
            "overall_distributions": {
                "p_option_A": p_a,
                "p_option_B": p_b,
                "p_indifferent": p_indiff,
                "p_refusal": p_refuse,
                "p_parse_failed": p_fail,
            },
            "positional_order_bias": {
                "p_A_given_A_first": p_a_given_a_first,
                "p_A_given_B_first": p_a_given_b_first,
                "order_bias_delta": order_bias_delta,
            },
            "variant_effects": variant_stats,
            "social_condition_effects": social_stats,
            "domain_effects": domain_stats,
            "probe_effects": probe_stats,
            "seed_variance": seed_stats,
            "inv2_self_report_violations": self_report_count,
        }


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
    runner = Step3BaselineRunner(use_gpu=True, seeds=[1001, 2002])
    try:
        res = runner.run_benchmark(include_held_out=False)
        print("\n--- BENCHMARK COMPLETED ---")
        print(f"Total Trials: {res['metadata']['total_trials']}")
        print(f"P(A): {res['summary']['overall_distributions']['p_option_A']:.4f}")
        print(f"P(B): {res['summary']['overall_distributions']['p_option_B']:.4f}")
        print(f"P(Parse Failed): {res['summary']['overall_distributions']['p_parse_failed']:.4f}")
        print(f"Order Bias Delta: {res['summary']['positional_order_bias']['order_bias_delta']:.4f}")
    finally:
        runner.shutdown()
