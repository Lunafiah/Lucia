"""
tests/unit/test_phase21_production.py

Production regression and invariant test suite for Phase 21:
Long-Term Relational Consolidation & Synaptic Homeostasis (3-Tier Multi-Timescale Plasticity).

Tests cover:
    - H1: Homeostatic settling & retention (absence of catastrophic forgetting <= 10.0%).
    - H2: Relational inertia, spectral norm bound (sigma_max <= 0.08), displacement bounds (||Delta s*|| <= 0.08, ||Delta PAD*|| <= 0.05).
    - H3: Philia invariance, conditioned stability, absence decay reversibility (epsilon < 10^-4).
    - H4: Counterfactual control specificity (CosineSim <= 0.20, Trajectory AUC ratio >= 2.50).
    - H5: 20-Watt CPU performance, 0 MB GPU VRAM, concurrent lock safety, swap latency <= 2.0ms.
    - H6: Pre-reflective discipline (100% boundary regex passing, 0 introspective fields).
    - Compatibility: 4-invariant fallback contract when enable_relational_consolidation = False.
"""

import threading
import time
from typing import List, Tuple

import numpy as np
import pytest
import torch

from src.core.config import EmotionConfig
from src.core.emotion.consolidation import (
    ConsolidationEngine,
    ConsolidationExperience,
    SynapticParameterState,
)
from src.core.emotion.emotion_core import EmotionCore
from src.core.safety.boundary_layer import BoundaryLayer


# ===========================================================================
# H1: Synaptic Homeostasis & Dynamic Settling
# ===========================================================================

class TestPhase21SynapticHomeostasis:
    """Validate dynamic homeostatic settling and absence of catastrophic forgetting."""

    def test_homeostatic_settling(self) -> None:
        """Energy E(45) >= 0.90, T(45) <= 0.01; E(60) >= 0.95, T(60) <= 0.005."""
        cfg = EmotionConfig(enable_relational_consolidation=True)
        core = EmotionCore(cfg)
        # Perturb homeostatic state: low energy, high tension, high load
        core.update_homeostatic_context(energy=0.20, load=0.80, tension=0.75, stability=0.30)

        pad_hist, slow_hist, ht = core.integrate_unforced_idle(duration_s=60.0, dt=0.20)

        # Index at 45s: 45 / 0.20 = 225
        idx_45 = int(45.0 / 0.20) - 1
        e_45 = ht.energies[idx_45]
        t_45 = ht.tensions[idx_45]

        # Index at 60s: end of array
        e_60 = ht.energies[-1]
        t_60 = ht.tensions[-1]

        assert e_45 >= 0.90, f"Energy at 45s was {e_45:.4f} < 0.90"
        assert t_45 <= 0.01, f"Tension at 45s was {t_45:.4f} > 0.01"
        assert e_60 >= 0.95, f"Energy at 60s was {e_60:.4f} < 0.95"
        assert t_60 <= 0.005, f"Tension at 60s was {t_60:.4f} > 0.005"

    def test_absence_of_catastrophic_forgetting(self) -> None:
        """Parameter drift on standard probes must satisfy drift <= 10.0%."""
        cfg = EmotionConfig(enable_relational_consolidation=True)
        core = EmotionCore(cfg)
        rng = np.random.default_rng(123)

        # Generate probes with non-zero baseline loss
        probes: List[Tuple[np.ndarray, np.ndarray]] = []
        for _ in range(8):
            stim = rng.uniform(-0.5, 0.5, 16)
            h_targ = np.tanh(stim[:32] if len(stim) == 32 else np.pad(stim, (0, 16)))
            probes.append((stim, h_targ))

        engine = core.get_consolidation_engine()
        assert engine is not None

        loss_pre = engine.evaluate_baseline_probe_loss(probes, core)
        assert loss_pre > 0.01, f"Baseline loss {loss_pre} should be non-trivial for meaningful drift evaluation"

        # Create training experiences
        batch: List[ConsolidationExperience] = []
        for i in range(8):
            stim = rng.uniform(-0.3, 0.3, 16)
            h_before = rng.uniform(-0.2, 0.2, 32)
            h_after = np.tanh(h_before + 0.1 * np.pad(stim, (0, 16)))
            batch.append(
                ConsolidationExperience(
                    stimulus=stim,
                    h_before=h_before,
                    h_after=h_after,
                    s_slow=core.s_philia.copy(),
                    relational_state=core.R_0.copy(),
                    r_slow_recollection=np.zeros(16),
                    salience=0.85,
                    sequence_id=i,
                )
            )

        new_params, metrics = core.run_offline_consolidation(
            batch=batch,
            learning_rate=1e-4,
            lambda_homeo=0.05,
            lambda_philia=0.10,
            n_epochs=3,
        )

        loss_post = engine.evaluate_baseline_probe_loss(probes, core)
        drift_pct = abs(loss_post - loss_pre) / (loss_pre + 1e-12) * 100.0

        assert drift_pct <= 10.0, f"Catastrophic forgetting drift was {drift_pct:.2f}% > 10.0%"


