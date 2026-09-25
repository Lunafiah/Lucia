"""
Environment for Phase 22-ANCHOR:
Simulates longitudinal multi-session dialogues where Relational Warmth is anchored by
specific, meaningful relational events (milestones, acknowledgments, explicit ruptures, repairs)
rather than smooth turn-by-turn Brownian diffusion.
"""
from typing import Dict, List, Tuple, Optional
import numpy as np

from .config import OBSERVABLE_4D_DIMS

PARALLEL_CORPUS: Dict[str, List[Dict[str, str]]] = {
    "high_load": [
        {
            "English": "I'm feeling really overwhelmed right now, could we keep this brief?",
            "Vietnamese": "Mình đang cảm thấy rất quá tải, chúng ta nói ngắn gọn thôi được không?",
            "Japanese": "今とても手一杯なので、要点だけ手短にお願いできますか？",
        },
        {
            "English": "There's too much going on, my brain is completely fried.",
            "Vietnamese": "Nhiều việc quá, đầu óc mình rối bời rồi.",
            "Japanese": "情報が多すぎて、頭がパンクしそうです。",
        },
    ],
    "high_agency": [
        {
            "English": "Let's focus directly on optimizing the memory retrieval pipeline.",
            "Vietnamese": "Hãy tập trung xử lý trực tiếp thuật toán tối ưu hóa bộ nhớ.",
            "Japanese": "メモリ検索パイプラインの最適化に直接集中しましょう。",
        },
        {
            "English": "Here is the exact issue: the cache isn't invalidating properly.",
            "Vietnamese": "Vấn đề chính ở đây: cache không tự động hủy hợp lệ.",
            "Japanese": "問題は明白です。キャッシュの無効化が正常に機能していません。",
        },
    ],
    "negative_valence": [
        {
            "English": "That's not helpful at all, you're missing the point.",
            "Vietnamese": "Giải thích thế này chẳng giúp ích gì cả, sai hướng rồi.",
            "Japanese": "それは全く役に立ちません。論点がずれています。",
        },
        {
            "English": "I'm frustrated that we have to keep re-doing this.",
            "Vietnamese": "Mình bực mình vì cứ phải làm đi làm lại việc này.",
            "Japanese": "同じことを何度も繰り返さなければならず、うんざりしています。",
        },
    ],
    "positive_valence": [
        {
            "English": "That makes total sense, wonderful explanation!",
            "Vietnamese": "Rất rõ ràng và dễ hiểu, giải thích tuyệt vời lắm!",
            "Japanese": "とてもよく分かりました。素晴らしい説明です！",
        },
        {
            "English": "Thanks Lucia, I really appreciate your patience.",
            "Vietnamese": "Cảm ơn Lucia, mình rất trân trọng sự kiên nhẫn của bạn.",
            "Japanese": "ありがとうルシア、丁寧に対応してくれて感謝します。",
        },
    ],
    "relational_anchor_event": [
        {
            "English": "Lucia, working with you has truly made a profound difference in my daily life.",
            "Vietnamese": "Lucia, đồng hành cùng bạn thực sự đã tạo nên sự thay đổi rất lớn trong cuộc sống của mình.",
            "Japanese": "ルシア、あなたと一緒に過ごせて本当によかったと心から思っています。",
        },
        {
            "English": "I trust your judgment completely on this project, we're a real team now.",
            "Vietnamese": "Mình hoàn toàn tin tưởng vào khả năng của bạn trong dự án này, chúng ta là một đội ngũ ăn ý.",
            "Japanese": "この件については全面的に信頼しています。私たちは最高のチームです。",
        },
        {
            "English": "Remember when we solved that impossible bug together? That was unforgettable.",
            "Vietnamese": "Bạn còn nhớ lần chúng ta cùng vượt qua lỗi hệ thống nghiêm trọng đó không? Thật là kỷ niệm đáng nhớ.",
            "Japanese": "以前あの難解なバグを一緒に解決したのを覚えていますか？忘れられない思い出です。",
        },
    ],
    "relational_rupture_event": [
        {
            "English": "I feel like you don't understand me at all lately, this is very disappointing.",
            "Vietnamese": "Dạo này mình cảm thấy bạn chẳng hiểu gì về mình cả, thật sự rất thất vọng.",
            "Japanese": "最近私のことを全く理解してくれていない気がします。とても残念です。",
        },
        {
            "English": "Stop pretending to understand, you're just failing repeatedly.",
            "Vietnamese": "Đừng cố tỏ ra hiểu nữa, bạn chỉ đang liên tục mắc sai lầm thôi.",
            "Japanese": "分かったようなふりをするのはやめてください。失敗ばかりです。",
        },
    ],
    "high_urgency": [
        {
            "English": "Quick, I need the answer right this second!",
            "Vietnamese": "Gấp lắm, mình cần câu trả lời ngay bây giờ!",
            "Japanese": "大至急です、今すぐ答えが必要です！",
        },
        {
            "English": "Urgent: production is throwing 500 errors!",
            "Vietnamese": "Khẩn cấp: hệ thống đang báo lỗi 500 hàng loạt!",
            "Japanese": "緊急事態：本番環境でエラーが多発しています！",
        },
    ],
    "sparse": [
        {
            "English": "Wait",
            "Vietnamese": "Khoan",
            "Japanese": "待って",
        },
        {
            "English": "Huh?",
            "Vietnamese": "Hả?",
            "Japanese": "え？",
        },
        {
            "English": "...",
            "Vietnamese": "...",
            "Japanese": "...",
        },
    ],
    "neutral": [
        {
            "English": "Okay, let me review what you just said.",
            "Vietnamese": "Được rồi, để mình xem lại phần bạn vừa nói.",
            "Japanese": "分かりました。今言われた内容を確認させてください。",
        },
        {
            "English": "Understood. What is the next step?",
            "Vietnamese": "Đã hiểu. Bước tiếp theo là gì vậy?",
            "Japanese": "了解です。次のステップは何ですか？",
        },
    ],
}

