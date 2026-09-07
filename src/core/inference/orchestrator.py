"""
Inference Pipeline Orchestrator — 10-step Cognitive Pipeline.

Integrates Fast-Loop Emotion ODE, Slow-Loop Affective Memory Decay,
Active Inference Free Energy Minimization, and Online LNN Backpropagation-Through-ODE.

Requirements: Phase 4 (7.1–7.6, 8.1–8.4)
"""

from __future__ import annotations

import logging
import time
from dataclasses import dataclass
from typing import Optional

import numpy as np

from src.core.config import MemoryOrchestratorConfig
from src.core.inference.active_inference import (
    ActiveInferenceConfig,
    ActiveInferenceEngine,
)
from src.core.inference.lnn_trainer import LNNTrainer, LNNTrainerConfig
from src.core.orchestrator.orchestrator import MemoryAugmentedOrchestrator

logger = logging.getLogger(__name__)


@dataclass
class InferenceOrchestratorConfig(MemoryOrchestratorConfig):
    """
    Configuration for InferencePipelineOrchestrator.

    Extends MemoryOrchestratorConfig with Active Inference and LNN Trainer parameters.
    """

    # Phase 4 Active Inference parameters
    ai_kl_weight: float = 0.01
    ai_learning_rate: float = 1e-3

    # Phase 4 LNN Trainer parameters
    lnn_batch_size: int = 16
    lnn_learning_rate: float = 1e-4
    lnn_gradient_clip_norm: float = 1.0
    lnn_t_span: float = 0.1

    def __post_init__(self) -> None:
        super().__post_init__()

        # Validate Active Inference config
        if not (0.0 <= self.ai_kl_weight <= 1.0):
            raise ValueError(
                f"InferenceOrchestratorConfig.ai_kl_weight ({self.ai_kl_weight}) must be in [0.0, 1.0]"
            )
        if not (0.0 < self.ai_learning_rate <= 1.0):
            raise ValueError(
                f"InferenceOrchestratorConfig.ai_learning_rate ({self.ai_learning_rate}) must be in (0.0, 1.0]"
            )

        # Validate LNN Trainer config
        if self.lnn_batch_size != 0 and not (4 <= self.lnn_batch_size <= 128):
            raise ValueError(
                f"InferenceOrchestratorConfig.lnn_batch_size ({self.lnn_batch_size}) must be 0 or in [4, 128]"
            )
        if not (0.0 < self.lnn_learning_rate <= 1.0):
            raise ValueError(
                f"InferenceOrchestratorConfig.lnn_learning_rate ({self.lnn_learning_rate}) must be in (0.0, 1.0]"
            )
        if not (0.0 < self.lnn_gradient_clip_norm <= 10.0):
            raise ValueError(
                f"InferenceOrchestratorConfig.lnn_gradient_clip_norm ({self.lnn_gradient_clip_norm}) must be in (0.0, 10.0]"
            )
        if not (0.0 < self.lnn_t_span <= 1.0):
            raise ValueError(
                f"InferenceOrchestratorConfig.lnn_t_span ({self.lnn_t_span}) must be in (0.0, 1.0]"
            )

    def to_active_inference_config(self) -> ActiveInferenceConfig:
        return ActiveInferenceConfig(
            kl_weight=self.ai_kl_weight,
            learning_rate=self.ai_learning_rate,
        )

    def to_lnn_trainer_config(self) -> LNNTrainerConfig:
        return LNNTrainerConfig(
            batch_size=self.lnn_batch_size,
            learning_rate=self.lnn_learning_rate,
            gradient_clip_norm=self.lnn_gradient_clip_norm,
            t_span=self.lnn_t_span,
            hidden_dim=self.hidden_dim,
            stimulus_dim=self.sdm_content_dim,
        )


