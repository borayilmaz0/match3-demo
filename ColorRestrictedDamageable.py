from BasicDamageable import BasicDamageable
from DamageContext import DamageContext
from DamageType import DamageType


class ColorRestrictedDamageable(BasicDamageable):
    def __init__(self, hp: int, allowed_minimum: DamageType, allowed_color):
        super().__init__(hp, allowed_minimum)
        self.allowed_color = allowed_color

    def can_take_damage(self, ctx: DamageContext) -> bool:
        # first apply base damage rule
        if not super().can_take_damage(ctx):
            return False

        # if damage is MATCH_NEAR, require color match
        if ctx.damage_type == DamageType.MATCH_NEAR:
            return ctx.color == self.allowed_color

        return True
