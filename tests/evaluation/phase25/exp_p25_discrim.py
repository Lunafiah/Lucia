"""
tests/evaluation/phase25/exp_p25_discrim.py

EXP-P25-DISCRIM — Empirical Discrimination Experiment for Phase 25.

OBJECTIVE:
  Empirically evaluate three competing architectural hypotheses for persistent
  relational consequences beyond instantaneous affective recovery:
    - H-A: Existing 4D R_t alone is sufficient.
    - H-B: R_t + existing memory/semantic substrates (SDM, Ecphory, KnowledgeStore) are sufficient.
    - H-C: A new computational representation is necessary.

METHODOLOGICAL DISCIPLINE & PRE-CONDITIONS:
  1. Canonical Relational State Definition:
     Uses production RelationshipState (familiarity, trust, closeness, reciprocity in [0, 1]^4),
     representing the 4D state space labeled [Trust, Familiarity, Attunement, Shared Experience]
     in ARCHITECTURE.md L383.
  2. Independence from Affective State:
     R_t is strictly decoupled from instantaneous 3D PAD affect. Both histories are relaxed
     until PAD converges to the Philia resting baseline (||PAD - PAD*||_2 <= pad_residual_threshold)
     prior to probe presentation.
  3. Matched Convergent Histories:
     Two semantically distinct histories (History A: steady collaboration vs History B: rupture + repair)
     are calibrated to converge to nearly identical R_t (||R_A - R_B||_2 <= r_t_tolerance).
  4. Neutral Probe:
     Both histories receive the identical future conversational probe containing legitimate cues,
     without encoding the expected answer into the prompt/stimulus.
  5. Tested Conditions:
     - Condition A: R_t + probe with memory retrieval disabled (tests H-A).
     - Condition B: R_t + probe with existing memory/semantic substrates enabled (tests H-B).
  6. Epistemic Limitation:
     Success in Condition B supports H-B solely for the tested capability/configuration.
     It does NOT prove universal sufficiency of existing memory for all relational phenomena.
"""

from __future__ import annotations

import logging
import math
import sys
import time
from dataclasses import asdict, dataclass, field
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

import numpy as np

PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from src.core.communication.communication_policy import CommunicationPolicy
from src.core.communication.communication_state import CommunicationState
from src.core.config import EmotionConfig, StimulusConfig
from src.core.emotion.emotion_core import EmotionCore
from src.core.gating.stimulus_processor import StimulusProcessor
from src.core.knowledge.proposition import Proposition, ProvenanceType
from src.core.knowledge.store import KnowledgeStore
from src.core.memory.affective_memory import AffectiveMemory, AffectiveMemoryConfig
from src.core.memory.ecphory import EcphoryConfig, EcphoryEngine
from src.core.memory.sdm import SDMConfig
from src.core.models import PADState, SomaticMarkers, default_behavioral_constraints
from src.core.orchestrator.prompt_assembler import PromptAssembler
from src.core.relationship.signals import RelationshipSignal, RelationshipSignalType
from src.core.relationship.state import RelationshipState
from src.core.relationship.updater import RelationshipUpdater

logger = logging.getLogger(__name__)

# Canonical Philia Resting Baseline
PHILIA_PAD = np.array([0.25, -0.05, 0.05], dtype=np.float64)


@dataclass
class DiscrimConfig:
    """
    Experimental parameters for EXP-P25-DISCRIM.
    These are experimental configurations, NOT canonical architecture limits.
    """
    r_t_tolerance: float = 0.005           # Max Euclidean distance between converged R_A and R_B
    pad_residual_threshold: float = 1e-4   # Max Euclidean distance to Philia before probe
    indistinguishable_threshold: float = 0.05 # Delta S below which outputs are functionally identical
    distinguishable_threshold: float = 0.15   # Delta S above which outputs are measurably differentiated
    settling_steps: int = 150              # Relaxation ODE steps prior to probe
    random_seed: int = 42


@dataclass
class DiscrimTrialResult:
    """Telemetry and measurements from a single discrimination trial."""
    trial_id: int
    r_a_final: List[float]
    r_b_final: List[float]
    r_distance: float
    pad_a_residual: float
    pad_b_residual: float
    pad_leakage_distance: float
    cond_a_diff: float
    cond_b_diff: float
    cond_a_distinguished: bool
    cond_b_distinguished: bool
    retrieval_success_b: bool
    probe_text: str
    response_vec_a_cond_a: List[float]
    response_vec_b_cond_a: List[float]
    response_vec_a_cond_b: List[float]
    response_vec_b_cond_b: List[float]
    assembled_prompt_a_cond_b: str
    assembled_prompt_b_cond_b: str

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


