from BoardElement import BoardElement
from CellOccupant import CellOccupant
from CellOverlay import CellOverlay
from CellUnderlay import CellUnderlay
from GameEvents import EntityClearedEvent
from MatchBlocking import MatchBlocking
from Swappable import Swappable


class Cell(BoardElement):
    __slots__ = ("occupant", "overlay", "underlay", "_event_bus")

    def __init__(self, occupant: CellOccupant = None, overlay: CellOverlay = None, underlay: CellUnderlay = None, event_bus=None):
        self.occupant = occupant
        self.overlay = overlay
        self.underlay = underlay
        self._event_bus = event_bus

    def set_event_bus(self, event_bus) -> None:
        self._event_bus = event_bus

    def __str__(self):
        return f"{str(self.occupant):>17}|{str(self.overlay)[:5]}|{str(self.underlay)[:5]}"

    def is_empty(self) -> bool:
        return self.occupant is None

    def can_fall_through(self) -> bool:
        return False

    def can_spawn(self) -> bool:
        return True

    def can_hold_occupant(self) -> bool:
        return True

    def can_use_cell_occupant(self):
        if self.overlay:
            blocker_overlay = self.overlay.get(MatchBlocking)
            if blocker_overlay and blocker_overlay.blocks_matching():
                return False
        return True

    def can_swap(self) -> bool:
        if self.overlay:
            sw = self.overlay.get(Swappable)
            if sw and not sw.can_swap():
                return False

        if self.occupant:
            sw = self.occupant.get(Swappable)
            if sw and not sw.can_swap():
                return False

        return True

    def entities(self):
        """Yields (layer_name, entity) in damage priority order."""
        for layer_name, entity in (
            ("overlay", self.overlay),
            ("occupant", self.occupant),
            ("underlay", self.underlay),
        ):
            if entity is not None:
                yield layer_name, entity

    def clear_occupant(self, pos=None) -> None:
        if self.occupant is not None:
            self.remove_entity(self.occupant, pos=pos, layer_name="occupant")

    def remove_entity(self, entity, pos=None, layer_name=None) -> None:
        if entity is self.overlay:
            self.overlay = None
            layer_name = layer_name or "overlay"
        elif entity is self.occupant:
            self.occupant = None
            layer_name = layer_name or "occupant"
        elif entity is self.underlay:
            self.underlay = None
            layer_name = layer_name or "underlay"
        else:
            # Unknown entity; do not emit a misleading "cleared" event.
            return

        if self._event_bus is not None:
            self._event_bus.emit(
                EntityClearedEvent(entity=entity, position=pos, layer=layer_name)
            )
