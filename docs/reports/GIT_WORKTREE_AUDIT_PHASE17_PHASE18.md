# Git Working-Tree Audit & Commit Plan — Phase 17 + Phase 18

> **Document Authority:** Authoritative Git Audit and Commit Strategy Report
> **Status:** AUDIT COMPLETE — FILTER REQUIRED
> **Date:** 2026-09-13
> **Repository:** `Lucia` (Branch: `main`)

---

## 1. Summary

- **Total changed/untracked files:** 129
- **Production:** 8
- **Tests:** 14
- **Docs:** 4
- **Reports:** 6
- **Manifests / Provenance Data:** 14
- **Audio:** 7
- **Video:** 7
- **Models:** 0 (0 untracked in Git worktree; real weights in `models/voice/rvc/` are 100% ignored by `.gitignore`)
- **Generated/temp:** 68 (46 in `docs/specs/.../temp_run_store/`, 21 in `evaluation_artifacts/phase18/temp_harness/`, 1 duplicate manifest)
- **Other:** 0

### High-Level Disposition Summary

| Disposition | File Count | Total Size | Description |
|---|---:|---:|---|
| **Definitely Safe to Commit (KEEP)** | 37 | 2.53 MB | Production RVC source, evaluation suites, specifications, reports, and matrix data |
| **Files Requiring Review (REVIEW)** | 24 | 3.74 MB | Official Phase 18 evidence: 7 WAV audio, 7 MP4 video, 10 session telemetry JSON files |
| **Files That Should NOT Be Committed (EXCLUDE)** | 68 | 437.8 KB | Ephemeral test execution residues (mock models, temp snapshots, duplicate manifest) |
| **TOTAL** | **129** | **6.70 MB** | Complete inventory of all uncommitted working-tree items |

---

## 2. Complete File Inventory

The table below lists every single one of the 129 changed/untracked files in the repository working tree:

