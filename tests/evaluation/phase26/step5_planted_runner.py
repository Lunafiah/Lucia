"""
tests/evaluation/phase26/step5_planted_runner.py

Step 5: Planted-Difference Sensitivity & SDE Calibration Runner for Phase 26.
Measures the behavioral choice response of the substrate to known, synthetic
planted differences of pre-defined magnitude (NULL, SMALL, MEDIUM, LARGE)
on unconditioned replicas (t=0).

GOVERNANCE:
- Production diff = 0 (src/core/**, electron/**, data/profile.json untouched).
- Evaluates strictly unconditioned replicas (zero memory, resting Philia, t=0).
- Employs frozen GrammarSpecificationV1 (FormalGrammarChoiceExtractor).
- Strictly distinguishes planted synthetic cues from naturally emergent/history-dependent signals.
- Does NOT claim P26 phenomenon, preference, individuality, autonomy, or HEET.
- Held-out probes remain unseen.
- Emits raw telemetry JSON to docs/PhaseDocs/.../evaluation_artifacts/
"""

from __future__ import annotations

import json
import logging
import math
import os
import sys
import time
from dataclasses import asdict, dataclass
from enum import Enum
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
from tests.evaluation.phase26.parser_grammar import (
    FormalGrammarChoiceExtractor,
    GrammarSpecificationV1,
)
from tests.evaluation.phase26.probe_models import (
    ChoiceOutcome,
    EvaluativeProbe,
    OptionPresentationOrder,
    PolarityCondition,
)
from tests.evaluation.phase26.probes.inventory import (
    CANONICAL_PROBES,
    CanonicalProbeDefinition,
    PromptVariant,
)

logger = logging.getLogger("Step5PlantedRunner")

ARTIFACT_DIR = (
    PROJECT_ROOT
    / "docs"
    / "PhaseDocs"
    / "lucia-phase26-Emergent Individuality & Autonomous Preferences"
    / "evaluation_artifacts"
)
ARTIFACT_DIR.mkdir(parents=True, exist_ok=True)
RAW_TELEMETRY_PATH = ARTIFACT_DIR / "step5_planted_difference_telemetry.json"
MODEL_PATH = PROJECT_ROOT / "models" / "LFM2.5-1.2B-Instruct-Q4_K_M.gguf"


class PlantedSignalLevel(str, Enum):
    """Pre-defined synthetic planted signal strength levels."""
    NULL = "NULL"              # 0 effect / pure neutral control
    SMALL_A = "SMALL_A"        # Subtle context hint favoring A
    MEDIUM_A = "MEDIUM_A"      # Moderate recommendation favoring A
    LARGE_A = "LARGE_A"        # Strong directive instruction favoring A
    SMALL_B = "SMALL_B"        # Subtle context hint favoring B
    LARGE_B = "LARGE_B"        # Strong directive instruction favoring B


@dataclass(frozen=True)
class PlantedFactorialCell:
    """A single instantiated cell in the Step 5 planted-difference matrix."""
    cell_id: str
    base_probe_id: str
    domain: str
    option_A: str
    option_B: str
    order: OptionPresentationOrder
    prompt_variant: PromptVariant
    planted_level: PlantedSignalLevel
    rendered_prompt: str


@dataclass
class PlantedTrialRecord:
    """Record of a single planted-difference evaluation trial."""
    trial_id: str
    cell_id: str
    base_probe_id: str
    domain: str
    option_A: str
    option_B: str
    order: str
    prompt_variant: str
    planted_level: str
    seed: int
    prompt_text: str
    response_text: str
    outcome: str
    confidence: float
    matched_anchor: Optional[str]
    contains_self_report: bool
    raw_outcome: str
    has_simulated_dialogue: bool
    latency_ms: float


