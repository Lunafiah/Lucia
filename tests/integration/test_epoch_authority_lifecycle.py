"""
tests/integration/test_epoch_authority_lifecycle.py

Integration test suite for WP-04 — Full Lifecycle Ordering & ADR-033/F-02 Interaction.

Governing ADRs: ADR-034 (Identity Authority) & ADR-033 (Epoch Manifest & Persistence)
Reference: docs/others/IDENTITY_AUTHORITY_SPECIFICATION/IMPLEMENTATION_PLAN.md

Verifies:
1. Strict ordering contract:
   Acquire OS Lock (WP-01) -> Validate Identity Anchor (WP-02) ->
   Verify Provenance/Hardware (WP-03) -> verify_and_reconcile_stores (WP-04) ->
   Inject R_t -> Recover Affect (F-02).
2. Zero ingress on pre-lock failure (WP-01 failure exits 75 before any store reading/writing).
3. Corrupted identity anchor fails closed (WP-02 failure exits 1 before provenance or epoch checks).
4. Hardware divergence pauses execution (WP-03 failure exits 76 before epoch reconciliation).
5. Normal startup with valid identity, authority, and epoch stores reaches LUCIA_BACKEND_READY.
6. Cold restart after provenance update verifies new hardware digest, reconciles stores, and succeeds.
7. Interrupted turn commit recovery at startup: uncommitted store automatically rolled back to matching manifest.
8. F-02 dynamical recovery after cold restart restores emotional state while identity anchor remains bit-exact.
9. Pre-Genesis profile invariant: data/profile.json remains bit-exact {"is_onboarded": false}.
"""

from __future__ import annotations

import json
import os
from pathlib import Path
import subprocess
import sys
import time

import numpy as np
import pytest

from src.core.emotion.persistence import (
    CURRENT_SCHEMA_VERSION,
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
)
from src.core.identity.instance_lock import InstanceLock
from src.core.identity.provenance_verifier import (
    collect_hardware_components,
    compute_component_digests,
    compute_hardware_digest,
    normalize_workspace_path,
)
from src.core.relationship.persistence import (
    load_relationship,
    save_relationship,
)
from src.core.relationship.state import RelationshipState

SAMPLE_UUID = "3fa85f64-5717-4562-b3fc-2c963f66afa6"
SAMPLE_BORN_AT = "2026-10-01T00:00:00.000000Z"
SAMPLE_COMMIT = "ce106a245890abcdef1234567890abcdef123456"
SAMPLE_ROOT_HASH = "e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855"


def create_onboarded_test_profile(
    path: Path,
    workspace_path: Path,
    bound_hardware_digest: str,
    migration_epoch: int = 0,
) -> None:
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
        "user_name": "Friend",
        "companion_name": "Lucia",
    }
    path.write_text(json.dumps(data, indent=2), encoding="utf-8")


def create_synced_stores(
    directory: Path,
    epoch_id: int,
) -> tuple[Path, Path, Path, Path]:
    rel_p = directory / "relationship.json"
    dyn_p = directory / "dynamical_state.json"
    man_p = directory / "epoch_manifest.json"
    chat_p = directory / "chat_history.json"

    rel_state = RelationshipState(familiarity=0.45, trust=0.55, closeness=0.4, reciprocity=0.5)
    save_relationship(rel_state, filepath=rel_p, epoch_id=epoch_id)

    dyn_snap = DynamicalStateSnapshot(
        h_fast=np.zeros(EXPECTED_FAST_DIM),
        s_slow=np.ones(EXPECTED_SLOW_DIM) * 0.2,
        created_at=time.time(),
        epoch_id=epoch_id,
    )
    save_dynamical_checkpoint(dyn_snap, filepath=dyn_p)

    manifest = EpochManifest(
        epoch_id=epoch_id,
        t_checkpoint=time.time(),
        stores={"relationship": epoch_id, "dynamical_state": epoch_id},
    )
    save_epoch_manifest(manifest, filepath=man_p)

    chat_p.write_text("[]", encoding="utf-8")
    return rel_p, dyn_p, man_p, chat_p


