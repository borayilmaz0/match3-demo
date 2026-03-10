import random
from DamageContext import DamageContext
from DamageType import DamageType
from CandyType import CandyType
from Candy import Candy, CandyFactory
from MatchResult import MatchResult


class SpecialActivationLogic:

    def __init__(self, board, damage_logic):
        self.board = board
        self.damage_logic = damage_logic
        self._impacted_columns = set()
        self._activating_positions = set()

        # ------------------------------------------------------------
        # Handler registries
        # ------------------------------------------------------------

        # Swap activation: handler(pos, candy, neighbor_candy) -> bool or None
        self._swap_handlers = {
            CandyType.ROCKET_H:
            lambda pos, candy, neighbor: self._rocket_h(pos),
            CandyType.ROCKET_V:
            lambda pos, candy, neighbor: self._rocket_v(pos),
            CandyType.BOMB:
            lambda pos, candy, neighbor: self._bomb(pos),
            CandyType.PROPELLER:
            lambda pos, candy, neighbor: self._propeller(pos, pre_damage=True),
        }

        # Hit activation: handler(pos, candy) -> None
        self._hit_handlers = {
            CandyType.ROCKET_H:
            lambda pos, candy: self._rocket_h(pos),
            CandyType.ROCKET_V:
            lambda pos, candy: self._rocket_v(pos),
            CandyType.BOMB:
            lambda pos, candy: self._bomb(pos),
            CandyType.PROPELLER:
            lambda pos, candy: self._propeller(pos, pre_damage=True),
            CandyType.LIGHT_BALL:
            lambda pos, candy: self._light_ball_on_hit(
                pos, random.choice(list(self.board.color_set))),
        }

        # Ordered combos: (type_a, type_b) means "a swapped into b"
        # handler(pos_a, pos_b, candy_a, candy_b) -> None
        self._combo_handlers_ordered = {
            # ---------------------------------------------------------
            # ROCKET + ROCKET
            # ---------------------------------------------------------
            (CandyType.ROCKET_H, CandyType.ROCKET_H): self._combo_cross_rocket,
            (CandyType.ROCKET_H, CandyType.ROCKET_V): self._combo_cross_rocket,
            (CandyType.ROCKET_V, CandyType.ROCKET_H): self._combo_cross_rocket,
            (CandyType.ROCKET_V, CandyType.ROCKET_V): self._combo_cross_rocket,

            # ---------------------------------------------------------
            # BOMB COMBOS
            # ---------------------------------------------------------
            (CandyType.BOMB, CandyType.BOMB): self._combo_mega_bomb,
            (CandyType.ROCKET_H, CandyType.BOMB): self._combo_rocket_bomb,
            (CandyType.ROCKET_V, CandyType.BOMB): self._combo_rocket_bomb,
            (CandyType.BOMB, CandyType.ROCKET_H): self._combo_rocket_bomb,
            (CandyType.BOMB, CandyType.ROCKET_V): self._combo_rocket_bomb,

            # ---------------------------------------------------------
            # PROPELLER COMBOS
            # ---------------------------------------------------------
            (CandyType.PROPELLER, CandyType.PROPELLER): self._combo_propeller_propeller,
            (CandyType.PROPELLER, CandyType.ROCKET_H): self._combo_propeller_rocket_h,
            (CandyType.PROPELLER, CandyType.ROCKET_V): self._combo_propeller_rocket_v,
            (CandyType.ROCKET_H, CandyType.PROPELLER): self._combo_propeller_rocket_h,
            (CandyType.ROCKET_V, CandyType.PROPELLER): self._combo_propeller_rocket_v,
            (CandyType.PROPELLER, CandyType.BOMB): self._combo_propeller_bomb,
            (CandyType.BOMB, CandyType.PROPELLER): self._combo_propeller_bomb,

            # ---------------------------------------------------------
            # LIGHT BALL COMBOS
            # ---------------------------------------------------------
            (CandyType.LIGHT_BALL, CandyType.NORMAL): self._combo_light_ball_normal,
            (CandyType.NORMAL, CandyType.LIGHT_BALL): self._combo_light_ball_normal,

            (CandyType.LIGHT_BALL, CandyType.ROCKET_H): self._combo_light_ball_rocket,
            (CandyType.LIGHT_BALL, CandyType.ROCKET_V): self._combo_light_ball_rocket,
            (CandyType.ROCKET_H, CandyType.LIGHT_BALL): self._combo_light_ball_rocket,
            (CandyType.ROCKET_V, CandyType.LIGHT_BALL): self._combo_light_ball_rocket,

            (CandyType.LIGHT_BALL, CandyType.BOMB): self._combo_light_ball_bomb,
            (CandyType.BOMB, CandyType.LIGHT_BALL): self._combo_light_ball_bomb,

            (CandyType.LIGHT_BALL, CandyType.PROPELLER): self._combo_light_ball_propeller,
            (CandyType.PROPELLER, CandyType.LIGHT_BALL): self._combo_light_ball_propeller,

            (CandyType.LIGHT_BALL, CandyType.LIGHT_BALL): self._combo_light_ball_light_ball,
        }

    def _collect_normal_candies_of_color(self, color):
        positions = []
        for r in range(self.board.rows):
            for c in range(self.board.cols):
                if not self.board.can_cell_hold_occupant(r, c):
                    continue
                cell = self.board.get_board_element(r, c)
                occ = cell.occupant
                if isinstance(
                        occ, Candy
                ) and occ.type == CandyType.NORMAL and occ.color == color:
                    positions.append((r, c))
        return positions

    # ============================================================
    # PUBLIC API
    # ============================================================

    def activate_on_swap(self, pos, candy, neighbor_candy):
        self._impacted_columns.clear()
        if candy is None:
            return False

        handler = self._swap_handlers.get(candy.type)
        if handler is None:
            return False

        handler(pos, candy, neighbor_candy)
        return True

    def activate_on_hit(self, pos, candy, ctx=None):
        if candy is None:
            return False
        if pos in self._activating_positions:
            return False
        handler = self._hit_handlers.get(candy.type)
        if handler is None:
            return False

        self._activating_positions.add(pos)
        try:
            cell = self.board.get_board_element(*pos)
            if cell.occupant is candy:
                cell.occupant = None

            handler(pos, candy)
            return True
        finally:
            self._activating_positions.remove(pos)

    # ============================================================
    # ORDERED SWAP COMBOS (INFRASTRUCTURE ONLY)
    # ============================================================

    def can_activate_combo_on_swap(self, candy_a, candy_b) -> bool:
        if not isinstance(candy_a, Candy) or not isinstance(candy_b, Candy):
            return False
        return (candy_a.type, candy_b.type) in self._combo_handlers_ordered

    def activate_combo_on_swap(self, pos_a, pos_b, candy_a, candy_b) -> bool:
        self._impacted_columns.clear()
        if not self.can_activate_combo_on_swap(candy_a, candy_b):
            return False

        handler = self._combo_handlers_ordered[(candy_a.type, candy_b.type)]
        if handler is None:
            return False

        handler(pos_a, pos_b, candy_a, candy_b)
        return True

    def _consume_occupant_if_present(self, pos):

        if not self.board.can_cell_hold_occupant(pos[0], pos[1]):
            return

        cell = self.board.get_board_element(*pos)
        if cell.occupant is not None:
            cell.occupant = None

    # ============================================================
    # IMPLEMENTATIONS (BASE SPECIALS)
    # ============================================================

    def _rocket_h(self, pos):
        r, c = pos
        for cc in range(self.board.cols):
            self._apply_enhanced_damage(r, cc)

    def _rocket_v(self, pos):
        r, c = pos
        for rr in range(self.board.rows):
            self._apply_enhanced_damage(rr, c)

    def _bomb(self, pos):
        r, c = pos
        for dr in range(-2, 3):
            for dc in range(-2, 3):
                self._apply_enhanced_damage(r + dr, c + dc)

    def _propeller(self, pos, pre_damage):
        r, c = pos

        self._apply_enhanced_damage(r, c)
        if pre_damage:
            self._propeller_neighbor_damage(pos)

        target = self._find_random_valid_target()
        self._apply_enhanced_damage(*target)

    def _light_ball_on_hit(self, pos, color):
        for r in range(self.board.rows):
            for c in range(self.board.cols):
                if not self.board.can_cell_hold_occupant(r, c):
                    continue

                cell = self.board.get_board_element(r, c)
                if not isinstance(cell.occupant, Candy):
                    continue

                if cell.occupant.color == color:
                    cell.apply_damage(
                        DamageContext(DamageType.MATCH, color=color))

        self._apply_enhanced_damage(pos[0], pos[1])

    # ============================================================
    # COMBO IMPLEMENTATIONS
    # ============================================================

    def _combo_cross_rocket(self, pos_a, pos_b, candy_a, candy_b):
        """
        ROCKET + ROCKET → cross rocket
        Centered on pos_b (the 'swapped-into' position)
        """
        self._consume_occupant_if_present(pos_a)
        self._consume_occupant_if_present(pos_b)
        print("before action:\n", self.board)
        self._rocket_h(pos_b)
        self._rocket_v(pos_b)
        print("after action:\n", self.board)

    def _combo_mega_bomb(self, pos_a, pos_b, candy_a, candy_b):
        """
        BOMB + BOMB → mega bomb (7x7)
        Centered on pos_b
        """
        r, c = pos_b
        self._consume_occupant_if_present(pos_a)
        self._consume_occupant_if_present(pos_b)
        # radius = 3 → 7x7
        for dr in range(-3, 4):
            for dc in range(-3, 4):
                self._apply_enhanced_damage(r + dr, c + dc)
        print("after action:\n", self.board)

    def _combo_rocket_bomb(self, pos_a, pos_b, candy_a, candy_b):
        """
        ROCKET + BOMB → 3x3 cross-rocket grid (Royal Match style)
        Centered on pos_b (the 'swapped-into' position).
        Cross rockets are applied even if a 3x3 position is outside the board;
        _apply_enhanced_damage safely ignores invalid cells.
        """
        center_r, center_c = pos_b
        self._consume_occupant_if_present(pos_a)
        self._consume_occupant_if_present(pos_b)
        print("before action:\n", self.board)
        # iterate 3x3 area around center
        for dr in (-1, 0, 1):
            pos_h = (center_r + dr, center_c)
            self._rocket_h(pos_h)
        for dc in (-1, 0, 1):
            pos_h = (center_r, center_c + dc)
            self._rocket_v(pos_h)
        print("after action:\n", self.board)

    def _combo_propeller_rocket_h(self, pos_a, pos_b, candy_a, candy_b):
        """
        Propeller carries a horizontal rocket.
        """

        self._consume_occupant_if_present(pos_a)
        self._consume_occupant_if_present(pos_b)

        self._apply_enhanced_damage(pos_b[0], pos_b[1])
        self._propeller_neighbor_damage(pos_b)

        target = self._find_random_valid_target()
        if not target:
            return

        tr, _ = target
        for cc in range(self.board.cols):
            self._apply_enhanced_damage(tr, cc)

    def _combo_propeller_rocket_v(self, pos_a, pos_b, candy_a, candy_b):
        """
        Propeller carries a vertical rocket.
        """
        self._consume_occupant_if_present(pos_a)
        self._consume_occupant_if_present(pos_b)

        self._apply_enhanced_damage(pos_b[0], pos_b[1])
        self._propeller_neighbor_damage(pos_b)

        target = self._find_random_valid_target()
        if not target:
            return

        _, tc = target
        for rr in range(self.board.rows):
            self._apply_enhanced_damage(rr, tc)

    def _combo_propeller_bomb(self, pos_a, pos_b, candy_a, candy_b):
        """
        Propeller carries a bomb.
        """

        self._consume_occupant_if_present(pos_a)
        self._consume_occupant_if_present(pos_b)

        self._apply_enhanced_damage(pos_b[0], pos_b[1])
        self._propeller_neighbor_damage(pos_b)

        target = self._find_random_valid_target()
        if not target:
            return

        tr, tc = target
        for dr in range(-2, 3):
            for dc in range(-2, 3):
                self._apply_enhanced_damage(tr + dr, tc + dc)

    def _combo_propeller_propeller(self, pos_a, pos_b, candy_a, candy_b):
        """
        PROPELLER + PROPELLER
        - Apply neighbor pre-damage at swap center
        - Destroy both originals
        - Spawn 3 propeller flights (no neighbor damage)
        """

        self._consume_occupant_if_present(pos_a)
        self._consume_occupant_if_present(pos_b)

        self._apply_enhanced_damage(pos_b[0], pos_b[1])
        self._propeller_neighbor_damage(pos_b)

        for _ in range(3):
            target = self._find_random_valid_target()
            if not target:
                continue
            self._apply_enhanced_damage(*target)

    def _combo_light_ball_rocket(self, pos_a, pos_b, candy_a, candy_b):
        # identify which is light ball
        light_pos = pos_a if candy_a.type == CandyType.LIGHT_BALL else pos_b
        other_type = candy_b.type if light_pos == pos_a else candy_a.type
        target_color = random.choice(list(self.board.color_set))

        self._consume_occupant_if_present(pos_a)
        self.board.get_board_element(pos_b[0],
                                     pos_b[1]).occupant = CandyFactory.create(
                                         CandyType.LIGHT_BALL, target_color)



        rocket_positions = []
        for r, c in self._collect_normal_candies_of_color(target_color):
            print("next position", r, c)
            new_type = random.choice([CandyType.ROCKET_H, CandyType.ROCKET_V])
            self.board.get_board_element(r, c).occupant = CandyFactory.create(
                new_type, target_color)
            rocket_positions.append((r, c))
            print("added", self.board.get_board_element(r, c))
        self.board.get_board_element(
            pos_b[0], pos_b[1]).occupant = CandyFactory.create(
                other_type, target_color)
        rocket_positions.append(pos_b)

        print("before action:\n", self.board)

        # trigger rockets sequentially
        for r, c in rocket_positions:
            occ = self.board.get_occupant(r, c)
            if not isinstance(occ, Candy):
                continue

            if occ.type == CandyType.ROCKET_H:
                self._consume_occupant_if_present((r, c))
                self._rocket_h((r, c))
            elif occ.type == CandyType.ROCKET_V:
                self._consume_occupant_if_present((r, c))
                self._rocket_v((r, c))

            # destroy rocket after activation
            self._apply_enhanced_damage(r, c)

    def _combo_light_ball_bomb(self, pos_a, pos_b, candy_a, candy_b):
        # identify which is light ball
        light_pos = pos_a if candy_a.type == CandyType.LIGHT_BALL else pos_b
        other_type = candy_b.type if light_pos == pos_a else candy_a.type
        target_color = random.choice(list(self.board.color_set))

        self._consume_occupant_if_present(pos_a)
        self.board.get_board_element(pos_b[0],
                                     pos_b[1]).occupant = CandyFactory.create(
                                         CandyType.LIGHT_BALL, target_color)

        bomb_centers = []
        for r, c in self._collect_normal_candies_of_color(target_color):
            self.board.get_board_element(r, c).occupant = CandyFactory.create(
                other_type, target_color)
            bomb_centers.append((r, c))
        self.board.get_board_element(
            pos_b[0], pos_b[1]).occupant = CandyFactory.create(
                other_type, target_color)
        bomb_centers.append(pos_b)

        print("before action:\n", self.board)

        # collect affected cells (set prevents stacking)
        affected = set()
        for r, c in bomb_centers:
            for dr in range(-2, 3):
                for dc in range(-2, 3):
                    if self.board.can_cell_hold_occupant(r + dr, c + dc):
                        affected.add((r + dr, c + dc))

        for r, c in bomb_centers:
            self._consume_occupant_if_present((r, c))

        # apply damage once per cell
        for r, c in affected:
            self._apply_enhanced_damage(r, c)

    def _combo_light_ball_propeller(self, pos_a, pos_b, candy_a, candy_b):
        light_pos = pos_a if candy_a.type == CandyType.LIGHT_BALL else pos_b
        other_type = candy_b.type if light_pos == pos_a else candy_a.type
        target_color = random.choice(list(self.board.color_set))

        self._consume_occupant_if_present(pos_a)
        self.board.get_board_element(pos_b[0],
                                     pos_b[1]).occupant = CandyFactory.create(
                                         CandyType.LIGHT_BALL, target_color)

        prop_positions = []
        for r, c in self._collect_normal_candies_of_color(target_color):
            self.board.get_board_element(r, c).occupant = CandyFactory.create(
                CandyType.PROPELLER, target_color)
            prop_positions.append((r, c))
        self.board.get_board_element(
            pos_b[0], pos_b[1]).occupant = CandyFactory.create(
                other_type, target_color)
        prop_positions.append(pos_b)

        print("before action:\n", self.board)

        # activate propellers one by one
        for r, c in prop_positions:
            self._consume_occupant_if_present((r, c))
            self._propeller((r, c), pre_damage=False)

    def _combo_light_ball_light_ball(self, pos_a, pos_b, candy_a, candy_b):
        """
        LIGHT BALL + LIGHT BALL
        - Destroy both light balls
        - Apply exactly ONE enhanced damage to every valid cell
        """
        # destroy both light balls
        self._consume_occupant_if_present(pos_a)

        self._consume_occupant_if_present(pos_b)
        for r in range(self.board.rows):
            for c in range(self.board.cols):
                if self.board.can_cell_hold_occupant(r, c):
                    self._apply_enhanced_damage(r, c)

    def _combo_light_ball_normal(self, pos_a, pos_b, candy_a, candy_b):
        light_pos = pos_a if candy_a.type == CandyType.LIGHT_BALL else pos_b
        other_candy = candy_a if not candy_a.type == CandyType.LIGHT_BALL else candy_b
        target_color = other_candy.color

        self._consume_occupant_if_present(pos_a)
        self.board.get_board_element(pos_b[0],
                                     pos_b[1]).occupant = CandyFactory.create(
                                         CandyType.LIGHT_BALL, target_color)

        normal_positions = []
        asd = self._collect_normal_candies_of_color(target_color)
        for r, c in asd:
            normal_positions.append((r, c))
        normal_positions.append(pos_b)
        match_res = MatchResult(normal_positions, pivot_candy=self.board.get_board_element(pos_b[0],
                                     pos_b[1]).occupant)

        print("before action:\n", self.board)

        self.damage_logic.apply_match_result(match_res)

        print("after action:\n", self.board)
        print()

    # ============================================================
    # HELPERS
    # ============================================================

    def _apply_enhanced_damage(self, r, c):
        if not self.board.can_cell_hold_occupant(r, c):
            return

        cell = self.board.get_board_element(r, c)
        if cell.occupant is None and cell.overlay is None and cell.underlay is None:
            return

        self._impacted_columns.add(c)

        self.damage_logic.apply_damage_at((r, c),
                                          DamageContext(DamageType.ENHANCED))

    def _apply_match_damage(self, r, c):
        if not self.board.can_cell_hold_occupant(r, c):
            return

        cell = self.board.get_board_element(r, c)
        if cell.occupant is None and cell.overlay is None and cell.underlay is None:
            return

        self._impacted_columns.add(c)

        self.damage_logic.apply_damage_at((r, c),
                                          DamageContext(DamageType.MATCH))

    def consume_impacted_columns(self):
        cols = set(self._impacted_columns)
        self._impacted_columns.clear()
        return cols

    def _propeller_neighbor_damage(self, pos):
        r, c = pos
        for dr, dc in ((1, 0), (-1, 0), (0, 1), (0, -1)):
            self._apply_enhanced_damage(r + dr, c + dc)

    def _find_random_valid_target(self):
        candidates = []
        for r in range(self.board.rows):
            for c in range(self.board.cols):
                if not self.board.can_cell_hold_occupant(r, c):
                    continue
                cell = self.board.get_board_element(r, c)
                if cell.occupant:
                    candidates.append((r, c))

        return random.choice(candidates) if candidates else None
