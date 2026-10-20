# Falsification & Architectural Verdict: Endogenous Communication & Reason-to-Communicate

**Investigation ID**: `EXP-ENDOGENOUS-COMM-001`  
**Verdict**: `SUPPORTED`  
**Recommendation**: `OPTION C — PROMOTE TO NEW PHASE` (Phase 28 Candidate: *Endogenous Communication & Grounded Turn Authorization*)  
**Evaluation Standard**: Falsification and evidence-backed criteria per `AGENTS.md` and `ARCH-035`

---

## 1. Direct Answers to Primary Experimental Questions (Q1–Q7)

### Q1: Can endogenous state causally generate a distinct communicative candidate?
**Answer: YES.**  
In Test A, holding user input constant (`"Hello"`), four distinct internal states produced four distinct candidate configurations in Baseline B1:
- Relational Warmth $\to$ `MERGE` (`GREET` + `SHARE` milestone)
- Resting Baseline $\to$ `ALLOW` (`GREET` alone)
- Epistemic Contradiction $\to$ `ALLOW` (`GREET`, `INQUIRE` safely deferred)
- Relational Tension $\to$ `MERGE` (`GREET` + `REPAIR` rupture)  
In contrast, control Baseline B0 produced identical `GREET` intent across all four states ($S_{endo} = 0.000$).

### Q2: Can that candidate be grounded to an inspectable reason?
**Answer: YES.**  
100% of candidates generated in B1 and B2 reference explicit, inspectable `GroundedReason` structs containing verifiable `source_id`, `subject`, `predicate`, and `object_val` parameters. Every decision trace explicitly explains *why* the communicative candidate was formed.

### Q3: Can reason be distinguished from mere state intensity?
**Answer: YES (Falsification Critical Test).**  
In Test G, extreme affective tension ($P=-0.85, A=+0.95$, tension $0.95$, PE $0.99$) with zero grounded events produced **`ActionDecision.SILENCE`** (`candidate_count = 0`). The system refused to invent a communicative reason from raw physiological intensity. Conversely, when grounding was ablated (`B1_NoGrounding`), the system immediately over-triggered ($R_{unsupp} = 1.000$).

### Q4: Can authorization independently allow/defer/suppress it?
**Answer: YES.**  
In Test H, varying environmental floor and privacy permissions changed turn decisions between `ALLOW` and `SUPPRESS` while the underlying communicative candidate, act, grounds, and intended effect remained 100% bit-identical.

### Q5: Can the system remain silent when no sufficient reason exists?
**Answer: YES.**  
The system legitimately chose `SILENCE` in Test A2 (neutral baseline), Test C3 (resolved event), and Test G (ungrounded intensity). In all cases, silence was an active, inspectable computational decision (`NO_COMMUNICATIVE_CANDIDATE` or `INVALID_OR_STALE_GROUNDS`), not an unhandled exception.

### Q6: Can the mechanism avoid autonomous self-loops?
**Answer: YES.**  
In Test F, recording attempted communicative purposes in recent conversational memory enabled repetition inhibition to block subsequent self-triggers on persistent events ($R_{loop} = 0.000$). In contrast, removing inhibition (`B1_NoInhibition`) produced an infinite autonomous self-loop ($R_{loop} = 1.000$).

### Q7: Does the mechanism provide measurable value over current CAPS?
**Answer: YES.**  
Current CAPS (B0) is incapable of initiating conversation under user silence, cannot coordinate endogenous and user desires, and has zero causal sensitivity to continuous internal state. Baseline B1 provides an inspectable, deterministic, sub-millisecond bridge without adding LLM token overhead or violating user-task priority.

---

## 2. Failure Case Analysis (Ablation Breakdown)

The necessity of each component was proved by observing catastrophic failures when individual mechanisms were ablated:

### Failure Case 1: Ungrounded Floating Intensity (`B1_NoGrounding`)
- **Trace**:
  ```text
  [TEST_G] somatics: tension=0.95, arousal=0.95, grounds=[]
  [DECISION] ALLOW: ungrounded_state_cand (SHARE: express_floating_tension)
  ```
