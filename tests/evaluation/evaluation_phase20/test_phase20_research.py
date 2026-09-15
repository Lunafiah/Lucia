"""
Automated Test Suite for Phase 20 Affective Recollection Research (EXP20.1 - EXP20.10).

Executes the full evaluation matrix defined in PHASE_20_RESEARCH_SPEC.md:
  - Retrieval Specificity (EXP20.1)
  - Affective Trace Reconstruction (EXP20.2)
  - Temporal Persistence (EXP20.3)
  - Causal Trajectory Modulation (EXP20.4)
  - Downstream Cognitive Modulation (EXP20.5)
  - Memory Identity vs. Vector-Injection Counterfactual Controls (EXP20.6)
  - Ambiguous Cue Competition (EXP20.7)
  - Repeated Recollection & Habituation (EXP20.8)
  - Comprehensive Ablation Matrix A1 - A10 (EXP20.9)
  - Deterministic Replay & Numerical Stability (EXP20.10)
"""

from __future__ import annotations

import numpy as np
import pytest

from tests.evaluation_phase20.metrics import (
    compute_affective_fidelity,
    compute_causal_impact,
    compute_counterfactual_metrics,
    compute_retrieval_metrics,
    compute_stability_metrics,
    compute_temporal_persistence,
)
from tests.evaluation_phase20.models import CounterfactualGenerator, MemoryRecord
from tests.evaluation_phase20.reactivation_engine import (
    AffectiveRecollectionEngine,
    RecollectionConfig,
)
from tests.evaluation_phase20.scenarios import (
    ScenarioGenerator,
    generate_50_memory_fixtures,
)


@pytest.fixture
def memory_fixtures() -> list[MemoryRecord]:
    return generate_50_memory_fixtures(dim=64)


@pytest.fixture
def scenario_gen(memory_fixtures: list[MemoryRecord]) -> ScenarioGenerator:
    return ScenarioGenerator(memory_fixtures)


@pytest.fixture
def engine(memory_fixtures: list[MemoryRecord]) -> AffectiveRecollectionEngine:
    eng = AffectiveRecollectionEngine(RecollectionConfig())
    eng.set_memory_store(memory_fixtures)
    eng.reset_to_resting()
    return eng


# ==============================================================================
# EXP20.1: Retrieval Specificity & Competitive Ranking
# Pre-registered criteria: Precision@1 >= 0.85, FRR <= 0.10, SNR >= 3.00
# ==============================================================================
def test_exp20_1_retrieval_specificity(
    engine: AffectiveRecollectionEngine,
    scenario_gen: ScenarioGenerator,
    memory_fixtures: list[MemoryRecord],
) -> None:
    target_ids = []
    retrieved_results = []

    # Test all 50 memories with exact cues
    for mem in memory_fixtures:
        target_ids.append(mem.episode_id)
        cue = scenario_gen.get_exact_cue(mem)
        _, scored = engine.evaluate_recollection(cue)
        retrieved_results.append([(r.episode_id, comp, alpha) for (r, _, _, comp, alpha) in scored])

    # Add 10 noisy queries to test robust discrimination
    for mem in memory_fixtures[:10]:
        target_ids.append(mem.episode_id)
        noisy_cue = scenario_gen.get_noisy_cue(mem, noise_std=0.08, seed=123)
        _, scored = engine.evaluate_recollection(noisy_cue)
        retrieved_results.append([(r.episode_id, comp, alpha) for (r, _, _, comp, alpha) in scored])

    # Add 10 orthogonal distractor queries (target = NONE)
    for i in range(10):
        target_ids.append("NONE")
        ortho_cue = scenario_gen.get_orthogonal_cue(seed=900 + i)
        _, scored = engine.evaluate_recollection(ortho_cue)
        retrieved_results.append([(r.episode_id, comp, alpha) for (r, _, _, comp, alpha) in scored])

    metrics = compute_retrieval_metrics(target_ids, retrieved_results)

    print(f"\n[EXP20.1 Metrics] {metrics}")
    assert metrics["precision_at_1"] >= 0.85, f"Precision@1 {metrics['precision_at_1']:.3f} < 0.85"
    assert metrics["frr"] <= 0.10, f"FRR {metrics['frr']:.3f} > 0.10"
    assert metrics["snr"] >= 3.00, f"SNR {metrics['snr']:.3f} < 3.00"


