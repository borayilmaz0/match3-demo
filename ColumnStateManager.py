from ColumnState import ColumnState


class ColumnStateManager:
    def __init__(self, cols):
        self.states = [ColumnState.STABLE for _ in range(cols)]

    def is_stable(self, col):
        return self.states[col] == ColumnState.STABLE

    def is_locked(self, col):
        return self.states[col] == ColumnState.LOCKED

    def is_falling(self, col):
        return self.states[col] == ColumnState.FALLING

    def can_interact(self, col):
        return self.is_stable(col)

    def can_match(self, col):
        return not self.is_falling(col)

    def lock(self, col: int):
        self.states[col] = ColumnState.LOCKED

    def lock_many(self, cols):
        for col in set(cols):
            self.lock(col)

    def start_falling(self, col):
        self.states[col] = ColumnState.FALLING

    def start_falling_many(self, cols):
        for col in set(cols):
            self.start_falling(col)

    def set_stable(self, col):
        self.states[col] = ColumnState.STABLE

    def set_stable_many(self, cols):
        for col in set(cols):
            self.set_stable(col)

    def any_falling(self):
        return any(s == ColumnState.FALLING for s in self.states)

    def any_locked(self):
        return any(s == ColumnState.LOCKED for s in self.states)

    def __str__(self):
        return str(self.states)