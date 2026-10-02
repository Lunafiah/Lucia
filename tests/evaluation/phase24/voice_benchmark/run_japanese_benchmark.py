"""
tests/evaluation/phase24/voice_benchmark/run_japanese_benchmark.py

Phase 24 Gate 2 — Japanese Listening Benchmark Supplement.
Executes the production voice pipeline (Edge-TTS ja-JP-NanamiNeural -> Direct RVC v2 VaresaGIJP)
across 6 representative Japanese conversational test cases.
Measures acoustic metrics and generates listening pack WAV files.
"""

from __future__ import annotations

import asyncio
import io
import json
import logging
import os
import sys
import time
import wave
from pathlib import Path
from typing import Any, Dict, List, Tuple

import edge_tts
import numpy as np
import parselmouth

# Add project root to sys.path
PROJECT_ROOT = Path(__file__).resolve().parents[4]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from src.core.voice.rvc_pipeline import RVCPipeline, decode_audio_to_16k

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger("P24JapaneseBenchmark")

JP_TEST_CASES = [
    {
        "id": "JP-01",
        "file_prefix": "JP_01_baseline",
        "text": "おはようございます。今日も穏やかな一日になりそうですね。",
        "romaji": "Ohayou gozaimasu. Kyou mo odayaka na ichinichi ni narisou desu ne.",
        "meaning": "Good morning. It looks like today will be another peaceful day.",
        "pitch_hz": 0,
        "pitch_str": "+0Hz",
        "rate_percent": 0,
        "rate_str": "+0%",
        "purpose": "Native-language baseline timbre & conversational greeting",
    },
    {
        "id": "JP-02",
        "file_prefix": "JP_02_pitch_plus15",
        "text": "お疲れ様でした。温かいお茶でも淹れましょうか？",
        "romaji": "Otsukaresama deshita. Atatakai ocha demo iremashou ka?",
        "meaning": "Thank you for your hard work. Shall I make some warm tea for you?",
        "pitch_hz": 15,
        "pitch_str": "+15Hz",
        "rate_percent": 0,
        "rate_str": "+0%",
        "purpose": "Moderate upward pitch (+15 Hz), gentle caring inquiry",
    },
    {
        "id": "JP-03",
        "file_prefix": "JP_03_pitch_minus15",
        "text": "少し静かにして、落ち着いて考えてみましょう。",
        "romaji": "Sukoshi shizuka ni shite, ochitsuite kangaete mimashou.",
        "meaning": "Let's be quiet for a moment, and think about it calmly.",
        "pitch_hz": -15,
        "pitch_str": "-15Hz",
        "rate_percent": 0,
        "rate_str": "+0%",
        "purpose": "Moderate downward pitch (-15 Hz), subdued/comforting register",
    },
    {
        "id": "JP-04",
        "file_prefix": "JP_04_pitch_plus30",
        "text": "すごいですね！本当にうまくいって良かったです！",
        "romaji": "Sugoi desu ne! Hontou ni umaku itte yokatta desu!",
        "meaning": "That's amazing! I'm so glad everything worked out well!",
        "pitch_hz": 30,
        "pitch_str": "+30Hz",
        "rate_percent": 0,
        "rate_str": "+0%",
        "purpose": "Upper pitch boundary (+30 Hz), high-valence joyful inflection",
    },
    {
        "id": "JP-05",
        "file_prefix": "JP_05_rate_plus20",
        "text": "時間がありません、急いで次のステップへ進みましょう。",
        "romaji": "Jikan ga arimasen, isoide tsugi no suteppu e susumimashou.",
        "meaning": "We don't have much time, let's hurry and move to the next step.",
        "pitch_hz": 0,
        "pitch_str": "+0Hz",
        "rate_percent": 20,
        "rate_str": "+20%",
        "purpose": "Faster speech rate (+20%), brisk tempo, consonant clarity under speed",
    },
    {
        "id": "JP-06",
        "file_prefix": "JP_06_rate_minus20",
        "text": "焦らなくても大丈夫ですよ。ゆっくり進めればいいんです。",
        "romaji": "Asaranakutemo daijoubu desu yo. Yukkuri susumereba ii n desu.",
        "meaning": "There is no need to rush. It's completely fine to take it slowly.",
        "pitch_hz": 0,
        "pitch_str": "+0Hz",
        "rate_percent": -20,
        "rate_str": "-20%",
        "purpose": "Slower speech rate (-20%), deliberate relaxed pacing, vowel glide stability",
    },
]


def decode_wav_to_float(wav_bytes: bytes) -> Tuple[np.ndarray, int]:
    with wave.open(io.BytesIO(wav_bytes), "rb") as wf:
        n_channels = wf.getnchannels()
        sampwidth = wf.getsampwidth()
        sr = wf.getframerate()
        n_frames = wf.getnframes()
        frames = wf.readframes(n_frames)

    if sampwidth == 2:
        raw_int = np.frombuffer(frames, dtype=np.int16)
        if n_channels > 1:
            raw_int = raw_int.reshape(-1, n_channels)[:, 0]
        audio_float = (raw_int.astype(np.float32) / 32768.0)
    else:
        raise ValueError(f"Unsupported sample width: {sampwidth}")

    return audio_float, sr