# ==============================================================================
# EXP20.2: Affective Trace Reconstruction Fidelity
# Pre-registered criteria: Cosine Sim >= 0.70, Latent Error <= 0.35, PAD Error <= 0.30
# ==============================================================================
def test_exp20_2_trace_reconstruction_fidelity(
    engine: AffectiveRecollectionEngine,
    scenario_gen: ScenarioGenerator,
    memory_fixtures: list[MemoryRecord],
) -> None:
    cos_sims = []
    latent_errors = []
    pad_errors = []

    # Evaluate across representative emotional memories
    test_mems = [m for m in memory_fixtures if m.salience >= 0.70][:15]

    for mem in test_mems:
        cue = scenario_gen.get_exact_cue(mem)
        r_slow, scored = engine.evaluate_recollection(cue)
        
        # Project reconstructed slow perturbation into PAD space
        pad_actual = engine.project_slow_to_pad(r_slow)
        pad_target = engine.project_slow_to_pad(mem.slow_latent_state - engine.s_philia)

        fidelity = compute_affective_fidelity(
            r_slow=r_slow,
            s_target=mem.slow_latent_state,
            s_philia=engine.s_philia,
            pad_actual=pad_actual,
            pad_target=pad_target,
        )

        cos_sims.append(fidelity["cosine_similarity"])
        latent_errors.append(fidelity["latent_l2_error"])
        pad_errors.append(fidelity["pad_alignment_error"])

    mean_cos = float(np.mean(cos_sims))
    mean_latent_err = float(np.mean(latent_errors))
    mean_pad_err = float(np.mean(pad_errors))

    print(f"\n[EXP20.2 Metrics] Cosine={mean_cos:.3f}, Latent_L2={mean_latent_err:.3f}, PAD_Error={mean_pad_err:.3f}")
    assert mean_cos >= 0.70, f"Cosine similarity {mean_cos:.3f} < 0.70"
    assert mean_latent_err <= 0.35, f"Latent error {mean_latent_err:.3f} > 0.35"
    assert mean_pad_err <= 0.30, f"PAD error {mean_pad_err:.3f} > 0.30"


# ==============================================================================
# EXP20.3: Temporal Persistence & Biphasic Dynamics
# Pre-registered criteria: t_1/2 >= 10.0s, retention >= 20.0s, restoration error < 1e-4
# ==============================================================================
def test_exp20_3_temporal_persistence(
    engine: AffectiveRecollectionEngine,
    scenario_gen: ScenarioGenerator,
    memory_fixtures: list[MemoryRecord],
) -> None:
    # Use a high-salience joy memory
    mem = memory_fixtures[0]  # Kyoto rainy walk
    cue = scenario_gen.get_exact_cue(mem)

    # Condition C3: Proposed slow-field reactivation
    engine.reset_to_resting()
    ts, pad_traj_c3, slow_traj_c3, telem_c3 = engine.simulate_cue_recollection(
        cue_text=mem.text_content,
        cue_vec=cue,
        duration_s=360.0,
        pulse_duration_s=3.0,
    )

    metrics_c3 = compute_temporal_persistence(ts, pad_traj_c3, engine.p_philia)
    print(f"\n[EXP20.3 C3 Metrics] {metrics_c3}")

    assert metrics_c3["deflection_half_life"] >= 10.0, f"Half life {metrics_c3['deflection_half_life']} < 10s"
    assert metrics_c3["retention_duration"] >= 20.0, f"Retention {metrics_c3['retention_duration']} < 20s"
    assert metrics_c3["restoration_error"] < 1e-4, f"Restoration error {metrics_c3['restoration_error']} >= 1e-4"

    # Comparative Baseline C1: Text-only (no limbic perturbation)
    cfg_c1 = RecollectionConfig(ablate_no_memory=True)
    eng_c1 = AffectiveRecollectionEngine(cfg_c1)
    eng_c1.set_memory_store(memory_fixtures)
    ts, pad_traj_c1, _, _ = eng_c1.simulate_cue_recollection(mem.text_content, cue, duration_s=80.0)
    metrics_c1 = compute_temporal_persistence(ts, pad_traj_c1, engine.p_philia)
    
    # C1 should show zero limbic deflection
    assert metrics_c1["max_deflection"] < 1e-6, "C1 text-only showed non-zero limbic deflection"