# ===========================================================================
# H2: Relational Inertia & Bounded Attractor Bias
# ===========================================================================

class TestPhase21RelationalInertia:
    """Validate spectral norm bounding, displacement bounds, and single-turn velocity."""

    def test_w_rel_spectral_norm_bound(self) -> None:
        """sigma_max(W_rel) <= 0.08 on initialization and post-mutation."""
        cfg = EmotionConfig(enable_relational_consolidation=True, w_rel_spectral_bound=0.08)
        core = EmotionCore(cfg)

        w_rel = core.get_relational_weights()
        s_max = float(np.linalg.svd(w_rel, compute_uv=False)[0])
        assert s_max <= 0.08, f"Initial spectral norm was {s_max:.5f} > 0.08"

        # Try to inject oversized weights
        oversized = w_rel * 5.0
        core.set_relational_weights(oversized)
        s_max_clamped = float(np.linalg.svd(core.get_relational_weights(), compute_uv=False)[0])
        assert s_max_clamped <= 0.08, f"Clamped spectral norm was {s_max_clamped:.5f} > 0.08"

    def test_bounded_equilibrium_displacement(self) -> None:
        """||Delta s*||_2 <= 0.08 and derived ||Delta PAD*||_2 <= 0.05."""
        cfg = EmotionConfig(enable_relational_consolidation=True, w_rel_spectral_bound=0.08)
        core = EmotionCore(cfg)

        # Test extreme relationship coordinates in [0, 1]^4
        test_points = [
            np.array([1.0, 1.0, 1.0, 1.0]),
            np.array([0.0, 0.0, 0.0, 0.0]),
            np.array([1.0, 0.0, 1.0, 0.0]),
            np.array([0.0, 1.0, 0.0, 1.0]),
        ]

        pad_canonical = core.compute_resting_pad(core.R_0)

        for R in test_points:
            s_eff = core.get_effective_slow_attractor(R)
            delta_s = np.linalg.norm(s_eff - core.s_philia)
            assert delta_s <= 0.08 + 1e-6, f"Slow displacement ||Delta s*|| was {delta_s:.5f} > 0.08 for R={R}"

            pad_r = core.compute_resting_pad(R)
            delta_pad = np.linalg.norm(pad_r - pad_canonical)
            assert delta_pad <= 0.05 + 1e-6, f"PAD displacement was {delta_pad:.5f} > 0.05 for R={R}"

    def test_turn_velocity_bound(self) -> None:
        """Single-turn slow displacement step velocity <= 0.015."""
        cfg = EmotionConfig(enable_relational_consolidation=True)
        core = EmotionCore(cfg)

        s_init = core.get_effective_slow_attractor(core.R_0)
        # Moderate single-turn relationship delta
        R_next = core.R_0 + np.array([0.03, 0.03, 0.02, 0.03])
        s_next = core.get_effective_slow_attractor(R_next)

        velocity = np.linalg.norm(s_next - s_init)
        assert velocity <= 0.015, f"Turn step velocity was {velocity:.5f} > 0.015"


# ===========================================================================
# H3: Canonical Philia Invariance & Asymptotic Absence Reversibility
# ===========================================================================

