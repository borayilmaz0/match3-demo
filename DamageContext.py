from ColorType import ColorType
from DamageType import DamageType


class DamageContext:
    __slots__ = ("damage_type", "color")

    def __init__(self, damage_type: DamageType, color: ColorType = None):
        self.damage_type = damage_type
        self.color = color
