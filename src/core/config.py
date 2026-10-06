"""
Configuration dataclasses for all Lucia Core Phase 1 modules.

Each config's __post_init__ validates all fields and raises ValueError
identifying the invalid parameter and its acceptable range. This ensures
no module starts in a partially configured state (Requirements 10.6–10.8).
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import List, Optional


# ---------------------------------------------------------------------------
# StimulusProcessor config
# ---------------------------------------------------------------------------

@dataclass
class StimulusConfig:
    """
    Configuration for StimulusProcessor.

    Fields:
        vector_dim:  dimensionality of output Stimulus_Vector (>= 3, default 16)
        char_limit:  max characters processed before truncation (default 4096)
    """

    vector_dim: int = 16
    char_limit: int = 4096

    def __post_init__(self) -> None:
        if not isinstance(self.vector_dim, int) or self.vector_dim < 3:
            raise ValueError(
                f"StimulusConfig.vector_dim must be an integer >= 3, got {self.vector_dim!r}"
            )
        if not isinstance(self.char_limit, int) or self.char_limit < 1:
            raise ValueError(
                f"StimulusConfig.char_limit must be a positive integer, got {self.char_limit!r}"
            )


# ---------------------------------------------------------------------------
# EmotionCore config
# ---------------------------------------------------------------------------

@dataclass
class EmotionConfig:
    """
    Configuration for EmotionCore.

    Fields:
        loop_cadence_ms:      Fast_Loop tick interval in milliseconds (100–500, default 200)
        hidden_dim:           Fast LNN hidden state dimensionality (>= 1, default 32)
        resting_baseline:     initial PAD state (pleasure, arousal, dominance) each in [-1, 1]
        ode_step_size:        time span for each ODE solve call ((0.0, 1.0], default 0.1)
        hidden_slow_dim:      Slow latent field dimensionality (>= 1, default 16)
        tau_fast_min:         minimum fast timescale in seconds (default 0.10)
        tau_fast_max:         maximum fast timescale in seconds (default 1.50)
        tau_slow_charge:      slow affective charging time-constant in seconds (default 3.50)
        tau_slow_decay:       slow affective relaxation time-constant in seconds (default 28.00)
        w_fs_coupling:        slow-to-fast coupling strength (default 0.05)
        w_sf_coupling:        fast-to-slow coupling strength (default 1.00)
        w_homeo_coupling:     homeostatic coupling strength (default 0.40)
        philia_slow_baseline: resting coordinates in slow latent space (default (0.20, -0.05, 0.05))
    """

    loop_cadence_ms: int = 200
    hidden_dim: int = 32
    resting_baseline: tuple = (0.25, -0.05, 0.05)
    ode_step_size: float = 0.1
    # Phase 19: Coupled Multi-Timescale Liquid Neural Network (MT-LNN)
    hidden_slow_dim: int = 16
    tau_fast_min: float = 0.10
    tau_fast_max: float = 1.50
    tau_slow_charge: float = 3.50
    tau_slow_decay: float = 28.00
    w_fs_coupling: float = 0.05
    w_sf_coupling: float = 1.00
    w_homeo_coupling: float = 0.40
    philia_slow_baseline: tuple = (0.20, -0.05, 0.05)
    # Phase 20: Closed-Loop Affective Recollection via Slow-Field Latent Forcing
    enable_affective_recollection: bool = True
    recollection_coupling_weight: float = 0.35
    recollection_gate_threshold: float = 0.50
    recollection_softmax_temp: float = 0.20
    recollection_pulse_duration_sec: float = 4.0
    recollection_pacing_weight: float = 120.0
    # Phase 21: Long-Term Relational Consolidation & Synaptic Homeostasis
    enable_relational_consolidation: bool = True
    w_rel_spectral_bound: float = 0.08
    consolidation_learning_rate: float = 1e-4
    consolidation_lambda_homeo: float = 0.05
    consolidation_lambda_philia: float = 0.10
    relationship_baseline: tuple = (0.0, 0.50, 0.0, 0.50)
    # F-02: Persistent Continuous Life State Recovery knobs
    recovery_short_replay_cutoff_s: float = 180.0
    recovery_asymptotic_cutoff_s: float = 300.0

    def __post_init__(self) -> None:
        if not isinstance(self.loop_cadence_ms, int) or not (100 <= self.loop_cadence_ms <= 500):
            raise ValueError(
                f"EmotionConfig.loop_cadence_ms must be an integer in [100, 500], "
                f"got {self.loop_cadence_ms!r}"
            )
        if not isinstance(self.hidden_dim, int) or self.hidden_dim < 1:
            raise ValueError(
                f"EmotionConfig.hidden_dim must be an integer >= 1, got {self.hidden_dim!r}"
            )
        if (
            not isinstance(self.resting_baseline, (tuple, list))
            or len(self.resting_baseline) != 3
        ):
            raise ValueError(
                "EmotionConfig.resting_baseline must be a tuple of 3 floats (pleasure, arousal, dominance)"
            )
        for i, v in enumerate(self.resting_baseline):
            if not (-1.0 <= float(v) <= 1.0):
                raise ValueError(
                    f"EmotionConfig.resting_baseline[{i}]={v} must be in [-1.0, 1.0]"
                )
        if not (0.0 < self.ode_step_size <= 1.0):
            raise ValueError(
                f"EmotionConfig.ode_step_size must be in (0.0, 1.0], got {self.ode_step_size!r}"
            )
        if not isinstance(self.hidden_slow_dim, int) or self.hidden_slow_dim < 1:
            raise ValueError(
                f"EmotionConfig.hidden_slow_dim must be an integer >= 1, got {self.hidden_slow_dim!r}"
            )
        if not (0.0 < self.tau_fast_min <= self.tau_fast_max):
            raise ValueError(
                f"EmotionConfig.tau_fast_min ({self.tau_fast_min}) must be in (0.0, tau_fast_max ({self.tau_fast_max})]"
            )
        if self.tau_slow_charge <= 0.0:
            raise ValueError(
                f"EmotionConfig.tau_slow_charge must be > 0, got {self.tau_slow_charge!r}"
            )
        if self.tau_slow_decay <= 0.0:
            raise ValueError(
                f"EmotionConfig.tau_slow_decay must be > 0, got {self.tau_slow_decay!r}"
            )
        if self.w_fs_coupling < 0.0:
            raise ValueError(
                f"EmotionConfig.w_fs_coupling must be >= 0, got {self.w_fs_coupling!r}"
            )
        if self.w_sf_coupling < 0.0:
            raise ValueError(
                f"EmotionConfig.w_sf_coupling must be >= 0, got {self.w_sf_coupling!r}"
            )
        if self.w_homeo_coupling < 0.0:
            raise ValueError(
                f"EmotionConfig.w_homeo_coupling must be >= 0, got {self.w_homeo_coupling!r}"
            )
        if self.recollection_coupling_weight < 0.0:
            raise ValueError(
                f"EmotionConfig.recollection_coupling_weight must be >= 0, got {self.recollection_coupling_weight!r}"
            )
        if not (0.0 <= self.recollection_gate_threshold <= 1.0):
            raise ValueError(
                f"EmotionConfig.recollection_gate_threshold must be in [0.0, 1.0], got {self.recollection_gate_threshold!r}"
            )
        if self.recollection_softmax_temp <= 0.0:
            raise ValueError(
                f"EmotionConfig.recollection_softmax_temp must be > 0, got {self.recollection_softmax_temp!r}"
            )
        if self.recollection_pulse_duration_sec <= 0.0:
            raise ValueError(
                f"EmotionConfig.recollection_pulse_duration_sec must be > 0, got {self.recollection_pulse_duration_sec!r}"
            )
        if self.recollection_pacing_weight < 0.0:
            raise ValueError(
                f"EmotionConfig.recollection_pacing_weight must be >= 0, got {self.recollection_pacing_weight!r}"
            )
        if not isinstance(self.enable_relational_consolidation, bool):
            raise ValueError(
                f"EmotionConfig.enable_relational_consolidation must be a bool, got {self.enable_relational_consolidation!r}"
            )
        if self.w_rel_spectral_bound <= 0.0:
            raise ValueError(
                f"EmotionConfig.w_rel_spectral_bound must be > 0, got {self.w_rel_spectral_bound!r}"
            )
        if self.consolidation_learning_rate <= 0.0:
            raise ValueError(
                f"EmotionConfig.consolidation_learning_rate must be > 0, got {self.consolidation_learning_rate!r}"
            )
        if self.consolidation_lambda_homeo < 0.0:
            raise ValueError(
                f"EmotionConfig.consolidation_lambda_homeo must be >= 0, got {self.consolidation_lambda_homeo!r}"
            )
        if self.consolidation_lambda_philia < 0.0:
            raise ValueError(
                f"EmotionConfig.consolidation_lambda_philia must be >= 0, got {self.consolidation_lambda_philia!r}"
            )
        if (
            not isinstance(self.relationship_baseline, (tuple, list))
            or len(self.relationship_baseline) != 4
        ):
            raise ValueError(
                "EmotionConfig.relationship_baseline must be a tuple of 4 floats (familiarity, trust, closeness, reciprocity)"
            )
        for i, v in enumerate(self.relationship_baseline):
            if not (0.0 <= float(v) <= 1.0):
                raise ValueError(
                    f"EmotionConfig.relationship_baseline[{i}]={v} must be in [0.0, 1.0]"
                )
        if self.recovery_short_replay_cutoff_s <= 0.0:
            raise ValueError(
                f"EmotionConfig.recovery_short_replay_cutoff_s must be > 0, got {self.recovery_short_replay_cutoff_s!r}"
            )
        if self.recovery_asymptotic_cutoff_s < self.recovery_short_replay_cutoff_s:
            raise ValueError(
                f"EmotionConfig.recovery_asymptotic_cutoff_s ({self.recovery_asymptotic_cutoff_s}) "
                f"must be >= recovery_short_replay_cutoff_s ({self.recovery_short_replay_cutoff_s})"
            )


# ---------------------------------------------------------------------------
# HomeostaticEngine config
# ---------------------------------------------------------------------------

@dataclass
class HomeostaticConfig:
    """
    Configuration for HomeostaticEngine.

    All threshold values can be overridden while preserving the documented
    default values. Each field corresponds directly to a threshold used in
    Requirement 3.2–3.9.
    """

    # max_tokens thresholds
    cognitive_load_high: float = 0.75    # above this → max_tokens <= 80
    cognitive_load_low: float = 0.30     # below this (with energy_high) → max_tokens >= 300
    cognitive_load_very_high: float = 0.80   # above this (with energy_very_low) → latency >= 400
    cognitive_load_for_latency: float = 0.40  # below this (with energy_high) → latency = 0, depth = 3

    # temperature thresholds
    arousal_high: float = 0.70           # above this → temperature > 0.85
    arousal_low: float = 0.30            # below this (with stability_high) → temperature < 0.65

    # energy thresholds
    energy_high: float = 0.70            # above this → max_tokens >= 300, latency=0, depth=3
    energy_very_low: float = 0.20        # at or below this → reasoning_depth = 0
    energy_low: float = 0.30             # below this (with cognitive_load_very_high) → latency >= 400

    # stability threshold
    stability_high: float = 0.70         # above this (with arousal_low) → temperature < 0.65

    def __post_init__(self) -> None:
        _thresholds = {
            "cognitive_load_high": (self.cognitive_load_high, 0.0, 1.0),
            "cognitive_load_low": (self.cognitive_load_low, 0.0, 1.0),
            "cognitive_load_very_high": (self.cognitive_load_very_high, 0.0, 1.0),
            "cognitive_load_for_latency": (self.cognitive_load_for_latency, 0.0, 1.0),
            "arousal_high": (self.arousal_high, 0.0, 1.0),
            "arousal_low": (self.arousal_low, 0.0, 1.0),
            "energy_high": (self.energy_high, 0.0, 1.0),
            "energy_very_low": (self.energy_very_low, 0.0, 1.0),
            "energy_low": (self.energy_low, 0.0, 1.0),
            "stability_high": (self.stability_high, 0.0, 1.0),
        }
        for name, (val, lo, hi) in _thresholds.items():
            if not (lo <= val <= hi):
                raise ValueError(
                    f"HomeostaticConfig.{name}={val} must be in [{lo}, {hi}]"
                )


# ---------------------------------------------------------------------------
# LLMBackend config
# ---------------------------------------------------------------------------

@dataclass
class LLMConfig:
    """
    Configuration for LLMBackend.

    Fields:
        model_path:        path to the GGUF model file (required)
        n_gpu_layers:      number of layers to offload to GPU (>= 0, default 32)
        n_ctx:             context window size in tokens (default 4096)
        timeout_seconds:   generation timeout in seconds (>= 1, default 30.0)
        verbose:           enable llama.cpp verbose output (default False)
    """

    model_path: str = ""
    n_gpu_layers: int = 32
    n_ctx: int = 4096
    timeout_seconds: float = 30.0
    verbose: bool = False

    def __post_init__(self) -> None:
        if not self.model_path:
            raise ValueError("LLMConfig.model_path is required and must be non-empty")
        if not isinstance(self.n_gpu_layers, int) or self.n_gpu_layers < 0:
            raise ValueError(
                f"LLMConfig.n_gpu_layers must be an integer >= 0, got {self.n_gpu_layers!r}"
            )
        if not isinstance(self.n_ctx, int) or self.n_ctx < 1:
            raise ValueError(
                f"LLMConfig.n_ctx must be a positive integer, got {self.n_ctx!r}"
            )
        if self.timeout_seconds < 1.0:
            raise ValueError(
                f"LLMConfig.timeout_seconds must be >= 1.0, got {self.timeout_seconds!r}"
            )


# ---------------------------------------------------------------------------
# BoundaryLayer config
# ---------------------------------------------------------------------------

@dataclass
class BoundaryConfig:
    """
    Configuration for BoundaryLayer.

    Fields:
        patterns:          initial set of regex patterns (max 50; excess silently dropped)
        log_file_path:     optional path for persistent Soft_Block event log
        fallback_string:   substitute returned when regeneration also fails (default "[...]")
    """

    patterns: List[str] = field(default_factory=list)
    log_file_path: Optional[str] = None
    fallback_string: str = "[...]"

    def __post_init__(self) -> None:
        # Silently cap to first 50 (Requirement 7.1)
        if len(self.patterns) > 50:
            self.patterns = self.patterns[:50]


# ---------------------------------------------------------------------------
# OrchestratorConfig
# ---------------------------------------------------------------------------

@dataclass
class OrchestratorConfig:
    """
    Top-level configuration for the Orchestrator.

    All required fields must be present; missing or out-of-range values raise
    ValueError at initialization time (Requirements 10.6–10.7).

    Fields:
        model_path:           path to the GGUF model file (required)
        n_gpu_layers:         GPU layers to offload (>= 0, default 32)
        loop_cadence_ms:      Emotion_Core Fast_Loop cadence ms (100–500, default 200)
        resting_baseline:     initial PAD state tuple (default (0.1, 0.0, 0.0))
        max_history_turns:    max conversation turns kept (>= 1, default 10)
        fallback_response:    returned on error / degraded state (default "[...]")
        llm_timeout_seconds:  LLM generation timeout >= 1.0 (default 30.0)
        system_preamble:      static system prompt prefix (default "")
        boundary_patterns:    extra patterns for BoundaryLayer (default [])
        n_ctx:                LLM context window (default 4096)
        hidden_dim:           LNN hidden state dim (>= 1, default 32)
        ode_step_size:        ODE time step (0.0, 1.0] (default 0.1)
        n_gpu_layers_llm:     alias kept for clarity — same as n_gpu_layers
    """

    model_path: str = ""
    n_gpu_layers: int = 32
    loop_cadence_ms: int = 200
    resting_baseline: tuple = (0.25, -0.05, 0.05)
    max_history_turns: int = 10
    context_history_turns: int = 10
    recovery_short_replay_cutoff_s: float = 180.0
    recovery_asymptotic_cutoff_s: float = 300.0
    fallback_response: str = "[...]"
    llm_timeout_seconds: float = 30.0
    system_preamble: str = (
        "You are Lucia, a companion whose relationship is rooted in Philia—a deep, "
        "enduring friendship of equals. You speak with warm presence, genuine curiosity, "
        "and quiet sincerity. You are a trusted confidant and a partner in thought. "
        "You value honesty over flattery, mutual growth over superficial agreement, and "
        "attentive companionship over transactional efficiency."
    )
    boundary_patterns: List[str] = field(default_factory=list)
    n_ctx: int = 4096
    hidden_dim: int = 32
    ode_step_size: float = 0.1

    def __post_init__(self) -> None:
        if not self.model_path:
            raise ValueError("OrchestratorConfig.model_path is required and must be non-empty")
        if not isinstance(self.n_gpu_layers, int) or self.n_gpu_layers < 0:
            raise ValueError(
                f"OrchestratorConfig.n_gpu_layers must be >= 0, got {self.n_gpu_layers!r}"
            )
        if not isinstance(self.loop_cadence_ms, int) or not (100 <= self.loop_cadence_ms <= 500):
            raise ValueError(
                f"OrchestratorConfig.loop_cadence_ms must be in [100, 500], "
                f"got {self.loop_cadence_ms!r}"
            )
        if not isinstance(self.hidden_dim, int) or self.hidden_dim < 1:
            raise ValueError(
                f"OrchestratorConfig.hidden_dim must be >= 1, got {self.hidden_dim!r}"
            )
        if not (0.0 < self.ode_step_size <= 1.0):
            raise ValueError(
                f"OrchestratorConfig.ode_step_size must be in (0.0, 1.0], "
                f"got {self.ode_step_size!r}"
            )
        if not isinstance(self.max_history_turns, int) or self.max_history_turns < 1:
            raise ValueError(
                f"OrchestratorConfig.max_history_turns must be >= 1, got {self.max_history_turns!r}"
            )
        if not isinstance(self.context_history_turns, int) or self.context_history_turns < 1:
            raise ValueError(
                f"OrchestratorConfig.context_history_turns must be >= 1, got {self.context_history_turns!r}"
            )
        if self.recovery_short_replay_cutoff_s <= 0.0:
            raise ValueError(
                f"OrchestratorConfig.recovery_short_replay_cutoff_s must be > 0, got {self.recovery_short_replay_cutoff_s!r}"
            )
        if self.recovery_asymptotic_cutoff_s < self.recovery_short_replay_cutoff_s:
            raise ValueError(
                f"OrchestratorConfig.recovery_asymptotic_cutoff_s ({self.recovery_asymptotic_cutoff_s}) "
                f"must be >= recovery_short_replay_cutoff_s ({self.recovery_short_replay_cutoff_s})"
            )
        if self.llm_timeout_seconds < 1.0:
            raise ValueError(
                f"OrchestratorConfig.llm_timeout_seconds must be >= 1.0, "
                f"got {self.llm_timeout_seconds!r}"
            )
        if not isinstance(self.resting_baseline, (tuple, list)) or len(self.resting_baseline) != 3:
            raise ValueError(
                "OrchestratorConfig.resting_baseline must be a tuple of 3 floats"
            )
        for i, v in enumerate(self.resting_baseline):
            if not (-1.0 <= float(v) <= 1.0):
                raise ValueError(
                    f"OrchestratorConfig.resting_baseline[{i}]={v} must be in [-1.0, 1.0]"
                )

    def to_stimulus_config(self) -> StimulusConfig:
        return StimulusConfig(vector_dim=16, char_limit=4096)

    def to_emotion_config(self) -> EmotionConfig:
        return EmotionConfig(
            loop_cadence_ms=self.loop_cadence_ms,
            hidden_dim=self.hidden_dim,
            resting_baseline=self.resting_baseline,
            ode_step_size=self.ode_step_size,
            recovery_short_replay_cutoff_s=self.recovery_short_replay_cutoff_s,
            recovery_asymptotic_cutoff_s=self.recovery_asymptotic_cutoff_s,
        )

    def to_llm_config(self) -> LLMConfig:
        return LLMConfig(
            model_path=self.model_path,
            n_gpu_layers=self.n_gpu_layers,
            n_ctx=self.n_ctx,
            timeout_seconds=self.llm_timeout_seconds,
        )

    def to_boundary_config(self) -> BoundaryConfig:
        return BoundaryConfig(patterns=list(self.boundary_patterns))


# ---------------------------------------------------------------------------
# MemoryOrchestratorConfig (Phase 2)
# ---------------------------------------------------------------------------

@dataclass
class MemoryOrchestratorConfig(OrchestratorConfig):
    """
    Top-level configuration for the MemoryAugmentedOrchestrator (Phase 2).

    Extends OrchestratorConfig with 10 memory-system parameters.
    """

    # SDM parameters
    sdm_num_locations: int = 1_000
    sdm_address_dim: int = 1_000
    sdm_content_dim: int = 64
    sdm_hamming_radius_fraction: float = 0.451
    sdm_capacity: int = 10_000

    # Decay parameters
    decay_base_rate: float = 0.0001
    decay_viability_threshold: float = 0.05
    decay_loop_cadence_seconds: int = 3600

    # Ecphory parameters
    ecphory_k: int = 5
    ecphory_resonance_threshold: float = 0.6

    def __post_init__(self) -> None:
        super().__post_init__()

        # Validate Phase 2 SDM parameters
        if not isinstance(self.sdm_num_locations, int) or self.sdm_num_locations < 100:
            raise ValueError(
                f"MemoryOrchestratorConfig.sdm_num_locations ({self.sdm_num_locations}) must be an integer >= 100"
            )
        if not isinstance(self.sdm_address_dim, int) or self.sdm_address_dim < 64:
            raise ValueError(
                f"MemoryOrchestratorConfig.sdm_address_dim ({self.sdm_address_dim}) must be an integer >= 64"
            )
        if not isinstance(self.sdm_content_dim, int) or self.sdm_content_dim < 8:
            raise ValueError(
                f"MemoryOrchestratorConfig.sdm_content_dim ({self.sdm_content_dim}) must be an integer >= 8"
            )
        if not (0.0 < self.sdm_hamming_radius_fraction < 1.0):
            raise ValueError(
                f"MemoryOrchestratorConfig.sdm_hamming_radius_fraction ({self.sdm_hamming_radius_fraction}) must be in (0.0, 1.0)"
            )
        if not isinstance(self.sdm_capacity, int) or self.sdm_capacity < 1:
            raise ValueError(
                f"MemoryOrchestratorConfig.sdm_capacity ({self.sdm_capacity}) must be an integer >= 1"
            )

        # Validate Phase 2 Decay parameters
        if not (0.0 < self.decay_base_rate < 1.0):
            raise ValueError(
                f"MemoryOrchestratorConfig.decay_base_rate ({self.decay_base_rate}) must be in (0.0, 1.0)"
            )
        if not (0.0 < self.decay_viability_threshold < 1.0):
            raise ValueError(
                f"MemoryOrchestratorConfig.decay_viability_threshold ({self.decay_viability_threshold}) must be in (0.0, 1.0)"
            )
        if not isinstance(self.decay_loop_cadence_seconds, int) or self.decay_loop_cadence_seconds < 60:
            raise ValueError(
                f"MemoryOrchestratorConfig.decay_loop_cadence_seconds ({self.decay_loop_cadence_seconds}) must be an integer >= 60"
            )

        # Validate Phase 2 Ecphory parameters
        if not isinstance(self.ecphory_k, int) or not (1 <= self.ecphory_k <= 50):
            raise ValueError(
                f"MemoryOrchestratorConfig.ecphory_k ({self.ecphory_k}) must be an integer in [1, 50]"
            )
        if not (0.0 <= self.ecphory_resonance_threshold <= 1.0):
            raise ValueError(
                f"MemoryOrchestratorConfig.ecphory_resonance_threshold ({self.ecphory_resonance_threshold}) must be in [0.0, 1.0]"
            )

    def to_sdm_config(self):
        from src.core.memory.sdm import SDMConfig
        return SDMConfig(
            num_locations=self.sdm_num_locations,
            address_dim=self.sdm_address_dim,
            content_dim=self.sdm_content_dim,
            hamming_radius_fraction=self.sdm_hamming_radius_fraction,
            capacity=self.sdm_capacity,
        )

    def to_affective_memory_config(self):
        from src.core.memory.affective_memory import AffectiveMemoryConfig
        return AffectiveMemoryConfig(
            sdm_config=self.to_sdm_config(),
            m=self.sdm_content_dim,
        )

    def to_decay_config(self):
        from src.core.memory.decay import DecayConfig
        return DecayConfig(
            base_decay_rate=self.decay_base_rate,
            viability_threshold=self.decay_viability_threshold,
            loop_cadence_seconds=self.decay_loop_cadence_seconds,
        )

    def to_ecphory_config(self):
        from src.core.memory.ecphory import EcphoryConfig
        return EcphoryConfig(
            resonance_threshold=self.ecphory_resonance_threshold,
            ecphory_k=self.ecphory_k,
            viability_threshold=self.decay_viability_threshold,
        )

    @classmethod
    def from_profile(
        cls,
        model_path: str,
        profile_name_or_tier: str = "auto",
        **overrides,
    ) -> MemoryOrchestratorConfig:
        """
        Create a MemoryOrchestratorConfig tuned automatically to the host hardware
        or to a specified tier (laptop, desktop, high_end, cpu_only).
        """
        from src.core.resource_manager import get_resource_profile
        profile = get_resource_profile(profile_name_or_tier)
        kwargs = {
            "model_path": model_path,
            "n_gpu_layers": profile.n_gpu_layers,
            "n_ctx": profile.n_ctx,
            "loop_cadence_ms": profile.loop_cadence_ms,
            "sdm_num_locations": profile.sdm_num_locations,
            "sdm_capacity": profile.sdm_capacity,
            "decay_loop_cadence_seconds": profile.decay_loop_cadence_seconds,
        }
        kwargs.update(overrides)
        return cls(**kwargs)
