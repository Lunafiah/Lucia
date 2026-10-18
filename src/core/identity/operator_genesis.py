"""
Operator Genesis Entry Point.

Official, deterministic operator entry point for Genesis/Birth.
Codified under ADR-034 (ARCH-034: Identity Authority, Instance Exclusivity & Anti-Branching Boundary)
and Genesis Semantic & Protocol Contract (G1–G4).

Guarantees:
- Solemn, irreversible identity commitment ceremony.
- Invokes canonical execute_genesis() without duplicating logic.
- Requires explicit operator confirmation (--confirm-genesis).
- Fails closed on any pre-condition defect (already BORN, ENDED, UNKNOWN, INVALID_EVIDENCE, uncommitted git).
- Does NOT allow execution during normal backend boot or via conversational routes (/process).
- Produces deterministic, auditable operator outputs.
"""

from __future__ import annotations

import copy
from datetime import datetime, timezone
import json
import logging
import os
from pathlib import Path
import subprocess
from typing import Any, Dict, Optional, Union
import uuid

from src.core.identity.genesis import (
    GenesisCommitment,
    GenesisError,
    GenesisVerificationOutcome,
    OntologyState,
    ReGenesisForbiddenError,
    TerminalLifecycleError,
    execute_genesis,
    verify_genesis,
)
from src.core.identity.identity_anchor import (
    DEFAULT_PROFILE_PATH,
    guard_immutable_fields,
    validate_born_at,
    validate_genesis_commit,
    validate_instance_uuid,
)

logger = logging.getLogger("lucia.identity.operator_genesis")


class OperatorGenesisError(GenesisError):
    """Base exception for operator Genesis execution errors."""
    pass


class OperatorPreconditionError(OperatorGenesisError):
    """Raised when operator Genesis preconditions are violated."""
    pass


def resolve_git_commit(workspace_dir: Optional[Union[Path, str]] = None) -> str:
    """
    Resolve current HEAD commit SHA from git in the specified workspace.
    Fails closed if git is unavailable or returns an invalid SHA.
    Falls back to Path.cwd() if an isolated test workspace is not a git repository.
    """
    ws = Path(workspace_dir).resolve() if workspace_dir else Path.cwd().resolve()
    try:
        res = subprocess.run(
            ["git", "rev-parse", "HEAD"],
            cwd=str(ws),
            capture_output=True,
            text=True,
            check=True,
        )
        commit = res.stdout.strip()
        return validate_genesis_commit(commit)
    except Exception as exc:
        if ws != Path.cwd().resolve():
            try:
                fallback_res = subprocess.run(
                    ["git", "rev-parse", "HEAD"],
                    cwd=str(Path.cwd().resolve()),
                    capture_output=True,
                    text=True,
                    check=True,
                )
                commit = fallback_res.stdout.strip()
                return validate_genesis_commit(commit)
            except Exception:
                pass
        raise OperatorPreconditionError(
            f"Failed to resolve git HEAD commit SHA: {exc}. "
            "Ensure git is installed and the directory is a git repository, "
            "or provide --genesis-commit explicitly."
        ) from exc


