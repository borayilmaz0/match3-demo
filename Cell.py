from BasicDamageable import BasicDamageable
from BoardElement import BoardElement
from CellOccupant import CellOccupant
from CellOverlay import CellOverlay
from CellUnderlay import CellUnderlay
from DamageContext import DamageContext
from DamageReflecting import DamageReflecting
from Damageable import Damageable
from MatchBlocking import MatchBlocking
from Swappable import Swappable
from CellEntityClearedEvent import CellEntityClearedEvent


class Cell(BoardElement):
    __slots__ = ("occupant", "overlay", "underlay", "_listeners")

    def __init__(self, occupant: CellOccupant = None, overlay: CellOverlay = None, underlay: CellUnderlay = None, _listeners: list = None):
        self.occupant = occupant
        self.overlay = overlay
        self.underlay = underlay
        self._listeners = []

    def add_listener(self, listener):
        self._listeners.append(listener)

    def __str__(self):
        return f"{str(self.occupant):>17}|{str(self.overlay)[:5]}|{str(self.underlay)[:5]}"

    # ---------- basic state ----------

    def is_empty(self) -> bool:
        return self.occupant is None

    def can_fall_through(self) -> bool:
        return False

    def can_spawn(self) -> bool:
        return True

    def can_hold_occupant(self) -> bool:
        return True

    def can_use_cell_occupant(self):
        # If an overlay blocks matching, the occupant should not be visible to
        # match/deadlock detection (Board.get_occupant will return None).
        if self.overlay:
            blocker_overlay = self.overlay.get(MatchBlocking)
            if blocker_overlay and blocker_overlay.blocks_matching():
                return False
        return True

    # ---------- swap logic ----------

    def can_swap(self) -> bool:
        # overlay may block swaps
        if self.overlay:
            sw = self.overlay.get(Swappable)
            if sw and not sw.can_swap():
                return False

        # occupant must be swappable
        if self.occupant:
            sw = self.occupant.get(Swappable)
            if sw and not sw.can_swap():
                return False

        return True

    # ---------- damage routing ----------

    def apply_damage(self, ctx: DamageContext, event_sink = None):
        """
        Damage priority:
        overlay -> occupant -> underlay
        """
        for entity in (self.overlay, self.occupant, self.underlay):
            if not entity:
                continue

            dmg = entity.get(Damageable)
            if not dmg or not dmg.can_take_damage(ctx):
                continue

            # Apply damage
            dmg.take_damage(ctx)

            # Remove if destroyed
            if dmg.is_destroyed():
                self._remove_entity(entity)

            # Decide whether damage continues
            reflector = entity.get(DamageReflecting)
            if not reflector or not reflector.can_reflect_damage():
                break


    # ---------- helpers ----------

    def _remove_entity(self, entity):
        if entity is self.overlay:
            self.overlay = None
        elif entity is self.occupant:
            self.occupant = None  # ✅ FIX
        elif entity is self.underlay:
            self.underlay = None  # ✅ FIX

        # 🔔 notify listeners AFTER removal
        for listener in self._listeners:
            listener.on_entity_cleared(entity)