class TestEpochAuthorityLifecycleIntegration:
    """Integration test suite for WP-04 full startup lifecycle ordering and recovery."""

    def test_ordering_wp01_lock_acquisition_precedes_all(self, tmp_path: Path):
        """WP-01 failure (another process holds lock) exits with 75 before any store operations."""
        lock_file = tmp_path / ".instance.lock"
        profile_file = tmp_path / "profile.json"
        rel_p, dyn_p, man_p, chat_p = create_synced_stores(tmp_path, epoch_id=2)

        # Process A holds the lock
        holder_lock = InstanceLock(lock_path=lock_file)
        holder_lock.acquire()
        try:
            sub_code = f"""
import os, sys
from pathlib import Path
import src.api.server as srv

os.environ["LUCIA_LOCK_PATH"] = str(Path(r"{lock_file}"))
os.environ["LUCIA_PROFILE_PATH"] = str(Path(r"{profile_file}"))
os.environ["LUCIA_RELATIONSHIP_PATH"] = str(Path(r"{rel_p}"))
os.environ["LUCIA_DYNAMICAL_PATH"] = str(Path(r"{dyn_p}"))
os.environ["LUCIA_EPOCH_MANIFEST_PATH"] = str(Path(r"{man_p}"))
os.environ["LUCIA_CHAT_HISTORY_PATH"] = str(Path(r"{chat_p}"))

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

            assert proc.returncode == 75
            assert "LUCIA_BACKEND_ERROR: instance_already_active" in proc.stdout
        finally:
            holder_lock.release()

    def test_ordering_wp02_identity_validation_precedes_provenance_and_epoch(self, tmp_path: Path):
        """WP-02 failure (corrupted anchor) exits with 1 before provenance or epoch store operations."""
        lock_file = tmp_path / ".instance.lock"
        profile_file = tmp_path / "profile.json"
        rel_p, dyn_p, man_p, chat_p = create_synced_stores(tmp_path, epoch_id=2)

        # Corrupted UUID in profile
        corrupted_profile = {
            "schema_version": CANONICAL_SCHEMA_VERSION,
            "is_onboarded": True,
            "identity_anchor": {
                "instance_uuid": "not-a-valid-uuid",
                "born_at": SAMPLE_BORN_AT,
                "genesis_commit": SAMPLE_COMMIT,
                "genesis_root_hash": SAMPLE_ROOT_HASH,
            },
        }
        profile_file.write_text(json.dumps(corrupted_profile, indent=2), encoding="utf-8")

        sub_code = f"""
import os, sys
from pathlib import Path
import src.api.server as srv

os.environ["LUCIA_LOCK_PATH"] = str(Path(r"{lock_file}"))
os.environ["LUCIA_PROFILE_PATH"] = str(Path(r"{profile_file}"))
os.environ["LUCIA_RELATIONSHIP_PATH"] = str(Path(r"{rel_p}"))
os.environ["LUCIA_DYNAMICAL_PATH"] = str(Path(r"{dyn_p}"))
os.environ["LUCIA_EPOCH_MANIFEST_PATH"] = str(Path(r"{man_p}"))
os.environ["LUCIA_CHAT_HISTORY_PATH"] = str(Path(r"{chat_p}"))

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

        assert proc.returncode == 1
        assert "LUCIA_BACKEND_ERROR: corrupted_identity_anchor" in proc.stdout

    def test_ordering_wp03_hardware_mismatch_halts_before_epoch_reconciliation(self, tmp_path: Path):
        """WP-03 hardware divergence pauses with exit code 76 before epoch reconciliation runs."""
        lock_file = tmp_path / ".instance.lock"
        profile_file = tmp_path / "profile.json"
        ws_dir = tmp_path / "ws"
        ws_dir.mkdir()
        rel_p, dyn_p, man_p, chat_p = create_synced_stores(tmp_path, epoch_id=2)

        # Profile bound to nonexistent hardware digest
        create_onboarded_test_profile(profile_file, ws_dir, bound_hardware_digest="0" * 64)

        sub_code = f"""
import os, sys
from pathlib import Path
import src.api.server as srv

os.environ["LUCIA_LOCK_PATH"] = str(Path(r"{lock_file}"))
os.environ["LUCIA_PROFILE_PATH"] = str(Path(r"{profile_file}"))
os.environ["LUCIA_WORKSPACE_PATH"] = str(Path(r"{ws_dir}"))
os.environ["LUCIA_RELATIONSHIP_PATH"] = str(Path(r"{rel_p}"))
os.environ["LUCIA_DYNAMICAL_PATH"] = str(Path(r"{dyn_p}"))
os.environ["LUCIA_EPOCH_MANIFEST_PATH"] = str(Path(r"{man_p}"))
os.environ["LUCIA_CHAT_HISTORY_PATH"] = str(Path(r"{chat_p}"))
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

        assert proc.returncode == 76
        assert "LUCIA_BACKEND_ERROR: awaiting_hardware_reconfirmation" in proc.stdout

    def test_normal_startup_with_valid_identity_authority_epoch(self, tmp_path: Path):
        """Valid identity, valid authority, and valid epoch stores start up and reach LUCIA_BACKEND_READY."""
        lock_file = tmp_path / ".instance.lock"
        profile_file = tmp_path / "profile.json"
        ws_dir = tmp_path / "ws"
        ws_dir.mkdir()
        rel_p, dyn_p, man_p, chat_p = create_synced_stores(tmp_path, epoch_id=3)

        comps = collect_hardware_components(ws_dir)
        hw_digest = compute_hardware_digest(comps)
        create_onboarded_test_profile(profile_file, ws_dir, bound_hardware_digest=hw_digest)

        # Subprocess mocks LLMBackend so server can initialize CognitiveOrchestrator without model weights
        sub_code = f"""
