"""
Phase 23-D — EXP-01 Dataset Generator
Generates deterministic abstract semantic structures for evaluating
compositionality, recursion, role-binding preservation, and scoping
across depths D in {1, 2, 3, 4}.
"""
from typing import Dict, List, Any, Optional
import json
import os


def generate_corpus(seed: int = 42) -> Dict[str, Any]:
    """Generates deterministic semantic corpus with 6 test suites across depths 1 to 4."""
    corpus: Dict[str, Any] = {
        "metadata": {
            "experiment": "EXP-01_compositionality",
            "seed": seed,
            "version": "1.0.0",
            "depths": [1, 2, 3, 4],
            "suites": [
                "simple_role_binding",
                "nested_proposition",
                "nested_with_role_binding",
                "negated_proposition",
                "nested_negation_scope",
                "adversarial_role_swap",
            ],
        },
        "scenarios": [],
    }

    # Entities pool
    entities = {
        "ent_user": {"id": "ent_user", "label": "USER", "type": "ENTITY"},
        "ent_lucia": {"id": "ent_lucia", "label": "LUCIA", "type": "ENTITY"},
        "ent_admin": {"id": "ent_admin", "label": "ADMIN", "type": "ENTITY"},
        "ent_agent_c": {"id": "ent_agent_c", "label": "AGENT_C", "type": "ENTITY"},
        "ent_task": {"id": "ent_task", "label": "TASK", "type": "ENTITY"},
        "ent_book": {"id": "ent_book", "label": "BOOK", "type": "ENTITY"},
        "ent_home": {"id": "ent_home", "label": "HOME", "type": "ENTITY"},
        "ent_office": {"id": "ent_office", "label": "OFFICE", "type": "ENTITY"},
    }

    scenario_id = 1

    for depth in [1, 2, 3, 4]:
        # ── 1. Simple Role Binding ──────────────────────────────────────────────
        corpus["scenarios"].append({
            "id": f"SCEN_{scenario_id:03d}",
            "depth": depth,
            "suite": "simple_role_binding",
            "description": f"Standard predicate-argument frame at depth {depth}",
            "root_event": f"e_root_d{depth}",
            "independent_assertion": {
                "id": "e_indep_01",
                "predicate": "LOCATED_IN",
                "roles": {":ARG0": "ent_user", ":ARG1": "ent_home"},
                "negated": False,
            },
            "events": [
                {
                    "id": f"e_d{depth}_base",
                    "predicate": "EXECUTE_01",
                    "roles": {":ARG0": "ent_user", ":ARG1": "ent_task"},
                    "sub_event": None,
                    "negated": False,
                }
            ],
            "expected_bindings": [
                {"event": f"e_d{depth}_base", "role": ":ARG0", "expected_filler": "ent_user"},
                {"event": f"e_d{depth}_base", "role": ":ARG1", "expected_filler": "ent_task"},
            ],
            "expected_paths": [
                {"start": f"e_d{depth}_base", "path": [":ARG0"], "expected_terminal": "ent_user"},
                {"start": f"e_d{depth}_base", "path": [":ARG1"], "expected_terminal": "ent_task"},
            ],
            "expected_scopes": [
                {"event": f"e_d{depth}_base", "negated": False, "modal_scope": None}
            ],
        })
        scenario_id += 1

        # ── 2. Nested Proposition (Pure Embedding) ──────────────────────────────
        events_nested = []
        expected_paths_nested = []
        path_steps = []
        for d in range(1, depth + 1):
            eid = f"e_nest_d{depth}_lvl{d}"
            sub_id = f"e_nest_d{depth}_lvl{d+1}" if d < depth else None
            events_nested.append({
                "id": eid,
                "predicate": f"PRED_LVL_{d}",
                "roles": {":ARG0": f"ent_user" if d % 2 == 1 else "ent_lucia"},
                "sub_event": sub_id,
                "negated": False,
            })
            if d < depth:
                path_steps.append(":sub-event")

        path_steps.append(":ARG0")
        expected_paths_nested.append({
            "start": f"e_nest_d{depth}_lvl1",
            "path": path_steps,
            "expected_terminal": "ent_user" if depth % 2 == 1 else "ent_lucia",
        })

        corpus["scenarios"].append({
            "id": f"SCEN_{scenario_id:03d}",
            "depth": depth,
            "suite": "nested_proposition",
            "description": f"Pure nested proposition chain at depth {depth}",
            "root_event": f"e_nest_d{depth}_lvl1",
            "independent_assertion": {
                "id": "e_indep_02",
                "predicate": "STATUS_CHECK",
                "roles": {":ARG0": "ent_lucia", ":ARG1": "ent_task"},
                "negated": False,
            },
            "events": events_nested,
            "expected_bindings": [
                {"event": e["id"], "role": ":ARG0", "expected_filler": e["roles"][":ARG0"]}
                for e in events_nested
            ],
            "expected_paths": expected_paths_nested,
            "expected_scopes": [
                {"event": e["id"], "negated": False, "modal_scope": None}
                for e in events_nested
            ],
        })
        scenario_id += 1

        # ── 3. Nested Proposition + Multi-Role Binding ──────────────────────────
        events_multi = []
        expected_paths_multi = []
        expected_bindings_multi = []
        for d in range(1, depth + 1):
            eid = f"e_multi_d{depth}_lvl{d}"
            sub_id = f"e_multi_d{depth}_lvl{d+1}" if d < depth else None
            arg0 = "ent_user" if d == 1 else ("ent_lucia" if d == 2 else ("ent_admin" if d == 3 else "ent_agent_c"))
            arg1 = "ent_book" if d == depth else ("ent_task" if d % 2 == 0 else "ent_office")
            events_multi.append({
                "id": eid,
                "predicate": f"ACTION_LVL_{d}",
                "roles": {":ARG0": arg0, ":ARG1": arg1},
                "sub_event": sub_id,
                "negated": False,
            })
            expected_bindings_multi.append({"event": eid, "role": ":ARG0", "expected_filler": arg0})
            expected_bindings_multi.append({"event": eid, "role": ":ARG1", "expected_filler": arg1})

        # Deep traversal path to lowest level ARG1
        deep_path = [":sub-event"] * (depth - 1) + [":ARG1"]
        expected_paths_multi.append({
            "start": f"e_multi_d{depth}_lvl1",
            "path": deep_path,
            "expected_terminal": "ent_book",
        })

        corpus["scenarios"].append({
            "id": f"SCEN_{scenario_id:03d}",
            "depth": depth,
            "suite": "nested_with_role_binding",
            "description": f"Nested chain with rich multi-role fillers at depth {depth}",
            "root_event": f"e_multi_d{depth}_lvl1",
            "independent_assertion": {
                "id": "e_indep_03",
                "predicate": "PREFERS",
                "roles": {":ARG0": "ent_user", ":ARG1": "ent_book"},
                "negated": False,
            },
            "events": events_multi,
            "expected_bindings": expected_bindings_multi,
            "expected_paths": expected_paths_multi,
            "expected_scopes": [
                {"event": e["id"], "negated": False, "modal_scope": None}
                for e in events_multi
            ],
        })
        scenario_id += 1

        # ── 4. Negated Proposition ──────────────────────────────────────────────
        events_neg = [
            {
                "id": f"e_neg_d{depth}_01",
                "predicate": "COMPLETED_01",
                "roles": {":ARG0": "ent_user", ":ARG1": "ent_task"},
                "sub_event": None,
                "negated": True,
            }
        ]
        corpus["scenarios"].append({
            "id": f"SCEN_{scenario_id:03d}",
            "depth": depth,
            "suite": "negated_proposition",
            "description": f"Directly negated event frame at depth {depth}",
            "root_event": f"e_neg_d{depth}_01",
            "independent_assertion": {
                "id": "e_indep_04",
                "predicate": "ONLINE_STATUS",
                "roles": {":ARG0": "ent_lucia", ":ARG1": "ent_home"},
                "negated": False,
            },
            "events": events_neg,
            "expected_bindings": [
                {"event": f"e_neg_d{depth}_01", "role": ":ARG0", "expected_filler": "ent_user"},
                {"event": f"e_neg_d{depth}_01", "role": ":ARG1", "expected_filler": "ent_task"},
            ],
            "expected_paths": [
                {"start": f"e_neg_d{depth}_01", "path": [":ARG0"], "expected_terminal": "ent_user"},
            ],
            "expected_scopes": [
                {"event": f"e_neg_d{depth}_01", "negated": True, "modal_scope": None}
            ],
        })
        scenario_id += 1

        # ── 5. Nested Negation / Scope ──────────────────────────────────────────
        # E.g. A believes that B did NOT complete C
        # Level 1 is affirmative; Level depth is negated
        events_scope = []
        expected_scopes = []
        for d in range(1, depth + 1):
            eid = f"e_scope_d{depth}_lvl{d}"
            sub_id = f"e_scope_d{depth}_lvl{d+1}" if d < depth else None
            # Negate innermost or middle level depending on depth
            is_neg = (d == depth)  # innermost is negated
            events_scope.append({
                "id": eid,
                "predicate": "BELIEVE_01" if d < depth else "RESOLVE_01",
                "roles": {":ARG0": "ent_lucia" if d == 1 else "ent_user", ":ARG1": "ent_task"},
                "sub_event": sub_id,
                "negated": is_neg,
            })
            expected_scopes.append({"event": eid, "negated": is_neg, "modal_scope": sub_id})

        corpus["scenarios"].append({
            "id": f"SCEN_{scenario_id:03d}",
            "depth": depth,
            "suite": "nested_negation_scope",
            "description": f"Nested proposition where innermost clause is negated at depth {depth}",
            "root_event": f"e_scope_d{depth}_lvl1",
            "independent_assertion": {
                "id": "e_indep_05",
                "predicate": "TRUST_01",
                "roles": {":ARG0": "ent_lucia", ":ARG1": "ent_user"},
                "negated": False,
            },
            "events": events_scope,
            "expected_bindings": [
                {"event": e["id"], "role": ":ARG0", "expected_filler": e["roles"][":ARG0"]}
                for e in events_scope
            ],
            "expected_paths": [
                {"start": f"e_scope_d{depth}_lvl1", "path": [":sub-event"] * (depth - 1) + [":ARG0"], "expected_terminal": "ent_user" if depth > 1 else "ent_lucia"}
            ],
            "expected_scopes": expected_scopes,
        })
        scenario_id += 1

        # ── 6. Adversarial Role Swap & Repeated Entities ────────────────────────
        # Pair 1: A acts on B in recursive context
        # Pair 2: B acts on A in recursive context
        # Repeated entity: A appears at depth 1 as ARG0 and at depth 2 as ARG1
        events_adv = []
        # Level 1: USER believes Level 2
        # Level 2: LUCIA helps USER (USER is ARG1 here!)
        events_adv.append({
            "id": f"e_adv_d{depth}_lvl1",
            "predicate": "BELIEVE_01",
            "roles": {":ARG0": "ent_user", ":ARG1": "ent_task"},
            "sub_event": f"e_adv_d{depth}_lvl2" if depth > 1 else None,
            "negated": False,
        })
        if depth >= 2:
            events_adv.append({
                "id": f"e_adv_d{depth}_lvl2",
                "predicate": "HELP_01",
                "roles": {":ARG0": "ent_lucia", ":ARG1": "ent_user"},  # Inverted role: user is ARG1
                "sub_event": f"e_adv_d{depth}_lvl3" if depth > 2 else None,
                "negated": False,
            })
        if depth >= 3:
            events_adv.append({
                "id": f"e_adv_d{depth}_lvl3",
                "predicate": "OBSERVE_01",
                "roles": {":ARG0": "ent_admin", ":ARG1": "ent_lucia"},
                "sub_event": f"e_adv_d{depth}_lvl4" if depth > 3 else None,
                "negated": False,
            })
        if depth >= 4:
            events_adv.append({
                "id": f"e_adv_d{depth}_lvl4",
                "predicate": "RECORD_01",
                "roles": {":ARG0": "ent_agent_c", ":ARG1": "ent_admin"},
                "sub_event": None,
                "negated": False,
            })

        expected_adv_bindings = []
        for e in events_adv:
            for r, filler in e["roles"].items():
                expected_adv_bindings.append({"event": e["id"], "role": r, "expected_filler": filler})

        corpus["scenarios"].append({
            "id": f"SCEN_{scenario_id:03d}",
            "depth": depth,
            "suite": "adversarial_role_swap",
            "description": f"Adversarial repeated entity with role reversal across recursion at depth {depth}",
            "root_event": f"e_adv_d{depth}_lvl1",
            "independent_assertion": {
                "id": "e_indep_06",
                "predicate": "MAINTAINS_BOND",
                "roles": {":ARG0": "ent_lucia", ":ARG1": "ent_user"},
                "negated": False,
            },
            "events": events_adv,
            "expected_bindings": expected_adv_bindings,
            "expected_paths": [
                {"start": f"e_adv_d{depth}_lvl1", "path": [":ARG0"], "expected_terminal": "ent_user"},
                *([{"start": f"e_adv_d{depth}_lvl1", "path": [":sub-event", ":ARG0"], "expected_terminal": "ent_lucia"},
                   {"start": f"e_adv_d{depth}_lvl1", "path": [":sub-event", ":ARG1"], "expected_terminal": "ent_user"}] if depth >= 2 else []),
            ],
            "expected_scopes": [
                {"event": e["id"], "negated": False, "modal_scope": e["sub_event"]}
                for e in events_adv
            ],
        })
        scenario_id += 1

    return corpus


def save_corpus(corpus: Dict[str, Any], filepath: str) -> None:
    """Saves generated corpus to JSON format."""
    os.makedirs(os.path.dirname(filepath), exist_ok=True)
    with open(filepath, "w", encoding="utf-8") as f:
        json.dump(corpus, f, indent=2)


if __name__ == "__main__":
    out_path = os.path.join(os.path.dirname(__file__), "corpus.json")
    data = generate_corpus(seed=42)
    save_corpus(data, out_path)
    print(f"Generated {len(data['scenarios'])} scenarios in {out_path}")
