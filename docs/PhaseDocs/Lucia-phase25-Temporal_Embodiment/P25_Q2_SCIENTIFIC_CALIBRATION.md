# P25-Q2: Reciprocal Social Feedback & Temporal Embodiment Dynamics — Scientific Calibration & Research Specification

> **DOCUMENT TYPE:** RESEARCH SPECIFICATION / SCIENTIFIC CALIBRATION  
> **STATUS:** P25-Q2 — SCIENTIFIC CALIBRATION RATIFIED / EVALUATION SPECIFICATION STAGED  
> **EVALUATION HARNESS STATUS:** NOT CREATED / NOT EXECUTED (EXECUTION PROHIBITED AT THIS STAGE)  
> **PHASE 25 HORIZON STATUS:** PLANNED (ACTIVE FUTURE RESEARCH HORIZON)  
> **ARCHITECTURE GATE:** LOCKED (NO PRODUCTION MUTATION AUTHORIZED)  
> **IMPLEMENTATION GATE:** LOCKED  
> **GENESIS INVARIANT (INV-8):** PRESERVED BIT-EXACT (`data/profile.json == {"is_onboarded": false}`)  
> **CANONICAL INVARIANTS:** INV-1 (ONE CONTINUOUS LIFE), INV-2 (NO REFLECTIVE EGO) STRICTLY PRESERVED  

---

## 1. Executive Summary & Governance Scope

This research specification establishes the scientific calibration, experimental controls, diagnostic metrics, and operational boundaries for **Research Question P25-Q2** under post-Phase 24 research-first governance.

Following formal architectural review (verdict: *PASS WITH MINOR CORRECTIONS*), principal design confounds identified in the prior draft have been explicitly controlled or operationally isolated in the proposed experiment. In accordance with strict epistemic standards, this specification does not claim universal elimination of all conceivable confounds, but isolates the manipulated feedback pathways under controlled experimental fixtures.

### The Research Question (P25-Q2)
> *Does closed-loop reciprocal social feedback (bidirectional adaptation between user and embodiment dynamics) produce measurable temporal attunement, information flow asymmetry, or interpersonal synchrony without destabilizing somatic homeostasis or violating INV-1 (One Continuous Life)?*

### Formal Phase & Gate Governance
- **P25-Q2 Stage:** Scientific Calibration Ratified / Evaluation Protocol Staged.
- **Harness & Execution Gate:** **LOCKED**. The evaluation harness for P25-Q2 is **not** created or executed in this increment.
- **Architecture Gate:** **LOCKED**. No ADR authored or adopted. No new production ontology classes (`ReciprocalCoupling`, `SocialFeedbackLoop`, `EntrainmentField`) are introduced into runtime code.
- **Implementation Gate:** **LOCKED**. Production codebase diff is strictly zero (`src/core/**` diff = 0, `src/api/**` diff = 0, `electron/**` diff = 0, `data/**` diff = 0).
- **Genesis Gate (INV-8):** Bit-exact preservation of `data/profile.json` (`{"is_onboarded": false}`).

---

## 2. Experimental Conditions: Operational Definition of C1 vs C2

To evaluate the empirical necessity and dynamical behavior of reciprocal embodiment feedback, the experimental protocol defines two strictly isolated conditions. The operational distinction must remain crisp: **C2 must NOT become "C1 + one extra feature"**, but must represent the genuine closing of the bidirectional feedback loop.

```
Condition C1 (Unilateral Adaptation):
  User Behavior U(t) ──> [Observation] ──> Lucia Adaptation A_L(t)
                                                    │
                                                    ▼
                                          Output Actuation only
                                     (User response NOT fed back)

Condition C2 (Bidirectional Adaptation):
  User Behavior U(t) ──> [Observation] ──> Lucia Adaptation A_L(t)
          ▲                                         │
          │                                         ▼
   User Response R_U(t+Δ) <─────────────── Lucia Behavior B_L(t)
          │
          ▼
   Modulates Next Adaptation A_L(t+2Δ)
```

### Condition C1 — Unilateral Adaptation
- **Operational Definition:** Lucia observes and adapts to measured user behavior (e.g., user speech cadence, pause duration, or non-verbal timing markers).
- **Feedback Topology:** Open-loop / feedforward adaptation ($\text{User} \to \text{Lucia}$).
- **Key Constraint:** The user's subsequent reactive response to Lucia's adaptation does **not** directly enter Lucia's adaptive feedback state. Lucia updates her behavior solely as a function of incoming user observations without tracking whether or how the user adapted in return.

