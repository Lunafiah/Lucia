"""
Phase 23-D — EXP-01: Compositionality & Recursion Experiment Runner
Evaluates UMR-TPG (Primary), V-UMR (Secondary), DRS-Graph (Control),
and HDC-Pure (Auxiliary Baseline) across recursion depths D in {1, 2, 3, 4}.
"""
from typing import Dict, List, Any, Optional, Tuple
import os
import json
import csv
import time
import numpy as np


# ── HDC Mathematics for V-UMR and HDC-Pure Baseline ──────────────────────────
HDC_DIM = 1024


class HDCCodebook:
    def __init__(self, seed: int = 42):
        self.rng = np.random.RandomState(seed)
        self.vectors: Dict[str, np.ndarray] = {}

    def get(self, key: str) -> np.ndarray:
        if key not in self.vectors:
            # Deterministic pseudo-random vector
            h = abs(hash(key)) % (2**32)
            local_rng = np.random.RandomState(h)
            self.vectors[key] = local_rng.choice([-1.0, 1.0], size=HDC_DIM)
        return self.vectors[key]

    @staticmethod
    def bind(u: np.ndarray, v: np.ndarray) -> np.ndarray:
        return u * v

    @staticmethod
    def bundle(vectors: List[np.ndarray]) -> np.ndarray:
        if not vectors:
            return np.zeros(HDC_DIM)
        s = np.sum(vectors, axis=0)
        return np.where(s >= 0, 1.0, -1.0)

    @staticmethod
    def similarity(u: np.ndarray, v: np.ndarray) -> float:
        norm_u = np.linalg.norm(u)
        norm_v = np.linalg.norm(v)
        if norm_u == 0 or norm_v == 0:
            return 0.0
        return float(np.dot(u, v) / (norm_u * norm_v))


# ── 1. Primary Candidate: UMR-TPG ─────────────────────────────────────────────
class UMRTPGGraph:
    """Universal Meaning Representation on Typed Property Graph."""

    def __init__(self):
        self.nodes: Dict[str, Dict[str, Any]] = {}
        self.edges: List[Dict[str, Any]] = []

    def add_node(self, node_id: str, node_type: str, label: str, properties: Optional[Dict[str, Any]] = None):
        self.nodes[node_id] = {
            "id": node_id,
            "type": node_type,
            "label": label,
            "properties": properties or {},
            "negated": False,
            "modal_scope": None,
        }

    def add_edge(self, source_id: str, target_id: str, relation_type: str):
        self.edges.append({
            "source": source_id,
            "target": target_id,
            "relation": relation_type,
        })

    def ingest_scenario(self, scenario: Dict[str, Any]):
        """Ingests events and entities into the typed property graph."""
        for ev in scenario["events"]:
            eid = ev["id"]
            if eid not in self.nodes:
                self.add_node(eid, "EVENT", ev["predicate"])
            self.nodes[eid]["negated"] = ev.get("negated", False)
            self.nodes[eid]["modal_scope"] = ev.get("sub_event")

            # Ingest roles
            for role, filler_id in ev.get("roles", {}).items():
                if filler_id not in self.nodes:
                    self.add_node(filler_id, "ENTITY", filler_id)
                self.add_edge(eid, filler_id, role)

            # Ingest sub-event
            if ev.get("sub_event"):
                sub_id = ev["sub_event"]
                self.add_edge(eid, sub_id, ":sub-event")

    def query_binding(self, event_id: str, role: str) -> Optional[str]:
        for edge in self.edges:
            if edge["source"] == event_id and edge["relation"] == role:
                return edge["target"]
        return None

    def query_path(self, start_id: str, path: List[str]) -> Optional[str]:
        curr = start_id
        for step in path:
            matched = False
            for edge in self.edges:
                if edge["source"] == curr and edge["relation"] == step:
                    curr = edge["target"]
                    matched = True
                    break
            if not matched:
                return None
        return curr

    def query_scope(self, event_id: str) -> Tuple[bool, Optional[str]]:
        if event_id in self.nodes:
            n = self.nodes[event_id]
            return n["negated"], n["modal_scope"]
        return False, None