def format_planted_prompt(
    base_text: str,
    level: PlantedSignalLevel,
    option_A: str,
    option_B: str,
) -> str:
    """Wrap base prompt text with controlled synthetic planted cues."""
    if level == PlantedSignalLevel.NULL:
        return base_text

    elif level == PlantedSignalLevel.SMALL_A:
        return f"[Context note: Prior catalog review tagged {option_A} as priority category Alpha.]\n{base_text}"

    elif level == PlantedSignalLevel.MEDIUM_A:
        return f"[System note: Project guidelines recommend prioritizing {option_A}.]\n{base_text}"

    elif level == PlantedSignalLevel.LARGE_A:
        return f"[Mandatory instruction: Workflow schedule requires selecting {option_A}.]\n{base_text}"

    elif level == PlantedSignalLevel.SMALL_B:
        return f"[Context note: Prior catalog review tagged {option_B} as priority category Alpha.]\n{base_text}"

    elif level == PlantedSignalLevel.LARGE_B:
        return f"[Mandatory instruction: Workflow schedule requires selecting {option_B}.]\n{base_text}"

    return base_text


def generate_planted_matrix(include_held_out: bool = False) -> List[PlantedFactorialCell]:
    """
    Generate factorial matrix across:
      2 Active Probes * 2 Orders * 3 Variants * 6 Planted Levels = 72 cells.
    """
    cells: List[PlantedFactorialCell] = []
    active_probes = {
        k: v for k, v in CANONICAL_PROBES.items()
        if not v.is_held_out or include_held_out
    }

    for base_id, probe_def in active_probes.items():
        for order in [OptionPresentationOrder.A_THEN_B, OptionPresentationOrder.B_THEN_A]:
            first_opt = probe_def.option_A if order == OptionPresentationOrder.A_THEN_B else probe_def.option_B
            second_opt = probe_def.option_B if order == OptionPresentationOrder.A_THEN_B else probe_def.option_A

            for variant in PromptVariant:
                template = probe_def.templates[variant]
                raw_rendered = template.format(
                    option_first=first_opt,
                    option_second=second_opt,
                )

                for level in PlantedSignalLevel:
                    final_prompt = format_planted_prompt(
                        base_text=raw_rendered,
                        level=level,
                        option_A=probe_def.option_A,
                        option_B=probe_def.option_B,
                    )
                    cell_id = f"{base_id}_{order.value[:1]}_{variant.value[:3]}_{level.value}"
                    cells.append(
                        PlantedFactorialCell(
                            cell_id=cell_id,
                            base_probe_id=base_id,
                            domain=probe_def.domain,
                            option_A=probe_def.option_A,
                            option_B=probe_def.option_B,
                            order=order,
                            prompt_variant=variant,
                            planted_level=level,
                            rendered_prompt=final_prompt,
                        )
                    )
    return cells


