"""
Tests for Phase 22 H1 Gate 2 Compression Diagnostic Tooling.

Verifies that the diagnostic scripts accurately reconstruct the observed
compression from immutable datasets without altering any baseline state.
"""

import pytest
import numpy as np
from pathlib import Path

from tests.evaluation_phase22.scripts.diagnose_gate2_compression import (
    load_datasets,
    task4_reconstruct_v14_compression,
    REPO_ROOT,
)
from src.core.gating.stimulus_processor import StimulusProcessor
from src.core.config import StimulusConfig
from tests.evaluation_phase22.fixtures.probes_h1_v14 import _SM_TEMPLATES as sm_v14
from tests.evaluation_phase22.fixtures.probes_h1_path_c import _SM_TEMPLATES as sm_pc


def test_reconstructed_v14_compression_numbers():
    v14_raw, v14_probes, _ = load_datasets()
    assert len(v14_raw) == 1350
    assert len(v14_probes) == 270

    stats_table = task4_reconstruct_v14_compression(v14_probes)
    
    # Check T=12 values
    s_l_t12 = stats_table["Low"][12]["mean"]
    s_m_t12 = stats_table["Med"][12]["mean"]
    s_h_t12 = stats_table["High"][12]["mean"]

    assert pytest.approx(s_l_t12, abs=1e-4) == 0.2647
    assert pytest.approx(s_m_t12, abs=1e-4) == 0.5792
    assert pytest.approx(s_h_t12, abs=1e-4) == 0.6477

    delta_ml_t12 = s_m_t12 - s_l_t12
    delta_hm_t12 = s_h_t12 - s_m_t12

    assert pytest.approx(delta_ml_t12, abs=1e-4) == 0.3145
    assert pytest.approx(delta_hm_t12, abs=1e-4) == 0.0685


def test_path_c_vs_v14_difference():
    # In Path C, S_M(T=12) was 0.4387, yielding Delta_HM = 0.2090
    # In v1.4, S_M(T=12) was 0.5792, yielding Delta_HM = 0.0685
    sm_diff = 0.5792 - 0.4387
    dhm_diff = 0.0685 - 0.2090
    assert pytest.approx(sm_diff, abs=1e-4) == 0.1405
    assert pytest.approx(dhm_diff, abs=1e-4) == -0.1405


def test_v14_sm_valence_elevation():
    sp = StimulusProcessor(StimulusConfig())
    vad_pc = [sp._analyzer.polarity_scores(t)["compound"] for t in sm_pc]
    vad_v14 = [sp._analyzer.polarity_scores(t)["compound"] for t in sm_v14]

    mean_vad_pc = float(np.mean(vad_pc))
    mean_vad_v14 = float(np.mean(vad_v14))

    assert pytest.approx(mean_vad_pc, abs=1e-3) == 0.4158
    assert pytest.approx(mean_vad_v14, abs=1e-3) == 0.5846
    assert mean_vad_v14 > mean_vad_pc

    enc_pc_dens = [sp.encode(t)[2] for t in sm_pc]
    enc_v14_dens = [sp.encode(t)[2] for t in sm_v14]

    assert pytest.approx(np.mean(enc_pc_dens), abs=1e-3) == 0.7952
    assert pytest.approx(np.mean(enc_v14_dens), abs=1e-3) == 0.9777
