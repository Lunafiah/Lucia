"""
Integration Tests for WP-03 Provenance & Environment Verification at Server Startup.

Governing ADR: ADR-034 (ARCH-034: Identity Authority, Instance Exclusivity & Anti-Branching Boundary).
Reference Specification: docs/others/IDENTITY_AUTHORITY_SPECIFICATION/IDENTITY_AUTHORITY_SPEC_V01.md
Reference Plan: docs/others/IDENTITY_AUTHORITY_SPECIFICATION/IMPLEMENTATION_PLAN.md

Tests cover:
- Startup workspace location divergence fails closed (exit code 1, 'workspace_location_divergence').
- Startup hardware divergence enters modal state (exit code 76, 'awaiting_hardware_reconfirmation').
- Startup hardware reconfirmation via flag (LUCIA_RECONFIRM_HARDWARE=1) updates profile safely,
  increments migration epoch, and preserves identity anchor.
- WP-01 lock precedence: Instance lock conflict (exit code 75) halts startup before provenance check.
- Pre-Genesis locked profile startup defers provenance checks safely without disk mutation.
- Live profile invariant preservation: data/profile.json remains bit-exact {"is_onboarded": false}.
"""

from __future__ import annotations

import json
import os
from pathlib import Path
import subprocess
import sys

import pytest

from src.core.identity.identity_anchor import (
    CANONICAL_SCHEMA_VERSION,
)
from src.core.identity.instance_lock import InstanceLock
from src.core.identity.provenance_verifier import (
    collect_hardware_components,
    compute_component_digests,
    compute_hardware_digest,
    normalize_workspace_path,
)

SAMPLE_UUID = "3fa85f64-5717-4562-b3fc-2c963f66afa6"
SAMPLE_BORN_AT = "2026-10-01T00:00:00.000000Z"
SAMPLE_COMMIT = "ce106a245890abcdef1234567890abcdef123456"
SAMPLE_ROOT_HASH = "e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855"


def create_test_onboarded_profile(
    path: Path,
    workspace_path: Path,
    bound_hardware_digest: str,
    migration_epoch: int = 0,
) -> None:
    """Helper to write an onboarded profile with specified authority binding."""
    comps = collect_hardware_components(workspace_path)
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
            "bound_machine_guid_digest": bound_hardware_digest,
            "activation_host_platform": comps.platform_str,
            "last_known_canonical_path": normalize_workspace_path(workspace_path),
            "hardware_migration_epoch": migration_epoch,
            "last_verified_at": SAMPLE_BORN_AT,
            "component_digests": compute_component_digests(comps),
        },
    }
    path.write_text(json.dumps(data, indent=2), encoding="utf-8")


class TestProvenanceStartupIntegration:
    """Integration test suite for server.py startup lifecycle integration with WP-03."""

    def test_startup_workspace_divergence_fails_closed(self, tmp_path: Path) -> None:
        """Workspace location divergence causes server to fail closed with exit code 1."""
        lock_file = tmp_path / ".instance.lock"
        profile_file = tmp_path / "profile.json"
        registered_ws = tmp_path / "Primary_Workspace"
        registered_ws.mkdir()
        active_ws = tmp_path / "Copied_Workspace"
        active_ws.mkdir()

        # Compute current host hardware digest so hardware check would otherwise pass
        comps = collect_hardware_components(registered_ws)
        hw_digest = compute_hardware_digest(comps)

        # Profile was registered at registered_ws, but active workspace will be active_ws
        create_test_onboarded_profile(profile_file, registered_ws, bound_hardware_digest=hw_digest)
        content_before = profile_file.read_text(encoding="utf-8")

        sub_code = f"""
import os, sys
from pathlib import Path
import src.api.server as srv

os.environ["LUCIA_LOCK_PATH"] = str(Path(r"{lock_file}"))
os.environ["LUCIA_PROFILE_PATH"] = str(Path(r"{profile_file}"))
os.environ["LUCIA_WORKSPACE_PATH"] = str(Path(r"{active_ws}"))

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
            f"Expected exit code 1, got {proc.returncode}. Stdout: {proc.stdout}, Stderr: {proc.stderr}"
        )
        assert "LUCIA_BACKEND_ERROR: workspace_location_divergence" in proc.stdout
        # Non-destructive check: profile must remain untouched
        assert profile_file.read_text(encoding="utf-8") == content_before

    def test_startup_hardware_mismatch_enters_awaiting_reconfirmation(self, tmp_path: Path) -> None:
        """Hardware digest divergence without reconfirmation enters AWAITING_HARDWARE_RECONFIRMATION (exit 76)."""
        lock_file = tmp_path / ".instance.lock"
        profile_file = tmp_path / "profile.json"
        ws_dir = tmp_path / "Lucia_App"
        ws_dir.mkdir()

        # Set a deliberately mismatched bound digest
        mismatched_digest = "0000000000000000000000000000000000000000000000000000000000000000"
        create_test_onboarded_profile(profile_file, ws_dir, bound_hardware_digest=mismatched_digest)
        content_before = profile_file.read_text(encoding="utf-8")

        sub_code = f"""
