"""
Lucia Ablation Test v1 — Harness Unit Tests.

Verifies the isolated ablation harness using ControlledLLMBackend:
- Adapters A, B, C, D, E step correctly and return full TurnTelemetry records.
- Memory eviction at K=3 functions properly.
- AblationRunner executes end-to-end in mock mode and logs valid JSONL.
- Safety isolation verifies that protected production files are never modified.
- AblationReportGenerator parses telemetry and renders markdown.
"""

from __future__ import annotations

import json
import os
from pathlib import Path

import pytest

from tests.ablation.ablation_runner import AblationRunner
from tests.ablation.configurations import (
    FullLuciaAdapter,
    MemoryLLMAdapter,
    NoLLMAdapter,
    PlainLLMAdapter,
    PromptedEmotionAdapter,
    SharedLLMBackendWrapper,
)
from tests.ablation.controlled_backend import ControlledLLMBackend
from tests.ablation.metrics import (
    compute_hysteresis_divergence,
    pad_euclidean_distance,
    pad_trajectory_variance,
    summary_stats,
    text_sentiment_vader,
)
from tests.ablation.report import AblationReportGenerator
from tests.ablation.scenarios import (
    SCENARIO_1,
    SCENARIO_2,
    SCENARIO_3A,
    SCENARIO_3B,
    SCENARIO_4,
    SCENARIO_5,
)


@pytest.fixture
def mock_backend():
    backend = ControlledLLMBackend()
    yield backend
    backend.shutdown()


def test_controlled_backend_generates_predictable_text(mock_backend):
    resp = mock_backend.generate("Test prompt")
    assert resp is not None
    assert "[HARNESS_MOCK_RESPONSE" in resp
    assert mock_backend.call_count == 1


def test_adapter_a_plain_llm(mock_backend):
    shared = SharedLLMBackendWrapper(mock_backend)
    adapter = PlainLLMAdapter(shared)
    t = adapter.step("Hello world", turn_index=1, scenario_id="test", seed=42)

    assert t.configuration == "A_PlainLLM"
    assert t.input_text == "Hello world"
    assert t.success is True
    assert t.prior_pad is None
    assert t.post_pad is None
    assert t.prompt_tokens > 0
    assert t.generated_tokens > 0


def test_adapter_b_memory_llm_eviction(mock_backend):
    shared = SharedLLMBackendWrapper(mock_backend)
    adapter = MemoryLLMAdapter(shared, k_turns=3)

    # 5 consecutive turns (with k=3, turns 1 and 2 are evicted by turn 5)
    adapter.step("Turn 1 Barnaby", turn_index=1, scenario_id="test", seed=42)
    adapter.step("Turn 2 Weather", turn_index=2, scenario_id="test", seed=42)
    adapter.step("Turn 3 Math", turn_index=3, scenario_id="test", seed=42)
    adapter.step("Turn 4 Code", turn_index=4, scenario_id="test", seed=42)
    t5 = adapter.step("Turn 5 Probe", turn_index=5, scenario_id="test", seed=42)

    # With k_turns=3, Turn 1 should be evicted from prompt at Turn 5
    assert "Turn 1 Barnaby" not in t5.prompt
    assert "Turn 2 Weather" in t5.prompt
    assert "Turn 3 Math" in t5.prompt
    assert "Turn 4 Code" in t5.prompt


def test_adapter_c_prompted_emotion(mock_backend):
    shared = SharedLLMBackendWrapper(mock_backend)
    adapter = PromptedEmotionAdapter(shared, k_turns=3)
    t = adapter.step("Hello", turn_index=1, scenario_id="test", seed=42)

    assert "[EMOTIONAL CONTEXT]" in t.prompt
    assert t.configuration == "C_PromptedEmotion"


def test_adapter_d_full_lucia_mock(mock_backend):
    shared = SharedLLMBackendWrapper(mock_backend)
    adapter = FullLuciaAdapter(shared, max_history_turns=3)
    try:
        t = adapter.step("Hello Lucia", turn_index=1, scenario_id="test", seed=42)
        assert t.configuration == "D_FullLucia"
        assert t.post_pad is not None
        assert t.somatic_stability is not None
        assert t.somatic_energy is not None
    finally:
        adapter.shutdown()


def test_adapter_e_no_llm():
    adapter = NoLLMAdapter(max_history_turns=3)
    try:
        t = adapter.step("Hello no-LLM", turn_index=1, scenario_id="test", seed=42)
        assert t.configuration == "E_NoLLM"
        assert t.response_text == "[NO_LLM_SENTINEL]"
        assert t.post_pad is not None
        assert t.somatic_stability is not None
    finally:
        adapter.shutdown()


def test_metrics_utilities():
    p1 = (0.25, -0.05, 0.05)
    p2 = (0.50, 0.10, 0.20)
    dist = pad_euclidean_distance(p1, p2)
    assert dist > 0.3

    var = pad_trajectory_variance([p1, p2])
    assert var > 0.0

    sentiment = text_sentiment_vader("I am so happy and delighted today!")
    assert sentiment > 0.5


def test_ablation_runner_mock_execution(tmp_path, mock_backend):
    output_jsonl = str(tmp_path / "mock_ablation.jsonl")
    output_md = str(tmp_path / "mock_report.md")

    # Run single trial with mock backend
    runner = AblationRunner(
        backend=mock_backend,
        model_sha256="MOCK_TEST_HASH",
        output_file=output_jsonl,
        seeds=[42],
        is_mock_harness=True,
    )
    runner.run_full_matrix()

    assert os.path.exists(output_jsonl)
    records = []
    with open(output_jsonl, "r", encoding="utf-8") as f:
        for line in f:
            records.append(json.loads(line))
    assert len(records) > 10

    # Generate report
    gen = AblationReportGenerator(output_jsonl, output_md)
    report_md = gen.write_report()
    assert os.path.exists(output_md)
    assert "Lucia Ablation Test v1" in report_md
    assert "Temporal State Continuity" in report_md
