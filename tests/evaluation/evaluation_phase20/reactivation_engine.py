"""
AffectiveRecollectionEngine — Isolated Research Engine for Phase 20.

Implements:
1. Multi-modal memory retrieval scoring (Semantic + Ecphoric Resonance + Salience)
2. Competitive Softmax Gating (tau_comp=0.20, theta_gate=0.50)
3. Bounded Slow-Field Perturbation (r_slow in R^16, tanh saturation)
4. Multi-Timescale Liquid Neural Network (MT-LNN) ODE solver with slow-field coupling
5. Downstream cognitive consequence calculation (pacing latency, communication policy)
6. 10 experimental ablation modes (A1 - A10)
7. Human-interpretable telemetry tracing
"""

from __future__ import annotations

import logging
import time
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Tuple

import numpy as np
from scipy.integrate import solve_ivp
from scipy.special import expit, softplus

from src.core.models import PADState
from tests.evaluation_phase20.models import MemoryRecord, RecollectionTelemetry

logger = logging.getLogger(__name__)


def _xavier_uniform(shape: tuple, rng: np.random.Generator) -> np.ndarray:
    fan_in, fan_out = shape[-1], shape[0]
    limit = np.sqrt(6.0 / (fan_in + fan_out))
    return rng.uniform(-limit, limit, size=shape).astype(np.float64)


@dataclass
class RecollectionConfig:
    """Configuration for Affective Recollection & Reactivation."""
    hidden_fast_dim: int = 32
    hidden_slow_dim: int = 16
    stimulus_dim: int = 16
    homeo_dim: int = 4
    
    # Timescale parameters matching Phase 19 MT-LNN
    tau_fast_min: float = 0.10
    tau_fast_max: float = 1.50
    tau_slow_charge: float = 3.5
    tau_slow_decay: float = 28.0
    ode_step_size: float = 0.10
    
    # Philia resting baseline
    resting_baseline: Tuple[float, float, float] = (0.25, -0.05, 0.05)
    
    # Retrieval scoring weights
    w_sem: float = 0.60
    w_aff: float = 0.25
    w_sigma: float = 0.15
    
    # Gating parameters
    tau_comp: float = 0.20
    theta_gate: float = 0.50
    
    # Slow-field coupling gain W_rec
    coupling_rec_gain: float = 0.35
    
    # Fast-Slow coupling
    coupling_fs_strength: float = 0.05
    coupling_sf_strength: float = 1.00
    coupling_homeo_strength: float = 0.40
    
    # Ablation Flags (A1 - A10)
    ablate_no_memory: bool = False             # A1: r_slow = 0
    ablate_semantic_only: bool = False         # A2: w_aff=0, w_sigma=0
    ablate_affective_trace: bool = False       # A3: s_enc = s*_philia
    ablate_pad_only_trace: bool = False        # A4: s_enc reconstructed from 3D PAD pseudo-inverse
    ablate_latent_only_trace: bool = False     # A5: w_aff=0 (PAD omitted from retrieval)
    ablate_ecphoric_congruence: bool = False   # A6: w_aff=0
    ablate_softmax_gating: bool = False        # A7: theta_gate=0, linear weighting
    ablate_fixed_strength: bool = False        # A8: uniform alpha_k across passing traces
    ablate_unbounded_coupling: bool = False    # A9: remove tanh clamp on r_slow
    ablate_inject_fast_layer: bool = False     # A10: inject memory into h_fast instead of s_slow (Phase 11 replication)
    
    init_seed: int = 42


