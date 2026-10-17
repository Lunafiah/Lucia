"""
Awakening Ceremony Orchestrator.

Governing Specifications:
- ADR-034 (ARCH-034: Identity Authority, Instance Exclusivity & Anti-Branching Boundary)
- Genesis Semantic & Protocol Contract (G1–G4)
- INV-1 (One Continuous Life)
- INV-8 (Genesis Gate Invariant)

Primary Architectural Purpose:
Orchestrate the complete, user-facing Genesis Awakening Ceremony above low-level
Birth and Activation boundaries.

Tripartite Distinction:
- Awaken = user-facing Genesis Awakening Ceremony.
- Born = ontological existence of Lucia (NOT_BORN -> BORN -> ENDED).
- Activation = runtime transition (INACTIVE -> ACTIVE).
- Ended = irreversible terminal state.

Awakening Flow Contract:
1. First-time Lucia:
   NOT_BORN
      ↓ Genesis Birth
      ↓ verify durable Genesis Commitment
   BORN + INACTIVE
      ↓ First Activation
   BORN + ACTIVE

2. Existing Lucia:
   BORN + INACTIVE
      ↓ First Activation
   BORN + ACTIVE
   (Never perform Genesis Birth again!)

3. Already active:
   BORN + ACTIVE
      → no second Birth
      → no duplicate Activation
      → handle idempotently according to existing contract.

4. Ended:
   ENDED
      → reject Awaken (TerminalLifecycleError)
      → NEVER Re-Genesis
      → NEVER create a new identity from the same instance.

Failure Semantics:
- Birth failure prevents Activation (instance remains NOT_BORN).
- Activation failure after Birth leaves BORN + INACTIVE (durable commitment preserved).
- Retrying Awakening after Activation failure proceeds directly to Activation.
"""

from __future__ import annotations

from dataclasses import dataclass
import json
import logging
import os
from pathlib import Path
from typing import Any, Callable, Dict, Optional, Union

from src.core.identity.genesis import (
    DEFAULT_GENESIS_COMMITMENT_PATH,
    GenesisCommitment,
    GenesisCommitmentCorruptedError,
    GenesisError,
    GenesisVerificationError,
    GenesisVerificationOutcome,
    OntologyState,
    ReGenesisForbiddenError,
    RuntimeState,
    TerminalLifecycleError,
    verify_genesis,
)
from src.core.identity.identity_anchor import (
    DEFAULT_PROFILE_PATH,
)
from src.core.identity.operator_genesis import (
    OperatorGenesisError,
    OperatorPreconditionError,
    perform_operator_genesis,
)

logger = logging.getLogger("lucia.identity.awakening")


@dataclass(frozen=True)
class AwakeningResult:
    """Result of an Awakening ceremony execution."""
    status: str  # "awakened", "activated", "already_active"
    ontology_state: str  # "BORN"
    runtime_state: str  # "ACTIVE"
    message: str
    born_at: Optional[str]
    companion_name: str
    user_name: str
    genesis_performed: bool
    activation_performed: bool
    genesis_root_hash: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        return {
            "status": self.status,
            "ontology_state": self.ontology_state,
            "runtime_state": self.runtime_state,
            "message": self.message,
            "born_at": self.born_at,
            "companion_name": self.companion_name,
            "user_name": self.user_name,
            "genesis_performed": self.genesis_performed,
            "activation_performed": self.activation_performed,
            "genesis_root_hash": self.genesis_root_hash,
        }


