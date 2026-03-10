"""
Central registry of all game event data-classes.

Keeping every event in one file makes it easy to:
  - see all events the game can produce at a glance
  - avoid circular imports (events have no game-logic dependencies)
  - map to C# event/delegate signatures during Unity migration

Adding a new event = add a class here, emit it, subscribe wherever needed.
"""

from dataclasses import dataclass


@dataclass(frozen=True)
class EntityClearedEvent:
    """
    Emitted by Cell when an entity (overlay / occupant / underlay)
    is fully destroyed and removed from its slot.

    `entity` is the actual CellEntity instance that was removed —
    subscribers can isinstance-check it to react to specific types.
    """
    entity: object  # CellEntity — avoid circular import with a loose type here


# ── Future events (not yet wired, shown as examples) ──────────────────

@dataclass(frozen=True)
class MatchResolvedEvent:
    """Emitted after a match group is processed."""
    cells_removed: frozenset
    combo_count: int


@dataclass(frozen=True)
class CascadeCompleteEvent:
    """Emitted when the board reaches a stable state after cascading."""
    pass


@dataclass(frozen=True)
class MoveConsumedEvent:
    """Emitted when the player successfully spends a move."""
    moves_remaining: int
