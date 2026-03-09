from BoardElement import BoardElement
from DamageContext import DamageContext


class GapCell(BoardElement):
    """
    Represents a hole in the board layout.
    No occupant can be placed here, nothing can fall through,
    nothing can be spawned or swapped.
    """

    def can_spawn(self) -> bool:
        return False

    def can_hold_occupant(self) -> bool:
        return False

    def can_swap(self) -> bool:
        return False

    def apply_damage(self, ctx: DamageContext) -> None:
        pass   # gaps are indestructible

    def set_event_bus(self, event_bus) -> None:
        pass   # gaps never emit events; accept the call silently

    def __str__(self) -> str:
        return "-" * 27