import random

from Candy import Candy, NormalCandy, CandyFactory
from Cascading import Cascading


class SpawnLogic:
    def __init__(self, board):
        self.board = board

    def apply(self, columns=None) -> set[int]:
        if columns is None:
            columns = range(self.board.cols)

        spawned_columns = set()
        for c in columns:
            if self.apply_column(c):
                spawned_columns.add(c)

        return spawned_columns

    def apply_column(self, c) -> bool:
        """
        Spawn only into entry slots that remain empty after gravity settles
        the column.

        We do NOT spawn into every empty playable cell.
        We only fill the top empty run of each free interval.
        """
        spawned = False

        for r in self._collect_spawn_rows_for_column(c):
            cell = self.board.get_board_element(r, c)
            if cell.occupant is None:
                cell.occupant = self.spawn_random_candy()
                spawned = True

        return spawned

    def _collect_spawn_rows_for_column(self, c):
        results = []

        for segment_rows in self._iter_column_segments(c):
            results.extend(self._collect_spawn_rows_for_segment(c, segment_rows))

        return results

    def _iter_column_segments(self, c):
        segment = []

        for r in range(self.board.rows):
            cell = self.board.get_board_element(r, c)
            if cell.can_hold_occupant():
                segment.append(r)
            elif segment:
                yield segment
                segment = []

        if segment:
            yield segment

    def _collect_spawn_rows_for_segment(self, c, segment_rows):
        spawn_rows = []
        interval_start = 0

        while interval_start < len(segment_rows):
            interval_end = interval_start

            while interval_end < len(segment_rows):
                r = segment_rows[interval_end]
                occ = self.board.get_board_element(r, c).occupant

                if occ is not None:
                    cascade_behavior = occ.get(Cascading)
                    if not cascade_behavior or not cascade_behavior.can_fall():
                        break

                interval_end += 1

            interval_rows = segment_rows[interval_start:interval_end]
            spawn_rows.extend(self._top_empty_run_in_interval(c, interval_rows))
            interval_start = interval_end + 1

        return spawn_rows

    def _top_empty_run_in_interval(self, c, interval_rows):
        rows = []

        for r in interval_rows:
            cell = self.board.get_board_element(r, c)
            if cell.occupant is None and cell.can_spawn():
                rows.append(r)
            else:
                break

        return rows

    def spawn_random_candy(self):
        color = random.choice(self.board.color_set)
        return NormalCandy(color)

    def spawn_custom_candy(self, color, _type):
        return CandyFactory.create(_type, color)