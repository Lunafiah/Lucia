"""
tests/harness/isolated_identity_harness.py

Isolated Verification Harness for WP-01 through WP-05 Identity Authority under ADR-034 / ARCH-034.

Governing ADRs:
- ADR-034: Identity Authority, Instance Exclusivity & Anti-Branching Boundary (WP-01 .. WP-06)
- ADR-033: Persistent Life-State & Downtime Recovery Contracts (F-02)

Primary Architectural Purpose:
Provide a deterministic, fully isolated verification harness proving that
WP-01 through WP-05 identity authority mechanisms can be tested end-to-end without touching
Lucia's live state or unlocking the canonical Genesis gate (data/profile.json).

Hard Invariants Enforced:
- NEVER modify live data/profile.json (remains bit-exact '{"is_onboarded": false}').
- NEVER perform actual Genesis in test execution.
- Fail closed with LiveStateSafetyViolation if any test path resolves to canonical repository data/.
- All synthetic fixtures are strictly isolated in temporary directories and clearly marked.
- 100% offline edge execution (INV-5: zero cloud dependencies).
"""

from __future__ import annotations

import copy
from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone
import hashlib
import json
import logging
import os
from pathlib import Path
import shutil
import subprocess
import sys
import time
from typing import Any, Dict, List, Optional, Sequence, Set, Tuple, Union
import uuid

import numpy as np

from src.core.emotion.persistence import (
    CURRENT_SCHEMA_VERSION,
    DEFAULT_DYNAMICAL_STATE_PATH,
    DEFAULT_EPOCH_MANIFEST_PATH,
    EXPECTED_FAST_DIM,
    EXPECTED_SLOW_DIM,
    DynamicalStateSnapshot,
    EpochManifest,
    StoreReconciliationReport,
    load_dynamical_checkpoint,
    load_epoch_manifest,
    save_dynamical_checkpoint,
    save_epoch_manifest,
    verify_and_reconcile_stores,
)
from src.core.identity.identity_anchor import (
    CANONICAL_SCHEMA_VERSION,
    DEFAULT_PROFILE_PATH,
    IMMUTABLE_IDENTITY_FIELDS,
    CorruptedIdentityAnchorError,
    DecommissionedInstanceError,
    FrozenMigrationStateError,
    IdentityAnchor,
    IdentityAnchorError,
    IdentityProfileState,
    ImmutableIdentityMutationError,
    InvalidIdentityAnchorError,
    PhylogeneticLineage,
    apply_phylogenetic_upgrade,
    guard_immutable_fields,
    validate_identity_anchor,
    validate_profile_identity,
    verify_identity_on_startup,
)
from src.core.identity.instance_lock import (
    DEFAULT_LOCK_PATH,
    InstanceAuthorityConflictError,
    InstanceLock,
)
from src.core.identity.migration_boundary import (
    DecommissionProof,
    MigrationActivationResult,
    MigrationError,
    MigrationManifest,
    MigrationReceipt,
    MigrationStatus,
    MigrationVerificationResult,
    abort_source_freeze,
    activate_destination_instance,
    decommission_source_instance,
    export_migration_archive,
    freeze_for_migration,
    verify_migration_archive,
)
from src.core.identity.provenance_verifier import (
    AuthorityBinding,
    HardwareDigestComponents,
    ProvenanceVerificationResult,
    ProvenanceVerificationStatus,
    ThreatClassification,
    collect_hardware_components,
    compute_component_digests,
    compute_hardware_digest,
    format_high_gravity_hardware_notice,
    normalize_workspace_path,
    reconfirm_hardware_environment,
    verify_provenance_and_environment,
)
from src.core.relationship.persistence import (
    load_relationship,
    save_relationship,
)
from src.core.relationship.state import RelationshipState

logger = logging.getLogger("lucia.test_harness.isolated_identity")

