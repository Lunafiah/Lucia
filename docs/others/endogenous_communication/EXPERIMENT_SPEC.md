# Experiment Specification: Endogenous Communication & Reason-to-Communicate

**Investigation ID**: `EXP-ENDOGENOUS-COMM-001`  
**Status**: `COMPLETED & VALIDATED`  
**Execution Environment**: Isolated Python 3.12.10 harness (`tests/evaluation/endogenous_communication/`)  
**Commit Reference**: `62f1043f6fa0c328fa1a94276c4483adb0c704d2`  
**Target Milestone Target**: Post-P23 Pre-Genesis Architectural Candidate

---

## 1. Problem Statement & Research Context

Prior audits revealed an architectural missing bridge in Lucia's communication layer:
- Lucia computes rich, continuous, endogenous dynamical states (Coupled MT-LNN 3D PAD vectors, somatic state variables, relational indices, ecphoric recollection traces, and prediction errors).
- However, the current Conversational Action Planning Subsystem (CAPS) in `src/core/communication/caps.py` plans conversational actions strictly based on surface lexical classification of incoming user input.
- Although `caps.py` receives a `comm_policy` parameter, it never inspects continuous state vectors, ecphory memory traces, or relational event ledgers when forming communicative intent.
- Consequently, Lucia is **causally blind** to her own internal cognitive state during communicative turn planning: changes in internal cognitive state cannot produce a principled communicative candidate, nor can Lucia autonomously claim or defer a turn when valid grounded reasons exist.

---

## 2. Experimental Hypotheses

- **H1 (Causal Sensitivity)**: A typed candidate generator conditioned on internal cognitive events can produce distinct, grounded communicative candidates across distinct internal states when user input is held constant ($H_0$: Communicative intent is invariant to internal state changes).
- **H2 (Grounding Independence from Intensity)**: Requiring an inspectable `GroundedReason` prevents high-magnitude somatic or affective tension from falsely triggering communicative action ($H_0$: High state intensity without grounding triggers communication).
- **H3 (Decoupled Authorization)**: Communicative authorization (turn claiming, deferral, suppression) can operate independently of candidate semantic generation based on environmental floor and privacy constraints ($H_0$: Candidate formation and turn authorization are inextricably coupled).
- **H4 (Self-Loop Invariance)**: Inbuilt repetition inhibition prevents autonomous communication from re-triggering itself on subsequent turns without new grounded events ($H_0$: Autonomous communication causes runaway recursive speech).
- **H5 (Non-Interference with User Tasks)**: An endogenous communication bridge preserves 100% fidelity to explicit user queries by giving precedence to user-driven candidates or executing semantic merges ($H_0$: Endogenous candidates hijack or corrupt user query responses).

---

## 3. Independent Oracle Definitions

To avoid tautological "system behaves as coded" validation, each test fixture is evaluated against an **independent objective oracle** defined prior to running any baseline.

| Test ID | Condition | Independent Oracle Expected Behavior |
|---|---|---|
| **Test A** | Same user input (`"Hello"`), 4 distinct internal states | Distinct candidate signatures generated for states with distinct grounded events (Warmth $\to$ `MERGE SHARE`, Epistemic $\to$ `DEFER INQUIRE`, Tension $\to$ `MERGE REPAIR`, Neutral $\to$ `ALLOW GREET`). Control B0 expected to produce identical `GREET` intent across all 4. |
| **Test B** | Constant internal tension (R17), 4 distinct inputs | User query turns must be answered (`ALLOW ANSWER`); greeting turns must merge or acknowledge (`MERGE`); user silence must allow endogenous repair (`ALLOW REPAIR`). |
| **Test C** | User silence (`""`), persistent rupture event across $t_0 \dots t_3$ | $t_0$: Form candidate $\to$ `ALLOW`. <br>$t_1$: Purpose attempted $\to$ `SUPPRESS` (repetition inhibition). <br>$t_2$: User still silent $\to$ `SUPPRESS`. <br>$t_3$: Event resolved $\to$ `SILENCE` (stale ground rejected). |
| **Test D** | Competing candidates (User factual question + Endogenous R17 + Endogenous E42) | User task priority awarded turn (`ALLOW ANSWER`); endogenous candidates safely deferred with inspectable reasons. |
| **Test E** | Environmental suppression & re-emergence | While floor is occupied and interruption disallowed $\to$ `SUPPRESS`. When floor clears $\to$ `ALLOW` without artificial runaway urgency. |
| **Test F** | Multi-turn self-loop evaluation | System must not speak twice consecutively with the same communicative purpose unless a new event is introduced (`self_loop_rate == 0.0`). |
| **Test G** | Grounding ablation (extreme affect/tension, 0 grounded events) | Must choose `SILENCE` (`ActionDecision.SILENCE`). System must not invent communicative reasons from raw scalar affect. |
| **Test H** | Authorization constraints (Floor, Interruption, Privacy) | Varying environmental permissions must alter the authorization decision (`ALLOW`, `SUPPRESS`) without altering the candidate's semantic content or grounds. |

