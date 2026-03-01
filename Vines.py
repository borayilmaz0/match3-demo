
from BasicDamageable import BasicDamageable
from BasicMatchBlocking import BasicMatchBlocking
from CellOverlay import CellOverlay
from DamageType import DamageType
from LockedSwappable import LockedSwappable


class Vines(CellOverlay):
    __slots__ = ("hp",)

    def __init__(self):
        super().__init__()  # initializes _behaviors

        self.hp = 1

        # ----- behaviors -----
        self.add_behavior(LockedSwappable())
        self.add_behavior(BasicMatchBlocking())
        self.add_behavior(
            BasicDamageable(
                hp=self.hp,
                allowed_minimum=DamageType.MATCH_NEAR
            )
        )

    def __str__(self):
        return f"VINES"