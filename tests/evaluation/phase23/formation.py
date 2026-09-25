"""
Phase 23 Semantic Formation Microbenchmark v0.2 — Formation Engine
Implements Track 1 (U1 causal intention & graph formation),
Track 4 (U4 closed-loop continuous limbic-semantic coupling),
and Track 5 (U5 genuine multi-turn revisions with entity merges & belief corrections).
"""
import time
from typing import Dict, List, Optional, Any, Tuple
import numpy as np
from .config import (
    ContinuousCognitiveState,
    CommunicativeIntention,
    SemanticGraph,
    SemanticNode,
    SemanticEdge,
)


class SemanticFormationEngine:
    """
    Core non-LLM semantic formation engine.
    Causally derives communicative intentions and structured semantic graphs
    directly from continuous cognitive state variables.
    """

    def __init__(self):
        self.generation_count = 0

    def derive_intention(
        self, cog_state: ContinuousCognitiveState, topic_entities: List[str]
    ) -> CommunicativeIntention:
        """
        Causally derives CommunicativeIntention from continuous variables:
        [P, A, D, energy, trust, entropy].
        """
        p, a, d = float(cog_state.pad[0]), float(cog_state.pad[1]), float(cog_state.pad[2])
        energy = float(cog_state.somatic_energy)
        trust = float(cog_state.relational_trust)
        entropy = float(cog_state.epistemic_entropy)

        # 1. Causal Dialogue Act Selection
        if cog_state.active_breach or (p < -0.20 and trust < 0.35):
            act_type = "ASSERT_BOUNDARY"
            is_guarded = True
            has_rupture = True
            has_repair = False
        elif cog_state.bilateral_repair:
            act_type = "REPAIR_BILATERAL"
            is_guarded = False
            has_rupture = False
            has_repair = True
        elif entropy > 0.60 or (a > 0.20 and entropy > 0.40):
            act_type = "CLARIFY_QUERY"
            is_guarded = False
            has_rupture = False
            has_repair = False
        elif p > 0.15 and trust >= 0.50:
            act_type = "PROPOSE"
            is_guarded = False
            has_rupture = False
            has_repair = False
        else:
            act_type = "INFORM"
            is_guarded = False
            has_rupture = False
            has_repair = False

        # 2. Relational Tier Mapping from Continuous Trust
        if trust < 0.20:
            rel_tier = "T0_STRANGER"
        elif trust < 0.45:
            rel_tier = "T1_ACQUAINTANCE"
        elif trust < 0.70:
            rel_tier = "T2_COLLABORATOR"
        elif trust < 0.88:
            rel_tier = "T3_COMPANION"
        else:
            rel_tier = "T4_CONFIDANT"

        # 3. Dynamic Cardinality Bounded by Somatic Energy
        if energy < 0.30:
            max_entities = 1
        elif energy < 0.70:
            max_entities = 2
        else:
            max_entities = min(len(topic_entities), 4)

        selected_entities = topic_entities[:max(1, max_entities)]

        # 4. Epistemic Confidence as inverse of entropy
        confidence = float(np.clip(1.0 - (entropy / 2.0), 0.10, 1.0))

        # 5. Urgency derived from arousal and energy
        urgency = float(np.clip(0.5 + 0.3 * a - 0.2 * (1.0 - energy), 0.1, 1.0))

        return CommunicativeIntention(
            act_type=act_type,
            target_entities=selected_entities,
            affective_drive=cog_state.pad,
            relational_tier=rel_tier,
            epistemic_confidence=confidence,
            is_guarded=is_guarded,
            has_rupture=has_rupture,
            has_repair=has_repair,
            urgency=urgency,
            target_cardinality=len(selected_entities),
            metadata={"somatic_energy": energy, "trust": trust, "entropy": entropy},
        )

    def form_semantic_graph(self, intention: CommunicativeIntention) -> Tuple[SemanticGraph, float]:
        """
        Expands CommunicativeIntention into a grounded variable-size SemanticGraph.
        Returns (SemanticGraph, latency_ms).
        """
        t0 = time.perf_counter()
        graph = SemanticGraph(
            epistemic_confidence=intention.epistemic_confidence,
            intention_source=intention,
        )

        # 1. Root Predicate
        root_id = "ROOT_PRED"
        predicate_label = f"act_{intention.act_type.lower()}"
        root_node = SemanticNode(
            node_id=root_id,
            node_type="predicate",
            label=predicate_label,
            salience=intention.urgency,
            epistemic_modality="CERTAIN" if intention.epistemic_confidence >= 0.8 else "POSSIBLE",
        )
        graph.add_node(root_node)

        # 2. Agent Nodes
        lucia_node = SemanticNode(
            node_id="AGENT_LUCIA",
            node_type="entity",
            label="Lucia",
            provenance_anchor="anchor_self_identity",
            salience=0.9,
        )
        user_node = SemanticNode(
            node_id="AGENT_USER",
            node_type="entity",
            label="User",
            provenance_anchor="anchor_user_primary",
            salience=0.95,
        )
        graph.add_node(lucia_node)
        graph.add_node(user_node)

        # 3. Connect Agents by Act Type
        if intention.act_type in ["INFORM", "PROPOSE", "ASSERT_BOUNDARY"]:
            graph.add_edge(SemanticEdge(source_id=root_id, target_id=lucia_node.node_id, relation_type="AGENT"))
            graph.add_edge(SemanticEdge(source_id=root_id, target_id=user_node.node_id, relation_type="BENEFICIARY"))
        elif intention.act_type == "CLARIFY_QUERY":
            graph.add_edge(SemanticEdge(source_id=root_id, target_id=lucia_node.node_id, relation_type="EXPERIENCER"))
            graph.add_edge(SemanticEdge(source_id=root_id, target_id=user_node.node_id, relation_type="PATIENT"))
        elif intention.act_type == "REPAIR_BILATERAL":
            graph.add_edge(SemanticEdge(source_id=root_id, target_id=lucia_node.node_id, relation_type="AGENT"))
            graph.add_edge(SemanticEdge(source_id=root_id, target_id=user_node.node_id, relation_type="AGENT"))

        # 4. Bind Target Entities
        for i, ent in enumerate(intention.target_entities):
            ent_id = f"ENT_{i}_{ent.replace(' ', '_').lower()}"
            is_negated = ent.startswith("NOT_") or ent.startswith("neg_")
            clean_label = ent.replace("NOT_", "").replace("neg_", "")

            ent_node = SemanticNode(
                node_id=ent_id,
                node_type="entity",
                label=clean_label,
                provenance_anchor=f"anchor_sdm_{clean_label}",
                salience=0.85,
                negated=is_negated,
            )
            graph.add_node(ent_node)

            assigned_role = "THEME" if i == 0 else ("PATIENT" if i == 1 else "LOCATION")
            graph.add_edge(SemanticEdge(source_id=root_id, target_id=ent_id, relation_type=assigned_role))

        # 5. Apply Relational & Boundary Constraints
        if intention.is_guarded:
            guard_node = SemanticNode(
                node_id="GUARD_STANCE",
                node_type="modifier",
                label="defensive_hold",
                salience=1.0,
            )
            graph.add_node(guard_node)
            graph.add_edge(SemanticEdge(source_id=root_id, target_id="GUARD_STANCE", relation_type="MODIFIER"))

        if intention.has_rupture:
            root_node.epistemic_modality = "DOUBTFUL"
        if intention.has_repair:
            root_node.epistemic_modality = "CERTAIN"

        latency_ms = (time.perf_counter() - t0) * 1000.0
        self.generation_count += 1
        return graph, latency_ms


