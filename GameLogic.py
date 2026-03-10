from Candy import Candy
from BoardResolutionPhase import BoardResolutionPhase
from CascadeLogic import CascadeLogic
from CascadePivotPolicy import CascadePivotPolicy
from DamageResolutionLogic import DamageResolutionLogic
from DeadlockDetectionLogic import DeadlockDetectionLogic
from EffectQueue import EffectQueue, Effect
from EventBus import EventBus
from GameEvents import (
    BoardPhaseChangedEvent,
    BoardBecameStableEvent,
    ColumnCellsReleasedEvent,
    ColumnCellsReservedEvent,
    ColumnFallingStartedEvent,
    ColumnFallingStoppedEvent,
    ColumnStateChangedEvent,
    SpecialTriggeredEvent,
)
from MatchDetectionLogic import MatchDetectionLogic
from MatchLogic import MatchLogic
from SpawnLogic import SpawnLogic
from SpecialActivationLogic import SpecialActivationLogic
from SwapPivotPolicy import SwapPivotPolicy
from Cascading import Cascading


class ColumnStateController:
    def __init__(self, board, event_bus=None):
        self.board = board
        self.event_bus = event_bus

    def lock_positions(self, positions, reason="effect"):
        by_col = {}
        for r, c in positions:
            by_col.setdefault(c, set()).add(r)

        for c, rows in by_col.items():
            old_state = self.board.column_states.states[c]
            self.board.column_states.lock(c)
            self.board.column_states.reserve(c, rows)
            self._emit_state_change(c, old_state, self.board.column_states.states[c], reason)
            self._emit_rows_reserved(c, rows, reason)

    def release_positions(self, positions, reason="effect-complete"):
        by_col = {}
        for r, c in positions:
            by_col.setdefault(c, set()).add(r)

        for c, rows in by_col.items():
            self.board.column_states.release(c, rows)
            self._emit_rows_released(c, rows, reason)

    def transition_locked_to_falling(self):
        falling = set()
        for c in range(self.board.cols):
            if not self.board.column_states.is_locked(c):
                continue
            if self._column_needs_fall(c):
                falling.add(c)

        if falling:
            for c in falling:
                old_state = self.board.column_states.states[c]
                unstable_rows = self._collect_unstable_rows(c)
                self.board.column_states.start_falling(c)
                self.board.column_states.mark_unstable(c, unstable_rows)
                self._emit_state_change(c, old_state, self.board.column_states.states[c], "gravity")
            if self.event_bus is not None:
                self.event_bus.emit(ColumnFallingStartedEvent(columns=tuple(sorted(falling))))
        return falling

    def transition_falling_to_locked(self, columns):
        changed = set(columns)
        for c in changed:
            old_state = self.board.column_states.states[c]
            self.board.column_states.lock(c)
            self.board.column_states.clear_unstable(c)
            self._emit_state_change(c, old_state, self.board.column_states.states[c], "post-fall")
        if changed and self.event_bus is not None:
            self.event_bus.emit(ColumnFallingStoppedEvent(columns=tuple(sorted(changed))))

    def settle_locked_columns(self):
        settled = set()
        for c in range(self.board.cols):
            if (
                self.board.column_states.is_locked(c)
                and not self._column_needs_fall(c)
                and not self.board.column_states.reserved_rows(c)
            ):
                settled.add(c)

        for c in settled:
            old_state = self.board.column_states.states[c]
            self.board.column_states.set_steady(c)
            self._emit_state_change(c, old_state, self.board.column_states.states[c], "settled")
        return settled

    def unlock_all(self):
        for c in range(self.board.cols):
            old_state = self.board.column_states.states[c]
            self.board.column_states.set_steady(c)
            self._emit_state_change(c, old_state, self.board.column_states.states[c], "unlock-all")

    def unlock_many(self, cols):
        for c in set(cols):
            old_state = self.board.column_states.states[c]
            self.board.column_states.set_steady(c)
            self._emit_state_change(c, old_state, self.board.column_states.states[c], "unlock-many")

    def release_all_reservations(self):
        for c in range(self.board.cols):
            rows = self.board.column_states.reserved_rows(c)
            if rows:
                self.board.column_states.release(c)
                self._emit_rows_released(c, rows, "release-all")

    def _collect_unstable_rows(self, c):
        unstable = set()
        seen_empty = False
        for r in range(self.board.rows - 1, -1, -1):
            if not self.board.can_cell_hold_occupant(r, c):
                continue

            cell = self.board.get_board_element(r, c)
            occ = cell.occupant

            if occ is None:
                seen_empty = True
                unstable.add(r)
                continue

            cascading = occ.get(Cascading)
            if seen_empty and cascading and cascading.can_fall():
                unstable.add(r)
        return unstable

    def _column_needs_fall(self, c):
        seen_empty = False
        for r in range(self.board.rows - 1, -1, -1):
            if not self.board.can_cell_hold_occupant(r, c):
                continue

            cell = self.board.get_board_element(r, c)
            occ = cell.occupant

            if occ is None:
                seen_empty = True
                continue

            cascading = occ.get(Cascading)
            if seen_empty and cascading and cascading.can_fall():
                return True

        return False

    def _emit_state_change(self, column, old_state, new_state, reason):
        if self.event_bus is None or old_state == new_state:
            return
        self.event_bus.emit(
            ColumnStateChangedEvent(
                column=column,
                old_state=old_state,
                new_state=new_state,
                reason=reason,
            )
        )

    def _emit_rows_reserved(self, column, rows, reason):
        if self.event_bus is not None and rows:
            self.event_bus.emit(
                ColumnCellsReservedEvent(column=column, rows=tuple(sorted(rows)), reason=reason)
            )

    def _emit_rows_released(self, column, rows, reason):
        if self.event_bus is not None and rows:
            self.event_bus.emit(
                ColumnCellsReleasedEvent(column=column, rows=tuple(sorted(rows)), reason=reason)
            )


