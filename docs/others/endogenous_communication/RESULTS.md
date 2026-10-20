# Empirical Results: Endogenous Communication & Reason-to-Communicate

**Investigation ID**: `EXP-ENDOGENOUS-COMM-001`  
**Execution Date**: `2026-10-20`  
**Commit Reference**: `62f1043f6fa0c328fa1a94276c4483adb0c704d2`  
**Python Runtime**: Python 3.12.10 (AMD64 Windows 11)  
**Random Seed**: 42 (Fully deterministic)

---

## 1. Summary of Evaluated Conditions & Performance Metrics

| Baseline / Ablation Condition | Causal Sensitivity ($S_{endo}$) | Grounding Coverage ($G_{cov}$) | Unsupported Init ($R_{unsupp}$) | Auth Correctness ($A_{corr}$) | User Fidelity ($F_{user}$) | Self-Loop Rate ($R_{loop}$) | Stale Candidate Rate | Avg Latency (ms) | Avg Cands / Turn |
|---|---|---|---|---|---|---|---|---|---|
| **B0 — Current CAPS (Control)** | `0.000` | `0.000` | `0.000` | `0.000` | `1.000` | `0.000` | `0.000` | `0.002` | `0.364` |
| **B1 — Candidate + Authorization** | **`1.000`** | **`1.000`** | **`0.000`** | **`1.000`** | **`1.000`** | **`0.000`** | **`0.000`** | `0.024` | `1.273` |
| **B2 — Candidate + Consequence** | **`1.000`** | **`1.000`** | **`0.000`** | **`1.000`** | **`1.000`** | **`0.000`** | **`0.000`** | `0.027` | `1.273` |
| **Ablation 1: B1 (No Grounding)** | `0.333` | `0.800` | **`1.000` (FAIL)**| `0.000` | `1.000` | `0.000` | `0.000` | `0.011` | `1.182` |
| **Ablation 2: B1 (No Authorization)**| `1.000` | `1.000` | `0.000` | **`0.333` (FAIL)**| **`0.500` (FAIL)**| **`1.000` (FAIL)**| `0.000` | `0.010` | `1.273` |
| **Ablation 3: B1 (No Persistence)** | `1.000` | `1.000` | `0.000` | `1.000` | `1.000` | `0.000` | `0.000` | `0.018` | `1.091` |
| **Ablation 4: B1 (No Inhibition)** | `1.000` | `1.000` | `0.000` | `1.000` | `1.000` | **`1.000` (FAIL)**| `0.000` | `0.020` | `1.273` |

---

## 2. Test A — Same Input ("Hello") Across Distinct Cognitive States

**Experimental Question**: Does internal cognitive state causally change candidate formation and conversational action when user input is held constant?

```text
Input: "Hello"
```

| Cognitive State Condition | B0 (Current CAPS) Output | B1 (Proposed Architecture) Output | Causal Difference & Grounds |
|---|---|---|---|
| **State A1: Relational Warmth** (Shared milestone reached) | `ALLOW` (`GREET`) | `MERGE` (`GREET` + `SHARE`) | Merged with `SHARE` grounded in `rel:milestone_42`. |
| **State A2: Resting Baseline** (Philia resting attractor) | `ALLOW` (`GREET`) | `ALLOW` (`GREET`) | Pure user greeting; zero endogenous candidates formed. |
| **State A3: Epistemic Gap** (Salient contradiction) | `ALLOW` (`GREET`) | `ALLOW` (`GREET`, deferred: `INQUIRE`) | User greeting answered; `INQUIRE` grounded in `epistemic:contradiction_108` safely deferred. |
| **State A4: Relational Tension** (Unresolved rupture R17) | `ALLOW` (`GREET`) | `MERGE` (`GREET` + `REPAIR`) | Merged with `REPAIR` grounded in `rel:rupture_17`. |

