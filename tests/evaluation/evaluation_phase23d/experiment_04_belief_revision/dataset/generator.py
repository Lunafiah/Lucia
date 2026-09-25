"""Deterministic Dataset Generator for EXP-04: Belief Revision & Contradiction.

Covers 10 preregistered scenarios:
1. simple_contradiction: P then NOT P in same valid interval
2. authority_conflict: conflicting assertions from different authorities (Admin vs Guest)
3. dependent_belief: A -> B, A defeated -> B retracted
4. multi_hop_dependency: A -> B -> C, A defeated -> C retracted
5. local_revision: contradiction in Subgraph 1; Subgraph 2 completely unaffected
6. temporal_conflict: P valid in T1, NOT P valid in T2 (non-overlapping) -> NOT contradiction
7. same_interval_conflict: P and NOT P in overlapping valid intervals -> contradiction triggered
8. historical_retention: belief retracted (OUT) but historical record preserved in ledger
9. repeated_revision: P -> NOT P -> P, checking operational state and full provenance trace
10. irrelevant_subgraph: 50 independent background assertions, 0 collateral retraction
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Dict, List


def generate_exp04_corpus() -> Dict[str, Any]:
    scenarios: List[Dict[str, Any]] = [
        # 1. simple_contradiction
        {
            "id": "SC01",
            "name": "simple_contradiction",
            "description": "Direct negation in same valid-time interval: P then NOT P.",
            "initial_assertions": [
                {
                    "id": "SC01_A1",
                    "predicate": "HAS_STATUS",
                    "arguments": ["Server01", "Online"],
                    "polarity": True,
                    "conceiver": "User",
                    "valid_time": [0, 100],
                    "tx_time": 1,
                    "justifications": [],
                }
            ],
            "updates": [
                {
                    "id": "SC01_A2",
                    "predicate": "HAS_STATUS",
                    "arguments": ["Server01", "Online"],
                    "polarity": False,
                    "conceiver": "User",
                    "valid_time": [0, 100],
                    "tx_time": 2,
                    "justifications": [],
                }
            ],
            "expected_oracle": {
                "contradictions": [["SC01_A1", "SC01_A2"]],
                "final_states": {
                    "SC01_A1": "OUT",
                    "SC01_A2": "IN",
                },
                "retracted_dependencies": [],
                "unaffected_in": [],
                "history_count": 2,
                "defeaters": {
                    "SC01_A1": "SC01_A2",
                },
            },
        },
        # 2. authority_conflict
        {
            "id": "SC02",
            "name": "authority_conflict",
            "description": "Two conceivers assert conflicting facts; Admin (high authority) defeats Guest (low authority).",
            "initial_assertions": [
                {
                    "id": "SC02_A1",
                    "predicate": "ACCESS_LEVEL",
                    "arguments": ["User01", "ReadOnly"],
                    "polarity": True,
                    "conceiver": "Guest",
                    "valid_time": [0, 100],
                    "tx_time": 1,
                    "justifications": [],
                }
            ],
            "updates": [
                {
                    "id": "SC02_A2",
                    "predicate": "ACCESS_LEVEL",
                    "arguments": ["User01", "RootAdmin"],
                    "polarity": True,  # mutually exclusive functional relation
                    "conceiver": "Admin",
                    "valid_time": [0, 100],
                    "tx_time": 2,
                    "justifications": [],
                }
            ],
            "expected_oracle": {
                "contradictions": [["SC02_A1", "SC02_A2"]],
                "final_states": {
                    "SC02_A1": "OUT",
                    "SC02_A2": "IN",
                },
                "retracted_dependencies": [],
                "unaffected_in": [],
                "history_count": 2,
                "defeaters": {
                    "SC02_A1": "SC02_A2",
                },
            },
        },
        # 3. dependent_belief
        {
            "id": "SC03",
            "name": "dependent_belief",
            "description": "1-hop dependency: A -> B. When A is defeated, B must become OUT.",
            "initial_assertions": [
                {
                    "id": "SC03_A",
                    "predicate": "LOCATED_IN",
                    "arguments": ["User01", "DaNang"],
                    "polarity": True,
                    "conceiver": "User",
                    "valid_time": [0, 100],
                    "tx_time": 1,
                    "justifications": [],
                },
                {
                    "id": "SC03_B",
                    "predicate": "TIMEZONE",
                    "arguments": ["User01", "UTC+7"],
                    "polarity": True,
                    "conceiver": "LuciaInference",
                    "valid_time": [0, 100],
                    "tx_time": 2,
                    "justifications": ["SC03_A"],
                },
            ],
            "updates": [
                {
                    "id": "SC03_A_DEFEAT",
                    "predicate": "LOCATED_IN",
                    "arguments": ["User01", "Tokyo"],
                    "polarity": True,  # mutually exclusive with DaNang
                    "conceiver": "User",
                    "valid_time": [0, 100],
                    "tx_time": 3,
                    "justifications": [],
                }
            ],
            "expected_oracle": {
                "contradictions": [["SC03_A", "SC03_A_DEFEAT"]],
                "final_states": {
                    "SC03_A": "OUT",
                    "SC03_B": "OUT",
                    "SC03_A_DEFEAT": "IN",
                },
                "retracted_dependencies": ["SC03_B"],
                "unaffected_in": [],
                "history_count": 3,
                "defeaters": {
                    "SC03_A": "SC03_A_DEFEAT",
                    "SC03_B": "SC03_A",
                },
            },
        },
        # 4. multi_hop_dependency
        {
            "id": "SC04",
            "name": "multi_hop_dependency",
            "description": "Multi-hop dependency A -> B -> C. Defeat of A propagates all the way to C.",
            "initial_assertions": [
                {
                    "id": "SC04_A",
                    "predicate": "EMPLOYED_AT",
                    "arguments": ["User01", "TechCorp"],
                    "polarity": True,
                    "conceiver": "User",
                    "valid_time": [0, 100],
                    "tx_time": 1,
                    "justifications": [],
                },
                {
                    "id": "SC04_B",
                    "predicate": "HOLDS_BADGE",
                    "arguments": ["User01", "TechBadge101"],
                    "polarity": True,
                    "conceiver": "LuciaInference",
                    "valid_time": [0, 100],
                    "tx_time": 2,
                    "justifications": ["SC04_A"],
                },
                {
                    "id": "SC04_C",
                    "predicate": "HAS_PHYSICAL_ACCESS",
                    "arguments": ["User01", "ServerRoomB"],
                    "polarity": True,
                    "conceiver": "LuciaInference",
                    "valid_time": [0, 100],
                    "tx_time": 3,
                    "justifications": ["SC04_B"],
                },
            ],
            "updates": [
                {
                    "id": "SC04_A_DEFEAT",
                    "predicate": "EMPLOYED_AT",
                    "arguments": ["User01", "TechCorp"],
                    "polarity": False,
                    "conceiver": "Admin",
                    "valid_time": [0, 100],
                    "tx_time": 4,
                    "justifications": [],
                }
            ],
            "expected_oracle": {
                "contradictions": [["SC04_A", "SC04_A_DEFEAT"]],
                "final_states": {
                    "SC04_A": "OUT",
                    "SC04_B": "OUT",
                    "SC04_C": "OUT",
                    "SC04_A_DEFEAT": "IN",
                },
                "retracted_dependencies": ["SC04_B", "SC04_C"],
                "unaffected_in": [],
                "history_count": 4,
                "defeaters": {
                    "SC04_A": "SC04_A_DEFEAT",
                    "SC04_B": "SC04_A",
                    "SC04_C": "SC04_B",
                },
            },
        },
        # 5. local_revision
        {
            "id": "SC05",
            "name": "local_revision",
            "description": "Contradiction in Subgraph 1 (P1 -> D1). Subgraph 2 (P2 -> D2) must remain strictly IN.",
            "initial_assertions": [
                {
                    "id": "SC05_P1",
                    "predicate": "PREFERS_THEME",
                    "arguments": ["User01", "DarkTheme"],
                    "polarity": True,
                    "conceiver": "User",
                    "valid_time": [0, 100],
                    "tx_time": 1,
                    "justifications": [],
                },
                {
                    "id": "SC05_D1",
                    "predicate": "RENDER_BACKGROUND",
                    "arguments": ["UI", "Hex1A1A1A"],
                    "polarity": True,
                    "conceiver": "LuciaInference",
                    "valid_time": [0, 100],
                    "tx_time": 2,
                    "justifications": ["SC05_P1"],
                },
                {
                    "id": "SC05_P2",
                    "predicate": "PRIMARY_LANGUAGE",
                    "arguments": ["User01", "Vietnamese"],
                    "polarity": True,
                    "conceiver": "User",
                    "valid_time": [0, 100],
                    "tx_time": 3,
                    "justifications": [],
                },
                {
                    "id": "SC05_D2",
                    "predicate": "LOCALE_CONFIG",
                    "arguments": ["UI", "vi-VN"],
                    "polarity": True,
                    "conceiver": "LuciaInference",
                    "valid_time": [0, 100],
                    "tx_time": 4,
                    "justifications": ["SC05_P2"],
                },
            ],
            "updates": [
                {
                    "id": "SC05_P1_UPDATE",
                    "predicate": "PREFERS_THEME",
                    "arguments": ["User01", "LightTheme"],
                    "polarity": True,  # mutually exclusive
                    "conceiver": "User",
                    "valid_time": [0, 100],
                    "tx_time": 5,
                    "justifications": [],
                }
            ],
            "expected_oracle": {
                "contradictions": [["SC05_P1", "SC05_P1_UPDATE"]],
                "final_states": {
                    "SC05_P1": "OUT",
                    "SC05_D1": "OUT",
                    "SC05_P1_UPDATE": "IN",
                    "SC05_P2": "IN",
                    "SC05_D2": "IN",
                },
                "retracted_dependencies": ["SC05_D1"],
                "unaffected_in": ["SC05_P2", "SC05_D2"],
                "history_count": 5,
                "defeaters": {
                    "SC05_P1": "SC05_P1_UPDATE",
                    "SC05_D1": "SC05_P1",
                },
            },
        },
        # 6. temporal_conflict (Non-overlapping valid times -> NOT a contradiction)
        {
            "id": "SC06",
            "name": "temporal_conflict",
            "description": "P true in [2023, 2024], NOT P true in [2025, 2026]. Disjoint valid times -> No contradiction.",
            "initial_assertions": [
                {
                    "id": "SC06_A1",
                    "predicate": "HAS_ROLE",
                    "arguments": ["User01", "JuniorDev"],
                    "polarity": True,
                    "conceiver": "User",
                    "valid_time": [2023, 2024],
                    "tx_time": 1,
                    "justifications": [],
                }
            ],
            "updates": [
                {
                    "id": "SC06_A2",
                    "predicate": "HAS_ROLE",
                    "arguments": ["User01", "JuniorDev"],
                    "polarity": False,
                    "conceiver": "User",
                    "valid_time": [2025, 2026],
                    "tx_time": 2,
                    "justifications": [],
                }
            ],
            "expected_oracle": {
                "contradictions": [],  # Valid times disjoint -> Zero contradiction
                "final_states": {
                    "SC06_A1": "IN",
                    "SC06_A2": "IN",
                },
                "retracted_dependencies": [],
                "unaffected_in": ["SC06_A1", "SC06_A2"],
                "history_count": 2,
                "defeaters": {},
            },
        },
        # 7. same_interval_conflict (Overlapping valid times -> Contradiction triggered)
        {
            "id": "SC07",
            "name": "same_interval_conflict",
            "description": "P valid in [2026-01, 2026-12], NOT P valid in [2026-06, 2026-08]. Overlapping -> Contradiction.",
            "initial_assertions": [
                {
                    "id": "SC07_A1",
                    "predicate": "SUBSCRIPTION_STATUS",
                    "arguments": ["User01", "ActivePro"],
                    "polarity": True,
                    "conceiver": "BillingSystem",
                    "valid_time": [100, 200],
                    "tx_time": 1,
                    "justifications": [],
                }
            ],
            "updates": [
                {
                    "id": "SC07_A2",
                    "predicate": "SUBSCRIPTION_STATUS",
                    "arguments": ["User01", "ActivePro"],
                    "polarity": False,
                    "conceiver": "BillingSystem",
                    "valid_time": [150, 180],  # Overlaps [100, 200]
                    "tx_time": 2,
                    "justifications": [],
                }
            ],
            "expected_oracle": {
                "contradictions": [["SC07_A1", "SC07_A2"]],
                "final_states": {
                    "SC07_A1": "OUT",
                    "SC07_A2": "IN",
                },
                "retracted_dependencies": [],
                "unaffected_in": [],
                "history_count": 2,
                "defeaters": {
                    "SC07_A1": "SC07_A2",
                },
            },
        },
        # 8. historical_retention
        {
            "id": "SC08",
            "name": "historical_retention",
            "description": "Belief retracted (OUT), but full provenance and assertion metadata preserved in ledger.",
            "initial_assertions": [
                {
                    "id": "SC08_A1",
                    "predicate": "PROJECT_DEADLINE",
                    "arguments": ["LuciaP23", "2026-10-01"],
                    "polarity": True,
                    "conceiver": "User",
                    "valid_time": [0, 100],
                    "tx_time": 1,
                    "justifications": [],
                }
            ],
            "updates": [
                {
                    "id": "SC08_A2",
                    "predicate": "PROJECT_DEADLINE",
                    "arguments": ["LuciaP23", "2026-11-15"],
                    "polarity": True,
                    "conceiver": "User",
                    "valid_time": [0, 100],
                    "tx_time": 2,
                    "justifications": [],
                }
            ],
            "expected_oracle": {
                "contradictions": [["SC08_A1", "SC08_A2"]],
                "final_states": {
                    "SC08_A1": "OUT",
                    "SC08_A2": "IN",
                },
                "retracted_dependencies": [],
                "unaffected_in": [],
                "history_count": 2,
                "defeaters": {
                    "SC08_A1": "SC08_A2",
                },
            },
        },
        # 9. repeated_revision (P -> NOT P -> P)
        {
            "id": "SC09",
            "name": "repeated_revision",
            "description": "Repeated revision cycle: P1 -> NOT P2 -> P3. Tests complete state flip and provenance chain.",
            "initial_assertions": [
                {
                    "id": "SC09_P1",
                    "predicate": "CAN_EXECUTE_SCRIPTS",
                    "arguments": ["AgentDaemon", "True"],
                    "polarity": True,
                    "conceiver": "Admin",
                    "valid_time": [0, 100],
                    "tx_time": 1,
                    "justifications": [],
                }
            ],
            "updates": [
                {
                    "id": "SC09_P2",
                    "predicate": "CAN_EXECUTE_SCRIPTS",
                    "arguments": ["AgentDaemon", "True"],
                    "polarity": False,
                    "conceiver": "Admin",
                    "valid_time": [0, 100],
                    "tx_time": 2,
                    "justifications": [],
                },
                {
                    "id": "SC09_P3",
                    "predicate": "CAN_EXECUTE_SCRIPTS",
                    "arguments": ["AgentDaemon", "True"],
                    "polarity": True,
                    "conceiver": "Admin",
                    "valid_time": [0, 100],
                    "tx_time": 3,
                    "justifications": [],
                },
            ],
            "expected_oracle": {
                "contradictions": [
                    ["SC09_P1", "SC09_P2"],
                    ["SC09_P2", "SC09_P3"],
                ],
                "final_states": {
                    "SC09_P1": "OUT",
                    "SC09_P2": "OUT",
                    "SC09_P3": "IN",
                },
                "retracted_dependencies": [],
                "unaffected_in": [],
                "history_count": 3,
                "defeaters": {
                    "SC09_P1": "SC09_P2",
                    "SC09_P2": "SC09_P3",
                },
            },
        },
        # 10. irrelevant_subgraph (50 independent background assertions, zero collateral retraction)
        {
            "id": "SC10",
            "name": "irrelevant_subgraph",
            "description": "50 independent background assertions present. Contradiction in target premise must yield CRR=0.",
            "initial_assertions": [
                # Target premise and dependent
                {
                    "id": "SC10_TARGET_P",
                    "predicate": "AUDIO_OUTPUT_DEVICE",
                    "arguments": ["System", "Speakers"],
                    "polarity": True,
                    "conceiver": "User",
                    "valid_time": [0, 100],
                    "tx_time": 1,
                    "justifications": [],
                },
                {
                    "id": "SC10_TARGET_D",
                    "predicate": "SAMPLING_RATE",
                    "arguments": ["System", "48000Hz"],
                    "polarity": True,
                    "conceiver": "LuciaInference",
                    "valid_time": [0, 100],
                    "tx_time": 2,
                    "justifications": ["SC10_TARGET_P"],
                },
            ]
            + [
                # 50 background independent facts
                {
                    "id": f"SC10_BG_{i:02d}",
                    "predicate": f"BACKGROUND_FACT_{i:02d}",
                    "arguments": [f"Entity_{i:02d}", f"Value_{i:02d}"],
                    "polarity": True,
                    "conceiver": "SystemSeed",
                    "valid_time": [0, 100],
                    "tx_time": 3 + i,
                    "justifications": [],
                }
                for i in range(50)
            ],
            "updates": [
                {
                    "id": "SC10_TARGET_DEFEAT",
                    "predicate": "AUDIO_OUTPUT_DEVICE",
                    "arguments": ["System", "Headphones"],
                    "polarity": True,  # mutually exclusive
                    "conceiver": "User",
                    "valid_time": [0, 100],
                    "tx_time": 55,
                    "justifications": [],
                }
            ],
            "expected_oracle": {
                "contradictions": [["SC10_TARGET_P", "SC10_TARGET_DEFEAT"]],
                "final_states": {
                    "SC10_TARGET_P": "OUT",
                    "SC10_TARGET_D": "OUT",
                    "SC10_TARGET_DEFEAT": "IN",
                    **{f"SC10_BG_{i:02d}": "IN" for i in range(50)},
                },
                "retracted_dependencies": ["SC10_TARGET_D"],
                "unaffected_in": [f"SC10_BG_{i:02d}" for i in range(50)],
                "history_count": 53,
                "defeaters": {
                    "SC10_TARGET_P": "SC10_TARGET_DEFEAT",
                    "SC10_TARGET_D": "SC10_TARGET_P",
                },
            },
        },
    ]

    return {
        "benchmark": "Phase23D_EXP04_BeliefRevision",
        "version": "1.0.0",
        "description": "Deterministic evaluation corpus for belief revision, contradiction detection, and JTMS dependency propagation.",
        "scenario_count": len(scenarios),
        "scenarios": scenarios,
    }


def write_corpus(output_path: Path) -> None:
    corpus = generate_exp04_corpus()
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(corpus, f, indent=2, ensure_ascii=False)


if __name__ == "__main__":
    out = Path(__file__).parent / "corpus.json"
    write_corpus(out)
    print(f"Generated EXP-04 corpus with {len(generate_exp04_corpus()['scenarios'])} scenarios at {out}")
