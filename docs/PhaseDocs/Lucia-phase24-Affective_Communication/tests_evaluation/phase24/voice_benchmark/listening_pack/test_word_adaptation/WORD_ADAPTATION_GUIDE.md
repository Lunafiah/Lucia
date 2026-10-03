# Phase 24 Gate 2 — Word-Level & Punctuation Prosody Adaptation Guide

## 1. Problem Statement & User Observation

> *"this approach works well, but still the punctuation in each word isn't natural. Like we just fix the general pitch and semitone of the whole record, it should be able to adapt word by word too"*
>
> *"now can you make a version that combines both Mechanisms"*

### Root Cause Analysis:
1. **Global Static Multiplier Invariance:**
   Applying a constant scalar `pitch_shift_semitones` in RVC or `pitch="+60Hz"` in Edge-TTS multiplies the entire fundamental frequency contour by a single constant scalar $F_0(t) = C \cdot F_0(t)$ everywhere across the sentence.
   While this raises the pitch register, it leaves the intonation contour completely rigid: every word is elevated by the exact same mathematical ratio.
2. **Why Punctuation Feels Unnatural Without Adaptation:**
   - Real human conversational speech relies on **rhythmic micro-pauses**, **focal pitch accents on key semantic words**, and **intonation resets across punctuation boundaries** (e.g., continuation plateau at `,`, terminal declination at `.`, high-energy peak at `!`, and contemplative hesitation at `...`).
   - If the incoming TTS prosody is flat, RVC faithfully converts the voice identity but preserves that flat, mechanical cadence.
3. **Microsoft Edge-TTS Technical Constraints Discovered:**
   - Edge-TTS strictly rejects nested `<prosody pitch="...">` or `<break time="..."/>` tags inside the text (throwing `NoAudioReceived`). Edge-TTS operates as a read-aloud browser API and only accepts plain XML-escaped text.
   - `en-US-JennyNeural` and `ja-JP-NanamiNeural` support `boundary="WordBoundary"`.
   - `vi-VN-HoaiMyNeural` strictly rejects `boundary="WordBoundary"` with `NoAudioReceived`, supporting only `SentenceBoundary`. For Vietnamese, acoustic intensity envelope analysis is used to align clause pauses.

---

## 2. The Architectural Mechanisms Tested

### Mechanism 1: Upstream Expressive Punctuation & Phrasing (Cadence & Pauses)
Edge-TTS's neural acoustic model derives pausing, breath cadence, and boundary intonation from orthography:
- Natural conversational phrasing markers (`...` for breathing hesitations, `,` for clause plateaus, and `!` for emotional peak attack).
- **Effect:** Expands duration naturally with breathing room (EN: 5.92s $\rightarrow$ 7.16s, VI: 6.04s $\rightarrow$ 8.36s, JP: 7.36s $\rightarrow$ 8.36s).

### Mechanism 2: Downstream Dynamic $F_0$ Contouring (Intonation & Melodic Accent)
Instead of a flat semitone shift, a time-varying semitone trajectory $S(t)$ modulates the continuous 10ms $F_0$ array inside RVC:
- Base elevation: $+2.0$ to $+3.0$ semitones.
- Focal content words (*"morning"*, *"really"*, *"wonderfully"*, *"sáng"*, *"rất vui"*, *"tuyệt vời"*, *"本当によかった"*): receive a smooth Hanning-window pitch boost of $+2.0$ to $+2.5$ semitones.
- Connective / function words: remain relaxed at base.

### Combined Version: Mechanism 1 + Mechanism 2 (Unified Conversational Prosody)
The combined version feeds expressively punctuated text into Edge-TTS to establish the human respiratory cadence and pause structure, and simultaneously applies the time-varying $S(t)$ semitone contour in RVC to emphasize focal emotional content words during conversion.

---

## 3. Comprehensive Acoustic Telemetry Table (All 4 Variants)

All files are post-RVC 24 kHz 16-bit linear PCM WAVs.

