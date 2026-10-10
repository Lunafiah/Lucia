"""
Genesis Implementation Contract Unit Tests (G1–G4).

Governing Specifications:
- ADR-034 (ARCH-034: Identity Authority, Instance Exclusivity & Anti-Branching Boundary)
- Genesis Implementation Contract (G1–G4)

Focused Test Coverage:
1. Pre-Genesis remains untouched.
2. Genesis Record construction.
3. Deterministic Genesis Root.
4. Genesis Commitment creation in isolated workspace.
5. Durable commitment verification.
6. NOT_FOUND verification outcome.
7. VERIFIED_BORN verification outcome.
8. UNKNOWN verification outcome.
9. INVALID_EVIDENCE verification outcome.
10. Immutable Genesis Root.
11. Immutable Identity Anchor.
12. Crash-before-commit simulation (NOT_BORN).
13. Crash-before-durability simulation (NOT_BORN, no PARTIALLY_BORN).
14. Crash-after-durable-commit recovery (BORN + INACTIVE).
15. Corrupted Genesis evidence handling (fails closed, never NOT_BORN).
16. Re-Genesis rejection for Born instance.
17. Re-Genesis rejection for UNKNOWN outcome.
18. Re-Genesis rejection for INVALID_EVIDENCE outcome.
19. Born-but-inactive state verification.
20. First Activation requires Born (fails closed on NOT_BORN).
21. First Activation does not create Birth.
22. /lifecycle/end remains terminal (forbids activation and re-Genesis).
23. Live data/profile.json remains bit-exact {"is_onboarded": false}.
24. End-to-end canonical lifecycle sequence integration.
"""

from __future__ import annotations

from dataclasses import FrozenInstanceError
import json
import os
from pathlib import Path
from unittest.mock import patch
import pytest
from starlette.testclient import TestClient

import src.api.server as api_module
from src.core.identity.identity_anchor import (
    IdentityAnchor,
    ImmutableIdentityMutationError,
    InvalidIdentityAnchorError,
    guard_immutable_fields,
    validate_identity_anchor,
)
from src.core.identity.genesis import (
    CANONICAL_GENESIS_PROTOCOL_VERSION,
    CANONICAL_GENESIS_SCHEMA_VERSION,
    GenesisCommitment,
    GenesisProvenance,
    GenesisRecord,
    GenesisVerificationOutcome,
    OntologyState,
    ReGenesisForbiddenError,
    TerminalLifecycleError,
    build_genesis_record,
    canonical_json_bytes,
    commit_genesis,
    compute_genesis_root,
    execute_genesis,
    get_canonical_genesis_root_preimage,
    mark_lifecycle_ended,
    recover_genesis,
    verify_genesis,
    verify_genesis_record_integrity,
)

# Test Fixtures
SAMPLE_UUID = "9b1deb4d-3b7d-4bad-9bdd-2b0d7b3dcb6d"
SAMPLE_BORN_AT = "2026-10-10T12:00:00.000000Z"
SAMPLE_COMMIT = "a" * 40


@pytest.fixture
def isolated_workspace(tmp_path: Path):
    """Provide isolated directory structure with data/ subdirectory."""
    ws = tmp_path / "lucia_workspace"
    data_dir = ws / "data"
    data_dir.mkdir(parents=True, exist_ok=True)
    return ws