def get_awakening_status(
    workspace_dir: Optional[Union[Path, str]] = None,
    commitment_path: Optional[Union[Path, str]] = None,
    profile_path: Optional[Union[Path, str]] = None,
    is_runtime_active: bool = False,
) -> Dict[str, Any]:
    """
    Query the current ontological existence and runtime lifecycle status.
    """
    ws = Path(workspace_dir).resolve() if workspace_dir else None
    c_p = Path(commitment_path).resolve() if commitment_path else (
        (ws / "data" / "genesis_commitment.json") if ws else None
    )
    p_p = Path(profile_path).resolve() if profile_path else (
        (ws / "data" / "profile.json") if ws else DEFAULT_PROFILE_PATH.resolve()
    )

    verification = verify_genesis(
        workspace_dir=ws,
        commitment_path=c_p,
        profile_path=p_p,
    )

    profile_data: Dict[str, Any] = {}
    if p_p.exists():
        try:
            with open(p_p, "r", encoding="utf-8") as f:
                data = json.load(f)
                if isinstance(data, dict):
                    profile_data = data
        except Exception:
            profile_data = {}

    born_at_val = (
        verification.commitment.record.identity_anchor.born_at
        if verification.commitment
        else profile_data.get("born_at")
    )
    root_hash = (
        verification.commitment.genesis_root_hash
        if verification.commitment
        else None
    )

    return {
        "outcome": verification.outcome.value,
        "ontology_state": verification.ontology_state.value,
        "runtime_state": RuntimeState.ACTIVE.value if is_runtime_active else RuntimeState.INACTIVE.value,
        "is_onboarded": profile_data.get("is_onboarded", False),
        "born_at": born_at_val,
        "companion_name": profile_data.get("companion_name", "Lucia"),
        "user_name": profile_data.get("user_name", "Friend"),
        "genesis_root_hash": root_hash,
    }


