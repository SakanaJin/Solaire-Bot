from enum import Enum

class FavorLevels(Enum):
    HATED = (-0.20, 0.02)
    POOR = (-0.05, 0.02)
    NEUTRAL = (-0.02, 0.05)
    FAVORED = (-0.02, 0.15)
    LOVED = (-0.02, 0.20)