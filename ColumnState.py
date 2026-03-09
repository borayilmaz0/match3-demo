# ColumnState.py
from enum import Enum, auto


class ColumnState(Enum):
    STABLE = auto()
    LOCKED = auto()
    FALLING = auto()