# Canonical repository root and live paths
REPO_ROOT: Path = Path(__file__).resolve().parents[2]
CANONICAL_LIVE_DATA_DIR: Path = (REPO_ROOT / "data").resolve()
CANONICAL_LIVE_PROFILE: Path = (CANONICAL_LIVE_DATA_DIR / "profile.json").resolve()
CANONICAL_LIVE_LOCK: Path = (CANONICAL_LIVE_DATA_DIR / ".instance.lock").resolve()


# ===========================================================================
# 1. Live-State Safety Guard & Violation Exception
# ===========================================================================

class LiveStateSafetyViolation(Exception):
    """
    Fatal safety violation raised when test execution, path resolution,
    or environment variables attempt to access or mutate the repository's
    live data/ directory or live profile state.
    """
    pass


class LiveStateSafetyGuard:
    """
    Enforces absolute isolation between test execution and the live companion runtime.
    Fails closed immediately if any fixture or target resolves to the real data/ tree.
    """

    @classmethod
    def assert_isolated_path(cls, path: Union[str, Path]) -> Path:
        """
        Verify that a path does NOT point to or reside within the live repository data/ directory.
        Returns the resolved Path if safe; raises LiveStateSafetyViolation if unsafe.
        """
        resolved = Path(path).resolve()
        norm_resolved = os.path.normcase(str(resolved))
        norm_live_data = os.path.normcase(str(CANONICAL_LIVE_DATA_DIR))
        norm_live_profile = os.path.normcase(str(CANONICAL_LIVE_PROFILE))
        norm_live_lock = os.path.normcase(str(CANONICAL_LIVE_LOCK))

        if (
            norm_resolved == norm_live_data
            or norm_resolved == norm_live_profile
            or norm_resolved == norm_live_lock
        ):
            raise LiveStateSafetyViolation(
                f"LIVE-STATE SAFETY VIOLATION: Path '{resolved}' resolves directly to live data state!"
            )

        for parent in resolved.parents:
            if os.path.normcase(str(parent.resolve())) == norm_live_data:
                raise LiveStateSafetyViolation(
                    f"LIVE-STATE SAFETY VIOLATION: Path '{resolved}' resides inside live data directory '{CANONICAL_LIVE_DATA_DIR}'!"
                )

        return resolved

    @classmethod
    def audit_environment(cls, env: Dict[str, str]) -> None:
        """
        Inspect an environment dictionary to ensure no path variable points
        to the live data directory.
        """
        keys_to_check = [
            "LUCIA_WORKSPACE_PATH",
            "LUCIA_LOCK_PATH",
            "LUCIA_PROFILE_PATH",
            "LUCIA_CHAT_HISTORY_PATH",
            "LUCIA_RELATIONSHIP_PATH",
            "LUCIA_DYNAMICAL_PATH",
            "LUCIA_EPOCH_MANIFEST_PATH",
        ]
        for key in keys_to_check:
            val = env.get(key)
            if val:
                try:
                    cls.assert_isolated_path(val)
                except LiveStateSafetyViolation as exc:
                    raise LiveStateSafetyViolation(
                        f"Environment variable '{key}' points to unsafe path '{val}': {exc}"
                    ) from exc

    @classmethod
    def verify_live_genesis_invariant(cls) -> Dict[str, Any]:
        """
        Verify that the live canonical data/profile.json remains strictly locked
        and bit-exact '{"is_onboarded": false}'.
        """
        if not CANONICAL_LIVE_PROFILE.exists():
            raise LiveStateSafetyViolation(
                f"FATAL: Live profile {CANONICAL_LIVE_PROFILE} does not exist!"
            )
        raw_text = CANONICAL_LIVE_PROFILE.read_text(encoding="utf-8").strip()
        expected_text = '{"is_onboarded": false}'
        if raw_text != expected_text:
            raise LiveStateSafetyViolation(
                f"LIVE GENESIS INVARIANT VIOLATED! Content was: '{raw_text}', expected: '{expected_text}'"
            )
        data = json.loads(raw_text)
        if data != {"is_onboarded": False}:
            raise LiveStateSafetyViolation(
                f"LIVE GENESIS INVARIANT VIOLATED! Parsed content: {data}"
            )
        return data


