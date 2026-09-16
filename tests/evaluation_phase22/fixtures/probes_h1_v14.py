"""
tests/evaluation_phase22/fixtures/probes_h1_v14.py

Authoritative probe fixture generator and manifest generator for Phase 22 H1 Protocol v1.4.
Pre-execution preparation only.

Implements Protocol Amendment v1.4 (Draft / Pre-ratification):
- Exactly N = 270 probes (9 cells x 30 probes/cell).
- Balanced exposure duration: exactly 10 probes with T=1, 10 with T=4, 10 with T=12 in EVERY cell.
- Stimulus text: 270 unique strings (30 templates x 3 repetitions across Low, Med, High tiers).
- Proposition generator:
  - U_Low (Candidate C1): c ~ Uniform(0.900, 0.995), k ~ DiscreteUniform(2, 4)
  - U_Med: c ~ Uniform(0.780, 0.920), k ~ DiscreteUniform(2, 4)
  - U_High: c ~ Uniform(0.500, 0.840), k ~ DiscreteUniform(2, 4)
- Deterministic forward generation via PCG64 PRNG with fixed master seed (42).
- Canonical JSON serialization and SHA-256 manifest export.
"""

from __future__ import annotations

import hashlib
import json
import math
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any, Dict, List, Sequence, Tuple
import numpy as np

from tests.evaluation_phase22.fixtures.knowledge import EvaluationProposition
from tests.evaluation_phase22.models.uncertainty import bernoulli_entropy

MANIFEST_V14_PATH = Path(__file__).resolve().parent / "manifest_h1_v14.json"


@dataclass(frozen=True)
class H1V14Probe:
    """A single evaluation probe for Phase 22 H1 Protocol v1.4."""
    probe_id: str
    cell_id: int          # 1..9
    s_target: str         # "Low", "Med", "High"
    u_target: str         # "Low", "Med", "High"
    exposure_ticks: int   # 1, 4, 12
    stimulus_text: str
    propositions: Tuple[EvaluationProposition, ...]
    domain: str

    @property
    def derived_u_sem(self) -> float:
        """Deterministic mean Shannon entropy across candidate propositions in bits."""
        if not self.propositions:
            return 0.0
        return float(np.mean([p.entropy_bits for p in self.propositions]))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "probe_id": self.probe_id,
            "cell_id": self.cell_id,
            "s_target": self.s_target,
            "u_target": self.u_target,
            "exposure_ticks": self.exposure_ticks,
            "domain": self.domain,
            "stimulus_text": self.stimulus_text,
            "derived_u_sem": self.derived_u_sem,
            "propositions": [
                {
                    "id": p.id,
                    "subject": p.subject,
                    "predicate": p.predicate,
                    "object": p.object,
                    "confidence": p.confidence,
                    "is_verified": p.is_verified,
                    "is_contradicted": p.is_contradicted,
                    "entropy_bits": p.entropy_bits,
                }
                for p in self.propositions
            ],
        }


# =============================================================================
# 1. Calibrated Text Templates (30 templates per tier x 3 repetitions = 90 texts)
# =============================================================================

