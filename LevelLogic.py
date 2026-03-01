from BoardDesigner import BoardDesigner
from ClearEntityObjective import ClearEntityObjective
from GameLogic import GameLogic
from ObjectiveManager import ObjectiveManager
from Snow import Snow
from Vines import Vines


class LevelLogic:
    def __init__(self, board_designer: BoardDesigner, move_count: int):
        self.board_designer = board_designer
        self.board = self.board_designer.board
        self.move_count = move_count
        self.objective_manager = ObjectiveManager()
        self.objective_manager.add_objective(ClearEntityObjective(Vines))
        self.objective_manager.add_objective(ClearEntityObjective(Snow))

        self.game_logic = GameLogic(self.board)
    def start_game(self):
        for r in range(self.board.rows):
            for c in range(self.board.cols):
                cell = self.board.get_board_element(r, c)
                cell.add_listener(self.objective_manager)
        self.objective_manager.start(self.board)
        while self.move_count > 0 and not self.objective_manager.all_completed():
            while self.game_logic.deadlock_logic.find_any_valid_swap() is None:
                print("no moves were found, should reshuffle normal candies, repopulating")
                self.board_designer.repopulate_normal_candies()
            print(f"obj:\n{self.objective_manager}")
            print(self.board)


            # get a move input
            move = input(f"enter move ({self.move_count} left):") # "tap <r>,<c>" "or swap <r1>, <c1>, up|down|left|right"
            move_type, coordinates = self._resolve_move(move)
            if move_type == "invalid":
                print("invalid move")
            elif move_type == "swap":
                if self.game_logic.try_swap(coordinates[0][0], coordinates[0][1], coordinates[1][0], coordinates[1][1]):
                    self.move_count -= 1
                else:
                    print("invalid swap")
            elif move_type == "tap":
                if self.game_logic.tap(coordinates[0][0], coordinates[0][1]):
                    self.move_count -= 1
                else:
                    print("invalid tap")
        if self.objective_manager.all_completed():
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

        except Exception:
            return "invalid", None

        return "invalid", None