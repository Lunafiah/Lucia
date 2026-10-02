"""
tests/evaluation/phase24/voice_benchmark/benchmark_harness.py

Phase 24 Gate 2 — Voice Stack Control Surface Audit Benchmark Harness.
Audits the production Edge-TTS -> Direct RVC v2 pipeline across 30 utterances (15 EN + 15 VI).
Measures:
  - Synthesis latencies (Edge-TTS, RVC, End-to-End, Real-Time Factor)
  - Acoustic properties pre- and post-RVC (F0 mean/median/std/min/max, voiced fraction, RMS, peak)
  - Realized F0 shift vs SSML pitch target (±30, ±15, 0 Hz)
  - Realized duration change vs SSML rate target (±20%, ±10%, 0%)
  - F0 tracking errors & artifact indicators (octave jumps, unvoiced dropouts, clipping)
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
from typing import Any, Dict, List, Optional, Tuple

import edge_tts
import numpy as np
import parselmouth

# Add project root to sys.path
PROJECT_ROOT = Path(__file__).resolve().parents[4]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from src.core.voice.rvc_pipeline import RVCPipeline, decode_audio_to_16k

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger("P24VoiceAudit")


def decode_wav_to_float(wav_bytes: bytes) -> Tuple[np.ndarray, int]:
    """Decode 16-bit linear PCM WAV bytes to float32 numpy array and sample rate."""
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
    """Extract acoustic metrics using Parselmouth (Praat AC pitch extraction)."""
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
            "f0_p05": 0.0,
            "f0_p95": 0.0,
            "octave_jumps": 0,
            "rms": 0.0,
            "peak": 0.0,
            "clipping_ratio": 0.0,
        }

    snd = parselmouth.Sound(audio, sampling_frequency=sr)
    # Pitch extraction using standard Praat autocorrelation
    pitch = snd.to_pitch_ac(time_step=0.01, pitch_floor=50.0, pitch_ceiling=600.0)
    f0_arr = pitch.selected_array["frequency"]
    voiced_f0 = f0_arr[f0_arr > 0]

    # Detect octave jump artifacts (frame-to-frame frequency doubling/halving)
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
        "f0_p05": round(float(np.percentile(voiced_f0, 5)), 2) if len(voiced_f0) > 0 else 0.0,
        "f0_p95": round(float(np.percentile(voiced_f0, 95)), 2) if len(voiced_f0) > 0 else 0.0,
        "octave_jumps": octave_jumps,
        "rms": round(float(np.sqrt(np.mean(audio ** 2))), 4),
        "peak": round(float(np.max(np.abs(audio))), 4),
        "clipping_ratio": round(clipping_ratio, 6),
    }


async def run_benchmark(
    utterances_path: Path,
    output_dir: Path,
    model_pth: str,
    index_path: str,
) -> Dict[str, Any]:
    output_dir.mkdir(parents=True, exist_ok=True)
    audio_dir = output_dir / "audio"
    audio_dir.mkdir(exist_ok=True)

    with open(utterances_path, "r", encoding="utf-8") as f:
        spec = json.load(f)

    test_cases = spec["test_cases"]
    logger.info("Initializing RVCPipeline (device=cpu)...")
    pipeline = RVCPipeline(device="cpu")
    logger.info("Loading checkpoint: %s", model_pth)
    pipeline.load_model(model_pth, index_path)
    logger.info("Pre-warming ContentVec/HuBERT...")
    pipeline._get_or_load_hubert()

    results: List[Dict[str, Any]] = []

    # Store baseline mean F0 and duration for reference (EN_01 and VI_01)
    baselines: Dict[str, Dict[str, float]] = {}

    for idx, tc in enumerate(test_cases, 1):
        tc_id = tc["id"]
        lang = tc["lang"]
        text = tc["text"]
        voice = tc["voice"]
        pitch_str = tc["pitch_str"]
        rate_str = tc["rate_str"]

        logger.info(
            "[%d/%d] Processing %s (%s, pitch=%s, rate=%s): %s",
            idx, len(test_cases), tc_id, lang, pitch_str, rate_str, text[:30] + "..."
        )

        # 1. Edge-TTS Synthesis with retry for transient network hiccups
        t_edge_start = time.perf_counter()
        edge_bytes = b""
        for attempt in range(1, 4):
            try:
                comm = edge_tts.Communicate(
                    text,
                    voice=voice,
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

        # Decode Edge-TTS audio to 16 kHz float32 for pre-RVC analysis
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

        if not rvc_res.rvc_applied or rvc_res.execution_status != "success":
            logger.error("RVC conversion failed for %s: %s", tc_id, rvc_res.error_message)
            post_metrics = {k: 0.0 for k in pre_metrics}
            post_audio_24k = np.zeros(0, dtype=np.float32)
        else:
            post_audio_24k, post_sr = decode_wav_to_float(rvc_res.audio_bytes)
            post_metrics = compute_acoustic_features(post_audio_24k, post_sr)

        # Save audio samples for inspection
        with open(audio_dir / f"{tc_id}_pre.mp3", "wb") as f_out:
            f_out.write(edge_bytes)
        if rvc_res.rvc_applied:
            with open(audio_dir / f"{tc_id}_post.wav", "wb") as f_out:
                f_out.write(rvc_res.audio_bytes)

        # Save baseline values for language
        if tc["category"] == "baseline_control":
            baselines[lang] = {
                "pre_f0_mean": pre_metrics["f0_mean"],
                "post_f0_mean": post_metrics["f0_mean"],
                "pre_duration_s": pre_metrics["duration_s"],
                "post_duration_s": post_metrics["duration_s"],
            }

        lang_base = baselines.get(lang, {
            "pre_f0_mean": pre_metrics["f0_mean"],
            "post_f0_mean": post_metrics["f0_mean"],
            "pre_duration_s": pre_metrics["duration_s"],
            "post_duration_s": post_metrics["duration_s"],
        })

        # Comparative & Derived Metrics
        realized_pre_f0_shift = round(pre_metrics["f0_mean"] - lang_base["pre_f0_mean"], 2)
        realized_post_f0_shift = round(post_metrics["f0_mean"] - lang_base["post_f0_mean"], 2)
        rvc_f0_discrepancy = round(post_metrics["f0_mean"] - pre_metrics["f0_mean"], 2)

        pre_rate_ratio = round(pre_metrics["duration_s"] / max(0.01, lang_base["pre_duration_s"]), 4)
        post_rate_ratio = round(post_metrics["duration_s"] / max(0.01, lang_base["post_duration_s"]), 4)
        duration_preservation_ratio = round(post_metrics["duration_s"] / max(0.01, pre_metrics["duration_s"]), 4)

        real_time_factor = round(total_latency_ms / max(1.0, post_metrics["duration_s"] * 1000.0), 3)

        entry = {
            "id": tc_id,
            "lang": lang,
            "category": tc["category"],
            "intent": tc["intent"],
            "target_pitch_hz": tc["pitch_hz"],
            "target_pitch_str": tc["pitch_str"],
            "target_rate_percent": tc["rate_percent"],
            "target_rate_str": tc["rate_str"],
            "text": text,
            "latencies": {
                "edge_tts_ms": round(edge_latency_ms, 2),
                "rvc_ms": round(rvc_latency_ms, 2),
                "total_ms": round(total_latency_ms, 2),
                "real_time_factor": real_time_factor,
            },
            "pre_rvc": pre_metrics,
            "post_rvc": post_metrics,
            "derived": {
                "realized_pre_f0_shift_hz": realized_pre_f0_shift,
                "realized_post_f0_shift_hz": realized_post_f0_shift,
                "rvc_f0_discrepancy_hz": rvc_f0_discrepancy,
                "pre_duration_ratio_vs_base": pre_rate_ratio,
                "post_duration_ratio_vs_base": post_rate_ratio,
                "duration_preservation_ratio": duration_preservation_ratio,
                "unvoiced_dropout_ratio": round(pre_metrics["voiced_fraction"] - post_metrics["voiced_fraction"], 4),
                "post_octave_jumps": post_metrics["octave_jumps"],
            },
        }
        results.append(entry)

    # Save raw telemetry JSON
    raw_path = output_dir / "raw_benchmark_telemetry.json"
    with open(raw_path, "w", encoding="utf-8") as f:
        json.dump(
            {
                "metadata": {
                    "total_utterances": len(results),
                    "model_pth": model_pth,
                    "index_path": index_path,
                    "baselines": baselines,
                },
                "results": results,
            },
            f,
            indent=2,
            ensure_ascii=False,
        )
    logger.info("Saved raw telemetry to: %s", raw_path)

    # Save CSV summary
    csv_path = output_dir / "acoustic_summary.csv"
    headers = [
        "id", "lang", "category", "target_pitch_hz", "target_rate_pct",
        "edge_ms", "rvc_ms", "total_ms", "rtf",
        "pre_dur_s", "post_dur_s", "dur_ratio",
        "pre_f0_mean", "post_f0_mean", "f0_disc_hz",
        "pre_f0_shift", "post_f0_shift",
        "pre_voiced_frac", "post_voiced_frac", "octave_jumps", "peak", "clipping_ratio"
    ]
    lines = [",".join(headers)]
    for r in results:
        d = r["derived"]
        l = r["latencies"]
        pre = r["pre_rvc"]
        post = r["post_rvc"]
        row = [
            r["id"], r["lang"], r["category"], str(r["target_pitch_hz"]), str(r["target_rate_percent"]),
            f"{l['edge_tts_ms']:.1f}", f"{l['rvc_ms']:.1f}", f"{l['total_ms']:.1f}", f"{l['real_time_factor']:.2f}",
            f"{pre['duration_s']:.2f}", f"{post['duration_s']:.2f}", f"{d['duration_preservation_ratio']:.3f}",
            f"{pre['f0_mean']:.1f}", f"{post['f0_mean']:.1f}", f"{d['rvc_f0_discrepancy_hz']:.1f}",
            f"{d['realized_pre_f0_shift_hz']:.1f}", f"{d['realized_post_f0_shift_hz']:.1f}",
            f"{pre['voiced_fraction']:.2f}", f"{post['voiced_fraction']:.2f}",
            str(d['post_octave_jumps']), f"{post['peak']:.3f}", f"{post['clipping_ratio']:.6f}"
        ]
        lines.append(",".join(row))

    with open(csv_path, "w", encoding="utf-8") as f:
        f.write("\n".join(lines))
    logger.info("Saved CSV summary to: %s", csv_path)

    return {"results": results, "baselines": baselines}


def main():
    bench_dir = Path(__file__).resolve().parent
    utterances_json = bench_dir / "utterances.json"
    model_pth = str(PROJECT_ROOT / "models/voice/rvc/VaresaGIJP/VaresaGIJP_300e_2100s.pth")
    index_path = str(PROJECT_ROOT / "models/voice/rvc/VaresaGIJP/added_VaresaGIJP_v2.index")

    asyncio.run(run_benchmark(utterances_json, bench_dir, model_pth, index_path))


if __name__ == "__main__":
    main()
