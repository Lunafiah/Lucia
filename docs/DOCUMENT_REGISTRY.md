# Lucia — Master Document Registry & Classification Catalog

> **Canonical Repository-Wide Catalog of Authoritative Documents, Specifications, Evidence, and Context Projections**  
> **Status:** `[CANONICAL REPOSITORY REGISTRY]`  
> **Classification Schema:** Document ID | Title | Path | Type | Phase | Stage | Status | Authority | Canonical Owner | Provenance Links

---

## 1. Document Classification Schema & Field Definitions

Every documented artifact in the Lucia repository is registered and classified according to the following 15-attribute metadata standard:

1. **Document ID**: Unique stable identifier (`DOC-<Category>-<Number>`).
2. **Title**: Formal title of the document.
3. **File Path**: Relative repository path from workspace root.
4. **Knowledge Class**: One of the 7 knowledge classes (Canonical Current, Research History, Evaluation Evidence, Implementation History, Architectural Decision, Historical/Superseded, Agent Context).
5. **Phase**: Development phase (P01–P27, Genesis, or REPO-WIDE).
6. **Sub-Phase**: Sub-phase or research branch identifier (e.g. `P23-H`, `22-SC`, `N/A`).
7. **Lifecycle Stage**: Specific stage (Specification, Research, Contract, Implementation, Audit, Fix, Freeze, Operational).
8. **Status**: Controlled status (`CANONICAL`, `ACTIVE`, `FROZEN`, `IMPLEMENTED`, `VERIFIED`, `SUPERSEDED`, `REJECTED`, `RESEARCH`).
9. **Authority Level**: Authority tier (`CANONICAL`, `DECISION`, `RESEARCH`, `EVIDENCE`, `IMPLEMENTATION`, `CONTEXT`, `HISTORICAL`).
10. **Canonical Owner**: The single document that has primary ownership of facts in this artifact.
11. **Parent Document**: The immediate hierarchical parent in the documentation tree.
12. **Evidence Links**: Relative paths or identifiers of supporting benchmark data.
13. **Decision Links**: Relative paths or IDs of governing ADRs (e.g. `ADR-028`, `ARCH-031`).
14. **Implementation Links**: Production source files or commit hashes.
15. **Superseded By / Referenced By**: Cross-references to newer documents or parent indexes.

---

## 2. Core Governance, Living Canon & Navigation (Tier L0–L4)