import os, sys
from pathlib import Path
import src.api.server as srv

os.environ["LUCIA_LOCK_PATH"] = str(Path(r"{lock_file}"))
os.environ["LUCIA_PROFILE_PATH"] = str(Path(r"{profile_file}"))
os.environ["LUCIA_WORKSPACE_PATH"] = str(Path(r"{ws_dir}"))
os.environ.pop("LUCIA_RECONFIRM_HARDWARE", None)

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

        assert proc.returncode == 76, (
            f"Expected exit code 76 for awaiting hardware reconfirmation, got {proc.returncode}. "
            f"Stdout: {proc.stdout}, Stderr: {proc.stderr}"
        )
        assert "LUCIA_BACKEND_ERROR: awaiting_hardware_reconfirmation" in proc.stdout
        # Non-destructive check: profile untouched
        assert profile_file.read_text(encoding="utf-8") == content_before

    def test_startup_hardware_reconfirmation_via_flag(self, tmp_path: Path) -> None:
        """With LUCIA_RECONFIRM_HARDWARE=1, startup updates hardware digest and migration epoch non-destructively."""
        lock_file = tmp_path / ".instance.lock"
        profile_file = tmp_path / "profile.json"
        ws_dir = tmp_path / "Lucia_App"
        ws_dir.mkdir()

        mismatched_digest = "1111111111111111111111111111111111111111111111111111111111111111"
        create_test_onboarded_profile(
            profile_file, ws_dir, bound_hardware_digest=mismatched_digest, migration_epoch=0
        )

        sub_code = f"""
import os, sys
from pathlib import Path
import src.api.server as srv

os.environ["LUCIA_LOCK_PATH"] = str(Path(r"{lock_file}"))
os.environ["LUCIA_PROFILE_PATH"] = str(Path(r"{profile_file}"))
os.environ["LUCIA_WORKSPACE_PATH"] = str(Path(r"{ws_dir}"))
os.environ["LUCIA_RECONFIRM_HARDWARE"] = "1"

# We pass a non-existent model path so it passes provenance, then fails at model initialization
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

        # It must NOT exit with 76 (awaiting reconfirmation) or workspace divergence
        assert "LUCIA_BACKEND_ERROR: awaiting_hardware_reconfirmation" not in proc.stdout
        assert "LUCIA_BACKEND_ERROR: workspace_location_divergence" not in proc.stdout
        # Expect model_path_not_configured (which happens after provenance verification!)
        assert "LUCIA_BACKEND_ERROR: model_path_not_configured" in proc.stdout

        # Verify profile was updated with new hardware digest and incremented epoch
        with open(profile_file, "r", encoding="utf-8") as f:
            updated = json.load(f)

        auth = updated["authority_binding"]
        comps = collect_hardware_components(ws_dir)
        expected_digest = compute_hardware_digest(comps)
        assert auth["bound_machine_guid_digest"] == expected_digest
        assert auth["hardware_migration_epoch"] == 1

        # Verify identity anchor remains bit-exact
        anchor = updated["identity_anchor"]
        assert anchor["instance_uuid"] == SAMPLE_UUID
        assert anchor["born_at"] == SAMPLE_BORN_AT
        assert anchor["genesis_commit"] == SAMPLE_COMMIT
        assert anchor["genesis_root_hash"] == SAMPLE_ROOT_HASH

    def test_startup_wp01_ordering_precedence_over_provenance(self, tmp_path: Path) -> None:
        """
        WP-01 ordering contract: Instance authority lock check executes BEFORE provenance verification.
        If lock is held by another process, server exits with code 75 ('instance_already_active')
        regardless of any provenance or hardware divergence.
        """
        lock_file = tmp_path / ".instance.lock"
        profile_file = tmp_path / "profile.json"
        ws_dir = tmp_path / "Lucia_App"
        ws_dir.mkdir()

        # Both workspace and hardware are invalid
        mismatched_digest = "9999999999999999999999999999999999999999999999999999999999999999"
        create_test_onboarded_profile(profile_file, tmp_path / "Wrong_Ws", bound_hardware_digest=mismatched_digest)

        # Process A acquires the lock
        holder = InstanceLock(lock_path=lock_file)
        holder.acquire()

        try:
            # Process B attempts startup
            sub_code = f"""
