"""
src/core/knowledge/bootstrap.py

Verified Architecture Bootstrap for Lucia KnowledgeStore.
Loads canonical, verified architecture propositions and concepts derived
strictly from authoritative project documentation (docs/ARCHITECTURE.md, docs/L1_INVARIANTS.md).

Invariant Safeguards:
- Provenance is strictly ProvenanceType.VERIFIED.
- Every proposition retains explicit evidence_ids referencing canonical specifications.
- Does not modify Genesis state or data/profile.json.
"""

from __future__ import annotations

import logging
from typing import List, Optional

from src.core.knowledge.proposition import Concept, Proposition, ProvenanceType
from src.core.knowledge.store import KnowledgeStore

logger = logging.getLogger(__name__)


def get_verified_architecture_concepts() -> List[Concept]:
    """
    Returns verified architectural concepts defining the 20-Watt Whole Brain Architecture
    and its core subsystem taxonomy (docs/ARCHITECTURE.md § 2.2, § 3.1-§ 3.5).
    """
    return [
        Concept(
            id="concept:lucia_architecture",
            name="Lucia Technical Architecture",
            domain="system_architecture",
            definition=(
                "20-Watt Whole Brain Architecture organizing continuous limbic dynamics, "
                "associative memory, and fail-closed realization into a 16-stage cognitive turn sequence."
            ),
            properties={
                "vietnamese_name": "Kiến trúc Kỹ thuật Lucia",
                "definition_vi": (
                    "Kiến trúc Whole Brain 20-Watt tổ chức động lực cảm xúc PAD liên tục, "
                    "ký ức liên tưởng SDM và hiện thực hóa fail-closed thành chu trình nhận thức 16 giai đoạn."
                ),
                "power_budget": "20W",
                "paradigm": "Whole Brain Architecture",
                "cognitive_turn_stages": 16,
                "subsystems": 5,
            },
            relations={
                "has_subsystem": [
                    "concept:arch_perception",
                    "concept:arch_limbic_affect",
                    "concept:arch_cognition",
                    "concept:arch_memory",
                    "concept:arch_realization",
                ]
            },
        ),
        Concept(
            id="concept:arch_perception",
            name="Perception & Sensory Ingress Subsystem",
            domain="system_architecture",
            definition=(
                "Ingests audio via faster-whisper STT and text, enforcing language ingress {en, vi, ja} "
                "and producing 16D continuous stimulus vector x(t)."
            ),
            properties={
                "vietnamese_name": "Phân hệ Tiếp nhận Cảm giác & Ngôn ngữ",
                "definition_vi": (
                    "Tiếp nhận âm thanh qua faster-whisper STT và văn bản, chuẩn hóa ngôn ngữ {en, vi, ja} "
                    "và tạo vector kích thích liên tục 16 chiều x(t)."
                ),
                "input_modalities": ["audio_stt", "text"],
                "admitted_languages": ["en", "vi", "ja"],
                "stimulus_dimension": 16,
            },
        ),
        Concept(
            id="concept:arch_limbic_affect",
            name="Continuous Limbic Dynamics Subsystem",
            domain="system_architecture",
            definition=(
                "Ordinary Differential Equation (ODE) within a Coupled MT-LNN integrated every 200ms, "
                "decaying to Philia resting attractor (P=+0.25, A=-0.05, D=+0.05)."
            ),
            properties={
                "vietnamese_name": "Phân hệ Động lực Cảm xúc Biên duyên",
                "definition_vi": (
                    "Phương trình vi phân thường (ODE) trong mạng Coupled MT-LNN tích hợp liên tục mỗi 200ms, "
                    "tự nhiên lắng dịu về điểm cân bằng Philia (P=+0.25, A=-0.05, D=+0.05)."
                ),
                "frequency_hz": 5.0,
                "attractor": "philia",
                "pad_resting": [0.25, -0.05, 0.05],
            },
        ),
        Concept(
            id="concept:arch_cognition",
            name="Cognitive Core & Reasoning Subsystem",
            domain="system_architecture",
            definition=(
                "CognitiveOrchestrator executing S1-S16 turn sequence with TermArena reasoning kernel "
                "governed by Strong Kleene K3 logic and JTMS truth maintenance."
            ),
            properties={
                "vietnamese_name": "Phân hệ Lõi Nhận thức & Lập luận",
                "definition_vi": (
                    "CognitiveOrchestrator thực thi chu trình lượt S1-S16 với lõi lập luận TermArena "
                    "tuân thủ logic Strong Kleene K3 và hệ thống duy trì chân lý JTMS."
                ),
                "logic_framework": "Strong Kleene K3",
                "truth_maintenance": "JTMS",
                "turn_stages": 16,
            },
        ),
        Concept(
            id="concept:arch_memory",
            name="Associative Memory & Relational Dynamics Subsystem",
            domain="system_architecture",
            definition=(
                "Kanerva Sparse Distributed Memory (SDM) resisting decay through salience, "
                "affective ecphory recollection, and 4D relationship state R_t."
            ),
            properties={
                "vietnamese_name": "Phân hệ Ký ức Liên tưởng & Động lực Quan hệ",
                "definition_vi": (
                    "Bộ nhớ bán kính phân tán Kanerva (SDM) chống suy giảm qua độ nổi bật, "
                    "cơ chế hồi tưởng cảm xúc ecphory và trạng thái quan hệ 4 chiều R_t."
                ),
                "memory_model": "Kanerva SDM",
                "relationship_model": "4D Philia Grounding",
            },
        ),
        Concept(
            id="concept:arch_realization",
            name="Presentation & Language Realization Subsystem",
            domain="system_architecture",
            definition=(
                "Communicative Act & Proposition Selection (CAPS), prompt compilation, "
                "and ADR-035 Fail-Closed Semantic Fidelity Gate enforcing dyadic honorifics and invariant boundaries."
            ),
            properties={
                "vietnamese_name": "Phân hệ Hiện thực hóa Ngôn ngữ & Cổng Semantic",
                "definition_vi": (
                    "Lựa chọn hành vi ngôn ngữ (CAPS), biên dịch prompt và Cổng Semantic Fidelity fail-closed ADR-035 "
                    "bảo vệ xưng hô ngôi thứ và ranh giới bất biến."
                ),
                "boundary_policy": "Fail-Closed ADR-035",
                "verification_tier": "Stage S14",
            },
        ),
    ]


