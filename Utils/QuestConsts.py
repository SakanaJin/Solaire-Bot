from enum import Enum

class QuestTypes(str, Enum):
    KILL = "kill"
    COLLECT = "collect"
    LVL = "lvl"
    COMMAND = "command"

class QuestCategories(str, Enum):
    MAIN = "main"
    DAILY = "daily"
    BANNER = "banner"