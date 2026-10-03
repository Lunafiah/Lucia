# Phase 23-D — EXP-03: Reference Resolution & Zero-Anaphora Report

> **Experiment ID:** EXP-03  
> **Status:** `[EVALUATION REPORT / COMPLETE]`  
> **Governance:** Isolated under `tests/evaluation/evaluation_phase23d/experiment_03_coreference/`  
> **Production Mutation:** 0 files modified (Zero modifications to `src/core/**` or runtime)

---

## 1. Executive Summary

Experiment 03 evaluated the capability of three candidate semantic architectures (**UMR-TPG**, **V-UMR**, **DRS-Graph**) to maintain **persistent discourse referents** and resolve anaphoric linkages across multi-sentence and multi-turn discourse.

The evaluation specifically addressed English overt pronouns, Japanese subject/object zero-anaphora (pro-drop), Vietnamese kinship deixis (*anh*, *chị*, *em*), discourse perspective shifts, long reference chains, and antecedent ambiguity.

In accordance with Phase 23-D governance, evaluation was explicitly partitioned into:
- **Layer A (Representation Capability):** Substrate's fidelity in maintaining entity clusters and reference chains when given valid assignments.
- **Layer B (Resolution Capability):** Deterministic resolution behavior when linking pronouns and pro-drop without external language models.

---

## 2. Quantitative Results

### 2.1 Mode A — Representation Capability (Gold Coreference Ingestion)

| Candidate Substrate | Verdict | $\text{CEAF}_e \text{ F1}$ | $B^3 \text{ F1}$ | CRA | URP | EPR | RSA | Status |
|---|---|---|---|---|---|---|---|---|
| **UMR-TPG** | **`PASS`** | **1.000** | **1.000** | **1.000** | **1.000** | **1.000** | **1.000** | Full representation fidelity; zero fragmentation |
| **V-UMR** | **`PASS`** | **1.000** | **1.000** | **1.000** | **1.000** | **1.000** | **1.000** | Full representation fidelity; zero fragmentation |
| **DRS-Graph** | **`PASS`** | **1.000** | **1.000** | **1.000** | **1.000** | **1.000** | **1.000** | Full representation fidelity; zero fragmentation |

### 2.2 Mode B — Resolution Capability (Deterministic Rule Resolution)

| Candidate Substrate | Verdict | $\text{CEAF}_e \text{ F1}$ | $B^3 \text{ F1}$ | CRA | URP | EPR | RSA | Status |
|---|---|---|---|---|---|---|---|---|
| **UMR-TPG** | **`PASS`** | **1.000** | **1.000** | **1.000** | **1.000** | **1.000** | **1.000** | Satisfies all gates on controlled test set |
| **V-UMR** | **`PASS`** | **1.000** | **1.000** | **1.000** | **1.000** | **1.000** | **1.000** | Satisfies all gates on controlled test set |
| **DRS-Graph** | **`PASS`** | **1.000** | **1.000** | **1.000** | **1.000** | **1.000** | **1.000** | Satisfies all gates on controlled test set |

*Note: All three candidates satisfy the $\text{CEAF}_e \text{ F1} \ge 0.82$, $\text{EPR} \ge 0.95$, and $\text{URP} \ge 0.90$ falsification gates on the controlled 10-phenomenon corpus.*

---

## 3. Phenomenon-by-Phenomenon Analysis

| Case ID | Linguistic Phenomenon | Target Behavior Tested | Observed Outcome |
|---|---|---|---|
| **C01** | `english_overt_pronoun` | Third-person pronouns (*he*, *it*) binding to *user* and *doc* | $100\%$ accuracy; correct gender/animacy matching |
| **C02** | `japanese_omitted_subject` | Subject pro-drop bound to preceding topic *user* | $100\%$ recovery via topical subject salience |
| **C03** | `japanese_omitted_object` | Object pro-drop bound to preceding patient *report* | $100\%$ recovery via object-role salience |
| **C04** | `japanese_unresolved_zero` | Zero-anaphora without preceding context | Retained as `UNKNOWN_ENTITY`; zero speaker hallucination |
| **C05** | `vietnamese_kinship_persistent` | Honorific *anh* mapped to persistent user entity | Identity maintained alongside `SENIOR_MALE_PEER` deixis |
| **C06** | `vietnamese_perspective_shift` | Shift in honorific perspective across speakers (*Lucia, Admin, Nam*) | Identity preserved; zero spurious merger of *em* mentions |
| **C07** | `long_reference_chain` | Entity continuity across 5 sequential sentences | $100\%$ persistence rate ($\text{EPR} = 1.0$); zero chain splitting |
| **C08** | `competing_antecedents` | Disambiguation between two male entities (*user* vs *admin*) | Role-matched disambiguation prevents reference swapping |
| **C09** | `ambiguous_antecedent` | Pronoun with insufficient disambiguation evidence | Retained as `AMBIGUOUS_UNRESOLVED`; zero arbitrary binding |
| **C10** | `multi_event_persistence` | Single entity (*server*) participating in 4 sequential events | Maintained single coherent cluster across events |

---

## 4. Representation vs Resolution Attribution

- **Representation Capability (Layer A):**  
  All three architectures (UMR-TPG, V-UMR, DRS-Graph) can represent persistent entities, maintain multi-sentence chains, and preserve referent boundaries without degradation.
- **Resolution Capability (Layer B):**  
  On the controlled 10-case evaluation corpus, deterministic salience rules paired with gender, role, and animacy constraints successfully bound antecedents and correctly refrained from resolving ambiguous or ungrounded mentions.
- **Critical Distinction:**  
  The success of Layer B on controlled test cases demonstrates **feasibility under structured constraints**. It does **NOT** imply that open-domain reference resolution or conversational coreference in raw spoken dialogue is completed.

---

## 5. Epistemic Scope Boundaries

### What EXP-03 Demonstrates:
1. **Discourse Entity Persistence:** UMR-TPG, V-UMR, and DRS-Graph maintain persistent discourse entities across multi-sentence chains without chain fragmentation ($\text{EPR} = 1.000$).
2. **Non-Hallucinatory Zero-Anaphora Handling:** When context evidence is absent (C04), candidate models successfully output `UNKNOWN_ENTITY` instead of defaulting to the speaker.
3. **Vietnamese Pragmatic Separation:** Vietnamese kinship deixis (*anh*, *em*) can be tracked as perspective-dependent relations without corrupting base entity identity or causing false entity mergers.
4. **Ambiguity Isolation:** Ambiguous pronominal references without adequate disambiguation evidence are preserved as `AMBIGUOUS_UNRESOLVED` rather than arbitrarily forced into a cluster.

### What EXP-03 Does NOT Demonstrate:
1. It does **NOT** prove that conversational coreference for noisy, ungrammatical, or multi-party natural dialogue is finalized.
2. It does **NOT** demonstrate production readiness for Lucia's runtime pipeline.
3. It does **NOT** establish an overall architectural winner among UMR-TPG, V-UMR, and DRS-Graph.
