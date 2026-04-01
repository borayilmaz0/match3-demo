from Matchable import Matchable


class MatchDetectionLogic:
    def __init__(self, board):
        self.board = board

    def _is_matchable(self, entity):
        if entity is None:
            return False
        matchable = entity.get(Matchable)
        return matchable is not None and matchable.can_be_matched()

    # ------------------------------------------------------------
    # Collect all matched cells caused by pivot (r, c)
    # ------------------------------------------------------------
    def collect_matches_at(
            self,
            r: int,
            c: int,
            get_cell_occupant_fn=None,
    ):
        if get_cell_occupant_fn is None:
            get_cell_occupant_fn = self.board.get_occupant

        if not self.board.can_cell_hold_occupant(r, c):
            return set()

        origin = get_cell_occupant_fn(r, c)
        if not self._is_matchable(origin):
            return set()

        origin_color = origin.color
        matches = set()

        # =========================
        # Horizontal scan
        # =========================
        horiz = [(r, c)]

        cc = c - 1
        while self.board.can_cell_hold_occupant(r, cc):
            b = get_cell_occupant_fn(r, cc)
            if not self._is_matchable(b) or b.color != origin_color:
                break
            horiz.append((r, cc))
            cc -= 1

        cc = c + 1
        while self.board.can_cell_hold_occupant(r, cc):
            b = get_cell_occupant_fn(r, cc)
            if not self._is_matchable(b) or b.color != origin_color:
                break
            horiz.append((r, cc))
            cc += 1

        if len(horiz) >= 3:
            matches.update(horiz)

        # =========================
        # Vertical scan
        # =========================
        vert = [(r, c)]

        rr = r - 1
        while self.board.can_cell_hold_occupant(rr, c):
            b = get_cell_occupant_fn(rr, c)
            if not self._is_matchable(b) or b.color != origin_color:
                break
            vert.append((rr, c))
            rr -= 1

        rr = r + 1
        while self.board.can_cell_hold_occupant(rr, c):
            b = get_cell_occupant_fn(rr, c)
            if not self._is_matchable(b) or b.color != origin_color:
                break
            vert.append((rr, c))
            rr += 1

        if len(vert) >= 3:
            matches.update(vert)

        # =========================
        # 2x2 square scan
        # =========================
        for dr in (-1, 0):
            for dc in (-1, 0):
                square_coords = [
                    (r + dr, c + dc),
                    (r + dr + 1, c + dc),
                    (r + dr, c + dc + 1),
                    (r + dr + 1, c + dc + 1),
                ]

                if not all(
                        self.board.can_cell_hold_occupant(rr, cc)
                        for rr, cc in square_coords
                ):
                    continue

                blocks = [
                    get_cell_occupant_fn(rr, cc)
                    for rr, cc in square_coords
                ]

                if not all(self._is_matchable(b) for b in blocks):
                    continue

                color = blocks[0].color
                if all(b.color == color for b in blocks):
                    matches.update(square_coords)

        return matches

    # ------------------------------------------------------------
    # Collect all matches on the board
    # ------------------------------------------------------------
    def collect_all_matches(self):
        visited = set()
        matches = []

        for r in range(self.board.rows):
            for c in range(self.board.cols):
                if (r, c) in visited:
                    continue

                if not self.board.can_cell_hold_occupant(r, c):
                    continue

                origin = self.board.get_board_element(r, c).occupant
                if not self._is_matchable(origin):
                    continue

                match = self.collect_matches_at(r, c)
                if match:
                    matches.append(match)
                    visited |= match

        return matches
