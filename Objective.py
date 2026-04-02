from abc import ABC, abstractmethod

from GameEvents import GameEvent


class Objective(ABC):
    @abstractmethod
    def on_event(self, event: GameEvent):
        pass

    @abstractmethod
    def is_completed(self) -> bool:
        pass

    @abstractmethod
    def start(self, board):
        pass
