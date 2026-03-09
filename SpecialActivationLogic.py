import random
from DamageContext import DamageContext
from DamageType import DamageType
from CandyType import CandyType
from Candy import Candy, CandyFactory, BombCandy, PropellerCandy


class SpecialActivationLogic:
    def __init__(self, board, damage_logic):
        self.board = board
        self.damage_logic = damage_logic

        # ------------------------------------------------------------
        # Handler registries
        # ------------------------------------------------------------

        # Swap activation: handler(pos, candy, neighbor_candy) -> bool or None
        self._swap_handlers = {
            CandyType.LIGHT_BALL: self._swap_light_ball,
            CandyType.ROCKET_H: lambda pos, candy, neighbor: self._rocket(pos, horizontal=True),
            CandyType.ROCKET_V: lambda pos, candy, neighbor: self._rocket(pos, horizontal=False),
            CandyType.BOMB: lambda pos, candy, neighbor: self._bomb(pos),
            CandyType.PROPELLER: lambda pos, candy, neighbor: self._propeller(pos, pre_damage=True),
        }

        # Hit activation: handler(pos, candy) -> None
        self._hit_handlers = {
            CandyType.ROCKET_H: lambda pos, candy: self._rocket(pos, horizontal=True),
            CandyType.ROCKET_V: lambda pos, candy: self._rocket(pos, horizontal=False),
            CandyType.BOMB: lambda pos, candy: self._bomb(pos),
            CandyType.PROPELLER: lambda pos, candy: self._propeller(pos, pre_damage=True),
            CandyType.LIGHT_BALL: lambda pos, candy: self._light_ball_from_swap(
                pos, random.choice(list(self.board.color_set))
            ),
        }

        # Ordered combos: (type_a, type_b) means "a swapped into b"
        # handler(pos_a, pos_b, candy_a, candy_b) -> None
        self._combo_handlers_ordered = {
            (CandyType.ROCKET_H, CandyType.ROCKET_H): lambda pos_a, pos_b, candy_a, candy_b: self._combo_cross_rocket(pos_a, pos_b, candy_a, candy_b),
            (CandyType.ROCKET_H, CandyType.ROCKET_V): lambda pos_a, pos_b, candy_a, candy_b: self._combo_cross_rocket(pos_a, pos_b, candy_a, candy_b),
            (CandyType.ROCKET_V, CandyType.ROCKET_H): lambda pos_a, pos_b, candy_a, candy_b: self._combo_cross_rocket(pos_a, pos_b, candy_a, candy_b),
            (CandyType.ROCKET_V, CandyType.ROCKET_V): lambda pos_a, pos_b, candy_a, candy_b: self._combo_cross_rocket(pos_a, pos_b, candy_a, candy_b),

            (CandyType.BOMB, CandyType.BOMB): lambda pos_a, pos_b, candy_a, candy_b: self._combo_mega_bomb(pos_a, pos_b, candy_a, candy_b),
            (CandyType.ROCKET_H, CandyType.BOMB): lambda pos_a, pos_b, candy_a, candy_b: self._combo_rocket_bomb(pos_a, pos_b, candy_a, candy_b),
            (CandyType.ROCKET_V, CandyType.BOMB): lambda pos_a, pos_b, candy_a, candy_b: self._combo_rocket_bomb(pos_a, pos_b, candy_a, candy_b),
            (CandyType.BOMB, CandyType.ROCKET_H): lambda pos_a, pos_b, candy_a, candy_b: self._combo_rocket_bomb(pos_a, pos_b, candy_a, candy_b),
            (CandyType.BOMB, CandyType.ROCKET_V): lambda pos_a, pos_b, candy_a, candy_b: self._combo_rocket_bomb(pos_a, pos_b, candy_a, candy_b),

            (CandyType.PROPELLER, CandyType.PROPELLER): lambda pos_a, pos_b, candy_a, candy_b: self._combo_propeller_propeller(pos_a, pos_b, candy_a, candy_b),
            (CandyType.PROPELLER, CandyType.ROCKET_H): lambda pos_a, pos_b, candy_a, candy_b: self._combo_propeller_rocket_h(pos_a, pos_b, candy_a, candy_b),
            (CandyType.PROPELLER, CandyType.ROCKET_V): lambda pos_a, pos_b, candy_a, candy_b: self._combo_propeller_rocket_v(pos_a, pos_b, candy_a, candy_b),
            (CandyType.PROPELLER, CandyType.BOMB): lambda pos_a, pos_b, candy_a, candy_b: self._combo_propeller_bomb(pos_a, pos_b, candy_a, candy_b),
            (CandyType.ROCKET_H, CandyType.PROPELLER): lambda pos_a, pos_b, candy_a, candy_b: self._combo_propeller_rocket_h(pos_a, pos_b, candy_a, candy_b),
            (CandyType.ROCKET_V, CandyType.PROPELLER): lambda pos_a, pos_b, candy_a, candy_b: self._combo_propeller_rocket_v(pos_a, pos_b, candy_a, candy_b),
            (CandyType.BOMB, CandyType.PROPELLER): lambda pos_a, pos_b, candy_a, candy_b: self._combo_propeller_bomb(pos_a, pos_b, candy_a, candy_b),

            (CandyType.LIGHT_BALL, CandyType.ROCKET_H): lambda pos_a, pos_b, candy_a, candy_b: self._combo_light_ball_rocket(pos_a, pos_b, candy_a, candy_b),
            (CandyType.LIGHT_BALL, CandyType.ROCKET_V): lambda pos_a, pos_b, candy_a, candy_b: self._combo_light_ball_rocket(pos_a, pos_b, candy_a, candy_b),
            (CandyType.ROCKET_H, CandyType.LIGHT_BALL): lambda pos_a, pos_b, candy_a, candy_b: self._combo_light_ball_rocket(pos_a, pos_b, candy_a, candy_b),
            (CandyType.ROCKET_V, CandyType.LIGHT_BALL): lambda pos_a, pos_b, candy_a, candy_b: self._combo_light_ball_rocket(pos_a, pos_b, candy_a, candy_b),
            (CandyType.LIGHT_BALL, CandyType.BOMB): lambda pos_a, pos_b, candy_a, candy_b: self._combo_light_ball_bomb(pos_a, pos_b, candy_a, candy_b),
            (CandyType.BOMB, CandyType.LIGHT_BALL): lambda pos_a, pos_b, candy_a, candy_b: self._combo_light_ball_bomb(pos_a, pos_b, candy_a, candy_b),
            (CandyType.LIGHT_BALL, CandyType.PROPELLER): lambda pos_a, pos_b, candy_a, candy_b: self._combo_light_ball_propeller(pos_a, pos_b, candy_a, candy_b),
            (CandyType.PROPELLER, CandyType.LIGHT_BALL): lambda pos_a, pos_b, candy_a, candy_b: self._combo_light_ball_propeller(pos_a, pos_b, candy_a, candy_b),
            (CandyType.LIGHT_BALL, CandyType.LIGHT_BALL): lambda pos_a, pos_b, candy_a, candy_b: self._combo_light_ball_light_ball(pos_a, pos_b, candy_a, candy_b),
        }

    def _collect_normal_candies_of_color(self, color):
        positions = []
        for r in range(self.board.rows):
            for c in range(self.board.cols):
                if not self.board.can_cell_hold_occupant(r, c):
                    continue
                cell = self.board.get_board_element(r, c)
                occ = cell.occupant
                if isinstance(occ, Candy) and occ.type == CandyType.NORMAL and occ.color == color:
                    positions.append((r, c))
        return positions
    # ============================================================
    # PUBLIC API
    # ============================================================

    def activate_on_swap(self, pos, candy, neighbor_candy):
        if candy is None:
            return False

        handler = self._swap_handlers.get(candy.type)
        if handler is None:
            return False

        result = handler(pos, candy, neighbor_candy)
        # Light ball returns bool; others return None
        return True if result is None else bool(result)

    def activate_on_hit(self, pos, candy):
        if candy is None:
            return False

        handler = self._hit_handlers.get(candy.type)
        if handler is None:
            return False

        handler(pos, candy)
        return True

    # ============================================================
    # ORDERED SWAP COMBOS (INFRASTRUCTURE ONLY)
    # ============================================================

    def register_combo(self, type_a: CandyType, type_b: CandyType, handler):
        """
        Register an ordered combo: (type_a, type_b) means candy_a swapped into candy_b.
        handler(pos_a, pos_b, candy_a, candy_b) -> None
        """
        self._combo_handlers_ordered[(type_a, type_b)] = handler

    def can_activate_combo_on_swap(self, candy_a, candy_b) -> bool:
        if not isinstance(candy_a, Candy) or not isinstance(candy_b, Candy):
            return False
        return (candy_a.type, candy_b.type) in self._combo_handlers_ordered

    def activate_combo_on_swap(self, pos_a, pos_b, candy_a, candy_b) -> bool:
        if not self.can_activate_combo_on_swap(candy_a, candy_b):
            return False

        handler = self._combo_handlers_ordered[(candy_a.type, candy_b.type)]
        handler(pos_a, pos_b, candy_a, candy_b)
        return True

    # ============================================================
    # IMPLEMENTATIONS (BASE SPECIALS)
    # ============================================================

    def _rocket(self, pos, horizontal):
        r, c = pos

        if horizontal:
            for cc in range(self.board.cols):
                self._apply_enhanced_damage(r, cc)
        else:
            for rr in range(self.board.rows):
                self._apply_enhanced_damage(rr, c)

        self._apply_enhanced_damage(pos[0], pos[1])

    def _bomb(self, pos):
        r, c = pos
        for dr in range(-2, 3):
            for dc in range(-2, 3):
                self._apply_enhanced_damage(r + dr, c + dc)

        self._apply_enhanced_damage(pos[0], pos[1])

    def _propeller(self, pos, pre_damage):
        r, c = pos

        if pre_damage:
            for dr, dc in ((1, 0), (-1, 0), (0, 1), (0, -1)):
                self._apply_enhanced_damage(r + dr, c + dc)

        self._apply_enhanced_damage(pos[0], pos[1])

        target = self._find_random_valid_target()
        if target:
            self._apply_enhanced_damage(*target)

    def _light_ball_from_swap(self, pos, color):
        for r in range(self.board.rows):
            for c in range(self.board.cols):
                if not self.board.can_cell_hold_occupant(r, c):
                    continue

                cell = self.board.get_board_element(r, c)
                if not isinstance(cell.occupant, Candy):
                    continue

                if cell.occupant.color == color:
                    cell.apply_damage(
                        DamageContext(DamageType.MATCH, color=color)
                    )

        self._apply_enhanced_damage(pos[0], pos[1])

    # ============================================================
    # COMBO IMPLEMENTATIONS
    # ============================================================

    def _combo_cross_rocket(self, pos_a, pos_b, candy_a, candy_b):
        """
        ROCKET + ROCKET → cross rocket
        Centered on pos_b (the 'swapped-into' position)
        """
        # destroy both originals
        self._apply_enhanced_damage(pos_a[0], pos_a[1])
        self._apply_enhanced_damage(pos_b[0], pos_b[1])

        r, c = pos_b

        # horizontal
        for cc in range(self.board.cols):
            self._apply_enhanced_damage(r, cc)

        # vertical
        for rr in range(self.board.rows):
            self._apply_enhanced_damage(rr, c)

    def _combo_mega_bomb(self, pos_a, pos_b, candy_a, candy_b):
        """
        BOMB + BOMB → mega bomb (7x7)
        Centered on pos_b
        """
        # destroy both originals
        self._apply_enhanced_damage(pos_a[0], pos_a[1])
        self._apply_enhanced_damage(pos_b[0], pos_b[1])

        r, c = pos_b

        # radius = 3 → 7x7
        for dr in range(-3, 4):
            for dc in range(-3, 4):
                self._apply_enhanced_damage(r + dr, c + dc)

    def _combo_rocket_bomb(self, pos_a, pos_b, candy_a, candy_b):
        """
        ROCKET + BOMB → 3x3 cross-rocket grid (Royal Match style)
        Centered on pos_b (the 'swapped-into' position).
        Cross rockets are applied even if a 3x3 position is outside the board;
        _apply_enhanced_damage safely ignores invalid cells.
        """
        # destroy both originals
        self._apply_enhanced_damage(pos_a[0], pos_a[1])
        self._apply_enhanced_damage(pos_b[0], pos_b[1])

        center_r, center_c = pos_b

        # iterate 3x3 area around center
        for dr in (-1, 0, 1):
            for dc in (-1, 0, 1):
                r = center_r + dr
                c = center_c + dc

                # horizontal beam at (r, c)
                for cc in range(self.board.cols):
                    self._apply_enhanced_damage(r, cc)

                # vertical beam at (r, c)
                for rr in range(self.board.rows):
                    self._apply_enhanced_damage(rr, c)

    def _combo_propeller_rocket_h(self, pos_a, pos_b, candy_a, candy_b):
        """
        Propeller carries a horizontal rocket.
        """
        # 1) propeller spin damage at swap center
        self._propeller_neighbor_damage(pos_b)

        # 2) destroy both originals
        self._apply_enhanced_damage(pos_a[0], pos_a[1])
        self._apply_enhanced_damage(pos_b[0], pos_b[1])

        # 3) fly to random target
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
        self._propeller_neighbor_damage(pos_b)

        self._apply_enhanced_damage(pos_a[0], pos_a[1])
        self._apply_enhanced_damage(pos_b[0], pos_b[1])

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
        self._propeller_neighbor_damage(pos_b)

        self._apply_enhanced_damage(pos_a[0], pos_a[1])
        self._apply_enhanced_damage(pos_b[0], pos_b[1])

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
        # 1) pre-damage at center
        self._propeller_neighbor_damage(pos_b)

        # 2) destroy both originals
        self._apply_enhanced_damage(pos_a[0], pos_a[1])
        self._apply_enhanced_damage(pos_b[0], pos_b[1])

        # 3) fly three independent propellers
        for _ in range(3):
            target = self._find_random_valid_target()
            if not target:
                continue
            self._apply_enhanced_damage(*target)

    def _combo_light_ball_rocket(self, pos_a, pos_b, candy_a, candy_b):
        """
        LIGHT BALL + ROCKET
        - Light ball remains
        - Rocket is destroyed
        - Pick random color
        - Turn all NORMAL candies of that color into random rockets
        - Trigger rockets ONE BY ONE
        """
        # identify which is light ball
        light_pos = pos_a if candy_a.type == CandyType.LIGHT_BALL else pos_b
        other_pos = pos_b if light_pos == pos_a else pos_a

        # destroy the non-light-ball special
        self._apply_enhanced_damage(other_pos[0], other_pos[1])

        target_color = random.choice(list(self.board.color_set))

        rocket_positions = []
        for r, c in self._collect_normal_candies_of_color(target_color):
            new_type = random.choice([CandyType.ROCKET_H, CandyType.ROCKET_V])
            self.board.get_board_element(r, c).occupant = CandyFactory.create(new_type, target_color)
            rocket_positions.append((r, c))

        # trigger rockets sequentially
        for r, c in rocket_positions:
            occ = self.board.get_occupant(r, c)
            if not isinstance(occ, Candy):
                continue

            if occ.type == CandyType.ROCKET_H:
                for cc in range(self.board.cols):
                    self._apply_enhanced_damage(r, cc)
            elif occ.type == CandyType.ROCKET_V:
                for rr in range(self.board.rows):
                    self._apply_enhanced_damage(rr, c)

            # destroy rocket after activation
            self._apply_enhanced_damage(r, c)

    def _combo_light_ball_bomb(self, pos_a, pos_b, candy_a, candy_b):
        """
        LIGHT BALL + BOMB
        - Light ball remains
        - Bomb is destroyed
        - Pick random color
        - Turn all NORMAL candies of that color into bombs
        - Apply ALL bomb explosions at once (no stacking)
        """
        # identify which is light ball
        light_pos = pos_a if candy_a.type == CandyType.LIGHT_BALL else pos_b
        other_pos = pos_b if light_pos == pos_a else pos_a

        # destroy the non-light-ball special
        self._apply_enhanced_damage(other_pos[0], other_pos[1])

        target_color = random.choice(list(self.board.color_set))

        bomb_centers = []
        for r, c in self._collect_normal_candies_of_color(target_color):
            self.board.get_board_element(r, c).occupant = BombCandy(target_color)
            bomb_centers.append((r, c))

        # collect affected cells (set prevents stacking)
        affected = set()
        for r, c in bomb_centers:
            for dr in range(-2, 3):
                for dc in range(-2, 3):
                    if self.board.can_cell_hold_occupant(r + dr, c + dc):
                        affected.add((r + dr, c + dc))

        # apply damage once per cell
        for r, c in affected:
            self._apply_enhanced_damage(r, c)

        # destroy all bombs after explosion
        for r, c in bomb_centers:
            self._apply_enhanced_damage(r, c)

    def _combo_light_ball_propeller(self, pos_a, pos_b, candy_a, candy_b):
        """
        LIGHT BALL + PROPELLER
        - Light ball remains
        - Propeller is destroyed
        - Convert NORMAL candies of random color into propellers
        - Each propeller:
            * applies enhanced damage to its own cell
            * flies once (no neighbor pre-damage)
            * is destroyed
        """
        # identify which is light ball
        light_pos = pos_a if candy_a.type == CandyType.LIGHT_BALL else pos_b
        other_pos = pos_b if light_pos == pos_a else pos_a

        # destroy the propeller
        self._apply_enhanced_damage(other_pos[0], other_pos[1])

        target_color = random.choice(list(self.board.color_set))

        prop_positions = []
        for r, c in self._collect_normal_candies_of_color(target_color):
            self.board.get_board_element(r, c).occupant = PropellerCandy(target_color)
            prop_positions.append((r, c))

        # activate propellers one by one
        for r, c in prop_positions:
            # apply enhanced damage to its own cell
            self._apply_enhanced_damage(r, c)

            # fly once (no neighbor pre-damage)
            target = self._find_random_valid_target()
            if target:
                self._apply_enhanced_damage(*target)

            # destroy propeller after action
            self._apply_enhanced_damage(r, c)

    def _combo_light_ball_light_ball(self, pos_a, pos_b, candy_a, candy_b):
        """
        LIGHT BALL + LIGHT BALL
        - Destroy both light balls
        - Apply exactly ONE enhanced damage to every valid cell
        """
        # destroy both light balls
        self._apply_enhanced_damage(pos_a[0], pos_a[1])
        self._apply_enhanced_damage(pos_b[0], pos_b[1])

        for r in range(self.board.rows):
            for c in range(self.board.cols):
                if self.board.can_cell_hold_occupant(r, c):
                    self._apply_enhanced_damage(r, c)

    # ============================================================
    # HELPERS
    # ============================================================

    def _swap_light_ball(self, pos, candy, neighbor_candy) -> bool:
        if not isinstance(neighbor_candy, Candy):
            return False

        target_color = (
            neighbor_candy.color
            if neighbor_candy.color is not None
            else random.choice(list(self.board.color_set))
        )

        self._light_ball_from_swap(pos, target_color)
        return True

    def _apply_enhanced_damage(self, r, c):
        if not self.board.can_cell_hold_occupant(r, c):
            return

        cell = self.board.get_board_element(r, c)
        if cell.occupant is None:
            return

        cell.apply_damage(
            DamageContext(DamageType.ENHANCED)
        )

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
