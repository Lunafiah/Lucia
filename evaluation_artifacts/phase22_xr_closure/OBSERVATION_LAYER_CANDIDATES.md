# OBSERVATION LAYER ARCHITECTURE CANDIDATES: HYPOTHESIS SPACE

> **Document Type:** Candidate Architecture Specification  
> **Status:** EXPLORATORY RESEARCH — NO WINNER DECLARED  
> **Applicability:** Observation Layer Replacement Study  
> **Governance:** Pre-Registration Before Empirical Benchmarking  

---

## 1. Introduction

Phase 22-XR proved that while continuous belief filtering is highly effective, the monolithic 421M-parameter ModernBERT-large backbone (`convaiinnovations/laya`) is too computationally heavy and poorly calibrated for edge deployment.

The **Observation Layer Replacement Study** investigates six candidate architectural classes (C1 through C6). Each candidate class represents a distinct inductive bias for translating human dialogue into semantic observation evidence $\mathbf{y}_t$.

In accordance with strict research governance, **no candidate is chosen or declared a winner in advance**. All classes must be evaluated against the frozen criteria in `OBSERVATION_LAYER_REQUIREMENTS.md`.

---

## 2. Candidate Architecture Classes

```text
                                C1: Lightweight Multilingual Sentence Encoder
                                    (e.g., MiniLM, BGE-small, 20M-40M params)
                                                    │
                                C2: Distilled Semantic Encoder
                                    (e.g., Distil-ModernBERT, MobileBERT, 15M-60M params)
                                                    │
RAW CONVERSATIONAL              C3: Audio-First Acoustic / Prosodic Encoder
STREAM (Text + Audio) ───────>     (e.g., Pitch, Energy, Speech Rate, Emformer, w2v-light)
                                                    │
                                C4: Hybrid Multimodal Observation
                                    (Text Semantic Embedding + Prosodic Feature Vector)
                                                    │
                                C5: Structured Semantic Observation (P23 Compatible)
                                    (Renderer-Independent Dialogue Acts / Slot Representation)
                                                    │
                                C6: Decoupled Learned Observation Projection Layer
                                    (Frozen Encoder + Explicit g^-1 Calibration Projector)
```

---

### Candidate C1: Lightweight Multilingual Sentence Encoder
* **Architectural Concept:**
  Replace the heavy task-specific classification head with a compact, highly optimized bi-encoder trained for multilingual semantic similarity (e.g., `paraphrase-multilingual-MiniLM-L12-v2`, `bge-small-en-v1.5`, or `bge-m3-tiny`).
* **Mechanism:**
  - Utterances are mapped into a dense continuous embedding space $\mathbf{e}_t \in \mathbb{R}^{384}$.
  - Latent coordinates are extracted via cosine similarity against reference anchor vectors representing relational and cognitive extremes.
* **Hypothesized Strengths:**
  - Extremely fast CPU execution ($< 25\text{ ms}$).
  - Low parameter footprint ($15\text{M} - 35\text{M}$ parameters, $< 100\text{ MB}$ RAM).
  - Native multilingual zero-shot transfer across English, Vietnamese, and Japanese.
* **Potential Risks / Failure Modes:**
  - Sentence embeddings capture topic similarity rather than subtle conversational intent or emotional valence.
  - Requires anchor vectors to define coordinate poles.

---

### Candidate C2: Distilled Semantic Encoder
* **Architectural Concept:**
  Train a specialized, highly compressed student encoder (e.g., 6-layer MobileBERT or Distil-BERT/ModernBERT, $20\text{M} - 50\text{M}$ parameters) distilled directly from larger conversational dialogue act classifiers.
* **Mechanism:**
  - Employs knowledge distillation with temperature scaling to transfer semantic logits into a lightweight student model.
  - Incorporates temperature scaling directly into the distillation objective to enforce calibration ($ECE \le 0.10$).
* **Hypothesized Strengths:**
  - Maintains domain-specific conversational act awareness while cutting latency by $85\%$.
  - Explicit calibration training during distillation resolves the overconfidence flaw of raw Laya.
* **Potential Risks / Failure Modes:**
  - Requires an offline distillation dataset and teacher inference pipeline.
  - Student model may suffer performance drop on subtle interpersonal cues.

---

### Candidate C3: Audio-First Acoustic / Prosodic Observation
* **Architectural Concept:**
  Derive continuous user-state observations directly from non-verbal acoustic signals (F0 fundamental frequency, vocal jitter, speech energy, tempo, silence duration) rather than relying exclusively on lexical tokens.
* **Mechanism:**
  - Lightweight digital signal processing (DSP) extracts a 16-dimensional acoustic feature vector $\mathbf{a}_t$ at negligible CPU cost ($< 5\text{ ms}$).
  - A small temporal filter maps prosodic dynamics to emotional valence and arousal.
* **Hypothesized Strengths:**
  - Near-zero latency ($< 10\text{ ms}$ total).
  - Completely language-independent (acoustic prosody transcends text vocabularies).
  - Highly sensitive to user fatigue, hesitation, urgency, and dominance.
