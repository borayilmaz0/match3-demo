# ===== Candy.py =====
from abc import ABC

from BasicMatchable import BasicMatchable
from CandyType import CandyType
from CellOccupant import CellOccupant
from ColorType import ColorType
from BasicSwappable import BasicSwappable
from BasicDamageReflecting import BasicDamageReflecting
from BasicCascading import BasicCascading
from BasicDamageable import BasicDamageable
from DamageType import DamageType


class Candy(CellOccupant, ABC):
    """
    Abstract candy base class.

    Cells should only ever hold concrete candy subclasses such as:
    - NormalCandy
    - RocketHCandy
    - RocketVCandy
    - BombCandy
    - LightBallCandy
    - PropellerCandy
    """

    __slots__ = ("color",)
    candy_type = None

    def __init__(self, color: ColorType):
        if type(self) is Candy:
            raise TypeError("Candy is abstract and cannot be instantiated directly")

        super().__init__()
        self.color = color

        self.add_behavior(BasicMatchable())
        self.add_behavior(BasicSwappable())
        self.add_behavior(BasicCascading())
        self.add_behavior(BasicDamageReflecting())
        self.add_behavior(
            BasicDamageable(
                hp=1,
                allowed_minimum=DamageType.MATCH,
            )
        )

    @property
    def type(self) -> CandyType:
        if self.candy_type is None:
            raise NotImplementedError(
                f"{type(self).__name__} must define candy_type"
            )
        return self.candy_type

    def is_special(self) -> bool:
        raise NotImplementedError(
            f"{type(self).__name__} must implement is_special()"
        )

    def is_normal(self) -> bool:
        return not self.is_special()

    def on_swap(self, special_logic, pos, neighbor_candy) -> bool:
        """Hook for explicit swap activation."""
        return False

    def on_hit(self, special_logic, pos) -> bool:
        """Hook for indirect activation from another effect."""
        return False

    def __str__(self):
        return f"{self.type.name}-{self.color.name}"

    def __eq__(self, other):
        return (
            isinstance(other, Candy)
            and type(self) is type(other)
            and self.color == other.color
        )




class NormalCandy(Candy):
    candy_type = CandyType.NORMAL

    def is_special(self) -> bool:
        return False


class SpecialCandy(Candy, ABC):
    def is_special(self) -> bool:
        return True


class RocketHCandy(SpecialCandy):
    candy_type = CandyType.ROCKET_H

    def on_swap(self, special_logic, pos, neighbor_candy) -> bool:
        special_logic.trigger_rocket(pos, horizontal=True)
        return True

    def on_hit(self, special_logic, pos) -> bool:
        special_logic.trigger_rocket(pos, horizontal=True)
        return True


class RocketVCandy(SpecialCandy):
    candy_type = CandyType.ROCKET_V

    def on_swap(self, special_logic, pos, neighbor_candy) -> bool:
        special_logic.trigger_rocket(pos, horizontal=False)
        return True

    def on_hit(self, special_logic, pos) -> bool:
        special_logic.trigger_rocket(pos, horizontal=False)
        return True


class BombCandy(SpecialCandy):
    candy_type = CandyType.BOMB

    def on_swap(self, special_logic, pos, neighbor_candy) -> bool:
        special_logic.trigger_bomb(pos)
        return True

    def on_hit(self, special_logic, pos) -> bool:
        special_logic.trigger_bomb(pos)
        return True


class LightBallCandy(SpecialCandy):
    candy_type = CandyType.LIGHT_BALL

    def on_swap(self, special_logic, pos, neighbor_candy) -> bool:
        if neighbor_candy is None:
            return False
        return special_logic.trigger_light_ball_swap(pos, neighbor_candy)

    def on_hit(self, special_logic, pos) -> bool:
        return special_logic.trigger_light_ball_hit(pos)


class PropellerCandy(SpecialCandy):
    candy_type = CandyType.PROPELLER

    def on_swap(self, special_logic, pos, neighbor_candy) -> bool:
        special_logic.trigger_propeller(pos, pre_damage=True)
        return True

    def on_hit(self, special_logic, pos) -> bool:
        special_logic.trigger_propeller(pos, pre_damage=True)
        return True

class CandyFactory:
    @staticmethod
    def create(candy_type: CandyType, color: ColorType) -> Candy:
        mapping = {
            CandyType.NORMAL: NormalCandy,
            CandyType.ROCKET_H: RocketHCandy,
            CandyType.ROCKET_V: RocketVCandy,
            CandyType.BOMB: BombCandy,
            CandyType.LIGHT_BALL: LightBallCandy,
            CandyType.PROPELLER: PropellerCandy,
        }
        candy_cls = mapping.get(candy_type)
        if candy_cls is None:
            raise ValueError(f"Unsupported candy type: {candy_type}")
        return candy_cls(color)
