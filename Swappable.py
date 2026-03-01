from abc import ABC, abstractmethod

from Behavior import Behavior


class Swappable(ABC, Behavior):
    @abstractmethod
    def can_swap(self) -> bool:
        pass