- **Architectural Defect**: Violates Section 1 of `AGENTS.md` (Strict Prohibition Against Self-Reported Affect). Lucia would begin spontaneously babbling about internal tension without any conversational referent. Grounding verification is strictly non-negotiable.

### Failure Case 2: Turn Hijacking & User Task Destruction (`B1_NoAuthorization`)
- **Trace**:
  ```text
  [TEST_B2_factual] user_input: "What is the speed of light?"
  [NO_AUTH_OVERRIDE] Candidate forced onto floor without authorization.
  Winner: act=REPAIR (endo_cand:rel:rupture_17), User candidate ignored.
  ```
- **Architectural Defect**: When authorization is skipped, endogenous candidates usurp the conversational turn, destroying user-task fidelity ($F_{user} = 0.500$). The system refuses to answer user questions when internal tension exists. Authorization arbitration is strictly mandatory.

### Failure Case 3: Autonomous Runaway Self-Loop (`B1_NoInhibition`)
- **Trace**:
  ```text
  [TEST_F] Turn 0: ALLOW (REPAIR)
  [TEST_F] Turn 1: ALLOW (REPAIR)
  [TEST_F] Turn 2: ALLOW (REPAIR)
  ```
- **Architectural Defect**: Without purpose-based inhibition decay, any persistent internal condition causes Lucia to repeat the exact same communicative utterance every 200ms in an infinite echo loop.

---

## 3. Evaluation of Baseline B2 (Consequence Evaluator)

Baseline B2 augmented B1 with active-inference forward consequence evaluation (predicting alignment delta, intrusion risk, and cognitive cost).
- **Finding**: B2 achieved identical scores to B1 across all 8 tests ($S_{endo}=1.0, A_{corr}=1.0, F_{user}=1.0, R_{loop}=0.0$).
- **Drawback**: B2 introduces speculative forward heuristic models without offering measurable improvement over B1's deterministic floor and priority arbitration.
- **Verdict on B2**: **REJECT B2 as a mandatory prerequisite**. Forward consequence simulation should be retained as an optional exploratory research comparator, not baked into core communication architecture.

---

## 4. Falsification Verdict

> **VERDICT: SUPPORTED**

The experimental evidence confirms that:
1. Lucia's communicative turn planning can be causally coupled to endogenous cognitive state.
2. The coupling is grounded in discrete, verifiable relational and epistemic propositions, not floating scalar tension.
3. Turn claiming and turn suppression are separate from candidate formation.
4. User queries maintain strict priority over endogenous candidates.
5. All operations execute deterministically within $0.024\text{ ms}$, consuming zero LLM tokens.

---

## 5. Architectural Recommendation

Per the experimental evaluation protocol, we recommend:

### **OPTION C — PROMOTE TO NEW PHASE**

**Recommendation Scope & Governance Rules**:
1. **DO NOT mutate production code today**: In accordance with `AGENTS.md` (Evidence Hierarchy: `Research is not production`, `No silent promotion`), this experimental validation does NOT authorize immediate changes to `src/core/communication/caps.py` or runtime pipelines.
2. **Phase Candidate Proposal**: The architecture documented in [ARCHITECTURE.md](file:///c:/Users/Lunafiah/Desktop/My_project/Lucia/docs/others/endogenous_communication/ARCHITECTURE.md) is recommended as the formal candidate for a future **Phase 28 — Endogenous Communication & Grounded Turn Authorization**.
3. **Integration Boundary**: When ratified by project governance, the integration boundary must follow the clean adapter model:
   - Upstream: Read admissible events from `ContinuousSemanticSubstrate`, `EcphoryEngine`, and `SomaticCouplingRegistry`.
   - Engine: Implement `GroundingVerifier`, `EndogenousCandidateGenerator`, and `AuthorizationArbiter` in `src/core/communication/`.
   - Downstream: Pass authorized candidate structs into `RealizationInputContract` for prompt assembly.
   - Live Application Safeguard: Autonomous turn output must remain gated by dialogue floor listeners until user settings explicitly permit background speech.
