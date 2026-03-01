from BoardElement import BoardElement
from DamageContext import DamageContext


class GapCell(BoardElement):

    def can_fall_through(self) -> bool:
        return True

    def __str__(self):
        return "-"*27

    def can_spawn(self) -> bool:
        return False

    def can_hold_occupant(self) -> bool:
        return False

    def can_use_cell_occupant(self):
        return False

    def can_swap(self) -> bool:
        return False

    def apply_damage(self, ctx: DamageContext):
        ...

    def _remove_entity(self, entity):
        ...