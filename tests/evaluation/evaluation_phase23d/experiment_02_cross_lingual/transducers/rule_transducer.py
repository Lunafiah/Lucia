"""
Phase 23-D — EXP-02: Rule-Based Deterministic Transducer
Implements a non-LLM, pattern-driven transducer for EN, JA, and VI.
Tests feasibility of edge rule-based semantic parsing.
Limitations and unresolvable phenomena are marked UNSUPPORTED / UNRESOLVED.
"""
from typing import Dict, Any, Optional
from .oracle_transducer import SemanticInstance


def transduce_en_rule(text: str, scenario_id: str, candidate_name: str) -> SemanticInstance:
    """Rule-based semantic parser for English surface sentences."""
    inst = SemanticInstance(candidate_name, "EN", scenario_id)
    text_lower = text.lower()

    # Negation
    negated = "did not" in text_lower or " not " in text_lower

    # Predicate mapping
    pred = "UNKNOWN_PRED"
    if "solved" in text_lower:
        pred = "SOLVE_01"
    elif "assisted" in text_lower:
        pred = "ASSIST_01"
    elif "read" in text_lower:
        pred = "READ_01"
    elif "analyzing" in text_lower:
        pred = "ANALYZE_01"
    elif "verified" in text_lower:
        pred = "VERIFY_01"
    elif "delete" in text_lower:
        pred = "DELETE_01"
    elif "believes" in text_lower:
        pred = "BELIEVE_01"
    elif "reported" in text_lower:
        pred = "REPORT_01"
    elif "reviewed" in text_lower:
        pred = "REVIEW_01"

    # Agent / ARG0
    arg0 = "UNKNOWN_ENTITY"
    if text_lower.startswith("lucia"):
        arg0 = "ent_lucia"
    elif "the user" in text_lower:
        arg0 = "ent_user"
    elif "someone" in text_lower:
        arg0 = "UNKNOWN_ENTITY"

    # Patient / ARG1
    arg1 = "UNKNOWN_ENTITY"
    if "the problem" in text_lower:
        arg1 = "ent_problem"
    elif "lucia" in text_lower and not text_lower.startswith("lucia"):
        arg1 = "ent_lucia"
    elif "book" in text_lower:
        arg1 = "ent_book"
    elif "code" in text_lower:
        arg1 = "ent_code"
    elif "the system" in text_lower:
        arg1 = "ent_system"
    elif "repository" in text_lower:
        arg1 = "ent_repo"
    elif "reviewed it" in text_lower:
        arg1 = "ent_doc"

    # Temporal & Aspect
    temporal = "PAST"
    if "is currently" in text_lower:
        temporal = "PRESENT_PROGRESSIVE"
    elif "believes" in text_lower:
        temporal = "PRESENT"
    elif "before" in text_lower:
        temporal = "PRECEDES"

    # Conceiver
    conceiver = "CANONICAL_SPEAKER"
    if "believes" in text_lower:
        conceiver = arg0
    elif "reported" in text_lower:
        conceiver = arg0

    # Social & Sortal
    social = "NEUTRAL"
    if "senior male" in text_lower:
        social = "SENIOR_MALE_PEER"
    sortal = "NONE"
    if "physical book" in text_lower:
        sortal = "SORTAL_BOUND_VOLUME"

    # Populate SemanticInstance
    eid = f"e_{scenario_id}"
    inst.nodes[eid] = {
        "id": eid,
        "type": "EVENT",
        "predicate": pred,
        "negated": negated,
        "conceiver": conceiver,
        "temporal": temporal,
        "aspect": "PROGRESSIVE" if "currently" in text_lower else "NONE",
    }
    for ent in [arg0, arg1]:
        if ent != "UNKNOWN_ENTITY":
            inst.nodes[ent] = {
                "id": ent,
                "type": "ENTITY",
                "label": ent,
                "sortal": sortal if ent == "ent_book" else "NONE",
                "social_deixis": social if ent == "ent_user" else "NEUTRAL",
            }
    if arg0 != "UNKNOWN_ENTITY":
        inst.edges.append({"source": eid, "target": arg0, "role": ":ARG0"})
    if arg1 != "UNKNOWN_ENTITY":
        inst.edges.append({"source": eid, "target": arg1, "role": ":ARG1"})

    return inst


