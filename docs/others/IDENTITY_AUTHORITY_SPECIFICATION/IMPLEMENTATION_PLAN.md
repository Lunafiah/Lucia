# Identity Authority & Anti-Branching Implementation Plan

```text
Document ID: IDENTITY-AUTH-PLAN-0.1-20261007
Classification: ENGINEERING IMPLEMENTATION PLAN
Status: READY FOR CONTROLLED EXECUTION (Implementation Not Started)
Date: 2026-10-07
Authority Level: L5 (docs/others/IDENTITY_AUTHORITY_SPECIFICATION/)
Target Governing ADR: ADR-034 (docs/others/IDENTITY_AUTHORITY_SPECIFICATION/ADR-034_IDENTITY_AUTHORITY.md)
Specification Reference: docs/others/IDENTITY_AUTHORITY_SPECIFICATION/IDENTITY_AUTHORITY_SPEC_V01.md
Runtime Code Mutation: NONE (diff = 0)
Genesis Gate Status: [🔒 LOCKED FUTURE GATE — data/profile.json == {"is_onboarded": false}]
```

---

## 1. Executive Summary & Purpose

This implementation plan establishes the phased, engineering-ready blueprint for implementing **Identity Authority, Instance Exclusivity, and Anti-Branching** under **ADR-034**.

