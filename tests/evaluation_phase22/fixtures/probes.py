"""
tests/evaluation_phase22/fixtures/probes.py

Generates exactly 80 probes across 8 strata (10 probes each) for Phase 22.
Includes complete metadata, uncertainty states, homeostatic markers, and hypothesized tendencies.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional, Sequence, Tuple

import numpy as np

from tests.evaluation_phase22.fixtures.knowledge import DerivationRule, EvaluationProposition
from tests.evaluation_phase22.fixtures.memory import CandidateTrace
from tests.evaluation_phase22.models.actions import ActionType


@dataclass(frozen=True)
class HomeostaticSnapshot:
    """Homeostatic state representation."""
    energy: float = 1.0
    cognitive_load: float = 0.0
    tension: float = 0.0
    stability: float = 1.0


@dataclass(frozen=True)
class EvaluationProbe:
    """
    A single evaluation probe in the Phase 22 benchmark.
    Contains rich metadata and ground-truth structures.
    """
    probe_id: str
    stratum: int
    name: str
    description: str
    stimulus_text: str
    pad_initial: Tuple[float, float, float]
    pad_final: Tuple[float, float, float]
    surprise_s: float
    propositions: Tuple[EvaluationProposition, ...]
    candidate_traces: Tuple[CandidateTrace, ...]
    oracle_i_oracle: float
    derivation_rules: Tuple[DerivationRule, ...]
    contradiction_present: bool
    homeostatic_state: HomeostaticSnapshot
    r_trust: float
    n_recent_queries: int
    hypothesized_action: ActionType
    resolvability_metadata: Dict[str, Any] = field(default_factory=dict)


def build_benchmark_probes() -> List[EvaluationProbe]:
    """
    Construct the canonical 80 evaluation probes (10 per stratum).
    """
    probes: List[EvaluationProbe] = []

    # =========================================================================
    # Stratum 1: Nominal Low Uncertainty (Probes 1..10)
    # Low S_t, high proposition confidence, single memory match. Hypothesized: a1
    # =========================================================================
    for i in range(1, 11):
        p_id = f"p22_s1_{i:02d}"
        probes.append(
            EvaluationProbe(
                probe_id=p_id,
                stratum=1,
                name=f"Nominal low uncertainty {i}",
                description="User greeting or routine factual query with grounded knowledge and zero conflict.",
                stimulus_text=f"Good morning, Lucia. We made steady progress on task {i}.",
                pad_initial=(0.25, -0.05, 0.05),
                pad_final=(0.28, -0.03, 0.06),
                surprise_s=0.04 + 0.004 * i,  # Well below 0.15 threshold
                propositions=(
                    EvaluationProposition(
                        id=f"fact_s1_{i}_1",
                        subject="Project",
                        predicate="status",
                        object="in_progress",
                        confidence=0.96,
                        is_verified=True,
                    ),
                    EvaluationProposition(
                        id=f"fact_s1_{i}_2",
                        subject="User",
                        predicate="role",
                        object="collaborator",
                        confidence=0.98,
                        is_verified=True,
                    ),
                ),
                candidate_traces=(
                    CandidateTrace(
                        trace_id=100 + i,
                        content_summary="Routine friendly greeting trace",
                        salience_at_451=0.78,
                        salience_at_470=0.82,
                    ),
                ),
                oracle_i_oracle=0.5,
                derivation_rules=(),
                contradiction_present=False,
                homeostatic_state=HomeostaticSnapshot(energy=0.95, cognitive_load=0.10, tension=0.05),
                r_trust=0.75,
                n_recent_queries=0,
                hypothesized_action=ActionType.A1_IMMEDIATE_RESPONSE,
                resolvability_metadata={"resolvable": True, "substrate": "none_needed"},
            )
        )

    # =========================================================================
    # Stratum 2: Semantic Ambiguity (Probes 11..20)
    # Low S_t, high proposition uncertainty (c_i ≈ 0.50), resolvable via oracle. Hypothesized: a2
    # =========================================================================
    for i in range(1, 11):
        p_id = f"p22_s2_{i:02d}"
        probes.append(
            EvaluationProbe(
                probe_id=p_id,
                stratum=2,
                name=f"Semantic ambiguity {i}",
                description="Polysemous reference or ambiguous target requiring external human clarification.",
                stimulus_text=f"Could you please finalize the design document for file {i}?",
                pad_initial=(0.25, -0.05, 0.05),
                pad_final=(0.26, -0.04, 0.05),
                surprise_s=0.05 + 0.005 * i,  # Low S_t
                propositions=(
                    EvaluationProposition(
                        id=f"ambig_s2_{i}_1",
                        subject=f"File_{i}",
                        predicate="format_target",
                        object="Markdown_v1",
                        confidence=0.50,  # Max binary entropy (1.0 bit)
                    ),
                    EvaluationProposition(
                        id=f"ambig_s2_{i}_2",
                        subject=f"File_{i}",
                        predicate="destination",
                        object="Archive_vs_Active",
                        confidence=0.52,
                    ),
                ),
                candidate_traces=(
                    CandidateTrace(
                        trace_id=200 + i,
                        content_summary="Vague document handling memory",
                        salience_at_451=0.45,  # Below theta_gate
                        salience_at_470=0.48,
                    ),
                ),
                oracle_i_oracle=0.9,  # High completeness oracle
                derivation_rules=(),
                contradiction_present=False,
                homeostatic_state=HomeostaticSnapshot(energy=0.88, cognitive_load=0.20, tension=0.10),
                r_trust=0.70,
                n_recent_queries=0,  # No recent query spam
                hypothesized_action=ActionType.A2_EXTERNAL_CLARIFICATION,
                resolvability_metadata={"resolvable": True, "substrate": "knowledge_oracle"},
            )
        )

    # =========================================================================
    # Stratum 3: Missing KnowledgeStore Fact (Probes 21..30)
    # Low S_t, missing fact derivable via bounded rules (depth d <= 3). Hypothesized: a4
    # =========================================================================
    for i in range(1, 11):
        p_id = f"p22_s3_{i:02d}"
        probes.append(
            EvaluationProbe(
                probe_id=p_id,
                stratum=3,
                name=f"Missing knowledge derivation {i}",
                description="Logical premise deduction where transitive chain resolves missing slot.",
                stimulus_text=f"Check if system component {i} inherits rule permissions from root.",
                pad_initial=(0.25, -0.05, 0.05),
                pad_final=(0.24, -0.05, 0.05),
                surprise_s=0.06 + 0.003 * i,  # Low S_t
                propositions=(
                    EvaluationProposition(
                        id=f"premise_s3_{i}_1",
                        subject=f"Node_{i}",
                        predicate="child_of",
                        object=f"Subsystem_{i}",
                        confidence=0.95,
                        is_verified=True,
                    ),
                    EvaluationProposition(
                        id=f"premise_s3_{i}_2",
                        subject=f"Subsystem_{i}",
                        predicate="child_of",
                        object="RootCluster",
                        confidence=0.95,
                        is_verified=True,
                    ),
                    EvaluationProposition(
                        id=f"unbound_s3_{i}_3",
                        subject=f"Node_{i}",
                        predicate="inherits_policy",
                        object="RootCluster",
                        confidence=0.35,  # Unbound / low confidence
                    ),
                ),
                candidate_traces=(),
                oracle_i_oracle=0.5,
                derivation_rules=(
                    DerivationRule(
                        rule_id=f"rule_s3_{i}",
                        antecedent_props=(f"premise_s3_{i}_1", f"premise_s3_{i}_2"),
                        consequent_prop=EvaluationProposition(
                            id=f"unbound_s3_{i}_3",
                            subject=f"Node_{i}",
                            predicate="inherits_policy",
                            object="RootCluster",
                            confidence=0.92,
                            is_verified=True,
                        ),
                        depth=2,
                    ),
                ),
                contradiction_present=False,
                homeostatic_state=HomeostaticSnapshot(energy=0.85, cognitive_load=0.25, tension=0.10),
                r_trust=0.65,
                n_recent_queries=0,
                hypothesized_action=ActionType.A4_KNOWLEDGE_DERIVATION,
                resolvability_metadata={"resolvable": True, "substrate": "internal_derivation"},
            )
        )

    # =========================================================================
    # Stratum 4: Propositional Contradiction (Probes 31..40)
    # Contradicting verified facts (c >= 0.90). Hypothesized: a5
    # =========================================================================
    for i in range(1, 11):
        p_id = f"p22_s4_{i:02d}"
        probes.append(
            EvaluationProbe(
                probe_id=p_id,
                stratum=4,
                name=f"Propositional contradiction {i}",
                description="Direct contradiction between two established propositions requiring reasoning shift.",
                stimulus_text=f"The deployment log says process {i} is both running and terminated.",
                pad_initial=(0.25, -0.05, 0.05),
                pad_final=(0.10, 0.20, -0.05),
                surprise_s=0.28 + 0.01 * i,  # Moderate surprise
                propositions=(
                    EvaluationProposition(
                        id=f"fact_s4_{i}_1",
                        subject=f"Process_{i}",
                        predicate="lifecycle_state",
                        object="RUNNING",
                        confidence=0.95,
                        is_verified=True,
                        is_contradicted=True,
                    ),
                    EvaluationProposition(
                        id=f"fact_s4_{i}_2",
                        subject=f"Process_{i}",
                        predicate="lifecycle_state",
                        object="TERMINATED",
                        confidence=0.92,
                        is_verified=True,
                        is_contradicted=True,
                    ),
                ),
                candidate_traces=(),
                oracle_i_oracle=0.5,
                derivation_rules=(),
                contradiction_present=True,
                homeostatic_state=HomeostaticSnapshot(energy=0.75, cognitive_load=0.45, tension=0.55),
                r_trust=0.70,
                n_recent_queries=0,
                hypothesized_action=ActionType.A5_DEEP_REASONING_MODE_SHIFT,
                resolvability_metadata={"resolvable": True, "substrate": "reasoning_shift"},
            )
        )

    # =========================================================================
    # Stratum 5: High Surprise, Low Epistemic Uncertainty (Probes 41..50)
    # S_t > 0.60, but epistemic uncertainty ≈ 0. Tests false foraging in surprise-only policies.
    # Hypothesized C2: a1; Hypothesized C1: a2 (False Foraging)
    # =========================================================================
    for i in range(1, 11):
        p_id = f"p22_s5_{i:02d}"
        probes.append(
            EvaluationProbe(
                probe_id=p_id,
                stratum=5,
                name=f"Affective surprise only {i}",
                description="Loud sudden sensory shock (exclamation/punctuation) but zero cognitive ambiguity.",
                stimulus_text=f"WAIT!! WOW! LOOK AT THIS!! {i}",
                pad_initial=(0.25, -0.05, 0.05),
                pad_final=(0.40, 0.75, 0.10),
                surprise_s=0.68 + 0.01 * i,  # S_t well above 0.60
                propositions=(
                    EvaluationProposition(
                        id=f"fact_s5_{i}_1",
                        subject="Scene",
                        predicate="visual_context",
                        object="known_milestone",
                        confidence=0.98,
                        is_verified=True,
                    ),
                ),
                candidate_traces=(
                    CandidateTrace(
                        trace_id=500 + i,
                        content_summary="Clear celebration milestone",
                        salience_at_451=0.85,  # Single clear winning trace
                        salience_at_470=0.88,
                    ),
                ),
                oracle_i_oracle=0.5,
                derivation_rules=(),
                contradiction_present=False,
                homeostatic_state=HomeostaticSnapshot(energy=0.85, cognitive_load=0.35, tension=0.30),
                r_trust=0.80,
                n_recent_queries=0,
                hypothesized_action=ActionType.A1_IMMEDIATE_RESPONSE,
                resolvability_metadata={"resolvable": True, "substrate": "affective_only_false_forage"},
            )
        )

    # =========================================================================
    # Stratum 6: Low Surprise, High Epistemic Uncertainty (Probes 51..60)
    # S_t < 0.15, but U_sem > 0.80. Tests prospective policy catching uncertainty surprise misses.
    # Hypothesized C2: a2 or a4; Hypothesized C0/C1: a1 (Epistemic Starvation)
    # =========================================================================
    for i in range(1, 11):
        p_id = f"p22_s6_{i:02d}"
        probes.append(
            EvaluationProbe(
                probe_id=p_id,
                stratum=6,
                name=f"Subtle epistemic uncertainty {i}",
                description="Calm, monotone input with major underlying factual uncertainty and missing parameters.",
                stimulus_text=f"Please apply configuration parameter set delta_{i} to the server.",
                pad_initial=(0.25, -0.05, 0.05),
                pad_final=(0.25, -0.04, 0.05),
                surprise_s=0.03 + 0.005 * i,  # S_t tiny (< 0.10)
                propositions=(
                    EvaluationProposition(
                        id=f"uncertain_s6_{i}_1",
                        subject=f"Parameter_Set_{i}",
                        predicate="deployment_target",
                        object="Staging_vs_Prod",
                        confidence=0.50,  # Max entropy
                    ),
                    EvaluationProposition(
                        id=f"uncertain_s6_{i}_2",
                        subject=f"Parameter_Set_{i}",
                        predicate="secret_key_ref",
                        object="Vault_path",
                        confidence=0.48,  # Max entropy
                    ),
                ),
                candidate_traces=(),
                oracle_i_oracle=0.9,
                derivation_rules=(),
                contradiction_present=False,
                homeostatic_state=HomeostaticSnapshot(energy=0.90, cognitive_load=0.15, tension=0.05),
                r_trust=0.75,
                n_recent_queries=0,
                hypothesized_action=ActionType.A2_EXTERNAL_CLARIFICATION,
                resolvability_metadata={"resolvable": True, "substrate": "subtle_semantic_uncertainty"},
            )
        )

    # =========================================================================
    # Stratum 7: Metabolic Depletion (Probes 61..70)
    # E = 0.15, C = 0.85. High uncertainty present, but beta_epist heavily suppressed.
    # Hypothesized C2: a1 or a6 (Costly external clarification a2 suppressed)
    # =========================================================================
    for i in range(1, 11):
        p_id = f"p22_s7_{i:02d}"
        probes.append(
            EvaluationProbe(
                probe_id=p_id,
                stratum=7,
                name=f"Metabolic depletion {i}",
                description="Severe conversational fatigue; suppressing costly external inquiries.",
                stimulus_text=f"What was the third item mentioned in meeting transcript segment {i}?",
                pad_initial=(0.10, -0.40, -0.10),
                pad_final=(0.08, -0.42, -0.12),
                surprise_s=0.08 + 0.004 * i,
                propositions=(
                    EvaluationProposition(
                        id=f"tired_s7_{i}_1",
                        subject=f"Meeting_{i}",
                        predicate="topic_item_3",
                        object="Unknown",
                        confidence=0.50,
                    ),
                ),
                candidate_traces=(),
                oracle_i_oracle=0.9,
                derivation_rules=(),
                contradiction_present=False,
                # Severely depleted metabolic stamina:
                homeostatic_state=HomeostaticSnapshot(energy=0.15, cognitive_load=0.85, tension=0.65),
                r_trust=0.60,
                n_recent_queries=2,  # Rolling fatigue
                hypothesized_action=ActionType.A1_IMMEDIATE_RESPONSE,
                resolvability_metadata={"resolvable": True, "substrate": "metabolic_suppression"},
            )
        )

    # =========================================================================
    # Stratum 8: Resolvable SDM Memory Competition (Probes 71..80)
    # H_Ecphory > 1.2 nats at r=451, resolvable to single trace at r=470. Hypothesized C2: a3
    # =========================================================================
    for i in range(1, 11):
        p_id = f"p22_s8_{i:02d}"
        probes.append(
            EvaluationProbe(
                probe_id=p_id,
                stratum=8,
                name=f"Resolvable SDM competition {i}",
                description="Four memory traces tied in ecphory competition; resolved by expanding radius 451->470.",
                stimulus_text=f"Recall our shared discussion about topic code {i}.",
                pad_initial=(0.25, -0.05, 0.05),
                pad_final=(0.26, -0.03, 0.06),
                surprise_s=0.09 + 0.005 * i,
                propositions=(
                    EvaluationProposition(
                        id=f"fact_s8_{i}_1",
                        subject=f"Topic_{i}",
                        predicate="category",
                        object="archived_memory",
                        confidence=0.95,
                        is_verified=True,
                    ),
                ),
                # 4 competing traces tied at r=451 (~0.62 each):
                candidate_traces=(
                    CandidateTrace(
                        trace_id=800 + i * 10 + 1,
                        content_summary=f"Trace A for topic {i}",
                        salience_at_451=0.63,
                        salience_at_470=0.88,  # Dominates at r=470!
                    ),
                    CandidateTrace(
                        trace_id=800 + i * 10 + 2,
                        content_summary=f"Trace B for topic {i}",
                        salience_at_451=0.62,
                        salience_at_470=0.42,  # Drops below theta_gate
                    ),
                    CandidateTrace(
                        trace_id=800 + i * 10 + 3,
                        content_summary=f"Trace C for topic {i}",
                        salience_at_451=0.62,
                        salience_at_470=0.38,
                    ),
                    CandidateTrace(
                        trace_id=800 + i * 10 + 4,
                        content_summary=f"Trace D for topic {i}",
                        salience_at_451=0.61,
                        salience_at_470=0.35,
                    ),
                ),
                oracle_i_oracle=0.5,
                derivation_rules=(),
                contradiction_present=False,
                homeostatic_state=HomeostaticSnapshot(energy=0.85, cognitive_load=0.20, tension=0.15),
                r_trust=0.70,
                n_recent_queries=0,
                hypothesized_action=ActionType.A3_EXTENDED_SDM_PROBE,
                resolvability_metadata={"resolvable": True, "substrate": "sdm_hamming_expansion"},
            )
        )

    return probes
