# main.py

from BoardDesigner import BoardDesigner
from Crate import Crate
from LevelLogic import LevelLogic
from Cell import Cell
from GapCell import GapCell
from ColorType import ColorType
from Candy import Candy
from CandyType import CandyType
from Snow import Snow
from Vines import Vines


def main():
    # --------------------------------------------------
    # 1. Define color set for this level
    # --------------------------------------------------
    color_set = [
        ColorType.RED,
        ColorType.BLUE,
        ColorType.GREEN,
        ColorType.YELLOW,
    ]

    # --------------------------------------------------
    # 2. Define board layout (structure only)
    #    Cell = playable
    #    GapCell = hole
    # --------------------------------------------------
    layout = [
        [Cell(), Cell(), Cell(), Cell(), Cell(), Cell(), Cell(), Cell()],
        [Cell(), Cell(), Cell(), Cell(), Cell(), Cell(), Cell(), Cell()],
        [Cell(), Cell(), Cell(), GapCell(), GapCell(), Cell(), Cell(), Cell()],
        [Cell(), Cell(), Cell(), Cell(), Cell(), Cell(), Cell(), Cell()],
        [Cell(), Cell(), Cell(), Cell(), Cell(), Cell(), Cell(), Cell()],
        [Cell(), Cell(), Cell(), Cell(), Cell(), Cell(), Cell(), Cell()],
        [Cell(), Cell(), Cell(), Cell(), Cell(), Cell(), Cell(), Cell()],
        [Cell(), Cell(), Cell(), Cell(), Cell(), Cell(), Cell(), Cell()],
    ]

    layout = [[Cell(), Cell(), Cell()],[Cell(), Cell(), Cell()],[Cell(), Cell(), Cell()]]

    # --------------------------------------------------
    # 3. Create BoardDesigner
    # --------------------------------------------------
    designer = BoardDesigner(
        layout=layout,
        color_set=color_set
    )

    # --------------------------------------------------
    # 4. Create board (structure + random NORMAL candies)
    # --------------------------------------------------
    board = designer.create_board()
    designer.populate_random_candies(board)

    # --------------------------------------------------
    # 5. Modify specific cells (special candies, blockers, etc.)
    # --------------------------------------------------
    """designer.modify_cell(
        r=4,
        c=3,
        occupant=Candy(ColorType.YELLOW, CandyType.PROPELLER)
    )

    designer.modify_cell(
        r=4,
        c=4,
        occupant=Crate(2),
        underlay=Snow(hp=2)
    )"""

    designer.modify_cell(
        r=0,
        c=0,
        occupant=Candy(ColorType.YELLOW, CandyType.ROCKET_H),
        overlay=Vines(),
        underlay=Snow()
    ) 

    designer.modify_cell(
        r=0,
        c=1,
        occupant=Candy(ColorType.YELLOW, CandyType.ROCKET_H))

    # --------------------------------------------------
    # 6. Create LevelLogic
    # --------------------------------------------------
    level = LevelLogic(
        designer,
        move_count=1
    )

    # --------------------------------------------------
    # 7. Start game loop
    # --------------------------------------------------
    level.start_game()


if __name__ == "__main__":
    main()