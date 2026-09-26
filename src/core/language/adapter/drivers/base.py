"""
src/core/language/adapter/drivers/base.py

Shared utilities and baseline abstractions for language adapter drivers.
"""

from __future__ import annotations

import re
from typing import Dict, List, Optional, Set, Tuple

from src.core.knowledge.fortification import (
    EpistemicState,
    ProvenanceRecord,
    ScopeBoundary,
    ScopeType,
    SemanticEdge,
    SemanticGraph,
    SemanticNode,
)
from src.core.language.adapter.contracts import (
    CoverageReport,
    LanguageAdapter,
    ParseResult,
    RealizeResult,
)


class BaseLanguageDriver(LanguageAdapter):
    """
    Base class providing common graph construction, verification,
    and coverage calculation routines for language drivers.
    """

    def _create_empty_graph(self, session_id: str) -> SemanticGraph:
        """Create a new SemanticGraph initialized with ROOT scope."""
        graph = SemanticGraph(session_id=session_id)
        graph.add_scope(ScopeBoundary(scope_id="scope:root", scope_type=ScopeType.ROOT))
        return graph

    def _build_coverage_report(
        self,
        text: str,
        recognized_tokens: Set[str],
    ) -> CoverageReport:
        """Compute coverage ratio given recognized tokens."""
        # Simple whitespace tokenization for coverage approximation
        tokens = [t.strip().lower() for t in re.split(r"[\s,.\?!;:\"'（）()「」]+", text) if t.strip()]
        total_tokens = len(tokens)
        if total_tokens == 0:
            return CoverageReport(
                coverage_ratio=1.0,
                recognized_tokens_count=0,
                total_tokens_count=0,
                unrecognized_segments=(),
            )

        recognized_count = sum(1 for t in tokens if t in recognized_tokens)
        unrecognized = tuple(t for t in tokens if t not in recognized_tokens)
        ratio = round(recognized_count / total_tokens, 4)

        return CoverageReport(
            coverage_ratio=ratio,
            recognized_tokens_count=recognized_count,
            total_tokens_count=total_tokens,
            unrecognized_segments=unrecognized,
        )
