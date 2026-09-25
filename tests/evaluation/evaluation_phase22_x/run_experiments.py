"""
Comprehensive Test and Experiment Runner for Lucia Phase 22-X.
Executes Experiments E1–E7, measures all metrics and CPU resources,
and generates structured JSON results.
"""
import os
import time
import json
from typing import Dict, List, Any
import numpy as np
import torch

from .sim_user_env import (
    SimUserEnv,
    NUM_STATES,
    NUM_INTENTS,
    LATENT_STATES,
    INTENT_CLASSES,
)
from .baselines import (
    B0_MajorityPrior,
    B1_CalibratedDiscriminative,
    B2_BayesFilter,
    B3_POMDPTracker,
    B4_JevLayaSurrogate,
    B5_TemporalLatentMarkov,
)
from .metrics import (
    compute_ece,
    compute_brier_score,
    compute_nll,
    compute_tv_distance,
    compute_entropy,
)
from .prediction_tree import (
    BoundedPredictionTree,
    EpistemicActionSelector,
)


def run_experiment_e1(env_train: SimUserEnv, env_val: SimUserEnv, seed: int = 42) -> Dict[str, Any]:
    """
    E1: Observation Calibration under In-Distribution and Distribution Shift (DS-1 to DS-5).
    """
    torch.manual_seed(seed)
    np.random.seed(seed)
    
    # 1. Generate data splits
    X_train, y_train, _ = env_train.generate_dataset(10000)
    X_val, y_val, _ = env_val.generate_dataset(2500)
    
    # In-distribution test
    env_test = SimUserEnv(seed=seed + 10, noise_level=0.10)
    X_test, y_test, _ = env_test.generate_dataset(5000)

    # Models
    b0 = B0_MajorityPrior()
    b0.fit(y_train, np.zeros_like(y_train))
    
    b1 = B1_CalibratedDiscriminative()
    t0 = time.perf_counter()
    b1.fit(X_train, y_train, epochs=35)
    b1.calibrate(X_val, y_val)
    t_train_b1 = time.perf_counter() - t0

    b4 = B4_JevLayaSurrogate()
    t0 = time.perf_counter()
    b4.fit(X_train, y_train, epochs=35)
    b4.calibrate(X_val, y_val)
    t_train_b4 = time.perf_counter() - t0

    # In-Distribution Evaluation
    t0 = time.perf_counter()
    p_b0_id = b0.predict_state_probs(X_test)
    t_inf_b0 = (time.perf_counter() - t0) / len(X_test) * 1000.0

    t0 = time.perf_counter()
    p_b1_id = b1.predict_probs(X_test)
    t_inf_b1 = (time.perf_counter() - t0) / len(X_test) * 1000.0

    t0 = time.perf_counter()
    p_b4_id, unc_b4_id = b4.predict_probs_and_uncertainty(X_test)
    t_inf_b4 = (time.perf_counter() - t0) / len(X_test) * 1000.0

    results = {
        "in_distribution": {
            "B0": {
                "ece": compute_ece(p_b0_id, y_test),
                "brier": compute_brier_score(p_b0_id, y_test, NUM_STATES),
                "nll": compute_nll(p_b0_id, y_test),
                "acc": float(np.mean(np.argmax(p_b0_id, axis=1) == y_test)),
                "latency_ms": t_inf_b0,
            },
            "B1": {
                "ece": compute_ece(p_b1_id, y_test),
                "brier": compute_brier_score(p_b1_id, y_test, NUM_STATES),
                "nll": compute_nll(p_b1_id, y_test),
                "acc": float(np.mean(np.argmax(p_b1_id, axis=1) == y_test)),
                "latency_ms": t_inf_b1,
                "temp": float(b1.temperature.item()),
            },
            "B4": {
                "ece": compute_ece(p_b4_id, y_test),
                "brier": compute_brier_score(p_b4_id, y_test, NUM_STATES),
                "nll": compute_nll(p_b4_id, y_test),
                "acc": float(np.mean(np.argmax(p_b4_id, axis=1) == y_test)),
                "latency_ms": t_inf_b4,
                "temp": float(b4.temperature.item()),
            },
        },
        "distribution_shifts": {},
    }

    # Evaluate across Distribution Shift Regimes (DS-1 through DS-5)
    ds_regimes = ["DS-1", "DS-2", "DS-3", "DS-4", "DS-5"]
    for ds in ds_regimes:
        env_ds = SimUserEnv(seed=seed + 20, noise_level=0.10, ds_regime=ds)
        X_ds, y_ds, _ = env_ds.generate_dataset(3000)
        
        p_b1_ds = b1.predict_probs(X_ds)
        p_b4_ds, unc_b4_ds = b4.predict_probs_and_uncertainty(X_ds)
        
        results["distribution_shifts"][ds] = {
            "B1": {
                "ece": compute_ece(p_b1_ds, y_ds),
                "brier": compute_brier_score(p_b1_ds, y_ds, NUM_STATES),
                "acc": float(np.mean(np.argmax(p_b1_ds, axis=1) == y_ds)),
            },
            "B4": {
                "ece": compute_ece(p_b4_ds, y_ds),
                "brier": compute_brier_score(p_b4_ds, y_ds, NUM_STATES),
                "acc": float(np.mean(np.argmax(p_b4_ds, axis=1) == y_ds)),
                "mean_uncertainty": float(np.mean(unc_b4_ds)),
            },
        }

    return results, b1, b4


