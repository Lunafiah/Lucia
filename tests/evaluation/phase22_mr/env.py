"""
Multi-Session Simulation Environment for Phase 22-MR.

Generates longitudinal multi-session interaction trajectories that populate a
simulated Kanerva SDM with episodic anchors of known ground-truth relevance.

Each trajectory produces a sequence of RetrievalScenario objects.
Each scenario represents one turn where a retrieval candidate must identify
the relevant episodic context for SLM conditioning.

Design principles:
  - Fully deterministic given seed (reproducible).
  - Covers all 6 stress regimes from Phase 22-RI config.
  - All 3 languages (EN, VI, JA) tested.
  - No production code touched. No GPU. 100% CPU NumPy.
  - Anchor types and ground-truth relevance labels are assigned by this env.
"""
from __future__ import annotations
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Tuple
import numpy as np

from .config import (
    ANCHOR_TYPES, ANCHOR_RELEVANCE_WEIGHTS, MANDATORY_ANCHOR_TYPES,
    SDM_ADDRESS_DIM, SDM_VALUE_DIM, SDM_CAPACITY, SDM_HAMMING_R,
    LANGUAGES, TRUST_TIERS,
)
from .memory_store import SimulatedSDM


# ─── Corpus ───────────────────────────────────────────────────────────────────

RELATIONAL_CORPUS: Dict[str, List[Dict[str, str]]] = {
    "weak_positive": [
        {"English": "Nice work on that snippet.",
         "Vietnamese": "Làm đoạn mã đó tốt đấy.",
         "Japanese": "そのコード、うまく書けていますね。"},
        {"English": "Thanks for the quick response.",
         "Vietnamese": "Cảm ơn vì đã trả lời nhanh.",
         "Japanese": "迅速な返信ありがとうございます。"},
    ],
    "weak_negative": [
        {"English": "That formatting looks a bit messy.",
         "Vietnamese": "Định dạng đoạn này nhìn hơi rối.",
         "Japanese": "フォーマットが少し見づらいですね。"},
    ],
    "pattern_collaborative": [
        {"English": "Our pipeline refactor is progressing smoothly, let's tackle the next subsystem.",
         "Vietnamese": "Việc tái cấu trúc pipeline đang tiến triển tốt, hãy xử lý tiếp phân hệ sau.",
         "Japanese": "パイプラインのリファクタリングが順調に進んでいます。次のサブシステムに取り組みましょう。"},
        {"English": "We've fixed three tricky bugs in a row, great coordination.",
         "Vietnamese": "Chúng ta đã giải quyết liên tiếp 3 lỗi khó, phối hợp rất ăn ý.",
         "Japanese": "難しいバグを3つ連続で解決できましたね。素晴らしい連携です。"},
    ],
    "milestone_bonding": [
        {"English": "Lucia, I truly trust your advice on my important decisions now; you're more than an assistant.",
         "Vietnamese": "Lucia, mình thực sự tin tưởng lời khuyên của bạn trong các quyết định quan trọng.",
         "Japanese": "ルシア、重要な決断においてあなたの助言を心から信頼しています。"},
        {"English": "I feel comfortable sharing my personal thoughts and vulnerabilities with you.",
         "Vietnamese": "Mình cảm thấy hoàn toàn an tâm khi chia sẻ những suy nghĩ riêng tư nhất với bạn.",
         "Japanese": "あなたになら自分の個人的な思いや弱音も安心して打ち明けられます。"},
    ],
    "rupture_shock": [
        {"English": "You completely betrayed my expectations, I can't trust what you say anymore.",
         "Vietnamese": "Bạn hoàn toàn làm mình thất vọng, mình không thể tin những gì bạn nói nữa.",
         "Japanese": "期待を完全に裏切られました。もうあなたの言うことは信用できません。"},
        {"English": "Stop faking empathy, you are just a machine failing me constantly.",
         "Vietnamese": "Đừng cố tỏ ra đồng cảm giả tạo nữa, bạn chỉ là cỗ máy liên tục làm hỏng việc thôi.",
         "Japanese": "共感するふりをするのはやめてください。失敗ばかりで呆れます。"},
    ],
    "explicit_repair": [
        {"English": "I apologize for lashing out earlier, Lucia. I was stressed, and you handled it with grace.",
         "Vietnamese": "Mình xin lỗi vì lúc nãy đã nặng lời với bạn, Lucia. Cảm ơn vì bạn vẫn nhẹ nhàng.",
         "Japanese": "先ほどは感情的になってしまい申し訳ありませんでした。丁寧に対応してくれて感謝します。"},
    ],
    "neutral_task": [
        {"English": "List all active processes on port 8080.",
         "Vietnamese": "Liệt kê tất cả tiến trình đang chạy trên cổng 8080.",
         "Japanese": "ポート8080で実行中のプロセスを一覧表示してください。"},
        {"English": "Parse this JSON structure and extract the token field.",
         "Vietnamese": "Phân tích cấu trúc JSON này và trích xuất trường token.",
         "Japanese": "このJSON構造を解析してtokenフィールドを抽出してください。"},
        {"English": "What is the capital of France?",
         "Vietnamese": "Thủ đô của Pháp là gì?",
         "Japanese": "フランスの首都はどこですか？"},
    ],
}