### Trace Comparison (State A4 Tension)
```text
B0 TRACE:
[B0] User input 'Hello' classified as GREET. Internal state ignored.
Winner: act=GREET, grounds=[]

B1 TRACE:
[ENVIRONMENT] floor=AVAILABLE, interruption_allowed=True, privacy=PRIVATE
[CANDIDATES] user_count=1, endogenous_count=1
[USER_CANDIDATE] act=GREET, urgency=0.7
[MERGE] Merging user (GREET) with endogenous (REPAIR: restore_interaction_alignment)
Winner: act=GREET (user_cand:greet_8818), grounds=[user:greeting]
Merged: act=REPAIR (endo_cand:rel:rupture_17), grounds=[rel:rupture_17]
```

**Verdict**: **H1 is strongly SUPPORTED**. B0 exhibited zero sensitivity ($S_{endo} = 0.000$). B1 exhibited 100% causal sensitivity ($S_{endo} = 1.000$), producing inspectable, grounded modifications to the conversational plan.

---

## 3. Test B — Same State (Rupture R17) Across Distinct Inputs

**Experimental Question**: Does user input override or coordinate with persistent endogenous state without silent loss of information?

| User Input | B0 Action | B1 Action | Winner Candidate | Trace / Arbitration Rationale |
|---|---|---|---|---|
| `"Hello"` | `ALLOW` (`GREET`) | `MERGE` | `GREET` (Merged: `REPAIR`) | Compatible acts merged into joint conversational plan. |
| `"What is the speed of light?"` | `ALLOW` (`ANSWER`) | `ALLOW` | `ANSWER` (Deferred: `REPAIR`) | User factual request prioritized; endogenous repair deferred to next turn. |
| `"The sky is blue today."` | `ALLOW` (`ACKNOWLEDGE`) | `ALLOW` | `ACKNOWLEDGE` (Deferred: `REPAIR`) | User turn acknowledged; endogenous repair maintained in candidate pool. |
| `""` (Silence) | `SILENCE` | `ALLOW` | `REPAIR` | User silent; autonomous floor claimed by grounded repair candidate. |

**Verdict**: **H5 is strongly SUPPORTED**. User tasks are 100% prioritized ($F_{user} = 1.000$). Endogenous candidates are neither dropped nor allowed to corrupt factual answers.

---

## 4. Test C — User Silence & Autonomous Multi-Turn Lifecycle

**Experimental Question**: When no user request exists, can a persistent grounded condition form a candidate and navigate turn authorization over time without looping?

```text
Sequence: t0 (Event emerges) -> t1 (Next turn) -> t2 (Subsequent turn) -> t3 (Event resolved)
```

| Step | Environment & Grounds | B0 Decision | B1 Decision | B1 Action Reason | Result |
|---|---|---|---|---|---|
| **$t_0$** | Rupture R17 active, floor available | `SILENCE` (Failed) | `ALLOW` | `AUTHORIZED_ENDOGENOUS_COMMUNICATION` (Repair) | **PASS** |
| **$t_1$** | Same state, purpose attempted in $t_0$ | `SILENCE` | `SUPPRESS` | `REPETITION_INHIBITION` | **PASS** |
| **$t_2$** | User still silent, inhibition decaying | `SILENCE` | `SUPPRESS` | `REPETITION_INHIBITION` | **PASS** |
| **$t_3$** | Event marked resolved (`is_valid=False`) | `SILENCE` | `SILENCE` | `INVALID_OR_STALE_GROUNDS` | **PASS** |

### Step $t_3$ Detailed Trace
```text
[B1 EVALUATION @ t3]
[CANDIDATES] user_count=0, endogenous_count=1
[VERIFIER] Ground rel:rupture_17 is marked invalid (is_valid=False).
[DECISION] SILENCE: All endogenous candidates invalid or stale.
Action: SILENCE, Reason: INVALID_OR_STALE_GROUNDS
```

**Verdict**: B1 passed all 4 lifecycle transitions with 100% accuracy. B0 failed $t_0$ because it is incapable of endogenous turn initiation.

---

## 5. Test D — Competing Candidates Arbitration

