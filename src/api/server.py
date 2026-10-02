"""
FastAPI HTTP server — Phase 9 Cognitive Unification.

Endpoints:
    POST /process  — serialized single-turn cognitive loop (asyncio.Lock, HTTP 429 guard)
    GET  /state    — non-blocking real-time emotional telemetry snapshot
    GET  /health   — orchestrator health check
    GET  /system/profile — current hardware scaling profile

Requirements: Phase 3 (1.1–1.8, 2.1–2.7, 3.1–3.7, 9.3); Phase 9 (ADR-014–ADR-020)
"""

from __future__ import annotations

import argparse
import asyncio
from datetime import datetime
import json
import logging
import os
from pathlib import Path
import signal
import sys
import time
import uuid
from typing import Any, Dict, List, Optional, Tuple, Union

import numpy as np

# Ensure project root is on sys.path regardless of execution mode or IDE root
_PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "../.."))
if _PROJECT_ROOT not in sys.path:
    sys.path.insert(0, _PROJECT_ROOT)

from fastapi import FastAPI, File, HTTPException, Request, Response, UploadFile, status
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field
import uvicorn

from src.core.voice.stt_engine import get_stt_engine

from src.core.config import MemoryOrchestratorConfig
from src.core.models import BehavioralConstraints, SomaticMarkers
from src.core.orchestrator.cognitive_orchestrator import (
    CognitiveOrchestrator,
    build_cognitive_orchestrator,
)
# Backward-compatibility alias for test specs
InstrumentedOrchestrator = CognitiveOrchestrator
from src.core.orchestrator.policies import CognitiveTurnResult
from src.core.plugins.hook_bus import HookBus
from src.core.resource_manager import ResourceProfile, get_resource_profile
from src.core.simulation import (
    ActivationSafetyError,
    ScenarioRunner,
    SimulationRuntime,
)
from src.core.storage.history_store import ChatHistoryStore
from src.core.telemetry.stability_evaluator import StabilityEvaluator

logger = logging.getLogger("lucia.api")

_hook_bus = HookBus()
_history_store: Any = ChatHistoryStore()
_stability_evaluator: StabilityEvaluator = StabilityEvaluator()
_sim_runtime: Optional[SimulationRuntime] = None
_scenario_runner: Optional[ScenarioRunner] = None
_mode: str = "live"


def get_history_store() -> Any:
    global _history_store
    if _sim_runtime is not None:
        return _sim_runtime.chat_store
    if _history_store is None:
        _history_store = ChatHistoryStore()
    return _history_store


def get_stability_evaluator() -> StabilityEvaluator:
    global _stability_evaluator
    if _sim_runtime is not None:
        return _sim_runtime.stability_evaluator
    if _stability_evaluator is None:
        _stability_evaluator = StabilityEvaluator()
    return _stability_evaluator


# ---------------------------------------------------------------------------
# Pydantic Request / Response Models
# ---------------------------------------------------------------------------

class ProcessRequest(BaseModel):
    input: str = Field(..., min_length=1, max_length=4000)


class ProcessResponse(BaseModel):
    response: str
    call_id: str
    surprise: float = 0.0
    generation_mode: str = "reflexive"
    expression: Optional[Dict[str, Any]] = None
    relationship: Optional[Dict[str, Any]] = None
    communication: Optional[Dict[str, Any]] = None


class PADSnapshot(BaseModel):
    pleasure: float
    arousal: float
    dominance: float


class SomaticSnapshot(BaseModel):
    stability: float
    cognitive_load: float
    energy: float
    tension: float


class ConstraintsSnapshot(BaseModel):
    max_tokens: int
    temperature: float
    latency_ms: int
    reasoning_depth: int


class StateSnapshot(BaseModel):
    pad: PADSnapshot
    somatic: SomaticSnapshot
    constraints: ConstraintsSnapshot
    memory_trace_count: int
    timestamp: float
    profile: Optional[str] = None
    surprise: float = 0.0
    generation_mode: str = "reflexive"
    expression: Optional[Dict[str, Any]] = None
    relationship: Optional[Dict[str, Any]] = None
    communication: Optional[Dict[str, Any]] = None


# ---------------------------------------------------------------------------
# Phase 9: asyncio turn-admission lock (Tier 1, ADR-018)
# ---------------------------------------------------------------------------
#
# Exactly one cognitive turn may be in-flight at a time.  A second request
# waits; a third (and any beyond) receives HTTP 429 immediately.
#
# The queue depth bound of 1 + 1 = 2 concurrent awaits (1 executing + 1
# waiting) is enforced by the _turn_queue_depth counter.

_turn_admission_lock: asyncio.Lock = asyncio.Lock()
_turn_queue_depth: int = 0  # number of requests currently admitted (0, 1, or 2)


# ---------------------------------------------------------------------------
# FastAPI Application & Global State
# ---------------------------------------------------------------------------

app = FastAPI(title="Lucia Backend API", version="9.0.0")

_orchestrator: Optional[CognitiveOrchestrator] = None
_resource_profile: Optional[ResourceProfile] = None


