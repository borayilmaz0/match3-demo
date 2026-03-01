from DamageReflecting import DamageReflecting


class BasicDamageReflecting(DamageReflecting):
    def can_reflect_damage(self) -> bool:
        return True