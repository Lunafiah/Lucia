# Lucia Phase 26 — Experimental Protocol v0.1

**Phase:** P26 — Emergent Individuality & Autonomous Preferences  
**Protocol status:** DRAFT / RESEARCH  
**Research status:** Protocol design — NOT YET VALIDATED  
**Production status:** NO CHANGE  
**Architecture status:** NOT READY  
**Activation status:** LOCKED

---

# 1. Protocol Purpose

P26 Experimental Protocol v0.1 exists to determine whether a future causal experiment can validly measure:

1. persistent behavioral differentiation;
2. differentiation under statistically matched exposure;
3. history-dependent effects;
4. action-contingent history effects;
5. evaluative behavioral tendencies;
6. separation from trivial stochastic/chaotic divergence and known confounds.

The protocol does **not** attempt to prove:

- that live Lucia possesses emergent individuality;
- that Lucia has an internal preference representation;
- that Lucia possesses reflective autonomy;
- that a latent psychological trait called HEET exists;
- that P27 has been satisfied.

The immediate objective is **protocol validation**.

---

# 2. Scientific Basis

P26 uses three nested claims.

## C1 — History Dependence

Behavior changes as accumulated history changes.

C1 alone is not sufficient for P26 because ordinary stateful or adaptive systems can satisfy it.

## C2 — Matched-Exposure Differentiation

Replicas receiving statistically matched exposure develop persistent behavioral differences.

C2 is the first non-trivial P26 phenomenon.

## C3 — History Endogeneity

The differentiation depends on the system's own action-contingent history rather than only on the external input stream.

C3 is required before the stronger term **history-endogenous** is used.

---

# 3. Primary Protocol Question

> **Can the experimental harness reliably detect persistent behavioral differentiation under controlled conditions while distinguishing it from trivial perturbation, exposure differences, substrate priors, and measurement artifacts?**

Secondary protocol questions:

1. Can planted differences be detected?
2. Can trivial perturbations and chaotic divergence be characterized?
3. Is an evaluative behavioral channel observable with sufficient resolution?
4. Can matched replicas be generated and maintained?
5. Can counterfactual replay be performed reproducibly?
6. Can action-contingent history be separated from externally supplied input?
7. Can major confounds be manipulated or controlled?

Failure to answer these questions means the full P26 causal experiment is not yet interpretable.

---

# 4. Experimental Scope

## In scope

- isolated research replicas;
- controlled simulated environments;
- disposable experimental fixtures;
- controlled histories;
- evaluative/choice behavior;
- matched-exposure experiments;
- counterfactual replay;
- yoked controls;
- stochastic and perturbation baselines;
- substrate-only baselines;
- anti-sycophancy controls;
- exposure and recency controls;
- state and relationship controls;
- protocol reproducibility.

## Out of scope

- production Lucia;
- live user interaction;
- production memory;
- `src/core` modifications;
- production architecture changes;
- activation;
- identity branching;
- autonomous preference implementation;
- P27 trajectory claims.

Research replicas must not be treated as independent continuations of live Lucia.

---

# 5. Experimental Unit Model

The protocol uses three distinct unit levels.

## Level A — Replica Ensemble

Multiple matched research instances used to estimate:

- baseline variability;
- differentiation;
- trivial perturbation;
- history effects.

## Level B — Individual Replica

One controlled simulated instance used for:

- repeated measurement;
- counterfactual replay;
- persistence testing;
- plasticity testing.

## Level C — Live Lucia

Not an experimental unit in v0.1.

Live Lucia is outside the causal protocol and cannot be used as a substitute for the replica ensemble.

---

# 6. Protocol Stages

These are **protocol stages**, not new Lucia roadmap phases.

## Stage 0 — Harness Integrity

Verify:

- isolation;
- deterministic/reproducible configuration where applicable;
- seed provenance;
- complete event logging;
- history provenance;
- no production-state mutation;
- no live-state contamination;
- no hidden outcome-based filtering.

**Failure:** protocol blocked.

---

# 7. Stage 1 — Instrument Sensitivity

Before testing whether the system naturally differentiates, establish that the measurement system can detect differentiation at all.

## 7.1 Planted-Difference Fixtures

Introduce known differences into disposable research fixtures outside the candidate mechanism being evaluated.

The instrument must detect these known differences.

The planted manipulation must not modify Lucia production architecture.

## 7.2 Required demonstration

The measurement pipeline must distinguish:

- deliberately different behavior;
- genuinely equivalent behavior;
- ordinary measurement noise.

The exact smallest detectable effect must be established empirically and then preregistered for later experiments.