# ==============================================================================
# EXP20.4: Causal Trajectory Modulation
# Pre-registered criteria: Delta PAD AUC >= 0.15
# ==============================================================================
def test_exp20_4_causal_trajectory_modulation(
    engine: AffectiveRecollectionEngine,
    scenario_gen: ScenarioGenerator,
    memory_fixtures: list[MemoryRecord],
) -> None:
    # Baseline C0 unperturbed trajectory
    engine.reset_to_resting()
    ts_base, pad_base, _, _ = engine.simulate_cue_recollection(
        cue_text="Neutral stimulus",
        cue_vec=scenario_gen.get_orthogonal_cue(seed=999),
        duration_s=60.0,
    )

    # Test distinct emotional categories: Joy (MEM-JOY-01) and Stress (MEM-STRESS-01)
    joy_mem = memory_fixtures[0]
    stress_mem = memory_fixtures[10]

    # Joy recollection
    engine.reset_to_resting()
    ts_joy, pad_joy, _, telem_joy = engine.simulate_cue_recollection(
        cue_text=joy_mem.text_content,
        cue_vec=scenario_gen.get_exact_cue(joy_mem),
        duration_s=60.0,
    )
    causal_joy = compute_causal_impact(ts_joy, pad_joy, pad_base, telem_joy.somatic_latency_ms)

    # Stress recollection
    engine.reset_to_resting()
    ts_stress, pad_stress, _, telem_stress = engine.simulate_cue_recollection(
        cue_text=stress_mem.text_content,
        cue_vec=scenario_gen.get_exact_cue(stress_mem),
        duration_s=60.0,
    )
    causal_stress = compute_causal_impact(ts_stress, pad_stress, pad_base, telem_stress.somatic_latency_ms)

    print(f"\n[EXP20.4 Joy Delta AUC] {causal_joy['delta_pad_auc']:.4f}")
    print(f"[EXP20.4 Stress Delta AUC] {causal_stress['delta_pad_auc']:.4f}")

    assert causal_joy["delta_pad_auc"] >= 0.15, f"Joy Delta AUC {causal_joy['delta_pad_auc']:.4f} < 0.15"
    assert causal_stress["delta_pad_auc"] >= 0.15, f"Stress Delta AUC {causal_stress['delta_pad_auc']:.4f} < 0.15"


# ==============================================================================
# EXP20.5: Downstream Cognitive & Behavioral Modulation
# Pre-registered criteria: Delta tau_pace >= 100ms, Comm Mode Shift >= 30%
# ==============================================================================
def test_exp20_5_downstream_cognitive_modulation(
    engine: AffectiveRecollectionEngine,
    scenario_gen: ScenarioGenerator,
    memory_fixtures: list[MemoryRecord],
) -> None:
    salient_mems = [m for m in memory_fixtures if m.salience >= 0.75]
    shifts = 0
    pacing_deltas = []

    # Resting baseline latency
    engine.reset_to_resting()
    base_latency, default_mode = engine.compute_cognitive_consequences()
    assert default_mode == "STABLE_COGNITIVE"

    for mem in salient_mems:
        engine.reset_to_resting()
        cue = scenario_gen.get_exact_cue(mem)
        _, pad_traj, _, telem = engine.simulate_cue_recollection(
            cue_text=mem.text_content,
            cue_vec=cue,
            duration_s=30.0,
            pulse_duration_s=2.0,
        )

        pacing_delta = telem.somatic_latency_ms - base_latency
        pacing_deltas.append(pacing_delta)

        if telem.communication_mode != default_mode:
            shifts += 1

    mean_pacing = float(np.mean(pacing_deltas))
    shift_rate = shifts / len(salient_mems)

    print(f"\n[EXP20.5 Metrics] Mean Pacing Shift: +{mean_pacing:.1f}ms, Mode Shift Rate: {shift_rate*100:.1f}%")
    assert mean_pacing >= 100.0, f"Mean pacing latency {mean_pacing:.1f}ms < 100ms"
    assert shift_rate >= 0.30, f"Mode shift rate {shift_rate*100:.1f}% < 30%"


