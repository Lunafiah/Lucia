"""Non-blocking, exception-safe cognitive lifecycle hook bus."""
import logging
from collections import defaultdict
from typing import Any, Callable, Dict, List, Tuple

logger = logging.getLogger(__name__)


class HookBus:
    """Non-blocking lifecycle hook and plugin bus.
    
    Allows external modules (e.g. screen vision, web search, custom logging)
    to hook into the 10-step cognitive pipeline cleanly.
    """

    def __init__(self) -> None:
        # Map: event_name -> list of (priority, callback)
        self._hooks: Dict[str, List[Tuple[int, Callable]]] = defaultdict(list)

    def register(self, event_name: str, callback: Callable, priority: int = 100) -> None:
        """Register a callback for an event. Lower priority values execute earlier."""
        self._hooks[event_name].append((priority, callback))
        self._hooks[event_name].sort(key=lambda x: x[0])

    def unregister(self, event_name: str, callback: Callable) -> bool:
        """Unregister a callback from an event. Returns True if removed."""
        initial_len = len(self._hooks[event_name])
        self._hooks[event_name] = [item for item in self._hooks[event_name] if item[1] != callback]
        return len(self._hooks[event_name]) < initial_len

    def emit(self, event_name: str, *args: Any, **kwargs: Any) -> None:
        """Emit an event to all registered listeners. Exceptions in listeners are caught and logged."""
        for _, cb in self._hooks.get(event_name, []):
            try:
                cb(*args, **kwargs)
            except Exception as e:
                logger.error("Error in hook '%s' (%s): %s", event_name, getattr(cb, '__name__', str(cb)), e, exc_info=True)

    def emit_filter(self, event_name: str, value: Any, *args: Any, **kwargs: Any) -> Any:
        """Pass a value through a chain of filter callbacks. Each callback returns the transformed value."""
        current_value = value
        for _, cb in self._hooks.get(event_name, []):
            try:
                res = cb(current_value, *args, **kwargs)
                if res is not None:
                    current_value = res
            except Exception as e:
                logger.error("Error in filter hook '%s': %s", event_name, e, exc_info=True)
        return current_value

    def clear(self) -> None:
        """Clear all registered hooks."""
        self._hooks.clear()

    @property
    def registered_events(self) -> List[str]:
        """Return a list of event names with at least one active listener."""
        return [k for k, v in self._hooks.items() if len(v) > 0]