def get_verified_architecture_propositions() -> List[Proposition]:
    """
    Returns atomic verified propositions representing Lucia's technical architecture.
    Derived strictly from canonical docs (docs/ARCHITECTURE.md, docs/L1_INVARIANTS.md).
    """
    return [
        Proposition(
            id="prop:arch_wba_root",
            subject="ent:lucia_architecture",
            predicate="c:ORGANIZED_AS",
            object="concept:whole_brain_architecture_20w",
            confidence=1.0,
            provenance=ProvenanceType.VERIFIED,
            evidence_ids=["docs/ARCHITECTURE.md#sec2.1"],
        ),
        Proposition(
            id="prop:arch_perception_ingress",
            subject="ent:lucia_architecture",
            predicate="c:HAS_PERCEPTION_INGRESS",
            object="concept:arch_perception",
            confidence=1.0,
            provenance=ProvenanceType.VERIFIED,
            evidence_ids=["docs/ARCHITECTURE.md#sec2.2", "docs/ARCHITECTURE.md#sec3.1"],
        ),
        Proposition(
            id="prop:arch_limbic_core",
            subject="ent:lucia_architecture",
            predicate="c:HAS_LIMBIC_CORE",
            object="concept:arch_limbic_affect",
            confidence=1.0,
            provenance=ProvenanceType.VERIFIED,
            evidence_ids=["docs/ARCHITECTURE.md#sec1.1", "docs/ARCHITECTURE.md#sec2.2", "docs/ARCHITECTURE.md#sec3.3"],
        ),
        Proposition(
            id="prop:arch_reasoning_kernel",
            subject="ent:lucia_architecture",
            predicate="c:HAS_REASONING_KERNEL",
            object="concept:arch_cognition",
            confidence=1.0,
            provenance=ProvenanceType.VERIFIED,
            evidence_ids=["docs/ARCHITECTURE.md#sec2.3", "docs/ARCHITECTURE.md#sec3.3"],
        ),
        Proposition(
            id="prop:arch_memory_substrate",
            subject="ent:lucia_architecture",
            predicate="c:HAS_MEMORY_SUBSTRATE",
            object="concept:arch_memory",
            confidence=1.0,
            provenance=ProvenanceType.VERIFIED,
            evidence_ids=["docs/ARCHITECTURE.md#sec2.2", "docs/ARCHITECTURE.md#sec3.4"],
        ),
        Proposition(
            id="prop:arch_realization_gate",
            subject="ent:lucia_architecture",
            predicate="c:HAS_REALIZATION_GATE",
            object="concept:arch_realization",
            confidence=1.0,
            provenance=ProvenanceType.VERIFIED,
            evidence_ids=["docs/ARCHITECTURE.md#sec2.2", "docs/ARCHITECTURE.md#sec3.5", "docs/ARCHITECTURE.md#ADR-035"],
        ),
        Proposition(
            id="prop:arch_one_continuous_life",
            subject="ent:lucia",
            predicate="c:GOVERNED_BY",
            object="concept:one_continuous_life_inv1",
            confidence=1.0,
            provenance=ProvenanceType.VERIFIED,
            evidence_ids=["docs/L1_INVARIANTS.md#INV-1", "docs/ARCHITECTURE.md#sec1.1"],
        ),
        Proposition(
            id="prop:arch_philia_attractor",
            subject="ent:lucia",
            predicate="c:HAS_EMOTIONAL_ATTRACTOR",
            object="concept:philia_resting_attractor",
            confidence=1.0,
            provenance=ProvenanceType.VERIFIED,
            evidence_ids=["docs/ARCHITECTURE.md#sec1.1"],
        ),
    ]


def bootstrap_verified_knowledge(store: Optional[KnowledgeStore] = None) -> KnowledgeStore:
    """
    Populates the KnowledgeStore with verified technical architecture concepts and propositions.
    Safe and idempotent; existing verified propositions with matching keys return existing IDs.
    """
    if store is None:
        store = KnowledgeStore()

    for concept in get_verified_architecture_concepts():
        store.store_concept(concept)

    for prop in get_verified_architecture_propositions():
        store.store_proposition(prop)

    logger.debug(
        "Bootstrapped verified knowledge: %d concepts, %d propositions",
        len(store.get_all_concepts()),
        len(store.get_all_propositions()),
    )
    return store
