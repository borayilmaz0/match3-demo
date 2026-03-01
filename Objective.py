from abc import ABC, abstractmethod


class Objective(ABC):
    @abstractmethod
    def on_event(self, event):
        pass

    @abstractmethod
    def is_completed(self) -> bool:
        pass

    @abstractmethod
    def start(self, board):
        pass