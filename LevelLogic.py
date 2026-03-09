from time import sleep

from BoardDesigner import BoardDesigner
from ClearEntityObjective import ClearEntityObjective
from GameLogic import GameLogic
from LevelDesigner import LevelDesigner


class LevelLogic:
    def __init__(self, level_designer: LevelDesigner):
        self.level_designer = level_designer
        self.board_designer = self.level_designer.board_designer
        self.game_logic = GameLogic(self.board_designer.board)

    def start_game(self):
        self.level_designer.set_objectives()
        while self.level_designer.level.moves > 0 and not self.level_designer.objective_manager.all_completed():
            while self.game_logic.deadlock_logic.find_any_valid_swap() is None:
                print("no moves were found, should reshuffle normal candies, repopulating")
                self.board_designer.repopulate_normal_candies()
                sleep(0.1)
            print(f"obj:\n{self.level_designer.objective_manager}")
            print(self.board_designer.board)

            move = input(f"enter move ({self.level_designer.level.moves} left):") # "tap <r>,<c>" "or swap <r1>, <c1>, up|down|left|right"
            move_type, coordinates = self._resolve_move(move)
            if move_type == "invalid":
                print("invalid move")
            elif move_type == "swap":
                if self.game_logic.try_swap(coordinates[0][0], coordinates[0][1], coordinates[1][0], coordinates[1][1]):
                    self.level_designer.level.moves -= 1
                else:
                    print("invalid swap")
            elif move_type == "tap":
                if self.game_logic.tap(coordinates[0][0], coordinates[0][1]):
                    self.level_designer.level.moves -= 1
                else:
                    print("invalid tap")
        if self.level_designer.objective_manager.all_completed():
            print("game win!!!")
            return True
        else:
            print("game over :(")
            return False

    def _resolve_move(self, move):
        """
        Parses console input into a move.
        Supported:
          - tap r,c
          - swap r,c up|down|left|right
        """
        try:
            parts = move.strip().lower().split()
            if not parts:
                return "invalid", None

            # ----------------
            # TAP
            # ----------------
            if parts[0] == "tap" and len(parts) == 2:
                r, c = map(int, parts[1].split(","))
                return "tap", [(r, c)]

            # ----------------
            # SWAP
            # ----------------
            if parts[0] == "swap" and len(parts) == 3:
                r, c = map(int, parts[1].split(","))
                direction = parts[2]

                drdc = {
                    "up": (-1, 0),
                    "down": (1, 0),
                    "left": (0, -1),
                    "right": (0, 1),
                }

                if direction not in drdc:
                    return "invalid", None

                dr, dc = drdc[direction]
                r2, c2 = r + dr, c + dc

                return "swap", [(r, c), (r2, c2)]

        except ValueError:
            return "invalid", None

        return "invalid", None