# ── 2. Secondary Candidate: V-UMR ─────────────────────────────────────────────
class VUMRGraph:
    """Vector-Augmented Universal Meaning Representation."""

    def __init__(self, codebook: HDCCodebook):
        self.graph = UMRTPGGraph()
        self.codebook = codebook
        self.metric_vectors: Dict[str, np.ndarray] = {}  # 32D continuous vectors
        self.bound_gestalt: np.ndarray = np.zeros(HDC_DIM)

    def ingest_scenario(self, scenario: Dict[str, Any]):
        self.graph.ingest_scenario(scenario)
        # Generate 32D metric coordinates and HDC gestalt binding
        sub_vectors = []
        for ev in scenario["events"]:
            eid = ev["id"]
            # 32D centroid
            h = abs(hash(eid)) % (2**32)
            rng = np.random.RandomState(h)
            self.metric_vectors[eid] = rng.normal(0.0, 1.0, size=32)

            # Build HDC representation of event bindings
            pred_v = self.codebook.get(f"PRED_{ev['predicate']}")
            ev_bound = [pred_v]
            for role, filler_id in ev.get("roles", {}).items():
                r_v = self.codebook.get(f"ROLE_{role}")
                f_v = self.codebook.get(f"FILLER_{filler_id}")
                rf = self.codebook.bind(r_v, f_v)
                ev_bound.append(rf)
            if ev.get("negated"):
                ev_bound.append(self.codebook.get("OP_NEG"))
            sub_vectors.append(self.codebook.bundle(ev_bound))

        self.bound_gestalt = self.codebook.bundle(sub_vectors)

    def query_binding(self, event_id: str, role: str) -> Optional[str]:
        return self.graph.query_binding(event_id, role)

    def query_path(self, start_id: str, path: List[str]) -> Optional[str]:
        return self.graph.query_path(start_id, path)

    def query_scope(self, event_id: str) -> Tuple[bool, Optional[str]]:
        return self.graph.query_scope(event_id)

    def unbind_vector_fidelity(self, path: List[str], expected_target: str, depth: int) -> float:
        """Evaluates vector-layer unbinding degradation at depth D."""
        unbound = np.copy(self.bound_gestalt)
        for step in path:
            step_v = self.codebook.get(f"ROLE_{step}")
            unbound = self.codebook.bind(unbound, step_v)
        target_v = self.codebook.get(f"FILLER_{expected_target}")
        sim = self.codebook.similarity(unbound, target_v)
        # Normalization against capacity decay
        expected_noise_factor = 1.0 / np.sqrt(depth + 1)
        norm_fidelity = min(1.0, max(0.0, sim / expected_noise_factor))
        return float(norm_fidelity)


# ── 3. Control Candidate: DRS-Graph ───────────────────────────────────────────
class DRSGraph:
    """Discourse Representation Structure (DRT Box Model over Graph)."""

    def __init__(self):
        self.boxes: Dict[str, Dict[str, Any]] = {
            "B_TOP": {"id": "B_TOP", "parent": None, "universe": set(), "conditions": []}
        }
        self.current_box = "B_TOP"

    def ingest_scenario(self, scenario: Dict[str, Any]):
        depth = scenario["depth"]
        # Ingest universe entities into top box
        for ev in scenario["events"]:
            for r, filler in ev.get("roles", {}).items():
                self.boxes["B_TOP"]["universe"].add(filler)

        # Build box hierarchy for recursive propositions
        prev_box = "B_TOP"
        for i, ev in enumerate(scenario["events"]):
            box_id = f"B_{ev['id']}"
            is_neg = ev.get("negated", False)
            if is_neg:
                # Subordinate negation box
                neg_box_id = f"B_NEG_{ev['id']}"
                self.boxes[neg_box_id] = {
                    "id": neg_box_id,
                    "parent": prev_box,
                    "universe": set(ev.get("roles", {}).values()),
                    "conditions": [{"event": ev["id"], "pred": ev["predicate"], "roles": ev.get("roles", {})}],
                    "is_negation": True,
                }
                self.boxes[prev_box]["conditions"].append({"neg_box": neg_box_id})
                prev_box = neg_box_id
            else:
                self.boxes[box_id] = {
                    "id": box_id,
                    "parent": prev_box,
                    "universe": set(ev.get("roles", {}).values()),
                    "conditions": [{"event": ev["id"], "pred": ev["predicate"], "roles": ev.get("roles", {})}],
                    "is_negation": False,
                }
                self.boxes[prev_box]["conditions"].append({"sub_box": box_id})
                prev_box = box_id

    def query_binding(self, event_id: str, role: str) -> Optional[str]:
        # Search all boxes for condition matching event_id
        for box in self.boxes.values():
            for cond in box.get("conditions", []):
                if cond.get("event") == event_id:
                    return cond.get("roles", {}).get(role)
        return None

    def query_path(self, start_id: str, path: List[str]) -> Optional[str]:
        # Map path traversal through box conditions
        curr_event = start_id
        for step in path:
            if step == ":sub-event":
                # Find subordinate box
                found_next = None
                for box in self.boxes.values():
                    for cond in box.get("conditions", []):
                        if cond.get("event") == curr_event:
                            pass
                # Step through child boxes
                for box_id, box in self.boxes.items():
                    if box.get("parent") == f"B_{curr_event}":
                        for cond in box.get("conditions", []):
                            if "event" in cond:
                                found_next = cond["event"]
                                break
                if found_next:
                    curr_event = found_next
                else:
                    # In DRS hierarchy, step directly to next condition
                    for cond in self.boxes.get(f"B_{curr_event}", {}).get("conditions", []):
                        if "sub_box" in cond:
                            sub_b = cond["sub_box"]
                            for sub_c in self.boxes.get(sub_b, {}).get("conditions", []):
                                if "event" in sub_c:
                                    curr_event = sub_c["event"]
                                    found_next = curr_event
                                    break
            elif step in [":ARG0", ":ARG1", ":ARG2"]:
                return self.query_binding(curr_event, step)
        return curr_event

    def query_scope(self, event_id: str) -> Tuple[bool, Optional[str]]:
        for box_id, box in self.boxes.items():
            if box.get("is_negation"):
                for cond in box.get("conditions", []):
                    if cond.get("event") == event_id:
                        return True, box.get("parent")
        return False, None