def compute_acoustic_features(audio: np.ndarray, sr: int) -> Dict[str, Any]:
    duration_s = float(len(audio) / sr)
    if duration_s <= 0.05:
        return {
            "duration_s": duration_s,
            "total_frames": 0,
            "voiced_frames": 0,
            "voiced_fraction": 0.0,
            "f0_mean": 0.0,
            "f0_median": 0.0,
            "f0_std": 0.0,
            "f0_min": 0.0,
            "f0_max": 0.0,
            "octave_jumps": 0,
            "rms": 0.0,
            "peak": 0.0,
            "clipping_ratio": 0.0,
        }

    snd = parselmouth.Sound(audio, sampling_frequency=sr)
    pitch = snd.to_pitch_ac(time_step=0.01, pitch_floor=50.0, pitch_ceiling=600.0)
    f0_arr = pitch.selected_array["frequency"]
    voiced_f0 = f0_arr[f0_arr > 0]

    octave_jumps = 0
    if len(voiced_f0) > 1:
        ratios = voiced_f0[1:] / (voiced_f0[:-1] + 1e-8)
        octave_jumps = int(np.sum((ratios > 1.8) | (ratios < 0.55)))

    clipping_count = int(np.sum(np.abs(audio) >= 0.999))
    clipping_ratio = float(clipping_count / len(audio))

    return {
        "duration_s": round(duration_s, 4),
        "total_frames": int(len(f0_arr)),
        "voiced_frames": int(len(voiced_f0)),
        "voiced_fraction": round(float(len(voiced_f0) / max(1, len(f0_arr))), 4),
        "f0_mean": round(float(np.mean(voiced_f0)), 2) if len(voiced_f0) > 0 else 0.0,
        "f0_median": round(float(np.median(voiced_f0)), 2) if len(voiced_f0) > 0 else 0.0,
        "f0_std": round(float(np.std(voiced_f0)), 2) if len(voiced_f0) > 0 else 0.0,
        "f0_min": round(float(np.min(voiced_f0)), 2) if len(voiced_f0) > 0 else 0.0,
        "f0_max": round(float(np.max(voiced_f0)), 2) if len(voiced_f0) > 0 else 0.0,
        "octave_jumps": octave_jumps,
        "rms": round(float(np.sqrt(np.mean(audio ** 2))), 4),
        "peak": round(float(np.max(np.abs(audio))), 4),
        "clipping_ratio": round(clipping_ratio, 6),
    }


