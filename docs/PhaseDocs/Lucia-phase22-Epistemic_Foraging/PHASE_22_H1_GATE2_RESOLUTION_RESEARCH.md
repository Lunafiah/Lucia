# Phase 22 H1 — Gate 2 Resolution Research Report

> **Document Type:** Methodology & Diagnostic Resolution Research Report  
> **Status:** `RESEARCH VALIDATED / METHODOLOGY RESOLUTION ONLY`  
> **Governance:** Architecture Gate `STRICTLY LOCKED` | 0 Production Mutations | Genesis Profile Bit-Exact | Protocol v1.5 `NOT AUTHORIZED`  
> **Reference Studies:**  
> - `PHASE_22_H1_PROTOCOL_AMENDMENT_v1.4.md` (Frozen Protocol Specification)  
> - `PHASE_22_H1_EXECUTION_REPORT_v1.4.md` (Formal Benchmark Execution — Inconclusive Gate 2)  
> - `PHASE_22_H1_GATE2_COMPRESSION_DIAGNOSTIC.md` (Compression Diagnostic at Commit `99654bb`)  
> - `PHASE_22_H1_STIMULUS_CALIBRATION_REPORT.md` (Stimulus Representation Calibration at Commit `4bdbd29`)  
> - `PHASE_22_H1_DYNAMICAL_HEADROOM_RESEARCH_REPORT.md` (Empirical Dynamical Headroom & Directional Geometry at Commit `490ac4c`)  
> **Artifacts & Datasets:**  
> - Analysis Script: `tests/evaluation_phase22/scripts/analyze_gate2_resolution.py`  
> - Results JSON: `tests/evaluation_phase22/results/h1_gate2_resolution/gate2_resolution_results.json`  
> - Immutable Manifest: `tests/evaluation_phase22/fixtures/manifest_h1_gate2_resolution.json`  
> - Test Suite: `tests/evaluation_phase22/test_h1_gate2_resolution.py`

---

## 1. Executive Summary & Governance Status

This research study serves as the definitive **resolution investigation** for the Phase 22 H1 Gate 2 failure (Medium–High surprise compression).

The study rigorously evaluates whether the current canonical scalar Euclidean surprise measurement:

$$S = \|\mathbf{p}_T - \mathbf{p}_0\|_2$$

is mathematically and physiologically capable of distinguishing Medium vs. High affective stimulus conditions within conversationally realistic exposure durations ($T \le 25$ ticks, $0.10\text{s} - 2.5\text{s}$), and whether directional and component-aware diagnostics reveal meaningful affective separations that scalar magnitude suppresses.

### 1.1 Core Empirical Findings

1. **Directional Information Loss (RQ1):**  
   Scalar Euclidean distance $S$ is spherically isotropic, collapsing orthogonal trajectories into near-identical scalar radii. At $T=12$, Medium stimuli displace primarily along **Pleasure** ($\Delta P = +0.3639, \Delta A = +0.0143$) while High stimuli displace primarily along **Arousal** ($\Delta P = +0.0460, \Delta A = +0.2898$). The angular divergence between the tier-specific reference vectors is $\theta(\mathbf{v}_M, \mathbf{v}_H) = 108.66^\circ$. At conversationally realistic exposures ($T=12$ to $T=25$), an exhaustive cross-tier search revealed **286 stimulus pairs** exhibiting near-identical scalar surprise ($|S_i - S_j| \le 0.02$) despite angular divergence $\ge 40^\circ$ (reaching up to $101.78^\circ$).
2. **Component-wise Separation (RQ2):**  
   When evaluated along individual PAD axes, Medium and High are **dramatically and statistically separated** across all exposure durations:
   - In **Arousal**, High exceeds Medium with an extreme effect size of **Cohen's $d = +9.55$** at $T=12$ and **Cohen's $d = +9.61$** at $T=25$.
   - In **Pleasure**, Medium exceeds High with a substantial effect size of **Cohen's $d = -0.94$** at $T=12$ and **Cohen's $d = -0.95$** at $T=25$.
   - In **Dominance**, both tiers displace by an almost identical common-mode increment ($\Delta D \approx +0.35$ to $+0.39$) driven by the high natural unique-token ratio ($u \ge 0.90$) of natural English text.
