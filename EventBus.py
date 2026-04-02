from collections import defaultdict
from typing import Callable, Type


class EventBus:
    def __init__(self):
        self._handlers: dict[Type, list[Callable]] = defaultdict(list)
        self._history: list[object] = []

    def subscribe(self, event_type: Type, handler: Callable) -> None:
        if handler not in self._handlers[event_type]:
            self._handlers[event_type].append(handler)

    def unsubscribe(self, event_type: Type, handler: Callable) -> None:
        handlers = self._handlers.get(event_type, [])
        if handler in handlers:
            handlers.remove(handler)

    def emit(self, event) -> None:
        self._history.append(event)
        for handler in list(self._handlers.get(type(event), [])):
            handler(event)

    def emit_many(self, events) -> None:
        for event in events:
            self.emit(event)

    def drain_history(self) -> list[object]:
        history = list(self._history)
        self._history.clear()
        return history

    def clear(self) -> None:
        self._handlers.clear()
        self._history.clear()
