from Candy import Candy
from CandyType import CandyType
from CascadeLogic import CascadeLogic
from CascadePivotPolicy import CascadePivotPolicy
from DamageResolutionLogic import DamageResolutionLogic
from DeadlockDetectionLogic import DeadlockDetectionLogic
from MatchDetectionLogic import MatchDetectionLogic
from MatchLogic import MatchLogic
from SpawnLogic import SpawnLogic
from SpecialActivationLogic import SpecialActivationLogic
from SwapPivotPolicy import SwapPivotPolicy
from Cascading import Cascading


class ColumnStateController:
    def __init__(self, board):
        self.board = board

    def lock_positions(self, positions):
        self.board.column_states.lock_many(c for _, c in positions)

    def transition_locked_to_falling(self):
        falling = set()
        for c in range(self.board.cols):
            if not self.board.column_states.is_locked(c):
                continue
            if self._column_needs_fall(c):
                falling.add(c)

        self.board.column_states.start_falling_many(falling)
        return falling

    def transition_falling_to_locked(self, columns):
        self.board.column_states.lock_many(columns)

    def settle_locked_columns(self):
        settled = set()
        for c in range(self.board.cols):
            if self.board.column_states.is_locked(c) and not self._column_needs_fall(c):
                settled.add(c)

        self.board.column_states.set_steady_many(settled)
        return settled

    def unlock_all(self):
        self.board.column_states.set_steady_many(range(self.board.cols))

    def unlock_many(self, cols):
        self.board.column_states.set_steady_many(cols)

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


class BoardResolver:
    def __init__(self, board):
        self.board = board
        self.md_logic = MatchDetectionLogic(board)
        self.match_logic = MatchLogic(board)
        self.cascade_logic = CascadeLogic(board)
        self.column_states = ColumnStateController(board)
        self.special_logic = None
        self.damage_logic = DamageResolutionLogic(board, self._on_special_hit)
        self.spawn_logic = SpawnLogic(board)
        self.special_logic = SpecialActivationLogic(board, self.damage_logic)

    def try_swap(self, r1, c1, r2, c2):
        if not self.board.can_swap(r1, c1, r2, c2):
            return False

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
            print("after combo:\n", self.board)
            if combo_handled:
                pending_special_activations.append(True)

        if not combo_handled:
            self._swap(r1, c1, r2, c2)
            print("after swap:\n", self.board)

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

        if not pending_match_results and not pending_special_activations:
            self._swap(r1, c1, r2, c2)
            print("after swap back:\n", self.board)
            self.column_states.unlock_many([c1, c2])
            return False

        # now swap is actually valid, so we can lock
        self.column_states.lock_positions(pivots)

        for result in pending_match_results:
            self.damage_logic.apply_match_result(result)
            if result.spawn_candy:
                self.board.get_board_element(*result.spawn_pos).occupant = self.spawn_logic.spawn_custom_candy(
                    result.spawn_candy.color,
                    result.spawn_candy.type,
                )
                self.column_states.lock_positions([result.spawn_pos])
        print("after swap and pop:\n", self.board)
        self.resolve_until_stable()
        return True

    def try_tap(self, r, c):
        if not self.board.column_states.can_interact(c):
            return False

        candy = self.board.get_occupant(r, c)
        if not isinstance(candy, Candy) or candy.is_normal():
            return False

        self.column_states.lock_positions([(r, c)])
        activated = self.special_logic.activate_on_hit((r, c), candy)
        if not activated:
            self.column_states.unlock_all()
            return False
        print("after swap:\n",self.board)
        self.resolve_until_stable()
        return True

    def resolve_until_stable(self):
        while True:
            falling = self.column_states.transition_locked_to_falling()

            moved = False
            spawned = False

            if falling:
                moved = bool(self.cascade_logic.apply())
                active = {c for c in range(self.board.cols) if self.board.column_states.is_falling(c)}
                self.column_states.transition_falling_to_locked(active)

            # Important:
            # even if no column is "falling", a locked column may still contain
            # empty spawnable cells (e.g. fully cleared top cells / fully empty column).
            if self.board.column_states.any_locked():
                spawned = self.spawn_logic.apply()

            if moved or spawned:
                continue

            all_matches = self.md_logic.collect_all_matches()
            if all_matches:
                policy = CascadePivotPolicy()
                match_results = self.match_logic.resolve_matches(all_matches, policy)

                for result in match_results:
                    self.column_states.lock_positions(result.cells_to_remove)
                    self.damage_logic.apply_match_result(result)

                    if result.spawn_candy:
                        self.board.get_board_element(*result.spawn_pos).occupant = result.spawn_candy
                        self.column_states.lock_positions([result.spawn_pos])
                    print("after resolve iteration:\n", self.board)
                continue

            self.column_states.settle_locked_columns()

            print("after resolve iteration:\n", self.board)
            if not self.board.column_states.any_locked() and not self.board.column_states.any_falling():
                break

    def _swap(self, r1, c1, r2, c2) -> bool:
        if not self.board.can_swap(r1, c1, r2, c2):
            return False

        cell1 = self.board.get_board_element(r1, c1)
        cell2 = self.board.get_board_element(r2, c2)
        cell1.occupant, cell2.occupant = cell2.occupant, cell1.occupant
        return True

    def _on_special_hit(self, pos, entity, ctx):
        if not isinstance(entity, Candy):
            return False
        if not entity.is_special():
            return False
        self.column_states.lock_positions([pos])
        return entity.on_hit(self.special_logic, pos, ctx)


class GameLogic:
    def __init__(self, board):
        self.board = board
        self.board_resolver = BoardResolver(board)
        self.deadlock_logic = DeadlockDetectionLogic(board)

    def try_swap(self, r1, c1, r2, c2):
        return self.board_resolver.try_swap(r1, c1, r2, c2)

    def tap(self, r, c):
        return self.board_resolver.try_tap(r, c)
