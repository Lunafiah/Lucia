"""
Unit tests for PromptAssembler Phase 2 extensions.

Requirements: 11.2–11.4, 12.1, 12.5, 16.3
"""

import re
from unittest.mock import patch

import numpy as np
import pytest

from src.core.errors import AssemblyError
from src.core.models import BehavioralConstraints, SomaticMarkers
from src.core.orchestrator.prompt_assembler import PromptAssembler


@pytest.fixture
def assembler():
    return PromptAssembler()


@pytest.fixture
def sample_markers():
    return SomaticMarkers(
        stability=0.8,
        cognitive_load=0.2,
        energy=0.9,
        tension=0.1,
    )


@pytest.fixture
def sample_constraints():
    return BehavioralConstraints(
        max_tokens=150,
        temperature=0.75,
        latency_ms=0,
        reasoning_depth=1,
    )


class TestPromptAssemblerPhase2:
    def test_echo_vector_none_omits_memory_echo_section(
        self, assembler, sample_markers, sample_constraints
    ):
        prompt = assembler.assemble(
            somatic=sample_markers,
            constraints=sample_constraints,
            history=[("user", "hi")],
            system_preamble="You are Lucia.",
            echo_vector=None,
        )
        assert not isinstance(prompt, AssemblyError)
        assert "[MEMORY ECHO]" not in prompt
        assert "echo_" not in prompt

    def test_echo_vector_included_between_somatic_and_reasoning(
        self, assembler, sample_markers, sample_constraints
    ):
        echo_vec = np.linspace(-1.0, 1.0, 64, dtype=np.float32)
        prompt = assembler.assemble(
            somatic=sample_markers,
            constraints=sample_constraints,
            history=[("user", "hello")],
            system_preamble="You are Lucia.",
            echo_vector=echo_vec,
        )
        assert not isinstance(prompt, AssemblyError)
        assert "[MEMORY ECHO]" in prompt

        # Verify section ordering
        pos_preamble = prompt.find("You are Lucia.")
        pos_somatic = prompt.find("[SOMATIC STATE]")
        pos_echo = prompt.find("[MEMORY ECHO]")
        pos_reasoning = prompt.find("[REASONING]")
        pos_conv = prompt.find("[CONVERSATION]")

        assert pos_preamble < pos_somatic < pos_echo < pos_reasoning < pos_conv

    def test_echo_vector_included_when_reasoning_omitted(
        self, assembler, sample_markers
    ):
        no_reasoning = BehavioralConstraints(
            max_tokens=150,
            temperature=0.75,
            latency_ms=0,
            reasoning_depth=0,
        )
        echo_vec = np.zeros(16, dtype=np.float32)
        prompt = assembler.assemble(
            somatic=sample_markers,
            constraints=no_reasoning,
            history=[("user", "hello")],
            echo_vector=echo_vec,
        )
        assert not isinstance(prompt, AssemblyError)
        pos_somatic = prompt.find("[SOMATIC STATE]")
        pos_echo = prompt.find("[MEMORY ECHO]")
        pos_conv = prompt.find("[CONVERSATION]")

        assert "[REASONING]" not in prompt
        assert pos_somatic < pos_echo < pos_conv

    def test_echo_lines_format(
        self, assembler, sample_markers, sample_constraints
    ):
        echo_vec = np.array([0.123456, -0.654321], dtype=np.float32)
        prompt = assembler.assemble(
            somatic=sample_markers,
            constraints=sample_constraints,
            history=[],
            echo_vector=echo_vec,
        )
        assert "echo_0: 0.123456" in prompt
        assert "echo_1: -0.654321" in prompt

        # Check regex match on all echo lines
        pattern = re.compile(r"^echo_\d+: -?\d+\.\d{6}$")
        echo_section = prompt.split("[MEMORY ECHO]")[1].split("---")[0].strip()
        lines = [line.strip() for line in echo_section.split("\n") if line.strip()]
        assert len(lines) == 2
        for line in lines:
            assert pattern.match(line), f"Line did not match regex: {line}"

    def test_echo_section_exact_dimension_count(
        self, assembler, sample_markers, sample_constraints
    ):
        echo_vec = np.zeros(64, dtype=np.float32)
        prompt = assembler.assemble(
            somatic=sample_markers,
            constraints=sample_constraints,
            history=[],
            echo_vector=echo_vec,
        )
        echo_section = prompt.split("[MEMORY ECHO]")[1].split("---")[0].strip()
        lines = [line.strip() for line in echo_section.split("\n") if line.strip()]
        assert len(lines) == 64

    def test_forbidden_recall_phrase_in_echo_raises_assembly_error(
        self, assembler
    ):
        # Directly test _encode_echo_section with mock/tampered output
        with patch.object(
            assembler,
            "_encode_echo_section",
            side_effect=AssemblyError("contains forbidden recall phrase"),
        ):
            res = assembler.assemble(
                somatic=SomaticMarkers(1, 0, 1, 0),
                constraints=BehavioralConstraints(100, 0.7, 0, 1),
                history=[],
                echo_vector=np.zeros(4),
            )
            assert isinstance(res, AssemblyError)
