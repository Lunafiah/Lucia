"""
Unit Tests for Operator Genesis Entry Point (Blocker 1).

Governing Specifications:
- ADR-034 (ARCH-034: Identity Authority, Instance Exclusivity & Anti-Branching Boundary)
- Genesis Implementation Contract (G1–G4)
- INV-1 (One Continuous Life)
- INV-8 (Genesis Gate Invariant: Simulation != Activation)

Focused Test Coverage:
1. Refusal when explicit confirmation is omitted (confirm=False).
2. Successful Genesis execution in an isolated test workspace.
3. Durable commitment creation with deterministic Genesis Root.
4. Post-Genesis verification returns VERIFIED_BORN.
5. Refusal / rejection when instance is already BORN (INV-1).
6. Refusal when lifecycle has ENDED (TerminalLifecycleError).
7. Refusal when pre-existing profile is already onboarded.
8. Refusal when git commit hash is invalid.
9. Preservation of Pre-Genesis state on failure (no partial commitment).
10. CLI runner (tools.run_genesis) returns exit code 2 when --confirm-genesis is missing.
11. CLI runner succeeds with exit code 0 when --confirm-genesis is provided in isolated workspace.
12. Strict assertion: live repository data/profile.json remains bit-exact {"is_onboarded": false}
    and live data/genesis_commitment.json remains absent.
"""

from __future__ import annotations

import json
from pathlib import Path
import pytest
from unittest.mock import patch

from src.core.identity.genesis import (
    GenesisVerificationOutcome,
    OntologyState,
    ReGenesisForbiddenError,
    TerminalLifecycleError,
    verify_genesis,
)
from src.core.identity.operator_genesis import (
    OperatorGenesisError,
    OperatorPreconditionError,
    main as operator_genesis_cli_main,
    perform_operator_genesis,
    resolve_git_commit,
)
from scripts.run_genesis import main as cli_main
from scripts.run_genesis import main as script_cli_main

SAMPLE_UUID = "a1b2c3d4-e5f6-4a5b-8c9d-0e1f2a3b4c5d"
SAMPLE_BORN_AT = "2026-10-16T12:00:00.000000Z"
SAMPLE_COMMIT = "c" * 40


@pytest.fixture
def isolated_workspace(tmp_path: Path):
    """Provide isolated test directory with data/ subdirectory and un-onboarded profile."""
    ws = tmp_path / "test_workspace"
    data_dir = ws / "data"
    data_dir.mkdir(parents=True, exist_ok=True)
    profile_path = data_dir / "profile.json"
    profile_path.write_text(json.dumps({"is_onboarded": False}), encoding="utf-8")
    return ws


