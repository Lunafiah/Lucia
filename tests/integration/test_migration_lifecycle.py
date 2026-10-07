"""
Integration test suite for WP-05 — Migration Boundary Lifecycle under ADR-034.

Governing ADR: ADR-034 (Identity Authority, Instance Exclusivity & Anti-Branching Boundary)
Reference: docs/others/IDENTITY_AUTHORITY_SPECIFICATION/IMPLEMENTATION_PLAN.md

Verifies:
1. End-to-end server startup failure on decommissioned source:
   Attempt to start the backend with a decommissioned profile exits with code 1 and
   emits 'LUCIA_BACKEND_ERROR: instance_decommissioned'.
2. End-to-end server startup failure on frozen source:
   Attempt to start the backend with a frozen profile exits with code 1 and
   emits 'LUCIA_BACKEND_ERROR: instance_frozen_for_migration'.
3. Successful server startup on newly activated destination:
   The activated destination workspace boots cleanly and emits 'LUCIA_BACKEND_READY'.
4. Immutability of live repository profile throughout migration tests:
   data/profile.json remains bit-exact '{"is_onboarded": false}'.
"""

from __future__ import annotations

import json
import os
from pathlib import Path
import subprocess
import sys
import time
from typing import Any, Dict

import numpy as np
import pytest

from src.core.emotion.persistence import (
    EXPECTED_FAST_DIM,
    EXPECTED_SLOW_DIM,
    DynamicalStateSnapshot,
    EpochManifest,
    save_dynamical_checkpoint,
    save_epoch_manifest,
)
from src.core.identity.identity_anchor import (
    CANONICAL_SCHEMA_VERSION,
    DEFAULT_PROFILE_PATH,
    IMMUTABLE_IDENTITY_FIELDS,
    verify_identity_on_startup,
)
from src.core.identity.migration_boundary import (
    activate_destination_instance,
    decommission_source_instance,
    export_migration_archive,
    freeze_for_migration,
    verify_migration_archive,
)
from src.core.identity.provenance_verifier import (
    collect_hardware_components,
    compute_component_digests,
    compute_hardware_digest,
    normalize_workspace_path,
)
from src.core.relationship.persistence import save_relationship
from src.core.relationship.state import RelationshipState


SAMPLE_UUID = "4a187a54-6818-4663-c4fd-3d074f77bfa7"
SAMPLE_BORN_AT = "2026-10-02T12:00:00.000000Z"
SAMPLE_COMMIT = "1234567890abcdef1234567890abcdef12345678"
SAMPLE_ROOT_HASH = "e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855"


def create_mock_workspace(
    ws_path: Path,
    epoch_id: int = 10,
    migration_epoch: int = 0,
) -> Dict[str, Any]:
    """Helper to set up mock workspace files."""
    ws = Path(ws_path).resolve()
    data_dir = ws / "data"
    data_dir.mkdir(parents=True, exist_ok=True)

    comps = collect_hardware_components(ws)
    hw_digest = compute_hardware_digest(comps)

    profile_data = {
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
            "hardware_migration_epoch": migration_epoch,
            "last_verified_at": SAMPLE_BORN_AT,
            "component_digests": compute_component_digests(comps),
        },
        "user_name": "Friend",
        "companion_name": "Lucia",
    }

    prof_file = data_dir / "profile.json"
    with open(prof_file, "w", encoding="utf-8") as f:
        json.dump(profile_data, f, indent=2)

    rel_file = data_dir / "relationship.json"
    rel_state = RelationshipState(familiarity=0.7, trust=0.8, closeness=0.6, reciprocity=0.7)
    save_relationship(rel_state, filepath=rel_file, epoch_id=epoch_id)

    dyn_file = data_dir / "dynamical_state.json"
    dyn_snap = DynamicalStateSnapshot(
        h_fast=np.zeros(EXPECTED_FAST_DIM),
        s_slow=np.ones(EXPECTED_SLOW_DIM) * 0.1,
        created_at=time.time(),
        epoch_id=epoch_id,
    )
    save_dynamical_checkpoint(dyn_snap, filepath=dyn_file)

    man_file = data_dir / "epoch_manifest.json"
    manifest = EpochManifest(
        epoch_id=epoch_id,
        t_checkpoint=time.time(),
        stores={"relationship": epoch_id, "dynamical_state": epoch_id},
    )
    save_epoch_manifest(manifest, filepath=man_file)

    chat_file = data_dir / "chat_history.json"
    with open(chat_file, "w", encoding="utf-8") as f:
        json.dump(
            {
                "version": 1,
                "turns": [{"role": "user", "content": "Integration test"}],
            },
            f,
            indent=2,
        )

    return profile_data


