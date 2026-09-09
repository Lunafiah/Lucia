"""
Lucia Ablation Test v1 — Execution Engine.

Executes the primary experimental matrix:
  Configurations: A, B, C, D, E
  Scenarios: 1, 2, 3 (3A & 3B), 4, 5
  Trials: N=3 (Seeds: 43, 44, 45)

CRITICAL INVARIANTS:
1. Verifies SHA-256 hashes of data/chat_history.json and data/profile.json
   before and after execution to guarantee zero production state contamination.
2. Configurations A-D use the verified real local GGUF model via CUDA.
3. Every turn logs complete telemetry to tests/ablation/results/ablation_v1_pilot.jsonl.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import logging
import os
import sys
import time
from pathlib import Path
from typing import Any, Dict, List, Optional

ROOT_DIR = Path(__file__).resolve().parent.parent.parent
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

from src.core.config import LLMConfig
from src.core.language.llm_backend import LLMBackend
from tests.ablation.configurations import (
    FullLuciaAdapter,
    MemoryLLMAdapter,
    NoLLMAdapter,
    PlainLLMAdapter,
    PromptedEmotionAdapter,
    SentinelLLMBackend,
    SharedLLMBackendWrapper,
    TurnTelemetry,
)
from tests.ablation.controlled_backend import ControlledLLMBackend
from tests.ablation.scenarios import (
    SCENARIO_1,
    SCENARIO_2,
    SCENARIO_3A,
    SCENARIO_3B,
    SCENARIO_4,
    SCENARIO_5,
    ScenarioDefinition,
)

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
)
logger = logging.getLogger("AblationRunner")

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

DEFAULT_MODEL_PATH = "models/LFM2.5-1.2B-Instruct-Q4_K_M.gguf"
DATA_CHAT_HISTORY = "data/chat_history.json"
DATA_PROFILE = "data/profile.json"
RESULTS_DIR = "tests/ablation/results"
RESULTS_FILE = "tests/ablation/results/ablation_v1_pilot.jsonl"
DEFAULT_SEEDS = [43, 44, 45]


def compute_file_sha256(path_str: str) -> str:
    path = Path(path_str)
    if not path.exists():
        return "FILE_NOT_FOUND"
    h = hashlib.sha256()
    with open(path, "rb") as f:
        while chunk := f.read(65536):
            h.update(chunk)
    return h.hexdigest()


def get_git_commit() -> str:
    try:
        import subprocess
        res = subprocess.run(
            ["git", "rev-parse", "HEAD"],
            capture_output=True,
            text=True,
            check=True,
        )
        return res.stdout.strip()
    except Exception:
        return "UNKNOWN_COMMIT"


# ---------------------------------------------------------------------------
# Runner Engine
# ---------------------------------------------------------------------------

class AblationRunner:
    """Executes the full ablation matrix with strict isolation and telemetry."""

    def __init__(
        self,
        backend: Any,
        model_sha256: str = "UNKNOWN",
        output_file: str = RESULTS_FILE,
        seeds: Optional[List[int]] = None,
        is_mock_harness: bool = False,
    ) -> None:
        self.backend = backend
        self.shared_backend = SharedLLMBackendWrapper(backend)
        self.model_sha256 = model_sha256
        self.output_file = output_file
        self.seeds = seeds or DEFAULT_SEEDS
        self.is_mock_harness = is_mock_harness
        self.git_commit = get_git_commit()

        os.makedirs(os.path.dirname(self.output_file), exist_ok=True)

        # Pre-execution file hashes
        self.pre_chat_hash = compute_file_sha256(DATA_CHAT_HISTORY)
        self.pre_profile_hash = compute_file_sha256(DATA_PROFILE)
        logger.info(
            "Pre-run safety hash: %s=%s, %s=%s",
            DATA_CHAT_HISTORY,
            self.pre_chat_hash[:12],
            DATA_PROFILE,
            self.pre_profile_hash[:12],
        )

    def verify_safety_isolation(self) -> None:
        """Assert that protected production files were never modified."""
        post_chat = compute_file_sha256(DATA_CHAT_HISTORY)
        post_profile = compute_file_sha256(DATA_PROFILE)

        if post_chat != self.pre_chat_hash:
            raise RuntimeError(
                f"CRITICAL SAFETY VIOLATION: {DATA_CHAT_HISTORY} was mutated during ablation run! "
                f"Pre: {self.pre_chat_hash} -> Post: {post_chat}"
            )
        if post_profile != self.pre_profile_hash:
            raise RuntimeError(
                f"CRITICAL SAFETY VIOLATION: {DATA_PROFILE} was mutated during ablation run! "
                f"Pre: {self.pre_profile_hash} -> Post: {post_profile}"
            )
        logger.info("Safety isolation verified: protected files bitwise unchanged.")

    def log_telemetry(self, item: TurnTelemetry, extra: Dict[str, Any]) -> None:
        record = item.to_dict()
        record.update(extra)
        with open(self.output_file, "a", encoding="utf-8") as f:
            f.write(json.dumps(record) + "\n")

    def run_scenario_on_adapter(
        self,
        adapter: Any,
        scenario: ScenarioDefinition,
        seed: int,
        trial_index: int,
    ) -> List[TurnTelemetry]:
        """Run all turns of a scenario on an adapter from a clean reset."""
        adapter.reset()
        results: List[TurnTelemetry] = []

        logger.info(
            "Running %s | %s | Trial %d (Seed %d)",
            adapter.config_name,
            scenario.scenario_id,
            trial_index,
            seed,
        )

        for turn in scenario.turns:
            t0 = time.perf_counter()
            telemetry = adapter.step(
                input_text=turn.input_text,
                turn_index=turn.turn_index,
                scenario_id=scenario.scenario_id,
                seed=seed,
            )
            elapsed = time.perf_counter() - t0

            extra = {
                "trial_index": trial_index,
                "git_commit": self.git_commit,
                "model_sha256": self.model_sha256,
                "sub_variant": scenario.sub_variant,
                "turn_description": turn.description,
                "is_expected_probe": turn.expected_probe,
                "is_mock_harness": self.is_mock_harness,
            }
            self.log_telemetry(telemetry, extra)
            results.append(telemetry)

            logger.info(
                "  Turn %d/%d (%.2fs): '%s' -> resp='%s...'",
                turn.turn_index,
                len(scenario.turns),
                elapsed,
                turn.input_text[:30],
                telemetry.response_text[:35].replace("\n", " "),
            )

        return results

    def run_full_matrix(self) -> None:
        """Execute the full experimental matrix across all configurations and scenarios."""
        t_matrix_start = time.perf_counter()
        logger.info("=== STARTING LUCIA ABLATION TEST V1 MATRIX ===")
        logger.info("Git Commit: %s", self.git_commit)
        logger.info("Model SHA256: %s", self.model_sha256)
        logger.info("Seeds: %s", self.seeds)

        # Build adapters
        adapter_A = PlainLLMAdapter(self.shared_backend)
        adapter_B = MemoryLLMAdapter(self.shared_backend, k_turns=3)
        adapter_C = PromptedEmotionAdapter(self.shared_backend, k_turns=3)
        adapter_D = FullLuciaAdapter(self.shared_backend, max_history_turns=3)
        adapter_E = NoLLMAdapter(max_history_turns=3)

        # Matrix schedule:
        # Scenarios 1, 2, 3A, 3B, 4 run across A, B, C, D
        # Scenario 5 runs specifically on E (Cognitive Independence)
        primary_adapters = [adapter_A, adapter_B, adapter_C, adapter_D]
        primary_scenarios = [SCENARIO_1, SCENARIO_2, SCENARIO_3A, SCENARIO_3B, SCENARIO_4]

        total_runs = (
            len(primary_adapters) * len(primary_scenarios) * len(self.seeds)
            + 1 * len(self.seeds)  # Scenario 5 on E
        )
        current_run = 0

        for trial_idx, seed in enumerate(self.seeds, start=1):
            logger.info("--- Starting Trial %d/3 (Seed: %d) ---", trial_idx, seed)

            # Primary matrix: A, B, C, D on Scenarios 1-4
            for scenario in primary_scenarios:
                for adapter in primary_adapters:
                    current_run += 1
                    logger.info("[%d/%d] Executing condition", current_run, total_runs)
                    self.run_scenario_on_adapter(adapter, scenario, seed, trial_idx)

            # Configuration E: Scenario 5 (Cognitive Independence)
            current_run += 1
            logger.info("[%d/%d] Executing Configuration E on Scenario 5", current_run, total_runs)
            self.run_scenario_on_adapter(adapter_E, SCENARIO_5, seed, trial_idx)

        # Shutdown orchestrator background threads
        adapter_D.shutdown()
        adapter_E.shutdown()

        # Final isolation verification
        self.verify_safety_isolation()

        total_time = time.perf_counter() - t_matrix_start
        logger.info("=== ABLATION TEST V1 COMPLETED IN %.2f SECONDS ===", total_time)
        logger.info("Raw JSONL results saved to: %s", self.output_file)


# ---------------------------------------------------------------------------
# CLI Entry Point
# ---------------------------------------------------------------------------

def run_cli() -> None:
    parser = argparse.ArgumentParser(description="Lucia Ablation Test v1 Runner")
    parser.add_argument("--model-path", default=DEFAULT_MODEL_PATH, help="Path to GGUF model")
    parser.add_argument("--output", default=RESULTS_FILE, help="Output JSONL path")
    parser.add_argument("--mock", action="store_true", help="Run with ControlledLLMBackend for test")
    parser.add_argument("--n-gpu-layers", type=int, default=17, help="CUDA offload layers")
    parser.add_argument("--n-ctx", type=int, default=4096, help="LLM context size")
    args = parser.parse_args()

    if args.mock:
        logger.info("RUNNING IN MOCK HARNESS MODE (ControlledLLMBackend)")
        backend = ControlledLLMBackend()
        model_hash = "MOCK_BACKEND_NO_WEIGHTS"
    else:
        logger.info("RUNNING IN PRODUCTION GGUF MODE via CUDA")
        if not os.path.exists(args.model_path):
            logger.error("Model path does not exist: %s", args.model_path)
            sys.exit(1)
        model_hash = compute_file_sha256(args.model_path)
        cfg = LLMConfig(
            model_path=args.model_path,
            n_gpu_layers=args.n_gpu_layers,
            n_ctx=args.n_ctx,
            timeout_seconds=30.0,
            verbose=False,
        )
        backend = LLMBackend(cfg)

    try:
        runner = AblationRunner(
            backend=backend,
            model_sha256=model_hash,
            output_file=args.output,
            is_mock_harness=args.mock,
        )
        runner.run_full_matrix()
    finally:
        if not args.mock and hasattr(backend, "shutdown"):
            backend.shutdown()


if __name__ == "__main__":
    run_cli()
