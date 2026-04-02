"""
Central registry of simulation events.
"""

from dataclasses import dataclass

from CandyType import CandyType
from CellEntity import CellEntity
from ColorType import ColorType
from DamageType import DamageType


class GameEvent:
    """Base class for all game events."""
    pass


@dataclass(frozen=True)
class EntityClearedEvent(GameEvent):
    entity: CellEntity
    position: tuple[int, int] | None = None
    layer: str | None = None


@dataclass(frozen=True)
class DamageRequestedEvent(GameEvent):
    position: tuple[int, int]
    damage_type: DamageType
    color: ColorType | None = None
    source: str | None = None
    chain_id: int | None = None


@dataclass(frozen=True)
class DamageAppliedEvent(GameEvent):
    position: tuple[int, int]
    damage_type: DamageType
    color: ColorType | None = None
    did_change: bool = False
    destroyed_layers: tuple[str, ...] = ()


@dataclass(frozen=True)
class MatchResolvedEvent(GameEvent):
    cells_removed: frozenset[tuple[int, int]]
    combo_count: int = 0
    spawn_pos: tuple[int, int] | None = None
    spawned_type: str | None = None


@dataclass(frozen=True)
class SpecialTriggeredEvent(GameEvent):
    position: tuple[int, int]
    candy_type: CandyType
    trigger: str


@dataclass(frozen=True)
class OccupantMovedEvent(GameEvent):
    from_pos: tuple[int, int]
    to_pos: tuple[int, int]
    entity: CellEntity


@dataclass(frozen=True)
class SpawnedEvent(GameEvent):
    position: tuple[int, int]
    entity: CellEntity


@dataclass(frozen=True)
class BoardPhaseChangedEvent(GameEvent):
    old_phase: str
    new_phase: str


@dataclass(frozen=True)
class BoardBecameStableEvent(GameEvent):
    pass


@dataclass(frozen=True)
class CascadeCompleteEvent(GameEvent):
    pass


@dataclass(frozen=True)
class MoveConsumedEvent(GameEvent):
    moves_remaining: int
