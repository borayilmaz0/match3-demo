from abc import ABC, abstractmethod

from Behavior import Behavior


class DamageReflecting(ABC, Behavior):
    @abstractmethod
    def can_reflect_damage(self) -> bool:
        pass