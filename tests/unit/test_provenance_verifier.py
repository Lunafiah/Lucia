"""
Unit Tests for WP-03: Workspace Provenance & Environment Verification.

Governing ADR: ADR-034 (ARCH-034: Identity Authority, Instance Exclusivity & Anti-Branching Boundary).
Reference Specification: docs/others/IDENTITY_AUTHORITY_SPECIFICATION/IDENTITY_AUTHORITY_SPEC_V01.md
Reference Plan: docs/others/IDENTITY_AUTHORITY_SPECIFICATION/IMPLEMENTATION_PLAN.md

Tests cover:
- T01: Normal provenance verification (matching workspace & hardware -> VALID).
- T02: Workspace location divergence detection (copied directory -> WORKSPACE_DIVERGENCE).
- T03: Hardware environment divergence detection without reconfirmation -> AWAITING_HARDWARE_RECONFIRMATION.
- T04: Recovery-gated reconfirmation workflow (user confirms -> updates digest, increments migration epoch, preserves anchor).
- T05: Recovery-gated reconfirmation aborted (user cancels -> no disk mutation).
- T06: Legitimate software/model upgrade (phylogenetic update -> passes verification, no identity change).
- T07: Ordinary wall-clock rollback detection (clock regression -> WALL_CLOCK_ROLLBACK_DETECTED).
- T08: Epistemic honesty & threat classifications (Snapshot/VM rollback is UNSOLVED; no absolute anti-cloning).
- T09: Genesis invariant preservation (un-onboarded profile -> GENESIS_LOCKED, zero writes).
- T10: Non-destructive failure guarantee (data/ files untouched on all divergence and error conditions).
- T11: Hardware components collection & stable digest derivation.
- T12: Solemn High-Gravity Identity Notice formatting.
"""

from __future__ import annotations

import copy
from datetime import datetime, timezone
import json
from pathlib import Path
from typing import Any, Dict

import pytest

from src.core.identity.identity_anchor import (
    CANONICAL_SCHEMA_VERSION,
    apply_phylogenetic_upgrade,
    guard_immutable_fields,
)
from src.core.identity.provenance_verifier import (
    AuthorityBinding,
    HardwareDigestComponents,
    ProvenanceVerificationResult,
    ProvenanceVerificationStatus,
    ThreatClassification,
    are_workspace_paths_equal,
    check_wall_clock_monotonicity,
    collect_hardware_components,
    compute_component_digests,
    compute_hardware_digest,
    format_high_gravity_hardware_notice,
    normalize_workspace_path,
    reconfirm_hardware_environment,
    verify_provenance_and_environment,
)

SAMPLE_UUID = "3fa85f64-5717-4562-b3fc-2c963f66afa6"
SAMPLE_BORN_AT = "2026-10-01T00:00:00.000000Z"
SAMPLE_COMMIT = "ce106a245890abcdef1234567890abcdef123456"
SAMPLE_ROOT_HASH = "e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855"

MOCK_HW_1 = HardwareDigestComponents(
    machine_guid="guid-host-alpha-0001",
    smbios_uuid="smbios-host-alpha-0001",
    volume_serial="vol-alpha-0001",
    cpu_info="AMD Ryzen 9|cores:16",
    platform_str="Windows-11-Test-Alpha",
)

MOCK_HW_2 = HardwareDigestComponents(
    machine_guid="guid-host-beta-0002",
    smbios_uuid="smbios-host-beta-0002",
    volume_serial="vol-beta-0002",
    cpu_info="Intel Core i9|cores:24",
    platform_str="Windows-11-Test-Beta",
)


def create_sample_onboarded_profile(
    path: Path,
    workspace_path: Path,
    hw_components: HardwareDigestComponents = MOCK_HW_1,
    migration_epoch: int = 0,
    born_at: str = SAMPLE_BORN_AT,
) -> Dict[str, Any]:
    """Helper to generate a valid onboarded profile dictionary on disk."""
    hw_digest = compute_hardware_digest(hw_components)
    comp_digests = compute_component_digests(hw_components)

    data = {
        "schema_version": CANONICAL_SCHEMA_VERSION,
        "is_onboarded": True,
        "identity_anchor": {
            "instance_uuid": SAMPLE_UUID,
            "born_at": born_at,
            "genesis_commit": SAMPLE_COMMIT,
            "genesis_root_hash": SAMPLE_ROOT_HASH,
        },
        "phylogenetic_lineage": {
            "engine_version": "0.24.2",
            "last_upgraded_at": born_at,
            "compatible_schema_major": 2,
        },
        "authority_binding": {
            "hardware_binding_mode": "SOFT_WARNING",
            "bound_machine_guid_digest": hw_digest,
            "activation_host_platform": hw_components.platform_str,
            "last_known_canonical_path": normalize_workspace_path(workspace_path),
            "hardware_migration_epoch": migration_epoch,
            "last_verified_at": born_at,
            "component_digests": comp_digests,
        },
    }
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2)
    return data


