"""
tests/unit/test_p23h_rule_compiler.py

Comprehensive Unit Test Suite for KnowledgeStore -> P23-H RuleIndex Compiler.
Verifies all 17 specification test cases defined in:
DOC-P23H-RULE-COMPILER-IMPLEMENTATION-SPEC-R1-001.
"""

from __future__ import annotations

import pytest

from src.core.cognition.contract.projection import SymbolTable
from src.core.cognition.kernel.binding import (
    VAR_0,
    VAR_1,
    VAR_2,
    VAR_3,
    VAR_4,
    VAR_5,
    VAR_6,
    VAR_7,
)
from src.core.cognition.kernel.compiler import (
    RuleCompilationReport,
    RuleDiagnostic,
    RuleDiagnosticCode,
    compile_rule_set,
    is_variable_token,
)
from src.core.cognition.kernel.rules import InferenceRule as P23HInferenceRule, RuleIndex
from src.core.knowledge.proposition import InferenceRule as KSInferenceRule
from src.core.knowledge.store import KnowledgeStore


class TestRuleCompilerValidation:
    """Test suite covering the 17 specification cases for RuleCompilerAdapter."""

    def test_tc01_valid_ground_rule(self):
        """TC-01: Valid ground rule (all constants, no vars) compiles correctly."""
        st = SymbolTable()
        ks_rule = KSInferenceRule(
            id="rule:socrates",
            name="Socrates is mortal",
            domain="philosophy",
            antecedents=[("ent:socrates", "is_a", "c:human")],
            consequent_pattern=("ent:socrates", "is_a", "c:mortal"),
            confidence_decay=0.95,
        )

        rule_index, report = compile_rule_set([ks_rule], st)

        assert report.total_source_rules == 1
        assert report.compiled_count == 1
        assert report.quarantined_count == 0
        assert len(report.diagnostics) == 1
        assert report.diagnostics[0].code == RuleDiagnosticCode.OK

        # Verify kernel rule structure
        ru_id = st.intern_rule("rule:socrates")
        compiled = rule_index.get_rule_by_id(ru_id)
        assert compiled is not None
        assert compiled.head.predicate_id == st.intern_concept("is_a")
        assert compiled.head.arg0 == st.intern_concept("ent:socrates")
        assert compiled.head.arg1 == st.intern_concept("c:mortal")
        assert compiled.head.arg2 == 0
        assert compiled.head.polarity is True
        assert len(compiled.premises) == 1
        assert compiled.premises[0].arg0 == st.intern_concept("ent:socrates")
        assert compiled.premises[0].arg1 == st.intern_concept("c:human")
        assert compiled.premises[0].polarity is True

    def test_tc02_valid_variable_rule(self):
        """TC-02: Valid variable rule P(?x) -> Q(?x) compiles with VAR_0 in both slots."""
        st = SymbolTable()
        ks_rule = KSInferenceRule(
            id="rule:human_mortal",
            name="All humans are mortal",
            domain="philosophy",
            antecedents=[("?x", "is_a", "c:human")],
            consequent_pattern=("?x", "is_a", "c:mortal"),
        )

        rule_index, report = compile_rule_set([ks_rule], st)

        assert report.compiled_count == 1
        ru_id = st.intern_rule("rule:human_mortal")
        compiled = rule_index.get_rule_by_id(ru_id)
        assert compiled is not None
        assert compiled.head.arg0 == VAR_0  # -1
        assert compiled.premises[0].arg0 == VAR_0  # -1

    def test_tc03_variable_in_head_arg2(self):
        """TC-03: Variable first appearing in head.arg2 allocates correctly."""
        st = SymbolTable()
        # Consequent is 4-tuple with ?z in arg2
        ks_rule = KSInferenceRule(
            id="rule:ternary_transfer",
            name="Ternary Transfer",
            domain="commerce",
            antecedents=[
                ("?x", "owns", "?z"),
                ("?x", "trades_to", "?y"),
            ],
            consequent_pattern=("?x", "transfers", "?y", "?z"),
        )

        rule_index, report = compile_rule_set([ks_rule], st)

        assert report.compiled_count == 1
        ru_id = st.intern_rule("rule:ternary_transfer")
        compiled = rule_index.get_rule_by_id(ru_id)
        assert compiled is not None
        # Scan order: head.arg0 (?x -> VAR_0), head.arg1 (?y -> VAR_1), head.arg2 (?z -> VAR_2)
        assert compiled.head.arg0 == VAR_0
        assert compiled.head.arg1 == VAR_1
        assert compiled.head.arg2 == VAR_2
        # Check premises received matching bound indices
        assert compiled.premises[0].arg0 == VAR_0
        assert compiled.premises[0].arg1 == VAR_2
        assert compiled.premises[1].arg0 == VAR_0
        assert compiled.premises[1].arg1 == VAR_1

    def test_tc04_exactly_8_variables(self):
        """TC-04: Rule with exactly 8 distinct variables compiles successfully."""
        st = SymbolTable()
        ks_rule = KSInferenceRule(
            id="rule:max_vars",
            name="Max 8 Variables",
            domain="math",
            antecedents=[
                ("?a", "rel1", "?b"),
                ("?c", "rel2", "?d"),
                ("?e", "rel3", "?f"),
                ("?g", "rel4", "?h"),
            ],
            consequent_pattern=("?a", "consequent", "?h"),
        )

        rule_index, report = compile_rule_set([ks_rule], st)

        assert report.compiled_count == 1
        assert report.quarantined_count == 0
        ru_id = st.intern_rule("rule:max_vars")
        compiled = rule_index.get_rule_by_id(ru_id)
        assert compiled is not None
        # Head: ?a (VAR_0), ?h (VAR_1)
        assert compiled.head.arg0 == VAR_0
        assert compiled.head.arg1 == VAR_1

    def test_tc05_9_variables_quarantined(self):
        """TC-05: Rule with 9 distinct variables is quarantined with EXCESS_VARIABLES."""
        st = SymbolTable()
        ks_rule = KSInferenceRule(
            id="rule:too_many_vars",
            name="Excess 9 Variables",
            domain="math",
            antecedents=[
                ("?a", "rel1", "?b"),
                ("?c", "rel2", "?d"),
                ("?e", "rel3", "?f"),
                ("?g", "rel4", "?h", "?i"),  # 9th variable ?i
            ],
            consequent_pattern=("?a", "consequent", "?h"),
        )

        rule_index, report = compile_rule_set([ks_rule], st)

        assert report.compiled_count == 0
        assert report.quarantined_count == 1
        assert report.diagnostics[0].code == RuleDiagnosticCode.EXCESS_VARIABLES

    def test_tc06_unsafe_head_variable_quarantined(self):
        """TC-06: Unsafe head variable P(?x) -> Q(?x, ?y) is quarantined."""
        st = SymbolTable()
        ks_rule = KSInferenceRule(
            id="rule:unsafe_horn",
            name="Unsafe Horn Rule",
            domain="logic",
            antecedents=[("?x", "is_a", "c:dog")],
            consequent_pattern=("?x", "has_puppy", "?y"),  # ?y is unbound by antecedents!
        )

        rule_index, report = compile_rule_set([ks_rule], st)

        assert report.compiled_count == 0
        assert report.quarantined_count == 1
        diag = report.diagnostics[0]
        assert diag.code == RuleDiagnosticCode.UNSAFE_HEAD_VARIABLE
        assert "?y" in diag.detail

    def test_tc07_malformed_tuple_quarantined(self):
        """TC-07: Malformed tuple (consequent length 2 or 5) is quarantined."""
        st = SymbolTable()
        r_too_short = KSInferenceRule(
            id="rule:short_consequent",
            name="Short Consequent",
            domain="test",
            antecedents=[("?x", "p", "?y")],
            consequent_pattern=("?x", "p"),  # len 2
        )
        r_too_long = KSInferenceRule(
            id="rule:long_consequent",
            name="Long Consequent",
            domain="test",
            antecedents=[("?x", "p", "?y")],
            consequent_pattern=("?x", "p", "?y", "?z", "extra"),  # len 5
        )

        rule_index, report = compile_rule_set([r_too_short, r_too_long], st)

        assert report.compiled_count == 0
        assert report.quarantined_count == 2
        assert report.diagnostics[0].code == RuleDiagnosticCode.MALFORMED_STRUCTURE
        assert report.diagnostics[1].code == RuleDiagnosticCode.MALFORMED_STRUCTURE

    def test_tc08_empty_predicate_quarantined(self):
        """TC-08: Empty string or bare '?' as predicate is quarantined."""
        st = SymbolTable()
        r_empty = KSInferenceRule(
            id="rule:empty_pred",
            name="Empty Predicate",
            domain="test",
            antecedents=[("?x", "p", "?y")],
            consequent_pattern=("?x", "   ", "?y"),
        )
        r_bare_q = KSInferenceRule(
            id="rule:bare_q_pred",
            name="Bare Question Mark Predicate",
            domain="test",
            antecedents=[("?x", "?", "?y")],
            consequent_pattern=("?x", "valid_pred", "?y"),
        )

        rule_index, report = compile_rule_set([r_empty, r_bare_q], st)

        assert report.compiled_count == 0
        assert report.quarantined_count == 2
        assert report.diagnostics[0].code == RuleDiagnosticCode.EMPTY_PREDICATE
        assert report.diagnostics[1].code == RuleDiagnosticCode.EMPTY_PREDICATE

    def test_tc09_excess_antecedents_quarantined(self):
        """TC-09: Rule with 5 antecedents is quarantined with EXCESS_PREMISES."""
        st = SymbolTable()
        ks_rule = KSInferenceRule(
            id="rule:five_premises",
            name="Five Antecedents",
            domain="test",
            antecedents=[
                ("?x", "p1", "?a"),
                ("?a", "p2", "?b"),
                ("?b", "p3", "?c"),
                ("?c", "p4", "?d"),
                ("?d", "p5", "?y"),
            ],
            consequent_pattern=("?x", "goal", "?y"),
        )

        rule_index, report = compile_rule_set([ks_rule], st)

        assert report.compiled_count == 0
        assert report.quarantined_count == 1
        assert report.diagnostics[0].code == RuleDiagnosticCode.EXCESS_PREMISES

    def test_tc10_duplicate_ids_at_compiler_boundary(self):
        """TC-10: Duplicate rule IDs in compiler input sequence -> first compiles, second skips."""
        st = SymbolTable()
        r1 = KSInferenceRule(
            id="rule:duplicate_id",
            name="Version 1",
            domain="test",
            antecedents=[("?x", "is_a", "c:dog")],
            consequent_pattern=("?x", "is_a", "c:mammal"),
        )
        r2 = KSInferenceRule(
            id="rule:duplicate_id",
            name="Version 2",
            domain="test",
            antecedents=[("?x", "is_a", "c:cat")],
            consequent_pattern=("?x", "is_a", "c:mammal"),
        )

        rule_index, report = compile_rule_set([r1, r2], st)

        assert report.total_source_rules == 2
        assert report.compiled_count == 1
        assert report.quarantined_count == 1
        assert report.diagnostics[0].code == RuleDiagnosticCode.OK
        assert report.diagnostics[1].code == RuleDiagnosticCode.DUPLICATE_RULE_ID

        # Verify only the first rule is in index
        ru_id = st.intern_rule("rule:duplicate_id")
        compiled = rule_index.get_rule_by_id(ru_id)
        assert compiled is not None
        assert compiled.premises[0].arg1 == st.intern_concept("c:dog")

    def test_tc11_duplicate_ids_overwritten_by_knowledgestore(self):
        """TC-11: KnowledgeStore storage already overwrites duplicates at dict level."""
        store = KnowledgeStore()
        r1 = KSInferenceRule(
            id="rule:same_id",
            name="Version 1",
            domain="test",
            antecedents=[("?x", "p", "a")],
            consequent_pattern=("?x", "q", "b"),
        )
        r2 = KSInferenceRule(
            id="rule:same_id",
            name="Version 2",
            domain="test",
            antecedents=[("?x", "p", "c")],
            consequent_pattern=("?x", "q", "d"),
        )

        store.store_rule(r1)
        store.store_rule(r2)  # Overwrites r1 in _rules dict

        all_rules = store.get_all_rules()
        assert len(all_rules) == 1
        assert all_rules[0].name == "Version 2"

        # Compiler receives only 1 rule
        st = SymbolTable()
        rule_index, report = compile_rule_set(all_rules, st)
        assert report.total_source_rules == 1
        assert report.compiled_count == 1

    def test_tc12_deterministic_rule_ordering(self):
        """TC-12: Input order perturbation produces identical RuleIndex."""
        r_b = KSInferenceRule(
            id="rule:b",
            name="B Rule",
            domain="test",
            antecedents=[("?x", "p", "b")],
            consequent_pattern=("?x", "q", "b"),
        )
        r_a = KSInferenceRule(
            id="rule:a",
            name="A Rule",
            domain="test",
            antecedents=[("?x", "p", "a")],
            consequent_pattern=("?x", "q", "a"),
        )

        st1 = SymbolTable()
        index1, report1 = compile_rule_set([r_b, r_a], st1)

        st2 = SymbolTable()
        index2, report2 = compile_rule_set([r_a, r_b], st2)

        # Both compile rule:a first, then rule:b
        assert report1.compiled_count == 2
        assert report2.compiled_count == 2
        assert report1.diagnostics[0].source_rule_id == "rule:a"
        assert report1.diagnostics[1].source_rule_id == "rule:b"
        assert report2.diagnostics[0].source_rule_id == "rule:a"
        assert report2.diagnostics[1].source_rule_id == "rule:b"

    def test_tc13_deterministic_local_variable_allocation(self):
        """TC-13: Scan order head -> premises allocates variables deterministically."""
        st = SymbolTable()
        ks_rule = KSInferenceRule(
            id="rule:var_order",
            name="Var Order",
            domain="test",
            antecedents=[("?y", "p", "?x")],
            consequent_pattern=("?x", "q", "?y"),
        )

        rule_index, report = compile_rule_set([ks_rule], st)

        ru_id = st.intern_rule("rule:var_order")
        compiled = rule_index.get_rule_by_id(ru_id)
        assert compiled is not None
        # Head scanned first: ?x -> VAR_0 (-1), ?y -> VAR_1 (-2)
        assert compiled.head.arg0 == VAR_0
        assert compiled.head.arg1 == VAR_1
        # Premise inherits: ?y -> VAR_1, ?x -> VAR_0
        assert compiled.premises[0].arg0 == VAR_1
        assert compiled.premises[0].arg1 == VAR_0

    def test_tc14_repeated_variable_consistency(self):
        """TC-14: Repeated variables within and across premises share identical index."""
        st = SymbolTable()
        ks_rule = KSInferenceRule(
            id="rule:transitivity",
            name="Transitivity",
            domain="test",
            antecedents=[
                ("?x", "rel", "?y"),
                ("?y", "rel", "?z"),
            ],
            consequent_pattern=("?x", "rel", "?z"),
        )

        rule_index, report = compile_rule_set([ks_rule], st)

        ru_id = st.intern_rule("rule:transitivity")
        compiled = rule_index.get_rule_by_id(ru_id)
        assert compiled is not None
        # Head: ?x -> VAR_0, ?z -> VAR_1
        assert compiled.head.arg0 == VAR_0
        assert compiled.head.arg1 == VAR_1
        # Premise 0: ?x -> VAR_0, ?y -> VAR_2
        assert compiled.premises[0].arg0 == VAR_0
        assert compiled.premises[0].arg1 == VAR_2
        # Premise 1: ?y -> VAR_2 (same!), ?z -> VAR_1 (same!)
        assert compiled.premises[1].arg0 == VAR_2
        assert compiled.premises[1].arg1 == VAR_1

    def test_tc15_polarity_true_for_all(self):
        """TC-15: All compiled RuleHead and RulePremise have polarity=True."""
        st = SymbolTable()
        ks_rule = KSInferenceRule(
            id="rule:horn",
            name="Positive Horn",
            domain="test",
            antecedents=[("?x", "p", "?y"), ("?y", "q", "?z")],
            consequent_pattern=("?x", "r", "?z"),
        )

        rule_index, report = compile_rule_set([ks_rule], st)

        ru_id = st.intern_rule("rule:horn")
        compiled = rule_index.get_rule_by_id(ru_id)
        assert compiled is not None
        assert compiled.head.polarity is True
        for p in compiled.premises:
            assert p.polarity is True

    def test_tc16_confidence_decay_excluded_from_kernel(self):
        """TC-16: Source confidence_decay does not leak into kernel rule structure."""
        st = SymbolTable()
        ks_rule = KSInferenceRule(
            id="rule:decay",
            name="Decaying Rule",
            domain="test",
            antecedents=[("?x", "p", "?y")],
            consequent_pattern=("?x", "q", "?y"),
            confidence_decay=0.75,
        )

        rule_index, report = compile_rule_set([ks_rule], st)

        ru_id = st.intern_rule("rule:decay")
        compiled = rule_index.get_rule_by_id(ru_id)
        assert compiled is not None
        # P23HInferenceRule has slots: (rule_id, head, premises)
        assert not hasattr(compiled, "confidence_decay")
        assert not hasattr(compiled.head, "confidence_decay")

    def test_tc17_lifecycle_recompilation_after_reset(self):
        """TC-17: Recompilation with a fresh SymbolTable resets indices cleanly."""
        ks_rule = KSInferenceRule(
            id="rule:lifecycle",
            name="Lifecycle Test",
            domain="test",
            antecedents=[("?x", "p", "c:target")],
            consequent_pattern=("?x", "q", "c:target"),
        )

        # First lifecycle epoch
        st_epoch1 = SymbolTable()
        index_epoch1, report1 = compile_rule_set([ks_rule], st_epoch1)
        ru_id_1 = st_epoch1.intern_rule("rule:lifecycle")

        # Second lifecycle epoch (after reset_lifecycle)
        st_epoch2 = SymbolTable()
        index_epoch2, report2 = compile_rule_set([ks_rule], st_epoch2)
        ru_id_2 = st_epoch2.intern_rule("rule:lifecycle")

        assert ru_id_1 == ru_id_2 == 1
        assert report1.compiled_count == 1
        assert report2.compiled_count == 1
