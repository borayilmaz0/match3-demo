
from typing import NamedTuple


class Position(NamedTuple):
    """
    Typed (row, col) coordinate.

    Because it inherits from NamedTuple it is still a plain tuple under
    the hood, so every existing `r, c = pos` unpack and every dict/set
    key that currently uses a raw tuple continue to work unchanged.
    The 2-D board array is untouched — Position is only used at the
    *interface* level (method signatures, MatchResult, PivotPolicy).

    Unity migration path:
        Position  →  Vector2Int
        pos.r     →  pos.x  (or pos.y depending on axis convention)
        pos.c     →  pos.y
    """
    r: int
    c: int

    # ------------------------------------------------------------------
    # Convenience helpers (mirrors common Vector2Int operations)
    # ------------------------------------------------------------------

    def __add__(self, other: "Position") -> "Position":
        return Position(self.r + other.r, self.c + other.c)

    def __sub__(self, other: "Position") -> "Position":
        return Position(self.r - other.r, self.c - other.c)

    def manhattan(self, other: "Position") -> int:
        return abs(self.r - other.r) + abs(self.c - other.c)

    def neighbors(self):
        """Yields the four cardinal neighbors."""
        for dr, dc in ((-1, 0), (1, 0), (0, -1), (0, 1)):
            yield Position(self.r + dr, self.c + dc)

    def __repr__(self) -> str:
        return f"Position(r={self.r}, c={self.c})"