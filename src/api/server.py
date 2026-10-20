"""
FastAPI HTTP server — Phase 9 Cognitive Unification.

Endpoints:
    POST /process  — serialized single-turn cognitive loop (asyncio.Lock, HTTP 429 guard)
    GET  /state    — non-blocking real-time emotional telemetry snapshot
    GET  /health   — orchestrator health check
    GET  /system/hardware — factual host hardware and compute capabilities

Requirements: Phase 3 (1.1–1.8, 2.1–2.7, 3.1–3.7, 9.3); Phase 9 (ADR-014–ADR-020)
"""

from __future__ import annotations

import argparse
import asyncio
from contextlib import asynccontextmanager
import copy
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
from src.core.hardware import HostCapabilities, detect_host_capabilities
from src.core.simulation import (
    ActivationSafetyError,
    ScenarioRunner,
    SimulationRuntime,
)
from src.core.identity.instance_lock import (
    DEFAULT_LOCK_PATH,
    InstanceAuthorityConflictError,
    InstanceLock,
)
from src.core.identity.identity_anchor import (
    CorruptedIdentityAnchorError,
    DecommissionedInstanceError,
    FrozenMigrationStateError,
    ImmutableIdentityMutationError,
    InvalidIdentityAnchorError,
    guard_immutable_fields,
    verify_identity_on_startup,
)
from src.core.identity.provenance_verifier import (
    ProvenanceVerificationStatus,
    verify_provenance_and_environment,
)
from src.core.identity.genesis import (
    GenesisCommitmentCorruptedError,
    GenesisError,
    GenesisVerificationError,
    GenesisVerificationOutcome,
    OntologyState,
    TerminalLifecycleError,
    mark_lifecycle_ended,
    verify_genesis,
)
from src.core.identity.operator_genesis import (
    OperatorGenesisError,
    OperatorPreconditionError,
)
from src.core.identity.awakening import (
    AwakeningResult,
    awaken_companion,
    get_awakening_status,
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
_instance_lock: Optional[InstanceLock] = None
_is_live_companion_active: bool = False


def get_instance_lock() -> Optional[InstanceLock]:
    global _instance_lock
    return _instance_lock


def get_history_store() -> Any:
    global _history_store
    if _sim_runtime is not None:
        return _sim_runtime.chat_store
    if _history_store is None:
        chat_path = os.environ.get("LUCIA_CHAT_HISTORY_PATH", "data/chat_history.json")
        _history_store = ChatHistoryStore(file_path=chat_path)
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
    language: Optional[str] = None


class ProcessResponse(BaseModel):
    response: str
    call_id: str
    surprise: float = 0.0
    generation_mode: str = "reflexive"
    expression: Optional[Dict[str, Any]] = None
    relationship: Optional[Dict[str, Any]] = None
    communication: Optional[Dict[str, Any]] = None
    realization: Optional[Dict[str, Any]] = None


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


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Lifespan manager: clean up instance authority upon server shutdown."""
    yield
    global _instance_lock
    if _instance_lock is not None and _instance_lock.is_locked:
        _instance_lock.release()


app = FastAPI(title="Lucia Backend API", version="9.0.0", lifespan=lifespan)

_orchestrator: Optional[CognitiveOrchestrator] = None


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

    # First Activation Gate (ARCH-034 / G1-G4 §11)
    if not _is_live_companion_active:
        return JSONResponse(
            status_code=status.HTTP_403_FORBIDDEN,
            content={
                "error": "runtime_inactive",
                "detail": "Live companion is inactive. First activation via POST /lifecycle/activate is required before conversational processing.",
            },
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
                if req.language is not None:
                    result: CognitiveTurnResult = await loop.run_in_executor(
                        None, orch.process, req.input, req.language
                    )
                else:
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
        realization_dict = (
            result.realization.to_dict()
            if isinstance(result, CognitiveTurnResult) and result.realization is not None
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
            "realization": realization_dict,
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
    profile_name = detect_host_capabilities().backend

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
    language: Optional[str] = "ja"
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
            language=req.language or "ja",
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
    identity_anchor: Optional[Dict[str, Any]] = None
    phylogenetic_lineage: Optional[Dict[str, Any]] = None


class AwakenRequest(BaseModel):
    user_name: Optional[str] = None
    companion_name: Optional[str] = None
    confirm_ceremony: bool = True
    genesis_commit: Optional[str] = None


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
    p = Path(os.environ.get("LUCIA_PROFILE_PATH") or _PROFILE_FILE_PATH)
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
    p = Path(os.environ.get("LUCIA_PROFILE_PATH") or _PROFILE_FILE_PATH)
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

    existing_copy = copy.deepcopy(data)

    if req.user_name is not None:
        data["user_name"] = req.user_name.strip()
    if req.companion_name is not None:
        data["companion_name"] = req.companion_name.strip()
    if req.is_onboarded is not None:
        if req.is_onboarded is True and not existing_copy.get("is_onboarded", False):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Direct onboarding/birth activation via POST /profile is forbidden. "
                       "Genesis/Birth requires the canonical operator Genesis ceremony, "
                       "and activation requires POST /lifecycle/activate.",
            )
        data["is_onboarded"] = req.is_onboarded
    if req.birthday is not None:
        data["birthday"] = req.birthday
    if req.pronouns is not None:
        data["pronouns"] = req.pronouns
    if req.born_at is not None:
        if existing_copy.get("born_at") is None and not existing_copy.get("is_onboarded", False):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Direct 'born_at' mutation via POST /profile is forbidden. "
                       "'born_at' is an immutable field established exclusively during Genesis.",
            )
        data["born_at"] = req.born_at
    if req.identity_anchor is not None:
        if existing_copy.get("identity_anchor") is None and not existing_copy.get("is_onboarded", False):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Direct 'identity_anchor' injection via POST /profile is forbidden. "
                       "The Identity Anchor is established exclusively during Genesis.",
            )
        data["identity_anchor"] = req.identity_anchor
    if req.phylogenetic_lineage is not None:
        data["phylogenetic_lineage"] = req.phylogenetic_lineage

    # WP-02: Guard immutable identity anchor fields
    try:
        guard_immutable_fields(existing_copy, data)
    except ImmutableIdentityMutationError as exc:
        logger.warning("Immutable identity mutation rejected: %s", exc)
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Immutable identity mutation rejected: {exc}",
        )

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

    First Activation Boundary (G1–G4 §11):
    - Genesis establishes durable origin: BORN + INACTIVE.
    - Activation verifies BORN and transitions runtime state to ACTIVE.
    - Activation MUST NOT create Birth.
    - Fails closed if instance is NOT_BORN (NOT_FOUND), UNKNOWN, INVALID_EVIDENCE, or ENDED.
    """
    global _is_live_companion_active

    if _mode == "simulation" or _sim_runtime is not None:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Cannot activate live companion in simulation mode. Direct lifecycle activation is strictly forbidden in simulation mode.",
        )

    p = _get_profile_file()
    c_p = Path(os.environ.get("LUCIA_GENESIS_COMMITMENT_PATH") or (p.parent / "genesis_commitment.json"))
    verification = verify_genesis(commitment_path=c_p, profile_path=p)

    if verification.ontology_state == OntologyState.ENDED:
        raise HTTPException(
            status_code=status.HTTP_410_GONE,
            detail="Cannot activate companion: instance lifecycle has ENDED (terminal state). Activation is permanently forbidden.",
        )

    if verification.outcome == GenesisVerificationOutcome.NOT_FOUND:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cannot activate companion: instance is NOT_BORN. First activation requires an existing valid durable Genesis Commitment. Activation does not create Birth.",
        )

    if verification.outcome == GenesisVerificationOutcome.UNKNOWN:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=f"Cannot activate companion: Genesis verification returned UNKNOWN ({verification.error_details}). Failing closed.",
        )

    if verification.outcome == GenesisVerificationOutcome.INVALID_EVIDENCE:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"Cannot activate companion: Genesis verification failed with INVALID_EVIDENCE ({verification.error_details}). Failing closed to prevent unanchored activation.",
        )

    # Verification succeeded: Ontology is BORN
    try:
        with open(p, "r", encoding="utf-8") as f:
            data = json.load(f)
            if not isinstance(data, dict):
                data = {}
    except Exception:
        data = {}

    born_at_val = (
        verification.commitment.record.identity_anchor.born_at
        if verification.commitment
        else data.get("born_at")
    )

    if _is_live_companion_active:
        return {
            "status": "already_active",
            "message": "Lucia is already active",
            "born_at": born_at_val,
            "companion_name": data.get("companion_name", "Lucia"),
        }

    _is_live_companion_active = True
    logger.info("Lucia activated in live mode at %s", born_at_val)
    return {
        "status": "activated",
        "born_at": born_at_val,
        "companion_name": data.get("companion_name", "Lucia"),
    }