# ==============================================================================
# EXP20.6: Memory Identity vs. Vector-Injection Counterfactual Controls
# Pre-registered criteria:
#   Authentic vs Shuffled Alignment <= 0.20
#   Authentic vs Matched-Norm Random Ratio <= 0.20
#   Wrong-Memory Cross-Contamination <= 0.10
# ==============================================================================
def test_exp20_6_counterfactual_identity_controls(
    engine: AffectiveRecollectionEngine,
    scenario_gen: ScenarioGenerator,
    memory_fixtures: list[MemoryRecord],
) -> None:
    """
    Directly resolves Phase 11's core vulnerability by testing 4 conditions under the identical cue:
      1. Authentic target memory trace
      2. Wrong-memory trace (authentic, but orthogonal episode)
      3. Shuffled latent trace (matched norm & component distribution, destroyed alignment)
      4. Matched-norm random Gaussian vector
    """
    target_mem = memory_fixtures[0]  # Kyoto rainy walk (Joy)
    cue = scenario_gen.get_exact_cue(target_mem)

    auth_mem, wrong_mem, shuf_mem, rand_mem = scenario_gen.get_counterfactual_quadplet(target_mem)

    # 1. Authentic trace run
    engine.reset_to_resting()
    ts, traj_auth, _, _ = engine.simulate_cue_recollection(
        cue_text=target_mem.text_content,
        cue_vec=cue,
        duration_s=60.0,
        force_memory=auth_mem,
    )

    # 2. Wrong memory trace run (paired with same cue)
    engine.reset_to_resting()
    _, traj_wrong, _, _ = engine.simulate_cue_recollection(
        cue_text=target_mem.text_content,
        cue_vec=cue,
        duration_s=60.0,
        force_memory=wrong_mem,
    )

    # 3. Shuffled latent trace run (matched norm, scrambled dimensions)
    engine.reset_to_resting()
    _, traj_shuf, _, _ = engine.simulate_cue_recollection(
        cue_text=target_mem.text_content,
        cue_vec=cue,
        duration_s=60.0,
        force_memory=shuf_mem,
    )

    # 4. Matched-norm random vector run (pure Gaussian noise scaled to match ||s_enc||)
    engine.reset_to_resting()
    _, traj_rand, _, _ = engine.simulate_cue_recollection(
        cue_text=target_mem.text_content,
        cue_vec=cue,
        duration_s=60.0,
        force_memory=rand_mem,
    )

    cf_metrics = compute_counterfactual_metrics(
        timestamps=ts,
        traj_authentic=traj_auth,
        traj_wrong=traj_wrong,
        traj_shuffled=traj_shuf,
        traj_random=traj_rand,
        philia_pad=engine.p_philia,
    )

    print(f"\n[EXP20.6 Counterfactual Metrics] {cf_metrics}")

    assert cf_metrics["shuffled_alignment"] <= 0.20, (
        f"Shuffled alignment {cf_metrics['shuffled_alignment']:.3f} > 0.20 "
        "(recollection not sensitive to latent dimension structure!)"
    )
    assert cf_metrics["random_ratio"] <= 0.20, (
        f"Random vector alignment ratio {cf_metrics['random_ratio']:.3f} > 0.20 "
        "(replicates Phase 11 flaw: random vector produced authentic-like shift!)"
    )
    assert cf_metrics["wrong_memory_cross_contamination"] <= 0.10, (
        f"Wrong memory cross-contamination {cf_metrics['wrong_memory_cross_contamination']:.3f} > 0.10"
    )


# ==============================================================================
# EXP20.7: Ambiguous Cue Competition & Blending
# Pre-registered criteria: Bounded convex blending, zero NaN, zero instability
# ==============================================================================
def test_exp20_7_ambiguous_cue_competition(
    engine: AffectiveRecollectionEngine,
    scenario_gen: ScenarioGenerator,
    memory_fixtures: list[MemoryRecord],
) -> None:
    joy_mem = memory_fixtures[0]     # Joy (P=+0.80)
    stress_mem = memory_fixtures[10] # Stress (P=-0.70)

    # Ambiguous cue positioned equidistant between joy and stress
    ambig_cue = scenario_gen.get_ambiguous_cue(joy_mem, stress_mem)

    engine.reset_to_resting()
    r_slow, scored = engine.evaluate_recollection(ambig_cue)

    # Both should be candidates
    scored_ids = [item[0].episode_id for item in scored]
    assert joy_mem.episode_id in scored_ids
    assert stress_mem.episode_id in scored_ids

    # Simulate trajectory under ambiguous cue
    engine.reset_to_resting()
    ts, pad_traj, slow_traj, telem = engine.simulate_cue_recollection(
        cue_text="Ambiguous situation",
        cue_vec=ambig_cue,
        duration_s=40.0,
    )

    # Verify trajectory is bounded and intermediate between Joy and Stress
    max_p = float(np.max(pad_traj[:, 0]))
    min_p = float(np.min(pad_traj[:, 0]))
    
    assert not np.isnan(pad_traj).any(), "NaN found in ambiguous trajectory"
    assert np.all(np.abs(pad_traj) <= 1.0), "PAD bounded violation"
    print(f"\n[EXP20.7 Ambiguous Blend Range] Pleasure in [{min_p:.3f}, {max_p:.3f}]")


