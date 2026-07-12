from enum import Enum

class Symbols(Enum):
    BAD = "X"
    MID = "△"
    OK = "◻"
    GOOD = "◯"
    GREAT = "⦾"

class Affinities(Enum):
    BAD = 0.5
    MID = 1
    OK = 1.5
    GOOD = 2
    GREAT = 2.5

class Proficiencies(Enum):
    BAD = 0.5
    MID = 1
    OK = 1.5
    GOOD = 2
    GREAT = 2.5