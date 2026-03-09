
from BasicDamageable import BasicDamageable
from CellUnderlay import CellUnderlay
from DamageType import DamageType
from Damageable import Damageable


class Snow(CellUnderlay):

    def __init__(self, hp: int = 2):
        super().__init__()
        self.add_behavior(
            BasicDamageable(hp=hp, allowed_minimum=DamageType.MATCH)
        )

    def __str__(self) -> str:
        return f"SNOW{self.get(Damageable).hp}"