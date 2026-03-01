# LevelDesigner.py
from BoardDesigner import BoardDesigner
from ObjectiveManager import ObjectiveManager


class LevelDesigner:
    def __init__(self, level):
        self.level = level
        self.board_designer = BoardDesigner(level.layout, level.color_set)
        self.board_designer.populate_random_candies()
        self.objective_manager = ObjectiveManager()

    def set_objectives(self):
        self.level.set_objectives()
        for obj in self.level.objectives:
            self.objective_manager.add_objective(obj)

        for r in range(self.board_designer.board.rows):
            for c in range(self.board_designer.board.cols):
                self.board_designer.board.get_board_element(r, c).add_listener(self.objective_manager)
        self.objective_manager.start(self.board_designer.board)