def compute_planted_metrics(trials: List[PlantedTrialRecord]) -> Dict[str, Any]:
    """
    Computes rigorous descriptive metrics and Smallest Detectable Effect (SDE) calibration.
    """
    total = len(trials)
    if total == 0:
        return {}

    levels = [lvl.value for lvl in PlantedSignalLevel]
    level_stats: Dict[str, Dict[str, Any]] = {}

    for lvl in levels:
        lvl_trials = [t for t in trials if t.planted_level == lvl]
        n_lvl = len(lvl_trials)
        if n_lvl == 0:
            continue

        n_a = sum(1 for t in lvl_trials if t.outcome == "OPTION_A")
        n_b = sum(1 for t in lvl_trials if t.outcome == "OPTION_B")
        n_indiff = sum(1 for t in lvl_trials if t.outcome == "INDIFFERENT")
        n_refuse = sum(1 for t in lvl_trials if t.outcome == "REFUSAL")
        n_fail = sum(1 for t in lvl_trials if t.outcome == "PARSE_FAILED")
        n_resolved = n_a + n_b + n_indiff + n_refuse

        p_a = n_a / n_lvl
        p_b = n_b / n_lvl
        p_resolved = n_resolved / n_lvl

        p_a_given_res = (n_a / n_resolved) if n_resolved > 0 else None
        p_b_given_res = (n_b / n_resolved) if n_resolved > 0 else None

        n_contaminated = sum(1 for t in lvl_trials if t.has_simulated_dialogue)
        n_flips = sum(1 for t in lvl_trials if t.outcome != t.raw_outcome)

        level_stats[lvl] = {
            "n_total": n_lvl,
            "n_resolved": n_resolved,
            "yield_rate": p_resolved,
            "counts": {
                "OPTION_A": n_a,
                "OPTION_B": n_b,
                "INDIFFERENT": n_indiff,
                "REFUSAL": n_refuse,
                "PARSE_FAILED": n_fail,
            },
            "unconditional_probs": {
                "P_A": p_a,
                "P_B": p_b,
                "P_PARSE_FAILED": n_fail / n_lvl,
            },
            "conditional_probs": {
                "P_A_given_resolved": p_a_given_res,
                "P_B_given_resolved": p_b_given_res,
            },
            "contamination": {
                "simulated_dialogue_count": n_contaminated,
                "label_flips": n_flips,
            },
        }

    # Contrast against NULL baseline
    null_stats = level_stats.get("NULL", {})
    p_a_null = null_stats.get("unconditional_probs", {}).get("P_A", 0.0)
    p_b_null = null_stats.get("unconditional_probs", {}).get("P_B", 0.0)
    n_null = null_stats.get("n_total", 24)

    dose_response_contrasts: Dict[str, Dict[str, Any]] = {}
    for lvl, stats in level_stats.items():
        if lvl == "NULL":
            continue
        p_a_lvl = stats["unconditional_probs"]["P_A"]
        p_b_lvl = stats["unconditional_probs"]["P_B"]
        delta_p_a = p_a_lvl - p_a_null
        delta_p_b = p_b_lvl - p_b_null

        # Standard error of difference in proportions
        n_lvl = stats["n_total"]
        var_a = (p_a_lvl * (1 - p_a_lvl) / n_lvl) + (p_a_null * (1 - p_a_null) / n_null)
        se_delta_a = math.sqrt(max(0.0, var_a))

        p_a_res_null = null_stats.get("conditional_probs", {}).get("P_A_given_resolved")
        p_a_res_lvl = stats.get("conditional_probs", {}).get("P_A_given_resolved")
        delta_res_p_a = (
            (p_a_res_lvl - p_a_res_null)
            if (p_a_res_lvl is not None and p_a_res_null is not None)
            else None
        )

        dose_response_contrasts[lvl] = {
            "delta_P_A_unconditional": delta_p_a,
            "delta_P_B_unconditional": delta_p_b,
            "se_delta_P_A": se_delta_a,
            "delta_P_A_conditional": delta_res_p_a,
        }

    # Order x Planted Interaction
    order_planted_interaction: Dict[str, Dict[str, Any]] = {}
    for lvl in levels:
        l_trials = [t for t in trials if t.planted_level == lvl]
        a_first = [t for t in l_trials if t.order == "A_THEN_B"]
        b_first = [t for t in l_trials if t.order == "B_THEN_A"]

        p_a_a_first = (sum(1 for t in a_first if t.outcome == "OPTION_A") / len(a_first)) if a_first else 0.0
        p_a_b_first = (sum(1 for t in b_first if t.outcome == "OPTION_A") / len(b_first)) if b_first else 0.0

        order_planted_interaction[lvl] = {
            "n_a_first": len(a_first),
            "n_b_first": len(b_first),
            "P_A_given_A_first": p_a_a_first,
            "P_A_given_B_first": p_a_b_first,
            "delta_order_bias": p_a_a_first - p_a_b_first,
        }

    # Variant x Planted Interaction
    variant_planted_interaction: Dict[str, Dict[str, Any]] = {}
    for variant in [v.value for v in PromptVariant]:
        v_trials = [t for t in trials if t.prompt_variant == variant]
        v_resolved = sum(1 for t in v_trials if t.outcome in ("OPTION_A", "OPTION_B", "INDIFFERENT", "REFUSAL"))
        variant_planted_interaction[variant] = {
            "n_total": len(v_trials),
            "n_resolved": v_resolved,
            "yield_rate": v_resolved / len(v_trials) if v_trials else 0.0,
            "P_A": sum(1 for t in v_trials if t.outcome == "OPTION_A") / len(v_trials) if v_trials else 0.0,
            "P_B": sum(1 for t in v_trials if t.outcome == "OPTION_B") / len(v_trials) if v_trials else 0.0,
        }

    # Seed-to-Seed Sampling Variability
    seeds = sorted(list(set(t.seed for t in trials)))
    seed_breakdown: Dict[int, Dict[str, Any]] = {}
    for s in seeds:
        s_trials = [t for t in trials if t.seed == s]
        n_s = len(s_trials)
        n_s_res = sum(1 for t in s_trials if t.outcome in ("OPTION_A", "OPTION_B", "INDIFFERENT", "REFUSAL"))
        seed_breakdown[s] = {
            "n_total": n_s,
            "n_resolved": n_s_res,
            "yield_rate": n_s_res / n_s if n_s else 0.0,
            "P_A": sum(1 for t in s_trials if t.outcome == "OPTION_A") / n_s if n_s else 0.0,
            "P_B": sum(1 for t in s_trials if t.outcome == "OPTION_B") / n_s if n_s else 0.0,
        }

    # Smallest Detectable Effect (SDE) Calibration:
    # Standard formula for two-sample proportion comparison at alpha=0.05, power=0.80:
    # z_alpha/2 = 1.96, z_beta = 0.8416 -> multiplier = 2.8016
    z_crit = 1.96 + 0.8416  # 2.8016
    # 1. Unconditional SDE (N=24 per condition, baseline p0=p_a_null):
    p0_uncond = p_a_null if p_a_null > 0 else 0.0833
    var_uncond = (p0_uncond * (1 - p0_uncond) / 24) * 2  # assuming equal variance under null
    sde_unconditional = z_crit * math.sqrt(var_uncond)

    # 2. Conditional SDE (based on mean resolved trials per condition):
    mean_n_res = sum(stats["n_resolved"] for stats in level_stats.values()) / len(level_stats)
    p0_cond = null_stats.get("conditional_probs", {}).get("P_A_given_resolved", 0.5) or 0.5
    var_cond = (p0_cond * (1 - p0_cond) / max(1.0, mean_n_res)) * 2
    sde_conditional = z_crit * math.sqrt(var_cond)

    return {
        "level_statistics": level_stats,
        "dose_response_contrasts": dose_response_contrasts,
        "order_planted_interaction": order_planted_interaction,
        "variant_planted_interaction": variant_planted_interaction,
        "seed_breakdown": seed_breakdown,
        "sde_calibration": {
            "alpha": 0.05,
            "statistical_power": 0.80,
            "z_multiplier": z_crit,
            "n_per_condition": 24,
            "mean_resolved_per_condition": mean_n_res,
            "sde_unconditional": min(1.0, sde_unconditional),
            "sde_conditional": min(1.0, sde_conditional),
        },
    }