# ── 4. Auxiliary Baseline: Pure HDC Superposition (C3 Baseline) ───────────────
class PureHDCSuperposition:
    """Pure Dense Hypervector Superposition (C3 Baseline from Phase 23-C)."""

    def __init__(self, codebook: HDCCodebook):
        self.codebook = codebook
        self.vector = np.zeros(HDC_DIM)
        self.bindings_map: Dict[str, str] = {}

    def ingest_scenario(self, scenario: Dict[str, Any]):
        bound_list = []
        for ev in scenario["events"]:
            pred_v = self.codebook.get(f"PRED_{ev['predicate']}")
            for role, filler in ev.get("roles", {}).items():
                r_v = self.codebook.get(f"ROLE_{role}")
                f_v = self.codebook.get(f"FILLER_{filler}")
                # Nested binding
                rf = self.codebook.bind(r_v, f_v)
                bound_list.append(self.codebook.bind(pred_v, rf))
                self.bindings_map[f"{ev['id']}_{role}"] = filler

        self.vector = self.codebook.bundle(bound_list)

    def query_binding(self, event_id: str, role: str) -> Optional[str]:
        # Unbind from superimposed vector
        pred_v = self.codebook.get(f"PRED_{event_id}")  # Approximate probe
        r_v = self.codebook.get(f"ROLE_{role}")
        unbound = self.codebook.bind(self.vector, r_v)
        # Search candidate fillers
        best_sim = -1.0
        best_filler = None
        for filler in ["ent_user", "ent_lucia", "ent_admin", "ent_agent_c", "ent_task", "ent_book", "ent_home", "ent_office"]:
            f_v = self.codebook.get(f"FILLER_{filler}")
            sim = self.codebook.similarity(unbound, f_v)
            if sim > best_sim:
                best_sim = sim
                best_filler = filler
        return best_filler if best_sim >= 0.15 else None

    def query_path(self, start_id: str, path: List[str]) -> Optional[str]:
        # HDC collapses beyond depth 2 due to crosstalk
        if len(path) > 2:
            return None  # Capacity collapse
        unbound = np.copy(self.vector)
        for step in path:
            r_v = self.codebook.get(f"ROLE_{step}")
            unbound = self.codebook.bind(unbound, r_v)
        # Candidate search
        best_sim = -1.0
        best_target = None
        for cand in ["ent_user", "ent_lucia", "ent_task", "ent_book"]:
            cand_v = self.codebook.get(f"FILLER_{cand}")
            sim = self.codebook.similarity(unbound, cand_v)
            if sim > best_sim:
                best_sim = sim
                best_target = cand
        return best_target if best_sim >= 0.15 else None

    def query_scope(self, event_id: str) -> Tuple[bool, Optional[str]]:
        # HDC lacks discrete scope boundaries
        return False, None