class AffectiveRecollectionEngine:
    """Coupled MT-LNN with Closed-Loop Affective Memory Reactivation."""

    def __init__(self, config: Optional[RecollectionConfig] = None) -> None:
        if config is None:
            config = RecollectionConfig()
        self._config = config

        Hf = config.hidden_fast_dim
        Hs = config.hidden_slow_dim
        Nx = config.stimulus_dim
        Nm = config.homeo_dim

        rng = np.random.default_rng(config.init_seed)

        # Fast Layer weights
        self.W_ff = _xavier_uniform((Hf, Hf), rng) * 0.20
        self.W_fs = np.zeros((Hf, Hs), dtype=np.float64)
        self.U_f = _xavier_uniform((Hf, Nx), rng) * 0.30
        self.b_f = np.zeros(Hf, dtype=np.float64)

        # Sensory alignment on principal fast channels
        self.U_f[0, 0] = 1.00  # Valence -> Pleasure
        self.U_f[1, 1] = 1.00  # Arousal -> Arousal
        self.U_f[2, 2] = 0.80  # Density -> Dominance

        # Fast Time-Constant weights
        self.W_tau_f = _xavier_uniform((Hf, Hf), rng) * 0.10
        self.U_tau_f = _xavier_uniform((Hf, Nx), rng) * 0.10
        self.b_tau_f = np.zeros(Hf, dtype=np.float64)

        # Slow Layer weights
        self.W_sf = np.zeros((Hs, Hf), dtype=np.float64)
        self.W_sh = np.zeros((Hs, Nm), dtype=np.float64)

        # Cross-timescale coupling
        self.W_sf[0, 0] = config.coupling_sf_strength
        self.W_sf[1, 1] = config.coupling_sf_strength
        self.W_sf[2, 2] = config.coupling_sf_strength * 0.80

        self.W_fs[0, 0] = config.coupling_fs_strength
        self.W_fs[1, 1] = config.coupling_fs_strength
        self.W_fs[2, 2] = config.coupling_fs_strength * 0.80

        # Homeostatic weights
        self.W_sh[0, 2] = -0.60 * config.coupling_homeo_strength
        self.W_sh[0, 1] = -0.20 * config.coupling_homeo_strength
        self.W_sh[1, 2] = +0.70 * config.coupling_homeo_strength
        self.W_sh[1, 1] = +0.10 * config.coupling_homeo_strength
        self.W_sh[1, 0] = +0.50 * config.coupling_homeo_strength

        # Projections to PAD
        self.W_proj_f = np.zeros((3, Hf), dtype=np.float64)
        self.W_proj_f[0, 0] = 0.70
        self.W_proj_f[1, 1] = 0.70
        self.W_proj_f[2, 2] = 0.60

        self.W_proj_s = np.zeros((3, Hs), dtype=np.float64)
        self.W_proj_s[0, 0] = 0.45
        self.W_proj_s[1, 1] = 0.45
        self.W_proj_s[2, 2] = 0.35

        # Pseudo-inverse of W_proj_s for ablation A4
        self._W_proj_s_pinv = np.linalg.pinv(self.W_proj_s)

        # Memory Coupling matrix W_rec
        self.W_rec = np.eye(Hs, dtype=np.float64) * config.coupling_rec_gain

        # Philia reference
        self.p_philia = np.array(config.resting_baseline, dtype=np.float64)
        self.s_philia = np.zeros(Hs, dtype=np.float64)
        self.s_philia[0] = 0.20
        self.s_philia[1] = -0.05
        self.s_philia[2] = 0.05

        self.m_homeo_resting = np.array([1.0, 0.0, 0.0, 1.0], dtype=np.float64)

        # Memory Store
        self._memory_store: List[MemoryRecord] = []

        # Current internal state
        self._h_fast: np.ndarray = np.zeros(Hf, dtype=np.float64)
        self._s_slow: np.ndarray = self.s_philia.copy()
        self._m_homeo: np.ndarray = self.m_homeo_resting.copy()
        self._active_r_slow: np.ndarray = np.zeros(Hs, dtype=np.float64)
        self._active_r_fast_inject: np.ndarray = np.zeros(Hf, dtype=np.float64)

        # Current PAD snapshot
        self._pad_snapshot = PADState(
            pleasure=float(self.p_philia[0]),
            arousal=float(self.p_philia[1]),
            dominance=float(self.p_philia[2]),
            timestamp=time.monotonic(),
        )

        # Telemetry history
        self._telemetry_log: List[RecollectionTelemetry] = []

    # ------------------------------------------------------------------
    # State Management & Store
    # ------------------------------------------------------------------

    def reset_to_resting(self) -> None:
        """Reset internal limbic states to Philia equilibrium."""
        self._h_fast = np.zeros(self._config.hidden_fast_dim, dtype=np.float64)
        self._s_slow = self.s_philia.copy()
        self._m_homeo = self.m_homeo_resting.copy()
        self._active_r_slow = np.zeros(self._config.hidden_slow_dim, dtype=np.float64)
        self._active_r_fast_inject = np.zeros(self._config.hidden_fast_dim, dtype=np.float64)
        self._pad_snapshot = PADState(
            pleasure=float(self.p_philia[0]),
            arousal=float(self.p_philia[1]),
            dominance=float(self.p_philia[2]),
            timestamp=time.monotonic(),
        )

    def set_memory_store(self, memories: List[MemoryRecord]) -> None:
        """Populate the episodic memory store."""
        self._memory_store = list(memories)

    def get_pad_state(self) -> PADState:
        return self._pad_snapshot

    def get_fast_state(self) -> np.ndarray:
        return self._h_fast.copy()

    def get_slow_state(self) -> np.ndarray:
        return self._s_slow.copy()

    def get_telemetry_log(self) -> List[RecollectionTelemetry]:
        return list(self._telemetry_log)

    def project_slow_to_pad(self, delta_s: np.ndarray) -> np.ndarray:
        """Project a slow perturbation vector or delta into 3D PAD space."""
        pad_raw = (self.W_proj_s @ delta_s) + self.p_philia
        return np.clip(pad_raw, -1.0, 1.0)

    # ------------------------------------------------------------------
    # Multi-Modal Retrieval Scoring & Gating (Section 7.2)
    # ------------------------------------------------------------------

    def compute_retrieval_affinity(
        self,
        cue_vec: np.ndarray,
        record: MemoryRecord,
    ) -> Tuple[float, float, float]:
        """
        Compute Semantic, Ecphoric, and Composite affinity scores.
        
        Returns:
            (S_sem, S_aff, Composite_Affinity)
        """
        cfg = self._config

        # 1. Semantic Relevance S_sem = cue^T e_k
        norm_cue = np.linalg.norm(cue_vec)
        if norm_cue > 1e-12:
            cue_normed = cue_vec / norm_cue
        else:
            cue_normed = np.zeros_like(cue_vec)
        
        s_sem = float(np.dot(cue_normed, record.semantic_embedding))

        # 2. Ecphoric Resonance S_aff = cos(p(t) - p*_philia, p_enc - p*_philia)
        cur_p = np.array([
            self._pad_snapshot.pleasure,
            self._pad_snapshot.arousal,
            self._pad_snapshot.dominance,
        ], dtype=np.float64)
        
        enc_p = np.array([
            record.pad_state.pleasure,
            record.pad_state.arousal,
            record.pad_state.dominance,
        ], dtype=np.float64)

        delta_cur = cur_p - self.p_philia
        delta_enc = enc_p - self.p_philia

        norm_cur = float(np.linalg.norm(delta_cur))
        norm_enc = float(np.linalg.norm(delta_enc))

        if norm_cur > 1e-6 and norm_enc > 1e-6:
            s_aff = float(np.dot(delta_cur, delta_enc) / (norm_cur * norm_enc))
        else:
            s_aff = 0.0

        # Handle Ablations on retrieval scoring
        w_sem = cfg.w_sem
        w_aff = cfg.w_aff
        w_sigma = cfg.w_sigma

        if cfg.ablate_semantic_only:
            w_sem, w_aff, w_sigma = 1.0, 0.0, 0.0
        elif cfg.ablate_ecphoric_congruence or cfg.ablate_latent_only_trace:
            w_sem = cfg.w_sem / (cfg.w_sem + cfg.w_sigma)
            w_sigma = cfg.w_sigma / (cfg.w_sem + cfg.w_sigma)
            w_aff = 0.0

        composite = (
            w_sem * max(0.0, s_sem) +
            w_aff * max(0.0, s_aff) +
            w_sigma * record.salience
        )

        return s_sem, s_aff, composite

    def evaluate_recollection(
        self,
        cue_vec: np.ndarray,
        candidate_memories: Optional[List[MemoryRecord]] = None,
        force_memory: Optional[MemoryRecord] = None,
    ) -> Tuple[np.ndarray, List[Tuple[MemoryRecord, float, float, float, float]]]:
        """
        Evaluate memory retrieval across store, apply competitive softmax gating,
        and construct bounded slow-field perturbation vector r_slow.
        
        Returns:
            (r_slow_bounded, scored_records)
            scored_records: list of (record, s_sem, s_aff, composite, alpha_k)
        """
        cfg = self._config
        store = candidate_memories if candidate_memories is not None else self._memory_store

        if cfg.ablate_no_memory or not store:
            self._active_r_slow = np.zeros(cfg.hidden_slow_dim, dtype=np.float64)
            return self._active_r_slow.copy(), []

        # If a specific memory is forced (for controlled ablation / counterfactual tests)
        if force_memory is not None:
            s_sem, s_aff, comp = self.compute_retrieval_affinity(cue_vec, force_memory)
            alpha = 1.0
            scored = [(force_memory, s_sem, s_aff, comp, alpha)]
            traces = [force_memory]
            alphas = [alpha]
        else:
            scored_raw = []
            for record in store:
                s_sem, s_aff, comp = self.compute_retrieval_affinity(cue_vec, record)
                scored_raw.append((record, s_sem, s_aff, comp))

            # Competitive Softmax Gating
            passing = []
            for item in scored_raw:
                record, s_sem, s_aff, comp = item
                threshold = 0.0 if cfg.ablate_softmax_gating else cfg.theta_gate
                if comp >= threshold:
                    passing.append(item)

            if not passing:
                # Sub-threshold: no reactivation triggered
                self._active_r_slow = np.zeros(cfg.hidden_slow_dim, dtype=np.float64)
                scored = [(r, s, a, c, 0.0) for (r, s, a, c) in scored_raw]
                return self._active_r_slow.copy(), scored

            scored_map = {}
            if cfg.ablate_fixed_strength:
                uniform_alpha = 1.0 / len(passing)
                for item in passing:
                    scored_map[item[0].episode_id] = uniform_alpha
            elif cfg.ablate_softmax_gating:
                total_c = sum(c for (_, _, _, c) in passing) + 1e-12
                for item in passing:
                    scored_map[item[0].episode_id] = item[3] / total_c
            else:
                comps = np.array([c for (_, _, _, c) in passing], dtype=np.float64)
                max_c = np.max(comps)
                exp_c = np.exp((comps - max_c) / cfg.tau_comp)
                softmax_weights = exp_c / np.sum(exp_c)
                for i in range(len(passing)):
                    scored_map[passing[i][0].episode_id] = float(softmax_weights[i])

            scored = [
                (r, s, a, c, scored_map.get(r.episode_id, 0.0))
                for (r, s, a, c) in scored_raw
            ]
            traces = [item[0] for item in passing]
            alphas = [scored_map[item[0].episode_id] for item in passing]

        # 3. Construct r_slow via convex combination of centered traces
        r_slow = np.zeros(cfg.hidden_slow_dim, dtype=np.float64)
        for record, alpha in zip(traces, alphas):
            if cfg.ablate_affective_trace:
                s_enc = self.s_philia.copy()
            elif cfg.ablate_pad_only_trace:
                # Synthesize slow latent vector from 3D PAD pseudo-inverse
                p_enc = np.array([
                    record.pad_state.pleasure,
                    record.pad_state.arousal,
                    record.pad_state.dominance,
                ], dtype=np.float64)
                delta_p = p_enc - self.p_philia
                s_enc = self.s_philia + (self._W_proj_s_pinv @ delta_p)
            else:
                s_enc = record.slow_latent_state

            delta_s = s_enc - self.s_philia
            r_slow += alpha * delta_s

        # Bounded saturation
        total_alpha = sum(alphas)
        if cfg.ablate_unbounded_coupling:
            r_slow_bounded = r_slow
        else:
            r_slow_bounded = np.tanh(r_slow) * min(1.0, total_alpha)

        if cfg.ablate_inject_fast_layer:
            # A10 replication: inject into h_fast directly
            self._active_r_slow = np.zeros(cfg.hidden_slow_dim, dtype=np.float64)
            # Project or pad into fast layer
            r_fast = np.zeros(cfg.hidden_fast_dim, dtype=np.float64)
            r_fast[:len(r_slow_bounded)] = r_slow_bounded
            self._active_r_fast_inject = r_fast
        else:
            self._active_r_slow = r_slow_bounded
            self._active_r_fast_inject = np.zeros(cfg.hidden_fast_dim, dtype=np.float64)

        return self._active_r_slow.copy(), scored

    # ------------------------------------------------------------------
    # MT-LNN Continuous Dynamics with Coupled Slow-Field Forcing
    # ------------------------------------------------------------------

    def _ode_step(
        self,
        h_fast: np.ndarray,
        s_slow: np.ndarray,
        x: np.ndarray,
        m_homeo: np.ndarray,
        r_slow: np.ndarray,
        r_fast_inject: np.ndarray,
        dt: float,
    ) -> Tuple[np.ndarray, np.ndarray]:
        cfg = self._config
        Hf = cfg.hidden_fast_dim
        Hs = cfg.hidden_slow_dim

        y0 = np.concatenate([h_fast, s_slow])
        delta_m = m_homeo - self.m_homeo_resting

        def rhs(t: float, y: np.ndarray) -> np.ndarray:
            y_f = np.clip(y[:Hf], -1.0, 1.0)
            y_s = np.clip(y[Hf:], -1.0, 1.0)
            delta_s = y_s - self.s_philia

            # Fast timescale
            tau_f_raw = softplus(self.W_tau_f @ y_f + self.U_tau_f @ x + self.b_tau_f)
            tau_f = np.clip(tau_f_raw, cfg.tau_fast_min, cfg.tau_fast_max)

            # Fast ODE: NO direct memory forcing, unless ablate_inject_fast_layer (A10)
            fast_drive = self.W_ff @ y_f + self.W_fs @ delta_s + self.U_f @ x + self.b_f
            if cfg.ablate_inject_fast_layer:
                fast_drive += r_fast_inject

            f_fast = np.tanh(fast_drive)
            dh_fast = (-y_f + f_fast) / tau_f

            # Slow timescale ODE with bounded memory forcing: W_rec @ r_slow
            tau_decay = cfg.tau_slow_decay
            tau_charge = cfg.tau_slow_charge

            W_sf_eff = np.zeros_like(self.W_sf) if cfg.ablate_inject_fast_layer else self.W_sf
            slow_drive = W_sf_eff @ y_f + self.W_sh @ delta_m + (self.W_rec @ r_slow)
            forcing = np.tanh(slow_drive)
            ds_slow = (-delta_s / tau_decay) + (forcing / tau_charge)

            return np.concatenate([dh_fast, ds_slow])

        res = solve_ivp(
            rhs,
            t_span=(0.0, dt),
            y0=y0,
            method="RK45",
            rtol=1e-6,
            atol=1e-8,
            max_step=dt / 2.0,
            dense_output=False,
            vectorized=False,
        )

        y_next = res.y[:, -1]
        h_next = np.clip(y_next[:Hf], -1.0, 1.0)
        s_next = np.clip(y_next[Hf:], -1.0, 1.0)
        return h_next, s_next

    def _project_to_pad(self, h_fast: np.ndarray, s_slow: np.ndarray) -> PADState:
        delta_s = s_slow - self.s_philia
        pad_raw = (self.W_proj_f @ h_fast) + (self.W_proj_s @ delta_s) + self.p_philia
        pad_clamped = np.clip(pad_raw, -1.0, 1.0)
        return PADState(
            pleasure=float(pad_clamped[0]),
            arousal=float(pad_clamped[1]),
            dominance=float(pad_clamped[2]),
            timestamp=time.monotonic(),
        )

    def step(
        self,
        stimulus: Optional[np.ndarray] = None,
        r_slow_override: Optional[np.ndarray] = None,
        r_fast_override: Optional[np.ndarray] = None,
        dt: Optional[float] = None,
    ) -> PADState:
        """Advance the system by one ODE time step."""
        cfg = self._config
        dt_val = dt if dt is not None else cfg.ode_step_size
        x = stimulus if stimulus is not None else np.zeros(cfg.stimulus_dim, dtype=np.float64)
        r_s = r_slow_override if r_slow_override is not None else self._active_r_slow
        r_f = r_fast_override if r_fast_override is not None else self._active_r_fast_inject

        h_new, s_new = self._ode_step(
            self._h_fast,
            self._s_slow,
            x,
            self._m_homeo,
            r_s,
            r_f,
            dt_val,
        )

        self._h_fast = h_new
        self._s_slow = s_new
        self._pad_snapshot = self._project_to_pad(h_new, s_new)
        return self._pad_snapshot

    # ------------------------------------------------------------------
    # Downstream Cognitive Pacing & Policy Modulation (Section 7.5)
    # ------------------------------------------------------------------

    def compute_cognitive_consequences(self) -> Tuple[float, str]:
        """
        Compute somatic pacing latency modulation and communication policy mode.
        
        Returns:
            (delta_tau_pace_ms, comm_mode)
        """
        p = self._pad_snapshot
        delta_p = np.array([p.pleasure, p.arousal, p.dominance]) - self.p_philia
        delta_s = self._s_slow - self.s_philia
        s_norm = float(np.linalg.norm(delta_s))

        # Somatic pacing latency modulation (ms)
        # Higher emotional salience / slow resonance elevates cognitive processing latency
        delta_tau = (
            380.0 * s_norm +
            220.0 * abs(float(delta_p[0])) +
            220.0 * abs(float(delta_p[1]))
        )

        # Communication Policy
        if p.pleasure > 0.40 and s_norm > 0.08:
            mode = "DEEP_RECIPROCAL"
        elif p.arousal > 0.20 and delta_p[0] < -0.10:
            mode = "VIGILANT_ACCOMMODATING"
        elif p.pleasure < 0.10 and s_norm > 0.08:
            mode = "EMPATHIC_CONTAINMENT"
        elif s_norm > 0.10:
            mode = "AFFECTIVE_ATTUNED"
        else:
            mode = "STABLE_COGNITIVE"

        return delta_tau, mode

    # ------------------------------------------------------------------
    # Full Recollection Simulation Run with Telemetry Logging
    # ------------------------------------------------------------------

    def simulate_cue_recollection(
        self,
        cue_text: str,
        cue_vec: np.ndarray,
        duration_s: float = 60.0,
        pulse_duration_s: float = 2.0,
        force_memory: Optional[MemoryRecord] = None,
    ) -> Tuple[np.ndarray, np.ndarray, np.ndarray, RecollectionTelemetry]:
        """
        Simulate the complete temporal lifecycle of cue presentation, recollection,
        and unforced relaxation back toward Philia attractor.
        
        Returns:
            (timestamps, pad_trajectory, slow_trajectory, telemetry)
        """
        cfg = self._config
        dt = cfg.ode_step_size
        n_steps = int(duration_s / dt)
        pulse_steps = max(1, int(pulse_duration_s / dt))

        initial_pad = (
            self._pad_snapshot.pleasure,
            self._pad_snapshot.arousal,
            self._pad_snapshot.dominance,
        )

        # 1. Evaluate memory reactivation
        r_slow, scored = self.evaluate_recollection(cue_vec, force_memory=force_memory)

        retrieved_id = "NONE"
        s_sem = 0.0
        s_aff = 0.0
        comp = 0.0
        alpha_max = 0.0
        passed = False

        if scored:
            best = max(scored, key=lambda x: x[3])
            retrieved_id = best[0].episode_id
            s_sem = best[1]
            s_aff = best[2]
            comp = best[3]
            alpha_max = best[4]
            passed = alpha_max > 0.0

        r_norm = float(np.linalg.norm(r_slow))
        dom_idx = int(np.argmax(np.abs(r_slow))) if r_norm > 1e-6 else 0
        dominant_channel = (dom_idx, float(r_slow[dom_idx]))

        # Simulate trajectory
        timestamps = np.zeros(n_steps, dtype=np.float64)
        pad_traj = np.zeros((n_steps, 3), dtype=np.float64)
        slow_traj = np.zeros((n_steps, cfg.hidden_slow_dim), dtype=np.float64)

        peak_pad = initial_pad
        max_pad_dist = 0.0
        peak_somatic_latency = 0.0
        peak_comm_mode = "STABLE_COGNITIVE"

        for step_i in range(n_steps):
            t = step_i * dt
            timestamps[step_i] = t

            # Apply memory perturbation during cue pulse
            if step_i < pulse_steps:
                cur_r = r_slow
                cur_rf = self._active_r_fast_inject
            else:
                cur_r = np.zeros_like(r_slow)
                cur_rf = np.zeros_like(self._active_r_fast_inject)

            pad_state = self.step(r_slow_override=cur_r, r_fast_override=cur_rf, dt=dt)
            pad_curr = np.array([pad_state.pleasure, pad_state.arousal, pad_state.dominance])
            pad_traj[step_i] = pad_curr
            slow_traj[step_i] = self.get_slow_state()

            # Measure peak cognitive consequence during active recollective phase
            cur_lat, cur_mode = self.compute_cognitive_consequences()
            if cur_lat > peak_somatic_latency:
                peak_somatic_latency = cur_lat
                peak_comm_mode = cur_mode

            dist = float(np.linalg.norm(pad_curr - np.array(initial_pad)))
            if dist > max_pad_dist:
                max_pad_dist = dist
                peak_pad = (float(pad_curr[0]), float(pad_curr[1]), float(pad_curr[2]))

        # Calculate integrated AUC displacement from initial PAD
        pad_diffs = np.linalg.norm(pad_traj - np.array(initial_pad), axis=1)
        delta_auc = float(np.sum((pad_diffs[:-1] + pad_diffs[1:]) / 2.0 * np.diff(timestamps)))

        # Downstream consequences captured at peak
        somatic_latency_ms = peak_somatic_latency
        comm_mode = peak_comm_mode

        # Deflection half-life
        half_val = max_pad_dist / 2.0
        half_life_s = duration_s
        for step_i in range(n_steps):
            if pad_diffs[step_i] >= half_val:
                # Find when it drops below half_val after peak
                for drop_i in range(step_i, n_steps):
                    if pad_diffs[drop_i] <= half_val:
                        half_life_s = timestamps[drop_i] - timestamps[step_i]
                        break
                break

        # Restoration error at end of unforced window
        restoration_error = float(np.linalg.norm(pad_traj[-1] - self.p_philia))

        telemetry = RecollectionTelemetry(
            cue_text=cue_text,
            retrieved_id=retrieved_id,
            semantic_score=s_sem,
            ecphoric_score=s_aff,
            composite_affinity=comp,
            gating_passed=passed,
            activation_weight=alpha_max,
            r_slow_norm=r_norm,
            dominant_channel=dominant_channel,
            initial_pad=initial_pad,
            peak_pad=peak_pad,
            delta_pad_auc=delta_auc,
            somatic_latency_ms=somatic_latency_ms,
            communication_mode=comm_mode,
            half_life_s=half_life_s,
            restoration_error=restoration_error,
        )

        self._telemetry_log.append(telemetry)
        return timestamps, pad_traj, slow_traj, telemetry