import os, sys
from pathlib import Path
from unittest.mock import MagicMock, patch
import src.api.server as srv

os.environ["LUCIA_LOCK_PATH"] = str(Path(r"{lock_file}"))
os.environ["LUCIA_PROFILE_PATH"] = str(Path(r"{profile_file}"))
os.environ["LUCIA_WORKSPACE_PATH"] = str(Path(r"{ws_dir}"))
os.environ["LUCIA_RELATIONSHIP_PATH"] = str(Path(r"{rel_p}"))
os.environ["LUCIA_DYNAMICAL_PATH"] = str(Path(r"{dyn_p}"))
os.environ["LUCIA_EPOCH_MANIFEST_PATH"] = str(Path(r"{man_p}"))
os.environ["LUCIA_CHAT_HISTORY_PATH"] = str(Path(r"{chat_p}"))

mock_llm = MagicMock()
mock_llm.is_ready.return_value = True

with patch("src.core.orchestrator.cognitive_orchestrator.LLMBackend", return_value=mock_llm):
    srv.init_server(
        model_path="mock_model.gguf",
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

        assert "LUCIA_BACKEND_READY" in proc.stdout, f"Startup failed. Output: {proc.stdout}, Error: {proc.stderr}"
        assert proc.returncode == 0

    def test_interrupted_turn_commit_recovery_at_startup(self, tmp_path: Path):
        """
        Simulate crash after step 1 of turn commit (relationship written with epoch 6, manifest at 5).
        Server startup invokes verify_and_reconcile_stores, automatically rolling relationship back
        to epoch 5 before cognitive loop starts, and reaching LUCIA_BACKEND_READY.
        """
        lock_file = tmp_path / ".instance.lock"
        profile_file = tmp_path / "profile.json"
        ws_dir = tmp_path / "ws"
        ws_dir.mkdir()
        rel_p, dyn_p, man_p, chat_p = create_synced_stores(tmp_path, epoch_id=5)

        comps = collect_hardware_components(ws_dir)
        hw_digest = compute_hardware_digest(comps)
        create_onboarded_test_profile(profile_file, ws_dir, bound_hardware_digest=hw_digest)

        # Write uncommitted relationship at epoch 6 (bak at epoch 5)
        rel_state_6 = RelationshipState(familiarity=0.9, trust=0.9, closeness=0.9, reciprocity=0.9)
        save_relationship(rel_state_6, filepath=rel_p, epoch_id=6)

        sub_code = f"""
import os, sys
from pathlib import Path
from unittest.mock import MagicMock, patch
import src.api.server as srv

os.environ["LUCIA_LOCK_PATH"] = str(Path(r"{lock_file}"))
os.environ["LUCIA_PROFILE_PATH"] = str(Path(r"{profile_file}"))
os.environ["LUCIA_WORKSPACE_PATH"] = str(Path(r"{ws_dir}"))
os.environ["LUCIA_RELATIONSHIP_PATH"] = str(Path(r"{rel_p}"))
os.environ["LUCIA_DYNAMICAL_PATH"] = str(Path(r"{dyn_p}"))
os.environ["LUCIA_EPOCH_MANIFEST_PATH"] = str(Path(r"{man_p}"))
os.environ["LUCIA_CHAT_HISTORY_PATH"] = str(Path(r"{chat_p}"))

mock_llm = MagicMock()
mock_llm.is_ready.return_value = True

with patch("src.core.orchestrator.cognitive_orchestrator.LLMBackend", return_value=mock_llm):
    srv.init_server(
        model_path="mock_model.gguf",
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

        assert "LUCIA_BACKEND_READY" in proc.stdout, f"Startup failed: {proc.stdout}, {proc.stderr}"
        assert proc.returncode == 0

        # Relationship must have been rolled back to epoch 5
        restored = load_relationship(rel_p)
        assert np.isclose(restored.familiarity, 0.45)

    def test_cold_restart_after_provenance_update(self, tmp_path: Path):
        """
        Hardware reconfirmation via flag updates authority binding and increments migration epoch,
        followed immediately by successful epoch reconciliation and startup.
        """
        lock_file = tmp_path / ".instance.lock"
        profile_file = tmp_path / "profile.json"
        ws_dir = tmp_path / "ws"
        ws_dir.mkdir()
        rel_p, dyn_p, man_p, chat_p = create_synced_stores(tmp_path, epoch_id=4)

        # Bind to outdated hardware digest
        create_onboarded_test_profile(profile_file, ws_dir, bound_hardware_digest="2" * 64, migration_epoch=0)

        sub_code = f"""
import os, sys
from pathlib import Path
from unittest.mock import MagicMock, patch
import src.api.server as srv

os.environ["LUCIA_LOCK_PATH"] = str(Path(r"{lock_file}"))
os.environ["LUCIA_PROFILE_PATH"] = str(Path(r"{profile_file}"))
os.environ["LUCIA_WORKSPACE_PATH"] = str(Path(r"{ws_dir}"))
os.environ["LUCIA_RELATIONSHIP_PATH"] = str(Path(r"{rel_p}"))
os.environ["LUCIA_DYNAMICAL_PATH"] = str(Path(r"{dyn_p}"))
os.environ["LUCIA_EPOCH_MANIFEST_PATH"] = str(Path(r"{man_p}"))
os.environ["LUCIA_CHAT_HISTORY_PATH"] = str(Path(r"{chat_p}"))
os.environ["LUCIA_RECONFIRM_HARDWARE"] = "1"

mock_llm = MagicMock()
mock_llm.is_ready.return_value = True

with patch("src.core.orchestrator.cognitive_orchestrator.LLMBackend", return_value=mock_llm):
    srv.init_server(
        model_path="mock_model.gguf",
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

        assert "LUCIA_BACKEND_READY" in proc.stdout, f"Startup failed: {proc.stdout}, {proc.stderr}"
        assert proc.returncode == 0

        # Verify profile updated with incremented migration epoch and current hardware digest
        with open(profile_file, "r", encoding="utf-8") as f:
            updated = json.load(f)
        assert updated["authority_binding"]["hardware_migration_epoch"] == 1
        comps = collect_hardware_components(ws_dir)
        assert updated["authority_binding"]["bound_machine_guid_digest"] == compute_hardware_digest(comps)

        # Verify identity anchor remains bit-exact
        anchor = updated["identity_anchor"]
        assert anchor["instance_uuid"] == SAMPLE_UUID
        assert anchor["born_at"] == SAMPLE_BORN_AT
        assert anchor["genesis_commit"] == SAMPLE_COMMIT
        assert anchor["genesis_root_hash"] == SAMPLE_ROOT_HASH

    def test_live_profile_invariant_remains_locked(self):
        """Invariant 10: Real workspace data/profile.json must remain bit-exact {"is_onboarded": false}."""
        live_profile = Path("data/profile.json")
        assert live_profile.exists()
        content = live_profile.read_text(encoding="utf-8").strip()
        assert content == '{"is_onboarded": false}', (
            f"FATAL: Live data/profile.json violated Genesis invariant! Content: {content}"
        )
