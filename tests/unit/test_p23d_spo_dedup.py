"""
tests/unit/test_p23d_spo_dedup.py

Unit test suite for Phase 23-D referent adapter and KnowledgeStore deduplication.
Verifies TEST-P23D-ADPT-001, TEST-P23D-DEDUP-001, and TEST-P23D-DEDUP-002.

Authoritative Reference:
- docs/others/p23d_endogenous_cognition/P23D_IMPLEMENTATION_SPEC_V1.md §10.1
"""

import pytest

from src.core.cognition.referent_adapter import decode_referent_key, encode_referent_key
from src.core.knowledge.derivation import DerivationEngine
from src.core.knowledge.store import (
    Concept,
    InferenceRule,
    KnowledgeStore,
    Proposition,
    ProvenanceType,
)


class TestP23DSPODedup:
    def test_adpt_001_collision_resistance_with_delimiters(self):
        """
        TEST-P23D-ADPT-001: Collision resistance with colon-containing tokens.
        Referent tokens containing ':' (e.g. 'c:has_color', 'ent:lucia') encode into
        compact JSON tuple; decoded tokens match originals 100%.
        """
        scope = "scope:session:42"
        subject = "ent:lucia:v1"
        predicate = "c:has_preference:aesthetic"
        object_ = "val:calm:blue"

        # Encode
        encoded = encode_referent_key(scope, subject, predicate, object_)
        assert isinstance(encoded, str)
        # Should not use naive delimiter concatenation like scope:subject:predicate:object
        assert encoded.startswith("[") and encoded.endswith("]")

        # Decode
        dec_scope, dec_subj, dec_pred, dec_obj = decode_referent_key(encoded)
        assert dec_scope == scope
        assert dec_subj == subject
        assert dec_pred == predicate
        assert dec_obj == object_

        # Unicode preservation
        u_subj = "ent:ユーザー:01"
        u_pred = "c:好む"
        u_obj = "val:静寂"
        u_encoded = encode_referent_key("scope:root", u_subj, u_pred, u_obj)
        u_scope, u_s, u_p, u_o = decode_referent_key(u_encoded)
        assert u_s == u_subj
        assert u_p == u_pred
        assert u_o == u_obj

    def test_dedup_001_idempotent_proposition_deduplication(self):
        """
        TEST-P23D-DEDUP-001: Idempotent proposition deduplication.
        Storing identical (S, P, O) twice returns the original prop.id.
        len(_propositions) does not increment.
        """
        store = KnowledgeStore()
        prop1 = Proposition(
            id="prop:001",
            subject="ent:lucia",
            predicate="c:is_autonomous",
            object="false",
            confidence=1.0,
            provenance=ProvenanceType.VERIFIED,
        )

        id1 = store.store_proposition(prop1)
        assert id1 == "prop:001"
        assert len(store._propositions) == 1

        # Attempt to store identical proposition under a different proposed ID
        prop2 = Proposition(
            id="prop:002_duplicate",
            subject=" ent:lucia ",  # with whitespace
            predicate="C:IS_AUTONOMOUS",  # uppercase
            object="false",
            confidence=0.9,
            provenance=ProvenanceType.DERIVED,
        )

        id2 = store.store_proposition(prop2)
        # Must return existing prop_id without incrementing proposition count
        assert id2 == "prop:001"
        assert len(store._propositions) == 1
        assert store.get_proposition("prop:001") is not None
        assert store.get_proposition("prop:002_duplicate") is None

        # Verify serialization and deserialization retains _spo_index
        serialized = store.to_json()
        restored = KnowledgeStore.from_json(serialized)
        assert len(restored._propositions) == 1
        assert len(restored._spo_index) == 1

        # Storing again in restored store should also deduplicate
        id3 = restored.store_proposition(prop2)
        assert id3 == "prop:001"
        assert len(restored._propositions) == 1

    def test_dedup_002_deterministic_transitive_derivation(self):
        """
        TEST-P23D-DEDUP-002: Deterministic transitive derivation.
        Re-running transitive derivation produces identical 'derived:' IDs;
        zero duplicate propositions created in KnowledgeStore.
        """
        store = KnowledgeStore()

        # Define taxonomy: Socrates is a Human, Human is Mortal
        store.store_proposition(Proposition(
            id="prop:socrates_human",
            subject="ent:socrates",
            predicate="c:is_a",
            object="ent:human",
            confidence=1.0,
            provenance=ProvenanceType.OBSERVED,
        ))
        store.store_proposition(Proposition(
            id="prop:human_mortal",
            subject="ent:human",
            predicate="c:is_a",
            object="ent:mortal",
            confidence=1.0,
            provenance=ProvenanceType.VERIFIED,
        ))

        engine = DerivationEngine(max_depth=3)

        # First derivation run
        derived_1 = engine.apply_transitive_relations(store, "c:is_a")
        assert len(derived_1) == 1
        derived_prop_1 = derived_1[0]
        assert derived_prop_1.subject == "ent:socrates"
        assert derived_prop_1.predicate == "c:is_a"
        assert derived_prop_1.object == "ent:mortal"
        assert derived_prop_1.id.startswith("derived:")

        initial_count = len(store._propositions)

        # Second derivation run: must produce bit-exact proposition ID and zero duplicates
        derived_2 = engine.apply_transitive_relations(store, "c:is_a")
        assert len(derived_2) == 0  # Deduplication stops identical derived proposition from re-adding

        # Proposition count in KnowledgeStore must not have incremented
        assert len(store._propositions) == initial_count
