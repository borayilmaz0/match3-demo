import random
from Candy import NormalCandy, CandyFactory
from GameEvents import SpawnedEvent


class SpawnLogic:
    def __init__(self, board, event_bus=None):
        self.board = board
        self.event_bus = event_bus

    def apply(self) -> bool:
        spawned = False
        for c in range(self.board.cols):
            spawned |= self._spawn_column(c)
        return spawned

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
                if self.event_bus is not None:
                    self.event_bus.emit(SpawnedEvent(position=(r, c), entity=cell.occupant))

        return spawned

    def spawn_random_candy(self):
        color = random.choice(self.board.color_set)
        return NormalCandy(color)

    def spawn_custom_candy(self, color, _type):
        return CandyFactory.create(_type, color)