def run_experiment_e2(b1_model, b4_model, seed: int = 42) -> Dict[str, Any]:
    """
    E2: Recursive Belief Filtering.
    Evaluates state accuracy, TV distance, and contradiction recovery time.
    """
    np.random.seed(seed)
    num_episodes = 100
    episode_length = 50
    
    # We compare:
    # 1. Moving Average Accumulation (Naive)
    # 2. B2 Bayes Filter with B1 likelihoods
    # 3. B2 Bayes Filter with B4 likelihoods
    # 4. B3 POMDP Tracker
    
    results = {
        "naive_acc": [],
        "b1_bayes_acc": [],
        "b4_bayes_acc": [],
        "b3_pomdp_acc": [],
        "b1_tv_distances": [],
        "b4_tv_distances": [],
        "contradiction_recovery_turns": [],
    }

    env_contra = SimUserEnv(seed=seed + 100, ds_regime="DS-3")

    for ep in range(num_episodes):
        env = SimUserEnv(seed=seed + 200 + ep, noise_level=0.15)
        
        bayes_b1 = B2_BayesFilter()
        bayes_b4 = B2_BayesFilter()
        pomdp_b3 = B3_POMDPTracker()
        
        naive_belief = np.ones(NUM_STATES) / NUM_STATES
        
        ep_states = []
        ep_b1_preds = []
        ep_b4_preds = []
        ep_b3_preds = []
        ep_naive_preds = []
        ep_tv_b1 = []
        ep_tv_b4 = []

        for t in range(episode_length):
            obs, _, gt_state, _ = env.step()
            ep_states.append(gt_state)

            # Likelihoods
            p_b1 = b1_model.predict_probs(obs.reshape(1, -1))[0]
            p_b4 = b4_model.predict_probs(obs.reshape(1, -1))[0]

            # Updates
            b_b1 = bayes_b1.update(p_b1)
            b_b4 = bayes_b4.update(p_b4)
            b_b3 = pomdp_b3.step(p_b1)
            naive_belief = 0.7 * naive_belief + 0.3 * p_b1
            naive_belief /= naive_belief.sum()

            ep_b1_preds.append(np.argmax(b_b1))
            ep_b4_preds.append(np.argmax(b_b4))
            ep_b3_preds.append(np.argmax(b_b3))
            ep_naive_preds.append(np.argmax(naive_belief))

            # Ground truth distribution
            gt_one_hot = np.zeros(NUM_STATES)
            gt_one_hot[gt_state] = 1.0
            ep_tv_b1.append(compute_tv_distance(b_b1, gt_one_hot))
            ep_tv_b4.append(compute_tv_distance(b_b4, gt_one_hot))

        results["naive_acc"].append(float(np.mean(np.array(ep_naive_preds) == np.array(ep_states))))
        results["b1_bayes_acc"].append(float(np.mean(np.array(ep_b1_preds) == np.array(ep_states))))
        results["b4_bayes_acc"].append(float(np.mean(np.array(ep_b4_preds) == np.array(ep_states))))
        results["b3_pomdp_acc"].append(float(np.mean(np.array(ep_b3_preds) == np.array(ep_states))))
        results["b1_tv_distances"].append(float(np.mean(ep_tv_b1)))
        results["b4_tv_distances"].append(float(np.mean(ep_tv_b4)))

    # Evaluate contradiction recovery on DS-3
    for ep in range(30):
        env_c = SimUserEnv(seed=seed + 500 + ep, ds_regime="DS-3")
        bayes = B2_BayesFilter()
        recovered = False
        turns_to_recover = 0
        for t in range(1, 40):
            obs, _, gt_state, _ = env_c.step()
            p_b4 = b4_model.predict_probs(obs.reshape(1, -1))[0]
            b = bayes.update(p_b4)
            if t > 25:
                # Target is COGNITIVE_OVERLOAD (state 2)
                if np.argmax(b) == gt_state:
                    recovered = True
                    break
                turns_to_recover += 1
        results["contradiction_recovery_turns"].append(turns_to_recover if recovered else 15)

    return {
        "naive_mean_acc": float(np.mean(results["naive_acc"])),
        "b1_bayes_mean_acc": float(np.mean(results["b1_bayes_acc"])),
        "b4_bayes_mean_acc": float(np.mean(results["b4_bayes_acc"])),
        "b3_pomdp_mean_acc": float(np.mean(results["b3_pomdp_acc"])),
        "b1_mean_tv": float(np.mean(results["b1_tv_distances"])),
        "b4_mean_tv": float(np.mean(results["b4_tv_distances"])),
        "mean_recovery_turns": float(np.mean(results["contradiction_recovery_turns"])),
    }