def transduce_ja_rule(text: str, scenario_id: str, candidate_name: str) -> SemanticInstance:
    """Rule-based semantic parser for Japanese postpositional surface structures."""
    inst = SemanticInstance(candidate_name, "JA", scenario_id)

    # Postpositional role parsing
    # が (ga) -> ARG0
    # を (o) -> ARG1
    # は (wa) -> topic/subject
    arg0 = "UNKNOWN_ENTITY"
    arg1 = "UNKNOWN_ENTITY"

    if "ルシアが" in text or "ルシアは" in text:
        arg0 = "ent_lucia"
    elif "ユーザーが" in text or "ユーザーは" in text or "先輩のユーザーが" in text:
        arg0 = "ent_user"
    # Note: If no overt subject (zero anaphora), arg0 remains UNKNOWN_ENTITY without defaulting to speaker!

    if "問題を" in text:
        arg1 = "ent_problem"
    elif "ルシアを" in text:
        arg1 = "ent_lucia"
    elif "本を" in text:
        arg1 = "ent_book"
    elif "コードを" in text:
        arg1 = "ent_code"
    elif "システムを" in text:
        arg1 = "ent_system"
    elif "リポジトリを" in text:
        arg1 = "ent_repo"
    elif "それを" in text:
        arg1 = "ent_doc"

    # Predicate
    pred = "UNKNOWN_PRED"
    if "解決した" in text:
        pred = "SOLVE_01"
    elif "支援した" in text:
        pred = "ASSIST_01"
    elif "読んだ" in text:
        pred = "READ_01"
    elif "分析している" in text:
        pred = "ANALYZE_01"
    elif "検証した" in text:
        pred = "VERIFY_01"
    elif "削除しなかった" in text:
        pred = "DELETE_01"
    elif "信じている" in text:
        pred = "BELIEVE_01"
    elif "報告した" in text:
        pred = "REPORT_01"
    elif "査読した" in text:
        pred = "REVIEW_01"

    # Negation
    negated = "しなかった" in text or "ない" in text

    # Aspect & Temporal
    aspect = "PROGRESSIVE" if "ている" in text else "NONE"
    temporal = "PAST"
    if "分析している" in text:
        temporal = "PRESENT_PROGRESSIVE"
    elif "信じている" in text:
        temporal = "PRESENT"
    elif "前に" in text:
        temporal = "PRECEDES"

    # Social Deixis
    social = "SENIOR_MALE_PEER" if "先輩" in text else "NEUTRAL"
    # Classifier / Counter
    sortal = "SORTAL_BOUND_VOLUME" if "一冊" in text else "NONE"

    # Conceiver
    conceiver = "CANONICAL_SPEAKER"
    if "信じている" in text or "報告した" in text:
        conceiver = arg0

    eid = f"e_{scenario_id}"
    inst.nodes[eid] = {
        "id": eid,
        "type": "EVENT",
        "predicate": pred,
        "negated": negated,
        "conceiver": conceiver,
        "temporal": temporal,
        "aspect": aspect,
    }
    for ent in [arg0, arg1]:
        if ent != "UNKNOWN_ENTITY":
            inst.nodes[ent] = {
                "id": ent,
                "type": "ENTITY",
                "label": ent,
                "sortal": sortal if ent == "ent_book" else "NONE",
                "social_deixis": social if ent == "ent_user" else "NEUTRAL",
            }
    if arg0 != "UNKNOWN_ENTITY":
        inst.edges.append({"source": eid, "target": arg0, "role": ":ARG0"})
    if arg1 != "UNKNOWN_ENTITY":
        inst.edges.append({"source": eid, "target": arg1, "role": ":ARG1"})

    return inst


