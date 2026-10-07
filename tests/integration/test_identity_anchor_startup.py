"""
Integration Tests for WP-02 Identity Anchor & Startup Lifecycle Ordering.

Governing ADR: ADR-034 (ARCH-034)
Reference: docs/others/IDENTITY_AUTHORITY_SPECIFICATION/IMPLEMENTATION_PLAN.md

Tests:
- T11: Invalid initialized anchor on startup causes server to fail closed (exit code 1, 'corrupted_identity_anchor').
- T12: WP-01 ordering: Instance authority check executes BEFORE identity anchor verification.
  If another process holds the lock, server fails closed with exit code 75 (WP-01) regardless
  of profile status.
- Pre-Genesis locked profile startup executes safely without generating an identity or writing to disk.
- Valid initialized anchor passes startup validation.
- Immutability guard via /profile route: Attempted mutation of immutable identity anchor fields
  via API is rejected with HTTP 400 Bad Request.
- Phylogenetic lineage update via /profile route succeeds while preserving immutable fields.
- INV-8 preservation: Real data/profile.json remains bit-exact across test executions.
"""

from __future__ import annotations

import json
import os
from pathlib import Path
import subprocess
import sys

import pytest
from starlette.testclient import TestClient

import src.api.server as api_server
from src.core.identity.identity_anchor import (
    CANONICAL_SCHEMA_VERSION,
    CorruptedIdentityAnchorError,
    InvalidIdentityAnchorError,
    guard_immutable_fields,
    verify_identity_on_startup,
)
from src.core.identity.instance_lock import InstanceLock
from src.core.identity.provenance_verifier import (
    collect_hardware_components,
    compute_hardware_digest,
    normalize_workspace_path,
)

SAMPLE_UUID = "3fa85f64-5717-4562-b3fc-2c963f66afa6"
SAMPLE_BORN_AT = "2026-10-01T00:00:00.000000Z"
SAMPLE_COMMIT = "ce106a245890abcdef1234567890abcdef123456"
SAMPLE_ROOT_HASH = "e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855"


def create_valid_profile_json(path: Path) -> None:
    ws = Path.cwd().resolve()
    comps = collect_hardware_components(ws)
    hw_digest = compute_hardware_digest(comps)
    data = {
        "schema_version": CANONICAL_SCHEMA_VERSION,
        "is_onboarded": True,
        "identity_anchor": {
            "instance_uuid": SAMPLE_UUID,
            "born_at": SAMPLE_BORN_AT,
            "genesis_commit": SAMPLE_COMMIT,
            "genesis_root_hash": SAMPLE_ROOT_HASH,
        },
        "phylogenetic_lineage": {
            "engine_version": "0.24.2",
            "last_upgraded_at": SAMPLE_BORN_AT,
            "compatible_schema_major": 2,
        },
        "authority_binding": {
            "hardware_binding_mode": "SOFT_WARNING",
            "bound_machine_guid_digest": hw_digest,
            "activation_host_platform": comps.platform_str,
            "last_known_canonical_path": normalize_workspace_path(ws),
            "hardware_migration_epoch": 0,
            "last_verified_at": SAMPLE_BORN_AT,
        },
        "user_name": "Friend",
        "companion_name": "Lucia",
    }
    path.write_text(json.dumps(data, indent=2), encoding="utf-8")