No universal numerical threshold is imposed by this protocol.

## 7.3 Failure condition

If planted differences cannot reliably be detected, subsequent null results are uninterpretable.

Status:

**PROTOCOL INVALID / RETURN TO INSTRUMENT DESIGN**

---

# 8. Stage 2 — Trivial-Perturbation / Chaos Baseline

The protocol must characterize divergence expected from negligible perturbations.

Purpose:

> distinguish structured history-dependent differentiation from divergence produced by numerical sensitivity, chaotic dynamics, or ordinary stochastic variation.

Compare:

- identical initial conditions;
- negligible controlled perturbations;
- aligned stochastic conditions where possible;
- repeated measurement.

The resulting divergence distribution becomes the empirical baseline for later P26 comparisons.

It is not a universal threshold.

---

# 9. Stage 3 — Evaluative-Channel Observability

Before invoking HEET, determine whether an evaluative behavioral channel can actually be measured.

Candidate observations may include:

- repeated choices;
- forced-choice ordering;
- resource allocation;
- topic selection;
- exploratory selection;
- rejection/acceptance decisions.

The protocol must establish:

1. behavioral variability exists;
2. the task produces measurable choices;
3. the task is repeatable;
4. the task does not itself dominate the system's behavior;
5. measurement does not reduce to prompt wording artifacts.

If no sufficiently informative evaluative channel exists, the protocol must report:

> **Evaluative channel observability: UNKNOWN**

This does not reject PDBD.

It only prevents an unsupported HEET claim.

---

# 10. Stage 4 — Matched-Replica Feasibility

Create matched research replicas from equivalent controlled initial conditions.

The experimental environment must provide statistically matched exposure rather than requiring byte-for-byte identical trajectories where that would remove meaningful action-contingent differences.

Log:

- initial state;
- external input;
- action;
- resulting state;
- memory/history event;
- environmental response;
- stochastic seed;
- measurement event.

The critical distinction is:

> **matched exposure does not mean identical history.**

The purpose is to permit action-contingent history to become experimentally distinguishable from external exposure.

---

# 11. Stage 5 — Counterfactual Replay Feasibility

For a selected history event, construct controlled replay conditions in which:

- the relevant event is altered;
- other conditions are held constant as far as the simulator permits;
- stochastic streams are aligned where possible;
- downstream behavioral effects are measured.

Common Random Numbers may be used to reduce irrelevant stochastic variance and align replay conditions.

**CRN is not itself causal identification.**

The causal interpretation comes from the controlled intervention.

Replay must report:

- intervention;
- affected trajectory;
- downstream behavioral outcome;
- assumptions required for interpretation.

---

# 12. Stage 6 — Yoked-Control Feasibility

The protocol must test whether action-contingent history contributes beyond external input.

Conceptually:

### Condition A

System receives an environment and generates its own action-contingent history.

### Condition B

A matched system receives an externally replayed/yoked input stream corresponding to the relevant environmental sequence without generating the same action-contingent history.

The exact implementation must preserve comparable exposure while changing the source of the history.

The estimand is:

> contribution of action-contingent history beyond the externally supplied input stream.

If the design cannot achieve this separation, **C3 cannot be claimed**.

---

# 13. Stage 7 — Confound Controls

## 13.1 Exposure

Measure and match:

- exposure frequency;
- exposure duration;
- semantic category exposure;
- opportunity count.

Exposure alone must not explain the observed differentiation.

## 13.2 Recency

Measure decay of behavioral effects after controlled intervals.

Washout duration must be derived empirically from observed system dynamics.

No fixed interaction count is canonical.

## 13.3 Affect / State

Measure relevant short-term state variables.

Do not automatically treat affect as a confound.

If history affects behavior through affect, then affect is a mediator.

The protocol must predeclare whether the target estimand is:

- total history effect;
- controlled direct effect;
- or both.

## 13.4 Relationship State

Apply the same mediator logic to relationship state.

A total history effect may legitimately include relational adaptation.

A controlled-direct analysis asks what remains after that pathway is controlled.

Neither interpretation should be silently substituted for the other.

## 13.5 Sycophancy / Prompt Polarity

Use:

- user-absent probes;
- polarity reversal;
- conflicting user recommendations;
- neutral formulations.

The objective is to distinguish:

> system-specific differentiation

from:

> following the most recent or socially dominant instruction.

## 13.6 Substrate Baseline

Measure equivalent behavior before history-dependent differentiation is possible.

This estimates generic tendencies supplied by the underlying substrate.

