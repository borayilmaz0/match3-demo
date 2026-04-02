from collections import deque
from dataclasses import dataclass, field
from enum import Enum, auto


class EffectTiming(Enum):
    IMMEDIATE = auto()
    POST_FALL = auto()
    POST_SPAWN = auto()


@dataclass(frozen=True)
class Effect:
    kind: str
    payload: dict = field(default_factory=dict)
    timing: EffectTiming = EffectTiming.IMMEDIATE


class EffectQueue:
    def __init__(self):
        self._queues = {
            EffectTiming.IMMEDIATE: deque(),
            EffectTiming.POST_FALL: deque(),
            EffectTiming.POST_SPAWN: deque(),
        }

    def push(self, effect: Effect) -> None:
        self._queues[effect.timing].append(effect)

    def extend(self, effects) -> None:
        for effect in effects:
            self.push(effect)

    def pop_next(self):
        for timing in (EffectTiming.IMMEDIATE, EffectTiming.POST_FALL, EffectTiming.POST_SPAWN):
            queue = self._queues[timing]
            if queue:
                return queue.popleft()
        return None

    def has_pending(self) -> bool:
        return any(self._queues[t] for t in self._queues)

    def clear(self) -> None:
        for queue in self._queues.values():
            queue.clear()