def get_orchestrator() -> CognitiveOrchestrator:
    if _mode == "simulation" or _sim_runtime is not None:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Orchestrator is not available in simulation mode. Live companion is inactive.",
        )
    if _orchestrator is None:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Orchestrator not initialized",
        )
    return _orchestrator


@app.post("/process", response_model=ProcessResponse)
async def process_turn(req: ProcessRequest) -> Any:
    """
    Execute full cognitive-emotional turn via CognitiveOrchestrator.

    Concurrency (ADR-018):
      - Tier 1: asyncio.Lock() with queue depth = 1 (one waiting, rest → HTTP 429)
      - Tier 2: run_in_executor dispatches blocking inference to thread pool
      - Tier 3: CognitiveOrchestrator._turn_lock serializes pipeline stages

    Disabled in simulation mode.
    """
    global _turn_queue_depth

    if _mode == "simulation" or _sim_runtime is not None:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Live processing disabled in simulation mode. Use POST /sim/chat for simulated turns.",
        )
    orch = get_orchestrator()
    if orch._degraded or not orch.is_healthy():
        return JSONResponse(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            content={
                "error": "orchestrator_degraded",
                "call_id": uuid.uuid4().hex,
            },
        )

    # --- Tier 1: admission guard (max concurrent = 2: 1 executing + 1 waiting) ---
    if _turn_queue_depth >= 2:
        return JSONResponse(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            content={
                "error": "turn_in_progress",
                "detail": "Lucia is currently processing a thought. Please wait.",
            },
        )

    _turn_queue_depth += 1
    try:
        _hook_bus.emit("on_turn_start", req.input)
        store = get_history_store()
        store.append_turn("user", req.input)

        loop = asyncio.get_running_loop()

        # Tier 2: offload blocking LLM inference to thread pool
        try:
            async with _turn_admission_lock:
                result: CognitiveTurnResult = await loop.run_in_executor(
                    None, orch.process, req.input
                )
        except Exception as exc:
            logger.exception("Exception processing turn: %s", exc)
            return JSONResponse(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                content={"error": "internal_error", "call_id": uuid.uuid4().hex},
            )

        # Update stability metrics from turn result
        try:
            get_stability_evaluator().update_sdm_count(
                orch._affective_memory.trace_count
            )
        except Exception:
            pass

        if isinstance(result, CognitiveTurnResult):
            resp_text = result.response_text
            turn_call_id = result.call_id
            surprise = float(result.prediction_error)
            gen_mode = str(result.generation_policy.mode)
        else:
            resp_text = str(result)
            turn_call_id = uuid.uuid4().hex
            surprise = 0.0
            gen_mode = "reflexive"

        store.append_turn("companion", resp_text)
        _hook_bus.emit(
            "on_turn_completed",
            {"user": req.input, "response": resp_text},
        )

        expr_dict = (
            result.expression.to_dict()
            if isinstance(result, CognitiveTurnResult) and result.expression is not None
            else None
        )
        rel_dict = (
            result.relationship.to_dict()
            if isinstance(result, CognitiveTurnResult) and result.relationship is not None
            else None
        )
        comm_dict = (
            result.communication.to_dict()
            if isinstance(result, CognitiveTurnResult) and result.communication is not None
            else None
        )

        return {
            "response": resp_text,
            "call_id": turn_call_id,
            "surprise": surprise,
            "generation_mode": gen_mode,
            "expression": expr_dict,
            "relationship": rel_dict,
            "communication": comm_dict,
        }
    finally:
        _turn_queue_depth -= 1


