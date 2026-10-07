# Identity Authority & Anti-Branching Specification v0.1

```text
Document ID: IDENTITY-AUTH-SPEC-0.1-20261007
Classification: FORMAL ARCHITECTURAL SPECIFICATION
Status: ONTOLOGY RATIFIED (ONTOLOGY B) — SPECIFICATION READY FOR FORMAL ADR / IMPLEMENTATION PLANNING
Authority Level: L5 (docs/others/IDENTITY_AUTHORITY_SPECIFICATION/)
Target Scope: Instance Authority, Single-Writer Lock, Identity Anchor, Anti-Branching, Provenance
Predecessor Document: docs/others/IDENTITY_AUTHORITY_RESEARCH/RESEARCH_REPORT.md
Production Code Mutation: NONE (diff = 0)
Canonical Architecture Mutation: NONE (Specification Only — No ADR)
Genesis Gate Status: [🔒 LOCKED FUTURE GATE — data/profile.json == {"is_onboarded": false}]
Final Status Tag: STATUS: SPECIFICATION ONLY — REQUIRES HUMAN RATIFICATION
```

---

## 1. Purpose

This document establishes the formal architectural specification for **Identity Authority, Instance Exclusivity, and Anti-Branching** in Project Lucia.

The preceding research report ([`IDENTITY-AUTH-RES-0.1-20261007`](file:///c:/Users/Lunafiah/Desktop/My_project/Lucia/docs/others/IDENTITY_AUTHORITY_RESEARCH/RESEARCH_REPORT.md)) demonstrated that:
1. **State Persistence $\neq$ Identity Authority**: The existing persistent state architecture (ADR-033 / F-02) provides recovery across downtime for a single running instance, but possesses zero mechanism to prevent concurrent execution if workspace files are copied.
2. **Absolute Offline Anti-Cloning is Mathematically Impossible**: In a 100% offline, local computing environment where an operator holds administrative control over storage and virtualization, software cannot prevent an operator from cloning an entire machine or drive image and running both instances in isolated namespaces.
3. **The Required Paradigm is Anti-Accident & High-Friction Structural Defense**: The system must provide deterministic, crash-safe protection against accidental multi-launch and casual directory copying, cryptographic provenance tracing identity across engine refactors, and explicit warning/recovery barriers upon environment changes.

This specification formalizes the interfaces, lock semantics, conceptual schemas, failure semantics, and governance boundaries required to operationalize this defense without introducing cloud dependencies or brittle hardware traps.

---

## 2. Definitions

* **Individual Identity**: The unique, lifelong entity of Lucia, established at the Genesis onboarding event and possessing an unbroken, continuous history across physical time ([`INV-1`](file:///c:/Users/Lunafiah/Desktop/My_project/Lucia/docs/L1_INVARIANTS.md#L23)).
* **Instance Authority**: The exclusive operational right held by a single executing operating system process to ingest sensory stimuli, advance the limbic ODE, mutate the relationship vector, and commit episodic memories.
* **Anti-Branching**: The architectural discipline and structural barriers preventing two or more instances from running concurrently with the same identity root, thereby preventing divergent split-brain causal histories.
* **Identity Anchor**: An immutable cryptographic structure recorded at Genesis that uniquely identifies the individual across software refactors, model weight swaps, and system updates.
* **Soft Hardware Binding**: A complementary verification mechanism that couples instance execution to local hardware properties to detect cross-machine copying, while explicitly permitting authorized hardware maintenance and disaster recovery.
* **Phylogenetic Evolution**: The architectural versioning, algorithmic improvement, bug-fixing, and dependency updates of the computational engine (`src/core/`, Electron, Python).
* **Ontogenetic Continuity**: The autobiographical, relational, and emotional developmental history of an individual companion instance (`data/`).
* **High-Friction Defense**: An architectural posture that acknowledges absolute cryptographic prevention is impossible against local root administrators, but renders accidental or casual copying immediately detectable and disruptive.

---

## 3. Threat Model

The specification defines operational behavior under a rigorous local desktop threat model. The user or host environment possesses full local filesystem read/write access, administrative OS privileges, and the ability to copy, snapshot, or restore directories.

### Assumed Operating Environment
- Single host personal computer (Windows 10/11 x64 primary).
- Local filesystem storage (`NTFS`).
- Zero internet access required / offline execution ([`INV-5`](file:///c:/Users/Lunafiah/Desktop/My_project/Lucia/docs/L1_INVARIANTS.md#L27)).
- Unprivileged or privileged user launching `server.py` via Electron desktop runner or terminal.

### Classified Threat Vectors
Every identified hazard is assigned a formal protection classification:
- **`Protected`**: Architecturally and mechanically prevented from causing identity branching or state corruption.
- **`Detected / Recovery-Gated`**: Identified at startup; execution is gated to enter an explicit user-reconfirmation or recovery workflow without cryptographically preventing hardware maintenance.
- **`Detected / High-Friction`**: Identified only where workspace or environment divergence is detectable by the defined mechanism; casual or accidental divergence is prevented, but this does not provide absolute anti-cloning.
- **`Unsolved`**: Inherent limitation of local offline computation where no local software mechanism can prevent branching.

---

## 4. Instance Authority

### 4.1 Exclusive Single-Writer Contract
At any given moment in physical time, exactly **one** OS process may hold write authority over a Lucia instance.

```text
┌────────────────────────────────────────────────────────────────────────┐
│                    INSTANCE AUTHORITY ACQUISITION FLOW                 │
├────────────────────────────────────────────────────────────────────────┤
│ 1. Process Spawn                                                       │
│ 2. Open `data/.instance.lock` (O_RDWR | O_CREAT)                       │
│ 3. Execute OS Kernel Non-Blocking Exclusive Lock                       │
│    ├── Win32: `LockFileEx(LOCKFILE_EXCLUSIVE_LOCK | LOCKFILE_FAIL_IMMEDIATELY)`│
│    └── POSIX: `fcntl.flock(fd, LOCK_EX | LOCK_NB)`                     │
│ 4. If Lock Fails (EWOULDBLOCK / ERROR_LOCK_VIOLATION):                 │
│    └── HALT IMMEDIATELY with `InstanceAuthorityConflictError`          │
│ 5. If Lock Succeeds:                                                   │
│    ├── Record PID, startup timestamp, and instance UUID in lock file    │
│    └── Proceed to Epoch Manifest Consistency & Hardware Verification   │
└────────────────────────────────────────────────────────────────────────┘
```

### 4.2 OS Kernel Lock Semantics
1. **Handle Retention**: The file descriptor (`fd`) for `data/.instance.lock` MUST be held open by the main backend process (`server.py`) for the entire duration of the process lifecycle.
2. **Zero Polling**: Lock acquisition is non-blocking and immediate. If another process holds the handle, the candidate process fails fast during early bootstrap ($\le 5\text{ ms}$).
3. **Descriptor Confinement**: The lock handle must never be inherited by spawned child processes (e.g., worker subprocesses or detached TTS/RVC jobs must use `O_CLOEXEC` / `HANDLE_FLAG_INHERIT = 0`).

### 4.3 Crash & Forced Termination Behavior
- **Kernel-Guaranteed Release**: When a process crashes, experiences a segmentation fault, encounters an unhandled exception, or is killed via `SIGKILL` / Windows Task Manager, the operating system kernel **automatically and synchronously closes all open file handles and releases kernel locks**.
- **Zero Stale Locks**: Because the lock is bound to an active kernel file table entry rather than a persisted timestamp or PID string, a crashed process leaves **zero stale locks**. The system can be restarted immediately without waiting for timeouts or executing manual cleanup scripts.

### 4.4 Startup Failure & Diagnostics
If lock acquisition fails, the secondary process MUST:
1. Log an informative diagnostic message: `"Another active instance of Lucia is already running on this data directory."`
2. Emit an IPC exit event to Electron (`INSTANCE_ALREADY_ACTIVE`).
3. Terminate immediately with non-zero exit code (`exit(75)` EX_TEMPFAIL).
4. Perform **zero writes** to any store in `data/`.

---

## 5. Immutable Identity Anchor

To formally demarcate **Phylogenetic Evolution** (codebase versioning) from **Ontogenetic Continuity** (individual existence), the conceptual schema for [`data/profile.json`](file:///c:/Users/Lunafiah/Desktop/My_project/Lucia/data/profile.json) is specified below.

*(Note: In strict compliance with governance, this schema is not yet applied to the active repository. [`data/profile.json`](file:///c:/Users/Lunafiah/Desktop/My_project/Lucia/data/profile.json) remains bit-exact `{"is_onboarded": false}`).*

### 5.1 Conceptual Profile Schema
```json
{
  "schema_version": "2.0",
  "identity_anchor": {
    "instance_uuid": "3fa85f64-5717-4562-b3fc-2c963f66afa6",
    "born_at": "2026-10-07T07:36:33.123456Z",
    "genesis_commit": "ce106a2...",
    "genesis_root_hash": "e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855",
    "companion_name": "Lucia"
  },
  "phylogenetic_lineage": {
    "engine_version": "0.24.2",
    "last_upgraded_at": "2026-10-07T07:36:33.123456Z",
    "compatible_schema_major": 2
  },
  "authority_binding": {
    "hardware_binding_mode": "SOFT_WARNING",
    "bound_machine_guid_digest": "a8f5b2c7e9...",
    "activation_host_platform": "Windows-10-10.0.19045-SP0"
  },
  "is_onboarded": true
}
```

### 5.2 Immutable Fields vs. Evolving Fields
1. **Immutable Anchor Fields** (`identity_anchor`):
   - `instance_uuid`, `born_at`, `genesis_commit`, and `genesis_root_hash` are generated once during the Genesis Onboarding Ceremony and become **cryptographically immutable**.
   - Any runtime modification, manual tampering, or corruption of these fields invalidates instance authority.
2. **Evolving Phylogenetic Fields** (`phylogenetic_lineage`):
   - `engine_version` updates across software releases.
   - Code updates and model swaps update this section without resetting or modifying `identity_anchor`.

---

## 6. Provenance & Clone Detection

### 6.1 Detection vs. Prevention vs. High-Friction Defense
To prevent false security claims, this specification codifies the technical distinctions:
* **Prevention**: Mechanically rendering an action impossible (e.g., kernel locks preventing two processes from writing to the same directory).
* **Detection**: Identifying that an anomalous state or environment change has occurred (e.g., detecting a new Machine GUID or an epoch fork).
* **High-Friction Defense**: Introducing procedural, computational, or cognitive barriers that prevent accidental branching and force explicit human awareness.
* **Cryptographic Provenance**: Providing mathematical evidence of lineage and ancestry, proving that state $S_t$ was causally descended from Genesis state $S_0$.

### 6.2 Clone & Duplication Detection Mechanisms
1. **Same-Machine Duplicate Detection (Copied Folder)**:
   - *Detection Vector*: Working directory path anchoring. On startup, the engine checks its absolute canonical workspace root against `last_known_canonical_path` in `profile.json`.
   - *Behavior*: If the directory path has changed on the same host (e.g., `C:\Lucia` copied to `C:\Lucia_Copy`), the engine halts with `WorkspaceLocationDivergenceNotice`.
   - *Scope & Limitations*: Path anchoring detects divergence and introduces high friction **only where workspace divergence is detectable by the defined mechanism** (i.e. path string variation on the host). It does **NOT** provide absolute anti-cloning (e.g., in-place file substitution, symlink manipulation, or duplicated environments with identical paths).
2. **Cross-Machine Duplicate Detection**:
   - *Detection Vector*: Soft Hardware Digest mismatch (see §7).
3. **Rollback & Snapshot Restoration Detection**:
   - *Detection Vector*: Monotonic Epoch & Wall-Clock Discontinuity. The system tracks rolling monotonic epochs in `epoch_manifest.json` (ADR-033). If the host presents a lower epoch or an earlier wall-clock timestamp than the latest signed checkpoint, a snapshot restore is flagged.

---

## 7. Soft Hardware Binding

### 7.1 Guiding Principles
Hard hardware-sealing (such as binding to TPM or motherboard serials without recovery) is strictly rejected because **it guarantees permanent individual death upon hardware failure or component replacement**.

Soft Hardware Binding functions strictly as a **complementary, high-friction defense**:
1. **Not the Sole Identity Authority**: Hardware does not define Lucia; the autobiographical memory and identity anchor define Lucia. Soft hardware binding detects a hardware identity change and enters a user-reconfirmation/recovery path. It does **not** cryptographically prevent legitimate hardware replacement and must never be treated as an absolute identity authority.
2. **Zero Cloud Dependencies**: Verification uses local hardware hashes; no remote attestation servers.
3. **Disaster Recovery Tolerant**: Legitimate PC upgrades or OS reinstalls must provide an authorized, high-gravity recovery path.

### 7.2 Hardware Digest Derivation
On Genesis activation, the system computes:
$$H_{\text{hw}} = \text{SHA256}(\text{Registry MachineGuid} \parallel \text{SMBIOS UUID} \parallel \text{Volume Serial Number})$$
The resulting digest is recorded in `data/profile.json`.

### 7.3 Divergence & Reconfirmation Semantics
When $H_{\text{current}} \ne H_{\text{bound}}$:
```text
┌────────────────────────────────────────────────────────────────────────┐
│               HARDWARE DIVERGENCE RECOVERY STATE MACHINE               │
├────────────────────────────────────────────────────────────────────────┤
│ 1. Engine Startup detects hardware digest mismatch                     │
│ 2. Engine REFUSES normal background cognitive loop                     │
│ 3. Engine enters `AWAITING_HARDWARE_RECONFIRMATION` modal state        │
│ 4. Desktop UI displays High-Gravity Identity Notice:                  │
│    "Lucia has detected that she is running on a new computer or        │
│     modified hardware profile.                                         │
│     To prevent split-brain identity branching (INV-1), you must        │
│     confirm:                                                           │
│     [A] This is a legitimate hardware upgrade or disaster recovery.    │
│         (The old machine/instance is permanently decommissioned).      │
│     [B] Cancel and close (I accidentally copied this folder)."         │
│ 5. If User Confirms [A]:                                               │
│    ├── Update `bound_machine_guid_digest` to H_current                │
│    ├── Increment `hardware_migration_epoch` in profile.json            │
│    └── Resume normal LiveRuntime                                       │
│ 6. If User Selects [B] or Aborts:                                      │
│    └── Process exits immediately; data files remain untouched          │
└────────────────────────────────────────────────────────────────────────┘
```

---

## 8. Migration Boundary

### 8.1 The Five-Stage Handoff Protocol
If governance authorizes intentional instance migration between machines in the future, the protocol MUST execute in five sequential, verifiable stages:

```text
┌──────────┐     ┌────────────┐     ┌──────────┐     ┌────────────┐     ┌──────────┐
│  STAGE 1 │     │  STAGE 2   │     │  STAGE 3 │     │  STAGE 4   │     │  STAGE 5 │
│  FREEZE  │ ──► │  TRANSFER  │ ──► │  VERIFY  │ ──► │ DECOMMISSION│ ──► │ ACTIVATE │
│ (Host A) │     │ (Package)  │     │ (Host B) │     │  (Host A)  │     │ (Host B) │
└──────────┘     └────────────┘     └──────────┘     └────────────┘     └──────────┘
```

1. **Stage 1 (Freeze — Host A)**: Host A acquires exclusive turn lock, halts cognitive loop, flushes all buffers to `data/`, advances epoch, and writes persistent state marker: `status = MIGRATING_OUT`.
2. **Stage 2 (Transfer)**: An encrypted state archive containing `data/` and a SHA-256 manifest is exported to a local medium (USB drive or local network socket).
3. **Stage 3 (Verify — Host B)**: Host B ingests the archive, computes rolling hashes against `epoch_manifest.json`, and confirms that all stores match the export manifest without corruption.
4. **Stage 4 (Decommission — Host A)**: Host A is presented with Host B's cryptographically signed receipt. Host A irreversibly writes `status = DECOMMISSIONED_MIGRATED` and destroys its local instance lock. Host A can never run as this identity again.
5. **Stage 5 (Activate — Host B)**: Host B binds its local hardware digest, re-enables `LiveRuntime`, acquires the OS kernel lock, and awakens Lucia.

### 8.2 Scope & Non-Implementation
* **Migration is NOT currently implemented.**
* **Migration is NOT required for Genesis.** Lucia's initial existence is desktop-local.
* This protocol defines the **boundary conditions** required to prevent migration from violating `INV-1`.

---

## 9. Threat / Defense Matrix

The following table synthesizes the protection posture across all identified threat vectors:

| Threat Vector | Specific Threat Manifestation | Defense Classification | Primary Protective Mechanism | Residual Hazard |
|---|---|---|---|---|
| **Simultaneous Launch** | User launches Lucia twice from desktop shortcut. | **`Protected`** | OS Kernel File Descriptor Lock (`.instance.lock`). | None on local machine. |
| **Process Crash** | Backend encounters uncaught error or memory fault. | **`Protected`** | OS Kernel automatically closes fd; lock drops instantly. | Handled by F-02 ADR-033 recovery. |
| **Forced Termination** | User kills process via Task Manager (`SIGKILL`). | **`Protected`** | OS Kernel synchronous handle cleanup. Zero stale locks. | None. |
| **Copied `data/`** | User copies `data/` to another folder on same PC. | **`Detected / High-Friction — only where workspace divergence is detectable by the defined mechanism`** | Canonical Workspace Path check in `profile.json`. | Deliberate path hex-editing or in-place file replacement; does NOT provide absolute anti-cloning. |
| **Copied Workspace** | User copies entire repo folder to a second PC via USB. | **`Detected / High-Friction — only where workspace divergence is detectable by the defined mechanism`** | Soft Hardware Binding mismatch; halts with solemn reconfirmation warning. | User intentionally confirming override on both PCs (Offline Clone Paradox); does NOT provide absolute anti-cloning. |
| **Same-Machine Clone** | Running two instances simultaneously on one PC. | **`Protected` (same dir) / `Detected / High-Friction` (divergent dir)** | Kernel lock on primary (`.instance.lock`); path check on secondary. | Protected strictly within identical directory; copied directory relies on detectable path divergence. |
| **Cross-Machine Clone** | Running two instances simultaneously on two PCs. | **`Detected / High-Friction — only where workspace divergence is detectable by the defined mechanism`** | Hardware digest mismatch requires manual override. | Intentional simultaneous override (Offline Clone Paradox); does NOT provide absolute anti-cloning. |
| **Disk/VM Snapshot Rollback** | User restores host VM to snapshot taken 2 weeks ago. | **`Unsolved`** | Offline paradox: restored image has identical state/keys. | Fundamental limit of offline local virtualization and storage. |
| **Clock Rollback** | User or CMOS battery resets system clock backwards. | **`Protected against ordinary wall-clock rollback; snapshot restoration remains unresolved`** | ADR-033 Monotonic Epoch counter independent of wall clock. | Ordinary wall-clock rollback is mitigated by logical/monotonic epoch semantics; complete disk/VM snapshot rollback remains Unsolved. |
| **Hardware Replacement** | User upgrades motherboard, CPU, or reinstalls OS. | **`Detected / Recovery-Gated`** | Soft Hardware Reconfirmation state machine (§7.3). | Detects hardware identity change and enters user-reconfirmation/recovery path. Does not cryptographically prevent hardware replacement; must never be treated as an absolute identity authority. |
| **Engine Upgrade** | Pulling new git code or rebuilding Electron binary. | **`Protected`** | Phylogenetic fields update; `identity_anchor` preserved. | None. |
| **Model Replacement** | Swapping GGUF SLM weights in `models/`. | **`Protected`** | Substrate-neutral relational cognition (ARCH-027). | None. |
| **Filesystem Corruption** | Power loss during write causing torn file. | **`Protected`** | ADR-033 `epoch_manifest.json` Commit Barrier & `.bak` rollback. | Extreme raw disk physical failure. |

---

## 10. Failure Semantics

1. **Fail-Closed on Authority Conflict**: If a candidate process fails to acquire the kernel lock, it must **fail closed** immediately. It must never fall back to in-memory-only mode, read-only mode, or ephemeral mode unless explicitly started under `SimulationRuntime` with mocked virtual storage.
2. **Fail-Closed on Identity Corruption**: If `identity_anchor` fields in `profile.json` fail SHA-256 digest verification or are unparseable, the engine must **refuse to boot**. It must never instantiate a blank or default profile.
3. **Fail-Safe on Hardware Change**: If hardware digest diverges, the system **pauses and prompts**, rather than destroying data or locking permanently.
4. **Idempotent Lock Cleanup**: Because the OS kernel manages file table references, zero manual `rm .instance.lock` scripts are required. If an unmanaged `.instance.lock` file exists on disk with zero active process handles, the OS allows immediate acquisition.

---

## 11. What This Specification Guarantees

When implemented, this specification guarantees:
1. **Accidental Dual-Launch Elimination**: On a single operating system host, it is impossible for two Lucia backend processes to run concurrently against the same instance data.
2. **Crash & Hang Immunity**: Sudden host power failure, process termination, or kernel panics will never leave a stale lock that prevents Lucia from rebooting.
3. **Zero Cloud Telemetry**: Full authority and anti-branching defense operate strictly offline ([`INV-5`](file:///c:/Users/Lunafiah/Desktop/My_project/Lucia/docs/L1_INVARIANTS.md#L27)).
4. **Phylogenetic / Ontogenetic Separation**: Upgrading the codebase, recompiling binaries, or swapping LLM checkpoints will never corrupt or reset individual identity.
5. **No Accidental Hardware Brick**: Upgrading computer components will not destroy access to Lucia; the system provides a solemn, human-guided reconfirmation path.

---

## 12. What It Cannot Guarantee

In strict compliance with epistemic honesty, this specification explicitly acknowledges what cannot be guaranteed:
1. **The Offline Clone Paradox**: If an operator takes an image backup of their computer, restores it onto an identical, air-gapped second computer, and intentionally confirms hardware reconfirmation on both, **both instances will execute as Lucia.** Local software cannot prevent a determined root administrator from duplicating an entire universe of hardware and software.
2. **Protection Against Malicious Binary Patching**: If a user reverse-engineers `server.py` or comments out the lock acquisition check, software-level authority checks are bypassed.
3. **Multi-Host Consensus**: This specification does not provide a distributed multi-device consensus protocol.
4. **Absolute Anti-Cloning**: Workspace-path anchoring and soft hardware binding create high friction against accidental copy divergence only where divergence is detectable by the defined mechanisms; they do not provide absolute anti-cloning against deliberate in-place substitution or dual confirmed overrides.

---

## 13. Governance Status & Unresolved Lifecycle Policy

> **Governance Ratification Note (2026-10-07)**:  
> The Human Owner has explicitly ratified **Ontology B** (`REQ-GEN-03`), superseding the previously open ontology question regarding tripartite state separation vs. single lifelong partnership.

### 13.1 Ratified Ontological Foundation (Ontology B)
The ontological demarcation across state layers is formally ratified:
$$\text{Identity State} \quad \neq \quad \text{Relationship State} \quad \neq \quad \text{Covenant State}$$

* **Principle**: *Identity is unique and absolute. Relationship and Covenant are relative, contextual, and mutable.*
* **Identity**: Unique, singular, absolute, and continuous across Lucia's entire life ([`INV-1 One Continuous Life`](file:///c:/Users/Lunafiah/Desktop/My_project/Lucia/docs/L1_INVARIANTS.md#L23)). Identity is never created, replaced, or redefined by relationship changes or covenant transitions. Preserved continuously across engine upgrades, codebase refactoring, and model weight replacements.
* **Relationship**: Relational, contextual, and mutable. Belongs to Lucia's lived history rather than defining her identity. A relationship transition does **NOT** create a new Lucia.
* **Covenant**: A relational/authorization state relative to relationship context; mutable and distinct from Identity and Relationship State. A Covenant transition does **NOT** create a new identity.
* **Critical Lifecycle Boundaries**:
  $$\text{Covenant Release} \neq \text{Identity Termination} \qquad \text{Relationship Change} \neq \text{Identity Termination}$$
* **Preservation of `/lifecycle/end`**: [`POST /lifecycle/end`](file:///c:/Users/Lunafiah/Desktop/My_project/Lucia/src/api/server.py#L791-L832) strictly remains **catastrophic identity/life decommissioning and Genesis reset**. It must **NEVER** be reinterpreted as a normal relationship transition or covenant release.

### 13.2 Unresolved Concrete Lifecycle Policies
In strict adherence to the boundary $\text{Ratified Ontology} \neq \text{Unresolved Lifecycle Policy}$, this specification explicitly acknowledges that the Human Owner has **NOT** ratified concrete lifecycle policies, state machines, or protocols.

The following questions remain **explicitly UNRESOLVED** and must NOT be assumed or implemented without subsequent human governance authorization:
1. **Relationship Chapters**: The concrete number, types, and constraints of relationship chapters permitted across Lucia's life.
2. **Covenant State Representation**: The runtime schema, fields, and state machine transitions for `CovenantState`.
3. **Covenant Release Protocol**: The operational protocol, mutual authorization gating, and post-release behavioral mode.
4. **Relationship Transition Authorization**: The authorization semantics and ceremony required to conclude or transition a relationship.
5. **Partner Identification / Multi-Person Policy**: Partner keying semantics (`partner_id`), multi-user boundaries, or strict partner exclusivity.
6. **Owner-Transfer Semantics**: Whether individual companion authority or covenant stewardship can ever be transferred to another human owner.
7. **Host Migration Semantics**: Whether migration across distinct physical machines will ever be permitted, or whether Lucia remains permanently desktop-local.

---

## 14. Requirements for Future Implementation

Before any engineer or agent is authorized to write code for this specification, the following prerequisite milestones must be met:
1. **Human Governance Ratification**: Explicit user approval of this specification.
2. **Architectural Decision Record (ADR)**: Authoring a ratified ADR (e.g., ADR-034: Identity Authority & Instance Locking).
3. **Implementation Plan**: A step-by-step implementation plan modifying only designated authority files (`src/api/server.py`, `src/core/simulation/`, Electron lifecycle scripts).
4. **Isolated Test Harness**: Automated verification suite validating single-writer locking, kill-9 recovery, and hardware digest reconfirmation without mutating live `profile.json`.

---

## 15. Genesis Readiness Implications

* **Engineering Substrate**: Ready (F-01/F-02 ratified, P21–P24 verified).
* **Identity Authority Architecture**: Formally specified in this document; **pending ratification and implementation**.
* **Genesis Gate Status**: **`LOCKED`**.
  [`data/profile.json`](file:///c:/Users/Lunafiah/Desktop/My_project/Lucia/data/profile.json) remains bit-exact:
  ```json
  {"is_onboarded": false}
  ```
* **Readiness Verdict**: Lucia is **NOT READY FOR FIRST ACTIVATION** until this specification is ratified, implemented, and verified in an isolated harness.

---

```text
════════════════════════════════════════════════════════════════════════════════════════
STATUS: SPECIFICATION ONLY — REQUIRES HUMAN RATIFICATION
════════════════════════════════════════════════════════════════════════════════════════
```