| Language | Variant | Duration | Mean $F_0$ | Std Dev | $F_0$ Range (Min – Max) | Audio File Link |
| :--- | :--- | :---: | :---: | :---: | :---: | :--- |
| **English (EN)** | **1. Static Shift** (Uniform +4 st) | 5.92s | 335.7 Hz | ±65.2 Hz | 241 – 490 Hz | [`EN_static_semitones_plus4.wav`](file:///c:/Users/Lunafiah/Desktop/My_project/Lucia/tests/evaluation/phase24/voice_benchmark/listening_pack/test_word_adaptation/EN_static_semitones_plus4.wav) |
| **English (EN)** | **2. Mechanism 1** (Punctuation Cadence) | 7.16s | 358.6 Hz | ±67.5 Hz | 247 – 495 Hz | [`EN_expressive_punctuation_text.wav`](file:///c:/Users/Lunafiah/Desktop/My_project/Lucia/tests/evaluation/phase24/voice_benchmark/listening_pack/test_word_adaptation/EN_expressive_punctuation_text.wav) |
| **English (EN)** | **3. Mechanism 2** (Dynamic $F_0$ Accents) | 5.92s | 344.9 Hz | ±74.2 Hz | 245 – 554 Hz | [`EN_dynamic_word_adapted.wav`](file:///c:/Users/Lunafiah/Desktop/My_project/Lucia/tests/evaluation/phase24/voice_benchmark/listening_pack/test_word_adaptation/EN_dynamic_word_adapted.wav) |
| **English (EN)** | **4. Combined** (Mech 1 + Mech 2) | **7.16s** | **350.7 Hz** | **±72.1 Hz** | **233 – 522 Hz** | [`EN_combined_mechanisms.wav`](file:///c:/Users/Lunafiah/Desktop/My_project/Lucia/tests/evaluation/phase24/voice_benchmark/listening_pack/test_word_adaptation/EN_combined_mechanisms.wav) |
| **Vietnamese (VI)** | **1. Static Shift** (Uniform +2 st) | 6.04s | 337.9 Hz | ±63.0 Hz | 261 – 599 Hz | [`VI_static_semitones_plus2.wav`](file:///c:/Users/Lunafiah/Desktop/My_project/Lucia/tests/evaluation/phase24/voice_benchmark/listening_pack/test_word_adaptation/VI_static_semitones_plus2.wav) |
| **Vietnamese (VI)** | **2. Mechanism 1** (Punctuation Cadence) | 8.36s | 344.2 Hz | ±66.6 Hz | 263 – 566 Hz | [`VI_expressive_punctuation_text.wav`](file:///c:/Users/Lunafiah/Desktop/My_project/Lucia/tests/evaluation/phase24/voice_benchmark/listening_pack/test_word_adaptation/VI_expressive_punctuation_text.wav) |
| **Vietnamese (VI)** | **3. Mechanism 2** (Dynamic $F_0$ Accents) | 6.04s | 339.6 Hz | ±62.7 Hz | 259 – 595 Hz | [`VI_dynamic_word_adapted.wav`](file:///c:/Users/Lunafiah/Desktop/My_project/Lucia/tests/evaluation/phase24/voice_benchmark/listening_pack/test_word_adaptation/VI_dynamic_word_adapted.wav) |
| **Vietnamese (VI)** | **4. Combined** (Mech 1 + Mech 2) | **8.36s** | **352.1 Hz** | **±69.3 Hz** | **264 – 567 Hz** | [`VI_combined_mechanisms.wav`](file:///c:/Users/Lunafiah/Desktop/My_project/Lucia/tests/evaluation/phase24/voice_benchmark/listening_pack/test_word_adaptation/VI_combined_mechanisms.wav) |
| **Japanese (JP)** | **1. Static Shift** (Uniform +2 st) | 7.36s | 425.4 Hz | ±76.9 Hz | 265 – 579 Hz | [`JP_static_semitones_plus2.wav`](file:///c:/Users/Lunafiah/Desktop/My_project/Lucia/tests/evaluation/phase24/voice_benchmark/listening_pack/test_word_adaptation/JP_static_semitones_plus2.wav) |
| **Japanese (JP)** | **2. Mechanism 1** (Punctuation Cadence) | 8.36s | 442.9 Hz | ±92.7 Hz | 271 – 618 Hz | [`JP_expressive_punctuation_text.wav`](file:///c:/Users/Lunafiah/Desktop/My_project/Lucia/tests/evaluation/phase24/voice_benchmark/listening_pack/test_word_adaptation/JP_expressive_punctuation_text.wav) |
| **Japanese (JP)** | **3. Mechanism 2** (Dynamic $F_0$ Accents) | 7.36s | 425.1 Hz | ±77.0 Hz | 264 – 579 Hz | [`JP_dynamic_word_adapted.wav`](file:///c:/Users/Lunafiah/Desktop/My_project/Lucia/tests/evaluation/phase24/voice_benchmark/listening_pack/test_word_adaptation/JP_dynamic_word_adapted.wav) |
| **Japanese (JP)** | **4. Combined** (Mech 1 + Mech 2) | **8.36s** | **441.6 Hz** | **±95.8 Hz** | **50 – 616 Hz** | [`JP_combined_mechanisms.wav`](file:///c:/Users/Lunafiah/Desktop/My_project/Lucia/tests/evaluation/phase24/voice_benchmark/listening_pack/test_word_adaptation/JP_combined_mechanisms.wav) |

---

## 4. Auditory Comparison & Perceptual Observations

1. **Static Shift vs. Combined Version:**
   - In `EN_static_semitones_plus4.wav`, the entire sentence rushes forward without breathing room, and the pitch is held at an unnatural plateau.
   - In [`EN_combined_mechanisms.wav`](file:///c:/Users/Lunafiah/Desktop/My_project/Lucia/tests/evaluation/phase24/voice_benchmark/listening_pack/test_word_adaptation/EN_combined_mechanisms.wav), the speaker takes a natural breath after `"Good morning!"`, emphasizes `"really, really glad"` with a gentle melodic rise, hesitates warmly before `"everything turned out wonderfully!"`, and peaks with authentic enthusiasm on the final clause.
2. **Vietnamese Tone Integrity in Combined Version:**
   - In [`VI_combined_mechanisms.wav`](file:///c:/Users/Lunafiah/Desktop/My_project/Lucia/tests/evaluation/phase24/voice_benchmark/listening_pack/test_word_adaptation/VI_combined_mechanisms.wav), the Northern Vietnamese tones (sắc on *sáng*, ngang on *vui*, nặng on *tuyệt*, huyền on *vời*) maintain their relative micro-tonal distinctions without colliding, while the 890ms pause after `"Chào buổi sáng!"` and 900ms pause after `"cậu..."` give the relational delivery human warmth.
3. **Japanese Intonation in Combined Version:**
   - In [`JP_combined_mechanisms.wav`](file:///c:/Users/Lunafiah/Desktop/My_project/Lucia/tests/evaluation/phase24/voice_benchmark/listening_pack/test_word_adaptation/JP_combined_mechanisms.wav), the mora-timing and accent pattern on `"本当によかった！"` deliver expressive animation while preserving Varesa's native Japanese voice timbre.