@pytest.fixture
def client_with_isolated_env(tmp_path: Path):
    """Provide TestClient with isolated paths for lifecycle API tests."""
    ws = tmp_path / "api_workspace"
    data_dir = ws / "data"
    data_dir.mkdir(parents=True, exist_ok=True)

    profile_file = data_dir / "profile.json"
    commitment_file = data_dir / "genesis_commitment.json"
    history_file = data_dir / "chat_history.json"

    orig_profile = api_module._PROFILE_FILE_PATH
    orig_history = api_module._history_store.file_path
    orig_env_commit = os.environ.get("LUCIA_GENESIS_COMMITMENT_PATH")
    orig_env_prof = os.environ.get("LUCIA_PROFILE_PATH")
    orig_mode = api_module._mode
    orig_sim = api_module._sim_runtime
    orig_active = api_module._is_live_companion_active

    api_module._PROFILE_FILE_PATH = profile_file
    api_module._history_store.file_path = history_file
    api_module._history_store._ensure_file_exists()
    api_module._mode = "live"
    api_module._sim_runtime = None
    api_module._is_live_companion_active = False

    os.environ["LUCIA_PROFILE_PATH"] = str(profile_file)
    os.environ["LUCIA_GENESIS_COMMITMENT_PATH"] = str(commitment_file)

    # Initialize pre-Genesis profile
    profile_file.write_text(json.dumps({"is_onboarded": False}), encoding="utf-8")

    test_client = TestClient(api_module.app)

    yield {
        "client": test_client,
        "workspace": ws,
        "profile_file": profile_file,
        "commitment_file": commitment_file,
        "history_file": history_file,
    }

    # Restore environment
    api_module._PROFILE_FILE_PATH = orig_profile
    api_module._history_store.file_path = orig_history
    api_module._mode = orig_mode
    api_module._sim_runtime = orig_sim
    api_module._is_live_companion_active = orig_active

    if orig_env_commit is not None:
        os.environ["LUCIA_GENESIS_COMMITMENT_PATH"] = orig_env_commit
    else:
        os.environ.pop("LUCIA_GENESIS_COMMITMENT_PATH", None)

    if orig_env_prof is not None:
        os.environ["LUCIA_PROFILE_PATH"] = orig_env_prof
    else:
        os.environ.pop("LUCIA_PROFILE_PATH", None)


