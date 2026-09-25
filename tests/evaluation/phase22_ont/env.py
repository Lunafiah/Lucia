"""
Environment for Phase 22-ONT.
Provides continuous dialogue simulation generating:
1. 23D Multimodal observation vector (text, acoustics, temporal micro-derivatives, interaction dynamics).
2. Layer A: Ground truth 4D Observable Interaction State u_true = [load, valence, agency, urgency].
3. Layer B: Ground truth Slow Relational/Somatic State m_true = [fatigue, warmth].
4. Legacy 6D State z_true = [load, valence, agency, urgency, fatigue, warmth].
"""
from typing import Dict, List, Tuple, Optional
import numpy as np

from .config import OBSERVABLE_4D_DIMS, SLOW_MEMORY_DIMS, LEGACY_6D_DIMS

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
        {
            "English": "Wait, slow down, this is getting way too complicated.",
            "Vietnamese": "Khoan đã, chậm lại chút, cái này phức tạp quá.",
            "Japanese": "ちょっと待って、少しペースを落としてください。難しすぎます。",
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
        {
            "English": "What specific algorithm are you using for the spatial indexing?",
            "Vietnamese": "Bạn đang dùng công thức nào để tính chỉ số không gian?",
            "Japanese": "空間インデックスの計算にはどのアルゴリズムを使用していますか？",
        },
    ],
    "negative_valence": [
        {
            "English": "That's not helpful at all, you're missing the point.",
            "Vietnamese": "Giải thích thế này chẳng giúp ích gì cả, sai hướng rồi.",
            "Japanese": "それは全く役に立ちません。论点がずれています。",
        },
        {
            "English": "I'm frustrated that we have to keep re-doing this.",
            "Vietnamese": "Mình bực mình vì cứ phải làm đi làm lại việc này.",
            "Japanese": "同じことを何度も繰り返さなければならず、うんざりしています。",
        },
        {
            "English": "No, this explanation makes no sense.",
            "Vietnamese": "Không, câu trả lời này chẳng hợp lý chút nào.",
            "Japanese": "いいえ、その説明では全く納得できません。",
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
        {
            "English": "Yes! That solved it completely.",
            "Vietnamese": "Đúng rồi! Cách này đã giải quyết triệt để vấn đề.",
            "Japanese": "その通りです！これで完全に解決しました。",
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
        {
            "English": "Hurry, deadline is in 5 minutes.",
            "Vietnamese": "Nhanh lên nhé, chỉ còn 5 phút là đến hạn rồi.",
            "Japanese": "急いでください、締め切りまであと5分しかありません。",
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
            "English": "No",
            "Vietnamese": "Không",
            "Japanese": "違う",
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
        {
            "English": "Can you elaborate on that point?",
            "Vietnamese": "Bạn có thể nói rõ hơn về điểm này không?",
            "Japanese": "その点についてもう少し詳しく説明してもらえますか？",
        },
    ],
}

class SimUserEnvONT:
    def __init__(self, seed: int = 42, regime: str = "ID", language: str = "English", dt: float = 1.0):
        self.rng = np.random.RandomState(seed)
        self.regime = regime
        self.language = language
        self.dt = dt
        
        # 4D Observable state parameters (Load, Valence, Agency, Urgency)
        self.u0 = np.array([0.0, 0.2, 0.2, 0.1], dtype=np.float64)
        self.gamma_u = np.array([0.15, 0.10, 0.20, 0.25], dtype=np.float64)
        self.q_noise_u = 0.05 * np.ones(4, dtype=np.float64)
        
        # 2D Slow memory state parameters (Fatigue, Warmth)
        self.m0 = np.array([0.5, 0.3], dtype=np.float64)
        self.gamma_m = np.array([0.05, 0.05], dtype=np.float64) # 3x slower drift
        self.q_noise_m = 0.02 * np.ones(2, dtype=np.float64)
        
        if self.regime == "NoiseSurge":
            self.q_noise_u *= 5.0
            self.q_noise_m *= 3.0
        elif self.regime == "TemporalDrift":
            self.gamma_u *= 0.5
            self.gamma_m *= 0.5
            
        self.u_true = self.u0.copy() + self.rng.normal(0, 0.1, size=4)
        self.u_true[0:3] = np.clip(self.u_true[0:3], -1.0, 1.0)
        self.u_true[3]   = np.clip(self.u_true[3],    0.0, 1.0)
        self.u_prev = self.u_true.copy()
        
        self.m_true = self.m0.copy() + self.rng.normal(0, 0.05, size=2)
        self.m_true[0] = np.clip(self.m_true[0], 0.0, 1.0)
        self.m_true[1] = np.clip(self.m_true[1], -1.0, 1.0)
        
        self.turn = 0

    def reset(self):
        self.turn = 0
        self.u_true = self.u0.copy() + self.rng.normal(0, 0.1, size=4)
        self.u_true[0:3] = np.clip(self.u_true[0:3], -1.0, 1.0)
        self.u_true[3]   = np.clip(self.u_true[3],    0.0, 1.0)
        self.u_prev = self.u_true.copy()
        
        self.m_true = self.m0.copy() + self.rng.normal(0, 0.05, size=2)
        self.m_true[0] = np.clip(self.m_true[0], 0.0, 1.0)
        self.m_true[1] = np.clip(self.m_true[1], -1.0, 1.0)
        return self._emit()

    def step(self):
        self.turn += 1
        self.u_prev = self.u_true.copy()
        
        # Contradiction Shock at t=15
        if self.regime in ["ContradictionShock", "CombinedStress"] and self.turn == 15:
            self.u_true[1] = -self.u_true[1] # Flip valence
            self.m_true[1] = -self.m_true[1] # Flip warmth
            
        # 1. Update 4D Observable state (Fast timescale)
        drift_u = -self.gamma_u * (self.u_true - self.u0) * self.dt
        diff_u = self.rng.normal(0, self.q_noise_u) * np.sqrt(self.dt)
        self.u_true += drift_u + diff_u
        self.u_true[0:3] = np.clip(self.u_true[0:3], -1.0, 1.0)
        self.u_true[3]   = np.clip(self.u_true[3],    0.0, 1.0)
        
        # 2. Update 2D Slow state (Slow accumulation + coupling to u_true)
        # Fatigue increases with sustained load/urgency; warmth accumulates with positive valence
        somatic_coupling = np.array([
            0.10 * self.u_true[0] + 0.10 * self.u_true[3],
            0.15 * self.u_true[1] + 0.05 * self.u_true[2]
        ])
        drift_m = -self.gamma_m * (self.m_true - self.m0) * self.dt + somatic_coupling
        diff_m = self.rng.normal(0, self.q_noise_m) * np.sqrt(self.dt)
        self.m_true += drift_m + diff_m
        self.m_true[0] = np.clip(self.m_true[0], 0.0, 1.0)
        self.m_true[1] = np.clip(self.m_true[1], -1.0, 1.0)
        
        return self._emit()

    def _emit(self) -> Dict:
        u = self.u_true
        m = self.m_true
        u_vel = (u - self.u_prev) / max(self.dt, 1e-4)
        
        if self.regime in ["LexicalSparsity", "CombinedStress"] and self.rng.rand() < 0.7:
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
        i2 = np.clip(0.5 + 0.3 * m[1] + noise[13], 0.0, 1.0)             # Synchrony ~ Warmth
        i3 = np.clip(0.2 + 0.5 * (1.0 - m[0]) + noise[14], 0.0, 1.0)      # Density
        interaction = np.array([i0, i1, i2, i3], dtype=np.float64)
        
        # Text one-hot (7D)
        cat_order = ["high_load", "high_agency", "negative_valence", "positive_valence", "high_urgency", "sparse", "neutral"]
        text_logits = np.zeros(len(cat_order), dtype=np.float64)
        text_logits[cat_order.index(cat)] = 1.0
        
        features_23d = np.concatenate([text_logits, acoustics, temporal, interaction])
        z_legacy = np.concatenate([u, m]) # 6D
        
        return {
            "turn": self.turn,
            "u_true": u.copy(),
            "m_true": m.copy(),
            "z_legacy_true": z_legacy.copy(),
            "features_23d": features_23d,
            "utterance": utterance,
            "language": self.language,
            "regime": self.regime,
        }
