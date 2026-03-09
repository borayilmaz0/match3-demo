import random
from Candy import Candy, NormalCandy, CandyFactory


class SpawnLogic:
    def __init__(self, board):
        self.board = board

    def apply(self) -> bool:
        spawned = False
        for c in range(self.board.cols):
            spawned |= self._spawn_column(c)
        return spawned

    # ------------------------------------------------------------

    def _spawn_column(self, c) -> bool:
        spawned = False

        spawn_rows = [
            r for r in range(self.board.rows)
            if self.board.get_board_element(r, c).can_spawn()
        ]

        for r in spawn_rows:
            cell = self.board.get_board_element(r, c)
            if cell.occupant is None:
                cell.occupant = self.spawn_random_candy()
                spawned = True

        return spawned

    def spawn_random_candy(self):
        color = random.choice(self.board.color_set)
        return NormalCandy(color)

    def spawn_custom_candy(self, color, _type):
        return CandyFactory.create(_type, color)