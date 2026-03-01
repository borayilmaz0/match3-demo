class MatchResult:
    def __init__(self, cells_to_remove, spawn_pos=None, pivot_candy=None, spawn_candy=None):
        self.cells_to_remove = cells_to_remove  # set[(r, c)]
        self.spawn_pos = spawn_pos               # (r, c) or None
        self.pivot_candy = pivot_candy
        self.spawn_candy = spawn_candy           # Candy or None

    def has_special(self):
        return self.spawn_candy is not None