### Condition C2 — Bidirectional Adaptation
- **Operational Definition:** The user's temporally measurable response to Lucia's preceding behavior directly modulates Lucia's next adaptation.
- **Feedback Topology:** Closed-loop bidirectional coupling ($\text{Lucia} \to \text{User} \to \text{Lucia}$).
- **Mechanism of Second Direction:**
  1. At step $t$, Lucia manifests expressive behavior $B_L(t)$ conditioned on prior state.
  2. At step $t + \Delta$, the user's observed behavior $U(t + \Delta)$ changes in measurable response to $B_L(t)$ (yielding user response increment $R_U(t + \Delta) = U(t + \Delta) - U_{\text{baseline}}$).
  3. At step $t + 2\Delta$, Lucia's subsequent adaptive state update directly incorporates $R_U(t + \Delta)$ as a closed-loop feedback term:
     $$\mathbf{s}_{\text{adapt}}(t + 2\Delta) = f\big(\mathbf{s}_{\text{adapt}}(t), U(t + \Delta), R_U(t + \Delta)\big)$$
  4. This closes the causal loop: Lucia's prior behavior influences user response, which in turn dynamically reshapes Lucia's next adaptation. C2 is therefore structurally distinct from C1 in dynamical system topology, rather than being an identical model with an auxiliary scalar flag.

---

## 3. Information Flow & Metric Semantics

Information-theoretic diagnostics provide quantitative verification of causal coupling between conversational streams. The metric definitions and semantics are calibrated as follows:

### 3.1 Directed Transfer Entropy Quantities
Transfer Entropy (TE) measures the reduction in uncertainty of a future state of the target process obtained from past states of the source process, conditioning on past states of the target process:

1. **User-to-Lucia Directed Information Flow:**
   $$\text{TE}(\text{User} \to \text{Lucia}) = I\big(\text{Lucia}_{t+1} ; \text{User}_t^{(k)} \mid \text{Lucia}_t^{(l)}\big)$$
   Quantifies the predictive information that user behavioral dynamics impart to Lucia's adaptive trajectory.

2. **Lucia-to-User Directed Information Flow:**
   $$\text{TE}(\text{Lucia} \to \text{User}) = I\big(\text{User}_{t+1} ; \text{Lucia}_t^{(k)} \mid \text{User}_t^{(l)}\big)$$
   Quantifies the predictive information that Lucia's expressive output imparts to the user's subsequent behavior.

### 3.2 Directional Asymmetry Diagnostic ($\Delta\text{TE}_{\text{net}}$)
The net difference between directed flows is defined as:
$$\Delta\text{TE}_{\text{net}} = \text{TE}(\text{User} \to \text{Lucia}) - \text{TE}(\text{Lucia} \to \text{User})$$

> **CRITICAL SEMANTIC CALIBRATION:**  
> $\Delta\text{TE}_{\text{net}}$ is strictly a **directional asymmetry diagnostic**. It indicates the dominant direction of predictive information flow across the dyad.  
> $\Delta\text{TE}_{\text{net}}$ must **NOT** be labeled or interpreted as a "reciprocity metric". A value of $\Delta\text{TE}_{\text{net}} \approx 0$ can occur either when both directional flows are strong and balanced (high bidirectional coupling) or when both flows are zero (complete uncoupling).

### 3.3 Metric Separation Policy
The future Evaluation Specification must keep these four quantities conceptually and mathematically distinct:
1. $\text{TE}(\text{User} \to \text{Lucia})$ — User drive diagnostic.
2. $\text{TE}(\text{Lucia} \to \text{User})$ — Lucia drive diagnostic.
3. $\Delta\text{TE}_{\text{net}}$ — Directional asymmetry diagnostic.
4. **Bidirectional Reciprocity Metric:** No ad-hoc reciprocity metric is invented in this calibration. Any future reciprocity metric must be explicitly grounded in and justified by established literature (e.g., mutual information of joint phase trajectories, or co-regulation indices) before inclusion.

---

## 4. Longitudinal Persistence Horizons (P3 Calibration)

When investigating the temporal stability and persistence of relational attunement across interactions (Hypothesis Track P3):

> **CALIBRATION NOTE ON TEMPORAL HORIZON:**  
> Fixed descriptive horizons such as "days" or "weeks" are scientifically arbitrary and ungrounded in simulation fixtures.  
> All references to long-horizon persistence must be operationally specified as:  
> **"subsequent interaction episodes / future sessions"**  
> 
> Experimental fixtures must evaluate retention across discrete episodic boundaries (session teardown, resting Philia relaxation, and session re-initialization) without imposing unverified wall-clock assumptions.

