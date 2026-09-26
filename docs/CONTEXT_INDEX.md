# Lucia — Context Architecture Index & Retrieval Map

> **Lightweight Retrieval Routing & Minimal Sufficient Context Map for AI Coding Agents**  
> *Authoritative Context Routing Index — Post-Phase 21*  
> **Status:** Canonical Context Index | **Scope:** Repository-Wide Context Routing

---

## 1. Context Architecture Overview (Logical Layers L0–L6)

Lucia organizes context into **logical conceptual tiers (L0–L6)** to deliver **minimum sufficient context** for any development task, avoiding both under-informed edits and catastrophic context window saturation.

> [!IMPORTANT]
> `L0–L6` are **logical context layers**, not physical filesystem directories.  
> They define how an AI agent should progressively pull authority and context depending on task classification.

```text
┌────────────────────────────────────────────────────────────────────────┐
│                      LUCIA LOGICAL CONTEXT LAYERS                      │
├────────────────────────────────────────────────────────────────────────┤
│ L0: Mission & Front Door     ──► README.md                             │
│ L1: Invariant Ledger          ──► docs/L1_INVARIANTS.md, AGENTS.md §2   │
│ L2: Operational Governance    ──► AGENTS.md, docs/00_PROJECT_OVERVIEW.md│
│ L3: Technical Canon & ADRs   ──► docs/ARCHITECTURE.md                  │
│ L4: Navigation & Index Map   ──► docs/CONTEXT_INDEX.md,                │
│                                  docs/DOCUMENTATION_INDEX.md           │
│ L5: Domain / Historical Specs ──► docs/specs/**, docs/research/**, tests/evaluation/**│
│ L6: Production Codebase       ──► src/core/**, electron/**, config/**   │
└────────────────────────────────────────────────────────────────────────┘
```

---

## 2. Minimal Sufficient Context Routing by Task Type

Before reading large files or starting implementation, determine the task type and load **only** the required context layers:

| Task Type | Primary Context (Must Read) | Secondary / Reference Context | What NOT to Load (Avoid Context Bloat) |
|---|---|---|---|
| **Bug Fix / Core Logic** | `docs/L1_INVARIANTS.md`<br/>`src/core/<subsystem>/` | `docs/ARCHITECTURE.md` (§ relevant mechanism) | Historical specs in `docs/specs/**`<br/>Research evaluation reports |
| **Research / Evaluation** | `AGENTS.md` (§0, §6)<br/>`docs/L1_INVARIANTS.md` (§6)<br/>Target spec in `docs/specs/` or `docs/research/` | `tests/evaluation/phaseXX/`<br/>`docs/research/` Reviewer Pack | Production `electron/**`<br/>Active user persistence files |
| **UI / Presentation / Desktop** | `docs/L1_INVARIANTS.md` (§2 INV-1, INV-7)<br/>`docs/ARCHITECTURE.md` (§3.6, §4)<br/>`electron/` target module | `docs/specs/lucia-phase7-UI_refractoring/` | Math derivations in `docs/ARCHITECTURE.md`<br/>BPTT consolidation details |
| **Architecture / ADR Gate** | `docs/L1_INVARIANTS.md`<br/>`AGENTS.md` (§7)<br/>`docs/ARCHITECTURE.md` (§8 ADR ledger) | `docs/00_PROJECT_OVERVIEW.md` (§3) | Historical phase 1–6 scratch specs<br/>UI assets |
| **Governance / Documentation** | `AGENTS.md` (§3)<br/>`docs/DOCUMENTATION_INDEX.md`<br/>`docs/CONTEXT_INDEX.md` | Target documentation file | Unrelated Python test suites |

---

## 3. Canonical Authority & Subject Retrieval Table

When answering questions or designing changes, look up the canonical source of truth here:

| Domain / Subject | Canonical Document & Section | Quick Summary / Scope |
|---|---|---|
| **Universal Invariants** | [`docs/L1_INVARIANTS.md`](file:///c:/Users/Lunafiah/Desktop/My_project/Lucia/docs/L1_INVARIANTS.md) | The 8 core invariant rules, limbic constraints, locking rules. |
| **Agent Operating Rules** | [`AGENTS.md`](file:///c:/Users/Lunafiah/Desktop/My_project/Lucia/AGENTS.md) | Research-first governance, decision sequence, commit rules. |
| **Project Truth & Roadmap** | [`docs/00_PROJECT_OVERVIEW.md`](file:///c:/Users/Lunafiah/Desktop/My_project/Lucia/docs/00_PROJECT_OVERVIEW.md) | Philia philosophy, 24-subsystem health matrix, milestone status. |
| **Cognitive Pipeline (S1–S16)** | [`docs/ARCHITECTURE.md`](file:///c:/Users/Lunafiah/Desktop/My_project/Lucia/docs/ARCHITECTURE.md) §2, ADR-025 | 16-stage cognitive turn sequence executed by `CognitiveOrchestrator`. |
| **Limbic MT-LNN ODE (200ms)** | [`docs/ARCHITECTURE.md`](file:///c:/Users/Lunafiah/Desktop/My_project/Lucia/docs/ARCHITECTURE.md) §3.2, ADR-026 | Coupled fast/slow LNN ODE formulation and Lyapunov dissipative bounds. |
| **Homeostasis & Somatic Markers**| [`docs/ARCHITECTURE.md`](file:///c:/Users/Lunafiah/Desktop/My_project/Lucia/docs/ARCHITECTURE.md) §3.3 | Metabolic budget, Cognitive Load $\mathcal{C}$, Energy $\mathcal{E}$, Tension $\mathcal{T}$. |
| **Active Inference & Surprise** | [`docs/ARCHITECTURE.md`](file:///c:/Users/Lunafiah/Desktop/My_project/Lucia/docs/ARCHITECTURE.md) §3.4, ADR-015 | Generative transition model, Free Energy Surprise $\mathcal{S}$, depth $k=2$. |
| **Relational Attractor & Consolidation** | [`docs/ARCHITECTURE.md`](file:///c:/Users/Lunafiah/Desktop/My_project/Lucia/docs/ARCHITECTURE.md) §3.2, §3.4, ADR-028 | Spectral norm bound $\|\mathbf{W}_{\text{rel}}\|_2 \le 0.08$, CPU BPTT `ConsolidationEngine`. |
| **SDM & Affective Recollection** | [`docs/ARCHITECTURE.md`](file:///c:/Users/Lunafiah/Desktop/My_project/Lucia/docs/ARCHITECTURE.md) §3.5, ADR-027 | Kanerva SDM, 60s decay engine, closed-loop slow forcing pulse. |
| **Phase 23 Research & P23-H State** | [`docs/research/P23_HISTORY_CONSOLIDATED.md`](file:///c:/Users/Lunafiah/Desktop/My_project/Lucia/docs/research/P23_HISTORY_CONSOLIDATED.md), [`docs/research/P23-H_FINAL_STATE.md`](file:///c:/Users/Lunafiah/Desktop/My_project/Lucia/docs/research/P23-H_FINAL_STATE.md) | Consolidated P23-A through P23-H history, frozen P23-H kernel state (`3eef803`), and source map. |
| **Phase 23 Reviewer Pack (5-File)** | [`docs/research/P23_REVIEW_01_EXECUTIVE_CONTEXT.md`](file:///c:/Users/Lunafiah/Desktop/My_project/Lucia/docs/research/P23_REVIEW_01_EXECUTIVE_CONTEXT.md) | Minimal 5-document pack for rapid reviewer context ingestion and reconstruction. |
| **Phase 23-I Research Context** | [`docs/research/P23-I_RESEARCH_CONTEXT.md`](file:///c:/Users/Lunafiah/Desktop/My_project/Lucia/docs/research/P23-I_RESEARCH_CONTEXT.md) | Formal research question, epistemic boundaries, candidate avenues, non-implementation mandate. |
| **Lock Hierarchy & Concurrency** | [`docs/ARCHITECTURE.md`](file:///c:/Users/Lunafiah/Desktop/My_project/Lucia/docs/ARCHITECTURE.md) §5.1 | `_turn_lock` $\to$ `_step_lock` $\to$ `_train_lock` $\to$ `_stimulus_lock` $\to$ `_state_lock`. |
| **Desktop / Mascot Mode UI** | [`docs/ARCHITECTURE.md`](file:///c:/Users/Lunafiah/Desktop/My_project/Lucia/docs/ARCHITECTURE.md) §3.6, §4, ADR-008 | Quad-Engine Avatar, bounds math, trackpad cooldown, IPC bridge. |
| **Hardware Tiers (20W Target)** | [`docs/ARCHITECTURE.md`](file:///c:/Users/Lunafiah/Desktop/My_project/Lucia/docs/ARCHITECTURE.md) §6 | CPU_ONLY, LAPTOP, DESKTOP, HIGH_END runtime profiles. |
| **Simulation Runtime** | [`docs/ARCHITECTURE.md`](file:///c:/Users/Lunafiah/Desktop/My_project/Lucia/docs/ARCHITECTURE.md) §7, ADR-011 | `SimClock`, virtual time advancement, ephemeral in-memory storage. |
| **ADR Ledger** | [`docs/ARCHITECTURE.md`](file:///c:/Users/Lunafiah/Desktop/My_project/Lucia/docs/ARCHITECTURE.md) §8 | Full architectural decision records: ADR-001 through ADR-028, DRAFT ADR-029. |
| **Full Spec Catalog** | [`docs/DOCUMENTATION_INDEX.md`](file:///c:/Users/Lunafiah/Desktop/My_project/Lucia/docs/DOCUMENTATION_INDEX.md) | Exhaustive directory of all active and historical phase specifications. |
| **User Operation & Voice Setup** | [`docs/USER_MANUAL.md`](file:///c:/Users/Lunafiah/Desktop/My_project/Lucia/docs/USER_MANUAL.md) | Shortcuts, RVC model setup, hardware configuration. |

---

## 4. Anti-Patterns in Context Retrieval

When retrieving context in Lucia, agents must actively avoid:

1. **Massive Context Ingestion**: Reading all of `docs/specs/**` or full evaluation reports into context for simple bug fixes or local refactors.
2. **Consulting Historical Specs as Active Truth**: Historical specifications in `docs/specs/` document milestone progress at the time of development. They do **NOT** override `docs/ARCHITECTURE.md` or `docs/00_PROJECT_OVERVIEW.md`.
3. **Recreating Stale / Merged Documents**: Never recreate `docs/CURRENT_STATUS.md`, `docs/MECHANISM.md`, or `docs/DESIGN_DECISIONS.md`. Their contents live in canonical files.
4. **Inventing Directory Layers**: Do not create filesystem directories named `L0/`, `L1/`, etc. Layers are conceptual and map directly to repository paths outlined in Section 1.