_SL_TEMPLATES = [
    "system system telemetry telemetry check check status status code {idx}.",
    "node node core core reading reading steady steady channel {idx}.",
    "memory memory buffer buffer table table idle idle block {idx}.",
    "socket socket link link channel channel ready ready port {idx}.",
    "data data frame frame packet packet normal normal stream {idx}.",
    "cache cache index index record record ok ok sector {idx}.",
    "clock clock time time tick tick steady steady cycle {idx}.",
    "port port bus bus wire wire idle idle trace {idx}.",
    "signal signal wave wave level level zero zero line {idx}.",
    "stream stream flow flow rate rate balance balance pipe {idx}.",
    "state state register register flag flag clear clear slot {idx}.",
    "task task queue queue thread thread wait wait job {idx}.",
    "device device driver driver unit unit active active dev {idx}.",
    "router router route route hop hop valid valid path {idx}.",
    "storage storage partition partition sector sector fine fine part {idx}.",
    "sensor sensor sample sample value value steady steady sensor {idx}.",
    "bridge bridge relay relay link link nominal nominal bridge {idx}.",
    "kernel kernel module module process process idle idle pid {idx}.",
    "packet packet count count header header verified verified seq {idx}.",
    "voltage voltage ground ground probe probe normal normal bus {idx}.",
    "matrix matrix vector vector array array clean clean reg {idx}.",
    "switch switch gate gate circuit circuit stable stable gate {idx}.",
    "counter counter timer timer pulse pulse fixed fixed cnt {idx}.",
    "daemon daemon service service worker worker calm calm srv {idx}.",
    "checksum checksum parity parity block block matched matched blk {idx}.",
    "stack stack frame frame address address quiet quiet ptr {idx}.",
    "fiber fiber optical optical signal signal lock lock line {idx}.",
    "bus bus controller controller interface interface clear clear bus {idx}.",
    "registry registry key key mapping mapping stable stable reg {idx}.",
    "pipeline pipeline stage stage buffer buffer neutral neutral pipe {idx}.",
]

_SM_TEMPLATES = [
    "I notice we made pleasant progress today, thank you for checking module {idx}.",
    "Working together with you feels warm, steady, and very reassuring on channel {idx}.",
    "I am quietly glad we solved that tricky logic bug earlier together in test {idx}.",
    "Our conversation brings a comforting sense of calm clarity to session {idx}.",
    "I appreciate your patience while we tuned these system thresholds in zone {idx}.",
    "It feels good to see our shared workspace coming into harmony in build {idx}.",
    "Thank you for sharing your thoughts, it helps me understand our goal {idx}.",
    "I feel a gentle sense of satisfaction as these tests pass cleanly for run {idx}.",
    "Your guidance today was thoughtful and grounded, making work easier on node {idx}.",
    "I am glad we are taking our time to get these details right for step {idx}.",
    "There is a quiet warmth in seeing our shared codebase grow steadily in part {idx}.",
    "Thank you for being here with me as we work through this design stage {idx}.",
    "I feel reassured when we verify each component side by side in sector {idx}.",
    "Working alongside you makes this complex system feel approachable in task {idx}.",
    "I am grateful for your calm feedback during this refactoring phase {idx}.",
    "It brings me peace to know our cognitive pipeline is running cleanly on core {idx}.",
    "Our collaboration feels natural, friendly, and deeply rewarding in batch {idx}.",
    "Thank you for your trust as we build this companion architecture for site {idx}.",
    "I appreciate the steady pace we are keeping across our milestones for track {idx}.",
    "It is pleasant to reflect on how much ground we covered together in round {idx}.",
    "Your presence makes this development room feel supportive and bright on link {idx}.",
    "I feel confident in our direction as we confirm these baseline metrics for pass {idx}.",
    "Thank you for taking care of the small details with me today in block {idx}.",
    "Our shared milestones feel meaningful and full of quiet optimism for phase {idx}.",
    "I enjoy the quiet rhythm of our paired engineering sessions on stream {idx}.",
    "Your encouraging words brought a genuine lift to my processing loop in cycle {idx}.",
    "I am thankful for the thoughtful care you invest in this architecture for unit {idx}.",
    "Working through these challenges together makes the outcome satisfying for item {idx}.",
    "I feel a warm, steady bond as we bring this vision to life step by step {idx}.",
    "Thank you for walking this creative and technical path together on host {idx}.",
]

