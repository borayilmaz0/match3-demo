from Cascading import Cascading


class CascadeLogic:
    def __init__(self, board):
        self.board = board

    def apply(self, columns=None) -> set[int]:
        if columns is None:
            columns = range(self.board.cols)

        moved_columns = set()
        for c in columns:
            if self.apply_column(c):
                moved_columns.add(c)

        return moved_columns

    def apply_column(self, col) -> bool:
        """
        Resolve gravity inside a single column.

        The column is treated as independent vertical segments separated by
        cells that cannot hold occupants (gaps).

        Inside each segment:
        - falling occupants compact downward,
        - non-falling occupants stay fixed and behave like anchors,
        - empty cells are left only at the top of each free interval.
        """
        moved = False

        for segment_rows in self._iter_column_segments(col):
            if self._settle_segment(col, segment_rows):
                moved = True

        return moved

    def _iter_column_segments(self, col):
        segment = []

        for r in range(self.board.rows):
            cell = self.board.get_board_element(r, col)
            if cell.can_hold_occupant():
                segment.append(r)
            elif segment:
                yield segment
                segment = []

        if segment:
            yield segment

    def _can_fall(self, occupant) -> bool:
        if occupant is None:
            return False

        cascading = occupant.get(Cascading)
        return bool(cascading and cascading.can_fall())

    def _settle_segment(self, col, segment_rows) -> bool:
        moved = False
        next_write_idx = len(segment_rows) - 1

        for idx in range(len(segment_rows) - 1, -1, -1):
            r = segment_rows[idx]
            cell = self.board.get_board_element(r, col)
            occ = cell.occupant

            if occ is None:
                continue

            if not self._can_fall(occ):
                next_write_idx = idx - 1
                continue

            target_row = segment_rows[next_write_idx]
            if target_row != r:
                self.board.get_board_element(target_row, col).occupant = occ
                cell.occupant = None
                moved = True

            next_write_idx -= 1

        return moved