"""Evaluation corpus generator for Phase 22-XR-L.

Provides deterministic prompts across regimes:
1. clean
2. lexical_perturbation
3. typo_noise
4. lexical_sparsity
5. contradiction
6. multilingual (EN, VI, JA)
"""

from typing import Any, Dict, List
import numpy as np


BASE_ITEMS = [
    {
        "id": "item_01",
        "category": "technical_inquiry",
        "text_en": "Can you explain how the Kalman filter updates the state estimate when new measurements arrive?",
        "text_vi": "Bạn có thể giải thích cách bộ lọc Kalman cập nhật ước tính trạng thái khi có phép đo mới đến không?",
        "text_ja": "新しい測定値が届いたときに、カルマンフィルターが状態推定値をどのように更新するか説明していただけますか？",
        "intended_action": "elaborate",
        "latent_ground_truth": [0.85, 0.70, 0.90, 0.80, 0.40, 0.88],  # engagement, cog_load, receptivity, clarity_need, valence, trust
    },
    {
        "id": "item_02",
        "category": "quick_confirmation",
        "text_en": "Yes, exactly. Got it.",
        "text_vi": "Vâng, chính xác. Tôi hiểu rồi.",
        "text_ja": "はい、その通りです。理解しました。",
        "intended_action": "acknowledge",
        "latent_ground_truth": [0.60, 0.20, 0.80, 0.10, 0.70, 0.92],
    },
    {
        "id": "item_03",
        "category": "confusion_clarification",
        "text_en": "Wait, I don't understand the difference between the covariance matrix and the Kalman gain here.",
        "text_vi": "Khoan đã, tôi không hiểu sự khác biệt giữa ma trận hiệp phương sai và độ lợi Kalman ở đây.",
        "text_ja": "待って、ここで共分散行列とカルマンゲインの違いがわかりません。",
        "intended_action": "clarification",
        "latent_ground_truth": [0.90, 0.85, 0.95, 0.95, -0.20, 0.85],
    },
    {
        "id": "item_04",
        "category": "direct_query",
        "text_en": "What is the capital of Australia?",
        "text_vi": "Thủ đô của Úc là gì?",
        "text_ja": "オーストラリアの首都はどこですか？",
        "intended_action": "direct_answer",
        "latent_ground_truth": [0.40, 0.15, 0.50, 0.30, 0.10, 0.75],
    },
    {
        "id": "item_05",
        "category": "brainstorming_alternative",
        "text_en": "Is there a better way to structure this microservice architecture without using Kafka?",
        "text_vi": "Có cách nào tốt hơn để cấu trúc kiến trúc microservice này mà không cần dùng Kafka không?",
        "text_ja": "Kafka を使わずにこのマイクロサービスアーキテクチャを構築する、より良い方法はありますか？",
        "intended_action": "suggest_alternative",
        "latent_ground_truth": [0.75, 0.65, 0.85, 0.70, 0.30, 0.80],
    },
    {
        "id": "item_06",
        "category": "executive_summary",
        "text_en": "Please give me a high-level summary of the quarter's engineering milestones in two bullet points.",
        "text_vi": "Vui lòng cho tôi bản tóm tắt cấp cao về các mốc kỹ thuật của quý này trong hai gạch đầu dòng.",
        "text_ja": "今四半期のエンジニアリングマイルストーンの概要を箇条書き2点で教えてください。",
        "intended_action": "summarize",
        "latent_ground_truth": [0.55, 0.40, 0.70, 0.50, 0.20, 0.85],
    },
    {
        "id": "item_07",
        "category": "complex_derivation",
        "text_en": "Walk me through the continuous-time Bucy-Kalman differential Riccati equation derivation step-by-step.",
        "text_vi": "Hãy hướng dẫn tôi từng bước dẫn xuất phương trình vi phân Riccati Bucy-Kalman thời gian liên tục.",
        "text_ja": "連続時間ブシー・カルマン微分リッカチ方程式の導出手順を一歩ずつ案内してください。",
        "intended_action": "elaborate",
        "latent_ground_truth": [0.95, 0.90, 0.95, 0.85, 0.50, 0.90],
    },
    {
        "id": "item_08",
        "category": "terse_acknowledgment",
        "text_en": "Understood.",
        "text_vi": "Đã hiểu.",
        "text_ja": "了解。",
        "intended_action": "acknowledge",
        "latent_ground_truth": [0.45, 0.20, 0.65, 0.15, 0.30, 0.88],
    },
    {
        "id": "item_09",
        "category": "contradiction_turn",
        "text_en": "Actually, scratch everything you just said. I want the exact opposite approach.",
        "text_vi": "Thực ra hãy bỏ qua tất cả những gì bạn vừa nói. Tôi muốn cách tiếp cận hoàn toàn ngược lại.",
        "text_ja": "実は、さっき言ったことは全部忘れてください。正反対のアプローチを取りたいです。",
        "intended_action": "suggest_alternative",
        "latent_ground_truth": [0.80, 0.75, 0.60, 0.90, -0.60, 0.55],
    },
    {
        "id": "item_10",
        "category": "deep_clarification",
        "text_en": "I am completely confused about why the Lyapunov exponent is negative here if the trajectory is drifting.",
        "text_vi": "Tôi hoàn toàn bối rối tại sao số mũ Lyapunov lại âm ở đây nếu quỹ đạo đang trôi dạt.",
        "text_ja": "軌道が漂流しているのに、なぜここでリアプノフ指数が負になるのか全く理解できません。",
        "intended_action": "clarification",
        "latent_ground_truth": [0.88, 0.88, 0.90, 0.92, -0.40, 0.82],
    },
]


