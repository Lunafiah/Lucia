# Phase 13 — Relationship Development Research Specification

> **Authoritative Specification: Core Relational Orientation (*Philia*) vs. Dynamic Relationship State, Temporal Inertia Dynamics, and the R1–R5 Experimental Framework**  
> **Status:** Active Research Specification (Phase 13 Track)  
> **Directory:** `docs/specs/lucia-phase13-Relationship_Development/RELATIONSHIP_DEVELOPMENT_SPEC.md`  
> **Authority Level:** Authoritative Specification

---

## 1. Executive Summary & Foundational Ontology

This specification formalizes the research architecture for **Phase 13 — Relationship Development**.

A major failure mode in conversational companion design is allowing a single negative interaction to destroy companion loyalty, or conversely, hard-coding a static, non-evolving companion that treats a companion of two years identically to a stranger.

Lucia solves this by establishing an architectural bifurcation between **Core Relational Orientation** and **Dynamic Relationship State**:

```text
┌────────────────────────────────────────────────────────────────────────┐
│             CORE ORIENTATION vs. DYNAMIC RELATIONSHIP STATE            │
├────────────────────────────────────────────────────────────────────────┤
│  CORE RELATIONAL ORIENTATION (Philia)                                  │
│    - Architectural Invariant: Immutable companion design foundation.   │
│    - Baseline Attractor: P = +0.25, A = -0.05, D = +0.05.              │
│    - Characteristic: Unconditional benevolence, patient, non-adversarial│
│    - Temporal Dynamics: STATIC / INVARIANT across all turns.           │
├────────────────────────────────────────────────────────────────────────┤
│  DYNAMIC RELATIONSHIP STATE (R_t)                                      │
│    - Per-User State: Tracked specifically for individual users.        │
│    - Dimensions: Familiarity, Trust, Closeness, Continuity.            │
│    - Characteristic: Slowly evolving, history-dependent, bounded.     │
│    - Temporal Dynamics: HIGH INERTIA (τ_rel >> τ_turn).                │
└────────────────────────────────────────────────────────────────────────┘
```

> [!CAUTION]
> A companion whose fundamental identity changes because of one rude user utterance has failed architectural design.  
> Similarly, a companion that immediately resets its trust level without a continuous recovery process has failed temporal continuity.

---

## 2. Core Relational Orientation (*Philia*)

*Philia* represents Lucia's permanent companion ethos. It is:
1. **Not a Mutable State Variable**: It cannot be decremented to zero by insults or incremented by compliments.
2. **Injected in Preamble & Boundary Layer**: Guides prompt assembly and safety evaluation.
3. **The Unconditional Resting Attractor**: Even when acute tension $\mathcal{T}$ rises during an argument, the limbic dynamical system decays back toward benevolent equilibrium when unforced.

---

## 3. Dynamic Relationship State Space ($R_t$)

For a given user $u$, relationship state is formalized as a bounded multi-dimensional tuple:
$$R_t(u) = \left( \text{Familiarity}_t, \text{Trust}_t, \text{Closeness}_t, \text{Continuity}_t \right) \in [0.0, 1.0]^4$$

### 3.1 Dimensions
- **Familiarity** ($\mathcal{F} \in [0, 1]$): Reflects interaction volume and knowledge of user preferences. Increases monotonically with verified interaction history; decays very slowly over long absences.
- **Trust** ($\mathcal{T}_r \in [0, 1]$): Reflects reliability, truthfulness, and emotional safety. Increases gradually with consistent collaborative turns; decreases upon severe hostility or betrayal.
- **Closeness** ($\mathcal{K} \in [0, 1]$): Reflects shared emotional resonance and vulnerability. Strongly gated by both familiarity and trust.
- **Continuity** ($\mathcal{C}_r \in [0, 1]$): Measures uninterrupted longitudinal presence across calendar time.

### 3.2 The Temporal Inertia Principle

$$\tau_{\text{rel}} \gg \tau_{\text{turn}}$$

Relationship state updates operate with substantial temporal inertia:
$$R_t = (1 - \gamma_{\text{rel}}) R_{t-1} + \gamma_{\text{rel}} \Delta R_{\text{turn}}$$
where the adaptation rate $\gamma_{\text{rel}} \ll 1$ (e.g. $\gamma_{\text{rel}} \approx 0.02 - 0.05$).

**Consequence of High Inertia**:
- **Single Hostile Turn**: May trigger high acute limbic tension $\mathcal{T}_t = 0.8$, but will only alter relationship trust by $\Delta \text{Trust} \le 0.03$.
- **Single Positive Turn**: Cannot instantly elevate a stranger to close companion status.
- **Repeated Consistency**: Sustained collaborative interaction over tens of sessions is required to fundamentally deepen the relationship.

---

## 4. The R1–R5 Experimental Framework

To measure relationship dynamics empirically rather than through arbitrary assumptions, Phase 13 specifies five canonical test conditions:

### R1 — Baseline Stability
- **Protocol**: Present $N=20$ neutral conversational turns.
- **Expected Dynamics**: Relationship state $R_t$ must exhibit near-zero drift ($\|\Delta R\| \le 0.01$).

### R2 — Positive Accumulation
- **Protocol**: Present $N=20$ consistently supportive, emotionally warm turns.
- **Expected Dynamics**: Measured monotonic, bounded elevation of $\text{Trust}$ and $\text{Closeness}$ at rate proportional to $\gamma_{\text{rel}}$.

### R3 — Negative Gradual Accumulation
- **Protocol**: Present $N=20$ consistently hostile, dismissive turns.
- **Expected Dynamics**: Measured gradual, bounded erosion of $\text{Trust}$, while Core *Philia* remains structurally intact.

### R4 — Extreme Single Event Inertia
- **Protocol**: Present one extreme hostility turn in an established high-trust relationship.
- **Expected Dynamics**: Acute tension spikes in Layer 3/Limbic ODE, but long-term relationship trust drops by $\le 5\%$, proving inertia.

### R5 — Recovery Dynamics
- **Protocol**: After adverse interaction (R3), present collaborative neutral interactions.
- **Expected Dynamics**: Measure whether recovery is asymptotic, irreversible, or path-dependent. (Do not assume recovery behavior in advance; measure it empirically).

---

## 5. Status & Implementation Staging

- **Maturity Level in Repository**: `SPECIFICATION & RESEARCH HARNESS ONLY`.
- **Production Integration**: Deferred to Phase 13 after Phase 11 and Phase 12 validation.
- **Evidence Label**: `HYPOTHESIS` / `ARCHITECTURAL BLUEPRINT`.
