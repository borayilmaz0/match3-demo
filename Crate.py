# ===== Crate.py =====

from CellOccupant import CellOccupant
from BasicSwappable import BasicSwappable
from BasicCascading import BasicCascading
from BasicDamageable import BasicDamageable
from DamageType import DamageType
from Damageable import Damageable


class Crate(CellOccupant):
    __slots__ = ("hp",)

    def __init__(self, hp: int = 1):
        super().__init__()  # initializes _behaviors

        self.hp = hp

        # ----- behaviors -----
        self.add_behavior(BasicSwappable())
        self.add_behavior(BasicCascading())
        self.add_behavior(
            BasicDamageable(
                hp=hp,
                allowed_minimum=DamageType.MATCH_NEAR
            )
        )

    def __str__(self):
        return f"CRATE({self.get(Damageable).hp})"