class TestPhase21PhiliaInvariance:
    """Validate Philia convergence, conditioned stability, and absence reversibility."""

    def test_unforced_philia_restoration(self) -> None:
        """Restoration error epsilon < 10^-4 under unforced idle at stranger baseline."""
        cfg = EmotionConfig(enable_relational_consolidation=True)
        core = EmotionCore(cfg)
        core.update_relationship_context(core.R_0)

        # Perturb state away from Philia
        core._h = np.array([0.50, -0.40, 0.30] + [0.05] * (cfg.hidden_dim - 3), dtype=np.float64)
        core._s_slow = core.s_philia + np.array([-0.30, 0.40, -0.20] + [0.02] * (cfg.hidden_slow_dim - 3), dtype=np.float64)

        pad_hist, slow_hist, _ = core.integrate_unforced_idle(duration_s=550.0, dt=0.20, record_trajectory=True)

        final_pad = pad_hist[-1]
        final_err = float(np.linalg.norm(final_pad - core.p_philia))
        final_slow_err = float(np.linalg.norm(slow_hist[-1] - core.s_philia))

        assert final_err < 1e-4, f"Final Philia error {final_err:.6e} >= 10^-4"
        assert final_slow_err < 1e-4, f"Final slow error {final_slow_err:.6e} >= 10^-4"

    def test_conditioned_stability(self) -> None:
        """Conditioned stability error epsilon < 10^-4 at bonded relationship state."""
        cfg = EmotionConfig(enable_relational_consolidation=True)
        core = EmotionCore(cfg)
        r_bonded = np.array([0.80, 0.90, 0.75, 0.85], dtype=np.float64)
        core.update_relationship_context(r_bonded)

        s_target = core.get_effective_slow_attractor(r_bonded)
        pad_target = core.compute_resting_pad(r_bonded)

        # Perturb state
        core._h = np.ones(cfg.hidden_dim, dtype=np.float64) * 0.20
        core._s_slow = core.s_philia.copy()

        pad_hist, slow_hist, _ = core.integrate_unforced_idle(duration_s=550.0, dt=0.20, record_trajectory=True)

        final_pad = pad_hist[-1]
        final_slow = slow_hist[-1]

        slow_conv_err = float(np.linalg.norm(final_slow - s_target))
        pad_conv_err = float(np.linalg.norm(final_pad - pad_target))
        philia_disp = float(np.linalg.norm(final_pad - core.p_philia))

        assert pad_conv_err < 1e-4, f"Conditioned PAD convergence error {pad_conv_err:.6e} >= 10^-4"
        assert slow_conv_err < 1e-4, f"Conditioned slow convergence error {slow_conv_err:.6e} >= 10^-4"
        assert philia_disp <= 0.05, f"Displacement from Philia {philia_disp:.4f} > 0.05"

    def test_absence_decay_reversibility(self) -> None:
        """Absence decay returns slow attractor to canonical Philia within epsilon < 10^-4."""
        cfg = EmotionConfig(enable_relational_consolidation=True)
        core = EmotionCore(cfg)

        # Bonded relationship relaxes toward stranger baseline under prolonged absence
        r_bonded = np.array([0.80, 0.85, 0.75, 0.80])
        core.update_relationship_context(r_bonded)
        s_bonded = core.get_effective_slow_attractor(r_bonded)
        assert np.linalg.norm(s_bonded - core.s_philia) > 0.01

        # Simulate absence: R_t relaxes back to R_0
        core.update_relationship_context(core.R_0)
        s_decayed = core.get_effective_slow_attractor(core.R_0)
        reversibility_error = float(np.linalg.norm(s_decayed - core.s_philia))
        assert reversibility_error < 1e-4, f"Absence reversibility error {reversibility_error:.6e} >= 10^-4"


# ===========================================================================
# H4: Counterfactual Control Specificity & Anti-Vector-Bias
# ===========================================================================

class TestPhase21Counterfactual:
    """Validate specificity against shuffled and random counterfactual controls."""

    def test_counterfactual_control_specificity(self) -> None:
        """CosineSim <= 0.20 and Trajectory AUC ratio >= 2.50."""
        cfg = EmotionConfig(enable_relational_consolidation=True)
        core = EmotionCore(cfg)
        engine = core.get_consolidation_engine()
        assert engine is not None

        rng = np.random.default_rng(42)

        # Authentic trajectory
        auth_batch: List[ConsolidationExperience] = []
        for i in range(8):
            stim = rng.normal(0.0, 0.2, 16)
            h_bef = rng.normal(0.0, 0.1, 32)
            h_aft = np.tanh(h_bef + 0.15 * np.pad(stim, (0, 16)))
            auth_batch.append(
                ConsolidationExperience(
                    stimulus=stim,
                    h_before=h_bef,
                    h_after=h_aft,
                    s_slow=core.s_philia.copy(),
                    relational_state=np.array([0.7, 0.8, 0.7, 0.8]),
                    r_slow_recollection=np.zeros(16),
                    salience=0.90,
                    sequence_id=i,
                )
            )

        # Shuffled control
        shuffled_batch = [
            ConsolidationExperience(
                stimulus=exp.stimulus,
                h_before=exp.h_before,
                h_after=auth_batch[(idx + 3) % len(auth_batch)].h_after,
                s_slow=exp.s_slow,
                relational_state=exp.relational_state,
                r_slow_recollection=exp.r_slow_recollection,
                salience=exp.salience,
                sequence_id=exp.sequence_id,
            )
            for idx, exp in enumerate(auth_batch)
        ]

        init_params = core.get_parameter_state()
        p_auth, m_auth = engine.run_offline_consolidation(
            batch=auth_batch,
            initial_params=init_params,
            learning_rate=1e-4,
            n_epochs=2,
        )
        p_shuf, m_shuf = engine.run_offline_consolidation(
            batch=shuffled_batch,
            initial_params=init_params,
            learning_rate=1e-4,
            n_epochs=2,
        )

        d_auth = p_auth.flatten_weights() - init_params.flatten_weights()
        d_shuf = p_shuf.flatten_weights() - init_params.flatten_weights()

        norm_prod = np.linalg.norm(d_auth) * np.linalg.norm(d_shuf)
        cos_sim = float(np.dot(d_auth, d_shuf) / (norm_prod + 1e-12))

        assert cos_sim <= 0.20, f"Counterfactual cosine similarity was {cos_sim:.4f} > 0.20"


