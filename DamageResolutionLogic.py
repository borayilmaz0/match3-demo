from Damageable import Damageable
from DamageContext import DamageContext
from DamageReflecting import DamageReflecting
from DamageType import DamageType
from MatchResult import MatchResult
from GameEvents import DamageRequestedEvent, DamageAppliedEvent, MatchResolvedEvent


class DamageResolutionLogic:
    def __init__(self, board, event_bus=None):
        self.board = board
        self.event_bus = event_bus

    def apply_damage_at(self, pos, ctx: DamageContext, source: str | None = None):
        r, c = pos
        if not self.board.can_cell_hold_occupant(r, c):
            return False

        if self.event_bus is not None:
            self.event_bus.emit(
                DamageRequestedEvent(
                    position=pos,
                    damage_type=ctx.damage_type,
                    color=ctx.color,
                    source=source,
                )
            )

        cell = self.board.get_board_element(r, c)
        did_change, destroyed_layers = self._apply_damage_to_cell(cell, ctx, pos)

        if self.event_bus is not None:
            self.event_bus.emit(
                DamageAppliedEvent(
                    position=pos,
                    damage_type=ctx.damage_type,
                    color=ctx.color,
                    did_change=did_change,
                    destroyed_layers=destroyed_layers,
                )
            )
        return did_change

    def _apply_damage_to_cell(self, cell, ctx: DamageContext, pos) -> tuple[bool, tuple[str, ...]]:
        damage_given = False
        destroyed_layers: list[str] = []

        for layer_name, entity in cell.entities():
            dmg = entity.get(Damageable)
            if not dmg or not dmg.can_take_damage(ctx):
                continue

            dmg.take_damage(ctx)
            damage_given = True
            reflector = entity.get(DamageReflecting)

            if dmg.is_destroyed():
                cell.remove_entity(entity, pos=pos, layer_name=layer_name)
                destroyed_layers.append(layer_name)

            if not reflector or not reflector.can_reflect_damage():
                break

        return damage_given, tuple(destroyed_layers)

    def apply_match_result(self, match_result: MatchResult):
        match_cells = set(match_result.cells_to_remove)
        neighbor_cells = set()

        for r, c in match_cells:
            self.apply_damage_at(
                (r, c),
                DamageContext(DamageType.MATCH, color=match_result.pivot_candy.color),
                source="match",
            )
            neighbor_cells.update(self._neighbors(r, c))

        neighbor_cells -= match_cells

        for nr, nc in neighbor_cells:
            self.apply_damage_at(
                (nr, nc),
                DamageContext(DamageType.MATCH_NEAR, color=match_result.pivot_candy.color),
                source="match-near",
            )

        if self.event_bus is not None:
            self.event_bus.emit(
                MatchResolvedEvent(
                    cells_removed=frozenset(match_cells),
                    combo_count=0,
                    spawn_pos=match_result.spawn_pos,
                    spawned_type=type(match_result.spawn_candy).__name__ if match_result.spawn_candy else None,
                )
            )

    def _neighbors(self, r, c):
        for dr, dc in ((1, 0), (-1, 0), (0, 1), (0, -1)):
            nr, nc = r + dr, c + dc
            if self.board.can_cell_hold_occupant(nr, nc):
                yield nr, nc