def run_experiment_e3(b1_model, b4_model, seed: int = 42) -> Dict[str, Any]:
    """
    E3: Temporal User-State Dynamics.
    Compares static classification against B5 temporal latent Markov model.
    Measures jitter / state-flipping rate and next-state prediction accuracy.
    """
    np.random.seed(seed)
    num_episodes = 80
    episode_length = 50

    static_flips = []
    temporal_flips = []
    static_next_acc = []
    temporal_next_acc = []

    for ep in range(num_episodes):
        env = SimUserEnv(seed=seed + 300 + ep, noise_level=0.25)  # elevated noise spikes
        b5 = B5_TemporalLatentMarkov(b4_model)

        states = []
        static_preds = []
        temporal_preds = []
        next_state_preds = []

        for t in range(episode_length):
            obs, _, gt_state, _ = env.step()
            states.append(gt_state)

            # Static prediction
            p_stat = b1_model.predict_probs(obs.reshape(1, -1))[0]
            pred_stat = np.argmax(p_stat)
            static_preds.append(pred_stat)

            # Temporal dynamic prediction
            post_b, next_pred = b5.step(obs)
            pred_temp = np.argmax(post_b)
            temporal_preds.append(pred_temp)
            next_state_preds.append(np.argmax(next_pred))

        # Flip rate (flipping when true state did not change)
        states = np.array(states)
        static_preds = np.array(static_preds)
        temporal_preds = np.array(temporal_preds)

        static_flip_count = 0
        temp_flip_count = 0
        valid_flips = 0

        for t in range(1, len(states)):
            if states[t] == states[t - 1]:
                valid_flips += 1
                if static_preds[t] != static_preds[t - 1]:
                    static_flip_count += 1
                if temporal_preds[t] != temporal_preds[t - 1]:
                    temp_flip_count += 1

        if valid_flips > 0:
            static_flips.append(static_flip_count / valid_flips)
            temporal_flips.append(temp_flip_count / valid_flips)

        # Next-state accuracy: comparing predicted next state at t against actual state at t+1
        if len(states) > 1:
            actual_next = states[1:]
            stat_next = static_preds[:-1]  # static uses current state as naive next prediction
            temp_next = np.array(next_state_preds[:-1])

            static_next_acc.append(np.mean(stat_next == actual_next))
            temporal_next_acc.append(np.mean(temp_next == actual_next))

    return {
        "static_flip_rate": float(np.mean(static_flips)),
        "temporal_flip_rate": float(np.mean(temporal_flips)),
        "flip_rate_reduction_pct": float((np.mean(static_flips) - np.mean(temporal_flips)) / np.mean(static_flips) * 100.0),
        "static_next_acc": float(np.mean(static_next_acc)),
        "temporal_next_acc": float(np.mean(temporal_next_acc)),
        "next_acc_gain_pct": float((np.mean(temporal_next_acc) - np.mean(static_next_acc)) * 100.0),
    }