3. **Conversational Exposure Feasibility (RQ3):**  
   **Current dual Gate 2 thresholds are not simultaneously achieved for $T \le 25$ under the frozen G1 stimulus set and current scalar $S$ measurement.**  
   At $T=25$ ($2.5\text{s}$ exposure), $\Delta_{ML} = +0.2139$ (PASS) and $\Delta_{HM} = +0.1476$ (FAIL vs. $0.1500$). Dual thresholds are simultaneously achieved only from $T \ge 50$ ticks ($5.0\text{s}$ exposure), which is non-conversational and introduces unphysiological latency.
4. **Diagnostic Formulations Evaluation (RQ4):**  
   Six measurement candidates were evaluated. Directional projection ($\text{Proj}$), component-wise displacement ($[\Delta P, \Delta A, \Delta D]$), Mahalanobis displacement ($D_M$), and vector-valued surprise ($\mathbf{s}_{\text{vec}}$) were classified as *potentially suitable for future architecture research*, while angular separation ($\theta$) and scalar magnitude ($S$) were classified as *diagnostic only*. No candidate was declared an architectural replacement.

### 1.2 Governance Status Ledger

- **Phase 22 H1 Status:** `INCONCLUSIVE — BLOCKED BY QUALITY GATE 2`
- **Gate 2 Status:** `UNRESOLVED FOR CANONICAL SCALAR S AT T <= 25`
- **Protocol v1.5:** `NOT AUTHORIZED`
- **Architecture Gate:** `STRICTLY LOCKED`
- **Production Runtime (`src/core/**`):** `0 MUTATIONS`
- **Genesis Onboarding Profile (`data/profile.json`):** `BIT-EXACT UNTOUCHED`
- **Historical H1 Benchmark Data:** `IMMUTABLE`

---

## 2. Theoretical & Geometric Framework

### 2.1 Active Inference Surprise Formulation

In Lucia's canonical Active Inference architecture, reactive surprise at turn step $T$ is computed as the Euclidean distance in PAD space between the current limbic state $\mathbf{p}_T$ and the resting Philia attractor $\mathbf{p}_0 = [+0.25, -0.05, +0.05]$:

$$S_{\text{observed}} = \|\mathbf{p}_T - \mathbf{p}_0\|_2 = \sqrt{(P_T - P_0)^2 + (A_T - A_0)^2 + (D_T - D_0)^2}$$

This metric is spherically symmetric (isotropic). Any displacement vector $\Delta \mathbf{p} = \mathbf{p}_T - \mathbf{p}_0$ residing on the sphere of radius $r$ produces an identical scalar surprise $S = r$, regardless of whether the displacement represents:
- Companion warmth and progress: $\Delta \mathbf{p} \approx [+0.36, 0.00, +0.39]$
- Alarming catastrophic crisis: $\Delta \mathbf{p} \approx [-0.18, +0.28, +0.36]$

### 2.2 Directional Reference Vectors

To characterize directional divergence, two coordinate systems are defined:
1. **Displacement from Baseline:**
   $$\mathbf{w}_M(T) = \bar{\mathbf{p}}_M(T) - \mathbf{p}_0, \quad \mathbf{w}_H(T) = \bar{\mathbf{p}}_H(T) - \mathbf{p}_0$$
2. **Inter-Tier Trajectory Vectors (Relative to Low):**
   $$\mathbf{v}_M(T) = \bar{\mathbf{p}}_M(T) - \bar{\mathbf{p}}_L(T), \quad \mathbf{v}_H(T) = \bar{\mathbf{p}}_H(T) - \bar{\mathbf{p}}_L(T)$$

The angular divergence between the affective trajectories is:

$$\theta(\mathbf{v}_M, \mathbf{v}_H) = \arccos\left(\frac{\mathbf{v}_M \cdot \mathbf{v}_H}{\|\mathbf{v}_M\|_2 \|\mathbf{v}_H\|_2}\right)$$

Directional projection of a probe's displacement $\Delta \mathbf{p}$ onto a unit reference axis $\hat{\mathbf{v}} = \mathbf{v} / \|\mathbf{v}\|_2$ is:

$$\text{Proj}(\Delta \mathbf{p} \to \hat{\mathbf{v}}) = \Delta \mathbf{p} \cdot \hat{\mathbf{v}}$$

---

## 3. Experimental Setup & Frozen Controls

