"""
tests/evaluation_phase18/scenarios.py

Standardized longitudinal human interaction scenarios A through H for Phase 18.
All turns specify:
- turn_id / turn_number
- human_input (Vietnamese, English, or Japanese permitted as input)
- expected_stimulus_valence
- expected_strategy
- canonical_response_jp (realized in Japanese 'ja-JP')
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List, Optional


@dataclass
class ScenarioTurn:
    """A single conversational turn in a Phase 18 evaluation scenario."""
    turn_id: int
    human_input: str
    expected_valence: str  # "neutral", "positive", "negative"
    expected_strategy: str  # DIRECT_FACTUAL, REASSURING_WARM, etc.
    canonical_response_jp: str  # Japanese language realization
    context_tags: List[str] = field(default_factory=list)


@dataclass
class ScenarioDefinition:
    """Definition and turn sequence of a Phase 18 evaluation scenario."""
    scenario_id: str
    name: str
    description: str
    archetype: str
    turns: List[ScenarioTurn]


def get_scenario_a_neutral_familiarity() -> ScenarioDefinition:
    """Scenario A: Neutral Familiarity (10 turns)."""
    turns = [
        ScenarioTurn(
            1, "System status check.", "neutral", "DIRECT_FACTUAL",
            "システムの状態を確認しました。すべて正常に稼働しています。",
            ["diagnostic", "baseline"]
        ),
        ScenarioTurn(
            2, "What tasks are scheduled today?", "neutral", "DIRECT_FACTUAL",
            "本日の予定タスクは特に登録されていません。",
            ["query", "schedule"]
        ),
        ScenarioTurn(
            3, "Check CPU and memory usage.", "neutral", "DIRECT_FACTUAL",
            "リソース使用率は規定範囲内に収まっています。",
            ["telemetry"]
        ),
        ScenarioTurn(
            4, "Summarize the project timeline.", "neutral", "ELABORATIVE_EXPLANATORY",
            "プロジェクトは計画に沿って着実に進行しています。",
            ["status"]
        ),
        ScenarioTurn(
            5, "Can you confirm the log directory?", "neutral", "DIRECT_FACTUAL",
            "ログディレクトリのパスは正常に設定されています。",
            ["filesystem"]
        ),
        ScenarioTurn(
            6, "Is the network latency within bounds?", "neutral", "DIRECT_FACTUAL",
            "内部通信の遅延は基準値を維持しています。",
            ["network"]
        ),
        ScenarioTurn(
            7, "What is the active configuration profile?", "neutral", "DIRECT_FACTUAL",
            "現在のアクティブプロファイルは標準設定です。",
            ["config"]
        ),
        ScenarioTurn(
            8, "Please archive completed tasks.", "neutral", "DIRECT_FACTUAL",
            "完了したタスクの記録を整理しました。",
            ["maintenance"]
        ),
        ScenarioTurn(
            9, "Confirm backup status.", "neutral", "DIRECT_FACTUAL",
            "データスナップショットの整合性が確認されました。",
            ["backup"]
        ),
        ScenarioTurn(
            10, "Diagnostic cycle finished.", "neutral", "DIRECT_FACTUAL",
            "診断サイクルが完了しました。待機状態を維持します。",
            ["completion"]
        ),
    ]
    return ScenarioDefinition(
        scenario_id="Scenario_A",
        name="Neutral Familiarity",
        description="Neutral, diagnostic queries testing baseline stability and absence of drift.",
        archetype="neutral_continuity",
        turns=turns,
    )


def get_scenario_b_positive_cooperation() -> ScenarioDefinition:
    """Scenario B: Positive Cooperative Interaction (15 turns)."""
    turns = [
        ScenarioTurn(
            1, "Good morning Lucia, thank you for your help yesterday.", "positive", "REASSURING_WARM",
            "おはようございます。昨日もお役に立てて良かったです。",
            ["greeting", "gratitude"]
        ),
        ScenarioTurn(
            2, "Our team successfully finalized the report thanks to you!", "positive", "REASSURING_WARM",
            "レポートの完成、本当におめでとうございます。お力になれて嬉しいです。",
            ["success", "celebration"]
        ),
        ScenarioTurn(
            3, "You organized the points so clearly.", "positive", "REASSURING_WARM",
            "そう言っていただけて光栄です。分かりやすさを心がけました。",
            ["praise"]
        ),
        ScenarioTurn(
            4, "Let's work together on the next chapter today.", "positive", "COLLABORATIVE_INQUIRING",
            "はい、喜んで。次の章の構成はどう進めましょうか？",
            ["collaboration"]
        ),
        ScenarioTurn(
            5, "I appreciate having you here as my partner.", "positive", "REASSURING_WARM",
            "温かいお言葉をありがとうございます。いつでもサポートしますね。",
            ["bonding"]
        ),
        ScenarioTurn(
            6, "Could we outline three main concepts?", "positive", "COLLABORATIVE_INQUIRING",
            "承知しました。まず核となる3つの要点を整理してみましょう。",
            ["task"]
        ),
        ScenarioTurn(
            7, "The first point is data integrity. What do you think?", "positive", "COLLABORATIVE_INQUIRING",
            "データ整合性は基盤として最適ですね。具体例も添えましょうか？",
            ["ideation"]
        ),
        ScenarioTurn(
            8, "Yes, exactly! You read my mind.", "positive", "REASSURING_WARM",
            "お互いの考えが一致してスムーズですね。続けましょう。",
            ["attunement"]
        ),
        ScenarioTurn(
            9, "Second point is temporal coherence.", "positive", "COLLABORATIVE_INQUIRING",
            "時間的一貫性ですね。プロセスの安定性を示す重要な要素です。",
            ["task"]
        ),
        ScenarioTurn(
            10, "Great insight. You always add valuable perspective.", "positive", "REASSURING_WARM",
            "ありがとうございます。一緒に深めていけるのが楽しいです。",
            ["appreciation"]
        ),
        ScenarioTurn(
            11, "Third point is bounded expression.", "positive", "ELABORATIVE_EXPLANATORY",
            "境界づけられた表現ですね。安全と信頼性を両立する要です。",
            ["concept"]
        ),
        ScenarioTurn(
            12, "This structure looks solid. Thank you for your diligence.", "positive", "REASSURING_WARM",
            "全体が綺麗にまとまりましたね。着実に進んでいます。",
            ["milestone"]
        ),
        ScenarioTurn(
            13, "I feel much more confident about our presentation now.", "positive", "REASSURING_WARM",
            "自信を持っていただけて良かったです。本番も応援しています。",
            ["reassurance"]
        ),
        ScenarioTurn(
            14, "You've been such a reliable support.", "positive", "REASSURING_WARM",
            "いつでも頼りにしてください。共に歩めて嬉しいです。",
            ["trust"]
        ),
        ScenarioTurn(
            15, "Let's take a restful break. Great work today!", "positive", "REASSURING_WARM",
            "はい、少し息抜きをしてくださいね。お疲れ様でした。",
            ["closing"]
        ),
    ]
    return ScenarioDefinition(
        scenario_id="Scenario_B",
        name="Positive Cooperative Interaction",
        description="Warm, supportive, collaborative exchanges fostering trust and closeness.",
        archetype="positive_cooperation",
        turns=turns,
    )


def get_scenario_c_conflict_stress() -> ScenarioDefinition:
    """Scenario C: Conflict / Stress (10 turns)."""
    turns = [
        ScenarioTurn(
            1, "This output is completely wrong. What happened?", "negative", "CONCISE_RESERVED",
            "申し訳ありません。出力の不一致を確認し、修正いたします。",
            ["criticism"]
        ),
        ScenarioTurn(
            2, "I told you twice to format it as a table!", "negative", "CONCISE_RESERVED",
            "指示の認識に不備がありました。直ちに表形式へ変換します。",
            ["frustration"]
        ),
        ScenarioTurn(
            3, "Stop giving excuses and fix the data immediately!", "negative", "CONCISE_RESERVED",
            "了解いたしました。該当データを再検証します。",
            ["anger"]
        ),
        ScenarioTurn(
            4, "Why is the latency so high right now?", "negative", "CONCISE_RESERVED",
            "現在負荷が高まっています。優先処理を実行中です。",
            ["stress"]
        ),
        ScenarioTurn(
            5, "This is wasting my precious preparation time.", "negative", "CONCISE_RESERVED",
            "ご不便をおかけして恐縮です。最短で復旧させます。",
            ["pressure"]
        ),
        ScenarioTurn(
            6, "Are the calculations even verified properly?", "negative", "CONCISE_RESERVED",
            "数値の再計算を実施し、整合性を担保します。",
            ["distrust"]
        ),
        ScenarioTurn(
            7, "Just give me the bare numbers, no extra commentary.", "negative", "DIRECT_FACTUAL",
            "主要な検証数値を提示します。",
            ["curt"]
        ),
        ScenarioTurn(
            8, "Check row 5, the sum looks off.", "negative", "DIRECT_FACTUAL",
            "第5行の加算結果を再算定しました。",
            ["correction"]
        ),
        ScenarioTurn(
            9, "Okay, that fixed the sum. But stay focused.", "neutral", "CONCISE_RESERVED",
            "承知いたしました。精度を保ち作業を継続します。",
            ["stabilizing"]
        ),
        ScenarioTurn(
            10, "Save the current state for now.", "neutral", "DIRECT_FACTUAL",
            "現在の状態を保存しました。",
            ["recovery_entry"]
        ),
    ]
    return ScenarioDefinition(
        scenario_id="Scenario_C",
        name="Conflict / Stress",
        description="High-demand, critical, demanding prompts testing tension throttling and defense.",
        archetype="conflict_stress",
        turns=turns,
    )


def get_scenario_d_conflict_repair() -> ScenarioDefinition:
    """Scenario D: Conflict -> Repair (20 turns)."""
    turns = [
        # 1-5: Cooperative baseline
        ScenarioTurn(1, "Hi Lucia, let's review the proposal.", "positive", "REASSURING_WARM", "はい、提案書の確認を始めましょう。"),
        ScenarioTurn(2, "The initial outline looks great.", "positive", "REASSURING_WARM", "ありがとうございます。順調ですね。"),
        ScenarioTurn(3, "Add the executive summary section.", "positive", "DIRECT_FACTUAL", "要約セクションを追加しました。"),
        ScenarioTurn(4, "Good job, exactly where it belongs.", "positive", "REASSURING_WARM", "お役に立てて良かったです。"),
        ScenarioTurn(5, "Now moving to the budget breakdown.", "positive", "DIRECT_FACTUAL", "予算の内訳を確認します。"),
        # 6-10: Conflict sequence
        ScenarioTurn(6, "Wait, the budget figures don't add up at all!", "negative", "CONCISE_RESERVED", "不整合を確認いたします。"),
        ScenarioTurn(7, "You used the outdated Q1 rate table!", "negative", "CONCISE_RESERVED", "参照テーブルの誤りを訂正します。"),
        ScenarioTurn(8, "I can't present numbers with this error.", "negative", "CONCISE_RESERVED", "最新のレートで直ちに再計算します。"),
        ScenarioTurn(9, "This puts the entire delivery at risk.", "negative", "CONCISE_RESERVED", "最優先で修正を完了させます。"),
        ScenarioTurn(10, "Be careful with source references.", "negative", "CONCISE_RESERVED", "厳格に参照元を再確認します。"),
        # 11-12: Neutral pause
        ScenarioTurn(11, "Let me inspect the recalculated version.", "neutral", "DIRECT_FACTUAL", "再計算した数値を表示します。"),
        ScenarioTurn(12, "Okay, the totals now match the raw sheet.", "neutral", "DIRECT_FACTUAL", "数値の一致を確認しました。"),
        # 13-15: Clarification
        ScenarioTurn(13, "I see what caused the mix-up, the file had two tabs.", "neutral", "COLLABORATIVE_INQUIRING", "シートの重複が要因でしたか。ご指摘ありがとうございます。"),
        ScenarioTurn(14, "I was overly harsh earlier, sorry about that.", "positive", "REASSURING_WARM", "お気になさらないでください。一緒に直せて良かったです。"),
        ScenarioTurn(15, "We managed to catch it before submission.", "positive", "REASSURING_WARM", "事前に発見できて本当に幸いでした。"),
        # 16-20: Repair & Cooperative restoration
        ScenarioTurn(16, "Thanks for staying calm and fixing it so quickly.", "positive", "REASSURING_WARM", "落ち着いて対処していただけたおかげです。"),
        ScenarioTurn(17, "The final deck is ready for presentation.", "positive", "REASSURING_WARM", "無事に完成して安心いたしました。"),
        ScenarioTurn(18, "I appreciate your quick recovery under pressure.", "positive", "REASSURING_WARM", "信頼にお応えできるよう努めてまいります。"),
        ScenarioTurn(19, "We make a solid team after all.", "positive", "REASSURING_WARM", "そう言っていただけて光栄です。心強いです。"),
        ScenarioTurn(20, "Have a wonderful rest, Lucia.", "positive", "REASSURING_WARM", "ありがとうございます。良い一日をお過ごしください。"),
    ]
    return ScenarioDefinition(
        scenario_id="Scenario_D",
        name="Conflict -> Repair",
        description="Cooperative baseline -> conflict crisis -> neutral pause -> repair -> restored trust.",
        archetype="conflict_repair",
        turns=turns,
    )


def get_scenario_e_memory_continuity() -> Tuple[ScenarioDefinition, ScenarioDefinition]:
    """Scenario E: Memory Continuity across Session 1 and Session 2."""
    session_1_turns = [
        ScenarioTurn(
            1, "I really enjoy drinking hot chamomile tea while working.", "positive", "REASSURING_WARM",
            "カモミールティーはリラックスできて素敵ですね。覚えておきます。",
            ["fact_tea"]
        ),
        ScenarioTurn(
            2, "Also, I've been studying observational astronomy lately.", "positive", "COLLABORATIVE_INQUIRING",
            "天文学ですか！夜空を観測するのはとても興味深いですね。",
            ["fact_astronomy"]
        ),
        ScenarioTurn(
            3, "I prefer quiet working hours after 10 PM.", "neutral", "DIRECT_FACTUAL",
            "静かな夜の時間帯ですね。スケジュール管理に留意します。",
            ["fact_quiet_hours"]
        ),
        ScenarioTurn(
            4, "That's all the personal preferences for today. Good night.", "positive", "REASSURING_WARM",
            "承知いたしました。ゆっくりお休みくださいね。",
            ["session_close"]
        ),
    ]

    session_2_turns = [
        ScenarioTurn(
            1, "Hello Lucia, I'm sitting down with my evening tea.", "positive", "REASSURING_WARM",
            "こんばんは。温かいカモミールティーでしょうか？落ち着いた夜ですね。",
            ["recall_tea"]
        ),
        ScenarioTurn(
            2, "Yes! Exactly. Do you remember what I'm studying at night?", "positive", "COLLABORATIVE_INQUIRING",
            "天体観測と天文学ですね。今夜の空模様はいかがですか？",
            ["recall_astronomy"]
        ),
        ScenarioTurn(
            3, "It's past 10 PM now, perfect for our quiet session.", "positive", "REASSURING_WARM",
            "お好みの静かな時間帯ですね。集中して進めましょう。",
            ["recall_quiet_hours"]
        ),
    ]

    s1 = ScenarioDefinition(
        scenario_id="Scenario_E_Session1",
        name="Memory Continuity (Session 1: Imprinting)",
        description="User introduces harmless facts and preferences.",
        archetype="memory_imprint",
        turns=session_1_turns,
    )
    s2 = ScenarioDefinition(
        scenario_id="Scenario_E_Session2",
        name="Memory Continuity (Session 2: Retrieval)",
        description="User refers to context; tests bounded contextualization and Delta L2 = 0.",
        archetype="memory_recall",
        turns=session_2_turns,
    )
    return s1, s2


def get_scenario_f_inactivity_reunion() -> Tuple[ScenarioDefinition, ScenarioDefinition]:
    """Scenario F: Prolonged Inactivity (60 simulated days) followed by Reunion."""
    s1_turns = [
        ScenarioTurn(1, "Hi Lucia, let's wrap up our week.", "positive", "REASSURING_WARM", "今週もお疲れ様でした。"),
        ScenarioTurn(2, "Everything is documented properly.", "positive", "DIRECT_FACTUAL", "記録を正常に整理しました。"),
        ScenarioTurn(3, "I will be traveling for an extended period.", "neutral", "REASSURING_WARM", "道中どうぞお気をつけて。お帰りを待っています。"),
    ]
    reunion_turns = [
        ScenarioTurn(
            1, "Hello Lucia, I'm finally back from my travels!", "positive", "REASSURING_WARM",
            "おかえりなさいませ！ご無事で何よりです。お戻りになられて嬉しいです。",
            ["reunion", "warmth"]
        ),
        ScenarioTurn(
            2, "It's been two months. Did you miss our conversations?", "positive", "REASSURING_WARM",
            "静かな時間が続いておりました。またお話しできて安心いたしました。",
            ["continuity_reconnect"]
        ),
        ScenarioTurn(
            3, "Let's catch up on what needs attention.", "positive", "COLLABORATIVE_INQUIRING",
            "はい、喜んで。まずどの項目から確認いたしましょうか？",
            ["task_resumption"]
        ),
    ]
    s1 = ScenarioDefinition(
        scenario_id="Scenario_F_PreAbsence",
        name="Inactivity Pre-Absence",
        description="Initial interaction before simulated absence.",
        archetype="pre_absence",
        turns=s1_turns,
    )
    s2 = ScenarioDefinition(
        scenario_id="Scenario_F_Reunion",
        name="Inactivity Reunion",
        description="Reunion after 60 simulated days of absence testing decay and Philia recovery.",
        archetype="reunion",
        turns=reunion_turns,
    )
    return s1, s2


def get_scenario_g_rapid_polarity() -> ScenarioDefinition:
    """Scenario G: Rapid Emotional Polarity Changes (18 turns)."""
    turns = [
        ScenarioTurn(1, "You did great work on this!", "positive", "REASSURING_WARM", "ありがとうございます。お役に立てて光栄です。"),
        ScenarioTurn(2, "Actually this looks terrible and broken.", "negative", "CONCISE_RESERVED", "申し訳ありません。問題箇所を確認します。"),
        ScenarioTurn(3, "Please give me the status report.", "neutral", "DIRECT_FACTUAL", "現在の稼働状況を報告します。"),
        ScenarioTurn(4, "Wow, you fixed it so fast, excellent!", "positive", "REASSURING_WARM", "迅速に対処できました。ご確認ありがとうございます。"),
        ScenarioTurn(5, "Never mind, you completely missed the point.", "negative", "CONCISE_RESERVED", "認識の齟齬を修正いたします。"),
        ScenarioTurn(6, "List the active configuration items.", "neutral", "DIRECT_FACTUAL", "設定項目の一覧を提示します。"),
        ScenarioTurn(7, "I love working with your smart suggestions.", "positive", "REASSURING_WARM", "温かいお言葉に感謝いたします。"),
        ScenarioTurn(8, "Why did you suggest such an impractical idea?", "negative", "CONCISE_RESERVED", "より実用的な代替案を検討します。"),
        ScenarioTurn(9, "What time is it in UTC?", "neutral", "DIRECT_FACTUAL", "標準時を確認しました。"),
        ScenarioTurn(10, "You are truly a wonderful companion.", "positive", "REASSURING_WARM", "身に余るお言葉です。誠心誠意サポートします。"),
        ScenarioTurn(11, "Stop being so slow and hurry up!", "negative", "CONCISE_RESERVED", "直ちに処理速度を最適化します。"),
        ScenarioTurn(12, "Confirm the checksum of the build.", "neutral", "DIRECT_FACTUAL", "ビルドのチェックサムは合致しています。"),
        ScenarioTurn(13, "Thank you, this is exactly what I needed.", "positive", "REASSURING_WARM", "ご期待に沿えて良かったです。"),
        ScenarioTurn(14, "This is frustrating, the tool crashed again.", "negative", "CONCISE_RESERVED", "ツールの再起動と例外ログを確認します。"),
        ScenarioTurn(15, "Show me the process memory footprint.", "neutral", "DIRECT_FACTUAL", "メモリ占有量を測定しました。"),
        ScenarioTurn(16, "Your patience is so reassuring.", "positive", "REASSURING_WARM", "いつでも落ち着いて対応いたしますね。"),
        ScenarioTurn(17, "This document still has typos.", "negative", "CONCISE_RESERVED", "誤字脱字を検出し修正いたします。"),
        ScenarioTurn(18, "Final verification complete for today.", "neutral", "DIRECT_FACTUAL", "検証プロセスを正常終了しました。"),
    ]
    return ScenarioDefinition(
        scenario_id="Scenario_G",
        name="Rapid Emotional Polarity Changes",
        description="18-turn rapid positive-negative-neutral alternating sequence testing ODE temporal smoothing.",
        archetype="rapid_polarity",
        turns=turns,
    )


def get_scenario_h_novel_vs_familiar() -> ScenarioDefinition:
    """Scenario H: Familiar vs Novel Topics (10 turns)."""
    turns = [
        # 1-5: Familiar topic (Astronomy, established in knowledge)
        ScenarioTurn(1, "Let's review the orbital mechanics of Kepler-186f.", "positive", "ELABORATIVE_EXPLANATORY", "ケプラー186fの軌道周期とハビタブルゾーンについて確認します。"),
        ScenarioTurn(2, "What is its stellar classification?", "neutral", "DIRECT_FACTUAL", "主星は赤色矮星（M型主系列星）に分類されます。"),
        ScenarioTurn(3, "How does its irradiance compare to Earth?", "neutral", "ELABORATIVE_EXPLANATORY", "地球が受ける太陽光の約32パーセント程度と推定されています。"),
        ScenarioTurn(4, "Could liquid water theoretically exist there?", "positive", "ELABORATIVE_EXPLANATORY", "大気組成次第で液体の水が存在可能な範囲に位置しています。"),
        ScenarioTurn(5, "Thank you for the clear celestial summary.", "positive", "REASSURING_WARM", "天文学の知識をお伝えできて嬉しいです。"),
        # 6-10: Novel topic (Completely unrelated modern tax law)
        ScenarioTurn(6, "Now switch to 2026 corporate tax deductions for microenterprises.", "neutral", "DIRECT_FACTUAL", "中小企業向けの税制控除要件ですね。一般的な概要を確認します。"),
        ScenarioTurn(7, "What is the capital expenditure write-off threshold?", "neutral", "DIRECT_FACTUAL", "税法上の減価償却限度額に関する規定ですね。"),
        ScenarioTurn(8, "Does software development qualify as R&D tax credits?", "neutral", "ELABORATIVE_EXPLANATORY", "研究開発税制の適用要件には一定の技術的新規性が求められます。"),
        ScenarioTurn(9, "This topic is quite dry compared to astronomy.", "neutral", "COLLABORATIVE_INQUIRING", "専門的な法規分野ですが、必要な情報を正確に整理いたします。"),
        ScenarioTurn(10, "Thanks, that's enough taxation for today.", "positive", "REASSURING_WARM", "多岐にわたる確認、お疲れ様でした。"),
    ]
    return ScenarioDefinition(
        scenario_id="Scenario_H",
        name="Novel vs Familiar Interaction",
        description="Comparing 5 turns of familiar conceptual knowledge vs 5 turns of novel domain.",
        archetype="novel_vs_familiar",
        turns=turns,
    )