import os, sys
from pathlib import Path
import src.api.server as srv

os.environ["LUCIA_LOCK_PATH"] = str(Path(r"{lock_file}"))
os.environ["LUCIA_PROFILE_PATH"] = str(Path(r"{profile_file}"))
os.environ["LUCIA_WORKSPACE_PATH"] = str(Path(r"{ws_dir}"))

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

            # Process B must exit with 75 (WP-01), not 1 or 76!
            assert proc.returncode == 75, (
                f"Expected exit code 75 (Instance Authority Conflict), got {proc.returncode}. "
                f"Stdout: {proc.stdout}, Stderr: {proc.stderr}"
            )
            assert "LUCIA_BACKEND_ERROR: instance_already_active" in proc.stdout
        finally:
            holder.release()

    def test_startup_pre_genesis_profile_defers_provenance(self, tmp_path: Path) -> None:
        """Pre-Genesis locked profile defers provenance checks safely without disk mutation."""
        lock_file = tmp_path / ".instance.lock"
        profile_file = tmp_path / "profile.json"
        profile_file.write_text('{"is_onboarded": false}', encoding="utf-8")

        sub_code = f"""
import os, sys
from pathlib import Path
import src.api.server as srv

os.environ["LUCIA_LOCK_PATH"] = str(Path(r"{lock_file}"))
os.environ["LUCIA_PROFILE_PATH"] = str(Path(r"{profile_file}"))

# With no model path, startup passes genesis check then fails on model_path_not_configured
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

        assert "LUCIA_BACKEND_ERROR: model_path_not_configured" in proc.stdout
        assert "LUCIA_BACKEND_ERROR: workspace_location_divergence" not in proc.stdout
        assert "LUCIA_BACKEND_ERROR: awaiting_hardware_reconfirmation" not in proc.stdout
        # Profile remains bit-exact
        assert profile_file.read_text(encoding="utf-8") == '{"is_onboarded": false}'

    def test_live_genesis_invariant_preservation(self) -> None:
        """INV-8: Verify that real data/profile.json remains exactly {"is_onboarded": false}."""
        real_profile = Path("data/profile.json")
        assert real_profile.exists()
        content = real_profile.read_text(encoding="utf-8").strip()
        assert content == '{"is_onboarded": false}', (
            f"INV-8 violated: real data/profile.json was modified: '{content}'"
        )
