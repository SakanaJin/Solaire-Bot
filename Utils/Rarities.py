from enum import Enum

class Rarities(Enum):
    COMMON = 0xf7faf8
    UNCOMMON = 0x14c744
    RARE = 0x1791e8
    LEGENDARY = 0x7217e8
    INCANDESCENT = 0xfcb632
    KEYITEM = 0x068067
    MONUMENT = 0xfcf914

class Weights(Enum):
    COMMON = 1000
    UNCOMMON = 400
    RARE = 100
    LEGENDARY = 25
    INCANDESCENT = 5