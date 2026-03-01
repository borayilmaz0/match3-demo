from PivotPolicy import PivotPolicy


class CascadePivotPolicy(PivotPolicy):
    def choose_pivot(self, cells: set[tuple[int, int]]):
        rows = [r for r, _ in cells]
        cols = [c for _, c in cells]

        center = (sum(rows) // len(rows), sum(cols) // len(cols))
        if center in cells:
            return center

        return min(cells)