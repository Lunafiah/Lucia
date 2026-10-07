"""
Workspace Provenance & Environment Verification (WP-03).

Governing ADR: ADR-034 (ARCH-034: Identity Authority, Instance Exclusivity & Anti-Branching Boundary).
Reference Specification: docs/others/IDENTITY_AUTHORITY_SPECIFICATION/IDENTITY_AUTHORITY_SPEC_V01.md
Reference Plan: docs/others/IDENTITY_AUTHORITY_SPECIFICATION/IMPLEMENTATION_PLAN.md

Primary Architectural Purpose:
Detect workspace copying, unauthorized cross-machine replication, and hardware replacements
while providing a solemn, recovery-gated reconfirmation workflow that guarantees non-destructive
fail-safe operation.

Classification of Threat Vectors (ADR-034 §2.4):
- Same-Directory Dual Launch:
    Protected (WP-01 OS Kernel File Lock).
- Copied Workspace (data/ or folder duplication on same host):
    Detected / High-Friction — only where workspace divergence is detectable by the defined mechanism
    (Canonical Workspace Path check in profile.json).
- Cross-Machine Unauthorized Copy:
    Detected / Recovery-Gated (Soft Hardware Binding mismatch).
- Authorized Hardware Replacement:
    Detected / Recovery-Gated (Soft Hardware Reconfirmation state machine).
- Clock Rollback:
    Protected against ordinary wall-clock rollback; snapshot restoration remains unresolved
    (Rolling monotonic epoch & wall-clock monotonicity checks).
- Storage Snapshot / VM Rollback:
    Unsolved (Inherent limit of offline local storage and virtualization).
- Deliberate Offline Cloning:
    Unsolved (Offline Clone Paradox; root administrator offline environment copying).

Epistemic Honesty Standard (ADR-034 §2.4.2):
The mechanisms herein are anti-accident, tamper-evident, and high-friction structural defenses.
No claim of absolute cryptographic anti-cloning is made.

Boundary & Invariant Guarantees:
- INV-1 (One Continuous Life): Detects split-brain branching vectors.
- INV-5 (Zero Cloud Dependencies): 100% offline local edge verification; zero telemetry or network calls.
- INV-8 (Genesis Gate Invariant): Live `data/profile.json` remains bit-exact `{"is_onboarded": false}`.
  Un-onboarded profiles are Genesis-locked; provenance checks return GENESIS_LOCKED without disk mutation.
- Fail-Safe & Non-Destructive: Hardware divergence pauses and prompts; never deletes user data.
- WP-01 Ordering: Instance authority must be acquired before provenance/environment verification.
"""

from __future__ import annotations

import copy
from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum
import hashlib
import json
import logging
import os
from pathlib import Path
import platform
import sys
from typing import Any, Callable, Dict, Optional, Tuple, Union
import uuid

from src.core.identity.identity_anchor import (
    DEFAULT_PROFILE_PATH,
    guard_immutable_fields,
    validate_profile_identity,
)

logger = logging.getLogger("lucia.identity.provenance")

DEFAULT_HARDWARE_SALT: str = "lucia-hardware-digest-v1"
DEFAULT_EPOCH_MANIFEST_PATH: Path = Path("data/epoch_manifest.json")


# ---------------------------------------------------------------------------
# Threat & Status Classifications (ADR-034 §2.4)
# ---------------------------------------------------------------------------

class ThreatClassification(str, Enum):
    """Canonical defense classifications codified in ADR-034."""
    PROTECTED = "Protected"
    DETECTED_RECOVERY_GATED = "Detected / Recovery-Gated"
    DETECTED_HIGH_FRICTION = "Detected / High-Friction"
    UNSOLVED = "Unsolved"


class ProvenanceVerificationStatus(str, Enum):
    """Outcome status of provenance and environment verification."""
    VALID = "VALID"
    GENESIS_LOCKED = "GENESIS_LOCKED"
    WORKSPACE_DIVERGENCE = "WORKSPACE_DIVERGENCE"
    AWAITING_HARDWARE_RECONFIRMATION = "AWAITING_HARDWARE_RECONFIRMATION"
    WALL_CLOCK_ROLLBACK_DETECTED = "WALL_CLOCK_ROLLBACK_DETECTED"
    MISSING_AUTHORITY_BINDING = "MISSING_AUTHORITY_BINDING"


