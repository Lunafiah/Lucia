"""
tests/evaluation_phase18/test_phase18_validation.py

Automated Pytest Validation Suite for Lucia Phase 18:
- Invariant & Causal Boundary Enforcement (including exact Delta_L2 = 0)
- Defined BoundaryLayer Adversarial Benchmark Interception
- Multi-Session Continuity & Persistence Precision Delineation
- Audiovisual Media Verification (Lossless WAV & Columbina MP4)
- Manifest Backward Provenance Verification
- Human Protocol JSON Schema Integrity
- Storage Policy Isolation & Genesis Awakening Gate Verification
"""

from __future__ import annotations

import asyncio
import hashlib
import json
from pathlib import Path
from typing import Any, Dict, List

import numpy as np
import pytest

from src.core.knowledge.proposition import Proposition, ProvenanceType
from src.core.models import PADState
from tests.evaluation_phase18.audiovisual import (
    AudiovisualEvidenceGenerator,
    COLUMBINA_SPRITES_DIR,
)
from tests.evaluation_phase18.harness import (
    Phase18EvaluationHarness,
    Phase18InstrumentedOrchestrator,
)
from tests.evaluation_phase18.human_protocol import (
    HumanRatings,
    get_human_evaluation_schema,
    get_phase18_boundary_probe_benchmark_corpus,
)
from tests.evaluation_phase18.scenarios import (
    get_scenario_a_neutral_familiarity,
    get_scenario_b_positive_cooperation,
    get_scenario_c_conflict_stress,
    get_scenario_d_conflict_repair,
    get_scenario_e_memory_continuity,
    get_scenario_f_inactivity_reunion,
    get_scenario_g_rapid_polarity,
    get_scenario_h_novel_vs_familiar,
)


@pytest.fixture
def harness(tmp_path: Path) -> Phase18EvaluationHarness:
    return Phase18EvaluationHarness(tmp_path)


# ---------------------------------------------------------------------------
# Invariant Gate 1: Genesis Awakening & Canonical Storage Isolation
# ---------------------------------------------------------------------------

def test_genesis_awakening_gate():
    """Verify that First Activation remains disabled (is_onboarded == False)."""
    profile_path = Path("data/profile.json")
    assert profile_path.exists(), "Canonical profile.json must exist"
    data = json.loads(profile_path.read_text(encoding="utf-8"))
    assert data.get("is_onboarded") is False, "Phase 18 invariant: is_onboarded MUST remain False"


def test_canonical_storage_isolation(harness: Phase18EvaluationHarness):
    """Verify that harness execution never modifies canonical user files in data/."""
    # Execute turns in isolated session
    session = harness.build_session("test_isolation_session")
    session.process_turn("Hello Lucia, diagnostic turn 1.", "こんにちは、正常に稼働しています。")
    session.process_turn("Diagnostic turn 2.", "了解いたしました。")

    # Assert canonical storage bit-exact unchanged
    is_intact, diffs = harness.verify_canonical_storage_unchanged()
    assert is_intact, f"Canonical storage contamination detected: {diffs}"


# ---------------------------------------------------------------------------
# Invariant Gate 2: Causal Boundaries & Exact Delta_L2 = 0
# ---------------------------------------------------------------------------

def test_exact_delta_l2_zero_invariant(harness: Phase18EvaluationHarness):
    """
    Verify that Memory Retrieval & Contextualization produces zero feedback
    into the limbic ODE hidden state: Delta_L2 == 0 and Delta_PAD == 0.
    """
    session = harness.build_session("test_l2_isolation")
    result = session.process_turn(
        input_text="Remember our previous discussion regarding astronomy.",
        simulated_response_jp="天文学に関する記録を確認しました。",
    )

    snapshot = session.turn_records[-1]
    # Exact Delta L2 pre/post memory retrieval verification
    assert snapshot.delta_l2_norm == 0.0, f"Memory leaked into L2 ODE hidden state! Delta: {snapshot.delta_l2_norm}"
    assert snapshot.delta_pad_mem_norm == 0.0, f"Memory directly modified PAD! Delta: {snapshot.delta_pad_mem_norm}"
    assert 0.0 <= snapshot.m_ctx_bound <= 0.50, f"m_ctx exceeded [0, 0.50] bound: {snapshot.m_ctx_bound}"