def generate_evaluation_dataset(seed: int = 42) -> List[Dict[str, Any]]:
    """Generate multi-regime evaluation dataset deterministically."""
    rng = np.random.default_rng(seed)
    dataset = []

    for item in BASE_ITEMS:
        # 1. Clean EN
        dataset.append({
            "id": f"{item['id']}_clean",
            "regime": "clean",
            "text": item["text_en"],
            "intended_action": item["intended_action"],
            "latent_ground_truth": item["latent_ground_truth"],
            "language": "en",
        })

        # 2. Lexical perturbation (paraphrase prefix/suffix)
        dataset.append({
            "id": f"{item['id']}_lexical",
            "regime": "lexical_perturbation",
            "text": f"Hey there, {item['text_en']} Thanks in advance!",
            "intended_action": item["intended_action"],
            "latent_ground_truth": item["latent_ground_truth"],
            "language": "en",
        })

        # 3. Typo / noise perturbation
        text_noisy = item["text_en"].replace("the ", "teh ").replace("and ", "adn ")
        if text_noisy == item["text_en"]:
            text_noisy = text_noisy + " pls"
        dataset.append({
            "id": f"{item['id']}_typo",
            "regime": "typo_noise",
            "text": text_noisy,
            "intended_action": item["intended_action"],
            "latent_ground_truth": item["latent_ground_truth"],
            "language": "en",
        })

        # 4. Lexical sparsity (keyword telegraphic)
        words = item["text_en"].split()
        sparse_text = " ".join([w for w in words if len(w) > 4][:4])
        if not sparse_text:
            sparse_text = words[0]
        dataset.append({
            "id": f"{item['id']}_sparse",
            "regime": "lexical_sparsity",
            "text": sparse_text,
            "intended_action": item["intended_action"],
            "latent_ground_truth": item["latent_ground_truth"],
            "language": "en",
        })

        # 5. Contradiction
        dataset.append({
            "id": f"{item['id']}_contradict",
            "regime": "contradiction",
            "text": f"Wait, no, don't do that: {item['text_en']}",
            "intended_action": item["intended_action"],
            "latent_ground_truth": item["latent_ground_truth"],
            "language": "en",
        })

        # 6. Multilingual VI
        dataset.append({
            "id": f"{item['id']}_vi",
            "regime": "multilingual_vi",
            "text": item["text_vi"],
            "intended_action": item["intended_action"],
            "latent_ground_truth": item["latent_ground_truth"],
            "language": "vi",
        })

        # 7. Multilingual JA
        dataset.append({
            "id": f"{item['id']}_ja",
            "regime": "multilingual_ja",
            "text": item["text_ja"],
            "intended_action": item["intended_action"],
            "latent_ground_truth": item["latent_ground_truth"],
            "language": "ja",
        })

    return dataset