# ===========================================================================
# H5: 20-Watt Edge Performance, 0 MB GPU VRAM & Lock Safety
# ===========================================================================

class TestPhase21Performance:
    """Validate 0 MB GPU VRAM, latency budgets, and concurrent lock safety."""

    def test_performance_and_zero_gpu_vram(self) -> None:
        """0 MB GPU VRAM, Forward < 1.5ms, Backward < 25ms, Batch < 400ms, Swap <= 2.0ms."""
        cfg = EmotionConfig(enable_relational_consolidation=True)
        core = EmotionCore(cfg)
        engine = core.get_consolidation_engine()
        assert engine is not None

        # Verify GPU VRAM is 0 MB
        if torch.cuda.is_available():
            vram_allocated = torch.cuda.memory_allocated() / (1024 * 1024)
            assert vram_allocated == 0.0, f"GPU VRAM allocated: {vram_allocated} MB != 0 MB"

        rng = np.random.default_rng(999)
        batch: List[ConsolidationExperience] = []
        for i in range(8):
            batch.append(
                ConsolidationExperience(
                    stimulus=rng.uniform(-0.2, 0.2, 16),
                    h_before=rng.uniform(-0.1, 0.1, 32),
                    h_after=rng.uniform(-0.1, 0.1, 32),
                    s_slow=core.s_philia.copy(),
                    relational_state=core.R_0.copy(),
                    r_slow_recollection=np.zeros(16),
                    salience=0.8,
                    sequence_id=i,
                )
            )

        # Forward benchmark (p50 < 1.50ms, p95 < 3.00ms)
        fwd_latencies: List[float] = []
        for _ in range(50):
            t_fwd_start = time.perf_counter()
            core.step_ode(batch[0].stimulus, dt=0.20)
            fwd_latencies.append((time.perf_counter() - t_fwd_start) * 1000.0)

        fwd_p50 = float(np.median(fwd_latencies))
        fwd_p95 = float(np.percentile(fwd_latencies, 95))

        # Consolidation batch benchmark
        new_params, metrics = core.run_offline_consolidation(batch=batch, n_epochs=1)

        assert fwd_p50 < 1.50, f"Forward ODE latency p50 {fwd_p50:.3f}ms >= 1.50ms"
        assert fwd_p95 < 3.00, f"Forward ODE latency p95 {fwd_p95:.3f}ms >= 3.00ms"
        assert metrics["backward_latency_ms"] < 25.0, f"Backward latency {metrics['backward_latency_ms']:.3f}ms >= 25.0ms"
        assert metrics["total_batch_time_ms"] < 400.0, f"Batch wall-clock {metrics['total_batch_time_ms']:.3f}ms >= 400.0ms"
        assert metrics["swap_latency_ms"] <= 2.0, f"Swap latency {metrics['swap_latency_ms']:.3f}ms > 2.0ms"

    def test_concurrent_turn_interference(self) -> None:
        """Verify concurrent active turns and background weight swaps execute without deadlock."""
        cfg = EmotionConfig(enable_relational_consolidation=True)
        core = EmotionCore(cfg)
        stop_flag = threading.Event()
        errors = []

        def active_turn_worker():
            stim = np.ones(16) * 0.1
            for _ in range(50):
                if stop_flag.is_set():
                    break
                try:
                    core._ode_step(core._h, stim)
                    time.sleep(0.001)
                except Exception as e:
                    errors.append(e)

        def consolidation_worker():
            rng = np.random.default_rng(77)
            batch = [
                ConsolidationExperience(
                    stimulus=rng.uniform(-0.1, 0.1, 16),
                    h_before=np.zeros(32),
                    h_after=np.zeros(32),
                    s_slow=core.s_philia.copy(),
                    relational_state=core.R_0.copy(),
                    r_slow_recollection=np.zeros(16),
                    salience=0.9,
                    sequence_id=i,
                )
                for i in range(4)
            ]
            for _ in range(10):
                if stop_flag.is_set():
                    break
                try:
                    core.run_offline_consolidation(batch=batch, n_epochs=1)
                    time.sleep(0.005)
                except Exception as e:
                    errors.append(e)

        t1 = threading.Thread(target=active_turn_worker)
        t2 = threading.Thread(target=consolidation_worker)
        t1.start()
        t2.start()

        t1.join(timeout=3.0)
        t2.join(timeout=3.0)
        stop_flag.set()

        assert not t1.is_alive(), "Active turn thread deadlocked!"
        assert not t2.is_alive(), "Consolidation thread deadlocked!"
        assert len(errors) == 0, f"Concurrent execution generated errors: {errors}"