class TestProvenanceVerifierUnit:
    """Unit test suite for WP-03 provenance and environment verification."""

    def test_t01_normal_provenance_verification(self, tmp_path: Path) -> None:
        """T01: Same workspace and matching hardware digest passes as VALID."""
        ws_path = tmp_path / "Lucia_Primary"
        ws_path.mkdir()
        profile_path = ws_path / "data" / "profile.json"
        profile_path.parent.mkdir()

        create_sample_onboarded_profile(profile_path, ws_path, hw_components=MOCK_HW_1)

        result = verify_provenance_and_environment(
            workspace_path=ws_path,
            profile_path=profile_path,
            hardware_components_override=MOCK_HW_1,
        )

        assert result.status == ProvenanceVerificationStatus.VALID
        assert result.is_valid is True
        assert result.is_genesis_locked is False
        assert result.hardware_matched is True
        assert result.workspace_matched is True
        assert result.clock_monotonic is True
        assert result.divergence_details is None

    def test_t02_workspace_location_divergence(self, tmp_path: Path) -> None:
        """T02: Folder copy on same machine triggers WORKSPACE_DIVERGENCE notice."""
        ws_primary = tmp_path / "Lucia_Primary"
        ws_primary.mkdir()
        ws_copied = tmp_path / "Lucia_Copied"
        ws_copied.mkdir()

        profile_path = ws_copied / "data" / "profile.json"
        profile_path.parent.mkdir()

        # Recorded canonical path is ws_primary, but running in ws_copied
        create_sample_onboarded_profile(profile_path, ws_primary, hw_components=MOCK_HW_1)

        content_before = profile_path.read_text(encoding="utf-8")

        result = verify_provenance_and_environment(
            workspace_path=ws_copied,
            profile_path=profile_path,
            hardware_components_override=MOCK_HW_1,
        )

        assert result.status == ProvenanceVerificationStatus.WORKSPACE_DIVERGENCE
        assert result.is_valid is False
        assert result.workspace_matched is False
        assert result.hardware_matched is True
        assert "Workspace path diverged" in str(result.divergence_details)
        # Verify classification is Detected / High-Friction
        assert result.threat_classifications["Copied Workspace"] == ThreatClassification.DETECTED_HIGH_FRICTION.value
        # Fail-safe: profile remains bit-exact and untouched
        assert profile_path.read_text(encoding="utf-8") == content_before

    def test_t03_hardware_digest_mismatch_without_reconfirmation(self, tmp_path: Path) -> None:
        """T03: Different hardware digest without reconfirmation enters AWAITING_HARDWARE_RECONFIRMATION."""
        ws_path = tmp_path / "Lucia"
        ws_path.mkdir()
        profile_path = ws_path / "data" / "profile.json"
        profile_path.parent.mkdir()

        # Bound to MOCK_HW_1, but executing under MOCK_HW_2
        create_sample_onboarded_profile(profile_path, ws_path, hw_components=MOCK_HW_1)
        content_before = profile_path.read_text(encoding="utf-8")

        result = verify_provenance_and_environment(
            workspace_path=ws_path,
            profile_path=profile_path,
            hardware_components_override=MOCK_HW_2,
            allow_reconfirmation=False,
        )

        assert result.status == ProvenanceVerificationStatus.AWAITING_HARDWARE_RECONFIRMATION
        assert result.is_valid is False
        assert result.hardware_matched is False
        assert "Awaiting owner reconfirmation" in str(result.divergence_details)
        assert result.threat_classifications["Authorized Hardware Replacement"] == ThreatClassification.DETECTED_RECOVERY_GATED.value
        # Fail-safe: zero writes
        assert profile_path.read_text(encoding="utf-8") == content_before

    def test_t04_recovery_gated_reconfirmation_success(self, tmp_path: Path) -> None:
        """T04: Explicit owner reconfirmation updates bound digest, increments epoch, preserves anchor."""
        ws_path = tmp_path / "Lucia"
        ws_path.mkdir()
        profile_path = ws_path / "data" / "profile.json"
        profile_path.parent.mkdir()

        create_sample_onboarded_profile(
            profile_path, ws_path, hw_components=MOCK_HW_1, migration_epoch=0
        )

        # Execute verification with allow_reconfirmation=True
        result = verify_provenance_and_environment(
            workspace_path=ws_path,
            profile_path=profile_path,
            hardware_components_override=MOCK_HW_2,
            allow_reconfirmation=True,
        )

        assert result.status == ProvenanceVerificationStatus.VALID
        assert result.is_valid is True
        assert result.hardware_matched is True

        # Inspect updated profile on disk
        with open(profile_path, "r", encoding="utf-8") as f:
            updated_data = json.load(f)

        auth = updated_data["authority_binding"]
        expected_digest_2 = compute_hardware_digest(MOCK_HW_2)
        assert auth["bound_machine_guid_digest"] == expected_digest_2
        assert auth["hardware_migration_epoch"] == 1
        assert auth["activation_host_platform"] == MOCK_HW_2.platform_str

        # CRITICAL: Identity Anchor must remain 100% bit-exact
        anchor = updated_data["identity_anchor"]
        assert anchor["instance_uuid"] == SAMPLE_UUID
        assert anchor["born_at"] == SAMPLE_BORN_AT
        assert anchor["genesis_commit"] == SAMPLE_COMMIT
        assert anchor["genesis_root_hash"] == SAMPLE_ROOT_HASH

    def test_t05_recovery_gated_reconfirmation_aborted(self, tmp_path: Path) -> None:
        """T05: When user aborts reconfirmation callback, system enters pause state with zero writes."""
        ws_path = tmp_path / "Lucia"
        ws_path.mkdir()
        profile_path = ws_path / "data" / "profile.json"
        profile_path.parent.mkdir()

        create_sample_onboarded_profile(profile_path, ws_path, hw_components=MOCK_HW_1)
        content_before = profile_path.read_text(encoding="utf-8")

        # Callback returns False (user selects [B] Cancel and close)
        result = verify_provenance_and_environment(
            workspace_path=ws_path,
            profile_path=profile_path,
            hardware_components_override=MOCK_HW_2,
            allow_reconfirmation=False,
            reconfirm_callback=lambda: False,
        )

        assert result.status == ProvenanceVerificationStatus.AWAITING_HARDWARE_RECONFIRMATION
        assert result.is_valid is False
        assert profile_path.read_text(encoding="utf-8") == content_before

    def test_t06_legitimate_software_model_upgrade_passes_provenance(self, tmp_path: Path) -> None:
        """T06: Normal engine/model upgrade does NOT invalidate provenance or trigger hardware mismatch."""
        ws_path = tmp_path / "Lucia"
        ws_path.mkdir()
        profile_path = ws_path / "data" / "profile.json"
        profile_path.parent.mkdir()

        profile_data = create_sample_onboarded_profile(
            profile_path, ws_path, hw_components=MOCK_HW_1
        )

        # Apply phylogenetic software upgrade (e.g. engine 0.24.2 -> 0.25.0)
        upgraded_profile = apply_phylogenetic_upgrade(
            profile_data,
            new_engine_version="0.25.0",
            last_upgraded_at="2026-10-02T00:00:00.000000Z",
        )
        with open(profile_path, "w", encoding="utf-8") as f:
            json.dump(upgraded_profile, f, indent=2)

        # Run provenance check: must succeed as VALID
        result = verify_provenance_and_environment(
            workspace_path=ws_path,
            profile_path=profile_path,
            hardware_components_override=MOCK_HW_1,
        )

        assert result.status == ProvenanceVerificationStatus.VALID
        assert result.is_valid is True
        assert result.hardware_matched is True
        assert result.workspace_matched is True

    def test_t07_ordinary_wall_clock_rollback_detected(self, tmp_path: Path) -> None:
        """T07: Ordinary system clock rollback is detected against profile and epoch timestamps."""
        ws_path = tmp_path / "Lucia"
        ws_path.mkdir()
        profile_path = ws_path / "data" / "profile.json"
        profile_path.parent.mkdir()

        # Recorded timestamp in 2026
        create_sample_onboarded_profile(
            profile_path, ws_path, hw_components=MOCK_HW_1, born_at="2026-10-07T07:36:33.123456Z"
        )

        # Simulated system wall clock set backwards to 2024
        past_clock = datetime(2024, 1, 1, 0, 0, 0, tzinfo=timezone.utc)

        result = verify_provenance_and_environment(
            workspace_path=ws_path,
            profile_path=profile_path,
            hardware_components_override=MOCK_HW_1,
            current_utc=past_clock,
        )

        assert result.status == ProvenanceVerificationStatus.WALL_CLOCK_ROLLBACK_DETECTED
        assert result.is_valid is False
        assert result.clock_monotonic is False
        assert "wall-clock rollback detected" in str(result.divergence_details)
        assert result.threat_classifications["Clock Rollback"] == (
            "Protected against ordinary wall-clock rollback; snapshot restoration remains unresolved"
        )

    def test_t08_epistemic_honesty_and_threat_classifications(self, tmp_path: Path) -> None:
        """T08: Epistemic honesty classifications are formally preserved as Unsolved."""
        ws_path = tmp_path / "Lucia"
        ws_path.mkdir()
        profile_path = ws_path / "data" / "profile.json"
        profile_path.parent.mkdir()

        create_sample_onboarded_profile(profile_path, ws_path, hw_components=MOCK_HW_1)

        result = verify_provenance_and_environment(
            workspace_path=ws_path,
            profile_path=profile_path,
            hardware_components_override=MOCK_HW_1,
        )

        threats = result.threat_classifications
        # Verify canonical classifications from ADR-034 §2.4
        assert threats["Same-Directory Dual Launch"] == ThreatClassification.PROTECTED.value
        assert threats["Copied Workspace"] == ThreatClassification.DETECTED_HIGH_FRICTION.value
        assert threats["Cross-Machine Unauthorized Copy"] == ThreatClassification.DETECTED_RECOVERY_GATED.value
        assert threats["Authorized Hardware Replacement"] == ThreatClassification.DETECTED_RECOVERY_GATED.value
        assert threats["Storage Snapshot / VM Rollback"] == ThreatClassification.UNSOLVED.value
        assert threats["Deliberate Offline Cloning"] == "Unsolved (Offline Clone Paradox)"

    def test_t09_pre_genesis_profile_invariant(self, tmp_path: Path) -> None:
        """T09: Pre-Genesis un-onboarded profile returns GENESIS_LOCKED without writing files."""
        ws_path = tmp_path / "Lucia"
        ws_path.mkdir()
        profile_path = ws_path / "data" / "profile.json"
        profile_path.parent.mkdir()

        raw_pre_genesis = '{"is_onboarded": false}'
        profile_path.write_text(raw_pre_genesis, encoding="utf-8")

        result = verify_provenance_and_environment(
            workspace_path=ws_path,
            profile_path=profile_path,
            hardware_components_override=MOCK_HW_1,
        )

        assert result.status == ProvenanceVerificationStatus.GENESIS_LOCKED
        assert result.is_valid is True
        assert result.is_genesis_locked is True
        # Verify file remains bit-exact
        assert profile_path.read_text(encoding="utf-8") == raw_pre_genesis

    def test_t10_non_destructive_failures_across_all_divergence_types(self, tmp_path: Path) -> None:
        """T10: Verifies that no verification failure causes destructive disk mutation."""
        ws_path = tmp_path / "Lucia"
        ws_path.mkdir()
        profile_path = ws_path / "data" / "profile.json"
        profile_path.parent.mkdir()

        create_sample_onboarded_profile(profile_path, ws_path, hw_components=MOCK_HW_1)
        original_bytes = profile_path.read_bytes()

        # 1. Hardware mismatch failure
        verify_provenance_and_environment(
            workspace_path=ws_path,
            profile_path=profile_path,
            hardware_components_override=MOCK_HW_2,
            allow_reconfirmation=False,
        )
        assert profile_path.read_bytes() == original_bytes

        # 2. Workspace divergence failure
        verify_provenance_and_environment(
            workspace_path=tmp_path / "Different_Folder",
            profile_path=profile_path,
            hardware_components_override=MOCK_HW_1,
        )
        assert profile_path.read_bytes() == original_bytes

        # 3. Clock rollback failure
        past = datetime(2020, 1, 1, 0, 0, 0, tzinfo=timezone.utc)
        verify_provenance_and_environment(
            workspace_path=ws_path,
            profile_path=profile_path,
            hardware_components_override=MOCK_HW_1,
            current_utc=past,
        )
        assert profile_path.read_bytes() == original_bytes

    def test_t11_hardware_components_collection_and_digest(self) -> None:
        """T11: Hardware components are successfully collected and digest is deterministic."""
        comps = collect_hardware_components()
        assert comps.machine_guid != ""
        assert comps.cpu_info != ""
        assert comps.platform_str != ""

        digest_a = compute_hardware_digest(comps)
        digest_b = compute_hardware_digest(comps)
        assert digest_a == digest_b
        assert len(digest_a) == 64

        comp_digests = compute_component_digests(comps)
        assert "machine_guid" in comp_digests
        assert "smbios_uuid" in comp_digests
        assert "volume_serial" in comp_digests
        assert "cpu_info" in comp_digests
        for d in comp_digests.values():
            assert len(d) == 64

    def test_t12_high_gravity_notice_formatting(self) -> None:
        """T12: Notice text adheres to Spec v0.1 §7.3."""
        notice = format_high_gravity_hardware_notice()
        assert "HIGH-GRAVITY IDENTITY NOTICE: HARDWARE DIVERGENCE DETECTED" in notice
        assert "[A] This is a legitimate hardware upgrade or disaster recovery." in notice
        assert "[B] Cancel and close" in notice
        assert "(INV-1)" in notice
