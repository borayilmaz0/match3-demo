from DamageContext import DamageContext
from DamageType import DamageType
from MatchResult import MatchResult


class DamageResolutionLogic:
    def __init__(self, board):
        self.board = board

    def apply_damage_at(self, pos, ctx: DamageContext):
        r, c = pos
        if not self.board.can_cell_hold_occupant(r, c):
            return False

        cell = self.board.get_board_element(r, c)
        cell.apply_damage(
            ctx,
            pos=pos,
        )
        return True

    def apply_match_result(self, match_result: MatchResult):
        match_cells = set(match_result.cells_to_remove)
        neighbor_cells = set()

        for r, c in match_cells:
            # Apply primary MATCH damage
            self.apply_damage_at(
                (r, c),
                DamageContext(
                    DamageType.MATCH,
                    color=match_result.pivot_candy.color,
                ),
            )

            # Blindly add all valid neighbors to the set
            neighbor_cells.update(self._neighbors(r, c))

        # Remove the original match cells from the neighbors set in one shot
        neighbor_cells -= match_cells

        # Apply MATCH_NEAR damage to the remaining true neighbors
        for nr, nc in neighbor_cells:
            self.apply_damage_at(
                (nr, nc),
                DamageContext(
                    DamageType.MATCH_NEAR,
                    color=match_result.pivot_candy.color,
                ),
            )

    def _neighbors(self, r, c):
        for dr, dc in ((1, 0), (-1, 0), (0, 1), (0, -1)):
            nr, nc = r + dr, c + dc
            if self.board.can_cell_hold_occupant(nr, nc):
                yield nr, nc