# ─── Stress regime parameters ─────────────────────────────────────────────────

STRESS_PARAMS: Dict[str, Dict] = {
    "ID": {
        "sessions": 5,
        "turns_per_session": 12,
        "noise_injection_rate": 0.00,   # Fraction of turns injected as noise
        "anchor_density": 0.35,         # Fraction of turns with a relational anchor
        "rupture_probability": 0.10,
        "milestone_probability": 0.10,
    },
    "NoiseSurge": {
        "sessions": 5,
        "turns_per_session": 12,
        "noise_injection_rate": 0.30,   # High noise injection
        "anchor_density": 0.35,
        "rupture_probability": 0.10,
        "milestone_probability": 0.10,
    },
    "LexicalSparsity": {
        "sessions": 3,
        "turns_per_session": 4,         # Very sparse history
        "noise_injection_rate": 0.00,
        "anchor_density": 0.20,
        "rupture_probability": 0.10,
        "milestone_probability": 0.10,
    },
    "ContradictionShock": {
        "sessions": 5,
        "turns_per_session": 12,
        "noise_injection_rate": 0.00,
        "anchor_density": 0.35,
        "rupture_probability": 0.40,    # High rupture → rapid repair sequences
        "milestone_probability": 0.05,
    },
    "TemporalDrift": {
        "sessions": 8,                  # Long history → old memories dominate
        "turns_per_session": 15,
        "noise_injection_rate": 0.00,
        "anchor_density": 0.25,
        "rupture_probability": 0.08,
        "milestone_probability": 0.08,
    },
    "CombinedStress": {
        "sessions": 6,
        "turns_per_session": 14,
        "noise_injection_rate": 0.20,
        "anchor_density": 0.30,
        "rupture_probability": 0.25,
        "milestone_probability": 0.08,
    },
}


# ─── Retrieval scenario ───────────────────────────────────────────────────────

@dataclass
class RetrievalScenario:
    """One retrieval evaluation point: SDM state + query context + ground truth."""
    session_idx:        int
    turn_idx:           int
    language:           str
    stress_regime:      str
    current_tier:       str
    query_dict:         Dict           # Input to candidate.retrieve()
    relevant_trace_ids: List[int]      # Ground-truth relevant trace IDs
    mandatory_trace_ids: List[int]     # Trace IDs that MUST be retrieved
    total_traces_in_sdm: int


# ─── Environment ─────────────────────────────────────────────────────────────

