from Swappable import Swappable


class LockedSwappable(Swappable):
    def can_swap(self) -> bool:
        return False