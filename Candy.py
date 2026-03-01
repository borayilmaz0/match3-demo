# ===== Candy.py =====
from BasicMatchable import BasicMatchable
from CandyType import CandyType
from CellOccupant import CellOccupant
from ColorType import ColorType
from BasicSwappable import BasicSwappable
from BasicDamageReflecting import BasicDamageReflecting
from BasicCascading import BasicCascading
from BasicDamageable import BasicDamageable
from DamageType import DamageType


class Candy(CellOccupant):
    __slots__ = ("color", "type")

    def __init__(self, color: ColorType, type: CandyType = CandyType.NORMAL):
        super().__init__()  # IMPORTANT: initializes _behaviors

        self.color = color
        self.type = type

        # ----- default behaviors -----
        self.add_behavior(BasicSwappable())
        self.add_behavior(BasicCascading())
        self.add_behavior(BasicDamageReflecting())

        # basic candies are destroyed by normal match damage
        self.add_behavior(
            BasicDamageable(
                hp=1,
                allowed_minimum=DamageType.MATCH
            )
        )

        # ----- special candy overrides -----
        self._configure_by_type()

    def _configure_by_type(self):
        """
        Modify or replace behaviors depending on candy type.
        This is intentionally simple for now.
        """
        return

    def is_special(self) -> bool:
        return self.type != CandyType.NORMAL

    def __str__(self):
        return f"{self.type.name}-{self.color.name}"

    def __eq__(self, other):
        return (
            isinstance(other, Candy)
            and self.color == other.color
            and self.type == other.type
        )