@app.post("/lifecycle/awaken")
async def awaken_companion_route(req: AwakenRequest) -> Dict[str, Any]:
    """
    User-facing Genesis Awakening Ceremony Orchestration Endpoint.

    Governing Architecture:
    - Orchestrates the complete Awakening Ceremony above low-level Birth and Activation boundaries.
    - First-time Lucia:
        NOT_BORN -> Genesis Birth -> verify durable Genesis Commitment -> BORN + INACTIVE -> First Activation -> BORN + ACTIVE.
    - Existing Lucia:
        BORN + INACTIVE -> First Activation -> BORN + ACTIVE. (Never repeats Genesis Birth).
    - Already active:
        BORN + ACTIVE -> idempotent confirmation.
    - Ended:
        ENDED -> permanently rejected (410 GONE).
    - Strictly gated to live mode.
    """
    global _is_live_companion_active

    if _mode == "simulation" or _sim_runtime is not None:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Cannot awaken live companion in simulation mode. Direct lifecycle awakening is strictly forbidden in simulation mode.",
        )

    p = _get_profile_file()
    c_p = Path(os.environ.get("LUCIA_GENESIS_COMMITMENT_PATH") or (p.parent / "genesis_commitment.json"))
    ws = Path(os.environ.get("LUCIA_WORKSPACE_PATH") or Path.cwd())

    def _activate_runtime() -> None:
        global _is_live_companion_active
        _is_live_companion_active = True
        logger.info("Lucia activated in live mode via Awakening ceremony")

    try:
        res = awaken_companion(
            confirm_ceremony=req.confirm_ceremony,
            user_name=req.user_name,
            companion_name=req.companion_name,
            genesis_commit=req.genesis_commit,
            workspace_dir=ws,
            commitment_path=c_p,
            profile_path=p,
            is_runtime_active=_is_live_companion_active,
            activate_runtime_fn=_activate_runtime,
        )
        return res.to_dict()
    except TerminalLifecycleError as exc:
        raise HTTPException(
            status_code=status.HTTP_410_GONE,
            detail=str(exc),
        )
    except OperatorPreconditionError as exc:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(exc),
        )
    except (GenesisVerificationError, GenesisCommitmentCorruptedError) as exc:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=str(exc),
        )
    except GenesisError as exc:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(exc),
        )