@app.get("/state", response_model=StateSnapshot)
async def get_state(response: Response) -> StateSnapshot:
    """
    Return non-blocking real-time emotional state snapshot with no caching.

    Concurrency: This endpoint does NOT acquire _turn_admission_lock or
    _turn_lock.  It reads EmotionCore._state_lock (≤ 1 ms) and the atomic
    CognitiveTurnResult reference.  Always responds in < 15 ms.
    """
    response.headers["Cache-Control"] = "no-store"
    if _sim_runtime is not None:
        pad_state = _sim_runtime.emotion_core.get_pad_state()
        markers = _sim_runtime.homeostatic_engine.compute_somatic_markers(pad_state)
        constraints = _sim_runtime.homeostatic_engine.compute_behavioral_constraints(
            markers, pad_state
        )
        return StateSnapshot(
            pad=PADSnapshot(
                pleasure=float(pad_state.pleasure),
                arousal=float(pad_state.arousal),
                dominance=float(pad_state.dominance),
            ),
            somatic=SomaticSnapshot(
                stability=float(markers.stability),
                cognitive_load=float(markers.cognitive_load),
                energy=float(markers.energy),
                tension=float(markers.tension),
            ),
            constraints=ConstraintsSnapshot(
                max_tokens=int(constraints.max_tokens),
                temperature=float(constraints.temperature),
                latency_ms=int(constraints.latency_ms),
                reasoning_depth=int(constraints.reasoning_depth),
            ),
            memory_trace_count=_sim_runtime.affective_memory.trace_count,
            timestamp=_sim_runtime.sim_clock.virtual_time_s,
            profile="simulation",
        )

    orch = get_orchestrator()

    # Non-blocking PAD read (≤ 1 ms — Tier 4 state lock)
    pad_state = orch._emotion_core.get_pad_state()
    pad_snap = PADSnapshot(
        pleasure=float(pad_state.pleasure),
        arousal=float(pad_state.arousal),
        dominance=float(pad_state.dominance),
    )

    # Latest turn snapshot (atomic pointer read — no lock required)
    latest = getattr(orch, "latest_result", None)
    if isinstance(latest, CognitiveTurnResult):
        somatic_snap = SomaticSnapshot(
            stability=float(latest.somatic.stability),
            cognitive_load=float(latest.somatic.cognitive_load),
            energy=float(latest.somatic.energy),
            tension=float(latest.somatic.tension),
        )
        constraints_snap = ConstraintsSnapshot(
            max_tokens=int(latest.constraints.max_tokens),
            temperature=float(latest.constraints.temperature),
            latency_ms=int(latest.constraints.latency_ms),
            reasoning_depth=int(latest.constraints.reasoning_depth),
        )
        surprise = float(latest.prediction_error)
        generation_mode = str(latest.generation_policy.mode)
    elif getattr(orch, "_last_somatic", None) is not None and getattr(orch, "_last_constraints", None) is not None and isinstance(orch._last_somatic, SomaticMarkers):
        somatic = orch._last_somatic
        constraints = orch._last_constraints
        somatic_snap = SomaticSnapshot(
            stability=float(somatic.stability),
            cognitive_load=float(somatic.cognitive_load),
            energy=float(somatic.energy),
            tension=float(somatic.tension),
        )
        constraints_snap = ConstraintsSnapshot(
            max_tokens=int(constraints.max_tokens),
            temperature=float(constraints.temperature),
            latency_ms=int(constraints.latency_ms),
            reasoning_depth=int(constraints.reasoning_depth),
        )
        surprise = 0.0
        generation_mode = "reflexive"
    else:
        somatic_snap = SomaticSnapshot(
            stability=0.0, cognitive_load=0.0, energy=0.0, tension=0.0
        )
        constraints_snap = ConstraintsSnapshot(
            max_tokens=150, temperature=0.75, latency_ms=0, reasoning_depth=1
        )
        surprise = 0.0
        generation_mode = "reflexive"

    trace_count = orch._affective_memory.trace_count
    profile_name = _resource_profile.name if _resource_profile else "auto"

    expr_dict = (
        latest.expression.to_dict()
        if isinstance(latest, CognitiveTurnResult) and latest.expression is not None
        else None
    )
    rel_dict = (
        latest.relationship.to_dict()
        if isinstance(latest, CognitiveTurnResult) and latest.relationship is not None
        else None
    )
    comm_dict = (
        latest.communication.to_dict()
        if isinstance(latest, CognitiveTurnResult) and latest.communication is not None
        else None
    )

    return StateSnapshot(
        pad=pad_snap,
        somatic=somatic_snap,
        constraints=constraints_snap,
        memory_trace_count=trace_count,
        timestamp=time.monotonic(),
        profile=profile_name,
        surprise=surprise,
        generation_mode=generation_mode,
        expression=expr_dict,
        relationship=rel_dict,
        communication=comm_dict,
    )


from fastapi.responses import JSONResponse, Response
from src.core.voice.voice_engine import VoiceEngine, VoiceEngineConfig

_voice_engine: VoiceEngine = VoiceEngine()


class SynthesizeRequest(BaseModel):
    text: str
    rate: Optional[str] = None
    volume: Optional[str] = None
    pitch: Optional[str] = None
    pitch_hz: Optional[float] = None
    closeness: Optional[float] = None
    focal_words: Optional[List[str]] = None


class SelectModelRequest(BaseModel):
    model_name: str


@app.post("/voice/synthesize")
async def synthesize_voice(req: SynthesizeRequest) -> Response:
    """
    Synthesize spoken audio for the given text using current voice/RVC settings.
    Bounded voice control surface (ADR-032): pitch_hz in [-30, 30], closeness in [0, 1].
    """
    clean_text = req.text.strip()
    if not clean_text:
        return Response(content=b"", media_type="audio/mpeg")
    try:
        # Bounded validation and clamping (ADR-032)
        clamped_pitch_hz = float(np.clip(req.pitch_hz, -30.0, 30.0)) if req.pitch_hz is not None else None
        clamped_closeness = float(np.clip(req.closeness, 0.0, 1.0)) if req.closeness is not None else None
        safe_focal = [str(w)[:50] for w in req.focal_words[:10]] if req.focal_words else None

        audio_data = await _voice_engine.synthesize_speech(
            clean_text,
            rate=req.rate,
            volume=req.volume,
            pitch=req.pitch,
            pitch_hz=clamped_pitch_hz,
            closeness=clamped_closeness,
            focal_words=safe_focal,
        )
        return Response(content=audio_data, media_type="audio/mpeg")
    except Exception as exc:
        logger.exception("Voice synthesis failed: %s", exc)
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content={"error": str(exc)},
        )