# ===========================================================================
# 2. Deterministic Fixture Generator
# ===========================================================================

class DeterministicFixtureGenerator:
    """
    Generates synthetic, deterministic fixtures for testing all post-Genesis
    behavioral layers without performing actual Genesis or modifying live state.
    """

    DEFAULT_SEED_UUID = "4a187a54-6818-4663-c4fd-3d074f77bfa7"
    DEFAULT_BORN_AT = "2026-10-02T12:00:00.000000Z"
    DEFAULT_GENESIS_COMMIT = "1234567890abcdef1234567890abcdef12345678"
    DEFAULT_ROOT_HASH = "e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855"

    @classmethod
    def generate_synthetic_anchor(
        cls,
        instance_uuid: Optional[str] = None,
        born_at: Optional[str] = None,
        genesis_commit: Optional[str] = None,
        genesis_root_hash: Optional[str] = None,
        schema_version: str = CANONICAL_SCHEMA_VERSION,
    ) -> Tuple[IdentityAnchor, Dict[str, Any]]:
        """Generate a valid, deterministic synthetic IdentityAnchor."""
        uid = instance_uuid or cls.DEFAULT_SEED_UUID
        b_at = born_at or cls.DEFAULT_BORN_AT
        commit = genesis_commit or cls.DEFAULT_GENESIS_COMMIT
        root_h = genesis_root_hash or cls.DEFAULT_ROOT_HASH

        anchor = IdentityAnchor(
            instance_uuid=uid,
            born_at=b_at,
            genesis_commit=commit,
            genesis_root_hash=root_h,
        )
        anchor_dict = {
            "instance_uuid": uid,
            "born_at": b_at,
            "genesis_commit": commit,
            "genesis_root_hash": root_h,
            "schema_version": schema_version,
            "_is_synthetic_fixture": True,
        }
        return anchor, anchor_dict

    @classmethod
    def generate_synthetic_profile(
        cls,
        workspace_path: Path,
        is_onboarded: bool = True,
        anchor_dict: Optional[Dict[str, Any]] = None,
        hardware_digest: Optional[str] = None,
        migration_epoch: int = 0,
        engine_version: str = "1.0.0",
        decommissioned: bool = False,
        migration_status: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Generate a synthetic full profile dictionary for testing."""
        if not is_onboarded:
            return {"is_onboarded": False}

        if anchor_dict is None:
            _, anchor_dict = cls.generate_synthetic_anchor()

        comps = collect_hardware_components(workspace_path)
        hw_digest = hardware_digest or compute_hardware_digest(comps)
        norm_ws = normalize_workspace_path(workspace_path)
        now_iso = datetime.now(timezone.utc).isoformat()

        profile: Dict[str, Any] = {
            "schema_version": CANONICAL_SCHEMA_VERSION,
            "is_onboarded": True,
            "user_name": "SyntheticTester",
            "companion_name": "Lucia-Synthetic",
            "identity_anchor": copy.deepcopy(anchor_dict),
            "phylogenetic_lineage": {
                "engine_version": engine_version,
                "last_upgraded_at": now_iso,
                "compatible_schema_major": 2,
                "upgrade_history": [],
            },
            "authority_binding": {
                "hardware_binding_mode": "SOFT_WARNING",
                "bound_machine_guid_digest": hw_digest,
                "activation_host_platform": comps.platform_str,
                "last_known_canonical_path": norm_ws,
                "hardware_migration_epoch": migration_epoch,
                "last_verified_at": now_iso,
                "component_digests": compute_component_digests(comps),
            },
            "covenant": {
                "status": "UNRATIFIED_SPEC_PLACEHOLDER",
            },
            "_is_synthetic_fixture": True,
        }
        if decommissioned:
            profile["migration_state"] = {
                "status": MigrationStatus.DECOMMISSIONED.value,
                "decommissioned_at": now_iso,
            }
        if migration_status:
            profile["migration_state"] = {
                "status": migration_status,
                "updated_at": now_iso,
            }
        return profile

    @classmethod
    def populate_synthetic_stores(
        cls,
        workspace_data_dir: Path,
        epoch_id: int = 10,
        relationship_depth: float = 0.5,
        turn_count: int = 5,
    ) -> Dict[str, str]:
        """
        Populate coherent synthetic stores (relationship, dynamical_state, chat_history,
        and matching epoch_manifest) in an isolated data directory.
        """
        LiveStateSafetyGuard.assert_isolated_path(workspace_data_dir)
        workspace_data_dir.mkdir(parents=True, exist_ok=True)

        # 1. Relationship store
        rel_state = RelationshipState(
            familiarity=float(relationship_depth),
            trust=0.7,
            closeness=float(relationship_depth),
            reciprocity=0.6,
        )
        rel_file = workspace_data_dir / "relationship.json"
        save_relationship(rel_state, filepath=rel_file, epoch_id=epoch_id)

        # 2. Dynamical state store
        dyn_snapshot = DynamicalStateSnapshot(
            h_fast=np.zeros(EXPECTED_FAST_DIM),
            s_slow=np.ones(EXPECTED_SLOW_DIM) * 0.1,
            created_at=time.time(),
            pad={"pleasure": 0.25, "arousal": -0.05, "dominance": 0.05},
            epoch_id=epoch_id,
        )
        dyn_file = workspace_data_dir / "dynamical_state.json"
        save_dynamical_checkpoint(dyn_snapshot, filepath=dyn_file)

        # 3. Chat history store
        chat_file = workspace_data_dir / "chat_history.json"
        chat_payload = {
            "version": 1,
            "epoch_id": epoch_id,
            "turns": [
                {
                    "turn_id": i + 1,
                    "user": f"Synthetic message {i+1}",
                    "lucia": f"Synthetic response {i+1}",
                    "timestamp": datetime.now(timezone.utc).isoformat(),
                }
                for i in range(turn_count)
            ],
        }
        chat_file.write_text(json.dumps(chat_payload, indent=2), encoding="utf-8")

        # 4. Compute file hashes for commit barrier
        def _sha256(p: Path) -> str:
            h = hashlib.sha256()
            with open(p, "rb") as f:
                while chunk := f.read(8192):
                    h.update(chunk)
            return h.hexdigest()

        file_digests = {
            "relationship.json": _sha256(rel_file),
            "dynamical_state.json": _sha256(dyn_file),
            "chat_history.json": _sha256(chat_file),
        }

        # 5. Epoch manifest
        manifest = EpochManifest(
            epoch_id=epoch_id,
            t_checkpoint=time.time(),
            stores={"relationship": epoch_id, "dynamical_state": epoch_id},
        )
        man_file = workspace_data_dir / "epoch_manifest.json"
        save_epoch_manifest(manifest, filepath=man_file)

        return file_digests


# ===========================================================================
# 3. Isolated Workspace
# ===========================================================================

class IsolatedWorkspace:
    """
    Self-contained, temporary directory environment mimicking Lucia's companion filesystem.
    Guaranteed by LiveStateSafetyGuard to reside strictly outside the repository's live data/ tree.
    """

    def __init__(self, workspace_root: Path):
        self.workspace_root: Path = LiveStateSafetyGuard.assert_isolated_path(workspace_root)
        self.data_dir: Path = self.workspace_root / "data"
        self.lock_path: Path = self.data_dir / ".instance.lock"
        self.profile_path: Path = self.data_dir / "profile.json"
        self.chat_history_path: Path = self.data_dir / "chat_history.json"
        self.relationship_path: Path = self.data_dir / "relationship.json"
        self.dynamical_path: Path = self.data_dir / "dynamical_state.json"
        self.epoch_manifest_path: Path = self.data_dir / "epoch_manifest.json"
        self.snapshots_dir: Path = self.data_dir / "snapshots"

        # Initialize folders
        self.data_dir.mkdir(parents=True, exist_ok=True)
        self.snapshots_dir.mkdir(parents=True, exist_ok=True)

        self._active_lock: Optional[InstanceLock] = None

    def setup_pre_genesis_profile(self) -> Path:
        """Write a strictly pre-Genesis un-onboarded profile: {"is_onboarded": false}."""
        data = {"is_onboarded": False}
        self.profile_path.write_text(json.dumps(data), encoding="utf-8")
        return self.profile_path

    def setup_synthetic_initialized_profile(
        self,
        anchor_dict: Optional[Dict[str, Any]] = None,
        hardware_digest: Optional[str] = None,
        migration_epoch: int = 0,
        engine_version: str = "1.0.0",
        decommissioned: bool = False,
        migration_status: Optional[str] = None,
    ) -> Path:
        """Write a valid synthetic initialized profile into the isolated workspace."""
        profile = DeterministicFixtureGenerator.generate_synthetic_profile(
            workspace_path=self.workspace_root,
            anchor_dict=anchor_dict,
            hardware_digest=hardware_digest,
            migration_epoch=migration_epoch,
            engine_version=engine_version,
            decommissioned=decommissioned,
            migration_status=migration_status,
        )
        self.profile_path.write_text(json.dumps(profile, indent=2), encoding="utf-8")
        return self.profile_path

    def setup_epoch_stores(
        self,
        epoch_id: int = 10,
        relationship_depth: float = 0.5,
        turn_count: int = 5,
    ) -> Dict[str, str]:
        """Populate epoch stores and manifest inside this isolated workspace."""
        return DeterministicFixtureGenerator.populate_synthetic_stores(
            workspace_data_dir=self.data_dir,
            epoch_id=epoch_id,
            relationship_depth=relationship_depth,
            turn_count=turn_count,
        )

    def acquire_lock(self) -> InstanceLock:
        """Acquire an InstanceLock bound to this isolated workspace."""
        if self._active_lock is not None and self._active_lock.is_locked:
            raise RuntimeError("Active lock already held by this isolated workspace instance.")
        lock = InstanceLock(lock_path=self.lock_path)
        lock.acquire()
        self._active_lock = lock
        return lock

    def release_lock(self) -> None:
        """Release the currently held isolated lock, if any."""
        if self._active_lock is not None and self._active_lock.is_locked:
            self._active_lock.release()
            self._active_lock = None

    def get_env_overrides(self, extra_env: Optional[Dict[str, str]] = None) -> Dict[str, str]:
        """
        Return an environment dictionary with all paths pointed to this isolated workspace.
        Audited by LiveStateSafetyGuard to prevent leakage.
        """
        env = dict(os.environ)
        overrides = {
            "LUCIA_WORKSPACE_PATH": str(self.workspace_root),
            "LUCIA_LOCK_PATH": str(self.lock_path),
            "LUCIA_PROFILE_PATH": str(self.profile_path),
            "LUCIA_CHAT_HISTORY_PATH": str(self.chat_history_path),
            "LUCIA_RELATIONSHIP_PATH": str(self.relationship_path),
            "LUCIA_DYNAMICAL_PATH": str(self.dynamical_path),
            "LUCIA_EPOCH_MANIFEST_PATH": str(self.epoch_manifest_path),
            "LUCIA_MODE": "live",
        }
        if extra_env:
            overrides.update(extra_env)

        LiveStateSafetyGuard.audit_environment(overrides)
        env.update(overrides)
        return env

    def teardown(self) -> None:
        """Clean up active locks and ensure file handles are released."""
        self.release_lock()


# ===========================================================================
# 4. Migration Harness
# ===========================================================================

class MigrationHarness:
    """
    Coordinates end-to-end migration transactions between two isolated workspaces
    (source and target) under ADR-034 WP-05.
    """

    def __init__(self, source_ws: IsolatedWorkspace, target_ws: IsolatedWorkspace):
        self.source_ws: IsolatedWorkspace = source_ws
        self.target_ws: IsolatedWorkspace = target_ws

        # Ensure both are safe and distinct
        LiveStateSafetyGuard.assert_isolated_path(self.source_ws.workspace_root)
        LiveStateSafetyGuard.assert_isolated_path(self.target_ws.workspace_root)
        if self.source_ws.workspace_root.resolve() == self.target_ws.workspace_root.resolve():
            raise ValueError("Source and target workspaces must be strictly distinct!")

        self.last_manifest: Optional[MigrationManifest] = None
        self.last_archive_path: Optional[Path] = None
        self.last_receipt: Optional[MigrationReceipt] = None
        self.last_decommission_proof: Optional[DecommissionProof] = None
        self.last_activation_result: Optional[MigrationActivationResult] = None

    def step1_freeze_source(self) -> MigrationManifest:
        """Step 1: Freeze source instance for migration."""
        manifest, _ = freeze_for_migration(
            workspace_path=self.source_ws.workspace_root,
            profile_path=self.source_ws.profile_path,
            lock_path=self.source_ws.lock_path,
        )
        self.last_manifest = manifest
        return manifest

    def step1_abort_freeze(self) -> None:
        """Step 1 abort: Abort freeze on source instance."""
        abort_source_freeze(
            workspace_path=self.source_ws.workspace_root,
            profile_path=self.source_ws.profile_path,
        )

    def step2_export_archive(self, export_path: Optional[Path] = None) -> Path:
        """Step 2: Export encrypted/signed migration archive from frozen source."""
        if self.last_manifest is None:
            raise ValueError("Cannot export archive without running step1_freeze_source first.")
        out_path = export_path or (self.source_ws.workspace_root / "migration_archive.tar.gz")
        res_path = export_migration_archive(
            manifest=self.last_manifest,
            data_dir=self.source_ws.data_dir,
            output_archive_path=out_path,
        )
        self.last_archive_path = res_path
        return res_path

    def step3_verify_archive(
        self,
        archive_path: Optional[Path] = None,
        target_hw_components: Optional[HardwareDigestComponents] = None,
    ) -> MigrationReceipt:
        """Step 3: Verify archive on target and issue migration receipt."""
        arch = archive_path or self.last_archive_path
        if arch is None:
            raise ValueError("No archive path provided or available.")
        ver_res, receipt = verify_migration_archive(
            archive_path=arch,
            destination_workspace_path=self.target_ws.workspace_root,
            destination_hardware_components=target_hw_components,
        )
        if not ver_res.is_valid or receipt is None:
            raise MigrationError(f"Archive verification failed: {ver_res.errors}")
        self.last_receipt = receipt
        return receipt

    def step4_decommission_source(
        self,
        receipt: Optional[MigrationReceipt] = None,
    ) -> DecommissionProof:
        """Step 4: Decommission source instance using verified receipt."""
        rec = receipt or self.last_receipt
        if rec is None:
            raise ValueError("No receipt provided or available.")
        proof = decommission_source_instance(
            workspace_path=self.source_ws.workspace_root,
            receipt=rec,
            profile_path=self.source_ws.profile_path,
            lock_path=self.source_ws.lock_path,
        )
        self.last_decommission_proof = proof
        return proof

    def step5_activate_target(
        self,
        archive_path: Optional[Path] = None,
        receipt: Optional[MigrationReceipt] = None,
        proof: Optional[DecommissionProof] = None,
    ) -> MigrationActivationResult:
        """Step 5: Activate destination instance using verified decommission proof."""
        arch = archive_path or self.last_archive_path
        rec = receipt or self.last_receipt
        prf = proof or self.last_decommission_proof
        if arch is None or rec is None or prf is None:
            raise ValueError("Activation requires archive_path, receipt, and decommission_proof.")
        act_res = activate_destination_instance(
            destination_workspace_path=self.target_ws.workspace_root,
            archive_path=arch,
            receipt=rec,
            decommission_proof=prf,
            destination_lock_path=self.target_ws.lock_path,
        )
        self.last_activation_result = act_res
        return act_res

    def run_full_migration(self) -> MigrationActivationResult:
        """Run all 5 steps of the migration boundary sequentially."""
        self.step1_freeze_source()
        self.step2_export_archive()
        self.step3_verify_archive()
        self.step4_decommission_source()
        return self.step5_activate_target()


# ===========================================================================
# 5. Verification Reporter & Summary Model
# ===========================================================================

@dataclass
class ScenarioResult:
    scenario_id: str
    layer: str
    wp_coverage: str
    title: str
    expected_result: str
    actual_result: str
    status: str  # "PASS" or "FAIL"
    invariant_coverage: List[str]
    isolation_status: str = "VERIFIED_ISOLATED"
    unresolved_limitations: Optional[str] = None
    execution_time_ms: float = 0.0


class VerificationReporter:
    """
    Collects, tallies, and serializes test execution evidence across
    all layers and cross-WP invariants.
    """

    def __init__(self):
        self.results: List[ScenarioResult] = []

    def record(
        self,
        scenario_id: str,
        layer: str,
        wp_coverage: str,
        title: str,
        expected_result: str,
        actual_result: str,
        status: str,
        invariant_coverage: List[str],
        isolation_status: str = "VERIFIED_ISOLATED",
        unresolved_limitations: Optional[str] = None,
        execution_time_ms: float = 0.0,
    ) -> ScenarioResult:
        res = ScenarioResult(
            scenario_id=scenario_id,
            layer=layer,
            wp_coverage=wp_coverage,
            title=title,
            expected_result=expected_result,
            actual_result=actual_result,
            status=status,
            invariant_coverage=invariant_coverage,
            isolation_status=isolation_status,
            unresolved_limitations=unresolved_limitations,
            execution_time_ms=execution_time_ms,
        )
        self.results.append(res)
        return res

    @property
    def total_count(self) -> int:
        return len(self.results)

    @property
    def passed_count(self) -> int:
        return sum(1 for r in self.results if r.status == "PASS")

    @property
    def failed_count(self) -> int:
        return sum(1 for r in self.results if r.status == "FAIL")

    def to_dict(self) -> Dict[str, Any]:
        return {
            "harness_name": "WP-06 Isolated Test Harness",
            "governing_adr": "ADR-034 (ARCH-034)",
            "genesis_gate": "LOCKED (data/profile.json bit-exact {'is_onboarded': false})",
            "total_scenarios": self.total_count,
            "passed": self.passed_count,
            "failed": self.failed_count,
            "all_passed": self.failed_count == 0 and self.total_count > 0,
            "scenarios": [asdict(r) for r in self.results],
        }

    def to_json(self, indent: int = 2) -> str:
        return json.dumps(self.to_dict(), indent=indent)

    def to_markdown_table(self) -> str:
        lines = [
            "| Scenario ID | Layer / WP | Title | Expected Result | Actual Result | Status | Invariants | Limitations |",
            "|---|---|---|---|---|:---:|---|---|",
        ]
        for r in self.results:
            invs = ", ".join(r.invariant_coverage)
            limit = r.unresolved_limitations or "None"
            lines.append(
                f"| `{r.scenario_id}` | {r.layer} ({r.wp_coverage}) | {r.title} | {r.expected_result} | {r.actual_result} | **{r.status}** | {invs} | {limit} |"
            )
        return "\n".join(lines)
