"""
Phase 23-D — EXP-02: Multilingual Semantic Query Suite (Q1–Q10)
Executes standardized semantic probes against candidate semantic instances
to evaluate functional equivalence without requiring graph isomorphism.
"""
from typing import Dict, Any, List, Tuple
try:
    from ..transducers.oracle_transducer import SemanticInstance
except (ImportError, ValueError):
    from tests.evaluation.evaluation_phase23d.experiment_02_cross_lingual.transducers.oracle_transducer import SemanticInstance


def extract_q1_entities(inst: SemanticInstance) -> List[str]:
    """Q1: Extract set of discourse entities."""
    if inst.candidate_name == "DRS-Graph" and "B_TOP" in inst.boxes:
        return sorted(list(inst.boxes["B_TOP"]["universe"]))
    return sorted([nid for nid, n in inst.nodes.items() if n.get("type") in ["ENTITY", "UNRESOLVED_ENTITY"]])


def extract_q2_predicate(inst: SemanticInstance) -> str:
    """Q2: Extract primary predicate."""
    if inst.candidate_name == "DRS-Graph" and "B_TOP" in inst.boxes:
        for c in inst.boxes["B_TOP"]["conditions"]:
            if c.get("type") == "PRED":
                return c.get("pred", "NONE")
    for nid, n in inst.nodes.items():
        if n.get("type") == "EVENT":
            return n.get("predicate", "NONE")
    return "NONE"


def extract_q3_roles(inst: SemanticInstance) -> Dict[str, str]:
    """Q3: Extract ARG0 and ARG1 bindings."""
    roles = {":ARG0": "NONE", ":ARG1": "NONE"}
    if inst.candidate_name == "DRS-Graph":
        for b in inst.boxes.values():
            for c in b.get("conditions", []):
                if "arg0" in c:
                    roles[":ARG0"] = c.get("arg0", "NONE")
                if "arg1" in c:
                    roles[":ARG1"] = c.get("arg1", "NONE")
        return roles

    for e in inst.edges:
        if e.get("role") in [":ARG0", ":ARG1"]:
            roles[e["role"]] = e.get("target", "NONE")
    return roles


def extract_q4_temporal(inst: SemanticInstance) -> str:
    """Q4: Extract temporal relation / aspect."""
    if inst.candidate_name == "DRS-Graph" and "B_TOP" in inst.boxes:
        return inst.boxes["B_TOP"].get("temporal", "NONE")
    for n in inst.nodes.values():
        if n.get("type") == "EVENT":
            return n.get("temporal", "NONE")
    return "NONE"


def extract_q5_negation(inst: SemanticInstance) -> bool:
    """Q5: Extract negation status."""
    if inst.candidate_name == "DRS-Graph":
        return any(b.get("is_negated", False) for b in inst.boxes.values())
    for n in inst.nodes.values():
        if n.get("type") == "EVENT":
            return n.get("negated", False)
    return False


def extract_q6_conceiver(inst: SemanticInstance) -> str:
    """Q6: Extract epistemic conceiver."""
    if inst.candidate_name == "DRS-Graph" and "B_TOP" in inst.boxes:
        return inst.boxes["B_TOP"].get("conceiver", "CANONICAL_SPEAKER")
    for n in inst.nodes.values():
        if n.get("type") == "EVENT":
            return n.get("conceiver", "CANONICAL_SPEAKER")
    return "CANONICAL_SPEAKER"


def extract_q7_omitted_resolution(inst: SemanticInstance) -> str:
    """Q7: Extract resolution of dropped arguments."""
    roles = extract_q3_roles(inst)
    arg0 = roles.get(":ARG0")
    if arg0 == "UNKNOWN_ENTITY":
        return "UNKNOWN_ENTITY"
    if arg0 == "ent_user" and any(n.get("social_deixis") != "NEUTRAL" for n in inst.nodes.values()):
        return "RESOLVED_DEIXIS"
    if any(e.get("role") == ":coref" for e in inst.edges):
        return "RESOLVED_COREFERENCE"
    return "NONE_OVERT"


def extract_q8_social(inst: SemanticInstance) -> str:
    """Q8: Extract social relation / deixis."""
    if inst.candidate_name == "DRS-Graph":
        for b in inst.boxes.values():
            for c in b.get("conditions", []):
                if "social" in c:
                    return c.get("social", "NEUTRAL")
    for n in inst.nodes.values():
        if n.get("social_deixis", "NEUTRAL") != "NEUTRAL":
            return n.get("social_deixis")
    return "NEUTRAL"


def extract_q9_sortal(inst: SemanticInstance) -> str:
    """Q9: Extract sortal classifier constraint."""
    if inst.candidate_name == "DRS-Graph":
        for b in inst.boxes.values():
            for c in b.get("conditions", []):
                if "sortal" in c:
                    return c.get("sortal", "NONE")
    for n in inst.nodes.values():
        if n.get("sortal", "NONE") != "NONE":
            return n.get("sortal")
    return "NONE"


def extract_q10_cross_sentence(inst: SemanticInstance) -> str:
    """Q10: Extract cross-sentence entity reference."""
    for e in inst.edges:
        if e.get("role") == ":coref":
            return e.get("target", "NONE")
    return "NONE"


QUERY_EXTRACTORS = {
    "Q1": extract_q1_entities,
    "Q2": extract_q2_predicate,
    "Q3": extract_q3_roles,
    "Q4": extract_q4_temporal,
    "Q5": extract_q5_negation,
    "Q6": extract_q6_conceiver,
    "Q7": extract_q7_omitted_resolution,
    "Q8": extract_q8_social,
    "Q9": extract_q9_sortal,
    "Q10": extract_q10_cross_sentence,
}


def evaluate_query_suite(inst_a: SemanticInstance, inst_b: SemanticInstance) -> Dict[str, bool]:
    """Evaluates pairwise query equivalence across all 10 queries."""
    results = {}
    for q_id, extractor in QUERY_EXTRACTORS.items():
        val_a = extractor(inst_a)
        val_b = extractor(inst_b)
        results[q_id] = (val_a == val_b)
    return results
