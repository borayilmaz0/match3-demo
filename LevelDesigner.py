# LevelDesigner.py
from BoardDesigner import BoardDesigner
from EventBus import EventBus
from GameEvents import EntityClearedEvent
from ObjectiveManager import ObjectiveManager


class LevelDesigner:
    def __init__(self, level):
        self.level = level
        self.event_bus = EventBus()
        self.board_designer = BoardDesigner(level.layout, level.color_set)
        self.board_designer.populate_random_candies()
        self._wire_event_bus()
        self.objective_manager = ObjectiveManager()

    def set_objectives(self) -> None:
        self.level.set_objectives()

        for obj in self.level.objectives:
            self.objective_manager.add_objective(obj)

        self._wire_event_bus()

        # Single subscription — no per-cell loop needed.
        self.event_bus.subscribe(
            EntityClearedEvent,
            self.objective_manager.on_entity_cleared,
        )

        self.objective_manager.start(self.board_designer.board)


    def _wire_event_bus(self) -> None:
        """
        Push the EventBus reference into every cell on the board.
        Called once during __init__, before objectives are registered.
        GapCell.set_event_bus() is a silent no-op, so no type checks needed.
        """
        board = self.board_designer.board
        for r in range(board.rows):
            for c in range(board.cols):
                board.get_board_element(r, c).set_event_bus(self.event_bus)