def perform_operator_genesis(
    confirm: bool,
    user_name: Optional[str] = None,
    companion_name: Optional[str] = None,
    genesis_commit: Optional[str] = None,
    instance_uuid: Optional[str] = None,
    born_at: Optional[str] = None,
    workspace_dir: Optional[Union[Path, str]] = None,
    commitment_path: Optional[Union[Path, str]] = None,
    profile_path: Optional[Union[Path, str]] = None,
) -> GenesisCommitment:
    """
    Execute the authoritative operator Genesis ceremony under strict safety guards.

    Preconditions:
    1. confirm must be True (explicit operator authorization).
    2. verify_genesis must establish NOT_FOUND (Ontology == NOT_BORN).
    3. Profile, if present, must be un-onboarded (is_onboarded == False, no anchor).
    4. Valid git commit SHA resolved or supplied.
    """
    # 1. Operator confirmation guard
    if not confirm:
        raise OperatorPreconditionError(
            "Genesis is an irreversible ceremony that establishes Lucia's permanent identity. "
            "Explicit operator confirmation (confirm=True or --confirm-genesis) is required."
        )

    ws = Path(workspace_dir).resolve() if workspace_dir else None
    c_p = Path(commitment_path).resolve() if commitment_path else (
        (ws / "data" / "genesis_commitment.json") if ws else None
    )
    p_p = Path(profile_path).resolve() if profile_path else (
        (ws / "data" / "profile.json") if ws else DEFAULT_PROFILE_PATH.resolve()
    )

    # 2. Strict verification pre-check
    verification = verify_genesis(
        workspace_dir=ws,
        commitment_path=c_p,
        profile_path=p_p,
    )

    if verification.ontology_state == OntologyState.ENDED:
        raise TerminalLifecycleError(
            "Genesis forbidden: Instance lifecycle has ENDED (terminal state). "
            "Re-Genesis is permanently prohibited under G1–G4."
        )

    if verification.outcome == GenesisVerificationOutcome.VERIFIED_BORN:
        raise ReGenesisForbiddenError(
            "Genesis forbidden: Instance is already VERIFIED_BORN. "
            "Lucia is one continuous life (INV-1); re-Genesis is strictly prohibited."
        )

    if verification.outcome == GenesisVerificationOutcome.UNKNOWN:
        raise ReGenesisForbiddenError(
            f"Genesis forbidden: Verification returned UNKNOWN ({verification.error_details}). Fail closed."
        )

    if verification.outcome == GenesisVerificationOutcome.INVALID_EVIDENCE:
        raise ReGenesisForbiddenError(
            f"Genesis forbidden: Corrupted evidence detected ({verification.error_details}). "
            "Corrupted evidence must never be overwritten. Fail closed."
        )

    if verification.outcome != GenesisVerificationOutcome.NOT_FOUND:
        raise ReGenesisForbiddenError(
            f"Genesis forbidden: Unexpected verification outcome '{verification.outcome}'."
        )

    # 3. Check profile on disk (must not be onboarded)
    if p_p.exists():
        try:
            with open(p_p, "r", encoding="utf-8") as f:
                prof_data = json.load(f)
            if isinstance(prof_data, dict):
                if prof_data.get("is_onboarded") is True:
                    raise OperatorPreconditionError(
                        "Genesis forbidden: Profile already has 'is_onboarded': true."
                    )
                if prof_data.get("identity_anchor") is not None:
                    raise OperatorPreconditionError(
                        "Genesis forbidden: Profile already contains an 'identity_anchor'."
                    )
        except (json.JSONDecodeError, OSError) as exc:
            raise OperatorPreconditionError(f"Failed to read profile at '{p_p}': {exc}") from exc

    # 4. Resolve parameters
    resolved_commit = (
        validate_genesis_commit(genesis_commit)
        if genesis_commit
        else resolve_git_commit(ws)
    )
    resolved_uuid = (
        validate_instance_uuid(instance_uuid)
        if instance_uuid
        else str(uuid.uuid4())
    )
    resolved_born_at = (
        validate_born_at(born_at)
        if born_at
        else datetime.now(timezone.utc).isoformat()
    )

    # 5. Invoke canonical Genesis implementation
    commitment = execute_genesis(
        instance_uuid=resolved_uuid,
        born_at=resolved_born_at,
        genesis_commit=resolved_commit,
        workspace_dir=ws,
        commitment_path=c_p,
        profile_path=p_p,
    )

    # 6. Apply operator naming preferences if provided
    final_user = (user_name or "").strip()
    final_companion = (companion_name or "").strip()
    if final_user or final_companion:
        try:
            with open(p_p, "r", encoding="utf-8") as f:
                current_profile = json.load(f)
            updated_profile = copy.deepcopy(current_profile)
            if final_user:
                updated_profile["user_name"] = final_user
            if final_companion:
                updated_profile["companion_name"] = final_companion

            guard_immutable_fields(current_profile, updated_profile)

            tmp_p = p_p.with_suffix(".tmp")
            p_bytes = json.dumps(updated_profile, indent=2, sort_keys=True, ensure_ascii=False).encode("utf-8")
            fd = os.open(str(tmp_p), os.O_WRONLY | os.O_CREAT | os.O_TRUNC, 0o600)
            try:
                os.write(fd, p_bytes)
                os.fsync(fd)
            finally:
                os.close(fd)
            os.replace(tmp_p, p_p)
        except Exception as exc:
            logger.warning("Operator preferences sync warning: %s", exc)

    # 6B. Ensure initial host authority binding is established
    try:
        from src.core.identity.provenance_verifier import reconfirm_hardware_environment
        reconfirm_hardware_environment(profile_path=p_p, current_workspace_path=ws)
    except Exception as exc:
        logger.warning("Operator Genesis authority binding warning: %s", exc)

    # 7. Post-Genesis verification assertion
    post_check = verify_genesis(
        workspace_dir=ws,
        commitment_path=c_p,
        profile_path=p_p,
    )
    if post_check.outcome != GenesisVerificationOutcome.VERIFIED_BORN:
        raise OperatorGenesisError(
            f"Post-Genesis verification check failed: expected VERIFIED_BORN, got {post_check.outcome}."
        )

    logger.info(
        "Operator Genesis successfully committed: UUID=%s, BornAt=%s, Root=%s...",
        resolved_uuid,
        resolved_born_at,
        commitment.genesis_root_hash[:12],
    )
    return commitment


