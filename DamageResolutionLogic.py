from DamageContext import DamageContext
from DamageType import DamageType
from MatchResult import MatchResult


class DamageResolutionLogic:
    def __init__(self, board, on_special_hit=None):
        self.board = board
        self.on_special_hit = on_special_hit

    def apply_damage_at(self, pos, ctx: DamageContext):
        r, c = pos
        if not self.board.can_cell_hold_occupant(r, c):
            return False

        cell = self.board.get_board_element(r, c)
        cell.apply_damage(
            ctx,
            pos=pos,
            on_special_hit=self.on_special_hit,
        )
        return True

    def apply_match_result(self, match_result: MatchResult):
        for r, c in match_result.cells_to_remove:
            self.apply_damage_at(
                (r, c),
                DamageContext(
                    DamageType.MATCH,
                    color=match_result.pivot_candy.color,
                ),
            )

        for r, c in match_result.cells_to_remove:
            for nr, nc in self._neighbors(r, c):
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
