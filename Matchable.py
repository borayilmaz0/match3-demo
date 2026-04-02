from abc import ABC, abstractmethod

from Behavior import Behavior


class Matchable(ABC, Behavior):
    """
    Behavior for entities that can participate in match-3 pattern detection.
    Only entities with this behavior are considered by MatchDetectionLogic.
    """
    @abstractmethod
    def can_be_matched(self) -> bool:
        pass