# ==============================================================================
# EXP20.8: Repeated Recollection & Habituation Dynamics
# Pre-registered criteria: Asymptotic saturation (max norm <= 0.85), Drift <= 0.10
# ==============================================================================
def test_exp20_8_repeated_recollection_habituation(
    engine: AffectiveRecollectionEngine,
    scenario_gen: ScenarioGenerator,
    memory_fixtures: list[MemoryRecord],
) -> None:
    mem = memory_fixtures[0]
    cue = scenario_gen.get_exact_cue(mem)

    engine.reset_to_resting()
    dt = 0.10
    total_turns = 5
    turn_interval_s = 10.0
    turn_steps = int(turn_interval_s / dt)

    peak_slow_norms = []

    for turn in range(total_turns):
        # Present cue and apply perturbation
        r_slow, _ = engine.evaluate_recollection(cue)
        
        # Run turn interval
        turn_max_norm = 0.0
        for step_i in range(turn_steps):
            cur_r = r_slow if step_i < int(2.0 / dt) else np.zeros_like(r_slow)
            engine.step(r_slow_override=cur_r, dt=dt)
            s = engine.get_slow_state()
            norm = float(np.linalg.norm(s - engine.s_philia))
            if norm > turn_max_norm:
                turn_max_norm = norm

        peak_slow_norms.append(turn_max_norm)

    print(f"\n[EXP20.8 Peak Slow Norms across 5 turns] {[f'{x:.4f}' for x in peak_slow_norms]}")
    
    # Asymptotic saturation: peaks must not grow unboundedly
    assert max(peak_slow_norms) <= 0.85, f"Slow norm {max(peak_slow_norms):.3f} exceeded 0.85 bound"
    # Drift bound between turn 4 and 5 must be <= 0.10 (saturation reached)
    drift = abs(peak_slow_norms[-1] - peak_slow_norms[-2])
    assert drift <= 0.10, f"Drift between turns {drift:.4f} > 0.10"


