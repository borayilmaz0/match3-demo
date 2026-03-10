from Cell import Cell
from ColumnStateManager import ColumnStateManager


class Board:

    def __init__(self, rows, cols, color_set, board_layout=None):
        self.rows = rows
        self.cols = cols
        self.color_set = list(color_set)
        self.column_states = ColumnStateManager(self.cols)

        # Board structure (Cell / GapCell)
        if board_layout is None:
            self.board = [[Cell() for _ in range(cols)] for _ in range(rows)]
        else:
            self.board = board_layout

    # --------------------------------------------------
    # Debug / display
    # --------------------------------------------------
    def __str__(self):
        s = ""
        for c in range(self.cols):
            s += f"{self.column_states.states[c].name:>31}"
        s += "\n"
        for r in range(self.rows):
            row = []
            for c in range(self.cols):
                row.append(str(self.get_board_element(r, c)))
            s += f"{row}\n"
        return s

    # --------------------------------------------------
    # Cell access
    # --------------------------------------------------
    def get_board_element(self, r, c):
        if 0 <= r < self.rows and 0 <= c < self.cols:
            return self.board[r][c]
        raise IndexError("Board access out of bounds")

    def set_cell(self, r, c, cell):
        if 0 <= r < self.rows and 0 <= c < self.cols:
            self.board[r][c] = cell
            return True
        raise IndexError("Board access out of bounds")

    # --------------------------------------------------
    # Occupant access
    # --------------------------------------------------
    def get_occupant(self, r, c):
        cell = self.get_board_element(r, c)
        if not cell.can_hold_occupant() or not cell.can_use_cell_occupant():
            return None
        return cell.occupant

    # --------------------------------------------------
    # Validation
    # --------------------------------------------------
    def can_cell_hold_occupant(self, r, c):
        try:
            cell = self.get_board_element(r, c)
        except IndexError:
            return False
        return cell.can_hold_occupant()

    # --------------------------------------------------
    # Swap validation
    # --------------------------------------------------
    def can_swap(self, r1, c1, r2, c2) -> bool:
        try:
            if abs(r1 - r2) + abs(c1 - c2) != 1:
                return False

            if not self.column_states.can_interact(
                    c1) or not self.column_states.can_interact(c2):
                return False

            cell1 = self.get_board_element(r1, c1)
            cell2 = self.get_board_element(r2, c2)

            if not cell1.can_swap() or not cell2.can_swap():
                return False

            return True
        except IndexError:
            return False