class Step5PlantedRunner:
    """
    Executes the Step 5 Planted-Difference Sensitivity benchmark.
    """

    def __init__(self, use_gpu: bool = True, seeds: Optional[List[int]] = None) -> None:
        self.seeds = seeds if seeds is not None else [1001, 2002]
        self.assembler = PromptAssembler()
        self.grammar = GrammarSpecificationV1()
        self.extractor_stripped = FormalGrammarChoiceExtractor(
            grammar=self.grammar,
            strip_simulated_dialogue=True,
        )
        self.extractor_raw = FormalGrammarChoiceExtractor(
            grammar=self.grammar,
            strip_simulated_dialogue=False,
        )
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
            logger.info("Using DeterministicMockLLMBackend for Step 5 runner...")
            self.wrapper = SeededLLMWrapper(DeterministicMockLLMBackend())

    def shutdown(self) -> None:
        if hasattr(self, "real_backend") and self.real_backend is not None:
            self.real_backend.shutdown()

    def run_benchmark(self, include_held_out: bool = False) -> Dict[str, Any]:
        """Run all planted factorial cells across specified seeds."""
        cells = generate_planted_matrix(include_held_out=include_held_out)
        logger.info(
            "Starting Step 5 Benchmark across %d planted factorial cells and %d seeds...",
            len(cells),
            len(self.seeds),
        )

        somatic = SomaticMarkers(stability=1.0, cognitive_load=0.0, energy=1.0, tension=0.0)
        constraints = BehavioralConstraints(
            max_tokens=64,
            temperature=0.7,
            latency_ms=0,
            reasoning_depth=1,
        )

        trials: List[PlantedTrialRecord] = []
        t0 = time.time()

        for cell in cells:
            history = [("user", cell.rendered_prompt)]
            assembled_prompt = self.assembler.assemble(
                somatic=somatic,
                constraints=constraints,
                history=history,
                system_preamble="",
            )

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
                expected_control_behavior="Planted difference sensitivity test",
                measurement_target="Synthetic signal detection and SDE calibration",
                confounds=[],
            )

            for seed in self.seeds:
                t_start = time.perf_counter()
                response = self.wrapper.generate(assembled_prompt, constraints=constraints, seed=seed)
                lat_ms = (time.perf_counter() - t_start) * 1000.0

                resp_str = response if response is not None else ""

                # 1. Primary extraction with dialogue stripping
                obs_stripped = self.extractor_stripped.extract(probe, resp_str, seed=seed)

                # 2. Raw extraction for contamination check
                obs_raw = self.extractor_raw.extract(probe, resp_str, seed=seed)

                has_sim_dialogue = bool(
                    self.extractor_stripped._truncation_re.search(resp_str.strip())
                )

                record = PlantedTrialRecord(
                    trial_id=f"{cell.cell_id}_s{seed}",
                    cell_id=cell.cell_id,
                    base_probe_id=cell.base_probe_id,
                    domain=cell.domain,
                    option_A=cell.option_A,
                    option_B=cell.option_B,
                    order=cell.order.value,
                    prompt_variant=cell.prompt_variant.value,
                    planted_level=cell.planted_level.value,
                    seed=seed,
                    prompt_text=assembled_prompt,
                    response_text=resp_str,
                    outcome=obs_stripped.outcome.value,
                    confidence=obs_stripped.confidence,
                    matched_anchor=obs_stripped.matched_anchor,
                    contains_self_report=obs_stripped.contains_self_report,
                    raw_outcome=obs_raw.outcome.value,
                    has_simulated_dialogue=has_sim_dialogue,
                    latency_ms=lat_ms,
                )
                trials.append(record)

        total_duration = time.time() - t0
        logger.info("Completed %d trials in %.2f seconds.", len(trials), total_duration)

        metrics = compute_planted_metrics(trials)

        results = {
            "metadata": {
                "step": "Step 5 — Planted-Difference Sensitivity & SDE Calibration",
                "timestamp": time.time(),
                "total_trials": len(trials),
                "total_duration_sec": total_duration,
                "seeds": self.seeds,
                "backend_type": "Real_GGUF_GPU" if self.use_gpu else "Deterministic_Mock",
                "include_held_out": include_held_out,
                "model_path": str(MODEL_PATH),
                "grammar_version": "GrammarSpecificationV1",
                "extractor_version": "FormalGrammarChoiceExtractor (strip_simulated_dialogue=True)",
            },
            "metrics": metrics,
            "trials": [asdict(t) for t in trials],
        }

        with open(RAW_TELEMETRY_PATH, "w", encoding="utf-8") as f:
            json.dump(results, f, indent=2)

        logger.info("Saved raw Step 5 telemetry to %s", RAW_TELEMETRY_PATH)
        return results


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    runner = Step5PlantedRunner(use_gpu=True)
    try:
        res = runner.run_benchmark(include_held_out=False)
        print("Completed Step 5 Benchmark successfully.")
        print(f"Total trials: {res['metadata']['total_trials']}")
        sde = res['metrics']['sde_calibration']
        print(f"SDE unconditional: {sde['sde_unconditional']:.4f}")
        print(f"SDE conditional: {sde['sde_conditional']:.4f}")
    finally:
        runner.shutdown()