def main(args=None) -> int:
    import argparse
    import sys

    parser = argparse.ArgumentParser(
        description="Execute canonical operator Genesis ceremony for Project Lucia.",
    )
    parser.add_argument(
        "--confirm-genesis",
        action="store_true",
        default=False,
        help="Explicit operator confirmation flag.",
    )
    parser.add_argument("--user-name", type=str, default="Friend")
    parser.add_argument("--companion-name", type=str, default="Lucia")
    parser.add_argument("--genesis-commit", type=str, default=None)
    parser.add_argument("--instance-uuid", type=str, default=None)
    parser.add_argument("--born-at", type=str, default=None)
    parser.add_argument("--workspace-dir", type=str, default=None)
    parser.add_argument("--commitment-path", type=str, default=None)
    parser.add_argument("--profile-path", type=str, default=None)

    parsed = parser.parse_args(args)

    if not parsed.confirm_genesis:
        print("[ERROR] Genesis authorization failed: --confirm-genesis is required.", file=sys.stderr)
        return 2

    ws_dir = Path(parsed.workspace_dir).resolve() if parsed.workspace_dir else Path.cwd()
    c_path = Path(parsed.commitment_path).resolve() if parsed.commitment_path else None
    p_path = Path(parsed.profile_path).resolve() if parsed.profile_path else None

    try:
        commitment = perform_operator_genesis(
            confirm=parsed.confirm_genesis,
            user_name=parsed.user_name,
            companion_name=parsed.companion_name,
            genesis_commit=parsed.genesis_commit,
            instance_uuid=parsed.instance_uuid,
            born_at=parsed.born_at,
            workspace_dir=ws_dir,
            commitment_path=c_path,
            profile_path=p_path,
        )
        print("[SUCCESS] Operator Genesis successfully executed.")
        print(f"  Instance UUID:     {commitment.record.identity_anchor.instance_uuid}")
        print(f"  Born At:           {commitment.record.identity_anchor.born_at}")
        print(f"  Genesis Commit:    {commitment.record.identity_anchor.genesis_commit}")
        print(f"  Genesis Root Hash: {commitment.genesis_root_hash}")
        return 0
    except Exception as exc:
        print(f"[ERROR] Operator Genesis failed: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    import sys
    sys.exit(main())

