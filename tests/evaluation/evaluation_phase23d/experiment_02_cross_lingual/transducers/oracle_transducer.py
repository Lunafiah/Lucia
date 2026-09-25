"""
Phase 23-D — EXP-02: Oracle Semantic Transducer
Deterministically converts gold parallel semantic intentions into
exact semantic graphs for UMR-TPG, V-UMR, and DRS-Graph across EN, JA, VI.
This tests representation capability under perfect semantic input.
"""
from typing import Dict, Any, List, Optional
import numpy as np


class SemanticInstance:
    """Unified container for an instantiated candidate semantic graph."""
    def __init__(self, candidate_name: str, language: str, scenario_id: str):
        self.candidate_name = candidate_name
        self.language = language
        self.scenario_id = scenario_id
        self.nodes: Dict[str, Dict[str, Any]] = {}
        self.edges: List[Dict[str, Any]] = []
        self.metadata: Dict[str, Any] = {}
        self.boxes: Dict[str, Dict[str, Any]] = {}  # For DRS-Graph
        self.metric_vectors: Dict[str, np.ndarray] = {}  # For V-UMR


def build_oracle_umr_tpg(scenario: Dict[str, Any], lang: str) -> SemanticInstance:
    inst = SemanticInstance("UMR-TPG", lang, scenario["id"])
    intent = scenario["canonical_intent"]
    ans = scenario["expected_answers"]

    # Entities
    for ent in ans["Q1_entities"]:
        inst.nodes[ent] = {
            "id": ent,
            "type": "ENTITY" if ent != "UNKNOWN_ENTITY" else "UNRESOLVED_ENTITY",
            "label": ent,
            "sortal": ans.get("Q9_sortal", "NONE"),
            "social_deixis": ans.get("Q8_social_relation", "NEUTRAL") if ent == "ent_user" else "NEUTRAL",
        }

    # Primary Event
    eid = intent.get("event_id", "e1")
    inst.nodes[eid] = {
        "id": eid,
        "type": "EVENT",
        "predicate": ans["Q2_predicate"],
        "negated": ans["Q5_negation"],
        "conceiver": ans["Q6_conceiver"],
        "temporal": ans["Q4_temporal"],
        "aspect": intent.get("aspect", "NONE"),
    }

    # Thematic roles
    if "Q3_arg0" in ans and ans["Q3_arg0"] != "NONE":
        inst.edges.append({"source": eid, "target": ans["Q3_arg0"], "role": ":ARG0"})
    if "Q3_arg1" in ans and ans["Q3_arg1"] != "NONE":
        inst.edges.append({"source": eid, "target": ans["Q3_arg1"], "role": ":ARG1"})

    # Nested sub-event if present
    if "sub_event" in intent:
        sub_e = intent["sub_event"]
        inst.nodes[sub_e] = {"id": sub_e, "type": "EVENT", "predicate": intent.get("nested_pred", "SUB_EVENT")}
        inst.edges.append({"source": eid, "target": sub_e, "role": ":sub-event"})
        if "nested_agent" in intent:
            inst.edges.append({"source": sub_e, "target": intent["nested_agent"], "role": ":ARG0"})
        if "nested_patient" in intent:
            inst.edges.append({"source": sub_e, "target": intent["nested_patient"], "role": ":ARG1"})

    # Cross-sentence reference edge if present
    if ans.get("Q10_cross_sentence") != "NONE":
        shared = ans["Q10_cross_sentence"]
        inst.edges.append({"source": eid, "target": shared, "role": ":coref"})

    return inst


def build_oracle_v_umr(scenario: Dict[str, Any], lang: str) -> SemanticInstance:
    # V-UMR builds on UMR-TPG and adds 32D metric coordinates
    inst = build_oracle_umr_tpg(scenario, lang)
    inst.candidate_name = "V-UMR"
    for nid in inst.nodes:
        h = abs(hash(f"{nid}_{lang}_{scenario['id']}")) % (2**32)
        rng = np.random.RandomState(h)
        inst.metric_vectors[nid] = rng.normal(0.0, 1.0, size=32)
    return inst


def build_oracle_drs_graph(scenario: Dict[str, Any], lang: str) -> SemanticInstance:
    inst = SemanticInstance("DRS-Graph", lang, scenario["id"])
    ans = scenario["expected_answers"]
    intent = scenario["canonical_intent"]

    # Top Universe Box
    inst.boxes["B_TOP"] = {
        "id": "B_TOP",
        "universe": set(ans["Q1_entities"]),
        "conditions": [
            {"type": "PRED", "pred": ans["Q2_predicate"], "event": intent.get("event_id", "e1")}
        ],
        "is_negated": False,
        "conceiver": ans["Q6_conceiver"],
        "temporal": ans["Q4_temporal"],
    }

    # If negated, wrap condition in negation box
    if ans["Q5_negation"]:
        inst.boxes["B_NEG"] = {
            "id": "B_NEG",
            "parent": "B_TOP",
            "conditions": [
                {
                    "type": "PRED",
                    "pred": ans["Q2_predicate"],
                    "arg0": ans.get("Q3_arg0"),
                    "arg1": ans.get("Q3_arg1"),
                }
            ],
            "is_negated": True,
        }
        inst.boxes["B_TOP"]["conditions"].append({"neg_box": "B_NEG"})
    else:
        inst.boxes["B_TOP"]["conditions"].append({
            "type": "ROLES",
            "arg0": ans.get("Q3_arg0"),
            "arg1": ans.get("Q3_arg1"),
            "social": ans.get("Q8_social_relation", "NEUTRAL"),
            "sortal": ans.get("Q9_sortal", "NONE"),
        })

    return inst


def transduce_oracle(scenario: Dict[str, Any], candidate_name: str, lang: str) -> SemanticInstance:
    if candidate_name == "UMR-TPG":
        return build_oracle_umr_tpg(scenario, lang)
    elif candidate_name == "V-UMR":
        return build_oracle_v_umr(scenario, lang)
    elif candidate_name == "DRS-Graph":
        return build_oracle_drs_graph(scenario, lang)
    raise ValueError(f"Unknown candidate {candidate_name}")
