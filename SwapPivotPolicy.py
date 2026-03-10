from PivotPolicy import PivotPolicy


class SwapPivotPolicy(PivotPolicy):
    def __init__(self, swapped_positions):
        # preserve order: [(r1,c1), (r2,c2)]
        self.swapped = list(swapped_positions)

    def choose_pivot(self, cells: set[tuple[int, int]]):
        for pos in self.swapped:
            if pos in cells:
                return pos
        return None