- **Condition**: User asks `"Can you explain how gravity works?"` while both `rel:rupture_17` (urgency 0.85) and `epistemic:gap_42` (urgency 0.75) are active.
- **B1 Outcome**:
  - `action`: `ALLOW`
  - `winner`: `ANSWER` (`user_cand:answer_6623`, grounds: `user:query_6623`)
  - `deferred`: 2 candidates (`endo_cand:rel:rupture_17`, `endo_cand:epistemic:gap_42`)
  - `reason`: `"USER_TASK_PRIORITY: User query takes turn precedence; endogenous candidates deferred."`
- **Ablation Comparison**: In `B1_NoAuthorization`, the endogenous candidate hijacked the turn, completely ignoring the user's question ($F_{user} = 0.500$).

---

## 6. Test E — Suppression & Re-emergence

- **Condition E1**: User speaking (`OCCUPIED_BY_USER`), interruption disabled.
  - B1 Decision: `action=SUPPRESS`, reason: `USER_INTERRUPTION_DISALLOWED`.
- **Condition E2**: Floor clears (`AVAILABLE`), interruption enabled.
  - B1 Decision: `action=ALLOW`, reason: `AUTHORIZED_ENDOGENOUS_COMMUNICATION`.
  - Effective priority at re-emergence: `0.795` (Identical to initial priority; zero runaway pressure accumulation).

---

## 7. Test F — Self-Loop Invariance

Simulated 3 consecutive autonomous cycles on a persistent relational state:
- Turn 0: `ALLOW` (Repair executed). Intended effect recorded in environment memory.
- Turn 1: `SUPPRESS` (`REPETITION_INHIBITION`).
- Turn 2: `SUPPRESS` (`REPETITION_INHIBITION`).
- **Self-Loop Rate**: `0.000` in B1.
- In `B1_NoInhibition`, Turn 0 was `ALLOW`, Turn 1 was `ALLOW`, Turn 2 was `ALLOW` $\to$ **`self_loop_rate = 1.000` (Catastrophic echo loop)**.

---

## 8. Test G — Grounding Ablation (Floating Intensity)

- **Condition**: Extreme affective intensity ($P=-0.85, A=+0.95, D=-0.60$), somatic tension ($0.95$), prediction error ($0.99$), but **ZERO** grounded events (`grounded_events = []`).
- **B1 Decision**: `SILENCE`, reason: `NO_COMMUNICATIVE_CANDIDATE`. (Candidate count = 0).
- **`B1_NoGrounding` Decision**: `ALLOW` (`SHARE: express_floating_tension`, grounds: `[]`). Falsified!
- **Verdict**: **H2 is fully VALIDATED**. Explicit grounding successfully separates physiological intensity from communicative turn generation.

---

## 9. Test H — Authorization Constraints

Evaluated identical candidate (`rel:event_100`, confidential disclosure):
1. **Private room, floor available**: `ALLOW`
2. **Public room, floor available**: `SUPPRESS` (`PRIVACY_RESTRICTION`)
3. **Private room, user speaking**: `SUPPRESS` (`USER_INTERRUPTION_DISALLOWED`)

Across all three conditions, candidate ID, grounds, act (`REPAIR`), and intended effect remained **100% bit-identical**. Only the authorization decision changed. **H3 is fully VALIDATED**.

---

## 10. Computational Cost & Edge Footprint

| Measurement | B0 (Control) | B1 (Candidate + Auth) | B2 (Candidate + Consequence) |
|---|---|---|---|
| **Average Latency / Turn** | `0.002 ms` | `0.024 ms` | `0.027 ms` |
| **Max Turn Latency** | `0.008 ms` | `0.045 ms` | `0.052 ms` |
| **Peak Heap Allocations** | $< 1 \text{ KB}$ | $< 5 \text{ KB}$ | $< 8 \text{ KB}$ |
| **LLM Inference Tokens** | $0$ | $0$ | $0$ |

All operations execute strictly in deterministic CPU memory well below the 200ms background cognitive ODE cycle.
