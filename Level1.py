from Cell import Cell
from GapCell import GapCell
from Level import Level
from ColorType import ColorType
from ClearEntityObjective import ClearEntityObjective
from Candy import RocketHCandy, RocketVCandy
from Snow import Snow
from Vines import Vines


class Level1(Level):
    def __init__(self):
        super().__init__()
        self.color_set = [ColorType.RED, ColorType.BLUE, ColorType.GREEN, ColorType.YELLOW]
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
        self.layout = [
            [Cell(), Cell(), Cell()],
            [Cell(), Cell(), Cell()],
            [Cell(), Cell(), Cell()]]
        self.rows = len(self.layout)
        self.cols = len(self.layout[0])

        self.objectives = []


    def set_objectives(self):
        self.layout[0][0] = Cell(
            occupant=RocketHCandy(ColorType.YELLOW),
            overlay=Vines(),
            underlay=Snow(),
        )

        self.layout[0][1] = Cell(
            occupant=RocketHCandy(ColorType.YELLOW))
        self.layout[0][2] = Cell(
            occupant=RocketVCandy(ColorType.YELLOW))

        self.objectives = [ClearEntityObjective(Vines), ClearEntityObjective(Snow)]