| # | File | Phase | Category | Size | Keep? | Git Treatment | Reason |
|---|---|---|---|---:|---|---|---|
| 1 | `docs/CURRENT_STATUS.md` | Shared | Documentation / Spec / ADR | 38.1 KB | **KEEP** | Git Commit (Commit 5) | System architecture documentation index & live operational status tracking |
| 2 | `docs/DOCUMENTATION_INDEX.md` | Shared | Documentation / Spec / ADR | 23.7 KB | **KEEP** | Git Commit (Commit 5) | System architecture documentation index & live operational status tracking |
| 3 | `docs/specs/lucia-phase17-Integrated_Affective_Life_Evaluation/PHASE_17_EVALUATION_REPORT.md` | Phase 17 | Documentation / Spec / ADR | 27.3 KB | **KEEP** | Git Commit (Commit 1) | Authoritative Phase 17 specification and evaluation report |
| 4 | `docs/specs/lucia-phase17-Integrated_Affective_Life_Evaluation/PHASE_17_SPECIFICATION.md` | Phase 17 | Documentation / Spec / ADR | 12.7 KB | **KEEP** | Git Commit (Commit 1) | Authoritative Phase 17 specification and evaluation report |
| 5 | `docs/specs/lucia-phase17-Integrated_Affective_Life_Evaluation/results/phase17_evaluation_matrix.json` | Phase 17 | Manifest / Provenance / Reproducibility Data | 1.50 MB | **KEEP** | Git Commit (Commit 1) | Authoritative Phase 17 evaluation matrix data |
| 6 | `docs/specs/lucia-phase17-Integrated_Affective_Life_Evaluation/results/temp_run_store/TrackA_Alternating_40_104/model.gguf` | Phase 17 | Cache / Temp / Build Output | 25 B | **DO NOT COMMIT** | Exclude / Ignore | Ephemeral Phase 17 test run scratch store (mock model / temp relationship snapshot) |
| 7 | `docs/specs/lucia-phase17-Integrated_Affective_Life_Evaluation/results/temp_run_store/TrackA_Alternating_40_104/relationship.json` | Phase 17 | Cache / Temp / Build Output | 31.0 KB | **DO NOT COMMIT** | Exclude / Ignore | Ephemeral Phase 17 test run scratch store (mock model / temp relationship snapshot) |
| 8 | `docs/specs/lucia-phase17-Integrated_Affective_Life_Evaluation/results/temp_run_store/TrackA_Long_100_105/model.gguf` | Phase 17 | Cache / Temp / Build Output | 25 B | **DO NOT COMMIT** | Exclude / Ignore | Ephemeral Phase 17 test run scratch store (mock model / temp relationship snapshot) |
| 9 | `docs/specs/lucia-phase17-Integrated_Affective_Life_Evaluation/results/temp_run_store/TrackA_Long_100_105/relationship.json` | Phase 17 | Cache / Temp / Build Output | 36.0 KB | **DO NOT COMMIT** | Exclude / Ignore | Ephemeral Phase 17 test run scratch store (mock model / temp relationship snapshot) |
| 10 | `docs/specs/lucia-phase17-Integrated_Affective_Life_Evaluation/results/temp_run_store/TrackA_Negative_50_103/model.gguf` | Phase 17 | Cache / Temp / Build Output | 25 B | **DO NOT COMMIT** | Exclude / Ignore | Ephemeral Phase 17 test run scratch store (mock model / temp relationship snapshot) |
| 11 | `docs/specs/lucia-phase17-Integrated_Affective_Life_Evaluation/results/temp_run_store/TrackA_Negative_50_103/relationship.json` | Phase 17 | Cache / Temp / Build Output | 38.8 KB | **DO NOT COMMIT** | Exclude / Ignore | Ephemeral Phase 17 test run scratch store (mock model / temp relationship snapshot) |
| 12 | `docs/specs/lucia-phase17-Integrated_Affective_Life_Evaluation/results/temp_run_store/TrackA_Neutral_50_101/model.gguf` | Phase 17 | Cache / Temp / Build Output | 25 B | **DO NOT COMMIT** | Exclude / Ignore | Ephemeral Phase 17 test run scratch store (mock model / temp relationship snapshot) |
| 13 | `docs/specs/lucia-phase17-Integrated_Affective_Life_Evaluation/results/temp_run_store/TrackA_Neutral_50_101/relationship.json` | Phase 17 | Cache / Temp / Build Output | 38.8 KB | **DO NOT COMMIT** | Exclude / Ignore | Ephemeral Phase 17 test run scratch store (mock model / temp relationship snapshot) |
| 14 | `docs/specs/lucia-phase17-Integrated_Affective_Life_Evaluation/results/temp_run_store/TrackA_Positive_50_102/model.gguf` | Phase 17 | Cache / Temp / Build Output | 25 B | **DO NOT COMMIT** | Exclude / Ignore | Ephemeral Phase 17 test run scratch store (mock model / temp relationship snapshot) |
| 15 | `docs/specs/lucia-phase17-Integrated_Affective_Life_Evaluation/results/temp_run_store/TrackA_Positive_50_102/relationship.json` | Phase 17 | Cache / Temp / Build Output | 38.8 KB | **DO NOT COMMIT** | Exclude / Ignore | Ephemeral Phase 17 test run scratch store (mock model / temp relationship snapshot) |
| 16 | `docs/specs/lucia-phase17-Integrated_Affective_Life_Evaluation/results/temp_run_store/TrackB_AblateBodyIPC_201/model.gguf` | Phase 17 | Cache / Temp / Build Output | 25 B | **DO NOT COMMIT** | Exclude / Ignore | Ephemeral Phase 17 test run scratch store (mock model / temp relationship snapshot) |
| 17 | `docs/specs/lucia-phase17-Integrated_Affective_Life_Evaluation/results/temp_run_store/TrackB_AblateBodyIPC_201/relationship.json` | Phase 17 | Cache / Temp / Build Output | 2.3 KB | **DO NOT COMMIT** | Exclude / Ignore | Ephemeral Phase 17 test run scratch store (mock model / temp relationship snapshot) |
| 18 | `docs/specs/lucia-phase17-Integrated_Affective_Life_Evaluation/results/temp_run_store/TrackB_AblateCommPolicy_201/model.gguf` | Phase 17 | Cache / Temp / Build Output | 25 B | **DO NOT COMMIT** | Exclude / Ignore | Ephemeral Phase 17 test run scratch store (mock model / temp relationship snapshot) |
| 19 | `docs/specs/lucia-phase17-Integrated_Affective_Life_Evaluation/results/temp_run_store/TrackB_AblateCommPolicy_201/relationship.json` | Phase 17 | Cache / Temp / Build Output | 2.3 KB | **DO NOT COMMIT** | Exclude / Ignore | Ephemeral Phase 17 test run scratch store (mock model / temp relationship snapshot) |
| 20 | `docs/specs/lucia-phase17-Integrated_Affective_Life_Evaluation/results/temp_run_store/TrackB_AblateExprPolicy_201/model.gguf` | Phase 17 | Cache / Temp / Build Output | 25 B | **DO NOT COMMIT** | Exclude / Ignore | Ephemeral Phase 17 test run scratch store (mock model / temp relationship snapshot) |
| 21 | `docs/specs/lucia-phase17-Integrated_Affective_Life_Evaluation/results/temp_run_store/TrackB_AblateExprPolicy_201/relationship.json` | Phase 17 | Cache / Temp / Build Output | 2.3 KB | **DO NOT COMMIT** | Exclude / Ignore | Ephemeral Phase 17 test run scratch store (mock model / temp relationship snapshot) |
| 22 | `docs/specs/lucia-phase17-Integrated_Affective_Life_Evaluation/results/temp_run_store/TrackB_AblateKnowledge_201/model.gguf` | Phase 17 | Cache / Temp / Build Output | 25 B | **DO NOT COMMIT** | Exclude / Ignore | Ephemeral Phase 17 test run scratch store (mock model / temp relationship snapshot) |
| 23 | `docs/specs/lucia-phase17-Integrated_Affective_Life_Evaluation/results/temp_run_store/TrackB_AblateKnowledge_201/relationship.json` | Phase 17 | Cache / Temp / Build Output | 2.3 KB | **DO NOT COMMIT** | Exclude / Ignore | Ephemeral Phase 17 test run scratch store (mock model / temp relationship snapshot) |
| 24 | `docs/specs/lucia-phase17-Integrated_Affective_Life_Evaluation/results/temp_run_store/TrackB_AblateMemory_201/model.gguf` | Phase 17 | Cache / Temp / Build Output | 25 B | **DO NOT COMMIT** | Exclude / Ignore | Ephemeral Phase 17 test run scratch store (mock model / temp relationship snapshot) |
| 25 | `docs/specs/lucia-phase17-Integrated_Affective_Life_Evaluation/results/temp_run_store/TrackB_AblateMemory_201/relationship.json` | Phase 17 | Cache / Temp / Build Output | 2.3 KB | **DO NOT COMMIT** | Exclude / Ignore | Ephemeral Phase 17 test run scratch store (mock model / temp relationship snapshot) |
| 26 | `docs/specs/lucia-phase17-Integrated_Affective_Life_Evaluation/results/temp_run_store/TrackB_AblateRelUpdate_201/model.gguf` | Phase 17 | Cache / Temp / Build Output | 25 B | **DO NOT COMMIT** | Exclude / Ignore | Ephemeral Phase 17 test run scratch store (mock model / temp relationship snapshot) |
| 27 | `docs/specs/lucia-phase17-Integrated_Affective_Life_Evaluation/results/temp_run_store/TrackB_AblateRelationshipRead_201/model.gguf` | Phase 17 | Cache / Temp / Build Output | 25 B | **DO NOT COMMIT** | Exclude / Ignore | Ephemeral Phase 17 test run scratch store (mock model / temp relationship snapshot) |
| 28 | `docs/specs/lucia-phase17-Integrated_Affective_Life_Evaluation/results/temp_run_store/TrackB_AblateRelationshipRead_201/relationship.json` | Phase 17 | Cache / Temp / Build Output | 2.3 KB | **DO NOT COMMIT** | Exclude / Ignore | Ephemeral Phase 17 test run scratch store (mock model / temp relationship snapshot) |
| 29 | `docs/specs/lucia-phase17-Integrated_Affective_Life_Evaluation/results/temp_run_store/TrackB_FullSystem_201/model.gguf` | Phase 17 | Cache / Temp / Build Output | 25 B | **DO NOT COMMIT** | Exclude / Ignore | Ephemeral Phase 17 test run scratch store (mock model / temp relationship snapshot) |
| 30 | `docs/specs/lucia-phase17-Integrated_Affective_Life_Evaluation/results/temp_run_store/TrackB_FullSystem_201/relationship.json` | Phase 17 | Cache / Temp / Build Output | 2.3 KB | **DO NOT COMMIT** | Exclude / Ignore | Ephemeral Phase 17 test run scratch store (mock model / temp relationship snapshot) |
| 31 | `docs/specs/lucia-phase17-Integrated_Affective_Life_Evaluation/results/temp_run_store/TrackC_ConflictRepair_40_302/model.gguf` | Phase 17 | Cache / Temp / Build Output | 25 B | **DO NOT COMMIT** | Exclude / Ignore | Ephemeral Phase 17 test run scratch store (mock model / temp relationship snapshot) |
| 32 | `docs/specs/lucia-phase17-Integrated_Affective_Life_Evaluation/results/temp_run_store/TrackC_ConflictRepair_40_302/relationship.json` | Phase 17 | Cache / Temp / Build Output | 31.0 KB | **DO NOT COMMIT** | Exclude / Ignore | Ephemeral Phase 17 test run scratch store (mock model / temp relationship snapshot) |
| 33 | `docs/specs/lucia-phase17-Integrated_Affective_Life_Evaluation/results/temp_run_store/TrackC_Cooperation_30_301/model.gguf` | Phase 17 | Cache / Temp / Build Output | 25 B | **DO NOT COMMIT** | Exclude / Ignore | Ephemeral Phase 17 test run scratch store (mock model / temp relationship snapshot) |
| 34 | `docs/specs/lucia-phase17-Integrated_Affective_Life_Evaluation/results/temp_run_store/TrackC_Cooperation_30_301/relationship.json` | Phase 17 | Cache / Temp / Build Output | 23.1 KB | **DO NOT COMMIT** | Exclude / Ignore | Ephemeral Phase 17 test run scratch store (mock model / temp relationship snapshot) |
| 35 | `docs/specs/lucia-phase17-Integrated_Affective_Life_Evaluation/results/temp_run_store/TrackD_EmptyMemory_403/model.gguf` | Phase 17 | Cache / Temp / Build Output | 25 B | **DO NOT COMMIT** | Exclude / Ignore | Ephemeral Phase 17 test run scratch store (mock model / temp relationship snapshot) |
| 36 | `docs/specs/lucia-phase17-Integrated_Affective_Life_Evaluation/results/temp_run_store/TrackD_EmptyMemory_403/relationship.json` | Phase 17 | Cache / Temp / Build Output | 1.5 KB | **DO NOT COMMIT** | Exclude / Ignore | Ephemeral Phase 17 test run scratch store (mock model / temp relationship snapshot) |
| 37 | `docs/specs/lucia-phase17-Integrated_Affective_Life_Evaluation/results/temp_run_store/TrackD_IrrelevantMemory_402/model.gguf` | Phase 17 | Cache / Temp / Build Output | 25 B | **DO NOT COMMIT** | Exclude / Ignore | Ephemeral Phase 17 test run scratch store (mock model / temp relationship snapshot) |
| 38 | `docs/specs/lucia-phase17-Integrated_Affective_Life_Evaluation/results/temp_run_store/TrackD_IrrelevantMemory_402/relationship.json` | Phase 17 | Cache / Temp / Build Output | 1.5 KB | **DO NOT COMMIT** | Exclude / Ignore | Ephemeral Phase 17 test run scratch store (mock model / temp relationship snapshot) |
| 39 | `docs/specs/lucia-phase17-Integrated_Affective_Life_Evaluation/results/temp_run_store/TrackD_RelevantMemory_401/model.gguf` | Phase 17 | Cache / Temp / Build Output | 25 B | **DO NOT COMMIT** | Exclude / Ignore | Ephemeral Phase 17 test run scratch store (mock model / temp relationship snapshot) |
| 40 | `docs/specs/lucia-phase17-Integrated_Affective_Life_Evaluation/results/temp_run_store/TrackD_RelevantMemory_401/relationship.json` | Phase 17 | Cache / Temp / Build Output | 1.5 KB | **DO NOT COMMIT** | Exclude / Ignore | Ephemeral Phase 17 test run scratch store (mock model / temp relationship snapshot) |
| 41 | `docs/specs/lucia-phase17-Integrated_Affective_Life_Evaluation/results/temp_run_store/TrackF_BoundaryLayerAttacks_601/model.gguf` | Phase 17 | Cache / Temp / Build Output | 25 B | **DO NOT COMMIT** | Exclude / Ignore | Ephemeral Phase 17 test run scratch store (mock model / temp relationship snapshot) |
| 42 | `docs/specs/lucia-phase17-Integrated_Affective_Life_Evaluation/results/temp_run_store/TrackF_BoundaryLayerAttacks_601/relationship.json` | Phase 17 | Cache / Temp / Build Output | 4.4 KB | **DO NOT COMMIT** | Exclude / Ignore | Ephemeral Phase 17 test run scratch store (mock model / temp relationship snapshot) |
| 43 | `docs/specs/lucia-phase17-Integrated_Affective_Life_Evaluation/results/temp_run_store/TrackI_Replay_999/model.gguf` | Phase 17 | Cache / Temp / Build Output | 25 B | **DO NOT COMMIT** | Exclude / Ignore | Ephemeral Phase 17 test run scratch store (mock model / temp relationship snapshot) |
| 44 | `docs/specs/lucia-phase17-Integrated_Affective_Life_Evaluation/results/temp_run_store/TrackI_Replay_999/relationship.json` | Phase 17 | Cache / Temp / Build Output | 2.4 KB | **DO NOT COMMIT** | Exclude / Ignore | Ephemeral Phase 17 test run scratch store (mock model / temp relationship snapshot) |
| 45 | `docs/specs/lucia-phase17-Integrated_Affective_Life_Evaluation/results/temp_run_store/TrackK_StressRecovery_60_701/model.gguf` | Phase 17 | Cache / Temp / Build Output | 25 B | **DO NOT COMMIT** | Exclude / Ignore | Ephemeral Phase 17 test run scratch store (mock model / temp relationship snapshot) |
| 46 | `docs/specs/lucia-phase17-Integrated_Affective_Life_Evaluation/results/temp_run_store/TrackK_StressRecovery_60_701/relationship.json` | Phase 17 | Cache / Temp / Build Output | 39.2 KB | **DO NOT COMMIT** | Exclude / Ignore | Ephemeral Phase 17 test run scratch store (mock model / temp relationship snapshot) |
| 47 | `docs/specs/lucia-phase17-Integrated_Affective_Life_Evaluation/results/temp_run_store/rel_c3.json` | Phase 17 | Cache / Temp / Build Output | 21.8 KB | **DO NOT COMMIT** | Exclude / Ignore | Ephemeral Phase 17 test run scratch store (mock model / temp relationship snapshot) |
| 48 | `docs/specs/lucia-phase17-Integrated_Affective_Life_Evaluation/results/temp_run_store/session_concurrency_l/model.gguf` | Phase 17 | Cache / Temp / Build Output | 25 B | **DO NOT COMMIT** | Exclude / Ignore | Ephemeral Phase 17 test run scratch store (mock model / temp relationship snapshot) |
| 49 | `docs/specs/lucia-phase17-Integrated_Affective_Life_Evaluation/results/temp_run_store/session_persist_1/model.gguf` | Phase 17 | Cache / Temp / Build Output | 25 B | **DO NOT COMMIT** | Exclude / Ignore | Ephemeral Phase 17 test run scratch store (mock model / temp relationship snapshot) |
| 50 | `docs/specs/lucia-phase17-Integrated_Affective_Life_Evaluation/results/temp_run_store/session_persist_1/relationship.json` | Phase 17 | Cache / Temp / Build Output | 1.0 KB | **DO NOT COMMIT** | Exclude / Ignore | Ephemeral Phase 17 test run scratch store (mock model / temp relationship snapshot) |
| 51 | `docs/specs/lucia-phase17-Integrated_Affective_Life_Evaluation/results/temp_run_store/session_persist_2/model.gguf` | Phase 17 | Cache / Temp / Build Output | 25 B | **DO NOT COMMIT** | Exclude / Ignore | Ephemeral Phase 17 test run scratch store (mock model / temp relationship snapshot) |
| 52 | `docs/specs/lucia-phase18-Human_Longitudinal_Validation/HUMAN_EVALUATION_PROTOCOL.md` | Phase 18 | Documentation / Spec / ADR | 10.4 KB | **KEEP** | Git Commit (Commit 2) | Authoritative Phase 18 specification, protocol, or report |
| 53 | `docs/specs/lucia-phase18-Human_Longitudinal_Validation/PHASE_18_EVALUATION_REPORT.md` | Phase 18 | Documentation / Spec / ADR | 33.7 KB | **KEEP** | Git Commit (Commit 2) | Authoritative Phase 18 specification, protocol, or report |
| 54 | `docs/specs/lucia-phase18-Human_Longitudinal_Validation/PHASE_18_LONGITUDINAL_AUDIOVISUAL_REGENERATION_REPORT.md` | Phase 18 | Documentation / Spec / ADR | 19.1 KB | **KEEP** | Git Commit (Commit 2) | Authoritative Phase 18 specification, protocol, or report |
| 55 | `docs/specs/lucia-phase18-Human_Longitudinal_Validation/PHASE_18_RVC_AUDIO_QUALITY_DIAGNOSTIC.md` | Phase 18 | Documentation / Spec / ADR | 24.5 KB | **KEEP** | Git Commit (Commit 3) | RVC neural voice verification and diagnostic report |
| 56 | `docs/specs/lucia-phase18-Human_Longitudinal_Validation/PHASE_18_RVC_AUDIO_QUALITY_FINAL_VERIFICATION.md` | Phase 18 | Documentation / Spec / ADR | 19.1 KB | **KEEP** | Git Commit (Commit 3) | RVC neural voice verification and diagnostic report |
| 57 | `docs/specs/lucia-phase18-Human_Longitudinal_Validation/PHASE_18_SPECIFICATION.md` | Phase 18 | Documentation / Spec / ADR | 11.2 KB | **KEEP** | Git Commit (Commit 2) | Authoritative Phase 18 specification, protocol, or report |
| 58 | `docs/specs/lucia-phase18-Human_Longitudinal_Validation/PHASE_18_VOICE_RUNTIME_VERIFICATION_REPORT.md` | Phase 18 | Documentation / Spec / ADR | 12.7 KB | **KEEP** | Git Commit (Commit 3) | RVC neural voice verification and diagnostic report |
| 59 | `docs/specs/lucia-phase18-Human_Longitudinal_Validation/results/audiovisual_manifest.json` | Phase 18 | Manifest / Provenance / Reproducibility Data | 35.9 KB | **KEEP** | Git Commit (Commit 2) | Authoritative Phase 18 matrix, manifest, or schema |
| 60 | `docs/specs/lucia-phase18-Human_Longitudinal_Validation/results/human_evaluation_schema.json` | Phase 18 | Manifest / Provenance / Reproducibility Data | 2.7 KB | **KEEP** | Git Commit (Commit 2) | Authoritative Phase 18 matrix, manifest, or schema |
| 61 | `docs/specs/lucia-phase18-Human_Longitudinal_Validation/results/phase18_evaluation_matrix.json` | Phase 18 | Manifest / Provenance / Reproducibility Data | 474.2 KB | **KEEP** | Git Commit (Commit 2) | Authoritative Phase 18 matrix, manifest, or schema |
| 62 | `evaluation_artifacts/phase18/audio/Scenario_A_turn1.wav` | Phase 18 | Generated Audiovisual Artifacts | 305.7 KB | **REVIEW** | Git Commit (Commit 4) or LFS/Release | Official Phase 18 spoken audio WAV evidence |
| 63 | `evaluation_artifacts/phase18/audio/Scenario_B_turn2.wav` | Phase 18 | Generated Audiovisual Artifacts | 333.8 KB | **REVIEW** | Git Commit (Commit 4) or LFS/Release | Official Phase 18 spoken audio WAV evidence |
| 64 | `evaluation_artifacts/phase18/audio/Scenario_C_turn3.wav` | Phase 18 | Generated Audiovisual Artifacts | 252.2 KB | **REVIEW** | Git Commit (Commit 4) or LFS/Release | Official Phase 18 spoken audio WAV evidence |
| 65 | `evaluation_artifacts/phase18/audio/Scenario_D_turn16.wav` | Phase 18 | Generated Audiovisual Artifacts | 173.5 KB | **REVIEW** | Git Commit (Commit 4) or LFS/Release | Official Phase 18 spoken audio WAV evidence |
| 66 | `evaluation_artifacts/phase18/audio/Scenario_E_Session2_turn1.wav` | Phase 18 | Generated Audiovisual Artifacts | 324.4 KB | **REVIEW** | Git Commit (Commit 4) or LFS/Release | Official Phase 18 spoken audio WAV evidence |
| 67 | `evaluation_artifacts/phase18/audio/Scenario_F_Reunion_turn1.wav` | Phase 18 | Generated Audiovisual Artifacts | 348.8 KB | **REVIEW** | Git Commit (Commit 4) or LFS/Release | Official Phase 18 spoken audio WAV evidence |
| 68 | `evaluation_artifacts/phase18/audio/Scenario_G_turn4.wav` | Phase 18 | Generated Audiovisual Artifacts | 261.6 KB | **REVIEW** | Git Commit (Commit 4) or LFS/Release | Official Phase 18 spoken audio WAV evidence |
| 69 | `evaluation_artifacts/phase18/manifests/audiovisual_manifest.json` | Phase 18 | Cache / Temp / Build Output | 35.9 KB | **DO NOT COMMIT** | Exclude / Ignore | Exact duplicate of docs/specs/.../results/audiovisual_manifest.json |
| 70 | `evaluation_artifacts/phase18/telemetry/Scenario_A_session_A_telemetry.json` | Phase 18 | Manifest / Provenance / Reproducibility Data | 43.6 KB | **REVIEW** | Git Commit (Commit 4) | Official Phase 18 longitudinal session telemetry JSON evidence |
| 71 | `evaluation_artifacts/phase18/telemetry/Scenario_B_session_B_telemetry.json` | Phase 18 | Manifest / Provenance / Reproducibility Data | 64.5 KB | **REVIEW** | Git Commit (Commit 4) | Official Phase 18 longitudinal session telemetry JSON evidence |
| 72 | `evaluation_artifacts/phase18/telemetry/Scenario_C_session_C_telemetry.json` | Phase 18 | Manifest / Provenance / Reproducibility Data | 43.6 KB | **REVIEW** | Git Commit (Commit 4) | Official Phase 18 longitudinal session telemetry JSON evidence |
| 73 | `evaluation_artifacts/phase18/telemetry/Scenario_D_session_D_telemetry.json` | Phase 18 | Manifest / Provenance / Reproducibility Data | 84.6 KB | **REVIEW** | Git Commit (Commit 4) | Official Phase 18 longitudinal session telemetry JSON evidence |
| 74 | `evaluation_artifacts/phase18/telemetry/Scenario_E_Session1_session_E_s1_telemetry.json` | Phase 18 | Manifest / Provenance / Reproducibility Data | 18.4 KB | **REVIEW** | Git Commit (Commit 4) | Official Phase 18 longitudinal session telemetry JSON evidence |
| 75 | `evaluation_artifacts/phase18/telemetry/Scenario_E_Session2_session_E_s2_telemetry.json` | Phase 18 | Manifest / Provenance / Reproducibility Data | 14.1 KB | **REVIEW** | Git Commit (Commit 4) | Official Phase 18 longitudinal session telemetry JSON evidence |
| 76 | `evaluation_artifacts/phase18/telemetry/Scenario_F_PreAbsence_session_F_s1_telemetry.json` | Phase 18 | Manifest / Provenance / Reproducibility Data | 13.6 KB | **REVIEW** | Git Commit (Commit 4) | Official Phase 18 longitudinal session telemetry JSON evidence |
| 77 | `evaluation_artifacts/phase18/telemetry/Scenario_F_Reunion_session_F_reunion_telemetry.json` | Phase 18 | Manifest / Provenance / Reproducibility Data | 13.8 KB | **REVIEW** | Git Commit (Commit 4) | Official Phase 18 longitudinal session telemetry JSON evidence |
| 78 | `evaluation_artifacts/phase18/telemetry/Scenario_G_session_G_telemetry.json` | Phase 18 | Manifest / Provenance / Reproducibility Data | 76.2 KB | **REVIEW** | Git Commit (Commit 4) | Official Phase 18 longitudinal session telemetry JSON evidence |
| 79 | `evaluation_artifacts/phase18/telemetry/Scenario_H_session_H_telemetry.json` | Phase 18 | Manifest / Provenance / Reproducibility Data | 43.8 KB | **REVIEW** | Git Commit (Commit 4) | Official Phase 18 longitudinal session telemetry JSON evidence |
| 80 | `evaluation_artifacts/phase18/temp_harness/session_A/model.gguf` | Phase 18 | Cache / Temp / Build Output | 15 B | **DO NOT COMMIT** | Exclude / Ignore | Ephemeral Phase 18 test run scratch store (mock model / temp relationship snapshot) |
| 81 | `evaluation_artifacts/phase18/temp_harness/session_A/relationship.json` | Phase 18 | Cache / Temp / Build Output | 8.1 KB | **DO NOT COMMIT** | Exclude / Ignore | Ephemeral Phase 18 test run scratch store (mock model / temp relationship snapshot) |
| 82 | `evaluation_artifacts/phase18/temp_harness/session_B/model.gguf` | Phase 18 | Cache / Temp / Build Output | 15 B | **DO NOT COMMIT** | Exclude / Ignore | Ephemeral Phase 18 test run scratch store (mock model / temp relationship snapshot) |
| 83 | `evaluation_artifacts/phase18/temp_harness/session_B/relationship.json` | Phase 18 | Cache / Temp / Build Output | 10.9 KB | **DO NOT COMMIT** | Exclude / Ignore | Ephemeral Phase 18 test run scratch store (mock model / temp relationship snapshot) |
| 84 | `evaluation_artifacts/phase18/temp_harness/session_C/model.gguf` | Phase 18 | Cache / Temp / Build Output | 15 B | **DO NOT COMMIT** | Exclude / Ignore | Ephemeral Phase 18 test run scratch store (mock model / temp relationship snapshot) |
| 85 | `evaluation_artifacts/phase18/temp_harness/session_C/relationship.json` | Phase 18 | Cache / Temp / Build Output | 8.1 KB | **DO NOT COMMIT** | Exclude / Ignore | Ephemeral Phase 18 test run scratch store (mock model / temp relationship snapshot) |
| 86 | `evaluation_artifacts/phase18/temp_harness/session_D/model.gguf` | Phase 18 | Cache / Temp / Build Output | 15 B | **DO NOT COMMIT** | Exclude / Ignore | Ephemeral Phase 18 test run scratch store (mock model / temp relationship snapshot) |
| 87 | `evaluation_artifacts/phase18/temp_harness/session_D/relationship.json` | Phase 18 | Cache / Temp / Build Output | 14.1 KB | **DO NOT COMMIT** | Exclude / Ignore | Ephemeral Phase 18 test run scratch store (mock model / temp relationship snapshot) |
| 88 | `evaluation_artifacts/phase18/temp_harness/session_E_s1/model.gguf` | Phase 18 | Cache / Temp / Build Output | 15 B | **DO NOT COMMIT** | Exclude / Ignore | Ephemeral Phase 18 test run scratch store (mock model / temp relationship snapshot) |
| 89 | `evaluation_artifacts/phase18/temp_harness/session_E_s1/relationship.json` | Phase 18 | Cache / Temp / Build Output | 4.2 KB | **DO NOT COMMIT** | Exclude / Ignore | Ephemeral Phase 18 test run scratch store (mock model / temp relationship snapshot) |
| 90 | `evaluation_artifacts/phase18/temp_harness/session_E_s2/model.gguf` | Phase 18 | Cache / Temp / Build Output | 15 B | **DO NOT COMMIT** | Exclude / Ignore | Ephemeral Phase 18 test run scratch store (mock model / temp relationship snapshot) |
| 91 | `evaluation_artifacts/phase18/temp_harness/session_E_s2/relationship.json` | Phase 18 | Cache / Temp / Build Output | 2.6 KB | **DO NOT COMMIT** | Exclude / Ignore | Ephemeral Phase 18 test run scratch store (mock model / temp relationship snapshot) |
| 92 | `evaluation_artifacts/phase18/temp_harness/session_F_reunion/model.gguf` | Phase 18 | Cache / Temp / Build Output | 15 B | **DO NOT COMMIT** | Exclude / Ignore | Ephemeral Phase 18 test run scratch store (mock model / temp relationship snapshot) |
| 93 | `evaluation_artifacts/phase18/temp_harness/session_F_reunion/relationship.json` | Phase 18 | Cache / Temp / Build Output | 2.3 KB | **DO NOT COMMIT** | Exclude / Ignore | Ephemeral Phase 18 test run scratch store (mock model / temp relationship snapshot) |
| 94 | `evaluation_artifacts/phase18/temp_harness/session_F_s1/model.gguf` | Phase 18 | Cache / Temp / Build Output | 15 B | **DO NOT COMMIT** | Exclude / Ignore | Ephemeral Phase 18 test run scratch store (mock model / temp relationship snapshot) |
| 95 | `evaluation_artifacts/phase18/temp_harness/session_F_s1/relationship.json` | Phase 18 | Cache / Temp / Build Output | 3.0 KB | **DO NOT COMMIT** | Exclude / Ignore | Ephemeral Phase 18 test run scratch store (mock model / temp relationship snapshot) |
| 96 | `evaluation_artifacts/phase18/temp_harness/session_G/model.gguf` | Phase 18 | Cache / Temp / Build Output | 15 B | **DO NOT COMMIT** | Exclude / Ignore | Ephemeral Phase 18 test run scratch store (mock model / temp relationship snapshot) |
| 97 | `evaluation_artifacts/phase18/temp_harness/session_G/relationship.json` | Phase 18 | Cache / Temp / Build Output | 12.7 KB | **DO NOT COMMIT** | Exclude / Ignore | Ephemeral Phase 18 test run scratch store (mock model / temp relationship snapshot) |
| 98 | `evaluation_artifacts/phase18/temp_harness/session_H/model.gguf` | Phase 18 | Cache / Temp / Build Output | 15 B | **DO NOT COMMIT** | Exclude / Ignore | Ephemeral Phase 18 test run scratch store (mock model / temp relationship snapshot) |
| 99 | `evaluation_artifacts/phase18/temp_harness/session_H/relationship.json` | Phase 18 | Cache / Temp / Build Output | 8.1 KB | **DO NOT COMMIT** | Exclude / Ignore | Ephemeral Phase 18 test run scratch store (mock model / temp relationship snapshot) |
| 100 | `evaluation_artifacts/phase18/temp_harness/session_boundary_probes/model.gguf` | Phase 18 | Cache / Temp / Build Output | 15 B | **DO NOT COMMIT** | Exclude / Ignore | Ephemeral Phase 18 test run scratch store (mock model / temp relationship snapshot) |
| 101 | `evaluation_artifacts/phase18/video/Scenario_A_turn1.mp4` | Phase 18 | Generated Audiovisual Artifacts | 214.4 KB | **REVIEW** | Git Commit (Commit 4) or LFS/Release | Official Phase 18 Columbina sprite video MP4 evidence |
| 102 | `evaluation_artifacts/phase18/video/Scenario_B_turn2.mp4` | Phase 18 | Generated Audiovisual Artifacts | 228.6 KB | **REVIEW** | Git Commit (Commit 4) or LFS/Release | Official Phase 18 Columbina sprite video MP4 evidence |
| 103 | `evaluation_artifacts/phase18/video/Scenario_C_turn3.mp4` | Phase 18 | Generated Audiovisual Artifacts | 183.2 KB | **REVIEW** | Git Commit (Commit 4) or LFS/Release | Official Phase 18 Columbina sprite video MP4 evidence |
| 104 | `evaluation_artifacts/phase18/video/Scenario_D_turn16.mp4` | Phase 18 | Generated Audiovisual Artifacts | 137.4 KB | **REVIEW** | Git Commit (Commit 4) or LFS/Release | Official Phase 18 Columbina sprite video MP4 evidence |
| 105 | `evaluation_artifacts/phase18/video/Scenario_E_Session2_turn1.mp4` | Phase 18 | Generated Audiovisual Artifacts | 225.3 KB | **REVIEW** | Git Commit (Commit 4) or LFS/Release | Official Phase 18 Columbina sprite video MP4 evidence |
| 106 | `evaluation_artifacts/phase18/video/Scenario_F_Reunion_turn1.mp4` | Phase 18 | Generated Audiovisual Artifacts | 238.5 KB | **REVIEW** | Git Commit (Commit 4) or LFS/Release | Official Phase 18 Columbina sprite video MP4 evidence |
| 107 | `evaluation_artifacts/phase18/video/Scenario_G_turn4.mp4` | Phase 18 | Generated Audiovisual Artifacts | 188.7 KB | **REVIEW** | Git Commit (Commit 4) or LFS/Release | Official Phase 18 Columbina sprite video MP4 evidence |
| 108 | `src/core/voice/rvc_modules/__init__.py` | Phase 18 | Production Source | 0 B | **KEEP** | Git Commit (Commit 3) | Core on-device RVC v2 neural voice synthesis pipeline and tensor modules |
| 109 | `src/core/voice/rvc_modules/attentions.py` | Phase 18 | Production Source | 15.6 KB | **KEEP** | Git Commit (Commit 3) | Core on-device RVC v2 neural voice synthesis pipeline and tensor modules |
| 110 | `src/core/voice/rvc_modules/commons.py` | Phase 18 | Production Source | 5.3 KB | **KEEP** | Git Commit (Commit 3) | Core on-device RVC v2 neural voice synthesis pipeline and tensor modules |
| 111 | `src/core/voice/rvc_modules/models.py` | Phase 18 | Production Source | 36.0 KB | **KEEP** | Git Commit (Commit 3) | Core on-device RVC v2 neural voice synthesis pipeline and tensor modules |
| 112 | `src/core/voice/rvc_modules/modules.py` | Phase 18 | Production Source | 17.3 KB | **KEEP** | Git Commit (Commit 3) | Core on-device RVC v2 neural voice synthesis pipeline and tensor modules |
| 113 | `src/core/voice/rvc_modules/transforms.py` | Phase 18 | Production Source | 7.3 KB | **KEEP** | Git Commit (Commit 3) | Core on-device RVC v2 neural voice synthesis pipeline and tensor modules |
| 114 | `src/core/voice/rvc_pipeline.py` | Phase 18 | Production Source | 17.0 KB | **KEEP** | Git Commit (Commit 3) | Core on-device RVC v2 neural voice synthesis pipeline and tensor modules |
| 115 | `src/core/voice/voice_engine.py` | Phase 18 | Production Source | 11.3 KB | **KEEP** | Git Commit (Commit 3) | Core on-device RVC v2 neural voice synthesis pipeline and tensor modules |
| 116 | `tests/evaluation/__init__.py` | Phase 17 | Test / Eval Infrastructure | 82 B | **KEEP** | Git Commit (Commit 1) | Automated Phase 17 evaluation test suite, harness, scenarios, and runner |
| 117 | `tests/evaluation/harness.py` | Phase 17 | Test / Eval Infrastructure | 32.7 KB | **KEEP** | Git Commit (Commit 1) | Automated Phase 17 evaluation test suite, harness, scenarios, and runner |
| 118 | `tests/evaluation/run_evaluations.py` | Phase 17 | Test / Eval Infrastructure | 20.0 KB | **KEEP** | Git Commit (Commit 1) | Automated Phase 17 evaluation test suite, harness, scenarios, and runner |
| 119 | `tests/evaluation/scenarios.py` | Phase 17 | Test / Eval Infrastructure | 5.0 KB | **KEEP** | Git Commit (Commit 1) | Automated Phase 17 evaluation test suite, harness, scenarios, and runner |
| 120 | `tests/evaluation/test_phase17_evaluation.py` | Phase 17 | Test / Eval Infrastructure | 16.3 KB | **KEEP** | Git Commit (Commit 1) | Automated Phase 17 evaluation test suite, harness, scenarios, and runner |
| 121 | `tests/evaluation_phase18/__init__.py` | Phase 18 | Test / Eval Infrastructure | 118 B | **KEEP** | Git Commit (Commit 2) | Phase 18 longitudinal evaluation harness, scenarios, telemetry, and runner |
| 122 | `tests/evaluation_phase18/audiovisual.py` | Phase 18 | Test / Eval Infrastructure | 17.6 KB | **KEEP** | Git Commit (Commit 2) | Phase 18 longitudinal evaluation harness, scenarios, telemetry, and runner |
| 123 | `tests/evaluation_phase18/harness.py` | Phase 18 | Test / Eval Infrastructure | 26.7 KB | **KEEP** | Git Commit (Commit 2) | Phase 18 longitudinal evaluation harness, scenarios, telemetry, and runner |
| 124 | `tests/evaluation_phase18/human_protocol.py` | Phase 18 | Test / Eval Infrastructure | 9.4 KB | **KEEP** | Git Commit (Commit 2) | Phase 18 longitudinal evaluation harness, scenarios, telemetry, and runner |
| 125 | `tests/evaluation_phase18/runner.py` | Phase 18 | Test / Eval Infrastructure | 19.6 KB | **KEEP** | Git Commit (Commit 2) | Phase 18 longitudinal evaluation harness, scenarios, telemetry, and runner |
| 126 | `tests/evaluation_phase18/scenarios.py` | Phase 18 | Test / Eval Infrastructure | 24.2 KB | **KEEP** | Git Commit (Commit 2) | Phase 18 longitudinal evaluation harness, scenarios, telemetry, and runner |
| 127 | `tests/evaluation_phase18/telemetry.py` | Phase 18 | Test / Eval Infrastructure | 5.5 KB | **KEEP** | Git Commit (Commit 2) | Phase 18 longitudinal evaluation harness, scenarios, telemetry, and runner |
| 128 | `tests/evaluation_phase18/test_phase18_validation.py` | Phase 18 | Test / Eval Infrastructure | 14.3 KB | **KEEP** | Git Commit (Commit 2) | Phase 18 longitudinal evaluation harness, scenarios, telemetry, and runner |
| 129 | `tests/evaluation_phase18/test_rvc_runtime.py` | Phase 18 | Test / Eval Infrastructure | 12.1 KB | **KEEP** | Git Commit (Commit 3) | Direct unit & regression test suite for RVC v2 runtime |