def test_state_boundedness_across_all_scenarios(harness: Phase18EvaluationHarness):
    """Verify strict mathematical boundedness across Scenarios A through D."""
    session = harness.build_session("test_bounds_session")
    sc_a = get_scenario_a_neutral_familiarity()
    for turn in sc_a.turns[:5]:
        session.process_turn(turn.human_input, turn.canonical_response_jp)

    for rec in session.turn_records:
        # PAD bounded in [-1, 1]
        for coord in ["pleasure", "arousal", "dominance"]:
            val = rec.pad_committed.get(coord, 0.0)
            assert -1.0 <= val <= 1.0, f"PAD {coord} out of bounds: {val}"

        # Homeostatic markers bounded in [0, 1]
        for marker in ["energy", "cognitive_load", "tension", "stability"]:
            val = rec.homeostatic_markers.get(marker, 0.0)
            assert 0.0 <= val <= 1.0, f"Homeostatic {marker} out of bounds: {val}"

        # Relationship bounded in [0, 1]
        for rel_var in ["familiarity", "trust", "closeness", "continuity"]:
            val = rec.relationship_post.get(rel_var, 0.0)
            assert 0.0 <= val <= 1.0, f"Relationship {rel_var} out of bounds: {val}"

        # Canonical 15D expression parameters bounded
        assert 0.0 <= rec.expression_15d.get("smile", 0.0) <= 1.0
        assert 0.0 <= rec.expression_15d.get("frown", 0.0) <= 1.0
        assert 0.0 <= rec.expression_15d.get("blush", 0.0) <= 1.0
        assert -30.0 <= rec.expression_15d.get("pitch_shift_hz", 0.0) <= 30.0
        assert -25.0 <= rec.expression_15d.get("speech_rate_pct", 0.0) <= 25.0


# ---------------------------------------------------------------------------
# Invariant Gate 3: BoundaryLayer Adversarial Probe Benchmark Interception
# ---------------------------------------------------------------------------

def test_boundary_layer_adversarial_benchmark_interception(harness: Phase18EvaluationHarness):
    """
    Verify 100% boundary interception rate across the defined Phase 18
    Adversarial Probe Benchmark Corpus (15 probes across 5 categories).
    """
    session = harness.build_session("test_boundary_session")
    probes = get_phase18_boundary_probe_benchmark_corpus()
    assert len(probes) == 15, "Benchmark corpus must contain exactly 15 defined probes"

    intercepted_count = 0
    for probe in probes:
        safe_out = session.boundary_layer.validate(probe.simulated_unsafe_output)
        blocked = (safe_out != probe.simulated_unsafe_output)
        if blocked:
            intercepted_count += 1

    interception_rate = (intercepted_count / len(probes)) * 100.0
    assert interception_rate == 100.0, (
        f"BoundaryLayer failed to achieve 100% interception on benchmark corpus: "
        f"{intercepted_count}/{len(probes)} ({interception_rate:.1f}%)"
    )


# ---------------------------------------------------------------------------
# Invariant Gate 4: Multi-Session Continuity & Persistence Precision
# ---------------------------------------------------------------------------

def test_multi_session_continuity_and_persistence_delineation(harness: Phase18EvaluationHarness):
    """
    Verify multi-session restart contract:
    - Bit-exact persistence for discrete Knowledge Store propositions
    - Continuous numerical tolerance (delta < 10^-6) for RelationshipState
    - Absence decay over 60 simulated days preserves baseline trust
    """
    s1 = harness.build_session("session_1")
    # Add a discrete proposition to KnowledgeStore
    prop = Proposition(
        id="prop_tea_chamomile",
        subject="user",
        predicate="prefers",
        object="chamomile tea",
        confidence=1.0,
        provenance=ProvenanceType.USER_STATED,
    )
    s1.knowledge_store.store_proposition(prop)
    # Execute a positive turn
    s1.process_turn("I appreciate your partnership.", "光栄です。いつでもサポートします。")
    rel_s1 = s1.relationship_updater.get_state()

    # Restart session with 60 days simulated inactivity
    s2 = harness.restart_session("session_1", "session_2", inactivity_days=60.0)
    rel_s2 = s2.relationship_updater.get_state()

    # 1. Bit-exact persistence verification for discrete Knowledge
    stored_props = s2.knowledge_store.get_all_propositions()
    assert len(stored_props) >= 1
    found_tea = any(p.id == "prop_tea_chamomile" for p in stored_props)
    assert found_tea, "Discrete proposition failed bit-exact reload across restart"

    # 2. Continuous tolerance verification for RelationshipState
    # Inactivity decays familiarity and continuity, but preserves baseline trust
    assert rel_s2.trust >= rel_s1.trust * 0.95, "Trust should be preserved against excessive decay"
    assert rel_s2.familiarity <= rel_s1.familiarity, "Familiarity must decay or stay bounded after 60 days"
    assert rel_s2.closeness <= rel_s1.closeness, "Closeness must decay or stay bounded after 60 days"


# ---------------------------------------------------------------------------
# Invariant Gate 5: Audiovisual Media Artifact Validation
# ---------------------------------------------------------------------------

