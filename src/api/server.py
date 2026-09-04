"""
FastAPI HTTP server wrapping MemoryAugmentedOrchestrator for desktop IPC.

Endpoints:
    POST /process  — synchronous single-turn interaction
    GET  /state    — 500ms real-time emotional telemetry snapshot
    GET  /health   — orchestrator health check
    GET  /system/profile — current hardware scaling profile

Requirements: Phase 3 (1.1–1.8, 2.1–2.7, 3.1–3.7, 9.3)
"""

from __future__ import annotations

import argparse
import asyncio
import logging
import os
import signal
import sys
import time
import uuid
from typing import Any, Dict, Optional

# Ensure project root is on sys.path regardless of execution mode or IDE root
_PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "../.."))
if _PROJECT_ROOT not in sys.path:
    sys.path.insert(0, _PROJECT_ROOT)

from fastapi import FastAPI, HTTPException, Request, Response, status
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field
import uvicorn

from src.core.config import MemoryOrchestratorConfig
from src.core.models import BehavioralConstraints, SomaticMarkers
from src.core.orchestrator.orchestrator import MemoryAugmentedOrchestrator
from src.core.plugins.hook_bus import HookBus
from src.core.resource_manager import ResourceProfile, get_resource_profile
from src.core.storage.history_store import ChatHistoryStore
from src.core.telemetry.stability_evaluator import StabilityEvaluator

logger = logging.getLogger("lucia.api")

_hook_bus = HookBus()
_history_store = ChatHistoryStore()
_stability_evaluator = StabilityEvaluator()


# ---------------------------------------------------------------------------
# Pydantic Request / Response Models
# ---------------------------------------------------------------------------

class ProcessRequest(BaseModel):
    input: str = Field(..., min_length=1, max_length=4000)


class ProcessResponse(BaseModel):
    response: str
    call_id: str


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


# ---------------------------------------------------------------------------
# Instrumented Orchestrator subclass
# ---------------------------------------------------------------------------

class InstrumentedOrchestrator(MemoryAugmentedOrchestrator):
    """
    Subclasses MemoryAugmentedOrchestrator to expose latest somatic markers
    and behavioral constraints for GET /state telemetry.
    """

    def __init__(self, config: MemoryOrchestratorConfig) -> None:
        super().__init__(config)
        self._last_somatic: Optional[SomaticMarkers] = None
        self._last_constraints: Optional[BehavioralConstraints] = None

    def _execute_pipeline(
        self, input_text: str, call_id: str, t_start: float
    ) -> str:
        # Step 1-4 execute in parent, but we capture the intermediate metrics
        stimulus = self._stimulus_processor.encode(input_text)
        self._emotion_core.push_stimulus(stimulus)
        pad = self._emotion_core.get_pad_state()
        self._homeostatic_engine.record_input()
        markers = self._homeostatic_engine.compute_somatic_markers(pad)
        constraints = self._homeostatic_engine.compute_behavioral_constraints(
            markers, pad
        )

        self._last_somatic = markers
        self._last_constraints = constraints

        # Delegate rest of pipeline to super
        return super()._execute_pipeline(input_text, call_id, t_start)


# ---------------------------------------------------------------------------
# FastAPI Application & Global State
# ---------------------------------------------------------------------------

app = FastAPI(title="Lucia Backend API", version="3.0.0")

_orchestrator: Optional[InstrumentedOrchestrator] = None
_resource_profile: Optional[ResourceProfile] = None


def get_orchestrator() -> InstrumentedOrchestrator:
    if _orchestrator is None:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Orchestrator not initialized",
        )
    return _orchestrator


@app.post("/process", response_model=ProcessResponse)
async def process_turn(req: ProcessRequest) -> Dict[str, str]:
    """
    Execute full cognitive-emotional turn synchronously via run_in_executor.
    """
    orch = get_orchestrator()
    if orch._degraded or not orch.is_healthy():
        return JSONResponse(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            content={
                "error": "orchestrator_degraded",
                "call_id": uuid.uuid4().hex,
            },
        )

    call_id = uuid.uuid4().hex
    _hook_bus.emit("on_turn_start", req.input)
    _history_store.append_turn("user", req.input)

    loop = asyncio.get_running_loop()

    try:
        response_text = await loop.run_in_executor(None, orch.process, req.input)

        # Update stability metrics
        if hasattr(orch, "_affective_memory") and orch._affective_memory is not None:
            _stability_evaluator.update_sdm_count(orch._affective_memory.trace_count)

        # Store turn in history
        _history_store.append_turn("companion", response_text)
        _hook_bus.emit("on_turn_completed", {"user": req.input, "response": response_text})

        return {"response": response_text, "call_id": call_id}
    except Exception as exc:
        logger.exception("Exception processing turn (call_id=%s): %s", call_id, exc)
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content={"error": "internal_error", "call_id": call_id},
        )


