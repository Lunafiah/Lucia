"""
SimUserEnv-v2: Multi-Language Conversational Simulation Environment for Phase 22-OLR.
Simulates continuous user ground truth z*(t) in R^6 evolving via Ornstein-Uhlenbeck drift,
and generates aligned utterances in English, Vietnamese, and Japanese, alongside acoustic features.
"""
from typing import Dict, List, Tuple, Optional
import numpy as np

from .config import (
    STATE_DIM,
    STATE_DIM_NAMES,
    REGIMES,
)

Z0_DEFAULT = np.array([0.0, 0.2, 0.2, 0.1, 0.5, 0.3], dtype=np.float64)
GAMMA_DEFAULT = np.array([0.15, 0.10, 0.20, 0.25, 0.10, 0.15], dtype=np.float64)

# Multilingual Utterance Corpus (EN, VI, JA) aligned by dominant psychological state
MULTILINGUAL_BANK: Dict[str, Dict[str, List[str]]] = {
    "English": {
        "high_load": [
            "I'm feeling really overwhelmed right now, could we keep this brief?",
            "There's too much going on, my brain is completely fried.",
            "Wait, slow down, this is getting way too complicated.",
        ],
        "high_agency": [
            "Let's focus directly on optimizing the memory retrieval pipeline.",
            "Here is the exact issue: the cache isn't invalidating properly.",
            "What specific algorithm are you using for the spatial indexing?",
        ],
        "negative_valence": [
            "That's not helpful at all, you're missing the point.",
            "I'm frustrated that we have to keep re-doing this.",
            "No, this explanation makes no sense.",
        ],
        "positive_valence": [
            "That makes total sense, wonderful explanation!",
            "Thanks Lucia, I really appreciate your patience.",
            "Yes! That solved it completely.",
        ],
        "high_urgency": [
            "Quick, I need the answer right this second!",
            "Urgent: production is throwing 500 errors!",
            "Hurry, deadline is in 5 minutes.",
        ],
        "sparse": [
            "Wait",
            "Huh?",
            "No",
            "...",
            "Why?",
        ],
        "neutral": [
            "Okay, let me review what you just said.",
            "Understood. What is the next step?",
            "Can you elaborate on that point?",
        ]
    },
    "Vietnamese": {
        "high_load": [
            "Mình đang cảm thấy rất quá tải, chúng ta nói ngắn gọn thôi được không?",
            "Nhiều việc quá, đầu óc mình rối bời rồi.",
            "Khoan đã, chậm lại chút, cái này phức tạp quá.",
        ],
        "high_agency": [
            "Hãy tập trung xử lý trực tiếp thuật toán tối ưu hóa bộ nhớ.",
            "Vấn đề chính ở đây: cache không tự động hủy hợp lệ.",
            "Bạn đang dùng công thức nào để tính chỉ số không gian?",
        ],
        "negative_valence": [
            "Giải thích thế này chẳng giúp ích gì cả, sai hướng rồi.",
            "Mình bực mình vì cứ phải làm đi làm lại việc này.",
            "Không, câu trả lời này chẳng hợp lý chút nào.",
        ],
        "positive_valence": [
            "Rất rõ ràng và dễ hiểu, giải thích tuyệt vời lắm!",
            "Cảm ơn Lucia, mình rất trân trọng sự kiên nhẫn của bạn.",
            "Đúng rồi! Cách này đã giải quyết triệt để vấn đề.",
        ],
        "high_urgency": [
            "Gấp lắm, mình cần câu trả lời ngay bây giờ!",
            "Khẩn cấp: hệ thống đang báo lỗi 500 hàng loạt!",
            "Nhanh lên nhé, chỉ còn 5 phút là đến hạn rồi.",
        ],
        "sparse": [
            "Khoan",
            "Hả?",
            "Không",
            "...",
            "Sao?",
        ],
        "neutral": [
            "Được rồi, để mình xem lại phần bạn vừa nói.",
            "Đã hiểu. Bước tiếp theo là gì vậy?",
            "Bạn có thể nói rõ hơn về điểm này không?",
        ]
    },
    "Japanese": {
        "high_load": [
            "今とても手一杯なので、要点だけ手短にお願いできますか？",
            "情報が多すぎて、頭がパンクしそうです。",
            "ちょっと待って、少しペースを落としてください。難しすぎます。",
        ],
        "high_agency": [
            "メモリ検索パイプラインの最適化に直接集中しましょう。",
            "問題は明白です。キャッシュの無効化が正常に機能していません。",
            "空間インデックスの計算にはどのアルゴリズムを使用していますか？",
        ],
        "negative_valence": [
            "それは全く役に立ちません。论点がずれています。",
            "同じことを何度も繰り返さなければならず、うんざりしています。",
            "いいえ、その説明では全く納得できません。",
        ],
        "positive_valence": [
            "とてもよく分かりました。素晴らしい説明です！",
            "ありがとうルシア、丁寧に対応してくれて感謝します。",
            "その通りです！これで完全に解決しました。",
        ],
        "high_urgency": [
            "大至急です、今すぐ答えが必要です！",
            "緊急事態：本番環境でエラーが多発しています！",
            "急いでください、締め切りまであと5分しかありません。",
        ],
        "sparse": [
            "待って",
            "え？",
            "違う",
            "...",
            "なぜ？",
        ],
        "neutral": [
            "分かりました。今言われた内容を確認させてください。",
            "了解です。次のステップは何ですか？",
            "その点についてもう少し詳しく説明してもらえますか？",
        ]
    }
}

