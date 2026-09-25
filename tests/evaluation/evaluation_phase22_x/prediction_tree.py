"""
Bounded Prediction Tree and Epistemic Action Selection for Phase 22-X.
"""
from typing import Dict, List, Tuple, Optional
import numpy as np

from .sim_user_env import (
    NUM_STATES,
    NUM_INTENTS,
    GROUND_TRUTH_TRANSITION,
    GROUND_TRUTH_INTENT_EMISSION,
)
from .metrics import compute_entropy


class TreeNode:
    """
    Node in the Bounded Prospective Prediction Tree.
    """
    def __init__(
        self,
        belief: np.ndarray,
        depth: int,
        path_prob: float = 1.0,
        intent_history: Optional[List[int]] = None,
    ):
        self.belief = belief.copy()
        self.depth = depth
        self.path_prob = path_prob
        self.intent_history = list(intent_history) if intent_history is not None else []
        self.children: List[TreeNode] = []

    def is_leaf(self) -> bool:
        return len(self.children) == 0


class BoundedPredictionTree:
    """
    Bounded Prediction Tree (H <= 3, B <= 3).
    Expands prospective intent hypotheses and propagates belief states.
    """
    def __init__(
        self,
        max_depth: int = 3,
        branching_factor: int = 3,
        pruning_threshold: float = 0.05,
        transition_matrix: Optional[np.ndarray] = None,
        intent_matrix: Optional[np.ndarray] = None,
    ):
        self.max_depth = max_depth
        self.branching_factor = branching_factor
        self.pruning_threshold = pruning_threshold
        self.transition_matrix = transition_matrix if transition_matrix is not None else GROUND_TRUTH_TRANSITION.copy()
        self.intent_matrix = intent_matrix if intent_matrix is not None else GROUND_TRUTH_INTENT_EMISSION.copy()
        self.node_count = 0

    def build_tree(self, root_belief: np.ndarray) -> TreeNode:
        self.node_count = 1
        root = TreeNode(belief=root_belief, depth=0, path_prob=1.0)
        self._expand(root)
        return root

    def _expand(self, node: TreeNode):
        if node.depth >= self.max_depth:
            return

        # 1. Predict next state prior: P(s_{t+h+1}) = T^T @ belief
        pred_state = self.transition_matrix.T @ node.belief
        
        # 2. Prospective intent distribution: P(intent) = E^T @ pred_state
        pred_intent_probs = self.intent_matrix.T @ pred_state
        
        # 3. Select top-B intent branches
        top_intent_indices = np.argsort(pred_intent_probs)[::-1][:self.branching_factor]

        for intent_idx in top_intent_indices:
            branch_intent_prob = pred_intent_probs[intent_idx]
            child_path_prob = node.path_prob * branch_intent_prob

            # Pruning condition
            if child_path_prob < self.pruning_threshold:
                continue

            # Update child belief conditioned on intent observation
            # P(s | intent) \propto P(intent | s) * P(s)
            likelihood = self.intent_matrix[:, intent_idx]
            unnorm = likelihood * pred_state
            if np.sum(unnorm) > 1e-12:
                child_belief = unnorm / np.sum(unnorm)
            else:
                child_belief = pred_state.copy()

            child_node = TreeNode(
                belief=child_belief,
                depth=node.depth + 1,
                path_prob=child_path_prob,
                intent_history=node.intent_history + [intent_idx],
            )
            node.children.append(child_node)
            self.node_count += 1

            self._expand(child_node)

    def get_leaves(self, root: TreeNode) -> List[TreeNode]:
        leaves = []
        def _collect(n: TreeNode):
            if n.is_leaf():
                leaves.append(n)
            else:
                for c in n.children:
                    _collect(c)
        _collect(root)
        return leaves

    def check_trajectory_coverage(self, root: TreeNode, true_intents: List[int]) -> bool:
        """
        Check if the true multi-step trajectory is covered within the tree.
        """
        depth_to_check = min(len(true_intents), self.max_depth)
        target_prefix = true_intents[:depth_to_check]
        
        leaves = self.get_leaves(root)
        for leaf in leaves:
            if leaf.intent_history[:depth_to_check] == target_prefix:
                return True
        return False


class EpistemicActionSelector:
    """
    Epistemic Action Selection comparing Expected Information Gain (EIG)
    vs. Reactive Scalar Surprise.
    """
    ACTIONS = [
        "Proceed",          # Exploit / Pragmatic action
        "ClarifySpecific", # Epistemic query targeting ambiguous state
        "ClarifyOpen",     # Broad clarification
        "Summarize",       # Pragmatic alignment
        "WaitPassive",     # Zero cost passive observation
    ]

    def __init__(
        self,
        lambda_pragm: float = 1.0,
        lambda_epist: float = 1.2,
        clarification_cost: float = 0.25,
    ):
        self.lambda_pragm = lambda_pragm
        self.lambda_epist = lambda_epist
        self.clarification_cost = clarification_cost

    def compute_action_values(
        self,
        current_belief: np.ndarray,
        scalar_surprise: float,
        obs_entropy: float,
    ) -> Dict[str, float]:
        """
        Compute action valuation V(a) = \lambda_p Q(a) + \lambda_e EIG(a) - c(a).
        """
        values = {}
        h_current = compute_entropy(current_belief)

        for a in self.ACTIONS:
            # Pragmatic base value: proceeding is favored when belief is confident
            if a == "Proceed":
                q_pragm = 1.0 - (h_current / np.log(NUM_STATES))
                eig = 0.0
                cost = 0.0
            elif a == "ClarifySpecific":
                q_pragm = 0.2
                # High EIG if current belief is ambiguous/high entropy
                eig = max(0.0, h_current - 0.4)
                cost = self.clarification_cost
            elif a == "ClarifyOpen":
                q_pragm = 0.1
                eig = max(0.0, h_current - 0.6)
                cost = self.clarification_cost * 1.2
            elif a == "Summarize":
                q_pragm = 0.5
                eig = max(0.0, h_current - 0.8)
                cost = self.clarification_cost * 0.5
            elif a == "WaitPassive":
                q_pragm = 0.1
                eig = 0.0
                cost = 0.0
            else:
                q_pragm, eig, cost = 0.0, 0.0, 0.0

            v = self.lambda_pragm * q_pragm + self.lambda_epist * eig - cost
            values[a] = float(v)

        return values

    def select_action_eig(
        self,
        current_belief: np.ndarray,
        scalar_surprise: float,
        obs_entropy: float,
    ) -> str:
        values = self.compute_action_values(current_belief, scalar_surprise, obs_entropy)
        return max(values, key=values.get)

    def select_action_reactive_surprise(
        self,
        current_belief: np.ndarray,
        scalar_surprise: float,
        surprise_threshold: float = 0.65,
    ) -> str:
        """
        Baseline reactive policy: Clarify only when scalar surprise exceeds threshold.
        """
        if scalar_surprise > surprise_threshold:
            return "ClarifySpecific"
        return "Proceed"