@app.get("/lifecycle/status")
async def get_lifecycle_status_route() -> Dict[str, Any]:
    """Query current ontological and runtime lifecycle status."""
    p = _get_profile_file()
    c_p = Path(os.environ.get("LUCIA_GENESIS_COMMITMENT_PATH") or (p.parent / "genesis_commitment.json"))
    ws = Path(os.environ.get("LUCIA_WORKSPACE_PATH") or Path.cwd())

    return get_awakening_status(
        workspace_dir=ws,
        commitment_path=c_p,
        profile_path=p,
        is_runtime_active=_is_live_companion_active,
    )


@app.post("/lifecycle/end")
async def end_lifecycle() -> Dict[str, Any]:
    """
    Atomic transition ending the current Lucia's lifecycle.
    Disabled in simulation mode.

    Terminal Lifecycle Transition (G1–G4 §7, §10):
    - Transitions ontology state to ENDED.
    - Resets orchestrator, chat history, and stability evaluator.
    - Permanently forbids re-Genesis and activation.
    """
    global _is_live_companion_active

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

        # 4. Mark lifecycle as permanently ENDED
        p = _get_profile_file()
        c_p = Path(os.environ.get("LUCIA_GENESIS_COMMITMENT_PATH") or (p.parent / "genesis_commitment.json"))
        mark_lifecycle_ended(commitment_path=c_p, profile_path=p)

        # 5. Deactivate runtime
        _is_live_companion_active = False

        # 6. Reset profile persistence to un-onboarded / Genesis-ready state
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
        "active_profile": detect_host_capabilities().backend,
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