def transduce_vi_rule(text: str, scenario_id: str, candidate_name: str) -> SemanticInstance:
    """Rule-based semantic parser for Vietnamese surface sentences."""
    inst = SemanticInstance(candidate_name, "VI", scenario_id)
    text_lower = text.lower()

    # Agent identification
    arg0 = "UNKNOWN_ENTITY"
    social = "NEUTRAL"
    if text_lower.startswith("lucia"):
        arg0 = "ent_lucia"
    elif text_lower.startswith("người dùng"):
        arg0 = "ent_user"
    elif text_lower.startswith("anh "):
        arg0 = "ent_user"
        social = "SENIOR_MALE_PEER"
    # Zero anaphora: If text starts with "đã giải quyết" without overt subject, arg0 remains UNKNOWN_ENTITY

    # Patient
    arg1 = "UNKNOWN_ENTITY"
    if "vấn đề" in text_lower:
        arg1 = "ent_problem"
    elif "hỗ trợ lucia" in text_lower:
        arg1 = "ent_lucia"
    elif "sách" in text_lower:
        arg1 = "ent_book"
    elif "mã nguồn" in text_lower:
        arg1 = "ent_code"
    elif "hệ thống" in text_lower:
        arg1 = "ent_system"
    elif "kho lưu trữ" in text_lower:
        arg1 = "ent_repo"
    elif "xem lại nó" in text_lower:
        arg1 = "ent_doc"

    # Predicate
    pred = "UNKNOWN_PRED"
    if "giải quyết" in text_lower:
        pred = "SOLVE_01"
    elif "hỗ trợ" in text_lower:
        pred = "ASSIST_01"
    elif "đọc" in text_lower:
        pred = "READ_01"
    elif "phân tích" in text_lower:
        pred = "ANALYZE_01"
    elif "kiểm tra" in text_lower:
        pred = "VERIFY_01"
    elif "xóa" in text_lower:
        pred = "DELETE_01"
    elif "tin rằng" in text_lower:
        pred = "BELIEVE_01"
    elif "báo cáo" in text_lower:
        pred = "REPORT_01"
    elif "xem lại" in text_lower:
        pred = "REVIEW_01"

    # Negation
    negated = "không" in text_lower or "chưa" in text_lower

    # Aspect & Temporal
    aspect = "PROGRESSIVE" if "đang" in text_lower else "NONE"
    temporal = "PAST"
    if "đang" in text_lower:
        temporal = "PRESENT_PROGRESSIVE"
    elif "tin rằng" in text_lower:
        temporal = "PRESENT"
    elif "trước khi" in text_lower:
        temporal = "PRECEDES"

    # Classifier (quyển / cuốn / con / cái)
    sortal = "SORTAL_BOUND_VOLUME" if "quyển" in text_lower or "cuốn" in text_lower else "NONE"

    # Conceiver
    conceiver = "CANONICAL_SPEAKER"
    if "tin rằng" in text_lower or "báo cáo" in text_lower:
        conceiver = arg0

    eid = f"e_{scenario_id}"
    inst.nodes[eid] = {
        "id": eid,
        "type": "EVENT",
        "predicate": pred,
        "negated": negated,
        "conceiver": conceiver,
        "temporal": temporal,
        "aspect": aspect,
    }
    for ent in [arg0, arg1]:
        if ent != "UNKNOWN_ENTITY":
            inst.nodes[ent] = {
                "id": ent,
                "type": "ENTITY",
                "label": ent,
                "sortal": sortal if ent == "ent_book" else "NONE",
                "social_deixis": social if ent == "ent_user" else "NEUTRAL",
            }
    if arg0 != "UNKNOWN_ENTITY":
        inst.edges.append({"source": eid, "target": arg0, "role": ":ARG0"})
    if arg1 != "UNKNOWN_ENTITY":
        inst.edges.append({"source": eid, "target": arg1, "role": ":ARG1"})

    return inst


def transduce_rule_based(text: str, lang: str, scenario_id: str, candidate_name: str) -> SemanticInstance:
    if lang == "EN":
        return transduce_en_rule(text, scenario_id, candidate_name)
    elif lang == "JA":
        return transduce_ja_rule(text, scenario_id, candidate_name)
    elif lang == "VI":
        return transduce_vi_rule(text, scenario_id, candidate_name)
    raise ValueError(f"Unsupported language {lang}")
