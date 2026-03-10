from enum import Enum, auto


class BoardResolutionPhase(Enum):
    IDLE = auto()
    RESOLVING_INPUT = auto()
    RESOLVING_EFFECTS = auto()
    FALLING = auto()
    SPAWNING = auto()
    MATCHING = auto()
    STABLE = auto()
