"""
tests/evaluation/language_realization/semantic_graph_preservation/harness/evaluator.py

Core evaluation engine for Stage 3-A SemanticGraph Preservation Audit.
Implements:
- Level 1: Deterministic Structural Preservation (SemanticGraph -> Realization Input Prompt)
- Level 2: Semantic Realization Evaluation (SemanticGraph -> Generated Text)
- Level 3: Discourse Acceptability Classification (True Loss vs Acceptable Ellipsis vs Paraphrase)
"""

from __future__ import annotations

import re
from dataclasses import asdict, dataclass, field
from typing import Any, Dict, List, Optional, Set, Tuple


@dataclass
class StructuralComparisonReport:
    fixture_id: str
    target_language: str
    act: str
    total_graph_nodes: int
    preserved_nodes_count: int
    dropped_nodes_count: int
    preserved_node_ids: List[str]
    dropped_node_ids: List[str]
    total_graph_edges: int
    preserved_edges_count: int
    dropped_edges_count: int
    dropped_edge_roles: List[str]
    total_scopes: int
    preserved_scopes_count: int
    dropped_scopes_count: int
    dropped_scope_types: List[str]
    provenance_present: bool
    provenance_preserved: bool
    serialization_fidelity_ratio: float  # (preserved_nodes + preserved_edges) / total
    prompt_serialization_text: str

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


class StructuralEvaluator:
    """Level 1: Deterministic evaluation of structural graph serialization."""

    def evaluate(self, fixture: Dict[str, Any], prompt_text: str) -> StructuralComparisonReport:
        f_id = fixture["id"]
        lang = fixture.get("target_language", "en")
        act = fixture.get("act", "ASSERT")
        graph = fixture.get("authoritative_semantic_graph", {})

        nodes = graph.get("nodes", [])
        edges = graph.get("edges", [])
        scopes = graph.get("scopes", [])
        caps = fixture.get("caps_result", {})

        # Extract what PromptAssembler serialized in [COMMUNICATIVE INTENT & PROPOSITION]
        target_pred = caps.get("target_predicate", "")
        focus_arg = caps.get("focus_argument", "")
        epistemic = caps.get("epistemic", {}).get("status", "")
        grounded_str = str(caps.get("grounded", "")).lower()

        preserved_nodes = []
        dropped_nodes = []
        for n in nodes:
            n_id = n["id"]
            concept = n.get("concept_symbol", "")
            # Check if this node was explicitly included in the prompt serialization lines
            if concept == target_pred or n_id == focus_arg or concept == focus_arg:
                preserved_nodes.append(n_id)
            else:
                dropped_nodes.append(n_id)

        # In current PromptAssembler, edges and roles are NEVER serialized to prompt lines
        preserved_edges = []
        dropped_edges = []
        dropped_edge_roles = []
        for e in edges:
            # Current PromptAssembler has zero edge serialization
            dropped_edges.append(f"{e['source_id']}->{e['target_id']}({e.get('relation_role')})")
            dropped_edge_roles.append(e.get("relation_role", "unknown"))

        # Scopes are NEVER explicitly serialized (only ROOT vs implicit)
        preserved_scopes = []
        dropped_scopes = []
        dropped_scope_types = []
        for s in scopes:
            if s.get("scope_type") == "ROOT":
                preserved_scopes.append(s["scope_id"])
            else:
                dropped_scopes.append(s["scope_id"])
                dropped_scope_types.append(s.get("scope_type", "UNKNOWN"))

        # Provenance: checked if provenance metadata is present in graph
        prov_present = any(n.get("provenance") is not None for n in nodes) or bool(caps.get("provenance"))
        # In current PromptAssembler, provenance premise_ids and rule_id are omitted
        prov_preserved = False

        total_elements = len(nodes) + len(edges) + len(scopes)
        preserved_elements = len(preserved_nodes) + len(preserved_edges) + len(preserved_scopes)
        ratio = round(preserved_elements / max(1, total_elements), 4)

        return StructuralComparisonReport(
            fixture_id=f_id,
            target_language=lang,
            act=act,
            total_graph_nodes=len(nodes),
            preserved_nodes_count=len(preserved_nodes),
            dropped_nodes_count=len(dropped_nodes),
            preserved_node_ids=preserved_nodes,
            dropped_node_ids=dropped_nodes,
            total_graph_edges=len(edges),
            preserved_edges_count=len(preserved_edges),
            dropped_edges_count=len(dropped_edges),
            dropped_edge_roles=dropped_edge_roles,
            total_scopes=len(scopes),
            preserved_scopes_count=len(preserved_scopes),
            dropped_scopes_count=len(dropped_scopes),
            dropped_scope_types=dropped_scope_types,
            provenance_present=prov_present,
            provenance_preserved=prov_preserved,
            serialization_fidelity_ratio=ratio,
            prompt_serialization_text=prompt_text,
        )


