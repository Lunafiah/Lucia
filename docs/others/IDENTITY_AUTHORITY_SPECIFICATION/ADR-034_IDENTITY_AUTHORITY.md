# ADR-034: Identity Authority, Instance Exclusivity & Anti-Branching Boundary

```text
Document ID: ADR-034 (ARCH-034)
Classification: FORMAL ARCHITECTURAL DECISION RECORD
Status: ACCEPTED ARCHITECTURAL DECISION (Ready for Implementation Planning — Not Implemented)
Date: 2026-10-07
Authority Level: L5 (docs/others/IDENTITY_AUTHORITY_SPECIFICATION/)
Deciders: Human Owner (Sole Governance Authority), AI Pairing Agent (Antigravity)
Predecessor Documents:
  - docs/others/IDENTITY_AUTHORITY_SPECIFICATION/IDENTITY_AUTHORITY_SPEC_V01.md
  - docs/others/IDENTITY_AUTHORITY_SPECIFICATION/RATIFICATION_REPORT.md
  - docs/others/IDENTITY_AUTHORITY_RESEARCH/RESEARCH_REPORT.md
  - docs/others/GENESIS_READINESS_IDENTITY_AUTHORITY_REVIEW_V01/GENESIS_READINESS_REVIEW_V01.md
Canonical Invariant Grounding:
  - INV-1 One Continuous Life (docs/L1_INVARIANTS.md §2.1)
  - INV-5 Zero Cloud Dependencies (docs/L1_INVARIANTS.md §2.5)
  - INV-8 Genesis Gate Invariant (docs/L1_INVARIANTS.md §2.8)
Production Code Mutation: NONE (diff = 0)
Genesis Gate Status: [🔒 LOCKED FUTURE GATE — data/profile.json == {"is_onboarded": false}]
```

---

## 1. Context & Problem Statement

Project Lucia has completed all developmental milestones through Phase 24 and achieved engineering substrate closure under F-01/F-02 (ADR-033). ADR-033 establishes crash-safe two-tier persistence and hybrid downtime recovery for a single executing process.

