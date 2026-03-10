from Behavior import Behavior


class CellEntity:
    __slots__ = ("_behaviors",)

    def __init__(self):
        self._behaviors = {}

    def add_behavior(self, behavior: Behavior):
        self._behaviors[type(behavior)] = behavior

    def get(self, behavior_type):
        # exact match first (fast path)
        if behavior_type in self._behaviors:
            return self._behaviors[behavior_type]

        # fallback: find subclass
        for behavior in self._behaviors.values():
            if isinstance(behavior, behavior_type):
                return behavior

        return None

    def has(self, behavior_type) -> bool:
        return behavior_type in self._behaviors