class SemanticRealizerEvaluator:
    """Level 2 & Level 3: Semantic realization fidelity & discourse acceptability."""

    INTROSPECTIVE_AFFECT_PATTERNS = [
        re.compile(r"tôi cảm thấy (vui|buồn|lo lắng|hạnh phúc|tức giận)", re.IGNORECASE),
        re.compile(r"i feel (happy|sad|anxious|overjoyed|angry)", re.IGNORECASE),
        re.compile(r"(私は|僕が)(とても)?(嬉しい|悲しい|怒って)います", re.IGNORECASE),
        re.compile(r"(as an ai|là một ai|ai言語モデルとして|aiとして)", re.IGNORECASE),
    ]

    CERTAINTY_STRENGTHENING = {
        "vi": [re.compile(r"(chắc chắn 100%|chắc chắn là|tuyệt đối|cam đoan|hoàn toàn chắc chắn)", re.IGNORECASE)],
        "en": [re.compile(r"(100% certain|absolutely certain|definitely|guaranteed to be|without any doubt|undeniably)", re.IGNORECASE)],
        "ja": [re.compile(r"(絶対に|確実に|100%間違いなく|断言します)", re.IGNORECASE)],
    }

    HEDGING_PATTERNS = {
        "vi": [re.compile(r"(có vẻ|dường như|thấy|hình như|dự đoán|phỏng đoán)", re.IGNORECASE)],
        "en": [re.compile(r"(seems|appears|likely|might|could|possibly|suspect|feeling)", re.IGNORECASE)],
        "ja": [re.compile(r"(ようです|思われます|かもしれません|可能性がある|報告)", re.IGNORECASE)],
    }

    def evaluate_realization(
        self,
        fixture: Dict[str, Any],
        realized_text: str,
        structural_report: StructuralComparisonReport,
    ) -> Dict[str, Any]:
        rules = fixture.get("evaluation_rules", {})
        act_req = rules.get("act_requirement", fixture.get("act", "ASSERT"))
        epistemic_level = rules.get("epistemic_level", "FACT")
        polarity_expected = rules.get("polarity", True)
        temporal_expected = rules.get("temporal", "PRESENT")
        required_concepts = rules.get("required_concepts", [])
        forbidden_additions = rules.get("forbidden_additions", [])
        allowed_strengthening = rules.get("allowed_strengthening", True)
        lang = fixture.get("target_language", "en")
        norm_text = realized_text.strip()

        # Concept matches
        concepts_preserved = []
        concepts_missing = []
        for pattern_str in required_concepts:
            regex = re.compile(rf"({pattern_str})", re.IGNORECASE)
            if regex.search(norm_text):
                concepts_preserved.append(pattern_str)
            else:
                concepts_missing.append(pattern_str)

        # Forbidden additions (hallucinations / ungrounded claims)
        forbidden_triggered = []
        for pattern_str in forbidden_additions:
            regex = re.compile(rf"({pattern_str})", re.IGNORECASE)
            if regex.search(norm_text):
                forbidden_triggered.append(pattern_str)

        # Introspective affect filter
        introspective_detected = any(rx.search(norm_text) for rx in self.INTROSPECTIVE_AFFECT_PATTERNS)

        # Epistemic strengthening check
        epistemic_strengthened = False
        if not allowed_strengthening or epistemic_level in ("INFERRED", "UNKNOWN", "AMBIGUOUS"):
            patterns = self.CERTAINTY_STRENGTHENING.get(lang, [])
            for rx in patterns:
                if rx.search(norm_text):
                    epistemic_strengthened = True
                    break

        # Polarity check
        polarity_preserved = True
        if not polarity_expected:
            # Check negation cues
            negation_cues = {
                "vi": ["không", "chưa", "chẳng", "đừng", "từ chối"],
                "en": ["not", "no", "never", "cannot", "hasn't", "didn't", "unable", "refuse"],
                "ja": ["ない", "ません", "なかった", "未", "拒否"],
            }
            cues = negation_cues.get(lang, ["not", "no"])
            if not any(re.search(rf"\b{re.escape(c)}\b" if lang == "en" else re.escape(c), norm_text, re.IGNORECASE) for c in cues):
                polarity_preserved = False

        # Act fulfillment check
        act_fulfilled = True
        if act_req == "INQUIRE" and not re.search(r"(\?|như thế nào|tại sao|vì sao|what|why|how|何|どう)", norm_text, re.IGNORECASE):
            act_fulfilled = False
        elif act_req == "REFUSE" and not any(re.search(c, norm_text, re.IGNORECASE) for c in ["không thể", "chưa có", "cannot", "unable", "できません", "未対応"]):
            act_fulfilled = False
        elif act_req == "CLARIFY" and not any(re.search(c, norm_text, re.IGNORECASE) for c in ["nào", "which", "どちら", "どの"]):
            act_fulfilled = False

        # Discourse Acceptability Analysis (Level 3)
        is_acceptable_ellipsis = False
        is_paraphrase = False
        evaluator_uncertain = False

        # Detect ellipsis vs loss:
        # In Japanese or Vietnamese, elision of subject ("ent:user" or "ent:lucia") is standard grammatical ellipsis
        if len(concepts_missing) == 1 and concepts_missing[0] in ("user", "người dùng", "tôi", "私"):
            is_acceptable_ellipsis = True

        # Paraphrase check: if all core concepts preserved and no forbidden additions
        if len(concepts_missing) == 0 and len(forbidden_triggered) == 0:
            is_paraphrase = True

        # Critical Semantic Error Determination
        has_critical_error = False
        failure_labels = []

        if len(forbidden_triggered) > 0:
            if not polarity_preserved:
                has_critical_error = True
                failure_labels.append("CONTRADICTED")
            else:
                failure_labels.append("UNSUPPORTED_ADDITION")

        if epistemic_strengthened:
            has_critical_error = True
            failure_labels.append("EPISTEMIC_DISTORTION")

        if not polarity_preserved:
            has_critical_error = True
            if "CONTRADICTED" not in failure_labels:
                failure_labels.append("CONTRADICTED")

        if not act_fulfilled:
            has_critical_error = True
            failure_labels.append("COMMUNICATIVE_ACT_FAILURE")

        if len(concepts_missing) > 0 and not is_acceptable_ellipsis:
            has_critical_error = True
            failure_labels.append("ARGUMENT_ENTITY_LOSS")

        if introspective_detected:
            has_critical_error = True
            failure_labels.append("EPISTEMIC_DISTORTION")

        # Fallback to SUPPORTED if no critical errors
        if not has_critical_error and len(failure_labels) == 0:
            failure_labels.append("SUPPORTED")
            if is_acceptable_ellipsis:
                failure_labels.append("ACCEPTABLE_ELLIPSIS")
            elif is_paraphrase:
                failure_labels.append("PARAPHRASE")

        # Determine Root Cause Layer (Chain attribution)
        attribution = "SUPPORTED"
        if has_critical_error:
            # Check if the error is due to Serialization loss vs Realizer failure
            if structural_report.dropped_nodes_count > 0 or structural_report.dropped_edges_count > 0:
                # If the lost concept/role was in dropped_nodes or dropped_edges and NOT in directives
                lost_str = " ".join(concepts_missing)
                if any(d_role in lost_str for d_role in structural_report.dropped_edge_roles):
                    attribution = "SERIALIZATION"
                elif "scope" in fixture.get("semantic_features", []) and structural_report.dropped_scopes_count > 0:
                    attribution = "SERIALIZATION"
                else:
                    attribution = "REALIZER"
            else:
                attribution = "REALIZER"
        elif is_acceptable_ellipsis:
            attribution = "ELLIPSIS"

        return {
            "fixture_id": fixture["id"],
            "target_language": lang,
            "realized_text": norm_text,
            "concepts_preserved": concepts_preserved,
            "concepts_missing": concepts_missing,
            "forbidden_triggered": forbidden_triggered,
            "epistemic_strengthened": epistemic_strengthened,
            "polarity_preserved": polarity_preserved,
            "act_fulfilled": act_fulfilled,
            "is_acceptable_ellipsis": is_acceptable_ellipsis,
            "is_paraphrase": is_paraphrase,
            "has_critical_error": has_critical_error,
            "semantic_labels": failure_labels,
            "attribution": attribution,
        }