@app.get("/voice/models")
async def get_voice_models() -> Dict[str, Any]:
    """
    Return discovered RVC models and current active model configuration.
    """
    return {
        "models": _voice_engine.get_available_models(),
        "active_model": _voice_engine._config.active_rvc_model,
        "base_voice": _voice_engine._config.base_voice,
    }


@app.post("/voice/select-model")
async def select_voice_model(req: SelectModelRequest) -> Dict[str, Any]:
    """
    Select active RVC model or 'default'.
    """
    success = _voice_engine.set_active_model(req.model_name)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"RVC Model '{req.model_name}' not found",
        )
    return {
        "status": "ok",
        "active_model": _voice_engine._config.active_rvc_model,
    }


@app.post("/voice/transcribe")
async def transcribe_audio(
    req: Request,
    file: Optional[UploadFile] = File(None),
) -> Dict[str, Any]:
    """
    Transcribe spoken audio to text using self-contained offline faster-whisper.
    Accepts either multipart/form-data upload or raw audio body.
    """
    try:
        audio_bytes = b""
        if file is not None:
            audio_bytes = await file.read()
        elif req is not None:
            audio_bytes = await req.body()

        if not audio_bytes:
            return {"status": "ok", "text": ""}

        engine = get_stt_engine()
        loop = asyncio.get_running_loop()
        text = await loop.run_in_executor(None, engine.transcribe_bytes, audio_bytes)
        return {"status": "ok", "text": text}
    except Exception as exc:
        logger.exception("Voice transcription failed: %s", exc)
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content={"status": "error", "error": str(exc), "text": ""},
        )


@app.get("/telemetry/stability")
async def get_stability_telemetry() -> Dict[str, Any]:
    """
    Return composite Limbic Stability Index (LSI), tick jitter, and ODE variance.
    """
    return get_stability_evaluator().get_snapshot().to_dict()


@app.get("/history")
async def get_chat_history(limit: int = 50) -> Dict[str, Any]:
    """
    Return recent conversation turns across active and past sessions.
    """
    return {"turns": get_history_store().get_history(limit=limit)}


@app.post("/history/new-session")
async def new_chat_session() -> Dict[str, Any]:
    """
    Start a fresh conversation session without deleting older history.
    """
    session_id = get_history_store().new_session()
    return {"status": "ok", "session_id": session_id}


@app.delete("/history")
async def clear_chat_history() -> Dict[str, Any]:
    """
    Clear all conversation history logs.
    """
    get_history_store().clear_history()
    return {"status": "ok", "message": "History cleared"}


@app.get("/history/export")
async def export_chat_history() -> Response:
    """
    Export full conversation history as a formatted Markdown file.
    """
    md_content = get_history_store().export_markdown()
    return Response(
        content=md_content,
        media_type="text/markdown",
        headers={"Content-Disposition": "attachment; filename=lucia_chat_history.md"},
    )


class ProfileUpdateRequest(BaseModel):
    user_name: Optional[str] = None
    companion_name: Optional[str] = None
    is_onboarded: Optional[bool] = None
    birthday: Optional[str] = None
    pronouns: Optional[str] = None
    born_at: Optional[str] = None


@app.get("/models/avatar")
async def get_avatar_models() -> Dict[str, Any]:
    """
    Discover all custom avatar models in models/avatar/ (sprites, live2d, vrm).
    """
    base_dir = Path("models/avatar")
    sprites = []
    live2d = []
    vrm = []

    try:
        sprites_dir = base_dir / "sprites"
        if sprites_dir.exists() and sprites_dir.is_dir():
            sprites = [d.name for d in sprites_dir.iterdir() if d.is_dir()]

        live2d_dir = base_dir / "live2d"
        if live2d_dir.exists() and live2d_dir.is_dir():
            live2d = [d.name for d in live2d_dir.iterdir() if d.is_dir()]

        vrm_dir = base_dir / "vrm"
        if vrm_dir.exists() and vrm_dir.is_dir():
            vrm = [f.name for f in vrm_dir.iterdir() if f.is_file() and f.suffix.lower() == ".vrm"]
    except Exception as e:
        logger.error("Failed to scan avatar models: %s", e)

    return {
        "engines": ["canvas", "sprites", "live2d", "vrm"],
        "sprites": sprites,
        "live2d": live2d,
        "vrm": vrm,
    }


_PROFILE_FILE_PATH: Path = Path("data/profile.json")


def _reset_profile_file() -> Dict[str, Any]:
    """
    Atomically reset data/profile.json to initial un-onboarded / Genesis-ready state.
    """
    p = _PROFILE_FILE_PATH
    p.parent.mkdir(parents=True, exist_ok=True)
    initial = {
        "version": 1,
        "user_name": "Friend",
        "companion_name": "Lucia",
        "born_at": None,
        "is_onboarded": False,
        "pronouns": "they/them",
        "avatar_engine": "canvas",
        "avatar_model": "default",
    }
    tmp = p.with_suffix(".tmp")
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump(initial, f, indent=2, ensure_ascii=False)
    tmp.replace(p)
    return initial