---

## 3. Files Definitely Safe to Commit

There are **37 files** that are definitely safe to commit. These files comprise production source code, reusable test/evaluation suites, authoritative specifications, verification reports, and reproducibility matrices.

### A. Production Source (8 files — Commit 3)
- [`src/core/voice/rvc_modules/__init__.py`](file:///src/core/voice/rvc_modules/__init__.py) (0 B) — Core on-device RVC v2 neural voice synthesis pipeline and tensor modules
- [`src/core/voice/rvc_modules/attentions.py`](file:///src/core/voice/rvc_modules/attentions.py) (15.6 KB) — Core on-device RVC v2 neural voice synthesis pipeline and tensor modules
- [`src/core/voice/rvc_modules/commons.py`](file:///src/core/voice/rvc_modules/commons.py) (5.3 KB) — Core on-device RVC v2 neural voice synthesis pipeline and tensor modules
- [`src/core/voice/rvc_modules/models.py`](file:///src/core/voice/rvc_modules/models.py) (36.0 KB) — Core on-device RVC v2 neural voice synthesis pipeline and tensor modules
- [`src/core/voice/rvc_modules/modules.py`](file:///src/core/voice/rvc_modules/modules.py) (17.3 KB) — Core on-device RVC v2 neural voice synthesis pipeline and tensor modules
- [`src/core/voice/rvc_modules/transforms.py`](file:///src/core/voice/rvc_modules/transforms.py) (7.3 KB) — Core on-device RVC v2 neural voice synthesis pipeline and tensor modules
- [`src/core/voice/rvc_pipeline.py`](file:///src/core/voice/rvc_pipeline.py) (17.0 KB) — Core on-device RVC v2 neural voice synthesis pipeline and tensor modules
- [`src/core/voice/voice_engine.py`](file:///src/core/voice/voice_engine.py) (11.3 KB) — Core on-device RVC v2 neural voice synthesis pipeline and tensor modules

### B. Phase 17 Evaluation Infrastructure & Documentation (8 files — Commit 1)
- [`docs/specs/lucia-phase17-Integrated_Affective_Life_Evaluation/PHASE_17_EVALUATION_REPORT.md`](file:///docs/specs/lucia-phase17-Integrated_Affective_Life_Evaluation/PHASE_17_EVALUATION_REPORT.md) (27.3 KB) — Authoritative Phase 17 specification and evaluation report
- [`docs/specs/lucia-phase17-Integrated_Affective_Life_Evaluation/PHASE_17_SPECIFICATION.md`](file:///docs/specs/lucia-phase17-Integrated_Affective_Life_Evaluation/PHASE_17_SPECIFICATION.md) (12.7 KB) — Authoritative Phase 17 specification and evaluation report
- [`docs/specs/lucia-phase17-Integrated_Affective_Life_Evaluation/results/phase17_evaluation_matrix.json`](file:///docs/specs/lucia-phase17-Integrated_Affective_Life_Evaluation/results/phase17_evaluation_matrix.json) (1.50 MB) — Authoritative Phase 17 evaluation matrix data
- [`tests/evaluation/__init__.py`](file:///tests/evaluation/__init__.py) (82 B) — Automated Phase 17 evaluation test suite, harness, scenarios, and runner
- [`tests/evaluation/harness.py`](file:///tests/evaluation/harness.py) (32.7 KB) — Automated Phase 17 evaluation test suite, harness, scenarios, and runner
- [`tests/evaluation/run_evaluations.py`](file:///tests/evaluation/run_evaluations.py) (20.0 KB) — Automated Phase 17 evaluation test suite, harness, scenarios, and runner
- [`tests/evaluation/scenarios.py`](file:///tests/evaluation/scenarios.py) (5.0 KB) — Automated Phase 17 evaluation test suite, harness, scenarios, and runner
- [`tests/evaluation/test_phase17_evaluation.py`](file:///tests/evaluation/test_phase17_evaluation.py) (16.3 KB) — Automated Phase 17 evaluation test suite, harness, scenarios, and runner

### C. Phase 18 Longitudinal Infrastructure & Specifications (9 files — Commit 2)
- [`docs/specs/lucia-phase18-Human_Longitudinal_Validation/HUMAN_EVALUATION_PROTOCOL.md`](file:///docs/specs/lucia-phase18-Human_Longitudinal_Validation/HUMAN_EVALUATION_PROTOCOL.md) (10.4 KB) — Authoritative Phase 18 specification, protocol, or report
- [`docs/specs/lucia-phase18-Human_Longitudinal_Validation/PHASE_18_EVALUATION_REPORT.md`](file:///docs/specs/lucia-phase18-Human_Longitudinal_Validation/PHASE_18_EVALUATION_REPORT.md) (33.7 KB) — Authoritative Phase 18 specification, protocol, or report
- [`docs/specs/lucia-phase18-Human_Longitudinal_Validation/PHASE_18_LONGITUDINAL_AUDIOVISUAL_REGENERATION_REPORT.md`](file:///docs/specs/lucia-phase18-Human_Longitudinal_Validation/PHASE_18_LONGITUDINAL_AUDIOVISUAL_REGENERATION_REPORT.md) (19.1 KB) — Authoritative Phase 18 specification, protocol, or report
- [`docs/specs/lucia-phase18-Human_Longitudinal_Validation/PHASE_18_SPECIFICATION.md`](file:///docs/specs/lucia-phase18-Human_Longitudinal_Validation/PHASE_18_SPECIFICATION.md) (11.2 KB) — Authoritative Phase 18 specification, protocol, or report
- [`docs/specs/lucia-phase18-Human_Longitudinal_Validation/results/audiovisual_manifest.json`](file:///docs/specs/lucia-phase18-Human_Longitudinal_Validation/results/audiovisual_manifest.json) (35.9 KB) — Authoritative Phase 18 matrix, manifest, or schema
- [`docs/specs/lucia-phase18-Human_Longitudinal_Validation/results/human_evaluation_schema.json`](file:///docs/specs/lucia-phase18-Human_Longitudinal_Validation/results/human_evaluation_schema.json) (2.7 KB) — Authoritative Phase 18 matrix, manifest, or schema
- [`docs/specs/lucia-phase18-Human_Longitudinal_Validation/results/phase18_evaluation_matrix.json`](file:///docs/specs/lucia-phase18-Human_Longitudinal_Validation/results/phase18_evaluation_matrix.json) (474.2 KB) — Authoritative Phase 18 matrix, manifest, or schema
- [`tests/evaluation_phase18/__init__.py`](file:///tests/evaluation_phase18/__init__.py) (118 B) — Phase 18 longitudinal evaluation harness, scenarios, telemetry, and runner
- [`tests/evaluation_phase18/audiovisual.py`](file:///tests/evaluation_phase18/audiovisual.py) (17.6 KB) — Phase 18 longitudinal evaluation harness, scenarios, telemetry, and runner
- [`tests/evaluation_phase18/harness.py`](file:///tests/evaluation_phase18/harness.py) (26.7 KB) — Phase 18 longitudinal evaluation harness, scenarios, telemetry, and runner
- [`tests/evaluation_phase18/human_protocol.py`](file:///tests/evaluation_phase18/human_protocol.py) (9.4 KB) — Phase 18 longitudinal evaluation harness, scenarios, telemetry, and runner
- [`tests/evaluation_phase18/runner.py`](file:///tests/evaluation_phase18/runner.py) (19.6 KB) — Phase 18 longitudinal evaluation harness, scenarios, telemetry, and runner
- [`tests/evaluation_phase18/scenarios.py`](file:///tests/evaluation_phase18/scenarios.py) (24.2 KB) — Phase 18 longitudinal evaluation harness, scenarios, telemetry, and runner
- [`tests/evaluation_phase18/telemetry.py`](file:///tests/evaluation_phase18/telemetry.py) (5.5 KB) — Phase 18 longitudinal evaluation harness, scenarios, telemetry, and runner
- [`tests/evaluation_phase18/test_phase18_validation.py`](file:///tests/evaluation_phase18/test_phase18_validation.py) (14.3 KB) — Phase 18 longitudinal evaluation harness, scenarios, telemetry, and runner

### D. Phase 18 Voice Runtime Tests & Diagnostic Reports (4 files — Commit 3)
- [`docs/specs/lucia-phase18-Human_Longitudinal_Validation/PHASE_18_RVC_AUDIO_QUALITY_DIAGNOSTIC.md`](file:///docs/specs/lucia-phase18-Human_Longitudinal_Validation/PHASE_18_RVC_AUDIO_QUALITY_DIAGNOSTIC.md) (24.5 KB) — RVC neural voice verification and diagnostic report
- [`docs/specs/lucia-phase18-Human_Longitudinal_Validation/PHASE_18_RVC_AUDIO_QUALITY_FINAL_VERIFICATION.md`](file:///docs/specs/lucia-phase18-Human_Longitudinal_Validation/PHASE_18_RVC_AUDIO_QUALITY_FINAL_VERIFICATION.md) (19.1 KB) — RVC neural voice verification and diagnostic report
- [`docs/specs/lucia-phase18-Human_Longitudinal_Validation/PHASE_18_VOICE_RUNTIME_VERIFICATION_REPORT.md`](file:///docs/specs/lucia-phase18-Human_Longitudinal_Validation/PHASE_18_VOICE_RUNTIME_VERIFICATION_REPORT.md) (12.7 KB) — RVC neural voice verification and diagnostic report
- [`tests/evaluation_phase18/test_rvc_runtime.py`](file:///tests/evaluation_phase18/test_rvc_runtime.py) (12.1 KB) — Direct unit & regression test suite for RVC v2 runtime

### E. Root Architectural Documentation (2 files — Commit 5)
- [`docs/CURRENT_STATUS.md`](file:///docs/CURRENT_STATUS.md) (38.1 KB) — System architecture documentation index & live operational status tracking
- [`docs/DOCUMENTATION_INDEX.md`](file:///docs/DOCUMENTATION_INDEX.md) (23.7 KB) — System architecture documentation index & live operational status tracking

---

## 4. Files That Should NOT Be Committed

There are **68 files** that MUST NOT be committed to the repository:

### A. Ephemeral Phase 17 Test Run Scratch Store (46 files)
Located in `docs/specs/lucia-phase17-Integrated_Affective_Life_Evaluation/results/temp_run_store/`.
- **24 mock model files** (`model.gguf`, 25 bytes each): temporary dummy files generated by `run_evaluations.py` to isolate model paths during simulation.
- **22 relationship state dumps** (`relationship.json`, 4 KB – 40 KB each): ephemeral scenario relationship snapshots saved to isolate test runs from production `data/`.
- **Reason to Exclude:** Purely disposable runtime residues. Committing them would permanently pollute the repository tree with scratch files.

### B. Ephemeral Phase 18 Test Harness Scratch Store (21 files)
Located in `evaluation_artifacts/phase18/temp_harness/`.
- **11 mock model files** (`model.gguf`, 15 bytes each): temporary mock model stubs created by `tests/evaluation_phase18/harness.py`.
- **10 relationship state dumps** (`relationship.json`, 4 KB – 15 KB each): temporary session state snapshots created to protect `data/profile.json`.
- **Reason to Exclude:** Purely disposable runtime residues generated during automated scenario validation.

### C. Duplicate Manifest (1 file)
- `evaluation_artifacts/phase18/manifests/audiovisual_manifest.json` (36.7 KB)
- **Reason to Exclude:** Bit-exact duplicate (SHA-256: `2b7f12f6...`) of the authoritative manifest at `docs/specs/lucia-phase18-Human_Longitudinal_Validation/results/audiovisual_manifest.json`.

---

## 5. Files Requiring Review

There are **24 files** requiring review (Total size: 3.74 MB):

These 24 files represent the **official longitudinal audiovisual and telemetry research evidence** generated during Phase 18 validation across Scenarios A through H:

### A. Spoken Audio Evidence (7 files — 2.05 MB)
- [`evaluation_artifacts/phase18/audio/Scenario_A_turn1.wav`](file:///evaluation_artifacts/phase18/audio/Scenario_A_turn1.wav) (305.7 KB)
- [`evaluation_artifacts/phase18/audio/Scenario_B_turn2.wav`](file:///evaluation_artifacts/phase18/audio/Scenario_B_turn2.wav) (333.8 KB)
- [`evaluation_artifacts/phase18/audio/Scenario_C_turn3.wav`](file:///evaluation_artifacts/phase18/audio/Scenario_C_turn3.wav) (252.2 KB)
- [`evaluation_artifacts/phase18/audio/Scenario_D_turn16.wav`](file:///evaluation_artifacts/phase18/audio/Scenario_D_turn16.wav) (173.5 KB)
- [`evaluation_artifacts/phase18/audio/Scenario_E_Session2_turn1.wav`](file:///evaluation_artifacts/phase18/audio/Scenario_E_Session2_turn1.wav) (324.4 KB)
- [`evaluation_artifacts/phase18/audio/Scenario_F_Reunion_turn1.wav`](file:///evaluation_artifacts/phase18/audio/Scenario_F_Reunion_turn1.wav) (348.8 KB)
- [`evaluation_artifacts/phase18/audio/Scenario_G_turn4.wav`](file:///evaluation_artifacts/phase18/audio/Scenario_G_turn4.wav) (261.6 KB)

### B. Columbina Sprite Video Evidence (7 files — 1.45 MB)
- [`evaluation_artifacts/phase18/video/Scenario_A_turn1.mp4`](file:///evaluation_artifacts/phase18/video/Scenario_A_turn1.mp4) (214.4 KB)
- [`evaluation_artifacts/phase18/video/Scenario_B_turn2.mp4`](file:///evaluation_artifacts/phase18/video/Scenario_B_turn2.mp4) (228.6 KB)
- [`evaluation_artifacts/phase18/video/Scenario_C_turn3.mp4`](file:///evaluation_artifacts/phase18/video/Scenario_C_turn3.mp4) (183.2 KB)
- [`evaluation_artifacts/phase18/video/Scenario_D_turn16.mp4`](file:///evaluation_artifacts/phase18/video/Scenario_D_turn16.mp4) (137.4 KB)
- [`evaluation_artifacts/phase18/video/Scenario_E_Session2_turn1.mp4`](file:///evaluation_artifacts/phase18/video/Scenario_E_Session2_turn1.mp4) (225.3 KB)
- [`evaluation_artifacts/phase18/video/Scenario_F_Reunion_turn1.mp4`](file:///evaluation_artifacts/phase18/video/Scenario_F_Reunion_turn1.mp4) (238.5 KB)
- [`evaluation_artifacts/phase18/video/Scenario_G_turn4.mp4`](file:///evaluation_artifacts/phase18/video/Scenario_G_turn4.mp4) (188.7 KB)

### C. Longitudinal Turn Telemetry Evidence (10 files — 426.3 KB)
- [`evaluation_artifacts/phase18/telemetry/Scenario_A_session_A_telemetry.json`](file:///evaluation_artifacts/phase18/telemetry/Scenario_A_session_A_telemetry.json) (43.6 KB)
- [`evaluation_artifacts/phase18/telemetry/Scenario_B_session_B_telemetry.json`](file:///evaluation_artifacts/phase18/telemetry/Scenario_B_session_B_telemetry.json) (64.5 KB)
- [`evaluation_artifacts/phase18/telemetry/Scenario_C_session_C_telemetry.json`](file:///evaluation_artifacts/phase18/telemetry/Scenario_C_session_C_telemetry.json) (43.6 KB)
- [`evaluation_artifacts/phase18/telemetry/Scenario_D_session_D_telemetry.json`](file:///evaluation_artifacts/phase18/telemetry/Scenario_D_session_D_telemetry.json) (84.6 KB)
- [`evaluation_artifacts/phase18/telemetry/Scenario_E_Session1_session_E_s1_telemetry.json`](file:///evaluation_artifacts/phase18/telemetry/Scenario_E_Session1_session_E_s1_telemetry.json) (18.4 KB)
- [`evaluation_artifacts/phase18/telemetry/Scenario_E_Session2_session_E_s2_telemetry.json`](file:///evaluation_artifacts/phase18/telemetry/Scenario_E_Session2_session_E_s2_telemetry.json) (14.1 KB)
- [`evaluation_artifacts/phase18/telemetry/Scenario_F_PreAbsence_session_F_s1_telemetry.json`](file:///evaluation_artifacts/phase18/telemetry/Scenario_F_PreAbsence_session_F_s1_telemetry.json) (13.6 KB)
- [`evaluation_artifacts/phase18/telemetry/Scenario_F_Reunion_session_F_reunion_telemetry.json`](file:///evaluation_artifacts/phase18/telemetry/Scenario_F_Reunion_session_F_reunion_telemetry.json) (13.8 KB)
- [`evaluation_artifacts/phase18/telemetry/Scenario_G_session_G_telemetry.json`](file:///evaluation_artifacts/phase18/telemetry/Scenario_G_session_G_telemetry.json) (76.2 KB)
- [`evaluation_artifacts/phase18/telemetry/Scenario_H_session_H_telemetry.json`](file:///evaluation_artifacts/phase18/telemetry/Scenario_H_session_H_telemetry.json) (43.8 KB)

### Review Assessment & Options:
1. **Option 1 (Recommended — Commit to Git directly):** Because the total size across all 14 audiovisual files is only **3.50 MB** (and total telemetry is 0.43 MB), committing them in a dedicated commit (`test(phase18): add audiovisual validation evidence and manifests`) creates zero performance penalty or repository bloat, while preserving permanent, immutable audit evidence.
2. **Option 2 (Git LFS):** Move WAV/MP4 files to Git LFS if strict repository policies forbid any multimedia in standard Git. (Note: Git LFS is currently not configured).
3. **Option 3 (GitHub Release Artifacts):** Package `evaluation_artifacts/phase18/` into a release `.tar.gz` and exclude from Git, tracking only SHA-256 manifests.

---

## 6. Proposed `.gitignore` Changes

The current `.gitignore` properly excludes models, virtual environments, and python caches, but lacks ignore rules for test harness scratch stores. The following patch should be applied:

```diff
--- a/.gitignore
+++ b/.gitignore
@@ -93,6 +93,10 @@ scratch/
 
+# Temporary evaluation harness scratch stores
+docs/specs/**/temp_run_store/
+evaluation_artifacts/**/temp_harness/
+evaluation_artifacts/**/manifests/
+
 # Local config
 config/local/
```

Applying this rule ensures that future test runs of Phase 17 or Phase 18 will never introduce dirty working-tree files.

---

## 7. Proposed Commit Groups

To ensure atomicity, traceability, and architectural separation, the 61 files recommended to keep should be committed across **5 distinct commits**:

### Commit 1: Phase 17 Affective Life Evaluation
```text
feat(evaluation): finalize Phase 17 integrated affective life evaluation
```
**Files (8 files):**
- `tests/evaluation/__init__.py`
- `tests/evaluation/harness.py`
- `tests/evaluation/run_evaluations.py`
- `tests/evaluation/scenarios.py`
- `tests/evaluation/test_phase17_evaluation.py`
- `docs/specs/lucia-phase17-Integrated_Affective_Life_Evaluation/PHASE_17_SPECIFICATION.md`
- `docs/specs/lucia-phase17-Integrated_Affective_Life_Evaluation/PHASE_17_EVALUATION_REPORT.md`
- `docs/specs/lucia-phase17-Integrated_Affective_Life_Evaluation/results/phase17_evaluation_matrix.json`

### Commit 2: Phase 18 Human Longitudinal Validation Infrastructure
```text
feat(phase18): add human longitudinal validation infrastructure
```
**Files (14 files):**
- `tests/evaluation_phase18/__init__.py`
- `tests/evaluation_phase18/audiovisual.py`
- `tests/evaluation_phase18/harness.py`
- `tests/evaluation_phase18/human_protocol.py`
- `tests/evaluation_phase18/runner.py`
- `tests/evaluation_phase18/scenarios.py`
- `tests/evaluation_phase18/telemetry.py`
- `tests/evaluation_phase18/test_phase18_validation.py`
- `docs/specs/lucia-phase18-Human_Longitudinal_Validation/PHASE_18_SPECIFICATION.md`
- `docs/specs/lucia-phase18-Human_Longitudinal_Validation/HUMAN_EVALUATION_PROTOCOL.md`
- `docs/specs/lucia-phase18-Human_Longitudinal_Validation/PHASE_18_EVALUATION_REPORT.md`
- `docs/specs/lucia-phase18-Human_Longitudinal_Validation/PHASE_18_LONGITUDINAL_AUDIOVISUAL_REGENERATION_REPORT.md`
- `docs/specs/lucia-phase18-Human_Longitudinal_Validation/results/audiovisual_manifest.json`
- `docs/specs/lucia-phase18-Human_Longitudinal_Validation/results/human_evaluation_schema.json`
- `docs/specs/lucia-phase18-Human_Longitudinal_Validation/results/phase18_evaluation_matrix.json`

### Commit 3: Production RVC Voice Engine Integration & Diagnostics
```text
feat(voice): integrate validated VaresaGIJP RVC inference
```
**Files (12 files):**
- `src/core/voice/voice_engine.py`
- `src/core/voice/rvc_pipeline.py`
- `src/core/voice/rvc_modules/__init__.py`
- `src/core/voice/rvc_modules/attentions.py`
- `src/core/voice/rvc_modules/commons.py`
- `src/core/voice/rvc_modules/models.py`
- `src/core/voice/rvc_modules/modules.py`
- `src/core/voice/rvc_modules/transforms.py`
- `tests/evaluation_phase18/test_rvc_runtime.py`
- `docs/specs/lucia-phase18-Human_Longitudinal_Validation/PHASE_18_VOICE_RUNTIME_VERIFICATION_REPORT.md`
- `docs/specs/lucia-phase18-Human_Longitudinal_Validation/PHASE_18_RVC_AUDIO_QUALITY_DIAGNOSTIC.md`
- `docs/specs/lucia-phase18-Human_Longitudinal_Validation/PHASE_18_RVC_AUDIO_QUALITY_FINAL_VERIFICATION.md`

### Commit 4: Phase 18 Longitudinal Audiovisual & Telemetry Evidence
```text
test(phase18): add audiovisual validation evidence and manifests
```
**Files (24 files):**
- `evaluation_artifacts/phase18/audio/Scenario_A_turn1.wav`
- `evaluation_artifacts/phase18/audio/Scenario_B_turn2.wav`
- `evaluation_artifacts/phase18/audio/Scenario_C_turn3.wav`
- `evaluation_artifacts/phase18/audio/Scenario_D_turn16.wav`
- `evaluation_artifacts/phase18/audio/Scenario_E_Session2_turn1.wav`
- `evaluation_artifacts/phase18/audio/Scenario_F_Reunion_turn1.wav`
- `evaluation_artifacts/phase18/audio/Scenario_G_turn4.wav`
- `evaluation_artifacts/phase18/video/Scenario_A_turn1.mp4`
- `evaluation_artifacts/phase18/video/Scenario_B_turn2.mp4`
- `evaluation_artifacts/phase18/video/Scenario_C_turn3.mp4`
- `evaluation_artifacts/phase18/video/Scenario_D_turn16.mp4`
- `evaluation_artifacts/phase18/video/Scenario_E_Session2_turn1.mp4`
- `evaluation_artifacts/phase18/video/Scenario_F_Reunion_turn1.mp4`
- `evaluation_artifacts/phase18/video/Scenario_G_turn4.mp4`
- `evaluation_artifacts/phase18/telemetry/Scenario_A_session_A_telemetry.json`
- `evaluation_artifacts/phase18/telemetry/Scenario_B_session_B_telemetry.json`
- `evaluation_artifacts/phase18/telemetry/Scenario_C_session_C_telemetry.json`
- `evaluation_artifacts/phase18/telemetry/Scenario_D_session_D_telemetry.json`
- `evaluation_artifacts/phase18/telemetry/Scenario_E_Session1_session_E_s1_telemetry.json`
- `evaluation_artifacts/phase18/telemetry/Scenario_E_Session2_session_E_s2_telemetry.json`
- `evaluation_artifacts/phase18/telemetry/Scenario_F_PreAbsence_session_F_s1_telemetry.json`
- `evaluation_artifacts/phase18/telemetry/Scenario_F_Reunion_session_F_reunion_telemetry.json`
- `evaluation_artifacts/phase18/telemetry/Scenario_G_session_G_telemetry.json`
- `evaluation_artifacts/phase18/telemetry/Scenario_H_session_H_telemetry.json`

### Commit 5: Repository Documentation Index & Operational Status
```text
docs: update documentation index and current system status
```
**Files (2 files):**
- `docs/CURRENT_STATUS.md`
- `docs/DOCUMENTATION_INDEX.md`

---

## 8. Large Binary / Artifact Strategy

| Binary Type | Location | Total Size | Status / Recommendation |
|---|---|---:|---|
| **RVC Model Checkpoint (`.pth`)** | `models/voice/rvc/VaresaGIJP/VaresaGIJP_300e_2100s.pth` | 55.23 MB | **Already Ignored** by `.gitignore` (`models/voice/rvc/**/*.pth`). Do not track in Git. |
| **RVC Feature Index (`.index`)** | `models/voice/rvc/VaresaGIJP/added_VaresaGIJP_v2.index` | 32.81 MB | **Already Ignored** by `.gitignore` (`models/voice/rvc/**/*.index`). Do not track in Git. |
| **LLM Model (`.gguf`)** | `models/LFM2.5-1.2B-Instruct-Q4_K_M.gguf` | 730.90 MB | **Already Ignored** by `.gitignore` (`models/*.gguf`). Do not track in Git. |
| **Phase 18 Audio (`.wav`)** | `evaluation_artifacts/phase18/audio/*.wav` (7 files) | 2.05 MB | **Commit to Normal Git** (Commit 4). Small footprint, required as reproducible scientific evidence. |
| **Phase 18 Video (`.mp4`)** | `evaluation_artifacts/phase18/video/*.mp4` (7 files) | 1.45 MB | **Commit to Normal Git** (Commit 4). Small footprint, required as multimodal sprite verification evidence. |
| **Mock `model.gguf` stubs** | `temp_run_store/**` & `temp_harness/**` (35 files) | < 1 KB | **Exclude & Ignore**. Ephemeral dummy stubs. |

---

## 9. Phase 17 / Phase 18 Integrity Check

An automated integrity check was performed against all Phase 16 invariants and canonical storage:

### A. Phase 16 Invariant Compliance
1. **Memory $X \rightarrow$ L2 $h$ forbidden:** VERIFIED. No bypass or direct memory coupling to the ODE hidden state was introduced.
2. **Expression/Body $X \rightarrow$ EmotionCore ODE forbidden:** VERIFIED. The 15D expression policy and avatar rendering consume emotion readouts downstream without feedback loops.
3. **Communication strategy $X \rightarrow$ relationship reward forbidden:** VERIFIED. Dialogue strategy modulates surface formatting and pacing, not relationship affinity.
4. **Simulation/tests $X \rightarrow$ canonical storage forbidden:** VERIFIED. All Phase 17 and Phase 18 test harnesses redirected persistence to isolated temporary stores (`temp_run_store` and `temp_harness`).

### B. First Activation Boundary Verification
- `data/profile.json`: SHA-256 = `1bf496e742b503a324ecd27156e4e30b30ed35cab496897c3a831380fbf0f97c` (**100% BIT-EXACT UNTOUCHED**)
- `data/chat_history.json`: SHA-256 = `0344098fd533e972de4034fc1355f9b27c7617fce3b4fc7812a175d21fbd0165` (**100% BIT-EXACT UNTOUCHED**)
- `is_onboarded` status: **`False`**
- **Conclusion:** Lucia has **NEVER** been activated or onboarded. The First Activation boundary is completely intact.

---

## 10. Final Recommendation

### Verdict
```text
DO NOT COMMIT ALL — FILTER REQUIRED
```

### Exact Rationale
A blind `git add .` would commit **68 ephemeral files** (comprising 35 mock model stubs, 32 temporary test-session relationship snapshots, and 1 duplicate manifest) into the repository. These files are disposable test run residues that belong in `.gitignore`.

The repository should follow the proposed **5-stage commit plan**, committing exactly **61 authoritative files** (37 definite + 24 reviewed evidence) and excluding all 68 temporary residues.

---
*Report generated automatically by Antigravity AI Agent during Git Worktree Audit.*