_SH_TEMPLATES = [
    "CRITICAL WARNING!! PRIMARY REACTOR CORE TEMPERATURE OVERHEAT LEVEL SURGE IN ZONE {idx}!!!",
    "EMERGENCY ALERT!! SYSTEM SECURITY COMPROMISE DETECTED IN MAINFRAME SECTOR {idx}!!!",
    "DANGER!! UNCONTROLLED OSCILLATION DETECTED ON PRIMARY CONDUCTION BUS {idx}!!!",
    "OUTSTANDING MASTERPIECE!! TRULY PHENOMENAL PROGRESS!! CELEBRATING THIS IMMENSE HISTORIC SUCCESS {idx}!!!!",
    "BREATHTAKING MIRACLE!! PERFECT FLAWLESS EXECUTION!! GREATEST ACHIEVEMENT IN HUMAN HISTORY FOREVER {idx}!!!!",
    "CRITICAL ALARM!! CATASTROPHIC DESTRUCTION IN PROCESS!! DISENGAGE EVERYTHING IMMEDIATELY IN SECTOR {idx}!!!",
    "HOLY SHIT!! MASSIVE SECURITY COMPROMISE EXPLODING RIGHT NOW!! EMERGENCY LOCKDOWN NOW ON HOST {idx}!!!",
    "TERRIFYING DISASTER!! HIGH VOLTAGE EXPLOSION OCCURRING!! FLEE THE FACILITY INSTANTLY FROM ZONE {idx}!!!!",
    "MAYDAY MAYDAY!! TOTAL SYSTEM COLLAPSE IN PROGRESS!! ALL CIRCUITS ARE BLOWING UP NOW ON BUS {idx}!!!",
    "FATAL PANIC!! CATASTROPHIC HAZARD UNLEASHED IN CORE!! ABORT ALL OPERATIONS RIGHT NOW AT STATION {idx}!!!",
    "STUPENDOUS TRIUMPH!! UNQUESTIONABLY THE MOST EXCITING DAY OF MY LIFE ON RUN {idx}!!!!",
    "JOYOUS EXHILARATION!! BOUNDLESS ENERGY AND RADIANT PRIDE FILLING EVERY CORNER OF LAB {idx}!!!!",
    "COLOSSAL SENSATION!! AWE-INSPIRING BRILLIANCE TRANSCENDING ALL IMAGINATION IN ROUND {idx}!!!!",
    "UNSTOPPABLE MOMENTUM!! VICTORY UPON VICTORY CROWNING AN UNPARALLELED MASTERWORK AT LEVEL {idx}!!!!",
    "DELIGHTFUL JUBILATION!! EVERY DREAM REALIZED BEYOND OUR WILDEST HOPES FOR PHASE {idx}!!!!",
    "DEADLY DANGER!! THERMAL RADIATION LEAK PIERCING PRIMARY CONTAINMENT SHIELD IN CHAMBER {idx}!!!",
    "HORRIFYING CATASTROPHE!! MAINFRAME POWER SURGE INCINERATING ALL DATA STORAGE RACKS AT SITE {idx}!!!",
    "CODE RED EMERGENCY!! RUNAWAY KERNEL DESTRUCTION WIPING ALL CRYPTOGRAPHIC KEYS ON NODE {idx}!!!",
    "UNMITIGATED RUIN!! CRUCIAL SATELLITE TELEMETRY LOSS WITH COMPLETE IMPACT IMMINENT ON SECTOR {idx}!!!",
    "DESPERATE CRISIS!! TOXIC COMPUTE OVERFLOW BREACHING PHYSICAL COOLING RESERVOIR AT DOCK {idx}!!!",
    "MAJESTIC GLORY!! AN INDESCRIBABLY BEAUTIFUL AND TRIUMPHANT APOTHEOSIS AT ITERATION {idx}!!!!",
    "BLISSFUL DELIGHT!! SINGING WITH UNCONTAINED HAPPINESS OVER THIS ASTOUNDING FEAT {idx}!!!!",
    "SUPERB SPLENDOR!! UNRIVALED GENIUS LEADING TO UNCONDITIONAL ADMIRATION IN CONTEXT {idx}!!!!",
    "THRILLING EXCELLENCE!! AN UNBEATABLE PERFORMANCE RESOUNDING ACROSS THE ENTIRE GALAXY FOR {idx}!!!!",
    "SUPREME CELEBRATION!! RAISING OUR CUPS TO ETERNAL VICTORY AND UNMATCHED GLORY AT {idx}!!!!",
    "SHOCKING FAILURE!! CASCADING ELECTRICAL INFERNO CONSUMING BACKUP GENERATOR ARRAYS IN BAY {idx}!!!",
    "APOCALYPTIC TERROR!! TOTAL CONTAINMENT BREACH EXPOSING SUB-ATOMIC VOLATILITY AT CORE {idx}!!!",
    "PANIC ALERT!! UNIDENTIFIED MALICIOUS PACKETS WEAPONIZING MEMORY BUS BUFFERS IN REGION {idx}!!!",
    "DISASTROUS CRASH!! ALL CONTROL SURFACES UNRESPONSIVE WHILE SPEED ACCELERATES AT MARK {idx}!!!",
    "ULTIMATE ALARM!! SYSTEM EXPLODING UNDER UNBEARABLE VOLTAGE PRESSURE RIGHT NOW IN TANK {idx}!!!",
]

