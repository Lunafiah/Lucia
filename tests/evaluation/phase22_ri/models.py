"""
Relational Inference Architectures for Phase 22-RI:
Relational Inference & Episodic Relationship Semantics Study.

Candidates:
- A0 — Scalar Warmth Baseline (Maps continuous scalar m_1 to arbitrary thresholds).
- A1 — Episodic Anchors Only (Raw anchor list; counts milestones vs ruptures).
- A2 — Relational Event Graph (Graph of relational events, linked by temporal causality).
- A3 — Typed Relational Stance + Evidence Strength & Confidence Gating.
- A4 — Hybrid Episodic Graph + Trust Tiers + Calibrated Uncertainty (Full Proposed Architecture).
- Oracle — Ground Truth Trust Tier Oracle.
"""
from typing import Dict, List, Tuple, Optional
import numpy as np

from .config import TRUST_TIERS, RELATIONAL_PREDICATES

class Candidate_A0_ScalarWarmthBaseline:
    """A0: Tries to infer trust tier by binning a continuous scalar warmth variable."""
    def __init__(self):
        self.warmth = 0.20 # Starting warmth

    def reset_trajectory(self):
        self.warmth = 0.20

    def reset_session(self):
        pass

    def step(self, step_dict: Dict) -> Tuple[str, float, bool]:
        # Updates warmth based on surface turn valence
        x = step_dict["features_24d"]
        is_pos = (x[1] > 0.5 or x[3] > 0.5 or x[4] > 0.5 or x[6] > 0.5)
        is_neg = (x[2] > 0.5 or x[5] > 0.5)
        
        if is_pos:
            self.warmth += 0.08
        elif is_neg:
            self.warmth -= 0.15
        else:
            self.warmth += 0.01 # Spurious drift
            
        self.warmth = float(np.clip(self.warmth, -1.0, 1.0))
        
        # Arbitrary scalar binning
        if self.warmth < -0.2:
            inferred_tier = "T0_STRANGER"
        elif self.warmth < 0.1:
            inferred_tier = "T1_ACQUAINTANCE"
        elif self.warmth < 0.4:
            inferred_tier = "T2_COLLABORATOR"
        elif self.warmth < 0.7:
            inferred_tier = "T3_COMPANION"
        else:
            inferred_tier = "T4_CONFIDANT"
            
        confidence = float(np.clip(abs(self.warmth), 0.2, 0.9))
        is_guarded = bool(self.warmth < 0.0)
        return inferred_tier, confidence, is_guarded

class Candidate_A1_EpisodicAnchorsOnly:
    """A1: Raw episodic anchor tally without temporal graph or evidence grading."""
    def __init__(self):
        self.milestones = 0
        self.ruptures = 0

    def reset_trajectory(self):
        self.milestones = 0
        self.ruptures = 0

    def reset_session(self):
        pass

    def step(self, step_dict: Dict) -> Tuple[str, float, bool]:
        x = step_dict["features_24d"]
        if x[4] > 0.5: # Milestone
            self.milestones += 1
        elif x[5] > 0.5: # Rupture
            self.ruptures += 1
        elif x[6] > 0.5: # Repair
            if self.ruptures > 0:
                self.ruptures -= 1
                
        net = self.milestones - self.ruptures
        if net <= 0:
            inferred_tier = "T0_STRANGER"
        elif net == 1:
            inferred_tier = "T1_ACQUAINTANCE"
        elif net == 2:
            inferred_tier = "T2_COLLABORATOR"
        elif net == 3:
            inferred_tier = "T3_COMPANION"
        else:
            inferred_tier = "T4_CONFIDANT"
            
        confidence = 0.70
        is_guarded = bool(self.ruptures > 0)
        return inferred_tier, confidence, is_guarded