def run_experiment_e4(b4_model, seed: int = 42) -> Dict[str, Any]:
    """
    E4: Intent Prediction.
    Evaluates Top-1, Top-2, and confidence calibration of prospective intent.
    Zero future information leakage.
    """
    np.random.seed(seed)
    num_episodes = 50
    episode_length = 40

    b0_prior = B0_MajorityPrior()
    # Prior intent distribution
    prior_intents = np.array([0.27, 0.16, 0.13, 0.08, 0.16, 0.08, 0.06, 0.06])

    b5 = B5_TemporalLatentMarkov(b4_model)
    E_intent = b5.transition_matrix  # emission matrix
    from .sim_user_env import GROUND_TRUTH_INTENT_EMISSION

    top1_matches = []
    top2_matches = []
    prior_top1_matches = []
    all_pred_intent_probs = []
    all_actual_intents = []

    for ep in range(num_episodes):
        env = SimUserEnv(seed=seed + 400 + ep, noise_level=0.10)
        b5.reset()

        # Step 0 to initialize
        obs, intent, _, _ = env.step()

        for t in range(episode_length - 1):
            # Compute belief and prospective intent BEFORE observing turn t+1
            post_b, next_state_pred = b5.step(obs)
            pred_intent_prob = GROUND_TRUTH_INTENT_EMISSION.T @ next_state_pred
            pred_intent_prob /= pred_intent_prob.sum()

            # Now observe turn t+1
            obs, next_intent, _, _ = env.step()

            # Measure accuracy
            top1 = int(np.argmax(pred_intent_prob))
            top2 = np.argsort(pred_intent_prob)[::-1][:2]

            top1_matches.append(top1 == next_intent)
            top2_matches.append(next_intent in top2)
            prior_top1_matches.append(int(np.argmax(prior_intents)) == next_intent)

            all_pred_intent_probs.append(pred_intent_prob)
            all_actual_intents.append(next_intent)

    all_pred_intent_probs = np.array(all_pred_intent_probs)
    all_actual_intents = np.array(all_actual_intents)

    return {
        "top1_accuracy": float(np.mean(top1_matches)),
        "top2_recall": float(np.mean(top2_matches)),
        "prior_top1_accuracy": float(np.mean(prior_top1_matches)),
        "intent_ece": compute_ece(all_pred_intent_probs, all_actual_intents),
        "intent_brier": compute_brier_score(all_pred_intent_probs, all_actual_intents, NUM_INTENTS),
    }


def run_experiment_e5(b4_model, seed: int = 42) -> Dict[str, Any]:
    """
    E5: Prediction Tree (Bounded Horizon Lookahead).
    Evaluates trajectory coverage, node count, latency, and memory.
    """
    np.random.seed(seed)
    num_trials = 200
    
    tree_builder = BoundedPredictionTree(max_depth=3, branching_factor=3, pruning_threshold=0.04)
    b5 = B5_TemporalLatentMarkov(b4_model)

    latencies_us = []
    node_counts = []
    coverage_h1 = []
    coverage_h2 = []
    coverage_h3 = []
    map_coverage_h2 = []

    for trial in range(num_trials):
        env = SimUserEnv(seed=seed + 500 + trial, noise_level=0.10)
        obs, _, _, _ = env.step()
        post_b, _ = b5.step(obs)

        # Build prediction tree
        t0 = time.perf_counter()
        root = tree_builder.build_tree(post_b)
        elapsed_us = (time.perf_counter() - t0) * 1e6
        latencies_us.append(elapsed_us)
        node_counts.append(tree_builder.node_count)

        # Generate ground truth future trajectory of length 3
        future_intents = []
        for _ in range(3):
            _, fut_intent, _, _ = env.step()
            future_intents.append(fut_intent)

        # Check coverage
        coverage_h1.append(tree_builder.check_trajectory_coverage(root, future_intents[:1]))
        coverage_h2.append(tree_builder.check_trajectory_coverage(root, future_intents[:2]))
        coverage_h3.append(tree_builder.check_trajectory_coverage(root, future_intents[:3]))

        # Greedy MAP path coverage for H=2
        leaves = tree_builder.get_leaves(root)
        if leaves:
            best_leaf = max(leaves, key=lambda l: l.path_prob)
            map_coverage_h2.append(best_leaf.intent_history[:2] == future_intents[:2])
        else:
            map_coverage_h2.append(False)

    return {
        "mean_latency_us": float(np.mean(latencies_us)),
        "p95_latency_us": float(np.percentile(latencies_us, 95)),
        "max_latency_us": float(np.max(latencies_us)),
        "mean_node_count": float(np.mean(node_counts)),
        "max_node_count": int(np.max(node_counts)),
        "trajectory_coverage_h1": float(np.mean(coverage_h1)),
        "trajectory_coverage_h2": float(np.mean(coverage_h2)),
        "trajectory_coverage_h3": float(np.mean(coverage_h3)),
        "map_coverage_h2": float(np.mean(map_coverage_h2)),
    }


