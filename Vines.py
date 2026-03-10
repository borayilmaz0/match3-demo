from BasicDamageable import BasicDamageable
from BasicMatchBlocking import BasicMatchBlocking
from CellOverlay import CellOverlay
from DamageType import DamageType
from LockedSwappable import LockedSwappable


class Vines(CellOverlay):

    def __init__(self):
        super().__init__()
        self.add_behavior(LockedSwappable())
        self.add_behavior(BasicMatchBlocking())
        self.add_behavior(
            BasicDamageable(hp=1, allowed_minimum=DamageType.MATCH_NEAR)
        )

    def __str__(self) -> str:
        return "VINES"
