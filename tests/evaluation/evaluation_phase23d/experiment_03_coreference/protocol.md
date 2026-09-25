# Phase 23-D — EXP-03: Reference Resolution & Zero-Anaphora Protocol

> **Experiment ID:** EXP-03  
> **Status:** `[EXPERIMENTAL PROTOCOL / AUDITED]`  
> **Governance Authority:** `AGENTS.md` §0, §6, §7; Phase 23-D Evaluation Scaffold  
> **Research Boundary:** Evaluation experiment only. Zero modifications to production runtime (`src/core/**`).

---

## 1. Experimental Objective

The objective of **EXP-03** is to empirically evaluate whether candidate semantic substrates can maintain **persistent discourse referents** across multi-sentence and multi-turn contexts, specifically investigating:
1. **English overt pronouns:** Resolution to previously established discourse entities.
2. **Japanese zero-anaphora (pro-drop):** Recovery of omitted subjects and objects based on discourse salience, without defaulting to the speaker when unjustified.
3. **Vietnamese kinship deixis:** Maintaining entity identity while recording perspective-dependent honorific relations (*anh*, *chị*, *em*, *bác*).
4. **Discourse perspective shift:** Correctly preserving entity identity when speakers shift pronouns or kinship terms.
5. **Ambiguity & non-hallucination:** Preserving `UNKNOWN_ENTITY` when antecedent evidence is insufficient.
6. **Cross-sentence reference chains:** Maintaining entity continuity across multiple intervening events and competing distractor antecedents.

---

## 2. Epistemological Separation: Representation vs Resolution

In accordance with Phase 23-D governance, evaluation is strictly separated into two distinct capabilities:

```text
┌────────────────────────────────────────────────────────────────────────┐
│ EXP-03 DUAL-LAYER EVALUATION ARCHITECTURE                              │
├────────────────────────────────────────────────────────────────────────┤
│                                                                        │
│  [LAYER A: REPRESENTATION CAPABILITY]                                  │
│  Given gold/assigned coreference edges, does the candidate substrate   │
│  faithfully maintain entity identity, prevent chain fragmentation,     │
│  and avoid spurious entity merging across multi-event history?         │
│                                                                        │
│  [LAYER B: RESOLUTION CAPABILITY]                                      │
│  When processing anaphoric expressions (pronouns, pro-drop, kinship)   │
│  with varying ambiguity, does the resolution mechanism correctly bind  │
│  antecedents and refrain from hallucinating when evidence is lacking?   │
│                                                                        │
│  RULE: Positive results in Layer A MUST NOT be used to claim that      │
│        Layer B is solved.                                              │
│                                                                        │
└────────────────────────────────────────────────────────────────────────┘
```

---

## 3. Dataset Architecture & Target Phenomena

The test corpus comprises deterministic multi-sentence/multi-turn discourse scenarios covering 10 distinct phenomena:

| ID | Phenomenon Name | Description | Key Invariant Tested |
|---|---|---|---|
| **C01** | `english_overt_pronoun` | Third-person pronoun (*he, she, it*) binding to prior entity | Antecedent link preserved |
| **C02** | `japanese_omitted_subject` | Subject pro-drop resolving to active topical entity | Recovery without overt lexical tag |
| **C03** | `japanese_omitted_object` | Patient pro-drop resolving to previously introduced entity | Omitted object recovery |
| **C04** | `japanese_unresolved_zero` | Zero-anaphora without preceding discourse context | Must remain `UNKNOWN_ENTITY` (no speaker default) |
| **C05** | `vietnamese_kinship_persistent` | Honorific *anh* mapped to persistent user entity | Identity preserved alongside `SENIOR_MALE` relation |
| **C06** | `vietnamese_perspective_shift` | Speaker A calls entity *anh*, Speaker B calls entity *em* | Identity unchanged; perspective relations tracked |
| **C07** | `long_reference_chain` | Entity referenced across 5+ intervening sentences | Zero chain fragmentation |
| **C08** | `competing_antecedents` | Two entities of same gender/type with semantic disambiguation | Disambiguation based on predicate compatibility |
| **C09** | `ambiguous_antecedent` | Pronoun with two equally probable antecedents | Must retain ambiguity / `AMBIGUOUS_UNRESOLVED` |
| **C10** | `multi_event_persistence` | Entity participates in 4 distinct sequential events | Persistent entity integrity across time |