# ---------------------------------------------------------------------------
# Exceptions
# ---------------------------------------------------------------------------

class ProvenanceError(RuntimeError):
    """Base exception for all provenance and environment verification errors."""
    pass


class WorkspaceLocationDivergenceNotice(ProvenanceError):
    """
    Raised when the executing workspace path diverges from the recorded canonical path.

    Classification: Detected / High-Friction — only where workspace divergence is detectable
    by the defined mechanism.
    """
    pass


class HardwareEnvironmentDivergenceError(ProvenanceError):
    """
    Raised when current hardware digest does not match the bound machine digest.

    Classification: Detected / Recovery-Gated.
    """
    pass


class ClockDiscontinuityError(ProvenanceError):
    """
    Raised when system wall-clock rollback is detected relative to recorded checkpoints.

    Classification: Protected against ordinary wall-clock rollback; snapshot restoration remains unresolved.
    """
    pass


class HardwareReconfirmationRequiredError(ProvenanceError):
    """
    Raised when the engine enters AWAITING_HARDWARE_RECONFIRMATION modal state.
    """
    pass


# ---------------------------------------------------------------------------
# Domain Models & Hardware Components
# ---------------------------------------------------------------------------

@dataclass(frozen=True)
class HardwareDigestComponents:
    """
    Multi-component raw hardware identifiers collected from the local host.

    Components:
    - machine_guid: OS machine GUID (Windows registry or Linux machine-id or fallback node)
    - smbios_uuid: SMBIOS UUID or motherboard identifier
    - volume_serial: Primary workspace volume serial number
    - cpu_info: Processor family, model string, and logical core count
    - platform_str: Platform and OS kernel descriptor
    """

    machine_guid: str
    smbios_uuid: str
    volume_serial: str
    cpu_info: str
    platform_str: str

    def to_dict(self) -> Dict[str, str]:
        return {
            "machine_guid": self.machine_guid,
            "smbios_uuid": self.smbios_uuid,
            "volume_serial": self.volume_serial,
            "cpu_info": self.cpu_info,
            "platform_str": self.platform_str,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "HardwareDigestComponents":
        return cls(
            machine_guid=str(data.get("machine_guid", "")),
            smbios_uuid=str(data.get("smbios_uuid", "")),
            volume_serial=str(data.get("volume_serial", "")),
            cpu_info=str(data.get("cpu_info", "")),
            platform_str=str(data.get("platform_str", "")),
        )


@dataclass(frozen=True)
class AuthorityBinding:
    """
    Authority and provenance binding block stored in data/profile.json.

    Corresponds to ADR-034 §5.1 / Spec v0.1 §5.1.
    """

    hardware_binding_mode: str = "SOFT_WARNING"
    bound_machine_guid_digest: str = ""
    activation_host_platform: str = ""
    last_known_canonical_path: str = ""
    hardware_migration_epoch: int = 0
    last_verified_at: Optional[str] = None
    component_digests: Optional[Dict[str, str]] = None

    def to_dict(self) -> Dict[str, Any]:
        result: Dict[str, Any] = {
            "hardware_binding_mode": self.hardware_binding_mode,
            "bound_machine_guid_digest": self.bound_machine_guid_digest,
            "activation_host_platform": self.activation_host_platform,
            "last_known_canonical_path": self.last_known_canonical_path,
            "hardware_migration_epoch": self.hardware_migration_epoch,
        }
        if self.last_verified_at:
            result["last_verified_at"] = self.last_verified_at
        if self.component_digests:
            result["component_digests"] = self.component_digests
        return result

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "AuthorityBinding":
        return cls(
            hardware_binding_mode=str(data.get("hardware_binding_mode", "SOFT_WARNING")),
            bound_machine_guid_digest=str(data.get("bound_machine_guid_digest", "")),
            activation_host_platform=str(data.get("activation_host_platform", "")),
            last_known_canonical_path=str(data.get("last_known_canonical_path", "")),
            hardware_migration_epoch=int(data.get("hardware_migration_epoch", 0)),
            last_verified_at=data.get("last_verified_at"),
            component_digests=data.get("component_digests"),
        )


@dataclass(frozen=True)
class ProvenanceVerificationResult:
    """Comprehensive result of provenance and environment verification."""

    status: ProvenanceVerificationStatus
    is_valid: bool
    is_genesis_locked: bool
    workspace_path: Path
    recorded_workspace_path: Optional[str]
    current_hardware_digest: str
    bound_hardware_digest: Optional[str]
    hardware_matched: bool
    workspace_matched: bool
    clock_monotonic: bool
    divergence_details: Optional[str] = None
    threat_classifications: Dict[str, str] = field(default_factory=dict)


# ---------------------------------------------------------------------------
# Hardware Identifier Retrieval & Digest Derivation
# ---------------------------------------------------------------------------

def collect_hardware_components(
    workspace_path: Optional[Union[Path, str]] = None,
) -> HardwareDigestComponents:
    """
    Collect local hardware identifiers via non-blocking, offline system APIs.

    Guarantees:
    - 100% offline edge execution (INV-5).
    - Zero external network requests or cloud telemetry.
    - Zero subprocess hangs (uses direct OS APIs or registry with robust fallbacks).
    - Non-destructive and safe on all operating systems.
    """
    platform_desc = platform.platform()
    cpu_desc = f"{platform.processor()}|cores:{os.cpu_count() or 1}"

    machine_guid = ""
    smbios_uuid = ""
    volume_serial = ""

    # 1. Machine GUID retrieval
    if sys.platform == "win32":
        try:
            import winreg  # type: ignore[import-not-found]
            with winreg.OpenKey(
                winreg.HKEY_LOCAL_MACHINE, r"SOFTWARE\Microsoft\Cryptography"
            ) as key:
                machine_guid, _ = winreg.QueryValueEx(key, "MachineGuid")
        except Exception as exc:
            logger.debug("winreg MachineGuid query failed: %s", exc)
    else:
        # Linux / POSIX machine-id
        for candidate in (Path("/etc/machine-id"), Path("/var/lib/dbus/machine-id")):
            if candidate.exists():
                try:
                    machine_guid = candidate.read_text(encoding="utf-8").strip()
                    if machine_guid:
                        break
                except Exception:
                    pass

    if not machine_guid:
        # Deterministic node fallback
        machine_guid = hex(uuid.getnode())

    # 2. SMBIOS / Baseboard identification
    if sys.platform == "win32":
        try:
            import winreg  # type: ignore[import-not-found]
            with winreg.OpenKey(
                winreg.HKEY_LOCAL_MACHINE, r"HARDWARE\DESCRIPTION\System\BIOS"
            ) as key:
                product_name, _ = winreg.QueryValueEx(key, "SystemProductName")
                board_prod, _ = winreg.QueryValueEx(key, "BaseBoardProduct")
                smbios_uuid = f"{product_name}:{board_prod}"
        except Exception as exc:
            logger.debug("winreg BIOS query failed: %s", exc)

    if not smbios_uuid:
        # Linux DMI fallback
        dmi_uuid_file = Path("/sys/class/dmi/id/product_uuid")
        if dmi_uuid_file.exists():
            try:
                smbios_uuid = dmi_uuid_file.read_text(encoding="utf-8").strip()
            except Exception:
                pass

    if not smbios_uuid:
        smbios_uuid = platform.node() or "default-smbios-node"

    # 3. Volume Serial Number
    ws_target = Path(workspace_path).resolve() if workspace_path else Path.cwd().resolve()
    if sys.platform == "win32":
        try:
            import ctypes
            drive_letter = os.path.splitdrive(str(ws_target))[0] + "\\"
            vol_serial = ctypes.c_ulong()
            success = ctypes.windll.kernel32.GetVolumeInformationW(
                ctypes.c_wchar_p(drive_letter),
                None,
                0,
                ctypes.byref(vol_serial),
                None,
                None,
                None,
                0,
            )
            if success:
                volume_serial = hex(vol_serial.value)
        except Exception as exc:
            logger.debug("kernel32 GetVolumeInformationW failed: %s", exc)

    if not volume_serial:
        try:
            st = os.stat(str(ws_target))
            volume_serial = hex(getattr(st, "st_dev", 0))
        except Exception:
            volume_serial = "vol-0000"

    return HardwareDigestComponents(
        machine_guid=str(machine_guid).strip(),
        smbios_uuid=str(smbios_uuid).strip(),
        volume_serial=str(volume_serial).strip(),
        cpu_info=str(cpu_desc).strip(),
        platform_str=str(platform_desc).strip(),
    )


def compute_hardware_digest(
    components: Optional[HardwareDigestComponents] = None,
    salt: str = DEFAULT_HARDWARE_SALT,
) -> str:
    """
    Compute salted SHA-256 multi-component hardware digest.

    Formula (Spec v0.1 §7.2 / Plan WP-03):
        H_hw = SHA256(salt || MachineGuid || SMBIOS UUID || Volume Serial || CPU info)
    """
    comps = components or collect_hardware_components()
    raw_payload = (
        f"{salt}:"
        f"{comps.machine_guid}:"
        f"{comps.smbios_uuid}:"
        f"{comps.volume_serial}:"
        f"{comps.cpu_info}"
    )
    return hashlib.sha256(raw_payload.encode("utf-8")).hexdigest()


def compute_component_digests(
    components: HardwareDigestComponents,
) -> Dict[str, str]:
    """Compute individual SHA-256 digests for individual hardware components."""
    return {
        "machine_guid": hashlib.sha256(components.machine_guid.encode("utf-8")).hexdigest(),
        "smbios_uuid": hashlib.sha256(components.smbios_uuid.encode("utf-8")).hexdigest(),
        "volume_serial": hashlib.sha256(components.volume_serial.encode("utf-8")).hexdigest(),
        "cpu_info": hashlib.sha256(components.cpu_info.encode("utf-8")).hexdigest(),
    }


# ---------------------------------------------------------------------------
# Path Normalization & Canonical Comparison
# ---------------------------------------------------------------------------

def normalize_workspace_path(path: Union[Path, str]) -> str:
    """
    Return canonical absolute normalized workspace path string.

    On Windows: Resolves drive letters, normalizes slashes, and maintains clean format.
    """
    resolved = Path(path).resolve()
    return str(resolved)


def are_workspace_paths_equal(
    path_a: Union[Path, str],
    path_b: Union[Path, str],
) -> bool:
    """
    Compare two workspace paths for equivalence under host filesystem semantics.

    On Windows: Case-insensitive drive and path comparison.
    On POSIX: Strict case-sensitive comparison.
    """
    p1 = Path(path_a).resolve()
    p2 = Path(path_b).resolve()

    if sys.platform == "win32":
        return str(p1).lower() == str(p2).lower()
    return str(p1) == str(p2)


# ---------------------------------------------------------------------------
# Wall-Clock Monotonicity Check
# ---------------------------------------------------------------------------

def check_wall_clock_monotonicity(
    profile_data: Dict[str, Any],
    epoch_manifest_path: Optional[Union[Path, str]] = None,
    current_utc: Optional[datetime] = None,
) -> Tuple[bool, Optional[str]]:
    """
    Detect ordinary wall-clock rollback against recorded checkpoint timestamps.

    Checks:
    - profile.json identity_anchor.born_at
    - profile.json phylogenetic_lineage.last_upgraded_at
    - profile.json authority_binding.last_verified_at
    - data/epoch_manifest.json t_checkpoint (ADR-033)

    Returns:
    (True, None) if system clock is forward of all checkpoints.
    (False, details) if current clock is earlier than a known historical timestamp.
    """
    now = current_utc or datetime.now(timezone.utc)
    now_ts = now.timestamp()

    # 1. Check profile timestamps
    timestamps_to_check: list[Tuple[str, str]] = []

    anchor = profile_data.get("identity_anchor")
    if isinstance(anchor, dict) and anchor.get("born_at"):
        timestamps_to_check.append(("identity_anchor.born_at", str(anchor["born_at"])))

    lineage = profile_data.get("phylogenetic_lineage")
    if isinstance(lineage, dict) and lineage.get("last_upgraded_at"):
        timestamps_to_check.append(("phylogenetic_lineage.last_upgraded_at", str(lineage["last_upgraded_at"])))

    authority = profile_data.get("authority_binding")
    if isinstance(authority, dict) and authority.get("last_verified_at"):
        timestamps_to_check.append(("authority_binding.last_verified_at", str(authority["last_verified_at"])))

    for label, ts_str in timestamps_to_check:
        try:
            iso_str = ts_str.replace("Z", "+00:00")
            dt = datetime.fromisoformat(iso_str)
            if now < dt:
                return (
                    False,
                    f"System wall-clock rollback detected: current UTC time ({now.isoformat()}) "
                    f"is earlier than recorded {label} ({ts_str}).",
                )
        except Exception:
            pass

    # 2. Check epoch_manifest.json t_checkpoint if present
    man_path = Path(epoch_manifest_path) if epoch_manifest_path else DEFAULT_EPOCH_MANIFEST_PATH
    if man_path.exists():
        try:
            with open(man_path, "r", encoding="utf-8") as f:
                man_data = json.load(f)
            t_checkpoint = man_data.get("t_checkpoint")
            if t_checkpoint is not None:
                checkpoint_val = float(t_checkpoint)
                # Allow minor clock jitter threshold (5.0s) for rapid restart edge cases
                if now_ts < (checkpoint_val - 5.0):
                    return (
                        False,
                        f"System wall-clock rollback detected: current time ({now_ts}) "
                        f"is earlier than epoch manifest checkpoint ({checkpoint_val}).",
                    )
        except Exception as exc:
            logger.debug("Could not verify epoch manifest timestamp: %s", exc)

    return (True, None)


# ---------------------------------------------------------------------------
# High-Gravity Identity Notice Generator
# ---------------------------------------------------------------------------

def format_high_gravity_hardware_notice() -> str:
    """Format the solemn High-Gravity Identity Notice specified in Spec v0.1 §7.3."""
    return (
        "================================================================================\n"
        "HIGH-GRAVITY IDENTITY NOTICE: HARDWARE DIVERGENCE DETECTED\n"
        "================================================================================\n"
        "Lucia has detected that she is running on a new computer or modified hardware profile.\n"
        "To prevent split-brain identity branching (INV-1), you must confirm:\n\n"
        "  [A] This is a legitimate hardware upgrade or disaster recovery.\n"
        "      (The old machine/instance is permanently decommissioned).\n"
        "  [B] Cancel and close (I accidentally copied this folder).\n\n"
        "Selection required. Without confirmation, startup halts immediately.\n"
        "================================================================================"
    )


# ---------------------------------------------------------------------------
# Hardware Reconfirmation State Mutation (Non-Destructive)
# ---------------------------------------------------------------------------

def reconfirm_hardware_environment(
    profile_path: Optional[Union[Path, str]] = None,
    current_workspace_path: Optional[Union[Path, str]] = None,
    hardware_components: Optional[HardwareDigestComponents] = None,
    salt: str = DEFAULT_HARDWARE_SALT,
) -> Dict[str, Any]:
    """
    Execute authorized, non-destructive hardware reconfirmation.

    Execution contract (Spec v0.1 §7.3):
    1. Updates bound_machine_guid_digest to current hardware digest H_current.
    2. Increments hardware_migration_epoch.
    3. Updates last_known_canonical_path to current workspace path.
    4. Updates activation_host_platform to current platform.
    5. Sets last_verified_at to current UTC ISO timestamp.
    6. Verifies guard_immutable_fields to guarantee identity_anchor is bit-exact.
    7. Atomically persists changes to profile.json.

    Returns the updated profile dictionary.
    """
    target = Path(profile_path) if profile_path else DEFAULT_PROFILE_PATH
    if not target.exists():
        raise ProvenanceError(f"Cannot reconfirm hardware: profile file '{target}' does not exist.")

    with open(target, "r", encoding="utf-8") as f:
        existing_profile = json.load(f)

    if not isinstance(existing_profile, dict):
        raise ProvenanceError(f"Invalid profile content in '{target}': expected JSON object.")

    if not existing_profile.get("is_onboarded", False):
        raise ProvenanceError("Cannot reconfirm hardware on an un-onboarded / pre-Genesis profile.")

    comps = hardware_components or collect_hardware_components(current_workspace_path)
    new_digest = compute_hardware_digest(comps, salt=salt)
    comp_digests = compute_component_digests(comps)

    updated_profile = copy.deepcopy(existing_profile)
    auth_block = updated_profile.setdefault("authority_binding", {})
    if not isinstance(auth_block, dict):
        auth_block = {}
        updated_profile["authority_binding"] = auth_block

    current_epoch = int(auth_block.get("hardware_migration_epoch", 0))
    auth_block["hardware_migration_epoch"] = current_epoch + 1
    auth_block["bound_machine_guid_digest"] = new_digest
    auth_block["activation_host_platform"] = comps.platform_str
    auth_block["component_digests"] = comp_digests
    auth_block["last_verified_at"] = datetime.now(timezone.utc).isoformat()

    ws_norm = normalize_workspace_path(current_workspace_path or Path.cwd())
    auth_block["last_known_canonical_path"] = ws_norm

    # Also synchronize root-level fields if present
    if "last_known_canonical_path" in updated_profile:
        updated_profile["last_known_canonical_path"] = ws_norm

    # Critical Safety: Guard immutable identity anchor fields from WP-02
    guard_immutable_fields(existing_profile, updated_profile)

    # Atomic write
    tmp_path = target.with_suffix(".tmp")
    with open(tmp_path, "w", encoding="utf-8") as f:
        json.dump(updated_profile, f, indent=2)
    tmp_path.replace(target)

    logger.info(
        "Hardware authority reconfirmed: new_digest=%s..., migration_epoch=%d, canonical_path=%s",
        new_digest[:12],
        auth_block["hardware_migration_epoch"],
        ws_norm,
    )
    return updated_profile


# ---------------------------------------------------------------------------
# Core Provenance Verification Engine
# ---------------------------------------------------------------------------

def verify_provenance_and_environment(
    workspace_path: Optional[Union[Path, str]] = None,
    profile_path: Optional[Union[Path, str]] = None,
    epoch_manifest_path: Optional[Union[Path, str]] = None,
    hardware_components_override: Optional[HardwareDigestComponents] = None,
    salt: str = DEFAULT_HARDWARE_SALT,
    allow_reconfirmation: bool = False,
    reconfirm_callback: Optional[Callable[[], bool]] = None,
    current_utc: Optional[datetime] = None,
) -> ProvenanceVerificationResult:
    """
    Execute comprehensive provenance and environment verification.

    Startup Sequence Ordering (ADR-034 / IMPLEMENTATION_PLAN.md):
        Acquire OS Lock (WP-01) -> Validate Identity Anchor (WP-02) -> Verify Provenance (WP-03)

    Threat Classification Mapping:
    - Same-Directory Execution: Protected
    - Workspace Path Divergence: Detected / High-Friction — only where workspace divergence is detectable
    - Cross-Machine Digest Mismatch: Detected / Recovery-Gated
    - System Clock Rollback: Protected against ordinary wall-clock rollback; snapshot restoration remains unresolved
    - Snapshot / VM Rollback: Unsolved
    - Deliberate Offline Cloning: Unsolved (Offline Clone Paradox)

    Execution Behavior:
    1. If profile does not exist or is un-onboarded ({"is_onboarded": false}):
       Returns status=GENESIS_LOCKED without writing any files or synthesizing digests.
    2. If profile is onboarded, validates authority_binding block.
    3. Checks workspace path anchoring. If diverged -> WORKSPACE_DIVERGENCE.
    4. Checks soft hardware digest. If diverged:
       - If allow_reconfirmation or reconfirm_callback() is True: executes non-destructive reconfirmation.
       - Else: enters AWAITING_HARDWARE_RECONFIRMATION.
    5. Checks system wall-clock monotonicity. If rollback detected -> WALL_CLOCK_ROLLBACK_DETECTED.
    """
    ws = Path(workspace_path).resolve() if workspace_path else Path.cwd().resolve()
    target_profile = Path(profile_path) if profile_path else DEFAULT_PROFILE_PATH

    threat_classifications: Dict[str, str] = {
        "Same-Directory Dual Launch": ThreatClassification.PROTECTED.value,
        "Copied Workspace": ThreatClassification.DETECTED_HIGH_FRICTION.value,
        "Cross-Machine Unauthorized Copy": ThreatClassification.DETECTED_RECOVERY_GATED.value,
        "Authorized Hardware Replacement": ThreatClassification.DETECTED_RECOVERY_GATED.value,
        "Clock Rollback": "Protected against ordinary wall-clock rollback; snapshot restoration remains unresolved",
        "Storage Snapshot / VM Rollback": ThreatClassification.UNSOLVED.value,
        "Deliberate Offline Cloning": "Unsolved (Offline Clone Paradox)",
    }

    # Step 1: Handle non-existent profile (Pre-Genesis)
    if not target_profile.exists():
        return ProvenanceVerificationResult(
            status=ProvenanceVerificationStatus.GENESIS_LOCKED,
            is_valid=True,
            is_genesis_locked=True,
            workspace_path=ws,
            recorded_workspace_path=None,
            current_hardware_digest="",
            bound_hardware_digest=None,
            hardware_matched=True,
            workspace_matched=True,
            clock_monotonic=True,
            divergence_details="Profile does not exist. Pre-Genesis mode.",
            threat_classifications=threat_classifications,
        )

    try:
        with open(target_profile, "r", encoding="utf-8") as f:
            profile_data = json.load(f)
    except Exception as exc:
        raise ProvenanceError(f"Failed to read profile at '{target_profile}': {exc}") from exc

    if not isinstance(profile_data, dict):
        raise ProvenanceError(f"Profile file '{target_profile}' does not contain a JSON dictionary.")

    # Step 2: Handle Pre-Genesis locked profile
    if not profile_data.get("is_onboarded", False):
        return ProvenanceVerificationResult(
            status=ProvenanceVerificationStatus.GENESIS_LOCKED,
            is_valid=True,
            is_genesis_locked=True,
            workspace_path=ws,
            recorded_workspace_path=None,
            current_hardware_digest="",
            bound_hardware_digest=None,
            hardware_matched=True,
            workspace_matched=True,
            clock_monotonic=True,
            divergence_details="Genesis gate is LOCKED (un-onboarded profile).",
            threat_classifications=threat_classifications,
        )

    # Step 3: Extract authority binding from onboarded profile
    raw_binding = profile_data.get("authority_binding")
    if not isinstance(raw_binding, dict):
        # Look for legacy / top-level fallback
        if "bound_machine_guid_digest" in profile_data:
            raw_binding = {
                "bound_machine_guid_digest": profile_data.get("bound_machine_guid_digest"),
                "last_known_canonical_path": profile_data.get("last_known_canonical_path", ""),
                "hardware_migration_epoch": profile_data.get("hardware_migration_epoch", 0),
            }
        else:
            return ProvenanceVerificationResult(
                status=ProvenanceVerificationStatus.MISSING_AUTHORITY_BINDING,
                is_valid=False,
                is_genesis_locked=False,
                workspace_path=ws,
                recorded_workspace_path=None,
                current_hardware_digest="",
                bound_hardware_digest=None,
                hardware_matched=False,
                workspace_matched=False,
                clock_monotonic=True,
                divergence_details="Onboarded profile is missing 'authority_binding' section.",
                threat_classifications=threat_classifications,
            )

    binding = AuthorityBinding.from_dict(raw_binding)
    recorded_path = binding.last_known_canonical_path or profile_data.get("last_known_canonical_path", "")

    # Collect current hardware identifiers
    comps = hardware_components_override or collect_hardware_components(ws)
    curr_digest = compute_hardware_digest(comps, salt=salt)
    bound_digest = binding.bound_machine_guid_digest

    # Step 4: Workspace Path Anchoring Check (Copied Workspace Detection)
    workspace_matched = True
    if recorded_path:
        workspace_matched = are_workspace_paths_equal(ws, recorded_path)
        if not workspace_matched:
            return ProvenanceVerificationResult(
                status=ProvenanceVerificationStatus.WORKSPACE_DIVERGENCE,
                is_valid=False,
                is_genesis_locked=False,
                workspace_path=ws,
                recorded_workspace_path=recorded_path,
                current_hardware_digest=curr_digest,
                bound_hardware_digest=bound_digest,
                hardware_matched=(curr_digest == bound_digest),
                workspace_matched=False,
                clock_monotonic=True,
                divergence_details=(
                    f"Workspace path diverged: expected canonical path '{recorded_path}', "
                    f"actual runtime path '{normalize_workspace_path(ws)}'."
                ),
                threat_classifications=threat_classifications,
            )

    # Step 5: Hardware Digest Verification
    hardware_matched = (curr_digest == bound_digest) if bound_digest else True
    if bound_digest and not hardware_matched:
        # Check if reconfirmation is authorized
        should_reconfirm = allow_reconfirmation
        if not should_reconfirm and reconfirm_callback is not None:
            should_reconfirm = bool(reconfirm_callback())

        if should_reconfirm:
            # Execute non-destructive reconfirmation
            updated = reconfirm_hardware_environment(
                profile_path=target_profile,
                current_workspace_path=ws,
                hardware_components=comps,
                salt=salt,
            )
            return ProvenanceVerificationResult(
                status=ProvenanceVerificationStatus.VALID,
                is_valid=True,
                is_genesis_locked=False,
                workspace_path=ws,
                recorded_workspace_path=normalize_workspace_path(ws),
                current_hardware_digest=curr_digest,
                bound_hardware_digest=curr_digest,
                hardware_matched=True,
                workspace_matched=True,
                clock_monotonic=True,
                divergence_details="Hardware environment divergence reconfirmed by authorized owner.",
                threat_classifications=threat_classifications,
            )
        else:
            # Enter AWAITING_HARDWARE_RECONFIRMATION modal state (non-destructive)
            return ProvenanceVerificationResult(
                status=ProvenanceVerificationStatus.AWAITING_HARDWARE_RECONFIRMATION,
                is_valid=False,
                is_genesis_locked=False,
                workspace_path=ws,
                recorded_workspace_path=recorded_path,
                current_hardware_digest=curr_digest,
                bound_hardware_digest=bound_digest,
                hardware_matched=False,
                workspace_matched=workspace_matched,
                clock_monotonic=True,
                divergence_details=(
                    f"Hardware environment divergence detected: bound digest '{bound_digest[:12]}...', "
                    f"current digest '{curr_digest[:12]}...'. Awaiting owner reconfirmation."
                ),
                threat_classifications=threat_classifications,
            )

    # Step 6: Wall-Clock Monotonicity Check
    clock_ok, clock_err = check_wall_clock_monotonicity(
        profile_data=profile_data,
        epoch_manifest_path=epoch_manifest_path,
        current_utc=current_utc,
    )
    if not clock_ok:
        return ProvenanceVerificationResult(
            status=ProvenanceVerificationStatus.WALL_CLOCK_ROLLBACK_DETECTED,
            is_valid=False,
            is_genesis_locked=False,
            workspace_path=ws,
            recorded_workspace_path=recorded_path,
            current_hardware_digest=curr_digest,
            bound_hardware_digest=bound_digest,
            hardware_matched=hardware_matched,
            workspace_matched=workspace_matched,
            clock_monotonic=False,
            divergence_details=clock_err,
            threat_classifications=threat_classifications,
        )

    # Normal / Valid Verification
    return ProvenanceVerificationResult(
        status=ProvenanceVerificationStatus.VALID,
        is_valid=True,
        is_genesis_locked=False,
        workspace_path=ws,
        recorded_workspace_path=recorded_path,
        current_hardware_digest=curr_digest,
        bound_hardware_digest=bound_digest,
        hardware_matched=True,
        workspace_matched=True,
        clock_monotonic=True,
        divergence_details=None,
        threat_classifications=threat_classifications,
    )
