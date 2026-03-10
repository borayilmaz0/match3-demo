from Candy import Candy
from CandyType import CandyType


class MatchDetectionLogic:
    def __init__(self, board):
        self.board = board

    # ------------------------------------------------------------
    # Collect all matched cells caused by pivot (r, c)
    # ------------------------------------------------------------
    def collect_matches_at(
            self,
            r: int,
            c: int,
            get_cell_occupant_fn=None,
    ):
        if not self.board.column_states.can_match(c, r):
            return set()

        if get_cell_occupant_fn is None:
            get_cell_occupant_fn = self.board.get_occupant

        if not self.board.can_cell_hold_occupant(r, c):
            return set()

        origin = get_cell_occupant_fn(r, c)
        if not isinstance(origin, Candy) or origin.type != CandyType.NORMAL:
            return set()

        matches = set()

        # =========================
        # Horizontal scan
        # =========================
        horiz = [(r, c)]

        cc = c - 1
        while self.board.can_cell_hold_occupant(r, cc) and self.board.column_states.can_match(cc, r):
            b = get_cell_occupant_fn(r, cc)
            if (
                not isinstance(b, Candy)
                or b.type != CandyType.NORMAL
                or b.color != origin.color
            ):
                break
            horiz.append((r, cc))
            cc -= 1

        cc = c + 1
        while self.board.can_cell_hold_occupant(r, cc) and self.board.column_states.can_match(cc, r):
            b = get_cell_occupant_fn(r, cc)
            if (
                not isinstance(b, Candy)
                or b.type != CandyType.NORMAL
                or b.color != origin.color
            ):
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
            if (
                not isinstance(b, Candy)
                or b.type != CandyType.NORMAL
                or b.color != origin.color
            ):
                break
            vert.append((rr, c))
            rr -= 1

        rr = r + 1
        while self.board.can_cell_hold_occupant(rr, c):
            b = get_cell_occupant_fn(rr, c)
            if (
                not isinstance(b, Candy)
                or b.type != CandyType.NORMAL
                or b.color != origin.color
            ):
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

                # all positions must be valid
                if not all(
                        self.board.can_cell_hold_occupant(rr, cc)
                        and self.board.column_states.can_match(cc, rr)
                        for rr, cc in square_coords
                ):
                    continue

                blocks = [
                    get_cell_occupant_fn(rr, cc)
                    for rr, cc in square_coords
                ]

                if any(
                    not isinstance(b, Candy) or b.type != CandyType.NORMAL
                    for b in blocks
                ):
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

                if not self.board.column_states.can_match(c, r):
                    continue

                if not self.board.can_cell_hold_occupant(r, c):
                    continue

                origin = self.board.get_board_element(r, c).occupant
                if not isinstance(origin, Candy) or origin.type != CandyType.NORMAL:
                    continue

                match = self.collect_matches_at(r, c)
                if match:
                    matches.append(match)
                    visited |= match

        return matches
