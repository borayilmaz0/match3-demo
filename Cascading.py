from abc import ABC, abstractmethod

from Behavior import Behavior


class Cascading(ABC, Behavior):
    @abstractmethod
    def can_fall(self) -> bool:
        pass