class LimbicSemanticCoupler:
    """
    Track 4 (U4): Closed-loop bidirectional coupling between continuous MT-LNN limbic ODE
    and discrete semantic state.
    """

    def __init__(self, deadband: float = 0.08, gamma: float = 0.25):
        self.deadband = deadband
        self.gamma = gamma
        self.philia = np.array([0.25, -0.05, 0.05])
        self.w_feedback = np.array([0.05, 0.02, 0.03])  # Weight matrix for semantic feedback
        self.previous_stance = "NEUTRAL"
        self.flap_count = 0
        self.step_count = 0

    def step_closed_loop(
        self,
        current_pad: np.ndarray,
        current_graph: SemanticGraph,
        dt: float = 0.1,
        external_noise: Optional[np.ndarray] = None,
    ) -> Tuple[np.ndarray, SemanticGraph, Dict[str, Any]]:
        """
        Executes one closed-loop step:
        1. Semantic feedback vector s_sem is extracted from current_graph.
        2. ODE dx/dt = -gamma*(x - philia) + W_f * s_sem + noise updates PAD.
        3. Updated PAD modulates graph salience and stance with deadband hysteresis.
        """
        # 1. Semantic Feedback Vector: [valence_bias, urgency, defensiveness]
        is_guarded = "GUARD_STANCE" in current_graph.nodes
        urgency = current_graph.nodes.get("ROOT_PRED", SemanticNode("dummy", "pred", "d")).salience
        confidence = current_graph.epistemic_confidence

        s_sem = np.array([
            0.10 * (confidence - 0.5),
            0.15 * (urgency - 0.5),
            -0.20 if is_guarded else 0.05,
        ])

        # 2. ODE Update
        noise = external_noise if external_noise is not None else np.zeros(3)
        dpad = -self.gamma * (current_pad - self.philia) + (self.w_feedback * s_sem) + noise
        next_pad = np.clip(current_pad + dpad * dt, -1.0, 1.0)

        # 3. Apply Deadband Hysteresis for Stance Modulation
        p = float(next_pad[0])
        candidate_stance = "NEUTRAL"
        if p < -0.30 - self.deadband:
            candidate_stance = "GUARDED"
        elif p > 0.25 + self.deadband:
            candidate_stance = "RECEPTIVE"
        elif self.previous_stance in ["GUARDED", "RECEPTIVE"]:
            if self.previous_stance == "GUARDED" and p < -0.30 + self.deadband:
                candidate_stance = "GUARDED"
            elif self.previous_stance == "RECEPTIVE" and p > 0.25 - self.deadband:
                candidate_stance = "RECEPTIVE"

        if candidate_stance != self.previous_stance:
            if self.step_count > 0:
                self.flap_count += 1
            self.previous_stance = candidate_stance

        # 4. Modulate Graph Salience
        new_urgency = float(np.clip(0.5 + 0.3 * next_pad[1], 0.1, 1.0))
        for node in current_graph.nodes.values():
            if node.node_type == "predicate":
                node.salience = new_urgency
            elif node.node_id == "GUARD_STANCE":
                node.salience = 1.0 if candidate_stance == "GUARDED" else 0.0

        self.step_count += 1
        flapping_rate = float(self.flap_count / max(1, self.step_count))

        diagnostics = {
            "stance": candidate_stance,
            "urgency": new_urgency,
            "flapping_rate": flapping_rate,
            "dpad": dpad,
        }
        return next_pad, current_graph, diagnostics

    @staticmethod
    def compute_lyapunov_exponent(trajectories: np.ndarray) -> float:
        """
        Computes maximal Lyapunov exponent across closed-loop trajectories.
        Must satisfy lambda_max <= 0.0 for asymptotic stability.
        """
        diffs = np.linalg.norm(np.diff(trajectories, axis=0), axis=1)
        ratios = diffs[1:] / np.maximum(diffs[:-1], 1e-8)
        log_ratios = np.log(np.maximum(ratios, 1e-8))
        return float(np.mean(log_ratios))


