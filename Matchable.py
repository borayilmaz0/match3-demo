from abc import ABC, abstractmethod

from Behavior import Behavior


class Matchable(ABC, Behavior):
    """
    TODO: Ideally reserved for future use. Occupants like Candy
    should have this trait because they are trivially matchable on
    Board. Though the game is not scaled enough to make use of this
    behavioral abstraction yet.
    """
    @abstractmethod
    def can_be_matched(self) -> bool:
        pass