* **Potential Risks / Failure Modes:**
  - Microphone quality, background noise, and room acoustics introduce high measurement variance.
  - Audio cannot infer semantic cognitive goals or factual conversation topics.

---

### Candidate C4: Hybrid Multimodal Observation
* **Architectural Concept:**
  Fuse lightweight text semantic representations (from C1 or C2) with acoustic prosodic features (from C3) into a unified observation vector:
  $$\mathbf{y}_t = \mathbf{W}_e \mathbf{e}_t + \mathbf{W}_a \mathbf{a}_t$$
* **Mechanism:**
  - Multimodal Kalman observation update: $\mathbf{y}_t$ combines lexical content ("what was said") with prosodic delivery ("how it was said").
  - Observation noise covariance $\mathbf{R}_t$ is dynamically scaled based on acoustic SNR and lexical confidence.
* **Hypothesized Strengths:**
  - Resolves textual ambiguity (e.g., sarcasm, hesitation, reluctant agreement).
  - Provides fallback robustness: if audio is noisy, text dominates; if text is brief, prosody dominates.
* **Potential Risks / Failure Modes:**
  - Multimodal synchronization overhead.
  - Requires simultaneous audio-text input streams.

---

### Candidate C5: Structured Semantic Observation (P23 Compatible)
* **Architectural Concept:**
  Extract a renderer-independent, structured semantic representation consisting of high-level dialogue acts, intent slots, and epistemic queries.
* **Mechanism:**
  - Produces an interpretable intermediate symbolic/vector representation that interfaces directly with both the continuous user filter and the Phase 23 language rendering pipeline.
  - Decouples surface phrasing from underlying intent.
* **Hypothesized Strengths:**
  - 100% interoperable with future Phase 23 structured dialogue generation.
  - Transparent error analysis and deterministic debuggability.
* **Potential Risks / Failure Modes:**
  - May re-introduce categorical boundary quantization if slots are discrete rather than continuous probabilities.

---

### Candidate C6: Decoupled Learned Observation Projection Layer
* **Architectural Concept:**
  Architecturally isolate any underlying neural backbone from the continuous ODE dynamics by inserting an explicit, mathematically constrained projection and calibration layer:
  $$\hat{\mathbf{z}}_t = g^{-1}(\mathbf{y}_{\text{raw}}; \boldsymbol{\theta})$$
* **Mechanism:**
  - The encoder outputs raw logits or embeddings; the projection layer applies Isotonic Regression / Platt Scaling for calibration, followed by a constrained log-odds projection (M2) onto the unit hypercube $[-1, 1]^6$.
  - Computes an empirical observation noise covariance $\mathbf{R}_t$ derived from prediction residuals.
* **Hypothesized Strengths:**
  - Can wrap *any* upstream encoder (C1, C2, C4, or even a future foundation model).
  - Solves the coordinate mismatch problem mathematically without altering the underlying encoder weights.
* **Potential Risks / Failure Modes:**
  - Projection layer requires calibration data to fit $\boldsymbol{\theta}$.

---

## 3. Comparison & Hypothesis Matrix

| Candidate Class | Core Primitive | Expected Param Count | Expected CPU Latency | Multilingual Mechanism | Primary Research Question |
|:---|:---|:---:|:---:|:---:|:---|
| **C1** | Small Sentence Bi-Encoder | $20\text{M} - 40\text{M}$ | $15 - 35\text{ ms}$ | Shared multilingual latent space | Does sentence similarity preserve interpersonal dynamics? |
| **C2** | Distilled Semantic Classifier | $15\text{M} - 60\text{M}$ | $25 - 60\text{ ms}$ | Distilled multilingual student | Can distillation fix overconfidence and high CPU latency? |
| **C3** | Acoustic / Prosodic DSP | $< 1\text{M}$ | $2 - 8\text{ ms}$ | Language-agnostic physical acoustics | Can acoustic features track user arousal and valence? |
| **C4** | Hybrid Text + Audio Fusion | $25\text{M} - 50\text{M}$ | $30 - 70\text{ ms}$ | Multilingual text + acoustic audio | Does multimodal fusion resolve textual ambiguity? |
| **C5** | Structured Semantic Slots | Variable | $20 - 50\text{ ms}$ | Universal semantic primitives | Does structured abstraction integrate cleanly with P23? |
| **C6** | Decoupled Projection Layer | $\sim 50\text{K}$ (Layer) | $< 1\text{ ms}$ | Inherits encoder properties | Can explicit $g^{-1}$ achieve $R^2 \ge 0.85$ on continuous latents? |

---

## 4. Evaluation Mandate

All candidate classes will be implemented as modular, interchangeable adapters conforming strictly to the `IObservationEncoder` interface contract. Benchmarking will proceed strictly under the frozen protocol defined in `OBSERVATION_LAYER_EVALUATION_PLAN.md`.
