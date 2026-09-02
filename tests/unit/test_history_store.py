"""Unit tests for ChatHistoryStore persistence and export."""
import os
import pytest
from src.core.storage.history_store import ChatHistoryStore


class TestChatHistoryStore:
    def test_store_creation_and_append(self, tmp_path):
        history_file = tmp_path / "chat_history.json"
        store = ChatHistoryStore(file_path=str(history_file))

        turn1 = store.append_turn("user", "Hello Lucia")
        assert turn1["role"] == "user"
        assert turn1["content"] == "Hello Lucia"

        turn2 = store.append_turn("companion", "Hello my friend!")
        assert turn2["role"] == "companion"

        history = store.get_history()
        assert len(history) == 2
        assert history[0]["content"] == "Hello Lucia"
        assert history[1]["content"] == "Hello my friend!"

    def test_new_session_and_retrieval(self, tmp_path):
        history_file = tmp_path / "chat_history.json"
        store = ChatHistoryStore(file_path=str(history_file))

        store.append_turn("user", "Session 1 message")
        new_sid = store.new_session()
        assert "session_" in new_sid

        store.append_turn("user", "Session 2 message")
        history = store.get_history()
        assert len(history) == 2

    def test_clear_history(self, tmp_path):
        history_file = tmp_path / "chat_history.json"
        store = ChatHistoryStore(file_path=str(history_file))

        store.append_turn("user", "To be cleared")
        assert len(store.get_history()) == 1

        store.clear_history()
        assert len(store.get_history()) == 0

    def test_export_markdown(self, tmp_path):
        history_file = tmp_path / "chat_history.json"
        store = ChatHistoryStore(file_path=str(history_file))

        store.append_turn("user", "Tell me about Philia")
        store.append_turn("companion", "Philia is deep friendship.")

        md = store.export_markdown()
        assert "# Lucia — Conversation History Log" in md
        assert "👤 **User**" in md
        assert "Tell me about Philia" in md
        assert "✨ **Lucia**" in md
        assert "Philia is deep friendship." in md

    def test_corrupted_turns_as_string_handled_gracefully(self, tmp_path):
        import json
        history_file = tmp_path / "chat_history.json"
        corrupted_data = {
            "version": 1,
            "sessions": [
                {
                    "id": "session_test",
                    "turns": "this_is_a_string_instead_of_a_list"
                }
            ]
        }
        with open(history_file, "w", encoding="utf-8") as f:
            json.dump(corrupted_data, f)

        store = ChatHistoryStore(file_path=str(history_file))
        store._current_session_id = "session_test"

        # Appending should not crash with AttributeError: 'str' object has no attribute 'append'
        turn = store.append_turn("user", "Hello again")
        assert turn["content"] == "Hello again"
        assert len(store.get_history()) == 1

    def test_corrupted_sessions_as_string_handled_gracefully(self, tmp_path):
        import json
        history_file = tmp_path / "chat_history.json"
        corrupted_data = {
            "version": 1,
            "sessions": "invalid_sessions_string"
        }
        with open(history_file, "w", encoding="utf-8") as f:
            json.dump(corrupted_data, f)

        store = ChatHistoryStore(file_path=str(history_file))
        turn = store.append_turn("user", "Hello")
        assert turn["content"] == "Hello"
        assert len(store.get_history()) == 1
