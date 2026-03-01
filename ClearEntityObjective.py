from Objective import Objective


class ClearEntityObjective(Objective):
    def __init__(self, entity_type):
        self.entity_type = entity_type
        self.count = 0

    def on_event(self, event):
        if isinstance(event, self.entity_type):
            self.count -= 1

    def is_completed(self) -> bool:
        return self.count == 0

    def start(self, board):
        count = 0
        for r in range(board.rows):
            for c in range(board.cols):
                cell = board.get_board_element(r, c)

                for entity in (cell.overlay, cell.occupant, cell.underlay):
                    if isinstance(entity, self.entity_type):
                        count += 1
        self.count = count

    def __str__(self):
        return (
            f"Clear {self.entity_type.__name__}: "
            f"{self.count}"
        )