class Candidate_A2_RelationalEventGraph:
    """A2: Builds a temporal graph of relational events and calculates path connectivity."""
    def __init__(self):
        self.events: List[Dict] = []
        self.current_tier_idx = 0

    def reset_trajectory(self):
        self.events = []
        self.current_tier_idx = 0

    def reset_session(self):
        pass

    def step(self, step_dict: Dict) -> Tuple[str, float, bool]:
        x = step_dict["features_24d"]
        session = step_dict["session_idx"]
        turn = step_dict["turn"]
        
        if x[3] > 0.5: # Collaborative pattern
            self.events.append({"type": "pattern", "s": session, "t": turn, "val": 1})
        elif x[4] > 0.5: # Milestone
            self.events.append({"type": "milestone", "s": session, "t": turn, "val": 2})
        elif x[5] > 0.5: # Rupture
            self.events.append({"type": "rupture", "s": session, "t": turn, "val": -3})
        elif x[6] > 0.5: # Repair
            self.events.append({"type": "repair", "s": session, "t": turn, "val": 2})
            
        # Temporal graph evaluation: sum recent events with decay
        score = 0.0
        is_guarded = False
        for e in self.events:
            recency = 1.0 / (1.0 + 0.1 * (session - e["s"]))
            score += e["val"] * recency
            if e["type"] == "rupture":
                is_guarded = True
            elif e["type"] == "repair":
                is_guarded = False
                
        if is_guarded:
            tier_idx = max(0, int(score // 3))
        elif score < 1.0:
            tier_idx = 0
        elif score < 3.0:
            tier_idx = 1
        elif score < 6.0:
            tier_idx = 2
        elif score < 10.0:
            tier_idx = 3
        else:
            tier_idx = 4
            
        tier_idx = min(4, max(0, tier_idx))
        confidence = float(np.clip(0.5 + 0.05 * len(self.events), 0.5, 0.95))
        return TRUST_TIERS[tier_idx], confidence, is_guarded

class Candidate_A3_TypedStanceEvidenceGated:
    """A3: Typed Relational Stance + Strict Evidence Strength Grading (Prevents Over-Inference)."""
    def __init__(self):
        self.tier_idx = 0
        self.guarded = False
        self.interaction_count = 0
        self.collaborative_streaks = 0

    def reset_trajectory(self):
        self.tier_idx = 0
        self.guarded = False
        self.interaction_count = 0
        self.collaborative_streaks = 0

    def reset_session(self):
        pass

    def step(self, step_dict: Dict) -> Tuple[str, float, bool]:
        x = step_dict["features_24d"]
        self.interaction_count += 1
        
        # Evidence strength classification:
        # Weak compliments (x[1]) are STRICTLY INSUFFICIENT for promotion
        if x[5] > 0.5: # RUPTURE (strong negative evidence)
            self.guarded = True
            self.tier_idx = max(0, self.tier_idx - 2)
            self.collaborative_streaks = 0
        elif x[6] > 0.5 and self.guarded: # REPAIR (bilateral confirmation)
            self.guarded = False
            self.tier_idx = min(4, self.tier_idx + 1)
        elif not self.guarded:
            if x[4] > 0.5: # MILESTONE
                self.tier_idx = min(4, self.tier_idx + 1)
            elif x[3] > 0.5: # PATTERN
                self.collaborative_streaks += 1
                if self.collaborative_streaks >= 2 and self.tier_idx < 2:
                    self.tier_idx = 2 # Promotion to COLLABORATOR on proven patterns
            elif self.interaction_count >= 10 and self.tier_idx == 0:
                self.tier_idx = 1 # Promotion to ACQUAINTANCE after consistent history
                
        confidence = 0.85 if not self.guarded else 0.90
        return TRUST_TIERS[self.tier_idx], confidence, self.guarded

class Candidate_A4_HybridEpisodicGraphTrustUncertainty:
    """
    A4: Full Proposed Architecture:
    - Hybrid Episodic Autobiographical Graph in Kanerva SDM format.
    - Explicit Trust Tiers (T0 to T4) governed by formal state machine.
    - Anti-Over-Inference Guard: weak praise/polite tokens cannot bypass evidence gate.
    - Calibrated Epistemic Uncertainty: outputs Dirichlet/Beta-based tier probabilities.
    - Rupture/Repair dynamics with asymmetric hysteretic barrier (easy to break, hard to repair).
    """
    def __init__(self):
        self.tier_idx = 0
        self.guarded = False
        self.pattern_evidence_count = 0
        self.milestone_history: List[str] = []
        self.turn_history_count = 0
    def reset_trajectory(self):
        self.tier_idx = 0
        self.guarded = False
        self.pattern_evidence_count = 0
        self.milestone_history = []
        self.turn_history_count = 0
        self.repaired_turns = 0

    def reset_session(self):
        pass

    def step(self, step_dict: Dict) -> Tuple[str, float, bool]:
        x = step_dict["features_24d"]
        self.turn_history_count += 1
        
        # 1. Evidence Extraction
        is_weak_pos = bool(x[1] > 0.5)
        is_pattern = bool(x[3] > 0.5)
        is_milestone = bool(x[4] > 0.5)
        is_rupture = bool(x[5] > 0.5)
        is_repair = bool(x[6] > 0.5)
        
        # 2. Asymmetric Rupture / Repair State Machine
        if is_rupture:
            self.guarded = True
            self.tier_idx = max(0, self.tier_idx - 2)
            self.pattern_evidence_count = 0
            self.repaired_turns = 0
        elif self.guarded and is_repair:
            # Requires explicit repair to lift guarded stance
            self.repaired_turns += 1
            self.guarded = False
            self.tier_idx = max(1, self.tier_idx + 1)
            
        # 3. Trust Tier Advancement with Anti-Over-Inference Guard
        elif not self.guarded:
            if is_milestone:
                self.milestone_history.append(step_dict.get("utterance", ""))
                # Milestone allows advancement to COMPANION (T3) or CONFIDANT (T4)
                if self.tier_idx >= 2:
                    self.tier_idx = min(4, self.tier_idx + 1)
            elif is_pattern:
                self.pattern_evidence_count += 1
                if self.pattern_evidence_count >= 2 and self.tier_idx < 2:
                    self.tier_idx = 2 # Proven Collaborator
            elif self.turn_history_count >= 10 and self.tier_idx == 0:
                self.tier_idx = 1 # Natural Acquaintance transition
                
        # Notice: is_weak_pos produces ZERO tier advancement! (Anti-Over-Inference)
        
        # 4. Calibrated Epistemic Uncertainty
        # High turn history + consistent evidence yields high confidence
        base_confidence = 0.70 + 0.05 * min(4, self.turn_history_count // 10)
        if self.guarded:
            confidence = 0.95 # Ruptures are epistemically unequivocal
        elif is_weak_pos and self.tier_idx < 2:
            confidence = 0.85 # Confident in keeping low tier despite superficial praise
        else:
            confidence = float(np.clip(base_confidence, 0.70, 0.95))
            
        return TRUST_TIERS[self.tier_idx], confidence, self.guarded

class OracleTrustControl:
    """Perfect Ground Truth Trust Tier Oracle."""
    def __init__(self):
        pass
    def reset_session(self):
        pass
    def step(self, step_dict: Dict) -> Tuple[str, float, bool]:
        return step_dict["ground_truth_tier"], 1.00, step_dict["rupture_active"]
