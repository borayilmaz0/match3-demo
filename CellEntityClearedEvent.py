class CellEntityClearedEvent:
    """
    Emitted when a cell entity (overlay / occupant / underlay)
    is fully destroyed and removed from the board.
    """

    __slots__ = ("entity",)

    def __init__(self, entity):
        self.entity = entity

    def __str__(self):
        return f"{self.entity.__class__.__name__} cleared"