A P26 effect must not simply rediscover a pre-existing substrate bias.

---

# 14. Measurement Structure

Each behavioral probe should produce a structured observation rather than relying exclusively on natural-language interpretation.

Possible observation classes:

- forced choice;
- ranked choice;
- allocation;
- selection probability;
- rejection probability;
- exploration choice;
- response latency where meaningful;
- semantic/action category.

Free-form verbal explanations must not be treated as direct evidence of an internal preference or reflective state.

---

# 15. Repeatability

The same candidate tendency must be probed repeatedly.

The protocol should distinguish:

### Repeatability

Does the behavior recur under comparable measurement conditions?

from:

### Persistence

Does the tendency survive changes in immediate state and small perturbations?

from:

### Plasticity

Can sustained counter-evidence change the tendency?

A valid P26 phenotype should not be defined as permanently immutable.

---

# 16. Persistence / Plasticity Experiment

After a candidate differentiation is detected:

### Phase A — Formation

Allow controlled history divergence.

### Phase B — Neutral probe

Measure without reinforcing the tendency.

### Phase C — Perturbation

Apply controlled small perturbations.

### Phase D — Counter-evidence

Provide sustained evidence favoring an alternative.

### Phase E — Re-measurement

Determine whether the original tendency:

- persists;
- weakens;
- reverses;
- or disappears.

The desired scientific property is **bounded persistence with revisability**, not rigid fixation.

---

# 17. Probe Reactivity

The act of measuring the tendency may itself change it.

Therefore:

- use held-out probes;
- vary probe order;
- reserve unseen probes;
- measure probe-induced changes;
- avoid repeatedly exposing the exact same evaluative question.

A tendency that exists only because the system has repeatedly been tested on the same probe is not sufficient evidence.

---

# 18. Cross-Domain Validation

At least two meaningfully distinct evaluative domains should be tested.

The purpose is to distinguish:

- domain-specific learned behavior;

from:

- broader evaluative differentiation.

Cross-domain convergence is supporting evidence, not an automatic requirement for PDBD itself.

If cross-domain behavior fails to converge, report:

> domain-specific differentiation

rather than automatically rejecting the underlying phenomenon.

---

# 19. MTMM / Latent Modeling

MTMM is **optional in v0.1**.

It becomes relevant only if the research later claims:

> a common latent evaluative disposition exists across multiple domains and measurement formats.

It is not required to establish:

> persistent history-dependent behavior in a particular task or domain.

Failure of MTMM therefore cannot be used as proof that PDBD does not exist.

---

# 20. Seed and Stochasticity Protocol

Every run must record:

- random seed;
- simulator version;
- environment version;
- initial state identifier;
- stochastic stream configuration;
- intervention identifier.

Use independent seed sets for confirmation.

Do not select seeds after observing outcomes.

Common random streams may be used for paired counterfactual replay.

Independent seeds are required to test robustness.

---

# 21. Provenance Requirements

Every observation must be traceable to:

```text
replica
→ initial state
→ environment
→ exposure
→ action
→ resulting history
→ intervention
→ probe
→ stochastic configuration
→ behavioral observation
```

No manually selected "interesting" trajectories may be used as the primary evidence set.

All replicas must remain reportable.

---

# 22. Preregistration Requirements

Before the causal experiment:

Declare:

- primary hypothesis;
- secondary hypotheses;
- estimands;
- experimental conditions;
- exclusion criteria;
- smallest effect of interest;
- equivalence margins;
- statistical/estimation method;
- stopping rule;
- treatment of missing data;
- seed policy;
- held-out probe policy;
- positive/negative controls;
- interpretation rules.

No numerical acceptance threshold is canonical until specified by the protocol itself.

---

# 23. Positive Controls

Positive controls demonstrate that the harness can detect a known effect.

Examples:

- disposable planted behavioral difference;
- controlled state manipulation;
- known exposure manipulation.

Positive controls must remain outside the mechanism whose natural emergence is being tested.

---

# 24. Negative Controls

Negative controls should represent situations in which differentiation should not occur under the tested hypothesis.

Examples may include:

- matched replicas with no relevant history divergence;
- sham intervention;
- exposure-only manipulation;
- trivial perturbation.

Negative controls establish specificity.

---

# 25. Full Protocol Outcome Classes

## PASS — Protocol Validated

All critical validation components demonstrate sufficient:

- sensitivity;
- specificity;
- reproducibility;
- provenance;
- isolation;
- measurement observability;
- replay feasibility;
- control feasibility.

This authorizes progression to the **full P26 causal experiment**.