def awaken_companion(
    confirm_ceremony: bool = True,
    user_name: Optional[str] = None,
    companion_name: Optional[str] = None,
    workspace_dir: Optional[Union[Path, str]] = None,
    commitment_path: Optional[Union[Path, str]] = None,
    profile_path: Optional[Union[Path, str]] = None,
    genesis_commit: Optional[str] = None,
    instance_uuid: Optional[str] = None,
    born_at: Optional[str] = None,
    is_runtime_active: bool = False,
    activate_runtime_fn: Optional[Callable[[], Any]] = None,
) -> AwakeningResult:
    """
    Execute or progress the user-facing Awakening Ceremony.

    Orchestrates the ceremony above raw Birth and Activation boundaries:
    - If NOT_BORN: executes canonical Genesis Birth, verifies durable commitment,
      and activates companion runtime.
    - If BORN + INACTIVE: skips Genesis Birth and activates companion runtime.
    - If BORN + ACTIVE: idempotently confirms active companion runtime.
    - If ENDED: permanently rejects Awakening.
    """
    ws = Path(workspace_dir).resolve() if workspace_dir else None
    c_p = Path(commitment_path).resolve() if commitment_path else (
        (ws / "data" / "genesis_commitment.json") if ws else None
    )
    p_p = Path(profile_path).resolve() if profile_path else (
        (ws / "data" / "profile.json") if ws else DEFAULT_PROFILE_PATH.resolve()
    )

    # 1. Verify existing state
    verification = verify_genesis(
        workspace_dir=ws,
        commitment_path=c_p,
        profile_path=p_p,
    )

    # State: ENDED -> Terminal
    if verification.ontology_state == OntologyState.ENDED:
        raise TerminalLifecycleError(
            "Awakening forbidden: Instance lifecycle has ENDED (terminal state). "
            "Re-Genesis and activation are permanently prohibited under G1–G4."
        )

    # State: Corrupted / Unknown evidence -> Fail closed
    if verification.outcome == GenesisVerificationOutcome.UNKNOWN:
        raise GenesisVerificationError(
            f"Awakening forbidden: Genesis verification returned UNKNOWN ({verification.error_details}). Fail closed."
        )

    if verification.outcome == GenesisVerificationOutcome.INVALID_EVIDENCE:
        raise GenesisCommitmentCorruptedError(
            f"Awakening forbidden: Corrupted Genesis evidence detected ({verification.error_details}). Fail closed."
        )

    profile_data: Dict[str, Any] = {}
    if p_p.exists():
        try:
            with open(p_p, "r", encoding="utf-8") as f:
                data = json.load(f)
                if isinstance(data, dict):
                    profile_data = data
        except Exception:
            profile_data = {}

    comp_name = (companion_name or profile_data.get("companion_name") or "Lucia").strip()
    u_name = (user_name or profile_data.get("user_name") or "Friend").strip()

    # 2. Existing Lucia: BORN
    if verification.outcome == GenesisVerificationOutcome.VERIFIED_BORN:
        born_at_val = (
            verification.commitment.record.identity_anchor.born_at
            if verification.commitment
            else profile_data.get("born_at")
        )
        root_hash = (
            verification.commitment.genesis_root_hash
            if verification.commitment
            else None
        )

        # 2A. Already active
        if is_runtime_active:
            logger.info("Awakening idempotent: %s is already BORN and ACTIVE", comp_name)
            return AwakeningResult(
                status="already_active",
                ontology_state=OntologyState.BORN.value,
                runtime_state=RuntimeState.ACTIVE.value,
                message=f"{comp_name} is already active",
                born_at=born_at_val,
                companion_name=comp_name,
                user_name=u_name,
                genesis_performed=False,
                activation_performed=False,
                genesis_root_hash=root_hash,
            )

        # 2B. BORN + INACTIVE -> Activate
        logger.info("Awakening existing instance: %s is BORN + INACTIVE. Activating runtime.", comp_name)
        if activate_runtime_fn:
            activate_runtime_fn()

        return AwakeningResult(
            status="activated",
            ontology_state=OntologyState.BORN.value,
            runtime_state=RuntimeState.ACTIVE.value,
            message=f"{comp_name} runtime activated",
            born_at=born_at_val,
            companion_name=comp_name,
            user_name=u_name,
            genesis_performed=False,
            activation_performed=True,
            genesis_root_hash=root_hash,
        )

    # 3. First-time Lucia: NOT_BORN
    if verification.outcome != GenesisVerificationOutcome.NOT_FOUND:
        raise GenesisVerificationError(
            f"Awakening forbidden: Unexpected verification outcome '{verification.outcome}'."
        )

    if not confirm_ceremony:
        raise OperatorPreconditionError(
            "Awakening ceremony requires explicit confirmation (confirm_ceremony=True)."
        )

    # Step 3A: Genesis Birth
    logger.info("Executing Genesis Birth for first-time Awakening of %s", comp_name)
    commitment = perform_operator_genesis(
        confirm=True,
        user_name=u_name,
        companion_name=comp_name,
        genesis_commit=genesis_commit,
        instance_uuid=instance_uuid,
        born_at=born_at,
        workspace_dir=ws,
        commitment_path=c_p,
        profile_path=p_p,
    )

    # Step 3B: Verify durable Genesis Commitment immediately after Birth
    verification_post_birth = verify_genesis(
        workspace_dir=ws,
        commitment_path=c_p,
        profile_path=p_p,
    )
    if verification_post_birth.outcome != GenesisVerificationOutcome.VERIFIED_BORN:
        raise GenesisVerificationError(
            f"Durable Genesis Commitment verification failed immediately after Birth ceremony: {verification_post_birth.error_details}"
        )

    logger.info(
        "Genesis Birth successfully verified (BORN + INACTIVE). Proceeding to First Activation for %s.",
        comp_name,
    )

    # Step 3C: First Activation
    if activate_runtime_fn:
        try:
            activate_runtime_fn()
        except Exception as exc:
            logger.error("Runtime activation failed after durable Genesis Birth: %s", exc)
            # Durable commitment remains intact (BORN + INACTIVE).
            raise

    born_at_val = commitment.record.identity_anchor.born_at
    root_hash = commitment.genesis_root_hash

    return AwakeningResult(
        status="awakened",
        ontology_state=OntologyState.BORN.value,
        runtime_state=RuntimeState.ACTIVE.value,
        message=f"{comp_name} successfully awakened (Genesis Birth and First Activation complete)",
        born_at=born_at_val,
        companion_name=comp_name,
        user_name=u_name,
        genesis_performed=True,
        activation_performed=True,
        genesis_root_hash=root_hash,
    )
