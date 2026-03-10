from abc import abstractmethod, ABC

from Behavior import Behavior
from DamageContext import DamageContext


class Damageable(ABC, Behavior):
    @abstractmethod
    def can_take_damage(self, ctx: DamageContext) -> bool:
        pass

    @abstractmethod
    def take_damage(self, ctx: DamageContext):
        pass

    @abstractmethod
    def is_destroyed(self) -> bool:
        pass
