from CandyType import CandyType
from CellOccupant import CellOccupant
from ColorType import ColorType
from BasicSwappable import BasicSwappable
from BasicDamageReflecting import BasicDamageReflecting
from BasicCascading import BasicCascading
from BasicDamageable import BasicDamageable
from BasicMatchable import BasicMatchable
from DamageType import DamageType


class Candy(CellOccupant):
    __slots__ = ("candy_type", "color")

    def __init__(self, candy_type: CandyType, color: ColorType):
        super().__init__()
        self.candy_type = candy_type
        self.color = color

        self.add_behavior(BasicSwappable())
        self.add_behavior(BasicCascading())
        self.add_behavior(BasicDamageReflecting())
        self.add_behavior(
            BasicDamageable(
                hp=1,
                allowed_minimum=DamageType.MATCH,
            )
        )

        if candy_type == CandyType.NORMAL:
            self.add_behavior(BasicMatchable())

    @property
    def type(self) -> CandyType:
        return self.candy_type

    def is_special(self) -> bool:
        return self.candy_type != CandyType.NORMAL

    def is_normal(self) -> bool:
        return self.candy_type == CandyType.NORMAL

    def __str__(self):
        return f"{self.candy_type.name}-{self.color.name}"

    def __eq__(self, other):
        return (
            isinstance(other, Candy)
            and self.candy_type == other.candy_type
            and self.color == other.color
        )


class CandyFactory:
    @staticmethod
    def create(candy_type: CandyType, color: ColorType) -> Candy:
        return Candy(candy_type, color)
