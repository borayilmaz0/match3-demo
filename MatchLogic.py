# MatchLogic.py
from Candy import Candy, RocketVCandy, CandyFactory
from CandyType import CandyType
from MatchResult import MatchResult


class MatchLogic:
    def __init__(self, board):
        self.board = board

    def find_best_match(self, match_cells, pivot):
        if not match_cells or pivot not in match_cells:
            return None
        return self._resolve_group(match_cells, pivot)

    def resolve_matches(self, all_matches, pivot_policy):
        results = []

        for cells in all_matches:
            if not cells:
                continue

            pivot = pivot_policy.choose_pivot(cells)
            if pivot is None:
                continue

            results.append(self._resolve_group(cells, pivot))

        return results

    def _resolve_group(self, cells, pivot):
        pivot_candy = self.board.get_occupant(*pivot)
        if not isinstance(pivot_candy, Candy):
            return None

        h_len, v_len = self._analyze_pivot(cells, pivot)
        size = len(cells)

        spawn_candy = None

        if max(h_len, v_len) >= 5:
            spawn_candy = CandyFactory.create(
                candy_type=CandyType.LIGHT_BALL,
                color=pivot_candy.color
            )

        elif h_len >= 3 and v_len >= 3:
            spawn_candy = CandyFactory.create(
                candy_type=CandyType.BOMB,
                color=pivot_candy.color
            )

        elif max(h_len, v_len) == 4:
            spawn_candy = CandyFactory.create(
                candy_type=CandyType.ROCKET_H if h_len == 4 else CandyType.ROCKET_V,
                color=pivot_candy.color
            )

        elif size >= 4:
            spawn_candy = CandyFactory.create(
                candy_type=CandyType.PROPELLER,
                color=pivot_candy.color
            )

        return MatchResult(
            cells_to_remove=set(cells),
            spawn_pos=pivot if spawn_candy else None,
            spawn_candy=spawn_candy,
            pivot_candy=pivot_candy
        )

    def _analyze_pivot(self, cells, pivot):
        pr, pc = pivot
        cell_set = set(cells)

        def count_dir(dr, dc):
            r, c = pr + dr, pc + dc
            count = 0
            while (r, c) in cell_set:
                count += 1
                r += dr
                c += dc
            return count

        left = count_dir(0, -1)
        right = count_dir(0, 1)
        up = count_dir(-1, 0)
        down = count_dir(1, 0)

        h_len = left + right + 1
        v_len = up + down + 1

        return h_len, v_len