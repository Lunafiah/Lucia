"""Unit tests for HookBus lifecycle and filter hooks."""
import pytest
from src.core.plugins.hook_bus import HookBus


class TestHookBus:
    def test_register_and_emit(self):
        bus = HookBus()
        events = []

        def on_turn(text):
            events.append(f"turn:{text}")

        bus.register("on_turn_start", on_turn)
        bus.emit("on_turn_start", "Hello Lucia")

        assert events == ["turn:Hello Lucia"]

    def test_priority_ordering(self):
        bus = HookBus()
        sequence = []

        bus.register("event", lambda: sequence.append("third"), priority=300)
        bus.register("event", lambda: sequence.append("first"), priority=10)
        bus.register("event", lambda: sequence.append("second"), priority=100)

        bus.emit("event")
        assert sequence == ["first", "second", "third"]

    def test_unregister(self):
        bus = HookBus()
        calls = []

        def my_listener():
            calls.append(1)

        bus.register("test", my_listener)
        bus.emit("test")
        assert len(calls) == 1

        assert bus.unregister("test", my_listener) is True
        bus.emit("test")
        assert len(calls) == 1

    def test_exception_safety(self):
        bus = HookBus()
        calls = []

        def buggy_listener():
            raise RuntimeError("Explosion in plugin!")

        def healthy_listener():
            calls.append("healthy")

        bus.register("test", buggy_listener, priority=10)
        bus.register("test", healthy_listener, priority=20)

        # Emit must not crash even when buggy_listener raises
        bus.emit("test")
        assert calls == ["healthy"]

    def test_emit_filter(self):
        bus = HookBus()

        def prefix_filter(text):
            return f"[AUGMENTED] {text}"

        def suffix_filter(text):
            return f"{text} (checked)"

        bus.register("prompt_filter", prefix_filter, priority=10)
        bus.register("prompt_filter", suffix_filter, priority=20)

        result = bus.emit_filter("prompt_filter", "Hello")
        assert result == "[AUGMENTED] Hello (checked)"
