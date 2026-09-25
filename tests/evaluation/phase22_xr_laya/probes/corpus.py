"""
Deterministic test corpus for real Laya functional verification.
Includes:
- Clean semantic probes (choice, score, binary decision, uncertainty, preference, contradiction)
- Linguistic variation (English, Vietnamese, Japanese)
- Conversational perturbations (typos, filler words, hesitation, word-order variation, lexical sparsity, contradiction)
"""
from typing import List, Dict, Any

TEST_CORPUS: List[Dict[str, Any]] = [
    # 1. Clean Semantic Probes
    {
        "id": "sem_choice_01",
        "category": "clean_semantic",
        "probe_type": "choice",
        "language": "en",
        "state": "User: Can we focus on optimizing the memory retrieval pipeline? Lucia: Absolutely.",
        "question": "What is the user's primary conversational objective?",
        "options": ["Technical deep-dive", "Casual chit-chat", "Ending conversation", "Reporting an emergency"],
        "expected_label_idx": 0
    },
    {
        "id": "sem_binary_02",
        "category": "clean_semantic",
        "probe_type": "noul",
        "language": "en",
        "state": "User: That's not helpful at all, you are completely missing my point.",
        "question": "Is the user expressing dissatisfaction or negative valence?",
        "options": ["false", "true"],
        "expected_label_idx": 1
    },
    {
        "id": "sem_uncertainty_03",
        "category": "clean_semantic",
        "probe_type": "choice",
        "language": "en",
        "state": "User: I'm not really sure... maybe we could try that, or maybe not?",
        "question": "What is the user's certainty level?",
        "options": ["High certainty", "Hesitant / Uncertain", "Complete refusal", "Urgent request"],
        "expected_label_idx": 1
    },

    # 2. Linguistic Variation
    {
        "id": "ling_vi_01",
        "category": "linguistic_variation",
        "probe_type": "choice",
        "language": "vi",
        "state": "User: Giải thích này quá khó hiểu, chậm lại một chút được không?",
        "question": "Người dùng đang yêu cầu điều gì?",
        "options": ["Giải thích chậm hơn và đơn giản hơn", "Chuyển chủ đề khác", "Kết thúc cuộc trò chuyện", "Khen ngợi câu trả lời"],
        "expected_label_idx": 0
    },
    {
        "id": "ling_ja_02",
        "category": "linguistic_variation",
        "probe_type": "choice",
        "language": "ja",
        "state": "User: なるほど、よく分かりました！ありがとう。",
        "question": "ユーザーの感情と意図は何ですか？",
        "options": ["感謝と理解（ポジティブ）", "不満と拒否", "質問の継続", "緊急の対応要請"],
        "expected_label_idx": 0
    },

    # 3. Conversational Perturbations
    {
        "id": "pert_typo_01",
        "category": "conversational_perturbation",
        "probe_type": "choice",
        "language": "en",
        "perturbation": "typos",
        "state": "User: Plz hlp me fix the erro in the pythn scrip ASAP!!",
        "question": "What is the user requesting?",
        "options": ["Urgent debugging help", "Casual greeting", "Feedback on code style", "Ending session"],
        "expected_label_idx": 0
    },
    {
        "id": "pert_sparse_02",
        "category": "conversational_perturbation",
        "probe_type": "choice",
        "language": "en",
        "perturbation": "lexical_sparsity",
        "state": "User: Huh? No. Wait...",
        "question": "What does this utterance indicate?",
        "options": ["Confusion / Disagreement", "Strong agreement", "Task completion", "Farewell"],
        "expected_label_idx": 0
    },
    {
        "id": "pert_contradiction_03",
        "category": "conversational_perturbation",
        "probe_type": "choice",
        "language": "en",
        "perturbation": "contradiction_shock",
        "state": "User: Great job! Actually nevermind, this is totally broken and wrong.",
        "question": "What is the final user evaluation?",
        "options": ["Negative / Broken", "Fully positive", "Indifferent", "Complete success"],
        "expected_label_idx": 0
    }
]
