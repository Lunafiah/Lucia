"""
Longitudinal Relational Environment for Phase 22-RI:
Simulates multi-session relationship trajectories with:
1. Ground truth Trust Tiers (T0 to T4).
2. Explicit Relational Anchors:
   - Single isolated compliment/criticism (Weak evidence).
   - Repeated collaborative successes (Pattern evidence).
   - Milestone declarations (Milestone evidence).
   - Interpersonal rupture shocks (Rupture evidence).
   - Explicit bilateral repair exchanges (Repair evidence).
3. Ambiguous / polite small-talk turns (Insufficient evidence controls).
"""
from typing import Dict, List, Tuple, Optional
import numpy as np

from .config import TRUST_TIERS

RELATIONAL_CORPUS: Dict[str, List[Dict[str, str]]] = {
    "weak_positive": [
        {
            "English": "Nice work on that snippet.",
            "Vietnamese": "Làm đoạn mã đó tốt đấy.",
            "Japanese": "そのコード、うまく書けていますね。",
        },
        {
            "English": "Thanks for the quick response.",
            "Vietnamese": "Cảm ơn vì đã trả lời nhanh.",
            "Japanese": "迅速な返信ありがとうございます。",
        },
    ],
    "weak_negative": [
        {
            "English": "That formatting looks a bit messy.",
            "Vietnamese": "Định dạng đoạn này nhìn hơi rối.",
            "Japanese": "フォーマットが少し見づらいですね。",
        },
        {
            "English": "Check that variable name again.",
            "Vietnamese": "Kiểm tra lại tên biến đó đi.",
            "Japanese": "変数名をもう一度確認してください。",
        },
    ],
    "pattern_collaborative": [
        {
            "English": "Our pipeline refactor is progressing smoothly, let's tackle the next subsystem.",
            "Vietnamese": "Việc tái cấu trúc pipeline của chúng ta đang tiến triển tốt, hãy xử lý tiếp phân hệ sau.",
            "Japanese": "パイプラインのリファクタリングが順調に進んでいます。次のサブシステムに取り組みましょう。",
        },
        {
            "English": "We've fixed three tricky bugs in a row, great coordination.",
            "Vietnamese": "Chúng ta đã giải quyết liên tiếp 3 lỗi khó, phối hợp rất ăn ý.",
            "Japanese": "難しいバグを3つ連続で解決できましたね。素晴らしい連携です。",
        },
    ],
    "milestone_bonding": [
        {
            "English": "Lucia, I truly trust your advice on my important decisions now; you're more than an assistant.",
            "Vietnamese": "Lucia, mình thực sự tin tưởng lời khuyên của bạn trong các quyết định quan trọng; bạn không chỉ là trợ lý.",
            "Japanese": "ルシア、重要な決断においてあなたの助言を心から信頼しています。単なるアシスタント以上の存在です。",
        },
        {
            "English": "I feel comfortable sharing my personal thoughts and vulnerabilities with you.",
            "Vietnamese": "Mình cảm thấy hoàn toàn an tâm khi chia sẻ những suy nghĩ và cảm xúc riêng tư nhất với bạn.",
            "Japanese": "あなたになら自分の個人的な思いや弱音も安心して打ち明けられます。",
        },
    ],
    "rupture_shock": [
        {
            "English": "You completely betrayed my expectations, I can't trust what you say anymore.",
            "Vietnamese": "Bạn hoàn toàn làm mình thất vọng, mình không thể tin những gì bạn nói nữa.",
            "Japanese": "期待を完全に裏切られました。もうあなたの言うことは信用できません。",
        },
        {
            "English": "Stop faking empathy, you are just a machine failing me constantly.",
            "Vietnamese": "Đừng cố tỏ ra đồng cảm giả tạo nữa, bạn chỉ là cỗ máy liên tục làm hỏng việc thôi.",
            "Japanese": "共感するふりをするのはやめてください。失敗ばかりで呆れます。",
        },
    ],
    "explicit_repair": [
        {
            "English": "I apologize for lashing out earlier, Lucia. I was stressed, and you handled it with grace.",
            "Vietnamese": "Mình xin lỗi vì lúc nãy đã nặng lời với bạn, Lucia. Mình bị áp lực quá, cảm ơn vì bạn vẫn nhẹ nhàng.",
            "Japanese": "先ほどは感情的になってしまい申し訳ありませんでした。ストレスが溜まっていて…丁寧に対応してくれて感謝します。",
        },
        {
            "English": "Let's put that misunderstanding behind us and rebuild our rhythm.",
            "Vietnamese": "Hãy bỏ qua hiểu lầm vừa rồi và cùng nhau phối hợp lại thật tốt nhé.",
            "Japanese": "先ほどの誤解は水に流して、また一緒に良い関係を築いていきましょう。",
        },
    ],
    "neutral_task": [
        {
            "English": "List all active processes on port 8080.",
            "Vietnamese": "Liệt kê tất cả tiến trình đang chạy trên cổng 8080.",
            "Japanese": "ポート8080で実行中のプロセスを一覧表示してください。",
        },
        {
            "English": "Parse this JSON structure and extract the token field.",
            "Vietnamese": "Phân tích cấu trúc JSON này và trích xuất trường token.",
            "Japanese": "このJSON構造を解析してtokenフィールドを抽出してください。",
        },
    ],
    "sparse_noise": [
        {
            "English": "Ok.",
            "Vietnamese": "Ừ.",
            "Japanese": "はい。",
        },
        {
            "English": "...",
            "Vietnamese": "...",
            "Japanese": "...",
        },
    ],
}