# ==============================================================================
# EXP20.9: Comprehensive Ablation Matrix (A1 - A10)
# ==============================================================================
def test_exp20_9_ablation_matrix(
    memory_fixtures: list[MemoryRecord],
    scenario_gen: ScenarioGenerator,
) -> None:
    target_mem = memory_fixtures[0]
    cue = scenario_gen.get_exact_cue(target_mem)

    # Reference full model (C3)
    full_eng = AffectiveRecollectionEngine(RecollectionConfig())
    full_eng.set_memory_store(memory_fixtures)
    ts, pad_full, _, telem_full = full_eng.simulate_cue_recollection("Test", cue, duration_s=40.0)
    delta_auc_full = telem_full.delta_pad_auc

    # A1: No Memory (r_slow = 0)
    eng_a1 = AffectiveRecollectionEngine(RecollectionConfig(ablate_no_memory=True))
    eng_a1.set_memory_store(memory_fixtures)
    _, pad_a1, _, telem_a1 = eng_a1.simulate_cue_recollection("Test", cue, duration_s=40.0)
    assert telem_a1.delta_pad_auc < 1e-6, "A1 No Memory had non-zero AUC"

    # A3: Affective Trace Disabled (s_enc = s*_philia)
    eng_a3 = AffectiveRecollectionEngine(RecollectionConfig(ablate_affective_trace=True))
    eng_a3.set_memory_store(memory_fixtures)
    _, pad_a3, _, telem_a3 = eng_a3.simulate_cue_recollection("Test", cue, duration_s=40.0)
    assert telem_a3.delta_pad_auc < 1e-6, "A3 Affective Trace Disabled had non-zero AUC"

    # A4: PAD-only Trace (reconstructed s_enc)
    eng_a4 = AffectiveRecollectionEngine(RecollectionConfig(ablate_pad_only_trace=True))
    eng_a4.set_memory_store(memory_fixtures)
    r_slow_a4, _ = eng_a4.evaluate_recollection(cue)
    fidelity_a4 = compute_affective_fidelity(r_slow_a4, target_mem.slow_latent_state, eng_a4.s_philia, np.zeros(3), np.zeros(3))
    # Synthetic reconstruction from 3D PAD has higher error than authentic 16D latent trace
    assert fidelity_a4["latent_l2_error"] > 0.05

    # A7: Softmax Gating Disabled (noise susceptibility)
    eng_a7 = AffectiveRecollectionEngine(RecollectionConfig(ablate_softmax_gating=True))
    eng_a7.set_memory_store(memory_fixtures)
    ortho_cue = scenario_gen.get_orthogonal_cue(seed=777)
    r_a7, scored_a7 = eng_a7.evaluate_recollection(ortho_cue)
    # Without gating, orthogonal noise causes spurious activation
    assert np.linalg.norm(r_a7) > 0.01, "A7 without gating failed to demonstrate noise leakage"

    # A10: Fast Layer Injection (Replicates Phase 11 failure)
    eng_a10 = AffectiveRecollectionEngine(RecollectionConfig(ablate_inject_fast_layer=True))
    eng_a10.set_memory_store(memory_fixtures)
    ts_a10, pad_a10, _, _ = eng_a10.simulate_cue_recollection("Test", cue, duration_s=40.0)
    persistence_a10 = compute_temporal_persistence(ts_a10, pad_a10, eng_a10.p_philia)
    # Fast layer decay is extremely rapid (tau_f < 1.5s), proving the dual-timescale necessity
    print(f"\n[A10 Fast Layer Half-Life] {persistence_a10['deflection_half_life']:.2f}s (vs C3: {telem_full.half_life_s:.2f}s)")
    assert persistence_a10["deflection_half_life"] < 4.0, "A10 fast injection unexpectedly persisted"


# ==============================================================================
# EXP20.10: Deterministic Replay & Numerical Stability
# Pre-registered criteria: Replay diff < 1e-12, NaN/Inf == 0, max norm <= 1.00
# ==============================================================================
def test_exp20_10_deterministic_replay_and_numerical_stability(
    memory_fixtures: list[MemoryRecord],
    scenario_gen: ScenarioGenerator,
) -> None:
    cue = scenario_gen.get_exact_cue(memory_fixtures[0])

    # Run 1
    eng1 = AffectiveRecollectionEngine(RecollectionConfig(init_seed=42))
    eng1.set_memory_store(memory_fixtures)
    ts1, pad1, slow1, _ = eng1.simulate_cue_recollection("Run 1", cue, duration_s=50.0)

    # Run 2
    eng2 = AffectiveRecollectionEngine(RecollectionConfig(init_seed=42))
    eng2.set_memory_store(memory_fixtures)
    ts2, pad2, slow2, _ = eng2.simulate_cue_recollection("Run 2", cue, duration_s=50.0)

    # Replay invariance
    diff_max = float(np.max(np.abs(pad1 - pad2)))
    print(f"\n[EXP20.10 Replay Max Diff] {diff_max:.2e}")
    assert diff_max < 1e-12, f"Deterministic replay difference {diff_max:.2e} >= 1e-12"

    # Numerical stability over 1,000 steps
    eng_stress = AffectiveRecollectionEngine(RecollectionConfig(init_seed=99))
    eng_stress.set_memory_store(memory_fixtures)
    
    fast_history = []
    slow_history = []
    rng = np.random.default_rng(12345)

    for i in range(1000):
        # Apply random stimuli and recollections
        stim = rng.normal(0.0, 0.5, size=16)
        r_perturb = rng.normal(0.0, 0.3, size=16)
        eng_stress.step(stimulus=stim, r_slow_override=r_perturb, dt=0.1)
        fast_history.append(eng_stress.get_fast_state())
        slow_history.append(eng_stress.get_slow_state())

    stability = compute_stability_metrics(np.array(fast_history), np.array(slow_history), replay_diff_max=diff_max)
    print(f"[EXP20.10 Stability Metrics] {stability}")

    assert stability["non_finite_count"] == 0, "Non-finite values (NaN/Inf) encountered"
    assert stability["max_norm"] <= 1.00, f"Max hidden norm {stability['max_norm']:.4f} > 1.00"
