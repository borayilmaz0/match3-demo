from Candy import Candy
from DamageContext import DamageContext
from DamageType import DamageType
from MatchResult import MatchResult


class DamageResolutionLogic:
    def __init__(self, board):
        self.board = board

    def apply_match_result(self, match_result:MatchResult):
        """
        match_result:
            - cells_to_remove: set[(r, c)]
            - color
        """

        # 1️⃣ direct match damage
        for r, c in match_result.cells_to_remove:
            cell = self.board.get_board_element(r, c)
            if cell:
                cell.apply_damage(
                    DamageContext(
                        DamageType.MATCH,
                        color=match_result.pivot_candy.color
                    )
                )

        # 2️⃣ near damage
        for r, c in match_result.cells_to_remove:
            for nr, nc in self._neighbors(r, c):
                cell = self.board.get_board_element(nr, nc)
                if cell:
                    cell.apply_damage(
                        DamageContext(
                            DamageType.MATCH_NEAR,
                            color=match_result.pivot_candy.color
                        )
                    )

    def _neighbors(self, r, c):
        for dr, dc in ((1,0), (-1,0), (0,1), (0,-1)):
            nr, nc = r + dr, c + dc
            if self.board.can_cell_hold_occupant(nr, nc):
                yield nr, nc