def run_experiment_e6(b4_model, seed: int = 42) -> Dict[str, Any]:
    """
    E6: Epistemic Action Selection (EIG vs. Reactive Surprise).
    Evaluates entropy reduction, clarification ratio, and redundant questioning.
    """
    np.random.seed(seed)
    num_episodes = 100
    episode_length = 30

    selector = EpistemicActionSelector()
    b5_eig = B5_TemporalLatentMarkov(b4_model)
    b5_react = B5_TemporalLatentMarkov(b4_model)

    eig_entropy_drops = []
    react_entropy_drops = []
    eig_clarify_counts = []
    react_clarify_counts = []
    excess_queries_eig = []
    excess_queries_react = []

    for ep in range(num_episodes):
        env = SimUserEnv(seed=seed + 600 + ep, noise_level=0.15)
        b5_eig.reset()
        b5_react.reset()

        obs, _, gt_state, _ = env.step()

        for t in range(episode_length):
            # EIG policy
            post_b_eig, _ = b5_eig.step(obs)
            h_before_eig = compute_entropy(post_b_eig)
            action_eig = selector.select_action_eig(post_b_eig, scalar_surprise=0.2, obs_entropy=h_before_eig)

            # Step environment with EIG action
            obs_next, _, next_state, _ = env.step(agent_action=action_eig)
            post_b_next_eig, _ = b5_eig.step(obs_next)
            h_after_eig = compute_entropy(post_b_next_eig)

            if "Clarify" in action_eig:
                eig_clarify_counts.append(1)
                eig_entropy_drops.append(max(0.0, h_before_eig - h_after_eig))
                # Redundant query check: if user was already in FOCUSED_TASK, clarifying is redundant
                if gt_state == 0:
                    excess_queries_eig.append(1)
            else:
                eig_clarify_counts.append(0)

            # Reactive Surprise policy comparison
            post_b_react, _ = b5_react.step(obs)
            h_before_react = compute_entropy(post_b_react)
            action_react = selector.select_action_reactive_surprise(post_b_react, scalar_surprise=0.7 if h_before_react > 1.2 else 0.1)

            if "Clarify" in action_react:
                react_clarify_counts.append(1)
                react_entropy_drops.append(max(0.0, h_before_react - h_after_eig))
                if gt_state == 0:
                    excess_queries_react.append(1)
            else:
                react_clarify_counts.append(0)

            obs = obs_next
            gt_state = next_state

    return {
        "eig_clarification_ratio": float(np.mean(eig_clarify_counts)),
        "react_clarification_ratio": float(np.mean(react_clarify_counts)),
        "eig_mean_entropy_reduction": float(np.mean(eig_entropy_drops)) if eig_entropy_drops else 0.0,
        "react_mean_entropy_reduction": float(np.mean(react_entropy_drops)) if react_entropy_drops else 0.0,
        "eig_excess_query_ratio": float(np.sum(excess_queries_eig) / max(1, np.sum(eig_clarify_counts))),
        "react_excess_query_ratio": float(np.sum(excess_queries_react) / max(1, np.sum(react_clarify_counts))),
    }


