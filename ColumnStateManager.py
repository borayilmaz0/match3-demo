from ColumnState import ColumnState


class ColumnStateManager:
    def __init__(self, cols):
        self.states = [ColumnState.STEADY for _ in range(cols)]
        self._reserved_rows: dict[int, set[int]] = {c: set() for c in range(cols)}
        self._unstable_rows: dict[int, set[int]] = {c: set() for c in range(cols)}

    def is_steady(self, col):
        return self.states[col] == ColumnState.STEADY

    def is_locked(self, col):
        return self.states[col] == ColumnState.LOCKED

    def is_falling(self, col):
        return self.states[col] == ColumnState.FALLING

    def reserve(self, col: int, rows):
        self._reserved_rows[col].update(rows)

    def release(self, col: int, rows=None):
        if rows is None:
            self._reserved_rows[col].clear()
            return
        self._reserved_rows[col].difference_update(rows)

    def mark_unstable(self, col: int, rows):
        self._unstable_rows[col].update(rows)

    def clear_unstable(self, col: int, rows=None):
        if rows is None:
            self._unstable_rows[col].clear()
            return
        self._unstable_rows[col].difference_update(rows)

    def reserved_rows(self, col: int):
        return set(self._reserved_rows[col])

    def unstable_rows(self, col: int):
        return set(self._unstable_rows[col])

    def can_interact(self, col, row=None):
        if self.is_locked(col):
            return False
        if row is None:
            return self.is_steady(col) and not self._reserved_rows[col] and not self._unstable_rows[col]
        if row in self._reserved_rows[col]:
            return False
        if row in self._unstable_rows[col]:
            return False
        return True

    def can_match(self, col, row=None):
        if row is None:
            return not self.is_falling(col)
        if row in self._reserved_rows[col]:
            return False
        if row in self._unstable_rows[col]:
            return False
        return not self.is_locked(col)

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

    def set_steady(self, col):
        self.states[col] = ColumnState.STEADY
        self._reserved_rows[col].clear()
        self._unstable_rows[col].clear()

    def set_steady_many(self, cols):
        for col in set(cols):
            self.set_steady(col)

    def any_falling(self):
        return any(s == ColumnState.FALLING for s in self.states)

    def any_locked(self):
        return any(s == ColumnState.LOCKED for s in self.states)

    def clear_all_transients(self):
        for c in range(len(self.states)):
            self._reserved_rows[c].clear()
            self._unstable_rows[c].clear()

    def __str__(self):
        return str(self.states)
