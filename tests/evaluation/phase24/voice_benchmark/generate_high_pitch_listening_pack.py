"""
tests/evaluation/phase24/voice_benchmark/generate_high_pitch_listening_pack.py

Phase 24 Gate 2 — High Pitch Listening Pack Generator.
Generates an all-post-RVC listening pack across higher pitch ranges:
  +0 Hz (baseline), +60 Hz, +80 Hz, +100 Hz, +120 Hz, +150 Hz
for English (EN), Northern Vietnamese (VI), and Japanese (JP).
All files saved as 24 kHz 16-bit linear PCM WAVs.
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
logger = logging.getLogger("HighPitchPackGenerator")

PITCH_GRID = [
    ("00_baseline", 0, "+0Hz", "Baseline reference pitch (+0 Hz)"),
    ("01_pitch_plus60Hz", 60, "+60Hz", "High pitch tier 1 (+60 Hz)"),
    ("02_pitch_plus80Hz", 80, "+80Hz", "High pitch tier 2 (+80 Hz)"),
    ("03_pitch_plus100Hz", 100, "+100Hz", "High pitch tier 3 (+100 Hz)"),
    ("04_pitch_plus120Hz", 120, "+120Hz", "Extreme high pitch tier 4 (+120 Hz)"),
    ("05_pitch_plus150Hz", 150, "+150Hz", "Extreme high pitch ceiling (+150 Hz)"),
]

LANGUAGES = [
    {
        "lang_code": "EN",
        "voice": "en-US-JennyNeural",
        "text": "Good morning! I'm really glad to see you today, everything turned out wonderfully.",
        "lang_name": "English",
        "intent": "Conversational friendly morning greeting and positive report",
    },
    {
        "lang_code": "VI",
        "voice": "vi-VN-HoaiMyNeural",
        "text": "Chào buổi sáng, mình rất vui được gặp lại cậu, mọi chuyện hôm nay đều diễn ra thật tuyệt vời.",
        "lang_name": "Northern Vietnamese",
        "intent": "Friendly Northern Vietnamese greeting with rich tone variety (ngang, huyền, sắc, hỏi, nặng)",
    },
    {
        "lang_code": "JP",
        "voice": "ja-JP-NanamiNeural",
        "text": "おはようございます。今日も一緒に楽しい一日にしていきましょうね！",
        "lang_name": "Japanese",
        "intent": "Native Japanese cheerful morning greeting and encouraging statement",
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
    # Pitch extraction using Praat autocorrelation up to 800 Hz
    pitch = snd.to_pitch_ac(time_step=0.01, pitch_floor=50.0, pitch_ceiling=800.0)
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


async def generate_high_pitch_pack() -> None:
    bench_dir = Path(__file__).resolve().parent
    listening_pack_dir = bench_dir / "listening_pack"
    listening_pack_dir.mkdir(parents=True, exist_ok=True)

    model_pth = str(PROJECT_ROOT / "models/voice/rvc/VaresaGIJP/VaresaGIJP_300e_2100s.pth")
    index_path = str(PROJECT_ROOT / "models/voice/rvc/VaresaGIJP/added_VaresaGIJP_v2.index")

    logger.info("Initializing RVCPipeline on CPU...")
    pipeline = RVCPipeline(device="cpu")
    pipeline.load_model(model_pth, index_path)
    pipeline._get_or_load_hubert()

    results: List[Dict[str, Any]] = []
    baselines: Dict[str, float] = {}

    total_tasks = len(LANGUAGES) * len(PITCH_GRID)
    task_num = 0

    for lang_info in LANGUAGES:
        lang_code = lang_info["lang_code"]
        voice = lang_info["voice"]
        text = lang_info["text"]
        lang_name = lang_info["lang_name"]
        intent = lang_info["intent"]

        for step_label, pitch_val, pitch_str, purpose in PITCH_GRID:
            task_num += 1
            file_name = f"{lang_code}_{step_label}.wav"
            logger.info(
                "[%d/%d] Generating %s (%s, pitch=%s): %s",
                task_num, total_tasks, file_name, lang_code, pitch_str, text[:25]
            )

            # Edge-TTS with retry
            t_edge_start = time.perf_counter()
            edge_bytes = b""
            for attempt in range(1, 4):
                try:
                    comm = edge_tts.Communicate(
                        text,
                        voice=voice,
                        rate="+0%",
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
                    logger.warning("Edge-TTS attempt %d failed for %s: %s", attempt, file_name, stream_err)
                    if attempt < 3:
                        await asyncio.sleep(1.5)
                    else:
                        raise
            t_edge_end = time.perf_counter()
            edge_latency_ms = (t_edge_end - t_edge_start) * 1000.0

            pre_audio_16k = decode_audio_to_16k(edge_bytes)
            pre_metrics = compute_acoustic_features(pre_audio_16k, 16000)

            # RVC Conversion
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

            assert rvc_res.rvc_applied and rvc_res.execution_status == "success", f"RVC conversion failed for {file_name}"
            post_audio_24k, post_sr = decode_wav_to_float(rvc_res.audio_bytes)
            post_metrics = compute_acoustic_features(post_audio_24k, post_sr)

            # Write ONLY the post-RVC WAV file to the listening pack
            wav_path = listening_pack_dir / file_name
            with open(wav_path, "wb") as f_out:
                f_out.write(rvc_res.audio_bytes)

            if pitch_val == 0:
                baselines[lang_code] = post_metrics["f0_mean"]

            realized_shift = round(post_metrics["f0_mean"] - baselines[lang_code], 2)
            rvc_f0_discrepancy = round(post_metrics["f0_mean"] - pre_metrics["f0_mean"], 2)
            dur_preservation_ratio = round(post_metrics["duration_s"] / max(0.01, pre_metrics["duration_s"]), 4)
            rtf = round(total_latency_ms / max(1.0, post_metrics["duration_s"] * 1000.0), 3)

            item = {
                "file_name": file_name,
                "lang_code": lang_code,
                "lang_name": lang_name,
                "voice": voice,
                "text": text,
                "intent": intent,
                "target_pitch_hz": pitch_val,
                "target_pitch_str": pitch_str,
                "purpose": purpose,
                "latencies": {
                    "edge_tts_ms": round(edge_latency_ms, 2),
                    "rvc_ms": round(rvc_latency_ms, 2),
                    "total_ms": round(total_latency_ms, 2),
                    "real_time_factor": rtf,
                },
                "pre_rvc": pre_metrics,
                "post_rvc": post_metrics,
                "derived": {
                    "realized_shift_hz": realized_shift,
                    "rvc_f0_discrepancy_hz": rvc_f0_discrepancy,
                    "duration_preservation_ratio": dur_preservation_ratio,
                },
            }
            results.append(item)

    # Save summary CSV
    csv_path = listening_pack_dir / "high_pitch_acoustic_summary.csv"
    headers = [
        "file_name", "lang", "target_pitch_hz", "pre_f0_mean", "post_f0_mean",
        "realized_shift_hz", "f0_disc_hz", "pre_dur_s", "post_dur_s", "dur_ratio",
        "pre_voiced_frac", "post_voiced_frac", "octave_jumps", "peak", "clipping_ratio",
        "total_ms", "rtf"
    ]
    rows = [",".join(headers)]
    for r in results:
        pre = r["pre_rvc"]
        post = r["post_rvc"]
        d = r["derived"]
        l = r["latencies"]
        row = [
            r["file_name"], r["lang_code"], str(r["target_pitch_hz"]),
            f"{pre['f0_mean']:.1f}", f"{post['f0_mean']:.1f}",
            f"{d['realized_shift_hz']:.1f}", f"{d['rvc_f0_discrepancy_hz']:.1f}",
            f"{pre['duration_s']:.2f}", f"{post['duration_s']:.2f}", f"{d['duration_preservation_ratio']:.3f}",
            f"{pre['voiced_fraction']:.2f}", f"{post['voiced_fraction']:.2f}",
            str(post['octave_jumps']), f"{post['peak']:.3f}", f"{post['clipping_ratio']:.6f}",
            f"{l['total_ms']:.1f}", f"{l['real_time_factor']:.2f}"
        ]
        rows.append(",".join(row))

    with open(csv_path, "w", encoding="utf-8") as f:
        f.write("\n".join(rows))
    logger.info("Saved high pitch summary CSV to: %s", csv_path)

    # Save telemetry JSON
    json_path = listening_pack_dir / "high_pitch_telemetry.json"
    with open(json_path, "w", encoding="utf-8") as f:
        json.dump({"results": results, "baselines": baselines}, f, indent=2, ensure_ascii=False)
    logger.info("Saved high pitch telemetry JSON to: %s", json_path)


def main():
    asyncio.run(generate_high_pitch_pack())


if __name__ == "__main__":
    main()
