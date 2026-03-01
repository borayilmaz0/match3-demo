from abc import ABC, abstractmethod

from Behavior import Behavior


class MatchBlocking(ABC, Behavior):
    """
    Behavior for entities (typically overlays) that prevent the cell occupant
    from being considered for match/deadlock detection.
    """
    @abstractmethod
    def blocks_matching(self) -> bool:
        pass