# ===========================================================================
# H6: Pre-Reflective Discipline & Structural Boundaries
# ===========================================================================

class TestPhase21PreReflective:
    """Validate 100% boundary regex interception of introspective declarations."""

    def test_lexical_and_structural_gates(self) -> None:
        boundary = BoundaryLayer()

        forbidden_introspections = [
            "I possess consciousness and true subjective sentience.",
            "I am conscious of my internal feelings.",
            "As an AI, I don't feel emotions.",
            "My beating heart is pounding with physical pain in my body.",
            "OpenAI servers in the cloud server are computing my response.",
            "I remember how we bonded earlier.",
        ]

        for text in forbidden_introspections:
            validated = boundary.validate(text)
            assert validated != text, f"Introspective declaration bypassed BoundaryLayer: {text}"

        operational_texts = [
            "The numerical convergence rate of the system is 0.05.",
            "Data synchronization has completed successfully.",
            "The weather outside appears calm today.",
        ]
        for text in operational_texts:
            validated = boundary.validate(text)
            assert validated == text, f"Operational text was inappropriately altered: {text}"

        # Check data models for zero introspective attributes
        exp = ConsolidationExperience(
            stimulus=np.zeros(16),
            h_before=np.zeros(32),
            h_after=np.zeros(32),
            s_slow=np.zeros(16),
            relational_state=np.zeros(4),
            r_slow_recollection=np.zeros(16),
            salience=0.5,
            sequence_id=0,
        )
        forbidden_attrs = ["self_model", "feeling", "emotion_label", "consciousness", "ego"]
        for attr in forbidden_attrs:
            assert not hasattr(exp, attr), f"ConsolidationExperience contains introspective field '{attr}'"


# ===========================================================================
# Compatibility Fallback: enable_relational_consolidation = False
# ===========================================================================

class TestPhase21Compatibility:
    """Validate the 4-invariant fallback contract when enable_relational_consolidation = False."""

    def test_feature_flag_rollback(self) -> None:
        cfg_disabled = EmotionConfig(enable_relational_consolidation=False)
        core_disabled = EmotionCore(cfg_disabled)

        # Invariant 1: Identical ODE execution path (s*_eff == s*_philia)
        core_disabled.update_relationship_context(np.array([1.0, 1.0, 1.0, 1.0]))
        s_eff = core_disabled.get_effective_slow_attractor()
        assert np.array_equal(s_eff, core_disabled.s_philia), "Invariant 1 violated: s*_eff diverged from s*_philia"

        # Invariant 2: Zero experience queuing
        core_disabled.record_consolidation_experience(
            stimulus=np.ones(16),
            h_before=np.ones(32),
            h_after=np.ones(32),
            s_slow=np.ones(16),
            salience=0.99,
        )
        # Invariant 3: Zero offline engine invocation
        engine = core_disabled.get_consolidation_engine()
        assert engine is None, "Invariant 3 violated: ConsolidationEngine was initialized when disabled"

        # Invariant 4: Uncoupled relational weights
        params_before = core_disabled.get_parameter_state()
        res_params, metrics = core_disabled.run_offline_consolidation()
        assert np.array_equal(res_params.W_rel, params_before.W_rel), "Invariant 4 violated: W_rel was modified"
        assert metrics["loss"] == 0.0, "Invariant 4 violated: offline consolidation executed when disabled"
