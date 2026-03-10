import random

from Board import Board
from Candy import Candy, NormalCandy
from CandyType import CandyType


class BoardDesigner:
    def __init__(self, layout, color_set):
        """
        layout: 2D list of Cell or GapCell
        color_set: iterable of colors
        """
        self.layout = layout
        self.color_set = set(color_set)
        self.board = self.create_board()

    def create_board(self):
        """
        Phase 1 + 2: create board with structure
        """
        rows = len(self.layout)
        cols = len(self.layout[0])

        board = Board(
            rows,
            cols,
            self.color_set,
            board_layout=self.layout
        )

        return board

    def modify_cell(
        self,
        r,
        c,
        occupant=None,
        overlay=None,
        underlay=None,
    ):
        """
        Phase 4: deterministic modifications
        """
        if not self.board.can_cell_hold_occupant(r, c):
            return False

        cell = self.board.get_board_element(r, c)

        if occupant is not None:
            cell.occupant = occupant

        if overlay is not None:
            cell.overlay = overlay

        if underlay is not None:
            cell.underlay = underlay

        return True

    def __is_normal_candy(self, occ):
        return isinstance(occ, Candy) and occ.type == CandyType.NORMAL

    def populate_random_candies(self):
        """
        Phase 3: fill cells with random NORMAL candies
        """
        for r in range(self.board.rows):
            for c in range(self.board.cols):
                if not self.board.can_cell_hold_occupant(r, c):
                    continue

                cell = self.board.get_board_element(r, c)
                if cell.occupant is None:
                    self._place_candy(r, c)

    def repopulate_normal_candies(self):
        for r in range(self.board.rows):
            for c in range(self.board.cols):
                occ = self.board.get_occupant(r, c)
                if not self.__is_normal_candy(occ):
                    continue
                self._place_candy(r, c)

    def _place_candy(self, r, c):
        if not self.board.can_cell_hold_occupant(r, c):
            return

        choices = set(self.board.color_set)

        # prevent vertical XXX
        if r >= 2:
            a = self.board.get_occupant(r - 1, c)
            b = self.board.get_occupant(r - 2, c)
            if self.__is_normal_candy(a) and self.__is_normal_candy(b) and a.color == b.color:
                choices.discard(a.color)

        # prevent horizontal XXX
        if c >= 2:
            a = self.board.get_occupant(r, c - 1)
            b = self.board.get_occupant(r, c - 2)
            if self.__is_normal_candy(a) and self.__is_normal_candy(b) and a.color == b.color:
                choices.discard(a.color)

        # prevent 2x2 square
        if r >= 1 and c >= 1:
            a = self.board.get_occupant(r - 1, c)
            b = self.board.get_occupant(r, c - 1)
            d = self.board.get_occupant(r - 1, c - 1)
            if self.__is_normal_candy(a) and self.__is_normal_candy(b) and self.__is_normal_candy(d) and a.color == b.color == d.color:
                choices.discard(a.color)

        if not choices:
            raise RuntimeError("No valid colors available during initialization")

        self.board.get_board_element(r, c).occupant = NormalCandy(random.choice(tuple(choices)))
