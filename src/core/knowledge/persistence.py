"""
src/core/knowledge/persistence.py

Atomic JSON serialization and persistence for the Knowledge Subsystem.
Ensures crash-resilient disk writes and isolated test storage support.
"""

from __future__ import annotations

import json
import logging
import os
import tempfile
from pathlib import Path
from typing import Optional, Union

from src.core.knowledge.proposition import Concept, InferenceRule, Proposition, ProvenanceType
from src.core.knowledge.store import KnowledgeStore

logger = logging.getLogger(__name__)

DEFAULT_KNOWLEDGE_PATH = Path("data/knowledge.json")


def save_knowledge(
    store: KnowledgeStore,
    filepath: Optional[Union[str, Path]] = None,
) -> Path:
    """
    Atomically persist KnowledgeStore to disk via temporary file rename.
    Guarantees no half-written JSON files on crash or interruption.
    """
    target = Path(filepath) if filepath else DEFAULT_KNOWLEDGE_PATH
    target.parent.mkdir(parents=True, exist_ok=True)

    data = {
        "version": "1.0",
        "propositions": [p.to_dict() for p in store.get_all_propositions()],
        "concepts": [c.to_dict() for c in store.get_all_concepts()],
        "rules": [
            {
                "id": r.id,
                "name": r.name,
                "domain": r.domain,
                "antecedents": r.antecedents,
                "consequent_pattern": r.consequent_pattern,
                "confidence_decay": r.confidence_decay,
            }
            for r in store.get_all_rules()
        ],
        "revision_history": store.get_revision_history(),
    }

    # Write atomically using a temporary file in the same directory
    temp_fd, temp_path = tempfile.mkstemp(
        dir=str(target.parent),
        prefix="knowledge_",
        suffix=".tmp",
    )
    try:
        with os.fdopen(temp_fd, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
        # Atomic replace
        os.replace(temp_path, target)
        logger.debug("Successfully saved KnowledgeStore to %s", target)
    except Exception as e:
        if os.path.exists(temp_path):
            try:
                os.remove(temp_path)
            except OSError:
                pass
        logger.error("Failed to save KnowledgeStore to %s: %s", target, e)
        raise

    return target


def load_knowledge(
    filepath: Optional[Union[str, Path]] = None,
) -> KnowledgeStore:
    """
    Load KnowledgeStore from disk. If the file does not exist, return an empty store.
    """
    target = Path(filepath) if filepath else DEFAULT_KNOWLEDGE_PATH
    store = KnowledgeStore()

    if not target.exists():
        logger.info("Knowledge file %s does not exist; initializing empty store.", target)
        return store

    try:
        with open(target, "r", encoding="utf-8") as f:
            data = json.load(f)

        for p_dict in data.get("propositions", []):
            prop = Proposition.from_dict(p_dict)
            store.store_proposition(prop)

        for c_dict in data.get("concepts", []):
            concept = Concept.from_dict(c_dict)
            store.store_concept(concept)

        for r_dict in data.get("rules", []):
            rule = InferenceRule(
                id=r_dict["id"],
                name=r_dict["name"],
                domain=r_dict["domain"],
                antecedents=[tuple(a) for a in r_dict["antecedents"]],
                consequent_pattern=tuple(r_dict["consequent_pattern"]),
                confidence_decay=r_dict.get("confidence_decay", 0.95),
            )
            store.store_rule(rule)

        for rev in data.get("revision_history", []):
            store.append_revision_history(rev)

        logger.info("Loaded KnowledgeStore from %s (%d props, %d concepts, %d rules)",
                    target, len(store.get_all_propositions()), len(store.get_all_concepts()), len(store.get_all_rules()))
    except Exception as e:
        logger.error("Failed to load KnowledgeStore from %s: %s", target, e)
        raise

    return store
