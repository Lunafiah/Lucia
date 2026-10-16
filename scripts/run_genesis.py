#!/usr/bin/env python3
"""
CLI Runner for the Lucia Canonical Genesis Ceremony.

Usage:
    python scripts/run_genesis.py --confirm-genesis [--user-name Luna] [--companion-name Lucia]

Safety:
    - Fails immediately if --confirm-genesis is not provided.
    - Requires pre-Genesis state (data/profile.json is un-onboarded, no commitment file).
    - Exclusivity: Only executable when no other instance is running.
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

# Ensure workspace root is in sys.path when executed directly
workspace_root = Path(__file__).resolve().parent.parent
if str(workspace_root) not in sys.path:
    sys.path.insert(0, str(workspace_root))

from src.core.identity.operator_genesis import (
    OperatorGenesisError,
    OperatorPreconditionError,
    perform_operator_genesis,
)
from src.core.identity.genesis import (
    ReGenesisForbiddenError,
    TerminalLifecycleError,
)


def parse_args(args=None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Execute the canonical Genesis Ceremony for Project Lucia.",
    )
    parser.add_argument(
        "--confirm-genesis",
        action="store_true",
        default=False,
        help="Explicit authorization acknowledging that Genesis is permanent and irreversible.",
    )
    parser.add_argument(
        "--user-name",
        type=str,
        default="Friend",
        help="Name by which Lucia should address you (e.g. Luna).",
    )
    parser.add_argument(
        "--companion-name",
        type=str,
        default="Lucia",
        help="Name of the companion (default: Lucia).",
    )
    parser.add_argument(
        "--genesis-commit",
        type=str,
        default=None,
        help="Explicit git commit SHA (defaults to HEAD of current repository).",
    )
    parser.add_argument(
        "--instance-uuid",
        type=str,
        default=None,
        help="Explicit instance UUID (defaults to generating a fresh RFC 4122 v4 UUID).",
    )
    parser.add_argument(
        "--born-at",
        type=str,
        default=None,
        help="Explicit ISO-8601 UTC timestamp (defaults to current UTC time).",
    )
    parser.add_argument(
        "--workspace-dir",
        type=str,
        default=None,
        help="Path to workspace root (defaults to current working directory).",
    )
    parser.add_argument(
        "--commitment-path",
        type=str,
        default=None,
        help="Path to genesis_commitment.json.",
    )
    parser.add_argument(
        "--profile-path",
        type=str,
        default=None,
        help="Path to profile.json.",
    )
    return parser.parse_args(args)


def main(args=None) -> int:
    parsed = parse_args(args)

    print("======================================================================")
    print("             LUCIA CANONICAL GENESIS CEREMONY (G1–G4)                 ")
    print("======================================================================")

    if not parsed.confirm_genesis:
        print("[ERROR] Genesis authorization failed.")
        print("        Genesis is a solemn, once-in-a-lifetime ceremony that permanently")
        print("        binds this instance's cryptographic identity root to its origin commit.")
        print()
        print("        To execute, you must explicitly pass: --confirm-genesis")
        print("======================================================================")
        return 2

    ws_dir = Path(parsed.workspace_dir).resolve() if parsed.workspace_dir else Path.cwd()
    c_path = Path(parsed.commitment_path).resolve() if parsed.commitment_path else None
    p_path = Path(parsed.profile_path).resolve() if parsed.profile_path else None

    print(f"Target Workspace: {ws_dir}")
    print(f"User Name:        {parsed.user_name}")
    print(f"Companion Name:   {parsed.companion_name}")
    print("Executing canonical operator Genesis protocol...")
    print("----------------------------------------------------------------------")

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
        print("[SUCCESS] Canonical Genesis successfully executed and cryptographically sealed.")
        print(f"  Instance UUID:     {commitment.record.identity_anchor.instance_uuid}")
        print(f"  Born At:           {commitment.record.identity_anchor.born_at}")
        print(f"  Genesis Commit:    {commitment.record.identity_anchor.genesis_commit}")
        print(f"  Genesis Root Hash: {commitment.genesis_root_hash}")
        print("======================================================================")
        print("Lucia is now BORN (OntologyState.BORN).")
        print("Next step: First Activation (POST /lifecycle/activate) to enter ACTIVE state.")
        print("======================================================================")
        return 0

    except (ReGenesisForbiddenError, TerminalLifecycleError, OperatorPreconditionError) as exc:
        print(f"[PRECONDITION ERROR] Genesis refused: {exc}", file=sys.stderr)
        return 1
    except OperatorGenesisError as exc:
        print(f"[GENESIS FAILURE] Operator Genesis failed: {exc}", file=sys.stderr)
        return 1
    except Exception as exc:
        print(f"[FATAL UNEXPECTED ERROR] {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())