class BoardResolver:
    def __init__(self, board, event_bus=None, blocking_mode=True):
        self.board = board
        self.event_bus = event_bus or EventBus()
        self.phase = BoardResolutionPhase.IDLE
        self.blocking_mode = blocking_mode
        self.effect_queue = EffectQueue()

        self.md_logic = MatchDetectionLogic(board)
        self.match_logic = MatchLogic(board)
        self.cascade_logic = CascadeLogic(board, event_bus=self.event_bus)
        self.column_states = ColumnStateController(board, event_bus=self.event_bus)
        self.damage_logic = DamageResolutionLogic(board, event_bus=self.event_bus)
        self.spawn_logic = SpawnLogic(board, event_bus=self.event_bus)
        self.special_logic = SpecialActivationLogic(board, self.damage_logic)

    def set_blocking_mode(self, blocking_mode: bool):
        self.blocking_mode = blocking_mode

    def try_swap(self, r1, c1, r2, c2):
        if not self.board.can_swap(r1, c1, r2, c2):
            return False

        self._set_phase(BoardResolutionPhase.RESOLVING_INPUT)

        pivots = [(r1, c1), (r2, c2)]
        swap_policy = SwapPivotPolicy(pivots)

        pending_match_results = []
        pending_special_activations = []

        candy_a = self.board.get_occupant(r1, c1)
        candy_b = self.board.get_occupant(r2, c2)

        combo_handled = False
        if self.special_logic.can_activate_combo_on_swap(candy_a, candy_b):
            combo_handled = self.special_logic.activate_combo_on_swap(
                (r1, c1), (r2, c2), candy_a, candy_b
            )
            if combo_handled:
                pending_special_activations.append(True)

        if combo_handled:
            impacted = self.special_logic.consume_impacted_columns()
            self.column_states.lock_positions([(0, c) for c in impacted], reason="combo-impact")
        else:
            self._swap(r1, c1, r2, c2)

        for pos in pivots:
            if combo_handled:
                continue

            r, c = pos
            candy = self.board.get_occupant(r, c)

            match = self.md_logic.collect_matches_at(r, c)
            if match:
                pivot = swap_policy.choose_pivot(match)
                result = self.match_logic.find_best_match(match, pivot)
                if result:
                    pending_match_results.append(result)

            if isinstance(candy, Candy) and candy.is_special():
                neighbor = self.board.get_occupant(r2, c2) if pos == (r1, c1) else self.board.get_occupant(r1, c1)
                activated = self.special_logic.activate_on_swap(pos, candy, neighbor)
                if activated:
                    pending_special_activations.append(True)
                    self.event_bus.emit(
                        SpecialTriggeredEvent(position=pos, candy_type=candy.type, trigger="swap")
                    )

        if not pending_match_results and not pending_special_activations:
            self._swap(r1, c1, r2, c2)
            self.column_states.unlock_many([c1, c2])
            self._set_phase(BoardResolutionPhase.STABLE)
            return False

        self.column_states.lock_positions(pivots, reason="player-swap")

        for result in pending_match_results:
            self.effect_queue.push(Effect(kind="apply_match_result", payload={"result": result}))

        return self._finish_resolution_request()

    def try_tap(self, r, c):
        if not self.board.column_states.can_interact(c, r):
            return False

        candy = self.board.get_occupant(r, c)
        if not isinstance(candy, Candy) or candy.is_normal():
            return False

        self._set_phase(BoardResolutionPhase.RESOLVING_INPUT)
        self.column_states.lock_positions([(r, c)], reason="tap")
        activated = self.special_logic.activate_on_hit((r, c), candy)
        if not activated:
            self.column_states.unlock_all()
            self._set_phase(BoardResolutionPhase.STABLE)
            return False

        self.event_bus.emit(
            SpecialTriggeredEvent(position=(r, c), candy_type=candy.type, trigger="tap")
        )
        impacted = self.special_logic.consume_impacted_columns()
        if impacted:
            self.column_states.lock_positions([(0, col) for col in impacted], reason="special-impact")
        return self._finish_resolution_request()

    def _finish_resolution_request(self):
        if self.blocking_mode:
            self.resolve_until_stable()
        return True

    def resolve_until_stable(self):
        while self.resolve_next_step():
            pass

    def resolve_next_step(self):
        self._set_phase(BoardResolutionPhase.RESOLVING_EFFECTS)

        effect = self.effect_queue.pop_next()
        if effect is not None:
            self._apply_effect(effect)
            return True

        falling = self.column_states.transition_locked_to_falling()

        moved = False
        spawned = False

        if falling:
            self._set_phase(BoardResolutionPhase.FALLING)
            moved_columns = self.cascade_logic.apply(falling)
            moved = bool(moved_columns)
            self.column_states.transition_falling_to_locked(falling)

        if self.board.column_states.any_locked():
            self._set_phase(BoardResolutionPhase.SPAWNING)
            spawned = self.spawn_logic.apply()
            if spawned:
                self.column_states.release_all_reservations()

        if moved or spawned:
            return True

        self._set_phase(BoardResolutionPhase.MATCHING)
        all_matches = self.md_logic.collect_all_matches()
        if all_matches:
            policy = CascadePivotPolicy()
            match_results = self.match_logic.resolve_matches(all_matches, policy)

            for result in match_results:
                self.effect_queue.push(Effect(kind="apply_match_result", payload={"result": result}))
            return True

        self.column_states.release_all_reservations()
        self.column_states.settle_locked_columns()

        if not self.board.column_states.any_locked() and not self.board.column_states.any_falling():
            self._set_phase(BoardResolutionPhase.STABLE)
            self.event_bus.emit(BoardBecameStableEvent())
            return False

        return True

    def _apply_effect(self, effect):
        if effect.kind == "apply_match_result":
            result = effect.payload["result"]
            self.column_states.lock_positions(result.cells_to_remove, reason="match-clear")
            self.damage_logic.apply_match_result(result)
            self.column_states.release_positions(result.cells_to_remove, reason="match-applied")

            if result.spawn_candy:
                self.board.get_board_element(*result.spawn_pos).occupant = self.spawn_logic.spawn_custom_candy(
                    result.spawn_candy.color,
                    result.spawn_candy.type,
                )
                self.column_states.lock_positions([result.spawn_pos], reason="spawn-special")
                self.column_states.release_positions([result.spawn_pos], reason="spawn-special-done")

    def _set_phase(self, new_phase):
        old_phase = self.phase
        self.phase = new_phase
        if self.event_bus is not None and old_phase != new_phase:
            self.event_bus.emit(BoardPhaseChangedEvent(old_phase=old_phase.name, new_phase=new_phase.name))

    def _swap(self, r1, c1, r2, c2) -> bool:
        if not self.board.can_swap(r1, c1, r2, c2):
            return False

        cell1 = self.board.get_board_element(r1, c1)
        cell2 = self.board.get_board_element(r2, c2)
        cell1.occupant, cell2.occupant = cell2.occupant, cell1.occupant
        return True


class GameLogic:
    def __init__(self, board, event_bus=None, blocking_mode=True):
        self.board = board
        self.event_bus = event_bus or EventBus()
        self.board_resolver = BoardResolver(board, event_bus=self.event_bus, blocking_mode=blocking_mode)
        self.deadlock_logic = DeadlockDetectionLogic(board)

    def try_swap(self, r1, c1, r2, c2):
        return self.board_resolver.try_swap(r1, c1, r2, c2)

    def tap(self, r, c):
        return self.board_resolver.try_tap(r, c)

    def resolve_next_step(self):
        return self.board_resolver.resolve_next_step()

    def resolve_until_stable(self):
        self.board_resolver.resolve_until_stable()