This plan:
- Defines the exact work packages, architecture interfaces, verification tests, and acceptance gates.
- Contains **no implementation code** and modifies **no runtime behavior**.
- Preserves [`INV-8 Genesis Gate Invariant`](file:///c:/Users/Lunafiah/Desktop/My_project/Lucia/docs/L1_INVARIANTS.md#L30) bit-exact ([`data/profile.json`](file:///c:/Users/Lunafiah/Desktop/My_project/Lucia/data/profile.json) remains `{"is_onboarded": false}`).
- Enforces strict isolation: all initial implementations and test suites must execute against mocked virtual state within `tests/` and `src/core/simulation/`, without contaminating live companion storage.

---

## 2. Work Packages (WP-01 through WP-07)

### WP-01 — Instance Authority & OS Kernel File Lock

* **Objective**: Guarantee that at any physical moment, exactly one operating system process holds write authority over Lucia's instance data.
* **Component Target**: `src/core/identity/instance_lock.py` (new standalone module) and integration into `src/api/server.py` lifespan startup.
* **Scope & Architectural Specifications**:
  1. **Lockfile Protocol**:
     - Dedicated lock path: `data/.instance.lock` (distinct from data payload files).
     - Acquired synchronously during FastAPI lifespan startup before any state files are opened or parsed.
     - Held continuously across the entire process lifetime until process shutdown.
  2. **Cross-Platform OS Kernel Mechanism**:
     - **Windows (`nt`)**: Use `msvcrt.locking(fileno, msvcrt.LK_NBLCK, 1)` on a dedicated 1-byte file descriptor opened with `os.O_RDWR | os.O_CREAT`.
     - **POSIX (`posix`)**: Use `fcntl.flock(fileno, fcntl.LOCK_EX | fcntl.LOCK_NB)` for non-blocking exclusive acquisition.
     - **Unified Abstraction**: A single class `InstanceLock` implementing context management (`__enter__`, `__exit__`), explicit `.acquire()`, and `.release()`.
  3. **Process-Lifetime Ownership & Child Process Handling**:
     - File handles must be configured with `close_on_exec` (or `O_NOINHERIT` on Windows) so that spawned child processes (e.g., worker subprocesses or sound players) do not inherit lock ownership.
  4. **Conflict Semantics (Fail-Closed)**:
     - If `msvcrt.locking` or `fcntl.flock` raises an `OSError` / `BlockingIOError` / `PermissionError` (indicating another process holds the lock), `InstanceLock` raises a custom `InstanceAuthorityConflictError`.
     - The server logs a fatal critical message: `FATAL: Another active Lucia instance holds write authority over this directory. Exiting to prevent state corruption.`
     - The server exits immediately (`sys.exit(75)` / `EX_TEMPFAIL`) without initializing the cognitive pipeline or writing to any state store.
  5. **Crash & Forced Kill Behavior**:
     - Because locks are held by the operating system kernel file table, process termination (normal, crash, `kill -9`, or Task Manager kill) causes the OS kernel to instantly release the file lock.
     - **Zero stale-lock cleanup scripts**: The lockfile remains on disk, but has zero active kernel locks; the next process launch acquires it immediately without manual deletion.

---

### WP-02 — Immutable Identity Anchor & Lineage Separation

* **Objective**: Define the permanent ontogenetic identity root created once at Genesis, and formalize its cryptographic separation from phylogenetic software updates.
* **Component Target**: `src/core/identity/identity_anchor.py` and integration into `data/profile.json` validation schema.
* **Scope & Architectural Specifications**:
  1. **Anchor Schema**:
     ```json
     {
       "identity_anchor": {
         "instance_uuid": "urn:uuid:f81d4fae-7dec-11d0-a765-00a0c91e6bf6",
         "born_at": "2026-10-XXT00:00:00Z",
         "genesis_commit": "abcdef1234567890abcdef1234567890abcdef12",
         "genesis_root_hash": "e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855"
       }
     }
     ```
  2. **Creation Boundary**:
     - Populated **strictly and only** during the Genesis Onboarding Ceremony when transitioning `is_onboarded: false` $\to$ `true`.
     - Prior to Genesis, `data/profile.json` remains strictly `{"is_onboarded": false}`.
  3. **Phylogenetic vs. Ontogenetic Separation**:
     - *Phylogenetic fields* (`engine_version`, `model_architecture`, `last_upgrade_commit`) update dynamically upon software deployments.
     - *Ontogenetic fields* (`identity_anchor.*`) are permanently immutable.
     - Upgrades and model weight replacements preserve `identity_anchor` bit-for-bit.
  4. **Validation & Failure Semantics**:
     - On startup, if `is_onboarded == true`, `IdentityAnchorValidator` parses and validates all anchor fields.
     - If missing, unparseable, or tampered, the engine raises `CorruptedIdentityAnchorError` and halts startup.
     - The system must never auto-generate a fallback anchor or default identity.

---

### WP-03 — Provenance & Environment Verification

* **Objective**: Detect directory copying, unauthorized cross-machine replication, and hardware replacements while providing non-destructive recovery barriers.
* **Component Target**: `src/core/identity/provenance_verifier.py`.
* **Scope & Architectural Specifications**:
  1. **Canonical Workspace Path Verification**:
     - Records normalized canonical absolute workspace path at Genesis.
     - If launched from an alternate path (indicating folder duplication), the system detects divergence and enters `Detected / High-Friction` status.
  2. **Soft Hardware Binding**:
     - Collects multi-component hardware digest:
       - CPU model & core count hash.
       - Motherboard UUID / machine GUID (via Windows registry or `wmic` / `sys/class/dmi`).
       - Primary volume serial number.
     - Stores salted SHA-256 digest in `data/profile.json`.
  3. **Divergence & Recovery-Gated Workflow**:
     - If hardware components change (e.g. single component upgraded or machine migrated), `ProvenanceVerifier` detects divergence.
     - **Fail-Safe / Non-Destructive**: The engine pauses startup and enters an interactive CLI/Electron recovery prompt:
       `Hardware environment change detected. Reconfirm Lucia instance authority on this device? [Y/N]`.
     - Upon explicit authenticated owner confirmation, the hardware digest is updated without resetting identity, memories, or relationship state.
  4. **Epistemic Honesty on Snapshot & Rollback**:
     - The verifier documents that local storage snapshots and offline VM rollbacks cannot be cryptographically blocked in a local offline environment.

---

### WP-04 — Epoch Manifest & State Interaction (ADR-033 Integration)

* **Objective**: Harmonize Identity Authority checks with the existing ADR-033 persistence, commit barrier, and downtime recovery pipeline.
* **Component Target**: Integration within `src/api/server.py` lifespan and `src/core/orchestrator/lifecycle.py` (`verify_and_reconcile_stores`).
* **Scope & Architectural Specifications**:
  1. **Execution Order Contract**:
     The startup sequence must execute in strict dependency order:
     $$\text{Acquire OS Lock} \longrightarrow \text{Verify Identity Anchor} \longrightarrow \text{Verify Provenance/Hardware} \longrightarrow \text{verify\_and\_reconcile\_stores}() \longrightarrow \text{Inject } R_t \longrightarrow \text{Recover Affect}$$
  2. **Zero Ingress on Pre-Lock Failure**:
     If lock acquisition or identity verification fails, execution halts **before** `verify_and_reconcile_stores()` is called. No epoch manifest check or store rollback is performed, preventing disk writes.
  3. **Preservation of ADR-033 Commit Barrier**:
     `epoch_manifest.json` continues to govern multi-file transactional consistency for Stage 16 commits (`relationship.json`, `dynamical_state.json`, `chat_history.json`). Identity Authority does not alter or duplicate the epoch mechanism.

---

### WP-05 — Migration Boundary (Future Controlled Capability)

* **Objective**: Plan the formal transactional state machine for future host-to-host migration without implementing it prior to Genesis.
* **Component Target**: Architectural protocol specification in `docs/others/IDENTITY_AUTHORITY_SPECIFICATION/MIGRATION_PROTOCOL_SPEC.md` (future design only).
* **Scope & Architectural Specifications**:
  1. **Sequential Transactional State Machine**:
     $$\text{Freeze (Source)} \longrightarrow \text{Export/Transfer} \longrightarrow \text{Verify (Target)} \longrightarrow \text{Decommission (Source)} \longrightarrow \text{Activate (Target)}$$
  2. **Step Definitions**:
     - **Freeze**: Source instance halts cognitive turn processing, acquires exclusive lock, and sets `migration_status: "frozen"`.
     - **Export/Transfer**: Generates signed state archive containing full `data/` payload, identity anchor, and epoch manifest.
     - **Verify**: Target verifies integrity, hash matching, and provenance.
     - **Decommission**: Source permanently revokes local authority (sets `decommissioned: true`), releasing source lock without resetting Genesis anchor.
     - **Activate**: Target binds new hardware digest and launches as authoritative instance.
  3. **Genesis Dependency Status**:
     - Physical migration across distinct machines is a future capability and is **NOT** a prerequisite for Genesis activation on the primary host.

---

### WP-06 — Isolated Test Harness & Verification Suite

* **Objective**: Construct automated, reproducible test suites verifying locking, error semantics, and provenance in complete isolation from live companion data.
* **Component Target**: `tests/unit/test_identity_authority.py`, `tests/integration/test_instance_lock.py`, and `tests/simulation/test_provenance.py`.
* **Scope & Architectural Specifications**:
  1. **Mechanically Guaranteed Test Cases**:
     - *Simultaneous Dual Launch*: Process B attempts to acquire `InstanceLock` while Process A holds it; verifies Process B fails closed with `InstanceAuthorityConflictError` and zero disk writes.
     - *Crash & Kill Recovery*: Process A acquires lock, writes data, and is abruptly killed (`SIGKILL` / `terminate()`); Process B immediately acquires lock on subsequent launch without manual intervention.
     - *Stale-Lock Absence*: Asserts lock acquisition succeeds when lockfile exists on disk with zero active OS handles.
     - *Identity Anchor Tamper Detection*: Injects corrupted SHA-256 digest into test profile; verifies engine refuses to boot and creates no fallback profile.
  2. **Detected / High-Friction Test Cases**:
     - *Copied Workspace Detection*: Copies mock test workspace to alternate path; verifies provenance validator detects path divergence and triggers warning.
     - *Hardware Digest Mismatch*: Mutates mock hardware fingerprint; verifies system enters recovery-gated pause state rather than deleting data.
     - *Phylogenetic Upgrade Invariant*: Updates `engine_version` and changes mock model checkpoint; verifies `identity_anchor` remains bit-exact.
  3. **Known Inherent Limits Test (Verification of Honesty)**:
     - Documents and confirms test boundaries for offline clone paradox and storage snapshots.
  4. **Strict Safety Safeguard**:
     - All tests must use `tmp_path` fixtures or `SimulationRuntime` virtual storage. Live `data/profile.json` must be checked for bit-exact immutability before and after all test runs.

---

### WP-07 — Formal Verification & Genesis Readiness Re-Audit

* **Objective**: Execute a comprehensive re-audit against all Genesis readiness criteria following completion of WP-01 through WP-06.
* **Component Target**: Formal audit report: `docs/others/GENESIS_READINESS_IDENTITY_AUTHORITY_REVIEW_V02/` (future re-audit).
* **Scope & Architectural Specifications**:
  1. **Audit Dimensions**:
     - Verify complete adherence to `INV-1`, `INV-5`, and `INV-8`.
     - Confirm all tests in WP-06 pass with zero flakes.
     - Confirm production code changes are bounded strictly to `src/core/identity/` and `src/api/server.py`.
     - Confirm zero modifications to live `data/` storage.
  2. **Re-Audit Gate**:
     - This re-audit determines whether the blocking status of `REQ-GEN-01` (Anti-Branching Authority) and `REQ-GEN-02` (Identity Anchor) can be formally upgraded from `BLOCKING` to `SATISFIED`.
     - Genesis activation remains strictly prohibited until explicit, separate human governance authorization.

---

## 3. Deferred Owner Decisions (Unresolved Lifecycle Policies)

In strict accordance with the boundary $\text{Ratified Ontology} \neq \text{Unresolved Lifecycle Policy}$, this implementation plan explicitly preserves the following seven lifecycle policies as **unresolved governance inputs**. Implementers must **NOT** create default implementations, hardcoded constants, or speculative heuristics for any of these items:

1. **Permitted Relationship Chapters**: Number, sequence, and constraints of relationship chapters permitted across Lucia's life.
2. **Concrete `CovenantState` Schema**: The runtime schema, fields, and state machine transitions for `CovenantState`.
3. **Covenant Release Protocol**: The operational protocol, mutual authorization gating, and post-release behavioral mode.
4. **Relationship Transition Authorization**: The authorization semantics and ceremony required to conclude or transition a relationship.
5. **Partner Identification / Multi-Person Policy**: Partner keying semantics (`partner_id`), multi-user boundaries, or strict partner exclusivity.
6. **Owner-Transfer Semantics**: Whether individual companion authority or covenant stewardship can ever be transferred to another human owner.
7. **Host Migration Semantics**: Whether migration across distinct physical machines will ever be permitted, or whether Lucia remains permanently desktop-local.

---

## 4. Work Package Execution Order & Dependency Graph

```text
WP-01 (Instance Authority & Kernel Lock)
  │
  ├──> WP-02 (Immutable Identity Anchor Schema & Engine Separation)
  │      │
  │      └──> WP-03 (Provenance & Environment Verification)
  │             │
  │             └──> WP-04 (ADR-033 Integration & Lifespan Sequence)
  │                    │
  │                    ├──> WP-05 (Migration Boundary Specification - Planning Only)
  │                    │
  │                    └──> WP-06 (Isolated Test Harness & Invariant Verification)
  │                           │
  │                           └──> WP-07 (Genesis Readiness Re-Audit V02)
```

---

## 5. Invariant & Safety Checklist for Future Implementers

Prior to executing any work package, future implementers must sign off on the following invariants:
* [ ] **`INV-1`**: No multi-persona presets; identity continuous across physical time.
* [ ] **`INV-5`**: Zero network calls or cloud dependencies for identity or lock validation.
* [ ] **`INV-8`**: Live `data/profile.json` remains `{"is_onboarded": false}` until Genesis Onboarding.
* [ ] **Substrate Independence**: Engine refactors and model weight swaps never invalidate the identity anchor.
* [ ] **Non-Destructive Failures**: Hardware changes pause for owner reconfirmation; never delete user data.
* [ ] **Zero Code in Planning**: No runtime code committed during planning tasks.