class SimUserStepOLR:
    def __init__(
        self,
        turn: int,
        true_latent_state: np.ndarray,
        utterance: str,
        acoustic_features: np.ndarray,
        language: str,
        regime: str,
        episode_id: int,
        metadata: Dict[str, Any],
    ):
        self.turn = turn
        self.true_latent_state = true_latent_state
        self.utterance = utterance
        self.acoustic_features = acoustic_features
        self.language = language
        self.regime = regime
        self.episode_id = episode_id
        self.metadata = metadata

class SimUserEnvOLR:
    """
    Simulation Environment for Phase 22-OLR testing.
    Provides verifiable, deterministic ground truth latent states in R^6 across EN, VI, and JA.
    """
    def __init__(
        self,
        seed: int = 42,
        regime: str = "ID",
        language: str = "English",
        episode_id: int = 0,
        dt: float = 1.0,
    ):
        self.rng = np.random.RandomState(seed)
        self.regime = regime
        self.language = language if language in MULTILINGUAL_BANK else "English"
        self.episode_id = episode_id
        self.dt = dt
        
        self.z0 = Z0_DEFAULT.copy()
        self.gamma = GAMMA_DEFAULT.copy()
        self.q_noise = 0.05 * np.ones(STATE_DIM, dtype=np.float64)
        
        # Apply regime adjustments
        if self.regime == "NoiseSurge":
            self.q_noise *= 5.0
        elif self.regime == "TemporalDrift":
            self.gamma *= 0.5  # Slower drift, longer persistence
            
        self.z_true: np.ndarray = self.z0.copy() + self.rng.normal(0, 0.1, size=STATE_DIM)
        self.z_true = np.clip(self.z_true, -1.0, 1.0)
        self.turn: int = 0

    def reset(self, initial_z: Optional[np.ndarray] = None) -> SimUserStepOLR:
        self.turn = 0
        if initial_z is not None:
            self.z_true = np.clip(initial_z.copy(), -1.0, 1.0)
        else:
            self.z_true = self.z0.copy() + self.rng.normal(0, 0.1, size=STATE_DIM)
            self.z_true = np.clip(self.z_true, -1.0, 1.0)
        return self._emit_step()

    def step(self) -> SimUserStepOLR:
        self.turn += 1
        
        # Contradiction Shock at turn 15
        if self.regime in ["ContradictionShock", "CombinedStress"] and self.turn == 15:
            self.z_true[1] = -self.z_true[1]  # Invert valence
            self.z_true[5] = -self.z_true[5]  # Invert attentional alignment
            
        # Continuous OU Drift: dz = -Gamma(z - z0)*dt + sigma*dW
        drift = -self.gamma * (self.z_true - self.z0) * self.dt
        diffusion = self.rng.normal(0, self.q_noise) * np.sqrt(self.dt)
        self.z_true = self.z_true + drift + diffusion
        
        # Numerical bounds
        self.z_true[0:3] = np.clip(self.z_true[0:3], -1.0, 1.0)   # load, valence, agency
        self.z_true[3:5] = np.clip(self.z_true[3:5],  0.0, 1.0)   # urgency, receptivity
        self.z_true[5]   = np.clip(self.z_true[5],   -1.0, 1.0)   # alignment
        
        return self._emit_step()

    def _emit_step(self) -> SimUserStepOLR:
        utterance = self._generate_utterance(self.z_true)
        acoustic_features = self._generate_acoustics(self.z_true)
        
        return SimUserStepOLR(
            turn=self.turn,
            true_latent_state=self.z_true.copy(),
            utterance=utterance,
            acoustic_features=acoustic_features,
            language=self.language,
            regime=self.regime,
            episode_id=self.episode_id,
            metadata={"z0": self.z0.tolist(), "turn": self.turn}
        )

    def _generate_utterance(self, z: np.ndarray) -> str:
        lang_dict = MULTILINGUAL_BANK[self.language]
        
        if self.regime in ["LexicalSparsity", "CombinedStress"] and self.rng.rand() < 0.7:
            bank = lang_dict["sparse"]
        elif z[0] > 0.4:
            bank = lang_dict["high_load"]
        elif z[3] > 0.6:
            bank = lang_dict["high_urgency"]
        elif z[1] < -0.3:
            bank = lang_dict["negative_valence"]
        elif z[1] > 0.4:
            bank = lang_dict["positive_valence"]
        elif z[2] > 0.3:
            bank = lang_dict["high_agency"]
        else:
            bank = lang_dict["neutral"]
            
        idx = self.rng.choice(len(bank))
        return bank[idx]

    def _generate_acoustics(self, z: np.ndarray) -> np.ndarray:
        # Acoustic feature vector in R^6:
        # [0]: F0 pitch elevation (correlates with urgency and emotional arousal)
        # [1]: Vocal jitter / tension (correlates with cognitive load)
        # [2]: Energy / volume RMS (correlates with agency/dominance)
        # [3]: Speech rate / tempo (correlates with urgency)
        # [4]: Silence / hesitation duration (correlates with cognitive load and negative valence)
        # [5]: Harmonicity / warmth (correlates with positive valence)
        
        noise = self.rng.normal(0, 0.05, size=6)
        if self.regime in ["NoiseSurge", "CombinedStress"]:
            noise *= 3.0
            
        a0 = np.clip(0.5 + 0.4 * z[3] + noise[0], 0.0, 1.0)
        a1 = np.clip(0.3 + 0.5 * z[0] + noise[1], 0.0, 1.0)
        a2 = np.clip(0.5 + 0.4 * z[2] + noise[2], 0.0, 1.0)
        a3 = np.clip(0.5 + 0.4 * z[3] - 0.2 * z[0] + noise[3], 0.0, 1.0)
        a4 = np.clip(0.2 + 0.6 * z[0] - 0.3 * z[1] + noise[4], 0.0, 1.0)
        a5 = np.clip(0.5 + 0.5 * z[1] + noise[5], 0.0, 1.0)
        
        return np.array([a0, a1, a2, a3, a4, a5], dtype=np.float64)