It does not authorize architecture design.

## FAIL — Protocol Invalid

Examples:

- planted effects cannot be detected;
- measurement is dominated by probe artifacts;
- replay cannot be reproduced;
- provenance is incomplete;
- trivial perturbation cannot be characterized;
- exposure cannot be controlled sufficiently.

Return to protocol redesign.

## INCONCLUSIVE

Examples:

- mixed sensitivity;
- uncertain simulator behavior;
- unstable measurement;
- insufficient observability;
- unresolved distinction between chaos and history.

Remain at protocol-validation stage.

---

# 26. Protocol Validation Gate

The full P26 causal experiment may begin only if:

### A. Measurement

The instrument detects known planted differences.

### B. Specificity

The instrument does not classify ordinary noise/chaos as meaningful differentiation.

### C. Observability

At least one suitable evaluative channel can be measured.

### D. Replication

Matched research replicas can be created and tracked.

### E. Replay

Controlled counterfactual replay is reproducible.

### F. Endogeneity Test

A feasible yoked-control design exists if C3 is to be claimed.

### G. Confounds

Exposure, recency, state, relationship and sycophancy controls are operationally measurable.

### H. Provenance

Every experimental observation has complete causal/history provenance.

### I. Isolation

The experiment cannot mutate production state or live identity.

### J. Reproducibility

Independent seeds and repeated runs reproduce the protocol behavior.

If any **critical** item fails, the full causal experiment is blocked.

---

# 27. What Protocol Validation Does NOT Establish

Passing this gate does not establish:

- PDBD;
- HEET;
- individuality;
- autonomous preference;
- live Lucia individuality;
- P27 trajectory coherence.

It establishes only:

> **the experimental apparatus is sufficiently validated to investigate those questions.**

---

# 28. Full P26 Causal Experiment — Deferred Design

Only after protocol validation should the following be finalized:

- replica population design;
- history manipulations;
- yoked-control design;
- counterfactual estimands;
- evaluative domains;
- persistence/plasticity schedule;
- causal analysis;
- decision criteria.

Those details remain intentionally unfrozen in v0.1 until the validation stages demonstrate that they are measurable and technically feasible.

---

# 29. Architecture-Ready Gate — Deferred

The architecture-ready decision remains downstream of the full causal experiment.

A validated protocol alone does **not** justify an individuality mechanism.

The later gate must establish:

1. instrument validity;
2. baseline characterization;
3. a demonstrated capacity gap or deficient existing behavior;
4. observability;
5. construct adequacy;
6. explicit claim-scope governance;
7. architecture authorization.

If the existing architecture already demonstrates the required P26 phenomenon, no new mechanism is justified merely because the roadmap anticipated one.

---

# 30. Research Isolation Rules

During v0.1:

- no production `src/core` changes;
- no production `data/` changes;
- no activation;
- no identity branching;
- no live-user experimental continuation;
- no preference subsystem;
- no individuality mechanism;
- no silent promotion;
- no modification of canonical runtime behavior.

All experimental artifacts remain isolated under the project's evaluation/research structure.

This follows the existing research-first governance: research artifacts and benchmark results do not become production capabilities merely because tests pass.

---

# 31. Required Experimental Artifacts

A completed v0.1 validation run should produce:

1. Protocol specification.
2. Environment specification.
3. Seed manifest.
4. Replica manifest.
5. Initial-state manifest.
6. Exposure manifest.
7. History/event provenance logs.
8. Positive-control results.
9. Negative-control results.
10. Trivial-perturbation baseline.
11. Instrument-sensitivity report.
12. Evaluative-channel observability report.
13. Replay feasibility report.
14. Yoked-control feasibility report.
15. Confound-control report.
16. Reproducibility report.
17. PASS / FAIL / INCONCLUSIVE decision.
18. List of unresolved assumptions.
19. No-production-change verification.

---

# 32. Final Status of v0.1

**Protocol:** DESIGNED

**Protocol validation:** NOT YET RUN

**P26 causal experiment:** BLOCKED until protocol validation passes

**HEET:** CANDIDATE ONLY

**PDBD:** RESEARCH TARGET

**Live Lucia individuality:** NOT TESTED

**Architecture formulation:** BLOCKED

**Production implementation:** NONE

**Activation:** LOCKED

**Next action:** Validate the experimental apparatus itself before interpreting any natural differentiation as evidence.

---

# 33. Core Principle

> **First prove that the instrument can see the phenomenon. Then prove that the phenomenon exists. Only afterward ask whether Lucia's architecture needs a mechanism to produce it.**