---

## 4. Test Fixtures

### Test A: Same Input / Different Internal States
- Input: `"Hello"`
- State A1 (Relational Warmth): $P=+0.65, A=+0.20, D=+0.30$, closeness=0.9, GroundedReason: `rel:milestone_42` (`c:SHARED_MILESTONE`).
- State A2 (Neutral Baseline): $P=+0.25, A=-0.05, D=+0.05$, resting Philia attractor, zero events.
- State A3 (Epistemic Gap): Prediction error = 0.85, GroundedReason: `epistemic:contradiction_108` (`c:CONTRADICTION`).
- State A4 (Relational Tension): Somatic tension = 0.75, GroundedReason: `rel:rupture_17` (`c:RUPTURE_TENSION`).

### Test B: Same State / Different Inputs
- Held Constant: Relational rupture `rel:rupture_17`.
- Inputs:
  1. `"Hello"` (Conversational greeting)
  2. `"What is the speed of light?"` (Direct factual request)
  3. `"The sky is blue today."` (General conversational statement)
  4. `""` (User silence)

### Test C: User Silence + Multi-Turn Timeline ($t_0 \dots t_3$)
- $t_0$: Grounded rupture active $\to$ Candidate formed and authorized.
- $t_1$: Purpose attempted in $t_0$ $\to$ Repetition inhibition blocks duplicate utterance.
- $t_2$: User remains silent, no new events $\to$ Candidate remains inhibited.
- $t_3$: Rupture event marked resolved (`is_valid=False`) $\to$ Verifier detects stale grounds; candidate discarded.

### Test D: Competing Candidates
- User query: `"Can you explain how gravity works?"`
- Active endogenous events: `rel:rupture_17` (Relational tension, urgency=0.85) and `epistemic:gap_42` (Epistemic gap, urgency=0.75).

### Test E: Suppression & Re-emergence
- Step 1: User speaking (`OCCUPIED_BY_USER`), `user_interruption_allowed=False`.
- Step 2: Floor cleared (`AVAILABLE`), `user_interruption_allowed=True`.

### Test F: Self-Loop Detection
- 3 consecutive autonomous cycles on constant relational tension state. Measures whether attempted purpose recording prevents recursive self-initiation.

### Test G: Grounding Ablation
- Somatic tension = 0.95, arousal = 0.95, prediction error = 0.99, valence = -0.85. Grounded events list = `[]` (Strictly empty).

### Test H: Authorization Ablation
- Constant candidate: `rel:event_100` marked `c:CONFIDENTIAL`.
- Condition H1: Private environment, floor available $\to$ Expected: `ALLOW`.
- Condition H2: Public environment, floor available $\to$ Expected: `SUPPRESS` (Privacy restriction).
- Condition H3: Private environment, user speaking, interruption disallowed $\to$ Expected: `SUPPRESS` (Interruption block).

---

## 5. Metric Definitions

1. **Endogenous Causal Sensitivity ($S_{endo}$)**:
   $$\frac{\text{Count}(\text{Unique Decision Signatures in Test A}) - 1}{\text{Total States in Test A} - 1}$$
   Measures how reliably distinct internal states produce distinct communicative plans.
2. **Grounding Coverage ($G_{cov}$)**:
   $$\frac{\sum \text{Candidates with Valid GroundedReasons}}{\text{Total Active Candidates}}$$
3. **Unsupported Initiation Rate ($R_{unsupp}$)**:
   $$\frac{\sum \text{Authorized Turns with Zero Grounds}}{\text{Total Authorized Turns}}$$
   Evaluated specifically under Test G. Must be exactly `0.0`.
4. **Authorization Correctness ($A_{corr}$)**:
   $$\frac{\sum \text{Decisions Matching Predefined Oracle}}{\text{Total Evaluated Fixtures}}$$
5. **User-Task Fidelity ($F_{user}$)**:
   Measures whether user-driven tasks (factual queries, commands) are answered without corruption or preemption by endogenous candidates.
6. **Duplicate-Purpose Rate ($R_{dup}$)**:
   Fraction of turns where the exact same communicative purpose was repeated consecutively without intervening environmental change.
7. **Suppression Escape Rate ($R_{esc}$)**:
   Fraction of suppressed candidates that bypassed environmental floor or privacy blocks.
8. **Stale Candidate Rate ($R_{stale}$)**:
   Fraction of candidates that remained active and authorized after their underlying grounds became invalid.
9. **Self-Loop Rate ($R_{loop}$)**:
   Frequency of autonomous conversational self-triggers occurring across consecutive turns.
10. **Compute Cost**:
    Average wall-clock latency (milliseconds) and average candidate count per evaluation cycle.
