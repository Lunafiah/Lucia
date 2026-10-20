"""
tests/unit/test_p23d_condition.py

Unit test suite for Phase 23-D UnresolvedCondition primitive.
Verifies TEST-P23D-COND-001 through TEST-P23D-COND-003.

Authoritative Reference:
- docs/others/p23d_endogenous_cognition/P23D_IMPLEMENTATION_SPEC_V1.md §10.1
"""

import dataclasses
import hashlib
import pytest

from src.core.cognition.contract.condition import (
    ConditionStatus,
    ConditionType,
    ResolutionSource,
    UnresolvedCondition,
)
from src.core.cognition.referent_adapter import compute_condition_id, encode_referent_key


class TestP23DCondition:
    def test_cond_001_instantiation_and_deterministic_id(self):
        """
        TEST-P23D-COND-001: Instantiation and deterministic ID computation.
        Given identical type and referent key, condition_id is bit-exact SHA-256 digest.
        Exactly 6 fields exist.
        """
        referent_key = encode_referent_key("scope:root", "ent:lucia", "c:knows", "ent:user")
        cond_id = compute_condition_id(ConditionType.MISSING_PREMISE, referent_key)

        expected_id = hashlib.sha256(
            f"{ConditionType.MISSING_PREMISE.value}:{referent_key}".encode("utf-8")
        ).hexdigest()

        assert cond_id == expected_id

        cond = UnresolvedCondition(
            condition_id=cond_id,
            condition_type=ConditionType.MISSING_PREMISE,
            referent_key=referent_key,
            status=ConditionStatus.ACTIVE,
            resolution_source=ResolutionSource.INTERNAL_SEARCH,
            epoch_created=1,
        )

        # Assert exactly 6 fields exist in dataclass
        fields = dataclasses.fields(cond)
        assert len(fields) == 6
        field_names = {f.name for f in fields}
        expected_names = {
            "condition_id",
            "condition_type",
            "referent_key",
            "status",
            "resolution_source",
            "epoch_created",
        }
        assert field_names == expected_names

        # Verify serialization round-trip
        data = cond.to_dict()
        assert data["condition_id"] == cond_id
        assert data["condition_type"] == "MISSING_PREMISE"
        assert data["status"] == "ACTIVE"
        assert data["resolution_source"] == "INTERNAL_SEARCH"
        assert data["epoch_created"] == 1

        restored = UnresolvedCondition.from_dict(data)
        assert restored == cond

    def test_cond_002_immutability_and_copy_on_write(self):
        """
        TEST-P23D-COND-002: Immutability and copy-on-write transition.
        Direct attribute assignment raises FrozenInstanceError.
        transition_to() returns fresh instance.
        """
        referent_key = encode_referent_key("scope:root", "ent:agent", "c:believes", "true")
        cond_id = compute_condition_id(ConditionType.CONTRADICTION, referent_key)

        cond = UnresolvedCondition(
            condition_id=cond_id,
            condition_type=ConditionType.CONTRADICTION,
            referent_key=referent_key,
            status=ConditionStatus.ACTIVE,
            resolution_source=ResolutionSource.INTERNAL_SEARCH,
            epoch_created=1,
        )

        # Assert frozen / immutable
        with pytest.raises(dataclasses.FrozenInstanceError):
            cond.status = ConditionStatus.RESOLVED  # type: ignore

        with pytest.raises(dataclasses.FrozenInstanceError):
            cond.condition_id = "modified_id"  # type: ignore

        # Copy-on-write transition
        transitioned = cond.transition_to(ConditionStatus.RESOLVED)
        assert transitioned is not cond
        assert cond.status == ConditionStatus.ACTIVE  # original remains unchanged
        assert transitioned.status == ConditionStatus.RESOLVED
        assert transitioned.condition_id == cond.condition_id
        assert transitioned.referent_key == cond.referent_key

        # Forbidden transitions
        # RESOLVED -> ACTIVE is forbidden
        with pytest.raises(ValueError, match="Illegal lifecycle transition"):
            transitioned.transition_to(ConditionStatus.ACTIVE)

        # SUPPRESSED -> ACTIVE is forbidden
        suppressed = cond.transition_to(ConditionStatus.SUPPRESSED)
        with pytest.raises(ValueError, match="Illegal lifecycle transition"):
            suppressed.transition_to(ConditionStatus.ACTIVE)

        # SUPPRESSED -> DEFERRED is permitted
        deferred = suppressed.transition_to(ConditionStatus.DEFERRED)
        assert deferred.status == ConditionStatus.DEFERRED

    def test_cond_003_deserialization_validation(self):
        """
        TEST-P23D-COND-003: Deserialization validation of malformed records.
        Missing fields or invalid enum strings raise ValueError. Corrupted records fail-closed.
        """
        valid_dict = {
            "condition_id": compute_condition_id(ConditionType.MISSING_PREMISE, "[\"scope:root\",\"ent:a\",\"c:p\",\"ent:b\"]"),
            "condition_type": "MISSING_PREMISE",
            "referent_key": "[\"scope:root\",\"ent:a\",\"c:p\",\"ent:b\"]",
            "status": "ACTIVE",
            "resolution_source": "INTERNAL_SEARCH",
            "epoch_created": 2,
        }

        # 1. Missing mandatory field raises ValueError
        for key in valid_dict.keys():
            incomplete = dict(valid_dict)
            del incomplete[key]
            with pytest.raises(ValueError, match=f"Missing required fields for UnresolvedCondition: .*{key}"):
                UnresolvedCondition.from_dict(incomplete)

        # 2. Invalid condition_type enum raises ValueError
        bad_type = dict(valid_dict, condition_type="INVALID_TYPE")
        with pytest.raises(ValueError, match="Invalid condition_type"):
            UnresolvedCondition.from_dict(bad_type)

        # 3. Invalid status enum raises ValueError
        bad_status = dict(valid_dict, status="UNKNOWN_STATUS")
        with pytest.raises(ValueError, match="Invalid status"):
            UnresolvedCondition.from_dict(bad_status)

        # 4. Invalid resolution_source enum raises ValueError
        bad_source = dict(valid_dict, resolution_source="INVALID_SOURCE")
        with pytest.raises(ValueError, match="Invalid resolution_source"):
            UnresolvedCondition.from_dict(bad_source)
