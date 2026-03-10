from BoardDesigner import BoardDesigner
from GameLogic import GameLogic
from Level import Level
from LevelDesigner import LevelDesigner
from LevelLogic import LevelLogic


class GameSession:
    def __init__(self, level: Level):
        self.level_designer = LevelDesigner(level)
        self.level_logic = LevelLogic(self.level_designer)

    def start(self):
        self.level_logic.start_game()