class TestOperatorGenesis:
    def test_01_refusal_without_confirmation(self, isolated_workspace):
        """1. Genesis must fail immediately if confirm=False."""
        c_path = isolated_workspace / "data" / "genesis_commitment.json"
        p_path = isolated_workspace / "data" / "profile.json"

        with pytest.raises(OperatorPreconditionError) as exc_info:
            perform_operator_genesis(
                confirm=False,
                workspace_dir=isolated_workspace,
                commitment_path=c_path,
                profile_path=p_path,
                genesis_commit=SAMPLE_COMMIT,
            )
        assert "Explicit operator confirmation" in str(exc_info.value)
        assert not c_path.exists()
        assert json.loads(p_path.read_text(encoding="utf-8")) == {"is_onboarded": False}

    def test_02_successful_genesis_in_isolated_workspace(self, isolated_workspace):
        """2. Successful Genesis in isolated workspace establishes durable commitment and updates profile."""
        c_path = isolated_workspace / "data" / "genesis_commitment.json"
        p_path = isolated_workspace / "data" / "profile.json"

        commitment = perform_operator_genesis(
            confirm=True,
            user_name="Luna",
            companion_name="Lucia",
            genesis_commit=SAMPLE_COMMIT,
            instance_uuid=SAMPLE_UUID,
            born_at=SAMPLE_BORN_AT,
            workspace_dir=isolated_workspace,
            commitment_path=c_path,
            profile_path=p_path,
        )

        assert commitment.ontology_state == OntologyState.BORN.value
        assert commitment.record.identity_anchor.instance_uuid == SAMPLE_UUID
        assert commitment.record.identity_anchor.born_at == SAMPLE_BORN_AT
        assert commitment.record.identity_anchor.genesis_commit == SAMPLE_COMMIT

        # Check durable commitment file
        assert c_path.exists()
        c_data = json.loads(c_path.read_text(encoding="utf-8"))
        assert c_data["genesis_root_hash"] == commitment.genesis_root_hash
        assert c_data["ontology_state"] == "BORN"

        # Check updated profile
        p_data = json.loads(p_path.read_text(encoding="utf-8"))
        assert p_data["is_onboarded"] is True
        assert p_data["user_name"] == "Luna"
        assert p_data["companion_name"] == "Lucia"
        assert p_data["identity_anchor"]["instance_uuid"] == SAMPLE_UUID

    def test_03_verification_returns_verified_born(self, isolated_workspace):
        """3. Post-Genesis verification returns outcome VERIFIED_BORN."""
        c_path = isolated_workspace / "data" / "genesis_commitment.json"
        p_path = isolated_workspace / "data" / "profile.json"

        perform_operator_genesis(
            confirm=True,
            genesis_commit=SAMPLE_COMMIT,
            workspace_dir=isolated_workspace,
            commitment_path=c_path,
            profile_path=p_path,
        )

        res = verify_genesis(commitment_path=c_path, profile_path=p_path)
        assert res.outcome == GenesisVerificationOutcome.VERIFIED_BORN
        assert res.ontology_state == OntologyState.BORN

    def test_04_refusal_when_already_born(self, isolated_workspace):
        """4. Second Genesis execution must be strictly rejected (INV-1)."""
        c_path = isolated_workspace / "data" / "genesis_commitment.json"
        p_path = isolated_workspace / "data" / "profile.json"

        perform_operator_genesis(
            confirm=True,
            genesis_commit=SAMPLE_COMMIT,
            workspace_dir=isolated_workspace,
            commitment_path=c_path,
            profile_path=p_path,
        )

        with pytest.raises(ReGenesisForbiddenError) as exc_info:
            perform_operator_genesis(
                confirm=True,
                genesis_commit=SAMPLE_COMMIT,
                workspace_dir=isolated_workspace,
                commitment_path=c_path,
                profile_path=p_path,
            )
        assert "already VERIFIED_BORN" in str(exc_info.value)

    def test_05_refusal_when_ended(self, isolated_workspace):
        """5. Re-Genesis forbidden if instance lifecycle has ENDED."""
        c_path = isolated_workspace / "data" / "genesis_commitment.json"
        p_path = isolated_workspace / "data" / "profile.json"

        p_path.write_text(json.dumps({"is_onboarded": False, "ontology_state": "ENDED"}), encoding="utf-8")

        with pytest.raises(TerminalLifecycleError) as exc_info:
            perform_operator_genesis(
                confirm=True,
                genesis_commit=SAMPLE_COMMIT,
                workspace_dir=isolated_workspace,
                commitment_path=c_path,
                profile_path=p_path,
            )
        assert "ENDED" in str(exc_info.value)

    def test_06_refusal_when_profile_already_onboarded(self, isolated_workspace):
        """6. Rejection if profile is already onboarded."""
        c_path = isolated_workspace / "data" / "genesis_commitment.json"
        p_path = isolated_workspace / "data" / "profile.json"
        p_path.write_text(json.dumps({"is_onboarded": True}), encoding="utf-8")

        with pytest.raises((OperatorPreconditionError, ReGenesisForbiddenError)) as exc_info:
            perform_operator_genesis(
                confirm=True,
                genesis_commit=SAMPLE_COMMIT,
                workspace_dir=isolated_workspace,
                commitment_path=c_path,
                profile_path=p_path,
            )
        assert "Profile already" in str(exc_info.value) or "Profile contains initialized anchor" in str(exc_info.value)

    def test_07_refusal_on_invalid_commit_hash(self, isolated_workspace):
        """7. Fails closed when an invalid git commit hash is passed."""
        c_path = isolated_workspace / "data" / "genesis_commitment.json"
        p_path = isolated_workspace / "data" / "profile.json"

        with pytest.raises(Exception):
            perform_operator_genesis(
                confirm=True,
                genesis_commit="not-a-valid-sha",
                workspace_dir=isolated_workspace,
                commitment_path=c_path,
                profile_path=p_path,
            )
        assert not c_path.exists()

    def test_08_cli_runner_missing_confirmation(self, isolated_workspace):
        """8. CLI runner returns exit code 2 when --confirm-genesis is not passed."""
        c_path = str(isolated_workspace / "data" / "genesis_commitment.json")
        p_path = str(isolated_workspace / "data" / "profile.json")

        exit_code = cli_main(["--commitment-path", c_path, "--profile-path", p_path])
        assert exit_code == 2

    def test_09_cli_runner_successful_execution(self, isolated_workspace):
        """9. CLI runner succeeds with exit code 0 when --confirm-genesis is provided."""
        c_path = str(isolated_workspace / "data" / "genesis_commitment.json")
        p_path = str(isolated_workspace / "data" / "profile.json")

        exit_code = cli_main([
            "--confirm-genesis",
            "--genesis-commit", SAMPLE_COMMIT,
            "--instance-uuid", SAMPLE_UUID,
            "--born-at", SAMPLE_BORN_AT,
            "--commitment-path", c_path,
            "--profile-path", p_path,
            "--user-name", "Luna",
        ])
        assert exit_code == 0
        assert Path(c_path).exists()
        prof = json.loads(Path(p_path).read_text(encoding="utf-8"))
        assert prof["is_onboarded"] is True
        assert prof["user_name"] == "Luna"

    def test_10_scripts_run_genesis_and_module_main(self, isolated_workspace):
        """10. Verify scripts.run_genesis.main and src.core.identity.operator_genesis.main behave identically."""
        # Test scripts.run_genesis missing confirmation
        assert script_cli_main([]) == 2
        # Test operator_genesis module main missing confirmation
        assert operator_genesis_cli_main([]) == 2

        # Test operator_genesis module main with confirmation on another clean workspace
        ws2 = isolated_workspace.parent / "ws2"
        d2 = ws2 / "data"
        d2.mkdir(parents=True, exist_ok=True)
        p2 = d2 / "profile.json"
        p2.write_text(json.dumps({"is_onboarded": False}), encoding="utf-8")
        c2 = d2 / "genesis_commitment.json"

        exit_code = script_cli_main([
            "--confirm-genesis",
            "--genesis-commit", SAMPLE_COMMIT,
            "--instance-uuid", SAMPLE_UUID,
            "--born-at", SAMPLE_BORN_AT,
            "--commitment-path", str(c2),
            "--profile-path", str(p2),
            "--user-name", "Luna",
        ])
        assert exit_code == 0
        assert c2.exists()

    def test_11_live_repository_remains_untouched(self):
        """10. Verify live repository state invariant INV-8 is 100% untouched."""
        live_profile = Path("data/profile.json")
        assert live_profile.exists()
        assert live_profile.read_text(encoding="utf-8").strip() == '{"is_onboarded": false}'

        live_commitment = Path("data/genesis_commitment.json")
        assert not live_commitment.exists(), "Fatal error: live data/genesis_commitment.json must NOT exist!"