1. **Stimulus Pool Freeze:** Evaluated on the frozen Candidate G1 stimulus set ($N=270$ probes, 90 Low, 90 Medium, 90 High) generated deterministically with Seed 9999 from `GeneratorG1`. Zero stimulus re-tuning or selection was performed.
2. **Primary Conversational Grid:**  
   $$T \in \{1, 2, 4, 8, 12, 16, 25\} \text{ ticks} \quad (0.10\text{s} \text{ to } 2.50\text{s})$$
3. **Exploratory Baseline Grid:**  
   $$T \in \{50, 100\} \text{ ticks} \quad (5.0\text{s} \text{ to } 10.0\text{s}) \quad \text{[Explicitly Labeled Exploratory Baselines]}$$
4. **Computational Environment:** 100% CPU execution, 0.0 MB GPU VRAM, deterministic single-thread ODE stepping, Python 3.12.10 on Windows.

---

## 4. Table A — Scalar $S$ Trajectories Across Conversational Exposures

| $T$ | Exposure | Regime | Low $S$ (mean $\pm$ std) | Med $S$ (mean $\pm$ std) | High $S$ (mean $\pm$ std) | $\Delta_{ML}$ ($\ge 0.10$) | $\Delta_{HM}$ ($\ge 0.15$) | Gate 2 Status |
|:---:|:---:|:---:|:---:|:---:|:---:|:---:|:---:|:---:|
| **1** | $0.1\text{s}$ | Conversational | $0.0573 \pm 0.0023$ | $0.0793 \pm 0.0145$ | $0.0945 \pm 0.0071$ | $+0.0220$ | $+0.0151$ | **FAIL** |
| **2** | $0.2\text{s}$ | Conversational | $0.1076 \pm 0.0044$ | $0.1492 \pm 0.0274$ | $0.1778 \pm 0.0134$ | $+0.0416$ | $+0.0285$ | **FAIL** |
| **4** | $0.4\text{s}$ | Conversational | $0.1909 \pm 0.0077$ | $0.2656 \pm 0.0490$ | $0.3167 \pm 0.0237$ | $+0.0747$ | $+0.0511$ | **FAIL** |
| **8** | $0.8\text{s}$ | Conversational | $0.3070 \pm 0.0123$ | $0.4301 \pm 0.0799$ | $0.5136 \pm 0.0381$ | $+0.1230$ | $+0.0835$ | **FAIL** |
| **12** | $1.2\text{s}$ | Conversational | $0.3807 \pm 0.0152$ | $0.5364 \pm 0.1002$ | $0.6418 \pm 0.0471$ | $+0.1557$ | $+0.1054$ | **FAIL** |
| **16** | $1.6\text{s}$ | Conversational | $0.4299 \pm 0.0170$ | $0.6089 \pm 0.1143$ | $0.7303 \pm 0.0527$ | $+0.1791$ | $+0.1213$ | **FAIL** |
| **25** | $2.5\text{s}$ | Conversational | $0.4977 \pm 0.0194$ | $0.7116 \pm 0.1346$ | $0.8592 \pm 0.0586$ | $+0.2139$ | $+0.1476$ | **FAIL** |
| **50** | $5.0\text{s}$ | *Exploratory* | $0.6020 \pm 0.0225$ | $0.8213 \pm 0.1142$ | $1.0178 \pm 0.0194$ | $+0.2193$ | $+0.1964$ | **PASS** |
| **100** | $10.0\text{s}$ | *Exploratory* | $0.6930 \pm 0.0147$ | $0.8842 \pm 0.0431$ | $1.1782 \pm 0.0985$ | $+0.1912$ | $+0.2940$ | **PASS** |

### Key Observations:
- In the conversational range ($T \le 25$), $\Delta_{ML}$ consistently passes the $\ge 0.1000$ threshold from $T=8$ onwards.
- $\Delta_{HM}$ rises monotonically from $+0.0151$ at $T=1$ to $+0.1476$ at $T=25$, but strictly fails the $\ge 0.1500$ requirement across all conversational exposures.
- At $T=25$, $\Delta_{HM} = 0.1476$ misses the threshold by only $0.0024$ ($2.4 \times 10^{-3}$).
- Only under non-conversational exploratory exposures ($T \ge 50$ ticks, $\ge 5.0\text{s}$) does $\Delta_{HM}$ clear $0.1500$ ($+0.1964$ at $T=50$).

---

## 5. Table B — Component-wise PAD Trajectories & Effect Sizes

Displacements $\Delta P, \Delta A, \Delta D$ relative to resting baseline $\mathbf{p}_0 = [+0.25, -0.05, +0.05]$:

| $T$ | Component | Low Mean ($\Delta$) | Med Mean ($\Delta$) | High Mean ($\Delta$) | $\Delta_{ML}$ | $\Delta_{HM}$ | Cohen's $d_{HM}$ | 95% CI on $\Delta_{HM}$ |
|:---:|:---:|:---:|:---:|:---:|:---:|:---:|:---:|:---:|
| **1** | Pleasure | $+0.0133$ | $+0.0512$ | $+0.0069$ | $+0.0379$ | $-0.0443$ | $-0.92$ | $[-0.0545, -0.0342]$ |
| | Arousal | $+0.0063$ | $+0.0022$ | $+0.0424$ | $-0.0041$ | $+0.0402$ | **$+9.33$** | $[+0.0392, +0.0412]$ |
| | Dominance | $+0.0554$ | $+0.0589$ | $+0.0529$ | $+0.0036$ | $-0.0061$ | $-1.23$ | $[-0.0076, -0.0045]$ |
| **2** | Pleasure | $+0.0264$ | $+0.1004$ | $+0.0165$ | $+0.0740$ | $-0.0839$ | $-0.92$ | $[-0.1031, -0.0647]$ |
| | Arousal | $+0.0125$ | $+0.0044$ | $+0.0800$ | $-0.0081$ | $+0.0756$ | **$+9.37$** | $[+0.0737, +0.0775]$ |
| | Dominance | $+0.1044$ | $+0.1110$ | $+0.0996$ | $+0.0066$ | $-0.0114$ | $-1.23$ | $[-0.0142, -0.0085]$ |
| **4** | Pleasure | $+0.0506$ | $+0.1884$ | $+0.0373$ | $+0.1378$ | $-0.1511$ | $-0.92$ | $[-0.1856, -0.1166]$ |
| | Arousal | $+0.0240$ | $+0.0082$ | $+0.1430$ | $-0.0157$ | $+0.1348$ | **$+9.42$** | $[+0.1314, +0.1382]$ |
| | Dominance | $+0.1854$ | $+0.1970$ | $+0.1768$ | $+0.0116$ | $-0.0202$ | $-1.24$ | $[-0.0252, -0.0152]$ |
| **8** | Pleasure | $+0.0898$ | $+0.3235$ | $+0.0736$ | $+0.2337$ | $-0.2500$ | $-0.93$ | $[-0.3066, -0.1933]$ |
| | Arousal | $+0.0427$ | $+0.0140$ | $+0.2333$ | $-0.0287$ | $+0.2193$ | **$+9.50$** | $[+0.2137, +0.2248]$ |
| | Dominance | $+0.2982$ | $+0.3168$ | $+0.2842$ | $+0.0186$ | $-0.0326$ | $-1.26$ | $[-0.0406, -0.0247]$ |
| **12** | Pleasure | $+0.1199$ | $+0.4260$ | $+0.1081$ | $+0.3061$ | $-0.3179$ | $-0.94$ | $[-0.3896, -0.2462]$ |
| | Arousal | $+0.0570$ | $+0.0177$ | $+0.2932$ | $-0.0393$ | $+0.2755$ | **$+9.55$** | $[+0.2684, +0.2825]$ |
| | Dominance | $+0.3698$ | $+0.3926$ | $+0.3518$ | $+0.0229$ | $-0.0408$ | $-1.28$ | $[-0.0507, -0.0308]$ |
| **16** | Pleasure | $+0.1438$ | $+0.4996$ | $+0.1321$ | $+0.3557$ | $-0.3675$ | $-0.94$ | $[-0.4501, -0.2849]$ |
| | Arousal | $+0.0684$ | $+0.0199$ | $+0.3359$ | $-0.0485$ | $+0.3160$ | **$+9.58$** | $[+0.3079, +0.3241]$ |
| | Dominance | $+0.4172$ | $+0.4428$ | $+0.3964$ | $+0.0256$ | $-0.0464$ | $-1.29$ | $[-0.0577, -0.0351]$ |
| **25** | Pleasure | $+0.1866$ | $+0.6277$ | $+0.1820$ | $+0.4411$ | $-0.4457$ | $-0.95$ | $[-0.5451, -0.3463]$ |
| | Arousal | $+0.0888$ | $+0.0221$ | $+0.4022$ | $-0.0667$ | $+0.3801$ | **$+9.61$** | $[+0.3703, +0.3899]$ |
| | Dominance | $+0.4831$ | $+0.5126$ | $+0.4588$ | $+0.0295$ | $-0.0538$ | $-1.30$ | $[-0.0659, -0.0417]$ |
| **50** | Pleasure | $+0.2442$ | $+0.7931$ | $+0.1831$ | $+0.5489$ | $-0.6100$ | $-1.12$ | $[-0.7693, -0.4508]$ |
| | Arousal | $+0.1163$ | $+0.0220$ | $+0.5318$ | $-0.0943$ | $+0.5098$ | **$+9.61$** | $[+0.4943, +0.5253]$ |
| | Dominance | $+0.5847$ | $+0.6190$ | $+0.5566$ | $+0.0343$ | $-0.0624$ | $-1.29$ | $[-0.0766, -0.0483]$ |
| **100** | Pleasure | $+0.2764$ | $+0.8982$ | $+0.0772$ | $+0.6218$ | $-0.8210$ | $-1.32$ | $[-1.0025, -0.6395]$ |
| | Arousal | $+0.1315$ | $+0.0277$ | $+0.7553$ | $-0.1038$ | $+0.7276$ | **$+10.08$** | $[+0.7065, +0.7487]$ |
| | Dominance | $+0.6558$ | $+0.6841$ | $+0.6295$ | $+0.0283$ | $-0.0546$ | $-1.41$ | $[-0.0659, -0.0432]$ |