class IncrementalStateUpdater:
    """
    Track 5 (U5): Applies genuine multi-turn semantic operations:
    additions, deletions, conflict resolution, entity mergers, and attribute updates.
    """

    @staticmethod
    def apply_delta(
        graph: SemanticGraph, delta_action: str, target_id: str, payload: Dict[str, Any]
    ) -> Tuple[SemanticGraph, float]:
        """
        Applies a genuine localized semantic revision.
        delta_action: 'ADD_ENTITY' | 'UPDATE_ATTRIBUTE' | 'CORRECT_BELIEF' | 'MERGE_ENTITIES' | 'PRUNE_NODE'
        """
        t0 = time.perf_counter()
        updated_graph = graph.clone()

        if delta_action == "ADD_ENTITY":
            new_node = SemanticNode(
                node_id=target_id,
                node_type=payload.get("node_type", "entity"),
                label=payload.get("label", target_id),
                attributes=payload.get("attributes", {}),
                provenance_anchor=payload.get("anchor", None),
            )
            updated_graph.add_node(new_node)
            src = payload.get("source_id", "ROOT_PRED")
            rel = payload.get("relation_type", "THEME")
            updated_graph.add_edge(SemanticEdge(source_id=src, target_id=target_id, relation_type=rel))

        elif delta_action == "UPDATE_ATTRIBUTE":
            if target_id in updated_graph.nodes:
                for k, v in payload.items():
                    updated_graph.nodes[target_id].attributes[k] = v

        elif delta_action == "CORRECT_BELIEF":
            if target_id in updated_graph.nodes:
                node = updated_graph.nodes[target_id]
                node.negated = payload.get("negated", not node.negated)
                node.epistemic_modality = payload.get("modality", "CERTAIN")
                if "new_label" in payload:
                    node.label = payload["new_label"]

        elif delta_action == "MERGE_ENTITIES":
            # Genuine entity merger: merge target_id into canonical_id
            canonical_id = payload["canonical_id"]
            if target_id in updated_graph.nodes and canonical_id in updated_graph.nodes:
                target_node = updated_graph.nodes[target_id]
                canonical_node = updated_graph.nodes[canonical_id]
                # Merge attributes
                canonical_node.attributes.update(target_node.attributes)
                # Rewire all edges
                for edge in updated_graph.edges:
                    if edge.source_id == target_id:
                        edge.source_id = canonical_id
                    if edge.target_id == target_id:
                        edge.target_id = canonical_id
                # Remove duplicate edges
                seen_edges = set()
                deduped_edges = []
                for e in updated_graph.edges:
                    key = (e.source_id, e.target_id, e.relation_type)
                    if key not in seen_edges and e.source_id != e.target_id:
                        seen_edges.add(key)
                        deduped_edges.append(e)
                updated_graph.edges = deduped_edges
                del updated_graph.nodes[target_id]

        elif delta_action == "PRUNE_NODE":
            if target_id in updated_graph.nodes:
                del updated_graph.nodes[target_id]
                updated_graph.edges = [
                    e for e in updated_graph.edges if e.source_id != target_id and e.target_id != target_id
                ]

        latency_ms = (time.perf_counter() - t0) * 1000.0
        return updated_graph, latency_ms
