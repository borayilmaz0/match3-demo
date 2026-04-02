from GameEvents import EntityClearedEvent


class ObjectiveManager:
    def __init__(self):
        self.objectives = []

    def add_objective(self, objective):
        self.objectives.append(objective)

    def on_entity_cleared(self, event: EntityClearedEvent) -> None:
        """Called by the EventBus whenever a Cell removes an entity."""
        for obj in self.objectives:
            obj.on_event(event)

    def start(self, board):
        for obj in self.objectives:
            obj.start(board)

    def all_completed(self) -> bool:
        return all(obj.is_completed() for obj in self.objectives)

    def __str__(self):
        return "\n".join(str(obj) for obj in self.objectives)
