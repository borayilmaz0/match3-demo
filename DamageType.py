from enum import Enum, auto


class DamageType(Enum):
    MATCH_NEAR = 1
    MATCH = 2
    ENHANCED = 3

    def __gt__(self, other):
        return self.value > other.value

    def __ge__(self, other):
        return self.value >= other.value

    def __lt__(self, other):
        return self.value < other.value

    def __le__(self, other):
        return self.value <= other.value