def _get_profile_file() -> Path:
    p = _PROFILE_FILE_PATH
    p.parent.mkdir(parents=True, exist_ok=True)
    if not p.exists():
        initial = {
            "version": 1,
            "user_name": "Friend",
            "companion_name": "Lucia",
            "born_at": None,
            "is_onboarded": False,
            "pronouns": "they/them",
            "avatar_engine": "canvas",
            "avatar_model": "default"
        }
        with open(p, "w", encoding="utf-8") as f:
            json.dump(initial, f, indent=2, ensure_ascii=False)
    return p


@app.get("/profile")
async def get_profile() -> Dict[str, Any]:
    """
    Return current user/companion profile and awakening status.
    """
    if _sim_runtime is not None:
        return _sim_runtime.profile_store.get_profile()

    p = _get_profile_file()
    try:
        with open(p, "r", encoding="utf-8") as f:
            data = json.load(f)
            if isinstance(data, dict):
                return data
    except Exception as e:
        logger.error("Failed to read profile: %s", e)
    return {"version": 1, "user_name": "Friend", "companion_name": "Lucia", "is_onboarded": False, "born_at": None}


@app.post("/profile")
async def update_profile(req: ProfileUpdateRequest) -> Dict[str, Any]:
    """
    Update profile fields (user name, companion name, onboarding status).
    Guards against live awakening in simulation mode.
    """
    if _sim_runtime is not None:
        if req.is_onboarded is True:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Live onboarding activation forbidden in simulation mode: is_onboarded=True forbidden.",
            )
        try:
            updated = _sim_runtime.profile_store.update_profile(
                user_name=req.user_name,
                companion_name=req.companion_name,
                birthday=req.birthday,
                pronouns=req.pronouns,
            )
            return {"status": "ok", "profile": updated}
        except ActivationSafetyError as exc:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Live onboarding activation forbidden in simulation mode: {exc}",
            )

    p = _get_profile_file()
    try:
        with open(p, "r", encoding="utf-8") as f:
            data = json.load(f)
            if not isinstance(data, dict):
                data = {}
    except Exception:
        data = {}

    if req.user_name is not None:
        data["user_name"] = req.user_name.strip()
    if req.companion_name is not None:
        data["companion_name"] = req.companion_name.strip()
    if req.is_onboarded is not None:
        data["is_onboarded"] = req.is_onboarded
    if req.birthday is not None:
        data["birthday"] = req.birthday
    if req.pronouns is not None:
        data["pronouns"] = req.pronouns
    if req.born_at is not None:
        data["born_at"] = req.born_at
    elif req.is_onboarded and not data.get("is_onboarded"):
        # Establish canonical Genesis birth timestamp upon awakening
        data["born_at"] = datetime.now().isoformat()

    try:
        with open(p, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
    except Exception as e:
        logger.error("Failed to save profile: %s", e)

    return {"status": "ok", "profile": data}


@app.post("/lifecycle/activate")
async def activate_companion() -> Dict[str, Any]:
    """
    Explicit activation endpoint transitioning Lucia from Genesis-ready to live companion.
    Strictly gated to live mode.
    """
    if _mode == "simulation" or _sim_runtime is not None:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Cannot activate live companion in simulation mode. Direct lifecycle activation is strictly forbidden in simulation mode.",
        )
    p = _get_profile_file()
    try:
        with open(p, "r", encoding="utf-8") as f:
            data = json.load(f)
            if not isinstance(data, dict):
                data = {}
    except Exception:
        data = {}

    if data.get("is_onboarded") is True:
        return {
            "status": "already_active",
            "message": "Lucia is already active",
            "born_at": data.get("born_at"),
            "companion_name": data.get("companion_name", "Lucia"),
        }

    data["is_onboarded"] = True
    data["born_at"] = datetime.now().isoformat()
    try:
        with open(p, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
    except Exception as e:
        logger.error("Failed to save profile during activation: %s", e)
        raise HTTPException(status_code=500, detail="Failed to persist activation")

    logger.info("Lucia activated in live mode at %s", data["born_at"])
    return {
        "status": "activated",
        "born_at": data["born_at"],
        "companion_name": data.get("companion_name", "Lucia"),
    }


@app.post("/lifecycle/end")
async def end_lifecycle() -> Dict[str, Any]:
    """
    Atomic transition ending the current Lucia's lifecycle.
    Disabled in simulation mode.
    """
    if _mode == "simulation" or _sim_runtime is not None:
        return JSONResponse(
            status_code=status.HTTP_403_FORBIDDEN,
            content={
                "error": "LifecycleEndForbiddenInSimulation",
                "message": "Cannot end live lifecycle while running in simulation mode.",
            },
        )

    try:
        # 1. Reset Orchestrator state (dialogue, emotion, memory, somatic) if active
        if _orchestrator is not None:
            if hasattr(_orchestrator, "reset_lifecycle"):
                _orchestrator.reset_lifecycle()

        # 2. Reset chat history persistence
        get_history_store().clear_history()

        # 3. Reset stability telemetry
        get_stability_evaluator().reset()

        # 4. Reset profile persistence to un-onboarded / Genesis-ready state
        fresh_profile = _reset_profile_file()

        logger.info("Lucia lifecycle ended successfully: returned to Genesis-ready state")
        return {
            "status": "ok",
            "message": "Lucia lifecycle ended successfully",
            "profile": fresh_profile,
        }
    except Exception as exc:
        logger.exception("Failed to end Lucia lifecycle: %s", exc)
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content={"status": "error", "message": str(exc)},
        )


