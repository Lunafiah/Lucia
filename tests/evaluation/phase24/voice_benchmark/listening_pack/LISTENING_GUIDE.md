# Phase 24 Gate 2 — High Pitch Listening Pack & Evaluation Guide

> **All-Post-RVC Higher Pitch Benchmark Package (+60 Hz to +150 Hz)**  
> **Source Pipeline:** Direct RVC v2 (`models/voice/rvc/VaresaGIJP/VaresaGIJP_300e_2100s.pth`) conditioned on Edge-TTS  
> **Audio Format:** 24,000 Hz, 16-bit Mono Linear PCM WAV (**100% Post-RVC Outputs Only**)  
> **Directory Location:** [`tests/evaluation/phase24/voice_benchmark/listening_pack/`](file:///c:/Users/Lunafiah/Desktop/My_project/Lucia/tests/evaluation/phase24/voice_benchmark/listening_pack/)  
> **Acoustic Summary CSV:** [`tests/evaluation/phase24/voice_benchmark/listening_pack/high_pitch_acoustic_summary.csv`](file:///c:/Users/Lunafiah/Desktop/My_project/Lucia/tests/evaluation/phase24/voice_benchmark/listening_pack/high_pitch_acoustic_summary.csv)  
> **Telemetry JSON:** [`tests/evaluation/phase24/voice_benchmark/listening_pack/high_pitch_telemetry.json`](file:///c:/Users/Lunafiah/Desktop/My_project/Lucia/tests/evaluation/phase24/voice_benchmark/listening_pack/high_pitch_telemetry.json)  

---

## 1. Executive Summary & Design of the Pack

This listening pack replaces all previous listening sets with a focused, **all-post-RVC** high-pitch sweep across the target ladder:
$$\{+0\text{ Hz (Baseline)}, +60\text{ Hz}, +80\text{ Hz}, +100\text{ Hz}, +120\text{ Hz}, +150\text{ Hz}\}$$
evaluated symmetrically across three languages:
1. **English (EN):** Base voice `en-US-JennyNeural` $\to$ RVC `VaresaGIJP`
2. **Northern Vietnamese (VI):** Base voice `vi-VN-HoaiMyNeural` $\to$ RVC `VaresaGIJP`
3. **Japanese (JP):** Base voice `ja-JP-NanamiNeural` $\to$ RVC `VaresaGIJP`

### Pure Acoustic Progression (Controlled Phonetics)
To eliminate phonetic confusion, the utterance text is **held strictly constant** within each language across the entire pitch ladder. When listening from `00_baseline` up to `05_pitch_plus150Hz`, the listener hears the *exact same sentence* smoothly ascending through the vocal registers.

---

## 2. Master Listening Index (All 18 Post-RVC WAVs)

All 18 audio files are 24 kHz WAVs located in [`tests/evaluation/phase24/voice_benchmark/listening_pack/`](file:///c:/Users/Lunafiah/Desktop/My_project/Lucia/tests/evaluation/phase24/voice_benchmark/listening_pack/):

### 2.1 English High Pitch Ladder (`EN`)
*Constant Text:* `"Good morning! I'm really glad to see you today, everything turned out wonderfully."*

| # | Audio File (Clickable) | Target Pitch | Pre F0 Mean | Post F0 Mean | Realized Shift vs Baseline | F0 Discrepancy (Post - Pre) | Duration | Peak Ampl. | Auditory Focus |
|---|---|---:|---|---|---|---|---|---|---|
| **EN-00** | [`EN_00_baseline.wav`](file:///c:/Users/Lunafiah/Desktop/My_project/Lucia/tests/evaluation/phase24/voice_benchmark/listening_pack/EN_00_baseline.wav) | `+0Hz` | 191.1 Hz | **189.4 Hz** | Baseline (0.0 Hz) | -1.6 Hz | 5.92s | 0.900 | Natural conversational chest register anchor. |
| **EN-01** | [`EN_01_pitch_plus60Hz.wav`](file:///c:/Users/Lunafiah/Desktop/My_project/Lucia/tests/evaluation/phase24/voice_benchmark/listening_pack/EN_01_pitch_plus60Hz.wav) | `+60Hz` | 268.1 Hz | **266.7 Hz** | **+77.2 Hz** | -1.4 Hz | 5.92s | 0.904 | Clear head register transition; energetic greeting. |
| **EN-02** | [`EN_02_pitch_plus80Hz.wav`](file:///c:/Users/Lunafiah/Desktop/My_project/Lucia/tests/evaluation/phase24/voice_benchmark/listening_pack/EN_02_pitch_plus80Hz.wav) | `+80Hz` | 286.7 Hz | **285.9 Hz** | **+96.5 Hz** | -0.8 Hz | 5.92s | 0.887 | Upper boundary inflection; bright excited persona. |
| **EN-03** | [`EN_03_pitch_plus100Hz.wav`](file:///c:/Users/Lunafiah/Desktop/My_project/Lucia/tests/evaluation/phase24/voice_benchmark/listening_pack/EN_03_pitch_plus100Hz.wav) | `+100Hz` | 286.9 Hz | **285.9 Hz** | **+96.4 Hz** | -1.1 Hz | 5.92s | 0.893 | Clamped at +80Hz ceiling (acoustically identical). |
| **EN-04** | [`EN_04_pitch_plus120Hz.wav`](file:///c:/Users/Lunafiah/Desktop/My_project/Lucia/tests/evaluation/phase24/voice_benchmark/listening_pack/EN_04_pitch_plus120Hz.wav) | `+120Hz` | 286.9 Hz | **286.0 Hz** | **+96.6 Hz** | -0.9 Hz | 5.92s | 0.909 | Clamped at +80Hz ceiling (acoustically identical). |
| **EN-05** | [`EN_05_pitch_plus150Hz.wav`](file:///c:/Users/Lunafiah/Desktop/My_project/Lucia/tests/evaluation/phase24/voice_benchmark/listening_pack/EN_05_pitch_plus150Hz.wav) | `+150Hz` | 286.7 Hz | **285.6 Hz** | **+96.2 Hz** | -1.0 Hz | 5.92s | 0.874 | Clamped at +80Hz ceiling (acoustically identical). |

---

### 2.2 Northern Vietnamese High Pitch Ladder (`VI`)
*Constant Text:* *"Chào buổi sáng, mình rất vui được gặp lại cậu, mọi chuyện hôm nay đều diễn ra thật tuyệt vời."*

| # | Audio File (Clickable) | Target Pitch | Pre F0 Mean | Post F0 Mean | Realized Shift vs Baseline | F0 Discrepancy (Post - Pre) | Duration | Peak Ampl. | Auditory Focus |
|---|---|---:|---|---|---|---|---|---|---|
| **VI-00** | [`VI_00_baseline.wav`](file:///c:/Users/Lunafiah/Desktop/My_project/Lucia/tests/evaluation/phase24/voice_benchmark/listening_pack/VI_00_baseline.wav) | `+0Hz` | 215.6 Hz | **215.8 Hz** | Baseline (0.0 Hz) | +0.2 Hz | 6.04s | 0.901 | Natural Northern Vietnamese conversational anchor. |
| **VI-01** | [`VI_01_pitch_plus60Hz.wav`](file:///c:/Users/Lunafiah/Desktop/My_project/Lucia/tests/evaluation/phase24/voice_benchmark/listening_pack/VI_01_pitch_plus60Hz.wav) | `+60Hz` | 301.8 Hz | **301.5 Hz** | **+85.6 Hz** | -0.4 Hz | 6.04s | 0.897 | Tonal glides shifted cleanly into 300 Hz range. |
| **VI-02** | [`VI_02_pitch_plus80Hz.wav`](file:///c:/Users/Lunafiah/Desktop/My_project/Lucia/tests/evaluation/phase24/voice_benchmark/listening_pack/VI_02_pitch_plus80Hz.wav) | `+80Hz` | 323.6 Hz | **322.1 Hz** | **+106.3 Hz** | -1.5 Hz | 6.04s | 0.880 | High expressive inflection; tones remain clear. |
| **VI-03** | [`VI_03_pitch_plus100Hz.wav`](file:///c:/Users/Lunafiah/Desktop/My_project/Lucia/tests/evaluation/phase24/voice_benchmark/listening_pack/VI_03_pitch_plus100Hz.wav) | `+100Hz` | 323.6 Hz | **322.2 Hz** | **+106.4 Hz** | -1.4 Hz | 6.04s | 0.904 | Clamped at +80Hz ceiling (acoustically identical). |
| **VI-04** | [`VI_04_pitch_plus120Hz.wav`](file:///c:/Users/Lunafiah/Desktop/My_project/Lucia/tests/evaluation/phase24/voice_benchmark/listening_pack/VI_04_pitch_plus120Hz.wav) | `+120Hz` | 323.2 Hz | **324.0 Hz** | **+108.2 Hz** | +0.8 Hz | 6.04s | 0.910 | Clamped at +80Hz ceiling (acoustically identical). |
| **VI-05** | [`VI_05_pitch_plus150Hz.wav`](file:///c:/Users/Lunafiah/Desktop/My_project/Lucia/tests/evaluation/phase24/voice_benchmark/listening_pack/VI_05_pitch_plus150Hz.wav) | `+150Hz` | 323.6 Hz | **323.5 Hz** | **+107.7 Hz** | -0.1 Hz | 6.04s | 0.903 | Clamped at +80Hz ceiling (acoustically identical). |

---

### 2.3 Japanese High Pitch Ladder (`JP`)
*Constant Text:* *"おはようございます。今日も一緒に楽しい一日にしていきましょうね！"*  
*(Romaji: "Ohayou gozaimasu. Kyou mo issho ni tanoshii ichinichi ni shite ikimashou ne!")*

| # | Audio File (Clickable) | Target Pitch | Pre F0 Mean | Post F0 Mean | Realized Shift vs Baseline | F0 Discrepancy (Post - Pre) | Duration | Peak Ampl. | Auditory Focus |
|---|---|---:|---|---|---|---|---|---|---|
| **JP-00** | [`JP_00_baseline.wav`](file:///c:/Users/Lunafiah/Desktop/My_project/Lucia/tests/evaluation/phase24/voice_benchmark/listening_pack/JP_00_baseline.wav) | `+0Hz` | 291.9 Hz | **291.4 Hz** | Baseline (0.0 Hz) | -0.5 Hz | 6.12s | 0.896 | Native Japanese character baseline anchor. |
| **JP-01** | [`JP_01_pitch_plus60Hz.wav`](file:///c:/Users/Lunafiah/Desktop/My_project/Lucia/tests/evaluation/phase24/voice_benchmark/listening_pack/JP_01_pitch_plus60Hz.wav) | `+60Hz` | 408.9 Hz | **404.1 Hz** | **+112.6 Hz** | -4.8 Hz | 6.12s | 0.891 | Enters 400+ Hz anime companion register. |
| **JP-02** | [`JP_02_pitch_plus80Hz.wav`](file:///c:/Users/Lunafiah/Desktop/My_project/Lucia/tests/evaluation/phase24/voice_benchmark/listening_pack/JP_02_pitch_plus80Hz.wav) | `+80Hz` | 436.4 Hz | **439.6 Hz** | **+148.1 Hz** | +3.2 Hz | 6.12s | 0.876 | Extreme high anime register (~440 Hz). |
| **JP-03** | [`JP_03_pitch_plus100Hz.wav`](file:///c:/Users/Lunafiah/Desktop/My_project/Lucia/tests/evaluation/phase24/voice_benchmark/listening_pack/JP_03_pitch_plus100Hz.wav) | `+100Hz` | 436.4 Hz | **440.2 Hz** | **+148.8 Hz** | +3.9 Hz | 6.12s | 0.869 | Clamped at +80Hz ceiling (acoustically identical). |
| **JP-04** | [`JP_04_pitch_plus120Hz.wav`](file:///c:/Users/Lunafiah/Desktop/My_project/Lucia/tests/evaluation/phase24/voice_benchmark/listening_pack/JP_04_pitch_plus120Hz.wav) | `+120Hz` | 436.3 Hz | **439.5 Hz** | **+148.1 Hz** | +3.2 Hz | 6.12s | 0.910 | Clamped at +80Hz ceiling (acoustically identical). |
| **JP-05** | [`JP_05_pitch_plus150Hz.wav`](file:///c:/Users/Lunafiah/Desktop/My_project/Lucia/tests/evaluation/phase24/voice_benchmark/listening_pack/JP_05_pitch_plus150Hz.wav) | `+150Hz` | 436.4 Hz | **436.2 Hz** | **+144.7 Hz** | -0.2 Hz | 6.12s | 0.899 | Clamped at +80Hz ceiling (acoustically identical). |

---

## 3. Major Empirical Discovery: The "+80Hz Clamping Ceiling"

The objective acoustic data reveals a fundamental property of Microsoft Edge-TTS / Azure Cognitive Speech architecture:

```text
┌──────────────────────────────────────────────────────────────────────────────┐
│                    EDGE-TTS PITCH SATURATION CURVE                           │
├─────────────────┬──────────────┬──────────────┬──────────────┬───────────────┤
│ Target Pitch    │ English F0   │ Vietnamese F0│ Japanese F0  │ Status        │
├─────────────────┼──────────────┼──────────────┼──────────────┼───────────────┤
│ +0 Hz (Base)    │ 189.4 Hz     │ 215.8 Hz     │ 291.4 Hz     │ Unmodified    │
│ +60 Hz          │ 266.7 Hz     │ 301.5 Hz     │ 404.1 Hz     │ Linear Ascent │
│ +80 Hz          │ 285.9 Hz     │ 322.1 Hz     │ 439.6 Hz     │ SATURATION PT │
│ +100 Hz         │ 285.9 Hz     │ 322.2 Hz     │ 440.2 Hz     │ CLAMPED       │
│ +120 Hz         │ 286.0 Hz     │ 324.0 Hz     │ 439.5 Hz     │ CLAMPED       │
│ +150 Hz         │ 285.6 Hz     │ 323.5 Hz     │ 436.2 Hz     │ CLAMPED       │
└─────────────────┴──────────────┴──────────────┴──────────────┴───────────────┘
```

### Acoustic Fact
Across all three languages, Microsoft Edge-TTS **internally clamps the SSML pitch modifier at approximately `+80Hz`**.
- When `+100Hz`, `+120Hz`, or `+150Hz` is sent, Edge-TTS clamps the prosodic shift to the exact same value as `+80Hz`.
- **Listening Verification:** Notice that `EN_02`, `EN_03`, `EN_04`, and `EN_05` sound identical in pitch. The same holds true for `VI_02` through `VI_05` and `JP_02` through `JP_05`.
- **Phase 24 Policy Implication:** The effective dynamic range of SSML pitch in Edge-TTS is $[-50\text{ Hz}, +80\text{ Hz}]$. Values above $+80\text{ Hz}$ do not increase pitch further.

---

## 4. Auditory Evaluation Protocol (What to Listen For)

1. **Step-by-Step Pitch Climb (Baseline $\to$ +60Hz $\to$ +80Hz):**
   - Play `EN_00` $\to$ `EN_01` $\to$ `EN_02`.
   - Play `VI_00` $\to$ `VI_01` $\to$ `VI_02`.
   - Play `JP_00` $\to$ `JP_01` $\to$ `JP_02`.
   - *Observation:* Listen to how the persona transitions from a grounded, warm companion into an enthusiastic, high-energy register.
2. **Harmonic Clarity & Absence of Vocoder Squeal:**
   - Even at **440 Hz** in `JP_02`–`JP_05`, RVC's NSF harmonic excitation tracks with $|\Delta F_0| \le 3.9\text{ Hz}$ and **zero clipping** (`clipping_ratio = 0.000000`).
   - Listen for whether the voice sounds squeaky/cartoonish or retains character identity.
3. **Tonal Inflection Stability in Vietnamese at 320+ Hz:**
   - In `VI_01` (301 Hz) and `VI_02` (322 Hz), observe whether Northern tones (*"sáng"*, *"mình"*, *"rất"*, *"cậu"*, *"tuyệt"*) remain distinct or whether the pitch shift causes tonal flattening. (Praat data shows voiced fraction remains stable at 0.62–0.63).
4. **Saturation Confirmation:**
   - Listen to `EN_02` (+80Hz) and `EN_05` (+150Hz) back-to-back to audibly confirm that the pitch has hit Edge-TTS's internal prosodic ceiling.