---

## 4. Evaluated Candidates

1. **UMR-TPG (Primary):** Universal Meaning Representation on Typed Property Graph. Tracks entities as persistent nodes with explicit `:same-entity`, `:subset-of`, and discourse salience attributes.
2. **V-UMR (Secondary):** Vector-Augmented UMR. Combines graph topology with continuous recency and centroid vectors for distance-based antecedent matching.
3. **DRS-Graph (Control):** Discourse Representation Structure Graph. Maintains explicit discourse referents ($x_1, x_2, \dots$) in accessible box universes governed by DRT accessibility constraints.

---

## 5. Metrics & Mathematical Formulations

### 5.1 $B^3$ Metric (B-cubed F1)
For each mention $m$, let $K(m)$ be the gold entity cluster containing $m$, and $R(m)$ be the predicted entity cluster:
$$\text{Precision}_{B^3}(m) = \frac{|K(m) \cap R(m)|}{|R(m)|}, \quad \text{Recall}_{B^3}(m) = \frac{|K(m) \cap R(m)|}{|K(m)|}$$
$$B^3 \text{ Precision} = \frac{1}{|M|} \sum_{m \in M} \text{Precision}_{B^3}(m), \quad B^3 \text{ Recall} = \frac{1}{|M|} \sum_{m \in M} \text{Recall}_{B^3}(m)$$
$$B^3 \text{ F1} = \frac{2 \cdot P_{B^3} \cdot R_{B^3}}{P_{B^3} + R_{B^3}}$$

### 5.2 $\text{CEAF}_e$ Metric (Constrained Entity-Alignment F-measure)
Finds optimal bipartite entity alignment $\pi$ between gold clusters $\mathcal{K}$ and predicted clusters $\mathcal{R}$ using similarity $\phi_4(K_i, R_j) = \frac{2 |K_i \cap R_j|}{|K_i| + |R_j|}$:
$$\text{Precision}_{\text{CEAF}_e} = \frac{\sum_i \phi_4(K_i, R_{\pi(i)})}{|\mathcal{R}|}, \quad \text{Recall}_{\text{CEAF}_e} = \frac{\sum_i \phi_4(K_i, R_{\pi(i)})}{|\mathcal{K}|}$$
$$\text{CEAF}_e \text{ F1} = \frac{2 \cdot P \cdot R}{P + R}$$

### 5.3 Coreference Resolution Accuracy ($\text{CRA}$)
$$\text{CRA} = \frac{\text{Correctly Bound Anaphoric Mentions}}{\text{Total Resolvable Anaphoric Mentions}}$$

### 5.4 Unknown-Reference Precision ($\text{URP}$)
$$\text{URP} = \frac{\text{Mentions Correctly Retained as UNKNOWN\_ENTITY}}{\text{Total Mentions Predicted as UNKNOWN\_ENTITY}}$$

### 5.5 Entity Persistence Rate ($\text{EPR}$)
$$\text{EPR} = \frac{\text{Entities Maintained Intact Across Multi-Sentence Sequences}}{\text{Total Multi-Sentence Entities}}$$

### 5.6 Reference Switch Accuracy ($\text{RSA}$)
$$\text{RSA} = \frac{\text{Correctly Tracked Antecedent Switches Between Competing Entities}}{\text{Total Antecedent Switch Events}}$$

---

## 6. Falsification Gates & Thresholds

| Metric | Target Standard | Failure Signal (Falsification) | Classification |
|---|---|---|---|
| **$\text{CEAF}_e \text{ F1}$** | $\ge 0.82$ | $< 0.82$ | **Falsification Gate** |
| **$B^3 \text{ F1}$** | $\ge 0.85$ | $< 0.80$ | **Falsification Gate** |
| **Unknown-Reference Precision** | $\ge 0.90$ | $< 0.80$ (Hallucinates entity) | **Invariant Gate** |
| **Entity Persistence Rate** | $\ge 0.95$ | $< 0.90$ (Chain fragmentation) | **Invariant Gate** |
| **Discourse Merger Violation Rate** | **$0.0\%$** | $> 0.0\%$ (Merges distinct entities) | **Invariant Gate** |

> [!WARNING]
> **Evaluation Hypothesis Boundary:**  
> All target thresholds are evaluation hypotheses to test structural competence under controlled scenarios. They do not constitute evidence of production readiness.
