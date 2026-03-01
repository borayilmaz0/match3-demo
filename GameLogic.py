from Candy import Candy
from CascadeLogic import CascadeLogic
from CascadePivotPolicy import CascadePivotPolicy
from DamageResolutionLogic import DamageResolutionLogic
from DeadlockDetectionLogic import DeadlockDetectionLogic
from MatchDetectionLogic import MatchDetectionLogic
from MatchLogic import MatchLogic
from SpawnLogic import SpawnLogic
from SwapPivotPolicy import SwapPivotPolicy
from SpecialActivationLogic import SpecialActivationLogic
from CandyType import CandyType


class GameLogic:

    def __init__(self, board):
        self.board = board
        self.md_logic = MatchDetectionLogic(board)
        self.match_logic = MatchLogic(board)
        self.damage_logic = DamageResolutionLogic(board)
        self.cascade_logic = CascadeLogic(board)
        self.spawn_logic = SpawnLogic(board)
        self.special_logic = SpecialActivationLogic(board, self.damage_logic)
        self.deadlock_logic = DeadlockDetectionLogic(board)

    def __swap(self, r1, c1, r2, c2) -> bool:
        """
        Attempt to swap two cell occupants.
        Returns True if swap was performed, False otherwise.
        """
        if not self.board.can_swap(r1, c1, r2, c2):
            return False

        cell1 = self.board.get_board_element(r1, c1)
        cell2 = self.board.get_board_element(r2, c2)

        cell1.occupant, cell2.occupant = cell2.occupant, cell1.occupant
        return True

    def try_swap(self, r1, c1, r2, c2):
        if not self.__swap(r1, c1, r2, c2):
            return False

        print(f"after swap:\n{self.board}")

        pivots = [(r1, c1), (r2, c2)]
        swap_policy = SwapPivotPolicy(pivots)

        pending_match_results = []
        pending_special_activations = []

        candy_a = self.board.get_occupant(r1, c1)
        candy_b = self.board.get_occupant(r2, c2)

        combo_handled = False
        # 0️⃣ ordered special+special combo: (a swapped into b)
        if self.special_logic.can_activate_combo_on_swap(candy_a, candy_b):
            combo_handled = self.special_logic.activate_combo_on_swap(
                (r1, c1), (r2, c2), candy_a, candy_b
            )
            if combo_handled:
                pending_special_activations.append(True)

        # ------------------------------------------------------------
        # 1️⃣ Evaluate both pivots independently
        # ------------------------------------------------------------
        for pos in pivots:
            r, c = pos
            candy = self.board.get_occupant(r, c)

            # --- normal match detection ---
            match = self.md_logic.collect_matches_at(r, c)
            if match:
                pivot = swap_policy.choose_pivot(match)
                result = self.match_logic.find_best_match(match, pivot)
                if result:
                    pending_match_results.append(result)

            if combo_handled:
                continue

            # --- special swap activation ---
            if isinstance(candy, Candy) and candy.type != CandyType.NORMAL:
                # Determine the neighboring (other swapped) candy
                if pos == (r1, c1):
                    neighbor = self.board.get_occupant(r2, c2)
                else:
                    neighbor = self.board.get_occupant(r1, c1)

                activated = self.special_logic.activate_on_swap(
                    pos,
                    candy,
                    neighbor
                )

                if activated:
                    pending_special_activations.append(True)

        # ------------------------------------------------------------
        # 2️⃣ If nothing happened, revert swap
        # ------------------------------------------------------------
        if not pending_match_results and not pending_special_activations:
            self.__swap(r1, c1, r2, c2)
            return False

        # ------------------------------------------------------------
        # 3️⃣ Apply match damage
        # ------------------------------------------------------------
        for result in pending_match_results:
            self.damage_logic.apply_match_result(result)
            if result.spawn_candy:
                self.board.get_board_element(*result.spawn_pos).occupant = (
                    self.spawn_logic.spawn_custom_candy(
                        result.spawn_candy.color,
                        result.spawn_candy.type
                    )
                )

        print(f"after swap and pop:\n{self.board}")

        # ------------------------------------------------------------
        # 5️⃣ Cascades + combos
        # ------------------------------------------------------------
        self._resolve_cascade()
        self._resolve_combos()

        return True

    def tap(self, r, c):
        """
        Tap activation:
        - Activates a special candy without swapping
        - Normal candies cannot be tapped
        """
        candy = self.board.get_occupant(r, c)
        if not isinstance(candy, Candy):
            return False
        if candy.type == CandyType.NORMAL:
            return False

        # activate the special immediately
        activated = self.special_logic.activate_on_hit((r, c), candy)
        if not activated:
            return False

        print(f"after tap and pop:\n{self.board}")

        # resolve cascades and follow-up combos
        self._resolve_cascade()
        self._resolve_combos()

        return True

    def _resolve_cascade(self):
        """
        Runs cascade + spawn until board is stable.
        """
        while True:
            moved = self.cascade_logic.apply()
            spawned = self.spawn_logic.apply()

            if not moved and not spawned:
                break

        print(f"after resolve cascade:\n{self.board}")

    def _resolve_combos(self):
        """
        Detects and resolves matches until board is stale.
        """
        combo = 0
        policy = CascadePivotPolicy()

        while True:
            all_matches = self.md_logic.collect_all_matches()
            if not all_matches:
                break

            combo += 1
            print(f"combo {combo}")

            match_results = self.match_logic.resolve_matches(all_matches, policy)
            for result in match_results:
                print(
                    "match result:", result.cells_to_remove, result.spawn_candy
                    if result.spawn_candy is not None else None,
                    result.spawn_pos if result.spawn_pos is not None else None)

            for result in match_results:
                self.damage_logic.apply_match_result(result)

                if result.spawn_candy:
                    self.board.get_board_element(*result.spawn_pos).occupant = (
                        result.spawn_candy
                    )

            print(f"after resolve combo:\n{self.board}")

            self._resolve_cascade()