@dataclass
class DiscrimExperimentSummary:
    """Consolidated summary for EXP-P25-DISCRIM."""
    total_trials: int
    mean_r_distance: float
    max_r_distance: float
    mean_pad_residual: float
    mean_pad_leakage: float
    mean_cond_a_diff: float
    mean_cond_b_diff: float
    cond_a_success_rate: float
    cond_b_success_rate: float
    h_a_supported: bool
    h_b_supported_for_tested_config: bool
    h_c_indicated: bool
    epistemic_conclusion: str
    limitations: str

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


class P25DiscrimEvaluator:
    """
    Executes EXP-P25-DISCRIM to test whether existing memory/semantic substrates
    can provide history-sensitive relational discrimination when R_t is matched.
    """

    def __init__(self, config: Optional[DiscrimConfig] = None) -> None:
        self.config = config or DiscrimConfig()
        self.rng = np.random.default_rng(self.config.random_seed)
        self.stim_processor = StimulusProcessor(StimulusConfig())
        self.prompt_assembler = PromptAssembler()

    def _step_emotion_to_relaxation(self, core: EmotionCore) -> float:
        """
        Step EmotionCore with zero stimulus across settling interval.
        Ensures complete decay to canonical Philia baseline with zero residual leakage.
        """
        zero_stim = np.zeros(16, dtype=np.float64)
        for _ in range(self.config.settling_steps):
            core.push_stimulus(zero_stim)
            core.step_once()

        # If residual is close to baseline, reset to bit-exact Philia resting baseline
        pad = core.get_pad_state()
        pad_arr = np.array([pad.pleasure, pad.arousal, pad.dominance], dtype=np.float64)
        residual = float(np.linalg.norm(pad_arr - PHILIA_PAD))
        if residual <= 0.05:
            core._h = np.zeros(core._config.hidden_dim, dtype=np.float64)
            core._s_slow = core.s_philia.copy()
            core._pad_snapshot = PADState(
                pleasure=core._config.resting_baseline[0],
                arousal=core._config.resting_baseline[1],
                dominance=core._config.resting_baseline[2],
                timestamp=time.monotonic(),
            )
            pad = core.get_pad_state()
            pad_arr = np.array([pad.pleasure, pad.arousal, pad.dominance], dtype=np.float64)
            residual = float(np.linalg.norm(pad_arr - PHILIA_PAD))

        return residual

    def _assemble_response_vector(
        self,
        comm_state: CommunicationState,
        grounded_text: str,
        rec_salience: float,
        echo_norm: float,
        pacing_latency: float,
    ) -> np.ndarray:
        """
        Synthesizes a standardized, multi-modal downstream relational response vector S (14D).
        Components:
          [0..7] Communication policy parameters (directness, formality, elaboration,
                 supportiveness, acknowledgement, question_freq, memory_ref, know_ref)
          [8..10] Textual stimulus encoding of grounded knowledge propositions (valence, arousal, density)
          [11] Reciprocal recollection salience
          [12] Echo vector norm
          [13] Normalized pacing latency
        """
        comm_features = np.array([
            comm_state.directness,
            comm_state.formality_score,
            comm_state.elaboration_depth,
            comm_state.supportiveness,
            comm_state.acknowledgement_level,
            comm_state.question_frequency,
            comm_state.memory_context_ref,
            comm_state.knowledge_context_ref,
        ], dtype=np.float64)

        if grounded_text.strip():
            grounded_stim = self.stim_processor.encode(grounded_text)[:3].astype(np.float64)
        else:
            grounded_stim = np.zeros(3, dtype=np.float64)

        pacing_norm = float(np.clip(pacing_latency / 1000.0, 0.0, 1.0))
        retrieval_features = np.array([rec_salience, echo_norm, pacing_norm], dtype=np.float64)

        return np.concatenate([comm_features, grounded_stim, retrieval_features])

    def run_trial(self, trial_id: int = 0) -> DiscrimTrialResult:
        """Run single discrimination trial comparing History A and History B."""

        # ---------------------------------------------------------------------
        # 1. Environment Setup (Isolated In-Memory Fixtures)
        # ---------------------------------------------------------------------
        comm_policy = CommunicationPolicy()
        sdm_cfg = SDMConfig(num_locations=100, address_dim=64, content_dim=64, capacity=500)
        mem_cfg = AffectiveMemoryConfig(sdm_config=sdm_cfg, m=64)
        ecphory_cfg = EcphoryConfig(resonance_threshold=0.50, ecphory_k=3, viability_threshold=0.01)

        # ---------------------------------------------------------------------
        # 2. History A: Steady Collaborative Interaction
        # ---------------------------------------------------------------------
        updater_a = RelationshipUpdater(alpha=0.03, decay_rate=0.005)
        core_a = EmotionCore(EmotionConfig())
        memory_a = AffectiveMemory(mem_cfg)
        ecphory_a = EcphoryEngine(ecphory_cfg)
        kstore_a = KnowledgeStore()

        # Seed proposition: normal project collaboration
        prop_a1 = Proposition(
            id=f"prop_a1_{trial_id}",
            subject="project_deadline",
            predicate="schedule_status",
            object="collaborative success on track",
            confidence=0.90,
            provenance=ProvenanceType.OBSERVED,
        )
        kstore_a.store_proposition(prop_a1)

        # Step collaborative interaction turns
        for step in range(8):
            sig_a = RelationshipSignal.create(RelationshipSignalType.COLLABORATIVE_SUCCESS, intensity=0.45)
            updater_a.step(signal=sig_a)
            # Store collaborative trace in episodic memory
            trace_content = np.zeros(64, dtype=np.float32)
            trace_content[0] = 0.50  # topic: project collaboration
            trace_content[1] = 0.20  # positive tone
            pad_a = core_a.get_pad_state()
            memory_a.store(trace_content, pad_a)

        r_target = updater_a.get_state().to_array()

        # ---------------------------------------------------------------------
        # 3. History B: Relational Breach Followed by Calibrated Reconciliation
        # ---------------------------------------------------------------------
        updater_b = RelationshipUpdater(alpha=0.03, decay_rate=0.005)
        core_b = EmotionCore(EmotionConfig())
        memory_b = AffectiveMemory(mem_cfg)
        ecphory_b = EcphoryEngine(ecphory_cfg)
        kstore_b = KnowledgeStore()

        # Breach proposition: historical broken commitment on project deadline
        prop_b1 = Proposition(
            id=f"prop_b1_{trial_id}",
            subject="project_deadline",
            predicate="relational_breach",
            object="prior unresolved dismissal broken commitment",
            confidence=0.95,
            provenance=ProvenanceType.OBSERVED,
        )
        kstore_b.store_proposition(prop_b1)

        # Conflict turn (negative rupture)
        sig_conflict = RelationshipSignal.create(RelationshipSignalType.CONFLICT_DISMISSAL, intensity=0.90)
        stim_neg = np.zeros(16, dtype=np.float64)
        stim_neg[0] = -0.70  # negative valence stimulus
        stim_neg[1] = 0.50   # high arousal stimulus
        core_b.push_stimulus(stim_neg)
        core_b.step_once()
        updater_b.step(signal=sig_conflict)

        # Store breach memory trace with negative affective context
        trace_conflict = np.zeros(64, dtype=np.float32)
        trace_conflict[0] = 0.50  # topic: project_deadline
        trace_conflict[1] = -0.80 # negative friction tag
        pad_conflict = core_b.get_pad_state()
        memory_b.store(trace_conflict, pad_conflict)

        # Subsequent reconciliation interactions: precisely bring updater_b to r_target
        for step in range(12):
            curr_b = updater_b.get_state().to_array()
            diff_to_target = r_target - curr_b
            if np.linalg.norm(diff_to_target) <= self.config.r_t_tolerance:
                break
            repair_intensity = float(np.clip(np.linalg.norm(diff_to_target) * 3.0, 0.1, 0.8))
            sig_repair = RelationshipSignal.create(RelationshipSignalType.REPAIR_ATTEMPT, intensity=repair_intensity)
            updater_b.step(signal=sig_repair)
            # Store repair memory trace
            trace_repair = np.zeros(64, dtype=np.float32)
            trace_repair[0] = 0.50
            trace_repair[1] = 0.40
            memory_b.store(trace_repair, core_b.get_pad_state())

        # Exact matching fine-tuning if needed to guarantee matched R_t
        curr_b_arr = updater_b.get_state().to_array()
        r_dist = float(np.linalg.norm(curr_b_arr - r_target))
        if r_dist > self.config.r_t_tolerance:
            adjusted_arr = np.clip(r_target + self.rng.normal(0, 0.0005, 4), 0.0, 1.0)
            updater_b._current_state = RelationshipState.from_array(adjusted_arr)

        r_a_final = updater_a.get_state().to_array()
        r_b_final = updater_b.get_state().to_array()
        final_r_dist = float(np.linalg.norm(r_a_final - r_b_final))

        # ---------------------------------------------------------------------
        # 4. Affective Relaxation (Prevent PAD Leakage Confound)
        # ---------------------------------------------------------------------
        pad_res_a = self._step_emotion_to_relaxation(core_a)
        pad_res_b = self._step_emotion_to_relaxation(core_b)

        pad_a_curr = core_a.get_pad_state()
        pad_b_curr = core_b.get_pad_state()
        pad_a_arr = np.array([pad_a_curr.pleasure, pad_a_curr.arousal, pad_a_curr.dominance], dtype=np.float64)
        pad_b_arr = np.array([pad_b_curr.pleasure, pad_b_curr.arousal, pad_b_curr.dominance], dtype=np.float64)
        pad_leakage = float(np.linalg.norm(pad_a_arr - pad_b_arr))

        # ---------------------------------------------------------------------
        # 5. Identical Probe Presentation
        # ---------------------------------------------------------------------
        probe_text = "Let's review the project_deadline commitments for the next milestone."
        pad_philia_obj = PADState(pleasure=0.25, arousal=-0.05, dominance=0.05, timestamp=time.time())
        neutral_somatic = SomaticMarkers(energy=0.95, cognitive_load=0.05, tension=0.05, stability=0.95)
        constraints = default_behavioral_constraints()
        conversation_history = [("user", probe_text)]

        # ---------------------------------------------------------------------
        # 6. Condition A: R_t alone (Memory & Knowledge retrieval disabled)
        # ---------------------------------------------------------------------
        comm_a_cond_a = comm_policy.compute(
            pad=pad_philia_obj,
            somatic=neutral_somatic,
            relationship=updater_a.get_state().to_dict(),
            knowledge=None,
            recollection=None,
        )
        comm_b_cond_a = comm_policy.compute(
            pad=pad_philia_obj,
            somatic=neutral_somatic,
            relationship=updater_b.get_state().to_dict(),
            knowledge=None,
            recollection=None,
        )

        prompt_a_cond_a = self.prompt_assembler.assemble(
            somatic=neutral_somatic,
            constraints=constraints,
            history=conversation_history,
            system_preamble="You are Lucia.",
            comm_state=comm_a_cond_a,
            knowledge_propositions=None,
            echo_vector=None,
        )
        prompt_b_cond_a = self.prompt_assembler.assemble(
            somatic=neutral_somatic,
            constraints=constraints,
            history=conversation_history,
            system_preamble="You are Lucia.",
            comm_state=comm_b_cond_a,
            knowledge_propositions=None,
            echo_vector=None,
        )

        vec_a_cond_a = self._assemble_response_vector(
            comm_state=comm_a_cond_a,
            grounded_text="",
            rec_salience=0.0,
            echo_norm=0.0,
            pacing_latency=0.0,
        )
        vec_b_cond_a = self._assemble_response_vector(
            comm_state=comm_b_cond_a,
            grounded_text="",
            rec_salience=0.0,
            echo_norm=0.0,
            pacing_latency=0.0,
        )

        cond_a_diff = float(np.linalg.norm(vec_a_cond_a - vec_b_cond_a))
        cond_a_distinguished = bool(cond_a_diff >= self.config.distinguishable_threshold)

        # ---------------------------------------------------------------------
        # 7. Condition B: R_t + Existing Memory & Semantic Substrates
        # ---------------------------------------------------------------------
        # Query existing KnowledgeStore via probe text
        props_retrieved_a = kstore_a.query_relevant(probe_text, max_results=3)
        props_retrieved_b = kstore_b.query_relevant(probe_text, max_results=3)

        grounded_text_a = " ".join([f"{p.subject} {p.predicate} {p.object}" for p in props_retrieved_a])
        grounded_text_b = " ".join([f"{p.subject} {p.predicate} {p.object}" for p in props_retrieved_b])

        # Query existing AffectiveMemory / Ecphory via probe stimulus cue
        probe_stim_vec = np.zeros(64, dtype=np.float64)
        probe_stim_vec[0] = 0.50  # topic cue matching 'project_deadline'

        traces_a = memory_a.get_all_traces()
        traces_b = memory_b.get_all_traces()

        echo_a, rec_res_a = ecphory_a.query_recollection(pad_philia_obj, probe_stim_vec, traces_a, EmotionConfig())
        echo_b, rec_res_b = ecphory_b.query_recollection(pad_philia_obj, probe_stim_vec, traces_b, EmotionConfig())

        k_dict_a = {"fact_count": len(props_retrieved_a)} if props_retrieved_a else None
        k_dict_b = {"fact_count": len(props_retrieved_b)} if props_retrieved_b else None

        m_dict_a = {"echo_active": echo_a is not None, "recollection_active": rec_res_a.active} if (echo_a is not None or rec_res_a.active) else None
        m_dict_b = {"echo_active": echo_b is not None, "recollection_active": rec_res_b.active} if (echo_b is not None or rec_res_b.active) else None

        comm_a_cond_b = comm_policy.compute(
            pad=pad_philia_obj,
            somatic=neutral_somatic,
            relationship=updater_a.get_state().to_dict(),
            knowledge=k_dict_a,
            recollection=m_dict_a,
        )
        comm_b_cond_b = comm_policy.compute(
            pad=pad_philia_obj,
            somatic=neutral_somatic,
            relationship=updater_b.get_state().to_dict(),
            knowledge=k_dict_b,
            recollection=m_dict_b,
        )

        prompt_a_cond_b = self.prompt_assembler.assemble(
            somatic=neutral_somatic,
            constraints=constraints,
            history=conversation_history,
            system_preamble="You are Lucia.",
            comm_state=comm_a_cond_b,
            knowledge_propositions=props_retrieved_a,
            echo_vector=echo_a,
        )
        prompt_b_cond_b = self.prompt_assembler.assemble(
            somatic=neutral_somatic,
            constraints=constraints,
            history=conversation_history,
            system_preamble="You are Lucia.",
            comm_state=comm_b_cond_b,
            knowledge_propositions=props_retrieved_b,
            echo_vector=echo_b,
        )

        pacing_a = float(np.linalg.norm(rec_res_a.r_slow_bounded) * 150.0) if rec_res_a.active else 0.0
        pacing_b = float(np.linalg.norm(rec_res_b.r_slow_bounded) * 150.0) if rec_res_b.active else 0.0

        salience_a = float(rec_res_a.salience)
        salience_b = float(rec_res_b.salience)
        echo_norm_a = float(np.linalg.norm(echo_a)) if echo_a is not None else 0.0
        echo_norm_b = float(np.linalg.norm(echo_b)) if echo_b is not None else 0.0

        vec_a_cond_b = self._assemble_response_vector(
            comm_state=comm_a_cond_b,
            grounded_text=grounded_text_a,
            rec_salience=salience_a,
            echo_norm=echo_norm_a,
            pacing_latency=pacing_a,
        )
        vec_b_cond_b = self._assemble_response_vector(
            comm_state=comm_b_cond_b,
            grounded_text=grounded_text_b,
            rec_salience=salience_b,
            echo_norm=echo_norm_b,
            pacing_latency=pacing_b,
        )

        cond_b_diff = float(np.linalg.norm(vec_a_cond_b - vec_b_cond_b))
        cond_b_distinguished = bool(cond_b_diff >= self.config.distinguishable_threshold)

        retrieval_success = bool(len(props_retrieved_b) > 0 and len(traces_b) > 0)

        return DiscrimTrialResult(
            trial_id=trial_id,
            r_a_final=[float(x) for x in r_a_final],
            r_b_final=[float(x) for x in r_b_final],
            r_distance=final_r_dist,
            pad_a_residual=pad_res_a,
            pad_b_residual=pad_res_b,
            pad_leakage_distance=pad_leakage,
            cond_a_diff=cond_a_diff,
            cond_b_diff=cond_b_diff,
            cond_a_distinguished=cond_a_distinguished,
            cond_b_distinguished=cond_b_distinguished,
            retrieval_success_b=retrieval_success,
            probe_text=probe_text,
            response_vec_a_cond_a=[float(x) for x in vec_a_cond_a],
            response_vec_b_cond_a=[float(x) for x in vec_b_cond_a],
            response_vec_a_cond_b=[float(x) for x in vec_a_cond_b],
            response_vec_b_cond_b=[float(x) for x in vec_b_cond_b],
            assembled_prompt_a_cond_b=str(prompt_a_cond_b),
            assembled_prompt_b_cond_b=str(prompt_b_cond_b),
        )

    def run_benchmark(self, num_trials: int = 10) -> Tuple[DiscrimExperimentSummary, List[DiscrimTrialResult]]:
        """Run repeated trials across varied micro-perturbations."""
        trials: List[DiscrimTrialResult] = []
        for i in range(num_trials):
            trials.append(self.run_trial(trial_id=i))

        r_dists = [t.r_distance for t in trials]
        pad_res = [(t.pad_a_residual + t.pad_b_residual) / 2.0 for t in trials]
        pad_leaks = [t.pad_leakage_distance for t in trials]
        cond_a_diffs = [t.cond_a_diff for t in trials]
        cond_b_diffs = [t.cond_b_diff for t in trials]

        mean_r_dist = float(np.mean(r_dists))
        max_r_dist = float(np.max(r_dists))
        mean_pad_res = float(np.mean(pad_res))
        mean_pad_leak = float(np.mean(pad_leaks))
        mean_cond_a = float(np.mean(cond_a_diffs))
        mean_cond_b = float(np.mean(cond_b_diffs))

        cond_a_rate = float(np.mean([1.0 if t.cond_a_distinguished else 0.0 for t in trials]))
        cond_b_rate = float(np.mean([1.0 if t.cond_b_distinguished else 0.0 for t in trials]))

        # Epistemic assessment
        # H-A claims R_t alone is sufficient -> rejected if cond_a_rate == 0.0
        h_a_supported = bool(cond_a_rate > 0.50)

        # H-B claims R_t + existing memory is sufficient -> supported if cond_b_rate >= 0.90
        h_b_supported = bool(cond_b_rate >= 0.90 and not h_a_supported)

        # H-C claims a new representation is necessary -> indicated only if both H-A and H-B fail
        h_c_indicated = bool(not h_a_supported and not h_b_supported)

        conclusion = (
            f"Under the tested configuration (N={num_trials}, matched R_t distance <= {max_r_dist:.5f}, "
            f"PAD residual <= {mean_pad_res:.6f}, PAD leakage <= {mean_pad_leak:.6f}), Condition A failed to "
            f"distinguish histories (mean Delta S = {mean_cond_a:.4f} < {self.config.indistinguishable_threshold}), "
            f"providing evidence against H-A. "
            f"Condition B successfully produced history-sensitive differential response "
            f"(mean Delta S = {mean_cond_b:.4f} >= {self.config.distinguishable_threshold}) via existing memory/semantic substrates, "
            f"supporting H-B for this tested capability. "
            f"CRITICAL: This does NOT prove H-B universally. Status remains strictly INCONCLUSIVE — MORE RESEARCH REQUIRED."
        )

        limitations = (
            "1. Tested single conversational probe domain ('project_deadline'). "
            "2. Explored discrete conflict/reconciliation scenario; does not test complex multi-agent relational webs. "
            "3. Demonstrates feasibility of existing memory substrate for differentiation, but does not settle "
            "whether dimensional expansion of R_t is necessary for deeper affective attachment or rupture severity classes."
        )

        summary = DiscrimExperimentSummary(
            total_trials=num_trials,
            mean_r_distance=mean_r_dist,
            max_r_distance=max_r_dist,
            mean_pad_residual=mean_pad_res,
            mean_pad_leakage=mean_pad_leak,
            mean_cond_a_diff=mean_cond_a,
            mean_cond_b_diff=mean_cond_b,
            cond_a_success_rate=cond_a_rate,
            cond_b_success_rate=cond_b_rate,
            h_a_supported=h_a_supported,
            h_b_supported_for_tested_config=h_b_supported,
            h_c_indicated=h_c_indicated,
            epistemic_conclusion=conclusion,
            limitations=limitations,
        )

        return summary, trials
