from Cell import Cell
from GapCell import GapCell
from Level import Level
from ColorType import ColorType
from ClearEntityObjective import ClearEntityObjective
from Candy import *
from Snow import Snow
from Vines import Vines


class Level1(Level):

    def __init__(self):
        super().__init__()
        self.color_set = [
            ColorType.RED, ColorType.BLUE, ColorType.GREEN, ColorType.YELLOW
        ]
        self.moves = 20
        """self.layout = [
            [Cell(), Cell(), Cell(), Cell(), Cell(), Cell(), Cell(), Cell()],
            [Cell(), Cell(), Cell(), Cell(), Cell(), Cell(), Cell(), Cell()],
            [Cell(), Cell(), Cell(), GapCell(), GapCell(), Cell(), Cell(), Cell()],
            [Cell(), Cell(), Cell(), Cell(), Cell(), Cell(), Cell(), Cell()],
            [Cell(), Cell(), Cell(), Cell(), Cell(), Cell(), Cell(), Cell()],
            [Cell(), Cell(), Cell(), Cell(), Cell(), Cell(), Cell(), Cell()],
            [Cell(), Cell(), Cell(), Cell(), Cell(), Cell(), Cell(), Cell()],
            [Cell(), Cell(), Cell(), Cell(), Cell(), Cell(), Cell(), Cell()],
        ]"""
        self.layout = [[Cell(), Cell(), Cell(),
                        Cell(), Cell()],
                       [Cell(), Cell(), Cell(),
                        Cell(), Cell()],
                       [Cell(), Cell(), Cell(),
                        Cell(), Cell()],
                       [Cell(), Cell(), Cell(),
                        Cell(), Cell()],
                       [Cell(), Cell(), Cell(),
                        Cell(), Cell()]]
        self.rows = len(self.layout)
        self.cols = len(self.layout[0])

        self.objectives = []

    def set_objectives(self):
        self.layout[0][0] = Cell(
            occupant=RocketVCandy(ColorType.YELLOW),
            overlay=Vines(),
            underlay=Snow(),
        )

        self.layout[1][1] = Cell(occupant=RocketVCandy(ColorType.YELLOW),
                                 underlay=Snow())
        self.layout[1][2] = Cell(occupant=BombCandy(ColorType.YELLOW),
                                 underlay=Snow())

        self.objectives = [
            ClearEntityObjective(Vines),
            ClearEntityObjective(Snow)
        ]
