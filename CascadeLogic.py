from Cascading import Cascading

class CascadeLogic:
    def __init__(self, board):
        self.board = board

    def apply(self) -> bool:
        moved = False
        for c in range(self.board.cols):
            if self._cascade_column(c):
                moved = True
        return moved

    # ------------------------------------------------------------

    def _cascade_column(self, c) -> bool:
        moved = False

        # rows that can hold occupants
        valid_rows = [
            r for r in range(self.board.rows)
            if self.board.get_board_element(r, c).can_hold_occupant()
        ]

        if not valid_rows:
            return False

        write_index = len(valid_rows) - 1

        for r in reversed(valid_rows):
            cell = self.board.get_board_element(r, c)
            occ = cell.occupant

            if occ is None:
                continue

            cascading = occ.get(Cascading)
            if not cascading or not cascading.can_fall():
                write_index -= 1
                continue

            target_row = valid_rows[write_index]
            if target_row != r:
                self.board.get_board_element(target_row, c).occupant = occ
                cell.occupant = None
                moved = True

            write_index -= 1

        return moved