@app.get("/system/hardware")
async def system_hardware() -> Dict[str, Any]:
    """
    Return factual host hardware and compute capabilities (device, CUDA, VRAM, CPU threads).
    """
    caps = detect_host_capabilities()
    return caps.to_dict()



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
    lock_path: Optional[Union[str, Path]] = None,
    warmup_voice: bool = False,
) -> None:
    global _orchestrator, _sim_runtime, _scenario_runner, _mode, _instance_lock
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

    # Live mode execution — acquire exclusive instance authority before any state mutation
    active_lock_path = lock_path or os.environ.get("LUCIA_LOCK_PATH") or DEFAULT_LOCK_PATH
    if _instance_lock is None or not _instance_lock.is_locked:
        _instance_lock = InstanceLock(lock_path=active_lock_path)
        try:
            _instance_lock.acquire()
        except InstanceAuthorityConflictError:
            logger.critical(
                "FATAL: Another active Lucia instance holds write authority over this directory. "
                "Exiting to prevent state corruption."
            )
            sys.stdout.write("LUCIA_BACKEND_ERROR: instance_already_active\n")
            sys.stdout.flush()
            sys.exit(75)

    # WP-02: Validate identity anchor integrity before any model or store operations
    active_profile_path = os.environ.get("LUCIA_PROFILE_PATH") or _PROFILE_FILE_PATH
    try:
        identity_state = verify_identity_on_startup(active_profile_path)
        if identity_state.is_genesis_locked:
            logger.info("Lucia Genesis gate is LOCKED (un-onboarded profile). Runtime in Genesis-ready mode.")
        else:
            logger.info(
                "Lucia identity anchor verified: uuid=%s",
                identity_state.anchor.instance_uuid if identity_state.anchor else None,
            )
    except DecommissionedInstanceError as exc:
        logger.critical(
            "FATAL: Instance has been decommissioned via migration: %s. "
            "Refusing to boot to prevent dual-authority split-brain.",
            exc,
        )
        if _instance_lock is not None and _instance_lock.is_locked:
            _instance_lock.release()
        sys.stdout.write("LUCIA_BACKEND_ERROR: instance_decommissioned\n")
        sys.stdout.flush()
        sys.exit(1)
    except FrozenMigrationStateError as exc:
        logger.critical(
            "FATAL: Instance is frozen for migration: %s. "
            "Refusing to boot while migration is in progress.",
            exc,
        )
        if _instance_lock is not None and _instance_lock.is_locked:
            _instance_lock.release()
        sys.stdout.write("LUCIA_BACKEND_ERROR: instance_frozen_for_migration\n")
        sys.stdout.flush()
        sys.exit(1)
    except (InvalidIdentityAnchorError, CorruptedIdentityAnchorError) as exc:
        logger.critical(
            "FATAL: Corrupted or invalid identity anchor detected: %s. "
            "Failing closed to prevent identity state corruption.",
            exc,
        )
        if _instance_lock is not None and _instance_lock.is_locked:
            _instance_lock.release()
        sys.stdout.write("LUCIA_BACKEND_ERROR: corrupted_identity_anchor\n")
        sys.stdout.flush()
        sys.exit(1)

    # WP-03: Verify workspace provenance & environment binding
    if not identity_state.is_genesis_locked:
        active_workspace = Path(os.environ.get("LUCIA_WORKSPACE_PATH") or Path.cwd())
        allow_reconfirm = os.environ.get("LUCIA_RECONFIRM_HARDWARE") == "1"
        try:
            prov_result = verify_provenance_and_environment(
                workspace_path=active_workspace,
                profile_path=active_profile_path,
                allow_reconfirmation=allow_reconfirm,
            )
            if not prov_result.is_valid:
                if prov_result.status == ProvenanceVerificationStatus.AWAITING_HARDWARE_RECONFIRMATION:
                    logger.critical(
                        "FATAL: Hardware environment divergence detected. "
                        "Entering AWAITING_HARDWARE_RECONFIRMATION state to prevent split-brain branching."
                    )
                    if _instance_lock is not None and _instance_lock.is_locked:
                        _instance_lock.release()
                    sys.stdout.write("LUCIA_BACKEND_ERROR: awaiting_hardware_reconfirmation\n")
                    sys.stdout.flush()
                    sys.exit(76)
                elif prov_result.status == ProvenanceVerificationStatus.WORKSPACE_DIVERGENCE:
                    logger.critical(
                        "FATAL: Workspace location divergence detected: expected '%s', actual '%s'. "
                        "Failing closed to prevent folder-duplication branching.",
                        prov_result.recorded_workspace_path,
                        prov_result.workspace_path,
                    )
                    if _instance_lock is not None and _instance_lock.is_locked:
                        _instance_lock.release()
                    sys.stdout.write("LUCIA_BACKEND_ERROR: workspace_location_divergence\n")
                    sys.stdout.flush()
                    sys.exit(1)
                elif prov_result.status == ProvenanceVerificationStatus.WALL_CLOCK_ROLLBACK_DETECTED:
                    logger.critical(
                        "FATAL: Wall-clock discontinuity detected: %s. "
                        "Failing closed to protect temporal causality.",
                        prov_result.divergence_details,
                    )
                    if _instance_lock is not None and _instance_lock.is_locked:
                        _instance_lock.release()
                    sys.stdout.write("LUCIA_BACKEND_ERROR: wall_clock_rollback_detected\n")
                    sys.stdout.flush()
                    sys.exit(1)
                elif prov_result.status == ProvenanceVerificationStatus.MISSING_AUTHORITY_BINDING:
                    logger.critical(
                        "FATAL: Onboarded profile is missing 'authority_binding' section. "
                        "Failing closed to prevent unanchored execution.",
                    )
                    if _instance_lock is not None and _instance_lock.is_locked:
                        _instance_lock.release()
                    sys.stdout.write("LUCIA_BACKEND_ERROR: missing_authority_binding\n")
                    sys.stdout.flush()
                    sys.exit(1)
                else:
                    logger.critical(
                        "FATAL: Provenance and environment verification failed: %s (%s)",
                        prov_result.status,
                        prov_result.divergence_details,
                    )
                    if _instance_lock is not None and _instance_lock.is_locked:
                        _instance_lock.release()
                    sys.stdout.write("LUCIA_BACKEND_ERROR: provenance_verification_failed\n")
                    sys.stdout.flush()
                    sys.exit(1)
            else:
                logger.info(
                    "Workspace provenance and environment verified: status=%s, matched=%s",
                    prov_result.status.value,
                    prov_result.hardware_matched,
                )
        except Exception as exc:
            logger.critical("FATAL: Error during provenance/environment verification: %s", exc)
            if _instance_lock is not None and _instance_lock.is_locked:
                _instance_lock.release()
            sys.stdout.write(f"LUCIA_BACKEND_ERROR: {exc}\n")
            sys.stdout.flush()
            sys.exit(1)
    else:
        logger.info("Lucia Genesis gate is LOCKED (un-onboarded profile). Workspace provenance check deferred.")

    if not model_path:
        model_path = os.environ.get("LUCIA_MODEL_PATH", "")

    if not model_path:
        if _instance_lock is not None and _instance_lock.is_locked:
            _instance_lock.release()
        sys.stdout.write("LUCIA_BACKEND_ERROR: model_path_not_configured\n")
        sys.stdout.flush()
        sys.exit(1)

    try:
        host_caps = detect_host_capabilities()
        n_gpu = 32 if host_caps.cuda_available else 0
        config = MemoryOrchestratorConfig(model_path=model_path, n_gpu_layers=n_gpu)
        # Phase 9: use composition-based CognitiveOrchestrator (ADR-014); F-02: reseed from persistent history
        _orchestrator = build_cognitive_orchestrator(
            config,
            chat_history_path=os.environ.get("LUCIA_CHAT_HISTORY_PATH", "data/chat_history.json"),
            relationship_storage_path=os.environ.get("LUCIA_RELATIONSHIP_PATH"),
            dynamical_storage_path=os.environ.get("LUCIA_DYNAMICAL_PATH"),
            epoch_manifest_path=os.environ.get("LUCIA_EPOCH_MANIFEST_PATH"),
        )
    except Exception as exc:
        if _instance_lock is not None and _instance_lock.is_locked:
            _instance_lock.release()
        logger.exception("Failed to initialize Orchestrator: %s", exc)
        sys.stdout.write(f"LUCIA_BACKEND_ERROR: {exc}\n")
        sys.stdout.flush()
        sys.exit(1)

    # Warm up RVC voice pipeline if requested or enabled via environment
    if warmup_voice or (os.environ.get("LUCIA_WARMUP_RVC") == "1" and mode == "live"):
        try:
            _voice_engine.warmup_rvc()
        except Exception as exc:
            logger.warning("VoiceEngine: startup warmup skipped or non-fatal error: %s", exc)

    # Signal ready to Electron parent process
    sys.stdout.write("LUCIA_BACKEND_READY\n")
    sys.stdout.flush()


def main() -> None:
    args = _parse_args()
    port = int(os.environ.get("LUCIA_PORT", args.port)) if args.port == 8765 else args.port
    mode = os.environ.get("LUCIA_MODE", args.mode)
    warmup_voice = os.environ.get("LUCIA_WARMUP_RVC", "1") != "0" and mode == "live"
    init_server(
        model_path=args.model_path,
        port=port,
        profile_name=args.profile,
        log_level=args.log_level,
        mode=mode,
        warmup_voice=warmup_voice,
    )

    def shutdown_handler(sig, frame):
        logger.info("Received termination signal %s, shutting down...", sig)
        if _sim_runtime is not None:
            _sim_runtime.shutdown()
        if _orchestrator is not None:
            _orchestrator.shutdown()
        if _instance_lock is not None and _instance_lock.is_locked:
            _instance_lock.release()
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
