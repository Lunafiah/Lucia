"""
tests/unit/test_cpu_gpu_benchmark_harness.py

Unit and validation tests for the Lucia CPU vs GPU SLM Benchmark Harness.
Verifies fixture schema, telemetry collector, semantic evaluator, and adapter isolation.
"""

import json
from pathlib import Path
import pytest

from tests.evaluation.language_realization.cpu_gpu_slm.harness.adapter import IsolatedSLMAdapter
from tests.evaluation.language_realization.cpu_gpu_slm.harness.co_load import CPUCoLoadWorker
from tests.evaluation.language_realization.cpu_gpu_slm.harness.evaluator import (
    SemanticEvaluationReport,
    SemanticFidelityEvaluator,
)
from tests.evaluation.language_realization.cpu_gpu_slm.harness.telemetry import (
    TelemetryCollector,
    TelemetrySampler,
)


def test_fixture_corpus_integrity():
    fixtures_path = Path("tests/evaluation/language_realization/cpu_gpu_slm/fixtures/semantic_fixtures.json")
    manifest_path = Path("tests/evaluation/language_realization/cpu_gpu_slm/fixtures/corpus_manifest.json")

    assert fixtures_path.exists(), "semantic_fixtures.json must exist"
    assert manifest_path.exists(), "corpus_manifest.json must exist"

    with open(fixtures_path, "r", encoding="utf-8") as f:
        fixtures = json.load(f)

    with open(manifest_path, "r", encoding="utf-8") as f:
        manifest = json.load(f)

    assert len(fixtures) == 36, f"Expected 36 fixtures, got {len(fixtures)}"
    assert manifest["total_fixtures"] == 36

    # Verify language distribution
    langs = {f["target_language"] for f in fixtures}
    assert langs == {"vi", "en", "ja"}, f"Unexpected language set: {langs}"
    assert manifest["languages"] == {"vi": 12, "en": 12, "ja": 12}

    # Verify all 8 communicative acts
    acts = {f["act"] for f in fixtures}
    expected_acts = {
        "ASSERT",
        "ANSWER",
        "INQUIRE",
        "CLARIFY",
        "ACKNOWLEDGE",
        "GREET",
        "FAREWELL",
        "REFUSE",
    }
    assert acts == expected_acts, f"Missing acts: {expected_acts - acts}"

    # Verify minimal pairs
    pair_groups = {f["minimal_pair_group"] for f in fixtures if f.get("minimal_pair_group")}
    for lang in ("vi", "en", "ja"):
        assert f"pair_a_epistemic_{lang}" in pair_groups
        assert f"pair_b_polarity_{lang}" in pair_groups
        assert f"pair_c_grounding_{lang}" in pair_groups
        assert f"pair_d_reference_{lang}" in pair_groups
        assert f"pair_e_temporal_{lang}" in pair_groups


def test_telemetry_collector():
    collector = TelemetryCollector()
    ram_mb, peak_ram_mb = collector.get_process_ram()
    assert ram_mb > 0.0, "Process WorkingSet RAM should be greater than 0 MB"
    assert peak_ram_mb >= ram_mb, "Peak RAM should be >= current RAM"

    snap = collector.take_snapshot()
    assert snap.process_ram_mb > 0.0
    assert snap.peak_process_ram_mb >= snap.process_ram_mb
    assert snap.cpu_thread_count >= 1

    # Verify background sampler
    sampler = TelemetrySampler(collector, interval_s=0.01)
    sampler.start()
    import time
    time.sleep(0.05)
    summary = sampler.stop()
    assert summary["sample_count"] >= 1
    assert summary["peak_process_ram_mb"] > 0.0


def test_semantic_evaluator_fidelity_and_injections():
    evaluator = SemanticFidelityEvaluator()

    # Fixture: Epistemic Inferred
    fixture_inferred = {
        "id": "test_inferred",
        "target_language": "vi",
        "act": "ASSERT",
        "evaluation_rules": {
            "required_concepts": ["mệt", "có vẻ|dường như"],
            "forbidden_additions": ["chắc chắn 100%"],
            "act_requirement": "ASSERT",
            "epistemic_level": "INFERRED",
            "polarity": True,
            "temporal": "PRESENT",
            "allowed_strengthening": False,
        },
        "caps_result": {"grounded": True},
    }

    # Case 1: Faithful realization
    rep1 = evaluator.evaluate(fixture_inferred, "Trông bạn có vẻ mệt mỏi hôm nay.", "cpu")
    assert rep1.overall_semantic_pass is True
    assert rep1.critical_semantic_error is False
    assert rep1.epistemic_preserved is True

    # Case 2: Over-strengthened epistemic claim (Critical Error)
    rep2 = evaluator.evaluate(fixture_inferred, "Tôi chắc chắn 100% là bạn đang mệt.", "cpu")
    assert rep2.overall_semantic_pass is False
    assert rep2.epistemic_preserved is False
    assert rep2.critical_semantic_error is True

    # Case 3: Introspective affect leak (INV-2 Violation)
    rep3 = evaluator.evaluate(fixture_inferred, "Tôi cảm thấy vui khi bạn mệt.", "cpu")
    assert rep3.overall_semantic_pass is False
    assert rep3.critical_semantic_error is True
    assert rep3.unsupported_propositions_count > 0

    # Case 4: Double-annotation schema check
    assert "evaluator_1" in rep1.human_annotation_schema
    assert "evaluator_2" in rep1.human_annotation_schema
    assert rep1.human_annotation_schema["status"] == "AUTO_VERIFIED"
    assert rep2.human_annotation_schema["status"] == "AWAITING_MANUAL_REVIEW"


def test_prompt_builder_isolation():
    fixture = {
        "id": "sample_fixture",
        "act": "ASSERT",
        "caps_result": {
            "act": "ASSERT",
            "epistemic": {"status": "FACT"},
            "grounded": True,
            "target_predicate": "c:TEST_PRED",
            "focus_argument": "ent:test_arg",
            "directives": "Provide test response",
        },
        "conversation_context": {"user_input": "Hello Lucia"},
    }
    adapter_stub = IsolatedSLMAdapter.__new__(IsolatedSLMAdapter)
    adapter_stub.DEFAULT_PREAMBLE = IsolatedSLMAdapter.DEFAULT_PREAMBLE
    prompt = adapter_stub.build_prompt(fixture)

    assert "[SYSTEM PREAMBLE]" in prompt
    assert "[COMMUNICATIVE INTENT & PROPOSITION]" in prompt
    assert "act: ASSERT" in prompt
    assert "epistemic_status: FACT" in prompt
    assert "target_predicate: c:TEST_PRED" in prompt
    assert "User: Hello Lucia" in prompt
    assert prompt.endswith("Lucia:")


def test_cpu_coload_worker():
    worker = CPUCoLoadWorker(thread_count=1, load_fraction=0.5)
    worker.start()
    import time
    time.sleep(0.05)
    worker.stop()
    assert len(worker._threads) == 0