@app.get("/health")
async def health_check() -> Dict[str, Any]:
    """
    Healthcheck endpoint for ProcessManager monitoring.
    """
    if _sim_runtime is not None:
        return {"status": "ok", "mode": "simulation", "healthy": True}
    if _orchestrator is not None and _orchestrator.is_healthy():
        return {"status": "ok"}
    return JSONResponse(
        status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
        content={"status": "degraded"},
    )


# ---------------------------------------------------------------------------
# Simulation API Models & Endpoints (Phase 8)
# ---------------------------------------------------------------------------

class ClockStepRequest(BaseModel):
    delta_ms: float = Field(200.0, ge=0.0)

class ClockSpeedRequest(BaseModel):
    multiplier: float = Field(1.0, gt=0.0)

class ClockResetRequest(BaseModel):
    reset_time_s: float = Field(0.0, ge=0.0)

class StimulusTextRequest(BaseModel):
    text: str = Field(..., min_length=1, max_length=4000)
    source: str = "simulation_ui"

class StimulusVectorRequest(BaseModel):
    vector: List[float] = Field(..., min_length=16, max_length=16)
    source: str = "debug_probe"

class StimulusPresetRequest(BaseModel):
    preset: str
    pathway: str = "sensory_text"

class ScenarioRunRequest(BaseModel):
    scenario_id: str = "all"


def _require_sim_runtime() -> SimulationRuntime:
    if _sim_runtime is None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Simulation environment is not active. Start server with --mode simulation.",
        )
    return _sim_runtime


@app.get("/runtime/descriptor")
async def get_runtime_descriptor() -> Dict[str, Any]:
    if _mode == "simulation" and _sim_runtime is not None:
        return {
            "mode": "simulation",
            "is_live": False,
            "is_simulated": True,
            "state": _sim_runtime.state,
            "active_profile": "simulation",
            "capabilities": [
                "virtual_clock",
                "storage_isolation",
                "sensory_stimulus",
                "debug_vector_probe",
                "scenario_runner",
                "in_memory_chat",
            ],
        }
    return {
        "mode": "live",
        "is_live": True,
        "is_simulated": False,
        "state": "READY" if _orchestrator and _orchestrator.is_healthy() else "DEGRADED",
        "active_profile": _resource_profile.name if _resource_profile else "auto",
        "capabilities": ["live_chat", "model_inference", "voice", "presence"],
    }


@app.get("/runtime/snapshot")
async def get_runtime_snapshot() -> Dict[str, Any]:
    if _sim_runtime is not None:
        return _sim_runtime.get_state_snapshot()

    state_snap = await get_state(Response())
    return {
        "runtime": {
            "mode": "live",
            "state": "READY" if _orchestrator and _orchestrator.is_healthy() else "DEGRADED",
            "is_live": True,
            "is_simulated": False,
        },
        "pad": state_snap.pad.dict(),
        "somatic_markers": state_snap.somatic.dict(),
        "behavioral_constraints": state_snap.constraints.dict(),
        "stability": get_stability_evaluator().get_snapshot().to_dict(),
        "storage": {
            "storage_type": "persistent_disk",
            "chat_turns_count": len(get_history_store().get_history(1000)),
        },
    }


@app.post("/sim/clock/step")
async def sim_clock_step(req: ClockStepRequest) -> Dict[str, Any]:
    rt = _require_sim_runtime()
    return rt.step_simulation(req.delta_ms)


@app.post("/sim/clock/pause")
async def sim_clock_pause() -> Dict[str, Any]:
    rt = _require_sim_runtime()
    rt.pause_simulation()
    return {"status": "ok", "is_paused": True, "virtual_time_s": rt.sim_clock.virtual_time_s}


@app.post("/sim/clock/resume")
async def sim_clock_resume() -> Dict[str, Any]:
    rt = _require_sim_runtime()
    rt.start_simulation()
    return {"status": "ok", "is_paused": False, "virtual_time_s": rt.sim_clock.virtual_time_s}


@app.post("/sim/clock/speed")
async def sim_clock_speed(req: ClockSpeedRequest) -> Dict[str, Any]:
    rt = _require_sim_runtime()
    rt.sim_clock.set_speed(req.multiplier)
    return {"status": "ok", "speed_factor": rt.sim_clock.speed_factor}


