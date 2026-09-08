"""
Unit tests for StoragePolicy, InMemoryChatHistoryStore, and InMemoryProfileStore.

Phase 8.6 — Level 0 / Level 1 isolation tests.

Verifies:
- StoragePolicy blocks writes to protected production paths in simulation mode.
- StoragePolicy allows all writes in live mode.
- InMemoryChatHistoryStore: append, get, clear, add_turn, export_markdown.
- InMemoryProfileStore: get, save, update, is_onboarded, reset, activation guard.
"""

from __future__ import annotations

import threading
from pathlib import Path

import pytest

from src.core.simulation.storage_policy import (
    ActivationSafetyError,
    InMemoryChatHistoryStore,
    InMemoryProfileStore,
    StoragePolicy,
)


# ---------------------------------------------------------------------------
# StoragePolicy
# ---------------------------------------------------------------------------

class TestStoragePolicy:
    def test_simulation_mode_is_reported(self):
        policy = StoragePolicy(is_simulation=True)
        assert policy.is_simulation is True

    def test_live_mode_is_reported(self):
        policy = StoragePolicy(is_simulation=False)
        assert policy.is_simulation is False

    def test_live_mode_allows_any_write(self):
        policy = StoragePolicy(is_simulation=False)
        # Must NOT raise even for protected paths
        policy.assert_write_permitted(Path("data/chat_history.json"))
        policy.assert_write_permitted(Path("data/profile.json"))
        policy.assert_write_permitted(None)

    def test_simulation_mode_allows_write_to_unprotected_path(self):
        policy = StoragePolicy(is_simulation=True)
        policy.assert_write_permitted(Path("some/other/file.json"))

    def test_simulation_mode_blocks_chat_history(self):
        policy = StoragePolicy(is_simulation=True)
        with pytest.raises(ActivationSafetyError, match="protected production file"):
            policy.assert_write_permitted(Path("data/chat_history.json").resolve())

    def test_simulation_mode_blocks_profile_json(self):
        policy = StoragePolicy(is_simulation=True)
        with pytest.raises(ActivationSafetyError, match="protected production file"):
            policy.assert_write_permitted(Path("data/profile.json").resolve())

    def test_simulation_mode_allows_none_path(self):
        """No-path call must not raise in simulation mode; it is a generic write-intent check."""
        policy = StoragePolicy(is_simulation=True)
        policy.assert_write_permitted(None)

    def test_activation_safety_error_is_runtime_error(self):
        assert issubclass(ActivationSafetyError, RuntimeError)


# ---------------------------------------------------------------------------
# InMemoryChatHistoryStore
# ---------------------------------------------------------------------------

