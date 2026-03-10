from enum import Enum, auto

class ColumnState(Enum):
    STEADY = auto()
    LOCKED = auto()
    FALLING = auto()