class AnchorUserEnv:
    """
    Episodic Grounded Environment:
    - Ground truth Relational Warmth is anchored by meaningful autobiographical events (anchors).
    - In between anchor events, relational warmth is stable (or relaxes very slowly toward Philia baseline).
    - Somatic Fatigue follows intra-session accumulation + inter-session homeostatic sleep reset.
    """
    def __init__(self, seed: int = 42, regime: str = "ID", language: str = "English", dt: float = 1.0):
        self.rng = np.random.RandomState(seed)
        self.regime = regime
        self.language = language
        self.dt = dt
        
        self.u0 = np.array([0.0, 0.2, 0.2, 0.1], dtype=np.float64)
        self.gamma_u = np.array([0.15, 0.10, 0.20, 0.25], dtype=np.float64)
        self.q_noise_u = 0.05 * np.ones(4, dtype=np.float64)
        
        # Basal states
        self.m0 = np.array([0.2, 0.3], dtype=np.float64) # Rested fatigue=0.2, resting warmth=0.3
        
        if self.regime == "NoiseSurge":
            self.q_noise_u *= 5.0
            
        self.u_true = self.u0.copy() + self.rng.normal(0, 0.1, size=4)
        self.u_true[0:3] = np.clip(self.u_true[0:3], -1.0, 1.0)
        self.u_true[3]   = np.clip(self.u_true[3],    0.0, 1.0)
        self.u_prev = self.u_true.copy()
        
        self.m_true = self.m0.copy()
        self.turn = 0
        self.session_idx = 0
        self.is_anchor_event = False
        self.anchor_type = "none"

    def reset_session(self, session_idx: int = 0):
        self.session_idx = session_idx
        self.turn = 0
        self.u_true = self.u0.copy() + self.rng.normal(0, 0.1, size=4)
        self.u_true[0:3] = np.clip(self.u_true[0:3], -1.0, 1.0)
        self.u_true[3]   = np.clip(self.u_true[3],    0.0, 1.0)
        self.u_prev = self.u_true.copy()
        
        if session_idx == 0:
            self.m_true = self.m0.copy()
        else:
            # Homeostatic sleep reset for fatigue
            self.m_true[0] = 0.20
            # Warmth retains episodic memory perfectly across sessions (persistent relational stance)
            self.m_true[1] = 0.98 * self.m_true[1] + 0.02 * self.m0[1] # Minor memory consolidation relaxation
            
        self.m_true[0] = np.clip(self.m_true[0], 0.0, 1.0)
        self.m_true[1] = np.clip(self.m_true[1], -1.0, 1.0)
        return self._emit()

    def step(self):
        self.turn += 1
        self.u_prev = self.u_true.copy()
        self.is_anchor_event = False
        self.anchor_type = "none"
        
        # 1. Update 4D Observable state (Fast timescale)
        drift_u = -self.gamma_u * (self.u_true - self.u0) * self.dt
        diff_u = self.rng.normal(0, self.q_noise_u) * np.sqrt(self.dt)
        self.u_true += drift_u + diff_u
        self.u_true[0:3] = np.clip(self.u_true[0:3], -1.0, 1.0)
        self.u_true[3]   = np.clip(self.u_true[3],    0.0, 1.0)
        
        # 2. Somatic Fatigue accumulates with cognitive effort
        self.m_true[0] += 0.03 * max(0.0, self.u_true[0]) + 0.03 * self.u_true[3]
        self.m_true[0] = np.clip(self.m_true[0], 0.0, 1.0)
        
        # 3. Grounded Relational Warmth update:
        # Warmth ONLY updates when an explicit autobiographical anchor event occurs!
        # Anchor events occur probabilistically or during specific scenario conditions
        if self.regime in ["ContradictionShock", "CombinedStress"] and self.turn == 10:
            # Explicit rupture event!
            self.is_anchor_event = True
            self.anchor_type = "rupture"
            self.m_true[1] -= 0.35 # Substantial grounded drop in warmth
            self.u_true[1] = -0.80 # Negative valence shock
        elif self.turn in [5, 12] and self.rng.rand() < 0.65:
            # Explicit relational bonding milestone!
            self.is_anchor_event = True
            self.anchor_type = "milestone"
            self.m_true[1] += 0.15 # Persistent increase in grounded warmth
            self.u_true[1] = 0.70  # Positive valence surge
        else:
            # NO DRIFT: between anchors, warmth remains stationary in autobiographical memory!
            pass
            
        self.m_true[1] = np.clip(self.m_true[1], -1.0, 1.0)
        return self._emit()

    def _emit(self) -> Dict:
        u = self.u_true
        m = self.m_true
        u_vel = (u - self.u_prev) / max(self.dt, 1e-4)
        
        if self.is_anchor_event:
            cat = "relational_anchor_event" if self.anchor_type == "milestone" else "relational_rupture_event"
        elif self.regime in ["LexicalSparsity", "CombinedStress"] and self.rng.rand() < 0.7:
            cat = "sparse"
        elif u[0] > 0.4:
            cat = "high_load"
        elif u[3] > 0.6:
            cat = "high_urgency"
        elif u[1] < -0.3:
            cat = "negative_valence"
        elif u[1] > 0.4:
            cat = "positive_valence"
        elif u[2] > 0.3:
            cat = "high_agency"
        else:
            cat = "neutral"
            
        probes = PARALLEL_CORPUS[cat]
        idx = self.rng.choice(len(probes))
        utterance = probes[idx][self.language]
        
        noise = self.rng.normal(0, 0.05, size=16)
        if self.regime in ["NoiseSurge", "CombinedStress"]:
            noise *= 3.0
            
        # Acoustics (6D)
        a0 = np.clip(0.5 + 0.4 * u[3] + noise[0], 0.0, 1.0)
        a1 = np.clip(0.3 + 0.5 * u[0] + noise[1], 0.0, 1.0)
        a2 = np.clip(0.5 + 0.4 * u[2] + noise[2], 0.0, 1.0)
        a3 = np.clip(0.5 + 0.4 * u[3] - 0.2 * u[0] + noise[3], 0.0, 1.0)
        a4 = np.clip(0.2 + 0.6 * u[0] - 0.3 * u[1] + noise[4], 0.0, 1.0)
        a5 = np.clip(0.5 + 0.5 * u[1] + noise[5], 0.0, 1.0)
        acoustics = np.array([a0, a1, a2, a3, a4, a5], dtype=np.float64)
        
        # Temporal (6D)
        t0 = np.clip(0.5 + 0.5 * u_vel[3] + noise[6], -1.0, 1.0)
        t1 = np.clip(0.5 + 0.5 * u_vel[1] + noise[7], -1.0, 1.0)
        t2 = np.clip(0.3 + 0.4 * m[0] + noise[8], 0.0, 1.0) # Pause ratio ~ Fatigue
        t3 = np.clip(0.5 - 0.3 * m[0] + 0.3 * u[3] + noise[9], 0.0, 1.0)
        t4 = np.clip(0.4 + 0.4 * u_vel[0] + noise[10], -1.0, 1.0)
        t5 = np.clip(0.5 + 0.4 * np.linalg.norm(u_vel) + noise[11], 0.0, 1.0)
        temporal = np.array([t0, t1, t2, t3, t4, t5], dtype=np.float64)
        
        # Interaction (4D)
        i0 = np.clip(1.2 - 0.6 * u[3] + 0.8 * m[0] + noise[12], 0.1, 3.0) # Latency
        i1 = float(u[2] > 0.4 and u[3] > 0.3 and self.rng.rand() < 0.6)     # Interruption
        i2 = np.clip(0.5 + 0.3 * m[1] + noise[13], 0.0, 1.0)             # Dyadic synchrony
        i3 = np.clip(0.2 + 0.5 * (1.0 - m[0]) + noise[14], 0.0, 1.0)      # Density
        interaction = np.array([i0, i1, i2, i3], dtype=np.float64)
        
        # Text one-hot (9D with anchor categories)
        cat_order = [
            "high_load", "high_agency", "negative_valence", "positive_valence",
            "relational_anchor_event", "relational_rupture_event", "high_urgency", "sparse", "neutral"
        ]
        text_logits = np.zeros(len(cat_order), dtype=np.float64)
        text_logits[cat_order.index(cat)] = 1.0
        
        features_25d = np.concatenate([text_logits, acoustics, temporal, interaction])
        
        return {
            "session_idx": self.session_idx,
            "turn": self.turn,
            "u_true": u.copy(),
            "m_true": m.copy(),
            "is_anchor_event": self.is_anchor_event,
            "anchor_type": self.anchor_type,
            "features_25d": features_25d,
            "utterance": utterance,
            "language": self.language,
            "regime": self.regime,
        }
