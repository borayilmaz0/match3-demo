from collections import defaultdict
from typing import Callable, Type


class EventBus:
    """
    Lightweight publish/subscribe event bus.

    Usage
    -----
    bus = EventBus()

    # subscribe
    bus.subscribe(EntityClearedEvent, my_handler)   # handler(event) -> None

    # emit
    bus.emit(EntityClearedEvent(entity))

    # unsubscribe (useful for level teardown)
    bus.unsubscribe(EntityClearedEvent, my_handler)
    """

    def __init__(self):
        # event_type -> list of callables
        self._handlers: dict[Type, list[Callable]] = defaultdict(list)

    def subscribe(self, event_type: Type, handler: Callable) -> None:
        if handler not in self._handlers[event_type]:
            self._handlers[event_type].append(handler)

    def unsubscribe(self, event_type: Type, handler: Callable) -> None:
        handlers = self._handlers.get(event_type, [])
        if handler in handlers:
            handlers.remove(handler)

    def emit(self, event) -> None:
        for handler in list(self._handlers.get(type(event), [])):
            handler(event)

    def clear(self) -> None:
        """Remove all subscriptions (call on level teardown)."""
        self._handlers.clear()
