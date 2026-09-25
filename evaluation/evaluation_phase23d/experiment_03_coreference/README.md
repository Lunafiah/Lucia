# Experiment 03 — Reference & Zero Anaphora Resolution

> **Track:** EXP-03  
> **Target Capability:** Multi-Turn Discourse Reference & Pro-Drop (Zero Anaphora) Tracking  
> **Status:** `[EVALUATION PROTOCOL SPECIFICATION]`  
> **Governing Documents:** `candidate_spec.md`, `metrics.md`, `research_baseline.md`

---

## 1. Scientific Context & Hypothesis Formulation

In multi-turn human-companion interaction, natural language relies heavily on **anaphora** (pronouns) and, in Vietnamese and Japanese, pervasive **zero-anaphora (pro-drop)**. When a speaker says:
- EN (Turn 1): *"The user started a new task."* -> (Turn 2): *"It is challenging."*
- VI (Turn 1): *"Anh Nam vừa bắt đầu dự án mới."* -> (Turn 2): *"Thấy [Ø] rất thú vị."*
- JA (Turn 1): *"田中さんは本を読んでいる。"* -> (Turn 2): *"とても [Ø] 面白そうだ。"*

A non-LLM cognitive substrate must preserve active discourse referents across turns, resolve pronouns, and correctly identify omitted subjects/objects without maintaining a runaway token window.

### 1.1 Testable Hypotheses

- **$H_1$ (Discourse Referent Persistence in UMR-TPG):**  
  By maintaining a persistent document-level discourse graph with salience-weighted entity nodes, UMR-TPG will correctly resolve zero-anaphora across multi-turn dialogues, achieving Anaphora Resolution F1 ($\text{AR-F1}$) $\ge 0.85$ over antecedent distances of up to 5 turns.
- **$H_0$ (Referent Attenuation Null Hypothesis):**  
  Without natural-language prompt buffers, discourse entities experience referential drift, causing $\text{AR-F1}$ to drop below $0.70$ when antecedent distance $k \ge 3$.
- **$H_2$ (V-UMR Recency-Vector Advantage):**  
  In V-UMR, continuous temporal recency vectors combined with graph topology will achieve higher antecedent disambiguation accuracy in the presence of multiple distractors than pure graph traversal.
- **$H_3$ (DRS-Graph Accessibility Constraints):**  
  DRS-Graph will enforce strictly sound referent accessibility according to formal DRT subordination, preventing illegal bindings out of negated or universal boxes.

---

## 2. Experimental Setup & Multi-Turn Scenarios

### 2.1 Scenario Architecture
The test suite consists of 60 multi-turn dialogues (20 per language: EN, VI, JA) ranging from 3 to 10 turns.
1. **Overt Pronominal Reference (EN):** Anaphoric pronouns (*he, she, it, they*).
2. **Subject Pro-Drop (VI/JA):** Null subject bound to the primary interlocutor or recently introduced entity.
3. **Object Pro-Drop (VI/JA):** Null patient bound to an inanimate topic introduced 2–4 turns prior.
4. **Adversarial Distractor Scenarios:** Dialogues containing two or more entities of the same semantic category (e.g. two female persons, two books).

### 2.2 Antecedent Distance Horizons
Dialogues test referent recovery across distance horizons:
- Immediate ($k = 1$ turn)
- Short ($k = 2 - 3$ turns)
- Medium ($k = 4 - 6$ turns)
- Long ($k = 7 - 10$ turns)

---

## 3. Manipulated & Measured Variables

| Variable | Type | Description |
|---|---|---|
| **Antecedent Distance ($k$)** | Independent | Number of intervening turns ($1 \le k \le 10$) |
| **Referent Type** | Independent | Overt pronoun vs Zero-anaphor (pro-drop) |
| **Distractor Entity Count** | Independent | 0, 1, 2, or 4 competing discourse entities |
| **Anaphora Resolution F1 ($\text{AR-F1}$)** | Dependent | Harmonic mean of precision and recall for referent links |
| **Zero Anaphora Recovery ($\text{ARR}$)** | Dependent | Recall specifically on null argument positions |
| **DRT Accessibility Violation Rate** | Dependent | Percentage of referents bound outside accessible universe |

---

## 4. Falsification Criteria & Thresholds

| Candidate | Metric | Passing Threshold | Falsification Boundary (Failure) | Epistemological Status |
|---|---|---|---|---|
| **UMR-TPG** | $\text{AR-F1}$ ($k \le 5$) | $\ge 0.85$ | $< 0.75$ | **Engineering Hypothesis** |
| **UMR-TPG** | Zero-Anaphora Recall ($\text{ARR}$) | $\ge 0.80$ | $< 0.70$ | **Engineering Hypothesis** |
| **V-UMR** | $\text{AR-F1}$ ($k \le 5$) | $\ge 0.85$ | $< 0.75$ | **Engineering Hypothesis** |
| **DRS-Graph** | Accessibility Violation Rate | **$0.0\%$** | $> 0.0\%$ (Violates DRT axioms) | **Formal Logical Axiom** |
| **All** | Resolution Latency | $\le 1.0\text{ ms}$ / turn | $> 5.0\text{ ms}$ | **Engineering Hypothesis** |

> [!NOTE]
> **Epistemological Classification:**  
> While pronominal coreference in English has extensive empirical benchmarks in NLP, multi-turn pro-drop resolution in lightweight edge graphs without LLM generation is classified as an **`[Engineering Hypothesis Requiring Benchmark]`**.