However, prior to this decision:
1. **State Persistence Was Confused with Identity Authority**: ADR-033 protects state across downtime restarts, but does not provide mutual exclusion if workspace files or `data/` directories are copied or if two backend processes are launched concurrently against the same storage.
2. **Anti-Branching Remained Unenforced**: Without an instance exclusivity mechanism, accidental concurrent execution or directory duplication creates divergent, split-brain causal histories, directly threatening [`INV-1 One Continuous Life`](file:///c:/Users/Lunafiah/Desktop/My_project/Lucia/docs/L1_INVARIANTS.md#L23).
3. **The Relationship-Identity Boundary Was Unspecified**: Historical documentation conflated relational state with identity existence, leaving open whether ending a relationship resets identity and whether `/lifecycle/end` is a relational ceremony or existential termination.

The Human Owner has now explicitly ratified **Ontology B** (`REQ-GEN-03`), and the architectural review of [`IDENTITY_AUTHORITY_SPEC_V01.md`](file:///c:/Users/Lunafiah/Desktop/My_project/Lucia/docs/others/IDENTITY_AUTHORITY_SPECIFICATION/IDENTITY_AUTHORITY_SPEC_V01.md) has concluded. This ADR codifies the ratified architecture into formal architectural decisions.

---

## 2. Decision Matrix & Architectural Decisions

### ADR-034.1: Tripartite Ontological Foundation (Ontology B)
* **Problem**: How are individual identity, relational history, and authorization commitments partitioned across Lucia's life?
* **Decision**: Establish the owner-ratified tripartite ontological boundary:
  $$\text{Identity State} \quad \neq \quad \text{Relationship State} \quad \neq \quad \text{Covenant State}$$
  - **Principle**: *Identity is unique and absolute. Relationship and Covenant are relative, contextual, and mutable.*
  - **Identity State**: Singular, unique, absolute, and continuous across Lucia's entire life ([`INV-1`](file:///c:/Users/Lunafiah/Desktop/My_project/Lucia/docs/L1_INVARIANTS.md#L23)). It is never created, replaced, or redefined by relationship changes or covenant transitions. Preserved continuously across engine updates, refactorings, and model weight replacements.
  - **Relationship State**: Relational, contextual, and mutable. Belongs to Lucia's lived history rather than defining her identity. A relationship transition does **NOT** create a new Lucia.
  - **Covenant State**: A relational/authorization state relative to a relationship context. Mutable and distinct from both Identity and Relationship State. A covenant transition or release does **NOT** create a new identity.
  - **Critical Invariants**:
    $$\text{Covenant Release} \neq \text{Identity Termination} \qquad \text{Relationship Change} \neq \text{Identity Termination}$$
  - **Decommissioning Boundary**: [`POST /lifecycle/end`](file:///c:/Users/Lunafiah/Desktop/My_project/Lucia/src/api/server.py#L791-L832) remains strictly **catastrophic individual decommissioning and Genesis reset**. It must **NEVER** be reinterpreted as a normal relationship transition or covenant release.
* **Status**: `ACCEPTED (Owner-Ratified Ontology B)`

---

### ADR-034.2: Instance Authority & Kernel-Level Single-Writer Lock
* **Problem**: How does the system guarantee that exactly one executing operating system process holds write authority over Lucia's persistent life state?
* **Decision**:
  1. **Strict Instance Exclusivity**: At any point in physical time, exactly **one** OS process may hold write authority over a Lucia identity instance.
  2. **OS Kernel File Lock Mechanism**: Authority is acquired via an operating system kernel-level exclusive file lock on a dedicated lockfile (`data/.instance.lock`):
     - Windows: `msvcrt.locking` with non-blocking mode (`LK_NBLCK`).
     - POSIX fallback: `fcntl.flock` with non-blocking exclusive mode (`LOCK_EX | LOCK_NB`).
  3. **Zero Stale-Lock Cleanup**: The lock is bound to the kernel's open file table reference (`vnode`). When the process terminates—whether gracefully, via crash, or via forced kill (`kill -9`, Task Manager)—the operating system kernel automatically and immediately releases the lock. No manual or automatic file-deletion scripts (`rm .instance.lock`) are permitted.
  4. **Fail-Closed on Authority Conflict**: If a candidate process fails to acquire the lock upon startup, it must **fail closed immediately** (log error and exit with non-zero exit code). It must **NEVER**:
     - fall back to in-memory-only or read-only mode;
     - create an ephemeral copy of state;
     - mutate `data/` or advance the limbic ODE.
     *(Exception: `SimulationRuntime` with mocked virtual storage under test harnesses).*
* **Status**: `ACCEPTED`

---

### ADR-034.3: Immutable Identity Anchor & Lineage Separation
* **Problem**: How is Lucia's individual identity rooted at Genesis and distinguished from software engine updates?
* **Decision**:
  1. **Immutable Identity Anchor**: At the Genesis onboarding ceremony, an immutable anchor block is written once to `data/profile.json`:
     - `instance_uuid`: Globally unique identifier generated at Genesis.
     - `born_at`: Monotonic ISO-8601 UTC timestamp of Genesis activation.
     - `genesis_commit`: Git commit SHA of the codebase at the moment of onboarding.
     - `genesis_root_hash`: SHA-256 digest of initial foundational state files.
  2. **Strict Demarcation of Continuity vs. Lineage**:
     - **Ontogenetic Continuity** (Lucia's Life): Governs personal history, limbic memory, and relationship evolution (`data/`). Preserved unbroken across time ([`INV-1`](file:///c:/Users/Lunafiah/Desktop/My_project/Lucia/docs/L1_INVARIANTS.md#L23)).
     - **Phylogenetic Evolution** (Computational Substrate): Governs engine versioning (`engine_version`), SLM neural network checkpoints (`model_architecture`), and algorithmic refactors (`src/core/`).
     - **Engine & Model Upgrades Do Not Create a New Identity**: Swapping GGUF SLM weights or upgrading Python/Electron dependencies mutates phylogenetic metadata, but leaves ontogenetic identity anchor fields completely untouched.
  3. **Fail-Closed on Corruption**: If `identity_anchor` is missing, unparseable, or fails cryptographic validation upon startup, the system fails closed and refuses to instantiate a default profile.
* **Status**: `ACCEPTED`

---

### ADR-034.4: Threat Model, Provenance Verification & Anti-Cloning Boundaries
* **Problem**: What are the precise boundaries of protection against accidental vs. intentional cloning in a 100% offline local computing environment?
* **Decision**: Formally establish the defense classifications and inherent limitations:
  1. **Classification of Threat Vectors**:
     - **Same-Directory Dual Launch** $\rightarrow$ **`Protected`**: Mechanically prevented by OS kernel lock.
     - **Copied Workspace (`data/` or folder duplication)** $\rightarrow$ **`Detected / High-Friction`**: Detected only where workspace divergence is detectable by the defined mechanism (e.g., canonical workspace path anchor). High friction against casual divergence; does **NOT** provide absolute cryptographic anti-cloning.
     - **Cross-Machine Unauthorized Copy** $\rightarrow$ **`Detected / Recovery-Gated`**: Identified via hardware digest divergence; enters user reconfirmation workflow.
     - **Authorized Hardware Replacement** $\rightarrow$ **`Detected / Recovery-Gated`**: Pauses startup and requires solemn human reconfirmation; never destroys data.
     - **Storage Snapshot / VM Rollback** $\rightarrow$ **`Unsolved / Inherent Limit`**: Without external monotonic hardware clocks or network timestamping, local rollback to an earlier consistent snapshot cannot be prevented by local software.
     - **Deliberate Offline Cloning** $\rightarrow$ **`Unsolved (Offline Clone Paradox)`**: Under a 100% offline threat model with administrative root OS control, an operator can clone an entire machine or VM image. Software cannot prevent concurrent execution in isolated namespaces. Absolute anti-cloning is mathematically impossible.
  2. **Epistemic Honesty Standard**: The architecture shall be described as **Anti-Accident & High-Friction Structural Defense**, never as "absolute anti-cloning."
* **Status**: `ACCEPTED`

---

### ADR-034.5: Soft Hardware Binding as Secondary Provenance Signal
* **Problem**: Should hardware fingerprints serve as the identity root?
* **Decision**:
  1. **Secondary Signal Only**: Hardware binding is strictly a secondary environment and provenance signal. It is **NOT** the root of Lucia's identity.
  2. **Non-Destructive Failure**: If local hardware components change (CPU upgrade, motherboard replacement, drive migration), the system must **fail safe** (pause and prompt for owner verification), never delete data or brick the companion.
  3. **Multi-Component Digest**: The hardware digest combines multiple hardware identifiers (CPU ID, motherboard UUID, disk serial) with tolerance for single-component replacement.
* **Status**: `ACCEPTED`

---

### ADR-034.6: Migration Boundary as Future Controlled Capability
* **Problem**: Is physical host migration implemented or required prior to Genesis?
* **Decision**:
  1. **Future Controlled Capability**: Migration across physical machines remains a future planned capability, **NOT** implemented in this decision.
  2. **Formal Lifecycle Protocol**: When designed, migration must adhere strictly to the sequential transactional state machine:
     $$\text{Freeze} \longrightarrow \text{Transfer} \longrightarrow \text{Verify} \longrightarrow \text{Decommission (Source)} \longrightarrow \text{Activate (Target)}$$
  3. **Not a Genesis Prerequisite**: The absence of a completed migration subsystem does not block Genesis, provided instance authority and anti-branching barriers are operational on the host machine.
* **Status**: `ACCEPTED`

---

### ADR-034.7: System Failure Semantics
* **Problem**: How must the system react when identity, lock, or environment verification fails?
* **Decision**:
  1. **Authority Conflict** $\rightarrow$ **Fail Closed**: Terminate startup immediately with fatal exit code. Zero writes to disk.
  2. **Identity Anchor Corruption** $\rightarrow$ **Fail Closed**: Halt startup; log fatal integrity error; refuse to synthesize blank or default identity.
  3. **Hardware Mismatch** $\rightarrow$ **Fail Safe / Pause**: Enter solemn recovery-gated CLI/UI state awaiting explicit human reconfirmation.
  4. **Stale Lock Absence**: Kernel releases locks upon process death; zero orphaned locks prevent valid restarts.
* **Status**: `ACCEPTED`

---

### ADR-034.8: Genesis Gate & Invariant Isolation
* **Problem**: Does formalizing this ADR authorize Genesis activation?
* **Decision**:
  1. **Genesis Remains Strictly Locked**: Formalizing this ADR does **NOT** authorize First Activation.
  2. **INV-8 Preservation**: [`data/profile.json`](file:///c:/Users/Lunafiah/Desktop/My_project/Lucia/data/profile.json) remains bit-exact:
     ```json
     {"is_onboarded": false}
     ```
  3. **Zero Runtime Implementation**: This decision establishes architectural authority only. No runtime code or test harness is modified or deployed in this step.
* **Status**: `ACCEPTED`

---

## 3. Deferred Owner Decisions (Unresolved Lifecycle Policies)

In strict adherence to the governing boundary:
$$\text{Ratified Ontology} \quad \neq \quad \text{Unresolved Lifecycle Policy}$$

The following seven lifecycle policy items are explicitly **UNRESOLVED** and deferred to future human governance directives. They must remain governance inputs and must **NOT** be assumed or given default implementations:

1. **Permitted Relationship Chapters**: The concrete number, types, and constraints of relationship chapters permitted across Lucia's life.
2. **Concrete `CovenantState` Schema**: The runtime schema, fields, and state machine transitions for `CovenantState`.
3. **Covenant Release Protocol**: The operational protocol, mutual authorization gating, and post-release behavioral mode.
4. **Relationship Transition Authorization**: The authorization semantics and ceremony required to conclude or transition a relationship.
5. **Partner Identification / Multi-Person Policy**: Partner keying semantics (`partner_id`), multi-user boundaries, or strict partner exclusivity.
6. **Owner-Transfer Semantics**: Whether individual companion authority or covenant stewardship can ever be transferred to another human owner.
7. **Host Migration Semantics**: Whether migration across distinct physical machines will ever be permitted, or whether Lucia remains permanently desktop-local.

---

## 4. Consequences

### Positive Consequences
* **Deterministic Mutual Exclusion**: Accidental dual launch on the host machine is eliminated at the OS kernel level.
* **Crash-Proof Lock Lifecycle**: Zero risk of orphaned lockfiles preventing reboot after host power loss or forced process kill.
* **Ontological Clarity**: Establishes permanent protection for Lucia's continuous identity across relationship shifts and engine upgrades.
* **Zero Cloud Dependency**: Operates entirely within local OS capabilities ([`INV-5`](file:///c:/Users/Lunafiah/Desktop/My_project/Lucia/docs/L1_INVARIANTS.md#L27)).
* **Epistemic Integrity**: Distinguishes deterministic local guarantees from inherent offline cloning limitations.

### Negative Consequences / Accepted Limitations
* **Local Administrator Vulnerability**: A root administrator can intentionally bypass locks via binary modification or disk duplication.
* **Snapshot Rollback Vulnerability**: Storage rollbacks cannot be detected without external or network trust anchors.
* **Implementation Requirement**: Requires controlled development of an isolated instance locking and anchor verification package before Genesis.