class TestGenesisImplementationContract:
    """Test suite covering the complete Genesis Implementation Contract (G1–G4)."""

    def test_01_pre_genesis_remains_untouched(self, isolated_workspace: Path):
        """1. Pre-Genesis state verification performs zero disk writes and leaves profile untouched."""
        profile_file = isolated_workspace / "data" / "profile.json"
        profile_file.write_text('{"is_onboarded": false}', encoding="utf-8")
        stat_before = profile_file.stat()

        result = verify_genesis(workspace_dir=isolated_workspace)

        assert result.outcome == GenesisVerificationOutcome.NOT_FOUND
        assert result.ontology_state == OntologyState.NOT_BORN
        assert result.commitment is None

        stat_after = profile_file.stat()
        assert stat_before.st_mtime == stat_after.st_mtime
        assert profile_file.read_text(encoding="utf-8") == '{"is_onboarded": false}'

    def test_02_genesis_record_construction(self):
        """2. Minimum Genesis Record contains Identity Anchor (WHO) and Genesis Provenance (WHEN/HOW)."""
        record = build_genesis_record(
            instance_uuid=SAMPLE_UUID,
            born_at=SAMPLE_BORN_AT,
            genesis_commit=SAMPLE_COMMIT,
        )

        assert record.identity_anchor.instance_uuid == SAMPLE_UUID
        assert record.identity_anchor.born_at == SAMPLE_BORN_AT
        assert record.identity_anchor.genesis_commit == SAMPLE_COMMIT
        assert len(record.identity_anchor.genesis_root_hash) == 64
        assert record.provenance.protocol_version == CANONICAL_GENESIS_PROTOCOL_VERSION
        assert record.provenance.schema_version == CANONICAL_GENESIS_SCHEMA_VERSION

        raw_dict = record.to_dict()
        assert "identity_anchor" in raw_dict
        assert "genesis_provenance" in raw_dict

        # Verify no forbidden state is present
        forbidden_keys = {
            "personality", "memory", "chat_history", "relationship",
            "preferences", "pad", "runtime_state", "hardware_digest",
        }
        assert not any(k in raw_dict for k in forbidden_keys)

        # Roundtrip
        reconstructed = GenesisRecord.from_dict(raw_dict)
        assert reconstructed == record

    def test_03_deterministic_genesis_root(self):
        """3. Genesis Root is deterministic, canonical, and sensitive to any parameter change."""
        root1 = compute_genesis_root(SAMPLE_UUID, SAMPLE_BORN_AT, SAMPLE_COMMIT)
        root2 = compute_genesis_root(SAMPLE_UUID, SAMPLE_BORN_AT, SAMPLE_COMMIT)
        assert root1 == root2
        assert len(root1) == 64

        # Changing instance_uuid changes root
        root_alt_uuid = compute_genesis_root("00000000-0000-0000-0000-000000000000", SAMPLE_BORN_AT, SAMPLE_COMMIT)
        assert root_alt_uuid != root1

        # Changing born_at changes root
        root_alt_time = compute_genesis_root(SAMPLE_UUID, "2026-10-11T00:00:00.000000Z", SAMPLE_COMMIT)
        assert root_alt_time != root1

        # Changing commit changes root
        root_alt_commit = compute_genesis_root(SAMPLE_UUID, SAMPLE_BORN_AT, "b" * 40)
        assert root_alt_commit != root1

        # Preimage format verification
        preimage = get_canonical_genesis_root_preimage(SAMPLE_UUID, SAMPLE_BORN_AT, SAMPLE_COMMIT)
        canon_bytes = canonical_json_bytes(preimage)
        assert b" " not in canon_bytes  # no whitespace separators

    def test_04_genesis_commitment_creation_isolated(self, isolated_workspace: Path):
        """4. Genesis Commitment creation in an isolated workspace."""
        record = build_genesis_record(SAMPLE_UUID, SAMPLE_BORN_AT, SAMPLE_COMMIT)
        commitment = commit_genesis(record, workspace_dir=isolated_workspace)

        commit_file = isolated_workspace / "data" / "genesis_commitment.json"
        assert commit_file.exists()
        assert commitment.durable is True
        assert commitment.ontology_state == OntologyState.BORN.value
        assert commitment.genesis_root_hash == record.identity_anchor.genesis_root_hash

        data = json.loads(commit_file.read_text(encoding="utf-8"))
        assert data["genesis_root_hash"] == record.identity_anchor.genesis_root_hash
        assert data["ontology_state"] == "BORN"

    def test_05_durable_commitment_verification(self, isolated_workspace: Path):
        """5. Durable commitment verification confirms Record <-> Root integrity."""
        record = build_genesis_record(SAMPLE_UUID, SAMPLE_BORN_AT, SAMPLE_COMMIT)
        commit_genesis(record, workspace_dir=isolated_workspace)

        result = verify_genesis(workspace_dir=isolated_workspace)
        assert result.outcome == GenesisVerificationOutcome.VERIFIED_BORN
        assert result.ontology_state == OntologyState.BORN
        assert result.commitment is not None
        assert result.commitment.record == record

    def test_06_verification_outcome_not_found(self, isolated_workspace: Path):
        """6. Outcome NOT_FOUND returned when local evidence confirms absence of Genesis Commitment."""
        result = verify_genesis(workspace_dir=isolated_workspace)
        assert result.outcome == GenesisVerificationOutcome.NOT_FOUND
        assert result.ontology_state == OntologyState.NOT_BORN

    def test_07_verification_outcome_verified_born(self, isolated_workspace: Path):
        """7. Outcome VERIFIED_BORN returned when valid commitment exists."""
        record = build_genesis_record(SAMPLE_UUID, SAMPLE_BORN_AT, SAMPLE_COMMIT)
        commit_genesis(record, workspace_dir=isolated_workspace)

        result = verify_genesis(workspace_dir=isolated_workspace)
        assert result.outcome == GenesisVerificationOutcome.VERIFIED_BORN

    def test_08_verification_outcome_unknown(self, isolated_workspace: Path, monkeypatch):
        """8. Outcome UNKNOWN returned on I/O error; does NOT infer NOT_BORN; fails closed."""
        record = build_genesis_record(SAMPLE_UUID, SAMPLE_BORN_AT, SAMPLE_COMMIT)
        commit_genesis(record, workspace_dir=isolated_workspace)

        # Simulate permission error on reading the commitment file
        orig_open = open
        def mock_open(path, *args, **kwargs):
            if "genesis_commitment.json" in str(path):
                raise PermissionError("Access denied by OS test harness")
            return orig_open(path, *args, **kwargs)

        monkeypatch.setattr("builtins.open", mock_open)

        result = verify_genesis(workspace_dir=isolated_workspace)
        assert result.outcome == GenesisVerificationOutcome.UNKNOWN
        assert result.ontology_state != OntologyState.BORN
        assert "Access denied" in (result.error_details or "")

    def test_09_verification_outcome_invalid_evidence(self, isolated_workspace: Path):
        """9. Outcome INVALID_EVIDENCE returned on corrupted evidence; does NOT convert to NOT_BORN."""
        commit_file = isolated_workspace / "data" / "genesis_commitment.json"
        commit_file.write_text("{corrupted_json: syntax error", encoding="utf-8")

        result = verify_genesis(workspace_dir=isolated_workspace)
        assert result.outcome == GenesisVerificationOutcome.INVALID_EVIDENCE
        assert result.ontology_state != OntologyState.BORN
        assert "Corrupted JSON" in (result.error_details or "")

    def test_10_immutable_genesis_root(self):
        """10. Genesis Root is immutable (frozen in dataclass)."""
        record = build_genesis_record(SAMPLE_UUID, SAMPLE_BORN_AT, SAMPLE_COMMIT)
        with pytest.raises(FrozenInstanceError):
            record.identity_anchor.genesis_root_hash = "f" * 64  # type: ignore

    def test_11_immutable_identity_anchor(self):
        """11. Identity Anchor immutable fields are protected from mutation."""
        record = build_genesis_record(SAMPLE_UUID, SAMPLE_BORN_AT, SAMPLE_COMMIT)
        profile_original = {
            "is_onboarded": True,
            "identity_anchor": record.identity_anchor.to_dict(),
        }
        profile_mutated = json.loads(json.dumps(profile_original))
        profile_mutated["identity_anchor"]["instance_uuid"] = "00000000-0000-0000-0000-000000000000"

        with pytest.raises(ImmutableIdentityMutationError) as exc_info:
            guard_immutable_fields(profile_original, profile_mutated)
        assert "instance_uuid" in str(exc_info.value)

    def test_12_crash_before_commit_simulation(self, isolated_workspace: Path):
        """12. Crash before commitment leaves instance NOT_BORN (outcome NOT_FOUND)."""
        # Process constructed GenesisRecord in memory but crashed before commit
        record = build_genesis_record(SAMPLE_UUID, SAMPLE_BORN_AT, SAMPLE_COMMIT)
        assert record is not None

        # Recovery checks disk
        recovery = recover_genesis(workspace_dir=isolated_workspace)
        assert recovery.outcome == GenesisVerificationOutcome.NOT_FOUND
        assert recovery.ontology_state == OntologyState.NOT_BORN

    def test_13_crash_before_durability_simulation(self, isolated_workspace: Path):
        """13. Crash before durability (only .tmp file exists) yields NOT_BORN. No PARTIALLY_BORN."""
        tmp_file = isolated_workspace / "data" / "genesis_commitment.json.tmp"
        tmp_file.write_text("{\"record\": \"incomplete write\"}", encoding="utf-8")

        # Destination commitment file does not exist
        recovery = recover_genesis(workspace_dir=isolated_workspace)
        assert recovery.outcome == GenesisVerificationOutcome.NOT_FOUND
        assert recovery.ontology_state == OntologyState.NOT_BORN

    def test_14_crash_after_durable_commit_recovery(self, isolated_workspace: Path):
        """14. Crash after durable commitment recovers BORN + INACTIVE."""
        record = build_genesis_record(SAMPLE_UUID, SAMPLE_BORN_AT, SAMPLE_COMMIT)
        commit_genesis(record, workspace_dir=isolated_workspace)

        # Simulate system reboot / recovery
        recovery = recover_genesis(workspace_dir=isolated_workspace)
        assert recovery.outcome == GenesisVerificationOutcome.VERIFIED_BORN
        assert recovery.ontology_state == OntologyState.BORN
        assert recovery.commitment is not None

    def test_15_corrupted_genesis_evidence_handling(self, isolated_workspace: Path):
        """15. Corrupted evidence is never reinterpreted as NOT_BORN, and never overwritten."""
        record = build_genesis_record(SAMPLE_UUID, SAMPLE_BORN_AT, SAMPLE_COMMIT)
        commit_genesis(record, workspace_dir=isolated_workspace)

        commit_file = isolated_workspace / "data" / "genesis_commitment.json"
        raw_data = json.loads(commit_file.read_text(encoding="utf-8"))
        # Tamper with the root hash to simulate corruption
        raw_data["genesis_root_hash"] = "0" * 64
        commit_file.write_text(json.dumps(raw_data), encoding="utf-8")

        result = verify_genesis(workspace_dir=isolated_workspace)
        assert result.outcome == GenesisVerificationOutcome.INVALID_EVIDENCE

        # Re-Genesis must be rejected; evidence must remain intact
        with pytest.raises(ReGenesisForbiddenError) as exc_info:
            execute_genesis(SAMPLE_UUID, SAMPLE_BORN_AT, SAMPLE_COMMIT, workspace_dir=isolated_workspace)
        assert "INVALID_EVIDENCE" in str(exc_info.value)
        # Confirm file on disk was NOT overwritten
        assert json.loads(commit_file.read_text(encoding="utf-8"))["genesis_root_hash"] == "0" * 64

    def test_16_regenesis_rejection_for_born_instance(self, isolated_workspace: Path):
        """16. Re-Genesis is strictly rejected for an already-born instance (INV-1)."""
        execute_genesis(SAMPLE_UUID, SAMPLE_BORN_AT, SAMPLE_COMMIT, workspace_dir=isolated_workspace)

        with pytest.raises(ReGenesisForbiddenError) as exc_info:
            execute_genesis(
                instance_uuid="11111111-1111-1111-1111-111111111111",
                born_at="2026-10-10T13:00:00.000000Z",
                genesis_commit="f" * 40,
                workspace_dir=isolated_workspace,
            )
        assert "VERIFIED_BORN" in str(exc_info.value)

    def test_17_regenesis_rejection_for_unknown(self, isolated_workspace: Path, monkeypatch):
        """17. Re-Genesis is rejected when verification returns UNKNOWN."""
        record = build_genesis_record(SAMPLE_UUID, SAMPLE_BORN_AT, SAMPLE_COMMIT)
        commit_genesis(record, workspace_dir=isolated_workspace)

        # Mock permission error
        orig_open = open
        def mock_open(path, *args, **kwargs):
            if "genesis_commitment.json" in str(path):
                raise PermissionError("Access denied by OS lock")
            return orig_open(path, *args, **kwargs)

        monkeypatch.setattr("builtins.open", mock_open)

        with pytest.raises(ReGenesisForbiddenError) as exc_info:
            execute_genesis(SAMPLE_UUID, SAMPLE_BORN_AT, SAMPLE_COMMIT, workspace_dir=isolated_workspace)
        assert "UNKNOWN" in str(exc_info.value)

    def test_18_regenesis_rejection_for_invalid_evidence(self, isolated_workspace: Path):
        """18. Re-Genesis is rejected when evidence is corrupted (INVALID_EVIDENCE)."""
        commit_file = isolated_workspace / "data" / "genesis_commitment.json"
        commit_file.write_text("corrupted bytes", encoding="utf-8")

        with pytest.raises(ReGenesisForbiddenError) as exc_info:
            execute_genesis(SAMPLE_UUID, SAMPLE_BORN_AT, SAMPLE_COMMIT, workspace_dir=isolated_workspace)
        assert "Corrupted Genesis evidence detected" in str(exc_info.value)

    def test_19_born_but_inactive_state(self, isolated_workspace: Path):
        """19. Born-but-inactive state is verified: ontology is BORN while runtime remains INACTIVE."""
        commitment = execute_genesis(SAMPLE_UUID, SAMPLE_BORN_AT, SAMPLE_COMMIT, workspace_dir=isolated_workspace)
        assert commitment.ontology_state == OntologyState.BORN.value

        ver = verify_genesis(workspace_dir=isolated_workspace)
        assert ver.ontology_state == OntologyState.BORN

        # Runtime active flag in API layer is False
        assert api_module._is_live_companion_active is False

    def test_20_first_activation_requires_born(self, client_with_isolated_env):
        """20. First Activation requires BORN. Calling /lifecycle/activate on NOT_BORN fails with 400."""
        client = client_with_isolated_env["client"]
        # Profile is {"is_onboarded": false}, no commitment exists (NOT_FOUND)
        resp = client.post("/lifecycle/activate")
        assert resp.status_code == 400
        assert "NOT_BORN" in resp.json()["detail"]
        assert "Activation does not create Birth" in resp.json()["detail"]

    def test_21_first_activation_does_not_create_birth(self, client_with_isolated_env):
        """21. First Activation does not create Birth: profile remains un-onboarded, no commitment created."""
        client = client_with_isolated_env["client"]
        profile_file = client_with_isolated_env["profile_file"]
        commitment_file = client_with_isolated_env["commitment_file"]

        resp = client.post("/lifecycle/activate")
        assert resp.status_code == 400

        # Confirm zero identity anchor generated
        prof_data = json.loads(profile_file.read_text(encoding="utf-8"))
        assert prof_data.get("is_onboarded") is False
        assert "identity_anchor" not in prof_data
        assert "born_at" not in prof_data
        assert not commitment_file.exists()

    def test_22_lifecycle_end_remains_terminal(self, client_with_isolated_env):
        """22. /lifecycle/end transitions to ENDED and permanently forbids activation and re-Genesis."""
        client = client_with_isolated_env["client"]
        ws = client_with_isolated_env["workspace"]
        commitment_file = client_with_isolated_env["commitment_file"]
        profile_file = client_with_isolated_env["profile_file"]

        # 1. Establish valid Genesis in isolated workspace
        execute_genesis(
            SAMPLE_UUID,
            SAMPLE_BORN_AT,
            SAMPLE_COMMIT,
            commitment_path=commitment_file,
            profile_path=profile_file,
        )

        # 2. Activate companion (BORN -> ACTIVE)
        act_resp = client.post("/lifecycle/activate")
        assert act_resp.status_code == 200
        assert act_resp.json()["status"] == "activated"
        assert act_resp.json()["born_at"] == SAMPLE_BORN_AT

        # 3. Call POST /lifecycle/end (ACTIVE -> ENDED)
        end_resp = client.post("/lifecycle/end")
        assert end_resp.status_code == 200
        assert end_resp.json()["status"] == "ok"
        assert end_resp.json()["profile"]["is_onboarded"] is False

        # 4. Subsequent activation is forbidden (HTTP 410 Gone)
        act_resp2 = client.post("/lifecycle/activate")
        assert act_resp2.status_code == 410
        assert "ENDED" in act_resp2.json()["detail"]

        # 5. Subsequent re-Genesis is strictly forbidden
        with pytest.raises(TerminalLifecycleError) as exc_info:
            execute_genesis(
                instance_uuid="22222222-2222-2222-2222-222222222222",
                born_at="2026-10-10T14:00:00.000000Z",
                genesis_commit="c" * 40,
                commitment_path=commitment_file,
                profile_path=profile_file,
            )
        assert "ENDED" in str(exc_info.value)

    def test_23_live_profile_json_remains_bit_exact(self):
        """23. Live repository data/profile.json remains bit-exact {"is_onboarded": false}."""
        live_profile = Path("data/profile.json")
        assert live_profile.exists()
        content = live_profile.read_text(encoding="utf-8").strip()
        assert content == '{"is_onboarded": false}'

    def test_24_canonical_lifecycle_sequence_integration(self, client_with_isolated_env):
        """24. Complete canonical sequence integration test."""
        client = client_with_isolated_env["client"]
        ws = client_with_isolated_env["workspace"]
        commitment_file = client_with_isolated_env["commitment_file"]
        profile_file = client_with_isolated_env["profile_file"]

        # Stage 1: PRE-GENESIS (NOT_FOUND)
        res1 = verify_genesis(commitment_path=commitment_file, profile_path=profile_file)
        assert res1.outcome == GenesisVerificationOutcome.NOT_FOUND
        assert res1.ontology_state == OntologyState.NOT_BORN

        # Stage 2: Attempt activation before Genesis -> Fails
        act_fail = client.post("/lifecycle/activate")
        assert act_fail.status_code == 400

        # Stage 3: Genesis Execution (Construct -> Root -> Durable Commit -> BORN + INACTIVE)
        record = build_genesis_record(SAMPLE_UUID, SAMPLE_BORN_AT, SAMPLE_COMMIT)
        commit = commit_genesis(record, commitment_path=commitment_file, profile_path=profile_file)
        assert commit.ontology_state == OntologyState.BORN.value

        # Stage 4: Verification (BORN + INACTIVE)
        res2 = verify_genesis(commitment_path=commitment_file, profile_path=profile_file)
        assert res2.outcome == GenesisVerificationOutcome.VERIFIED_BORN
        assert res2.ontology_state == OntologyState.BORN
        assert api_module._is_live_companion_active is False

        # Stage 5: First Activation (BORN -> ACTIVE)
        act_ok = client.post("/lifecycle/activate")
        assert act_ok.status_code == 200
        assert act_ok.json()["status"] == "activated"
        assert act_ok.json()["born_at"] == SAMPLE_BORN_AT
        assert api_module._is_live_companion_active is True

        # Second activation is idempotent: returns already_active
        act_again = client.post("/lifecycle/activate")
        assert act_again.status_code == 200
        assert act_again.json()["status"] == "already_active"

        # Stage 6: Terminal End (ACTIVE -> ENDED)
        end_ok = client.post("/lifecycle/end")
        assert end_ok.status_code == 200
        assert api_module._is_live_companion_active is False

        # Stage 7: Activation and re-Genesis forbidden after ENDED
        act_post_end = client.post("/lifecycle/activate")
        assert act_post_end.status_code == 410

        with pytest.raises(TerminalLifecycleError):
            execute_genesis(SAMPLE_UUID, SAMPLE_BORN_AT, SAMPLE_COMMIT, commitment_path=commitment_file)
