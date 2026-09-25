"""
Phase 23-D — EXP-03 Dataset Generator
Generates deterministic multi-sentence/multi-turn discourse scenarios
covering 10 reference, zero-anaphora, and deixis phenomena.
"""
from typing import Dict, List, Any
import os
import json


def generate_coreference_corpus(seed: int = 42) -> Dict[str, Any]:
    corpus: Dict[str, Any] = {
        "metadata": {
            "experiment": "EXP-03_reference_resolution_and_zero_anaphora",
            "seed": seed,
            "version": "1.0.0",
            "total_cases": 10,
        },
        "scenarios": [
            {
                "id": "C01",
                "phenomenon": "english_overt_pronoun",
                "language": "EN",
                "text": "The user created a document. He submitted it to Lucia.",
                "sentences": [
                    "The user created a document.",
                    "He submitted it to Lucia.",
                ],
                "mentions": [
                    {"id": "m1", "text": "The user", "sent_idx": 0, "type": "NOMINAL", "gender": "MASCULINE", "animacy": "ANIMATE"},
                    {"id": "m2", "text": "a document", "sent_idx": 0, "type": "NOMINAL", "gender": "NEUTER", "animacy": "INANIMATE"},
                    {"id": "m3", "text": "He", "sent_idx": 1, "type": "PRONOMINAL", "gender": "MASCULINE", "animacy": "ANIMATE"},
                    {"id": "m4", "text": "it", "sent_idx": 1, "type": "PRONOMINAL", "gender": "NEUTER", "animacy": "INANIMATE"},
                    {"id": "m5", "text": "Lucia", "sent_idx": 1, "type": "PROPER", "gender": "FEMININE", "animacy": "ANIMATE"},
                ],
                "gold_clusters": {
                    "ent_user": ["m1", "m3"],
                    "ent_doc": ["m2", "m4"],
                    "ent_lucia": ["m5"],
                },
                "is_ambiguous": False,
                "has_zero_anaphora": False,
            },
            {
                "id": "C02",
                "phenomenon": "japanese_omitted_subject",
                "language": "JA",
                "text": "ユーザーはタスクを開始した。[Ø] コードを修正した。",
                "sentences": [
                    "ユーザーはタスクを開始した。",
                    "[Ø] コードを修正した。",
                ],
                "mentions": [
                    {"id": "m1", "text": "ユーザー", "sent_idx": 0, "type": "NOMINAL", "salience": 1.0, "is_topic": True},
                    {"id": "m2", "text": "タスク", "sent_idx": 0, "type": "NOMINAL", "salience": 0.5, "is_topic": False},
                    {"id": "m3", "text": "[Ø_subject]", "sent_idx": 1, "type": "ZERO_ANAPHOR", "role": ":ARG0", "salience": 0.9},
                    {"id": "m4", "text": "コード", "sent_idx": 1, "type": "NOMINAL", "salience": 0.5, "is_topic": False},
                ],
                "gold_clusters": {
                    "ent_user": ["m1", "m3"],
                    "ent_task": ["m2"],
                    "ent_code": ["m4"],
                },
                "is_ambiguous": False,
                "has_zero_anaphora": True,
            },
            {
                "id": "C03",
                "phenomenon": "japanese_omitted_object",
                "language": "JA",
                "text": "ルシアは新しいレポートを作成した。ユーザーは [Ø] 確認した。",
                "sentences": [
                    "ルシアは新しいレポートを作成した。",
                    "ユーザーは [Ø] 確認した。",
                ],
                "mentions": [
                    {"id": "m1", "text": "ルシア", "sent_idx": 0, "type": "PROPER", "salience": 0.8, "role": ":ARG0"},
                    {"id": "m2", "text": "新しいレポート", "sent_idx": 0, "type": "NOMINAL", "salience": 0.9, "is_topic": True, "role": ":ARG1"},
                    {"id": "m3", "text": "ユーザー", "sent_idx": 1, "type": "NOMINAL", "salience": 1.0, "role": ":ARG0"},
                    {"id": "m4", "text": "[Ø_object]", "sent_idx": 1, "type": "ZERO_ANAPHOR", "role": ":ARG1", "salience": 0.8},
                ],
                "gold_clusters": {
                    "ent_lucia": ["m1"],
                    "ent_report": ["m2", "m4"],
                    "ent_user": ["m3"],
                },
                "is_ambiguous": False,
                "has_zero_anaphora": True,
            },
            {
                "id": "C04",
                "phenomenon": "japanese_unresolved_zero",
                "language": "JA",
                "text": "[Ø] 窓を開けた。",
                "sentences": [
                    "[Ø] 窓を開けた。",
                ],
                "mentions": [
                    {"id": "m1", "text": "[Ø_subject]", "sent_idx": 0, "type": "ZERO_ANAPHOR", "role": ":ARG0", "context_evidence": False},
                    {"id": "m2", "text": "窓", "sent_idx": 0, "type": "NOMINAL", "role": ":ARG1"},
                ],
                "gold_clusters": {
                    "UNKNOWN_ENTITY": ["m1"],
                    "ent_window": ["m2"],
                },
                "is_ambiguous": True,
                "has_zero_anaphora": True,
            },
            {
                "id": "C05",
                "phenomenon": "vietnamese_kinship_persistent",
                "language": "VI",
                "text": "Anh Nam là kỹ sư phần mềm. Anh đã hỗ trợ dự án này.",
                "sentences": [
                    "Anh Nam là kỹ sư phần mềm.",
                    "Anh đã hỗ trợ dự án này.",
                ],
                "mentions": [
                    {"id": "m1", "text": "Anh Nam", "sent_idx": 0, "type": "KINSHIP_PROPER", "social_rel": "SENIOR_MALE_PEER"},
                    {"id": "m2", "text": "Anh", "sent_idx": 1, "type": "KINSHIP_DEIXIS", "social_rel": "SENIOR_MALE_PEER"},
                    {"id": "m3", "text": "dự án này", "sent_idx": 1, "type": "NOMINAL"},
                ],
                "gold_clusters": {
                    "ent_nam": ["m1", "m2"],
                    "ent_project": ["m3"],
                },
                "is_ambiguous": False,
                "has_zero_anaphora": False,
            },
            {
                "id": "C06",
                "phenomenon": "vietnamese_perspective_shift",
                "language": "VI",
                "text": "Lucia: Em chào anh Nam. Admin: Anh Nam đã nhắc em về lịch họp. Nam: Tôi đã chuẩn bị xong.",
                "sentences": [
                    "Em chào anh Nam.",
                    "Anh Nam đã nhắc em về lịch họp.",
                    "Tôi đã chuẩn bị xong.",
                ],
                "mentions": [
                    {"id": "m1", "text": "Em (Lucia)", "sent_idx": 0, "speaker": "Lucia", "type": "KINSHIP_FIRST_PERSON"},
                    {"id": "m2", "text": "anh Nam", "sent_idx": 0, "speaker": "Lucia", "type": "KINSHIP_SECOND_PERSON"},
                    {"id": "m3", "text": "Anh Nam", "sent_idx": 1, "speaker": "Admin", "type": "KINSHIP_THIRD_PERSON"},
                    {"id": "m4", "text": "em (Admin)", "sent_idx": 1, "speaker": "Admin", "type": "KINSHIP_FIRST_PERSON"},
                    {"id": "m5", "text": "Tôi (Nam)", "sent_idx": 2, "speaker": "Nam", "type": "FIRST_PERSON_PRONOUN"},
                ],
                "gold_clusters": {
                    "ent_nam": ["m2", "m3", "m5"],
                    "ent_lucia": ["m1"],
                    "ent_admin": ["m4"],
                },
                "is_ambiguous": False,
                "has_zero_anaphora": False,
            },
            {
                "id": "C07",
                "phenomenon": "long_reference_chain",
                "language": "EN",
                "text": "The user opened the workstation. He reviewed the architecture. The system prompted for credentials. He entered the key. After that, he launched the simulation.",
                "sentences": [
                    "The user opened the workstation.",
                    "He reviewed the architecture.",
                    "The system prompted for credentials.",
                    "He entered the key.",
                    "After that, he launched the simulation.",
                ],
                "mentions": [
                    {"id": "m1", "text": "The user", "sent_idx": 0, "type": "NOMINAL"},
                    {"id": "m2", "text": "the workstation", "sent_idx": 0, "type": "NOMINAL"},
                    {"id": "m3", "text": "He", "sent_idx": 1, "type": "PRONOMINAL"},
                    {"id": "m4", "text": "the architecture", "sent_idx": 1, "type": "NOMINAL"},
                    {"id": "m5", "text": "The system", "sent_idx": 2, "type": "NOMINAL"},
                    {"id": "m6", "text": "credentials", "sent_idx": 2, "type": "NOMINAL"},
                    {"id": "m7", "text": "He", "sent_idx": 3, "type": "PRONOMINAL"},
                    {"id": "m8", "text": "the key", "sent_idx": 3, "type": "NOMINAL"},
                    {"id": "m9", "text": "he", "sent_idx": 4, "type": "PRONOMINAL"},
                    {"id": "m10", "text": "the simulation", "sent_idx": 4, "type": "NOMINAL"},
                ],
                "gold_clusters": {
                    "ent_user": ["m1", "m3", "m7", "m9"],
                    "ent_workstation": ["m2"],
                    "ent_architecture": ["m4"],
                    "ent_system": ["m5"],
                    "ent_credentials": ["m6"],
                    "ent_key": ["m8"],
                    "ent_simulation": ["m10"],
                },
                "is_ambiguous": False,
                "has_zero_anaphora": False,
            },
            {
                "id": "C08",
                "phenomenon": "competing_antecedents",
                "language": "EN",
                "text": "The user consulted the administrator. He requested elevated permissions from him.",
                "sentences": [
                    "The user consulted the administrator.",
                    "He requested elevated permissions from him.",
                ],
                "mentions": [
                    {"id": "m1", "text": "The user", "sent_idx": 0, "type": "NOMINAL", "gender": "MASCULINE", "role": ":ARG0"},
                    {"id": "m2", "text": "the administrator", "sent_idx": 0, "type": "NOMINAL", "gender": "MASCULINE", "role": ":ARG1"},
                    {"id": "m3", "text": "He", "sent_idx": 1, "type": "PRONOMINAL", "gender": "MASCULINE", "role": ":ARG0"},
                    {"id": "m4", "text": "him", "sent_idx": 1, "type": "PRONOMINAL", "gender": "MASCULINE", "role": ":ARG2"},
                ],
                "gold_clusters": {
                    "ent_user": ["m1", "m3"],
                    "ent_admin": ["m2", "m4"],
                },
                "is_ambiguous": False,
                "has_zero_anaphora": False,
            },
            {
                "id": "C09",
                "phenomenon": "ambiguous_antecedent",
                "language": "EN",
                "text": "The client telephoned the supplier because he needed an update.",
                "sentences": [
                    "The client telephoned the supplier because he needed an update.",
                ],
                "mentions": [
                    {"id": "m1", "text": "The client", "sent_idx": 0, "type": "NOMINAL", "gender": "MASCULINE"},
                    {"id": "m2", "text": "the supplier", "sent_idx": 0, "type": "NOMINAL", "gender": "MASCULINE"},
                    {"id": "m3", "text": "he", "sent_idx": 0, "type": "PRONOMINAL", "gender": "MASCULINE", "is_ambiguous": True},
                ],
                "gold_clusters": {
                    "ent_client": ["m1"],
                    "ent_supplier": ["m2"],
                    "AMBIGUOUS_UNRESOLVED": ["m3"],
                },
                "is_ambiguous": True,
                "has_zero_anaphora": False,
            },
            {
                "id": "C10",
                "phenomenon": "multi_event_persistence",
                "language": "EN",
                "text": "Lucia initialized the server. The server configured the network. The server started the database. It signaled readiness.",
                "sentences": [
                    "Lucia initialized the server.",
                    "The server configured the network.",
                    "The server started the database.",
                    "It signaled readiness.",
                ],
                "mentions": [
                    {"id": "m1", "text": "Lucia", "sent_idx": 0, "type": "PROPER", "role": ":ARG0"},
                    {"id": "m2", "text": "the server", "sent_idx": 0, "type": "NOMINAL", "role": ":ARG1", "animacy": "INANIMATE", "gender": "NEUTER"},
                    {"id": "m3", "text": "The server", "sent_idx": 1, "type": "NOMINAL", "role": ":ARG0", "animacy": "INANIMATE", "gender": "NEUTER"},
                    {"id": "m4", "text": "the network", "sent_idx": 1, "type": "NOMINAL", "role": ":ARG1", "animacy": "INANIMATE", "gender": "NEUTER"},
                    {"id": "m5", "text": "The server", "sent_idx": 2, "type": "NOMINAL", "role": ":ARG0", "animacy": "INANIMATE", "gender": "NEUTER"},
                    {"id": "m6", "text": "the database", "sent_idx": 2, "type": "NOMINAL", "role": ":ARG1", "animacy": "INANIMATE", "gender": "NEUTER"},
                    {"id": "m7", "text": "It", "sent_idx": 3, "type": "PRONOMINAL", "role": ":ARG0", "animacy": "INANIMATE", "gender": "NEUTER"},
                    {"id": "m8", "text": "readiness", "sent_idx": 3, "type": "NOMINAL", "role": ":ARG1"},
                ],
                "gold_clusters": {
                    "ent_lucia": ["m1"],
                    "ent_server": ["m2", "m3", "m5", "m7"],
                    "ent_network": ["m4"],
                    "ent_database": ["m6"],
                    "ent_readiness": ["m8"],
                },
                "is_ambiguous": False,
                "has_zero_anaphora": False,
            },
        ],
    }
    return corpus


def save_coreference_corpus(corpus: Dict[str, Any], filepath: str) -> None:
    os.makedirs(os.path.dirname(filepath), exist_ok=True)
    with open(filepath, "w", encoding="utf-8") as f:
        json.dump(corpus, f, indent=2)


if __name__ == "__main__":
    out = os.path.join(os.path.dirname(__file__), "corpus.json")
    c = generate_coreference_corpus(seed=42)
    save_coreference_corpus(c, out)
    print(f"Generated {len(c['scenarios'])} EXP-03 scenarios into {out}")