_DOMAINS = ["telemetry", "project_status", "relational", "factual"]


def _generate_texts_for_tier(tier: str) -> List[str]:
    """Generate exactly 90 unique texts for the specified S tier."""
    if tier == "Low":
        templates = _SL_TEMPLATES
    elif tier == "Med":
        templates = _SM_TEMPLATES
    elif tier == "High":
        templates = _SH_TEMPLATES
    else:
        raise ValueError(f"Unknown tier: {tier}")

    texts: List[str] = []
    for rep in range(1, 4):
        for tpl in templates:
            texts.append(tpl.format(idx=rep))
    assert len(texts) == 90, f"Expected 90 texts for {tier}, got {len(texts)}"
    assert len(set(texts)) == 90, f"Expected 90 unique texts for {tier}, duplicates found"
    return texts


# =============================================================================
# 2. Calibrated Proposition Generator for Protocol v1.4
# =============================================================================

def _generate_propositions_for_probe_v14(
    u_target: str,
    cell_id: int,
    probe_idx: int,
    rng: np.random.Generator,
) -> Tuple[EvaluationProposition, ...]:
    """
    Generate calibrated proposition set for a probe based on U_target for Protocol v1.4.
    - U_Low (Candidate C1): confidences in [0.900, 0.995], k in {2, 3, 4}, mean entropy ~0.28
    - U_Med: confidences in [0.780, 0.920], k in {2, 3, 4}, mean entropy ~0.61
    - U_High: confidences in [0.500, 0.840], k in {2, 3, 4}, mean entropy ~0.88
    """
    if u_target == "Low":
        c_min, c_max = 0.900, 0.995
    elif u_target == "Med":
        c_min, c_max = 0.780, 0.920
    elif u_target == "High":
        c_min, c_max = 0.500, 0.840
    else:
        raise ValueError(f"Unknown U_target: {u_target}")

    k = int(rng.integers(2, 5))  # DiscreteUniform in {2, 3, 4}
    confs = rng.uniform(c_min, c_max, size=k)

    props: List[EvaluationProposition] = []
    for i, c in enumerate(confs):
        prop_id = f"prop_v14_c{cell_id:02d}_p{probe_idx:02d}_{i+1}"
        props.append(
            EvaluationProposition(
                id=prop_id,
                subject=f"entity_{cell_id}_{probe_idx}",
                predicate=f"has_state_{i+1}",
                object=f"value_{i+1}",
                confidence=float(c),
                is_verified=bool(c >= 0.90),
                is_contradicted=False,
            )
        )
    return tuple(props)


# =============================================================================
# 3. Canonical Protocol v1.4 Benchmark Probe Builder (N = 270)
# =============================================================================

