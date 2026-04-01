from Candy import Candy
from BoardResolutionPhase import BoardResolutionPhase
from CascadeLogic import CascadeLogic
from CascadePivotPolicy import CascadePivotPolicy
from Cascading import Cascading
from DamageResolutionLogic import DamageResolutionLogic
from DeadlockDetectionLogic import DeadlockDetectionLogic
from EffectQueue import EffectQueue, Effect
from EventBus import EventBus
from GameEvents import (
    BoardPhaseChangedEvent,
    BoardBecameStableEvent,
    SpecialTriggeredEvent,
)
from MatchDetectionLogic import MatchDetectionLogic
from MatchLogic import MatchLogic
from SpawnLogic import SpawnLogic
from SpecialActivationLogic import SpecialActivationLogic
from SwapPivotPolicy import SwapPivotPolicy


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
        self.damage_logic = DamageResolutionLogic(board, event_bus=self.event_bus)
        self.spawn_logic = SpawnLogic(board, event_bus=self.event_bus)
        self.special_logic = SpecialActivationLogic(board, self.damage_logic)

    def set_blocking_mode(self, blocking_mode: bool):
        self.blocking_mode = blocking_mode

    def is_accepting_input(self):
        return self.phase in (BoardResolutionPhase.IDLE, BoardResolutionPhase.STABLE)

    def try_swap(self, r1, c1, r2, c2):
        if not self.is_accepting_input():
            return False

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

        if not combo_handled:
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
            self._set_phase(BoardResolutionPhase.STABLE)
            return False

        for result in pending_match_results:
            self.effect_queue.push(Effect(kind="apply_match_result", payload={"result": result}))

        return self._finish_resolution_request()

    def try_tap(self, r, c):
        if not self.is_accepting_input():
            return False

        candy = self.board.get_occupant(r, c)
        if not isinstance(candy, Candy) or candy.is_normal():
            return False

        self._set_phase(BoardResolutionPhase.RESOLVING_INPUT)
        activated = self.special_logic.activate_on_hit((r, c), candy)
        if not activated:
            self._set_phase(BoardResolutionPhase.STABLE)
            return False

        self.event_bus.emit(
            SpecialTriggeredEvent(position=(r, c), candy_type=candy.type, trigger="tap")
        )
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

        falling_cols = self._find_columns_needing_fall()

        moved = False
        spawned = False

        if falling_cols:
            self._set_phase(BoardResolutionPhase.FALLING)
            moved_columns = self.cascade_logic.apply(falling_cols)
            moved = bool(moved_columns)

        self._set_phase(BoardResolutionPhase.SPAWNING)
        spawned = self.spawn_logic.apply()

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

        self._set_phase(BoardResolutionPhase.STABLE)
        self.event_bus.emit(BoardBecameStableEvent())
        return False

    def _apply_effect(self, effect):
        if effect.kind == "apply_match_result":
            result = effect.payload["result"]
            self.damage_logic.apply_match_result(result)

            if result.spawn_candy:
                self.board.get_board_element(*result.spawn_pos).occupant = self.spawn_logic.spawn_custom_candy(
                    result.spawn_candy.color,
                    result.spawn_candy.type,
                )

    def _find_columns_needing_fall(self):
        columns = set()
        for c in range(self.board.cols):
            if self._column_needs_fall(c):
                columns.add(c)
        return columns

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
