from Matchable import Matchable
from MatchDetectionLogic import MatchDetectionLogic


class DeadlockDetectionLogic:
    def __init__(self, board):
        self.board = board
        self.matcher = MatchDetectionLogic(board)

    # ------------------------------------------------------------
    # Return the occupant at (r, c) assuming a swap between (r1,c1)
    # and (r2,c2) has occurred
    # ------------------------------------------------------------
    def _occupant_after_swap(self, r, c, r1, c1, r2, c2):
        if (r, c) == (r1, c1):
            return self.board.get_occupant(r2, c2)
        if (r, c) == (r2, c2):
            return self.board.get_occupant(r1, c1)
        return self.board.get_occupant(r, c)

    # ------------------------------------------------------------
    # Check whether a specific swap is valid
    # ------------------------------------------------------------
    def _is_valid_swap(self, r1, c1, r2, c2):
        if abs(r1 - r2) + abs(c1 - c2) != 1:
            return False

        if not self.board.can_swap(r1, c1, r2, c2):
            return False

        a = self.board.get_occupant(r1, c1)
        b = self.board.get_occupant(r2, c2)

        matchable_a = a.get(Matchable) if a else None
        matchable_b = b.get(Matchable) if b else None

        if (
                not matchable_a or not matchable_a.can_be_matched()
                or not matchable_b or not matchable_b.can_be_matched()
                or a.color == b.color
        ):
            return False

        def get_after_swap(r, c):
            return self._occupant_after_swap(r, c, r1, c1, r2, c2)

        matches_a = self.matcher.collect_matches_at(r1, c1, get_after_swap)
        matches_b = self.matcher.collect_matches_at(r2, c2, get_after_swap)

        # causality: swapped cell must actually change
        if matches_a:
            before = self.board.get_occupant(r1, c1)
            after = get_after_swap(r1, c1)
            if before and after and before.color != after.color:
                return True

        if matches_b:
            before = self.board.get_occupant(r2, c2)
            after = get_after_swap(r2, c2)
            if before and after and before.color != after.color:
                return True

        return False

    # find a valid swap
    def find_any_valid_swap(self):
        rows = self.board.rows
        cols = self.board.cols

        for r in range(rows):
            for c in range(cols):
                if not self.board.can_cell_hold_occupant(r, c):
                    continue

                if c + 1 < cols and self.board.can_cell_hold_occupant(r, c + 1):
                    if self._is_valid_swap(r, c, r, c + 1):
                        print("found valid swap:", r, c, r, c + 1)
                        return (r, c), (r, c + 1)

                if r + 1 < rows and self.board.can_cell_hold_occupant(r + 1, c):
                    if self._is_valid_swap(r, c, r + 1, c):
                        print("found valid swap:", r, c, r + 1, c)

                        return (r, c), (r + 1, c)

        return None
