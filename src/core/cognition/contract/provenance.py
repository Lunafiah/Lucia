"""
src/core/cognition/contract/provenance.py

Phase 23-G: Cognitive Core Provenance Record.

Strict Invariants:
1. Every INFERRED term must contain rule_id, supporting premise references, and provenance.
2. Numeric representation in Core (rule_id: int, supporting_premise_ids: Tuple[int, ...]).
3. Full round-trip fidelity between Cognitive Core ProvenanceRecord and
   P23-E Knowledge ProvenanceRecord.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Dict, Optional, Tuple, TYPE_CHECKING

if TYPE_CHECKING:
    from src.core.knowledge.fortification import ProvenanceRecord as P23EProvenanceRecord
    from src.core.cognition.contract.projection import SymbolTable


@dataclass(frozen=True)
class ProvenanceRecord:
    """
    Language-independent numeric derivation provenance for Cognitive Core terms.
    All rule IDs and premise links are integer identifiers.
    """
    rule_id: int = 0
    supporting_premise_ids: Tuple[int, ...] = ()
    session_id: int = 0
    turn_id: int = 0
    timestamp: float = 0.0
    confidence: float = 1.0
    metadata: Dict[int, int] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "rule_id": self.rule_id,
            "supporting_premise_ids": list(self.supporting_premise_ids),
            "session_id": self.session_id,
            "turn_id": self.turn_id,
            "timestamp": self.timestamp,
            "confidence": self.confidence,
            "metadata": dict(self.metadata),
        }

    @classmethod
    def from_dict(cls, d: Dict[str, Any]) -> ProvenanceRecord:
        return cls(
            rule_id=int(d.get("rule_id", 0)),
            supporting_premise_ids=tuple(int(p) for p in d.get("supporting_premise_ids", ())),
            session_id=int(d.get("session_id", 0)),
            turn_id=int(d.get("turn_id", 0)),
            timestamp=float(d.get("timestamp", 0.0)),
            confidence=float(d.get("confidence", 1.0)),
            metadata={int(k): int(v) for k, v in d.get("metadata", {}).items()},
        )

    def to_p23e_provenance(self, symbol_table: SymbolTable) -> P23EProvenanceRecord:
        """Convert numeric provenance back to P23-E string-based ProvenanceRecord."""
        from src.core.knowledge.fortification import ProvenanceRecord as P23EProvenanceRecord

        rule_symbol = symbol_table.get_rule_symbol(self.rule_id) if self.rule_id else None
        premises = tuple(
            symbol_table.get_term_symbol(pid) or f"node:term_{pid}"
            for pid in self.supporting_premise_ids
        )
        return P23EProvenanceRecord(
            derivation_rule_id=rule_symbol,
            supporting_premises=premises,
            originating_session_id=f"session:{self.session_id}" if self.session_id else "",
            originating_turn_id=f"turn:{self.turn_id}" if self.turn_id else "",
            timestamp=self.timestamp,
            metadata={"confidence": self.confidence},
        )

    @classmethod
    def from_p23e_provenance(
        cls,
        p23e_prov: P23EProvenanceRecord,
        symbol_table: SymbolTable,
    ) -> ProvenanceRecord:
        """Convert P23-E string-based ProvenanceRecord to numeric Core ProvenanceRecord."""
        rule_id = symbol_table.intern_rule(p23e_prov.derivation_rule_id) if p23e_prov.derivation_rule_id else 0
        premise_ids = tuple(
            symbol_table.intern_node(p) for p in p23e_prov.supporting_premises
        )

        session_id = 0
        if p23e_prov.originating_session_id:
            try:
                session_id = int(p23e_prov.originating_session_id.split(":")[-1])
            except ValueError:
                session_id = symbol_table.intern_node(p23e_prov.originating_session_id)

        turn_id = 0
        if p23e_prov.originating_turn_id:
            try:
                turn_id = int(p23e_prov.originating_turn_id.split(":")[-1])
            except ValueError:
                turn_id = symbol_table.intern_node(p23e_prov.originating_turn_id)

        confidence = float(p23e_prov.metadata.get("confidence", 1.0)) if p23e_prov.metadata else 1.0

        return cls(
            rule_id=rule_id,
            supporting_premise_ids=premise_ids,
            session_id=session_id,
            turn_id=turn_id,
            timestamp=p23e_prov.timestamp,
            confidence=confidence,
        )
