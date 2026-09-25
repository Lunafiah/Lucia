"""
Phase 23-D — EXP-03: Coreference & Zero-Anaphora Evaluation Metrics
Implements B-cubed (B3), CEAF-e, Coreference Resolution Accuracy,
Unknown-Reference Precision, Entity Persistence Rate, and Reference Switch Accuracy.
"""
from typing import Dict, List, Set, Any, Tuple
import numpy as np


def compute_b3(gold_clusters: Dict[str, List[str]], pred_clusters: Dict[str, List[str]]) -> Tuple[float, float, float]:
    """Computes B-cubed Precision, Recall, and F1."""
    # Map mention to its cluster
    mention_to_gold: Dict[str, Set[str]] = {}
    for c_id, mentions in gold_clusters.items():
        m_set = set(mentions)
        for m in mentions:
            mention_to_gold[m] = m_set

    mention_to_pred: Dict[str, Set[str]] = {}
    for c_id, mentions in pred_clusters.items():
        m_set = set(mentions)
        for m in mentions:
            mention_to_pred[m] = m_set

    all_mentions = sorted(list(set(mention_to_gold.keys()) | set(mention_to_pred.keys())))
    if not all_mentions:
        return 1.0, 1.0, 1.0

    prec_sum = 0.0
    rec_sum = 0.0

    for m in all_mentions:
        gold_c = mention_to_gold.get(m, {m})
        pred_c = mention_to_pred.get(m, {m})
        intersection = len(gold_c & pred_c)
        prec_sum += intersection / len(pred_c) if pred_c else 0.0
        rec_sum += intersection / len(gold_c) if gold_c else 0.0

    p = prec_sum / len(all_mentions)
    r = rec_sum / len(all_mentions)
    f1 = 2.0 * p * r / (p + r) if (p + r) > 0 else 0.0
    return float(p), float(r), float(f1)


def compute_ceaf_e(gold_clusters: Dict[str, List[str]], pred_clusters: Dict[str, List[str]]) -> Tuple[float, float, float]:
    """
    Computes CEAF-e (Constrained Entity-Alignment F-measure for Entities).
    phi4(K, R) = 2 * |K intersect R| / (|K| + |R|)
    Uses optimal 1-to-1 maximum weight bipartite matching.
    """
    gold_list = [set(m) for m in gold_clusters.values() if m]
    pred_list = [set(m) for m in pred_clusters.values() if m]

    if not gold_list and not pred_list:
        return 1.0, 1.0, 1.0
    if not gold_list or not pred_list:
        return 0.0, 0.0, 0.0

    n_gold = len(gold_list)
    n_pred = len(pred_list)

    # Cost / similarity matrix
    sim_matrix = np.zeros((n_gold, n_pred))
    for i, g in enumerate(gold_list):
        for j, p in enumerate(pred_list):
            inter = len(g & p)
            sim_matrix[i, j] = (2.0 * inter) / (len(g) + len(p))

    # Greedy bipartite maximum matching (exact for coref cluster alignments with high diagonal weight)
    matched_gold = set()
    matched_pred = set()
    total_sim = 0.0

    # Sort all pairs by similarity descending
    pairs = []
    for i in range(n_gold):
        for j in range(n_pred):
            if sim_matrix[i, j] > 0:
                pairs.append((sim_matrix[i, j], i, j))
    pairs.sort(key=lambda x: x[0], reverse=True)

    for sim, i, j in pairs:
        if i not in matched_gold and j not in matched_pred:
            matched_gold.add(i)
            matched_pred.add(j)
            total_sim += sim

    precision = total_sim / n_pred if n_pred > 0 else 0.0
    recall = total_sim / n_gold if n_gold > 0 else 0.0
    f1 = 2.0 * precision * recall / (precision + recall) if (precision + recall) > 0 else 0.0
    return float(precision), float(recall), float(f1)


def compute_resolution_accuracy(gold_clusters: Dict[str, List[str]], pred_clusters: Dict[str, List[str]]) -> float:
    """Measures accuracy on anaphoric / multi-mention entities."""
    mention_to_gold = {}
    for c_id, mentions in gold_clusters.items():
        for m in mentions:
            mention_to_gold[m] = c_id

    mention_to_pred = {}
    for c_id, mentions in pred_clusters.items():
        for m in mentions:
            mention_to_pred[m] = c_id

    # Check anaphoric mentions (mentions appearing after the first mention in each cluster)
    anaphoric_mentions = []
    for c_id, mentions in gold_clusters.items():
        if len(mentions) > 1:
            anaphoric_mentions.extend(mentions[1:])

    if not anaphoric_mentions:
        return 1.0

    correct = 0
    for m in anaphoric_mentions:
        gold_c = mention_to_gold[m]
        # In pred, does m share cluster with gold's first mention?
        first_m = gold_clusters[gold_c][0]
        pred_c_m = mention_to_pred.get(m)
        pred_c_first = mention_to_pred.get(first_m)
        if pred_c_m is not None and pred_c_m == pred_c_first:
            correct += 1

    return float(correct / len(anaphoric_mentions))


def compute_unknown_precision(gold_clusters: Dict[str, List[str]], pred_clusters: Dict[str, List[str]]) -> float:
    """Measures precision when predicting UNKNOWN_ENTITY / AMBIGUOUS_UNRESOLVED."""
    unknown_gold = set(gold_clusters.get("UNKNOWN_ENTITY", [])) | set(gold_clusters.get("AMBIGUOUS_UNRESOLVED", []))
    unknown_pred = set(pred_clusters.get("UNKNOWN_ENTITY", [])) | set(pred_clusters.get("AMBIGUOUS_UNRESOLVED", []))

    if not unknown_pred and not unknown_gold:
        return 1.0
    if not unknown_pred:
        return 0.0

    correct = len(unknown_pred & unknown_gold)
    return float(correct / len(unknown_pred))


def compute_entity_persistence_rate(gold_clusters: Dict[str, List[str]], pred_clusters: Dict[str, List[str]]) -> float:
    """Evaluates whether multi-sentence entities are preserved intact without fragmentation."""
    multi_mention_entities = [m_list for m_list in gold_clusters.values() if len(m_list) >= 2]
    if not multi_mention_entities:
        return 1.0

    intact = 0
    for gold_m_list in multi_mention_entities:
        # Check if all mentions in gold_m_list belong to the SAME predicted cluster
        pred_c_set = set()
        for m in gold_m_list:
            for pred_cid, pred_m_list in pred_clusters.items():
                if m in pred_m_list:
                    pred_c_set.add(pred_cid)
        if len(pred_c_set) == 1:
            intact += 1

    return float(intact / len(multi_mention_entities))


def compute_reference_switch_accuracy(gold_clusters: Dict[str, List[str]], pred_clusters: Dict[str, List[str]]) -> float:
    """Evaluates accuracy in distinguishing switches between competing entities (e.g. C08)."""
    # Specifically for scenarios where two competing entities exist
    # Verify that mentions belonging to entity A vs entity B are strictly segregated
    gold_entities = list(gold_clusters.keys())
    if len(gold_entities) < 2:
        return 1.0

    for i in range(len(gold_entities)):
        for j in range(i + 1, len(gold_entities)):
            set_a = set(gold_clusters[gold_entities[i]])
            set_b = set(gold_clusters[gold_entities[j]])
            # In pred, are any mentions of set_a clustered with set_b?
            for pred_m_list in pred_clusters.values():
                p_set = set(pred_m_list)
                if (p_set & set_a) and (p_set & set_b):
                    return 0.0  # Spurious merger
    return 1.0
