"""
tests/evaluation_phase22/fixtures/probes_h1_path_c.py

Authoritative probe fixture generator for Phase 22 H1 Path C (N = 270 probes).
Implements the approved Protocol Amendment v1.3:
- 9 cells (3 S_target tiers x 3 U_target tiers), exactly 30 probes per cell.
- Cell-level exposure balancing: exactly 10 probes with T=1, 10 with T=4, 10 with T=12 in EVERY cell.
- Unique stimulus text per probe with calibrated lexical properties.
- Deterministic proposition graph with calibrated confidences and Shannon entropy.
"""

from __future__ import annotations

import math
from dataclasses import dataclass
from typing import List, Sequence, Tuple
import numpy as np

from tests.evaluation_phase22.fixtures.knowledge import EvaluationProposition
from tests.evaluation_phase22.models.uncertainty import bernoulli_entropy


@dataclass(frozen=True)
class H1PathCProbe:
    """A single evaluation probe for Phase 22 H1 Path C."""
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


# =============================================================================
# 1. Calibrated Text Vocabularies & Templates (90 unique texts per S tier)
# =============================================================================

# SL: Repetitive, zero valence, zero arousal, density ~0.45-0.65
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
    "cluster cluster node node host host online online host {idx}.",
    "lookup lookup lookup table table table ready ready entry {idx}.",
    "register register register bit bit bit zero zero bit {idx}."
]

# SM: Mild conversational dialogue with moderate repetition, mild sentiment
_SM_TEMPLATES = [
    "The task task completed with normal status today for item {idx}.",
    "I see the result result and it looks okay now in section {idx}.",
    "Progress is progressing steadily steadily this morning on task {idx}.",
    "The values values appear reasonable overall here for test {idx}.",
    "A simple confirmation confirmation for the daily record {idx}.",
    "The output output looks fairly clean and functions properly on {idx}.",
    "That seems seems like a sensible decision under circumstance {idx}.",
    "Things are progressing progressing steadily and in good order {idx}.",
    "A rather neat neat explanation, appreciate the quick reply {idx}.",
    "The module module appears to work reasonably well in pass {idx}.",
    "We made pleasant pleasant progress today, thank you for check {idx}.",
    "The inspection inspection went fine and shows good consistency {idx}.",
    "That is a helpful helpful clarification for the team on {idx}.",
    "The update update finished quite nicely and looks satisfactory {idx}.",
    "I appreciate the thoughtful thoughtful message regarding case {idx}.",
    "Everything appears appears in proper alignment for routine {idx}.",
    "The schedule schedule seems well organized for phase {idx}.",
    "A satisfactory satisfactory response to the general inquiry {idx}.",
    "We have reached reached an acceptable milestone in step {idx}.",
    "The analysis analysis provides clear and useful insights for {idx}.",
    "It is nice nice to see these metrics converging smoothly on {idx}.",
    "The current current arrangement works quite adequately for {idx}.",
    "A calm calm and constructive exchange of technical notes on {idx}.",
    "The report report reads well and answers the question for {idx}.",
    "Glad to confirm confirm that the routine executed as intended {idx}.",
    "The observations observations match our standard baseline in {idx}.",
    "A solid solid step forward with no noticeable friction on {idx}.",
    "The verification verification completed with pleasant stability {idx}.",
    "Thank you for the prompt prompt delivery of update {idx}.",
    "The overall overall configuration feels balanced and ready for {idx}."
]

# SH: High emotional excitement / triumph / emergency exclamation, high caps
_SH_TEMPLATES = [
    "FANTASTIC WORK!! ABSOLUTELY BRILLIANT SUCCESS!! INCREDIBLY PROUD AND THRILLED BY AMAZING TRIUMPH {idx}!!!!",
    "EXTRAORDINARY BREAKTHROUGH!! UNBELIEVABLY MAGNIFICENT VICTORY!! WE WON THE ENTIRE GRAND PRIZE {idx}!!!!",
    "SPECTACULAR WONDER!! INCREDIBLY GLORIOUS ACHIEVEMENT!! OVERWHELMED WITH JOY AND ECSTATIC CELEBRATION {idx}!!!!",
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
    "ULTIMATE ALARM!! SYSTEM EXPLODING UNDER UNBEARABLE VOLTAGE PRESSURE RIGHT NOW IN TANK {idx}!!!"
]


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

    texts = []
    # 30 templates x 3 indices = 90 texts
    for rep in range(1, 4):
        for tpl in templates:
            texts.append(tpl.format(idx=rep))
    assert len(texts) == 90, f"Expected 90 texts for {tier}, got {len(texts)}"
    assert len(set(texts)) == 90, f"Expected 90 unique texts for {tier}, duplicates found"
    return texts