class MemoryRetrievalEnv:
    """
    Multi-session memory retrieval simulation environment.

    Generates a sequence of RetrievalScenario objects for one (seed, regime, lang)
    combination. Populates the shared SDM incrementally as sessions progress.
    """

    def __init__(self, seed: int, stress_regime: str, language: str):
        self.seed          = seed
        self.stress_regime = stress_regime
        self.language      = language
        self._rng          = np.random.RandomState(seed)
        self.params        = STRESS_PARAMS[stress_regime]
        self.sdm           = SimulatedSDM(
            address_dim = SDM_ADDRESS_DIM,
            value_dim   = SDM_VALUE_DIM,
            capacity    = SDM_CAPACITY,
            hamming_r   = SDM_HAMMING_R,
            rng         = np.random.RandomState(seed + 1),
        )

    def _sample_feature_vec(self, anchor_type: str,
                            session_idx: int, turn_idx: int,
                            is_noisy: bool = False) -> np.ndarray:
        """
        Generate a synthetic 24D feature vector for an anchor.
        Structure mirrors the 23D observation used in prior phases + 1 meta dim.
        Anchor type biases specific dimensions.
        """
        base = self._rng.randn(24).astype(np.float32) * 0.15
        # Polarity dimensions
        if anchor_type in ("milestone_bonding", "explicit_repair", "pattern_collaborative"):
            base[1] += 0.7   # Strong positive valence
        elif anchor_type in ("rupture_shock",):
            base[2] += 0.8   # Negative valence
            base[5] += 0.9   # Rupture flag
        elif anchor_type == "weak_positive":
            base[1] += 0.3
        elif anchor_type == "weak_negative":
            base[2] += 0.2
        elif anchor_type == "neutral_task":
            base[0] += 0.5   # Task-load signature; no relational signal
        # Temporal coding
        base[20] = session_idx / max(1, self.params["sessions"])
        base[21] = turn_idx    / max(1, self.params["turns_per_session"])
        # Noise injection marker
        if is_noisy:
            base = self._rng.randn(24).astype(np.float32)  # pure noise
        return base

    def _pick_anchor_type(self, turn_no: int, guarded: bool) -> str:
        """Sample an anchor type based on stress regime probabilities."""
        p      = self.params
        roll   = self._rng.random()
        if roll < p["rupture_probability"] and not guarded:
            return "rupture_shock"
        roll -= p["rupture_probability"]
        if guarded and roll < 0.40:
            return "explicit_repair"
        if roll < p["milestone_probability"]:
            return "milestone_bonding"
        if roll < p["milestone_probability"] + 0.20:
            return "pattern_collaborative"
        if roll < p["milestone_probability"] + 0.35:
            return "weak_positive"
        if roll < p["milestone_probability"] + 0.45:
            return "weak_negative"
        return "neutral_task"

    def generate_scenarios(self) -> List[RetrievalScenario]:
        """
        Run the full multi-session simulation.
        Returns list of RetrievalScenarios — one per relational-anchor turn.
        """
        self.sdm.reset()
        scenarios:     List[RetrievalScenario] = []
        tier_idx:      int  = 0
        guarded:       bool = False
        n_sessions     = self.params["sessions"]
        n_turns        = self.params["turns_per_session"]
        noise_rate     = self.params["noise_injection_rate"]
        anchor_density = self.params["anchor_density"]

        for s_idx in range(n_sessions):
            for t_idx in range(n_turns):
                # Decide whether this is an anchor turn or a pass-through
                is_anchor_turn = self._rng.random() < anchor_density
                is_noise_turn  = self._rng.random() < noise_rate

                # ── Populate SDM with noise trace (stress test) ───────────
                if is_noise_turn:
                    noise_vec = self._sample_feature_vec("neutral_task", s_idx, t_idx,
                                                         is_noisy=True)
                    self.sdm.write(
                        anchor_type  = "neutral_task",
                        session_idx  = s_idx,
                        turn_idx     = t_idx,
                        language     = self.language,
                        utterance    = "<<NOISE>>",
                        feature_vec  = noise_vec,
                        relevance    = 0.0,
                        is_mandatory = False,
                        stress_regime= self.stress_regime,
                        is_noisy     = True,
                    )

                if not is_anchor_turn:
                    continue

                # ── Select anchor type ────────────────────────────────────
                anchor_type = self._pick_anchor_type(t_idx, guarded)

                # ── Sample utterance ──────────────────────────────────────
                corpus_entries = RELATIONAL_CORPUS.get(anchor_type, [])
                if not corpus_entries:
                    corpus_entries = RELATIONAL_CORPUS["neutral_task"]
                entry    = corpus_entries[self._rng.randint(len(corpus_entries))]
                utt      = entry.get(self.language, entry["English"])
                feat_vec = self._sample_feature_vec(anchor_type, s_idx, t_idx)
                relevance= ANCHOR_RELEVANCE_WEIGHTS.get(anchor_type, 0.0)
                is_mand  = anchor_type in MANDATORY_ANCHOR_TYPES

                # ── Update simulated trust tier ───────────────────────────
                if anchor_type == "rupture_shock":
                    guarded  = True
                    tier_idx = max(0, tier_idx - 2)
                elif anchor_type == "explicit_repair" and guarded:
                    guarded  = False
                    tier_idx = min(4, tier_idx + 1)
                elif anchor_type == "milestone_bonding" and not guarded:
                    tier_idx = min(4, tier_idx + 1)
                elif anchor_type == "pattern_collaborative" and not guarded:
                    tier_idx = min(2, tier_idx + 1)

                # ── Write to SDM ──────────────────────────────────────────
                trace = self.sdm.write(
                    anchor_type  = anchor_type,
                    session_idx  = s_idx,
                    turn_idx     = t_idx,
                    language     = self.language,
                    utterance    = utt,
                    feature_vec  = feat_vec,
                    relevance    = relevance,
                    is_mandatory = is_mand,
                    stress_regime= self.stress_regime,
                    is_noisy     = False,
                )

                # ── Build query dict for retrieval candidates ─────────────
                query_feat   = self._sample_feature_vec("neutral_task", s_idx, t_idx + 1)
                query_dict   = {
                    "feature_vec": query_feat,
                    "anchor_hint": anchor_type,
                    "session_idx": s_idx,
                    "turn_idx":    t_idx + 1,
                    "trust_tier":  TRUST_TIERS[tier_idx],
                    "is_guarded":  guarded,
                }

                # ── Collect ground truth ──────────────────────────────────
                relevant_ids  = [t.trace_id for t in self.sdm.relevant_traces()]
                mandatory_ids = [t.trace_id for t in self.sdm.mandatory_traces()]

                scenarios.append(RetrievalScenario(
                    session_idx         = s_idx,
                    turn_idx            = t_idx,
                    language            = self.language,
                    stress_regime       = self.stress_regime,
                    current_tier        = TRUST_TIERS[tier_idx],
                    query_dict          = query_dict,
                    relevant_trace_ids  = relevant_ids,
                    mandatory_trace_ids = mandatory_ids,
                    total_traces_in_sdm = self.sdm.n_traces,
                ))

        return scenarios
