"""
Central registry of simulation events.
"""

from dataclasses import dataclass
from typing import Any


@dataclass(frozen=True)
class EntityClearedEvent:
    entity: object
    position: tuple[int, int] | None = None
    layer: str | None = None


@dataclass(frozen=True)
class DamageRequestedEvent:
    position: tuple[int, int]
    damage_type: Any
    color: Any = None
    source: str | None = None
    chain_id: int | None = None


@dataclass(frozen=True)
class DamageAppliedEvent:
    position: tuple[int, int]
    damage_type: Any
    color: Any = None
    did_change: bool = False
    destroyed_layers: tuple[str, ...] = ()


@dataclass(frozen=True)
class MatchResolvedEvent:
    cells_removed: frozenset
    combo_count: int = 0
    spawn_pos: tuple[int, int] | None = None
    spawned_type: Any = None


@dataclass(frozen=True)
class SpecialTriggeredEvent:
    position: tuple[int, int]
    candy_type: Any
    trigger: str


@dataclass(frozen=True)
class OccupantMovedEvent:
    from_pos: tuple[int, int]
    to_pos: tuple[int, int]
    entity: object


@dataclass(frozen=True)
class SpawnedEvent:
    position: tuple[int, int]
    entity: object


@dataclass(frozen=True)
class BoardPhaseChangedEvent:
    old_phase: str
    new_phase: str


@dataclass(frozen=True)
class BoardBecameStableEvent:
    pass


@dataclass(frozen=True)
class CascadeCompleteEvent:
    pass


@dataclass(frozen=True)
class MoveConsumedEvent:
    moves_remaining: int