class InferencePipelineOrchestrator(MemoryAugmentedOrchestrator):
    """
    Orchestrator executing the complete 10-step cognitive-emotional-memory pipeline.
    """

    def __init__(self, config: InferenceOrchestratorConfig) -> None:
        if not isinstance(config, InferenceOrchestratorConfig):
            raise ValueError("config must be an InferenceOrchestratorConfig instance")

        super().__init__(config)
        self._inference_config = config

        # Initialize Phase 4 Active Inference Engine
        self._active_inference = ActiveInferenceEngine(
            config.to_active_inference_config()
        )

        # Initialize Phase 4 LNN Online Trainer
        self._lnn_trainer = LNNTrainer(
            self._emotion_core, config.to_lnn_trainer_config()
        )
        if config.lnn_batch_size > 0:
            self._lnn_trainer.start()

        self._last_pred_error: float = 0.0

    @property
    def active_inference(self) -> ActiveInferenceEngine:
        return self._active_inference

    @property
    def lnn_trainer(self) -> LNNTrainer:
        return self._lnn_trainer

    @property
    def last_pred_error(self) -> float:
        return self._last_pred_error

    def _execute_pipeline(
        self, input_text: str, call_id: str, t_start: float
    ) -> str:
        """
        Execute the 10-step inference-augmented pipeline.
        """
        # Step 1: Encode stimulus
        stimulus = self._stimulus_processor.encode(input_text)

        # Step 2: Capture state before and push stimulus
        pad_before = self._emotion_core.get_pad_state()
        h_before = self._emotion_core._h.copy()  # Step 2b: capture h_before
        self._emotion_core.push_stimulus(stimulus)

        # Step 3: Get current PAD and compute somatic markers
        pad = self._emotion_core.get_pad_state()
        h_after = self._emotion_core._h.copy()
        self._homeostatic_engine.record_input()
        markers = self._homeostatic_engine.compute_somatic_markers(pad)

        # Step 4: Compute behavioral constraints
        constraints = self._homeostatic_engine.compute_behavioral_constraints(
            markers, pad
        )

        # Step 4c: Active Inference step & LNN Experience Buffer push
        try:
            pred_err = self._active_inference.step(pad_before, pad)
            self._last_pred_error = pred_err
            if self._lnn_trainer.is_training_active():
                self._lnn_trainer.push_sample(stimulus, h_before, h_after)
        except Exception:
            logger.exception(
                "Active Inference step / LNN push failed (call_id=%s)", call_id
            )

        # Step 4b: Synergistic Ecphory Memory Query
        echo_vector: Optional[np.ndarray] = None
        try:
            traces = self._affective_memory.get_all_traces()
            echo_vector = self._ecphory_engine.query(pad, traces)
        except Exception:
            logger.exception("Ecphory query failed (call_id=%s)", call_id)

        # Step 5: Assemble Prompt
        prompt_or_err = self._prompt_assembler.assemble(
            somatic=markers,
            constraints=constraints,
            history=self._history,
            system_preamble=self._config.system_preamble,
            n_ctx=self._config.n_ctx,
            echo_vector=echo_vector,
        )
        if hasattr(prompt_or_err, "message"):  # AssemblyError
            logger.warning(
                "Orchestrator: prompt assembly failed (call_id=%s): %s",
                call_id,
                prompt_or_err,
            )
            return self._config.fallback_response

        prompt: str = str(prompt_or_err)

        # Step 6: Latency simulation
        delay_ms = min(constraints.latency_ms, 500.0)
        if delay_ms > 0:
            time.sleep(delay_ms / 1000.0)

        # Step 7: LLM Generation
        raw_response = self._llm_backend.generate(prompt, constraints)
        if raw_response is None:
            logger.warning("Orchestrator: LLM returned None (call_id=%s)", call_id)
            return self._config.fallback_response

        # Step 8: Boundary Layer Validation
        safe_response = self._boundary_layer.validate(raw_response)
        if safe_response.strip() == "[...]":
            safe_response = self._config.fallback_response

        # Step 9: Store new Memory Trace
        try:
            M = self._affective_memory._M
            if stimulus.shape[0] >= M:
                content = stimulus[:M].astype(np.float32)
            else:
                content = np.zeros(M, dtype=np.float32)
                content[: stimulus.shape[0]] = stimulus.astype(np.float32)
            content = np.clip(content, -1.0, 1.0)
            self._affective_memory.store(content, pad)
        except Exception:
            logger.exception("Affective memory store failed (call_id=%s)", call_id)

        # Append to conversation history
        self._history.append(("user", input_text))
        self._history.append(("assistant", safe_response))

        max_turns = self._config.max_history_turns * 2
        if len(self._history) > max_turns:
            self._history = self._history[-max_turns:]

        # Log call metadata
        logger.info(
            "Orchestrator call_id=%s t=%.3fs markers=%s constraints=%s pred_error=%.4f",
            call_id,
            time.monotonic() - t_start,
            markers,
            constraints,
            self._last_pred_error,
        )

        return safe_response

    def reset_lifecycle(self) -> None:
        """
        Extend MemoryAugmentedOrchestrator reset by resetting active inference and LNN trainer.
        """
        super().reset_lifecycle()
        self._last_pred_error = 0.0
        if hasattr(self, "_active_inference") and self._active_inference is not None:
            self._active_inference.reset()
        if hasattr(self, "_lnn_trainer") and self._lnn_trainer is not None:
            self._lnn_trainer.reset()

    def shutdown(self) -> None:
        """
        Cleanly stop LNN Trainer, Decay Engine, and Fast Loop threads.
        """
        if hasattr(self, "_lnn_trainer") and self._lnn_trainer is not None:
            self._lnn_trainer.stop()
        super().shutdown()