class TestInMemoryChatHistoryStore:
    def test_initial_state_has_empty_turns(self):
        store = InMemoryChatHistoryStore()
        turns = store.get_turns()
        assert isinstance(turns, list)
        assert len(turns) == 0

    def test_append_turn_adds_entries(self):
        store = InMemoryChatHistoryStore()
        store.append_turn("user", "Hello Lucia")
        turns = store.get_turns()
        assert len(turns) == 1
        assert turns[0]["role"] == "user"
        assert turns[0]["content"] == "Hello Lucia"

    def test_append_multiple_roles(self):
        store = InMemoryChatHistoryStore()
        store.append_turn("user", "Msg 1")
        store.append_turn("assistant", "Reply 1")
        turns = store.get_turns()
        assert len(turns) == 2
        assert turns[0]["role"] == "user"
        assert turns[1]["role"] == "assistant"

    def test_get_turns_limit_is_respected(self):
        store = InMemoryChatHistoryStore()
        for i in range(20):
            store.append_turn("user", f"msg {i}")
        limited = store.get_turns(limit=5)
        assert len(limited) == 5
        assert limited[-1]["content"] == "msg 19"

    def test_add_turn_records_user_and_assistant(self):
        store = InMemoryChatHistoryStore()
        turn_id = store.add_turn(
            user_input="Good morning",
            response_text="Good morning, observer",
            pad_before={"pleasure": 0.25, "arousal": -0.05, "dominance": 0.05},
            pad_after={"pleasure": 0.30, "arousal": 0.00, "dominance": 0.08},
        )
        assert turn_id is not None
        turns = store.get_turns()
        assert len(turns) == 2
        assert turns[0]["content"] == "Good morning"
        assert turns[1]["content"] == "Good morning, observer"

    def test_clear_removes_all_turns(self):
        store = InMemoryChatHistoryStore()
        store.append_turn("user", "Test")
        assert len(store.get_turns()) > 0
        store.clear()
        assert store.get_turns() == []

    def test_clear_history_alias(self):
        store = InMemoryChatHistoryStore()
        store.append_turn("user", "Test")
        store.clear_history()
        assert store.get_turns() == []

    def test_export_markdown_contains_session_header(self):
        store = InMemoryChatHistoryStore()
        store.append_turn("user", "Hello")
        md = store.export_markdown()
        assert "## Session:" in md
        assert "Hello" in md

    def test_thread_safe_concurrent_writes(self):
        store = InMemoryChatHistoryStore()
        errors = []

        def write_many(n):
            try:
                for i in range(n):
                    store.append_turn("user", f"concurrent msg {i}")
            except Exception as e:
                errors.append(e)

        threads = [threading.Thread(target=write_many, args=(50,)) for _ in range(4)]
        for t in threads:
            t.start()
        for t in threads:
            t.join()

        assert not errors
        assert len(store.get_turns(limit=200)) == 200

    def test_new_session_resets_active_session(self):
        store = InMemoryChatHistoryStore()
        store.append_turn("user", "pre-session msg")
        session_id = store.new_session()
        assert isinstance(session_id, str)
        assert session_id.startswith("sim_session_")
        turns = store.get_turns()
        assert any(t["content"] == "pre-session msg" for t in turns)


# ---------------------------------------------------------------------------
# InMemoryProfileStore
# ---------------------------------------------------------------------------

class TestInMemoryProfileStore:
    def test_default_profile_structure(self):
        store = InMemoryProfileStore()
        profile = store.get_profile()
        assert profile["user_name"] == "Developer"
        assert profile["companion_name"] == "Lucia (Sim)"
        assert profile["is_onboarded"] is False
        assert profile["born_at"] is None

    def test_is_onboarded_returns_false_by_default(self):
        store = InMemoryProfileStore()
        assert store.is_onboarded() is False

    def test_save_profile_updates_fields(self):
        store = InMemoryProfileStore()
        store.save_profile({"user_name": "Alice", "is_onboarded": True})
        profile = store.get_profile()
        assert profile["user_name"] == "Alice"
        assert profile["is_onboarded"] is True
        assert store.is_onboarded() is True

    def test_update_profile_merges_fields(self):
        store = InMemoryProfileStore()
        store.update_profile(user_name="Bob")
        assert store.get_profile()["user_name"] == "Bob"
        assert store.get_profile()["companion_name"] == "Lucia (Sim)"

    def test_update_profile_blocks_live_awakening(self):
        """Setting is_onboarded=True via update_profile MUST raise ActivationSafetyError."""
        store = InMemoryProfileStore()
        with pytest.raises(ActivationSafetyError, match="simulation mode"):
            store.update_profile(is_onboarded=True)

    def test_save_profile_does_not_raise_for_is_onboarded(self):
        """save_profile is a lower-level direct setter with no safety guard."""
        store = InMemoryProfileStore()
        store.save_profile({"is_onboarded": True})
        assert store.is_onboarded() is True

    def test_reset_restores_defaults(self):
        store = InMemoryProfileStore()
        store.save_profile({"user_name": "Custom", "is_onboarded": True})
        assert store.is_onboarded() is True
        store.reset()
        assert store.is_onboarded() is False
        assert store.get_profile()["user_name"] == "Developer"

    def test_get_profile_returns_copy(self):
        """Mutating the returned dict must not affect internal state."""
        store = InMemoryProfileStore()
        profile = store.get_profile()
        profile["user_name"] = "Mutated"
        assert store.get_profile()["user_name"] == "Developer"

    def test_update_profile_skips_none_values(self):
        store = InMemoryProfileStore()
        store.update_profile(user_name=None)
        assert store.get_profile()["user_name"] == "Developer"
