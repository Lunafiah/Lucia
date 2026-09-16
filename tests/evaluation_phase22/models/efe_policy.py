"""
tests/evaluation_phase22/models/efe_policy.py

Expected Free Energy (EFE) Policy & Cost Model.
Formulates G(a) = -alpha_pragm * V_pragm(a) - beta_epist(E,C) * EIG(a) + C(a)
and selects a* = argmin_a G(a).
"""

from __future__ import annotations

import math
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Tuple

import numpy as np

from tests.evaluation_phase22.models.actions import ACTION_REGISTRY, ActionMetadata, ActionType
from tests.evaluation_phase22.models.ligp import LIGPConfig, compute_expected_information_gain


@dataclass(frozen=True)
class SocialCostConfig:
    """Configurable coefficients for social disruption cost of a2."""
    gamma_0: float = 0.20       # Base social disruption penalty
    gamma_1: float = 0.15       # Exponential fatigue coefficient
    tau_q: float = 2.0          # Decay rate for rolling query count
    mu_trust: float = 0.20      # Mitigating trust factor

    def __post_init__(self) -> None:
        if self.gamma_0 < 0.0 or self.gamma_1 < 0.0 or self.tau_q <= 0.0 or self.mu_trust < 0.0:
            raise ValueError("Social cost parameters must be valid and positive.")


@dataclass(frozen=True)
class EFEConfig:
    """Configurable coefficients for Expected Free Energy policy."""
    alpha_pragm: float = 1.0    # Pragmatic value weight
    beta_0: float = 2.0         # Baseline epistemic exploration weight
    social_cost: SocialCostConfig = field(default_factory=SocialCostConfig)
    ligp: LIGPConfig = field(default_factory=LIGPConfig)

    def __post_init__(self) -> None:
        if self.alpha_pragm < 0.0 or self.beta_0 < 0.0:
            raise ValueError("EFE coefficients must be non-negative.")


def compute_social_cost(
    action: ActionType,
    n_recent_queries: int,
    r_trust: float,
    config: Optional[SocialCostConfig] = None,
) -> float:
    """
    Compute social disruption cost:
    c_social(a) = 0.0 for internal actions {a1, a3, a4, a5, a6}
    c_social(a2) = max(0.0, gamma_0 + gamma_1 * exp(N_queries / tau_q) - mu_trust * R_trust)
    """
    if action != ActionType.A2_EXTERNAL_CLARIFICATION:
        return 0.0

    cfg = config if config is not None else SocialCostConfig()
    n_q = max(0, min(5, int(n_recent_queries)))
    r_t = float(np.clip(r_trust, 0.0, 1.0))

    cost = cfg.gamma_0 + cfg.gamma_1 * math.exp(n_q / cfg.tau_q) - cfg.mu_trust * r_t
    return float(max(0.0, cost))


def compute_compute_cost(action: ActionType) -> float:
    """Estimated CPU compute cost / latency penalty."""
    return ACTION_REGISTRY[action].base_compute_cost


def compute_total_cost(
    action: ActionType,
    n_recent_queries: int,
    r_trust: float,
    config: Optional[SocialCostConfig] = None,
) -> float:
    """Total cost C(a) = c_compute(a) + c_social(a)."""
    return compute_compute_cost(action) + compute_social_cost(action, n_recent_queries, r_trust, config)


def compute_homeostatic_beta(energy: float, cognitive_load: float, beta_0: float = 2.0) -> float:
    """
    Homeostatic epistemic weighting:
    beta_epist(E, C) = beta_0 * E * (1.0 - 0.5 * C)
    Where E in [0, 1], C in [0, 1].
    """
    e = float(np.clip(energy, 0.0, 1.0))
    c = float(np.clip(cognitive_load, 0.0, 1.0))
    return float(max(0.0, beta_0 * e * (1.0 - 0.5 * c)))


def compute_pragmatic_value(
    action: ActionType,
    contradiction_present: bool = False,
    energy: float = 1.0,
    tension: float = 0.0,
) -> float:
    """
    Pragmatic value V_pragm(a):
    - a1: Immediate response default value 1.0
    - a5: Deliberative reasoning mode 0.70 if contradiction present, else 0.0
    - a6: Somatic pause 0.60 if low energy (< 0.30) or acute tension (>= 0.70), else 0.0
    - a2, a3, a4: Purely epistemic, pragmatic value 0.0
    """
    if action == ActionType.A1_IMMEDIATE_RESPONSE:
        return 1.0
    elif action == ActionType.A5_DEEP_REASONING_MODE_SHIFT:
        return 0.70 if contradiction_present else 0.0
    elif action == ActionType.A6_WAIT_CONVERSATIONAL_PAUSE:
        return 0.60 if (energy < 0.30 or tension >= 0.70) else 0.0
    return 0.0


