"""
tests/unit/test_p23d_persistence.py

Unit test suite for Phase 23-D Condition Persistence authority and crash-safety.
Verifies TEST-P23D-PERS-001 and TEST-P23D-PERS-002.

Authoritative Reference:
- docs/others/p23d_endogenous_cognition/P23D_IMPLEMENTATION_SPEC_V1.md §10.1
"""

import json
from pathlib import Path
import pytest

from src.core.cognition.condition_persistence import load_conditions, save_conditions
from src.core.cognition.contract.condition import (
    ConditionStatus,
    ConditionType,
    ResolutionSource,
    UnresolvedCondition,
)
from src.core.cognition.referent_adapter import compute_condition_id


@pytest.fixture
def temp_conditions_file(tmp_path: Path) -> Path:
    return tmp_path / "cognitive_conditions.json"


class TestP23DPersistence:
    def test_pers_001_atomic_persistence_and_backup_creation(self, temp_conditions_file: Path):
        """
        TEST-P23D-PERS-001: Atomic persistence and backup creation.
        save_conditions() writes .tmp then replaces target. Existing target is preserved in .json.bak.
        """
        cond_id = compute_condition_id(ConditionType.MISSING_PREMISE, "[\"scope:root\",\"ent:lucia\",\"c:has\",\"ent:voice\"]")
        c1 = UnresolvedCondition(
            condition_id=cond_id,
            condition_type=ConditionType.MISSING_PREMISE,
            referent_key="[\"scope:root\",\"ent:lucia\",\"c:has\",\"ent:voice\"]",
            status=ConditionStatus.ACTIVE,
            resolution_source=ResolutionSource.INTERNAL_SEARCH,
            epoch_created=1,
        )

        # 1. First save: creates target file
        saved_path = save_conditions([c1], temp_conditions_file)
        assert saved_path == temp_conditions_file
        assert temp_conditions_file.exists()

        # Temporary file should not remain
        tmp_file = temp_conditions_file.with_suffix(".json.tmp")
        assert not tmp_file.exists()

        loaded = load_conditions(temp_conditions_file)
        assert len(loaded) == 1
        assert loaded[0] == c1

        # 2. Second save with modification: existing target must be copied to .json.bak
        c2 = c1.transition_to(ConditionStatus.RESOLVED)
        saved_path2 = save_conditions([c2], temp_conditions_file)
        assert saved_path2 == temp_conditions_file

        bak_file = temp_conditions_file.with_suffix(".json.bak")
        assert bak_file.exists()

        # Check backup content contains previous version (ACTIVE)
        with open(bak_file, "r", encoding="utf-8") as f:
            bak_data = json.load(f)
        assert len(bak_data["conditions"]) == 1
        assert bak_data["conditions"][0]["status"] == "ACTIVE"

        # Check primary content contains current version (RESOLVED)
        loaded2 = load_conditions(temp_conditions_file)
        assert len(loaded2) == 1
        assert loaded2[0].status == ConditionStatus.RESOLVED

    def test_pers_002_crash_safe_recovery_and_fallback_order(self, temp_conditions_file: Path):
        """
        TEST-P23D-PERS-002: Crash-safe recovery and fallback order.
        Corrupting primary file triggers automatic fallback to .json.bak.
        Corrupting both triggers .corrupt quarantine and returns [].
        """
        cond_id_orig = compute_condition_id(ConditionType.CONTRADICTION, "[\"scope:root\",\"ent:a\",\"c:rel\",\"ent:b\"]")
        c_orig = UnresolvedCondition(
            condition_id=cond_id_orig,
            condition_type=ConditionType.CONTRADICTION,
            referent_key="[\"scope:root\",\"ent:a\",\"c:rel\",\"ent:b\"]",
            status=ConditionStatus.DEFERRED,
            resolution_source=ResolutionSource.INTERNAL_SEARCH,
            epoch_created=2,
        )

        # Save twice to establish primary and .bak
        save_conditions([c_orig], temp_conditions_file)
        c_mod = c_orig.transition_to(ConditionStatus.ACTIVE)
        save_conditions([c_mod], temp_conditions_file)

        bak_file = temp_conditions_file.with_suffix(".json.bak")
        assert temp_conditions_file.exists()
        assert bak_file.exists()

        # Case A: Corrupt primary file with invalid syntax
        with open(temp_conditions_file, "w", encoding="utf-8") as f:
            f.write("CORRUPTED_PRIMARY_NOT_VALID_JSON{[[{")

        # Loading must gracefully recover from .bak
        recovered = load_conditions(temp_conditions_file)
        assert len(recovered) == 1
        assert recovered[0].condition_id == cond_id_orig
        assert recovered[0].status == ConditionStatus.DEFERRED

        # Case B: Corrupt backup as well
        with open(bak_file, "w", encoding="utf-8") as f:
            f.write("CORRUPTED_BACKUP_NOT_VALID_JSON")

        # Loading must trigger fail-closed quarantine and return []
        quarantined_results = load_conditions(temp_conditions_file)
        assert quarantined_results == []

        # Verify .corrupt file exists
        corrupt_files = list(temp_conditions_file.parent.glob("cognitive_conditions.corrupt_*.json"))
        assert len(corrupt_files) >= 1
