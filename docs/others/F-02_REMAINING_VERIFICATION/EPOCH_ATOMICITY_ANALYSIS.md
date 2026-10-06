# Multi-Store Epoch Coordination & Atomicity Analysis (F-02)

**Document ID:** `VERIF-EPOCH-ATOM-20261007`  
**Classification:** Concurrency, Filesystem Semantics & Transactional Integrity Analysis  
**Baseline Commit:** `32660ac4e422bdb2ecb9c7b97a4bdc04c805418e`  
**Parent Document:** [`REPORT.md`](file:///c:/Users/Lunafiah/Desktop/My_project/Lucia/docs/others/F-02_REMAINING_VERIFICATION/REPORT.md)  

---

## 1. Problem Statement: The Multi-Store Atomicity Challenge

In the current Lucia implementation, state persistence is partitioned across independent JSON files:
1. `data/relationship.json` (Written at Stage 16.3)
2. `data/dynamical_state.json` (Written at Stage 16.5)
3. `data/chat_history.json` (Written at `/process` entry and exit)

Each file individually achieves single-file crash consistency via tempfile write + atomic `os.replace`. However, as revealed by finding **E-04**, there is **zero transaction coordination** across these stores.

If the host machine loses power, the OS terminates the process (`taskkill /F`), or an Out-Of-Memory (OOM) event occurs between Stage 16.3 and Stage 16.5:
- `relationship.json` reflects Turn $N+1$.
- `dynamical_state.json` reflects Turn $N$.
- On subsequent restart, subsystems load mutually contradictory logical epochs.

This analysis evaluates candidate mechanisms to achieve cross-store consistency on local Windows edge environments.

---

## 2. Fundamental Distinction: Atomic Commit vs. Consistency Detection

To avoid architectural conflation, we establish the strict distinction between these two capabilities:

| Dimension | **Consistency Detection** | **Atomic Commit** |
|---|---|---|
| **Definition** | Ability to detect on cold boot whether persistent stores agree on the identical epoch. | Ability to guarantee that multi-file mutations transition from epoch $N \to N+1$ simultaneously or not at all. |
| **Crash Handling** | If an epoch mismatch is detected, system halts, flags an error, or rolls back the divergent store to `.bak`. | Impossible for a partial state transition to become visible on disk. |
| **Filesystem Requirement** | Standard POSIX / NTFS file write; metadata header validation. | Transactional filesystem, Write-Ahead Log (WAL), or Directory Renaming. |
| **Complexity** | Extremely low ($\le 50$ lines of code). | Moderate to high (requires WAL replay or directory swap). |

---

## 3. Comparative Evaluation of Six Coordination Architectures

### Option A: Shared Epoch Manifest (`data/epoch_manifest.json`)
- **Mechanism:** A lightweight manifest file recording `{"epoch_id": 42, "t_commit": float, "stores": {"rel": 42, "dyn": 42}}`.
- **Commit Sequence:**
  1. Write `relationship.json.tmp` $\to$ `os.replace` to `relationship.json`.
  2. Write `dynamical_state.json.tmp` $\to$ `os.replace` to `dynamical_state.json`.
  3. Write `epoch_manifest.json.tmp` $\to$ `os.replace` to `epoch_manifest.json` (The Commit Point).
- **Crash Recovery:** On startup, read `epoch_manifest.json`. If `relationship.json` or `dynamical_state.json` has an internal `epoch_id` that does not match the manifest's committed `epoch_id`, roll back the uncommitted store using its `.bak` file.
- **Verdict:** **HIGHLY PRACTICAL.** Provides an explicit **Commit Barrier**.

---

### Option B: Write-Ahead Journal (WAL / SQLite)
- **Mechanism:** Route all turn state changes into an embedded SQLite database using WAL mode (`PRAGMA journal_mode=WAL`).
- **Strengths:** True ACID transactions; zero multi-file tearing; atomic multi-table commits.
- **Weaknesses:** Requires migrating existing human-readable JSON files (`data/*.json`) into SQLite; complicates transparency and manual inspection; introduces SQL migrations.
- **Verdict:** **OVER-ENGINEERED FOR F-02.** Defers human readability without biological necessity.

---

### Option C: Transactional Directory Snapshot (Shadow Directory Swap)
- **Mechanism:** Write all files into a temporary directory `data_next/`. Once all writes succeed, perform an atomic directory swap `data/ $\leftrightarrow$ data_next/`.
- **Failure Mode on Windows:** On Windows NTFS, directory renaming is **NOT atomic** if any file in the directory has an open handle (e.g., active loggers, Electron watchers). `os.replace` on directories on Windows frequently raises `PermissionError` or `AccessDenied`.
- **Verdict:** **REJECTED.** Unreliable on Windows NTFS.

---

### Option D: Single Consolidated Life-State File
- **Mechanism:** Merge `relationship.json` and `dynamical_state.json` into a single monolithic JSON file `data/life_state.json`.
- **Strengths:** Atomic commit is trivial: a single `os.replace` commits both relational and dynamical state simultaneously.
- **Weaknesses:** Tightly couples subcortical limbic ODE serialization with social relationship tracking; breaks existing modular APIs (`GET /state/relationship`, `GET /state/dynamical`).
- **Verdict:** **VIABLE FALLBACK, BUT SUBOPTIMAL MODULARITY.**

---

### Option E: Two-Phase Commit Across JSON Stores
- **Mechanism:** Implement distributed 2PC coordinator in Python with `PREPARE` and `COMMIT` phases across files.
- **Weaknesses:** Extremely complex; requires crash-state recovery machines; prone to deadlocks and recovery edge-cases.
- **Verdict:** **REJECTED.** Unjustified complexity for single-process local execution.

---

### Option F: Hybrid Manifest + Atomic File Replacement (Recommended)
- **Mechanism:** Combines Option A with existing single-file backup ladders:
  1. Sequential atomic writes to domain JSON stores (`data/relationship.json`, `data/dynamical_state.json`), each stamped with `epoch_id = N+1`.
  2. Final atomic commit of `data/epoch_manifest.json` recording `committed_epoch = N+1`.
  3. If a crash occurs before step 2: on boot, orchestrator observes `dyn.epoch == N+1` but `manifest.epoch == N`. Orchestrator restores `dynamical_state.json.bak` (epoch $N$), restoring causal consistency bit-exact.
- **Windows Filesystem Compatibility:** 100% compliant. `os.replace` on single files is atomic on Windows NTFS on the same volume.

---

## 4. Multi-Store Architecture Comparison Matrix

| Criterion | Option A (Manifest) | Option B (SQLite WAL) | Option C (Dir Swap) | Option D (Single File) | Option E (2PC) | Option F (Hybrid Manifest) |
|---|---|---|---|---|---|---|
| **Crash Consistency** | HIGH | EXCELLENT | POOR (Win NTFS) | EXCELLENT | MODERATE | **EXCELLENT** |
| **Commit Barrier** | YES | YES | YES | YES | YES | **YES** |
| **Windows NTFS Safety** | SAFE | SAFE | FAILS (Locks) | SAFE | RISKY | **SAFE** |
| **Recovery Complexity** | LOW | MINIMAL | HIGH | ZERO | HIGH | **LOW** |
| **Schema Migration** | ZERO | HIGH (DB Schema) | ZERO | HIGH (Unified) | HIGH | **ZERO** |
| **Subsystem Modularity**| EXCELLENT | POOR | MODERATE | POOR | MODERATE | **EXCELLENT** |
| **CPU / Lock Overhead** | $\le 1\,\text{ms}$ | $2\text{--}5\,\text{ms}$ | $5\text{--}10\,\text{ms}$ | $\le 1\,\text{ms}$ | $5\text{--}10\,\text{ms}$ | **$\le 1\,\text{ms}$** |
| **Human Readability** | PRESERVED | LOST | PRESERVED | PRESERVED | PRESERVED | **PRESERVED** |

---

## 5. Architectural Recommendation

We recommend **Option F (Hybrid Manifest + Atomic File Replacement)**:
1. It solves finding **E-04** completely without altering existing JSON schemas or introducing external database engines.
2. It guarantees that subsystems agree on the exact logical turn boundary upon cold restart.
3. It preserves single-file human inspection and git transparency.