@dataclass(frozen=True)
class ActionValuation:
    """Valuation components for a single candidate action under EFE."""
    action: ActionType
    g_value: float              # Total EFE objective value G(a)
    pragmatic_term: float       # -alpha_pragm * V_pragm(a)
    epistemic_term: float       # -beta_epist * EIG(a)
    compute_cost: float         # c_compute(a)
    social_cost: float          # c_social(a)
    eig: float                  # EIG(a)


class EFEPolicyEvaluator:
    """
    Evaluates candidate actions under Expected Free Energy objective.
    CPU-only numerical execution within sub-millisecond latency.
    """

    def __init__(self, config: Optional[EFEConfig] = None) -> None:
        self.config = config if config is not None else EFEConfig()

    def evaluate_action(
        self,
        action: ActionType,
        delta_h_knowledge: float,
        delta_h_memory: float,
        energy: float,
        cognitive_load: float,
        tension: float,
        r_trust: float,
        n_recent_queries: int,
        contradiction_present: bool,
        unweighted_beta: bool = False,
    ) -> ActionValuation:
        """
        Evaluate single action under EFE objective:
        G(a) = -alpha_pragm * V_pragm(a) - beta_epist(E,C) * EIG(a) + C(a)
        """
        eig = compute_expected_information_gain(
            action, delta_h_knowledge, delta_h_memory, self.config.ligp
        )

        beta = (
            self.config.beta_0
            if unweighted_beta
            else compute_homeostatic_beta(energy, cognitive_load, self.config.beta_0)
        )

        v_pragm = compute_pragmatic_value(action, contradiction_present, energy, tension)
        pragm_term = -self.config.alpha_pragm * v_pragm
        epist_term = -beta * eig

        c_comp = compute_compute_cost(action)
        c_soc = compute_social_cost(action, n_recent_queries, r_trust, self.config.social_cost)
        total_c = c_comp + c_soc

        g_val = pragm_term + epist_term + total_c

        return ActionValuation(
            action=action,
            g_value=float(g_val),
            pragmatic_term=float(pragm_term),
            epistemic_term=float(epist_term),
            compute_cost=float(c_comp),
            social_cost=float(c_soc),
            eig=float(eig),
        )

    def select_action_c2(
        self,
        delta_h_knowledge_map: Dict[ActionType, float],
        delta_h_memory_map: Dict[ActionType, float],
        energy: float,
        cognitive_load: float,
        tension: float,
        r_trust: float,
        n_recent_queries: int,
        contradiction_present: bool,
        unweighted_beta: bool = False,
    ) -> Tuple[ActionType, Dict[ActionType, ActionValuation]]:
        """
        Condition 2: Full Prospective Epistemic Foraging.
        Selects a* = argmin_a G(a).
        """
        valuations: Dict[ActionType, ActionValuation] = {}
        for action in ActionType:
            d_k = delta_h_knowledge_map.get(action, 0.0)
            d_m = delta_h_memory_map.get(action, 0.0)
            val = self.evaluate_action(
                action=action,
                delta_h_knowledge=d_k,
                delta_h_memory=d_m,
                energy=energy,
                cognitive_load=cognitive_load,
                tension=tension,
                r_trust=r_trust,
                n_recent_queries=n_recent_queries,
                contradiction_present=contradiction_present,
                unweighted_beta=unweighted_beta,
            )
            valuations[action] = val

        # argmin over G(a), break ties deterministically by action definition order
        best_action = min(valuations.keys(), key=lambda a: (valuations[a].g_value, a.value))
        return best_action, valuations

    @staticmethod
    def select_action_c0(
        surprise_s: float,
        tension: float,
        contradiction_present: bool = False,
    ) -> ActionType:
        """
        Condition 0: Canonical Baseline (Phase 21 behavior).
        Retrospective surprise threshold S_t > 0.60 or tension >= 0.70 triggers deliberative mode.
        No prospective epistemic policy; does NOT select epistemic foraging actions (a2, a3, a4).
        """
        if surprise_s > 0.60 or tension >= 0.70:
            if contradiction_present:
                return ActionType.A5_DEEP_REASONING_MODE_SHIFT
            # Standard deliberative generation mode (k=2) is a pragmatic response variation
            return ActionType.A1_IMMEDIATE_RESPONSE
        return ActionType.A1_IMMEDIATE_RESPONSE

    @staticmethod
    def select_action_c1(
        surprise_s: float,
    ) -> ActionType:
        """
        Condition 1: Heuristic Stress-Test Control.
        Operationalized heuristic policy triggered by S_t >= 0.15.
        When S_t >= 0.15, selects a2 (external clarification) greedily as the heuristic operationalization,
        regardless of whether actual semantic uncertainty exists.
        When S_t < 0.15, falls back to a1.
        """
        if surprise_s >= 0.15:
            return ActionType.A2_EXTERNAL_CLARIFICATION
        return ActionType.A1_IMMEDIATE_RESPONSE