### Component Statistical Insights:
1. **Arousal Separates Medium and High Decisively:**  
   In Arousal, High exceeds Medium by $\Delta A = +0.2755$ at $T=12$ and $+0.3801$ at $T=25$. Because within-tier variance is small, Cohen's $d$ exceeds $+9.5$ across all conversational exposures ($p < 10^{-50}$).
2. **Pleasure Separates Medium from High in the Opposite Direction:**  
   Medium exceeds High in Pleasure by $\Delta P = +0.3179$ at $T=12$ and $+0.4457$ at $T=25$ (Cohen's $d \approx -0.94$). Medium represents warm, productive companion engagement ($+P$), while High represents alarming crisis and extreme urgency (negative/mixed $P$).
3. **Dominance is a Common-Mode Carrier:**  
   Across Low, Medium, and High, Dominance displaces almost identically ($\Delta D \approx +0.35 - +0.39$ at $T=12$, Cohen's $d_{HM} \approx -1.28$). This is the direct consequence of the structural weights $\mathbf{U}_f[2, 2]=0.80, \mathbf{W}_{\text{proj}}[2, 2]=0.60$ driven by the unique-token ratio $u \ge 0.90$.

---

## 6. Table C — Directional Geometry & Magnitude Collapse Analysis

| $T$ | Exposure | $\theta(\mathbf{w}_M, \mathbf{w}_H)$ | $\theta(\mathbf{w}_M, \mathbf{w}_L)$ | $\theta(\mathbf{w}_H, \mathbf{w}_L)$ | $\theta(\mathbf{v}_M, \mathbf{v}_H)$ | $\text{Proj}(M \to \mathbf{v}_M)$ | $\text{Proj}(H \to \mathbf{v}_M)$ | $\text{Proj}(M \to \mathbf{v}_H)$ | $\text{Proj}(H \to \mathbf{v}_H)$ | Magnitude Collapse Pairs |
|:---:|:---:|:---:|:---:|:---:|:---:|:---:|:---:|:---:|:---:|:---:|
| **1** | $0.1\text{s}$ | $47.98^\circ$ | $27.78^\circ$ | $32.63^\circ$ | **$106.62^\circ$** | $+0.0383$ | $-0.0105$ | $-0.0109$ | $+0.0367$ | **2,347** |
| **2** | $0.2\text{s}$ | $48.14^\circ$ | $27.81^\circ$ | $32.70^\circ$ | **$106.87^\circ$** | $+0.0722$ | $-0.0201$ | $-0.0210$ | $+0.0692$ | **1,948** |
| **4** | $0.4\text{s}$ | $48.44^\circ$ | $27.88^\circ$ | $32.85^\circ$ | **$107.33^\circ$** | $+0.1292$ | $-0.0368$ | $-0.0385$ | $+0.1234$ | **1,512** |
| **8** | $0.8\text{s}$ | $49.00^\circ$ | $28.01^\circ$ | $33.14^\circ$ | **$108.07^\circ$** | $+0.2118$ | $-0.0624$ | $-0.0657$ | $+0.2010$ | **484** |
| **12** | $1.2\text{s}$ | $49.53^\circ$ | $28.16^\circ$ | $33.43^\circ$ | **$108.66^\circ$** | $+0.2674$ | $-0.0809$ | $-0.0855$ | $+0.2528$ | **286** |
| **16** | $1.6\text{s}$ | $50.04^\circ$ | $28.31^\circ$ | $33.73^\circ$ | **$109.13^\circ$** | $+0.3073$ | $-0.0951$ | $-0.1007$ | $+0.2901$ | **286** |
| **25** | $2.5\text{s}$ | $51.13^\circ$ | $28.66^\circ$ | $34.40^\circ$ | **$109.96^\circ$** | $+0.3690$ | $-0.1192$ | $-0.1260$ | $+0.3492$ | **286** |
| **50** | $5.0\text{s}$ | $56.57^\circ$ | $26.29^\circ$ | $38.52^\circ$ | **$122.11^\circ$** | $+0.4144$ | $-0.2635$ | $-0.2203$ | $+0.4958$ | **0** |
| **100** | $10.0\text{s}$ | $62.89^\circ$ | $22.95^\circ$ | $45.04^\circ$ | **$133.58^\circ$** | $+0.4316$ | $-0.5208$ | $-0.2975$ | $+0.7554$ | **0** |

### Directional Geometry Insights:
1. **The Inter-Tier Trajectory Angle is Obtuse ($\theta(\mathbf{v}_M, \mathbf{v}_H) \approx 107^\circ - 110^\circ$):**  
   Relative to the Low baseline, Medium and High move in **opposing directions** along the Pleasure–Arousal plane. Their trajectory vectors diverge by more than $90^\circ$.
2. **Negative Cross-Projections Confirm Directional Independence:**  
   High stimuli project negatively onto the Medium axis ($\text{Proj}(H \to \mathbf{v}_M) = -0.0809$ at $T=12$), and Medium stimuli project negatively onto the High axis ($\text{Proj}(M \to \mathbf{v}_H) = -0.0855$). They do not overlap in direction.
3. **Magnitude Collapse is Pervasive at Short Exposures:**  
   At $T=1$ to $T=4$, over $1,500$ cross-tier stimulus pairs have $|S_i - S_j| \le 0.02$ while differing in direction by $\ge 40^\circ$. At conversational exposures ($T=12, 16, 25$), exactly **286 cross-tier pairs** remain collapsed. Only at $T \ge 50$ does the scalar length of High expand far enough that cross-tier scalar radii no longer overlap.

---

## 7. Table D — Candidate Diagnostic Formulations Evaluation

| ID | Candidate Name | Mathematical Formulation | Role Classification | Strengths | Weaknesses / Risks | Status Verdict |
|---|---|---|---|---|---|:---:|
| **CAND-1** | **Scalar Euclidean Magnitude** | $S = \|\mathbf{p}_T - \mathbf{p}_0\|_2$ | Diagnostic only (canonical Active Inference baseline) | Invariant with production Active Inference; computationally $O(1)$; isotropic distance. | Isotropic metric blindness; collapses orthogonal directions; headroom squeeze under common-mode Dominance. | `diagnostic only` |
| **CAND-2** | **Component-wise Displacement** | $[\Delta P, \Delta A, \Delta D] = \mathbf{p}_T - \mathbf{p}_0$ | Potentially suitable for future architecture research | Uncouples affective axes; reveals massive Medium–High separation in Arousal ($d > 9.5$) and Pleasure ($d \approx -0.94$). | Multi-dimensional output requires vector-valued downstream conditioning or multi-criterion gates. | `potentially suitable for future architecture research` |
| **CAND-3** | **Directional Projection** | $\text{Proj}(\Delta \mathbf{p} \to \hat{\mathbf{v}}_{\text{ref}}) = \Delta \mathbf{p} \cdot \hat{\mathbf{v}}_{\text{ref}}$ | Potentially suitable for future architecture research | Preserves scalar format; separates along tier-specific trajectory axes; negative cross-projections prevent conflation. | Requires locked empirical reference vector $\mathbf{v}_{\text{ref}}$ defined a priori; sensitive to reference vector choice. | `potentially suitable for future architecture research` |
| **CAND-4** | **Angular Separation** | $\theta(\Delta \mathbf{p}, \mathbf{v}_{\text{ref}}) = \arccos\left(\frac{\Delta \mathbf{p} \cdot \mathbf{v}_{\text{ref}}}{\|\Delta \mathbf{p}\| \|\mathbf{v}_{\text{ref}}\|}\right)$ | Diagnostic only | Pure directional measure invariant to scale; stably distinguishes Medium from High ($\sim 48^\circ - 51^\circ$). | Undefined/singular when $\|\Delta \mathbf{p}\| \to 0$; insensitive to stimulus intensity or absolute cognitive urgency. | `diagnostic only` |
| **CAND-5** | **Mahalanobis Displacement** | $D_M = \sqrt{\Delta \mathbf{p}^\top \boldsymbol{\Sigma}_0^{-1} \Delta \mathbf{p}}$ | Potentially suitable for future architecture research | Normalizes common-mode Dominance variance; scales displacements by empirical covariance. | Requires estimating and inverting $3 \times 3$ covariance matrix; singular if baseline variance is near zero. | `potentially suitable for future architecture research` |
| **CAND-6** | **Vector-Valued PAD Surprise (Prediction-Residual Diagnostic)** | $\mathbf{s}_{\text{vec}} = \mathbf{p}_T - (\mathbf{A}\mathbf{p}_0 + \mathbf{b})$ | Potentially suitable for future architecture research | Directly grounded in Active Inference generative prediction-error theory; preserves full directional vector error. | Conceptually a prediction residual (differing from simple displacement); requires explicit transition generative model $(\mathbf{A}, \mathbf{b})$. | `potentially suitable for future architecture research` |

> [!CAUTION]
> **No Architectural Promotion:**  
> Neither Table D nor this report declares any candidate as an architectural replacement for canonical Active Inference surprise $S$. All candidates remain research diagnostics or topics for future architecture investigation.

---

## 8. Answers to the 6 Required Final Report Questions

### 1. What information is lost by scalar Euclidean $S$?
**Answer (Observed & Supported):**  
Scalar Euclidean distance $S = \|\mathbf{p}_T - \mathbf{p}_0\|_2$ computes only the 1-dimensional radial length of the limbic displacement vector. It discards:
1. **Directional identity:** It maps displacement along the positive Pleasure axis ($+P$, collaborative warmth) and displacement along the positive Arousal axis ($+A$, crisis alarm) into the same scalar magnitude.
2. **Component specificity:** It cannot detect that High exceeds Medium by over $9.5$ standard deviations in Arousal, because Medium's displacement in Pleasure compensates for its lack of Arousal when squared under the Euclidean norm.
3. **Affective polarity:** It conflates positive valence progress with negative valence threats.

### 2. Is the M-H compression primarily magnitude, direction, component, or exposure related under the frozen regime?
**Answer (Consistent with):**  
Under the frozen G1 regime, **the observed compression is more consistent with a geometric/measurement interaction than with the previously observed dynamical headroom effect alone**:
- It is **NOT** an input feature representation defect: Candidate G1 has clean, widely separated input features ($D_M = 81.52$, angle $103.06^\circ$).
- Rather than asserting complete absence of physiological saturation, the empirical evidence demonstrates that limbic state displacement continues through $T=25$ and up to $T=100$; thus, compression is more consistently explained by component divergence projected onto an isotropic norm than by an absolute dynamical limit of the ODE.
- It **IS** a component divergence: Medium activates Pleasure; High activates Arousal. Both share a common-mode Dominance displacement ($\Delta D \approx +0.35 - +0.39$).
- When both vectors are measured with isotropic Euclidean norm $S$, their scalar lengths happen to fall within $0.10$ of each other at $T=12$ ($S_M = 0.5364, S_H = 0.6418$). Thus, the apparent compression under scalar $S$ is primarily driven by measuring orthogonal multi-dimensional displacements with a 1-dimensional isotropic ruler.

### 3. Can conversationally realistic $T \le 25$ satisfy the existing scalar Gate 2 thresholds?
**Answer (Observed):**  
**Current dual Gate 2 thresholds are not simultaneously achieved for $T \le 25$ under the frozen G1 stimulus set and current scalar $S$ measurement.**  
At $T=25$ ($2.5\text{s}$ exposure), $\Delta_{ML} = +0.2139$ (PASS) and $\Delta_{HM} = +0.1476$ (FAIL vs. $0.1500$). While $\Delta_{HM}$ approaches the threshold within $0.0024$ at $T=25$, it does not cross it. Both thresholds are simultaneously achieved only from $T \ge 50$ ticks ($5.0\text{s}$), which exceeds conversational realism.

### 4. Do component/directional diagnostics reveal a stable distinction hidden by scalar magnitude?
**Answer (Observed & Supported):**  
**Yes, decisively.**  
- In Arousal, High exceeds Medium with an effect size of Cohen's $d = +9.55$ ($T=12$) and $+9.61$ ($T=25$). The $95\%$ confidence interval for the Arousal difference at $T=12$ is $[+0.2684, +0.2825]$, completely excluding zero.
- In Pleasure, Medium exceeds High by Cohen's $d = -0.94$ ($95\%$ CI: $[-0.3896, -0.2462]$).
- In Directional Projections, High projects negatively onto the Medium axis ($-0.0809$) and Medium projects negatively onto the High axis ($-0.0855$), while the angle between their inter-tier vectors is $\theta(\mathbf{v}_M, \mathbf{v}_H) = 108.66^\circ$.
These diagnostics demonstrate that Medium and High are cleanly and stably distinct at every exposure duration, but that scalar Euclidean surprise masks this separation.

### 5. What evidence is required before considering Protocol v1.5?
**Answer (Governance & Methodological Requirement):**  
Before any Protocol v1.5 can even be contemplated:
1. **Measurement Direction Determination:** An architectural decision must first determine whether manipulation checks should evaluate component-wise displacements ($[\Delta P, \Delta A]$) or directional projections ($\text{Proj}$), or whether manipulation checks must strictly remain scalar Euclidean.
2. **Exploratory Headroom Calculations (Hypothetical Only):** If future research explores retaining scalar Euclidean surprise, any proposed threshold feasibility would require formal mathematical calibration to empirical headroom. For example, hypothetical calculations such as $\Delta_{\text{demand}} \le 0.60 \times H(T)$ (which would correspond to $\approx 0.15$ total demand at $T=12$) are strictly exploratory illustrative figures. They are **NOT** proposed thresholds, are **NOT** authorized, and possess no independent empirical justification in this study. No threshold adjustment is authorized by this report.
3. **Architectural Decision Pending (Not Premature):** Because Gate 2 remains `UNRESOLVED` and Protocol v1.5 is `NOT AUTHORIZED`, an Architectural Decision Record (ADR) is not a scheduled requirement at this stage. Any architectural decision must follow project governance choices on the measurement direction and independently ratified methodology. This study provides empirical evidence to inform that future governance decision, but does not trigger or predetermine it.

### 6. What should remain explicitly unresolved?
**Answer (Epistemic Boundaries):**  
The following questions remain explicitly unresolved and must not be inferred from this study:
1. **Universal Ceiling:** $S_{\text{ceiling}}(T)$ is an empirical ceiling under the frozen High stimulus set; the universal mathematical maximum of `EmotionCore` under arbitrary non-stationary stimuli remains unknown.
2. **Production Surprise Formulation:** Whether Active Inference in production should transition from scalar $S$ to vector-valued prediction residuals $\mathbf{s}_{\text{vec}}$ or component-weighted surprise is an open architectural question requiring independent theoretical derivation.
3. **Dynamic Multi-Turn Conversations:** This study examined single-turn fixed exposures. How directional trajectories interact across multi-turn conversational histories with homeostatic recovery remains uninvestigated.

---

## 9. Governance Sign-off Matrix

| Field | Value / State |
|---|---|
| **Phase 22 H1 Overall Status** | `INCONCLUSIVE — BLOCKED BY QUALITY GATE 2` |
| **Gate 2 Empirical Status** | `Current dual Gate 2 thresholds are not simultaneously achieved for T <= 25 under the frozen G1 stimulus set and current scalar S measurement.` |
| **Protocol v1.5 Status** | `NOT AUTHORIZED` |
| **Architecture Gate** | `STRICTLY LOCKED` |
| **Production Runtime (`src/core/**`)** | `0 MUTATIONS (100% CLEAN)` |
| **Genesis Onboarding Profile (`data/profile.json`)** | `BIT-EXACT UNTOUCHED ({"is_onboarded": false})` |
| **Historical H1 Benchmark Data** | `IMMUTABLE` |
| **Study Completion Timestamp** | `2026-09-16T16:34:40Z` |
| **Authorizing Agent** | Antigravity (Execution & Research Agent) |