---

## 5. Documentation Authority & Relational Vector Representation ($R_t$)

The repository maintains an explicit distinction between runtime production truth and architectural documentation history:

### 5.1 Canonical Runtime Authority
The canonical engineering definition of the 4D relational state vector $\mathbf{R}_t$ is defined by the production runtime contract in [`src/core/relationship/state.py`](file:///c:/Users/Lunafiah/Desktop/My_project/Lucia/src/core/relationship/state.py):
$$\mathbf{R}_t = [\text{familiarity}, \text{trust}, \text{closeness}, \text{reciprocity}] \in [0.0, 1.0]^4$$
- `familiarity`: Accumulated interaction exposure / volume $[0.0, 1.0]$
- `trust`: Stability and reliability of interaction expectations $[0.0, 1.0]$
- `closeness`: Relational proximity and shared context depth $[0.0, 1.0]$
- `reciprocity`: Degree of balanced, mutually sustained engagement $[0.0, 1.0]$

This runtime contract is authoritative for all fixtures, test suites, and evaluation models.

### 5.2 Architectural Documentation Drift
In historical sections of [`docs/ARCHITECTURE.md`](file:///c:/Users/Lunafiah/Desktop/My_project/Lucia/docs/ARCHITECTURE.md), an alternative vector description appears:
$$\mathbf{R}_t = [\text{Trust}, \text{Familiarity}, \text{Attunement}, \text{Shared Experience}]$$

> **GOVERNANCE INVARIANT ON RELATIONAL REPRESENTATION:**  
> This discrepancy is recognized as **documentation drift** between earlier conceptual notes and the realized production implementation in `src/core/relationship/state.py`.  
> In accordance with research-first discipline, agents and researchers must **NOT** silently reconcile, rename, or modify either representation as part of P25-Q2.  
> Production code must **NOT** be touched. Fixtures must reference `src/core/relationship/state.py`.

---

## 6. Scientific Calibration Checklist & Audit Summary

| Calibration Item | Prior Draft Issue | Audited Correction Ratified | Epistemic Status |
|---|---|---|---|
| **1. Executive Wording** | Overstated claim: "all multi-variable confounds eliminated" | Replaced with: "principal design confounds identified in the prior draft have been explicitly controlled or operationally isolated in the proposed experiment." | **CALIBRATED** |
| **2. TE Metric Semantics** | $\Delta\text{TE}_{\text{net}}$ mislabeled as "reciprocity metric" | Classified strictly as directional asymmetry diagnostic. $\text{TE}(U\to L)$, $\text{TE}(L\to U)$, and $\Delta\text{TE}_{\text{net}}$ kept separate. No ad-hoc reciprocity metric invented. | **CALIBRATED** |
| **3. P3 Persistence Horizon** | Arbitrary "days/weeks" wall-clock claim | Replaced with operational: "subsequent interaction episodes / future sessions". | **CALIBRATED** |
| **4. Documentation Authority** | Potential collision between `state.py` and `ARCHITECTURE.md` | `src/core/relationship/state.py` recognized as canonical for fixtures; `ARCHITECTURE.md` noted as documentation drift; zero reconciliation edits. | **PRESERVED** |
| **5. C2 Operational Definition** | Risk of C2 collapsing into "C1 + extra feature" | C2 defined as closed-loop bidirectional coupling where user response to Lucia's behavior directly modulates Lucia's next adaptation. | **CALIBRATED** |

---

## 7. Current Governance Gates Status

- **Phase 25 Overall**: `PLANNED` (Future Horizon / Not Implemented)
- **Sub-Inquiry P25-Q1**: `RESEARCH COMPLETE / ARCHIVED AS EVIDENCE` (Report: [`docs/PhaseDocs/Lucia-phase25-Temporal_Embodiment/P25_Q1_FINAL_RESEARCH_REPORT.md`](file:///c:/Users/Lunafiah/Desktop/My_project/Lucia/docs/PhaseDocs/Lucia-phase25-Temporal_Embodiment/P25_Q1_FINAL_RESEARCH_REPORT.md))
- **Sub-Inquiry P25-Q2**: `SCIENTIFIC CALIBRATION RATIFIED / EVALUATION SPECIFICATION STAGED`
- **P25-Q2 Evaluation Harness**: **NOT CREATED / NOT EXECUTED**
- **Architecture Gate**: **LOCKED**
- **Implementation Gate**: **LOCKED**
- **Production Diff**: **0 files**
- **Genesis Invariant (INV-8)**: **LOCKED & BIT-EXACT** (`{"is_onboarded": false}`)
