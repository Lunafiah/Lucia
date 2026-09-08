"""
StoragePolicy & In-Memory Adapters for Runtime Isolation (Phase 8).

Guarantees Zero Live Data Contamination (INV-2) by providing pure in-memory
stores for chat history and profile state, and enforcing that production storage
paths (data/chat_history.json, data/profile.json) are never opened or modified.
"""

from __future__ import annotations

from datetime import datetime
import json
import logging
from pathlib import Path
import threading
from typing import Any, Dict, List, Optional

logger = logging.getLogger("lucia.simulation.storage_policy")


class ActivationSafetyError(RuntimeError):
    """Raised when an operation attempts to activate Lucia or mutate live data in simulation mode."""
    pass


class StoragePolicy:
    """
    Guards access to storage resources based on active runtime mode.
    """

    def __init__(self, is_simulation: bool = False) -> None:
        self._is_simulation = is_simulation
        self._protected_paths = [
            Path("data/chat_history.json").resolve(),
            Path("data/profile.json").resolve(),
        ]

    @property
    def is_simulation(self) -> bool:
        return self._is_simulation

    def assert_write_permitted(self, target_path: Optional[Path] = None) -> None:
        """
        Assert that writing to target_path is permitted under the active policy.
        Raises ActivationSafetyError if attempting to write to live files in simulation mode.
        """
        if not self._is_simulation:
            return

        if target_path is not None:
            resolved = Path(target_path).resolve()
            for protected in self._protected_paths:
                if resolved == protected or protected in resolved.parents:
                    raise ActivationSafetyError(
                        f"StoragePolicy violation: attempt to write to protected production file '{resolved}' in simulation mode."
                    )


class InMemoryChatHistoryStore:
    """
    Thread-safe, RAM-only drop-in replacement for ChatHistoryStore.
    Guarantees that simulation conversation turns never touch data/chat_history.json.
    """

    def __init__(self) -> None:
        self._lock = threading.RLock()
        self._sessions: List[Dict[str, Any]] = []
        self._active_session_id: Optional[str] = None
        self.new_session()

    def new_session(self) -> str:
        with self._lock:
            session_id = f"sim_session_{datetime.now().strftime('%Y%m%d_%H%M%S_%f')}"
            self._active_session_id = session_id
            self._sessions.append({
                "id": session_id,
                "created_at": datetime.now().isoformat(),
                "turns": [],
            })
            return session_id

    def append_turn(
        self,
        role: str,
        content: str,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> None:
        with self._lock:
            if not self._sessions:
                self.new_session()
            active_session = self._sessions[-1]
            turn = {
                "role": role,
                "content": content,
                "timestamp": datetime.now().timestamp(),
                "created_at": datetime.now().isoformat(),
                "metadata": metadata or {},
            }
            active_session["turns"].append(turn)

    def get_history(self, limit: int = 50) -> List[Dict[str, Any]]:
        with self._lock:
            all_turns: List[Dict[str, Any]] = []
            for s in self._sessions:
                all_turns.extend(s.get("turns", []))
            return all_turns[-limit:]

    def clear_history(self) -> None:
        with self._lock:
            self._sessions.clear()
            self.new_session()

    clear = clear_history
    get_turns = get_history

    def add_turn(
        self,
        user_input: str,
        response_text: str,
        pad_before: Optional[Dict[str, float]] = None,
        pad_after: Optional[Dict[str, float]] = None,
    ) -> str:
        with self._lock:
            self.append_turn("user", user_input, {"pad_before": pad_before})
            self.append_turn("assistant", response_text, {"pad_after": pad_after})
            return f"turn_{len(self.get_history())}"

    def export_markdown(self) -> str:
        with self._lock:
            lines = ["# Simulated Conversation History\n"]
            for s in self._sessions:
                lines.append(f"## Session: {s['id']}\n")
                for t in s.get("turns", []):
                    role = "**User**" if t["role"] == "user" else "**Lucia (Sim)**"
                    lines.append(f"{role}: {t['content']}\n")
            return "\n".join(lines)


class InMemoryProfileStore:
    """
    RAM-only drop-in replacement for profile storage in simulation mode.
    Guarantees that simulation identity state never touches data/profile.json.
    """

    def __init__(self) -> None:
        self._lock = threading.RLock()
        self._profile: Dict[str, Any] = {
            "version": 1,
            "user_name": "Developer",
            "companion_name": "Lucia (Sim)",
            "born_at": None,
            "is_onboarded": False,
            "pronouns": "they/them",
            "avatar_engine": "canvas",
            "avatar_model": "default",
        }

    def get_profile(self) -> Dict[str, Any]:
        with self._lock:
            return dict(self._profile)

    def is_onboarded(self) -> bool:
        with self._lock:
            return bool(self._profile.get("is_onboarded", False))

    def save_profile(self, data: Dict[str, Any]) -> None:
        with self._lock:
            self._profile.update(data)

    def update_profile(self, **kwargs: Any) -> Dict[str, Any]:
        with self._lock:
            # Block live awakening attempts
            if kwargs.get("is_onboarded") is True:
                raise ActivationSafetyError(
                    "Cannot awaken live companion in simulation mode: is_onboarded=True forbidden."
                )
            for k, v in kwargs.items():
                if v is not None:
                    self._profile[k] = v
            return dict(self._profile)

    def reset(self) -> None:
        with self._lock:
            self._profile = {
                "version": 1,
                "user_name": "Developer",
                "companion_name": "Lucia (Sim)",
                "born_at": None,
                "is_onboarded": False,
                "pronouns": "they/them",
                "avatar_engine": "canvas",
                "avatar_model": "default",
            }
