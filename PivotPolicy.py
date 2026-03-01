from abc import ABC, abstractmethod

class PivotPolicy(ABC):
    @abstractmethod
    def choose_pivot(self, group: set[tuple[int,int]]):
        ...