def run_experiment_e7(b4_model, seed: int = 42) -> Dict[str, Any]:
    """
    E7: Closed-Loop Multi-Turn Stability.
    500 episodes, T = 30 turns.
    Monitors:
      - Deadlocks
      - Belief Flapping
      - Confirmation Bias
      - Attractor Collapse
    """
    np.random.seed(seed)
    num_episodes = 500
    episode_length = 30

    selector = EpistemicActionSelector()
    b5 = B5_TemporalLatentMarkov(b4_model)

    deadlock_count = 0
    flapping_count = 0
    attractor_collapse_count = 0
    total_turns = num_episodes * episode_length

    for ep in range(num_episodes):
        # Sample different regimes: 70% normal, 10% DS-1, 10% DS-2, 10% DS-3
        reg = None
        if ep % 10 == 1:
            reg = "DS-1"
        elif ep % 10 == 2:
            reg = "DS-2"
        elif ep % 10 == 3:
            reg = "DS-3"

        env = SimUserEnv(seed=seed + 700 + ep, noise_level=0.12, ds_regime=reg)
        b5.reset()

        obs, _, _, _ = env.step()
        consecutive_queries = 0
        state_history = []

        for t in range(episode_length):
            post_b, _ = b5.step(obs)
            h = compute_entropy(post_b)
            pred_state = np.argmax(post_b)
            state_history.append(pred_state)

            action = selector.select_action_eig(post_b, scalar_surprise=0.2, obs_entropy=h)

            if "Clarify" in action:
                consecutive_queries += 1
                if consecutive_queries > 5:
                    # Query deadlock failure
                    deadlock_count += 1
                    break
            else:
                consecutive_queries = 0

            # Step environment
            obs, _, _, _ = env.step(agent_action=action)

        # Flapping check: alternating state sequence A -> B -> A -> B for >= 4 turns
        for i in range(len(state_history) - 4):
            w = state_history[i:i + 4]
            if w[0] == w[2] and w[1] == w[3] and w[0] != w[1]:
                flapping_count += 1
                break

        # Attractor collapse check: entropy drops permanently < 1e-4 and never recovers
        if compute_entropy(post_b) < 1e-4:
            attractor_collapse_count += 1

    return {
        "num_episodes": num_episodes,
        "total_turns": total_turns,
        "deadlock_episodes": deadlock_count,
        "deadlock_rate": float(deadlock_count / num_episodes),
        "flapping_episodes": flapping_count,
        "flapping_rate": float(flapping_count / num_episodes),
        "attractor_collapse_episodes": attractor_collapse_count,
        "attractor_collapse_rate": float(attractor_collapse_count / num_episodes),
        "loop_stability_rate": float(1.0 - (deadlock_count + flapping_count + attractor_collapse_count) / num_episodes),
    }