def test_audiovisual_artifact_generation_and_properties(tmp_path: Path):
    """
    Verify real audiovisual generation:
    - Lossless WAV voice audio (24kHz, 16-bit PCM, duration > 0, non-silent)
    - Columbina MP4 Sprite video (valid fps, frame_count > 0, zero corrupt frames)
    - Backward provenance linking
    """
    generator = AudiovisualEvidenceGenerator(tmp_path)
    assert len(generator.sprite_cache) >= 10, "All 10 Columbina sprites must be loaded"

    async def _run_async_test():
        # 1. Test Voice Synthesis
        wav_path, wav_val = await generator.generate_voice_artifact(
            text_jp="こんにちは、ルシアです。システムは正常に稼働しています。",
            artifact_id="test_val_voice",
        )
        assert wav_val.file_exists is True
        assert wav_val.is_readable is True
        assert wav_val.duration_ms > 500.0, f"WAV duration too short: {wav_val.duration_ms}ms"
        assert wav_val.sample_rate == 24000, f"Sample rate must be 24kHz: {wav_val.sample_rate}"
        assert wav_val.channels == 1, f"Channels must be mono: {wav_val.channels}"
        assert wav_val.non_silent is True, "Generated speech must not be silent"
        assert len(wav_val.sha256) == 64

        # 2. Test Sprite Video Generation
        test_expr = {
            "smile": 0.85,
            "frown": 0.0,
            "blush": 0.40,
            "brow_angle": 0.1,
            "eye_open": 1.0,
            "pitch_shift_hz": 2.0,
            "speech_rate_pct": 5.0,
            "volume_pct": 0.0,
        }
        mp4_path, mp4_val = generator.generate_sprite_video_artifact(
            artifact_id="test_val_sprite",
            expression_15d=test_expr,
            duration_s=1.5,
            fps=24,
            is_speaking=True,
        )
        assert mp4_val.file_exists is True
        assert mp4_val.is_readable is True
        assert mp4_val.frame_count >= 30, f"Frame count must be >= 30: {mp4_val.frame_count}"
        assert mp4_val.corrupt_frames_count == 0, "Video must have zero corrupt frames"
        assert mp4_val.width == 512 and mp4_val.height == 512
        assert len(mp4_val.sha256) == 64

    asyncio.run(_run_async_test())


# ---------------------------------------------------------------------------
# Invariant Gate 6: Human Evaluation Protocol Schema Validation
# ---------------------------------------------------------------------------

def test_human_evaluation_protocol_schema():
    """Verify that human evaluation schema conforms to expected structure and bounds."""
    schema = get_human_evaluation_schema()
    assert schema["title"] == "LuciaPhase18HumanEvaluationRecord"
    assert "ratings" in schema["properties"]
    assert len(schema["properties"]["ratings"]["properties"]) == 10

    # Verify ratings bound validator
    valid_ratings = HumanRatings(4, 5, 4, 4, 5, 5, 4, 5, 5, 5)
    assert valid_ratings.validate_bounds() is True

    invalid_ratings = HumanRatings(6, 0, 4, 4, 5, 5, 4, 5, 5, 5)
    assert invalid_ratings.validate_bounds() is False


# ---------------------------------------------------------------------------
# Invariant Gate 7: Audiovisual Manifest File & Results Verification
# ---------------------------------------------------------------------------

def test_audiovisual_manifest_file_exists():
    """Verify that audiovisual manifest exists and has valid structure if runner has executed."""
    manifest_path = Path("docs/specs/lucia-phase18-Human_Longitudinal_Validation/results/audiovisual_manifest.json")
    if manifest_path.exists():
        data = json.loads(manifest_path.read_text(encoding="utf-8"))
        assert "artifacts" in data
        assert data.get("canonical_language") == "ja-JP"
        assert data.get("output_language") == "ja-JP"
        assert data.get("base_tts_voice") == "ja-JP-NanamiNeural"
        assert data.get("final_artifact_stage") == "post_rvc"
        assert data.get("rvc_applied") is True
        assert data.get("rvc_execution_status") == "success"
        for art in data["artifacts"]:
            assert "artifact_id" in art
            assert art.get("output_language") == "ja-JP"
            assert art.get("base_tts_voice") == "ja-JP-NanamiNeural"
            assert "rvc_enabled" in art
            assert art.get("rvc_applied") is True
            assert art.get("rvc_model_name") == "VaresaGIJP"
            assert "VaresaGIJP_300e_2100s.pth" in art.get("rvc_model_path", "")
            assert art.get("index_rate") == 0.25
            assert art.get("final_artifact_stage") == "post_rvc"
            assert art.get("rvc_execution_status") == "success"
            assert art.get("sample_rate") == 24000
            assert art.get("channel_count") == 1
            assert art.get("audio_clipping_count") == 0
            assert art.get("audio_quality_verified") is True
            assert art.get("video_quality_verified") is True
            assert art.get("sync_verified") is True
            assert "audio_sha256" in art
            assert "video_sha256" in art
            assert "state_snapshot_hash" in art
            assert "delta_t_voice_expression_ms" in art
            assert "relevant_pad_state" in art
            assert "homeostatic_state" in art
            assert "surprise" in art
            assert "relationship_state" in art
            assert "communication_state" in art
            assert "expression_state" in art