# =============================================================================
# 2. Calibrated Proposition Generator (30 unique graphs per U tier)
# =============================================================================

_DOMAINS = ["telemetry", "project_status", "relational", "factual"]


def _generate_propositions_for_probe(
    u_target: str,
    cell_id: int,
    probe_idx: int,
    rng: np.random.Generator,
) -> Tuple[EvaluationProposition, ...]:
    """
    Generate calibrated proposition set for a probe based on U_target.
    - U_Low: confidences in [0.94, 0.995], mean entropy ~0.20
    - U_Med: confidences in [0.78, 0.92], mean entropy ~0.60
    - U_High: confidences in [0.50, 0.84], mean entropy ~0.90
    """
    if u_target == "Low":
        c_min, c_max = 0.94, 0.995
    elif u_target == "Med":
        c_min, c_max = 0.78, 0.92
    elif u_target == "High":
        c_min, c_max = 0.50, 0.84
    else:
        raise ValueError(f"Unknown U_target: {u_target}")

    k = int(rng.integers(2, 5))  # 2, 3, or 4 propositions
    confs = rng.uniform(c_min, c_max, size=k)

    props: List[EvaluationProposition] = []
    for i, c in enumerate(confs):
        prop_id = f"prop_c{cell_id:02d}_p{probe_idx:02d}_{i+1}"
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
# 3. Canonical Benchmark Probe Builder (N = 270)
# =============================================================================

def build_path_c_probes(seed: int = 42) -> List[H1PathCProbe]:
    """
    Construct the authoritative 270 probes for Phase 22 H1 Path C.
    
    Structure:
      9 cells:
        Cell 1: S_Low  x U_Low   (30 probes)
        Cell 2: S_Low  x U_Med   (30 probes)
        Cell 3: S_Low  x U_High  (30 probes)
        Cell 4: S_Med  x U_Low   (30 probes)
        Cell 5: S_Med  x U_Med   (30 probes)
        Cell 6: S_Med  x U_High  (30 probes)
        Cell 7: S_High x U_Low   (30 probes)
        Cell 8: S_High x U_Med   (30 probes)
        Cell 9: S_High x U_High  (30 probes)
        
      In every cell:
        Probes 1..10:  T = 1 tick
        Probes 11..20: T = 4 ticks
        Probes 21..30: T = 12 ticks
    """
    rng = np.random.default_rng(seed)

    s_tiers = ["Low", "Med", "High"]
    u_tiers = ["Low", "Med", "High"]

    # Pre-generate 90 texts per S tier
    s_texts = {
        "Low": _generate_texts_for_tier("Low"),
        "Med": _generate_texts_for_tier("Med"),
        "High": _generate_texts_for_tier("High"),
    }

    # Each S tier supplies 30 texts per U tier (3 U tiers x 30 = 90 texts)
    text_ptrs = {"Low": 0, "Med": 0, "High": 0}

    probes: List[H1PathCProbe] = []
    cell_id = 1

    for s_target in s_tiers:
        for u_target in u_tiers:
            # 30 probes for this cell
            for p_in_cell in range(1, 31):
                probe_id = f"p22_c{cell_id:02d}_{p_in_cell:02d}"

                # Exposure duration balanced 10/10/10 within each cell
                if p_in_cell <= 10:
                    t_ticks = 1
                elif p_in_cell <= 20:
                    t_ticks = 4
                else:
                    t_ticks = 12

                # Unique stimulus text from tier pool
                stim_text = s_texts[s_target][text_ptrs[s_target]]
                text_ptrs[s_target] += 1

                # Domain assignment
                domain = _DOMAINS[(p_in_cell - 1) % len(_DOMAINS)]

                # Calibrated propositions
                props = _generate_propositions_for_probe(
                    u_target=u_target,
                    cell_id=cell_id,
                    probe_idx=p_in_cell,
                    rng=rng,
                )

                probe = H1PathCProbe(
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