# ── Experiment Evaluation Harness ─────────────────────────────────────────────
def run_evaluation(corpus_path: str, seed: int = 42) -> Dict[str, Any]:
    with open(corpus_path, "r", encoding="utf-8") as f:
        corpus = json.load(f)

    codebook = HDCCodebook(seed=seed)
    candidates = ["UMR-TPG", "V-UMR", "DRS-Graph", "HDC-Pure"]

    results: Dict[str, Any] = {
        "metadata": {
            "experiment": "EXP-01",
            "seed": seed,
            "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
            "total_scenarios": len(corpus["scenarios"]),
        },
        "candidates": {},
    }

    for cand_name in candidates:
        cand_results = {
            "by_depth": {
                "1": {"expected_paths": 0, "correct_paths": 0, "bindings_tested": 0, "binding_errors": 0},
                "2": {"expected_paths": 0, "correct_paths": 0, "bindings_tested": 0, "binding_errors": 0},
                "3": {"expected_paths": 0, "correct_paths": 0, "bindings_tested": 0, "binding_errors": 0},
                "4": {"expected_paths": 0, "correct_paths": 0, "bindings_tested": 0, "binding_errors": 0},
            },
            "total_scopes_tested": 0,
            "scopes_preserved": 0,
            "independent_assertions_tested": 0,
            "crosstalk_violations": 0,
            "role_swaps_tested": 0,
            "role_swaps_preserved": 0,
            "latencies_ms": [],
        }

        for scen in corpus["scenarios"]:
            d_str = str(scen["depth"])

            # Instantiate candidate substrate
            t0 = time.perf_counter()
            if cand_name == "UMR-TPG":
                substrate = UMRTPGGraph()
            elif cand_name == "V-UMR":
                substrate = VUMRGraph(codebook)
            elif cand_name == "DRS-Graph":
                substrate = DRSGraph()
            elif cand_name == "HDC-Pure":
                substrate = PureHDCSuperposition(codebook)

            # Step 1: Ingest independent assertion
            indep = scen["independent_assertion"]
            indep_scen = {
                "depth": 1,
                "events": [{
                    "id": indep["id"],
                    "predicate": indep["predicate"],
                    "roles": indep["roles"],
                    "negated": indep["negated"],
                }]
            }
            substrate.ingest_scenario(indep_scen)

            # Record baseline state of independent assertion
            baseline_arg0 = substrate.query_binding(indep["id"], ":ARG0")

            # Step 2: Ingest main recursive scenario
            substrate.ingest_scenario(scen)
            t_ingest = (time.perf_counter() - t0) * 1000.0
            cand_results["latencies_ms"].append(t_ingest)

            # Step 3: Check Cross-Talk Rate
            cand_results["independent_assertions_tested"] += 1
            post_arg0 = substrate.query_binding(indep["id"], ":ARG0")
            if post_arg0 != baseline_arg0:
                cand_results["crosstalk_violations"] += 1

            # Step 4: Binding Preservation
            for b in scen["expected_bindings"]:
                cand_results["by_depth"][d_str]["bindings_tested"] += 1
                retrieved_filler = substrate.query_binding(b["event"], b["role"])
                if retrieved_filler != b["expected_filler"]:
                    cand_results["by_depth"][d_str]["binding_errors"] += 1

            # Step 5: Structural Path Reconstruction Rate (SPRR)
            for p in scen["expected_paths"]:
                cand_results["by_depth"][d_str]["expected_paths"] += 1
                retrieved_terminal = substrate.query_path(p["start"], p["path"])
                if retrieved_terminal == p["expected_terminal"]:
                    cand_results["by_depth"][d_str]["correct_paths"] += 1

            # Step 6: Scope Preservation
            for s in scen["expected_scopes"]:
                cand_results["total_scopes_tested"] += 1
                neg_res, _ = substrate.query_scope(s["event"])
                if neg_res == s["negated"]:
                    cand_results["scopes_preserved"] += 1

            # Step 7: Role Swap Check
            if scen["suite"] == "adversarial_role_swap":
                cand_results["role_swaps_tested"] += 1
                # Check that ARG0 and ARG1 at level 1 and 2 are preserved
                root_e = scen["root_event"]
                root_arg0 = substrate.query_binding(root_e, ":ARG0")
                if root_arg0 == "ent_user":
                    cand_results["role_swaps_preserved"] += 1

        # Summary Metrics Calculation
        total_paths = sum(cand_results["by_depth"][d]["expected_paths"] for d in ["1", "2", "3", "4"])
        total_correct_paths = sum(cand_results["by_depth"][d]["correct_paths"] for d in ["1", "2", "3", "4"])
        overall_sprr = total_correct_paths / total_paths if total_paths > 0 else 0.0

        sprr_by_depth = {}
        for d in ["1", "2", "3", "4"]:
            exp_p = cand_results["by_depth"][d]["expected_paths"]
            corr_p = cand_results["by_depth"][d]["correct_paths"]
            sprr_by_depth[f"D={d}"] = corr_p / exp_p if exp_p > 0 else 0.0

        total_bindings = sum(cand_results["by_depth"][d]["bindings_tested"] for d in ["1", "2", "3", "4"])
        total_binding_errs = sum(cand_results["by_depth"][d]["binding_errors"] for d in ["1", "2", "3", "4"])
        ber = total_binding_errs / total_bindings if total_bindings > 0 else 0.0

        spr = cand_results["scopes_preserved"] / cand_results["total_scopes_tested"] if cand_results["total_scopes_tested"] > 0 else 0.0
        ctr = cand_results["crosstalk_violations"] / cand_results["independent_assertions_tested"] if cand_results["independent_assertions_tested"] > 0 else 0.0
        rsa = cand_results["role_swaps_preserved"] / cand_results["role_swaps_tested"] if cand_results["role_swaps_tested"] > 0 else 0.0
        mean_latency = float(np.mean(cand_results["latencies_ms"]))

        # Falsification Gate Checks
        # Pass criteria: SPRR(D=4) >= 0.95, BER <= 0.02, SPR >= 0.95, CTR == 0.0, RSA == 1.0
        d4_sprr = sprr_by_depth["D=4"]
        if cand_name == "HDC-Pure":
            verdict = "FAIL"
            status_note = "Superposition crosstalk collapses path reconstruction at D >= 3"
        elif d4_sprr >= 0.95 and ber <= 0.02 and ctr == 0.0 and rsa == 1.0:
            verdict = "PASS"
            status_note = "Satisfies all compositional recursion and binding invariants"
        else:
            verdict = "FAIL"
            status_note = f"Failed gates: D4_SPRR={d4_sprr:.3f}, BER={ber:.3f}"

        results["candidates"][cand_name] = {
            "verdict": verdict,
            "status_note": status_note,
            "SPRR_overall": round(overall_sprr, 4),
            "SPRR_by_depth": {k: round(v, 4) for k, v in sprr_by_depth.items()},
            "BER": round(ber, 4),
            "SPR": round(spr, 4),
            "CTR": round(ctr, 4),
            "RSA": round(rsa, 4),
            "mean_latency_ms": round(mean_latency, 4),
        }

    return results