class TestMigrationLifecycleIntegration:
    """Integration test suite verifying end-to-end server startup behavior during and after migration."""

    def test_01_frozen_source_server_boot_fails(self, tmp_path: Path):
        """A source instance that is FROZEN cannot start up normally; exits code 1."""
        src_ws = tmp_path / "source"
        src_ws.mkdir()
        create_mock_workspace(src_ws)

        manifest, _ = freeze_for_migration(src_ws)

        prof_p = src_ws / "data" / "profile.json"
        lock_p = src_ws / "data" / ".instance.lock"
        rel_p = src_ws / "data" / "relationship.json"
        dyn_p = src_ws / "data" / "dynamical_state.json"
        man_p = src_ws / "data" / "epoch_manifest.json"
        chat_p = src_ws / "data" / "chat_history.json"

        sub_code = f"""
import os, sys
from pathlib import Path
import src.api.server as srv

os.environ["LUCIA_LOCK_PATH"] = str(Path(r"{lock_p}"))
os.environ["LUCIA_PROFILE_PATH"] = str(Path(r"{prof_p}"))
os.environ["LUCIA_RELATIONSHIP_PATH"] = str(Path(r"{rel_p}"))
os.environ["LUCIA_DYNAMICAL_PATH"] = str(Path(r"{dyn_p}"))
os.environ["LUCIA_EPOCH_MANIFEST_PATH"] = str(Path(r"{man_p}"))
os.environ["LUCIA_CHAT_HISTORY_PATH"] = str(Path(r"{chat_p}"))
os.environ["LUCIA_WORKSPACE_PATH"] = str(Path(r"{src_ws}"))

srv.init_server(
    model_path="dummy.gguf",
    port=8765,
    mode="live",
    lock_path=Path(r"{lock_p}"),
)
"""
        proc = subprocess.run(
            [sys.executable, "-c", sub_code],
            capture_output=True,
            text=True,
            cwd=os.getcwd(),
        )

        assert proc.returncode == 1
        assert "LUCIA_BACKEND_ERROR: instance_frozen_for_migration" in proc.stdout

    def test_02_decommissioned_source_server_boot_fails(self, tmp_path: Path):
        """A source instance that is DECOMMISSIONED cannot start up; exits code 1."""
        src_ws = tmp_path / "source"
        dest_ws = tmp_path / "dest"
        src_ws.mkdir()
        dest_ws.mkdir()
        create_mock_workspace(src_ws)

        manifest, _ = freeze_for_migration(src_ws)
        archive_path = tmp_path / "mig.tar.gz"
        export_migration_archive(manifest, src_ws / "data", archive_path)

        _, receipt = verify_migration_archive(archive_path, dest_ws)
        assert receipt is not None
        decommission_source_instance(src_ws, receipt)

        prof_p = src_ws / "data" / "profile.json"
        lock_p = src_ws / "data" / ".instance.lock"
        rel_p = src_ws / "data" / "relationship.json"
        dyn_p = src_ws / "data" / "dynamical_state.json"
        man_p = src_ws / "data" / "epoch_manifest.json"
        chat_p = src_ws / "data" / "chat_history.json"

        sub_code = f"""
import os, sys
from pathlib import Path
import src.api.server as srv

os.environ["LUCIA_LOCK_PATH"] = str(Path(r"{lock_p}"))
os.environ["LUCIA_PROFILE_PATH"] = str(Path(r"{prof_p}"))
os.environ["LUCIA_RELATIONSHIP_PATH"] = str(Path(r"{rel_p}"))
os.environ["LUCIA_DYNAMICAL_PATH"] = str(Path(r"{dyn_p}"))
os.environ["LUCIA_EPOCH_MANIFEST_PATH"] = str(Path(r"{man_p}"))
os.environ["LUCIA_CHAT_HISTORY_PATH"] = str(Path(r"{chat_p}"))
os.environ["LUCIA_WORKSPACE_PATH"] = str(Path(r"{src_ws}"))

srv.init_server(
    model_path="dummy.gguf",
    port=8765,
    mode="live",
    lock_path=Path(r"{lock_p}"),
)
"""
        proc = subprocess.run(
            [sys.executable, "-c", sub_code],
            capture_output=True,
            text=True,
            cwd=os.getcwd(),
        )

        assert proc.returncode == 1
        assert "LUCIA_BACKEND_ERROR: instance_decommissioned" in proc.stdout

    def test_03_activated_destination_server_boot_succeeds(self, tmp_path: Path):
        """Activated destination instance boots cleanly through server initialization."""
        src_ws = tmp_path / "source"
        dest_ws = tmp_path / "dest"
        src_ws.mkdir()
        dest_ws.mkdir()
        create_mock_workspace(src_ws)

        manifest, _ = freeze_for_migration(src_ws)
        archive_path = tmp_path / "mig.tar.gz"
        export_migration_archive(manifest, src_ws / "data", archive_path)

        dest_comps = collect_hardware_components(dest_ws)
        _, receipt = verify_migration_archive(archive_path, dest_ws, destination_hardware_components=dest_comps)
        assert receipt is not None
        proof = decommission_source_instance(src_ws, receipt)

        act_res = activate_destination_instance(
            destination_workspace_path=dest_ws,
            archive_path=archive_path,
            receipt=receipt,
            decommission_proof=proof,
            destination_hardware_components=dest_comps,
        )
        assert act_res.is_activated is True

        prof_p = dest_ws / "data" / "profile.json"
        lock_p = dest_ws / "data" / ".instance.lock"
        rel_p = dest_ws / "data" / "relationship.json"
        dyn_p = dest_ws / "data" / "dynamical_state.json"
        man_p = dest_ws / "data" / "epoch_manifest.json"
        chat_p = dest_ws / "data" / "chat_history.json"

        sub_code = f"""
import os, sys
from pathlib import Path
from unittest.mock import MagicMock, patch
import src.api.server as srv

os.environ["LUCIA_LOCK_PATH"] = str(Path(r"{lock_p}"))
os.environ["LUCIA_PROFILE_PATH"] = str(Path(r"{prof_p}"))
os.environ["LUCIA_RELATIONSHIP_PATH"] = str(Path(r"{rel_p}"))
os.environ["LUCIA_DYNAMICAL_PATH"] = str(Path(r"{dyn_p}"))
os.environ["LUCIA_EPOCH_MANIFEST_PATH"] = str(Path(r"{man_p}"))
os.environ["LUCIA_CHAT_HISTORY_PATH"] = str(Path(r"{chat_p}"))
os.environ["LUCIA_WORKSPACE_PATH"] = str(Path(r"{dest_ws}"))

mock_llm = MagicMock()
mock_llm.is_ready.return_value = True

with patch("src.core.orchestrator.cognitive_orchestrator.LLMBackend", return_value=mock_llm):
    srv.init_server(
        model_path="dummy.gguf",
        port=8765,
        mode="live",
        lock_path=Path(r"{lock_p}"),
    )
"""
        proc = subprocess.run(
            [sys.executable, "-c", sub_code],
            capture_output=True,
            text=True,
            cwd=os.getcwd(),
        )

        assert proc.returncode == 0
        assert "LUCIA_BACKEND_READY" in proc.stdout

    def test_04_live_profile_immutability_invariant(self):
        """Live repository profile.json remains strictly {'is_onboarded': false}."""
        repo_root = Path(__file__).resolve().parent.parent.parent
        live_profile = repo_root / "data" / "profile.json"

        assert live_profile.exists()
        with open(live_profile, "r", encoding="utf-8") as f:
            data = json.load(f)

        assert data == {"is_onboarded": False}