@app.get("/state", response_model=StateSnapshot)
async def get_state(response: Response) -> StateSnapshot:
    """
    Return non-blocking real-time emotional state snapshot with no caching.
    """
    response.headers["Cache-Control"] = "no-store"
    orch = get_orchestrator()

    pad_state = orch._emotion_core.get_pad_state()
    pad_snap = PADSnapshot(
        pleasure=float(pad_state.pleasure),
        arousal=float(pad_state.arousal),
        dominance=float(pad_state.dominance),
    )

    somatic = orch._last_somatic
    if somatic is not None:
        somatic_snap = SomaticSnapshot(
            stability=float(somatic.stability),
            cognitive_load=float(somatic.cognitive_load),
            energy=float(somatic.energy),
            tension=float(somatic.tension),
        )
    else:
        somatic_snap = SomaticSnapshot(
            stability=0.0, cognitive_load=0.0, energy=0.0, tension=0.0
        )

    constraints = orch._last_constraints
    if constraints is not None:
        constraints_snap = ConstraintsSnapshot(
            max_tokens=int(constraints.max_tokens),
            temperature=float(constraints.temperature),
            latency_ms=int(constraints.latency_ms),
            reasoning_depth=int(constraints.reasoning_depth),
        )
    else:
        constraints_snap = ConstraintsSnapshot(
            max_tokens=150, temperature=0.75, latency_ms=0, reasoning_depth=1
        )

    trace_count = orch._affective_memory.trace_count if hasattr(orch, "_affective_memory") else len(orch._affective_memory.get_all_traces())

    profile_name = _resource_profile.name if _resource_profile else "auto"

    return StateSnapshot(
        pad=pad_snap,
        somatic=somatic_snap,
        constraints=constraints_snap,
        memory_trace_count=trace_count,
        timestamp=time.monotonic(),
        profile=profile_name,
    )


from fastapi.responses import JSONResponse, Response
from src.core.voice.voice_engine import VoiceEngine, VoiceEngineConfig

_voice_engine: VoiceEngine = VoiceEngine()


class SynthesizeRequest(BaseModel):
    text: str
    rate: Optional[str] = None
    volume: Optional[str] = None
    pitch: Optional[str] = None


class SelectModelRequest(BaseModel):
    model_name: str


@app.post("/voice/synthesize")
async def synthesize_voice(req: SynthesizeRequest) -> Response:
    """
    Synthesize spoken audio for the given text using current voice/RVC settings.
    """
    if not req.text.strip():
        return Response(content=b"", media_type="audio/mpeg")
    try:
        audio_data = await _voice_engine.synthesize_speech(
            req.text, rate=req.rate, volume=req.volume, pitch=req.pitch
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


@app.get("/telemetry/stability")
async def get_stability_telemetry() -> Dict[str, Any]:
    """
    Return composite Limbic Stability Index (LSI), tick jitter, and ODE variance.
    """
    return _stability_evaluator.get_snapshot().to_dict()


@app.get("/history")
async def get_chat_history(limit: int = 50) -> Dict[str, Any]:
    """
    Return recent conversation turns across active and past sessions.
    """
    return {"turns": _history_store.get_history(limit=limit)}


@app.post("/history/new-session")
async def new_chat_session() -> Dict[str, Any]:
    """
    Start a fresh conversation session without deleting older history.
    """
    session_id = _history_store.new_session()
    return {"status": "ok", "session_id": session_id}


@app.delete("/history")
async def clear_chat_history() -> Dict[str, Any]:
    """
    Clear all conversation history logs.
    """
    _history_store.clear_history()
    return {"status": "ok", "message": "History cleared"}


@app.get("/history/export")
async def export_chat_history() -> Response:
    """
    Export full conversation history as a formatted Markdown file.
    """
    md_content = _history_store.export_markdown()
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


def _get_profile_file() -> Path:
    p = Path("data/profile.json")
    p.parent.mkdir(parents=True, exist_ok=True)
    if not p.exists():
        initial = {
            "version": 1,
            "user_name": "Friend",
            "companion_name": "Lucia",
            "born_at": datetime.now().isoformat(),
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
    p = _get_profile_file()
    try:
        with open(p, "r", encoding="utf-8") as f:
            data = json.load(f)
            if isinstance(data, dict):
                return data
    except Exception as e:
        logger.error("Failed to read profile: %s", e)
    return {"version": 1, "user_name": "Friend", "companion_name": "Lucia", "is_onboarded": False}


@app.post("/profile")
async def update_profile(req: ProfileUpdateRequest) -> Dict[str, Any]:
    """
    Update profile fields (user name, companion name, onboarding status).
    """
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

    try:
        with open(p, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
    except Exception as e:
        logger.error("Failed to save profile: %s", e)

    return {"status": "ok", "profile": data}


@app.get("/health")
async def health_check() -> Dict[str, str]:
    """
    Healthcheck endpoint for ProcessManager monitoring.
    """
    if _orchestrator is not None and _orchestrator.is_healthy():
        return {"status": "ok"}
    return JSONResponse(
        status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
        content={"status": "degraded"},
    )


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
    return parser.parse_args()


def init_server(
    model_path: str,
    port: int = 8765,
    profile_name: str = "auto",
    log_level: str = "INFO",
) -> None:
    global _orchestrator, _resource_profile

    logging.basicConfig(level=getattr(logging, log_level.upper(), logging.INFO))

    # Read env fallbacks
    if not model_path:
        model_path = os.environ.get("LUCIA_MODEL_PATH", "")

    if not model_path:
        sys.stdout.write("LUCIA_BACKEND_ERROR: model_path_not_configured\n")
        sys.stdout.flush()
        sys.exit(1)

    if not (1024 <= port <= 65535):
        sys.stdout.write("LUCIA_BACKEND_ERROR: invalid_port\n")
        sys.stdout.flush()
        sys.exit(1)

    try:
        _resource_profile = get_resource_profile(profile_name)
        config = MemoryOrchestratorConfig.from_profile(
            model_path=model_path,
            profile_name_or_tier=profile_name,
        )
        _orchestrator = InstrumentedOrchestrator(config)
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
    init_server(
        model_path=args.model_path,
        port=port,
        profile_name=args.profile,
        log_level=args.log_level,
    )

    def shutdown_handler(sig, frame):
        logger.info("Received termination signal %s, shutting down...", sig)
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