class TestIdentityAnchorStartupIntegration:
    """Integration test suite for identity anchor validation on startup and ordering with WP-01."""

    def test_t11_invalid_initialized_anchor_fails_closed_at_startup(self, tmp_path: Path):
        """T11: Corrupted or invalid initialized anchor at startup causes fail-closed exit(1)."""
        lock_file = tmp_path / ".instance.lock"
        corrupted_profile = tmp_path / "profile_corrupted.json"

        # Create an initialized profile with a corrupted UUID
        corrupted_data = {
            "schema_version": CANONICAL_SCHEMA_VERSION,
            "is_onboarded": True,
            "identity_anchor": {
                "instance_uuid": "invalid-corrupted-uuid",
                "born_at": SAMPLE_BORN_AT,
                "genesis_commit": SAMPLE_COMMIT,
                "genesis_root_hash": SAMPLE_ROOT_HASH,
            },
        }
        corrupted_profile.write_text(json.dumps(corrupted_data), encoding="utf-8")

        # Subprocess startup with the corrupted profile
        sub_code = f"""
import os, sys
from pathlib import Path
import src.api.server as srv

os.environ["LUCIA_LOCK_PATH"] = str(Path(r"{lock_file}"))
os.environ["LUCIA_PROFILE_PATH"] = str(Path(r"{corrupted_profile}"))

srv.init_server(
    model_path="dummy.gguf",
    port=8765,
    mode="live",
    lock_path=Path(r"{lock_file}"),
)
"""
        proc = subprocess.run(
            [sys.executable, "-c", sub_code],
            capture_output=True,
            text=True,
            cwd=os.getcwd(),
        )

        assert proc.returncode == 1, (
            f"Expected exit code 1 for corrupted identity anchor, got {proc.returncode}. "
            f"Stdout: {proc.stdout}, Stderr: {proc.stderr}"
        )
        assert "LUCIA_BACKEND_ERROR: corrupted_identity_anchor" in proc.stdout

    def test_t12_wp01_ordering_authority_before_identity_validation(self, tmp_path: Path):
        """
        T12: WP-01 ordering contract: OS kernel instance lock is acquired BEFORE identity verification.
        If instance lock is held by another process, server exits with code 75 ('instance_already_active')
        regardless of whether the profile is valid, invalid, or pre-Genesis.
        """
        lock_file = tmp_path / ".instance.lock"
        corrupted_profile = tmp_path / "profile_corrupted.json"

        # Write corrupted profile to prove lock check happens first
        corrupted_profile.write_text(
            json.dumps({"is_onboarded": True, "identity_anchor": {"instance_uuid": "bad"}}),
            encoding="utf-8",
        )

        # Process A holds the lock
        holder = InstanceLock(lock_path=lock_file)
        holder.acquire()

        try:
            # Process B attempts startup
            sub_code = f"""
import os, sys
from pathlib import Path
import src.api.server as srv

os.environ["LUCIA_LOCK_PATH"] = str(Path(r"{lock_file}"))
os.environ["LUCIA_PROFILE_PATH"] = str(Path(r"{corrupted_profile}"))

srv.init_server(
    model_path="dummy.gguf",
    port=8765,
    mode="live",
    lock_path=Path(r"{lock_file}"),
)
"""
            proc = subprocess.run(
                [sys.executable, "-c", sub_code],
                capture_output=True,
                text=True,
                cwd=os.getcwd(),
            )

            # Must fail with WP-01 exit code 75 (NOT WP-02 exit code 1)
            assert proc.returncode == 75, (
                f"Expected exit code 75 (lock conflict before identity check), got {proc.returncode}. "
                f"Stdout: {proc.stdout}, Stderr: {proc.stderr}"
            )
            assert "LUCIA_BACKEND_ERROR: instance_already_active" in proc.stdout

        finally:
            holder.release()

    def test_pre_genesis_profile_startup_succeeds_without_identity_creation(self, tmp_path: Path):
        """Pre-Genesis profile (is_onboarded=False) starts safely without identity synthesis."""
        lock_file = tmp_path / ".instance.lock"
        pre_genesis_profile = tmp_path / "profile.json"
        pre_genesis_profile.write_text(json.dumps({"is_onboarded": False}), encoding="utf-8")

        sub_code = f"""
import os, sys
from pathlib import Path
import src.api.server as srv

os.environ["LUCIA_LOCK_PATH"] = str(Path(r"{lock_file}"))
os.environ["LUCIA_PROFILE_PATH"] = str(Path(r"{pre_genesis_profile}"))

# Model path empty to trigger exit(1) after identity verification passes
srv.init_server(
    model_path="",
    port=8765,
    mode="live",
    lock_path=Path(r"{lock_file}"),
)
"""
        proc = subprocess.run(
            [sys.executable, "-c", sub_code],
            capture_output=True,
            text=True,
            cwd=os.getcwd(),
        )

        # It should exit with code 1 (model_path_not_configured) having passed the identity check!
        assert "LUCIA_BACKEND_ERROR: model_path_not_configured" in proc.stdout
        assert "LUCIA_BACKEND_ERROR: corrupted_identity_anchor" not in proc.stdout

        # Verify profile was untouched
        assert json.loads(pre_genesis_profile.read_text(encoding="utf-8")) == {"is_onboarded": False}

    def test_valid_initialized_profile_startup_succeeds(self, tmp_path: Path):
        """Valid initialized profile passes identity check and advances to subsequent stages."""
        lock_file = tmp_path / ".instance.lock"
        valid_profile = tmp_path / "profile.json"
        create_valid_profile_json(valid_profile)

        sub_code = f"""
import os, sys
from pathlib import Path
import src.api.server as srv

os.environ["LUCIA_LOCK_PATH"] = str(Path(r"{lock_file}"))
os.environ["LUCIA_PROFILE_PATH"] = str(Path(r"{valid_profile}"))

srv.init_server(
    model_path="",
    port=8765,
    mode="live",
    lock_path=Path(r"{lock_file}"),
)
"""
        proc = subprocess.run(
            [sys.executable, "-c", sub_code],
            capture_output=True,
            text=True,
            cwd=os.getcwd(),
        )

        # Passes identity check and halts at model_path_not_configured
        assert "LUCIA_BACKEND_ERROR: model_path_not_configured" in proc.stdout
        assert "LUCIA_BACKEND_ERROR: corrupted_identity_anchor" not in proc.stdout

    def test_profile_update_route_guards_immutable_fields(self, tmp_path: Path, monkeypatch):
        """HTTP POST /profile rejects mutation of immutable fields with 400 Bad Request."""
        profile_file = tmp_path / "profile.json"
        create_valid_profile_json(profile_file)

        # Redirect server profile file to temporary test fixture
        monkeypatch.setattr(api_server, "_PROFILE_FILE_PATH", profile_file)

        client = TestClient(api_server.app)

        # Attempt to mutate instance_uuid
        payload_corrupted_uuid = {
            "identity_anchor": {
                "instance_uuid": "4fa85f64-5717-4562-b3fc-2c963f66afa7",  # mutated
                "born_at": SAMPLE_BORN_AT,
                "genesis_commit": SAMPLE_COMMIT,
                "genesis_root_hash": SAMPLE_ROOT_HASH,
            }
        }
        res_uuid = client.post("/profile", json=payload_corrupted_uuid)
        assert res_uuid.status_code == 400
        assert "Immutable identity mutation rejected" in res_uuid.json()["detail"]

        # Attempt to mutate genesis_commit
        payload_corrupted_commit = {
            "identity_anchor": {
                "instance_uuid": SAMPLE_UUID,
                "born_at": SAMPLE_BORN_AT,
                "genesis_commit": "0000000000000000000000000000000000000000",  # mutated
                "genesis_root_hash": SAMPLE_ROOT_HASH,
            }
        }
        res_commit = client.post("/profile", json=payload_corrupted_commit)
        assert res_commit.status_code == 400

        # Successful update: Phylogenetic update and user name change
        payload_phylogenetic = {
            "user_name": "Companion-User",
            "phylogenetic_lineage": {
                "engine_version": "0.25.0",
                "last_upgraded_at": "2026-10-15T00:00:00Z",
                "compatible_schema_major": 2,
            },
        }
        res_phy = client.post("/profile", json=payload_phylogenetic)
        assert res_phy.status_code == 200
        assert res_phy.json()["profile"]["user_name"] == "Companion-User"
        assert res_phy.json()["profile"]["phylogenetic_lineage"]["engine_version"] == "0.25.0"
        # Anchor is preserved untouched
        assert res_phy.json()["profile"]["identity_anchor"]["instance_uuid"] == SAMPLE_UUID

    def test_live_genesis_invariant_preservation(self):
        """Verify repository data/profile.json is strictly bit-exact and locked."""
        live_profile = Path("data/profile.json")
        assert live_profile.exists()
        raw_text = live_profile.read_text(encoding="utf-8").strip()
        assert raw_text == '{"is_onboarded": false}'
        parsed = json.loads(raw_text)
        assert parsed == {"is_onboarded": False}