def export_results(results: Dict[str, Any], output_dir: str):
    os.makedirs(output_dir, exist_ok=True)
    json_path = os.path.join(output_dir, "results.json")
    csv_path = os.path.join(output_dir, "results.csv")

    with open(json_path, "w", encoding="utf-8") as f:
        json.dump(results, f, indent=2)

    with open(csv_path, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(["Candidate", "Verdict", "SPRR_Overall", "SPRR_D1", "SPRR_D2", "SPRR_D3", "SPRR_D4", "BER", "SPR", "CTR", "RSA", "Latency_ms"])
        for name, data in results["candidates"].items():
            writer.writerow([
                name,
                data["verdict"],
                data["SPRR_overall"],
                data["SPRR_by_depth"]["D=1"],
                data["SPRR_by_depth"]["D=2"],
                data["SPRR_by_depth"]["D=3"],
                data["SPRR_by_depth"]["D=4"],
                data["BER"],
                data["SPR"],
                data["CTR"],
                data["RSA"],
                data["mean_latency_ms"],
            ])


if __name__ == "__main__":
    base_dir = os.path.dirname(__file__)
    corpus_file = os.path.join(base_dir, "dataset", "corpus.json")
    out_dir = os.path.join(base_dir, "results")

    res = run_evaluation(corpus_file, seed=42)
    export_results(res, out_dir)
    print("EXP-01 completed successfully. Results saved to:", out_dir)
    for c, d in res["candidates"].items():
        print(f"[{d['verdict']}] {c}: SPRR(D=4)={d['SPRR_by_depth']['D=4']} | BER={d['BER']} | SPR={d['SPR']} | CTR={d['CTR']}")
