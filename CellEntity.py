from Behavior import Behavior


class CellEntity:
    __slots__ = ("_behaviors",)

    def __init__(self):
        self._behaviors = {}

    def add_behavior(self, behavior: Behavior):
        for cls in type(behavior).__mro__:
            if cls is Behavior or cls is object:
                continue
            if issubclass(cls, Behavior):
                self._behaviors[cls] = behavior

    def get(self, behavior_type):
        return self._behaviors.get(behavior_type)

    def has(self, behavior_type) -> bool:
        return behavior_type in self._behaviors