def main():
    print("=" * 70)
    print("Starting Lucia Phase 22-X Isolated Research Evaluation")
    print("Governance: AGENTS.md §0, §6, §7 | Scope: RESEARCH ONLY")
    print("Hardware: CPU-Only | Zero GPU VRAM | Zero Production Diff")
    print("=" * 70)

    seed = 42
    env_train = SimUserEnv(seed=seed, noise_level=0.10)
    env_val = SimUserEnv(seed=seed + 1, noise_level=0.10)

    # 1. Run E1
    print("\n--- Running Experiment E1: Observation Calibration ---")
    results_e1, b1, b4 = run_experiment_e1(env_train, env_val, seed=seed)
    print("E1 In-Distribution ECE: B0={:.4f}, B1={:.4f}, B4={:.4f}".format(
        results_e1["in_distribution"]["B0"]["ece"],
        results_e1["in_distribution"]["B1"]["ece"],
        results_e1["in_distribution"]["B4"]["ece"],
    ))
    print("E1 DS-1 (Noise Surge) ECE: B1={:.4f}, B4={:.4f}".format(
        results_e1["distribution_shifts"]["DS-1"]["B1"]["ece"],
        results_e1["distribution_shifts"]["DS-1"]["B4"]["ece"],
    ))

    # 2. Run E2
    print("\n--- Running Experiment E2: Recursive Belief Update ---")
    results_e2 = run_experiment_e2(b1, b4, seed=seed)
    print("E2 State Accuracy: Naive={:.2f}%, B1-Bayes={:.2f}%, B4-Bayes={:.2f}%".format(
        results_e2["naive_mean_acc"] * 100,
        results_e2["b1_bayes_mean_acc"] * 100,
        results_e2["b4_bayes_mean_acc"] * 100,
    ))
    print("E2 Contradiction Recovery Turns: {:.2f}".format(results_e2["mean_recovery_turns"]))

    # 3. Run E3
    print("\n--- Running Experiment E3: Temporal Dynamics ---")
    results_e3 = run_experiment_e3(b1, b4, seed=seed)
    print("E3 State Flip Rate: Static={:.4f}, Temporal={:.4f} (-{:.1f}%)".format(
        results_e3["static_flip_rate"],
        results_e3["temporal_flip_rate"],
        results_e3["flip_rate_reduction_pct"],
    ))
    print("E3 Next-State Accuracy: Static={:.2f}%, Temporal={:.2f}% (+{:.1f}%)".format(
        results_e3["static_next_acc"] * 100,
        results_e3["temporal_next_acc"] * 100,
        results_e3["next_acc_gain_pct"],
    ))

    # 4. Run E4
    print("\n--- Running Experiment E4: Intent Prediction ---")
    results_e4 = run_experiment_e4(b4, seed=seed)
    print("E4 Prospective Intent: Top-1={:.2f}%, Top-2={:.2f}%, Prior={:.2f}%".format(
        results_e4["top1_accuracy"] * 100,
        results_e4["top2_recall"] * 100,
        results_e4["prior_top1_accuracy"] * 100,
    ))
    print("E4 Intent ECE={:.4f}, Brier={:.4f}".format(results_e4["intent_ece"], results_e4["intent_brier"]))

    # 5. Run E5
    print("\n--- Running Experiment E5: Prediction Tree ---")
    results_e5 = run_experiment_e5(b4, seed=seed)
    print("E5 Trajectory Coverage: H=1: {:.2f}%, H=2: {:.2f}%, H=3: {:.2f}% (MAP H=2: {:.2f}%)".format(
        results_e5["trajectory_coverage_h1"] * 100,
        results_e5["trajectory_coverage_h2"] * 100,
        results_e5["trajectory_coverage_h3"] * 100,
        results_e5["map_coverage_h2"] * 100,
    ))
    print("E5 Mean Latency: {:.1f} us (Max: {:.1f} us), Mean Nodes: {:.1f}".format(
        results_e5["mean_latency_us"],
        results_e5["max_latency_us"],
        results_e5["mean_node_count"],
    ))

    # 6. Run E6
    print("\n--- Running Experiment E6: Epistemic Action Selection ---")
    results_e6 = run_experiment_e6(b4, seed=seed)
    print("E6 Clarification Ratio: EIG={:.2f}%, Reactive={:.2f}%".format(
        results_e6["eig_clarification_ratio"] * 100,
        results_e6["react_clarification_ratio"] * 100,
    ))
    print("E6 Mean Entropy Drop: EIG={:.4f} nats, Reactive={:.4f} nats".format(
        results_e6["eig_mean_entropy_reduction"],
        results_e6["react_mean_entropy_reduction"],
    ))

    # 7. Run E7
    print("\n--- Running Experiment E7: Closed-Loop Multi-Turn Stability ---")
    results_e7 = run_experiment_e7(b4, seed=seed)
    print("E7 Stability Rate: {:.2f}% (Deadlocks: {}, Flapping: {}, Collapse: {})".format(
        results_e7["loop_stability_rate"] * 100,
        results_e7["deadlock_episodes"],
        results_e7["flapping_episodes"],
        results_e7["attractor_collapse_episodes"],
    ))

    # Save comprehensive results JSON
    full_output = {
        "experiment_e1": results_e1,
        "experiment_e2": results_e2,
        "experiment_e3": results_e3,
        "experiment_e4": results_e4,
        "experiment_e5": results_e5,
        "experiment_e6": results_e6,
        "experiment_e7": results_e7,
    }
    
    out_dir = os.path.join("evaluation_artifacts", "phase22_x")
    os.makedirs(out_dir, exist_ok=True)
    out_file = os.path.join(out_dir, "raw_measurements.json")
    with open(out_file, "w") as f:
        json.dump(full_output, f, indent=2)
    print(f"\nAll measurements saved to: {out_file}")
    print("=" * 70)


if __name__ == "__main__":
    main()
