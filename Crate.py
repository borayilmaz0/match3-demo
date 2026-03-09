# ===== Crate.py =====

from CellOccupant import CellOccupant
from BasicSwappable import BasicSwappable
from BasicCascading import BasicCascading
from BasicDamageable import BasicDamageable
from DamageType import DamageType
from Damageable import Damageable


class Crate(CellOccupant):

    def __init__(self, hp: int = 1):
        super().__init__()
        self.add_behavior(BasicSwappable())
        self.add_behavior(BasicCascading())
        self.add_behavior(
            BasicDamageable(hp=hp, allowed_minimum=DamageType.MATCH_NEAR)
        )

    def __str__(self) -> str:
        return f"CRATE({self.get(Damageable).hp})"