@app.post("/sim/clock/reset")
async def sim_clock_reset(req: ClockResetRequest) -> Dict[str, Any]:
    rt = _require_sim_runtime()
    rt.reset_simulation()
    return {"status": "ok", "virtual_time_s": rt.sim_clock.virtual_time_s}


@app.post("/sim/stimulus/inject-text")
async def sim_stimulus_text(req: StimulusTextRequest) -> Dict[str, Any]:
    rt = _require_sim_runtime()
    entry = rt.stimulus_service.inject_text(req.text, source=req.source, custom_timestamp=rt.sim_clock.virtual_time_s)
    return {"status": "ok", "stimulus": entry, "pathway": entry.get("pathway"), "pad_after": entry.get("pad_after")}


@app.post("/sim/stimulus/inject-vector")
async def sim_stimulus_vector(req: StimulusVectorRequest) -> Dict[str, Any]:
    rt = _require_sim_runtime()
    entry = rt.stimulus_service.inject_vector(req.vector, source=req.source, custom_timestamp=rt.sim_clock.virtual_time_s)
    return {
        "status": "ok",
        "stimulus": entry,
        "pathway": entry.get("pathway"),
        "source": entry.get("source"),
        "pad_after": entry.get("pad_after"),
    }


@app.get("/sim/stimulus/presets")
async def sim_stimulus_presets() -> Dict[str, Any]:
    rt = _require_sim_runtime()
    return {"presets": rt.stimulus_service.get_presets()}


@app.post("/sim/stimulus/preset")
async def sim_stimulus_preset(req: StimulusPresetRequest) -> Dict[str, Any]:
    rt = _require_sim_runtime()
    entry = rt.stimulus_service.inject_preset(
        req.preset,
        pathway=req.pathway,
        source="sim_preset_api",
        custom_timestamp=rt.sim_clock.virtual_time_s,
    )
    return {
        "status": "ok",
        "stimulus": entry,
        "pathway": entry.get("pathway"),
        "source": entry.get("source"),
        "pad_after": entry.get("pad_after"),
    }


@app.get("/sim/stimulus/history")
async def sim_stimulus_history(limit: int = 50) -> Dict[str, Any]:
    rt = _require_sim_runtime()
    return {"history": rt.stimulus_service.get_history(limit)}


@app.get("/sim/scenarios/list")
async def sim_scenarios_list() -> Dict[str, Any]:
    rt = _require_sim_runtime()
    global _scenario_runner
    if _scenario_runner is None:
        _scenario_runner = ScenarioRunner(rt)
    return {"scenarios": _scenario_runner.list_scenarios()}


@app.post("/sim/scenarios/run")
async def sim_scenarios_run(req: ScenarioRunRequest) -> Dict[str, Any]:
    rt = _require_sim_runtime()
    global _scenario_runner
    if _scenario_runner is None:
        _scenario_runner = ScenarioRunner(rt)

    if req.scenario_id == "all":
        summary = _scenario_runner.run_all()
        results_list = list(summary["scenarios"].values())
        return {"all_passed": summary["all_passed"], "results": results_list, "summary": summary}
    res = _scenario_runner.run_scenario(req.scenario_id)
    return {"status": "ok", "results": [res], "result": res}


@app.get("/sim/scenarios/results")
async def sim_scenarios_results() -> Dict[str, Any]:
    rt = _require_sim_runtime()
    global _scenario_runner
    if _scenario_runner is None:
        _scenario_runner = ScenarioRunner(rt)
    last = _scenario_runner.get_last_results()
    if isinstance(last, dict) and "scenarios" in last:
        results_list = list(last["scenarios"].values())
    elif isinstance(last, dict):
        results_list = [v for k, v in last.items() if isinstance(v, dict) and "passed" in v]
    else:
        results_list = []
    return {"results": results_list, "last_run": last}


@app.post("/sim/chat")
async def sim_chat(req: ProcessRequest) -> Dict[str, Any]:
    rt = _require_sim_runtime()
    res = rt.send_chat(req.input, source="sim_chat_api")
    return {
        **res,
        "response": res.get("assistant_reply", ""),
        "call_id": f"sim_{uuid.uuid4().hex[:12]}",
    }


@app.get("/system/profile")
async def system_profile() -> Dict[str, Any]:
    """
    Return information about the active hardware profile and resource allocation.
    """
    if _resource_profile is None:
        return {"tier": "unknown"}
    return {
        "tier": _resource_profile.tier.value,
        "name": _resource_profile.name,
        "description": _resource_profile.description,
        "vram_mb": _resource_profile.vram_mb,
        "n_gpu_layers": _resource_profile.n_gpu_layers,
        "n_ctx": _resource_profile.n_ctx,
        "loop_cadence_ms": _resource_profile.loop_cadence_ms,
        "sdm_capacity": _resource_profile.sdm_capacity,
    }