| Doc ID | Title | File Path | Class | Phase | Stage | Status | Authority | Canonical Owner | Governing Links |
|---|---|---|---|---|---|---|---|---|---|
| **DOC-CAN-001** | Public Front Door | [`README.md`](file:///c:/Users/Lunafiah/Desktop/My_project/Lucia/README.md) | Canonical Current | REPO-WIDE | Operational | `CANONICAL` | `CANONICAL` | Self | Points to `docs/00_PROJECT_OVERVIEW.md` |
| **DOC-CAN-002** | Master Invariant Ledger | [`docs/L1_INVARIANTS.md`](file:///c:/Users/Lunafiah/Desktop/My_project/Lucia/docs/L1_INVARIANTS.md) | Canonical Current | REPO-WIDE | Operational | `CANONICAL` | `CANONICAL` | Self | Codifies 8 core invariants & lock rules |
| **DOC-CAN-003** | Master Agent Operating Instructions | [`AGENTS.md`](file:///c:/Users/Lunafiah/Desktop/My_project/Lucia/AGENTS.md) | Canonical Current | REPO-WIDE | Operational | `CANONICAL` | `CANONICAL` | Self | Master instructions, decision sequences |
| **DOC-CAN-004** | Canonical Project Truth & Roadmap | [`docs/00_PROJECT_OVERVIEW.md`](file:///c:/Users/Lunafiah/Desktop/My_project/Lucia/docs/00_PROJECT_OVERVIEW.md) | Canonical Current | REPO-WIDE | Operational | `CANONICAL` | `CANONICAL` | Self | Subsystem health matrix, milestone status |
| **DOC-CAN-005** | Technical Architecture & ADR Ledger | [`docs/ARCHITECTURE.md`](file:///c:/Users/Lunafiah/Desktop/My_project/Lucia/docs/ARCHITECTURE.md) | Canonical Current | REPO-WIDE | Operational | `CANONICAL` | `CANONICAL` | Self | ADR-001 to ADR-032, ARCH-001 to ARCH-032 |
| **DOC-CAN-006** | Documentation Architecture | [`docs/DOCUMENTATION_ARCHITECTURE.md`](file:///c:/Users/Lunafiah/Desktop/My_project/Lucia/docs/DOCUMENTATION_ARCHITECTURE.md) | Canonical Current | REPO-WIDE | Operational | `CANONICAL` | `CANONICAL` | Self | Information architecture & taxonomy |
| **DOC-CAN-007** | Master Phase Registry | [`docs/PHASE_REGISTRY.md`](file:///c:/Users/Lunafiah/Desktop/My_project/Lucia/docs/PHASE_REGISTRY.md) | Canonical Current | REPO-WIDE | Operational | `CANONICAL` | `CANONICAL` | Self | Exhaustive milestone progression ledger |
| **DOC-CAN-008** | Master Document Registry | [`docs/DOCUMENT_REGISTRY.md`](file:///c:/Users/Lunafiah/Desktop/My_project/Lucia/docs/DOCUMENT_REGISTRY.md) | Canonical Current | REPO-WIDE | Operational | `CANONICAL` | `CANONICAL` | Self | This document: full catalog & metadata |
| **DOC-CAN-009** | Repository Source & Provenance Map | [`docs/SOURCE_MAP.md`](file:///c:/Users/Lunafiah/Desktop/My_project/Lucia/docs/SOURCE_MAP.md) | Canonical Current | REPO-WIDE | Operational | `CANONICAL` | `CANONICAL` | Self | Claim-to-measurement provenance ledger |
| **DOC-CAN-010** | Agent Context Architecture | [`docs/CONTEXT_ARCHITECTURE.md`](file:///c:/Users/Lunafiah/Desktop/My_project/Lucia/docs/CONTEXT_ARCHITECTURE.md) | Canonical Current | REPO-WIDE | Operational | `CANONICAL` | `CANONICAL` | Self | Context projection model for Ciah/Gemini |
| **DOC-CAN-011** | Context Architecture Retrieval Map | [`docs/CONTEXT_INDEX.md`](file:///c:/Users/Lunafiah/Desktop/My_project/Lucia/docs/CONTEXT_INDEX.md) | Agent Context | REPO-WIDE | Operational | `CANONICAL` | `CONTEXT` | `docs/CONTEXT_ARCHITECTURE.md` | L0–L6 minimal sufficient routing |
| **DOC-CAN-012** | Documentation Index & Navigation | [`docs/DOCUMENTATION_INDEX.md`](file:///c:/Users/Lunafiah/Desktop/My_project/Lucia/docs/DOCUMENTATION_INDEX.md) | Canonical Current | REPO-WIDE | Operational | `CANONICAL` | `CANONICAL` | Self | Reading pathways by persona |
| **DOC-CAN-013** | Documentation Conflict Ledger | [`docs/DOCUMENTATION_CONFLICTS.md`](file:///c:/Users/Lunafiah/Desktop/My_project/Lucia/docs/DOCUMENTATION_CONFLICTS.md) | Canonical Current | REPO-WIDE | Operational | `CANONICAL` | `CANONICAL` | Self | Catalog of contradictions & resolutions |
| **DOC-CAN-014** | Documentation Migration Plan | [`docs/DOCUMENTATION_MIGRATION_PLAN.md`](file:///c:/Users/Lunafiah/Desktop/My_project/Lucia/docs/DOCUMENTATION_MIGRATION_PLAN.md) | Canonical Current | REPO-WIDE | Operational | `CANONICAL` | `CANONICAL` | Self | Safe, phased migration strategy |
| **DOC-CAN-015** | User Operation & Setup Manual | [`docs/USER_MANUAL.md`](file:///c:/Users/Lunafiah/Desktop/My_project/Lucia/docs/USER_MANUAL.md) | Canonical Current | REPO-WIDE | Operational | `CANONICAL` | `CANONICAL` | Self | UI controls, RVC voice, mascot guide |
| **DOC-CAN-016** | Foundational Affective Whitepaper | [`docs/Triết lý thiết kế AI cảm xúc.md`](file:///c:/Users/Lunafiah/Desktop/My_project/Lucia/docs/Triết lý thiết kế AI cảm xúc.md) | Research History | P01 | Conceptual Seed | `HISTORICAL` | `HISTORICAL` | Self | Vietnamese whitepaper founding 20W WBA |

---

## 3. Historical Phase Specifications & Realization Designs (Phases 1–21)

| Doc ID | Title | File Path | Class | Phase | Stage | Status | Authority | Canonical Owner |
|---|---|---|---|---|---|---|---|---|
| **DOC-SPC-001** | Phase 1 Requirements | `docs/PhaseDocs/lucia-phase1-core/Phase_1_requirements.md` | Research History | P01 | Requirement | `HISTORICAL` | `HISTORICAL` | `docs/ARCHITECTURE.md` |
| **DOC-SPC-002** | Phase 1 Design Document | `docs/PhaseDocs/lucia-phase1-core/Phase_1_design.md` | Implementation History | P01 | Design | `HISTORICAL` | `HISTORICAL` | `docs/ARCHITECTURE.md` |
| **DOC-SPC-003** | Phase 1 Implementation Tasks | `docs/PhaseDocs/lucia-phase1-core/Phase_1_tasks.md` | Implementation History | P01 | Task Plan | `HISTORICAL` | `HISTORICAL` | `docs/ARCHITECTURE.md` |
| **DOC-SPC-004** | Phase 2 Requirements | `docs/PhaseDocs/lucia-phase2-memory/Phase_2_requirements.md` | Research History | P02 | Requirement | `HISTORICAL` | `HISTORICAL` | `docs/ARCHITECTURE.md` |
| **DOC-SPC-005** | Phase 2 Design Document | `docs/PhaseDocs/lucia-phase2-memory/Phase_2_design.md` | Implementation History | P02 | Design | `HISTORICAL` | `HISTORICAL` | `docs/ARCHITECTURE.md` |
| **DOC-SPC-006** | Phase 2 Implementation Tasks | `docs/PhaseDocs/lucia-phase2-memory/Phase_2_tasks.md` | Implementation History | P02 | Task Plan | `HISTORICAL` | `HISTORICAL` | `docs/ARCHITECTURE.md` |
| **DOC-SPC-007** | Phase 3 Requirements | `docs/PhaseDocs/lucia-phase3-ui/Phase_3_requirements.md` | Research History | P03 | Requirement | `SUPERSEDED` | `HISTORICAL` | `docs/PhaseDocs/lucia-phase7-UI_refractoring/` |
| **DOC-SPC-008** | Phase 3 Design Document | `docs/PhaseDocs/lucia-phase3-ui/Phase_3_design.md` | Implementation History | P03 | Design | `SUPERSEDED` | `HISTORICAL` | `docs/PhaseDocs/lucia-phase7-UI_refractoring/` |
| **DOC-SPC-009** | Phase 3 Implementation Tasks | `docs/PhaseDocs/lucia-phase3-ui/Phase_3_tasks.md` | Implementation History | P03 | Task Plan | `SUPERSEDED` | `HISTORICAL` | `docs/PhaseDocs/lucia-phase7-UI_refractoring/` |
| **DOC-SPC-010** | Phase 4 Requirements | `docs/PhaseDocs/lucia-phase4-inference/Phase_4_requirements.md` | Research History | P04 | Requirement | `HISTORICAL` | `HISTORICAL` | `docs/ARCHITECTURE.md` |
| **DOC-SPC-011** | Phase 4 Design Document | `docs/PhaseDocs/lucia-phase4-inference/Phase_4_design.md` | Implementation History | P04 | Design | `HISTORICAL` | `HISTORICAL` | `docs/ARCHITECTURE.md` |
| **DOC-SPC-012** | Phase 4 Implementation Tasks | `docs/PhaseDocs/lucia-phase4-inference/Phase_4_tasks.md` | Implementation History | P04 | Task Plan | `HISTORICAL` | `HISTORICAL` | `docs/ARCHITECTURE.md` |
| **DOC-SPC-013** | Phase 5 Requirements | `docs/PhaseDocs/lucia-phase5-presence/Phase_5_requirements.md` | Research History | P05 | Requirement | `HISTORICAL` | `HISTORICAL` | `docs/ARCHITECTURE.md` |
| **DOC-SPC-014** | Phase 5 Design Document | `docs/PhaseDocs/lucia-phase5-presence/Phase_5_design.md` | Implementation History | P05 | Design | `HISTORICAL` | `HISTORICAL` | `docs/ARCHITECTURE.md` |
| **DOC-SPC-015** | Phase 5 Implementation Tasks | `docs/PhaseDocs/lucia-phase5-presence/Phase_5_tasks.md` | Implementation History | P05 | Task Plan | `HISTORICAL` | `HISTORICAL` | `docs/ARCHITECTURE.md` |
| **DOC-SPC-016** | Phase 6 Requirements | `docs/PhaseDocs/lucia-phase6-refinement/Phase_6_requirements.md` | Research History | P06 | Requirement | `HISTORICAL` | `HISTORICAL` | `docs/ARCHITECTURE.md` |
| **DOC-SPC-017** | Phase 6 Design Document | `docs/PhaseDocs/lucia-phase6-refinement/Phase_6_design.md` | Implementation History | P06 | Design | `HISTORICAL` | `HISTORICAL` | `docs/ARCHITECTURE.md` |
| **DOC-SPC-018** | Phase 6 Implementation Tasks | `docs/PhaseDocs/lucia-phase6-refinement/Phase_6_tasks.md` | Implementation History | P06 | Task Plan | `HISTORICAL` | `HISTORICAL` | `docs/ARCHITECTURE.md` |
| **DOC-SPC-019** | Phase 7 Product Brief | `docs/PhaseDocs/lucia-phase7-UI_refractoring/Phase_7_new_UI_requirement.md` | Canonical Current | P07 | Product Brief | `CANONICAL` | `CANONICAL` | Self |
| **DOC-SPC-020** | Phase 7 UI Specification | `docs/PhaseDocs/lucia-phase7-UI_refractoring/PHASE_7_UI_REFACTORING_SPEC.md` | Canonical Current | P07 | UI Architecture | `CANONICAL` | `CANONICAL` | Self |
| **DOC-SPC-021** | Phase 8 Specification | `docs/PhaseDocs/lucia-phase8-ISOLATION/PHASE_8.md` | Canonical Current | P08 | Architecture | `CANONICAL` | `CANONICAL` | Self |
| **DOC-SPC-022** | Phase 8 Architecture Review | `docs/PhaseDocs/lucia-phase8-ISOLATION/PHASE_8_ARCHITECTURE_REVIEW.md` | Implementation History | P08 | Audit | `CANONICAL` | `CANONICAL` | Self |
| **DOC-SPC-023** | Phase 8 Report | `docs/PhaseDocs/lucia-phase8-ISOLATION/PHASE_8_REPORT.md` | Implementation History | P08 | Report | `HISTORICAL` | `HISTORICAL` | `PHASE_8_ARCHITECTURE_REVIEW.md` |
| **DOC-SPC-024** | Phase 8 Review Duplicate | `docs/PhaseDocs/lucia-phase8-ISOLATION/PHASE_8_review.md` | Implementation History | P08 | Review | `SUPERSEDED` | `HISTORICAL` | `PHASE_8_ARCHITECTURE_REVIEW.md` |
| **DOC-SPC-025** | Phase 9 Specification (v2.0) | `docs/PhaseDocs/lucia-phase9-Cognition_Unifying/PHASE_9.md` | Canonical Current | P09 | Architecture | `CANONICAL` | `CANONICAL` | Self |
| **DOC-SPC-026** | Phase 9 Architecture Gate (v2.0) | `docs/PhaseDocs/lucia-phase9-Cognition_Unifying/PHASE_9_ARCHITECTURE_GATE.md` | Architectural Decision | P09 | Gate | `CANONICAL` | `DECISION` | Self |
| **DOC-SPC-027** | Phase 9 Ablation Test Report | `docs/PhaseDocs/lucia-phase9-Cognition_Unifying/Phase_9_ABLATION_TEST_V1.md` | Evaluation Evidence | P09 | Ablation | `HISTORICAL` | `EVIDENCE` | `PHASE_9_ARCHITECTURE_GATE.md` |
| **DOC-SPC-028** | Phase 9.5 Real LLM Recovery | `docs/PhaseDocs/lucia-phase9-Cognition_Unifying/PHASE_9_5_REAL_LLM_BACKEND_RECOVERY.md` | Implementation History | P09.5 | Hardware Report | `CANONICAL` | `IMPLEMENTATION` | `docs/ARCHITECTURE.md` §6 |
| **DOC-SPC-029** | Phase 10 Affective Dynamics Spec | `docs/PhaseDocs/lucia-phase10-Affective_Dynamics/Phase_10_AFFECTIVE_DYNAMICS_SPEC.md` | Research History | P10 | Mathematical Spec | `PROMOTED` | `RESEARCH` | `docs/ARCHITECTURE.md` §3.2 |
| **DOC-SPC-030** | Phase 11 Affective Memory Spec | `docs/PhaseDocs/lucia-phase11-Affective_Memory/Phase_11_AFFECTIVE_MEMORY_SPEC.md` | Research History | P11 | Research Spec | `PROMOTED` | `RESEARCH` | `docs/ARCHITECTURE.md` §3.5 |
| **DOC-SPC-031** | Phase 12 Knowledge Learning Spec | `docs/PhaseDocs/lucia-phase12-Knowledge_Learning/Phase_12_KNOWLEDGE_LEARNING_SPEC.md` | Research History | P12 | Ontology Spec | `PROMOTED` | `RESEARCH` | `docs/ARCHITECTURE.md` §8 (ADR-021) |
| **DOC-SPC-032** | Phase 13 Relationship Spec | `docs/PhaseDocs/lucia-phase13-Relationship_Development/Phase_13_RELATIONSHIP_DEVELOPMENT_SPEC.md` | Research History | P13 | Relational Spec | `PROMOTED` | `RESEARCH` | `docs/ARCHITECTURE.md` §8 (ADR-022) |
| **DOC-SPC-033** | Phase 14 Expression Policy Spec | `docs/PhaseDocs/lucia-phase14-Embodiment_Affective_Expression/Phase_14_AFFECTIVE_EXPRESSION_SPEC.md` | Research History | P14 | Actuator Spec | `PROMOTED` | `RESEARCH` | `docs/ARCHITECTURE.md` §8 (ADR-024) |
| **DOC-SPC-034** | Phase 15 Communication Spec | `docs/PhaseDocs/lucia-phase15-Affective_Communication/Phase_15_AFFECTIVE_COMMUNICATION_SPEC.md` | Research History | P15 | Pacing Spec | `PROMOTED` | `RESEARCH` | `docs/ARCHITECTURE.md` §8 (ADR-023) |
| **DOC-SPC-035** | Phase 16 Architecture | `docs/PhaseDocs/lucia-phase16-Affective_Life_Integration/PHASE_16_ARCHITECTURE.md` | Canonical Current | P16 | Architecture | `CANONICAL` | `CANONICAL` | `docs/ARCHITECTURE.md` §2 |
| **DOC-SPC-036** | Phase 16 Integration Plan | `docs/PhaseDocs/lucia-phase16-Affective_Life_Integration/PHASE_16_INTEGRATION_PLAN.md` | Implementation History | P16 | Plan | `IMPLEMENTED` | `IMPLEMENTATION` | `PHASE_16_ARCHITECTURE.md` |
| **DOC-SPC-037** | Phase 16 Promotion Matrix | `docs/PhaseDocs/lucia-phase16-Affective_Life_Integration/PHASE_16_PROMOTION_MATRIX.md` | Architectural Decision | P16 | Gate Matrix | `CANONICAL` | `DECISION` | `PHASE_16_ARCHITECTURE.md` |
| **DOC-SPC-038** | Phase 16 Acceptance Report | `docs/PhaseDocs/lucia-phase16-Affective_Life_Integration/PHASE_16_ACCEPTANCE_REPORT.md` | Implementation History | P16 | Acceptance | `VERIFIED` | `IMPLEMENTATION` | `PHASE_16_ARCHITECTURE.md` |
| **DOC-SPC-039** | Phase 17 Specification | `docs/PhaseDocs/lucia-phase17-Integrated_Affective_Life_Evaluation/PHASE_17_SPECIFICATION.md` | Research History | P17 | Protocol | `VERIFIED` | `RESEARCH` | `PHASE_17_EVALUATION_REPORT.md` |
| **DOC-SPC-040** | Phase 17 Evaluation Report | `docs/PhaseDocs/lucia-phase17-Integrated_Affective_Life_Evaluation/PHASE_17_EVALUATION_REPORT.md` | Evaluation Evidence | P17 | Longitudinal Report | `VERIFIED` | `EVIDENCE` | Self |
| **DOC-SPC-041** | Phase 18 Specification | `docs/PhaseDocs/lucia-phase18-Human_Longitudinal_Validation/PHASE_18_SPECIFICATION.md` | Canonical Current | P18 | Protocol | `CANONICAL` | `CANONICAL` | Self |
| **DOC-SPC-042** | Phase 18 Evaluation Report | `docs/PhaseDocs/lucia-phase18-Human_Longitudinal_Validation/PHASE_18_EVALUATION_REPORT.md` | Evaluation Evidence | P18 | Evaluation Report | `VERIFIED` | `EVIDENCE` | Self |
| **DOC-SPC-043** | Phase 18 RVC Audio Diagnostic | `docs/PhaseDocs/lucia-phase18-Human_Longitudinal_Validation/PHASE_18_RVC_AUDIO_QUALITY_DIAGNOSTIC.md` | Evaluation Evidence | P18 | Diagnostic | `VERIFIED` | `EVIDENCE` | Self |
| **DOC-SPC-044** | Phase 18 RVC Quality Verification | `docs/PhaseDocs/lucia-phase18-Human_Longitudinal_Validation/PHASE_18_RVC_AUDIO_QUALITY_FINAL_VERIFICATION.md` | Evaluation Evidence | P18 | Final Verification | `VERIFIED` | `EVIDENCE` | Self |
| **DOC-SPC-045** | Phase 18 Voice Runtime Verification | `docs/PhaseDocs/lucia-phase18-Human_Longitudinal_Validation/PHASE_18_VOICE_RUNTIME_VERIFICATION_REPORT.md` | Implementation History | P18 | Verification | `VERIFIED` | `IMPLEMENTATION` | Self |
| **DOC-SPC-046** | Phase 18 Audiovisual Regeneration | `docs/PhaseDocs/lucia-phase18-Human_Longitudinal_Validation/PHASE_18_LONGITUDINAL_AUDIOVISUAL_REGENERATION_REPORT.md` | Evaluation Evidence | P18 | Regeneration Report | `VERIFIED` | `EVIDENCE` | Self |
| **DOC-SPC-047** | Phase 18 Human Protocol | `docs/PhaseDocs/lucia-phase18-Human_Longitudinal_Validation/Phase_18_HUMAN_EVALUATION_PROTOCOL.md` | Research History | P18 | Human Protocol | `VERIFIED` | `RESEARCH` | Self |
| **DOC-SPC-048** | Phase 19 Research Proposal | `docs/PhaseDocs/Lucia-phase19-Multi_Timescale_Affective_Life/PHASE_19_RESEARCH_PROPOSAL.md` | Research History | P19 | Proposal | `PROMOTED` | `RESEARCH` | `docs/ARCHITECTURE.md` §3.2 |
| **DOC-SPC-049** | Phase 19 Experiment Plan | `docs/PhaseDocs/Lucia-phase19-Multi_Timescale_Affective_Life/PHASE_19_EXPERIMENT_PLAN.md` | Research History | P19 | Protocol | `VERIFIED` | `RESEARCH` | `PHASE_19_ACCEPTANCE_REPORT.md` |
| **DOC-SPC-050** | Phase 19 Results | `docs/PhaseDocs/Lucia-phase19-Multi_Timescale_Affective_Life/PHASE_19_RESULTS.md` | Evaluation Evidence | P19 | Results | `VERIFIED` | `EVIDENCE` | `PHASE_19_ACCEPTANCE_REPORT.md` |
| **DOC-SPC-051** | Phase 19 Production Design | `docs/PhaseDocs/Lucia-phase19-Multi_Timescale_Affective_Life/PHASE_19_PRODUCTION_REALIZATION_DESIGN.md` | Implementation History | P19 | Design | `IMPLEMENTED` | `IMPLEMENTATION` | `docs/ARCHITECTURE.md` §3.2 |
| **DOC-SPC-052** | Phase 19 Acceptance Report | `docs/PhaseDocs/Lucia-phase19-Multi_Timescale_Affective_Life/PHASE_19_ACCEPTANCE_REPORT.md` | Implementation History | P19 | Acceptance | `VERIFIED` | `IMPLEMENTATION` | Self |
| **DOC-SPC-053** | Phase 20 Research Specification | `docs/PhaseDocs/Lucia-phase20-Affective_Recollection/PHASE_20_RESEARCH_SPEC.md` | Research History | P20 | Specification | `PROMOTED` | `RESEARCH` | `docs/ARCHITECTURE.md` §3.5 |
| **DOC-SPC-054** | Phase 20 Evaluation Report | `docs/PhaseDocs/Lucia-phase20-Affective_Recollection/PHASE_20_RESEARCH_EVALUATION_REPORT.md` | Evaluation Evidence | P20 | Report | `VERIFIED` | `EVIDENCE` | `PHASE_20_ACCEPTANCE_REPORT.md` |
| **DOC-SPC-055** | Phase 20 Results | `docs/PhaseDocs/Lucia-phase20-Affective_Recollection/PHASE_20_RESULTS.md` | Evaluation Evidence | P20 | Results | `VERIFIED` | `EVIDENCE` | `PHASE_20_ACCEPTANCE_REPORT.md` |
| **DOC-SPC-056** | Phase 20 Production Design | `docs/PhaseDocs/Lucia-phase20-Affective_Recollection/PHASE_20_PRODUCTION_REALIZATION_DESIGN.md` | Implementation History | P20 | Design | `IMPLEMENTED` | `IMPLEMENTATION` | `docs/ARCHITECTURE.md` §3.5 |
| **DOC-SPC-057** | Phase 20 Acceptance Report | `docs/PhaseDocs/Lucia-phase20-Affective_Recollection/PHASE_20_ACCEPTANCE_REPORT.md` | Implementation History | P20 | Acceptance | `VERIFIED` | `IMPLEMENTATION` | Self |
| **DOC-SPC-058** | Phase 21 Research Specification | `docs/PhaseDocs/Lucia-phase21-Relational_Consolidation/PHASE_21_RESEARCH_SPEC.md` | Research History | P21 | Specification | `PROMOTED` | `RESEARCH` | `docs/ARCHITECTURE.md` §3.4 |
| **DOC-SPC-059** | Phase 21 Evaluation Report | `docs/PhaseDocs/Lucia-phase21-Relational_Consolidation/PHASE_21_RESEARCH_EVALUATION_REPORT.md` | Evaluation Evidence | P21 | Report | `VERIFIED` | `EVIDENCE` | `PHASE_21_ACCEPTANCE_REPORT.md` |
| **DOC-SPC-060** | Phase 21 Results | `docs/PhaseDocs/Lucia-phase21-Relational_Consolidation/PHASE_21_RESULTS.md` | Evaluation Evidence | P21 | Results | `VERIFIED` | `EVIDENCE` | `PHASE_21_ACCEPTANCE_REPORT.md` |
| **DOC-SPC-061** | Phase 21 Production Design | `docs/PhaseDocs/Lucia-phase21-Relational_Consolidation/PHASE_21_PRODUCTION_REALIZATION_DESIGN.md` | Implementation History | P21 | Design | `IMPLEMENTED` | `IMPLEMENTATION` | `docs/ARCHITECTURE.md` §3.4 |
| **DOC-SPC-062** | Phase 21 Acceptance Report | `docs/PhaseDocs/Lucia-phase21-Relational_Consolidation/PHASE_21_ACCEPTANCE_REPORT.md` | Implementation History | P21 | Acceptance | `VERIFIED` | `IMPLEMENTATION` | Self |

---

## 4. Phase 22 Master Corpus & Epistemic Foraging Research Series

| Doc ID | Title | File Path | Class | Phase | Stage | Status | Authority | Canonical Owner |
|---|---|---|---|---|---|---|---|---|
| **DOC-P22-001** | Phase 22 Master Research Corpus | [`docs/PhaseDocs/Lucia-phase22-Epistemic_Foraging/PHASE_22_FINAL_REPORTS.md`](file:///c:/Users/Lunafiah/Desktop/My_project/Lucia/docs/PhaseDocs/Lucia-phase22-Epistemic_Foraging/PHASE_22_FINAL_REPORTS.md) | Research History | P22 | Master Synthesis | `RESEARCH VALIDATED` | `RESEARCH` | Self |
| **DOC-P22-002** | Phase 22 Research Audit Report | `docs/PhaseDocs/Lucia-phase22-Epistemic_Foraging/PHASE_22_RESEARCH_AUDIT_REPORT.md` | Implementation History | P22 | Audit | `RESEARCH VALIDATED` | `EVIDENCE` | `PHASE_22_FINAL_REPORTS.md` |
| **DOC-P22-003** | Phase 22 Evaluation Walkthrough | `docs/PhaseDocs/Lucia-phase22-Epistemic_Foraging/PHASE_22_walkthrough.md` | Agent Context | P22 | Guide | `RESEARCH VALIDATED` | `CONTEXT` | `PHASE_22_FINAL_REPORTS.md` |
| **DOC-P22-004** | H1 Protocol Amendment v1.4 | `docs/PhaseDocs/Lucia-phase22-Epistemic_Foraging/PHASE_22_H1_PROTOCOL_AMENDMENT_v1.4.md` | Research History | P22-H1 | Protocol | `RATIFIED` | `RESEARCH` | Self |
| **DOC-P22-005** | H1 Path C Execution Report | `docs/PhaseDocs/Lucia-phase22-Epistemic_Foraging/PHASE_22_H1_EXECUTION_REPORT_PATH_C.md` | Evaluation Evidence | P22-H1 | Execution | `INCONCLUSIVE` | `EVIDENCE` | Preserved Negative Evidence |
| **DOC-P22-006** | H1 Gate 2 Compression Diagnostic | `docs/PhaseDocs/Lucia-phase22-Epistemic_Foraging/PHASE_22_H1_GATE2_COMPRESSION_DIAGNOSTIC.md` | Evaluation Evidence | P22-H1 | Diagnostic | `DIAGNOSTIC` | `EVIDENCE` | Preserved Negative Evidence |
| **DOC-P22-007** | H1 Gate 2 Resolution Research | `docs/PhaseDocs/Lucia-phase22-Epistemic_Foraging/PHASE_22_H1_GATE2_RESOLUTION_RESEARCH.md` | Research History | P22-H1 | Resolution | `RESEARCH VALIDATED` | `RESEARCH` | Self |
| **DOC-P22-008** | H1 Measurement Architecture Study | `docs/PhaseDocs/Lucia-phase22-Epistemic_Foraging/PHASE_22_H1_MEASUREMENT_ARCHITECTURE_STUDY.md` | Research History | P22-H1 | Study | `RESEARCH VALIDATED` | `RESEARCH` | Self |
| **DOC-P22-009** | H1 Directional Side-Channel Study | `docs/PhaseDocs/Lucia-phase22-Epistemic_Foraging/PHASE_22_H1_DIRECTIONAL_SIDECHANNEL_BEHAVIORAL_UTILIZATION_STUDY.md` | Research History | P22-H1 | Study | `RESEARCH VALIDATED` | `RESEARCH` | Self |
| **DOC-P22-010** | H1 R3 Architecture Feasibility Study| `docs/PhaseDocs/Lucia-phase22-Epistemic_Foraging/PHASE_22_H1_R3_ARCHITECTURE_INTEGRATION_FEASIBILITY_STUDY.md` | Research History | P22-H1 | Study | `RESEARCH VALIDATED` | `RESEARCH` | Self |
| **DOC-P22-011** | H1 R3 Production Admission Study | `docs/PhaseDocs/Lucia-phase22-Epistemic_Foraging/PHASE_22_H1_R3_PRODUCTION_ADMISSION_CRITERIA_STUDY.md` | Architectural Decision | P22-H1 | Gate Criteria | `RESEARCH VALIDATED` | `DECISION` | Self |
| **DOC-P22-012** | H1 ADR-029 Draft Evidence Ledger | `docs/PhaseDocs/Lucia-phase22-Epistemic_Foraging/PHASE_22_H1_ADR029_DRAFT_UPDATE_EVIDENCE_LEDGER.md` | Architectural Decision | P22-H1 | Ledger | `DRAFT UPDATED` | `DECISION` | `docs/ARCHITECTURE.md` §8 |
| **DOC-P22-013** | H1 End-to-End Behavioral Utility | `docs/PhaseDocs/Lucia-phase22-Epistemic_Foraging/PHASE_22_H1_R3_END_TO_END_BEHAVIORAL_UTILITY_STUDY.md` | Evaluation Evidence | P22-H1 | Study | `RESEARCH VALIDATED` | `EVIDENCE` | Self |
| **DOC-P22-014** | H1 Consumer Transferability Study | `docs/PhaseDocs/Lucia-phase22-Epistemic_Foraging/PHASE_22_H1_R3_CONSUMER_TRANSFERABILITY_STUDY.md` | Evaluation Evidence | P22-H1 | Study | `RESEARCH VALIDATED` | `EVIDENCE` | Self |
| **DOC-P22-015** | H1 Causal Attribution Study | `docs/PhaseDocs/Lucia-phase22-Epistemic_Foraging/PHASE_22_H1_R3_CAUSAL_ATTRIBUTION_STUDY.md` | Evaluation Evidence | P22-H1 | Study | `RESEARCH VALIDATED` | `EVIDENCE` | Self |
| **DOC-P22-016** | H1 Information-Gain Belief Study | `docs/PhaseDocs/Lucia-phase22-Epistemic_Foraging/PHASE_22_H1_R3_INFORMATION_GAIN_BELIEF_UPDATE_STUDY.md` | Evaluation Evidence | P22-H1 | Study | `RESEARCH VALIDATED` | `EVIDENCE` | Self |
| **DOC-P22-017** | H1 Multi-Turn Dialogue Study | `docs/PhaseDocs/Lucia-phase22-Epistemic_Foraging/PHASE_22_H1_MULTI_TURN_INTERACTIVE_DIALOGUE_STUDY.md` | Evaluation Evidence | P22-H1 | Study | `RESEARCH VALIDATED` | `EVIDENCE` | Self |
| **DOC-P22-018** | Phase 22-X Research Specification | `docs/PhaseDocs/Lucia-phase22-Epistemic_Foraging/PHASE_22_X_RESEARCH_SPEC.md` | Research History | P22-X | Specification | `RESEARCH` | `RESEARCH` | Self |
| **DOC-P22-019** | Phase 22-XR Research Specification | `docs/PhaseDocs/Lucia-phase22-Epistemic_Foraging/PHASE_22_XR_RESEARCH_SPEC.md` | Research History | P22-XR | Specification | `RESEARCH` | `RESEARCH` | Self |
| **DOC-P22-020** | Phase 22-XR Laya Verification Protocol| `docs/PhaseDocs/Lucia-phase22-Epistemic_Foraging/PHASE_22_XR_LAYA_VERIFICATION_PROTOCOL.md` | Research History | P22-XR | Protocol | `RESEARCH` | `RESEARCH` | Self |

---

## 5. Phase 23 Semantic Architecture Series (P23-A through P23-I)

| Doc ID | Title | File Path | Class | Phase | Stage | Status | Authority | Canonical Owner |
|---|---|---|---|---|---|---|---|---|
| **DOC-P23-001** | P23 Semantic State Contract v0.2 | [`tests/evaluation/phase23/SEMANTIC_STATE_CONTRACT_v0.2.md`](file:///c:/Users/Lunafiah/Desktop/My_project/Lucia/tests/evaluation/phase23/SEMANTIC_STATE_CONTRACT_v0.2.md) | Research History | P23-A | Contract | `RESEARCH VALIDATED` | `RESEARCH` | Self |
| **DOC-P23-002** | P23 Microbenchmark Spec v0.2 | [`tests/evaluation/phase23/SEMANTIC_FORMATION_MICROBENCHMARK_v0.2.md`](file:///c:/Users/Lunafiah/Desktop/My_project/Lucia/tests/evaluation/phase23/SEMANTIC_FORMATION_MICROBENCHMARK_v0.2.md) | Evaluation Evidence | P23-B | Benchmark Spec | `RESEARCH VALIDATED` | `EVIDENCE` | Self |
| **DOC-P23-003** | P23 Empirical Synthesis v0.1 | [`docs/PhaseDocs/Lucia-phase23-Semantic_Substrate/evaluation_artifacts/phase23/PHASE23_EMPIRICAL_SYNTHESIS_v0.1.md`](file:///c:/Users/Lunafiah/Desktop/My_project/Lucia/docs/PhaseDocs/Lucia-phase23-Semantic_Substrate/evaluation_artifacts/phase23/PHASE23_EMPIRICAL_SYNTHESIS_v0.1.md) | Research History | P23-B | Synthesis | `RESEARCH VALIDATED` | `RESEARCH` | Self |
| **DOC-P23-004** | P23 Semantic Architecture v0.1 | [`docs/PhaseDocs/Lucia-phase23-Semantic_Substrate/evaluation_artifacts/phase23/PHASE23_SEMANTIC_ARCHITECTURE_v0.1.md`](file:///c:/Users/Lunafiah/Desktop/My_project/Lucia/docs/PhaseDocs/Lucia-phase23-Semantic_Substrate/evaluation_artifacts/phase23/PHASE23_SEMANTIC_ARCHITECTURE_v0.1.md) | Architectural Decision | P23-B | Architecture | `RESEARCH VALIDATED` | `DECISION` | Self |
| **DOC-P23-005** | P23-C Concept Formation Monograph | [`docs/PhaseDocs/Lucia-phase23-Semantic_Substrate/evaluation_artifacts/phase23/PHASE23_C_RAW_INPUT_CONCEPT_FORMATION_v0.1.md`](file:///c:/Users/Lunafiah/Desktop/My_project/Lucia/docs/PhaseDocs/Lucia-phase23-Semantic_Substrate/evaluation_artifacts/phase23/PHASE23_C_RAW_INPUT_CONCEPT_FORMATION_v0.1.md) | Research History | P23-C | Monograph | `RESEARCH VALIDATED (CANONICAL)` | `RESEARCH` | Self |
| **DOC-P23-006** | P23-D Evaluation Scaffold README | [`tests/evaluation/evaluation_phase23d/README.md`](file:///c:/Users/Lunafiah/Desktop/My_project/Lucia/tests/evaluation/evaluation_phase23d/README.md) | Evaluation Evidence | P23-D | Scaffold | `RESEARCH VALIDATED` | `EVIDENCE` | `tests/evaluation/evaluation_phase23d/final_synthesis.md` |
| **DOC-P23-007** | P23-D Final Synthesis & Disposition | [`tests/evaluation/evaluation_phase23d/final_synthesis.md`](file:///c:/Users/Lunafiah/Desktop/My_project/Lucia/tests/evaluation/evaluation_phase23d/final_synthesis.md) | Research History | P23-D | Final Synthesis | `RESEARCH VALIDATED / CANONICAL FOUNDATION` | `RESEARCH` | Self |
| **DOC-P23-008** | P23-E Fortification Evaluation Report | [`docs/PhaseDocs/Lucia-phase23-Semantic_Substrate/evaluation_artifacts/phase23e/P23E_FORTIFICATION_EVALUATION_REPORT.md`](file:///c:/Users/Lunafiah/Desktop/My_project/Lucia/docs/PhaseDocs/Lucia-phase23-Semantic_Substrate/evaluation_artifacts/phase23e/P23E_FORTIFICATION_EVALUATION_REPORT.md) | Evaluation Evidence | P23-E | Evaluation | `IMPLEMENTED` | `EVIDENCE` | `docs/00_PROJECT_OVERVIEW.md` §7.2 |
| **DOC-P23-009** | P23-F Adapter Evaluation Report | [`docs/PhaseDocs/Lucia-phase23-Semantic_Substrate/evaluation_artifacts/phase23f/P23F_ADAPTER_EVALUATION_REPORT.md`](file:///c:/Users/Lunafiah/Desktop/My_project/Lucia/docs/PhaseDocs/Lucia-phase23-Semantic_Substrate/evaluation_artifacts/phase23f/P23F_ADAPTER_EVALUATION_REPORT.md) | Evaluation Evidence | P23-F | Evaluation | `IMPLEMENTED` | `EVIDENCE` | `docs/00_PROJECT_OVERVIEW.md` §7.2 |
| **DOC-P23-010** | P23-G Core Contract Evaluation Report| [`docs/PhaseDocs/Lucia-phase23-Semantic_Substrate/evaluation_artifacts/phase23g/P23G_CORE_CONTRACT_EVALUATION_REPORT.md`](file:///c:/Users/Lunafiah/Desktop/My_project/Lucia/docs/PhaseDocs/Lucia-phase23-Semantic_Substrate/evaluation_artifacts/phase23g/P23G_CORE_CONTRACT_EVALUATION_REPORT.md) | Evaluation Evidence | P23-G | Evaluation | `IMPLEMENTED` | `EVIDENCE` | `docs/00_PROJECT_OVERVIEW.md` §7.2 |
| **DOC-P23-011** | P23-H Reasoning Kernel Evaluation | [`docs/PhaseDocs/Lucia-phase23-Semantic_Substrate/evaluation_artifacts/phase23h/P23H_CORE_REASONING_EVALUATION_REPORT.md`](file:///c:/Users/Lunafiah/Desktop/My_project/Lucia/docs/PhaseDocs/Lucia-phase23-Semantic_Substrate/evaluation_artifacts/phase23h/P23H_CORE_REASONING_EVALUATION_REPORT.md) | Evaluation Evidence | P23-H | Evaluation | `FROZEN @ 3eef803` | `EVIDENCE` | `docs/research/P23-H_FINAL_STATE.md` |
| **DOC-P23-012** | P23-H Final State & Epistemic Boundary| [`docs/research/P23-H_FINAL_STATE.md`](file:///c:/Users/Lunafiah/Desktop/My_project/Lucia/docs/research/P23-H_FINAL_STATE.md) | Canonical Current | P23-H | State Spec | `FROZEN @ 3eef803` | `CANONICAL` | Self |
| **DOC-P23-013** | P23 Consolidated Research History | [`docs/research/P23_HISTORY_CONSOLIDATED.md`](file:///c:/Users/Lunafiah/Desktop/My_project/Lucia/docs/research/P23_HISTORY_CONSOLIDATED.md) | Research History | P23 | History Index | `RESEARCH VALIDATED` | `RESEARCH` | Self |
| **DOC-P23-014** | P23 Authoritative Source Map | [`docs/research/P23_SOURCE_MAP.md`](file:///c:/Users/Lunafiah/Desktop/My_project/Lucia/docs/research/P23_SOURCE_MAP.md) | Canonical Current | P23 | Source Map | `CANONICAL` | `CANONICAL` | Self |
| **DOC-P23-015** | P23-I Research Context & Boundary | [`docs/research/P23-I_RESEARCH_CONTEXT.md`](file:///c:/Users/Lunafiah/Desktop/My_project/Lucia/docs/research/P23-I_RESEARCH_CONTEXT.md) | Research History | P23-I | Research Context | `CLOSED (ABSORBED INTO P23-G ARCH-030.1)` | `RESEARCH` | Self |
| **DOC-P23-016** | P23-I Gemini Final Research Report | [`docs/research/P23-I_FINAL_RESEARCH_REPORT.md`](file:///c:/Users/Lunafiah/Desktop/My_project/Lucia/docs/research/P23-I_FINAL_RESEARCH_REPORT.md) | Research History | P23-I | Final Report | `SUPERSEDED PRELIMINARY RECOMMENDATION` | `RESEARCH` | Self (Attributed to Gemini) |
| **DOC-P23-017** | P23-I Evidence Closure & Falsification Report | [`docs/research/P23-I_EVIDENCE_CLOSURE_AND_FALSIFICATION_REPORT.md`](file:///c:/Users/Lunafiah/Desktop/My_project/Lucia/docs/research/P23-I_EVIDENCE_CLOSURE_AND_FALSIFICATION_REPORT.md) | Evaluation Evidence | P23-I | Evidence Closure | `CLOSED (REJECTED / BOUNDARY ABSORBED INTO P23-G)` | `EVIDENCE` | Self |

---

## 6. Reviewer Context Projections (Ciah 5-File Pack)

| Doc ID | Title | File Path | Class | Target Agent | Status | Authority | Canonical Source |
|---|---|---|---|---|---|---|---|
| **DOC-REV-001** | Pack File 1: Executive Context | [`docs/research/P23_REVIEW_01_EXECUTIVE_CONTEXT.md`](file:///c:/Users/Lunafiah/Desktop/My_project/Lucia/docs/research/P23_REVIEW_01_EXECUTIVE_CONTEXT.md) | Agent Context | Ciah | `ACTIVE` | `CONTEXT` | `docs/00_PROJECT_OVERVIEW.md` |
| **DOC-REV-002** | Pack File 2: Phase History | [`docs/research/P23_REVIEW_02_PHASE_HISTORY.md`](file:///c:/Users/Lunafiah/Desktop/My_project/Lucia/docs/research/P23_REVIEW_02_PHASE_HISTORY.md) | Agent Context | Ciah | `ACTIVE` | `CONTEXT` | `docs/research/P23_HISTORY_CONSOLIDATED.md` |
| **DOC-REV-003** | Pack File 3: Architecture State | [`docs/research/P23_REVIEW_03_ARCHITECTURE_STATE.md`](file:///c:/Users/Lunafiah/Desktop/My_project/Lucia/docs/research/P23_REVIEW_03_ARCHITECTURE_STATE.md) | Agent Context | Ciah | `ACTIVE` | `CONTEXT` | `docs/ARCHITECTURE.md` |
| **DOC-REV-004** | Pack File 4: Evidence & Negatives | [`docs/research/P23_REVIEW_04_EVIDENCE_AND_NEGATIVE_RESULTS.md`](file:///c:/Users/Lunafiah/Desktop/My_project/Lucia/docs/research/P23_REVIEW_04_EVIDENCE_AND_NEGATIVE_RESULTS.md) | Agent Context | Ciah | `ACTIVE` | `CONTEXT` | `docs/PhaseDocs/**/evaluation_artifacts/**` |
| **DOC-REV-005** | Pack File 5: Ciah Review Context & Boundary | [`docs/research/P23_REVIEW_05_P23-I_RESEARCH_BOUNDARY.md`](file:///c:/Users/Lunafiah/Desktop/My_project/Lucia/docs/research/P23_REVIEW_05_P23-I_RESEARCH_BOUNDARY.md) | Agent Context | Ciah | `CLOSED (P23-I ABSORBED INTO P23-G ARCH-030.1)` | `CONTEXT` | `docs/research/P23-I_EVIDENCE_CLOSURE_AND_FALSIFICATION_REPORT.md` |

---

## 7. Phase 24 Adaptive Communication Series & Retrospective Research

| Doc ID | Title | File Path | Class | Phase | Stage | Status | Authority | Canonical Owner |
|---|---|---|---|---|---|---|---|---|
| **DOC-P24-001** | P24 Adaptive Communication Contract | [`tests/evaluation/phase24/P24_ADAPTIVE_COMMUNICATION_CONTRACT.md`](file:///c:/Users/Lunafiah/Desktop/My_project/Lucia/tests/evaluation/phase24/P24_ADAPTIVE_COMMUNICATION_CONTRACT.md) | Architectural Decision | P24 | Contract | `RATIFIED / IMPLEMENTED` | `DECISION` | `docs/ARCHITECTURE.md` §8 (ADR-032) |
| **DOC-P24-002** | P24 ADR Adaptive Communication | [`tests/evaluation/phase24/P24_ADR_ADAPTIVE_COMMUNICATION.md`](file:///c:/Users/Lunafiah/Desktop/My_project/Lucia/tests/evaluation/phase24/P24_ADR_ADAPTIVE_COMMUNICATION.md) | Architectural Decision | P24 | ADR Specification | `RATIFIED / IMPLEMENTED` | `DECISION` | `docs/ARCHITECTURE.md` §8 (ADR-032) |
| **DOC-P24-003** | P24 Gemini Final Research Report | [`docs/research/P24_GEMINI'S_REPORT.md`](file:///c:/Users/Lunafiah/Desktop/My_project/Lucia/docs/research/P24_GEMINI%27S_REPORT.md) | Research History | P24 | Synthesis | `RESEARCH VALIDATED` | `RESEARCH` | Self |
| **DOC-P24-004** | P24 Voice Benchmark Prosody Report | [`tests/evaluation/phase24/voice_benchmark/VOICE_BENCHMARK_PROSODY_REPORT.md`](file:///c:/Users/Lunafiah/Desktop/My_project/Lucia/tests/evaluation/phase24/voice_benchmark/VOICE_BENCHMARK_PROSODY_REPORT.md) | Evaluation Evidence | P24 | Benchmark Report | `EMPIRICALLY VERIFIED` | `EVIDENCE` | Self |
| **DOC-RES-001** | Retrospective 7-Topic Architectural Gap Review | [`docs/research/RETROSPECTIVE_ARCHITECTURAL_GAP_REVIEW_7_TOPICS.md`](file:///c:/Users/Lunafiah/Desktop/My_project/Lucia/docs/research/RETROSPECTIVE_ARCHITECTURAL_GAP_REVIEW_7_TOPICS.md) | Research History | Post-P24 | Architectural Review | `RESEARCH REVIEW (NON-CANONICAL)` | `RESEARCH` | Self |

---

## 8. Phase 25 Research Evidence & Inquiries

| Doc ID | Title | File Path | Class | Phase | Stage | Status | Authority | Canonical Owner |
|---|---|---|---|---|---|---|---|---|
| **DOC-P25-001** | Phase 25 Evaluation Report | [`docs/PhaseDocs/Lucia-phase25-Temporal_Embodiment/evaluation_report.md`](file:///c:/Users/Lunafiah/Desktop/My_project/Lucia/docs/PhaseDocs/Lucia-phase25-Temporal_Embodiment/evaluation_report.md) | Evaluation Evidence | P25 | Harness Report | `RESEARCH EVIDENCE` | `EVIDENCE` | Self |
| **DOC-P25-002** | P25-Q1 Final Research Report | [`docs/PhaseDocs/Lucia-phase25-Temporal_Embodiment/P25_Q1_FINAL_RESEARCH_REPORT.md`](file:///c:/Users/Lunafiah/Desktop/My_project/Lucia/docs/PhaseDocs/Lucia-phase25-Temporal_Embodiment/P25_Q1_FINAL_RESEARCH_REPORT.md) | Research Synthesis | P25 | Final Research Artifact | `P25-Q1 RESEARCH COMPLETE / ARCHIVED AS EVIDENCE` | `EVIDENCE` | Self |
| **DOC-P25-003** | P25-Q2 Scientific Calibration | [`docs/PhaseDocs/Lucia-phase25-Temporal_Embodiment/P25_Q2_SCIENTIFIC_CALIBRATION.md`](file:///c:/Users/Lunafiah/Desktop/My_project/Lucia/docs/PhaseDocs/Lucia-phase25-Temporal_Embodiment/P25_Q2_SCIENTIFIC_CALIBRATION.md) | Research Specification | P25 | Scientific Calibration | `CALIBRATION RATIFIED / SPEC STAGED` | `RESEARCH SPEC` | Self |
| **DOC-P25-004** | EXP-P25-Q2.1 Evaluation Specification | [`docs/PhaseDocs/Lucia-phase25-Temporal_Embodiment/EXP_P25_Q2_1_EVALUATION_SPECIFICATION.md`](file:///c:/Users/Lunafiah/Desktop/My_project/Lucia/docs/PhaseDocs/Lucia-phase25-Temporal_Embodiment/EXP_P25_Q2_1_EVALUATION_SPECIFICATION.md) | Evaluation Specification | P25 | Formal Specification | `HISTORICAL SPECIFICATION / HARNESS EXECUTED (C2 BLOCKED)` | `EVAL SPEC` | Self |
| **DOC-P25-005** | EXP-P25-Q2.1 Final Evaluation Report | [`docs/PhaseDocs/Lucia-phase25-Temporal_Embodiment/evaluation_artifacts/phase25/EXP-P25-Q2.1/FINAL_EVALUATION_REPORT.md`](file:///c:/Users/Lunafiah/Desktop/My_project/Lucia/docs/PhaseDocs/Lucia-phase25-Temporal_Embodiment/evaluation_artifacts/phase25/EXP-P25-Q2.1/FINAL_EVALUATION_REPORT.md) | Evaluation Evidence | P25 | Final Evaluation Report | `AUDITED / RERUN REQUIRED (SURROGATE INVALID)` | `EVIDENCE` | Self |
| **DOC-P25-006** | P25-Q2 Surrogate Methodology Review | [`docs/PhaseDocs/Lucia-phase25-Temporal_Embodiment/P25_Q2_SURROGATE_METHODOLOGY_REVIEW.md`](file:///c:/Users/Lunafiah/Desktop/My_project/Lucia/docs/PhaseDocs/Lucia-phase25-Temporal_Embodiment/P25_Q2_SURROGATE_METHODOLOGY_REVIEW.md) | Research Specification | P25 | Methodology Note | `RATIFIED METHODOLOGY AUDIT / RERUN NOT AUTHORIZED` | `RESEARCH SPEC` | Self |
| **DOC-P25-007** | P25-Q2 Metric Ratification (TBD-Q2-05) | [`docs/PhaseDocs/Lucia-phase25-Temporal_Embodiment/P25_Q2_METRIC_RATIFICATION.md`](file:///c:/Users/Lunafiah/Desktop/My_project/Lucia/docs/PhaseDocs/Lucia-phase25-Temporal_Embodiment/P25_Q2_METRIC_RATIFICATION.md) | Research Specification | P25 | Metric Ratification | `TBD-Q2-05 RATIFIED / RERUN NOT AUTHORIZED` | `RESEARCH SPEC` | Self |
| **DOC-P25-008** | P25-Q2 Pre-Rerun Architecture Review | [`docs/PhaseDocs/Lucia-phase25-Temporal_Embodiment/P25_Q2_ARCHITECTURE_REVIEW_PRE_RERUN.md`](file:///c:/Users/Lunafiah/Desktop/My_project/Lucia/docs/PhaseDocs/Lucia-phase25-Temporal_Embodiment/P25_Q2_ARCHITECTURE_REVIEW_PRE_RERUN.md) | Architecture Review | P25 | Pre-Rerun Review | `Architecture Candidate / Evidence Synthesis` | `ARCH REVIEW` | Self |
| **DOC-P25-009** | P25-Q2 w_fb Calibration (TBD-Q2-04) | [`docs/PhaseDocs/Lucia-phase25-Temporal_Embodiment/P25_Q2_Q2-04_WFB_CALIBRATION.md`](file:///c:/Users/Lunafiah/Desktop/My_project/Lucia/docs/PhaseDocs/Lucia-phase25-Temporal_Embodiment/P25_Q2_Q2-04_WFB_CALIBRATION.md) | Research Specification | P25 | Parameter Calibration | `Q2-04 REMAINS OPEN / C2 BLOCKED` | `RESEARCH SPEC` | Self |
| **DOC-P25-010** | P25 Post-Q2-04 Research Clarification | [`docs/PhaseDocs/Lucia-phase25-Temporal_Embodiment/P25_Q2_RESEARCH_CLARIFICATION.md`](file:///c:/Users/Lunafiah/Desktop/My_project/Lucia/docs/PhaseDocs/Lucia-phase25-Temporal_Embodiment/P25_Q2_RESEARCH_CLARIFICATION.md) | Research Specification | P25 | Research Clarification | `NEXT RESEARCH QUESTION IDENTIFIED` | `RESEARCH SPEC` | Self |
| **DOC-P25-011** | P25-Q2 w_fb Identifiability Audit | [`docs/PhaseDocs/Lucia-phase25-Temporal_Embodiment/P25_Q2_Q2-04_WFB_IDENTIFIABILITY_AUDIT.md`](file:///c:/Users/Lunafiah/Desktop/My_project/Lucia/docs/PhaseDocs/Lucia-phase25-Temporal_Embodiment/P25_Q2_Q2-04_WFB_IDENTIFIABILITY_AUDIT.md) | Research Specification | P25 | Identifiability Audit | `IDENTIFIABILITY CLASSIFICATION RATIFIED / w_fb UNIDENTIFIED / C2 BLOCKED` | `RESEARCH SPEC` | Self |
| **DOC-P25-012** | P25-Q2 Q2-04 Protocol Design Space Audit | [`docs/PhaseDocs/Lucia-phase25-Temporal_Embodiment/P25_Q2_Q2-04_PROTOCOL_DESIGN_SPACE.md`](file:///c:/Users/Lunafiah/Desktop/My_project/Lucia/docs/PhaseDocs/Lucia-phase25-Temporal_Embodiment/P25_Q2_Q2-04_PROTOCOL_DESIGN_SPACE.md) | Research Specification | P25 | Protocol Design Space Audit | `PROTOCOL DESIGN SPACE SUFFICIENTLY MAPPED / w_fb UNIDENTIFIED / C2 BLOCKED` | `RESEARCH SPEC` | Self |
| **DOC-P25-013** | P25-Q2 Q2-04 Protocol Specification Audit | [`docs/PhaseDocs/Lucia-phase25-Temporal_Embodiment/P25_Q2_Q2-04_PROTOCOL_SPECIFICATION.md`](file:///c:/Users/Lunafiah/Desktop/My_project/Lucia/docs/PhaseDocs/Lucia-phase25-Temporal_Embodiment/P25_Q2_Q2-04_PROTOCOL_SPECIFICATION.md) | Research Specification | P25 | Protocol Specification Audit | `PROTOCOL CANDIDATE SELECTION NOT RATIFIED / w_fb UNIDENTIFIED / C2 BLOCKED` | `RESEARCH SPEC` | Self |
| **DOC-P25-014** | P25 Coverage & Research Gap Audit | [`docs/PhaseDocs/Lucia-phase25-Temporal_Embodiment/P25_COVERAGE_AND_RESEARCH_GAP_AUDIT.md`](file:///c:/Users/Lunafiah/Desktop/My_project/Lucia/docs/PhaseDocs/Lucia-phase25-Temporal_Embodiment/P25_COVERAGE_AND_RESEARCH_GAP_AUDIT.md) | Research Audit | P25 | Coverage & Research Gap Audit | `AUDIT RATIFIED / RESEARCH COVERAGE SUFFICIENT / FREEZE CANDIDATE` | `RESEARCH AUDIT` | Self |
| **DOC-P25-015** | P25 Source & Mechanism Verification Audit | [`docs/PhaseDocs/Lucia-phase25-Temporal_Embodiment/P25_SOURCE_MECHANISM_VERIFICATION_AUDIT.md`](file:///c:/Users/Lunafiah/Desktop/My_project/Lucia/docs/PhaseDocs/Lucia-phase25-Temporal_Embodiment/P25_SOURCE_MECHANISM_VERIFICATION_AUDIT.md) | Research Audit | P25 | Source & Mechanism Verification | `AUDIT RATIFIED / GATE_0_PREMATURE` | `RESEARCH AUDIT` | Self |
| **DOC-P25-016** | P25 Architecture Contract v0.1 | [`docs/PhaseDocs/Lucia-phase25-Temporal_Embodiment/P25_ARCHITECTURE_CONTRACT_v0.1.md`](file:///c:/Users/Lunafiah/Desktop/My_project/Lucia/docs/PhaseDocs/Lucia-phase25-Temporal_Embodiment/P25_ARCHITECTURE_CONTRACT_v0.1.md) | Architectural Decision | P25 | Architecture Contract | `APPROVED UNILATERAL BASELINE (CONTRACT v0.1)` | `DECISION` | Self |
| **DOC-P25-017** | P25 Finalization & Freeze Report | [`docs/PhaseDocs/Lucia-phase25-Temporal_Embodiment/P25_FINALIZATION_AND_FREEZE_REPORT.md`](file:///c:/Users/Lunafiah/Desktop/My_project/Lucia/docs/PhaseDocs/Lucia-phase25-Temporal_Embodiment/P25_FINALIZATION_AND_FREEZE_REPORT.md) | Governance & Freeze | P25 | Finalization & Freeze | `IMPLEMENTED / VERIFIED / CLOSED (Unilateral Baseline)` | `CANONICAL CLOSURE` | Self |

---

## 9. Phase 26 Emergent Individuality Research Evidence & Post-Trial Freeze

| Doc ID | Title | File Path | Class | Phase | Stage | Status | Authority | Canonical Owner |
|---|---|---|---|---|---|---|---|---|
| **DOC-P26-001** | P26 Experimental Protocol v0.1 | [`docs/PhaseDocs/lucia-phase26-Emergent Individuality & Autonomous Preferences/P26 Experimental Protocol v0.1.md`](file:///c:/Users/Lunafiah/Desktop/My_project/Lucia/docs/PhaseDocs/lucia-phase26-Emergent%20Individuality%20&%20Autonomous%20Preferences/P26%20Experimental%20Protocol%20v0.1.md) | Research Specification | P26 | Protocol | `FROZEN` | `RESEARCH SPEC` | Self |
| **DOC-P26-002** | P26 Evaluative Behavioral Probe Spec v0.1 | [`docs/PhaseDocs/lucia-phase26-Emergent Individuality & Autonomous Preferences/evaluation_artifacts/protocol_feasibility/P26_EVALUATIVE_PROBE_SPEC_v0.1.md`](file:///c:/Users/Lunafiah/Desktop/My_project/Lucia/docs/PhaseDocs/lucia-phase26-Emergent%20Individuality%20&%20Autonomous%20Preferences/evaluation_artifacts/protocol_feasibility/P26_EVALUATIVE_PROBE_SPEC_v0.1.md) | Research Specification | P26 | Instrument Spec | `FROZEN` | `RESEARCH SPEC` | Self |
| **DOC-P26-003** | P26 Evaluative Probe Pre-Validation Report | [`docs/PhaseDocs/lucia-phase26-Emergent Individuality & Autonomous Preferences/evaluation_artifacts/protocol_feasibility/P26_EVALUATIVE_PROBE_PREVALIDATION.md`](file:///c:/Users/Lunafiah/Desktop/My_project/Lucia/docs/PhaseDocs/lucia-phase26-Emergent%20Individuality%20&%20Autonomous%20Preferences/evaluation_artifacts/protocol_feasibility/P26_EVALUATIVE_PROBE_PREVALIDATION.md) | Evaluation Evidence | P26 | Pre-Validation | `VALIDATED` | `EVIDENCE` | Self |
| **DOC-P26-004** | P26 Step 6 Protocol Validation Gate Review | [`docs/PhaseDocs/lucia-phase26-Emergent Individuality & Autonomous Preferences/evaluation_artifacts/protocol_feasibility/P26_STEP6_PROTOCOL_VALIDATION_GATE.md`](file:///c:/Users/Lunafiah/Desktop/My_project/Lucia/docs/PhaseDocs/lucia-phase26-Emergent%20Individuality%20&%20Autonomous%20Preferences/evaluation_artifacts/protocol_feasibility/P26_STEP6_PROTOCOL_VALIDATION_GATE.md) | Research Audit | P26 | Gate Review | `GATE PASSED` | `RESEARCH AUDIT` | Self |
| **DOC-P26-005** | P26 Experimental Design Freeze Specification | [`docs/PhaseDocs/lucia-phase26-Emergent Individuality & Autonomous Preferences/evaluation_artifacts/protocol_feasibility/P26_EXPERIMENTAL_DESIGN_FREEZE.md`](file:///c:/Users/Lunafiah/Desktop/My_project/Lucia/docs/PhaseDocs/lucia-phase26-Emergent%20Individuality%20&%20Autonomous%20Preferences/evaluation_artifacts/protocol_feasibility/P26_EXPERIMENTAL_DESIGN_FREEZE.md) | Research Specification | P26 | Design Freeze | `FROZEN (SHA-256 RATIFIED)` | `RESEARCH SPEC` | Self |
| **DOC-P26-006** | P26 C2/C3 Scientific Trial Execution Report | [`docs/PhaseDocs/lucia-phase26-Emergent Individuality & Autonomous Preferences/evaluation_artifacts/protocol_feasibility/P26_C2_C3_TRIAL_EXECUTION_REPORT.md`](file:///c:/Users/Lunafiah/Desktop/My_project/Lucia/docs/PhaseDocs/lucia-phase26-Emergent%20Individuality%20&%20Autonomous%20Preferences/evaluation_artifacts/protocol_feasibility/P26_C2_C3_TRIAL_EXECUTION_REPORT.md) | Evaluation Evidence | P26 | Trial Execution | `TRIAL COMPLETED (N=120)` | `EVIDENCE` | Self |
| **DOC-P26-007** | P26 Post-Trial Scientific Audit & Result Freeze Report | [`docs/PhaseDocs/lucia-phase26-Emergent Individuality & Autonomous Preferences/evaluation_artifacts/protocol_feasibility/P26_POST_TRIAL_SCIENTIFIC_AUDIT.md`](file:///c:/Users/Lunafiah/Desktop/My_project/Lucia/docs/PhaseDocs/lucia-phase26-Emergent%20Individuality%20&%20Autonomous%20Preferences/evaluation_artifacts/protocol_feasibility/P26_POST_TRIAL_SCIENTIFIC_AUDIT.md) | Research Audit | P26 | Result Freeze | `RESULT FROZEN / NOT PROMOTED` | `RESEARCH AUDIT` | Self |

---

## 10. Phase 27 Personalized Individual Trajectory Research Closure

| Doc ID | Title | File Path | Class | Phase | Stage | Status | Authority | Canonical Owner |
|---|---|---|---|---|---|---|---|---|
| **DOC-P27-001** | P27 Scientific Boundary Audit & Research Closure Report | [`docs/PhaseDocs/Lucia-phase27-Personalized_Individual_Trajectory/P27_SCIENTIFIC_CLOSURE_REPORT.md`](file:///c:/Users/Lunafiah/Desktop/My_project/Lucia/docs/PhaseDocs/Lucia-phase27-Personalized_Individual_Trajectory/P27_SCIENTIFIC_CLOSURE_REPORT.md) | Research History | P27 | Scientific Closure | `CLOSED / NO NEW SCIENTIFIC GAP` | `CANONICAL CLOSURE` | `docs/PHASE_REGISTRY.md` |

## 11. Genesis Preparation Series

| Doc ID | Title | File Path | Class | Phase | Stage | Status | Authority | Canonical Owner |
|---|---|---|---|---|---|---|---|---|
| **DOC-GEN-001** | Genesis Semantic & Protocol Contract Implementation | [`docs/others/GENESIS_CONTRACT_IMPLEMENTATION/GENESIS_CONTRACT_IMPLEMENTATION.md`](file:///c:/Users/Lunafiah/Desktop/My_project/Lucia/docs/others/GENESIS_CONTRACT_IMPLEMENTATION/GENESIS_CONTRACT_IMPLEMENTATION.md) | Engineering Implementation | Non-Phase | Implementation | `IMPLEMENTED & VERIFIED` | `DECISION` | Self |
| **DOC-GEN-FREEZE-001** | Genesis Preparation Canonical Closure & Freeze Report | [`docs/others/GENESIS_PREPARATION_FREEZE/GENESIS_PREPARATION_FREEZE_REPORT.md`](file:///c:/Users/Lunafiah/Desktop/My_project/Lucia/docs/others/GENESIS_PREPARATION_FREEZE/GENESIS_PREPARATION_FREEZE_REPORT.md) | Governance & Freeze | Non-Phase | Freeze Report | `GENESIS PREPARATION FROZEN` | `CANONICAL CLOSURE` | `docs/PHASE_REGISTRY.md` |

---

## 12. Maintenance & Registration Rules

When authoring any new document, specification, or evaluation report:
1. **Assign a Document ID**: Prepend with standard category prefix (`DOC-CAN`, `DOC-SPC`, `DOC-P22`, `DOC-P23`, `DOC-P24`, `DOC-P25`, `DOC-P26`, `DOC-P27`, `DOC-REV`, `DOC-RES`).
2. **Explicit Canonical Owner**: The document must explicitly declare which document owns the underlying facts.
3. **Register in Document Registry**: Add the document entry to this catalog before merging into main.
4. **Epistemic Invariant Check**: Ensure unproven hypotheses are marked `RESEARCH` and never `VERIFIED`.