async def run_japanese_benchmark() -> None:
    bench_dir = Path(__file__).resolve().parent
    listening_dir = bench_dir / "japanese_listening"
    listening_dir.mkdir(parents=True, exist_ok=True)

    model_pth = str(PROJECT_ROOT / "models/voice/rvc/VaresaGIJP/VaresaGIJP_300e_2100s.pth")
    index_path = str(PROJECT_ROOT / "models/voice/rvc/VaresaGIJP/added_VaresaGIJP_v2.index")
    voice_name = "ja-JP-NanamiNeural"

    logger.info("Initializing RVCPipeline on CPU...")
    pipeline = RVCPipeline(device="cpu")
    pipeline.load_model(model_pth, index_path)
    pipeline._get_or_load_hubert()

    results: List[Dict[str, Any]] = []
    baseline_f0 = None
    baseline_dur = None

    for idx, tc in enumerate(JP_TEST_CASES, 1):
        tc_id = tc["id"]
        prefix = tc["file_prefix"]
        text = tc["text"]
        pitch_str = tc["pitch_str"]
        rate_str = tc["rate_str"]

        logger.info(
            "[%d/%d] Processing %s (pitch=%s, rate=%s): %s",
            idx, len(JP_TEST_CASES), tc_id, pitch_str, rate_str, text[:25]
        )

        # 1. Edge-TTS Synthesis with retry
        t_edge_start = time.perf_counter()
        edge_bytes = b""
        for attempt in range(1, 4):
            try:
                comm = edge_tts.Communicate(
                    text,
                    voice=voice_name,
                    rate=rate_str,
                    pitch=pitch_str,
                )
                edge_buffer = io.BytesIO()
                async for chunk in comm.stream():
                    if chunk["type"] == "audio":
                        edge_buffer.write(chunk["data"])
                edge_bytes = edge_buffer.getvalue()
                if len(edge_bytes) > 0:
                    break
            except Exception as stream_err:
                logger.warning("Edge-TTS attempt %d failed for %s: %s. Retrying...", attempt, tc_id, stream_err)
                if attempt < 3:
                    await asyncio.sleep(1.5)
                else:
                    raise
        t_edge_end = time.perf_counter()
        edge_latency_ms = (t_edge_end - t_edge_start) * 1000.0

        pre_audio_16k = decode_audio_to_16k(edge_bytes)
        pre_metrics = compute_acoustic_features(pre_audio_16k, 16000)

        # 2. Direct RVC v2 Conversion
        t_rvc_start = time.perf_counter()
        rvc_res = pipeline.convert(
            base_audio=edge_bytes,
            pth_path=model_pth,
            index_path=index_path,
            model_name="VaresaGIJP",
            index_rate=0.25,
            pitch_shift_semitones=0,
        )
        t_rvc_end = time.perf_counter()
        rvc_latency_ms = (t_rvc_end - t_rvc_start) * 1000.0
        total_latency_ms = (t_rvc_end - t_edge_start) * 1000.0

        assert rvc_res.rvc_applied and rvc_res.execution_status == "success", f"RVC conversion failed for {tc_id}"
        post_audio_24k, post_sr = decode_wav_to_float(rvc_res.audio_bytes)
        post_metrics = compute_acoustic_features(post_audio_24k, post_sr)

        # Save WAV output in listening pack
        wav_path = listening_dir / f"{prefix}.wav"
        with open(wav_path, "wb") as f_out:
            f_out.write(rvc_res.audio_bytes)

        # Save Pre-RVC reference
        pre_mp3_path = listening_dir / f"{prefix}_pre.mp3"
        with open(pre_mp3_path, "wb") as f_out:
            f_out.write(edge_bytes)

        if tc_id == "JP-01":
            baseline_f0 = post_metrics["f0_mean"]
            baseline_dur = post_metrics["duration_s"]

        realized_post_f0_shift = round(post_metrics["f0_mean"] - baseline_f0, 2)
        rvc_f0_discrepancy = round(post_metrics["f0_mean"] - pre_metrics["f0_mean"], 2)
        dur_preservation_ratio = round(post_metrics["duration_s"] / max(0.01, pre_metrics["duration_s"]), 4)
        rtf = round(total_latency_ms / max(1.0, post_metrics["duration_s"] * 1000.0), 3)

        item = {
            "id": tc_id,
            "file": f"{prefix}.wav",
            "text": text,
            "romaji": tc["romaji"],
            "meaning": tc["meaning"],
            "purpose": tc["purpose"],
            "target_pitch_hz": tc["pitch_hz"],
            "target_pitch_str": tc["pitch_str"],
            "target_rate_percent": tc["rate_percent"],
            "target_rate_str": tc["rate_str"],
            "latencies": {
                "edge_tts_ms": round(edge_latency_ms, 2),
                "rvc_ms": round(rvc_latency_ms, 2),
                "total_ms": round(total_latency_ms, 2),
                "real_time_factor": rtf,
            },
            "pre_rvc": pre_metrics,
            "post_rvc": post_metrics,
            "derived": {
                "realized_post_f0_shift_hz": realized_post_f0_shift,
                "rvc_f0_discrepancy_hz": rvc_f0_discrepancy,
                "duration_preservation_ratio": dur_preservation_ratio,
            },
        }
        results.append(item)

    # Save JSON telemetry
    telemetry_path = bench_dir / "japanese_telemetry.json"
    with open(telemetry_path, "w", encoding="utf-8") as f:
        json.dump({"results": results}, f, indent=2, ensure_ascii=False)
    logger.info("Saved Japanese telemetry to: %s", telemetry_path)

    # Save CSV summary
    csv_path = bench_dir / "japanese_acoustic_summary.csv"
    headers = [
        "id", "file", "target_pitch_hz", "target_rate_pct",
        "edge_ms", "rvc_ms", "total_ms", "rtf",
        "pre_dur_s", "post_dur_s", "dur_ratio",
        "pre_f0_mean", "post_f0_mean", "f0_disc_hz", "realized_post_shift_hz",
        "pre_voiced_frac", "post_voiced_frac", "octave_jumps", "peak", "clipping_ratio"
    ]
    rows = [",".join(headers)]
    for r in results:
        l = r["latencies"]
        pre = r["pre_rvc"]
        post = r["post_rvc"]
        d = r["derived"]
        row = [
            r["id"], r["file"], str(r["target_pitch_hz"]), str(r["target_rate_percent"]),
            f"{l['edge_tts_ms']:.1f}", f"{l['rvc_ms']:.1f}", f"{l['total_ms']:.1f}", f"{l['real_time_factor']:.2f}",
            f"{pre['duration_s']:.2f}", f"{post['duration_s']:.2f}", f"{d['duration_preservation_ratio']:.3f}",
            f"{pre['f0_mean']:.1f}", f"{post['f0_mean']:.1f}", f"{d['rvc_f0_discrepancy_hz']:.1f}", f"{d['realized_post_f0_shift_hz']:.1f}",
            f"{pre['voiced_fraction']:.2f}", f"{post['voiced_fraction']:.2f}",
            str(post['octave_jumps']), f"{post['peak']:.3f}", f"{post['clipping_ratio']:.6f}"
        ]
        rows.append(",".join(row))

    with open(csv_path, "w", encoding="utf-8") as f:
        f.write("\n".join(rows))
    logger.info("Saved Japanese CSV summary to: %s", csv_path)


def main():
    asyncio.run(run_japanese_benchmark())


if __name__ == "__main__":
    main()
