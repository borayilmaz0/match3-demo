from DamageContext import DamageContext
from DamageType import DamageType
from Damageable import Damageable


class BasicDamageable(Damageable):
    def __init__(self, hp: int, allowed_minimum: DamageType):
        self.hp = hp
        self.allowed_minimum = allowed_minimum

    def can_take_damage(self, ctx: DamageContext) -> bool:
        return ctx.damage_type >= self.allowed_minimum

    def take_damage(self, ctx: DamageContext):
        if self.can_take_damage(ctx):
            self.hp -= 1

    def is_destroyed(self) -> bool:
        return self.hp <= 0