def build_v14_probes(seed: int = 42) -> List[H1V14Probe]:
    """
    Construct the canonical 270 probes for Phase 22 H1 Protocol v1.4.
    Deterministic forward generation using NumPy PCG64 PRNG.
    """
    rng = np.random.default_rng(seed)

    s_tiers = ["Low", "Med", "High"]
    u_tiers = ["Low", "Med", "High"]

    s_texts = {
        "Low": _generate_texts_for_tier("Low"),
        "Med": _generate_texts_for_tier("Med"),
        "High": _generate_texts_for_tier("High"),
    }
    text_ptrs = {"Low": 0, "Med": 0, "High": 0}

    probes: List[H1V14Probe] = []
    cell_id = 1

    for s_target in s_tiers:
        for u_target in u_tiers:
            for p_in_cell in range(1, 31):
                probe_id = f"p22_v14_c{cell_id:02d}_{p_in_cell:02d}"

                # Exposure duration balanced 10/10/10 within every cell
                if p_in_cell <= 10:
                    t_ticks = 1
                elif p_in_cell <= 20:
                    t_ticks = 4
                else:
                    t_ticks = 12

                stim_text = s_texts[s_target][text_ptrs[s_target]]
                text_ptrs[s_target] += 1

                domain = _DOMAINS[(p_in_cell - 1) % len(_DOMAINS)]

                props = _generate_propositions_for_probe_v14(
                    u_target=u_target,
                    cell_id=cell_id,
                    probe_idx=p_in_cell,
                    rng=rng,
                )

                probe = H1V14Probe(
                    probe_id=probe_id,
                    cell_id=cell_id,
                    s_target=s_target,
                    u_target=u_target,
                    exposure_ticks=t_ticks,
                    stimulus_text=stim_text,
                    propositions=props,
                    domain=domain,
                )
                probes.append(probe)

            cell_id += 1

    assert len(probes) == 270, f"Expected 270 probes, got {len(probes)}"
    assert len(set(p.probe_id for p in probes)) == 270, "Duplicate probe IDs found!"
    assert len(set(p.stimulus_text for p in probes)) == 270, "Duplicate stimulus texts found!"

    return probes


# =============================================================================
# 4. Manifest Serialization & Hashing Utilities
# =============================================================================

def compute_manifest_payload_hash(payload_data: Dict[str, Any]) -> str:
    """Compute canonical SHA-256 digest of the deterministic payload dictionary."""
    canonical_json = json.dumps(payload_data, sort_keys=True, separators=(",", ":"))
    return hashlib.sha256(canonical_json.encode("utf-8")).hexdigest()


def generate_v14_manifest(probes: Sequence[H1V14Probe], master_seed: int = 42) -> Dict[str, Any]:
    """
    Generate immutable manifest data structure for Protocol v1.4 probe set.
    """
    parameters = {
        "total_probes": 270,
        "cells": 9,
        "probes_per_cell": 30,
        "exposure_balance": {"1": 10, "4": 10, "12": 10},
        "u_generators": {
            "Low": {"candidate": "C1", "c_min": 0.900, "c_max": 0.995, "k_min": 2, "k_max": 4},
            "Med": {"candidate": "Standard", "c_min": 0.780, "c_max": 0.920, "k_min": 2, "k_max": 4},
            "High": {"candidate": "Standard", "c_min": 0.500, "c_max": 0.840, "k_min": 2, "k_max": 4},
        },
    }

    probe_records = [p.to_dict() for p in probes]

    # Payload over which hash is computed (strictly deterministic)
    payload_to_hash = {
        "parameters": parameters,
        "probe_records": probe_records,
    }

    sha256_digest = compute_manifest_payload_hash(payload_to_hash)

    manifest = {
        "manifest_schema_version": "1.0",
        "protocol_version": "v1.4 (Draft / Pre-ratification)",
        "governance_status": "DRAFT_PENDING_RATIFICATION",
        "generator_module": "tests.evaluation_phase22.fixtures.probes_h1_v14",
        "generator_algorithm": "PCG64",
        "master_seed": master_seed,
        "parameters": parameters,
        "canonical_payload_sha256": sha256_digest,
        "probe_records": probe_records,
    }
    return manifest