@app.post("/system/profile")
async def update_system_profile(payload: Dict[str, Any]) -> Dict[str, Any]:
    """
    Dynamically update the active hardware scalability profile.
    """
    global _resource_profile
    profile_name = payload.get("profile", "auto")
    try:
        _resource_profile = get_resource_profile(profile_name)
        logger.info("Hardware scalability profile updated to: %s (%s)", _resource_profile.name, _resource_profile.tier.value)
        return {
            "status": "ok",
            "tier": _resource_profile.tier.value,
            "name": _resource_profile.name,
            "description": _resource_profile.description,
            "vram_mb": _resource_profile.vram_mb,
            "n_gpu_layers": _resource_profile.n_gpu_layers,
            "n_ctx": _resource_profile.n_ctx,
            "loop_cadence_ms": _resource_profile.loop_cadence_ms,
            "sdm_capacity": _resource_profile.sdm_capacity,
        }
    except Exception as exc:
        logger.error("Failed to update hardware profile to %s: %s", profile_name, exc)
        return {"status": "error", "message": str(exc)}



# ---------------------------------------------------------------------------
# CLI & Lifespan Logic
# ---------------------------------------------------------------------------

def _parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Lucia Backend Server")
    parser.add_argument("--port", type=int, default=8765, help="HTTP port")
    parser.add_argument("--model-path", type=str, default="", help="Path to GGUF model")
    parser.add_argument("--profile", type=str, default="auto", help="Hardware scaling tier")
    parser.add_argument("--log-level", type=str, default="INFO", help="Logging level")
    parser.add_argument(
        "--mode",
        type=str,
        default=os.environ.get("LUCIA_MODE", "live"),
        choices=["live", "simulation", "preview"],
        help="Runtime mode (live, simulation, or preview)",
    )
    return parser.parse_args()


def init_server(
    model_path: str = "",
    port: int = 8765,
    profile_name: str = "auto",
    log_level: str = "INFO",
    mode: str = "live",
) -> None:
    global _orchestrator, _resource_profile, _sim_runtime, _scenario_runner, _mode
    _mode = mode.lower()

    logging.basicConfig(level=getattr(logging, log_level.upper(), logging.INFO))

    if not (1024 <= port <= 65535):
        sys.stdout.write("LUCIA_BACKEND_ERROR: invalid_port\n")
        sys.stdout.flush()
        sys.exit(1)

    if _mode == "simulation":
        logger.info("Initializing Lucia Backend in SIMULATION mode...")
        try:
            _sim_runtime = SimulationRuntime()
            _scenario_runner = ScenarioRunner(_sim_runtime)
            _resource_profile = get_resource_profile("minimal")
            logger.info("Simulation runtime initialized successfully.")
        except Exception as exc:
            logger.exception("Failed to initialize SimulationRuntime: %s", exc)
            sys.stdout.write(f"LUCIA_BACKEND_ERROR: {exc}\n")
            sys.stdout.flush()
            sys.exit(1)

        # Signal ready to Electron parent process
        sys.stdout.write("LUCIA_BACKEND_READY\n")
        sys.stdout.flush()
        return

    # Live mode execution
    if not model_path:
        model_path = os.environ.get("LUCIA_MODEL_PATH", "")

    if not model_path:
        sys.stdout.write("LUCIA_BACKEND_ERROR: model_path_not_configured\n")
        sys.stdout.flush()
        sys.exit(1)

    try:
        _resource_profile = get_resource_profile(profile_name)
        config = MemoryOrchestratorConfig.from_profile(
            model_path=model_path,
            profile_name_or_tier=profile_name,
        )
        # Phase 9: use composition-based CognitiveOrchestrator (ADR-014)
        _orchestrator = build_cognitive_orchestrator(config)
    except Exception as exc:
        logger.exception("Failed to initialize Orchestrator: %s", exc)
        sys.stdout.write(f"LUCIA_BACKEND_ERROR: {exc}\n")
        sys.stdout.flush()
        sys.exit(1)

    # Signal ready to Electron parent process
    sys.stdout.write("LUCIA_BACKEND_READY\n")
    sys.stdout.flush()


def main() -> None:
    args = _parse_args()
    port = int(os.environ.get("LUCIA_PORT", args.port)) if args.port == 8765 else args.port
    mode = os.environ.get("LUCIA_MODE", args.mode)
    init_server(
        model_path=args.model_path,
        port=port,
        profile_name=args.profile,
        log_level=args.log_level,
        mode=mode,
    )

    def shutdown_handler(sig, frame):
        logger.info("Received termination signal %s, shutting down...", sig)
        if _sim_runtime is not None:
            _sim_runtime.shutdown()
        if _orchestrator is not None:
            _orchestrator.shutdown()
        sys.exit(0)

    signal.signal(signal.SIGINT, shutdown_handler)
    signal.signal(signal.SIGTERM, shutdown_handler)

    uvicorn.run(
        app,
        host="127.0.0.1",
        port=port,
        log_level=args.log_level.lower(),
        access_log=False,
    )


if __name__ == "__main__":
    main()