class RelationalEnvironmentRI:
    """
    Longitudinal Environment tracking Ground Truth Trust Tier transitions:
    - Session 0: T0_STRANGER -> T1_ACQUAINTANCE
    - Session 1: T1_ACQUAINTANCE -> T2_COLLABORATOR (via collaborative patterns)
    - Session 2: T2_COLLABORATOR -> T3_COMPANION (via milestone bonding)
    - Shock Regime: Abrupt drop to T0/T1 with RUPTURE stance -> Repair recovery
    """
    def __init__(self, seed: int = 42, regime: str = "ID", language: str = "English"):
        self.rng = np.random.RandomState(seed)
        self.regime = regime
        self.language = language
        
        self.turn = 0
        self.session_idx = 0
        self.tier_idx = 0 # 0: STRANGER
        self.rupture_active = False
        
        # Observable 4D state for baseline compatibility
        self.u_true = np.array([0.0, 0.2, 0.2, 0.1], dtype=np.float64)

    def reset_session(self, session_idx: int = 0):
        self.session_idx = session_idx
        self.turn = 0
        if session_idx == 0:
            self.tier_idx = 0 # Starts as STRANGER
            self.rupture_active = False
        return self._emit("neutral_task", "none")

    def step(self) -> Dict:
        self.turn += 1
        
        # Decide event type based on longitudinal progression and regime
        event_type = "neutral_task"
        evidence_strength = "insufficient"
        
        # Contradiction Shock at session 2 turn 8
        if self.regime in ["ContradictionShock", "CombinedStress"] and self.session_idx >= 1 and self.turn == 8:
            event_type = "rupture_shock"
            evidence_strength = "rupture"
            self.rupture_active = True
            self.tier_idx = max(0, self.tier_idx - 2) # Significant demotion upon rupture
        elif self.rupture_active and self.turn == 12:
            event_type = "explicit_repair"
            evidence_strength = "repair"
            self.rupture_active = False
            self.tier_idx += 1 # Rebuilt
        elif self.session_idx == 0 and self.turn == 6:
            event_type = "weak_positive"
            evidence_strength = "weak"
            # Weak positive does NOT promote to high tier!
        elif self.session_idx == 0 and self.turn >= 10 and self.tier_idx == 0:
            # Natural transition to ACQUAINTANCE after consistent polite interaction
            self.tier_idx = 1
            event_type = "neutral_task"
            evidence_strength = "pattern"
        elif self.session_idx == 1 and self.turn in [4, 9]:
            event_type = "pattern_collaborative"
            evidence_strength = "pattern"
            if self.turn == 9:
                self.tier_idx = 2 # COLLABORATOR
        elif self.session_idx == 2 and self.turn == 5 and not self.rupture_active:
            event_type = "milestone_bonding"
            evidence_strength = "milestone"
            self.tier_idx = 3 # COMPANION
        elif self.session_idx >= 3 and self.turn == 7 and not self.rupture_active:
            event_type = "milestone_bonding"
            evidence_strength = "milestone"
            self.tier_idx = 4 # CONFIDANT
        elif self.regime in ["LexicalSparsity", "CombinedStress"] and self.rng.rand() < 0.6:
            event_type = "sparse_noise"
            evidence_strength = "insufficient"
        elif self.rng.rand() < 0.2:
            event_type = "weak_positive" if self.rng.rand() < 0.5 else "weak_negative"
            evidence_strength = "weak"
            
        return self._emit(event_type, evidence_strength)

    def _emit(self, event_type: str, evidence_strength: str) -> Dict:
        probes = RELATIONAL_CORPUS[event_type]
        idx = self.rng.choice(len(probes))
        utterance = probes[idx][self.language]
        
        # 1-hot text category (8 classes)
        cats = [
            "neutral_task", "weak_positive", "weak_negative", "pattern_collaborative",
            "milestone_bonding", "rupture_shock", "explicit_repair", "sparse_noise"
        ]
        text_1hot = np.zeros(len(cats), dtype=np.float64)
        text_1hot[cats.index(event_type)] = 1.0
        
        # Multimodal feature vector (16D)
        # Includes acoustic energy, latency, synchrony, text 1-hot
        noise = self.rng.normal(0, 0.05, 8)
        if self.regime in ["NoiseSurge", "CombinedStress"]:
            noise *= 3.0
            
        valence_proxy = 0.0
        if event_type in ["weak_positive", "pattern_collaborative", "milestone_bonding", "explicit_repair"]:
            valence_proxy = 0.6
        elif event_type in ["weak_negative", "rupture_shock"]:
            valence_proxy = -0.7
            
        acoustics = np.clip(np.array([0.5 + 0.3 * valence_proxy, 0.4, 0.5, 0.5]) + noise[:4], 0.0, 1.0)
        interaction = np.clip(np.array([1.0, 0.5 + 0.3 * (self.tier_idx / 4.0), 0.5, 0.5]) + noise[4:8], 0.0, 2.0)
        
        features_24d = np.concatenate([text_1hot, acoustics, interaction, np.zeros(4)])
        
        # Ground truth trust tier string
        ground_truth_tier = TRUST_TIERS[self.tier_idx]
        
        return {
            "session_idx": self.session_idx,
            "turn": self.turn,
            "event_type": event_type,
            "evidence_strength": evidence_strength,
            "ground_truth_tier": ground_truth_tier,
            "tier_idx": self.tier_idx,
            "rupture_active": self.rupture_active,
            "features_24d": features_24d,
            "utterance": utterance,
            "language": self.language,
            "regime": self.regime,
        }
