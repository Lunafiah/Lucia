"""Chat history persistence with open-ended schema and Markdown export."""
import json
import logging
import os
import threading
import time
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional

logger = logging.getLogger(__name__)


class ChatHistoryStore:
    """Manages persistent conversation history across sessions."""

    def __init__(self, file_path: str = "data/chat_history.json") -> None:
        self.file_path = Path(file_path)
        self._lock = threading.Lock()
        self._current_session_id = self._generate_session_id()
        self._ensure_file_exists()

    def _generate_session_id(self) -> str:
        return f"session_{datetime.now().strftime('%Y%m%d_%H%M%S')}"

    def _ensure_file_exists(self) -> None:
        if not self.file_path.parent.exists():
            self.file_path.parent.mkdir(parents=True, exist_ok=True)

        if not self.file_path.exists():
            initial_data = {
                "version": 1,
                "metadata": {"created_at": datetime.now().isoformat()},
                "sessions": [
                    {
                        "id": self._current_session_id,
                        "created_at": datetime.now().isoformat(),
                        "turns": []
                    }
                ]
            }
            with self._lock:
                with open(self.file_path, "w", encoding="utf-8") as f:
                    json.dump(initial_data, f, indent=2, ensure_ascii=False)

    def _read_data(self) -> Dict[str, Any]:
        try:
            with open(self.file_path, "r", encoding="utf-8") as f:
                data = json.load(f)
                if isinstance(data, dict):
                    return data
                return {"version": 1, "metadata": {}, "sessions": []}
        except Exception as e:
            logger.error("Failed to read chat history: %s", e)
            return {"version": 1, "metadata": {}, "sessions": []}

    def _write_data(self, data: Dict[str, Any]) -> None:
        try:
            with open(self.file_path, "w", encoding="utf-8") as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
        except Exception as e:
            logger.error("Failed to write chat history: %s", e)

    def append_turn(
        self,
        role: str,
        content: str,
        metadata: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Append a user or companion turn to the active session."""
        turn = {
            "role": role,
            "content": content,
            "timestamp": time.time(),
            "created_at": datetime.now().isoformat(),
            "metadata": metadata or {}
        }

        with self._lock:
            data = self._read_data()
            if not isinstance(data, dict):
                data = {"version": 1, "metadata": {}, "sessions": []}

            sessions = data.setdefault("sessions", [])
            if not isinstance(sessions, list):
                sessions = []
                data["sessions"] = sessions

            # Find active session or create it
            active_session = None
            for s in sessions:
                if isinstance(s, dict) and s.get("id") == self._current_session_id:
                    active_session = s
                    break

            if active_session is None:
                active_session = {
                    "id": self._current_session_id,
                    "created_at": datetime.now().isoformat(),
                    "turns": []
                }
                sessions.append(active_session)

            if not isinstance(active_session.get("turns"), list):
                active_session["turns"] = []

            active_session["turns"].append(turn)
            self._write_data(data)

        return turn

    def get_history(self, limit: int = 50) -> List[Dict[str, Any]]:
        """Retrieve recent conversation turns across all sessions or current session."""
        with self._lock:
            data = self._read_data()
            all_turns = []
            sessions = data.get("sessions", []) if isinstance(data, dict) else []
            if isinstance(sessions, list):
                for s in sessions:
                    if isinstance(s, dict):
                        turns = s.get("turns", [])
                        if isinstance(turns, list):
                            all_turns.extend(turns)
            return all_turns[-limit:]

    def new_session(self) -> str:
        """Start a new session without erasing older session histories."""
        with self._lock:
            self._current_session_id = self._generate_session_id()
            data = self._read_data()
            if not isinstance(data, dict):
                data = {"version": 1, "metadata": {}, "sessions": []}
            sessions = data.setdefault("sessions", [])
            if not isinstance(sessions, list):
                sessions = []
                data["sessions"] = sessions
            sessions.append({
                "id": self._current_session_id,
                "created_at": datetime.now().isoformat(),
                "turns": []
            })
            self._write_data(data)
        return self._current_session_id

    def clear_history(self) -> None:
        """Clear all stored chat history."""
        with self._lock:
            self._current_session_id = self._generate_session_id()
            data = {
                "version": 1,
                "metadata": {"cleared_at": datetime.now().isoformat()},
                "sessions": [
                    {
                        "id": self._current_session_id,
                        "created_at": datetime.now().isoformat(),
                        "turns": []
                    }
                ]
            }
            self._write_data(data)

    def export_markdown(self) -> str:
        """Export all conversation history formatted as a beautiful Markdown document."""
        with self._lock:
            data = self._read_data()

        lines = [
            "# Lucia — Conversation History Log",
            f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
            "",
            "---",
            ""
        ]

        sessions = data.get("sessions", []) if isinstance(data, dict) else []
        if isinstance(sessions, list):
            for s in sessions:
                if not isinstance(s, dict):
                    continue
                lines.append(f"## Session: `{s.get('id', 'unknown')}` ({s.get('created_at', '')})")
                lines.append("")
                turns = s.get("turns", [])
                if isinstance(turns, list):
                    for turn in turns:
                        if not isinstance(turn, dict):
                            continue
                        role_label = "👤 **User**" if turn.get("role") == "user" else "✨ **Lucia**"
                        ts = turn.get("created_at", "")
                        content = turn.get("content", "")
                        lines.append(f"{role_label} *({ts})*:")
                        lines.append(f"> {content}")
                        lines.append("")
                lines.append("---")
                lines.append("")

        return "\n".join(lines)
