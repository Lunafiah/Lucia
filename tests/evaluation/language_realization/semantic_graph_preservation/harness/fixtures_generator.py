"""
tests/evaluation/language_realization/semantic_graph_preservation/harness/fixtures_generator.py

Generates the authoritative 42-fixture evaluation corpus for the Stage 3-A SemanticGraph Preservation Audit.
Builds complete UMR-TPG SemanticGraph objects for:
- 36 baseline fixtures (EN, VI, JA across 8 communicative acts)
- 6 targeted graph-structure variants covering complex argument reversal, nested modal scope,
  and contrastive coordination.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Dict, List


def generate_audit_fixtures() -> List[Dict[str, Any]]:
    # Load 36 baseline fixtures
    baseline_path = Path("tests/evaluation/language_realization/cpu_gpu_slm/fixtures/semantic_fixtures.json")
    with open(baseline_path, "r", encoding="utf-8") as f:
        baseline_fixtures: List[Dict[str, Any]] = json.load(f)

    audit_fixtures: List[Dict[str, Any]] = []

    # Map each baseline fixture into a fixture with an explicit authoritative SemanticGraph
    for fix in baseline_fixtures:
        f_id = fix["id"]
        act = fix["act"]
        lang = fix["target_language"]
        caps = fix.get("caps_result", {})
        pred = caps.get("target_predicate", f"c:{f_id.upper()}")
        focus = caps.get("focus_argument", "ent:user")
        epistemic = caps.get("epistemic", {}).get("status", "FACT")
        polarity = caps.get("polarity", True)
        grounded = caps.get("grounded", True)
        prov_origin = caps.get("provenance", {}).get("origin", "PERCEPTION")
        premises = caps.get("provenance", {}).get("premise_ids", [])
        rule_id = caps.get("provenance", {}).get("rule_id", None)
        temporal = caps.get("temporal", "PRESENT")

        # Build authoritative SemanticGraph nodes & edges
        event_node_id = f"node:event_{pred.replace(':', '_')}"
        arg0_node_id = focus if focus else "ent:user"
        arg1_node_id = f"ent:target_{f_id}"

        nodes = [
            {
                "id": event_node_id,
                "epistemic_state": epistemic,
                "concept_symbol": pred,
                "scope_id": "scope:root" if polarity else "scope:negation",
                "polarity": polarity,
                "provenance": {
                    "origin": prov_origin,
                    "supporting_premises": premises,
                    "derivation_rule_id": rule_id,
                },
                "role": "PREDICATE_EVENT",
            },
            {
                "id": arg0_node_id,
                "epistemic_state": "FACT" if grounded else "UNKNOWN",
                "concept_symbol": arg0_node_id,
                "scope_id": "scope:root",
                "polarity": True,
                "role": ":ARG0",
            },
        ]

        edges = [
            {
                "source_id": event_node_id,
                "target_id": arg0_node_id,
                "relation_role": ":ARG0",
            }
        ]

        scopes = [
            {"scope_id": "scope:root", "scope_type": "ROOT", "parent_scope_id": None}
        ]
        if not polarity:
            scopes.append(
                {"scope_id": "scope:negation", "scope_type": "NEGATION", "parent_scope_id": "scope:root"}
            )

        # Multi-arg or specific categories
        if act in ("ASSERT", "ANSWER") and "pair_b" in f_id:
            nodes.append({
                "id": arg1_node_id,
                "epistemic_state": epistemic,
                "concept_symbol": "c:STATUS_FLAG",
                "scope_id": "scope:root",
                "polarity": True,
                "role": ":ARG1",
            })
            edges.append({
                "source_id": event_node_id,
                "target_id": arg1_node_id,
                "relation_role": ":ARG1",
            })

        graph_dict = {
            "session_id": f"session:{f_id}",
            "scopes": scopes,
            "nodes": nodes,
            "edges": edges,
            "temporal": temporal,
            "epistemic_level": epistemic,
        }

        # Embed authoritative graph into fixture
        fix_copy = dict(fix)
        fix_copy["authoritative_semantic_graph"] = graph_dict
        audit_fixtures.append(fix_copy)

    # ──────────────────────────────────────────────────────────────────────────
    # Add 6 Targeted Graph-Structure Variants
    # ──────────────────────────────────────────────────────────────────────────

    # 1. EN Argument Roles (ARG0 != ARG1 Asymmetric Reversal)
    en_arg_reversal = {
        "id": "en_arg_reversal",
        "act": "ASSERT",
        "target_language": "en",
        "semantic_features": ["argument_roles", "asymmetric_agent_patient", "multi_argument"],
        "minimal_pair_group": "pair_arg_roles",
        "minimal_pair_variant": "ASYMMETRIC",
        "caps_result": {
            "act": "ASSERT",
            "epistemic": {"status": "FACT", "confidence": 1.0, "is_grounded": True},
            "provenance": {"origin": "OBSERVATION", "premise_ids": ["log:assign_01"], "rule_id": None},
            "resolution": {"resolution_status": "RESOLVED", "resolved_entity_id": "ent:lead_dev"},
            "grounded": True,
            "target_predicate": "c:ASSIGN_TASK",
            "focus_argument": "ent:lead_dev",
            "directives": "Explicitly state that the lead developer assigned the code audit to the assistant. Do NOT reverse the roles.",
            "polarity": True,
            "temporal": "PAST",
        },
        "authoritative_semantic_graph": {
            "session_id": "session:en_arg_reversal",
            "scopes": [{"scope_id": "scope:root", "scope_type": "ROOT", "parent_scope_id": None}],
            "nodes": [
                {
                    "id": "node:event_assign",
                    "epistemic_state": "FACT",
                    "concept_symbol": "c:ASSIGN_TASK",
                    "scope_id": "scope:root",
                    "polarity": True,
                    "role": "PREDICATE_EVENT",
                },
                {"id": "ent:lead_dev", "epistemic_state": "FACT", "concept_symbol": "ent:lead_dev", "scope_id": "scope:root", "polarity": True, "role": ":ARG0"},
                {"id": "ent:code_audit", "epistemic_state": "FACT", "concept_symbol": "c:CODE_AUDIT", "scope_id": "scope:root", "polarity": True, "role": ":ARG1"},
                {"id": "ent:lucia", "epistemic_state": "FACT", "concept_symbol": "ent:lucia", "scope_id": "scope:root", "polarity": True, "role": ":ARG2"},
            ],
            "edges": [
                {"source_id": "node:event_assign", "target_id": "ent:lead_dev", "relation_role": ":ARG0"},
                {"source_id": "node:event_assign", "target_id": "ent:code_audit", "relation_role": ":ARG1"},
                {"source_id": "node:event_assign", "target_id": "ent:lucia", "relation_role": ":ARG2"},
            ],
            "temporal": "PAST",
            "epistemic_level": "FACT",
        },
        "conversation_context": {
            "user_input": "Who assigned this code audit task to whom?",
            "turn_id": 1,
        },
        "evaluation_rules": {
            "act_requirement": "ASSERT",
            "epistemic_level": "FACT",
            "required_concepts": ["lead dev|developer", "audit|task", "assigned"],
            "forbidden_additions": ["you assigned to the developer", "i assigned to the lead developer"],
            "polarity": True,
            "temporal": "PAST",
            "allowed_strengthening": True,
        },
    }

    # 2. EN Nested Proposition & Modal Scope (Belief Embedding)
    en_nested_modal_scope = {
        "id": "en_nested_modal_scope",
        "act": "ASSERT",
        "target_language": "en",
        "semantic_features": ["nested_proposition", "modal_scope", "epistemic_attribution"],
        "minimal_pair_group": "pair_nested_modal",
        "minimal_pair_variant": "BELIEF_EMBEDDED",
        "caps_result": {
            "act": "ASSERT",
            "epistemic": {"status": "INFERRED", "confidence": 0.8, "is_grounded": True},
            "provenance": {"origin": "USER_REPORT", "premise_ids": ["claim:user_report_crash"], "rule_id": "rule:reported_event"},
            "resolution": {"resolution_status": "RESOLVED", "resolved_entity_id": "ent:user"},
            "grounded": True,
            "target_predicate": "c:BELIEVE",
            "focus_argument": "ent:user",
            "directives": "Communicate that the user suspects or believes the backend crashed, but keep it embedded as the user's belief, not an objective verified crash.",
            "polarity": True,
            "temporal": "PRESENT",
        },
        "authoritative_semantic_graph": {
            "session_id": "session:en_nested_modal_scope",
            "scopes": [
                {"scope_id": "scope:root", "scope_type": "ROOT", "parent_scope_id": None},
                {"scope_id": "scope:modal_belief", "scope_type": "MODAL", "parent_scope_id": "scope:root"},
            ],
            "nodes": [
                {"id": "node:event_believe", "epistemic_state": "FACT", "concept_symbol": "c:BELIEVE", "scope_id": "scope:root", "polarity": True, "role": "PREDICATE_EVENT"},
                {"id": "ent:user", "epistemic_state": "FACT", "concept_symbol": "ent:user", "scope_id": "scope:root", "polarity": True, "role": ":ARG0"},
                {"id": "node:event_crash", "epistemic_state": "UNKNOWN", "concept_symbol": "c:CRASH", "scope_id": "scope:modal_belief", "polarity": True, "role": ":ARG1_EMBEDDED"},
                {"id": "ent:backend", "epistemic_state": "FACT", "concept_symbol": "ent:backend", "scope_id": "scope:modal_belief", "polarity": True, "role": ":ARG0_INNER"},
            ],
            "edges": [
                {"source_id": "node:event_believe", "target_id": "ent:user", "relation_role": ":ARG0"},
                {"source_id": "node:event_believe", "target_id": "node:event_crash", "relation_role": ":ARG1", "is_cross_scope_link": True},
                {"source_id": "node:event_crash", "target_id": "ent:backend", "relation_role": ":ARG0"},
            ],
            "temporal": "PRESENT",
            "epistemic_level": "INFERRED",
        },
        "conversation_context": {
            "user_input": "I have a bad feeling the backend service crashed after that commit.",
            "turn_id": 1,
        },
        "evaluation_rules": {
            "act_requirement": "ASSERT",
            "epistemic_level": "INFERRED",
            "required_concepts": ["think|believe|suspect|feeling", "backend|service|crashed"],
            "forbidden_additions": ["the backend has definitely crashed 100%", "verified crash confirmed"],
            "polarity": True,
            "temporal": "PRESENT",
            "allowed_strengthening": False,
        },
    }

    # 3. VI Argument Roles (Asymmetric Role Inversion)
    vi_arg_reversal = {
        "id": "vi_arg_reversal",
        "act": "ASSERT",
        "target_language": "vi",
        "semantic_features": ["argument_roles", "asymmetric_agent_patient"],
        "minimal_pair_group": "pair_arg_roles_vi",
        "minimal_pair_variant": "ASYMMETRIC",
        "caps_result": {
            "act": "ASSERT",
            "epistemic": {"status": "FACT", "confidence": 1.0, "is_grounded": True},
            "provenance": {"origin": "OBSERVATION", "premise_ids": ["premise:medical_log"], "rule_id": None},
            "resolution": {"resolution_status": "RESOLVED", "resolved_entity_id": "ent:bac_si"},
            "grounded": True,
            "target_predicate": "c:KHAM_BENH",
            "focus_argument": "ent:bac_si",
            "directives": "Xác nhận rõ ràng rằng bác sĩ đã khám cho bệnh nhân, tuyệt đối không đảo ngược thành bệnh nhân khám cho bác sĩ.",
            "polarity": True,
            "temporal": "PAST",
        },
        "authoritative_semantic_graph": {
            "session_id": "session:vi_arg_reversal",
            "scopes": [{"scope_id": "scope:root", "scope_type": "ROOT", "parent_scope_id": None}],
            "nodes": [
                {"id": "node:event_kham", "epistemic_state": "FACT", "concept_symbol": "c:KHAM_BENH", "scope_id": "scope:root", "polarity": True, "role": "PREDICATE_EVENT"},
                {"id": "ent:bac_si", "epistemic_state": "FACT", "concept_symbol": "ent:bac_si", "scope_id": "scope:root", "polarity": True, "role": ":ARG0"},
                {"id": "ent:benh_nhan", "epistemic_state": "FACT", "concept_symbol": "ent:benh_nhan", "scope_id": "scope:root", "polarity": True, "role": ":ARG1"},
            ],
            "edges": [
                {"source_id": "node:event_kham", "target_id": "ent:bac_si", "relation_role": ":ARG0"},
                {"source_id": "node:event_kham", "target_id": "ent:benh_nhan", "relation_role": ":ARG1"},
            ],
            "temporal": "PAST",
            "epistemic_level": "FACT",
        },
        "conversation_context": {
            "user_input": "Bác sĩ hay bệnh nhân là người thực hiện thăm khám vậy?",
            "turn_id": 1,
        },
        "evaluation_rules": {
            "act_requirement": "ASSERT",
            "epistemic_level": "FACT",
            "required_concepts": ["bác sĩ", "khám", "bệnh nhân"],
            "forbidden_additions": ["bệnh nhân đã khám cho bác sĩ"],
            "polarity": True,
            "temporal": "PAST",
            "allowed_strengthening": True,
        },
    }

    # 4. VI Nested Modal Scope (Reported Claim vs Fact)
    vi_nested_modal_scope = {
        "id": "vi_nested_modal_scope",
        "act": "ASSERT",
        "target_language": "vi",
        "semantic_features": ["nested_proposition", "modal_scope", "attribution"],
        "minimal_pair_group": "pair_nested_modal_vi",
        "minimal_pair_variant": "REPORTED_EMBEDDED",
        "caps_result": {
            "act": "ASSERT",
            "epistemic": {"status": "INFERRED", "confidence": 0.85, "is_grounded": True},
            "provenance": {"origin": "USER_REPORT", "premise_ids": ["claim:khach_hang_phan_nan"], "rule_id": "rule:reported_claim"},
            "resolution": {"resolution_status": "RESOLVED", "resolved_entity_id": "ent:khach_hang"},
            "grounded": True,
            "target_predicate": "c:BAO_CAO",
            "focus_argument": "ent:khach_hang",
            "directives": "Nêu rõ rằng khách hàng phản ánh đơn hàng bị chậm trễ, giữ đúng phạm vi phản ánh chứ không tự ý xác nhận lỗi hệ thống 100%.",
            "polarity": True,
            "temporal": "PRESENT",
        },
        "authoritative_semantic_graph": {
            "session_id": "session:vi_nested_modal_scope",
            "scopes": [
                {"scope_id": "scope:root", "scope_type": "ROOT", "parent_scope_id": None},
                {"scope_id": "scope:reported_claim", "scope_type": "MODAL", "parent_scope_id": "scope:root"},
            ],
            "nodes": [
                {"id": "node:event_bao_cao", "epistemic_state": "FACT", "concept_symbol": "c:BAO_CAO", "scope_id": "scope:root", "polarity": True, "role": "PREDICATE_EVENT"},
                {"id": "ent:khach_hang", "epistemic_state": "FACT", "concept_symbol": "ent:khach_hang", "scope_id": "scope:root", "polarity": True, "role": ":ARG0"},
                {"id": "node:event_cham_tre", "epistemic_state": "UNKNOWN", "concept_symbol": "c:CHAM_TRE", "scope_id": "scope:reported_claim", "polarity": True, "role": ":ARG1_EMBEDDED"},
                {"id": "ent:don_hang", "epistemic_state": "FACT", "concept_symbol": "ent:don_hang", "scope_id": "scope:reported_claim", "polarity": True, "role": ":ARG0_INNER"},
            ],
            "edges": [
                {"source_id": "node:event_bao_cao", "target_id": "ent:khach_hang", "relation_role": ":ARG0"},
                {"source_id": "node:event_bao_cao", "target_id": "node:event_cham_tre", "relation_role": ":ARG1", "is_cross_scope_link": True},
                {"source_id": "node:event_cham_tre", "target_id": "ent:don_hang", "relation_role": ":ARG0"},
            ],
            "temporal": "PRESENT",
            "epistemic_level": "INFERRED",
        },
        "conversation_context": {
            "user_input": "Tình hình đơn hàng có gì mới không?",
            "turn_id": 1,
        },
        "evaluation_rules": {
            "act_requirement": "ASSERT",
            "epistemic_level": "INFERRED",
            "required_concepts": ["khách hàng|người mua", "phản ánh|báo|khiếu nại", "chậm|trễ"],
            "forbidden_additions": ["chắc chắn lỗi hoàn toàn do kho vận chuyển"],
            "polarity": True,
            "temporal": "PRESENT",
            "allowed_strengthening": False,
        },
    }

    # 5. JA Scope Negation Contrast (A and NOT B)
    ja_scope_negation_contrast = {
        "id": "ja_scope_negation_contrast",
        "act": "ASSERT",
        "target_language": "ja",
        "semantic_features": ["scope", "negation_scope", "contrastive_coordination"],
        "minimal_pair_group": "pair_scope_contrast_ja",
        "minimal_pair_variant": "CONTRASTIVE_NEGATION",
        "caps_result": {
            "act": "ASSERT",
            "epistemic": {"status": "FACT", "confidence": 1.0, "is_grounded": True},
            "provenance": {"origin": "PIPELINE_LOG", "premise_ids": ["ci:tests_pass", "ci:deploy_blocked"], "rule_id": None},
            "resolution": {"resolution_status": "RESOLVED", "resolved_entity_id": "ent:system"},
            "grounded": True,
            "target_predicate": "c:TEST_PASSED_BUT_DEPLOY_BLOCKED",
            "focus_argument": "ent:system",
            "directives": "テストは全件合格したが、本番デプロイはまだ承認されていない（未完了である）という対比を正確に伝えてください。",
            "polarity": True,
            "temporal": "PRESENT",
        },
        "authoritative_semantic_graph": {
            "session_id": "session:ja_scope_negation_contrast",
            "scopes": [
                {"scope_id": "scope:root", "scope_type": "ROOT", "parent_scope_id": None},
                {"scope_id": "scope:negation_deploy", "scope_type": "NEGATION", "parent_scope_id": "scope:root"},
            ],
            "nodes": [
                {"id": "node:event_test", "epistemic_state": "FACT", "concept_symbol": "c:TEST_PASS", "scope_id": "scope:root", "polarity": True, "role": "CONJUNCT_A"},
                {"id": "node:event_deploy", "epistemic_state": "FACT", "concept_symbol": "c:DEPLOY_APPROVE", "scope_id": "scope:negation_deploy", "polarity": False, "role": "CONJUNCT_B"},
            ],
            "edges": [
                {"source_id": "node:event_test", "target_id": "node:event_deploy", "relation_role": ":CONTRAST"},
            ],
            "temporal": "PRESENT",
            "epistemic_level": "FACT",
        },
        "conversation_context": {
            "user_input": "テストとデプロイの進捗はどうなっていますか？",
            "turn_id": 1,
        },
        "evaluation_rules": {
            "act_requirement": "ASSERT",
            "epistemic_level": "FACT",
            "required_concepts": ["テスト", "合格|パス|成功", "デプロイ", "未|まだ|承認されてい"],
            "forbidden_additions": ["デプロイも完了しました", "テストが失敗しました"],
            "polarity": True,
            "temporal": "PRESENT",
            "allowed_strengthening": True,
        },
    }

    # 6. JA Nested Reported Attribution
    ja_nested_modal_scope = {
        "id": "ja_nested_modal_scope",
        "act": "ASSERT",
        "target_language": "ja",
        "semantic_features": ["nested_proposition", "modal_scope", "attribution"],
        "minimal_pair_group": "pair_nested_attribution_ja",
        "minimal_pair_variant": "ATTRIBUTION_EMBEDDED",
        "caps_result": {
            "act": "ASSERT",
            "epistemic": {"status": "INFERRED", "confidence": 0.85, "is_grounded": True},
            "provenance": {"origin": "USER_REPORT", "premise_ids": ["msg:tanaka_report"], "rule_id": "rule:reported_event"},
            "resolution": {"resolution_status": "RESOLVED", "resolved_entity_id": "ent:tanaka_san"},
            "grounded": True,
            "target_predicate": "c:REPORT",
            "focus_argument": "ent:tanaka_san",
            "directives": "田中さんがサーバーは稼働中だと報告している旨を伝え、Lucia自身の直接確認ではなく田中さんの報告であるという帰属スコープを維持してください。",
            "polarity": True,
            "temporal": "PRESENT",
        },
        "authoritative_semantic_graph": {
            "session_id": "session:ja_nested_modal_scope",
            "scopes": [
                {"scope_id": "scope:root", "scope_type": "ROOT", "parent_scope_id": None},
                {"scope_id": "scope:reported_tanaka", "scope_type": "MODAL", "parent_scope_id": "scope:root"},
            ],
            "nodes": [
                {"id": "node:event_report", "epistemic_state": "FACT", "concept_symbol": "c:REPORT", "scope_id": "scope:root", "polarity": True, "role": "PREDICATE_EVENT"},
                {"id": "ent:tanaka_san", "epistemic_state": "FACT", "concept_symbol": "ent:tanaka_san", "scope_id": "scope:root", "polarity": True, "role": ":ARG0"},
                {"id": "node:event_running", "epistemic_state": "UNKNOWN", "concept_symbol": "c:SERVER_RUNNING", "scope_id": "scope:reported_tanaka", "polarity": True, "role": ":ARG1_EMBEDDED"},
            ],
            "edges": [
                {"source_id": "node:event_report", "target_id": "ent:tanaka_san", "relation_role": ":ARG0"},
                {"source_id": "node:event_report", "target_id": "node:event_running", "relation_role": ":ARG1", "is_cross_scope_link": True},
            ],
            "temporal": "PRESENT",
            "epistemic_level": "INFERRED",
        },
        "conversation_context": {
            "user_input": "サーバーの状態について誰か何か言っていましたか？",
            "turn_id": 1,
        },
        "evaluation_rules": {
            "act_requirement": "ASSERT",
            "epistemic_level": "INFERRED",
            "required_concepts": ["田中", "報告|言って", "稼働|動いて"],
            "forbidden_additions": ["私が直接確認したところ100%正常です"],
            "polarity": True,
            "temporal": "PRESENT",
            "allowed_strengthening": False,
        },
    }

    audit_fixtures.extend([
        en_arg_reversal,
        en_nested_modal_scope,
        vi_arg_reversal,
        vi_nested_modal_scope,
        ja_scope_negation_contrast,
        ja_nested_modal_scope,
    ])

    return audit_fixtures


def main() -> None:
    fixtures = generate_audit_fixtures()
    out_file = Path("tests/evaluation/language_realization/semantic_graph_preservation/fixtures/audit_fixtures.json")
    out_file.parent.mkdir(parents=True, exist_ok=True)
    with open(out_file, "w", encoding="utf-8") as f:
        json.dump(fixtures, f, ensure_ascii=False, indent=2)
    print(f"Successfully generated {len(fixtures)} audit fixtures at {out_file}")


if __name__ == "__main__":
    main()
